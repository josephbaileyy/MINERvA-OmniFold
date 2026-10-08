# ISSUE-87 — `mnv_guarded_run.py` leaves a per-process tool directory behind whenever the guarded process is replaced by `exec`

**Severity:** LOW. **Status:** OPEN (2026-10-07). **Index row:** `KNOWN_ISSUES.md` row 87. **Updated:** 2026-10-07.

## What happens

When the guard is installed, `nd-unfolding/mnv_guarded_run.py` creates two per-process directories in `TMPDIR`:

- `_generated_wrapper_dir` creates `mnv-guard-bin-<pid>-*` (`:1053`);
- `_generated_forwarder_dir` creates `mnv-guard-tools-<pid>-*` (`:1147`), about 40 one-line forwarders to
  resolved system tools.

It puts both on the restricted `PATH`, and removes each with `atexit.register(shutil.rmtree, directory, True)`
(`:1069`, `:1166`). That removal is best-effort by design, and the code says why (`:1066-1068`, `:1165`): an
`os.exec*` replacement never runs `atexit`, and *"a child outliving its parent must not lose its interpreter"*
or `ls`.

Measured at `9cf09152`: one run of `nd-unfolding/tests/test_mnv_guarded_run.py` under an empty `TMPDIR` left 19
`mnv-guard-tools-*` directories, 3,040 KiB in total. No `mnv-guard-bin-*` directory was left. Production runs
were not measured. The directory goes wherever `TMPDIR` points: the guard receipt
`nd-unfolding/pet/configuration_comparison/receipts/20260918-calibration/guard.json` records a Perlmutter run's
tool directory as `/tmp/mnv-guard-tools-1243405-ys1c2zkj`.

## Why this is separate from the test leaks

The directory is not test-owned scratch. Processes started under the guard reach their tools through it, and
some of them can outlive the Python process that created it. Removing it when that process ends, which is the
pattern PR #48 used for test directories, can break a live child. That is the failure the current code avoids
on purpose. Any fix must tie removal to the lifetime of the last process that inherited the `PATH`, not to the
creating process.

## Bounded remedy, in order of preference

1. **Tests only, no production change.** `test_mnv_guarded_run.py` runs each guarded child with `TMPDIR` set to
   a directory the test owns, created per test and removed by `addCleanup`. Cleanups run after the test body,
   so this is safe for every test whose body waits for, or kills, the children it starts; check that per test
   before relying on it. Leftover tool directories then land inside, and go with, the test's own directory.
2. **Production.** Place the directories under a location whose lifetime is the whole job: a per-job
   directory that the launcher, or the scheduler's job-end cleanup, removes after every process in the job has
   exited. Do not delete earlier in-process.

   `mnv_guarded_run.py` is sha256-pinned in 7 tracked files at `a8a8e1da` (receipts and manifests under
   `docs/orchestration/state/` and `nd-unfolding/pet/direct_token_comparison/`). A production change therefore
   needs those pins re-issued through their owning gates, with a record, and never by editing a hash.

## Done when

- Remedy 1: one run of `test_mnv_guarded_run.py` leaves 0 entries in the caller's `TMPDIR`. Its outcome is
  unchanged: 271 passed, 1 skipped, and the 2 failures that predate this issue (both
  `test_every_multiprocessing_START_METHOD_and_the_POOL_still_run_a_GUARDED_child`, in
  `TheKernelFloorIsHookedAndTheResidualIsBelowIt` and `TheApprovalIsBoundToTheFileAndNotOnlyToTheArgv`).
- Remedy 2, if pursued: a control in which a child outlives its parent still runs a forwarded tool, and the
  directory is gone after the job ends.

**Out of scope:** removing the directories from inside the guarded process at any time before its children
have exited.

Measurement logs: the `tmpdir-leaks-20261007` evidence epoch, `validation-logs/before/`. See
`docs/LOCAL_CHECKOUTS_AND_STORAGE.md`.
