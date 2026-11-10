# FD-PRR prr_ibu attempt 2: the record of a refusal (job 61043652, FAILED)

The valid-region lane, 2026-11-09, under FD-PRR BINDING 1 ruling 7 and addendums A1 and A3. The code was at M_A3 =
06657cff7a6ed6c9832fe27957899125e6cac4ad. A3's TimeLimit fix held: the job passed its own checks and started
prr_ibu.py. prr_ibu.py then refused its first plain read of $OUT/stage.json inside REF-G1's read guard, before any
unfold. This is a records-only receipt. By the director's ruling of 2026-11-09 the post was not run, so post-ibu* stays
free. Nothing was repaired or resubmitted.
<!-- absence-ok: the lane's own action, by the director's ruling; the post's paths are shown absent in lane/remote-listing.txt -->

CITABLE FOR: job 61043652 ended FAILED 1:0 after 132 s; the refusal's text; its cause in prr_ibu.py @ 06657cff; that
A3's TimeLimit check passed on the cluster; the charge, 0.0367 node-h, with the study at 7.4267 of the 27.0 cap; what
the job wrote (log-ibu/ with FAILED, an empty route2/); the connect's checks.
NOT CITABLE FOR: any route-2 result (C-IBU, R-ID, R-SUP, PR-2) or any prior-retention reading. Route 2 never unfolded.

## The refusal

- **Slurm.** `cluster/sacct.txt:1-3`:
  - prr_ibu is FAILED, exit 1:0, Elapsed 00:02:12 (132 s), 1 node, 256 CPUs, from 2026-11-09T10:09:24 to 10:11:36
    (Pacific), TimeLimit 00:30:00;
  - the .batch step is FAILED 1:0;
  - the .extern step is COMPLETED.
- **The job's output.** `cluster/logs/prr_ibu_61043652.out.txt`, in full:

  ```
  [prr] mode=ibu job=61043652 host=nid004495 pin=06657cff7a6ed6c9832fe27957899125e6cac4ad start=2026-11-09T18:11:23Z
  [prr] STOP: route 2 failed (rc=2)
  ```

  - Line 1 is `sbatch_prr.sh:105` @ 06657cff. The job script prints it only after its checks:
    - the name;
    - the TimeLimit (`:46-74`, A3's code);
    - the dry run's DONE;
    - the environment (`:95-96`);
    - the staged copies (`:101-102`, verify-stage, whose log is empty on success).
  - Line 2 is `:109`, the job script's report of prr_ibu.py's rc.
- **prr_ibu.py's own message.** `cluster/log-ibu/ibu.log.txt`, its one line:
  `refusing: a plain read of /pscratch/sd/j/josephrb/fd-prr-20261108/stage.json: files under ['/pscratch', '/global/cfs'] are read only through O_NOATIME`.
- **What the job wrote.** It was read-only at 18:23:52Z on login36 (`lane/remote-listing.txt`):
  - $OUT/log-ibu/ holds env.log, FAILED ("rc=2"), ibu.log, verify-stage.log (0 bytes) and an empty tasks/;
  - $OUT/route2/ exists and is empty;
  - there is no DONE and no SHA256SUMS;
  - post-ibu and post-ibu.tar.gz are absent.
- **The environment.** `cluster/log-ibu/env.log.txt` holds the same two missing optional setup.sh lines as cap's and
  misc's, here with deploy-ibu-2.

## The cause (prr_ibu.py @ 06657cff, M_A3)

- **The guard.** `main()` reads `a.stage` plainly at :337 to take its `dest`. At :339 it enters
  `ref_g1.read_guards(ref_g1.PROTECTED, (REPO, a.out, stage_dir, a.queue_dir), root=False)` and calls `run()` inside it.
  - PROTECTED is (/pscratch, /global/cfs) (`nd-unfolding/ref_g1/ref_g1.py:133` @ 06657cff).
  - Under it, a plain Python read is allowed only below the repository, $OUT/route2, the stage dest and $OUT/queues
    (`ref_g1.py:175-190`, with the audit hook's refusal at `:138-153`).
  - The stage dest is $OUT/stage (`../../dry/cluster/stage.json`, its "dest").
- **The read.** `run()` reads the stage record again at :274, `stage_rec = json.loads(stage_json.read_text())`.
  $OUT/stage.json is under /pscratch and under none of the four allowed roots. The audit hook therefore refused it,
  and `main()` returned 2 (:341-343).
- **Why the other jobs were unaffected.** dry, iter, cap and misc read stage.json through `prr_probe.py:725` @
  06657cff, where no read guard is active.
- **Why no test caught it.** Route2Run's only run test (`test_prr.py:790-809` @ 06657cff) writes stage.json in a
  tempfile directory. That directory is under neither PROTECTED root, so the guard never protects any of its paths.
- **Why the connect passed.** The connect reads stage.json with sha256sum. It does not run prr_ibu.py.
- **The fix.** The director ruled for addendum A4 (2026-11-09):
  - `main()` reads the stage record once, before the guard, and passes it to `run()`;
  - a REQUIRED Route2Run test runs with ref_g1.PROTECTED patched over its temp root;
  - a mutant restores the in-guard read;
  - a static trace lists every read and write on the run path.
  Attempt 3 runs from A4's merge commit.

## A3's fix on the cluster

The job passed `sbatch_prr.sh:46-74` @ 06657cff with its real squeue limit. The connect's squeue line shows that limit as
"30:00" (`cluster/logs/connect-ibu-2.log.txt:49`: `61043652 prr_ibu PENDING 0:00 30:00 …`). Attempt 1 refused this
same form. This time the job went on to line 105.

## The charge

`cluster/sacct.txt:4-9` lists every prr_* job, each on 1 node:

| job | id | ElapsedRaw (s) |
|---|---|---|
| prr_dry | 61022062 | 3648 |
| prr_iter | 61024185 | 9038 |
| prr_cap | 61028298 | 5220 |
| prr_misc | 61030122 | 8657 |
| prr_ibu, attempt 1 | 61035510 | 41 |
| prr_ibu, attempt 2 | 61043652 | 132 |

That totals 26,736 s, or 7.4267 node-h, against the cap of 27.0. This job's share is 0.0367 node-h.

## The connect (`cluster/logs/connect-ibu-2.log.txt`, connect sha256 c9246a83…)

- **Before it.** iris on login35 at 17:57:45Z showed m3246 at 18,361.5 charged of 20,000.0 (`lane/iris-before.txt`).
  - squeue --me listed two ll5d_gate jobs of another lane.
  - route2, log-ibu and every attempt-2 connect path were absent. Attempt 1's deploy-ibu and ibu.jobid were present.
- **Launch.** One ssh session on login23 staged the connect, checked its sha256 and launched it with nohup
  (`lane/launch-session.txt`). ssh exited 0, read unpiped.
- **Other families** (lines 7-9). The two ll5d jobs were listed, not refused. The echo reads "outside $OUT and the
  deploy", attempt 1's slip corrected.
- **Balance and charge** (lines 12-19):
  - the balance was 1638.5 node-h, half 819.2;
  - all five sacct pins matched, among them `61035510|prr_ibu|FAILED|41|1`;
  - 7.3900 + 0.5 = 7.8900, within 27.0.
- **Deploy and pins** (lines 20-37):
  - a fresh clone at M_A3, with porcelain 0 before and after (line 55);
  - the six FD-PRR files matched, as did the declaration, A1, A3 (48641cf9…) and BINDING-1.md at origin/main cd8e16fe
    (b691d956…);
  - the four queues, stage.json and log-dry/DONE matched;
  - there were 20 B0 lines.
- **Limit and submission** (lines 41-48):
  - `prr_probe.py limit ibu` gave 0:30:00;
  - the job was submitted as 61043652, with its id written to logs/ibu-2.jobid;
  - scontrol's TimeLimit read 00:30:00;
  - connect-ibu-2.done reads 0.

## How the files were fetched

- **The copies.** Read-only, each by `cat` over ssh into an empty directory.
  - `lane/remote-sha256.txt` gives each file's sha256 on the cluster (login36).
  - Every fetched file has the same sha256, 8 of 8.
  - verify-stage.log is empty (e3b0c442…).
- **Renames.** The five names git ignores carry ".txt" (`RENAMES.tsv`). Their contents are unchanged.
- **Attempt 1's files** stay where they are (`../attempt1/`). The attempt-2 connect wrote only names with "ibu-2"; the
  job wrote prr_ibu_61043652.out, log-ibu/ and route2/.

## What comes next (the director's ruling, recorded here; the move is done since: see the addendum below)

- **The move.** After this record merges, one ssh session moves $OUT/log-ibu and $OUT/route2 into $OUT/ibu-attempt2/,
  with a listing and the sha256 of every moved file before and after. That output is added to this record as a short
  addendum.
- **Attempt 3** writes $OUT/log-ibu and $OUT/route2 fresh, so prr_read is unchanged. It uses TAG=ibu-3 on the connect
  side, pins both earlier attempts in sacct and runs from A4's merge commit. Its post reads logs/ibu-3.jobid.

## Files

- `cluster/logs/`: prr_ibu_61043652.out, connect-ibu-2.log, connect-ibu-2.done and ibu-2.jobid.
- `cluster/log-ibu/`: env.log, FAILED, ibu.log and verify-stage.log. tasks/ was empty, and $OUT/route2/ was empty.
- `cluster/sacct.txt`: the job's sacct rows and the study's prr_* rows.
- `lane/iris-before.txt`, `lane/launch-session.txt`, `lane/remote-listing.txt` (the listing, the sha256, the absent
  paths, squeue and sacct, in one session) and `lane/remote-sha256.txt`.

## Addendum (2026-11-09): the move

The director's go of 2026-11-09 covered `prr_move_attempt2.sh` at sha256
518fc8b85110035d5df7cd053c551849d98b0361720fe21a7baf22ca81e261a7 (`move/prr_move_attempt2.sh`), after this record had
merged (ef9411a3). The session ran in the foreground. ssh's rc was read unpiped: 0.

- **The session** (`move/move-session.txt`, sha256 dbf7b4f18cd990cb99dcaeacfdfe9ba968c1bf7368fe27f40db67a91b48e0870),
  on login08 at 2026-11-09T21:20:42Z. It was one ssh session:
  - The script went to /dev/shm, was checked at its sha256, and was removed at the end.
  - It printed iris's m3246 row and `squeue --me` (`move/move-session.txt:3-7`). The two jobs listed are
    ll5d_gate_AR23 61040235 and ll5d_gate_G18 61040163, and neither is a prr_* job.
- **The script's checks:** log-ibu and route2 were present and ibu-attempt2 absent; no prr_* job in squeue; the four
  log-ibu files were at this record's sha256 (`lane/remote-sha256.txt`), with 4 OK lines (`:10-13`); route2 and
  log-ibu held 4 files in all (the script stops otherwise).
- **The move:** `mkdir $OUT/ibu-attempt2`, then `mv` of `log-ibu` and `route2` into it.
- **Before and after:** the listings and the four sha256 are identical (`move/move-session.txt:14-37`):
  - env.log 986cd8be…;
  - FAILED 9830ce9d…;
  - ibu.log 6c0c07e7…;
  - verify-stage.log e3b0c442… (empty);
  - `log-ibu/tasks/` and `route2/` are empty directories.
- **After the move**, `$OUT/log-ibu` and `$OUT/route2` are gone: `ls -d` printed "No such file or directory" for both
  (`:38-39`). The script printed "moved rc=0" and the session "script rc=0" (`:40-41`).
  <!-- absence-ok: shown by the session's own ls -d of both paths, move/move-session.txt:38-39 -->
- **Attempt 3** therefore writes `$OUT/log-ibu` and `$OUT/route2` fresh. Its connect (FD-PRR-ADDENDUM-A4 §10)
  requires `$OUT/ibu-attempt2/log-ibu` and `$OUT/ibu-attempt2/route2`.

CITABLE FOR: attempt 2's four files and two empty directories are at `$OUT/ibu-attempt2/`, unchanged by sha256; the two
paths attempt 3 writes are free.
NOT CITABLE FOR: anything about the staging step or attempt 3, neither of which has run.
