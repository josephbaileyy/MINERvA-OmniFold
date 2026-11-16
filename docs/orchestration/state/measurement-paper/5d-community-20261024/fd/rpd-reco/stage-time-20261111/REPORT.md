# RPD-RECO: the staging time in the prepare receipt (2026-11-11)

**Director-authorized** (2026-11-11). This is cov2d's condition, made binding by the director, for the flux connect's
one protected-path exception. Authored by the limitation-resolver lane. The branch is based on #848's head `a4c3e556`
and is proposed as a PR into #848's branch, so #848's authorship stays Codex2's. Nothing runs.
<!-- absence-ok: the document's own status, not a claim that a result does not exist -->

## The change

cov2d's condition: the prepare receipt carries the exception file's `stat_before` and `stat_after` (device, inode,
bytes, mtime_ns, atime_ns), plus the UTC time of the staging.

- `stat_before` and `stat_after` were already there: custody `prepare`'s `copy()` records both from `source_stat`
  (`fd_rpd_reco_custody.py:379-388`), and STAGE_SOURCE_STAT compares them.
- The staging time was not there. `copy()` now records `staging_utc_ns`, with `started` and `ended`: `time.time_ns()`
  taken just before `stat_before` and just after `stat_after`. That is the UTC wall time around the one stat-bracketed
  staging, with two O_NOATIME reads (`noatime_digest`, then `stage_copy`).
- The field reaches every staged item in `files`, and through `{**item, **staged}` every `mat_dependencies` entry. The
  MPARAMFILES constraint file is one of those entries.

Four lines in `fd_rpd_reco_custody.py`. No guard changes, and no other file of the producer changes.

## The test

`test_prepare_records_stat_bracket_and_staging_time` runs `prepare` on the existing fixture. It requires, for every item
in `files` and every `mat_dependencies` entry:
- both stats, with exactly the five fields, all integers;
- the two stats equal;
- `staging_utc_ns` with integer `started` ≤ `ended` ≤ `prepare_time_ns`.

It also requires that the MPARAMFILES entry is the constraint file, and that its window equals its `files` item's.

**A hand mutation shows the test bites.** Deleting the `staging_utc_ns` line from `copy()` fails this test, with a `KeyError` at the
field's access (recorded in `HAND-MUTATION.txt`). The harness generates mutants from guards and named expressions. This change adds neither, so its
mutant set is unchanged, and it is rerun to show every prior mutant is still killed.
<!-- absence-ok: the harness's mutant population (guards and named clauses), not a claim about a result -->

| run | result | file |
|---|---|---|
| the suite on this branch | **300 passed** (299 at `a4c3e556`, + 1) | `SUITE.txt` |
| the harness on this branch | **236 required, 236 executed, 236 killed; complete and all_killed true** | `MUTATIONS.txt`, `MUTATIONS.json` |
| black / ruff | clean on the two changed files | `STATIC-CHECKS.txt` |

`MUTATIONS.json` is the harness's raw report (sha256 `1e6818a5…`, recorded in its `receipt_annotation`) with #1069's two
annotations added, `receipt_annotation` and `disposable_fixture_artifact_paths`. All runs were serial, with the five thread caps at 1. `SOURCE-SHA256SUMS` holds the four files' sha256. They were equal
before and after the runs.

Nothing is submitted, deposited or tagged.
