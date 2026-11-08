Band diagnosis, P0: the stat-only connect (FD-1B-BAND-DIAGNOSIS-BINDING-1.md rulings 2, 4 and 5; declaration section
6). The director's go of 2026-11-08 on sha256 1ed8dd7c. Run by limitation-resolver on login27, 17:45:24-17:45:39Z, at
0 node-h.

RESULT: CLEAN, and ruling 4 reads BRANCH SHARED.

- All 73 sources exist; none is missing. No file content was read (stat, lstat and readlink only).
  - Staged, 11: staged.json, the 9 derivation copies (CV + 8 detector universes) and the S1 assembly, under
    /pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107/stage.
  - Part 1's products, 27: fd1b_pfd_{A,B,Dnom}_{CV,<u>}.npz under .../fd-1b-precheck-fd-20261107/unf.
  - In place under ruling 4, 34: of_inputs_5d.npz, s5c-20260924/runs/p2/bkg_dump.npz, and the 8 detector universes
    x {wt, wr, denom_nd, bkgw} under s5p-20260926/bank_detector.
  - Other in place, 1: fd-1b-20261030/pins.json.
  - The list comes from the bound code at M: fd_1b_band_diag.detector_universes() (8 universes, asserted),
    fd_1b_precheck_fd.TAG and MODES, and s5p_universe.weight_keys() (denom_nd keys, asserted).
- Every source's realpath equals its path; no symlink is involved.
- The oldest atime is 2026-11-01T01:33:08Z (pins.json). Purge exposure therefore starts at 2026-12-27T01:33:08Z
  (oldest atime plus 8 weeks, arithmetic). P0's atimes are a record only: the section 5 comparison takes its
  before-stat at P1.

RULING 4: BRANCH SHARED.
- ENS1's stage-2 list is stage2-inputs-stat.txt (#940), read from the clone at M: sha256 0764135280f2d025..., 738
  rows. Each of its paths was realpath'd on the node.
- All 34 ruling-4 sources are shared with it, by realpath (each is also one of ENS1's listed paths verbatim).
  None of the other 39 sources is shared.
- Cross-check, done on the Mac from p0.out and the committed list: for all 34, the inode, size and mtime equal ENS1's
  recorded values.
- Consequence, per the binding: this campaign's P1-to-P3 window must not overlap any ens1_* job. The connects'
  fence allows fd1b_bdg_* only, and the director sequences the gos. Section 5's atime comparison is not narrowed.
  The director's note of 2026-11-08: P1's before-stat is taken after ENS1's stage 2 and its post-run have ended,
  because ENS1's tasks read these files plainly.

THE CONNECT: bdg_p0_login.sh, sha256 1ed8dd7c10fa193ad193779490e3c156d6bf27380b2f6bb8de7ac1ca80ee48c8. The node
compared that digest before running it, and the director had the sha256 before launch.
- A fresh https clone at M = 83ac32fb5024026ac6c51c0621d5ae9ff9073370, HEAD equal, porcelain 0.
- The fence was recorded from squeue (rc 0): no cov2d-*, ens1_*, rs1_* or fd1b_bdg_* row. From the Mac,
  cov2d_fence.sh was also clear at 17:43:24Z (fence-p0.out).
- login27 was the lowest-load node (survey-p0.txt).
- The local root /dev/shm/limres-bdg-p0-20261108 was removed by its literal path, and the script deleted its own
  copy. ssh rc 0 (read unpiped), script rc 0.

Files:
- bdg_p0_login.sh;
- p0.out, the full transcript with every stat line and every SHARED row;
- p0.err, the NERSC banner only;
- fence-p0.out, survey-p0.txt.
Digests: SHA256SUMS.txt.
