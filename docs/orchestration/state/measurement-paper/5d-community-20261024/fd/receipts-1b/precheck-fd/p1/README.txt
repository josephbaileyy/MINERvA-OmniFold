1B gate-D pre-check, Part 1, P1: staging and controls E and M (FD-1B-PRECHECK-FD-BINDING-1.md ruling 3; declaration
sections 5-7). The director's go of 2026-11-07, run on P0's clean result (#876). Run by limitation-resolver on login27,
06:38:45-06:39:05Z, at nice 19 and 0 node-h.

RESULT: INVALID on control M. Under declaration section 5, a failed control makes the run INVALID, reported
unrepaired. Staging and control E passed.

WHAT PASSED (p1.out):
- The fence gate, immediately before staging: squeue rc 0, no cov2d-* row.
- The clone: fresh, at M = ed8f328f, porcelain 0. The module sha256 is 7c3ffe86..., the bound blob.
- Staging, with the bound `fd_1b_precheck_fd.py stage` (fd_1b_inv.stage). All 355 entries of the staging spec were
  staged into /pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107/stage. The spec was generated in the connect from
  fd_1b_toys.s1_universes() at M (sha256 f648816d5b4dbbe1fc1a9b55f5517eb58116fef79c927ec7c224be50dbb912d6, kept in
  the run directory; not committed, since it names the staged copies' bare filenames):
  - 176 derivation products and 176 S1 unfolds;
  - the S1 assembly (db000707), the flux constraint (e38ad7d2) and the flux-universe file (5eecae84). Each equals its
    declared digest, since stage refuses otherwise;
  - each source was read once with O_NOATIME. The stage reported missing [] and rc 0.
  - staged.json has sha256 f2f0641975d810172ad946f650d9b59c52fea57e3b70947c12cb87656bf31189. Following I0's practice,
    it is not committed, because it lists each product's digest.
- The source stat: stat-before.txt and stat-after.txt (355 sources: name, size, mtime, atime) are byte-identical,
  sha256 a14aeddf... both. No atime moved.
- Control E: gate D's flux and detector per_group_sigma_ratio, and the diagnosis's per-band sigma_ratio for all five
  bands, reproduced bit for bit. The readout runs control E before control M, and it reached control M.

THE FAILURE (p1.out):
  CONTROLS: FAIL (fs.Invalid): band Flux: the staged S1 unfolds do not reproduce the assembly's block exactly
- Control M stops at the first band it checks (Flux), so the detector bands were not reached.

THE CAUSE, from reading the code at M (not run):
- S1 built its blocks with U = functional_matrix(fine_map(definition)) in float64 (s1_assemble.py:303 @ ed8f328f).
- It stores that U in the assembly as float32 (:370, "U": U.astype(np.float32)).
- fd_1b_precheck_fd.readout's control M rebuilds the blocks with the assembly's stored s1["U"], so a bitwise match
  cannot hold.
- I0's control M rebuilt them with the float64 U from the H2 definition (fd_1b_inv.py:321 @ ed8f328f) and passed.
- The test suite could not see it, because its fixture's U is an identity matrix, exact in float32.
- Control E is unaffected: gate D built E with the stored s1["U"] too, and E reproduced bit for bit.
- This is a defect in the lane's control code, not a finding about the data. Its repair is a code change for the
  director to rule on, and nothing was patched or rerun.

LEFT ON PSCRATCH: the 355 staged copies and the record files under /pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107
(stage/, the stat lists, the spec, and an empty unf/), kept for the director's ruling. The local
clone root /dev/shm/limres-pfd-p1-20261107 was removed by its literal path. No job ran.

Files: pfd_p1_login.sh (sha256 7b8cb1c3..., compared on the node; the director had it before launch), p1.out (the full
transcript, NERSC banner included), stat-before.txt, stat-after.txt. Digests: SHA256SUMS.txt.
