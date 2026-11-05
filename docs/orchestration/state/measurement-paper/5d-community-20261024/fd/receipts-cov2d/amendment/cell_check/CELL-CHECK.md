# COV2D cell check: the pilot's reference cell sets (P5)

**By** the `cov2d` session, 2026-11-04. Proposed by the rolling audit (part 4, P5). The director gave the go for
`connect-cells.sh` (sha256 `8907839942b26ed33896c97ad416701de4186f1932eae2144f86e253ce128284`) at M
`045364a835bfb8702b7301e3a71bbbb701cab091`. Run as a login connect on login02 at 0 node-h, 2026-11-04
23:16:21Z–23:16:54Z, in the pinned MAT environment.

**MEASURES:** whether each part B reference that the pilot compares against has E_R's reported-cell set
(hXSec2D > 0, C order). The (2b) and §9.12 controls' `re2_k1.compare` requires `same_cell_set`. **CANNOT
AUTHORIZE:** the pilot, which needs binding 2.

## Result: CELL-CHECK PASS

| product | cells | sha256 = its pin | same set as E_R | atime unchanged |
|---|---:|---|---|---|
| `ER/xsec.root` | 205 | yes (`a5c13fc3…`, E_R's pin) | — | yes |
| `U_MaRES_0/xsec.root` | 205 | yes (`2d4dc33f…`, part B's sums) | yes (none extra, none missing) | yes |
| `S3_BeamAngleX0/xsec.root` | 205 | yes (`b8bf4ac3…`, part B's sums) | yes (none extra, none missing) | yes |

So the §9.12 controls cannot fail on the cell set when the pilot reproduces part B. The full cell lists are in
`cells.log.txt` (its `CELLS` line).

## The run

- The clone at M had porcelain 0. Five blobs were asserted (`blobs`): `cov2d_pilot.py` `cfbe69a7`,
  `cov2d_pseudo_write.py` `e6124ab0`, `re2_k1.py` `62a1dc33`, `re2c_rollup.py` `e41940cb`, `fd_rpd_inputs.py`
  `7c2e018f`.
- Each product was read as an O_NOATIME copy pinned exactly as `cov2d_pilot.ref` pins it: E_R by `pw.PINS["er"]`, the
  other two by `re2c_rollup.partb_sums()`.
- MAT: `run_check_mat_setup` (6 scripts, 0 mismatches) before sourcing; `mat_environment` after (libMAT.so the only
  mapped file; the MnvH1D dictionary present).
- Before the connect, the probe's exact Python ran locally on fixtures. It read a matching set as `same_as_ER` and
  marked a set with one extra cell `CELL-CHECK FAIL` (`only_here [3]`).
- The script was placed at `/dev/shm/josephrb-cov2d-cells.sh`. Its sha256 was compared to the approved value
  (DIGEST_MATCH) in the same invocation that launched it.

## Files

| file | sha256 (as fetched; equal to the node's) |
|---|---|
| `connect-cells.log.txt` (node: `connect-cells.log`) | `08011d2ca710a39c5e865b180fca40c884b78e503f025013c611ce95e980299d` |
| `cells.log.txt` (node: `cells.log`) | `586f5772474dbe9c254785eb58d1218da6213f190796eec1d40c4ee902e0ad3a` |
| `blobs` | `0b80565fa6fa718a22dc0831ac039f50a1901fe001c0ccfc21a734e8114c40fe` |

The `.log` files were renamed `.log.txt` because the repository ignores `*.log`.

## Removals

- In the script: the clone (1.2G) and its tmp, 23:16:53Z, rc 0, both confirmed absent.
- Afterwards (`removal.log.txt`, 23:17:56Z): the work directory and the script (re-hashed before removal, `89078399…`),
  each rc 0. `/dev/shm` then held no `josephrb` entry, and the process listing shows no probe process.
