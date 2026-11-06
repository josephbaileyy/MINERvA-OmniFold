REF-C2C1 step two, the replicas' completion, attempt 1: job 60897523, stopped by its own concurrency guard on a correct run
(REF-C2C1-BINDING-2.md ruling 2.2; the director's timeout ruling of 2026-11-06; code at M = 77d76cfc). Run by
limitation-resolver on the GO of coverage-5b-audit and the director. The connect ran on login04, 10:00:39Z-10:01:29Z, rc 0
(refc2c1_completion_submit.sh, sha256 cf4eac53...; connect.log). It embedded refc2c1_completion_job.sbatch (bee44fae...) and
lanes-j4.tsv (b6d66658..., the 47 c2_replica units without a PASS marker in REPLICAS-TIMEOUT-j0..3). Parsed TimeLimit 01:30:00
as declared; Partition regular_milan_ss11. Copied by O_NOATIME reads (survey/pull1_tar.py) from
/pscratch/sd/j/josephrb/ref-c2c1-20261106/ (logs-completion/, the job script, REPLICAS-DONE-j4). Full sha256 of each file:
SHA256SUMS.txt.

OUTCOME: INVALID, from a connect-level guard defect (the director's ruling of 2026-11-06). It is not a control STOP, and the 8
bound blobs are untouched. The job ended FAILED 1:0 after 00:01:48, at 12:18:49Z-12:20:37Z, costing 0.0300 node-h. That brings
REF-C2C1 to 10.4456 of the 12.5 cap. No unit wrote a .done, and no result exists to read.
- The in-job fit passed: AllocTRES mem=487802 ≥ 4 x 114688 = 458752 MB and cpu=256 ≥ 256. SLURM_MEM_PER_NODE was empty in
  this job, so the AllocTRES source was the one that read.
- All four lane steps were running together. sacct.txt (times in the cluster's local zone, UTC-8) shows steps .0-.3 (r4-l2,
  r4-l0, r4-l3, r4-l1) with Start 04:19:03 = 12:19:03Z, cpu=64, mem=112G each, ending "CANCELLED by 0" at 12:20:34Z. Each
  j4-lane<l>.log shows the unit driver reading its inputs, then "task 0: Killed".
- THE DEFECT: at +90 s (12:20:33Z) the guard counted "0 of 4 lane steps created". It counted with
  `squeue -s -j $SLURM_JOB_ID`, which listed only .batch and .extern; it then killed the srun clients (rcs 137 x 4). On
  Perlmutter `squeue -s` doesn't list srun steps at all. survey/squeue-steps-evidence.txt is a read-only check at 12:23:04Z on
  the lane's running cov2d-AR23_L (60895983): sacct shows steps .2 and .3 RUNNING, `squeue -s -j`, `squeue -s -u` and
  `squeue --steps` list only batch/extern or nothing, and `scontrol show step` and `sstat -a` list .2 and .3. The guard's
  preflight tested its format on live jobs but never confirmed that a known-running step appeared, so it could not pass.
- REPLICAS-DONE-j4 (sha256 7016fdef7b4810b55b3c9dc2d70d05934dc64526d47add3fac661b4d8ac54ab1 at the pull; this copy is the
  file in this directory): units 47, pass_markers 0, rcs "137 137 137 137", watch_moved 0, porcelain_after 0,
  concurrent 0, unit_list (the 47). The 3b read gate (b162ba9a) refuses it on pass_markers, rcs and concurrent.
- No leftovers (survey/leftovers-1222Z.txt, stat only, at 12:22:38Z): no file under units/ for any of the 47 names (units/
  still holds 918 entries = 306 names x 3), and tmp-replicas-j4 is empty.
- The COV2D inputs: j4-watch-after.txt is byte-identical to j4-watch-before.txt (303 paths), so no atime moved. Deploy
  porcelain --ignored is 0 before and after. The fence, recorded: the job's start line holds the full squeue.
- Next (the ruling and its addendum): after this receipt merges, rename every attempt-1 path that exists among
  $O/REPLICAS-DONE-j4, deploy-completion, libcheck-completion, logs-completion and tmp-replicas-j4 to
  <name>.attempt-1-60897523, with no deletions. The B9-form ledger row (ls and sha256, or a file manifest, before and after;
  the mv lines; the time) is committed here as a follow-up. logs-completion's contents are already in this directory.
  The concurrency guard is rebuilt to count from `scontrol show step`, tested both ways on a live job, with the parsed
  output committed as a fixture. coverage-5b-audit gives a delta audit, then attempt 2 runs.

Files: the connect's copy, log and done marker; clone.log; jobs.tsv; submit-j4.out; the batch .out; the job script;
lanes-j4.tsv and the watch list; j4-lane<l>.log and .time (the .time files are empty, since the steps were killed); the two
watch snapshots; REPLICAS-DONE-j4; sacct.txt; survey/ (the copy script, the squeue evidence, the leftover listing, and the
audited diffs of the completion job, the submit script and the read gate against their predecessors).
