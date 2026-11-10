# FD-PRR prr_ibu attempt 1: the record of a refusal (job 61035510, FAILED)

The valid-region lane, 2026-11-09, under FD-PRR BINDING 1 ruling 7 and addendum A1 (code at M_A1 =
6727020a7c58b00dd00806151c627c8a24f72402). Route 2's job refused at its own TimeLimit check 41 s after it started,
before it wrote anything. This is a records-only receipt: by the director's ruling of 2026-11-09 the post was not run,
so post-ibu* stays free for attempt 2. Nothing was repaired or resubmitted.
<!-- absence-ok: the lane's own action, by the director's ruling; the post's paths are shown absent below -->

CITABLE FOR: job 61035510 ended FAILED 2:0 after 41 s; the refusal's text; its cause in sbatch_prr.sh @ 6727020a; the
charge, 0.0114 node-h, with the study at 7.3900 of the 27.0 cap; that $OUT/log-ibu and $OUT/route2 were never created;
the connect's checks.
NOT CITABLE FOR: any route-2 result (C-IBU, R-ID, R-SUP, PR-2) or any prior-retention reading. Route 2 never ran.

## The refusal

- **Slurm.** `cluster/sacct.txt:2`: prr_ibu, FAILED, exit 2:0, Elapsed 00:00:41 (41 s), 1 node, 256 CPUs, from
  2026-11-09T06:08:43 to 06:09:24 (Pacific), TimeLimit 00:30:00. The .batch step is FAILED 2:0 (line 3).
- **The job's output.** `cluster/logs/prr_ibu_61035510.out.txt`, in full:

  ```
  Traceback (most recent call last):
    File "<stdin>", line 6, in <module>
    File "<stdin>", line 4, in sec
  ValueError: not enough values to unpack (expected 3, got 2)
  [prr] refusing: Slurm TimeLimit 30:00 exceeds the declared 0:30:00
  ```

- **Nothing was written.** Read-only at 2026-11-09T14:11Z (`lane/absent-check.txt`): $OUT/log-ibu, $OUT/route2,
  $OUT/post-ibu and $OUT/post-ibu.tar.gz do not exist, and squeue --me is empty. The only ibu files are the connect's
  10 under $OUT/logs and the job's .out. The search was `ls -d $OUT/log-ibu $OUT/route2 $OUT/post-ibu
  $OUT/post-ibu.tar.gz; ls $OUT/logs | grep ibu; squeue --me` on login35, and its output is `lane/absent-check.txt`.
  <!-- absence-ok: a cluster-state record, not a result; no git sha exists for it; its search and raw output are in lane/absent-check.txt -->

## The cause (sbatch_prr.sh @ 6727020a)

- **The read.** Line 39 takes the job's limit from `squeue -h -j "$SLURM_JOB_ID" -o %l`. For a limit under one hour,
  squeue prints it as M:SS. The connect's own squeue line shows this job's limit as "30:00"
  (`cluster/logs/connect-ibu.log.txt:44`: `61035510 prr_ibu PENDING 0:00 30:00 …`).
- **The parse.** sec() at lines 48-50 splits on ":" into exactly three fields, `h, m, s = (int(x) for x in
  t.split(":"))`. On "30:00" it raises ValueError.
- **The message.** Line 46's `|| { echo "[prr] refusing: Slurm TimeLimit $TL exceeds the declared $LIMIT"; exit 2; }`
  reports any non-zero exit of the check as "exceeds". So the parse error reads as a false limit breach: 30:00 does not
  exceed 0:30:00.
- **Why the connect passed.** It reads scontrol (`connect-ibu.log.txt:43`, TimeLimit=00:30:00), which always prints
  [D-]HH:MM:SS.
- **Why no test caught it.** Outside Slurm the job takes TL from PRR_TIMELIMIT, which defaults to LIMIT, prr_probe's
  "0:30:00" (line 41), already in H:MM:SS form. test_prr.py's TimeLimit cases ("5:16:00", "1-00:00:00", "4:00:00",
  test_prr.py:1337-1341 @ 6727020a) are all in H:MM:SS or D-HH:MM:SS form.
- **Why dry, iter, cap and misc were unaffected.** Their limits (5:15:00, 7:30:00, 6:30:00, 7:15:00) are all at least
  one hour, so squeue prints them in H:MM:SS form. All four completed with DONE (`../../dry/`, `../../iter/`,
  `../../cap/`, `../../misc/`).
- **The fix.** The director ruled for a fix to sec() in its own addendum, A3 (2026-11-09). Attempt 2 runs from A3's
  merge commit.

## The charge

`cluster/sacct.txt:6-10` lists every prr_* job: prr_dry 3648 s, prr_iter 9038 s, prr_cap 5220 s, prr_misc 8657 s and
prr_ibu 41 s, each on 1 node. That is 26,604 s, or 7.3900 node-h, against the cap of 27.0. This job's share is 0.0114.

## The connect (`cluster/logs/connect-ibu.log.txt`, connect sha256 23a4f44f…)

- **Before it.** iris on login36 at 14:05:09Z: m3246 18,356.2 charged of 20,000.0; $OUT/route2 and $OUT/log-ibu absent
  (`lane/iris-before.txt`).
- **Launch.** One ssh session on login13 staged the connect, checked its sha256 and launched it with nohup
  (`lane/launch-session.txt`). ssh exited 0, read unpiped.
- **Balance and charge** (lines 9 and 11-15): balance 1643.8 node-h; prr_dry, prr_iter, prr_cap and prr_misc as
  recorded; 7.3786 + 0.5 = 7.8786, within 27.0.
- **Deploy and pins** (lines 16-31): a fresh clone at M_A1, porcelain 0; the six FD-PRR files, the declaration, A1 and
  BINDING-1.md at origin/main 5898c791 (04686d70) matched. The four queues, stage.json and log-dry/DONE matched the dry
  run's digests.
- **B0 lines** (line 32): 20, one per route-2 experiment.
- **Limit and submission** (lines 36-43): `prr_probe.py limit ibu` gave 0:30:00. Submitted as 61035510, and scontrol's
  TimeLimit read 00:30:00. Porcelain was 0 after (line 50), and connect-ibu.done reads 0.
- **An echo slip.** Line 5 prints "other lanes' families (listed, not refused; this job reads nothing outside $OUT)",
  carried over from the cap connect. For ibu that should read "outside $OUT and the deploy", as the connect's header
  comment says: prr_ibu.py also reads REF-G1's readout and config in the deploy. It is an echo only, with no effect on
  any check. Attempt 2's connect corrects it.

## How the files were fetched

- **The copies.** Read-only, each by `cat` over ssh into an empty directory. `lane/remote-sha256.txt` gives each
  file's sha256 on the cluster (login35), and every committed file has the same sha256.
- **Renames.** The two names git ignores carry ".txt" (`RENAMES.tsv`), and their contents are unchanged.

## Files

- `cluster/logs/`: prr_ibu_61035510.out, connect-ibu.log, connect-ibu.done and ibu.jobid.
- `cluster/sacct.txt`: the job's sacct rows and the study's prr_* rows.
- `lane/iris-before.txt`, `lane/launch-session.txt`, `lane/remote-sha256.txt` and `lane/absent-check.txt`.
