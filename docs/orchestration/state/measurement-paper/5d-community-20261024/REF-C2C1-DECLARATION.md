# REF-C2C1 DECLARATION: a binned cross-check of the 2D shape difference (c2), and the joint-test estimator in 2D (c1) (2026-11-04)

**Asked for by** the director, for Joseph. Joseph commissioned "c2 with c1"
(`docs/orchestration/DECISION-20261104-joseph-referee-analysis-commission.md`, merged at `1a87d209a`, item 1). Each
commissioned analysis is declared, audited and bound before it runs, within the standing CPU grant.

**Drafted by** the limitations-catalog lane. Read-only on origin/main `0e1dd76a1`. No jobs, no cluster contact, no
data read. Every path:line below is at that sha unless another is named.

**Designs from:**
- `secondary-results/scope-referee-analysis-20261104/REPORT.md` §4 (#758, `9b1f470c`; "SCOPE §4"): c1 and c2.
- `secondary-results/diagnosis-three-items-20261104/REPORT.md` §B (#760, `0e1dd76a`; "DIAG §B"), whose points B-I
  and B-J the director told this lane to fold in:
  - match E_R's inputs and corrections exactly;
  - freeze the iteration scan and report it in full;
  - never choose the iteration by closeness to the publication;
  - reconcile c1's settings explicitly.

**The run waits** until DIAG §B's B-C component accounting reports (the director's ordering). An upstream defect
found there would change what c2 and c1 should test. B-C may therefore amend this declaration before binding.

**CITABLE FOR:** the designs, the readings fixed before any c2 or c1 output, the licences, admissibility, and the
preconditions.

**NOT CITABLE FOR:** any result, a cause of the 2D difference, any physics claim, a caveat count, or paper wording.
Each result goes to Joseph before any paper text uses it (commission item 4).

## 0. The question, and what is already on record

**The object.** E_R is the adopted 2D result, with Q_R as its headline uncertainty
(`DECISION-20261024-joseph-adopt-re2-2d-refined.md`, item 1). Its distance from the published result is
χ²/ndf = 2.270 against the published covariance (`re2/RE2-PARTC-REPORT.md` §5, the `\chiPaper` row). That value is
465.4153 over 205 reported bins (`re2/run/partc_r2/partc-r2/receipts/figs/tension_report.txt:5, 14`).

**ndf** is the number of bins with a positive diagonal in the published covariance, not a recomputed rank:
`mask = diag > 0`, `n_keep = int(mask.sum())`, `ndf = n_keep` (`2d-unfolding/compare_to_paper_fullcov.py:102-109`).
This distance is descriptive. The two analyses share data and systematics, so it is not a calibrated compatibility
test (DIAG §B1).

**Already decomposed; c2 and c1 do not re-estimate these** (`docs/analysis-note/app_statmethods.tex:536-557`):
- the learner band: exact-split 3.66; HistGBT 2.70 ± 0.04 over 10 seeds; LightGBM 2.65;
- the background treatment: 2.654 (purity) against 2.270 (refined), both LightGBM seed 42;
- the OmniFold iteration count: 5 → 10 moves χ² by +0.01.

c2 asks a different question: whether the distance lives in the inputs and corrections shared by any unfolding of
them, or in the unfolding algorithm. Its readings are not added to the shifts above. χ² is not additive across a
chain (DIAG §B3, B-C), so no reading here is a term in a decomposition of 2.270.

**The existing anatomy is reused, not regenerated.** RE-2's tension receipt on E_R gives:
- diagonal-only 0.29 against 2.270 correlated;
- 9.6 % of the statistic in the 10 smallest modes;
- the largest single mode at 4.8 %.

(DIAG §B1; `RE2-PARTC-REPORT.md` §5.)

## 1. c2: a binned IBU on E_R's own 2D inputs

### 1.1 The estimator (frozen)

| choice | value | source or reason |
|---|---|---|
| algorithm | D'Agostini IBU, `RooUnfoldBayes`, from `unbinned_unfolding/build/libRooUnfold.so` | the library `2d-unfolding/ibu_omnifold_paired_cdelta.py` uses (its docstring, `:10-12`) |
| binning, truth and reco | the published 14 × 16 (p_T, p_∥) grid, `PT_EDGES` and `PZ_EDGES` of `ibu_omnifold_paired_cdelta.py:26-29` | `compare_to_paper_fullcov.py:47-48` (14 × 16), so the output reads through the same comparison code |
| inputs | **E_R's**, unchanged: the same 2D event file, the same signal-MC rows and weights, the same truth denominator, flux, POT and nucleon count, and the same truth definition and phase space | B-I: "the same 2D reco input, background, response, truth definition and corrections as E_R" |
| background | **E_R's refined signed sample:** data at +1 ∪ template at −w_bkg, with the Stay-Positive refinement at E_R's settings (400 trees, 31 leaves, `PB:55`) and E_R's seed, as `2d-unfolding/re2/re2_driver.py --bkg-mode negweight-refined` builds it. It is histogrammed on the reco grid as IBU's measured input | B-I's "same background". IBU-1's template-fold treatment is not used here, because it would change the background, not only the algorithm |
| response and prior | filled from E_R's signal-MC rows with E_R's weights; the prior is the MC truth | as E_R's MC |
| extraction | E_R's own extraction (efficiency, flux, nucleons, POT), applied to IBU's unfolded truth counts | B-I |
| iteration scan | **K ∈ {1, 2, 3, 4, 5, 10, 15, 20}, frozen here, reported in full** | B-I |
| primary K | **K = 10**, the published analysis's count as the paper states it ("ten there, five here", `PB:117`, citing `MINERvA:2021owq`) | SCOPE §4: "the published iteration count read from the published paper". **Confirmed against the publication itself** (arXiv:2106.16210v4, PDF sha256 `39b6b8f1e6a59007ce31f4da4ab1af50dd07b491f537a3bbd898d57e2271ef69`, read 2026-11-04): "Based on these studies, the data was unfolded using 10 iterations." The paper chose it on fake-data χ² over generator variations, "no more than 10" in all of them |
| second fixed K | K = 5, E_R's own count | reported beside K = 10 under the same readings, never chosen between |

**Not chosen by closeness.** No K, binning, background or prior is selected by its distance from the published
result. The rows above are fixed before any output (B-I: "Never choose the adopted iteration by closeness to
published data").

### 1.2 Controls (each must pass, or the run stops and goes to the director)

- **C-SIM (B-I's "reproduce nominal simulation before comparing data"):** IBU on the MC's own reco expectation,
  through the full chain, returns the MC truth cross section to 1e-9 relative in every bin at every K in the scan.
  With prior = truth and measured = R·truth exactly, IBU's fixed point is the truth, so any larger deviation is a
  chain defect.
- **C-REF:** the refined signed sample the c2 code builds reproduces E_R's recorded refinement evidence (the driver's
  `re2Refinement` output, `re2_driver.py:25, 2241`) exactly, so the background is E_R's.
- **C-PUB:** the comparison code, given E_R itself, reproduces 465.4153 over 205 bins to 1e-8 relative
  (`tension_report.txt:14`).

### 1.3 The paired difference

δ = x_IBU − x_E_R on the 224 bins, both through E_R's extraction.
- **Statistical pairing:** IBU runs on the same three-stream bootstrap draws as E_R's replicas (data Poisson, signal
  MC, background stream; `re2_driver.py:21-23`), with the refinement refitted per replica as E_R's is.
  - **Replica set:**
    - The existing Q_R replicas are used if C-DRAW shows their draws regenerate bit for bit from their recorded
      seeds. C-DRAW: one regenerated replica's refined-sample sums equal the recorded ones.
    - Otherwise, 200 new E_R replicas are run (SCOPE §4: 200 × 0.0489 = 9.8 node-h).
  - **Ensemble:** N replicas give δ_r and C_δ = the sample covariance (ddof 1) of δ_r.
- **Universe pairing (optional second pass):** IBU on each universe of `$UNI`, paired with Q_R's E_R universe
  product for the same universe.
  - Q_R's products are reused if they are listed with sha256.
  - Otherwise SCOPE §4's 175 × 0.122 = 21.4 node-h applies.

### 1.4 Readings, fixed before any c2 output

All at K = 10; K = 5 is reported identically. Every other K is printed and read by nothing.

**Operands:**
- **D_X:** χ²/ndf of result X against the published result under the published covariance, by
  `compare_to_paper_fullcov.chi2_with_cov` (ndf = `n_keep`, `:102-109`). D_E_R is 2.270 by C-PUB.
- **ρ = D_IBU / D_E_R.**
- **T_δ:** δᵀ C_δ⁺ δ, with C_δ⁺ the pseudo-inverse truncated to rank r = ⌊N/4⌋ leading eigenmodes (r = 50 at
  N = 200). N replicas cannot support the full 224 bins: the rank is at most N − 1, and the finite-N factor at
  rank 100 is 0.4925 (`BRIEF-20260822-oi137-finite-N-precision-bias-exposure.md:235, 344-350`).
  - **The null for T_δ is empirical, not χ²:** leave-one-out over the N replicas. For each r, T computed on
    δ_r − δ̄₋ᵣ with C_δ⁺ from the other N − 1 replicas, at the same rank.
  - **Bars:** q̂₉₅ is that null's 95th percentile, and max̂ is its maximum.
  - The Hartlap factor (N − r − 2)/(N − 1) is reported as a sensitivity and read by nothing.

**C2-R1, IBU against E_R (gated):**

| T_δ | reading |
|---|---|
| T_δ ≤ q̂₉₅ | **agree** |
| q̂₉₅ < T_δ ≤ max̂ | **marginal** |
| T_δ > max̂ | **differ** |

**C2-R2, localisation (the commissioned reading):**

| condition | reading |
|---|---|
| ρ ≥ 0.75 | **input side**: a binned unfolding of the same inputs sits about as far from the published result as E_R does |
| ρ ≤ 0.50 and C2-R1 = differ | **algorithm side**: on the same inputs, the binned unfolding is materially closer to the published result |
| otherwise | **unresolved** |

The bars 0.75 and 0.50 are declared, not calibrated. ρ is a ratio of two descriptive distances that share every
input.

**Printed beside the readings, read by nothing:**
- per-bin δ in units of √(C_δ)_bb;
- δ projected on RE-2's committed tension modes, if their vectors are recoverable (DIAG §B3, B-M);
- D_IBU at every K;
- the universe-pass C_δ,univ and T_δ with it, if run.

### 1.5 What each c2 outcome licenses

| outcome | licenses | does not license |
|---|---|---|
| input side | narrowing "the source of the shape difference has not been identified" (`PB:94`, as SCOPE §4 quotes it) to "a binned unfolding of the same inputs shows a similar distance". The next step is B-C's per-ingredient accounting | naming an input as the cause; changing a correction, the flux or E_R |
| algorithm side | "on the same inputs, a binned unfolding at the published iteration count is closer to the published result", sized by ρ | calling OmniFold wrong, or switching the 2D estimator; the iteration count or regularisation being "the cause" |
| unresolved | reporting ρ and T_δ as measured | either sentence above |
| any | the result to Joseph, then the paper lane through the PRD read | paper text before that |

Either localising outcome "localises the difference by one level. Neither identifies the cause" (SCOPE §4).

## 2. c1: the joint-test estimator on E_R's 2D inputs

### 2.1 The settings, reconciled (B-J)

E_R and the joint-test estimator (e) already share the following (`PB:55`):
- five OmniFold iterations;
- LightGBM at 100 trees and 8 leaves in both steps;
- the negative-weight subtraction with refinement at 400 trees and 31 leaves.

(e) is "a deterministic LightGBM with the same background treatment and refinement capacity" (`PB:55`). Its
determinism is `s5c_unfold`'s configuration `deterministic` (`nd-unfolding/s5c_unfold.py:17-21, 53-59`):
`bin_construct_sample_cnt` above any row count, `deterministic=True`, `force_row_wise=True`, and a fixed
`num_threads`.

**c1 is E_R's pipeline with exactly those four parameters added** to every LightGBM the OmniFold loop builds.
- Inputs, background, refinement, seed, iterations and extraction stay E_R's.
- The code records every estimator's parameters, as `s5c_unfold.estimator_config` does, and refuses to write
  unless the only difference from E_R's parameter set is those four keys.
- **C-SET:** that recorded diff, printed.
- **C-CV:** with the four keys removed, the c1 code reproduces E_R bitwise.

### 2.2 Products

- one central run;
- 50 paired replicas on the same draws as 50 of E_R's (SCOPE §4: 0.08 + 50 × 0.049 ≈ 2.5 node-h).

### 2.3 Readings, fixed before any c1 output

**C1-R1, (e) against E_R (gated).** T_ef = δᵀ C_δ⁺ δ, with δ = x_(e) − x_E_R, at rank ⌊N/4⌋ = 12. The null is
leave-one-out exactly as C2-R1's, and the bars are the same:

| T_ef | reading |
|---|---|
| T_ef ≤ q̂₉₅ | **equivalent** |
| q̂₉₅ < T_ef ≤ max̂ | **marginal** |
| T_ef > max̂ | **setting-dependent** |

**C1-R2, published comparison (descriptive).** D_(e) beside D_E_R = 2.270, with no bar.

### 2.4 What each c1 outcome licenses

| outcome | licenses | does not license |
|---|---|---|
| equivalent | "the joint-test estimator, run on the 2D inputs, reproduces the 2D central value within its paired noise". This is Sonnet 9's literal request; `PB:55`'s "not combined" could become a measured statement (SCOPE §4, c1) | combining the estimators' results, or any change to E_R or Q_R |
| setting-dependent | "the 2D central value moves with the determinism settings by T_ef", a setting dependence | which setting is right (B-J); replacing E_R ("an adopted 2D replacement is F", DIAG §B3) |
| marginal | T_ef as measured | either sentence |

## 3. Admissibility (both)

- **Post hoc diagnostics, class D (DIAG §B3), declared before they run.** Neither IBU nor (e)-in-2D becomes a
  reported 2D estimator on this evidence. Adopting either would be a post hoc estimator choice, and
  "No hyperparameter search was performed on data" (`PB:57`) would fail.
- **The outcome only is reported.** No follow-up run is made because of an outcome unless a new declaration binds
  it.
- Fixed here:
  - K's scan and primary;
  - the binning;
  - the background;
  - the rank rule;
  - the readings and bars.
- **"Do not jeopardise cov2d's frozen pair"** (DIAG §B4). c2 and c1 read E_R's inputs and products and write
  nothing that cov2d reads.

## 4. Preconditions, compute, calendar

**Before binding:**
1. **B-C has reported.** Any upstream defect it finds is brought into an amendment of this declaration.
2. **The published K: done.** It is 10, confirmed against the publication itself (§1.1).

**Before the run (the cluster lane, 0 node-h; this lane does not connect):**
3. `libRooUnfold.so` is present and loads on the cluster: a listing and an import. Its presence is unverified
   (SCOPE §4).
4. E_R's inputs are listed with sha256, along with its central product and refinement evidence, Q_R's replica
   products with their seeds, and Q_R's universe products (for the optional pass).
5. C-DRAW is run on one replica, to decide between reusing the replicas and running 200 new ones.
6. Reads use O_NOATIME. Nothing is touched to reset exposure.

**Compute** (SCOPE §4, as the commission states them):

| part | CPU node-h |
|---|---:|
| c2, IBU side | ≈ 0 (binned) |
| c2, E_R replicas (0 if reused) | ≤ 9.8 |
| c1 | ≈ 2.5 |
| **cap without the universe pass** | **12.5** |
| universe pass, E_R side (if Q_R's products cannot be reused) | 21.4 |
| **cap with the universe pass** | **33.0** |

The universe pass runs only if the binding says so. No GPU.

**Calendar.** `$UNI`, the 2D universe omnifile, is exposed from **2026-12-19**, with no copy
(`COV2D-SCOPING.md`, the exposure table after `:245`). The universe pass must run before then, or `$UNI` must be
preserved. That is Joseph's decision, through the director. The production flux is exposed from 2026-12-25. `$CV`
and the laterals are on CFS.

**Code (written after binding, pinned in the binding):**
- c2: reuses `re2_driver.py`'s input reading, refinement and extraction, and `RooUnfoldBayes`.
- c1: `re2_driver.py` with `s5c_unfold.config_params("deterministic", threads)` injected.
- Tests: each control's failure and silence, the leave-one-out null on a fixture with a known answer, and the rank
  rule.
- A mutation harness with a mutant per control, bar and pairing key.

**Lane:** ________ (the director assigns). If Joseph's Codex lane takes the 2D shape difference, c2 and c1 move to
it with this declaration (the director's ruling).

## 5. Open for the director before binding

- **C2-R2's bars, 0.75 and 0.50.** They are declared, not calibrated.
- **The rank rule ⌊N/4⌋ with a leave-one-out null.** It replaces #758's "rank cut declared in advance" plus a
  finite-N correction, because the correction is not exact for a truncated pseudo-inverse and the leave-one-out
  null needs no correction.
- **Whether the universe pass is wanted.** It is the only part that runs into the 12-19 date.
