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
4. a dry run on real inputs at binding: one short single-node regular job, by a cluster lane (§11).

**Revised after the independent audit** (`coverage-5b-audit`, 2026-11-03, PR #720), item by item in §12.

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

**The data never enter a product.** They are loaded by the production loader (`s5c_unfold.load_inputs`), and the
jitter's grid-membership check reads their coordinates, but the pseudo-experiment's measured side is built from the
simulation and the background dump alone (`s5n_pseudo.build_pseudo`), and the unfolding takes only that side
(`s5e_trace.unf_inputs`). A test replaces the data and shows the unfolding's inputs unchanged
(`DataNeverInAProduct`). The stability runner requires `--construction pseudo` at pseudo-seed 990000, and the closure
runner `--expectation --no-nuisance` with the declared split. The refusal is decided on the runner's own parsed
arguments, so a repeated or abbreviated option cannot pass it, and no product is written unless that check ran
(`check_namespace`, `ArgvForms`). "No hyperparameter search was performed on data" therefore stays true.

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
  criterion. The analysis refuses a closure whose pseudo seed is not 991000 or whose MC fraction is not half, and
  requires each candidate's split key to equal the control's at every truth.
- **Nominal and A7 MnvTune are the same closure**: one hypothesis, no alternative, one split. The pair is kept as a
  **bitwise determinism control**: each candidate's two products must be identical, or the analysis stops. So **17
  distinct truths** are judged, and the familywise counts below are over 17 × 2 = 34 comparisons.

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
- s is propagated to first order from **that candidate's own** per-cell rounding SD: the base and the 51 jitters of
  §3.1, mapped to the 16 cells as X / X_base, and the SD **around their mean, with ddof = 1**. The base is one
  rounding realization like each jitter (KNOWN_ISSUES 80: the response to a rounding-level change is chaotic), so an
  SD taken around the base would have expectation σ² + n_b², not σ²; in simulation its median is 1.22σ and its p95
  2.2σ, which the 1.20 factor does not bound. Around the mean the p5–p95 range is 0.84–1.16σ. So the floor is
  measured and varies by candidate and by truth. The per-cell SD and every Δ are recorded in the readout.
- **A zero floor is INVALID, not "worse".** If Δ_RMS or Δ_MAX is exactly 0 at a truth, the floor model has failed
  there (a cell where both estimators are exactly insensitive to rounding). That truth is recorded as INVALID, and the
  verdict is INVALID if a candidate that meets the stability bound has one (§6).
- **The factors.** 1.20 is the 95% upper factor of an SD estimated with 50 degrees of freedom, √(50/χ²₀.₀₅,₅₀) =
  1.199; the SD here has 51, so the factor is slightly conservative. 3 is the per-metric threshold. Over 17 distinct
  truths × 2 metrics under Gaussian noise, the familywise rate of a false "worse" is about 0.54% if the SD is
  estimated correctly (the threshold is then 3.6σ), and about 4.49% if it is underestimated by the full factor
  (one-sided 3σ, 34 comparisons; my arithmetic, 1 − (1 − 0.00135)³⁴).
- **The seed floor is zero**, because the estimator is seed-invariant (S1's seed block measured 0).
- **Sizing against the replica-count effect relayed from RPD part 2**, where α̂'s realization spread was driven by
  the replica count, 0.027–0.17 at 3 replicas:
  - here the SD estimate rests on the base and 51 jitters, about ±10%, and the 1.20 factor bounds that;
  - what it does **not** cover is the realization spread of the one stability pseudo-experiment (§9).
- **The floor transfers from the stability input to every closure.** That is an assumption: the spread grows away
  from the prior, and the GiBUU departure is among the largest. It is stated, not measured.

**5.3 The GiBUU readout is descriptive.** The closure biases at A7 GiBUU and Stage 0c GiBUU are printed per candidate.
**Neither the bias criterion beyond "no worse", nor any other criterion, nor the tie-break may use them** (the
director's rule (i)). The verdict function takes no bias magnitude, and a test checks that an improvement at the
GiBUU truths does not move the verdict.

## 6. Verdict, tie-break and terminal branches

- **PASS:** a candidate passes if it meets §4.3 and is no worse at all 17 distinct truths (§5.2).
- **UNINFORMATIVE:** G0 failed. **Terminal.** No estimator change proceeds from this probe. IV G stays as stated,
  and 1B stage 1 launches on the current estimator, as decided.
- **NONE_PASS:** no candidate passes. **Terminal**, with the same consequences.
- **INCOMPLETE:** the full run did not complete: a STOP, a failed task, or Slurm's limit (§7). Nothing is graded:
  the analysis requires the full run's `DONE` receipt, with all 128 tasks ended, rc 0, and no `STOP` or `FAILED` beside
  it, and otherwise reads no product. The receipt is derived from `--runs` (`<OUT>/runs` gives `<OUT>/log-full/DONE`),
  so a receipt from another run cannot stand in, and an explicit `--receipt` naming another file is refused
  (`EndToEnd.test_the_receipt_is_this_runs`). The outcome is reported to the director, and no estimator is adopted. Only an
  addendum the director binds can complete the run (§7).
- **INVALID:** a candidate that meets §4.3 has a zero floor at some truth (§5.2). **Terminal for this analysis:** the
  readout goes to the director, and nothing is adopted from it.
- **WINNER, or CO_WINNERS:**
  - Among passers, the lowest mean maximum ranks first.
  - Every passer within one combined standard error of it, √(SE_c² + SE_best²), is a co-winner. A co-winner is
    reported, not broken by any other rule.
  - The GiBUU readout is never used.
- **What follows a winner:** the result goes to Joseph, whose adoption decision weighs §9's disclosure. 1B stage 1
  waits for that decision.

## 7. Compute

| item | unfolds | tasks |
|---|---|---|
| stability, per candidate: jitter 1 alone, then the base and jitters 2–51 in tasks of 4 (`STAB_CHUNK`) | 52 | 14 |
| closures, per candidate | 18 | 18 |
| **4 candidates** | **280** | **128** |

- **Per unfold:** 0.022828 CPU node-h, packed 8 lanes per node (`FD-1B-STAGED-DECLARATION.md:530`, measured on S1),
  so one unfold is 657 s of one lane (`UNIT_S`).
- **Packing.** One node, **8 lanes**, one task per lane at a time, all fed from one queue (`sbatch_fd_stab.sh`,
  `xargs -P 8`). The queue interleaves the candidates, so B2's cost is measured in the first round. With every task at
  most 4 unfolds, the lanes stay balanced: about 35 unfolds per lane. Each stability task passes its pairs as one
  token, `--pairs=…`: as two tokens, the runner's argparse reads the leading `-:-` as an option and exits 2. A test
  runs every queue line through the real runners' own parsers (`RealParsers`).
- **Expected:** 280 × 0.022828 = **6.39 node-h**, a wall of 6.4 h, if B2 costs about one fit, as two half-sample fits
  should.
- **The price is above the 3.2–6.4 node-h Joseph was shown** (`DECISION-20261102-…`), because the scope priced only
  B2 and one B3 point. The control is required: G0 (§4.4) cannot fail without it. The second B3 point is the grid's
  other end. A cap of 6.4 would mean dropping one of them, or stopping on any B2 overrun.
- **Cap: 8.0 CPU node-h**, for the dry run and the full run together. **It covers B2 up to about 1.7× per unfold**,
  not 2×. The lane sum at 2× is already 7.99, and the dry run's charge and the queue's tail come on top of it. The
  table below simulates the dry run and the full run through the real gate (the audit's simulator, committed as
  `fd/stab/gatesim/gatesim2.py`, with the dry run on 8 lanes and 120 s of setup per job; run without noise, it
  reproduces the seven cells re-run at this head). α is the dry run's per-unfold time over the full run's, which is not
  measured.
  <!-- absence-ok: describes a parameter of this declaration's own cost simulation and gate, not a claim that a result is absent from the repository -->

  | B2 factor | α = 1.0 | α = 0.9 | α = 0.8 | α = 1.1 |
  |---|---|---|---|---|
  | 1.5× | complete, 7.46 | complete, 7.44 | complete, 7.41 | — |
  | 1.6× | complete, 7.63 | complete, 7.60 | — | stop at once, 0.39 |
  | 1.7× | complete, 7.81 | complete, 7.78 | complete, 7.75 | — |
  | 1.75× | complete, 7.92 | complete, 7.89 | complete, 7.86 | — |
  | 1.8× | complete, 7.99 | complete, 7.96 | complete, 7.93 | — |
  | 1.85× | stop at once, 0.40 | stop at task 89, 6.95 | Slurm limit, 8.00 | — |
  | 1.9×, 2.0× | stop at once, 0.41–0.43 | — | — | — |

  Without timing noise, up to 1.7× the run completes for every α tried, and above about 1.8× it usually stops before
  the full run spends anything. The exception is a dry run faster than the full run (α < 1): the projection catches up
  only as full-run tasks finish. At 1.85×, α = 0.9 stops at task 89 after 6.95 node-h, and **α = 0.8 never stops: it
  meets Slurm's limit at 8.00 node-h, incomplete.**

  **With per-task timing noise** (the same simulator, with log-normal noise on each task's time; 40 seeds per cell,
  α 0.8–1.1, B2 1.0–2.0×; run by the limitations-catalog session on this probe code: `fd/stab/gatesim/sweep.sh`
  writes `sweep.txt`, and `summarize.py` prints these counts from it):
  - "Early" below is a stop within the first 16 queue lines, which spent at most 2.49 node-h in every seed; a later
    stop is "mid-run".
  - **At 2%:** every seed completes up to 1.75× for α 0.8–1.0. At α = 1.1 the run stops early from 1.5× (38 of 40
    seeds). At 1.8× and α = 1.0 the outcomes mix: 11 complete, 17 stop early, 11 stop mid-run, 1 meets Slurm's limit.
    At 1.85× and α ≤ 0.9, mid-run stops reach 8.00 node-h, and at α = 0.8, 24 of 40 seeds meet Slurm's limit.
  - **At 10%:** every seed completes up to 1.3× for α 0.8–1.0, and up to 1.5× for α 0.8–0.9. From 1.5× a stop can
    come mid-run with most of the cap spent, **up to 7.85 node-h** (1.75×, α = 1.0). A few seeds at α = 0.8 meet
    Slurm's limit (2 of 40 at 1.75× and at 1.8×).
  - The auditor puts the measured per-task spread at about 2% (MP1); that figure is not re-derived here.
  - The simulation lets running tasks finish after a stop, so its mid-run spends are upper figures. On the cluster,
    GNU xargs is expected to exit at once on a 255 without waiting for running tasks (not verified there; the BSD xargs
    of the local tests waits). The job then ends and Slurm stops them, and a stopped unfold leaves no product, since
    products are written to a temporary file and renamed (`s5n_pseudo.write_product`).

  **Authority:** Joseph's 2026-11-01 approval of compute that resolves a
  limitation (`DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md` item 2, #640): each campaign is
  declared, priced and bound, and one priced above half the group balance (2,074.5 node-h last recorded) returns to
  Joseph first. 8.0 is far below that.
- **How the cap binds, three ways:**
  1. **Slurm's own limit.** The dry run is submitted with `--time=0:45` (at most 0.75 node-h). The full run is
     submitted with `--time` equal to 8.0 minus the dry run's charged node-hours from `sacct`, so at most 7:15. On one
     node the charge cannot exceed `--time`.
  2. **The cumulative gate.** Before each launch, `estimator_stability_probe.py gate` prices the **whole remaining
     run, tail included**. The lanes start with what is left of the running tasks, and each unstarted task, in queue
     order, goes to the lane that frees first, as `xargs -P 8` feeds them. The projected wall is when the last lane
     finishes.
     - **Rates.** Each (candidate, kind) uses the mean per-unfold time of its finished tasks, falling back to the
       candidate's over both kinds, then to an assumption (B2 at 2×, the others at 1×). Unmeasured, B2 at 2× does not
       fit, so nothing starts on assumptions alone.
       <!-- absence-ok: describes a parameter of this declaration's own cost simulation and gate, not a claim that a result is absent from the repository -->
     - **The dry run's timings** are on the 8-lane basis (§11). The full run inherits them, so every candidate's rate
       is measured before it starts. The gate skips the dry run's eight tasks rather than re-running them, so their
       measured timings stand. Starts, ends and the job's start all come from one clock at sub-second resolution.
     - **If the projected total exceeds the cap's remainder, the gate stops before that launch** and the run comes
       back to the director to be repriced. That is what the gate guarantees: **it stops before any launch whose
     projected total, tail included, exceeds the cap's remainder.** It does not guarantee a complete run, or a stop
     that spends little. The projection is made from the tasks measured so far, so a dry run faster than the full run,
     or timing noise, can leave it low: a run can then stop mid-way with most of the cap spent, or meet Slurm's limit
     (the tables above). **The hard limit is Slurm's `--time` (item 1): 8.00 node-h.** The gate stops the audit's
     mixed case (B2 at 1.9×, the others at 1.1×, 8.31 in all) before it is spent
     (`Gate.test_the_audits_mixed_overrun_stops`).
  3. **The B2 rule.** No task starts once B2's measured per-unfold time exceeds 2× the control's, compared like for
     like: stability with stability, closure with closure.

  A stop writes `STOP` with the projection; nothing further starts; the products so far are kept; the run returns
  to the director with the measured cost. **Only a run whose every task ended, with no STOP and rc 0, writes a `DONE`
  receipt.** The full run refuses unless the dry run's receipt exists and every dry-run task ended. A failed task,
  a STOP and a Slurm time-limit kill each leave no receipt. The receipt's count of ended tasks is defensive: with rc 0
  and no STOP every task has ended, since the gate skips only a task whose end exists. Its test reaches it by removing
  an end during the run (`JobScript.test_an_end_lost_during_the_run_leaves_no_receipt`).
- **After a stop** (the director's ruling, 2026-11-03):
  - **No resume without an addendum the director binds.** The job refuses to re-run a mode whose log exists, so a
    stopped full run cannot be restarted by submitting it again. A fresh run beside it would re-launch finished tasks:
    the runner skips an existing product at once, so the task would record a near-zero time, the round-1 defect. An
    addendum states the new price, how the spend already made counts against the cap, and how finished tasks are kept.
  - **The products already made are kept and pinned.** The job writes `SHA256SUMS` of every product whatever the
    outcome (`JobScript.test_a_reprice_stop_keeps_and_pins_the_products_and_is_not_resumed`). A Slurm time-limit kill
    ends the job before it can, so the report pins them then.
  - **They are not graded until the probe completes** (§6, `EndToEnd.test_an_incomplete_run_is_not_graded`).
  - **If the probe is not completed, the outcome is INCOMPLETE:** reported, and no estimator is adopted.
- **Who runs it.** The limitations-catalog session, which wrote the probe, does not contact the cluster. The dry run
  and the full run are submitted, watched and charged from `sacct` by a cluster lane the director assigns at binding.
  The same lane pins the products and reports a stop or the completed run to the director.
- **Every job under 12 h:** 0:45 and at most 7:15. The longest task is 4 unfolds, 1.5 h at B2's 2×.
- **Rules:**
  - CPU only, regular QOS, `--no-requeue`, `--exclusive`;
  - nothing written to CFS from jobs;
  - the charge from `sacct`, in the report.
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
| `nd-unfolding/estimator_stability_probe.py` | the candidates; `install` rebinds `s5c_unfold.config_params`, `omnifold_nn_core.make_estimators` and `s5n_pseudo.write_product` for one invocation, and checks the runner's parsed arguments; the stability and closure runners (`s5p_numerics`, `s5p_nullexp`, unchanged); the declared queue and the dry run's eight tasks; the budget `gate` |
| `nd-unfolding/sbatch_fd_stab.sh` | the job: the dry run or the full queue, on 8 lanes, every task through the gate; a DONE receipt only for a complete, clean run |
| `nd-unfolding/estimator_stability_analyze.py` | §§4–6: the completeness check (INCOMPLETE), the product checks, the criteria, the verdict |
| `nd-unfolding/tests/test_estimator_stability_probe.py` | 94 tests, with every refusal and criterion tested in the direction it acts and the other; the job script is run locally on a stand-in deploy |
| `nd-unfolding/tests/estimator_stability_mutation.py` | 68 planted defects in the probe, the analysis and the job script, each of which must be killed by its NAMED test; the unmutated suite must run all 94 tests in script mode |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/stab/no-ratio.json` | the q3 placeholder |

- **No production module is edited.**
- **The control runs through the same wrappers** as the candidates, so a wrapper cannot separate them. A test shows
  the wrapper is a bitwise pass-through.
- **Not testable locally:** LightGBM, SciPy and the real inputs are not installed here, so the tests use
  deterministic stand-in estimators and a small synthetic grid.
- The **dry run on real inputs at binding** (§11) is the first run of the code with LightGBM.

**Commands.**

    python3 -B nd-unfolding/tests/test_estimator_stability_probe.py          # 94 tests
    python3 -B nd-unfolding/tests/estimator_stability_mutation.py            # 68 mutations, all killed
    python3 -I nd-unfolding/estimator_stability_probe.py tasks --out <OUT>/queue.tsv --dry-out <OUT>/dry.tsv \
        --npz … --bkg … --bank … --detector-dir … --expect-npz-sha256 … --expect-bkg-sha256 … \
        --closure-ratio-dir <pv-ladder dir> --runs <OUT>/runs
    sbatch --time=0:45 nd-unfolding/sbatch_fd_stab.sh dry <deploy> <pin> <OUT> 8.0
    sbatch --time=<8.0 minus the dry run's charge> nd-unfolding/sbatch_fd_stab.sh full <deploy> <pin> <OUT> <8.0 minus that charge>
    python3 -I nd-unfolding/estimator_stability_analyze.py --runs <OUT>/runs --s5c-contract docs/orchestration/state/s5c/contract.json \
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
2. **The dry run: one short single-node regular job** (`sbatch_fd_stab.sh dry`, `--time=0:45`), by the cluster lane
   the director assigns (§7), before step two of the binding. Its eight one-unfold tasks run on the **full run's 8 lanes**, so its timings are on
   the basis the gate uses. A login node's wall, or a four-lane job's, would not be.
   - The tasks (`DRY_TASKS`): each candidate's first stability task (one jittered unfold, through the stability
     runner); the control's nominal and A7 MnvTune closures (also the determinism pair); one B2 and one B3b closure.
   - The products' `stability_probe` blocks read back; the two control products compared bitwise.
   - Its products and timings carry into the full run, whose gate skips those eight tasks, so its charge is inside
     the 8.0 cap. The full run needs its `DONE` receipt.
   - **The environment:** the job sources `setup_salloc_env.sh` and refuses unless `lightgbm` and `scipy` import.
     No committed launcher records which environment the s5p runs used, so the dry run is where that is established.
3. **Retention** of the inputs (§7).
4. **The B3 grid.** The audit may ask for a depth-limit point (§2), at about 1.6 node-h.

## 12. The audit and its dispositions (`coverage-5b-audit`, 2026-11-03)

The audit (PR #720, comment 6610397251) found the design and the GiBUU separation sound, and asked for six changes
and thirteen tests. Each claim was checked against the code before it was changed.

| item | finding | disposition |
|---|---|---|
| R1 | each stability task was one 52-unfold call, about 9.5 h; the cap and the 12 h rule failed as packed | **accepted.** Tasks of 4 pairs, one 8-lane queue, the cumulative gate, `--time` as the cap's remainder, #640 cited (§7) |
| R2 | the argv refusal passed repeated, abbreviated and `=` forms | **accepted.** Decided on the runner's own parse; no product without that check; the five forms tested; §3 reworded |
| R3 | the floor's SD was taken around the base | **accepted.** The base is a rounding realization (KNOWN_ISSUES 80); the SD is around the mean of the 52, ddof = 1 (§5.2). The stability statistic, r_j against the base, is s5e's and is unchanged |
| R4 | Δ could be exactly zero | **accepted.** A zero floor is INVALID; Δ recorded per truth (§5.2, §6) |
| R5 | the closures' split was never checked | **accepted.** Pseudo seed, MC fraction and split key checked, and equal to the control's (§3.2) |
| R6 | a login-node dry run does not measure the gate's cost | **accepted.** One short single-node regular job (§11) |
| gaps | 13 tests | **added**, each with a mutant killed by it (`estimator_stability_mutation.py`) |
| — | found while fixing R1 | the local run of the job script found that a gate could read a half-written timing file, that the job's whole-second end times could precede the gate's sub-second starts, and that the full run would have re-run the dry run's tasks and overwritten their timings. All three fixed and tested (`JobScript`, `Gate`) |
| nits | nominal ≡ A7 MnvTune; 4.9% should be 4.75%; `functionals_used` not required | **accepted.** The pair is a bitwise determinism control, 17 truths judged; rates recomputed for 34 comparisons; 153 required |
<!-- absence-ok: describes defects the audit found in this declaration's own code, each now fixed and tested, not a claim that a result is absent from the repository -->

**The audit's second round** (`coverage-5b-audit`, bc0f1941, PR #720 comment 6613024951; the director's rulings):

| item | finding | disposition |
|---|---|---|
| F1 | `--pairs -:-,…` as two tokens: the real `s5p_numerics` parser exits 2, so every stability task would fail; in the code since 035ce983 | **fixed:** one token, `--pairs=…`. `RealParsers` runs every queue line through `probe.main` into the real runners' own parsers and fails on any SystemExit; a mutant restores the two-token form |
| F2 | the gate could spend the cap into an incomplete run: an unpriced tail, a 4-lane dry run, and a §7 claim of 2× | **fixed:** the projection simulates the lanes, tail included; the dry run is eight tasks on 8 lanes; rates are per kind; it stops before a launch and comes back for a reprice; the tolerance is stated as about 1.7×, with the simulation (§7) |
| F3 | a failed or time-limited dry run was accepted by the full run | **fixed:** a `DONE` receipt only after every task ended with rc 0; the full run requires it and every dry-run task's end, and checks both before writing anything |
| mutants | `main` without the guard's mode, and five job-script guards, survived | **killed:** `RealParsers` needs the guard on the production path; `JobScript` tests a failed task, a dry run with a missing end, an existing log and a missing `lightgbm`; script mutants run through the harness |
| load | `test_dry_then_full` failed once under load | the B2 ratio compared a closure with a stability task, so the start-up time skewed it; it is now like for like, and the stand-in runners sleep 0.3 s per unfold |

**The audit's third round** (`coverage-5b-audit`, 1943db31, PR #720; F1–F3 verified fixed; the director's rulings):

| item | finding | disposition |
|---|---|---|
| G1 | §7's "it does not spend down to the cap" was contradicted by §7's own table (1.85× at α = 0.8 meets Slurm's limit at 8.00), and the audit saw a mid-run stop after 6.34 node-h at 10% per-task noise | **fixed:** §7 states what the gate guarantees, a stop before any launch whose projected total exceeds the cap's remainder, and that Slurm's `--time` is the hard limit; the α = 0.8 row is stated as it reads. A 2,880-run noise sweep (`fd/stab/gatesim/`) puts mid-run spends up to 7.85 node-h at 10% noise, above the audit's single run |
| G2 | what a reprice resumes was not declared, and a fresh full run would re-launch finished tasks and record near-zero times | **fixed, as the director ruled:** no resume without an addendum the director binds; products kept and pinned (`SHA256SUMS` on every outcome), not graded until the probe completes; otherwise INCOMPLETE, reported, and no estimator adopted. The analysis enforces it: without a complete full run's receipt it reads no product (§6, §7) |
| G3 | two of the audit's 28 mutants survived: B2's ratio from the cheaper kind, and DONE without the count of ended tasks | **killed:** `Gate.test_b2_over_twice_in_one_kind_only_stops` (both kinds); the count is stated as defensive and tested by removing an end mid-run (`JobScript.test_an_end_lost_during_the_run_leaves_no_receipt`) |
| fixture | the job-script tests' stand-in runner read `--pairs` as two tokens, so every task slept as one unfold | **fixed:** it reads the `=` form, so its lane time is in proportion to the unfolds, and it writes a product per task for the pinning test |
| receipt | the audit's confirmation at 7f7f59ae noted that `--receipt` was not tied to `--runs`, so a `DONE` from another run would pass; the director ruled it a G2 defect, to be fixed before binding | **fixed:** the receipt is derived from `--runs`, and an explicit `--receipt` naming another file is refused (`EndToEnd.test_the_receipt_is_this_runs`, two mutants). §7 now says who runs the jobs: a cluster lane the director assigns |

