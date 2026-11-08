1B pre-check Part 1: the P1 rerun at M_A1 (2026-11-08T05:40Z, login27, 0 node-h). PASSED.

The director gave the go after addendum A1 (#921, merged 7ff4ab35). A1 binds M_A1 = 8d7a40c23b3b6b70c2913ba363a10a22e152aee4
(#883's merge) with the module fd_1b_precheck_fd.py at sha256 a7fbbb58. The connect pfd_p1r_login.sh has sha256
3ac867ca2ac2775b636a7e9cf65bf08d74339915ccfdbe60d035a9e80bdbd894. P1 (#877) was ruled INVALID because control M used the
assembly's float32 U. #883 repaired that, and coverage-5b-audit found it GO.

RESULT
  "CONTROLS: E and M PASSED; the readout stopped at its first mode product, as expected before P2:
   /pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107/unf/fd1b_pfd_A_CV.npz". controls rc 0; connect rc 0.

WHAT RAN (p1r.out is stdout; p1r.err is stderr, the login banner and host line only)
  Before the connect, from the Mac: fence-mac.out showed no cov2d-* job. survey.txt picked login27 (load 7.49 on
  244). One ssh (saul -> login27) wrote the script to a /dev/shm mktemp, compared its sha256 (matched), then ran it.
  ssh's rc was 0, read unpiped.
  1. The fence passed: no cov2d-* row. The clone was fresh at 8d7a40c2, HEAD equal and porcelain 0. The module sha256
     was a7fbbb58, as expected.
  2. Thread environment, as I0 ran (A1, ruling 2): no thread variable exported.
       shell, as inherited and as used: OMP_NUM_THREADS, OPENBLAS_NUM_THREADS, MKL_NUM_THREADS, NUMEXPR_NUM_THREADS all
       unset
       python, inside the controls: the same four unset; numpy 1.26.4; threadpoolctl:
       [('openblas', 128, '0.3.30', '/global/u2/j/josephrb/.conda/envs/root_6_28/lib/libopenblasp-r0.3.30.so')]
     A fact, not a defect (the director): OpenBLAS ran with 128 threads, inherited with none set, as I0 ran. P2 and P3
     run on compute nodes under their own job scripts, and their thread settings are whatever Part 1's bound sbatch
     sets. P2's connect will report them.
  3. The stage, verified and not re-staged, reading every file with O_NOATIME (A1, ruling 3). staged.json's sha256 is
     f2f06419, equal to P1's record. All 355 staged copies were re-hashed: 0 mismatches, 0 extra files, 0 missing.
  4. The originals: the spec's 355 sources were stat'd only, as name|size|mtime|atime.
       stat-p1r.txt (before the controls) is byte-identical to P1's stat-after.txt (a14aeddf..., #877).
       stat-p1r-end.txt (after the controls) is byte-identical to stat-p1r.txt.
     A difference at either point would have STOPped with rc 4. Neither did. No original's atime moved.
  5. Controls E and M ran through the bound pfd.readout with the committed nd-unfolding/pv-ladder/readouts/
     h2_definition.json as its definition argument, and stopped as above.

STAGE ATIME (stat only)
  p1r-stage-atime-before.tsv         b4b5e134...  before the rehash
  p1r-stage-atime-after-rehash.tsv   b4b5e134...  after the rehash: identical, 0 of 356 files moved
  p1r-stage-atime-after-controls.tsv cd8b5812...  after the controls: 286 of 356 moved
  The staged copies' atimes may move during the controls, by the bound module's own reads (a7fbbb58:360-392:
  fs.load_s1, derivation_blocks, sa.flux_weights, sa.universe_bands). The director allowed this: they are staged
  working copies, never an original, and P1 made the same reads. The 286 that moved are listed by name in p1r.out:
    - the derivation npz files, CV included;
    - flux_constraint.txt;
    - s1/s1_assembly.npz;
    - uni/S1_Flux_0..99, uni/S1_GEANT_{Neutron,Pion,Proton}_{0,1} and uni/S1_MinosEfficiency_{0,1}.

THE RECORDS FETCH (pfd_p1r_fetch.sh, sha256 70e30fa6..., the director's go; fetch.out, fetch.err, fence-mac-fetch.out)
  login27, 0 node-h, fence clear, ssh rc 0, rc 0. It read only the five files above that the P1 rerun wrote under
  $V, each with O_NOATIME, and wrote nothing. Each decoded copy's sha256 and size equal the remote values. In the
  committed fetch.out the base64 blocks are replaced by notes; the full stdout's sha256 is on its last line.
