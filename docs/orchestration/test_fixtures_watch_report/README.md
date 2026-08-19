# test_fixtures_watch_report

Real producer-emitted log excerpts for `test_watch_report_train_run.py`. See `PROVENANCE.tsv` for each
fixture's source path, the source file's full sha256, and exactly how it was excerpted.

Three real runs are represented. **None of the five documented failure signatures was written until
after these runs failed**, so which signature (if any) each run matches is a MEASUREMENT, recorded in
the tests, not an assumption:

| run | what happened | measured verdict |
|---|---|---|
| `57235710` (task 0) | killed at the target stage in ~10 s by a `set -u` added to a conda activate shim | **UNKNOWN** — matches none of the five |
| `57253127_0` | ~131 s, off-by-one in the F2 family-root derivation | **FAIL-2** |
| `57256638_0` | 02:58:44 — trained fully, six fits, LR anneal verified, both finals round-trip verified, then died at the receipt write | **FAIL-3** |

`57235710` is the load-bearing fixture for the UNKNOWN branch precisely because it is a real
producer-emitted outcome that the closed set does not cover. It is also the only fixture kept as a
COMPLETE byte-identical pair, and its stdout is EMPTY (0 bytes) — an empty-but-readable stream, which
is why it classifies UNKNOWN and not NO-LOGS.

Note `57235710`'s logs are named `target_*`, not `train_*`, and live in a different tree: it is a
TARGET-stage job. Tests point `--log-prefix target` at it.

## Why the `.txt` suffix

`.gitignore:13-14` exclude `*.out` and `*.err` repo-wide, which is the right policy for job logs. Rather
than override it with `git add -f` or edit a file outside this work's scope, each fixture is stored with a
trailing `.txt`; the tests copy it to the producer's real `train_<job>_<task>.{out,err}` name in a temp
directory. The stored bytes are the excerpt bytes, unchanged by the rename.
