1B gate-D pre-check, Part 1, P0: the stat-only connect (FD-1B-PRECHECK-FD-BINDING-1.md ruling 3; declaration section
6). The director's go of 2026-11-07. Run by limitation-resolver on login27, 06:38:09-06:38:29Z, at 0 node-h.

RESULT: CLEAN. All 791 sources exist; none is missing. No file content was read.
- Staged sources, 355: the 176 derivation products, the 176 S1 unfolds, the S1 assembly, the flux constraint and the
  flux-universe file.
- Sources read in place, 436: the inputs npz, the background dump, the pins, the bank's cv.npz, the 100 Flux universes
  x {wt, wr, tdw, bkgw}, and the 8 detector universes x {wt, wr, denom_nd, bkgw}.
- The universe lists come from the bound code at M: fd_1b_toys.s1_universes(), 175 universes, and
  fd_1b_precheck_fd.universes(), 108.
- The oldest atime is 2026-10-25T06:07:09Z. So purge exposure starts at 2026-12-20T06:07:09Z (oldest atime plus
  8 weeks, arithmetic).

THE CONNECT: pfd_p0_login.sh, sha256 a975466faa32de59e742de32dd21826f43442384aaa0312f030637f7fdebd42b. The node
compared that digest before running it, and the director had the sha256 before launch.
- A fresh https clone at M = ed8f328fab52122112f54850d0078d79e81834c5, HEAD equal, porcelain 0.
- The COV2D fence was recorded: squeue rc 0, no cov2d-* row. It was also clear from the Mac at 06:36:20Z
  (fence-p0.out).
- login27 was the lowest-load node (survey-p0.txt).
- Each source's name, size, mtime and atime are in p0.out. The local root /dev/shm/limres-pfd-p0-20261107 was removed
  by its literal path, and the script deleted its own copy. ssh rc 0, script rc 0.

Files: pfd_p0_login.sh, p0.out (the full transcript with every stat line, NERSC banner included), fence-p0.out,
survey-p0.txt. Digests: SHA256SUMS.txt.
