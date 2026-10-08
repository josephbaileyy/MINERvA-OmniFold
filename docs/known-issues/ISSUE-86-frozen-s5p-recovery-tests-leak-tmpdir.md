# ISSUE-86 — The two frozen s5p recovery test files leave their temp directories behind

**Severity:** LOW. **Status:** OPEN (2026-10-07). **Index row:** `KNOWN_ISSUES.md` row 86. **Updated:** 2026-10-07.

## What happens

`docs/orchestration/state/s5p/recovery/test_s5p_recovery.py` (classes `Tables`, `Determinism`, `Resolve`) and
`test_s5p_recovery_world.py` (the `World` helper's `__init__`) create directories with `tempfile.mkdtemp()` and
never remove them. Measured at `9cf09152` with each file run alone under an empty `TMPDIR`: 28 and 13
directories, 668 KiB and 4,176 KiB, so 41 directories and 4.7 MiB per run of both. Both files are unchanged at
`a8a8e1da`, where PR #48 fixed the same leak in 16 other test files.

## Why it was not fixed in place

`docs/orchestration/MANIFEST.tsv` classifies both files `MACHINE`, `generated`, `immutable: yes`: they are the
41 controls of the closed s5p lost-seed recovery procedure (`PROCEDURE-20261005-s5p-lost-seed-recovery.md`).
Their bytes must stay frozen:

    74770b391f229ac317861714cc600fa0990264dff11b790fcc2eb367f291a946  test_s5p_recovery.py
    5702c8c640e7e8c7c2bc5dd08e4d985352fba1abfda984e1a292c6b89579902c  test_s5p_recovery_world.py

## Bounded remedy

Contain the leak around execution and leave the files alone. Whatever runs these two files does this:

1. creates a dedicated, empty, disposable directory and exports it as `TMPDIR` for that run only;
2. runs pytest on the two files;
3. after the pytest process has exited, removes that directory and nothing else. The caller's own `TMPDIR`,
   other scratch and evidence archives are not touched.

The removal happens only after the test process exits, so no test can lose a file it still uses.

## Done when

- a committed invocation (a runner script or a documented command at the procedure's test route) does steps
  1 to 3;
- running it leaves 0 entries in the caller's `TMPDIR`;
- the two sha256 values above are unchanged;
- the outcome is still 41 passed (28 + 13 at `9cf09152`).

**Out of scope:** editing either file, and changing the `immutable` classification. Lifting the classification
would let the two-line `addCleanup` fix used in PR #48 apply instead, and that is a separate decision.

Measurement logs: the `tmpdir-leaks-20261007` evidence epoch, `validation-logs/before/`. See
`docs/LOCAL_CHECKOUTS_AND_STORAGE.md`.
