REF-C2C1 step two, stage 2 (the units), part 1: the three centrals, timed (REF-C2C1-BINDING-2.md ruling 2.2; code at
M = 77d76cfc). Run by limitation-resolver under the binding's fixed conditional sequence: the connect on login27,
2026-11-06T06:04:54Z-06:05:43Z (refc2c1_centrals_submit.sh, sha256 5b75dd03...d6fd), which submitted job 60889566
(refc2c1_centrals_job.sbatch, sha256 de0b6321..., checked by the connect before sbatch; TimeLimit 01:00:00 as
declared), COMPLETED 0:0 on nid005933, 06:18:54Z-06:31:12Z, 00:12:18 (0.2050 node-h; REF-C2C1 total 0.3839 of the
12.5 cap). Copied with dd iflag=noatime from /pscratch/sd/j/josephrb/ref-c2c1-20261106/ (logs-units/, units/*.done,
CENTRALS-DONE, the job script). Full sha256 of each file: SHA256SUMS.txt. The products (.npz, .root) stay on pscratch;
each one's sha256 is in its done-marker.

OUTCOME: PASS. CENTRALS-DONE: {"job": "60889566", "rcs": "0 0 0", "pass_markers": 3, "porcelain_after": 0}.
- The gate: stage 1's stage.json on origin/main 99b32ada hashes to 559da9e8..., equal to the pscratch record; both
  staged copies present. A fresh clean clone at M, porcelain --ignored 0 before and after; the binding's 8 blobs.
- libRooUnfold.so (config.json inputs.roounfold_lib): the source read by O_NOATIME and the copy in libcheck/ both
  hash to 0b34e1e39102b0dddc5923dad7f69e59c70cd6a2fcbcef07728b72cf2933fefd, config.json's full sha256 (F2's interim).
  The c2 units dlopen the configured path itself (a C-level read; not a declared or COV2D input).
- Each unit as `srun --exclusive -n1 -c 64 --mem=120G` at OMP/MKL/OPENBLAS 64/1/1 (NUMEXPR 1); each unit's own gate
  admitted it (affinity exactly 64, thread environment equal to config.json e_r):
  er          565.1 s (srun step 00:09:56, MaxRSS 14.1 GB); er.done PASS (npz 355a57cd, root 3136efed)
  c2_central  186.3 s (step 00:03:37, MaxRSS 9.8 GB); controls C-FILL, C-SIM, C-ROO all pass; c2_central.done PASS
              (npz 929d0e78, root 595ce19f)
  c1_central  691.5 s (step 00:12:02, MaxRSS 14.8 GB); c1_central.done PASS (npz 62e29ff3, root fd120d1d)
- The replicas' projection from these step times, accepted by the director: 300 c2 x 217 s and 50 c1 x 722 s at 4
  units per node = 7.03 node-h, about 7.4 of 12.5 with the spent 0.38; 4 jobs x 4 lanes at --time=02:30:00 (worst
  case 10.38).
- THE FENCE: cov2d-pseudo_AR23 (job 60889690) started at 06:19:09Z, three seconds after these units' srun steps
  (06:19:06Z), and overlapped them for about 12 minutes; the job's start line recorded it PENDING (06:18:59Z); the
  connect's refusal check at 06:04:54Z had been clear. Evidence that the overlap touched no COV2D input, by stat (no
  read) at 06:32:41Z (cov2d-watch-0632Z.txt): the 303 COV2D inputs (the flux constraint, ER/xsec.root, 300
  S1_*/xsec.root, the publication's covariance) are byte-identical to attempt 4's after-snapshot at 02:16:03Z
  (cov2d-watch-0216Z-attempt4.txt, from ../../code-cluster/attempt-4/watch-after.txt); the CFS $CV and $MC sources'
  atimes are unchanged (2026-10-23T15:52:50Z, 2026-07-21T04:16:41Z). The director's ruling (2026-11-06): for guarded
  readers whose reads are only their own staged copies and the repository, the fence is a recorded line, not a
  refusal; the 303-input stat is kept before and after each job.
- Files: the connect's log, done marker and copy; clone.log; submit.out, job.id; the job script, its .out, sacct;
  each unit's log and GNU time; the three done-markers; CENTRALS-DONE; the two watch snapshots.
