1B pre-check Part 1, P3: the bulk. Jobs 60991405 60991413 60991415 60991418 60991419 60991420 60991421, about
2026-11-08T07:02–08:23Z. All seven COMPLETED 0:0. Charged 9.0892 node-h; Part 1's total is 9.3523 node-h, against a cap of 18.5.

Route (a) with choice (i), as in P2: the committed packer and s5c_array.sh, run behind P2's wrapper job script, which
first runs one in-lane thread probe step. Binding 1 with addendum A1, at
M_A1 = 8d7a40c23b3b6b70c2913ba363a10a22e152aee4. The director approved the submit connect (a00b632b...) and the records
connect (ca6f868c...). Only the products' meta was read, never their arrays.

FILES
  pfd_p3_login.sh       the submit connect, sha256 a00b632b...; stdout p3.out, stderr p3.err (login banner only)
  pfd_p3_post_login.sh  the records connect, sha256 ca6f868c...; stdout post.out, stderr post.err (login banner only).
                        In post.out the base64 tar body is replaced by a note giving the decoded tar's sha256
                        (47a635ff...). Every other line is unchanged.
  tools/make_p3_table.py  P3's table generator (f066f1a0...). The submit connect wrote it to $V/p3/tools and gated it
                        on its sha256. The wrapper and the probe are P2's, unchanged, gated on the same digests:
                        ../p2/tools/pfd_p2_wrapper.sh (038a6353...) and ../p2/tools/pfd_threadprobe.py (d9369712...).
  records/              the tar-back from the records connect: 192 files, each sha256 equal to the cluster value
                        printed in post.out
  fence-mac*.out, survey*.txt   the Mac-side COV2D fences and login-load surveys before each connect
  watch.log             sacct State polled from the Mac every five minutes (read-only)

SUBMISSION (p3.out; login27, 07:00:52–07:01:33Z, ssh rc 0, connect rc 0)
  iris, read first. m3246: user 2341.8 charged of 10000.0; project 18243.9 of 20000.0. Remaining: user 7658.2,
  project 1756.1. Half of each is 3829.1 and 878.0. Part 1 charged 0.2631 + P3 reserved 17.5 = 17.7631, which is
  under the cap of 18.5, so OK.
  Fence: clear before anything was written and again immediately before sbatch. squeue was empty both times.
  Deploy: a fresh clone at M_A1 in $V/deploy-p3, porcelain 0. Each bound file was gated on its sha256:
    packer b72aaa62..., s5c_array.sh dd95db5d..., module a7fbbb58..., setup_salloc_env.sh ea3c6998... (blob b4a9c3f6).
  Table: records/p3/tables/tasks-p3.tsv, sha256 490b73be3a750f813ca694e5d1d7d76de7224f5e1ab3404d2008b64c790ddbf2.
    54 lanes and 319 items: A 106 in 18 lanes, B 106 in 18, Dnom 107 in 18; 5 or 6 items per lane. The generator
    checked the module's universes(), PILOT and MODES against the declaration. The connect re-checked the table in
    bash: 54 lanes, 319 items, 0 lanes over 6, 0 duplicates, 0 malformed, 0 pilot items.
  Submitting shell: all four thread variables unset.
  Seven sbatch calls: -A m3246 -q regular -C cpu --nodes=1 --exclusive --no-requeue
    --export=ALL,HOME=/global/homes/j/josephrb --time=02:30:00 -J fd1b_pfd_p3_j<k>. Lines per job: 0-7, 8-15, 16-23,
    24-31, 32-39, 40-47 and 48-53. Every TimeLimit read back as 02:30:00.

PROBES (post.out section 2; records/p3/logs/probe-compare.txt). These were compared before any P3 result was read.
  PROBES: ALL MATCH P2. Each of the seven in-lane probes has status ok, and none differs from P2's probe (job
  60990199) on the four thread variables, SLURM_CPUS_PER_TASK, the affinity size or threadpool_info. Those read: all
  four variables unset; SLURM_CPUS_PER_TASK 32; affinity size 32; openblas 0.3.30 at 32 threads, libgomp at 32,
  scipy's openblas 0.3.29.dev at 32, and scikit-learn's libgomp at 32.

THE JOBS (records/p3/logs/sacct-p3.psv; Start and End there are the cluster's local time, UTC-8)
  All seven jobs and all their steps are COMPLETED 0:0. ElapsedRaw by job:
    60991405 4646 s, 60991413 4640, 60991415 4660, 60991418 4575, 60991419 4712, 60991420 4785, 60991421 4703.
  sum(ElapsedRaw x NNodes) / 3600 = 32721 / 3600 = 9.0892 node-h charged, against 17.5 reserved.
  Part 1's total with P2's 0.2631 is 9.3523 node-h, against the cap of 18.5.
  Probe steps took 43–58 s. Lane steps took 3682–4724 s; the longest was line41, in job 60991420. Lane MaxRSS was
  22311184K–25109632K.
  In every job log, the packer and the lines ended rc=0 (14 lines). No lane log contains a Traceback or a refusal
  (post.out section 4 lists none).

PRODUCTS AND META (post.out sections 5–7; records/p3/logs/meta-p3.jsonl, meta only)
  products: expected 327, present 327, missing 0, extra 0. That is 109 per mode.
  meta: 327 products read. 319 came from P3 jobs (48, 48, 46, 48, 46, 48 and 35 by job, in job order) and 8 from P2.
    No product came from any other job.
  threads values [32]. Module digest a7fbbb5850733b248c89c3f4e9527c40b8531228b88241ab2d3f2063c0863d2d in all 327.
  P3 seconds_unfold: min 660.713 (B_Flux_98), median 730.912, max 919.495 (A_Flux_97), against unit_seconds 1370.
  P3 peak_rss_kib max 21638880 (Dnom_Flux_16), against the limit of 44040192.
  These are recorded values. The walls reading is coverage-5b-audit's.

READS AND ATIME
  The module's atime sidecars (records/unf/atime-*.json): 62 sidecars (54 from P3 and 8 from P2), with moved [] in
  every one.
  stat-after vs P3's stat-before (records/p3/logs/stat-{before,after}.txt): originals changed: 0. The four originals
  read in place (of_inputs_5d.npz, bkg_dump.npz, pins.json and the bank's cv.npz) are unchanged in size, mtime and
  atime. The staged flux copy ($V/stage/flux_universes.root) moved atime from 1794033543 to 1794125403, which the
  director allows.

RECORDED FACT: SETUP IN THE DEPLOY
  All 54 lanes' env logs (records/p3/lanes/logs/*.env.log) contain the "No such file or directory" lines from
  sourcing setup_salloc_env.sh in the deploy clone, as in P2 (see ../p2/README.txt). The unfolds completed.

P4
  P4's readout connect (7716c9bd...) is pre-approved by the director. It runs only after this receipt merges, with
  the probe comparison reading ALL MATCH P2 and the product check reading 327 present, 0 missing, 0 extra (both hold
  above), and after a one-line "P3 merged at <sha>" has gone to the director.
