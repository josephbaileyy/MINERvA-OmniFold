# 2D playlist-consistency term: REPORT (2026-10-16)

**Answer:**
- **Size.** The block C_PL has a per-cell median relative σ of **2.14%**, at about **0.34× VL175's σ** per cell.
  - p84 3.31%, max 5.69%.
  - Integral 1.97%.
  - p_∥ marginals 1.24–3.36%; p_T marginals 1.17–2.72%.
- **Checks.** Every frozen check passed.
- **Recompute.** A fresh verifier recomputed the block independently from the raw inputs: REPRODUCED, to ≤ 1e-12.

**CITABLE FOR:**
- the size and shape of the block as designed;
- its sensitivities;
- the algebraic reference-scenario numbers;
- the noise share;
- the checks and the independent recomputation.

**NOT CITABLE FOR:**
- adoption. The block is diagnostic until Joseph adopts it at Stage F (checklist J2);
- a coverage claim. A block built from the period differences contains them by construction (DESIGN §4, §6);
- a cause for the inconsistency, or which period is right;
- any budget against the S5 total. That is reported when S5 lands (checklist F9).

| field | content |
|---|---|
| `Design` | [`DESIGN.md`](DESIGN.md): frozen at `c144cdc4` (PR #141), amended before the run at `074051b5` (PR #142) and `769d33e3` (PR #143) |
| `Authority` | [`../../../DECISION-20261015-joseph-playlist-consistency-term.md`](../../../DECISION-20261015-joseph-playlist-consistency-term.md) |
| `Who` | The director wrote the design and the script and ran it. Pre-run review and recompute: two fresh read-only verifiers, Claude Opus 5.5 subagents on the claude-school account, the same model as the director |
| `Compute` | Login node `login04`; 0 node-h; no Slurm |
| `Outputs` | [`outputs/playlist_term.json`](outputs/playlist_term.json) `5b023478…`; [`outputs/run.log.txt`](outputs/run.log.txt) `afe987c3…`. `playlist_term.npz` `c1723cb5…` is gitignored and lives in `/global/cfs/cdirs/m3246/josephrb/2d-closeout-playlist-term-20261016/` (with `SHA256SUMS`) and in `/pscratch/sd/j/josephrb/tmp-playlist-term-20261016/out/` |

## 1. Reviews and run

1. **Pre-run review of `c144cdc4`: APPROVE WITH CHANGES, 1 MATERIAL and 6 MINOR.**
   - The MATERIAL finding: the pre-declared coverage reading could not fail.
   - It was replaced by an algebraic statement, before any number was computed (DESIGN §6).
2. **Re-review of `074051b5`: APPROVE WITH CHANGES, 4 MINOR.** These were text and label fixes, applied in `769d33e3`.
3. **Run** of script `b21d03ce…`. Every check passed:

   | check | result |
   |---|---|
   | pins: scripts, `common.py`, `analysis.json`, `E_U`, `work_cov`, 37 run files | OK |
   | grid equals the `E_U` axes; x against `E_U` | true; 0.0 |
   | populations | 205 cells; 10 draws per period |
   | control: `dr_PB/PA` step / `bias_PB` χ² p_∥ | 0.0694268 / 33.7789, both bit-equal to `analysis.json` |
   | Σ e g; symmetry; min eig / max; rank | 2.9e-16; 0; −2.5e-16; 2 |
   | functional identity | 3.3e-16 |

4. **Independent recompute: REPRODUCED.** The verifier used its own reader and its own code, without reading or importing
   the script. Its outputs are in `/pscratch/sd/j/josephrb/tmp-playlist-term-recompute-20261016/`.

   | quantity | agreement |
   |---|---|
   | C_PL entrywise | 1.3e-16 of max |
   | S_ref | 8.9e-17 of max |
   | S_raw, S_ref_raw | 0 |
   | the 31 functional σ | ≤ 8.9e-16 |
   | χ² | ≤ 1.2e-12 (the largest, p_T against VL175 + C_PL, is near-singular pinv rounding; inferred) |
   | noise shares | ≤ 4.4e-14 |
   | eigenvalues | 4.4e-16 |

   - Its one MINOR finding was wording: the noise draws are taken on r = x/t, not on x. The record now says so (§4).
   - On x, the bootstrap share would be 0.076, not 0.084.

## 2. Results

**The block and its sensitivities.** σ is relative to `E_U`; "ratio" is the median per-cell σ over VL175's:

| block | cell median | p84 | max | integral | p_∥ marginals | p_T marginals | ratio |
|---|---:|---:|---:|---:|---|---|---:|
| **C_PL** (primary: reference-free, double ratio) | **2.14%** | 3.31% | 5.69% | **1.97%** | 1.24–3.36% | 1.17–2.72% | **0.345** |
| S_ref (P_A as reference, dr; the decision's starting candidate) | 1.45% | 2.24% | 4.27% | 1.09% | 0.69–2.24% | 0.65–1.79% | 0.216 |
| S_raw (primary on raw ratios) | 2.41% | 3.99% | 12.48% | 1.99% | 1.73–4.41% | 1.48–3.29% | 0.411 |
| S_ref_raw | 1.55% | 2.88% | 10.44% | 1.08% | 0.94–3.94% | 0.84–2.38% | 0.271 |

- k = V2/(1 − V2) = 0.669, with e = 0.533, 0.295, 0.172 (A, B, C).
- The primary block is larger than S_ref, because it does not assume P_A is right.
- The raw variants have larger maxima in single cells. That is the MC-predicted flux difference the double ratio removes.

**Two modes** (p_∥ marginal, % of `E_U`; sign convention: positive above 8 GeV/c):
- **Mode 1** (eigenvalue ratio 8.2 to mode 2): positive in every bin, 0.1–3.4%. It is largest at 6–8 GeV/c (3.4%, 3.2%), and smallest at 9–10 GeV/c (0.10%). It is broadly a normalization with a p_∥ structure.
- **Mode 2:** −1.2% in the lowest bin (1.5–2 GeV/c), within ±0.8% from 2 to 8 GeV/c, then +1.9%, +2.6% and +1.8% from
  8 to 15 GeV/c. This is the 1G–1M step shape.

**Reference scenario: algebraic, no pass/fail** (χ² in the p_∥ and p_T marginals):

| vector | p_∥ vs VL175 | p_∥ vs VL175 + C_PL | p_T vs VL175 | p_T vs VL175 + C_PL | out of span (Euclid; p_∥ χ² fraction) | first-order bound |
|---|---:|---:|---:|---:|---|---:|
| b_B, dr | 33.12 | 0.68 | 2.85 | 0.56 | 0.8%; 0.07% | 0.683 |
| b_C, dr | 2.86 | 0.31 | 0.81 | 0.24 | 0.6%; 0.08% | 0.340 |
| `bias_PB`, raw (frozen) | 33.78 | 1.98 | 1.96 | 0.60 | 46%; 5.4% | — |
| `bias_PC`, raw (frozen) | 2.62 | 0.40 | 0.62 | 0.21 | 13%; 44% | — |

- **The dr rows sit at their e-only bound**, as the algebra requires. They show that the block contains the reference
  scenario. They are not evidence that it covers it.
- **The raw rows are informative.** They are mostly outside the block's span, but with the block added, the frozen
  `bias_PB` χ² p_∥ falls from 33.8 to 2.0.

**Noise share.** The same estimator was applied to the noise-only draws on r:
- bootstrap: 8.4% of the per-cell variance (median) and 1.9% of the p_∥ marginal variance;
- seed: 0.2% and 0.02%;
- sum: 8.7% and 1.9%.

The noise is not subtracted, which is conservative.

## 3. Limits (DESIGN §3, carried)

- **Three periods.** The spread estimate rests on about 1.83 effective dof. Its relative SE is about 105%, and σ is
  biased low, by about 0.89 at 2 dof.
- **Regularization** may shrink the per-period differences, so the block may be an underestimate.
- **Per-period responses** are used as in the test. Response-modelling errors that differ by period are inside δ_X.
- **The grouping** follows the flux files: 1F is in A.
- **Same-model caveat:** the director and both verifiers are Claude Opus 5.5.

## 4. Next

- **When S5 lands (checklist F8–F9):** the budget with and without C_PL, and the χ² rows against S5 + C_PL.
- **Joseph's review, and with Ben** (agenda item 12): the construction choice (reference-free, against the P_A-reference
  candidate), and the disclosure (draft D5).
