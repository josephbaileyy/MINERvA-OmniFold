# FD-STAB DECLARATION: a stabilisation probe of the estimator on simulated GiBUU-like pseudo-data (2026-11-03)

**Authority.** Joseph, 2026-11-02, asked whether to declare a stabilisation probe on simulated pseudo-data and
whether 1B's stage 1 should wait for it:
> Probe, 1B waits (Recommended)

The sha256 of the text plus a final newline begins `a830b9c7dd691581`
(`DECISION-20261102-joseph-bias-and-stabilisation-routes.md`, merged 86a7b4b4, "What is decided" item 1).

**Written by** the limitations-catalog session, at the director's offer. The design comes from the scope report
(`state/2d-closeout/stageF/methods/secondary-results/scope-bias-stabilisation-20261102/REPORT.md` §1, B2–B4, and §5).
**Process:**
1. code first, with mutation tests (§8);
2. an independent audit, which is not this session and is arranged by the director;
3. the director's two-step binding;
4. a dry run on real inputs at binding, by a cluster lane (§11).

Nothing runs before the binding.

**CITABLE FOR:** the probe's design, its criteria, its price and its code, as declared.

**NOT CITABLE FOR:**
- any result;
- a verdict on any estimator;
- the adoption of a winner. Adoption is Joseph's separate decision, covering the re-run, the 5D lateral block and the
  s5p joint tests (§10).

## 1. The question, and what it cannot answer

**Question:** does any of three changes to configuration (e)'s OmniFold estimators bring its rounding-scale numerical
spread under the predeclared stability bar, without making its bias worse at any F0b truth? The bar is median at most
0.3 and maximum at most 1.0 statistical σ (s5e amendment 3, A3).

**What it measures:** stability and bias of each candidate on simulated pseudo-data. It cannot measure a candidate's
statistical σ, coverage, model dependence on data, or behaviour on the data.

## 2. The candidates

Each candidate is configuration (e), with one change to the three OmniFold estimators only. Configuration (e) is
s5e candidate R: the Stay-Positive refinement at 400 trees and 31 leaves, and the OmniFold estimators at the
deterministic F2 parameters, 100 trees, 8 leaves, 5 iterations (`registry/ESTIMATORS.tsv`, `e-R-joint-test`). The
refinement classifier is unchanged in every candidate.

| candidate | change | why |
|---|---|---|
| **control** | none | the paired reference |
| **B2** | **2-fold cross-fitting** of the two OmniFold classifiers | It answers Q11 (training and evaluating on the same events) and is a candidate cure for the instability (Sonnet M5; scope §1 B2). K = 2 costs about one fit, because each of the two models trains on half the rows. K = 5 would cost about 4 fits. |
| **B3a** | `min_child_samples` = 10,000 on the three OmniFold estimators | Tree regularisation (Gemini 2; the decision's "for example `min_child_samples` and depth limits"). |
| **B3b** | `min_child_samples` = 100,000 | the same, ten times stronger |

**B2 in detail.**
- Each training row's fold is a keyed hash of its **position** (`FOLD_KEY`), never of its values, so the rounding
  perturbation the probe applies cannot move a row between folds.
- The model of fold f trains on the other fold. Every row the loop evaluates is predicted by the model that did not
  train on it.
- In step 2 the two copies of an event, labels 0 and 1, share a fold, so neither copy leaks into its own model.
- The regressor already predicts only rows it did not train on, so it is unchanged.

**Why B3's grid is these two points.**
- LightGBM's default `min_child_samples` is 20. On about 3×10⁷ training rows with 8 leaves that limit never binds,
  so a B3 at the default scale would test nothing.
- The two points are 10⁴ and 10⁵ rows.
- A depth limit was considered and is not tested. With `num_leaves` 8, `max_depth` 3 would force a balanced tree,
  which is a further candidate (about 1.6 node-h) left for the audit to ask for.
  <!-- absence-ok: describes this declaration's own design (a candidate or measurement the probe does not include), not a claim that a result is absent from the repository -->
- Each fit's minimum leaf count is recorded in every product (`stability_probe.fits`). That shows whether the limit
  bound.

**No B1.** The jitter ensemble is excluded by the decision.

## 3. Inputs: simulated pseudo-data only

**The data are never read.** The probe's stability runner refuses `--construction data`, and its closure runner
requires `--expectation --no-nuisance`. "No hyperparameter search was performed on data" therefore stays true.

**3.1 The stability input: a GiBUU-like truth that is not an F0b truth.**
- The truth is `eavail_shape` at amplitude 1 with `state/s5n/eavail-ratio-gibuu-over-genie.json` (sha256
  `45cc3e0a…`): s5e's GiBUU departure, where the rounding spread was measured at 7× its nominal size (KNOWN_ISSUES 80).
- The pseudo-experiment is one background-inclusive experiment exactly as `s5n_pseudo.build_pseudo` draws it:
  - signal MC split by keyed hash into the unfolding half A and the pseudo-data source B;
  - background into source C and template D;
  - Poisson pseudo-data from B and C.

  It runs through `s5p_numerics.py --construction pseudo` at pseudo-seed **990000**, a seed no campaign has used.
- The base is unfolded unjittered, and under jitter seeds **1–51**.

**Why this truth, not F0b's (the director's selection-contamination rule).**
- F0b's GiBUU truths are two:
  - Stage 0c GiBUU, `eavail_shape` with the flux-repaired ratio `c001dce8…`;
  - the A7 GiBUU hybrid, the fine-grid null `0080495c…`.
- The s5n ratio is neither. A test checks that its digest is no F0b pin (`TruthTable.test_stability_input_is_not_an_f0b_truth`).
- **Residual overlap, disclosed.** Stage 0c's own control requires its re-derived ratio to agree with this s5n ratio
  within 2% in every E_avail bin (`5d-design-20261023/stage0/stage0c_ratio.py`, `TOL`). So the stability input is a
  different truth in the same direction as Stage 0c GiBUU.
- It is also the development truth of the paper's IV E (Fig. 3), which was never held out.

**3.2 The bias input: noise-free closures at the 18 F0b truths.**
- Every truth runs through `s5p_nullexp.py --expectation --no-nuisance --mc-fraction half` at split seed 991000:
  - the full estimator, background and refinement included;
  - every Poisson draw replaced by its mean;
  - one MC split.
- The truth is the hypothesis null, with an alternative ratio on top where F0b's truth has one:

| F0b truth | hypothesis | alternative (truth, amplitude) |
|---|---|---|
| nominal, A7 MnvTune | `nullsJ/null-mnvtune_v1-J` (the prior) | — |
| W1 | MnvTune null | `s5n/eavail-ratio-nuwro-over-genie` (`eavail_shape`, 1) |
| W2, W3 | MnvTune null | `s5e/w2-…`, `s5e/w3-…` (`ratio_nd`, 1) |
| q3 | MnvTune null | `fd/stab/no-ratio.json` (`q3_given_eavail_w`, 0.3) |
| Stage 0c GiBUU | MnvTune null | `…/stage0/receipts-A/eavail-ratio-gibuu-over-genie-fluxfix` (`eavail_shape`, 1) |
| closure NuWro | MnvTune null | the pv-ladder ratio `prep/ratios/L-5D-PV/nuwro.json`, cluster-held, pinned `38e47eb6…`; truth kind from its `schema` |
| A7 GENIE CV, GENIE MEC, NuWro, GiBUU | `nullsF/null-<generator>-F` | — |
| P1r, P2r, P3r | MnvTune null | `altR/p1r` (`ratio_nd`), `altR/p2r` (`cond_ratio`), `altR/p3r` (`ratio_nd`), 1 |
| P1g, P2g, P3g | `nullsF/null-genie_cv-F` | the same three |

- **Every file is checked against F0's own pins**, not retyped: `fd_f0_regrade.RATIO`, `ALT` and `HYP`
  (`TruthTable` tests). The analysis refuses a product whose hypothesis or alternative digest differs.
- **The q3 tilt** is a built-in truth that reads no ratio. `s5p_nullexp` applies an alternative only when a file is
  given, so a declared placeholder is passed. A test shows the ratio is never read
  (`test_q3_truth_never_reads_its_placeholder_ratio`).
- **These are not F0b's products.** F0b graded pseudo-experiment means; these are noise-free closures at one MC
  split. Only the **paired** difference between a candidate and the control, at the same truth and split, enters a
  criterion.

## 4. The stability measure and criterion

**4.1 The protocol is s5e's.**
- Each jitter is an edge-safe ±½ float32-ulp perturbation of every input coordinate (`s5e_trace.jitter_coords`): MC
  truth, MC reco, observed and template. Values on a grid edge are never moved.
- A product whose fine-grid membership changes is refused (`s5p_numerics`, exit 5).
- The quantities are s5e's 153 reported functionals (`s5c_coverage.reported_functionals`), with
  r_j = F_j / F_base − 1.

**4.2 σ: the committed pseudo-data bootstrap σ of configuration (e).**
- It is `state/s5e/cand/assess_receipt.json` `sigma_rel_pct` (sha256 `84266e30…`, pinned in code): 100
  refit-per-replica bootstrap replicas of nominal pseudo-experiment 700000, estimator R. It is used as a relative σ.
- **Why this σ:**
  - it is committed and data-free;
  - the probe analyses pseudo-data, whose own statistical scale is a pseudo-data bootstrap's;
  - at nominal the rounding spread is 20× below its data size (KNOWN_ISSUES 80), so this σ carries almost none of
    the quantity being tested.
- **What it costs in strictness.** The data-bootstrap σ is 1.57× this σ (EW median, the same receipt), so the
  0.3 / 1.0 bars read here are stricter than s5e's on data by up to that factor. The readout also gives the
  data-σ-equivalent. The per-functional data σ is not committed, only its median.

**4.3 The statistic.**
- s5e's A3 statistic used **two** jitters (seeds 1 and 2): per functional, the larger |r|/σ of the two, then the
  median and maximum over functionals.
- A maximum grows with the number of jitters, so the 51 are **not** pooled into one maximum. Jitters (1,2), (3,4), …,
  (49,50) form 25 disjoint pairs, s5e's statistic is computed on each, and the criterion reads its **mean over the
  pairs**, with the standard error across pairs.
- Jitter 51 enters only the per-functional SD (n = 51 = 1 + 1/(2·0.1²), s5e's next-design item 1) and the readouts.
- **Criterion: mean median ≤ 0.3 and mean maximum ≤ 1.0.**

**4.4 G0, the informativeness gate.** The probe can discriminate only if the **control fails** the criterion on this
input. If it passes, no candidate can be shown to improve on it, and the verdict is UNINFORMATIVE (§6).
- My arithmetic, from KNOWN_ISSUES 80: the GiBUU departure on pseudo-data is about 7/20 of the data spread, about
  0.27 / 0.90 data-σ. In this σ that is about 0.43 / 1.42.
- So the control is expected to fail, but not by a wide margin. G0 states that risk rather than assuming it away.

## 5. The bias criterion: no worse at any F0b truth

**5.1 The metrics.**
- For each candidate and truth T, b = X / X_true − 1 on the 16 reporting cells, by S1's integration rule over the
  pinned H2 definition (`s1_assemble.functional_matrix`).
- Two metrics: RMS_T over the cells, and MAX_T = max |b|.
- These are relative and data-free. F0b's z needs the data central value f, which the probe does not read.

**5.2 "No worse", with a measured floor.**
- A candidate is no worse at T if **RMS_T(c) − RMS_T(control) ≤ Δ_RMS and MAX_T(c) − MAX_T(control) ≤ Δ_MAX**.
- Each Δ = 3 × 1.20 × √(s_c² + s_control²), where s is the metric's rounding-noise SD.
- s is propagated to first order from **that candidate's own** per-cell jitter SD: 51 jitters of §3.1, mapped to the
  16 cells. So the floor is measured and varies by candidate and by truth.
- **The factors.** 1.20 is the 95% upper factor of an SD estimated with 50 degrees of freedom, √(50/χ²₀.₀₅,₅₀) =
  1.199. 3 is the per-metric threshold. Over 18 truths × 2 metrics under Gaussian noise, the familywise rate of a false
  "worse" is about 0.6% if the SD is estimated correctly (the threshold is then 3.6σ), and about 4.9% if it is
  underestimated by the full factor (one-sided 3σ, 36 comparisons; my arithmetic).
- **The seed floor is zero**, because the estimator is seed-invariant (S1's seed block measured 0).
- **Sizing against the replica-count effect relayed from RPD part 2**, where α̂'s realization spread was driven by
  the replica count, 0.027–0.17 at 3 replicas:
  - here the SD estimate rests on 51 jitters, about ±10%, and the 1.20 factor bounds that;
  - what it does **not** cover is the realization spread of the one stability pseudo-experiment (§9).
- **The floor transfers from the stability input to every closure.** That is an assumption: the spread grows away
  from the prior, and the GiBUU departure is among the largest. It is stated, not measured.

**5.3 The GiBUU readout is descriptive.** The closure biases at A7 GiBUU and Stage 0c GiBUU are printed per candidate.
**Neither the bias criterion beyond "no worse", nor any other criterion, nor the tie-break may use them** (the
director's rule (i)). The verdict function takes no bias magnitude, and a test checks that an improvement at the
GiBUU truths does not move the verdict.

## 6. Verdict, tie-break and terminal branches

- **PASS:** a candidate passes if it meets §4.3 and is no worse at all 18 truths (§5.2).
- **UNINFORMATIVE:** G0 failed. **Terminal.** No estimator change proceeds from this probe. IV G stays as stated,
  and 1B stage 1 launches on the current estimator, as decided.
- **NONE_PASS:** no candidate passes. **Terminal**, with the same consequences.
- **WINNER, or CO_WINNERS:**
  - Among passers, the lowest mean maximum ranks first.
  - Every passer within one combined standard error of it, √(SE_c² + SE_best²), is a co-winner. A co-winner is
    reported, not broken by any other rule.
  - The GiBUU readout is never used.
- **What follows a winner:** the result goes to Joseph, whose adoption decision weighs §9's disclosure. 1B stage 1
  waits for that decision.

## 7. Compute

| item | unfolds |
|---|---|
| stability, per candidate: base + 51 jitters | 52 |
| closures, per candidate | 18 |
| **4 candidates** | **280** |

- **Per unfold:** 0.022828 CPU node-h, packed 8 per node (`FD-1B-STAGED-DECLARATION.md:530`, measured on S1).
- **Expected:** about **6.4 node-h**, if B2 costs about one fit, as two half-sample fits should.
  - This is above the scope's 3.2–6.4 because the scope priced only B2 and one B3 point. The control and the second
    B3 point were not in it.
- **Cap: 8.0 CPU node-h.** It covers B2 at up to 2× per unfold.
- **Stop rule:** if B2's first packed job runs over 2× the control's per-unfold wall time, stop and return to the
  director with the measured cost.
- **Rules:**
  - CPU only, regular QOS, `--no-requeue`, every job under 12 h;
  - nothing written to CFS from jobs;
  - charged from `sacct` and stopped past 1.25× the projected wall.
- **Reads.** The jobs read their inputs through the production loaders, which update atime. That is legitimate use
  (`DECISION-20261101-joseph-eventloops-copy-to-cfs.md` item 4). Any audit or inspection read uses O_NOATIME.
- **Calendar:**
  - Inputs: `of_inputs_5d.npz` and `bkg_dump.npz` (pscratch, the s5p bank), the s5p detector directory, and the
    pv-ladder closure ratio. Their retention is checked in the dry run.
  - HPSS is down until 2026-11-06 17:00, which matters only if an input must be restored.
  - The 1B redesign waits on this probe.

## 8. Code and tests

| file | role |
|---|---|
| `nd-unfolding/estimator_stability_probe.py` | the candidates; `install` rebinds `s5c_unfold.config_params`, `omnifold_nn_core.make_estimators` and `s5n_pseudo.write_product` for one invocation; the stability and closure runners (`s5p_numerics`, `s5p_nullexp`, unchanged); the declared task list |
| `nd-unfolding/estimator_stability_analyze.py` | §§4–6: the product checks, the criteria, the verdict |
| `nd-unfolding/tests/test_estimator_stability_probe.py` | 41 tests, with every refusal and criterion tested in the direction it acts and the other |
| `nd-unfolding/tests/estimator_stability_mutation.py` | 13 planted defects, each of which must be killed by its NAMED test; the unmutated suite must run all 41 tests in script mode |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/stab/no-ratio.json` | the q3 placeholder |

- **No production module is edited.**
- **The control runs through the same wrappers** as the candidates, so a wrapper cannot separate them. A test shows
  the wrapper is a bitwise pass-through.
- **Not testable locally:** LightGBM, SciPy and the real inputs are not installed here, so the tests use
  deterministic stand-in estimators and a small synthetic grid.
- The **dry run on real inputs at binding** (§11) is the first run of the code with LightGBM.

**Commands.**

    python3 -B nd-unfolding/tests/test_estimator_stability_probe.py          # 41 tests
    python3 -B nd-unfolding/tests/estimator_stability_mutation.py            # 13 mutations, all killed
    python3 -I nd-unfolding/estimator_stability_probe.py tasks --out TSV --npz … --bkg … --bank … --detector-dir … \
        --expect-npz-sha256 … --expect-bkg-sha256 … --closure-ratio-dir <pv-ladder dir> --runs <run root>
    python3 -I nd-unfolding/estimator_stability_analyze.py --runs <run root> --s5c-contract docs/orchestration/state/s5c/contract.json \
        --sigma-receipt docs/orchestration/state/s5e/cand/assess_receipt.json \
        --h2-definition nd-unfolding/pv-ladder/readouts/h2_definition.json --out <readout> --repo .

## 9. Disclosures and limits

**The director's selection-contamination rule (ii).**
- If a winner is adopted, the paper's fake-data results at the GiBUU truths are no longer fully held-out tests of the
  chosen estimator. The bias criterion "no worse" reads them, and the stability input lies within 2% in shape of
  Stage 0c GiBUU's.
- The adoption decision must weigh this, and the paper would have to say so.

**Limits:**
- **One pseudo-experiment realization** carries the stability statistic. Its realization-to-realization spread is
  not measured.
  <!-- absence-ok: describes this declaration's own design (a candidate or measurement the probe does not include), not a claim that a result is absent from the repository -->
- **B2's statistical σ is not measured.** Each half-trained model is noisier, and only an adoption re-run would
  measure that.
  <!-- absence-ok: describes this declaration's own design (a candidate or measurement the probe does not include), not a claim that a result is absent from the repository -->
- **The bias floor's transfer** from the stability input to the closures is assumed (§5.2).
- **G0 may fail.** The expected margin is small (§4.4).

## 10. Out of scope

Adopting a winner, and with it:
- re-running the bound validations;
- the 5D lateral block, which cannot be remade without new event loops;
- regenerating the s5p joint tests, or labelling them as from the previous estimator.

These are Joseph's separate decision (`DECISION-20261102-joseph-bias-and-stabilisation-routes.md`; scope §1, B1–B4).

## 11. Open items for the audit and the binding

1. **The pv-ladder closure ratio** (`prep/ratios/L-5D-PV/nuwro.json`, `38e47eb6…`). The dry run confirms the file's
   presence, its digest and its `schema`, which must name a declared truth kind (`SCHEMA_TRUTH`); the probe refuses
   otherwise.
2. **The dry run on a login node**, by a cluster lane, before step two of the binding:
   - one control stability unfold (the base) and one control closure (nominal);
   - one B2 and one B3b closure, to measure their per-unfold cost against the stop rule;
   - the products' `stability_probe` blocks read back.
3. **Retention** of the inputs (§7).
4. **The B3 grid.** The audit may ask for a depth-limit point (§2), at about 1.6 node-h.
