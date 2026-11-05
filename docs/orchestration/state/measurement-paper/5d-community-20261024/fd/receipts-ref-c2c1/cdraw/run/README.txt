REF-C2C1 C-DRAW, the run (the scripts are in ../, committed in #779 before they ran). Copied by limitation-resolver
on 2026-11-05 with dd iflag=noatime from /pscratch/sd/j/josephrb/ref-c2c1-20261105/cdraw/ and its logs/. Full sha256 of
each file: SHA256SUMS.txt.

RESULT: C-DRAW PASS. The regenerated S1_001 (RE-2's driver at dbdad2f9, S1_001's recorded argv) has a p1Streams record
equal to the recorded product's on every field, so Q_R's existing 300 replicas are reused (REF-C2C1-DECLARATION.md
§1.3); no 200 new replicas are run.

  step A (dtn01, 09:56:21-09:57:04Z)   stage.json 61174290... PASS: the CFS $CV staged and re-read at 43f8cc16, the
                                       recorded S1_001 copied at 2ea9b7d2, $MC at d40aea69. mc_cfs_candidates.txt: one
                                       CFS copy of $MC, equal to d40aea69 (minerva-shutdown-stage/fig_products/...).
  step B (login31, 09:59:29-10:00:56Z) connect.log: the stage record and both copies re-verified; the deploy at
                                       dbdad2f9 clean with its 3 blobs; the comparison and job scripts equal to the
                                       committed ones; "scontrol TimeLimit=00:45:00 (declared 00:45:00)".
  job 60847127                         sacct-60847127.txt: COMPLETED 0:0, 644 s on 1 node, 0.1789 node-h (12.5 cap).
                                       fd_cdraw_60847127.out: driver rc 0, the comparison's field-by-field printout,
                                       "C-DRAW PASS", the staged copy deleted. compare.log, cdraw.json (e3f30a26...),
                                       S1_001.log (the driver's log), deletions.tsv (the deletion's ledger row).

NOTES (reported to the director with the result):
- The p1Streams record has 7 fields; cdraw_compare.py's docstring names 5 (streams and unit_factors are the other two).
  The rule compares the whole record (new == rec), so all 7 were compared and equal.
- The job's output shows two warnings from setup_salloc_env.sh, lines 18 and 21: unbinned_unfolding/build/setup.sh
  and MINERvA101/opt/bin/setup.sh are absent from a fresh clone. The driver ran (rc 0); the compared draws are made
  before any library call or fit.
