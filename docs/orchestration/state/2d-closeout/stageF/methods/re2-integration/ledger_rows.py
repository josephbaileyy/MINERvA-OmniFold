#!/usr/bin/env python3
"""Write the M and F rows of ledger.tsv (after the V rows that apply_values.py generated).

usage (from the repository root): python3 docs/orchestration/state/2d-closeout/stageF/methods/re2-integration/ledger_rows.py

Each M row names a new values.tex macro and the product field the checker recomputes it from. Each F row is one fact of a
wording draft: the text that must print, the text that must not, and the committed source line it comes from. The rows are
written here, not typed into the TSV, so that a reviewer reads the claims and their sources side by side; check_ledger.py
is what verifies them. Re-running replaces everything after the "# M rows:" marker.
"""
from pathlib import Path
D = Path('docs/orchestration/state/2d-closeout/stageF/methods/re2-integration')
S = 'docs/orchestration/state/2d-closeout/stageF/methods'
CM = f'{S}/re2/run/partc_r2/partc-r2/cmodel/cmodel_R.json'
VT = f'{S}/re2/run/partc_r2/partc-r2/values_table.tsv'
RP = f'{S}/re2/RE2-PARTC-REPORT.md'
RB = f'{S}/re2/RE2-PARTB-REPORT.md'
A3 = f'{S}/re2/RE2-PARTC-A3-REPORT.md'
TR = f'{S}/re2/run/partc_r2/partc-r2/receipts/figs/tension_report.txt'
TRP = 'docs/orchestration/receipts/2d-lgbm42-20261011/tension_report.txt'
DM = 'docs/orchestration/DECISION-20261024-joseph-2d-model-dependence-component.md'
DA = 'docs/orchestration/DECISION-20261024-joseph-adopt-re2-2d-refined.md'
DS = 'docs/orchestration/DECISION-20261023-joseph-2d-refined-integrate-ci.md'
PV = f'{S}/pv2d/REPORT.md'
UM = '2d-unfolding/re2/partc/re2c_values_unmatched.tsv'
EST = 'docs/orchestration/registry/ESTIMATORS.tsv'
S5 = f'{S}/re2/run/partc_r2/partc-r2/s5/s5.json.gz'
AN = f'{S}/re2/run/partc_r2/partc-r2/periods/analysis.json'
PL = f'{S}/re2/run/partc_r2/partc-r2/playlist/playlist_term.json'
CB = f'{S}/re2/run/partc_r2/partc-r2/combination/combination.json'
R1 = f'{S}/re1/RE1-REPORT-2.md'
VL = 'VALIDATION_LEDGER.md'
M = [
 ('M-cmodelMedian', 'cmodelMedian', CM, 'cell_rel_sigma.C_model.median', '100', '.2f'),
 ('M-qrCmodelMedian', 'qrCmodelMedian', CM, 'cell_rel_sigma.Q_R_plus_C_model.median', '100', '.2f'),
 ('M-cmodelIntegral', 'cmodelIntegral', CM, 'integral_rel_sigma.C_model', '100', '.2f'),
 ('M-sigTwoDPurity', 'sigTwoDPurity', VT, 'm-sigTwoD.purity_value', '1', '.3e'),
 ('M-chiPaperPurity', 'chiPaperPurity', VT, 'm-chiPaper.purity_value', '1', '.2f'),
]
F = [
 # W1: C_model beside Q_R (paper)
 ('W1-p1', 'paper_body.tex', r"dependence on the regularization; the dependence on the prior's generator shape is reported beside it (below).", r"dependence on the unfolding model and its regularization.", DM, "Q, which becomes Q_R once RE-2 lands, stays the headline 2D uncertainty."),
 ('W1-p2', 'paper_body.tex', r"$C_{\mathrm{model}}=\sum_k s_k s_k^{\mathsf{T}}$", '-', DM, "C_model = Σ_k s_k s_kᵀ"),
 ('W1-p3', 'paper_body.tex', r"It is a measure of generator-shape model dependence, not a calibrated bound on the unfolding bias.", '-', CM, "generator-shape model dependence; not a calibrated bound"),
 ('W1-p4', 'paper_body.tex', r"(GENIE with meson-exchange currents, NuWro, or GiBUU) to that of GENIE, with its normalization kept.", '-', PV, "The vertices are pure shape departures (κ preserves the prior's truth weight)"),
 ('W1-p5', 'paper_body.tex', r"which leaves the integrated uncertainty at \SI{\uqIntegral}{\percent}, and it does not test the model dependence of the normalization.", '-', RP, "| **`Q_R` + C_model, the secondary users' total** | **7.90 %** | 12.32 % | 13.74 % | 24.49 % | 4.759 % |"),
 ('W1-p6', 'paper_body.tex', r"it omits the learner dependence and $C_{\mathrm{model}}$, and the two bands are", r"it omits the learner dependence, and the two bands are", RP, "diag Q_R = diag S5_R + diag C_PL_R"),
 # W1: note
 ('W1-n1', 'sec_systematics.tex', r"\item the dependence on the generator shape of the prior, which is reported beside the covariance as $C_{\mathrm{model}}$ (below).", r"\item the dependence on the unfolding model and its regularization, whose estimate requires independent-generator samples", DM, "C_model,2D is built and reported as a separate named covariance."),
 ('W1-n2', 'sec_systematics.tex', r"Each generator enters as one fully correlated component, unscaled, so $C_{\mathrm{model}}$ has rank three.", '-', DM, "C_model has rank 3"),
 ('W1-n3', 'sec_systematics.tex', r"(84th percentile \SI{7.10}{\percent}, maximum \SI{21.10}{\percent})", '-', RP, "| C_model | 3.71 % | 7.10 % | 8.50 % | 21.10 % | 0.029 % |"),
 ('W1-n4', 'sec_systematics.tex', r"(84th percentile \SI{12.32}{\percent}, maximum \SI{24.49}{\percent})", '-', RP, "| **`Q_R` + C_model, the secondary users' total** | **7.90 %** | 12.32 % | 13.74 % | 24.49 % | 4.759 % |"),
 ('W1-n5', 'sec_systematics.tex', r"these 52 cells hold \SI{59.4}{\percent} of the trace of $C_{\mathrm{model}}$ and carry most of its large shifts.", '-', RP, "the 52 step-adjacent cells hold 59.4 % of tr C_model"),
 ('W1-n6', 'sec_systematics.tex', r"The cells beside a step of more than 0.1 in a generator's reweighting ratio drawn by its construction", '-', PV, "One rule throughout** (`report_tables.classify_cell`, threshold 0.1)"),
 ('W1-r1', 'primer_body.tex', r"That combination is \SI{\cmodelMedian}{\percent} in a typical cell, and added to the error bars it raises their typical size from \SI{\uqMedian}{\percent} to \SI{\qrCmodelMedian}{\percent}.", r"the tree learner, and the dependence on the unfolding model.", DA, "The users' total is `Q_R` + C_model."),
 ('W1-r2', 'primer_body.tex', r"because the three changes alter only the shape, not the total.", '-', PV, "The vertices are pure shape departures (κ preserves the prior's truth weight)"),
 # W2: comparison with the published result
 ('W2-p1', 'paper_body.tex', r"at the central value's seed, the refined negative-weight subtraction lowers the LightGBM distance from $\chiPaperPurity$ to $\chiPaper$.", r"depends on the learner: ten LightGBM training seeds give 2.64--2.75", VT, "m-chiPaper\tN/values.tex:\\chiPaper\t2.65\t2.27"),
 ('W2-p2', 'paper_body.tex', r"uses the covariance without $C_{\mathrm{model}}$, because neither has a component for the residual dependence on the prior's generator shape:", '-', DM, "neither Q nor the published uncertainty carries the residual dependence on the prior's generator shape"),
 ('W2-p3', 'paper_body.tex', r"the published analysis chose its ten iterations in a fake-data study and assigns no uncertainty to the remaining dependence", '-', DM, "MINERvA chose its 10 iterations from a fake-data study of 10 GENIE-reweighted predictions"),
 ('W2-p4', 'paper_body.tex', r"The iteration counts differ (ten there, five here), so we make no statement about the size of the published analysis's residual.", '-', DM, "Iteration counts differ (10 there, 5 here), so no claim is made about the size of the published analysis's residual."),
 ('W2-p5', 'paper_body.tex', r"The central value and the exact-split cross-check, which differ in learner and in background treatment, differ by a per-bin median of \SI{1.03}{\percent}", r"The two learners differ by a per-bin median of", VT, "lit-learner-median-pb373\tN/paper_body.tex:373\t0.98\t1.03"),
 ('W2-n1', 'sec_results.tex', r"The comparison leaves out the generator-shape component $C_{\mathrm{model}}$ (\S\ref{sec:uq-2d-scope}), because the published uncertainty has no such component either; with it, the per-bin median is \SI{\qrCmodelMedian}{\percent}.", '-', DM, "The reproduction comparison with MINERvA's published result is made with Q alone, like for like."),
 ('W2-n2', 'sec_results.tex', r"At the central value's seed, the refined negative-weight subtraction of the quoted result lowers the LightGBM distance from $\chiPaperPurity$ to $\chiPaper$.", r"The choice of GBDT estimator spreads the distance over about one unit, a methodological band: the exact-split", VT, "m-chiPaper\tN/values.tex:\\chiPaper\t2.65\t2.27"),
 ('W2-a1', 'app_statmethods.tex', r"LightGBM, 5 iter, seed 42 & $2.654$ & $0.564$ \\", '-', VT, "cfg-lgbm42-chi2\tN/app_statmethods.tex:1000\t2.654\t2.270"),
 ('W2-a2', 'app_statmethods.tex', r"All rows except the quoted one use the purity-based subtraction.", '-', EST, "Paper/note configuration (a): nominal LightGBM (100 trees, 8 leaves, learning rate 0.1), purity-based subtraction"),
 ('W2-e1', 'sec_execsummary.tex', r"A generator-shape model-dependence component, reported beside that uncertainty and absent from the published one, raises the per-bin median to \SI{\qrCmodelMedian}{\percent}", '-', DM, "Users** are given Q + C_model as the total."),
 ('W2-s1', 'sec_summary.tex', r"whose size depends on the estimator (exact-split cross-check $\chiPaperExact$).", r"whose size depends on the learner (exact-split cross-check", RP, "| `\\chiPaper`, χ²/ndf against the published covariance | 2.65 | 2.27 |"),
 # W3: RO-FPS
 ('W3-1', 'sec_fps.tex', r"is $\SI{\sigTwoD}{cm^2/nucleon}$, \SI{\roFpsDiff}{\percent} lower, so the control no longer reproduces it.", r"reproduces the 2D total at the printed precision", RP, "**It does not reproduce.** The two values differ by −0.14 %."),
 ('W3-2', 'values.tex', r"\newcommand{\roFpsDiff}{0.14}", '-', RP, "The two values differ by −0.14 %."),
 ('W3-3', 'sec_fps.tex', r"The control's total, $\SI{\sigTwoDPurity}{cm^2/nucleon}$, equals at the printed precision that of the purity-subtracted 2D central values (exact-split and LightGBM).", '-', VL, "Control unfold total 3.073e-38 = the frozen production"),
 # W4: S2
 ('W4', 'sec_systematics.tex', r"Because the background simulation is resampled in every replica, the separable background-only term is contained in the statistical block.", r"(a median 0.26 of the statistical $\sigma$)", RP, "S1 resamples the background in both arms"),
 # W5: \fpsAbove
 ('W5-1', 'sec_fps.tex', r"compared with $\SI{\sigTwoDPurity}{cm^2/nucleon}$ for the control unfold in the restricted phase space.", r"\SI{\fpsAbove}{\percent} above the restricted-phase-space", RP, "1 declared failure**, **`\\fpsAbove` (46)**, not regenerated."),
 ('W5-2', 'sec_summary.tex', r"against \SI{\sigTwoDPurity}{cm^2/nucleon} for its control unfold in the restricted phase space.", r"(\SI{\fpsAbove}{\percent} above the restricted phase space)", VL, "**FPS total cross section 4.502e-38 cm²/nucleon**"),
 # W6: the hand sites of re2c_values_unmatched.tsv
 ('W6-01', 'sec_results.tex', r"The eightfold increase lies entirely in the off-diagonal", '-', TR, "=> 7.8x inflation comes purely from the off-diagonal"),
 ('W6-02a', 'sec_results.tex', r"the largest has a paper-covariance-standardized component of magnitude $4.8$, and the next nine $3.4$--$3.8$.", r"of magnitude about $4$--$5$", TR, "0   3.549e-09      23/205          -4.75"),
 ('W6-02b', 'sec_results.tex', r"and the next nine $3.4$--$3.8$.", '-', TR, "1   4.314e-10       9/205          -3.78"),
 ('W6-02c', 'sec_results.tex', r"and the next nine $3.4$--$3.8$.", '-', TR, "9   6.708e-09      27/205          +3.36"),
 ('W6-03', 'sec_results.tex', r"two of the five largest contributors lie in the smallest-$\lambda$ tenth", '-', TR, "fraction of top-5 contributors in the smallest-10%% lambda band: 0.40"),
 ('W6-05', 'sec_systematics.tex', r"It has rank two: with three period groups, its own size is poorly determined.", r"about 1.8 effective degrees of freedom", PL, '"rank": 2,'),
 ('W6-06', 'sec_systematics.tex', r"It has rank two: with three period groups, its own size is poorly determined.", r"at the order of \SI{100}{\percent}", UM, "'at the order of 100%' (size of C_PL poorly determined): heuristic from the dof statement; no source field"),
 ('W6-07', 'sec_systematics.tex', r"which is about 3.7 times that of the training-seed block used here", r"which is about three times the training-seed block", S5, '"sigma_c08_over_sigma_ml_median": 0.26946226226768916,'),
 ('W6-08', 'sec_method.tex', r"With the purity-based subtraction (configuration~(a)), the seed-42 central value differs from the seed-1 one by a per-bin median of \SI{0.18}{\percent} (maximum \SI{1.79}{\percent}), or 0.30 (maximum 1.28)", '-', UM, "E_U (seed 42) vs the seed-1 central value, per-bin median; no field in the allowed sources"),
 ('W6-12', 'sec_method.tex', r"Against the ten purity-subtracted LightGBM central values at seeds 1--10 it is mildly over-dispersed (RMS standardized difference 1.28, maximum 4.25).", '-', UM, "E_U vs the ten LightGBM seeds 1-10, RMS standardized difference"),
 ('W6-14', 'sec_3d.tex', r"Both use refined negative-weight subtraction with a 400-tree, 31-leaf refinement;", r"On the 2D data, the background treatment alone moves cells by a median of", EST, "with --bkg-mode negweight-refined and the Stay-Positive refinement classifier at 400 trees, 31 leaves"),
 ('W6-16', 'sec_systematics.tex', r"two independent estimators give $\rho=0.87$--$0.90$", '-', UM, "published-side (second rho estimator from the paper ancillary)"),
 ('W6-17', 'sec_results.tex', r"against \SI{4.01}{\percent} for the published flux block", '-', UM, "published-side (median of the published flux block)"),
 ('W6-18', 'paper_body.tex', r"The published flux uncertainty (median \SI{4.01}{\percent})", '-', UM, "published-side (published flux median)"),
 ('W6-19', 'app_statmethods.tex', r"& $4.61\%$ & $4.76\%$ \\", '-', UM, "published-side (paper width-weighted total sigma, = \\uqPaperIntegral)"),
 ('W6-20', 'sec_execsummary.tex', r"within about one percent, with a correlated shape difference", '-', VT, "m-ratioTot\tN/values.tex:\\ratioTot\t1.011\t1.010"),
 ('W6-21', 'primer_body.tex', r"used with different ways of removing background, give answers that differ by about one percent in a typical cell", r"two software implementations of the tree learner give answers", VT, "lit-learner-median-180\tN/sec_systematics.tex:180\t0.98\t1.03"),
 ('W6-23', 'app_statmethods.tex', r"= 1.011$, median bin ratio $1.006$), and the per-bin pull RMS against the paper covariance is only $0.598$ for the exact-split cross-check", '-', UM, "exact-split history (the configuration (b) 'paradox' section): unchanged by RE-2; integration confirms the classification"),
 ('W6-25', 'app_statmethods.tex', r"The $+1.1\%$ normalization offset", '-', UM, "exact-split history (the same section): unchanged by RE-2; integration confirms"),
 # W6-extra: sites found in the stale-value sweep, outside the 25 listed rows
 ('X1', 'sec_systematics.tex', r"\SI{0.39}{\percent} in a marginal bin (the highest $\pPar$ bin; at most", r"(the lowest $\pPar$ bin;", AN, "-0.3948"),
 ('X2', 'sec_systematics.tex', r"and the $\pPar$ projections by at most \SI{21}{\percent}; it carries a", r"(at 6--\SI{7}{GeV/c})", CB, '"functional_sigma_increase_pct_max": 20.65589185827996,'),
 ('X3', 'app_statmethods.tex', r"its systematic-only rank is $120$, below the $138$ of our universe block", r"below the $137$ of our universe block", VT, "rank-univ-1e12\tN/app_statmethods.tex:743\t137\t138"),
 ('X4', 'sec_method.tex', r"and from the quoted central value, which also differs from it in background treatment, by \SI{1.03}{\percent} (maximum \SI{17.6}{\percent}).", '-', VT, "lit-learner-max-181\tN/sec_systematics.tex:181\t12.2\t17.6"),
 ('X5', 'app_negweight.tex', r"the purity-based 2D covariance on its 205 reported cells (the quoted covariance when the test ran)", r"the quoted 2D covariance on its 205 reported cells", R1, "σ_total: `sqrt(diag(total_plus_C_PL))` of Q `8ccb4d72…`, the adopted 2D uncertainty;"),
 # W7: the adopted refined result and the configuration labels
 ('W7-p1', 'paper_body.tex', r"The two-observable central value uses configuration~(f): the learner and seed of configuration~(a) with negative-weight background subtraction and the refinement capacity of configuration~(e).", r"The two- and five-observable central values use configuration~(a)", DA, "The adopted 2D result is `E_R`, with `Q_R` as its headline uncertainty."),
 ('W7-p2', 'paper_body.tex', r"\pcell{0.24\columnwidth}{(f) as (a), refined} & \pcell{0.30\columnwidth}{negative weights; refinement 400 trees, 31 leaves}", r"2D and 5D central values; 2D and 5D covariances; 3D and 4D closures", EST, "random_state seed + 3 = 45"),
 ('W7-p3', 'paper_body.tex', r"The two-dimensional result therefore uses the refined estimator, configuration~(f)", r"being moved to the refined estimator", DA, "The adopted 2D result is `E_R`, with `Q_R` as its headline uncertainty."),
 ('W7-p4', 'paper_body.tex', r"and (f) is (a) with the refinement of (e), its refinement classifier seeded at the estimator seed plus three.", '-', RB, "recorded `random_state` equal to its estimator seed + 3 (B10)"),
 ('W7-p5', 'paper_body.tex', r"area-weighted total agrees with the configuration-(f) two-dimensional result to \SI{0.141}{\percent}", r"agrees with the configuration-(a) two-dimensional result", VT, "pap-closure-3d\tN/paper_body.tex:475\t0.001"),
 ('W7-p0', 'paper_body.tex', r"\pcell{0.50\columnwidth}{2D covariance, median \SI{\uqMedian}{\percent} per bin} & \pcell{0.12\columnwidth}{(f)}", r"\pcell{0.50\columnwidth}{2D covariance, median \SI{\uqMedian}{\percent} per bin} & \pcell{0.12\columnwidth}{(a)}", DA, "The adopted 2D result is `E_R`, with `Q_R` as its headline uncertainty."),
 ('W7-p0b', 'paper_body.tex', r"\pcell{0.50\columnwidth}{2D integral within about 1\%; correlated shape difference} & \pcell{0.12\columnwidth}{(f)}", '-', DA, "The adopted 2D result is `E_R`, with `Q_R` as its headline uncertainty."),
 ('W7-e3', 'sec_execsummary.tex', r"the configuration-(e) 3D marginal agrees with the configuration-(f) 2D result", r"the configuration-(e) 3D marginal agrees with the configuration-(a) 2D result", DA, "The adopted 2D result is `E_R`, with `Q_R` as its headline uncertainty."),
 ('W7-y1', 'sec_systematics.tex', r"The central value and the exact-split cross-check, which differ in learner and in background treatment, differ by a per-bin median of \SI{1.03}{\percent}", r"The LightGBM central value and the exact-split cross-check differ by a per-bin median of", VT, "lit-learner-median-180\tN/sec_systematics.tex:180\t0.98\t1.03"),
 ('W7-n1', 'sec_method.tex', r"Six estimator configurations, labeled (a)--(f) as in the article", r"Five estimator configurations, labeled (a)--(e)", EST, "a-refined-400-31"),
 ('W7-n2', 'sec_method.tex', r"The 2D central value and its covariance were rebuilt with configuration~(f) after a two-dimensional closure test with backgrounds found the purity bias", r"In two and five dimensions, the central values and their covariances use purity-based subtraction", DS, "The adopted 2D result moves to the refined estimator,"),
 ('W7-n3', 'sec_method.tex', r"A central unfold at seed~45 differs from the seed-42 one by at most \SI{1.4}{\percent} in a cell.", '-', RB, "| PB-pow-S4CV | differs | `S4CV_s45` | `run:ER` | 0.0142 |"),
 ('W7-n4', 'sec_method.tex', r"The quoted central value records its run configuration; it repeats to $9\times10^{-12}$", r"There is no execution log or recorded run configuration for the seed-42 central value itself.", RB, "| PB-ER-rep | le | `ER` | `run:C0_cv` | 9.17e-12 |"),
 ('W7-n5', 'sec_method.tex', r"equals the refined 2D data unfold of App.~\ref{sec:negweight-footing} to $7\times10^{-12}$", '-', RB, "| PB-ER-D2 | le | `ER` | RE-1's `d2_data_refined.npz` | 7.45e-12 |"),
 ('W7-n6', 'sec_method.tex', r"refinement classifier has 400 trees and 31 leaves and takes the estimator seed plus three as its seed. This is configuration~(f) below.", '-', RB, "used `--bkg-mode negweight-refined` with 400 trees and 31 leaves, and recorded `random_state` equal"),
 ('W7-n7', 'sec_method.tex', r"\pcell{0.20\textwidth}{(f) refined central-value estimator}", '-', EST, "the 2D estimator Joseph decided to move the adopted result to"),
 ('W7-n8', 'sec_3d.tex', r"the data comparison to (e) against (f)), so their ratio is not", r"the data comparison to (e) against (a))", DA, "The adopted 2D result is `E_R`, with `Q_R` as its headline uncertainty."),
 ('W7-n9', 'sec_3d.tex', r"scatter compares (e) with (f), so the scatter is not read here as", r"scatter compares (e) with (a), so", DA, "The adopted 2D result is `E_R`, with `Q_R` as its headline uncertainty."),
 ('W7-n10', 'sec_5d.tex', r"Two-dimensional reproduction (f), (a), (b)", r"Two-dimensional reproduction (a), (b)}", DA, "The adopted 2D result is `E_R`, with `Q_R` as its headline uncertainty."),
 ('W7-e1', 'sec_execsummary.tex', r"and the 2D central value and its covariance use the same treatment, in configuration (f).", r"The 2D and 5D central values and all quoted uncertainties use the purity subtraction", DA, "The adopted 2D result is `E_R`, with `Q_R` as its headline uncertainty."),
 ('W7-e2', 'sec_execsummary.tex', r"On this basis the 2D result was moved to the refined estimator (\S\ref{sec:negweight-footing}).", r"the revisit of the choice of purity is in progress", DS, "The adopted 2D result moves to the refined estimator,"),
 ('W7-m1', 'main_note.tex', r"the two-dimensional result and its covariance use the refined estimator.", r"The two- and five-dimensional central values and all quoted uncertainties use the purity subtraction", DA, "The adopted 2D result is `E_R`, with `Q_R` as its headline uncertainty."),
 ('W7-m2', 'main_note.tex', r"The negative-weight treatment is used for the two-, three- and four-dimensional central values", r"revisit of the choice of purity is in progress.", DA, "C_model stays separate, beside `Q_R`"),
 ('W7-s1', 'sec_summary.tex', r"and on this basis the two-dimensional result was moved to the refined estimator.", '-', DS, "The adopted 2D result moves to the refined estimator,"),
 ('W7-g1', 'app_negweight.tex', r"The 2D result quoted in this note uses the refined treatment, configuration~(f), with its covariance and its comparison with the published result rebuilt for it", r"The 2D result quoted in this note still uses the purity subtraction", DA, "The adopted 2D result is `E_R`, with `Q_R` as its headline uncertainty."),
 ('W7-g2', 'app_negweight.tex', r"In two dimensions, the closure test below is the revisit's result, and the 2D result and its covariance now use the refined estimator", r"revisit is in progress, and the two-dimensional closure test below is its first result.", DS, "the note records the background-treatment revisit as carried out, with RE-1 as its evidence."),
 ('W7-g3', 'app_negweight.tex', r"except the 2D result and its covariance and the 3D and 4D central values.", r"\S\ref{sec:method-algo}, except the 3D and 4D central values.", DA, "The adopted 2D result is `E_R`, with `Q_R` as its headline uncertainty."),
 ('W7-g4', 'app_negweight.tex', r"the quoted 2D central value uses the same refinement capacity, in configuration (f).", r"but not the quoted 2D and 5D central values.", EST, "the Stay-Positive refinement classifier at 400 trees, 31 leaves, random_state seed + 3 = 45"),
 ('W7-r1', 'primer_body.tex', r"and that result now uses the improved removal.", r"that result is being moved to the improved removal", DA, "The adopted 2D result is `E_R`, with `Q_R` as its headline uncertainty."),
 ('W7-t1', 'result_status_rows.tex', r"2D: LightGBM, five iterations, seed 42, refined negative-weight subtraction (configuration (f); exact-split cross-check)", r"\rsA{2D: LightGBM, five iterations, seed 42 (exact-split cross-check)}", DA, "The adopted 2D result is `E_R`, with `Q_R` as its headline uncertainty."),
 # W8: the shift-versus-bias count, labelled descriptive, with the quoted result's operand
 ('W8', 'sec_systematics.tex', r"the NuWro shift of the quoted result reaches the bias in 67, and the quadrature sum of the other two generators' shifts reaches it in 72; these counts are descriptive.", '-', CM, "the refined arm's NuWro |shift| reaches |bias| in 67"),
 # W9
 ('W9', 'app_statmethods.tex', r"$V$ full-rank ($\mathrm{rank}=205$, with 204 eigenvalues above $10^{-12}\lambda_{\max}$;", r"full-rank ($\mathrm{rank}=204$", TRP, "rank(lam>0) = 205/205"),
 ('W9b', 'app_statmethods.tex', r"with 204 eigenvalues above $10^{-12}\lambda_{\max}$", '-', TRP, "1e-12        2.653     204"),
 # W10
 ('W10', 'app_release.tex', r"of the refined LightGBM result, with RC7's plotting code extended to draw this analysis's band.", r"from the committed LightGBM values and covariance, with RC7's plotting code extended to draw this analysis's band.", A3, "4e18c266"),
 # Figures (RE-2 integration, figure install): the bootstrap caption names the central value, not E_U
 ('FIG-cap', 'sec_systematics.tex', r"per-bin spread $\sigma$ relative to the central value of the unfolded 2D cross section", r"spread $\sigma/E_U$ of the unfolded 2D cross section", f'{S}/re2/RE2-PARTC-REPORT.md', "`block_stat.root`'s `hRel2D` is √diag(stat)/x of the same arrays."),
 # D30 (outside review, agy): the sentence a draft comment had swallowed prints again
 ('X4b', 'sec_method.tex', r"It has no matched covariance: no exact-split bootstrap, universe sweep or seed scan exists.", '-', f'{S}/re2/RE2-PARTC-REPORT.md', "RE2-BINDING-C"),
]
# G rows: the 2D figures installed from RE-2 part C's refined products; each pin is read from the committed SHA256SUMS.
SUMS = f'{S}/re2/run/partc_r2/partc-r2/SHA256SUMS'
G_ENTRIES = ['./fig67/MEFHC_fig6_7_uncertainty_pt.pdf', './fig67/MEFHC_fig6_7_uncertainty_pz.pdf', './stat/uq_spread_2d.pdf',
             './stat/uq_corr_2d.pdf', './figs/MEFHC_5iter_fig13.pdf', './figs/MEFHC_5iter_pull_full.pdf',
             './figs/MEFHC_5iter_xsec_eff_heatmap.pdf', './figs/MEFHC_5iter_xsec_paper_pt_slices.pdf',
             './figs/MEFHC_5iter_xsec_paper_pz_slices.pdf', './figs/MEFHC_5iter_xsec_proj_pt.pdf',
             './figs/MEFHC_5iter_xsec_proj_pz.pdf', './receipts/figs/model_comp_projections.pdf',
             './receipts/figs/model_comp_ratio_maps.pdf', './receipts/figs/tension_chi2_map.pdf',
             './receipts/figs/tension_mode_maps.pdf', './receipts/figs/tension_spectrum.pdf']
_sums = {l.split()[1]: l.split()[0] for l in Path(SUMS).read_text().splitlines() if len(l.split()) == 2}
G = [(f'FIG-{e.rsplit("/", 1)[1][:-4]}', e.rsplit('/', 1)[1], _sums[e], SUMS, e) for e in G_ENTRIES]
lines = ['# M rows: new values.tex macros, computed by the checker from their product.']
lines += ['\t'.join(('M',) + r) for r in M]
lines += ['# F rows: the facts of each wording draft (DRAFTS.md ids). Every new text must print; every old text must not.']
lines += ['\t'.join(('F',) + r[:-1] + (r[-1].replace('\t', ' '),)) for r in F]
lines += ['# G rows: figures installed from RE-2 part C (pin = the committed SHA256SUMS line).']
lines += ['\t'.join(('G',) + r) for r in G]
t = (D / 'ledger.tsv').read_text()
cut = t.find('# M rows:')
t = t if cut < 0 else t[:cut]
(D / 'ledger.tsv').write_text(t + '\n'.join(lines) + '\n')
print(len(M), 'M rows;', len(F), 'F rows;', len(G), 'G rows')
