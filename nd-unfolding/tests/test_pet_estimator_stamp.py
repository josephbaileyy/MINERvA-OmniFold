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


class OtherProducerStampTests(Fixture):
    """The remaining component producers stamp the same way, so a freshly produced budget
    assembles WITHOUT --allow-unstamped."""

    WANT = {"niter": 2, "schema_id": "recoil-pc-v1", "producer_commit": "aeb6668c"}

    def cml(self, *stamp_args):
        md = self.tmp / "cml"
        md.mkdir(exist_ok=True)
        rng = np.random.default_rng(5)
        for s in (0, 1):
            for e in (0, 1):
                np.savez(md / f"pet_s{s}_e{e}_bkgsub_5d_xsec.npz",
                         xsec_flat=self.cv * (1 + 0.02 * rng.normal(size=NBINS)))
        return self.run_py("combine_cml_bkgsub.py", "--glob", str(md / "*.npz"), "--cv", "cv.npz",
                           "--floor", "absent.json", "--out", "cml.npz", "--expect", "4",
                           *stamp_args)

    def cstat100(self, *extra):
        return self.run_py("combine_cstat_bkgsub_100rep.py",
                           "--glob", str(self.tmp / "reps" / "*.npz"), "--cv", "cv.npz",
                           "--floor", "absent.json", "--expected-ids", "1-6",
                           "--no-weight-check", "--out", "cstat100.npz", *extra)

    def csyst(self, argv):
        """build_csyst_prelim_bkgsub.main() in-process with its PyROOT modules replaced by fakes:
        the stamp is the unit under test, not the systematic calculation."""
        import importlib.util
        import types
        from unittest import mock
        cv, rng = self.cv, np.random.default_rng(7)
        pse = types.ModuleType("pet_systematics_5d")

        class FakePET:
            shape, edges = (NBINS,), None

            def __init__(self, *a):
                pass

            def xsec(self, r):
                return cv.copy() if r is None else cv * (1 + 0.01 * rng.normal(size=NBINS))
        pse.PETxsec5D, pse.KNOB_BANDS, pse.RHO_CLIP = FakePET, ("KnobA",), None
        pse._opt = lambda bank, name: name
        uqm = types.ModuleType("uq_math")
        uqm.guarded_ratio = lambda v, label, invalid_policy=None, clip=None: v
        uqm.mat_covariance = lambda X: np.cov(np.asarray(X), rowvar=False, bias=True)
        uqm.require_truth_ratio_bank = lambda bank, bands, expected_flux=100: [0, 1, 2]
        xnd = types.ModuleType("xsec_nd")
        xnd.total_xsec = lambda x, edges: 1.0
        spec = importlib.util.spec_from_file_location("csyst_under_test",
                                                      PET / "build_csyst_prelim_bkgsub.py")
        mod = importlib.util.module_from_spec(spec)
        with mock.patch.dict(sys.modules, {"pet_systematics_5d": pse, "uq_math": uqm,
                                           "xsec_nd": xnd}), \
                mock.patch.object(sys, "argv", ["build_csyst_prelim_bkgsub.py", *argv]):
            spec.loader.exec_module(mod)
            mod.main()

    def test_cml_missing_stamp_exits_nonzero(self):
        r = self.cml()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--estimator-niter", r.stderr)
        self.assertFalse((self.tmp / "cml.npz").exists())

    def test_cml_stamp_round_trips(self):
        r = self.cml(*STAMP_ARGS)
        self.assertEqual(r.returncode, 0, r.stderr)
        with np.load(self.tmp / "cml.npz") as z:
            self.assertEqual(estimator_stamp.read_npz(z), self.WANT)
        summary = json.loads((self.tmp / "cml.summary.json").read_text())
        self.assertEqual(summary["estimator_stamp"], self.WANT)

    def test_cstat100_missing_stamp_exits_nonzero(self):
        r = self.cstat100()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--estimator-niter", r.stderr)

    def test_cstat100_stamp_round_trips(self):
        r = self.cstat100(*STAMP_ARGS)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        with np.load(self.tmp / "cstat100.npz") as z:
            self.assertEqual(estimator_stamp.read_npz(z), self.WANT)
        summary = json.loads((self.tmp / "cstat100.summary.json").read_text())
        self.assertEqual(summary["estimator_stamp"], self.WANT)

    def test_cstat100_refuses_a_ref20_of_a_different_estimator(self):
        self.assertEqual(self.combine("--estimator-niter", "3", "--schema-id", "recoil-pc-v1",
                                      "--producer-commit", "aeb6668c").returncode, 0)
        r = self.cstat100(*STAMP_ARGS, "--ref20", "cstat.npz")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("disagrees with the --ref20", r.stderr)
        self.assertFalse((self.tmp / "cstat100.npz").exists())

    def test_csyst_missing_stamp_is_refused_before_the_root_imports(self):
        r = self.run_py("build_csyst_prelim_bkgsub.py", "--out", "csyst.npz")
        self.assertEqual(r.returncode, 2, r.stderr)          # argparse, not ModuleNotFoundError
        self.assertIn("--estimator-niter", r.stderr)
        self.assertNotIn("ModuleNotFoundError", r.stderr)

    def test_csyst_stamp_round_trips(self):
        self.csyst(["--out", str(self.tmp / "csyst.npz"), *STAMP_ARGS])
        with np.load(self.tmp / "csyst.npz") as z:
            self.assertEqual(estimator_stamp.read_npz(z), self.WANT)
        summary = json.loads((self.tmp / "csyst.summary.json").read_text())
        self.assertEqual(summary["estimator_stamp"], self.WANT)

    def test_fresh_components_assemble_without_allow_unstamped(self):
        self.assertEqual(self.combine(*STAMP_ARGS).returncode, 0)
        self.assertEqual(self.cml(*STAMP_ARGS).returncode, 0)
        self.csyst(["--out", str(self.tmp / "csyst.npz"), *STAMP_ARGS])
        r = self.run_py("assemble_ctotal_bkgsub.py", "--cretrain", "", "--w-source", "w.npz",
                        "--csyst", "csyst.npz", "--cstat", "cstat.npz", "--cml", "cml.npz",
                        "--out", "ctotal.npz")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        summary = json.loads((self.tmp / "ctotal.summary.json").read_text())
        self.assertEqual(summary["estimator_stamp"], self.WANT)
        self.assertEqual(summary["unstamped_components"], [])


if __name__ == "__main__":
    unittest.main()
