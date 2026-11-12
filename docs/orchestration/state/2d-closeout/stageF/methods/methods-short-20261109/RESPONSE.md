# Response to the GPT referee recheck of #977 at 2bfb1410c (gpt-6.1-sol, 5/10)

**Report:** `secondary-results/referee-methods-recheck-20261111/gpt.txt` (PR #1074). Section numbers below are the
report's.

**Classes:**
- **T** — text only, from existing records.
- **L** — a lookup or recomputation from committed products, on a login node or locally.
- **A** — a new analysis, priced in node-h.
- **X** — outside this lane.

**M** in the misreading column marks a request that rests on a misreading; that column gives the fact.

**Rules for the work.** Every new number or claim in a T row cites its record. Protected spans stay verbatim: the B0
sentences, RS1's paragraph, #981's quotes and the LISTED_CLAIMS anchors. A ONCE sentence or an anchor that a move
touches is listed in its row.

**The director's rulings** (2026-11-11): T rows start at once. L and A rows wait for a ruling. Text fixes are approved
under the director's authority.

**Code paths** below are at abdc88c5. Note paths are at #952 4219869a2, whose labels equal acf934d71's.

## Major issues

| # | Request | Class | Source / inputs / cost | Proposed resolution | Misreading? |
|---|---|---|---|---|---|
| 1.1 | One complete cross-section equation; reconcile "completeness" with "no separate efficiency correction" | T | note sec_method.tex:178-186 (equation; c ≡ 1 bin by bin because unmatched truth events are appended; a monitored self-check); sec_experiment.tex:36 (c = 1.000000); code s5c_unfold.py:135-144, xsec_nd.py:54-83 | Put the equation in §3.1 with every factor defined, and say c ≡ 1 by construction. S4 step 3 points to it. | partly: the two statements are consistent, and the text does not say why |
| 1.2 | The unmatched-event procedure and its weighting assumption (15.7–68.1 % of a cell's final weight) | T, with an optional A | omnifold_nn_core.py:258-260 (`reg.fit(MCgen[pass_reco], new_w[pass_reco])`, with no sample_weight); ESS keys ess-nrp-min/max (READOUTS ess d4f1268d) | State in §3.1 and S4 that the regressor is fitted with equal event weights: a conditional-mean estimate of u at fixed truth under the event count, not the physical weight. Name the untested consequence as a limitation. Optional A: refit (e) on data with a weighted regressor, about 0.15 node-h (pv-ladder/BINDING.md:15: three 5D data unfolds ≈ 0.45 node-h), plus a regrade; does not wait for LL5D. | no |
| 1.3 | The systematic treatment of unreconstructed events | T | note sec_systematics.tex sec:uq-2d-scope (the 2D universes' miss-weight approximation), already limitation 7; the 5D universes reweight the appended truth events like any other (Supp S5 :347 and note sec:fived16-cov) | One sentence each for 2D and 5D in §3.2, with limitation 7 pointing to it. | no |
| 1.4 | Numerical response-scale uncertainties (C_resp) | T, or L if no record states the factors | Supp :347 names four categories, each "scaled by its own one-standard-deviation factor"; no number is printed. Source to pin: the C_resp producer's configuration or the note's App. D | Print the four factors, with the record's path:line. If no committed record states them, read them from the producer's configuration (L, minutes). | no |
| 1.5 | The numerical ingredients to reproduce the covariance construction | T, with an optional L | Supp Tables S3–S5 (per-group σ, correlations), the machine-readable files (:162), the replica and universe counts already keyed (cov16 and s1-* keys) | A compact "construction" table in S5: each block, its ensemble, size, weights, centring and normalization, all from keys already printed. Optional L: per-block CSVs from the S1 tables (retrieved from HPSS on 2026-11-11, retention logs). | no |
| 1.6 | Enough to reproduce several test configurations | T | S9's test tables and S4's step list | Name each test's estimator configuration, truth, split, repetitions and threshold in one S9 ledger (see structure 10). | no |
| 1.7 | Keep code references as aids, not definitions | T | S4 :236-245 | S4 states each step in words first; the line ranges stay in one closing sentence per step. | no |
| 2.1 | State the coverage tests' qualifications together and prominently | T | Supp S9.4 :697-725 (discrete or Gaussian laws, C_T fixed per tune, the lateral surrogate, draw-matched contents, what is drawn and what is omitted); FD-F1-DECLARATION.md:157-178 (gated, normalized tunes) | One list in §6.2's opening paragraph, which now carries the scope sentence. | no |
| 2.2 | A compact, auditable form: ensemble, fixed covariance, reference contents, thresholds, counts, controls | T | the keys printed in §6.2 and S9.4 (cov2d-*, null-*; score_AR23.json fe5263e9, score_G18.json 84976694) | A small table in §6.2: one column per tune (and per variant for the second test, as variants), with reference content, threshold, count and control result. | no |
| 2.3 | The pending test: three outcomes (valid without under-coverage, valid with it, invalid) consistent in the abstract, the table and the conclusions | T | variants.md V-L1 to V-L3; the abstract's ll5d-abs-*; Table 2's ll5d group; §6.2's ll5d group | Check each variant and add the missing conclusions case. Every invalid case reads "no coverage conclusion". | partly: the variants already distinguish them; the conclusions need the same three |
| 2.4 | A repair or continuation after a check is distinguishable from the specified test | T | the ll5d-route variants (descriptive status) | Already implemented. Add the same route clause to §7. | partly |
| 2.5 | Keep the one-way PSD qualification, with its rank conditions | T | §6.2 second-test grading paragraph; S9.4 :725 | Kept. State the rank condition in both places in the same words. | no |
| 2.6 | A pass does not validate the full data uncertainty budget | T | the ll5d-anypass variant; the §6.2 scope sentence | Add "it does not validate the uncertainty of the data result" to the pass case in the abstract, §6.2 and §7. | no |
| 2.7 | Conditional covariance-adequacy tests, not general frequentist coverage | T | as 2.1 | One sentence in §6.2's opening: "conditional tests of the procedure's covariance at the specified laws and truths". | no |
| 3.1 | C_model: a common supported phase space for the GiBUU shift (p∥ and E_ν truncation) | A | Design: rebuild the GiBUU ratio on the phase space all three generators support (p∥ below cmodel-gibuu-pz-lack, with E_ν ≤ cmodel-gibuu-enu in every sample), re-unfold the data with configuration (e) under that prior, rebuild C_model, and regrade the fake-data, held-out-tune and generator readings. Cost about 0.15 node-h for the unfold (pv-ladder/BINDING.md:15) plus login-node regrading; wall time under 1 h; does not wait for LL5D. | Report as a sensitivity row in S5 and in Table 3's caption. | no |
| 3.2 | C_model: a less discontinuous ratio construction | A | Design: the same three shifts with the ratio gate (pvl_lib.py:103-141, stat_max) replaced by a smoothed ratio, for example pooling at the coarse cell for every fine cell, so that the cmodel-step fraction falls. Re-unfold (e) three times; about 0.45 node-h (pv-ladder/BINDING.md:15); rebuild and regrade as 3.1; does not wait for LL5D. | As 3.1. | no |
| 3.3 | Which grades depend on the GiBUU component (leave-one-out) | L | stored per-generator shifts S (nd-unfolding/pv-ladder/readouts/cmodel_5d.json, keys S and trace_share_by_vertex), the F0b bias records and block matrices (T2B's inputs, t2b.json 0e281a61); locally, minutes | Regrade with C_model built from GENIE + MEC and NuWro only; descriptive, as T2B. | no |
| 3.4 | Call C_model an implementation-specific shape sensitivity, not a calibrated uncertainty | T | §3.2 already: "measures … and is not calibrated as a bound"; S5 :332 | Use the referee's term once in §3.2 and S5, and list the construction effects (carbon, E_ν cut, p∥ cut, gated steps) in one sentence. | no |
| 3.5 | State which conclusions survive these choices | T after 3.1–3.3 | 3.1–3.3's outputs | One paragraph in §5.2 or S5. Until those rows run, the text says which grades change with C_model doubled or removed (Table S15) and without it (T2B). | no |
| 4.1 | A bookkeeping table: selection, exposure, normalization, backgrounds, response inputs, each marked verified against the publication or unavailable | T | Supp S1 (selection, POT 1.057e21, nucleons 3.2353e30); note sec_experiment.tex:8 (same exposure as the publication); :26 (genuine background 0.35 % on 1A, against the publication's 0.2 %); stageD-inputs/q2-opendata-20261014/REPORT.md :22-28 and triage/REPORT.md :3-8 (1A only); the publication's flux and response not available here | One table in S1, with "verified", "compared, differs by definition" or "not available" per row. | no |
| 4.2 | Full-sample genuine-background and out-of-phase-space fractions | L | the per-playlist background and out-of-phase-space templates of the 2D production; login node, minutes. Inputs to confirm: whether they are committed or only on pscratch. | Add both fractions to S1 and the table of 4.1. | no |
| 4.3 | Their distribution where the 2D shape difference is largest | L | as 4.2, on the 205 cells with fig:tension2d's largest contributors | One figure or sentence in S6. | no |
| 4.4 | The 1A check does not establish equivalence to the published inputs | T | Supp S1 :28 already says so ("it does not compare unfolded results or these inputs with those of the published analysis") | Bring the clause into the paper's §2 sentence. | M: the Supplement already states it; the paper's "was checked" sentence is too short |
| 4.5 | κ: explain the data value below its replica range, or drop the classification | T (drop) | OUTCOME-20261106-ref-c2c1-read.md:32-37 (no mechanism offered); the readout keeps only the range's end points (read-2/readout.json) | Drop κ and its "unresolved" class from the paper (§4.1 and Table 2). S8 keeps the definition and one sentence that the data value lies below the replica range and the class reading is not used. Reason: an explanation needs the per-replica distances, which the record does not keep (an A); the paired T comparison stands without κ. | no |
| 5.1 | Call χ² tail areas reference scores, not calibrated probabilities | T | §3.3's flag definition; Table 3's caption | Say "reference p, a score against χ²₁₆" at the definition, once; captions follow. | no |
| 5.2 | "Agree" → "No difference detected" | T | Table 2 status words :175 | Rename the status in Table 2, its glossary, S9's tables and §4.1, §4.3. | no |
| 5.3 | The sixteen-cell IBU null's flux surrogate (100 Gaussian vectors against n_eff ≈ 19) | T | REF-G1-DECLARATION.md:142-143 (each draw forms Ĉ*_flux "by S1's Flux estimator: the same 100 constraint weights", so the weighted estimator and its effective size are reproduced); :271 (χ²₁₆'s 0.997 quantile 35.89), :160 (Hartlap 46.09); T = 194.4 against 39.04 (ibu16-*) | State the weighted construction in S8, and that T exceeds every alternative threshold on record (χ²₁₆ 35.89, Hartlap 46.09) by a factor of more than 4, so the "differ" reading does not depend on the surrogate. | M: the null applies the constraint weights, so its effective size is the reported ensemble's |
| 5.4 | Keep the 2D coverage failure; eigenmodes do not identify its cause | T | §6.2 (the batch's "leaves its cause open"); T2A licence | Already; check §7's checklist sentence, which says the χ² is "dominated by mean bias in the poorly determined directions". | no |
| 6.1 | "Moves past the truth" is a projected statement | T | §5.3 :322, Table 4 caption :329, §7 :436, the abstract :59 prr-abs, S9.3 :704 | Write "overshoots the truth along the prior-to-truth direction" at each site; the abstract keeps its length. | no |
| 6.2 | The discretization: exact binned IBU is exact for the discretized problem | T | §5.1 :245, S8 :500-503; d-id/REPORT.md :432-452 | One sentence before any implementation-share attribution: the binned comparison uses the truth grid; OmniFold uses event-level features. | no |
| 6.3 | Keep RMS and covariance-weighted bias beside ρ | T | Table 4 (prr-rms-*, prr-chi2-*) | Kept, and named in the §5.3 text. | no |
| 6.4 | Simplify the "consistent with" taxonomy | T | §5.3 :304-311 (the declared labels, FD-PRR-DECLARATION.md:323-329) | One sentence naming the labels that hold at both truths, in place of two per-truth lists; the list of definitions moves to S9.3. | no |
| 6.5 | The results support sensitivity to implementation and settings, not a unique cause | T | FD-PRR CITABLE FOR :30-38, NOT CITABLE FOR :40-56 | One closing sentence in §5.3. | no |
<!-- absence-ok: row 1.2's "untested consequence" scopes what this lane's records test about the regressor's weighting (omnifold_nn_core.py:258-260 at abdc88c5, fitted without sample_weight); it is not a claim that a result does not exist -->

## The report's §4 rows marked (a) or (c)

| Row | Class | Source | Proposed resolution | Misreading? |
|---|---|---|---|---|
| (a) GEANT neutron/proton control discrepancies and block non-additivity | T, with an optional A | OUTCOME-20261108-1b-precheck-part1.md:41-42 (both bands DEPART), :70 (NOT CITABLE FOR the cause); LL5D-DECLARATION.md:90-94 (the primary reading never draws them; DECISION-20261108-joseph-5d-coverage-and-parallel-studies.md item 1) | Restrict the claim, as the referee allows: the primary reading is the validated subset and excludes the two bands; the second reading's grades with them are reported beside it, with their departure unexplained; the non-additivity concerns the stopped first test only. Optional A: diagnose defect against non-linearity, unpriced. | no |
| (a) C_model dominated by a truncated, gated GiBUU shift | as 3.1–3.3 | — | — | no |
| (a) The reproduction package is not deposited | X | app_release.tex (RC7, about 16 MB, not deposited) | Depositing is Joseph's decision. The paper keeps its Data availability text, which is protected. | no |
| (c) The stopped first five-observable test's history | T | §6.2's "Earlier five-observable tests"; S9.5 | One sentence stays in the paper. S9.5 keeps the findings that constrain the second test (the like-for-like control, the GEANT bands); the chronology leaves S9.5. The note lane gets the chronology if the note lacks it. | no |
| (c) The free-proton validation failure history | T | S10.1 :764 (NuWro's reason in its record's terms; GiBUU's) | Already one sentence in S10.1; no history in the paper. | M: the Supplement is already concise |
| (c) Superseded configurations, old band tests, selection chronology | T | S4's history table (tab:estimators-matrix), S9.1 (the superseded band test; the note carries it as sec:coverage) | Remove S9.1 to the note's sec:coverage (pointer only) and S4's history table to one sentence with a note pointer. Check #981's quotes first: none sits in S9.1 or the history table. | no |

## Minor issues

| # | Request | Class | Source | Proposed resolution | Misreading? |
|---|---|---|---|---|---|
| m1 | Narrower status labels; "valid" names its rule | T | Table 2 :161 ("of 16 cells valid"); S9 test 6 | "pass the bias-half rule"; "No difference detected" (5.2). | no |
| m2 | Not every deformation is generator-sized; the q3 tilt is a stress amplitude | T | OUTCOME-20260925-s5n-stage1-development-fail.md:41-45 (a declared stress amplitude); S9 test 2's truths list the tilt | Separate the tilt in Table 2's row names, §5.1 and S9 test 2. | no |
| m3 | Present the released-cell instability prominently; distinguish 0.133 % from 2.6σ | T | §6.1 B0 span (protected), keys rnd16-*, s5e-round-* | Abstract: "a median of 0.133 % on the sixteen released cells; up to 2.6 statistical standard deviations over 153 finer quantities", within 250 words. §6.1 leads with the released cells (structure 7). | no |
| m4 | Algorithm differences in physical units in the paper | T | ibu16-dof-R11, -R06, -R05 (REF-G1 readout 4db170d3) | One sentence in §5.4 with the three largest fractional differences. | no |
| m5 | Figure 3 with the injected changes | L | figures/methods_short/m3_fig2_deformation_arrays.json holds injected_change_pct for the lower-capacity panel only; the three shapes' injected changes come from their truth ratios (the producer's inputs); locally, minutes | Add the injected change to each panel through the figure lane's producer, with arrays asserted as now. | no |
| m6 | Normalization terminology: cell-integrated, differential, covariances | T | Supp S3 :162 (the CSV descriptions), S5 :332 (fractional and absolute C_model) | One definitions sentence in §2 and S3; consistent nouns. | no |
| m7 | Define the shape-only χ²; why 100ff^T suffices | T, with a seconds-long L for one number | Supp :402; Sherman–Morrison: χ²(C + λff^T) = χ² − (fᵀC⁻¹Δ)²/(λ⁻¹ + fᵀC⁻¹f), which approaches the profiled shape χ² as λ → ∞; the remainder is set by 1/(λ fᵀC⁻¹f), computed from xsec16_cross_section.csv and the covariance CSV | State the identity and the size of the remainder at λ = 100. | no |
| m8 | Reduce procedural language | T | the "fixed in advance" family across the paper | One study-design sentence in §3.3, then cut repeats elsewhere. ONCE sentences stay. | no |
| m9 | Redundant W: finite-capacity learning against information | T | S2 :76 | Rephrase the last sentence of S2 :76 to separate the two questions. | no |
| m10 | Figure S2 missing | T, and a fix to the rater-copy script | Figure S2 is in the PDF. Its float lands after the references, and make_supp_rater_copy.sh's blinding cuts at "References", so the blinded copy dropped its caption. The script counts table captions only. | Put \clearpage before the Supplement's references, so the float prints before them. Add a figure-caption count to make_supp_rater_copy.sh, like the table one, so a dropped figure fails the copy. | M: the figure is there; the blinded copy lost it |
| m11a | "sections 6.2 and 6.2" in limitation 5 | T | paper limitation 5, (sec:calib and sec:ll5d both print 6.2 since T1-2) | "(section 6.2)". | no (confirmed) |
| m11b | Configuration-(a) qualifications inside the reported estimator's discussion | T | S4's hyperparameter paragraph :267 ("Configurations (a) and (f) do not set the histogram construction …") | Move that clause to the history table's row (a). | no |
| m11c | "diagonal fraction" against "reconstruction stability" | T | S10 :788 ("four cells have low reconstruction stability") | "low diagonal fraction", as §2 and limitation 6. | no |

## Structure

| # | Request | Class | Proposed resolution | Dependencies |
|---|---|---|---|---|
| s1 | Open §3 with the two reported estimators and their products | T | Move §3.1's estimators paragraphs to its start. | none |
| s2 | Split §4.1: selection history to §3/S4; paired algorithm comparisons in their own subsection | T | §4.1 keeps the integral, projections and distance; a new §4.2 "Paired comparisons with other unfoldings" takes the IBU and C1 paragraph; the learner-choice history moves to §3.1's choices sentence and S4. | κ leaves (4.5) |
| s3 | §4.2 leads with the step; the per-period eigenmode-distance readings move to the benchmark or S6 | T | Move the two pp-* readings to S6 (with a pointer from §4.1). | Q23 (#981) is in S6 already and unchanged |
| s4 | §5.1: the lower-capacity background sentence to S4; the exact-binned discussion beside §5.3's IBU study, with a grid warning | T | As requested. | none |
| s5 | §5.3: lead with the retained fractions and Table 4; taxonomy and thresholds to S9.3; merge the per-truth label sentences; Figure 5 and "Two other findings" as the motivation | T | Reorder; one label sentence for both truths (6.4). | variant sites per paragraph (check 1) |
| s6 | Split §5.4 | T | §5.4 algorithm dependence; §5.5 per-cell rules, one paragraph (sec:ibu and sec:vhalf are already separate labels). | none |
| s7 | §6.1: lead with the released cells; move the ensemble's floor accounting to S9; drop the future-study sentence | T, with a ruling on W-4 | Reorder around the protected B0 span (kept contiguous). The future-study sentence is W-4, Joseph's provisional decision (DECISION-20261109-joseph-bv-mention-title-preread.md item 1). Cutting it needs your ruling. | B0 span; ONCE "We report the ensemble average as a tested mitigation of the instability." stays |
| s8 | §6.2: the earlier estimator's 6 % coverage and the stopped-test chronology to the note | T | Cut the r5:223 sentence to a pointer. | check_sec4_receipts.py anchors that sentence (test_check_sec4_receipts.py), so the test needs updating with it; #977's check 6 |
| s9 | §7: compact checks; merge repeats; shorten the hadronic-structure search | T | Shorten. | ONCE "That test is a next step." (check_round ONCE): keep or update ONCE with your approval |
| s10 | Paper–Supplement–note balance; S4 long; S9's four tables duplicate Table 2 | T | The paper gains the normalization equation (1.1), the largest algorithm differences (m4) and the coverage qualifications (2.1). S4 loses the history (c row). S9's four tables become one test ledger, which also takes Table 2's full detail (s11h). | Table 2's variant cells (ll5d, prr, vhalf) move with it; check 1 |
| s11a | Figure 1 stays | — | none | — |
| s11b | Figure 2 to the Supplement | T | Move to S6 (the tension map). | — |
| s11c | Figure 3: injected changes; show the reported estimator's GiBUU case | L | m5. The reported estimator's GiBUU-to-GENIE residuals per (E_avail, W) cell: inputs to check in assess_receipt.json points.eavail_gibuu (OUTCOME-20260926-s5e-oi192, :68, :85). Plotting only if present; an A (20 pseudo-experiments) if absent. | — |
| s11d | Figure 4 stays | — | none | — |
| s11e | Figure 5 to the Supplement | T | Move to S9.3 with its paragraph's motivation sentence kept in §5.3. | — |
| s11f | Figure 6 with a nearby sixteen-cell summary | T | One sentence by the figure with rnd16-* (already in the B0 span). | B0 span |
| s11g | Table 1 after the cell construction | T | Move the float after the construction paragraph. | — |
| s11h | Table 2 to principal findings; full ledger to the Supplement | T | Table 2 keeps one row per finding (about 10); S9's ledger keeps every row. | variant cells, as s10 |
| s11i | Table 3 compact | T | Keep the primary columns; the two sensitivity readings become one column of flagged truths. | make_figures.check_against reads Table 3's truth order and keys (check 9) |
| s11j | Table 4 stays | — | none | — |
| s11k | S10's generator comparisons optional; fewer χ² sensitivity tables | T (decline in part) | Keep Table S14 and Fig. S2. Merge Table S15 into S14's caption. Reason: #981's quotes Q05, Q06, Q07, Q14–Q18 sit in S10; Q06 is tab:cmodel16's label, so S15 stays as a label-bearing table unless #981 is re-pinned (limitation-resolver). | #981 |

## Count by class

Rows: 33 major sub-requests, 6 limitation rows, 13 minor and 21 structure (73). Each row is counted once, under its
main class.

| Class | Count | Rows |
|---|---|---|
| T | 61 | every row not listed below, including 1.4, which becomes L only if no committed record states the four factors |
| L | 5 | 3.3, 4.2, 4.3, m5, s11c |
| A | 2 | 3.1, 3.2 (about 0.15 + 0.45 node-h, under 1 h wall, not waiting for LL5D) |
| X | 1 | the reproduction package |
| no action | 4 | s11a, s11d, s11j, and the C_model (a) row, which points to 3.1–3.3 |

Optional extras inside T rows:
- **A:** 1.2's weighted-regressor refit (about 0.15 node-h) and the GEANT row's cause diagnosis (unpriced).
- **L:** 1.5's per-block CSVs and m7's one number (seconds).

Misreadings or partial misreadings: 1.1 (partly), 2.3 and 2.4 (partly), 4.4, 5.3, m10, and the free-proton (c) row.

Needing your ruling inside the T batch:
- s7, cutting the W-4 bias-variance sentence (Joseph's provisional decision);
- s9, the ONCE sentence "That test is a next step.";
- s8, check_sec4_receipts.py's anchor sentence;
- s11k, #981's S10 quotes.

## The director's rulings (2026-11-11)

- **L:** 3.3, 4.2, 4.3, m5 and s11c are approved, and so are 1.5's per-block CSVs and m7's one number. Each is run
  locally or on a login node, with its product's sha recorded here.
- **A:** 3.1, 3.2 and 1.2's weighted refit are approved in principle, about 0.75 node-h. Their declaration (three arms)
  goes to tier3-design, then coverage-5b-audit, then the director's binding, then the cluster after the maintenance.
  Their paper text waits for their results; meanwhile 3.x's text reads correctly under either outcome.
- **The GEANT cause diagnosis:** not now (post-paper list). The claim is restricted, as T.
- **κ:** dropped, as proposed.
- **Major 5:** T. The text says each null draw rebuilds the flux block with the same 100 constraint weights, and gives
  the thresholds.
- **s7 (W-4):** Joseph's; held.
- **s9:** "That test is a next step." stays byte-identical; the paragraph is shortened around it.
- **s8:** the note carries the sentence at both release revisions, so it is cut from the paper and check_sec4's anchor
  moves.
- **s11k:** approved as proposed.
- **Rater-copy fix:** approved.

## Batch status (the T batch)

| Rows | Status | Where |
|---|---|---|
| 1.1, 1.2, 1.3, 1.7 | done | §3.1 equation (eq:xsec), c ≡ 1, the regressor's equal weights; §3.2 the 5D universes' weights; S4's step list and regressor clause; limitation 8 |
| 1.4 | **L, not T** | no committed record prints the four C_resp scale factors (note sec_fived16.tex:106 and Supp S5 name only "its own one-standard-deviation factor"). They are to be read from the C_resp producer's configuration, which needs a ruling to add it to the L list |
| 1.5 | done (the table); the CSVs are L | S5 tab:construction |
| 1.6 | done as is | S9's test tables give each test's estimator, truths, split, repetitions, statistic and threshold |
| 2.1, 2.7 | done | §6.2 opening: the conditional-test list |
| 2.2 | done | §6.2 tab:cov2d |
| 2.3, 2.4 | done | §7: an ll5d-status sentence in all four cases (graded / descriptive / invalid / stopped); the route variants unchanged |
| 2.5 | done as is | §6.2 and S9.4 already state the one-way implication and its rank condition ("16 degrees of freedom" / "the same n") |
| 2.6 | done | the ll5d-anypass case in §6.2: "They do not validate the uncertainty of the data result."; §7's graded case |
| 3.4 | done | §3.2 and S5 :332 |
| 3.1, 3.2 | A, declared by tier3-design | — |
| 3.3, 3.5 | L / after A | 3.5's text waits for 3.1–3.3 |
| 4.1, 4.4 | done | S1 tab:bookkeeping; §2's 1A clause |
| 4.2, 4.3 | L | — |
| 4.5 | done | κ and its class reading removed from §4.1 (now §4.2); S8 keeps its definition, adding "The paper does not use this classification." |
| 5.1, 5.2 | done | §3.3 (reference tail area, a score); Table 2 and S9's test 5 say "No difference detected" |
| 5.3 | done | §5.4 and S8: each draw's flux block uses the same 100 constraint weights (effective number s1-flux-neff); T = 194.4 against χ²₁₆'s 35.89 and the Hotelling limit's 46.09 |
| 5.4 | done as is | §6.2 and §7 describe where the χ² sits, not its cause |
| 6.1 | done | "overshoots the truth along the prior-to-truth direction" in the abstract (prr-abs less-less), §5.3, Table 4's caption, §7, S9.3 and S9 test 4 |
| 6.2, 6.3, 6.4, 6.5 | done | §5.3: the discretization sentence; RMS and χ² beside ρ; the classes and labels moved to S9.2 (formerly S9.3); the closing sentence |
| (a) GEANT | done (T) | §6.2 second-test design and S9.5 (formerly S9.6) |
| (c) stopped first test | done | one paragraph in §6.2; S9.4 keeps the findings |
| (c) free-proton | done as is | — |
| (c) superseded | done | S4's history table → four sentences and a note pointer; S9.1 removed, with a note pointer in S9's opening |
| m1–m4, m6, m9, m11a–c | done | see the rows |
| m5 | L | — |
| m7 | done (the identity); its number is L | S5 |
| m8 | done in part | one design sentence in §3.3; "specified/fixed in advance" cut where §3.3 now covers it (§4.2, §5.3, §6.1, §6.2). Kept where it is the reading (RS1's protected paragraph, the status glossary, stopping rules) |
| m10 | done | \clearpage before the Supplement's references; make_supp_rater_copy.sh counts figure captions before and after blinding, and on 2bfb1410c's sources it fails ("blinding dropped a figure: 1 of 2"). Figure S2 is now Fig. S4, since the tension map (S2) and the prior-response figure (S3) moved in |
| s1–s6, s8, s9 | done | §3.1 order; §4.2 "Paired comparisons with other unfoldings"; §4.1 carries the per-period readings; §5.1 → S4 and §5.3; §5.3 order; §5.4/§5.5 split; the 6 % sentence cut; §7 shortened, ONCE kept |
| s7 | done in part, W-4 held | §6.1 leads with the released cells; the floor accounting moved to S4 ("The ensemble average's bias criterion"); the bias-variance sentence held for Joseph |
| s10 | done in part | the paper gains the equation, the largest differences and the qualifications; S4 loses its history table. S9's four test tables are kept: Table 2 now lists only the principal findings (15 rows), so S9's tables are the only full ledger, and each pair of five tests fills one page |
| s11b, s11e, s11f, s11g, s11h | done | Figs. 2 and 5 → S6 and S9.2; the sixteen-cell sentence before Fig. 6; Table 1 after the cell construction; Table 2 principal findings |
| s11i | **declined** | Table 3's paragraph is make_values LISTED_CLAIMS-anchored (its four sentences) and reads "the middle columns" and "the right-hand columns" by name. Compacting the columns would change anchored claims; make_figures.check_against also reads Table 3's truth order. The director may rule otherwise |
| s11k | declined in part (ruled) | Table S14 and Fig. S4 (formerly S2) stay; Table S15 stays, since #981's Q06 is its label and Q05, Q07 and Q14–Q18 sit in S10 |

**Tooling found and fixed in this batch:**
- check_supp_pointers.py matched only whole-number pointers (`S(\d+)\}`), so every subsection pointer (\ssec{S9.4}{…})
  went unchecked. It now numbers subsections and has a self-test case. At 2bfb1410c all 53 pointers pass under the fixed
  check, so the gap hid no wrong pointer then; at the new head it caught four in the hold.
- check_sec4_receipts.py's earlier-estimator anchor now reads sec_5d.tex sec:coverage-5d ("coverage as low as 0.060"):
  17/17 PASS, and test_check_sec4_receipts.py passes (17 tests).

## Second batch (2026-11-11, after the director's rulings on d1d6f1ded)

| Rows | Status | Where and source |
|---|---|---|
| s7 | done | §6.1: the W-4 bias-variance sentence is cut. Joseph's decision, relayed by the director: "Cut it (Recommended)". BV96 had STOPPED (#1017), so "is to address" was stale. Record: docs/orchestration/DECISION-20261111-joseph-bv-sentence-cut.md (#1075, merged; blob ad9842f3, sha256 06f1b440…). The stability gain, the bias increase and "not adopted" with its rule stay. |
| 1.4 | done (L) | S5: the four C_resp factors are 3.5 % (protons), 5 % (mesons), 3 % (electromagnetic) and 20 % (other). Source: the reported readout's meta.sizes (assigned-uncertainties/cresp/cresp.json, READOUTS cresp 19bb2ee1). Check 1: its code_sha256 for build_cresp.py, fe1aec8b, equals nd-unfolding/build_cresp.py on main (:38 SIZES). Check 2: the readout's primary list is proton, meson, em, other; xtalk is a variant, not in C_resp. |
| m7 | done (L) | S5: fᵀC⁻¹f under the reported covariance, without V_g, is 584.2 on the 16 cells and 438.8 on GiBUU's 8, so λ⁻¹ = 0.01 is below 3×10⁻⁵ of it. Inputs: supplemental/xsec16_cross_section.csv (adfb17d7…) and xsec16_covariance.csv (f7e25107…); λ = 100 on absolute f (fd_g_compare.py:51, :153). |
| 3.3, 4.2, 4.3, 1.5, m5, s11c | waiting on Perlmutter | The director's ruling: one read-only login-node session after the maintenance, after the cov2d fence and Joseph's cert renewal, with the script's sha sent to the director before it runs. For s11c and m5, the existing products are fetched if present; otherwise the A is priced. |
| 3.1, 3.2, 1.2 (A) | with tier3-design | The declaration (three arms). |

# F. The fresh referee read (gpt-6.1-sol, 5/10, on 9ab00ec9)

**Report:** `secondary-results/referee-methods-fresh-20261111/gpt.txt` (PR #1076). Rows are named F<major>.<sub>,
F§4-<n>, Fm<n> and Fs<n>. "= 1.2" etc. cross-references a recheck row above. Classes and rules are as above.

## Majors

| # | Request | Class | Source / inputs / cost | Proposed resolution | Misreading? |
|---|---|---|---|---|---|
| F1.1 | The equal-weight misses regression against a physically weighted one: nominal closure, the principal deformed truths and data, on cell integrals and the failing covariance directions | A (= 1.2, widened) | 1.2's arm grows from a data refit to four unfolds of (e): data, nominal closure, and the GiBUU and q3 truths noise-free. About 0.15 node-h each (pv-ladder/BINDING.md:15: three 5D unfolds ≈ 0.45 node-h), so about 0.6 node-h; wall under 1 h; does not wait for LL5D | Report the cell and eigen-direction changes in §3.1 and S4 when it runs; limitation 8 stays until then | no |
| F1.2 | Whether residual dependence on reconstruction acceptance or omitted truth information matters | A (a new arm) | Design: (i) refit with the regressor's inputs widened by truth quantities outside the five (the neutrino energy, the vertex position and the leading-proton kinetic energy), at the same four points as F1.1; (ii) a transfer test in simulation: mask a random subset of matched events as if missed and compare the regressor's prediction with their known step-1 weight, overall and against those omitted quantities. (i) costs about 0.6 node-h; (ii) is one fit on one iteration's stored weights, about 0.15 node-h. In all, about 0.75 node-h; wall under 1 h; does not wait for LL5D | As F1.1 | no |
| F1.3 | Report changes on data, including the covariance-weighted directions | A | the output of F1.1 and F1.2 | As F1.1 | no |
| F2.1 | Account compactly for what pseudo-data and simulation side do: truth and reconstruction weights, flux denominators, simulation resampling, clipping | T | LL5D-DECLARATION.md §2 (the like-for-like construction, group by group); Supp tab:cov-design rows; OUTCOME-20261108-1b-precheck-part1.md:41-42, :70 | A column in S9.3's design table for the first test's checks, against the second test's like-for-like construction, built from those records | no |
| F2.2 | Resolve the GEANT4 neutron and proton mismatch before any coverage claim involving those bands | A (priced below), with T meanwhile | Design: for each band's two universes, rebuild the pre-check's three objects (the pseudo-data side, the simulation side and the nominal-truth Dnom) with the operations switched on one at a time: truth weights, reconstruction weights, the flux and denominator recomputation, simulation resampling and clipping. Which switch moves the 6+4 departing cells (R00, R02, R08, R09, R10, R11; R01, R05, R07, R08) into [0.9, 1.1] identifies the mismatch. Items: 2 bands × 2 universes × 3 objects × 6 switch settings = 72 unfolds, plus 3 CV controls = 75. Unit: 0.027–0.029 node-h per item (FD-1B-PRECHECK-FD-DECLARATION.md:229-230; 327 items cost 9.35 node-h, OUTCOME-20261108-1b-precheck-part1.md:29), so about 2.1 node-h expected. Cap 4.0 node-h with the pre-check's 2.5 h job limit. Wall about 3 h with the pilot gate; does not wait for LL5D | Until it runs, every coverage statement on these bands stays restricted: the paper says the primary reading excludes them, and that an excluded band's treatment is not validated by the restricted test | no |
| F2.3 | The pending test's four outcomes: no under-coverage, under-coverage, invalid or stopped, and repaired or continued after a check | T | ll5d variants (V-L1 to V-L3); §6.2, §7, Table 2 | Already implemented. Add to §6.2 that a repaired or continued run is descriptive unless an independent confirmation follows | partly: already implemented |
| F2.4 | Excluding bands defines a restricted test and cannot validate the omitted treatment | T | as F2.2 | One sentence in §6.2 and S9.4 | no |
| F3.1 | Correct the 2D universes' misses approximation, or bound it against the final covariance and the failing eigenmodes | A (Joseph's; **the price in this row is wrong; see "F3 corrected" below**) | Note sec_systematics.tex sec:uq-2d-scope: a missed event keeps the CV weight divided by the universe's completeness; tested in MaRES_0 and Flux:23 only, against an earlier ten-seed σ about 3.7× the current block. **(a) Consistent rebuild:** rerun the 185 weight universes with each missed event at its universe truth weight, rebuild the systematic block, and compare with the reported 2D covariance in the T2A eigenbasis beyond the 73 largest directions. Unit: the stage-C grant priced the universe set at 35 jobs × 0.25 node-h cap = 8.75 node-h (AUTHORIZATION-20261015 §2), with expected/cap 44.9/117.9 there, so about 3.3 node-h expected; wall about 1–2 h. **(a+) Also rebuild C_T at the two tunes** with the corrected procedure and regrade the 300 stored errors per tune: about 2 × 8.75 node-h more cap (about 6.7 expected), plus a login regrade if the errors are stored, else a rerun of the 300 per tune (COV2D cap 165.8 node-h, COV2D-AMENDMENT-1:184). **(b) Bound only:** rerun the 25 universes with the largest weight in the failing directions at two seeds each, with both treatments, about 10 jobs × 0.25 = 2.5 node-h cap (about 1 expected), giving a band-level bound against the final covariance's eigenvalues. Recommended: (a), since its cost is close to (b) and it removes the approximation rather than bounding it; (a+) if the coverage verdict itself is to be re-graded. None waits for LL5D | Until it runs, limitation 7 states the approximation and the earlier test's weakness plainly | no |
| F4.1 | Call the integral a normalization benchmark | T | §4.1 | Reword. | no |
| F4.2 | Give the IBU-to-publication distance beside OmniFold's | L (local, done) | read-2/readout.json (0ee21301…): D_E_R = 2.270; D_IBU = 1.027 at K = 10 (primary) and 0.830 at K = 5; D_IBU at K = 1, 2, 3, 4, 5, 10, 15, 20 is 3.95, 1.59, 1.08, 0.90, 0.83, 1.03, 1.52, 2.16. OUTCOME-20261106-ref-c2c1-read.md: "printed and read by nothing"; the record licenses no attribution and leaves "the source of the shape difference has not been identified" standing | Print D_IBU at K = 10 and K = 5 beside D_E_R in §4.2, descriptively, keyed through make_values, with the record's no-attribution scope | no |
| F4.3 | Full-sample background and out-of-phase-space yields | L (= 4.2, pscratch) | — | — | no |
| F4.4 | Which inputs can be checked against the publication; unavailable inputs identified | T | tab:bookkeeping | Keep "not compared", which is what this analysis did. Whether the publication releases an input is not a claim the records support either way | no |
| F4.5 | Keep the distance descriptive | T | §4.1 already | Done as is. | no |
| F5.1 | State truth W's Q² convention (massless muon, fixed beam axis) in the main text, against q3's exact four-vectors | T | Supp S2 (:34-36: truth W uses the massless-muon Q² with θ_μ from the beam axis) | One clause in §2's W definition | no |
| F5.2 | State the acceptance boundary behind "no underflow nor overflow" | T | Supp S3 :141-150 | One sentence: reconstructed events outside the window are excluded, and their truth contribution enters through the misses | no |
| F5.3 | Weighted fractions excluded by the window and by negative W² | L (pscratch) for the window; T for W² | negative W² = 4.9×10⁻⁵ of the weight, already in S2 :80 | Join the read-only session | no |
| F5.4 | The four unreported boxes' contribution | L (pscratch) | h2_definition.json lists them ([2], [6], [10], [14]) but not their content | Join the read-only session | no |
| F6.1 | The sixteen cells' standardized rounding shifts and their size against the statistical σ | L (local, done) | rs1_r0.json (READOUTS rs1r0 724f0c3a): R0a = σ_J/σ_stat per cell has median 0.512, min 0.385, max 0.819; R0b (variances subtracted) has median 0.596, max 1.43 | Print R0a's median and range in §6.1 (keys from rs1r0); two-perturbation shifts on the sixteen cells are not in a record (pscratch, if wanted) | no |
| F6.2 | The perturbation law; what the statistical block estimates | T | note app_statmethods_nd.tex:37 (uniform within half a float32 ulp, edge-safe); paper §3.2 | §3.2: the law in one clause, and that the block estimates the spread of the randomized procedure (data resampling with a fresh rounding perturbation per replica), which for the deterministic output adds a numerical-variability term to the sampling variance | no |
| F6.3 | Show the ensemble trade-off quantitatively | T | keys ens1-g-rms, ens1-g-rmsc (0.056467 against 0.055955), ens1-median/max against s5e-round-* | §6.1: the two RMS values beside the stability gain; "not adopted" keeps its rule | no |
| F6.4 | If advocated as a mitigation, test it on data | T | §6.1 already: "evaluated only on simulated pseudo-data"; it is not advocated | Done as is. | no |
| F7.1 | The run-period block as an empirical sensitivity allowance | T | §3.2 and S5 | One sentence. | no |
| F7.2 | The 68 % interval: its stochastic model, or call it an illustration | T | FD-CT-5B-AUDIT-DECLARATION.md:276-282: the three groups as draws of one Gaussian period effect, ν = 1.82 Satterthwaite effective degrees of freedom for the exposure-weighted spread, χ²_ν interval [0.73, 2.56]; known before the data, not calibrated | State that model in §3.2, call the interval a scale illustration under it, and say it says nothing about the block's orientation | no |
| F8.1 | A route from accessible inputs and versions to the principal findings | X (the deposit); T (the description) | note app_release.tex (the candidate release package and its reproduction limits) | S3's "Machine-readable files" gains a paragraph on what the package contains and reproduces, as the note's App. G states it, with no claim of deposit. The Data availability section (protected) is unchanged | no |
| F8.2 | Essential evidence in the manuscript or Supplement, not only the note | T | this round's moves | The F rows bring the like-for-like accounting (F2.1), the misses role (1.1/1.2) and the conventions (F5) in | no |
<!-- absence-ok: the F rows' "until it runs" and "not yet identified" scope pending analyses (F1, F2, F3) that are priced here; they are not claims that a result does not exist -->

## The report's §4 rows marked (a) or (c)

| Row | Class | Resolution |
|---|---|---|
| (a) GEANT neutron/proton discrepancies | = F2.2 | A priced; restricted claim meanwhile |
| (c) Chronology of the stopped test and redesign | T | The paper keeps the mismatched-estimand explanation in one sentence, and the "staged redesign" clause moves to S9.4. S9.4 keeps the controls' outcomes |
| (a) Equal-weight misses regression | = F1.1, F1.2 | A |
| (a) Approximate misses weighting in the 2D universes | = F3.1 | A, Joseph's |
| (a) The numerical 68 % run-block scale interval | = F7.2 | T: a stated-model illustration |
| (c) Abort and sampling-validation history of unused samples | T, done as is | S10.1 keeps one clause per generator as each record states it; no history |
| (a) Reproducibility package and essentials on the note | = F8 | X and T |
| (c) Superseded configurations, unused classifications, decision chronology | T, done as is (recheck (c) rows) | S4's history is four sentences; the class taxonomy is in S9.2 |

## Minors

| # | Request | Class | Resolution / note |
|---|---|---|---|
| Fm1 | The abstract is overloaded | T, partly | It conflicts with the recheck's m3, which asked for both rounding summaries in the abstract. Proposal: keep the principal failures and the illustrative status, and cut the stability numbers to "beyond a requirement fixed in advance, also on the sixteen released cells". For the director's ruling |
| Fm2 | Avoid certification language: "bias-screening rule", "passes this rule" | T | §5.5 → "Per-cell bias-screening rules"; "valid" → "pass" wherever not protected. #981's Q19 ("Fourteen cells are valid under it") and Q09 stay verbatim in S11 |
| Fm3 | "Simultaneous unfolding of five correlated observables"; reserve "five-dimensional" | T | Sweep the paper's "five-dimensional" |
| Fm4 | One covariance notation: C_reported | T | Define $C_{\mathrm{rep}}=C_{\mathrm{total}}+C_{\mathrm{resp}}+C_{\mathrm{PL,5D}}$ in §3.2 and use it in the paper's text and captions. Table headings keep the explicit sums |
| Fm5 | "The five-observable training-seed block" | T, **protected** | The phrase sits in the B0 sentences (check_restyle's protected span). For the director: a one-word change to a protected span, or a clarifying sentence before it (proposed: before it) |
| Fm6 | Relate the 20-perturbation spread to the two-perturbation grading | T | One sentence in §6.1 |
| Fm7 | Figure 2's injected departures, unsupported cells and populations | L (= m5, pscratch) | — |
| Fm8 | Non-detection 13.87 < 14.46 is not equivalence | T | §4.2: "no difference detected in the tested subspace (rank 12) at that resolution" (the record: rank 12, OUTCOME-20261106-ref-c2c1-read.md) |
| Fm9 | Drop the Gaussian expected flag counts in S9 | T | Remove the Gaussian reference counts from S9.1's group paragraph and the tunes paragraph |
| Fm10 | The run-period step's ±0.41 %: which fluctuations; the reference without 1F | T | period-unfold-20261014/REPORT.md:55-66 (10 paired bootstrap draws) and :113 (the unfold reference P_A includes 1F, while the reconstruction-level reference was 1A–1E) |
| Fm11 | "small next to the reported covariance" needs the flagged truths' exception | T | S9.1's smaller-matrices paragraph |
| Fm12 | Typography | T (check) | Check the figures in the PDF; the damaged glyphs are pdftotext artifacts of math in figure text |

## Structure

| # | Request | Class | Resolution / conflict |
|---|---|---|---|
| Fs1 | The final five-observable result leads §6.2's five-observable part; the stopped test follows as background | T | Move the second test's two paragraphs and its variant group before "The first five-observable test." |
| Fs2a | §3.1: a short disclosure of the two choices; the numerical history to §4.1 and S4 | T, a compromise | The recheck asked for the reverse (history out of §4.1). Both agree on S4: §3.1 keeps one disclosure sentence, the χ² values move to S4, and §4.1 keeps its "descriptive; not a blind validation" sentence |
| Fs2b | §3.2 opens with a compact definition of both covariances | T | One opening sentence |
| Fs3a | §4.1's removal-of-1G–1M discussion → §4.3, a conclusion in §4.1 | T, a compromise | The recheck asked the reverse. Details to S6 (which the recheck allowed), one conclusion sentence in §4.1 with a pointer |
| Fs3b | The IBU-to-publication benchmark in §4.2; C1 shortened | T + L | = F4.2; C1 to one sentence |
| Fs4a | §5.3 leads with the projections and total biases; ρ defined right after | T | Reorder |
| Fs4b | The 109-joint-cell exact-binned comparison → S8, with a short context in §5.3 | T, a compromise | The recheck moved it into §5.3. S8 already carries its per-truth numbers; §5.3 keeps one sentence with the grid warning |
| Fs4c | Merge §5.5 into §5.2 as auxiliary bias diagnostics | T | A \paragraph at §5.2's end; sec:vhalf kept |
| Fs5 | §6.1 order and repeated range | T, constrained | The B0 sentences (protected) say "quoted above" of the rounding numbers, so they must follow them. The repeated sixteen-cell range in the lead is replaced by F6.1's ratio |
| Fs6a | §7 begins with the findings; the checklist follows | T | Swap |
| Fs6b | §7.1 grouped: bias, numerical, calibration, data/response | T | Regroup the list |
| Fs7a | Split §3.2's run-period paragraph and §4.1's condition-number paragraph | T | Split |
| Fs7b | §5.3's closing sentence joins the preceding paragraph; S7 is too thin | T | Join; fold S7 into S3 as a paragraph, renumbering S8–S11 to S7–S10 |
| Fs8 | The main paper gains the W convention, misses, coverage assumptions and control outcomes | T | F5.1, 1.1/1.2, 2.1, F2.1 |
| Fs9 | Figure placement (Fig. 1 near §4.1) | T (layout) | Try the float's placement; check in the PDF |
| Fs10a | Table 1 not to interrupt the estimator description | T (layout) | Place before §3 |
| Fs10b | Table 2's status dictionary: only the statuses used | T | Trim |
| Fs10c | Table 3's third covariance reading to the Supplement | T, declined | As s11i: LISTED_CLAIMS anchors the paragraph that reads Table 3's right-hand columns |
| Fs11a | Fig. S2 with the published-result comparison | T (layout) | Place in S6 earlier |
| Fs11b | Fig. S3 is not a bound on data bias | T | Caption clause |
| Fs11c | Fig. S4 and the generator tables optional; Tables S8–S11 consolidated | T, declined in part | As s11k and s10 (#981; one page per five tests) |

## F batch status (the T batch for the fresh read)

| Rows | Status |
|---|---|
| F2.1, F2.3, F2.4, F4.1, F4.2 (L, local), F5.1, F5.2, F6.1 (L, local), F6.2, F6.3, F7.1, F7.2, F8.1, F8.2 | done. F4.2's keys c2c1-dibu, c2c1-dibu-k5 and c2c1-der come from read-2/readout.json, and make_values asserts D_IBU/D_E_R = ρ and D_E_R = 2.27. F6.1's keys rnd16-r0a-* come from rs1_r0.json R0a_summary |
| F2.2, F3.1, F1.* | A, priced above, for the director (F3 for Joseph) |
| F4.3, F5.3 (window), F5.4, Fm7 | L, joining the pscratch session |
| F§4 (c) stopped-test chronology | done: the "staged redesign" clause leaves the paper; S8.4 keeps it |
| Fm2, Fm3 (no "five-dimensional" in the paper text), Fm4 (C_rep defined in §3.2), Fm6, Fm8, Fm9, Fm10, Fm11 | done |
| Fm1, Fm5 | waiting for the director's rulings (the abstract conflict; the protected B0 span) |
| Fm12 | checked: 0 Overfull in both builds; the damaged glyphs are figure text in pdftotext, not the PDF |
| Fs1, Fs2a, Fs2b, Fs3a, Fs4a, Fs4b, Fs4c, Fs5 (as constrained), Fs6a, Fs6b, Fs7a, Fs7b, Fs8, Fs11b | done. S7 is folded into S3, so S8–S11 are now S7–S10; check_supp_pointers caught and fixed all 30 affected pointers |
| Fs9, Fs10a, Fs11a | layout left to the floats; checked in the build |
| Fs10b | done as is (Table 2's statuses are those used) |
| Fs10c, Fs11c | declined, as s11i and s11k |

## F rulings applied (2026-11-11)

| Rows | Status |
|---|---|
| Fm1 | done: the abstract drops the stability numbers and keeps "its results are sensitive to rounding-level changes of its inputs, beyond a requirement fixed in advance"; the numbers are in §6.1 |
| Fm5 | done: a clarifying sentence precedes the B0 span; the span is verbatim (check_restyle reports no protected-text failure) |
| F4.2 | done, by Joseph's decision with the director's ruling on its PRD read (dibu-read/referee-read.md, ACCEPT WITH CHANGES; the read's wording). §4.2 prints IBU on the same inputs at χ²/ndf 1.03 (K = 10), 0.83–1.59 (K = 2–15), 2.16 (K = 20) and 3.95 (K = 1), against 2.27. The keys c2c1-dibu-* come from D_IBU_every_K. The inputs are not excluded as a contributor, the mechanism is not established, and the values are descriptive. Table 2's IBU row, §1, §4.1, §7 and the abstract now say "mechanism" and state the comparison. §4.1's sentence changed; #981 re-sources build_package.py:848 and PROVENANCE.txt:185 at its re-pin |
| The claim sweep | no other sentence implies the inputs cause the difference. §5.4's "leave open whether these inputs equal the publication's", S1's selected-sample scope and Table S1's "not compared" are consistent with "not excluded as a contributor"; S6's flux-band sentence concerns the band's size |

## F3 corrected (2026-11-11)

- **The error.** F3.1's basis, "35 jobs × 0.25 node-h cap = 8.75 node-h (AUTHORIZATION-20261015 §2)", used the wrong
  row. In that §2 the 35 runs are S4(ii), 7 universe settings × 5 seeds, not the universe set. The prices of (a), (a+)
  and (b) above are void.
- **The price.** COV2D-G2R-DECLARATION.md (#1079, merged; sha256 225a89ae…) §7 re-prices it from COV2D's own charges:
  - 44.67 node-h bought 349 universe unfolds, 0.128 node-h per unfold;
  - the corrected unfold runs 1.08× to 1.38× slower;
  - (a), 175 unfolds at the data: 24.2–30.9 node-h;
  - (+), 350 unfolds at G18 and AR23: 48.4–61.8 node-h;
  - prepare: ≤ 1 node-h;
  - **total about 74–94 node-h expected, cap 110 node-h**.
- **Joseph's decision:** the full regrade, (a) and (+), at that price. Adopting C_new at the data is his, after the
  result.
- **The text.** §10's outcome table, fixed before any number is read, decides the §6.2, limitation 7, abstract and
  limitation 1 text. The current text holds under its "not yet run" row: limitation 7 states the approximation and the
  earlier test's weakness, and the 2D grade is the first grade. Each row's edits are made when the result lands.

## F2 revised (2026-11-11)

- **The director:** no new analysis. The GEANT n/p diagnosis the referee asks for already ran (the band diagnosis,
  #935 and #971).
- **The finding (director-helper-2):** the referee's five operations are inert or already like-for-like.
- **The record:** a records-only note mapping major 2 onto those records is in preparation. When it merges, it is cited
  here, and the text states, with no new licence:
  - that the two constructions match in each listed operation;
  - that the cause lies inside the estimator and is unclassified;
  - that the primary reading excludes the bands.
- F2.2's A row and its price are withdrawn.

## F2 and F3: the records cited (2026-11-11)

- **F2:** docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/geant-np-records/GEANT-NP-REFEREE-MAP.md
  (#1081, main 05a74e7c; sha256 05421836…).
  - The text (S8.4, and §6.2 in brief) states, in the director's record-true phrases:
    - truth weights "change the σ ratio between the two simulation-side blocks by at most 2×10⁻⁷" (Part 1's readout
      8e05ca9b: 6.0×10⁻⁸ for neutron, 1.6×10⁻⁷ for proton);
    - flux and denominator "unchanged for these bands";
    - resampling "not part of either compared object";
    - clipping "not exercised";
    - #971's EQUAL sentence for the reconstruction weights.
  - The conclusion is #971's: the constructions match in each listed operation, what separates them lies inside the
    estimator and is unclassified, and the primary reading excludes the bands.
  - The channel split is not printed (NOT CITABLE).
- **F3:** the corrected price's binding is COV2D-G2R-BINDING-1.md (#1080): 73.6–93.7 node-h expected, cap 110 node-h.

## The L rows: the read-only pscratch session (2026-11-12)

The session ran under the director's go for `pscr_remote.sh` 9513d080, `pscr_fetch.sh` 9401337b and
`w_inventory.sha256` a08ae0eb. It ran on login27 at 00:08:59Z with the fence clear and 0 node-h. Its 102 inputs were
read with O_NOATIME, stat unchanged and whole, and every sha matches its record. The receipt is `pscr-20261112/`
(f70e805c). The derived numbers come from `l-rows-20261112/code/l_rows.py`, whose readout is
`l-rows-20261112/derived/l_rows.json`, pinned as READOUTS `lrows`. The director accepted the receipt's recompressed
member, the force-added npz, the hook fixes and m5's definition.

| row | source | printed |
|---|---|---|
| 4.2/F4.3 | `work_proxy.npz` (42ce788b) and `proxy_hists_meta.json`'s POT. The template is k·B over D on the 14×16 grid: 2.906 % in the full sample, 2.72–3.23 % per playlist. Data in the grid is 4,091,707, equal to E_U's; the template is 118,895.5 against E_U's 119,132.37, 0.20 % lower | table S1's new row "Background template, full sample" (keys bkg42-*) |
| 4.3 | fig:tension2d's per-bin contributions: the committed capture of the current figure (e3f12c5d), 205 bins summing to C-PUB's χ² 465.41527219152636. The cell set was fixed before the fractions were read: the largest contributors, until their sum first reaches χ²/2. That gives 15 bins and 51 %. The template is 3.08 % on them against 2.91 % overall, and its Spearman ρ with the contribution over the 205 is −0.09 | one sentence before fig:tension2d in S6 (keys bkg43-*) |
| F5.3 | `f53.json`: weighted fractions of pass_reco w_reco, using r4_migration.py's masks (its unweighted control matched). 2.0×10⁻⁵ is outside the reco window and 1.1×10⁻⁴ has its truth outside the grid; those 1,755 gen rows include the −9999 q3/W sentinels | one sentence after the negative-W² paragraph in S2, the window fraction only (key f53-win). The gen-side 1.1×10⁻⁴ is not printed. The meaning read found that it contradicts S3's "the truth grids are exhaustive" and overlaps the negative-W² exclusion beside it. Whether its 1,755 rows are only the −9999 sentinels is not in a record. This goes back to the director |
| F5.4 | `stage1_inspect.json` mc.H2 at h2_definition.json's unreported boxes [2], [6], [10], [14]. They hold 2.9×10⁻⁸ of the truth weight and 6.5×10⁻⁸ of the expected reconstructed signal | one sentence after the unreported-box sentence in §2 (keys f54-*) |
| 3.3 | `r33_leave_gibuu.py`. T2B's B0–B3 re-pass, and the existing grade is reproduced on all 16 records. With only GiBUU left out of C_model, the \|z\| > 2 count moves only at q3, in R15, the same cell as T2B's M1 (max \|z\| 1.62 → 2.02). χ² rises by at most 9.7, at q3. The GiBUU truths' grades already leave that component out | one sentence in S8's T2B paragraph (keys r33-*) |
| 1.5 | the table was done earlier (tab:construction). The optional per-block CSVs are not made; see below | — |
| m5/Fm7 | `m5_injected.py`, using s5n_truth_check's full-sample definition, M1 @ x(W) / M1 @ x(nom) − 1. Max \|injected\| is 21.4 % for W1 (EW6), 14.8 % for W2 (EW37; 11.8 % at EW1 among supported cells) and 27.5 % for W3 (EW7). The W1 and W2 controls pass to 8×10⁻¹⁵. The unsupported cells are EW11, EW36 and EW37, with truth weight 777, 246 and 629. Not checkable: a fine cell populated in the full MC but empty in all 100 halves | waiting on the figure lane's producer (below) |
| s11c | `assess_receipt.json` points.eavail_gibuu, the reported estimator over 20 experiments. The residuals are present: 73.86 % at EW29, as §5.1 prints (s5e-gibuu-ewmax), with a median \|residual\| of 10.8 %. No A is needed | waiting on the figure lane's producer (below) |

**Meaning read** (lrows-read/pairs.tsv, 5 rows; an independent reader given the sources, not the conclusions). Every number re-derived. One defect: M003's gen-side clause, which is removed (above). Two wordings were tightened: S1's clause now names "genuine background and out-of-phase-space signal" instead of "the two rows above", so a reader does not subtract 0.35 % from 2.74 % on 1A; and S8's "moves" became "takes … past |z| = 2".

**The 4.2 split.** The fraction printed is that of the combined background template, the `mc_background` tree's
selected rows (sim_background_pass = 1, weight w_bkg), which the two-dimensional analysis subtracts before
unfolding. No committed record divides that template into genuine background and out-of-phase-space signal. The 1A
genuine-background figure of 0.35 % has no receipt (stageF referee-presentation REPORT.md:124-127), and whether the May
files' `mc_background` includes out-of-phase-space signal at all is inferred from a driver comment, not verified. So
table S1 gives the combined fraction and says its division between the two rows is not recorded. A read-only probe
of the twelve per-playlist May files is approved in principle by the director, and would give the split if their
bkg_* branches exist; a re-run of the event loop is a separate price.

**F5.3, the out-of-window rows.** OUTCOME-20260925-s5c-purity-background-bias-at-high-W.md:37 says "428 of 20.4 M, zero
weight". The code says this refers to the measured weight only. `nd-unfolding/s5c_pseudo.py` :104-112 (main 50402c0a3,
sha256 d81d4f46…) gives every pseudo-data entry outside the [first, last) window measured weight 0, while
`s5c_unfold.py` :124-127 (510d749a…) passes the same rows to `omnifold_loop` at their own w_reco, 72.41 in total. The
OUTCOME line is right for what it describes, so no records correction is listed. The paper does not say "zero weight".

**Not done:**
- **1.5's optional CSVs.** Per-block matrices are a release item, and #981's lane owns the release package.
- **m5/s11c's figure series.** These go through the figure lane's producer, `fig_m3_deformation.py`, which asserts its
  arrays against the presentation baseline. The operands are ready: `derived/m5_injected.json` and
  `assess_receipt.json` points.eavail_gibuu, first 42 entries of mean_rel. Routing is the director's.

## The L rows, continued (2026-11-12)

**m5/Fm7 and s11c: done.** The director routed them to me after I checked the file's ownership: no OWNER line, no
other open PR on these files, no figures-lane session live. Figure 3, the reported estimator, now draws:
- each withheld shape's injected change as a dashed step in its own colour, from `pscr-20261112/derived/m5_injected.json`;
- the reported estimator at the GiBUU-to-GENIE change (assess_receipt.json points.eavail_gibuu, red), with its
  injected change, which is the lower-capacity panel's (the same truth, ratio file 45cc3e0a and amplitude 1.0);
- the three unsupported cells shaded (EW11, EW36, EW37; keys fm7-tw-lo/hi give their truth weights, 246–777).

The new arrays are asserted in `presentation_original_arrays.json`. Its additions block records their sources, and
`inputs.json` re-pins it. The producer checks the GiBUU maximum (73.86 % at EW29, as s5e-gibuu-ewmax) and the three
injected maxima. make_values asserts that the caption's "at most 0.22 %" covers the GiBUU series too (0.185 %). The
caption states m5's not-checkable limit. The meaning read is in `fig3-read/`, and both rater copies were rebuilt.

**4.2: open item.** The referee's split of the background into genuine background and out-of-phase-space signal
cannot be measured from the May per-playlist files. The split probe (`split-20261112/`, exit 6) found that they lack
the truth branches (bkg_nuPDG, bkg_current, bkg_vtx_*). Their mtimes also precede the Phase-18 commit d1bc8813a,
before which the event loop left out of `mc_background` every event inside the signal definition, so the template's
composition is not established. Table S1's row now says "its composition is not recorded". A re-run of the event
loop would settle the split and is priced separately. The provenance search for the files behind the paper's template
(the merged CV and $UNI) is under way. Until it reports, S4 :222 and S1 :25, both carried from the note, and table
S1's out-of-phase-space row stay unchanged. Any change to the note's sentences goes to Joseph and the note loop.


**4.2: the records disagree on what the template contains.**
- The routing log says the out-of-phase-space set is empty under the reco cuts
  (d1bc8813a:2d-unfolding/2D_OMNIFOLD_RUN_LOG.md:1003-1009), yet the template is 2.91 % against the 0.35 % genuine
  background.
- The two percentages are different templates. The 0.35 % is April's Phase-11 `hBkgReco2D` on 1A (1,256 events,
  RUN_LOG :208), from the code that left every event inside the signal definition out of `mc_background`. The 2.91 %
  is May's Phase-18 template, 2.735 % on 1A.
- The counts reconcile exactly: the routing test's 4,277 (:1004) plus the 48,349 ν_μ CC events that Phase 18's
  truth-tree gate drops from mc_signal_reco (:1016-1018) equal the May 1A file's n_bkg_pass of 52,626.
- But the committed background loop does not route those events (d1bc8813a:…runEventLoopOmniFold.cpp:443-445, on the
  reco tree). So whether they are in the template is not settled by any record.
- An event-loop re-run with the truth branches is the only measurement. The director takes its price to Joseph if he
  wants it before submission.
- On the count reading (raw counts; superseded by the weighted record below), the May template would be about 92 % ν_μ CC that the truth tree puts outside the phase
  space (48,349 of 52,626, by raw count). Weighted shares are not recorded. This reading conflicts with
  d1bc8813a:MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp:443-445, whose background skip is evaluated
  on the reco tree and so does not route those events.
- **Considered and declined:** an entry-count read of the May 1A file (0 node-h). Both counts are already in the
  records, 2,682,267 = 2,730,616 − 48,349 in RUN_LOG :1051-1054 and 52,626 in proxy_hists_meta.json. The read cannot
  tell routed events from dropped ones, so no outcome would change a decision (the director, 2026-11-12). Nothing was
  run or committed. <!-- absence-ok: records that a declined read was not run, by the director's ruling; not a finding that a result does not exist -->
- **Where it gets measured:** the F1.2(i) event-loop re-dump lane, owned by tier3-design. It runs current code, which
  has carried the bkg_* branches since 3e855893b. The director asked it to keep mc_background with its truth branches
  and to add a control that its 1A pass histogram reproduces work_proxy's 1A B.
- **A later record (2026-11-12, found by the meaning read):** RUN_LOG :1052-1064, "Validation on 1A (2026-05-14)",
  says "`hBkgReco2D` integral 1,788 → 9,782 (+8 k weighted; the 48 k "Set E" reco-fakes are now correctly subtracted
  from data …)". The May 1A template summed from work_proxy (k·B in the grid) is 9,781.53, which rounds to that 9,782.
  - **Composition, as a record and not a measurement:** on 1A, weighted and POT-scaled, about 82 % (7,994) is Set E,
    ν_μ CC that fail the phase space on the truth tree, i.e. out-of-phase-space signal. About 18 % (1,788) is the
    earlier background. This supersedes the empty-set sentence at :1003-1009, which predates the fix.
  - **The conflict remains:** the committed background loop (d1bc8813a:443-445) does not show the routing. The same
    log records a build trap at :1069-1072 ("existed at two paths on disk … silently used stale code").
  - **The measurement:** C-BKG in the F1.2(i) re-dump pilot (tier3-design) measures this. If it passes, its 1A
    fraction replaces table S1's "not measured here" clause. The 82 % is not printed (the director: a narrative-log
    number with a code conflict does not meet the bar for a printed value).
- **The text, per the director's rulings of 2026-11-12:**
  - S4 :222 now reads "all selected simulated events other than signal inside the phase space (Sec. S1), that is,
    genuine backgrounds and out-of-phase-space signal".
  - Table S1: the 0.35 % row is deleted. The template row says its split "is not measured here". <!-- absence-ok: quotes table S1's scope clause; the split is unmeasured here because the May files lack the truth branches (split-20261112, exit 6), and C-BKG measures it --> The
    out-of-phase-space row says "routed into the background template and subtracted with it". "Run period" replaces
    "playlist" in this table and in the moved 1A sentence.
  - The S1 paragraph is DESYNCED from the note, with the reason recorded at :24 (the note's 0.35 % describes the April
    template). The 0.35 % sentence and the sentences resting on it are deleted, along with the self-referential "This
    paragraph does not split …", and "treated separately" becomes "routed into the background template".
  - The note is unchanged. Its fix goes to Joseph.


**4.2: C-BKG measured on 1A (`cbkg-20261112/`, 8b68bc79).**
- **Input:** base_cv, MP-1 S0's 1A event loop. Its mc_background reproduces the paper's 1A template exactly, with a
  largest difference of 0.0 against work_proxy's 1A__ana__B by the producer's rule.
- **Composition,** weighted, over the passing rows in the grid:
  - out-of-phase-space signal: 9.6–32.0 %;
  - ν_μ CC with an out-of-fiducial vertex (genuine): 83.2–60.8 %;
  - other flavour, wrong sign or NC (genuine): 7.2 %.
- **The bracket** is the inner and outer radius bounds on the 850 mm hexagon; 22.4 % of the weight lies between them.
  Narrowing it needs the analysis's own fiducial test (PlotUtils/CCInclusiveSignal.h truth::Apothem). That source is
  in the MAT tree on the cluster only, so its read waits on the director.
- **RUN_LOG :1061's ~82 %** lumps out-of-fiducial ν_μ CC with out-of-phase-space signal. Here ν_μ CC of any vertex is
  92.8 %, so the two are consistent.
- **Reading 4, RESPONSE.md only by the director's ruling:** the other-flavour, wrong-sign and NC class is 0.197 % of
  the selected 1A data, against the publication's 0.2 % (8655 events, which counts only those components). This is
  descriptive and untested, and the definitions may differ. <!-- absence-ok: scopes a descriptive comparison, by the director's ruling; not a claim that a result does not exist -->
- **Table S1:** the clause "is not measured here" was replaced once the bracket was narrowed (below).

**4.2: C-BKG-2, the composition measured with the analysis's own fiducial test (`cbkg2-20261112/`, 2a2af241).**
- **The source:** truth::Apothem and truth::ZRange, read from MAT-MINERvA/calculators/CCInclusiveSignal.h (cf9ee8c4,
  :103-104, :108, :122). The tree is at main 50d76314, as M4-W-RECORD.md:32 records. Port 1 (bkg_channel_split.py:58-70)
  is identical to it line by line, so its fraction is the measured value.
- **On 1A, weighted:**
  - out-of-phase-space signal: 10.4 % (11.4 % raw);
  - ν_μ CC with an out-of-fiducial vertex (genuine): 82.4 %;
  - other flavour, wrong sign or NC (genuine): 7.2 %.
  - The control is exact.
- **±1 mm vertex-position sensitivity:** 2.5 % of the weight (1,333 rows) changes class when the fiducial limits move
  by ±1 mm. The rule itself is exact, so this is not uncertainty in the definition; it stays in the receipt and here.
- **The run log reconciled:** RUN_LOG :1061's "Set E" (~82 % of the 1A template) is ν_μ CC failing the truth-tree
  phase space, which includes out-of-fiducial vertices. The measured split shows that most of that share is
  out-of-fiducial ν_μ CC, which S1 counts as genuine background; out-of-phase-space signal is 10 %. ν_μ CC of any vertex
  is 92.8 %, consistent with the record.
- **Printed:** table S1 now reads "subtracted before unfolding. Composition measured on playlist 1A only: about 10 %
  (weighted) is out-of-phase-space signal; the rest is genuine background, mostly ν_μ charged-current events with a
  true vertex outside the fiducial volume".
  - Key cbkg2-oops-1a; two significant figures, by the director's ruling; the PRD read's sentence split and "true
    vertex".
  - Both reads are in cbkg2-read/referee-read.md: PRD ACCEPT, meaning read OK.
  - The meaning read noted that MAT's code places the fiducial cuts in phaseSpace. The Supplement's S1 :26 sets the
    convention that out-of-fiducial ν_μ CC is genuine background, and the row follows it. Recorded here for a referee
    question.

**Follow-up list:** the docstrings of docs/…/m4-w/probe_mad.py:47 and playlist-spread-20261014/scripts/intensity.py:7 cite TargetUtils::IsInHexagon as the fiducial test. The event loop's truth::Apothem is a different function, which does not call it (cbkg2-20261112/README.md). Correct the docs; don't edit them now (the director, 2026-11-12).

**Follow-up list (optional):** counting whether F5.3's 1,755 gen-outside-grid rows are only the −9999 sentinels
(0 node-h, on OF5D). Printing that number would not help the paper (the director, 2026-11-12).

## The figure referee read and check A (2026-11-12)

**The record:** `secondary-results/referee-figure-deformation-20261112/`. At Joseph's request the director ran a figure
referee read of fig:deformation (gpt-6.1-sol, high). Check A tested the referee's point from the records
(`check-a/a_recovery.py`). For each truth and supported (E_avail, W) cell with |i| > 2 %, the recovered fraction is
f = [(1+r)(1+i) − (1+r₀)]/i, net of the nominal closure.
- In EW29 (E_avail 0.8–1.5 GeV, W ≥ 3 GeV) the unfolded cell moves opposite to the change for GiBUU, W1 and W3.
- Over the supported cells, the median f is 56–88 % (GiBUU 63 %). The numbers of opposite cells are 12/39 (GiBUU),
  10/33 (W1), 0/26 (W2) and 8/35 (W3).
- σ_f is at most 0.04. Seven cells lie within 3σ of a class boundary, so the "signs robust" statement is made with that
  count, not as a blanket.
- All of these are keys rec-* (READOUTS recov).

**The sweep, by claim:** every sentence that says or implies that the unfolding partly recovers a shape change.

| site | the claim | disposition (after the PRD and meaning reads of recov-read/) |
|---|---|---|
| paper §5.1 para 1 (:265) | "recovers only part of a change …" | rewritten: "the median unfolded (E_avail, W) cell moves by 56–88 % of the injected change, but individual cells range from moving opposite to it to overshooting it". GiBUU: median 63 %, with 12 of 39 opposite and 10 overshooting (cells with \|i\| > 2 %). EW29: −30 % injected, unfolded +21 % above nominal (residual 74 %). "Several percent in the largest cells" cut (B7) |
| paper §5.1 para 2 (:268) | the withheld shapes' residuals | now over the most affected SUPPORTED cell, 9–31 %. The old 16 % was W2's unsupported EW37 (keys rec-w-supmax-*; check_sec4_receipts recomputes the range from the assess receipt and the support rule). Plus median 56–88 %, 0 to 10 opposite and 1 to 9 overshooting |
| Table 2, the generator-sized row and its status word (:175, :191) | "Partial: the truth change is recovered only in part" | "Mixed per cell: the median unfolded cell moves by less than the full truth change, and individual cells range from moving opposite to it to overshooting it". The row gives the supported-cell maximum and the median range |
| paper §5.4, the first finding (:330) | "the residual … an exact binned unfolding … leaves a similar residual there" | the median framing. The IBU comparison now names its population (the joint cells), the exact response matrix and five iterations (S7 :588), so "residual" has a referent |
| paper §7.1, the limitation "Estimator bias" (:511) | "retains part of its prior" | scoped to the four changes of fig:deformation: median 56–88 %, up to 12 of 39 supported cells with \|i\| > 2 % opposite. "Retains part of its prior" is kept, as the sixteen-cell ρ result |
| introduction (:20) | "retains part of its prior" | qualified, per the PRD read: "on the sixteen reporting cells, while individual (E_avail, W) cells can move opposite to a generator-sized change or overshoot it" |
| abstract (main_paper.tex:62) | "In controlled studies the result retains part of its prior" | NOT changed. The PRD read asks for the same qualifier, which would take the abstract from 244 words past its 250-word limit. Sent to the director to rule |
| Supplement S4 :340 | "the estimator does not follow generator-sized E_avail shape changes" (the earlier variants) | "does not fully follow … (for the reported estimator, Sec. supp:recovery)" |
| Supplement S4, supp:recovery and tab:recovery (new) | the definitions | f with its numerator stated explicitly, the 2 % threshold and why, supported cells, σ_f ≤ 0.04 including r₀, and the near-boundary cells split into near f = 0 (which bounds the opposite count) and near f = 1 |
| Supplement S7 :588, :590 | the IBU comparison's median residuals on the joint cells | kept: they are the referent now named at :330, a different population from tab:recovery |
| fig:deformation caption | descriptive | revised under item B; no recovery claim |
| Supplement fig:supp-lowcap caption and its paragraph (:266-278) | descriptive | kept |
| §5.4 heading and the ρ study (:324-354), §7's checklist (:487) | "retains part of its prior", ρ | kept: the sixteen-cell retained fraction ρ is a different, defined projection, and check A does not test it |
| paper §3.3 (:155) | "how well the unfolding recovers a specified deformation" | a definition of a closure test; kept |

## Housekeeping

- 2026-11-12: heads 800579be through 2a2af241 carried a values producer (make_values_fived16.py) that refused to run. The abstract edit had broken a LISTED_CLAIMS anchor (:247) and its self-test plant (:2438). The committed values_fived16.tex was correct throughout, so nothing printed wrong. Fixed in dba7628c; make_values --self-test is now part of the push gate, which the director approved as standing practice.

# G. The fresh referee read on 283f3044 (gpt-6.1-sol, 5/10), with the style-only round 1 (6/10)

**Reports:**
- `secondary-results/referee-methods-fresh-20261112/gpt.txt`. Its rows are G<major>.<sub>, G§4-<n>, Gm<n> and Gs<n>.
- `secondary-results/style-methods-20261112/round1/gpt.txt`, the style-only read. Its eight ranked changes are rows St1
  to St8, and its line-level fixes are Stp<n> (paper) and Sts<n> (Supplement).

Classes and rules are as at the top of this file. **Lane:** "paper" is director-helper-3 (paper_body.tex,
main_paper.tex, make_values). "Supp" is journal-editor (supplemental_body.tex prose, since the hand-off at 60d14439).

**The L numbers** are director-helper-2's `lrows-g/` (PR #1102, a0e504d0, not yet merged): cp_intervals.json
`73e25db3`, geant_share.json `4d93b3c9`, rounding_decomp.json `46c6f8f3`, reconcile.json `ecdb66a2`.

**The director's rulings of 2026-11-12, already given:**
- St1: the abstract is restructured as application, benchmark, findings, interpretation.
- St8: out of scope.
- St6: the terminology.
- St4: the §6.1 study-summary table, if it replaces prose.
- St7: Fig. 2's caption.
- D2: "no effect" becomes "no detected change".
- D3: "valid" becomes "passes this rule".

## Majors

| # | Request | Class | Source / inputs / cost | Proposed resolution | Lane | Misreading? |
|---|---|---|---|---|---|---|
| G1.1 | A compact specification of the two reported estimators, then a test-to-estimator map | T | Table 2 (paper); journal-editor's new S4 configuration table (tab:configs, step 2); Table S9's Estimator column | The paper's §3.1 opens with the common procedure and the two reported configurations, pointing to tab:configs for the full map (= Gs3) | paper + Supp | no |
| G1.2 | For the headline setting scans: the tested levels, ρ and total bias at each, and the noise thresholds | L (local) | FD-PRR's committed readout (the prr keys; tab:prr-rho holds IBU's). Levels per factor are keys prr-nlev-*. 0 node-h | A table in S8.2 of level, ρ, RMS bias and threshold per factor and truth, keyed through make_values | Supp (table), paper (keys) | no |
| G2.1 | Resolve the GEANT4 neutron and proton mismatch with matched single-band controls, or isolate it and quantify its effect on the reported covariance | L, the quantification (done); the mechanism study is **declined** (Joseph, 2026-11-12) | geant_share.json (`4d93b3c9`). Both bands' share of the reported covariance's diagonal: median 0.02 %, at most 0.21 % (R08). Removing both lowers the reported σ by a median 0.01 %, at most 0.11 %. Dropping them from the bias tests' χ² raises it by at most +0.57 (+1.8 % relative), and no graded truth's \|z\| > 2 cell list changes. The χ² is reproduced to 0.76 % on the graded truths, because only N_T's diagonal is committed. The channel split (#1081) is not used | **Joseph rules whether it prints.** If yes, one sentence in §6.2 and S8.4: "an unresolved implementation property, whose two bands contribute at most 0.21 % of any cell's variance in the reported covariance" | paper + Supp | no |
| G2.2 | Say what each side holds fixed: truth, reco sample, nominal simulation, background, normalization, resampling, configuration | T | S8.4 "What each side does" (F2.1, the director's record-true wording; GEANT-NP-REFEREE-MAP.md) | Partly in place. Add "the estimator configuration is (e) on both sides" and "both subtract the varied truth" if the referee map states it, else nothing | Supp | partly: S8.4 already lists the operations |
| G2.3 | "300 shared by the readings" (Table S10) against "300 in each variant" (§6.2): common random numbers, or identical pseudo-data? | T | LL5D-DECLARATION.md :170-172 (both readings consume identical random streams; the primary reading drops the two bands' universes from the composition), :254 (shared toy seeds), :550 (600 toys per truth, 300 per reading) | Table S10 row 10: "300 per tune in each reading, drawn with the same random streams". §6.2: "the primary reading leaves the two bands out of both its pseudo-data and its covariance". Both statements are true, so this is a wording fix | Supp (S10), paper (§6.2) | partly: both statements hold |
| G3.1 | For each final test: expected content, observed count, threshold, clipping qualification, and an interval on the observed fraction | L (done) + T | cp_intervals.json (`73e25db3`): joint 0/300 at both tunes, CP 95 % [0, 0.0122], against a null content of 0.692 (AR23) and 0.697 (G18). Flagged cells: AR23 29, 164/300 [0.488, 0.604]; AR23 56 and G18 29, 148/300 [0.435, 0.551]. The cells' null contents are 0.684 to 0.687 | Table 5 (or its caption) gains the null content and the CP interval for the joint fraction and the flagged cells, keyed. The weakened-by-clipping counts are already in S8.3 | paper (Table 5) | no |
| G3.2 | Controls: does the covariance describe the ensemble at nominal truth and group by group before the unfamiliar-truth term? | T | COV2D: "spread alone, against C_T without C_model" (OUTCOME-20261108 §3: median p̂ 0.673 and 0.653). The per-group draws reproduce within 10 % in σ (S8.4 :833, the first test's pre-check) | One sentence in §6.2 naming the spread-alone readout, and the per-group check where it exists | paper | partly: the readouts exist |
| G3.3 | Sensitivity of the conclusion to finite covariance estimation (eigensolver agreement is not precision) | A, unpriced; T meanwhile | — | T: one sentence in §7.1's calibration group saying finite-ensemble precision of C_T was not estimated <!-- absence-ok: proposes a scope sentence for an unpriced analysis; not a claim about the records --> For an A arm, the director prices it | paper | no |
| G3.4 | Read the pending result conditionally (five outcomes) | T, done | The ll5d variants (V-L1 to V-L3); F2.3's repaired/continued clause | Already implemented | — | yes: already implemented |
| G4 | A direct sensitivity study of the equal-weight regression for unreconstructed events | A | **RSN's WR and WU arms** | Limitation 8 stays until they run | RSN | no |
| G5 | C_model: robustness to gating, pooling, truncation and target, or consistently "recovery of these constructed deformations" | A + T | **RSN's G6, SM and TR arms** | T now: a sweep of the paper so every generator-derived truth reads as the specified construction, which the referee accepts as an alternative. The hydrogen clause already makes no model-agreement claim | RSN (A), paper (T) | no |
| G6 | ρ is not a mechanism or a ranking: lead with the full bias results, call ρ a directional summary, and use "no change detected" | T | Table 4 (tab:prr-rho) | §5.3 leads with Table 4's RMS bias and χ², then ρ as a directional summary. "Consistent with a share specific to the implementation" is softened to "the tested settings change this projection; the cause of the total residual is not established". "No effect" becomes "no detected change" (D2). LISTED_CLAIMS anchors in §5.3 must be checked first | paper | no |
| G7.1 | Present the reporting-cell and finer-grid stability results separately | T | §6.1 | St4's study-summary table (ruling 4) | paper | no |
| G7.2 | How much the statistical covariance changes with and without the jitter | L (diagonal done); L (pscratch) for the off-diagonals | rounding_decomp.json (`46c6f8f3`), under R0b's additivity: the jitter is a median 26.2 % (14.9–67.0 %) of each cell's bootstrap variance. Without it the bootstrap σ falls by a median 14.1 % (7.7–42.6 %), and the reported σ by a median 0.009 % (at most 0.048 %). Off-diagonals: I0 kept per-cell spreads only. Either a 0 node-h login read of the 20 data-jitter unfolds, if they survive on pscratch, or a bootstrap rerun without jitter (priced in lrows-g G3) | §3.2 gains the decomposition in one sentence (keys from rounding_decomp.json). **For the director:** the off-diagonal read | paper | no |
| G7.3 | Sensitivity to the perturbation prescription | T or A | The law is in §3.2 (F6.2) | T: name the law, and state that other prescriptions were not tested <!-- absence-ok: proposes a scope sentence; RS1-DECLARATION is the record to check before printing it --> after checking RS1-DECLARATION for any other scale | paper | no |
| G7.4 | A scientific assessment of the ensemble trade-off | T | ens1 keys (F6.3 already prints the two RMS values) | One sentence: the practical cost (an RMS bias difference of 0.0005, about 1 %) against the stability gain. Six decimals go to the Supplement (= Gm8) | paper | partly: the numbers are printed |
| G8.1 | A run-period figure of reconstructed and unfolded double ratios, with a consistent reference | L (local, 0 node-h; about 2–3 h) | lrows-g G4: all products are committed. Unfolded: period-unfold analysis.json (`05edff61`) and RE-2's partc-r2 periods analysis.json (`2ce5d5da`, the reported 2D configuration). Reco: work_proxy.npz on this branch (`42ce788b`) for the same P_A/P_B/P_C groups | **For the director:** a figures-lane producer, two panels (reco, unfolded) by p_∥ for P_B/P_A and P_C/P_A, on the RE-2 products, with the reference stated in the caption | figures | no |
| G8.2 | An account of the checks on exposure, selection, backgrounds, flux and response | T | The note's period records (S5 carries the block); period-unfold REPORT.md | A short S5 paragraph listing what was checked and what remains unknown, each with its record | Supp | no |
| G8.3 | Deposit the release; products to reproduce the headline diagnostics | X | — | Joseph's | Joseph | no |
<!-- absence-ok: G rows' "not estimated", "not tested" and "until they run" scope proposed sentences and pending arms; each names the record to check first -->

## The report's §4 rows marked (a)

| Row | Class | Resolution |
|---|---|---|
| (a) The neutron and proton band mismatch | = G2.1 | L done; Joseph rules on printing; the mechanism study is declined |
| (a) The equal-weight regression | = G4 | A: RSN's WR and WU |
| (a) The 2D universes' approximate weighting of misses | A | **COV2D-G2R** |
| (a) The undeposited release and access to the evidence | X (= G8.3) | Joseph's; the T part is G1.2, G3.1 and G8.1 |

## Minors

| # | Request | Class | Resolution | Lane |
|---|---|---|---|---|
| Gm1 | Reduce repeated qualification | T | The style pass (= St3): each limitation stated in full once, at its inference, with pointers elsewhere, plus the abstract and §7 | paper + Supp |
| Gm2 | "Valid" → "passes this rule" | T (D3) | Paper: already "pass" (Table 2 :180, §5.4 :322); only the keys' names say valid. **#981's Q19 ("Fourteen cells are valid under it; R02 and R06 fail") is a protected quote:** journal-editor has taken it to the director | paper + Supp |
| Gm3 | "No detected change" for a thresholded non-detection | T (D2) | The keys keep their names. The printed class label changes in make_values (mine), and the paper's Table 4 and §5.3 in the same commit. journal-editor matches S8.2 and Table S10 | paper + Supp |
| Gm4 | §5.3's "Its root-mean-square bias": name IBU | T | Name IBU | paper |
| Gm5 | "No learner setting was tuned on data" against the data-informed choices: explain once | T | One sentence where §4.1 qualifies the benchmark (= Gs3's move) | paper |
| Gm6 | Reconcile 6.94 ± 0.41 % with 6.89 ± 0.46 %, and 9 % with 16 % | T | reconcile.json (`ecdb66a2`): the paper's :233 prints the pre-RE-2 period unfold (period-unfold analysis.json); the Supplement's :500 prints RE-2's refined regeneration (partc-r2, the reported 2D configuration), as the note does. **The paper switches to +(6.89 ± 0.46) %**, keyed, with that record. 9–31 % is over supported cells (rec-w-supmax) and 16–31 % over all cells (s5e-shapes-ewmax; W2's 16.4 % is the unsupported EW37). Table S10 row 2 names its population ("over all cells") | paper + Supp |
| Gm7 | Configuration ambiguities in S4 | T | journal-editor's step 2 (S4 restructure) | Supp |
| Gm8 | False precision: six decimals in the narrative | T | §6.1 prints the practical difference. The exact values stay in S8. Rounded keys come from make_values from the same readout, and **the director rules on adding them** | paper |
| Gm9 | "Usage-recommendation rule" and status labels | T | = St5 | paper + Supp |
| Gm10 | Fig. 4's pointer to Fig. S3; Fig. 2 as small multiples | T | Fig. 4's caption (:395) cites Fig. S3 for the support rule. The pass checks where the rule is defined (the referee reads S3 as the prior-sensitivity figure) and points there. Small multiples is a figure redesign: **for the director** (the figures lane; fig:deformation's producer) | paper / figures |

## Structure

| # | Request | Class | Resolution / conflict | Lane |
|---|---|---|---|---|
| Gs1 | The introduction states the final implementation's status before listing the tests; the abstract leads with the three findings | T | Intro paragraph order; the abstract = St1 | paper |
| Gs2 | §2: the sixteen cells in one bounded subsection; the "fine grid is the analysis binning" paragraph moves to test design or the Supplement | T | The paragraph moves to §3.3 (test design), with a one-line pointer in §2 | paper |
| Gs3 | §3.1: the final estimator first; the data-informed-choices paragraph moves to §4.1 | T, **conflict** | The recheck round (Fs2a) settled a compromise: one disclosure sentence in §3.1. This round asks for the full move. Proposed: move it to §4.1's opening and keep a half-sentence pointer in §3.1. For the director | paper |
| Gs4 | §3.2: lead with a covariance map; move the run-period size interval and construction details to S5; the empirical run-period evidence to §4.3 | T | A compact list or table of the blocks, each with its physical meaning and omissions. The 0.73–2.56 interval to S5 (a Supplement merge with journal-editor) | paper + Supp |
| Gs5 | §5: observation before interpretation; consolidate the screening-rule paragraph; §5.3's classification machinery to S8.2; merge the GiBUU and q3 paragraphs; lead with Table 4 | T | As G6. The LISTED_CLAIMS anchors in §5.2 and §5.3 are checked before any merge | paper + Supp |
| Gs6 | §6.1: reproducibility, then the sixteen-cell scale, then the finer-grid failure, then covariance treatment, mechanism and mitigation. Delete the "next sentences concern" scaffolding; split the mechanism paragraph | T, **protected** | **RS1's paragraph (the mechanism study) is a protected span** (check_restyle), so it cannot be split. Proposed: keep it verbatim and move the scope and candidate-cause material around it into separate short paragraphs. The B0 sentences keep their "quoted above" order. For the director | paper |
| Gs7 | §6.2: the common definition, then the 2D result, then the final five-observable design and outcome; the staged chronology to S8.4; split "These are conditional tests" | T | Reorder and split; the chronology already moved in F | paper + Supp |
| Gs8 | §7 and §7.1 overlap; the hadronic-origin proposal shrinks to one sentence; general checks separated from implementation-specific criteria | T | Regroup | paper |
| Gs9 | Rebalance: the scan settings (G1.2), run-period evidence (G8) and controls in; superseded configurations out of S4; combine S7's repeated paragraphs; the unused prior-spread rule out of S10; consider moving S17 and the correlation-perturbation studies | T | journal-editor (steps 1–2 under way). The prior-spread rule is Q09-adjacent (#981), so journal-editor has it with the director | Supp |
| Gs10 | Placement at first use: Table 1 in §2, Fig. 1 in §4.1, Fig. 2 in §5.1, Fig. 3 with Table 3 in §5.2, Table 4 in §5.3, Table 5 in §6.2; Fig. S2 in S6; Fig. S4 in S9 | T (layout) | Float positions in the source, checked in the PDF. Fig. S2 has moved within S6 (journal-editor's step 1) | paper + Supp |

## The style-only round 1 (6/10)

| # | Change | Class | Resolution | Lane |
|---|---|---|---|---|
| St1 | The abstract: application → benchmark → findings → interpretation | T (ruled) | Restructured on its example. The pending-test clause stays the variant group, at most 250 words in every case. The abstract read comes first | paper |
| St2 | The final method separate from its history (§§3.1, 6.1–6.2; S4, S8.4) | T | = Gs3, Gs6, Gs7 in the paper; journal-editor's S4 and S8.4 | paper + Supp |
| St3 | Consolidate qualifications | T | = Gm1 | paper + Supp |
| St4 | One function per paragraph; tables carry inventories (§§3.2, 5.2, 6.1–6.2, 7) | T (ruled) | §5.2's three-covariance walk-through goes to its example's three sentences, with Table 3 carrying the rest. §6.1's study-summary table replaces the population and ensemble prose | paper |
| St5 | Direct descriptions in place of labels; define ρ before its first use; trim Table 2's status key | T | Labels such as "increases" become statements ("Lower capacity raises the retained fraction"), keeping the class keys. Table 2's key lists only the statuses the rows use (St8's pending statuses stay while LL5D is pending) | paper |
| St6 | Terminology and notation | T (ruled) | "Diagonal fraction" everywhere (S3's "reconstruction stability" is journal-editor's). The recovered fraction becomes ψ, agreed with journal-editor; the paper names it in words. C_model is marked fractional or dimensional. "Withheld shapes" and "held-out tunes" are each defined once (§3.3) | paper + Supp |
| St7 | Shorter captions; S7's duplicate | T (ruled) | Fig. 2: the derivation moves to supp:recovery, leaving one clause (a Supplement insertion, coordinated with journal-editor). S7's duplicate is journal-editor's | paper + Supp |
| St8 | [PENDING] placeholders | out of scope (ruled) | They resolve with LL5D's fill | — |
| Stp1–Stp8 | The eight paper line fixes: §3.1 universe sentence; §4.2 "Two comparisons compare"; §4.2's iteration-scan sentence (the scan to the Supplement); §5.2's fragment; §5.3 IBU (= Gm4); §5.3 GiBUU/q3 merge (= Gs5); §6.1 scaffolding (= Gs6); Fig. 4's S3 pointer (= Gm10) | T | Each in the sentence pass | paper |
| Sts1–Sts8 | The Supplement line fixes | T | journal-editor's | Supp |

## For the director before the text pass

1. **The L prices:**
   - G7.2's off-diagonal read (0 node-h login, if the J products survive);
   - G8.1's figure (local, figures lane, about 2–3 h);
   - G3.3, unpriced.
2. **G2.1:** whether the GEANT quantification prints. That is Joseph's call, so the sentence is held.
3. **Moves that cut or conflict:**
   - Gs3, the full move of the data-informed-choices paragraph against Fs2a's compromise;
   - Gs6, RS1's protected paragraph;
   - Gm6, the paper's period step switching from 6.94 ± 0.41 to RE-2's 6.89 ± 0.46;
   - Gm8, rounded ensemble keys;
   - Gm10, Fig. 2 as small multiples.
4. **The order:** structure moves first (Gs1–Gs8, Gs10, St4, St5, G6), then the abstract (St1) with its read, then the sentence pass.

## The #981 re-pin list from the Supplement style pass (journal-editor, 2026-11-12)

The director's rulings of 2026-11-12. #981 is not edited now; its re-pin runs once, after #977 merges.

- **Q19**, "Fourteen cells are valid under it; R02 and R06 fail", is re-sourced to "Fourteen cells pass it; R02 and R06
  fail" (D3: "valid" -> "passes this rule"). build_package.py:440-443 at 91f9cb615 checks the printed sentence
  "… cells are valid under it", so that check follows.
- **Q09**, "The second rule is ours, not taken from Ref.~\cite{ATLAS:2024jets}", is gone from the Supplement (D4: the
  prior-spread rule's definition moves to the note, sec:fived16-fd; one sentence keeps the withholding and its reason).
  DECISION-20261110-joseph-vprior-withhold.md item 2 has #981 drop its V-PRIOR rows; it does not name Q09, so D4 is
  the reason recorded here.
- **Broken before this pass:** Q11, Q12, Q13, Q20, Q21 and Q22 count 0 at 60d144395, from earlier #977 edits
  (4580caf5, 716ce04c, 10b88ad9). The re-pin re-sources them.
supp-quotes.tsv records Q09 and Q19 in comments beside their rows.

## G rulings and the paper's structure batch (director-helper-3, 2026-11-12)

**The director's rulings on section G:**
- **Gs3:** the data-informed-choices paragraph moves whole to §4.1, with a pointer sentence left in §3.1. This
  supersedes Fs2a's compromise.
- **Gs6:** RS1's protected paragraph stays verbatim.
- **Gm8:** rounded ensemble keys, asserted against the exact values.
- **Gm10:** Fig. 2 as small multiples, a producer-only change.
- **G7.2:** diagonal only; helper-2's jitter-free bootstrap check found 2 of 100 replicas, so there is no correlation
  change to print.
- **G3.3:** a scope sentence in §7.1, with the unpriced analysis on the follow-up list.
- **G4/Gm6:** one reference, 1A–1F, at both levels.

**The run-period reference, recorded.** Before this batch the paper printed two numbers against different references:
- the reconstruction-level step as +6.10 % for 1G–1M against **1A–1E**, the reconstruction-level reference of
  playlist-spread-20261014 (ref_shape.json);
- the unfolded step as +(6.94 ± 0.41) %, the purity-background period unfold against 1A–1F, before RE-2.

The text had to explain the mismatch ("the unfolding's reference group includes 1F, whereas the reconstruction-level
reference does not"). The referee asked for a consistent reference (major 8), and the figure (lrows-g/g4-runperiod, PR
#1104) draws both levels against 1A–1F. That matches the three groups the run-period block is built from. So the paper
now prints keys rp-*: +5.99 % (reco) and +(6.89 ± 0.46) % (unfolded, RE-2's refined background, the reported 2D
configuration) for 1G–1M, and +1.26 % and +(1.85 ± 0.64) % for 1N–1P. The 1F caveat sentence is gone. The figure's
producer asserts that it reproduces the old 6.10 % against 1A–1E.

**Status of the paper rows** (paper_body.tex and main_paper.tex, at the next push):

| Rows | Status |
|---|---|
| Gs1 | done: the implementation's scope paragraph precedes the three findings |
| Gs2 | done: the fine-grid paragraph moved to §3.3, with a pointer in §2 |
| Gs3, Gm5, Stp1 | done, as ruled. §4.1 opens with the fixed learner settings and the two data-informed choices. §3.1's universe sentence rewritten. The registry's ALIASES row 39 and ATTRIBUTION row 17 re-cited by hand to the changed line |
| Gs4 | done: §3.2's first paragraph split by block; the run-period interval paragraph moved to S5, which already states it, leaving a pointer |
| G7.2 | done: the diagonal jitter share (keys rdec-*, READOUTS rdecomp 46c6f8f3), "diagonal elements only" |
| Gs5, G6, Gm4, D2 | done. §5.3 leads with table 4's RMS bias and χ², with IBU named. ρ is a directional summary. The class machinery is cut to what the results use. "No detected change" in the text, table 2 and make_values' WORDS (the printed class label; key names kept). Table 4 moved to its first use |
| Stp4 | done: the screening-rule fragment |
| St4 (§5.2) | partial: the repeated "the bias is the same" remark is cut. The rest of that paragraph holds the four LISTED_CLAIMS anchors and stays |
| Gs6, St4 (§6.1) | done. The scaffolding sentence is cut, so the B0 sentences open their paragraph verbatim. A one-sentence reproducibility/stability distinction opens §6.1. tab:stability lists the populations and ensembles in place of their prose |
| Gm8, G7.4 | done: keys ens1-g-rms-r, ens1-g-rmsc-r, ens1-g-rms-dpct, plus a sentence that the decision follows the criterion and does not weigh gain against bias |
| Gs7, G2.3, G3.1 | done. §6.2's conditional-test paragraph stands alone. The variants share their random draws, and the primary variant leaves the two bands out of its pseudo-data and covariance alike (LL5D-DECLARATION.md :170-172, :254, :550). Table 5 gains the joint fraction's 95 % Clopper–Pearson interval, and the flagged cells' intervals are in the text (keys cp-*, READOUTS cpint 73e25db3) |
| Gs8, G3.3 | done: the hadronic-origin proposal in two sentences plus the ONCE sentence; the checks' scope; the finite-ensemble scope sentence |
| St5 | done: table 2's key prints the Invalid, Stopped and LL5D-descriptive entries only when the second coverage test's status uses them |
| St6 | done: "the withheld shapes" defined in §3.3 |
| St7, Gm10 | done. Fig. 3 (formerly 2) is small multiples, with arrays asserted unchanged against presentation_original_arrays.json and the lower-capacity figure byte-identical. Its caption is shortened; the derivation is in supp:recovery (journal-editor, 20e4baab). Fig. 4's support-rule pointer now goes to section 2 |
| G8.1 | done: fig:runperiod in §4.3, installed byte-identical to PR #1104's PDF (asserted in make_values) |
| St1 | done, after its PRD and meaning reads (absread4, verdict MINOR, all four defects fixed). No rendered case has a semicolon. Worst words per sentence 33.0 → 20.2. The live cases run 195–249 words |
| Gs10 | Fig. 1 moved into §4.1, Table 4 to its first use; the other floats checked in the PDF |
| G2.1 | held for Joseph |
| Stp3 | in the sentence pass |

### S9.2's correlation-sensitivity details, no longer printed (journal-editor, 2026-11-12, 74c75cbef)

The director's approval of referee6 6b.9: the Supplement keeps the flux-correlation fall for the three GENIE predictions
(sens-alpha-pct, sens-b5-flux-fall-lo/-hi) and points to the note's sec:fived16-gen, which prints its own version over its
pre-B5 predictions (sens-*, fb-*, tab:fived16-sens). No document now prints the Supplement's GENIE-only values of
sens-b5-detlat-fall-max, sens-b5-joint-chi2-min, fb-plo, fb-phi, fb-b5-edge-max and fb-b5-offset-relmax. The keys stay in
docs/analysis-note/values_fived16.tex (make_values_fived16.py, the b5 sensitivity block), with their -nopl variants.
Table S17 (tab:cmodel16) stays: #981's Q06 and tab-cmodel16.csv anchor it.
