# COV2D-G2R addendum J1: test, mutation and coverage receipts (2026-11-12)

**From** a clean detached checkout of the code commit `a14a08e50d5148b8b7b8a3b64718d1f15482ff6c`, with porcelain 0 before and
after each run. The platform was macOS, with `/opt/homebrew/bin/python3.13`, ROOT 6.36.000 and numpy 2.4.4. There is no
LightGBM here, so no test trains. The trained checks are the environment-test job and D_Ua's first run (J1 §2, §4).

| file | what |
|---|---|
| `test_g2r_jobs.txt` | `test_g2r_jobs.py` at PYTHONHASHSEED 0, 1 and 2: 51 tests, OK, rc 0 each time |
| `g2r_jobs_mutation.txt` | `g2r_jobs_mutation.py`: the unmutated suite full (51, none skipped); 30 mutations, all killed; sources restored byte-identical to HEAD; rc 0 |
| `amendment1_suites.txt` | amendment 1's suites at this commit: `test_g2r` 27, `test_re2_miss_map` 11 and `test_g2r_glue` 18, OK each; `g2r_mutation.py` 23 of 23 killed, rc 0 |
| `coverage_sweep.txt` | every executable line of `g2r_jobs.py` is run by `test_g2r_jobs.py`: 0 of 350 never executed |
| `coverage_tracer_usercustomize.py`, `coverage_uncovered_j1.py` | the sweep's tracer and reader (see below) |

**The tracer** is amendment 1's (`../a1/coverage_tracer_usercustomize.py`), changed in two ways:
- it matches files by their repository-relative path;
- it records each traced file's sha256 at exit.

The reader then counts the hits of a copy only if that sha256 equals the worktree file's. This is what lets the tests'
fixture deploy count: the submit tests run a byte-identical copy of `g2r_jobs.py` in a temporary git repository that
is deleted at the end. The sweep found 2 such copies.

## The shell scripts' paths, each run by a named test against stubs

The stubs stand in for sbatch, sacct, scontrol, srun, omnifold_py310, the MAT setup and a fixture deploy whose
origin/main carries the binding and the records. `g2r_env.sh`'s two test hooks, `G2R_O` and `G2R_TEST_STUB`, are
refused on any NERSC machine (`test_the_hooks_are_refused_on_a_nersc_machine`).

| script | path | test (`Shell.`…) |
|---|---|---|
| `g2r_env.sh` | the hooks refused where `NERSC_HOST` is set; the cluster's paths without hooks; each point's data directory; an unknown point | `test_the_hooks_are_refused_on_a_nersc_machine`, `test_without_hooks_the_paths_are_the_clusters` |
| `g2r_env.sh` `g2r_preflight` | C or M unset (2); the MAT setup not pinned (7); not the pinned MAT environment (7); QOS (2); TimeLimit (2) | `test_the_preflight_refusals`, `test_a_real_run_stops_on_a_failed_check_and_the_wrong_limit` |
| `g2r_job.sbatch` | the envtest and prepare refused; no runs or mixed points; DRYRUN; a real run (sums, walls); a product never overwritten (1); a failed check (4); a failed run recorded while the lane goes on (1); a dirty deploy (2) | `test_the_job_script_refuses_the_envtest_and_prepare_and_mixed_points`, `test_dry_run_of_d_ud_prints_its_45_runs_with_the_off_reruns_unpatched`, `test_dry_run_of_a_tune_job_reads_its_realization`, `test_a_real_run_of_g18_ud_against_stubs`, `test_a_real_run_stops_on_a_failed_check_and_the_wrong_limit`, `test_a_failed_run_is_recorded_and_the_lane_goes_on`, `test_a_dirty_deploy_is_refused` |
| `g2r_envtest.sbatch` | PASS, and a rerun refused (3); a difference (5); a failed run (6, no comparison); the pre deploy not at PRE_M (2); the limit (2); a failed check (4) | `test_the_envtest_passes_and_refuses_a_rerun`, `test_the_envtest_finds_a_difference_and_a_failed_run`, `test_the_envtest_refuses_a_pre_deploy_not_at_pre_m`, `test_the_envtest_stops_on_its_limit_and_its_check` |
| `g2r_prepare.sbatch` | rc 0, 5, 7 and 8 passed through, with 12 blocks given; `$UNI`'s stat (4); the limit (2); an existing prepare (3); a dirty deploy (2) | `test_the_prepare_passes_its_rc_through`, `test_the_prepare_refuses`, `test_the_prepare_refuses_a_dirty_deploy` |
| `g2r_submit.sh` | the sequence envtest → prepare → D_Ua → D_Ub, with each refusal between (3), the map's sha256 from the committed record and the STOP (9); one job per call (2); M not on the M_J1 line (2); the binding missing (2); an unknown job (2); a changed table (2); a dirty deploy (2); a failed fetch (2); the gate refusing an envtest (3); sbatch returning no id (2); sacct never listing the id (6) | `test_the_submission_sequence`, `test_the_submit_refusals`, `test_the_binding_must_name_m_on_its_m_j1_line`, `test_a_missing_binding_is_refused`, `test_more_submit_refusals`, `test_sacct_never_listing_the_id_is_rc_6` |

**Not run by any test:**
- `g2r_job.sbatch`'s `no runs for $JOB`, which is unreachable after the point check;
- `g2r_submit.sh`'s refusal when `map-sha` finds no committed map, which is unreachable once the order has passed,
  because the order requires the same record.

**MEASURES:** the tests, mutants and coverage on synthetic fixtures and stubs. **CANNOT AUTHORIZE:** any job.
