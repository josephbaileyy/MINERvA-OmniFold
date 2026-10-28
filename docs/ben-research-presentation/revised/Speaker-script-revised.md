# MINERvA OmniFold: revised timed script for Ben

28 minutes of delivery plus 2 minutes of discussion. 24 main slides and 10 backups. Timing is a rehearsal estimate.

Detailed answers and editorial recommendations: Questions-and-note-suggestions.pdf. Main slide numbers match the original talk.

Evidence snapshot: ced3a8db5a8db544436c1f9cf635a8ce79ae73ad.

## Timed route

00:00–00:56  01. MINERvA OmniFold  
00:56–01:53  02. The project now has three distinct outcomes  
01:53–02:52  03. The data and the measurement  
02:52–04:14  04. One complete OmniFold iteration  
04:14–05:19  05. Three different tests of an unfolding result  
05:19–06:20  06. The 2D cross section reproduces the published scale  
06:20–07:24  07. The 2D controls test recovery and bookkeeping  
07:24–08:41  08. The 2D repair leaves two validation questions  
08:41–09:51  09. Each added observable asks a physics question  
09:51–11:05  10. Hadronic energy reveals model differences  
11:05–12:08  11. The 5D projection locates a high-energy difference  
12:08–13:13  12. Extending the domain increases reliance on simulation  
13:13–14:42  13. The adopted 5D covariance carries four measurements  
14:42–16:04  14. The scalar campaigns exposed two distinct biases  
16:04–17:25  15. From an unqualified measurement to a model test  
17:25–18:46  16. All ten tests reject their specified hybrid nulls  
18:46–19:53  17. The inference has useful, measured limits  
19:53–21:04  18. PET gives OmniFold a set of objects per event  
21:04–22:10  19. The earlier PET covariance did not qualify  
22:10–23:21  20. PET recovery improved substantially in simulation  
23:21–24:37  21. Coverage counts intervals containing the true bin value  
24:37–25:51  22. The paired PET–tree comparison depends on the distortion  
25:51–26:57  23. Reproducibility became part of the research  
26:57–28:00  24. Discussion with Ben  
## Slide 1: MINERvA OmniFold

**00:00–00:56 (56 seconds)**

Ben, I want to bring you up to date on the whole project and separate what we have established from what still needs work. The original goal was to reproduce MINERvA’s inclusive muon-neutrino cross section using OmniFold, then use the same event-based method to add hadronic information. That expanded into two research directions: scalar observables, meaning one numerical value per event for each chosen quantity, and a learned representation of the particles and detector deposits in an event. I will show the successful reproduction first, then explain why uncertainty validation has become the central issue. I have kept the details of individual campaigns in backup slides so we can follow whichever part you want to discuss.

Sources:

- [docs/analysis-note/main_note.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/main_note.tex)
- [docs/publication/submission/PACKAGE-MANIFEST-20261006.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/publication/submission/PACKAGE-MANIFEST-20261006.md)

## Slide 2: The project now has three distinct outcomes

**00:56–01:53 (57 seconds)**

A central estimate is the fitted spectrum; an uncertainty procedure supplies its error bars. Closure asks whether unfolding recovers known simulated truth. Coverage asks whether intervals contain truth at their stated frequency across repeated experiments. With that distinction, there are three outcomes. The two-dimensional central result reproduces the published scale, but its error bars were computed with a different tree implementation, and their transfer is unvalidated. The statistical band was repaired, but has not passed an independent coverage re-test. Adding scalar observables passes specific recovery and consistency tests, while later tests expose limitations. A separate, conditional model test rejects five specified predictions. PET, a network that processes sets of particles or detector objects, improves some simulated recoveries but has no eligible uncertainty procedure.

Sources:

- [2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md)
- [3d-unfolding/3D_OMNIFOLD_STATUS.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/3d-unfolding/3D_OMNIFOLD_STATUS.md)
- [docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md)
- [nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md)
- [docs/orchestration/ASSESSMENT-20261008-2d-estimator-pairing.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/ASSESSMENT-20261008-2d-estimator-pairing.md)

## Slide 3: The data and the measurement

**01:53–02:52 (59 seconds)**

We use the same medium-energy neutrino-mode exposure as the published inclusive measurement: about 1.057 times ten to the twenty-one protons on target, leaving about 4.12 million selected events. Protons on target measures the accelerator exposure. Charged-current means the neutrino produces a charged lepton, here a muon. Inclusive means we do not require a particular hadronic final state. The fiducial volume is the selected interior region of the tracker. The reference cross section also restricts the muon angle and momentum as shown. MINERvA measures the interaction and recoil activity, while the downstream magnetized MINOS detector provides muon momentum and charge. Here p transverse and p parallel are momentum components relative to the beam. Simulation supplies paired records of the generated interaction and its detector reconstruction. PET keeps the reconstructed MINOS selection. Extended fiducial studies enlarge the truth domain, not the observed data sample.

Sources:

- [docs/analysis-note/sec_experiment.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_experiment.tex)
- [2d-unfolding/2D_OMNIFOLD_REFERENCE.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/2d-unfolding/2D_OMNIFOLD_REFERENCE.md)

## Slide 4: One complete OmniFold iteration

**02:52–04:14 (82 seconds)**

Unfolding estimates the particle-level distribution that could have produced detector observations. Truth means the simulation before detector effects; it is unknown for the data. This recovered animation uses conceptual toy events. First, a classifier, a function trained to separate labeled examples, compares data with reconstructed simulation. With the correct class normalization, its probability gives a density ratio, p divided by one minus p: where simulation needs more or less weight. The weights travel through the paired simulation to truth. A regressor predicts weights for truth events without a selected detector partner. A second classifier learns the truth-space reweighting. We repeat the cycle; each repetition is an iteration. The scalar analyses use boosted decision trees, small decision rules fitted successively. The output is a weighted truth ensemble, which we can histogram later. Iteration count and learner capacity restrict the fitted structure. The animation illustrates the algorithm; it does not certify every recovery or error bar.

Sources:

- [docs/analysis-note/sec_method.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_method.tex)
- [evidence/prepublication-2026-08-20-0b329e8a:docs/jul-16-presentation/visual-prototypes/presentation-grade/README.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/evidence/prepublication-2026-08-20-0b329e8a/docs/jul-16-presentation/visual-prototypes/presentation-grade/README.md)

## Slide 5: Three different tests of an unfolding result

**04:14–05:19 (65 seconds)**

Your shorthand is useful: closure primarily tests the point-estimation procedure, and coverage tests the interval procedure. In closure we know the simulated truth, optionally deform it away from the starting simulation, then ask how accurately unfolding recovers it. A dimensional anchor instead integrates away an added observable and checks consistency with the earlier result. Coverage counts repeated experiments whose intervals contain the target bin value. It is not event classification. Bias in the central estimate can also spoil coverage, so the two tests are connected. Passing a few closures cannot establish coverage, and wide intervals can cover even a biased estimate. Every verdict needs its target, simulated response, departures and sample construction. The one-dimensional binned study was a completed equivalence and debugging check, not a separate publication result.

Sources:

- [docs/analysis-note/sec_validation.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_validation.tex)
- [docs/analysis-note/sec_3d.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_3d.tex)

## Slide 6: The 2D cross section reproduces the published scale

**05:19–06:20 (61 seconds)**

This figure compares the two-dimensional extraction with the published result. The bin ratios show shape agreement, while the integrated comparison checks normalization. The integrated result is 3.073 times ten to the minus thirty-eight square centimeters per nucleon, 1.11 percent above the published total. Across the 205 reported bins, about 94 percent are within ten percent of the published values. This is a meaningful reproduction of the extraction and normalization using a different unfolding method. It uses the same data and many of the same systematic ingredients, so it is not an independent measurement of the physics. There is also a backend distinction: the published central estimate uses scikit-learn’s exact-split trees, while the uncertainty ensembles use LightGBM, another boosted-tree implementation. The central estimator and covariance are not strictly matched.

Sources:

- [2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md)
- [docs/analysis-note/figures/MEFHC_5iter_xsec_proj_pt.pdf](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/figures/MEFHC_5iter_xsec_proj_pt.pdf)
- [docs/analysis-note/sec_method.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_method.tex)
- [docs/analysis-note/figures/paper_fig1_validation.pdf](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/figures/paper_fig1_validation.pdf)

## Slide 7: The 2D controls test recovery and bookkeeping

**06:20–07:24 (64 seconds)**

The injected-shape and alternative-model rows are closure tests: they ask whether a known truth is recovered. Examples have median absolute residuals of 0.046 and 0.013 percent, within the 1.5 percent threshold. The missed-event row is a bookkeeping invariant, not a separate closure. A signal event can be inside our truth definition but fail reconstruction. Keeping that row preserves the full denominator and permits an efficiency correction; dropping it changes the target to selected events. It cannot create information where acceptance is zero. The iteration comparison checks stability: five versus ten iterations changes the total by 0.026 percent, while per-bin shape RMS changes by 1.54 percent. A hidden-resolution deformation tests a harder closure. At amplitude 0.30 the median residual is 3.43 percent, above the 3 percent rule; smaller amplitudes pass. Amplitude 0.30 names the injected shape parameter, not a thirty-percent detector error.

Sources:

- [docs/analysis-note/sec_validation.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_validation.tex)
- [docs/analysis-note/sec_method.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_method.tex)
- [2d-unfolding/2D_OMNIFOLD_REFERENCE.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/2d-unfolding/2D_OMNIFOLD_REFERENCE.md)

## Slide 8: The 2D repair leaves two validation questions

**07:24–08:41 (77 seconds)**

The covariance records variances and correlations between bins. Its reported 6.87 percent median budget uses a LightGBM central denominator, not the quoted exact-split central; the transfer remains unmeasured. The old statistical band covered fixed truth within two standard deviations in 91.21 percent of cases. It failed because the entire 99.5 percent confidence interval, 90.65 to 91.79 percent, lay below the predeclared acceptable window, 92.81 to 97.22 percent. We did not demand exact equality to the Gaussian 95.45 percent target. Removing an inconsistent fluctuating completeness factor produced the adopted replacement. An October seventh diagnostic found the bootstrap faithful on same-event pseudo-data, supporting under-scattering of those toys. That is not coverage validation. The full independent re-test remains deferred, and its proposed production-size population design is infeasible with the available independent simulation. A newer narrowed 2D route is a proposal, not a result or an authorized run.

Sources:

- [VALIDATION_LEDGER.md: VL169–VL172](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/VALIDATION_LEDGER.md)
- [docs/analysis-note/sec_systematics.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_systematics.tex)
- [docs/analysis-note/sec_validation.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_validation.tex)
- [KNOWN_ISSUES.md: 84–85](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/KNOWN_ISSUES.md)
- [docs/orchestration/ASSESSMENT-20261008-2d-estimator-pairing.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/ASSESSMENT-20261008-2d-estimator-pairing.md)
- [docs/orchestration/state/ki85-diag-20261006/ki85_result.json](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/state/ki85-diag-20261006/ki85_result.json)
- [docs/orchestration/DELIVERY-20261008-uncertainty-preparation.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/DELIVERY-20261008-uncertainty-preparation.md)
- [docs/orchestration/state/next-preparation-20261009/two-d-path/REPORT.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/state/next-preparation-20261009/two-d-path/REPORT.md)

## Slide 9: Each added observable asks a physics question

**08:41–09:51 (70 seconds)**

Available energy is a species-defined proxy for visible recoil energy, not all energy transferred by the neutrino. The incident neutrino supplies the energy but is not a final-state deposit. Final-state neutrinos are invisible here, and the adopted truth sum excludes neutrons and several other species as well. Momentum-transfer magnitude q three and inferred hadronic mass W distinguish interaction kinematics. Quasielastic scattering resembles nucleon knockout; resonances are excited hadronic states; deep-inelastic scattering populates high mass. But these are not independent axes: reconstructed q three and W both use the muon and the same recoil-energy estimate. Five coordinates therefore need at most four continuous inputs in this implementation. Extra coordinates can help a learner or organize a projection without adding independent information. We have no validated count of the additional measurable degrees of freedom from PET. Opening the truth phase space also does not create detector sensitivity.

Sources:

- [docs/analysis-note/sec_3d.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_3d.tex)
- [docs/analysis-note/sec_eavailw.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_eavailw.tex)
- [MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h)

## Slide 10: Hadronic energy reveals model differences

**09:51–11:05 (74 seconds)**

The three-dimensional result preserves the overall normalization of the two-dimensional anchor and recovers the tested injected available-energy shape. Here the spectrum shows how generator predictions separate once we examine the hadronic energy. Monte Carlo means simulation using random sampling. A generator is a Monte Carlo model of the neutrino interaction and final-state particles. GENIE, NuWro and GiBUU implement different physics assumptions, while MINERvA Tune v1 applies experiment-specific weights to the reference GENIE simulation. The low-energy deficit is related to the familiar two-particle–two-hole contribution, abbreviated two p two h: an interaction involving a pair of nucleons that leaves two holes in the nuclear state. Adding the Valencia model fills 52 percent of the gap below 0.4 GeV in this comparison. That is descriptive evidence about the central spectra, not proof of a unique mechanism or a significance. The older three-dimensional covariance-derived significances remain excluded from current claims. The history appendix retains a quarantined chi-square scan, excluded from current scientific claims. The energy definition also differs from some published low-recoil measurements, which limits direct comparisons.

Sources:

- [3d-unfolding/3D_OMNIFOLD_STATUS.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/3d-unfolding/3D_OMNIFOLD_STATUS.md)
- [VALIDATION_LEDGER.md: VL159–VL160](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/VALIDATION_LEDGER.md)
- [docs/analysis-note/figures/generators_vs_unfolded_band_central.pdf](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/figures/generators_vs_unfolded_band_central.pdf)

## Slide 11: The 5D projection locates a high-energy difference

**11:05–12:08 (63 seconds)**

This projection sums over the other three coordinates and shows the cell-integrated difference from the starting MINERvA Tune prediction. Sixty-seven percent of the positive excess lies above 0.8 GeV available energy; eighty-three percent of that is above W of 1.8 GeV. The largest cell in this particular map contains twenty-two percent of its positive excess. That does not establish the largest discrepancy across all observables: fractional differences, integrated excess and statistical significance are different rankings. The wide catch bins collect substantial phase space. The map motivates deep-inelastic modeling questions, but does not identify a unique cause. Finite iterations and learner capacity stabilize unfolding while leaving possible model dependence, called regularization bias. The nominal detector response is another assumption. The anchors and early closures stand, but neither certifies a local significance here.

Sources:

- [docs/analysis-note/sec_eavailw.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_eavailw.tex)
- [docs/analysis-note/figures/paper_fig2_joint.pdf](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/figures/paper_fig2_joint.pdf)
- [VALIDATION_LEDGER.md: VL149–VL152](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/VALIDATION_LEDGER.md)

## Slide 12: Extending the domain increases reliance on simulation

**12:08–13:13 (65 seconds)**

The extended-fiducial study asks what happens if we remove the truth-level muon kinematic restrictions while keeping the reconstructed selection. It is still an interaction in the tracker volume, not unrestricted neutrino phase space. Efficiency is the fraction of true events that become selected reconstructed events. The map shows a substantial region where that fraction is nearly zero. About 27.7 percent of the weighted true rate lies below two percent efficiency. In those regions the result relies heavily on extrapolating the missed-event weights from simulation. The published subdomain remains well anchored, and finite closure and three-prior comparisons provide useful diagnostics. But three priors do not bound all possible model dependence. One historical NuWro-shaped prior also predates the flux repair. There is no corrected covariance for this enlarged domain, so its result is preliminary central-value and validation information.

Sources:

- [docs/analysis-note/sec_fps.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_fps.tex)
- [docs/analysis-note/figures/fps_acceptance_MEFHC.pdf](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/figures/fps_acceptance_MEFHC.pdf)

## Slide 13: The adopted 5D covariance carries four measurements

**13:13–14:42 (89 seconds)**

Four measurements accompany the adopted five-dimensional covariance. A seed sets the random choices in training. Here the seed pair means two estimator configurations, not reco versus truth: an offset changes the ensemble while the physical throws stay fixed. First, the largest projected uncertainty-width change is 6.145 percent, exceeding the approved five percent bound. That bound was motivated by the roughly 5.6 percent sampling precision of a 160-throw width; it is a tolerance, not a significance or a generator-error fraction. Second, the effect stays near six percent in nested samples of 40, 80 and 160 throws at this one seed pair, while the same-seed resampling control decreases. Larger ensembles and other seed pairs remain unmeasured. Third, five fixed-seed bands carry 6.75 percent of the trace, the sum of bin variances; their unprobed effect could move either way. Fourth, seed-induced central shifts reach 6.02 percent of projected uncertainty, and 49.8 percent for individual five-dimensional bins. The exception adopts specific bytes; it does not turn failed criteria into passes.

Sources:

- [docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md: §4](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md)
- [docs/orchestration/CORRECTION-20260921-seed-effect-larger-ensemble-corollary-withdrawn.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/CORRECTION-20260921-seed-effect-larger-ensemble-corollary-withdrawn.md)
- [docs/orchestration/CORRECTION-20260920-lower-bound-inference-withdrawn.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/CORRECTION-20260920-lower-bound-inference-withdrawn.md)
- [docs/orchestration/AUTHORIZATION-20260918-d-resource-required-deliverable-path.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/AUTHORIZATION-20260918-d-resource-required-deliverable-path.md)
- [docs/orchestration/PREREGISTRATION-20260919-cause3-two-member-campaign.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/PREREGISTRATION-20260919-cause3-two-member-campaign.md)

## Slide 14: The scalar campaigns exposed two distinct biases

**14:42–16:04 (82 seconds)**

The first bias came from multiplying data by a simulated signal fraction in detector bins, called purity. That approximation produced about four percent nominal-truth bias in the highest-W column. Signed subtraction instead represents data minus simulated background using negative background contributions; it need not be biased in expectation. A learned positive-weight representation can introduce approximation error. The later diagnosis found insufficient refinement-classifier capacity and repaired that nominal bias by increasing capacity. A separate failure remained: when truth was changed to generator-like shapes, residuals reached about seventy-four percent in some cells. Signal-only tests also failed, so negative subtraction cannot explain that failure. Candidate R then failed a real-data numerical-stability rule. A newer binned-response diagnostic finds many tested residual directions weakly constrained even with an exact response iteration. It is conditional evidence about those functions and grids, not a proof that every unbinned method must fail. These studies adopted no replacement measurement.

Sources:

- [VALIDATION_LEDGER.md: VL149–VL152](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/VALIDATION_LEDGER.md)
- [docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md)
- [docs/orchestration/state/next-preparation-20261009/d-id/REPORT.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/state/next-preparation-20261009/d-id/REPORT.md)

## Slide 15: From an unqualified measurement to a model test

**16:04–17:25 (81 seconds)**

Because we could not qualify the five-dimensional measurement and its total intervals, a separately authorized branch asked how strongly the data disagree with specified generator hypotheses. Each null combines the generator’s fine-cell rates with MINERvA Tune’s shape inside each cell and the declared detector assumptions. We simulate experiments under that hybrid and process them with the same estimator. Nuisance parameters describe uncertain ingredients such as an energy response. The resulting p-value is the probability, under that null, of a discrepancy at least as large as observed, not the probability the generator is true. The estimator still learns from unbinned events. The hypothesis and test statistic use a fixed finite grid so the predictions, metrics and pseudo-experiment comparisons are explicitly reproducible. That is a design choice, not an OmniFold requirement. It introduces within-cell assumptions, which is why refinement matters. An unbinned test would still need its own statistic and calibration.

Sources:

- [docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md)
- [docs/orchestration/RECORD-20260927-s5p-stage2-exit.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/RECORD-20260927-s5p-stage2-exit.md)
- [docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md)

## Slide 16: All ten tests reject their specified hybrid nulls

**17:25–18:46 (81 seconds)**

Yes: we reject compatibility of the data with each specified hybrid model, including its detector and uncertainty assumptions. We do not isolate the generator as the unique cause. All ten tests reject: five predictions, each tested for rate-plus-shape and for normalized shape. The predictions are MINERvA Tune, GENIE with and without Valencia two-nucleon interactions, NuWro and GiBUU. Testing several hypotheses gives several chances for a false rejection. Familywise five percent means controlling the probability of at least one such error across this declared family. Holm orders p-values and applies successively less stringent thresholds. This addresses the same multiplicity problem as the look-elsewhere effect, but here the family is ten fixed tests, not a continuous scan over possible bump locations. The six conditions on the slide remain part of every claim. Independent recomputation checks the calculation, not their physical adequacy. Monte Carlo p-values have finite resolution and are never zero.

Sources:

- [docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md: §3](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md)
- [docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md: §1](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md)
- [docs/publication/CLAIMS-20261005-claim-to-evidence.md: §§E–F](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/publication/CLAIMS-20261005-claim-to-evidence.md)

## Slide 17: The inference has useful, measured limits

**18:46–19:53 (67 seconds)**

Refinement divides truth cells more finely and repeats the null construction. If the answer keeps changing, the assumed shape inside the cells still matters. Here kappa multiplies the last measured refinement change in the output, along that direction only. One means one last-step shift; the primary analysis assumes two and the robustness check three. There is no universal typical kappa or guarantee that the remaining error is that small. In frozen ensembles, all ten decisions remain determinate to about 5.25; with recovered draws included the first loss is about 5.17. This is sensitivity, not convergence. The matched coarse muon-only projection does not reject GENIE CV, so hadronic inputs matter for that comparison. It does not prove an advantage over every lower-dimensional test. An exploratory four percent data-side energy shift also leaves the rejections, but does not test the full hadronic response.

Sources:

- [publication/kappa/RECORD-20261008-kappa-breakdown.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/publication/kappa/RECORD-20261008-kappa-breakdown.md)
- [publication/w2/W2B-REPORT-20261006.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/publication/w2/W2B-REPORT-20261006.md)
- [docs/publication/CLAIMS-20261005-claim-to-evidence.md: §§D–F](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/publication/CLAIMS-20261005-claim-to-evidence.md)

## Slide 18: PET gives OmniFold a set of objects per event

**19:53–21:04 (71 seconds)**

PET is the point-cloud transformer used by OmniLearn. It receives sets of detector deposits or simulated particles instead of only scalar summaries. A token represents one object numerically. Attention lets the network use relationships between objects. The historical recoil-only version omitted muon inputs; the later full-event model adds them at event level. Both retain at most twelve energy-ranked cloud objects, with padding for smaller sets. Twelve was a compute and memory compromise, not a demonstrated optimum. In the recorded truth inventory only 2.31 percent of events reach the cap, and the twelfth object carries on average 0.09 percent of retained truth energy. Reco clusters pile up at the cap, so those truth-side numbers do not show negligible detector information loss. Later designs added energy summaries to recover some omitted information. More tokens or features are not automatically more independently measurable physics quantities.

Sources:

- [docs/analysis-note/sec_pet.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_pet.tex)

## Slide 19: The earlier PET covariance did not qualify

**21:04–22:10 (66 seconds)**

The historical nominal and fifty-member bootstrap family disagreed in a localized way. On their common 257-cell domain, the bin-width-weighted nominal total is 10.27 percent above the family mean. The median cell ratio is nevertheless 1.00032, so this is not a uniform normalization shift. Sixty-three cells have nominal-to-mean ratios above 1.5; in forty-four of them the nominal exceeds every one of the fifty replicas. Those are measured discrepancies, not Gaussian significances or proof of a particular mechanism. A bootstrap randomly resamples events to estimate repeated-sample variation. I declined this nominal/covariance pairing; the partial covariance remains constructed but unverified. No full-event training-variation covariance or total PET covariance was adopted. Reconsideration would need estimator equivalence and separate coverage evidence. The later PET studies therefore concern method development.

Sources:

- [docs/analysis-note/sec_pet.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_pet.tex)
- [VALIDATION_LEDGER.md: VL132](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/VALIDATION_LEDGER.md)
- [docs/OPEN_ITEMS.md: OI-126](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/OPEN_ITEMS.md)
- [docs/orchestration/state/gate6-member-trajectories-result-56847059.json](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/state/gate6-member-trajectories-result-56847059.json)
- [docs/orchestration/state/RECEIPT-20260815-cstat-tail-geometry-and-weighting-correction.json](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/state/RECEIPT-20260815-cstat-tail-geometry-and-weighting-correction.json)

## Slide 20: PET recovery improved substantially in simulation

**22:10–23:21 (71 seconds)**

The September studies asked whether representation and training changes could improve recovery. We score normalized histograms using one minus the absolute distance between unfolded and target distributions divided by the prior’s distance from that target. That is R: one is exact recovery, zero means no improvement on the prior, and a negative value means moving farther away. The initial improvement study found gains from detector summaries, categorical particle identity and an efficiency-corrected truth step, but no frozen configuration passed both accuracy and stress requirements. The final-design study added longer truth-step training and better seed stability. On sixty final-bank draws of the available-energy tilt, the compact hybrid reaches 0.895 and the larger hybrid 0.863, versus 0.306 for the historical control. Those are substantial point-estimate gains. The banks are fixed finite simulation samples, and the study is signal-only. These results do not establish a universal architecture ranking, real-data performance or calibrated uncertainty.

Sources:

- [nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md)
- [docs/analysis-note/sec_pet_campaigns.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_pet_campaigns.tex)
- [VALIDATION_LEDGER.md: VL164–VL167](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/VALIDATION_LEDGER.md)

## Slide 21: Coverage counts intervals containing the true bin value

**23:21–24:37 (76 seconds)**

These percentages concern intervals for histogram bin values, not whether events were correctly classified as truth. In each simulated experiment, the compact estimate averages six bootstrap unfoldings, and the stated interval uses their spread. We ask whether that interval contains the known bin value. Across 120 draws, nominal 68 percent intervals contain truth in 89.6 percent of aggregate bin-draw cases. They over-cover. In low-acceptance regions, meaning truth events seldom enter the selected detector sample, containment is only 25.7 percent, and 78.9 percent for nominal 95 percent intervals. That is undercoverage. Moderate regions are nearer nominal; good-acceptance regions over-cover. The procedure therefore fails differently across regions; one common rescaling is not justified by this table. The compact point estimator passes its declared accuracy and stability tests, but the interval fails calibration. The larger finalist fails a separate point rule. No eligible design was selected.

Sources:

- [nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md)
- [docs/analysis-note/sec_pet_campaigns.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_pet_campaigns.tex)

## Slide 22: The paired PET–tree comparison depends on the distortion

**24:37–25:51 (74 seconds)**

The tree comparison uses identical simulated events, targets and injected departures. A departure is a controlled change to the truth distribution. Generator reweightings change event frequencies to resemble NuWro, NuWro-prime or GiBUU, while keeping the same detector simulation; they are not new simulated detectors. PET gains 0.102 and 0.070 in recovery on the available-energy tilt, but trees recover the three generator-shaped changes better. Some hadron-content comparisons depend on the tree iteration count. There are measured costs: a compact-finalist unfolding used a median 1.768 A100-hours at the declared packing, versus 1.517 for the larger finalist. More iterations make compact slower here. The 352-task tree comparison cost 5.306 charged CPU core-hours in total, not per task. Different hardware and packing prevent a clean speedup ratio. Neither a universal performance ranking nor an uncertainty comparison follows.

Sources:

- [docs/analysis-note/sec_pet_campaigns.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_pet_campaigns.tex)
- [VALIDATION_LEDGER.md: VL168](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/VALIDATION_LEDGER.md)
- [nd-unfolding/pet/gbdt_comparison/REPORT-20261005.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/nd-unfolding/pet/gbdt_comparison/REPORT-20261005.md)
- [nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md)

## Slide 23: Reproducibility became part of the research

**25:51–26:57 (66 seconds)**

The short version is that consequential claims need different kinds of checks. It is not that every result has been independently checked several times. Execution checks establish which input bytes and code actually ran. Numerical reproduction asks whether an independent implementation gets the same answer. Closure and coverage address recovery and intervals under declared assumptions. Physical validation asks whether those assumptions describe the detector and interaction well enough. Repeating one calculation cannot replace a missing check at another level. The import-path defect showed why matching file hashes alone was insufficient: the process could import another checkout. Some constructions remain unverified, and independent agreement on a hypothesis-test calculation does not certify its calibration model. The note, paper and replay materials should identify the check each claim has actually received.

Sources:

- [docs/OPEN_ITEMS.md: OI-136](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/OPEN_ITEMS.md)
- [docs/orchestration/CAMPAIGN-REVIEW-20260929.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/CAMPAIGN-REVIEW-20260929.md)
- [docs/publication/submission/PACKAGE-MANIFEST-20261006.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/publication/submission/PACKAGE-MANIFEST-20261006.md)
- [reproduction/s5p/README.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/reproduction/s5p/README.md)

## Slide 24: Discussion with Ben

**26:57–28:00 (63 seconds)**

The package is assembled but not submitted, and the publication-ready measurement objective remains unmet. I chose to keep the current two-dimensional central value and disclose the unmeasured transfer from its LightGBM uncertainty construction. That is an interim documentation decision, not a scientific resolution. An October tenth design proposes a matched seed-forty-two LightGBM route with narrower, explicit precision and nuisance-propagation claims; it does not establish total-interval coverage and is not adopted. Its next reproducibility experiment is specified but not authorized. The joint-five-dimensional study and PET remain useful for understanding model discrepancies and method limits. I would like us to decide which scientific claim should lead the paper, and what validation would most improve its credibility. More data or a larger network only helps if it addresses that particular missing evidence. [Pause for discussion.]

Sources:

- [docs/publication/submission/PACKAGE-MANIFEST-20261006.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/publication/submission/PACKAGE-MANIFEST-20261006.md)
- [docs/orchestration/PROPOSAL-20261005-scalar-measurement-successor.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/PROPOSAL-20261005-scalar-measurement-successor.md)
- [docs/orchestration/state/next-preparation-20261009/closeout/REPORT.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/state/next-preparation-20261009/closeout/REPORT.md)
- [docs/orchestration/state/next-preparation-20261009/two-d-path/REPORT.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/state/next-preparation-20261009/two-d-path/REPORT.md)

## Backup B1: Backup: exact available-energy convention

**Optional, outside the timed talk**

ECAL means electromagnetic calorimeter. A blob is a reconstructed aggregate of detector energy. Muon fuzz is energy associated with the muon’s nearby deposits and subtracted from the recoil estimate. No final nonnegative clamp is applied to the reconstructed quantity. The truth definition excludes secondary electrons, neutrons, kaons and other species not explicitly listed. The charged-pion subtraction uses 135 MeV rather than about 139.57 MeV. The effect has been measured, but its materiality against the adopted 5D projection is not established. There is no universal published available-energy convention. Do not describe this implementation as generically matching all low-recoil publications.

Sources:

- [docs/analysis-note/sec_3d.tex: operational definition](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_3d.tex)

## Backup B2: Backup: q3 and W are inferred kinematic quantities

**Optional, outside the timed talk**

At reconstruction level q zero comes from calorimetry and Q squared combines that energy estimate with the muon kinematics. M is the nucleon mass used in the estimator. These expressions motivate the variables, but nuclear motion and reconstruction mean W is an operational experimenter’s quantity, not a complete measurement of every final-state particle’s invariant mass. Quasielastic scattering, baryon resonances and deep-inelastic interactions populate different regions without forming perfectly separated event classes. The quantities are correlated and change under lateral systematics, which shift event coordinates rather than only their weights.

Sources:

- [docs/analysis-note/sec_3d.tex: fourth axis](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_3d.tex)
- [docs/analysis-note/sec_eavailw.tex: W as a fifth axis](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_eavailw.tex)

## Backup B3: Backup: the adopted covariance’s exact boundary

**Optional, outside the timed talk**

The full digest is 3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5. The projection digest begins 835828bf. Identity verification establishes which covariance was projected, not its statistical adequacy. The predeclaration ordering defect is ratified by exception, not cured, and no declared cause-3 boundary was evaluated by production. The paired measurement products used for the seed comparison are different digests and are not separately adopted. Five pinned bands are BeamAngleX, BeamAngleY, MuonResolution, Muon_Energy_MINERvA and Muon_Energy_MINOS. Their seed effect is unprobed in either direction. See slide 13 for the mandatory numerical measurements and their finite-ensemble scope.

Sources:

- [docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md)
- [docs/orchestration/OPERATIVE-SHEET-scalar5d.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/OPERATIVE-SHEET-scalar5d.md)

## Backup B4: Backup: reading the conditional p-values

**Optional, outside the timed talk**

These statistics belong only to the hybrid-null construction and the six conditions on slide 16. The frozen family has zero exceedances in nine tests and one in NuWro shape. Clopper–Pearson intervals are exact binomial confidence intervals for the exceedance probability. Determinacy requires those Monte Carlo intervals to resolve the decision relative to the multiple-testing threshold. The lost-draw recovery is report-only. Four nulls would have stopped one batch earlier with complete batches, with the same decisions. The closest recovered margin is 4.6 statistic units for GENIE plus MEC shape at kappa three. Independent checks cover the frozen-shift reading; the union reading is a same-code consistency replay. A small conditional p-value does not identify a nuclear mechanism or localize a discrepancy.

Sources:

- [docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md)
- [docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md)

## Backup B5: Backup: the PET representation studies

**Optional, outside the timed talk**

Pooling summarizes several objects into one representation. Individual routing gives each object its own attention token. The synthetic comparison used a small fixed object fixture and cannot settle production-multiplicity performance. The production cap acts on generic calorimeter clusters, not simply a thin typed-object tail. Later hybrid designs use energy summaries to recover some omitted information. PDG is the particle-identity code assigned by the Particle Data Group. One-hot encoding represents identity with separate category indicators rather than treating the code as a continuous number. PET2 is a tested pretrained model family. Pretraining means learning on another sample before this task. Its failure here applies to the tested recipes, not all possible pretraining. CPU–GPU optimizer differences were also investigated; numerical reproducibility does not establish physical accuracy.

Sources:

- [nd-unfolding/pet/direct_token_comparison/REPORT_FOR_BEN.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/nd-unfolding/pet/direct_token_comparison/REPORT_FOR_BEN.md)
- [nd-unfolding/pet/direct_token_comparison/GO_NO_GO-20260918.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/nd-unfolding/pet/direct_token_comparison/GO_NO_GO-20260918.md)
- [docs/analysis-note/sec_pet_campaigns.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_pet_campaigns.tex)

## Backup B6: Backup: the closed scalar sequence

**Optional, outside the timed talk**

These labels identify successive bounded campaigns, not distinct published measurements. They are all terminal. The background repair is a causal diagnosis for one nominal-bias component. The physical truth-departure failure remains without a single established cause. Reopening a closed study would require a new decision and contract. R is a targeted refinement change, not the production central-value estimator. A nominal-truth calibration check cannot establish performance over every alternative truth, and a pooled calibration result can hide individual functionals with poor coverage. A functional is any declared quantity extracted from the distribution, such as a bin, integral or projection.

Sources:

- [VALIDATION_LEDGER.md: VL149–VL155](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/VALIDATION_LEDGER.md)
- [docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md)
- [docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md)

## Backup B7: Backup: what the release can reproduce

**Optional, outside the timed talk**

Sufficient products are the stored quantities needed to recompute the reported inference without regenerating every event or training run. RC4 is a local release candidate, not a public deposit. Its scope excludes reproducing the 2D uncertainty, closure, bias, low-recoil, W2 and covariance-status numbers, as listed in its README. Those results retain their own evidence routes. The article still needs author decisions and external-release actions, including coauthor review, deposit and submission. None of those acts is authorized by preparing this talk.

Sources:

- [docs/publication/submission/PACKAGE-MANIFEST-20261006.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/publication/submission/PACKAGE-MANIFEST-20261006.md)
- [docs/publication/release/RC4-README.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/publication/release/RC4-README.md)
- [reproduction/s5p/README.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/reproduction/s5p/README.md)

## Backup B8: 2D: what changed, and what is still open

**Optional, outside the timed talk**

Two dimensions were enough for the original muon-kinematic measurement, and that reproduction remains valuable. They cannot reveal the conditional hadronic distributions integrated out of that projection. Separately, the early pipeline had bookkeeping defects; those were repaired before the frozen central result. The new uncertainty issues are not a reversal of that central-value reproduction. The October sixth repair removed a normalization factor from bootstrap replicas that was absent from their central estimator. The newer pairing audit showed that the quoted exact-split central and all LightGBM uncertainty blocks are different estimators. Their central shapes differ by a median 0.97 percent, or 1.3 statistical standard deviations per bin, despite nearly equal totals. Keep-and-disclose preserves the result while acknowledging this open transfer. The proposed matched route narrows its claims and requires its own decisions.

Sources:

- [2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md)
- [docs/orchestration/ASSESSMENT-20261008-2d-estimator-pairing.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/ASSESSMENT-20261008-2d-estimator-pairing.md)
- [docs/orchestration/state/next-preparation-20261009/two-d-path/REPORT.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/state/next-preparation-20261009/two-d-path/REPORT.md)

## Backup B9: Recorded coordinates and independent information

**Optional, outside the timed talk**

q zero is energy transfer, whereas available energy counts selected visible species. At fixed muon kinematics, the reconstruction forms Q squared from muon energy plus q zero, then computes both q three and W. W is therefore not an independent detector input once those shared ingredients are given. Truth uses related kinematics with its own mass and Q-squared conventions. A Pearson correlation alone would miss nonlinear dependence. I found no adopted correlation or information-rank measurement that supplies an independent-degree-of-freedom count for the scalar stack or a PET gain. The new binned-response diagnostic instead measures how weakly some specific truth combinations are constrained: among its selected resolution-stable weakly constrained joint functionals, median local Cramer–Rao widths are 31 percent on the coarse truth grid and 58 percent on the refined grid. These are conditional binned diagnostics, not OmniFold uncertainty estimates or a theorem about all unbinned methods.

Sources:

- [MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h)
- [docs/orchestration/state/next-preparation-20261009/d-id/REPORT.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/state/next-preparation-20261009/d-id/REPORT.md)

## Backup B10: More events: distinguish three different proposals

**Optional, outside the timed talk**

We should distinguish more measured data from more training simulation and a different physics sample. The scalar reproduction already uses the twelve medium-energy forward-horn-current playlists for this signal. PET has trained on smaller subsets of the truth inventory, so increasing that sample is a possible design change, with substantial cost. It does not automatically repair bias, a misspecified response, or interval calibration. The current open release also lists reverse-horn-current data. That enables an antineutrino-dominated analysis, not a direct extension of the same neutrino cross section without new modeling. Enlarging truth acceptance with unchanged reconstructed selection adds extrapolation, not observed events. Finally, more bootstrap replicas only reduce the numerical noise in a bootstrap estimate; they do not provide the independent detector-simulated populations missing from the coverage design.

Sources:

- [docs/analysis-note/sec_3d.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_3d.tex)
- [docs/analysis-note/sec_fps.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/analysis-note/sec_fps.tex)
- [nd-unfolding/pet/gbdt_comparison/REPORT-20261005.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/nd-unfolding/pet/gbdt_comparison/REPORT-20261005.md)
- [docs/orchestration/DELIVERY-20261008-uncertainty-preparation.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ced3a8db5a8db544436c1f9cf635a8ce79ae73ad/docs/orchestration/DELIVERY-20261008-uncertainty-preparation.md)
- [https://minerva.fnal.gov/getdata/](https://minerva.fnal.gov/getdata/)

## Technical reference: The adopted 5D covariance carries four measurements

Expanded measurements for slide 13 (reference, not additional timed speech):
M1: The maximum fractional change in a declared projected uncertainty width is s_proj = 6.145%, above the 5% bound. The aggregate and median diagnostics are 0.471% and 0.485%. The comparison products are different from the adopted digest.
M2: s_proj is 6.02%, 6.02% and 6.145% on nested N = 40, 80 and 160 subsets at one seed pair. The same-seed resampling control falls from 20.91% to 7.57% between 40 and 80. The quoted 6.04% ± 0.39% summarizes subset scatter, not the width over seed pairs. Larger N and seed-pair width remain unmeasured.
M3: BeamAngleX, BeamAngleY, MuonResolution, Muon_Energy_MINERvA and Muon_Energy_MINOS remain at literal seed 42. These five of 45 bands carry 6.75% of covariance trace, or 26.0% of the square-root trace scale, and contribute zero seed movement by construction. Releasing their seeds could change the total statistic in either direction.
M4: On 43 projection functionals, central relative shifts have median 0.104% and maximum 0.761%, compared with median relative uncertainty 10.1%. In units of their own uncertainties the shifts have median 1.06%, maximum 6.02%, and total-rate movement 1.13%. Per individual 5D bin, median is 3.77%, 90th percentile 13.6%, maximum 49.8% of uncertainty. The same-seed control is 9.4e-13.
Criterion scope: the 5% bound was approved with the roughly 5.6% finite-ensemble width precision as motivation. The seed comparison grades comparison products; the adopted digest did not evaluate C3 in its own production. Adoption does not change that history.

## Technical reference: All ten tests reject their specified hybrid nulls

Expanded conditions for slide 16 (reference, not additional timed speech):
1. The fine-grid null uses generator G's cross section, with MnvTune shapes and G's finite-MC fine-cell fluctuations below it. Refinement has not converged. The 0.50–0.86 comparison is the L2 norm of per-cell relative changes. The frozen kappa = 2 variants and the report-only kappa = 3 check follow the last refinement shift. The true sub-fine residual remains unmeasured and potentially material.
2. Detector calibration assumes the simulated per-event response beyond the drawn MinosEfficiency and GEANT neutron, pion and proton bands at plus or minus one standard deviation, together with the linear surrogate for five lateral bands. There is no recoil-energy-scale band. Hadronic-response completeness is not established.
3. Every pseudo-experiment draws all 34 vertical interaction-model bands. Negative LowQ2_1 and HighQ2_1 weights are clipped per universe under the recorded exception, at no more than 0.35% of a band's shift in the covariance-standardized norm.
4. Toys unfold with half the MC, whereas the data use the full MC. The shift measured in 16 pairs has median absolute size 0.02–0.075% per cell. Along the null's bias direction it is not always consistent with zero, but is at most about 0.05 null standard deviations. A bias-aligned upper-bound variant enters the rule.
5. GiBUU lacks neutrino energy above 20 GeV. Its truth outside p_parallel < 6 GeV/c still migrates into the tested domain under that energy truncation. All generator samples lack neutrino energy above 100 GeV; the record treats that tail as negligible.
6. Each prediction's finite simulation enters both as a diagonal variance term in the comparison metric and as a sampled residual. Independent recomputation establishes arithmetic agreement under these choices, not calibration adequacy.

## Terminology reference

**Acceptance / efficiency** (slides 3, 12, 21): Probability that a true signal event enters the selected detector sample. Weak acceptance increases reliance on simulation.

**Adoption under exception** (slides 13, B3): A decision to use one identified product despite specified failed or unresolved criteria. It does not change those criteria's grades.

**Band / universe / throw** (slides 7, 8, 13): A band groups variations of an uncertainty source. A universe is one variation. A throw is one random draw of the declared uncertain ingredients.

**Bias / residual** (slides 11, 14): Bias is the average displacement from truth over repeated experiments. A residual is an individual estimate minus its reference. A data-method difference alone does not measure bias.

**Bootstrap / Poisson bootstrap** (slides 8, 19–21): Resampling to estimate sampling variation. In the Poisson version, each event receives an independent random multiplicity with mean one, and the analysis is repeated.

**Boosted decision trees / GBDT / HGB** (slides 4, 6, 22): Successive small decision trees combine into a predictor. GBDT means gradient-boosted decision trees. HGB is the histogram-based implementation used for the paired comparator.

**Calibrated classifier** (slides 4): A classifier whose probability output is checked against class frequencies. Density-ratio use also requires the appropriate class-weight normalization.

**Calibrated test or interval** (slides 5, 15, 21): A test or interval whose long-run behavior has been checked under specified simulated assumptions. This differs from calibrating a classifier probability.

**Central value / estimator** (slides 2): The reported fitted value or distribution. An estimator is the full algorithm and settings that map observations to that output.

**Charged-current, CC / inclusive** (slides 3): CC produces a charged lepton. Inclusive here allows any hadronic final state consistent with the signal definition.

**Chi-square / metric** (slides 8, 16): A discrepancy measure, often a covariance-weighted squared distance. Its numerical value needs a specified sampling model before it becomes a p-value.

**Classifier / regressor** (slides 4): A classifier separates labeled examples. A regressor predicts a continuous numerical quantity, here including weights for missed events.

**Clipping / signed weights** (slides 14, 16): Some simulated corrections can be negative. Clipping replaces specified negative weights by a boundary value. Signed-background methods instead represent subtraction through negative contributions.

**Closure / pseudo-data / toy** (slides 5): Closure unfolds simulated data with known truth. Pseudo-data are the simulated observations. A toy is one simulated repeated experiment.

**Conditional inference** (slides 2, 15–17): A conclusion that holds under the specified model, detector and sampling assumptions. Agreement in arithmetic does not establish all of those assumptions.

**Covariance / trace / projected width** (slides 8, 13): Covariance records variances and correlations between bins. Its trace sums the bin variances. The width of a linear projection with coefficients u is sqrt(u^T C u).

**Coverage / undercoverage / overcoverage** (slides 5, 8, 21): Fraction of repeated intervals containing the specified truth. Below the stated confidence level is undercoverage, above it is overcoverage. Aggregate coverage can hide poor regions.

**CV / nominal / tune / prior** (slides 6, 10–11): CV is central value. Nominal denotes the reference settings. A tune modifies simulation using fitted or chosen adjustments. The unfolding prior is its starting truth distribution.

**Density ratio / event weight** (slides 4): A factor that changes the relative population of events at given coordinates. An event weight scales that event's contribution to the estimated distribution.

**Determinate decision** (slides 16–17, B4): A rejection decision resolved despite the Monte Carlo uncertainty in the estimated tail probability, using the declared confidence-interval rule.

**Dimensional anchor / marginal / projection** (slides 5, 9–11): Integrate over an added coordinate to recover a lower-dimensional distribution. Normalization agreement is weaker than agreement in every cell.

**Eavail / recoil / ECAL / blob / muon fuzz** (slides 9–10, B1): Eavail is the implemented visible-hadronic-energy quantity, detailed in B1. Recoil is non-muon activity. ECAL is the electromagnetic calorimeter. Blobs are reconstructed aggregates of deposits. Muon fuzz is nearby muon-associated energy subtracted from recoil.

**Ensemble / replica / member / seed** (slides 8, 13, 19–21): An ensemble is a collection of repeated fits. A replica or member is one fit. A seed fixes a pseudo-random sequence. Seed variation and event-resampling variation probe different effects.

**Familywise alpha / Holm correction** (slides 16): Alpha is the allowed false-rejection probability. Familywise control bounds the probability of any false rejection across the declared set. Holm applies successively adjusted thresholds to ordered p-values.

**Fiducial volume / phase space / FPS** (slides 3, 12): Fiducial volume is the selected detector region. Phase space here means the allowed kinematic domain. The project's FPS work extends truth-muon cuts while retaining the tracker-volume and reconstructed-selection requirements.

**Fine-grid hybrid null / sub-grid** (slides 15–17): The tested truth has generator G's rates in fine cells and MnvTune shapes, with G's finite-MC fluctuations, below them. Sub-grid denotes structure within those cells. This is a specified hybrid model, not arbitrary generator truth.

**Flux / protons on target, POT / FHC** (slides 3, 8): Flux is incident neutrinos per area. POT measures accelerator exposure. FHC means forward horn current, the beam-focusing configuration used for neutrino mode.

**Functional / supported cell** (slides 13, B4, B6): A functional is a declared extracted quantity, such as a bin or projection. A supported cell has simulation support under the analysis's declared domain rules.

**Gaussian / standard deviation, SD / RMS** (slides 5, 8, B4): Gaussian is the normal distribution. SD measures spread around the mean. RMS is the square root of the average squared quantity. A tail probability is not automatically a Gaussian significance.

**Generator / Monte Carlo, MC** (slides 10, 16): A generator simulates interactions and final-state particles using a physics model. Monte Carlo uses random sampling. GENIE, NuWro and GiBUU are generator frameworks used here.

**Hadronic response / detector response** (slides 7, 11, 16–17): The distribution of reconstructed signals given an underlying event. Hadronic response concerns energy and activity from the non-leptonic part of the event.

**Hash / digest / checkout / import path** (slides 13, 23, B3): A hash or digest identifies file bytes. A checkout is a local code version. An import path controls where the program finds modules. Correct file hashes alone do not prove the intended modules executed.

**Held-out / final bank / reserve bank** (slides 20–22): Simulation samples reserved for distinct stages of evaluation. A fixed bank is a finite parent sample, so inference using it remains conditional on that bank.

**Iteration / capacity / regularization** (slides 4, 7, 11, 14): An iteration repeats OmniFold's two steps. Capacity describes how complex a fitted function can be. Restricting either can stabilize estimation but retain bias toward the prior.

**Kappa / refinement shift** (slides 17): Kappa scales the last measured change under grid refinement. The reported scan follows that one direction and does not bound the unknown remaining error.

**Lateral / vertical systematics / surrogate** (slides 16, B2): Lateral changes shift event coordinates and can change selection. Vertical changes alter weights. A surrogate approximates a more expensive change, here the specified linear treatment of lateral variations.

**LightGBM / scikit-learn / backend** (slides 6): Software implementations of the learner. A backend is a selectable implementation. Matching broad tree settings does not make different backends the same estimator.

**MAT / MinosEfficiency / GEANT** (slides 8, 16): MAT is the MINERvA Analysis Toolkit. MinosEfficiency is the MINOS selection-efficiency uncertainty band. GEANT-based detector simulation includes hadron-transport variations.

**Missing event / purity / background** (slides 4, 7, 14): A miss is a true signal event without a selected reconstructed partner. Purity is the predicted signal fraction in a detector bin. Background is selected activity outside the declared signal.

**Null / p-value / power** (slides 15–17, B4): The null is the specified hypothesis tested. A p-value is its tail probability for the observed statistic. Power is the probability of rejecting the null under a specified alternative.

**Nuisance parameter** (slides 15): An uncertain model or detector ingredient varied while testing the main physics hypothesis.

**PET / transformer / attention / token** (slides 18): PET is the point-cloud transformer used in OmniLearn. A transformer learns interactions among object representations through attention. A token is one object's input representation.

**Point cloud / full-event / recoil-only** (slides 18–19): A point cloud is an unordered set of objects. Full-event PET includes muon information alongside recoil objects. The historical recoil-only classifier omitted the muon.

**PDG / one-hot / pooling / pretraining** (slides 20, B5): PDG is a particle-identity code. One-hot uses separate category indicators. Pooling combines multiple objects into a summary. Pretraining learns parameters on another sample before this task.

**q0 / q3 / Q² / W** (slides 9, B2): Energy transfer, magnitude of three-momentum transfer, positive spacelike transfer squared, and experimenter's hadronic mass. B2 gives the relations and operational interpretation.

**Quasielastic / resonance / DIS / 2p2h / MEC** (slides 9–11, 16): Quasielastic resembles nucleon knockout. Resonances are excited hadronic states. DIS is deep-inelastic scattering at high hadronic mass. 2p2h involves two particles and two holes in the nuclear state. MEC means meson-exchange current, the label used for the Valencia two-nucleon contribution in these predictions.

**Recovery R / L1 distance** (slides 20–22): Here R = 1 - sum|unfolded-target|/sum|prior-target| for unit-normalized histograms. The sum of absolute differences is L1 distance. R becomes unstable when the injected marginal change is tiny.

**Rounding sensitivity / reproducibility floor** (slides 14): Movement caused by tiny numerical perturbations of the same inputs. It can matter when statistical intervals are similarly small.

**Scalar observable / dimensionality** (slides 1, 9): One numerical value per event for a chosen property. Five recorded observables need not represent five independent physical degrees of freedom.

**Shape-only / total test** (slides 16): A shape-only comparison removes overall normalization. A total comparison retains rate information as defined by the campaign statistic.

**Student-t / Clopper–Pearson** (slides B4; PET interval details): Student-t accounts for estimating a spread from a small sample. Clopper–Pearson gives exact binomial confidence limits for an exceedance probability. Neither fixes model misspecification.

**Systematic / statistical / training uncertainty** (slides 8, 19): Statistical variation comes from finite event samples. Systematics reflect uncertain detector or physics ingredients. Training variation comes from the learning procedure at fixed inputs.

**Sufficient products / replay / regeneration / RC4** (slides 23, B7): Sufficient products retain what is needed for a specified calculation. Replay recomputes from them. Regeneration rebuilds upstream simulation or training. RC4 is the local fourth release candidate.

**Terminal / gate / VL / s5c–s5p** (slides 8, 14–15, 19, B6): Terminal means a study ended under its rules. A gate is a required check before a next action. VL identifies validation-ledger entries. The s5 labels identify bounded scalar campaigns, not separate measurements.

**Uncertainty transfer** (slides 2, 8): The claim that a band constructed for one estimator also describes another estimator; here it remains unmeasured.

**q0** (slides 9, B9): Energy transferred from the lepton to the hadronic system, distinct from the selected visible-energy sum Eavail.

**Identifiable quantity** (slides B9): A truth quantity distinguishable through the observed detector distribution under stated assumptions.

**Cramer–Rao width** (slides B9): A local information-based precision diagnostic for a specified response model and estimator class; not a universal bound on biased or differently specified estimators.

**Familywise error** (slides 16): Probability of at least one false rejection across the stated family of tests.

**A100-hour** (slides 22): One hour of use of one NVIDIA A100 GPU; distinct from a CPU core-hour or whole-node hour.
