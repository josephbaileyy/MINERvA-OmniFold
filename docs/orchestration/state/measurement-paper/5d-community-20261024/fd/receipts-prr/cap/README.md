# FD-PRR prr_cap: receipt (job 61028298)

The valid-region lane, 2026-11-09, under FD-PRR BINDING 1 ruling 7 and addendum A1, with the code at M_A1 =
6727020a7c58b00dd00806151c627c8a24f72402. It was launched against BINDING-1.md 04686d70, after erratum E1. This is
the second full job, the capacity levels C25, C400 and C1000 at the truths of the committed queue. Nothing here was
repaired or relaunched.

CITABLE FOR: prr_cap ended COMPLETED with DONE, 29 of 29 tasks; the charge, 1.4500 node-h, and the study's charge so
far, 4.9739 of the 27.0 cap; the measured lane seconds per level against the dry run's rates; the queue span against
the gate's projection; the connect's checks; the post's logs/*cap* listing; that the dry and iter products' sha256
lines are unchanged in log-cap/SHA256SUMS.
NOT CITABLE FOR: any prior-retention reading (rho, PR-1 to PR-3); those come from prr_read at M_A2, after every job.
Not for a rate's run-to-run spread beyond the n tasks listed per level.

## The connect (`cluster/logs/connect-cap.log.txt`, connect sha256 f32aeafa…)

- **Launch.** One ssh session landed on login16. It staged the connect, checked its sha256 and launched it with
  nohup, all in that session (`lane/launch-session.txt`). ssh exited 0, read unpiped.
- **Other families** (lines 5-6): none listed.
- **iris** (line 9): the balance is 1648.4 node-h, half is 824.2, and the cap is 27.0.
- **Charge before** (lines 11-13): prr_dry 3648 s and prr_iter 9038 s, 3.5239 node-h charged; with this job's 6.5 h
  limit the sum is 10.0239. The connect required both rows as recorded before it went on.
- **Deploy** (lines 14-26). A fresh clone at M_A1, with porcelain --ignored 0 before and after (line 46). The six
  files matched the bound sha256, as did the declaration (5be1e19c…), A1 (ca6b8457…), and BINDING-1.md at origin/main
  7085fee5 (04686d70…). The inputs (queues/cap.tsv 480b124d…, stage.json, log-dry/DONE) matched.
- **The gate's projection at t0** (line 32): 1.3937 h against 5.85 h, with `"unmeasured": []` and `"pass": true`.
- **Submission:** "Submitted batch job 61028298" (line 37). scontrol's TimeLimit read 06:30:00 (line 39).

## The job

- **Slurm.** `cluster/sacct.txt:2`: COMPLETED, exit 0:0, Elapsed 01:27:00 (5220 s), 1 node, 256 CPUs, from
  2026-11-09T01:43:52 to 03:10:52 (Pacific), limit 06:30:00.
- **Charge.** `cluster/charge_node_h.txt:1`: 1.4500 node-h.
- **The study so far.** `cluster/study-charge.txt` lists prr_dry at 3648 s, prr_iter at 9038 s and prr_cap at 5220 s,
  so 4.9739 node-h have been charged against the cap of 27.0.
- **Script output.** `cluster/logs/prr_cap_61028298.out.txt:1-3`: pin 6727020a, 8 lanes, limit 6:30:00, queue rc=0,
  done.
- **DONE.** `cluster/log-cap/DONE`: 29 tasks, 29 ended, rc 0. There is no STOP and no FAILED.
- **verify-stage.** It passed: there is no STOP, and its log is empty on success (0 bytes).
- **Products.** `cluster/log-cap/SHA256SUMS` lists 88: the 15 dry, the 44 iter and the 29 cap products. They stay on
  pscratch. Each of the 59 lines of `../iter/cluster/log-iter/SHA256SUMS` appears unchanged among the 88, and the 29
  others are C25 11, C400 11 and C1000 7.
- **Task records.** Every task's GNU time record shows exit 0 (29 of 29). The largest maximum RSS is 11,974,792 kB.
- **Task logs.** The only warnings are sklearn's feature-name UserWarnings. Search: `grep -hiE
  'warn|error|traceback|nan|refus' cluster/log-cap/tasks/*.log.txt | sort | uniq -c` gives 319 LGBMClassifier, 145
  LGBMRegressor and 464 `warnings.warn(` lines @ this receipt.
- **Environment.** `cluster/log-cap/env.log.txt` has the same two missing optional setup.sh lines as the connect's
  pre-check (`cluster/logs/env-precheck-cap.log.txt`, identical) and as iter's, with deploy-cap in place of deploy-iter.

## Measured against the dry run (`lane/cap_times.json`, from `lane/cap_times.py`)

| level | n | mean s | min to max s | dry rate s | mean / dry |
|---|---|---|---|---|---|
| C25 | 11 | 375.5 | 333.2 to 446.6 | 254.1 | 1.478 |
| C400 | 11 | 1364.2 | 1213.6 to 1605.2 | 1254.3 | 1.088 |
| C1000 | 7 | 2451.2 | 2338.8 to 2560.2 | 2531.1 | 0.968 |

- **The queue span** was 5187.8 s, or 1.4410 h. That is 1.034 × the projection of 1.3937 h, and well inside the gate's
  5.85 h.
- **C25, the shortest task, ran slowest relative to its single dry sample,** as K2 did in iter. C1000 ran a little
  faster than its dry sample.

## The post (`lane/post-session1.txt`, post sha256 15a7e143…)

- **The run.** One ssh session on login28 staged the post, checked its sha256 and ran it in the foreground. post_rc
  was 0 (line 15), the /dev/shm copy was gone after the run (line 16), and ssh exited 0, read unpiped.
- **logs/\*cap\*** (the director's check before the fetch). Listed in the same session before the post ran (lines
  3-14) and in post-cap/logs after it (lines 20-34): the same 11 files. They are the cap connect's 10 files and the
  job's prr_cap_61028298.out. No other job's file matches the glob.
- **The tarball.** post-cap.tar.gz is 36,415 bytes, with sha256
  1e1e071161e35abd45a4d30b524003ae641c567c11c414cfd0a1e8694df758d2. The same sha256 came from the .sha256 file beside
  it, from the remote sha256sum (lines 17-18) and from the local file.
  - tasks/ holds 29 .log and 29 .time files and nothing else (lines 35-37), so there are no products in the tarball.
- **The extract.** Into an empty directory, with no absolute paths and no "..". SHA256SUMS then checked 165 of 165
  files.
  - `cluster/` is the extract. The 39 names git ignores carry ".txt" (`RENAMES.tsv`), and `lane/verify_receipts.py`
    re-checks them.
- **The final post.log and post.done.** Fetched separately, each with its sha256 matching on both sides (lines 39-40),
  into `cluster-final/`:
  - post.log is 0f843385…. Its diff from `cluster/post.log.txt` is the 3 appended lines only, ending "prr cap post
    rc=0";
  - post.done is 9a271f2a… and reads "0".

## The post's SHA256SUMS does not cover log-$MODE/SHA256SUMS

- **What.** The post builds its SHA256SUMS with `find . -type f ! -name SHA256SUMS ! -name post.log ! -name post.done`
  (`cluster/prr_cap_post.sh:55`). That leaves out log-cap/SHA256SUMS as well as the top-level file. The same line is
  in the dry and iter posts, so `../dry/` and `../iter/` have the same gap. Their READMEs do not say so.
- **Closed by a direct check, 2026-11-09.** Read-only sha256sum on the cluster, compared with the committed copies:

  | file | sha256 | committed copy |
  |---|---|---|
  | $OUT/log-cap/SHA256SUMS | e791abe3eb1ffafc1f401d0668d0770edf06464285f2d1cd00ae0816bd442141 | same |
  | $OUT/log-iter/SHA256SUMS and post-iter/log-iter/SHA256SUMS | 3e8c59f31c43decd1633d2ab6089138a06a072438c9666b1c5c9dff44d5f1af3 | same |
  | $OUT/log-dry/SHA256SUMS and post-dry/log-dry/SHA256SUMS | 082506fae14749f8791bb227e9bf8bca29e87200abbd8ff29d75f0feb69a0f3d | same |

- **In the verifier.** `lane/verify_receipts.py` takes the log-cap sha256 as its second argument and fails if it
  differs. The dry and iter receipts are not changed.
- **For misc and ibu.** Their posts will be copies of this one, so each of their receipts will record the same direct
  check, unless the director rules otherwise.

## Files

- `cluster/`: $OUT/post-cap as extracted, with the renames in `RENAMES.tsv`.
- `cluster-final/`: post.log and post.done, fetched after the post ended.
- `lane/launch-session.txt` and `lane/post-session1.txt`: the two ssh sessions.
- `lane/cap_times.py` and `lane/cap_times.json`: the measured times.
- `lane/verify_receipts.py`: re-checks `cluster/`.
- `lane/check-at-head.txt`: both scripts rerun in a clean clone at this receipt's head.
