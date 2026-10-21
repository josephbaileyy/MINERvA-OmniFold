# r13 triage of the r12 rater flags

**Inputs.**
- P3 lists: `xmodel/r12/runs/P3__r12__sol__r1.md` (35 flags) and `P3__r12__sol__r2.md` (46 flags).
- `P3__r12__gemini__r1.md` is empty (0 bytes), so it is not used.
- P1 quotes: sol r1–r3 and Gemini r1–r3.

Below, the union of the two sol lists has one row per distinct sentence. "r1/r2" says which run flagged it, with its tag.

**Classes.**
- **(a)** The material moves to the note, where it already prints. The paper points to it there.
- **(b)** The material stays, restated once as a design fact or a scope statement beside its claim.
- **(c)** A false alarm: the sentence is standard PRD register and is left as it is.
- **(P)** The sentence is protected (rule 4, Data availability). It is not edited; see `DA-proposal.md`.

**After the independent review (`REVIEW.md`, ADOPT-AFTER-FIXES).** These rows were revised; the final wording is in `paper_body.tex`:
- #10: the scoped rule was restored in the paper (SHOULD-FIX 2): "Configuration (e) keeps five iterations under a rule fixed before the comparison, because 10, 15, or 20 did not reduce the rule's measure of model dependence, the largest residual proxy over the development truth changes (Ref. [14], Sec. 9.4)." The note's unscoped §9.4 sentence is left for the note pass, as the director instructed.
- #16 and #17: "The first, whose test was specified in advance, undercovered …" and "A post hoc rescoring of the same pseudo-experiments against the second, rebuilt band removes the tail undercoverage: …" (SHOULD-FIX 3). The SEC4 phrases are unchanged.
- #38: "These target-corrected evaluations are descriptive and do not re-grade the decisions of Table IV, which concern each prediction on the target it was generated for and stand (Ref. [14], Sec. 10.9)." This matches `sec_joint.tex:703–704` (SHOULD-FIX 1); "as generated" was dropped.
- #6: "an effect whose materiality is not established because it has not been assessed against the covariance" (NIT 1). Nothing now moves for this row.
- #9: the §3.2 pointer now sits on "the central-value estimator" (NIT 2).
- #33: "permits this" is now "is unaffected by this" (NIT 3).
- #26: "the same estimator's envelope alone does not exceed it" (NIT 4).
- The step-5 VII B sentence: "Three properties are distinct." (NIT 5).
- #3: "The three- to five-observable outputs are central values …; their intervals have no validated coverage, and the paper does not deliver …" (NIT 6).

**Priority passages.** Sol quoted these in P1, and they were fixed first:
- the design-review and budget sentence (#33; all three sol runs and all three Gemini runs);
- the rebuilt-band paragraph (#16–#19; sol r2 and all three Gemini runs);
- the hydrocarbon sentence (#38; sol r1 and r3).

Gemini's 135 MeV rewrites (r1, r2) claim the effect is "well below the experimental uncertainties" or "negligible compared to the total experimental uncertainties". Both are rejected: the paper and the note (§7.1) say the effect has not been assessed against the covariance.

## Sec. I

| # | flagged sentence (r12) | flags | class | r13 action |
|---|---|---|---|---|
| 1 | "Two requirements are kept apart." | r1 jargon; r2 internal-record | b | Now "Two properties must be distinguished." The calibration definition is split into two sentences. |
| 2 | "Sections IV–VI ask whether …; these validation studies are the paper's main results, and Table I lists them with …" | r1 internal-record; r2 bookkeeping | b | Split: "Sections IV–VI test whether … These validation studies are the paper's main results; Table I lists each with its configuration, test, and principal limitation." |
| 3 | "The paper does not deliver a validated five-observable cross-section measurement: the three- to five-observable central values are outputs …, and their intervals have no validated coverage." | r1, r2 hedging | b (guardrail) | Restated as one scope sentence that leads with what the results are: "The three- to five-observable results are central values, outputs of … ; their intervals have no validated coverage, so the paper does not deliver a validated five-observable cross-section measurement." Rule 2's example keeps "no validated coverage". |
| 4 | "The companion analysis note [14] gives the full validation record, … and is cited below by section." | r2 internal-record | c | Unchanged. A companion-paper pointer is standard. |

## Sec. II

| # | flagged sentence | flags | class | r13 action |
|---|---|---|---|---|
| 5 | "The files analysed are an earlier production of that release (see Data availability)." | r2 dev-history | b | Merged into the first sentence of Sec. II: "… from an earlier production of the MINERvA open-data release … (see Data availability)." |
| 6 | "Relative to the charged-pion mass, in a simulated sample it moves 0.67 % …; its materiality has not been established, because it has not been assessed against the covariance (Ref. [14], Sec. 7.1)." | r1 jargon; r2 internal-record | a + b | The clause "its materiality has not been established" moves to note §7.1, where it prints ("Its materiality is not established"). The limitation and its pointer stay, as the r12 review B4 requires: "…, a shift that has not been assessed against the covariance (Ref. [14], Sec. 7.1)." |

## Sec. III

| # | flagged sentence | flags | class | r13 action |
|---|---|---|---|---|
| 7 | "Each classifier is trained on the full sample …, with no held-out or cross-fitted split, no early stopping, and no class balancing, and no effective sample size of the unfolded ensemble is computed" | r1 internal-record | a + b | One design sentence: "… without a held-out or cross-fitted split, early stopping, or class balancing (training details: Ref. [14], Sec. 3.1)." The effective-sample-size clause moves to §3.1, which prints it verbatim. |
| 8 | "No hyperparameter search was performed on data: the nominal settings are scikit-learn defaults, …" | r1, r2 dev-history | b | The design fact now comes first, and the no-search clause follows it. |
| 9 | "The two- to five-observable central values use configuration (a) …, and were not recomputed with the refinement (Ref. [14], Sec. 3.2); the two-dimensional one is …" | r1, r2 dev-history | a + b | Split into two sentences. "Were not recomputed with the refinement" moves to §3.2, which prints "they were not regenerated". The pointer stays. The paper says what the central values are: configuration (a), with the purity-based subtraction. |
| 10 | "It keeps five iterations under a rule fixed before the comparison, because 10, 15, or 20 did not reduce the rule's measure of model dependence, …" | r1, r2 dev-history | a | Moved to §9.4, which prints the rule and its measure. The paper now reads "the rule that set its five iterations is given in Ref. [14], Sec. 9.4". The paper no longer states the outcome, so the r12 B2 defect (an unscoped "did not reduce its model dependence") cannot recur. |
| 11 | "Ref. [14], Sec. 3.2 gives the full matrix." (Table II caption) | r2 bookkeeping | c | Unchanged. |

## Sec. IV

| # | flagged sentence | flags | class | r13 action |
|---|---|---|---|---|
| 12 | "The distance depends on the learner: ten LightGBM training seeds give 2.64–2.75, …" | r2 dev-history | c | Unchanged. It reports a measured dependence. |
| 13 | "We quote the LightGBM result as the central value, so that …; this learner was chosen after both comparisons were known, so the benchmark is a reproduction …" | r1, r2 dev-history | b (guardrail) | Split into two sentences. The disclosure stays, because Table I lists it as the row's principal limitation and "end-to-end test" would otherwise read as an independent validation. |
| 14 | "The systematic-universe unfoldings approximate …; we do not correct this approximation, and tests in two of the 187 universes cannot exclude a small effect" | r2 hedging | b | Now "… cannot exclude a small effect of this uncorrected approximation". |
| 15 | "Neither this block nor the total has had a coverage test." | r2 internal-record | b (guardrail) | Now "The coverage of this block, and of the total, has not been tested." Without it, the rescoring reads as a coverage result for the quoted block. |
| 16 | "In 100 closure pseudo-experiments at a fixed truth, an earlier version of the statistical band undercovered …, against 95.4 % nominal." | r1, r2 dev-history | b (SEC4 gate) | Restructured: "Two earlier versions of the statistical band, distinct from the quoted block, were scored on 100 closure pseudo-experiments at a fixed truth (Ref. [14], Sec. 5.2). The first undercovered in its tails: …". The gate phrase "against \SI{95.4}{\percent} nominal" is kept. |
| 17 | "Rescoring the same pseudo-experiments against the rebuilt band removes the tail undercoverage: 97.7 % … 78.1 % within one." | r1, r2 dev-history | b (SEC4 gate) | Kept verbatim, because the gate requires the phrase. |
| 18 | "Because the simulated part of the rebuilt band reuses …, this rescoring is not an independent coverage test" | r1, r2 dev-history | b (guardrail) | Reordered so the claim leads: "This rescoring is not an independent coverage test, because …". |
| 19 | "The rebuilt band is not the quoted block, which is a separate 300-replica ensemble; neither has been tested on independent pseudo-experiments." | r1 bookkeeping; r2 dev-history | b + collapse | The guardrail half (r12 B3) now prints before the history, as "distinct from the quoted block". "Neither has been tested on independent pseudo-experiments" is collapsed into #15 and #18: the quoted block is untested, and the rebuilt band's only score is the non-independent rescoring. Note §4.2 and §5.2 print both. |
| 20 | "The two-dimensional central value is therefore reproducible …, but its intervals, bias, and covariance have not been independently validated: we make no claim about coverage, …" | r1, r2 hedging | b (guardrail) | Split into two sentences: "… is therefore reproducible, and its covariance is built with the same estimator. Its intervals, bias, and covariance have not been independently validated: we claim no coverage, …". The next sentence is positive: "The covariance omits …, and it assumes …". |

## Sec. V

| # | flagged sentence | flags | class | r13 action |
|---|---|---|---|---|
| 21 | "The covariance of the five-observable central value … does not meet the validation criteria of its specification" | r1, r2 internal-record | c | Unchanged. It states a result. |
| 22 | "We use it, and no other five-observable covariance, for the comparisons of Sec. V B; it is separate from the calibration of the joint tests" | r1, r2 bookkeeping | b | Now "The comparisons of Sec. V B use this covariance and no other five-observable covariance; the calibration of the joint tests (Sec. VII) does not use it." "Only" was rejected, because it would change the claim. |
| 23 | "No frequentist coverage is therefore claimed for the five-observable intervals." | r2 hedging | b (guardrail) | Merged with the next sentence: "The five-observable intervals therefore have no validated frequentist coverage, and agreement …". Rule 2's example applies. |
| 24 | "A diagnosis of the stored pseudo-experiments attributes the miscoverage to a residual bias, growing with W, that …: the rate change itself is recovered, and the intervals are not, apart from a minor effect, too narrow." | r1 internal-record | b | Split into two direct sentences. "Inferred … rather than measured directly" stays as a guardrail, because "attributes" is an inference. |
| 25 | "A dedicated study searched for a definition whose total uncertainties meet such targets." | r2 internal-record | b | Merged into the headline: "Under the specified envelope prescription, none of the reporting definitions … tested in a dedicated study meets our 10 % precision target." |
| 26 | "With the joint-test estimator, the envelope alone exceeds the target, a 10 % median half-width …; for a coarser, non-nested partition … it does not, but …" | r1 jargon | b | Three sentences: the target, the two definitions it fails, and the 27-cell case. |
| 27 | Table III caption: "The counts in the text also pool a GENIE + MEC/GENIE CV ratio …, whose boosted-tree comparator includes background; the counts are unchanged without it." | r2 bookkeeping | b (guardrail) | Now "… pool a fifth change, a GENIE + MEC/GENIE CV ratio in (Eavail, W) whose boosted-tree comparator includes background; they are unchanged without it." Without the background clause, the caption's "signal-only" would be false as read of the pooled counts. |
| 30 | Fig. 3 caption: "Panel (a) uses the random seeds of the estimator's development studies; panel (b) uses separate assessment seeds, which also entered its later development." | r1, r2 dev-history | b (kept unchanged) | Kept. Without it, "three shape changes not used while it was chosen" reads as a fully held-out test. The seed disclosure does not print in the note, so it cannot move under rule 1. See the writer's reply, unsure item 1. |
| 31 | Fig. 4 caption: "The third truth … is not shown: its reweighting does not implement the intended change, and the test's verdict does not depend on it." | r1, r2 internal-record | b | Now "… is omitted because its reweighting does not implement the intended change; the test's verdict does not depend on it." It stays because the Bonferroni factor in the same caption counts three truths, and the note does not print the reason. |

## Sec. VI

| # | flagged sentence | flags | class | r13 action |
|---|---|---|---|---|
| 28 | "The miscoverage of Sec. V C is also attributed to a residual bias, inferred from the stored pseudo-experiments and not removed by the nominal-truth correction; whether it has the same origin is not established." | r1 internal-record | b + collapse | Now "… is also attributed to a residual bias, but whether that bias has the same origin is not established." The inference and correction clauses repeat Sec. V C (#24) and were collapsed there. |
| 29 | "On the same 109 joint cells and the fixed truth changes used to develop the estimator, an exact binned iterative unfolding …" | r1, r2 dev-history | c | Unchanged. The development-truth population is the diagnostic's scope. |

## Sec. VII

| # | flagged sentence | flags | class | r13 action |
|---|---|---|---|---|
| 32 | "The point estimates (k+1)/(B+1) carry no separate validity claim." | r2 hedging | c (guardrail) | Unchanged. The familywise-error statement concerns the decision rule. Without this sentence, a reader would take the printed p values as calibrated. |
| 33 | "The test design was fixed before any observed statistic was computed; its reviewers had seen …, and a bounded extension … was decided with observed p values visible, which the result above covers, since it holds for any stopping rule" | r1, r2 dev-history; all P1 runs | b (priority) | Now "The test design was fixed before any observed statistic was computed, although its reviewers had already seen descriptive per-cell residuals of the data. The calibration's computing budget was later extended by a bounded amount with observed p values visible; the error control above permits this, because it holds for any stopping rule (Ref. [14], Sec. 10.3)." Every fact is kept. |
| 34 | "Computing time limits interrupted or prevented 224 calibration and 53 power pseudo-experiments; when rerun, …" | r1, r2 bookkeeping | b | Now "The pseudo-experiments that computing time limits interrupted or prevented (224 for calibration, 53 for power) were rerun; none reaches …". The counts and the no-assignment clause are kept. Assumption A2 (independent exceedances) makes the losses relevant to the stated error control, so the sentence was not moved. |
| 35 | "Independently written code reproduces every p value and decision." | r1, r2 bookkeeping | c | Unchanged. It is a standard verification statement, and Sec. VII D refers back to it ("The independent recomputation verifies …"). |
| 36 | "The decisions test the hybrid null and hold under six conditions on the nuisance model, numbered as in …" | r1, r2 bookkeeping | b | Now "The decisions concern the hybrid nulls and rest on six conditions …". |
| 37 | "This matters for the rejections: the calibrated tests restricted to the matched (pT, p∥) projection … (p = 0.48 in total, 0.63 in shape; a post hoc observation) …" | r2 dev-history | b (guardrail) | Now "The omission matters for the rejections: restricted to the matched … projection (Sec. VII E), the calibrated tests do not reject GENIE 2.12.10 CV (p = 0.48 in total and 0.63 in shape, a post hoc observation), …". The post hoc label stays, as the r12 review S1 requires. |
| 38 | "These corrected evaluations are descriptive and do not re-grade the recorded decisions of Table IV (Ref. [14], Sec. 10.9)." (with the preceding hydrocarbon and GiBUU sentences) | r1 internal-record; P1 sol r1, r3 | b (priority) | Now "Correcting both predictions … moves both toward the data, and NuWro's total-test rejection does not survive that correction robustly; GiBUU's deep-inelastic events on hydrogen do not conserve energy, which affects its correction and possibly its carbon prediction. These target-corrected evaluations are descriptive; the decisions of Table IV are those of the predictions as generated (Ref. [14], Sec. 10.9)." This follows sol's rewrite. The GiBUU clause stays, as the r12 review S4 requires. |

## Sec. VIII

| # | flagged sentence | flags | class | r13 action |
|---|---|---|---|---|
| 39 | "Within the scope stated in Sec. I, the study's results are its validation findings, summarized in Table I." | r2 hedging | b | Now "The study's results are the validation findings summarized in Table I, within the scope stated in Sec. I." |
| 40 | "The higher-dimensional central values keep the purity-based subtraction and its bias of up to 4 % …" | r2 dev-history | b | "Keep" is now "use", and the bias is attached with "with". |

## Data availability (main_paper.tex, protected)

| # | flagged sentence | flags | class |
|---|---|---|---|
| 41 | "The input data and simulation are the MINERvA open-data AnaTuples, …" | r1, r2 internal-record | P |
| 42 | "A candidate release package of about 16 MB, described there and prepared locally but not yet deposited, …" | r1, r2 dev-history; P1 sol r2 | P |
| 43 | "With it a reader can recompute every p value, …" | r1, r2 bookkeeping; P1 sol r2 | P |
| 44 | "Rerunning the packaged files from an empty directory reproduces …" | r1 internal-record; r2 bookkeeping; P1 sol r1, r3 | P |
| 45 | "The package carries the exact-split two-dimensional curve; …" | r1 bookkeeping; r2 dev-history; P1 sol r1 | P |
| 46 | "Apart from the multiplier scan …, the other quoted numbers cannot be recomputed from this package." | r1, r2 bookkeeping | P |
| 47 | "That appendix states what each part of the release does and does not reproduce." | r1, r2 bookkeeping | P |

## Passages not flagged but revised under method step 5

These sentences have three or more joined clauses or exceed about 55 words. Each was split; none changes a fact.
- Sec. II, the external-prediction sentence: the W and neutrino-axis clauses are now two sentences.
- Sec. VII B, "Three requirements are distinct: …; …; …": now "Three questions are distinct." followed by three sentences.
- Sec. VII B, the source-half sentence: split at the semicolon.
- Sec. VII D (i): "… of the hypothesis definition. Convergence of the fine grid has not been shown: …".
- Sec. VII D (iv): two semicolons are now two sentences, and "measured for the mean only" sits beside "the resulting shift".
- Sec. VI, the D-ID scope sentence: the trailing "it does not bound …, and it does not address … or validate …" is now one scope sentence: "What unbinned information could recover, the coverage failure, and the validity of any interval lie outside its scope."
- Sec. VIII, the last sentence (68 words): now two sentences.

Left as they are:
- the Sec. VI checklist sentence ("closure with the backgrounds included; …"), whose semicolons separate list items;
- Table and figure captions, whose semicolons separate panel descriptions.
