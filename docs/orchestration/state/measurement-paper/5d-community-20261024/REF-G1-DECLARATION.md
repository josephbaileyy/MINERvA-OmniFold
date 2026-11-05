# REF-G1 DECLARATION: a binned unfolding head-to-head on the 16 reporting cells (2026-11-04)

**Asked for by** the director, for Joseph. Joseph commissioned g1, "the 16-cell binned head-to-head"
(`docs/orchestration/DECISION-20261104-joseph-referee-analysis-commission.md`, merged at `1a87d209a`, item 1). The
commission requires each analysis to be declared, audited and bound before it runs, within the standing CPU grant,
using the scope report's designs and prices.

**Drafted by** the limitations-catalog lane. Read-only on origin/main `0e1dd76a1`. No jobs, no cluster contact, no
data read. Every path:line below is at that sha unless another is named.

**The design comes from** `secondary-results/scope-referee-analysis-20261104/REPORT.md` §8 (#758, `9b1f470c`,
`:540-596`; "SCOPE §8" below). The request it answers is Sonnet 8: "a head-to-head comparison against a conventional
binned unfolding (same cells, same data, same systematics), or toning down the motivation" (as SCOPE §8 quotes it,
`:542-543`). This declaration fixes what SCOPE §8 left open: the truth grid, the background treatment, the
pairing, the readings, and what each reading licenses.

**CITABLE FOR:** the design, the readings fixed before any g1 output, the licences, the admissibility conditions and
the preconditions of the run.

**NOT CITABLE FOR:** any result, any physics claim, a caveat count, or wording for the paper. Paper wording from a
g1 result goes through the PRD-referee read and to Joseph before merge (commission item 4).

## 0. What g1 is, in one paragraph

A binned D'Agostini unfolding (IBU) of the same data, with the same simulation, the same background template and
the same weight-only systematic universes as configuration (e), integrated to the same 16 reporting cells R00–R15.
It is placed beside (e)'s committed result. Each of its replicas and universes is paired with the (e) product made
from the same draw or the same weights, so the difference between the two estimators is judged against its own
noise. IBU is a declared cross-check. It never becomes the reported estimator (§5).

## 1. Already on record, and what g1 adds

- **IBU-1** compared binned IBU with OmniFold on the same pseudo-experiments at the 109 J cells. Its verdict was
  UNRESOLVED, with "consistent" at GiBUU and W1–W3 (`2d-closeout/stageF/methods/ibu1/REPORT.md:22-36`). It also
  unfolded the data at the J cells, descriptively (IA-11; `nd-unfolding/ibu1/ibu1.py:478-503`). The 16 reporting
  cells are not in it (SCOPE §8 `:549`).
- **The paper already concedes** that the tests "show no evidence of additional discrimination beyond matched coarse
  projections" (limitation 3, as SCOPE §8 quotes `PB:281`).
- **g1 adds** the reported cells, the data, and the paired systematic universes: Sonnet's "same cells, same data,
  same systematics", with the exceptions listed in §3.4.

## 2. The estimator (frozen)

| choice | value | source or reason |
|---|---|---|
| algorithm | D'Agostini with a known additive reco term, `did.ibu` | reused through IBU-1's `unfold_ibu` (`ibu1.py:173-200`); never re-implemented |
| reco binning | the fine 5D reco cells of `s5e_trace.flat_index` inside IA-7's reco window | IBU-1's (`ibu1.py:96-146`) |
| truth grid | the **H2 coarse cells**, `s5p_stage1_inspect.coarse_map(H2_EDGES)` (`s5p_stage1_inspect.py:77, 261`), empty cells dropped by `did.make_grid` | R00–R15 are unions of H2 cells (`DECISION-20261024-joseph-h2-16-cell-definition.md`), so no truth cell straddles a reporting-cell boundary. Whether IBU-1's J grid nests in R00–R15 is not checked here |
| within-cell spreading | `did.share_matrix` on the nominal truth | IBU-1's (`ibu1.py:195`) |
| prior | the analysis simulation's own truth (Tune v1), full MC × 1 | as (e) and IBU-1's data unit (`ibu1.py:484-485`) |
| iterations | **K = 5 primary**; K ∈ {1, 2, 3, 4, 5, 10, 20} reported in full | IBU-1's declared K (`ibu1/config.json:54-63`), fixed before IBU-1 ran; not chosen here and not chosen on data |
| background, primary | arm N `fold`: the data histogram with the template as the known additive term | IBU-1's N primary (`ibu1/config.json` `variants.N`; `ibu1.py:306-309`), on `s5n_pseudo.build_data` (`s5n_pseudo.py:189`), the same data construction as (e) |
| background, secondary | arm N `sub`: the template subtracted, floored at 0 | IBU-1's N secondary; reported, never read |
| extraction | `xsec_nd.extract_cross_section_nd` | IBU-1's (`ibu1.py:202-212`) |
| cell integrals | Σ_f x_f vol_f over the fine map whose sha256 begins `930326a3` | S1's rule (`s1_assemble.py:10, 120-122`) |
| inputs | `of_inputs_5d.npz` `07fccc1a…`, `bkg_dump.npz` `2addac8f…` | S1's pins (`s1_assemble.py:47-48`) |

**Known and accepted differences from (e)**, to be printed beside any result:
- background: (e) refines the signed sample with Stay-Positive (the refined negative-weight subtraction); IBU folds
  the template as an additive term. SCOPE §8 names this (`:552-553`);
- the algorithm, which is the point of the comparison;
- IBU has no estimator seed and no jitter, so it has no C_seed.

## 3. Products and pairing

| product | IBU side (new, binned) | (e) side (committed, read only) | pairing |
|---|---|---|---|
| data central value | IBU at K ∈ the set, both background variants | the committed central product, sha256 `fb5cc679…` (`s1_assemble.py:49`, `= data_R = P5`) | same data |
| statistical replicas | IBU on (e)'s replica construction, step for step (`s5p_numerics.py:183-200`): `jittered(inputs, bkg, 100+b)` (`:79-87`), then `s5n_pseudo.build_data`, then `s5n_pseudo.bootstrap_replica(exp, b)`, b = 1…50 | S1's `data_b{b}_j{100+b}.npz`, b = 1…50 (`s1_assemble.py:54, 316-319`) | same bootstrap seed b: the same Poisson draws of data, MC and template |
| weight-only universes | IBU with every CV weight replaced by universe u's, as `s5p_universe` does for (e): signal truth and reco weights, truth denominator, template weights; a Flux universe divided by its own flux (`s5p_universe.py:1-23`) | S1's universe products, the declared set of `s1_assemble.EXPECT` (`s1_assemble.py:58-65`) | same universe u, same bank |
| model vertices | IBU on the data with the MC reweighted to GENIE+MEC, NuWro and GiBUU by the ladder's truth ratios, as `build_cmodel5d.py`'s X_k (`pv-ladder/build_cmodel5d.py:4-8`) | the ladder's three (e) unfolds that C_model,5D was built from | same generator truth |
| closure truths (descriptive) | IBU, noise-free, at F0b's truths | F0b's (e) closure products | same truth |

### 3.1 The difference and its covariance

Δ = f_IBU − f_(e) on R00–R15, both as cell integrals.
- **C_Δ,stat:** the sample covariance (ddof 1) of the 50 paired replica differences Δ_b.
- **C_Δ,univ:** S1's estimator for each band applied to the paired universe differences Δ_u: `CalcCovMx`-style,
  mean-centred, 1/N; Flux with the ν-e + IMD constraint weights, centred on the weighted mean; Rvp1pi not a band
  (`s1_assemble.py:11-22`).
- **C_Δ,norm:** (0.014 Δ)(0.014 Δ)ᵀ, S1's normalisation applied to the difference.
- **C_Δ = C_Δ,stat + C_Δ,univ + C_Δ,norm.** Lateral, C_resp and C_PL,5D are not in C_Δ (§3.4).
- **The model block is not in C_Δ.** Both estimators use the same prior, so Δ is defined at that prior. The three
  paired vertex differences Δ_k are printed beside T and read by nothing.

### 3.2 IBU's own covariance, for the precision reading

C_IBU = C_stat,IBU + Σ_b C_b,IBU + C_norm,IBU + C_model_abs,IBU, each by S1's estimator on the IBU products. C_model
is built from the three IBU vertices by `build_cmodel5d.py`'s formula, κ = 1. It has no C_seed.

### 3.3 Controls (each must pass, or the run stops and goes to the director)

- **G-CV:** the IBU universe code with the CV weights reproduces the IBU central product bitwise. This is
  `s5p_universe`'s matched-CV control, carried over.
- **G-pair:** each (e) replica and universe product is the one S1's inventory lists, by sha256 and meta
  (`s1_assemble.py:316-319, 219-238`).
- **G-IBU1:** the driver on IBU-1's J grid reproduces IBU-1's data unit (IA-11, `D_N.npz`, sha256 `a160dbea…`)
  bitwise, meaning array equality (`np.array_equal`) of every array. This shows the grid change is the only change.
  The reference exists only on pscratch, so it is in §7's listing.
- **G-cells:** the 16 cell integrals of (e)'s central product, computed by g1's integration, equal S1's committed f to
  1e-12 relative per cell. Summation order may differ.
- **G-draw:** for each b, g1 calls (e)'s construction path:
  1. `s5p_numerics.jittered(inputs, bkg, 100+b)`, the edge-safe ±½ float32-ulp jitter (`s5p_numerics.py:186`),
     with the loop's refusal if grid membership moves (`:188-191`) applied as there;
  2. `s5n_pseudo.build_data`;
  3. `s5n_pseudo.bootstrap_replica(exp, b)`.

  It compares the per-row arrays bitwise with those g1's own replica builder hands IBU: the keep mask,
  `obs_counts`, the MC Poisson factors and `tmpl_w`. This pins the pairing, including a row within ½ ulp of a
  non-float32 edge, which the jitter step could move across it and so shift every later count. A rebuild without
  the jitter step would compare IBU's construction with itself (coverage-5b-audit, #763 delta check).

### 3.4 Carried, labelled, not remade

| block | why it cannot be remade for IBU | how it is shown |
|---|---|---|
| lateral (5 bands) | the 5D lateral dumps no longer exist; only (e)'s 10 lateral unfolds remain (`FD-1B-DECLARATION.md:99`) | (e)'s lateral block, labelled "(e)'s, carried", in IBU's total only; excluded from C_Δ |
| C_resp | the MP-1 zero loops are needed; exposed 12-15 with no copy (SCOPE §1) | as lateral |
| C_PL,5D | a run-period readout of (e) | as lateral |

"Same systematics" therefore holds for:
- the statistical, universe and normalisation blocks in R1;
- those blocks and the model block in R3.

It does not hold for these three carried blocks, nor for the model block in R1 (§3.1). Any sentence from g1 says
so.

## 4. Readings, fixed before any g1 output

All readings use K = 5, background `fold`, and the 16 cells. Every other K and variant is reported in full and read
by nothing.

**R1. Central agreement (gated).** T = Δᵀ C_Δ⁻¹ Δ over the 16 cells, ndf = 16.
- C_Δ must be positive definite with a condition number below 1e10. Otherwise R1 reads "not formed", with the
  eigenvalues reported, and no cutoff is chosen after the fact.
- **T's null is calibrated at the realized block composition, not taken from χ²₁₆.** C_Δ,stat is estimated from 50
  replicas in 16 dimensions. In the stat-only limit T's null is Hotelling's, (49·16/34) F(16, 34), and χ²₁₆ bars
  would read "differ" about 1 time in 7 when the estimators agree (coverage-5b-audit's audit of #763, B1).
  - The null comes from a parametric bootstrap with **M = 10⁶ draws, seed 20261104** (decision item 2's floor).
    **No step reads the realized Δ.** Write C_Δ,univ = C_Δ,flux + C_Δ,fixed. Each draw:
    1. draws 50 vectors from N(0, Ĉ_Δ,stat) and takes their sample covariance Ĉ*_stat (ddof 1);
    2. draws 100 vectors from N(0, Ĉ_Δ,flux) and forms Ĉ*_flux by S1's Flux estimator: the same 100 constraint
       weights in universe order, weighted-mean-centred (`s1_assemble.py:13-14, 134`);
    3. draws Δ* from N(0, Ĉ_Δ,stat + C_Δ,univ). Under the null the true difference is 0, so the normalisation block
       adds nothing to the draw;
    4. computes T* = Δ*ᵀ (Ĉ*_stat + Ĉ*_flux + C_Δ,fixed + C*_norm)⁻¹ Δ*, with C*_norm = (0.014 Δ*)(0.014 Δ*)ᵀ
       recomputed from the draw's own Δ*, as R1 computes C_Δ,norm from the data's Δ. T* is uncorrected, by the
       production formula.
  - **Which universe bands are sampled** (`s1_assemble.py:58-65`):
    - Flux has 100 PPFX universes, a random sample, so its sampling noise is resampled in step 2.
    - Every other band is held fixed as C_Δ,fixed:
      - 2p2h's 3 universes;
      - each model band's 2 universes, its ±1σ pair;
      - each of the 4 weight-only detector bands' 2 universes.
      These are named, deterministic variations, not draws. S1's estimators use them as given, with no sampling
      model: choice 2, the mean-centred pair estimator, and choice 7, the detector bands, as
      `FD-1B-DECLARATION.md:97-98` cites them. A resampling would invent a distribution S1 does not assume.
  - **Self-check:** with Ĉ_Δ,flux = C_Δ,fixed = 0 and C*_norm dropped, the bootstrap's 0.95 and 0.997 quantiles
    must match (16·49/34) F(16, 34) = 23.06 F(16, 34) within their Monte Carlo error. Otherwise the run stops.
    - Equivalently, the Hartlap T's quantiles must match 29.39 and 46.09.
    - The Monte Carlo error is the binomial order-statistic interval at M = 10⁶.
  - **Order** (decision item 3):
    1. The bars are computed from Ĉ_Δ,stat and Ĉ_Δ,univ alone: replica and universe differences, mean-centred,
       never the central Δ.
    2. They are written to `bars.json`, which the cluster lane commits and pushes, recording the commit and the
       file's sha256.
    3. Only then does the code form the central Δ, and it refuses unless it is given that sha and the file matches
       it.
    4. The bars step refuses if a central-Δ product already exists in the run directory. A Δ formed first stops the
       run.
  - **The stated direction** (decision item 6): the null treats the paired universe differences as scatter in Δ. If
    the two estimators respond to systematics alike, the true systematic scatter in Δ is smaller than the null
    assumes, and the reading leans toward "agree".
- **Bars:** q*₀.₉₅ and q*₀.₉₉₇ are T*'s quantiles.

  | T | reading |
  |---|---|
  | T ≤ q*₀.₉₅ | **agree**: the two estimators' results are indistinguishable at the reported cells within the paired uncertainty (statistical, universe and normalisation blocks) |
  | q*₀.₉₅ < T ≤ q*₀.₉₉₇ | **marginal** |
  | T > q*₀.₉₉₇ | **differ** |

- **Printed and read by nothing** (decision item 5):
  - χ²₁₆'s 26.30 and 35.89;
  - T with the Hartlap factor 32/49 on the C_Δ,stat part, against the F quantiles 29.39 and 46.09;
  - the bars under a stat-only null for Δ (the same bootstrap with Ĉ_Δ,univ = 0 in steps 2–4), labelled
    "sensitivity: stat-only null".

- The per-cell pulls Δ_c / √(C_Δ)_cc are printed for all 16 cells, read by nothing.
- The data-dependence of (e)'s replicas (refit per replica, jitter) is part of C_Δ,stat by construction.

**R2. Closure bias (descriptive, with IBU-1's band).** At each of F0b's truths: the median over the 16 cells of
|f̂/f_true − 1| for IBU over that for (e). "Within" if the ratio lies in [0.5, 2], otherwise "IBU better" or "IBU
worse". This is IBU-1's factor-2 band (`IBU1-SPEC.md:55-60`) carried to the reported cells. There is no noise and no
interval, so it is a point reading.
- (e)'s closures carry estimator-seed noise and IBU's carry none. R2 compares a noisy point with a noiseless one,
  and says so beside the numbers.

**R3. Precision (descriptive).** Per cell, σ_IBU / σ_(e), where each σ comes from the same blocks: stat, universes,
normalisation and model. The carried blocks are excluded from both. Reported: the 16 ratios and their median. No
bar. It answers "does OmniFold give smaller uncertainties at the same cells?" by description only.
- (e)'s C_stat absorbs its estimator noise (refit per replica, jitter; amendment 4 in `s1_assemble.py:11-12`). IBU
  has none, so σ_(e) includes a numerical part that σ_IBU lacks. This is printed beside the ratios.

## 5. What each outcome licenses

| outcome | licenses | does not license |
|---|---|---|
| R1 agree | "a binned unfolding of the same data, cells and weight-only systematics agrees with the reported result within their paired uncertainty", stating that the model block is not in that uncertainty, plus §3.4's three carried blocks | any statement that OmniFold is better, or that it adds information; dropping a caveat; tightening the reported uncertainty |
| R1 marginal | reporting T and the pulls as measured, with no direction | a reading of "differ" or "agree" |
| R1 differ | "the reported cells depend on the unfolding algorithm at the level of T", as a measured estimator dependence, against T's calibrated null | switching to IBU; adding the IBU–(e) difference as a systematic (that is a new block, Joseph's decision); choosing cells, K or a background treatment after the read |
| R2 any | the per-truth readings, beside IBU-1's | a coverage statement for either estimator |
| R3 any | the 16 ratios, descriptively | "OmniFold adds discrimination" (limitation 3 stands unless Joseph decides otherwise on the full record) |
| any | the motivation-wording question (g0) goes to the paper lane with the result attached | paper text without the PRD read and Joseph |

## 6. Admissibility

- **A post-read estimator comparison, declared before it runs.** IBU's data result comes after (e)'s read. It is
  admissible as a declared cross-check only.
- **IBU never becomes the reported estimator** on this evidence. That would be a post hoc estimator choice, and
  "No hyperparameter search was performed on data" (`PB:57`, as SCOPE §0 cites it) would fail.
- **Nothing is selected on data:** K, the truth grid, the background treatment, the cells and the readings are
  fixed here.
- **The outcome only is reported.** No second analysis is run because of the outcome unless a new declaration binds
  it.
- The cells stay R00–R15 as decided. "Cell merges or new cuts after the data read stay inadmissible" (SCOPE §0).

## 7. Preconditions, compute and calendar

**Preconditions (the cluster lane, 0 node-h, before the run; this lane does not connect):**
1. List, with sha256, every (e) product in §3:
   - the central product;
   - the 50 replicas;
   - the universe products of `EXPECT`;
   - the three ladder (e) unfolds;
   - F0b's closure products.

   Each must match S1's or F0b's inventory. List IBU's own inputs with them:
   - `of_inputs_5d.npz`, `07fccc1a…`;
   - `bkg_dump.npz`, `2addac8f…`;
   - the ladder's three truth ratios;
   - G-IBU1's reference `D_N.npz`, `a160dbea…`.
2. List the bank (701 files, `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware/`) and
   the detector dump (33 files, `/pscratch/sd/j/josephrb/s5p-20260926/bank_detector/`) that `s5p_universe` reads,
   with sha256 and atime (`S1-BINDING.md:77-79`). **If either is missing or differs, stop and report to the
   director.** It is not rebuilt here.
   - The 734 files have a verified HPSS copy, `/home/j/josephrb/mnv-5d-s1-inputs-20261024`
     (`S1-PRESERVE-REPORT.md`, PASS).
   - The 12 per-playlist universe loops the bank was built from are exposed on pscratch from 2026-11-09
     (`FD-CT-RETENTION.md:64`). They have a verified CFS copy made since that record
     (`DECISION-20261101-joseph-eventloops-copy-to-cfs.md`, "The copy, verified").
   - (e)'s S1 products are on HPSS as `mnv-5d-s1-products-20261024` (`S1-REPORT.md:495`).
   - No retention record gives the bank's or the detector dump's atime, so their pscratch exposure date is unknown
     until this listing gives it. The HPSS copy is the fallback.
3. Reads use O_NOATIME. Files are never touched to reset exposure.

**Compute:** SCOPE §8 estimates about 1–5 node-h (`:568-570`), from IBU-1's measured 1.0652 node-h
(`ibu1/REPORT.md:180-187`). The universe fill is I/O-bound and unmeasured. **Cap: 5.0 CPU node-h.**
<!-- absence-ok: 'unmeasured' scopes the price of an unrun design (SCOPE §8's own qualifier), not a claim that a result does not exist -->
- The cluster lane times one universe unit first.
- If the timing projects the batch above the cap, it stops and reports. It does not shrink the set.
- No GPU.

**Code (written after this binds, pinned in the binding):** `nd-unfolding/ref_g1/` reuses `ibu1.py`'s World,
`unfold_ibu`, `n_variants` and its digest-pinned producers, with the truth grid as the only change (G-IBU1). Tests
include:
- a real-format fixture through the real parsers;
- each control's failure and silence;
- the readings on hand-checkable vectors.

A mutation harness kills a mutant per reading bar, per control, and per pairing key. It must include:
- the bootstrap's quantiles swapped for χ²₁₆'s (26.30, 35.89);
- C*_norm computed from the realized Δ instead of Δ*;
- the flux block held fixed instead of resampled;
- the self-check skipped;
- the order guard removed, so the central Δ is formed before `bars.json` is committed.

**Lane:** ________ (the director assigns).

## 8. The director's rulings, and the audit

- **R3 stays descriptive, with no bar** (director, 2026-11-04).
- **R1's bars.** The director first accepted χ²₁₆'s 26.30 and 35.89 and said he would take them to Joseph only if the
  audit disputed them.
  - coverage-5b-audit disputed them (B1, #763 comment 6645264150). With C_Δ,stat from 50 replicas, "differ" would
    fire about 1 time in 7 under the null.
  - §4 R1 now reads T against its own calibrated null.
  - **Joseph decided:** "Calibrated by simulation (Recommended)" (sha256 of the text begins `a7ac558c5449d451`).
    This is recorded in `DECISION-20261104-joseph-g1-r1-calibrated-bars.md` (#768, merged at `b6a8c5c3`), with the
    independent consult in `fd/consult-g1-r1-bars-20261104/`. §4 R1 implements its items 2–6:
    - the draws, with M = 10⁶;
    - the order;
    - the self-check and the χ²-swap mutant;
    - the prints;
    - the stated direction.
  - The director's three conditions are met in §4 R1 and §7:
    - C_norm is recomputed from each draw's Δ*;
    - the sampled flux block is resampled, and the deterministic bands are named;
    - the χ²-quantile swap is a required mutant.
