# Playlist-consistency block combined with the S5 production total (Stage F F9): frozen specification

**Owner:** the paper-tighten lane, as director (Stage F, checklist F9). Written 2026-10-17, **before any S5 number was
read**. The closer's S5 message gave only check tallies, digests and paths.

**CITABLE FOR:** how the candidate total S5 + C_PL is formed and checked, and which numbers are reported.
**NOT CITABLE FOR:** any adoption. The combined matrix is a candidate for Joseph's decision (checklist J2). No claim,
KI-85 lift or publication change follows from it.

The block's construction is frozen in [`DESIGN.md`](DESIGN.md), and its values are in [`REPORT.md`](REPORT.md). DESIGN
§4 promised this second report: "the same χ² numbers, against S5 + C_PL; the budget, with and without the block".

## 1. Inputs

| input | pin |
|---|---|
| S5 product `production_cov.npz` | `6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc`, written by the bound `s5_rollup.py` `6c437004`. Identical on pscratch and on CFS `m3246/josephrb/2d-closeout-stageC-production-20261015/results/s5/`. The director re-measured it on 2026-10-17 |
| `playlist_term.npz` | `c1723cb5…`, the REPORT's block |
| `analysis.json`, the period-unfold code and `common.py` | the same pins as `scripts/playlist_term.py` |
| Script | [`scripts/combine_s5.py`](scripts/combine_s5.py), committed before it runs. All four pins, including the S5 product's, are constants in the script. Run with `python3 -I` in root_6_28 on a login node, 0 node-h |

The per-period runs are reloaded through the pinned code only to rebuild the four reference vectors (the raw ones are
not stored in the npz) and the VL175 metric for the control.

## 2. Construction

`Q = S5 total + C_PL`, on S5's 205 cells and its 31 functionals F. Nothing in S5 or C_PL is edited, rescaled or
re-estimated.

## 3. Checks (each a STOP)

0. **Shapes.** Every array read has its expected shape (205, 205×205 or 31×205), checked before any arithmetic.
1. **S5 product.** `total` = `universe` + `stat` + `c08` to 1e-12. Symmetric to 1e-12. Min eigenvalue ≥ −1e-10 × max:
   S5's own frozen PSD tolerance (`s5_rollup.py` `PSD_TOL`), so a total S5 passed cannot stop here.
2. **Alignment.** The npz `cells` equal work_cov's `cells`, which equal the nonzero cells of `E_U`. S5's `cells_x_EU`, the npz `x` and the work_cov `E_U` agree per cell to a relative 1e-12. S5's
   `functionals` and `area` equal the playlist F and its area row to 1e-12 of their max. This closes DESIGN check 5's
   "S5's stored functional map is compared at the S5 report".
3. **Block consistency.** The npz `r_X` equal the reloaded runs' x/t to 1e-12. C_PL rebuilt from them equals the npz
   C_PL to 1e-12.
4. **Combination.** Q is symmetric to 1e-12 and PSD to 1e-10.
5. **Control.** The committed p_∥ χ² rows of `b_PB_dr` and the frozen `bias_PB`, against VL175 and VL175 + C_PL,
   reproduce `outputs/playlist_term.json` to a relative 1e-9.

## 4. Reported (no pass/fail)

- **The budget,** for VL175, S5 universe, S5 stat, S5 c08, the S5 total, C_PL and S5 + C_PL: per-cell relative σ
  (median, p84, max), the integral, the 14 p_T and 16 p_∥ projections, and the median per-cell σ ratio to VL175.
- **The effect of C_PL on S5:** the per-cell σ increase (median, max), the integral and the largest functional
  increase, and C_PL's share of the variance per cell (median) and in the integral.
- **The χ² rows of DESIGN §4,** in the p_∥ and p_T marginals, for `b_PB_dr`, `b_PC_dr` and the frozen raw `bias_PB`
  and `bias_PC`, against VL175, VL175 + C_PL, S5 and S5 + C_PL.
  - The dr rows are bounded by construction and show the algebraic property, not coverage (DESIGN §4, §6 item 1).
  - The raw rows are mostly out of span. They are informative as a sensitivity only: they include the MC-predicted
    flux difference that DESIGN §2 calls legitimate. **No threshold or coverage reading applies to any row.**
  - The "vs S5" and "vs VL175" columns differ by the whole recipe change (c08 replacing the ML seed scan, R5 stat;
    X02, X03 and the background-separable term reported but not added), not by C_PL alone.
- The numerical ranks of the S5 total and of Q, at S5's rcond 1e-10.

## 5. Order and review

1. A fresh read-only verifier reviews this record and the script before they run. Done 2026-10-17: APPROVE WITH
   CHANGES, 1 MATERIAL (the S5 pin was an argument, not a constant) and 5 MINOR, all applied before the first commit.
2. Run, then commit `outputs/combination.json` and the log. `s5_plus_playlist.npz` is gitignored, so it goes to CFS
   with `SHA256SUMS`.
3. A fresh verifier recomputes the reported numbers from the two pinned npz files with its own code.
4. The numbers then go into the disclosures, revision 2 (checklist F10).

**Same-model caveat:** the director and the verifiers are Claude Opus 5.5 on the claude-school account.
