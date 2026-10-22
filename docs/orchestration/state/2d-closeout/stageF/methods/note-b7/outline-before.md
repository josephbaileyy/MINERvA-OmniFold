# Reverse outline of `sec_joint.tex` at origin/main b603f9cf (one sentence per paragraph)

Paragraph ids are used in `ledger.md` and `changes.md`. Line numbers are those of b603f9cf.

## §10 opening (sec:joint5d)
- **J0** (l.5-16) The section is the complete record of the joint 5D tests (design fixed before production, two
  disclosed data-informed elements); they test hybrid nulls about five predictions, are not a cross section, add no
  reportable uncertainty and do not validate the five-axis covariance; "everything the argument needs is stated here";
  the cited records are its provenance. *Complaints: META (sol r1, r2).*

## §10.1 Hypotheses, grid and statistics (sec:joint5d-design)
- **J1** (l.25-45) H0(G): truth = G on every fine cell; below the grid, Tune v1 composition varied by the drawn
  model universes with fine-cell integrals fixed, Tune v1 background; this hybrid null is what the calibration
  simulates; for Tune v1 nothing external is combined; three distinct requirements (definition, representation of G,
  calibration fidelity); total and shape tests, ten in all.
- **J2** (l.50-52) The fine grid is the analysis binning, 14x16x7x7x6; test cells are its integrals.
- **J3** (l.54-62) The coarse 3^5 test grid with its edges, 109 supported cells, GiBUU's 72-cell domain; the grid
  specifies a finite hypothesis and a statistic, not binned unfolding.
- **J4** (l.64-73) T_tot and T_sh; Sigma = V + diag Var(mu_G); V Ledoit-Wolf from 194 pilot pseudo-experiments; the
  metric affects power, the calibration sets size.
- **J5** (l.82-91) Diagonal prediction variance; pilot seeds disjoint but same events, no MINOS band; diag V matches
  (median ratio 1.00); shrinkage 0.015 floors ~80 of 109 directions, whitened trace ~47; power only; other
  intensities not measured.

## §10.2 Calibration (sec:joint5d-calibration)
- **J6** (l.96-115) Null from full-chain pseudo-experiments with the joint-test estimator (config chosen before the
  design was fixed); itemized draws.
- **J7** (l.116-126) Data unfolded once; p = (k+1)/(B+1), never zero; claim p = max over D and +-2 delta_fine
  variants; external nulls non-central (lambda 318-6344) because of the estimator's pull.
- **J8** (l.141-155, paragraph "Generative model") Random halves; truth = G on populated fine cells, at most 0.2% /
  about 4% of the null SD (spread < 1.5%); per-cell renormalized bands; independent flux and band universes,
  multiplied; lateral bands as sum z_b Delta_b from data endpoint unfoldings; GEANT4 reweights; null conditional on
  data-derived inputs, not validated.
- **T1** Table tab:joint5d-genmodel (picture and tabular).

## §10.3 Multiplicity, stopping rule and the predeclared design (sec:joint5d-frozen)
- **J9** (l.213-220) Holm at 5%; determinacy requirement (95% CP interval below threshold); batches of 200 to 1999;
  sequential rule stops a null once both decisions determined.
- **J10** (l.227-242) Stop: 99.5% CP interval on one side + precision; gate = 97.5% one-sided upper bound; under A1, A2
  the gate bound holds for any stopping rule incl. budget extensions; FWER <= 0.8902 alpha < 0.9 alpha (App.);
  A2 requires loss independent of outcome, "which has not been shown"; size averaged over nuisance priors.
- **J11** (l.244-252) Everything fixed before production; two data-informed elements disclosed (reviewers saw
  residuals; status outputs exposed observed claim p); budget extension decided while visible, to reach the
  predeclared stop; nothing changed; bound holds whatever the stopping rule. *Complaint: PROC (gemini).*
- **J12** (l.255-257) Independent recomputation agrees on 1379 rows; verifies calculation, not calibration adequacy.
- **J13** (l.260-266) Three post-decision studies outside the decision rule, each specified before it ran (kappa scan,
  recovery, projections; the last after 5D outcomes known); GENIE muon-projection non-rejection post hoc.

## §10.4 Conditions (sec:joint5d-conditions)
- **J14** (l.271-275) Six conditions, quoted verbatim apart from typesetting; bracketed text editorial (replaces file
  references, annotates two superseded statements). *Complaint: META/BOOK (gemini).*
- **Q** (l.282-314) The verbatim quote (i)-(vi). Untouched.
- **J15** (l.315) "In the terms of this note, and grouped by kind, they read as follows."
- **J16** (l.318-345, "Numerical convergence") (i) Tune v1 composition below the grid; convergence not shown (L2
  ratio 0.50-0.86); design proxy shrink 0.45-0.76, calculation not recorded; residual ~1-3x last step; claim variants
  +-2, robustness +-3 for reporting only (outside the decision rule); geometric assumption; 0.55-2.0 and 1.07-3.6 null
  SD; carry-over to G only if ...; (vi) prediction samples.
- **J17** (l.350-358, "Calibration validity") Valid to the extent the chain reproduces the data analysis; no
  rejection rate measured; two departures bounded; (iv) half vs full simulation, <= ~0.07 null SD, upper-bound variant.
- **J18** (l.367-388) Mean-only measurement; quarter-simulation check (first 200 of NuWro, GENIE, GENIE+MEC): medians
  within 0.074, widths 0.975-1.010, mean paired shift 0.006-0.034; extrapolation conservative, all ten rejected; not a
  test of the data process; same simulated events, conditional; margins 1.11/1.30 (1.01/0.67 robust), others 2.7-203
  (2.0-203); crossing means undetermined; rounding nondeterminism changes only NuWro shape 2/1752 -> 3/1752.
- **J19** (l.394-408, "Physical-model adequacy") (ii) detector model, surrogate checked only for endpoint symmetry; no
  recoil response band; (iii) 34 bands, two clipped <= 0.35%; (v) GiBUU energy limits, 100 GeV negligible; Tune v1
  composition is a modelling choice too.

## §10.5 Decisions (sec:joint5d-results)
- **J20** (l.413-420) All ten rejected; nine k=0, NuWro shape k=1; survive +-3 robustness; figure description.
- **T2** Table tab:joint5d + caption (B at the predeclared stop; 1400/1800 submitted; rest lost, recovered for
  reporting only).
- **F1** Figure fig:joint5d-nulls caption.
- **J21** (l.475-484, "Sensitivity to the sub-fine-grid residual", label sec:joint5d-kappa) kappa definition; scan
  for reporting only: determinate rejections up to 5.25; lost between 5.2547 and 5.2563 (5.1688-5.1703 with recovered
  draws), GENIE+MEC shape then GENIE shape via Holm; neither a determinate non-rejection; one direction, no bound.
- **J22** (l.489-496, "Power") power is context only; values and binomial intervals.
- **J23** (l.499-502) power sets lost some of 200 (172-199 retained); complete sets agree within 0.01; first GENIE set
  0.72 with null recomputed on all draws.

## §10.6 Lost pseudo-experiments and their recovery (sec:joint5d-lost)
- **J24** (l.507-516) Time limits: 224 calibration (111 interrupted, 113 never started), 53 power; decisions on
  completed draws; pre-recovery sensitivity: every decision could change, p 0.013-0.019 if every interrupted draw
  exceeded; |rho| <= 0.06, supports but does not certify. *Complaint: PROC (gemini).*
- **J25** (l.518-529) Rerun for reporting only under a reviewed procedure; determinism 16/16; every submitted draw
  observed; none reaches; closest margin 4.6 of 868.6, next 49.8; complete batches would have stopped four nulls at
  B=1200 with the same decisions.
- **J26** (l.531-539) Scope of the recovery's checks: 856/856 cross-check of the primary-shift reading only; the
  all-draws reading only by a standalone rerun; earlier stops only by the calibration run itself.
- **J27** (l.540-545) Recovery for reporting only; primary decisions at the stopping B; the rejections "are stated as
  holding with every submitted draw observed ... no longer accompanies them". *Complaint: HEDGE/DENSE (sol r1, r2).*

## §10.7 Matched coarse projections (sec:joint5d-projections)
- **J28** (l.556-570) Projections give p < 0.05 for every test in one of two; no evidence of extra discrimination;
  specified before run, after 5D outcomes; same ensembles with recovered draws; reproduced independently; GENIE not
  rejected in (pT,ppar) (post hoc), rejected in (Eavail,W); hadronic information participates; no added power shown;
  powers not compared.
- **J29** (l.571-576) Table; criterion fixed before the run (both projected p >= 0.05 in both readings); none meets
  it; same values in both readings.
- **T3** Table tab:joint5d-projections + caption.

## §10.8 Hadronic-response condition (sec:joint5d-response)
- **J30** (l.609-626) Test-beam response uncertainty, 10% at 0.9<q3<1.2 GeV; no calorimetric band here; effect on p
  unmeasured; muon-only published comparison is context; GENIE projection shows hadronic axes involved.
- **J31** (l.628-642) Exploratory +-4% recoil scale; null distributions used for the decisions; size from test-beam
  agreement 0.35-2.0 GeV/c; neutrons/high momentum outside; not a validated prescription; unscaled re-unfold
  reproduces; all ten hold; statistics move up to ~11%; nine k=0; NuWro shape k 1 -> 3 at +4% (p 0.0023 vs 0.05);
  reproduced independently.
- **T4** Table tab:joint5d-recoil + caption.
- **J32** (l.669-680) Nulls fixed; one coherent scale after calibration; untested (a)-(c); conditional on the
  simulation's hadronic response; response model not shown complete.

## §10.9 Hydrocarbon target correction (sec:joint5d-ch)
- **J33** (l.689-692) NuWro and GiBUU on carbon; corrected to CH and re-evaluated against the decision nulls; "They are
  descriptive: they do not re-grade the recorded decisions of Table, which stand."
- **J34** (l.696-707, "Construction") 12/13 C + 1/13 H; f_H 5.08% / 4.77%; r_c ranges; f_H per cell 0.112 / 0.109;
  both toward the data.
- **J35** (l.716-726, "Re-evaluated tests") NuWro total -3.83 SD, shape -0.37; at original position undetermined
  (-1.11 SD); rejected only by re-sorting to last (0.05); not rejected at kappa=3 (p=0.075); shape +0.74; GiBUU -4.67 /
  -1.33, margins 7.86->3.18, 3.58->2.24, rejected incl. kappa=3; W_CH no change.
- **J36** (l.733-734, "Generation checks") The verbatim B3 label and its framing: sampling closure failed; post hoc bias
  check declared before computed met <= 0.1 sigma_c; moves CH by ~5e-4 sigma_c. *Complaint: BOOK (sol).*
- **J37** (l.738-743) GiBUU DIS on hydrogen, 46%, lose median 45 MeV, pT imbalance 31 MeV; others balance; cause
  unidentified; may affect carbon, uncheckable.
- **J38** (l.745-752) NuWro hydrogen: four chunks rerun; excluded 1.8e-5 / 3.8e-5 (1.9e-5 / 6.2e-5 with first
  attempt); four to six events; 95% bound 1.8e-4 > 1e-4, flagged.

## §10.10 What the tests establish (sec:joint5d-reading)
- **J39** (l.757-769) Recover the published disagreements; contribution is calibration; global assessments; generator
  versions; all six conditions; response and residual outside any validated bound; what an extension needs.
