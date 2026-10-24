**My judgment: a publishable joint measurement remains plausible, but the strongest route involves coarser reporting, explicit unfolding-model dependence, and possibly a published regularization operator.** The records argue against the present precision targets; they do not establish that a useful 5D publication is impossible.

One qualification matters immediately: reconstructed \(W\) is determined by \((p_T,p_\parallel,q_3)\), and truth \(W\) is nearly determined by them. This can be a joint distribution in five observables, but it supplies fewer than five independent kinematic constraints. That affects both the scientific pitch and sensible binning ([sec_eavailw.tex, lines 109–140](docs/analysis-note/sec_eavailw.tex:109)).

**1. What publication would actually require**

Community practice accepts quantified model dependence and regularization. For example:

- MINERvA’s \(E_{\rm avail},q_3\) measurement assigns an uncertainty from the difference between extractions using MnvTune-v1.2 and v3; it also propagates hadronic-response uncertainties grounded in test-beam measurements ([paper, Sec. VI](https://arxiv.org/pdf/2110.13372)).
- T2K validates with alternative generators and substantial reweightings finer than its reporting bins, including changes to within-bin efficiency. It publishes both regularized and unregularized results ([paper, Secs. IV.3–IV.6](https://arxiv.org/html/2004.05434v2)).
- MicroBooNE publishes regularized cross sections, covariance matrices, and \(A_C\) matrices that users apply to predictions. Its fake-data tests check whether the assigned uncertainties accommodate alternative-generator results ([multidifferential measurement, Sec. V](https://arxiv.org/pdf/2301.03700), [validation example, Sec. V](https://arxiv.org/pdf/2310.06082)).

**My inference from these precedents:** publication requires a defensible measurement and usable comparison prescription, rather than a universal guarantee of unbiased recovery.

For this analysis, I would require four concrete deliverables:

1. **A reporting definition matched to actual sensitivity.** Publish supported joint cell integrals, with explicit fiducial cuts, normalization, conventions and acceptance exclusions. The existing 27-cell H2 partition is genuinely joint in five observables; the EW projection alone is not ([DESIGN.md, lines 93–127](docs/orchestration/state/measurement-paper/5d-design-20261023/DESIGN.md:93)).

2. **A central value and uncertainty from the same estimator.** Configuration (e) needs its own statistical and systematic covariance. The design explicitly records that this covariance does not yet exist; its production estimate is modest once inputs exist ([DESIGN.md, lines 310–370](docs/orchestration/state/measurement-paper/5d-design-20261023/DESIGN.md:310)).

3. **An explicit treatment of regularization bias.** Either propagate justified model variations, with correlations, or publish the measurement’s response to truth through a validated operator. Presently, generator-sized residuals enter no quoted uncertainty. That is a substantive publication obstacle ([sec_5d.tex, lines 105–123](docs/analysis-note/sec_5d.tex:105)).

4. **Validation of the released object.** Include background-inclusive fake data, rate changes, interaction/FSI changes, within-cell composition changes, detector shifts, statistical pull checks and reconstructed-data agreement. Release the covariance, bin map and comparison instructions. Reproducing 2D or closing a \(W\) marginal does not validate joint cells.

Hadronic response deserves particular attention. MP1’s shortcut failed its declared test; subsequent studies attributed its apparent curvature to estimator discreteness. That leaves a repairable uncertainty-propagation problem, rather than evidence that hadronic response is negligible ([S1-REPORT.md, lines 3–13 and 311–325](docs/orchestration/state/measurement-paper/phase1/mp1/S1-REPORT.md:3)).

**2. Best route, cost and main risk**

**My first choice is a coarser, supported joint measurement using configuration (e), with a correlated unfolding-model component and relaxed precision targets.** Start with H2 as a candidate, then merge or restrict cells based on response sensitivity and simulation support. Coarsening alone is insufficient: the records show that freeing within-cell shapes can substantially enlarge uncertainties ([PLAN.md, lines 369–379](docs/orchestration/state/measurement-paper/PLAN.md:369)).

I would test an unscaled, physically motivated correlated model component before trying to shrink it through a single calibrated \(\kappa\). Stage 0 rejected that particular transfer prescription: GiBUU’s bias-containment fraction was 0.541 on J and 0.259 on H2. These fractions are **not repeated-experiment coverage probabilities**. The result does not establish that every larger or differently constructed model uncertainty fails ([STAGE0-REPORT.md, lines 25–36 and 105–125](docs/orchestration/state/measurement-paper/5d-design-20261023/STAGE0-REPORT.md:25)).

If that cannot accommodate plausible departures without making the result uninformative, **my preferred fallback is a linear regularized measurement with a released \(A_C\)**. Build and validate this as a separate estimator; a local derivative of nonlinear OmniFold is not automatically a globally valid smearing matrix.

| Route | Cost assessment | Main risk |
|---|---|---|
| Coarse joint result plus model uncertainty | Recorded covariance production: roughly **16–18 CPU node-hours or 25–28 GPU node-hours**, excluding input preparation. **My planning estimate:** reserve 100–300 CPU and 500–2,000 GPU node-hours for development, systematics and validation. | Model variations miss response-relevant within-cell composition. |
| Regularized result plus \(A_C\) | **My estimate:** tens of CPU node-hours for an initial binned prototype; hundreds for a release-quality study. No complete repository costing exists. | Resolution may be too broad to support useful joint conclusions. |
| Existing extensive coverage programme | Recorded estimate: about **28,300 GPU node-hours** for its per-functional stage, plus preceding work. | Precisely establishing failure of an unsuitable construction. |

The recorded costs are in [DESIGN.md, lines 362–423](docs/orchestration/state/measurement-paper/5d-design-20261023/DESIGN.md:362). My estimates are budget envelopes, not measured forecasts. Your allocation is ample for the first two routes; I would not initially commit most of it to coverage certification.

The largest scientific risk is **response model dependence beyond the five scalars**. Existing full-event generator reweighting failed its establishment tests for every generator ([S2-CLOSURE-SUMMARY.md, lines 18–31](docs/orchestration/state/measurement-paper/phase1/mp2/S2-CLOSURE-SUMMARY.md:18)). More toys cannot resolve that missing physical validation.

**3. Where the standards are stricter—and appropriately strict**

The 10% median total-width cap, 5% model-component cap and required recovered fraction are project objectives, not general publication requirements. Likewise, simultaneous coverage certification across every functional and fresh truth is considerably stronger than the cited experimental practice ([DESIGN.md, lines 440–448 and 500–517](docs/orchestration/state/measurement-paper/5d-design-20261023/DESIGN.md:440)). A useful first measurement can have 20–40% uncertainties; that range is my judgment, not a prediction here.

The project is right to distinguish closure from coverage, require matched central values and covariance, expose acceptance holes, and refuse to ignore known bias. Prior-free bounds of median 28.59% and p90 120.8% show why some cells require restriction or explicit model assumptions ([MP4-A REPORT, lines 19–27](docs/orchestration/state/measurement-paper/phase1/mp4a/REPORT.md:19)). Absence of exhaustive coverage tests in other papers does not license disregarding failures already observed here.

**4. Dead ends I would reconsider**

Three closures are conditional on the project’s endpoint: **model dependence as an uncertainty, coarser joint cells, and \(A_C\)-based reporting** ([PLAN.md, lines 381–390](docs/orchestration/state/measurement-paper/PLAN.md:381)). All remain scientifically legitimate publication routes.

I would give extra reconstructed information lower priority. R10 is formally **INCOMPLETE**, with a failed null control; nevertheless, none of its eleven configurations achieved the required residual reduction ([R10 REPORT, lines 24–37 and 82–106](docs/orchestration/state/measurement-scoping/r10/REPORT.md:24)). It establishes neither impossibility nor a promising rescue.

I would therefore spend the next effort defining a useful, honestly regularized joint measurement that existing data can support, before pursuing stronger precision or coverage guarantees.