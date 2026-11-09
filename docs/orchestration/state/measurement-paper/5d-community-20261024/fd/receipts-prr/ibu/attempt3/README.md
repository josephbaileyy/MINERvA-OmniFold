# FD-PRR prr_ibu attempt 3: receipt (job 61057142, COMPLETED)

The valid-region lane, 2026-11-09, under FD-PRR BINDING 1 ruling 7 and addendums A1, A3 and A4. The code was at
M_A4 = cb13a6443a457bd3887d1c421723dfcdb1909ec8, bound by #1003 (BINDING-1.md 634cded3…). The director gave the go for
the connect `prr_ibu3_submit.sh` at sha256 17fbafb9a85d44f2d3a19055e8eb64d3c3f0faee83c3b918c85b74abbee77c6b and the post
`prr_ibu3_post.sh` at 7b598fec73795244ea2d63e46d8c5da02743ce6d001bb47ad9e4a229c60302c7. Route 2 ran once and
completed; nothing was repaired or relaunched. Attempts 1 and 2 are recorded in `../attempt1/` and `../attempt2/`, and
the rho staging it started from in `../../stage-a4/`.

CITABLE FOR: prr_ibu 61057142 ended COMPLETED 0:0 after 546 s with DONE rc 0; ibu.log's line `{"experiments": 20,
"C-IBU": true}`; the charge, 0.1517 node-h, and the study's charge, 7.5783 of the 27.0 cap; the two route-2 products'
sha256 (`cluster/log-ibu/SHA256SUMS`); the connect's checks; that the job ran without a refusal under REF-G1's guard.
NOT CITABLE FOR: any prior-retention reading (C-IBU's components, R-ID, R-SUP, PR-2); those come from prr_read, which
has not run. Not for which rho files the job opened: ibu.log records only its one summary line, and no per-read trace
was logged on the cluster.
<!-- absence-ok: prr_read is the lane's next step, run only on the director's go; ibu.log is one line (cluster/log-ibu/ibu.log.txt) -->

## The connect (`cluster/logs/connect-ibu-3.log.txt`, connect sha256 17fbafb9…)

- **Before it.** A separate read-only session, on login20 at 2026-11-09T22:48:42Z (`lane/iris-before.txt`), printed:
  - iris and `squeue --me`: only cov2d's two ll5d_gate jobs, no prr_* job;
  - the absence of `route2`, `log-ibu`, `deploy-ibu-3`, the ibu-3 connect log, done and jobid, `post-ibu` and
    `post-ibu.tar.gz`;
  - the presence of `ibu-attempt2/{log-ibu,route2}`, `stage-a4.json` (00457e58…) and `stage/s5p-nullsF`.
  <!-- absence-ok: each path's own ls -d "No such file or directory" in lane/iris-before.txt -->
- **Launch.** One ssh session, on login31 at 22:48:53Z. It staged the connect in /dev/shm, checked its sha256 and
  launched it with nohup (`lane/launch-session.txt`). ssh exited 0, read unpiped. The deployed copy,
  `cluster/logs/prr_ibu-3_submit.sh`, is byte for byte the approved script.
- **The connect's log** (line numbers are `cat -n`'s in `lane/connect-readback.txt`):
  - Other families (lines 7-9): ll5d_gate_AR23 and ll5d_gate_G18, listed and not refused.
  - iris (lines 11-12): balance 1627.4 node-h, half 813.7, cap 27.0.
  - Charge before (lines 14-20): the four completed jobs and both earlier attempts, 61035510 FAILED 41 s and 61043652
    FAILED 132 s, each required as recorded. Charged 7.4267 node-h; with this job's 0.5 h limit the sum is 7.9267.
  - Deploy (lines 21-32): a fresh clone at M_A4, porcelain --ignored 0 before and after (line 62). The six FD-PRR files
    are OK. The declaration, A1, A3 and A4 (3ba2f47b…) are at their bound sha256, and BINDING-1.md at origin/main
    65875111 is 634cded3….
  - Inputs (lines 33-43): the four queues, stage.json, log-dry/DONE, stage-a4.json and the four staged rho copies are
    all OK against their pins. There are 20 B0 lines (line 44).
  - Environment (lines 45-50): python 3.11.14 (root_6_28), lightgbm 4.6.0, scipy 1.16.3, numpy 1.26.4; `prr_probe.py
    limit ibu` gives 0:30:00.
  - Submission (lines 52-56): "Submitted batch job 61057142"; scontrol's TimeLimit read 00:30:00. The connect ended
    "prr ibu-3 submit rc=0" at 22:49:59Z (lines 63-64).

## The job

- **Slurm** (`cluster/sacct.txt:2`): COMPLETED, exit 0:0, Elapsed 00:09:06 (546 s), 1 node, 256 CPUs. It ran from
  2026-11-09T15:03:45 to 15:12:51 (Pacific) with a limit of 00:30:00. The `.batch` and `.extern` steps are COMPLETED
  0:0. The lane's watch saw PENDING, RUNNING, then COMPLETED (`lane/watch.txt`).
- **Charge** (`cluster/charge_node_h.txt`): 0.1517 node-h, against the 0.5 bound.
- **The study so far** (`cluster/study-charge.txt`): the seven prr_* jobs come to 7.5783 node-h of the 27.0 cap.
- **Script output** (`cluster/logs/prr_ibu_61057142.out.txt`): `pin=cb13a644…`, start 2026-11-09T23:04:24Z, then
  `[prr] done`.
- **DONE** (`cluster/log-ibu/DONE`): `{"mode": "ibu", "rc": 0, "job": "61057142"}`. There is no STOP and no FAILED.
  <!-- absence-ok: the post copies log-ibu/STOP and FAILED when present (prr_ibu_post.sh); the fetched log-ibu/ holds only DONE, env.log, ibu.log, SHA256SUMS and verify-stage.log -->
- **verify-stage** passed. Its log is empty on success (0 bytes, e3b0c442…).
- **ibu.log** (`cluster/log-ibu/ibu.log.txt`, one line): `{"experiments": 20, "C-IBU": true}`.
- **Products** (`cluster/log-ibu/SHA256SUMS`). They stay on pscratch:
  - `route2/route2.npz` 759be4ab28cc10950fcdb0fcd6c6a438749ea78c7b7286f3ff02798fe77d8a68;
  - `route2/route2.json` ac6b1940659c6ae4da194e2f9dbc9e43fad7ada6083f4ba8fd8ef8faf891f6e5.
- **Environment.** `cluster/log-ibu/env.log.txt` is byte for byte the connect's pre-check
  (`cluster/logs/env-precheck-ibu-3.log.txt`; both 83a0341a…). It holds the same two missing optional setup.sh lines
  as the earlier jobs, with deploy-ibu-3 in place.
- **The rho reads.** A per-read trace was not logged on the cluster, so this is shown by the code, not observed:
  <!-- absence-ok: ibu.log is one line (cluster/log-ibu/ibu.log.txt) and the job .out two; nothing else logs reads -->
  - the run ran inside REF-G1's read guard at M_A4, which refuses a plain read of the shared s5p-20260926 path;
  - `prr_ibu.capture` refuses a hypothesis whose rho sha256 has no staged copy;
  - the job ended rc 0 with no refusal.
  The REQUIRED test and the trace in `../../a4/` show the same path on the synthetic fixture: 8 loads, all from
  `stage/s5p-nullsF`.

## The post and the fetch

- **The post** ran in one foreground session, on login24 at 23:22:39Z (`lane/post-session.txt`). It staged the post in
  /dev/shm and checked its sha256, and ended with post rc 0 and post.done 0. It copied 43 files and wrote
  `post-ibu.tar.gz` with sha256 c07245467564cca6bda0d4c5146eeb77dff41f61fddfde15f4266981f0748a8c.
- **The fetch.** `scp` into a new empty directory; the sha256 matches (`lane/fetch-sha256.txt`). Every member is under
  `post-ibu/`. `sha256sum -c SHA256SUMS` gives 41 of 41 OK.
- **What is committed here.**
  - The attempt-3 files from the tarball: `logs/*ibu-3*`, the job's .out, `log-ibu/`, sacct, the charges, the post's
    SHA256SUMS, its script and its log.
  - The tarball's copies of attempts 1's and 2's logs are not repeated. They are committed in `../attempt1/` and
    `../attempt2/`.
- **Renames.** The eleven names git ignores carry ".txt" (`RENAMES.tsv`). Their contents are unchanged.

## Next

The PRR read (`prr_read.py`) over all five jobs' products, on its own script and the director's go.
