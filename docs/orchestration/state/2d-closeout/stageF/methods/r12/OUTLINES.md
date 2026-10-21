# Round r12 reverse outlines (writer, 2026-10-21)

Before: paper_body.tex at 1a74560c. After: the writer's target outline, before the review fixes (see METHODS-IMPLEMENTATION.md §15).

## Before


One sentence per printed paragraph (comments stripped, floats listed separately). Paragraph ids `P#` are used by
`ledger.md`. Line numbers are those of `docs/analysis-note/paper_body.tex` at 1a74560c.

| ¶ | lines | section | main idea, one sentence |
|---|---|---|---|
| abs | main_paper.tex | Abstract | 2D integral within ~1% with a shape difference; 3–5D central values only, with background bias, partial recovery, undercoverage and no definition meeting 10%; the hybrid-null tests all reject, with five qualifiers. |
| P1 | 28–42 | I | Binned unfolding scales badly with observables; OmniFold is unbinned and has been used at H1, ATLAS and on simulated T2K data. |
| P2 | 46–58 | I | We reproduce the published 2D MINERvA cross section and add Eavail, q3 and W, which are simultaneous but not independent; binned data measurements reach three dimensions. |
| P3 | 64–85 | I | The paper is a case study asking whether the implementation is reliable under generator-sized mismodelling; interval coverage and test calibration are kept apart, and this distinction organizes the paper. |
| P4 | 94–101 | I | The validation studies are the main results (Table I); the generator tests are an application calibrated within the simulation model. |
| T-I | 109–129 | I | Table I: nine findings, each with configuration, test, principal limitation and section. |
| P5 | 142–160 | I | Scope: one implementation, no validated 5D measurement, unvalidated intervals, no covariance significance, hybrid nulls, nuisance-averaged size, FWER under assumptions, no recoil band, carbon targets, not exclusions. |
| P6 | 163–165 | I | The analysis note gives the details, and each pointer names its section. |
| P7 | 170–206 | II | Data, exposure, detector, signal definition, background, selection, event counts, GENIE+Tune v1 simulation; the selection is fixed as features grow. |
| P8 | 216–249 | II | Truth-level observable definitions, including Eavail with a 135 MeV constant whose effect is quantified but not compared with the covariance; reconstructed Eavail, q3, W. |
| P9 | 253–287 | II | Reconstructed W is an exact function of (pT, p∥, q3) apart from a clamp, truth W nearly so; only reco W is redundant; metric degeneracy consistent with but not shown to come from this. |
| P10 | 304–334 | II | The four external predictions, their targets, flux treatment, W and pT conventions, and the carbon/CH difference (8.3% at W<1.1 GeV), which the tests do not correct. |
| P11 | 342–351 | II | Fine grid, coarse 3^5 test grid, the 1000-event support rule (109 cells, 0.47% left out), the GiBUU domain (72 cells). |
| P12 | 356–364 | III | One OmniFold iteration: two classifiers, pull-back, push; cross section from histogramming; no efficiency correction. |
| P13 | 370–380 | III | Purity-based subtraction versus the unbinned negative-weight treatment with a clipped refinement; they agree on bin integrals but not inside bins. |
| P14 | 387–390 | III | Classifiers are trained in-sample, no early stopping, no class balancing, no effective sample size. |
| P15 | 392–428 | III | Configurations: five iterations, GBDT, defaults, no tuning; (a) for central values, (e) for tests (selected before the design); central values keep purity because they predate the bias finding; five iterations kept under a prior rule. |
| T-II | 433–460 | III | Table II: the five configurations (a)–(e). |
| P16 | 462–474 | III | Closure versus coverage (pointwise); pseudo-data reweighting keeps response; the envelope reweights the prior; detector response fixed except in the calibration. |
| P17 | 492–530 | IV A | 2D: integral ratio 1.011, 95.6% of bins within 10%, χ²/ndf 2.65 as a descriptive shape distance; learner dependence; LightGBM chosen after both comparisons, so not an independent validation; 0.98%/12.2% learner difference outside the covariance. |
| F-1 | 534–554 | IV A | Fig. 1: projections, pulls and uncertainty summary. |
| P18 | 574–616 | IV B | 2D covariance: four blocks, 6.45%/4.75% vs published 6.85%/4.61%; flux 3.75% vs 4.01% unexplained; block-sum assumptions; miss-row approximation not corrected. |
| P19 | 630–645 | IV B | Run periods are mutually inconsistent (7% step); the run-period block absorbs it (2.0% on the integral) by construction, so it is not a test. |
| P20 | 654–681 | IV B | Statistical block 0.684% with a 0.26σ offset; untested coverage; an earlier band undercovered (91.2% vs 95.4%), and the post hoc rescoring of the rebuilt band is not independent. |
| P21 | 692–704 | IV B | 2D intervals, bias and covariance are not validated; omitted terms; validated intervals would need unavailable samples. |
| P22 | 718–743 | V A | 3–5D normalizations agree at 1–2%; closures (0.10, 1.1%) without prior criteria; purity bias up to 4% at high W, below 0.3% with negative weights. |
| P23 | 754–776 | V B | A generator-sized Eavail change is only partly recovered (up to 74%), interpreted as regularization bias; 16–31% for other shapes with the joint-test estimator. |
| P24 | 792–810 | V C | The 5D coverage test failed its prior criterion: under a ~10% rate reduction, 51 of 153 integrals lie below 0.66, as low as 0.06. |
| P25 | 820–833 | V C | The diagnosis: residual bias growing with W, inferred, source not established, separating test not run; no frequentist coverage claimed. |
| F-2,3,4 | 842–917 | V | Figs. 2–4: background residual, deformation recovery, coverage. |
| P26 | 924–951 | V D | The 5D covariance has not met its prior validation criteria; it is used for the V B comparisons only; seed dependence 6.1% vs 5% limit, from one pair, with pinned bands. |
| P27 | 957–963 | V D | Rounding-level instability: the refinement fails a 0.3/1.0σ data-stability test, shifting by up to 2.6 (baseline 2.5). |
| P28 | 987–1002 | V E | No tested reporting definition meets the 10% criterion under the envelope prescription, within the study's rules and budget; per-definition outcome. |
| P29 | 1004–1008 | V E | The envelope (10–13% median) is comparable to generator differences, motivating the tests. |
| P30 | 1020–1031 | VI | Three results point to the unfolded result retaining its prior; the coverage failure's origin is not established and its separating test not run. |
| P31 | 1046–1065 | VI | An exact binned comparison in simulation leaves about the same residual, so the residual is consistent with regularization of the inverse problem rather than the tree approximation, within a stated scope. |
| P32 | 1070–1077 | VI | The checks a reader should carry to another analysis, and calibration when intervals cannot be validated. |
| P33 | 1096–1103 | VII A | Descriptive comparisons: all generators underpredict at low Eavail. |
| P34 | 1111–1118 | VII A | Relative to Tune v1 the positive difference concentrates at high Eavail and W, with a fifth in the overflow cell, and also extends to low W in ratio. |
| P35 | 1124–1133 | VII A | Data exceed all four external predictions; GiBUU energy limit and target difference; no response-mismatch closure; the map locates no mechanism. |
| P36 | 1141–1160 | VII B | Definition of the hybrid null and the three distinct requirements. |
| P37 | 1178–1193 | VII B | One calibration pseudo-experiment; null conditional on data-derived lateral shifts, unvalidated. |
| P38 | 1204–1214 | VII B | Total and shape statistics and their Ledoit–Wolf metric; the metric sets power, the calibration sets size. |
| P39 | 1224–1232 | VII C | p = (k+1)/(B+1) and the shifted nulls fixed in advance. |
| P40 | 1244–1247 | VII C | Holm at α = 0.05 with sequential sampling to at most 1999. |
| P41 | 1256–1268 | VII C | The Clopper–Pearson rule controls FWER at 5% under A1 and A2 for any stopping rule (0.8902α). |
| P42 | 1277–1287 | VII C | Lost pseudo-experiments; A2 unshown; the rerun changes no decision; the size is nuisance-averaged. |
| P43 | 1297–1303 | VII C | Everything was fixed before the ensembles; an independent recomputation agrees. |
| P44 | 1308–1319 | VII C | Choices made after results were seen: learner, design review, budget extension, post-decision studies, the GENIE CV observation. |
| P45 | 1328–1329 | VII D | Six conditions, numbered as in the note. |
| P46 | 1344–1358 | VII D | (i) Fine-grid convergence not shown; κ = 2 rests on an undocumented geometric rate; carry-over to G is conditional. |
| P47 | 1363–1377 | VII D | (ii) No calorimetric response band; GENIE CV's rejection involves the hadronic axes. |
| P48 | 1386–1398 | VII D | (ii) A ±4% recoil-scale sensitivity leaves the rejections, with stated untested effects. |
| P49 | 1400–1401 | VII D | (iii) The 34-band prior with two bands clipped. |
| P50 | 1415–1438 | VII D | (iv) Half- vs full-simulation shift (0.07 null SD), the quarter-simulation check, conditional on the simulation; closest margins 1.11 and 1.30. |
| P51 | 1440–1443 | VII D | (v), (vi) GiBUU domain and prediction samples. |
| P52 | 1448–1452 | VII D | Calibration validity rests on the chain reproducing the data analysis; no data-like null rejection rate measured. |
| P53 | 1457–1487 | VII E | All ten reject; CH replays (NuWro total not robust; GiBUU hydrogen energy); κ scan to 5.2; external nulls displaced. |
| T-III | 1496–1522 | VII E | Table III: the ten decisions. |
| P54 | 1528–1561 | VII E | The contribution is the calibration; known disagreements; coarse projections show no added discrimination; global; power. |
| P55 | 1576–1583 | VIII | Results are the validation findings; 2D learner dependence and untested stat block; 3–5D purity bias and unvalidated intervals; Sec. VI link. |
| P56 | 1594–1600 | VIII | Tests illustrate inference with a biased estimator; FWER provided calibration exact; what physical interpretation requires. |
| P57 | 1605–1616 | VIII | Why unfold before testing: reuse, and a reconstruction-level test would need the same response model; power not compared. |

## What the outline shows (for the rewrite)

- **Chronology and bookkeeping** sit inside result paragraphs: P15 (when the central values were computed; a rule set
  before), P17 (choice after the comparison), P20 (specified in advance; rescored after), P22 (no prior criterion),
  P24 (criterion set before the test), P26 (criteria set before it was built; limit set before), P28 (rules and budget),
  P39–P44 (fixed in advance; budget extension; lost seeds; post-decision studies), P46 (undocumented rate).
- **Sec. VII C–D** (P39–P52, about 1,300 words) carry the sequential-sampling argument, lost-seed recovery, the
  design chronology and the full conditions text; the note prints all of them (sec_joint.tex §§10.2–10.8).
- **Scope** is stated in P3, P4 and P5 (three paragraphs); P5 alone lists ten qualifiers.
- **Sec. VIII repeats Sec. VI** (P55's last sentence) and holds the rationale (P57) that Sec. VII needs first.
- **Pointers** to the note are descriptive ("analysis note, section on …"): 37 printed mentions of the note.

## After (target)


One sentence per paragraph; each sentence is the paragraph's topic sentence, and states its result. A limitation kept
in the paper is attached to the claim it bounds and stated as its effect. Paragraph ids `N#` are used by `ledger.md`
("paper location after"). Ref. [14] is the analysis note, cited by numbered section through `xr-hyper`.

## I. Introduction and scope
- **N1.** Binned unfolding scales badly with the number of observables; OmniFold unfolds unbinned and has been applied
  to collider data and to simulated neutrino data.
- **N2.** We reproduce MINERvA's published 2D cross section and add Eavail, q3 and W, obtaining simultaneous three- to
  five-observable central values that are not independent; data measurements reach three dimensions.
- **N3.** The paper asks whether this implementation gives reliable multidimensional cross sections under
  generator-sized mismodelling; keeping interval coverage apart from test calibration organizes it, the validation
  findings (Table I) are its main results, and the generator tests are a secondary application.
- **T-I.** Table I, shorter cells, the same nine findings and qualifiers.
- **N4.** Scope, one paragraph: one implementation and the tested configurations; no validated five-observable
  measurement; hybrid-null tests with FWER control under the stated assumptions, on average over the nuisance priors;
  no recoil-response band; not exclusions; the note is cited by section.

## II. Data, observables, and domains
- **N5.** The data, signal definition, selection and simulation (unchanged facts).
- **N6.** The truth-level observables, including the 135 MeV convention and its size.
- **N7.** Reconstructed W is an exact function of the other reconstructed muon and q3 inputs (apart from a 1.5% clamp),
  so the five observables are simultaneous, not independent; truth W is nearly so.
- **N8.** The four external predictions, their targets and flux treatment, two small convention differences, and the
  carbon/CH difference the tests do not correct.
- **N9.** The fine grid, the coarse 3^5 test grid and its 109 supported cells.

## III. Estimators and validation design
- **N10.** One OmniFold iteration (unchanged).
- **N11.** The two background treatments (unchanged).
- **N12.** Training details (unchanged).
- **N13.** All configurations use five iterations of untuned boosted trees; (a) gives the central values and carries the
  purity bias of Sec. V A; (e) gives the tests and removes most of that bias; more iterations do not reduce its model
  dependence.
- **T-II.** Table II (caption pointer numbered).
- **N14.** Closure, pointwise coverage, and which studies reweight the pseudo-data and which the prior (unchanged).

## IV. Two-dimensional benchmark
- **N15.** The integral agrees within about 1% and 95.6% of bins within 10%, with a correlated shape difference
  (χ²/ndf = 2.65) whose size depends on the learner, chosen after the comparison, so the benchmark is a reproduction.
- **F-1.** Fig. 1 (caption unchanged).
- **N16.** The four-block 2D covariance gives 6.45% per bin (published 6.85%), under the block-sum assumptions, with
  an uncorrected miss-row approximation.
- **N17.** The run periods are mutually inconsistent; the run-period block carries this (2.0% on the integral), but its
  size cannot be validated because it is built from the observed differences.
- **N18.** The quoted statistical block (0.684%) and the total have had no coverage test; an earlier band undercovered
  and the rebuilt band's rescoring is not independent.
- **N19.** The 2D intervals, bias and covariance are therefore not independently validated, and named terms are in no
  block.

## V. Five observables: bias, coverage, and precision
- **N20.** The 3–5D normalizations agree at 1–2%; nominal closure is good except a purity bias of up to 4% at high W,
  which negative weights reduce below 0.3%.
- **N21.** A generator-sized Eavail change is only partly recovered (up to 74%), a regularization bias in no quoted
  uncertainty; 16–31% for other shapes.
- **N22.** Bias-corrected statistical intervals miscover under a ~10% rate reduction: 51 of 153 integrals below the 0.66
  threshold, as low as 0.06.
- **N23.** The miscoverage is a residual bias growing with W, inferred and of unestablished source, so no frequentist
  coverage is claimed.
- **N24.** The five-observable covariance does not meet its validation criteria and is seed dependent (6.1% against a 5%
  limit, one pair), so it serves only the V B comparisons and gives no significance.
- **N25.** The estimators are unstable at the rounding level (up to 2.6σ_stat).
- **N26.** No tested reporting definition meets the 10% target under the envelope prescription; per-definition outcome.
- **N27.** The envelope (10–13%) is comparable to generator differences, which motivates the tests.

## VI. What limits the estimator
- **N28.** Three results show the unfolded result retaining part of its prior; the coverage failure's link is open.
- **N29.** An exact binned unfolding in simulation leaves about the same residual (Table III), which is consistent with
  regularization of a weakly constrained inverse problem rather than the tree approximation, within a stated scope.
- **T-III.** New Table III: J-cell median residuals, boosted trees against exact binned unfolding, from the note.
- **N30.** The checks a reader should carry; calibration when intervals cannot be validated.

## VII. Application: comparison with generator predictions
- **N31.** (Opening, moved from Sec. VIII.) Unfolding makes results reusable at truth level, but a test still needs the
  response model, so the tests calibrate the unfolded statistic in simulation.
- **N32–N34.** Descriptive comparison (A): the low-Eavail underprediction; the map relative to Tune v1; the four external
  predictions; the map locates no mechanism.
- **N35.** (B) The hybrid null and the three distinct requirements.
- **N36.** (B) One calibration pseudo-experiment; nulls conditional on data-derived shifts.
- **N37.** (B) The total and shape statistics; metric sets power, calibration sets size.
- **N38.** (C) p values and the shifted nulls.
- **N39.** (C) Holm with a Clopper–Pearson rule controls FWER at 5% under A1–A2 for any stopping rule, on average over
  the nuisance priors.
- **N40.** (C) The design was fixed before the observed statistics, with two data-informed elements; the lost
  pseudo-experiments change no decision; an independent recomputation agrees.
- **N41–N48.** (D) The six conditions, each as its effect on the rejections; calibration fidelity (A1) is not
  demonstrated beyond the simulation-size check.
- **N49.** (E) All ten tests reject; the CH replays, the κ scan and the displaced nulls.
- **T-IV.** Table IV, the decisions (unchanged).
- **N50.** (E) The contribution is the calibration; the projections show no added discrimination; power.

## VIII. Discussion and conclusions
- **N51.** The validation findings, within the stated scope (one short paragraph, no repeat of Sec. VI).
- **N52.** The tests illustrate inference with a biased estimator, valid if the calibration is exact; what physical
  interpretation would need.
