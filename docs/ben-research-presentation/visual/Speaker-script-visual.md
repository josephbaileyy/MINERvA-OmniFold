# Visual presentation script

30 main slides, seven backups. Estimated 28-minute route plus two minutes for discussion.

Main snapshot: 3892e769043cddebfd58ec19e1ab1a567eb01784. XR interim snapshot: 9be8bfb4d4acace2ec64273970130d6404f1813c.

## Timed route

00:00–00:28  01. MINERvA OmniFold  
00:28–01:19  02. Reproduction, conditional inference and PET development  
01:19–02:10  03. The selected neutrino sample and its truth domain  
02:10–03:21  04. Closure, dimensional anchors and coverage  
03:21–04:12  05. The 2D central result reproduces the published scale  
04:12–05:07  06. Most iteration movement occurs before five iterations  
05:07–06:00  07. Closure passes depend on what the test changes  
06:00–07:03  08. XR reproduces both LightGBM reference centrals  
07:03–08:02  09. The repaired 2D band still needs a coverage test  
08:02–08:54  10. Added coordinates expose hadronic structure  
08:54–09:59  11. Reconstructed q3 and W share the same event inputs  
09:59–10:46  12. Hadronic energy reveals model differences  
10:46–11:38  13. The excess concentrates at high Eavail and high W  
11:38–12:22  14. Extending truth acceptance increases extrapolation  
12:22–13:40  15. The 5% bound limits seed-induced movement of error bars  
13:40–14:40  16. Four measurements accompany the adopted 5D covariance  
14:40–15:51  17. Purity weights and negative-weight subtraction  
15:51–16:56  18. Repairing background bias did not repair truth recovery  
16:56–17:48  19. A separate test asks whether specified models fit the data  
17:48–18:44  20. All ten specified joint-5D null hypotheses are rejected  
18:44–19:38  21. The rejection survives a bounded refinement stress test  
19:38–20:34  22. PET uses particle and detector-object structure  
20:34–21:39  23. The 12-token cap truncates reco clouds much more often  
21:39–22:28  24. The earlier PET central disagrees with its bootstrap family  
22:28–23:15  25. PET recovers more of the tested Eavail tilt  
23:15–24:21  26. Coverage counts intervals that contain the true bin value  
24:21–25:11  27. PET intervals over-cover overall and under-cover low acceptance  
25:11–26:04  28. PET gains depend on the tested departure  
26:04–26:48  29. Reproducibility and scientific validation answer different questions  
26:48–28:00  30. The next decision is what measurement claim can be supported  
## Slide 1: MINERvA OmniFold

**00:00–00:28 (28 seconds)**

Ben, this is the current state of the OmniFold analysis: a reproduced two-dimensional central result, higher-dimensional inference and validation limits, and full-event PET development. I will separate what the data show from what the uncertainty and calibration studies justify.

Sources:

- [docs/analysis-note/main_note.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/main_note.tex)
- [docs/publication/submission/PACKAGE-MANIFEST-20261006.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/publication/submission/PACKAGE-MANIFEST-20261006.md)

## Slide 2: Reproduction, conditional inference and PET development

**00:28–01:19 (51 seconds)**

The two-dimensional central result reproduces the published muon measurement. XR has now regenerated the LightGBM reference centrals at both seeds, which closes specific reproducibility questions. It does not yet establish that those error bars describe the quoted exact-tree central. The higher-dimensional program reveals hadronic structure and supports a conditional generator test, but did not qualify a joint-five-dimensional measurement. PET improves recovery of some simulated departures while its tested intervals remain miscalibrated. These are different scientific outcomes, and the plots will show both the achievements and the limits.

Sources:

- [2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md)
- [3d-unfolding/3D_OMNIFOLD_STATUS.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/3d-unfolding/3D_OMNIFOLD_STATUS.md)
- [docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md)
- [nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md)
- [docs/orchestration/ASSESSMENT-20261008-2d-estimator-pairing.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/ASSESSMENT-20261008-2d-estimator-pairing.md)
- [9be8bfb4d4acace2ec64273970130d6404f1813c:docs/orchestration/state/next-preparation-20261009/xr-linux/REPORT.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/9be8bfb4d4acace2ec64273970130d6404f1813c/docs/orchestration/state/next-preparation-20261009/xr-linux/REPORT.md)
- [9be8bfb4d4acace2ec64273970130d6404f1813c:docs/orchestration/state/next-preparation-20261009/xr-linux/logs/compare-interim-L1.json](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/9be8bfb4d4acace2ec64273970130d6404f1813c/docs/orchestration/state/next-preparation-20261009/xr-linux/logs/compare-interim-L1.json)

## Slide 3: The selected neutrino sample and its truth domain

**01:19–02:10 (51 seconds)**

We use about 4.12 million selected events from the twelve medium-energy neutrino-mode playlists. The signal is inclusive muon-neutrino charged-current scattering in the tracker. The reference truth domain has a forward muon within the published momentum cuts, and selected reconstruction includes a downstream MINOS match. Those are distinct definitions: a truth signal event can miss reconstructed selection. The extended-fiducial PET studies keep the reconstructed selection while enlarging the truth domain. The September PET selection studies are signal-only simulations on fixed banks, rather than a complete real-data background analysis.

Sources:

- [docs/analysis-note/sec_experiment.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_experiment.tex)
- [2d-unfolding/2D_OMNIFOLD_REFERENCE.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/2d-unfolding/2D_OMNIFOLD_REFERENCE.md)

## Slide 4: Closure, dimensional anchors and coverage

**02:10–03:21 (71 seconds)**

Your shorthand is useful: closure primarily tests the point-estimation procedure, and coverage tests the interval procedure. In closure we know the simulated truth, optionally deform it away from the starting simulation, then ask how accurately unfolding recovers it. A dimensional anchor instead integrates away an added observable and checks consistency with the earlier result. Coverage counts repeated experiments whose intervals contain the target bin value. It is not event classification. Bias in the central estimate can also spoil coverage, so the two tests are connected. Passing a few closures cannot establish coverage, and wide intervals can cover even a biased estimate. Every verdict needs its target, simulated response, departures and sample construction. The one-dimensional binned study was a completed equivalence and debugging check, not a separate publication result.

Sources:

- [docs/analysis-note/sec_validation.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_validation.tex)
- [docs/analysis-note/sec_3d.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_3d.tex)

## Slide 5: The 2D central result reproduces the published scale

**03:21–04:12 (51 seconds)**

The central result reproduces the published scale: the integrated cross section is 3.073 times ten to the minus 38 square centimetres per nucleon, 1.11 percent above the published total. This figure also shows the bin-by-bin agreement. It uses the same data and shares systematic sources with the publication, so this is a reproduction, not an independent measurement. The quoted central uses exact-split scikit-learn trees; the uncertainty ensembles use LightGBM. XR has now reproduced the LightGBM references, but their uncertainty transfer to the exact central remains unmeasured.

Sources:

- [2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md)
- [docs/analysis-note/figures/MEFHC_5iter_xsec_proj_pt.pdf](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/figures/MEFHC_5iter_xsec_proj_pt.pdf)
- [docs/analysis-note/sec_method.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_method.tex)
- [docs/analysis-note/figures/paper_fig1_validation.pdf](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/figures/paper_fig1_validation.pdf)

## Slide 6: Most iteration movement occurs before five iterations

**04:12–05:07 (55 seconds)**

This is the archived playlist-1A iteration scan, with each tree estimator compared to its own ten-iteration result. The exact-tree shape RMS falls from 5 percent at one iteration to 1.54 percent at five and 0.55 percent at eight. The histogram-tree version reaches 0.86 percent at five. Ten is the reference, so its zero is automatic. This supports five as a practical stopping choice, not proof that every bin has reached an unbiased limit. The reported five-to-ten total-cross-section change is only 0.026 percent. Iteration stability and closure ask different questions: a stable answer can still be biased.

Sources:

- [docs/analysis-note/sec_validation.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_validation.tex)
- [docs/analysis-note/sec_method.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_method.tex)
- [2d-unfolding/2D_OMNIFOLD_REFERENCE.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/2d-unfolding/2D_OMNIFOLD_REFERENCE.md)
- [evidence/prepublication-2026-08-20-0b329e8a:2d-unfolding/2D_OMNIFOLD_RUN_LOG_ARCHIVE.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/evidence/prepublication-2026-08-20-0b329e8a/2d-unfolding/2D_OMNIFOLD_RUN_LOG_ARCHIVE.md)
- [2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md)

## Slide 7: Closure passes depend on what the test changes

**05:07–06:00 (53 seconds)**

The easy truth deformations close very well: median residuals are 0.046 and 0.013 percent against a 1.5 percent limit. The more revealing test changes a hidden resolution variable, reconstructed minus truth transverse momentum. Its residual rises with the deformation, reaching 3.43 percent at amplitude 0.30 and exceeding the 3 percent criterion. These are playlist-1A, LightGBM, five-iteration tests. They validate the tested situations, not arbitrary detector errors. Missed events are a separate bookkeeping requirement: retaining truth events without selected reconstruction preserves the signal denominator, but cannot create data constraints in zero-acceptance regions.

Sources:

- [2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md)
- [docs/analysis-note/sec_validation.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_validation.tex)
- [docs/analysis-note/sec_method.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_method.tex)

## Slide 8: XR reproduces both LightGBM reference centrals

**06:00–07:03 (63 seconds)**

The newer XR record changes the previous presentation. The seed-42 run agrees with the systematic-sweep central to a maximum relative bin difference of 1.38 times ten to the minus eleven. Against the July background-aware central the difference is 9.81 times ten to the minus thirteen. The seed-one run reproduces its reference to 2.41 times ten to the minus twelve. All are below the frozen ten-to-the-minus-eight criterion in 205 cells. These are committed interim results, not the completed campaign review. The exact-tree reproduction and one-seed comparisons remain incomplete in that snapshot. Reproducing the LightGBM references establishes their provenance and reproducibility; it does not measure covariance transfer between LightGBM and the quoted exact-tree central.

Sources:

- [9be8bfb4d4acace2ec64273970130d6404f1813c:docs/orchestration/state/next-preparation-20261009/xr-linux/REPORT.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/9be8bfb4d4acace2ec64273970130d6404f1813c/docs/orchestration/state/next-preparation-20261009/xr-linux/REPORT.md)
- [9be8bfb4d4acace2ec64273970130d6404f1813c:docs/orchestration/state/next-preparation-20261009/xr-linux/logs/compare-interim-L1.json](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/9be8bfb4d4acace2ec64273970130d6404f1813c/docs/orchestration/state/next-preparation-20261009/xr-linux/logs/compare-interim-L1.json)

## Slide 9: The repaired 2D band still needs a coverage test

**07:03–08:02 (59 seconds)**

The old statistical band contained truth only 91.21 percent of the time for its nominal 95.45 percent intervals. Its 99.5 percent confidence interval lies wholly below the predeclared acceptable window, so this is a statistical failure rather than a demand for exactly 95 percent. Completeness was repaired in the adopted VL170 band, but that replacement has not received an independent coverage re-test. The October diagnostic supports under-scattering of same-event toys; it does not certify the real-data band. The later split-sample design supports conditional width agreement only, and finds the original objective infeasible under the current inputs. XR addresses reproduction, not this coverage question.

Sources:

- [VALIDATION_LEDGER.md: VL169–VL172](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/VALIDATION_LEDGER.md)
- [docs/analysis-note/sec_systematics.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_systematics.tex)
- [docs/analysis-note/sec_validation.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_validation.tex)
- [KNOWN_ISSUES.md: 84–85](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/KNOWN_ISSUES.md)
- [docs/orchestration/ASSESSMENT-20261008-2d-estimator-pairing.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/ASSESSMENT-20261008-2d-estimator-pairing.md)
- [docs/orchestration/state/ki85-diag-20261006/ki85_result.json](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/state/ki85-diag-20261006/ki85_result.json)
- [docs/orchestration/DELIVERY-20261008-uncertainty-preparation.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/DELIVERY-20261008-uncertainty-preparation.md)
- [docs/orchestration/state/next-preparation-20261009/two-d-path/REPORT.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/state/next-preparation-20261009/two-d-path/REPORT.md)
- [docs/orchestration/state/next-preparation-20261009/two-d-followup/REPORT.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/state/next-preparation-20261009/two-d-followup/REPORT.md)
- [9be8bfb4d4acace2ec64273970130d6404f1813c:docs/orchestration/state/next-preparation-20261009/xr-linux/REPORT.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/9be8bfb4d4acace2ec64273970130d6404f1813c/docs/orchestration/state/next-preparation-20261009/xr-linux/REPORT.md)
- [9be8bfb4d4acace2ec64273970130d6404f1813c:docs/orchestration/state/next-preparation-20261009/xr-linux/logs/compare-interim-L1.json](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/9be8bfb4d4acace2ec64273970130d6404f1813c/docs/orchestration/state/next-preparation-20261009/xr-linux/logs/compare-interim-L1.json)

## Slide 10: Added coordinates expose hadronic structure

**08:02–08:54 (52 seconds)**

The muon variables reproduce the established two-dimensional result. Available energy adds a species-defined visible-energy measurement, and the calorimetric energy transfer q-zero supplies additional reconstructed information. The derived variables q-three and W then express those inputs in useful interaction coordinates. Available energy excludes invisible outgoing neutrinos and also omits neutrons under the implemented convention; the incoming neutrino supplies energy rather than being an outgoing deposit. The key distinction is between a useful coordinate and a new independent observation. Five scalar inputs do not automatically mean five independent degrees of freedom.

Sources:

- [docs/analysis-note/sec_3d.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_3d.tex)
- [docs/analysis-note/sec_eavailw.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_eavailw.tex)
- [MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h)

## Slide 11: Reconstructed q3 and W share the same event inputs

**08:54–09:59 (65 seconds)**

Both quantities use the muon energy and direction and the same calorimetric q-zero. The neutrino-energy estimate is muon energy plus q-zero. From that we calculate Q-squared, then q-three and W using the displayed equations. In the physical interior, muon kinematics and q-three already determine q-zero, so adding reconstructed W supplies no independent detector measurement. It can still organize the interaction physics and help a finite learner by presenting a useful nonlinear transformation. That is why it is too strong to say we should expect nothing useful. Truth W uses a struck-nucleon mass and its own generator convention; exact identities between stored truth coordinates need those conventions checked. Clipping at the reconstruction boundaries can also break invertibility.

Sources:

- [MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h)
- [docs/analysis-note/sec_eavailw.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_eavailw.tex)

## Slide 12: Hadronic energy reveals model differences

**09:59–10:46 (47 seconds)**

Adding available energy preserves the lower-dimensional normalization and closes the injected available-energy shape. It also exposes model differences hidden by the muon projection. The measured spectrum is harder than several generator predictions. Valencia two-particle–two-hole strength fills 52 percent of the low-energy gap in this comparison, but that observation does not uniquely identify an interaction mechanism. These are central-value comparisons. The historical three-dimensional covariance significances remain withheld; the conditional joint-five-dimensional test later in the talk is a separate result.

Sources:

- [3d-unfolding/3D_OMNIFOLD_STATUS.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/3d-unfolding/3D_OMNIFOLD_STATUS.md)
- [VALIDATION_LEDGER.md: VL159–VL160](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/VALIDATION_LEDGER.md)
- [docs/analysis-note/figures/generators_vs_unfolded_band_central.pdf](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/figures/generators_vs_unfolded_band_central.pdf)

## Slide 13: The excess concentrates at high Eavail and high W

**10:46–11:38 (52 seconds)**

The E-avail versus W map localizes the difference from the MINERvA Tune prediction. Sixty-seven percent of this map’s positive excess lies above 0.8 GeV available energy, and 83 percent of that lies above W of 1.8 GeV. The largest cell contains 22 percent of the positive excess, partly because it spans a broad region. This is not a ranking of significance or fractional discrepancy across all variables. It suggests hadronic physics questions but does not isolate a cause; prior support, regularization and detector modelling can also affect the result.

Sources:

- [docs/analysis-note/sec_eavailw.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_eavailw.tex)
- [docs/analysis-note/figures/paper_fig2_joint.pdf](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/figures/paper_fig2_joint.pdf)
- [VALIDATION_LEDGER.md: VL149–VL152](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/VALIDATION_LEDGER.md)

## Slide 14: Extending truth acceptance increases extrapolation

**11:38–12:22 (44 seconds)**

Removing the truth-level muon cuts enlarges the signal domain while retaining reconstructed selection. The efficiency plot shows the consequence: about 27.7 percent of the weighted truth rate lies below two percent efficiency. Those regions rely heavily on simulation and extrapolation through missed events. The dimensional anchors and available-energy closure still pass, and the muon marginal is recovered, but these are central-value and prior tests. No corrected covariance was adopted for this extended-domain result.

Sources:

- [docs/analysis-note/sec_fps.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_fps.tex)
- [docs/analysis-note/figures/fps_acceptance_MEFHC.pdf](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/figures/fps_acceptance_MEFHC.pdf)

## Slide 15: The 5% bound limits seed-induced movement of error bars

**12:22–13:40 (78 seconds)**

The bound was a declared numerical-stability tolerance, motivated by the precision of a 160-throw estimate of a standard deviation. For independent Gaussian throws, the approximate relative standard error of a sample standard deviation is one over the square root of twice N minus one. At 160 this is about 5.61 percent. Five percent was chosen as a direct movement tolerance of roughly that scale. It is not a derived confidence threshold for a maximum over correlated projections. We compare the same nuisance throws under different estimator seeds and calculate each projected standard deviation. The largest relative width change is 6.145 percent, above five. If a reference width were ten units, that magnitude would mean a change of 0.6145 units, not a 6.145 percent shift in the cross section. A perfectly seed-invariant estimator would give zero; the tolerated value is at most five percent.

Sources:

- [docs/orchestration/AUTHORIZATION-20260918-d-resource-required-deliverable-path.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/AUTHORIZATION-20260918-d-resource-required-deliverable-path.md)
- [nd-unfolding/z_statistics.py](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/nd-unfolding/z_statistics.py)
- [docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md)

## Slide 16: Four measurements accompany the adopted 5D covariance

**13:40–14:40 (60 seconds)**

These four measurements travel with the adopted covariance. First, the largest projected-width movement is 6.145 percent against the five percent bound. Second, it stays near six percent across nested 40, 80 and 160 throw subsets at one seed pair, while the same-seed resampling floor falls. Larger ensembles and other seed pairs remain unmeasured. Third, five fixed-seed bands carry 6.75 percent of the trace; their seed effect is unprobed in either direction. Fourth, central values move by up to 6.02 percent of projected uncertainty and 49.8 percent of individual-bin uncertainty. The exception adopts specific bytes without changing their NON-PASSING status or computing the missing production criterion.

Sources:

- [docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md: §4](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md)
- [docs/orchestration/CORRECTION-20260921-seed-effect-larger-ensemble-corollary-withdrawn.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/CORRECTION-20260921-seed-effect-larger-ensemble-corollary-withdrawn.md)
- [docs/orchestration/CORRECTION-20260920-lower-bound-inference-withdrawn.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/CORRECTION-20260920-lower-bound-inference-withdrawn.md)
- [docs/orchestration/AUTHORIZATION-20260918-d-resource-required-deliverable-path.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/AUTHORIZATION-20260918-d-resource-required-deliverable-path.md)
- [docs/orchestration/PREREGISTRATION-20260919-cause3-two-member-campaign.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/PREREGISTRATION-20260919-cause3-two-member-campaign.md)

## Slide 17: Purity weights and negative-weight subtraction

**14:40–15:51 (71 seconds)**

The standard two-dimensional and scalar five-dimensional production chains use binned purity weights: all data events in a reconstructed bin receive the same nonnegative background correction. Negative-weight injection instead appends simulated background with negative weight and leaves data at positive one. The two constructions share bin totals when the floor is inactive, but they generally differ within bins. A synthetic example shows why: purity preserves the data shape, while pointwise subtraction removes the background shape. Signed injection is a comparison method, not the adopted standard chain. The later scalar diagnostic and inference candidates use a learned positive-weight refinement of the signed target, rather than feeding raw signed weights to the final classifier. The refinement can itself underfit. Clipped negative GENIE systematic weights in the inference calibration are a different operation.

Sources:

- [docs/analysis-note/app_negweight.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/app_negweight.tex)
- [docs/analysis-note/sec_method.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_method.tex)
- [docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md)
- [docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md)

## Slide 18: Repairing background bias did not repair truth recovery

**15:51–16:56 (65 seconds)**

The nominal background bias was traced to an underpowered positive-weight refinement classifier. Increasing it from 100 trees and eight leaves to 400 trees and 31 leaves reduced that paired bias by more than 80 percent in every worst cell, with a median reduction of 93 percent. But the physical truth-departure residuals barely changed: the largest E-avail residual remained about 74 percent. They also persist in signal-only tests, so negative weights cannot explain the entire failure. Candidate R subsequently failed the real-data numerical-stability criterion. These studies identify one repairable approximation and a distinct unresolved recovery limitation. They do not show that correct background subtraction is intrinsically biased or establish the generator as the unique source of the discrepancy.

Sources:

- [VALIDATION_LEDGER.md: VL149–VL152](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/VALIDATION_LEDGER.md)
- [docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md)
- [docs/orchestration/state/next-preparation-20261009/d-id/REPORT.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/state/next-preparation-20261009/d-id/REPORT.md)

## Slide 19: A separate test asks whether specified models fit the data

**16:56–17:48 (52 seconds)**

The joint-five-dimensional measurement branch did not qualify, so a separately authorized branch tested specified generator hypotheses. Each null includes generator fine-cell rates, an imposed within-cell distribution, and a detector and nuisance model. Repeated simulated experiments calibrate the same test statistic used on data. The unfolding still uses unbinned events; the hypothesis and statistic use a finite grid to make the null and calibration explicit. An unbinned test is possible in principle, but would need its own calibration. This inference supplies neither a new measured cross section nor a reportable uncertainty.

Sources:

- [docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md)
- [docs/orchestration/RECORD-20260927-s5p-stage2-exit.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/RECORD-20260927-s5p-stage2-exit.md)
- [docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md)

## Slide 20: All ten specified joint-5D null hypotheses are rejected

**17:48–18:44 (56 seconds)**

All five predictions are rejected in both total and shape tests after Holm correction across the ten hypotheses. Total retains normalization; shape removes it. The familywise five percent level controls false rejections across this stated family. That is the same multiple-opportunity principle as the look-elsewhere effect, though this is a fixed family rather than a continuous bump scan. The rejection applies to the full hybrid null. The six conditions displayed alongside it restrict its interpretation. Independent recomputation agrees on the calculation; it does not establish every calibration assumption. Monte Carlo p-values have finite resolution and are never zero.

Sources:

- [docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md: §3](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md)
- [docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md: §1](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md)
- [docs/publication/CLAIMS-20261005-claim-to-evidence.md: §§E–F](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/publication/CLAIMS-20261005-claim-to-evidence.md)

## Slide 21: The rejection survives a bounded refinement stress test

**18:44–19:38 (54 seconds)**

Refinement splits truth cells to test sensitivity to the imposed within-cell shape. Kappa scales the last observed change: two is the primary test and three the robustness check. There is no universal typical kappa or confidence-level interpretation. In frozen ensembles, the first loss of determinate rejection is around 5.25; recovered draws shift it to about 5.17. That is not determinate acceptance, and the grid has not converged. The matched coarse muon-only comparison does not reject GENIE CV. This post-hoc comparison supports the relevance of joint hadronic information without establishing a universal power advantage.

Sources:

- [publication/kappa/RECORD-20261008-kappa-breakdown.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/publication/kappa/RECORD-20261008-kappa-breakdown.md)
- [publication/w2/W2B-REPORT-20261006.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/publication/w2/W2B-REPORT-20261006.md)
- [docs/publication/CLAIMS-20261005-claim-to-evidence.md: §§D–F](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/publication/CLAIMS-20261005-claim-to-evidence.md)

## Slide 22: PET uses particle and detector-object structure

**19:38–20:34 (56 seconds)**

PET receives sets of objects rather than only scalar summaries. This archived event display places truth hadrons, reconstructed recoil clusters and the muon on a common energy-angle plane. Detector clusters are not individual reconstructed hadrons: a single particle can produce many deposits. The original recoil-cloud representation gives the muon separately as event-level features; the later full-event models incorporate aligned event scalars. The plot uses a nominal vertex to illustrate cluster angle, while the model consumes the stored view and position features. PET can learn relationships among objects, but more tokens do not automatically produce more independently measurable physics.

Sources:

- [docs/analysis-note/sec_pet.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_pet.tex)
- [docs/analysis-note/figures/pet_event_displays_energy_angle.pdf](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/figures/pet_event_displays_energy_angle.pdf)

## Slide 23: The 12-token cap truncates reco clouds much more often

**20:34–21:39 (65 seconds)**

This is the actual cardinality distribution after truncation. Truth clouds are relatively sparse, with mean 4.57 including nuclear-remnant bookkeeping particles. Only 2.31 percent reach twelve. Reconstructed clusters pile up strongly at the cap, because a hadron can leave many deposits. The twelfth truth constituent carries 0.09 percent of retained truth energy on average, but that is neither the total discarded energy nor a bound on lost reconstruction information. Twelve was a compute and memory choice, not the winner of a controlled cap scan. Attention pair costs grow roughly quadratically with token count, although total training cost has other terms. The correct conclusion is that the optimal cap and the effect of discarded structure remain unmeasured.

Sources:

- [docs/analysis-note/sec_pet.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_pet.tex)
- [docs/analysis-note/figures/pet_cardinality_withremnant.pdf](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/figures/pet_cardinality_withremnant.pdf)

## Slide 24: The earlier PET central disagrees with its bootstrap family

**21:39–22:28 (49 seconds)**

The earlier PET nominal and its bootstrap family disagree locally. On 257 common cells, the width-weighted total ratio is 1.1027, while the median cell ratio is only 1.0003. Sixty-three cells have nominal-to-mean ratio above 1.5; in 44 of those, nominal is above all fifty replicas. This localized anomaly motivated declining the central/statistical pairing. Its mechanism remains unresolved, and the covariance construction lacks independent verification. No full-event PET total covariance or ML covariance was adopted. The later PET studies therefore focus on method development.

Sources:

- [docs/analysis-note/sec_pet.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_pet.tex)
- [VALIDATION_LEDGER.md: VL132](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/VALIDATION_LEDGER.md)
- [docs/OPEN_ITEMS.md: OI-126](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/OPEN_ITEMS.md)
- [docs/orchestration/state/gate6-member-trajectories-result-56847059.json](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/state/gate6-member-trajectories-result-56847059.json)
- [docs/orchestration/state/RECEIPT-20260815-cstat-tail-geometry-and-weighting-correction.json](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/state/RECEIPT-20260815-cstat-tail-geometry-and-weighting-correction.json)

## Slide 25: PET recovers more of the tested Eavail tilt

**22:28–23:15 (47 seconds)**

The final-bank available-energy tilt measures recovery with R: one means the injected change is recovered, and zero means the prior discrepancy remains. The historical control reaches 0.306, the compact hybrid 0.895, and the larger hybrid 0.863. These are substantial improvements on that tested departure. The full selection study also required accuracy and stress performance, and no design passed every requirement. It used signal-only simulated banks. This plot establishes neither a universal architecture ranking nor a calibrated real-data cross-section measurement.

Sources:

- [nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md)
- [docs/analysis-note/sec_pet_campaigns.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_pet_campaigns.tex)
- [VALIDATION_LEDGER.md: VL164–VL167](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/VALIDATION_LEDGER.md)

## Slide 26: Coverage counts intervals that contain the true bin value

**23:15–24:21 (66 seconds)**

These are deliberately synthetic histograms, to isolate the idea. The true value in the highlighted bin is 80. Experiment A estimates 84 with an interval from 76 to 92, which contains 80. Experiment B estimates 90 with an interval from 84 to 96, which misses it. Repeat the whole procedure on many experiments and count the containing intervals for that target. A nominal 68 percent procedure aims to contain the target 68 percent of the time under the declared experiment model. It is not a statement that 68 percent of events are truth-like. The next slide shows the actual PET study, whose target is the known truth-bin value for each simulated draw and whose reported entries pool bin-draw checks.

Sources:

- [nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md)
- [docs/analysis-note/sec_pet_campaigns.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_pet_campaigns.tex)

## Slide 27: PET intervals over-cover overall and under-cover low acceptance

**24:21–25:11 (50 seconds)**

Here are the measured coverage fractions, pooled over bin-draw checks in 120 simulated experiments. The nominal 68 percent intervals contain truth 89.6 percent of the time in aggregate, but only 25.7 percent in low acceptance. The 95 percent intervals also under-cover there, at 78.9 percent. Moderate and good acceptance behave differently. A common rescaling cannot fix both broad aggregate intervals and the narrow low-acceptance intervals. These are intervals for truth-bin values, not event classifications or simultaneous coverage of all bins. No eligible design was selected.

Sources:

- [nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md)
- [docs/analysis-note/sec_pet_campaigns.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_pet_campaigns.tex)

## Slide 28: PET gains depend on the tested departure

**25:11–26:04 (53 seconds)**

The matched comparison uses identical simulated events and declared truth deformations. PET improves recovery of the available-energy tilt; trees do better on the NuWro, NuWro-prime and GiBUU reweightings, which retain the same detector simulation. The compact and larger PET finalists cost median 1.768 and 1.517 A100-hours per unfolding at study scale. The tree campaign used 5.306 charged CPU-core-hours across 352 tasks plus a control and retries. Those are different hardware and workload units, so they do not yield a clean speedup factor. The conclusion depends on the departure and training configuration.

Sources:

- [docs/analysis-note/sec_pet_campaigns.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_pet_campaigns.tex)
- [VALIDATION_LEDGER.md: VL168](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/VALIDATION_LEDGER.md)
- [nd-unfolding/pet/gbdt_comparison/REPORT-20261005.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/nd-unfolding/pet/gbdt_comparison/REPORT-20261005.md)
- [nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md)

## Slide 29: Reproducibility and scientific validation answer different questions

**26:04–26:48 (44 seconds)**

Reproducibility work distinguishes execution integrity, numerical agreement and scientific validation. An import-path defect once caused a different checkout’s code to run despite matching file hashes. XR now answers specific numerical-reproduction questions for the LightGBM centrals. Closure and coverage answer different questions about recovery and calibration. No result becomes scientifically validated just because several people repeat the same calculation. The note, primer, paper and replay materials should preserve those distinctions when they quote results.

Sources:

- [docs/OPEN_ITEMS.md: OI-136](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/OPEN_ITEMS.md)
- [docs/orchestration/CAMPAIGN-REVIEW-20260929.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/CAMPAIGN-REVIEW-20260929.md)
- [docs/publication/submission/PACKAGE-MANIFEST-20261006.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/publication/submission/PACKAGE-MANIFEST-20261006.md)
- [reproduction/s5p/README.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/reproduction/s5p/README.md)

## Slide 30: The next decision is what measurement claim can be supported

**26:48–28:00 (72 seconds)**

The article is assembled but not submitted, and the remaining scientific choices are consequential. XR now establishes reproduction of the LightGBM reference centrals. The exact-tree comparisons are not complete in the inspected committed snapshot, and covariance transfer remains unmeasured. Coverage of the corrected statistical band also remains open. The proposed matched-LightGBM route would narrow the claim to conditional precision and nuisance propagation; it is not an adopted replacement or an empirical total-coverage result. For higher dimensions, the most useful existing result is the conditional generator test and the diagnosis of why a measurement did not qualify. For PET, the next design would need to connect better recovery, low-acceptance calibration and representation choices such as the token cap. These are the decisions I would like to discuss with Ben.

Sources:

- [docs/publication/submission/PACKAGE-MANIFEST-20261006.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/publication/submission/PACKAGE-MANIFEST-20261006.md)
- [docs/orchestration/PROPOSAL-20261005-scalar-measurement-successor.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/PROPOSAL-20261005-scalar-measurement-successor.md)
- [docs/orchestration/state/next-preparation-20261009/closeout/REPORT.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/state/next-preparation-20261009/closeout/REPORT.md)
- [docs/orchestration/state/next-preparation-20261009/two-d-path/REPORT.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/state/next-preparation-20261009/two-d-path/REPORT.md)
- [9be8bfb4d4acace2ec64273970130d6404f1813c:docs/orchestration/state/next-preparation-20261009/xr-linux/REPORT.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/9be8bfb4d4acace2ec64273970130d6404f1813c/docs/orchestration/state/next-preparation-20261009/xr-linux/REPORT.md)
- [9be8bfb4d4acace2ec64273970130d6404f1813c:docs/orchestration/state/next-preparation-20261009/xr-linux/logs/compare-interim-L1.json](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/9be8bfb4d4acace2ec64273970130d6404f1813c/docs/orchestration/state/next-preparation-20261009/xr-linux/logs/compare-interim-L1.json)
- [docs/orchestration/state/next-preparation-20261009/two-d-followup/REPORT.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/state/next-preparation-20261009/two-d-followup/REPORT.md)

## Backup B1: exact available-energy convention

**Optional, outside the timed talk**

ECAL means electromagnetic calorimeter. A blob is a reconstructed aggregate of detector energy. Muon fuzz is energy associated with the muon’s nearby deposits and subtracted from the recoil estimate. No final nonnegative clamp is applied to the reconstructed quantity. The truth definition excludes secondary electrons, neutrons, kaons and other species not explicitly listed. The charged-pion subtraction uses 135 MeV rather than about 139.57 MeV. The effect has been measured, but its materiality against the adopted 5D projection is not established. There is no universal published available-energy convention. Do not describe this implementation as generically matching all low-recoil publications.

Sources:

- [docs/analysis-note/sec_3d.tex: operational definition](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_3d.tex)

## Backup B2: the adopted covariance’s exact boundary

**Optional, outside the timed talk**

The full digest is 3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5. The projection digest begins 835828bf. Identity verification establishes which covariance was projected, not its statistical adequacy. The predeclaration ordering defect is ratified by exception, not cured, and no declared cause-3 boundary was evaluated by production. The paired measurement products used for the seed comparison are different digests and are not separately adopted. Five pinned bands are BeamAngleX, BeamAngleY, MuonResolution, Muon_Energy_MINERvA and Muon_Energy_MINOS. Their seed effect is unprobed in either direction. See slide 16 for the mandatory numerical measurements and their finite-ensemble scope.

Sources:

- [docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md)
- [docs/orchestration/OPERATIVE-SHEET-scalar5d.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/OPERATIVE-SHEET-scalar5d.md)

## Backup B3: reading the conditional p-values

**Optional, outside the timed talk**

These statistics belong only to the hybrid-null construction and the six conditions on slide 20. The frozen family has zero exceedances in nine tests and one in NuWro shape. Clopper–Pearson intervals are exact binomial confidence intervals for the exceedance probability. Determinacy requires those Monte Carlo intervals to resolve the decision relative to the multiple-testing threshold. The lost-draw recovery is report-only. Four nulls would have stopped one batch earlier with complete batches, with the same decisions. The closest recovered margin is 4.6 statistic units for GENIE plus MEC shape at kappa three. Independent checks cover the frozen-shift reading; the union reading is a same-code consistency replay. A small conditional p-value does not identify a nuclear mechanism or localize a discrepancy.

Sources:

- [docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md)
- [docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md)

## Backup B4: the PET representation studies

**Optional, outside the timed talk**

Pooling summarizes several objects into one representation. Individual routing gives each object its own attention token. The synthetic comparison used a small fixed object fixture and cannot settle production-multiplicity performance. The production cap acts on generic calorimeter clusters, not simply a thin typed-object tail. Later hybrid designs use energy summaries to recover some omitted information. PDG is the particle-identity code assigned by the Particle Data Group. One-hot encoding represents identity with separate category indicators rather than treating the code as a continuous number. PET2 is a tested pretrained model family. Pretraining means learning on another sample before this task. Its failure here applies to the tested recipes, not all possible pretraining. CPU–GPU optimizer differences were also investigated; numerical reproducibility does not establish physical accuracy.

Sources:

- [nd-unfolding/pet/direct_token_comparison/REPORT_FOR_BEN.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/nd-unfolding/pet/direct_token_comparison/REPORT_FOR_BEN.md)
- [nd-unfolding/pet/direct_token_comparison/GO_NO_GO-20260918.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/nd-unfolding/pet/direct_token_comparison/GO_NO_GO-20260918.md)
- [docs/analysis-note/sec_pet_campaigns.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_pet_campaigns.tex)

## Backup B5: the closed scalar sequence

**Optional, outside the timed talk**

These labels identify successive bounded campaigns, not distinct published measurements. They are all terminal. The background repair is a causal diagnosis for one nominal-bias component. The physical truth-departure failure remains without a single established cause. Reopening a closed study would require a new decision and contract. R is a targeted refinement change, not the production central-value estimator. A nominal-truth calibration check cannot establish performance over every alternative truth, and a pooled calibration result can hide individual functionals with poor coverage. A functional is any declared quantity extracted from the distribution, such as a bin, integral or projection.

Sources:

- [VALIDATION_LEDGER.md: VL149–VL155](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/VALIDATION_LEDGER.md)
- [docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md)
- [docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md)

## Backup B6: what the release can reproduce

**Optional, outside the timed talk**

Sufficient products are the stored quantities needed to recompute the reported inference without regenerating every event or training run. RC4 is a local release candidate, not a public deposit. Its scope excludes reproducing the 2D uncertainty, closure, bias, low-recoil, W2 and covariance-status numbers, as listed in its README. Those results retain their own evidence routes. The article still needs author decisions and external-release actions, including coauthor review, deposit and submission. None of those acts is authorized by preparing this talk.

Sources:

- [docs/publication/submission/PACKAGE-MANIFEST-20261006.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/publication/submission/PACKAGE-MANIFEST-20261006.md)
- [docs/publication/release/RC4-README.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/publication/release/RC4-README.md)
- [reproduction/s5p/README.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/reproduction/s5p/README.md)

## Backup B7: More events: distinguish three different proposals

**Optional, outside the timed talk**

We should distinguish more measured data from more training simulation and a different physics sample. The scalar reproduction already uses the twelve medium-energy forward-horn-current playlists for this signal. PET has trained on smaller subsets of the truth inventory, so increasing that sample is a possible design change, with substantial cost. It does not automatically repair bias, a misspecified response, or interval calibration. The current open release also lists reverse-horn-current data. That enables an antineutrino-dominated analysis, not a direct extension of the same neutrino cross section without new modeling. Enlarging truth acceptance with unchanged reconstructed selection adds extrapolation, not observed events. Finally, more bootstrap replicas only reduce the numerical noise in a bootstrap estimate; they do not provide the independent detector-simulated populations missing from the coverage design.

Sources:

- [docs/analysis-note/sec_3d.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_3d.tex)
- [docs/analysis-note/sec_fps.tex](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/sec_fps.tex)
- [nd-unfolding/pet/gbdt_comparison/REPORT-20261005.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/nd-unfolding/pet/gbdt_comparison/REPORT-20261005.md)
- [docs/orchestration/DELIVERY-20261008-uncertainty-preparation.md](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/DELIVERY-20261008-uncertainty-preparation.md)
- [https://minerva.fnal.gov/getdata/](https://minerva.fnal.gov/getdata/)

## Technical reference: Four measurements accompany the adopted 5D covariance

Expanded measurements for slide 16 (reference, not additional timed speech):
M1: The maximum fractional change in a declared projected uncertainty width is s_proj = 6.145%, above the 5% bound. The aggregate and median diagnostics are 0.471% and 0.485%. The comparison products are different from the adopted digest.
M2: s_proj is 6.02%, 6.02% and 6.145% on nested N = 40, 80 and 160 subsets at one seed pair. The same-seed resampling control falls from 20.91% to 7.57% between 40 and 80. The quoted 6.04% ± 0.39% summarizes subset scatter, not the width over seed pairs. Larger N and seed-pair width remain unmeasured.
M3: BeamAngleX, BeamAngleY, MuonResolution, Muon_Energy_MINERvA and Muon_Energy_MINOS remain at literal seed 42. These five of 45 bands carry 6.75% of covariance trace, or 26.0% of the square-root trace scale, and contribute zero seed movement by construction. Releasing their seeds could change the total statistic in either direction.
M4: On 43 projection functionals, central relative shifts have median 0.104% and maximum 0.761%, compared with median relative uncertainty 10.1%. In units of their own uncertainties the shifts have median 1.06%, maximum 6.02%, and total-rate movement 1.13%. Per individual 5D bin, median is 3.77%, 90th percentile 13.6%, maximum 49.8% of uncertainty. The same-seed control is 9.4e-13.
Criterion scope: the 5% bound was approved with the roughly 5.6% finite-ensemble width precision as motivation. The seed comparison grades comparison products; the adopted digest did not evaluate C3 in its own production. Adoption does not change that history.

## Technical reference: All ten specified joint-5D null hypotheses are rejected

Expanded conditions for slide 20 (reference, not additional timed speech):
1. The fine-grid null uses generator G's cross section, with MnvTune shapes and G's finite-MC fine-cell fluctuations below it. Refinement has not converged. The 0.50–0.86 comparison is the L2 norm of per-cell relative changes. The frozen kappa = 2 variants and the report-only kappa = 3 check follow the last refinement shift. The true sub-fine residual remains unmeasured and potentially material.
2. Detector calibration assumes the simulated per-event response beyond the drawn MinosEfficiency and GEANT neutron, pion and proton bands at plus or minus one standard deviation, together with the linear surrogate for five lateral bands. There is no recoil-energy-scale band. Hadronic-response completeness is not established.
3. Every pseudo-experiment draws all 34 vertical interaction-model bands. Negative LowQ2_1 and HighQ2_1 weights are clipped per universe under the recorded exception, at no more than 0.35% of a band's shift in the covariance-standardized norm.
4. Toys unfold with half the MC, whereas the data use the full MC. The shift measured in 16 pairs has median absolute size 0.02–0.075% per cell. Along the null's bias direction it is not always consistent with zero, but is at most about 0.05 null standard deviations. A bias-aligned upper-bound variant enters the rule.
5. GiBUU lacks neutrino energy above 20 GeV. Its truth outside p_parallel < 6 GeV/c still migrates into the tested domain under that energy truncation. All generator samples lack neutrino energy above 100 GeV; the record treats that tail as negligible.
6. Each prediction's finite simulation enters both as a diagonal variance term in the comparison metric and as a sampled residual. Independent recomputation establishes arithmetic agreement under these choices, not calibration adequacy.

## Terminology reference

**Acceptance / efficiency**: Probability that a true signal event enters the selected detector sample. Weak acceptance increases reliance on simulation.

**Adoption under exception**: A decision to use one identified product despite specified failed or unresolved criteria. It does not change those criteria's grades.

**Band / universe / throw**: A band groups variations of an uncertainty source. A universe is one variation. A throw is one random draw of the declared uncertain ingredients.

**Bias / residual**: Bias is the average displacement from truth over repeated experiments. A residual is an individual estimate minus its reference. A data-method difference alone does not measure bias.

**Bootstrap / Poisson bootstrap**: Resampling to estimate sampling variation. In the Poisson version, each event receives an independent random multiplicity with mean one, and the analysis is repeated.

**Boosted decision trees / GBDT / HGB**: Successive small decision trees combine into a predictor. GBDT means gradient-boosted decision trees. HGB is the histogram-based implementation used for the paired comparator.

**Calibrated classifier**: A classifier whose probability output is checked against class frequencies. Density-ratio use also requires the appropriate class-weight normalization.

**Calibrated test or interval**: A test or interval whose long-run behavior has been checked under specified simulated assumptions. This differs from calibrating a classifier probability.

**Central value / estimator**: The reported fitted value or distribution. An estimator is the full algorithm and settings that map observations to that output.

**Charged-current, CC / inclusive**: CC produces a charged lepton. Inclusive here allows any hadronic final state consistent with the signal definition.

**Chi-square / metric**: A discrepancy measure, often a covariance-weighted squared distance. Its numerical value needs a specified sampling model before it becomes a p-value.

**Classifier / regressor**: A classifier separates labeled examples. A regressor predicts a continuous numerical quantity, here including weights for missed events.

**Clipping / signed weights**: Some simulated corrections can be negative. Clipping replaces specified negative weights by a boundary value. Signed-background methods instead represent subtraction through negative contributions.

**Closure / pseudo-data / toy**: Closure unfolds simulated data with known truth. Pseudo-data are the simulated observations. A toy is one simulated repeated experiment.

**Conditional inference**: A conclusion that holds under the specified model, detector and sampling assumptions. Agreement in arithmetic does not establish all of those assumptions.

**Covariance / trace / projected width**: Covariance records variances and correlations between bins. Its trace sums the bin variances. The width of a linear projection with coefficients u is sqrt(u^T C u).

**Coverage / undercoverage / overcoverage**: Fraction of repeated intervals containing the specified truth. Below the stated confidence level is undercoverage, above it is overcoverage. Aggregate coverage can hide poor regions.

**CV / nominal / tune / prior**: CV is central value. Nominal denotes the reference settings. A tune modifies simulation using fitted or chosen adjustments. The unfolding prior is its starting truth distribution.

**Density ratio / event weight**: A factor that changes the relative population of events at given coordinates. An event weight scales that event's contribution to the estimated distribution.

**Determinate decision**: A rejection decision resolved despite the Monte Carlo uncertainty in the estimated tail probability, using the declared confidence-interval rule.

**Dimensional anchor / marginal / projection**: Integrate over an added coordinate to recover a lower-dimensional distribution. Normalization agreement is weaker than agreement in every cell.

**Eavail / recoil / ECAL / blob / muon fuzz**: Eavail is the implemented visible-hadronic-energy quantity, detailed in B1. Recoil is non-muon activity. ECAL is the electromagnetic calorimeter. Blobs are reconstructed aggregates of deposits. Muon fuzz is nearby muon-associated energy subtracted from recoil.

**Ensemble / replica / member / seed**: An ensemble is a collection of repeated fits. A replica or member is one fit. A seed fixes a pseudo-random sequence. Seed variation and event-resampling variation probe different effects.

**Familywise alpha / Holm correction**: Alpha is the allowed false-rejection probability. Familywise control bounds the probability of any false rejection across the declared set. Holm applies successively adjusted thresholds to ordered p-values.

**Fiducial volume / phase space / FPS**: Fiducial volume is the selected detector region. Phase space here means the allowed kinematic domain. The project's FPS work extends truth-muon cuts while retaining the tracker-volume and reconstructed-selection requirements.

**Fine-grid hybrid null / sub-grid**: The tested truth has generator G's rates in fine cells and MnvTune shapes, with G's finite-MC fluctuations, below them. Sub-grid denotes structure within those cells. This is a specified hybrid model, not arbitrary generator truth.

**Flux / protons on target, POT / FHC**: Flux is incident neutrinos per area. POT measures accelerator exposure. FHC means forward horn current, the beam-focusing configuration used for neutrino mode.

**Functional / supported cell**: A functional is a declared extracted quantity, such as a bin or projection. A supported cell has simulation support under the analysis's declared domain rules.

**Gaussian / standard deviation, SD / RMS**: Gaussian is the normal distribution. SD measures spread around the mean. RMS is the square root of the average squared quantity. A tail probability is not automatically a Gaussian significance.

**Generator / Monte Carlo, MC**: A generator simulates interactions and final-state particles using a physics model. Monte Carlo uses random sampling. GENIE, NuWro and GiBUU are generator frameworks used here.

**Hadronic response / detector response**: The distribution of reconstructed signals given an underlying event. Hadronic response concerns energy and activity from the non-leptonic part of the event.

**Hash / digest / checkout / import path**: A hash or digest identifies file bytes. A checkout is a local code version. An import path controls where the program finds modules. Correct file hashes alone do not prove the intended modules executed.

**Held-out / final bank / reserve bank**: Simulation samples reserved for distinct stages of evaluation. A fixed bank is a finite parent sample, so inference using it remains conditional on that bank.

**Iteration / capacity / regularization**: An iteration repeats OmniFold's two steps. Capacity describes how complex a fitted function can be. Restricting either can stabilize estimation but retain bias toward the prior.

**Kappa / refinement shift**: Kappa scales the last measured change under grid refinement. The reported scan follows that one direction and does not bound the unknown remaining error.

**Lateral / vertical systematics / surrogate**: Lateral changes shift event coordinates and can change selection. Vertical changes alter weights. A surrogate approximates a more expensive change, here the specified linear treatment of lateral variations.

**LightGBM / scikit-learn / backend**: Software implementations of the learner. A backend is a selectable implementation. Matching broad tree settings does not make different backends the same estimator.

**MAT / MinosEfficiency / GEANT**: MAT is the MINERvA Analysis Toolkit. MinosEfficiency is the MINOS selection-efficiency uncertainty band. GEANT-based detector simulation includes hadron-transport variations.

**Missing event / purity / background**: A miss is a true signal event without a selected reconstructed partner. Purity is the predicted signal fraction in a detector bin. Background is selected activity outside the declared signal.

**Null / p-value / power**: The null is the specified hypothesis tested. A p-value is its tail probability for the observed statistic. Power is the probability of rejecting the null under a specified alternative.

**Nuisance parameter**: An uncertain model or detector ingredient varied while testing the main physics hypothesis.

**PET / transformer / attention / token**: PET is the point-cloud transformer used in OmniLearn. A transformer learns interactions among object representations through attention. A token is one object's input representation.

**Point cloud / full-event / recoil-only**: A point cloud is an unordered set of objects. Full-event PET includes muon information alongside recoil objects. The historical recoil-only classifier omitted the muon.

**PDG / one-hot / pooling / pretraining**: PDG is a particle-identity code. One-hot uses separate category indicators. Pooling combines multiple objects into a summary. Pretraining learns parameters on another sample before this task.

**q0 / q3 / Q² / W**: Energy transfer, magnitude of three-momentum transfer, positive spacelike transfer squared, and experimenter's hadronic mass. B2 gives the relations and operational interpretation.

**Quasielastic / resonance / DIS / 2p2h / MEC**: Quasielastic resembles nucleon knockout. Resonances are excited hadronic states. DIS is deep-inelastic scattering at high hadronic mass. 2p2h involves two particles and two holes in the nuclear state. MEC means meson-exchange current, the label used for the Valencia two-nucleon contribution in these predictions.

**Recovery R / L1 distance**: Here R = 1 - sum|unfolded-target|/sum|prior-target| for unit-normalized histograms. The sum of absolute differences is L1 distance. R becomes unstable when the injected marginal change is tiny.

**Rounding sensitivity / reproducibility floor**: Movement caused by tiny numerical perturbations of the same inputs. It can matter when statistical intervals are similarly small.

**Scalar observable / dimensionality**: One numerical value per event for a chosen property. Five recorded observables need not represent five independent physical degrees of freedom.

**Shape-only / total test**: A shape-only comparison removes overall normalization. A total comparison retains rate information as defined by the campaign statistic.

**Student-t / Clopper–Pearson**: Student-t accounts for estimating a spread from a small sample. Clopper–Pearson gives exact binomial confidence limits for an exceedance probability. Neither fixes model misspecification.

**Systematic / statistical / training uncertainty**: Statistical variation comes from finite event samples. Systematics reflect uncertain detector or physics ingredients. Training variation comes from the learning procedure at fixed inputs.

**Sufficient products / replay / regeneration / RC4**: Sufficient products retain what is needed for a specified calculation. Replay recomputes from them. Regeneration rebuilds upstream simulation or training. RC4 is the local fourth release candidate.

**Terminal / gate / VL / s5c–s5p**: Terminal means a study ended under its rules. A gate is a required check before a next action. VL identifies validation-ledger entries. The s5 labels identify bounded scalar campaigns, not separate measurements.

**Uncertainty transfer**: The claim that a band constructed for one estimator also describes another estimator; here it remains unmeasured.

**q0**: Energy transferred from the lepton to the hadronic system, distinct from the selected visible-energy sum Eavail.

**Identifiable quantity**: A truth quantity distinguishable through the observed detector distribution under stated assumptions.

**Cramer–Rao width**: A local information-based precision diagnostic for a specified response model and estimator class; not a universal bound on biased or differently specified estimators.

**Familywise error**: Probability of at least one false rejection across the stated family of tests.

**A100-hour**: One hour of use of one NVIDIA A100 GPU; distinct from a CPU core-hour or whole-node hour.
