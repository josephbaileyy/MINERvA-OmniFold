REF-C2C1 step two, stage 2 (the units), part 2: the replicas' completion, attempt 2, job 60901504 (REF-C2C1-BINDING-2.md
ruling 2.2; the director's rulings of 2026-11-06 on the four TIMEOUT jobs (../timeout/) and on attempt 1
(../completion-attempt-1/); code at M = 77d76cfc). Run by limitation-resolver on the GO of coverage-5b-audit (the guard,
../completion-attempt-2-guard/, #834; the rename ledger, #835) and the director. Copied by O_NOATIME reads
(launcher/pull2_tar.py) from /pscratch/sd/j/josephrb/ref-c2c1-20261106/. Full sha256 of each file: SHA256SUMS.txt.

OUTCOME: PASS. REPLICAS-DONE-j4 (sha256 5680f1f9d0e37602e5627fbb6eefd014ce18a9b5e96806d8e3ecf352e4b918e5): units 47,
pass_markers 47, rcs "0 0 0 0", watch_moved 0, porcelain_after 0, concurrent 1, unit_list (the 47 of lanes-j4.tsv).
- THE LAUNCH, from main's bytes (launcher/). launch_from_main.sh, sha256 40126474a54e74aec5973df976778c9f469a8cc3c8690ff7e128b34c6b348616,
  is a wrapper OUTSIDE the audited set: it only fetches main's bytes and compares them. I tightened it after the audit:
  a login-side sha mismatch now exits 5, and ssh's rc is read from the ssh command itself. Its output (launch.out; the
  check-only run before it is check.out) records both values of each comparison, each refusing on mismatch. On main
  0a42b576 the submit is c41ffb61 (audited c41ffb61), the job c82055f6 (audited c82055f6), the submit's embedded JOB_SHA is
  c82055f6, and the rename ledger reads rc=0. login27 re-hashed main's bytes in /dev/shm to c41ffb61, so it launched;
  ssh rc 0 at 12:49:15Z.
- THE CONNECT (refc2c1_completion_submit.sh c41ffb61; connect.log, login27, 12:49:15Z-12:50:02Z, rc 0):
  - CENTRALS-DONE accepted;
  - the four REPLICAS-TIMEOUT on main 0a42b576 equal to pscratch;
  - HEAD M with porcelain 0, 8 blobs and 0 mismatches; libRooUnfold.so 0b34e1e3;
  - the unit set: 350 declared; the TIMEOUT PASS sets 73/77/77/76 are disjoint with union 303; lanes-j4 (b6d66658) is the
    47 that remain, with no files under units/;
  - the fit: 4 x 114688 = 458752 MB ≤ MaxMemPerNode 487802, and 256 ≤ 256 CPUs; the iris half-balance check;
  - the job script c82055f6, checked; TimeLimit=01:30:00 as declared, Partition regular_milan_ss11.
- THE JOB, nid004930, COMPLETED 0:0, 12:54:43Z-13:31:30Z (sacct.txt, in the cluster's local zone, UTC-8):
  - the in-job fit: AllocTRES mem=487802 and cpu=256; SLURM_MEM_PER_NODE was empty again, and the AllocTRES source read it.
  - THE GUARD: at +90 s (12:56:27Z) it read 4 of 4 lane steps RUNNING from `scontrol -o show step` (j4-steps-at-90s.txt:
    60901504.0-.3 = r4-l0, r4-l1, r4-l3, r4-l2). The sstat -a cross-check listed 4. It was silent, as intended. sacct shows
    all four steps starting at 12:54:57Z.
  - the lanes: rcs 0 0 0 0. GNU time 36:11, 36:30, 35:54 and 32:56 (lanes 0-3), MaxRSS 10.0-10.3 GB, Exit status 0.
    The 47 c2_replica units ran 178.2 s mean (175.3-188.9 s), matching the replicas' 177 s.
  - 47 of 47 PASS markers (units/, the 47 done-markers). The products stay on pscratch, each one's sha256 in its marker.
  - The COV2D inputs: j4-watch-after.txt is byte-identical to j4-watch-before.txt (303 paths), so no atime moved. Deploy
    porcelain --ignored is 0 before and after. THE FENCE, recorded: the connect's squeue and the job's start line.
- THE CHARGE: Elapsed 00:36:47 = 2207 s = 0.6131 node-h. REF-C2C1 total (sacct actuals): C-DRAW 0.1789, the centrals
  0.2050, the TIMEOUT jobs 10.0317, attempt 1 0.0300, this job 0.6131 = 11.0587 of the 12.5 cap.
  - The SPENT DISCREPANCY: the audited submit's fixed SPENT=10.4156 predates attempt 1 and omits its 0.0300. The true
    projection at submission was 10.4456 + 1.5 = 11.9456 ≤ 12.5, so its price check could not have passed wrongly.
- THE 3b READ GATE (refc2c1_read_login.sh b162ba9a), its python dry-run locally (O_NOATIME stubbed) on these records,
  the four REPLICAS-TIMEOUT and all 350 done-markers: records failing their fields [], unit sets [73, 77, 77, 76, 47],
  disjoint, union 350, equal to lanes.tsv's 350, none without a PASS marker; rc 0. The read itself waits for this receipt
  on main, since its gate also requires REPLICAS-DONE-j4 here to equal the pscratch record.

Files: the connect's copy, log and done marker; clone.log; jobs.tsv; submit-j4.out; the batch .out; the job script;
lanes-j4.tsv and the watch list; j4-steps-at-90s.txt; the two watch snapshots; REPLICAS-DONE-j4; sacct.txt; lanes/ (each
lane's log and GNU time); units/ (the 47 done-markers); launcher/ (the wrapper, its outputs, the copy script).
