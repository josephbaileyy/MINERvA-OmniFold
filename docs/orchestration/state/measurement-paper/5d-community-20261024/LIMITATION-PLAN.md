# PLAN: can the 5D result's three limitations be reduced? A costed scoping for Joseph (2026-10-27)

**By** the measurement session, for the director.

**Under** [`DECISION-20261027-joseph-measurement-framing-and-limitation-scoping.md`](../../../DECISION-20261027-joseph-measurement-framing-and-limitation-scoping.md)
item 2 (PR #420). Joseph asked: "are we sure theres no way to resoslve the limitations?"

**MEASURES:** nothing.
- No step of this plan ran on the cluster, and none is declared or bound.
- The only computation is arithmetic on three committed readouts: `fd_f0b_readout.json` (`b9db935a…`),
  `cmodel_5d.json` (`3cfdc6a5…`) and `fd_data_product.json` (`b79556f0…`).
  - The script is [`limitation-plan/plan_arithmetic.py`](limitation-plan/plan_arithmetic.py), and its output is
    [`plan_arithmetic.out`](limitation-plan/plan_arithmetic.out).
  - It ran on a laptop at 0 node-h.
- No data-against-generator χ² is computed anywhere in this plan.
  <!-- absence-ok: describes this plan's own scope (what it ran and computed), not a claim that a result is absent from the repository -->

**CANNOT AUTHORIZE:** a run, a declaration, a change to the reported covariance or to κ, a claim, or printed wording.
All of these are Joseph's. Where the plan says what the paper "could state", it gives only the content. The wording is
his.

**CITABLE FOR:** the options, their costs (estimates from the recorded unit costs), and the evidence each rests on.

**NOT CITABLE FOR:** a coverage result, a new uncertainty, or any reading of the data.

**Paths:**
- a bare filename is in this directory;
- `DECISION-*` and `OUTCOME-*` are in `docs/orchestration/`;
- `nd-unfolding/…` and `2d-unfolding/…` are from the repository root;
- every other path is relative to `docs/orchestration/state/`.

## 0. The answer in one table

**Limitation 1: interval coverage is not validated.** <!-- absence-ok: names the limitation as DECISION-20261027-joseph-measurement-framing-and-limitation-scoping.md:27 states it -->
- **Options and costs:**
  - **1C,** a descriptive readout of the existing nuisance-drawn A7 experiments: 0 node-h.
  - **1A,** F1's held-out bias test: 0.84–1.25 node-h, cap 2.1.
  - **1B,** a nuisance-drawn coverage test at two GENIE v3 truths: about 45–146 node-h (§1.4), 1–2 weeks.
  - **1B′,** the same test at existing truths, with no GENIE v3: about 37–133 node-h.
- **Likely effect:** **reduces** it, at best, to "covered at the tested truths under the nominal response". It **cannot
  remove** it. At the GiBUU-like and q3 truths, F0b's measured biases already put 1σ coverage at or below 0.5 in 3–5
  cells, whatever the spread (§1.3).

**Limitation 2: the fake-data bias at the GiBUU-like truths and the q3 tilt.**
- **Best option:** (c), keep it as stated, quantified with F0b's numbers. Cost 0.
- **Likely effect:** **re-describes** it. (a) moves the bias into the covariance and cannot then be tested. (b) does not
  cover it even with every C_model vertex scaled without limit (§2.2).

**Limitation 3: the χ²'s flux-correlation sensitivity.**
- **Best option:** state it, as decided. Optionally add 3D, a bootstrap of the flux correlations over the 100
  universes. Cost 0, plus a declaration and a login-node run for 3D.
- **Likely effect:** it is **inherent.** 3D **re-describes** it on a measured footing, in place of an arbitrary α.

**None of the three can be removed** by work admissible after the data read. Two can be narrowed: coverage at the
tested truths, and the flux sensitivity's description. The third, the GiBUU-like and q3 bias, can only be moved into
a number that nothing can then test.

## 1. Interval coverage is not validated <!-- absence-ok: the section title names the limitation as the framing decision (:27) states it -->

### 1.1 What exists

<!-- absence-ok: each absence in this subsection restates a cited record's own status (FD-PLAN.md:92, :303-317; FD-F0b-REPORT.md:19; DECISION-20261024-joseph-5d-community-standard-route.md:46-47; fd_data_product.json not_citable_for); the 16-cell coverage-test absence is scoped to the Search line at the end of this plan -->

- **No coverage test of the 16-cell intervals is on record.** F0 and F0b are bias tests. <!-- absence-ok: scoped to the Search line at the end of this plan and to FD-PLAN.md:92 -->
  - **What "graded" means there:** the bias b_T, the mean of x̂/x_true − 1 over pseudo-experiments, is χ²-tested
    against the leave-own-vertex-out matrix plus the noise of the mean (`FD-PLAN.md:229-237`, `:288-293`).
  - The plan says so itself: "None is a coverage gate" (`FD-PLAN.md:92`).
  - F0b is not citable for held-out truths (`FD-F0b-REPORT.md:19`).
  - The graded pseudo-experiments are Poisson only, with no nuisance draws (`FD-PLAN.md:142-146`).
- **S-3, the spread test, was withdrawn** (`FD-PLAN.md:303-317`). It asked whether the nuisance-drawn spread matches
  C_e, and it was dropped for three reasons:
  - A7's draws move only the response, with the truth fixed in every fine cell;
  - A7's flux mechanics differ from S1's, which unfolds with each universe's flux and denominator;
  - "An expected value for the statistic would need a derivation first."
- **The paper must already state the gap.** "Validated coverage at held-out truths is **not** a requirement… The
  paper states plainly that coverage was not validated, and why" (`DECISION-20261024-joseph-5d-community-standard-route.md:46-47`). <!-- absence-ok: a quotation of the decision record -->
  The data product carries `not_citable_for: coverage`.
- **The project's one coverage test failed.**
  - It was the 2D fixed-truth coverage test of the statistical band, VL169 (`OUTCOME-20261005-2d-fixed-truth-coverage-fail.md`).
  - It was pre-registered, with a futility interim at 100 toys and positive controls at ×0.7 and ×1.3.
  - Verdict: FAIL-undercoverage, with C2 = 0.9121 against the window [0.9281, 0.9722]. Cost 13.33 node-h.
  - Its design is the template for §1.4.

### 1.2 Would the merged 16 cells calibrate better or worse than H2's Stage 0?

- **Stage 0 on H2** graded family hold-out c_F. The pass rule is c_F ≥ 0.60 for every family and pooled ≥ 0.68.
  - GiBUU: **0.259** (7 of 27, κ 0.496).
  - NuWro: 0.747.
  - GENIE MEC: 1.000.
  - Pooled: 0.697 (`measurement-paper/5d-design-20261023/STAGE0-REPORT.md:30`, `:113-116`).
  - Stage 0 graded H2's 27 supported boxes. The 16 reported cells merge 28 boxes, with box 17 absorbed into R09.
- **Coarser against finer, from Stage 0 itself, is mixed.** Comparing H2 with the finer J grid
  (`measurement-paper/5d-design-20261023/STAGE0-REPORT.md:109-115`):
  - GiBUU is worse on H2: 0.259 against 0.541.
  - NuWro is better on H2: 0.747 against 0.570.
- **R10 bears on finer binning, not coarser cells.** It tested finer reco binning and a sixth reco axis on the J
  group. Its verdict was INCOMPLETE, with 0 PASS, 5 FAIL and 6 UNDETERMINED. It reports the H2 group descriptively
  only (`measurement-scoping/r10/REPORT.md:24-41`, `:144`).
- **The direct evidence on the 16 cells is F0b's bias grade, which is not a c_F calibration.** It shows the GiBUU bias
  surviving the merge.
  - A7 GiBUU has |z| > 2 at R02, R06 and R07 (`FD-F0b-REPORT.md:128`).
  - Its χ² is 175.13/16 against the grade matrix, and 142.62/16 in-sample, with its own vertex included (`:157`).
  - Stage 0c GiBUU still flags R06 (`:127`).
  - At NuWro-like truths the bias grade passes: closure NuWro 11.60, p 0.771, and A7 NuWro 24.92, p 0.0713
    (`:152`, `:156`).
- **Expectation (inference):** merging boxes whose biases share a sign does not cancel the bias. So there is no
  reason to expect the 16 cells to transfer better than H2 at GiBUU-like truths. Stage 0's c_F has not been computed on
  the 16 cells. <!-- absence-ok: scoped to STAGE0-REPORT.md, which grades J, H2 and EW only (:105-116) -->

**A correction to the premise.** The "181" is F0's in-sample χ² for A7 GiBUU: 180.99, p 5.32e-30
(`FD-F0-REPORT.md:205`). F0b's in-sample figure is 142.62. Both are far above 32.0, the χ²₁₆ at p = 0.01.

### 1.3 What a coverage test would find at the truths already graded

**One statement holds whatever the spread.** Suppose a cell's bias exceeds its reported σ, so |z_c| > 1. Then the
interval of half-width σ centred on the expected estimate, x_true(1 + b_c), excludes the truth. An experiment's
interval covers the truth only if its error e brings it back across. For any error distribution symmetric about zero,
that happens with probability at most 0.5.
- This assumes the bias under nuisance draws equals F0b's Poisson-only b_c, or at least still exceeds σ_c.

z_c here is F0b's in-sample (or grade) z, whose denominator also carries the noise of the mean. It therefore
understates |b_c|/σ_c, which makes the count conservative.

**A second statement depends on an assumption that is known to be false.** It assumes the reported σ is the true
spread, P(|z_c + e| ≤ 1) with e ~ N(0, 1). But a nuisance draw at a fixed truth reproduces at most C_e and C_resp,
never C_model (§1.4). So the means below are indicative only. The nominal value is 0.683.

| truth | cells with \|z\| > 1, coverage ≤ 0.5 for any symmetric spread | mean over 16 cells, under the assumption | min |
|---|---|---:|---:|
| A7 GENIE CV, A7 GENIE+MEC, closure NuWro, W1, W2 | none | 0.665–0.682 | ≥ 0.575 |
| W3 | R10 | 0.635 | 0.467 |
| A7 NuWro | R06, R07 | 0.623 | 0.366 |
| Stage 0c GiBUU | R06, R10, R15 | 0.592 | 0.211 |
| q3 tilt | R06, R07, R08, R10, R15 | 0.567 | 0.263 |
| **A7 GiBUU** | **R02, R06, R07, R10, R15** | **0.502** | **0.000** |

Source: `plan_arithmetic.out` §3.

**What this leaves a coverage test to say.**
- At the GiBUU-like and q3 truths, the flagged cells undercover whatever the width. A test would only confirm it.
- At the low-bias truths (nominal, A7 GENIE CV, W2, closure NuWro), coverage depends entirely on spread against width,
  which F0b's Poisson-only experiments never measured. <!-- absence-ok: F0b's graded rows carry no nuisance draws, FD-PLAN.md:142-146 --> A test there is informative, and needs no new generator. This
  is 1B′.
- At a held-out truth (GENIE v3), both questions are open. This is 1B.

### 1.4 The designs

**1C. A descriptive readout of the existing nuisance-drawn experiments, at 0 node-h.**
- **The products:** row 5, the A7 calibration truths, holds 1,343–1,751 nuisance-drawn experiments per truth
  (`FD-PLAN.md:146`). The truths are MnvTune v1, GENIE CV, GENIE MEC, NuWro and GiBUU. FD-PLAN records them on
  pscratch and in an HPSS archive (`FD-PLAN.md:146`). They were not re-measured for this plan.
- **What it would give:** the spread of x̂ on R00–R15 against C_e, and the per-cell coverage of each interval set.
- **Disqualifiers,** which make it descriptive only:
  - F0's offset control 7 failed, at χ²₁₆ = 245.74 (`FD-F0-REPORT.md:39-41`);
  - the draws differ from S1's mechanics, as S-3 found (§1.1): one flux universe in 100 drawn uniformly, not
    constraint-weighted; the model bands move only the response; the laterals are not applied;
  - the truths are hybrids on the J cells, and the products use half of the MC.
- **Cost:** a login-node reader plus a declaration.
- **Likely effect:** **re-describes** the gap. It cannot validate coverage.

**1A. F1 as priced: a held-out bias test, not a coverage test.**
- **Design:** two GENIE v3 truths, G18_10a_02_11b and AR23_20i. Each gets 1 closure and 20 Poisson pseudo-experiments,
  graded as F0b (`FD-PLAN.md:118`, `:489-492`).
- **Samples:** no GENIE v3 events exist yet. Software and splines are on CVMFS (`FD-PLAN.md:216`).
  - The pseudo-data are a truth reweight (`ratio_nd`) of the existing MC under the nominal response. No new event loop
    is needed, and the detector response is not probed (`FD-PLAN.md:528-533`).
- **Cost:** F1a pilot 0.05–0.17, F1b generation and preparation 0.11–0.33, and F1c unfolds 0.68–0.75 node-h. In all,
  **0.84–1.25 node-h, cap 2.1** (`FD-PLAN.md` §5.2). Each job is under 1 h.
- **What it gives:** the first bias grade at a truth that is not a vertex. GENIE v3 is close to the GENIE family:
  same-family truths are "partial evidence" (`FD-PLAN.md:214`).
- **Why it is not coverage:** the noise of the mean is 0.0004–0.0014 against a median σ of 7.29 %. So per-cell
  coverage reduces to whether |b_c| < σ_c, which 20 experiments settle.
- **The chooser rule:** whoever chooses the configuration, seeds and amplitude "must not be a lane that tunes the
  recipe", and "the outcome stays uninspected until the recipe is frozen" (`2d-closeout/stageD-inputs/REPORT.md:297`).
  Joseph chooses (`FD-DIRECTOR-RULINGS.md:59`).

<!-- absence-ok: GENIE v3 events, throughput and the Perlmutter build are stated as the cited records state them (FD-PLAN.md:216; 2d-closeout/stageD-inputs/REPORT.md:287, :377-378); the repository search is the Search line at the end of this plan -->
- **What is not known yet:** per-event throughput is unmeasured, and whether the CVMFS builds run on Perlmutter is
  unverified (`2d-closeout/stageD-inputs/REPORT.md:287`, `:377-378`). F1a measures both first.

**1B. A nuisance-drawn coverage test: the real one.**
- **Precondition: the S-3 derivation.** The pseudo-data must draw every block of C_e (`S1-REPORT.md:277`):
  - flux, through each universe's flux and denominator, weighted by the ν-e + IMD constraint;
  - the interaction and detector bands, with the prior's dependence. The interaction block is built from ±1σ bands,
    so a draw scheme needs a declared Gaussian interpolation of the knobs;
  - the laterals, 0.1406 of the trace, which A7 did not apply. They would come from the existing lateral dumps;
  - the normalization (0.0276) and the statistics;
  - C_resp, only if the scheme re-runs the response's stochastic part.
  - Any block that is not drawn is removed from the control arm's intervals, and from the §1c reference below.
    Otherwise the control over-covers by construction.

  The expected spread must be derived and declared before binding (`FD-PLAN.md:303-317`).
- **Two interval sets are scored, because the draws cannot reproduce C_model.** At a fixed truth, the nuisances move
  the result by C_e (and C_resp, if drawn) only. C_model is the model term, about 0.42 of the reported trace.
  - **The control arm: the nominal truth, with intervals from the drawn blocks only** (C_e, plus C_resp if drawn). It
    is scored two-sided against nominal 0.683 / 0.954. If it fails, the machinery is wrong and the other arms are
    ungraded.
  - **The test arms: the reported intervals,** C_total + C_resp. At zero bias these are expected to over-cover:
    1σ mean 0.791 (min 0.701) and 2σ 0.983, if the spread is the full C_e; 0.759 (min 0.684) and 0.975, if it is
    C_e + C_resp (`plan_arithmetic.out` §1c).
  - So the test arms are scored **one-sided.** A test arm fails if its pooled C1 or C2 interval lies wholly below
    nominal, 0.683 or 0.954. The expected over-coverage is declared per cell in advance, as context, not as the
    reference.
- **Arms:**
  - **1B:** the nominal control, plus two GENIE v3 truths (from 1A).
  - **1B′:** the nominal control, plus A7 GENIE CV, a non-vertex truth already graded. No generation, and no
    unverified v3 build.
- **Positive controls:** free, from the same toys with the bands scaled, as in VL169.
  - The control arm uses ×0.7 and ×1.3, both two-sided.
  - The test arms use ×0.7 only, against nominal. At zero bias it gives C1 0.594–0.627 and C2 0.893–0.915
    (`plan_arithmetic.out` §1c), so it can fire. A ×1.3 control cannot fail a one-sided rule.
- **Count:** N = 300 per arm.
  - The per-cell binomial SE at 0.683 is 0.027. Pooled over 16 cells it lies between 0.0067 and 0.027, depending on
    how correlated the draws are across cells.
  - A futility interim at N = 100, as in VL169, gives 0.047 (`plan_arithmetic.out` §5).
- **Cost (estimate):**
  - Production: 900 unfolds (1B) at 0.025 node-h is 22.5 node-h, cap 35.2 at 1.5625× (1.25 × 1.25). 1B′'s 600 unfolds
    are 15.0, cap 23.4.
    - The 0.025 unit is A7's measured nuisance-drawn unit (`FD-PLAN.md:471`). The S1-style draws above may cost more
      per experiment. The unit is an assumption until a pilot measures it.
  - Development and admission of the mode: 15–40 node-h, as for the comparable MP1-A-full mode.
  - Verification and repair: 7–70 node-h, the same analogue's line (`measurement-paper/phase1/mp1/S1-REPORT.md:400-410`).
  - F1a and F1b, for 1B only: 0.2–0.5 node-h.
  - **Totals: about 45–146 node-h for 1B, and 37–133 for 1B′.** The low end assumes the analogue's minimum repair.
- **Wall time:** about 40 unfolds per node-hour, packed 8 × 32. For 1B that is 3 nodes × 7.5 h, each job under 12 h,
  on regular QOS, plus queue. With the derivation, declaration and binding, about 1–2 weeks.
- **Not proposed: a nested design.** Rebuilding C_e for every experiment costs one S1 each, 6.04 node-h. That is about
  1,800 node-h per arm at N = 300, and 5,438 for three arms.
- **Decision rules, pre-registered with VL169's form:**
  - C1 = P(|z| ≤ 1) and C2 = P(|z| ≤ 2), pooled over cells, each with a 99.5 % toy-bootstrap interval against a
    declared window;
  - the futility interim at N = 100;
  - the positive controls above must fire;
  - the control arm is two-sided; the test arms are one-sided against nominal, as above.
- **Consequences, fixed in advance.** The data have been read, so the result changes no interval and no covariance.
  Any adoption rule, such as scaling the intervals on a fail, would be Joseph's, declared before the run, and would
  break κ = 1.

**What the paper could state.** These are the contents only; the wording is Joseph's.
- **On a pass:** at the tested truths, under the nominal detector response, the reported 16-cell intervals did not
  undercover, with the measured rates and windows. Nothing would follow about the GiBUU-like truths (§1.3) or the
  detector response.
- **On a fail:** the measured undercoverage, in place of "not validated".

**Likely effect: reduces, does not remove.** 1B or 1B′ narrows the limitation to the tested truths. 1A narrows only the
bias statement. 1C only re-describes.

## 2. The fake-data bias at GiBUU-like truths and the q3 tilt

### 2.1 The facts

- **Both triggered truths are listed in F0b,** by p (`FD-F0b-REPORT.md:125-128`):
  - A7 GiBUU, max |b| 0.3604 at R02;
  - the q3 tilt, 53.42/16, p 6.44e-06, max |b| 0.1287 at R15.
- **The q3 tilt is synthetic.** It is a within-(E_avail, W) reweight, 1 + a·z with a = 0.3, which keeps the
  (E_avail, W) marginal (`nd-unfolding/s5c_pseudo.py:56-95`; `FD-PLAN.md:142`). It is not a vertex (`FD-PLAN.md:200`).
- **C_model,5D already holds a GiBUU vertex.**
  - s_k = X_k/X_0 − 1, where X_k is the data unfolded with the prior reweighted to generator k.
    C_model,5D = Σ s_k s_kᵀ, with κ = 1 (`measurement-scoping/pv-ladder/H2-DEFINITION-DECLARATION.md:192-200`).
  - The GiBUU vertex holds 89.0 % of the trace (`measurement-scoping/pv-ladder/BUILD-REPORT.md:138-139`).
- **When the data were read:**
  - Stage G read the data against the generators on 2026-10-26 at 10:16:49Z (`FD-G-REPORT.md:37-39`).
  - f has been printed in `cmodel_5d.json` since 2026-10-24 (`FD-PLAN.md:377-381`).
  - U-PLAN fixed option (a)'s form, N1 quadrature over a declared truth set, in `e4916dca` at 2026-10-26T02:42Z. That
    is before Stage G's read.
  - C_resp was adopted from its own σ readout, before any data-against-generator χ²
    (`DECISION-20261026-joseph-adopt-cresp.md:8-13`). The safeguard U-PLAN names: "Deciding after Stage G's χ² are
    seen would make the choice of matrix depend on the comparison" (`measurement-scoping/assigned-uncertainties/U-PLAN.md:302`).
- **An added positive semidefinite term never raises any χ²,** since (C + A)⁻¹ ⪯ C⁻¹ for A ⪰ 0. So every option below
  that adds to the covariance moves every Stage G χ² down or leaves it unchanged. This plan computes none of them.

### 2.2 The options

**(a) An assigned non-closure term from the measured bias.**
- **Construction:** U-PLAN's form, C_FD = Σ_T b_T b_Tᵀ, over a declared truth set of one truth per generator family
  plus the q3 tilt.
  - It is labelled "fake-data residual bias; not a calibrated bound".
  - It is printed both as a named line and as a second total, C_total + C_resp + C_FD (`measurement-scoping/assigned-uncertainties/U-PLAN.md:231-234`).
- **U-PLAN's own recommendation was not to add it:** "**(a), now.**" In U-PLAN's labels, (a) is "no: keep C_model,5D
  as the model term and the F0 limitation as stated" (`measurement-scoping/assigned-uncertainties/U-PLAN.md:231`). It gave three grounds:
  - C_model,5D is already the term comparable papers carry;
  - "C_FD built from F0's truths makes F0 uninformative";
  - adding it reopens a limitation Joseph accepted on 2026-10-25, and the term would be dominated by GiBUU
    (`measurement-scoping/assigned-uncertainties/U-PLAN.md:235-242`).
- **Its size** (`plan_arithmetic.out` §4). The sets here are illustrative; the set is Joseph's.

  | set added | median relative σ, from 7.29 % | largest cell | trace |
  |---|---|---|---|
  | A7 GiBUU only | 10.44 % | R06: 5.89 % → 27.82 % | ×3.19 |
  | q3 only | 9.08 % | R15: 7.94 % → 15.12 % | ×1.55 |
  | A7 GENIE+MEC, A7 NuWro, A7 GiBUU, q3 | 12.30 % | R06: 5.89 % → 29.29 % | ×4.04 |

- **What it would change:**
  - The reported covariance grows up to about fourfold in trace.
  - F0b's grade of every truth in the set passes by construction: against a matrix holding b bᵀ, χ² ≤ q/(1 + q) < 1.
  - Every Stage G χ² goes down or stays the same.
  - Nothing can then test the term, except 1A, 1B or 1B′ at their own truths.
- **Precedents** (verified; `limitation-plan/external_citations.tsv`):
  - T2K's oscillation analysis adds fake-data bias only above a threshold: "If a simulated data bias is greater than
    50% of the systematic uncertainty on a parameter then an additional uncertainty is added", as "the quadrature sum
    of the observed biases" (PRD 103, 112008 (2021), arXiv:2101.03779).
  - ATLAS's OmniFold measurement assigns an "unfolding prior" term from data-reweighted MC, plus a closure term (PRL
    133, 261803 (2024), arXiv:2405.20041).
  - In the papers checked, MINERvA and NOvA use warped or alternative-model fake data to choose the number of
    iterations, and state no separate residual-bias term:
    - MINERvA: arXiv:2002.12496, 2110.13372, 2106.16210, 2203.08022;
    - NOvA: arXiv:2109.12220.
    <!-- absence-ok: scoped to the five papers named, as read in their full texts by the delegated search (limitation-plan/external_citations.tsv); no claim about MINERvA or NOvA practice beyond them -->
  - U-PLAN's own survey agrees. Comparators use fake-data studies as validation, and a fake-data bias becomes an added
    uncertainty "only when it is not negligible… T2K's oscillation analysis (N1) has an explicit rule" (`measurement-scoping/assigned-uncertainties/U-PLAN.md:39-41`).
- **Cost:** 0 node-h. It is a login-node builder on committed readouts, plus a declaration and a binding: about one
  session-day.
- **Avoiding tuning to the data:** this is not fully possible, because adoption would come after Stage G's read. It is
  limited by:
  - the pre-read U-PLAN form, with no κ and no threshold choice;
  - a truth set fixed by family, not by which truths fail;
  - both totals printed.
- **Likely effect: re-describes.** The uncovered bias becomes a covered but untestable term. It removes "not covered"
  only by construction.

**(b) A generator-shape component built from the GiBUU or q3 truth.**
- **Built from the existing vertex directions, it cannot cover the bias, even scaled without limit.**
  - **Exact bound, GiBUU vertex alone.** Take M as the grade matrix and the GiBUU vertex s added at scale κ.
    Sherman–Morrison gives χ²(∞) = χ²_in − (χ²_out − χ²_in)/q, with q = sᵀM⁻¹s ≥ max_c s_c²/M_cc.
    - This uses only the readout's χ² and diagonals, so it is exact.
    - q ≥ 1.700, at R02, where s = −0.1111 and σ = 0.0852.
    - **A7 GiBUU stays at χ²₁₆ ≥ 123.50** in F0b (≥ 146.92 in F0). Stage 0c GiBUU stays at ≥ 21.63
      (`plan_arithmetic.out` §1).
  - **All three vertices scaled together.** This is the κ the decision fixes. The rank-3 limit is
    min_a (b − Sᵀa)ᵀ(C_e + C_resp + N)⁻¹(b − Sᵀa) (`plan_arithmetic.out` §1b).
    - The readout records only the diagonal of the noise N_T = Cov_i(r)/B_T (`FD-PLAN.md:237`). With diagonal N, the
      readout's χ² is reproduced to about 0.1 %.
    - Any positive semidefinite N_T with that diagonal satisfies 0 ⪯ N_T ⪯ tr(N_T)·I. That gives a rigorous bracket.

    | truth | all vertices, diagonal N [bracket] | own vertex left out [bracket] | p = 0.01 at |
    |---|---|---|---:|
    | A7 GiBUU | **116.15** [112.12, 116.43] | 150.24 [144.30, 150.90] | 32.0 |
    | q3 tilt | 51.31 [48.21, 51.55] | — | 32.0 |
    | Stage 0c GiBUU | 22.81 [21.77, 22.90] | 25.39 [24.53, 25.48] | 32.0 |
    | A7 NuWro | 18.38 [17.60, 18.41] | 18.99 [18.31, 19.02] | 32.0 |

  - **This answers the premise.** F0b's in-sample grade, with the GiBUU vertex included, still fails A7 GiBUU because
    the vertices point the wrong way, not because they are too small. No κ fixes it.
    - Heuristically, A7 GiBUU's bias has Euclidean cosine −0.485 with s_GiBUU, and 87.5 % of |b| lies outside it
      (`plan_arithmetic.out` §2). The bounds above are the rigorous statement.
    - Raising κ is in any case Joseph's: "Nothing rescales C_model. κ = 1 stands"
      (`DECISION-20261025-joseph-f0-limitation-stage-g-and-paper-scope.md:32`).
- **Built from the truth itself:** a component along b_T is (a) under another name. For the q3 tilt no generator
  exists, so this is the only construction.
- **Built from the generators' truth-level shape differences** (g_k/g_0 − 1): this would put into the covariance the
  very differences that the generator comparison measures. Stage G already notes that the vertices are partly built
  from the compared generators (`FD-G-REPORT.md:105-107`).
- **Precedents:**
  - MicroBooNE adds an alternative-generator universe, "To account for potential biases due to the nominal MC" (PRD
    108, 053002 (2023), arXiv:2301.03700).
  - H1's OmniFold measurement takes "the difference in the result when unfolding with Rapgap and with Djangoh" (PRL
    128, 132002 (2022), arXiv:2108.12376).
  - C_model,5D already follows this practice.
- **Cost:** 0 node-h for the arithmetic, plus a declaration.
- **Likely effect: neither removes nor reduces.** Built from the vertex directions it does not cover the bias; built
  from the bias, it is (a).

**(a′) For completeness: ATLAS's data-reweighted prior.**
- **Construction:** reweight the MC to the data at reco level, unfold, and take the difference (arXiv:2405.20041). This
  is F1-W's truth (`FD-PLAN.md:119`, `:493`).
- **Drawback:** it reads the data at reco level (`FD-DIRECTOR-RULINGS.md:63-68`), and it targets the data, not GiBUU.
  Whether it would cover the GiBUU-like bias is unknown.
- **Cost:** 0.36–0.6 node-h, cap 0.75 (`FD-PLAN.md:493`).
  <!-- absence-ok: "unmeasured" restates FD-PLAN.md:493's own status for the F1-W build -->
  The build's cost is unmeasured.
- **Likely effect: unknown.** It is a published OmniFold practice, but it would be a new component after the read.

**(c) Keep the limitation as stated.**
- **Construction:** state it with F0b's numbers:
  - A7 GiBUU's grade, in-sample and 8-cell χ², and its R02, R06 and R07;
  - the q3 tilt's χ²;
  - §2.2(b)'s finding that no scaling of the existing vertices covers it.
- **Precedent and decision:**
  - this matches the majority practice above, in which fake data validate and do not become terms;
  - it matches U-PLAN's recommendation;
  - it matches the decided treatment: "The fake-data limitation for GiBUU-like truths is stated where the GiBUU
    comparison is given" (`DECISION-20261026-joseph-5d-generator-comparison-presentation.md:24-25`).
- **Cost:** 0.
- **Likely effect: re-describes,** more precisely than now.

**Recommendation:** (c). If Joseph wants the bias in a number, use (a) in U-PLAN's pre-read form, printed beside the
present total and never only folded in. Either way, 1A, 1B or 1B′ is the only route to a bias test at a truth that is
not a vertex.

## 3. The χ²'s flux-correlation sensitivity

### 3.1 The facts

- **The flux block in Stage G's matrix** comes from 100 PPFX universes weighted by the ν-e + IMD constraint. n_eff is
  19.06 (`S1-REPORT.md:288`), and the block carries 0.1881 of C_total's trace (`S1-REPORT.md:277`).
- **The flux is common to data and predictions.** Every prediction is integrated against the same constrained CV
  flux. The predictions carry no flux uncertainty, since V_g is finite MC only (`FD-G-DECLARATION.md:222`, `:308`;
  `s5p/gen5d/README-gen5d-fluxfix.md:43-50`).
- **The flux block is almost fully correlated.** The R04–R08 correlation is +0.983 in the block alone, and 0.811 in
  the reported matrix (`FD-G-FOLLOWUP-REPORT.md:180-198`).
- **The leading 16-cell modes are cell contrasts in which flux cancels.** Their flux_ratio is 0.001–0.060.
  - In the GENIE CV top mode, the interaction and C_model blocks dominate; the flux block's share is 0.079.
  - GiBUU's top mode is the exception, with flux_ratio 5.10 (`FD-G-SENS2-REPORT.md:364-452`).
- **The 16-cell χ² when the flux off-diagonals are shrunk by 10 % (α = 0.1)** (`FD-G-SENS2-REPORT.md:107-155`):

  | prediction | α = 0 | flux family, α = 0.1 | joint c_e_systematic family, α = 0.1 |
  |---|---:|---|---|
  | GENIE CV | 109.35 | 83.35 (−24 %) | −35 % |
  | GENIE+MEC | 272.12 | 158.95 (−42 %) | −51 % |
  | NuWro | 188.03 | 103.72 (−45 %) | −52 % |
  | MnvTune | 329.72 | 172.92 (−48 %) | −56 % |
  | GiBUU (8 cells) | 58.46 | 55.00 (−6 %) | −14 % |

- **A factual mismatch for the director to route.** The draft `2d-closeout/stageF/methods/secondary-results/astra-consult-20261027/inputs/5d-addition.md:19-21`
  says "Weakening the flux correlations by 10 percent roughly halves it".
  - For the flux family alone the falls are 24–48 %, and 6 % for GiBUU.
  - The joint family's are 35–56 %.
  - The text is not this session's to edit.

### 3.2 Options

**3A. State it, in the decided one sentence** (`DECISION-20261026-joseph-5d-generator-comparison-presentation.md:26-27`).
- Feasibility: cost 0.
- It names the covariance group that carries the sensitivity.
- **Re-describes.** This is already decided.

**3B. Shape-only χ² beside the full one.**
- Feasibility: done (`FD-G-REPORT.md:67-95`).
- It removes only a normalization along f. The 16-cell gaps are 0.03–18.53, so it does not touch this sensitivity.
- **Inherent.** It is already printed.

**3C. χ² under the published constrained flux covariance.**
- Feasibility: not feasible.
- The only independent flux covariance in reach is the 2D release's `FluxCovariance` on the p_T–p_∥ bins
  (`2d-unfolding/compare_to_paper_fullcov.py:211-215`).
  - It cannot be mapped to cells that split on E_avail, q3 and W.
  - It likely uses a different constraint, FHC-only (`2d-closeout/c04-repair/REPORT.md:284-287`).
- MINERvA tabulates its flux constraints' covariances in the papers, on E_ν:
  - ν-e: PRD 100, 092001 (2019), arXiv:1906.00111;
  - IMD: PRD 104, 092010 (2021), arXiv:2107.01059;
  - ν̄-e + ν-e + IMD: PRD 107, 012001 (2023), arXiv:2209.05540.

**3C′. A projection check.** Compare the 2D analysis's own flux correlations with the published `FluxCovariance`
correlations on the 2D bins.
- Feasibility: cost 0, on a login node, plus a declaration.
- It tests the universe-based flux correlations on a projection the release covers.
  <!-- absence-ok: scoped to 2d-closeout/c04-repair/REPORT.md:284-287, which compares the per-cell σ (4.01 % vs 3.655 %) and states no correlation comparison -->
  c04-repair's disclosure compares the σ (4.01 % against 3.655 %), not the correlations.
- **Re-describes.** It supports the flux model, not the 5D cells.

**3D. A bootstrap or jackknife of the flux correlations over the 100 weighted universes, plus a uniform-weight variant.**
- Feasibility: cost 0, on a login node, plus a declaration.
  - The 100 per-universe `S1_Flux_*.npz` are committed (`measurement-paper/5d-community-20261024/s1/readout/s1_assembly/`).
  - `cresp.npz` and the predictions are on pscratch, so this is a login-node run like G-SENS2.
- It measures how well n_eff ≈ 19 pins correlations of 0.97–0.998. That gives a χ² band from estimation noise in place
  of an arbitrary α. c04-repair already notes a "rough ±16% relative sampling scatter on σ" (`2d-closeout/c04-repair/REPORT.md:288-289`).
- **Re-describes, on a measured footing.** It may **reduce** the stated sensitivity, if the band is narrow.

**3E. Profile the flux as nuisance parameters.**
- For a linear Gaussian model this gives the same χ² as the full covariance.
- **Inherent.**

**3F. Put the flux uncertainty on the predictions as well.**
- Not recommended: data and predictions share the CV flux, so it would double-count.

**Practice** (verified; `limitation-plan/external_citations.tsv`):
- MINERvA prints a log-normal χ² beside the standard one, "Because of the flux is a dominant uncertainty"
  (arXiv:2106.16210).
- T2K prints a shape-only χ² because "χ2 statistics may suffer from 'Peelle's Pertinent Puzzle'" (PRD 101, 112004
  (2020), arXiv:2004.05434).
- The standard reference on normalization-dominated χ² is D'Agostini, NIM A 346, 306 (1994).

The decision's "a property of the comparison, not a defect of the measurement" matches this practice.

**Likely effect: inherent.** 3D is the one option that adds a measurement: the estimation uncertainty of the
correlations the χ² depends on.

## 4. Constraints every option keeps

- **No cell merge or new cut after the data read** (`FD-DIRECTOR-RULINGS.md:21-33`; the framing decision, `:45-46`).
- **κ = 1,** unless Joseph changes it (`DECISION-20261024-joseph-5d-community-standard-route.md:44`;
  `DECISION-20261025-joseph-f0-limitation-stage-g-and-paper-scope.md:32`). Only (b) at κ ≠ 1 and 1B's optional adoption
  rule would touch it. Both are Joseph's.
- **Nothing runs before Joseph decides.** Each option needs its own declaration and binding. An extra block's
  "construction and digest must be fixed in the binding before the run" (`FD-G-DECLARATION.md:51`).
- **Every job runs under 12 h:**
  - on regular QOS of m3246, never premium, with no GPU;
  - with `--no-requeue`, ledgered from `sacct`, and stopped past 1.25× its projected wall (`FD-PLAN.md:481-483`);
  - with nothing written to CFS.

## 5. What Joseph decides

1. **Coverage:**
   - none;
   - 1C (0 node-h, descriptive);
   - 1A (0.84–1.25 node-h);
   - 1B′ (about 37–133 node-h);
   - or 1A then 1B (about 45–146 node-h, 1–2 weeks).

   The GENIE v3 configurations are his to choose, under the chooser rule.
2. **The bias:** (c), (a) in U-PLAN's form, or (a′). (a) and (a′) change the reported covariance.
3. **Flux:** 3A alone, as decided, or 3A with 3D and/or 3C′.

## Sources

- **Repository records:** read at `origin/main` `67f5600f`.
- **External papers:** each was verified on its arXiv full text and its INSPIRE record by a delegated read-only
  search. They are listed in [`limitation-plan/external_citations.tsv`](limitation-plan/external_citations.tsv).
- **Independent review:** two read-only rounds.
  - The first round's findings were folded in: the 1B control, the §1.3 assumption, 1B′, 1C, the rank-3 limit, the
    cost caveats, the absence scopes and the citation table.
  - The second round's findings were folded in too: every C_e block drawn, the one-sided reference, the rank-3
    bracket and the paths.

<!-- absence-ok: the coverage-test, GENIE v3 sample and flux-covariance absences are each scoped to the Search line below and to the records cited at each claim; no claim is made about files outside them -->
Search: "coverage" in FD-PLAN.md, FD-F0-REPORT.md, FD-F0b-REPORT.md, FD-DIRECTOR-RULINGS.md and the DECISION-2026102[4-7]-joseph-* records; "G18_10a|AR23_20i|GENIE v3" repo-wide (git grep) and KNOWN_ISSUES.md; "flux covariance|FluxCovariance|NuEConstraint|IMD" repo-wide (git grep) @ 67f5600f
