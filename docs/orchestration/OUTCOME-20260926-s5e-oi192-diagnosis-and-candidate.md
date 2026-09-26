# OUTCOME 2026-09-26 — s5e (`OI-192`): diagnosis, one candidate, assessment A_FAIL; campaign CLOSED

**CITABLE FOR:**

- the diagnosis of the 5D estimator's departure failure and of the nominal background bias
  ([`DIAGNOSIS-20260926-s5e-oi192-estimator.md`](DIAGNOSIS-20260926-s5e-oi192-estimator.md),
  independently reviewed);
- the development and assessment of the one justified candidate, `R`;
- the real-data validation of `R`'s estimator and interval, and the costed next validation design.

Every number is from a committed receipt produced by committed code, and was re-measured from operands
by independent reviews: [`state/s5e/diag/review-round-1.md`](state/s5e/diag/review-round-1.md) and
[`state/s5e/cand/review-round-2.md`](state/s5e/cand/review-round-2.md).

**NOT CITABLE FOR:** a coverage validation (the assessment is development scale), an adopted estimator,
covariance or central value, or a measured bias of the real data. Nothing here changes the adopted trunk
`3d7465f6…`, its projection `835828bf…` or any s5c/s5n/Z grade.

Authority: [`AUTHORIZATION-20260925-oi192-estimator-diagnosis.md`](AUTHORIZATION-20260925-oi192-estimator-diagnosis.md).
Campaign: [`CAMPAIGN-s5e-20260925-index.md`](CAMPAIGN-s5e-20260925-index.md). Contract:
`state/s5e/contract.json` with amendments 1–3.

## 1. Diagnosis (summary; the record has the numbers)

- **Pipeline.**
  - The departure failure is the same on the unmodified driver as on the npz path, now measured: E_avail
    EW29 73.8% against 73.5%, EW correlation 0.9998.
  - Driver and npz inputs are identical once the npz's 2,801 −9999-sentinel rows are removed: masks and
    weights bitwise, coordinates at float32 rounding.
  - `KNOWN_ISSUES.md` 79 (1.29% on data) is **not a pipeline defect**. Seeds and dtype are bitwise inert;
    the sentinel mask does not reduce the difference; the difference sits at the estimator's
    rounding-sensitivity floor (≈ 1% max, 0.2% median on data).
- **Departures.**
  - Step 1 fits the reco data and step 2 transfers it faithfully, yet the unfolded result does not reach
    a data-consistent solution.
  - It reproduces ≥ 99.2% (EW projection) of each departure's reco-level signal, while truth residuals
    of median 5–11% and maximum 38–74% remain.
  - The remaining imprint is small relative to the departure but statistically strong at the analysis
    exposure (λ_EW 68–144 for E_avail).
  - Iterations reduce the E_avail residual slowly (−26% from k = 5 to 30, still falling) and increase
    the q3 residual. Capacity improves the reco fit but not the E_avail truth residual. The missed-event
    regressor is not responsible for E_avail.
  - No single cause is named (INCONCLUSIVE). No authorized estimator change passes its predeclared
    screen for the physical E_avail departure.
- **Nominal background bias (`KNOWN_ISSUES.md` 75's residual, s5n C3).** **Cause named:** the
  Stay-Positive refinement classifier underfits at 100 trees / 8 leaves. At 400 / 31 the paired
  background-related bias falls by more than 80% in every worst cell (median 93%). The source/template
  split is excluded.

## 2. Candidate decision (contract amendment 3)

**One candidate: `R`** = B0 (the s5n family N) with the refinement classifier at 400 trees and 31 leaves.
It is a targeted refinement repair, **scoped to the nominal background bias only**. No iteration,
capacity or missed-event candidate was justified: their measured effects on the physical anchor are
partial or absent, and far from the statistical scale.

`R`'s development exit required K1 to pass and the departures not to worsen. That is an explicit,
reasoned change of the campaign-internal screen, frozen before any candidate run. **It was a declared
weakening:** under the contract's original text ("improve on B0") `R` fails development (K2 median 1.002×,
K3 1.035× B0's), as any background-only repair must (review round 2, M4). The departure residual still
gates the qualified scope through A4.

## 3. Development (seeds 700000–702019; receipt `state/s5e/cand/dev_receipt.json`)

| check | result |
|---|---|
| K1 nominal closure, 20 background-inclusive | **PASS**: max \|t\| 2.18, none beyond 3.6. B0 on the same seeds FAILS (max \|t\| 8.6, 56 functionals); paired R − B0 max \|t\| 13.2 |
| K2 GiBUU/GENIE E_avail (a = 1) | median / max \|EW residual\| 10.81 / 73.9% (B0 10.79 / 74.1%): unchanged, as scoped |
| K3 q3 (a = 0.3) | 4.90 / 36.9% (B0 4.74 / 37.4%) |
| K4 seed stability | estimator seed 43 bitwise; row permutations ≤ 1.2e-10 σ |
| K5 calibration (on K1) | pooled pull SD 0.988; 2.0% of functionals outside 1 ± 3 SE; Hartlap Mahalanobis 40.6 in [33.6, 50.4] |

`development_exit` = true; no revision was used.

## 4. Assessment (fresh seeds 800000–805019, withheld W1–W3; receipt `state/s5e/cand/assess_receipt.json`)

| criterion (frozen, amendment 3) | result | verdict |
|---|---|---|
| A1: C3 on 40 fresh nominal background-inclusive experiments | max \|t\| 2.69, none beyond 3.6; EW median \|residual\| 0.02%, max 0.09% | **PASS** |
| A2: calibration | pooled pull SD 1.023 (window 0.9–1.1); 3.9% outside 1 ± 3 SE (≤ 10%); Mahalanobis 43.1 in [33.6, 50.4]; pooled coverage 0.680 / 0.942. **A pooled pass, not per-functional calibration:** 6 functionals lie outside 3 SE against ≈ 0.4 expected, repeating between development and assessment (EW41 pull SD 1.42 with 68% coverage 0.375, J206, J215) | **PASS** (pooled) |
| A3: stability | seed 43 bitwise; permutations ≤ 1.4e-10 σ. **But on the real data an edge-safe float32-ulp perturbation moves the functionals by 0.78 data-σ (median) and 2.58 (max, J145)**; bounds 0.3 / 1.0 | **FAIL** |
| A4: model dependence (withheld W1–W3) | residual median / max over EW: W1 (NuWro E_avail) 6.2 / 31.3%; W2 (GENIE MEC, (E_avail,W)) 1.9 / 16.4%; W3 (NuWro (pT,p‖,E_avail)) 5.7 / 23.7%. **20 of 42 EW cells** have MD within the adopted C_EW σ; the scope depends on the deformations counted (16 with the GiBUU anchor added, 5 with q3 as well). EW41 is in the scope despite its A2 under-coverage | non-empty scope |
| A5: useful width | σ_R / σ_B0 over EW: median 0.98, max 1.49 | **PASS** |

The fresh-seed development anchors reproduce: GiBUU E_avail 10.8 / 73.9% (EW29), q3 4.9 / 36.8% (EW36).

**Verdict: A_FAIL** (A3). `R` repairs the nominal background bias on fresh seeds and its statistical
interval is calibrated at nominal truth. The estimator it shares with B0, however, has a numerical
reproducibility floor on the real data comparable to, and in places larger than, that interval.

- **The failure belongs to the estimator family, not to `R`, and was foreseeable at the freeze.** On
  `R`'s data-σ scale, B0's diagnosis probe gives median 0.80 and max 2.48, the same as `R`'s 0.78 and
  2.58. `R` changes only the refinement, so no `R`-type candidate could meet 0.3 / 1.0 (review round 2,
  M2).
- **It is not established that the data interval misses this noise.** The data-bootstrap σ, which refits
  everything per replica, is 1.57× the pseudo-experiment σ (EW median). The jitter spread matches
  √(1 − σ_pseudo²/σ_data²) ≈ 0.80 data-σ, so that bootstrap may already absorb the numerical spread; data
  behaving as a model departure is the alternative. Next-design item 1 decides it (M3). The A3 verdict,
  a reproducibility limit, is unaffected.
- **No revision was used.** The contract allows revisions only at development, so A_FAIL is terminal. In
  addition, the failing probe is on the real data, so no fresh sample exists to test a revision tuned to
  it. Inflating the interval is excluded by the authorization.
- The plan §6 5% projected-σ stability quantity was not computed (only central-value movement was).

**Real data (same estimator and interval).**

- `R` − B0 method sensitivity: median 0.28%, max 1.58% (J161). The median sits at the rounding-noise level
  (0.78 data-σ); only the tail, at J161 where B0 has its largest nominal bias, reads as a method effect.
- Data-bootstrap σ: median 0.26% relative over EW cells, about 1.57× the pseudo-experiment σ.
- 100 replicas carry the declared background fluctuations (per-event observed Poisson, template
  Poisson(1), MC Poisson(1), refinement refit), and their covariance feeds the correlated check.
- This validates the pipeline. It is not a corrected central value.

## 5. Spend (meter, all admissions closed)

| stage | CPU node-h |
|---|---:|
| diagnosis (3 allocations) | 3.932 |
| candidate development (2) | 2.224 |
| assessment (2) | 4.243 |
| verification (reviews ran on login nodes, read-only; no compute admitted) | 0.000 |
| **campaign total** | **10.399 of 60** |

- GPU: 0.
- Carried-forward envelope: 24.687 (s5c + s5n) + 10.399 = 35.086 of 345.27 CPU node-h.
- Storage: well under the 20 GiB namespace cap.

## 6. Costed next validation design (`state/s5e/cand/next_design.json`; each item a separate decision)

| # | increment | sample size / assurance (measured inputs) | CPU node-h |
|---|---|---|---:|
| 1 | Numerical-reproducibility component on data (the A3 failure): 51 rounding-probe unfolds (per-functional spread to 10%) plus a 200-replica data bootstrap; decides whether the data bootstrap already absorbs the spread, or whether it must be declared as a separate estimator component | n = 1 + 1/(2·0.1²) | ≈ 6.3 |
| 2 | Unfolding-model (regularization) component: departure residuals under generator-anchored truths (GiBUU, NuWro 1D/3D, GENIE MEC, GENIE FSI variants) | the per-experiment spread (≈ 0.3%) is far below 1/3 of the adopted σ, so a few experiments per truth suffice; choosing the truths is the binding question | ≈ 1 (10 per truth × 6) |
| 3 | Convergence study (noise-free, K up to 200, B0 and capacity) | tests whether the E_avail residual keeps falling past k = 30 | ≈ 4–6 |
| 4 | Coverage-grade statistical-scope validation at nominal for the 20 A4-scope EW cells (Tier-S gate, simultaneous 95% Clopper–Pearson, Bonferroni over F × G) | 80% assurance needs n = 11,422 (68%) / 6,418 (95%) at exactly nominal coverage. At the measured minimum per-functional normal-model coverage (0.50 / 0.81, a noisy minimum over 40 experiments) assurance is 0 at any n | ≈ 131 (68%) / 74 (95%), one point; 510 / 287 with two nuisance points |
| 5 | Same for all 42 EW cells / all 153 functionals | n = 13,681 / 17,709 (68%) | ≈ 157 / 204 per point |

Items 1–3 fit the remaining campaign-style envelopes. Item 4 exceeds this campaign's cap and is premature
until item 1 is resolved: an interval that the estimator's own numerical noise exceeds cannot be
coverage-validated.

## 7. Four status fields

| field | value |
|---|---|
| `campaign_disposition` | **CLOSED — diagnosis complete and reviewed; one candidate (`R`) developed (PASS) and assessed: `A_FAIL` (A3, numerical reproducibility floor on data). The bounded objective is met; no estimator qualifies.** |
| `reportable_uncertainty_scope` | **Unchanged.** The 2D standalone covariance (validated) and the `(E_avail,W)` `C_EW` `835828bf…` published under exception with M1–M4 travelling. Neither the background bias (`KNOWN_ISSUES.md` 75) nor the departure (regularization) bias (77) is in any covariance; whether any interval absorbs the numerical floor (80) is not established. No 5D interval carries a frequentist coverage claim, and nothing is adopted. |
| `joint_5d_inference_status` | **NOT PERFORMED** (excluded by the authorization; it also still lacks a qualified covariance). |
| `publication_readiness` | **NOT READY.** The larger publication objective is not met. |
