Band diagnosis, P3: the bulk (FD-1B-BAND-DIAGNOSIS-DECLARATION.md section 7; BINDING-1 ruling 2 as addenda A1 and A2,
#958 and #962: 4 jobs x 7 lanes x 4 items, --time=01:40:00). Run by limitation-resolver.

RELEASE: the director's go of 2026-11-09 on bdg_p3_login.sh sha256 260b162410fa5b6ff940652b47f8266eafc20bf65b7e5d29dacac6ce8fdde98f,
and the director's pre-approved go on bdg_p3_post_login.sh sha256 1f84582df81cbd6ce31031fe6fdaa70a7ec075445bba50ff7e629ba3350f1491.
Both shas were audited by coverage-5b-audit (GO, https://github.com/josephbaileyy/MINERvA-OmniFold/pull/965#issuecomment-6729650677).
Each node compared its digest before running it. The sshproxy certificate is valid from 2026-11-09T00:10:00Z to
2026-11-10T00:11:04Z (ssh-keygen -L, read locally).

RESULT: all four jobs COMPLETED, 126 products exist, and no source's stat moved.
  job        lines    node       start (UTC)          end (UTC)            elapsed   state
  61015630   0..6     nid004347  2026-11-09T00:56:47  2026-11-09T01:45:32  00:48:45  COMPLETED 0:0
  61015632   7..13    nid004405  2026-11-09T00:56:47  2026-11-09T01:45:41  00:48:54  COMPLETED 0:0
  61015633   14..20   nid004475  2026-11-09T00:56:47  2026-11-09T01:46:43  00:49:56  COMPLETED 0:0
  61015635   21..27   nid004966  2026-11-09T00:56:47  2026-11-09T01:46:06  00:49:19  COMPLETED 0:0
- Charge: 11,814 s on 4 nodes, 3.28 node-h of the 6.67 reserved. With P2's 0.457, the campaign has used 3.74 node-h of the
  9.0 cap.
- Every step COMPLETED 0:0: 4 thread probes and 28 lines (post.out, section 1).
- Section 5's final comparison: the 73 sources were re-stat'd after the jobs (records/p3/logs/stat-after-p3.txt). The
  result is byte-identical to P1's stat-before.txt (sha256 7986e2bf...), as was the re-stat at submission
  (stat-submit.txt). The module's 36 per-lane atime records in records/unf (28 from P3, 8 from P2) all list moved [].
- Products: 126 in $W/unf (14 pilot + 112 bulk), each listed with size and sha256 in post.out, section 4. The npz bytes
  stay on pscratch.

THE WINDOWS (to the second; job stamps from records/p3/logs/fd1b_bdg_p3_*.out)
  submit connect 00:55:40–00:55:48Z (p3.out; no copy made: P2's deploy was reused and re-gated)
  read windows: from each job's probe completion (00:57:03.570–00:57:03.722Z) to its packer end (01:45:32.041,
    01:45:40.562, 01:46:05.829 and 01:46:43.338Z)
  post connect 04:43:41–04:43:46Z (post.out). The post ran about three hours after the jobs ended, after a pause in
    this lane; the stat comparison covers that interval too.

THE THREAD ENVIRONMENT
  Each job's in-lane probe (records/p3/lanes/threadprobe-*.log) reads SLURM_CPUS_PER_TASK 32, affinity 32 and
  openmp_default_num_threads [32, 32], status ok. This matches P2's probe and Part 1's.

THE SUBMIT CONNECT (bdg_p3_login.sh; stdout p3.out, stderr p3.err, the banner only), login27
  - iris: m3246 user 2422.8 of 10000.0, project 18340.4 of 20000.0, as at P2; P2's charge was not yet posted. The cap
    is under half of each remaining balance.
  - P2's gates read from disk: "EQUAL PASS".
  - Fence (A1): only fd1b_bdg_*, ll5d_* and prr_* would have been allowed, with no fd1b_bdg_* queued. squeue listed no
    job, at both checks.
  - P2's deploy: still at M with no tracked change. The module (658ca918), the packer (b72aaa62), s5c_array.sh
    (dd95db5d), mnv_guarded_run.py (30162f57) and setup_salloc_env.sh (ea3c6998) were re-gated.
  - Tools, written and gated, committed here at their audited shas (coverage-5b-audit's low (b)):
    tools/make_bdg_p3_table.py 0aed80b8; tools/pfd_p2_wrapper.sh 038a6353 (Part 1's committed P2/P3 job script,
    byte-identical); tools/pfd_threadprobe.py d93697123 (Part 1's, unchanged); tools/gen_p3.py c665826e, which writes both
    connects.
  - The table (records/p3/tables/tasks-p3.tsv): "TABLE: 28 lines, 112 items = bulk_items(); each line one group of 4".
    Job j runs lines 7j..7j+6.
  - Four sbatch, each -A m3246 -q regular -C cpu --nodes=1 --exclusive --no-requeue --time=01:40:00 -J fd1b_bdg_p3.
    Each TimeLimit was read back as 01:40:00.

THE POST CONNECT (bdg_p3_post_login.sh; stdout post.out, stderr post.err), login27
  sacct for the four jobs and their steps; the deploy still at M, clean; section 5's final re-stat; the product list
  (126); and the records tar (140 files; each sha256 on the cluster equals its sha256 here). In the committed post.out,
  the base64 block is replaced by a one-line note giving the decoded tar's sha256 (fc1be6d7...) and the full stdout's
  (911cfee0...).

HELD LOW (coverage-5b-audit (a)): make_bdg_p3_table.py's check that every carried item is in items() can never fire,
because items() is pilot plus bulk and the lines must already equal bulk_items(). The generator is left unchanged so
that the audited sha stands.

FILES
  bdg_p3_login.sh, p3.out, p3.err, fence-mac.out, survey.txt
  bdg_p3_post_login.sh, post.out, post.err, fence-mac-post.out, survey-post.txt
  tools/: make_bdg_p3_table.py, pfd_p2_wrapper.sh, pfd_threadprobe.py, gen_p3.py
  records/: p3/tables, p3/logs (the four job outputs, submit records, jobs.txt, stat-submit and stat-after-p3),
    p3/lanes (thread probes, line logs, inventories), unf/atime-*.json
  Digests: SHA256SUMS.txt.
