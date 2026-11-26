# Tests A and B: choices declared before any fit or score

Joseph approved tests A and B on 2026-11-26, as `../test1/NEXT.md` describes them. Both are local and use 0 node-hours. This file fixes every fit choice, metric and reading before any A or B model is fitted or scored. Any later change is made in a new commit that says what changed and why, and the original reading is reported alongside.

**What has already been seen.** The held-out playlists are not untouched for these hypotheses. Test 1 printed held-out Data/fold by reco p∥ band and E_avail bin (`../test1/test1.txt`). The full-sample (p∥, E_vis) table (`../test1/evis-by-pz.txt`) covers both halves. Both features tested here were identified in those outputs. What this declaration protects against is choosing the model form, binning or threshold after seeing how a model scores.

## Common to A and B

- **Split.** The same training/held-out split as the existing controls (`prior_fit` in `../score.py`). Training is `1A 1C 1E 1G 1M 1O`; held out is `1B 1D 1F 1L 1N 1P`. Every fit uses training only. The swap (fit held-out, score training) is reported as a secondary result, under the same readings.
- **Prediction.** MC is the all-selected fold of `../score.py` per track, scaled by each playlist's own data/MC POT. This is the same as `../test1/events.py`.
- **"No further freedom".** Every number scored on the held-out playlists comes from parameters fitted on training, with no refit. The only exception is the positive-sign normalization in B, stated there.
- **Variance per scored yield cell.** It is the sum of four terms: the predicted count μ, the MC sum of squared weights, the training-fit parameter variance (linear propagation of the Hessian covariance, diagonal only), and a systematic floor (0.02 μ)². The 2% floor is declared here because the nominal fold already scatters by a few percent against data at reco 20–40 (`../test1/test1.txt`). Results are also printed without the floor, but readings use the floor. Correlated flux, detector and anchor uncertainties are not propagated, so p-values are diagnostic.
- **Cells scored.** Only cells whose held-out fold is at least 5 events are scored. This is decided from MC alone.
- **Outcome words.** Each test reports "supports", "contradicts" or "inconclusive" for its stated hypothesis, using the reading below.

## A. One recoil function for all p∥ bands

**Sample.** Good-curvature (|σ(q/p)/(q/p)| < 0.30) negative tracks. Reco p∥ bands are [20,40), [40,50), [50,60), [60,80) and [80,∞). E_avail edges are −∞, 1, 2, 3, 5, 7.5, 10, 15, 20 and ∞ GeV, giving 9 bins and 45 cells.

**A1, separable form.** The model is μ_ij = a_i · b_j · fold_ij, with b fixed at 1 in the first E_avail bin. That gives 5 + 8 = 13 parameters, fitted by a binned Poisson likelihood on training. An interaction model adds one parameter: μ_ij = a_i · b_j · exp(γ · z_i · e_j). Here z_i = (band mean reco p∥ in training MC − 30)/30, and e_j = ln(1 + bin mean E_avail in training MC / 1 GeV).

**A2, single recoil scale.** Every simulated track's E_avail is multiplied by s, so the MC is rebinned and data are unchanged. The model is μ_ij(s) = a_i · fold_ij(s). The scan grid is s = 0.90, 0.91, …, 1.20, and s and a_i are fitted on training at the grid point with the lowest deviance. Per-band best s_i values are also reported, each with its own normalization and with the range where Δdeviance ≤ 1 taken as ±1σ (minimum 0.005, half a grid step). Their consistency χ² about the common s is printed for information and does not enter the reading.

**Metric.** The held-out Pearson χ², using the declared variance, over the scored cells. The degrees of freedom are the number of scored cells, because nothing is refitted. For the interaction model, γ/σ_γ on training and the held-out Δχ² between A1 and the interaction model (γ fixed from training) are also reported.

**Hypothesis H_A: a single muon-independent recoil function describes the E_avail rise in every band.**
- **Supports:** the A1 held-out p ≥ 0.01, |γ/σ_γ| < 3 on training, and held-out Δχ² < 9.
- **Contradicts:** the A1 held-out p < 0.001, or |γ/σ_γ| ≥ 3 with held-out Δχ² ≥ 9 in the same direction. If γ > 0, that is reported as a recoil slope that steepens with p∥, the high-y/Eν reading in `../test1/NEXT.md`.
- **Inconclusive:** anything else.
- A2 is read the same way, without the γ clause: supports if p ≥ 0.01, contradicts if p < 0.001.

## B. Constant curvature offset against a rate tilt

**Variation.** Every simulated track with fitted curvature (`curv == 1`, finite q/p) gets q/p′ = q/p + ε, in (GeV/c)⁻¹. Both signs are shifted, and a sign change follows from q/p′. The steps are:
1. p_curv′ = 1/|q/p′|.
2. Total momentum p′ = p + (p_curv′ − p_curv) at fixed direction, then p∥′ and p_T′ scale by p′/p.
3. Reapply 0 ≤ p_T′ < 4.5 and p∥′ ≥ 20.
4. Recompute fractional error as σ/(q/p′), with σ fixed.

Range-only tracks and data are unchanged. Tracks below reco p∥ 20 are not in the tables, so the fit starts at 25. The scan grid is ε = −0.0040 to +0.0040 in steps of 0.0001. For |ε| ≤ 0.004, a track needs Δ(1/p) = 0.01 to move from 20 to 25, which keeps entry from below 20 outside the fit range.

**Fit.** Training playlists, negative tracks with E_avail < 1 GeV, all curvature precisions, reco p∥ 25–60 in 2.5 GeV bins (14 bins). The model is k · fold(ε), with ε on the grid and k continuous, fitted by Poisson likelihood. σ_ε comes from Δdeviance = 1, using a parabola through the seven grid points around the minimum. The prediction variance from ε is half the difference between predictions at ε ± σ_ε, squared. The variance from k is (μ/√N_fit)².

**Rate alternative, the same fit with no curvature change.** The model is k · fold · (1 + c · (p∥_reco − 25)/35), applied to every simulated track of either sign, with the weight clipped at zero. The tilt uses reco p∥ as the proxy, matching the observable. Its prediction variance is propagated from ±1σ shifts of c and the relative error of k, both from the training Hessian.

**Scored on held-out, 16 terms, fixed for both models:**
- **S1.** Negative tracks with E_avail < 1 GeV at 40–50, 50–60, 60–80 and ≥80 (4 yields).
- **S2.** Negative tracks, all E_avail, at 40–50, 50–60, 60–80 and ≥80 (4 yields).
- **S3.** Positive tracks, all E_avail, at 40–50, 50–60, 60–80 and ≥80 (4 yields). The positive prediction is normalized to the held-out positive count at 20–40. This is the only quantity taken from held-out data, so 20–40 positives are not scored. Its Poisson error is added to the S3 variance.
- **S4.** The good-curvature fraction of negative tracks at 40–50, 50–60, 60–80 and ≥80 (4 binomial terms, with the MC fraction's statistical variance added and no floor).

**Hypothesis H_B: a constant curvature offset describes the low-recoil excess that grows with p∥.**
- **Supports:** ε differs from 0 by at least 3σ on training, the ε model's held-out p ≥ 0.01 over the 16 terms, and its χ² is at least 9 below the rate model's.
- **Contradicts:** ε is within 2σ of 0, or the rate model's χ² is at least 9 below the ε model's.
- **Inconclusive:** anything else, including both models failing with p < 0.001 within 9 of each other.
- The S1–S4 contributions are printed separately so it is visible which observable drives the result. Under `../test1/NEXT.md`, C is proposed only if B does not support H_B.

## Output

Results go in this folder. One `run.sh` regenerates every output, and every number comes from a committed script. The report gives each test's outcome against these readings.
