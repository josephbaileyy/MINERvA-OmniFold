# EVW5D attempt 1 (BINDING 1): a false STOP at the connect's allocation check, 0 node-h

The one bound connect (2026-11-25, launch/bound/evw5d_connect.sh a002ec55, from a checkout at aada31f2, login31 by a
read-only load survey, the certificate valid to 2026-11-26T15:19:52Z) passed every precondition and submitted one job,
61997953. Its post-submit check then printed `scontrol TimeLimit=00:30:00 (declared 00:30:00) NumNodes=1-1
array_lines=0` and cancelled the job: scontrol shows a pending job's node count as a range, and the check compared it
with `1`. The allocation was the declared one (one node, 30:00, no array).

- sacct: `61997953|evw5d|CANCELLED by 112498|0:0|0|1|None|2026-11-25T13:36:06` (ElapsedRaw 0, never started; 0 node-h).
- The director accepted it as terminal and as a false refusal (2026-11-25), and ruled the fix (NumNodes matching
  `^1(-1)?$`), a new namespace for the rerun (`/pscratch/sd/j/josephrb/evw5d-20261125-r2`), and a fixture test.
- Attempt 1's directories on scratch (`evw5d-20261125/{deploy,toolclone,logs}`) are left as they are; removing scratch
  run data is Joseph's call.

`cluster-logs/` holds the connect's logs, copied read-only from `$OUT/logs` (the staged `evw5d_connect.sh` there has
sha256 a002ec55, the bound one). `lane/` holds the launcher's output, the ssh session, the login survey and the sacct
line. The `*.out`, `*.err` and `*.log` files are force-added (`.gitignore` would drop them).
