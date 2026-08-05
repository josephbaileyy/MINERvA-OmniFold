"""Login-safe tests for the Gate-4 publication PET NOMINAL launcher + driver.

No GPU / no TF / no training / no submit. Exercise: the fail-closed publication config gate
(assert_publication_config routed through the driver), the launcher's no-auto-submit guard, bash
syntax, driver byte-compile, and negative fingerprint/inventory cases via synthetic g2 npz fixtures."""
import json
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


def synth_target_and_receipt(td, inputs_npz, *, rows=8, status="PASS",
                             fingerprint="pet-fullevent-fps-v1",
                             target_mode="negweight-refined", learned=True, bootstrap_seed=None,
                             normalized_sum=1.0e6, identity=None, input_size=None):
    """A precomputed target plus the Gate-2 runtime receipt that owns it (D2 fixture).

    Mirrors only the fields `assert_target_provenance` reads, and the sha is computed from the file
    just written so a matching pair is genuinely matching rather than asserted to be.
    """
    tgt = os.path.join(td, "TARGET.npy")
    np.save(tgt, np.linspace(0.5, 2.0, rows).astype(np.float32))
    rec = {
        "status": status,
        "verdict": "GATE2_CANONICAL_RUNTIME_PASS_INDEPENDENT_PROMOTION_PENDING",
        "step1_feed": {"rows": rows, "normalized_sum": normalized_sum,
                       "weights": {"sha256": drv.sha256_file(tgt),
                                   "size_bytes": os.path.getsize(tgt)}},
        "runtime_target": {"estimator_fingerprint": fingerprint, "target_mode": target_mode,
                           "refinement_is_learned_production": learned,
                           "bootstrap_seed": bootstrap_seed, "n_measured_rows": rows,
                           "input_identity_hashes": identity or {"sig": "1" * 64, "data": "2" * 64,
                                                                 "bkg": "3" * 64}},
        "input_preflight": {"size_bytes": (input_size if input_size is not None
                                           else os.path.getsize(inputs_npz))},
    }
    rp = os.path.join(td, "RECEIPT.json")
    with open(rp, "w") as fh:
        json.dump(rec, fh)
    return tgt, rp


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
        # --config-gate-only must return 0 without importing TF / training.
        # D2 (2026-08-04): it now ALSO binds the precomputed target to its receipt, so the fixture
        # has to supply one. That is deliberate -- Step 2b's question is "may this train?", and a
        # nominal that cannot name a certified target is not launchable.
        with tempfile.TemporaryDirectory() as td:
            p = synth_g2_npz(os.path.join(td, "G2_target.npz"))
            tgt, rec = synth_target_and_receipt(td, p)
            rc = drv.main(["--inputs", p, "--config-gate-only",
                           "--target-npy", tgt, "--target-receipt", rec])
            self.assertEqual(rc, 0)
            self.assertNotIn("tensorflow", sys.modules)   # TF never imported by the gate path

    def test_config_gate_only_fails_closed_without_a_target(self):
        """No fallback. Pre-D2 the driver rebuilt the refinement in process (audit J04) and would
        happily run with no certified target at all."""
        with tempfile.TemporaryDirectory() as td:
            p = synth_g2_npz(os.path.join(td, "G2_target.npz"))
            with self.assertRaises(SystemExit):
                drv.main(["--inputs", p, "--config-gate-only",
                          "--target-npy", os.path.join(td, "absent.npy"),
                          "--target-receipt", os.path.join(td, "absent.json")])


class TargetProvenanceGate(unittest.TestCase):
    """D2: the nominal must consume the array Gate-2 certified, and prove it is that array.

    Each case breaks exactly ONE binding, because a gate that only fails when several things are
    wrong at once is not a gate on any of them individually.
    """

    def _pair(self, td, **kw):
        p = synth_g2_npz(os.path.join(td, "G2_target.npz"))
        tgt, rec = synth_target_and_receipt(td, p, **kw)
        return p, tgt, rec

    def test_matching_pair_passes(self):
        with tempfile.TemporaryDirectory() as td:
            p, tgt, rec = self._pair(td)
            out = drv.assert_target_provenance(tgt, rec, p)
            self.assertEqual(out["status"], "PASS")

    def test_target_content_change_is_caught(self):
        with tempfile.TemporaryDirectory() as td:
            p, tgt, rec = self._pair(td)
            np.save(tgt, np.linspace(0.5, 2.0, 8).astype(np.float32) * 1.01)   # same shape/size
            with self.assertRaises(SystemExit) as cm:
                drv.assert_target_provenance(tgt, rec, p)
            self.assertIn("sha256", str(cm.exception))

    def test_missing_target_is_caught(self):
        with tempfile.TemporaryDirectory() as td:
            p, tgt, rec = self._pair(td)
            os.remove(tgt)
            with self.assertRaises(SystemExit):
                drv.assert_target_provenance(tgt, rec, p)

    def test_non_pass_receipt_is_caught(self):
        with tempfile.TemporaryDirectory() as td:
            p, tgt, rec = self._pair(td, status="GATE_2_NOT_YET_PASS")
            with self.assertRaises(SystemExit):
                drv.assert_target_provenance(tgt, rec, p)

    def test_wrong_fingerprint_is_caught(self):
        with tempfile.TemporaryDirectory() as td:
            p, tgt, rec = self._pair(td, fingerprint="pet-reduced-fps-cross")
            with self.assertRaises(SystemExit):
                drv.assert_target_provenance(tgt, rec, p)

    def test_control_target_mode_is_caught(self):
        with tempfile.TemporaryDirectory() as td:
            p, tgt, rec = self._pair(td, target_mode="purity")
            with self.assertRaises(SystemExit):
                drv.assert_target_provenance(tgt, rec, p)

    def test_substitute_refiner_is_caught(self):
        """refinement_is_learned_production=False is the flag Step 4 names as the reason Delta
        cannot produce a nominal; a target built that way cannot certify one either."""
        with tempfile.TemporaryDirectory() as td:
            p, tgt, rec = self._pair(td, learned=False)
            with self.assertRaises(SystemExit):
                drv.assert_target_provenance(tgt, rec, p)

    def test_bootstrap_replica_target_is_caught(self):
        with tempfile.TemporaryDirectory() as td:
            p, tgt, rec = self._pair(td, bootstrap_seed=7)
            with self.assertRaises(SystemExit):
                drv.assert_target_provenance(tgt, rec, p)

    def test_source_dump_size_mismatch_is_caught(self):
        with tempfile.TemporaryDirectory() as td:
            p, tgt, rec = self._pair(td, input_size=12345)
            with self.assertRaises(SystemExit):
                drv.assert_target_provenance(tgt, rec, p)

    def test_unrecorded_normalization_is_caught(self):
        with tempfile.TemporaryDirectory() as td:
            p, tgt, rec = self._pair(td, normalized_sum=None)
            with self.assertRaises(SystemExit):
                drv.assert_target_provenance(tgt, rec, p)


class ConsumedInventoryBinding(unittest.TestCase):
    """Row ORDER, the property a file hash cannot express."""

    IDENT = {"sig": "1" * 64, "data": "2" * 64, "bkg": "3" * 64}

    def _rec(self, ident=None):
        return {"runtime_target": {"input_identity_hashes": ident or self.IDENT}}

    def test_matching_inventory_passes(self):
        drv.assert_consumed_inventory_matches_receipt(
            {"input_identity_hashes": dict(self.IDENT)}, self._rec())

    def test_reordered_inventory_is_caught(self):
        consumed = dict(self.IDENT)
        consumed["data"] = "9" * 64          # same rows, different order => different order hash
        with self.assertRaises(SystemExit) as cm:
            drv.assert_consumed_inventory_matches_receipt(
                {"input_identity_hashes": consumed}, self._rec())
        self.assertIn("row order", str(cm.exception))

    def test_unverified_inventory_is_caught(self):
        """verify_identities=False leaves nothing to compare, which must not read as agreement."""
        with self.assertRaises(SystemExit):
            drv.assert_consumed_inventory_matches_receipt({"input_identity_hashes": {}}, self._rec())

    def test_receipt_without_identity_hashes_is_caught(self):
        with self.assertRaises(SystemExit):
            drv.assert_consumed_inventory_matches_receipt(
                {"input_identity_hashes": dict(self.IDENT)}, {"runtime_target": {}})


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
