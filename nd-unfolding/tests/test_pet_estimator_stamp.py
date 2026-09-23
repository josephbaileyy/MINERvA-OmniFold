"""KNOWN_ISSUES row 32: PET covariance components carry the estimator stamp in their own artifacts.

End to end through the real CLIs on synthetic inputs: a missing stamp exits non-zero, a stamp
round-trips from flags to npz and summary and back, and the assembler refuses components whose
estimator configurations disagree -- while accepting the case it must accept (agreeing stamps).
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
PET = ND / "pet"
sys.path.insert(0, str(PET))

import estimator_stamp  # noqa: E402
import assemble_ctotal_bkgsub as ac  # noqa: E402

NBINS = int(np.prod(ac.SHAPE5))
STAMP_ARGS = ["--estimator-niter", "2", "--schema-id", "recoil-pc-v1",
              "--producer-commit", "aeb6668c"]


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="pet-stamp-"))
        rng = np.random.default_rng(3)
        self.cv = np.zeros(NBINS)
        self.rep_idx = rng.choice(NBINS, 24, replace=False)
        self.cv[self.rep_idx] = rng.uniform(1.0, 2.0, self.rep_idx.size)
        np.savez(self.tmp / "cv.npz", xsec_flat=self.cv)
        (self.tmp / "reps").mkdir()
        for rid in range(1, 7):
            x = self.cv * (1 + 0.05 * rng.normal(size=NBINS))
            np.savez(self.tmp / "reps" / f"pet_bootstrap_5d_{rid}.npz", seed=rid, xsec_flat=x)
        np.savez(self.tmp / "w.npz", edges_4=np.linspace(0.0, 3.0, ac.SHAPE5[4] + 1))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, True)

    def run_py(self, script, *args):
        return subprocess.run([sys.executable, str(PET / script), *args],
                              capture_output=True, text=True, cwd=self.tmp)

    def combine(self, *stamp_args, out="cstat.npz"):
        return self.run_py("combine_cstat_bkgsub.py",
                           "--glob", str(self.tmp / "reps" / "*.npz"), "--cv", "cv.npz",
                           "--floor", "absent.json", "--expected-ids", "1-6", "--out", out,
                           *stamp_args)

    def component(self, name, key, stamp=None):
        mask = self.cv > 0
        n = int(mask.sum())
        extra = {} if stamp is None else {estimator_stamp.NPZ_KEY: estimator_stamp.npz_value(stamp)}
        np.savez(self.tmp / name, **{key: np.eye(n) * 1e-4}, reported_mask=mask, cv=self.cv,
                 **extra)
        return name


class CombineStampTests(Fixture):
    def test_missing_stamp_exits_nonzero(self):
        r = self.combine()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--estimator-niter", r.stderr)
        self.assertFalse((self.tmp / "cstat.npz").exists())

    def test_invalid_stamp_exits_nonzero(self):
        bad = ["--estimator-niter", "2", "--schema-id", "recoil-pc-v1",
               "--producer-commit", "not-a-sha"]
        r = self.combine(*bad)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("producer_commit", r.stderr)

    def test_stamp_round_trips_to_npz_and_summary(self):
        r = self.combine(*STAMP_ARGS)
        self.assertEqual(r.returncode, 0, r.stderr)
        want = {"niter": 2, "schema_id": "recoil-pc-v1", "producer_commit": "aeb6668c"}
        with np.load(self.tmp / "cstat.npz") as z:
            self.assertEqual(estimator_stamp.read_npz(z), want)
        summary = json.loads((self.tmp / "cstat.summary.json").read_text())
        self.assertEqual(summary["estimator_stamp"], want)
        self.assertIn("head=", summary["combined_by"])


class AssembleStampTests(Fixture):
    def assemble(self, *args):
        return self.run_py("assemble_ctotal_bkgsub.py", "--cretrain", "", "--w-source", "w.npz",
                           "--out", "ctotal.npz", *args)

    def test_agreeing_stamps_assemble_and_the_stamp_is_derived(self):
        self.assertEqual(self.combine(*STAMP_ARGS).returncode, 0)
        s = estimator_stamp.make_stamp(2, "recoil-pc-v1", "aeb6668c")
        r = self.assemble("--csyst", self.component("csyst.npz", "C_syst", s),
                          "--cstat", "cstat.npz", "--cml", self.component("cml.npz", "C_ml", s))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        with np.load(self.tmp / "ctotal.npz") as z:
            self.assertEqual(estimator_stamp.read_npz(z), s)
        summary = json.loads((self.tmp / "ctotal.summary.json").read_text())
        self.assertEqual(summary["estimator_stamp"], s)
        self.assertEqual(summary["unstamped_components"], [])

    def test_mismatched_niter_is_refused(self):
        self.assertEqual(self.combine(*STAMP_ARGS).returncode, 0)
        s2 = estimator_stamp.make_stamp(2, "recoil-pc-v1", "aeb6668c")
        s3 = estimator_stamp.make_stamp(3, "recoil-pc-v1", "aeb6668c")
        r = self.assemble("--csyst", self.component("csyst.npz", "C_syst", s2),
                          "--cstat", "cstat.npz", "--cml", self.component("cml.npz", "C_ml", s3))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("disagree", r.stderr)
        self.assertFalse((self.tmp / "ctotal.npz").exists())

    def test_mismatched_schema_is_refused(self):
        self.assertEqual(self.combine(*STAMP_ARGS).returncode, 0)
        s = estimator_stamp.make_stamp(2, "fullevent-v2", "aeb6668c")
        r = self.assemble("--csyst", self.component("csyst.npz", "C_syst", s),
                          "--cstat", "cstat.npz", "--cml", self.component("cml.npz", "C_ml", s))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("disagree", r.stderr)

    def test_declared_stamp_disagreeing_with_components_is_refused(self):
        self.assertEqual(self.combine(*STAMP_ARGS).returncode, 0)
        s = estimator_stamp.make_stamp(2, "recoil-pc-v1", "aeb6668c")
        r = self.assemble("--csyst", self.component("csyst.npz", "C_syst", s),
                          "--cstat", "cstat.npz", "--cml", self.component("cml.npz", "C_ml", s),
                          "--estimator-niter", "3", "--schema-id", "recoil-pc-v1",
                          "--producer-commit", "aeb6668c")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("declared estimator", r.stderr)

    def test_unstamped_component_is_refused_unless_allowed_and_then_disclosed(self):
        self.assertEqual(self.combine(*STAMP_ARGS).returncode, 0)
        s = estimator_stamp.make_stamp(2, "recoil-pc-v1", "aeb6668c")
        args = ["--csyst", self.component("csyst.npz", "C_syst"), "--cstat", "cstat.npz",
                "--cml", self.component("cml.npz", "C_ml", s)]
        r = self.assemble(*args)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("C_syst", r.stderr)
        r = self.assemble(*args, "--allow-unstamped", "C_syst")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        summary = json.loads((self.tmp / "ctotal.summary.json").read_text())
        self.assertEqual(summary["unstamped_components"], ["C_syst"])

    def test_differing_producer_commits_are_disclosed_and_need_a_declaration(self):
        a = estimator_stamp.make_stamp(2, "recoil-pc-v1", "aeb6668c")
        b = estimator_stamp.make_stamp(2, "recoil-pc-v1", "7ab8720f")
        with self.assertRaises(ValueError):
            ac.reconcile_stamps({"C_syst": a, "C_stat": b})
        stamp, report = ac.reconcile_stamps({"C_syst": a, "C_stat": b}, declared=a)
        self.assertEqual(stamp, a)
        self.assertTrue(report["producer_commits_differ"])


if __name__ == "__main__":
    unittest.main()
