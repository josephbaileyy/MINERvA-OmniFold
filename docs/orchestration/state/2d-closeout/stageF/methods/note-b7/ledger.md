# Fact ledger: `sec_joint.tex`, origin/main b603f9cf -> worktree `wt-note-b7`

One row per number, claim, limitation and disclosure printed in §10. Paragraph ids (`before`) are from
`outline-before.md`. The verbatim specification quote (Q), the four tables (T1-T4) and the figure caption (F1) are
not edited; T2, T3 and Q are covered by BASE byte-identity probes rather than row by row.

**Dispositions.** `KEEP` (wording may change, meaning does not); `KEEP (guardrail)` (a qualifier kept because the
sentence would be false without it; reason given); `COLLAPSED` (a repeat removed; the fact still prints where the
probe points); `REWORDED` (meta text replaced by a plain statement of the same content); `REMOVED` (no fact; probe
shows the text is gone). `ADDED-to-note` (round 2, on the review: a sourced fact newly printed so that a paper pointer
lands; source in the row and in a source comment). No row moves to the records document: nothing printed in §10 is a pure record.

**Probes.** `N:file::` (prints in that file), `S:label::` (prints inside the subsection or paragraph that label
opens: the paper's pointer still lands on it), `X:file::` (no longer printed), `BASE:file::a||b` (raw bytes from a to
b identical to origin/main). `check_ledger.py` runs them; a probe shows the text is there, and each row's meaning was
also checked by reading.

## Protected text (byte-identical)

| id | fact | before | disposition | probe |
|---|---|---|---|---|
| V1 | opening: "hybrid null hypotheses about five predictions" (separate correction) | J0 | KEEP (protected) | `BASE:sec_joint.tex::hybrid null hypotheses||about five predictions` && `S:sec:joint5d::hybrid null hypotheses about five predictions (\S\ref{sec:joint5d-design})` |
| V2 | GiBUU label, verbatim (binding ruling, ADDENDUM-7 item 3); lead-in "carries the label required for it" -> "is reported under the label" (review E5) | J36 | KEEP (protected) | `BASE:sec_joint.tex::``B3 (sampling closure)||\sigma_{c}$''` && `S:sec:joint5d-ch::The GiBUU re-evaluation is reported under the label ``B3 (sampling closure) failed on hydrogen; a post-hoc bias check of its premise passed at $\le0.1\,\sigma_{c}$''` |
| V3 | the framing of V2 stays accurate: B3 failed on hydrogen; the post hoc check was declared before computing and met its 0.1 sigma_c criterion; effect at most 5.1e-4 sigma_c (mp3c/REPORT.md:31-38: max abs, reading (a), 5.1e-4; acceptance max <= 0.1 over the 72 cells) | J36 | KEEP (review F4: "at most about 5e-4" -> "at most 5.1e-4") | `S:sec:joint5d-ch::the sampling-closure check failed on the hydrogen sample, and a post hoc bias check of that check's premise, declared before it was computed, met its criterion of at most $0.1\,\sigma_{c}$ in every cell` && `S:sec:joint5d-ch::moving the CH prediction by at most $5.1\times10^{-4}\,\sigma_{c}$` |
| V11 | NEW: sigma_c is the SD of the cell's result over NuWro's null used for the decisions, B = 1751 (mp3b/REPORT.md:37 reading (a); mp3c/REPORT.md:31) (review F5) | J36 | KEEP (corrected definition) | `S:sec:joint5d-ch::where $\sigma_{c}$ is the standard deviation of the cell's result over NuWro's null distribution used for the decisions ($B=1751$)` && `X:sec_joint.tex::of the cell over the null distribution used for the decisions` |
| V4 | the verbatim specification quote (i)-(vi) | Q | KEEP (protected) | `BASE:sec_joint.tex::\begin{quote}\small||\end{quote}` |
| V5 | decisions table and caption | T2 | KEEP | `BASE:sec_joint.tex::\begin{tabular}{@{}llrrlll@{}}||\label{tab:joint5d}` |
| V6 | projections table and caption | T3 | KEEP | `BASE:sec_joint.tex::\begin{tabular}{@{}llll@{}}||\label{tab:joint5d-projections}` |
| V7 | recoil table and caption | T4 | KEEP | `BASE:sec_joint.tex::\begin{tabular}{@{}lrrrrrrrr@{}}||\label{tab:joint5d-recoil}` |
| V8 | generative-model table and caption | T1 | KEEP | `BASE:sec_joint.tex::\caption{Generative model of the calibration.||\end{table}` |
| V9 | figure caption | F1 | KEEP | `BASE:sec_joint.tex::\includegraphics[width=\textwidth]{paper_joint_nulls}||\label{fig:joint5d-nulls}` |
| V10 | records citation with its tag (check_note_records P6) | J0 | KEEP | `N:sec_joint.tex::(Ref.~\cite{NoteRecords2026}, \texttt{joint-5d})` |

## §10 opening

| id | fact | before | disposition | probe |
|---|---|---|---|---|
| O1 | design fixed before any production pseudo-experiment or observed statistic | J0 | KEEP | `S:sec:joint5d::Their design was fixed before any production pseudo-experiment or observed statistic was computed` |
| O2 | ... with two data-informed elements (pointer to §10.3) | J0 | KEEP ("disclosed" dropped; the elements are stated in §10.3) | `S:sec:joint5d::with two data-informed elements (\S\ref{sec:joint5d-frozen})` |
| O3 | not a measured cross section; no reportable uncertainty | J0 | KEEP | `S:sec:joint5d::They are not a measured cross section, add no reportable uncertainty` |
| O4 | do not validate the five-axis covariance, which they do not use | J0 | KEEP | `S:sec:joint5d::do not validate the five-axis covariance used elsewhere in this note (\S\ref{sec:eavailw-adopted}), which they do not use` |
| O5 | the section gives the specification with its six conditions in its own words, the decisions, the recovery and the later studies with numbers | J0 | REWORDED (from "Everything the argument below needs is stated here") | `S:sec:joint5d::gives the pre-registered specification, with its six conditions in its own words (\S\ref{sec:joint5d-conditions}), the decisions, the recovery of the lost pseudo-experiments and the later sensitivity studies with their numbers` && `X:sec_joint.tex::Everything the argument below needs` |
| O6 | the records cited in the section are its provenance: specification and decisions in JointTestRecord2026, each later study its own record | J0 | KEEP (review F1 wording) | `S:sec:joint5d::The specification and the decisions are documented in Ref.~\cite{JointTestRecord2026}; each later study cites its own record.` && `S:sec:joint5d-lost::\cite{JointTestRecovery2026}` && `S:sec:joint5d-kappa::\cite{JointTestKappa2026}` && `S:sec:joint5d-projections::\cite{JointTestProjections2026}` && `S:sec:joint5d-response::\cite{JointTestRecoil2026}` && `X:sec_joint.tex::the supporting records are in` |
| O7 | "complete record ... the article states its result and conditions and refers here" (document-structure meta text; no fact) | J0 | REMOVED | `X:sec_joint.tex::complete record of the joint` && `X:sec_joint.tex::refers here for the detail` |

## §10.1 Hypotheses, grid and statistics

| id | fact | before | disposition | probe |
|---|---|---|---|---|
| D1 | five predictions named, with versions | J1 | KEEP | `S:sec:joint5d-design::the MINERvA Tune~v1, GENIE~2.12.10 without and with MEC, NuWro~21.09 and GiBUU~2019` |
| D2 | H0(G): true cross section equals G on every fine cell | J1 | KEEP | `S:sec:joint5d-design::is that the true cross section equals $G$ on every cell of a fine five-dimensional grid` |
| D3 | below the grid: Tune v1 composition, varied by drawn universes, fine-cell integrals fixed; Tune v1 background with bands | J1 | KEEP | `S:sec:joint5d-design::interaction-model universes with every fine-cell integral held fixed, and the background is the Tune~v1 simulation's, with its uncertainty bands` |
| D4 | the hybrid null is what the calibration simulates; for Tune v1 nothing external is combined | J1 | KEEP | `S:sec:joint5d-design::is the hypothesis the calibration simulates; for the Tune~v1, the analysis simulation itself, no external prediction is combined` |
| D5 | three distinct requirements: exact definition (no convergence needed); representation of G depends on sub-grid composition and convergence (cond. i); calibration fidelity (ii)-(iv) | J1 | KEEP (split into three sentences) | `S:sec:joint5d-design::Three requirements are distinct. The hybrid null is defined exactly on the finite grid, and no convergence is needed to define it.` && `S:sec:joint5d-design::depends on the composition below the fine grid and on convergence of that grid` && `S:sec:joint5d-design::reproduces the analysis of the data is calibration fidelity (conditions~(ii)--(iv))` |
| D6 | total and shape tests: ten tests | J1 | KEEP | `S:sec:joint5d-design::and in shape alone: \jtNtests{} tests` |
| D7 | fine grid = analysis binning 14x16x7x7x6; test cells its integrals | J2 | KEEP | `S:sec:joint5d-design::$14\times16\times7\times7\times6$ bins in $(\pT,\pPar,\Eavail,q_{3},W)$; the test cells below are its integrals` |
| D8 | coarse 3^5 grid with its edges (paper pointer: edges, §10.1) | J3 | KEEP | `S:sec:joint5d-design::$\pT\in[0,0.55,0.85,4.5]\,\si{GeV/c}$, $\pPar\in[1.5,3.5,6,60]\,\si{GeV/c}$` && `S:sec:joint5d-design::$W\in[0,1.4,2.2,100]\,\si{GeV}$.` && `S:sec:joint5d-design::The tests are restricted to the \jtNcells{} supported cells (J)` |
| D17 | NEW: inner coarse edges = fine edges nearest the weighted tertiles of the development simulation's signal truth distribution, per coordinate (s5c_partition.py:14-15, 45-52, 80); no support threshold in that file (paper pointer :239, review F2) | J3 | ADDED-to-note | `S:sec:joint5d-design::Each inner edge is the fine-grid edge nearest a tertile of the weighted simulated truth distribution of the signal sample in that coordinate, taken from the development simulation, so the cells keep physical bin widths.` |
| D9 | GiBUU domain: 72 cells with ppar < 6 GeV/c (lacks high-energy neutrinos) | J3 | KEEP | `S:sec:joint5d-design::the \jtNcellsGiBUU{} cells with $\pPar<\SI{6}{GeV/c}$` |
| D10 | the grid does not turn OmniFold into binned unfolding | J3 | KEEP | `S:sec:joint5d-design::it does not turn OmniFold's event-level training into binned unfolding` |
| D11 | T_tot, T_sh definitions; Jacobian; one cell dropped | J4 | KEEP | `S:sec:joint5d-design::on the normalized cell fractions, with the normalization Jacobian applied to $\Sigma$ and one cell dropped` |
| D12 | Sigma = V + diag Var(mu_G); V Ledoit-Wolf of 194 pilot pseudo-experiments at Tune v1 | J4 | KEEP | `S:sec:joint5d-design::covariance~\cite{LedoitWolf:2004} of \jtVn{} pilot pseudo-experiments at the Tune~v1 null` |
| D13 | the metric affects power; calibration sets size | J4 | KEEP | `S:sec:joint5d-design::the null calibration below, not the metric, sets each test's size` |
| D14 | diagonal prediction variance; pilot seeds disjoint, same events, no MINOS band | J5 | KEEP | `S:sec:joint5d-design::but it reuses the same simulated events and omitted the MINOS-efficiency band` |
| D15 | diag V matches (median ratio 1.00); shrinkage 0.015 floors ~80 of 109; whitened trace ~47 | J5 | KEEP | `S:sec:joint5d-design::(median ratio 1.00), but the shrinkage (intensity 0.015) floors about 80 of the 109 nearly degenerate correlation directions` && `S:sec:joint5d-design::whitened trace of about 47 rather than 109` |
| D16 | power only; other shrinkage intensities not measured | J5 | KEEP (guardrail: the effect on power is unknown) | `S:sec:joint5d-design::the power at other shrinkage intensities has not been measured` |

## §10.2 Calibration

| id | fact | before | disposition | probe |
|---|---|---|---|---|
| C1 | joint-test estimator: deterministic LightGBM OmniFold, five iterations, 400-tree 31-leaf refinement, chosen before the design was fixed | J6 | KEEP | `S:sec:joint5d-calibration::negative-weight background treatment with a 400-tree, 31-leaf refinement classifier, chosen before the design was fixed` |
| C2 | itemized draws (halves, background, 100 flux universes, 34 bands, detector bands, 1.4% norm, rounding from 20 re-unfolds, prediction residual) | J6 | KEEP | `S:sec:joint5d-calibration::draws one of \jtFluxUniverses{} flux universes and every one of the \jtModelBands{} interaction-model bands` && `S:sec:joint5d-calibration::(taken from 20 real-data re-unfolds with rounding-level input changes)` |
| C3 | data unfolded once; p = (k+1)/(B+1), never zero | J7 | KEEP | `S:sec:joint5d-calibration::The data are unfolded once, with the full simulation.` && `S:sec:joint5d-calibration::it is never zero` |
| C4 | claim p = max over the D variant (cond. iv) and +-2 delta_fine (cond. i) (paper pointer) | J7 | KEEP | `S:sec:joint5d-calibration::simulation-size difference between the pseudo-experiments and the data unfold (condition~(iv) below) and by $\pm\jtMoneKappa\,\delta_{\mathrm{fine}}$ (condition~(i))` |
| C5 | external nulls non-central, lambda 318-6344, estimator pull | J7 | KEEP | `S:sec:joint5d-calibration::non-centralities $\lambda$ of \jtLambdaMin{}--\jtLambdaMax{} in these units` |
| C6 | truth = G on populated fine cells; empty cells lower a coarse cell by <= 0.2%, ~4% of null SD; spread < 1.5% | J8 | KEEP | `S:sec:joint5d-calibration::lower a coarse cell by at most \SI{0.2}{\percent}, or about \SI{4}{\percent} of the null standard deviation` |
| C7 | per-cell renormalized bands; independent universes multiply; lateral bands sum z_b Delta_b; GEANT4 reweights | J8 | KEEP | `S:sec:joint5d-calibration::enter as $\sum_{b}z_{b}\Delta_{b}$, with $\Delta_{b}$ from endpoint unfoldings of the data` |
| C8 | null conditional on data-derived inputs, not validated (paper pointer) | J8 | KEEP (guardrail) | `S:sec:joint5d-calibration::distributions are conditional on these data-derived inputs, which would differ in a repeated experiment; that conditioning has not been validated` |

## §10.3 Multiplicity, stopping rule and the predeclared design

| id | fact | before | disposition | probe |
|---|---|---|---|---|
| F1 | Holm at familywise 5% | J9 | KEEP | `S:sec:joint5d-frozen::falsely rejecting at least one true hypothesis among the ten is at most 5\%` |
| F2 | determinacy requirement: 95% CP interval entirely below the threshold | J9 | KEEP | `S:sec:joint5d-frozen::a step rejects only when the 95\% Clopper--Pearson interval~\cite{Clopper:1934} of $k/B$ lies entirely below its Holm threshold` |
| F3 | batches of 200, to at most 1999; sequential stop | J9 | KEEP | `S:sec:joint5d-frozen::Calibration proceeded in batches of \jtBatch{} pseudo-experiments per null, to at most \jtBcap{}` |
| F4 | stop: 99.5% interval + precision; gate = 97.5% one-sided bound | J10 | KEEP | `S:sec:joint5d-frozen::A null stopped when a 99.5\% Clopper--Pearson interval` && `S:sec:joint5d-frozen::one-sided 97.5\% upper bound` |
| F5 | under A1, A2, any stopping rule incl. budget extensions; FWER <= 0.8902 alpha < 0.9 alpha | J10 | KEEP | `S:sec:joint5d-frozen::whatever rule determines when sampling stops, including the budget extensions` && `S:sec:joint5d-frozen::$\mathrm{FWER}\le0.8902\,\alpha<0.9\,\alpha$` |
| F6 | A2 requires loss independent of outcome, "has not been shown" (paper-cited) | J10 | KEEP (guardrail, paper-cited) | `S:sec:joint5d-frozen::A2 requires the lost pseudo-experiments to have been lost independently of their outcomes, which has not been shown, although none of them reaches the observed statistic when rerun` |
| F7 | size averaged over nuisance priors; can exceed alpha at fixed nuisances | J10 | KEEP (guardrail) | `S:sec:joint5d-frozen::at a fixed true value of the nuisance parameters it can exceed $\alpha$` |
| F8 | hypotheses, statistics, variants, multiplicity, stopping rule, every input fixed before production or observed statistic | J11 | KEEP | `S:sec:joint5d-frozen::The hypotheses, statistics, variants, multiplicity rule, stopping rule and every input were fixed before any production pseudo-experiment or observed statistic` |
| F9 | data-informed element 1: reviewers saw descriptive per-cell residuals before fixing (paper-cited) | J11 | KEEP | `S:sec:joint5d-frozen::with two data-informed elements. The design's reviewers had seen descriptive per-cell residuals of the data before it was fixed` |
| F10 | data-informed element 2: the calibration's monitoring (job-controller status) output showed observed claim p during production | J11 | KEEP (software detail dropped, review E2) | `S:sec:joint5d-frozen::During production, the calibration's monitoring output showed observed claim $p$ values` |
| F11 | bounded budget extension decided while visible, to reach the predeclared stop rather than a budget stop (paper-cited) | J11 | KEEP | `S:sec:joint5d-frozen::a bounded extension of the production budget was decided while they were visible, so that the sequential rule could reach the stop set by its predeclared rule rather than a budget stop` |
| F12 | nothing changed; bound holds whatever the stopping rule | J11 | KEEP | `S:sec:joint5d-frozen::No statistic, variant, threshold or stopping rule was changed, and the familywise bound above holds whatever rule determined when sampling stopped` |
| F13 | independent recomputation, 1379 rows; verifies calculation, not adequacy | J12 | KEEP (guardrail) | `S:sec:joint5d-frozen::agrees with the production evaluation on all \jtRecompRows{} compared rows; it verifies the calculation, not the adequacy of the calibration` |
| F14 | three post-decision studies outside the decision rule, each specified before it ran | J13 | KEEP (term per glossary A7, first use) | `S:sec:joint5d-frozen::Three studies followed the decisions and are for reporting only (outside the decision rule); each was specified before it ran` |
| F15 | the projection comparison was specified after the 5D outcomes were known | J13 | KEEP | `S:sec:joint5d-frozen::which was specified after the five-dimensional outcomes were known` |
| F16 | GENIE muon-projection non-rejection is post hoc | J13 | COLLAPSED (still in §10.7 text and Table 13 caption) | `S:sec:joint5d-projections::$\woneGcvPtShape$ in shape; a post hoc observation)` && `X:sec_joint.tex::The non-rejection of GENIE~2.12.10 in the muon-kinematic projection is a post hoc observation` |

## §10.4 Conditions

| id | fact | before | disposition | probe |
|---|---|---|---|---|
| K1 | six conditions of the declared model; quoted from the specification, typesetting only | J14 | REWORDED | `S:sec:joint5d-conditions::Each decision holds under six conditions of the declared model. They are quoted below from the pre-registered specification, changed only in typesetting.` |
| K2 | bracketed text is editorial: replaces file references by content; annotates the two superseded statements | J14 | KEEP | `S:sec:joint5d-conditions::Text in square brackets is ours: it replaces references to internal files by their content and annotates the two statements that the implementation or a later measurement supersedes` |
| K3 | restated in the note's terms, grouped by kind | J15 | REWORDED | `S:sec:joint5d-conditions::In the terms of this note, they fall into three kinds.` && `S:sec:joint5d-conditions::\paragraph{Numerical convergence.}` && `S:sec:joint5d-conditions::\paragraph{Calibration validity.}` && `S:sec:joint5d-conditions::\paragraph{Physical-model adequacy.}` |
| K4 | (i) Tune v1 composition below grid; convergence not shown; L2 ratio 0.50-0.86; residual unmeasured, potentially material | J16 | KEEP (guardrail) | `S:sec:joint5d-conditions::is \jtMoneMin--\jtMoneMax{} of the whole change from the coarse test grid to the fine grid` && `S:sec:joint5d-conditions::the residual below the fine grid is unmeasured and potentially material` |
| K5 | design proxy shrink 0.45-0.76 per halving; value from the design review; derivation not documented | J16 | KEEP (guardrail: the provenance limitation of the value) | `S:sec:joint5d-conditions::shrink by a factor of \jtMoneWnormMin--\jtMoneWnormMax{} per halving; this value comes from the design review, and its derivation is not given` |
| K6 | geometric extrapolation: residual ~1-3x last step delta_fine; delta_fine definition | J16 | KEEP | `S:sec:joint5d-conditions::the residual would be about one to three times the last step, $\delta_{\mathrm{fine}}$ (the change of the noise-free unfolded result` |
| K7 | claim variants +-2, robustness +-3 for reporting only | J16 | KEEP (glossary A7: short form after first use) | `S:sec:joint5d-conditions::the robustness check, for reporting only, at $\pm\jtMoneKappaRobust\,\delta_{\mathrm{fine}}$` |
| K8 | geometric assumption; measured ratios allow slower rates and larger residuals | J16 | KEEP (guardrail) | `S:sec:joint5d-conditions::the measured $L_{2}$ ratios also allow slower rates and larger residuals` |
| K9 | variants move nulls by 0.55-2.0 and 1.07-3.6 null SD, measured before any observed statistic | J16 | KEEP | `S:sec:joint5d-conditions::move the external nulls by \jtMoneClaimSdMin--\jtMoneClaimSdMax{} null standard deviations and the robustness variants by \jtMoneRobSdMin--\jtMoneRobSdMax{}` |
| K10 | carry-over to G only if ... (paper-cited) | J16 | KEEP (guardrail) | `S:sec:joint5d-conditions::the variants carry the rejections over to $G$ itself only if replacing the Tune~v1's shape below the fine grid by $G$'s moves` |
| K11 | (vi) prediction samples in metric and residual | J16 | KEEP | `S:sec:joint5d-conditions::(vi) The predictions' own finite samples enter the metric` |
| K12 | validity to the extent the chain reproduces the data analysis; recomputation verifies calculation; no rejection rate measured | J17 | KEEP (guardrail) | `S:sec:joint5d-conditions::no rejection rate has been measured for null pseudo-data processed like the data, which would require an independent simulation sample` |
| K13 | (iv) half vs full simulation, <= ~0.07 null SD, not always consistent with zero, upper-bound variant | J17 | KEEP | `S:sec:joint5d-conditions::at most about 0.07 null standard deviations but not always consistent with zero` |
| K14 | mean-only measurement without noise or nuisances | J18 | KEEP (guardrail) | `S:sec:joint5d-conditions::That shift was measured for the mean only, in a process without noise or nuisance draws.` |
| K15 | quarter-simulation check: medians within 0.074, widths 0.975-1.010, mean paired shift 0.006-0.034; all ten remain rejected | J18 | KEEP | `S:sec:joint5d-conditions::(medians within 0.074 null standard deviations, widths within 0.975--1.010 of the half-simulation values), only a mean paired shift of 0.006--0.034` && `S:sec:joint5d-conditions::all three shape decisions, and so all ten, remain rejected` |
| K16 | not a test of the data process; same events, conditional | J18 | KEEP (guardrail) | `S:sec:joint5d-conditions::it is not a test of the data process. Every pseudo-experiment resamples the same simulated events` |
| K17 | margins 1.11/1.30 (1.01/0.67 robust); others 2.7-203 (2.0-203) (paper: "all margins") | J18 | KEEP | `S:sec:joint5d-conditions::by 1.11 and 1.30 null standard deviations, with the Holm order held fixed (1.01 and 0.67 with the robustness variants` && `S:sec:joint5d-conditions::the other eight tests lie 2.7 to 203 null standard deviations from it (2.0 to 203 with the robustness variants)` |
| K18 | crossing would make a test undetermined, not unrejected | J18 | KEEP | `S:sec:joint5d-conditions::Crossing that value would make a test undetermined` |
| K19 | rounding nondeterminism: only NuWro shape 2/1752 -> 3/1752 | J18 | KEEP | `S:sec:joint5d-conditions::unchanged except NuWro's shape test (2/1752 to 3/1752)` |
| K20 | (ii) surrogate checked only for endpoint symmetry; no recoil response band; completeness not established | J19 | KEEP (guardrail) | `S:sec:joint5d-conditions::the surrogate has been checked only for the symmetry of its endpoints` && `S:sec:joint5d-conditions::completeness of the hadronic-response model is not established` |
| K21 | (iii) 34 bands; two clipped at most 0.35% | J19 | KEEP | `S:sec:joint5d-conditions::are clipped per universe, at most 0.35\% of a band's shift` |
| K22 | (v) GiBUU lacks E>20 GeV; E>100 GeV absent for all, negligible; Tune v1 composition is a modelling choice | J19 | KEEP | `S:sec:joint5d-conditions::GiBUU lacks $E_{\nu}>\SI{20}{GeV}$` && `S:sec:joint5d-conditions::is also a modelling choice of this kind` |

## §10.5 Decisions

| id | fact | before | disposition | probe |
|---|---|---|---|---|
| R1 | all ten rejected; nine k=0, NuWro shape k=1 | J20 | KEEP | `S:sec:joint5d-results::nine have $k=0$, and NuWro's shape test has $k=1$` |
| R2 | each rejection survives the +-3 robustness variants | J20 | KEEP | `S:sec:joint5d-results::Each rejection also survives the robustness variants` |
| R3 | null distributions shown; Tune v1 centred low, external displaced by the pull (paper pointer) | J20 | KEEP | `S:sec:joint5d-results::the Tune~v1 null is centred at small values, whereas the external nulls are displaced far upward by the estimator's pull toward its prior` |
| R4 | kappa scales delta_fine; kappa=1 is one change, not an SD or CL | J21 | KEEP | `S:sec:joint5d-kappa::$\kappa=1$ means one such change, not one standard deviation or a confidence level` |
| R5 | scan for reporting only: determinate rejections up to 5.25 (paper: "about 5.2") | J21 | KEEP | `S:sec:joint5d-kappa::for reporting only, found all ten decisions to remain determinate rejections at every sampled multiplier up to 5.25` |
| R6 | lost between 5.2547 and 5.2563 (5.1688-5.1703 with recovered draws); GENIE+MEC shape, then GENIE shape via Holm; not determinate non-rejections | J21 | KEEP | `S:sec:joint5d-kappa::multipliers 5.2547 and 5.2563 (between 5.1688 and 5.1703 with the recovered draws included)` && `S:sec:joint5d-kappa::neither is then a determinate failure to reject` |
| R7 | one direction; no convergence or bound; residual unmeasured, potentially material (paper-cited) | J21 | KEEP (guardrail) | `S:sec:joint5d-kappa::scan probes one prescribed direction; it establishes neither convergence nor a bound on the actual below-grid residual` |
| R8 | power is context only | J22 | KEEP | `S:sec:joint5d-power::Every test rejects, so power is context only` |
| R9 | power values and binomial 95% intervals (paper pointer) | J22 | KEEP | `S:sec:joint5d-power::$[0.98,1]$ for the first two Tune~v1 alternatives, $[0.17,0.30]$ for the third, and $[0.67,0.80]$, $[0.01,0.05]$ and $[0,0.02]$` |
| R10 | power sets as evaluated for the decisions; lost some of 200 (172-199 retained) | J23 | KEEP | `S:sec:joint5d-power::These values use the power sets as evaluated for the decisions, each of which had lost some of its 200 alternative pseudo-experiments to time limits (172--199 retained)` |
| R11 | complete sets agree within 0.01 against decision nulls; first GENIE set 0.72 with null on all draws | J23 | KEEP | `S:sec:joint5d-power::agree with them within 0.01 against the null ensembles used for the decisions` && `S:sec:joint5d-power::first GENIE~2.12.10 set moves to 0.72` |

## §10.6 Lost pseudo-experiments and their recovery

| id | fact | before | disposition | probe |
|---|---|---|---|---|
| L1 | 224 calibration (111 interrupted, 113 never started) and 53 power lost to time limits (paper-cited) | J24 | KEEP ("Scheduler" -> "Computing", as in the paper) | `S:sec:joint5d-lost::Computing time limits interrupted or prevented \jtLostCal{} of the submitted calibration pseudo-experiments (\jtLostInterrupted{} interrupted, \jtLostNever{} never started) and \jtLostPow{} power pseudo-experiments` |
| L2 | decisions evaluated on the completed draws | J24 | KEEP | `S:sec:joint5d-lost::decisions in Table~\ref{tab:joint5d} were evaluated on the completed draws` |
| L3 | pre-recovery sensitivity: every decision could change; p 0.013-0.019 if every interrupted draw exceeded | J24 | KEEP | `S:sec:joint5d-lost::A sensitivity analysis computed before the lost outcomes were known showed that every decision could change under a realizable assignment of them` && `S:sec:joint5d-lost::no test would have been rejected ($p$ \jtWorstIntLo--\jtWorstIntHi)` |
| L4 | runtime not associated (|rho| <= 0.06); supports but does not certify | J24 | KEEP (guardrail) | `S:sec:joint5d-lost::($|\rho|\le\jtRuntimeRho$), which supports but does not certify the decisions` |
| L5 | rerun for reporting only, under a procedure fixed and reviewed beforehand (paper: "were rerun") | J25 | KEEP | `S:sec:joint5d-lost::The lost seeds were rerun, for reporting only, under a procedure fixed and independently reviewed beforehand` |
| L6 | determinism 16/16; every submitted draw observed | J25 | KEEP | `S:sec:joint5d-lost::(16 of 16 completed seeds rerun bitwise identically) shows that each recovered draw is the lost draw, so every submitted draw has been observed` |
| L7 | none reaches the observed statistic in any test or variant; no assignment changes any decision (paper-cited) | J25 | KEEP | `S:sec:joint5d-lost::No recovered draw reaches the observed statistic in any test, claim variant or robustness variant, so no assignment of the lost draws changes any decision` |
| L8 | margins 4.6 of 868.6 (GENIE+MEC shape, +-3), next 49.8 | J25 | KEEP | `S:sec:joint5d-lost::The closest margin is 4.6 units of $T$ below the observed value of 868.6` && `S:sec:joint5d-lost::the next is 49.8` |
| L9 | complete batches: four nulls one batch earlier (B=1200), same decisions | J25 | KEEP | `S:sec:joint5d-lost::one batch earlier ($B=1200$), with the same decisions` |
| L10 | recovery checks narrower: 856/856 primary-shift reading only; all-draws reading only by standalone rerun; earlier stops only by the run itself | J26 | KEEP (guardrail) | `S:sec:joint5d-lost::its independent cross-check (856 of 856 quantities) covers only the reading with the variant shifts of the primary evaluation` && `S:sec:joint5d-lost::a consistency check rather than an independent recomputation` && `S:sec:joint5d-lost::the earlier-stop decisions rest on the calibration run's own re-application of the sequential rule, with no independent check` |
| L11 | recovery for reporting only; primary decisions are the pre-recovery ones at the stopping B | J27 | KEEP (guardrail) | `S:sec:joint5d-lost::The recovery is for reporting only: the primary decisions are those of the evaluation before recovery, at the $B$ at which its rule stopped` |
| L12 | with every draw observed and none reaching, the ten rejections hold, with closest margin and earlier stops | J27 | KEEP (reworded from "are stated as holding") | `S:sec:joint5d-lost::With every submitted draw observed and none reaching the observed statistic, the ten rejections hold, with the closest margin and the earlier stops given above` && `X:sec_joint.tex::are stated as holding` |
| L13 | the pre-recovery "could change" finding no longer qualifies them (superseded by the observed outcomes) | J27 | KEEP (reworded from "no longer accompanies them") | `S:sec:joint5d-lost::The finding of the sensitivity analysis, that every decision could change under some assignment of the lost draws, is superseded by their observed outcomes` |

## §10.7 Matched coarse projections

| id | fact | before | disposition | probe |
|---|---|---|---|---|
| P1 | p < 0.05 for every test in one of two 3x3 projections; no evidence of additional discrimination (paper-cited) | J28 | KEEP | `S:sec:joint5d-projections::gives $p<0.05$, without a multiplicity correction, for every test in at least one of the two projections, so this study provides no evidence of additional discrimination from the joint five-observable information` |
| P8 | NEW: projected tests uncorrected for multiplicity; outside the Holm family; change no decision (PACKET-20261005 sec. 6, :252; paper pointer :1066-1069, review F3) | J28 | ADDED-to-note | `S:sec:joint5d-projections::The projected tests do not enter the Holm family and change no decision of Table~\ref{tab:joint5d}.` |
| P2 | specified after the 5D outcomes, before the run | J28 | KEEP | `S:sec:joint5d-projections::specified after the five-dimensional outcomes were known but before the comparison was run` |
| P3 | criterion (fixed before the run): both projected p >= 0.05 in both readings; none meets it; same values both readings (paper-cited) | J29 | KEEP (moved up beside the result) | `S:sec:joint5d-projections::The comparison and its criterion were specified` && `S:sec:joint5d-projections::only if both of its projected claim $p$ values were at least 0.05, both with the variant shifts of the primary evaluation and with the shifts recomputed on all draws; no test meets it, and the values are the same in both readings` |
| P4 | table gives every projected claim p | J29 | KEEP | `S:sec:joint5d-projections::(Table~\ref{tab:joint5d-projections} gives every projected claim $p$ value)` |
| P5 | same ensembles incl. recovered draws, same variants and claim rule; reproduced independently | J28 | KEEP | `S:sec:joint5d-projections::uses the same calibration ensembles, with the recovered draws included, and the same variants and claim rule, and its $p$ values were reproduced independently~\cite{JointTestProjections2026}` |
| P6 | GENIE not rejected in (pT,ppar), post hoc; rejected in (Eavail,W); hadronic information participates; no added power; GENIE not accepted | J28 | KEEP (guardrail) | `S:sec:joint5d-projections::GENIE~2.12.10 is not rejected ($p=\woneGcvPtTot$ in total` && `S:sec:joint5d-projections::this does not establish added power of the joint test over all matched projections, or accept GENIE as true` |
| P7 | powers of joint and projected tests not compared | J28 | KEEP | `S:sec:joint5d-projections::The powers of the joint and projected tests have not been compared.` |

## §10.8 Hadronic-response condition and recoil-energy sensitivity

| id | fact | before | disposition | probe |
|---|---|---|---|---|
| H1 | test-beam response uncertainty, 10% at 0.9<q3<1.2 GeV | J30 | KEEP | `S:sec:joint5d-response::to \SI{10}{\percent} at its highest three-momentum transfers` |
| H2 | no calorimetric band; acts on all five nulls; net effect on p unmeasured | J30 | KEEP (guardrail) | `S:sec:joint5d-response::the net effect on each $p$ value is unmeasured` |
| H3 | muon-only published comparison is context; different estimator and calibration | J30 | KEEP | `S:sec:joint5d-response::but the hypotheses tested here use a different estimator and calibration` |
| H4 | GENIE projection: hadronic axes involved | J30 | KEEP | `S:sec:joint5d-response::involves the hadronic axes, on which a response band would act` |
| H5 | exploratory study, +-4% recoil scale, decision nulls | J31 | KEEP | `S:sec:joint5d-response::In an exploratory sensitivity study of the response~\cite{JointTestRecoil2026}, the data are re-unfolded with the simulation's reconstructed recoil energy scaled by $\pm\SI{4}{\percent}$` |
| H6 | size from test-beam 0.35-2.0 GeV/c; neutrons and high-momentum outside | J31 | KEEP | `S:sec:joint5d-response::neutrons and higher-momentum hadrons, which matter at high $W$, lie outside that sample` |
| H7 | +-4% not a validated uncertainty prescription | J31 | KEEP (guardrail; "a labelled exploratory sensitivity" collapsed into the opening "exploratory") | `S:sec:joint5d-response::the $\pm4\%$ size is not a validated uncertainty prescription` && `X:sec_joint.tex::labelled exploratory sensitivity` |
| H8 | unscaled re-unfold reproduces the decisions within rounding range | J31 | KEEP | `S:sec:joint5d-response::A re-unfold with unscaled recoil reproduces the decisions of Table~\ref{tab:joint5d}, with every claim $p$ value inside the range spanned by the data's rounding variations` |
| H9 | all ten hold at +-4%; up to ~11%; nine k=0; NuWro shape k 1->3 at +4% (p 0.0023 vs 0.05); reproduced independently | J31 | KEEP | `S:sec:joint5d-response::changes from $k=1$ to $k=3$ of 1751 at $+4\%$ ($p=0.0023$, against a Holm threshold of 0.05)` && `S:sec:joint5d-response::The evaluation was reproduced independently.` |
| H10 | untested (a)-(c) (paper pointer "untested effects") | J32 | KEEP (guardrail) | `S:sec:joint5d-response::The study leaves untested (a) the response of the null distributions` && `S:sec:joint5d-response::(b) particle-species, energy-dependent or resolution effects, and a response difference applied before calibration; and (c) larger variations` |
| H11 | rejections conditional on the simulation's hadronic response; model not shown complete | J32 | KEEP (guardrail) | `S:sec:joint5d-response::rejections are therefore conditional on the simulation's hadronic response, and the response model is not shown to be complete` |

## §10.9 Hydrocarbon target correction

| id | fact | before | disposition | probe |
|---|---|---|---|---|
| G1 | NuWro and GiBUU generated on carbon; data and other predictions per nucleon of CH | J33 | KEEP | `S:sec:joint5d-ch::NuWro~21.09 and GiBUU~2019 were generated on carbon, while the data and the other predictions are per nucleon of CH` |
| G2 | descriptive; do not re-grade the recorded decisions, which stand (paper-cited) | J33 | KEEP (antecedent fixed: "They" -> "The re-evaluations"; status word "recorded" dropped, review E7: the table is the decisions) | `S:sec:joint5d-ch::The re-evaluations are descriptive: they do not re-grade the decisions of Table~\ref{tab:joint5d}, which stand.` |
| G3 | construction 12/13 C + 1/13 H; f_H 5.08% / 4.77% | J34 | KEEP | `S:sec:joint5d-ch::$f_{\mathrm{H}}=5.08\%$ for NuWro over the grid and 4.77\% for GiBUU over its 72 cells` |
| G4 | r_c ranges; f_H per cell max 0.112 / 0.109; both toward the data | J34 | KEEP | `S:sec:joint5d-ch::0.923, 0.963, and 1.039 for NuWro` && `S:sec:joint5d-ch::Both corrections move the prediction toward the data.` |
| G5 | NuWro: total -3.83, shape -0.37; undetermined at original position; rejected only by re-sort; not rejected at kappa=3 (p=0.075) (paper: "does not survive robustly") | J35 | KEEP (guardrail) | `S:sec:joint5d-ch::It remains rejected only because its larger $p$ value moves it to the last Holm position` && `S:sec:joint5d-ch::it is not rejected ($p=0.075$)` |
| G6 | GiBUU -4.67/-1.33; margins 7.86->3.18, 3.58->2.24; W_CH no change | J35 | KEEP | `S:sec:joint5d-ch::3.18 and from 3.58 to 2.24 null standard deviations` && `S:sec:joint5d-ch::no decision changes for either generator` |
| G7 | GiBUU DIS on hydrogen (46%) do not conserve energy; 45 MeV / 31 MeV; cause unidentified; may affect carbon, uncheckable (paper-cited) | J37 | KEEP (guardrail) | `S:sec:joint5d-ch::GiBUU's deep-inelastic events on hydrogen, 46\% of its hydrogen sample, do not conserve energy` && `S:sec:joint5d-ch::It may also affect GiBUU's carbon prediction, which cannot be checked in this way.` |
| G8 | NuWro hydrogen: four chunks rerun; 1.8e-5 / 3.8e-5 (1.9e-5 / 6.2e-5); four to six events; 1.8e-4 > 1e-4, flagged | J38 | KEEP | `S:sec:joint5d-ch::$6.2\times10^{-5}$ including the first attempt; these estimates rest on four to six events` && `S:sec:joint5d-ch::so the supplement is flagged rather than assumed negligible` |

## §10.10 What the tests establish

| id | fact | before | disposition | probe |
|---|---|---|---|---|
| E1 | recover the published disagreements; contribution is calibration | J39 | KEEP | `S:sec:joint5d-reading::recover the generator disagreements already established by the published two-dimensional measurement` |
| E2 | global assessments; localization needs separate tests | J39 | KEEP | `S:sec:joint5d-reading::assigning a discrepancy to a kinematic region or nuclear mechanism would require separate tests` |
| E3 | all six conditions retained; response and residual outside any validated bound; extension needs | J39 | KEEP (guardrail) | `S:sec:joint5d-reading::the hadronic response and the sub-fine-grid residual remain outside any validated uncertainty bound` && `S:sec:joint5d-reading::a demonstrated bound on the residual below the fine grid` |
