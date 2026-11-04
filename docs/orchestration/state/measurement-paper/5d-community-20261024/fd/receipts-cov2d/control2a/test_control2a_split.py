"""Local checks of control2a_split.py, in an env with PyROOT and uproot together (conda-forge ROOT 6.28/12, uproot
5.6.9), on a synthetic $CV built by test_cov2d_writer's own write_cv. The code is exported from M with git archive.
macOS has no O_NOATIME, so each step runs through a launcher that sets os.O_NOATIME = 0 first, as the writer's
tests do; the cluster run keeps the real flag.

  REPO=<checkout> M=<sha> python -m unittest -v test_control2a_split
"""
from __future__ import annotations

import contextlib
import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
HARNESS = HERE / "control2a_split.py"
REPO = Path(os.environ["REPO"])
M = os.environ["M"]
LAUNCH = ("import os, runpy, sys; os.O_NOATIME = getattr(os, 'O_NOATIME', 0); sys.argv = sys.argv[1:]; "
          "runpy.run_path(sys.argv[0], run_name='__main__')")
EXPORT = ["2d-unfolding/cov2d", "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/control1"]


def run(*args):
    r = subprocess.run([sys.executable, "-B", "-c", LAUNCH, str(HARNESS), *map(str, args)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def field(text, key):
    return re.search(rf"{key}=([0-9a-f]{{64}})", text).group(1)


class Split(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        cls.deploy = Path(cls.td.name) / "deploy"
        cls.deploy.mkdir()
        tar = subprocess.run(["git", "-C", str(REPO), "archive", M, *EXPORT], check=True, capture_output=True).stdout
        with tarfile.open(fileobj=io.BytesIO(tar)) as t:
            t.extractall(cls.deploy)
        sys.path[:0] = [str(cls.deploy / "2d-unfolding/cov2d"), str(cls.deploy / "2d-unfolding/cov2d/tests")]
        import cov2d_writer
        import test_cov2d_writer
        cls.w = cov2d_writer
        r = np.random.default_rng(12)
        n = 2345
        cls.cols = {"measured": r.uniform(0, 3, n), "measured_pz": r.uniform(1, 30, n),
                    "measured_pass": (r.uniform(size=n) < 0.8).astype(np.uint8)}
        cls.cols["measured"][7] = -0.0
        cls.pot = 1.057394261158926e21
        cls.cv = Path(cls.td.name) / "cv.root"
        test_cov2d_writer.write_cv(cls.cv, cls.cols, cls.pot)
        os.utime(cls.cv, (time.time() + 86400, os.stat(cls.cv).st_mtime))

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def setUp(self):
        self.d = Path(tempfile.mkdtemp(dir=self.td.name))

    def read_write(self):
        npz, man, out = self.d / "cv.npz", self.d / "cv.json", self.d / "out.root"
        rc, t1 = run("--deploy", self.deploy, "read", "--cv", self.cv, "--npz", npz, "--manifest", man)
        self.assertEqual(rc, 0, t1)
        rc, t2 = run("--deploy", self.deploy, "write", "--npz", npz, "--npz-sha", field(t1, "npz_sha256"),
                     "--manifest", man, "--manifest-sha", field(t1, "manifest_sha256"), "--out", out)
        self.assertEqual(rc, 0, t2)
        return npz, man, out, t1, t2

    def check(self, out, sha):
        return run("--deploy", self.deploy, "check", "--cv", self.cv, "--out", out, "--out-sha", sha)

    # ---------------------------------------------------------------- the split passes, and equals one process
    def test_split_passes_with_the_digest_chain(self):
        npz, man, out, t1, t2 = self.read_write()
        self.assertIn(f"write: expects npz_sha256={field(t1, 'npz_sha256')}", t2.splitlines()[0])
        self.assertIn("every array equals the read step's in dtype, shape and bytes", t2)
        rc, t3 = self.check(out, field(t2, "out_sha256"))
        self.assertEqual(rc, 0, t3)
        self.assertIn(f"check: expects out_sha256={field(t2, 'out_sha256')}", t3.splitlines()[0])
        self.assertIn("WRITER-CONTROL PASS failures=0", t3)
        self.assertIn("CHECK rc=0 stub_calls=1", t3)

    def test_split_file_equals_the_single_process_file(self):
        import uproot
        import control1_content_check as cc
        _, _, out, _, _ = self.read_write()
        single = self.d / "single.root"
        self.w.write_data_file(single, *self._read_cv())
        failures = []
        with open(single, "rb") as a, open(out, "rb") as b:
            fa, fb = uproot.open(a), uproot.open(b)
            cc.compare_tree(fa, fb, "data", cc.STEP, failures)
            self.assertEqual(sorted(fa.classnames(recursive=False)), sorted(fb.classnames(recursive=False)))
            self.assertEqual(fa["dataPOTUsed"].member("fVal"), fb["dataPOTUsed"].member("fVal"))
        self.assertEqual(failures, [])

    def _read_cv(self):
        os.O_NOATIME = getattr(os, "O_NOATIME", 0)
        return self.w.read_cv_data(str(self.cv))

    # ---------------------------------------------------------------- the check compares content (FAIL, rc 3)
    def bad_file(self, cols, pot, leaves=None):
        out = self.d / "bad.root"
        saved = dict(self.w.LEAVES)
        if leaves:
            self.w.LEAVES.update(leaves)
        try:
            self.w.write_data_file(out, cols, pot)
        finally:
            self.w.LEAVES.clear()
            self.w.LEAVES.update(saved)
        from control2a_split import sha256_file  # noqa: E402  (HERE is on sys.path via the test runner's cwd)
        return out, sha256_file(out)

    def assert_control_fails(self, out, sha):
        rc, t = self.check(out, sha)
        self.assertEqual(rc, 3, t)
        self.assertIn("WRITER-CONTROL FAIL", t)
        self.assertIn("stub_calls=1", t)

    def test_fails_on_one_changed_row(self):
        cols = {k: v.copy() for k, v in self.cols.items()}
        cols["measured_pz"][1000] = np.nextafter(cols["measured_pz"][1000], np.inf)
        self.assert_control_fails(*self.bad_file(cols, self.pot))

    def test_fails_on_a_dropped_row(self):
        self.assert_control_fails(*self.bad_file({k: v[:-1] for k, v in self.cols.items()}, self.pot))

    def test_fails_on_a_leaf_type(self):
        self.assert_control_fails(*self.bad_file(self.cols, self.pot, {"measured_pass": ("i", "I")}))

    def test_fails_on_the_pot(self):
        self.assert_control_fails(*self.bad_file(self.cols, np.nextafter(self.pot, np.inf)))

    def test_fails_on_negative_zero_turned_positive(self):
        cols = {k: v.copy() for k, v in self.cols.items()}
        cols["measured"][7] = 0.0
        self.assert_control_fails(*self.bad_file(cols, self.pot))

    # ---------------------------------------------------------------- the digest chain refuses (rc 4)
    def test_check_refuses_a_file_that_is_not_the_write_steps(self):
        _, _, out, _, t2 = self.read_write()
        rc, t = self.check(out, "0" * 64)
        self.assertEqual(rc, 4, t)
        self.assertIn("the stub refuses", t)
        with open(out, "ab") as f:
            f.write(b"\0")
        rc, t = self.check(out, field(t2, "out_sha256"))
        self.assertEqual(rc, 4, t)

    def test_write_refuses_a_wrong_npz_or_manifest_digest(self):
        npz, man, _, t1, _ = self.read_write()
        for npz_sha, man_sha in (("0" * 64, field(t1, "manifest_sha256")), (field(t1, "npz_sha256"), "0" * 64)):
            rc, t = run("--deploy", self.deploy, "write", "--npz", npz, "--npz-sha", npz_sha, "--manifest", man,
                        "--manifest-sha", man_sha, "--out", self.d / "x.root")
            self.assertEqual(rc, 4, t)
            self.assertFalse((self.d / "x.root").exists())

    def test_write_refuses_an_array_unequal_to_the_read_steps(self):
        from control2a_split import sha256_file
        npz, man, _, t1, _ = self.read_write()
        with np.load(npz) as z:
            arrays = {k: z[k] for k in z.files}
        variants = {"bytes": dict(arrays, measured=np.where(np.arange(arrays["measured"].size) == 3, 9.0,
                                                           arrays["measured"])),
                    "dtype": dict(arrays, measured_pass=arrays["measured_pass"].astype(np.int64)),
                    "shape": dict(arrays, measured_pz=arrays["measured_pz"].reshape(1, -1))}
        for name, v in variants.items():
            with self.subTest(name):
                bad = self.d / f"{name}.npz"
                np.savez(bad, **v)
                rc, t = run("--deploy", self.deploy, "write", "--npz", bad, "--npz-sha", sha256_file(bad),
                            "--manifest", man, "--manifest-sha", field(t1, "manifest_sha256"),
                            "--out", self.d / f"{name}.root")
                self.assertEqual(rc, 4, t)
                self.assertIn("differs from the read step's", t)
                self.assertFalse((self.d / f"{name}.root").exists())

    def mutated_deploy(self, name, new_call):
        rel = "2d-unfolding/cov2d/cov2d_writer.py"
        d = self.d / name
        shutil.copytree(self.deploy, d)
        src = (d / rel).read_text()
        old = "    write_data_file(out, cols, pot)\n"
        self.assertEqual(src.count(old), 1)
        (d / rel).write_text(src.replace(old, new_call))
        return d

    def test_check_fails_when_the_stub_is_not_called(self):
        _, _, out, _, t2 = self.read_write()
        d = self.mutated_deploy("nocall", "    pass\n")
        rc, t = run("--deploy", d, "check", "--cv", self.cv, "--out", out, "--out-sha", field(t2, "out_sha256"))
        self.assertIn("WRITER-CONTROL PASS failures=0", t)  # the control alone would pass on the existing file
        self.assertEqual(rc, 5, t)
        self.assertIn("stub_calls=0", t)

    def test_check_fails_when_the_file_changes_under_it(self):
        _, _, out, _, t2 = self.read_write()
        d = self.mutated_deploy("append", "    write_data_file(out, cols, pot)\n    open(out, 'ab').write(b'\\0')\n")
        rc, t = run("--deploy", d, "check", "--cv", self.cv, "--out", out, "--out-sha", field(t2, "out_sha256"))
        self.assertEqual(rc, 6, t)
        self.assertIn("the file changed under the check", t)

    # ---------------------------------------------------------------- patch reach
    def test_a_raising_module_global_reaches_the_write(self):
        class Reached(Exception):
            pass

        def raising(*a, **k):
            raise Reached

        saved = self.w.write_data_file
        self.w.write_data_file = raising
        os.O_NOATIME = getattr(os, "O_NOATIME", 0)
        try:
            with self.assertRaises(Reached), contextlib.redirect_stdout(io.StringIO()):
                self.w.main(["control", "--out", str(self.d / "never.root"), "--cv", str(self.cv)])
        finally:
            self.w.write_data_file = saved
        self.assertFalse((self.d / "never.root").exists())

    def test_reach_passes_on_m(self):
        rc, t = run("--deploy", self.deploy, "reach")
        self.assertEqual(rc, 0, t)
        self.assertIn("the one use is writer_control's direct call", t)

    def test_reach_fails_on_each_other_path(self):
        rel = "2d-unfolding/cov2d/cov2d_writer.py"
        src = (self.deploy / rel).read_text()
        mutants = {
            "alias": src + "\n_keep = write_data_file\n",
            "partial": src.replace("import argparse\n", "import argparse\nfrom functools import partial\n", 1),
            "subprocess": src.replace("import argparse\n", "import argparse\nimport subprocess\n", 1),
            "getattr": src + "\n_g = globals()['write_data_file']\n",
            "default_arg": src.replace("def writer_control(cv: str, out: str)",
                                       "def writer_control(cv: str, out: str, _w=write_data_file)", 1),
        }
        for name, text in mutants.items():
            with self.subTest(name):
                self.assertNotEqual(text, src)
                d = self.d / name
                shutil.copytree(self.deploy, d)
                (d / rel).write_text(text)
                rc, t = run("--deploy", d, "reach")
                self.assertEqual(rc, 4, t)
                self.assertIn("REACH FAIL", t)
        d = self.d / "importer"
        shutil.copytree(self.deploy, d)
        p = d / "2d-unfolding/cov2d/cov2d.py"
        p.write_text(p.read_text() + "\nfrom cov2d_writer import write_data_file as _w\n")
        rc, t = run("--deploy", d, "reach")
        self.assertEqual(rc, 4, t)


if __name__ == "__main__":
    unittest.main()
