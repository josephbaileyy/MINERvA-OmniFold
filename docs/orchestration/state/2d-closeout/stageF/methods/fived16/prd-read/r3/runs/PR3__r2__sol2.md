A: VERDICT: SHORTEN
SHORTER-FORM: We report a simultaneous measurement of the ν_μ charged-current inclusive cross section in five observables: muon transverse and longitudinal momenta, available hadronic energy, three-momentum transfer and hadronic invariant mass. MINERvA medium-energy open data are unfolded without binning using OmniFold and reported in sixteen cells with a covariance and a median per-cell uncertainty of 7.29%. Three external generator predictions give χ² values of 109–272 for 16 degrees of freedom; GiBUU gives 58 on 8 cells. Interval coverage has not been validated. In fake-data studies, the reported uncertainties do not cover the estimator’s bias at GiBUU-like truths or a synthetic q_3 tilt. Weakening flux correlations by 10% reduces the sixteen-cell χ² values by 24–48%. The unfolding reproduces the published muon-kinematic integral within about 1%, with a correlated shape difference. Validation studies show partial recovery of generator-sized truth changes. Simulation-calibrated hybrid-null tests reject five generator predictions at the 5% familywise level, with no evidence of gain over matched coarse projections.
LENGTH: ACCEPTABLE
REASON: The measurement leads appropriately, but fewer subsidiary validation details would make the abstract easier to follow.
<!-- absence-ok: verbatim rater output quoting or proposing the paper's printed limitation text; added by the lane so the record can be committed; not a claim of the lane -->

B: VERDICT: SHORTEN
SHORTER-FORM: This note documents simultaneous unbinned unfolding of MINERvA medium-energy ν_μ charged-current inclusive open data with OmniFold and its validation. It presents a sixteen-cell cross section in muon transverse and longitudinal momenta, available energy, three-momentum transfer and hadronic invariant mass, with a covariance and a median per-cell uncertainty of 7.29%. Interval coverage has not been validated; fake-data studies find biases exceeding the reported uncertainties at GiBUU-like truths and a synthetic q_3 tilt. Generator comparisons are sensitive to flux correlations. The note also documents reproduction of the published muon-kinematic cross section, three- and four-observable central values, and an earlier purity-subtracted five-observable result on a finer grid. The earlier covariance fails its specified acceptance criteria, and its quoted uncertainties omit background and regularization biases. Validation studies show that negative-weight subtraction removes most of the purity method’s background bias, generator-sized truth changes are only partly recovered, and statistical intervals from a deterministic purity-subtracted variant miscover at the tested truths. No tested reporting definition meets the predeclared 10% precision criterion. Simulation-calibrated joint tests reject hybrid null hypotheses for five generator predictions at a 5% familywise error rate. These tests are not physical exclusions, show no evidence of discrimination beyond matched coarse projections, omit calorimetric recoil-response uncertainty and assume convergence of the fine grid defining the null hypotheses. NuWro’s total-test rejection is not robust to a hydrocarbon-target correction.
LENGTH: TOO-LONG
REASON: Although substantially improved over the OLD abstract, the NEW version still reads as a catalogue of results and qualifications rather than a concise technical-note abstract.
<!-- absence-ok: verbatim rater output quoting or proposing the paper's printed limitation text; added by the lane so the record can be committed; not a claim of the lane -->

C: BEST: T1
REASON: T1 foregrounds the measurement, identifies the process and target, and conveys the five-observable scope without the exhaustive list in T2 or the methodological emphasis in T3.

P01: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: The revision establishes the principal measurement immediately and gives the reproduction and intermediate results their appropriate supporting roles.

P02: VERDICT: SHORTEN
SHORTER-FORM: The validation studies assess the result through the two-dimensional reproduction, background-subtraction tests, recovery of generator-sized truth changes, a coverage test and a fake-data study of estimator bias. They examine whether the unfolding gives reliable multidimensional cross sections when the simulated truth differs by generator-sized amounts.
REASON: The revised emphasis is appropriate, but “show how far the result can be trusted” is less precise and formal than the surrounding measurement language.

P03: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: The opening makes the principal qualifications prominent, while the revised table identifies relevant estimators without requiring readers to track retired configuration labels.

P04: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: Removing this categorical framing suits the measurement-led presentation because the specific coverage and bias qualifications remain explicit elsewhere.

P05: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: The revision clearly distinguishes the reported measurement from its supporting validation and generator tests.

P06: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: “Both estimators” directly matches the revised presentation and avoids suggesting a larger configuration catalogue.

P07: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: The estimator is now identifiable from the sentence itself rather than through combinations of obsolete configuration labels.

P08: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: The revision clearly assigns the reported results to an estimator and provides a concise pointer to its development history.

P09: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: The reduced table gives readers the estimator definitions and result assignments needed for the paper while directing development details to the note.

P10: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: These detailed comparisons among development variants fit the companion note better than the measurement narrative.

P11: VERDICT: SHORTEN
SHORTER-FORM: The distance depends on the estimator (Ref. [14], Sec. 6.4). LightGBM was selected after its comparison and the exact-split learner’s comparison with the publication were known, so this benchmark is a reproduction rather than an independent validation. With purity-based subtraction, the exact-split result differs from the central value by a per-bin median of 1.03% (maximum 17.6%); estimator details are given in Ref. [14], Sec. 3.2.
REASON: The selection qualification belongs in the paper, but the NEW opening sentence is cumbersome and its final reference should identify its purpose more clearly.

P12: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: The revision separates checks of the reported estimators from earlier studies and retains the background-bias finding in understandable terms.

P13: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: Removing the retired configuration label preserves the sentence’s meaning and improves continuity.

P14: VERDICT: SHORTEN
SHORTER-FORM: When the true shape is reweighted by the GiBUU-to-GENIE ratio, the (E_avail,W) cells unfolded with a development variant of the joint-test estimator using 100 trees and 8 leaves for refinement deviate from it by several percent in the largest cells and by up to 74% in the cell 0.8≤E_avail<1.5 GeV, W≥3 GeV.
REASON: Identifying the development variant is useful, but the relative clause and repeated high-W description can be tightened.

P15: VERDICT: SHORTEN
SHORTER-FORM: We interpret this residual as regularization bias because it persists over the tested iteration numbers and classifier capacities: in noise-free studies of that variant, thirty iterations reduce the E_avail residual by 26%, while a larger classifier improves the reconstruction-level fit without reducing the residual. For other fixed generator shapes, the joint-test estimator’s residual is 16–31% in the most affected (E_avail,W) cell and lies within the quoted total uncertainty in about half of those cells. These uncertainties come from the covariance of an earlier purity-subtracted five-observable result, which fails its specified acceptance criteria (Ref. [14], Sec. 9.6).
REASON: The added attribution is valuable, but the NEW version overloads its final sentence and awkwardly identifies an uncertainty with a covariance.

P16: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: Naming the estimator and subtraction method makes the coverage statement intelligible without the removed configuration table.

P17: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: The caption concisely identifies the common learner, differing background treatments and pseudo-experiment counts.

P18: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: The added descriptions let the caption identify both estimators and the uncertainty band without relying on retired labels.

P19: VERDICT: SHORTEN
SHORTER-FORM: Error bars are the standard error of the mean. [figure] Caption: Empirical coverage of statistical intervals for the 153 reported cell and projection integrals, corrected for nominal-truth bias. The study uses a deterministic LightGBM estimator with purity-based subtraction and 400 pseudo-experiments at a truth with an approximately 10% lower signal rate and a weak E_avail slope (Sec. V C).
REASON: Splitting the caption removes the repeated “with” constructions and makes the estimator and test conditions easier to parse.

P20: VERDICT: SHORTEN
SHORTER-FORM: The integrals are ordered as the (E_avail,W) projection (cells 0–41 and their sum), the 109 coarse joint cells (labelled by their index in the 3^5 grid), and the total. [Estimator stability] Rounding-level input changes shift the joint-test estimator’s results by up to 2.6 statistical standard deviations (2.5 for its lower-capacity development variant), exceeding data-stability limits of 0.3 (median) and 1.0 (maximum). This spread lies within the data-bootstrap statistical uncertainty but limits the reproducibility of the central values. The earlier purity-subtracted five-observable covariance, its status and its seed studies are documented in Ref. [14], Sec. 9.6.
REASON: Moving the earlier covariance discussion is appropriate, and the retained stability finding reads more clearly without the long causal sentence.

P21: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: Replacing the configuration label with the estimator’s name makes the measurement introduction self-contained.

P22: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: The terminology now identifies the relevant estimator consistently with the revised methods section.

P23: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: The revision states the scope of the descriptive comparisons directly and removes dependence on retired labels.

P24: VERDICT: SHORTEN
SHORTER-FORM: The earlier purity-subtracted five-observable (E_avail,W) map and its generator comparisons are given in the companion note [14].
REASON: A concise pointer suits the revised scope, but unresolved reference and section placeholders are unsuitable for publication.

P25: VERDICT: SHORTEN
SHORTER-FORM: [Discussion and conclusions] The principal result is the sixteen-cell cross section of Sec. V F, with its covariance and generator comparison; Table I summarizes the validation findings.
REASON: The measurement should lead the conclusion, but “show how far it can be trusted” is imprecise and unnecessary.

P26: VERDICT: ACCEPT
SHORTER-FORM: -
REASON: The revision clearly limits this statement to the retained intermediate central values while the principal measurement’s qualifications are stated separately.

END