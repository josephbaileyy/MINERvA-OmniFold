1B pre-check Part 1, P2: the pilot. Job 60990199, 2026-11-08T06:16–06:32Z. walls: PASS. Charged 0.2631 node-h.

The director gave the go for route (a) with choice (i): the committed packer plus s5c_array.sh, run behind a wrapper
job script that first runs one in-lane thread probe step. Binding 1 with addendum A1, at
M_A1 = 8d7a40c23b3b6b70c2913ba363a10a22e152aee4. This receipt goes to coverage-5b-audit, which reads the walls before P3.
Only the products' meta was read, never their arrays.

FILES
  pfd_p2_login.sh       the submit connect, sha256 1f9e1f85...; stdout p2.out, stderr p2.err (login banner only)
  pfd_p2_post_login.sh  the records connect, sha256 7d4c13a0...; stdout post.out (base64 tar replaced by a note giving
                        its sha256), stderr post.err
  tools/                pfd_p2_wrapper.sh (038a6353...), pfd_threadprobe.py (d9369712...), make_p2_table.py
                        (43f35c8e...), each written to $V/p2/tools by the submit connect and gated on its sha256
  records/              the tar-back from the records connect; every file's sha256 equals the cluster value
  fence-mac*.out, survey*.txt   the Mac-side COV2D fences and login-load surveys before each connect
  watch.log             sacct State polled from the Mac every two minutes (read-only)

SUBMISSION (p2.out; login27, 06:14:17–06:14:54Z, ssh rc 0, connect rc 0)
  iris, read first. m3246: user 2341.5 charged of 10000.0, project 18242.7 of 20000.0. Remaining: user 7658.5, project
  1757.3. The cap of 18.5 node-h is under half of each (3829.2 and 878.6), so OK.
  Fence: clear before anything was written and again immediately before sbatch. squeue was empty; no fd1b job.
  Deploy: a fresh clone at M_A1 in $V/deploy, porcelain 0. Each bound file was gated on its sha256:
    packer b72aaa62..., s5c_array.sh dd95db5d..., module a7fbbb58..., setup_salloc_env.sh ea3c6998... (blob b4a9c3f6).
  Table: records/p2/tables/tasks-p2.tsv, sha256 16c55eca5ca2a3dca8a0c6d5e27f1b88128d55883ac2fb8c349519bb17d3726d. Eight
    lines, exactly section 7's pilot items in order: A_CV B_CV Dnom_CV A_Flux_0 B_Flux_0 Dnom_Flux_0 A_MinosEfficiency_0
    B_MinosEfficiency_0. The generator checked the module's PILOT tuple against section 7 by ast; the connect
    re-checked the lines in bash.
  Submitting shell: all four thread variables unset.
  sbatch -A m3246 -q regular -C cpu --nodes=1 --exclusive --no-requeue --export=ALL,HOME=/global/homes/j/josephrb
    --time=01:00:00 -J fd1b_pfd_p2 ... pfd_p2_wrapper.sh <deploy> M_A1 <table> <lanes> 0 7 <probe>
  Job 60990199. TimeLimit read back as 01:00:00.

THE JOB (records/p2/logs/sacct-p2.psv, records/p2/logs/fd1b_pfd_p2_60990199.out)
  COMPLETED 0:0 on nid005567. Elapsed 00:15:47, ElapsedRaw 947 s, 1 node: 947 x 1 / 3600 = 0.2631 node-h charged,
  against 1.0 reserved and the cap of 18.5. Part 1's total so far is 0.2631 node-h.
  Steps: threadprobe 56 s. line0..7 784–885 s each; every step COMPLETED 0:0; MaxRSS 20040M–21522860K.
  Each lane's s5c line ended rc=0. No Traceback or refusal appears in any lane log.

THREADS (records/p2/lanes/threadprobe-60990199.log; the probe step had the lanes' exact shape)
  OMP/OPENBLAS/MKL/NUMEXPR thread variables: all unset. SLURM_CPUS_PER_TASK 32; affinity size 32; os.cpu_count 256.
  python 3.11.14, numpy 1.26.4, lightgbm 4.6.0, threadpoolctl 3.6.0.
  threadpool_info:
    openblas 0.3.30 (libopenblasp-r0.3.30.so)         32 threads
    libgomp (env lib)                                  32 threads
    scipy's openblas 0.3.29.dev                        32 threads
    scikit-learn's libgomp                             32 threads
  The OpenMP default is 32.
  meta["threads"] = 32 in all eight products (post.out section 5): LightGBM was given --threads 32 by the table.
  P3 reuses the wrapper. Its probe must reproduce the four variables, SLURM_CPUS_PER_TASK, the affinity size and
  threadpool_info. Any difference goes to the director before P3's results are read.

WALLS (records/p2/walls.json; the bound module's `walls` subcommand, run from the deploy)
  verdict PASS.
  max seconds_unfold 821.547 (Dnom_Flux_0) against unit_seconds 1370.0.
  max peak_rss_kib 21342840 against rss_limit_kib 44040192.
  Per item (seconds_unfold, peak_rss_kib):
    A_CV 711.848, 20197840          B_CV 709.779, 20143908          Dnom_CV 708.423, 20927976
    A_Flux_0 814.013, 20828764      B_Flux_0 814.157, 20493244      Dnom_Flux_0 821.547, 21342840
    A_MinosEfficiency_0 772.388, 20852940                          B_MinosEfficiency_0 773.919, 20389876
  Every product's meta names slurm_job 60990199, numpy 1.26.4 and fd_1b_precheck_fd.py a7fbbb58...

READS AND ATIME
  The module's atime sidecars (records/unf/atime-*.json): 8 sidecars, 4–8 files each, moved [] in every one.
  stat-after vs stat-before (records/p2/logs/stat-{before,after}.txt):
    the four originals read in place (of_inputs_5d.npz, bkg_dump.npz, pins.json, the bank's cv.npz) are unchanged in
    size, mtime and atime;
    the staged flux copy ($V/stage/flux_universes.root) moved atime 1794033543 -> 1794118648 through ROOT's plain read,
    which the director allowed and asked to be recorded.

RECORDED FACT: SETUP IN THE DEPLOY
  In every lane, s5c_array.sh's source of setup_salloc_env.sh from the deploy clone printed two "No such file or
  directory" lines (records/p2/lanes/logs/*.env.log, all eight identical). The clone has no
  unbinned_unfolding/build/setup.sh and no MINERvA101/opt/bin/setup.sh: those are build products of the main pscratch
  checkout, not tracked files. The conda activation ran, and s5c's Python 3.11 check passed. The unfolds completed.
  The same two lines appear in earlier 1B and F1 receipts' env logs, for example
  ../../staged/stage1/connect32/env.log.

PROJECTION FOR P3, FROM THESE WALLS (an estimate, not a measurement; the walls gate is coverage-5b-audit's)
  Step elapsed minus seconds_unfold was at most 74 s per item (line0: 786 - 711.8). Section 7's P3 puts at most 6 items
  in a lane. With the pilot's largest seconds_unfold, the worst lane is about 6 x (821.5 + 75) + 56 (probe) = 5,435 s,
  or 1.51 h. That is inside 02:30:00 (9,000 s). Seven one-node jobs would charge about 10.6 node-h at that worst case,
  against 17.5 reserved; section 7 expected 9.3. No REPRICE trigger: walls PASS, and the projection is inside the price.
