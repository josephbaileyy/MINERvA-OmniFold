# Fact ledger: paper_body.tex at b70156a1

**Source:** `docs/analysis-note/paper_body.tex` at commit b70156a1 (worktree `wt-con`), read-only. The driver
`main_paper.tex` is out of scope except for the PROTECTED table at the end.

**What this is.** Every fact the paper body states, so that a writer who never sees the prose can restate all of it.
Each row is one fact. `atoms` are the exact source strings (printed form: comments removed, whitespace collapsed)
that must print again for the fact to be stated; several are joined by ` && `. Numbers are macros: print the macro
call, never its value. The values are listed at the end for reading only.

**Sentence ids.** `base` is PB<n>, the 0-based index of the sentence in paper_body.tex's printed text, as computed
by `printed` and `sentences` of `docs/orchestration/state/2d-closeout/stageF/methods/note-n4/check_ledger.py`
(imported with `python3 -I -B`). There are 255 base sentences, PB0 to PB254. A base sentence often begins with a heading, a label or the end of a float; the split is mechanical. `base text` is the first 60 characters of the base
sentence. PROTECTED rows use MP<n>, the same split applied to main_paper.tex.

**Status.**
- **KEEP**: a qualifier whose removal would make the sentence false. Keep the qualifier with the claim it qualifies.
- **HONESTY**: a disclosure or limitation. It must still be stated, next to the result it qualifies.
- **GATE**: a phrase that `docs/analysis-note/check_sec4_receipts.py` finds by regex in paper_body.tex and checks
  against a receipt. It must print **exactly** as quoted, **exactly once**. The eight bound phrases, quoted in full:
  1. `with a median statistical uncertainty of \SI{0.676}{\percent}`
  2. `biased by up to \SI{4}{\percent} in simulation`
  3. `reduces it to below \SI{0.3}{\percent}`
  4. `leaving up to \SI{1}{\percent} in some joint cells`
  5. `differ by at most \SI{1.4}{\percent}`
  6. `by up to \SI{74}{\percent} at high $W$`
  7. `it is \SIrange{16}{31}{\percent} in the most affected`
  8. `within the quoted total uncertainty in about half of those cells` (the VERBAL check)

  The same script also checks `\uqMedian`, `\uqIntegral`, `\covTwoDNtoy`, `\covTwoDCTwo` and `\covTwoDCOne` in
  values.tex, and two phrases in the note's sec_validation.tex. The rewrite does not touch those.
- **FROZEN**: `Interval coverage has not been validated.` must print verbatim. It is also `KEEP_SENTENCE` in
  `stageF/methods/paper-protections/check_ledger.py` (check 5).
- **STRUCTURE**: headings, labels, float environments, graphics, macro definitions, and the four tables' contents.
  The writer copies tables and figures verbatim. Every `\label` must survive (paper-protections check 3).
- **ORDINARY**: any other fact: a number, a definition, a citation or a pointer.
- **PROTECTED**: text in main_paper.tex that stays byte-identical.
- **PLANTED**: the deliberately false row FX. The downstream checker must reject it.

**Constraints outside this ledger that a rewrite will meet** (found while building it; not facts of the paper):
- `docs/orchestration/registry/ALIASES.tsv:38` and `ATTRIBUTION.tsv:17` cite `paper_body.tex` line 72 ("the
  joint-test estimator, a deterministic LightGBM", digest `504c9c374d42e800`), and `ALIASES.tsv:47` cites line 86
  ("negative weights; refinement 400 trees, 31 leaves", digest `34f71afb108bc778`), each by line number and digest.
  A rewrite that moves these lines breaks those citations unless the registry is updated.
- `paper-protections/check_ledger.py` check 6 fails any *added* sentence that contains a numeral typed by hand
  (only `\fvval` and the value macros are exempt; numbers inside `\SI{..}` arguments escape its regex, but
  `$4.12$`, `20 pseudo-experiments` and `10--13\%` do not). Many facts below carry literal numerals. A reworded
  sentence that keeps one fails that check unless the check is waived or the number becomes a macro.
- The paper-protections ledger probes several body strings verbatim (the rows say "probed verbatim"). Rewording them
  fails those probes.

## I. Introduction (`sec:intro`)

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F001 | I | Preamble macro definitions that open the body file: a fixed-width table cell, and the two pointer macros into the companion note (they print "Ref. [note], Sec./App. N") | `\newcommand{\pcell}[2]{\parbox[t]{#1}{\raggedright\strut#2\strut}}` && `\newcommand{\nsec}[1]{Ref.~\cite{AnalysisNote2026}, Sec.~\ref*{N-#1}}` && `\newcommand{\napp}[1]{Ref.~\cite{AnalysisNote2026}, App.~\ref*{N-#1}}` | PB0 | STRUCTURE | `\newcommand{\pcell}[2]{\parbox[t]{#1}{\raggedright\strut#2\s` |
| F002 | I | Section heading and label | `\section{Introduction}` && `\label{sec:intro}` | PB0 | STRUCTURE | `\newcommand{\pcell}[2]{\parbox[t]{#1}{\raggedright\strut#2\s` |
| F003 | I | Multidifferential neutrino cross sections test interaction models across muon and hadronic observables | `Multidifferential neutrino cross sections` && `test interaction models` && `muon and hadronic observables` | PB0 | ORDINARY | `\newcommand{\pcell}[2]{\parbox[t]{#1}{\raggedright\strut#2\s` |
| F004 | I | Their interpretation depends on correcting for detector response and on assessing the unfolding's bias and uncertainty | `correcting detector response` && `bias and uncertainty of the unfolding procedure` | PB1 | ORDINARY | `Their interpretation depends on correcting detector response` |
| F005 | I | Iterative Bayesian unfolding on a binned migration matrix is widely used; its response tensor grows rapidly as observables are added | `Iterative Bayesian unfolding` && `binned migration matrix` && `\cite{DAgostini:1994fjx}` && `response tensor grows rapidly` | PB2 | ORDINARY | `Iterative Bayesian unfolding on a binned migration matrix~\c` |
| F006 | I | OmniFold learns event weights in an unbinned feature space by classifier-based density-ratio estimation | `OmniFold learns event weights in an unbinned feature space` && `classifier-based density-ratio estimation` && `\cite{Andreassen:2019cjw,Andreassen:2021zzk}` | PB3 | ORDINARY | `OmniFold learns event weights in an unbinned feature space t` |
| F007 | I | This allows simultaneous higher-dimensional unfolding without a separate binned response tensor for each projection | `simultaneous higher-dimensional unfolding` && `without specifying a separate binned response tensor for every projection` | PB4 | ORDINARY | `This makes simultaneous higher-dimensional unfolding possibl` |
| F008 | I | Unbinned unfolding on collider data: eight observables in DIS at H1 | `collider data` && `eight observables in deep-inelastic scattering at H1~\cite{H1:2021wkz}` | PB5 | ORDINARY | `Unbinned unfolding has been applied to collider data, for ex` |
| F009 | I | Unbinned unfolding on collider data: twenty-four Z+jets observables at ATLAS | `twenty-four $Z$+jets observables at ATLAS~\cite{ATLAS:2024jets}` | PB5 | ORDINARY | `Unbinned unfolding has been applied to collider data, for ex` |
| F010 | I | A survey of unbinned unfolding is cited | `\cite{Canelli:2025guide} for a survey` | PB5 | ORDINARY | `Unbinned unfolding has been applied to collider data, for ex` |
| F011 | I | In neutrino physics it has been demonstrated only on a public simulated T2K near-detector sample (simulated, not data) | `demonstrated` && `public simulated T2K near-detector sample~\cite{Huang:2025omnifold}` | PB6 | KEEP | `In neutrino physics it has been demonstrated on a public sim` |
| F012 | I | Multidifferential neutrino measurements on data reach three dimensions (four cited measurements) | `Multidifferential neutrino measurements on data reach three dimensions` && `\cite{MINERvA:2022qelike3d,MINERvA:2026qeleme,MicroBooNE:2023inc3d,NOvA:2026inc3d}` | PB7 | KEEP | `Multidifferential neutrino measurements on data reach three ` |
| F013 | I | The method is applied to MINERvA medium-energy muon-neutrino data from the open-data release | `MINERvA medium-energy $\nu_{\mu}$ data` && `open-data release~\cite{MINERvA:OpenData}` | PB8 | ORDINARY | `We apply the method to MINERvA medium-energy $\nu_{\mu}$ dat` |
| F014 | I | The result: a simultaneous CC inclusive cross section in five observables (pT, ppar, Eavail, q3, W), each defined by name | `simultaneous charged-current inclusive cross section in five observables` && `transverse and longitudinal muon momenta $\pT$ and $\pPar$` && `available hadronic energy $\Eavail$` && `three-momentum transfer $q_{3}$` && `hadronic invariant mass $W$` | PB9 | ORDINARY | `The result is a simultaneous charged-current inclusive cross` |
| F015 | I | It is reported in sixteen cells with its covariance (pointer to the result section) | `reported in sixteen cells with its covariance (Sec.~\ref{sec:result16})` | PB9 | ORDINARY | `The result is a simultaneous charged-current inclusive cross` |
| F016 | I | It is compared with five generator predictions (pointer) | `compared with five generator predictions (Sec.~\ref{sec:gen16})` | PB9 | ORDINARY | `The result is a simultaneous charged-current inclusive cross` |
| F017 | I | The published double-differential cross section in pT and ppar is first reproduced, as an end-to-end test of the unfolding | `reproduce the published double-differential cross section` && `$d^{2}\sigma/(d\pT\,d\pPar)$~\cite{MINERvA:2021owq}` && `end-to-end test of the unfolding` | PB10 | ORDINARY | `We first reproduce the published double-differential cross s` |
| F018 | I | Three- and four-observable results are given as central values (only) | `three- and four-observable central values` | PB10 | KEEP | `We first reproduce the published double-differential cross s` |
| F019 | I | Reconstructed W is fixed by reconstructed (pT, ppar, q3), so the five observables are simultaneous but not independent | `Reconstructed $W$ is fixed by the reconstructed $(\pT,\pPar,q_{3})$` && `simultaneous but not independent` | PB11 | KEEP | `Reconstructed $W$ is fixed by the reconstructed $(\pT,\pPar,` |
| F020 | I | The validation studies: the 2D reproduction, background-subtraction tests, recovery of generator-sized truth changes, a coverage test, a fake-data study of estimator bias | `two-dimensional reproduction` && `background-subtraction tests` && `recovery of generator-sized truth changes` && `a coverage test` && `fake-data study of estimator bias` | PB12 | ORDINARY | `The validation studies assess the result through the two-dim` |
| F021 | I | They examine whether the unfolding gives reliable multidimensional cross sections when the simulation mismodels the truth by generator-sized amounts | `reliable multidimensional cross sections` && `mismodels the truth by generator-sized amounts` | PB13 | ORDINARY | `They examine whether the unfolding gives reliable multidimen` |
| F022 | I | Definition: coverage of unfolded intervals is the rate at which they contain the true cross section | `coverage of unfolded intervals is the rate at which they contain the true cross section` | PB14 | ORDINARY | `The coverage of unfolded intervals is the rate at which they` |
| F023 | I | Interval coverage has not been validated (frozen sentence; also the KEEP_SENTENCE of paper-protections/check_ledger.py) | `Interval coverage has not been validated.` | PB15 | FROZEN | `Interval coverage has not been validated.` |
| F024 | I | The bias tests, the fake-data study and the dependence of the generator chi2 on the flux correlations are given with the result (pointers) | `The bias tests, the fake-data study` && `dependence of the generator $\chi^{2}$ on the flux correlations` && `Secs.~\ref{sec:fd16} and~\ref{sec:gen16}` | PB16 | ORDINARY | `The bias tests, the fake-data study and the dependence of th` |
| F025 | I | Scope: the findings are those of one OmniFold implementation on one data set, for the observables, configurations and deformations tested, not of multidimensional OmniFold in general (probed verbatim by the paper-protections ledger) | `\emph{Scope.} The findings are those of one OmniFold implementation on one data set, for the observables, configurations, and deformations tested, rather than of multidimensional OmniFold in general.` | PB17 | KEEP | `\emph{Scope.} The findings are those of one OmniFold impleme` |
| F026 | I | The limitations are listed in the Limitations subsection | `The limitations are listed in Sec.~\ref{sec:limitations}` | PB18 | ORDINARY | `The limitations are listed in Sec.~\ref{sec:limitations}.` |
| F027 | I | Roadmap: data/simulation/observables section; extraction section covers the unfolding and the reporting cells | `Section~\ref{sec:data}` && `data, the simulation and the observables` && `Sec.~\ref{sec:method} the unfolding and the reporting cells` | PB19 | ORDINARY | `Section~\ref{sec:data} describes the data, the simulation an` |
| F028 | I | Roadmap: the validation section runs from the 2D reproduction to the fake-data tests of the sixteen-cell result; the result section gives the result and generator comparison | `Section~\ref{sec:validation} gives the uncertainties and the validation studies` && `reproduction of the published two-dimensional measurement to the fake-data tests of the sixteen-cell result` && `Sec.~\ref{sec:result16} gives the result and its comparison with generator predictions` | PB20 | ORDINARY | `Section~\ref{sec:validation} gives the uncertainties and the` |
| F029 | I | Roadmap: the conclusions discuss what limits the estimator; the Limitations subsection summarizes the principal limitations | `Section~\ref{sec:conclusions} discusses what limits the estimator` && `Sec.~\ref{sec:limitations} summarizes the principal limitations` | PB21 | ORDINARY | `Section~\ref{sec:conclusions} discusses what limits the esti` |
| F030 | I | The companion analysis note gives the full validation record, the construction of the uncertainties and the tests with their assumptions, and is cited by section | `companion analysis note~\cite{AnalysisNote2026}` && `full validation record` && `construction of the uncertainties` && `the tests with their assumptions` && `cited below by section` | PB22 | ORDINARY | `The companion analysis note~\cite{AnalysisNote2026} gives th` |
<!-- absence-ok: quotes printed limitation sentences of the paper as facts to restate; not a claim that a result does not exist -->

## II. Data, simulation, and observables (`sec:data`)

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F031 | II | Section heading and label | `\section{Data, simulation, and observables}` && `\label{sec:data}` | PB23 | STRUCTURE | `\section{Data, simulation, and observables} \label{sec:data}` |
| F032 | II | Data: the twelve MINERvA medium-energy forward-horn-current run periods | `twelve MINERvA medium-energy, forward-horn-current run periods` | PB23 | ORDINARY | `\section{Data, simulation, and observables} \label{sec:data}` |
| F033 | II | Exposure 1.057e21 POT; average neutrino energy near 6 GeV (per the published analysis) | `$1.057\times10^{21}$ protons on target` && `average neutrino energy near \SI{6}{GeV}~\cite{MINERvA:2021owq}` | PB23 | ORDINARY | `\section{Data, simulation, and observables} \label{sec:data}` |
| F034 | II | The input is an earlier production of the open-data release of pre-selected AnaTuples; pointer to Data availability | `earlier production of the MINERvA open-data release` && `pre-selected analysis ntuples (AnaTuples)~\cite{MINERvA:OpenData}` && `(see Data availability)` | PB23 | KEEP | `\section{Data, simulation, and observables} \label{sec:data}` |
| F035 | II | The detector, including the downstream MINOS near detector serving as muon spectrometer, is described in the cited reference | `MINOS near detector` && `muon spectrometer` && `Ref.~\cite{MINERvA:2013zvz}` | PB24 | ORDINARY | `The detector, including the downstream MINOS near detector t` |
| F036 | II | Signal: a muon-neutrino CC interaction with any final state, true vertex in the tracker fiducial volume | `$\nu_{\mu}$ charged-current interaction, with any final state` && `true vertex lies in the tracker fiducial volume` | PB25 | ORDINARY | `The signal is a $\nu_{\mu}$ charged-current interaction, wit` |
| F037 | II | Fiducial volume: 5980 < z < 8422 mm, inside a hexagon of apothem 850 mm | `$5980<z<\SI{8422}{mm}$` && `hexagon of apothem \SI{850}{mm}` | PB25 | ORDINARY | `The signal is a $\nu_{\mu}$ charged-current interaction, wit` |
| F038 | II | Signal muon limits: theta < 20 deg, 1.5 < ppar < 60 GeV/c, pT <= 4.5 GeV/c | `$\theta_{\mu}<20^{\circ}$` && `$1.5<\pPar<\SI{60}{GeV/c}$` && `$\pT\le\SI{4.5}{GeV/c}$` | PB25 | ORDINARY | `The signal is a $\nu_{\mu}$ charged-current interaction, wit` |
| F039 | II | Selected simulated events outside the signal definition, including CC muon-neutrino events whose muon is outside the limits, are background | `Selected simulated events outside this definition` && `muon lies outside these limits, are background` | PB26 | KEEP | `Selected simulated events outside this definition, including` |
| F040 | II | Selection: reconstructed vertex in the same volume; reconstructed muon theta < 20 deg matched to a negative-charge MINOS track; a dead-time requirement; as in the published analysis | `reconstructed vertex in the same volume` && `reconstructed muon with $\theta_{\mu}<20^{\circ}$` && `matched to a MINOS track of negative charge` && `dead-time requirement` && `as in Ref.~\cite{MINERvA:2021owq}` | PB27 | ORDINARY | `The selection requires a reconstructed vertex in the same vo` |
| F041 | II | The flux treatment follows the cited flux paper | `The flux treatment follows Ref.~\cite{MINERvA:2016iqn}` | PB28 | ORDINARY | `The flux treatment follows Ref.~\cite{MINERvA:2016iqn}.` |
| F042 | II | 4.12 million selected data events | `$4.12$ million selected data events` | PB29 | ORDINARY | `After selection, the sample contains $4.12$ million selected` |
| F043 | II | Simulation: 32.8 million unweighted true signal events and 20.5 million selected simulated events | `$32.8$ million unweighted true signal events` && `$20.5$ million selected simulated events` | PB30 | ORDINARY | `The simulation contains $32.8$ million unweighted true signa` |
| F044 | II | The simulation is scaled to the data exposure | `scaled to the data exposure` | PB31 | ORDINARY | `The simulation is scaled to the data exposure.` |
| F045 | II | Simulated events: GENIE 2.12.6 with the MINERvA Tune v1 | `GENIE~2.12.6~\cite{Andreopoulos:2009rq}` && `MINERvA Tune~v1` | PB32 | ORDINARY | `The simulated events are generated with GENIE~2.12.6~\cite{A` |
| F046 | II | Tune v1 reweights GENIE with a non-resonant pion reduction, an RPA correction and an empirical low-recoil 2p2h enhancement (2p2h defined here) | `non-resonant pion reduction` && `random-phase-approximation correction` && `empirical low-recoil two-particle--two-hole (2p2h) enhancement~\cite{MINERvA:2016lowrecoil}` | PB32 | ORDINARY | `The simulated events are generated with GENIE~2.12.6~\cite{A` |
| F047 | II | Event selection is held fixed as classifier inputs and unfolded observables grow from (pT, ppar) to all five | `Event selection is held fixed` && `from $(\pT,\pPar)$ to $(\pT,\pPar,\Eavail,q_3,W)$` | PB33 | KEEP | `Event selection is held fixed as the classifier inputs and u` |
| F048 | II | Adding features adds no selected events and does not relax the signal definition | `does not add selected events or relax the signal definition` | PB34 | KEEP | `Adding features does not add selected events or relax the si` |
| F049 | II | The unfolded observables are defined at truth level | `defined at truth level` | PB35 | KEEP | `The unfolded observables are defined at truth level.` |
| F050 | II | Definitions: pT = p sin(theta), ppar = p cos(theta) | `$\pT=p_{\mu}\sin\theta_{\mu}$` && `$\pPar=p_{\mu}\cos\theta_{\mu}$` | PB36 | ORDINARY | `Besides the muon momentum components $\pT=p_{\mu}\sin\theta_` |
| F051 | II | Definition: q3 is the magnitude of the three-momentum transfer, from the generator's four-vectors | `three-momentum transfer $q_{3}=` && `\vec{q}` && `from the generator's four-vectors` | PB36 | ORDINARY | `Besides the muon momentum components $\pT=p_{\mu}\sin\theta_` |
| F052 | II | Definition: W = sqrt(M^2 + 2M(Enu - Emu) - Q^2), with M the struck-nucleon mass | `$W=\sqrt{M^{2}+2M(E_{\nu}-E_{\mu})-Q^{2}}$` && `struck-nucleon mass $M$` | PB36 | ORDINARY | `Besides the muon momentum components $\pT=p_{\mu}\sin\theta_` |
| F053 | II | Displayed equation defining Eavail (copy verbatim, with its label) | `\Eavail=\sum_{p}(E_{p}-m_{p})+\sum_{\pi^{\pm}}(E_{\pi}-\SI{135}{MeV}) +\sum_{\pi^{0}}E_{\pi}+\sum_{\gamma}E_{\gamma},` && `\label{eq:eavail}` | PB36 | ORDINARY | `Besides the muon momentum components $\pT=p_{\mu}\sin\theta_` |
| F054 | II | The charged-pion term subtracts a defined constant of 135 MeV, not the charged-pion mass | `defined constant of \SI{135}{MeV}, rather than the charged-pion mass, in the charged-pion term` | PB36 | KEEP | `Besides the muon momentum components $\pT=p_{\mu}\sin\theta_` |
| F055 | II | All other final-state particles, including neutrons, contribute nothing to Eavail | `including neutrons, contribute nothing` | PB37 | ORDINARY | `All other final-state particles, including neutrons, contrib` |
| F056 | II | The sums run over generator final-state particles after FSI, with neutral pions undecayed | `after final-state interactions` && `neutral pions appear undecayed` | PB38 | ORDINARY | `The sums run over the generator's final-state particles afte` |
| F057 | II | The 135 MeV constant is inherited from the analysis framework's definition | `inherited from the analysis framework's definition` | PB39 | ORDINARY | `The \SI{135}{MeV} constant is inherited from the analysis fr` |
| F058 | II | It defines the reported observable and is used consistently by the analysis and every prediction | `defines the reported observable` && `used consistently by the analysis and every prediction` | PB40 | KEEP | `It defines the reported observable and is used consistently ` |
| F059 | II | Reconstructed Eavail is 1.17 times the calorimetric recoil energy in the tracker and ECAL, muon deposits removed | `$1.17$ times the calorimetric recoil energy` && `tracker and electromagnetic calorimeter` && `muon deposits removed` | PB41 | ORDINARY | `Reconstructed $\Eavail$ is $1.17$ times the calorimetric rec` |
| F060 | II | Reconstructed q3 and W combine the muon kinematics with a separate calorimetric energy-transfer estimate q0 | `Reconstructed $q_{3}$ and $W$ instead combine the muon kinematics with a separate calorimetric estimate $q_{0}$ of the energy transfer` | PB42 | ORDINARY | `Reconstructed $q_{3}$ and $W$ instead combine the muon kinem` |
| F061 | II | Reconstructed W is an exact function of reconstructed (pT, ppar, q3); the five reconstructed inputs share information and are not five independent constraints | `Reconstructed $W$ is an exact function of the reconstructed $(\pT,\pPar,q_{3})$` && `do not provide five independent constraints` | PB43 | HONESTY | `Reconstructed $W$ is an exact function of the reconstructed ` |
| F062 | II | Why: W_reco^2 = (Mbar + q0)^2 - q3_reco^2 with Mbar an average nucleon mass, and q3_reco increases with q0 at fixed muon kinematics | `$W_{\mathrm{reco}}^{2}=(\bar M+q_{0})^{2}-q_{3,\mathrm{reco}}^{2}$` && `$\bar M$ an average nucleon mass` && `increases with $q_{0}$ at fixed muon kinematics` | PB44 | ORDINARY | `The relation holds because $W_{\mathrm{reco}}^{2}=(\bar M+q_` |
| F063 | II | The relation is exact apart from a clamp at W^2 = 0 | `exact apart from a clamp at $W^{2}=0$` | PB45 | KEEP | `This relation is exact apart from a clamp at $W^{2}=0$.` |
| F064 | II | Only reconstructed W is fixed by the other inputs | `Only reconstructed $W$ is fixed by the other inputs` | PB46 | KEEP | `Only reconstructed $W$ is fixed by the other inputs.` |
| F065 | II | Reconstructed Eavail has its own calorimetric estimator and is not a function of them | `own calorimetric estimator and is not a function of them` | PB47 | ORDINARY | `Reconstructed $\Eavail$ comes from its own calorimetric esti` |
| F066 | II | At truth level the muon angle (hence pT, ppar) is measured from a fixed beam axis, not the true neutrino direction | `At truth level` && `measured from a fixed beam axis rather than from the true neutrino direction` | PB48 | ORDINARY | `At truth level, $\theta_{\mu}$, and with it $\pT$ and $\pPar` |
| F067 | II | Truth W is therefore fixed by (pT, ppar, q3) only up to that event-by-event angle and the choice of M | `only up to that event-by-event angle and the choice of $M$` | PB49 | KEEP | `Truth $W$ is therefore fixed by $(\pT,\pPar,q_{3})$ only up ` |
| F068 | II | Pointer: definitions detailed in the note | `Ref.~\cite{AnalysisNote2026}, Secs.~\ref*{N-sec:eavail-definition} and~\ref*{N-sec:eavailw-definitions}` | PB50 | ORDINARY | `The definitions are detailed in Ref.~\cite{AnalysisNote2026}` |
| F069 | II | External predictions for CH: untuned GENIE 2.12.10 without ("GENIE CV") and with ("GENIE + MEC") the Valencia 2p2h component | `external predictions for CH` && `untuned GENIE~2.12.10` && `GENIE CV` && `GENIE + MEC` && `Valencia 2p2h component~\cite{Nieves:2011pp}` | PB51 | ORDINARY | `The external predictions for CH are the untuned GENIE~2.12.1` |
| F070 | II | Definition: the Valencia component models meson-exchange currents (MEC) | `meson-exchange currents (MEC)` | PB51 | ORDINARY | `The external predictions for CH are the untuned GENIE~2.12.1` |
| F071 | II | Predictions for carbon: NuWro 21.09 and GiBUU 2019 | `predictions for carbon` && `NuWro~21.09~\cite{Golan:2012wx}` && `GiBUU~2019~\cite{Buss:2011mx}` | PB52 | ORDINARY | `The predictions for carbon are NuWro~21.09~\cite{Golan:2012w` |
| F072 | II | All predictions are per nucleon of their own target | `per nucleon of their target` | PB53 | KEEP | `All are per nucleon of their target.` |
| F073 | II | GENIE and NuWro predictions are reweighted exactly, event by event, to the analysis flux | `GENIE and NuWro` && `reweighted exactly, event by event, to the analysis flux` | PB54 | ORDINARY | `The GENIE and NuWro predictions are reweighted exactly, even` |
| F074 | II | The GiBUU sample stops at Enu about 20 GeV | `$E_{\nu}\approx\SI{20}{GeV}$` | PB55 | HONESTY | `The GiBUU sample stops at $E_{\nu}\approx\SI{20}{GeV}$.` |
| F075 | II | The predictions compute W with the neutron mass for every event and measure pT about their own neutrino axis (differences from the analysis definitions) | `$W$ with the neutron mass for every event` && `$\pT$ about their own neutrino axis` | PB56 | HONESTY | `The predictions compute $W$ with the neutron mass for every ` |
| F076 | II | Hydrogen has no QE, 2p2h or coherent CC channel, so per-nucleon normalization does not remove the target difference | `Hydrogen has no quasielastic, 2p2h, or coherent $\nu_{\mu}$ charged-current channel` && `does not remove the difference between the targets` | PB57 | HONESTY | `Hydrogen has no quasielastic, 2p2h, or coherent $\nu_{\mu}$ ` |
| F077 | II | In GENIE's own CH sample, carbon-only per nucleon exceeds CH by 8.3% for W < 1.1 GeV | `In GENIE's own CH sample` && `\SI{8.3}{\percent}` && `$W<\SI{1.1}{GeV}$` | PB58 | ORDINARY | `In GENIE's own CH sample, the carbon-only cross section per ` |
| F078 | II | The NuWro and GiBUU comparisons contain such a target difference, which the sixteen-cell comparison does not correct | `NuWro and GiBUU comparisons contain a target difference` && `Sec.~\ref{sec:gen16} does not correct` | PB59 | HONESTY | `The NuWro and GiBUU comparisons contain a target difference ` |
| F079 | II | Pointer: the comparisons of the predictions with the analysis definitions are in the note | `Ref.~\cite{AnalysisNote2026}, Secs.~\ref*{N-sec:eavailw-axis} and~\ref*{N-sec:eavailw-generators}` | PB60 | ORDINARY | `The comparisons of the predictions with the analysis definit` |
| F080 | II | Fine grid = analysis binning: published 14x16 muon-momentum bins times 7 Eavail, 7 q3 and 6 W bins | `fine grid is the analysis binning` && `$14\times16$ muon-momentum bins` && `7 $\Eavail$, 7 $q_{3}$, and 6 $W$ bins` | PB61 | ORDINARY | `The fine grid is the analysis binning: the published $14\tim` |
| F081 | II | Coarse 3^5 grid in the five observables, edges at the fine edges nearest the simulated tertiles | `coarse $3^{5}$ grid in $(\pT,\pPar,\Eavail,q_{3},W)$` && `fine edges nearest the simulated tertiles` | PB62 | ORDINARY | `A coarse $3^{5}$ grid in $(\pT,\pPar,\Eavail,q_{3},W)$ has i` |
| F082 | II | A coarse cell is kept if its expected reconstructed signal and its truth weight at data exposure are both at least 1000 events (the paper later calls a rule of this kind "the support rule", without naming it here) | `expected reconstructed signal and its truth weight at the data exposure are both at least 1000 events` | PB63 | ORDINARY | `A coarse cell is kept if its expected reconstructed signal a` |
| F083 | II | Definition: the jtNcells coarse cells that pass are the joint cells | `\jtNcells{} pass; these are the joint cells` | PB64 | ORDINARY | `Of the coarse cells, \jtNcells{} pass; these are the joint c` |
| F084 | II | The other coarse cells hold 0.47% of the expected signal and stay in the total only | `\SI{0.47}{\percent} of the expected signal` && `stay in the total only` | PB65 | ORDINARY | `The others, which hold \SI{0.47}{\percent} of the expected s` |
| F085 | II | Pointer: construction of the coarse grid | `\nsec{sec:joint5d-design}` | PB66 | ORDINARY | `The construction of the coarse grid is given in \nsec{sec:jo` |

## III. Cross-section extraction (`sec:method`), with III A (`sec:uncertainty-status`) and III B (Reporting cells, no label)

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F086 | III | Section heading and label | `\section{Cross-section extraction}` && `\label{sec:method}` | PB67 | STRUCTURE | `\section{Cross-section extraction} \label{sec:method} Each O` |
| F087 | III | Each OmniFold iteration has two classification steps | `two classification steps` | PB67 | ORDINARY | `\section{Cross-section extraction} \label{sec:method} Each O` |
| F088 | III | A reconstruction-level classifier separates data from simulation and defines a likelihood-ratio weight | `reconstruction-level classifier distinguishes data from simulated events` && `likelihood-ratio weight` | PB68 | ORDINARY | `A reconstruction-level classifier distinguishes data from si` |
| F089 | III | Event pairing transfers the weight to truth, including unmatched events; a truth-level classifier propagates a smooth reweighting to the next iteration | `event pairing transfers that weight to truth, including unmatched events` && `truth-level classifier propagates a smooth reweighting to the next iteration` | PB69 | ORDINARY | `The event pairing transfers that weight to truth, including ` |
| F090 | III | Cross sections: histogram reweighted truth events in the reporting binning, divide by integrated flux, target count and bin width | `histogramming the reweighted truth events in the reporting binning` && `dividing by integrated flux, target count, and bin width` | PB70 | ORDINARY | `Cross sections are formed by histogramming the reweighted tr` |
| F091 | III | Events failing reconstruction enter as unmatched truth events, so no separate efficiency correction is applied | `enter as unmatched truth events` && `no separate efficiency correction is applied` | PB71 | ORDINARY | `Events that fail reconstruction enter as unmatched truth eve` |
| F092 | III | Backgrounds enter the reconstruction-level step through the target density the classifier matches | `Backgrounds enter the reconstruction-level step through the density the classifier learns to match` | PB72 | ORDINARY | `Backgrounds enter the reconstruction-level step through the ` |
| F093 | III | Purity-based subtraction: each data event in reco bin b gets w_pur(b) = max(0, 1 - B_b/D_b) (D_b, B_b data and predicted background counts); target density D(x) w_pur(b) | `$w_{\mathrm{pur}}(b)=\max(0,\,1-B_{b}/D_{b})$` && `data and predicted background counts in that bin` && `$D(x)\,w_{\mathrm{pur}}(b)$` | PB73 | ORDINARY | `In the purity-based subtraction every data event in reconstr` |
| F094 | III | Unbinned negative-weight treatment: simulated background added to data with negative weight, target D(x) - B(x) pointwise; a classifier refinement clipped at zero converts it to non-negative weights before the first iteration | `simulated background events with negative weight` && `$D(x)-B(x)$ pointwise` && `classifier refinement~\cite{StayPositive2025}, clipped at zero` && `before the first iteration` | PB74 | ORDINARY | `The unbinned negative-weight treatment instead adds simulate` |
| F095 | III | The two targets share bin integrals wherever B_b < D_b but differ within a bin where the background fraction varies (pointer to appendix) | `share bin integrals wherever $B_{b}<D_{b}$` && `differ inside a bin wherever the background fraction varies within it` && `\napp{app:negweight}` | PB75 | KEEP | `The two targets share bin integrals wherever $B_{b}<D_{b}$ b` |
| F096 | III | Each classifier is trained on the full sample whose weights it sets: no held-out or cross-fitted split, no early stopping, no class balancing (pointer) | `trained on the full sample whose weights it then sets` && `without a held-out or cross-fitted split, early stopping, or class balancing` && `\nsec{sec:method-algo}` | PB76 | HONESTY | `Each classifier is trained on the full sample whose weights ` |
| F097 | III | Both estimators use five OmniFold iterations with gradient-boosted decision-tree classifiers | `five OmniFold iterations` && `gradient-boosted decision-tree classifiers~\cite{Pedregosa:2011sklearn,Ke:2017lightgbm}` | PB77 | ORDINARY | `Both estimators use five OmniFold iterations with gradient-b` |
| F098 | III | The iteration count and classifier capacity regularize the unfolding | `iteration count and classifier capacity regularize the unfolding` | PB78 | ORDINARY | `The iteration count and classifier capacity regularize the u` |
| F099 | III | Nominal settings are the scikit-learn defaults, LightGBM matched to their capacity | `scikit-learn defaults, with LightGBM matched to their capacity` | PB79 | ORDINARY | `The nominal settings are the scikit-learn defaults, with Lig` |
| F100 | III | The joint-test estimator's refinement capacity was chosen in simulation closure studies | `refinement capacity of the joint-test estimator was chosen in simulation closure studies` | PB80 | HONESTY | `The refinement capacity of the joint-test estimator was chos` |
| F101 | III | No hyperparameter search was performed on data | `No hyperparameter search was performed on data` | PB81 | KEEP | `No hyperparameter search was performed on data.` |
| F102 | III | The estimators table lists the two estimators and their uses | `Table~\ref{tab:estimators} lists the two estimators and the results each is used for` | PB82 | ORDINARY | `Table~\ref{tab:estimators} lists the two estimators and the ` |
| F103 | III | Two-observable central value: LightGBM at seed 42, negative-weight subtraction, refinement of 400 trees and 31 leaves | `two-observable central value uses LightGBM at seed~42` && `negative-weight background subtraction` && `refinement of 400 trees and 31 leaves` | PB83 | ORDINARY | `The two-observable central value uses LightGBM at seed~42 wi` |
| F104 | III | This reproducible central value is that of its own systematic-universe ensemble, so its covariance uses the same estimator | `reproducible central value is that of its own systematic-universe ensemble` && `covariance is built with the same estimator` | PB84 | ORDINARY | `This reproducible central value is that of its own systemati` |
| F105 | III | Definition: the joint-test estimator is used for the 3D and 4D central values and the sixteen-cell result; it is a deterministic LightGBM with the same background treatment and refinement capacity (registry ALIASES.tsv:38 and ATTRIBUTION.tsv:17 cite this phrase at paper_body.tex line 72 by digest) | `use the joint-test estimator` && `the joint-test estimator, a deterministic LightGBM` && `same background treatment and refinement capacity` && `three- and four-observable central values and the sixteen-cell five-observable result (Sec.~\ref{sec:result16})` | PB85 | KEEP | `The three- and four-observable central values and the sixtee` |
| F106 | III | It removes most of the purity-subtraction bias at nominal truth in the highest-W cells | `removes most of the bias of purity-based subtraction at nominal truth in the highest-$W$ cells (Sec.~\ref{sec:validation})` | PB85 | KEEP | `The three- and four-observable central values and the sixtee` |
| F107 | III | The note's simulation-calibrated tests use the same estimator | `the note's simulation-calibrated tests use the same estimator` | PB85 | ORDINARY | `The three- and four-observable central values and the sixtee` |
| F108 | III | Pointer: the development variants and the results that rest on them | `variants used in development, and the results that rest on them` && `\nsec{sec:method-config}` | PB86 | ORDINARY | `The variants used in development, and the results that rest ` |
| F109 | III | The joint-test estimator keeps five iterations because 10, 15 or 20 did not reduce its model dependence, measured as the largest residual proxy over the truth changes used in its development | `keeps five iterations because 10, 15, or 20 iterations did not reduce its model dependence` && `largest residual proxy over the truth changes used in its development` | PB87 | KEEP | `The joint-test estimator keeps five iterations because 10, 1` |
| F110 | III | Pointer: the comparison and its values | `The comparison and its values are given in \nsec{sec:gbdt-model-dependence}` | PB88 | ORDINARY | `The comparison and its values are given in \nsec{sec:gbdt-mo` |
| F111 | III | Table I (estimators) float opening and caption start | `\begin{table}[tb]` && `\caption{Estimators.` | PB89 | STRUCTURE | `\begin{table}[tb] \caption{Estimators.` |
| F112 | III | Caption: both estimators use five iterations, trees of nominal capacity (100 trees, 8 leaves) in both steps, and refined negative-weight subtraction | `Both use five OmniFold iterations` && `nominal capacity (100 trees, 8 leaves) in both OmniFold steps` && `refined negative-weight background subtraction` | PB90 | ORDINARY | `Both use five OmniFold iterations, gradient-boosted trees of` |
| F113 | III | Caption: the joint-test estimator is deterministic LightGBM (fixed seeds, reproducible training); the 2D estimator's refinement is seeded at the estimator seed plus three | `deterministic LightGBM (fixed seeds, reproducible training)` && `seeded at the estimator seed plus three` | PB90 | ORDINARY | `Both use five OmniFold iterations, gradient-boosted trees of` |
| F114 | III | Caption: results from the two estimators are not combined | `Results from the two estimators are not combined.` | PB91 | KEEP | `Results from the two estimators are not combined.` |
| F115 | III | Caption: pointer to the full configuration matrix incl. development variants; table label | `\nsec{sec:method-config} gives the full matrix, including the variants used in development.}` && `\label{tab:estimators}` | PB92 | ORDINARY | `\nsec{sec:method-config} gives the full matrix, including th` |
| F116 | III | Table I contents, verbatim (comment-stripped printed form; registry ALIASES.tsv:47 cites the row text "negative weights; refinement 400 trees, 31 leaves" at paper_body.tex line 86 by digest) | `\begin{tabular}{@{}lll@{}} \toprule \pcell{0.24\columnwidth}{Estimator} & \pcell{0.30\columnwidth}{Background treatment} & \pcell{0.38\columnwidth}{Used for} \\ \midrule \pcell{0.24\columnwidth}{joint-test estimator} & \pcell{0.30\columnwidth}{negative weights; refinement 400 trees, 31 leaves} & \pcell{0.38\columnwidth}{3D and 4D central values; sixteen-cell 5D result (Sec.~\ref{sec:result16}); held-out shapes (Fig.~\ref{fig:deformation}b); precision study} \\ \pcell{0.24\columnwidth}{two-observable estimator: LightGBM, seed 42} & \pcell{0.30\columnwidth}{negative weights; refinement 400 trees, 31 leaves} & \pcell{0.38\columnwidth}{2D central value and covariance (Sec.~\ref{sec:repro2d})} \\ \bottomrule \end{tabular}` | PB92 | STRUCTURE | `\nsec{sec:method-config} gives the full matrix, including th` |
| F117 | III.A | Subsection heading and label | `\subsection{Reporting definitions and the precision target}` && `\label{sec:uncertainty-status}` | PB92 | STRUCTURE | `\nsec{sec:method-config} gives the full matrix, including th` |
| F118 | III.A | Definition of the envelope: largest shift of a cell's data result when the prior is reweighted to each of five generator-sized truth changes, added linearly to the probabilistic half-width | `envelope of a cell as the largest shift of its data result when the simulation's prior is reweighted to each of five generator-sized changes of the truth` && `adds it linearly to the probabilistic half-width` | PB92 | ORDINARY | `\nsec{sec:method-config} gives the full matrix, including th` |
| F119 | III.A | The envelope is a sensitivity diagnostic tracking the regularization bias, not an interval | `sensitivity diagnostic that tracks the regularization bias, not an interval` | PB93 | KEEP | `The envelope is a sensitivity diagnostic that tracks the reg` |
| F120 | III.A | Precision target: a 10% median half-width for the total 68% interval | `\SI{10}{\percent} median half-width for the total 68\% interval` | PB94 | ORDINARY | `Our precision target is a \SI{10}{\percent} median half-widt` |
| F121 | III.A | With the envelope added, none of the tested five-observable reporting definitions meets the target | `none of the reporting definitions of a five-observable measurement tested in the study meets this target` | PB95 | HONESTY | `With the envelope added, none of the reporting definitions o` |
| F122 | III.A | With the joint-test estimator the envelope alone exceeds the target for the jtNcells coarse joint cells and for the fallback definition (39 supported (Eavail, W) cells) | `envelope alone exceeds it for the \jtNcells{} coarse joint cells` && `fallback definition, the 39 supported $(\Eavail,W)$ cells` | PB96 | HONESTY | `With the joint-test estimator, the envelope alone exceeds it` |
| F123 | III.A | For a coarser non-nested 27-cell partition of all five observables, the envelope alone does not exceed it, but the 1.4% normalization in every probabilistic half-width lifts the median above it | `coarser, non-nested partition of all five observables into 27 cells` && `envelope alone does not exceed it` && `\SI{1.4}{\percent} normalization contained in every probabilistic half-width lifts the median above it` | PB97 | HONESTY | `For a coarser, non-nested partition of all five observables ` |
| F124 | III.A | Pointer: the study | `The study is described in \nsec{sec:gbdt-model-dependence}` | PB98 | ORDINARY | `The study is described in \nsec{sec:gbdt-model-dependence}.` |
| F125 | III.A | Over these definitions the envelope's median is about 10-13% per cell, comparable to the generator differences such a measurement would need to resolve (literal numerals) | `median of about 10--13\% per cell` && `comparable to the generator differences that such a measurement would need to resolve` | PB99 | HONESTY | `Over these definitions, the envelope has a median of about 1` |
| F126 | III.B | Subsection heading (no label) | `\subsection{Reporting cells}` | PB100 | STRUCTURE | `\subsection{Reporting cells} A five-observable cross section` |
| F127 | III.B | A five-observable cross section with total uncertainties is reported separately from those definitions: the joint-test estimator's data result on 16 cells R00-R15 | `reported separately from those reporting definitions` && `the joint-test estimator's data result on 16 cells, R00--R15` | PB100 | KEEP | `\subsection{Reporting cells} A five-observable cross section` |
| F128 | III.B | The cells come from h2-nboxes boxes formed by one interior edge per axis | `\fvval{h2-nboxes} boxes formed by one interior edge per axis` | PB101 | ORDINARY | `They come from the \fvval{h2-nboxes} boxes formed by one int` |
| F129 | III.B | The interior edges: pT, ppar, q3 in GeV/c; Eavail and W in GeV | `$\pT$ \fvval{h2-mid-pt}, $\pPar$ \fvval{h2-mid-pz} and $q_3$ \fvval{h2-mid-q3}~GeV/$c$` && `$\Eavail$ \fvval{h2-mid-eavail} and $W$ \fvval{h2-mid-W}~GeV` | PB101 | ORDINARY | `They come from the \fvval{h2-nboxes} boxes formed by one int` |
| F130 | III.B | Each supported box with purity below h2-tau is merged into a neighbour | `each supported box with purity below \fvval{h2-tau} is merged into a neighbour` | PB101 | ORDINARY | `They come from the \fvval{h2-nboxes} boxes formed by one int` |
| F131 | III.B | h2-nunreported boxes remain unreported | `\fvval{h2-nunreported} boxes remain unreported` | PB101 | HONESTY | `They come from the \fvval{h2-nboxes} boxes formed by one int` |
| F132 | III.B | Every reported cell passes the support rule | `every reported cell passes the support rule` | PB101 | KEEP | `They come from the \fvval{h2-nboxes} boxes formed by one int` |
| F133 | III.B | Pointer: the result's covariance | `The result's covariance is given in Sec.~\ref{sec:cov16}` | PB102 | ORDINARY | `The result's covariance is given in Sec.~\ref{sec:cov16}.` |

## IV. Uncertainties and validation (`sec:validation`), lead paragraph

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F134 | IV | Section heading and label | `\section{Uncertainties and validation}` && `\label{sec:validation}` | PB103 | STRUCTURE | `\section{Uncertainties and validation} \label{sec:validation` |
| F135 | IV | Definition: a closure test measures recovery of a specified deformation of the known simulated truth with the prior (the initial truth distribution) held fixed | `closure test measures how well a specified deformation of the known simulated truth is recovered` && `the prior, the initial truth distribution, held fixed` | PB103 | ORDINARY | `\section{Uncertainties and validation} \label{sec:validation` |
| F136 | IV | Definition: coverage (how often intervals contain their target over repeated experiments) tests estimator and interval construction together | `how often intervals contain their target over repeated experiments` && `tests the estimator and the interval construction together` | PB104 | ORDINARY | `Coverage, how often intervals contain their target over repe` |
| F137 | IV | The coverage tested is pointwise, per reported quantity, not simultaneous | `the coverage tested here is pointwise, for each reported quantity separately, not the stronger simultaneous coverage of all of them` | PB104 | KEEP | `Coverage, how often intervals contain their target over repe` |
| F138 | IV | Closure, deformation and coverage studies reweight the true signal of simulated pseudo-data (reco and truth change together, detector response at fixed truth kept); the unfolding prior stays at Tune v1 | `reweight the true signal of the simulated events used as pseudo-data` && `keeps the detector response at fixed truth` && `the prior used to unfold them stays at Tune~v1` | PB105 | KEEP | `The closure, deformation, and coverage studies reweight the ` |
| F139 | IV | The envelope instead reweights the prior used to unfold the data | `The envelope of Sec.~\ref{sec:uncertainty-status} instead reweights the prior used to unfold the data` | PB106 | ORDINARY | `The envelope of Sec.~\ref{sec:uncertainty-status} instead re` |
| F140 | IV | Every study uses the analysis simulation's detector response | `Every study uses the analysis simulation's detector response` | PB107 | HONESTY | `Every study uses the analysis simulation's detector response` |

## IV A. The reported covariance (`sec:cov16`)

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F141 | IV.A | Subsection heading and label | `\subsection{The reported covariance}` && `\label{sec:cov16}` | PB108 | STRUCTURE | `\subsection{The reported covariance} \label{sec:cov16} The r` |
| F142 | IV.A | The sixteen-cell result's reported covariance is C_total + C_resp | `The reported covariance of the sixteen-cell result is $C_{\mathrm{total}}+C_{\mathrm{resp}}$` | PB108 | ORDINARY | `\subsection{The reported covariance} \label{sec:cov16} The r` |
| F143 | IV.A | Unlike the envelope, its model term is a covariance built from three generator shifts | `Unlike the envelope of Sec.~\ref{sec:uncertainty-status}` && `its model term is a covariance built from three generator shifts` | PB109 | ORDINARY | `Unlike the envelope of Sec.~\ref{sec:uncertainty-status}, it` |
| F144 | IV.A | C_total sums the joint-test estimator's statistical, flux, interaction, detector, lateral and normalization uncertainties and C_model | `$C_{\mathrm{total}}$ sums the statistical, flux, interaction, detector, lateral and normalization uncertainties of the joint-test estimator and $C_{\mathrm{model}}$` | PB110 | ORDINARY | `$C_{\mathrm{total}}$ sums the statistical, flux, interaction` |
| F145 | IV.A | C_model is built from the change in the unfolded data when the prior is reweighted to GENIE + MEC, NuWro and GiBUU in turn; it is unscaled generator-shape dependence, not a calibrated bound (probed verbatim by the paper-protections ledger) | `is built from the change in the unfolded data when the prior is reweighted to GENIE + MEC, NuWro and GiBUU in turn; it represents unscaled generator-shape dependence, not a calibrated bound` | PB111 | KEEP | `$C_{\mathrm{model}}$ is built from the change in the unfolde` |
| F146 | IV.A | C_model's coverage at truths held out of its construction has not been validated | `its coverage at truths held out of its construction has not been validated` | PB111 | HONESTY | `$C_{\mathrm{model}}$ is built from the change in the unfolde` |
| F147 | IV.A | C_resp: response to a one-sigma scale of the simulated reconstructed recoil energy, for protons, mesons, EM and other deposits | `one-standard-deviation scale of the reconstructed recoil energy in the simulation` && `for protons, mesons, electromagnetic and other deposits` | PB112 | ORDINARY | `$C_{\mathrm{resp}}$ is the response of the result to a one-s` |
| F148 | IV.A | C_resp does not cover neutron or muon deposits, nor species, energy-dependence or resolution effects beyond a scale | `it does not cover neutron or muon deposits, nor species, energy-dependence or resolution effects beyond a scale` | PB112 | HONESTY | `$C_{\mathrm{resp}}$ is the response of the result to a one-s` |
| F149 | IV.A | C_resp enters only this result, its fake-data tests and its generator comparison | `it enters only this result, its fake-data tests and its comparison in Sec.~\ref{sec:gen16}` | PB112 | KEEP | `$C_{\mathrm{resp}}$ is the response of the result to a one-s` |
| F150 | IV.A | Median per-cell relative uncertainty, with and without C_resp | `The median per-cell relative uncertainty is \fvval{sigmed-C_total_resp}\%` && `\fvval{sigmed-C_total}\% without $C_{\mathrm{resp}}$` | PB113 | ORDINARY | `The median per-cell relative uncertainty is \fvval{sigmed-C_` |
| F151 | IV.A | The note gives the cells, central values, per-group uncertainties and correlation matrix of the reported covariance | `The note gives the cells, the central values, the per-group uncertainties and the correlation matrix of the reported covariance` | PB114 | ORDINARY | `The note gives the cells, the central values, the per-group ` |
<!-- absence-ok: quotes printed limitation sentences of the paper as facts to restate; not a claim that a result does not exist -->

## IV B. Two-dimensional benchmark (`sec:repro2d`, `sec:repro2d-pub`), with Fig. 1 (`fig:validation`)

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F152 | IV.B | Subsection heading and its two labels | `\subsection{Two-dimensional benchmark}` && `\label{sec:repro2d}` && `\label{sec:repro2d-pub}` | PB115 | STRUCTURE | `\subsection{Two-dimensional benchmark} \label{sec:repro2d} \` |
| F153 | IV.B | The 2D result is an end-to-end test against a measurement from the same data | `end-to-end test of the unfolding against a measurement from the same data` | PB115 | KEEP | `\subsection{Two-dimensional benchmark} \label{sec:repro2d} \` |
| F154 | IV.B | Integrated cross section, published value, and their ratio | `\SI{\sigTwoD}{cm^2/nucleon}` && `\SI{\sigTwoDpaper}{cm^2/nucleon} in the published analysis` && `a ratio of $\ratioTot$` | PB116 | ORDINARY | `Its integrated cross section is \SI{\sigTwoD}{cm^2/nucleon},` |
| F155 | IV.B | RMS of standardized bin differences formed with the published uncertainties | `standardized bin differences formed with the published uncertainties have an RMS of $\pullRMS$` | PB117 | ORDINARY | `The standardized bin differences formed with the published u` |
| F156 | IV.B | Against the full published covariance, the descriptive covariance-weighted distance chi2/ndf | `Against the full published covariance` && `descriptive covariance-weighted distance` && `$\chi^{2}/\mathrm{ndf}=\chiPaper$` | PB118 | KEEP | `Against the full published covariance, the descriptive covar` |
| F157 | IV.B | Computed with the pseudo-inverse over 205 bins keeping all 205 eigenmodes (rank 205, condition number 1.5e12); ndf is the rank | `pseudo-inverse over the 205 bins` && `keeps all 205 eigenmodes` && `rank 205, condition number $1.5\times10^{12}$` && `ndf is that rank` | PB119 | ORDINARY | `It is computed with the pseudo-inverse over the 205 bins, wh` |
| F158 | IV.B | It indicates a correlated shape difference, not a normalization difference, spread over many eigenmodes | `correlated shape difference, not a normalization difference` && `spread over many eigenmodes of the published covariance` | PB120 | KEEP | `It indicates a correlated shape difference, not a normalizat` |
| F159 | IV.B | The source of the shape difference has not been identified | `The source of the shape difference has not been identified.` | PB121 | HONESTY | `The source of the shape difference has not been identified.` |
| F160 | IV.B | Fig. 1 shows the principal 1D projections | `Figure~\ref{fig:validation} shows the principal one-dimensional projections` | PB122 | ORDINARY | `Figure~\ref{fig:validation} shows the principal one-dimensio` |
| F161 | IV.B | LightGBM is quoted as the central value because its covariance uses the same estimator | `We quote the LightGBM result as the central value because its covariance uses the same estimator` | PB123 | ORDINARY | `We quote the LightGBM result as the central value because it` |
| F162 | IV.B | The distance depends on the estimator (pointer) | `The distance depends on the estimator (\nsec{sec:results-tension})` | PB124 | HONESTY | `The distance depends on the estimator (\nsec{sec:results-ten` |
| F163 | IV.B | The learner was selected after the LightGBM and exact-split comparisons with the published result, so the benchmark is a reproduction, not an independent validation | `learner was selected after the LightGBM and exact-split comparisons with the published result` && `a reproduction rather than an independent validation` | PB125 | HONESTY | `The learner was selected after the LightGBM and exact-split ` |
| F164 | IV.B | The purity-subtracted exact-split result differs from the central value by a median 1.03% per bin (maximum 17.6%) (pointer) | `purity-subtracted exact-split result differs from the central value by a median of \SI{1.03}{\percent} per bin` && `maximum \SI{17.6}{\percent}` && `\nsec{sec:method-config}` | PB126 | ORDINARY | `The purity-subtracted exact-split result differs from the ce` |
| F165 | IV.B | Fig. 1 float and graphic | `\begin{figure*}[t]` && `\includegraphics[width=0.86\textwidth]{paper_fig1_validation}` | PB127 | STRUCTURE | `\begin{figure*}[t] \centering \includegraphics[width=0.86\te` |
| F166 | IV.B | Fig. 1 caption: comparison with the published result | `\caption{Comparison with the published result~\cite{MINERvA:2021owq}.` | PB127 | ORDINARY | `\begin{figure*}[t] \centering \includegraphics[width=0.86\te` |
| F167 | IV.B | Fig. 1 caption, top: pT and ppar projections of the published result and this analysis, each with its total 1-sigma band, and Tune v1, with ratios below | `Top: $\pT$ and $\pPar$ projections of the published result and of this analysis` && `total $\pm1\sigma$ band` && `the MINERvA Tune~v1, with ratios to the published result below` | PB128 | ORDINARY | `Top: $\pT$ and $\pPar$ projections of the published result a` |
| F168 | IV.B | Fig. 1 caption: this analysis's band is the statistical, systematic-universe (incl. normalization), training-seed and run-period blocks | `statistical, systematic-universe (including the normalization), training-seed and run-period blocks of the covariance, Sec.~\ref{sec:uq2d}` | PB128 | ORDINARY | `Top: $\pT$ and $\pPar$ projections of the published result a` |
| F169 | IV.B | Fig. 1 caption: the band omits the learner dependence and C_model | `it omits the learner dependence and $C_{\mathrm{model}}$` | PB128 | HONESTY | `Top: $\pT$ and $\pPar$ projections of the published result a` |
| F170 | IV.B | Fig. 1 caption: the two bands are correlated, so their overlap is not a compatibility test | `the two bands are correlated, so their overlap is not a compatibility test` | PB128 | KEEP | `Top: $\pT$ and $\pPar$ projections of the published result a` |
| F171 | IV.B | Fig. 1 caption, bottom left: per-bin (OmniFold - published)/sigma_published, cells at equal size, grey not reported | `Bottom left: $(\mathrm{OmniFold}-\mathrm{published})/\sigma_{\mathrm{published}}$ per reported bin` && `cells drawn at equal size (grey: not reported)` | PB129 | ORDINARY | `Bottom left: $(\mathrm{OmniFold}-\mathrm{published})/\sigma_` |
| F172 | IV.B | Fig. 1 caption, bottom right: median relative uncertainties and residual summary; figure label | `Bottom right: median relative uncertainties and residual summary.}` && `\label{fig:validation}` | PB130 | ORDINARY | `Bottom right: median relative uncertainties and residual sum` |

## IV C. Two-dimensional covariance (`sec:uq2d`)

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F173 | IV.C | Subsection heading and label | `\subsection{Two-dimensional covariance}` && `\label{sec:uq2d}` | PB130 | STRUCTURE | `Bottom right: median relative uncertainties and residual sum` |
| F174 | IV.C | The 2D covariance is the sum of four blocks, each from LightGBM unfoldings with the central value's estimator | `sum of four blocks, each from LightGBM unfoldings with the central value's estimator` | PB130 | ORDINARY | `Bottom right: median relative uncertainties and residual sum` |
| F175 | IV.C | Blocks: systematic universes (187), statistical (300 bootstrap replicas), run period (three period groups) | `systematic universes (187 universes)` && `statistical (300 bootstrap replicas)` && `run period (three period groups)` | PB130 | ORDINARY | `Bottom right: median relative uncertainties and residual sum` |
| F176 | IV.C | Training-seed block: five seed settings, so its own size is poorly determined | `training seed (five seed settings, so that its own size is poorly determined)` | PB130 | HONESTY | `Bottom right: median relative uncertainties and residual sum` |
| F177 | IV.C | Median relative uncertainty per bin and on the integral, vs the publication's (uqMedian and uqIntegral are receipt-checked in values.tex by check_sec4_receipts.py) | `median of \SI{\uqMedian}{\percent} per bin` && `\SI{\uqIntegral}{\percent} on the integrated cross section` && `\SI{\uqPaper}{\percent} and \SI{\uqPaperIntegral}{\percent} for the publication` | PB131 | ORDINARY | `The resulting relative uncertainty has a median of \SI{\uqMe` |
| F178 | IV.C | The published flux uncertainty (median 4.01%) exceeds ours, for a reason the released inputs do not let us determine | `published flux uncertainty (median \SI{4.01}{\percent}) is larger than ours (\SI{\fluxBand}{\percent})` && `for a reason the released inputs do not let us determine` | PB132 | HONESTY | `The published flux uncertainty (median \SI{4.01}{\percent}) ` |
| F179 | IV.C | The covariance omits the approximation for failed-reconstruction events in the universe unfoldings, the learner dependence and the regularization dependence | `omits the approximation in the systematic-universe unfoldings for events that fail reconstruction` && `the learner dependence of Sec.~\ref{sec:repro2d-pub}` && `the dependence on the regularization` | PB133 | HONESTY | `The covariance omits the approximation in the systematic-uni` |
| F180 | IV.C | The prior-shape dependence is reported beside it | `the dependence on the prior's generator shape is reported beside it (below)` | PB133 | ORDINARY | `The covariance omits the approximation in the systematic-uni` |
| F181 | IV.C | The covariance has not been independently validated | `The covariance has not been independently validated.` | PB134 | HONESTY | `The covariance has not been independently validated.` |
| F182 | IV.C | It provides no calibrated significance for generator comparisons | `It provides no calibrated significance for generator comparisons.` | PB135 | HONESTY | `It provides no calibrated significance for generator compari` |
| F183 | IV.C | Pointer: block sizes, block-sum assumptions, tests of the approximation | `block sizes, the assumptions of the block sum, and the tests of the approximation` && `Ref.~\cite{AnalysisNote2026}, Secs.~\ref*{N-sec:results-uq}, \ref*{N-sec:uq-combine}, and~\ref*{N-sec:uq-2d-scope}` | PB136 | ORDINARY | `The block sizes, the assumptions of the block sum, and the t` |
| F184 | IV.C | Statistical block median 0.676% (bound phrase of check_sec4_receipts.py, regex `with a median statistical uncertainty of \SI{X}{\percent}`, must print exactly once) | `with a median statistical uncertainty of \SI{0.676}{\percent}` | PB137 | GATE | `The statistical block, with a median statistical uncertainty` |
| F185 | IV.C | The statistical block is a bootstrap of 300 replicas at the central value's training seed, background templates also resampled | `bootstrap of 300 replicas drawn at the central value's training seed` && `background templates are also resampled` | PB137 | ORDINARY | `The statistical block, with a median statistical uncertainty` |
| F186 | IV.C | The coverage of this block and of the total covariance has not been tested | `The coverage of this block and of the total covariance has not been tested.` | PB138 | HONESTY | `The coverage of this block and of the total covariance has n` |
| F187 | IV.C | No coverage claim on independent simulated samples or simultaneously over all bins and projections | `We make no coverage claim on independent simulated samples or simultaneously over all reported bins and projections.` | PB139 | KEEP | `We make no coverage claim on independent simulated samples o` |
| F188 | IV.C | Data from different run periods are not mutually consistent within the other uncertainties | `Data from different run periods are not mutually consistent within the other uncertainties.` | PB140 | HONESTY | `Data from different run periods are not mutually consistent ` |
| F189 | IV.C | One period group's unfolded ppar distribution relative to its own simulation differs from the earliest periods' by a step of about 7% near 8 GeV/c | `relative to its own simulation` && `step of about \SI{7}{\percent} near \SI{8}{GeV/c}` | PB141 | ORDINARY | `One period group's unfolded $\pPar$ distribution, taken rela` |
| F190 | IV.C | The cause is not known; the data cannot establish which period is correct | `The cause is not known, and these data cannot establish which period is correct.` | PB142 | HONESTY | `The cause is not known, and these data cannot establish whic` |
| F191 | IV.C | The run-period block, from double ratios among the three groups (each over its own simulated truth, no reference group), includes the inconsistency: 2.0% on the integral | `double ratios among the three period groups` && `each group's unfolded result over its own simulated truth, with no group chosen as the reference` && `\SI{2.0}{\percent} on the integrated cross section` | PB143 | ORDINARY | `The run-period block, built from double ratios among the thr` |
| F192 | IV.C | Because it is built from the observed period differences, the block's size is not validated and its own consistency check cannot fail | `built from the observed differences among the periods` && `its size is not validated and its own consistency check cannot fail` | PB144 | HONESTY | `Because the block is built from the observed differences amo` |
| F193 | IV.C | The prior's generator-shape dependence is reported as a separate covariance C_model = sum_k s_k s_k^T beside the four-block covariance | `separate covariance beside the four-block covariance` && `$C_{\mathrm{model}}=\sum_k s_k s_k^{\mathsf{T}}$` | PB145 | ORDINARY | `We report the dependence on the prior's generator shape as a` |
| F194 | IV.C | Definition of s_k: per-bin relative change when the prior truth is reweighted by generator k's (pT, ppar) shape (GENIE+MEC, NuWro or GiBUU) over GENIE's, normalization kept | `per-bin relative change of the result` && `ratio of the $(\pT,\pPar)$ shape of generator~$k$` && `(GENIE with meson-exchange currents, NuWro, or GiBUU) to that of GENIE, with its normalization kept` | PB146 | ORDINARY | `Here $s_k$ is the per-bin relative change of the result when` |
| F195 | IV.C | Median of C_model per bin | `Its median is \SI{\cmodelMedian}{\percent} per bin` | PB147 | ORDINARY | `Its median is \SI{\cmodelMedian}{\percent} per bin.` |
| F196 | IV.C | C_model measures generator-shape model dependence, not a calibrated bound on the unfolding bias | `measure of generator-shape model dependence, not a calibrated bound on the unfolding bias` | PB148 | KEEP | `It is a measure of generator-shape model dependence, not a c` |
| F197 | IV.C | Added to the four-block covariance, the total's median per bin | `Added to the four-block covariance` && `\SI{\qrCmodelMedian}{\percent} per bin` | PB149 | ORDINARY | `Added to the four-block covariance, it gives a total with a ` |
| F198 | IV.C | The comparison with the published uncertainty uses the covariance without C_model, because neither has a component for residual prior-shape dependence | `uses the covariance without $C_{\mathrm{model}}$` && `neither has a component for the residual dependence on the prior's generator shape` | PB150 | KEEP | `The comparison with the published uncertainty uses the covar` |
| F199 | IV.C | The published analysis chose ten iterations in a fake-data study and assigns no uncertainty to the remaining dependence | `chose its ten iterations in a fake-data study and assigns no uncertainty to the remaining dependence~\cite{MINERvA:2021owq}` | PB150 | ORDINARY | `The comparison with the published uncertainty uses the covar` |
| F200 | IV.C | Iteration counts differ (ten vs five), so no statement on the size of the published residual | `ten there, five here` && `we make no statement about the size of the published analysis's residual` | PB151 | HONESTY | `The iteration counts differ (ten there, five here), so we ma` |
<!-- absence-ok: quotes printed limitation sentences of the paper as facts to restate; not a claim that a result does not exist -->

## IV D. Normalization and closure (`sec:closure`), with Fig. 2 (`fig:bkg-residual`)

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F201 | IV.D | Subsection heading and label | `\subsection{Normalization and closure}` && `\label{sec:closure}` | PB152 | STRUCTURE | `\subsection{Normalization and closure} \label{sec:closure} O` |
| F202 | IV.D | Of the joint-test estimator's results, only the 3D marginal has been compared with the lower-dimensional result it extends | `only the three-observable marginal has been compared with the lower-dimensional result it extends` | PB152 | KEEP | `\subsection{Normalization and closure} \label{sec:closure} O` |
| F203 | IV.D | Its area-weighted total agrees with the 2D result to 0.141%, a comparison across the two estimators | `area-weighted total agrees with the two-dimensional result to \SI{0.141}{\percent}` && `a comparison across the two estimators` | PB152 | KEEP | `\subsection{Normalization and closure} \label{sec:closure} O` |
| F204 | IV.D | Pointers: normalization checks of the earlier purity-subtracted 5D central value; closure checks of its estimator in 3D and 4D | `normalization checks of the earlier purity-subtracted five-observable central value are described in \nsec{sec:eavailw-axis}` && `closure checks of its estimator in three and four observables in \nsec{sec:closure-map}` | PB153 | ORDINARY | `The normalization checks of the earlier purity-subtracted fi` |
| F205 | IV.D | Fig. 2: with purity subtraction in a deterministic LightGBM estimator, nominal-truth end-to-end pseudo-experiments reproduce the input except in the highest-W cells | `Figure~\ref{fig:bkg-residual} shows` && `purity-based background subtraction in a deterministic LightGBM estimator` && `end-to-end pseudo-experiments at nominal truth reproduce the input except in the highest-$W$ cells` | PB154 | ORDINARY | `Figure~\ref{fig:bkg-residual} shows that, with purity-based ` |
| F206 | IV.D | Purity bias in the highest-W cells up to 4% in simulation (bound phrase of check_sec4_receipts.py) | `biased by up to \SI{4}{\percent} in simulation` | PB154 | GATE | `Figure~\ref{fig:bkg-residual} shows that, with purity-based ` |
| F207 | IV.D | In the same estimator, unbinned negative-weight subtraction with a 100-tree, 8-leaf refinement; at most 0.4% elsewhere in the projection | `unbinned negative-weight subtraction with a refinement of 100 trees and 8 leaves` && `at most \SI{0.4}{\percent} elsewhere in the projection` | PB155 | ORDINARY | `In the same estimator, unbinned negative-weight subtraction ` |
| F208 | IV.D | The negative-weight treatment reduces the highest-W bias to below 0.3% (bound phrase, mode "below") | `reduces it to below \SI{0.3}{\percent}` | PB155 | GATE | `In the same estimator, unbinned negative-weight subtraction ` |
| F209 | IV.D | It leaves up to 1% in some joint cells (bound phrase) | `leaving up to \SI{1}{\percent} in some joint cells` | PB155 | GATE | `In the same estimator, unbinned negative-weight subtraction ` |
| F210 | IV.D | On data the two treatments differ by at most 1.4% (bound phrase) | `On data` && `differ by at most \SI{1.4}{\percent}` | PB156 | GATE | `On data, the two treatments differ by at most \SI{1.4}{\perc` |
| F211 | IV.D | Pointer: both kinds of closure study | `Both kinds of closure study are described in \nsec{sec:closure-map}` | PB157 | ORDINARY | `Both kinds of closure study are described in \nsec{sec:closu` |
| F212 | IV.D | 2D closure with backgrounds (20 pseudo-experiments at nominal truth): purity and refined estimates more than one statistical sigma apart in 14 of 205 cells | `20 pseudo-experiments at nominal truth` && `more than one statistical standard deviation apart in 14 of the 205 cells` | PB158 | ORDINARY | `In two observables, a closure test with backgrounds (20 pseu` |
| F213 | IV.D | Purity estimate up to 5.9 statistical sigma from truth (more than one total sigma in one cell); refined within 0.44 everywhere | `up to 5.9 statistical standard deviations from the truth` && `more than one total standard deviation in one cell` && `the refined one lies within 0.44 in every cell` | PB159 | ORDINARY | `The purity estimate lies up to 5.9 statistical standard devi` |
| F214 | IV.D | Hence the 2D result uses the refined estimator (pointer to appendix) | `The two-dimensional result therefore uses the refined estimator (\napp{sec:negweight-footing})` | PB160 | ORDINARY | `The two-dimensional result therefore uses the refined estima` |
| F215 | IV.D | Fig. 2 float and graphic | `\begin{figure*}[t]` && `\includegraphics[width=0.84\textwidth]{paper_fig_bkg_residual}` | PB161 | STRUCTURE | `\begin{figure*}[t] \centering \includegraphics[width=0.84\te` |
| F216 | IV.D | Fig. 2 caption: fractional closure residual at nominal truth, pseudo-experiments with backgrounds | `\caption{Fractional closure residual, (unfolded $-$ truth)/truth, at nominal truth, for pseudo-experiments that include backgrounds.` | PB161 | ORDINARY | `\begin{figure*}[t] \centering \includegraphics[width=0.84\te` |
| F217 | IV.D | Fig. 2 caption: both from a deterministic LightGBM estimator | `Both from a deterministic LightGBM estimator.` | PB162 | ORDINARY | `Both from a deterministic LightGBM estimator.` |
| F218 | IV.D | Fig. 2 caption: circles, purity subtraction (9 pseudo-experiments) | `Circles: purity-based background subtraction (9 pseudo-experiments).` | PB163 | ORDINARY | `Circles: purity-based background subtraction (9 pseudo-exper` |
| F219 | IV.D | Fig. 2 caption: squares, negative-weight subtraction with a 100/8 refinement (60 pseudo-experiments) | `Squares: unbinned negative-weight subtraction with a refinement of 100 trees and 8 leaves (60 pseudo-experiments).` | PB164 | ORDINARY | `Squares: unbinned negative-weight subtraction with a refinem` |
| F220 | IV.D | Fig. 2 caption: the pseudo-experiments are not paired | `The pseudo-experiments are not paired.` | PB165 | KEEP | `The pseudo-experiments are not paired.` |
| F221 | IV.D | Fig. 2 caption: panel (a), the 42 (Eavail, W) projection cells grouped by Eavail bin | `(a) The 42 $(\Eavail,W)$ projection cells, grouped by $\Eavail$ bin.` | PB166 | ORDINARY | `(a) The 42 $(\Eavail,W)$ projection cells, grouped by $\Eava` |
| F222 | IV.D | Fig. 2 caption: panel (b), the jtNcells coarse joint cells by 3^5-grid index, then the total | `(b) The \jtNcells{} coarse joint cells, labelled by their index in the $3^{5}$ grid, then the total integrated cross section.` | PB167 | ORDINARY | `(b) The \jtNcells{} coarse joint cells, labelled by their in` |
| F223 | IV.D | Fig. 2 caption: error bars are standard errors of the mean; figure label | `Error bars are the standard error of the mean.}` && `\label{fig:bkg-residual}` | PB168 | ORDINARY | `Error bars are the standard error of the mean.} \label{fig:b` |

## IV E. Generator-sized truth changes (`sec:departure`), with Fig. 3 (`fig:deformation`)

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F224 | IV.E | Subsection heading and label | `\subsection{Generator-sized truth changes}` && `\label{sec:departure}` | PB168 | STRUCTURE | `Error bars are the standard error of the mean.} \label{fig:b` |
| F225 | IV.E | Fig. 3: the unfolding recovers only part of an Eavail shape change as large as the generator difference | `Figure~\ref{fig:deformation} shows that the unfolding recovers only part of a change of the $\Eavail$ shape as large as the difference between generators` | PB168 | HONESTY | `Error bars are the standard error of the mean.} \label{fig:b` |
| F226 | IV.E | Truth reweighted by the GiBUU-to-GENIE ratio, unfolded with a development variant of the joint-test estimator (100-tree, 8-leaf refinement): deviations of several percent in the largest cells, in the cell 0.8 <= Eavail < 1.5 GeV, W >= 3 GeV | `reweighted by the GiBUU-to-GENIE ratio` && `development variant of the joint-test estimator using a 100-tree, 8-leaf refinement` && `by several percent in the largest cells` && `$0.8\le\Eavail<\SI{1.5}{GeV}$, $W\ge\SI{3}{GeV}$` | PB169 | ORDINARY | `When the true shape is reweighted by the GiBUU-to-GENIE rati` |
| F227 | IV.E | Up to 74% at high W (bound phrase of check_sec4_receipts.py) | `by up to \SI{74}{\percent} at high $W$` | PB169 | GATE | `When the true shape is reweighted by the GiBUU-to-GENIE rati` |
| F228 | IV.E | The deviations occur with or without background, so subtraction alone does not explain the residual | `These deviations occur with or without background, so background subtraction alone does not explain the residual` | PB170 | ORDINARY | `These deviations occur with or without background, so backgr` |
| F229 | IV.E | The residual is interpreted as regularization bias, persisting over the tested iteration numbers and capacities; no single cause is established | `We interpret the residual as regularization bias` && `persists over the tested iteration numbers and classifier capacities` && `although no single cause is established` | PB171 | HONESTY | `We interpret the residual as regularization bias, because it` |
| F230 | IV.E | For other fixed generator shapes with the joint-test estimator, 16-31% in the most affected (Eavail, W) cell (bound phrase; the regex includes the leading "it is ") | `For other fixed generator shapes tested with the joint-test estimator` && `it is \SIrange{16}{31}{\percent} in the most affected` && `$(\Eavail,W)$ cell` | PB172 | GATE | `For other fixed generator shapes tested with the joint-test ` |
| F231 | IV.E | ... and within the quoted total uncertainty in about half of those cells (bound verbal phrase of check_sec4_receipts.py VERBAL, must print exactly once) | `within the quoted total uncertainty in about half of those cells` | PB172 | GATE | `For other fixed generator shapes tested with the joint-test ` |
| F232 | IV.E | Those uncertainties come from an earlier purity-subtracted 5D covariance that fails its specified acceptance criteria | `Those uncertainties come from an earlier purity-subtracted five-observable covariance that fails its specified acceptance criteria (\nsec{sec:eavailw-adopted})` | PB173 | HONESTY | `Those uncertainties come from an earlier purity-subtracted f` |
| F233 | IV.E | For the sixteen-cell result, the fake-data tests of the estimator's bias are in their own subsection (probed verbatim by the paper-protections ledger) | `For the sixteen-cell result, Sec.~\ref{sec:fd16} reports the fake-data tests of the estimator's bias.` | PB174 | ORDINARY | `For the sixteen-cell result, Sec.~\ref{sec:fd16} reports the` |
| F234 | IV.E | Pointer: deformation studies, iteration and capacity tests, exact binned comparison, joint-test-estimator shapes | `deformation studies, the iteration and capacity tests, the exact binned comparison and the joint-test-estimator shapes` && `Ref.~\cite{AnalysisNote2026}, Secs.~\ref*{N-sec:val-negweight} and~\ref*{N-sec:val-departure}` | PB175 | ORDINARY | `The deformation studies, the iteration and capacity tests, t` |
| F235 | IV.E | Fig. 3 float and graphic | `\begin{figure*}[t]` && `\includegraphics[width=0.84\textwidth]{paper_fig_deformation}` | PB176 | STRUCTURE | `\begin{figure*}[t] \centering \includegraphics[width=0.84\te` |
| F236 | IV.E | Fig. 3 caption: fractional recovery residual per (Eavail, W) cell against each pseudo-experiment's deformed truth; all include backgrounds | `\caption{Fractional recovery residual, (unfolded $-$ truth)/truth, per $(\Eavail,W)$ cell, where the truth is each pseudo-experiment's deformed truth; all pseudo-experiments include backgrounds.` | PB176 | ORDINARY | `\begin{figure*}[t] \centering \includegraphics[width=0.84\te` |
| F237 | IV.E | Fig. 3 caption (a): development variant with a 100/8 refinement, truth reweighted by the GiBUU/GENIE Eavail ratio (60 pseudo-experiments); grey step = injected change | `(a) A development variant of the joint-test estimator, whose refinement has 100 trees and 8 leaves` && `GiBUU/GENIE $\Eavail$ shape ratio (60 pseudo-experiments)` && `the grey step is the injected change of the cell truth` | PB177 | ORDINARY | `(a) A development variant of the joint-test estimator, whose` |
| F238 | IV.E | Fig. 3 caption: at nominal truth this variant's largest residual is 0.39% | `At nominal truth this variant's largest residual is \SI{0.39}{\percent} (the squares of Fig.~\ref{fig:bkg-residual}a)` | PB178 | ORDINARY | `At nominal truth this variant's largest residual is \SI{0.39` |
| F239 | IV.E | Fig. 3 caption (b): the joint-test estimator for three shape changes not used while it was chosen, 20 pseudo-experiments each | `(b) The joint-test estimator, for three shape changes not used while it was chosen` && `(NuWro in $\Eavail$; GENIE + MEC in $(\Eavail,W)$; NuWro in $(\pT,\pPar,\Eavail)$), 20 pseudo-experiments each` | PB179 | KEEP | `(b) The joint-test estimator, for three shape changes not us` |
| F240 | IV.E | Fig. 3 caption (b): grey band = the total uncertainty of the (Eavail, W) projection of the earlier purity-subtracted 5D covariance | `the grey band is $\pm$ the total uncertainty of the $(\Eavail,W)$ projection of the covariance of an earlier purity-subtracted five-observable central value (\nsec{sec:eavailw-adopted})` | PB179 | ORDINARY | `(b) The joint-test estimator, for three shape changes not us` |
| F241 | IV.E | Fig. 3 caption: at nominal truth (40 pseudo-experiments) its largest residual is 0.09% | `At nominal truth (40 pseudo-experiments) its largest residual is \SI{0.09}{\percent}` | PB180 | ORDINARY | `At nominal truth (40 pseudo-experiments) its largest residua` |
| F242 | IV.E | Fig. 3 caption: neither seed set was held out from the estimator's development | `Neither seed set was held out from the estimator's development.` | PB181 | HONESTY | `Neither seed set was held out from the estimator's developme` |
| F243 | IV.E | Fig. 3 caption: W bin 6 is W >= 3 GeV | `$W$ bin 6 is $W\ge\SI{3}{GeV}$.` | PB182 | ORDINARY | `$W$ bin 6 is $W\ge\SI{3}{GeV}$.` |
| F244 | IV.E | Fig. 3 caption: error bars are standard errors of the mean; figure label | `Error bars are the standard error of the mean.}` && `\label{fig:deformation}` | PB183 | ORDINARY | `Error bars are the standard error of the mean.} \label{fig:d` |
| F245 | IV.E | Exact-binned diagnostic (binned, signal-only, noise-free; jtNcells joint cells; development truth changes; response fixed at the simulation's): exact binned IBU with five iterations leaves about the same median residual as the boosted-tree estimator | `binned, signal-only and noise-free diagnostic on the \jtNcells{} joint cells and the truth changes used to develop the estimator` && `with the detector response fixed at the simulation's` && `exact binned iterative unfolding with five iterations leaves about the same median residual as the boosted-tree estimator` | PB183 | KEEP | `Error bars are the standard error of the mean.} \label{fig:d` |
| F246 | IV.E | It covers only residuals whose diagnosis is stable under the truth resolution (38% of joint-cell residuals above 2%) | `It covers only the residuals whose diagnosis is stable under the truth resolution (\SI{38}{\percent} of the joint-cell residuals above \SI{2}{\percent})` | PB184 | KEEP | `It covers only the residuals whose diagnosis is stable under` |
| F247 | IV.E | Outside its scope: what unbinned information could recover, the coverage failure, the validity of any interval (source comment: kept verbatim, must stay beside the outcome, DECISION-20261023 item 3b) | `What unbinned information could recover, the coverage failure, and the validity of any interval lie outside its scope.` | PB185 | HONESTY | `What unbinned information could recover, the coverage failur` |
| F248 | IV.E | Within that scope the residual is consistent with regularization of the inverse problem at this binning and prior, not with the tree approximation (source comment: a kept scope sentence) | `Within that scope, the residual is consistent with the regularization of the inverse problem at this binning and prior, rather than with the tree approximation of the classifiers (\nsec{sec:val-departure})` | PB186 | KEEP | `Within that scope, the residual is consistent with the regul` |

## IV F. Coverage (`sec:coverage`)

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F249 | IV.F | Subsection heading and label | `\subsection{Coverage}` && `\label{sec:coverage}` | PB187 | STRUCTURE | `\subsection{Coverage} \label{sec:coverage} Statistical inter` |
| F250 | IV.F | Statistical intervals from a deterministic LightGBM estimator with purity subtraction, corrected for nominal-truth closure bias, miscover at the tested truths, most strongly when the true signal rate is lowered by about 10% | `Statistical intervals from a deterministic LightGBM estimator with purity-based subtraction` && `corrected for the estimator's closure bias at nominal truth` && `miscover at the tested truths` && `true signal rate is lowered by about \SI{10}{\percent}` | PB187 | HONESTY | `\subsection{Coverage} \label{sec:coverage} Statistical inter` |
| F251 | IV.F | Under that change, 51 of 153 reported cell and projection integrals have a 68% coverage whose upper confidence bound is below the 0.66 acceptance threshold; coverage as low as 0.06 | `51 of the 153 reported cell and projection integrals` && `68\% coverage whose upper confidence bound lies below the acceptance threshold of 0.66` && `coverage as low as 0.06` | PB188 | HONESTY | `Under that change, 51 of the 153 reported cell and projectio` |
| F252 | IV.F | The end-to-end test unfolds 400 pseudo-experiments per truth | `end-to-end test` && `400 pseudo-experiments per truth` | PB189 | ORDINARY | `The end-to-end test unfolds 400 pseudo-experiments per truth` |
| F253 | IV.F | A diagnosis attributes the miscoverage to a residual bias growing with W that survives the nominal-truth bias correction | `A diagnosis attributes the miscoverage` && `residual bias that grows with $W$ and survives the nominal-truth bias correction` | PB190 | ORDINARY | `A diagnosis attributes the miscoverage to a residual bias th` |
| F254 | IV.F | The source of this residual bias has not been established | `The source of this residual bias has not been established.` | PB191 | HONESTY | `The source of this residual bias has not been established.` |
| F255 | IV.F | Agreement in the marginal normalizations coexists with substantial residual bias under the tested deformations | `Agreement in the marginal normalizations coexists with substantial residual bias under the tested deformations.` | PB192 | HONESTY | `Agreement in the marginal normalizations coexists with subst` |
| F256 | IV.F | Pointer: interval construction and diagnosis | `The interval construction and the diagnosis are described in \nsec{sec:coverage-5d}` | PB193 | ORDINARY | `The interval construction and the diagnosis are described in` |

## IV G. Estimator stability (`sec:cov5d`)

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F257 | IV.G | Subsection heading and label (the label name does not match the title) | `\subsection{Estimator stability}` && `\label{sec:cov5d}` | PB194 | STRUCTURE | `\subsection{Estimator stability} \label{sec:cov5d} The joint` |
| F258 | IV.G | The joint-test estimator is unstable at the level of rounding | `The joint-test estimator is unstable at the level of rounding.` | PB194 | HONESTY | `\subsection{Estimator stability} \label{sec:cov5d} The joint` |
| F259 | IV.G | Rounding-level input changes move its results by up to 2.6 statistical sigma (the lower-capacity development variant: up to 2.5), failing a data-stability requirement of at most 0.3 (median) and 1.0 (maximum) | `up to 2.6 statistical standard deviations` && `lower-capacity development variant by up to 2.5` && `data-stability requirement of at most 0.3 (median) and 1.0 (maximum) statistical standard deviations` | PB195 | HONESTY | `Rounding-level changes of its inputs move its results by up ` |
| F260 | IV.G | The spread lies inside the data-bootstrap statistical uncertainty but limits how exactly the central values can be reproduced | `This spread lies inside the data-bootstrap statistical uncertainty` && `limits how exactly the central values can be reproduced` | PB196 | KEEP | `This spread lies inside the data-bootstrap statistical uncer` |

## IV H. Fake-data tests of the sixteen-cell result (`sec:fd16`), with Table II (`tab:fd16`)

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F261 | IV.H | Subsection heading and label | `\subsection{Fake-data tests of the sixteen-cell result}` && `\label{sec:fd16}` | PB197 | STRUCTURE | `\subsection{Fake-data tests of the sixteen-cell result} \lab` |
| F262 | IV.H | Pseudo-data are unfolded at f0b-all-truths truths, to compare the estimator's bias with the reported covariance when truth differs from simulation (probed by the paper-protections ledger) | `we unfold pseudo-data at \fvval{f0b-all-truths} truths` && `compare the estimator's bias with the reported covariance when the truth differs from the simulation` | PB197 | ORDINARY | `\subsection{Fake-data tests of the sixteen-cell result} \lab` |
| F263 | IV.H | The mean unfolded result is compared with each truth on the 16 cells by chi2 with 16 dof | `compare the mean unfolded result with each truth on the 16 cells through $\chi^2$ with 16 degrees of freedom` | PB197 | ORDINARY | `\subsection{Fake-data tests of the sixteen-cell result} \lab` |
| F264 | IV.H | The truths are not held out | `The truths are not held out` | PB198 | HONESTY | `The truths are not held out: they are the simulation's prior` |
| F265 | IV.H | Truth list: the simulation's prior; five hybrid truths (definition: a generator prediction on the fine grid with the Tune v1 composition below it) | `they are the simulation's prior` && `five hybrid truths, each a generator prediction on the fine grid with the MINERvA Tune~v1 composition below it` | PB198 | ORDINARY | `The truths are not held out: they are the simulation's prior` |
| F266 | IV.H | Truth list: NuWro shape changes in Eavail and in (pT, ppar, Eavail); a GENIE + MEC shape change in (Eavail, W); a GiBUU-to-GENIE Eavail ratio | `NuWro shape changes in $\Eavail$ and in $(\pT,\pPar,\Eavail)$` && `a GENIE + MEC shape change in $(\Eavail,W)$` && `a GiBUU-to-GENIE $\Eavail$ ratio` | PB198 | ORDINARY | `The truths are not held out: they are the simulation's prior` |
| F267 | IV.H | Truth list: a noise-free closure at the NuWro shape; a synthetic q3 tilt at fixed (Eavail, W) | `a noise-free closure at the NuWro shape` && `a synthetic tilt of the $q_3$ distribution at fixed $(\Eavail,W)$` | PB198 | ORDINARY | `The truths are not held out: they are the simulation's prior` |
| F268 | IV.H | For a truth from a generator contributing to C_model, the covariance omits that generator's component (the table's Cov. column) | `For a truth from a generator that contributes to $C_{\mathrm{model}}$, the covariance omits that generator's component` && `Cov. column of Table~\ref{tab:fd16}` | PB199 | KEEP | `For a truth from a generator that contributes to $C_{\mathrm` |
| F269 | IV.H | Listing criterion: p < trig-p or any cell with abs(z) > trig-z | `A truth is listed when $p<\fvval{trig-p}$ or when a cell has` && `\fvval{trig-z}` | PB200 | ORDINARY | `A truth is listed when $p<\fvval{trig-p}$ or when a cell has` |
| F270 | IV.H | Table II gives the results under the reported covariance and under C_total alone | `Table~\ref{tab:fd16} gives the results under the reported covariance and under $C_{\mathrm{total}}$ alone` | PB201 | ORDINARY | `Table~\ref{tab:fd16} gives the results under the reported co` |
| F271 | IV.H | f0b-nungraded further truths are ungraded and given in the note | `\fvval{f0b-nungraded} further truths are ungraded and given in the note` | PB201 | HONESTY | `Table~\ref{tab:fd16} gives the results under the reported co` |
| F272 | IV.H | Table II float and caption start | `\begin{table*}[tb]` && `\caption{Fake-data tests on the sixteen cells` | PB202 | STRUCTURE | `\begin{table*}[tb] \caption{Fake-data tests on the sixteen c` |
| F273 | IV.H | Table II caption: chi2 (16 dof), p and the cells beyond trig-z, against C_total + C_resp and against C_total, each without the truth's own generator component where the second column says so; label | `$\chi^2$ (16 degrees of freedom), $p$ and the cells with` && `\fvval{trig-z}$, against $C_{\mathrm{total}}+C_{\mathrm{resp}}$ and against $C_{\mathrm{total}}$, each without the truth's own generator component where the second column says so ($-$).}` && `\label{tab:fd16}` | PB202 | ORDINARY | `\begin{table*}[tb] \caption{Fake-data tests on the sixteen c` |
| F274 | IV.H | Table II contents, verbatim (comment-stripped printed form) | `\begin{tabular}{@{}llrrlrrl@{}} \toprule & & \multicolumn{3}{c}{$C_{\mathrm{total}}+C_{\mathrm{resp}}$} & \multicolumn{3}{c}{$C_{\mathrm{total}}$} \\ \cmidrule(lr){3-5}\cmidrule(l){6-8} Truth & Cov. & $\chi^2$ & $p$ & cells & $\chi^2$ & $p$ & cells \\ \midrule simulation prior & full & \fvval{f0b-nominal-chi2} & $\fvval{f0b-nominal-p}$ & \fvval{f0b-nominal-cells} & \fvval{f0-nominal-chi2} & $\fvval{f0-nominal-p}$ & \fvval{f0-nominal-cells} \\ Tune~v1, hybrid & full & \fvval{f0b-A7_mnvtune-chi2} & $\fvval{f0b-A7_mnvtune-p}$ & \fvval{f0b-A7_mnvtune-cells} & \fvval{f0-A7_mnvtune-chi2} & $\fvval{f0-A7_mnvtune-p}$ & \fvval{f0-A7_mnvtune-cells} \\ GENIE CV, hybrid & full & \fvval{f0b-A7_genie_cv-chi2} & $\fvval{f0b-A7_genie_cv-p}$ & \fvval{f0b-A7_genie_cv-cells} & \fvval{f0-A7_genie_cv-chi2} & $\fvval{f0-A7_genie_cv-p}$ & \fvval{f0-A7_genie_cv-cells} \\ GENIE + MEC, hybrid & $-$GENIE + MEC & \fvval{f0b-A7_genie_mec-chi2} & $\fvval{f0b-A7_genie_mec-p}$ & \fvval{f0b-A7_genie_mec-cells} & \fvval{f0-A7_genie_mec-chi2} & $\fvval{f0-A7_genie_mec-p}$ & \fvval{f0-A7_genie_mec-cells} \\ GENIE + MEC, $(\Eavail,W)$ shape & $-$GENIE + MEC & \fvval{f0b-W2-chi2} & $\fvval{f0b-W2-p}$ & \fvval{f0b-W2-cells} & \fvval{f0-W2-chi2} & $\fvval{f0-W2-p}$ & \fvval{f0-W2-cells} \\ NuWro, hybrid & $-$NuWro & \fvval{f0b-A7_nuwro-chi2} & $\fvval{f0b-A7_nuwro-p}$ & \fvval{f0b-A7_nuwro-cells} & \fvval{f0-A7_nuwro-chi2} & $\fvval{f0-A7_nuwro-p}$ & \fvval{f0-A7_nuwro-cells} \\ NuWro, $\Eavail$ shape & $-$NuWro & \fvval{f0b-W1-chi2} & $\fvval{f0b-W1-p}$ & \fvval{f0b-W1-cells} & \fvval{f0-W1-chi2} & $\fvval{f0-W1-p}$ & \fvval{f0-W1-cells} \\ NuWro, $(\pT,\pPar,\Eavail)$ shape & $-$NuWro & \fvval{f0b-W3-chi2} & $\fvval{f0b-W3-p}$ & \fvval{f0b-W3-cells} & \fvval{f0-W3-chi2} & $\fvval{f0-W3-p}$ & \fvval{f0-W3-cells} \\ NuWro, closure & $-$NuWro & \fvval{f0b-closure_nuwro-chi2} & $\fvval{f0b-closure_nuwro-p}$ & \fvval{f0b-closure_nuwro-cells} & \fvval{f0-closure_nuwro-chi2} & $\fvval{f0-closure_nuwro-p}$ & \fvval{f0-closure_nuwro-cells} \\ GiBUU, $\Eavail$ shape & $-$GiBUU & \fvval{f0b-stage0c_gibuu-chi2} & $\fvval{f0b-stage0c_gibuu-p}$ & \fvval{f0b-stage0c_gibuu-cells} & \fvval{f0-stage0c_gibuu-chi2} & $\fvval{f0-stage0c_gibuu-p}$ & \fvval{f0-stage0c_gibuu-cells} \\ GiBUU, hybrid & $-$GiBUU & \fvval{f0b-A7_gibuu-chi2} & $\fvval{f0b-A7_gibuu-p}$ & \fvval{f0b-A7_gibuu-cells} & \fvval{f0-A7_gibuu-chi2} & $\fvval{f0-A7_gibuu-p}$ & \fvval{f0-A7_gibuu-cells} \\ synthetic $q_3$ tilt & full & \fvval{f0b-q3-chi2} & $\fvval{f0b-q3-p}$ & \fvval{f0b-q3-cells} & \fvval{f0-q3-chi2} & $\fvval{f0-q3-p}$ & \fvval{f0-q3-cells} \\ \bottomrule \end{tabular}` | PB202 | STRUCTURE | `\begin{table*}[tb] \caption{Fake-data tests on the sixteen c` |
| F275 | IV.H | Under the reported covariance, without the GiBUU component for the two GiBUU truths, the bias is listed at the GiBUU Eavail shape (cell R06, z value) | `Under the reported covariance, without the GiBUU component for the two GiBUU truths` && `GiBUU $\Eavail$ shape (cell R06, $z=\fvval{f0b-stage0c_gibuu-zmax}$)` | PB202 | ORDINARY | `\begin{table*}[tb] \caption{Fake-data tests on the sixteen c` |
| F276 | IV.H | ... at the GiBUU hybrid truth (p; listed cells) and at the synthetic q3 tilt (p) | `GiBUU hybrid truth ($p=\fvval{f0b-A7_gibuu-p}$; cells \fvval{f0b-A7_gibuu-cells})` && `synthetic $q_3$ tilt ($p=\fvval{f0b-q3-p}$)` | PB202 | ORDINARY | `\begin{table*}[tb] \caption{Fake-data tests on the sixteen c` |
| F277 | IV.H | The reported uncertainty does not cover the fake-data bias at these GiBUU-like truths or at the q3 tilt (probed verbatim by the paper-protections ledger) | `the reported uncertainty does not cover the fake-data bias at these GiBUU-like truths or at the $q_3$ tilt` | PB202 | HONESTY | `\begin{table*}[tb] \caption{Fake-data tests on the sixteen c` |
| F278 | IV.H | At the other f0b-nunlisted truths the bias passes both criteria: no cell beyond trig-z sigma and p >= trig-p | `At the other \fvval{f0b-nunlisted} truths the bias passes both criteria` && `no cell beyond $\fvval{trig-z}\sigma$ and $p\geq\fvval{trig-p}$` | PB203 | KEEP | `At the other \fvval{f0b-nunlisted} truths the bias passes bo` |
| F279 | IV.H | Two GENIE v3 tunes were generated for this test and held out of the analysis (probed verbatim by the paper-protections ledger) | `Two GENIE~v3 tunes, \fvval{f1-tune-g18} and \fvval{f1-tune-ar23}, were generated for this test and held out of the analysis.` | PB204 | KEEP | `Two GENIE~v3 tunes, \fvval{f1-tune-g18} and \fvval{f1-tune-a` |
| F280 | IV.H | Each reweights the simulated truth by its shape ratio to GENIE CV, constructed as for the C_model components | `reweights the simulated truth using its shape ratio to GENIE CV, constructed as for the $C_{\mathrm{model}}$ components` | PB205 | ORDINARY | `Each reweights the simulated truth using its shape ratio to ` |
| F281 | IV.H | The simulated detector response is not probed | `The simulated detector response is not probed.` | PB206 | HONESTY | `The simulated detector response is not probed.` |
| F282 | IV.H | For each tune, f1-n Poisson pseudo-experiments and a noise-free closure are compared with the truth using the full reported covariance | `\fvval{f1-n} Poisson pseudo-experiments and a noise-free closure` && `using the full reported covariance` | PB207 | ORDINARY | `For each tune, \fvval{f1-n} Poisson pseudo-experiments and a` |
| F283 | IV.H | Both tunes satisfy the bias criteria: chi2 and p for each tune's pseudo-experiment means | `Both tunes satisfy the bias criteria` && `$\chi^2=\fvval{f1-g18-chi2}$ ($p=\fvval{f1-g18-p}$)` && `\fvval{f1-ar23-chi2} ($p=\fvval{f1-ar23-p}$)` | PB208 | ORDINARY | `Both tunes satisfy the bias criteria: the pseudo-experiment ` |
| F284 | IV.H | abs(z) <= f1-zmax-ceil in every cell of the means and closures (the paper-protections ledger probes the form beginning "with $" followed by the absolute-value bars) | `\leq\fvval{f1-zmax-ceil}$ in every cell of the means and closures` | PB208 | KEEP | `Both tunes satisfy the bias criteria: the pseudo-experiment ` |
| F285 | IV.H | In cell R11 at the G18 tune, the bias lies below the reported uncertainty only with C_model included | `In cell R11 at \fvval{f1-tune-g18}, the bias lies below the reported uncertainty only with $C_{\mathrm{model}}$ included` | PB209 | KEEP | `In cell R11 at \fvval{f1-tune-g18}, the bias lies below the ` |
| F286 | IV.H | The tunes share a QE model; the G18 tune and the GENIE + MEC component of C_model both use Valencia-family MEC models | `The tunes share a quasielastic cross-section model` && `\fvval{f1-tune-g18} and the GENIE + MEC component of $C_{\mathrm{model}}$ also use Valencia-family MEC models` | PB210 | HONESTY | `The tunes share a quasielastic cross-section model; \fvval{f` |
| F287 | IV.H | These tests provide partial evidence and are not independent | `These tests provide partial evidence and are not independent.` | PB211 | HONESTY | `These tests provide partial evidence and are not independent` |
| F288 | IV.H | Omitting that C_model component gives chi2 (p) for each tune, as a descriptive comparison | `Omitting that $C_{\mathrm{model}}$ component gives $\chi^2=\fvval{f1-g18-sens-chi2}$ ($p=\fvval{f1-g18-sens-p}$) and \fvval{f1-ar23-sens-chi2} ($p=\fvval{f1-ar23-sens-p}$)` && `as a descriptive comparison` | PB212 | KEEP | `Omitting that $C_{\mathrm{model}}$ component gives $\chi^2=\` |
| F289 | IV.H | The tests assess bias, not coverage: only event counts fluctuate, systematic parameters fixed, so interval widths cannot be tested (probed verbatim by the paper-protections ledger) | `The tests assess bias, not coverage: only event counts fluctuate, with systematic parameters fixed, so interval widths cannot be tested.` | PB213 | HONESTY | `The tests assess bias, not coverage: only event counts fluct` |

## V. The sixteen-cell cross section (`sec:result16`): V A Result (no label), with Table III (`tab:result16`)

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F290 | V | Section heading and label | `\section{The sixteen-cell cross section}` && `\label{sec:result16}` | PB214 | STRUCTURE | `\section{The sixteen-cell cross section} \label{sec:result16` |
| F291 | V.A | Subsection heading (no label) | `\subsection{Result}` | PB214 | STRUCTURE | `\section{The sixteen-cell cross section} \label{sec:result16` |
| F292 | V.A | Table III gives, for each cell R00-R15, its five-observable box, the cell-integrated cross section f, and its marginal relative uncertainty under C_total + C_resp | `Table~\ref{tab:result16} gives the sixteen-cell cross section` && `its box in the five observables, the cell-integrated cross section $f$` && `marginal relative uncertainty under the reported covariance $C_{\mathrm{total}}+C_{\mathrm{resp}}$ of Sec.~\ref{sec:cov16}` | PB214 | ORDINARY | `\section{The sixteen-cell cross section} \label{sec:result16` |
| F293 | V.A | The cells are correlated, so quantitative comparisons need the full covariance; its correlation matrix is in the note's table | `The cells are correlated, so quantitative comparisons need the full covariance` && `Ref.~\cite{AnalysisNote2026}, Table~\ref*{N-tab:fived16-corr}` | PB215 | KEEP | `The cells are correlated, so quantitative comparisons need t` |
| F294 | V.A | The note's cells table gives the uncertainties under C_total and C_resp separately | `Table~\ref*{N-tab:fived16-cells} there gives the uncertainties under $C_{\mathrm{total}}$ and $C_{\mathrm{resp}}$ separately` | PB215 | ORDINARY | `The cells are correlated, so quantitative comparisons need t` |
| F295 | V.A | Table III float | `\begin{table*}[t]` | PB216 | STRUCTURE | `\begin{table*}[t] \caption{The sixteen-cell cross section: e` |
| F296 | V.A | Table III caption: box units (pT, ppar, q3 in GeV/c; Eavail, W in GeV) | `\caption{The sixteen-cell cross section: each cell's box ($\pT$, $\pPar$ and $q_{3}$ in GeV/$c$; $\Eavail$ and $W$ in GeV)` | PB216 | ORDINARY | `\begin{table*}[t] \caption{The sixteen-cell cross section: e` |
| F297 | V.A | Table III caption: f is an integral over the box, not a differential density, in units of f-unit cm^2/nucleon | `(an integral over the box, not a differential density)` && `in units of $\fvval{f-unit}\,\si{cm^2/nucleon}$` | PB216 | KEEP | `\begin{table*}[t] \caption{The sixteen-cell cross section: e` |
| F298 | V.A | Table III caption: sigma/f (%) is the square root of the diagonal of C_total + C_resp over f | `marginal relative uncertainty $\sigma/f$ (\%), the square root of the diagonal of $C_{\mathrm{total}}+C_{\mathrm{resp}}$ over $f$` | PB216 | ORDINARY | `\begin{table*}[t] \caption{The sixteen-cell cross section: e` |
| F299 | V.A | Table III caption: the largest edge on each axis is the outer edge of the analysis grid, which contains every signal event | `The largest edge on each axis is the outer edge of the analysis grid, which contains every signal event (\nsec{sec:method-binning})` | PB217 | ORDINARY | `The largest edge on each axis is the outer edge of the analy` |
| F300 | V.A | Table III caption: the last row is the median over the cells | `The last row gives the median over the cells.` | PB218 | ORDINARY | `The last row gives the median over the cells.` |
| F301 | V.A | Table III caption: quantitative comparisons need the full covariance; label | `Quantitative comparisons need the full covariance (Sec.~\ref{sec:cov16}).}` && `\label{tab:result16}` | PB219 | KEEP | `Quantitative comparisons need the full covariance (Sec.~\ref` |
| F302 | V.A | Table III contents, verbatim (comment-stripped printed form) | `\begin{tabular}{@{}lcccccrr@{}} \toprule cell & $\pT$ & $\pPar$ & $\Eavail$ & $q_{3}$ & $W$ & $f$ & marginal $\sigma/f$ \\ \midrule R00 & \fvval{box-R00-pt} & \fvval{box-R00-pz} & \fvval{box-R00-eavail} & \fvval{box-R00-q3} & \fvval{box-R00-W} & \fvval{f-R00} & \fvval{sig-C_total_resp-R00} \\ R01 & \fvval{box-R01-pt} & \fvval{box-R01-pz} & \fvval{box-R01-eavail} & \fvval{box-R01-q3} & \fvval{box-R01-W} & \fvval{f-R01} & \fvval{sig-C_total_resp-R01} \\ R02 & \fvval{box-R02-pt} & \fvval{box-R02-pz} & \fvval{box-R02-eavail} & \fvval{box-R02-q3} & \fvval{box-R02-W} & \fvval{f-R02} & \fvval{sig-C_total_resp-R02} \\ R03 & \fvval{box-R03-pt} & \fvval{box-R03-pz} & \fvval{box-R03-eavail} & \fvval{box-R03-q3} & \fvval{box-R03-W} & \fvval{f-R03} & \fvval{sig-C_total_resp-R03} \\ R04 & \fvval{box-R04-pt} & \fvval{box-R04-pz} & \fvval{box-R04-eavail} & \fvval{box-R04-q3} & \fvval{box-R04-W} & \fvval{f-R04} & \fvval{sig-C_total_resp-R04} \\ R05 & \fvval{box-R05-pt} & \fvval{box-R05-pz} & \fvval{box-R05-eavail} & \fvval{box-R05-q3} & \fvval{box-R05-W} & \fvval{f-R05} & \fvval{sig-C_total_resp-R05} \\ R06 & \fvval{box-R06-pt} & \fvval{box-R06-pz} & \fvval{box-R06-eavail} & \fvval{box-R06-q3} & \fvval{box-R06-W} & \fvval{f-R06} & \fvval{sig-C_total_resp-R06} \\ R07 & \fvval{box-R07-pt} & \fvval{box-R07-pz} & \fvval{box-R07-eavail} & \fvval{box-R07-q3} & \fvval{box-R07-W} & \fvval{f-R07} & \fvval{sig-C_total_resp-R07} \\ R08 & \fvval{box-R08-pt} & \fvval{box-R08-pz} & \fvval{box-R08-eavail} & \fvval{box-R08-q3} & \fvval{box-R08-W} & \fvval{f-R08} & \fvval{sig-C_total_resp-R08} \\ R09 & \fvval{box-R09-pt} & \fvval{box-R09-pz} & \fvval{box-R09-eavail} & \fvval{box-R09-q3} & \fvval{box-R09-W} & \fvval{f-R09} & \fvval{sig-C_total_resp-R09} \\ R10 & \fvval{box-R10-pt} & \fvval{box-R10-pz} & \fvval{box-R10-eavail} & \fvval{box-R10-q3} & \fvval{box-R10-W} & \fvval{f-R10} & \fvval{sig-C_total_resp-R10} \\ R11 & \fvval{box-R11-pt} & \fvval{box-R11-pz} & \fvval{box-R11-eavail} & \fvval{box-R11-q3} & \fvval{box-R11-W} & \fvval{f-R11} & \fvval{sig-C_total_resp-R11} \\ R12 & \fvval{box-R12-pt} & \fvval{box-R12-pz} & \fvval{box-R12-eavail} & \fvval{box-R12-q3} & \fvval{box-R12-W} & \fvval{f-R12} & \fvval{sig-C_total_resp-R12} \\ R13 & \fvval{box-R13-pt} & \fvval{box-R13-pz} & \fvval{box-R13-eavail} & \fvval{box-R13-q3} & \fvval{box-R13-W} & \fvval{f-R13} & \fvval{sig-C_total_resp-R13} \\ R14 & \fvval{box-R14-pt} & \fvval{box-R14-pz} & \fvval{box-R14-eavail} & \fvval{box-R14-q3} & \fvval{box-R14-W} & \fvval{f-R14} & \fvval{sig-C_total_resp-R14} \\ R15 & \fvval{box-R15-pt} & \fvval{box-R15-pz} & \fvval{box-R15-eavail} & \fvval{box-R15-q3} & \fvval{box-R15-W} & \fvval{f-R15} & \fvval{sig-C_total_resp-R15} \\ \midrule median & \multicolumn{6}{c}{} & \fvval{sigmed-C_total_resp} \\ \bottomrule \end{tabular}` | PB219 | STRUCTURE | `Quantitative comparisons need the full covariance (Sec.~\ref` |

## V B. Comparison on the sixteen reported cells (`sec:gen16`), with Fig. 4 (`fig:ratio16`) and Table IV (`tab:gen16`)

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F303 | V.B | Subsection heading and label | `\subsection{Comparison on the sixteen reported cells}` && `\label{sec:gen16}` | PB219 | STRUCTURE | `Quantitative comparisons need the full covariance (Sec.~\ref` |
| F304 | V.B | Unfolded results can be compared with any prediction at truth level without simulating each generator through the detector | `compared with any prediction at truth level without simulating each generator through the detector` | PB219 | ORDINARY | `Quantitative comparisons need the full covariance (Sec.~\ref` |
| F305 | V.B | That makes the 2D result reusable, the higher-dimensional central values usable for qualitative comparison, and the sixteen-cell result usable for the comparison that follows | `two-dimensional result reusable` && `the higher-dimensional central values usable for qualitative comparison` && `sixteen-cell result usable for the comparison that follows` | PB219 | KEEP | `Quantitative comparisons need the full covariance (Sec.~\ref` |
| F306 | V.B | Table IV compares the sixteen-cell result with five predictions by chi2 against the reported covariance plus each prediction's finite-sample diagonal covariance V_g, with shape-only chi2 beside | `Table~\ref{tab:gen16} compares the sixteen-cell result of Sec.~\ref{sec:result16} with five predictions` && `reported covariance plus each prediction's finite-sample (diagonal) covariance $V_g$` && `shape-only $\chi^2$ beside it` | PB220 | ORDINARY | `Table~\ref{tab:gen16} compares the sixteen-cell result of Se` |
| F307 | V.B | Fig. 4 shows data over each prediction, cell by cell | `Figure~\ref{fig:ratio16} shows the data over each prediction, cell by cell` | PB221 | ORDINARY | `Figure~\ref{fig:ratio16} shows the data over each prediction` |
| F308 | V.B | GiBUU's sample stops at Enu = cmodel-gibuu-enu GeV, so GiBUU is compared on the 8 cells with ppar < h2-mid-pz GeV/c only | `GiBUU's sample stops at $E_\nu=\fvval{cmodel-gibuu-enu}$~GeV` && `compared on the 8 cells with $\pPar<\fvval{h2-mid-pz}$~GeV/$c$ only` | PB222 | KEEP | `GiBUU's sample stops at $E_\nu=\fvval{cmodel-gibuu-enu}$~GeV` |
| F309 | V.B | NuWro and GiBUU are on carbon with no correction to CH | `NuWro and GiBUU are on carbon, with no correction to CH` | PB223 | HONESTY | `NuWro and GiBUU are on carbon, with no correction to CH, and` |
| F310 | V.B | MINERvA Tune v1 is the simulation's prior | `MINERvA Tune~v1 is the simulation's prior` | PB223 | HONESTY | `NuWro and GiBUU are on carbon, with no correction to CH, and` |
| F311 | V.B | The GENIE + MEC, NuWro and GiBUU comparisons use covariance contributions derived from those generators; GENIE CV is their common reference | `The GENIE + MEC, NuWro and GiBUU comparisons use covariance contributions derived from those generators` && `GENIE CV enters as their common reference` | PB224 | HONESTY | `The GENIE + MEC, NuWro and GiBUU comparisons use covariance ` |
| F312 | V.B | Fig. 4 float and graphic | `\begin{figure*}[tb]` && `\includegraphics[width=0.86\textwidth]{fd_g_fig_ratio}` | PB225 | STRUCTURE | `\begin{figure*}[tb] \centering \includegraphics[width=0.86\t` |
| F313 | V.B | Fig. 4 caption: data over prediction f/g on the sixteen cells for the five predictions | `\caption{Data over prediction, $f/g$, on the sixteen cells for the five predictions of Table~\ref{tab:gen16}.` | PB225 | ORDINARY | `\begin{figure*}[tb] \centering \includegraphics[width=0.86\t` |
| F314 | V.B | Fig. 4 caption: error bar (f/g) sigma/f with sigma from the diagonal of C_total + C_resp; prediction uncertainties not drawn | `Each error bar is $(f/g)\,\sigma/f$, with $\sigma$ the square root of the diagonal of $C_{\mathrm{total}}+C_{\mathrm{resp}}$` && `the predictions' finite-sample uncertainties are not drawn` | PB226 | KEEP | `Each error bar is $(f/g)\,\sigma/f$, with $\sigma$ the squar` |
| F315 | V.B | Fig. 4 caption: GiBUU (lower panel) shown on its 8 cells only | `GiBUU (lower panel) is shown on its 8 cells with $\pPar<\fvval{h2-mid-pz}$~GeV/$c$ only.` | PB227 | ORDINARY | `GiBUU (lower panel) is shown on its 8 cells with $\pPar<\fvv` |
| F316 | V.B | Fig. 4 caption: the key below the axes gives each cell's box | `The key below the axes gives each cell's box.` | PB228 | ORDINARY | `The key below the axes gives each cell's box.` |
| F317 | V.B | Fig. 4 caption: Table IV's chi2 uses the full covariance, whose correlations the error bars do not show; label | `The $\chi^2$ of Table~\ref{tab:gen16} uses the full covariance, whose correlations the error bars do not show.}` && `\label{fig:ratio16}` | PB229 | KEEP | `The $\chi^2$ of Table~\ref{tab:gen16} uses the full covarian` |
| F318 | V.B | Table IV float | `\begin{table}[tb]` | PB229 | STRUCTURE | `The $\chi^2$ of Table~\ref{tab:gen16} uses the full covarian` |
| F319 | V.B | Table IV caption: chi2 and ndf of each prediction under C_total + C_resp + V_g; shape-only chi2 frees the normalization; label | `\caption{$\chi^2$ and its number of degrees of freedom of each prediction against the sixteen-cell result, under $C_{\mathrm{total}}+C_{\mathrm{resp}}+V_g$, with $V_g$ the prediction's finite-sample (diagonal) covariance; shape-only $\chi^2$ frees the normalization.}` && `\label{tab:gen16}` | PB229 | ORDINARY | `The $\chi^2$ of Table~\ref{tab:gen16} uses the full covarian` |
| F320 | V.B | Table IV contents, verbatim (comment-stripped printed form) | `\begin{tabular}{@{}lcc@{}} \toprule Prediction & $\chi^2$ and ndf & shape-only \\ \midrule \fvval{label-gcv} & \fvval{g-gcv-total-chi2int}/\fvval{g-gcv-total-ndf} & \fvval{g-gcv-shape_only-chi2int}/\fvval{g-gcv-shape_only-ndf} \\ \fvval{label-gmec} & \fvval{g-gmec-total-chi2int}/\fvval{g-gmec-total-ndf} & \fvval{g-gmec-shape_only-chi2int}/\fvval{g-gmec-shape_only-ndf} \\ \fvval{label-nuwro} & \fvval{g-nuwro-total-chi2int}/\fvval{g-nuwro-total-ndf} & \fvval{g-nuwro-shape_only-chi2int}/\fvval{g-nuwro-shape_only-ndf} \\ \fvval{label-gibuu} & \fvval{g-gibuu-total-chi2int}/\fvval{g-gibuu-total-ndf} & \fvval{g-gibuu-shape_only-chi2int}/\fvval{g-gibuu-shape_only-ndf} \\ \fvval{label-tune} & \fvval{g-tune-total-chi2int}/\fvval{g-tune-total-ndf} & \fvval{g-tune-shape_only-chi2int}/\fvval{g-tune-shape_only-ndf} \\ \bottomrule \end{tabular}` | PB229 | STRUCTURE | `The $\chi^2$ of Table~\ref{tab:gen16} uses the full covarian` |
| F321 | V.B | Weakening only the flux correlations by sens-alpha-pct % lowers the 16-cell chi2 by sens-flux-fall-lo to -hi % (probed verbatim by the paper-protections ledger) | `Weakening only the flux correlations by \fvval{sens-alpha-pct}\,\% lowers the $\chi^2$ of the 16-cell predictions by \fvval{sens-flux-fall-lo}--\fvval{sens-flux-fall-hi}\,\%.` | PB229 | ORDINARY | `The $\chi^2$ of Table~\ref{tab:gen16} uses the full covarian` |
| F322 | V.B | The same change to the detector or lateral correlations lowers it by at most sens-detlat-fall-max % | `The same change to the detector or lateral correlations lowers it by at most \fvval{sens-detlat-fall-max}\,\%` | PB230 | ORDINARY | `The same change to the detector or lateral correlations lowe` |
| F323 | V.B | With interaction, flux, detector and lateral correlations removed, every 16-cell prediction keeps chi2 >= sens-joint-chi2-min for 16 dof | `With the correlations of the interaction, flux, detector and lateral groups removed, every 16-cell prediction keeps $\chi^2\geq\fvval{sens-joint-chi2-min}$ for 16 degrees of freedom` | PB231 | ORDINARY | `With the correlations of the interaction, flux, detector and` |
| F324 | V.B | Flux correlations are estimated from fb-universes PPFX flux universes, weighted by the nu-e and inverse-muon-decay constraint | `estimated from \fvval{fb-universes} hadron-production (PPFX) flux universes~\cite{MINERvA:2016iqn}` && `weighted by the neutrino--electron and inverse-muon-decay constraint` | PB232 | ORDINARY | `The flux correlations are estimated from \fvval{fb-universes` |
| F325 | V.B | Bootstrapping the universes (flux variances kept) gives fb-plo to fb-phi percentile bands per chi2, edges within fb-edge-max % of the reported value, median at most fb-offset-relmax % above it | `Bootstrapping these universes, with the flux variances kept` && `\fvval{fb-plo}th--\fvval{fb-phi}th percentile bands for each 16-cell $\chi^2$` && `edges within \fvval{fb-edge-max}\,\% of the reported value` && `a median at most \fvval{fb-offset-relmax}\,\% above it` | PB233 | ORDINARY | `Bootstrapping these universes, with the flux variances kept,` |
| F326 | V.B | The bands describe chi2 scatter from estimating the correlations with these universes, not sensitivity to incorrect correlations (which the weakening probes); they are not intervals for chi2 under the true correlations | `These bands describe the scatter of the $\chi^2$ from estimating the correlations with these universes, not its sensitivity to incorrect correlations, which the weakening probes` && `they are not intervals for the $\chi^2$ under the true correlations` | PB234 | KEEP | `These bands describe the scatter of the $\chi^2$ from estima` |

## V C. Descriptive comparison of the central values (`sec:central`)

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F327 | V.C | Subsection heading and label | `\subsection{Descriptive comparison of the central values}` && `\label{sec:central}` | PB235 | STRUCTURE | `\subsection{Descriptive comparison of the central values} \l` |
| F328 | V.C | These comparisons use the 3D and 4D central values of the joint-test estimator, without uncertainties (probed verbatim by the paper-protections ledger) | `These comparisons use the three- and four-observable central values of the joint-test estimator, without uncertainties.` | PB235 | KEEP | `\subsection{Descriptive comparison of the central values} \l` |
| F329 | V.C | GENIE, Tune v1, NuWro and GiBUU all underpredict the unfolded central value at low Eavail, between the QE and Delta peaks, the region of the established low-recoil discrepancy | `GENIE, the MINERvA Tune~v1, NuWro, and GiBUU all underpredict the unfolded central value at low $\Eavail$` && `between the quasielastic and $\Delta$ peaks` && `established low-recoil discrepancy~\cite{MINERvA:2016lowrecoil,MINERvA:2022incl}` | PB236 | ORDINARY | `GENIE, the MINERvA Tune~v1, NuWro, and GiBUU all underpredic` |
| F330 | V.C | Pointer: comparisons with pion FSI variations, GENIE's Valencia 2p2h component and the published measurement | `pion final-state-interaction variations, GENIE's Valencia 2p2h component, and the published measurement` && `Ref.~\cite{AnalysisNote2026}, Secs.~\ref*{N-sec:3d-2p2h} and~\ref*{N-sec:4d}` | PB237 | ORDINARY | `Comparisons with pion final-state-interaction variations, GE` |
| F331 | V.C | Pointer: the 5D (Eavail, W) map of the earlier purity-subtracted central value and its generator comparisons | `five-observable $(\Eavail,W)$ map of the earlier purity-subtracted central value` && `Ref.~\cite{AnalysisNote2026}, Secs.~\ref*{N-sec:eavailw-map} and~\ref*{N-sec:eavailw-band}` | PB238 | ORDINARY | `The five-observable $(\Eavail,W)$ map of the earlier purity-` |

## VI. Discussion and conclusions (`sec:conclusions`; also the bare label `sec:limits`)

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F332 | VI | Section heading and label | `\section{Discussion and conclusions}` && `\label{sec:conclusions}` | PB239 | STRUCTURE | `\section{Discussion and conclusions} \label{sec:conclusions}` |
| F333 | VI | The principal result is the sixteen-cell cross section, with its covariance and generator comparison | `The principal result is the sixteen-cell cross section of Sec.~\ref{sec:result16}, with its covariance and generator comparison` | PB239 | ORDINARY | `\section{Discussion and conclusions} \label{sec:conclusions}` |
| F334 | VI | A bare label between paragraphs, not attached to a heading (it resolves to Sec. VI) | `\label{sec:limits}` | PB240 | STRUCTURE | `\label{sec:limits} Two validation findings point to the unfo` |
| F335 | VI | Two validation findings point to the unfolded result retaining part of its prior | `Two validation findings point to the unfolded result retaining part of its prior` | PB240 | ORDINARY | `\label{sec:limits} Two validation findings point to the unfo` |
| F336 | VI | First: the residual under a generator-sized truth change, interpreted as regularization bias | `residual under a generator-sized change of the truth in Sec.~\ref{sec:departure}, which we interpret as regularization bias` | PB241 | KEEP | `The first is the residual under a generator-sized change of ` |
| F337 | VI | Second: the envelope, which tracks the same bias and alone exceeds the precision target in two of the three tested reporting definitions | `envelope of Sec.~\ref{sec:uncertainty-status}, which tracks the same bias and alone exceeds the precision target in two of the three tested reporting definitions` | PB242 | ORDINARY | `The second is the envelope of Sec.~\ref{sec:uncertainty-stat` |
| F338 | VI | The note's calibrated tests show the same pull: their null distributions for the external predictions are displaced upward by it, as the calibration reproduces | `The note's calibrated tests show the same pull` && `null distributions for the external predictions are displaced upward by it, as the calibration reproduces (\nsec{sec:joint5d-results})` | PB243 | ORDINARY | `The note's calibrated tests show the same pull: their null d` |
| F339 | VI | The miscoverage is also attributed to a residual bias, but whether it has the same origin is not established | `The miscoverage of Sec.~\ref{sec:coverage} is also attributed to a residual bias, but whether that bias has the same origin is not established` | PB244 | HONESTY | `The miscoverage of Sec.~\ref{sec:coverage} is also attribute` |
| F340 | VI | What must be checked before interpreting unfolded intervals: closure with backgrounds; generator-sized truth changes, not only nominal closure; coverage under truth changes, not only at nominal truth; stability under seeds and rounding-level input changes; run-period consistency | `The studies of Sec.~\ref{sec:validation} show what must be checked before unfolded intervals are interpreted` && `closure with the backgrounds included; truth changes of generator size, not only nominal closure; coverage under changes of the truth, not only at nominal truth; stability under training seeds and rounding-level input changes; and run-period consistency` | PB245 | ORDINARY | `The studies of Sec.~\ref{sec:validation} show what must be c` |

## VI A. Limitations (`sec:limitations`)

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F341 | VI.A | Subsection heading and label | `\subsection{Limitations}` && `\label{sec:limitations}` | PB246 | STRUCTURE | `\subsection{Limitations} \label{sec:limitations} The limitat` |
| F342 | VI.A | The limitations are stated with the results they qualify, in Secs. III-V, and those of the calibrated tests in the companion note | `stated with the results they qualify, in Secs.~\ref{sec:method}--\ref{sec:result16}` && `those of the calibrated tests in the companion note` | PB246 | ORDINARY | `\subsection{Limitations} \label{sec:limitations} The limitat` |
| F343 | VI.A | Introduces the principal ones | `The principal ones are these.` | PB247 | ORDINARY | `The principal ones are these.` |
| F344 | VI.A | The 2D covariance has not been independently validated and its coverage has not been tested | `The two-dimensional covariance has not been independently validated, and its coverage has not been tested (Sec.~\ref{sec:uq2d})` | PB248 | HONESTY | `The two-dimensional covariance has not been independently va` |
| F345 | VI.A | The 3D and 4D central values lack intervals of validated coverage (probed verbatim by the paper-protections ledger) | `The three- and four-observable central values lack intervals of validated coverage (Sec.~\ref{sec:central}).` | PB249 | HONESTY | `The three- and four-observable central values lack intervals` |
| F346 | VI.A | The sixteen-cell result also has total uncertainties, whose coverage is not validated; pointer to its fake-data bias tests (probed verbatim by the paper-protections ledger) | `The sixteen-cell result also has total uncertainties, whose coverage is not validated; Sec.~\ref{sec:fd16} reports the fake-data tests of the estimator's bias.` | PB250 | HONESTY | `The sixteen-cell result also has total uncertainties, whose ` |
| F347 | VI.A | Four of the sixteen cells have stability h2-lowstab-min to -max, with the definition of stability (probed verbatim as ledger row L1 of the paper-protections ledger) | `Four of the sixteen cells, \fvval{h2-lowstab-cells}, have a stability of \fvval{h2-lowstab-min}--\fvval{h2-lowstab-max}: of the simulated signal events generated in such a cell and reconstructed, only that fraction is reconstructed in the same cell.` | PB251 | HONESTY | `Four of the sixteen cells, \fvval{h2-lowstab-cells}, have a ` |
| F348 | VI.A | The note's calibrated tests reject hybrid nulls, conditionally on the simulation's hadronic response (probed verbatim) | `The note's calibrated tests reject hybrid nulls, conditionally on the simulation's hadronic response` | PB252 | KEEP | `The note's calibrated tests reject hybrid nulls, conditional` |
| F349 | VI.A | The rejections carry over to the generator predictions themselves only under a bound on the residual below the fine grid, which has not been shown | `the rejections carry over to the generator predictions themselves only under a bound on the residual below the fine grid, which has not been shown` | PB252 | HONESTY | `The note's calibrated tests reject hybrid nulls, conditional` |
| F350 | VI.A | Their calibration is valid to the extent the simulated chain reproduces the analysis of the data (pointer; probed verbatim) | `Their calibration is valid to the extent that the simulated chain reproduces the analysis of the data` && `\nsec{sec:joint5d-conditions}` | PB253 | KEEP | `Their calibration is valid to the extent that the simulated ` |
| F351 | VI.A | They are not physical exclusions of the generators (probed verbatim) | `They are not physical exclusions of the generators` | PB254 | KEEP | `They are not physical exclusions of the generators, and they` |
| F352 | VI.A | They show no evidence of additional discrimination beyond matched coarse projections (probed verbatim) | `they show no evidence of additional discrimination beyond matched coarse projections.` | PB254 | KEEP | `They are not physical exclusions of the generators, and they` |
<!-- absence-ok: quotes printed limitation sentences of the paper as facts to restate; not a claim that a result does not exist -->

## PROTECTED: main_paper.tex (out of scope; byte-identical; not outlined)

Base ids here are MP<n>: the same sentence split, applied to main_paper.tex. These rows are not facts for the writer to restate; they name what must not change.

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| F353 | MP | The pubhold macro definition line (protected with every hold) | `\newcommand{\pubhold}[1]{\textcolor{red}{[HOLD: #1]}}` | MP0 | PROTECTED | `\documentclass[aps,prd,reprint,superscriptaddress,nofootinbi` |
| F354 | MP | Title | `\title{Simultaneous measurement of the $\nu_{\mu}$ charged-current inclusive cross section on hydrocarbon in five observables from MINERvA open data}` | MP0 | PROTECTED | `\documentclass[aps,prd,reprint,superscriptaddress,nofootinbi` |
| F355 | MP | Abstract, sentence 1 | `\begin{abstract}` && `We report a simultaneous measurement of the $\nu_{\mu}$ charged-current inclusive cross section in five observables` | MP0 | PROTECTED | `\documentclass[aps,prd,reprint,superscriptaddress,nofootinbi` |
| F356 | MP | Abstract, sentence 2 | `Three external generator predictions compared on all sixteen cells give $\chi^{2}$ of \fvval{g-ext-chi2int-min16}--\fvval{g-ext-chi2int-max16} for 16 degrees of freedom` | MP1 | PROTECTED | `Three external generator predictions compared on all sixteen` |
| F357 | MP | Abstract, sentence 3 | `In a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic $q_{3}$ tilt.` | MP2 | PROTECTED | `In a fake-data study, the reported uncertainty does not cove` |
| F358 | MP | Abstract, sentence 4, and its end | `The same unfolding reproduces the integral of the published muon-kinematic cross section within about 1\%, with a correlated shape difference.` | MP3 | PROTECTED | `The same unfolding reproduces the integral of the published ` |
| F359 | MP | Acknowledgments, sentence 1 (MINERvA data and tools) | `\end{abstract}` && `\begin{acknowledgments}` && `The authors thank the MINERvA Collaboration` | MP4 | PROTECTED | `\end{abstract} \maketitle \input{paper_body} \begin{acknowle` |
| F360 | MP | Acknowledgments, sentence 2 | `We thank Callum Wilkinson` | MP5 | PROTECTED | `We thank Callum Wilkinson for connecting us with this datase` |
| F361 | MP | Acknowledgments, sentence 3 | `under project m3246` | MP6 | PROTECTED | `This research used resources of the National Energy Research` |
| F362 | MP | Funding hold | `\pubhold{funding and grant acknowledgments}` | MP7 | PROTECTED | `\pubhold{funding and grant acknowledgments} AI language-mode` |
| F363 | MP | AI statement, sentence 1 | `AI language-model tools (Anthropic Claude and OpenAI GPT models` | MP7 | PROTECTED | `\pubhold{funding and grant acknowledgments} AI language-mode` |
| F364 | MP | AI statement, sentence 2 | `The authors directed the work and verified the results` | MP8 | PROTECTED | `The authors directed the work and verified the results; the ` |
| F365 | MP | AI statement, sentence 3 | `no figure was generated or edited by a generative-AI image tool` | MP9 | PROTECTED | `The figures were drawn by plotting code from the analysis ou` |
| F366 | MP | AI statement, sentence 4 | `AI tools are not authors, and the authors take responsibility for the content.` | MP10 | PROTECTED | `AI tools are not authors, and the authors take responsibilit` |
| F367 | MP | Data Availability heading and sentence 1 (CC0) | `\section*{Data availability}` && `\label{sec:data-availability}` && `released under CC0~\cite{MINERvA:OpenData}` | MP11 | PROTECTED | `\end{acknowledgments} \section*{Data availability} \label{se` |
| F368 | MP | Data Availability, Supplemental Material sentence | `provided as machine-readable files in the Supplemental Material` | MP12 | PROTECTED | `The sixteen-cell cross section, its covariance matrix and th` |
| F369 | MP | Data Availability, input-file sentence | `its 2,374 input files are identified by SHA256 checksum in the records cited in \napp{app:release}` | MP13 | PROTECTED | `This analysis used an earlier production of that release; it` |
| F370 | MP | Data Availability, candidate package sentence | `A candidate release package of about \SI{16}{MB}, not yet deposited` | MP14 | PROTECTED | `A candidate release package of about \SI{16}{MB}, not yet de` |
| F371 | MP | Data Availability, reproducibility sentence | `The paper's quoted numbers and the event-level processing require the archived analysis products` | MP15 | PROTECTED | `The paper's quoted numbers and the event-level processing re` |
| F372 | MP | Deposit hold | `\pubhold{deposit identifier and access route, after the separately authorized release decision.}` | MP16 | PROTECTED | `\pubhold{deposit identifier and access route, after the sepa` |

## PLANTED (a deliberately false row: the downstream checker must reject it)

| id | section | fact | atoms | base | status | base text |
|---|---|---|---|---|---|---|
| FX | VI.A | Planted false fact: this atom prints nowhere | `@@PLANTED@@` | PB15 | PLANTED | `Interval coverage has not been validated.` |

## Appendix: macro values at b70156a1 (for reading only)

The paper prints the macro, never the value. `\fvval` keys are from values_fived16.tex (generated by
make_values_fived16.py); plain macros are from values.tex and values_inference.tex. In first-use order.

```
\jtNcells = 109    [values_inference.tex]
\sigTwoD = 3.069e-38    [values.tex]
\sigTwoDpaper = 3.039e-38    [values.tex]
\ratioTot = 1.010    [values.tex]
\pullRMS = 0.535    [values.tex]
\chiPaper = 2.27    [values.tex]
\uqMedian = 6.41    [values.tex]
\uqIntegral = 4.76    [values.tex]
\uqPaper = 6.85    [values.tex]
\uqPaperIntegral = 4.61    [values.tex]
\fluxBand = 3.71    [values.tex]
\cmodelMedian = 3.71    [values.tex]
\qrCmodelMedian = 7.90    [values.tex]
\fvval{h2-nboxes} = 32
\fvval{h2-mid-pt} = 0.7
\fvval{h2-mid-pz} = 4.5
\fvval{h2-mid-q3} = 2
\fvval{h2-mid-eavail} = 0.8
\fvval{h2-mid-W} = 1.8
\fvval{h2-tau} = 0.1
\fvval{h2-nunreported} = 4
\fvval{sigmed-C_total_resp} = 7.29
\fvval{sigmed-C_total} = 6.74
\fvval{f0b-all-truths} = 12
\fvval{trig-p} = 0.01
\fvval{trig-z} = 2
\fvval{f0b-nungraded} = 6
\fvval{f0b-nominal-chi2} = 0.00
\fvval{f0b-nominal-p} = 1.00
\fvval{f0b-nominal-cells} = ---
\fvval{f0-nominal-chi2} = 0.00
\fvval{f0-nominal-p} = 1.00
\fvval{f0-nominal-cells} = ---
\fvval{f0b-A7_mnvtune-chi2} = 0.01
\fvval{f0b-A7_mnvtune-p} = 1.00
\fvval{f0b-A7_mnvtune-cells} = ---
\fvval{f0-A7_mnvtune-chi2} = 0.01
\fvval{f0-A7_mnvtune-p} = 1.00
\fvval{f0-A7_mnvtune-cells} = ---
\fvval{f0b-A7_genie_cv-chi2} = 16.14
\fvval{f0b-A7_genie_cv-p} = 0.44
\fvval{f0b-A7_genie_cv-cells} = ---
\fvval{f0-A7_genie_cv-chi2} = 17.37
\fvval{f0-A7_genie_cv-p} = 0.36
\fvval{f0-A7_genie_cv-cells} = ---
\fvval{f0b-A7_genie_mec-chi2} = 14.54
\fvval{f0b-A7_genie_mec-p} = 0.56
\fvval{f0b-A7_genie_mec-cells} = ---
\fvval{f0-A7_genie_mec-chi2} = 16.18
\fvval{f0-A7_genie_mec-p} = 0.44
\fvval{f0-A7_genie_mec-cells} = ---
\fvval{f0b-W2-chi2} = 0.57
\fvval{f0b-W2-p} = 1.00
\fvval{f0b-W2-cells} = ---
\fvval{f0-W2-chi2} = 0.77
\fvval{f0-W2-p} = 1.00
\fvval{f0-W2-cells} = ---
\fvval{f0b-A7_nuwro-chi2} = 24.92
\fvval{f0b-A7_nuwro-p} = 0.071
\fvval{f0b-A7_nuwro-cells} = ---
\fvval{f0-A7_nuwro-chi2} = 29.96
\fvval{f0-A7_nuwro-p} = 0.018
\fvval{f0-A7_nuwro-cells} = ---
\fvval{f0b-W1-chi2} = 5.01
\fvval{f0b-W1-p} = 1.00
\fvval{f0b-W1-cells} = ---
\fvval{f0-W1-chi2} = 5.69
\fvval{f0-W1-p} = 0.99
\fvval{f0-W1-cells} = ---
\fvval{f0b-W3-chi2} = 30.83
\fvval{f0b-W3-p} = 0.014
\fvval{f0b-W3-cells} = ---
\fvval{f0-W3-chi2} = 36.19
\fvval{f0-W3-p} = 0.0027
\fvval{f0-W3-cells} = ---
\fvval{f0b-closure_nuwro-chi2} = 11.60
\fvval{f0b-closure_nuwro-p} = 0.77
\fvval{f0b-closure_nuwro-cells} = ---
\fvval{f0-closure_nuwro-chi2} = 13.08
\fvval{f0-closure_nuwro-p} = 0.67
\fvval{f0-closure_nuwro-cells} = ---
\fvval{f0b-stage0c_gibuu-chi2} = 25.46
\fvval{f0b-stage0c_gibuu-p} = 0.062
\fvval{f0b-stage0c_gibuu-cells} = R06
\fvval{f0-stage0c_gibuu-chi2} = 35.75
\fvval{f0-stage0c_gibuu-p} = 0.0031
\fvval{f0-stage0c_gibuu-cells} = R06
\fvval{f0b-A7_gibuu-chi2} = 175.13
\fvval{f0b-A7_gibuu-p} = 8.0\times10^{-29}
\fvval{f0b-A7_gibuu-cells} = R02, R06, R07
\fvval{f0-A7_gibuu-chi2} = 246.75
\fvval{f0-A7_gibuu-p} = <10^{-30}
\fvval{f0-A7_gibuu-cells} = R02, R06, R07
\fvval{f0b-q3-chi2} = 53.42
\fvval{f0b-q3-p} = 6.4\times10^{-6}
\fvval{f0b-q3-cells} = ---
\fvval{f0-q3-chi2} = 59.83
\fvval{f0-q3-p} = 5.6\times10^{-7}
\fvval{f0-q3-cells} = ---
\fvval{f0b-stage0c_gibuu-zmax} = 2.01
\fvval{f0b-nunlisted} = 9
\fvval{f1-tune-g18} = G18\_10a\_02\_11b
\fvval{f1-tune-ar23} = AR23\_20i\_00\_000
\fvval{f1-n} = 20
\fvval{f1-g18-chi2} = 11.84
\fvval{f1-g18-p} = 0.76
\fvval{f1-ar23-chi2} = 16.86
\fvval{f1-ar23-p} = 0.39
\fvval{f1-zmax-ceil} = 0.65
\fvval{f1-g18-sens-chi2} = 15.15
\fvval{f1-g18-sens-p} = 0.51
\fvval{f1-ar23-sens-chi2} = 24.60
\fvval{f1-ar23-sens-p} = 0.077
\fvval{f-unit} = 10^{-40}
\fvval{box-R00-pt} = 0--0.7
\fvval{box-R00-pz} = 1.5--4.5
\fvval{box-R00-eavail} = 0--0.8
\fvval{box-R00-q3} = 0--2
\fvval{box-R00-W} = 0--100
\fvval{f-R00} = 32.6
\fvval{sig-C_total_resp-R00} = 7.10
\fvval{box-R01-pt} = 0--0.7
\fvval{box-R01-pz} = 1.5--4.5
\fvval{box-R01-eavail} = 0--100
\fvval{box-R01-q3} = 2--100
\fvval{box-R01-W} = 1.8--100
\fvval{f-R01} = 36.7
\fvval{sig-C_total_resp-R01} = 7.10
\fvval{box-R02-pt} = 0--0.7
\fvval{box-R02-pz} = 1.5--4.5
\fvval{box-R02-eavail} = 0.8--100
\fvval{box-R02-q3} = 0--2
\fvval{box-R02-W} = 0--1.8
\fvval{f-R02} = 6.31
\fvval{sig-C_total_resp-R02} = 14.00
\fvval{box-R03-pt} = 0--0.7
\fvval{box-R03-pz} = 1.5--4.5
\fvval{box-R03-eavail} = 0.8--100
\fvval{box-R03-q3} = 0--2
\fvval{box-R03-W} = 1.8--100
\fvval{f-R03} = 4.30
\fvval{sig-C_total_resp-R03} = 12.64
\fvval{box-R04-pt} = 0--0.7
\fvval{box-R04-pz} = 4.5--60
\fvval{box-R04-eavail} = 0--0.8
\fvval{box-R04-q3} = 0--2
\fvval{box-R04-W} = 0--100
\fvval{f-R04} = 49.0
\fvval{sig-C_total_resp-R04} = 4.20
\fvval{box-R05-pt} = 0--0.7
\fvval{box-R05-pz} = 4.5--60
\fvval{box-R05-eavail} = 0--100
\fvval{box-R05-q3} = 2--100
\fvval{box-R05-W} = 1.8--100
\fvval{f-R05} = 9.98
\fvval{sig-C_total_resp-R05} = 7.47
\fvval{box-R06-pt} = 0--0.7
\fvval{box-R06-pz} = 4.5--60
\fvval{box-R06-eavail} = 0.8--100
\fvval{box-R06-q3} = 0--2
\fvval{box-R06-W} = 0--1.8
\fvval{f-R06} = 5.57
\fvval{sig-C_total_resp-R06} = 5.89
\fvval{box-R07-pt} = 0--0.7
\fvval{box-R07-pz} = 4.5--60
\fvval{box-R07-eavail} = 0.8--100
\fvval{box-R07-q3} = 0--2
\fvval{box-R07-W} = 1.8--100
\fvval{f-R07} = 3.21
\fvval{sig-C_total_resp-R07} = 7.98
\fvval{box-R08-pt} = 0.7--4.5
\fvval{box-R08-pz} = 1.5--4.5
\fvval{box-R08-eavail} = 0--0.8
\fvval{box-R08-q3} = 0--100
\fvval{box-R08-W} = 0--1.8
\fvval{f-R08} = 13.9
\fvval{sig-C_total_resp-R08} = 6.25
\fvval{box-R09-pt} = 0.7--4.5
\fvval{box-R09-pz} = 1.5--4.5
\fvval{box-R09-eavail} = 0--100
\fvval{box-R09-q3} = 0--100
\fvval{box-R09-W} = 1.8--100
\fvval{f-R09} = 39.6
\fvval{sig-C_total_resp-R09} = 6.26
\fvval{box-R10-pt} = 0.7--4.5
\fvval{box-R10-pz} = 1.5--4.5
\fvval{box-R10-eavail} = 0.8--100
\fvval{box-R10-q3} = 0--2
\fvval{box-R10-W} = 0--1.8
\fvval{f-R10} = 7.83
\fvval{sig-C_total_resp-R10} = 8.59
\fvval{box-R11-pt} = 0.7--4.5
\fvval{box-R11-pz} = 1.5--4.5
\fvval{box-R11-eavail} = 0.8--100
\fvval{box-R11-q3} = 2--100
\fvval{box-R11-W} = 0--1.8
\fvval{f-R11} = 5.61
\fvval{sig-C_total_resp-R11} = 13.69
\fvval{box-R12-pt} = 0.7--4.5
\fvval{box-R12-pz} = 4.5--60
\fvval{box-R12-eavail} = 0--0.8
\fvval{box-R12-q3} = 0--2
\fvval{box-R12-W} = 0--100
\fvval{f-R12} = 22.0
\fvval{sig-C_total_resp-R12} = 6.63
\fvval{box-R13-pt} = 0.7--4.5
\fvval{box-R13-pz} = 4.5--60
\fvval{box-R13-eavail} = 0--100
\fvval{box-R13-q3} = 2--100
\fvval{box-R13-W} = 0--1.8
\fvval{f-R13} = 9.04
\fvval{sig-C_total_resp-R13} = 11.07
\fvval{box-R14-pt} = 0.7--4.5
\fvval{box-R14-pz} = 4.5--60
\fvval{box-R14-eavail} = 0--100
\fvval{box-R14-q3} = 2--100
\fvval{box-R14-W} = 1.8--100
\fvval{f-R14} = 49.6
\fvval{sig-C_total_resp-R14} = 5.27
\fvval{box-R15-pt} = 0.7--4.5
\fvval{box-R15-pz} = 4.5--60
\fvval{box-R15-eavail} = 0.8--100
\fvval{box-R15-q3} = 0--2
\fvval{box-R15-W} = 0--100
\fvval{f-R15} = 11.3
\fvval{sig-C_total_resp-R15} = 7.94
\fvval{cmodel-gibuu-enu} = 20
\fvval{label-gcv} = GENIE~2.12.10 CV
\fvval{g-gcv-total-chi2int} = 109
\fvval{g-gcv-total-ndf} = 16
\fvval{g-gcv-shape_only-chi2int} = 109
\fvval{g-gcv-shape_only-ndf} = 15
\fvval{label-gmec} = GENIE~2.12.10 + Valencia MEC
\fvval{g-gmec-total-chi2int} = 272
\fvval{g-gmec-total-ndf} = 16
\fvval{g-gmec-shape_only-chi2int} = 258
\fvval{g-gmec-shape_only-ndf} = 15
\fvval{label-nuwro} = NuWro~21.09
\fvval{g-nuwro-total-chi2int} = 188
\fvval{g-nuwro-total-ndf} = 16
\fvval{g-nuwro-shape_only-chi2int} = 188
\fvval{g-nuwro-shape_only-ndf} = 15
\fvval{label-gibuu} = GiBUU~2019
\fvval{g-gibuu-total-chi2int} = 58
\fvval{g-gibuu-total-ndf} = 8
\fvval{g-gibuu-shape_only-chi2int} = 28
\fvval{g-gibuu-shape_only-ndf} = 7
\fvval{label-tune} = MINERvA Tune~v1
\fvval{g-tune-total-chi2int} = 330
\fvval{g-tune-total-ndf} = 16
\fvval{g-tune-shape_only-chi2int} = 311
\fvval{g-tune-shape_only-ndf} = 15
\fvval{sens-alpha-pct} = 10
\fvval{sens-flux-fall-lo} = 24
\fvval{sens-flux-fall-hi} = 48
\fvval{sens-detlat-fall-max} = 18
\fvval{sens-joint-chi2-min} = 45
\fvval{fb-universes} = 100
\fvval{fb-plo} = 16
\fvval{fb-phi} = 84
\fvval{fb-edge-max} = 6.2
\fvval{fb-offset-relmax} = 1.0
\fvval{h2-lowstab-cells} = R02, R06, R10 and R15
\fvval{h2-lowstab-min} = 0.16
\fvval{h2-lowstab-max} = 0.25
```
