# VERDICT
## ENVIRONMENT
/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3
Python 3.11.14
## P1: F-7(b) PIN GATE
--- NO EXCLUSION ---
rc: 2
[p4] COULD NOT LOOK: tmp_pins.json records no preflight-exclusion digest. A pin that cannot express the exclusion cannot satisfy 7.0.15, and an absent record is not an unchanged exclusion. Re-write the pin with --write-pins.
--- WRONG DIGEST ---
rc: 3
[p4] EXCLUSION MOVED: nd-unfolding/mnv_preflight_exclusions.json
[p4]   pinned   sha256=000
[p4]   observed sha256=2d4ee2e9e6049098e356788f322236a18f9b1cbdb85b4b6cb8cbaadd206b2424
[p4] The 7.0.13 preflight exclusion is not the one this pin was written against. This fires in BOTH directions -- a widened exclusion and a narrowed one are both a changed guarding boundary -- and it is a VIOLATION, not a note.
--- REAL DIGEST ---
rc: 3
[p4] 6 VIOLATION(S):
[p4]   tmp_inv/a.jsonl (pid None) /tmp/grade-stack-20260826/pin/dummy.py: no guard was installed, so this record measures nothing
[p4]   tmp_inv/a.jsonl (pid None) /tmp/grade-stack-20260826/pin/dummy.py: no `checked_provenance`. A bare zero cannot distinguish 'the guard installed and resolved nothing' from 'no guard was installed', and this record predates the field that says which.
[p4]   tmp_inv/a.jsonl (pid None) /tmp/grade-stack-20260826/pin/dummy.py: checked == None; the guard resolved no absolute origin at all, so its silence is not evidence
[p4]   tmp_inv/a.jsonl (pid None) /tmp/grade-stack-20260826/pin/dummy.py: the emptiness flags are ABSENT. An absent key cannot distinguish 'no repository import occurred' from 'the inventory did not run'.
[p4]   /tmp/grade-stack-20260826/pin/dummy.py: no pinned import set. A new entrypoint on the path is a change that has to be looked at, not absorbed.
[p4]   dummy.py: pinned but NO inventory was produced for it. A missing inventory is a failure, not a gap.
import pathlib
# makes a tool read the wrong tree. `parents[1]` because this file sits at <repo>/nd-unfolding/.
_REPO = pathlib.Path(__file__).resolve().parents[1]
write-pins test rc: 0
[p4] wrote 1 pinned import set(s) to tmp_pins.json from 1 inventory record(s)
[p4]   exclusion pinned: nd-unfolding/mnv_preflight_exclusions.json sha256=2d4ee2e9e6049098e356788f322236a18f9b1cbdb85b4b6cb8cbaadd206b2424
[p4]   /tmp/grade-stack-20260826/pin/dummy.py: 0 module(s) []
## P2: SUCCESSOR PROBE
Diff to 2026-08-20 parent lines: 0
--- docs/orchestration/state/probe-oi136-sys-path-hijack-20260820.py	2026-08-26 14:16:26.761963071 -0700
+++ docs/orchestration/state/probe-oi136-sys-path-hijack-20260826.py	2026-08-26 14:16:26.765963023 -0700
+# SUCCESSOR PROBE, 2026-08-26. Identical to probe-oi136-sys-path-hijack-20260820.py except for
+# POSITIVE_CONTROLS below. The 08-20 artifact is UNCHANGED and still on disk: a probe is a RECORD of
+# what was run, and editing it would falsify that record.
+#
+# WHY A SUCCESSOR WAS NEEDED. `3d-unfolding/unfold_3d_omnifold_unbinned.py` was a declared positive
+# control AND became a repair target -- main repaired it in the 2026-08-23 authorized sweep
+# (c752f73e, a0a84a2e). A control that is also a repair target makes this probe exit 2,
+# `CANNOT CHECK :: positive control(s) absent`, the moment the repair lands, and the ratchet that
+# parses this probe's output fails with it. That is the SECOND time this exact shape has occurred:
+# `./nd-unfolding/unfold_nd_omnifold_unbinned.py` was retired for the same reason on 2026-08-22.
+# The pattern is now twice-observed and is recorded here rather than only in the test.
+#
+# WHY THIS REPLACEMENT AND NOT ANOTHER, chosen from THIS probe's own post-repair fail-open output
+# (45 paths, sha256 4201aceed0604f92a3ec88591fd4e471cb723323fb01b88184024d97d6c36c8b) -- the same
+# selection rule the 08-22 retirement used. `2d-unfolding/unfold_2d_omnifold_unbinned.py` is the
+# PUBLISHED 2D ARM, which Joseph ruled on 2026-08-23 to LEAVE: reachable in the k=0 static closure
+# but dormant. A file carrying a standing ruling AGAINST repair cannot silently become a repair
+# target, which is precisely the failure mode that retired the previous two controls. Its sha256 is
+# additionally pinned in three places needing three different treatments, and advancing the live one
+# requires a Gate-2 re-run producing bit-identical weights rather than a commit -- so it is the most
+# stable control available in this set, not merely a convenient one.
-                     "3d-unfolding/unfold_3d_omnifold_unbinned.py")
+                     "2d-unfolding/unfold_2d_omnifold_unbinned.py")
## P3: FAILOPEN CONSTANTS
Probe RC: 0
  [114 .py contain the hardcoded root; 45 FAIL-OPEN, 21 insert-but-not-rooted, 48 no insert(0,...)]
  positive controls IN the set: ['nd-unfolding/adopt_unified_5d.py', '2d-unfolding/unfold_2d_omnifold_unbinned.py']
  negative control -- rejected 21, e.g. ['./nd-unfolding/unified_throw_cov.py', './nd-unfolding/unfold_nd_omnifold_unbinned.py', './nd-unfolding/tests/test_p4_repair.py']
FAIL-OPEN SET:
    ./2d-unfolding/unfold_2d_omnifold_unbinned.py
    ./docs/orchestration/state/probe-oi120c-loader-purity-perturbation-20260814.py
    ./docs/orchestration/state/probe-oi22-leakage-real-input-20260814.py
    ./docs/orchestration/state/probe-oi22-schema-parity-real-input-20260814.py
    ./nd-unfolding/adopt_unified_4d.py
    ./nd-unfolding/adopt_unified_5d.py
    ./nd-unfolding/build_fps_prior_genie_5d.py
    ./nd-unfolding/build_fps_prior_nuwro.py
    ./nd-unfolding/build_fps_prior_nuwro_5d.py
    ./nd-unfolding/compare_ascencio_fine.py
    ./nd-unfolding/compare_ascencio_fullcov.py
    ./nd-unfolding/compare_le_evolution.py
    ./nd-unfolding/dump_td_q3.py
    ./nd-unfolding/dump_w_source_fps.py
    ./nd-unfolding/eavailW_covariance.py
    ./nd-unfolding/eavail_generator_significance.py
    ./nd-unfolding/excess_eavail_W.py
    ./nd-unfolding/fps_3prior_envelope_5d.py
    ./nd-unfolding/fps_acceptance.py
    ./nd-unfolding/fps_extension_validation.py
    ./nd-unfolding/fps_gbdt_prior_reunfold_5d.py
    ./nd-unfolding/fps_pilot_compare.py
    ./nd-unfolding/fps_prior_envelope.py
    ./nd-unfolding/make_control_plots.py
    ./nd-unfolding/nn_dump_inputs.py
    ./nd-unfolding/pet/d2_oracle.py
    ./nd-unfolding/pet/dump_pointcloud_inputs.py
    ./nd-unfolding/pet/fullevent_fps_dataloader.py
    ./nd-unfolding/pet/inversion_screen.py
    ./nd-unfolding/pet/push_vs_acceptance.py
    ./nd-unfolding/pet/train_fullevent_nominal.py
    ./nd-unfolding/pet/validate_pet_nominal_gate4.py
    ./nd-unfolding/pet_lateral_band.py
    ./nd-unfolding/pet_lateral_band_5d.py
    ./nd-unfolding/pet_lateral_correction.py
    ./nd-unfolding/pet_systematics.py
    ./nd-unfolding/pet_systematics_5d.py
    ./nd-unfolding/pet_unified_throw_5d.py
    ./nd-unfolding/plot_control_corner.py
    ./nd-unfolding/project_cov_nd.py
    ./nd-unfolding/q3_excess_projection.py
    ./nd-unfolding/q3_vs_ascencio_metrics.py
    ./nd-unfolding/rescale_flux_universes.py
    ./nd-unfolding/sweep_bank.py
    ./nd-unfolding/unified_throw.py
## P4: STEP 4 CHECKS
committed-only: 0 nonignored untracked path(s) EXCLUDED from both the table and the reference sources
OK: docs/orchestration/MANIFEST.tsv; rows=551 ARCHIVAL=107 DEAD=1 LIVE=78 MACHINE=365 overrides=101 defaults=450 tracking=tracked:551 mode=committed-only
resolved 134 bindings (848 unresolvable: data files, off-repo artifacts, binaries)
  1951 receipt hash keys are UNPAIRED across 124 receipts -- a `<role>_sha256` with no sibling path key, so they name no file, are in NEITHER cell above, and were never compared against anything
    46 of those, across 24 receipts, carry a role name that denotes repo CODE: driver_sha256, engine_net_sha256, launcher_sha256, loader_sha256, script_sha256, tool_sha256, tool_under_audit_sha256, validator_launcher_sha256, validator_sha256
    this is COVERAGE, not drift: no binding is shown broken. Resolving a role key needs a RECEIPT-SIDE declared mapping, never one inferred here (BEN-312)
  133 OK
  15 of them from EXPECTED_*_SHA guards in *.sh (22 pins seen, floor 15)
  119 of them from receipt bindings (inventory 119 tracked, sha256 09301df6f3bcc110fbe2ce347c0c1c5019416056f139f397caaefc0c8773f240)
44 canonical-namespace FIELD pins verified (floor 30) over 17 of 22 RECORD-FROZEN JSON receipts -- these pin a POINTER, not bytes; green says the receipts still point where they pointed
  1 known pre-existing drift (submit-time provenance):
      nd-unfolding/pet/sbatch_dump_g2_mefhc.sh  <- g2-dump-submit-20260719.json

24 binding(s) in 12 SELF-DECLARED fixture(s) held out of the production verdict (semantic `_fixture` marker, not a path rule)
  fixture-set integrity digest: 36355204b4b82fa4f901740b75667ee1efd0152864067196f17e23e3ed52a1e1
  these pin values the world may CONTRADICT on purpose; their integrity is the set and each file's own sha256, never a match against a live artifact

ALL BINDINGS INTACT
## P5: CONFLICT RESOLUTIONS
- mnv_guarded_run functions:
    def __init__(self, module: str, origin: str, found_root: str, expect_root: str):
def is_checkout(path: pathlib.Path) -> bool:
def checkout_root_of(path: str, _cache: dict[str, str | None] | None = None) -> str | None:
    def __init__(self, inner, expect_root: str, allowed: frozenset[str]):
    def find_spec(self, fullname, path=None, target=None):
    def invalidate_caches(self):
def install(expect_root: str, allow=()) -> GuardedPathFinder:
def loaded_checkout_roots(modules=None) -> "dict[str, list[str]]":
def _repo_env_capture(expect_root: str) -> "list[str]":
def _emit_inventory(expect_root: str, refused: "ImportTreeViolation | None" = None,
def _sha256_or_none(path: str) -> str | None:
def _verdict(outcome, origins, violation) -> str:
def write_inventory(dest, guard, script, expect_root, allow, outcome, violation=None,
def _safe_inventory(*a, **kw) -> bool:
def _report(exc: ImportTreeViolation) -> None:
def main(argv=None) -> int:
- mnv_guarded_run call to _emit_inventory:
def _emit_inventory(expect_root: str, refused: "ImportTreeViolation | None" = None,
        _emit_inventory(str(expect), violation)
- REVIEW-CONTRACT:
#### 7.0.19 THE DEPLOYMENT IS FROZEN AT `aa67c426` UNTIL F-1(b) IS FILED
1. **It does not meet Joseph's criterion.** M-1: it imports no repository module at all, before or
2. **It is the most expensive file on the path to touch.** M-3: it is the only entrypoint with a live
3. **It is a declared positive control of the OI-136 probe** (`probe-oi136-sys-path-hijack-20260820.py:52`).
1. **F-14 pre-submission also requires the repository's coupled generated artifacts to be
2. **F-15's counts are bound to the graded sha and must be re-measured, never carried forward.**
9.2 was **unsatisfiable** when ruling 20 was made. On a B-4 refusal the guard called
1. **The excluded set is enumerated and pinned, not open-ended** *(derived — from Joseph's own stated
2. **Both preflight tools remain covered by the A-2(f) source manifest and the A-3 parity set.**
3. **Both preflight tools run BEFORE any science invocation, in every launcher. A criterion, not a
9.6 is graded on 9.4's triple rather than on a string search. The second ambiguity — whether O-1's
1. **B-2, declining the source repair on `adopt_unified_5d.py`.** It rests on M-1 (no repository
2. **A-1's two-root split.** It is the largest change this contract asks for and it is my own
3. **N-2's fixture copy of the pinned writer.** Copying and editing a hash-pinned file, even as a
4. **Treating `unified_throw_cov.py` as in scope.** It is a module, not an entrypoint; it is in the
## P6: KNOWN_UNREPAIRED
BASE count: 52
MERGE count: 46
## P7: MANIFEST-overrides DEDUPE
Base rows: 98
Merge rows: 102
## P8: SUITE ARMS
Running docs/orchestration on base
RC: 1
Ran 431 tests in 40.247s
FAILED (failures=3, errors=3)
ERROR: test_loader_ordering_reco_before_truth_weight (unittest.loader._FailedTest.test_loader_ordering_reco_before_truth_weight)
ERROR: test_probe_oi120c_p4_retirement (unittest.loader._FailedTest.test_probe_oi120c_p4_retirement)
ERROR: test_probe_oi120c_verdict (unittest.loader._FailedTest.test_probe_oi120c_verdict)
FAIL: test_an_absent_token_becomes_the_literal_NOT_MEASURED (test_deploy_oi135_watcher_swap.TestReceiptWriter.test_an_absent_token_becomes_the_literal_NOT_MEASURED)
FAIL: test_only_the_five_keys_change_and_the_other_keys_are_byte_identical (test_deploy_oi135_watcher_swap.TestReceiptWriter.test_only_the_five_keys_change_and_the_other_keys_are_byte_identical)
FAIL: test_is_executable_with_a_shebang (test_deploy_oi135_watcher_swap.TestScriptHygiene.test_is_executable_with_a_shebang)
Running docs/orchestration on probe
RC: 1
Ran 431 tests in 40.396s
FAILED (failures=3, errors=3)
ERROR: test_loader_ordering_reco_before_truth_weight (unittest.loader._FailedTest.test_loader_ordering_reco_before_truth_weight)
ERROR: test_probe_oi120c_p4_retirement (unittest.loader._FailedTest.test_probe_oi120c_p4_retirement)
ERROR: test_probe_oi120c_verdict (unittest.loader._FailedTest.test_probe_oi120c_verdict)
FAIL: test_an_absent_token_becomes_the_literal_NOT_MEASURED (test_deploy_oi135_watcher_swap.TestReceiptWriter.test_an_absent_token_becomes_the_literal_NOT_MEASURED)
FAIL: test_only_the_five_keys_change_and_the_other_keys_are_byte_identical (test_deploy_oi135_watcher_swap.TestReceiptWriter.test_only_the_five_keys_change_and_the_other_keys_are_byte_identical)
FAIL: test_is_executable_with_a_shebang (test_deploy_oi135_watcher_swap.TestScriptHygiene.test_is_executable_with_a_shebang)
Running nd-unfolding/tests on base
RC: 1
Ran 1646 tests in 129.921s
FAILED (failures=8, errors=18, skipped=11)
ERROR: test_atomic_write (unittest.loader._FailedTest.test_atomic_write)
ERROR: test_cml_family_completeness_fails_closed (unittest.loader._FailedTest.test_cml_family_completeness_fails_closed)
ERROR: setUpClass (test_conftest_tmpdir_guard_live.TmpdirGuardLive)
ERROR: test_floor_replicate_launcher (unittest.loader._FailedTest.test_floor_replicate_launcher)
ERROR: test_gate5_replica_driver (unittest.loader._FailedTest.test_gate5_replica_driver)
ERROR: test_gate5_replica_extraction (unittest.loader._FailedTest.test_gate5_replica_extraction)
ERROR: test_gate6_floor_statistics (unittest.loader._FailedTest.test_gate6_floor_statistics)
ERROR: test_hash_bindings (unittest.loader._FailedTest.test_hash_bindings)
ERROR: test_legx_2x2_launcher (unittest.loader._FailedTest.test_legx_2x2_launcher)
ERROR: test_guard_is_inert_when_a_tmpdir_exists (test_p4_repair.TmpdirGuardItself.test_guard_is_inert_when_a_tmpdir_exists)
ERROR: test_probe_is_false_when_tempfile_raises (test_p4_repair.TmpdirGuardItself.test_probe_is_false_when_tempfile_raises)
ERROR: test_probe_is_true_when_a_tmpdir_works (test_p4_repair.TmpdirGuardItself.test_probe_is_true_when_a_tmpdir_works)
ERROR: test_tmpdir_dependent_tests_are_SKIPPED_not_errored (test_p4_repair.TmpdirGuardItself.test_tmpdir_dependent_tests_are_SKIPPED_not_errored)
ERROR: test_pet_diagnostic_artifact_identity_guards (unittest.loader._FailedTest.test_pet_diagnostic_artifact_identity_guards)
ERROR: test_reconcile_gate5_family (unittest.loader._FailedTest.test_reconcile_gate5_family)
ERROR: test_resume_guard (unittest.loader._FailedTest.test_resume_guard)
ERROR: test_step1_trajectory_checkpoint_tier (unittest.loader._FailedTest.test_step1_trajectory_checkpoint_tier)
ERROR: test_verify_executing_copy_is_committed (unittest.loader._FailedTest.test_verify_executing_copy_is_committed)
FAIL: test_module_is_importable_outside_the_cluster (test_cstat_100rep_gates.CovarianceGatesAreScaleAware.test_module_is_importable_outside_the_cluster)
FAIL: test_every_test_module_has_its_main_guard_last (test_cstat_data_only_predicates.MainGuardPosition.test_every_test_module_has_its_main_guard_last)
FAIL: test_guards_are_not_pytest_collectable_on_their_own (test_g2_guards_collected.G2GuardsRun.test_guards_are_not_pytest_collectable_on_their_own)
FAIL: test_launcher_emits_exactly_the_six_producing_paths (test_p4_resume_integration.PB2ProducingClosureResume.test_launcher_emits_exactly_the_six_producing_paths)
FAIL: test_no_LIVE_pipeline_instances (test_p4_sweep_snapshots.SweepSnapshots.test_no_LIVE_pipeline_instances)
FAIL: test_pipeline_sweep_matches_its_snapshot (test_p4_sweep_snapshots.SweepSnapshots.test_pipeline_sweep_matches_its_snapshot)
FAIL: test_MUTATION_prefix_surface_OMITS_the_shell_invoked_scripts (test_p4_token_gate_scope_and_rev.Defect4b_ShellInvokedScriptsAreOnTheSurface.test_MUTATION_prefix_surface_OMITS_the_shell_invoked_scripts)
FAIL: test_the_hook_git_would_run_EXISTS_and_is_executable (test_precommit_hook_is_wired.PreCommitHookIsWired.test_the_hook_git_would_run_EXISTS_and_is_executable)
Running nd-unfolding/tests on merge
RC: 1
Ran 1813 tests in 559.429s
FAILED (failures=12, errors=18, skipped=11)
ERROR: test_atomic_write (unittest.loader._FailedTest.test_atomic_write)
ERROR: test_cml_family_completeness_fails_closed (unittest.loader._FailedTest.test_cml_family_completeness_fails_closed)
ERROR: setUpClass (test_conftest_tmpdir_guard_live.TmpdirGuardLive)
ERROR: test_floor_replicate_launcher (unittest.loader._FailedTest.test_floor_replicate_launcher)
ERROR: test_gate5_replica_driver (unittest.loader._FailedTest.test_gate5_replica_driver)
ERROR: test_gate5_replica_extraction (unittest.loader._FailedTest.test_gate5_replica_extraction)
ERROR: test_gate6_floor_statistics (unittest.loader._FailedTest.test_gate6_floor_statistics)
ERROR: test_hash_bindings (unittest.loader._FailedTest.test_hash_bindings)
ERROR: test_legx_2x2_launcher (unittest.loader._FailedTest.test_legx_2x2_launcher)
ERROR: test_guard_is_inert_when_a_tmpdir_exists (test_p4_repair.TmpdirGuardItself.test_guard_is_inert_when_a_tmpdir_exists)
ERROR: test_probe_is_false_when_tempfile_raises (test_p4_repair.TmpdirGuardItself.test_probe_is_false_when_tempfile_raises)
ERROR: test_probe_is_true_when_a_tmpdir_works (test_p4_repair.TmpdirGuardItself.test_probe_is_true_when_a_tmpdir_works)
ERROR: test_tmpdir_dependent_tests_are_SKIPPED_not_errored (test_p4_repair.TmpdirGuardItself.test_tmpdir_dependent_tests_are_SKIPPED_not_errored)
ERROR: test_pet_diagnostic_artifact_identity_guards (unittest.loader._FailedTest.test_pet_diagnostic_artifact_identity_guards)
ERROR: test_reconcile_gate5_family (unittest.loader._FailedTest.test_reconcile_gate5_family)
ERROR: test_resume_guard (unittest.loader._FailedTest.test_resume_guard)
ERROR: test_step1_trajectory_checkpoint_tier (unittest.loader._FailedTest.test_step1_trajectory_checkpoint_tier)
ERROR: test_verify_executing_copy_is_committed (unittest.loader._FailedTest.test_verify_executing_copy_is_committed)
FAIL: test_module_is_importable_outside_the_cluster (test_cstat_100rep_gates.CovarianceGatesAreScaleAware.test_module_is_importable_outside_the_cluster)
FAIL: test_every_test_module_has_its_main_guard_last (test_cstat_data_only_predicates.MainGuardPosition.test_every_test_module_has_its_main_guard_last)
FAIL: test_guards_are_not_pytest_collectable_on_their_own (test_g2_guards_collected.G2GuardsRun.test_guards_are_not_pytest_collectable_on_their_own)
FAIL: test_the_fail_open_set_is_EXACTLY_the_recorded_one (test_oi136_failopen_inventory_ratchet.TheInventoryIsARatchet.test_the_fail_open_set_is_EXACTLY_the_recorded_one)
FAIL: test_this_ratchet_cannot_pass_over_an_empty_set (test_oi136_failopen_inventory_ratchet.TheInventoryIsARatchet.test_this_ratchet_cannot_pass_over_an_empty_set)
FAIL: test_it_exits_0_which_means_BOTH_its_controls_held (test_oi136_failopen_inventory_ratchet.TheProbeStillMeasures.test_it_exits_0_which_means_BOTH_its_controls_held)
FAIL: test_its_negative_control_still_rejects_something (test_oi136_failopen_inventory_ratchet.TheProbeStillMeasures.test_its_negative_control_still_rejects_something)
FAIL: test_launcher_emits_exactly_the_six_producing_paths (test_p4_resume_integration.PB2ProducingClosureResume.test_launcher_emits_exactly_the_six_producing_paths)
FAIL: test_no_LIVE_pipeline_instances (test_p4_sweep_snapshots.SweepSnapshots.test_no_LIVE_pipeline_instances)
FAIL: test_pipeline_sweep_matches_its_snapshot (test_p4_sweep_snapshots.SweepSnapshots.test_pipeline_sweep_matches_its_snapshot)
FAIL: test_MUTATION_prefix_surface_OMITS_the_shell_invoked_scripts (test_p4_token_gate_scope_and_rev.Defect4b_ShellInvokedScriptsAreOnTheSurface.test_MUTATION_prefix_surface_OMITS_the_shell_invoked_scripts)
FAIL: test_the_hook_git_would_run_EXISTS_and_is_executable (test_precommit_hook_is_wired.PreCommitHookIsWired.test_the_hook_git_would_run_EXISTS_and_is_executable)
Running nd-unfolding/tests on pin
RC: 1
Ran 1813 tests in 540.864s
FAILED (failures=12, errors=18, skipped=11)
ERROR: test_atomic_write (unittest.loader._FailedTest.test_atomic_write)
ERROR: test_cml_family_completeness_fails_closed (unittest.loader._FailedTest.test_cml_family_completeness_fails_closed)
ERROR: setUpClass (test_conftest_tmpdir_guard_live.TmpdirGuardLive)
ERROR: test_floor_replicate_launcher (unittest.loader._FailedTest.test_floor_replicate_launcher)
ERROR: test_gate5_replica_driver (unittest.loader._FailedTest.test_gate5_replica_driver)
ERROR: test_gate5_replica_extraction (unittest.loader._FailedTest.test_gate5_replica_extraction)
ERROR: test_gate6_floor_statistics (unittest.loader._FailedTest.test_gate6_floor_statistics)
ERROR: test_hash_bindings (unittest.loader._FailedTest.test_hash_bindings)
ERROR: test_legx_2x2_launcher (unittest.loader._FailedTest.test_legx_2x2_launcher)
ERROR: test_guard_is_inert_when_a_tmpdir_exists (test_p4_repair.TmpdirGuardItself.test_guard_is_inert_when_a_tmpdir_exists)
ERROR: test_probe_is_false_when_tempfile_raises (test_p4_repair.TmpdirGuardItself.test_probe_is_false_when_tempfile_raises)
ERROR: test_probe_is_true_when_a_tmpdir_works (test_p4_repair.TmpdirGuardItself.test_probe_is_true_when_a_tmpdir_works)
ERROR: test_tmpdir_dependent_tests_are_SKIPPED_not_errored (test_p4_repair.TmpdirGuardItself.test_tmpdir_dependent_tests_are_SKIPPED_not_errored)
ERROR: test_pet_diagnostic_artifact_identity_guards (unittest.loader._FailedTest.test_pet_diagnostic_artifact_identity_guards)
ERROR: test_reconcile_gate5_family (unittest.loader._FailedTest.test_reconcile_gate5_family)
ERROR: test_resume_guard (unittest.loader._FailedTest.test_resume_guard)
ERROR: test_step1_trajectory_checkpoint_tier (unittest.loader._FailedTest.test_step1_trajectory_checkpoint_tier)
ERROR: test_verify_executing_copy_is_committed (unittest.loader._FailedTest.test_verify_executing_copy_is_committed)
FAIL: test_module_is_importable_outside_the_cluster (test_cstat_100rep_gates.CovarianceGatesAreScaleAware.test_module_is_importable_outside_the_cluster)
FAIL: test_every_test_module_has_its_main_guard_last (test_cstat_data_only_predicates.MainGuardPosition.test_every_test_module_has_its_main_guard_last)
FAIL: test_guards_are_not_pytest_collectable_on_their_own (test_g2_guards_collected.G2GuardsRun.test_guards_are_not_pytest_collectable_on_their_own)
FAIL: test_the_fail_open_set_is_EXACTLY_the_recorded_one (test_oi136_failopen_inventory_ratchet.TheInventoryIsARatchet.test_the_fail_open_set_is_EXACTLY_the_recorded_one)
FAIL: test_this_ratchet_cannot_pass_over_an_empty_set (test_oi136_failopen_inventory_ratchet.TheInventoryIsARatchet.test_this_ratchet_cannot_pass_over_an_empty_set)
FAIL: test_it_exits_0_which_means_BOTH_its_controls_held (test_oi136_failopen_inventory_ratchet.TheProbeStillMeasures.test_it_exits_0_which_means_BOTH_its_controls_held)
FAIL: test_its_negative_control_still_rejects_something (test_oi136_failopen_inventory_ratchet.TheProbeStillMeasures.test_its_negative_control_still_rejects_something)
FAIL: test_launcher_emits_exactly_the_six_producing_paths (test_p4_resume_integration.PB2ProducingClosureResume.test_launcher_emits_exactly_the_six_producing_paths)
FAIL: test_no_LIVE_pipeline_instances (test_p4_sweep_snapshots.SweepSnapshots.test_no_LIVE_pipeline_instances)
FAIL: test_pipeline_sweep_matches_its_snapshot (test_p4_sweep_snapshots.SweepSnapshots.test_pipeline_sweep_matches_its_snapshot)
FAIL: test_MUTATION_prefix_surface_OMITS_the_shell_invoked_scripts (test_p4_token_gate_scope_and_rev.Defect4b_ShellInvokedScriptsAreOnTheSurface.test_MUTATION_prefix_surface_OMITS_the_shell_invoked_scripts)
FAIL: test_the_hook_git_would_run_EXISTS_and_is_executable (test_precommit_hook_is_wired.PreCommitHookIsWired.test_the_hook_git_would_run_EXISTS_and_is_executable)
Running nd-unfolding/tests on probe
RC: 1
Ran 1813 tests in 587.362s
FAILED (failures=8, errors=18, skipped=11)
ERROR: test_atomic_write (unittest.loader._FailedTest.test_atomic_write)
ERROR: test_cml_family_completeness_fails_closed (unittest.loader._FailedTest.test_cml_family_completeness_fails_closed)
ERROR: setUpClass (test_conftest_tmpdir_guard_live.TmpdirGuardLive)
ERROR: test_floor_replicate_launcher (unittest.loader._FailedTest.test_floor_replicate_launcher)
ERROR: test_gate5_replica_driver (unittest.loader._FailedTest.test_gate5_replica_driver)
ERROR: test_gate5_replica_extraction (unittest.loader._FailedTest.test_gate5_replica_extraction)
ERROR: test_gate6_floor_statistics (unittest.loader._FailedTest.test_gate6_floor_statistics)
ERROR: test_hash_bindings (unittest.loader._FailedTest.test_hash_bindings)
ERROR: test_legx_2x2_launcher (unittest.loader._FailedTest.test_legx_2x2_launcher)
ERROR: test_guard_is_inert_when_a_tmpdir_exists (test_p4_repair.TmpdirGuardItself.test_guard_is_inert_when_a_tmpdir_exists)
ERROR: test_probe_is_false_when_tempfile_raises (test_p4_repair.TmpdirGuardItself.test_probe_is_false_when_tempfile_raises)
ERROR: test_probe_is_true_when_a_tmpdir_works (test_p4_repair.TmpdirGuardItself.test_probe_is_true_when_a_tmpdir_works)
ERROR: test_tmpdir_dependent_tests_are_SKIPPED_not_errored (test_p4_repair.TmpdirGuardItself.test_tmpdir_dependent_tests_are_SKIPPED_not_errored)
ERROR: test_pet_diagnostic_artifact_identity_guards (unittest.loader._FailedTest.test_pet_diagnostic_artifact_identity_guards)
ERROR: test_reconcile_gate5_family (unittest.loader._FailedTest.test_reconcile_gate5_family)
ERROR: test_resume_guard (unittest.loader._FailedTest.test_resume_guard)
ERROR: test_step1_trajectory_checkpoint_tier (unittest.loader._FailedTest.test_step1_trajectory_checkpoint_tier)
ERROR: test_verify_executing_copy_is_committed (unittest.loader._FailedTest.test_verify_executing_copy_is_committed)
FAIL: test_module_is_importable_outside_the_cluster (test_cstat_100rep_gates.CovarianceGatesAreScaleAware.test_module_is_importable_outside_the_cluster)
FAIL: test_every_test_module_has_its_main_guard_last (test_cstat_data_only_predicates.MainGuardPosition.test_every_test_module_has_its_main_guard_last)
FAIL: test_guards_are_not_pytest_collectable_on_their_own (test_g2_guards_collected.G2GuardsRun.test_guards_are_not_pytest_collectable_on_their_own)
FAIL: test_launcher_emits_exactly_the_six_producing_paths (test_p4_resume_integration.PB2ProducingClosureResume.test_launcher_emits_exactly_the_six_producing_paths)
FAIL: test_no_LIVE_pipeline_instances (test_p4_sweep_snapshots.SweepSnapshots.test_no_LIVE_pipeline_instances)
FAIL: test_pipeline_sweep_matches_its_snapshot (test_p4_sweep_snapshots.SweepSnapshots.test_pipeline_sweep_matches_its_snapshot)
FAIL: test_MUTATION_prefix_surface_OMITS_the_shell_invoked_scripts (test_p4_token_gate_scope_and_rev.Defect4b_ShellInvokedScriptsAreOnTheSurface.test_MUTATION_prefix_surface_OMITS_the_shell_invoked_scripts)
FAIL: test_the_hook_git_would_run_EXISTS_and_is_executable (test_precommit_hook_is_wired.PreCommitHookIsWired.test_the_hook_git_would_run_EXISTS_and_is_executable)
## P9: FOUR ADJACENT FILES
File: ./nd-unfolding/unified_throw_cov_5d.py
Base: a36a4ecda3aa7ae30114ec31f2c37e14776b121e4a08aa0e38f29d9d647eb39a  ./nd-unfolding/unified_throw_cov_5d.py
Probe: af6b5f71e757bcb8d02974710414b27b118034fb118b76f63a675545cd14a1c7  ./nd-unfolding/unified_throw_cov_5d.py
File: ./nd-unfolding/unified_throw_cov.py
Base: 8431e3b8e34494abad74d13cef8a63d96e608dcd991910322f896d8f15adbe5a  ./nd-unfolding/unified_throw_cov.py
Probe: d4b1934407f1c32913867f411bf718b7556834333159a350e8989080d9711c73  ./nd-unfolding/unified_throw_cov.py
File: ./nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh
Base: f7ce66451109271e47ee32b3b11abe9dbd438f75fa39616bfaff2fb12c9236f0  ./nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh
Probe: 8c4a931d2cb53d28b8c0e69ad6bddd0d65d03f763aab1c7c07f48a9763a2808d  ./nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh
File: ./nd-unfolding/mii_adopt_unified_5d_stamped.py
Base: fc520bfd09a564f35660eb0bd3210be8d2836f9c65aa4672aa65b68b877827be  ./nd-unfolding/mii_adopt_unified_5d_stamped.py
Probe: e5bc51a4d482fcd236509745f97d78b4a3cba3499a9cc24a26f1b54473d9cea8  ./nd-unfolding/mii_adopt_unified_5d_stamped.py
## FIT VERDICT
