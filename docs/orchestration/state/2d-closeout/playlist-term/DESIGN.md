# 2D playlist-consistency term: DESIGN (frozen before any number is computed), 2026-10-16

**Issued by** the paper-tighten lane, as director. It carries out
[`../../../DECISION-20261015-joseph-playlist-consistency-term.md`](../../../DECISION-20261015-joseph-playlist-consistency-term.md)
§2, which requires these to be declared before computing:
- the construction;
- raw or double ratio;
- the reference period;
- how 1F and the per-period MC responses are handled.

The decision also requires a fresh read-only verifier to check the design before any number is quoted.

**CITABLE FOR:**
- the construction of the playlist-consistency block, its inputs, its frozen checks, and what it reports;
- the order: this DESIGN, then a verifier on the DESIGN and the script, then the computation, then a verifier on the
  numbers.

**NOT CITABLE FOR:**
- any number. None has been computed under this DESIGN. The term's size is unknown as this record is written;
- adoption. The block stays diagnostic until Joseph adopts it at Stage F;
- a cause for the inconsistency, or which period is right;
- compute. The computation runs on a login node and reads existing products, at 0 node-h.

## 1. Inputs (existing, pinned)

| input | identity |
|---|---|
| per-period unfolds, seed 42 | `pu_PA_s42`, `pu_PB_s42`, `pu_PC_s42` `xsec.root` under `/pscratch/sd/j/josephrb/2d-closeout-period-unfold-20261014/out/`, with the sha256 recorded in [`../period-unfold-20261014/outputs/analysis.json`](../period-unfold-20261014/outputs/analysis.json) `_runs` |
| seed-43 and bootstrap draws | `pu_X_s43` and `pu_X_b01–b10`, same record. Used only for the noise reference (§4) |
| pooled control | `pu_CTRL_s42`. It reproduces `E_U` to 3.0e-13 (period-unfold REPORT §1) |
| central value | `E_U` `4f5a1b6d…` (the `periods.py` pin). The vector x is read from `work_cov.npz` `EU`. Check 5 requires it to equal the pinned ROOT file's `hXSec2D` on the 205 cells |
| VL175 covariance | `work_cov.npz` `70c4daf2…`: `hCov_combined` + `ML`, the metric of the period-unfold analysis |
| loader and metric | the deployed `analyze_periods.py` `912af1dd…` and `periods.py` `d37c1a8f…`, imported unchanged: `load()` gives x, t, φ and POT per period; `Metric` gives the projections and χ². `common.py` `dcb78c52…` (`area`, `proj_matrix`, `mahalanobis2`, `cell_ipt_ipz`) is pinned too |

If any pin or sha256 differs, the script stops and writes no product.

## 2. Construction (frozen)

**Quantity: the double ratio.** For each period X ∈ {A, B, C} and each of the 205 cells:
- r_X = x_X / t_X, the unfolded data over that period's own MC truth.

  The MC truth t_X carries X's flux, POT, completeness and nucleon count, through the producer's formula.
- The double ratio removes the difference between periods that the MC predicts from their different fluxes. That
  difference is legitimate, because each period measures a cross section averaged over its own flux. The MC-truth
  ratio B/A is +1.48% in the integral, with a +3.13% step (period-unfold REPORT §2).
- The raw ratio would count that predicted difference as an inconsistency. So **dr is primary, and raw is reported as
  a sensitivity only.**

**Reference: none. The construction is reference-free.**
- The data cannot tell which period is right (playlist-spread REPORT; the decision's NOT CITABLE). So no period is
  treated as truth.
- **Model:** each period's result carries an unexplained offset δ_X of unknown cause. The offsets are treated as
  exchangeable draws with a common variance. The pooled result's error from them is δ̄ = Σ_X e_X δ_X.

**Estimator.** These are the unbiased reliability-weighted estimates, written per cell and as outer products over cells:
- e_X is the exposure share already used by the test (POT_X Φ_X(p_T) / Σ_Y POT_Y Φ_Y(p_T)). It is about 0.533, 0.295 and 0.172.
- m = Σ_X e_X r_X, the exposure-weighted mean double ratio.
- g_X = r_X / m − 1, so that Σ_X e_X g_X = 0 exactly.
- V2 = Σ_X e_X², per cell (constant here, because e does not vary with p_T).
- **C_PL = Σ_X [V2 / (1 − V2)] e_X (x ∘ g_X)(x ∘ g_X)ᵀ**, with x = `E_U` on the 205 cells.

  V2/(1 − V2) is per cell. If e varied by cell, the factor would enter as diag(√k) on each side, k = V2/(1 − V2).
  The rank ≤ 2 claim would then fail, and check 3 would stop the run. The test's e is identical in all 14 p_T rows.

This is the variance of the exposure-weighted mean of three exchangeable offsets, with the offsets' variance taken
from their weighted spread about that mean. By construction it is symmetric and PSD, with rank ≤ 2.

**Sensitivities, reported and never used as the block:**
- **S-ref** (the decision's starting candidate): Σ_{X∈{B,C}} b_X b_Xᵀ, with b_X = e_X (r_X / r_A − 1) ∘ x. It treats
  P_A as right, and the B and C offsets as separate sources;
- **S-raw:** the primary construction, with x_X in place of r_X;
- **S-ref-raw:** S-ref with x_X. Its b_B equals the frozen `bias_PB` vector of the test.

## 3. 1F, the grouping, the MC responses and regularization

- **Grouping.** The periods are those of the test: A = 1A–1F, B = 1G/1L/1M, C = 1N–1P. They follow the flux-file
  grouping of the code (`periods.py` docstring: 1A–1F use the 1D flux, 1G/1L/1M the 1M flux, 1N–1P the 1N flux).
  They were not chosen from the data. **1F stays in A**, because it shares A's flux file. The reco-level reference
  1A–1E was a data-driven choice of the earlier spread look, and it is not used.
- **MC responses.** Each period is unfolded with its own MC response, as in the test. That is the correct per-period
  treatment, so there is no adjustment. The double ratio removes MC-truth differences, but not response-modelling
  errors that differ by period. These would show up as part of δ_X, which the term carries.
- **Regularization.** At 5 iterations, each period may be pulled toward its own prior. That would shrink the observed
  offsets, so the term may be underestimated on this count. This is disclosed and not corrected.
- **Three periods.** The offsets' variance rests on 2 degrees of freedom; with these unequal e, the effective number
  is about 1.83. Its own relative SE is therefore of order 100% (about 105%), and the implied σ is biased low, by
  about 0.89 at 2 dof. This is disclosed. It is not inflated or shrunk.
- **Noise.** The period results carry their own statistical and seed noise, and the pooled stat block already covers
  the pooled share of it. The term does not subtract it, which is conservative. Its expected share is reported (§4).

## 4. Frozen checks (each a stop) and reported numbers

**Checks:**
1. Every pin and sha256 in §1.
2. **Control.** The script's own loader and metric recompute, from the same inputs, the frozen values in
   `analysis.json`, each to a relative 1e-9:
   - `dr_PB/PA` step: +6.94%, `analysis.json` `comparisons.dr_PB/PA.step.value`;
   - `bias_PB` χ² p_∥: 33.78, `comparisons.bias_PB.chi2_pz_marginal`.
3. **Identity.** Σ_X e_X g_X = 0 to 1e-12 per cell. C_PL is symmetric to 1e-12, and its min eigenvalue is ≥ −1e-12 ×
   max. Its numerical rank is ≤ 2 at rcond 1e-12. The symmetry check holds exactly by construction (a sum of
   outer products), so it guards only against a code change. The PSD and rank checks can fire.
4. **Functional identity.** For the 31 functionals F (the S5 map: the area-weighted integral, 14 p_T and 16 p_∥
   projections, built from `common.py` `area` and `proj_matrix`, which use the same orthogonal-bin-width
   convention), F C_PL Fᵀ equals the same estimator built from the projected vectors F(x ∘ g_X), to 1e-10
   relative to its max. This is a linear-algebra identity, so it cannot detect a wrong F. Check 5 tests F's inputs.
5. **Grid and central value.** The pinned `E_U` ROOT file's `hXSec2D` axes equal `common.py` `PT_A`/`PZ_A`, so F's
   bin widths are the result's own. Its `hXSec2D` on the 205 cells equals `work_cov` `EU`, to a relative 1e-12.
   S5's stored functional map is compared at the S5 report.
6. **Populations.** `work_cov` has exactly 205 cells and none is dropped. Each period has exactly 10 bootstrap
   draws, matching `analysis.json` `n_boot_pairs`.

**Reported (no pass/fail):**
- per-cell relative σ (median, p84, max), and the σ of each of the 31 functionals, for C_PL and for each sensitivity;
- the noise share: the same estimator applied to noise-only inputs. It replaces each period's g_X with that period's
  fractional bootstrap draw d_X,k, minus the e-weighted mean of the draws.
  - The bootstrap covariance is the mean over the 10 draws k. The seed covariance uses s_X / √2.
  - Each share is the median over the 205 cells of the noise covariance's diagonal over C_PL's. Likewise for the
    16 p_∥ marginal bins.
  - It is reported for the bootstrap, the seed and their sum. The sum may count part of the seed noise twice, if the
    bootstrap replicas already carry training noise; the test's noise model has the same feature;
- **the reference scenario, as an algebraic property, not a coverage test:**
  - the χ² of b_B and b_C (dr, S-ref) and of the frozen `bias_PB`/`bias_PC` (raw), in the p_∥ and p_T marginals,
    against VL175 alone and against VL175 + C_PL;
  - to first order, b_X(dr) = e_X(u_X − u_A) with u_X = x ∘ g_X. That lies in C_PL's span, so its χ² against
    VL175 + C_PL is bounded by an e-only constant, bᵀC_PL⁺b = cᵀM⁻¹c, whatever the data. This bound is printed
    beside the observed values;
  - the fraction of each b outside C_PL's span (Euclidean, and in the VL175 metric);
  - there is **no pass/fail reading**. A block built from the period differences contains them by construction. A real
    coverage statement would need an estimate that is not built from the same three vectors, and none exists. The raw
    rows are not in the span, so they are informative;
- C_PL's two eigenmodes, as p_∥ and p_T marginal shapes. The sign convention makes each mode's p_∥ marginal
  summed over [8, 15) GeV/c positive;
- the median ratio of C_PL's per-cell σ to VL175's.

A second report, against the S5 total, follows when S5 lands (Stage F checklist F9):
- the same χ² numbers, against S5 + C_PL;
- the budget, with and without the block.

## 5. Products and order

- **Script:** `scripts/playlist_term.py`, committed before it runs. It is run with `python3 -I` in the root_6_28
  environment on a login node.
- **Outputs:** written to `/pscratch/sd/j/josephrb/tmp-playlist-term-20261016/`:
  - `playlist_term.npz`: C_PL, the sensitivities, the g_X and e_X, the cells, x, and F;
  - `playlist_term.json`: every check, every number, and the input sha256s.

  The outputs are copied into `outputs/` with their sha256.
- **Order:**
  1. this DESIGN on `main`;
  2. the script;
  3. a fresh read-only verifier reviews the DESIGN and the script, and checks whether the script implements §2–§4. One
     review, at most two focused re-reviews;
  4. the run;
  5. a REPORT;
  6. a fresh read-only verifier recomputes C_PL independently from the same inputs, before any number is quoted to
     Joseph.
- **Delegation.** Each verifier runs on a permitted account (claude-school, codex-school, codex-school2 or agy), as Joseph
  ruled on 2026-10-16.

## 6. Amendments before the run (2026-10-16)

The pre-run verifier gave APPROVE WITH CHANGES on `c144cdc4`: 1 MATERIAL and 6 MINOR. No number had been computed.
This record was amended in place, and the script with it:
1. **MATERIAL.** The pre-declared reading "covers if χ² ≤ 4" could not fail. The dr reference vectors lie in
   C_PL's span to first order, so their χ² is bounded by an e-only constant of about 0.68. The reading is removed and
   replaced by the algebraic statement, the bound, and the out-of-span fractions (§4).
2. Check 4 is relabelled as an identity, and check 5 (grid and central value) is added. The symmetry check is noted as
   holding by construction.
3. `common.py` is pinned (`dcb78c52…`). The director re-measured it on the committed copy.
4. The noise-share wording now matches the code. The possible double count in the sum is disclosed.
5. Check 6 (populations: 205 cells, 10 draws per period) is added.
6. Precision: x comes from `work_cov` and is checked against `E_U`; the rank caveat for per-cell e; the effective dof
   and the σ bias.
7. The eigenmode sign convention.

The construction (§2) and the choices of §3 are unchanged.
