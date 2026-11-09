# FD-PRR prr_misc: receipt (job 61030122)

The valid-region lane, 2026-11-09, under FD-PRR BINDING 1 ruling 7 and addendum A1, with the code at M_A1 =
6727020a7c58b00dd00806151c627c8a24f72402. It was launched against BINDING-1.md 04686d70 at main 348ddc94. This is the
third full job, the 93 tasks of queues/misc.tsv: B0 18, MCq 15, O2 15, O3 11, O4 11, O4r 11, and C400, C1000 and K20
4 each. Nothing here was repaired or relaunched.

CITABLE FOR: prr_misc ended COMPLETED with DONE, 93 of 93 tasks; the charge, 2.4047 node-h, and the study's charge so
far, 7.3786 of the 27.0 cap; the measured lane seconds per level against the dry run's rates; the queue span against
the gate's projection; the connect's checks; the post's logs/*misc* listing; that the dry, iter and cap products'
sha256 lines are unchanged in log-misc/SHA256SUMS.
NOT CITABLE FOR: any prior-retention reading (rho, PR-1 to PR-3, R-ID, R-SUP); those come from prr_read at M_A2, after
every job. Not for a rate's run-to-run spread beyond the n tasks listed per level.

## The connect (`cluster/logs/connect-misc.log.txt`, connect sha256 6e0a66a3…)

- **Before it.** iris on login06 at 11:25:28Z: m3246 18,353.1 charged of 20,000.0, and squeue --me was empty.
- **Launch.** One ssh session landed on login31. It staged the connect, checked its sha256 and launched it with
  nohup, all in that session (`lane/launch-session.txt`). ssh exited 0, read unpiped.
- **Other families** (lines 5-6): none listed.
- **iris** (line 9): the balance is 1646.9 node-h, half is 823.5, and the cap is 27.0.
- **Charge before** (lines 11-14): prr_dry 3648 s, prr_iter 9038 s and prr_cap 5220 s, 4.9739 node-h charged; with
  this job's 7.25 h limit the sum is 12.2239. The connect required all three rows as recorded before it went on.
- **Deploy** (lines 15-27). A fresh clone at M_A1, with porcelain --ignored 0 before and after (line 47). The six
  files matched the bound sha256, as did the declaration (5be1e19c…), A1 (ca6b8457…), and BINDING-1.md at origin/main
  348ddc94 (04686d70…). The inputs (queues/misc.tsv 4ed15792…, stage.json, log-dry/DONE) matched.
- **The gate's projection at t0** (line 33): 1.9468 h against 6.525 h, with `"unmeasured": []` and `"pass": true`.
- **Submission:** "Submitted batch job 61030122" (line 38). scontrol's TimeLimit read 07:15:00 (line 40).

## The job

- **Slurm.** `cluster/sacct.txt:2`: COMPLETED, exit 0:0, Elapsed 02:24:17 (8657 s), 1 node, 256 CPUs, from
  2026-11-09T03:27:13 to 05:51:30 (Pacific), limit 07:15:00.
- **Charge.** `cluster/charge_node_h.txt:1`: 2.4047 node-h.
- **The study so far.** `cluster/study-charge.txt` lists prr_dry at 3648 s, prr_iter at 9038 s, prr_cap at 5220 s and
  prr_misc at 8657 s, so 7.3786 node-h have been charged against the cap of 27.0.
- **Script output.** `cluster/logs/prr_misc_61030122.out.txt:1-3`: pin 6727020a, 8 lanes, limit 7:15:00, queue rc=0,
  done.
- **DONE.** `cluster/log-misc/DONE`: 93 tasks, 93 ended, rc 0. There is no STOP and no FAILED.
- **verify-stage.** It passed: there is no STOP, and its log is empty on success (0 bytes).
- **Products.** `cluster/log-misc/SHA256SUMS` lists 181: the 88 of `../cap/cluster/log-cap/SHA256SUMS`, each line
  unchanged, and 93 new ones (B0 18, MCq 15, O2 15, O3 11, O4 11, O4r 11, C400 4, C1000 4, K20 4). They stay on
  pscratch.
- **Task records.** Every task's GNU time record shows exit 0 (93 of 93). The largest maximum RSS is 12,546,276 kB.
- **Task logs.** The only warnings are sklearn's feature-name UserWarnings. Search: `grep -hiE
  'warn|error|traceback|nan|refus' cluster/log-misc/tasks/*.log.txt | sort | uniq -c` gives 1,143 LGBMClassifier, 525
  LGBMRegressor and 1,668 `warnings.warn(` lines @ this receipt.
- **Environment.** `cluster/log-misc/env.log.txt` is identical to the connect's pre-check
  (`cluster/logs/env-precheck-misc.log.txt`): the same two missing optional setup.sh lines as cap's, with deploy-misc.

## Measured against the dry run (`lane/misc_times.json`, from `lane/misc_times.py`)

| level | n | mean s | min to max s | dry rate s | mean / dry |
|---|---|---|---|---|---|
| B0 | 18 | 563.1 | 484.7 to 659.8 | 512.1 | 1.100 |
| C400 | 4 | 1312.3 | 1257.1 to 1388.3 | 1254.3 | 1.046 |
| C1000 | 4 | 2597.6 | 2510.0 to 2629.4 | 2531.1 | 1.026 |
| K20 | 4 | 1692.0 | 1660.3 to 1772.0 | 1417.9 | 1.193 |
| MCq | 15 | 431.2 | 353.7 to 539.6 | 283.3 | 1.522 |
| O2 | 15 | 533.9 | 459.1 to 632.2 | 497.4 | 1.073 |
| O3 | 11 | 552.2 | 471.3 to 659.6 | 440.4 | 1.254 |
| O4 | 11 | 585.3 | 458.8 to 723.6 | 433.4 | 1.351 |
| O4r | 11 | 588.9 | 549.6 to 673.5 | 394.7 | 1.492 |

- **The queue span** was 8628.5 s, or 2.3968 h. That is 1.231 × the projection of 1.9468 h, and well inside the gate's
  6.525 h.
- **Why the ratio is larger than iter's (1.060) and cap's (1.034).** Every level ran slower than its dry sample, and
  four short levels (MCq, O4r, O4, O3) ran 1.25 to 1.52 × slower. Those four are 48 of this queue's 93 tasks. This is
  an observation from the records; no cause is claimed.
- **B0's dry rate** is the mean of the dry run's two B0 tasks (512.1 s, `../dry/README.md`); every other level's dry
  rate is a single task.

## The post (`lane/post-session1.txt`, post sha256 053204df…)

- **The run.** One ssh session on login29 staged the post, checked its sha256 and ran it in the foreground. post_rc
  was 0 (line 15), the /dev/shm copy was gone after the run (line 16), and ssh exited 0, read unpiped.
- **logs/\*misc\*** (the director's check before the fetch). Listed in the same session before the post ran (lines
  3-14) and in post-misc/logs after it (lines 20-34): the same 11 files. They are the misc connect's 10 files and the
  job's prr_misc_61030122.out. No other job's file matches the glob.
- **The tarball.** post-misc.tar.gz is 80,706 bytes, with sha256
  8aef01eea45c74f0ab9b85df9a6b63e4149c5b018293eef011ee122fc9f13d78. The same sha256 came from the .sha256 file beside
  it, from the remote sha256sum (lines 17-18) and from the local file.
  - tasks/ holds 93 .log and 93 .time files and nothing else (lines 35-37), so there are no products in the tarball.
- **The extract.** Into an empty directory, with no absolute paths and no "..". SHA256SUMS then checked 421 of 421
  files.
  - `cluster/` is the extract. The 103 names git ignores carry ".txt" (`RENAMES.tsv`), and `lane/verify_receipts.py`
    re-checks them.
- **The final post.log and post.done.** Fetched separately, each with its sha256 matching on both sides (lines 39-40),
  into `cluster-final/`:
  - post.log is 200ae3fb…. Its diff from `cluster/post.log.txt` is the 3 appended lines only, ending "prr misc post
    rc=0";
  - post.done is 9a271f2a… and reads "0".

## The post's SHA256SUMS does not cover log-misc/SHA256SUMS

- **The gap.** The post builds its SHA256SUMS with `find . -type f ! -name SHA256SUMS ! -name post.log ! -name
  post.done` (`cluster/prr_misc_post.sh:55`, unchanged from the cap post's line 55). That leaves out
  log-misc/SHA256SUMS. `../cap/README.md` records the same gap for dry, iter and cap.
- **The director's ruling (a), 2026-11-09.** The misc and ibu posts stay copies of the cap post. Each receipt records
  a direct read-only sha256 of log-$MODE/SHA256SUMS and passes it to its verify_receipts.py. Line 55 is not changed in
  this study; it is on the follow-up list.
- **The direct check.** In the post's own session (lines 41-44), $OUT/log-misc/SHA256SUMS and
  $OUT/post-misc/log-misc/SHA256SUMS both read 90f6531dd496d0d9b878c95f4fb058ab0bc7ff8af155ce0ed8a3c8858fe5de6d, with
  181 lines. The committed copy has the same sha256.
- **In the verifier.** `lane/verify_receipts.py` takes that sha256 as its second argument and fails if it differs.

## Files

- `cluster/`: $OUT/post-misc as extracted, with the renames in `RENAMES.tsv`.
- `cluster-final/`: post.log and post.done, fetched after the post ended.
- `lane/launch-session.txt` and `lane/post-session1.txt`: the two ssh sessions.
- `lane/misc_times.py` and `lane/misc_times.json`: the measured times.
- `lane/verify_receipts.py`: re-checks `cluster/`.
- `lane/check-at-head.txt`: both scripts rerun in a clean clone at this receipt's head.
