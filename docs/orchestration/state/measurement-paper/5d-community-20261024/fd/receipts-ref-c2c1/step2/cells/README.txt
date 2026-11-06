REF-C2C1 step two, stage 3a: the reported cells (REF-C2C1-BINDING-2.md, the director's ruling of 2026-11-06 inserting
the cells step before the read, #825 at main 1aa805b5; code at M = 77d76cfc). Run by limitation-resolver on login27,
2026-11-06T06:50:20Z-06:51:09Z, 0 node-h, under the binding's fixed conditional sequence. The connect as run:
refc2c1_cells_login.sh, sha256 bf04faeaf44b35ba8a3d49f4b7145e7e2a6df083b518f1af822eb8ab8bbdaa8a. Copied with dd
iflag=noatime from /pscratch/sd/j/josephrb/ref-c2c1-20261106/read/. Full sha256 of each file: SHA256SUMS.txt.

OUTCOME: PASS (rc 0). THE CELLS FILE FOR 3b: cells.root, sha256
    f06e4a26efc3085eac71d80fce5f806f17dc04cb89bfcc51ee2c939332aed743   (5,041 bytes; 205 cells)
committed here; 3b's read gates on it on main and passes it as --cells-sha256, in the same read directory
(/pscratch/sd/j/josephrb/ref-c2c1-20261106/read).
- A fresh clean clone at M, porcelain --ignored 0 before and 0 after; the binding's 8 blobs, 0 mismatches.
- `ref_c2c1_read.py cells --out <read>/cells.root` (write_cells), root_6_28 (3.11.14): it read only the publication's
  precision ROOT (config.json publication.path, cov_ptpl_minerva_inclusive_6GeV.root, pin 6c6dce72...), staged once by
  O_NOATIME into read/cells-inputs/ under read_guards, and no unit product. Its stdout (cells.stdout.txt; written on pscratch as
  cells.json, renamed here because it is not JSON: the reader prints a "[paper TH2D]" axis line before its JSON)
  ends {"cells": 205, "sha256": "f06e4a26..."}; 205 is the count the declaration names (REF-C2C1-DECLARATION.md:69, "the 205 indices").
  cells.root holds the identity histogram, the rule ("positive diagonal of StatOnlyCovariance on the paper's 224-bin
  global grid") and source_sha256.
- The publication, stat'd (no read) before and after: owner josephrb, mode 660, atime 1793499822, 1,272,641 bytes,
  unchanged.
- The fence, recorded: the full squeue at launch (the 4 replica jobs PENDING; cov2d-pseudo_AR23 and fd1b_mc_receipt_a2
  RUNNING).
- Files: cells.root, cells.stdout.txt, cells.log, cells.done (rc 0), clone-cells.log, the connect as run.
