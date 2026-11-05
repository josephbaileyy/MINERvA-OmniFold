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

**B-C has reported** (`secondary-results/component-accounting-20261104/REPORT.md` (B-C, #769, main `f1a335555`)). It found no new upstream numerical defect requiring a correction to E_R, and the
director released the hold. Its frozen operands, its guard and its scope limits are folded in (§1.0, §1.2, §1.5,
§2.4). The run still waits for this declaration's delta audit and the director's binding.

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

### 1.0 The operands, bound by digest (B-C §1 and §5; the director's instruction after B-C)

B-C is `secondary-results/component-accounting-20261104/REPORT.md` (B-C, #769, main `f1a335555`). It found no new upstream numerical defect requiring a correction to E_R, so the design stands. Its
frozen operands are bound here:

| operand | identity | refused if |
|---|---|---|
| E_R, the adopted central value | object `hXSec2D` of the product with sha256 `a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef` | the digest differs; E_U, the exact-split cross-check, a 1D-projection input or a universe-only CV is substituted |
| E_R's input | CV omnifile `43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df` and baseline flux `d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316` | either digest differs |
| the publication's precision reference | `cov_ptpl_minerva_inclusive_6GeV.root` `6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3`, object `pt_pl_cross_section`, with `StatOnlyCovariance` defining the mask | the digest differs, or the rounded text release is used in its place |
| the reported cells | the 205 indices selected by the receipt's rule, "positive diagonal of StatOnlyCovariance on the paper's 224-bin global grid" (`RECEIPT-agreement-windows.json`, `mask`; the receipt records the rule and the count, not the list). The list is materialised from the bound precision ROOT as a sorted index array and stored as `reported_cells.IDENTITY_HIST` (`2d-unfolding/uq/reported_cells.py:1-19`). It is committed with its sha256 before the run and bound **index by index**: GlobalID = (pT bin − 1)·16 + (p∥ bin − 1) on `hXSec2D`'s [pT, p∥] axes. The precision ROOT has the opposite axis order and is mapped explicitly, as `compare_to_paper_fullcov.py:47` onward does | the index set differs. **Equal counts are not enough.** A publication histogram flattened as if it had our axes is refused, and zero-valued unreported cells are never read as physical zeros |
| the refined target | E_R's signed/refined event sample, the actual refined training target. `hMeasTrain2D` is a purity diagnostic (B-C §2) | C-REF fails (§1.2) |

**Control C-IN:** every digest above is checked, and the index binding is asserted, before any unfold.

### 1.1 The estimator (frozen)

| choice | value | source or reason |
|---|---|---|
| algorithm | D'Agostini IBU, `RooUnfoldBayes`, from `unbinned_unfolding/build/libRooUnfold.so` | the library `2d-unfolding/ibu_omnifold_paired_cdelta.py` uses (its docstring, `:10-12`) |
| binning, truth and reco | **E_R's own grid**: `PT_EDGES` and `PZ_EDGES` of `2d-unfolding/re2/re2_driver.py:44-48` (14 × 16), which equal the paper's `minerva_paper_anc/bin_mapping.txt`. The code asserts this against the bound E_R product's axes | `compare_to_paper_fullcov.py:47-48` (14 × 16), so the output reads through the same comparison code. **Not** `ibu_omnifold_paired_cdelta.py:26-29`, whose p_T edges (0.075, 0.325, 0.475) differ from E_R's and the paper's (0.07, 0.33, 0.47). Its unrun design is not reused for the grid |
| inputs | **E_R's**, unchanged: the same 2D event file, the same signal-MC rows and weights, the same truth denominator, flux, POT and nucleon count, and the same truth definition and phase space | B-I: "the same 2D reco input, background, response, truth definition and corrections as E_R" |
| background | **E_R's refined sample:** E_R's signed sample (data at +1, template at −w_bkg) is refined by the driver's own `refine_stay_positive`, in-process, at E_R's settings (400 trees, 31 leaves, `PB:55`; `random_state` = seed + 3; `re2_driver.py:2198-2209`). That gives every event, data and template, the weight w̃ = \|w\|·max(2g − 1, 0) ≥ 0 (`re2_driver.py:476-519`). IBU's measured input is **Σ w̃ per reco bin**, the refined weights E_R's step 1 consumes | B-I's "same background". IBU-1's template-fold treatment is not used here, because it would change the background, not only the algorithm |
| response and prior | filled from E_R's signal-MC rows with E_R's weights. The response's truth denominator is **E_R's input truth**, the population `hUnfold2D` is defined on (B-C §2, unfolded-yield row). The prior is that MC truth | as E_R's MC |
| extraction | E_R's own extraction, applied to IBU's unfolded truth counts: division by the input completeness `hOFCompleteness2D` (input truth over full truth), flux Φ_i, target count and POT, and the **explicit area Jacobian** ΔpT·Δp∥, then m² → cm² (B-C §2, bin-area and efficiency rows). It never divides by the selection efficiency `hEff2D`, which is diagnostic. Every integral is area-weighted, Σ x·ΔpT·Δp∥, and never a bare sum of bin contents (B-C §1: E_R's area-weighted integral is 3.0687381668997114e-38 cm²/nucleon) | B-I; B-C §5 items 2 and 4 |
| iteration scan | **K ∈ {1, 2, 3, 4, 5, 10, 15, 20}, frozen here, reported in full** | B-I |
| primary K | **K = 10**, the published analysis's count as the paper states it ("ten there, five here", `PB:117`, citing `MINERvA:2021owq`) | SCOPE §4: "the published iteration count read from the published paper". **Confirmed against the publication itself** (arXiv:2106.16210v4, PDF sha256 `39b6b8f1e6a59007ce31f4da4ab1af50dd07b491f537a3bbd898d57e2271ef69`, read 2026-11-04), **page 5**, at the end of the paragraph on the unfolding's fake-data studies: "Based on these studies, the data was unfolded using 10 iterations." The paper chose it on fake-data χ² over generator variations, "no more than 10" in all of them |
| second fixed K | K = 5, E_R's own count | reported beside K = 10 under the same readings, never chosen between |

**Not chosen by closeness.** No K, binning, background or prior is selected by its distance from the published
result. The rows above are fixed before any output (B-I: "Never choose the adopted iteration by closeness to
published data").

### 1.2 Controls (each must pass, or the run stops and goes to the director)

- **C-SIM (B-I's "reproduce nominal simulation before comparing data"):** IBU on the MC's own reco expectation,
  through the full chain, returns the MC truth cross section to 1e-9 relative in every bin at every K in the scan.
  With prior = truth and measured = R·truth exactly, IBU's fixed point is the truth, so any larger deviation is a
  chain defect.
- **C-REF** (coverage-5b-audit, #767 M1). `re2Refinement` records only aggregates (`re2_driver.py:2207-2209, 2241`),
  so it cannot check the per-bin input. Instead:
  - (a) the deterministic aggregates (the signed sum, and the positive and negative event counts) equal E_R's
    exactly;
  - (b) the fitted aggregates (the refined sum and the clipped fraction) agree within RE-2's ≤ 1e-8 relative rule (`re2/RE2-DECLARATION.md:42, 213` @ `5c538db6a`; 1e-8 is the XR frozen-repeat criterion), at E_R's CPU count. E_R's
    LightGBM is not in deterministic mode;
  - (c) the same in-process refinement, passed on through the driver's own OmniFold step, reproduces E_R's `hXSec2D`
    to ≤ 1e-8 relative in every bin, by the same rule. This ties the w̃ that IBU histograms to the w̃ that E_R
    unfolded. It costs one E_R central run (about 0.08 node-h).
  - (d) **per event** (director's ruling on M1): the w̃ that IBU's measured histogram is filled from equals, event by
    event, the w̃ that the driver's own refinement path assigns. The check runs on the real 2D event file, not a
    stand-in.
    - E_R's per-event w̃ are not stored, so the reference is the driver's path (`re2_driver.py:2198-2209`) run
      in-process on the same signed sample; (c) ties that path to E_R.
    - The tolerance is |w̃_c2 − w̃_driver| ≤ 1e-8 × |w| per event, RE-2's rule scaled per event by |w|, because
      w̃ = |w|·max(2g − 1, 0). The clipped (w̃ = 0) sets must be identical.
    - If both sides are run in one process from one fitted classifier, equality is required bitwise.
- **C-PUB:** the comparison code, given E_R itself, reproduces 465.4153 over 205 bins to 1e-8 relative
  (`tension_report.txt:14`).
- **C-BKGSTREAM: the background-bootstrap guard** (B-C §5 item 3; the director's instruction).
  - c2's replicas use E_R's three-stream bootstrap, which includes the background stream (`p1_on`). Only that
    stream refuses signal fakes: `re2_driver.py:1920-1922` for the background histogram and `:2189-2192` for the
    refined injected rows, at `f1a335555`. The central run never exercises it, because E_R's health record has
    `background_stream=false` (B-C §2).
  - A test on the real-format input therefore runs that stream twice:
    - on the input as it is (post-Phase-18, n_fakes = 0), where the guard must stay silent;
    - with one planted signal fake (a `pass_reco & ~pass_truth` row inside the binning), where it must refuse.
  - A mutant removing the guard must be killed.

### 1.3 The paired difference

δ = x_IBU − x_E_R on the 224 bins, both through E_R's extraction.
- **Statistical pairing:** IBU runs on the same three-stream bootstrap draws as E_R's replicas (data Poisson, signal
  MC, background stream; `re2_driver.py:21-23`), with the refinement refitted per replica as E_R's is.
  - **Replica set:**
    - The existing Q_R replicas are used if C-DRAW shows their draws regenerate bit for bit from their recorded
      seeds. C-DRAW: one regenerated replica's deterministic `p1Streams` sums (`re2_driver.py:2244`) equal the recorded ones exactly. The refined sums are fitted, so they are not used.
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
- **T_δ:** δᵀ C_δ⁺ δ, with C_δ⁺ the pseudo-inverse truncated to rank r = ⌊N/4⌋ leading eigenmodes (r = 75 at
  N = 300, the Q_R set; r = 50 at N = 200, new replicas). N replicas cannot support the full 224 bins: the rank is at most N − 1, and the finite-N factor at
  rank 100 is 0.4925 (`BRIEF-20260822-oi137-finite-N-precision-bias-exposure.md:235, 344-350`).
  - **The null for T_δ is empirical, not χ²:** leave-one-out over the N replicas. For each r, T computed on
    δ_r − δ̄₋ᵣ with C_δ⁺ from the other N − 1 replicas, at the same rank.
  - **Bars:** q̂₉₅ is that null's 95th percentile, and max̂ is its maximum.
  - **The null is calibrated by simulation** (coverage-5b-audit, #767 Q1: p = 224, replicas centred on δ_data,
    truncated pinv at ⌊N/4⌋).
    - Rates for "differ": at N = 50, 0.017–0.022 against 1/(N + 1) = 0.020; at N = 200, 0.003 against 0.005.
    - It is exchangeable up to the (1 + 1/(N − 1)) factor on δ_r − δ̄₋ᵣ, which makes it conservative.
    - **So max̂ is about a 2 % bar for c1 (N = 50) and about 0.5 % for c2 (N = 200).**
  - **The null is exact agreement.** "differ" therefore measures whether a difference is detectable at this noise,
    not whether it is large.
  - The Hartlap factor (N − r − 2)/(N − 1) is reported as a sensitivity and read by nothing.

**C2-R1, IBU against E_R (gated):**

| T_δ | reading |
|---|---|
| T_δ ≤ q̂₉₅ | **agree** |
| q̂₉₅ < T_δ ≤ max̂ | **marginal** |
| T_δ > max̂ | **differ** |

**C2-R2, localisation (the commissioned reading; the director's ruling of 2026-11-04 on #767).**
- **ρ on each replica:** ρ_r = D_IBU,r / D_E_R,r on each paired replica r, the same draws on both sides, **all N of
  them** (director, 2026-11-04). The set and N are fixed by C-DRAW (§1.3):
  - if C-DRAW passes: the existing Q_R replica set, N = 300 three-stream replicas (`re2/RE2-PLAN.md:80`, P4), rank
    r = 75;
  - otherwise: 200 new E_R replicas, N = 200, rank r = 50.

  The binding records which set ran and its N. The same N serves C2-R1.
- **The interval:** the central 90 % interval [ρ₀.₀₅, ρ₀.₉₅].
- **The reading:** a class is read only if the whole interval lies inside it; otherwise the reading is
  "unresolved". The point ρ is printed beside it.

| interval lies within | reading |
|---|---|
| [0.75, 1/0.75 = 1.33] | **input side**: a binned unfolding of the same inputs sits about as far from the published result as E_R does |
| ρ ≤ 0.50, and C2-R1 = differ | **algorithm side**: on the same inputs, the binned unfolding is materially closer to the published result |
| ρ > 1.33 | **IBU farther: no attribution**, reported descriptively |
| (0.50, 0.75), or straddling a boundary | **unresolved** |

The bars are declared, not calibrated. The reading is descriptive and licenses no cause (§1.5, §5). ρ is a ratio of
two descriptive distances that share every input.

**Printed beside the readings, read by nothing:**
- per-bin δ in units of √(C_δ)_bb;
- δ projected on RE-2's committed tension modes, if their vectors are recoverable (DIAG §B3, B-M);
- D_IBU at every K;
- the universe-pass C_δ,univ and T_δ with it, if run.

### 1.5 What each c2 outcome licenses

| outcome | licenses | does not license |
|---|---|---|
| input side | narrowing "the source of the shape difference has not been identified" (`PB:94`, as SCOPE §4 quotes it) to "a binned unfolding of the same inputs shows a similar distance". The next step is a per-ingredient comparison, which needs the publication intermediates B-C found missing (B-C §4) | naming an input as the cause; changing a correction, the flux or E_R; **any statement that this analysis's inputs or intermediate stages equal the publication's** |
| algorithm side | "on the same inputs, a binned unfolding at the published iteration count is closer to the published result", sized by ρ | calling OmniFold wrong, or switching the 2D estimator; the iteration count or regularisation being "the cause" |
| IBU farther: no attribution | reporting ρ, its interval and T_δ, descriptively | any attribution to inputs or algorithm |
| unresolved | reporting ρ, its interval and T_δ as measured | any sentence above |
| any | the result to Joseph, then the paper lane through the PRD read | paper text before that. **c2 and c1 compare estimators on this analysis's inputs. Agreement between methods does not show that the upstream ingredients or intermediate stages equal MINERvA's, and a difference does not show that either method is correct** (B-C §5 item 5) |

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

**c1 is E_R's pipeline with exactly those four parameters added to every LightGBM it builds:**
- both OmniFold steps' classifiers and the regressor, through the helper's parameter merge (`omnifold.py:209-220`,
  as coverage-5b-audit traced it);
- **and the refinement classifier.** That one is built separately, by `_make_bkg_classifier` with `refine_params`.
  (e)'s refinement is deterministic: `s5n_pseudo.refine_params` = {`random_state`: seed + 3} plus the same four
  keys (`nd-unfolding/s5n_pseudo.py:61, 234-236`). c1's `refine_params` is therefore E_R's
  ({`random_state`: seed + 3} plus RE-2's 400/31; `re2_driver.py:2201-2204`) plus the four keys.

The rest stays E_R's: inputs, background, seed, iterations and extraction.

**Controls:**
- **C-SET:** the code records every estimator's parameters, as `s5c_unfold.estimator_config` does, including the
  refinement's. It refuses to write unless, in each of the two sets (the OmniFold estimators and `refine_params`),
  the only difference from E_R's is those four keys. The diff is printed.
- **C-CV:** with the four keys removed from both sets, the c1 code reproduces E_R's `hXSec2D` to ≤ 1e-8 relative,
  RE-2's ≤ 1e-8 relative rule (`re2/RE2-DECLARATION.md:42, 213` @ `5c538db6a`; 1e-8 is the XR frozen-repeat criterion), at E_R's CPU count. E_R's LightGBM is not deterministic, so bitwise equality is not required. Wherever both
  sides are deterministic (C-SIM, C-PUB's arithmetic, C-DRAW's `p1Streams` sums, C-SET's parameter diff), equality
  stays bitwise or as stated.

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
| equivalent | "the joint-test estimator, run on the 2D inputs, reproduces the 2D central value within its paired noise". This is Sonnet 9's literal request; `PB:55`'s "not combined" could become a measured statement (SCOPE §4, c1) | combining the estimators' results, or any change to E_R or Q_R; equality with the publication's intermediate stages (B-C §5 item 5) |
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
1. **B-C: done.** No new upstream defect was found. Its operands, guard and scope are folded in.
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

- **C2-R2's bars: ruled by the director on 2026-11-04.**
  - Two-sided: input side is [0.75, 1.33]; a class for ρ > 1.33, "IBU farther: no attribution"; algorithm side is
    ρ ≤ 0.50.
  - Read only if the replicas' 90 % interval lies inside the class.
  - Declared, not calibrated: the reading is descriptive and licenses no cause, and the licences are unchanged.
- **The audit (coverage-5b-audit, #767):** the leave-one-out null was found calibrated (Q1). M1, M2 and M3 were
  upheld by the director and are answered:
  - M1: C-REF (a)–(d), with a per-event w̃ control on the real input;
  - M2: c1's deterministic `refine_params`, enforced by C-SET and C-CV;
  - M3: RE-2's 1e-8 rule, cited, wherever E_R's non-deterministic LightGBM is the reference.
- **The rank rule ⌊N/4⌋ with a leave-one-out null.** It replaces #758's "rank cut declared in advance" plus a
  finite-N correction, because the correction is not exact for a truncated pseudo-inverse and the leave-one-out
  null needs no correction.
- **Whether the universe pass is wanted.** It is the only part that runs into the 12-19 date.
