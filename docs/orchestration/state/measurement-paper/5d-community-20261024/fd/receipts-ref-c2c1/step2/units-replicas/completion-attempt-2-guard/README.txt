REF-C2C1 step two, the replicas' completion, attempt 2: the concurrency-guard fix (the director's ruling of 2026-11-06 on
attempt 1, job 60897523, INVALID from a connect-level guard defect; receipt ../completion-attempt-1/). Built by
limitation-resolver for coverage-5b-audit's delta audit. Nothing here has run as a job.

THE CHANGE (diff-job-vs-attempt1.txt, diff-submit-vs-attempt1.txt):
- refc2c1_completion_job.sbatch: sha256 c82055f6f8dea72a2e16fb4722d1613610576e929209b4a7c5eea0123b24589f, replacing bee44fae.
  At +90 s the job writes `scontrol -o show step $SLURM_JOB_ID` to logs-completion/j4-steps-at-90s.txt. It counts, with
  running_lane_steps (the block between the ">>> lane-step guard" markers), the steps <job>.0..NL-1 that read
  State=RUNNING; each is counted once, and batch, extern and other indices are ignored. It prints each step's
  StepId/State/Name and records `sstat -a`'s count of numbered steps as a cross-check only. Below NL it records a STOP,
  kills the srun clients and writes concurrent=0, as before. Nothing else in the job changed: the unit call, --mem=112G, the
  fit check, the watch, the record.
- refc2c1_completion_submit.sh: sha256 c41ffb614a72864dff4d9fd0e44cb4ac54d07bf256fa3d6ab4f27321d229d503, replacing cf4eac53.
  Its only changes are JOB_SHA and the embedded job: paths, the gate, the fit check, --time=01:30:00, the price and
  lanes-j4.tsv (b6d66658, copied here) are byte-identical.

THE TESTS (test_lane_step_guard.sh, sha256 ae81a5b3...). The test evals the guard block straight out of the job script, so
it tests the shipped bytes.
- Fixtures (fixtures/): real `scontrol -o show step` output from two of the lane's running jobs, each captured beside its
  sacct at 2026-11-06T12:27Z. 60895985 has .8-.11 RUNNING; 60895983 has .3-.4 RUNNING and .0-.2 COMPLETED, which
  scontrol omits.
- 11 fixture cases. Silent when the expected count equals the running count (4 of 4; 2 of 2; a duplicated listing counts
  once). Fires when the expected count is one more, when the job has only batch/extern, on lanes 0-3 of a job running
  .8-.11, when index 1 is asked of .10/.11, on a job-id prefix, on State=COMPLETING, and on empty output. They pass under
  BSD awk (macOS) and GNU Awk 4.2.1 (Perlmutter).
- 12 live cases (live-test.out, login09, 12:28:15Z, read-only scontrol/sacct on four running cov2d-* jobs, no input
  touched). Silent on each job's sacct-RUNNING steps; fires with one index more, and on the job's COMPLETED steps.
  23 passed, 0 failed.
- Four mutants of the guard are each killed (mutants.out): no State test, no once-only, a constant count, a prefix match.
- The job's exact +90 s lines, run on live job 60895578 (live-exact-lines.out): indices 0-3 (not its running steps) gave 0 of 4, WOULD-FIRE;
  its running indices 14 15 gave 2 of 2, SILENT; sstat -a listed 2 numbered steps.

NOT TESTED: the guard inside a real job of this lane's, which takes a submission.
