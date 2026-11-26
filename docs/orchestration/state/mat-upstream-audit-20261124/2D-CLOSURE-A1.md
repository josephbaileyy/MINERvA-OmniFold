# Addendum A1 to 2D-CLOSURE.md: S5's own GEANT sizes, and the per-cell tail (2026-11-24)

Lane: `minerva-lib`. Zero compute, on the Mac. This record **narrows** the verdict of `2D-CLOSURE.md` in this
directory. It does not edit that record, which stays as merged in PR #1298. No index entry outside this
directory points to `2D-CLOSURE.md` (`git grep` at the commit below finds none), so there is nothing else to repoint.
Search: mat-upstream-audit; 2D-CLOSURE (git grep, excluding this directory and MANIFEST.tsv; no hit) @ 75c63def725d17ec829e484a115c41a8720fa2b2

**Narrowed verdict: negligible in the quoted median and integral; NOT negligible per cell in a tail of
cells; unmeasured.**
Search: 3e411c0d; GeantHadronUniverse; GeantNeutronCVReweighter (git grep, excluding this directory and MANIFEST.tsv; no hit) @ 75c63def725d17ec829e484a115c41a8720fa2b2

`closure_2d_a1.py` reads its inputs through `git show` at main `75c63def725d17ec829e484a115c41a8720fa2b2`. Its full
output is in `closure_2d_a1.txt`; every number below is copied from there.

## 1. Inputs and the formula control

| input | path | sha256 |
|---|---|---|
| S5 per-band matrices and total | `docs/orchestration/state/2d-closeout/stageC/production/evidence/production/results/production_cov.npz` | `6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc` |
| Q's recorded sizes | `docs/orchestration/state/2d-closeout/stageF/rebuild/outputs/recompute/recompute_results.json` | `35e00182ec934d678c32185d4fde6406daf406bdd9dca01b5d0110f451a58e03` |
| Q's recorded inputs | `docs/orchestration/state/2d-closeout/stageF/rebuild/outputs/recompute/input_sha256.txt` | `9d6747466ba7f38195b63babb59bf8459e2708a3c50969d56cccdc1909eb6bd9` |
| VL175 per-band sizes | `docs/orchestration/state/2d-closeout/c04-repair/products/budget.json` | `aab8a24ebd61df54e7277999d49300c3bdaa045710835bfa05adf3bfc71dd8fa` |

- **The committed S5 npz is the file Q was built from.** Its sha256 is one of the inputs listed in
  `input_sha256.txt`, and the script checks this.
- **The formula reproduces the recorded values.** Per-cell relative σ is `√C_cc / x_c × 100`, with
  `x = cells_x_EU`. The integral is `√(aᵀCa) / (x·a) × 100`, with `a = area`. Against
  `recompute_results.json`, every difference is at most 8.9e-16:
  - `total`: median 6.040559265, integral 4.328435633;
  - `universe`: median 5.968625171, integral 4.328004839.

## 2. Caveat 1 of 2D-CLOSURE: S5's per-band values against VL175's

| band | S5 median | S5 p84 | S5 max (cell) | S5 integral | VL175 median | VL175 p84 | VL175 max | VL175 integral |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `GEANT_Neutron` | 0.101137 | 0.284412 | 1.346278 (15) | 0.014798 | 0.125545 | 0.292490 | 1.532248 | 0.020422 |
| `GEANT_Pion` | 0.291159 | 1.213715 | 7.849489 (0) | 0.011819 | 0.259702 | 0.998588 | 3.695121 | 0.040644 |
| `GEANT_Proton` | 0.115735 | 0.332186 | 1.308173 (27) | 0.024473 | 0.088865 | 0.198061 | 0.803357 | 0.018279 |

- **For the median and integral, caveat 1 is discharged.** S5's medians are close to VL175's, and the bound
  computed from S5's own values has the same form:
  - **Median:** the quadrature of S5's medians is 0.329236. Removing all three bands gives 6.439489; doubling
    them gives 6.473068. This is still an approximate bound, because caveat 2 stands (§4).
  - **Integral:** exact, because variances add. The summed GEANT matrix's integral is 0.030945. Removing the
    bands gives 4.754879; doubling them gives 4.755282.
  - So the quoted integral of 4.75 is unchanged. The quoted median of 6.45 moves by at most one unit in its
    last digit.
- **In the tails, S5's GEANT bands are larger than VL175's.** `GEANT_Pion`'s maximum is 7.849 in S5 against
  3.695 in VL175, and `GEANT_Proton`'s is 1.308 against 0.803. 2D-CLOSURE's medians did not show this.

## 3. The per-cell tail

G is the sum of the three band matrices. The ratio is G's per-cell σ over S5's total per-cell σ, across the
205 cells.

| GEANT σ / total σ above | cells |
|---|---:|
| 0.05 | 127 |
| 0.1 | 57 |
| 0.2 | 24 |
| 0.3 | 13 |

The median variance share is 0.003597. The largest shares:

| cell | total σ (%) | GEANT σ (%) | ratio | variance share |
|---:|---:|---:|---:|---:|
| 195 | 5.9706 | 2.6392 | 0.4420 | 0.1954 |
| 203 | 7.6832 | 3.1762 | 0.4134 | 0.1709 |
| 193 | 5.3975 | 2.2311 | 0.4134 | 0.1709 |
| 1 | 9.6006 | 3.8224 | 0.3981 | 0.1585 |
| 0 | 20.1229 | 7.9491 | 0.3950 | 0.1560 |
| 194 | 5.9012 | 2.3076 | 0.3910 | 0.1529 |
| 182 | 4.8938 | 1.8351 | 0.3750 | 0.1406 |
| 183 | 5.1478 | 1.9020 | 0.3695 | 0.1365 |

**These shares are against S5's total, not Q.** Q is total + C_PL, so Q's per-cell shares are smaller
wherever C_PL's diagonal is non-zero. C_PL's per-cell values sit in `playlist_term.npz` on CFS. That file is
not committed and was not read. The only tracked `cpl_block.npz` is a 16-cell 5D block, not the 2D C_PL.
Search: playlist_term.npz; cpl_block.npz; C_PL (git ls-tree of tracked .npz paths) @ 75c63def725d17ec829e484a115c41a8720fa2b2

**What this means.** In these cells, a GEANT treatment that follows current upstream practice could move
the cell's σ and its pull by a visible amount. A χ² dominated by these cells could move too. How far the
three bands would change is unmeasured, and the direction is still reasoning only (README §3).
Search: 3e411c0d; GeantHadronUniverse; GeantNeutronCVReweighter (git grep, excluding this directory and MANIFEST.tsv; no hit) @ 75c63def725d17ec829e484a115c41a8720fa2b2

The tail is mostly `GEANT_Pion`. That is the band whose 5D rule K **passes** (`OUTCOME-20261108-1b-precheck-part1.md`).

## 4. Caveat 2 for the median stands

A rigorous per-cell bound on Q's median needs Q's diagonal, so it needs C_PL (§3). The bound that S5 alone
supports is a maximum shift of 1.636616 pp, in cell 0. That is too loose to bound the median, so the median
bound in §2 stays an approximate one.

## 5. What follows

- The geanttw campaign's P3 reading is set per cell, by the director's ruling of 2026-11-24. It reads:
  - the change in σ_c, pinned against patched, for every cell, with the tail cells of §3 named;
  - the change in the median and the integral;
  - optionally, the change in any χ² that compares like with like on our grid.
- It reads **no χ² against the published result.** The published pT edges are 0.075/0.325/0.475, while our
  grid's are 0.07/0.33/0.47. That comparison waits for the matched-edge products, as a declared amendment.
- Nothing here changes Q or any quoted number. The integral claim and the median bound of 2D-CLOSURE stand,
  and only its overall verdict is narrowed.
