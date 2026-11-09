Band diagnosis, P1: section 4.2's HK reading and the readout-reproduction control, from Part 1's products
(FD-1B-BAND-DIAGNOSIS-BINDING-1.md rulings 2, 4 and 5; declaration sections 4.2, 5 and 7). Run by limitation-resolver on
login27, 2026-11-08T23:58:08–23:58:25Z, at nice 19 and 0 node-h, with no Slurm job.

RELEASE: the director's go of 2026-11-08, after ENS1's stage-2 analysis ended (login37, 23:54:11Z) with no ens1_* job
left, on bdg_p1_login.sh sha256 6ac2eee9fd1710f1f125b65c942fac1b3eaef36ead1fe0a6fc16f101da0202f9. The node compared
that digest before running it.

RESULT: the reproduction control PASSED, all four detector bands read SAME COMPARISON, and no source's stat moved.
- same rc 0; the connect rc 0; ssh rc 0 (read unpiped).
- The control (declaration section 5) passed, with same.json "reproduced": {"part1_readout_sha256": "8e05ca9b...",
  "F_src_kappa_bitwise": true}:
  - F_src and kappa for the four detector bands, recomputed on O_NOATIME reads, equal readout.json's
    /bands/<b>/factors/{F_src,kappa} bit for bit;
  - Part 1's A, B and Dnom products at CV equal the derivation CV product bitwise;
  - the staged copies match staged.json, and the S1 assembly matches S1's digest.
  A failure of any of these would have raised Invalid and returned rc 4. Before §4.2's readings are read, the readout
  must have reproduced.
- same hashed 37 files at first read (same.json "digests"): the 9 derivation copies, the S1 assembly and Part 1's 27
  products.

SECTION 4.2, HK: rule K against rule S (same.json /bands/<b>/HK). This is a record of Part 1's committed products, not
a test. The thresholds (|ln(g^2 Dnom/E)| <= 1e-12 and |ln(B/A)| <= 1e-5 in every kappa-resolved cell) were set after
the declaration's disclosed values were seen.
  band              verdict          kappa-resolved   max |ln(g^2 Dnom/E)|   max |ln(B/A)|
  GEANT_Neutron     SAME COMPARISON  14               2.2e-16                1.21e-7
  GEANT_Proton      SAME COMPARISON  14               2.2e-16                3.12e-7
  GEANT_Pion        SAME COMPARISON  16               0                      3.34e-8
  MinosEfficiency   SAME COMPARISON  16               2.2e-16                5.29e-9
  cells_outside is empty in every band.
  - The B/A column is the block-level counterpart of the declaration's disclosed |ln F_side| (F_side = sqrt(B/A)). It
    is twice those values: 6.0e-8, 1.6e-7, 1.7e-8 and 2.7e-9, as disclosed.
  - The licence, declaration section 4.7, quoted with the values filled in, for each band b: "a record of Part 1's
    committed products, not a test: reading Part 1's committed readout and products, for band b kappa/(F_src*F_side) = 1
    to [value] in |ln| and g^2*Dnom = E to [value], with F_side = sqrt(B/A) differing from 1 by at most [value]; the
    thresholds were set after these values were seen. On that record, rule K's FAIL is not separate evidence."
    Not citable for: a test of HK; anything about kappa for the flux or interaction groups, or at another truth.
- Descriptive, per universe (same.json /bands/<b>/per_universe):
  - max |U.x_E - U.x_Dnom| / |s_E| is 0.0 for all 8 detector universes;
  - max |U.T_u - U.T_CV| / |U.T_CV| is 1.48e-16 for all 8.

SECTION 5's BASELINE: stat-before.txt
  The 73 sources P0 listed (#944) are listed again from the bound code at M: 11 staged, 27 Part 1 products, the 34
  in-place ruling-4 sources and pins.json. Each is stat'd only, as type|inode|nlink|size|mtime|atime|ctime|path. 73
  lines, 0 missing, sha256 7986e2bf...
  - It was taken at launch, after ENS1's stage-2 analysis ended, as the director's note of 2026-11-08 requires. This is
    the before-stat that P3's after-stat is compared with, byte for byte.
  - The 73 sources were re-stat'd after same into $W/stat-after-p1.txt. That file is byte-identical to stat-before.txt
    (the same sha256, 7986e2bf...), so no source's atime, or any other stat field, moved during P1.

THE CONNECT: bdg_p1_login.sh (sha256 6ac2eee9...). Its stdout is p1.out and its stderr p1.err (the NERSC banner only).
- Before the connect, from the Mac: fence-p1.out showed no cov2d-* job (23:56:19Z). survey-p1.txt picked login27
  (load 3.02 on 244).
- The in-script fence passed (refusing rows: []). Under ruling 4's SHARED branch only fd1b_bdg_* was allowed, and squeue
  listed no job.
- A fresh https clone at M = 83ac32fb5024026ac6c51c0621d5ae9ff9073370: HEAD equal, porcelain 0. fd_1b_band_diag.py
  sha256 658ca918... and Part 1's readout.json 8e05ca9b... were gated.
- The thread environment was as Part 1's P4: nothing exported. OMP, OPENBLAS, MKL and NUMEXPR were all unset, both as
  inherited and in Python (numpy 1.26.4).
- The new root $W = /pscratch/sd/j/josephrb/fd-1b-band-diag-20261109 was created owner-only. Its date is a label fixed
  in the connect; the run began at 23:58Z on 2026-11-08. It holds stat-before.txt, stat-after-p1.txt and same.json
  (sha256 15418f80...). Nothing was written under $V. The local clone root /dev/shm/limres-bdg-p1-20261109 was removed
  by its literal path.

FILES: bdg_p1_login.sh, p1.out, p1.err, fence-p1.out, survey-p1.txt, same.json and stat-before.txt (both extracted
from p1.out, with sha256 equal to the cluster's). Digests: SHA256SUMS.txt.
