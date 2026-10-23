# Coverage scoping for a measurement paper: which dimensionality, which intervals, at what cost (DRAFT, 2026-10-22)

**By** the validation lane, under its brief
([`../2d-closeout/stageF/lanes/VALIDATION-LANE-BRIEF.md`](../2d-closeout/stageF/lanes/VALIDATION-LANE-BRIEF.md),
task 2), for Joseph through the director. **0 node-h**: this memo reads committed records, plus read-only `iris` and `sinfo` listings and
the public MAD branch documentation (2026-10-23, §4).

**Status: DRAFT for Joseph.** IBU-1 has reported (verdict **unresolved**;
`O/state/2d-closeout/stageF/methods/ibu1/REPORT.md` §1, PR #277, unmerged when this was written). Its readings are
carried into §1, §4.1 and §5. Everything else is final from the records. **This memo proposes; it
decides nothing.** Any scope, claim, estimator or interval change is Joseph's.

**CITABLE FOR:** what has and has not been measured about statistical-interval coverage at each dimensionality, the
routes on record with their costs, and a proposed order of cheap decisive tests.
**NOT CITABLE FOR:** any coverage result, any new measured number other than the allocation and node listings in §4,
or a decision.

`O/` = `docs/orchestration/`. Every fact carries its record; an inference is marked **(inference)**.

## 1. The answer in brief

1. **No interval construction at any dimensionality has passed a coverage test.**
   - 5D has failed every route tried.
   - 2D has one failed test: the old band undercovered, from its width.
   - 3D and 4D have never been tested.
2. **At 5D on the J cells the obstacle is the inverse problem, not the classifier, as far as the evidence reaches.**
   - The boosted-tree residual equals exact binned IBU's at K = 5.
   - The label-stable J functionals are weakly identified, with binned Cramér–Rao widths of median 31% at the coarse
     truth grid against a 10% target (D-ID, `O/state/next-preparation-20261009/d-id/REPORT.md:419-421,514-536`).
   - Prior-free strict bounds fail at 28.6% (`O/state/measurement-paper/phase1/mp4a/REPORT.md:19-27`).
   - IBU-1 extends this to noise, background and both background constructions at the generator-sized departures.
     At GiBUU, W1, W2 and W3, exact binned IBU's residual is 0.77–1.31 × OmniFold's, each read "consistent". Its own
     400-seed statistical intervals cover the median J functional in none of the experiments at GiBUU, W1 and W3
     (`O/state/2d-closeout/stageF/methods/ibu1/REPORT.md` §1, §4).
   - IBU-1's formal verdict is **unresolved**, because the rate change (tilt) is unresolved; the rule leaves
     "inverse-problem limited" and "mixed" open, and excludes "implementation specific".
3. **The cheapest decisive step is an identifiability ladder.** It uses the existing D-ID and MP4-A code, locally, at
   about 0 node-h: binned Cramér–Rao and strict-bounds widths for natural reporting cells at 2D, 3D, 4D and the 5D
   (E_avail, W) cells. It says which dimensionality can even in principle carry ≤ 10% prior-free statistical
   intervals.
   - Since IBU-1 reads "consistent" at every generator-sized departure, a binned-IBU coverage pilot at the top passing
     dimensionality, at under 1 node-h, is the next filter, before any OmniFold coverage spend **(inference: the
     formal verdict is unresolved only at the rate change)**.
4. **The 2D measurement has the shortest path to a tested statistical interval:** a 7.4 node-h held-out calibration of
   the quoted band. It needs Joseph to lift the KI-85 deferral.
   - Total (statistical plus systematic) coverage is not affordably testable at any dimensionality on the record.
5. **On its own, the negative-weight background treatment (configuration (e)) is not a route to validated 5D coverage
   on the record (§4.1).**
   - It repairs what the background causes: the nominal bias, and the pooled calibration at nominal truth.
   - The departure failures are not caused by the background. They persist with no background, signal-only
     experiments reproduce them, and exact binned IBU leaves the same residual.
   - (e)'s own intervals have already been measured at development scale: pooled 68% coverage of 0.017–0.157 at five
     departed truths.
   - IBU-1 confirms it at W1–W3: exact binned IBU leaves (e)'s own residual to within a factor 2 on (e)'s own
     assessment seeds (ratios 0.93, 1.31 and 0.93).
   - One cheap test, ≈ 0.3 CPU node-h, would confirm this on (e)'s own path at the KI 98 rate change before anything
     larger is considered. After IBU-1 it is optional (§4.1).
6. **Reopening PET is not justified on the record, but its one open premise is cheap to test (R10, §4.2).**
   - A better classifier on the same five reco scalars cannot help: the GBDT already leaves the residual exact binned
     IBU leaves.
   - More reconstructed information might help. A 2× finer reco binning alone brings the binned J floor to the edge
     of the 10% target (MP4-A §6a), but that figure is optimistic about response-MC noise.
   - A binned test on D-ID's setting, with finer reco bins and one or two added reco variables from the tuples,
     costs a few local core-hours plus ≤ 3 CPU node-h for extraction. It says whether a GBDT run with extra reco
     features is worth making. A PET run comes only after that.

## 2. What is measured, by dimensionality

| dim | coverage tested | result | what is missing | record |
|---|---|---|---|---|
| **2D** `(pT, p∥)` | VL169: the VL162 statistical band, fixed MC truth, 100 toys, 205 bins | 68%: 0.679, inside its window. 95%: **0.912**, below [0.928, 0.972]. **FAIL**, "width, not bias" | The band now quoted (S1, seed 42) is **untested**; so are VL170, systematic and total coverage, and the adopted Q = S5 + C_PL ("NOT CITABLE FOR … a coverage, calibration or validation statement") | `VALIDATION_LEDGER.md:95`; `KNOWN_ISSUES.md` rows 84–85; `O/DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md:23,28` |
| **3D** `+E_avail` | none | — | everything: no coverage test, route or unit cost specific to 3D exists | `3d-unfolding/3D_OMNIFOLD_STATUS.md` (searched); `O/CAMPAIGN-s5c-20260924-index.md:68` |
| **4D** `+q3` | none | — | everything. The 5D estimator carries q3-direction distortions: under the q3 stress, pooled 68% coverage is 0.027 | `nd-unfolding/ND_OMNIFOLD_STATUS.md:167`; `O/OUTCOME-20260925-s5n-stage1-development-fail.md:58,79-80` |
| **5D** `+W` | s5c Tier S: bias-corrected statistical intervals, 153 functionals, 400 seeds at nominal, rate change and q3 | nominal futile 0/2 (68%/95%); **rate change 51/42**, min coverage 0.060; **FAIL (futility)**, reproduced | the uncorrected intervals ("predicted … to undercover worse"); total coverage; any interval of the adopted trunk | `O/OUTCOME-20260925-s5c-tier-s-futility-fail.md:7-8,30-37` |
| 5D | s5n stage 1 (negative-weight background), 60 seeds | GiBUU pooled 68% coverage **0.027**; q3 0.027; nominal 0.603 | — | `O/OUTCOME-20260925-s5n-stage1-development-fail.md:56-58` |
| 5D | s5e candidate R (= configuration (e)), 40 nominal plus 20 at each of five departures, uncorrected f̂ ± σ | nominal pooled 0.680/0.942, pooled pass only; EW41 0.375; numerical floor FAIL. Departures, pooled 68%/95%: GiBUU 0.024/0.044, q3 0.019/0.036, W1 0.025/0.045, W2 0.157/0.300, W3 0.017/0.030 | per-functional calibration; any coverage-grade n | `O/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md:80-87`; `O/state/s5e/cand/assess_receipt.json` → `points.*.pooled_cov68/95` |
| 5D | MP4-A strict bounds (width, not coverage), noise-free, signal-only | J median **28.59%**, p90 120.8%, against 10%/25%. **FAIL** | the unbinned-information loophole is "material": a 2× reco refinement gives a J floor of 9.7–10.8%, unsized for response-MC noise | `O/state/measurement-paper/phase1/mp4a/REPORT.md:19-27,133-146` |

## 3. Why the 5D intervals fail (mechanisms and their status)

| mechanism | status | record |
|---|---|---|
| purity-background closure bias, −3.5 to −4.1% at the highest W | established; the within-bin mechanism is inferred | `O/OUTCOME-20260925-s5c-purity-background-bias-at-high-W.md:25-28,42-45` |
| a σ that does not resample background (pulls 1.16× wider) | established | `O/OUTCOME-20260925-s5c-tier-s-futility-fail.md:45-47` |
| the nominal-truth correction does not transfer under the rate change: a W-graded bias of 1.3–2.6σ | established (a 400-seed read confirms the inferred table) | `O/state/2d-closeout/stageF/methods/M2-RATEFAIL-DIAGNOSIS.md`; `O/state/ki98-wbias-test/REPORT.md` |
| source of that W-graded term (B/S vs estimator) | **UNDETERMINED** | `O/state/ki98-wbias-test/REPORT.md:4,55-66` |
| regularization bias under generator-sized departures (E_avail median 9.7%) | established as the estimator's | `O/OUTCOME-20260925-s5n-stage1-development-fail.md:75-89` |
| weak identifiability of the J cells for binned estimators (D-ID branch C) | supported, at binned, signal-only, noise-free scope | `d-id/REPORT.md:514-536` |

**(inference)** The common thread is bias that a nominal-truth correction cannot remove, in directions the data barely
constrain. Coverage then fails at departures whatever the width. That points at identifiability per reported cell as
the quantity to scope, which is cheap to compute.

## 4. Routes, each with its decisive cheap test and cost

Costs are from the record; derived numbers are marked **(inference)**. The measured 5D unit is 0.0104–0.0148 CPU
node-h per OmniFold pseudo-experiment (`O/FEASIBILITY-20260925-s5c-scalar5d-measurement-and-inference.md:21`) and
about 182 kB of storage each (`:25`).

| route | dim | status on record | decisive cheap test | cost of the test | cost if it passes |
|---|---|---|---|---|---|
| **R1. Identifiability ladder** (new; uses D-ID's Fisher code and MP4-A's strict bounds) | 2D–5D | D-ID computed these widths only at 5D (J, EW, H2). The EW cells are ≈ 2.5–3.5% at the coarse truth grid and 20–30% at the split grid (`d-id/REPORT.md:424-425`) | per dimensionality, the fraction of natural reporting cells with binned CR and strict-bounds 68% half-width ≤ 10% at the analysis binning | local, about 10–20 core-h **(inference, from MP4-A's 8.8 core-h at 5D)**; 0 node-h | — (a filter) |
| **R2. Binned-IBU coverage pilot** (IBU-1 machinery) | top dim passing R1 | IBU-1 reported: at 5D J cells IBU's own 400-seed median J coverage is 0.000 at GiBUU, W1 and W3 (`O/state/2d-closeout/stageF/methods/ibu1/REPORT.md` §4), so the pilot is for lower dimensions | IBU coverage, 400 seeds × the IBU-1 truths, at that dimensionality | < 1 CPU node-h **(inference, from IBU-1's ≈ 20 s per experiment)** | — (a filter; meaningful only if IBU-1 reads inverse-problem limited) |
| **R3. OmniFold Tier-S pilot** | the dim passing R1 and R2 | s5c's design at 5D failed | 400 seeds at nominal plus two departures, with the amendment-4 construction | ≈ 1,200 × 0.0104–0.0148 ≈ **12–18 CPU node-h (inference)**; a 3D or 4D unfold is likely cheaper, but no 3D/4D timing is on record | full Tier S: 12,000 experiments ≈ **125 CPU node-h** (`FEASIBILITY…:72`). Exactly nominal coverage needs about 21,000 per point (`FEASIBILITY…:32-38`; the increment is ≈ 660 node-h there, ≈ 867 by s5n's recomputation, `OUTCOME-20260925-s5n…:158-159`) |
| **R4. 2D held-out variance calibration (N2)** | 2D | the cheapest informative 2D design; it needs Joseph to lift the KI-85 deferral | itself | **7.4 node-h**, 100 runs (`O/DESIGN-20261008-2d-independent-statistical-validation.md:455,516`) | — |
| R5. Identified functionals (I2) | 5D | "a different publication endpoint". At the split grid only 5/109 J, 3/39 EW and 2/27 H2 are identified, so it needs wide combinations | an MC-only selection, then a local reduction | 2–10 CPU core-h (`d-id/REPORT.md:569-578`) | an endpoint change: Joseph's |
| R6. Coarser or selected 5D functionals | 5D | **excluded by Joseph, 2026-10-10** (`O/state/measurement-paper/PLAN.md:388`; `O/DECISION-20261019-joseph-methods-first-and-measurement-compute.md:36-37`) | R1 covers the EW cells | — | **(inference)** whether "defer to what can be validated" (2026-10-22) reopens it is Joseph's |
| R7. Unbinned-information study (split-half responses) | 5D | named, "not part of MP4-A"; the loophole is material | **folded into R10**, whose test carries the split-half control | as R10 | as R10 |
| R8. Prior-free or bias-aware intervals at lower dimension | 2D–4D | strict bounds failed only at 5D J | part of R1 | as R1 | as R3 |
| **R9. Negative-weight background treatment, configuration (e)** (Joseph's question, 2026-10-22) | 5D | already measured at development scale (s5e): it fixes the nominal background bias. Departure coverage is 0.017–0.157 (§2), and the residual is not the background's. No covariance or coverage is validated for (e) | KI 98's tilt seeds re-unfolded with (e), background included, against (e)'s own nominal β and σ (§4.1) | ≈ 0.3 CPU node-h **(inference, from the measured (e) unit of 0.0115)** | coverage at nominal only: 74–204 CPU node-h per truth point, with assurance 0 at the measured per-functional minimum (`O/state/s5e/cand/next_design.json`) |
| **R10. More reconstructed information** (Joseph's question whether to reopen PET, 2026-10-22) | 5D | the classifier is not the bottleneck (D-ID); the unbinned-information loophole is material but its size is unmeasured once response-MC noise is counted (MP4-A §6a) | on D-ID's binned setting: the J width floor and departure residual with 2× and 4× finer reco bins, and with one or two added reco variables, under a split-half response (§4.2) | (i) ≈ 2–10 local core-h; (ii) one tuple-extraction pass, ≈ 1–3 CPU node-h, then ≈ 2–10 local core-h **(inference, from D-ID and MP4-A)** | a GBDT development assessment with the added features: ≈ 2.3 CPU node-h, or ≈ 4.5 GPU node-h **(estimate)**; a Tier-S pilot ≈ 17–25 CPU node-h, or ≈ 34–50 GPU node-h **(estimate)**. PET only after that, priced then |
| Closed on record | 5D | prior dependence as a component; more iterations or a bias correction; a neural or PET classifier on the same inputs (R10 asks about added information, not the classifier); FBU (`PLAN.md:385-390`) | — | — | — |

**Total (statistical plus systematic) coverage.** At 2D the record calls P1 infeasible (0.29–1.21 M node-h) and P2
inconclusive (575–3,518 node-h, an operand missing). Independent validation is a no-go: there are no disjoint
production-size MC populations (`O/ASSESSMENT-20261008-2d-total-uncertainty-feasibility.md:72-75,85-87`;
`O/DESIGN-20261008-…:44-58`). **(inference)** The same single-production obstacle binds 3D–5D.

**Constraints.**
- **Two `iris` readings** (read only, no charge):
  - 2026-10-19 16:40 UTC (`O/DECISION-20261019-joseph-methods-first-and-measurement-compute.md:41-51`, receipt
    `O/state/measurement-paper/iris-20261019.txt`);
  - 2026-10-23 05:31 UTC, by this lane (receipt [`iris-20261023.txt`](iris-20261023.txt)).

  | pool | group charged, 10-19 | group charged, 10-23 | left, 10-23 | rate over the 3.54 days between |
  |---|---:|---:|---:|---:|
  | `m3246` CPU (of 20,000) | 17,672.2 | 17,711.5 | **2,288.5** | 11.1 node-h/day (the 10-19 record: ≈ 89/day since 10-14) |
  | `m3246_g` GPU (of 180,000) | 133,774.0 | 137,272.6 | **42,727.4** | 990 node-h/day (the 10-19 record: ≈ 860), ≈ 43 days left at that rate |

  - Joseph's own use is 2,097.3 of 10,000 CPU node-h (+18.5 since 10-19) and 1,295.8 of 90,000 GPU node-h
    (unchanged).
  - The CPU group pool stays the binding CPU limit. The director grants the measurement work at most half of what
    remains (`DECISION-20261019…:48-53`).
- **The GPU pool as a CPU resource (estimates, labelled).**
  - LightGBM, IBU and the binned tests need no GPU. They can run on a GPU node's host CPU.
  - Slurm reports, measured 2026-10-23 with `sinfo`: a GPU node has 128 hardware threads (64 cores) and 257,100 MB;
    a CPU node has 256 threads (128 cores) and 515,100 MB.
  - **(estimate)** For core- or memory-bound CPU work, 1 CPU node-h of work therefore costs about **2 GPU node-h**.
    This ignores contention, which IBU-1 measured as a 3.8× per-step slowdown at 44-way packing on a CPU node
    ([`../2d-closeout/stageF/methods/ibu1/LEDGER-NOTES.md`](../2d-closeout/stageF/methods/ibu1/LEDGER-NOTES.md) §2).
    A GPU node packs about half as many steps, so the factor may be under 2. It is not measured.
  - At that rate even a full Tier S (≈ 125 CPU node-h) is ≈ 250 GPU node-h, under 1% of the GPU pool left.
  - **Any use of `m3246_g` is Joseph's and Ben's decision.** The pool is the group's. The 10-19 record reads "our
    compute" as Joseph's own share (`DECISION-20261019…:24`).
- **Storage:** nothing goes to CFS; scratch is acceptable if the work moves fast
  (`O/DECISION-20261022-joseph-measurement-scope-and-lanes.md`). Storage is not the limit: 12,000 experiments take
  about 2.2 GB.

### 4.1 R9: the negative-weight background treatment as a route to validated 5D coverage

**The question.** Joseph asked whether "doing the negative reweighting to try and get an accepted uncertainty" is worth
it, "but maybe we need to be more confident that it will work first?"
(`O/DECISION-20261022-joseph-open-items-and-rewrite-timing.md:19`). That record authorizes no coverage campaign under
this treatment (`:25-28`). Everything below stays on the current ME-FHC inputs (`:34`, `:54-55`), so that it is
comparable with s5c, KI 98, D-ID and IBU-1.

**What (e) is.** Configuration (e) is deterministic LightGBM OmniFold with 5 iterations, 100 trees and 8 leaves, and
the unbinned negative-weight (Stay-Positive) refinement at 400 trees and 31 leaves
(`O/state/2d-closeout/stageF/methods/RE1-SPEC.md:14-15`). This is the s5e candidate R
(`O/state/2d-closeout/stageF/methods/r12/REVIEW.md:48`). It already gives the 3D–5D central values (RE-1), and no
covariance or coverage exists for it (`RE1-SPEC.md:10`; `RE1-REPORT.md:11`).

**What the record already says.**

| evidence | what it shows | bearing on the route | record |
|---|---|---|---|
| s5e diagnosis | the nominal background bias was caused by the refinement underfitting at 100/8. At 400/31 it falls by > 80% in every worst cell | **for:** this is the part a background treatment can fix, and (e) fixes it | `O/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md:45-48` |
| s5e A1, A2 (40 nominal) | closure passes (EW median \|residual\| 0.02%). Pooled 68%/95% coverage 0.680/0.942; pull SD 1.023 | **for, at nominal only:** the only 5D construction on record calibrated at nominal truth, pooled. But 6 functionals fall outside 3 SE against ≈ 0.4 expected, and EW41's 68% coverage is 0.375 | `:79-80` |
| s5e K2 | (e)'s GiBUU E_avail residual is 10.81/73.9% (median/max EW), against B0's 10.79/74.1% | **against:** the refinement leaves the departure residual unchanged | `:68` |
| s5e assessment, five departures | pooled 68% coverage: GiBUU 0.024, q3 0.019, W1 0.025, W2 0.157, W3 0.017. The pseudo-experiment σ is a median 0.19% relative, against 2–11% median residuals | **against:** (e)'s own intervals already fail at every departure measured. (e)'s nominal mean residual is about 0.02% (EW median, A1), so amendment 4's nominal correction cannot close that gap **(inference)** | `O/state/s5e/cand/assess_receipt.json` → `points`, `sigma_rel_pct` |
| s5n, signal-only | signal-only experiments on the same seeds reproduce the departure residuals (correlation 0.9994 and 0.9993): "a property of the estimator, not of the background method" | **against:** a background treatment cannot fix a residual that exists without background | `O/OUTCOME-20260925-s5n-stage1-development-fail.md:81-84` |
| KI 98 arm (b), rate change | with no background at all, the W-graded residual persists: R_b = +2.840 (SE 0.459, k·SE 1.274), not different from arm (a) (D_b = −0.553, SE 0.479) | **against, for the departure where s5c failed:** the residual that made s5c's rate-change coverage futile is present with no background | `O/state/ki98-wbias-test/REPORT.md:58-59,63-64` |
| D-ID §11 | at K = 5 the GBDT's median residual equals exact binned and fine-grid IBU's; branch C, weak identifiability for binned estimators | **against:** the residual belongs to the inverse problem at this binning and exposure, not to OmniFold's background handling | `O/state/next-preparation-20261009/d-id/REPORT.md:524-526,550-552` |
| s5e A3 | on the real data, a float32-ulp perturbation moves the functionals by 0.78 data-σ (median) and 2.58 (max). "An interval that the estimator's own numerical noise exceeds cannot be coverage-validated" | **against, until resolved:** the open s5e item 1, ≈ 6.3 CPU node-h, decides whether the data bootstrap already absorbs this | `OUTCOME-20260926…:81,95-99,132,138-140` |
| IBU-1, per truth | at W1–W3, on (e)'s own assessment seeds, binned IBU's residual is 0.93, 1.31 and 0.93 × (e)'s, each "consistent"; at GiBUU, against s5n's negative-weight grid, 0.77, "consistent". At (e)'s nominal points IBU is worse (3.6×): (e)'s nominal residual is ≈ 0.02% | **against:** the departure residual matches exact binned IBU's, so it is not (e)'s to repair | `O/state/2d-closeout/stageF/methods/ibu1/REPORT.md` §1, §2, §4 |

**(inference) Reading.**
- The negative-weight treatment removes the background's share of the failure, and the record shows that share is
  small at departures.
- What breaks coverage at departures is a bias of 2–11% (median) against a σ of about 0.2%. It is present without
  background and is shared by exact binned IBU.
- With no background, the background treatment has nothing to act on. KI 98's arm (b) is then very nearly (e)'s own
  no-background result on the tilt. The KI 98 arm-(b) product used the s5c F2 base, deterministic with 5 iterations (`O/state/s5c/contract.json:43,56`).
  That (e)'s base unfold is the same is checked by control K-e0 below, not assumed.
- So the record predicts that (e) inherits the +2.8σ W-graded residual at the rate change.

**The decisive cheap test (a proposal; it needs a declaration and Joseph's grant through the director).**
- **What it runs.** KI 98's rate-change truth (`eavail_tilt`, a = 0.2) at seeds 204000–204019, built with the
  negative-weight construction and background included, then unfolded with (e).
  - `s5n_pseudo.truth_weight` passes `eavail_tilt` through to s5c's definition unchanged (`nd-unfolding/s5n_pseudo.py:94-99`
    at `d28ebad6`), so no producer change is needed.
  - The first five seeds are KI 98's. The signal-half split is shared through the same split key; the background
    stream differs by construction.
- **References.**
  - (e)'s nominal β and se come from R's 40 nominal assessment experiments, 800000–800039.
  - σ comes from R's 100-replica bootstrap (nominal 700000).
  - Both already exist and are digest-pinned as IBU-1 comparators (`ibu1/DECLARATION.md` table, `N_nominal_R` and
    `N_sigma_R`). Nothing new is needed at nominal.
- **Controls.**
  - **K-e0:** one tilt seed with `no_background` through (e)'s path reproduces KI 98's arm-(b) product for that seed,
    bitwise or at the recorded rounding level. This tests the identity the prediction rests on.
  - **K-e1:** one nominal seed reproduces its recorded R assessment product.
- **Not a KI 98 extension.** KI 98 forbids adding seeds or arms after its result (`ki98-wbias-test/REPORT.md:131-132`).
  This would be a separate declared test, and it leaves KI 98's UNDETERMINED verdict as it is.
- **Readout.** KI 98's: R_e = the mean ρ_e over seeds on the primary band (EW, W ≥ 3), with k·SE_e from the same
  t rule. Also R_e − R_b, and all 153 functionals descriptively.
- **Cost.**
  - The measured (e) unit is 0.0115 CPU node-h per pseudo-experiment (`O/state/s5e/cand/next_design.json` →
    `inputs.cost_pseudo`).
  - 22 experiments are therefore ≈ 0.25 node-h. With KI 98's measured startup overhead (0.197 node-h for 16 F2 tasks,
    `ki98-wbias-test/REPORT.md:134-140`), the ceiling to grant is **≈ 0.5 CPU node-h** **(inference)**.

**What result would make the route worth a campaign.** All four of these must hold. The record predicts that the first
fails.
1. **The tilt test:** R_e is not resolved (\|R_e\| ≤ k·SE_e), and no reported functional's mean ρ_e exceeds 1 in
   magnitude beyond its own k·SE. Expected instead: R_e ≈ R_b ≈ +2.8, resolved.
2. **s5e item 1** (≈ 6.3 CPU node-h) shows that the data bootstrap absorbs the numerical floor.
3. **IBU-1** does not read "inverse-problem limited" on arm N. If it does, no OmniFold-side background treatment can
   reach those functionals at this binning.
   - **Reported: this condition fails.** Every arm-N truth (GiBUU, W1, W2, W3) reads "consistent" (`O/state/2d-closeout/stageF/methods/ibu1/REPORT.md` §1).
     The formal verdict is unresolved only through the arm-P rate change. **(inference)** On arm N the pattern is the
     inverse-problem-limited one.
4. **Joseph accepts the scope this could reach.** That is statistical coverage at nominal truth and at departures of
   the tilt's size, not at generator-sized ones, where (e) is already measured at 0.017–0.157.
   - Its cost is s5e's own design, 74–204 CPU node-h per truth point at exactly nominal coverage. At the measured
     per-functional minimum coverage (0.50/0.81), assurance is 0 at any n (`OUTCOME-20260926…:135-136`).

**Proposal for this route.**
- Treat (e) as what it already is: the central-value estimator (RE-1), calibrated in pooled form at nominal truth only.
- Do not plan a coverage campaign on it.
- If Joseph wants the confidence he asked for, the 0.5 node-h tilt test above gives it at the lowest cost:
  - a resolved R_e ≈ R_b closes the route as a coverage route on these inputs;
  - an unresolved R_e (unexpected) moves the route to conditions 2–4.
- IBU-1 has now reported, and condition 3 fails. So the route does not qualify for a campaign whatever the tilt test
  shows **(inference)**. The tilt test would add confirmation on (e)'s own path at the rate change, not a decision.

### 4.2 R10: more reconstructed information, and whether to reopen PET

**The question.** On 2026-10-22 Joseph asked whether to reopen PET. The director advised against it, "because D-ID
shows the residual is not the classifier's" (`O/DECISION-20261022-joseph-measurement-scope-and-lanes.md:5-9`). That
reasoning closes a better classifier on the same inputs. It does not close more information on the reco side. PET
differs from the scalar GBDT in what it sees: a cloud of reco clusters, not five scalars. So the question here is
whether the reco side carries information beyond the five binned scalars, and enough of it to matter.

**What the record says.**

| evidence | what it shows | bearing | record |
|---|---|---|---|
| D-ID §9.3 | at K = 5 the GBDT's J median residual equals exact binned and fine-grid IBU's on the same five reco scalars: GiBUU 9.5/8.3/8.6%, W1 5.4/5.4/5.6%, W3 5.6/4.9/5.0%, q3 4.3/5.3/4.0% | **against a better classifier:** on these inputs the classifier is not the bottleneck (`PLAN.md:387` closes it) | `O/state/next-preparation-20261009/d-id/REPORT.md:432-440` |
| D-ID §11 limits | "Unbinned information is not bounded by them" (the Fisher widths) | **open:** the binned no-go leaves the information question | `d-id/REPORT.md:546-548` |
| MP4-A §6a | splitting every reco bin at its midpoint on each axis (10,499 → 113,062 occupied cells) takes the J Cramér–Rao floor at T2 from 28.7% to **10.8%** median (9.7% with holes excluded), p90 117% → 31.6%. J functionals at ≤ 10% go from 32 to 54 | **for:** the loophole is "material, not marginal" | `O/state/measurement-paper/phase1/mp4a/REPORT.md:107-137` |
| MP4-A §6a caveat | the refined response comes from the same finite MC, ≈ 180 events per occupied cell, and the Fisher treats it as exact, "so MC fluctuations in R read as resolution". Sizing it soundly needs split-half responses | **against taking 10.8% at face value:** it is an optimistic figure | `mp4a/REPORT.md:140-146` |
| PET development diagnostics | whole-event reco summaries in step 1 let PET close the stored-cluster energy distribution and pass on part of a proton-multiplicity change. Under a neutron change the same channel pushes E_avail the wrong way: "the hidden-variable pattern" | **both:** added reco information can carry real signal, and can also import the prior's reco–truth correlations as bias | `nd-unfolding/pet/final_design/DIAGNOSTICS-20260925.md:70-78` |
| PET reco cloud | the stored reco cloud is capped at 12 clusters in 85.5% of selected events, so its stored-cluster count and energy sum are truncated summaries | the extra variables should be whole-event branches, not the capped cloud | `DIAGNOSTICS-20260925.md:82-88` |

**(inference) Reading.**
- A better classifier on the five scalars is closed.
- Information finer than the analysis reco binning, or in other reco variables, is open and plausibly material.
- Its size is not known once response-MC noise is counted, and its value at departures is not known: MP4-A measured
  widths at nominal only, and residuals not at all.
- Reopening PET on this premise is premature. The binned test below sizes the premise first, and a GBDT run with extra
  reco features tests it more cheaply than PET would.

**The decisive cheap test (a proposal; no run; it needs a declaration and a grant through the director).**
- **Setting.** D-ID's binned setting unchanged:
  - the same events (`of_inputs_5d.npz`, sha256 `07fccc1a…`);
  - the same truth grids T1 and T2;
  - the same weight sets: nominal, GiBUU, W1, W2 and W3, with q3 descriptive;
  - exact binned IBU at K = 5 and at D-ID's convergence rule, and the Fisher F = Rᵀ diag(1/(Rt + b)) R;
  - D-ID's own code (`d-id/did.py`) and MP4-A's refinement (`measurement-paper/phase1/mp4a/extra_c.py`), imported
    unchanged by new code in a new directory.
- **(i) Finer reco binning of the five scalars.**
  - Refinement factors f = 1 (control), 2 and 4 per axis, by midpoint splits as in MP4-A §6a. f = 4 splits each
    f = 2 cell again.
- **(ii) Added reco variables.** Each is a sixth reco axis with 3 bins at nominal-MC quantile edges, frozen before any
  output. Each is run alone at f = 1 and f = 2, and one declared pair at f = 1.
  - The candidates are whole-event branches in the official MAD branch documentation
    (`MinervaExpt/Tuple-Documentation`, `MAD_tuple_MainDoc.csv` at `da1087cc`, sha256 `cbf34b1c…`; rows by CSV line).
    All four branch families are present in both the FHC MC and the FHC data 1B files listed by the 2026-10-22
    survey (`O/state/data-survey-20261022/outputs/followup/branches_fhc_{mc,data}_1B.json`).
  - **C1, in-time recoil cluster count:** `part_response_recoil_allNonMuonClusters_<subdetector>_nClus` (row 4,
    "Number of Clusters in-time-with-the-vertex (-20, 35 ns window) that are not attached to the primary lepton").
    It is uncapped, unlike PET's stored-cluster count.
  - **C2, recoil energy by subdetector:** `part_response_total_recoil_passive_allNonMuonClusters_<subdetector>`
    (row 7, the "passive-material corrected, calibrated energy" per subdetector). Reco E_avail sums the subdetectors;
    **(inference)** the tracker/ECAL/HCAL split carries hadron-composition information that the sum loses.
  - **C3, charged-hadron track count:** `part_response_container_total_recoil_passive_primaryHadrons_<subdetector>_sz`
    (row 30, "Number of 'Primary Hadrons' or charged particles tracked to the vertex").
  - **C4, neutron candidates:** their count, `MasterAnaDev_BlobNClusters_sz` (row 229), and visible energy,
    `MasterAnaDev_BlobTotalE` (row 204).
  - Which subdetector index each uses is fixed in the declaration.
- **Split-half control (R7, folded in here).** The MC is split in half by the event key. The response is built from
  half A; half B's noise-free, departure-weighted reco is unfolded with it and scored against half B's own truth. The
  Fisher widths are computed from R_A at half B's expected counts. Same-sample figures are reported beside them as
  the optimistic bound. **Only the split-half figures decide.**
- **Controls.**
  - At f = 1, same-sample, the widths and the K = 5 residuals reproduce D-ID's `tables.npz` and r_IBU bitwise, as
    MP4-A's control did.
  - A null added variable (a uniform random number per event, seeded) must leave every width and residual unchanged
    within split-half noise. It tests that the split-half construction does not read MC noise as information.
- **Readout.** For each configuration:
  - the J median and p90 of the 68% CR half-width at T1 and T2 (holes as +∞ and excluded);
  - the J median |r_IBU| at K = 5 and at convergence, per departure.
  - OSB widths only at a configuration whose CR widths pass, since positivity moved the J median by ≈ 0.2%
    (`mp4a/REPORT.md:92-93`).
- **Cost.**
  - (i): D-ID's whole diagnostic took 0.806 core-h at f = 1 (`d-id/REPORT.md:361`), and MP4-A's 2× Fisher took 43
    CPU-s and 3.17 GB (`mp4a/REPORT.md:116`). **(inference)** With ≈ 10× the occupied cells at f = 2, and more at
    f = 4, (i) is ≈ 2–10 local core-h. f = 4 may need a cluster node for memory, ≤ 0.5 CPU node-h.
  - (ii) first needs one extraction pass that reads the candidate branches from the 12 ME-FHC MC playlists and joins
    them to the `of_inputs_5d.npz` rows. The measured analogue is MP1's 1A species passes, which read ≈ 25 extra
    `part_response_*` branches in 0.035–0.073 CPU node-h each on shared QOS (`O/state/measurement-paper/phase1/mp1/S0-REPORT.md:180-201`).
    **(inference)** Scaled to 12 playlists that is ≈ 1–3 CPU node-h, then ≈ 2–10 local core-h for the binned
    computation.
  - The join must use the inventory's event key and gate on `pass_reco`. A (run, subrun, gate) key is a gate key, not
    an event key.

**What result would justify the next step.** Fixed here before any output; the declaration may tighten it but not
loosen it.
1. **A GBDT run with the extra features is justified** only if some configuration from (i) or (ii), on split-half
   figures, does both of these:
   - brings the J CR floor at T2 to median ≤ 10% and p90 ≤ 25% (the frozen T1 bar), or at least halves the f = 1
     split-half median;
   - cuts the J median |r_IBU(K = 5)| by at least a third at three or more of the four departures GiBUU, W1, W2 and
     W3, against f = 1.

   The null variable must pass in the same run. A width gain with no residual gain is not enough: the departures
   are where coverage failed (§3).
   - That run would be s5e's development assessment (40 nominal plus 20 at each of five departures) with the chosen
     features, priced at 140 × 0.0115 × 1.4 ≈ **2.3 CPU node-h**, or ≈ **4.5 GPU node-h (estimate)**. The 1.4 is
     **(inference)**: LightGBM's histogram cost is taken to scale with the number of features, 7 over 5.
   - Before any coverage claim it would also need a departure in the added variable's own truth correlate, such as
     PET's proton and neutron multiplicity cases (`DIAGNOSTICS-20260925.md:44-78`). That is the hidden-variable risk.
2. **A PET run is justified** only after that GBDT run:
   - if it shows the gain the binned test predicted, but leaves a residual the binned test attributes to information
     that a few scalars cannot carry;
   - for example, (i) gains keep growing from f = 2 to f = 4 while (ii)'s scalar additions saturate.
   - PET is GPU work, on `m3246_g` or Delta `bhvk`. It is priced from the PET records at that point, not here.
3. **If nothing passes** on split-half figures, the loophole is closed for binned information at this exposure, and
   the record has no ground for reopening PET.
   - An unbinned estimator could still exceed a 4× binning only through structure finer than 4× per axis. The
     2× → 4× trend bounds that **(inference)**.

**Not a route to coverage by itself.** Even a pass leaves the departures' bias (§3) to be shown repaired. The
coverage tests R2/R3 follow at the chosen inputs.

## 5. Recommendation (a proposal for Joseph; the uncertainties follow)

1. **IBU-1 is done** (1.07 CPU node-h). Verdict **unresolved**: consistent at GiBUU, W1, W2 and W3; unresolved at the
   rate change (`O/state/2d-closeout/stageF/methods/ibu1/REPORT.md`).
2. **Run R1, the identifiability ladder, now, locally at 0 node-h.**
   - For 2D, 3D, 4D and the 5D (E_avail, W) cells: binned CR and strict-bounds widths of the natural reporting cells
     at the analysis binning.
   - It needs a short declaration that fixes the cells and the ≤ 10% bar before any output. The bar is the frozen 5D
     target T1, applied to each dimensionality's own cells.
   - It answers "what dimensionality can reach validated intervals" in its prior-free, statistics-only form, before
     any node-hour is spent.
3. **Then branch on IBU-1.** The verdict is unresolved, with "inverse-problem limited" and "mixed" still open.
   **(inference)** At the generator-sized departures the record reads as the first branch. Only the rate change
   could still make it mixed.
   - **If inverse-problem limited:** run R2 (binned-IBU coverage at the highest dimensionality R1 passes, < 1 node-h).
     If IBU covers there, run R3, the OmniFold Tier-S pilot at that dimensionality (≈ 12–18 node-h), and only then a
     full Tier S (≈ 125 node-h).
   - **If implementation specific:** the OmniFold configuration, not the problem, is the target. The next step is an
     estimator-family question for Joseph, outside this lane.
   - **If mixed:** use R1 and the per-truth readings to pick the dimensionality, and go to R3 directly.
4. **Separately, for 2D:** ask Joseph whether to lift the KI-85 deferral for N2 (7.4 node-h). It would give the 2D
   statistical band a tested calibration, the strongest validated interval the record can reach soon.
5. **On Joseph's negative-weight question (R9, §4.1):** do not plan a coverage campaign under configuration (e).
   - IBU-1's arm N reads consistent at every truth, which fails §4.1's condition 3.
   - The tilt test (≤ 0.5 CPU node-h, with its own declaration and grant) is now optional confirmation, not a
     decision. The record predicts that it would close the route too.
6. **On reopening PET (R10, §4.2):** not yet. First run the binned information test, with split-half responses and
   a null-variable control: a few local core-hours, plus ≈ 1–3 CPU node-h for the tuple extraction that (ii) needs.
   - A GBDT development run with the added features follows only on the pass rule fixed in §4.2: ≈ 2.3 CPU node-h,
     or ≈ 4.5 GPU node-h **(estimate)**.
   - PET follows only after that GBDT run. Any use of the GPU pool is Joseph's and Ben's decision.
   - It can run beside R1, which uses the same D-ID code.
7. **Do not plan total-coverage validation** at any dimensionality. The record prices it out of reach. A measurement
   paper would state statistical coverage where tested, and carry systematics as quoted blocks without a coverage
   claim.

**Uncertainties.**
- R1's widths are binned, signal-only, noise-free and local. They are optimistic at the coarse grid and pessimistic
  for unbinned estimators (`d-id/REPORT.md:187-196`). So R1 is a filter, not a guarantee.
- A dimensionality that fails R1 is a binned no-go, not an impossibility (MP4-A's loophole).
- R2 predicts OmniFold only where IBU-1 reads inverse-problem limited: on the record, at the generator-sized
  departures, not yet at the rate change.
- R3's cost for 3D/4D is inferred from 5D timings; no 3D/4D timing is on record.
- Whether a lower-dimensional measurement, or 5D (E_avail, W) cells, falls under Joseph's 2026-10-10 exclusion of
  "coarser or selected functionals" is his call. The record does not settle it.
- R10's binned test sees information only up to 4× finer reco bins and the declared variables. Its departures are
  D-ID's, which do not vary the added variables' own truth correlates.
- The conversion of CPU work to GPU node-h is an estimate from node size. No CPU-only job has been timed on a GPU
  node here.

## 6. Not done here

- No new computation. The only reads are two `iris` and `sinfo` listings (2026-10-23) and the public branch documentation.
- R1's cells and bar are not frozen: that needs its own declaration.
- R10's variables, subdetector indices, quantile edges and split key are not frozen: that needs its own declaration.
- RHC and the newer FHC release are not assessed: RHC follows a validated method (director's reading,
  `O/DECISION-20261022-joseph-measurement-scope-and-lanes.md`).
