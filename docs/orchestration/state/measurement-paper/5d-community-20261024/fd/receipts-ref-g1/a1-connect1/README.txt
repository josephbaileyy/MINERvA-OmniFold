REF-G1 addendum A1, connect 1 (REF-G1-BINDING-2-A1.md ruling 4.1; A1 section 5 step 2; #814 at main 410c4868; code at
M' = 0bb9a1bf). Run by limitation-resolver under the binding's fixed conditional sequence (sha256 and result reported,
no go awaited): the connect on login27, 2026-11-06T02:56:55Z-02:57:45Z (refg1a1_c1_submit.sh, sha256 f832d632...),
which submitted job 60884877 (refg1a1_c1_job.sbatch, sha256 f9017bf9..., checked by the connect before sbatch;
TimeLimit 00:30:00 as declared), COMPLETED 0:0 on nid004327, 03:07:47Z-03:12:11Z, 00:04:24 elapsed (0.0733 node-h;
REF-G1 total 0.2250 of the 5.0 cap). Copied with dd iflag=noatime from /pscratch/sd/j/josephrb/ref-g1-20261106/.
Full sha256 of each file: SHA256SUMS.txt.

OUTCOME: PASS (DONE: gibu1_rc 0, bars_rc 0, atime_moved 0, porcelain_after 0). This record on main gates connect 2.

THE PIN FOR CONNECT 2 (A1 section 1; B1 option (a); config.json is not changed):
    --gibu1-product /pscratch/sd/j/josephrb/ref-g1-20261106/gibu1/gibu1.npz
    --gibu1-sha256  683b493652d4a1e651e8af1684de4e170f79a636761454dd219d0ffc140dace6
  from its done-marker (gibu1.done: verdict PASS, sha256 683b4936...), equal to the job's own sha256sum of the file
  (19,055 bytes); also in gibu1-product.tsv.
- The connect: COV2D fence clear (02:56:55Z); a fresh clean clone at M', porcelain --ignored 0, the binding's 5 blobs
  (d015a352, e045d962, 24569752, 820d4afd, 2d29a915), 0 mismatches; the price: at most 0.5 node-h against the cap, and
  under half the iris balance (1983.6).
- The stat set (A1 section 4): `ref_g1_read.py reads` at M' lists 236 paths (reads.tsv: of_inputs_5d, bkg_dump,
  flux_constraint, e_central, 50 e_replica, 175 e_universe, 3 e_ladder, 2 e_closure, s1_assembly, gibu1_reference);
  each stat'd (no read; reads-stat-before.txt: owner, mode, atime, bytes, path): all 236 owned by josephrb.
  DEADLINE = earliest atime + 56 days = 2026-12-31T14:42:21Z (of_inputs_5d.npz, atime 2026-11-05T14:42:21Z).
- gibu1, alone, in IBU-1's recorded environment: `srun --exclusive -n1 -c 2 --mem=20G` (sacct step 60884877.0:
  AllocCPUS 2, 00:00:49, MaxRSS 5.46 GB), OMP/OPENBLAS/MKL_NUM_THREADS=1, NUMEXPR unset, into the new
  .../ref-g1-20261106/gibu1. ref_g1.py's gibu1_environment() admitted it (rc 0). Its meta (gibu1-meta-environment.json,
  read from the product by O_NOATIME): cpus 2; thread_env 1/1/1; threadpoolctl: openblas 0.3.30 (Zen) and scipy's
  openblas 0.3.29.dev (Haswell), each at 1 thread; root_loaded false; numpy 1.26.4, scipy 1.16.3. --mem was 20G
  against IBU-1's 10G (headroom; memory is not part of the recorded environment). G-IBU1 itself is checked by the read.
- The bars, by the new reader, into the new .../ref-g1-20261106/read (bars.json, sha256 ba4b6985...; inputs staged in
  read/inputs-bars/), at 4 threads as #791's were made: self-check PASS. Against the old bars.json (de12c674, #791):
  products_digest EQUAL (574fecea...; A1 section 3 expected it), bars and sensitivity_stat_only_null EQUAL bitwise,
  quantile_levels EQUAL; reader_sha256 and config_sha256 differ (the new reader and config, as A1 requires); the new
  record adds staged_sha256.
- The stat set again after both steps (reads-stat-after.txt) is byte-identical to the one before: no atime moved,
  so every declared input was read through O_NOATIME.
- Porcelain --ignored 0 before and 0 after, in the job.
- Files: the connect's log, done marker and copy; the job script, its .out, sacct; gibu1's log, GNU time and
  done-marker; the bars' log and GNU time; DONE; reads.tsv, reads.err (empty), the two stat files.
