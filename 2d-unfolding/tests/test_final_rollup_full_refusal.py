"""uq/final_rollup_full.sh must not overwrite its two sha-pinned products.

Steps (a) and (b) of the superseded rollup write
uq/seedscan_lgbm_ml/uq_covariance_ml.root (an input of the adopted VL172
rollup) and uq/bootstrap_MEFHC_300/uq_covariance_boot300.root (the VL162 band)
in place. The script now refuses while either exists.

Each case runs the script with bash in a throwaway tree that satisfies its
preconditions, with a stub `python` first on PATH that only records its
arguments, so no analysis runs. The control case runs the script as it was at
PRE_GUARD_COMMIT and shows that it reached step (a) with the pinned file
present. Needs bash and git; the control skips if git cannot supply the blob.
"""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[2]
SCRIPT = REPO / "2d-unfolding" / "uq" / "final_rollup_full.sh"
PRE_GUARD_COMMIT = "5ac9706a"
PINNED = ("uq/seedscan_lgbm_ml/uq_covariance_ml.root",
          "uq/bootstrap_MEFHC_300/uq_covariance_boot300.root")


class FinalRollupRefusalTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.u2d = root / "2d-unfolding"
        (self.u2d / "uq").mkdir(parents=True)
        (self.u2d / "seedscan_lgbm").mkdir()
        (root / "setup_salloc_env.sh").write_text("")
        for rel in ("runEventLoopOmniFold_MEFHC_universes_full.root",
                    "uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root",
                    "uq/2d_xsec_MEFHC_5iter_lgbm_boot1.root",
                    "seedscan_lgbm/2d_xsec_MEFHC_5iter_lgbm_seed1.root"):
            (self.u2d / rel).write_text("x")
        for k in range(100):
            (self.u2d / f"uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_Flux_{k}.root").write_text("x")
        self.bin = root / "bin"
        self.bin.mkdir()
        self.calls = root / "python_calls.txt"
        stub = self.bin / "python"
        stub.write_text(f'#!/bin/bash\necho "$*" >> "{self.calls}"\n')
        stub.chmod(0o755)

    def tearDown(self):
        self.tmp.cleanup()

    def place_pinned(self):
        for rel in PINNED:
            p = self.u2d / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"pinned " + rel.encode())

    def run_script(self, text):
        script = self.u2d / "uq" / "final_rollup_full.sh"
        script.write_text(text)
        env = dict(os.environ, PATH=f"{self.bin}{os.pathsep}{os.environ['PATH']}")
        return subprocess.run(["bash", str(script)], env=env, capture_output=True, text=True)

    def test_refuses_while_a_pinned_product_exists(self):
        for keep in PINNED:
            with self.subTest(present=keep):
                self.place_pinned()
                other = next(r for r in PINNED if r != keep)
                (self.u2d / other).unlink()
                archived = self.u2d / "uq/universe_stage2_MEFHC_full/uq_universe_covariance_full.root"
                archived.parent.mkdir(parents=True, exist_ok=True)
                archived.write_text("previous rollup")
                p = self.run_script(SCRIPT.read_text())
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.assertIn("refusing to overwrite", p.stdout)
                self.assertFalse(self.calls.exists(), "a step ran before the refusal")
                self.assertTrue(archived.exists(), "the archive step moved files before the refusal")
                self.assertEqual((self.u2d / keep).read_bytes(), b"pinned " + keep.encode())

    def test_runs_when_no_pinned_product_exists(self):
        p = self.run_script(SCRIPT.read_text())
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("--outdir uq/seedscan_lgbm_ml", self.calls.read_text())

    def test_control_pre_guard_script_overwrote(self):
        g = subprocess.run(["git", "-C", str(REPO), "show",
                            f"{PRE_GUARD_COMMIT}:2d-unfolding/uq/final_rollup_full.sh"],
                           capture_output=True, text=True)
        if g.returncode != 0:
            self.skipTest(f"git cannot supply {PRE_GUARD_COMMIT}")
        self.place_pinned()
        p = self.run_script(g.stdout)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("--outdir uq/seedscan_lgbm_ml --out-root uq_covariance_ml.root",
                      self.calls.read_text())


if __name__ == "__main__":
    unittest.main()
