grader role       : agy-g2-gate-verifier
conversation uuid : dc93a0f8-6863-48c8-9b7b-76f22f6deae2
export PATH=/global/u2/j/josephrb/.conda/envs/root_6_28/bin:$PATH
export TMPDIR=/tmp/grade-stack-20260826/tmp
command -v python3: /global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3
Python 3.11.14

--- WORKTREE CHECK ---
HEAD: d0decbd35b0c4986dc31286a221220d3a29555d1
Detached state: detached
Porcelain count: 2

--- RUNNING PROBE TESTS ---
Probe rc: 1
Ran 1813 tests in 603.258s
FAILED (failures=8, errors=18, skipped=11)
Probe Failures and Errors:
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

--- COMPARISON AGAINST BASE ---
BASE minus PROBE (resolved in probe):

PROBE minus BASE (regressions in probe):

--- EXPECTATION CHECK ---
The expectation is that the 4 OI-136 arms (which failed in merge and pin, bringing failures from 8 to 12) are green in probe, meaning probe should have the EXACT SAME 8 failures and 18 errors as base.

Classification of test_g2_guards_collected:
test_g2_guards_collected.G2GuardsRun.test_guards_are_not_pytest_collectable_on_their_own fails at base too because root_6_28 has no pytest. It is pre-existing and is NOT a regression.

--- REACHABILITY ---
COMPLETED: identity, environment export/verification, HEAD check, probe test execution, base comparison, expectation check, classification of test_g2_guards_collected. UNREACHED: none.
