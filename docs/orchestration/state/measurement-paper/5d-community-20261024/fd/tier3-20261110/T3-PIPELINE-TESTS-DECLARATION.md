# T3 DECLARATION: where configuration (e)'s retained prior stops falling — noise-free pipeline tests at the two flagged truths (2026-11-10, rev 1, DRAFT for coverage-5b-audit and the director's binding; nothing runs)

**By:** session tier3-design, at the director's brief and ruling of 2026-11-10.

**Authority.**
- Joseph, 2026-11-10 (`DECISION-20261110-joseph-confirm-round-scope.md`, "What is decided" item 2): "Tier 3 joins the
  post-LL5D task list. If usage allows, its design and declaration start earlier, but no Tier 3 job runs before the
  LL5D readout without the director's go."
- Compute that resolves a limitation is under `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md`
  item 2 (#640), as `FD-PRR-DECLARATION.md` cites it. The cap here, 10.0 CPU node-h (§9), is far below half the group
  balance. The director checks the balance at binding.

**Status.**
- Rev 1 fixes the question, the arms, the quantities, the readings, the controls, the price and the licences.
- **No code is written yet.** Following FD-PRR's sequence, the code, its digests, its tests and a mutation receipt
  come in rev 2, after the director rules on rev 1's §12 questions. Design and code are then audited together.
- Nothing runs before the audit, the binding **and** the director's go after the LL5D readout.
- Paths are relative to `docs/orchestration/` unless they start with `nd-unfolding/` or `docs/analysis-note/`. Every
  `file:line` is at main `4231b14d` unless another commit is named.

**MEASURES:** in simulation only, on R00–R15, at the two flagged truths (A7 GiBUU hybrid, q3 tilt), with FD-PRR's
noise-free background-inclusive construction at FD-PRR's split:
- configuration (e)'s retained fraction ρ at **every** iteration k = 1…50 (§4.1), and the same trajectory when one
  pipeline component is replaced at a time (§3);
- beside ρ: the bias component perpendicular to the departure, the RMS relative bias and the noise-free χ² (§4.2);
- at every k, the reconstruction-level closure after step 1 and after step 2 (§4.3).

**CITABLE FOR:**
- each arm's ρ(k), b_∥(k), b_⊥(k), RMS b(k) and noise-free χ²(k) at each flagged truth, labelled "noise-free, one MC
  split, simulation only";
- each arm's reco-level retained fractions ρᴿ₁(k), ρᴿ₂(k);
- the classes of §5.1 (TR-1) and §5.2 (TR-2), the trajectory classes of §5.3 and the location classes of §5.4;
- the composite labels of §5.5, each worded "consistent with", as defined there;
- the measured cost per arm.

**NOT CITABLE FOR:**
- **a cause beyond the "consistent with" labels.** An arm that lowers ρ shows that changing that component is
  *sufficient* to lower it, in noise-free simulation at these truths. It does not show that the component is the only
  one, or that the fixed point would move the same way on data;
- **an estimator change.** No arm is adopted. Two arms (MO, OP) use the true per-event weight, which no data analysis
  has. They are diagnostics by construction. Any change to the reported procedure would need Joseph's decision and
  its own held-out test (FD-PRR §6 and its ruling 1, applied here);
- **any held-out performance claim, or a statement that an arm "would pass".** Nothing is selected on these truths;
- **Table II or its grades;** coverage, an interval or a measurement; **any data quantity**;
- **any result before it is read once under §7, after the LL5D readout;**
- **paper or note wording.** Any sentence goes through the paper lane, a PRD-referee read of the exact wording, and
  Joseph.

## 1. What the records already establish

### 1.1 What the referees asked

- **Claude Opus, M2** (`state/2d-closeout/stageF/methods/secondary-results/referee-methods-confirm-20261110/claude.txt:51-71`):
  four noise-free tests — "(i) oracle miss weights, i.e. the true reweighting applied to misses; (ii) the refinement
  disabled, on signal-only pseudo-data; (iii) a reconstruction-level closure after step 1 at each iteration, which
  separates 'step 1 cannot match the pseudo-data' from 'pull-back or step 2 loses the information'; (iv) a weighted
  version of the miss regressor" (`:60-64`). It also asks for "the component of the bias orthogonal to the departure
  alongside ρ" (`:69`). Its §5 (`:214`, `:224`) asks that the diagnoses not stop at "cause unknown" where the evidence
  points to testable causes.
- **GPT, major issue 1** (`…/gpt.txt:11-17`): a signed ρ "cannot by itself rank accuracy"; report "the bias component
  perpendicular to the injected deformation alongside its parallel component and total norm" (`:17`).
- **Joseph** put the tests after LL5D (`DECISION-20261110-joseph-confirm-round-scope.md`, item 2).

### 1.2 The premise, corrected against the readout

**Claude M2's first paragraph says that more capacity, and at the q3 tilt more iterations, *increase* ρ (`claude.txt:53`).
The FD-PRR readout shows the opposite direction.** The readout is `fd/receipts-prr/read/cluster/readout.json`
(sha256 `9238f22bfe29685e33c1d5bb46da3938a3ebfdc93a54575a4fe99de3a7af9ead`, re-measured), keys `table.<level>/<truth>/s991000.rho`:

| level | A7 GiBUU | q3 tilt |
|---|---:|---:|
| K = 2 | 0.168 | 0.235 |
| **K = 5 (B0)** | **0.125** | **0.179** |
| K = 10 | 0.113 | 0.172 |
| K = 20 | 0.104 | 0.172 |
| K = 50 | 0.094 | 0.163 |
| capacity 25/4 | 0.355 | 0.499 |
| capacity 400/31 | 0.103 | 0.158 |
| capacity 1000/63 | 0.102 | 0.163 |

- More iterations and more capacity **lower** ρ at both flagged truths. Every step is smaller than FD-PRR's bar of
  0.05, and one capacity step (q3, 400/31 → 1000/63) rises by 0.005.
- FD-PRR's PR-1 class "increases" (`readings.PR-1`) means, by `FD-PRR-DECLARATION.md` §5.1, that *some tested level
  raises ρ relative to B0*. The levels that do so are the **lower** ones: capacity 25/4 (+0.23, +0.32), K = 2 at q3
  (+0.057) and the two-observable mask O2. The paper printed the bare class (the confirming round's manuscript,
  `…/manuscript-confirm.blind.txt:628-631`), and both referees read it as a direction.
- The director confirmed this against the readout on 2026-11-10 and ruled that this declaration ask the corrected
  question (§2). The director is correcting the decision record and the paper's class wording. Neither is this
  lane's.

**What is anomalous:**
- On the same pseudo-data, exact binned IBU passes the truth within three iterations and then overshoots
  (`readout.json` key `ibu.K<k>/<truth>/s991000.rho`): at A7 GiBUU, +0.230 at K = 1, −0.016 at K = 3, −0.116 at K = 5,
  −0.247 at K = 200; at q3, +0.360, −0.020, −0.130 and −0.377.
- (e)'s ρ falls by 0.031 (A7) and 0.016 (q3) from K = 5 to K = 50, and by 0.022 and 0.020 from 100/8 to 400/31.
  From the PRR's five K points, (e) either approaches a fixed point well above 0 or converges very slowly. Which of
  the two, and why, is not measured.
  Search: the search of §1.5, @ 4231b14d.

**Context only, not ρ.** The supplement's statement that 10–20 iterations raise a model-dependence proxy (0.314 at
k = 5, at least 0.384 at k = 10, 15 or 20; the confirming round's `…/supplement-confirm.blind.txt:797-800`) is a
different quantity. It is the largest residual proxy over the s5p development truths, on the J and H2 cells, in a
construction without background (`RECORD-20260927-s5p-stage2-exit.md:114-117`). It is not the retained fraction on
R00–R15, and this study does not read it.

### 1.3 The components the tests isolate, in the bound code

| component | where | what it does |
|---|---|---|
| the probability clip | `nd-unfolding/omnifold_nn_core.py:152-155` | w = p/(1−p) with p clipped to [10⁻⁶, 1 − 10⁻⁶] (`:154`) |
| step 1, in-sample | `omnifold_nn_core.py:251-257` | the classifier is fitted on reco MC at w_push·w_reco against the measured side, and evaluated on the same MC rows (`:257`) |
| **the miss regressor** | `omnifold_nn_core.py:258-260` | `reg.fit(MCgen[pass_reco], new_w[pass_reco])` with **no sample weight** (`:259`); misses get `reg.predict` (`:260`) |
| the pull | `omnifold_nn_core.py:261` | w_pull = w_push · new_w, no renormalization |
| step 2 | `omnifold_nn_core.py:263-266` | the classifier separates MCgen at w_truth from MCgen at w_pull·w_truth; w_push is its p/(1−p) |
| the extraction | `nd-unfolding/s5c_unfold.py:135-146` | the truth histogram at w_push·w_truth, efficiency-corrected |
| **the refinement** | `nd-unfolding/s5e_trace.py:424-435`, `nd-unfolding/s5n_pseudo.py:264-282` | the Stay-Positive classifier at 400/31 (configuration R, `s5e_candidate.install`, `s5p_nullexp.py:287`) maps {observed at +count} ∪ {template at −weight} to non-negative weights. **With no template rows it does not run** (`s5e_trace.py:428-429`) |
| the pseudo-data | `s5n_pseudo.py:117-167`, through `s5p_nullexp.build` (`s5p_nullexp.py:240-257`) | half B's reco rows at 2·w_reco·r plus source-C background, at their means under `--expectation`; truth = half B reweighted by r. `build_pseudo` already takes `no_background` (`s5n_pseudo.py:118`, `:136-137`, `:144-145`) |
| the truth weight r | `s5p_nullexp.py:299` | `s5p_truths.hypothesis_weight`, known per MC event |

The paper describes them at S4 (`docs/analysis-note/supplemental_body.tex:171-177` on #977's branch
`draft/methods-short-20261109` at `10b88ad9`): misses "receive weights predicted by an unweighted regression of the
step-1 weight on the truth observables"; p is "restricted to [10⁻⁶, 1−10⁻⁶]"; "no renormalization between
iterations"; each classifier is "trained on the full sample to which it then assigns weights".

### 1.4 The instrument already exists

`nd-unfolding/s5e_trace.py` (the s5e diagnosis tracer, `OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md` §1) traces
one unfold **without re-implementing the loop**:
- It rebinds `omnifold_nn_core.make_estimators` so the loop receives thin wrappers around its own three estimators
  (`s5e_trace.py:132-197`).
- It rebuilds w_pull and w_push at every iteration and checks them **bitwise** against what the loop hands to the
  next step. It also recomputes the final unfold from the last w_push and requires equality (`:200-233`, `:256-259`).
  A run that fails any check writes nothing.
- It records truth functionals from w_pull and w_push and reco-level folds of both beside the measured side, at every
  iteration (`:320-339`).
- It already has one miss intervention, `--missed unity`: misses keep new_w = 1 (`:166-168`, `:235-240`).

**Two consequences for the design:**
- **One 50-iteration traced unfold gives the whole trajectory k = 1…50.** The loop's state after iteration k does not
  depend on the total count (`omnifold_nn_core.py:248-266`), and the estimators are deterministic at fixed threads
  (`s5c_unfold.config_params("deterministic")`). Control C-PAIR (§6) checks this bitwise against FD-PRR's own K = 5,
  10, 20 and 50 products.
- **The arms are wrapper changes, not edits.** Each intervention acts on what one wrapped estimator returns or
  receives. No production module is edited.

### 1.5 What is not measured
<!-- absence-ok: a section heading; the section's claims carry their search at its end -->

No record measures any of the following on R00–R15 at the flagged truths:
- ρ beyond the five K points of FD-PRR, or its limit;
- the effect of oracle or weighted miss weights, or of signal-only pseudo-data, on ρ;
- the reco-level closure per iteration.

**Related measurements at other functionals and constructions.** They set expectations for two arms, and none
answers them here:
- **For MO, MW and OP:** the s5e diagnosis (J/EW functionals, no background, B0 before R) found that step 1
  "reproduces ≥ 99.2% (EW projection) of each departure's reco-level signal, while truth residuals of median 5–11% and
  maximum 38–74% remain", and that "the missed-event regressor is not responsible for E_avail"
  (`OUTCOME-20260926-…:34-42`). The GBDT successor report cites s5e for "step 2 reproduces step-1 truth sums to 0.11%"
  (`state/next-preparation-20261009/gbdt/REPORT.md:178`).
- **For SO:** s5n's signal-only experiments on the same seeds reproduced the departure residuals (correlation 0.9994
  and 0.9993), "a property of the estimator, not of the background method" (`state/measurement-scoping/SCOPING.md:183`;
  also `:56`). At J, D-ID found signal-only close to the noise-free trace (FD-PRR §9).
- **What they do not measure:** ρ on R00–R15, the flagged truths under (e) with its 400/31 refinement, a per-iteration
  reco closure, or oracle and weighted miss weights. If SO or MU show "no effect" here, that agrees with these records.
  It is not a new finding.
<!-- absence-ok: scoped to the search below and the hits read; not a claim that no result exists elsewhere -->
Search: signal-only; weighted regress; oracle miss; missed unity|--missed (`git grep -l -i -E`, over
docs/orchestration and docs/analysis-note) @ 4231b14d, intersected with retained fraction|retained prior|R00.R15|rho|ρ:
68 files. Of them, 56 are paper or note text and its revision records (drafts, rater copies, ledgers, gap tables,
inventories), referee and consult reports, the CATALOG, and one 2026-08-10 verifier transcript. The 12
measurement and planning records were opened at their matching lines (FD-CT-3B, FD-F0, FD-F1, FD-PLAN, the
measurement-paper PLAN and EVIDENCE-MAP, the pv-ladder declaration, SCOPING, the GBDT report and its review,
`make_values_fived16.py`, an astra consult). Their signal-only closures are at the nominal truth, the J cells or the
pv-ladder, and none measures the quantities above. "reco-level closure" gives no hit.

## 2. The question

At R00–R15 and the two flagged truths, with FD-PRR's noise-free pseudo-data:

1. **Does (e)'s ρ(k) approach 0, cross it, or level off above it as k grows to 50?**
2. **Which pipeline component sets that limit?** Each arm replaces one component (§3). An arm that moves the limit
   implicates that component, and an arm that does not clears it, at these truths.
3. **Where is the departure lost?** Does step 1 fail to match the pseudo-data at reco level, or does the pull-back
   and step 2 lose what step 1 matched, or are both matched while the truth is not (§4.3)?

It cannot answer:
- why, beyond "consistent with" (§5.5);
- whether any arm is a better estimator;
- anything about data.

**A test that finds no cause is a valid outcome.** If no arm moves the limit and the reco closure is matched, the
result is "unattributed" (§5.5), and the paper keeps the limitation with the tests now run.

## 3. Design: one traced unfold per arm, paired on FD-PRR's pseudo-data

### 3.1 The baseline and the pairing

- **B0 is configuration (e)**, as in FD-PRR §3.1: the Stay-Positive refinement at 400/31 and the three OmniFold
  estimators at 100/8, run through `s5p_nullexp.py --expectation --no-nuisance --mc-fraction half`.
- **The pseudo-data are FD-PRR's, unchanged.** Each task runs FD-PRR's own queue line for (B0, truth, seed) through
  `s5p_nullexp.main`, unchanged, and is stopped where `build` returns (`s5p_nullexp.py:338`), as `prr_ibu.capture`
  does. The unfold is then `s5e_trace.traced_unfold` on `s5p_numerics.unfold_one`'s own inputs (`s5p_numerics.py:112-116`:
  `measured_side`, then `unf_inputs`), at 50 iterations.
- **The primary split is pseudo seed 991000,** FD-PRR's and FD-STAB's. Every arm runs at the same seed and split as
  B0, so each comparison is a paired difference at one truth and one split.
- **Same thread layout as FD-PRR:** 8 lanes × 32 threads, CPU, one node per job.

### 3.2 The truths

The two flagged truths only: **A7 GiBUU** and **q3**, with FD-PRR's truth files, read from FD-PRR's `CLOSURES`
through its pins, not retyped. The prior P is the nominal truth's x_true at the same split. x_true does not depend
on the unfold or on the background (`s5n_pseudo.py:156`, `:170`), so P is computed from `build` alone and checked
against FD-PRR's committed nominal products (C-P, §6).
<!-- absence-ok: a design statement about this study's own truth set -->

### 3.3 The arms

| arm | component replaced | what the wrapper does | bound code? |
|---|---|---|---|
| **B0** | none | the trace only | yes: `s5e_trace.traced_unfold`, `missed="regress"` |
| **MU** (miss unity) | the miss regressor → the plain EM treatment | misses keep new_w = 1, so their w_pull = w_push | yes: `missed="unity"` (`s5e_trace.py:238`) |
| **MW** (weighted miss regressor; referee test iv) | the unweighted regression (`omnifold_nn_core.py:259`) | the regressor's `fit` receives `sample_weight = w_push · w_truth` on the reco-passing rows, the population the loop is reweighting at that iteration; the target y is the loop's own | **no:** a new `fit` override on the wrapped regressor |
| **MO** (oracle miss weights; referee test i) | the miss fill | `reg.predict` returns r / w_push on the misses, so their w_pull is the true per-event weight r at every iteration. The reco-passing events are untouched | **no:** a new `predict` override |
| **SO** (signal-only; referee test ii) | the background and the refinement | `build_pseudo(…, no_background=True)` for that call only: no source-C background in the pseudo-data and no template, so `measured_side` skips the refinement (`s5e_trace.py:428-429`) and step 1 sees the signal pseudo-data at their expected counts | **partly:** the flag is bound; the one-call rebinding is new |
| **OP** (oracle pull; a control) | step 1 and the miss fill together | every event's w_pull is r: the step-1 wrapper's output gives new_w = r / w_push on the reco-passing rows and `reg.predict` gives it on the misses. Step 2 then sees the same inputs at every iteration, so 2 iterations suffice | **no:** a new `predict_proba` and `predict` override |

**Why these arms:**
- **MU, MW, MO** span the miss treatment: the EM assumption (misses follow w_push), a weighted fill, an unweighted
  fill (B0) and the truth. Misses carry 15.7–68.1% of a cell's sum (S4, as `claude.txt:54` quotes it). If any arm
  moves the limit, it is the treatment of the events that the reco data cannot see.
- **SO** is the referee's test (ii). It removes two things at once, because a refinement of an all-positive sample is
  not defined in this pipeline. The arm can therefore implicate or clear "background plus refinement", not either
  one alone (§10).
- **OP** is not a referee test. It gives step 2 and the extraction the exact answer for w_pull. ρ_OP is then the
  closest any arm can come to 0 through step 2 at this capacity, which bounds what MO, MW and MU can show (§5.2).
  It costs about 2% of the study's lane-seconds (§9).

**Not tested, and why:**
- **The clip** (`:154`). The referee names it, but no arm replaces it. A clip-free arm must handle p = 0 or 1 exactly,
  which is a new numerical construction. Instead, each traced iteration **records how many events sit at each clip
  edge**, in step 1 and in step 2 (descriptive, §4.4). If that count is 0 at every k, the clip did not act.
- **Renormalization between iterations** and **in-sample training** (`claude.txt:57-58`). Neither is replaced. The
  normalization is printed per iteration (the sum of w_push·w_truth over its value at k = 0; §4.4). Cross-fitting
  was measured by FD-STAB at A7 GiBUU: it moved the RMS fractional bias by at most 0.012
  (`OUTCOME-20261105-fd-stab-none-pass.md:34-36`).
- **Capacity and iterations** are FD-PRR's factors. They are not re-run; B0's trace extends iterations to every k ≤ 50.

## 4. Quantities, defined before any number is read

### 4.1 ρ and the trajectory

At truth T, arm A, split s and iteration k, on R00–R15, by FD-PRR §4.1 exactly, with `prr_read.rho`
(`nd-unfolding/prior_retention/prr_read.py:261-266`) applied to:
- **X̂(k) = M16 · x̂(k),** with x̂(k) the cross section extracted from w_push after iteration k by the production
  extraction (`s5e_trace.xs_from_push`), and M16 = `estimator_stability_analyze.cell_matrix` on the pinned H2
  definition (`nd-unfolding/estimator_stability_analyze.py:234-237`; `s1_assemble.py:103-122`), as `prr_read.py:437-438` uses it;
- X = M16 · x_true and P = M16 · x_true(nominal) at the same split.

So d = (X − P)/P, b(k) = (X̂(k) − X)/P, and ρ(k) = −Σ_S b d / Σ_S d² over S = {|d| ≥ 0.01}. It is undefined if |S| < 2.
ρ = 1 is the prior, ρ = 0 the truth, and ρ < 0 a result past the truth (overshoot).

**The truth-level pull:** ρ_pull(k) is the same with x̂ from w_pull instead of w_push. It shows what step 1 and the
miss fill imply at truth level before step 2 smooths them. It is printed and read by §5.4 only.

### 4.2 Beside ρ: the perpendicular bias, the RMS and the χ²

At every k, on all 16 cells:
- **b_∥,c = −ρ d_c** for c ∈ S, and 0 outside S; **b_⊥ = b − b_∥.**
- Because ρ is the least-squares coefficient of −b on d over S, b_⊥ is orthogonal to d on S. So
  ‖b‖² = ‖b_∥‖² + ‖b_⊥‖² exactly, with every cell outside S counted in b_⊥.
- **Printed:** RMS b (FD-PRR's `rms_b`), RMS b_∥ and RMS b_⊥ over the 16 cells, and the share ‖b_⊥‖²/‖b‖².
- **The noise-free χ²₁₆, p and max |z|:** FD-PRR's `table_ii` on r = X̂/X − 1 against F0b's grade matrix for T
  (`prr_read.py:269-274`), built by `prr_read.grade_matrices` from the same committed inputs under control C-CT.

This answers both referees' request: a signed ρ cannot rank accuracy, so ρ is never read alone (§5.5).

### 4.3 The reconstruction-level closure at every iteration (referee test iii)

**The reco cells.** The same 16 cells on the reco coordinates: the reco 5D fine-grid count histogram, summed over the
fine cells that S1's fine map assigns to each cell (`s1_assemble.fine_map`, `s1_assemble.py:103-117`). These are counts,
with no bin volume, so only ratios are used.

**The reco images,** for any per-event weight w on half A's reco-passing rows: F_c(w) = Σ w_reco · w over the rows in
cell c. Then:
- **D:** the measured side step 1 receives (refined in B0, MU, MW, MO and OP; signal-only in SO), binned on the same
  cells;
- **Fᴾ = F(1)**, the prior's image; **Fᵀ = F(r)**, the truth's image in half A.

**Three reco-level retained fractions,** each by `prr_read.rho`'s formula with the reco departure d^R = (D − Fᴾ)/Fᴾ:
- **ρᴿ₁(k):** b = (F(w_pull(k)) − D)/Fᴾ. *Does step 1 match the pseudo-data?*
- **ρᴿ₂(k):** b = (F(w_push(k)) − D)/Fᴾ. *Does the unfolded truth fold back to the pseudo-data?*
- **ρᴿ_D** (one per arm and truth, not per k): d = (Fᵀ − Fᴾ)/Fᴾ and b = (D − Fᵀ)/Fᴾ. *How much of the truth's reco
  image does the measured side itself lack?* That comes from the refinement and the A/B split.

**Also printed:** the reco departure's own size, RMS d^R over the 16 cells beside RMS d. If the reco departure is much
smaller than the truth departure, that is itself the information the data carry.

### 4.4 Descriptive per-iteration records (read by nothing)

- **the clip:** the counts of step-1 and step-2 evaluations at p = 10⁻⁶ and at p = 1 − 10⁻⁶;
- **the normalization:** Σ w_push·w_truth and Σ w_pull·w_truth over their values at k = 0;
- **the misses:** the mean fill on misses and their share of each cell's w_pull mass (`s5e_trace`'s
  `mean_fill_fail` and `truth_ew_fail_*`, mapped to R00–R15);
- the (E_avail, W) projections `s5e_trace` already records.

## 5. Readings, fixed before any number is read

**The bars:**
- δ_A = max(0.05, T_Q · s_A) for arm A, with s_A the sample SD over the five splits (991000, 994001–994004) of the
  paired difference ρ_A(k) − ρ_B0(k), at k = 50 for TR-1. Each is measured at A7 GiBUU and transferred to q3, as FD-PRR
  §3.5 does, and labelled a transfer.
- **T_Q = 8.6103** is the two-sided Student-t quantile on 4 degrees of freedom at 0.01/10: Bonferroni over the 10
  primary readings of §5.1 and §5.2 at familywise 0.01. The code will use 8.610301581379899 (`scipy.stats.t.ppf`),
  and a test will recompute it.
- The absolute floor 0.05 is FD-PRR's.

### 5.1 TR-1: each arm's effect on the limit (8 primary readings)

At T ∈ {A7 GiBUU, q3} and arm A ∈ {MU, MW, MO, SO}, at split 991000:
- Δ_A = ρ_A(50) − ρ_B0(50);
- **lowers the limit** if Δ_A ≤ −δ_A; **raises the limit** if Δ_A ≥ +δ_A; **no effect** otherwise;
- **undefined** if ρ is undefined at T for either arm (not expected at these truths: |S| = 16 at both in FD-PRR).
- Δ_A at k = 5 (the reported setting) is printed beside it and read by nothing.

### 5.2 TR-2: can step 2 and the extraction carry the exact pull weights? (2 primary readings)

At each flagged truth, from OP at split 991000:
- **"step 2 carries the truth"** if |ρ_OP(2)| < δ_OP, with δ_OP = max(0.05, T_Q · s_OP) and s_OP the SD of ρ_OP(2)
  over the five splits. That SD is the A/B split's own scatter, since OP has no other noise.
- **"step 2 does not carry the truth"** otherwise. ρ_OP is then the limit that step 2 and the extraction alone impose,
  at 100/8.

**How TR-2 conditions TR-1.** No arm that keeps step 2 can reach below about ρ_OP. So if TR-2 reads "does not carry",
an MO "no effect" is read as **"bounded by step 2"**, not as "the misses are cleared". The pairing is fixed here,
before any number.

### 5.3 The trajectory class of each arm (descriptive, 10 classes)

For arm A at truth T, with δ = 0.05 and δ_t = max(0.02, T_FD · s_F1) = 0.0211 (T_FD = 9.02937 and s_F1 = 0.0023377,
FD-PRR's iteration-factor floor; `readout.json` `readings.floor`; a transfer), one class:

| class | condition | what it means for B0 | what it means for an arm |
|---|---|---|---|
| **crosses** | min over k ≤ 50 of ρ(k) ≤ −δ | (e) passes the truth, as IBU does; then K = 5 is early stopping, and the limit is not a fixed point | the replaced component held (e) back from the truth |
| **reaches 0** | not crosses, and ρ(50) < δ | (e) converges to the truth within 50 iterations; the residual at K = 5 is slow convergence | the replaced component slowed convergence |
| **slow approach** | ρ(50) ≥ δ, and ρ(25) − ρ(50) ≥ δ_t | still falling at k = 50; neither a limit nor convergence is shown | the arm changes the rate, and the limit is not measured |
| **plateau** | ρ(50) ≥ δ, and \|ρ(25) − ρ(50)\| < δ_t | a fixed point above the truth, set by some component | if B0 also plateaus, compare the levels (TR-1): a lower plateau means the arm sets a share of the limit; the same plateau clears it |
| **rises** | ρ(50) − ρ(25) ≥ δ_t | more iterations move (e) back toward the prior | the replaced component prevented a divergence |
<!-- absence-ok: definitions of this study's own trajectory classes, not claims that a result does not exist -->

**What is already known about B0.** FD-PRR's five points for B0 are in §1.2, so B0's class is not blind. It is
printed as a description. The arms' classes and TR-1 are the test.

### 5.4 Where the departure is lost (descriptive, one class per arm and truth, at k = 50)

With δ_R = 0.05:
- **"step 1 does not match the pseudo-data"** if ρᴿ₁(50) ≥ δ_R;
- **"the pull-back or step 2 loses it"** if ρᴿ₁(50) < δ_R and ρᴿ₂(50) ≥ δ_R;
- **"reco matched, truth not"** if both are < δ_R and ρ(50) ≥ δ. The remaining truth departure then has almost no reco
  image under this response and these observables. No pipeline component is implicated, and the label is §5.5's
  "consistent with weakly constrained directions";
- **"closed"** if all three are < δ.

ρᴿ_D is printed beside each class. If ρᴿ_D ≥ δ_R, the measured side lacks part of the truth's reco image before any
unfold, and the arm's class is read with that disclosed.

**Why not IBU here.** IBU's crossing (§1.2) is not evidence that the information exists for (e). IBU's binned response
carries the prior's within-cell shape, so its overshoot can be a binning bias. GPT asks that "exact" binned IBU not be
read as an exact solution of the continuous problem (`gpt.txt:17`). The reco closure is the test that discriminates.

### 5.5 Composite labels, per flagged truth (descriptive; "consistent with" only)

Each label holds if its condition holds. Several can hold at once:

| label | condition |
|---|---|
| **consistent with a limit set at the misses** | TR-1 MO = lowers the limit |
| **consistent with a limit a feasible miss treatment lowers** | TR-1 MW or MU = lowers the limit |
| **consistent with a share from the background and refinement** | TR-1 SO = lowers the limit |
| **consistent with a limit set by step 2's representation** | TR-2 = does not carry the truth |
| **consistent with weakly constrained directions** | §5.4 = "reco matched, truth not" for B0 |
| **consistent with slow convergence, not a fixed point** | B0's class is "slow approach", "reaches 0" or "crosses" |
| **unattributed** | none of the above |

**ρ is never read alone.** Each label is printed with each arm's RMS b, RMS b_⊥ and χ² at k = 5 and k = 50. Where an
arm lowers ρ but raises RMS b_⊥ or the χ², that is printed beside the label, as GPT's major issue 1 asks.

### 5.6 Multiplicity

- **The primary readings are 10:** 8 from TR-1 and 2 from TR-2. T_Q bounds the familywise rate of a false class at
  0.01, under a Gaussian model of the paired difference across splits. The floor 0.05 makes it smaller.
- **Not covered:** the transfer of s from A7 GiBUU to q3, and δ_t's transfer from FD-PRR. Both are disclosed (§10).
- §5.3–§5.5 are descriptive and add nothing to the family.

## 6. Controls (each gates the readings; any failure is a STOP reported to the director)

| control | check |
|---|---|
| **C-PINS** | every bound module equals its digest before the runner is imported: FD-PRR's 15 `prr_probe.CODE_PINS`, plus `s5e_trace.py` and the rev-2 wrapper module. Each product records them |
| **C-TRACE** | `s5e_trace`'s own checks pass on every arm: the bitwise rebuild of w_pull and w_push at every iteration, one factory call, 50 traced iterations (2 for OP), and the final unfold recomputed from the last w_push (`s5e_trace.py:200-233`, `:256-259`). For MO, MW and OP, the rebuild uses the overridden values, which the wrapper records |
| **C-PAIR** | **B0's trace reproduces FD-PRR bitwise:** its unfold at k = 5, 10, 20 and 50, at A7 GiBUU and q3 on split 991000, equals `xsec_flat` of FD-PRR's `prr_{B0,K10,K20,K50}_{A7_gibuu,q3}_s991000.npz` (8 comparisons). At the floor splits, its k = 5 and k = 20 equal FD-PRR's `prr_B0_A7_gibuu_s99400[1-4].npz` and `prr_K20_A7_gibuu_s99400[1-4].npz` (8 more). Each FD-PRR product is staged once and checked against its committed digest (`fd/receipts-prr/{dry,iter,cap,misc}/cluster/log-*/SHA256SUMS`). The dry job runs A7's four comparisons first. A mismatch stops the study, since without it the trajectory is not FD-PRR's estimator |
| **C-ARM** | each intervention is shown to have acted, and nothing else: MU, every miss fill is 1; MW, the regressor received a `sample_weight` equal to w_push·w_truth on the reco-passing rows, bitwise, and the same target y; MO, w_pull on misses equals r to 10⁻¹² relative at every k, and the reco-passing rows' new_w equals the classifier's; SO, zero template rows, the refinement evidence reads `ran: False`, and zero background events; OP, w_pull equals r to 10⁻¹² relative at both iterations, and w_push(1) equals w_push(2) bitwise |
| **C-P** | P at each split, from `build`'s x_true at the nominal truth, equals M16 · `xtrue_flat` of FD-PRR's `prr_B0_nominal_s<seed>.npz`, bitwise |
| **C-CT** | FD-PRR's control: the grade matrices reproduce F0b's committed relative sigmas and its noise-free `closure_nuwro` grade (`prr_read.grade_matrices`) |
| **C-RECO** | the reco cells lose no row: Σ_c Fᴾ_c equals the reco-passing half-A weight inside the cells' fine bins, and D's sum equals the measured side's weight in the same bins, to 10⁻¹² relative |
| **C-SPLIT** | each product's split key is `s5c_pseudo.split_key_for(seed)` |
| **C-FIN** | every X̂(k), X, P and reco image is finite, every truth integral and Fᴾ_c positive, every C_T positive definite |

## 7. How the results are read, once

- **After every job has completed,** one reader run (`t3p_read.py`, rev 2) in a clean clone at the bound commit
  reads every product, applies §6, computes §4 and writes `readout.json` and `readout.txt`, under F0b's `LeakGuard`
  as FD-PRR's reader does.
- **No reading before that.** An incomplete study is reported as INCOMPLETE, and nothing in it is read.
- **One read.** The readout is committed as a receipt, with no class quoted in the commit, and reported to the
  director. The director reports it to Joseph before any paper text.
- **No re-read with changed bars, arms or classes.** Any change needs an addendum the director binds, and the change
  and the first readout are both kept.

## 8. What the readings can and cannot change

- **No estimator change follows from any reading.** MO and OP use the truth. MW and MU are findings about the
  mechanism. Adopting either would need Joseph's decision and its own held-out test.
- **Unchanged:** the reported result R00–R15, every covariance block, Table II, F0b's grades, FD-PRR's readout and
  REF-G1's.
- **Where the results go.** To the director, then to Joseph and the paper lane. Until then the paper states each
  untested cause as a limitation, with these tests as recommended future work (the 2026-11-10 decision, item 2).
  <!-- absence-ok: restates the 2026-11-10 decision's instruction for the paper until Tier 3 reports -->

## 9. Price, caps and job names

### 9.1 Measured walls and units

| what | wall | source |
|---|---:|---|
| the unfold unit in the current campaigns | 1,062 s per unfold at 32 threads (1.25 × 849.6 s) | `LL5D-DECLARATION.md:543`; checked per product by `LL5D-AMENDMENT-A1B.md:66` (§9, walls) |
| a data unfold of the estimator, K = 5 with refinement | 692.9 s at 32 threads (job 58911473) | `nd-unfolding/gbdt_model_dependence/inputs/inventory.json`, `selected[360].metadata.seconds_unfold` = 692.864 |
| **FD-PRR B0, K = 5**, this exact construction, 12 truths | mean 527 s, max 611 s | `fd/receipts-prr/*/cluster/log-*/tasks/prr_B0_*_s991000.log.txt`, `"seconds"` (my arithmetic) |
| FD-PRR K = 10 / 20 | means 864 / 1,523 s, max 1,036 / 1,721 s | same, `prr_K10_*`, `prr_K20_*` |
| **FD-PRR K = 50** | mean 3,636 s, max 3,822 s | same, `prr_K50_*` |
| FD-PRR K = 2 | mean 254 s, max 339 s | same, `prr_K2_*` |

The walls are close to linear in K: about 69 s per iteration and about 180 s fixed (refinement, load, extraction; my
arithmetic on the means).

**The conservative task units:**
- **a 50-iteration trace:** 1.25 × 3,822 s × 1.25 = 5,972 s, taken as **6,000 s** (5.65 LL5D units). The second 1.25
  is an allowance for the tracer's per-iteration reductions, which are unmeasured. The dry run measures them.
  <!-- absence-ok: this declaration's own pricing assumption, measured by its own dry run -->
- **an OP task (2 iterations):** 1.25 × 339 s × 1.25 = 530 s, taken as **600 s**.

### 9.2 The tasks

| block | tasks | traced iterations | lane-seconds at the conservative unit |
|---|---:|---:|---:|
| primary split 991000, A7 GiBUU: B0, MU, MW, MO, SO (50 it.), OP (2 it.) | 6 | 252 | 30,600 |
| primary split 991000, q3: the same | 6 | 252 | 30,600 |
| floor splits 994001–994004, A7 GiBUU: the same six arms | 24 | 1,008 | 122,400 |
| **total** | **36** | **1,512** | **183,600 (172.9 LL5D units)** |

That is 30 traced 50-iteration unfolds and 6 two-iteration unfolds. By wall, the 30 traces are worth about 207 FD-PRR
B0 unfolds (30 × 3,636 / 527). The priors need no unfold (§3.2).

### 9.3 Jobs, `--time` and the cap

Every job runs on one node with 8 lanes × 32 threads, CPU only, QOS regular, `-A m3246 -C cpu --exclusive
--no-requeue`. Every job is under 6 h, far under MaxWall (`DECISION-20261106-joseph-relax-12h-job-limit.md`).
Nothing is written to CFS. The charge is taken from `sacct`.

| job | contents | tasks | longest lane at the conservative unit | `--time` | node-h at most |
|---|---|---:|---|---|---:|
| `t3p_dry` | staging (§9.4); primary A7 GiBUU: six arms; C-PAIR at A7 first, then every control on these products | 6 | 6,000 s = 1.667 h; / 0.9 = 1.852 h; + 0.25 h staging = 2.102 h | 2:15:00 | 2.25 |
| `t3p_q3` | primary q3: six arms; C-PAIR at q3 | 6 | 1.667 h; / 0.9 = 1.852 h | 2:00:00 | 2.00 |
| `t3p_floor` | floor splits at A7 GiBUU: 24 tasks; C-PAIR at the floor splits | 24 | longest first onto 8 lanes: 4 lanes × 3 traces = 18,000 s, 4 lanes × 2 traces + 1 OP each = 12,600 s; 18,000 s = 5.000 h; / 0.9 = 5.556 h | 5:45:00 | 5.75 |
| **cap** | | **36** | | | **10.00** |

- **Expected:** at the measured K = 50 mean with a 1.1 tracer allowance (about 4,000 s per trace), the walls are
  about 1.4, 1.1 and 3.3 h: **about 6 CPU node-h** charged.
- **Cap: 10.0 CPU node-h,** the sum of the three limits.
- **It binds as FD-PRR's does** (FD-PRR §10.3):
  - the job script refuses unless its Slurm TimeLimit is at most the declared limit and its name is `t3p_<mode>`;
  - every task starts through a gate that projects the job's whole queue onto 8 lanes and refuses if it exceeds
    0.9 × `--time`;
  - `t3p_q3` and `t3p_floor` start only after `t3p_dry`'s DONE with C-PAIR passed, and their gate prices each arm
    at its dry-run rate;
  - a `--time` can be lowered from the dry run's measurements, never raised without an addendum the director binds;
  - after a stop there is no resume without an addendum, and the products already made are kept and pinned.
- **The order:** `t3p_dry` first, then `t3p_q3` and `t3p_floor` in either order. **Not before the LL5D readout,
  without the director's go** (the 2026-11-10 decision, item 2).

**Job-name family: `t3p_`** (`t3p_dry`, `t3p_q3`, `t3p_floor`).
<!-- absence-ok: scoped to the stated git grep over the whole tree at the named commit -->
Search: `git grep -n -i -E '(^|[^A-Za-z0-9])t3p_'` over the tree at `4231b14d` (PDFs excluded) gives no hit. The
shorter `t3_` gives 118, so it is not used. The director tells every fenced lane before any go (the job-family rule).

### 9.4 Inputs and shared reads

- **Staged once,** by `t3p_dry`, before its queue starts, with FD-PRR's `prr_probe.py stage` pattern: one O_NOATIME
  copy per file through REF-G1's `copy_noatime`. The digest is taken in the same pass and the copy is refused unless
  it equals the pin. Each file's own stat is recorded before and after, and no directory atime is read (FD-PRR §10.4).
- **What is staged:**
  - FD-PRR's six inputs, with FD-PRR's pins: `of_inputs_5d`, `bkg_dump`, `bank_cv`, the closure ratio and the two
    FD-STAB controls;
  - the fine-ratio rho arrays FD-PRR addendum A4 staged;
  - **the FD-PRR products C-PAIR and C-P read** (21 files: 16 for C-PAIR, 5 for C-P), each against its committed digest.
- After staging, every task reads only the staged copies. Each later job re-verifies every copy before its queue.
- **Sharing with LL5D and any other lane running then:** the director's go names the window, and the dry job refuses
  while any job of a family the director names is queued or running (`squeue`), as `prr_dry` did for `ens1_`.
- **The pscratch survival of FD-PRR's products** is not guaranteed. The 2026-11-10 existence check found all 181
  present (CATALOG, V-HALF rebin assessment purge check). If any staged product is missing at the dry run, C-PAIR
  cannot run and the study comes back to the director before any unfold.

**Who runs it.** A cluster lane the director assigns at binding submits the jobs, watches them and charges them from
`sacct`. This lane writes the design and the code and does not connect.

## 10. Disclosures and limits

- **Not blind.** The design was fixed after reading FD-PRR's readout (§1.2), including B0's five K points and IBU's
  trajectory. The arms' trajectories and every reco-level quantity are unseen. No data enters.
- **The truths are not held out,** and nothing is selected on them.
- **Two flagged truths only.** The other ten graded truths are not run, so an arm's effect elsewhere is unmeasured.
- **One construction.** Background-inclusive at FD-PRR's settings, except SO. SO changes the background and the
  refinement together (§3.3), so it cannot separate them.
- **The noise floor is measured at A7 GiBUU and transferred to q3,** with 4 degrees of freedom. δ_t is transferred
  from FD-PRR's iteration factor.
- **The limit is read at k = 50.** A trajectory still falling at k = 50 is classed "slow approach", and its limit is
  not measured.
- **The oracles use per-event truth weights that the MC defines.** MO and OP show what the pipeline would do with
  that information. They do not show what any data-driven fill could reach.
- **The clip, renormalization and in-sample training are recorded, not replaced** (§3.3).
- **MW's weights are one choice** (w_push·w_truth, the population being reweighted). w_push·w_reco is the other
  natural choice. It is not run, and a rev-2 question asks the director (§12).
- **The tracer overhead is unmeasured,** so the conservative unit carries a 1.25 allowance, measured by the dry run.
<!-- absence-ok: disclosures of this study's own scope and design choices, not claims that a result does not exist -->

## 11. Not changed

- **Unchanged:** the reported result, every covariance block, every fake-data readout, Table II, FD-PRR, REF-G1, the
  paper and the note.
- **No production or bound file is edited.** The rev-2 code goes under `nd-unfolding/tier3/` only.
- **Nothing is run, submitted, deposited or tagged.**
<!-- absence-ok: a statement about this declaration's own status -->

## 12. For the director: questions on rev 1

1. **OP (the oracle pull control).** It is not one of the referee's four tests. I added it because, without it, an MO
   "no effect" cannot separate "the misses are cleared" from "step 2 is the bound" (§5.2). It costs 6 short tasks,
   about 3,600 lane-seconds at the conservative unit (2% of the study). Keep it, or drop it?
2. **MW's weights:** w_push·w_truth (declared), or w_push·w_reco, or both? Both adds 6 traces. The cap does not
   change: the two primary jobs stay within 8 lanes, and the floor job's longest lane goes from 18,000 s to 18,600 s,
   still inside 5:45:00. The expected charge rises by about 0.1 node-h, since every node is charged by its wall.
3. **MU.** The `--missed unity` probe is bound and costs one trace per truth and split (6 traces). s5e found it did
   not help E_avail at J (§1.5), but not on R00–R15. Keep it?
4. **The floor at five splits** is 24 of the 36 tasks. FD-PRR's floor sat far below its 0.05 bar (9.03 · s ≤ 0.021,
   `readings.floor`). A two-split floor would cut the cap to 6.25 node-h, but its t quantile on 1 degree of
   freedom (about 636.6 at 0.01/10) would make the bar depend on s much more than the floor does. I recommend keeping five.
5. **Code next.** On your rulings, rev 2 adds `nd-unfolding/tier3/` (the wrappers, the runner, the reader, the job
   script, tests and a mutation receipt), as FD-PRR rev 2 did. It is written only as usage allows and is not run.
   <!-- absence-ok: a statement about this declaration's own status -->
