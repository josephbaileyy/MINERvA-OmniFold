Resume the exact `agent-E-g2-source` UUID. Your build turn returned rc=0, but
the claimed Claude-background detachment did not survive provider-turn exit:
the login-side `srun` process disappeared, the partial ROOT stopped at
18,400,000/22,191,105 truth entries, and no `loop.rc`, DONE, or FAILED sentinel
exists. Treat attempt 1 as INTERRUPTED and never as evidence. Do not rebuild;
the canonical installed binary is already BUILD-PASS with SHA256
`61d7dfbf7ee38f39e51c656b48702056c773c3d1c5d1b2d9bf08a6da42d2e19b`.

This turn authorizes only a correctly OS-detached relaunch of the same 1A G2
smoke on the existing holder `56100487`, if it is still live with sufficient
wall. Do not submit sbatch, request a second holder, run 12 playlists, build an
NPZ, train PET, validate/adopt a scientific product, or touch other agents.

1. Reconfirm no `srun`/event-loop writer remains for attempt 1 and record its
   interrupted artifact/log sizes. Preserve it under its current namespace;
   launch attempt 2 in a distinct `nd-unfolding/pet/g2_smoke/attempt2/` work
   directory so no incomplete file is overwritten or mistaken for final.
2. Do NOT use Claude's background-Bash/task feature. From a foreground shell,
   start an explicit OS-detached `setsid` driver whose own process synchronously
   calls `alloc_run.sh`/`srun` for the event loop and writes `loop.rc` plus
   DONE/FAILED only after exit. Redirect stdin from `/dev/null` and stdout/stderr
   to an attempt-specific driver log. Use the canonical 1A manifests, canonical
   installed binary, and both `MNV101_DUMP_POINTCLOUD=1` and
   `MNV101_FULL_PHASE_SPACE=1`.
3. Before returning, prove detachment rather than assuming it: record driver
   PID, PPID, SID and command; require SID==PID; wait at least five seconds;
   show the driver and descendant `srun` still live and the attempt-2 loop log
   or ROOT growing. The driver must survive this Claude process and reparent to
   PID 1 after turn exit. If that invariant cannot be established, stop and
   report failure without another launch.
4. Return only SMOKE-RUNNING with the exact allocation, OS PID/SID, attempt-2
   paths and survival evidence. Do not claim validation or commit the pending
   G2 status/validator. The orchestrator will observe the DONE/FAILED sentinel
   and resume this same UUID for Stage 4 after a real terminal event.

Preserve the existing uncommitted E-owned status and validator. Do not stage or
commit during this relaunch-only turn. Leave the allocation alive.
