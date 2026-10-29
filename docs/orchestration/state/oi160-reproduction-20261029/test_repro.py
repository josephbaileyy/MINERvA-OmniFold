"""Tests for the OI-160 reproduction's wrapper and comparison, both directions, on synthetic files."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import repro_compare  # noqa: E402

LIB_CORE = "def omnifold_loop():\n    return 'lib'\n"
FAKE_CORE = "def omnifold_loop():\n    return 'canonical'\n"


class WrapperTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="oi160-wrap-"))
        self.lib = self.tmp / "lib"; self.lib.mkdir()
        (self.lib / "omnifold_nn_core.py").write_text(LIB_CORE)
        (self.lib / "xsec_nd.py").write_text("X = 1\n")
        self.canon = self.tmp / "canonical" / "nd-unfolding"; self.canon.mkdir(parents=True)
        (self.canon / "omnifold_nn_core.py").write_text(FAKE_CORE)   # the decoy the script would pick up
        (self.canon / "xsec_nd.py").write_text("X = 2\n")
        (self.canon / "only_here.py").write_text("Y = 3\n")

    def script(self, extra=""):
        p = self.tmp / "bootstrap_nd.py"
        p.write_text(
            "import sys\n"
            f"_ND={str(self.canon)!r}\n"
            "if _ND not in sys.path: sys.path.insert(0,_ND)\n"
            "from omnifold_nn_core import omnifold_loop\n"
            "import xsec_nd\n" + extra +
            "open(sys.argv[sys.argv.index('--out')+1],'w').write(omnifold_loop()+str(xsec_nd.X))\n")
        return p

    def run_wrapper(self, script):
        out, prov = self.tmp / "out.txt", self.tmp / "prov.json"
        r = subprocess.run([sys.executable, "-I", "-B", str(HERE / "repro_run.py"), "--script", str(script),
                            "--lib", str(self.lib), "--forbidden-root", str(self.canon.parent),
                            "--provenance", str(prov), "--", "--out", str(out)],
                           capture_output=True, text=True, cwd=self.tmp)
        return r, out, json.loads(prov.read_text())

    def test_the_lib_modules_are_used_not_the_canonical_decoys(self):
        r, out, prov = self.run_wrapper(self.script())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(out.read_text(), "lib1")
        self.assertTrue(prov["preimported_under_lib"])
        self.assertEqual(prov["modules_under_forbidden_root"], [])

    def test_a_module_only_in_the_canonical_root_is_refused(self):
        r, _, prov = self.run_wrapper(self.script("import only_here\n"))
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertTrue(any(m.startswith("only_here=") for m in prov["modules_under_forbidden_root"]))


def npz(path, values, seed=1):
    np.savez_compressed(path, seed=seed, xsec_flat=np.asarray(values, float), shape=np.array([len(values)]),
                        total_xsec=float(np.sum(values)))
    return path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class CompareTests(unittest.TestCase):
    TOP, PRE, OTHER = [1.0, 2.0, 0.0, 4.0], [1.01, 1.98, 0.0, 4.05], [0.9, 2.1, 0.1, 3.9]

    def readout(self, a1, a2, b1, top=None, pre=None, pin_ok=True):
        d = Path(tempfile.mkdtemp(prefix="oi160-cmp-"))
        files = {}
        for name, vals in (("A1", a1), ("A2", a2), ("B1", b1), ("top", top or self.TOP), ("pre", pre or self.PRE)):
            files[name] = d / f"{name}.npz"
            if vals is not None:
                npz(files[name], vals)
        out = d / "readout.json"
        argv = ["--a1", str(files["A1"]), "--a2", str(files["A2"]), "--b1", str(files["B1"]),
                "--s-top", str(files["top"]), "--s-pre", str(files["pre"]), "--out", str(out),
                "--s-top-sha256", sha(files["top"]) if pin_ok else "0" * 64, "--s-pre-sha256", sha(files["pre"])]
        code = repro_compare.main(argv)
        return code, (json.loads(out.read_text()) if out.exists() else None)

    def test_R2_when_the_corrected_code_reproduces_the_top_level_file(self):
        code, r = self.readout(self.TOP, self.TOP, self.PRE)
        self.assertEqual((code, r["outcome"]), (0, "R2"))
        self.assertTrue(r["K1_A1_equals_A2"] and r["K2_B1_equals_S_pre"])

    def test_R1_when_the_old_code_reproduces_the_top_level_file(self):
        self.assertEqual(self.readout(self.OTHER, self.OTHER, self.TOP)[1]["outcome"], "R1")

    def test_THIRD_when_the_control_holds_and_neither_reproduces_the_top_level_file(self):
        self.assertEqual(self.readout(self.OTHER, self.OTHER, self.PRE)[1]["outcome"], "THIRD")

    def test_INCONCLUSIVE_when_today_reproduces_neither_stored_file(self):
        b1 = [1.02, 1.97, 0.0, 4.06]
        self.assertEqual(self.readout(self.OTHER, self.OTHER, b1)[1]["outcome"], "INCONCLUSIVE")

    def test_VOID_when_the_corrected_code_does_not_reproduce_itself(self):
        self.assertEqual(self.readout(self.OTHER, [0.8, 2.2, 0.0, 3.8], self.PRE)[1]["outcome"], "VOID")

    def test_one_ulp_is_a_difference_there_is_no_tolerance(self):
        nudged = list(self.TOP); nudged[1] = np.nextafter(nudged[1], 3.0)
        r = self.readout(nudged, nudged, self.PRE)[1]
        self.assertFalse(r["A1_equals_S_top"])
        self.assertEqual(r["outcome"], "THIRD")

    def test_a_missing_old_code_output_matches_nothing(self):
        r = self.readout(self.TOP, self.TOP, None)[1]
        self.assertFalse(r["B1_equals_S_top"] or r["K2_B1_equals_S_pre"])
        self.assertEqual(r["outcome"], "R2")

    def test_a_stored_file_that_is_not_the_pinned_one_is_refused(self):
        code, r = self.readout(self.TOP, self.TOP, self.PRE, pin_ok=False)
        self.assertEqual((code, r), (1, None))


if __name__ == "__main__":
    unittest.main()
