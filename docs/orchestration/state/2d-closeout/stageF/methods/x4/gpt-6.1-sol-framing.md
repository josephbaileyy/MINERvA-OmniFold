## Part 1 — The central contribution

The contribution is a quantitative case study of applying OmniFold to MINERvA open neutrino data, showing what an implementation can reproduce, where its unfolding and uncertainty construction fail, and how a biased estimator can still serve as a statistic for explicitly simulated hypothesis tests. Its strongest results are the two-observable benchmark; the reduction of background-treatment bias; the substantial residual bias under generator-sized truth deformations; the failed coverage test; and the failure of the tested reporting definitions to meet the chosen precision target. The conditional generator tests illustrate full-chain calibration, but their claimed familywise error control still requires statistical justification, independently of whether the hypotheses are physically comprehensive. **[inference: editorial assessment]** This is a plausible but presently incomplete PRD methods paper: quantitative validation figures, a defensible Monte Carlo decision procedure, and a usable release would strengthen it without new physics results; its reach is capped by being one implementation on one dataset, with neither validated higher-dimensional measurement uncertainties nor demonstrated additional discrimination from the joint information.

## Part 2 — Titles and outline

Possible titles:

1. **Performance and limitations of multidimensional OmniFold unfolding with MINERvA open data**
2. **Multidimensional neutrino unfolding with OmniFold: validation and conditional hypothesis tests**
3. **Bias, uncertainty, and conditional inference in an OmniFold analysis of MINERvA data**

The first best reflects what the existing evidence establishes. The second becomes stronger once the test-calibration issues are resolved.

Throughout the paper, distinguish three categories explicitly:

- **Observed outputs:** quantities obtained from data using a specified estimator.
- **Demonstrated properties:** performance on specified simulated truths, responses, and ensembles.
- **Interpretive assumptions:** conditions needed to connect those demonstrations to data or generator predictions.

### I. Introduction and scope

**Main point:** This study evaluates an implementation of multidimensional unfolding and conditional inference, rather than delivering a validated five-observable cross-section measurement.

Use the existing motivation, the distinction from the cited simulated-neutrino application, and the three tasks: benchmark, diagnose unfolding performance, and demonstrate conditional tests. Do not assert priority beyond the manuscript’s stated knowledge.

Introduce the central negative findings immediately, without reproducing every number. Explain that calibration of a test and coverage of unfolded intervals are different requirements.

**New presentation:** A compact “claims and evidence” table, with rows for the two-observable benchmark, higher-dimensional central values, interval coverage, and conditional tests. Columns should identify the estimator, evidence, and permissible interpretation. This is an organizational table, requiring no new result.

Place the scope paragraph from Part 3 here.

### II. Data, observables, and reporting domains

**Main point:** The analysis uses a fixed selected dataset and five simultaneous observables whose reconstructed inputs overlap.

Include:

- Twelve run periods, \(1.057\times10^{21}\) protons on target, mean neutrino energy near 6 GeV.
- 4.12 million selected data events and 32.8 million simulated **true signal** events; keep those sample descriptions distinct.
- GENIE 2.12.6 with MINERvA Tune v1 as the analysis simulation.
- Explicit truth and reconstructed observable definitions, including the implemented charged-pion subtraction.
- Fixed event selection as features are added.
- Generator versions, CH versus carbon targets, corrected flux sampling, and GiBUU’s approximately 20 GeV endpoint.
- The fine analysis grid, coarse test grid, supported-cell masks, and restricted GiBUU domain.

The supplied text does not contain all signal, fiducial, reconstructed-variable, and mass-convention details requested by the referee. Those must be supplied from the actual implementation; the recast should not invent them.

**Prose to table:** An observable-definition table listing truth definition, reconstructed definition, shared inputs, and convention issues. A second table should list generator target, energy coverage, flux treatment, and test domain.

**Prose to figure:** Show the supported reporting domain or its projections using the existing masks. Plot occupancy or support, rather than implying that five named variables provide five independent constraints.

### III. Estimators and validation design

**Main point:** Different results use different estimator configurations, and each validation applies to the configuration actually tested.

Describe the five-iteration OmniFold procedure, flux and target normalization, regularization through iteration count and classifier capacity, and both background treatments.

Make the estimator distinctions unavoidable:

- LightGBM central-value estimator with purity subtraction.
- Exact-split cross-check.
- Deterministic variants used for particular validation studies.
- Joint-test estimator with unbinned background refinement.

Do not merge results from these configurations into a single performance claim.

Include the neural-network cross-check: 0.8% change in the three-observable integral and median projection differences of 0.7–1.4%.

**Prose to table:** An estimator matrix showing learner, stochastic settings, background treatment, refinement configuration, and associated results. Include numerical configuration details presently deferred to the analysis note.

**Prose to table:** A validation-design table specifying each injected truth change, whether backgrounds are included, whether the response changes, the reported domain, and the acceptance criterion. Where the manuscript does not supply the criterion, identify it as information to add.

### IV. Two-observable benchmark

**Main point:** The implementation closely reproduces the published normalization and many bins, while retaining a correlated difference and learner dependence.

Retain Fig. 1, with clearer terminology:

- \(3.073\) versus \(3.039\times10^{-38}\ {\rm cm}^{2}/{\rm nucleon}\).
- Integral ratio 1.011.
- 95.6% of 205 bins within 10%.
- Published-uncertainty-standardized residual RMS 0.564.
- Published-covariance-weighted distance divided by the stated ndf: 2.65.

Call the last quantity a descriptive distance, without a compatibility significance.

Show the exact-split alternative and disclose once that the LightGBM central value was chosen after both comparisons were known, to match the covariance estimator. Include the 0.98% median and 12.2% maximum per-bin learner difference, and the reported distance ranges.

**Prose to table or figure:** Compare the LightGBM and exact-split outputs and their distances. The existing ten-seed LightGBM range, 2.64–2.75, can be displayed without implying a measured exact-split seed distribution.

Keep the benchmark distinct from validation of uncertainty coverage.

### V. Bias and coverage in higher-dimensional unfolding

**Main point:** Selected consistency and closure checks succeed, but they coexist with substantial bias and failed coverage for other tested configurations and truths.

This should be the scientific center of the methods paper.

Include:

- Approximately 1–2% agreement of marginal normalizations.
- Three- and four-observable injected-distortion closure, identifying the actual distortions and criteria.
- Up to 4% nominal-truth background-treatment bias in highest-\(W\) cells.
- Reduction below 0.3% in the reported comparison, with residuals up to 1% in some joint cells.
- Data differences between background treatments of at most 1.4%.
- Generator-sized \(E_{\rm avail}\) deformation: several-percent residuals in large cells and up to 74% at high \(W\).
- Other tested generator shapes: 16–31% residuals in the most affected cell.
- Coverage study: 400 pseudo-experiments per truth; 51 of 153 reported quantities confidently below nominal 68% coverage under the tilt, with coverage as low as 0.06; 42 failures at 95%; two nominal-truth failures at 95%, lowest 0.85.
- Rounding-level sensitivity, with the estimator-specific qualifications already stated.

**Essential new figures from existing results:**

1. **Background-treatment comparison:** fractional unfolded-minus-truth residual by \((E_{\rm avail},W)\) cell, comparing purity subtraction and refinement under matched tested conditions.
2. **Deformation recovery:** injected truth change and recovered change, or fractional recovery residual, by cell. Show nominal and generator-sized deformation separately.
3. **Coverage:** empirical coverage for each of the 153 quantities, with nominal levels and binomial uncertainty intervals; separate cells from projection integrals and separate tested truths.

These should replace long prose accounts of the most consequential failures. If matched estimator comparisons are unavailable, show separate panels with explicit configuration labels.

### VI. What the uncertainty studies establish

**Main point:** The existing ensembles quantify specified variations, but do not constitute validated total uncertainty intervals.

Separate the two-observable budget from the five-observable study.

For two observables, include:

- Four covariance components.
- Median total relative uncertainty 6.45%; integral uncertainty 4.75%.
- Published values 6.85% and 4.61%.
- Systematic-universe median variance share 87%.
- Median statistical uncertainty 0.684%.
- Median training-seed uncertainty 0.06%, estimated from five seeds.
- Run-period component: median 2.1%, integral 2.0%.
- The approximately 7% run-period step.
- Unresolved flux-uncertainty difference and approximation for failed-reconstruction events.

For five observables, include:

- Seed sensitivity of the projected uncertainty, reported as 6.145% against the chosen 5% criterion, after defining the quantity mathematically.
- Its observed behavior over 40–160 throws and the limitations of one seed pair.
- The fixed-seed bands, with the trace expression corrected.
- The tested reporting-definition study and its chosen precision target.
- Median deformation-envelope size of 13.4% for the 39-cell fallback, and approximately 10–13% across considered definitions.

Rename “bounded model dependence” as an **envelope over the five tested truth deformations**, unless an actual broader bound is demonstrated.

**Prose to figures or tables:**

- Covariance-component table defining ensemble, estimand, normalization, and omissions.
- Run-period double-ratio plot versus \(p_\parallel\), showing the step.
- Projected uncertainty movement versus ensemble size, with the fixed-seed resampling comparison.
- Reporting-definition table showing supported-cell count, deformation-envelope median, and target outcome for each definition actually studied.

The conclusion is failure of the tested configurations to meet a chosen target, not a general precision limit.

### VII. Data outputs as illustrations

**Main point:** The higher-dimensional central values illustrate estimator behavior and descriptive comparisons, without assigning physical significance.

Retain Fig. 2 as the principal joint illustration. Retain Fig. 3 only if it helps explain the conditional-test benchmarks; otherwise move it to supplemental material.

Useful existing quantities include the central-value ratios, the concentration of cell-integrated differences, and the importance of the widest overflow cell. Keep their reference model explicit.

The 52% gap-filling statement, selected pion-FSI variations, low-recoil comparison with a different truth definition, and GiBUU tail substitution are secondary. They can be shortened or moved to supplemental material.

**Prose to table:** Show the overflow contributions and domain used for each quoted integrated ratio. Do not describe the map as locating a missing interaction mechanism.

### VIII. Conditional hypothesis tests

**Main point:** Full-chain simulation provides a route to testing specified ensembles with a biased estimator, but the test hypothesis, nuisance construction, and Monte Carlo decision rule must be defined precisely.

Organize this section in the following order:

1. Actual simulated hypotheses, including the exact Tune v1 case and external hybrid cases.
2. Generative description of nuisance draws and pseudo-data.
3. Statistic and fixed metric.
4. Monte Carlo calibration and multiplicity procedure.
5. Validation of the resulting decision rule.
6. Conditional data results.
7. Sensitivity checks and projection comparisons.

Use the 194 pilot pseudo-experiments, 109 supported cells, 72-cell GiBUU domain, noncentralities 318–6344, Table I, and Fig. 4.

The reported ten rejections should remain conditional **and** statistically provisional until the sequential-calibration concern is resolved. Changing the physics framing cannot establish familywise control.

**Prose to figures or tables:**

- Generative-model table distinguishing truth, response, background, prior, and nuisance variation.
- Fine-grid refinement comparison: changes in the unfolded result and reported norm ratios 0.50–0.86. Label the extrapolation as assumed.
- Matched-projection table: joint, muon, and hadronic-projection results on their actual domains, with multiplicity treatment explicit.
- Power table with denominators and uncertainty intervals; reconcile recovered pseudo-experiments before finalizing it.
- Sensitivity table distinguishing data-only recoil scaling, prescribed grid-direction shifts, and genuine recalibration.

Revise Fig. 4 to identify the displayed shift mathematically. State whether it is the distribution used for the conservative tail decision; largest median and largest tail probability are different selections.

### IX. Discussion, conclusions, and reproducibility

**Main point:** The transferable result is a set of demonstrated implementation behaviors and validation requirements, with clearly bounded claims.

State separately what worked, what failed, and what remains untested. Do not repeat the entire scope paragraph.

Provide current machine-readable outputs, configurations, masks, validation results, and test-replay inputs. Distinguish numerical replay from event-level reproduction, replace the obsolete two-observable release input, and resolve the deposit and funding placeholders.

## Part 3 — Scope statement and treatment of caveats

### Proposed scope paragraph

> This paper studies a specified OmniFold implementation on MINERvA open data. Higher-dimensional central values are estimator outputs under the implemented observable definitions, simulation response, background treatment, and regularization; they have no validated total interval coverage. Generator comparisons test the explicitly simulated ensembles: external predictions are represented on a finite truth grid with Tune v1 conditional shapes within cells, whereas Tune v1 itself has no such hybridization. Calibration draws the stated nuisance distributions, rather than establishing uniform validity over fixed nuisance configurations. The detector model includes the implemented variations but no calorimetric recoil-response band. The analysis also retains the stated target, flux-support, finite-simulation, and prediction-sample conventions. Grid convergence and equivalence of calibration to the data-analysis procedure have not been established. Any rejection claim requires a statistically justified Monte Carlo decision rule and applies to these ensembles; it does not establish a physical generator exclusion or a validated cross-section uncertainty.

This is approximately 150 words. It deliberately does not resolve the unclear role of interaction-model variations by asserting that the truth remains fixed.

### Which caveats can be centralized?

| Existing caveat | Treatment in the recast |
|---|---|
| Higher-dimensional results are central values only; no validated total coverage or covariance-based generator significance | **Centralize**, then put a short status label in relevant captions and release metadata. Readers encountering a figure alone need its status. |
| Response restricted to its parametrized family; missing calorimetric recoil-response uncertainty | **Centralize**, but retain beside the conditional-test result and recoil sensitivity study because it directly limits their interpretation. |
| External hypotheses retain Tune v1 within-cell shapes | **Centralize**, but retain in the mathematical hypothesis definition and table labels. It identifies what is tested. |
| Grid convergence unshown; residual potentially material | **Retain at the refinement study.** This is an observed methodological limitation, not merely a global disclaimer. |
| Geometric extrapolation lacks a recorded calculation | **Retain at the shift prescription.** Its evidential status must be visible where it enters decisions. |
| Shift scan follows only one direction | **Retain at the robustness claim.** Otherwise “robust” invites an unsupported multidirectional interpretation. |
| Nuisance draws and clipped negative interaction weights | **Centralize assumptions; retain implementation details in the generative model.** Their effect on the null must be defined. |
| Half simulation in pseudo-experiments versus full simulation for data | **Retain at calibration validation.** A mean shift is not automatically a bound on tail-probability differences. |
| Finite prediction samples enter metric and calibration | **Centralize convention; explain locally once.** Readers need to understand the construction. |
| GiBUU energy endpoint and migration from outside its test domain | **Retain at GiBUU results and domain definition.** This is prediction-specific. |
| Carbon versus CH targets | **Retain at affected comparisons.** It cannot disappear into a generic simulation caveat. |
| Five reconstructed inputs share hadronic information | **Retain in observable definitions.** Avoid any later claim of five independent constraints. |
| Charged-pion 135 MeV convention; measured migration effect not compared with full covariance | **Retain at the definition and sensitivity result.** It defines the published quantity. |
| Different \(E_{\rm avail}\) definition in the low-recoil publication | **Retain if that comparison stays.** The quoted proximity is not a quantitative equivalence test. |
| Same-data two-observable benchmark; missing cross-covariance | **Retain at Fig. 1 and its distance statistic.** It prevents a false compatibility test. |
| Learner dependence omitted from covariance; central-value choice made after inspection | **Retain once in the benchmark.** This materially qualifies the benchmark and budget. |
| Unknown run-period discrepancy; empirical covariance contains variation by construction | **Retain with the run-period result.** Construction is not validation of coverage. |
| Small training-seed ensemble and uncertain seed variance | **Retain in uncertainty table.** It concerns precision of that estimate. |
| Failed-reconstruction approximation tested in only two universes; unresolved flux difference | **Retain in uncertainty assessment**, with detailed diagnostic history in supplemental material. |
| Bootstrap mean offset omitted; quoted statistical block untested | **Retain with that covariance.** These describe its actual interpretation. |
| Earlier band failed; rescored rebuilt band is post hoc and partly circular | **Retain in the coverage account**, preferably a compact table; do not present rescoring as independent validation. |
| Background bias omitted from quoted uncertainty | **Retain at the bias figure.** It is a quantitative result. |
| Generator-sized regularization bias omitted from quoted uncertainty | **Retain at the deformation and uncertainty results.** This is central evidence. |
| Rounding-level sensitivity | **Retain with reproducibility and estimator stability.** Preserve which configuration was tested. |
| Covariance seed dependence; one seed pair; nested ensembles; fixed-seed bands | **Retain with the covariance-stability result.** These delimit that demonstration. |
| Precision study restricted by rules and computing budget | **Retain at the target outcome.** It prevents a universal impossibility claim. |
| Selected pion-FSI variations only; 52% gap filling is descriptive | **Retain if those statements remain.** Neither establishes a mechanism measurement. |
| Overflow dominance, model reference, no response-mismatch closure, large local bias | **Retain at the joint map.** They bear directly on apparent localization. |
| GiBUU tail supplemented from other generators | **Retain at that illustration**, or remove the illustration. It introduces an additional modelling assumption. |
| Other MINERvA selections do not provide independent confirmation | **Remove the confirmation framing**; retain a short distinction only if those comparisons remain. |
| Design informed by residuals; budget extension with visible p values; later studies post hoc | **Retain once in test-design provenance.** Statistical validity must then be addressed, not inferred from disclosure. |
| Arithmetic recomputation does not validate the ensemble | **State once in calibration validation.** |
| No demonstrated gain over coarse projections; no regional or mechanism attribution | **Retain in results and conclusion.** These are substantive limits of the contribution. |
| Release is partial, local, and contains an obsolete curve | **Resolve before submission.** These are publication defects, not enduring scope assumptions. |

## Part 4 — Proposed abstract

> We study the performance and limitations of OmniFold unfolding using MINERvA open data for medium-energy inclusive muon-neutrino charged-current interactions. A two-observable implementation reproduces the published integrated cross section within about one percent, with 95.6% of reported bins agreeing within 10%. Extending the estimator to five simultaneous observables preserves marginal normalizations but exposes background-treatment and regularization biases. Unbinned background refinement reduces the tested subtraction bias, while generator-sized truth deformations produce substantial residual bias and a tested statistical interval construction fails coverage. An envelope over selected truth deformations exceeds the chosen precision target for the reporting definitions studied. We also construct full-chain pseudo-experiment comparisons of explicitly defined generator-based hybrid hypotheses. These comparisons illustrate conditional inference with a biased estimator, subject to the implemented nuisance ensemble and Monte Carlo calibration requirements. They provide neither validated higher-dimensional measurement uncertainties nor physical generator exclusions, and additional discrimination from the joint observables is not demonstrated.

*148 words.*

This abstract intentionally omits the claimed 5% familywise rejection result until its statistical justification is completed.

## Part 5 — Disposition of the twelve major comments

Some comments contain both a framing issue and a substantive requirement. The classifications below identify the minimum needed for this methods paper.

| Comment | Disposition | Required response |
|---|---|---|
| **1. Primary result and aligned claims** | **(a)** | Make implementation performance and conditional inference the primary contribution. Relabel higher-dimensional products as estimator outputs and revise titles, captions, abstract, conclusion, and release accordingly. |
| **2. Missing calorimetric response** | **(a)** for the conditional demonstration; **(c)** for physical exclusions | Explicitly define the implemented-response scope. Retain ±4% scaling only as a data-output sensitivity check. A defensible response model propagated through calibration belongs to the later physics paper unless robustness to response uncertainty becomes a methods claim here. |
| **3. Hybrid hypotheses** | **(a)** if retained literally; **(c)** for transfer to physical generators | Test and name the hybrid hypotheses throughout. Separate Tune v1. Remove any suggestion that the directional scan bounds arbitrary within-cell residuals. Further refinement or independent-generator response studies are needed to claim equivalence to the generators themselves. |
| **4. Familywise error control** | **(b), essential** | Supply a valid sequential argument or recompute with a defensible calibration design. Concretely, use an independently fixed-size ensemble with an appropriate finite-simulation construction, or implement a sequential method with proven error control. Address the budget extension, repeated looks, ranking, ties, stopping counts, and multiplicity together. Validate or justify the final decision rule, rather than only its arithmetic. |
| **5. Interaction-model variations under a fixed null** | **(b), essential** | Audit what every variation changes: generated truth, conditional response, background, prior, or analysis weights. Write the generative model. If truth changes, redefine the null as the actual mixture or family and check that calibration implements it. If fixed truth was intended but not maintained, recalibration may be required. Specify correlations, clipping, and normalization treatment. |
| **6. Fidelity of full-chain calibration** | **(b), essential** | Establish pilot/production independence and whether the metric is fixed or regenerated in the claimed repeated experiment. Check rejection behavior using null datasets processed like data, including simulation-size effects and event reuse. Examine statistic distributions and tails, not only mean shifts. Quantify the lateral surrogate’s adequacy, or narrow the demonstration explicitly to the surrogate-defined ensemble. |
| **7. Higher-dimensional recovery** | **(b)** for presentation and audit; **(c)** for a validated measurement | Produce the compact closure and coverage figures from existing outputs. State deformations, configurations, domains, and criteria. No additional successful closure is required to publish documented failure, but the paper must establish exactly what failed. New bias reduction and validated total intervals belong to the later measurement. |
| **8. Definitions and information content** | **(b)** | Supply explicit definitions, mass conventions, relationships, and support masks. Verify identical observable implementation across predictions. Keeping 135 MeV is possible for a clearly named implementation study, but it requires exact consistency; correcting it requires propagating the change through affected outputs. A new demonstration of independent information is unnecessary if no such claim is made. |
| **9. Two-dimensional benchmark and run periods** | **(b)**, with some **(a)** | Reframe the covariance quantity as a distance and show the learner alternative. Present the run-period discrepancy and perform basic checks of exposure, selection, response, and normalization bookkeeping. A complete physical explanation can remain unresolved for a case study; calling the empirical term a validated systematic model cannot. |
| **10. Meaning of uncertainty** | **(b)** | Define each ensemble and estimand, explain overlap handling, and mathematically distinguish central-value seed variation from seed dependence of estimated uncertainty. Report the five-deformation envelope as such. Re-express the precision-target result within tested configurations. Full total-interval validation is deferred to **(c)**. |
| **11. Descriptive physics overinterpretation** | **(a)** through removal or narrowing; **(b)/(c)** if stronger claims retained | Remove mechanism attribution and physical localization claims. Define the 52% denominator if retained. Label carbon/CH and GiBUU-tail conventions explicitly; without a quantitative target correction, do not attribute their differences solely to interaction modelling. Physical generator conclusions require the later work. |
| **12. Article and release readiness** | **(b), essential** | Move essential definitions and validation prescriptions into the article. Deposit the current replay package, replace obsolete inputs, include masks/configurations and validation evidence, identify additional reproduction dependencies, and remove placeholders. Demonstrate what the deposited package actually reproduces. |

The recast therefore answers several physics objections by narrowing the object of study. It does **not** answer comments 4–6 by terminology alone.

## Part 6 — Before the authors start

**Do not build the revised paper around “all generators rejected.”** Build it around the evidence that marginal agreement and selected closure success can coexist with serious deformation-recovery and coverage failures. The conditional tests then illustrate a separate inference strategy; they do not repair the unfolded intervals.

Resolve the statistical specification before extensive rewriting. The manuscript currently moves between a fixed truth, nuisance-randomized pseudo-experiments, and an assertion of exact Monte Carlo validity. Those statements need one coherent probability model. **[inference]** Auditing that model may change the hypothesis labels or require new calibration, even if every observed decision ultimately survives.

Keep every numerical finding attached to its estimator. In particular, neither the failed deterministic-variant intervals nor the improved joint-test background treatment automatically characterizes the released central-value estimator. A configuration table is more valuable than repeated generic caveats.

Give the negative results figure space comparable to the data comparisons. A methods paper whose main failures remain in prose will still read like an unsuccessful measurement paper with qualifications appended.

Avoid a causal explanation stronger than the tests support. “Regularization bias” is the manuscript’s interpretation of persistent deformation residuals; the paper should show the tested iteration and capacity dependence supporting that interpretation. Likewise, failed recovery does not by itself establish a general identifiability limit, and exceeding a chosen target does not establish an OmniFold precision floor.

Finally, make the release serve the methods contribution. Readers should be able to reconstruct the bias comparisons, coverage plots, estimator distinctions, and conditional-test decisions—not merely reproduce the visually prominent central-value figures. **[inference: editorial assessment]** With those changes and a defensible calibration procedure, the paper could offer a useful, candid neutrino-unfolding case study; without them, recasting would change its claims more than its evidential strength.