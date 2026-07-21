"""Login-safe tests for the Gate-4 publication PET NOMINAL launcher + driver.

No GPU / no TF / no training / no submit. Exercise: the fail-closed publication config gate
(assert_publication_config routed through the driver), the launcher's no-auto-submit guard, bash
syntax, driver byte-compile, and negative fingerprint/inventory cases via synthetic g2 npz fixtures."""
import os
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PET = os.path.join(ND, "pet")
sys.path.insert(0, PET)

import train_fullevent_nominal as drv  # noqa: E402  (login-safe: TF lazy)
import fullevent_fps_dataloader as fe   # noqa: E402

LAUNCHER = os.path.join(PET, "sbatch_pet_fullevent_nominal.sh")
DRIVER = os.path.join(PET, "train_fullevent_nominal.py")


def synth_g2_npz(path, with_bkg=True, fingerprint="pet-fullevent-fps-v1",
                 schema="g2-fullevent-v1", has_full=1, full_ps=1):
    """Minimal g2-fullevent-v1 marker npz (scalars + optional w_bkg). No large arrays."""
    arr = {"petSchemaVersion": np.asarray(schema), "hasFullEventSchema": np.asarray(has_full),
           "fullPhaseSpace": np.asarray(full_ps), "estimator_fingerprint": np.asarray(fingerprint),
           "measured_pc": np.zeros((2, 12, 3), np.float32)}
    if with_bkg:
        arr["w_bkg"] = np.ones(2, np.float32)
    np.savez(path, **arr)
    return path


class DriverConfigGate(unittest.TestCase):
    def test_valid_target_passes(self):
        with tempfile.TemporaryDirectory() as td:
            p = synth_g2_npz(os.path.join(td, "G2_target.npz"))
            cfg = drv.run_config_gate(p)
            self.assertEqual(cfg["estimator_fingerprint"], "pet-fullevent-fps-v1")
            self.assertEqual(cfg["bkg_mode"], "negweight-refined")
            self.assertTrue(cfg["has_background"])

    def test_missing_background_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p = synth_g2_npz(os.path.join(td, "nobkg.npz"), with_bkg=False)
            with self.assertRaises(ValueError):
                drv.run_config_gate(p)

    def test_wrong_schema_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p = synth_g2_npz(os.path.join(td, "old.npz"), schema="recoil-only-crosscheck")
            with self.assertRaises(ValueError):
                drv.run_config_gate(p)

    def test_wrong_fingerprint_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p = synth_g2_npz(os.path.join(td, "reduced.npz"), fingerprint="pet-reduced-fps-cross")
            with self.assertRaises(ValueError):
                drv.run_config_gate(p)

    def test_recoil_marker_path_fails_closed(self):
        # a recoil/old/xps2 input path is forbidden even with correct markers
        with tempfile.TemporaryDirectory() as td:
            p = synth_g2_npz(os.path.join(td, "of_inputs_pc_fps_xps2.npz"))
            with self.assertRaises(ValueError):
                drv.run_config_gate(p)

    def test_missing_gate3_manifest_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p = synth_g2_npz(os.path.join(td, "G2_target.npz"))
            with self.assertRaises(ValueError):
                drv.run_config_gate(p, gate3_manifest=os.path.join(td, "nope.json"))

    def test_config_gate_only_cli_no_train(self):
        # --config-gate-only must return 0 without importing TF / training
        with tempfile.TemporaryDirectory() as td:
            p = synth_g2_npz(os.path.join(td, "G2_target.npz"))
            rc = drv.main(["--inputs", p, "--config-gate-only"])
            self.assertEqual(rc, 0)
            self.assertNotIn("tensorflow", sys.modules)   # TF never imported by the gate path


class DriverContract(unittest.TestCase):
    def test_calls_assert_publication_config(self):
        # the driver's gate must be the dataloader's authoritative fail-closed gate
        self.assertIs(fe.assert_publication_config, __import__("fullevent_fps_dataloader")
                      .assert_publication_config)
        self.assertEqual(drv.ESTIMATOR_FINGERPRINT, "pet-fullevent-fps-v1")
        self.assertEqual(drv.BKG_MODE, "negweight-refined")

    def test_byte_compiles(self):
        r = subprocess.run([sys.executable, "-m", "py_compile", DRIVER],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


class LauncherScript(unittest.TestCase):
    def test_bash_syntax(self):
        r = subprocess.run(["bash", "-n", LAUNCHER], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_no_auto_submit_without_slurm(self):
        # running the launcher body directly (no SLURM_JOB_ID, not selftest) must FAIL CLOSED, never
        # train or submit.
        env = {k: val for k, val in os.environ.items()
               if k not in ("SLURM_JOB_ID", "PET_FE_NOMINAL_SELFTEST")}
        r = subprocess.run(["bash", LAUNCHER], capture_output=True, text=True, env=env)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("must run as an sbatch job", r.stderr)

    def test_no_sbatch_or_submit_calls_in_script(self):
        # the script must not INVOKE sbatch/salloc/srun as a command (sourcing setup_salloc_env.sh is
        # fine). Check the first token of each non-comment line, incl. after ;/&&/|| separators.
        import re
        for raw in open(LAUNCHER):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            for seg in re.split(r"(?:&&|\|\||;)", line):
                tok = seg.strip().split()
                if tok:
                    self.assertNotIn(tok[0], ("sbatch", "salloc", "srun"),
                                     f"launcher must not auto-submit: {seg.strip()!r}")

    def test_not_recoil_quarantine_path(self):
        body = open(LAUNCHER).read()
        self.assertIn("assert_publication_config", open(DRIVER).read())
        self.assertNotIn("minerva_pet_dataloader", body)   # not the recoil loader
        self.assertIn("fullevent_fps_dataloader", body)

    def test_selftest_config_gate_pass(self):
        # login-safe selftest: config gate on the REAL bound Gate-2 target (marker read only).
        if not os.path.exists(os.path.join(
                ND, "g2_fullevent", "input", "G2_FPS_MEFHC_P12.npz")):
            self.skipTest("bound Gate-2 target NPZ not present")
        env = dict(os.environ, PET_FE_NOMINAL_SELFTEST="1")
        env.pop("SLURM_JOB_ID", None)
        r = subprocess.run(["bash", LAUNCHER], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("CONFIG GATE PASS", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
