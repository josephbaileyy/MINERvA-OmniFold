RESULT PACKAGE: the tables and figures of the five-observable OmniFold methods paper, as data files

A five-observable unbinned unfolding of MINERvA medium-energy muon-neutrino data, with a two-dimensional benchmark
against the published (p_T, p_par) result (arXiv:2106.16210). Version 1. Not yet included: 4 results (see pending/).

SCOPE OF USE (read first)
  The paper: "Interval coverage has not been validated." and "The sixteen-cell cross section the estimator gives
  on the data is therefore not a measurement." No file in this package is a coverage statement, and no file makes
  a measurement claim beyond the paper's. Each file's own scope is given with it below.

LICENCE
  To be set at deposit.

CONVENTIONS
  - Cells R00-R15 are always in that order, in rows and columns alike.
  - p_par (the muon momentum along the beam) is written pz in tab-result16_cells.csv and ppar elsewhere; momenta
    are in GeV/c, E_avail and W in GeV.
  - Every rel_sigma_* and *_over_f column is a fraction, not a percent. In sec-repro2d_benchmark.csv the unit
    column gives each row's unit.
  - The largest edge on each axis of a cell (4.5 GeV/c for p_T, 60 GeV/c for p_par, 100 for E_avail, q3 and W)
    is the outer edge of the analysis grid, which contains every signal event; it is not a cut.
  - Numbers are written at full float64 precision. Values such as p = 1.0000000000000002 and matrices that are
    symmetric only to about 3e-16 of sqrt(C_ii C_jj) are floating-point rounding in the source records, kept as
    they are.
  - Files are named by the paper's LaTeX label; the label-to-number map is below, to be completed at release.

GLOSSARY
  cell (R00-R15)
      one of the 16 reporting cells: a box in the five observables p_T, p_par, E_avail, q3 and W. The cells are
      boxes, not a product grid; tab-result16_cells.csv gives each box.
      Paper: "The largest edge on each axis is the outer edge of the analysis grid, which contains every signal
      event"
  f
      a cell's cross section integrated over its box, in cm^2/nucleon.
      Paper: "the cell-integrated cross section f (an integral over the box, not a differential density)"
  g
      a generator's prediction for the same cell and quantity as f; f/g is data over prediction.
      Paper: "Data over prediction, f/g"
  C_e, C_total
      C_e holds the statistical, flux, interaction, detector, lateral and normalization groups; C_total = C_e +
      C_model.
      Paper: "The statistical, flux, interaction, detector, lateral and normalization groups, with a
      training-seed block that is zero in every cell, form C_e, and C_total=C_e+C_model."
  lateral
      uncertainties that shift the reconstructed muon kinematics and beam angle instead of reweighting events.
      Paper: "the lateral uncertainties shift the reconstructed muon kinematics and beam angle rather than
      reweighting events"
  C_model (C_model_abs)
      the dependence on the prior's generator shape. The data product names the matrix C_model_abs (an absolute
      covariance, like every matrix here); tab-groups16.csv's rel_sigma_C_model is the same matrix (checked by
      the build).
      Paper: "The model term C_model is built from the change in the unfolded data when the prior is reweighted
      to GENIE + MEC, NuWro and GiBUU in turn."
  C_resp
      the response to a one-standard-deviation scale of the reconstructed recoil energy.
      Paper: "The response term C_resp is the response of the result to a one-standard-deviation scale of the
      reconstructed recoil energy in the simulation."
  C_PL,5D
      the run-period block, added after the data were seen; files are given with and without it.
      Paper: "The run-period block C_PL,5D includes this inconsistency in the reported covariance."
  reported
      the reported covariance, C_total + C_resp + C_PL,5D.
      Paper: "The reported covariance of the sixteen-cell result is C_total+C_resp+C_PL,5D."
  V_g
      a prediction's own finite-sample covariance (diagonal), added in every comparison with a prediction.
      Paper: "V_g, the diagonal covariance from the finite size of the prediction's own simulated sample"
  shape-only
      a chi^2 with the normalization freed (one fewer degree of freedom).
      Paper: "Shape-only chi^2 frees the normalization"
  fake-data chi^2, z
      the mean unfolded result at a truth against that truth, on the 16 cells; z is a cell's bias over its
      uncertainty under the same covariance. A truth is flagged at p < 0.01 or a cell with |z| > 2.
      Paper: "compare the mean unfolded result with each truth on the 16 cells through chi^2 with 16 degrees of
      freedom"
      Paper: "where z is the cell's bias divided by its uncertainty under the same covariance"
  2D four-block covariance
      the two-dimensional result's covariance: systematic universes (with the normalization), statistical, run
      period and training seed.
      Paper: "The two-dimensional covariance is the sum of four blocks, each from LightGBM unfoldings with the
      central value's estimator: systematic universes (187 universes, including the normalization), statistical
      (300 bootstrap replicas), run period (three period groups), and training seed (five seed settings, so that
      its own size is poorly determined)."

TRUTHS (tab-fd16.csv; * marks the paper's closure tests, where the truth is the simulation's own)
  nominal         simulation prior *
  A7_mnvtune      Tune v1, hybrid *
  A7_genie_cv     GENIE CV, hybrid
  A7_genie_mec    GENIE + MEC, hybrid
  W2              GENIE + MEC, (E_avail,W) shape
  A7_nuwro        NuWro, hybrid
  W1              NuWro, E_avail shape
  W3              NuWro, (p_T,p_par,E_avail) shape
  closure_nuwro   NuWro shape, noise-free closure
  stage0c_gibuu   GiBUU, E_avail shape
  A7_gibuu        GiBUU, hybrid
  q3              synthetic q3 tilt
  All 12 are the paper's graded truths.

FILES (package/)

* tab-result16_cells.csv   [paper label tab:result16; table or figure number: to be completed at release]
    The 16 cells: each box, f, and each matrix's relative uncertainty.
    - cell: R00-R15
    - pt_lo, pt_hi; pz_lo, pz_hi; q3_lo, q3_hi: box edges in GeV/c (pz is p_par)
    - eavail_lo, eavail_hi; W_lo, W_hi: box edges in GeV
    - f: cell-integrated cross section, cm^2/nucleon
    - rel_sigma_<M>: sqrt(diag M)/f for each matrix M (fraction)
    Scope: see "the 16-cell result and its covariance" below.

* sec-cov16_reported.csv   [paper label sec:cov16; table or figure number: to be completed at release]
    The reported covariance C_total + C_resp + C_PL,5D.
    - cell, R00-R15: a 16 x 16 matrix in (cm^2/nucleon)^2, rows and columns in the order R00-R15
    Scope: see "the 16-cell result and its covariance" below.

* sec-cov16_C_total_plus_C_resp.csv   [paper label sec:cov16; table or figure number: to be completed at release]
    The covariance without C_PL,5D.
    - cell, R00-R15: a 16 x 16 matrix in (cm^2/nucleon)^2, rows and columns in the order R00-R15
    Scope: see "the 16-cell result and its covariance" below.

* sec-cov16_C_e.csv   [paper label sec:cov16; table or figure number: to be completed at release]
    C_e.
    - cell, R00-R15: a 16 x 16 matrix in (cm^2/nucleon)^2, rows and columns in the order R00-R15
    Scope: see "the 16-cell result and its covariance" below.

* sec-cov16_C_model_abs.csv   [paper label sec:cov16; table or figure number: to be completed at release]
    C_model.
    - cell, R00-R15: a 16 x 16 matrix in (cm^2/nucleon)^2, rows and columns in the order R00-R15
    Scope: see "the 16-cell result and its covariance" below.

* sec-cov16_C_resp.csv   [paper label sec:cov16; table or figure number: to be completed at release]
    C_resp.
    - cell, R00-R15: a 16 x 16 matrix in (cm^2/nucleon)^2, rows and columns in the order R00-R15
    Scope: see "the 16-cell result and its covariance" below.

* sec-cov16_C_PL5D.csv   [paper label sec:cov16; table or figure number: to be completed at release]
    C_PL,5D.
    - cell, R00-R15: a 16 x 16 matrix in (cm^2/nucleon)^2, rows and columns in the order R00-R15
    Scope: see "the 16-cell result and its covariance" below.

* tab-corr16.csv   [paper label tab:corr16; table or figure number: to be completed at release]
    The correlation matrix of the reported covariance.
    - cell, R00-R15: a dimensionless 16 x 16 matrix, rows and columns in the order R00-R15
    Scope: see "the 16-cell result and its covariance" below.

* tab-groups16.csv   [paper label tab:groups16; table or figure number: to be completed at release]
    Each group's relative uncertainty per cell.
    - cell: R00-R15
    - rel_sigma_<group>: sqrt(diag)/f of that group (fraction; the paper prints percent); reported = C_total +
      C_resp + C_PL,5D
    Scope: see "the per-group uncertainties" below.

* tab-fd16.csv   [paper label tab:fd16; table or figure number: to be completed at release]
    Fake-data tests at the 12 graded truths (see TRUTHS), under the reported covariance and under C_total.
    - truth: the truth's id (see TRUTHS)
    - <cov>_matrix: the covariance the test uses; <cov> is reported or C_total
    - <cov>_without_component: when the truth is a generator that also enters C_model, that generator's
      component is removed from the covariance; this names it (empty otherwise)
    - <cov>_chi2, _ndf, _p: chi^2 of the mean unfolded result against the truth on the 16 cells, its degrees
      of freedom and p-value
    - <cov>_cells_abs_z_gt_2: the cells with |z| > 2, space-separated (empty when none): a list, not a count
    - <cov>_max_abs_z: the largest |z| over the cells
    - <cov>_n_pseudo_experiments: pseudo-experiments averaged; 1 marks a noise-free closure
    Scope: see "the fake-data tests" below.

* sec-fd16_tunes.csv   [paper label sec:fd16; table or figure number: to be completed at release]
    The two held-out GENIE v3 tunes, under the reported covariance.
    - tune: the GENIE v3 tune
    - record: the test: an ensemble of pseudo-experiments, or a noise-free closure
    - matrix, chi2, ndf, p, cells_abs_z_gt_2, max_abs_z, n_pseudo_experiments: as in tab-fd16.csv
    - max_abs_z_cell: the cell with the largest |z| (tab-fd16.csv has no such column)
    Scope: see "the held-out tunes" below.

* sec-fd16_validity.csv   [paper label sec:fd16; table or figure number: to be completed at release]
    Each cell's class under the two validity rules.
    - atlas_A1: at least 5000 effective simulated events (here those of the simulation's weights)
    - atlas_A2: a data statistical uncertainty below 15 %
    - atlas_A3: |z| <= 2 at each of the 12 graded truths under the reported covariance
    - atlas_mc_neff_truth, atlas_stat_rel: the effective number of simulated events, and the data's relative
      statistical uncertainty (fraction), behind A1 and A2
    - atlas_class: valid if A1, A2 and A3 hold, else not valid
    - prior_S_b, prior_S_g (_raw, _sub): the spread of the cell's fake-data bias over the graded truths (S_b)
      and of the generator predictions (S_g), each in two noise treatments
    - prior_rho_<b>_over_<g>: S_b / S_g in the four combinations of the two treatments
    - prior_class: valid if rho < 0.5 in all four, else not valid
    Scope: see "the per-cell validity rules" below.

* sec-repro2d_benchmark.csv   [paper label sec:repro2d; table or figure number: to be completed at release]
    The two-dimensional benchmark against the published result, and the run-period rows.
    - quantity: an id
    - description: what it is
    - value: the full-precision value
    - printed: the value as the paper prints it
    - unit: its unit (1 is dimensionless)
    Scope: see "the 2D benchmark" below.

* sec-repro2d_result2d.csv   [paper label fig:validation; table or figure number: to be completed at release]
    The two-dimensional result on the 205 reported bins.
    - global_id: pt_bin * 16 + ppar_bin
    - pt_bin, ppar_bin: bin indices from 0
    - pt_lo, pt_hi, ppar_lo, ppar_hi: bin edges in GeV/c
    - d2sigma_dpt_dppar: d^2 sigma / (dp_T dp_par) in cm^2/nucleon per (GeV/c)^2
    Scope: see "the 2D result per bin and its covariance" below.

* sec-uq2d_Q.csv   [paper label sec:uq2d; table or figure number: to be completed at release]
    2D covariance block: the four-block covariance: universe + stat + training seed + run period.
    - global_id, then the 205 ids: a 205 x 205 matrix in (cm^2/nucleon per (GeV/c)^2)^2, rows and columns in
      the order of sec-repro2d_result2d.csv
    Scope: see "the 2D result per bin and its covariance" below.

* sec-uq2d_universe.csv   [paper label sec:uq2d; table or figure number: to be completed at release]
    2D covariance block: systematic universes (including the normalization).
    - global_id, then the 205 ids: a 205 x 205 matrix in (cm^2/nucleon per (GeV/c)^2)^2, rows and columns in
      the order of sec-repro2d_result2d.csv
    Scope: see "the 2D result per bin and its covariance" below.

* sec-uq2d_stat.csv   [paper label sec:uq2d; table or figure number: to be completed at release]
    2D covariance block: statistical.
    - global_id, then the 205 ids: a 205 x 205 matrix in (cm^2/nucleon per (GeV/c)^2)^2, rows and columns in
      the order of sec-repro2d_result2d.csv
    Scope: see "the 2D result per bin and its covariance" below.

* sec-uq2d_c08.csv   [paper label sec:uq2d; table or figure number: to be completed at release]
    2D covariance block: training seed.
    - global_id, then the 205 ids: a 205 x 205 matrix in (cm^2/nucleon per (GeV/c)^2)^2, rows and columns in
      the order of sec-repro2d_result2d.csv
    Scope: see "the 2D result per bin and its covariance" below.

* sec-uq2d_C_PL.csv   [paper label sec:uq2d; table or figure number: to be completed at release]
    2D covariance block: run period.
    - global_id, then the 205 ids: a 205 x 205 matrix in (cm^2/nucleon per (GeV/c)^2)^2, rows and columns in
      the order of sec-repro2d_result2d.csv
    Scope: see "the 2D result per bin and its covariance" below.

* sec-uq2d_s5_total.csv   [paper label sec:uq2d; table or figure number: to be completed at release]
    2D covariance block: universe + stat + training seed, the covariance without the run-period block.
    - global_id, then the 205 ids: a 205 x 205 matrix in (cm^2/nucleon per (GeV/c)^2)^2, rows and columns in
      the order of sec-repro2d_result2d.csv
    Scope: see "the 2D result per bin and its covariance" below.

* tab-gen16.csv   [paper label tab:gen16; table or figure number: to be completed at release]
    chi^2 of each generator prediction. Illustrative, descriptive; not for fitting or constraining models.
    - prediction, label: the prediction
    - <cov>_<kind>_chi2, _ndf, _p: <cov> is reported or without_C_PL5D; <kind> is total or shape_only
      (normalization freed); V_g is added to the covariance in every chi^2
    - n_cells: cells compared (GiBUU: the 8 cells below p_par 4.5 GeV/c)
    Scope: see "the generator comparisons" below.

* tab-cmodel16.csv   [paper label tab:cmodel16; table or figure number: to be completed at release]
    How each prediction's chi^2 changes with C_model. Illustrative, descriptive; not for fitting or constraining
    models.
    - matrix, prediction, chi2_kind: as in tab-gen16.csv
    - chi2_carbon_ratios: the chi^2 as reported: C_model's NuWro and GiBUU shape ratios taken from carbon
      (equals tab-gen16.csv's chi^2)
    - chi2_CH_ratios, chi2_C_model_doubled, chi2_C_model_removed: the chi^2 with those ratios from CH, with
      C_model doubled, and with C_model removed
    - delta_CH, delta_doubled, delta_removed: each minus chi2_carbon_ratios
    Scope: see "the generator comparisons" below.

* fig-ratio16.csv   [paper label fig:ratio16; table or figure number: to be completed at release]
    The data behind the ratio figure. Illustrative, descriptive; not for fitting or constraining models.
    - f_data, g_prediction: cm^2/nucleon
    - f_over_g: data over prediction
    - sigma_reported_over_f: sqrt(diag reported)/f (fraction)
    - bar_half_width: f_over_g x sigma_reported_over_f: the data's reported uncertainty only, without V_g
    Scope: see "the generator comparisons" below.

SCOPE OF USE, BY FILE
  the 16-cell result and its covariance:
    - Illustrative output of the estimator on data, not a measurement; not for fitting or for constraining
      models.
    - Not a coverage or calibration statement: interval coverage has not been validated.
    - C_PL,5D was added after the data were seen and is given with and without; its size is not validated,
      since a block built from the observed differences contains them by construction.
    - No statement of the cause of the run-period difference, or of which period is right.
  the per-group uncertainties:
    - As for the 16-cell result above.
    - C_resp does not shift neutron or muon energy deposits.
  the fake-data tests:
    - Bias tests on simulated pseudo-data: no statement about data against generators, coverage, held-out
      truths or the detector response.
    - No reading of the difference between the two covariance columns.
  the held-out tunes:
    - A bias test at two held-out GENIE v3 tunes, not a coverage test. The paper's status for it: "Pass; not
      independent".
  the per-cell validity rules:
    - Per-cell diagnostics of the estimator at simulated truths: not a measurement and not a coverage
      statement; no reported value changes, and a cell that is not valid is not thereby excluded, wrong or
      unreported.
    - A1-A3 (the atlas_* columns) are this analysis's implementation of the ATLAS User Guide's thresholds, the
      usage recommendations the paper cites (ATLAS Collaboration, Phys. Rev. Lett. 133, 261803 (2024),
      arXiv:2405.20041). The guide's recommended test of correlation assumptions on pseudo-data (its item 5)
      is not met here.
    - The prior_* rule and its threshold of 0.5 are this analysis's own, not ATLAS's.
  the 2D benchmark:
    - The adopted two-dimensional result; no coverage validation is claimed for it.
    - It does not show that the five-observable result reproduces the full distribution, beyond this benchmark
      with its stated limits. The paper's status for the comparison: "Descriptive; source not identified".
    - The run-period rows do not say which period is right, nor the cause of the shape difference or of the
      run-period step.
  the 2D result per bin and its covariance:
    - As for the 2D benchmark above.
    - The four-block covariance does not include the generator-shape dependence C_model, which the paper
      reports as a separate covariance.
  the generator comparisons:
    - Illustrative, descriptive; not for fitting or constraining models.
    - Not a validation of the reported covariance or of C_model, and not a generator exclusion; no reading of
      the figure.
    - NuWro: the part of its free-proton sample generated at 50-100 GeV is flagged, because the events lost to
      generator aborts there were not shown to be negligible. GiBUU: corrected to CH with its own free-proton
      sample, which failed its sampling-closure check.

NOT INCLUDED
  - The published MINERvA result, which is cited, not redistributed.
  - The paper's validation-programme table (tab:outcomes) as a table: it is a text table, and its numerical
    entries are in the files above.
  - Per-group 16 x 16 matrices for the groups inside C_e: the source records give their relative uncertainties
    only (tab-groups16.csv).

NOT YET AVAILABLE (pending/)
  - ENS1.txt: the ensemble-averaged variant of the estimator (96 fits): its stability and bias results.
  - FD-PRR.txt: a study in simulation of what moves the estimator's retained prior on the 16 cells, with binned
    unfolding (IBU) on the same fake data.
  - LL5D.txt: the like-for-like five-observable coverage test at the two held-out GENIE v3 tunes.
  - V-HALF.txt: a per-cell validity rule: the bias at most half of the truth's departure from the prior.

REBUILD AND CHECK
  From the root of the source repository, at the version that holds this package:
    python3 docs/orchestration/state/2d-closeout/stageF/methods/result-package-20261109/build_package.py --check
  This rebuilds every file from the source records and requires each to equal the file here byte for byte, and
  every value to equal the paper's printed value. It is a transcription check, not a test of the results; it
  recomputes no physics. --self-test plants a wrong value in each kind of check and confirms that the build
  refuses it. Python 3, standard library only. PROVENANCE.txt lists the source records, their sha256 digests
  and the statements each scope rests on. SHA256SUMS lists every file.
