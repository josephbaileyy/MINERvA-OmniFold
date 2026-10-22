# Register round r14: changed sentences (paper_body.tex only)

Base: origin/main 58fe8a61 (r13), copied to `paper_body.r13.tex` in this directory. Each entry gives the printed text
before and after (LaTeX macros as in the source) and the reason. The rule for the round: put the scope in the claim,
state each claim once, and replace stacks of "not", "no" and "neither" with a positive statement where the claim does
not change. Ledger rows touched are given in brackets.

## Sec. I

**C1. Scope, first sentence** [S1]
- Before: "The findings concern one OmniFold implementation on one data set and the observables, configurations, and deformations tested, not multidimensional OmniFold in general."
- After: "The findings concern one OmniFold implementation, applied to one data set with the observables, configurations, and deformations tested."
- Why: the scope is stated positively, and the trailing "not … in general" is dropped. "One implementation, one data set, the … tested" already excludes the general case.

**C2. Scope of the rejections** [S9, S11]
- Before: "The detector model has no calorimetric recoil-response uncertainty, and the rejections are not physical exclusions of the generators and provide no measurement uncertainty."
- After: "The rejections, made with a detector model that has no calorimetric recoil-response uncertainty, are statements about these hypotheses rather than physical exclusions of the generators, and provide no measurement uncertainty."
- Why: the detector-model limitation becomes the scope of the rejections, and "not physical exclusions" becomes what they are. The abstract still prints "are not physical exclusions"; it is unchanged.

## Sec. II

**C3. Data source** [D4]
- Before: "… from an earlier production of the MINERvA open-data release of pre-selected analysis ntuples (AnaTuples) [8] (see Data availability)."
- After: the same sentence without "(see Data availability)".
- Why: review E item 8 (bookkeeping pointer). "Earlier production" stays because without it the sentence would be false as read. Data availability prints the detail unchanged.

**C4. Selection held fixed** [D11]
- Before: "Event selection is held fixed as the classifier inputs and unfolded observables grow from (pT,p∥) to (pT,p∥,Eavail,q3,W); adding features does not add selected events or relax the signal definition."
- After: "The event selection and the signal definition are held fixed as the classifier inputs and unfolded observables grow from (pT,p∥) to (pT,p∥,Eavail,q3,W)."
- Why: the negative clause restated the first clause. Both facts (selection fixed, signal definition fixed) are now one positive statement.

**C5. Reconstructed-W redundancy** [D21]
- Before: "… so the five reconstructed inputs share information and do not, by themselves, provide five independent constraints: the result is five simultaneous observables, not five independent measurements."
- After: "… so the five reconstructed inputs share information: the result is five simultaneous observables rather than five independent measurements."
- Why: three ways of saying "not independent" became one.

## Sec. III

**C6. Pointwise coverage** [no probe change]
- Before: "… pointwise, for each reported quantity separately, not the stronger simultaneous coverage of all of them."
- After: "… pointwise, for each reported quantity separately, rather than the stronger simultaneous coverage of all of them."
- Why: "rather than" in place of a trailing "not".

## Sec. IV A

**C7. Shape of the χ² difference** [B5, B6, B7]
- Before: "It indicates a correlated shape difference, not a normalization difference, spread over many eigenmodes of the published covariance, with no single pT or p∥ band carrying more than 15% of it; its source has not been identified."
- After: "It indicates a correlated shape difference of unidentified source, rather than a normalization difference, spread over many eigenmodes of the published covariance, with each pT or p∥ band carrying at most 15% of it."
- Why: the trailing caveat ("its source has not been identified") moves into the noun phrase. "No single band more than 15%" is restated as the equivalent "each band at most 15%".

**C8. Learner choice** [B10, B12]
- Before: "We quote the LightGBM result as the central value because its covariance uses the same estimator. This learner was chosen after both comparisons were known, so the benchmark is a reproduction rather than an independent validation."
- After: "The LightGBM result, quoted as the central value because its covariance uses the same estimator, was chosen after both comparisons were known, so the benchmark is a reproduction rather than an independent validation."
- Why: two sentences on one object became one (Gemini r13 item 3). The B12 guardrail clause is kept word for word.

## Sec. IV B

**C9. History of the statistical band** [C19, C21, C23, C25, C26]
- Before: "Two earlier versions of the statistical band, distinct from the quoted block, were scored on 100 closure pseudo-experiments at a fixed truth (Ref. [14], Sec. 5.2). The first, whose test was specified in advance, undercovered in its tails: pooled over experiments and bins, 91.2% of standardized residuals fell within two standard deviations, against 95.4% nominal. A post hoc rescoring of the same pseudo-experiments against the second, rebuilt band removes the tail undercoverage: 97.7% fall within two standard deviations and 78.1% within one. This rescoring is not an independent coverage test, because the simulated part of the rebuilt band reuses the resampling mechanism of those pseudo-experiments."
- After: "On 100 closure pseudo-experiments at a fixed truth, a coverage test specified in advance found an earlier statistical band, distinct from the quoted block, undercovering in its tails: pooled over experiments and bins, 91.2% of standardized residuals fell within two standard deviations, against 95.4% nominal (Ref. [14], Sec. 5.2). The band rebuilt after that test, also distinct from the quoted block, reuses in its simulated part the resampling mechanism of those pseudo-experiments, so a post hoc rescoring of them against it is not an independent coverage test; it removes the tail undercoverage: 97.7% fall within two standard deviations and 78.1% within one."
- Why: review E item 1, and Gemini r13 items 2 (runs 1–3).
  - Four sentences become two.
  - The trailing "This rescoring is not an independent coverage test, because …" becomes the scope that comes before the result.
- Kept:
  - both SEC4 phrases, byte for byte;
  - "specified in advance" and "post hoc" (r13 review SHOULD-FIX 3);
  - "distinct from the quoted block", for both bands (C26).
- Support: "rebuilt after that test" is note §5.2, "That term was removed on 2026-10-06 and the band rebuilt".

**C10. Summary of the 2D result** [C27]
- Before: "The two-dimensional central value is therefore reproducible, and its covariance is built with the same estimator."
- After: "The two-dimensional result is thus a reproducible central value with a covariance built by the same estimator."
- Why: one claim instead of two clauses. The disclaimer that follows ("Its intervals, bias, and covariance have not been independently validated: we claim no coverage …") is unchanged; see REPORT, uncertainty 4.

## Sec. V B

**C11. The quoted uncertainties omit the residual bias** [V14]
- Before: "This residual bias under the tested deformations is not included in the quoted uncertainties."
- After: "The quoted uncertainties omit this residual bias under the tested deformations."
- Why: positive form, matching Sec. V A's "the quoted uncertainties omit this bias".

## Sec. V C

**C12. Diagnosis of the miscoverage** [V23, V24, V25, L2]
- Before: "A diagnosis of the stored pseudo-experiments attributes the miscoverage to a residual bias that grows with W and survives the nominal-truth bias correction. The rate change itself is recovered, and apart from a minor effect the intervals are not too narrow. The per-quantity bias and spread are inferred from a Gaussian fit to each quantity's 68% and 95% coverage rather than measured directly, and the source of the bias is not established (Ref. [14], Sec. 9.5)."
- After: "With the per-quantity bias and spread inferred from a Gaussian fit to each quantity's 68% and 95% coverage rather than measured directly, a diagnosis of the stored pseudo-experiments attributes the miscoverage to a residual bias, of unestablished source, that grows with W and survives the nominal-truth bias correction; the rate change itself is recovered, and apart from a minor effect the intervals are not too narrow (Ref. [14], Sec. 9.5)."
- Why: the inference (V24 guardrail) now comes before the attribution it qualifies instead of trailing two sentences later. "Source not established" goes into the noun phrase.

## Sec. V (Fig. 3 caption)

**C13. Seeds** [FG3]
- Before: "Panel (a) uses the random seeds of the estimator's development studies; panel (b) uses separate assessment seeds, which also entered its later development."
- After: "Panel (a) uses the random seeds of the estimator's development studies and panel (b) a separate set of assessment seeds, also used in its later development."
- Why: review E item 5. The fact prints only in the paper (the note has no "assessment seeds" sentence), so it is reworded, not moved.

## Sec. V D

**C14. Status of the five-observable covariance** [V32, V34]
- Before: "The covariance of the five-observable central value, which has a 42-cell (Eavail,W) projection, does not meet the validation criteria of its specification (Ref. [14], Sec. 9.6). The comparisons of Sec. V B use this covariance and no other five-observable covariance; the calibration of the joint tests (Sec. VII) does not use it."
- After: "The covariance of the five-observable central value, with its 42-cell (Eavail,W) projection, is used, although it does not meet the validation criteria of its specification (Ref. [14], Sec. 9.6), in the comparisons of Sec. V B, as the only five-observable covariance they use; the calibration of the joint tests (Sec. VII) does not use it."
- Why: review E item 6 (internal-record framing). The status is now a qualifier on where the covariance is used, not a sentence of its own. The note §9.6 wording is "It is used although it has not passed the acceptance criteria of its specification".

**C15. Seed dependence** [S5, V35, V36, V38, V39]
- Before: "We quote no covariance-based generator significance, because covariances from this estimator depend measurably on its random seed: in two further covariances built at two seed settings, changing the seed moves the projected uncertainty by about 6.1%, against a stability limit of 5%. This rests on one seed pair, and the spread over seed pairs has not been measured; five bands built at a fixed seed, which carry 26.0% of √Tr C, cannot vary with it, so their seed sensitivity, which could move the total in either direction, is also unmeasured."
- After: "On the one seed pair measured, covariances from this estimator depend on its random seed: between two further covariances built at two seed settings, changing the seed moves the projected uncertainty by about 6.1%, against a stability limit of 5%. The spread over seed pairs is unmeasured, as is the seed sensitivity of five bands built at a fixed seed, which carry 26.0% of √Tr C and could move the total in either direction. We therefore quote no covariance-based generator significance."
- Why:
  - The one-pair scope (the V38 guardrail) now opens the claim instead of following it.
  - The two "unmeasured" facts are now one sentence.
  - The consequence comes last. "Cannot vary with it" is carried by "built at a fixed seed".

**C16. Rounding** [no probe change]
- Before: "The estimators are also unstable at the level of rounding. Rounding-level input changes move …"
- After: "The estimators are also unstable at the level of rounding: rounding-level input changes move …"
- Why: the topic sentence and its evidence are joined (Gemini r13 run 3, item 3).

## Sec. VI

**C17. Binned diagnostic (sol r13: quoted in 3 of 3 runs)** [L6, L9, L10]
- Before: "On the same 109 joint cells and the fixed truth changes used to develop the estimator, an exact binned iterative unfolding with the same simulation and five iterations leaves about the same median residual as the boosted-tree estimator. Of the 144 … whose diagnosis is stable under the truth resolution, pooled over five truth changes, the tree approximation dominates only 15; … The diagnostic is binned, signal-only and noise-free, with the detector response fixed at the simulation's, on those same truth changes, and covers only the residuals whose diagnosis is stable under the truth resolution (38% of the joint-cell residuals above 2%). What unbinned information could recover, the coverage failure, and the validity of any interval lie outside its scope. Within that scope, the residual is consistent with the regularization of the inverse problem at this binning and prior, rather than with the tree approximation of the classifiers (Ref. [14], Sec. 9.3)."
- After: "In a binned, noise-free, signal-only comparison with the detector response fixed at the simulation's, on the same 109 joint cells and the fixed truth changes used to develop the estimator, an exact binned iterative unfolding of the same simulated events with five iterations leaves about the same median residual as the boosted-tree estimator. Of the 144 … whose diagnosis is stable under the truth resolution (38% of the joint-cell residuals above 2%), pooled over five truth changes, the tree approximation dominates only 15; … For these residuals and within this comparison, the residual is consistent with the regularization of the inverse problem at this binning and prior, rather than with the tree approximation of the classifiers (scope and exclusions: Ref. [14], Sec. 9.3)."
- Why: this is the round's model case.
  - The scope (binned, noise-free, signal-only, response fixed, same truth changes, 38% stable) opens the claim and is stated once.
  - The "outside its scope" list is a MOVE: note §9.3 prints all three exclusions (see REPORT §2).
  - "With the same simulation" is now "of the same simulated events", as in note §9.3.

## Sec. VII

**C18. Power against a reconstruction-level test** [X9, X6–X9]
- Before: "… rather than the decision. We have not compared their power with that of a reconstruction-level test."
- After: "… rather than the decision; their power relative to a reconstruction-level test is not studied here."
- Why: the X9 guardrail stays, as a clause on the claim it limits.

**C19. Descriptive comparisons** [G1]
- Before: "These comparisons are descriptive: they use central values of configuration (a) only, and no significance is assigned to them."
- After: "These descriptive comparisons use only the central values of configuration (a), with no significance assigned."
- Why: three clauses became one, and "only" is kept.

**C20. What the map shows** [G8, G10]
- Before: "The high-Eavail, high-W region is where the regularization bias of Sec. V is largest, and no closure test with a mismodelled detector response has been run for the Tune v1 map. The map therefore describes where the central value differs from the Tune v1; it does not locate an interaction mechanism."
- After: "Because the high-Eavail, high-W region is where the regularization bias of Sec. V is largest, and the Tune v1 map has had no closure test with a mismodelled detector response, the map describes where the central value differs from the Tune v1 rather than locating an interaction mechanism."
- Why: the reason and its consequence are now one sentence, and the trailing "it does not" becomes "rather than".

**C21. FWER under the actual stopping** [H22, H38]
- Before: "… is below the threshold, whatever rule determines when sampling stops, so the decision rule controls the familywise error rate of the ten decisions at 5% (App. B.5)." Then, two sentences later: "The calibration's computing budget was later extended by a bounded amount with observed p values visible; the error control above is unaffected by this, because it holds for any stopping rule (Ref. [14], Sec. 10.3)."
- After: "… is below the threshold, whatever rule determines when sampling stops, including the bounded extension of the calibration's computing budget that was decided with observed p values visible, so the decision rule controls the familywise error rate of the ten decisions at 5% (App. B.5)."
- Why: sol r13 run 1 and Gemini r13 runs 1–3 quoted it. The disclosure becomes part of the scope of the claim it bears on, and is stated once. This matches note §10.3: "whatever rule determines when sampling stops, including the budget extensions". The §10.3 pointer is on the next sentence (C22).

**C22. Design chronology (sol r13: 1 of 3)** [H33, H36, H37]
- Before: "The test design was fixed before any observed statistic was computed, although its reviewers had already seen descriptive per-cell residuals of the data."
- After: "The test design was fixed after its reviewers had seen descriptive per-cell residuals of the data, and before any observed statistic was computed (Ref. [14], Sec. 10.3)."
- Why: the two facts are given in time order, without the concessive "although … already". Both facts are kept (review E item 2: "This disclosure is required").

**C23. Lost pseudo-experiments (sol r13: 2 of 3)** [H27 MOVE, H29]
- Before: "The pseudo-experiments that computing time limits interrupted or prevented (224 for calibration, 53 for power) were rerun; none reaches the observed statistic in any test or shifted null, so no assignment of the lost outcomes changes any decision (Ref. [14], Sec. 10.6)."
- After: "Every pseudo-experiment that computing time limits interrupted or prevented was rerun, and none reaches the observed statistic in any test or shifted null, so no decision depends on the lost outcomes (Ref. [14], Sec. 10.6)."
- Why: this is ruling 1's own example.
  - The counts move to note §10.6, where they print as `\jtLostCal` and `\jtLostPow`.
  - The rerun and its outcome stay, because Data availability ("the recovery of the lost pseudo-experiments") needs an antecedent in the body.
  - "No assignment … changes any decision" is restated as the equivalent "no decision depends on the lost outcomes".

**C24. Recoil-response sensitivity study** [H53, H56]
- Before: "In an exploratory sensitivity study, scaling … and re-unfolding the data leaves every rejection in place against the original null distributions, with the observed statistics moving by up to about 11%. Neutrons and higher-momentum hadrons, which matter at high W, lie outside the test-beam sample; the study regenerates no null distribution and tests no other form or size of response change (untested effects: Ref. [14], Sec. 10.8)."
- After: "An exploratory sensitivity study tests a single form and size of response change against the original null distributions: scaling … and re-unfolding the data leaves every rejection in place, with the observed statistics moving by up to about 11%. Neutrons and higher-momentum hadrons, which matter at high W, lie outside the test-beam sample, and the study regenerates no null distribution (untested effects: Ref. [14], Sec. 10.8)."
- Why: the study's scope (one form and size, original nulls) now opens the claim. "Tests no other form or size" becomes "tests a single form and size". The H53 guardrail "against the original null distributions" is kept.

**C25. Calibration fidelity** [H9, H31, H63, H64, H69, H70]
- Before: "The simulation-size check of condition (iv) is not a test of the data process: every pseudo-experiment resamples the same simulated events, so the null distributions are conditional on that simulation, and their conditioning on the data-derived lateral shifts has not been validated. The independent recomputation verifies the calculation, not whether the chain reproduces the data analysis, and no rejection rate has been measured for null pseudo-data processed like the data, which would require an independent simulation sample."
- After: "Every pseudo-experiment resamples the same simulated events, so the null distributions are conditional on that simulation, and the simulation-size check of condition (iv) is a check within it rather than a test of the data process; the conditioning of the null distributions on the data-derived lateral shifts has not been validated. The independent recomputation verifies the calculation rather than whether the chain reproduces the data analysis. Measuring a rejection rate for null pseudo-data processed like the data would require an independent simulation sample and has not been done."
- Why:
  - The cause now comes before the consequence.
  - The "not … not … no" stack becomes "rather than" twice and one positive statement of what the missing test would need.
  - The ambiguous "their" is made explicit.

**C26. Multiplier scan** [R5, R6]
- Before: "As a sensitivity check outside the decision rule, a scan of the multiplier of the shift along δfine finds all ten rejections determined up to a multiplier of about 5.2 (Ref. [14], Sec. 10.5); the scan tests that one direction and bounds neither the actual residual nor the convergence."
- After: "A sensitivity scan outside the decision rule, of the multiplier of the shift along the single direction δfine, finds all ten rejections determined up to a multiplier of about 5.2 (Ref. [14], Sec. 10.5); it bounds neither the actual residual nor the convergence."
- Why: "one direction" moves into the description of the scan. The R6 guardrail ("bounds neither …") is kept.

## Not changed (deliberately)
- **Data availability, `\pubhold`, funding and acknowledgments.** These are protected and in `main_paper.tex`, which this round does not edit.
- **The hydrocarbon sentence of Sec. VII E** (r13 review SHOULD-FIX 1).
- **The five-iteration sentence of Sec. III** (SHOULD-FIX 2).
- **The 135 MeV materiality clause** (r12 B4 and r13 NIT 1 guardrail).
- **The FWER assumptions A1 and A2, and the "on average over the nuisance priors" clause.**

## Post-review fixes (REVIEW.md, ADOPT-AFTER-FIXES; director's instruction)
Line numbers are in `S/wt-reg4/docs/analysis-note/paper_body.tex` after the fixes.

- **SHOULD-FIX 1 (C23), :911–914.**
  - Before: "so no decision depends on the lost outcomes".
  - After: "Every lost pseudo-experiment was rerun, and none reaches the observed statistic in any test or shifted null, so including the recovered outcomes changes no decision (Ref. [14], Sec. 10.6)".
  - Why: note §10.6 says the sensitivity computed before recovery showed "every decision could change under a realizable assignment" of the lost draws. What it supports is that the recovered draws, now observed, change no decision. "Lost" is defined by the A2 clause at :894–896.
- **NIT 1 (C15), :637–639.**
  - Before: "… which carry 26.0% of √Tr C and could move the total in either direction".
  - After: "… which carry 26.0% of √Tr C; letting them vary could move the total in either direction".
  - Why: in the old wording the bands themselves "could move" the total; it is letting them vary that could. This matches note §9.6.
- **NIT 2 (C17), :742–744.**
  - Before: "For these residuals and within this comparison".
  - After: "For the 144 resolution-stable residuals and within this comparison".
  - Why: "these residuals" had an ambiguous antecedent.
- **NIT 3 (C9), :455.**
  - Before: "…; it removes the tail undercoverage".
  - After: "…; that rescoring removes the tail undercoverage".
  - Why: the rescoring removes the undercoverage, not the band. The SEC4 phrase is unchanged.
- **NIT 4 (C14), :628–631.**
  - After: "The comparisons of Sec. V B use only one five-observable covariance, that of the central value with its 42-cell (Eavail,W) projection, although it does not meet the validation criteria of its specification (Ref. [14], Sec. 9.6); the calibration of the joint tests (Sec. VII) does not use it."
  - Why: the old sentence split "is used … in the comparisons" with a 20-word concession. The comparisons are now the subject.
- **NIT 5 (C21), :897–901.**
  - The FWER sentence now ends "… whatever rule determines when sampling stops, so the decision rule controls the familywise error rate of the ten decisions at 5% (Ref. [14], App. B.5)."
  - A new sentence follows: "That invariance covers the bounded extension of the calibration's computing budget, decided with observed p values visible."
  - Why: the 75-word sentence was split. Its qualifiers (under A1 and A2, any stopping rule) stay in the FWER sentence.
- **NIT 6 (A2), :894–896.**
  - Added: "; A2 also requires the pseudo-experiments that computing time limits interrupted or prevented to have been lost independently of their outcomes, which has not been shown (Ref. [14], Sec. 10.3)".
  - Why: with this clause the paper no longer reads as if A2 were established. The wording is note §10.3's.
  - The clause also names the lost population, which let C23 shrink to "Every lost pseudo-experiment".
  - Ledger H28 changes from MOVE to KEEP.
