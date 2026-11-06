REF-C2C1 step two, stage 2 (the units), part 2: the replicas, first submission: four TIMEOUT jobs (REF-C2C1-BINDING-2.md
ruling 2.2; code at M = 77d76cfc). Run by limitation-resolver: the connect on login03, 2026-11-06T06:38:09Z-06:39:04Z
(refc2c1_replicas_submit.sh, sha256 b9642fcf...), which wrote lanes.tsv (sha256 7b737d0c..., 350 units over 4 jobs x 4
lanes) and refc2c1_replicas_job.sbatch (sha256 4f38fc64...), each checked before sbatch, and submitted four 1-node jobs,
each with TimeLimit 02:30:00 as declared. Copied by O_NOATIME reads (survey/pull_tar.py) from
/pscratch/sd/j/josephrb/ref-c2c1-20261106/. Full sha256 of each file: SHA256SUMS.txt.

OUTCOME: INVALID (the director's ruling of 2026-11-06), not a control STOP. All four jobs were killed at their time limit:
  60890529 j0  TIMEOUT 0:0  06:53:02Z-09:23:29Z  02:30:27   73 of 86 units PASS
  60890530 j1  TIMEOUT 0:0  06:53:02Z-09:23:29Z  02:30:27   77 of 88 units PASS
  60890531 j2  TIMEOUT 0:0  07:07:09Z-09:37:39Z  02:30:30   77 of 88 units PASS
  60890532 j3  TIMEOUT 0:0  07:07:09Z-09:37:39Z  02:30:30   76 of 88 units PASS
Charge: 36114 s = 10.0317 node-h; REF-C2C1 total 0.3839 + 10.0317 = 10.4156 of the 12.5 cap. No job wrote its
REPLICAS-DONE-j<J>. The 303 units with PASS markers stand (the ruling): each passed its own controls. The 47 missing units
are all c2_replica and all in a lane 3; their list is in the REPLICAS-TIMEOUT records.

THE CAUSE (survey/): memory, not CPU or unit speed. The job allocation on regular_milan_ss11 is mem=487802M (AllocTRES; the
partition's MaxMemPerNode=487802; node RealMemory 515100, MemSpecLimit 27298). Four steps at `srun --exclusive -n1 -c 64
--mem=120G` need 491520M, which doesn't fit. In each job, lane 3's srun logged "step creation temporarily disabled
(Requested nodes are busy)" (lanes/j<J>-lane3.log, first lines) and started only when another lane ended. Lanes 0-2 ran
1:30:41-1:34:39 (GNU time, Exit status 0). In j0, lane 3's first unit (c1_replica_b4.done) is stamped 08:38:56Z, about 11 min
after lanes 0-2 ended at 08:27:22Z-08:27:55Z. Lane 3 then had about 56 min (j2, j3: about the same) and finished 10-11 units.
Unit times matched the centrals: c2_replica mean 177 s (175-183, n=253), c1_replica mean 698 s (679-717, n=50). The
centrals job ran three steps (360G), which fit, so these were the first four-step jobs.
Peak lane RSS was 16.6 GB (GNU time, lanes 0-2).

THE RECORD (timeout-record/, refc2c1_timeout_record_login.sh, sha256 015f6680..., on login27 at 09:44:51Z-09:44:54Z,
rc 0). The jobs were killed before their own after-stat and porcelain, so these were taken after the fact:
- the four jobs are out of the queue and sacct reads TIMEOUT (sacct.txt);
- lanes.tsv is the reviewed one; every unit's .done was read by O_NOATIME; no missing unit left any file under units/
  (no half-written unit); each tmp-replicas-j<J> is empty;
- the 303 COV2D inputs, stat'd (no read) at 09:44:52Z (watch/watch-after-login.txt), are byte-identical to each job's own
  before-file (watch/j<J>-watch-before.txt): no atime moved;
- $O/deploy-replicas porcelain --ignored: 0 lines;
- REPLICAS-TIMEOUT-j<J>, one per job: {"job", "index", "state": "TIMEOUT", "units_declared", "pass_markers",
  "pass_units", "missing_units", "watch_moved": 0, "porcelain_after": 0, "recorded"}. The pass_units sets are disjoint,
  total 303, and with the 47 missing make the 350 of lanes.tsv. The 3b read gate unions these sets with the completion
  job's record (the director's ruling).
- THE FENCE, recorded (the director's ruling: guarded readers record, not refuse): each job's start line holds the full
  squeue; at 09:44:51Z cov2d-G18_Ua and cov2d-G18_Ub were RUNNING and 18 cov2d-* jobs PENDING. This record read only the
  lane's own files and stat'd the COV2D inputs.

Files: the connect's copy, log and done marker; clone.log; jobs.tsv; submit-j<J>.out; the four batch .out files; the job
script; lanes.tsv and the watch list; lanes/ (each lane's log and GNU time; lane 3's time files are empty, since the lane
was killed); watch/; timeout-record/; units/ (the 303 done-markers; the products stay on pscratch, each one's sha256 in
its marker); survey/ (the two read-only diagnosis scripts and their outputs, and the copy script).
