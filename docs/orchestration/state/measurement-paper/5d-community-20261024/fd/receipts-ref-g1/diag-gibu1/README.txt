REF-G1 G-IBU1 diagnosis (the director's request of 2026-11-05 after the read's STOP, #792). Run by limitation-resolver
on login27, 2026-11-05T15:40:52Z-15:40:54Z, 0 node-h, read-only, with the connect the director approved
(refg1_gibu1_diag_login.sh, sha256 41f10bde...). Copied with dd iflag=noatime from
/pscratch/sd/j/josephrb/ref-g1-20261105/diag-gibu1/. Full sha256 of each file: SHA256SUMS.txt. No Delta was formed;
no other product was loaded. The STOP stays final until the director binds an addendum.

diag.json (sha256 4e34f809...) compares a = the batch's gibu1.npz (70bb60d0..., 18,718 bytes) with b = IBU-1's D_N.npz
(a160dbea..., 17,305 bytes), each read once with os.O_NOATIME and its sha256 checked before np.load. Both hold exactly
F_fold, F_sub and ks (plus meta).
- ks: int64 [7], equal ([1, 2, 3, 4, 5, 10, 20]).
- F_fold: float64 [7, 153] both; 35 of 1071 elements differ; max|a-b| 5.220e-54; max|b| 8.015e-36;
  max|a-b|/max|b| 6.51e-19; largest difference 2.0 spacings of b (ulps). Per-K max|a-b| (K = 1, 2, 3, 4, 5, 10, 20):
  8.16e-56, 5.10e-57, 8.16e-56, 5.22e-54, 1.63e-55, 5.22e-54, 2.04e-56.
- F_sub: float64 [7, 153] both; 36 of 1071 differ; max|a-b| 1.044e-53; max|b| 8.014e-36; max|a-b|/max|b| 1.30e-18;
  largest difference 2.0 ulps. Per-K max|a-b|: 2.61e-54, 4.08e-56, 2.04e-56, 1.63e-55, 2.61e-54, 1.04e-53, 5.22e-54.
- No non-finite values on either side.
- Environment of the diagnosis: numpy 1.26.4 (np.show_config in diag.json: BLAS/LAPACK openblas, gcc 12.3.0);
  threadpoolctl reports openblas 0.3.30, pthreads, Zen, 1 thread (OMP/OPENBLAS/MKL_NUM_THREADS=1 here).
- Recorded thread settings of the two producers (from receipts, not measured here): IBU-1's D_N ran with
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 (nd-unfolding/ibu1/sbatch_ibu1.sh:25 at its deploy
  7ea30e3d) under srun -c 2 (ibu1/receipts/sacct.txt:5, cpu=2); gibu1 ran with OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS=32
  (receipts-ref-g1/batch/refg1_batch_job.sbatch:26), lane 0 of 8 on nid005892, numpy 1.26.4 and scipy 1.16.3 (its
  meta). config.json's gibu1_environment pins the interpreter and Python version only (ref_g1.py:277-284 at M).
- atime: diag.log's stat shows both files at atime 1793891896 (2026-11-05T15:18:16Z) before and after this run, so this
  run's O_NOATIME reads left them unchanged. 15:18:16Z is the read's G-IBU1 control (STOP.json written_utc 15:18:16Z),
  which opens both files with plain np.load and sha256 (ref_g1_read.py:399-404 at M). D_N.npz's listed atime was
  2026-10-23T15:04:43Z (preconditions listing.json), so its exposed-from date moved from 2026-12-18T15:04Z to
  2026-12-31T15:18Z.
- diag.log (the run's log, including np.show_config's text), diag.done (rc 0), and the connect as run.
