# FD-PRR dry run: receipt (job 61022062, prr_dry)

The valid-region lane, 2026-11-09, under FD-PRR BINDING 1 ruling 7 and addendum A1 (code at M_A1 =
6727020a7c58b00dd00806151c627c8a24f72402). The dry run of FD-PRR-DECLARATION.md §10.3: staging, the 15-task dry queue,
then C-PAIR and C-MASK. Nothing here was repaired or relaunched.

CITABLE FOR: the dry job ended COMPLETED with DONE; C-PAIR and C-MASK passed; the charge was 1.0133 node-h; the
measured lane seconds of one task per level; the projections the full jobs' gate starts from; the scp incident and the
stale-copy sweep.
NOT CITABLE FOR: any prior-retention reading (rho, PR-1 to PR-3, R-ID, R-SUP); those come from the full jobs and
prr_read.py. Also not for a rate's run-to-run spread: each level has one task, except B0, which has two.

## The job

- **Slurm.** `cluster/sacct.txt:2`: prr_dry, COMPLETED, exit 0:0, Elapsed 01:00:48 (3648 s), 1 node, 256 CPUs, from
  2026-11-08T20:55:14 to 21:56:02 (Pacific), TimeLimit 05:15:00.
- **Charge.** `cluster/charge_node_h.txt:1` gives 1.0133 node-h, which is ElapsedRaw × NNodes / 3600. The dry limit is
  5.25 h and the study cap is 27.0.
- **Script output.** `cluster/logs/prr_dry_61022062.out.txt:1-3`: pin 6727020a, 8 lanes, limit 5:15:00, queue rc=0,
  done.
- **DONE.** `cluster/log-dry/DONE:1`: 15 tasks, 15 ended, rc 0.
- **Staging.** `cluster/log-dry/stage.log.txt:1` records `{"staged": 6}`; the per-file stat records are in
  `cluster/stage.json`.
- **C-PAIR and C-MASK.** `cluster/log-dry/pair.json`:
  - C-PAIR nominal: 65,856 cells, 0 differing;
  - C-PAIR A7_gibuu: 65,856 cells, 0 differing;
  - C-MASK nominal: pass;
  - overall: pass.
- **Products.** The 15 products stay on pscratch under $OUT/runs. They are listed by sha256 in
  `cluster/log-dry/SHA256SUMS`, which has 15 lines.
- **Task records.** Every task's GNU time record shows exit 0 (`cluster/log-dry/tasks/*.time`). The largest maximum
  RSS is 12,548,500 kB (O5), so 8 lanes used about 100 GB of the node's 512 GB.
- **Task logs.** The only warnings are sklearn's "X does not have valid feature names" UserWarnings from LGBM.
  Search: `grep -hiE 'warn|error|traceback|nan|refus' cluster/log-dry/tasks/*.log.txt | sort | uniq -c` gives 3
  distinct lines: 289 LGBMClassifier, 137 LGBMRegressor and 426 `warnings.warn(` @ this receipt.
- **Environment.** `cluster/log-dry/env.log.txt` has two lines, both missing optional setup.sh files
  (unbinned_unfolding/build and MINERvA101). The connect's pre-check shows the same two lines
  (`cluster/logs/env-precheck.log.txt`). The A1 source and the lightgbm, scipy and numpy import passed.

## Measured lane seconds per level (one unfold per task; `lane/projection.json`)

UNIT_S = 657.4464 s (prr_probe.py:197 @ 6727020a). The measured column is wall / UNIT_S. The wall is .end − .start in
`cluster/log-dry/` (each file holds time.time(); the gate's clock).

| level | assumed u | wall s | measured u |
|---|---|---|---|
| K2 | 0.4 | 215.9 | 0.328 |
| K10 | 2 | 860.5 | 1.309 |
| K20 | 4 | 1417.9 | 2.157 |
| K50 | 10 | 3596.9 | 5.471 |
| C25 | 0.5 | 254.1 | 0.387 |
| C400 | 4 | 1254.3 | 1.908 |
| C1000 | 15 | 2531.1 | 3.850 |
| MCq | 1 | 283.3 | 0.431 |
| O4r | 1 | 394.7 | 0.600 |
| O4 | 1 | 433.4 | 0.659 |
| O3 | 1 | 440.4 | 0.670 |
| O2 | 1 | 497.4 | 0.757 |
| O5 | 1 | 405.5 | 0.617 |
| B0 (A7_gibuu, nominal) | 1 | 487.6, 536.5 (mean 512.1) | 0.742, 0.816 |

Every level ran below its assumed units. The queue spanned 3597.2 s, set by K50, not by C1000, which the queue's order
assumed longest (`lane/projection.json:162`).

## What the full jobs' gate starts from

`lane/project_full.py` calls prr_probe.project() at the job's t0, on each committed queue. It uses the dry records
alone: a full job copies them into its log (sbatch_prr.sh:94 @ 6727020a). The script was run from a clean clone at
6727020a with nice 19 and thread caps 1. All three jobs have every level measured, and none of their tasks is a dry task.

| job | tasks | projected h | gate 0.9 × --time | --time | lines |
|---|---|---|---|---|---|
| iter | 44 | 2.3573 | 6.75 | 7:30:00 | `lane/projection.json:112-126` |
| cap | 29 | 1.3937 | 5.85 | 6:30:00 | `lane/projection.json:127-140` |
| misc | 93 | 1.9468 | 6.525 | 7:15:00 | `lane/projection.json:141-161` |

The gate re-projects before every launch, and from the first ends of the full job its own records join the rates
(prr_probe.py:489-519 @ 6727020a). A projection of 5.70 h for the three jobs, plus 1.01 h for the dry run and ≤ 0.5 h
for ibu, is about 7.2 node-h against the 27.0 cap. That is an expectation, not a measurement. The declared --time
limits are bound in code (JOB_LIMIT_H, prr_probe.py:201) and are left as declared: a job is charged its Elapsed, and
the limit bounds only a hang.

## The post connect

- **Copy and run.** `lane/post-session1.txt` records the session. The script was copied, checked and run in one ssh
  session on login30:
  - staged sha256 9a957fb8d002a79aefda87d8a73e935f1133781ba1e026a222b6ff1851e203d4 (line 2);
  - post_rc=0 (line 3);
  - the /dev/shm copy was gone after the run (line 4);
  - ssh rc 0, read unpiped.
- **The script.** Its own copy is `cluster/prr_dry_post.sh`, and its log is `cluster/post.log.txt`.
- **The tarball.** $OUT/post-dry.tar.gz has sha256 f1091205090273018f988f8dff890953aa8e5652cdaff5181512cab04cfb8480,
  both on the cluster and after fetching. It was extracted into an empty directory with no absolute paths or "..".
  `cluster/SHA256SUMS` then checked 85 of 85 files.
- **What is committed.** The extracted files are committed under `cluster/`. The 26 names git ignores (*.log, *.out,
  *.err) carry ".txt", and their contents are unchanged (`RENAMES.tsv`). `lane/verify_receipts.py` re-checks them.

## The scp incident (2026-11-09T04:51Z, before the launch)

- **What happened.** The launch connect, prr_dry_submit.sh (sha256 934c9c2f…), was first copied with scp to
  saul.nersc.gov:/dev/shm. The next ssh session to saul.nersc.gov landed on login12, and the file was not there. That
  session ran only `hostname`, `chmod` and `sha256sum`. chmod and sha256sum failed with "No such file or directory",
  and ssh exited 1.
- **Why.** saul.nersc.gov round-robins between login nodes, and /dev/shm is local to each node.
- **Nothing ran.** No session ran the copy. The real launch then copied, checked and ran the connect in a single ssh
  session. The copy is also inert: the connect refuses at once if $OUT exists (`[ ! -e "$OUT" ] || bail`,
  `cluster/logs/prr_dry_submit.sh:33`), and $OUT has existed since the real launch.
- **The rule from now on.** Every staged copy goes in the same ssh session as its run.

## The stale-copy sweep (2026-11-09T05:56Z, at the post)

- **The sweep.** From login29, each of login01 to login40 was asked for /dev/shm/prr_dry_submit.sh, and every copy
  found was removed. `lane/stale-sweep-raw.txt` is the raw output, NERSC's login banners included.
  `lane/stale-sweep-summary.txt` has one line per node.
- **login27: found and removed.** `lane/stale-sweep-summary.txt:27`: sha256
  934c9c2f45acd91a751135476ad063d9addd29e40463a048a93926102afd646d, 11,384 bytes, mtime 2026-11-08 20:51:29.55 −0800
  (04:51:29Z, the scp's minute). Removed, and absent after removal.
- **Absent: 36 nodes.** These include login29, where the sweep ran from, and login30, where the post ran
  (`lane/post-session1.txt:5-6`).
- **Not reached: login07, login17 and login19.** login07 and login17 gave "No route to host" (summary lines 7 and 17).
  login19 refused logins with pam_nologin (summary line 19). This receipt says nothing about /dev/shm on those three.
  The copy found on login27 matches the scp's minute, so it is the incident's copy.

## Added later: the final post.log and post.done (2026-11-09)

- **Why.** `cluster/post.log.txt` is the tarball's copy. The tar is made while post.log is still the post's open
  stdout, so that copy lacks the last 3 lines: the tarball's sha256, "prr dry post rc=0" and the time. post.done
  is absent from the tarball for the same reason. This is the director's low on the iter post.
- **What was added.** Both files were fetched read-only from $OUT/post-dry, each with its sha256 matching on both
  sides, into `cluster-final/`:
  - post.log.txt is f8f0f970…. Its diff from `cluster/post.log.txt` is those 3 lines only;
  - post.done is 9a271f2a… and reads "0".
- **Nothing above is changed.** The fetch is recorded in `../iter/README.md`.

## Files

- `cluster/`: $OUT/post-dry as extracted, with the renames in `RENAMES.tsv`.
- `lane/post-session1.txt`: the post connect's ssh session.
- `lane/stale-sweep-raw.txt` and `lane/stale-sweep-summary.txt`: the sweep.
- `lane/project_full.py` and `lane/projection.json`: the measured times and the projections.
- `lane/verify_receipts.py`: re-checks `cluster/` against `cluster/SHA256SUMS`.
- `lane/check-at-head.txt`: both scripts rerun in a clean clone at this receipt's head.
