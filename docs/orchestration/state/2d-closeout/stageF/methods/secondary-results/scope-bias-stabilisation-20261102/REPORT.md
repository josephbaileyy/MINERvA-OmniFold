# SCOPE: the fake-data bias (A) and the estimator's rounding instability (B), scoped and priced (2026-11-02)

**Asked for by** the director, under Joseph's authority, to scope and price two items that no one is working on. They
are among the items both blind referees of 11-01 list as disqualifying.
- *Corrected by the director, 2026-11-02.* This sentence first read "rest their verdict mainly on these two items",
  which came from the work order and is wrong.
- Sonnet ranks the run-period item as "potentially the most important physically, and the coverage item … the most
  important statistically" (`referee-and-qualifications-20261101/sonnet-referee-answer.txt:146`).
- Both referees list A and B among the items that disqualify the paper together, beside unvalidated coverage and the
  run-period block.

**Provenance.** Joseph, 2026-11-02, asked whether to scope and price both:
> yes scope and price both

The sha256 of the text plus a final newline begins `14ad7ab765b1f3a4`, recomputed here. This authorizes scoping at
0 compute. It does not authorize a declaration or a campaign.

**Done by** the limitations-catalog session.
- Read-only, at origin/main `3971bbb4`.
- No jobs, no cluster contact, no paper edits.
- One blind coder subagent (claude-school) measured the caveat counts (§4), under the director's conditions.
- One read-only subagent compiled the knock-on inventory (§3), and its key citations were spot-checked.

**CITABLE FOR:**
- the designs;
- their prices, from measured per-unfold costs and the arithmetic labelled as mine;
- the knock-on lists;
- the admissibility readings;
- the measured caveat counts, at the caveat study's ±25% coder spread.

**NOT CITABLE FOR:**
- a decision, a declaration or a campaign;
- any physics claim;
- a probability. Every probability here is my judgment.

## 0. The two items, and one correction to the work order's sources

- **(A) The fake-data bias and prior dependence.**
  - Sonnet M2 asks for a validated regularization-bias term, or proof that C_model covers held-out truths.
  - Sonnet M3 asks to diagnose and reduce the bias, or include it.
  - Gemini 1 asks either to re-tune until p > 0.01 and |z| ≤ 2 at all physical benchmarks, or to build "an honest,
    calibrated model-bias systematic covariance … proving that the resulting inflated uncertainties restore closure".
  - Inventory rows: Q12, Q35, Q36.
- **(B) The rounding instability, and training and evaluating on the same events.**
  - Sonnet M5 asks for cross-fitting with a stability test, a non-zero estimator-stability block, and a
    reconciliation of the zero seed block.
  - Gemini 2 asks for ensembling, bagging, min_child_samples, depth limits, or k-fold cross-fitting.
  - Inventory rows: Q33, Q11.
- **Correction: the work order points at the wrong artifact.**
  `nd-unfolding/pet/runtime_runs/20260910/rounding-diagnostic.{py,json}` is a synthetic bound on the linear
  operations of PET's typed-descriptor encoder. Its own `kind` field is `SYNTHETIC_ROUNDING_DIAGNOSTIC_NOT_ACCEPTANCE`.
  It is not the evidence for the paper's 2.6σ.
  - The evidence is `KNOWN_ISSUES.md` row 80, with the s5e outcome (`OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md` §4, §6), the diagnosis
    (`DIAGNOSIS-20260926-s5e-oi192-estimator.md` §3), VL154–VL155, and the s5p Stage-2 record (`RECORD-20260927-s5p-stage2-exit.md` §2).
  - No design here involves PET. So the question "does PET training need GPU" does not arise, and every design is
    CPU: LightGBM GPU training is not available in the analysis environment (`state/gpu-timing-20261023/REPORT.md:36`).

**What is already measured (KNOWN_ISSUES 80):**
- Edge-safe ±½ float32-ulp input perturbations move configuration (e) by a median of 0.78 and at most 2.58
  data-bootstrap σ.
- Seeds and row order are bitwise inert.
- Every refit-per-replica bootstrap replica carries the rounding spread at the same size (ratio 1.02), so the
  statistical σ already contains it (about 37% of its variance). It is below 0.1 of any total uncertainty.
- The spread is 20× smaller on nominal pseudo-data and 7× larger at the GiBUU departure. It grows as the data move
  away from the prior.
- The mechanism is not named (`DIAGNOSIS-20260926-s5e-oi192-estimator.md` §3). The perturbation is edge-safe, so it is
  not analysis-bin crossings.

## 1. The designs

Per-unfold cost of configuration (e): **0.022828 CPU node-h** packed 8 per node (`5dc/FD-1B-STAGED-DECLARATION.md:530`).
Here `5dc/` = `docs/orchestration/state/measurement-paper/5d-community-20261024/`. All sums are my arithmetic.

### A1. An assigned fake-data bias term C_FD = Σ_T b_T b_Tᵀ, printed as a second total (U-PLAN's pre-read form)

- **Closes:** Sonnet M2 first bullet, and Gemini 1(ii), only in form. The graded truths pass "by construction"
  (`5dc/LIMITATION-PLAN.md:295`), so nothing proves the term.
- **Paper change:**
  - The IV H listing sentences must stay. J1 states both lists (`DECISION-20261031-joseph-j1-j2-and-protections-split.md`), and dropping a truth would be selective.
  - A paragraph is added defining C_FD and its second total.
  - The abstract gains the inflated median.
- **Size** (from 7.29%, before C_PL; `5dc/LIMITATION-PLAN.md:286-291`):
  - median 10.44% (A7 GiBUU only);
  - 9.08% (q3 only);
  - 12.30% (A7 GENIE+MEC, A7 NuWro, A7 GiBUU, q3), with R06 going from 5.89% to 29.29% and the trace ×4.04.
- **Caveats: +5 distinct (2 → 7), measured (§4).** The added caveats are disclosures the term cannot do without:
  not a calibrated bound; untestable by its own truths; not independent of C_model; covers only its chosen truths;
  how the truth set was chosen.
- **Compute:** 0 node-h. It is a login-node builder on committed readouts (U-PLAN :244, where the term is U-PLAN's option (b)). About one session-day,
  plus a declaration, a binding, and a values regeneration for paper and note.
- **Knock-on:** every readout against the reported matrix changes, at 0 node-h each:
  - F0/F0b and F1 grades;
  - Stage G's χ² (Table III, and the abstract's χ² range);
  - G-FOLLOWUP, G-SENS2 and FLUX-BOOT;
  - GENCMP and E;
  - X's 16-cell side. C_FD has no 2D partner, so X's cross-covariance would be incomplete;
  - J2's without-block columns;
  - the abstract's median.
  - Adding a PSD term "never raises any χ²" (`5dc/LIMITATION-PLAN.md:269`).
- **Interactions:**
  - **C_model** (0.4196 of C_total's trace, `5dc/FD-1B-DECLARATION.md:102`) is SᵀS over the GENIE+MEC, NuWro and
    GiBUU vertices. F0's vertex-family truths are those generators (`5dc/FD-F0-REPORT.md:45-48`), so C_FD double-counts
    along the shared directions.
    - The overlap is partial for GiBUU: A7 GiBUU's bias has cosine −0.485 with s_GiBUU, and 87.5% of |b| lies
      outside it (`5dc/LIMITATION-PLAN.md`, §2.2(b)).
    - F1's G18 tune shares the Valencia MEC family (`5dc/FD-F1-REPORT.md:93`).
  - **C_PL,5D** comes from data-period offsets, with rank 2 and trace share 0.0609
    (`5dc/FD-CT-5B-ADDITION-REPORT.md:52`), so it does not overlap C_FD. But J1's "without C_PL,5D the GiBUU E_avail shape is also listed"
    would pass by construction once C_FD holds that truth.
- **Admissibility:**
  - **Post hoc.** It comes after the F0, F0b and Stage G reads.
  - **What limits that.** U-PLAN's pre-read form, a truth set fixed by family rather than by failure, and both
    totals printed.
  - **Can it be built from truths it is not graded on?**
    - In-sample, it passes by construction and is untestable.
    - Leave-one-family-out is Stage 0's design, which returned STOP for C_model
      (`5d-design-20261023/STAGE0-REPORT.md:22`, `:25-30`; GiBUU c_F 0.259 against 0.60). So it is likely to fail
      at the GiBUU family.
    - The F1 tunes are the only truths outside the vertex families, and they already pass.
    - U-PLAN itself recommended against it: "C_FD built from F0's truths makes F0 uninformative"
      (`measurement-scoping/assigned-uncertainties/U-PLAN.md:239`).
  - **Can 1B or cov2d validate it?** No.
    - 1B stage 1 grades C_e(T) + C_model_abs(T) for configuration (e) at G18/AR23
      (`5dc/FD-1B-STAGED-DECLARATION.md:272-275`). The same tunes as F1.
    - cov2d tests Q_R, the 2D covariance of configuration (f) (`5dc/COV2D-SCOPING.md`).
    - Neither tests C_FD.
- **Calendar:** no exposure. It needs no compute and no inputs at risk.
- **Risk:** it reads as tuning the uncertainty to the failures. It changes every χ² and the abstract.
- **P(changes a referee's verdict), my judgment:** low. A careful referee sees "passes by construction".
- **Joseph decides:** the covariance change, the truth set, and whether it is a second total or folded in. κ is not
  touched.

### A2. A data-reweighted unfolding-prior term (the ATLAS OmniFold practice; F1-W's truth)

- **What it is.** The simulation is reweighted to the data at reconstruction level and unfolded, and the difference
  becomes a covariance term (arXiv:2405.20041; `5dc/LIMITATION-PLAN.md`, §2.2 (a′)).
- **Closes:** Sonnet M2's "validated size" in part, because it is built from the data, not from the graded truths.
  It does not answer Gemini 1, because whether it covers the GiBUU-like bias is unknown: it targets the data, not
  GiBUU.
- **Caveats: +3 distinct (2 → 5), measured (§4).** The IV H listing stays, unless the term happens to cover it.
- **Compute:** 0.36–0.6 CPU node-h, cap 0.75 (`5dc/FD-PLAN.md:493`). The build cost is unmeasured.
  <!-- absence-ok: "unmeasured" restates FD-PLAN.md:493's own status for the F1-W build, as LIMITATION-PLAN.md §2.2 (a′) does --> Then the same
  0-node-h re-evaluation of every readout against the reported matrix.
- **Knock-on and interactions:** as A1. Its overlap with C_model is unknown, because it is a direction the data
  select.
- **Admissibility:**
  - A reconstruction-level read of the data is admissible only with its recipe frozen before the data/MC ratio is
    computed (`5dc/FD-DIRECTOR-RULINGS.md` §4, F1-W).
  - It is not circular in the graded truths, so F0b can grade it honestly.
  - 1B and cov2d do not test it.
- **Calendar:** none. It would use the 5D bkg-aware loops; the 12 per-playlist copies are on CFS
  (`DECISION-20261101-joseph-eventloops-copy-to-cfs.md:22`, `:40-41`).
- **Risk:** it adds a term and keeps the failure.
- **P(changes a verdict):** low.
- **Joseph decides:** the F1-W read, and the covariance change.

### A3. Reduce the bias by changing the estimator's regularization (iterations, capacity)

- **Strong prior against it.**
  - s5n found the estimator "does not follow physically anchored truth departures (up to 74%)" and judged revision
    pointless (`OUTCOME-20260925-s5n-stage1-development-fail.md:75-76`).
  - Exact binned unfolding leaves a median residual within a factor of 2 (inventory §5.3).
  - The s5e convergence study (K up to 200) is priced at about 4–6 node-h (s5e §6, item 3).
- **It is an estimator change**, so its knock-on is B's (§3).
- **Not developed further.** It would be one candidate inside a single "final estimator" probe (B4).

### A0. Do nothing for A: keep it as stated (the decided treatment)

- The fake-data limitation for GiBUU-like truths "is stated where the GiBUU comparison is given"
  (`DECISION-20261026-joseph-5d-generator-comparison-presentation.md:24-25`).
- Comparators use fake data to validate, not as added terms (`5dc/LIMITATION-PLAN.md`, §2.2 precedents).
- **Caveats:** 0 change.
- **Cost:** 0.
- **Residual sentence:** today's IV H listing and the abstract's "residual bias exceeding predeclared … thresholds".

### B0. Reconcile and quantify, with no estimator change

- **Closes:** Sonnet M5's third bullet, "reconcile the zero seed block with the observed instability", from
  measurements already made:
  - seeds and order are bitwise inert, which is why the seed block is zero;
  - every bootstrap replica carries the rounding spread (ratio 1.02), about 37% of the statistical variance and
    below 0.1 of the total.
- It does not close Gemini 2 or M5's "stabilise / cross-fit". The predeclared stability failure stays stated, because
  dropping it would be selective.
- **Caveats: 0 change (3 → 3), measured (§4).**
- **Compute:** 0.
- **Knock-on:** none.
- **Admissible:** it reports existing measurements.
- **Calendar:** none.
- **P(changes a verdict):** low. Both referees ask for stabilization.
- **Joseph decides:** the wording only.

### B1. A jitter-ensemble estimator: every result the mean of K unfoldings with independently perturbed inputs

- **What it is not.** A seed ensemble would do nothing, because the estimator does not depend on its seed
  (`5dc/FD-GENCMP-AMENDMENT-E-ADDENDUM-E2-REPORT.md:57`).
- **K.** If members are independent, the spread falls as 1/√K. This assumption is untested, and the probe must test
  it.
  <!-- absence-ok: "untested" is this report's design assumption for a hypothetical estimator, not a claim that any result is absent from the repository -->
  - median: (0.78/0.3)² = 6.8;
  - maximum: (2.58/1.0)² = 6.7;
  - so K = 8, which also fits 8-lane packing.
- **Closes:** Gemini 2 (ensembling) and Sonnet M5's ensemble block. It does not close same-event training (Q11).
- **Caveats: −1 distinct (3 → 2), measured on the success case (§4).** If the probe fails, the IV G failure stays,
  with the new attempt added.
- **Compute (CPU), each re-run at ×8 per unfold** (§3 lists them):
  - the charged configuration-(e) re-runs, 15.5 × 8 ≈ 124 node-h;
  - set A, 50 replicas, about 9 node-h;
  - F0's 80 "f4" products, about 15 node-h, if each is one unfold (their production cost is not recorded);
  - RPD, about 13 node-h;
  - 1B stage 1, expected 24.2–36.2 × 8 ≈ 194–290 node-h (cap 73 × 8 = 584).
  - **≈ 355–451 node-h in all, below half the balance (1,025.5)**, excluding the two items below:
    - the lateral block cannot be remade: "the 5D lateral dumps no longer exist … Re-dumping would need new event
      loops" (`5dc/FD-1B-DECLARATION.md:99`). Unpriced;
    - the s5p joint tests, 208 node-h of production (`DELIVERY-20261006-s5p-campaign-terminal.md:102`), would be
      ≈ 1,663 node-h at ×8, which returns to Joseph under the half-balance rule
      (`DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md`). Or the note labels them as run on the
      previous estimator.
  - Wall-clock: one 8-member ensemble unfold is one packed node for about 12 min (533 s per lane,
    `state/gpu-timing-20261023/REPORT.md:66-67`). Every job is under 12 h.
- **Admissibility:**
  - An estimator change after Stage G's read is data-informed. It is admissible if K and the acceptance criteria are
    fixed in a declaration before any new data read, and K is chosen on simulated GiBUU-like departures, where the
    spread is 7× nominal, not on the data.
  - The paper's "No hyperparameter search was performed on data" stays true only under that rule.
  - 1B and cov2d test the current objects. 1B would have to run on the new estimator; cov2d is unaffected unless (f)
    changes.
- **Calendar:**
  - HPSS is down until 11-06 17:00 (`RECORD-20261102-director-hpss-deferral.md:6`).
  - The 5D universe merge is exposed from 11-22. It was not copied, but it can be rebuilt from the twelve CFS copies
    (`DECISION-20261101-joseph-eventloops-copy-to-cfs.md:33`).
  - The MP-1 S1 loops behind C_resp are exposed from 12-15, with no CFS copy (`5dc/FD-CT-RETENTION.md:63`).
  - The W2b loops behind 3B are exposed from 12-03 (on CFS, `:60`).
  - Running 1B's redesign once, on the final estimator, means holding 1B until B is decided.
- **Risks:**
  - the 1/√K assumption;
  - a larger regularization bias;
  - the stale laterals;
  - the note's joint tests describing a superseded estimator.
- **P(changes a verdict):** moderate on item B alone. Low on the overall verdict while coverage and the run-period
  block remain.
- **Joseph decides:**
  - the estimator change;
  - about 355–451 node-h;
  - the laterals (new loops, or kept on the old estimator, labelled);
  - s5p (regenerate, or label);
  - 1B's timing.

### B2. K-fold cross-fitting (each classifier sets the weights of the events it was not trained on)

- **Closes:** Sonnet M5's cross-fitting and Q11's same-event training. Whether it cures the rounding instability is
  **unknown**: the mechanism is not named.
- **Caveats: −2 distinct (3 → 1), measured on the success case (§4).** If it fails, Q11 is closed and the IV G
  failure stays.
- **Compute (CPU).** No record measures the per-unfold cost of 2-fold fitting; I estimate 1–2× (my judgment).
  - re-runs ≈ 45–115 node-h, including 1B stage 1 at 24–72;
  - s5p ≈ 208–416 node-h if regenerated;
  - the laterals as in B1.
- **Admissibility, calendar, knock-on:** as B1.
- **P(changes a verdict):** moderate on item B, because Sonnet named it. Low overall.

### B3. Tree regularization or input quantization (min_child_samples, max_bin, rounding inputs to analysis precision)

- **Closes:** Gemini 2's "leaf-sample constraints". Its effect is unknown.
- **The risk.** Quantization could remove only the ulp-level test artefact. Because the spread grows at departures,
  the instability may be genuine. Stronger regularization could also raise the bias (A).
- **Compute:** about 1× per unfold. Re-runs ≈ 45–60 node-h, plus the laterals and s5p as above.
- **P(changes a verdict):** low to moderate.

### B4. The declared probe that must precede B1, B2 or B3 (Sonnet M6: one final estimator)

- **What it does.** Each candidate is measured on simulated GiBUU-like pseudo-data, not data:
  - 51 rounding-probe unfolds (s5e's n = 1 + 1/(2·0.1²));
  - 18 noise-free closures at the F0b truths, so that the bias does not get worse.
- **Cost:** about 12.6 node-h for B1 (×8) and about 1.6–3.2 each for B2 and B3. **About 16–18 node-h for all three.**
- **Criteria fixed in the declaration:**
  - the stability bar of 0.3 (median) and 1.0 (maximum);
  - the bias no worse at any truth.
- **The winner becomes the single final estimator.** Everything is re-run once (§3) and 1B runs on it.

## 2. Ranked recommendation

1. **B0 now, with A0.** 0 node-h; caveats ±0.
   - It answers the one referee request that measurements already settle (reconcile the seed block).
   - It keeps the decided fake-data treatment.
   - **Residual sentences:**
     - IV G keeps the predeclared stability failure, plus the reconciliation;
     - IV H keeps the listing (GiBUU hybrid and q3 tilt, and R06 without C_PL,5D);
     - Q11's same-event training stays.
2. **If Joseph wants item B answered on substance: B4, then the winner as the single final estimator.**
   - The probe is about 16–18 node-h.
   - The re-run is about 45–451 node-h, depending on the winner. It excludes the laterals (unpriced) and s5p
     (208–1,663).
   - 1B's redesign is held so that it runs once on the final estimator.
   - **Residual sentence on success:** −1 or −2 caveats. Q11 is closed only by B2.
   - The note's joint tests either carry a "previous estimator" label or are regenerated.
3. **A2 as a sensitivity printed beside the total**, if Joseph wants a data-driven prior statement. It costs under
   1 node-h. It is expected to add caveats (+3) and leave the failure.
4. **A1: not recommended.** It adds caveats (+5), passes its own truths by construction, double-counts C_model along
   the shared vertex directions, and nothing running can test it. If a bias-inclusive number is wanted anyway, print
   it as a second total in U-PLAN's form, never folded in.
5. **"Do neither" is defensible**, and it is option 1 without B0's rewording.
   - Both items are disclosed with measured sizes.
   - A1 and A2 cannot remove the fake-data sentence honestly.
   - Neither A nor B moves the referees' combined verdict while unvalidated coverage and the run-period block remain.
     Both referees list those as co-disqualifying.

## 3. Knock-on inventory (B changes configuration (e); A changes the reported matrix)

Measured costs come from each campaign's own report, as compiled by the read-only subagent and spot-checked. (B)
re-run costs are ×K for an ensemble.

| campaign | object | status | measured cost | under B | under A |
|---|---|---|---|---|---|
| S1, the C_e blocks | 256 (e) unfolds | complete | 6.04 (`5dc/S1-REPORT.md:137`) | re-run ×K; **laterals cannot be remade** | input unchanged |
| C_model,5D | (e) under 3 vertices | complete | 0.23 (`measurement-scoping/pv-ladder/REPORT.md:354`) | re-run | overlaps C_FD |
| C_resp | 11 (e) species-shifted unfolds | complete | 0.59 (`phase1/mp1/S1-REPORT.md:148-152`) | re-run; inputs exposed 12-15 | unchanged |
| 5B → C_PL,5D | 33 (e) period unfolds | complete | 0.90 (`5dc/FD-CT-5B-REPORT.md:59`) | re-run | no overlap |
| 3B, detector-mismatch closures | 13 (e) | complete | 0.44 (`5dc/FD-CT-3B-REPORT.md:36`) | re-run; W2b exposed 12-03 | beside the result, unchanged |
| F0 and F0b, the fake-data tables | 80 (e) products, regraded | complete | 0 (production not recorded) | new products | grades change; circular if C_FD uses them |
| F1, GENIE v3 | (e) at G18 and AR23 | complete | 1.33; unfolds 0.61 (`5dc/FD-F1-REPORT.md:138,143`) | re-run | grade changes; circular if used |
| Stage G and its sensitivities, GENCMP, E, EA2 | χ² and figures | complete | 0–0.16 | re-run at 0 after a new f | every χ² falls or holds |
| E2, CH vertices | 5 (e) | complete | 0.22 | re-run | changes |
| X, quadrants against 2D | reported matrix plus 100 new (e) replicas | complete | 3.55; BOOT 2.92 (`5dc/FD-GENCMP-X-REPORT.md:251,253`) | re-run | 16-cell side changes; no 2D pair |
| 1B staged, stage 0 | κ of S1, (e) | complete, PASS | 3.12 | re-run | grades C_e + C_model only |
| 1B staged, stage 1 | coverage of (e) at G18/AR23, against C_e(T) + C_model_abs(T) | stopped at N1; redesign approved | 0; cap 73, expected 24.2–36.2 | run on the new estimator, ×K | does not test C_FD |
| RPD | 492 (e) per-playlist unfolds | design bound; part 2 not run | expected 1.65, cap 3.0; deadline 12-15 | run on the new estimator | C_PL,12 printed beside the result |
| s5p, the note's joint tests | (e) calibration ensembles | terminal | production 207.9 | regenerate (new authorization) or label | none |
| cov2d | held-out-tune coverage of Q_R, (f) | scoped only; deadline 12-19 (`5dc/COV2D-SCOPING.md:252`) | price 80–153 | unaffected unless (f) changes | none |
| RE-2, the 2D E_R and Q_R | (f) | complete, adopted | 53.18 | only if (f) changes | none |

**Allocation:** 17,949.1 of 20,000.0 charged, so 2,050.9 remain and half is 1,025.5
(`5dc/FD-1B-STAGED-STAGE1-STOP-REPORT.md:74`). GPU: none of these used GPU.

## 4. The caveat counts, measured blind

**The method:**
- Seven excerpts went to one coder (claude-school subagent): the current IV H and IV G sentences ("before"), and each
  design's proposed text ("after").
- They were shuffled with seed 20261102 and named set-1 … set-7, with no design labels, no hypothesis, and no mark
  of which set is a proposal.
- The coder had the caveat study's `CODEBOOK.md` and nothing else.

`coder/` holds the prompt, the answer, the seven sets, the seven TSVs, the unblinding map, and `SHA256SUMS`.

| text | set | statements | distinct caveats | change in distinct caveats |
|---|---|---|---|---|
| before, A (abstract sentence and IV H) | 6 | 5 | 2 | — |
| A1, assigned term | 4 | 11 | 7 | **+5** |
| A2, prior term | 1 | 8 | 5 | **+3** |
| before, B (Sec. III training, the seed block, IV G) | 5 | 5 | 3 | — |
| B0, reconcile | 7 | 6 | 3 | 0 |
| B1, ensemble (success case) | 3 | 2 | 2 | −1 |
| B2, cross-fitting (success case) | 2 | 1 | 1 | −2 |

**Reading.**
- Joseph's suspicion holds on this measurement: a bias term adds caveats.
- The coder's study has a ±25% spread, so differences of ±1 (B0 to B2) are not results. The +5 and +3 are.
- **Limits:**
  - one coder;
  - my drafted texts;
  - B1 and B2 drafted as successes. Their texts omit the development variant's 2.5σ, which under an estimator change
    would move to the note;
  - the coder reused issue labels across the near-duplicate sets, as it reported, so the sets were not coded blind
    to one another.

## 5. The independent consult (Gemini), and where it differs from this ranking

**What ran.** Run by the director, with agy, gemini-3.8-flash-high and `--sandbox`. Both files are here verbatim and
listed in `SHA256SUMS`:
- `CONSULT-GEMINI-PROMPT.txt` (sha256 `993878f0…`);
- `CONSULT-GEMINI-ANSWER.txt` (`232c516d…`).

**What the consult saw.** The prompt is the director's task text, then both referee reports, then this report as of
`ed8156c1`. The referees are anonymised: Referee 1 is Sonnet and Referee 2 is Gemini.
- The prompt file itself has no provenance line and no record of the substitution; it contains neither model name.
- I checked the substitution by reversing it (Referee 1 → Sonnet, Referee 2 → Gemini) and diffing each section against
  `referee-and-qualifications-20261101/{sonnet,gemini}-referee-answer.txt` and against this REPORT at `ed8156c1`.
- They are identical up to whitespace.

**This report's ranking is unchanged.** The consult differs on four points.

1. **A0 and "do neither".**
   - The consult calls A0 "unacceptable for a PRD measurement paper", and "do neither" "completely indefensible".
   - It accepts both only under a methods-paper reframing (Referee 1's Route B, Referee 2's fallback).
   - This report's §2 item 5 called "do neither" defensible in the sense that neither A nor B alone moves the combined
     verdict. The consult's reading is the stricter one, and Joseph should see both.
2. **B0.** The consult calls B0 insufficient: the referees would still require stabilization. This report agreed
   (§1, B0: "P(changes a verdict): low"). It differs on whether B0 is worth doing first anyway.
3. **Which candidates to probe.**
   - The consult would test B2 (cross-fitting) and B3 (tree regularization; it would avoid "naive input
     quantization"), and drop B1 as "a compute-heavy … brute-force band-aid".
   - **B4 without B1 costs about 3.2–6.4 node-h** (my arithmetic from §1: about 1.6–3.2 each for B2 and B3), against
     about 16–18 with B1.
   - The consult agrees with the sequence: probe on simulated pseudo-data, one final estimator, everything re-run
     once, and the coverage campaign held.
4. **Its "missed option": merging the low-stability cells (R02, R06, R10, R15).** Its first action is to merge them
   "to ensure stability ≥ 0.40" and re-test, "because R02 and R06 drive the GiBUU hybrid failure".
   - **Already ruled.**
     - "Cell merges or new cuts after the data read stay inadmissible"
       (`DECISION-20261027-joseph-measurement-framing-and-limitation-scoping.md:45-46`).
     - The merge outcome left F0's plan: "Joseph may still change R00–R15, since the definition is his. Any such
       change is labelled post hoc wherever it is reported"
       (`5dc/FD-DIRECTOR-RULINGS.md:30-33`).
     - So a merge is Joseph's alone to make, and would be labelled post hoc.
   - **Its factual premise is partly right, and the inference does not follow.** These are the A7 GiBUU per-cell z
     from the committed F0b readouts, against C_total without the GiBUU vertex, plus C_resp, plus (second row)
     C_PL,5D:

     | matrix | R00 | R01 | R02 | R03 | R04 | R05 | R06 | R07 | R08 | R09 | R10 | R11 | R12 | R13 | R14 | R15 | χ²/16 | p |
     |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
     | + C_resp (`fd/readout/fd_f0b_readout.json`) | −0.40 | +0.11 | **+4.23** | −1.04 | −0.31 | +0.09 | **+5.17** | **−2.02** | −0.87 | −0.20 | +1.57 | −0.41 | −0.17 | −0.67 | −0.14 | +1.60 | 175.13 | 8.0e-29 |
     | reported, + C_PL,5D (`fd/with-cpl/readout/fd_f0b_readout.json`) | −0.40 | +0.11 | **+4.19** | −1.02 | −0.27 | +0.08 | **+4.53** | −1.89 | −0.87 | −0.18 | +1.55 | −0.40 | −0.16 | −0.64 | −0.13 | +1.50 | 171.01 | 5.3e-28 |

     - Under the reported covariance, R02 and R06 are the only cells with |z| > 2. They are two of the four
       low-stability cells, so that much of the claim holds.
     - They do not carry the failure alone. Their z² sum to 38.1, and all sixteen to 49.0, against a full-covariance
       χ² of 171.0 (my arithmetic). Most of the χ² comes from the correlated structure across cells, not from the two
       cells' diagonal residuals.
     - F0b's eight-cell variant (R00–R03, R08–R11) leaves out R06 and R07 and still gives 133.91 for 8 degrees of
       freedom, p 4.38e-25 (`5dc/FD-F0b-REPORT.md`, §6).
     - So merging R02 and R06 into neighbours would not be expected to remove the GiBUU-hybrid failure. Whether it
       would is untested, and testing it is the post hoc change the rulings reserve to Joseph.
     <!-- absence-ok: "untested" refers to the hypothetical merged grid the consult proposes; no claim that a result is absent from the repository -->

**Also flagged by the consult:**
- §0's "rest their verdict mainly" sentence, now corrected above.
- §1's "A1 closes Gemini 1(ii) only in form". The consult says an outer product of the failing residuals does not meet
  Referee 2's request "even in form". This report's conclusion, that A1 is not recommended, is the same.

