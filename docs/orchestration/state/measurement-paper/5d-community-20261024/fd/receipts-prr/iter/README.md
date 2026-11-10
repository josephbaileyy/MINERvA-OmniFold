# FD-PRR prr_iter: receipt (job 61024185)

The valid-region lane, 2026-11-09, under FD-PRR BINDING 1 ruling 7 and addendum A1, with the code at M_A1 =
6727020a7c58b00dd00806151c627c8a24f72402. It was launched against BINDING-1.md e3d8724b, before erratum E1, which
changes no limit. This is the first full job, the F1 iteration levels K2, K10, K20 and
K50 at the 11 non-dry truths. Nothing here was repaired or relaunched.

CITABLE FOR: prr_iter ended COMPLETED with DONE, 44 of 44 tasks; the charge, 2.5106 node-h, and the study's charge so
far, 3.5239 of the 27.0 cap; the measured lane seconds per level against the dry run's rates; the queue span against
the gate's projection; the connect's checks; the second sweep of login07, login17 and login19.
NOT CITABLE FOR: any prior-retention reading (rho, PR-1 to PR-3); those come from prr_read at M_A2, after every job.

## The connect (`cluster/logs/connect-iter.log.txt`, connect sha256 4666c631…)

- **Launch.** One ssh session landed on login34. It staged the connect, checked its sha256 and launched it with
  nohup, all in that session (`lane/launch-session.txt`). ssh exited 0, read unpiped.
- **iris** (line 13): the balance is 1653.7 node-h, half is 826.9, and the cap is 27.0.
- **Charge before** (line 16): 1.0133 node-h charged; with this job's 7.5 h limit the sum is 8.5133.
- **Deploy.** A fresh clone at M_A1, with porcelain --ignored 0 before and after. The six files matched the bound
  sha256, as did the declaration, A1, and BINDING-1.md at main db337440 (`e3d8724b`). The inputs (queues/iter.tsv,
  stage.json, log-dry/DONE) matched the dry run's digests.
- **The gate's projection at t0** (line 35): 2.3573 h against 6.75 h, with `"unmeasured": []` and `"pass": true`.
- **Submission:** "Submitted batch job 61024185" (line 40). scontrol's TimeLimit read 07:30:00 (line 42).

## The job

- **Slurm.** `cluster/sacct.txt:2`: COMPLETED, exit 0:0, Elapsed 02:30:38 (9038 s), 1 node, 256 CPUs, limit 07:30:00.
- **Charge.** `cluster/charge_node_h.txt:1`: 2.5106 node-h.
- **The study so far.** `cluster/study-charge.txt` lists prr_dry at 3648 s and prr_iter at 9038 s, so 3.5239 node-h
  have been charged against the cap of 27.0.
- **Script output.** `cluster/logs/prr_iter_61024185.out.txt:1-3`: pin 6727020a, 8 lanes, limit 7:30:00, queue rc=0,
  done.
- **DONE.** `cluster/log-iter/DONE`: 44 tasks, 44 ended, rc 0. There is no STOP and no FAILED.
- **verify-stage.** It passed: there is no STOP, and its log is empty on success.
- **Products.** `cluster/log-iter/SHA256SUMS` lists 59: the 15 dry products and the 44 iter products. They stay on
  pscratch.
- **Task records.** Every task's GNU time record shows exit 0 (44 of 44).
- **Task logs.** The only warnings are sklearn's feature-name UserWarnings. Search: `grep -hiE 'warn|error|traceback|nan|refus'
  cluster/log-iter/tasks/*.log.txt | sort | uniq -c` gives 1,848 LGBMClassifier, 902 LGBMRegressor and 2,750
  `warnings.warn(` lines @ this receipt.

## Measured against the dry run (`lane/iter_times.json`, from `lane/iter_times.py`)

| level | n | mean s | min to max s | dry rate s | mean / dry |
|---|---|---|---|---|---|
| K2 | 11 | 290.8 | 255.5 to 373.4 | 215.9 | 1.347 |
| K10 | 11 | 896.9 | 778.6 to 1064.1 | 860.5 | 1.042 |
| K20 | 11 | 1564.8 | 1373.6 to 1758.5 | 1417.9 | 1.104 |
| K50 | 11 | 3668.3 | 3313.6 to 3850.9 | 3596.9 | 1.020 |

- **The queue span** was 8995.8 s, or 2.4988 h. That is 1.060 × the projection of 2.3573 h, and well inside the gate's
  6.75 h.
- **Each level ran slower than its single dry sample.** K2, the shortest task, ran slowest relative to it.
- The gate re-projected before every launch, with the job's own ends joining the rates, and never stopped.

## The post (`lane/post-session1.txt`, post sha256 f97dfe43…)

- **The run.** One ssh session on login02 staged the post, checked its sha256 and ran it in the foreground. post_rc
  was 0, the /dev/shm copy was gone after the run, and ssh exited 0.
- **The tarball.** post-iter.tar.gz is 58,072 bytes, with sha256
  bd6f59c59e3e6b0e5fed564d838927ee81ce5b6602adc0345265c8902ac147dd. The same sha256 came from the .sha256 file beside
  it, from the remote sha256sum and from the local file.
  - tasks/ holds 44 .log and 44 .time files and nothing else, so there are no products in the tarball.
- **The extract.** Into an empty directory, with no absolute paths and no "..". SHA256SUMS then checked 225 of 225
  files.
  - `cluster/` is the extract. The 54 names git ignores carry ".txt" (`RENAMES.tsv`), and `lane/verify_receipts.py`
    re-checks them.
- **The final post.log and post.done** (the director's low of 2026-11-09). The tarball's post.log is written before
  the tar finishes, so it lacks the last lines. Both files were fetched separately, each with its sha256 matching on
  both sides, into `cluster-final/`:
  - post.log is a19b7fb3…, and ends "prr iter post rc=0";
  - post.done is 9a271f2a… and reads "0".
- **The dry run's final post.log and post.done** are added on the same terms in `../dry/cluster-final/`:
  - post.log is f8f0f970…. Its diff from `dry/cluster/post.log.txt` is only the 3 appended lines;
  - post.done is 9a271f2a….
  - The committed dry files are unchanged.

## login07, login17 and login19: unreached on two sweeps, closed

`cluster/logs/connect-iter.log.txt:7-10` records the second sweep:
- login07: "No route to host";
- login17: "No route to host";
- login19: "System is booting up … pam_nologin".

The first sweep, at the dry post, found the same (`../dry/lane/stale-sweep-summary.txt`). By the director's ruling of
2026-11-09 the three are **closed as unreached on two sweeps**, with no third try. Any copy left there is inert:
`prr_dry_submit.sh:33` bails while $OUT exists.

## Files

- `cluster/`: $OUT/post-iter as extracted, with the renames in `RENAMES.tsv`.
- `cluster-final/`: post.log and post.done, fetched after the post ended.
- `lane/launch-session.txt` and `lane/post-session1.txt`: the two ssh sessions.
- `lane/iter_times.py` and `lane/iter_times.json`: the measured times.
- `lane/verify_receipts.py`: re-checks `cluster/`.
- `lane/check-at-head.txt`: both scripts rerun in a clean clone at this receipt's head.
