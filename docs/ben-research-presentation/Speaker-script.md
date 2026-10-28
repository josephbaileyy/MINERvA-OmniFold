# MINERvA OmniFold: timed script for Ben

28 minutes of delivery plus 2 minutes of discussion. 24 main slides and 7 backups. About 135 words/minute with short figure pauses. Timing is a rehearsal estimate.

## Order selected

Question-led: method, 2D reproduction, added observables, uncertainty and inference, PET, decisions. See OUTLINE.md for the three alternatives considered before drafting.

## Timed route

00:00–00:56  01. MINERvA OmniFold  
00:56–01:53  02. The project now has three distinct outcomes  
01:53–02:52  03. The data and the measurement  
02:52–04:14  04. OmniFold learns event weights in two spaces  
04:14–05:19  05. Three different tests of an unfolding result  
05:19–06:20  06. The 2D cross section reproduces the published scale  
06:20–07:24  07. The 2D controls test recovery and bookkeeping  
07:24–08:41  08. The rebuilt uncertainty recipe still needs a coverage test  
08:41–09:51  09. Each added observable asks a physics question  
09:51–11:05  10. Hadronic energy reveals model differences  
11:05–12:08  11. The 5D projection locates a high-energy difference  
12:08–13:13  12. Extending the domain increases reliance on simulation  
13:13–14:42  13. The adopted 5D covariance carries four measurements  
14:42–16:04  14. The scalar campaigns exposed two distinct biases  
16:04–17:25  15. A calibrated model test answers a narrower question  
17:25–18:46  16. All ten tests reject their specified hybrid nulls  
18:46–19:53  17. The inference has useful, measured limits  
19:53–21:04  18. PET gives OmniFold a set of objects per event  
21:04–22:10  19. The earlier PET covariance did not qualify  
22:10–23:21  20. PET recovery improved substantially in simulation  
23:21–24:37  21. PET intervals fail differently across acceptance regions  
24:37–25:51  22. The paired PET–tree comparison depends on the distortion  
25:51–26:57  23. Reproducibility became part of the research  
26:57–28:00  24. Discussion with Ben  

28:00–30:00 Discussion

## Slide 1: MINERvA OmniFold

**00:00–00:56 (56 seconds)**

Ben, I want to bring you up to date on the whole project and separate what we have established from what still needs work. The original goal was to reproduce MINERvA’s inclusive muon-neutrino cross section using OmniFold, then use the same event-based method to add hadronic information.

That expanded into two research directions: scalar observables, meaning one numerical value per event for each chosen quantity, and a learned representation of the particles and detector deposits in an event. I will show the successful reproduction first, then explain why uncertainty validation has become the central issue. I have kept the details of individual campaigns in backup slides so we can follow whichever part you want to discuss.

Sources:

- [docs/analysis-note/main_note.tex](../../docs/analysis-note/main_note.tex)
- [docs/publication/submission/PACKAGE-MANIFEST-20261006.md](../../docs/publication/submission/PACKAGE-MANIFEST-20261006.md)

## Slide 2: The project now has three distinct outcomes

**00:56–01:53 (57 seconds)**

There are three outcomes to keep separate. The two-dimensional reproduction gives a stable central cross section close to the published result. Its uncertainty construction has been repaired, although the newest statistical band still needs a coverage re-test. The scalar extensions add up to five recorded observables and pass specific consistency and closure tests. A separate campaign gives conditional generator-test results, but did not qualify a five-dimensional cross-section measurement with total uncertainties.

Finally, the point-cloud studies substantially improve recovery of some simulated distortions. Their uncertainty procedure fails calibration, so they remain method development. A central estimate is the fitted spectrum. An uncertainty procedure is the rule that assigns its error bars. Success of one does not automatically establish the other.

Sources:

- [2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md](../../2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md)
- [3d-unfolding/3D_OMNIFOLD_STATUS.md](../../3d-unfolding/3D_OMNIFOLD_STATUS.md)
- [docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md](../../docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md)
- [nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md](../../nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md)

## Slide 3: The data and the measurement

**01:53–02:52 (59 seconds)**

We use the same medium-energy neutrino-mode exposure as the published inclusive measurement: about 1.057 times ten to the twenty-one protons on target, leaving about 4.12 million selected events. Protons on target measures the accelerator exposure. Charged-current means the neutrino produces a charged lepton, here a muon. Inclusive means we do not require a particular hadronic final state.

The fiducial volume is the selected interior region of the tracker. The reference cross section also restricts the muon angle and momentum as shown. MINERvA measures the interaction and recoil activity, while the downstream magnetized MINOS detector provides muon momentum and charge. Here p transverse and p parallel are momentum components relative to the beam. Simulation supplies paired records of the generated interaction and its detector reconstruction.

Sources:

- [docs/analysis-note/sec_experiment.tex](../../docs/analysis-note/sec_experiment.tex)
- [2d-unfolding/2D_OMNIFOLD_REFERENCE.md](../../2d-unfolding/2D_OMNIFOLD_REFERENCE.md)

## Slide 4: OmniFold learns event weights in two spaces

**02:52–04:14 (82 seconds)**

Unfolding estimates the particle-level distribution that could have produced the detector-level observations. Truth means the simulated interaction before detector effects, not something directly known for the data. OmniFold does this through event weights. In the detector step, a classifier learns to distinguish data from reconstructed simulation. A classifier is a function trained to separate labeled examples. With the appropriate class normalization, its probability gives a density ratio through p divided by one minus p. That ratio says where simulation needs more or less weight.

We transfer the weights through the paired simulated events to truth. A regressor, meaning a learned prediction of a numerical quantity, supplies weights for truth events without a selected reconstructed partner. The second classifier smooths the reweighting in truth space. Repeating these steps defines an iteration. The scalar analyses use boosted decision trees: an ensemble of small decision rules fitted successively. The final product is a weighted truth ensemble, so we can choose reporting histograms afterward. The number of iterations and the learner’s capacity limit how much structure the fit can recover.

Sources:

- [docs/analysis-note/sec_method.tex](../../docs/analysis-note/sec_method.tex)

## Slide 5: Three different tests of an unfolding result

**04:14–05:19 (65 seconds)**

These terms recur throughout the talk. A closure test creates pseudo-data, or simulated data, whose underlying truth we know. We change that truth, unfold, and ask whether we recover it. A dimensional anchor integrates away an added observable and compares with the earlier lower-dimensional result. That checks consistency, especially normalization, but does not prove every shape agrees.

Coverage asks a different question: if we repeated the experiment many times, how often would a stated interval contain the fixed truth? A nominal 95 percent interval should do so roughly 95 percent of the time under the tested model. A method can recover one injected bump and still have poorly calibrated intervals or miss a different distortion. The one-dimensional binned study served as an equivalence and debugging cross-check. It is complete and is not a separate publication result.

Sources:

- [docs/analysis-note/sec_validation.tex](../../docs/analysis-note/sec_validation.tex)
- [docs/analysis-note/sec_3d.tex](../../docs/analysis-note/sec_3d.tex)

## Slide 6: The 2D cross section reproduces the published scale

**05:19–06:20 (61 seconds)**

This figure compares the two-dimensional extraction with the published result. The bin ratios show shape agreement, while the integrated comparison checks normalization. The integrated result is 3.073 times ten to the minus thirty-eight square centimeters per nucleon, 1.11 percent above the published total. Across the 205 reported bins, about 94 percent are within ten percent of the published values.

This is a meaningful reproduction of the extraction and normalization using a different unfolding method. It uses the same data and many of the same systematic ingredients, so it is not an independent measurement of the physics. There is also a backend distinction: the published central estimate uses scikit-learn’s exact-split trees, while the uncertainty ensembles use LightGBM, another boosted-tree implementation. The central estimator and covariance are not strictly matched.

Sources:

- [2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md](../../2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md)
- [docs/analysis-note/figures/MEFHC_5iter_xsec_proj_pt.pdf](../../docs/analysis-note/figures/MEFHC_5iter_xsec_proj_pt.pdf)
- [docs/analysis-note/sec_method.tex](../../docs/analysis-note/sec_method.tex)
- [docs/analysis-note/figures/paper_fig1_validation.pdf](../../docs/analysis-note/figures/paper_fig1_validation.pdf)

## Slide 7: The 2D controls test recovery and bookkeeping

**06:20–07:24 (64 seconds)**

Several controls support that result. Injected truth shapes and selected alternative systematic-universe tests pass their declared thresholds. A universe here means a simulated variation of an uncertain model or detector parameter. We also repaired and checked the signal bookkeeping: truth records define the denominator, and an event that fails reconstruction remains present as a missed event. That prevents an apparently successful unfold from silently losing part of the signal.

Five iterations are the frozen production choice, supported by the existing iteration checks. The validation has a visible boundary. In a hidden-variable test, a sufficiently large distortion in a detector-resolution variable exceeds the closure threshold. That matters because agreement on the training observables cannot guarantee correctness for every unobserved feature or detector response. I would describe these as targeted validation successes, with their tested scope attached.

Sources:

- [docs/analysis-note/sec_validation.tex](../../docs/analysis-note/sec_validation.tex)
- [docs/analysis-note/sec_method.tex](../../docs/analysis-note/sec_method.tex)
- [2d-unfolding/2D_OMNIFOLD_REFERENCE.md](../../2d-unfolding/2D_OMNIFOLD_REFERENCE.md)

## Slide 8: The rebuilt uncertainty recipe still needs a coverage test

**07:24–08:41 (77 seconds)**

A covariance matrix describes both individual bin variances and how bins move together. The two-dimensional construction combines 187 systematic universes with statistical resampling and training variation. Flux means the number of incident neutrinos per area. Applying each universe’s flux normalization correctly was essential. The current construction follows the MINERvA Analysis Toolkit prescription and gives a median relative bin uncertainty of 6.87 percent. That number is not the error on the integral.

A recent fixed-truth test found that the old statistical band contained truth within two standard deviations only 91.21 percent of the time, below its predeclared acceptable window. The repair removed a spurious fluctuating completeness normalization from the replicas. I adopted the rebuilt statistical band, and the combined products were rebuilt. The printed total median barely changed because other sources dominate. The new band has not been coverage re-tested. Adding our covariance to the published one double-counts shared systematics, so I do not use the resulting small chi-square as the main validation claim.

Sources:

- [VALIDATION_LEDGER.md: VL169–VL172](../../VALIDATION_LEDGER.md)
- [docs/analysis-note/sec_systematics.tex](../../docs/analysis-note/sec_systematics.tex)
- [docs/analysis-note/sec_validation.tex](../../docs/analysis-note/sec_validation.tex)
- [KNOWN_ISSUES.md: 84–85](../../KNOWN_ISSUES.md)

## Slide 9: Each added observable asks a physics question

**08:41–09:51 (70 seconds)**

The progression follows the physics. Available energy, E avail, is a species-dependent measure of visible hadronic energy. It is not the total energy transfer, because neutrons and other excluded particles do not contribute to its truth definition. The fourth observable, q three, is the magnitude of the three-momentum transferred to the hadronic system. At reconstruction level it uses muon kinematics and a calorimetric estimate of energy transfer.

The fifth, W, is an experimenter’s inferred hadronic invariant mass. It helps separate the quasielastic region, where scattering resembles a nucleon knockout, from resonance production and the high-mass deep-inelastic region. These variables are correlated and partly derived, so five dimensions means five recorded coordinates, not five independent degrees of freedom. Adding an input avoids building a huge explicit response matrix, but it still increases demands on simulation support, training and validation. The exact energy convention matters, and I give it in backup.

Sources:

- [docs/analysis-note/sec_3d.tex](../../docs/analysis-note/sec_3d.tex)
- [docs/analysis-note/sec_eavailw.tex](../../docs/analysis-note/sec_eavailw.tex)

## Slide 10: Hadronic energy reveals model differences

**09:51–11:05 (74 seconds)**

The three-dimensional result preserves the overall normalization of the two-dimensional anchor and recovers the tested injected available-energy shape. Here the spectrum shows how generator predictions separate once we examine the hadronic energy. Monte Carlo means simulation using random sampling. A generator is a Monte Carlo model of the neutrino interaction and final-state particles. GENIE, NuWro and GiBUU implement different physics assumptions, while MINERvA Tune v1 applies experiment-specific weights to the reference GENIE simulation.

The low-energy deficit is related to the familiar two-particle–two-hole contribution, abbreviated two p two h: an interaction involving a pair of nucleons that leaves two holes in the nuclear state. Adding the Valencia model fills 52 percent of the gap below 0.4 GeV in this comparison. That is descriptive evidence about the central spectra, not proof of a unique mechanism or a significance. The older three-dimensional covariance-derived significances are quarantined. The energy definition also differs from some published low-recoil measurements, which limits direct comparisons.

Sources:

- [3d-unfolding/3D_OMNIFOLD_STATUS.md](../../3d-unfolding/3D_OMNIFOLD_STATUS.md)
- [VALIDATION_LEDGER.md: VL159–VL160](../../VALIDATION_LEDGER.md)
- [docs/analysis-note/figures/generators_vs_unfolded_band_central.pdf](../../docs/analysis-note/figures/generators_vs_unfolded_band_central.pdf)

## Slide 11: The 5D projection locates a high-energy difference

**11:05–12:08 (63 seconds)**

Projecting the five-coordinate result onto available energy and W shows where the nominal unfolded spectrum differs from the tuned prior. A projection means integrating or summing over the other coordinates. The prior is the simulated distribution we start from. Much of the positive difference lies at high available energy and high inferred hadronic mass.

That is an interesting place to investigate deep-inelastic modeling, but I would not claim that the map identifies the physical cause. This is also where later tests found large regularization effects. Regularization is the restriction imposed by finite iteration count and learner capacity: it stabilizes the inverse problem while potentially retaining dependence on the starting model. The dimensional anchors and earlier closures still stand, but they do not establish an uncertainty or a local significance for this feature.

Sources:

- [docs/analysis-note/sec_eavailw.tex](../../docs/analysis-note/sec_eavailw.tex)
- [docs/analysis-note/figures/paper_fig2_joint.pdf](../../docs/analysis-note/figures/paper_fig2_joint.pdf)
- [VALIDATION_LEDGER.md: VL149–VL152](../../VALIDATION_LEDGER.md)

## Slide 12: Extending the domain increases reliance on simulation

**12:08–13:13 (65 seconds)**

The extended-fiducial study asks what happens if we remove the truth-level muon kinematic restrictions while keeping the reconstructed selection. It is still an interaction in the tracker volume, not unrestricted neutrino phase space. Efficiency is the fraction of true events that become selected reconstructed events. The map shows a substantial region where that fraction is nearly zero. About 27.7 percent of the weighted true rate lies below two percent efficiency.

In those regions the result relies heavily on extrapolating the missed-event weights from simulation. The published subdomain remains well anchored, and finite closure and three-prior comparisons provide useful diagnostics. But three priors do not bound all possible model dependence. One historical NuWro-shaped prior also predates the flux repair. There is no corrected covariance for this enlarged domain, so its result is preliminary central-value and validation information.

Sources:

- [docs/analysis-note/sec_fps.tex](../../docs/analysis-note/sec_fps.tex)
- [docs/analysis-note/figures/fps_acceptance_MEFHC.pdf](../../docs/analysis-note/figures/fps_acceptance_MEFHC.pdf)

## Slide 13: The adopted 5D covariance carries four measurements

**13:13–14:42 (89 seconds)**

I adopted one specific five-dimensional covariance product under an explicit exception. That decision carries four measurements, which are part of the result. A seed fixes a pseudo-random sequence used by training. First, changing the estimator’s random seed moves a projected uncertainty width by as much as 6.145 percent, above the five percent limit. This statistic measures changes in square roots of projected variances, including correlations. Second, the effect remains about six percent across the tested 40, 80 and 160 throws. The smaller samples are nested subsets of one ensemble at one seed pair.

Larger ensembles and the distribution over seed pairs remain unmeasured. In contrast, the resampling control falls from 20.91 to 7.57 percent between 40 and 80. Third, five bands keep a fixed seed. They account for 6.75 percent of the covariance trace, the sum of bin variances, or 26 percent of its square-root trace scale. Their unmeasured contribution could move the result either way. Fourth, the seed also moves central values: at most 6.02 percent of the projected uncertainty, but as much as 49.8 percent for individual five-dimensional bins. Adoption did not convert the product’s failed criteria into passes.

Sources:

- [docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md: §4](../../docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md)
- [docs/orchestration/CORRECTION-20260921-seed-effect-larger-ensemble-corollary-withdrawn.md](../../docs/orchestration/CORRECTION-20260921-seed-effect-larger-ensemble-corollary-withdrawn.md)
- [docs/orchestration/CORRECTION-20260920-lower-bound-inference-withdrawn.md](../../docs/orchestration/CORRECTION-20260920-lower-bound-inference-withdrawn.md)

## Slide 14: The scalar campaigns exposed two distinct biases

**14:42–16:04 (82 seconds)**

The later scalar campaigns are important because they test things the early injected-feature closures did not. The s5c study found a bias from the binned purity background treatment in nominal pseudo-experiments, meaning a systematic displacement of the estimate from truth, reaching about four percent in the highest-W column. Purity is the estimated signal fraction in a detector bin, used to downweight data. The s5n study explored a refined alternative based on signed background subtraction. It improved that problem but exposed a much larger issue under generator-sized truth changes: residuals reached about 74 percent in some tested cells, and signal-only controls reproduced the departure failure.

The s5e diagnosis identified insufficient refinement-classifier capacity as a cause of the remaining nominal background bias. Increasing that capacity produced candidate R and repaired that specific bias on fresh tests. It did not fix the large truth-departure residuals, and R failed its real-data numerical-stability criterion. These are measured simulation failures and method sensitivities, not measurements of the real data’s bias. None of these campaigns adopted a replacement estimator or total covariance.

Sources:

- [VALIDATION_LEDGER.md: VL149–VL152](../../VALIDATION_LEDGER.md)
- [docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md](../../docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md)

## Slide 15: A calibrated model test answers a narrower question

**16:04–17:25 (81 seconds)**

The next campaign, s5p, tested whether any permitted reporting choice could provide a useful five-dimensional measurement with defensible total uncertainties. That measurement branch was not admitted. Instead, a separately authorized inference branch asked a narrower question. Suppose a particular generator’s fine-grid cross section were true, with specified assumptions below that grid and for the detector. How often would the complete estimation procedure produce a discrepancy as large as the observed one? That assumption is the null hypothesis.

Here the hybrid null combines the generator’s fine-cell rates and finite-sample fluctuations with MINERvA Tune’s shapes below the grid. We simulate pseudo-experiments under it, including the declared nuisance variations. A nuisance parameter describes an uncertain ingredient such as an energy response or interaction-model parameter. We then calibrate the comparison statistic empirically. The p-value is the probability, under that specific null, of a statistic at least as extreme as observed. It is not the probability that the generator is true. This route can account for an estimator’s modeled bias without turning its output into a qualified cross-section measurement.

Sources:

- [docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md](../../docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md)
- [docs/orchestration/RECORD-20260927-s5p-stage2-exit.md](../../docs/orchestration/RECORD-20260927-s5p-stage2-exit.md)
- [docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md](../../docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md)

## Slide 16: All ten tests reject their specified hybrid nulls

**17:25–18:46 (81 seconds)**

Under these six conditions, all ten tests reject their specified nulls: five predictions, each tested for total rate and shape. Shape means comparing distributions after removing their overall normalization. The predictions are MINERvA Tune v1, GENIE 2.12.10 with and without the Valencia two-nucleon component, NuWro 21.09 and GiBUU 2019. The familywise five percent threshold controls the chance of at least one false rejection across the declared family, under the calibration assumptions. Holm’s procedure adjusts the thresholds for the multiple comparisons. The conditions stay attached to that claim. The null assumes sub-grid shapes that have not converged under refinement.

Detector coverage is incomplete, especially for recoil energy. Interaction-model variations use the declared bands and clipping. The toys use less simulation than the data fit, with a measured correction variant. GiBUU has a restricted energy domain. All generators have finite simulation uncertainty. Independent recomputation agrees with the calculation, not the adequacy of every assumption. Recovered time-limited draws leave the decisions unchanged, with their margins disclosed. Monte Carlo p-values have finite resolution and are never zero.

Sources:

- [docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md: §3](../../docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md)
- [docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md: §1](../../docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md)
- [docs/publication/CLAIMS-20261005-claim-to-evidence.md: §§E–F](../../docs/publication/CLAIMS-20261005-claim-to-evidence.md)

## Slide 17: The inference has useful, measured limits

**18:46–19:53 (67 seconds)**

Several follow-ups tell us how far to take that inference. Kappa multiplies the change measured in the last grid-refinement step. Along that one direction, all ten decisions remain determinate to about 5.25 in the frozen ensembles. This is a sensitivity scan, not a measurement or bound on the actual unresolved sub-grid error. An exploratory coherent four percent shift of the data-side hadronic energy also does not remove the rejections.

It does not vary the null response or cover species dependence, resolution, or larger changes. A matched lower-dimensional comparison does not support a qualified claim that the joint test adds power beyond its coarse projections. In particular, the matched muon-only projection does not reject GENIE CV, so hadronic information matters for that comparison. The conditions on the preceding slide remain in force. Neither these tests nor independent arithmetic checks establish complete hadronic-response modeling.

Sources:

- [publication/kappa/RECORD-20261008-kappa-breakdown.md](../../publication/kappa/RECORD-20261008-kappa-breakdown.md)
- [publication/w2/W2B-REPORT-20261006.md](../../publication/w2/W2B-REPORT-20261006.md)
- [docs/publication/CLAIMS-20261005-claim-to-evidence.md: §§D–F](../../docs/publication/CLAIMS-20261005-claim-to-evidence.md)

## Slide 18: PET gives OmniFold a set of objects per event

**19:53–21:04 (71 seconds)**

The other major direction is PET, the point-cloud transformer used in OmniLearn. Instead of summarizing each event only by a few scalar quantities, it receives a set of detector deposits or simulated particles. A token is one object’s numerical representation. Attention is the learned operation that lets each object use information from the other objects. A point cloud is an unordered set, so the representation should not depend on an arbitrary input ordering. The historical recoil-only cross-check omitted the muon from classifier inputs.

The later full-event candidate adds a distinguished muon event input that conditions the transformer. These are different estimators. The stored clouds are energy-ranked and truncated to twelve objects. Detector events often contain far more deposits, so this discards meaningful information. That observation motivated detector energy summaries and comparisons of pooled versus individual object representations. The schematic is a representation diagram, not a display of one measured event.

Sources:

- [docs/analysis-note/sec_pet.tex](../../docs/analysis-note/sec_pet.tex)

## Slide 19: The earlier PET covariance did not qualify

**21:04–22:10 (66 seconds)**

The full-event covariance work reached an important stopping point in August. A fifty-member partial statistical covariance exists, but the independent construction check and central pairing were not established. I declined the pairing and demoted PET to diagnostic work. The nominal point estimate lies outside its bootstrap family in a spatially organized way. A bootstrap repeats an analysis after randomly resampling the events, to estimate sampling variation.

The observed mismatch is real, but the named bootstrap-centering and bias explanations were not established as its mechanism. The machine-learning covariance, meaning the covariance associated with training variability, was also not constructed, and its gate remains blocked. The later PET studies therefore start from a method-development question. They cannot inherit a publication uncertainty claim from the existence of that earlier artifact. Reconsidering the pairing would require estimator equivalence and separate coverage evidence.

Sources:

- [docs/analysis-note/sec_pet.tex](../../docs/analysis-note/sec_pet.tex)
- [VALIDATION_LEDGER.md: VL132](../../VALIDATION_LEDGER.md)
- [docs/OPEN_ITEMS.md: OI-126](../../docs/OPEN_ITEMS.md)
- [docs/orchestration/state/gate6-member-trajectories-result-56847059.json](../../docs/orchestration/state/gate6-member-trajectories-result-56847059.json)

## Slide 20: PET recovery improved substantially in simulation

**22:10–23:21 (71 seconds)**

The September studies asked whether representation and training changes could improve recovery. We score normalized histograms using one minus the absolute distance between unfolded and target distributions divided by the prior’s distance from that target. That is R: one is exact recovery, zero means no improvement on the prior, and a negative value means moving farther away. The initial improvement study found gains from detector summaries, categorical particle identity and an efficiency-corrected truth step, but no frozen configuration passed both accuracy and stress requirements.

The final-design study added longer truth-step training and better seed stability. On sixty final-bank draws of the available-energy tilt, the compact hybrid reaches 0.895 and the larger hybrid 0.863, versus 0.306 for the historical control. Those are substantial point-estimate gains. The banks are fixed finite simulation samples, and the study is signal-only. These results do not establish a universal architecture ranking, real-data performance or calibrated uncertainty.

Sources:

- [nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md](../../nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md)
- [docs/analysis-note/sec_pet_campaigns.tex](../../docs/analysis-note/sec_pet_campaigns.tex)
- [VALIDATION_LEDGER.md: VL164–VL167](../../VALIDATION_LEDGER.md)

## Slide 21: PET intervals fail differently across acceptance regions

**23:21–24:37 (76 seconds)**

The uncertainty test changes the conclusion. Each compact-finalist estimate averages six bootstrap members, and the declared interval uses their spread. On 120 final-bank simulated draws, intervals labeled 68 percent contain truth 89.6 percent of the time in the aggregate available-energy histogram. Those aggregate intervals are too wide under the frozen criterion. But in the low-acceptance region, the same nominal 68 percent intervals cover only 25.7 percent, and nominal 95 percent intervals cover 78.9 percent.

So this is not uniform conservatism. Acceptance is the probability that an event enters the selected sample, and the weakly observed region behaves very differently. The compact point estimator passes its accuracy, robustness and stability rules, but its interval construction fails calibration. The larger finalist fails a separate neutron-distortion point rule, with an unresolved statistical comparison around the threshold. The terminal outcome is no eligible design and no selected default. It does not mean neither point estimator is useful, and it does not authorize another round of repair.

Sources:

- [nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md](../../nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md)
- [docs/analysis-note/sec_pet_campaigns.tex](../../docs/analysis-note/sec_pet_campaigns.tex)

## Slide 22: The paired PET–tree comparison depends on the distortion

**24:37–25:51 (74 seconds)**

We also fitted a scalar histogram-gradient-boosting comparator to the same event samples, targets and distortions. Pairing means comparing methods on identical draws, which removes much of the variation from using different pseudo-data. PET does better on the available-energy tilt, with recovery gains of 0.102 and 0.070 for the two finalists. The broader distortion library changes the ordering: the tree method performs better on all three tested generator reweightings and on a narrow energy bump.

Some proton-content differences shrink or reverse when the tree iteration count changes. Those generator tests reweight a fixed detector simulation; they are not independent detector simulations. This comparison is exploratory because the PET final results had already been examined, and its intervals are not adjusted for the number of comparisons. There is no tree uncertainty procedure to compare, and PET’s own procedure failed. The useful conclusion is that representation helps some departures and loses on others, rather than that one method wins generally.

Sources:

- [docs/analysis-note/sec_pet_campaigns.tex](../../docs/analysis-note/sec_pet_campaigns.tex)
- [VALIDATION_LEDGER.md: VL168](../../VALIDATION_LEDGER.md)

## Slide 23: Reproducibility became part of the research

**25:51–26:57 (66 seconds)**

One contribution that is easy to miss in the note’s physics narrative is the infrastructure needed to trust these results. We found that a hardcoded import path could execute modules from a different checkout even while the pinned files passed hash comparisons. That is why guarded execution checks actual provenance, not just a job’s successful exit. A hash identifies file bytes; it does not establish which code ran or whether a scientific criterion is adequate.

Similarly, independent numerical recomputation is stronger than two workers repeating a shared summary, but it still checks a defined calculation. The bounded campaigns also taught us to preserve a terminal failure instead of selecting a better-looking iteration after inspection. We now have the note, primer, article and scoped replay materials. Replaying saved sufficient products is distinct from regenerating the full training and pseudo-experiment pipeline.

Sources:

- [docs/OPEN_ITEMS.md: OI-136](../../docs/OPEN_ITEMS.md)
- [docs/orchestration/CAMPAIGN-REVIEW-20260929.md](../../docs/orchestration/CAMPAIGN-REVIEW-20260929.md)
- [docs/publication/submission/PACKAGE-MANIFEST-20261006.md](../../docs/publication/submission/PACKAGE-MANIFEST-20261006.md)
- [reproduction/s5p/README.md](../../reproduction/s5p/README.md)

## Slide 24: Discussion with Ben

**26:57–28:00 (63 seconds)**

The article package is assembled for review, with the validation results and limits stated explicitly. It has not been submitted, deposited or sent to coauthors. Its readiness is assessed separately from s5p’s unmet precision-measurement objective. The reviewed successor proposal recommends stopping immediate measurement production and first checking whether the existing two-dimensional central estimator and uncertainty recipe can be made consistently matched.

Narrowing the measurement scope would itself need a scientific decision. For PET, the point-estimate improvements are worth understanding, while interval calibration is a separate problem. The questions I would like to discuss are which scientific result should lead the paper and which next validation would most improve its credibility. My preference is to resolve those questions before committing to another large campaign. [Pause here for two minutes of discussion.]

Sources:

- [docs/publication/submission/PACKAGE-MANIFEST-20261006.md](../../docs/publication/submission/PACKAGE-MANIFEST-20261006.md)
- [docs/orchestration/PROPOSAL-20261005-scalar-measurement-successor.md](../../docs/orchestration/PROPOSAL-20261005-scalar-measurement-successor.md)

## Backup B1: Backup: exact available-energy convention

**Optional, outside the timed talk**

ECAL means electromagnetic calorimeter. A blob is a reconstructed aggregate of detector energy. Muon fuzz is energy associated with the muon’s nearby deposits and subtracted from the recoil estimate. No final nonnegative clamp is applied to the reconstructed quantity.

The truth definition excludes secondary electrons, neutrons, kaons and other species not explicitly listed. The charged-pion subtraction uses 135 MeV rather than about 139.57 MeV. The effect has been measured, but its materiality against the adopted 5D projection is not established. There is no universal published available-energy convention. Do not describe this implementation as generically matching all low-recoil publications.

Sources:

- [docs/analysis-note/sec_3d.tex: operational definition](../../docs/analysis-note/sec_3d.tex)

## Backup B2: Backup: q3 and W are inferred kinematic quantities

**Optional, outside the timed talk**

At reconstruction level q zero comes from calorimetry and Q squared combines that energy estimate with the muon kinematics. M is the nucleon mass used in the estimator.

These expressions motivate the variables, but nuclear motion and reconstruction mean W is an operational experimenter’s quantity, not a complete measurement of every final-state particle’s invariant mass. Quasielastic scattering, baryon resonances and deep-inelastic interactions populate different regions without forming perfectly separated event classes. The quantities are correlated and change under lateral systematics, which shift event coordinates rather than only their weights.

Sources:

- [docs/analysis-note/sec_3d.tex: fourth axis](../../docs/analysis-note/sec_3d.tex)
- [docs/analysis-note/sec_eavailw.tex: W as a fifth axis](../../docs/analysis-note/sec_eavailw.tex)

## Backup B3: Backup: the adopted covariance’s exact boundary

**Optional, outside the timed talk**

The full digest is 3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5. The projection digest begins 835828bf. Identity verification establishes which covariance was projected, not its statistical adequacy. The predeclaration ordering defect is ratified by exception, not cured, and no declared cause-3 boundary was evaluated by production.

The paired measurement products used for the seed comparison are different digests and are not separately adopted. Five pinned bands are BeamAngleX, BeamAngleY, MuonResolution, Muon_Energy_MINERvA and Muon_Energy_MINOS. Their seed effect is unprobed in either direction. See slide 13 for the mandatory numerical measurements and their finite-ensemble scope.

Sources:

- [docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md](../../docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md)
- [docs/orchestration/OPERATIVE-SHEET-scalar5d.md](../../docs/orchestration/OPERATIVE-SHEET-scalar5d.md)

## Backup B4: Backup: reading the conditional p-values

**Optional, outside the timed talk**

These statistics belong only to the hybrid-null construction and the six conditions on slide 16. The frozen family has zero exceedances in nine tests and one in NuWro shape. Clopper–Pearson intervals are exact binomial confidence intervals for the exceedance probability. Determinacy requires those Monte Carlo intervals to resolve the decision relative to the multiple-testing threshold.

The lost-draw recovery is report-only. Four nulls would have stopped one batch earlier with complete batches, with the same decisions. The closest recovered margin is 4.6 statistic units for GENIE plus MEC shape at kappa three. Independent checks cover the frozen-shift reading; the union reading is a same-code consistency replay. A small conditional p-value does not identify a nuclear mechanism or localize a discrepancy.

Sources:

- [docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md](../../docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md)
- [docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md](../../docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md)

## Backup B5: Backup: the PET representation studies

**Optional, outside the timed talk**

Pooling summarizes several objects into one representation. Individual routing gives each object its own attention token. The synthetic comparison used a small fixed object fixture and cannot settle production-multiplicity performance. The production cap acts on generic calorimeter clusters, not simply a thin typed-object tail. Later hybrid designs use energy summaries to recover some omitted information.

PDG is the particle-identity code assigned by the Particle Data Group. One-hot encoding represents identity with separate category indicators rather than treating the code as a continuous number. PET2 is a tested pretrained model family. Pretraining means learning on another sample before this task. Its failure here applies to the tested recipes, not all possible pretraining. CPU–GPU optimizer differences were also investigated; numerical reproducibility does not establish physical accuracy.

Sources:

- [nd-unfolding/pet/direct_token_comparison/REPORT_FOR_BEN.md](../../nd-unfolding/pet/direct_token_comparison/REPORT_FOR_BEN.md)
- [nd-unfolding/pet/direct_token_comparison/GO_NO_GO-20260918.md](../../nd-unfolding/pet/direct_token_comparison/GO_NO_GO-20260918.md)
- [docs/analysis-note/sec_pet_campaigns.tex](../../docs/analysis-note/sec_pet_campaigns.tex)

## Backup B6: Backup: the closed scalar sequence

**Optional, outside the timed talk**

These labels identify successive bounded campaigns, not distinct published measurements. They are all terminal. The background repair is a causal diagnosis for one nominal-bias component. The physical truth-departure failure remains without a single established cause.

Reopening a closed study would require a new decision and contract. R is a targeted refinement change, not the production central-value estimator. A nominal-truth calibration check cannot establish performance over every alternative truth, and a pooled calibration result can hide individual functionals with poor coverage. A functional is any declared quantity extracted from the distribution, such as a bin, integral or projection.

Sources:

- [VALIDATION_LEDGER.md: VL149–VL155](../../VALIDATION_LEDGER.md)
- [docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md](../../docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md)
- [docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md](../../docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md)

## Backup B7: Backup: what the release can reproduce

**Optional, outside the timed talk**

Sufficient products are the stored quantities needed to recompute the reported inference without regenerating every event or training run. RC4 is a local release candidate, not a public deposit. Its scope excludes reproducing the 2D uncertainty, closure, bias, low-recoil, W2 and covariance-status numbers, as listed in its README.

Those results retain their own evidence routes. The article still needs author decisions and external-release actions, including coauthor review, deposit and submission. None of those acts is authorized by preparing this talk.

Sources:

- [docs/publication/submission/PACKAGE-MANIFEST-20261006.md](../../docs/publication/submission/PACKAGE-MANIFEST-20261006.md)
- [docs/publication/release/RC4-README.md](../../docs/publication/release/RC4-README.md)
- [reproduction/s5p/README.md](../../reproduction/s5p/README.md)

## Technical reference: The adopted 5D covariance carries four measurements

Expanded measurements for slide 13 (reference, not additional timed speech):
M1: The maximum fractional change in a declared projected uncertainty width is s_proj = 6.145%, above the 5% bound. The aggregate and median diagnostics are 0.471% and 0.485%. The comparison products are different from the adopted digest.
M2: s_proj is 6.02%, 6.02% and 6.145% on nested N = 40, 80 and 160 subsets at one seed pair. The same-seed resampling control falls from 20.91% to 7.57% between 40 and 80. The quoted 6.04% ± 0.39% summarizes subset scatter, not the width over seed pairs. Larger N and seed-pair width remain unmeasured.
M3: BeamAngleX, BeamAngleY, MuonResolution, Muon_Energy_MINERvA and Muon_Energy_MINOS remain at literal seed 42. These five of 45 bands carry 6.75% of covariance trace, or 26.0% of the square-root trace scale, and contribute zero seed movement by construction. Releasing their seeds could change the total statistic in either direction.
M4: On 43 projection functionals, central relative shifts have median 0.104% and maximum 0.761%, compared with median relative uncertainty 10.1%. In units of their own uncertainties the shifts have median 1.06%, maximum 6.02%, and total-rate movement 1.13%. Per individual 5D bin, median is 3.77%, 90th percentile 13.6%, maximum 49.8% of uncertainty. The same-seed control is 9.4e-13.

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
