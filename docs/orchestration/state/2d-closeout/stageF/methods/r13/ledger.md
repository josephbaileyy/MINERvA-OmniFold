# Fact ledger: r12 (origin/main 38a53a53) → r13 (worktree `wt-reg3`)

**r13 update (2026-10-21).** This ledger is r12's, carried forward. r13 is a sentence-level register pass; it moves no
paragraph, so the paragraph ids below (`P#` from r12's `outline-before.md`, `N#` from r12's `outline-after.md`, in
scratchpad `wt-reg2-work/`) still locate every row. Each row the r13 text touched has its probe rewritten to the r13
wording and its disposition marked `r13:`; the r12 ledger is committed at `docs/orchestration/state/2d-closeout/stageF/methods/r12/ledger.md` (origin/main 38a53a53). r13 adds nothing to the
note: every fact it takes out of the paper already prints at the note section the paper cites (`N:` probes).
After the independent review (`REVIEW.md`), the rows D18, M18, M19, C21, V50, H3, H22, R4 and RV-P3 were re-probed to the fixed wording; D18, M18 and M19 are KEEP again.
The r12 header follows.

## r12 header
# Fact ledger: paper before (origin/main 1a74560c) → paper after (worktree `wt-reg2`)

**Scope.** Every number, claim, limitation and disclosure printed in `paper_body.tex` and the abstract of
`main_paper.tex` at 1a74560c has one row. Paragraph ids: `P#` from `outline-before.md`, `N#` from `outline-after.md`.
The protected text of `main_paper.tex` (acknowledgments, funding, data availability, `\pubhold`) is unchanged and not
ledgered row by row; it is checked by diff (REPORT §4).

**Dispositions.**
- `KEEP` — stays in the paper (wording may change; meaning does not).
- `KEEP (guardrail)` — a qualifier that stays because without it a printed sentence would be false as read; the reason
  follows.
- `MOVE→note §n \label, Y` — leaves the paper; already printed in the note at that section.
- `ADDED-to-note file:line` — leaves the paper; it was not printed in the note, so it was added there.
- `COLLAPSED→row` — a repeat; the fact still prints at the row named.
- `NEW-paper` — newly printed in the paper, copied from the note.

**Probe column.** `P::text` must occur in the comment-stripped, whitespace-collapsed `paper_body.tex` after the rewrite;
`MP::` the same for `main_paper.tex`; `N:file::text` the same for that note file. Several probes are joined by ` && `.
`check_ledger.py` (same directory) runs every probe; its output is quoted in `REPORT.md`. A probe shows that the text is
there; the meaning of each row was checked by reading (step 5 of the method).

## Abstract (main_paper.tex)

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| A1 | 2D integral within about 1%, with a correlated shape difference | abs | KEEP | abs | `MP::integral within about 1\%, with a correlated shape difference` |
| A2 | five observables: central values only; normalizations agree with lower dimensions | abs | KEEP | abs | `MP::it yields central values only, whose normalizations agree with lower-dimensional results` |
| A3 | pseudo-experiments: background-subtraction bias, incomplete recovery, undercoverage at tested truths | abs | KEEP | abs | `MP::statistical undercoverage at the tested truths` |
| A4 | under the envelope prescription no tested reporting definition meets the 10% criterion | abs | KEEP ("adopted" → "specified", register only) | abs | `MP::specified envelope prescription, no tested reporting definition meets our 10\% precision criterion` |
| A5 | simulation-calibrated tests of hybrid nulls for five predictions all reject at 5% familywise | abs | KEEP | abs | `MP::all reject at the 5\% familywise level` |
| A6 | not exclusions; no evidence of gain over coarse projections; no recoil-response uncertainty; fine-grid convergence assumed; NuWro total not robust to CH | abs | KEEP | abs | `MP::not physical exclusions, show no evidence of gain over matched coarse projections, omit calorimetric recoil-response uncertainty, and assume fine-grid convergence` && `MP::is not robust to a hydrocarbon-target correction` |

## I. Introduction and scope

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| I1 | binned IBU widely used; response tensor grows with observables | P1 | KEEP | N1 | `P::the response tensor grows rapidly` |
| I2 | OmniFold: unbinned classifier density-ratio weights; no per-projection response tensor | P1 | KEEP | N1 | `P::classifier-based density-ratio estimation` |
| I3 | applications: H1 eight observables; ATLAS 24 Z+jets; survey; simulated T2K | P1 | KEEP | N1 | `P::eight observables in deep-inelastic scattering` && `P::twenty-four $Z$+jets observables` && `P::public simulated T2K near-detector sample` |
| I4 | apply to MINERvA ME data; reproduce published 2D d²σ/dpT dp∥; add Eavail, q3, W | P2 | KEEP | N2 | `P::then add available hadronic energy $\Eavail$` |
| I5 | simultaneous 3-, 4-, 5-observable central values | P2 | KEEP | N2 | `P::simultaneous three-, four-, and five-observable central values` |
| I6 | reco W fixed by reco (pT,p∥,q3): simultaneous, not independent | P2 | KEEP | N2 | `P::so the five observables are simultaneous but not independent` |
| I7 | data multi-differential measurements reach three dimensions | P2 | KEEP | N2 | `P::on data reach three dimensions` |
| I8 | case study of multidimensional unfolding and inference with a biased estimator | P3 | KEEP | N3 | `P::case study of multidimensional unfolding and of inference with a biased estimator` |
| I9 | question: reliability under generator-sized mismodelling; validation needed before interpretation | P3 | KEEP | N3 | `P::mismodels the truth by generator-sized amounts` |
| I10 | generator tests are secondary | P3 | KEEP | N3 | `P::As a secondary application` |
| I11 | coverage = rate intervals contain the truth | P3 | KEEP | N3 | `P::The coverage of unfolded intervals is the rate at which they contain the true cross section` |
| I12 | calibration = rate of rejecting a true hypothesis; obtainable without validated intervals by simulating the chain; to the extent the chain reproduces the data analysis | P3 | KEEP (guardrail: "can be obtained" is true only to that extent); r13: reworded | N3 | `P::Calibration can be obtained without validated intervals` && `P::to the extent that the simulated chain reproduces the analysis of the data` |
| I13 | the distinction organizes the paper: IV–VI validation, VII calibration | P3 | KEEP (merged into N3); r13: reworded | N3 | `P::test whether the unfolded results and their intervals can be validated` |
| I14 | validation studies are the main results; Table I gives config, test, limitation | P4 | KEEP | N3 | `P::validation studies are the paper's main results` |
| I15 | application tests predictions already disfavoured by the published measurement, calibrated within the implemented simulation model | P4 | KEEP | N3 | `P::already disfavours` && `P::with tests calibrated within the implemented simulation model` |
| TI1 | Table I row: 2D integral ~1%, shape difference; (a); published result; learner chosen after the comparison; IV A | T-I | KEEP ("…was seen" shortened) | T-I | `P::learner chosen after the comparison` |
| TI2 | row: 2D covariance median 6.45%; earlier band's coverage failed; not independently validated | T-I | KEEP | T-I | `P::an earlier band failed coverage` |
| TI3 | row: 3D–5D normalizations 1–2%; central values only | T-I | KEEP | T-I | `P::3D--5D normalizations agree at about 1--2\%` |
| TI4 | row: background bias up to 4% at high W; negative weights remove most; purity kept in central values | T-I | KEEP | T-I | `P::purity method kept in the central values` |
| TI5 | row: generator-sized changes partly recovered; regularization bias; in no quoted uncertainty | T-I | KEEP | T-I | `P::interpreted as regularization bias; in no quoted uncertainty` |
| TI6 | row: statistical intervals miscover under ~10% rate reduction; source not established | T-I | KEEP ("fixed thresholds" dropped: see V22) | T-I | `P::statistical intervals miscover under an about 10\% rate reduction` |
| TI7 | row: seed-dependent covariance; rounding instability; criteria not met; seed spread not measured | T-I | KEEP | T-I | `P::validation criteria not met; spread over seed pairs not measured` |
| TI8 | row: no tested reporting definition meets 10%; under the specified envelope prescription | T-I | KEEP (guardrail: the 10% statement is true under this prescription) | T-I | `P::under the specified envelope prescription` |
| TI9 | row: all ten hybrid-null tests reject; not exclusions; no recoil band; fine-grid convergence not shown | T-I | KEEP | T-I | `P::not physical exclusions; no recoil-response band; fine-grid convergence not shown` |
| S1 | scope: one implementation, one data set, tested observables/configurations/deformations, not OmniFold in general | P5 | KEEP | N4 | `P::multidimensional OmniFold in general` |
| S2 | no validated five-observable cross-section measurement | P5 | KEEP | N4 | `P::does not deliver a validated five-observable cross-section measurement` |
| S3 | central values are estimator outputs under definitions, response, background treatment, regularization | P5 | KEEP | N4 | `P::implemented observable definitions, simulated detector response, background treatment, and regularization` |
| S4 | their total intervals have no validated coverage | P5 | KEEP ("total intervals" → "intervals"; true of all their intervals, V27) | N4 | `P::their intervals have no validated coverage` |
| S5 | no covariance-based generator significance for them | P5 | COLLAPSED→V35 | N24 | `P::We quote no covariance-based generator significance` |
| S6 | tests are conditional tests of simulated hybrid hypotheses (G on fine grid, Tune v1 composition below) | P5 | KEEP | N4 | `P::conditional tests of simulated hybrid hypotheses` |
| S7 | calibrated size averaged over nuisance priors, not guaranteed at fixed nuisance values | P5 | KEEP (guardrail: the FWER sentence S8 is false as read for fixed nuisances without it); the fixed-nuisance clause prints at H29 | N4, N39 | `P::at 5\%, on average over the nuisance priors` |
| S8 | under the stated assumptions the decision rule controls FWER of the ten decisions at 5% | P5 | KEEP (guardrail: "under the assumptions") | N4 | `P::Under the assumptions of Sec.~\ref{sec:calibration}, their decision rule controls the familywise error rate of the ten decisions at 5\%` |
| S9 | no calorimetric recoil-response uncertainty | P5 | KEEP | N4 | `P::detector model has no calorimetric recoil-response uncertainty` |
| S10 | two predictions for carbon, data for CH | P5 | COLLAPSED→D33, D43, R2 | N8, N49 | `P::for carbon.` |
| S11 | rejections not physical exclusions; provide no measurement uncertainty | P5 | KEEP | N4 | `P::rejections are not physical exclusions of the generators and provide no measurement uncertainty` |
| S12 | the note gives full validation, uncertainty and joint-test details; pointers name the section | P6 | KEEP (now numbered pointers) | N4 | `P::is cited below by section` |

## II. Data, observables, and domains

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| D1 | twelve ME forward-horn-current run periods | P7 | KEEP | N5 | `P::twelve MINERvA medium-energy, forward-horn-current run periods` |
| D2 | 1.057×10²¹ POT; ⟨Eν⟩ near 6 GeV | P7 | KEEP | N5 | `P::$1.057\times10^{21}$ protons on target` && `P::average neutrino energy near \SI{6}{GeV}` |
| D3 | open-data AnaTuples; detector and MINOS described | P7 | KEEP | N5 | `P::(AnaTuples)` && `P::MINOS near detector that serves as its muon spectrometer` |
| D4 | files are an earlier production of the release | P7 | KEEP (r13: merged into the first sentence of Sec. II, with the Data-availability pointer) | N5 | `P::from an earlier production of the MINERvA open-data release` |
| D5 | signal definition: vertex 5980<z<8422 mm, apothem 850 mm, θ<20°, 1.5<p∥<60, pT≤4.5 GeV/c | P7 | KEEP | N5 | `P::$5980<z<\SI{8422}{mm}$` && `P::apothem \SI{850}{mm}` && `P::$1.5<\pPar<\SI{60}{GeV/c}$` && `P::$\pT\le\SI{4.5}{GeV/c}$` |
| D6 | selected events outside the definition (incl. CC outside muon limits) are background | P7 | KEEP | N5 | `P::whose muon lies outside these limits, are background` |
| D7 | selection: vertex, θ<20°, MINOS-matched negative track, dead time; flux treatment ref | P7 | KEEP | N5 | `P::a MINOS track of negative charge, with a dead-time requirement` |
| D8 | 4.12 M selected data events | P7 | KEEP | N5 | `P::$4.12$ million selected data events` |
| D9 | 32.8 M unweighted true signal, 20.5 M selected simulated; scaled to exposure | P7 | KEEP | N5 | `P::$32.8$ million unweighted true signal events and $20.5$ million selected simulated events` |
| D10 | GENIE 2.12.6 + Tune v1 (non-resonant pion reduction, RPA, low-recoil 2p2h) | P7 | KEEP | N5 | `P::GENIE~2.12.6` && `P::random-phase-approximation correction` |
| D11 | selection fixed as inputs grow; no added events | P7 | KEEP | N5 | `P::adding features does not add selected events or relax the signal definition` |
| D12 | truth-level observables: pT, p∥, q3 from generator four-vectors, W with struck-nucleon M | P8 | KEEP | N6 | `P::$q_{3}=` && `P::W=\sqrt{M^{2}+2M(E_{\nu}-E_{\mu})-Q^{2}}` |
| D13 | Eavail definition, Eq. (1) | P8 | KEEP | N6 | `P::\label{eq:eavail}` |
| D14 | 135 MeV constant instead of pion mass; neutrons and others contribute nothing | P8 | KEEP | N6 | `P::including neutrons, contribute nothing` |
| D15 | sums after FSI; π0 undecayed | P8 | KEEP | N6 | `P::appear undecayed` |
| D16 | 135 MeV inherited; defines the observable; used by analysis and every prediction | P8 | KEEP | N6 | `P::inherited from the analysis framework's definition` && `P::used consistently by the analysis and every prediction` |
| D17 | vs pion mass: 0.67% of events change true-Eavail bin; no bin changes by >1.05% | P8 | KEEP; r13: reworded | N6 | `P::it moves \SI{0.67}{\percent} of simulated events` && `P::more than \SI{1.05}{\percent}` |
| D18 | this effect not compared with the full covariance | P8 | KEEP (guardrail, r12 review B4 and r13 review NIT 1: limitation, materiality clause and pointer all stay) + note §7.1, Y | N6 | `P::an effect whose materiality is not established because it has not been assessed against the covariance (\nsec{sec:eavail-definition})` && `N:sec_3d.tex::Its materiality is not established` && `N:sec_3d.tex::has not been assessed against the projection of the scalar-5D covariance in use` |
| D19 | reco Eavail = 1.17 × calorimetric recoil (tracker, ECAL), muon removed | P8 | KEEP | N6 | `P::$1.17$ times the calorimetric recoil energy` |
| D20 | reco q3, W from muon kinematics and separate calorimetric q0 | P8 | KEEP | N6 | `P::separate calorimetric estimate $q_{0}$ of the energy transfer` |
| D21 | reco W exact function of reco (pT,p∥,q3); five inputs share information; five simultaneous, not independent | P9 | KEEP | N7 | `P::five simultaneous observables, not five independent measurements` |
| D22 | W²reco = (M̄+q0)² − q3²; q3 increases with q0 | P9 | KEEP | N7 | `P::$q_{3,\mathrm{reco}}$ increases with $q_{0}$` |
| D23 | exact apart from the W²=0 clamp (1.5% of events) | P9 | KEEP (guardrail: makes "exact function" literally true) | N7 | `P::exact apart from the clamp at $W^{2}=0$, which applies to \SI{1.5}{\percent} of simulated events` |
| D24 | truth θ from a fixed beam axis; truth W fixed up to ~1 mrad and M; residual ±2 MeV for 68% | P9 | KEEP | N7 | `P::\SI{1}{mrad}` && `P::within \SI{\pm2}{MeV} for 68\% of events` |
| D25 | only reco W redundant; reco Eavail its own estimator | P9 | KEEP | N7 | `P::Only reconstructed $W$ is fixed by the other inputs` |
| D26 | near-degenerate test-metric directions consistent with the redundancy, origin not shown | P9 | ADDED-to-note sec_eavailw.tex:136 (§8.2) | — | `N:sec_eavailw.tex::The nearly degenerate correlation directions of the joint-test metric` && `N:sec_eavailw.tex::origin has not been shown` |
| D27 | the information added by W has not been measured | P9 | ADDED-to-note sec_eavailw.tex:138 (§8.2) | — | `N:sec_eavailw.tex::the information added by $W$ has not been measured` |
| D28 | external predictions: GENIE 2.12.10 CV and +MEC (Valencia) for CH; NuWro 21.09, GiBUU 2019 for carbon | P10 | KEEP | N8 | `P::NuWro~21.09~\cite{Golan:2012wx} and GiBUU~2019~\cite{Buss:2011mx}, for carbon` |
| D29 | all per nucleon of their target | P10 | KEEP | N8 | `P::All are per nucleon of their target` |
| D30 | GENIE, NuWro reweighted exactly per event to analysis flux; GiBUU stops at ~20 GeV | P10 | KEEP | N8 | `P::reweighted exactly, event by event, to the analysis flux` |
| D31 | predictions' W with neutron mass changes coarse cells by ≤ ~1 MC SE where evaluated | P10 | KEEP (guardrail: "where evaluated" keeps the bound true) | N8 | `P::at most about one Monte Carlo standard error in each cell where this was evaluated` |
| D32 | where evaluated: GENIE CV and NuWro without 50–100 GeV; not cell-level for GENIE+MEC; not evaluable for GiBUU | P10 | GiBUU clause KEEP (restored, review S8); rest MOVE→note §8.1, Y | N8 | `P::(it cannot be evaluated for GiBUU)` && `N:sec_eavailw.tex::it was not evaluated at cell level for GENIE$+$MEC and cannot be evaluated for GiBUU` |
| D33 | predictions' pT about their own axis: ±4 MeV for 68% | P10 | KEEP | N8 | `P::\SI{\pm4}{MeV} for 68\% of events` |
| D34 | its net effect on the cells unmeasured | P10 | MOVE→note §8.2 sec:eavailw-definitions, Y | — | `N:sec_eavailw.tex::the net effect of this difference on the cell contents has not been measured` |
| D35 | hydrogen has no QE/2p2h/coherent CC; per-nucleon normalization does not remove the target difference | P10 | KEEP | N8 | `P::Hydrogen has no quasielastic, 2p2h, or coherent` |
| D36 | GENIE CH sample: carbon-only per nucleon exceeds CH by 8.3% for W<1.1 GeV | P10 | KEEP | N8 | `P::exceeds that of CH by \SI{8.3}{\percent} for $W<\SI{1.1}{GeV}$` |
| D37 | other W bins in the note | P10 | KEEP (numbered pointer); values printed in note §8.3, Y | N8 | `P::\nsec{sec:eavailw-generators}` && `N:sec_eavailw.tex::\SI{2.2}{\percent} below it` |
| D38 | NuWro and GiBUU comparisons contain such a difference, which the tests do not correct | P10 | KEEP | N8 | `P::which the tests of Sec.~\ref{sec:joint} do not correct` |
| D39 | fine grid: 14×16 muon bins × 7 Eavail × 7 q3 × 6 W | P11 | KEEP | N9 | `P::7 $\Eavail$, 7 $q_{3}$, and 6 $W$ bins` |
| D40 | coarse 3⁵ grid, edges nearest simulated tertiles (listed in the note) | P11 | KEEP | N9 | `P::nearest the simulated tertiles (\nsec{sec:joint5d-design})` |
| D41 | support rule ≥1000 events; 109 cells pass; others 0.47% of signal, total only | P11 | KEEP | N9 | `P::both at least 1000 events; \jtNcells{} cells pass` && `P::\SI{0.47}{\percent} of the expected signal` |
| D42 | GiBUU domain: 72 supported cells with p∥<6 GeV/c | P11 | KEEP | N9 | `P::the \jtNcellsGiBUU{} supported cells with $\pPar<\SI{6}{GeV/c}$` |

## III. Estimators and validation design

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| M1 | an iteration: reco-level classifier weight, pull-back to truth incl. unmatched, truth-level classifier | P12 | KEEP | N10 | `P::Each OmniFold iteration consists of two classification steps` |
| M2 | cross section: histogram reweighted truth; divide by flux, targets, width | P12 | KEEP | N10 | `P::dividing by integrated flux, target count, and bin width` |
| M3 | failed-reco events are unmatched truth; no efficiency correction | P12 | KEEP | N10 | `P::no separate efficiency correction is applied` |
| M4 | purity weight w_pur(b) = max(0, 1−B_b/D_b) | P13 | KEEP | N11 | `P::$w_{\mathrm{pur}}(b)=\max(0,\,1-B_{b}/D_{b})$` |
| M5 | negative-weight treatment: target D−B pointwise; clipped refinement | P13 | KEEP | N11 | `P::so the target is $D(x)-B(x)$ pointwise` |
| M6 | targets share bin integrals where B<D, differ inside bins | P13 | KEEP | N11 | `P::share bin integrals wherever $B_{b}<D_{b}$` |
| M7 | in-sample training, no held-out split, no early stopping, no class balancing, no ESS | P14 | KEEP (training facts); r13: the clause "no effective sample size of the unfolded ensemble is computed" MOVE→note §3.1 sec:method-algo, Y (paper points: "training details") | N12 | `P::without a held-out or cross-fitted split, early stopping, or class balancing (training details: \nsec{sec:method-algo})` && `N:sec_method.tex::No effective sample size of the unfolded ensemble is computed` && `N:sec_method.tex::with no held-out or cross-fitted split and no early stopping` |
| M8 | all configurations: five iterations, GBDT; each result names its configuration | P15 | KEEP | N13 | `P::All estimator configurations use five OmniFold iterations` |
| M9 | iteration count and capacity regularize | P15 | KEEP | N13 | `P::iteration count and classifier capacity regularize the unfolding` |
| M10 | no hyperparameter search on data; sklearn defaults; LightGBM matched; refinement capacity chosen in simulation closure studies | P15 | KEEP; r13: reworded | N13 | `P::no hyperparameter search was performed on data` && `P::was chosen in simulation closure studies` |
| M11 | 2–5D central values use (a); the 2D one is its universe ensemble's central value | P15 | KEEP; r13: reworded | N13 | `P::configuration~(a), the central-value estimator` && `P::central value is that of its systematic-universe ensemble` |
| M12 | joint tests use (e) | P15 | KEEP | N13 | `P::configuration~(e), the joint-test estimator` |
| M13 | (e) was selected before the joint-test design was fixed | P15 | MOVE→note §3.2 sec:method-config, Y | — | `N:sec_method.tex::It was selected before the joint-test design was frozen` |
| M14 | (e)'s negative weights and capacity remove most purity bias at nominal truth, highest W | P15 | KEEP | N13 | `P::remove most of the bias of the purity method at nominal truth in the highest-$W$ cells` |
| M15 | reported central values and covariance use purity subtraction, whose bias is in V A | P15 | KEEP | N13 | `P::with the purity-based subtraction, whose bias in simulation is given in Sec.~\ref{sec:closure}` |
| M16 | they were computed before the purity bias was found and the refinement developed, and not recomputed | P15 | MOVE→note §3.2 sec:method-config, Y | — | `N:sec_method.tex::produced before the purity bias was found and the refinement was developed, and they were not regenerated` |
| M17 | the refinement also fails the data-stability test | P15 | COLLAPSED→V42 | N25 | `P::the refinement fails a data-stability requirement` |
| M18 | (e) keeps five iterations: 10, 15, 20 did not reduce the rule's measure of model dependence | P15 | KEEP (guardrail, r12 B2, restored after r13 review SHOULD-FIX 2: scoped to the rule's measure, with the §9.4 pointer) | N13 | `P::did not reduce the rule's measure of model dependence, the largest residual proxy over the development truth changes (\nsec{sec:gbdt-model-dependence})` && `N:sec_5d.tex::only if they reduced the model dependence; none did, so five were kept` |
| M19 | …under a rule set before the comparison | P15 | KEEP (restored after r13 review SHOULD-FIX 2) + note §9.4, Y | N13 | `P::Configuration~(e) keeps five iterations under a rule fixed before the comparison` && `N:sec_5d.tex::a rule fixed before the comparison would have replaced its five iterations by 10, 15, or 20` |
| T2a | Table II caption: five iterations; 100 trees, 8 leaves; (c)–(e) deterministic; not combined; full matrix in note | T-II | KEEP (pointer numbered) | T-II | `P::Results from different configurations are not combined` && `P::\nsec{sec:method-config} gives the full matrix` |
| T2b | rows (a)–(e): learner, background treatment, use | T-II | KEEP (unchanged) | T-II | `P::(a) central value: LightGBM, seed 42 in 2D` && `P::(b) cross-check: scikit-learn exact splits, unseeded` && `P::negative weights; refinement 100 trees, 8 leaves` && `P::negative weights; refinement 400 trees, 31 leaves` |
| M20 | closure: recovery of a specified deformation with the prior fixed | P16 | KEEP | N14 | `P::with the prior, the initial truth distribution, held fixed` |
| M21 | coverage tests estimator and interval together; pointwise, not simultaneous | P16 | KEEP | N14 | `P::the coverage tested here is pointwise` |
| M22 | closure/deformation/coverage reweight pseudo-data truth; response fixed at truth; prior Tune v1 | P16 | KEEP | N14 | `P::keeps the detector response at fixed truth` |
| M23 | envelope reweights the prior used on data | P16 | KEEP | N14 | `P::instead reweights the prior used to unfold the data` |
| M24 | every study uses the analysis response except the calibration, which draws detector bands | P16 | KEEP | N14 | `P::except the calibration of the tests, which also draws the detector bands` |

## IV. Two-dimensional benchmark

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| B1 | end-to-end test against a measurement from the same data | P17 | KEEP | N15 | `P::end-to-end test of the unfolding against a measurement from the same data` |
| B2 | integrated σ 3.073e-38 vs 3.039e-38; ratio 1.011 | P17 | KEEP | N15 | `P::\SI{\sigTwoD}{cm^2/nucleon}` && `P::a ratio of $\ratioTot$` |
| B3 | 95.6% of 205 bins within 10%; standardized differences RMS 0.564 | P17 | KEEP | N15 | `P::\SI{\binsTen}{\percent} agree within \SI{10}{\percent}` && `P::RMS of $\pullRMS$` |
| B4 | χ²/ndf = 2.65 with pseudo-inverse, rank 205, condition number 1.5e12, ndf = rank | P17 | KEEP | N15 | `P::$\chi^{2}/\mathrm{ndf}=\chiPaper$` && `P::condition number $1.5\times10^{12}$` |
| B5 | indicates a correlated shape difference; used only as a descriptive distance | P17 | KEEP | N15 | `P::correlated shape difference, not a normalization difference` && `P::we use it only as a descriptive distance` |
| B6 | spread over many eigenmodes; no pT or p∥ band >15% | P17 | KEEP | N15 | `P::carrying more than \SI{15}{\percent} of it` |
| B7 | source not identified | P17 | KEEP | N15 | `P::its source has not been identified` |
| B8 | learner dependence: ten LightGBM seeds 2.64–2.75; exact-split 3.66 unseeded, 3.57 one seeded run | P17 | KEEP | N15 | `P::ten LightGBM training seeds give 2.64--2.75` && `P::$\chiPaperExact$ unseeded and $\chiPaperExactSeeded$ in one run with a fixed seed` |
| B9 | exact-split spread over seeds not measured | P17 | MOVE→note §3.2 sec:method-config, Y | — | `N:sec_method.tex::the spread over seeds is unmeasured` |
| B10 | LightGBM quoted so the central value shares its covariance's estimator | P17 | KEEP; r13: reworded | N15 | `P::result as the central value because its covariance uses the same estimator` |
| B11 | this choice replaced the exact-split result | P17 | MOVE→note §3.2 sec:method-config, Y | — | `N:sec_method.tex::Until 2026-10-11 the quoted 2D central value was an` |
| B12 | chosen after both comparisons were known, so a reproduction, not an independent validation | P17 | KEEP (guardrail: "end-to-end test" (B1) would read as an independent validation without it); r13: reworded | N15 | `P::This learner was chosen after both comparisons were known, so the benchmark is a reproduction rather than an independent validation` |
| B13 | learners differ by median 0.98% (max 12.2%), in no covariance term | P17 | KEEP | N15 | `P::per-bin median of \SI{0.98}{\percent} (maximum \SI{12.2}{\percent})` && `P::included in no term of the covariance` |
| B14 | Fig. 1 projections; published covariance sets the scale; significance needs cross-covariance | P17 | KEEP | N15 | `P::would also require their cross-covariance` |
| F1 | Fig. 1 caption (bands, learner dependence omitted, bands correlated, panels) | F-1 | KEEP (unchanged) | F-1 | `P::so their overlap is not a compatibility test` |
| C1 | 2D covariance = four blocks: 187 universes, 300 replicas, five seed settings (own size poorly determined), three period groups | P18 | KEEP | N16 | `P::five seed settings, so that its own size is poorly determined` && `P::run period (three period groups)` |
| C2 | median 6.45% per bin, 4.75% integral vs published 6.85%, 4.61% | P18 | KEEP | N16 | `P::median of \SI{\uqMedian}{\percent} per bin and is \SI{\uqIntegral}{\percent}` && `P::\SI{\uqPaper}{\percent} and \SI{\uqPaperIntegral}{\percent} for the publication` |
| C3 | universe block dominates per bin and integral; run-period raises median 6.04→6.45%; block sizes in note | P18 | KEEP | N16 | `P::raises the per-bin median from \SI{\uqSFiveMedian}{\percent}` && `P::(block sizes: \nsec{sec:results-uq})` |
| C4 | published flux 4.01% > ours 3.75%; reason not determinable from released inputs | P18 | KEEP | N16 | `P::(median \SI{4.01}{\percent}) is larger than ours` && `P::the released inputs do not let us determine` |
| C5 | blocks added as independent; assumes linear response | P18 | KEEP | N16 | `P::The block sum assumes independent blocks and a linear response to simultaneous perturbations` |
| C6 | run-period block rank ≤ 2 | P18 | KEEP | N16 | `P::the run-period block has rank at most two` |
| C7 | universe unfoldings approximate failed-reco weighting; not corrected; tests in 2 of 187 cannot exclude a small effect | P18 | KEEP (r13: "we do not correct this approximation" → "this uncorrected approximation") | N16 | `P::tests in two of the 187 universes cannot exclude a small effect of this uncorrected approximation` |
| C8 | run periods not mutually consistent within the other uncertainties | P19 | KEEP | N17 | `P::Data from different run periods are not mutually consistent within the other uncertainties` |
| C9 | ~7% step near 8 GeV/c | P19 | KEEP | N17 | `P::step of about \SI{7}{\percent} near \SI{8}{GeV/c}` |
| C10 | cause unknown; data cannot establish which period is correct | P19 | KEEP | N17 | `P::these data cannot establish which period is correct` |
| C11 | block from double ratios, no reference; includes the inconsistency; 2.0% on integral | P19 | KEEP | N17 | `P::with no group chosen as the reference` && `P::\SI{2.0}{\percent} on the integrated cross section` |
| C12 | block does not identify a correct period | P19 | MOVE→note §4.5 sec:uq-combine, Y (and COLLAPSED→C10) | N17 | `N:sec_systematics.tex::It does not identify which period is correct` |
| C13 | interpretation limited by few groups, shrinkage, retained noise | P19 | MOVE→note §4.5 sec:uq-combine, Y | — | `N:sec_systematics.tex::Its interpretation is limited by the small number of period groups` |
| C14 | contains the differences by construction: says nothing about its coverage | P19 | KEEP (restated as effect) | N17 | `P::Because the block is built from the observed differences among the periods, its size is not validated` |
| C15 | its consistency check passes whatever the data: not a test | P19 | KEEP (restated) | N17 | `P::its own consistency check cannot fail` |
| C16 | stat block: 300 replicas at CV seed, templates resampled, median 0.684% | P20 | KEEP (SEC4-bound phrase) | N18 | `P::with a median statistical uncertainty of \SI{0.684}{\percent}` |
| C17 | replica mean offset 0.26σ; block about the mean excludes it | P20 | KEEP | N18 | `P::median of 0.26 statistical standard deviations` |
| C18 | coverage of this block and of the total untested | P20 | KEEP (guardrail: without it the rescoring below reads as a coverage result for the quoted block) | N18 | `P::The coverage of this block, and of the total, has not been tested` |
| C19 | earlier band undercovered in tails: 100 closure pseudo-experiments at fixed truth, 91.2% within 2σ vs 95.4% | P20 | KEEP (SEC4-bound; r13: "Two earlier versions … were scored on") | N18 | `P::\covTwoDNtoy{} closure pseudo-experiments at a fixed truth` && `P::\SI{\covTwoDCTwoPctOne}{\percent} of standardized residuals fell within two standard deviations, against \SI{95.4}{\percent} nominal` |
| C20 | those pseudo-experiments were specified in advance | P20 | MOVE→note §5.2 sec:coverage, Y | — | `N:sec_validation.tex::Its design, criteria and positive control were fixed in advance` |
| C21 | the band was then rebuilt | P20 | KEEP (r13 review SHOULD-FIX 3: the rebuilt band is named as the second band, scored post hoc) + note §5.2, Y | N18 | `P::A post hoc rescoring of the same pseudo-experiments against the second, rebuilt band` && `N:sec_validation.tex::The rebuilt band, evaluated post hoc (history)` |
| C22 | rescoring vs rebuilt band: 97.7% within 2σ, 78.1% within 1σ | P20 | KEEP (SEC4-bound) | N18 | `P::removes the tail undercoverage: \SI{97.7}{\percent} fall within two standard deviations and \SI{78.1}{\percent} within one` |
| C23 | rescoring not an independent coverage test; reuses the resampling mechanism | P20 | KEEP (guardrail: "removes the tail undercoverage" would read as a validation without it); r13: reworded | N18 | `P::This rescoring is not an independent coverage test, because the simulated part of the rebuilt band reuses the resampling mechanism of those pseudo-experiments` |
| C24 | rescoring made after the failure was seen | P20 | MOVE→note §5.2 sec:coverage, Y | — | `N:sec_validation.tex::which is post hoc and partly circular` |
| C25 | rebuilt band not tested on independent pseudo-experiments | P20 | COLLAPSED→C18, C23 (r13: the quoted block is untested, C18; the rebuilt band's only score is the non-independent rescoring, C23); note §4.2 and §5.2, Y | N18 | `P::The coverage of this block, and of the total, has not been tested` && `P::This rescoring is not an independent coverage test` && `N:sec_systematics.tex::it has not been tested independently` && `N:sec_validation.tex::has not been run` |
| C26 | quoted stat block is a different ensemble from the rebuilt band | P20 | KEEP (guardrail, r12 review B3; r13: stated before the rescoring, "distinct from the quoted block") + note §5.2, Y | N18 | `P::Two earlier versions of the statistical band, distinct from the quoted block` && `N:sec_validation.tex::The quoted statistical block is now a different ensemble` |
| C27 | 2D central value reproducible, covariance with same estimator | P21 | KEEP | N19 | `P::The two-dimensional central value is therefore reproducible` |
| C28 | intervals, bias, covariance not independently validated; no coverage claim (independent samples, simultaneous) | P21 | KEEP; r13: reworded | N19 | `P::have not been independently validated: we claim no coverage, either on independent simulated samples or simultaneously over all reported bins and projections` |
| C29 | no calibrated significance for generator comparisons | P21 | KEEP | N19 | `P::the covariance provides no calibrated significance for generator comparisons` |
| C30 | no block includes miss-row approximation, learner dependence, unfolding-model/regularization dependence | P21 | KEEP (r13: "No block includes" → "The covariance omits"; the covariance is the block sum) | N19 | `P::The covariance omits the approximation in the systematic-universe unfoldings` && `P::and the dependence on the unfolding model and its regularization` |
| C31 | detector response assumed within its parametrized family | P21 | KEEP; r13: reworded | N19 | `P::it assumes that the detector response varies only within its parametrized family` |
| C32 | validated total intervals would need independent simulation and generator samples, not available | P21 | MOVE→note §4.6 sec:uq-2d-scope, Y | — | `N:sec_systematics.tex::an independent simulation sample of production size` && `N:sec_systematics.tex::none is available` |

## V. Five observables

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| V1 | each higher-D central value is checked against the lower-D result; 3-, 4-, 5-obs marginal normalizations agree at ~1–2% | P22 | KEEP (review B1: "is checked against" restored) | N20 | `P::Each higher-dimensional central value is checked against the lower-dimensional result it extends` && `P::marginal normalizations agree at the approximately $1$--$2\%$ level` |
| V2 | 3D Eavail-bump closure residual 0.10 of injected | P22 | KEEP | N20 | `P::leaves a residual of 0.10 of the injected change` |
| V3 | 4D q3-bump closes within 1.1% | P22 | KEEP | N20 | `P::closes to within \SI{1.1}{\percent} in the $q_{3}$ marginal` |
| V4 | neither had an acceptance criterion defined in advance | P22 | MOVE→note §5.1 tab:closure-map and §9.1 tab:validation-design-5d, Y | — | `N:sec_validation.tex::no predeclared threshold` && `N:sec_5d.tex::no threshold set in advance` |
| V5 | these closures reweight signal only | P22 | KEEP | N20 | `P::These closure tests reweight the simulated signal only` |
| V6 | with purity subtraction: highest-W cells biased up to 4% in simulation, ~1 quoted SD in one cell; quoted uncertainties omit it | P22 | KEEP (SEC4-bound) | N20 | `P::are biased by up to \SI{4}{\percent} in simulation, about one quoted standard deviation in one $(\Eavail,W)$ cell` && `P::the quoted uncertainties omit this bias` |
| V7 | negative weights (deterministic variant, i.e. (d)): <0.3% there, ≤0.4% elsewhere, up to 1% in joint cells | P22 | KEEP (SEC4-bound; estimator named by its Table II label) | N20 | `P::configuration~(d), reduces it to below \SI{0.3}{\percent}` && `P::at most \SI{0.4}{\percent} elsewhere in the projection` && `P::leaving up to \SI{1}{\percent} in some joint cells` |
| V8 | on data the treatments differ by ≤1.4% | P22 | KEEP (SEC4-bound) | N20 | `P::on data the treatments differ by at most \SI{1.4}{\percent}` |
| V9 | only part of a generator-sized Eavail change is recovered | P23 | KEEP | N21 | `P::The unfolding recovers only part of a change of the $\Eavail$ shape` |
| V10 | GiBUU-to-GENIE: several % in largest cells, up to 74% at high W | P23 | KEEP (SEC4-bound) | N21 | `P::by up to \SI{74}{\percent} at high $W$` |
| V11 | the 74% cell: 0.8≤Eavail<1.5 GeV, W≥3 GeV | P23 | KEEP | N21 | `P::$0.8\le\Eavail<\SI{1.5}{GeV}$, $W\ge\SI{3}{GeV}$` |
| V12 | its cross-section share was not recorded by the study | P23 | ADDED-to-note sec_5d.tex:118 (§9.2) | — | `N:sec_5d.tex::whose share of the cross section the deformation study did not record` |
| V13 | with or without background; background subtraction alone does not explain it | P23 | KEEP | N21 | `P::with or without background, so background subtraction alone does not explain the residual` |
| V14 | not in quoted uncertainties | P23 | KEEP | N21 | `P::is not included in the quoted uncertainties` |
| V15 | interpreted as regularization bias; persists over iterations/capacity: 30 iterations −26%; larger classifier fits reco better, not residual | P23 | KEEP | N21 | `P::We interpret it as regularization bias` && `P::reduce the $\Eavail$ residual by \SI{26}{\percent}` |
| V16 | other shapes, joint-test estimator: 16–31% in most affected cell; within quoted total in ~half (V D covariance omits regularization bias) | P23 | KEEP (SEC4-bound) | N21 | `P::it is \SIrange{16}{31}{\percent} in the most affected` && `P::within the quoted total uncertainty in about half of those cells` && `P::which omits the regularization bias` |
| V17 | end-to-end coverage test of bias-corrected statistical intervals, config (c), 400 pseudo-experiments per truth | P24 | KEEP | N22 | `P::The end-to-end test unfolds 400 pseudo-experiments per truth` && `P::Statistical intervals from configuration~(c)` |
| V18 | it failed its acceptance criterion | P24 | KEEP (as result: "miscover", "below the acceptance threshold") | N22 | `P::lies below the acceptance threshold of 0.66` |
| V19 | criterion set before the test | P24 | MOVE→note §9.5 sec:coverage-5d and §9.1 table, Y | — | `N:sec_5d.tex::It failed its predeclared futility criterion` && `N:sec_5d.tex::fixed in advance} \\` |
| V20 | intervals corrected for nominal-truth closure bias; construction in note | P24 | KEEP | N22 | `P::corrected for the estimator's closure bias at nominal truth` && `P::(interval construction: \nsec{sec:coverage-5d})` |
| V21 | the change: true-signal reweight, no renormalization, background unchanged; ≈10% rate cut, weak Eavail slope | P24 | KEEP | N22 | `P::without renormalization and with the background unchanged` |
| V22a | intervals miscover at the tested truths (nominal included), most strongly under the rate change | P25 | KEEP (restored, review S2) | N22 | `P::miscover at the tested truths, most strongly when the true signal rate is lowered` |
| V22 | 51 of 153 integrals: 68% coverage UCB below 0.66 (fixed before), as low as 0.06 | P24 | KEEP ("fixed before the test" → V19) | N22 | `P::51 of the 153 reported cell and projection integrals` && `P::with coverage as low as 0.06` |
| V23 | diagnosis: rate change recovered; intervals not too narrow apart from a minor effect; residual bias growing with W not removed by nominal correction | P25 | KEEP; r13: reworded | N23 | `P::The rate change itself is recovered, and apart from a minor effect the intervals are not too narrow` && `P::residual bias that grows with $W$ and survives the nominal-truth bias correction` |
| V24 | per-quantity bias and spread inferred from a Gaussian fit to 68%/95% coverage, not measured | P25 | KEEP (guardrail: "attributes the miscoverage to a residual bias" is an inference, stated as such); r13: reworded | N23 | `P::inferred from a Gaussian fit to each quantity's 68\% and 95\% coverage rather than measured directly` |
| V25 | source of the bias not established | P25 | KEEP | N23 | `P::the source of the bias is not established` |
| V26 | the separating test (background fraction vs estimator) not run | P25 | MOVE→note §9.5 sec:coverage-5d, Y | — | `N:sec_5d.tex::The test that would decide, rerunning the same` && `N:sec_5d.tex::has not been run` |
| V27 | intervals miscover at tested truths; no frequentist coverage claimed for 5-obs intervals | P25 | KEEP (guardrail: the 5D intervals keep "no validated coverage"; r13: "No frequentist coverage is therefore claimed" → "therefore have no validated frequentist coverage") | N23 | `P::The five-observable intervals therefore have no validated frequentist coverage` |
| V28 | normalization agreement coexists with substantial residual bias | P25 | KEEP | N23 | `P::coexists with substantial residual bias under the tested deformations` |
| V29 | envelope and uncertainty calibration remain limiting (V D, V E) | P25 | COLLAPSED→V30, V44 (a roadmap sentence) | N24, N26 | `P::does not meet the validation criteria of its specification` |
| FG2 | Fig. 2 caption: residual at nominal truth; (c) 9 and (d) 60 pseudo-experiments; not paired; panels; SEM | F-2 | KEEP (unchanged) | F-2 | `P::(9 pseudo-experiments)` && `P::The pseudo-experiments are not paired` |
| FG3 | Fig. 3 caption: (d) GiBUU/GENIE, 60; nominal 0.39%; (e) three held-out shapes, 20 each; band; nominal 0.09% (40); seeds: development / assessment seeds later used in development | F-3 | KEEP (unchanged) | F-3 | `P::largest residual is \SI{0.39}{\percent}` && `P::\SI{0.09}{\percent}` && `P::separate assessment seeds, which also entered its later development` |
| FG4 | Fig. 4 caption: 153 integrals; (c); 400; nominal: 0 below 0.66, 2 below 0.94; CP bounds at 0.05/459; third truth incorrectly constructed, verdict independent | F-4 | KEEP; r13: reworded | F-4 | `P::and two lie below the 0.94 threshold` && `P::$0.05/459$` && `P::is omitted because its reweighting does not implement the intended change; the test's verdict does not depend on it` |
| FG4b | thresholds 0.66 and 0.94 "fixed in advance"; third truth "was found to be" | F-4 | MOVE→note §9.1 tab:validation-design-5d, Y (chronology words only) | — | `N:sec_5d.tex::upper bound on coverage at least 0.66 (0.94), fixed in advance` |
| V30 | 5D covariance has not met the validation criteria of its specification | P26 | KEEP (consequential: it is the only 5D covariance used) | N24 | `P::does not meet the validation criteria of its specification` |
| V31 | …criteria set before it was built | P26 | MOVE→note §9.6 sec:eavailw-construction, Y | — | `N:sec_5d.tex::It is used although it has not passed the acceptance criteria of its specification` |
| V32 | 42-cell (Eavail,W) projection; separate from the test calibration | P26 | KEEP; r13: reworded | N24 | `P::\zprojCells-cell $(\Eavail,W)$ projection` && `P::the calibration of the joint tests (Sec.~\ref{sec:joint}) does not use it` |
| V33 | seed-dependence criterion cannot be met: no noise bound fixed before construction | P26 | MOVE→note §9.6, Y | — | `N:sec_5d.tex::requires its null bound to be fixed before production` |
| V34 | used, and no other 5D covariance, for the V B comparisons | P26 | KEEP; r13: reworded | N24 | `P::use this covariance and no other five-observable covariance` |
| V35 | no covariance-based generator significance, because covariances depend on seed | P26 | KEEP | N24 | `P::We quote no covariance-based generator significance, because covariances from this estimator depend measurably on its random seed` |
| V36 | two further covariances at two seeds: projected uncertainty moves ~6.1% vs 5% limit | P26 | KEEP | N24 | `P::in two further covariances built at two seed settings` && `P::by about \SI{6.1}{\percent}, against a stability limit of \SI{\sprojBound}{\percent}` |
| V37 | the limit was set before they were produced | P26 | MOVE→note §9.6, Y | — | `N:sec_5d.tex::before production, as a direct movement tolerance` |
| V38 | rests on one seed pair; spread over pairs not measured | P26 | KEEP (guardrail: the 6.1% is one pair's value) | N24 | `P::This rests on one seed pair, and the spread over seed pairs has not been measured` |
| V39 | five fixed-seed bands (26.0% of √TrC) cannot vary; their sensitivity could move the total either way; full sensitivity unmeasured | P26 | KEEP | N24 | `P::\SI{\pinnedBandsSqrtTr}{\percent} of $\sqrt{\mathrm{Tr}\,C}$` && `P::could move the total in either direction` |
| V40 | estimators unstable at the rounding level | P27 | KEEP | N25 | `P::The estimators are also unstable at the level of rounding` |
| V41 | rounding-level changes move the higher-capacity refinement by up to 2.6 σstat, baseline 2.5 | P27 | KEEP | N25 | `P::by up to 2.6 statistical standard deviations, as they move those of the baseline estimator (2.5)` |
| V42 | the refinement fails data stability with bounds 0.3 (median), 1.0 (max) σstat | P27 | KEEP | N25 | `P::fails a data-stability requirement of at most 0.3 (median) and 1.0 (maximum) statistical standard deviations` |
| V43 | for the joint-test estimator the spread is inside the bootstrap uncertainty; limits reproducibility | P27 | KEEP | N25 | `P::lies inside the data-bootstrap statistical uncertainty` && `P::it limits how exactly the central values can be reproduced` |
| V44 | no tested reporting definition meets the 10% target under the specified envelope prescription | P28 | KEEP (guardrail: the statement holds under that prescription; r13: the prescription leads the sentence) | N26 | `P::Under the specified envelope prescription, none of the reporting definitions of a five-observable measurement tested in a dedicated study meets our \SI{10}{\percent} precision target` |
| V45 | within the study's rules and computing budget | P28 | MOVE→note §9.4 sec:gbdt-model-dependence, Y ("tested" keeps N26 true without it) | — | `N:sec_5d.tex::that the study's selection rules allow within its computing budget` |
| V46 | a separate study searched for a definition meeting targets set in advance | P28 | KEEP (the search; r13: merged into V44's sentence, "tested in a dedicated study"); "set in advance" MOVE→note §9.4, Y | N26 | `P::tested in a dedicated study` && `N:sec_5d.tex::fixed before the study` |
| V47 | envelope: largest data shift over five generator-sized prior reweights; a sensitivity diagnostic tracking regularization bias, not an interval | P28 | KEEP | N26 | `P::it is a sensitivity diagnostic that tracks the regularization bias, not an interval` |
| V48 | added linearly to the probabilistic half-width | P28 | KEEP | N26 | `P::linearly to the probabilistic half-width` |
| V49 | joint-test estimator: envelope alone exceeds target (10% median 68% half-width) for 109 cells and the 39-cell fallback | P28 | KEEP (r13: the target stated in its own sentence) | N26 | `P::The target is a \SI{10}{\percent} median half-width for the total 68\% interval` && `P::the envelope alone exceeds it for the \jtNcells{} coarse joint cells` && `P::the 39 supported $(\Eavail,W)$ cells` |
| V50 | 27-cell partition: envelope alone does not; 1.4% normalization lifts median above | P28 | KEEP; r13: reworded (review NIT) | N26 | `P::into 27 cells, the same estimator's envelope alone does not exceed it, but the \SI{1.4}{\percent} normalization` |
| V51 | envelope median ~10–13% per cell, comparable to generator differences | P29 | KEEP | N27 | `P::median of about 10--13\% per cell` |
| V52 | motivates tests of the predictions as hypotheses | P29 | KEEP | N27 | `P::It motivates the different route to inference` |

## VI. What limits the estimator

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| L1 | three results point to retained prior: V B residual, envelope (exceeds in two of three definitions), null displacement | P30 | KEEP | N28 | `P::alone exceeds the precision target in two of the three tested reporting definitions` |
| L2 | miscoverage also attributed to a residual bias, inferred; same origin not established | P30 | KEEP (guardrail: "same origin not established" keeps the miscoverage out of the three results); r13: "inferred from the stored pseudo-experiments and not removed by the nominal-truth correction" COLLAPSED→V23, V24 (Sec. V C) | N28 | `P::but whether that bias has the same origin is not established` && `P::A diagnosis of the stored pseudo-experiments attributes the miscoverage` |
| L3 | the separating test not run | P30 | COLLAPSED→V26 (note) | — | `N:sec_5d.tex::The test that would decide, rerunning the same` |
| L4 | exact binned IBU, same 109 cells and development truths, 5 iterations: about the same median residual | P31 | KEEP | N29 | `P::leaves about the same median residual as the boosted-tree estimator` |
| L5 | 8.3% vs 9.5% for GiBUU-to-GENIE | P31 | KEEP (now in Table III) | T-III | `P::GiBUU/GENIE, $\Eavail$ & 9.5 & 8.3` |
| L6 | the tree approximation dominates only a small share | P31 | KEEP (quantified from the note: 15 of 144) | N29 | `P::Of the 144 cell-and-truth-change residuals above \SI{2}{\percent} whose diagnosis is stable under the truth resolution, pooled over five truth changes, the tree approximation dominates only 15` |
| L7 | most are weakly constrained (Cramér–Rao widths >10%); regularization trades variance for bias | P31 | KEEP | N29 | `P::Cram\'er--Rao widths above \SI{10}{\percent}` && `P::the regularization trades a large variance for the bias` |
| L8 | longer exact iteration removes much for GiBUU-to-GENIE, not for every change; long runs do not converge; last iterates | P31 | KEEP | N29 | `P::removes much of the residual for the GiBUU-to-GENIE change, but not for every change` && `P::the long runs do not converge` |
| L9 | scope: binned, signal-only, noise-free, response fixed, same truths; stable residuals only (38% of >2%); no bound on unbinned; no coverage or interval | P31 | KEEP (guardrail: L10's "consistent with" holds only within it); r13: reworded | N29 | `P::(\SI{38}{\percent} of the joint-cell residuals above \SI{2}{\percent})` && `P::What unbinned information could recover, the coverage failure, and the validity of any interval lie outside its scope` |
| L10 | within that scope: consistent with regularization of the inverse problem, not the tree approximation | P31 | KEEP | N29 | `P::rather than with the tree approximation of the classifiers` |
| L11 | NEW: 121 of the 144 in weakly constrained quantities | — | NEW-paper (note §9.3, Y) | N29 | `P::most of the 144 (121)` && `N:sec_5d.tex::Most of the 144 (121)` |
| L12 | NEW: Table III, J-cell medians at 5 iterations (trees vs exact: 9.5/8.3, 5.4/5.4, 5.6/4.9, 4.3/5.3) and exact longer runs (3.3, 0.8; 3.3, 2.8; 8.9; 6.7) | — | NEW-paper (note §9.3, Y; labels §9.4, Y) | T-III | `P::NuWro/GENIE, $(\pT,\pPar,\Eavail)$ & 5.6 & 4.9 & 4.4 & 8.9` && `P::$q_{3}$ at fixed $(\Eavail,W)$ & 4.3 & 5.3 & 6.6 & 6.7` && `N:sec_5d.tex::\SI{9.5}{\percent}, \SI{5.4}{\percent}, \SI{5.6}{\percent} and \SI{4.3}{\percent} for the boosted trees` && `N:sec_5d.tex::but not for W3 and the $q_3$ stress (\SI{4.4}{\percent} and \SI{6.6}{\percent} after 200 iterations, \SI{8.9}{\percent} and \SI{6.7}{\percent} after $10^{5}$)` |
| L13 | checks to carry: background-inclusive closure; generator-sized changes; coverage off nominal; seed and rounding stability; run-period consistency | P32 | KEEP | N30 | `P::closure with the backgrounds included` && `P::and run-period consistency` |
| L14 | calibration possible when intervals cannot be validated, to the extent the chain reproduces the data | P32 | KEEP (guardrail) | N30 | `P::tests can still be calibrated by simulating the analysis chain at the hypothesis` |

## VII. Application

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| X6 | why unfold: truth-level comparison without folding each generator; 2D reusable; higher-D qualitative | P57 | KEEP (moved within the paper to the opening of Sec. VII) | N31 | `P::without simulating each generator through the detector` |
| X7 | for tests the advantage is smaller; reco-level test avoids regularization bias but needs the same response model, the hybrid construction | P57 | KEEP (moved) | N31 | `P::For hypothesis tests the advantage is smaller` && `P::which is the hybrid construction of Sec.~\ref{sec:hypotheses}` |
| X8 | our tests calibrate the unfolded statistic: bias in the null, not the decision | P57 | KEEP (moved) | N31 | `P::so that the bias enters the null distribution rather than the decision` |
| X9 | power not compared with a reco-level test | P57 | KEEP (moved; guardrail: the paragraph argues for the approach, and would read as a power claim without it) | N31 | `P::We have not compared their power with that of a reconstruction-level test` |
| G1 | descriptive: config (a) central values only; no significance | P33 | KEEP | N32 | `P::no significance is assigned to them` |
| G2 | all four underpredict at low Eavail between QE and Δ (low-recoil region) | P33 | KEEP | N32 | `P::between the quasielastic and $\Delta$ peaks` |
| G3 | FSI, Valencia 2p2h and published comparisons in note | P33 | KEEP (numbered pointer) | N32 | `P::Secs.~\ref*{N-sec:3d-2p2h} and~\ref*{N-sec:4d}` |
| G4 | vs Tune v1: two thirds of positive difference at Eavail≥0.8, most at W≥1.8; a fifth in widest overflow cell | P34 | KEEP | N33 | `P::two thirds of the cell-integrated positive difference` && `P::a fifth of it sits in the single widest overflow cell` |
| G5 | ratio 12–30% in those cells, 23–31% at W<1.1 for every Eavail; extends to low W | P34 | KEEP | N33 | `P::\SIrange{\figTwoHiHiLo}{\figTwoHiHiHi}{\percent}` && `P::\SIrange{\figTwoLowWLo}{\figTwoLowWHi}{\percent}` && `P::also extends to low $W$` |
| G6 | data above all four externals overall (1.07–1.39) and at high W | P35 | KEEP | N34 | `P::$\genRatioTotLo$--$\genRatioTotHi$` |
| G7 | GiBUU most deficient, stops ~20 GeV; NuWro/GiBUU ratios contain the target difference | P35 | KEEP | N34 | `P::GiBUU, the most deficient, stops at $E_\nu\approx\SI{20}{GeV}$` |
| G8 | no mismodelled-response closure for the map | P35 | KEEP (consequential for N34's "therefore") | N34 | `P::no closure test with a mismodelled detector response has been run for the Tune~v1 map` |
| G9 | high-Eavail high-W is where regularization bias is largest | P35 | KEEP | N34 | `P::regularization bias of Sec.~\ref{sec:validation} is largest` |
| G10 | map describes where the central value differs from Tune v1; no mechanism | P35 | KEEP | N34 | `P::it does not locate an interaction mechanism` |
| H1 | H0(G): five predictions; equals G on every fine cell; below: Tune v1 composition varied by universes with fine-cell integrals fixed; Tune v1 background with bands | P36 | KEEP | N35 | `P::with every fine-cell integral held fixed` && `P::the background is the Tune~v1 simulation's, with its uncertainty bands` |
| H2 | the hybrid null is what the calibration simulates; tested in total and shape on supported cells | P36 | KEEP | N35 | `P::We call this hypothesis the hybrid null` && `P::tested in total and in shape` |
| H3 | three distinct requirements (exact on grid; physical representation needs composition and convergence; calibration fidelity) | P36 | KEEP (r13: "requirements" → "properties", review NIT 5; three sentences) | N35 | `P::Three properties are distinct` && `P::Calibration fidelity is whether the calibration reproduces the analysis of the data` |
| H4 | pseudo-experiment: halves; source reweighted to G with nuisances; per-fine-cell renormalized bands move composition, efficiency, migrations; lateral ΣzΔ from data endpoints | P37 | KEEP | N36 | `P::$\sum_{b}z_{b}\Delta_{b}$, with $\Delta_{b}$ from endpoint unfoldings of the data` && `P::and with it the efficiency and the migrations` |
| H5 | Poisson pseudo-data and background; unfold with other half; 1.4% norm, rounding noise, prediction residual added | P37 | KEEP | N36 | `P::the data's rounding noise, and the prediction's finite-sample residual are then added` |
| H6 | data unfolded once with the full simulation | P37 | KEEP | N36 | `P::The data are unfolded once, with the full simulation` |
| H7 | nulls conditional on data-derived inputs | P37 | KEEP | N36 | `P::the null distributions are conditional on these data-derived inputs` |
| H8 | which would differ in a repeated experiment | P37 | MOVE→note §10.2 sec:joint5d-calibration, Y | — | `N:sec_joint.tex::which would differ in a repeated experiment` |
| H9 | that conditioning has not been validated | P37 | KEEP (moved within the paper to the calibration-fidelity paragraph) | N48 | `P::conditioning on the data-derived lateral shifts has not been validated` |
| H10 | element-by-element model and flowchart in the note | P37 | KEEP (numbered pointer) | N36 | `P::inputs (\nsec{sec:joint5d-calibration})` |
| H11 | total statistic T_tot = rᵀΣ⁻¹r; "total (rate-and-shape) test" | P38 | KEEP | N37 | `P::total (rate-and-shape) test` |
| H12 | shape statistic on normalized fractions, one cell dropped | P38 | KEEP | N37 | `P::uses the normalized cell fractions, with one cell dropped` |
| H13 | Σ = V + diag Var(μG); V Ledoit–Wolf of 194 pilot pseudo-experiments; shrinkage floors ~80 of 109 directions | P38 | KEEP | N37 | `P::\jtVn{} pilot pseudo-experiments` && `P::floors about 80 of the 109 nearly degenerate correlation directions` |
| H14 | metric sets power; calibration sets size | P38 | KEEP | N37 | `P::the null calibration determines its size` |
| H15 | p = (k+1)/(B+1), never zero | P39 | KEEP | N38 | `P::$(k+1)/(B+1)$, where $k$ of $B$ null pseudo-experiments reach the observed statistic; it is never zero` |
| H16 | largest p over shifted nulls: 0, D/2, D (simulation-size bound), ±2δ_fine (last refinement step) | P39 | KEEP | N38 | `P::zero, half, or all of an upper bound $D$` && `P::is the change of the noise-free unfolded result in the last step of a refinement of the null truth's grid` |
| H17 | the shifted set was fixed in advance | P39 | MOVE→note §10.2 ("declared variants"), Y | — | `N:sec_joint.tex::is the largest over declared variants` |
| H18 | Holm at α=0.05; sequential sampling to ≤1999 per null | P40 | KEEP | N39 | `P::Holm procedure~\cite{Holm:1979}, with pseudo-experiments drawn sequentially, to at most \jtBcap{} per null` |
| H20 | reject iff upper end of two-sided 95% CP interval < Holm threshold | P41 | KEEP | N39 | `P::upper end of the two-sided 95\% Clopper--Pearson interval` |
| H21 | under A1 (tail probability uniform or conservative) and A2 (exceedances independent given data), meeting the criterion has probability below threshold at any B ≤ 1999, for any stopping rule | P41 | KEEP | N39 | `P::uniformly distributed or conservative (A1)` && `P::independent given the data (A2)` && `P::whatever rule determines when sampling stops` |
| H22 | including the budget extensions | P41 | KEEP (moved within the paper to the design sentence); r13: reworded (review NIT) | N40 | `P::the error control above is unaffected by this, because it holds for any stopping rule` |
| H23 | therefore FWER of the ten decisions at 5% under the stated assumptions | P41 | KEEP (guardrail: "Under them") | N39 | `P::Under them, the probability of meeting the criterion` && `P::controls the familywise error rate of the ten decisions at 5\%` |
| H24 | from A1, A2 alone the bound is 0.8902α < 0.9α | P41 | MOVE→note §10.3 and App. B.5 sec:joint5d-fwer, Y | — | `N:sec_joint.tex::$\mathrm{FWER}\le0.8902\,\alpha<0.9\,\alpha$` |
| H25 | derivation in the note's appendix | P41 | KEEP (numbered: App. B.5) | N39 | `P::(\napp{sec:joint5d-fwer})` |
| H26 | point estimates (k+1)/(B+1) carry no separate validity claim | P41 | KEEP | N39 | `P::carry no separate validity claim` |
| H27 | time limits interrupted/prevented 224 calibration and 53 power pseudo-experiments | P42 | KEEP; r13: reworded | N40 | `P::(\jtLostCal{} for calibration, \jtLostPow{} for power) were rerun` |
| H28 | A2 requires losses independent of outcomes, not shown | P42 | MOVE→note §10.3 sec:joint5d-frozen, Y (its effect, H29, stays) | — | `N:sec_joint.tex::A2 requires the lost pseudo-experiments to have been lost independently of their outcomes, which has not been shown` |
| H29 | all rerun; none reaches observed statistic in any test or shifted null; no assignment changes a decision | P42 | KEEP; r13: reworded | N40 | `P::were rerun; none reaches the observed statistic in any test or shifted null, so no assignment of the lost outcomes changes any decision` |
| H30 | the rerun followed a procedure fixed in advance | P42 | MOVE→note §10.6 sec:joint5d-lost, Y | — | `N:sec_joint.tex::under a procedure fixed and independently reviewed beforehand` |
| H31 | A1 (fidelity) discussed under (i), (iv), simulation-size dependence checked | P42 | KEEP (restated in the fidelity paragraph) | N48 | `P::which is assumption A1` && `P::The simulation-size check of condition~(iv)` |
| H32 | size averaged over nuisance priors; at fixed nuisance values can exceed α | P42 | KEEP (guardrail: the FWER sentence H23 is false as read at fixed nuisances without it) | N39 | `P::at a fixed true value of the nuisance parameters it can exceed $\alpha$` |
| H33 | design (hypotheses, statistics, shifts, multiplicity, stopping, inputs) fixed before any pseudo-experiment or observed statistic | P43 | KEEP (shortened: "before any observed statistic") | N40 | `P::The test design was fixed before any observed statistic was computed` |
| H34 | …before the first pseudo-experiment of the calibration and power ensembles | P43 | MOVE→note §10.3, Y | — | `N:sec_joint.tex::frozen before any production pseudo-experiment or observed statistic` |
| H35 | independent recomputation with separate code agrees | P43 | KEEP | N40 | `P::Independently written code reproduces every $p$ value and decision` |
| H36 | "some choices were made after results had been seen" (header) | P44 | COLLAPSED→B12, H37, H38; r13: reworded | N15, N40 | `P::its reviewers had already seen descriptive per-cell residuals` |
| H37 | design reviewed before fixed by people who had seen descriptive per-cell residuals | P44 | KEEP (consequential for the FWER statement; one clause); r13: reworded | N40 | `P::was fixed before any observed statistic was computed, although its reviewers had already seen descriptive per-cell residuals of the data` |
| H38 | budget extension decided while observed p values visible | P44 | KEEP (one clause); r13: reworded | N40 | `P::The calibration's computing budget was later extended by a bounded amount with observed $p$ values visible` |
| H39 | the extension changed no statistic, shift, threshold or stopping rule | P44 | MOVE→note §10.3, Y | — | `N:sec_joint.tex::No statistic, variant, threshold or stopping rule was changed` |
| H40 | κ scan, rerun and projection comparison ran after the decisions, outside the rule, to prior specifications; projection specified after 5D outcomes known | P44 | MOVE→note §10.3, Y ("outside the decision rule" kept at R5) | — | `N:sec_joint.tex::Three studies ran after the decisions and are not part of the decision rule` && `N:sec_joint.tex::specified after the five-dimensional outcomes were known` |
| H41 | GENIE CV non-rejection in muon projection is post hoc | P44, P47 | KEEP in condition (ii) (restored, review S1) + note §10.3, §10.7, Y; r13: reworded | N43 | `P::in shape, a post hoc observation)` && `N:sec_joint.tex::projection is a post hoc observation` |
| H42 | six conditions numbered as in the note | P45 | KEEP; r13: reworded | N41 | `P::rest on six conditions on the nuisance model, numbered as in \nsec{sec:joint5d-conditions}` |
| H43 | (i) Tune v1 composition below grid; convergence not shown; last step 0.50–0.86 of whole change; residual unmeasured, potentially material | P46 | KEEP; r13: reworded | N42 | `P::Convergence of the fine grid has not been shown` && `P::\jtMoneMin--\jtMoneMax{} of the whole change` && `P::unmeasured and potentially material` |
| H44 | shifts set (before any result) by assuming geometric shrinkage | P46 | KEEP ("before any result" → note, Y) | N42 | `P::were set by assuming that the refinement steps shrink geometrically` && `N:sec_joint.tex::Measured before any observed statistic` |
| H45 | the rate came from the design review, which did not document its calculation | P46 | MOVE→note §10.4 sec:joint5d-conditions, Y | — | `N:sec_joint.tex::a design-review value whose calculation is not recorded` |
| H46 | measured L2 ratios allow slower convergence | P46 | KEEP | N42 | `P::the measured $L_{2}$ ratios also allow slower convergence` |
| H47 | carry-over to G only if sub-grid shape replacement moves result ≤ ±2δ along δ | P46 | KEEP (guardrail: the rejections are of the hybrid null otherwise) | N42 | `P::carry over from the simulated hybrid null to $G$ itself only if` |
| H48 | (ii) detector model varied by drawn bands and lateral surrogate | P47 | KEEP | N43 | `P::varied only by the drawn detector bands and a linear surrogate for the lateral bands` |
| H49 | surrogate checked only for endpoint symmetry | P47 | MOVE→note §10.4, Y | — | `N:sec_joint.tex::checked only for the symmetry of its endpoints` |
| H50 | no calorimetric hadronic-response band; test-beam derived; 10% at highest q3 of low-recoil | P47 | KEEP | N43 | `P::It has no band for the calorimetric hadronic-energy response` && `P::rises to \SI{10}{\percent}` |
| H51 | mismodelling moves statistics either way; band would broaden/shift nulls; net effect unmeasured | P47 | KEEP | N43 | `P::the net effect on each $p$ value has not been measured` |
| H52 | matched (pT,p∥) projection does not reject GENIE CV (p = 0.48 total, 0.63 shape): hadronic axes involved | P47 | KEEP; r13: reworded | N43 | `P::($p=\woneGcvPtTot$ in total and $\woneGcvPtShape$ in shape, a post hoc observation)` && `P::involves the hadronic axes, on which a response band would act` |
| H53 | exploratory ±4% recoil scaling (test-beam level, 0.35–2.0 GeV/c): every rejection stays vs original nulls; statistics move ≤ ~11% | P48 | KEEP (guardrail: "against the original null distributions") | N44 | `P::In an exploratory sensitivity study` && `P::leaves every rejection in place against the original null distributions` && `P::up to about \SI{11}{\percent}` |
| H54 | nulls not regenerated | P48 | KEEP (restated) | N44 | `P::the study regenerates no null distribution` |
| H55 | neutrons and higher-momentum hadrons outside test-beam sample | P48 | KEEP | N44 | `P::higher-momentum hadrons, which matter at high $W$, lie outside the test-beam sample` |
| H56 | untested: species, energy-dependent, resolution effects, pre-calibration difference, larger variations | P48 | KEEP (summarized: "no other form or size") + detail MOVE→note §10.8 sec:joint5d-response, Y | N44 | `P::tests no other form or size of response change` && `N:sec_joint.tex::particle-species, energy-dependent or resolution effects, and a response difference applied before calibration` |
| H57 | rejections conditional on the simulation's hadronic response | P48 | KEEP | N44 | `P::remain conditional on the simulation's hadronic response` |
| H58 | (iii) 34-band prior, two bands clipped | P49 | KEEP | N45 | `P::\jtModelBands-band set, with negative weights of two bands clipped` |
| H59 | (iv) half vs full simulation; shift ≤ ~0.07 null SD; enters as D | P50 | KEEP; r13: reworded | N46 | `P::at most about 0.07 null standard deviations and measured for the mean only` && `P::enters as the upper-bound shift $D$` |
| H60 | …not always consistent with zero | P50 | MOVE→note §10.4, Y | — | `N:sec_joint.tex::not always consistent with zero, enters as` |
| H61 | measured for the mean only, without noise or nuisance draws | P50 | KEEP (restored, review S3) + note §10.4, Y; r13: reworded | N46 | `P::measured for the mean only, without noise or nuisance draws` && `N:sec_joint.tex::That shift was measured for the mean only, in a process without noise or nuisance draws` |
| H62 | quarter-simulation repeat: no change resolved; conservative extrapolation: all ten rejected | P50 | KEEP | N46 | `P::with a quarter of the simulation resolved no change of the null distributions` && `P::conservative by design all ten decisions remain rejected` |
| H63 | check concerns size only, not the data process | P50 | KEEP (moved within the paper) | N48 | `P::is not a test of the data process` |
| H64 | every pseudo-experiment resamples the same events: nulls conditional on the simulation | P50 | KEEP (moved within the paper) | N48 | `P::every pseudo-experiment resamples the same simulated events, so the null distributions are conditional on that simulation` |
| H65 | closest decisions exceed their boundary by 1.11 and 1.30 null SD; all margins in note | P50 | KEEP | N46 | `P::by 1.11 and 1.30 null standard deviations` |
| H66 | (v) GiBUU lacks Eν>20 GeV; out-of-domain truth migrates in | P51 | KEEP | N47 | `P::its out-of-domain truth enters the migrations into its domain` |
| H67 | (vi) predictions' finite samples in metric and residuals | P51 | KEEP | N47 | `P::The predictions' own finite samples enter the metric and the simulated residuals` |
| H68 | calibration valid to the extent the chain reproduces the data analysis | P52 | KEEP | N48 | `P::to the extent that the pseudo-experiment chain reproduces the analysis applied to the data` |
| H69 | recomputation verifies the calculation, not the chain | P52 | KEEP | N48 | `P::verifies the calculation, not whether the chain reproduces the data analysis` |
| H70 | no rejection rate for null pseudo-data processed like data; needs an independent sample | P52 | KEEP | N48 | `P::no rejection rate has been measured for null pseudo-data processed like the data, which would require an independent simulation sample` |
| R1 | ten decisions in Table; all rejected at α=0.05 | P53 | KEEP | N49 | `P::Every test is rejected at familywise $\alpha=\jtAlpha$` |
| R2 | NuWro, GiBUU on carbon; CH correction moves both toward data; NuWro total not robust | P53 | KEEP | N49 | `P::NuWro and GiBUU were generated on carbon` && `P::rejection does not survive that correction robustly` |
| R3 | GiBUU H DIS events do not conserve energy (cause unknown), may lower Eavail in the replay, possibly affects its carbon prediction | P53 | KEEP as a clause (restored, review S4); cause and Eavail detail in note §10.9, Y; r13: reworded | N49 | `P::GiBUU's deep-inelastic events on hydrogen do not conserve energy, which affects its correction and possibly its carbon prediction` && `N:sec_joint.tex::do not conserve energy` && `N:sec_joint.tex::It may also affect GiBUU's carbon prediction` |
| R4 | replays are descriptive and do not re-grade the recorded decisions (re-review R1) | P53 | KEEP (guardrail, r12 re-review R1; r13 review SHOULD-FIX 1: "do not re-grade … stand" restored, matching note §10.9) | N49 | `P::These target-corrected evaluations are descriptive and do not re-grade the decisions of Table~\ref{tab:joint}, which concern each prediction on the target it was generated for and stand` && `N:sec_joint.tex::They are descriptive: they do not re-grade the recorded decisions of Table~\ref{tab:joint5d}, which stand` |
| R5 | κ scan, outside the decision rule: all ten determined up to ~5.2 | P53 | KEEP | N49 | `P::As a sensitivity check outside the decision rule` && `P::a multiplier of about 5.2` |
| R6 | scan tests one direction; bounds neither residual nor convergence | P53 | KEEP (guardrail: R5 would read as a robustness bound) | N49 | `P::bounds neither the actual residual nor the convergence` |
| R7 | nulls (shown in note) differ in location: Tune v1 small; externals displaced upward by the pull toward the prior, reproduced by the calibration | P53 | KEEP | N49 | `P::the external nulls are displaced far upward by the estimator's pull toward its prior, which the calibration reproduces` |
| TJ | Table of decisions: B, k, p, Holm thresholds, CP intervals; 1400/1800 submitted | T-III | KEEP (unchanged; now Table IV) | T-IV | `P::$[0.0000145, 0.00318]$` && `P::of 1400 submitted per null (1800 for NuWro)` |
| R8 | contribution: calibration within the simulation model with bias and nuisances in each null; disagreements already established by the published 2D | P54 | KEEP | N50 | `P::The methodological contribution of these comparisons is a calibration` && `P::the disagreements they recover were already established` |
| R9 | matched 3×3 projections: p<0.05 for every test in at least one; no evidence of added discrimination | P54 | KEEP | N50 | `P::for every test in at least one of the two projections, so this study provides no evidence of additional discrimination` |
| R10 | its criterion fixed before it ran | P54 | MOVE→note §10.7 sec:joint5d-projections, Y | — | `N:sec_joint.tex::The criterion, fixed before the run` |
| R11 | each projected p used at 0.05 without multiplicity correction | P54 | KEEP | N50 | `P::gives $p<0.05$, without a multiplicity correction` |
| R12 | power of joint and projected tests not compared | P54 | ADDED-to-note sec_joint.tex:580 (§10.7) | — | `N:sec_joint.tex::The powers of the joint and projected tests have not been compared` |
| R13 | ensembles and independent reproduction in note | P54 | KEEP (numbered pointer); printed in note §10.7, Y | N50 | `P::(\nsec{sec:joint5d-projections})` && `N:sec_joint.tex::its $p$ values were reproduced independently` |
| R14 | rejections are global; region/mechanism needs separate tests | P54 | KEEP | N50 | `P::would require separate tests` |
| R15 | power: Tune v1 null, two of three alternatives 1.0 at 0.005, MEC-like 0.23; GENIE null 0.74, 0.02, 0.00 | P54 | KEEP ("specified in advance" → "specified"; the note's "declared alternatives", Y) | N50 | `P::two of three specified alternatives are detected in shape with power 1.0 at the 0.005 level` && `P::with 0.23` && `P::0.74, 0.02, and 0.00` && `N:sec_joint.tex::two of the three declared alternatives` |
| R16 | binomial intervals in note | P54 | KEEP (numbered pointer) | N50 | `P::(binomial intervals: \nsec{sec:joint5d-power})` |

## VIII. Discussion and conclusions

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| X1 | within the scope of Sec. I the results are the validation findings (Table I) | P55 | KEEP; r13: reworded | N51 | `P::The study's results are the validation findings summarized in Table~\ref{tab:findings}, within the scope stated in Sec.~\ref{sec:intro}` |
| X2 | 2D depends on learner at ~1 unit of χ²/ndf; stat block no coverage test | P55 | KEEP | N51 | `P::at the level of one unit of $\chi^{2}/\mathrm{ndf}$` && `P::its quoted statistical block has had no coverage test` |
| X3 | higher-D central values keep purity subtraction and its ≤4% bias at high W; intervals not validated | P55 | KEEP (r13: "keep" → "use") | N51 | `P::use the purity-based subtraction, with its bias of up to \SI{4}{\percent}` |
| X4 | Sec. VI relates three results to the retained prior | P55 | KEEP (the only reference to Sec. VI kept here) | N51 | `P::relates three of these results to the unfolded result retaining part of its prior` |
| X5 | tests illustrate inference with a biased estimator; FWER 5% provided calibration exact; physical interpretation needs a response band and a sub-grid bound | P56 | KEEP (guardrail: "provided the calibration is exact") | N52 | `P::controls the familywise error rate at 5\% provided the calibration is exact` && `P::a demonstrated bound on the residual below the fine grid` |
| X6–X9 | "Why unfold before testing" | P57 | KEEP, moved to Sec. VII opening (rows X6–X9 above) | N31 | `P::We have not compared their power with that of a reconstruction-level test` |

## Additions to the note (all four)

| id | text added | file:line (note section) | reason |
|---|---|---|---|
| ADD-1 | "The nearly degenerate correlation directions of the joint-test metric (§10.1) are consistent with this redundancy, but that origin has not been shown, and the information added by W has not been measured." | sec_eavailw.tex:136–139 (§8.2) | D26, D27 left the paper; not printed in the note |
| ADD-2 | "The 74% residual is in the cell 0.8≤Eavail<1.5 GeV, W≥3 GeV, whose share of the cross section the deformation study did not record." | sec_5d.tex:118–120 (§9.2) | V12 left the paper; the note named neither the cell nor the unrecorded share |
| ADD-3 | "For the joint-test estimator, a rule fixed before the comparison would have replaced its five iterations by 10, 15, or 20 only if they reduced the model dependence; none did, so five were kept." | sec_5d.tex:308–310 (§9.4) | M19 left the paper; the note did not print the rule |
| ADD-4 | "The powers of the joint and projected tests have not been compared." | sec_joint.tex:580 (§10.7) | R12 left the paper; the note did not print it |
| ADD-5 | "(4.4% and 6.6% after 200 iterations, …)" for W3 and the q3 stress | sec_5d.tex:185–186 (§9.3) | review S6: Table III's 200-iteration entries, verified in d-id/REPORT.md |

## Rows added for the review fixes (REVIEW.md, 2026-10-21)

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| RV-P1 | pointer for the moved 3D/4D no-threshold fact (S5) | P22 | KEEP pointer | N20 | `P::(closure studies: \nsec{sec:closure-map})` |
| RV-P2 | pointer for the exact-split seed spread and LightGBM replacement (S5) | P17 | KEEP pointer | N15 | `P::(both learners: \nsec{sec:method-config})` |
| RV-P3 | central values not recomputed with the refinement, with pointer (S5) | P15 | MOVE→note §3.2 sec:method-config, Y (r13: the paper states what the central values are, configuration (a) with the purity-based subtraction, M11; the pointer now sits on the configuration, review NIT 2) | N13 | `N:sec_method.tex::and they were not regenerated` && `P::the central-value estimator (\nsec{sec:method-config})` |
| RV-P4 | pointer for the 74% cell's unrecorded share (S5) | P23 | KEEP pointer | N21 | `P::$W\ge\SI{3}{GeV}$; \nsec{sec:val-negweight})` && `N:sec_5d.tex::whose share of the cross section the deformation study did not record` |
| RV-P5 | pointer for the iteration rule (S5, B2) | P15 | KEEP pointer | N13 | `P::(\nsec{sec:gbdt-model-dependence}).` |
| RV-T3 | Table III 200-iteration medians W3 4.4%, q3 6.6% (S6), verified in d-id/REPORT.md "Longer exact iteration" table (J median of abs r_IBU at K = 200, nominal-weighted T2, same quantity, population and iteration count as the 3.3% entries) | — | NEW-paper and ADDED-to-note sec_5d.tex:185–186 (§9.3) | T-III | `P::& 4.4 & 8.9` && `N:sec_5d.tex::\SI{4.4}{\percent} and \SI{6.6}{\percent} after 200 iterations` |
| RV-T3b | W2's boosted-tree comparator includes background; counts unchanged without it (N5) | — | KEEP (guardrail: the caption's "signal-only" would be false as read of the pooled counts without it; r13: "a fifth change") | T-III | `P::whose boosted-tree comparator includes background; they are unchanged without it` && `N:sec_5d.tex::whose boosted-tree comparator includes background and without which` |
