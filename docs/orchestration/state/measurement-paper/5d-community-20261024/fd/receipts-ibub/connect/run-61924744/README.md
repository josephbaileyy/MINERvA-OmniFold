# IBUB connect R under BINDING 2: rc 0, job 61924744 submitted (2026-11-24)

**By** `director-helper-3`. The run was under the director's GO for IBUB BINDING 2 (#1294, merge `f879d0cb`), with
launcher `668ff3f6…` and connect `f73494a6…`. Both were extracted byte for byte from `f879d0cb` and checked by
`shasum`. It ran on login38 with window end 1795570595 (2026-11-25T01:36:35Z, the certificate's expiry). The job's own
records (its end, IBUB-DONE, the units) follow in a second PR.

| step | record |
|---|---|
| launcher start | `launch-start-utc.txt`: 2026-11-24T16:37:23Z; staged `sha256 f73494a6…` on login38 |
| connect start (its first `date -u`) | `connect-run.log.txt`: 2026-11-24T16:37:31Z |
| fences | cov2d rev 3 `FENCE CLEAR`; the sacct fence `fence clear`, then clear again just before sbatch |
| clone, overlap, preflight, stage | HEAD `d12c4f2a3` (M‴), porcelain empty; `OVERLAP: CLEAR (pairs checked 1430, hits 0)`; preflight PASS; stage PASS |
| sbatch | `submitted 61924744 2026-11-24T16:39:17Z`; `sacct: 61924744\|ibub_run\|PENDING` |
| scontrol | `scontrol: name, QOS (regular_1) and limit as declared`; the fetched `logs/scontrol-connect-61924744.txt` reads `QOS=regular_1`, `TimeLimit=11:29:00`, `JobState=PENDING` |
| the end | the clone's porcelain is empty after; `ibub run rc=0`; `connect-run.done.txt` 0; launcher rc 0 at 16:39:56Z |
| records | `fetch-run.tar` sha256 `1cf1859fe91006e1ad849b9632e94b9f66dc1e0750ee8cd3e30ceb816abd603c` (51,200 bytes), equal to the log's line; RECORDS.SHA256SUMS holds for its 8 files (`records-check.txt`, empty under `--quiet`) |
| sacct after it | `sacct-after-launch.txt`, at 16:40:55Z: `61924744\|ibub_run\|regular_1\|PENDING\|0:0\|None\|Unknown\|00:00:00` |

The job's state is followed by sacct only.
