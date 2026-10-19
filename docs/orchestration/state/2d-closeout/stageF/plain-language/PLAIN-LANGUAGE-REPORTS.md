# Plain-language pass: the agents' reports, verbatim
**Owner:** the paper-tighten lane, as director (Stage F), 2026-10-18. The reports of the readers, writers, reviewers and verifier of the plain-language pass ([`../PLAIN-LANGUAGE.md`](../PLAIN-LANGUAGE.md)), copied verbatim from the director's session scratchpad, except that every heading is demoted two levels so this file keeps one title. Each report's sha256 (of the scratchpad original) is given with it. Line numbers inside a report are those of the commit it names.
**CITABLE FOR:** what each agent found and did. **NOT CITABLE FOR:** a decision; the dispositions are in [`../PLAIN-LANGUAGE-IMPLEMENTATION.md`](../PLAIN-LANGUAGE-IMPLEMENTATION.md). The reader reports are naive reads by design and are not authorities on content.
**Same-model caveat:** every agent is Claude Opus 5.5 on claude-school.

---

## R1. Baseline reader, paper (PDF at 28d28626) — `reader-baseline-paper.md` (sha256 `ae629c05212bd4bc…`)

### Reader test: "Multidimensional unbinned unfolding of MINERvA inclusive charged-current neutrino data: validation and calibrated model tests"

Reader persona: neutrino cross-section postdoc (MINERvA/T2K/MicroBooNE background), fluent in D'Agostini
unfolding, multi-universe systematics, chi2 against a covariance, toys and coverage; has heard of OmniFold;
has never seen this project. Source read: the 11-page PDF only. Quotes are exact apart from rejoined
line-break hyphenation.

---

#### 1. Overall verdict

The physics is interesting, and most of it can be extracted, but the paper takes much more work to read than
a PRD paper should. A typical referee would finish it with three impressions. (a) The authors are being
scrupulously honest. (b) The analysis has many unresolved problems. (c) The text was written as an audit
trail and not as an argument. The register problem is real, and it is concentrated in specific places. It is
not uniform.

- **Worst sections:** Sec. IV B (two-dimensional uncertainty and its coverage), Sec. VI B (Conditions, item
  (i) especially), Sec. VII (Status of a five-dimensional uncertainty), the second half of Sec. VI C (lost
  pseudo-experiments, multiplier scan), and the Data availability statement. These read like a review-board
  record. They tell the reader what was built, rebuilt, rescored, declared, frozen, excepted and recovered,
  and they bury what the uncertainty actually is.
- **Abstract and Introduction:** dense, but in a different way. The abstract is mostly a list of
  limitations written as stacked noun phrases ("background-treatment, regularization, coverage, and
  estimator-seed limitations"). It never states the clean positive results in numbers (1.1% agreement in
  the integrated 2D cross section, the low-recoil and high-W features). The same list of limitations
  appears in the abstract, twice in the Introduction, at the end of Sec. IV C, in Sec. VII and in the
  Conclusions, which is about five times.
- **Best sections:** the first paragraph of the Introduction, Sec. III's description of the OmniFold
  iteration and the two background treatments, most of Sec. V (central-value results), the definitions of
  the test statistics in Sec. VI A, and the first paragraph of Sec. VI D. These read like normal PRD prose.
  A MINERvA reader would be comfortable there. Sec. V does have local defensive asides, but they are short
  and mostly justified.
- **Mechanical problems a referee would flag at once:** red "[HOLD: ...]" placeholders, four bibliography
  entries with no locator ([25], [38], [39], and an analysis note at a git hash), and references whose
  titles carry internal codenames ("frozen contract", "s5p", "kappa-breakdown", "W2B-REPORT", "release
  candidate RC7").

My bottom line as a reader: a good, honest paper is in here. It is hidden under procedural vocabulary, and
it has one structural gap. The quantity said to block a 5D measurement, the "measured model dependence", is
never given as a number.

---

#### 2. Passages that read as non-physics register

Each entry gives: page / section, the exact quote, what reads wrong, and a suggested physics-register
version that keeps every disclosed limitation.

##### Abstract (p. 1)

**2.1** p. 1, Abstract.
> "The higher-dimensional central values pass marginal-normalization checks, and the three- and
> four-observable central values pass injected-shape closure checks, but background-inclusive tests and
> uncertainty studies expose background-treatment, regularization, coverage, and estimator-seed limitations,
> and the measured model dependence prevents a qualified five-dimensional measurement with total
> uncertainties at useful precision."

- *What reads wrong:* the sentence stacks four compound-noun "limitations" and three internal terms
  ("background-inclusive tests", "qualified", "useful precision"). It is one 60-word sentence.
- *Physics version:* "The three- to five-dimensional results reproduce the lower-dimensional marginals to
  1–2% and recover injected shape distortions in signal-only closure tests. Pseudo-experiments that include
  backgrounds show a bias of up to 4% at high W from the background subtraction. The unfolding only
  partially follows generator-sized shape changes. The statistical intervals have not been shown to cover.
  The model dependence of the unfolding is too large (X%) for us to quote a five-dimensional cross section
  with total uncertainties."

**2.2** p. 1, Abstract.
> "These conditional tests recover known discrepancies without demonstrated discrimination from the tested
> joint information beyond matched coarse projections, and their physical interpretation is limited by an
> omitted calorimetric recoil-response uncertainty and unresolved fine-grid convergence."

- *What reads wrong:* three negations in a row ("without demonstrated discrimination ... beyond ...
  omitted ... unresolved"). "Fine-grid convergence" is meaningless until p. 7. "Tested joint information"
  is not a physics phrase.
- *Physics version:* "The same tests applied to two-dimensional projections, (pT, p∥) or (Eavail, W),
  already reject every model, so the five-dimensional information adds no demonstrated discriminating
  power. The rejections assume the simulated calorimetric recoil response, for which no uncertainty is
  included. They also assume a model-construction approximation (Sec. VI B) whose convergence has not been
  demonstrated."

##### Introduction (pp. 1–2)

**2.3** p. 1, Sec. I.
> "We assess the practical reliability of this construction on data. The two-dimensional reproduction
> provides an external reference. Projection anchors, injected-shape tests, background-inclusive
> pseudo-experiments, and uncertainty ensembles test consistency, shape recovery, and sensitivity to
> background treatment, regularization, and estimator seeds as observables are added (Secs. IV and VII).
> Together they identify which parts of the construction work and which limit a five-dimensional
> measurement with total uncertainties."

- *What reads wrong:* "construction" is the project's word for the analysis. It recurs about 15 times. A
  physicist says "the analysis", "the unfolding" or "the method". "Projection anchors" is jargon. The final
  sentence is a promise about a process, not a statement of content.
- *Physics version:* "We validate the method in three ways. We compare with the published 2D result. We
  check that higher-dimensional results reproduce their lower-dimensional marginals. We run closure and
  pseudo-experiment tests, including backgrounds, regularization and the random seed of the classifier
  training (Secs. IV and VII)."

**2.4** pp. 1–2, Sec. I.
> "This regularization bias, the estimator-seed sensitivity, and untested coverage limit the construction,
> and the measured model dependence prevents a five-dimensional measurement with qualified total
> uncertainties at useful precision."

- *What reads wrong:* the abstract sentence is repeated almost verbatim. "Qualified total uncertainties"
  is internal governance language ("qualified" = passed an internal acceptance criterion).
- *Physics version:* say it once, in the abstract or the intro, with a number: "...the model dependence
  of the unfolding (X% in the most affected cells) exceeds our target precision, so we do not report
  five-dimensional uncertainties."

**2.5** p. 2, Sec. I.
> "All ten calibrated tests, in total and in shape for each of the five predictions, reject at the 5%
> familywise level under six stated conditions (Sec. VI B), among which an omitted calorimetric
> recoil-response uncertainty and unresolved fine-grid convergence limit their physical interpretation;
> because each test also has p < 0.05 in at least one matched coarse projection, the joint information is
> not shown to add discrimination."

- *What reads wrong:* the third restatement of the result, again with the condition list folded in.
  "Is not shown to add discrimination" is a double hedge.
- *Physics version:* "All five predictions are rejected, in both normalization and shape, at 5%
  family-wise significance (Sec. VI). The same tests on two-dimensional projections also reject every
  model, so the five-dimensional information does not add demonstrated sensitivity."

**2.6** p. 2, Sec. I.
> "The companion analysis note [14] gives the complete validation, uncertainty, and joint-test records."

- *What reads wrong:* "records" is an auditing word.
- *Physics version:* "Further details of the validation and the statistical tests are given in a
  companion note [14]."

##### Sec. II, Data, signal, and simulation (p. 2)

**2.7** p. 2, Sec. II.
> "The files analysed are an earlier production of that release; their names and sizes are recorded for
> reproduction (see Data availability)."

- *What reads wrong:* "earlier production" is project history. The reader wonders whether the paper uses
  stale data. "Recorded for reproduction" is process language.
- *Physics version:* "We use the [name/version] production of the open-data release; file checksums are
  listed in Ref. [38]." If the version differs from the current public one in a way that matters, say how.

**2.8** p. 2, Sec. II, after Eq. (1).
> "charged pions their energy minus an inherited constant of 135 MeV rather than the charged-pion mass (an
> uncorrected deviation that, in a simulated sample, moves 0.67 % of events into another true-Eavail bin and
> changes no true-Eavail bin by more than 1.05 %; it has not been compared with the correlated uncertainty)"

- *What reads wrong:* "inherited" and "uncorrected deviation" make this read like a known bug that was
  never fixed, not a definition. "It has not been compared with the correlated uncertainty" is opaque:
  which correlated uncertainty?
- *Physics version:* "Charged pions contribute Eπ − 135 MeV. This follows [the convention of Ref. X / the
  analysis code we build on] and differs slightly from the kinetic energy. Using mπ± instead moves 0.67%
  of simulated events across true-Eavail bins and changes no bin by more than 1.05%, which is small
  compared with [the relevant uncertainty]." If this really is an unintended inheritance, say so plainly
  in one clause: "a convention we inherited from the analysis framework and did not change."

**2.9** p. 2, Sec. II.
> "so the five reconstructed inputs share information and do not by themselves establish five
> independently constrained physical directions."

- *What reads wrong:* the point is correct, but "establish five independently constrained physical
  directions" is a roundabout way to say "are correlated".
- *Physics version:* "...so the five reconstructed observables are strongly correlated and the result does
  not contain five independent constraints."

**2.10** p. 2, Sec. II.
> "The GENIE and NuWro predictions use a corrected flux sampling (an exact event-by-event reweighting to
> the analysis flux, with added 50–100 GeV samples)"

- *What reads wrong:* "corrected" implies there was an earlier wrong version, which is history.
- *Physics version:* "The GENIE and NuWro predictions are reweighted event by event to the analysis flux,
  with dedicated samples added for 50–100 GeV."

##### Sec. III, Unbinned unfolding (pp. 2–3)

**2.11** p. 2, Sec. III.
> "All estimator configurations use five OmniFold iterations with gradient-boosted decision-tree
> classifiers [23, 24], and each result names the one it uses."

- *What reads wrong:* "each result names the one it uses" is a filing-system remark. The real problem is
  that the paper uses three estimators: an exact-split scikit-learn one, a nominal LightGBM one, and a
  "deterministic" LightGBM one with a different background treatment. The reader needs a table.
- *Physics version:* a small table, "Estimator A (2D cross-check), B (central values, Figs. 1–3), C (joint
  tests, Sec. VI)", with the classifier, the background treatment and where each is used. Then refer to
  A/B/C.

**2.12** p. 3, Sec. III.
> "An exact-split scikit-learn estimator, the original two-dimensional choice, is retained as a cross-check
> (Sec. IV A)."

- *What reads wrong:* "the original ... choice" is project history.
- *Physics version:* "An exact-split scikit-learn gradient-boosting classifier is used as a cross-check."

**2.13** p. 3, Sec. III.
> "The joint tests (Sec. VI) use a deterministic LightGBM configuration, selected before the joint-test
> design was fixed, whose unbinned negative-weight background treatment and higher-capacity refinement
> classifier together remove most of the purity method's nominal-truth bias in the highest-W cells
> (Sec. IV)."

- *What reads wrong:* "selected before the joint-test design was fixed" is a process timestamp.
  "Nominal-truth bias" is not standard. The reader immediately asks why the better background treatment is
  not used for the central values. The text never answers.
- *Physics version:* "For the hypothesis tests of Sec. VI we use a deterministic LightGBM configuration
  with the negative-weight background treatment, which reduces the background-subtraction bias at high W
  (Sec. IV C). The central values use the purity method because [reason]."

**2.14** p. 3, Sec. III.
> "The use of AI tools in this work is described in the Acknowledgments."

- *What reads wrong:* it is out of place in a methods section and reads like a compliance notice.
- *Physics version:* delete it here. The Acknowledgments disclosure is sufficient.

##### Sec. IV, Validation (p. 3)

**2.15** p. 3, Sec. IV intro.
> "In closure tests, truth denotes the known simulated target and the prior is the initial truth
> distribution; the response maps truth to selected observations. Closure measures recovery under a
> specified deformation. Coverage measures how often intervals contain their target over repeated
> experiments, testing the estimator and interval construction jointly. Missed-event bookkeeping is an
> invariant check, and iteration dependence is a stability diagnostic. Neither establishes recovery or
> coverage."

- *What reads wrong:* it is a glossary for a reader who already knows the terms, followed by a
  pre-emptive disclaimer. "Missed-event bookkeeping" never appears again. "Neither establishes recovery or
  coverage" defends against a claim nobody made.
- *Physics version:* delete the paragraph, or reduce it to one sentence defining "closure" and "coverage"
  as used here.

**2.16** p. 3, Sec. IV A.
> "against the full published covariance the indicative distance is χ2/ndf = 2.65, a correlated shape
> difference."

- *What reads wrong:* "indicative distance" is a hedge word. The reason it is only indicative (the two
  results share data, so their covariance is not the published one) comes three sentences later.
- *Physics version:* "Using the published covariance alone, χ²/ndf = 2.65 (ndf = 205), dominated by a
  correlated shape difference. Because both results come from the same events, this is not a significance;
  that would need the cross-covariance of the two estimates."

**2.17** p. 3, Sec. IV A.
> "The quoted central value was changed from exact-split to LightGBM after both comparisons were known, so
> that it matches the estimator of its covariance; the two differ by a per-bin median of 0.98 % (maximum
> 12.2 %), and no block of the covariance includes this learner dependence."

- *What reads wrong:* "was changed" is history. The disclosure itself is legitimate: the choice was made
  after the χ² values were seen.
- *Physics version:* "We take the LightGBM result as the central value, so that it is consistent with the
  covariance. This choice was made after both χ² values were known. The two estimators differ by a median
  of 0.98% per bin (maximum 12.2%); this learner dependence is not included in the uncertainty."

##### Sec. IV B, Two-dimensional uncertainty and its coverage (pp. 3–5). This is the worst section.

**2.18** p. 3.
> "The standalone covariance combines systematic-universe, statistical, training-seed and run-period
> blocks; the first three are LightGBM ensembles at the central value's estimator"

- *What reads wrong:* "standalone" is undefined. Standalone from what? "Ensembles at the central value's
  estimator" is awkward.
- *Physics version:* "The covariance of the 2D result is the sum of four terms: systematic universes,
  statistical (bootstrap), classifier training seed, and run-period consistency. The first three are
  obtained by repeating the unfolding with the central-value estimator."

**2.19** p. 3.
> "The published flux block (4.01 % median) is larger than ours (3.75 %), for a reason the release does
> not establish."

- *What reads wrong:* "for a reason the release does not establish" is legalistic.
- *Physics version:* "...larger than ours (3.75%); we could not determine the origin of the difference
  from the public release."

**2.20** p. 3.
> "Tests in two of the 187 universes (a resonance-production and a flux universe), each at two training
> seeds, resolved no effect above the noise of an earlier ten-seed training scan, about three times the
> training-seed block; an effect below about twice that noise is not excluded, so the test is not tight,
> and the approximation is not corrected."

- *What reads wrong:* four hedges in a row ("no effect above", "not excluded", "not tight", "not
  corrected"). "An earlier ten-seed training scan" is history. The sentence before it ("approximate the
  weighting of events that fail reconstruction") never says what the approximation is.
- *Physics version:* "In the systematic universes, the efficiency correction for events that fail
  reconstruction is [approximated as X]. Testing this in two universes (one resonance, one flux), at two
  training seeds each, finds no effect larger than the seed-to-seed noise (about 3× the training-seed
  uncertainty). The test is only sensitive to effects above about twice that noise. We apply no
  correction."

**2.21** pp. 3–4.
> "Its reference-free double-ratio construction uses the periods' own simulated responses; it does not
> identify a correct period. The small number of groups, possible regularization shrinkage and retained
> statistical and training noise limit its interpretation. Containment of the observed differences by this
> construction is not evidence of coverage. The block's own consistency check passes by construction; it is
> not a test."

- *What reads wrong:* four consecutive sentences of disclaimer, two of them pure negation. A physics
  reader does not need to be told that a check which passes by construction is not a test. Just do not
  present it as one.
- *Physics version:* "The run-period term is built from double ratios (data/simulation of each period
  group relative to the others), so it does not require choosing a reference period. With only three
  groups, and with statistical and training noise in each, it is a rough estimate."

**2.22** p. 4.
> "The statistical block, as first built, undercovered in its tails in 100 pre-registered closure
> pseudo-experiments against a fixed truth: pooled over experiments and bins, 91.2 % of standardized
> residuals fell within two standard deviations, against 95.4 % nominal. The main cause, a completeness
> division that the bootstrap replicas carried and the central value does not, was removed in a rebuilt
> band. Rescoring the same pseudo-experiments against the rebuilt band, which is post hoc and partly
> circular, removes the tail undercoverage: 97.7 % fall within two standard deviations and 78.1 % within
> one, so the rebuilt band is wider than the toy scatter, for reasons not established. The quoted
> statistical block is a different ensemble: 300 replicas drawn at the central value's training seed in
> three independent streams (data, signal and background simulation), with a median statistical
> uncertainty of 0.684 %. Neither it nor the rebuilt band has been independently tested."

- *What reads wrong:* this is the history of a bug and two rebuilds. The reader must keep track of three
  statistical bands (first built, rebuilt, quoted) to learn in the last sentence that the one actually used
  has never been coverage-tested. "Pre-registered" is clinical-trial vocabulary. "Rescoring" is process
  language.
- *Physics version:* "The statistical uncertainty is estimated from 300 bootstrap replicas, with the data,
  signal simulation and background simulation resampled independently. Its median is 0.68% per bin. The
  coverage of this band has not been tested. A coverage test of an earlier bootstrap with 100 toy
  experiments, defined in advance, found 91.2% of residuals within 2σ (95.4% expected). We traced this to
  an efficiency correction applied inconsistently to the replicas and the central value. The band used
  here does not have that inconsistency. Re-evaluating the same toys against a corrected band gives
  over-coverage (97.7% within 2σ, 78.1% within 1σ), which we do not understand."

**2.23** pp. 4–5.
> "An assessment of the saved products found construction defects in the earlier budget, among them a
> truth-input mismatch between its systematic sweep and that sweep's reference and unpropagated
> background-template statistics [25]; the quoted covariance is free of both."

- *What reads wrong:* this is entirely internal history ("saved products", "earlier budget", "systematic
  sweep"). It cites an unlocatable reference. It tells the reader about bugs in something not shown.
- *Physics version:* delete it. If the background-template statistical uncertainty matters, state
  positively that "the statistical uncertainty of the background templates is included."

**2.24** p. 5.
> "We report a reproducible two-dimensional central value with a matched uncertainty construction under
> declared conventions. Full scientific closeout is not achieved: the construction has not been
> independently validated for population or simultaneous interval coverage, and it supplies no calibrated
> covariance-based generator significance."

- *What reads wrong:* "full scientific closeout", "declared conventions", "matched uncertainty
  construction" and "population ... coverage" are project-management and audit vocabulary. "Supplies no
  calibrated covariance-based generator significance" describes something not done, in jargon.
- *Physics version:* "The 2D result is given with a full covariance (Fig. 1). The coverage of this
  covariance, bin by bin or jointly, has not been validated, so we do not convert χ² values computed with
  it into significances."

**2.25** p. 5.
> "Validated total intervals over the full reporting domain require new inputs: independent
> production-size simulation, a validated continuous nuisance generator and independent-generator samples
> not already inspected. No coverage claim is made."

- *What reads wrong:* "continuous nuisance generator" is undefined. "Not already inspected" refers to
  blinding without saying so. This is a work-plan item. "No coverage claim is made" is the fourth such
  statement in this subsection.
- *Physics version:* "Validating coverage would require an independent full-size simulation, a continuous
  [parametrization] of the nuisance parameters, and alternative-generator samples not used in developing
  the analysis." Cut "No coverage claim is made."

##### Sec. IV C, Higher-dimensional central values (p. 5)

**2.26** p. 5.
> "Every higher-dimensional central-value construction is tested against its lower-dimensional
> predecessor."

- *What reads wrong:* "predecessor" is chronological.
- *Physics version:* "Each higher-dimensional result is checked against the corresponding
  lower-dimensional one by integrating over the added observables."

**2.27** p. 5.
> "The unbinned negative-weight background treatment, as first measured with a deterministic variant of
> the five-dimensional LightGBM central-value estimator, reduces it to below 0.3 %, leaving up to 1 % in
> some joint cells"

- *What reads wrong:* "as first measured" is history. "Below 0.3%" and "up to 1%" in the same clause
  confuse: 0.3% in which cells?
- *Physics version:* "With the negative-weight background treatment (estimator C) the bias falls below
  0.3% in the highest-W [marginal] cells and below 1% in all (Eavail, W) cells."

**2.28** p. 5.
> "The unfolding follows a generator-sized change of the Eavail shape only partly."

- *What reads wrong:* "generator-sized" is coined. The structure of the sentence buries the finding.
- *Physics version:* "The unfolding does not fully recover a change of the Eavail shape as large as the
  difference between generators."

**2.29** p. 5.
> "This regularization bias lies outside the quoted uncertainty construction and persists across the
> tested iteration and capacity scans"

- *Physics version:* "This regularization bias is not included in the quoted uncertainties, and it does
  not decrease when the number of iterations or the classifier capacity is varied over the tested range."

**2.30** p. 5.
> "An end-to-end coverage test of bias-corrected statistical intervals from a deterministic variant of the
> estimator failed its predeclared criterion at nominal truth and under an Eavail tilt, so frequentist
> coverage of the five-dimensional intervals remains unestablished."

- *What reads wrong:* "failed ... so ... remains unestablished" understates. A failed coverage test shows
  under-coverage (or over-coverage). It does not leave coverage merely unestablished. "Predeclared
  criterion" is process language, and the criterion is not given.
- *Physics version:* "A coverage test of the bias-corrected statistical intervals of estimator C gave
  Y% coverage at nominal truth and Z% under an Eavail tilt, against a criterion of W%, so these intervals
  do not cover."

##### Sec. V, Central-value results (pp. 5–6). Mostly fine.

**2.31** p. 5.
> "(same-sample ratios computed with GENIE before its flux correction)"

- *What reads wrong:* "before its flux correction" is history. It refers back to the "corrected flux
  sampling" of Sec. II.
- *Physics version:* "(ratios computed within a single GENIE sample, without the flux reweighting of
  Sec. II)".

**2.32** p. 5.
> "but its effect on the two common cells is uncomputed, so the comparison is not quantitative."

- *Physics version:* "...we have not evaluated its effect on the two common cells, so the comparison is
  qualitative." This is acceptable as it stands. "Uncomputed" is just unidiomatic.

**2.33** p. 5.
> "These statements are descriptive: no significance is assigned, no response-mismatch closure has been
> run for this map, and the high-Eavail, high-W region is where the regularization bias of Sec. IV is
> largest."

- *What reads wrong:* the content is fine and important. "Response-mismatch closure" is undefined (it
  seems to be the test McFarland suggested in the Acknowledgments). The triple negation could be one
  positive caveat.
- *Physics version:* "No uncertainty is assigned to this map. The high-Eavail, high-W region is also where
  the regularization bias of Sec. IV C is largest, and we have not performed a closure test with a
  mismodelled detector response there."

**2.34** p. 6.
> "supplying the higher-energy share present in GENIE and NuWro gives it about the others' contrast."

- *What reads wrong:* the wording is opaque.
- *Physics version:* "If GiBUU is supplemented with the Eν > 20 GeV contribution taken from GENIE and
  NuWro, its high-W deficit becomes similar to theirs."

##### Sec. VI A, Hypotheses, statistics, and calibration (pp. 6–7)

**2.35** p. 6.
> "the null hypothesis H0(G) is that the true cross section equals G on a fine five-dimensional grid, with
> the MINERvA Tune v1's shape and G's finite-sample fluctuations below that grid. We call this the hybrid
> null"

- *What reads wrong:* the fine grid is never specified (number of bins, edges). "G's finite-sample
  fluctuations below that grid" is unclear: does the null include the statistical noise of the G
  generator sample?
- *Physics version:* "To generate pseudo-data under prediction G, we reweight the simulation so that it
  matches G in each bin of a fine 5D grid ([N] bins, Appendix/Ref. [14]). Within each fine bin the
  event distribution keeps the Tune v1 shape, and bin contents carry the statistical fluctuations of the
  finite G sample. We call this the hybrid null hypothesis. For G = Tune v1 it coincides with the exact
  null."

**2.36** p. 6.
> "Each decision uses the claim p value, the largest p value over a set of shifted nulls fixed in advance
> (the claim variants)"

- *What reads wrong:* "claim p value" and "claim variants" are internal vocabulary.
- *Physics version:* "For each test we quote a conservative p value: the largest over a predefined set of
  shifted null hypotheses that account for [the simulation-size difference and the fine-grid
  approximation]."

**2.37** p. 6.
> "The external nulls are strongly non-central, with non-centralities λ of 318–6344 in these units,
> because the calibration reproduces the estimator's pull toward its prior."

- *What reads wrong:* "in these units" for a dimensionless non-centrality is odd. The physics point is
  important and should be stated directly: the unfolding is so strongly biased toward Tune v1 that
  pseudo-data drawn from G, once unfolded, differ from G by T of hundreds to thousands.
- *Physics version:* "Because the unfolding is biased toward its Tune v1 prior, pseudo-data generated from
  G and then unfolded do not reproduce G. Under the null, T is therefore distributed far from a χ²
  (non-centrality 318–6344, against 109 cells). The calibration includes this bias by construction."

**2.38** p. 7.
> "Two data-informed elements are disclosed: reviewers of the design had seen descriptive per-cell
> residuals before it was fixed, and a bounded extension of the production budget, which changed no
> statistic, shifted null, threshold, or stopping rule, was decided while job-status outputs exposed
> observed claim p values; the Monte Carlo p values remain valid at the number of pseudo-experiments
> reached."

- *What reads wrong:* "data-informed elements are disclosed", "reviewers of the design", "production
  budget" and "job-status outputs" are review-board register. The disclosure is legitimate and should
  stay.
- *Physics version:* "The test design was fixed after the descriptive residuals of Sec. V had been seen.
  The number of pseudo-experiments was increased once after the observed p values were visible. This
  changed no statistic, threshold or stopping rule, and the p values are valid at the number of
  pseudo-experiments actually generated."

**2.39** p. 7.
> "An independent recomputation with separately written code agrees with the production evaluation in all
> 1379 compared quantities. The specification fixed in advance and the recorded result are in Ref. [32];
> the complete record is in the analysis note's joint-test section [14]."

- *What reads wrong:* this is an audit sentence. "1379 compared quantities" is oddly precise and
  meaningless to the reader.
- *Physics version:* "The test statistics and p values were cross-checked with an independent
  implementation. Details are in Ref. [14]."

##### Sec. VI B, Conditions (pp. 7–8)

**2.40** p. 7.
> "The decisions are tests of the hybrid null, and each holds under six conditions of the nuisance model,
> numbered as in the specification fixed in advance [32]."

- *What reads wrong:* "numbered as in the specification fixed in advance" is process language. A
  physicist would title this "Assumptions" or "Limitations of the null model".
- *Physics version:* "The tests rely on the following assumptions about the null model."

**2.41** p. 7, condition (i).
> "Before any result, the claim variants were set from an assumed extrapolation: if the step kept
> shrinking geometrically at a rate taken from the design review, whose calculation is not recorded, the
> residual would be about one to three times the last step; the claim variants take its central estimate,
> ±2 δfine, and robustness checks that do not enter the decisions use its upper end, ±3 δfine."

- *What reads wrong:* "a rate taken from the design review, whose calculation is not recorded" is the
  single most damaging phrase in the paper for reader trust (see Sec. 6). It reveals undocumented process.
  "Claim variants" and "robustness checks that do not enter the decisions" are internal.
- *Physics version:* "Assuming that successive refinements shrink geometrically, at a rate [r] estimated
  [how], the residual below the fine grid would be 1–3 times the last step. We therefore shift the null by
  ±2δfine in the quoted p values and check ±3δfine separately. The measured step sizes are also consistent
  with slower convergence, so this estimate may be optimistic."

**2.42** pp. 7–8, condition (i).
> "outside the decision rule, the scan of Sec. VI C finds them determinate for shifts along that direction
> up to about 5.2 δfine, which bounds neither the residual nor convergence."

- *What reads wrong:* it duplicates Sec. VI C. "Outside the decision rule" and "determinate" are internal.
  "Bounds neither ... nor" is a negation.
- *Physics version:* "The rejections persist for shifts up to 5.2δfine along this direction (Sec. VI C).
  This does not bound shifts in other directions."

**2.43** p. 8, after condition (vi).
> "The Monte Carlo p values are exact for the simulated null to the extent that the pseudo-experiment
> chain reproduces the analysis applied to the data; the independent recomputation verifies the
> calculation, not that adequacy."

- *Physics version:* "The p values are exact provided the pseudo-experiments reproduce the analysis
  applied to the data. The independent recomputation checks the arithmetic, not this assumption."

##### Sec. VI C, Results (p. 8)

**2.44** p. 8.
> "A scan of the shift multiplier along δfine, specified before it ran but run after the decisions and
> outside the decision rule [33], keeps all ten decisions determinate rejections at every sampled
> multiplier up to 5.25 δfine in the calibration ensembles at their stopping point (5.17 δfine with the
> recovered pseudo-experiments included); it tests one prescribed direction and bounds neither the actual
> residual nor convergence."

- *What reads wrong:* the procedural timestamping ("specified before it ran but run after the
  decisions"). Three near-identical numbers (5.2, 5.25, 5.17) appear across two subsections.
- *Physics version:* "Increasing the shift along δfine, all ten rejections hold up to 5.2δfine. This
  probes only one direction of the fine-grid residual."

**2.45** p. 8.
> "Computing-job time limits interrupted or prevented 224 calibration and 53 power pseudo-experiments. Had
> every interrupted one exceeded the observed statistic, no test would have been rejected, so the lost
> seeds were re-run after the decisions, outside the decision rule, under a procedure fixed and
> independently reviewed beforehand [34], which first reproduced 16 completed seeds exactly. None of the
> recovered pseudo-experiments reaches the observed statistic in any test or shifted null: every submitted
> pseudo-experiment has now been observed, and no assignment of the lost outcomes changes any decision. The
> closest approach is 4.6 below the observed value of 868.6 (GENIE + MEC shape, robustness shift)."

- *What reads wrong:* this is an operations log ("computing-job time limits", "lost seeds", "procedure
  fixed and independently reviewed beforehand", "first reproduced 16 completed seeds exactly"). The point
  (no selection bias from incomplete toys) is valid and needs only two sentences.
- *Physics version:* "224 of the calibration pseudo-experiments did not complete within batch time
  limits. Because they could in principle change the decisions, we re-ran all of them after the
  decisions. None exceeds the observed statistic (closest: 864.0 against 868.6, GENIE + MEC shape), so the
  decisions are unchanged with the complete ensemble."

**2.46** p. 8.
> "(each power set retains 172 to 199 of its 200 alternatives after time-limit losses)"

- *What reads wrong:* "power set" collides with the mathematical term. "Time-limit losses" is an
  operations detail.
- *Physics version:* "(estimated from 172–199 pseudo-experiments per alternative)".

**2.47** p. 8.
> "This comparison was specified before it was run but after the five-dimensional outcomes were known"

- *Physics version:* "This comparison was defined after the five-dimensional results were known." This is
  acceptable as a disclosure. The "specified before it was run" half adds nothing.

##### Sec. VI D, Hadronic-response condition (pp. 8–9). Mostly fine.

**2.48** p. 9.
> "The null distributions were not regenerated with the variation, and particle-species,
> energy-dependent, and resolution effects, a response difference applied before calibration, and larger
> variations were not tested, so the rejections remain conditional on the simulation's hadronic response."

- *What reads wrong:* a long untested-list sentence. "A response difference applied before calibration"
  is unclear.
- *Physics version:* "This study varies only the overall recoil scale in the data unfolding. It does not
  propagate the variation into the null distributions, and it does not test species-, energy- or
  resolution-dependent mismodelling, or variations larger than ±4%. The rejections therefore assume the
  simulated hadronic response."

##### Sec. VII, Status of a five-dimensional uncertainty (p. 9). Second-worst section.

**2.49** p. 9.
> "A covariance has been built for the five-dimensional central value, and its 42-cell (Eavail, W)
> projection formed; it is separate from the joint-test calibration. It has not met the analysis's
> predeclared qualification criteria, one of which requires a bound fixed before production and can no
> longer be applied to it, and it is used only under a documented exception limited to that one product."

- *What reads wrong:* this is governance language ("predeclared qualification criteria", "documented
  exception limited to that one product", "a bound fixed before production"). The reader cannot tell
  whether the covariance is used anywhere in the paper, or what for.
- *Physics version:* "We have built a covariance for the five-dimensional result, and for its 42-cell
  (Eavail, W) projection. We do not use it in this paper because it depends on the training seed more
  than our pre-set tolerance allows (below)." If it is used somewhere, say where.

**2.50** p. 9.
> "Five of the covariance's 45 uncertainty bands are built at a fixed seed that the variation cannot reach
> (26.0 % of √Tr C); their seed sensitivity, and its effect on the total in either direction, is
> unmeasured."

- *What reads wrong:* "√Tr C" is an unusual summary to put in a physics paper. "That the variation cannot
  reach" is awkward.
- *Physics version:* "Five of the 45 systematic sources, which contribute 26% of the total uncertainty [in
  quadrature-sum terms], were evaluated at a single seed. Their seed dependence is unknown."

**2.51** p. 9.
> "A separate study searched for a definition of a five-dimensional measurement whose total uncertainties
> could be qualified. None of the definitions it considered could meet the precision targets set in
> advance within its rules and computing budget; for its fallback definition, the bounded model-dependence
> component alone exceeded the target total width. The joint tests above came from the same study as a
> separate inference route and produce no new reportable uncertainty."

- *What reads wrong:* the paragraph is project history ("a separate study searched", "within its rules
  and computing budget", "fallback definition", "inference route", "reportable"). It is also the only
  place the paper gets close to the key number, and it does not give it.
- *Physics version:* "We also tried alternative definitions of a five-dimensional measurement (coarser
  binning, [restricted phase space], ...). In all of them the model dependence of the unfolding,
  estimated by [method], was at least X%, which exceeds our target total uncertainty of Y%. We therefore
  report no five-dimensional uncertainties. The hypothesis tests of Sec. VI do not require them."

##### Sec. VIII, Conclusions (pp. 9–10)

**2.52** p. 9.
> "These results differ in standing:"

- *What reads wrong:* "standing" is legal register.
- *Physics version:* "The results are of three kinds:"

**2.53** p. 9.
> "the joint tests are calibrated generator tests that are conditional on six stated conditions and yield
> no new reportable uncertainty."

- *Physics version:* "the hypothesis tests are calibrated with full-chain pseudo-experiments and hold under
  the assumptions of Sec. VI B." Drop "yield no new reportable uncertainty", which is internal.

**2.54** p. 10.
> "Each test also has p < 0.05 in at least one matched coarse projection, so additional discrimination
> from the joint information remains undemonstrated."

- *Physics version:* "Every model is also rejected using a two-dimensional projection alone, so we find
  no evidence that the five-dimensional information adds discriminating power." This is plainer and says
  exactly the same thing.

##### Acknowledgments and Data availability (p. 10)

**2.55** p. 10, Acknowledgments.
> "The analysis code, statistical procedures, computing campaigns, independent recomputations and reviews,
> figures, and manuscript drafts were produced with substantial assistance from AI language-model tools,
> used through the Claude Code and OpenAI Codex command-line agents: Anthropic Claude (Opus 4.7, 4.8, 5,
> and 5.5; Fable 5 and 5.1) and OpenAI GPT models (GPT-5.5, GPT-5.6 Sol and Luna, GPT-6 Astra, and
> GPT-6.1), including those used for independent review. The authors directed this work through written
> specifications fixed before each study. Results were accepted only after verification against committed
> evidence: predeclared criteria, independent recomputation by separately written code (for example, the
> joint-test evaluation and the lost-seed recovery), and independent read-only reviews."

- *What reads wrong:* a disclosure is appropriate. This one is a process statement ("committed evidence",
  "read-only reviews", "lost-seed recovery"), and the eleven-model version list is more than any journal
  asks for.
- *Physics version:* "AI language-model tools (Anthropic Claude and OpenAI GPT models, via Claude Code
  and OpenAI Codex) assisted substantially with the analysis code, statistical procedures, figures and
  drafting. All results were checked by the authors, including independent reimplementation of the key
  statistical calculations. AI tools are not authors; the authors take responsibility for the content."
  Put the version list in the analysis note if it is wanted.

**2.56** p. 10, Data availability.
> "A local release candidate, not yet deposited, of about 16 MB [39] lets a reader, with numpy, scipy, and
> matplotlib only, recompute every p value, decision, robustness label, and power figure of the joint
> tests, the lost-seed resolution, the coarse-projection comparison, and the fine-grid L2 ratios of
> condition (i)"

- *What reads wrong:* "local release candidate, not yet deposited" is a pre-release status. "Robustness
  label" and "lost-seed resolution" are internal.
- *Physics version:* "A data package (about 16 MB, DOI ...) contains the inputs needed to reproduce the
  hypothesis tests of Sec. VI, Figs. 2–4, and the numbers quoted from them, using only numpy, scipy and
  matplotlib."

**2.57** p. 10, Data availability.
> "The candidate predates the change of the two-dimensional central value to LightGBM and carries the
> exact-split curve; Fig. 1 and its numbers were instead regenerated with the release's plotting code,
> extended to draw this analysis's band, from the committed LightGBM values and covariance."

- *What reads wrong:* this is pure release-engineering history.
- *Physics version:* fix the package so that it contains what Fig. 1 shows. Otherwise: "Fig. 1 is not
  reproducible from the package; its inputs are available in Ref. [14]."

**2.58** p. 10, red text.
> "[HOLD: funding and grant acknowledgments]" and "[HOLD: deposit identifier and access route, after the
> separately authorized release decision.]"

- *What reads wrong:* these are draft placeholders, and the second one carries internal governance
  language ("separately authorized release decision"). They must not reach a referee.

##### References (pp. 10–11)

**2.59** The reference titles carry internal vocabulary.
> "[32] Joint five-dimensional generator tests: frozen contract and recorded result, ...
> RECORD-20261005-s5p-joint-5d-inference-result.md"
> "[33] ... report-only sensitivity scan, ... kappa/RECORD-20261008-kappa-breakdown.md"
> "[34] ... report-only recovery of the lost pseudo-experiments ..."
> "[37] ... W2B-REPORT-20261006.md"
> "[39] Article release candidate RC7: sufficient-input replay and figure regeneration (2026)."

- *What reads wrong:* "frozen contract", "report-only", "RC7", "sufficient-input replay" and the
  codenames (s5p, kappa, W2B) read as a lab notebook. [25], [38] and [39] have no locator at all.
- *Physics version:* fold [32]–[35] and [37] into the analysis note [14] as sections or appendices and
  cite them as "Ref. [14], Sec. X". Give [25], [38] and [39] a DOI/URL or remove them.

---

#### 3. Terms used without definition or in a non-standard sense

| Term | Page | Note |
|---|---|---|
| "construction" (the construction, uncertainty construction, central-value construction) | 1, 2, 5, 9 and throughout | Project word for "analysis / method / estimator / covariance". It is never defined and is used for several different things. |
| "qualified five-dimensional measurement", "qualified total uncertainties", "qualification criteria", "could be qualified" | 1, 2, 9 | Internal acceptance-gate sense. It is never defined, and the criteria are never stated. |
| "useful precision" | 1, 2, 10 | No target number is given anywhere. |
| "marginal-normalization checks", "marginal anchors", "projection anchors" | 1, 1, 9 | "Anchor" is non-standard. It is never explained that these are integrals over the added observables compared with the 2D result. |
| "injected-shape closure" | 1, 9 | Close to standard. Acceptable. |
| "background-inclusive tests / pseudo-experiments" | 1, 9 | Coined. It means "closure tests with backgrounds included". |
| "estimator-seed limitations / sensitivity" | 1, 2 | Means dependence on the classifier training random seed. Not said until Sec. VII. |
| "familywise level" | 1, 7 | Standard in statistics, uncommon in neutrino physics. Write "family-wise error rate" once. |
| "matched coarse projections" | 1, 2, 8, 10 | Used three times before it is defined on p. 8. |
| "fine-grid convergence", "fine grid", "twofold-merged grid" | 1, 6, 7 | The fine grid (number of bins, edges) is never specified. |
| "joint information", "tested joint information" | 1, 2, 10 | Non-standard. Means "the full five-dimensional distribution". |
| "nominal-truth bias" | 3 | Means "bias in closure at the nominal simulation". |
| "exact-split scikit-learn estimator" | 3 | ML jargon. Most neutrino physicists will not know what "exact split" means in gradient boosting, as opposed to histogram-based boosting. |
| "matched nominal capacity", "higher-capacity refinement classifier", "refinement capacity" | 2–3 | "Capacity" is undefined (tree depth? number of trees?). |
| "deterministic LightGBM configuration", "deterministic variant" | 3, 5 | Deterministic with respect to what? Seeded? Single-threaded? |
| "classifier refinement" / "background-refinement classifier" | 2, 6 | Only a citation [22] is given. It needs one sentence of explanation. |
| "Missed-event bookkeeping" | 3 | Defined as "an invariant check" and never used again. |
| "standalone covariance" | 3 | Standalone relative to what? |
| "indicative distance" | 3 | Hedge word, not a defined quantity. |
| "reference-free double-ratio construction" | 3–4 | The double ratio is not written down. |
| "completeness division" | 4 | Means the efficiency (acceptance) correction. Write it as such. |
| "rebuilt band", "rescoring", "toy scatter" | 4 | Process words. ("Toy" is fine for physicists.) |
| "pre-registered" | 3 | Clinical-trial vocabulary. Write "defined in advance". |
| "declared conventions" | 5 | Undefined. |
| "Full scientific closeout" | 5 | Project-management term. |
| "population or simultaneous interval coverage" | 5 | "Population coverage" is not a standard physics term. It presumably means bin-by-bin, averaged over bins. |
| "continuous nuisance generator" | 5 | Undefined. |
| "independent-generator samples not already inspected" | 5 | Means blind samples. Say so. |
| "lower-dimensional predecessor" | 5 | Chronological word. |
| "generator-sized change", "test deformation of generator size", "generator-sized shape changes" | 5, 10 | Coined. |
| "largest cells" | 5 | Ambiguous: widest, or most populated? |
| "bias-corrected statistical intervals" | 5 | The method of bias correction is not given. |
| "response-mismatch closure" | 5 | Undefined. Inferred from the Acknowledgments to be a closure with a mismodelled detector response. |
| "supported cells" (109 supported cells) | 6 | Undefined: nonzero prediction? Minimum population? |
| "hybrid null" | 6 | Defined, but the definition ("G's finite-sample fluctuations below that grid") is hard to parse. |
| "metric" for Σ | 6 | A statistician's usage. Physicists say "covariance" or "weight matrix". |
| test "size" | 6 | Statistics term (type-I error rate). Not universal in the field. |
| "claim p value", "claim variants" | 6, 7, 9 | Internal vocabulary. Figure 4 uses "most conservative claim variant". |
| "shifted nulls" | 6, 7, 8 | Understandable, but should be defined as a set. |
| δfine | 6, 7 | "the change of the noise-free unfolded result in the last step of a refinement of the null truth's grid". It is a vector, which becomes clear only from "along δfine" on p. 7. |
| "the data's rounding-level noise" | 6 | A nuisance term for floating-point rounding is unusual and needs one sentence of explanation. |
| "weight-based detector bands", "lateral bands", "linear surrogate" | 6, 7 | "Lateral" is MINERvA-internal (non-reweightable shifts). Non-MINERvA readers will not know it. "Surrogate" needs a definition. |
| "upper-bound shift" | 8 | Undefined until inferred. |
| "decisions determined", "determinate rejections" | 7, 8 | Means the Clopper–Pearson interval lies entirely on one side of the threshold. Say that once. |
| "decision rule", "outside the decision rule" | 7, 8 | Process term, used four times. |
| "robustness shift", "robustness checks", "robustness label" | 7, 8, 10 | Undefined as a set. |
| "power set" | 8 | Collides with the mathematical term. |
| "lost seeds", "time-limit losses", "recovered pseudo-experiments" | 8 | Operations vocabulary. |
| "documented exception" | 9 | Governance term. |
| "throws" | 9 | MINERvA usage, but not universal. |
| "same-seed resampling floor" | 9 | Undefined. |
| "√Tr C" | 9 | Unusual summary. Say what fraction of what. |
| "fallback definition", "inference route", "reportable uncertainty" | 9 | Process terms. |
| "differ in standing" | 9 | Legal register. |
| "GENIE CV" | 2 | In MINERvA usage "CV" (central value) usually means the tuned simulation. Here it labels untuned GENIE. That is confusing to MINERvA readers. "GENIE 2.12.10 (untuned)" would be clearer. |
| "inherited constant of 135 MeV", "uncorrected deviation" | 2 | Inherited from where? Uncorrected relative to what? |
| "the correlated uncertainty" (135 MeV aside) | 2 | Which correlated uncertainty? |
| "earlier production of that release" | 2 | Which production? |
| "frozen contract" | ref. [32] | Not a physics term. |

---

#### 4. Places where hedging hides what was measured or concluded

**4.1 The model dependence, which is the paper's central negative result, is never quantified.**
Abstract, Intro (p. 2), Conclusions (p. 10): "the measured model dependence prevents a qualified
five-dimensional measurement with total uncertainties at useful precision." Sec. VII (p. 9): "the bounded
model-dependence component alone exceeded the target total width." I finished the paper not knowing how
large the model dependence is, how it was measured, what "useful precision" or "the target total width"
is, or which cells drive it. This is the most important missing number.

**4.2 Is the 2D reproduction a success?** p. 3: integrated agreement 1.1%, 95.6% of bins within 10%, RMS
of standardized residuals 0.564, and then "the indicative distance is χ2/ndf = 2.65, a correlated shape
difference." With about 205 dof that χ² is formally enormous. The paper neither embraces it ("there is a
significant shape difference") nor dismisses it with a clear reason until later ("a significance ...
would additionally require the cross-covariance"). The learner dependence (2.64–2.75 for LightGBM against
3.57–3.66 for exact-split) is quoted, but its conclusion is left implicit. I could not tell what the
authors conclude: "consistent", "inconsistent", or "cannot tell".

**4.3 Which statistical uncertainty is in Fig. 1, and was it validated?** p. 4. After reading about a
"first built" band, a "rebuilt band" and a "quoted" band, I learn that the quoted one "Neither it nor the
rebuilt band has been independently tested." The coverage numbers in the paper (91.2%, 97.7%, 78.1%) refer
to bands that are not used. The reader has to work to see that the coverage of the shown band is
simply unknown.

**4.4 The regularization bias magnitude.** p. 5: "the (Eavail, W) cells deviate from it by several
percent in the largest cells and by up to 74 % at high W". Then: "for other fixed generator shapes,
measured with the joint-test estimator, it is 16 % to 31 % in the most affected (Eavail, W) cell and
within the quoted total uncertainty in about half of those cells." I could not tell:
- whether 74% applies to the central-value estimator and 16–31% to the joint-test estimator;
- whether "those cells" means the most affected cell for each of several shapes, or a set of cells;
- how 74% compares with the cell's uncertainty. A 74% bias would make that cell meaningless, and the paper
  does not say so.

**4.5 Floating-point sensitivity.** p. 5: "Input changes at the level of floating-point rounding move the
unfolded values on data by up to a few statistical standard deviations; for the joint-test estimator this
spread lies inside the data-bootstrap statistical uncertainty". By elimination, the shift of "a few
statistical standard deviations" applies to the central-value estimator. That would mean the Figs. 2–3
central values are uncertain at the several-σ level from rounding alone. Is that the claim? Is it in any
uncertainty? Which cells? The hedge "it limits how exactly the central values can be reproduced" turns
what may be a serious problem into a reproducibility footnote.

**4.6 The 5D coverage test outcome.** p. 5: "failed its predeclared criterion at nominal truth and under
an Eavail tilt, so frequentist coverage of the five-dimensional intervals remains unestablished." What
was the coverage, what was the criterion, and was it under- or over-coverage? "Failed" means coverage is
known to be wrong. "Remains unestablished" softens that.

**4.7 The hybrid null and what was actually rejected.** pp. 6–7. The rejected hypothesis is that "the true
cross section equals G on a fine five-dimensional grid, with the MINERvA Tune v1's shape ... below that
grid", and "The rejections carry over from the simulated hybrid null to G itself only if" a condition
holds that has not been shown. So, plainly: is GENIE+MEC (for example) rejected, or is only a
Tune-v1-shaped surrogate of it rejected? The abstract says "reject all five tested predictions". Sec. VI B
says this is true only under an unverified condition. The paper never gives a one-sentence answer.

**4.8 GENIE CV is not rejected by the muon-kinematic projection.** p. 8, Sec. VI D: "the calibrated tests
restricted to the matched (pT, p∥) projection do not reject GENIE 2.12.10 CV (p = 0.48 in total, 0.63 in
shape...)". Sec. VI C says "The comparisons recover the generator disagreements established by the
published two-dimensional measurement". These two statements pull against each other. The published 2D
measurement disfavours GENIE. This analysis's own (pT, p∥) test does not reject GENIE CV, so its rejection
rests on the hadronic axes, which carry no response uncertainty. That is a significant result. It is
spread over two subsections and labelled "a post hoc observation", and I had to assemble it myself.

**4.9 The power study.** p. 8: "two of three alternatives specified in advance are detected in shape with
power 1.0 at the 0.005 level, and the third, a MEC-like (Eavail, W) shape, with 0.23; at the GENIE 2.12.10
null the shape powers are 0.74, 0.02, and 0.00". Two of the three alternatives are never described, and
there is no interpretation. Power 0.00 at the GENIE null means the test cannot see that alternative at all.
That matters for the claim that the method is useful, and it passes without comment.

**4.10 Sec. VII: does a 5D covariance exist and is it used?** p. 9: "A covariance has been built ... It
has not met the analysis's predeclared qualification criteria ... and it is used only under a documented
exception limited to that one product." Used for what? Nothing in Figs. 2–3 uses it (Fig. 3 says
"uncertainties not shown"). I could not tell whether the exception concerns this paper.

**4.11 "Changing the seed moves the projected uncertainty by 6.145 %".** p. 9. Is this the relative change
of the uncertainty (σ changes by 6%), or an absolute 6% of the cross section? "Projected" onto what: the
42-cell (Eavail, W) projection? Is it a median, a maximum, or a norm?

**4.12 Marginal agreement "at the approximately 1–2% level".** p. 5. Agreement of what with what: the
integrated cross section, per-bin values of the 2D projection, or the maximum deviation?

**4.13 The high-W excess.** pp. 5–6. Fig. 2 shows data above Tune v1 by 12–30% at high Eavail and high W.
Then "For GENIE and NuWro the high-W shortfall is about their overall one" and "The high-Eavail, high-W
difference of Fig. 2 is thus a statement relative to the MINERvA Tune v1." Is there a high-W feature in
the data relative to the external generators, or not? The conclusion appears to be "no, beyond
normalization", but it is stated so indirectly that I am not sure.

**4.14 The 135 MeV constant (p. 2).** Is this an intentional convention or a known error? "Inherited" and
"uncorrected" suggest an error. "Has not been compared with the correlated uncertainty" leaves the reader
not knowing whether it matters.

**4.15 The run-period inconsistency (p. 3).** "one period group's unfolded p∥ distribution, taken
relative to its own simulation, differs from that of the earliest periods by a step of about 7 % near
8 GeV/c. The cause is not known". Which period group? Is this a known MINERvA feature (for example, a
known change in the MINOS reconstruction or the beam), or new? A MINERvA reader would want to know whether
it has been seen before.

**4.16 "The approximation in the systematic-universe unfolds" (p. 3, p. 5).** It is listed as excluded
from the uncertainty, but the approximation itself ("approximate the weighting of events that fail
reconstruction") is never described.

---

#### 5. Project-history passages a reader does not need in the body

Each is listed with a suggested disposition. Items marked **(keep, compress)** are genuine
disclosures that affect interpretation and should stay in one sentence.

1. p. 2, Sec. II: "The files analysed are an earlier production of that release; their names and sizes
   are recorded for reproduction". Name the production. Move checksums to Data availability.
2. p. 2, Sec. II: "an inherited constant of 135 MeV ... (an uncorrected deviation ...)". Recast as a
   convention, with its size.
3. p. 2, Sec. II: "a corrected flux sampling". Drop "corrected".
4. p. 3, Sec. III: "An exact-split scikit-learn estimator, the original two-dimensional choice, is
   retained as a cross-check". Drop "the original two-dimensional choice".
5. p. 3, Sec. III: "selected before the joint-test design was fixed". Drop.
6. p. 3, Sec. IV A: "The quoted central value was changed from exact-split to LightGBM after both
   comparisons were known". **(keep, compress)** It is an analysis choice made after seeing the result.
7. p. 3, Sec. IV B: "the noise of an earlier ten-seed training scan". Drop "earlier".
8. pp. 3–4, Sec. IV B: the whole "statistical block, as first built, undercovered ... rebuilt band.
   Rescoring the same pseudo-experiments against the rebuilt band, which is post hoc and partly circular
   ..." sequence. Replace with a statement about the band actually used ("coverage not tested"), with at
   most one sentence on the earlier test, or move it to the note.
9. pp. 4–5, Sec. IV B: "An assessment of the saved products found construction defects in the earlier
   budget, among them a truth-input mismatch ... [25]; the quoted covariance is free of both." Delete.
10. p. 5, Sec. IV B: "Full scientific closeout is not achieved". Delete.
11. p. 5, Sec. IV B: "Validated total intervals over the full reporting domain require new inputs:
    ...". This is a work plan. Shorten to one "future work" clause, or move it to the Conclusions.
12. p. 5, Sec. IV C: "lower-dimensional predecessor", and "as first measured with a deterministic variant".
    Drop the chronological words.
13. p. 5, Sec. V: "(same-sample ratios computed with GENIE before its flux correction)". Recast without
    "before".
14. p. 7, Sec. VI A: "Two data-informed elements are disclosed: reviewers of the design had seen
    descriptive per-cell residuals before it was fixed, and a bounded extension of the production budget
    ... was decided while job-status outputs exposed observed claim p values". **(keep, compress)**
15. p. 7, Sec. VI A: "An independent recomputation with separately written code agrees with the
    production evaluation in all 1379 compared quantities." Compress to one clause.
16. p. 7, Sec. VI A: "Calibration proceeded in batches of 200 pseudo-experiments per null, to at most
    1999, until both of a null's decisions were determined." **(keep)** This is a stopping rule and is
    legitimately methodological. Fine as it stands.
17. p. 7, Sec. VI B: "numbered as in the specification fixed in advance [32]". Drop.
18. p. 7, Sec. VI B (i): "Before any result, the claim variants were set from an assumed extrapolation: if
    the step kept shrinking geometrically at a rate taken from the design review, whose calculation is not
    recorded". State the rate and its origin, or say it was an assumption. Drop "design review" and "not
    recorded".
19. p. 8, Sec. VI C: "specified before it ran but run after the decisions and outside the decision rule".
    Drop. If needed, say "a post-hoc robustness scan".
20. p. 8, Sec. VI C: the lost-pseudo-experiment paragraph ("Computing-job time limits interrupted ... a
    procedure fixed and independently reviewed beforehand [34], which first reproduced 16 completed seeds
    exactly ..."). **(keep, compress)** to two sentences.
21. p. 8, Sec. VI C: "(each power set retains 172 to 199 of its 200 alternatives after time-limit
    losses)". Compress.
22. p. 8, Sec. VI C: "This comparison was specified before it was run but after the five-dimensional
    outcomes were known". **(keep, compress)** "defined after the 5D results were known".
23. p. 9, Sec. VII, para. 1: "It has not met the analysis's predeclared qualification criteria, one of
    which requires a bound fixed before production and can no longer be applied to it, and it is used
    only under a documented exception limited to that one product." Delete the governance and keep the
    physics reason (seed dependence).
24. p. 9, Sec. VII: the seed-convergence numbers ("6.02 %, 6.02 %, and 6.145 % at 40, 80, and 160
    throws ... a same-seed resampling floor fell from 20.91 % to 7.57 %"). This belongs in the note. One
    sentence in the body is enough.
25. p. 9, Sec. VII, para. 2: "A separate study searched for a definition ... within its rules and
    computing budget; for its fallback definition ... The joint tests above came from the same study as a
    separate inference route". Replace with a statement of what was tried and the numbers.
26. p. 10, Acknowledgments: "The authors directed this work through written specifications fixed before
    each study. Results were accepted only after verification against committed evidence: ...". Shorten.
27. p. 10, Data availability: "A local release candidate, not yet deposited", and "The candidate predates
    the change of the two-dimensional central value to LightGBM and carries the exact-split curve; Fig. 1
    and its numbers were instead regenerated ...". Fix the package, then drop this.
28. p. 10: both red "[HOLD: ...]" placeholders.
29. References [25], [32]–[35], [37]–[39]: titles such as "frozen contract and recorded result",
    "report-only sensitivity scan", "report-only recovery of the lost pseudo-experiments", "Article
    release candidate RC7", and file paths with codenames. Consolidate into the analysis note.

---

#### 6. Wording that lowered my trust more than the content warrants, and where plainness would overclaim

##### 6a. Wording that made me trust the result less than its content warrants

- **"a rate taken from the design review, whose calculation is not recorded"** (p. 7). This is the single
  worst phrase for credibility. It tells a referee that a number entering the decision rule has no
  documented derivation. If the rate is an assumption, call it an assumption and give its value. That
  is honest and far less alarming.
- **"Full scientific closeout is not achieved"** (p. 5). It sounds like an admission that the paper is
  unfinished. The content (no coverage validation of the 2D covariance) is a normal limitation that many
  published unfolding results share.
- **"An assessment of the saved products found construction defects in the earlier budget"** (pp. 4–5).
  It advertises bugs in something not shown and invites the reader to ask what other defects exist. The
  content (the quoted covariance is free of them) is reassuring, but the sentence leaves the reader
  worried.
- **The statistical-block story** (p. 4): "as first built, undercovered", "rebuilt band", "post hoc and
  partly circular", "for reasons not established", "Neither it nor the rebuilt band has been
  independently tested". The reader is led through a failure, a fix that over-corrects for unknown reasons,
  and an untested replacement. A plain "the coverage of the statistical band has not been tested" conveys
  the same limitation with far less alarm.
- **"for a reason the release does not establish"** (p. 3), "The cause is not known" (p. 3), "for
  reasons not established" (p. 4), "unmeasured" (pp. 7, 8, 9, four times), "uncomputed" (p. 5). Each is
  fine alone. Together they make the analysis sound out of control. Some of them (the 0.26% flux
  difference) are minor and could simply be stated.
- **"used only under a documented exception limited to that one product"** (p. 9). It sounds like
  something was waived. Readers of a physics paper do not know the project's gates, so "exception"
  suggests a rule was bent.
- **The red "[HOLD: ...]" markers and "not yet deposited"** (p. 10). They make the paper look
  unfinished.
- **The eleven-model AI list and "Results were accepted only after verification against committed
  evidence"** (p. 10). The verification statement is meant to reassure. Combined with the process register
  of the body, it reinforces the impression that the paper was written by a pipeline. A shorter disclosure
  would raise trust.
- **Repetition of the limitation list** (abstract, intro twice, Sec. IV C, Sec. VII, Conclusions). By the
  fifth repetition the reader suspects the limitations are the main result. They are not: the 2D
  reproduction, the Eavail/q3/W central-value features and the calibrated-test methodology are real
  contributions. The abstract does not state them in numbers.
- **Over-precise numbers**: "6.145 %", "20.91 % to 7.57 %", "1379 compared quantities", "0.684 %", "5.25
  δfine ... (5.17 δfine ...)". This precision reads as instrument output, not physics judgment. Rounding
  would read as more confident and lose nothing.
- **"Input changes at the level of floating-point rounding move the unfolded values on data by up to a
  few statistical standard deviations"** (p. 5). If this is as serious as it sounds, it needs a plain,
  prominent statement and a number. If it is not (for example, if it is confined to sparsely populated
  overflow cells), saying where it occurs would restore confidence. As written, the reader assumes the
  worst.

##### 6b. Places where a plainer version would risk overclaiming (keep these hedges in some form)

- **"All five generators are rejected."** Plain, but it would overclaim. Three qualifications must
  survive simplification. (1) The rejected hypothesis is the hybrid null, which equals G only if the
  sub-fine-grid shape does not matter (Sec. VI B (i)). (2) There is no recoil-response uncertainty, and
  GENIE CV is not rejected by the muon-kinematic projection alone (Sec. VI D). (3) The coarse projections
  already reject, so the 5D information adds nothing demonstrated. A plain abstract sentence that keeps
  all three: "All five predictions are rejected at 5% family-wise significance, assuming the simulated
  hadronic-energy response and a model-construction approximation (Sec. VI B). Two-dimensional
  projections already give the same rejections."
- **The 2D reproduction as "agreement".** Dropping χ²/ndf = 2.65 and the learner dependence (2.6–3.7)
  would overclaim. Keep both, with the reason the χ² is not a significance.
- **Calling the 3–5D results "measurements" or "cross sections".** They are central values without
  validated uncertainties, with up to 4% background bias and 16–74% regularization bias in some cells.
  Plain wording must keep "no uncertainties are reported for the three- to five-dimensional results, and
  these comparisons are descriptive."
- **The high-Eavail, high-W excess over Tune v1 (Fig. 2).** Presenting it as a physics finding would
  overclaim. It lies where the regularization bias is largest, it has no uncertainty, and relative to
  external generators it looks like normalization. The paper's caveat is correct. It only needs plainer
  phrasing.
- **"The Valencia 2p2h fills 52% of the low-Eavail gap" and "within 10% of the published low-recoil
  measurement".** These are fine as written. The paper's caveat about the different Eavail definition
  (11% migration) must stay.
- **The uncertainty band in Fig. 1.** The list of what is not included (learner dependence, the
  systematic-universe approximation, model/regularization dependence) must stay. Without it the band
  would look like a complete total uncertainty. The caption's note that "their overlap is not a
  compatibility test" is a good example of a necessary hedge written plainly.
- **The lost pseudo-experiments.** Compressing is safe, because the content is "no decision changes".
  The fact that they were re-run, and that the worst case would have flipped every decision, should
  remain in one clause.
- **The post-hoc disclosures** (central value chosen after both χ² values were known; design fixed after
  residuals were seen; budget extended after p values were visible; coarse-projection test defined after
  the 5D results). These protect against an accusation of p-hacking and should stay, one sentence each,
  in plain words.
- **The power result** (power 0.00–0.23 for some alternatives). If simplified to "the tests have high
  power", that would overclaim. Keep the numbers, and add one sentence saying what they mean.

---

## R2. Baseline reader, primer (PDF at 28d28626) — `reader-baseline-primer.md` (sha256 `7b25ddc4406db3ce…`)

### Reader baseline: `main_primer.pdf` (12 pages)

Who is reading: a physicist from outside neutrino physics (condensed-matter or astrophysics
graduate student, or a science journalist who knows physics). This is my first look at the
project. I read only the PDF. Quotes are copied from the rendered pages, so a ligature or hyphen
may differ from the source.

---

#### 1. Overall verdict

**Pages 1-2 work well. Most of page 3 onward does not work for me as a primer.** The opening is
good science writing. It covers what a neutrino is, what a cross section is, unfolding as
deblurring a photograph, the migration matrix and why it does not scale, and OmniFold as
"learn a weight per simulated event". After page 2 I could explain the method to a colleague.
The "trust check" (p. 5), "A new puzzle for the tuned simulation" (pp. 7-8) and the Figure 3
and 4 captions are also clear, concrete and honest. The final paragraph on the extended signal
definition (p. 10) is short and readable.

**I get lost at the start of Section 3 (p. 3), and mostly stay lost until p. 5.** Section 3 is
headed "What we found", but it opens with roughly a page and a half of validation status,
error-budget history, seed sensitivity, detector-systematic bookkeeping and "follow-up study"
results. This all comes before I have been told what was found. I was handed caveats on results
I had not yet seen: "the two-variable central value", "the higher-dimensional central values",
"the generator tests", "PET". The writing has the cadence of an internal review record. Many
sentences exist to say what something does *not* establish. Several refer back to the
document's own wording ("Two newer end-to-end tests qualify 'pass the stated validation
tests'"). I could not rebuild the logic of pp. 3-4 on a first read, and I gave up trying on the
second.

**The register gets heavy again on pp. 8-10.** These pages cover the joint five-simulation test,
the kappa scan and the whole PET section. Here the vocabulary is the project's own:
NO_ELIGIBLE_DESIGN, "frozen point rule", "six-member interval test", "development tilt",
"finalists", GBDT/LightGBM/tree learner. The PET material reads like a summary of a lab
notebook's decision log, not like an explanation.

**The author's worry is justified, but only for part of the document.** The plain-explanation
voice exists, and it is good, on pp. 1-2, 5, 6-8 and the end of 10. The defensive,
process-record voice dominates pp. 3-4 and 8-10. Most of the damage could be undone by
**moving material** rather than deleting disclosures:

- Put the trust check (p. 5) first in Section 3.
- Then the multi-quantity results (pp. 6-8).
- Then gather the five-quantity uncertainty caveats into one plainly written "What we cannot
  yet claim" subsection *after* the reader has seen the results.

Two more points matter. The headline "What we found" never gets a one-paragraph answer. And the
takeaway (p. 11) drops every caveat the body labors over, so the document whipsaws between
over-defending and summarizing cleanly.

---

#### 2. Passages that read as jargon or internal register

Each entry gives the page, the exact quote, what reads wrong, and a plainer version that keeps
the same content and limitations.

**2.1 (p. 3, opening of Section 3)**

> "The headline results have different levels of validation. The two-variable central value
> reproduces the published measurement, and its error budget was built with the same tree
> learner. The quoted statistical band awaits an independent coverage test. The
> higher-dimensional central values pass particular recovery checks; adoption of their
> covariance under an exception does not certify their intervals. The generator tests below are
> a separate inference, and PET remains method development. None of these statuses supplies
> another's missing validation."

- **What reads wrong:**
  - This is a status table written as prose, placed before any result.
  - "the same tree learner" assumes I know there are several learners.
  - "adoption of their covariance under an exception" and "certify" are governance language.
  - "None of these statuses supplies another's missing validation" is a rule for internal
    reviewers, not for readers.
- **Plainer:** "We report three kinds of result, and they are not equally well tested. (1) Our
  two-variable measurement reproduces MINERvA's published one, and we built its error bars
  independently. We have not yet checked whether its statistical error bars are the right size.
  (2) Our measurements of five variables at once pass the specific recovery tests described
  below. We show their central values only, because we have not shown that their error bars are
  trustworthy. (3) Separately, we test five simulations against the data, and we try a second
  type of neural network (PET) that is still under development. Passing one of these checks
  says nothing about the others."

**2.2 (p. 3)**

> "Selection and classifier inputs are also distinct. Every real-data route here requires a
> reconstructed muon matched to MINOS. The scalar classifiers use its momentum; the historical
> recoil-only PET classifier does not, even though the muon is needed to select the event.
> Full-event PET adds muon features. Removing truth-muon cuts enlarges the population being
> estimated without adding selected observations. The technical note's selection-versus-features
> table gives each route; PET design studies use signal-only simulation banks."

- **What reads wrong:**
  - "route", "scalar classifiers", "historical recoil-only PET classifier", "Full-event PET",
    "truth-muon cuts" and "signal-only simulation banks" are all undefined here. PET is not
    defined anywhere.
  - The paragraph points to a document I do not have ("The technical note's
    selection-versus-features table").
  - I cannot tell why this belongs in "The method, in plain language" at all.
- **Plainer:** "One distinction matters later. Which events we *keep* and what information the
  learner *sees* are separate choices. Every analysis here keeps only events in which the muon
  was tracked into MINOS, a second detector behind MINERvA that measures muon momentum. Most of
  our learners are given the muon's momentum. One experimental neural network (PET, described in
  Section 3) was originally shown only the hadronic debris, not the muon. Loosening the cuts on
  the *true* muon (Section 3, last part) widens the population we are estimating, but it does not
  give us any extra recorded events."

**2.3 (p. 3)**

> "An assessment of the saved products found construction defects in an earlier version of the
> two-variable error budget [1]. The quoted budget was rebuilt without them: its systematic
> sweep and that sweep's reference use the same truth inputs, a duplicated pion-model variation
> is counted once, the background simulation's statistics are propagated, and the detector
> variations that change the event selection come from complete re-runs. Some effects are in no
> part of it: [...]"

- **What reads wrong:**
  - This is a changelog. "saved products", "construction defects", "systematic sweep", "that
    sweep's reference" and "complete re-runs" are terms from the project's workflow.
  - "Some effects are in no part of it" is ungrammatical-feeling and hard to parse.
  - The list of fixed bugs is not something I need in order to understand the result.
  - The list of *still-missing* effects is something I do need, and it is buried.
- **Plainer:** "An internal review found bookkeeping errors in an earlier version of the
  two-variable error bars, and they have been fixed [1]. Three effects are still **not**
  included in the error bars:
  - an approximation in how we weight events the detector failed to reconstruct;
  - the roughly 1% difference between two software implementations of the learner;
  - the dependence on which simulation the unfolding starts from."

  (The list of fixed defects can go to the technical note.)

**2.4 (p. 3)**

> "Checking widths by splitting the existing simulation can test precision conditional on that
> sample, but cannot establish coverage across independently generated samples. Validated error
> bars would need new inputs: independent full-size simulation, a validated way to generate
> nuisance variations, and independent-generator samples not already inspected. No coverage claim
> is made."

- **What reads wrong:** It is a correct statistical point, but it is written for a referee.
  "conditional on that sample", "coverage", "nuisance variations" and "not already inspected" are
  not explained.
- **Plainer:** "To check whether error bars are the right size, you rerun the analysis on many
  fake experiments and count how often the bars contain the known answer. We can only make those
  fake experiments by reshuffling the one simulation we have. That tells us how much the answer
  wobbles *for that simulation*, not whether the bars would be right for a genuinely different
  one. A real test needs new, independent simulation that we have not yet looked at. Until then
  we make no claim that these error bars have the stated statistical meaning."

**2.5 (p. 3)**

> "A five-quantity uncertainty has now been adopted under a documented exception, and the
> two-quantity (E_avail, W) version of it has been built"

- **What reads wrong:** "adopted under a documented exception" is governance vocabulary: an
  exception to which rule, and documented where? "has now been" signals project history.
- **Plainer:** "We have built an uncertainty estimate for the five-variable result, although it
  does not meet our own original acceptance standard (explained next)."

**2.6 (pp. 3-4, the seed paragraph)**

> "Change that seed, leaving everything else alone, and the uncertainty we report on the
> projected result shifts by about 6.145 % (measured on two test versions of it built for
> exactly this comparison, not on the adopted version itself)"

- **What reads wrong:**
  - The reasoning in this paragraph is actually good: the shift does not shrink with more
    variations, so it is not noise. It is the clearest argument on pp. 3-4.
  - But "6.145 %" quotes four significant figures for a seed-to-seed shift, which reads as false
    precision.
  - "projected result" is undefined. It presumably means the five-variable result collapsed to
    two variables.
  - The parenthetical makes me wonder whether the adopted version is any different.
- **Plainer:** "...the size of the error bar on the two-variable view of the five-variable result
  changes by about 6% (measured on two test builds made for this comparison, not on the final
  version)."

**2.7 (p. 4)**

> "Two further facts qualify it: five of the forty-five uncertainty components are built in a way
> the seed cannot reach at all, so the figure above is the effect of the other forty and we have
> not measured which way those five would move it"

- **What reads wrong:** "the figure above" makes me look for a figure, but there is none; it
  means "the 6% number". "the seed cannot reach" is a vivid phrase but it is opaque.
- **Plainer:** "Two caveats. Five of the 45 uncertainty components do not involve the learner,
  so the seed cannot change them. The 6% comes from the other 40, and we do not know whether
  those five would increase or decrease it."

**2.8 (p. 4)**

> "Four others — the MINOS efficiency and three describing how hadrons interact in the detector —
> are applied instead by reweighting the simulated events, so there is nothing to rebuild. That
> tells us why those four sit outside the rebuild; it does not by itself show that the set of
> hadronic-response variations we include is the complete set this measurement needs."

- **What reads wrong:** The paragraph explains why four items are handled differently, then
  stacks a negation ("it does not by itself show that...") to head off an objection I had not
  raised. "MINOS efficiency" is undefined.
- **Plainer:** "Four others are handled by reweighting the simulation instead of re-running it:
  the efficiency of the downstream muon detector (MINOS), and three effects of how hadrons
  interact in the detector. That is a standard technique. We have not, however, checked that
  these three hadron effects are the only ones that matter here."

**2.9 (p. 4)**

> "Two newer end-to-end tests qualify "pass the stated validation tests"."

- **What reads wrong:** The document is annotating its own earlier sentence. This is an
  edit-history artifact ("newer"), and it is the clearest example of process-record register in
  the primer.
- **Plainer:** "Two more realistic tests show where the five-variable method falls short."

**2.10 (p. 4)**

> "(One of the two predictions behind that pattern was later found to have been made with a
> wrongly sampled beam spectrum, so the pattern is a test of a chosen size, not a measured
> difference between generators.)"

- **What reads wrong:** This is history ("was later found"). The conclusion is the useful part
  and it is fine.
- **Plainer:** "(The pattern is a deliberately chosen distortion of realistic size. It should not
  be read as the true difference between the two generators, because one input to it had a
  known error.)"

**2.11 (p. 4, the follow-up study paragraph)**

> "A later paired study found that the candidate's bootstrap already carries this rounding
> variability; this does not qualify the uncertainty attached to the published result or reverse
> the failed stability test."

- **What reads wrong:**
  - "paired study", "the candidate", "bootstrap" and "the failed stability test" are all
    undefined.
  - No stability test has been described as failing anywhere before this point. The only
    stability-like item is the seed shift, and that was never called a "stability test".
  - "this does not qualify ... or reverse ..." is a double defensive negation.
- **Plainer:** "The method's own resampling estimate of the statistical error already includes
  this rounding sensitivity. That does not change our conclusion that the five-variable error bar
  is sensitive to the seed and to rounding beyond what we can accept."

**2.12 (p. 4)**

> "Longer runs sometimes improve recovery and sometimes leave a persistent residual, but their
> repeat variability was not measured at the same settings. We therefore have not established a
> tradeoff between bias and variability. Combining cells changes what is measured, and changing
> the starting model does not give a guaranteed error bound. The one direct test of whether
> five-quantity statistical error bars contain the truth as often as stated, made on a variant of
> the method, failed, so we claim no such coverage. Nothing new was adopted."

- **What reads wrong:**
  - Six short sentences, each of which forecloses a remedy the reader has not heard proposed:
    longer runs, merging cells, varying the prior.
  - "Nothing new was adopted" is pure decision-log language.
- **Plainer:** "We tried the obvious fixes. Running longer helps in some cells but not others.
  Merging cells changes what is being measured. Varying the starting simulation gives no
  guaranteed bound. None of them solves the problem. The one direct test of whether the
  five-variable statistical error bars are the right size failed (it was done on a close variant
  of the method). So we do not claim those bars have their stated meaning, and we have not
  adopted a replacement."

**2.13 (p. 4-5)**

> "The two-dimensional trust check is unaffected by these five-quantity findings and retains its
> independently constructed uncertainty, with the qualification about learner dependence
> explained below."

- **What reads wrong:** It is a forward reference to a "trust check" that I have not been shown
  yet. This is a symptom of the ordering problem.
- **Fix:** Put the trust check first, and delete this sentence.

**2.14 (pp. 8-9, the joint test)**

> "Each hypothesis uses that generator's rates on a finite truth grid and Tune v1's shapes inside
> each cell. The unfolding still learns from unbinned events; the grid specifies the hypothesis
> and the quantities tested."

and

> "This is a test of the simulations under six conditions: unresolved structure below the fine
> grid; the stated detector-uncertainty model, which lacks a calorimetric recoil-response band;
> the stated interaction-model variations, including clipped negative weights; a bounded
> calibration shift from using half the simulation in pseudo-experiments and all of it for data;
> the generator energy domains; and finite generator-sample statistics."

- **What reads wrong:**
  - The first quote has the substance right, but "finite truth grid" and "Tune v1's shapes"
    need explanation.
  - The six-condition list is unreadable to me. Every item ("calorimetric recoil-response band",
    "clipped negative weights", "bounded calibration shift", "generator energy domains") is
    specialist or internal.
- **Plainer:** "Strictly, each test asks whether the data agree with a simulation's *predicted
  rate in each cell*, with the shape inside each cell borrowed from MINERvA's tuned simulation.
  The verdict holds under six stated assumptions:
  - differences finer than our grid are ignored;
  - our detector-uncertainty model, which omits one known effect on how the detector measures
    hadronic energy, is taken as correct;
  - our list of physics-model variations is complete;
  - a small, bounded bias from how the fake experiments were built is accepted;
  - each simulation is used only over the energy range it covers;
  - each simulation's finite sample size is accounted for.

  Details are in the analysis note."

**2.15 (p. 9, the kappa paragraph)**

> "The sensitivity multiplier κ counts multiples of the last measured grid-refinement shift; it
> is not a confidence level. The frozen tests first lose a determinate rejection near κ = 5.26, or
> 5.17 when recovered experiments are included. This is an ambiguous decision at that point, not
> a determinate non-rejection, and the one-direction scan does not bound the unmeasured
> below-grid error."

- **What reads wrong:**
  - This is the most opaque paragraph in the primer. κ is introduced and defined in the same
    breath.
  - "frozen tests", "determinate rejection", "recovered experiments" and "one-direction scan" are
    undefined.
  - I cannot tell whether this is good or bad news.
- **Plainer:** "How robust is the rejection? We can only estimate the error from ignoring
  differences finer than our grid. So we asked how large that error would have to be to overturn
  the result. The rejections survive until it is about five times the largest shift we actually
  measured when we made the grid finer. Beyond that, the test becomes inconclusive (it does not
  start favoring the simulations). This scan does not tell us how large that error really is."

**2.16 (p. 9, PET section)**

> "Completed simulation studies then improved PET's recovery of deliberately changed truth
> distributions. More iterations, detector summaries and a revised missed-event treatment helped,
> but none of the improvement study's frozen ten-iteration candidates qualified for coverage
> testing."

> "Better recovery did not yield a qualified design. The final outcome is NO_ELIGIBLE_DESIGN. One
> finalist failed a robustness threshold by the frozen point rule; the statistical comparison did
> not establish which finalist was more robust, and its coverage was never measured."

> "The diagnosis concerns the development tilt at study scale; generator-case and data-scale
> coverage of the six-fit average remain unmeasured."

- **What reads wrong:**
  - The monospace `NO_ELIGIBLE_DESIGN` is a literal internal status code.
  - "frozen ten-iteration candidates", "qualified for coverage testing", "finalist", "frozen point
    rule", "six-member interval test", "development tilt", "study scale", "generator-case and
    data-scale coverage" and "six-fit average" are all project-process terms.
  - The narrative is a sequence of study rounds ("improvement study", "final-design study",
    "saved outputs now give a partial explanation", "A subsequent exploratory comparison"). That
    is a history, not an explanation.
- **Plainer:** "Tuning made PET much better at recovering a deliberately distorted energy
  distribution: about 90% recovered, against 31% for the original version. But neither of the
  two best versions met all the criteria we fixed in advance. One failed a robustness test. The
  other got central values right, but its error bars were miscalibrated: too wide on average (90%
  of 68% intervals contained the truth) and too narrow where the detector sees few events (only
  26%). So we have not adopted PET for any result. We have a partial explanation for the error-bar
  problem. The bars average six fits, which washes out some of the variation they are meant to
  capture. But a simple correction does not fix it."

**2.17 (p. 10)**

> "The comparator differs from the production LightGBM studied earlier. Its uncertainty was not
> tested here; no precision comparison or ranking of the PET finalists follows. All results
> condition on the study's finite simulation banks and event scale."

- **What reads wrong:**
  - "the production LightGBM studied earlier" is never introduced.
  - The same learner has been called "tree learner" (p. 3), "tree-learner implementations"
    (p. 3), "scalar tree-based OmniFold" (p. 9), "the tree method" (p. 9), "GBDT" (Fig. 5) and
    "LightGBM" (p. 10). I was not sure these were the same thing.
- **Plainer:** "(The tree-based learner in this comparison is configured slightly differently
  from the one used for our main results. Neither learner's error bars were compared, so this
  does not show which is more precise.)"

**2.18 (p. 10)**

> "For the three generator reweightings, a saved-output diagnosis finds both underfitting at the
> detector step and weak extrapolation to missed events [7]. Exact distortion weights recover the
> changes well on those same samples."

- **What reads wrong:** "saved-output diagnosis", "detector step" (OmniFold's step 1 is never
  named as such) and "Exact distortion weights" are internal terms.
- **Plainer:** "PET does worse on the three generator-based tests for two reasons. It does not
  fully learn the detector-level differences, and it extrapolates poorly to events the detector
  missed. When we instead hand it the exact correct weights, the samples themselves recover fine.
  So the problem is in the learning, not in the test samples."

**2.19 (p. 2, the subsection heading "What the checks tell us" and Table 1)**

- **What reads wrong:**
  - The table's third column, "What it cannot establish", is a defensive frame. It is in fact
    useful, but it sets a negative tone before any result.
  - The caption defines "Bias", which the table does not use.
  - The sentence "A finite learner and a finite number of iterations can also leave an
    approximation error, even with the correct response" is fine, but "finite learner" is odd
    phrasing.
- **Suggestion:** Keep the table, which is a genuinely good idea. Retitle the column "What
  passing does not prove", and give each row one plain example.

---

#### 3. Terms used without explanation

| Term (exact) | Page | Note |
|---|---|---|
| "signal definition", "muon kinematic cuts" | 1 (abstract) | The abstract's last two sentences are opaque without these |
| "detector-supported and simulation-dominated regions" | 1 | Explained only implicitly on p. 10 |
| "MINOS" | 3, 4, 10 | Never said to be a separate downstream detector |
| "PET" | 3 onward | Never expanded. The term "point-cloud transformer" first appears on p. 9 and is not linked to the acronym |
| "scalar classifiers", "recoil-only", "Full-event PET" | 3 | |
| "simulation banks", "signal-only simulation banks" | 3, 10 | |
| "the technical note" / "the analysis note" | 3, 9 | I don't have it. Is it the same document? |
| "tree learner", "tree-learner implementations", "GBDT", "LightGBM", "scalar tree-based OmniFold" | 3, 5, 9, 10 | Five names; no definition of gradient-boosted trees |
| "coverage", "coverage test" | 2 (table), 3, 4, 5, 9 | The table gives a one-line definition; it needs a plain sentence |
| "covariance" | 3 | |
| "systematic sweep", "pion-model variation", "nuisance variations" | 3 | |
| "projected result" | 4 | Presumably the 5D result projected to 2D |
| "central values" | 3 onward | Defined only by contrast with uncertainties |
| "bootstrap", "paired study", "the candidate" | 4 | |
| "highest-W cells", "W", "E_avail", "q3" | 3-4 before definition on p. 6 | Used on pp. 3-4 before they are defined on p. 6 |
| "helper classifier" | 4 | |
| "Tune v1", "MINERvA Tune v1", "GENIE-CV", "GENIE+MEC", "MEC" | 6-8 | "MEC" is never expanded. 2p2h is explained, but MEC is not linked to it |
| "GENIE", "NuWro", "GiBUU" | 7 | Introduced only as "simulation predictions"; a phrase like "the three standard neutrino-interaction simulation programs" would help |
| "deep-inelastic" | 7 | Briefly glossed; fine |
| "maximal common grid" | 7 | |
| "pseudo-experiments" | 8 | Inferable from context |
| "combined 5% error level", "ten hypotheses" | 8 | 5 generators x 2 tests = 10 is not stated |
| "κ", "frozen tests", "determinate rejection", "recovered experiments", "one-direction scan", "below-grid error" | 9 | |
| "calorimetric recoil-response band", "clipped negative weights" | 9 | |
| "NO_ELIGIBLE_DESIGN", "finalist", "frozen point rule", "six-member interval test", "development tilt", "acceptance" | 9 | "low-acceptance" is used without definition |
| "additive variance model" | 9 | |
| "FB draw", "H2S1T24", "L128S1T24", "k=5/k=4/k=7" | 10 (Fig. 5) | Internal configuration labels in a figure |
| "σ_ext" | 10 | |
| "anchor ratio", "prior-swap ratio", "prior-dominated" | 11 (Fig. 6) | "prior" is defined on p. 2; "prior-swap" is guessable |
| "POT" | 6, 7, 11 (figure headers) | Protons on target; fine to leave in a figure stamp |

---

#### 4. Places where hedging hides what was found

1. **Section 3 never states its findings up front (p. 3).** "The headline results have different
   levels of validation" is the first sentence under "What we found". After reading the whole
   document, I would summarize the findings as:
   - (a) the method reproduces the published 2D result to about 1% in total rate;
   - (b) five-variable unfolding confirms the known low-recoil shortfall;
   - (c) it finds a new data excess over the tuned simulation at high E_avail and high W;
   - (d) all five simulations fail a joint test;
   - (e) the five-variable error bars are not yet trustworthy;
   - (f) the PET neural network did not produce a usable version.

   None of these is stated as a list anywhere. A five-bullet "What we found" box at the top of
   Section 3 would fix more than any sentence-level edit.

2. **Is the five-variable uncertainty usable or not? (pp. 3-4)** I read "A five-quantity
   uncertainty has now been adopted", then that it shifts 6% with the seed (above the 5%
   tolerance), then "Neither effect is in the quoted uncertainty yet", then "16 % to 31 % in the
   worst cell and smaller than the quoted uncertainty in about half of the (E_avail, W) cells",
   then "we claim no such coverage. Nothing new was adopted." I still do not know the bottom
   line. My best guess: an uncertainty exists and is adopted, it is probably too small in about
   half the cells for some realistic model changes, and it is not shown in any plot. That should
   be said in one sentence.

3. **"16 % to 31 % in the worst cell and smaller than the quoted uncertainty in about half of the
   (E_avail, W) cells" (p. 4).** The grammar hides the finding. "Smaller than the quoted
   uncertainty in about half" means the bias is *covered* in half the cells and *not covered* in
   the other half. The finding is the uncovered half, so say that half.

4. **"The higher-dimensional central values pass particular recovery checks" (p. 3).** Which
   checks? This sentence asserts a pass without saying what passed. It is the opposite of hedging
   in tone, but it hides the content.

5. **The joint generator test (p. 8).** The finding, "all ten hypotheses are rejected", sits
   mid-paragraph. Then the robustness discussion follows in language I cannot decode (κ, "frozen
   tests", "ambiguous decision"), so I end the section unsure whether to believe the rejection.
   The careful content seems to be "robust up to about 5x the measured grid effect", which is
   actually reassuring, but it reads as a retreat.

6. **The low-recoil result (p. 7).** "These comparisons support the two-nucleon contribution
   without uniquely establishing the cause" is fine. But the last sentence, "our central values
   lie 9.2 % and 6.3 % above it on the maximal common grid", leaves me unsure whether a 6-9%
   excess over MINERvA's own dedicated measurement is a problem, a tension or expected. The paper
   does not say.

7. **PET (p. 9).** The finding, that PET is not usable yet, is expressed as "The final outcome is
   NO_ELIGIBLE_DESIGN." The real content (which criterion failed, by how much) follows, but the
   headline is a status code.

---

#### 5. Project-history passages the reader does not need

The *conclusions* of these passages should stay. The narrative of how the project got there can
go to the technical note.

- **p. 3:** "An assessment of the saved products found construction defects in an earlier
  version of the two-variable error budget [1]. The quoted budget was rebuilt without them: [list
  of four fixes]." Keep one clause saying errors were found and fixed. The fix list is a
  changelog.
- **p. 3:** "A five-quantity uncertainty has now been adopted under a documented exception" uses
  "now" and an "exception" process.
- **p. 4:** "Two newer end-to-end tests qualify..." uses "newer".
- **p. 4:** "(One of the two predictions behind that pattern was later found to have been made
  with a wrongly sampled beam spectrum, ...)" Keep the conclusion and drop "was later found".
- **p. 4:** "A follow-up study looked inside the unfolding to find out why." / "A later paired
  study found..." is a sequence of studies.
- **p. 4:** "Nothing new was adopted."
- **p. 5:** "We originally quoted the slower one; we now quote the faster one, because every
  error-bar ingredient was computed with it. That choice was made after both comparisons with the
  published result were known." This is history, but **it is a real disclosure about analyst
  choice and must stay in some form.** Rephrase it as a present-tense fact (see 6.3).
- **p. 5:** "That test was of the statistical error bars as first built; the main cause was found
  and removed. The statistical bars now quoted were built again, ... and have not been tested."
  Rephrase in the present tense: "The error bars we quote have not yet passed this test. An
  earlier version failed it (91% instead of 95%) for a reason that has since been fixed."
- **p. 7:** "the GENIE and NuWro predictions were rebuilt with a correctly sampled beam spectrum"
  (Fig. 3 caption). This is a reprocessing note. Delete it, or move it to the technical note.
- **pp. 9-10, almost the entire PET subsection:** "Completed simulation studies then improved",
  "the improvement study's frozen ten-iteration candidates", "A later final-design study", "The
  final outcome is", "Saved outputs now give a partial explanation", "A subsequent exploratory
  comparison", "studied earlier". In a primer, PET deserves one paragraph: what it is, what it was
  meant to do, how close it came, why it was not adopted. References [3]-[7] carry the rest.
- **References [1], [3]-[7] (pp. 11-12):** these are links to markdown files at specific commits
  in a GitHub repository, with titles like "terminal decision record" and "REPORT-20261006.md".
  To an outside reader they signal internal documentation, not literature. That is fine for
  traceability, but it reinforces the process-record feel. Consider citing a single technical
  note instead.

---

#### 6. Where the wording made me trust the result less than its content warrants, and where a plainer version would risk overclaiming

##### 6a. Wording that undersells the content

1. **The ordering (pp. 3-5).** I read about defects, failed seed tolerances, failed coverage
   tests, biases of 16-31% and "Nothing new was adopted" *before* the trust check. By the time I
   reach a 1.1% rate agreement and 95.6% of cells within 10%, which is a strong result, I am
   primed to distrust it. Reordering alone would raise my confidence without changing a word of
   content.

2. **The density of negations.** On pp. 3-4 I counted more than 15 sentences whose main verb is
   negated or limiting: "does not certify", "None of these statuses supplies", "cannot establish",
   "No coverage claim is made", "do not assign", "did not establish", "cannot rule out", "have not
   measured", "does not by itself show", "Neither effect is in", "do not remove", "does not
   qualify", "have not established", "does not give", "claim no such", "Nothing new". The cumulative
   effect is that the authors seem to be defending against an accusation. It does not read like
   careful scientists reporting limits. Each individual disclosure is reasonable; it is the
   stacking and the lack of a summary that hurt.

3. **p. 5: "That choice was made after both comparisons with the published result were known."**
   This is honest, but it is stated bare, and it reads like a confession of tuning to the answer.
   The mitigating facts are both on the page: the reason for the choice ("every error-bar
   ingredient was computed with it") and the size of the effect ("about one percent in a typical
   cell"). They should be joined into one present-tense statement, for example: "We quote the
   faster implementation because all our error-bar inputs were computed with it. We made this
   choice after seeing both versions' agreement with the published result. The two differ by about
   1% per cell, which changes the size of the remaining shape difference."

4. **False precision.** "6.145 %" and "6.02 %" (pp. 4, 8) quote a seed effect to the thousandths
   or hundredths, while the text argues that this quantity is not noise-limited. Writing "about
   6%" would *raise* my trust.

5. **"Two newer end-to-end tests qualify 'pass the stated validation tests'" (p. 4).** Quoting
   your own claim in order to undercut it makes the earlier sentence look like it was wrong.

6. **The κ paragraph (p. 9).** The content appears to be that the rejection is robust to about
   5x the largest measured grid effect, which is a positive robustness statement. "ambiguous
   decision ... not a determinate non-rejection ... does not bound the unmeasured below-grid
   error" makes it sound like the test collapses.

7. **`NO_ELIGIBLE_DESIGN` (p. 9).** A status code in monospace makes PET read as a failed
   project. The content is more nuanced: recovery improved from 31% to about 90%, but the error
   bars were miscalibrated.

8. **"Some pseudo-experiments were lost to computing time limits." (p. 8).** This is stated
   before the reassurance that rerunning them changed nothing, and it sounds sloppier than it is.
   Lead with the reassurance.

##### 6b. Where a plainer version would risk overclaiming

These are places where the rewrite must keep the qualifier.

1. **Heading, p. 6: "Then, measure more at once — and rediscover known physics" and "With the
   trust check passed".** The 2D statistical bars "have not been tested" (p. 5), and an earlier
   version under-covered (91% vs 95%). "Trust check passed" is true of the central value and of
   the error-bar *sizes*, not of the bars' statistical meaning. A plain rewrite must say "passed
   for the central value", not just "passed".

2. **p. 6: "a first at MINERvA, where earlier multi-quantity results used binned methods".** This
   is a priority claim. Keep it narrow: first *unbinned* multi-quantity unfolding at MINERvA. Do
   not let a plain rewrite turn it into "first multi-quantity measurement".

3. **p. 8: "This is the kind of localized discrepancy that points theorists toward what their
   models are missing".** This sits beside "Its statistical significance is not assigned" and
   "Central values only". In plain language it is tempting to write "we found a new excess". The
   honest plain version is "the central values show an excess in this corner; we cannot yet say
   whether it is statistically significant."

4. **p. 8: "all ten hypotheses are rejected at a combined 5% error level".** The plain
   paraphrase "all five simulations are ruled out by the data" overclaims. The test holds under
   six stated conditions, borrows Tune v1 shapes within cells, and becomes ambiguous at κ of
   about 5. "Under the stated assumptions" must stay attached. The authors' own caution, "The
   result is not a new measurement with new error bars", is also worth keeping.

5. **p. 11, the Takeaway: "scales to many quantities at once, where the binned method's response
   table does not".** This contradicts p. 1, "nothing forbids it in principle; the limitation is
   one of scale", and p. 2, "Training, the amount of simulation needed, and uncertainty estimation
   still become more demanding". It also omits that the five-variable error bars are not
   validated. This is the one place where the *existing* text already overclaims. The takeaway
   should carry one clause of the caveat, e.g. "...scales to many quantities at once, although
   reliable error bars for the five-variable result remain open work."

6. **p. 5: "our uncertainties — worked out completely independently — come out close in size to
   the published ones".** "Completely independently" is plain and appealing. But p. 3 lists
   effects that are absent from this budget, and p. 3 also reports defects in an earlier version.
   A plain rewrite should not drop "close in size" in favor of "agree". Size agreement is what was
   shown; validity of the bars was not.

7. **p. 10: "σ_ext = 4.502 × 10^-38 cm^2/nucleon".** Four significant figures on a "preliminary"
   number, with 28% of it from a "simulation-dependent extrapolation". A plain rewrite should keep
   "preliminary" and the 6% / 28% split right next to the number. A lay summary such as "we
   extended the measurement to a third more events" would overclaim, because only about 6% is new
   detector-supported rate.

---

## R3. Writer, paper (round 1) — `impl-paper.md` (sha256 `bc56fbd35b3dadc9…`)

### Plain-language pass: the paper (writer's implementation record)

Worktree `wt-plain`, branch `stageF/plain-language-20261018`, base `28d28626`. Files edited:
`docs/analysis-note/main_paper.tex` (abstract and Data availability text only) and
`docs/analysis-note/paper_body.tex` (body and captions). No other file was touched, and no git write was made.

#### 1. Summary of changes, by section

**Abstract.** The stacked noun phrases are split into plain sentences: "pass marginal-normalization checks" is now "pass
checks of their marginal normalizations against the lower-dimensional results", "injected-shape closure checks" is
"recover injected shape changes in closure tests", "background-inclusive tests" is "pseudo-experiments that include
backgrounds", and "estimator-seed limitations" is "the stability under changes of the estimator's random seed".
"A qualified five-dimensional measurement" is now "a five-dimensional measurement with total uncertainties that meet our
predefined criteria", which Sec. VII also uses ("criteria that the analysis set in advance"). The last sentence names
the two limits in physics words: no calorimetric recoil-response uncertainty in the nuisance model, and convergence of
the fine grid that defines the nulls not shown. Every limitation stays in the abstract. No number was added, so the
positive results the reader asked for (1.1%) are still not in it (F-list F4).

**Sec. I.** In paragraph 3, "construction", "projection anchors", "background-inclusive" and "uncertainty
ensembles" are replaced by what each test is. Paragraph 5 is split into short sentences, with the same caveats on the
same claims. The two conditions that limit interpretation are now named, the coarse projections are "of the same
cells", and "qualified" is replaced as in the abstract. The repetition of the limitation list across the abstract, the
Introduction and the Conclusions is shortened in wording, not removed: each of those summaries carries claims that the
caveats qualify, and the brief says to keep when unsure. "Records" in the last paragraph became "full details".

**Sec. II.** The 135 MeV parenthesis is now two sentences after the equation. The content is unchanged: "inherited";
"not corrected"; 0.67%; 1.05%; "not compared with" the covariance. "Correlated uncertainty" became "full covariance".
The source comment says "the adopted covariance with off-diagonals"; the reviewer should check this. "Do not establish
five independently constrained physical directions" became "do not, by themselves, provide five independent
constraints". "A corrected flux sampling (an exact event-by-event reweighting …)" became "are reweighted exactly, event
by event, to the analysis flux"; Sec. V's "before its flux correction" was changed to match.

**Sec. III** (R7: nearly unchanged). "Each result names the one it uses" became "each result below states which
configuration it uses". "Exact-split" is defined at first use. "Nominal-truth bias" became "bias of the purity method at
nominal truth". The disclosures "the original two-dimensional choice" and "selected before the joint-test design was
fixed" are kept.

**Sec. IV (intro, IV A).** In the intro glossary, "missed-event bookkeeping" is defined ("events that fail
reconstruction", from `sec_systematics.tex`'s "miss rows"). In IV A, "the indicative distance is" became "χ²/ndf = …, a
correlated shape difference (indicative only; see below)". The post hoc central-value switch reads: "We quote the LightGBM
result as the central value, so that it uses the same estimator as its covariance. This choice, which replaced the
exact-split result, was made after both comparisons were known." It is kept in full. "No block … includes" became "not
included in any term of the covariance".

**Sec. IV B** (worst section). "Block" is defined at first use ("the sum of four terms, which we call blocks"), and
"standalone" is dropped. The G2 sentence is split into four. The run-period paragraph replaces the four disclaimer
sentences with the R1 model sentence from the brief. All of D5's required limits stay; see §2. The statistical-block
paragraph is reordered within the paragraph: the quoted block first (what it is, its median, its offset, untested), then
the earlier band's failed test and post hoc rescoring, then the earlier-budget errors. "Pre-registered" became "specified
before they were run". The endpoint paragraph (W1) loses "full scientific closeout", "declared conventions",
"construction", "population … coverage" and "supplies no calibrated covariance-based generator significance". Each is
restated in plain words; see §2.

**Sec. IV C.** "Central-value construction … lower-dimensional predecessor" became "Each higher-dimensional central value
is checked against the lower-dimensional result it extends". "Generator-sized change" is replaced. "Lies outside the
quoted uncertainty construction" became "is not included in the quoted uncertainties". "Predeclared criterion" became
"criterion, fixed in advance". "Remains unestablished" became "has not been established". The last sentence is split.
"As first measured with a deterministic variant" is kept: EDITORIAL-20261011 restored "deterministic variant" as a
dropped qualifier.

**Sec. V** (R7). Four small changes: "uncomputed" became "has not been computed"; "response-mismatch closure" became
"closure test with a mismodelled detector response" (the sense of the Acknowledgments); the GiBUU "others' contrast"
sentence is spelled out; and "before its flux correction" became "without its exact flux reweighting".

**Sec. VI A** (R7). "Claim p value" and "claim variants" are gone from the text. "Determined" is defined once ("until
each interval lay entirely on one side of its threshold"). The data-informed disclosure is split into plain sentences
with all its content. "Recorded result … complete record" became "result … full details". The Fig. 4 caption now says
"the shifted null used in the decisions (the ``claim variants'' of the legend)", because the figure's own legend still
says "most conservative claim variant" and the figure is out of scope (P-list P10).

**Sec. VI B, condition (i).** Split into short sentences. "Claim variants", "outside the decision rule" and
"determinate" are replaced. "A rate taken from the design review, whose calculation is not recorded" became "a rate
taken from the review of the test design, for which no calculation is recorded". The disclosure is kept; it is not
softened to "an assumption". In the closing remark, "the independent recomputation verifies the calculation, not that
adequacy" became "… not whether the chain does so".

**Sec. VI C.** The scan paragraph and the lost-pseudo-experiment paragraph are split into short sentences. All the
timing disclosures and numbers stay. "Power set … time-limit losses" became "each power estimate uses 172 to 199 of
its 200 alternative pseudo-experiments, the rest having been lost to time limits".

**Sec. VI D** (R7). "Unmeasured" became "has not been measured", and the untested-list sentence is split.

**Sec. VII.** The governance register is replaced ("predeclared qualification criteria" became "the criteria that the
analysis set in advance for an uncertainty", "throws" became "random throws", and "same-seed resampling floor" became
"the movement from resampling the throws at a fixed seed, a noise floor"). √Tr C is spelled out, and "reportable" and
"inference route" are replaced. "Documented exception" is kept as a phrase (see F-list F9).

**Sec. VIII.** "Differ in standing" became "are of three kinds". The one-sentence list of kinds is split into three
sentences, and "pass marginal anchors" and "background-inclusive" are replaced. "Additional discrimination … remains
undemonstrated" became "we have not shown that the joint information adds discrimination".

**Data availability.** "Release candidate" became "release package … prepared locally but not yet deposited",
"inventoried … identified by SHA256 checksum" became "listed with their SHA256 checksums", "robustness label" became
"robustness result", "lost-seed resolution" became "recovery of the lost pseudo-experiments", and "committed LightGBM
values" became "this paper's LightGBM values". The package history ("assembled before … carries the exact-split
curve"; Fig. 1 "instead regenerated separately") is kept and placed in shorter sentences.

**Deliberately left alone:** the Introduction's first two paragraphs; most of Sec. III; Sec. V apart from the four
phrases; the definitions and the calibration description in VI A; conditions (ii)–(vi); VI D apart from one split; the
Fig. 1–3 captions and Table I; the acknowledgments, `\pubhold` and the bibliography (out of scope). "Hybrid null" stays,
because it is defined at first use. "Fine grid" stays as a standard-words term; its binning is not given (F7).

#### 2. Limitation map for the paragraphs the reviewer must check

The left column lists every limitation, condition or number in the base paragraph. The right column says where it is in
the new text.

##### Abstract
| base content | new text |
|---|---|
| test practical limits; OmniFold; MINERvA open data; ME ν_μ CC inclusive | sentence 1, unchanged |
| reproduces published double-differential xs; extends to 5 observables (E_avail, q3, W) | sentence 2 |
| higher-dim CVs pass marginal-normalization checks | "pass checks of their marginal normalizations against the lower-dimensional results" |
| **three- and four-observable** CVs pass injected-shape closure (scope: not 5D) | "the three- and four-observable central values recover injected shape changes in closure tests" |
| background-inclusive tests and uncertainty studies expose background-treatment, regularization, coverage, estimator-seed limitations | sentence 4: "Pseudo-experiments that include backgrounds, and studies of the uncertainties, show limitations of the background treatment, the regularization, the interval coverage, and the stability under changes of the estimator's random seed" |
| measured model dependence prevents a qualified 5D measurement with total uncertainties at useful precision | sentence 5; "qualified" became "that meet our predefined criteria" |
| calibrated with full-chain pseudo-experiments under a stated nuisance model | sentence 6, unchanged |
| reject all five (list) in total and in shape at 5% familywise | sentence 6, unchanged |
| "conditional" tests | "These tests hold only under stated conditions." |
| recover known discrepancies | sentence 8 |
| no demonstrated discrimination from joint info beyond matched coarse projections | "they do not show that the joint five-observable information discriminates beyond matched coarse projections of the same cells" |
| interpretation limited by omitted calorimetric recoil-response uncertainty | last sentence, "the nuisance model has no calorimetric recoil-response uncertainty" |
| … and unresolved fine-grid convergence | last sentence, "convergence of the fine grid on which the null hypotheses are defined has not been shown" |
| numerals: 2.12.10, 21.09, 2019, 5 | unchanged |

##### Introduction, paragraph 5 (the `% J3/J4 provisional … C4` site)
| base content | new text |
|---|---|
| ~1% (ratioTot), binsTen% of 205 within 10% | unchanged |
| higher-dim pass marginal anchors; recover low-recoil discrepancy | "agree with their lower-dimensional marginals and recover the known low-recoil discrepancy" |
| 3,4-obs pass injected-shape closure | kept, with "three- and four-observable" scope |
| background-subtraction bias up to 4%, in simulation, highest-W cells | kept |
| unbinned treatment, used only for generator tests, largely removes it | kept, own sentence |
| quoted uncertainties omit it | "the quoted uncertainties do not include it" |
| follows a generator-sized E_avail change only partly | "recovers only part of a change of the E_avail shape as large as the difference between generators" |
| regularization bias, estimator-seed sensitivity, untested coverage limit the construction | kept ("the method") |
| model dependence prevents a 5D measurement with qualified total uncertainties at useful precision | kept; "qualified" as in the abstract; comment lines kept around it, plain-language comment added |
| all ten, total and shape, five predictions, 5% familywise | kept |
| under six stated conditions (Sec. VI B) | "They hold under six stated conditions (Sec. VI B)" |
| omitted recoil-response uncertainty and unresolved fine-grid convergence limit interpretation | "two of them, the absence of a calorimetric recoil-response uncertainty and the undemonstrated convergence of the fine grid …, limit their physical interpretation" |
| each test p<0.05 in ≥1 matched coarse projection, so the joint info is not shown to add discrimination | kept; "of the same cells" added (the definition in VI C) |

##### Sec. IV B, paragraph 1 (budget; the C2, W5, W7, D3 sites)
| base content | new text |
|---|---|
| four blocks: universe, statistical, training-seed, run-period | "sum of four terms, which we call blocks: …" ("standalone" dropped as undefined) |
| first three are LightGBM ensembles at the CV's estimator; fourth from LightGBM unfolds of three run periods | kept verbatim in content (the "three run periods" vs "three period groups" mismatch is listed, F3) |
| \uqMedian, \uqIntegral vs \uqPaper, \uqPaperIntegral | kept ("The resulting relative uncertainty …") |
| universe block dominates bin by bin (median 87% of variance) and in the integral; run-period raises median \uqSFiveMedian → \uqMedian | unchanged |
| flux block applies the MAT ν–e and IMD constraint weights | unchanged |
| published flux 4.01% > ours \fluxBand; reason not established by the release | "we could not determine the reason from the released inputs" (D10's own wording: "not established from the released inputs") |
| systematic and statistical blocks at the CV's training seed | own sentence |
| training-seed block: five settings including it; median 0.06%; ~70% uncertain in variance | own sentence |

##### Sec. IV B, paragraph 2a (G2, the D4 site)
| base content | new text |
|---|---|
| universe unfolds approximate the weighting of events failing reconstruction | sentence 1 |
| approximation not corrected | sentence 1, "we do not correct this approximation" |
| 2 of 187 universes (resonance, flux), each at two seeds | sentence 2 |
| no effect resolved above the noise of an **earlier** ten-seed scan, ~3× the training-seed block | sentence 3 ("earlier" kept) |
| effect below ~2× that noise not excluded | sentence 4 |
| test not tight | sentence 4 |

##### Sec. IV B, paragraph 2b (run period, the D5/W2 site)
| base content | new text |
|---|---|
| periods not mutually consistent within the other uncertainties | kept |
| one group's unfolded p∥ relative to its own simulation differs from the earliest periods by ~7% near 8 GeV/c | kept (the director's corrected sentence, not reworded) |
| cause unknown; data cannot establish which period is correct | kept verbatim |
| carried as the run-period block on the combined result | "We include the effect … as the run-period block" |
| built from differences among three groups, no reference | kept |
| 2.1% median; 1.2–3.4% on p∥ projections; 2.0% integral | kept |
| reference-free double-ratio construction uses the periods' own simulated responses | "The block uses double ratios between groups, each group's unfolded result being taken over its own simulated truth, so it relies on the periods' own simulated responses" (reference-free is carried by "without choosing any as the reference") |
| it does not identify a correct period | "and does not identify a correct period" |
| small number of groups, possible regularization shrinkage, retained statistical and training noise limit interpretation | "Its interpretation is limited by the small number of groups, by possible shrinkage from the regularization, and by the statistical and training noise it retains" |
| containment of the observed differences is not evidence of coverage | "Because the block is built from the differences among the periods, it covers them automatically; this says nothing about whether its size is right" (the brief's R1 model) |
| own consistency check passes by construction; not a test | "For the same reason, the block's own consistency check passes whatever the data, and it is not a test" (review m12 comment: "whatever the data") |

The base comment "the last three sentences are D5's Required clause, verbatim" survives verbatim, as C6 requires. It
now describes the base text. The added plain-language comment marks the rewording that C5 and DECISION-20261018-plain-
language allow ("or equivalent wording used", DRAFT-disclosures D5).

##### Sec. IV B, paragraph 3 (statistical block, the D2/D8/C4/J5 sites), reordered within the paragraph
| base content | new text |
|---|---|
| quoted block: 300 replicas, CV's training seed, three independent streams (data, signal, background sim) | sentence 1 ("a bootstrap of 300 replicas …"; D2 calls it a "300-replica bootstrap") |
| median 0.684% (gate phrase) | sentence 1, gate phrase intact |
| replica mean offset 0.26 stat SD per-bin median; block is a covariance about that mean and excludes it | sentence 2 |
| quoted block not independently tested | sentence 3, "The coverage of this block has not been independently tested" |
| coverage of the total untested | sentence 3 |
| earlier band undercovered in its tails | sentence 4 ("An earlier version of the statistical band undercovered in its tails …") |
| \covTwoDNtoy closure toys, **pre-registered**, fixed truth | "specified before they were run" |
| pooled over experiments and bins; \covTwoDCTwoPctOne% within 2σ vs 95.4% nominal (gate phrase) | kept |
| main cause: a completeness division in the replicas, not in the CV; removed in a rebuilt band | "a division by the completeness that the bootstrap replicas carried and the central value does not, was removed in a rebuilt band" |
| rescoring is post hoc and partly circular | "Rescoring … against the rebuilt band is post hoc and partly circular." |
| removes tail undercoverage: 97.7% / 78.1% (gate phrase) | kept |
| rebuilt band wider than toy scatter, reasons not established | kept |
| rebuilt band not independently tested | "The rebuilt band has not been independently tested either" |
| quoted block is a different ensemble (from the rebuilt band) | "and the quoted statistical block is a different ensemble from it" |
| earlier-budget defects found by an assessment of saved products: truth-input mismatch (sweep vs its reference) and unpropagated background-template statistics [25] | "A review of the stored analysis products found errors in an earlier version of the uncertainty budget, among them a mismatch between the truth input of its systematic-universe unfolds and that of their reference, and statistical fluctuations of the background templates that were not propagated [25]" |
| the quoted covariance is free of both | kept |

##### Sec. IV B, paragraph 4 (endpoint, the W1/D1 site)
| base content (D1 must-carry) | new text |
|---|---|
| reproducible 2D CV | kept |
| matched uncertainty construction | "a covariance built with the same estimator" (Sec. III's wording) |
| under declared conventions | "under stated conventions" (D1 draft's wording), and "The analysis note [14] states these conventions" |
| "Full scientific closeout is not achieved" (W1 meaning) | "The result is not fully validated." |
| not independently validated for population or simultaneous interval coverage | "Neither the average coverage of its per-bin intervals nor their simultaneous coverage over all bins has been independently validated" ("population" read as coverage averaged over the population of bins; reviewer to check) |
| supplies no calibrated covariance-based generator significance | "the covariance provides no calibrated significance for generator comparisons" |
| not in any block: G2 approximation; ML-estimator dependence (Sec. IV A); unfolding-model and regularization dependence, whose estimate needs independent-generator samples | kept, "not included in any block of the covariance" |
| detector response assumed to vary only within its parametrized family | kept |
| validated total intervals over the full domain require: independent production-size simulation; validated continuous nuisance generator; independent-generator samples not already inspected | "would require new inputs: an independent simulation sample of production size, a validated generator of continuous nuisance-parameter variations, and independent-generator samples that have not already been inspected" |
| no coverage claim is made | "We make no claim about coverage." |
| note states the conventions, further approximations and limits | kept |

##### Sec. VI B, condition (i)
| base content | new text |
|---|---|
| decisions test the hybrid null; six conditions of the nuisance model; numbered as in the advance specification [32] | sentences 1–2 |
| below the fine grid the null truth carries Tune v1 shapes | "Within each fine-grid cell the null truth has the Tune v1's shapes" |
| convergence on the fine grid not shown | same sentence |
| L2 norm of per-cell relative changes; last step twofold-merged → fine is \jtMoneMin–\jtMoneMax of the whole change from the coarse grid | own sentence, unchanged |
| residual unmeasured and potentially material | "The residual below the fine grid is therefore unmeasured and potentially material" |
| **before any result**, shifts set from an assumed extrapolation | "Before any result was known, the size of the shifts was set from an assumed extrapolation" |
| geometric shrinking at a rate taken from the design review, whose calculation is not recorded | "at a rate taken from the review of the test design, for which no calculation is recorded" |
| residual ~1–3× the last step | kept |
| decisions use the central estimate ±\jtMoneKappa δ | "The shifted nulls used for the decisions take its central estimate" |
| robustness checks, not entering decisions, use ±\jtMoneKappaRobust δ | kept |
| measured L2 ratios also allow slower convergence | kept verbatim |
| carry-over to G only if sub-grid replacement moves the result ≤ ±\jtMoneKappa δ along δ_fine | kept (no "therefore" added) |
| outside the decision rule, the scan finds rejections determinate along that direction to ~5.2 δ | "Separately from the decision rule, the scan of Sec. VI C finds the rejections still determined … up to about 5.2 δ_fine" ("determined" defined in VI A) |
| bounds neither residual nor convergence | kept |

##### Sec. VI C, scan sentence
| base content | new text |
|---|---|
| scan of the multiplier along δ_fine | "As a sensitivity check, we scanned the multiplier of the shift along δ_fine" (the reference title calls it a "sensitivity scan") |
| specified before it ran; run after the decisions; outside the decision rule [33] | "The scan was specified before it ran, but it was run after the decisions and is not part of the decision rule [33]" |
| all ten stay determinate rejections at every sampled multiplier up to 5.25 δ, calibration ensembles at their stopping point | kept |
| 5.17 δ with recovered pseudo-experiments included | kept |
| tests one prescribed direction; bounds neither actual residual nor convergence | kept |

##### Sec. VI C, lost pseudo-experiments
| base content | new text |
|---|---|
| time limits interrupted or prevented \jtLostCal calibration and \jtLostPow power pseudo-experiments | kept ("Batch-job time limits") |
| had every **interrupted** one exceeded the observed statistic, no test rejected | kept, "interrupted" (the note's sec:joint5d-lost confirms that the worst case is over the interrupted draws) |
| rerun after the decisions, outside the decision rule | kept |
| procedure fixed and independently reviewed beforehand [34] | kept |
| first reproduced 16 completed seeds exactly | "it first reproduced 16 completed pseudo-experiments exactly" |
| none recovered reaches the observed statistic in any test or shifted null | kept |
| every submitted pseudo-experiment observed; no assignment changes any decision | kept, own sentence, the same "and" (no causal "so" added) |
| closest 4.6 below 868.6 (GENIE+MEC shape, robustness shift) | kept |

##### Sec. VI C, last paragraph
Unchanged apart from the power parenthesis: 172 to 199 of 200 are kept, and the time-limit cause is kept.

##### Sec. VII, paragraph 1
| base content | new text |
|---|---|
| a covariance built for the 5D CV; \zprojCells-cell (E_avail, W) projection formed | sentence 1 |
| separate from the joint-test calibration | sentence 1 |
| has not met the analysis's predeclared qualification criteria | "It has not met the criteria that the analysis set in advance for an uncertainty" |
| one criterion requires a bound fixed before production and can no longer be applied | kept |
| used only under a documented exception limited to that one product | "used only under a documented exception to the criteria, limited to this one covariance" |
| no covariance-based generator significance, because covariances depend measurably on the seed | kept verbatim |
| two further covariances at two seeds (separate from the one in use): projected uncertainty moves \sprojMeasured% vs a \sprojBound% limit set before production | kept |
| movement did not fall with ensemble size (40, 80, 160 throws: \seedEffectNforty, \seedEffectNeighty, \sprojMeasured) | kept ("random throws") |
| same-seed resampling floor fell \floorNforty → \floorNeighty between 40 and 80 | "the movement from resampling the throws at a fixed seed, a noise floor, fell from …" |
| rests on one seed pair with nested throw subsets; seed-pair width and large-N behaviour unmeasured | "The comparison rests on one seed pair, with nested subsets of the throws, so the spread over seed pairs and the behaviour at much larger ensembles have not been measured" |
| 5 of 45 bands at a fixed seed the variation cannot reach (\pinnedBandsSqrtTr% of √Tr C) | "built at a fixed seed that the variation cannot change; they make up …% of √Tr C, the square root of the covariance's trace" |
| their seed sensitivity, and its effect on the total in either direction, unmeasured | kept, "has not been measured" |

##### Sec. VII, paragraph 2
| base content | new text |
|---|---|
| a separate study searched for a 5D measurement definition whose total uncertainties could be qualified | "… whose total uncertainties could meet these criteria" |
| none of the definitions considered could meet the advance precision targets within its rules and computing budget | kept ("within the study's rules and computing budget") |
| fallback definition: the bounded model-dependence component alone exceeded the target total width | kept verbatim (wording ambiguity listed as F8) |
| the joint tests came from the same study, as a separate inference route | "as a separate route to inference" |
| produce no new reportable uncertainty | "they produce no new uncertainty that could be reported for a measurement" |

##### Sec. VIII, paragraph 1 (the C4/J5 site)
| base content | new text |
|---|---|
| applies OmniFold, reproduces 2D, extends to five observables | kept ("extends the unfolding") |
| results differ in standing | "The results are of three kinds." |
| 2D comparison = end-to-end test vs the same-data measurement | own sentence |
| 3–5D CVs support only descriptive comparisons; no validated total-interval coverage; no covariance-based generator significance | own sentence, both "without" clauses |
| joint tests calibrated; conditional on six stated conditions; no new reportable uncertainty | own sentence |
| higher-dim pass marginal anchors; recover low-recoil discrepancy; 3,4-obs pass injected-shape closure | kept, the scope kept |
| background-inclusive tests reveal a subtraction bias that unbinned refinement reduces | kept |
| regularization bias persists under the tested generator-sized shape changes | "persists under the tested shape changes of generator size" |
| coverage and seed studies: quoted 2D statistical block awaits an independent coverage test (C4 comment beside it) | kept; plain-language comment added beside the J3/J4 line |
| 2D comparison depends on the learner at ~1 unit of χ²/ndf | kept |
| model dependence prevents a qualified 5D measurement at useful precision | "qualified" replaced as in the abstract |
| practical checks for future work | kept |

##### Sec. VIII, paragraph 2
Only one change: "additional discrimination … remains undemonstrated" became "we have not shown that the joint
information adds discrimination". All the conditions, 0.05, "recovering every lost pseudo-experiment changes no
decision", and the two requirements for extending the interpretation are unchanged.

##### Data availability
| base content | new text |
|---|---|
| inputs are the open-data AnaTuples, CC0 [8] | kept |
| an earlier production of that release | kept |
| 2,374 inventoried input files identified by SHA256 [38] | "2,374 input files are listed with their SHA256 checksums [38]" |
| local release candidate, not yet deposited, ~16 MB [39] | "A release package of about 16 MB [39], prepared locally but not yet deposited" |
| numpy, scipy, matplotlib only | "needs only numpy, scipy, and matplotlib" |
| recompute every p value, decision, robustness label, power figure of the joint tests; the lost-seed resolution; the coarse-projection comparison; the fine-grid L2 ratios of condition (i) | kept ("robustness result"; "recovery of the lost pseudo-experiments") |
| regenerate Figs. 2–4; recompute numbers quoted from Figs. 2 and 3 | kept |
| empty-directory replay reproduces every recorded value and every checked figure number | "Rerunning the packaged files from an empty directory reproduces every value recorded in the package and every checked figure number" |
| the candidate predates the LightGBM switch and carries the exact-split curve | "The package was assembled before the two-dimensional central value was changed to LightGBM, and it carries the exact-split curve" |
| Fig. 1 and its numbers instead regenerated with the release's plotting code, extended to draw this band, from the committed LightGBM values and covariance | kept; "committed" became "this paper's" |
| other quoted numbers, apart from the multiplier scan (recomputable from [33]), not recomputable from this release | kept, own sentence |
| they and event-level processing need archived products, AnaTuples, generator samples | kept |
| the note's release appendix [14] states what each part does and does not reproduce | kept |

#### 3. Invariance check, paper block (verbatim)

Command: `python3 -I …/check_invariance.py $W 28d28626 > $S/inv-paper.out; echo rc=$?` gave **rc=1**. The non-zero exit
comes from the primer and note blocks, which other writers own. The paper block:

```
== paper
  [SAME] numerals (325)
  [SAME] value macros (68)
  [SAME] cite keys (64)
  [SAME] ref targets (35)
  [SAME] labels (18)
  [SAME] comment lines: all 204 base lines survive
  [INFO] comment lines added (14):
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      (… the same line 14 times in all …)
== files changed outside scope
  [SAME] none
```

**There is no [DIFF] in the paper block.** All 325 numerals, 68 value macros, 64 cite keys, 35 ref targets and 18 labels
are unchanged, so there is no numeral spelling change to list. All 204 base comment lines survive, and each stays beside
its sentence. Two moved within their paragraph together with their sentences: the D2/D8 comment, now after the
quoted-block sentences, and the VL169 comment, now after the earlier-band sentences. The only addition is the
plain-language comment line, 14 times:
- 10 beside `% J3/J4 provisional` sites: Intro para 5; Sec. III exact-split (after the W3 KI-88 comment); IV B C2,
  W7, D3, D5, D2/D8, D2 (VL169) and KI-93/94; Conclusions C4; plus the Data-availability J4 site in `main_paper.tex`;
- 3 at other reworded sites: IV A after the learner sentence, which carries the W6 comment below it; G2 (D4), whose
  J3/J4 comment follows; and the endpoint (W1), whose J3/J4 comment follows.

The Sec. IV receipt gate's fixed phrases ("against … 95.4 … nominal", "with a median statistical uncertainty of …0.684",
"removes the tail undercoverage: …", "biased by up to … in simulation", "reduces it to below …", "leaving up to … in some
joint cells", "differ by at most …", "by up to … at high $W$", "it is \SIrange{16}{31}… in the most affected", "within the
quoted total uncertainty in about half of those cells") were all kept, and the gate passes 15/15.

#### 4. F-list (flagged, not made)

| id | location | base text | proposed text | why flagged |
|---|---|---|---|---|
| F1 | IV C | "failed its predeclared criterion at nominal truth and under an E_avail tilt, so frequentist coverage of the five-dimensional intervals remains unestablished" (now "has not been established") | "… failed its criterion …, so these intervals do not have their nominal coverage at nominal truth or under the tilt" | Stronger: a failed test shows miscoverage, not just unknown coverage (reader 2.30, 4.6). The size and direction of the failure are not printed, and adding them would add numbers. For Joseph. |
| F2 | IV B, stat block | "Neither it nor the rebuilt band has been independently tested" (kept as "has not been independently tested") | "The coverage of this block has not been tested." | DRAFT-disclosures D2 says S1 "has not been coverage-tested at all". This is stronger than the paper's "independently". It aligns with decided content, so the director rules (C7). |
| F3 | IV B, para 1 | "the fourth is built from LightGBM unfolds of three run periods" | "… of three groups of run periods" | **Base defect.** The same section says "three period groups". The comment names P_A = 1A–1F and P_B = 1G, 1L, 1M, so the unfolds are of period groups, not three single periods. |
| F4 | abstract, Intro, VII, VIII | "the measured model dependence prevents … at useful precision"; VII "the bounded model-dependence component alone exceeded the target total width" | give the bound and the target width (from the note's `sec:gbdt-model-dependence`, "Reporting definitions for a five-dimensional measurement") | The reader's main complaint (4.1): the central negative result has no number. Adding a number is not allowed (C1/C3). |
| F5 | abstract | (no positive numbers) | add "agrees with the published integrated cross section to 1.1%" | The reader asked for this (2.1, 6a). It is a new number in the abstract. |
| F6 | VI B (i) | "a rate taken from the review of the test design, for which no calculation is recorded" | give the rate (0.45–0.76 per halving, in the source comment) and call it an assumption | Adds a number. The comment also says the proxy rate "is NOT reproducible from any recorded number", which the reader called the most damaging phrase (6a). For Joseph. |
| F7 | VI A, VI B | "a fine five-dimensional grid" | state the fine grid's binning | Adds numbers (reader 2.35, table row "fine grid"). |
| F8 | VII para 2 | "the bounded model-dependence component alone exceeded the target total width" | "the bound on the model-dependence component alone …" or "the model-dependence component, as bounded there, alone …" | **Possible base defect:** "bounded component exceeded" can be read as the bound or as the component. The reading changes the strength, so it is left verbatim. |
| F9 | VII para 1 | "used only under a documented exception … limited to this one covariance" | "We use it only for [the stated purpose]; it enters no figure or test in this paper" | The reader (4.10) could not tell what the covariance is used for. Nothing in the paper says where it is used, and stating it would be a new claim. |
| F10 | II | "an inherited constant of 135 MeV" | "a constant of 135 MeV inherited from the MINERvA-101 analysis code" | Adds provenance. `docs/EAVAIL_DEFINITION.md` §3 traces it to the MINERvA 101 tutorial, but the paper does not say so (reader 2.8, 4.14). |
| F11 | IV C | "Input changes at the level of floating-point rounding move the unfolded values on data by up to a few statistical standard deviations" | say where it occurs, and which estimator | Reader 4.5. A clearer version needs new facts. |
| F12 | IV C | "by up to 74% at high W … measured with the joint-test estimator, it is 16% to 31%" | name the central-value estimator for the 74% (the source comment: "The 74% is the F2/N estimator") | Reader 4.4. It adds an attribution the text does not make. |
| F13 | VI C | power "0.74, 0.02, and 0.00" | add one sentence saying what power near zero means | New interpretive claim (reader 4.9). Note that CLAIMS I4 says power is context only. |
| F14 | VI C / VI D | VI C "recover the generator disagreements established by the published measurement"; VI D "do not reject GENIE 2.12.10 CV" in (p_T, p∥) | add in VI C: "except that, within this analysis, GENIE CV is not rejected by the muon-kinematic projection alone (Sec. VI D)" | Reader 4.8 says the two pull against each other. Joining them is a new sentence. |
| F15 | abstract | "reject all five tested predictions" | "reject the hybrid null hypotheses for all five tested predictions" | Reader 4.7. The wording narrows a claim (C3). The fine-grid condition is already in the abstract. |
| F16 | VI A | "with non-centralities λ of 318–6344 in these units" | drop "in these units", or say "in units of the test statistic" | The meaning of "in these units" is not clear to the writer, so it was left as is. |

Two judgment calls were made, not flagged; the reviewer should check both against C3. (a) "Qualified" became "meet our
predefined criteria" in the abstract, the Introduction and the Conclusions. This follows Sec. VII's use, where the
qualification criteria are those set in advance. (b) "Population or simultaneous interval coverage" became "the average
coverage of its per-bin intervals nor their simultaneous coverage over all bins". If the reviewer disagrees, the
fallback is to keep "population" and add "(averaged over bins)".

#### 5. P-list (proposed cuts and moves, and out-of-scope items)

| id | exact text (base) | proposal | where it already lives |
|---|---|---|---|
| P1 | "The use of AI tools in this work is described in the Acknowledgments." (Sec. III) | cut | the paper's own Acknowledgments (`main_paper.tex`); a pointer in Methods is not needed |
| P2 | Sec. IV intro paragraph "In closure tests, truth denotes … neither establishes recovery or coverage." | cut, or reduce to one sentence | `sec_validation.tex` `\paragraph{Closure.}` (l.37) and `sec:closure-map` cover the terms; the "missed-event"/invariance remark has no note home found by grep |
| P3 | "An earlier version of the statistical band undercovered … The rebuilt band has not been independently tested either, and the quoted statistical block is a different ensemble from it." (IV B; base: "The statistical block, as first built, … for reasons not established.") | keep one sentence ("An earlier band undercovered in a fixed-truth test and was rebuilt; the rebuilt band was only rescored post hoc (Ref. note)") | `sec_validation.tex` `sec:coverage` (l.214–250, the full VL169 test and verdict), and the "The rebuilt band, scored post hoc" paragraph named in the source comment; D2's must-carry (the history) would need the director's ruling |
| P4 | "An assessment of the saved products found construction defects in the earlier budget, … the quoted covariance is free of both." | cut, or replace with "the statistical fluctuations of the background templates are included" | `sec_systematics.tex` `sec:uq-2d-construction` (l.183–235: the May-sweep truth-input mismatch and "The earlier budget did not propagate background-template statistics"); EDITORIAL-20261011 H1 warns that cutting this may make the defects read as affecting the budget, or not affecting it |
| P5 | Sec. VII seed-convergence numbers ("The movement did not fall … have not been measured.") | keep one sentence | `sec_5d.tex` `sec:eavailw-construction`, "What the covariance supports" items 1–2 (l.469–505) |
| P6 | Data availability: "The candidate predates the change … from the committed LightGBM values and covariance." | cut once the package carries the LightGBM curve | **no note home found**: `app_release.tex` (`app:release`, `app:release-scope`) states RC7's scope but does not say that it predates the LightGBM switch. A move would need a note sentence first (C4). |
| P7 | VI C lost-PE paragraph: "under a procedure fixed and independently reviewed beforehand, which first reproduced 16 completed seeds exactly" | compress to "rerun after the decisions under a procedure fixed in advance; none reaches the observed statistic" | `sec_joint.tex` `sec:joint5d-lost` (l.256–280: procedure, 16/16 determinism check, both margins) |
| P8 | VI A: "An independent recomputation with separately written code agrees with the production evaluation in all 1379 compared quantities." | shorten to "An independent implementation reproduces every test statistic and p value" | `sec_joint.tex` l.107 (\jtRecompRows rows); `app_provenance.tex` l.140 |
| P9 | VI B (i) final clause and VI C scan sentence (5.2 / 5.25 / 5.17 δ_fine stated twice) | keep the endpoints only in VI C | `sec_joint.tex` `sec:joint5d-kappa` (exact endpoints) |
| P10 | **Out of scope (figure):** the Fig. 4 legend "null pseudo-experiments (most conservative claim variant)" | relabel "most conservative shifted null" | the figure producer, not a LaTeX source in scope; the caption now glosses the term |
| P11 | **Out of scope (bibliography):** titles [25] "construction findings and validation feasibility", [32] "frozen contract and recorded result", [33] "report-only sensitivity scan", [34] "report-only recovery …", [35], [37] "W2B-REPORT", [38] "completed hashes and data addition", [39] "Article release candidate RC7: sufficient-input replay …"; [25], [38], [39] have no locator | retitle in physics words, or fold into the note as "Ref. [14], Sec. X"; give locators | `technote.bib`/`publication.bib` (out of scope) |
| P12 | **Out of scope (`\pubhold`):** "[HOLD: funding and grant acknowledgments]" and "[HOLD: deposit identifier and access route, after the separately authorized release decision.]" | must not reach a referee; the second has internal register ("separately authorized release decision") | `main_paper.tex` `\pubhold` arguments (out of scope) |
| P13 | **Out of scope (acknowledgments):** the AI paragraph ("Results were accepted only after verification against committed evidence …", the eleven-model list) | shorten (reader 2.55, 6a) | `main_paper.tex` acknowledgments (out of scope; text approved by Joseph 2026-10-06/08) |
| P14 | **Out of scope (labels):** "GENIE CV" for the untuned GENIE 2.12.10, which MINERvA readers take to mean the tuned CV | relabel | W10 kept the legend labels (J4); for Joseph |

#### 6. Build

`$S/build_copy.sh paper` gave **rc=0**. The final run was made on the final sources, after every edit. All four
targets report `OK … written by this run; no unresolved references … after 1 latexmk invocation(s)`. The containment
gate (`check_dead_containment.py`) gives SELF-TEST PASS and RESULT PASS. The Sec. IV receipt gate
(`check_sec4_receipts.py`) gives SELF-TEST PASS (18 perturbations rejected) and SEC4-RECEIPTS PASS (15/15). The paper's
two overfull hboxes (abstract/title block 11.06 pt, Table I 0.71 pt) are the base's own.

| PDF | pages |
|---|---|
| main_paper | **12** (base 11; page 12 holds references [20]–[39] only) |
| main_note | 123 |
| main_primer | 14 |
| pet_note | 26 |

The note and primer counts include the other writers' concurrent edits. The paper grew by about half a column, all of it
in the reference list, because the body sentences are now split into shorter ones. It stays within the 12-page limit.
If an 11-page paper is wanted, P1, P2, P7 and P8 are the cheapest cuts, each needing the note home stated.

Pages read after the build: 1 (abstract and Introduction), 3–5 (Secs. III, IV A–C, Fig. 1), and 6–11 (Secs. V–VIII and
Data availability). They render cleanly, with no `??` and no stray comment text.

---

## R4. Writer, primer (round 1) — `impl-primer.md` (sha256 `78e1f29525f51027…`)

### Plain-language pass: primer implementation record

Writer: primer lane. Worktree `wt-plain`, branch `stageF/plain-language-20261018`, base `28d28626`.
Files edited: `docs/analysis-note/main_primer.tex` (abstract only) and `docs/analysis-note/primer_body.tex`. No
other file was touched, and nothing was written to git. A copy of the base body is at
`$S/primer_body.base.tex`. Base line numbers below (`Lnn`) refer to `primer_body.tex` at `28d28626`.

#### 1. Summary

**Left alone (R7).** Section 1 (L9–25). Section 2's first three paragraphs and Fig. 1 (L29–62). The trust-check
opening (L216–235, apart from one gloss). Fig. 2. The multi-quantity opening (L268–281). The low-recoil paragraph
(L283–295, apart from one gloss). The new-puzzle paragraph (L318–340, apart from a pointer). Fig. 4's caption
(apart from one word). The signal-definition paragraph (L481–489, one gloss). Fig. 6. The takeaway (L506–512, which
is flagged in F1 and not changed).

**Abstract.** The last two sentences now define "signal definition" and "muon kinematic cuts", and say plainly that
part of the extension is detector-supported and part simulation-dominated.

**Section 2.**
- "A finite learner" becomes "A learner of limited capacity".
- The table's third column is now headed "What passing it does not establish" (was "What it cannot establish").
- The selection-versus-inputs paragraph (L93–99) now:
  - defines MINOS (a second, downstream detector that measures the muon's momentum);
  - defines the scalar classifiers as gradient-boosted decision trees, named once as **the tree learner** and used
    under that one name from then on;
  - defines PET (a neural network, a "point-cloud transformer", that reads individual energy deposits);
  - names "the technical note" as "the companion analysis note". The table is
    `selection_features.tex`, input by the note's `sec_experiment.tex`.

**Section 3, reordered within the section (C4).** New order:
1. **Findings summary (new):** an opening sentence and six items, each carrying its caveats, then a closing sentence.
   It is built from the reworded status paragraph (L103–112, whose content is items 1, 2, 4 and 5 plus the closing
   sentence) and restates items 3 and 6, and parts of item 1, from the body with their caveats.
2. **"First, a trust check"**, now first. The trust paragraph (L216–256) is split into three paragraphs: results;
   learner qualification; coverage test. The 2D error-budget paragraph (L114–128 with its comments L129–136) moves
   here, split into two paragraphs (contents and exclusions; the coverage argument), and sits between the learner
   qualification and the coverage test.
3. **"Then, measure more at once"** and **"A new puzzle"**: unchanged apart from the pointer edits and the
   "maximal common grid" gloss.
4. **"What we cannot yet claim for the multi-quantity results" (new heading).** It holds base L138–143, L145–167,
   L169–177, L179–189, L191–208 and L210–212, in their base order, right after the multi-quantity results they
   qualify (they were before the trust check). L145–167 and L191–208 are each split into two paragraphs.
5. **"A joint test of five simulations"**: reworded. The six conditions are now an itemized list.
6. **"Alternative representations and signal definitions"**: the PET paragraphs are reworded to remove project
   vocabulary; the signal-definition paragraph and Fig. 6 are kept.

**Vocabulary removed or defined.**
- Removed: `NO_ELIGIBLE_DESIGN` (now "no eligible design"), "frozen point rule", "frozen tests", "frozen
  ten-iteration candidates", "development tilt", "study scale", "banks", "production LightGBM", "comparator",
  "helper classifier", "adopted"/"adoption" as a project act, "Nothing new was adopted", "the figure above" (there
  was no figure), and "qualify 'pass the stated validation tests'" (the text no longer quotes itself).
- One name for the learner: "the tree learner" replaces "tree-learner implementations", "scalar tree-based
  OmniFold", "the tree method", "the matched tree method" and "the comparator". The PET figure's "GBDT" is glossed
  in its caption.
- Defined: MINOS, PET, tree learner, coverage (in the trust check, at the point the argument needs it),
  pseudo-experiments, nuisance variations, bootstrap, acceptance, finalists, MEC, Tune v1, GENIE CV, κ,
  determinate, post hoc, ten hypotheses (5 × 2), signal definition, σ_ext and the maximal common grid.

**Page count.** 12 → 14. The growth comes from the findings list, the itemized joint-test conditions and the extra
paragraph breaks. There is white space at the foot of pp. 2 and 6, from `[H]` floats that do not fit; the float
specifiers were not changed.

#### 2. Preservation map, paragraph by paragraph

Each row lists what the base paragraph carried and where each item now sits. "Same" means the same words in the same
paragraph.

##### Abstract (`main_primer.tex`)
| base content | new location |
|---|---|
| jargon-light guide; what the method does; "why it lets us measure several quantities at once when the traditional method cannot" | same (the "cannot" is flagged in F2) |
| faithful reproduction; low-recoil discrepancy recovered with a different method | same |
| study of how far the signal definition can be extended beyond the published muon kinematic cuts | same, with "signal definition" glossed as "the set of interactions the measurement counts" and the cuts as "the published limits on the muon's angle and momentum" (the cuts are θ_μ < 20° and a p∥ range, `sec_fps.tex` l.14) |
| the extension has detector-supported and simulation-dominated regions, kept separate | "Part of that extension is supported by the detector's data and part is dominated by the simulation; the two kinds of region are kept separate." |

##### L66–71 (prior/response/truth)
"A finite learner" becomes "A learner of limited capacity". The approximation error "even with the correct
response" is unchanged.

##### Table 1 (L73–91)
The column header is now "What passing it does not establish". Every row and the caption are unchanged.

##### L93–99 (selection versus inputs)
| base content | new location |
|---|---|
| selection and classifier inputs are distinct | "which events are kept (the selection) and what the learner is shown (its inputs) are separate choices" |
| every real-data route requires a reconstructed muon matched to MINOS | "Every analysis of real data here requires a reconstructed muon matched to MINOS", with MINOS glossed |
| scalar classifiers use its momentum | same, plus the definition of the scalar classifiers as gradient-boosted decision trees (the tree learner); paper l.175, "gradient-boosted decision-tree classifiers" |
| the historical recoil-only PET classifier does not use the muon, though the muon is needed to select the event | same ("original" for "historical"), with PET defined in the sentence before |
| full-event PET adds muon features | same |
| removing truth-muon cuts enlarges the population without adding selected observations | same ("the cuts on the true muon's motion") |
| pointer to the selection-versus-features table; PET design studies use signal-only simulation banks | same (the "companion analysis note"; "simulated samples that contain signal events only") |

##### L103–112 (status paragraph) → findings summary, items 1, 2, 4, 5 and the closing sentence
| base content | new location |
|---|---|
| the headline results have different levels of validation | opening sentence: "Our results have different levels of validation …" |
| the 2D central value reproduces the published measurement | item 1 |
| its error budget was built with the same tree learner | item 1 ("as the central value") |
| the quoted statistical band awaits an independent coverage test (+ comment L106–107) | item 1, last sentence; the comment follows it verbatim, plus the plain-language comment |
| the higher-dimensional central values pass particular recovery checks | item 2 |
| adoption of their covariance under an exception does not certify their intervals | item 2: "in use under a documented exception …; that does not show that their error bars are right" |
| the generator tests are a separate inference | item 4, first sentence |
| PET remains method development | item 5, first sentence |
| none of these statuses supplies another's missing validation | closing sentence: "Passing one of these checks does not make up for a check that another result lacks." |

**Caveats added to the summary from the body**, so that each restated finding carries them:
- Item 1: the shape difference (L221–222); its learner dependence and the post hoc choice (L237–243); "some effects
  are not included" and "no coverage claim" (L121–128).
- Item 2: central values only and no significance (L140–142).
- Item 3: no significance (L309–310, L335); the seed moves the central values (L335–338); the corner share not
  measured (L337–338); "without uniquely establishing the cause" (L293–294).
- Item 4: under stated modelling assumptions and six conditions (L367, L381); not a new measurement (L389–390); the
  below-grid error not bounded (L402–403).
- Item 5: no eligible design (L427–428); no cross section or error bar (L416–417).
- Item 6: preliminary; only part detector-supported; a larger part extrapolated (L485–489; 6% < 28%).

The summary uses no numerals, so none is duplicated.

##### L114–128 + comments L129–136 (2D error budget) → trust-check subsection, paragraphs 3 and 4
| base content | new location |
|---|---|
| an assessment of the saved products found construction defects in an earlier version (cite TwoDFollowup2026) | "An assessment of the saved analysis outputs found errors in how an earlier version of the two-variable error budget was put together~\cite{TwoDFollowup2026}" |
| the quoted budget was rebuilt without them | same |
| sweep and its reference use the same truth inputs | "Its set of systematic variations and the reference those variations are compared with now use the same truth inputs." |
| a duplicated pion-model variation is counted once | "A pion-model variation that appeared twice is counted once." |
| the background simulation's statistics are propagated | "The statistical fluctuations of the background simulation are propagated." |
| selection-changing detector variations come from complete re-runs | "… come from complete re-runs of the analysis." |
| some effects are in no part of it: the failed-reconstruction weighting approximation, the difference between the two tree-learner implementations, the unfolding-model dependence | "Some effects are not included in any part of the budget:" with the same three. "Some" is kept, so the list does not read as exhaustive. |
| split-sample checks test precision conditional on the sample, not coverage across independent samples | paragraph 4, preceded by a one-sentence definition of a coverage test |
| validated error bars need independent full-size simulation, a validated nuisance generator, and uninspected independent-generator samples | same three items, "nuisance variations" glossed |
| no coverage claim is made | "We make no coverage claim." The comments L129–136 follow verbatim, plus the plain-language comment. |

**Placement:** the paragraph stays in Section 3. It sits right after the learner-qualification paragraph and right
before the coverage test, so the exclusions sit next to "its error bars are close in size", the claim they
qualify. This is the H1 lesson.

##### L138–143 → "What we cannot yet claim …", paragraph 1
| base content | new location |
|---|---|
| the multi-quantity central values pass the stated validation tests | "… above pass the validation tests stated with them" |
| a five-quantity uncertainty adopted under a documented exception | "We have built an uncertainty for the five-quantity result, which is in use under a documented exception to the analysis's own qualification rules" (paper `sec:uncertainty-status`: "has not met the analysis's predeclared qualification criteria … used only under a documented exception"; "only" is not imported) |
| its two-quantity (E_avail, W) version has been built | "and we have built its two-quantity (E_avail, W) version" |
| the plots still show central values only; no significance | same |
| the reason is measured, not a precaution | same |

"Has now been" (history) is dropped.

##### L145–167 (seed) → paragraphs 2 and 3 of that subsection
| base content | new location |
|---|---|
| random seed; the uncertainty on the projected result shifts by about `\sprojMeasured` % | same, with "projected result" spelled out as "the two-quantity (E_avail, W) projection of the result" (paper: "the projected uncertainty" of the `\zprojCells`-cell (E_avail, W) projection) |
| measured on two test versions built for this comparison, not on the adopted version | separate sentence; "not on the version in use" |
| more than the `\sprojBound` % fixed in advance | same |
| not shrinking: same at a quarter, a half and the whole; noise falls by nearly three between a quarter and a half | same |
| behaves like a real property; no reduction from a quarter to the full set | same |
| not established for a much larger set; one seed pair; nested subsets | same |
| five of the forty-five components unreachable by the seed; the figure is the other forty's effect; direction unmeasured | paragraph 3, "First, …" ("built with a fixed seed that this change cannot reach", from paper `sec:uncertainty-status`); "the figure above" becomes "the shift" |
| the seed moves the central values by at most `\cvMoveOverSigmaMax` % of their uncertainty | paragraph 3, "Second, …" |
| a significance would claim a precision the input does not have | same |

##### L169–177 (detector-uncertainty scope) → paragraph 4
Same content. "The MINOS efficiency" is spelled out as "the efficiency of MINOS for the muon". "Sit outside the
rebuild" becomes "are not rebuilt". "Does not by itself show … the complete set this measurement needs" is kept,
including "by itself".

##### L179–189 (end-to-end tests) → paragraph 5
| base content | new location |
|---|---|
| "Two newer end-to-end tests qualify 'pass the stated validation tests'" | "Two end-to-end tests limit what passing those validation tests means." "Newer" (history) is dropped. |
| background-inclusive pseudo-data: highest-W bias about 4% | same |
| unbinned removal: below 0.3%, about 1% in a few combined cells | same |
| truth changed by a generator-ratio pattern; follows it only partly | same |
| the pattern's flux error: a test of chosen size, not a measured generator difference | same, without "later found" (history) |
| typical cells about 10% off, highest-W much more | same |
| "Neither effect is in the quoted uncertainty yet." | same (F9) |

##### L191–208 (follow-up study) → paragraphs 6 and 7
| base content | new location |
|---|---|
| a follow-up study looked inside to find out why | same |
| iteration and capacity changes do not remove the bias; effects depend on truth and quantity | same ("the tested changes to the number of iterations and to the learner's capacity") |
| other generators: 16–31% in the worst cell; smaller than the quoted uncertainty in about half of the (E_avail, W) cells | same (F8) |
| "The truth dependence is not included in the quoted uncertainty." | moved two sentences earlier, inside the same paragraph, to sit right after the 16–31% claim it qualifies |
| background bias source: too-simple helper classifier; a larger one removes it | "an auxiliary classifier used in the background removal was too simple, and a larger one removes the bias" |
| the real-data result shifts by up to a few statistical σ under rounding | same, plus "which fails a stability test fixed in advance". This introduces the failed test the base names a sentence later without introducing it. Note `sec_5d.tex` l.112: "fails predeclared data stability". It is not tied to the larger classifier, because the note says the baseline fails too. |
| a later paired study: the candidate's bootstrap carries the rounding variability | "the bootstrap of the candidate with the larger classifier (its own resampling estimate of its statistical error)" (note l.105–117: the candidate is the raised-refinement-capacity version) |
| does not qualify the uncertainty attached to the published result, nor reverse the failed stability test | same, as two clauses (F4 flags "published result") |
| longer runs: sometimes improve, sometimes persistent residual; repeat variability not measured at the same settings; no bias–variability tradeoff established | paragraph 7, same |
| combining cells changes what is measured; changing the starting model gives no guaranteed bound | same |
| the one direct five-quantity coverage test, on a variant, failed; no coverage claimed | same |
| "Nothing new was adopted." | "We made no change to the method or the quoted uncertainty as a result of these studies." |

##### L210–212 → last paragraph of that subsection
| base content | new location |
|---|---|
| the 2D trust check is unaffected and keeps its independently constructed uncertainty | "None of these five-quantity findings affects the two-dimensional trust check, which retains its independently constructed uncertainty" |
| the learner-dependence qualification, "explained below" | "explained there" (the trust check now comes first) |

##### L216–256 (trust check) → trust-check paragraphs 1, 2 and 5
| base content | new location |
|---|---|
| reproduces an established measurement; rate about one percent (`\ratioTot`); `\binsTen` % within ten percent; a shape difference remains with the published correlations | paragraph 1, same |
| uncertainties, worked out independently, close in size (`\uqMedian` vs `\uqPaper`); ours a little smaller in the typical cell + comments L225–226 | paragraph 1, same; comments verbatim + plain-language comment |
| partly because our flux uncertainty is below the published one, reason not established; both use the ν–e and IMD constraint | same, "flux" glossed as "the beam's neutrino flux" |
| integral the other way (`\uqIntegral` vs `\uqPaperIntegral`) + comments L232–234 | same; comments verbatim + plain-language comment |
| the new method reproduces the old answer; error bars close in size | same |
| one qualification: two implementations differ by about one percent; the shape difference's size depends on which | paragraph 2, same ("two software implementations of the tree learner") |
| "We originally quoted the slower one; we now quote the faster one, because every error-bar ingredient was computed with it." | "We quote the faster one, because every ingredient of the error bars was computed with it; we had originally quoted the slower one." The justification now sits next to the choice. |
| "That choice was made after both comparisons with the published result were known." + comments L241–242 | "We made this choice after both comparisons with the published result were known." The comments sit at the same point in the sentence, plus the plain-language comment. The **post hoc disclosure is kept in full**, beside its stated justification. |
| the coverage test of the statistical part with simulated repeats | paragraph 5: "We did test the statistical part of those error bars in this way, using simulated repeats of the experiment with a known truth." ("in this way" points to the coverage definition just before) |
| uneven: many cells about right or too wide; a high-p∥ block and the largest-pT cells too narrow; pooled `\covTwoDCTwoPct` % instead of 95% | same |
| the test was of the bars as first built; the main cause found and removed | same ("the main cause of the shortfall") |
| the quoted bars were built again at the central value's learner settings, and have not been tested + comments L253–254 | same; comments verbatim + plain-language comment |
| the published numbers are unchanged by this check | same (F5) |

##### L283–296 (low recoil)
Unchanged, except that "on the maximal common grid" becomes "on the finest grid whose cell edges both measurements
share". This is the note's own definition, `sec_3d.tex` l.475: "maximal common grid --- edges present in [both]".
The missing E_avail-definition caveat is flagged in F6.

##### Fig. 3 caption (L298–314)
"For the reason given at the start of this section" becomes "for the reason given under 'What we cannot yet claim
for the multi-quantity results' below". This is a pointer update forced by the reordering. "Rebuilt with a correctly
sampled beam spectrum" is kept.

##### L318–340 (new puzzle)
"The random seed described at the start of this section" becomes "The learner's random seed, described under 'What
we cannot yet claim …' below". Everything else is the same: `\cvMoveOverSigmaMax`, the corner share not measured,
the significance not assigned, and every number.

##### Fig. 4 caption
"The estimator seed" becomes "The learner's random seed" (one name for one thing).

##### L367–390 (joint test) → two paragraphs and a list
| base content | new location |
|---|---|
| under stated modelling assumptions; five simulations named; overall and shape-only | same, plus glosses: MEC is GENIE's label for the two-nucleon process; Tune v1 is MINERvA's tuned simulation, the unfolding's starting point (Fig. 4 caption) |
| hypothesis: the generator's rates on a finite truth grid, Tune v1's shapes inside each cell | "each hypothesis gives the true cross section that generator's rate in each cell of a finite grid of true values, and Tune v1's shape inside each cell" |
| the unfolding learns from unbinned events; the grid specifies the hypothesis and the quantities | same |
| no textbook formula; about 1,340 to 1,750 pseudo-experiments per hypothesis; counted | same, "pseudo-experiments" glossed |
| at most one in each test; all ten rejected at a combined 5% error level, as designed | same, with "ten" glossed (five simulations × overall/shape) |
| some lost to time limits; rerunning those seeds recovered them, in a check reported separately; none as discrepant; one close in one robustness variant | same, clause order inside the sentence changed only |
| a test under six conditions: (1) below-grid structure; (2) the stated detector model, no calorimetric recoil-response band; (3) the stated interaction variations incl. clipped negative weights; (4) a bounded calibration shift from half/all the simulation; (5) generator energy domains; (6) finite generator statistics | the same six, as a list in the same order: (1) "structure finer than the grid, which the test does not resolve"; (2) "no uncertainty band for the calorimeter's response to the hadronic recoil energy"; (3) "including the clipping of some negative event weights"; (4) "a calibration shift, with a stated bound, that arises because …"; (5) "the range of neutrino energies each generator covers"; (6) "the finite size of each generator's simulated sample" |
| rounding sensitivity also checked; detailed in the analysis note; not a new measurement | same |

##### L392–396 (post hoc projection)
| base content | new location |
|---|---|
| post hoc; on the same coarse muon-only projection, GENIE CV not rejected, its hadronic projection rejected | same, with "post hoc" glossed and GENIE CV spelled out |
| hadronic information participates; no added power over all matched projections established | "we did not establish that the joint five-variable test adds power beyond all the matched lower-dimensional projections" |
| non-rejection is not acceptance | "A simulation that is not rejected is not thereby accepted as true." |

##### L398–403 (κ) + comments L404–405
| base content | new location |
|---|---|
| κ counts multiples of the last measured grid-refinement shift; not a confidence level | same, after a lead question and one clause on what the scan does |
| the frozen tests first lose a determinate rejection near κ = 5.26, or 5.17 with the recovered experiments | "In the tests as fixed in advance, the first decision stops being a clear-cut (determinate) rejection near κ=5.26, or 5.17 when the recovered pseudo-experiments are included." |
| ambiguous, not a determinate non-rejection | same |
| the one-direction scan does not bound the unmeasured below-grid error | same. The comments L404–405 follow verbatim. |

##### L409–417 (point-cloud transformer)
"Two studies …" is unchanged. Everything else is kept: end to end on low-level data; reconstructed recoil clusters
paired with truth final-state hadrons; the muon withheld from both classifiers (now glossed: the measured-level one
and the truth-level one); recoil-only diagnostic and method-development cross-check; not a whole-event
measurement; no cross section or error bar; the full-event version is method development only. "No point-cloud
error bar is adopted" becomes "no point-cloud error bar is used for any result" ("adopted" is project vocabulary,
R2).

##### L419–425 (improvement studies)
"Completed" is kept. More iterations, detector summaries and the missed-event treatment helped. "None of the
improvement study's frozen ten-iteration candidates qualified for coverage testing" becomes "in the first of these
studies, none of the candidate designs, each fixed in advance at ten iterations, qualified to go on to a coverage
test". The 90%/86% for the two finalists against 31% for the historical control are kept ("original PET"), with the
"available-energy tilt" glossed and both cites kept.

##### L427–435 (outcome)
| base content | new location |
|---|---|
| better recovery did not yield a qualified design; outcome `NO_ELIGIBLE_DESIGN` | "Better recovery did not give a qualified design: the study ended with no eligible design." The status code is replaced by its meaning (R2). |
| one finalist failed a robustness threshold by the frozen point rule | "under the rule, fixed in advance, that judges the point estimate" |
| the statistical comparison did not establish which was more robust; its coverage never measured | same ("this finalist's") |
| the other passed the point rules, failed its six-member interval test | "failed the test of its intervals, which are built from six repeated fits" |
| 68% → 90% aggregate; 26% at low acceptance; 79% for 95% there | same numbers ("their bin's target … over the overall distribution"; low acceptance defined) |
| over-covers in aggregate, under-covers at low acceptance | same, each glossed (more/less often than stated) |
| no design or default selected; no PET uncertainty adopted | "… no PET uncertainty is used for any result" |

##### L437–445 (interval diagnosis)
Every element is kept:
- the partial explanation (cite kept);
- point checks used one fit, intervals surrounded an average of six bootstrap fits (bootstrap glossed);
- under an additive variance model much variation averages away, helping explain the excess aggregate width;
- the event-sample component and bias do not average away;
- the diagnostic width adjustment still leaves poor coverage, especially at low acceptance; dividing by √6 is not a
  validated repair;
- the diagnosis is for the development tilt at study scale ("the available-energy tilt used in development, at the
  size of the study's samples");
- generator-case and data-scale coverage of the six-fit average unmeasured.

##### L447–457 (tree-learner comparison)
Every element is kept:
- exploratory, same events (cite kept);
- the figure shows PET's advantage on the two energy tilts;
- the ordering changes; the tree learner is better on all three generator reweightings and on the narrow bump;
- the proton-topology gap shrinks with more tree-learner iterations. This is now "the gap between them on the
  proton-content test". It does not say "PET's lead", because the larger finalist is level at k=7 (note
  `sec_pet_campaigns.tex` l.227–230);
- the binned method matches PET on the 1D tilt in development, so this is not a general ranking ("neural-network
  unfolding against unfolding on summary quantities" for "neural versus scalar");
- the comparator differs from the production LightGBM ("is a separate configuration, not the one used for the
  five-quantity results"; note l.216–218);
- its uncertainty is not tested; no precision comparison or finalist ranking;
- everything is conditional on the finite simulation banks and event scale ("the study's finite simulated samples
  and their size").

##### L459–465 (generator diagnosis)
Every element is kept:
- underfitting at the detector step and weak extrapolation to missed events (cite kept);
- exact distortion weights recover well on the same samples;
- the reco muon and scalar inputs are already in PET; adding the tree learner's scalar truth inputs is untested;
- the findings locate the shortfalls; no universal cause; the verdict is unchanged ("the outcome that no PET design
  was eligible").

##### Fig. 5 caption
"Relative to the matched tree method at its development-chosen seven iterations" becomes "relative to the tree
learner (labelled GBDT, for gradient-boosted decision trees) on the same events, at the seven iterations chosen in
development". "Conditional on the banks" becomes "conditional on the simulated samples". All numbers and the
"point-estimate comparisons, not validated uncertainty bands" sentence are kept.

##### L481–489 (extended signal definition)
"The preliminary central value is" becomes "The preliminary central value of the extended cross section is",
which defines σ_ext. Everything else is the same.

##### Numeral spellings (C1)
No numeral was respelled or merged. The new text uses only number words ("five", "ten", "six", "two") and no new
digits; the checker confirms 76 = 76.

#### 3. Invariance check, primer block (verbatim)

`python3 -I …/check_invariance.py $W 28d28626 > $S/inv-primer.out; echo rc=$?` gave `rc=1`. The non-zero status
comes from the note block (another writer's files), not from the primer.

```
== primer
  [SAME] numerals (76)
  [SAME] value macros (13)
  [SAME] cite keys (7)
  [SAME] ref targets (5)
  [SAME] labels (3)
  [SAME] comment lines: all 32 base lines survive
  [INFO] comment lines added (6):
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
```

The primer block has no `[DIFF]`. The six `[INFO]` lines are the required C5 markers. There is one beside each of
the six reworded sites that carry a `% J3/J4 provisional` comment:
- base L106 (now after summary item 1);
- L226 (trust paragraph 1);
- L232 (after the integral sentence);
- L129 (after "We make no coverage claim.");
- L241 (inside the post hoc sentence);
- L253 (after "They have not been tested.").

"Files changed outside scope: [SAME] none".

#### 4. F-list (flagged, not made)

| id | location (new text) | base text | proposed text | reason |
|---|---|---|---|---|
| F1 **base defect** | §4 takeaway | "… *and* scales to many quantities at once, where the binned method's response table does not. Using that, this analysis recovered …" | "… *and* extends to many quantities at once without the larger response table the binned method would need, although training, simulation and uncertainty estimation still become more demanding. Using that, this analysis recovered … [unchanged] … for a model-independent result. The multi-quantity results are central values only: their error bars have not been shown to be reliable." | "does not" contradicts §2 ("nothing forbids it in principle; the limitation is one of scale"; "Training … still become more demanding"). The takeaway also omits the body's central caveat on the multi-quantity results (§3 "What we cannot yet claim …"). The correction only aligns the summary with the body, so it is for the director. |
| F2 **base defect** | abstract | "why it lets us measure several quantities at once when the traditional method cannot" | "why it makes measuring several quantities at once more practical than the traditional method does" | the same contradiction with §2; alignment only |
| F3 **base defect** | §3 "Then, measure more at once", first sentence | "With the trust check passed, we used …" | "With the central value reproduced, we used …" (or "With the trust check passed for the central value and the size of its error bars, …") | the trust check's own last paragraph says the quoted statistical bars "have not been tested", and an earlier version under-covered (91% vs 95%); "passed" unqualified is stronger than the section it follows; alignment only |
| F4 **base defect** | "What we cannot yet claim …", paragraph 6 | "this does not qualify the uncertainty attached to the published result" | "this does not carry over to the uncertainty quoted for the five-quantity result" | everywhere else in the primer, "published result" means MINERvA's published 2D measurement. The source says the paired study does not "transfer to the adopted covariance" (`sec_5d.tex` l.305–306; paper: the spread "lies inside the data-bootstrap statistical uncertainty" for the joint-test estimator). As written, a reader takes it to refer to the 2D published result. Alignment with the note. |
| F5 | trust check, paragraph 5, last sentence | "The published numbers are unchanged by this check." | either "MINERvA's published numbers are unchanged by this check." or "Our quoted central value and error bars are unchanged by this check." | ambiguous; I could not tell from the sources which is meant, so it is for the author |
| F6 **base defect (omission)** | low-recoil paragraph, last sentence | "our central values lie 9.2% and 6.3% above it on the finest grid whose cell edges both measurements share" | append: "That measurement defines true available energy more broadly, so this comparison is not quantitative." | the paper (base `paper_body.tex` l.488–492) and the note (`sec_3d.tex` l.490) carry this caveat; the primer quotes the two numbers without it. It adds a caveat, so it is for Joseph (or the director, as alignment with decided content). |
| F7 | "What we cannot yet claim …", paragraphs 2–3; "A new puzzle"; Fig. 4 caption; extended-definition paragraph | `\SI{\sprojMeasured}{\percent}` (prints 6.145 %), `\SI{\cvMoveOverSigmaMax}{\percent}` (6.02 %), `\SI{\fpsSigma}{…}` (4.502e-38) | a primer-only rounded value: "about 6%" for the seed shift; "at most about 6% of their own uncertainty"; σ_ext to two figures, e.g. 4.5 × 10⁻³⁸ | false precision for a seed-driven quantity and a preliminary value (reader §6a.4, §6b.7). These are value macros, so C1 forbids changing them here. It would need either a primer-local macro defined from the same source or a literal "about 6", which is a numeral change. |
| F8 | "What we cannot yet claim …", paragraph 6 | "… 16% to 31% in the worst cell and smaller than the quoted uncertainty in about half of the (E_avail, W) cells" | "… 16% to 31% in the worst cell, and larger than the quoted uncertainty in about half of the (E_avail, W) cells" | the reader found the uncovered half is the finding (§4.3). The record has 20 of 42 cells within σ (paper comment, base `paper_body.tex` l.469), so "larger … in about half" is also true. A plainer sentence that might read stronger, so it is for Joseph (C3). |
| F9 | "What we cannot yet claim …", paragraph 5, last sentence | "Neither effect is in the quoted uncertainty yet." | "Neither effect is included in the quoted uncertainty." | "yet" implies a plan to include them, and I found no record of one; dropping it could read weaker or stronger (C3) |
| F10 | κ paragraph | the scan sentence as now worded | add before "In the tests …": "All ten decisions remain clear-cut rejections until κ is about five." | the reader read the κ paragraph as a retreat (§6a.6). The base content implies determinacy up to the first loss (CLAIMS §F, I3: "all ten decisions determinate up to κ ≈ 5.25"). A positive restatement might read as a robustness claim, so it is for Joseph (C3). |
| F11 **possible base defect** | trust check, paragraph 1 | "our *uncertainties* --- worked out completely independently --- come out close in size" | "worked out independently of the published analysis" | the same paragraph says both use MINERvA's flux constraint, and the next paragraphs list effects left out of the budget. "Completely" is stronger than the paragraph supports (reader §6b.6). |
| F12 **possible base defect** | abstract | "including a faithful reproduction of a published result" | "including a close reproduction of a published result" | the body says it "agrees with it closely" and "a shape difference remains"; "faithful" reads stronger |
| F13 | "A joint test …", paragraph 1 | "Some pseudo-experiments were lost to computing time limits. Rerunning exactly those seeds recovered them …" | "Rerunning exactly the seeds lost to computing time limits recovered them …" (one sentence) | the reader found that leading with the loss sounds sloppier than the content warrants (§6a.8); the merged sentence might read as minimizing the loss, so it is for Joseph |

#### 5. P-list (proposed cuts or moves, not made)

| id | exact text (new primer) | where it already lives |
|---|---|---|
| P1 | "Its set of systematic variations and the reference those variations are compared with now use the same truth inputs. A pion-model variation that appeared twice is counted once. The statistical fluctuations of the background simulation are propagated. And the detector variations that change which events are selected come from complete re-runs of the analysis." (replace with "The quoted budget was rebuilt without them.") | note `sec_systematics.tex` `sec:uq-2d-construction` (l.184 on); paper `sec:uq2d`; the reader called it a changelog (§2.3) |
| P2 | the PET paragraphs "Completed simulation studies then improved …", "Better recovery did not give …", "Saved outputs of these studies give …", "An exploratory comparison then ran …" and "For the three generator-model tests, …", condensed into one paragraph covering what PET is, how close it came (31% → about 90%) and why no design was eligible (one robustness failure; intervals over- and under-cover), with the cites kept | note `sec_pet_campaigns.tex` `sec:pet-campaigns` (l.2), its interval-diagnosis paragraph (l.148–167), `sec:pet-gbdt-paired` (l.206); the PET note |
| P3 | Fig. 5 (the paired-differences figure and its caption) | note `sec_pet_campaigns.tex` `fig:pet-gbdt-paired` |
| P4 | the six-item condition list and "Sensitivity to numerical rounding is also checked." (keep one sentence: "The verdict holds under six stated conditions, listed in the analysis note.") | note `sec_joint.tex` `sec:joint5d` |
| P5 | the κ paragraph "How robust are the rejections … below the grid." | note `sec_joint.tex` `sec:joint5d` |
| P6 | "Longer runs sometimes improve recovery … does not give a guaranteed error bound." | note `sec_5d.tex` `sec:val-departure` (l.83 on) and its unfolding-model-dependence paragraph |
| P7 | "(One of the two predictions behind that pattern was made with a wrongly sampled beam spectrum, so the pattern is a test of a chosen size, not a measured difference between generators.)" | note `sec_5d.tex` `sec:val-fiveaxis` / `sec:val-departure` (the flux-sampling caveat moved there 2026-10-11, EDITORIAL-20261011 table); `sec_3d.tex` flux-repair paragraph |
| P8 | Fig. 3 caption clause "the GENIE and NuWro predictions were rebuilt with a correctly sampled beam spectrum" | note `sec_3d.tex` (flux-repaired predictions, l.244–254), `sec_eavailw.tex` l.139 |
| P9 | the last sentence of the Section 2 selection paragraph, "The companion analysis note's selection-versus-features table … signal events only." | note `selection_features.tex` (input by `sec_experiment.tex` l.69); `sec_pet_campaigns.tex` l.8 |

P2–P5 would cut most of what the reader found heaviest on pp. 9–11. Each needs Joseph's decision under C4.

#### 6. Build

`$S/build_copy.sh primer`: `build_all rc=0`. All four PDFs report `OK … written by this run; no unresolved
references`:

| gate | result |
|---|---|
| `SELF-TEST` | PASS |
| `RESULT` | PASS (containment, strict mode) |
| `SELF-TEST` | PASS (18 perturbations rejected) |
| `SEC4-RECEIPTS` | PASS (15/15) |

`grep -c 'Reference.*undefined\|Citation.*undefined' main_primer.log` gives 0. The build includes the other
writers' files as they stood at build time.

| PDF | pages |
|---|---|
| main_primer | **14** (base 12) |
| main_paper | 12 |
| main_note | 124 |
| pet_note | 26 |

The rebuilt primer is `$S/builds/primer/repo/docs/analysis-note/main_primer.pdf` (sha256 `08465b4f…`). I read every
page of it. The summary list, the reordered trust check, the new subsection, the joint-test list and the PET pages
render cleanly. There are white-space gaps at the foot of pp. 2 and 6, caused by `[H]` floats; the float specifiers
were not changed.

**Same-model caveat:** written by Claude Opus 5.5. The independent preservation review (brief §4.3) should check
§2's map against `$S/primer_body.base.tex`.

---

## R5. Writer, note (round 1) — `impl-note.md` (sha256 `2e45d7f2bb9982d3…`)

### Plain-language pass: analysis note, in-scope parts (writer's implementation record)

Worktree `wt-plain`, branch `stageF/plain-language-20261018`, base `28d28626`. I edited LaTeX only and made no git
writes. Files touched: `main_note.tex` (abstract), `sec_execsummary.tex`, `sec_summary.tex`, `sec_systematics.tex`
(up to `What changes for the higher-dimensional products`), `sec_results.tex` (`Comparison to the published
measurement`, `Uncertainty budget`), `sec_validation.tex` (`Fixed-truth coverage of the 2D statistical band`).

#### 1. Summary

**What changed, by file and subsection**

- **`main_note.tex`, abstract.**
  - The long reproduction sentence is split in two.
  - "projection anchors against its lower-dimensional predecessor" becomes "integrated over the added observables,
    each reproduces the lower-dimensional result".
  - The 60-word limitations sentence becomes four sentences.
  - "qualified … at useful precision" becomes "total uncertainties that meet the useful-precision targets set in
    advance".
  - "familywise level" becomes "family-wise error rate".
  - The joint-test caveats are split into separate sentences, and "fine-grid convergence" is spelled out.
- **`sec_execsummary.tex`.**
  - The 3D–5D item gets the marginal wording.
  - In the high-E_avail item, "adopted under an exception" becomes "used under a documented exception".
  - In the joint-test item, "report-only" becomes "a robustness variant, not used for the decisions" or "outside
    the decisions", and "familywise" becomes "family-wise error rate".
  - In the Coverage item, C_2 is defined in words ("fraction within 2σ").
  - "predeclared" becomes "set in advance".
  - The item heading "Adopted covariance" becomes "Five-dimensional covariance", with "in use" and "not used".
  - Two rewordings were reverted so the summary stays at three pages (see "left alone").
- **`sec_summary.tex`.**
  - Bullet 1's coverage history is split into short sentences.
  - Bullet 2 gets the marginal wording.
  - Bullet 3: "predeclared" and "declared limit" become "specified in advance" and "set before production";
    "adopted" becomes "in use".
  - Bullet 4: "frozen" becomes "specified in advance", and "reportable uncertainty" becomes "new uncertainty on the
    cross section".
  - In the outlook, "adopted under a documented exception" becomes "in use under …", and "qualified" is spelled out.
  - In the reuse paragraph, "release candidate … replay verifier" is spelled out, and "separately settled covariance
    adoption" becomes "the choice of covariance, which was made separately".
- **`sec_systematics.tex`, from the start to before §"What changes …".**
  - Section intro: "what the construction does and does not include, and its declared conventions" is reworded.
  - §uq-universes: three printed `KNOWN_ISSUES.md` pointers (92, 95, 96) moved to comments; "standalone" and "earlier
    construction" reworded.
  - §uq-boot: the coverage history is split into short sentences, "pre-registered" is reworded, and the VL170 and
    KI-85 identifiers are removed from print.
  - §uq-2d-construction: retitled "Further checks of the 2D covariance". The review sentence, "driver digest",
    "uncommitted driver revision", "qualified by inference", "construction defect" and the KI-91/92 pointers are
    reworded or moved to comments.
  - §uq-combine:
    - "corrected construction" becomes "corrected procedure";
    - the C_PL paragraph's opening is reworded;
    - "earlier (VL175) budget" becomes "earlier budget";
    - D5's Required clause and the "cannot fail" sentence are rewritten in equivalent wording;
    - "default construction" becomes "default way to build the covariance".
  - §uq-2d-scope:
    - retitled "Scope, conventions and limitations of the 2D covariance";
    - "Endpoint" becomes "Status of the 2D result", the W1 paragraph is reworded, and the list items "not
      measured" and "neither is priced" are reworded;
    - "Declared conventions" becomes "Conventions";
    - in the G2 paragraph, "trainer" becomes "training" and "repaired" becomes "corrected";
    - "Construction limits" becomes "Other limitations", and "publication consumers" becomes "programs that use the
      covariance";
    - "digests" becomes "checksums".
- **`sec_results.tex`, §results-compare.**
  - "covariance distance", "standardized coordinate" and "indicative descriptive scale" become χ² and
    "standardized difference", "descriptive, shown for orientation only".
  - The χ² caveat paragraph is reworded ("ours-only", "standalone").
  - Two table rows, the table caption and the Fig. pull caption are reworded.
- **`sec_results.tex`, §results-uq.** "standalone" is reworded twice. "a difference the release does not explain;
  … leading inference" is reworded. The KI-95 pointer moved to a comment.
- **`sec_validation.tex`, §coverage.**
  - "in production … (the VL162 band)" becomes "in use when it ran (labelled VL162 in the appendices)", which defines
    the symbol the appendices use.
  - "pre-registered" becomes "fixed in advance" (twice).
  - "FAIL at the interim look" and "pre-registered verdict is FAIL-undercoverage" are reworded.
  - "A secondary" becomes "A secondary analysis", and "this term of the band's construction" becomes "this term of
    the band".
  - VL170 is defined ("labelled VL170 in the appendices"), and the KI-84 pointer moved to a comment.
  - "scored post hoc (historical)" and "Rescoring" become "evaluated post hoc (history)" and "Evaluating".
  - "bootstrap-on-one-toy" and "committed" are reworded, and the KI-85 pointer moved to a comment.
  - "lies outside every block of the quoted construction" becomes "what the quoted covariance does not include".

Every reworded site that carries a `% J3/J4 provisional` comment now has
`% plain-language pass (DECISION-20261018-joseph-plain-language-pass)` beside it. Where a base comment's statement
became stale because of the rewording, a new comment says what changed. Two cases:
- the D5 clause, whose comment says "verbatim";
- the W1 paragraph.
Every removed printed identifier is kept in an adjacent comment.

**Left alone, and why**

- Reverted for page budget: the exec summary must end on p. 3. A first build went to 124 pages, because the "What is
  not claimed" list spilled two lines onto p. 4. These were restored to their base wording:
  - Regularization bias: "generator-sized E_avail shape change (a fixed-size known-truth deformation …)";
  - the Table 1 caption "construction, adoption, testing and publication readiness are distinct". A second attempt
    at rewording it also spilled.

  Both rewordings are in the P-list (P4, P5), with the line that would need to go.
- Left as they read (R7, and history markers the reader needs):
  - the exec summary's Reproduction item, including "an earlier version omitted" and "was changed … after both
    comparisons … were known";
  - Low-recoil item: "flux-repaired", "pre-repair GENIE";
  - "Methodological finding", "Extended fiducial", PET;
  - §uq-ml whole;
  - the D6 (NormDISCC), D7 (POT) and D9 (J36) paragraphs;
  - the seed-related-terms paragraph apart from "digests";
  - the rest of §coverage (bullets, scope list).
- Out of scope, not touched: `result_status_rows.tex`, which feeds Table 1. It still prints "adopted under exception",
  "adoption measurements", "Frozen tests" and "no new reportable uncertainty" (see F7).
- Kept: MAT universe names (`MaRES_0`, `Flux:23`, `2p2h:0`, `MaCCQE:0`), playlist names (1A–1F, 1G–1M, 1N–1P) and
  `C_PL`. These are collaboration vocabulary, or a symbol defined in the text (the block-sum equation). The appendix
  key `\texttt{coverage-fixed-truth}` is also kept: it indexes App. provenance.

#### 2. Preservation map (each changed base paragraph)

Notation: **B** is the base paragraph's content items. **→** says where each sits in the new text. "kept" means the
same clause carries it in reworded form.

##### `main_note.tex` abstract
- **Reproduction sentence.**
  - B: reproduces the published d²σ incl. spectrum and "uncertainty scale"; computed with the central value's
    tree-learning implementation; universe and statistical blocks at the central value's training seed; "whether it
    describes the central value has not been measured".
  - → kept, now in two sentences ("own" added for the same implementation). The last clause is verbatim.
  - FACT, J3/J4 comments stay after it.
- **Marginal sentence.** B: each 3D/4D/5D unfold passes marginal checks against the lower-dimensional result, to
  ≈1–2%. → "Integrated over the added observables, each reproduces the lower-dimensional result to ≈1–2%."
- **Limitations sentence.**
  - B carries five items:
    - (a) background-inclusive tests show a purity-subtraction bias;
    - (b) a negative-weight treatment largely removes it;
    - (c) generator-sized shape-reweighting tests show a regularization bias that no quoted uncertainty includes;
    - (d) coverage and estimator-seed studies show further limits;
    - (e) the measured model dependence prevents a qualified 5D measurement with total uncertainties at useful
      precision.
  - → (a) and (b) are sentence 1 ("Closure tests that include backgrounds …").
  - → (c) is sentence 2 ("reweight the truth shape by about the size of the differences between generators").
  - → (d) is sentence 3 ("training-seed" = the estimator's seed).
  - → (e) is sentence 4. "Qualified" is rendered as "meet the useful-precision targets set in advance", per the
    note's §gbdt-model-dependence ("No reporting definition can meet the useful-precision targets"); see F3.
- **Joint-test sentences.**
  - B: reject all five predictions, in total and in shape, at 5% familywise; the tests are conditional; they recover
    known discrepancies; no demonstrated discrimination beyond matched coarse projections; interpretation limited by
    the omitted calorimetric recoil-response uncertainty and by unresolved fine-grid convergence.
  - → all kept, in this order. "Conditional" becomes "These tests hold under stated conditions". "Unresolved
    fine-grid convergence" becomes "the fine grid on which the null hypotheses are defined, whose convergence has
    not been shown" (sec_joint condition (i): "has not shown convergence").

##### `sec_execsummary.tex`
- **3D/4D/5D item.** B: ≈1–2% against the lower-dimensional result; binned MINERvA already triple-differential.
  → kept (marginal wording as above). The cites are unchanged.
- **High-E_avail item, last sentence.**
  - B: the projection's covariance is adopted under an exception; but its estimator-seed sensitivity, measured on
    two seed-varied companion products, exceeds the limit fixed before production; so the comparison is central
    value only.
  - → "used under a documented exception, but …". "Companion products" becomes "companion covariances", matching the
    exec summary's own later item. The "but" structure is kept, so the exception is not presented as caused by the
    sensitivity. "Uses central values only".
- **Joint-test item.**
  - B: five predictions in total and shape; ten simple hypotheses rejected at familywise 0.05; six stated
    conditions; each rejection survives a report-only variant with a larger assumed residual below the finest
    tested grid; that residual is unmeasured; every lost pseudo-experiment was rerun report-only and observed; no
    recovered draw changes a decision; hypothesis tests, not a measured uncertainty.
  - → all kept. "Report-only" becomes "a robustness variant, not used for the decisions" and "outside the
    decisions". The residual is "unmeasured". "All rerun and observed afterwards". "None changes a decision".
- **Coverage item.**
  - B: the earlier band undercovers a fixed truth in its tails (C₂ = \covTwoDCTwo vs 0.954); the rebuilt band has not
    been independently re-tested; the quoted block, a different ensemble, has not been tested; no 5D frequentist
    coverage.
  - → all kept. C₂ is defined as "fraction within 2σ" (the definition is in §coverage, |z| ≤ k).
- **Estimator stability.** Only "predeclared" becomes "set in advance". The rest is verbatim.
- **"Adopted covariance" item.**
  - B: four measurements, led by an estimator-seed sensitivity above its preproduction limit (measured on companion
    covariances), bound every result built from the adopted 5D covariance; the other corrected candidates are not
    adopted.
  - → heading "Five-dimensional covariance"; "Four measured limitations … qualify every result built from the
    five-dimensional covariance in use"; "the other corrected candidates are not used". "Preproduction limit" is
    kept verbatim, for page budget.

##### `sec_summary.tex`
- **Bullet 1, coverage clause.**
  - B: the first-built band failed a fixed-truth test in its tails; the rebuilt band was only rescored post hoc;
    neither it nor the quoted block has been independently tested.
  - → three sentences, all kept. "Rescored post hoc" becomes "re-evaluated post hoc, on the same pseudo-experiments",
    which is what rescoring is, per §coverage. "As first built" is kept; see F2 (possible base defect).
- **Bullet 2.** B: agree with their lower-dimensional predecessors to ≈1–2%. → "integrated over the added
  observables, agree with the lower-dimensional results to ≈1–2%".
- **Bullet 3.**
  - B:
    - the estimator does not follow generator-sized truth changes;
    - the model dependence rules out every predeclared 5D reporting definition at useful precision;
    - no 5D interval coverage is established;
    - the one adopted covariance has seed sensitivity above its declared limit;
    - so no covariance-based significance is quoted.
  - → all kept. "Does not follow" is kept. "Specified in advance", "in use", "set before production".
- **Bullet 4.**
  - B: frozen tests, calibrated through the full chain; all ten simple hypotheses rejected under six stated
    conditions; they recover established discrepancies, show no discrimination beyond matched coarse projections,
    and add no reportable uncertainty.
  - → kept. "Frozen" becomes "specified in advance"; "show no" becomes "do not show" (same reading); "no reportable
    uncertainty" becomes "no new uncertainty on the cross section".
- **Outlook, 5D sentences.**
  - B: a selection-complete scalar 5D covariance has been adopted under a documented exception; a 5D measurement with
    qualified total uncertainties at useful precision was not obtained; no reporting definition meets its precision
    targets within its rules and budget.
  - → "is in use under a documented exception"; "with total uncertainties at useful precision that meet the criteria
    set in advance"; the last clause is verbatim.
- **Reuse paragraph.**
  - B: a local release candidate with checksums and a replay verifier exists; no release tagged or deposited;
    rebuilding the documents reproduces no result; the release design has no bearing on the separately settled
    covariance adoption.
  - → "a local candidate data package, with checksums and a script that recomputes and checks its results" (App.
    release's description of RC7). The bold clause is verbatim. "Do not affect the choice of covariance, which was
    made separately".

##### `sec_systematics.tex`
- **Section intro, last sentence.** B: points to the scope subsection for what is and is not included, and for the
  conventions. → kept.
- **§uq-universes, rollup sentence.** B: Rvp1pi dropped because it encodes the same shift as Rvn1pi; 43 bands plus
  the flat normalization; KI-92. → kept; KI-92 in a comment.
- **Top bands.** B: flux with the ν–e and IMD constraint weights; KI-95; the other three band values. → kept; KI-95 in
  a comment.
- **Flux 1/Φ.**
  - B:
    - flux band \fluxBand with weights;
    - standalone combined budget \uqMedian;
    - unweighted and CV-Φ values of the earlier construction in App.;
    - MINOS universes divided by their own flux; KI-96;
    - integral σ 0.31%.
  - → kept. "Standalone" becomes "from our covariance alone"; "earlier construction" becomes "earlier budget"; KI-96
    in a comment.
- **§uq-boot, coverage sentences.**
  - B:
    - the earlier band undercovered in its tails, unevenly across bins;
    - the rebuilt (VL170) band was only rescored post hoc and partly circularly;
    - neither it nor the quoted block has been independently tested;
    - the held-out re-test is deferred until after the publication package and was not pre-registered (KI-85);
    - the original test cannot decide between "these explanations", because its truth equals the prior.
  - → all kept, in order. A connective sentence was added: "That band was then rebuilt." It restates what "the
    rebuilt band" presupposes. "Was not pre-registered" becomes "its design was not fixed in advance". The last
    sentence is verbatim; see F1 (base defect). VL170 and KI-85 are in a comment.
- **§uq-2d-construction, paragraph 1.**
  - B:
    - the review found more defects in the earlier (VL175) budget [cite];
    - the May sweep's truth input differs from its seed-42 reference;
    - EtaNCEL differs in all 205 cells, while the reco inputs agree;
    - a common displacement cancels to first order;
    - this neither invalidates the whole covariance nor supplies a correction;
    - the July sweep does not have the mismatch;
    - the unavailable May input and code revision prevent a more specific attribution;
    - the July products record no driver digest and came from an uncommitted revision;
    - seven universes, four of them also in the pilot, are reproduced to ≤1.4e-11;
    - the rest are qualified by inference from the same producer.
  - → all kept. "Does not invalidate …, and it does not supply …". "Because … are not available, the mismatch
    cannot be attributed more specifically". "Do not record a checksum of the driver code …, and that driver version
    was not committed". "Also checked in an earlier pilot". "Accepted by inference, because the same code produced
    them". VL175 is in a comment.
- **Rvn1pi paragraph.** B: double counting; 0.088% band; a real construction defect; no conclusion about the published
  analysis; the quoted block drops Rvp1pi; KI-92. → kept. "A real defect in how the covariance was built"; KI-92 in a
  comment.
- **Background-template paragraph.** Only "(KNOWN_ISSUES 91)" moved to a comment. Every number and statement is
  verbatim.
- **§uq-combine, unified-throw paragraph.** Only "construction" becomes "procedure".
- **C_PL paragraph.**
  - B carries:
    - observed inconsistency of unknown cause, carried as an uncertainty, not a measured systematic of a known
      source;
    - subsets not mutually consistent;
    - the step +6.94 ± 0.41% at 8 GeV/c;
    - raw shift small bin by bin, every marginal z below 0.7;
    - χ² 33.8 against the earlier (VL175) budget, where noise would give 1.8;
    - cause unknown, and these data cannot establish which period, if any, is correct;
    - three periods; 1N–1P treated in the same construction;
    - built against the exposure-weighted mean with no reference;
    - added after the other blocks;
    - rank ≤ 2, ~1.8 effective dof, size poorly determined at the order of 100%;
    - 2.14 / 3.31 / 5.69, 1.24–3.36, 1.97;
    - raises σ by 5.4% (max 34.5%), the integral by 9.9%, projections by ≤21% (6–7 GeV/c);
    - variance shares 9.9% and 17.1%;
    - the 1A–1F reference would give 1.45% / 1.09%;
    - the required clause: reference-free, uses the periods' own simulated responses, does not identify a correct
      period; limited by few groups, possible regularization shrinkage, and retained statistical and training noise;
      containment is not evidence of coverage;
    - its own double-ratio χ² is bounded whatever the data, so it is not a test;
    - the raw χ² 34.8 → 1.97 is a sensitivity reading only.
  - → every item kept, in the same order, with the same numbers.
  - The opening: "is an uncertainty assigned for an observed inconsistency between run periods whose cause is
    unknown; it is not a measured systematic uncertainty from an identified source".
  - "In the same way".
  - "Taking 1A–1F as the reference would give a smaller block".
  - The required clause becomes: "Because the block is built from double ratios, each period's unfolded result over
    that period's own simulated truth, it needs no reference period; it does not identify which period is correct.
    Its interpretation is limited by the small number of period groups, by possible shrinkage from the
    regularization, and by the statistical and training noise it retains. Because the block is built from the
    observed differences among the periods, it contains them automatically; this says nothing about its coverage,
    that is, about whether its size is right."
  - "For the same reason, the block's own double-ratio χ² … is bounded whatever the data, so it is not a test."
  - The base comment (which says "verbatim") stays. An added comment records the equivalent wording, which
    DRAFT-disclosures D5 allows: "or equivalent wording used".
- **"More generally" paragraph.** Only "a default construction" becomes "the default way to build the covariance".
- **§uq-2d-scope, "Endpoint" (W1).**
  - B:
    - reproducible 2D central value with a matched uncertainty construction under declared conventions;
    - full scientific closeout not achieved;
    - not independently validated for population or simultaneous interval coverage;
    - no calibrated covariance-based generator significance;
    - would need independent production-size simulation, a validated continuous nuisance generator, and
      independent-generator samples beyond the truth-level ones already inspected; none available;
    - no coverage claim;
    - GOF values indicative;
    - three items not in any block: (i) the miss-row approximation, not measured beyond the weak test; (ii) the
      learner dependence, 0.98% median, 12.2% max; (iii) the unfolding-model/regularization dependence (needs
      independent-generator samples) and response departures (assumed absent), neither priced.
  - → each item, in order:
    - "with a covariance computed with the central value's own estimator, under the conventions stated below";
    - "Full validation of the result has not been achieved";
    - "The coverage of its intervals has not been validated independently, either over repeated experiments drawn
      from independent simulated samples or simultaneously over all bins". "Population" is rendered as coverage over
      independent populations, per PLAN-20261011 Stage D/E ("untouched populations"; "simultaneous intervals").
      This is the record's sense. The reader's "bin by bin, averaged" guess is not it;
    - "The covariance also gives no calibrated significance for comparisons with generator predictions";
    - "Such validation would need … a validated generator of pseudo-data with continuously varied nuisance
      parameters … beyond the truth-level ones already examined; none is available". The continuous nuisance
      generator is glossed per PLAN-20261011 Stage D item 2;
    - "We therefore make no claim about coverage";
    - "indicative only";
    - "not included in the covariance": (i) "beyond the weak test described below, its effect has not been
      measured"; (ii) verbatim; (iii) "we assign no uncertainty for either".
- **"Declared conventions."**
  - B: about the mean of its universes (constraint-weighted for the flux), 1/N, not about the CV; the MAT universe
    law, a declared convention; centres 0.12–0.50% (0.08–2.26σ); the statistical block about the replica mean; 1.4%
    normalization, rank one.
  - → "This follows the MAT treatment of universes (§), which we use as a stated convention." The rest is verbatim.
- **G2 paragraph.**
  - B:
    - the miss-row approximation enters through completeness, not repaired;
    - tested in 2 of 187 universes (MaRES_0, Flux:23 = the largest median completeness change), seeds 42 and 43;
    - no effect resolved above the seed noise;
    - measured against σ of the earlier ten-seed block, ≈3× the block here;
    - excludes only a median effect >2σ;
    - an effect below trainer noise is not excluded;
    - not tight;
    - retraining moves the shifts by 1.28–1.29σ.
  - → all kept. "Not corrected"; "training-seed noise"; "compared the difference with"; split into two sentences.
- **"Construction limits."**
  - B: the two publication consumers (the χ² comparison and the Fig. uqbands producer) check the stored cell set
    equals the published one; it passes in every run of both on the quoted covariance; the other limits are listed
    with their blocks (the list).
  - → "The two programs that use the covariance for the reported results …". The list is kept; "the matching of
    estimator and seed".
- **Seed-related terms, last sentence.** "Their inputs' digests" becomes "the checksums of their inputs". The rest is
  verbatim.

##### `sec_results.tex`
- **§results-compare, paragraph 1.** B: shared systematics, no cross-covariance; every covariance distance and
  standardized coordinate is an indicative descriptive scale, not a calibrated GOF. → "their cross-covariance is not
  available. Every χ² and standardized difference here is therefore descriptive, shown for orientation only; none is
  a calibrated goodness-of-fit test."
- **Paragraph 2, last sentence.** "Indicative covariance distances per reported bin" becomes "Indicative values of χ²
  per reported bin". The macros and the ref are unchanged.
- **χ² caveat.**
  - B:
    - the combined χ² double-counts the shared systematics;
    - the ours-only χ² uses only the well-constrained subspace, with the truncated-spectral convention;
    - we quote pulls, the historical regularization scan of the exact-split cross-check (on an earlier covariance)
      and the truncated result together, rather than an unconstrained pseudo-inverse as a standalone GOF.
  - → all kept. "The χ² with our covariance alone is computed only in its well-constrained subspace, with a
    truncated spectral pseudo-inverse"; "as history, the regularization scan … on an earlier covariance";
    "goodness-of-fit test on its own".
- **Table rows and caption.** "Indicative covariance distance/bin" becomes "Indicative χ²/bin"; "covariance
  distances are descriptive scales" becomes "the χ² values are descriptive".
- **Fig. pull caption.** "a descriptive scale, not an independent-result pull" becomes "descriptive, not a pull between
  independent results".
- **§results-uq, paragraph 1.**
  - B:
    - the standalone budget is comparable to the published total (median and integral, with values);
    - flux is the largest band;
    - shares 0.87 and 0.83;
    - C_PL raises the median from \uqSFiveMedian to \uqMedian;
    - median smaller and integral larger;
    - part of the difference is the flux band, \fluxBand vs 4.01%;
    - the release does not explain the difference; the FHC-only constraint file is the leading inference, not
      established;
    - the constraint weights; an earlier version omitted them, 6.87%; KI-95; App.;
    - the stat and ML blocks under a tenth.
  - → all kept. "Our own combined budget, without the published covariance"; "the public release does not let us
    determine the origin of this difference, and our leading hypothesis, not established, is the FHC-only
    constraint file"; KI-95 in a comment.
- **Table uq caption.** "The standalone combined median" becomes "Our combined median".

##### `sec_validation.tex` §coverage
- **Paragraph 1.**
  - B: asks whether the 2D statistical band in production when the test ran (VL162; App. history) covers a fixed
    truth at its nominal rate; design, criteria and positive control pre-registered before any toy ran.
  - → "in use when it ran (labelled VL162 in the appendices; App.)"; "fixed in advance, before any toy was
    generated". The App. key is kept.
- **Criteria paragraph, last sentence.** "A FAIL at the interim look" becomes "A failure at the interim analysis". 100
  and 99.5% are kept.
- **Result heading and verdict.** "At the interim analysis". "The pre-registered verdict is FAIL-undercoverage, and
  the study stopped by its futility rule" becomes "By the criteria fixed in advance the band fails by undercoverage,
  and the study stopped under its futility rule". The recomputation sentence is verbatim.
- **Positive control.** "Both directions are flagged" becomes "the test flags both directions".
- **Completeness paragraph.**
  - B:
    - the replicas divide by a bootstrapped completeness;
    - a secondary was added by amendment after the pilot;
    - it overcovers (C₁);
    - attributed by the rule fixed before the full run, with the undercoverage branch written after the pilot pulls;
    - attribution partial (the 40–60 GeV/c column);
    - removed on 2026-10-06 and rebuilt (VL170; KI-84; App.);
    - the quoted block is now a different ensemble;
    - this result is for the earlier band, not re-tested.
  - → all kept. "A secondary analysis, added by an amendment after the pilot"; "attributed to this term of the band";
    "labelled VL170 in the appendices". KI-84 is in a comment.
- **Rebuilt-band paragraph.**
  - B:
    - rescoring is post hoc and partly circular (MC part reuses the resampling);
    - C₂ 0.977 [0.974, 0.980], C₁ 0.781 [0.771, 0.790], both above windows;
    - wider than the toy scatter (pull RMS 0.84, mean consistent with zero);
    - the excess in the data-statistics component; ~1.6×;
    - purity does not explain it; cause not established;
    - a post hoc bootstrap-on-one-toy diagnostic with a decision rule committed before it ran;
    - consistent with the toys under-scattering;
    - neither an independent-population coverage test nor a real-data calibration;
    - the held-out-MC re-test deferred until after the package (KI-85);
    - split-sample checks cannot establish coverage across independent populations;
    - new inputs needed (§scope), which also lists what lies outside every block.
  - → all kept, numbers verbatim. Heading "evaluated post hoc (history)"; "Evaluating"; "and its cause is not
    established"; "A post hoc diagnostic that bootstraps a single toy, with a decision rule fixed before it ran";
    "The re-test on held-out simulation …"; "what the quoted covariance does not include". KI-85 is in a comment.

#### 3. Invariance check (note block, verbatim) and scope

`python3 -I …/check_invariance.py $W 28d28626 > $S/inv-note.out` gave `rc=1`. It exits 1 on any difference, and the
paper and primer blocks belong to the other writers.

```
== note
  [DIFF] numerals: lost {'92': 2, '95': 2, '96': 1, '85': 2, '91': 1, '84': 1}  gained {'2': 7}
  [SAME] value macros (84)
  [SAME] cite keys (28)
  [SAME] ref targets (147)
  [SAME] labels (36)
  [SAME] comment lines: all 264 base lines survive
  [INFO] comment lines added (36):
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)   [x15]
      % Printed pointer moved to this comment by the plain-language pass: (\texttt{KNOWN\_ISSUES.md} 92).
      % Printed pointer moved to this comment by the plain-language pass: (\texttt{KNOWN\_ISSUES.md} 92).
      % Printed pointer moved to this comment by the plain-language pass: the flux band's \texttt{KNOWN\_ISSUES.md} 95.
      % Printed pointer moved to this comment by the plain-language pass: (\texttt{KNOWN\_ISSUES.md} 96).
      % Printed pointer moved to this comment by the plain-language pass: (\texttt{KNOWN\_ISSUES.md} 85); the earlier
      % bootstrap and the rebuilt band are VL170 (printed identifier removed).
      % Printed identifier removed by the plain-language pass: the earlier 2D budget is VL175.
      % Printed pointer moved to this comment by the plain-language pass: the index identity's (\texttt{KNOWN\_ISSUES.md} 91).
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass): D5's Required clause is now in equivalent
      % wording (DRAFT-disclosures D5: "or equivalent wording used"), from "Because the block is built from double ratios" to
      % "whether its size is right"; the "its own check cannot fail" sentence follows it. The earlier budget is VL175.
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass): W1's "Full scientific closeout is not achieved" is
      % carried by "Full validation of the result has not been achieved"; "population or simultaneous interval coverage" by
      % the two coverage cases; "no calibrated covariance-based generator significance" by the next sentence; "not
      % included in any uncertainty block" by "not included in the covariance"; "neither is priced" by "we assign no uncertainty".
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass). Printed pointer moved to this comment: the 6.87 % clause's
      % (\texttt{KNOWN\_ISSUES.md} 95).
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass). Printed pointer moved to this comment: the rebuild's
      % (\texttt{KNOWN\_ISSUES.md} 84).
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass). Printed pointer moved to this comment: the deferred
      % re-test's (\texttt{KNOWN\_ISSUES.md} 85).
== files changed outside scope
  [SAME] none
```

The 15 identical `% plain-language pass (…)` lines are printed one per line in `inv-note.out`. They are collapsed to
`[x15]` here; everything else is verbatim.

**Each [DIFF] explained.**
- **Numerals lost: 92 ×2, 95 ×2, 96, 85 ×2, 91, 84.** Each is the row number of a printed `\texttt{KNOWN\_ISSUES.md}
  N` pointer. The brief says to replace KI identifiers in printed text. None is a physics number. Each survives
  verbatim in an adjacent comment (the INFO lines above), next to the sentence it belonged to:
  - 92: §uq-universes rollup, and the Rvn1pi paragraph;
  - 95: §uq-universes top bands, and §results-uq 6.87% clause;
  - 96: flux 1/Φ, MINOS;
  - 85: §uq-boot, and §coverage rebuilt-band paragraph;
  - 91: background-template paragraph, index identity;
  - 84: §coverage rebuild sentence.
- **Numeral gained: '2' ×7.** No number was added. The checker's pattern counts a digit after `{` or a space. Sources:
  - 5 new `$\chi^{2}$`, where "covariance distance" became χ² (§results-compare: paragraph 1, paragraph 2, two table
    rows, the table caption). The superscript 2 is notation;
  - 1 `$2\sigma$` in the exec summary, defining C₂ as the fraction within 2σ. This is the definition the note already
    gives (§coverage, |z| ≤ k);
  - 1 "2D" in the new paragraph title "Status of the 2D result".
- **Numeral spelling changes (C1):** none. No numeral was spelled out and no duplicate was merged.
- **Comment lines:** all 264 base lines survive verbatim, each still beside its sentence. 36 lines were added.

**Scope-hunk confirmation.** `git -C $W diff -U0 28d28626 -- sec_systematics.tex sec_results.tex sec_validation.tex
main_note.tex` base hunk starts:
- `main_note.tex`: 50, 56, 60, 68–78. These are inside the abstract, base lines 45–82.
- `sec_results.tex`: 54–202. These are inside §results-compare and §results-uq, base lines 51–206. The next
  subsection starts at base line 207.
- `sec_systematics.tex`: 19–430. The last hunk is at base line 430; §"What changes …" starts at base line 432.
- `sec_validation.tex`: 216–301. These are inside §coverage, base lines 214–314.

`sec_execsummary.tex` and `sec_summary.tex` are in scope in full. No other file was touched by me. `git status` also
shows `main_primer.tex`, `paper_body.tex` and `primer_body.tex` modified; those are the other two writers'.

#### 4. F-list (flagged, not made)

| id | location | base text | proposed text | reason |
|---|---|---|---|---|
| F1 **base defect** | `sec_systematics.tex` §uq-boot, last sentence of the coverage passage | "The original test cannot decide between these explanations, because its truth equals the prior." | Name the explanations, e.g. "The original test cannot separate a band that is too narrow from a bias toward the prior, because its truth equals the prior." The director should confirm the intended antecedent against §coverage's scope list ("Because T equals the prior, it cannot detect regularization bias toward the prior"). | "These explanations" has no antecedent in the paragraph; the explanations it once referred to were cut in an earlier edit. I kept the sentence verbatim (C7). |
| F2 **possible base defect** | `sec_summary.tex` bullet 1 (and the exec summary's "An earlier 2D statistical band") | "The statistical band as first built failed …" (base: "the first-built statistical band") | "The statistical band in use when the fixed-truth coverage test ran failed …" | §coverage calls the tested band "the 2D statistical band in production when it ran" (VL162). App. history (`app_history.tex` l.50) shows an earlier seed-varying bootstrap before VL162, so "first-built" may be inexact. I kept "as first built". |
| F3 | abstract; `sec_summary.tex` outlook | "a qualified five-dimensional measurement with total uncertainties at useful precision" | (made) "total uncertainties that meet the useful-precision targets set in advance" / "… at useful precision that meet the criteria set in advance" | I made this because §gbdt-model-dependence states it in these terms. The reviewer should check that "qualified" carried no criterion beyond the useful-precision targets and the budget rules. If it did, revert to "that pass the criteria set in advance". |
| F4 | abstract, sentence 2 | "whether it describes the central value has not been measured" | "whether its intervals cover the true value has not been tested" | It is plainer, but it narrows "describes" to coverage. I kept the base clause verbatim. |
| F5 | `sec_systematics.tex` §uq-2d-scope | "not independently validated for population … interval coverage" | (made) "… over repeated experiments drawn from independent simulated samples …" | I took "population" from PLAN-20261011 Stages D/E ("untouched populations"). If Joseph meant bin-averaged ("population of bins") coverage, the sentence needs "for the bins individually and simultaneously" instead. Please confirm. |
| F6 | exec summary, joint-test item; `sec_summary.tex` bullet 4 | "add no reportable uncertainty" / "not a measured uncertainty" | (made in the summary) "provide no new uncertainty on the cross section" | "Reportable" is project vocabulary. "No new uncertainty on the cross section" is the same claim (the record says no new reportable uncertainty), but the reviewer should confirm that it does not read as "the tests add nothing". |
| F7 | `result_status_rows.tex` (out of scope; it feeds Table 1 in the in-scope exec summary) | "One scalar-5D covariance adopted under exception"; "all four adoption measurements apply"; "Frozen tests and arithmetic recomputation"; "no new reportable uncertainty"; "Publication readiness unresolved" | "One scalar-5D covariance, used under a documented exception"; "all four measured limitations apply"; "Tests specified in advance; independent recomputation of the arithmetic"; "no new uncertainty on the cross section" | This is the same register as the in-scope text, in a file outside every writer's scope. It is left for the director. |

#### 5. P-list (proposed cuts, not made)

| id | exact text | reason |
|---|---|---|
| P1 | `sec_systematics.tex` §uq-boot: "That band was then rebuilt. The rebuilt band was only re-evaluated post hoc, on the same pseudo-experiments and partly circularly, and" | §coverage carries the rebuild and rescoring history in full (paragraph "The rebuilt band, evaluated post hoc (history)"). §uq-boot needs only "neither it [the rebuilt band] nor the statistical block quoted here has been tested independently" and the deferral sentence. The caveat about the quoted block stays with the block. |
| P2 | `sec_systematics.tex` §uq-2d-scope "Other limitations": "The other limitations are stated with their blocks: the matching of estimator and seed, … and the flux block (\S\ref{sec:results-uq})." | It is a navigation sentence; each limitation is already stated in its own subsection. The refs would have to survive elsewhere (C1), so this is only a proposal. |
| P3 | `sec_results.tex` §results-compare, paragraph 1: "Every $\chi^{2}$ and standardized difference here is therefore descriptive, shown for orientation only; none is a calibrated goodness-of-fit test." | The same caveat is restated in the χ² paragraph, Table 2's caption and the Fig. pull caption. One statement per subsection plus the captions would do. |
| P4 | `sec_execsummary.tex` High-E_avail item: "(measured on two seed-varied companion covariances)" | The "Five-dimensional covariance" item below repeats "(measured on companion covariances)". Cutting the first frees about one line on p. 3. That line would allow the Regularization item to become "an $\Eavail$ shape change of about the size of generator differences (a known-truth deformation of fixed size, not a measured generator difference)" instead of the coined "generator-sized", which I reverted for page budget. |
| P5 | `sec_execsummary.tex` Table 1 caption: "Current scalar results: construction, adoption, testing and publication readiness are distinct." | Replace it with "Current scalar results." The four column headings already make the distinction. My plain rewording ("how each uncertainty is built, which products are used, what is tested and publication readiness are separate questions") pushed the summary to a fourth page and was reverted. |

#### 6. Build

`$S/build_copy.sh note`, final run: `build_all rc=0`.
- `main_note.pdf`, `main_primer.pdf`, `main_paper.pdf` and `pet_note.pdf`: each "written by this run; no unresolved
  references".
- The only "undefined" lines in `main_note.log` are the 30 `T1/cmtt` font-shape warnings, which the base build also
  has.
- Containment gate: `RESULT :: PASS` (self-test PASS). Sec. IV receipt gate: `SEC4-RECEIPTS :: PASS (15/15)`
  (self-test PASS, 18 perturbations rejected). It reads `paper_body.tex` and `values.tex` only, so no note wording
  affects it.
- Page counts: **main_note 123** (base 123), main_paper 12, main_primer 14, pet_note 26. The paper and primer counts
  include the other writers' concurrent edits; they were 11 and 12 at base.
- An intermediate build was at 124: the exec summary spilled two lines, then one. It was fixed by restoring two
  rewordings (see §1).

---

## R6. Independent preservation review, paper (386ece45) — `review-paper.md` (sha256 `3320b27e6ae6d9eb…`)

### Independent preservation review: the paper (plain-language pass)

Reviewer: fresh context, read-only, no authorship of the pass. Base `28d28626`, new `386ece45`.
Files: `docs/analysis-note/main_paper.tex` (abstract, Data availability), `docs/analysis-note/paper_body.tex`.
Method: I read the whole base and new text paragraph by paragraph (comments excluded), from `git show` of each commit.
I used the writer's map (`impl-paper.md` §2) only as a lead. Glosses were checked against the note sources at
`386ece45` and the records the LaTeX comments cite. Line numbers are in `386ece45`.

Counts: **MATERIAL 3, MINOR 10, NOTE 7.**

#### Findings

| id | sev | base text (28d28626) | new text (386ece45) | what is wrong | minimal fix |
|---|---|---|---|---|---|
| R1 | MATERIAL | Intro: "The higher-dimensional central values pass their marginal anchors"; IV C: "agreement with the marginal anchors coexists"; Concl.: "The higher-dimensional central values pass marginal anchors" | `paper_body.tex` 62–63 "The higher-dimensional central values agree with their lower-dimensional marginals"; 491 "agreement with the lower-dimensional marginals coexists"; 923–924 "The higher-dimensional central values agree with their lower-dimensional marginals" | **A widened word (H3 type).** The anchor is a normalization check: the abstract says "marginal normalizations", and IV C (456–458) says "marginal normalizations agree at the approximately 1–2% level". The note says the 3D→2D anchor's "*normalization* agrees closely", but "The *shape* agrees less closely" (χ²/ndf = 4.98, about 4.4% per-bin scatter; `sec_3d.tex` §`sec:3d-anchor`). "Agree with their lower-dimensional marginals" claims agreement of the whole marginal distribution, shape included. That is stronger than the base and than the note. | "agree in normalization with the lower-dimensional results they extend" (Intro, Concl.); IV C: "agreement in the marginal normalizations coexists with …" |
| R2 | MATERIAL | IV B endpoint: "the construction has not been independently validated for population or simultaneous interval coverage" | `paper_body.tex` 410–412 "Neither the average coverage of its per-bin intervals nor their simultaneous coverage over all bins has been independently validated" | **Wrong gloss (rule 3).** In this project, "population" means independent event populations, not an average over bins. DECISION-20261014 §2 names the missing inputs as independent production-size MC. `sec_validation.tex` 297 has "coverage across independent populations", the KI-85 diagnostic is "neither an independent-population coverage test …", and the plan's Stage E reads "On untouched populations, assess … coverage". The project calls an average over bins "pooled" (Table `tab:validation-questions`: "Coverage pooled over bins is not a simultaneous probability"). The same pass glossed the same phrase differently in the note (`sec_systematics.tex` 331–333: "either over repeated experiments drawn from independent simulated samples or simultaneously over all bins"), so the paper and the note now define one decided W1 phrase in two ways. No limitation is weakened: "average … not validated" still implies that per-bin coverage is not validated. But the definition is incorrect, and it points the reader at the pooled test, the one kind of test that *was* run, on the earlier band. | Use the note's wording: "The coverage of its intervals has not been validated with independent simulated samples, either bin by bin or simultaneously over all bins, and the covariance provides …" |
| R3 | MATERIAL | Sec II: "The GENIE and NuWro predictions use a corrected flux sampling (an exact event-by-event reweighting …)"; Sec V: "(same-sample ratios computed with GENIE before its flux correction)" | `paper_body.tex` 152–153 "The GENIE and NuWro predictions are reweighted exactly, event by event, to the analysis flux"; 510–511 "(same-sample ratios computed with GENIE without its exact flux reweighting)" | **A caveat softened (H-list: dropped qualifier).** The base tells the reader that the flux sampling was *corrected*, so the FSI ratios were made on the uncorrected, defective sample. `sec_3d.tex` 237–247 describes that defect: wide high-energy bins were under-weighted, which suppressed high-p∥ predictions and rates, and "The FSI-dial studies … retain unrepaired samples". The new text drops "corrected" in Sec II, and "without its exact flux reweighting" reads as a missing refinement, not a known defect. | Sec II: "use a corrected flux: they are reweighted exactly, event by event, …"; Sec V: "(same-sample ratios computed with GENIE samples whose flux sampling had not been corrected)" |
| R4 | MINOR | abstract: "the three- and four-observable central values pass injected-shape closure checks"; Intro/Concl.: "pass injected-shape closure tests" | `main_paper.tex` 58–59 "the three- and four-observable central values recover injected shape changes in closure tests"; `paper_body.tex` 64–65, 925–926 (same) | "Pass [the] checks", which is relative to their thresholds, became an unqualified "recover injected shape changes". The note says "passes depend on deformation and amplitude" (`tab:validation-questions`). The 3–4-observable scope keeps the 5D partial recovery (472) outside this sentence, so this is not material, but the sentence reads stronger. | "pass closure tests with injected shape changes" |
| R5 | MINOR | abstract: "without demonstrated discrimination from the tested joint information beyond matched coarse projections" | `main_paper.tex` 70–71 "they do not show that the joint five-observable information discriminates beyond matched coarse projections of the same cells" | The qualifier "the tested" was dropped (H-list). The negative statement now reads as being about five-observable information in general, not about the 3⁵ joint grid that was tested. "Of the same cells" partly re-anchors it. | "… that the tested joint five-observable information discriminates …" |
| R6 | MINOR | abstract: "These conditional tests recover known discrepancies"; Intro: "reject at the 5% familywise level under six stated conditions" | `main_paper.tex` 69 "These tests hold only under stated conditions."; `paper_body.tex` 77–78 "reject at the 5% familywise level.  They hold under six stated conditions" | The condition stays next to its claim, but "tests hold" is not standard English: what holds is the rejection. In the Intro, "reject at the 5% familywise level." is now a complete sentence with no conditions. | abstract: "These rejections hold only under stated conditions."; Intro: "… reject at the 5% familywise level under six stated conditions (Sec. VI B). Two of them, …" |
| R7 | MINOR | IV B: "in \covTwoDNtoy{} pre-registered closure pseudo-experiments against a fixed truth" | `paper_body.tex` 378–380 "in \covTwoDNtoy{} closure pseudo-experiments against a fixed truth, specified before they were run:" | The participle can attach to "a fixed truth" rather than to the pseudo-experiments. "Pre-registered" also covered the scoring windows, not only the run. | "in \covTwoDNtoy{} closure pseudo-experiments, specified in advance, against a fixed truth:" |
| R8 | MINOR | IV intro: "Missed-event bookkeeping is an invariant check" | `paper_body.tex` 221–222 "The bookkeeping of missed events (those that fail reconstruction) is checked for invariance" | The meaning changed. The base means a check of invariants: the note's `tab:validation-questions` says "Membership and completeness invariants". "Checked for invariance" suggests invariance under some change. | "The bookkeeping of missed events (those that fail reconstruction) is checked for completeness, an identity that must hold, …" |
| R9 | MINOR | IV B run period (D5 Required): "Containment of the observed differences by this construction is not evidence of coverage." | `paper_body.tex` 350–352 "Because the block is built from the differences among the periods, it covers them automatically; this says nothing about whether its size is right." | This follows the brief's R1 model sentence, so it is allowed. But "covers" is used for containment one paragraph before "coverage" is used in its statistical sense (365–372), and the D5 key term "coverage" is gone. A reader can take "covers them automatically" as a coverage statement. | "… it contains them by construction; this says nothing about its coverage, that is, whether its size is right." |
| R10 | MINOR | IV B: "Its reference-free double-ratio construction uses the periods' own simulated responses; it does not identify a correct period." | `paper_body.tex` 345–348 "The block uses double ratios between groups, each group's unfolded result being taken over its own simulated truth, so it relies on the periods' own simulated responses and does not identify a correct period." | The double-ratio gloss is correct (comment 336–338; period-unfold REPORT §2). The added "so" makes "does not identify a correct period" follow from the double ratios. In the base, that limit comes from the block being reference-free, and is not caused by the simulated responses. | "… so it relies on the periods' own simulated responses. It does not identify a correct period." |
| R11 | MINOR | Fig. 4 caption: "for the claim variant with the largest null median" | `paper_body.tex` 753–754 "for the shifted null used in the decisions (the ``claim variants'' of the legend) with the largest null median" | Read as written, there is a single shifted null used in the decisions. VI A (638–643) says the decisions use the largest p over a set of shifted nulls. | "for the one of the shifted nulls used in the decisions (the legend's ``claim variants'') with the largest null median" |
| R12 | MINOR | VII: "(\pinnedBandsSqrtTr% of √Tr C)" | `paper_body.tex` 893–894 "they make up \pinnedBandsSqrtTr% of √Tr C, the square root of the covariance's trace" | "Make up" implies an additive share of √Tr C, and square roots do not add. `values.tex` 453 gives 26.0% of √Tr C_Z next to 6.75% of the trace, so 26% is √(6.75%), not a share of √Tr C. | "the square root of their summed variance is \pinnedBandsSqrtTr% of √Tr C, …" |
| R13 | MINOR | Data availability: "A local release candidate, not yet deposited" | `main_paper.tex` 125–127 "A release package of about 16 MB [39], prepared locally but not yet deposited" | "Candidate" (not the final release) was dropped. The note says RC7 "has not been deposited or released under a publication tag" (`app_release.tex` 17–18). "Not yet deposited" keeps most of the caveat. | "A candidate release package of about 16 MB [39], prepared locally but not yet deposited, …" |
| N1 | NOTE | — | `paper_body.tex` 408–409 "under stated conventions"; 422–424 "The analysis note [14] states these conventions" | The conventions are not stated in the paper, so "stated" points to another document. | "under conventions given in the analysis note [14]" (and drop the duplicate at 422–424, if C1 allows) |
| N2 | NOTE | — | `paper_body.tex` 876–879 "used only under a documented exception to the criteria, limited to this one covariance" | Still process register, and the reader cannot tell what the covariance is used for (writer's F9). | for Joseph (F9) |
| N3 | NOTE | — | `paper_body.tex` 903–904 "as a separate route to inference, and they produce no new uncertainty that could be reported for a measurement" | Internal register remains. | "The joint tests came from the same study; they test generator predictions directly and do not provide a measurement uncertainty." |
| N4 | NOTE | — | `main_paper.tex` 64 and `paper_body.tex` 76, 937 "meet our predefined criteria" | Not defined where it first appears (the abstract). Sec. VII defines it only by reference ("the criteria that the analysis set in advance for an uncertainty"). | name the criteria once in VII (writer's F4 asks Joseph for the numbers) |
| N5 | NOTE | — | `paper_body.tex` 686–688 "at a rate taken from the review of the test design, for which no calculation is recorded" | Process register, though accurate (writer's F6). | for Joseph (F6) |
| N6 | NOTE | — | `main_paper.tex` 133–135 "every value recorded in the package and every checked figure number" | "Checked figure number" is process vocabulary. | "every value and figure number the package verifies" |
| N7 | NOTE | — | `paper_body.tex` 754 ``claim variants'' quoted in a caption | Needed only because the out-of-scope figure legend still uses the term (writer's P10). | relabel the legend (P10) |

##### Director's base-defect correction, paper F3 (`paper_body.tex` 281–284)

New: "the fourth from LightGBM unfolds of three groups of run periods". This is **verified correct.**
`state/2d-closeout/period-unfold-20261014/REPORT.md` 42–44 defines three groups: P_A = 1A–1F, P_B = 1G, 1L, 1M, and
P_C = 1N–1P. Its table (56–61) has both P_B/P_A and P_C/P_A. The new text also agrees with the same section's "three
period groups" (342–343). The base's "three run periods" was a defect. The correction only aligns the sentence with
decided content, so a director ruling is enough under C7.

#### Paragraphs checked and found preserved

- **Abstract**, apart from R4–R6: the background, regularization, coverage and seed limits; "prevents … at useful
  precision"; the full-chain calibration under a stated nuisance model; all five predictions; total and shape; the 5%
  familywise level; the recoil-response omission (it matches condition (ii)); fine-grid convergence. "The fine grid on
  which the null hypotheses are defined" is correct: H0(G) is defined on the fine grid (598–600). "Of the same cells"
  is correct (809–810).
- **Intro para 3** ("We assess …"): each instrument now has its own test. Nothing was lost.
- **Intro para 5**, apart from R1, R4 and R6: the 4% in simulation at highest W; "used only for the generator
  tests"; the bias is not in the quoted uncertainties; the partial recovery of a generator-sized change; the
  regularization, seed and untested-coverage limits; the two interpretation-limiting conditions; the coarse-projection
  result.
- **Intro para 6** ("full details"): preserved.
- **Sec II** E_avail definition: "inherited", not corrected, 0.67%, 1.05%, and not compared with the covariance. The
  comment reads "the adopted covariance with off-diagonals", so "full covariance" is right. The shared reconstructed
  inputs sentence is preserved. For the flux sentence, see R3.
- **Sec III**: "each result below states …" is preserved. The exact-split gloss is correct against `sec_method.tex`
  §`sec:method-config` ("single-threaded exact-split CART", against LightGBM's histogram bins). "Original
  two-dimensional choice" and "selected before the joint-test design was fixed" are kept, and so is "bias of the
  purity method at nominal truth".
- **IV intro** (closure and coverage definitions), apart from R8: preserved.
- **IV A**: "indicative only" is kept. The seed spread is not measured. **The post hoc disclosure of the
  central-value switch is kept in full and is still attached** ("This choice … was made after both comparisons were
  known"). 0.98% and 12.2% are kept, and so is "not included in any term of the covariance". The cross-covariance
  sentence is unchanged in meaning.
- **IV B para 1** (blocks, medians, the 87% share, MAT flux constraints, the published 4.01% flux against ours with the
  reason unknown, the seed setting, 0.06%, about 70% in variance): preserved. Dropping "standalone" loses nothing.
- **IV B G2 paragraph**: the approximation, not corrected, 2 of 187, two seeds, an "earlier" ten-seed scan, about 3×,
  an effect below about 2× noise not excluded, and the test is not tight. All are preserved and still attached.
- **IV B run-period paragraph**, apart from R9 and R10: the inconsistency, the 7% step (as the director corrected it),
  the unknown cause, no correct period established, no reference, 2.1%, 1.2–3.4% and 2.0%, few groups, shrinkage,
  retained noise, and the self-check is not a test. D5's Required limits all survive. The double-ratio gloss matches
  the comment at 336–338.
- **IV B statistical-block paragraph (reordered within the paragraph)**: 300 replicas, the seed, three streams,
  0.684%, the 0.26σ offset not in the covariance, the quoted block not independently tested, the total untested, the
  earlier band's undercoverage (with \covTwoDCTwoPctOne% against 95.4%), the cause and the rebuild. **"Post hoc and
  partly circular" is still attached to the rescoring.** 97.7% and 78.1% are kept, so is "for reasons not
  established", the rebuilt band is not independently tested, and the "different ensemble" statement is kept. No
  caveat was separated from its claim by the reorder. The D2/D8 and VL169 comments moved with their sentences. For
  wording, see R7.
- **IV B earlier-budget errors**: both defects and "the quoted covariance is free of both" are kept.
- **IV B endpoint (W1/D1)**, apart from R2: the estimator-matched covariance, "not fully validated" (this carries
  DECISION-20261014 §2's meaning: independent validation is lacking), no calibrated generator significance, the three
  terms in no block, the detector-response assumption, the three missing inputs, "We make no claim about coverage",
  and the pointer to the note.
- **IV C para 1**: preserved, including "deterministic variant", the 4%, the 0.3%, 1% and 1.4%, and "signal only".
- **IV C para 2**, apart from R1: the 74% and 16–31%; the regularization bias is not in the uncertainties; "the
  tested ranges" is kept. Rounding-level spread; "deterministic variant"; "failed its criterion, fixed in advance" at
  nominal truth and under the tilt; 5D coverage not established.
- **Sec V**: the low-E_avail paragraph (apart from R3), the 52%, the FSI scope, 1.09 and 1.06, the 11%, and "has not
  been computed, so … not quantitative". (E_avail,W) is descriptive: there is no significance, no closure test with a
  mismodelled detector response, and the bias is largest there. The generator-context paragraph's GiBUU "contrast"
  gloss is correct: `sec_eavailw.tex` 119 says "corner-to-integrated contrast".
- **VI A** hypotheses and statistics (unchanged). The calibration paragraph is preserved: the largest p over shifted
  nulls fixed in advance, and λ from the estimator's pull. The "determined" gloss is correct: the CP interval lies
  entirely on one side of the threshold. **Both data-informed disclosures are kept with full content**, including
  "changed no statistic, shifted null, threshold, or stopping rule" and the validity at the number reached. The
  recomputation in all \jtRecompRows quantities is kept.
- **VI B condition (i)**: "within each fine-grid cell" is equivalent to "below the fine grid". Convergence is not
  shown; the L2 step fraction is kept; the residual is "unmeasured and potentially material"; **"Before any result was
  known"** is kept; so are the assumed extrapolation, "no calculation is recorded", one to three times the last step,
  the central estimate for the decisions, the robustness upper end outside the decisions, "slower convergence", the
  carry-over condition with "only if", the scan "separately from the decision rule", and "bounds neither". Conditions
  (ii)–(vi) and the closing remark are preserved.
- **VI C scan**: specified before it ran, **run after the decisions, not part of the decision rule**; 5.25 and 5.17;
  one direction; bounds neither. Preserved.
- **VI C lost pseudo-experiments**: "interrupted" is kept; the worst case is kept; **rerun after the decisions,
  outside the decision rule**; the procedure was fixed and reviewed beforehand; 16 reproduced; none reaches the
  observed statistic; the "and" (no causal "so") is kept; 4.6 below 868.6. Preserved.
- **VI C last paragraph**: the coarse-projection result and **its post hoc disclosure** ("after the five-dimensional
  outcomes were known") are unchanged. The power numbers and the 172–199 of 200 are kept.
- **VI D**: the response band is absent; the net effect is not measured; the GENIE CV (pT,p∥) non-rejection with **"a
  post hoc observation"** is kept; the exploratory ±4% study, the test-beam scope including the neutron exclusion
  (unchanged, so H2 does not recur), the null not regenerated, the untested list, and "remain conditional".
- **VII para 1**, apart from R12: the criteria are not met; one cannot be applied; the exception is limited to one
  covariance; there is no significance because of seed dependence; \sprojMeasured against \sprojBound; flat with N
  (40, 80, 160); the floor fell; one seed pair, nested subsets, and large N not measured; 5 of 45 bands pinned, with
  their effect in either direction not measured. The noise-floor gloss is correct (`sec_5d.tex` 495–497).
- **VII para 2**: none could meet the targets within the rules and budget; the fallback's bounded component is
  verbatim (F8); the joint tests come from the same study and give no reportable uncertainty.
- **VIII para 1**, apart from R1 and R4: three kinds of result; descriptive only, without validated total-interval
  coverage or significance; the conditional joint tests give no reportable uncertainty; the subtraction bias is reduced
  but the regularization bias persists under the **tested** generator-sized changes; the 2D statistical block awaits
  an independent test; the learner dependence of about one unit of χ²/ndf; and "prevents … at useful precision".
- **VIII para 2**: preserved, with only the "not shown to add discrimination" rewording.
- **Data availability**, apart from R13: the CC0 open data and the earlier production; 2,374 files with SHA256; the
  dependency list; the recompute list ("recovery of the lost pseudo-experiments" equals "lost-seed resolution"); the
  figures; the empty-directory replay; **the package predates the LightGBM switch and carries the exact-split curve**;
  Fig. 1 was regenerated separately; the other numbers cannot be recomputed apart from the scan; what they need; and
  the pointer to the release appendix.

#### Post hoc disclosures inventory

All eight base disclosures survive, each still attached to its claim:
- the CV estimator switch (IV A);
- the rescoring of the rebuilt band (IV B);
- the design reviewers had seen residuals (VI A);
- the budget extension decided while the observed p values were visible (VI A);
- the scan run after the decisions (VI C);
- the lost-seed rerun after the decisions (VI C);
- the coarse-projection comparison specified after the 5D outcomes (VI C);
- the GENIE CV (pT,p∥) "post hoc observation" (VI D).

---

## R7. Independent preservation review, primer (386ece45) — `review-primer.md` (sha256 `d684acf3e8748e18…`)

### Preservation review: primer (plain-language pass)

Reviewer: independent, read-only, fresh context. I did not write the pass.
Files: `docs/analysis-note/main_primer.tex` (abstract) and `docs/analysis-note/primer_body.tex`.
Base `28d28626`, new `386ece45`. I read both versions in full from git. Line numbers `Lnnn` are in `primer_body.tex`
at `386ece45` unless marked "base" or "abstract". I used the writer's map (`impl-primer.md` §2) only as a lead and
checked each item against the base text and the note/paper sources at `28d28626`. No file was edited and nothing was
written to git; the only file I wrote is this report.

#### 1. Findings

| id | severity | base text (28d28626) | new text (386ece45) | what is wrong | minimal fix (plain register) |
|---|---|---|---|---|---|
| R1 | **MATERIAL** | base L208: "Nothing new was adopted." | L444–445: "We made no change to the method or the quoted uncertainty as a result of these studies." | **Widened word; factual error.** These studies did change a method. The primer's own L425–426 says the larger background classifier "removes the bias", and L408 describes the finer unbinned removal. Together they are the joint-test estimator. Note `sec_joint.tex` l.52–55: "the joint-test estimator (§val-departure: … negative-weight background treatment with a 400-tree, 31-leaf refinement classifier …)". `sec_5d.tex` l.176 calls it "candidate R … the raised-refinement-capacity estimator of §val-departure", and a comment in the paper (`paper_body.tex` l.468) gives "candidate R (refinement 400/31 = the joint-test estimator)". The base "adopted" meant adopted for the reported five-quantity product (compare `sec_5d.tex` l.131, "Nothing is adopted."). "No change to the method" goes beyond that and contradicts the joint-test section that follows. | "None of these studies changed the five-quantity central value or its quoted uncertainty." |
| R2 | **MATERIAL** | base L108–110: "The higher-dimensional central values pass particular recovery checks; adoption of their covariance under an exception does not certify their intervals." In the base, the caveats on this claim came right after it, in the same opening block (base L138–208, before the trust check). Base L179 is explicit about this: "Two newer end-to-end tests qualify 'pass the stated validation tests'". | L126–131, item 2: "The higher-dimensional central values pass particular recovery checks. An uncertainty for them is in use under a documented exception …; that does not show that their error bars are right. Their plots therefore show central values only, and no significance is assigned …" | **Caveat detached from its claim by the reorder (the EDITORIAL H1 pattern).** The list says it gives "each finding with how far it has been tested" (L111–112). Item 2 repeats "pass particular recovery checks", but the body's limits on that claim now sit about four pages later, under "What we cannot yet claim …" (L405–445). Those limits are: biases from the background removal and the generator-pattern test that are "not in the quoted uncertainty" (L416), the truth dependence that "is not included in the quoted uncertainty" (L423–424), and the one direct five-quantity coverage test, which failed on a variant of the method (L441–444). Items 1, 3, 4 and 6 each carry the body's main caveat; item 2 does not. The new subsection keeps each caveat with the results it qualifies, so the body is fine. The defect is only in the summary. | Append to item 2: "Other end-to-end tests show biases that are not included in that uncertainty, and the one direct test of whether such error bars contain the truth as often as stated, made on a variant of the method, failed." (no numerals, so C1 is unaffected) |
| R3 | MINOR | base L268: "With the trust check passed, we used …" | L255 (director ruling F3): "With the central value reproduced and the size of its error bars checked, we used …" | The ruling correctly removes "passed". But "checked" can read as "verified". The body only *compares* the size with the published one (L184–185, "close in size to the published ones"). It also says the quoted statistical bars "have not been tested" (L237–238), and item 1 says they "await an independent coverage test". | "With the central value reproduced, and its error bars found close in size to the published ones, we used …" |
| R4 | MINOR | base L141–143: "… we still do not assign statistical significance … The reason is worth stating plainly, because it is something we measured rather than a precaution." | L129–131, item 2: "that does not show that their error bars are right. Their plots therefore show central values only …" | "Therefore" ties central-values-only to the error bars not being shown right, which reads as a precaution. The body's reason is a measurement: the seed shift is above the tolerance fixed in advance (L366–367, L369–393). The summary's reason is not wrong, but it is not the body's reason. | "Their plots show central values only, and no significance is assigned to their differences from the simulations, because the uncertainty depends measurably on the learner's random seed." |
| R5 | MINOR | §2 base L97–98: "Removing truth-muon cuts enlarges the population being estimated without adding selected observations." Base L483–484: "We relaxed those truth-level cuts while retaining the same … reconstructed MINOS-based selection." | L151–152, item 6: "Relaxing the published cuts on the muon enlarges the population being estimated." | The item drops "truth-level" and "without adding selected observations / same selection" (note `sec_fps.tex` l.10: "the reconstructed MINOS-based selection is unchanged"). A reader can take it that the event selection was loosened. The next sentence partly covers this ("only part … newly supported by the detector"). | "Relaxing the published cuts on the true muon's motion, with the same event selection, enlarges the population being estimated without adding measured events." |
| R6 | MINOR | base L377–378: "all ten hypotheses are rejected at a combined 5% error level" | L142–144, item 4: "each of five widely used simulations is rejected, both overall and in shape alone." | The rejection level is dropped from the summary (the body keeps it, L466–468). With no level, "rejected" reads as unconditional. Words keep the summary numeral-free. | "… is rejected at a combined five-percent error level, both overall and in shape alone." (or "at the test's stated error level") |
| R7 | MINOR | base L221–222: "Judged with the published correlations between cells, a shape difference remains." | L114–116, item 1: "… reproduces MINERvA's published measurement, although a shape difference remains." | The condition (judged with the published cell-to-cell correlations) is dropped from the summary. The body keeps it (L166–168). Small scope loss. | "…, although a shape difference remains when judged with the published correlations between cells." |
| R8 | MINOR | base L433: "only 26% in low-acceptance regions" | L542–543: "only 26% of the time in regions where the detector accepts few events (low acceptance)" | The gloss is imprecise. Acceptance is the *fraction* of true events the detector selects, not the number of events. "Accepts few events" can be read as "low statistics". | "in regions where the detector records only a small fraction of the true events (low acceptance)" |
| R9 | MINOR | base L506–512 (no such sentence) | L636–637 (director ruling F1): "The multi-quantity results are central values only: their error bars have not been shown to be reliable." | The added caveat is consistent with the body, and the rest of the F1 ruling is correct. Its scope is loose, though: the joint-test rejections are multi-quantity results but not central values. The body calls the joint test "a separate inference" (L141) and "not a new measurement" (L488). | "The multi-quantity measurements are shown as central values only: their error bars have not been shown to be reliable." |
| R10 | NOTE | — (new heading) | L359: "What we cannot yet claim for the multi-quantity results" | "Yet" implies a plan to make the claim; this is the same concern as the writer's F9 about "yet" in L416. The base had "still" (base L140–141), which is milder. | "What we cannot claim for the multi-quantity results" |
| R11 | NOTE | base L368: "GENIE with and without MEC" (no gloss) | L456–457: "Here MEC is GENIE's label for the two-nucleon process" | The gloss is acceptable but loose. The paper (`paper_body.tex` l.142–144) says "GENIE + MEC" adds "the Valencia 2p2h component, which models meson-exchange currents (MEC)". MEC names the mechanism (meson-exchange currents), not just a label. | "Here MEC (meson-exchange currents) labels GENIE with its model of the two-nucleon process added" |
| R12 | NOTE | base L199: "the candidate's bootstrap" | L429–430: "the bootstrap of the candidate with the larger classifier" | "Candidate" is project vocabulary and is not defined in the primer. The identification is correct: `sec_5d.tex` l.105–117 and l.176, candidate R = raised refinement capacity. | "the bootstrap of the version of the method with the larger classifier" |
| R13 | NOTE | base L243–245: "We then tested whether the statistical part of those error bars contains a known truth as often as stated, using simulated repeats" | L228–229: "We did test the statistical part of those error bars in this way, using simulated repeats of the experiment with a known truth." | "In this way" points back to the coverage definition in L209–211, so a reader may take this test as the kind of coverage test L213–217 says is still missing. The note (`sec_validation.tex` l.216–229) describes it as a fixed-truth test, with pseudo-data drawn from this analysis's own simulation. The meaning is not changed, because the next sentences report it failing and the bars being rebuilt and left untested. | "We did run such a test on the statistical part of those error bars, using simulated repeats drawn from our own simulation against a fixed, known truth." |

#### 2. Director rulings on base defects: verification against sources

| ruling | new text | source checked | verdict |
|---|---|---|---|
| F1 (takeaway) | L628–631 "extends to many quantities at once without the larger response table … although training, simulation and uncertainty estimation still become more demanding"; L636–637 added caveat | primer §2 L31–36 and L48–53 ("nothing forbids it in principle"; "Training, the amount of simulation needed, and uncertainty estimation still become more demanding"); primer §3 L361–366 | Correct alignment. "Does not" contradicted §2 and is removed. The added caveat matches the body; see R9 for its scope. |
| F2 (abstract) | abstract: "makes measuring several quantities at once more practical than the traditional method does" | primer §2 L32, L52–53 ("makes the extensions … practical") | Correct alignment. |
| F3 | L255 "With the central value reproduced and the size of its error bars checked" | L184–185, L237–238 | Correct in removing "passed"; "checked" overreaches slightly (R3). |
| F4 | L433–435 "That finding does not carry over to the uncertainty quoted for the five-quantity central value, and it does not reverse the failed stability test." | note `sec_5d.tex` l.305–306: "The study does not regrade the stability failure, certify interval coverage, or transfer to the adopted covariance"; l.117: "addresses containment only for this candidate" | Correct. The base "published result" did read as MINERvA's 2D result. The adopted covariance belongs to the five-quantity central value, and the paired study concerns the joint-test estimator (candidate R). |
| F6 | L286–287 "That measurement defines true available energy more broadly, so this comparison is not quantitative." | paper `paper_body.tex` l.488–492: "That measurement defines true $\Eavail$ more broadly … its effect on the two common cells is uncomputed, so the comparison is not quantitative."; `sec_3d.tex` l.486–492 | Correct. It imports a caveat already decided in the paper and note. The primer drops the "uncomputed" step, which is acceptable compression, because "not quantitative" keeps the paper's strength. |
| F11 | L168–169 "worked out independently of the published analysis" | same paragraph L174–176: both use MINERvA's flux constraint | Correct. It removes "completely", which the paragraph itself contradicts. |
| F12 | abstract "a close reproduction" | L163 "agrees with it closely"; L166–168 shape difference | Correct. |
| note F2 | L235 "That test was of the statistical error bars in use when it ran." | `sec_validation.tex` l.216: "the 2D statistical band in production when it ran (the VL162 band)"; `app_history.tex` rows: VL162 succeeded an earlier seed-varying bootstrap set, so it was not the first-built band | Correct. "As first built" was inexact. The new paper text (l.378, "An earlier version of the statistical band") is consistent with it. |

Each ruling only aligns a sentence with content already in the primer, paper or note. None adds a claim that is not in
a decided source.

#### 3. Glosses checked against the note sources

| term | new text | source | verdict |
|---|---|---|---|
| MINOS | L95–96 "a second detector downstream of MINERvA that measures the muon's momentum" | `paper_body.tex` l.139 (MINOS-matched muon) | correct |
| tree learner | L96–99 the scalar classifiers "are gradient-boosted decision trees … the tree learner" | `paper_body.tex` l.175–176 ("gradient-boosted decision-tree classifiers"); the two implementations are LightGBM and exact-split scikit-learn (l.186–190) | correct. The PET comparator is HistGradientBoosting (`sec_pet_campaigns.tex` l.209), also a GBDT, and L571–572 correctly calls it a separate configuration |
| PET | L99–101 "a neural network (a 'point-cloud transformer') that reads the individual energy deposits" | base L411 already used "point-cloud transformer" | consistent with base |
| coverage | L209–211 | Table 1 | correct |
| nuisance variations | L215 | paper "validated continuous nuisance generator" | correct |
| κ / determinate | L498–506 | `paper_body.tex` l.663–666, l.695–699 (multiples of δ_fine; determinate up to about 5.2) | correct |
| MEC | L456–457 | `paper_body.tex` l.142–144 | loose (R11) |
| Tune v1 | L457–458 "MINERvA's tuned simulation, the one the unfolding starts from" | Fig. 4 caption (L339) | correct |
| GENIE CV | L490–491 "GENIE's untuned central configuration" | `paper_body.tex` l.141–143 (untuned GENIE 2.12.10 without the 2p2h component) | correct |
| post hoc | L490 "a comparison chosen after the result was known" | `paper_body.tex` l.774–775 ("specified before it was run but after the five-dimensional outcomes were known") | correct |
| ten hypotheses | L466 "five simulations, each tested overall and in shape" | Table `tab:joint` | correct |
| combined 5% level | L467 "for the ten tests" | "familywise α" (`paper_body.tex` l.619, l.694) | correct |
| finalists / which failed what | L532, L536–539 | `sec_pet_campaigns.tex` l.88–95 and l.141: L128S1T24 failed B2 and its coverage was never measured; H2S1T24 failed the intervals | "this finalist's" is correct |
| bootstrap (PET) | L551 "six fits, each to a randomly resampled copy of the events" | l.102–103 (six Poisson-bootstrap members) | correct |
| additive variance model | L552 | l.150–152 | correct |
| acceptance | L543 | — | imprecise (R8) |
| maximal common grid | L283–284 "the finest grid whose cell edges both measurements share" | `sec_3d.tex` l.475 ("edges present in both binnings") | correct |
| auxiliary (helper) classifier | L425–426 | `sec_5d.tex` l.107 (refinement classifier underfits) | correct |
| "fails a stability test fixed in advance" (added) | L428–429 | `sec_5d.tex` l.112 ("fails predeclared data stability") | correct; the base already named "the failed stability test" |
| seed facts | L371–374, L387–390 | `paper_body.tex` l.838–852 (two further covariances, separate from the one in use; the (E_avail,W) projection; 5 of 45 bands at a fixed seed the variation cannot reach) | correct |
| 16–31% "test patterns from other generators" | L421–423 | `paper_body.tex` l.449–452; `sec_5d.tex` l.127–130 | correct |
| abstract "limits on the muon's angle and momentum" | abstract | `sec_fps.tex` l.14 (θ_μ, p∥, pT) | correct |

#### 4. Paragraphs checked and preserved

Every paragraph, caption and list item was compared with its base text. Those below keep every number, limitation,
condition and post hoc disclosure, at the same strength and attached to the claim they qualify. Exceptions are noted
by finding id.

- **Abstract.** Preserved. F2 and F12 are correct; the signal-definition and cut glosses are correct; "part
  detector-supported, part simulation-dominated, kept separate" is preserved.
- **§1** (L7–25). Unchanged.
- **§2** method paragraphs and Fig. 1 (L27–62). Unchanged.
- **Prior/response paragraph** (L66–71). "Limited capacity" has the same meaning.
- **Table 1** (L73–91). The column header is reworded with the same meaning; the rows and caption are unchanged.
- **Selection versus inputs** (L93–107). Every element is kept; the MINOS, tree-learner and PET glosses are correct.
- **Findings list** (L111–157):
  - item 1: preserved, including the post hoc choice of learner, the exclusions, "no coverage claim" and the
    untested status (R7 minor);
  - item 2: R2, R4;
  - item 3: preserved, including no significance, the seed effect and the corner share not measured;
  - item 4: preserved, including the stated assumptions, six conditions, not a new measurement and below-grid error
    not bounded (R6 minor);
  - item 5: preserved;
  - item 6: R5;
  - the closing sentence is the base's at the same strength.
- **Trust check P1** (L161–185). Every number and comment is kept. F11 is correct. The flux reason is still "not yet
  established".
- **Trust check P2** (L187–195). **The post hoc disclosure is kept in full**: the faster implementation is quoted,
  the justification sits beside it, and the choice was made after both comparisons were known.
- **Trust check P3** (L197–207). The budget repairs and "Some effects are not included in any part of the budget"
  are kept, with the same three effects. The paragraph now sits right after "its error bars are close in size", the
  claim it qualifies. This is better than the base placement.
- **Trust check P4** (L209–226). The split-sample limit, the three new inputs and "We make no coverage claim" are
  kept; the comments are verbatim.
- **Trust check P5** (L228–242). The uneven result, the pooled `\covTwoDCTwoPct` vs 95%, the main cause removed and
  "They have not been tested" are kept. The note F2 ruling is correct (R13 note).
- **Fig. 2.** Unchanged.
- **"Then, measure more"** (L254–287). F3: R3. The five-coordinates caveat is unchanged. In the low-recoil paragraph,
  every caveat is kept and F6 is correct.
- **Fig. 3 caption.** Only the pointer changed. "Central values only; no band; no significance" is kept.
- **New puzzle** (L310–334). Only the pointer changed. The seed effect, the corner share not measured and no
  significance are kept.
- **Fig. 4 caption.** Only "learner's random seed" changed.
- **"What we cannot yet claim …"** (L359–449):
  - P1: the exception is kept ("to the analysis's own qualification rules" matches the paper l.835–837); central
    values only; no significance; "measured rather than a precaution";
  - P2: the seed shift, measured on test versions not the one in use, above the predeclared bound, not shrinking,
    one seed pair and nested subsets;
  - P3: the five of forty-five components, the direction unmeasured, the central-value movement and the
    significance argument;
  - P4: the detector scope, with "by itself" kept;
  - P5: the 4% / <0.3% / 1% figures, "only partly", the wrongly sampled beam spectrum (dropping "later" loses no
    needed disclosure), about 10% / highest-W "much more", and "Neither effect is in the quoted uncertainty yet";
  - P6: iteration and capacity do not remove the bias; 16–31%; about half; the truth-dependence exclusion, moved
    within the paragraph to sit right after its claim; the classifier cause; the rounding shift with its failed
    stability test; F4 correct;
  - P7: no bias–variability tradeoff established; combining cells; no guaranteed bound; the failed variant coverage
    test; "we claim no such coverage". The closing sentence: R1;
  - P8: the 2D trust check is unaffected, with its learner-dependence qualification.

  Each caveat that moved here still sits right after the multi-quantity results it qualifies and before the joint
  test. The Fig. 3 caption and the puzzle paragraph both point to it, so a reader of those results meets the caveats.
- **Joint test P1** (L453–471). The assumptions, the hypothesis construction, about 1,340–1,750 pseudo-experiments
  each, at most one, the combined 5% level, the lost and recovered seeds (in a check reported separately) and the
  robustness variant that came close are all kept.
- **Six-condition list** (L473–488). The same six conditions are kept in the same order; rounding sensitivity and
  "not a new measurement" are kept.
- **Post hoc projection** (L490–496). The post hoc disclosure is kept and glossed correctly; no added power is
  established; non-rejection is not acceptance.
- **κ paragraph** (L498–508). κ is not a confidence level; 5.26 / 5.17; ambiguous, not a non-rejection; the
  one-direction scan bounds nothing; the comments are kept.
- **PET recoil-only** (L512–523). "Diagnostic and method-development cross-check", no cross section or error bar,
  and "full-event method development only" are kept.
- **PET improvement studies** (L525–533). Kept, including the 90%/86% vs 31% figures and the cites.
- **PET outcome** (L535–547). No eligible design; the robustness failure under the predeclared point rule;
  robustness not statistically resolved; the coverage never measured; the interval failure (68→90%, 26%, 79%);
  over- and under-coverage; nothing selected; no PET uncertainty used. All kept (R8 minor).
- **PET interval diagnosis** (L549–560). Kept. "Only" in "covers only the … tilt" is supported by the next clause
  ("remains unmeasured").
- **PET–tree comparison** (L562–575). Kept. "Hold only for" is a fair plain version of "condition on".
- **PET generator diagnosis** (L577–585). Kept.
- **Fig. 5 caption.** Kept; the GBDT label is glossed correctly.
- **Extended signal definition** (L602–610) and Fig. 6. Kept; the σ_ext definition is correct.
- **Takeaway** (L627–637). F1 is correct (R9 minor).

**Register.** No internal vocabulary remains in the printed text apart from "candidate" (R12). I found no "frozen",
"adopted", "banks", "comparator", `NO_ELIGIBLE_DESIGN`, "closeout" or "construction". No "prevent", "ensure" or
"guarantee" was introduced.

**Comments (C6).** Every base comment block travels with its sentence. There are six plain-language markers and
seven director-ruling markers (F1, F2/F12, F3, F4, F6, F11, note F2).

#### 5. Counts

Report: `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/plain-language/review-primer.md`

- MATERIAL: 2 (R1, R2)
- MINOR: 7 (R3–R9)
- NOTE: 4 (R10–R13)

---

## R8. Independent preservation review, note (386ece45) — `review-note.md` (sha256 `cafadd6e2610f99d…`)

### Independent preservation review: plain-language pass, analysis note (in-scope parts)

Reviewer: fresh read-only context, no authorship of the pass. Base `28d28626`, new `386ece45`. Worktree `wt-plain`
was not modified (`git status --short` empty after the review).

Scope reviewed: `main_note.tex` abstract; `sec_execsummary.tex`; `sec_summary.tex`; `sec_systematics.tex` up to
`What changes for the higher-dimensional products`; `sec_results.tex` §results-compare and §results-uq;
`sec_validation.tex` §coverage. Each changed paragraph was read from the base with `--word-diff`, then checked
against: PLAIN-LANGUAGE.md (C1–C7, R1–R7); DRAFT-disclosures rev. 4 (D0–D12); DECISION-20261014 §2;
DECISION-20261017; DECISION-20261018 (J3–J5 and plain-language pass); DECISION-20261015 g2-carry §2 and
playlist-consistency-term §2; PLAN-20261011 §1 and Stages D/E; playlist-term DESIGN §2–§3; the note body
(sec_3d §3d-anchor, sec_eavailw, sec_5d §eavailw-adopted and §gbdt-model-dependence, sec_joint, app_history,
app_release, app_provenance); KNOWN_ISSUES rows 84, 85, 91, 92, 95, 96; EDITORIAL-20261011 §1.

#### Findings

| id | severity | base text (28d28626) | new text (386ece45, file:line) | what is wrong | minimal fix (plain register) |
|---|---|---|---|---|---|
| M1 | **MATERIAL** | "Its reference-free double-ratio construction uses the periods' own simulated responses; it does not identify a correct period." (D5 Required clause, sentence 1) | "Because the block is built from double ratios, each period's unfolded result over that period's own simulated truth, it needs no reference period; it does not identify which period is correct." (`sec_systematics.tex:297–299`) | Two defects in D5's Required clause. **(a) New, incorrect causal claim.** The block needs no reference period because each period is compared with the exposure-weighted mean of the three (DESIGN §2, "Reference: none"; the note says so at l.285–286). Double ratios do not cause this. The reference variant is built from the same double ratios: DESIGN §2 S-ref uses r_X/r_A. The sentence just before (l.296, "Taking 1A–1F as the reference would give a smaller block") is that counterexample. **(b) An element of the decided clause is replaced by a different fact.** "Uses the periods' own simulated responses" means each period is unfolded with its own MC response (DESIGN §3, "MC responses. Each period is unfolded with its own MC response"; DECISION-20261015 playlist §2, "how 1F and the per-period MC responses are handled"). The new text gives the ratio's denominator instead (own simulated *truth*, DESIGN §2). The own-response statement no longer appears anywhere in the paragraph. C5 says reworded, not reduced. DECISION-20261018 plain-language pass allows "plain wording of the same content" only. | "The block uses each period's unfolded result over that period's own simulated truth, with each period unfolded through its own simulated detector response. It compares each period with the exposure-weighted mean of the three, so it needs no reference period, and it does not identify which period is correct." Then keep the next three sentences as they are. |
| M2 | **MATERIAL** (claim strengthened; C3 says flag it, do not make it) | Abstract: "Each passes projection anchors against its lower-dimensional predecessor to ≈1–2 %." Exec summary: "each passing projection anchors against its lower-dimensional predecessor to ≈1–2 %" | "Integrated over the added observables, each reproduces the lower-dimensional result to ≈1–2 %." (`main_note.tex:61–62`); "each reproducing the lower-dimensional result, integrated over the added observables, to ≈1–2 %" (`sec_execsummary.tex:37`) | The anchors are normalization and median checks. 3D→2D gives a total +0.95 % and a median per-bin ratio of 1.0016, but "the shape agrees less closely": about 4.4 % per-bin scatter and an indicative χ²/ndf of 4.98 (`sec_3d.tex:122–133`). 5D→4D gives a total of 1.0011 and per-axis median differences of 0.3–1.5 % (`sec_eavailw.tex:32–35`). "Reproduces the lower-dimensional result to ≈1–2 %" reads as a bin-by-bin reproduction, which the body contradicts. The paper's base abstract states the same fact as "pass marginal-normalization checks". Base defect, C7: `sec_summary.tex` bullet 2 already said "agree with their lower-dimensional predecessors to ≈1–2 %" at base. The new l.22–23 keeps that reading, so the director should rule on all three sites together. | "Integrated over the added observables, each reproduces the normalization of the lower-dimensional result, and its per-axis medians, to ≈1–2 %." Shorter: "each passes marginal-normalization checks against the lower-dimensional result to ≈1–2 %." Use the same wording in the exec summary and in the summary's bullet 2. |
| m1 | MINOR | "Full scientific closeout is not achieved: the construction has not been independently validated for population or simultaneous interval coverage, …" | "Full validation of the result has not been achieved. The coverage of its intervals has not been validated independently, either over repeated experiments drawn from independent simulated samples or simultaneously over all bins." (`sec_systematics.tex:330–333`) | The strength is the same ("not achieved"), and the sentences that follow carry "independently" and the coverage scope. "Population" read as repeated sampling over independent populations matches PLAN-20261011 Stage E ("On untouched populations … coverage") and §coverage l.296–297 ("repeated-sampling coverage across independent populations"). I agree with the writer's F5 reading. The weak point is "Full validation". It is generic, and the note has a whole Validation section of passed closure tests, so a reader can take it as "some checks are pending". DECISION-20261014 §2 defines the unmet milestone as "independent validation that supports the interval, bias and covariance claims". D1 "must carry" names those three. "Bias" is carried neither by the base (except through the opaque "closeout") nor by the new text. "Over all bins" is also narrower than the record's 236 functionals (cells, integral, projections). That narrows a negative statement, so it is not a weakening. | "The independent validation that would support claims about its intervals, its bias and its covariance has not been done. In particular, the coverage of its intervals has not been tested on independent simulated samples, nor simultaneously over all reported bins and projections." |
| m2 | MINOR | "(\S…); the first-built statistical band failed a fixed-truth coverage test in its tails" | "a choice made after both comparisons were known (\S…). The statistical band then in use failed a fixed-truth coverage test in its tails." (`sec_summary.tex:14–17`) | Director correction F2. Replacing "first-built" is right: app_history l.50 shows a seed-varying bootstrap before VL162. But "then" has no antecedent of its own. Read after the previous sentence, "then" means when the LightGBM choice was made (2026-10-11). By then the band in use was the rebuilt VL170 (adopted 2026-10-06), not the tested VL162. §coverage l.216 says "in use when it ran". | "The statistical band in use when the fixed-truth coverage test ran failed it in its tails." (This is the writer's F2 proposal.) |
| m3 | MINOR | "the split data/MC streams of the earlier (VL170) bootstrap are in App. … the earlier statistical band undercovered … Neither the rebuilt (VL170) band, …" | "the split data/MC streams of the earlier bootstrap are in App. … found that an earlier statistical band undercovered … That band was then rebuilt." (`sec_systematics.tex:118–121`) | With both labels removed, two different objects now read as one. "The earlier bootstrap" is VL170, the rebuilt band. "An earlier statistical band" is VL162, the tested one. Without the label a reader takes the second as the first, and so attributes the App. data/MC streams to the band that failed. | "…the split data/MC streams of the earlier, rebuilt bootstrap (labelled VL170 in the appendices) are in App. …". Or name the tested band "the band in use when the test ran". |
| m4 | MINOR | "The projection's covariance is adopted under an exception, but the associated estimator-seed sensitivity (measured on two seed-varied companion products) exceeds …" | "The projection's covariance is used under a documented exception, but its estimator-seed sensitivity (measured on two seed-varied companion covariances) exceeds …" (`sec_execsummary.tex:49`) | "Its" assigns the sensitivity to the quoted covariance itself. §eavailw-adopted says the criterion is "predeclared and not computed for this object"; it was computed only on the companion products, "their grades do not regrade these bytes" (`sec_5d.tex:471–472, 528–531`). The base "associated" kept that distance. The parenthesis softens the problem but does not fix the possessive. | "…but the estimator-seed sensitivity measured on two seed-varied companion covariances exceeds the limit fixed before production, …" |
| m5 | MINOR | "Four measurements, led by …, bound every result built from the adopted five-dimensional covariance; the other corrected candidates are not adopted." | "Four measured limitations, led by …, qualify every result built from the five-dimensional covariance in use …; the other corrected candidates are not used." (`sec_execsummary.tex:132`) | Two problems. (a) Not all four items are limitations. Item 4 of `sec_5d.tex` (l.516–523) is a bounding measurement: seed shifts in central values are a small fraction of their uncertainty. Item 2 shows that the item-1 failure is not resampling noise. The body's word is "Four measurements bound the claims". (b) "Not used" is broader than "not adopted". The companion covariances, which are corrected candidates, are used to measure items 1, 2 and 4. | "Four measurements, led by …, limit every result built from the five-dimensional covariance in use …; the other corrected candidates are not used for any quoted result." |
| m6 | MINOR | "These conditional tests recover known discrepancies without demonstrated discrimination …" | "These tests hold under stated conditions. They recover known discrepancies, …" (`main_note.tex:77–78`) | "Conditional" is a limitation: the calibration rests on six stated conditions. "These tests hold under stated conditions" can read as an assurance that they hold. Same content, weaker force. | "These tests are valid only under stated conditions." Or: "These results are conditional on six stated assumptions." |
| N1 | NOTE | (`\texttt{KNOWN\_ISSUES.md}` 85, 91, 92, 95, 96, 84 printed) | moved to comments (`sec_systematics.tex` l.33, 48, 79, 129, 223, 250; `sec_results.tex` l.170; `sec_validation.tex` l.280, 308) | Check against the brief's question, row by row. **85** is OPEN/DEFERRED; print still says "is deferred until after the publication package" (`sec_systematics.tex:123–124`; `sec_validation.tex:293–294`). **92** is OPEN; print still says "a real defect in how the covariance was built", and that the quoted block drops Rvp1pi. **91** is OPEN; the base print gave no status beyond the pointer. **84, 95, 96** are fixed or resolved and are history. So no printed status statement was lost. What is lost is the route. The note's convention is to route tracker pointers to App. provenance's table (`tab:prov-trackers`), and that table does not list these rows. A note reader can no longer find that 85, 91 and 92 are tracked open items. | Out of scope for the writer. Director: either add `coverage-fixed-truth`-style tags for 85/91/92 to App. provenance, or accept the loss. |
| N2 | NOTE | "coverage and estimator-seed studies expose further limits" | "Coverage and training-seed studies show further limitations." (`main_note.tex:72–73`) | Same quantity, but the exec summary (l.49, 132), the summary (l.35) and sec_5d all keep "estimator-seed". The abstract now uses a different term for the same 5D finding. | Keep "estimator-seed" in the abstract, or change it everywhere. |
| N3 | NOTE | "with a decision rule committed before it ran" | "with a decision rule fixed before it ran" (`sec_validation.tex:291`) | "Committed" also said that the rule's timing is verifiable (commit `8eb40e5f`, per the comment). "Fixed" keeps the timing but loses that. | "…with a decision rule recorded before it ran". |
| N4 | NOTE | "($C_2=\covTwoDCTwo$ vs. 0.954" | "(fraction within $2\sigma$ $C_2=\covTwoDCTwo$ vs. 0.954" (`sec_execsummary.tex:98`) | Correct definition (§coverage: fraction with \|z\| ≤ k), but it reads as one run-on noun phrase. | "(the fraction within $2\sigma$, $C_2=\covTwoDCTwo$, vs. 0.954" |
| N5 | NOTE (base, C7) | "neither it nor the statistical block quoted here has been independently tested" | "neither it nor the statistical block quoted here has been tested independently" (`sec_systematics.tex:122–123`; same in `sec_summary.tex:17–18`) | Unchanged in substance, so this is not a finding against the pass. D2 says the quoted block S1 "has not been coverage-tested at all", and the exec summary says "has not been tested". "Not tested independently" lets a reader infer some non-independent test of S1. | Director: "the rebuilt band has not been tested independently, and the statistical block quoted here has not been tested". |

#### Director corrections checked

- **F1 (`sec_systematics.tex:126–128`), correct.** The new sentence names the three explanations: "whether the
  smaller statistical block reflects an efficiency gain, regularization bias or undercoverage".
  - `git log -S'these explanations'` shows the sentence was introduced in `43aaa140` (2026-10-05). At that commit
    the antecedent was the preceding sentence: the split bootstrap "cannot distinguish efficiency gain from
    regularization bias or undercoverage". Later edits cut that sentence.
  - app_history l.391–402 states the same three ("higher statistical efficiency is one of at least three
    explanations") and the same reason ("Its truth equals the prior … cannot see regularization bias").
  - "Also" is a connective only. The sentence remains a "cannot" statement, so nothing is strengthened.
- **F2 (`sec_summary.tex:16`).** Replacing "first-built" is correct per app_history l.50. The chosen "then in use"
  is ambiguous; see m2.

#### Highest-risk sites: verdicts

- **W1 (scope paragraph).** Strength preserved, and the population/simultaneous gloss matches the records. The
  wording "Full validation of the result" is weaker in precision than the endpoint ruling's definition (m1).
  Every other W1/D1 element survives:
  - no calibrated significance for generator comparisons;
  - the three missing inputs;
  - "none is available";
  - no coverage claim;
  - GOF indicative only;
  - the three exclusions, each with its "not measured" or "no uncertainty assigned".
- **D5 Required clause.** Most elements survive at full strength:
  - shrinkage, now "possible shrinkage from the regularization";
  - retained noise, "the statistical and training noise it retains";
  - few groups, "the small number of period groups";
  - "does not identify which period is correct";
  - containment is not evidence of coverage, "it contains them automatically; this says nothing about its
    coverage";
  - the check is passed by construction and is not a test, "For the same reason … bounded whatever the data, so it
    is not a test".

  The clause's first sentence is defective (M1).
- **KNOWN_ISSUES pointers.** Every open row's status that the base printed is still printed. Only the route is
  lost (N1).
- **Identifiers replaced by descriptions.** All are correct except where noted:
  - VL175 is "the earlier budget", consistent with App. `history-vl175`;
  - VL162 and VL170 are "labelled … in the appendices", and both labels are printed in app_history and
    app_provenance;
  - S5/Q are not printed in scope;
  - C_PL is kept and defined by the paragraph;
  - G2 is "the approximation in how the systematic-universe unfolds weight events that fail reconstruction";
  - X03 is "retraining moves these two universes' shifts";
  - C09/C10 are "the dependence on the unfolding model and its regularization … departures of the detector
    response from its parametrized family".

  The exceptions are m3 (VL170 removal conflates two bands) and m4.

#### Paragraphs checked and preserved (no finding)

- **Abstract.**
  - Reproduction sentences. "Own" is added; the "has not been measured" clause is verbatim.
  - "Closure tests that include backgrounds": `sec_validation.tex:154` lists background-inclusive as a closure row.
  - The regularization-bias sentence. "About the size of the differences between generators" matches sec_5d's
    "generator-sized truth departures".
  - The model-dependence sentence. "Prevents a qualified" became "is too large for … targets set in advance".
    sec_5d l.202–222 states the failure as the frozen total-width, model-component and recovery targets "within the
    budget". This is the same strength, and EDITORIAL H3 ("prevent" overstated) is not reintroduced. I accept F3.
  - Family-wise sentence.
  - "Do not demonstrate discriminating power beyond that of matched coarse projections".
  - Recoil-response and fine-grid sentence. sec_joint l.116–122: the null truth is refined to the fine grid, and
    "has not shown convergence".
- **Exec summary.**
  - Joint-test item. "Report-only" became "robustness variant, not used for the decisions" and "outside the
    decisions"; the residual stays "unmeasured".
  - Coverage item.
  - Estimator stability.
- **Summary.**
  - Bullet 1's rebuilt-band sentence. "Re-evaluated post hoc, on the same pseudo-experiments" is confirmed by
    §coverage l.284, "the same 100 toys".
  - Bullet 3.
  - Bullet 4. "No new uncertainty on the cross section" for "no reportable uncertainty" is the record's own term,
    "no new reportable uncertainty", so F6 is fine.
  - Outlook 5D sentences.
  - Reuse paragraph. "A script that recomputes and checks its results" matches app_release l.10–17, where RC7
    reproduces the joint-test results; the bold no-release clause is verbatim.
- **Systematics.**
  - Section intro.
  - §uq-universes: rollup, top bands, Flux 1/Φ ("from our covariance alone" for "standalone").
  - §uq-boot, apart from m3: history sentences, "partly circularly", deferral, "design was not fixed in advance"
    (= not pre-registered).
  - §uq-2d-construction paragraph 1. "Defects" matches the source REPORT's own word, and the H1 statement "These
    findings left the earlier printed budget unchanged" stays.
  - Rvn1pi paragraph.
  - Index-identity paragraph.
  - Unified-throw paragraph ("procedure").
  - C_PL opening. It is an uncertainty for an inconsistency of unknown cause, not a measured systematic of an
    identified source, per DECISION-20261015 §2.
  - Every C_PL number.
  - "More generally".
  - Conventions (D12, all four items).
  - G2 paragraph. All four DECISION-20261015 g2 §2 items, the "not tight" sentence and the 1.28–1.29 σ survive.
  - Other limitations (KI-90 pass statement and the list).
  - Seed-related terms ("checksums").
- **Results.**
  - Comparison paragraphs 1–3, including the χ² caveat with "as history" (C7 of J3).
  - Table 2 rows and caption.
  - Fig. pull caption.
  - §results-uq paragraph 1. "Our leading hypothesis, not established" is the same strength as "leading
    inference, not established".
  - Table uq caption.
- **Validation §coverage.**
  - Paragraph 1.
  - Criteria.
  - Verdict.
  - Positive control.
  - Completeness/secondary paragraph (the amendment timing and the partial attribution survive).
  - Rebuilt-band paragraph. Post hoc, partly circular, cause not established, neither an independent-population
    test nor a real-data calibration, deferral, and the split-sample limitation all survive.
- **Comments (C6).**
  - Base comment lines are intact.
  - Every J3/J4 site in scope has the plain-language comment beside it.
  - The stale "verbatim" comment on D5 is annotated (l.316–318).

#### Counts

MATERIAL 2 (M1, M2) · MINOR 6 (m1–m6) · NOTE 5 (N1–N5).

Report: `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/plain-language/review-note.md`

---

## R9. After-pass reader, paper (PDF at 386ece45) — `reader-after-paper.md` (sha256 `c17cb10d7843d498…`)

### Reader test: main_paper.pdf (12 pp.), read as an outside neutrino cross-section physicist

Reader persona: postdoc on a neutrino cross-section experiment. I know D'Agostini unfolding, multi-universe
systematics, chi2 against a covariance, toys and coverage, and I have heard of OmniFold. I have not seen this
project before. I read only the PDF. Quotes are transcribed from the rendered pages; math symbols are written
inline (e.g. "2δfine" for 2 δ_fine).

---

#### 1. Overall verdict

The physics content is good and unusually honest, and a referee would probably respect it once they had
worked it out. As written, though, a typical PRD reader would find large parts hard going. The trouble is not
that the paper discloses limitations. It is how they are disclosed. Limitations come one at a time as
negations ("has not been independently tested", "bounds neither ... nor ...", "is not a test", "We make no
claim about coverage"), often before the reader has been told the positive number. Internal process vocabulary
("blocks", "claim variant", "documented exception", "production", "fixed in advance", "the review of the test
design", "recovered pseudo-experiments") runs through the text, and the history of the analysis (earlier
versions, rebuilt bands, lost batch jobs, a switch of estimator) sits in the body, where a PRD paper would
give the final procedure and maybe one sentence on blinding. The cumulative effect is that I came away
trusting the analysis less than its content justifies. I also could not easily pull out the headline numbers:
how big the regularization bias is compared with the uncertainties, what the "predefined criteria" were, and
whether a generator is rejected or only a hybrid null.

- **Best sections:** Sec. V (Central-value results) reads like a normal PRD results section: concrete ratios,
  physical interpretation, one plain caveat per statement. Sec. II (Data, signal, simulation) and Sec. III
  (Unbinned unfolding) are mostly fine. Sec. VI D (Hadronic-response condition) is the best of the
  statistics material: it gives a real physics argument for why the missing band matters, with a number.
- **Worst sections:** Sec. IV B (the statistical-block paragraph and the "In summary" paragraph), Sec. VI A's
  last paragraph together with condition (i) of Sec. VI B, the lost-pseudo-experiment paragraph of Sec. VI C,
  all of Sec. VII, and Data availability. The abstract is also heavier than it needs to be: its last four
  sentences are all qualifications, and one of them leans on criteria the paper never states.

---

#### 2. Passages that read as non-physics register

For each: location, exact quote, what reads wrong, and a suggested physicist's phrasing that keeps the
limitation.

**2.1 Abstract, p. 1.**
> "These tests hold only under stated conditions. They recover known discrepancies, but they do not show that
> the joint five-observable information discriminates beyond matched coarse projections of the same cells.
> Their physical interpretation is limited because the nuisance model has no calorimetric recoil-response
> uncertainty and because convergence of the fine grid on which the null hypotheses are defined has not been
> shown."

What reads wrong: three sentences of negation in a row, and "hold only under stated conditions" without naming
any. Suggested: "The rejections are conditional on the simulated calorimetric recoil response, which carries
no uncertainty in the test, and on the null hypotheses' sub-grid shapes, whose convergence is not
demonstrated. Coarse 3×3 projections of the same cells already reject every prediction, so the tests show no
added discrimination from the joint five-observable information."

**2.2 Abstract, p. 1.**
> "The measured model dependence prevents a five-dimensional measurement with total uncertainties that meet
> our predefined criteria at useful precision."

What reads wrong: "predefined criteria" and "useful precision" are internal benchmarks that the paper never
states (see Sec. 4). Suggested: "Because the unfolded result depends strongly on the model, we do not report
five-dimensional uncertainties: the model-dependence component alone exceeds [X]% in [region]."

**2.3 Introduction, p. 2.**
> "This regularization bias, the dependence on the estimator's random seed, and the untested coverage limit
> the method, and the measured model dependence prevents a five-dimensional measurement with total
> uncertainties that meet our predefined criteria at useful precision."

What reads wrong: it lists limitations as a list of nouns, and repeats the abstract. Suggested: "The
five-dimensional result is limited by a regularization bias of up to [N]% (Sec. IV C), by sensitivity to the
classifier's random seed, and by untested interval coverage. We therefore report its central values without
uncertainties."

**2.4 Sec. II, p. 2.**
> "charged pions their energy minus an inherited constant of 135 MeV rather than the charged-pion mass ... We
> have not corrected this constant."

What reads wrong: "inherited" (inherited from what: earlier MINERvA code? Ref. [18]?) and "We have not
corrected" make it sound like a known bug. Suggested: "Following the convention of Ref. [X], charged pions
contribute E_π − 135 MeV. Using the charged-pion mass instead moves 0.67% of simulated events between true-E_avail
bins and changes no bin by more than 1.05%; we have not compared this with the covariance."

**2.5 Sec. II, p. 2.**
> "The files analysed are an earlier production of that release; their names and sizes are recorded for
> reproduction (see Data availability)."

What reads wrong: record-keeping register. Suggested: "We use the [version/date] processing of the open-data
release; file checksums are listed in Ref. [38]."

**2.6 Sec. III, p. 3.**
> "An exact-split scikit-learn estimator (one that evaluates tree splits on the exact feature values rather
> than on histogram bins), which was the original two-dimensional choice, is kept as a cross-check (Sec. IV A).
> The joint tests (Sec. VI) use a deterministic LightGBM configuration, selected before the joint-test design
> was fixed."

What reads wrong: "the original ... choice" and "selected before the joint-test design was fixed" are
history. Suggested: "As a cross-check we also unfold with an exact-split scikit-learn GBDT. The tests of
Sec. VI use a deterministic LightGBM configuration chosen before the test statistics were defined."

**2.7 Sec. IV opening, p. 3.**
> "In closure tests, truth denotes the known simulated target, the prior is the initial truth distribution,
> and the response maps truth to selected observations. A closure test measures how well a specified
> deformation is recovered. Coverage measures how often intervals contain their target over repeated
> experiments ... The bookkeeping of missed events (those that fail reconstruction) is checked for invariance,
> and the dependence on the number of iterations is a stability diagnostic; neither establishes recovery or
> coverage."

What reads wrong: a PRD audience does not need closure and coverage defined. It reads as a glossary set up so
that later sentences can deny things. "The bookkeeping ... is checked for invariance" is unclear (invariance
under what?). Suggested: delete the first three sentences, then write "We also verify that the treatment of
events failing reconstruction does not change the result [how?], and that results are stable in the number of
iterations."

**2.8 Sec. IV A, p. 3.**
> "We quote the LightGBM result as the central value, so that it uses the same estimator as its covariance.
> This choice, which replaced the exact-split result, was made after both comparisons were known."

What reads wrong: the disclosure is legitimate, but "replaced" is history. Suggested: "We take the LightGBM
result as central so that it matches the estimator used for the covariance; we note that this choice was made
after both comparisons with Ref. [9] had been seen."

**2.9 Sec. IV B, p. 3.**
> "The covariance of our two-dimensional result is the sum of four terms, which we call blocks"

What reads wrong: "blocks" is nonstandard (a covariance "block" usually means a sub-matrix) and then becomes
the word for everything ("flux block", "run-period block", "statistical block"). Suggested: "components" or
"contributions".

**2.10 Sec. IV B, p. 4.**
> "Because the block is built from the differences among the periods, it covers them automatically; this says
> nothing about whether its size is right. For the same reason, the block's own consistency check passes
> whatever the data, and it is not a test."

What reads wrong: it argues against a check the reader never heard of. Suggested: "By construction this
component covers the observed inter-period differences; with only three period groups its size is itself
poorly determined."

**2.11 Sec. IV B, p. 5, the statistical-block paragraph (worst paragraph in the paper).**
> "The coverage of this block has not been independently tested, and the coverage of the total remains
> untested. An earlier version of the statistical band undercovered in its tails in 100 closure
> pseudo-experiments against a fixed truth, specified before they were run ... The main cause, a division by
> the completeness that the bootstrap replicas carried and the central value does not, was removed in a
> rebuilt band. Rescoring the same pseudo-experiments against the rebuilt band is post hoc and partly
> circular. It removes the tail undercoverage: 97.7% fall within two standard deviations and 78.1% within
> one, so the rebuilt band is wider than the toy scatter, for reasons not established. The rebuilt band has
> not been independently tested either, and the quoted statistical block is a different ensemble from it."

What reads wrong: this is a lab-notebook account (earlier version, cause, rebuild, rescoring, caveat on the
rescoring, caveat on the rebuild, a different ensemble). I could not tell what property the quoted
statistical uncertainty actually has. Suggested: "In 100 closure toys the bootstrap statistical band
undercovered in the tails (91.2% within 2σ against 95.4%), mainly because the replicas, unlike the central
value, were divided by the efficiency. After that was corrected, the same toys give 97.7% within 2σ and 78.1%
within 1σ, i.e. mild overcoverage. This check reuses the toys that identified the problem, and the quoted
statistical covariance is an independent bootstrap ensemble with the same construction, so its coverage is not
independently established." (Confirm "same construction" is true: that is exactly what I could not tell.)

**2.12 Sec. IV B, p. 5.**
> "A review of the stored analysis products found errors in an earlier version of the uncertainty budget,
> among them a mismatch between the truth input of its systematic-universe unfolds and that of their
> reference, and statistical fluctuations of the background templates that were not propagated [25]; the
> quoted covariance is free of both."

What reads wrong: an erratum for an unpublished earlier version, cited to an internal document [25] that has
no locator. A PRD paper describes the final procedure. Suggested: drop it, or put the content positively in the
method description: "Each systematic universe is unfolded against the same truth reference as the nominal, and
the statistical fluctuations of the background templates are propagated through [method]."

**2.13 Sec. IV B, p. 5, summary paragraph.**
> "In summary, we report a reproducible two-dimensional central value with a covariance built with the same
> estimator, under stated conventions. The result is not fully validated. Neither the average coverage of its
> per-bin intervals nor their simultaneous coverage over all bins has been independently validated ... We
> make no claim about coverage."

What reads wrong: "under stated conventions" is vague. "Not fully validated" and "We make no claim about
coverage" restate the same thing three times. And "independent-generator samples that have not already been
inspected" is blinding vocabulary that is never explained. Suggested: "The two-dimensional covariance omits
[list]; the coverage of its intervals has not been tested, and establishing it would require [list]." Say it
once.

**2.14 Sec. IV C, p. 5.**
> "The unbinned negative-weight background treatment, as first measured with a deterministic variant of the
> five-dimensional LightGBM central-value estimator, reduces it to below 0.3%, leaving up to 1% in some joint
> cells"

What reads wrong: "as first measured" is history, and "a deterministic variant of the ... central-value
estimator" is a fourth estimator name. Suggested: "With the unbinned negative-weight subtraction the
high-W bias falls below 0.3% in the W marginal [if that is what is meant] and below 1% in every (E_avail, W) cell."

**2.15 Sec. IV C, p. 5.**
> "An end-to-end coverage test of bias-corrected statistical intervals from a deterministic variant of the
> estimator failed its criterion, fixed in advance, at nominal truth and under an E_avail tilt, so frequentist
> coverage of the five-dimensional intervals has not been established."

What reads wrong: "failed its criterion, fixed in advance" is a procedural verdict with no number in it.
Suggested: "In toys at nominal truth and under an E_avail tilt, bias-corrected statistical intervals covered
[x]% at 1σ (target [y]%); five-dimensional coverage is therefore not established."

**2.16 Sec. VI A, pp. 7-8.**
> "The hypotheses, statistics, shifted nulls, multiplicity and stopping rules, and every input were fixed
> before any production pseudo-experiment was run or any observed statistic computed. Two choices were informed
> by the data. The reviewers of the design had seen descriptive per-cell residuals before it was fixed. A
> bounded extension of the production computing budget was decided while the outputs of the computing jobs
> showed the observed p values used for the decisions; it changed no statistic, shifted null, threshold, or
> stopping rule, and the Monte Carlo p values remain valid at the number of pseudo-experiments reached. An
> independent recomputation with separately written code agrees with the production evaluation in all 1379
> compared quantities."

What reads wrong: "the reviewers of the design" (who are they? internal?), "production", "computing budget",
and "outputs of the computing jobs" are project-management register. "Two choices were informed by the data"
is followed by one item that is not a choice. The content (a pre-registered test, with two disclosed
deviations) is valuable and standard in spirit: HEP papers call it blinding. Suggested: "The test
specification (hypotheses, statistics, shifted nulls, Holm correction and stopping rule) was fixed before the
observed statistics were computed, i.e. the test was blinded. Two caveats: per-cell data/MC residuals had been
seen before the specification was fixed, and the maximum number of toys was raised after observed p values had
become visible; neither changed any statistic, null, or threshold. An independent implementation reproduces all
1379 compared quantities."

**2.17 Sec. VI B (i), p. 8.**
> "Before any result was known, the size of the shifts was set from an assumed extrapolation. If the step kept
> shrinking geometrically, at a rate taken from the review of the test design, for which no calculation is
> recorded, the residual would be about one to three times the last step."

What reads wrong: "for which no calculation is recorded" belongs in a lab notebook, and "the review of the test
design" is internal. Suggested: "Assuming geometric convergence at a rate of [r] (an estimate, not derived), the
remaining sub-grid residual would be one to three times the last refinement step; we shift the null by
±2δfine for the decisions and by ±3δfine in robustness checks."

**2.18 Sec. VI B (vi), p. 8.**
> "The Monte Carlo p values are exact for the simulated null to the extent that the pseudo-experiment chain
> reproduces the analysis applied to the data; the independent recomputation verifies the calculation, not
> whether the chain does so."

What reads wrong: software-QA register, and fine distinctions about what verifies what. Suggested: "The p values
assume that the toy chain reproduces the data analysis exactly; [state how this was checked, e.g. by running the
chain on the data]."

**2.19 Sec. VI C, p. 8.**
> "Batch-job time limits interrupted or prevented 224 calibration and 53 power pseudo-experiments. Had every
> interrupted one exceeded the observed statistic, no test would have been rejected. We therefore reran the
> lost pseudo-experiments after the decisions, outside the decision rule, with a procedure fixed and
> independently reviewed beforehand [34]; it first reproduced 16 completed pseudo-experiments exactly. ...
> Every submitted pseudo-experiment has now been observed"

What reads wrong: computing-operations history in a results section, and "has now been observed" is a
timestamped record. Suggested (or move to a footnote or appendix): "Of the submitted toys, 224 calibration and
53 power toys did not complete within batch time limits. Rerunning them (after verifying that the rerun
reproduces 16 completed toys exactly) gives none that exceeds the observed statistic; the closest is 4.6 below
the observed 868.6 (GENIE + MEC, shape). The results are therefore insensitive to the missing toys."

**2.20 Sec. VI C, p. 8.**
> "All ten rejections remain determined at every sampled multiplier up to 5.25δfine"

What reads wrong: "remain determined" is a sequential-testing term of art that is never explained. Suggested:
"All ten tests remain rejected (Clopper-Pearson interval entirely below the Holm threshold) for shifts up to
5.25δfine."

**2.21 Sec. VII, p. 10 (whole section).**
> "It has not met the criteria that the analysis set in advance for an uncertainty. One of these criteria
> requires a bound fixed before production and can no longer be applied to it, and the covariance is used only
> under a documented exception to the criteria, limited to this one covariance."

What reads wrong: this is governance language. I cannot tell what the criteria are, what "production" means
here, what the covariance is used for, or what the "exception" allows. Suggested: "We construct a covariance for
the five-dimensional result and its 42-cell (E_avail, W) projection, but we do not use it for inference: its
seed dependence ([quantity] changes by 6.1% between two seeds, against our 5% requirement) does not decrease with
the number of universes, which points to a systematic seed effect rather than sampling noise."

**2.22 Sec. VII, p. 10.**
> "A separate study looked for a definition of a five-dimensional measurement whose total uncertainties could
> meet these criteria. None of the definitions it considered could meet the precision targets set in advance,
> within the study's rules and computing budget. For its fallback definition, the bounded model-dependence
> component alone exceeded the target total width. The joint tests above came from the same study, as a
> separate route to inference"

What reads wrong: "a separate study", "the study's rules", "fallback definition", and "target total width" are
all internal and none is quantified. Suggested: "We also tried [coarser binnings / restricted phase space]; in
each, the model-dependence uncertainty alone exceeded [X]%, larger than our target total uncertainty of [Y]%.
This is why we report calibrated hypothesis tests (Sec. VI) instead of a five-dimensional covariance."

**2.23 Sec. VIII, p. 10.**
> "The joint tests are calibrated generator tests; they are conditional on six stated conditions and yield no
> new uncertainty that could be reported for a measurement."

What reads wrong: "yield no new uncertainty that could be reported for a measurement" repeats Sec. VII and is
an odd thing to say about a hypothesis test, which is not expected to yield an uncertainty. Suggested: "The joint
tests reject all five predictions, conditional on the simulated hadronic response and on sub-grid convergence;
they are hypothesis tests and do not provide a five-dimensional covariance."

**2.24 Acknowledgments, pp. 10-11.**
> "Results were accepted only after verification against committed evidence: predeclared criteria, independent
> recomputation by separately written code ..., and independent read-only reviews."

What reads wrong: "committed evidence" and "read-only reviews" are software-repository vocabulary. A physics
reader will not parse them. Suggested: "All quoted results were checked against pre-specified criteria and,
where noted, by independent reimplementation." (The AI-use disclosure itself is fine to keep; the long list of
model versions is unusual and could be shortened to "large-language-model coding assistants from Anthropic and
OpenAI (versions listed in [ref])".)

**2.25 Data availability, p. 11.**
> "A release package of about 16 MB [39], prepared locally but not yet deposited ... The package was assembled
> before the two-dimensional central value was changed to LightGBM, and it carries the exact-split curve.
> Fig. 1 and its numbers were instead regenerated separately ... [HOLD: deposit identifier and access route,
> after the separately authorized release decision.]"

What reads wrong: package history, and "separately authorized release decision" is internal governance.
Suggested (after deposit): "Code and derived inputs to reproduce Figs. 2-4 and Table I are available at [DOI].
Fig. 1 is reproduced by [script] in the same package."

**2.26 Fig. 4 legend and caption, p. 9.**
> legend: "null pseudo-experiments (most conservative claim variant)"; caption: "(the "claim variants" of the
> legend)"

What reads wrong: "claim variant" is internal. Suggested: "null pseudo-experiments (shifted null with largest
median)".

**2.27 Reference titles, p. 12.** [32] "frozen contract and recorded result", [33] "report-only sensitivity
scan", [34] "report-only recovery of the lost pseudo-experiments", [35] URL ".../W1-RECORD-20261006.md", [37]
".../W2B-REPORT-20261006.md", [39] "Article release candidate RC7", [25] and [38] with no locator. What reads
wrong: the core result is cited to repository markdown records with internal names. A referee will ask for
these to be in an appendix or supplemental material. At minimum give them descriptive titles ("Pre-registered
test specification and results", "Supplemental material: recovery of incomplete pseudo-experiments").

**Where the register is fine.** Sec. V throughout, for example: "Adding the Valencia 2p2h contribution fills 52%
of the data-GENIE gap below E_avail = 0.4 GeV. The conclusion about FSI applies to the chosen pion variations."
That is exactly the right weight of caveat. Also good: "The rejections are global assessments of the five
specified generator versions under the stated nuisance model; assigning a discrepancy to a kinematic region or
nuclear mechanism would require separate tests." And the Fig. 1 caption note "the two bands are correlated, so
their overlap is not a compatibility test" is a helpful, normal caveat. In Sec. III, "no hyperparameter search
was performed on data" is a good, plain disclosure.

---

#### 3. Terms used without definition or in a nonstandard sense

| Term (quote) | Page | Problem |
|---|---|---|
| "blocks" ("which we call blocks"; "flux block"; "run-period block") | 3-4 | Nonstandard for covariance components. Also inconsistent: the text lists four blocks (systematic universes, statistical, training seed, run period), then introduces a "flux block", and the Fig. 1 caption lists five components including "normalization". |
| "unfolds" as a noun ("systematic-universe unfolds") | 3, 5 | Jargon; say "unfoldings". |
| "central-value estimator", "joint-test estimator", "exact-split estimator", "a deterministic LightGBM configuration", "a deterministic variant of the five-dimensional LightGBM central-value estimator" | 3, 5 | Four or five estimator names; I lost track of which result uses which. A small table (estimator, classifier, background treatment, used for) would fix this. |
| "capacity" ("LightGBM matched to their capacity", "refinement capacity", "higher-capacity refinement classifier") | 3 | Not quantified (trees? depth? leaves?). |
| "classifier refinement [22] ... converts the signed sample" / "background-refinement classifier" | 2-3, 7 | Explained only through a citation; one sentence of mechanism would help. |
| "inherited constant of 135 MeV" | 2 | Inherited from what? |
| "The bookkeeping of missed events ... is checked for invariance" | 3 | Invariance under what operation? |
| "approximate the weighting of events that fail reconstruction" | 3 | What approximation is being made? |
| "earlier production of that release" | 2, 11 | "Production" is used in three senses in this paper: data processing version, the main toy run ("production pseudo-experiment"), and simulation size ("production size"). |
| "independent-generator samples that have not already been inspected" | 5 | Blinding concept not introduced. |
| "predefined criteria", "useful precision", "precision targets set in advance", "target total width", "a bound fixed before production", "documented exception", "fallback definition" | 1, 2, 10 | Never stated numerically or defined. |
| "hybrid null" | 6 | Defined, but the definition ("MINERvA Tune v1's shape and G's finite-sample fluctuations below that grid") is hard to parse. Say explicitly: "G's cross section integrated in each fine cell, with Tune v1's distribution within each cell". |
| "fine five-dimensional grid", "twofold-merged grid", "δfine", "refinement of the null truth's grid" | 7-8 | The fine grid's binning is never given (number of cells, edges). |
| "the 109 supported cells" | 7 | "Supported" undefined: nonzero prediction? Minimum statistics? |
| "noise-free unfolded result" | 7-8 | How is a noise-free unfolding obtained? Asimov-like? |
| "the data's rounding-level noise" | 7 | Floating-point rounding? Why does it enter Σ? |
| "the predictions' finite-sample residual" | 7 | Unclear. |
| "lateral bands", "linear surrogate", "lateral surrogate" | 7, 8 | MINERvA-toolkit jargon (lateral vs vertical error bands) that is not explained for non-MINERvA readers, and the surrogate is not described. |
| "weight-based detector bands" | 7 | Same. |
| "interaction-model prior is the analysis's 34-band set" | 8 | "Prior" already means the unfolding prior in this paper. Here it means the nuisance prior. Confusing. |
| "shifted nulls", "claim variant", "robustness shift" | 7-9 | Internal. |
| "decisions were determined", "remain determined" | 7, 8 | Sequential-test jargon; define once. |
| "non-centralities λ of 318-6344 in these units" | 7 | Which units? Non-centrality of what distribution? |
| "random throws" | 10 | Standard in T2K, but the paper elsewhere says "universes"; pick one. |
| "projected uncertainty" ("moves the projected uncertainty by 6.145%") | 10 | Which scalar? Median relative per-cell uncertainty in the 42-cell projection? Relative change of sqrt(Tr C)? |
| "MEC-like (E_avail, W) shape"; "two of three alternatives specified in advance" | 9 | The power-study alternatives are never described. |
| "recovered pseudo-experiments" | 8-9 | Internal shorthand. |
| "post hoc observation" | 9 | Fine as a phrase, but it signals process rather than physics. |

---

#### 4. Places where hedging hides what was measured or concluded

1. **The "predefined criteria" (abstract, intro, Sec. VII, conclusions).** This is the paper's central
   negative result: no five-dimensional measurement is possible. Yet the criteria, the precision targets, and
   the size of the model-dependence component are never given as numbers. I cannot judge whether the method
   misses by 10% or by a factor of 5. The only numeric criterion is the 5% seed limit against 6.145%.

2. **Two-dimensional reproduction, Sec. IV A, p. 3.** "χ²/ndf = 2.65, a correlated shape difference
   (indicative only; see below)." With 205 bins this is a very large χ², and because both results come from the
   same data I would naively expect χ²/ndf well below 1 against the published covariance. Is the reproduction
   consistent with the published result or not? The paper says per-bin agreement is good (RMS 0.564) but never
   says plainly that a significant correlated shape difference remains, how large it is, or where it sits. The
   conclusion's "depends on the learner at the level of one unit of χ²/ndf" makes the reproduction sound like a
   success with a footnote, when the content suggests an unresolved correlated discrepancy.

3. **Statistical coverage, Sec. IV B, p. 5.** After the paragraph I could not tell whether the *quoted*
   statistical uncertainty is expected to undercover, cover, or overcover. "The quoted statistical block is a
   different ensemble from it" leaves open whether it has the corrected construction.

4. **Regularization bias, Sec. IV C, p. 5.** "up to 74% at high W" and "16% to 31% in the most affected (E_avail,
   W) cell and within the quoted total uncertainty in about half of those cells". Which cells are "those"? In
   the 74% case, what is the cell's uncertainty? This is arguably the most important physics number in the
   validation, but it is buried mid-paragraph and needs a figure or table (bias/σ per cell). It also seems to
   sit oddly with the abstract's "recover injected shape changes in closure tests".

5. **Background bias, Sec. IV C.** "reduces it to below 0.3%, leaving up to 1% in some joint cells". Below 0.3%
   for which quantity? And the central values use the purity method, which has the 4% bias that "the quoted
   uncertainties omit". So are Figs. 2-3 biased high-W by up to 4%? The paper should say so directly next to the
   figures.

6. **Five-dimensional coverage test, Sec. IV C.** "failed its criterion, fixed in advance". No numbers.

7. **Floating-point sensitivity, Sec. IV C.** "Input changes at the level of floating-point rounding move the
   unfolded values on data by up to a few statistical standard deviations". This is startling, and it is
   immediately softened ("lies inside the data-bootstrap statistical uncertainty"), which seems to contradict
   "a few statistical standard deviations". Which estimator, and which standard deviation? I could not tell
   whether the central values in Figs. 2-3 are reproducible.

8. **What is rejected, Sec. VI.** The abstract says the tests "reject all five tested predictions". Sec. VI B
   says the decisions test the hybrid null, and "The rejections carry over from the simulated hybrid null to G
   itself only if ...". Then the scan shows robustness up to 5.2δfine against an estimated residual of 1-3δfine.
   That is actually a reasonably strong statement, but it is phrased only negatively ("bounds neither the actual
   residual nor the convergence", said three times). A plain sentence is needed: "If the sub-grid residual is
   within the geometric-extrapolation estimate, the rejections apply to G itself; they survive shifts about
   twice that estimate."

9. **Power studies, Sec. VI C, p. 9.** Powers of 0.02 and 0.00 at the GENIE null are reported without
   interpretation, and the alternatives are not described. Does this mean the test is blind to a MEC-like
   distortion near GENIE? That bears directly on the claim that the test discriminates.

10. **Sec. VII.** I could not tell what "the covariance is used only under a documented exception" means in
    practice: is any figure in the paper drawn with this covariance? Fig. 3 says "uncertainties not shown; Sec.
    VII", so I think the answer is no. If so, say "we show no five-dimensional uncertainties".

11. **Toy counts.** Sec. VI A says calibration proceeded "in batches of 200 pseudo-experiments per null, to at most
    1999", Table I says "of 1400 submitted per null (1800 for NuWro)", and Sec. VI A also mentions "a bounded
    extension of the production computing budget". I could not reconcile these numbers.

12. **Run-period inconsistency, Sec. IV B.** A 7% step between period groups is significant physics (flux? detector
    aging?). It is handled with a covariance term, and "The cause is not known" is honest. But it deserves a
    plain statement of its significance: is the inconsistency at the 3σ level, or 10σ?

---

#### 5. Project-history passages a reader does not need in the body

Each of these could be cut, compressed to one clause, or moved to an appendix or supplemental material. Items
marked (*) contain a disclosure that should survive in compressed form: that something was decided after seeing
results.

- p. 2: "The files analysed are an earlier production of that release; their names and sizes are recorded for
  reproduction".
- p. 3: "which was the original two-dimensional choice, is kept as a cross-check".
- p. 3: "selected before the joint-test design was fixed".
- p. 3 (*): "This choice, which replaced the exact-split result, was made after both comparisons were known."
- p. 3: "Neither showed an effect above the noise of an earlier ten-seed training scan".
- p. 5: the whole account of "An earlier version of the statistical band ... rebuilt band ... Rescoring ... post
  hoc and partly circular ... The rebuilt band has not been independently tested either".
- p. 5: "A review of the stored analysis products found errors in an earlier version of the uncertainty budget
  ... the quoted covariance is free of both."
- p. 5: "as first measured with a deterministic variant".
- p. 8 (*): "Before any result was known, the size of the shifts was set from an assumed extrapolation ... at a
  rate taken from the review of the test design, for which no calculation is recorded".
- pp. 7-8 (*): "The reviewers of the design had seen descriptive per-cell residuals before it was fixed. A bounded
  extension of the production computing budget was decided while the outputs of the computing jobs showed the
  observed p values".
- p. 8 (*): "The scan was specified before it ran, but it was run after the decisions and is not part of the
  decision rule".
- p. 8: "Batch-job time limits interrupted or prevented 224 calibration and 53 power pseudo-experiments ... Every
  submitted pseudo-experiment has now been observed". Keep one sentence with the result.
- p. 9: "the rest having been lost to time limits".
- p. 9 (*): "This comparison was specified before it was run but after the five-dimensional outcomes were known".
- p. 10: "One of these criteria requires a bound fixed before production and can no longer be applied to it, and
  the covariance is used only under a documented exception".
- p. 10: "A separate study looked for a definition ... within the study's rules and computing budget. For its
  fallback definition ... The joint tests above came from the same study".
- p. 11: "prepared locally but not yet deposited"; "The package was assembled before the two-dimensional central
  value was changed to LightGBM, and it carries the exact-split curve."

Suggestion: gather all the (*) items into one short "Blinding and analysis sequence" paragraph, perhaps at the
start of Sec. VI. Experimental papers routinely have one, and it would keep the integrity disclosures while
clearing them out of the results text.

---

#### 6. Where the wording lowered my trust more than the content warrants, and where plainer wording could overclaim

**Wording that made me trust the result less than its content warrants:**

- **"Had every interrupted one exceeded the observed statistic, no test would have been rejected."** (p. 8)
  On first reading this sounded as if the result might be void. The actual content (all reruns land far below
  the observed statistic) is a clean, robust result. Lead with the result.
- **"A review of the stored analysis products found errors in an earlier version of the uncertainty budget"**
  (p. 5). This invites the question of what other errors remain. The content (the final procedure does X and Y)
  inspires more confidence when stated as method.
- **"for which no calculation is recorded"** (p. 8). This makes the shift size look arbitrary, when it is really
  a stated assumption with a robustness scan reaching about twice its upper value.
- **"Rescoring ... is post hoc and partly circular"** (p. 5), and **"this says nothing about whether its size is
  right ... it is not a test"** (p. 4). Both are self-indictments of checks the reader would not have taken as
  tests in the first place.
- **"used only under a documented exception to the criteria"** (p. 10). This sounds like a rule was bent. If the
  content is "we do not use it for inference", say that.
- **"bounds neither the actual residual nor the convergence"** (p. 8, twice in substance, and again in VI C). The
  repetition makes the sub-grid issue feel fatal. The numbers (robust to 5.2δfine against an estimated 1-3δfine)
  suggest it is a moderate, quantified caveat.
- **Density of "has not been independently tested / validated / established / measured."** By the end of Sec.
  IV the reader has seen something like 15 such clauses, and stops being able to tell the crucial limitations
  (regularization bias, model dependence, untested coverage, no hadronic-response band) from minor ones (the
  135 MeV constant, the flux-weight approximation in two universes).
- **References [32]-[35], [37] as repository records with internal titles**, and the "[HOLD: ...]" placeholders.
  These make the paper look like a draft of an internal report rather than a submission, and a referee will
  doubt that the key test specification can be audited.
- **"agrees with the production evaluation in all 1379 compared quantities"** (p. 8). Fine content, but it reads as
  software QA. The content is reassuring; the register makes it feel like compliance.

**Where a plainer version would risk overclaiming (keep these qualifications):**

- **Title, "validation and calibrated model tests".** The body says the 2D result "is not fully validated" and 5D
  coverage "has not been established". A plainer body paired with this title would overclaim. Consider
  "validation studies" or "tests of".
- **"reject all five tested predictions"** must keep both conditions in the same sentence: no recoil-response
  uncertainty, and the hybrid null / sub-grid shapes. Sec. VI D's own evidence (GENIE CV is not rejected in the
  (pT, p∥) projection, p = 0.48, so the rejection comes from the hadronic axes) shows that the hadronic-response
  condition is load-bearing. Plain "the data reject GENIE/NuWro/GiBUU" would overclaim.
- **The ±4% recoil-scale study** (p. 9) must keep "The null distributions were not regenerated with the
  variation". A plain "the rejections are robust to the hadronic energy scale" would overclaim.
- **"no evidence of additional discrimination from the joint five-observable information"** should not be
  simplified to "the five-dimensional information adds nothing". The 5D p values sit at the Monte Carlo floor
  (k = 0), so the comparison cannot show that either.
- **The 2D reproduction "agrees ... to about one percent"** (intro) needs χ²/ndf = 2.65 next to it. On its own it
  overstates the agreement.
- **"recover injected shape changes in closure tests"** (abstract, conclusions) needs the 74% / 16-31%
  regularization-bias result next to it. Otherwise it overclaims shape recovery. The abstract currently says
  "recover injected shape changes" and then, separately, "show limitations of ... the regularization"; a reader
  of the abstract alone would not learn that the bias can be as large as the effect.
- **Descriptive (E_avail, W) excess, Sec. V.** "No significance is assigned" and "a statement relative to the
  MINERvA Tune v1" must stay. This region is also where the regularization and background biases are largest,
  and a plainer version should say so in the same paragraph (it currently does, briefly; keep it).

---

## R10. After-pass reader, primer (PDF at 386ece45) — `reader-after-primer.md` (sha256 `6b0b9e1caecb18ae…`)

### Reader test: "Measuring a neutrino cross section by teaching a computer to re-weight a simulation" (main_primer.pdf, 14 pp.)

Reader persona: a physicist from outside neutrino physics (condensed-matter or astro grad student, or a
physics-literate journalist) who has never seen this project. I read only the PDF. Quotes are transcribed
from the rendered pages. Where I could not read small figure text with confidence, I say so.

---

#### 1. Overall verdict

**Partly. The first two and a half pages work well. Most of pages 8 to 11 read like an internal review
record. That part is honest, but I could not tell from it what was found.**

What works, and works well:

- **Section 1 and the start of Section 2 (pp. 1-2) are good science writing.** The deblurring-a-photograph
  analogy, "done carelessly it amplifies noise into artifacts", and the description of the per-event
  weight ("there should be a little more (or less) of this kind of event to make the simulation look like
  the data") gave me a correct mental model in two paragraphs. "the morphed *true* simulation is the
  unfolded answer" is a sentence I would steal.
- **The trust check (p. 4, first paragraph) is concrete and convincing:** "ratio 1.011", "95.6 % of the
  individual measurement cells agree within ten percent", "6.45 % versus 6.85 % typical". This is where I
  started to believe the method.
- **The coverage explanation on p. 5 is good.** "two-standard-deviation bars contain the truth 91 % of the
  time instead of 95 %" is the kind of sentence that makes me trust the authors.
- **The random-seed argument on p. 8 is good physics, plainly told.** The uncertainty shift "is the same
  size whether we use a quarter, a half, or all of our variations, while genuine statistical noise ...
  falls by a factor of nearly three over the same step." I could follow it, and it made me trust the
  authors.
- **The GiBUU explanation on p. 7 is good.** "mostly because its simulated sample leaves out neutrinos
  above 20 GeV ... With them supplied, GiBUU too falls short in the corner by about as much as overall."
  It explains a surprising number instead of just qualifying it.
- **The extended-signal paragraph (p. 12) is clear:** "only about 6 % of the rate is a newly
  detector-supported extension; about 28 % lies in low- or zero-efficiency cells". It gives numbers, not
  adjectives.

Where it loses me:

1. **p. 3, the paragraph beginning "One more distinction matters later".** In about ten lines it brings in
   MINOS, "scalar classifiers", gradient-boosted trees, the "tree learner", PET, "recoil-only PET",
   "Full-event PET", removing cuts on the true muon, and "The companion analysis note's
   selection-versus-features table". I had no reason yet to care about any of them. I skimmed the rest of
   the paragraph.
2. **p. 3 to 4, the "What we found" bullets.** I expected the headline results here. I got a list of what
   each result is *not*. The second bullet ("in use under a documented exception to the analysis's own
   qualification rules") is opaque.
3. **Pages 8 to 11.** From "What we cannot yet claim" through the PET section, almost every paragraph
   answers an objection I had not raised: "does not by itself show", "does not carry over", "does not
   reverse", "does not give a guaranteed error bound", "it does not become a clear non-rejection", "is
   not a validated repair". By p. 10 I could not say which limits matter most. **The most important
   limit is buried on p. 9:** when the simulated truth is changed, the five-quantity unfolding comes back
   about 10 % off, more in the highest-W cells, and this is not in the uncertainty.
4. **The ratio of space is inverted.** The findings take about two pages. The limits on those findings
   take about five, and they are not ranked. A primer reader needs the top three caveats stated once and
   prominently. The rest can be pointed to.

Net: I came away knowing that the method reproduces a published measurement, that a known low-energy
excess shows up again, that there is a new excess in one corner, that all five simulations fail a joint
test, that PET is not ready, and that the signal definition can be partly extended. I learned that from
the bullets, Sec. 4 and the figure captions, mostly not from pp. 8-11. The candour made me trust the
*authors* more and the *results* less than I think they deserve (see Sec. 6).

A small layout point: page 6 is half empty, which looks like a broken document.

---

#### 2. Jargon or internal register: quote, problem, plainer version

Each rewrite keeps every limitation the original states.

**p. 3, "What we found", bullet 2**
> "An uncertainty for them is in use under a documented exception to the analysis's own qualification
> rules; that does not show that their error bars are right."

- *Problem:* "in use", "documented exception" and "qualification rules" are project-governance words. I
  do not know where the uncertainty is "in use", since the plots show central values only. I also do not
  know what the rules are or why an exception was needed.
- *Plainer:* "We have computed an uncertainty for these results, but it did not pass all of the tests we
  set ourselves in advance, so we do not yet rely on it. That is why the plots show central values only,
  with no error bars and no significance."

**p. 3, bullet 1**
> "Its size depends on which of two implementations of the tree learner is used, and we chose which one
> to quote after both comparisons were known."

- *Problem:* the disclosure is right, but it arrives before I know what an "implementation" is or how big
  the effect is. Without that, it sounds like a confession.
- *Plainer:* "Two software versions of the same learner differ by about 1 % per cell. Which one we use
  changes how large the remaining shape difference looks. We picked the version to quote after seeing
  both comparisons, so the shape agreement should be read with that in mind."

**p. 4, closing line of the bullet list**
> "Passing one of these checks does not make up for a check that another result lacks."

- *Problem:* it is a rule for reviewers, not information for readers.
- *Plainer:* cut it, or write: "Each result is only as validated as its own checks."

**p. 3, "One more distinction matters later" paragraph (whole paragraph)**
> "The original, recoil-only PET classifier does not use the muon, even though the muon is needed to
> select the event. Full-event PET adds muon features. Removing the cuts on the true muon's motion
> enlarges the population being estimated without adding selected observations. The companion analysis
> note's selection-versus-features table gives each analysis's choices; the PET design studies use
> simulated samples that contain signal events only."

- *Problem:* these are internal configuration names and a pointer to a document I don't have. The point,
  that what you select on and what you show the learner are different choices, is good but gets lost.
- *Plainer:* keep the first two sentences (selection versus inputs; every data analysis requires a muon
  that also reaches MINOS). Move the PET details to the PET section, and the "removing the cuts" sentence
  to the wider-signal section, where they are used. Drop the companion-note pointer, or make it a
  footnote.

**p. 4, error-budget paragraph**
> "An assessment of the saved analysis outputs found errors in how an earlier version of the two-variable
> error budget was put together [1]. The quoted budget was rebuilt without them. Its set of systematic
> variations and the reference those variations are compared with now use the same truth inputs. A
> pion-model variation that appeared twice is counted once. The statistical fluctuations of the
> background simulation are propagated. And the detector variations that change which events are
> selected come from complete re-runs of the analysis."

- *Problem:* this is a changelog. It tells me which bugs were fixed, not what the budget is.
- *Plainer:* "The error budget includes the main systematic variations, the statistical uncertainty of the
  background simulation, and detector effects that change which events are selected (each evaluated by
  re-running the full analysis). An earlier version contained construction errors, which have been
  corrected [1]. It still omits three effects: an approximation in how events that fail reconstruction are
  weighted, the difference between the two software versions of the tree learner, and the dependence on
  the unfolding's starting model."

**p. 5, coverage paragraph**
> "That test was of the statistical error bars in use when it ran. The main cause of the shortfall was
> found and removed, and the statistical bars now quoted were built again, at the same learner settings
> as the central value. They have not been tested. The published numbers are unchanged by this check."

- *Problem:* "in use when it ran" is project history. "The published numbers are unchanged by this check"
  is ambiguous: does it mean MINERvA's published result, or this analysis's quoted numbers?
- *Plainer:* "We found and fixed the main cause of the shortfall, then rebuilt the statistical error bars.
  The rebuilt bars have not yet been re-tested, so we make no coverage claim for them. The central values
  did not change."

**p. 8, "What we cannot yet claim", first paragraph**
> "We have built an uncertainty for the five-quantity result, which is in use under a documented
> exception to the analysis's own qualification rules, and we have built its two-quantity (E_avail, W)
> version."

- *Problem:* the same governance register as above, and "in use" contradicts "central values only" in
  the same paragraph.
- *Plainer:* same fix as bullet 2 above. The uncertainty exists, did not pass the pre-set tests, and is
  therefore not shown.

**p. 9, follow-up study**
> "A later paired study found that the bootstrap of the candidate with the larger classifier (its own
> resampling estimate of its statistical error) already carries this rounding variability. That finding
> does not carry over to the uncertainty quoted for the five-quantity central value, and it does not
> reverse the failed stability test."

- *Problem:* "candidate", "paired study" and "larger classifier" are internal names. The paragraph also
  stacks three negations.
- *Plainer:* "A version of the method with a larger background classifier removes the background bias. Its
  own statistical error estimate is already large enough to absorb the rounding effect. That fix has not
  been applied to the quoted five-quantity result, and the rounding test it failed still counts as
  failed."

**p. 9**
> "Longer runs sometimes improve recovery and sometimes leave a persistent residual, but how much they vary
> from one repeat to the next was not measured at the same settings, so we have not established a
> tradeoff between bias and variability. Combining cells changes what is measured, and changing the
> starting model does not give a guaranteed error bound."

- *Problem:* each clause rebuts a remedy that nobody in the text has proposed.
- *Plainer:* "Obvious remedies (more iterations, coarser cells, a different starting simulation) either
  change what is measured or do not reliably remove the bias, so none has been adopted yet."

**p. 10, hypothesis definition**
> "Strictly, each hypothesis gives the true cross section that generator's rate in each cell of a finite
> grid of true values, and Tune v1's shape inside each cell."

- *Problem:* I could not parse this sentence. A verb or preposition seems to be missing.
- *Plainer:* "Strictly, each hypothesis says: in every cell of a fixed grid, the true cross section equals
  that simulation's rate, and within each cell its shape follows MINERvA's tuned simulation."

**p. 10, κ paragraph**
> "In the tests as fixed in advance, the first decision stops being a clear-cut (determinate) rejection
> near κ = 5.26, or 5.17 when the recovered pseudo-experiments are included. At that point the decision
> becomes ambiguous; it does not become a clear non-rejection. The scan moves in one direction only, and
> it does not bound the unmeasured error from structure below the grid."

- *Problem:* "the first decision" (which one?), "determinate", and three negations in a row.
- *Plainer:* "We do not know how much structure finer than the grid could matter. As a stress test, we
  inflated the last measured effect of refining the grid. The rejections survive until that effect is about
  five times larger than measured (κ ≈ 5.2). Beyond that, the first of the ten tests to go becomes
  undecided, not reversed. This is a robustness margin, not a bound on the real error."

**p. 10, final sentence of the post-hoc paragraph**
> "A simulation that is not rejected is not thereby accepted as true."

- *Problem:* a physicist reader knows this, and here it reads as defensive.
- *Plainer:* cut it.

**p. 11, PET design study**
> "Better recovery did not give a qualified design: the study ended with no eligible design. One finalist
> failed a robustness threshold under the rule, fixed in advance, that judges the point estimate. The
> statistical comparison did not establish which finalist was more robust, and this finalist's coverage was
> never measured."

- *Problem:* this is the register of a decision record ("qualified", "eligible", "finalist", "rule fixed in
  advance").
- *Plainer:* "Neither of the two best designs met every test we set in advance. One was not robust enough
  in its central values, so its error bars were never tested. The other had good central values but
  unreliable error bars (numbers below). So no PET design is used for any result."

**p. 11**
> "A diagnostic width adjustment still leaves poor coverage, especially at low acceptance, so dividing the
> width by the square root of six is not a validated repair."

- *Problem:* it rejects a fix the reader never heard proposed.
- *Plainer:* "Simply shrinking the intervals by √6 to correct for the averaging does not fix the problem:
  coverage stays poor, especially where the detector sees few events."

**p. 11, comparison paragraph**
> "An exploratory comparison then ran PET and OmniFold with the tree learner on exactly the same simulated
> events [6]."

- *Problem:* this sentence implies PET is not OmniFold. Earlier I understood OmniFold to be the method,
  and the tree learner and PET to be two learners inside it.
- *Plainer:* "...ran OmniFold with each of the two learners, PET and the tree learner, on exactly the same
  simulated events."

**Figure 5 (p. 12): legend and footer text**
> "PET H2S1T24 (k=5) − GBDT (k=7)", "PET L128S1T24 (k=4) − GBDT (k=7)", "Paired differences per FB draw",
> "Simulation only; final-bank (FB) look-1 draws, inference conditional on the banks; exploratory,
> unadjusted 95% t intervals."

- *Problem:* these are internal configuration codes and process vocabulary ("final-bank", "look-1",
  "banks").
- *Plainer:* label the series "PET finalist A" and "PET finalist B", and drop the footer or reduce it to
  "Simulation only; exploratory 95 % intervals."

**Figure 6 (p. 13) panel titles**
> "(a) anchor ratio", "(b) prior-swap ratio"; caption: "The extended-fiducial scalar study"

- *Problem:* "anchor", "prior-swap", "fiducial" and "scalar" are internal names.
- *Plainer:* "(a) New vs. published result", "(b) Effect of changing the starting simulation". The caption
  could read "The wider-signal study".

**References [1], [3]-[7] (pp. 13-14)**
> e.g. "PET final-design selection: terminal decision record", ".../docs/orchestration/state/
> next-preparation-20261009/two-d-followup/REPORT.md"

- *Problem:* citations to repository process files ("orchestration/state", "DECISION_RECORD", "terminal
  decision record") signal a lab notebook, not a primer.
- *Plainer:* cite one public analysis note, or a single "supporting material" link.

---

#### 3. Terms used without explanation (or explained only after first use)

**Used before they are defined**

- "available energy" (p. 3, bullet 3): defined only on p. 6.
- "high hadronic mass" (p. 4, top): defined only on p. 6.
- "seeds", "rounding" (p. 3, Table 1: "iterations, seeds or rounding"): what is rounded, and why rounding
  matters, is still unclear on p. 9 ("when the inputs are rounded differently").
- "MEC" / "GENIE+MEC" (Fig. 3 legend, p. 7): defined only on p. 10.
- "GBDT" (Fig. 5): defined only in the Fig. 5 caption, although the text says "tree learner" throughout.

**Never explained**

- "central value": used throughout and never defined. A non-specialist may not realise it means "the best
  estimate without error bars".
- "PET": the acronym is never expanded, and "point-cloud transformer" (p. 3) does not match the letters.
- "momentum transfer (q₃)" (p. 6): the term is named, but its physical meaning is not given.
- "neutrino–electron scattering and inverse muon decay" (p. 4): I cannot tell why these constrain the
  "flux", or what the flux uncertainty is.
- "recoil", "low-recoil", "hadronic recoil energy", "calorimeter" (pp. 6, 10).
- "pion-rescattering", "proton and pion rescattering" (p. 6), and "deep-inelastic" (p. 7, glossed only as
  "shatters the nucleon").
- "at truth level" (p. 6) and "truth-level cuts" (p. 12).
- "independently measurable direction" (p. 6).
- "auxiliary classifier" (p. 9).
- "clipping of some negative event weights" (p. 10): I don't know why event weights can be negative.
- "a calibration shift, with a stated bound, that arises because the pseudo-experiments use half the
  simulation" (p. 10).
- "test statistic" (p. 10).
- "underfits at the detector-level step" (p. 12), and "Applying the exact weights that define each
  distortion" (p. 12).
- "tracker interaction volume" (p. 12) and "low- or zero-efficiency cells" (p. 12).
- "fiducial", "prior-dominated" (Fig. 6). The text says "simulation-dependent" for what is presumably the
  same thing.
- "POT", "ME FHC" (figure headers, Figs. 2, 3, 6).
- "MnvTune v1" (Fig. 2 legend) versus "Tune v1" in the text.
- "E0 ... E5", "k=4/5/7" (Fig. 5). The caption decodes E0-E5 but not k.
- "error budget" (p. 3 onward): understandable, but not explained.
- "two implementations of the tree learner", "the faster one" (p. 4): the reader is not told these are
  two software packages for the same algorithm.

**Possible inconsistencies a careful reader trips on**

- Fig. 2's legend appears to read "GENIE 2.12.6", while the Fig. 3 caption says "version 2.12.10". This is
  small text and I may be misreading it.
- p. 3 says "all four tested simulations", while p. 10 tests "five widely used simulations". The fifth
  (Tune v1) is explained only in the Fig. 4 caption.
- "6.145 %" (p. 8, the shift in the *uncertainty*) and "6.02 %" (pp. 7-9, the shift in the *central
  values* as a fraction of their uncertainty) are near-identical numbers with different meanings, quoted
  to four significant figures. I confused them on first read.

---

#### 4. Places where hedging hides what was found

**1. The five-quantity bias is the most consequential finding, and it is buried.**

- p. 3 says only: "The higher-dimensional central values pass particular recovery checks."
- The fact that matters is on p. 9: when the simulated truth is changed, "typical cells come back about
  10 % off, and the highest-W cells much more. Neither effect is in the quoted uncertainty yet." The
  follow-up adds "16 % to 31 % in the worst cell".
- This deserves a plain sentence in the bullet list: "When we change the simulated truth, the
  five-quantity unfolding recovers it only partly: about 10 % off in typical cells and more at high W.
  This bias is not yet in any uncertainty."
- At present "pass particular recovery checks" reads as a positive statement about results that also
  *fail* an important one.

**2. The rounding-stability failure.**

- p. 9: "the result on the real data shifts by up to a few times its statistical uncertainty when the
  inputs are rounded differently, which fails a stability test fixed in advance."
- This is a big statement: the real-data answer moves by several sigma under a numerical detail. It sits
  mid-paragraph, between bias numbers and a sentence about the bootstrap. It does not appear in the
  bullets or in the takeaway.

**3. How big is the "new puzzle"?**

- p. 7 is headed "A new puzzle for the tuned simulation" and says the leftover discrepancy "sits in a
  specific corner". It quantifies the *other* simulations (14-16 % in the corner versus 7-15 % overall).
- It never gives the excess over Tune v1 in the corner. I had to read it off Fig. 4's colour bar (a
  ratio somewhere above 1.4?).
- One number would let me judge it: "the data exceed Tune v1 by about X % in that corner, against Y %
  overall".

**4. What the 9.2 % and 6.3 % on p. 6 are.**

- "our central values lie 9.2 % and 6.3 % above it on the finest grid whose cell edges both measurements
  share."
- Two numbers, but I am not told what each refers to: two cells, two projections, or two versions.

**5. The joint test is the strongest statistical result, but it is not presented as one.**

- p. 10 reports a genuine rejection: all ten hypotheses rejected at a combined 5 % level, with at most one
  of about 1,340-1,750 pseudo-experiments as extreme as the data.
- It is surrounded by six conditions, a recovered-pseudo-experiment aside, a post-hoc projection
  comparison and the κ scan. As a result it reads as weaker than the *unvalidated* corner excess on p. 7.
- It also does not appear in the takeaway (Sec. 4).

**6. Is the 2D uncertainty validated or not?**

- p. 4 says "its error bars are close in size to the published ones". p. 5 says "We make no coverage
  claim". p. 9 says the 2D check "retains its independently constructed uncertainty".
- I finished unsure whether to treat the 2D error bars as usable. One explicit sentence would settle it.
  If they are usable but without a coverage guarantee, it would be: "the 2D error bars are comparable in
  size to MINERvA's and complete except for three listed effects; their coverage has not been
  independently verified."

**7. Fig. 5 and the text disagree on what is shown.**

- The text says "the tree learner does better on all three tests that reweight to other generator models
  and on the narrow energy bump".
- Fig. 5 shows only tests where PET is ahead or tied. The tests where the tree learner wins are not in the
  figure, so the figure alone overstates PET.
- The fix is to show all tests, or to say in the caption that the generator-model tests are not plotted.

---

#### 5. Project-history passages the reader does not need

The scientific content of most of these should stay, restated in the present tense as what *is*. Only
the history should go.

- p. 4: "we had originally quoted the slower one."
  - Keep the post-hoc disclosure. Drop "originally".
- p. 4: "An assessment of the saved analysis outputs found errors in how an earlier version of the
  two-variable error budget was put together [1]. The quoted budget was rebuilt without them." plus the
  list of four fixes.
  - Replace with a description of what the budget contains and omits (see Sec. 2).
- p. 5: "That test was of the statistical error bars in use when it ran. The main cause of the shortfall
  was found and removed, and the statistical bars now quoted were built again".
  - Say only "the bars have since been corrected and not yet re-tested".
- Fig. 3 caption: "the GENIE and NuWro predictions were rebuilt with a correctly sampled beam spectrum."
  - Unless the reader can see an older version, this is history. Cut it.
- p. 9: "(One of the two predictions behind that pattern was made with a wrongly sampled beam spectrum, so
  the pattern is a test of a chosen size, not a measured difference between generators.)"
  - The conclusion matters: it is a synthetic test pattern. The cause does not. Write: "The test pattern
    is a deliberately chosen distortion, not a real difference between generators."
- p. 9: "A later paired study found ..." and "We made no change to the method or the quoted uncertainty as
  a result of these studies."
  - The second sentence is useful but reads as defensive. Better: "These problems are not yet corrected in
    the quoted result."
- p. 10: "Some pseudo-experiments were lost to computing time limits. Rerunning exactly those seeds
  recovered them, in a check reported separately from the result: none looked as discrepant as the data,
  though in one robustness variant one came close."
  - This is a footnote at most.
- p. 11: "But in the first of these studies, none of the candidate designs, each fixed in advance at ten
  iterations, qualified to go on to a coverage test. A later study to choose a final design raised ..."
  - A two-stage design-campaign narrative. The reader needs only the end state: PET recovers distortions
    much better than the original (about 90 % versus 31 %), and neither best design has reliable error
    bars.
- p. 11: "Saved outputs of these studies give a partial explanation [5]."
  - "Saved outputs" is process vocabulary. Write "Our diagnosis suggests ..."
- p. 11: "A later full-event version that adds the muon is also method development only".
- References [1], [3]-[7]: titles such as "terminal decision record", "confirmatory results",
  "next-preparation-20261009".

---

#### 6. Where wording lowered my trust more than the content warrants, and where plainer wording would overclaim

##### Wording that lowered my trust unnecessarily

1. **The negation density on pp. 8-11.** When almost every sentence is "does not establish", "was not
   measured", "is not bounded" or "is not a validated repair", I start to assume the analysis is in
   trouble. The *content* is actually a careful, pre-registered validation programme: thresholds fixed in
   advance ("the 5 % we had decided in advance we would tolerate"), pseudo-experiment-calibrated tests, and
   a noise-scaling argument for the seed effect. Said positively, this would raise my trust. For example:
   "We set pass/fail thresholds before looking. The 2D result passes. The multi-quantity uncertainty does
   not yet, so we don't show it."
2. **The governance vocabulary** ("documented exception", "qualification rules", "eligible design",
   "terminal decision record") makes the work sound bureaucratically contested rather than scientifically
   careful.
3. **The changelog of fixed errors** (p. 4) makes me wonder what else is wrong. A statement of what the
   budget contains would not.
4. **The joint test's logic is not explained, so the strongest result looks the most fragile.** A naive
   reader asks: "you say the multi-quantity error bars are not reliable and the unfolding is biased by
   about 10 %. How can you reject five simulations at 5 %?" My guess is that the answer is in the method:
   the test's null distribution comes from pseudo-experiments that are *unfolded the same way* under each
   hypothesis. If so, the test is calibrated by construction and does not rely on the quoted error bars.
   One sentence saying so would make this the most trustworthy result in the primer. As it stands, the six
   conditions and the κ scan make it look like the least trustworthy.
5. **False precision undermines the hedges.** "6.145 %", "6.02 %", "κ = 5.26, or 5.17" come with four
   significant figures, next to "we compared only one pair of random seeds". Rounding them ("about 6 %",
   "κ ≈ 5") would match the message.
6. **References to internal process files** make the primer feel unreviewed.

##### Places where a plainer version would risk overclaiming

1. **The joint test (p. 10).** "All five simulations are ruled out" is plainer but drops two things:
   "under stated modelling assumptions", and the fact that the error from structure finer than the grid is
   *not bounded*. Any rewrite must keep "the test cannot see structure finer than its grid, and we have not
   bounded that error". It must also keep the result's status as a test of simulations rather than a
   measurement with error bars.
2. **The corner excess (p. 7).** The closing sentence already leans promotional: "This is the kind of
   localized discrepancy that points theorists toward what their models are missing — and it was only
   visible because we measured available energy and W jointly."
   - The excess has no significance, and its central values are shifted by the seed. On p. 9 the same
     five-quantity unfolding comes back about 10 %, and more at high W, off under a changed truth. That is
     the same size and location as the excess.
   - A plain reader will take "puzzle for theorists" as a discovery. The primer should connect the two
     facts explicitly: "the excess is comparable in size to the unfolding's known bias at high W, so it is
     a lead, not a result".
   - I would soften "only visible because" to "becomes visible when".
3. **2p2h (p. 6).** "Adding a process ... fills part of the gap" is correctly hedged. A plainer "2p2h
   explains the excess" would overclaim. Keep "part of" and "without uniquely establishing the cause".
4. **The reproduction (p. 4).** "Our method reproduces the published result" in a headline would be fair
   only if the post-hoc choice of tree-learner implementation and the remaining shape difference stay
   visible next to it. The current text does that well. Keep it, just state it once.
5. **The wider signal (p. 12).** "We measured the cross section over a wider region: 4.502 × 10⁻³⁸
   cm²/nucleon" would overclaim. The text rightly says "preliminary", that only about 6 % is
   detector-supported, and that about 28 % is simulation-dependent. It should also say plainly whether
   σ_ext has any uncertainty at all. As written I cannot tell.
6. **"a first at MINERvA" (p. 6).** This is fine as stated (simultaneous, unbinned). A plainer "the first
   five-dimensional measurement" would overclaim, given the authors' own warning that these are "five
   recorded coordinates, not five demonstrated independent pieces of information".
7. **The takeaway (p. 13)** says the multi-quantity "error bars have not been shown to be reliable". It
   does not say the multi-quantity *central values* carry an untreated bias of about 10 % under a changed
   truth. A reader who reads only the takeaway would overestimate the central values. Add one clause.

---

## R11. Fix round, paper — `fix-paper.md` (sha256 `afd88ea7aa6d08cf…`)

### Plain-language pass: paper fix round (fix-round writer's record)

Worktree `wt-plain` (branch at `386ece45`, base of the pass `28d28626`). Files edited:
- `docs/analysis-note/main_paper.tex`: abstract and Data availability only;
- `docs/analysis-note/paper_body.tex`.

No other file was touched, and no git write was made. Line numbers are in the working tree after this round. Each
changed site carries `% plain-language pass, review fix <id> (DECISION-20261018-joseph-plain-language-pass)`. Ids
`reader-*` mark the reader-derived changes in §2. All 204 base comment lines survive verbatim.

Every finding was checked against `git show 28d28626:` of both files and against the sources the finding cites.

#### 1. Review findings (review-paper.md: MATERIAL 3, MINOR 10, NOTE 7)

| id | sev | disposition | new text (line) | verification / reason |
|---|---|---|---|---|
| R1 | MATERIAL | **fixed** (director ruling R1) | Intro `paper_body` 62–64: "agree in normalization with the lower-dimensional results they extend and recover the known low-recoil discrepancy"; IV C 523–525: "agreement in the marginal normalizations coexists with substantial regularization bias"; Concl. 971–973: "agree in normalization with the lower-dimensional results they extend and recover the established low-recoil discrepancy" | Confirmed: `sec_3d.tex` §3d-anchor says "The *normalization* agrees closely", then "The *shape* agrees less closely" (χ²/ndf = 4.98). The base had "pass their marginal anchors" / "marginal-normalization checks". The abstract (`main_paper` 57–58, "pass checks of their marginal normalizations against the lower-dimensional results") was already normalization-only and is unchanged. |
| R2 | MATERIAL | **fixed** (director ruling R2) | `paper_body` 440–443: "In particular, the coverage of its intervals has not been validated on independent simulated samples, nor simultaneously over all reported bins and projections.  The covariance also provides no calibrated significance for generator comparisons." | Confirmed: the round-1 "average coverage of its per-bin intervals" was the wrong gloss for "population". **The note fixer changed the note's gloss during this round** (`sec_systematics.tex` §"Status of the 2D result", their fix m1). It now reads "on independent simulated samples, nor simultaneously over all reported bins and projections", citing PLAN-20261011 §1 (205 cells, their integral and 30 projections). The paper copies that wording word for word, so the two deliverables agree. If the note's sentence changes again, the paper must follow it. |
| W1 | (director instruction) | **fixed** | `paper_body` 437–438: "The result's intervals, bias and covariance have not been independently validated." | The round-1 text was generic ("The result is not fully validated"). The new sentence names what DECISION-20261014 §2 (l.49–50) says is missing: "independent validation that supports the interval, bias and covariance claims". The wording is the note's own (its fix m1), so the two agree. |
| R3 | MATERIAL | **fixed** | Sec. II `paper_body` 155–157: "The GENIE and NuWro predictions use a corrected flux sampling: they are reweighted exactly, event by event, to the analysis flux, with added 50–100 GeV samples"; Sec. V 545–546: "(same-sample ratios computed with GENIE before its flux sampling was corrected)" | Confirmed: `sec_3d.tex` 235–247 (¶"Flux repair") describes the defect and says "The FSI-dial studies … retain unrepaired samples". The base had "corrected flux sampling" and "before its flux correction". |
| R4 | MINOR | **fixed** | abstract `main_paper` 59: "pass closure checks with injected shape changes"; Intro `paper_body` 64–65 and Concl. 973–974: "pass closure tests with injected shape changes" | Confirmed: the base's "pass injected-shape … checks/tests" is relative to a criterion. The abstract keeps the base's "checks", and the body keeps "tests". |
| R5 | MINOR | **fixed** | abstract `main_paper` 72–74: "they do not show that the tested joint five-observable information discriminates beyond matched coarse projections of the same cells" | Confirmed: the base had "the tested joint information". |
| R6 | MINOR | **fixed** | abstract `main_paper` 70, 72: "These rejections hold only under stated conditions. The tests recover known discrepancies, but …"; Intro `paper_body` 79–80: "reject at the 5% familywise level under six stated conditions (Sec. VI B). Two of them, …" | Confirmed: the Intro's rejection sentence had lost its conditions. The base had "reject … under six stated conditions". |
| R7 | MINOR | **fixed** | `paper_body` 402–403: "in \covTwoDNtoy{} closure pseudo-experiments, specified in advance, against a fixed truth:" | Confirmed: the participle was ambiguous. The gate phrase "against … 95.4 … nominal" is intact (SEC4-RECEIPTS 15/15). |
| R8 | MINOR | **fixed** | `paper_body` 232–234: "is checked for completeness, an identity that must hold, and the dependence on the number of iterations is a stability diagnostic" | Confirmed: the note's `tab:validation-questions` row "Miss completeness" says "Membership and completeness invariants". The reader also asked "invariance under what?" (§3). |
| R9 | MINOR | **fixed** | `paper_body` 371–373: "it contains them by construction; this says nothing about its coverage, that is, whether its size is right" | Confirmed: "covers them automatically" read as a coverage claim, and the D5 key term "coverage" had gone. The fix keeps the brief's R1 model shape and restores "coverage". |
| R10 | MINOR | **fixed** | `paper_body` 365–367: "… so it relies on the periods' own simulated responses.  It does not identify a correct period." | Confirmed: the "so" made the limit follow from the double ratios. The base had a separate clause after ";". |
| R11 | MINOR | **fixed** | Fig. 4 caption `paper_body` 791–793: "for the shifted null with the largest null median among those used in the decisions (labelled ``claim variant'' in the legend)" | Confirmed against VI A ("the largest p value over a set of shifted nulls"). This also defines "claim variant" for the reader (§2). |
| R12 | MINOR | **fixed** | `paper_body` 934–936: "The square root of their contribution to the trace is \pinnedBandsSqrtTr% of √Tr C, the square root of the covariance's trace." | Confirmed: `values.tex` 453–454 gives 26.0% of √Tr C_Z and 6.75% of the trace, and √0.0675 = 0.2598. DECISION-20260920 M3 says "26.0% of √Tr C_Z, 6.75% of the trace". "Make up" implied an additive share. |
| R13 | MINOR | **fixed** | `main_paper` 129–131: "A candidate release package of about 16 MB [39], prepared locally but not yet deposited, needs only numpy, scipy, and matplotlib." | Confirmed: the base had "release candidate". |
| N1 | NOTE | **fixed** (register; the cite was moved within the paragraph, not added) | `paper_body` 433–435: "under the conventions stated in the analysis note [14]"; 454–455: "The analysis note also states the further approximations and limits." | The pointer sentence (W3's "one pointer sentence for D6–D12") is kept. The cite-key count is unchanged (64). |
| N2 | NOTE | **partly fixed** (register); F9 stays for Joseph | `paper_body` 916–919: "One of these criteria requires a bound fixed before the covariance was produced and can no longer be applied to it.  We use the covariance only under an exception to the criteria, recorded in the analysis note and limited to this one covariance." | "Documented exception" is replaced (reader item). "Recorded in the analysis note" is true: `sec_5d.tex` §eavailw-adopted says "Its digest-bound exception covers only these bytes". "Production" (three senses, reader §3) is replaced here by "before the covariance was produced", the note's own phrase ("could not be fixed before production"). **Not done:** saying what the covariance is used for. That is new content (F9). |
| N3 | NOTE | **fixed** (register) | VII `paper_body` 947–950: "The joint tests above came from the same study, as a different route to inference: they test the generator predictions as hypotheses and provide no new measurement uncertainty."; Concl. 968–969: "they are conditional on six stated conditions and provide no new measurement uncertainty" | The reviewer's "test generator predictions directly" was not used: "directly" could read as a stronger claim. "As hypotheses" is what Sec. VI says. |
| N4 | NOTE | **not applied** | — | Defining "predefined criteria" needs their numbers (F4, for Joseph). Any wording without numbers would still be undefined. |
| N5 | NOTE | **not applied** | — | The reviewer refers it to Joseph (F6). A register-only rewrite ("the review of the test design") would still not give the rate, and giving the rate adds a number. |
| N6 | NOTE | **fixed** (register) | `main_paper` 140–141: "reproduces every value recorded in the package and every figure number that it checks" | — |
| N7 | NOTE | **addressed in the caption**; the legend stays for P10 | see R11 | The figure legend is out of scope. |
| F3 ruling | — | verified by the reviewer; unchanged | `paper_body` 295–298 | "unfolds" became "unfoldings" in the same sentence (§2, reader-U). The ruling's comment line is untouched. |

#### 2. Reader-derived changes (reader-after-paper.md; register only)

| id | reader item | change (line) |
|---|---|---|
| reader-B | §3 "blocks": the text lists four, then a "flux block", then the Fig. 1 caption lists five, including "normalization" | Checked against `stageF/rebuild/REPORT.md` l.273: the universe row includes "the 1.4% rank-1 normalization", and the Flux band is one of the universe bands (MAT `CalcCovMx` with the ν-e+IMD weights). So the four blocks are correct. The caption and the "flux block" sentence were the inconsistent ones. Caption `paper_body` 273–275: "statistical, systematic-universe (including the normalization), training-seed and run-period blocks of the covariance". Text 315–317: "In the systematic-universe block, the flux universes carry the MINERvA analysis toolkit's per-universe … constraint weights." No number was added (the 1.4% is left out of the caption on purpose, by C1). |
| reader-E | §3: four or five estimator names | The two estimators are named once, where they are defined. 197–198: "…with the purity-based subtraction, which we call the central-value estimator"; 208–209: "a deterministic LightGBM configuration, the joint-test estimator, selected before…". The forward use at 188–189 became "the refinement capacity of the joint-test estimator (below)". The later uses now point to defined names: Sec. V "(LightGBM central-value estimator)", and IV C/VI "joint-test estimator". "A deterministic variant of the … central-value estimator" (IV C) is kept as is, because EDITORIAL-20261011 restored that qualifier and it is a distinct object. |
| reader-U | §3: "unfolds" as a noun | "Unfoldings" at 295, 297, 336, 423, 446. The verb "unfolds" at 663 is kept. Comment lines are unchanged. |
| reader-X | §2.21, §3: "documented exception", "a bound fixed before production" | see N2 |
| reader-D | §2.16: "Two choices were informed by the data" is followed by one item that is not a choice | 694–695: "Two parts of the procedure were informed by the data." This is the base's sense ("Two data-informed elements are disclosed"). |
| (R11) | §2.26, §3: "claim variant" | defined in the Fig. 4 caption (R11). It no longer appears in the body text. |

#### 3. New F-list and P-list items (flagged, not made)

| id | location | reader item | proposal | why not made |
|---|---|---|---|---|
| F17 | IV B statistical-block paragraph | §2.11, §4.3: the reader could not tell whether the quoted statistical block has the corrected construction (the completeness division removed) | add "The quoted block is built without the completeness division" if the records confirm it | a new factual claim; it needs the records (stageC DESIGN S3.4) and the director |
| F18 | IV B, Sec. VII | §3: "statistical band" and "rebuilt band" sit beside "statistical block", and "random throws" beside "universes" | one term each | the note uses "rebuilt band" (sec:coverage) and "throws" (sec_5d). Renaming in the paper alone would make the two deliverables disagree, and "throws" may not be the same object as the MAT universes |
| F19 | IV B endpoint | §2.13, §3: "independent-generator samples that have not already been inspected" is blinding vocabulary | the note's "samples from independent event generators beyond the truth-level ones already examined" | adds "truth-level" to the paper (new content), although it is the note's and DECISION-20261014's wording |
| F20 | abstract, Intro | §2.1: "hold only under stated conditions" does not name the conditions | name both conditions in the abstract's conditions sentence | the abstract's last sentence already names the two that limit interpretation. Naming all six is new content, and moving the last sentence up would be a reorder of the abstract's claims |
| F21 | VI B (i), VI C | §4.8: a positive summary ("if the residual is within the extrapolation estimate, the rejections apply to G itself; they survive shifts about twice that estimate") | as the reader proposes | a new inferential claim that changes its strength (C3) |
| F22 | IV A | §4.2: say plainly that a significant correlated shape difference remains | — | it changes claim strength ("indicative only") |
| P15 | VI A, VI B (i), VI C | §5: gather the post hoc and timing disclosures into one "Blinding and analysis sequence" paragraph | a move within Sec. VI is allowed by C4 only if every caveat stays with its claim. Several are attached to specific claims (the scan, the lost-seed rerun, the coarse projections) | for the director |
| P16 | IV B | §2.12: state the earlier-budget errors as method ("each universe is unfolded against the same truth reference as the nominal; background-template statistics are propagated") | the same as P4 | EDITORIAL-20261011 H1 warns against detaching it |

The earlier F1–F16 and P1–P14 (impl-paper.md) stand. F4 (numbers for the "predefined criteria"), F6 (the rate), F9
(the use of the 5D covariance) and P10 (the Fig. 4 legend) are the reader's strongest remaining items. All four are
for Joseph or for out-of-scope files.

#### 4. Invariance check

Command: `python3 -I …/check_invariance.py $W 28d28626 > $S/inv-paper-r2.out; echo rc=$?` gave **rc=1**. The
non-zero exit comes from the note block's numeral DIFF (the note fixer's printed KNOWN_ISSUES pointers moved to
comments). That block is not in my files. The paper block, verbatim, with the 48 added comment lines tallied:

```
== paper
  [SAME] numerals (325)
  [SAME] value macros (68)
  [SAME] cite keys (64)
  [SAME] ref targets (35)
  [SAME] labels (18)
  [SAME] comment lines: all 204 base lines survive
  [INFO] comment lines added (48):
     14 x % plain-language pass (DECISION-20261018-joseph-plain-language-pass)            [round 1]
      1 x % plain-language pass, director ruling on base defect paper F3 (...; PLAIN-LANGUAGE.md C7)  [round 1]
     33 x % plain-language pass, review fix <id> (DECISION-20261018-joseph-plain-language-pass)  [this round]
          ids: R1 x1, R1+R4 x2, R2, R3 x2, R4, R5, R6 x2, R7, R8, R9, R10, R11+N7, R12, R13, W1, N1 x2,
               N2+reader-X, N3 x2, N6, reader-B x2, reader-D, reader-E x3, reader-U x3
== files changed outside scope
  [SAME] none
```

There is no DIFF in the paper block, so there is no numeral spelling change to list. One accident was caught and
repaired before the build. Seven of my marker comments had been appended to a line that still carried the start of the
next sentence, which commented those words out ("With it a reader can", "We tested it in two", "This motivates …",
"Vertical lines mark …", "We quote no …", "Their", "Pseudo-experiments that include"). No numeral was in them, so the
checker could not see it. Each was split back onto its own line (`grep` for a marker followed by text now finds
nothing), and the rendered text of every site was read back from the PDF.

#### 5. Build

`$S/build_copy.sh paper-r2` gave **rc=0**, on the final sources. All four targets report `OK … written by this run; no
unresolved references`. The containment gate gives SELF-TEST PASS and RESULT PASS. The Sec. IV receipt gate gives
SELF-TEST PASS (18 perturbations rejected) and SEC4-RECEIPTS PASS (15/15). The PDF text has no "??". The two overfull
hboxes (title block 11.06 pt, Table I 0.71 pt) are the base's own.

| PDF | pages |
|---|---|
| main_paper | **12** (≤ 12; page 12 holds references [20]–[39] only) |
| main_note | 124 (includes the note fixer's concurrent edits) |
| main_primer | 14 |
| pet_note | 26 |

Pages read in `builds/paper-r2/repo/docs/analysis-note/main_paper.pdf`: every changed sentence was extracted and read
in context from pages 1–6, 7, 9, 10 and 11. Pages 5 (IV B–C) and 12 were also checked as rendered images. No stray
comment text and no broken sentences were found.

#### 6. Report path and summary

`/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/plain-language/fix-paper.md`

1. All 3 MATERIAL and 10 MINOR findings were verified against the base and their sources, and fixed. The fixes are
   normalization-only anchors (R1), corrected flux sampling (R3), and the paper's W1/R2 sentences copied word for word
   from the note's current text.
2. Of the 7 NOTEs, N1, N3 and N6 are fixed, N2 is partly fixed ("documented exception" is replaced), N7 is handled in
   the caption, and N4 and N5 stay with Joseph (F4, F6).
3. Reader-derived register fixes: the covariance blocks are made consistent (four blocks, normalization and flux inside
   the universe block); the central-value and joint-test estimators are named once; "unfoldings"; "claim variant" is
   defined; "Two parts of the procedure".
4. The paper invariance block is all SAME: 325 numerals, 68 macros, 64 cites, 35 refs, 18 labels, and all 204 base
   comments kept.
5. The build has rc 0, no unresolved references, both gates PASS, and the paper is 12 pages. New F17–F22 and P15–P16
   are for the director and Joseph.

---

## R12. Fix round, primer — `fix-primer.md` (sha256 `239b8026c211442c…`)

### Plain-language pass: primer fix round (review R1–R13, reader-after)

Writer: primer fix round. Worktree `wt-plain` (branch at `386ece45`, base of the pass `28d28626`).
Files edited: `docs/analysis-note/primer_body.tex` only. `main_primer.tex` (abstract) needed no change: no review
finding touches it, and the reader raised nothing in the abstract that is in rule. Nothing else touched, no git writes.
Line numbers `Lnnn` are in the edited `primer_body.tex` (working tree). Each changed site has a marker comment
`% plain-language pass, review fix <id> (DECISION-20261018-joseph-plain-language-pass)` on the line given.
Every base comment line is kept verbatim (the checker reports all 32 base lines survive).

#### 1. Review findings → disposition

| id | sev. | verified against | disposition | new text (line) |
|---|---|---|---|---|
| R1 | MATERIAL | `sec_joint.tex` l.52–55 (joint-test estimator = 400-tree, 31-leaf refinement classifier); `sec_5d.tex` l.106–117, l.131 ("Nothing is adopted"), l.176 (candidate R) | **fixed** (reviewer's text). "No change to the method" was false: the larger-classifier version is the joint-test estimator. | L474–476: "None of these studies changed the five-quantity central value or its quoted uncertainty." |
| R2 | MATERIAL | base L108–110 and the caveats right after it (base L138–208); body L428–476 | **fixed.** Item 2 now carries the body's limits right after "pass particular recovery checks", in words, with no numerals. | L131–143: "… pass particular recovery checks. Other end-to-end tests show biases that are not included in their quoted uncertainty: the unfolding follows a changed simulated truth only partly, and the background removal leaves a bias in some cells. That uncertainty has not met the requirements we set in advance, and it is used only under a documented exception to them, so their error bars have not been shown to be right. The one direct test of whether such error bars contain the truth as often as stated, made on a variant of the method, failed. …" ("in some cells" covers both the 4% highest-W bias and the ~1% left by the finer removal, so it does not say which treatment the product uses.) |
| R3 | MINOR | L184–185 ("close in size"), L251–254 (statistical bars untested) | **fixed** (reviewer's text). | L271–273: "With the central value reproduced, and its error bars found close in size to the published ones, we used …" |
| R4 | MINOR | body L384–386 (reason is measured), paper `sec:uncertainty-status` ("covariances from this estimator depend measurably on its random seed") | **fixed.** "Therefore" removed; the body's measured reason is given. | L141–143: "Their plots show central values only, and no significance is assigned to their differences from the simulations, because the uncertainty depends measurably on the learner's random seed." |
| R5 | MINOR | base L97–98, base L483–484; `sec_fps.tex` l.10 ("the reconstructed MINOS-based selection is unchanged") | **fixed** (reviewer's text). | L163–166: "Relaxing the published cuts on the true muon's motion, with the same event selection, enlarges the population being estimated without adding measured events." |
| R6 | MINOR | base L377–378; body L509–510 | **fixed.** Level in words ("five percent"), so no numeral is added and C1 counts are unchanged. | L154–156: "… is rejected at a combined error level of five percent, both overall and in shape alone." |
| R7 | MINOR | base L221–222 | **fixed** (reviewer's text). | L117–121: "… although a shape difference remains when judged with the published correlations between cells." |
| R8 | MINOR | definition of acceptance (fraction of true events selected) | **fixed** (reviewer's text). | L578–581: "in regions where the detector records only a small fraction of the true events (low acceptance)" |
| R9 | MINOR | L141, L520 ("a separate inference", "not a new measurement") | **fixed** (reviewer's text), combined with RD13 below. | L679–682: "The multi-quantity measurements are shown as central values only: their error bars have not been shown to be reliable, and end-to-end tests on simulation show biases that are not included in their quoted uncertainty." |
| R10 | NOTE | heading is new text; base had "still" | **fixed**, with a heading that names the content: "Limits on the multi-quantity results". The two pointers to it were updated to match. | L380–381 (heading); L321–323 (Fig. 3 caption pointer); L348–350 (puzzle-paragraph pointer) |
| R11 | NOTE | `paper_body.tex` l.142–144 | **fixed** (reviewer's text). | L487–490: "Here MEC (meson-exchange currents) labels GENIE with its model of the two-nucleon process added, …" |
| R12 | NOTE | `sec_5d.tex` l.105–117, l.176 | **fixed**, combined with RD6. | L456–459: "A later study found that the bootstrap of the version of the method with the larger classifier (its own resampling estimate of its statistical error) already carries this rounding variability." |
| R13 | NOTE | `sec_validation.tex` l.216–229 (fixed-truth test, pseudo-data from this analysis's simulation) | **fixed** (reviewer's text). | L242–245: "We did run such a test on the statistical part of those error bars, using simulated repeats drawn from our own simulation against a fixed, known truth." |
| N1 | director instruction | base L273–274 (base text, unchanged by the first round); paper abstract at `386ece45` ("pass checks of their marginal normalizations against the lower-dimensional results"); `paper_body.tex` l.456–458 ("marginal normalizations agree at the approximately 1–2% level") | **fixed** (aligned with the record, which supports agreement in normalization only). The only other "reproduce/agree" sentences in the primer are about the 2D result (L114, L161–185, Fig. 2, the takeaway, the abstract), so they were left alone. | L278–281: "Each richer measurement, when collapsed back down, agrees with the simpler one in overall normalization --- a built-in consistency check." (Base defect under C7; the marker records it as director-instructed.) |

No finding was rejected.

#### 2. Reader-derived changes (in-rule register only)

| id | site | change | rule |
|---|---|---|---|
| RD1 | "One more distinction matters later" paragraph, L93–110 | "The scalar classifiers, which read summary quantities" → "The classifiers that read summary quantities of each event". "The original, recoil-only PET classifier does not use the muon" → "The original version of PET reads only the hadronic recoil (the energy deposited by particles other than the muon), so it does not use the muon, even though …". "Full-event PET adds muon features" → "A later, full-event version of PET also reads the muon" (the same as L551–552). "The companion analysis note's selection-versus-features table gives each analysis's choices" → "A table in the companion analysis note lists, for each analysis, what it selects on and what its learner reads". Every sentence is kept; nothing moved. | R2, R3 |
| RD2 | item 1, L118–119 | gloss at the first use of "central value": "(the best estimate itself, apart from its error bars)" | R3 |
| RD3 | item 2 L137–139; subsection opening L383–390; L397–398 | "in use under a documented exception to the analysis's own qualification rules" → "It is the uncertainty we quote for the five-quantity result, but it has not met the requirements we set in advance, so it is used only under a documented exception to them" (paper `sec:uncertainty-status`: "has not met the analysis's predeclared qualification criteria … used only under a documented exception"; the primer's L455/F4 text already names it as "the uncertainty quoted for the five-quantity central value"). "But the multi-quantity plots" → "The multi-quantity plots". "not on the version in use" → "not on the one we quote". | R2 |
| RD4 | closing line of the findings list, L170–171 | "Passing one of these checks does not make up for a check that another result lacks." → "Each result is only as validated as its own checks." (the same content, said positively; base: "None of these statuses supplies another's missing validation") | R1 |
| RD5 | detector-uncertainty paragraph, L427–429 | "It does not, by itself, show that …" → "By itself, it says nothing about whether …" (the brief's own R1 pattern) | R1 |
| RD6 | follow-up paragraph, L456–463 | "paired study" and "candidate" removed (R12). The double negation is now "That finding is limited to that version's own bootstrap: it does not carry over to the uncertainty quoted for the five-quantity central value, and the stability test still counts as failed." (`sec_5d.tex` l.117: "addresses containment only for this candidate"; l.305–306: "does not regrade the stability failure … or transfer to the adopted covariance"). The F4 ruling's marker and wording ("does not carry over to the uncertainty quoted for the five-quantity central value") are kept. | R1, R2 |
| RD7 | remedies paragraph, L465–476 | adds a lead sentence, "Three possible remedies each have a limit." "So we have not established a tradeoff" → "so no tradeoff between bias and variability is established". "Changing the starting model does not give a guaranteed error bound" → "Changing the starting model gives no guaranteed error bound." Each limit is unchanged. I chose "possible" over the reader's "obvious" (an opinion) and over "further" (longer runs are more iterations, which the paragraph before already covers). | R1 |
| RD8 | hypothesis sentence, L490–492 | Fixes a sentence the reader could not parse: "each hypothesis sets the true cross section, in each cell of a finite grid of true values, to that generator's rate, with Tune v1's shape inside each cell." | R4 |
| RD9 | κ paragraph, L537–540 | "At that point the decision becomes ambiguous; it does not become a clear non-rejection. The scan …, and it does not bound …" → "At that point the decision becomes ambiguous, not a clear non-rejection. The scan moves in one direction only and gives no bound on …". The κ numbers and "first decision" are unchanged. F10 (stating determinacy up to κ≈5) was not made. | R1 |
| RD10 | PET paragraphs L562–575, L613–615, L625–627; Fig. 5 caption L632–634 | "candidate designs … qualified to go on to a coverage test" → "designs tried … met the requirements for going on to a coverage test". "(the finalists)" removed. "Better recovery did not give a qualified design: the study ended with no eligible design" → "Better recovery was not enough: no design met every requirement fixed in advance" (the same wording as summary item 5). "One finalist" → "One of the two best designs". "which finalist" → "which of the two". "this finalist's" → "this design's". "ranking of the PET finalists" → "ranking of the two PET designs". "the outcome that no PET design was eligible" → "they leave the outcome unchanged: no PET design met every requirement fixed in advance". Fig. 5: "each PET finalist" → "each of the two best PET designs". | R2 |
| RD11 | L587–588, L618–619 | "Saved outputs of these studies give a partial explanation" → "Our diagnosis of these studies gives a partial explanation"; "a diagnosis from the saved outputs finds" → "a separate diagnosis finds" (the cites are kept) | R2 |
| RD12 | L601–604 | "ran PET and OmniFold with the tree learner" → "ran OmniFold with each of the two learners, PET and the tree learner" (PET is a learner inside OmniFold, as L546–553 says). "Which method does better" → "Which learner does better". | R2/clarity |
| RD13 | takeaway, L679–682 | In addition to R9, the takeaway now states the body's bias caveat in words, with no numeral. It restates item 2 and L428–444 ("follows it only partly … Neither effect is in the quoted uncertainty yet"). The director may revert this clause if a takeaway beyond F1 is not wanted. | C2 (restatement) |

**Considered and not applied:**
- The √6 sentence (L593–595), because the reader's rewrite would be wrong. `sec_pet_campaigns.tex` l.157–162 shows that the "diagnostic width adjustment" is a modeled variance of the member mean, not division by √6. The sentence is left as it was at the base (see F-new-5).
- "A simulation that is not rejected is not thereby accepted as true." The reader suggested cutting it, which is a caveat cut (C2/C4).
- "That test was of the statistical error bars in use when it ran." It is director ruling note-F2, so it stays.
- "The published numbers are unchanged by this check." It is already F5, for the author.
- Fig. 6's "extended-fiducial scalar study". I tried "with the tree learner" and reverted it. `sec_fps.tex` l.4 says "a preliminary scalar central value", so I could not tell whether "scalar" there means the tree learner or a single-number σ_ext (F-new-6).

#### 3. New F/P items (flagged, not made)

| id | location | proposal | why not made |
|---|---|---|---|
| F-new-1 | item 2 / L438–440 | put the typical size of the changed-truth bias in item 2 and in the takeaway (body: "about 10% off, and the highest-W cells much more") | it would duplicate a numeral (C1 counts). The item now says it in words. For the director: a numeral duplicate in a summary needs a C1 entry. |
| F-new-2 | puzzle paragraph L332–355 | give the corner excess over Tune v1 as a number (reader §4.3) | no such number is in the primer body; it would be new content (C3), for Joseph |
| F-new-3 | joint test L494–512 | one sentence on why the test is calibrated independently of the quoted error bars: the null distribution comes from pseudo-experiments that rerun the full chain (reader §6.4). The body already says "we simulated … pseudo-experiments … unfolded each one, and counted"; the paper abstract says "calibrated with pseudo-experiments that rerun the full analysis chain". | adding "so the test does not rely on the quoted error bars" is a new inference in the primer (C3), for Joseph |
| F-new-4 | §3 "Limits on …" | rank the limits; name the top three once (reader §1.4) | a restructuring that changes emphasis; C4/C3, for Joseph |
| F-new-5 **base defect** | L593–595 | "A diagnostic width adjustment still leaves poor coverage, especially at low acceptance, so dividing the width by the square root of six is not a validated repair." The note (`sec_pet_campaigns.tex` l.157–162) gives a different reason: dividing by √6 is unjustified because the event-sample component is common to the six fits and bias does not average away (the primer's previous sentence). The diagnostic adjustment is a separate, modeled-variance interval that still covers poorly. Proposed: "Dividing the width by the square root of six is therefore not a valid repair, and a diagnostic width adjustment built from a model of the variance still leaves poor coverage, especially at low acceptance." | base text, alignment only; for the director (C7) |
| F-new-6 | Fig. 6 caption, panel titles | "extended-fiducial scalar study", "anchor ratio", "prior-swap ratio" (reader §2) | the caption's "scalar" is ambiguous in the source (see §2); the panel titles are in the figure (out of scope) |
| P-new-1 | bibliography (`technote.bib`) | titles such as "PET final-design selection: terminal decision record" and repository paths in [1], [3]–[7] read as a lab notebook (reader §2) | `technote.bib` is outside the primer's files and shared with the note |
| P-new-2 | Fig. 5 legend/footer (figure file) | "PET H2S1T24 (k=5)", "FB look-1 draws", "banks" (reader §2) | the figures are out of scope |
| P-new-3 | "One more distinction" paragraph | move the PET sentences to the PET section and the cut sentence to the signal-definition paragraph (reader §2) | a move; C4 allows it within a section only, and these are different sections |
| F-new-8 | Fig. 2 caption, L263–265 | add "the red curve is MINERvA's tuned simulation (Tune v1, built on GENIE 2.12.6)" (see §4) | adds a numeral (C1); for the director |
| F-new-7 | PET, L99–101 | expand the acronym (the reader notes "point-cloud transformer" does not match the letters) | no expansion appears in the note sources I searched; an expansion would be new content |

#### 4. Fig. 2 / Fig. 3 GENIE version

**There is no inconsistency. The two figures show two different simulations.**
- **Fig. 2** (`figures/MEFHC_5iter_fig13.pdf`, producer `2d-unfolding/plot_2d_threeway_fig13.py:200` via
  `make_figures.sh:35`). The red curve's legend is "GENIE 2.12.6 + MnvTune v1" (pdftotext confirms it). This is
  MINERvA Tune v1, the analysis reference simulation and the unfolding prior. The note (`sec_experiment.tex:24`,
  `sec_results.tex:118`) and the paper (`paper_body.tex:108`) both say GENIE 2.12.6.
- **Fig. 3** (`figures/eavailW_band.pdf`, producer `3d-unfolding/genie/overlay_eavailW_band.py` via
  `make_figures.sh:76`). The legend reads "GENIE-CV, GENIE+MEC, NuWro, GiBUU" and gives no version. The caption's
  "version 2.12.10" is the untuned gevgen central configuration (`sec_3d.tex:213`, `paper_body.tex:147`,
  `sec_joint.tex:19`).

The reader's confusion is real, though. The Fig. 2 caption does not say what the red curve is, so a reader meets
"2.12.6" there and "2.12.10" in Fig. 3 with nothing to link or separate them. A clarifying caption clause, e.g. "the
red curve is MINERvA's tuned simulation (Tune v1, built on GENIE 2.12.6)", would add a numeral to the primer (C1). It
is listed as F-new-8 for the director. No figure was changed.

#### 5. Invariance check (primer block, verbatim)

`python3 -I …/check_invariance.py $W 28d28626 > $S/inv-primer-r2.out; echo rc=$?` gave `rc=1`. The non-zero status
comes from the note block (`[DIFF] numerals …`, another fixer's files, in progress). The primer block has no DIFF, and
"files changed outside scope" is `[SAME] none`.

```
== primer
  [SAME] numerals (76)
  [SAME] value macros (13)
  [SAME] cite keys (7)
  [SAME] ref targets (5)
  [SAME] labels (3)
  [SAME] comment lines: all 32 base lines survive
  [INFO] comment lines added (43):
      (13 first-round markers: 6 plain-language and 7 director-ruling; 30 fix-round markers, listed at the lines in §1–2)
```
The full block, with all 43 added lines, is in `$S/inv-primer-r2-block.txt`. The 30 fix-round marker lines are the
ones at L93, 117, 131, 154, 163, 170, 242, 271, 279, 321, 349, 380, 383, 397, 427, 456, 465, 474, 487, 537, 562, 570,
579, 587, 601, 613, 618, 625, 632 and 679.

#### 6. Build

`$S/build_copy.sh primer-r2` (rerun after the last edit) gave `build_all rc=0`, and all four PDFs report "OK …
written by this run; no unresolved references". `main_primer.log` has 0 undefined references or citations. The
gates:
- SELF-TEST PASS;
- RESULT PASS (strict, all four products fresh);
- SELF-TEST PASS (18 perturbations rejected);
- SEC4-RECEIPTS PASS (15/15).

Page counts:
- **main_primer: 14** (unchanged from the first round);
- main_paper 12;
- main_note 123;
- pet_note 26.

These include the other fixers' files as they stood at build time.

The primer PDF is `$S/builds/primer-r2/repo/docs/analysis-note/main_primer.pdf` (sha256 `f91351bb…eddd86`). I read
the text of every changed page (pp. 3–5, 6–7 and 8–13) and rendered p. 3. The findings list, the new heading, the
remedies paragraph, the PET paragraphs, the Fig. 5 caption and the takeaway set cleanly.

**Same-model caveat:** written by Claude Opus 5.5. The edits have not been re-reviewed independently.

Report: `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/plain-language/fix-primer.md`

Summary:
1. All 13 review findings are fixed (R1, R2 MATERIAL; R3–R9 MINOR; R10–R13 NOTE), none rejected, plus N1: the "collapsed back down reproduces" sentence now claims agreement in overall normalization only.
2. 13 reader-derived register edits remove "qualification rules", "finalist", "eligible", "candidate", "paired study", "saved outputs" and the p. 3 internal names, and recast stacked negations positively; no numeral is added.
3. The primer invariance block is all SAME (76/13/7/5/3; 32 base comments survive). rc=1 comes only from the note block.
4. The build gives rc 0, no unresolved references, all gates PASS; the primer has 14 pages.
5. Fig. 2's "GENIE 2.12.6 + MnvTune v1" is Tune v1 and Fig. 3's 2.12.10 is untuned GENIE CV, so there is no conflict; a caption clause is flagged (F-new-8), with F-new-1…7 and P-new-1…3 for the director or Joseph.

---

## R13. Fix round, note — `fix-note.md` (sha256 `5d94c1cbbefb0650…`)

### Fix round 2: analysis note, in-scope parts (writer's record)

Worktree `wt-plain` (HEAD `386ece45`, base of the pass `28d28626`). LaTeX edits only, no git writes. The edits are
in the working tree on top of `386ece45`. The edit script is `$S/fix_r2.py`, plus one comment repair and one m5
re-wording for page budget, both described below. Files I touched: `main_note.tex` (abstract), `sec_execsummary.tex`,
`sec_summary.tex`, `sec_systematics.tex` (before §"What changes …"), `sec_validation.tex` (§coverage).
`sec_results.tex` is unchanged in this round.

#### 1. Review findings and their dispositions

Each finding was checked against the base (`git show 28d28626:…`) and against the sources it cites before I applied it.

| id | verified against | disposition | new text (file:line, working tree) |
|---|---|---|---|
| **M1** | playlist-term `DESIGN.md` §2: "r_X = x_X / t_X, the unfolded data over that period's own MC truth"; "**Reference: none**"; m = Σ e_X r_X; S-ref = r_X/r_A uses the same double ratios. §3: "Each period is unfolded with its own MC response". DECISION-20261015 playlist §2: "how 1F and the per-period MC responses are handled". DRAFT-disclosures D5 Required clause l.202–206. **Reviewer correct** on (a) and (b). | **Applied** (director ruling). The own-response element is restored. The reason no reference period is needed is now the comparison with the exposure-weighted mean of the three. Every other D5 element is unchanged: limited by few groups, possible regularization shrinkage, and retained statistical and training noise; contains the differences automatically, which says nothing about coverage; "for the same reason … not a test". The base "verbatim" comment is kept. The added comment now names the new first words and the M1 reasoning. | `sec_systematics.tex:308–312`: "The block uses each period's unfolded result over that period's own simulated truth, with each period unfolded through its own simulated detector response. Because each period is compared with the exposure-weighted mean of the three, the block needs no reference period, and it does not identify which period is correct." Comment at l.329–335. |
| **M2** | `sec_3d.tex:122–133`: normalization +0.95 %, median ratio 1.0016; "The *shape* agrees less closely" (χ²/ndf 4.98, ~4.4 % scatter). `sec_eavailw.tex:32–35`: 5D/4D total 1.0011, per-axis medians 0.3–1.5 %. **Reviewer correct.** The base `sec_summary.tex` bullet 2 ("agree with their lower-dimensional predecessors to ≈1–2 %") is the same over-reading. | **Applied at all three sites** (director ruling on base defect note M2), each marked `% plain-language pass, review fix M2, director ruling on base defect note M2 (…)`. | `main_note.tex:61–63`: "Each passes marginal-normalization checks against the lower-dimensional result to ≈1–2 %." `sec_execsummary.tex:37`: "…gives simultaneous unfolds, each passing marginal-normalization checks against the lower-dimensional result to ≈1–2 % (§…)". `sec_summary.tex:23–25`: "…unfolds (+E_avail, +q₃, +W) pass marginal-normalization checks against the lower-dimensional results to ≈1–2 % and recover an injected E_avail shape". |
| **m1** | DECISION-20261014 l.49–51: "Full scientific closeout is NOT ACHIEVED … That would be independent validation that supports the interval, bias and covariance claims". PLAN-20261011 §1 l.44: "205 reported cells, their area-weighted integral and 30 projections: 236 functionals". **Reviewer correct.** | **Applied.** The missing validation is now named as the endpoint ruling defines it. The two coverage cases are kept. "All bins" is widened to "all reported bins and projections", which matches the 236 functionals; a negative statement that gets wider is not a weakening. The first-round comment is kept, and an added comment says which of its carriers are superseded. | `sec_systematics.tex:347–350`: "The result's intervals, bias and covariance have not been independently validated. In particular, the coverage of its intervals has not been validated on independent simulated samples, nor simultaneously over all reported bins and projections." Comment at l.384–389. |
| **m2** | `sec_validation.tex` §coverage l.216: the band "in use when it ran". App. history l.51: VL162 was rebuilt as VL170, adopted 2026-10-06; LightGBM was chosen 2026-10-11. **Reviewer correct.** | **Applied** (director ruling). | `sec_summary.tex:16–18`: "The statistical band in use when the fixed-truth coverage test ran failed it in its tails." |
| **m3** | Base l.115–117 kept "the earlier (VL170) bootstrap" and "the earlier statistical band" apart only through the label. App. history l.51 and l.348: VL170 is the rebuild of VL162. **Reviewer correct.** | **Applied.** The VL170 label is restored in print, in the form §coverage already uses ("labelled … in the appendices"). The tested band is now "the statistical band in use when it ran, before that rebuild". The connective "That band was then rebuilt." is dropped because "before that rebuild" carries it. | `sec_systematics.tex:119–123`: "…the split data/MC streams of the earlier, rebuilt bootstrap (labelled VL170 in the appendices) are in App. …. The fixed-truth coverage test (§…) found that the statistical band in use when it ran, before that rebuild, undercovered in its tails, unevenly across bins." |
| **m4** | `sec_5d.tex:471–472`: "Items one, two and four use two companion covariances … only item three describes these bytes". l.528–531: "predeclared and not computed for this object". **Reviewer correct.** | **Applied.** "its" is dropped, so the sensitivity is no longer attributed to the quoted covariance. The sentence is 3 characters shorter. | `sec_execsummary.tex:50`: "…used under a documented exception, but the estimator-seed sensitivity measured on two seed-varied companion covariances exceeds the limit fixed before production, …" |
| **m5** | `sec_5d.tex:471`: "Four measurements bound the claims"; item 4 (l.516–523) is a bounding measurement, not a limitation. **Reviewer correct** on (a) and (b). | **Applied, with my own wording for (b).** The reviewer's "not used for any quoted result" is not accurate: the companions give quoted numbers (s_proj, items 1, 2 and 4). A first attempt, "no other corrected candidate is used as the covariance of any result", added a line and pushed the exec summary onto p. 4 (124 pages). The final wording is the same claim as base "not adopted" and fits. | `sec_execsummary.tex:135`: "Four measurements, led by …, limit every result built from the five-dimensional covariance in use (§…); no other corrected candidate is used in its place." |
| **m6** | Exec summary: "under six stated conditions"; sec_joint conditions. **Reviewer correct**: "hold under" reads as an assurance. | **Applied.** | `main_note.tex:79`: "These tests are valid only under stated conditions." |
| **N1** | KNOWN_ISSUES.md rows: 85 OPEN/DEFERRED; 91 OPEN 2026-10-09 (closure with the row owner); 92 OPEN 2026-10-11; 84 FIXED; 95, 96 RESOLVED IN THE QUOTED CONSTRUCTION. The note itself calls the repository "the analysis repository" (`app_provenance.tex:4`). | **Applied for the open rows (85 ×2, 91, 92 ×2).** Each base printed pointer is now a plain route without a row number: "tracked in the analysis repository's known-issues log". Every row number stays in its adjacent comment. "Tracked" implies only that the row exists; no status word ("open") is printed beyond what the base printed. **Not restored for the resolved rows (84, 95 ×2, 96)**: see F-r2-2. | `sec_systematics.tex:31–32` (92), `:128–129` (85), `:230` (92), `:251–252` (91); `sec_validation.tex:294–296` (85). |
| **N2** | Exec summary l.50 and l.135, summary l.36, and sec_5d all use "estimator-seed". | **Applied** (pure register; one term for one quantity). | `main_note.tex:74–75`: "Coverage and estimator-seed studies show further limitations." |
| **N3** | The comment cites the rule's commit `8eb40e5f`; KNOWN_ISSUES row 85: "committed before any run". | **Applied.** | `sec_validation.tex:291`: "with a decision rule recorded before it ran". |
| **N4** | §coverage defines C_k as the fraction with \|z\| ≤ k. | **Applied** (punctuation only). | `sec_execsummary.tex:100`: "(the fraction within 2σ, C₂ = \covTwoDCTwo, vs. 0.954; §…)" |
| **N5** | D2: S1 "has not been coverage-tested at all". The exec summary says "has not been tested". `sec_systematics.tex:127` and `sec_summary.tex:18–19` say "neither it nor the statistical block quoted here has been tested independently". | **Not applied; F-list (base defect, C7).** The text is base content, unchanged in substance, and changing it is the director's call. | — (F-r2-1) |

Director corrections from round 1 (F1 at `sec_systematics.tex:130–133`, F2 now replaced by m2) are untouched apart from m2.

#### 2. New F- and P-items

| id | location | base / current text | proposed text | reason |
|---|---|---|---|---|
| F-r2-1 **base defect** (N5) | `sec_systematics.tex:127`; `sec_summary.tex:18–19` | "neither it nor the statistical block quoted here has been tested independently" / "neither it nor the statistical block quoted now has been tested independently" | "the rebuilt band has not been tested independently, and the statistical block quoted here has not been tested" | D2 and the exec summary say the quoted block S1 has not been tested at all. "Independently" lets a reader infer some non-independent test of S1. The text is base content, so this is for the director (C7). |
| F-r2-2 (N1, resolved rows) | `sec_systematics.tex:46–48` (95, flux band), `:77–79` (96, MINOS own-flux), `sec_results.tex` §results-uq 6.87 % clause (95), `sec_validation.tex:274–275` (84) | pointer in a comment only | either leave as is, or add "(corrected; recorded in the analysis repository's known-issues log)" | These rows are fixed or resolved, so a pointer without a row number tells the reader only that the issue was once tracked. The printed sentences already state the fix. The 84 and 6.87 % sites already point to App. history or App. provenance. The note also prints 84 (`app_history.tex:227`, `app_provenance.tex:103`), 92 (`app_statmethods.tex:194`) and 95 (`app_statmethods.tex:399, 888`) outside scope. I found no other printed 96. I did not add the four pointers because they add little and cost lines. If the director wants every base pointer restored, the proposed text drops in at those four sites. |
| F-r2-3 (N1, permanent route) | App. provenance `tab:prov-trackers` (out of scope) | — | add tags for rows 85, 91 and 92 | This is the reviewer's own suggestion to the director. It would give the reader the row numbers that the words-only route drops. |

No new P-items.

#### 3. Invariance check (note block, verbatim)

`python3 -I …/check_invariance.py $W 28d28626 > $S/inv-note-r2.out; echo rc=$?` gave **rc=1**. It exits 1 on any
difference. The paper and primer blocks in the same output belong to the other fixers.

```
== note
  [DIFF] numerals: lost {'92': 2, '95': 2, '96': 1, '85': 2, '91': 1, '84': 1}  gained {'2': 7}
  [SAME] value macros (84)
  [SAME] cite keys (28)
  [SAME] ref targets (147)
  [SAME] labels (36)
  [SAME] comment lines: all 264 base lines survive
  [INFO] comment lines added (68):
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass, review fix M2, director ruling on base defect note M2 (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass, review fix M2, director ruling on base defect note M2 (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass, review fix M2, director ruling on base defect note M2 (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass, review fix N2 (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass, review fix m6 (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass, review fix m4 (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass, review fix N4 (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass, review fix m5 (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass, director ruling on base defect note F2 (DECISION-20261018-joseph-plain-language-pass; PLAIN-LANGUAGE.md C7)
      % plain-language pass, review fix m2 (DECISION-20261018-joseph-plain-language-pass)
      % Printed pointer moved to this comment by the plain-language pass: (\texttt{KNOWN\_ISSUES.md} 92).
      % Printed pointer moved to this comment by the plain-language pass: (\texttt{KNOWN\_ISSUES.md} 92).
      % plain-language pass, review fix N1 (DECISION-20261018-joseph-plain-language-pass): the route is restored in words (row 92).
      % plain-language pass, review fix N1 (DECISION-20261018-joseph-plain-language-pass): the route is restored in words (row 92).
      % Printed pointer moved to this comment by the plain-language pass: the flux band's \texttt{KNOWN\_ISSUES.md} 95.
      % Printed pointer moved to this comment by the plain-language pass: (\texttt{KNOWN\_ISSUES.md} 96).
      % plain-language pass, review fix m3 (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass, director ruling on base defect note F1 (DECISION-20261018-joseph-plain-language-pass; PLAIN-LANGUAGE.md C7)
      % Printed pointer moved to this comment by the plain-language pass: (\texttt{KNOWN\_ISSUES.md} 85); the earlier
      % bootstrap and the rebuilt band are VL170 (printed identifier removed).
      % Review fix N1: the route is restored in words ("tracked in the analysis repository's known-issues log" = row 85).
      % Review fix m3: the VL170 label is restored in print for the rebuilt bootstrap, and the tested band (VL162) is named
      % "the statistical band in use when it ran", as in sec:coverage.
      % Printed identifier removed by the plain-language pass: the earlier 2D budget is VL175.
      % Printed pointer moved to this comment by the plain-language pass: the index identity's (\texttt{KNOWN\_ISSUES.md} 91).
      % plain-language pass, review fix N1 (DECISION-20261018-joseph-plain-language-pass): the route is restored in words (row 91).
      % plain-language pass, review fix M1 (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass): D5's Required clause is now in equivalent
      % wording (DRAFT-disclosures D5: "or equivalent wording used"), from "The block uses each period's unfolded result" to
      % "whether its size is right"; the "its own check cannot fail" sentence follows it. The earlier budget is VL175.
      % Review fix M1: "uses the periods' own simulated responses" is carried by "unfolded through its own simulated detector
      % response" (playlist-term DESIGN §3 "MC responses"); "reference-free" by the comparison with the exposure-weighted mean
      % of the three (DESIGN §2 "Reference: none", m = sum_X e_X r_X), not by the double ratio, which the 1A-1F reference
      % variant S-ref also uses.
      % plain-language pass, review fix m1 (DECISION-20261018-joseph-plain-language-pass)
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass): W1's "Full scientific closeout is not achieved" is
      % carried by "Full validation of the result has not been achieved"; "population or simultaneous interval coverage" by
      % the two coverage cases; "no calibrated covariance-based generator significance" by the next sentence; "not
      % included in any uncertainty block" by "not included in the covariance"; "neither is priced" by "we assign no uncertainty".
      % plain-language pass, review fix m1 (DECISION-20261018-joseph-plain-language-pass): the first two carriers above are
      % superseded. "Full scientific closeout is not achieved" is now carried by "The result's intervals, bias and covariance
      % have not been independently validated", the endpoint ruling's definition (DECISION-20261014 l.49-56: "independent
      % validation that supports the interval, bias and covariance claims"); the coverage cases are "on independent simulated
      % samples" and "simultaneously over all reported bins and projections" (PLAN-20261011 §1: 205 cells, their integral and
      % 30 projections, 236 functionals).
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass). Printed pointer moved to this comment: the 6.87 % clause's
      % (\texttt{KNOWN\_ISSUES.md} 95).
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass). Printed pointer moved to this comment: the rebuild's
      % (\texttt{KNOWN\_ISSUES.md} 84).
      % plain-language pass (DECISION-20261018-joseph-plain-language-pass). Printed pointer moved to this comment: the deferred
      % re-test's (\texttt{KNOWN\_ISSUES.md} 85).
      % plain-language pass, review fix N1 and N3 (DECISION-20261018-joseph-plain-language-pass): the route is restored in words (row 85); "fixed before it
      % ran" becomes "recorded before it ran" (the rule was committed before the run, 8eb40e5f).
== files changed outside scope
```

The block ends at the next header, which reads "== files changed outside scope" followed by `[SAME] none`.
In the INFO list, the 15 identical bare markers `% plain-language pass (DECISION-20261018-joseph-plain-language-pass)`
are all round 1.

**Each DIFF in the "== note" block, explained:**
- **Numerals lost: 92 ×2, 95 ×2, 96, 85 ×2, 91, 84.** These are unchanged from round 1. Each is the row number of a
  base printed `\texttt{KNOWN\_ISSUES.md} N` pointer. Every one survives verbatim in an adjacent comment (the INFO lines
  "Printed pointer moved …"). For 85, 91 and 92 the printed route is now restored in words (N1). No physics number is
  involved.
- **Numerals gained: '2' ×7.** These are unchanged from round 1 and come from χ² superscripts, $2\sigma$ and "2D" in a
  title (see `impl-note.md` §3). This round adds no numeral. The restored `\texttt{VL170}` was in the base's print, and
  the checker does not count it.
- **Value macros, cite keys, ref targets, labels:** SAME. All 264 base comment lines survive.
- **Comment lines added, now 68 (36 in round 1).** The new ones are the review-fix markers
  `% plain-language pass, review fix <id> (DECISION-20261018-joseph-plain-language-pass)` and the M1, m1, m3, N1 and N3
  explanations. The first-round W1 explanatory comment was split by my first script run. I repaired it, so its original
  line now reads whole again, followed by the m1 supersession note.

#### 4. Scope confirmation

`git -C $W diff -U0 28d28626 -- …` base hunk starts:
- `main_note.tex`: 50, 56, 60, 68–78. These are inside the abstract, base lines 45–82.
- `sec_systematics.tex`: 19–430. The last hunk is at 430, and §"What changes for the higher-dimensional products" is
  at base line 432.
- `sec_results.tex`: 54–202. These are inside §results-compare and §results-uq, base lines 51–206. This round did not
  touch them; they are round 1.
- `sec_validation.tex`: 216–301. These are inside §coverage, base lines 214–314.

`sec_execsummary.tex` and `sec_summary.tex` are in scope in full. The checker reports "files changed outside scope:
none". `git status` also shows `main_paper.tex`, `paper_body.tex` and `primer_body.tex` modified. Those are the
concurrent paper and primer fixers' files; I did not touch them.

#### 5. Build, gates and page counts

`$S/build_copy.sh note-r2` (final run, after the m5 re-wording) gave **build_all rc=0**:
- `main_note.pdf`, `main_primer.pdf`, `main_paper.pdf` and `pet_note.pdf`: each "written by this run; no unresolved
  references".
- In the final `.log` files, the count of `LaTeX Warning: Reference|Citation|undefined references` is 0 for all four.
- Containment gate: `RESULT :: PASS` (self-test PASS). Sec. IV receipt gate: `SEC4-RECEIPTS :: PASS (15/15)`
  (self-test PASS, 18 perturbations rejected).
- Pages: **main_note 123** (unchanged); main_paper 12; main_primer 14; pet_note 26. The paper and primer counts include
  the other fixers' concurrent edits.
- The executive summary ends on p. 3. Its last line is "documented separately (App. F).", and the Contents begins on
  p. 4.
- The intermediate build at 124 pages was caused by the first m5 wording, which added one line. It was resolved by
  re-wording m5, not by reverting any fix.

Report: `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/plain-language/fix-note.md`

Summary:
1. M1, M2 (all three sites, director ruling on base defect note M2), and m1–m6 are applied after I checked each against the base and its cited records. All reviewer findings held. My m5 wording differs from the reviewer's, because "not used for any quoted result" would be false of the companions.
2. NOTE findings: N1 restored in words for the open rows (85, 91, 92); N2, N3 and N4 applied; N5 is in the F-list as a base defect (F-r2-1).
3. The resolved-row pointers (84, 95, 96) are not restored (F-r2-2). An App. provenance tag for 85, 91 and 92 is suggested as F-r2-3.
4. Invariance: rc=1, with the same DIFF as round 1 (KI row numbers moved to comments, χ² superscripts). Macros, cites, refs, labels and all 264 base comments are SAME. Nothing changed outside scope.
5. Build rc=0, no unresolved references, both gates PASS. The note is 123 pages, with the exec summary on pp. 2–3.

---

## R14. Verification of the fix round (24ec59af) — `verify-r2.md` (sha256 `4e4905cbc51dd724…`)

### Verification of the plain-language fix round (386ece45 → 24ec59af)

Verifier: independent and read-only, in a fresh context. I wrote none of the text, edited no source and made no git
write. `git -C wt-plain status --short` was empty before and after; HEAD is `24ec59af`.

Method:
- **Sources.** I extracted every in-scope file at `28d28626`, `386ece45` and `24ec59af` with `git show`, and read the
  diff `386ece45..24ec59af -- docs/analysis-note` in full.
- **Records the findings cite:**
  - DECISION-20261014 §2 (l.49–56);
  - DRAFT-disclosures D2 and D5;
  - playlist-term DESIGN §2–§3;
  - PLAN-20261011 §1 l.44;
  - stageC/production/DESIGN.md l.273.
- **Invariance.** `check_invariance.py` re-run against `28d28626` (exit 1). The paper and primer blocks are all SAME,
  with all 204 and 32 base comment lines surviving. The note block shows only round 1's KI row numerals and the χ²
  "2" superscripts. "Mid-line comment: none" and "outside scope: none".
- **PDFs.** `builds/r2` was built from sources byte-identical to `24ec59af` for all ten files. I compared their
  `pdftotext` output with the source.

Line numbers below are at `24ec59af`.

#### (a) Review findings: disposition claimed → verified

##### Paper (review-paper.md: MATERIAL 3, MINOR 10, NOTE 7) plus the director's W1 instruction

| id | claimed | verified? | new text at 24ec59af |
|---|---|---|---|
| R1 (MAT) | fixed, normalization only, 3 sites | **YES** | `paper_body.tex:62–65` "agree in normalization with the lower-dimensional results they extend"; `:524` "agreement in the marginal normalizations coexists with substantial regularization bias"; `:972–973` "agree in normalization with the lower-dimensional results they extend". The abstract (`main_paper.tex:57–58`) was already "pass checks of their marginal normalizations" and is unchanged. No widened marginal site is left (grep for marginal / lower-dimensional / anchor). |
| R2 (MAT) | fixed, note's wording copied | **YES** | `:440–443` "In particular, the coverage of its intervals has not been validated on independent simulated samples, nor simultaneously over all reported bins and projections." The wrong "average coverage of its per-bin intervals" gloss is gone. "Independent simulated samples" matches DECISION-20261014's "independent production-size MC". The text is word for word the note's. |
| W1 (director) | fixed | **YES** | `:438–439` "The result's intervals, bias and covariance have not been independently validated." DECISION-20261014 l.49–50: closeout = "independent validation that supports the interval, bias and covariance claims". All three objects are named, so what is missing is not narrowed. "Not achieved" is carried by the absence statement plus "We make no claim about coverage" (`:455`). See §(b) on strength. |
| R3 (MAT) | fixed | **YES** | `:155–157` "use a corrected flux sampling: they are reweighted exactly, event by event, to the analysis flux"; `:545–546` "(same-sample ratios computed with GENIE before its flux sampling was corrected)". The defect is again stated as a correction, as in the base. |
| R4 | fixed | **YES** | abstract `main_paper.tex:59` "pass closure checks with injected shape changes"; `:64–65`, `:973–974` "pass closure tests with injected shape changes". |
| R5 | fixed | **YES** | `main_paper.tex:72–74` "they do not show that the tested joint five-observable information discriminates beyond matched coarse projections of the same cells". |
| R6 | fixed | **YES** | `main_paper.tex:70` "These rejections hold only under stated conditions."; `:80` "reject at the 5% familywise level under six stated conditions (Sec. VI B). Two of them, …" |
| R7 | fixed | **YES** | `:403–404` "in 100 closure pseudo-experiments, specified in advance, against a fixed truth:" |
| R8 | fixed | **YES** | `:231–234` "is checked for completeness, an identity that must hold, and the dependence on the number of iterations is a stability diagnostic; neither establishes recovery or coverage." |
| R9 | fixed | **YES** | `:371–373` "it contains them by construction; this says nothing about its coverage, that is, whether its size is right." D5's key term "coverage" is restored. |
| R10 | fixed | **YES** for the finding as stated | `:365–367` "…so it relies on the periods' own simulated responses.  It does not identify a correct period." The limit no longer follows from "so". A remaining "so" defect is new finding **V1** (§b). |
| R11 | fixed | **YES** | `:792–794` "for the shifted null with the largest null median among those used in the decisions (labelled ``claim variant'' in the legend)" |
| R12 | fixed | **YES** | `:936–938` "The square root of their contribution to the trace is 26.0% of √Tr C". √0.0675 = 0.260, which agrees with values.tex (26.0% of √Tr, 6.75% of the trace). |
| R13 | fixed | **YES** | `main_paper.tex:129–131` "A candidate release package of about 16 MB [39], prepared locally but not yet deposited" |
| N1 | fixed | **YES** | `:435–436` "under the conventions stated in the analysis note [14]"; `:455–456` "The analysis note also states the further approximations and limits." The cite count is unchanged (64). |
| N2 | partly fixed; F9 kept for Joseph | **YES** | `:918–920` "We use the covariance only under an exception to the criteria, recorded in the analysis note and limited to this one covariance." "Limited to this one covariance" is kept. |
| N3 | fixed | **YES** | `:949–951` "they test the generator predictions as hypotheses and provide no new measurement uncertainty"; `:968–969` "conditional on six stated conditions and provide no new measurement uncertainty". No strengthening. |
| N4 | not applied (F4) | **YES** | Unchanged. The justification holds: defining the criteria needs their numbers (C1/C3). |
| N5 | not applied (F6) | **YES** | Unchanged; for Joseph. |
| N6 | fixed | **YES** | `main_paper.tex:140–141` "every figure number that it checks" |
| N7 | handled in the caption; legend is P10 | **YES** | See R11. The term is now defined where it appears. |
| F3 ruling | unchanged | **YES** | `:295–298` "from LightGBM unfoldings of three groups of run periods". |

##### Primer (review-primer.md: MATERIAL 2, MINOR 7, NOTE 4) plus the director's N1 instruction

| id | claimed | verified? | new text at 24ec59af |
|---|---|---|---|
| R1 (MAT) | fixed | **YES** | `primer_body.tex:475–476` "None of these studies changed the five-quantity central value or its quoted uncertainty." This is true and no longer contradicts the joint-test estimator. |
| R2 (MAT) | fixed | **YES** | `:131–143`, item 2: "…pass particular recovery checks. Other end-to-end tests show biases that are not included in their quoted uncertainty: the unfolding follows a changed simulated truth only partly, and the background removal leaves a bias in some cells. That uncertainty has not met the requirements we set in advance, and it is used only under a documented exception to them, so their error bars have not been shown to be right. The one direct test of whether such error bars contain the truth as often as stated, made on a variant of the method, failed. …" The body's three caveats are now attached to the claim. The base "does not certify their intervals" survives. No numeral is added, and nothing is stronger than the body: "a changed simulated truth" does not call the pattern generator-sized. |
| R3 | fixed | **YES** | `:272–273` "With the central value reproduced, and its error bars found close in size to the published ones," |
| R4 | fixed | **YES** | `:141–143` "…because the uncertainty depends measurably on the learner's random seed." This is the body's measured reason. |
| R5 | fixed | **YES** | `:164–166` "Relaxing the published cuts on the true muon's motion, with the same event selection, enlarges the population being estimated without adding measured events." |
| R6 | fixed | **YES** | `:155–156` "is rejected at a combined error level of five percent, both overall and in shape alone." |
| R7 | fixed | **YES** | `:120–121` "although a shape difference remains when judged with the published correlations between cells." |
| R8 | fixed | **YES** | `:579–581` "in regions where the detector records only a small fraction of the true events (low acceptance)" |
| R9 | fixed, with RD13 | **YES** | `:679–682` "The multi-quantity measurements are shown as central values only: their error bars have not been shown to be reliable, and end-to-end tests on simulation show biases that are not included in their quoted uncertainty." The added clause restates body l.428–444 and item 2. It is a caveat, not a claim. |
| R10 | fixed | **YES** | heading `:381` "Limits on the multi-quantity results"; both pointers updated (`:321–323`, `:349–350`). "cannot yet claim" no longer appears in the source or the PDF. |
| R11 | fixed | **YES** | `:487–489` "Here MEC (meson-exchange currents) labels GENIE with its model of the two-nucleon process added" |
| R12 | fixed | **YES** | `:457–459` "the bootstrap of the version of the method with the larger classifier". "Candidate" no longer appears in printed text. |
| R13 | fixed | **YES** | `:243–245` "We did run such a test on the statistical part of those error bars, using simulated repeats drawn from our own simulation against a fixed, known truth." |
| N1 (director) | fixed | **YES** | `:280–281` "Each richer measurement, when collapsed back down, agrees with the simpler one in overall normalization" |

##### Note (review-note.md: MATERIAL 2, MINOR 6, NOTE 5)

| id | claimed | verified? | new text at 24ec59af |
|---|---|---|---|
| M1 (MAT) | applied | **YES** | `sec_systematics.tex:310–314` "The block uses each period's unfolded result over that period's own simulated truth, with each period unfolded through its own simulated detector response. Because each period is compared with the exposure-weighted mean of the three, the block needs no reference period, and it does not identify which period is correct." Both points are checked against DESIGN: (b) §3 "Each period is unfolded with its own MC response"; (a) §2 "Reference: none", m = Σ e_X r_X. Every D5 element is present in the paragraph (list in §b). A causal-scope NOTE is **V2**. |
| M2 (MAT) | applied at 3 sites (director ruling) | **YES** | `main_note.tex:61–63` "Each passes marginal-normalization checks against the lower-dimensional result to ≈1–2 %."; `sec_execsummary.tex:37` "each passing marginal-normalization checks against the lower-dimensional result to ≈1–2 %"; `sec_summary.tex:23–26` "pass marginal-normalization checks against the lower-dimensional results to ≈1–2 %". The base defect in the summary is corrected under the marked ruling. |
| m1 | applied | **YES** | `sec_systematics.tex:349–352` (same two sentences as the paper). This matches the endpoint record and PLAN §1's family. See V6 on the rationale. |
| m2 | applied | **YES** | `sec_summary.tex:16–19` "The statistical band in use when the fixed-truth coverage test ran failed it in its tails." |
| m3 | applied | **YES** | `:120–123` "the split data/MC streams of the earlier, rebuilt bootstrap (labelled VL170 in the appendices) are in App. …. The fixed-truth coverage test (§…) found that the statistical band in use when it ran, before that rebuild, undercovered in its tails, unevenly across bins." The two bands are distinct again. |
| m4 | applied | **YES** | `sec_execsummary.tex:50` "but the estimator-seed sensitivity measured on two seed-varied companion covariances exceeds the limit fixed before production" |
| m5 | applied, own wording | **YES** | `:135` "Four measurements, led by …, limit every result built from the five-dimensional covariance in use (§…); no other corrected candidate is used in its place." This equals the base "not adopted". The fixer correctly rejected "not used for any quoted result". |
| m6 | applied | **YES** | `main_note.tex:79` "These tests are valid only under stated conditions." |
| N1 | applied for open rows 85, 91, 92 | **YES** | Five printed sites read "tracked in the analysis repository's known-issues log" (`sec_systematics.tex:31–32, 128–129, 232, 253–254`; `sec_validation.tex:294–295`). Each row number stays in a comment. The resolved rows are left for F-r2-2. See V5. |
| N2 | applied | **YES** | `main_note.tex:74–75` "Coverage and estimator-seed studies show further limitations." |
| N3 | applied | **YES** | `sec_validation.tex:291` "with a decision rule recorded before it ran" |
| N4 | applied | **YES** | `sec_execsummary.tex:100` "(the fraction within 2σ, C₂ = 0.912, vs. 0.954; …)" |
| N5 | not applied by the fixer (F-r2-1); director ruling F-r2-1 then applied in the commit | **YES** | paper `paper_body.tex:395–396` "The coverage of this block has not been tested, and the coverage of the total remains untested."; note `sec_systematics.tex:126–129` "…it has not been tested independently; the statistical block quoted here has not been tested at all."; `sec_summary.tex:19–20` "…and has not been tested independently; the statistical block quoted now has not been tested". This agrees with D2 ("S1 … has not been coverage-tested at all") and with the base exec summary's "has not been tested". The base's "independently" on S1 was the defect. V3 and V4 cover residual wording. |

**Totals: 48 rows verified YES and 0 NO.** That is 20 paper findings + W1, 13 primer findings + N1, and 13 note
findings. Including the F3 ruling row, there are 49 rows.

#### (b) New findings

##### V1 (MINOR): paper, run-period block, `paper_body.tex:364–367`
- **Base:** "Its reference-free double-ratio construction uses the periods' own simulated responses; it does not
  identify a correct period."
- **New:** "The block uses double ratios between groups, each group's unfolded result being taken over its own
  simulated truth, so it relies on the periods' own simulated responses.  It does not identify a correct period."
- **Problem:** The note's M1(b) defect survives here. "So" derives the use of each period's own response from the
  ratio's denominator, the period's own simulated *truth*. DESIGN §3 gives the own-response reliance as a separate
  fact: "Each period is unfolded with its own MC response". The R10 fix split the second clause but kept this "so".
  The note now states the two facts separately (`sec_systematics.tex:310–312`), so the two deliverables describe the
  construction differently.
- **Minimal fix:** "…each group's unfolded result being taken over its own simulated truth, and each group being
  unfolded through its own simulated detector response." No numeral is involved.

##### V2 (NOTE): note, run-period block, `sec_systematics.tex:313–314`
- **New:** "Because each period is compared with the exposure-weighted mean of the three, the block needs no
  reference period, and it does not identify which period is correct."
- **Problem:** "Because" can govern both clauses. The block then reads as failing to identify the correct period
  because of the mean comparison. In DESIGN §2 the order is the other way round: the data cannot tell which period is
  right, so the construction is reference-free. The paper's R10 fix separated exactly this attachment. The D5
  data-level statement survives separately at `:295–296` ("these data cannot establish which period, if any, is
  correct"), so nothing is lost.
- **Minimal fix:** "…the block needs no reference period. It does not identify which period is correct."

##### V3 (NOTE): note, `sec_systematics.tex:128–129` "has not been tested at all"
- **Problem:** D2 says "has not been *coverage*-tested at all". The same paragraph reports two checks of this block:
  the nested 150-vs-300 replica check (1.001) and the 0.26 σ centring. Bare "tested at all" is broader than D2. The
  context makes "coverage" the likely reading, and the base exec summary already uses a bare "has not been tested".
- **Minimal fix:** "has had no coverage test at all". The paper's "The coverage of this block has not been tested" is
  already precise.

##### V4 (NOTE): F-r2-1 not carried to two base sites
- **Sites:**
  - `paper_body.tex:981–982`: "the quoted two-dimensional statistical block awaits an independent coverage test";
  - `primer_body.tex:125–127`: "The quoted statistical error bars await an independent coverage test".
- **Problem:** Each carries the implicature the ruling removed elsewhere: that some non-independent test of S1
  exists. Neither site was edited in this round, and the primer body (`:253–254`, "They have not been tested") is
  correct.
- **For the director:** "awaits a coverage test" at both sites, or leave them as base text.

##### V5 (NOTE): note, `sec_systematics.tex:250–254`
- **Text:** "…is established by the code chain and by an exact test …; the identity is tracked in the analysis
  repository's known-issues log."
- **Problem:** Printed straight after "established", "the identity is tracked" can read as the identity itself being
  in doubt. KI-91 is open only for closure with the row owner.
- **Minimal fix:** "…and by an exact test …, and its open known-issues entry is tracked in the analysis repository's
  log."

##### V6 (NOTE): record-level only; the printed text is correct
- **(i) Wrong citation in fix-paper.md (reader-B).** It cites "`stageF/rebuild/REPORT.md` l.273" for "the 1.4%
  rank-1 normalization is in the universe block", but that file has 119 lines. The fact is in
  `stageC/production/DESIGN.md:273` ("Plus the 1.4% rank-1 normalization scaled to `E_U`"), so the caption
  "systematic-universe (including the normalization)" is right.
- **(ii) Rationale in fix-note.md (m1).** "A negative statement that gets wider is not a weakening" is backwards in
  logic. "Not validated simultaneously over F" is weaker for a larger F. The printed text is still faithful to the
  base, because the base's "simultaneous interval coverage" means PLAN §1's family. That family is 205 cells, their
  integral and 30 projections. "All reported bins and projections" leaves the integral implicit.

##### V7 (NOTE): primer, `primer_body.tex:588` and `:619` (reader edit RD11)
- **Base:** "Saved outputs now give a partial explanation"; "a saved-output diagnosis finds".
- **New:** "Our diagnosis of these studies gives …"; "a separate diagnosis finds".
- **Problem:** The rewrite drops that both diagnoses are retrospective analyses of stored outputs, with no new runs.
  The note's `sec_pet_campaigns.tex` keeps "saved-output diagnosis". The scope limits that follow ("at the size of the
  study's samples … remains unmeasured"; "without establishing a cause that holds in general") are intact, so this is
  provenance, not a caveat.
- **Minimal fix:** "A later analysis of the studies' stored outputs gives a partial explanation".

##### Item-2 checks against the base (no further finding)

- **Run-period block (note).** Every D5 element is present.
  - Must-carry, with the text that carries each:
    - unknown cause, not a measured systematic: `:287–289`;
    - covers 1G–1M p∥, with 1N–1P treated the same: `:290–297`;
    - added after the other blocks: `:300`;
    - its size: `:302–304`;
    - which period is right not established: `:295–296`, `:314`.
  - Required clause:
    - each period unfolded through its own simulated response: `:311–312`;
    - no reference period: `:313`;
    - does not identify the correct period: `:314`;
    - few groups, regularization shrinkage, retained statistical and training noise: `:314–316`;
    - containment is not evidence of coverage: `:317–318`.
  - "Its own check cannot fail": `:319–320`.
  - The comparison with the exposure-weighted mean of the three is stated twice (`:298`, `:313`), consistent with
    DESIGN §2.
- **Endpoint sentence (paper and note).**
  - It conveys that full validation is not achieved: none of intervals, bias or covariance is independently
    validated.
  - It names all three objects of DECISION-20261014 l.49–50. Nothing missing is narrowed.
  - It keeps the three absent inputs ("none is available" in the note), "We make no claim about coverage" and the
    GOF-indicative clause (note).
  - The package says so in both deliverables.
- **Marginal checks.** Every site is normalization-only:
  - paper: abstract, Intro, IV C ×2, Conclusions;
  - note: abstract, exec summary, summary;
  - primer: l.280.
- **Primer item 2 and takeaway.** They now carry the body's caveats. Neither is stronger than the body.
- **"Not tested" ruling.** It agrees with D2. The paper's version is exact; see V3 and V4 for the note and the
  remaining sites.
- **Reader-derived edits.** Reader-B, -D, -E and -U in the paper and RD1–RD13 in the primer were each checked against
  the base. None loses a limitation or adds a claim, apart from the provenance point in V7.
- **Numbers.** No numeral, macro, cite, ref or label changed in this round (invariance re-run).

#### (c) Cross-deliverable agreement at the fix-round sites

| fact | paper | note | primer | agree? |
|---|---|---|---|---|
| Endpoint sentence | `paper_body.tex:438–439` "The result's intervals, bias and covariance have not been independently validated." | `sec_systematics.tex:349–350`, identical | (no endpoint sentence; l.209–226 "No coverage claim") | **YES**, word for word |
| Coverage gloss | `:440–443` "…on independent simulated samples, nor simultaneously over all reported bins and projections." | `:350–352`, identical | P4: "cannot establish coverage across independently generated samples" | **YES** |
| Generator significance | "provides no calibrated significance for generator comparisons" | "gives no calibrated significance for comparisons with generator predictions" | — | **YES** (verb only) |
| Marginal checks | "marginal normalizations" / "agree in normalization" | "marginal-normalization checks … ≈1–2 %" ×3 | "agrees … in overall normalization" | **YES** |
| Run-period block | three groups, no reference, 2.1 / 1.2–3.4 / 2.0 %, limits, containment not coverage, check not a test; "so it relies on the periods' own simulated responses" | same content at 2.14 / 1.24–3.36 / 1.97 %; own response stated as its own fact; exposure-weighted mean | — | **Substance YES; wording differs on the own-response link (V1)** |
| Quoted stat block untested (F-r2-1) | "The coverage of this block has not been tested" (`:395`), but the Conclusions say "awaits an independent coverage test" (`:982`) | "has not been tested at all" / "has not been tested" | "They have not been tested" (`:253`), but item 1 says "await an independent coverage test" (`:125`) | **Substance YES; residual wording V3, V4** |

#### (d) PDF spot-check (builds/r2, sources byte-identical to 24ec59af)

- **Comment junctions.** I checked every fix-round comment insertion that falls inside a paragraph (61 junctions)
  for continuous text across the comment in `pdftotext` output:
  - 48 passed automatically;
  - the 13 macro-heavy or false-negative ones were checked by hand (Fig. 1 caption; `[14]`; `q3`; the 26% line; the
    Fig. 5 caption; the note abstract's ≈1–2 %; "(Sec. VI B). Two of them"; "50–100 GeV samples; the GiBUU";
    "closure studies. A"; "covariance's trace. Their"; primer items 1, 6 and the N1 sentence).

  **No words are swallowed and no junction runs together.** This includes `sec_summary.tex:16–19`, where two comment
  lines sit mid-sentence: the PDF reads "…test ran failed it in its tails."
- **MATERIAL sites, full sentences found verbatim in the PDF text** (allowing for line-break hyphenation and running
  page numbers):
  - paper R1 (all three), R2/W1 (the endpoint block), R3 (both sites), F-r2-1;
  - primer R1, R2 (the whole of item 2), R9/RD13;
  - note M1 (both sentences), M2 (all three sites), m1, F-r2-1 (systematics and summary), m2, m3.
- **Other fix sites**, also present in the PDF:
  - paper: R4–R13, N1–N3, N6;
  - primer: R3, R5, R6, R8, R10–R13, RD-edits;
  - note: m4–m6, N1–N4.
- **Stale strings.** "cannot yet claim" does not appear in the primer PDF.

#### Counts

- Findings verified: **48 YES, 0 NO.** That is the 46 review findings plus the paper W1 and primer N1 director items.
  The F3 ruling row is also YES.
- New findings: **MATERIAL 0, MINOR 1 (V1), NOTE 6 (V2–V7).**
