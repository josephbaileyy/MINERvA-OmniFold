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
                             normalized_sum=1.0e6, identity=None, input_size=None,
                             input_sha=None):
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
                                           else os.path.getsize(inputs_npz)),
                            # D2/audit: the source dump is bound by DIGEST, not only by size, so a
                            # same-size substitution cannot pair the certified target with a
                            # different dump. Computed from the fixture so a matching pair matches.
                            "sha256": (input_sha if input_sha is not None
                                       else drv.sha256_file(inputs_npz))},
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

    def test_same_size_source_substitution_is_caught(self):
        """The gap size-only binding left open: a re-dump of the same inventory with different
        values has the same length, so only the digest separates them."""
        with tempfile.TemporaryDirectory() as td:
            p, tgt, rec = self._pair(td)
            with open(p, "r+b") as fh:          # flip a byte; size unchanged
                fh.seek(-1, os.SEEK_END)
                b = fh.read(1)
                fh.seek(-1, os.SEEK_END)
                fh.write(bytes([b[0] ^ 0xFF]))
            with self.assertRaises(SystemExit) as cm:
                drv.assert_target_provenance(tgt, rec, p)
            self.assertIn("sha256", str(cm.exception))

    def test_receipt_without_source_digest_is_caught(self):
        with tempfile.TemporaryDirectory() as td:
            p, tgt, rec = self._pair(td)
            payload = json.load(open(rec))
            payload["input_preflight"].pop("sha256")
            json.dump(payload, open(rec, "w"))
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


# Every key of the frozen nominal policy -> the driver flag that sets it. RETYPED on purpose: derived
# from NOMINAL_SEED_POLICY it would follow a rename silently, and the point is a third independent
# statement (same device as test_pet_nominal_gate4_validator.py:69's retyped seed_policy literal).
POLICY_FLAGS = {"estimator_seed": "--estimator-seed", "subsample_seed": "--subsample-seed",
                "niter": "--niter", "epochs": "--epochs", "train_events": "--max-events",
                "batch_size": "--batch-size",
                # ADOPTED 2026-08-10: `lr_policy` is policy with NO FLAG -- deliberately not tunable
                # per run, because a per-run LR override is exactly how an artifact could claim the
                # adopted anneal while training under something else. None means "no flag exists and
                # none may be added"; test_no_flag_is_added_for_unflagged_policy enforces that, so a
                # future `--lr`/`--base-lr` cannot appear without this map being confronted.
                "lr_policy": None}


class LauncherRestatesNoPolicy(unittest.TestCase):
    """The launcher must own bound FOOTING only, never estimator configuration.

    Added 2026-08-06 after the failure it would have caught in 0.01s. Commit 2b2e5f1 moved the frozen
    policy niter 2 -> 3 in the driver and the validator but NOT in the launcher, which hardcoded
    `NITER=2` and passed `--niter "$NITER"`. Job 56410365 would have trained 8 GPU-hours and been
    rejected by `freeze:seed_policy`, which only fires on a FINISHED artifact. Caught while PENDING.

    Worse, the evidence was already on screen in a passing test: `test_selftest_config_gate_pass`
    runs the launcher, whose selftest echo printed `niter=2` into captured stdout, and asserted only
    that "CONFIG GATE PASS" appeared in it.

    NOT a self-agreement test: one side is the launcher's actual BYTES -- the artifact that drifted --
    and the other is a retyped list. Mutation-proved both ways."""

    def test_flag_map_covers_the_whole_policy(self):
        """A NEW policy key with no entry here would leave the next test silently blind to it."""
        self.assertEqual(set(POLICY_FLAGS), set(drv.NOMINAL_SEED_POLICY),
                         "POLICY_FLAGS and NOMINAL_SEED_POLICY disagree; a policy key was added or "
                         "renamed without extending this map, so the launcher check below would not "
                         "cover it")

    @staticmethod
    def _executable_lines(path):
        """Lines the shell actually runs: comment-only lines dropped.

        A whole-file substring search cannot tell `--niter "$NITER"` from a comment EXPLAINING why
        `--niter` is no longer passed, and the first draft of this test failed on its own rationale
        comment. That is the same trap as
        test_resume_guard.py::test_every_rg_caller_sources_the_library_first, which reads the first
        MENTION of an rg_ helper as its first use. Checking executable lines keeps the test about
        behaviour instead of about prose."""
        return [ln for ln in open(path).read().splitlines()
                if ln.strip() and not ln.lstrip().startswith("#")]

    def test_launcher_passes_no_policy_owned_flag(self):
        body = "\n".join(self._executable_lines(LAUNCHER))
        found = sorted(f for f in POLICY_FLAGS.values() if f and f in body)
        self.assertEqual(found, [], (
            "the launcher restates policy the driver already defaults from NOMINAL_SEED_POLICY: "
            f"{found}. Remove the flag rather than updating its value -- an override here makes "
            "launcher-vs-policy drift possible, and it is only detected after a full training run."))

    def test_no_flag_is_added_for_unflagged_policy(self):
        """A policy key mapped to None must stay flagless -- in the DRIVER as well as the launcher.

        `lr_policy` is the adopted anneal. If someone later adds `--lr` or `--base-lr`, a run could
        declare the adopted policy in seed_policy while training under an override, which is the exact
        claim-without-measurement failure the realized-LR assertion exists to prevent. Cheaper to
        forbid the flag than to detect the divergence afterwards.

        JOSEPH 2026-08-10, AND THIS IS THE REASON TO KEEP IT -- do not re-add the flag as a convenience:
        FORBIDDING THE FLAG IS WHAT MAKES THE DRIVER PIN LOAD-BEARING FOR THE LR POLICY. With no flag,
        changing the anneal requires editing the driver, which moves its sha256, breaks the Gate-4 pin,
        and forces a re-issue -- so a policy change cannot happen without the gate noticing. WITH a
        flag, a run could declare the adopted policy in `seed_policy` and train under something else
        with EVERY sha UNCHANGED. That is precisely the fingerprint hole closed on 2026-08-10 (a string
        meaning "features" being read as meaning "the estimator"), reopened at the command line.
        """
        unflagged = [k for k, v in POLICY_FLAGS.items() if v is None]
        self.assertTrue(unflagged, "this test is vacuous if no key is unflagged")
        drv_src = open(drv.__file__, encoding="utf-8").read()
        for bad in ("--lr", "--base-lr", "--learning-rate", "--annealed-lr"):
            self.assertNotIn(f'add_argument("{bad}"', drv_src,
                             f"{bad} would make the adopted lr_policy overridable per run")
        body = "\n".join(self._executable_lines(LAUNCHER))
        for bad in ("--lr ", "--base-lr", "--learning-rate"):
            self.assertNotIn(bad, body, f"the launcher must not set {bad}")

    def test_the_target_footing_pins_are_still_there(self):
        """The converse: removing policy must not have removed the footing this launcher DOES own."""
        body = "\n".join(self._executable_lines(LAUNCHER))
        for keep in ("EXPECTED_TARGET_SHA", "EXPECTED_TARGET_SIZE", "GATE3_MANIFEST"):
            self.assertIn(keep, body, f"{keep} is footing, not policy; it must stay")


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



class FinalCheckpointIsPersisted(unittest.TestCase):
    """BEN-043: the driver must persist the weights that actually produced `weights_push`.

    Static source assertions, because the behaviour they guard lives after `MultiFold.Unfold()` on a
    GPU and cannot be exercised in a login-safe test. Each one is written so that reverting the fix
    makes it FAIL -- the mutation proof is in `test_the_prefix_source_would_fail` below, which
    reconstructs the pre-fix source and requires the guards to fire.
    """

    @staticmethod
    def _src():
        return open(DRIVER).read()

    def test_saves_the_trained_clones_not_the_originals(self):
        """`of.model1`/`of.model2` are never reassigned, so saving them persists a random init."""
        src = self._src()
        self.assertIn("of.step1_models", src)
        self.assertIn("of.step2_models", src)
        # the specific wrong implementation must not appear
        self.assertNotIn("of.model2.save_weights", src)
        self.assertNotIn("of.model1.save_weights", src)

    def test_contract_points_at_the_final_checkpoint(self):
        """`extract_fullevent_fps.py:253` reads `step2_checkpoint`; it must be the final weights."""
        src = self._src()
        self.assertIn('"step2_checkpoint": final_ckpt[2]', src)
        self.assertIn('"step1_checkpoint": final_ckpt[1]', src)
        # the best-epoch path is kept, but under its own key
        self.assertIn('"step2_checkpoint_best_epoch"', src)
        self.assertIn('"checkpoint_semantics"', src)

    def test_round_trip_is_verified_and_fails_closed(self):
        """Saving without checking the file reads back is the same class of defect as BEN-043."""
        src = self._src()
        self.assertIn("load_weights(_p)", src)
        self.assertIn("np.array_equal", src)
        self.assertIn("does not round-trip", src)

    def test_empty_model_list_fails_closed(self):
        src = self._src()
        self.assertIn("step2_models empty", src.replace("step{_stepn}_models empty",
                                                        "step2_models empty"))

    def test_the_prefix_source_would_fail(self):
        """POWER PROOF: reconstruct the pre-fix source and require the guards above to fire.

        Without this, all four assertions could be vacuous -- the exact failure BEN-040 and BEN-032
        are about. The reconstruction removes the final-save block and restores the old contract line.
        """
        src = self._src()
        pre = src.replace('"step2_checkpoint": final_ckpt[2],',
                          '"step2_checkpoint": os.path.abspath(os.path.join(\n'
                          '            weights_folder, f"OmniFold_{mf_name}_iter0_step2.weights.h5")),')
        pre = pre.replace('"step1_checkpoint": final_ckpt[1],', "")
        pre = pre.replace('"step2_checkpoint_best_epoch"', '"_removed_best_epoch"')
        pre = pre.replace('"checkpoint_semantics"', '"_removed_semantics"')
        pre = pre.replace("of.step1_models", "_removed1").replace("of.step2_models", "_removed2")
        pre = pre.replace("load_weights(_p)", "_removed_roundtrip()")
        pre = pre.replace("does not round-trip", "_removed_message")

        self.assertNotIn('"step2_checkpoint": final_ckpt[2]', pre)
        self.assertNotIn('"step1_checkpoint": final_ckpt[1]', pre)
        self.assertNotIn('"step2_checkpoint_best_epoch"', pre)
        self.assertNotIn('"checkpoint_semantics"', pre)
        self.assertNotIn("of.step1_models", pre)
        self.assertNotIn("of.step2_models", pre)
        self.assertNotIn("load_weights(_p)", pre)
        self.assertNotIn("does not round-trip", pre)
        # and the reconstruction must differ from the real source, or it proved nothing
        self.assertNotEqual(pre, src)



if __name__ == "__main__":
    unittest.main(verbosity=2)
