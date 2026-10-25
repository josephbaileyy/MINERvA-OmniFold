# Changes, paragraph by paragraph: register round r17

Base: origin/main `f0b26234`. Only `docs/analysis-note/paper_body.tex` changed in the paper; `main_paper.tex`, the
note, the primer and the PET note are unchanged. The round was written in four section batches (b1 Secs. I–III, b2
Secs. IV–V and the Fig. 3 caption, b3 Secs. VI–VII, b4 Sec. VIII), spliced into one file, reviewed in both directions,
and fixed. Row ids in brackets are `ledger.md`'s. The moves S1–S14 are `outline.md`'s; S9 was declined by the director.

**Read the batch sections below with the review fixes.** Each batch's "after" text is the writer's draft. The review
fixes listed next were applied after the splice. `paper_body.tex` and `ledger.md` hold the final text; the ledger's
probes match it (0 failures).

## Review fixes applied after the splice

| finding | fix (final text) | ledger |
|---|---|---|
| b1-R1 | the scope sentence ends "…deformations tested, rather than of multidimensional OmniFold in general." | b1-8, b1-9, b1-10 |
| b1-R2 = b2-R6 | the reproducibility sentence becomes two sentences, so "so" does not cover reproducibility | b1-80 |
| b1-R3 | a source comment cites `re2/RE2-PARTB-REPORT.md:173` for "reproducible" | (comment) |
| b1-R5 | "The model dependence of configuration~(e) is measured as …" | b1-86 |
| b2-R2 | V A ¶1 ends "Both kinds of closure study are described in \nsec{sec:closure-map}." | b2-52 |
| b2-R3 | "beside the four-block covariance"; "Added to the four-block covariance" | b2-37 |
| b2-R4 | "These deviations occur with or without background, so background subtraction alone does not explain the residual." | b2-58 |
| b3-R1 | VII B ¶2 reverted to the base's "drawn from it" (the writer's "source half" is inaccurate for the background) | b3-42 |
| b3-R4 | "In this study, every rejection stays in place …" | b3-74 |
| b4-R1 | "We make no coverage claim on …" | b4-8 |
| b4-R2 | the source comment reads "with fewer negations per sentence" | (comment) |

## Every review finding and its disposition

### b4 (Sec. VIII) — ADOPT-AFTER-FIXES, no BLOCKING
| # | sev | finding | disposition |
|---|---|---|---|
| b4-R1 | SHOULD-FIX | item 1 "We claim no coverage on …" can parse as a claim that coverage fails (base: "no coverage is claimed"; DECISION-20261014 §2: "no coverage claim is made") | FIXED: "We make no coverage claim on …"; ledger b4-8 probe updated |
| b4-R2 | NIT | new source comment says "one negation per sentence", false for two sentences | FIXED: "with fewer negations per sentence" |
| b4-R3 | NIT | item 8 restates condition (ii)'s omission; base form also correct | KEPT as written (reviewer recommends keeping: list readers may not have read VII D) |
| b4-R4 | NIT | item 4 "is interpreted as" could be active voice | NOT ADOPTED (optional; same meaning) |
| b4-R5 | register | item 5 two "has not been measured"; optional rewrite | NOT ADOPTED (optional; each negative a distinct fact) |
<!-- absence-ok: quotes or summarizes printed paper text, whose paragraph in paper_body.tex carries its own Search line; not a new absence claim -->

### b2 (Secs. IV–V) — ADOPT-AFTER-FIXES, no BLOCKING
| # | sev | finding | disposition |
|---|---|---|---|
| b2-R1 | SHOULD-FIX | IV B: "failed the test" is printed without the test's criterion, so 95.4% nominal may read as the threshold | NOT ADOPTED this round: adding the criterion (band width within 10% of the scatter; note Sec. 5.2) would add a fact to the paper, outside "presentation only". The base had the same omission ("undercovered"). Flagged to the director. |
| b2-R2 | SHOULD-FIX | V A ¶1 lost its paragraph-final pointer (the closure-map pointer now ends ¶2 only) | FIXED: "Both kinds of closure study are described in \nsec{sec:closure-map}." (ledger b2-52) |
| b2-R3 | NIT | C_model paragraph's "the one above" / "the covariance above" now two paragraphs below the definition | FIXED: "the four-block covariance" (twice; ledger b2-37) |
| b2-R4 | NIT | V B: "with or without background" detached from the deviations | FIXED: "These deviations occur with or without background, so background subtraction alone does not explain the residual." (base wording restored in substance; ledger b2-58) |
| b2-R5 | NIT | Fig. 3: "the estimator's" refers to two estimators (base had the same ambiguity) | NOT ADOPTED: resolving it would assert which estimator's development each seed set belongs to; base wording kept. |
| b2-R6 | NIT (cross-batch, III) | "is reproducible and is that of its ensemble, so its covariance…" lets "so" cover reproducibility | FIXED: two sentences (ledger b1-80) |

### b3 (Secs. VI–VII) — ADOPT-AFTER-FIXES, no BLOCKING
| # | sev | finding | disposition |
|---|---|---|---|
| b3-R1 | SHOULD-FIX | VII B ¶2 "drawn from the source half" is inaccurate for the background, which is a Poisson draw from an independent half of the background sample (note sec:joint5d-calibration, tab:joint5d-genmodel; s5n_pseudo.py build_pseudo) | REVERTED to the base wording "drawn from it" (no claim change this round). The base's antecedent invites the same reading: a pre-existing accuracy issue, sent to the director with the note's wording as the proposed fix. |
| b3-R2 | SHOULD-FIX, for Joseph (pre-existing, carried from r16) | the note says A2 also needs the losses to be independent of their outcomes, "not shown"; "Under A1 and A2" now sits just before the lost-draw sentence | NOT CHANGED (claim addition); sent to the director. |
| b3-R3 | NIT | the S8 numeric paragraph has no pointer (both paragraphs are in one marked block) | NOT ADOPTED (acceptable per reviewer). |
| b3-R4 | NIT | "Every rejection stays in place…" no longer inside "In an exploratory sensitivity study" | FIXED: "In this study, every rejection stays in place…" (ledger b3-74) |
| b3-R5 | NIT | S12 pointer correct only while the κ paragraph stays in note 10.5 | KEPT; the source comment records it. |
| b3-R6 | NIT | writer's "A1/A2 named once" loosely worded (defined once, cited twice) | record wording only; no text change. |
| b3-R7 | register | "resolved no change"; "does not survive that correction robustly" | NOT ADOPTED (meaning nuance; optional). |
| (1) | — | VII C ¶3 "Under A1 and A2 … so it does not depend on this extension" | Reviewer: not stronger than base; matches note sec:joint5d-frozen and App. B.5. Kept. |

### b1 (Secs. I–III) — ADOPT-AFTER-FIXES, no BLOCKING
| # | sev | finding | disposition |
|---|---|---|---|
| b1-R1 | SHOULD-FIX | "not a general assessment of multidimensional OmniFold" removed; implied, but it was the body's only explicit statement that the verdicts concern this implementation | FIXED, positive-first: "…deformations tested, rather than of multidimensional OmniFold in general." (ledger b1-8, b1-9, b1-10) |
| b1-R2 | SHOULD-FIX | "is reproducible and is that of its ensemble, so its covariance …" adds reproducibility as a premise of "so" | FIXED (same as b2-R6): two sentences (ledger b1-80) |
| b1-R3 | NIT | "reproducible" beside Table II, whose caption calls only (c)–(e) reproducible | source comment added citing re2/RE2-PARTB-REPORT.md:173 (ER repeats itself to 9.2e-12) |
| b1-R4 | NIT | scope paragraph names "the generator tests" before the roadmap introduces them | NOT ADOPTED (would add a \ref; abstract and Table I introduce them) |
| b1-R5 | NIT | "Its model dependence" has "a criterion" as nearest antecedent | FIXED: "The model dependence of configuration~(e) is measured as …" (ledger b1-86) |
| b1-R6 | register | five "X uses configuration (Y)" sentences; process wording of the criterion | NOT ADOPTED (would drop text or add content) |
| note | — | reviewer saw the worktree change mid-review | those were the lane's own b4 fixes and the fix_da_order.py repair |

## KEEP ids at the two disclosure-bearing moves

- **S5 (IV B, statistical block):** the paragraph keeps the four facts the brief requires: an earlier band failed its
  coverage test; the rescoring was post hoc; the rescoring is not an independent coverage test, and why; and Table I's
  "an earlier band failed coverage" finds its test there. The bound phrases (`check_sec4_receipts.py`) print
  byte-identical. K6 is not in this paragraph in the base either; it prints in VIII A item 1. K8 is unchanged.
- **S10 (VII C ¶3):** D1 (the design fixed before the statistic, with the reviewers' prior look; the budget extension
  after the observed p values had become visible, at the choice); D2 (A1 and A2 named); the error-control sentence
  KEEP (narrowed): "Under A1 and A2, the error control holds for any rule that decides when sampling stops, so it does
  not depend on this extension." The lost-draw and rerun sentences print verbatim.


---


---

## Changes, paragraph by paragraph: batch b1 (Secs. I–III), register round r17

Base: `paper_body.tex` at `f0b26234`, lines 30–353. Text below is the printed source (comments stripped, whitespace collapsed; tables shown as [TABLE]). Ledger rows: `ledger.md` (rows b1-*).
Paragraphs not listed (III ¶1–¶3, III ¶5, Table II) are unchanged.

### I ¶1 (base line 33)

**Before:**

> Multidifferential neutrino cross sections test interaction models across muon and hadronic observables. Their interpretation depends on correcting detector response and assessing the bias and uncertainty of the unfolding procedure. Iterative Bayesian unfolding on a binned migration matrix~\cite{DAgostini:1994fjx} is widely used, but the response tensor grows rapidly when additional observables are reported. OmniFold learns event weights in an unbinned feature space through classifier-based density-ratio estimation \cite{Andreassen:2019cjw,Andreassen:2021zzk}. This makes simultaneous higher-dimensional unfolding possible without specifying a separate binned response tensor for every projection. Unbinned unfolding has been applied to collider data, for example eight observables in deep-inelastic scattering at H1~\cite{H1:2021wkz} and twenty-four $Z$+jets observables at ATLAS~\cite{ATLAS:2024jets}; see Ref.~\cite{Canelli:2025guide} for a survey. In neutrino physics it has been demonstrated on a public simulated T2K near-detector sample~\cite{Huang:2025omnifold}.

**After:**

> Multidifferential neutrino cross sections test interaction models across muon and hadronic observables. Their interpretation depends on correcting detector response and assessing the bias and uncertainty of the unfolding procedure. Iterative Bayesian unfolding on a binned migration matrix~\cite{DAgostini:1994fjx} is widely used, but the response tensor grows rapidly when additional observables are reported. OmniFold learns event weights in an unbinned feature space through classifier-based density-ratio estimation \cite{Andreassen:2019cjw,Andreassen:2021zzk}. This makes simultaneous higher-dimensional unfolding possible without specifying a separate binned response tensor for every projection. Unbinned unfolding has been applied to collider data, for example eight observables in deep-inelastic scattering at H1~\cite{H1:2021wkz} and twenty-four $Z$+jets observables at ATLAS~\cite{ATLAS:2024jets}; see Ref.~\cite{Canelli:2025guide} for a survey. In neutrino physics it has been demonstrated on a public simulated T2K near-detector sample~\cite{Huang:2025omnifold}. Multidifferential neutrino measurements on data reach three dimensions~\cite{MINERvA:2022qelike3d,MINERvA:2026qeleme,MicroBooNE:2023inc3d,NOvA:2026inc3d}.

- **Reason:** S1: the state of the art on data ("data measurements reach three dimensions", P10) moves here from ¶2 and becomes the last sentence of ¶1, after the simulated T2K demonstration. "Multi-differential" is spelled as in the paragraph's first word. No other change.
- **Rule:** S1, R1
- **KEEP ids touched:** none

### I ¶2 (base line 49)

**Before:**

> We apply the method to MINERvA medium-energy $\nu_{\mu}$ data from the MINERvA open-data release~\cite{MINERvA:OpenData}. We first reproduce the published double-differential charged-current inclusive cross section in transverse and longitudinal muon momentum, $d^{2}\sigma/(d\pT\,d\pPar)$~\cite{MINERvA:2021owq}, then add available hadronic energy $\Eavail$, three-momentum transfer $q_{3}$, and hadronic invariant mass $W$, and obtain simultaneous three-, four-, and five-observable central values. Reconstructed $W$ is fixed by the reconstructed $(\pT,\pPar,q_{3})$, so the five observables are simultaneous but not independent. Multi-differential neutrino measurements on data reach three dimensions~\cite{MINERvA:2022qelike3d,MINERvA:2026qeleme,MicroBooNE:2023inc3d,NOvA:2026inc3d}.

**After:**

> We apply the method to MINERvA medium-energy $\nu_{\mu}$ data from the MINERvA open-data release~\cite{MINERvA:OpenData}. We first reproduce the published double-differential charged-current inclusive cross section in transverse and longitudinal muon momentum, $d^{2}\sigma/(d\pT\,d\pPar)$~\cite{MINERvA:2021owq}, then add available hadronic energy $\Eavail$, three-momentum transfer $q_{3}$, and hadronic invariant mass $W$, and obtain simultaneous three-, four-, and five-observable central values. Reconstructed $W$ is fixed by the reconstructed $(\pT,\pPar,q_{3})$, so the five observables are simultaneous but not independent.

- **Reason:** S1: P10 leaves for ¶1; the paragraph now ends on the reconstructed-W statement. No other change.
- **Rule:** S1
- **KEEP ids touched:** none

### I ¶3 (base line 63)

**Before:**

> We evaluate this implementation as a case study of multidimensional unfolding and of inference with a biased estimator. The question is whether it gives reliable multidimensional cross sections when the simulation mismodels the truth by generator-sized amounts, and what validation is needed before its outputs can be interpreted. Two properties must be distinguished. The coverage of unfolded intervals is the rate at which they contain the true cross section. The calibration of a test is the rate at which it rejects a true hypothesis. Calibration can be obtained without validated intervals, by simulating the whole analysis chain at the hypothesis so that the estimator's bias enters the simulated null distribution, to the extent that the simulated chain reproduces the analysis of the data. Sections~\ref{sec:repro2d}--\ref{sec:limits} test whether the unfolded results and their intervals can be validated. These validation studies are the paper's main results, and Table~\ref{tab:findings} lists each with its configuration and test. As a secondary application, Sec.~\ref{sec:joint} tests generator predictions that the published muon-kinematic measurement already disfavours~\cite{MINERvA:2021owq}.

**After:**

> We evaluate this implementation as a case study of multidimensional unfolding and of inference with a biased estimator. The question is whether it gives reliable multidimensional cross sections when the simulation mismodels the truth by generator-sized amounts, and what validation is needed before its outputs can be interpreted. Two properties must be distinguished. The coverage of unfolded intervals is the rate at which they contain the true cross section. The calibration of a test is the rate at which it rejects a true hypothesis. Calibration can be obtained without validated intervals by simulating the whole analysis chain at the hypothesis, so that the estimator's bias enters the simulated null distribution. A calibration obtained in this way is valid to the extent that the simulated chain reproduces the analysis of the data.

- **Reason:** S1: the roadmap (P17–P19) leaves for the new paragraph after the scope. The calibration sentence (P16) is split in two: the method, then its condition of validity, which keeps "to the extent that the simulated chain reproduces the analysis of the data" verbatim. "Is valid" is the paper's own verb for this condition (Sec. VII D: "The calibration is valid ... to the extent that").
- **Rule:** S1, R10, R9
- **KEEP ids touched:** D2 (the calibration's fidelity condition, A1, stated once here with its condition kept)

### Table I (base lines 82–105)

**Before:**

> [TABLE]

**After:**

> [TABLE]

- **Reason:** Not touched. Byte-identical (diff of the 24 lines: empty) and in the same source position, between ¶3 and the scope paragraph.
- **Rule:** protected
- **KEEP ids touched:** none

### I ¶4, the scope paragraph (base line 106)

**Before:**

> \emph{Scope.} The findings are those of one OmniFold implementation on one data set, for the observables, configurations, and deformations tested; they are not a general assessment of multidimensional OmniFold. Throughout, a three- to five-observable result is a central value, the output of the estimators of Sec.~\ref{sec:method} with the observable definitions, simulated detector response, background treatment, and regularization given there. These results have no intervals of validated coverage, and the paper does not deliver a validated five-observable cross-section measurement. The generator tests are conditional tests of simulated hybrid hypotheses, under which the cross section equals a prediction on every cell of a fine five-observable grid, with the MINERvA Tune~v1 composition below it, as defined in Sec.~\ref{sec:hypotheses}. They are calibrated within the implemented simulation model, whose detector model has no calorimetric recoil-response uncertainty. Under the assumptions of Sec.~\ref{sec:calibration}, their decision rule controls the familywise error rate of the ten decisions at 5\%, on average over the nuisance priors. The rejections are not physical exclusions of the generators and provide no measurement uncertainty. Section~\ref{sec:limitations} lists the limitations of these results. The companion analysis note~\cite{AnalysisNote2026} gives the full validation record, the construction of the uncertainties, and the joint tests, and is cited below by section.

**After:**

> \emph{Scope.} The findings are those of one OmniFold implementation on one data set, for the observables, configurations, and deformations tested. Throughout, a three- to five-observable result is a central value without intervals of validated coverage: the output of the estimators of Sec.~\ref{sec:method}, with the observable definitions, simulated detector response, background treatment, and regularization given there. The paper does not deliver a validated five-observable cross-section measurement. The generator tests are conditional tests of simulated hybrid null hypotheses, under which the cross section equals a prediction on every cell of a fine five-observable grid, with the MINERvA Tune~v1 composition below that grid, as defined in Sec.~\ref{sec:hypotheses}. They are calibrated within the implemented simulation model, whose detector model has no calorimetric recoil-response uncertainty. Under the assumptions of Sec.~\ref{sec:calibration}, their decision rule controls the familywise error rate of the ten decisions at 5\%, on average over the nuisance priors. The rejections are not physical exclusions of the generators and provide no measurement uncertainty.

- **Reason:** S2: positive-first, as definitions. (1) The first sentence keeps the restriction to one implementation, one data set and the cases tested; the negative "they are not a general assessment of multidimensional OmniFold" is collapsed into that restriction (ledger b1-10), which entails it. (2) The naming convention now carries the coverage status: "a central value without intervals of validated coverage: the output of ..." (P22 + first half of P23, R1). (3) The single KEEP negative "The paper does not deliver a validated five-observable cross-section measurement" is its own sentence. (4) "simulated hybrid hypotheses" becomes "simulated hybrid null hypotheses" (the abstract's and Sec. VII B's term, K2); "below it" becomes "below that grid" (the note's own words, sec:joint5d-design). (5) The calibration sentence (no recoil-response uncertainty), the FWER sentence (assumptions of Sec. VII C, ten decisions, 5%, on average over the nuisance priors) and the exclusions sentence ("not physical exclusions ... no measurement uncertainty", one sentence) are unchanged. (6) The limitations pointer and the note pointer move to the roadmap paragraph.
- **Rule:** S2, R1, R8
- **KEEP ids touched:** K2 (hybrid null, kept and made explicit); the brief's scope KEEPs: not a validated five-observable measurement; no recoil-response uncertainty; FWER under the Sec. VII C assumptions averaged over the nuisance priors; not exclusions / no measurement uncertainty as one sentence

### I ¶5, new roadmap paragraph

**Before:**

> (new paragraph; its sentences were the end of I ¶3 and I ¶4)

**After:**

> Sections~\ref{sec:repro2d}--\ref{sec:limits} test whether the unfolded results and their intervals can be validated. These validation studies are the paper's main results, and Table~\ref{tab:findings} lists each with its configuration and test. As a secondary application, Sec.~\ref{sec:joint} tests generator predictions that the published muon-kinematic measurement already disfavours~\cite{MINERvA:2021owq}. Section~\ref{sec:limitations} lists the limitations of these results. The companion analysis note~\cite{AnalysisNote2026} gives the full validation record, the construction of the uncertainties, and the joint tests, and is cited below by section.

- **Reason:** S1: the roadmap now follows the scope. Its sentences are the base's P17, P18, P19, P28 and P29, unchanged in wording: main results Secs. IV–VI with Table I; Sec. VII secondary; limitations Sec. VIII A; the note pointer. It is a paragraph of its own rather than the tail of the scope paragraph (see REPORT, open question 1).
- **Rule:** S1, R7
- **KEEP ids touched:** none

### II ¶1 (base line 130)

**Before:**

> The analysis uses the twelve MINERvA medium-energy, forward-horn-current run periods, corresponding to $1.057\times10^{21}$ protons on target and an average neutrino energy near \SI{6}{GeV}~\cite{MINERvA:2021owq}, from an earlier production of the MINERvA open-data release of pre-selected analysis ntuples (AnaTuples)~\cite{MINERvA:OpenData} (see Data availability). The detector, including the downstream MINOS near detector that serves as its muon spectrometer, is described in Ref.~\cite{MINERvA:2013zvz}. The signal is a $\nu_{\mu}$ charged-current interaction, with any final state, whose true vertex lies in the tracker fiducial volume ($5980<z<\SI{8422}{mm}$, inside a hexagon of apothem \SI{850}{mm}) and whose muon has $\theta_{\mu}<20^{\circ}$, $1.5<\pPar<\SI{60}{GeV/c}$, and $\pT\le\SI{4.5}{GeV/c}$. Selected simulated events outside this definition, including charged-current $\nu_{\mu}$ events whose muon lies outside these limits, are background. The selection requires a reconstructed vertex in the same volume and a reconstructed muon with $\theta_{\mu}<20^{\circ}$, matched to a MINOS track of negative charge, with a dead-time requirement, as in Ref.~\cite{MINERvA:2021owq}; the flux treatment follows Ref.~\cite{MINERvA:2016iqn}. After selection, the sample contains $4.12$ million selected data events. The simulation contains $32.8$ million unweighted true signal events and $20.5$ million selected simulated events; it is scaled to the data exposure. The simulated events are generated with GENIE~2.12.6~\cite{Andreopoulos:2009rq} and the MINERvA Tune~v1, which reweights GENIE with a non-resonant pion reduction, a random-phase-approximation correction, and an empirical low-recoil two-particle--two-hole (2p2h) enhancement~\cite{MINERvA:2016lowrecoil}. Event selection is held fixed as the classifier inputs and unfolded observables grow from $(\pT,\pPar)$ to $(\pT,\pPar,\Eavail,q_3,W)$; adding features does not add selected events or relax the signal definition.

**After:**

> The analysis uses the twelve MINERvA medium-energy, forward-horn-current run periods, corresponding to $1.057\times10^{21}$ protons on target and an average neutrino energy near \SI{6}{GeV}~\cite{MINERvA:2021owq}, from an earlier production of the MINERvA open-data release of pre-selected analysis ntuples (AnaTuples)~\cite{MINERvA:OpenData} (see Data availability). The detector, including the downstream MINOS near detector that serves as its muon spectrometer, is described in Ref.~\cite{MINERvA:2013zvz}. The signal is a $\nu_{\mu}$ charged-current interaction, with any final state, whose true vertex lies in the tracker fiducial volume ($5980<z<\SI{8422}{mm}$, inside a hexagon of apothem \SI{850}{mm}) and whose muon has $\theta_{\mu}<20^{\circ}$, $1.5<\pPar<\SI{60}{GeV/c}$, and $\pT\le\SI{4.5}{GeV/c}$. Selected simulated events outside this definition, including charged-current $\nu_{\mu}$ events whose muon lies outside these limits, are background. The selection requires a reconstructed vertex in the same volume and a reconstructed muon with $\theta_{\mu}<20^{\circ}$, matched to a MINOS track of negative charge, with a dead-time requirement, as in Ref.~\cite{MINERvA:2021owq}. The flux treatment follows Ref.~\cite{MINERvA:2016iqn}. After selection, the sample contains $4.12$ million selected data events. The simulation contains $32.8$ million unweighted true signal events and $20.5$ million selected simulated events. The simulation is scaled to the data exposure. The simulated events are generated with GENIE~2.12.6~\cite{Andreopoulos:2009rq} and the MINERvA Tune~v1, which reweights GENIE with a non-resonant pion reduction, a random-phase-approximation correction, and an empirical low-recoil two-particle--two-hole (2p2h) enhancement~\cite{MINERvA:2016lowrecoil}. Event selection is held fixed as the classifier inputs and unfolded observables grow from $(\pT,\pPar)$ to $(\pT,\pPar,\Eavail,q_3,W)$. Adding features does not add selected events or relax the signal definition.

- **Reason:** R10: two semicolon joins split (selection / flux treatment; simulation counts / exposure scaling); the second half of the latter gets the explicit subject "The simulation". The fixed-selection sentence (P38) split at its semicolon. Every number and condition unchanged.
- **Rule:** R10
- **KEEP ids touched:** none

### II ¶2 (base line 167)

**Before:**

> The unfolded observables are defined at truth level. Besides the muon momentum components $\pT=p_{\mu}\sin\theta_{\mu}$ and $\pPar=p_{\mu}\cos\theta_{\mu}$, they are the three-momentum transfer $q_{3}=|\vec{q}\,|$ from the generator's four-vectors, the hadronic invariant mass $W=\sqrt{M^{2}+2M(E_{\nu}-E_{\mu})-Q^{2}}$ with the struck-nucleon mass $M$, and the available energy \begin{equation} \Eavail=\sum_{p}(E_{p}-m_{p})+\sum_{\pi^{\pm}}(E_{\pi}-\SI{135}{MeV}) +\sum_{\pi^{0}}E_{\pi}+\sum_{\gamma}E_{\gamma}, \label{eq:eavail} \end{equation} with a defined constant of \SI{135}{MeV}, rather than the charged-pion mass, in the charged-pion term; all other final-state particles, including neutrons, contribute nothing. The sums run over the generator's final-state particles after final-state interactions, in which neutral pions appear undecayed. The \SI{135}{MeV} constant is inherited from the analysis framework's definition; it defines the reported observable and is used consistently by the analysis and every prediction. Replacing it by the charged-pion mass would change no true-$\Eavail$ bin by more than \SI{1.05}{\percent}. Reconstructed $\Eavail$ is $1.17$ times the calorimetric recoil energy in the tracker and electromagnetic calorimeter, with muon deposits removed; reconstructed $q_{3}$ and $W$ instead combine the muon kinematics with a separate calorimetric estimate $q_{0}$ of the energy transfer.

**After:**

> The unfolded observables are defined at truth level. Besides the muon momentum components $\pT=p_{\mu}\sin\theta_{\mu}$ and $\pPar=p_{\mu}\cos\theta_{\mu}$, they are the three-momentum transfer $q_{3}=|\vec{q}\,|$ from the generator's four-vectors, the hadronic invariant mass $W=\sqrt{M^{2}+2M(E_{\nu}-E_{\mu})-Q^{2}}$ with the struck-nucleon mass $M$, and the available energy \begin{equation} \Eavail=\sum_{p}(E_{p}-m_{p})+\sum_{\pi^{\pm}}(E_{\pi}-\SI{135}{MeV}) +\sum_{\pi^{0}}E_{\pi}+\sum_{\gamma}E_{\gamma}, \label{eq:eavail} \end{equation} with a defined constant of \SI{135}{MeV}, rather than the charged-pion mass, in the charged-pion term. All other final-state particles, including neutrons, contribute nothing. The sums run over the generator's final-state particles after final-state interactions, in which neutral pions appear undecayed. The \SI{135}{MeV} constant is inherited from the analysis framework's definition. It defines the reported observable and is used consistently by the analysis and every prediction. Replacing it by the charged-pion mass would change no true-$\Eavail$ bin by more than \SI{1.05}{\percent}. Reconstructed $\Eavail$ is $1.17$ times the calorimetric recoil energy in the tracker and electromagnetic calorimeter, with muon deposits removed. Reconstructed $q_{3}$ and $W$ instead combine the muon kinematics with a separate calorimetric estimate $q_{0}$ of the energy transfer.

- **Reason:** R10: after the equation, the 135 MeV clause and "all other final-state particles ... contribute nothing" become two sentences; P42 and P44 split at their semicolons. Every definition and the 1.05% bound unchanged; no "negligible" added (E2).
- **Rule:** R10
- **KEEP ids touched:** none

### II ¶3 (base line 194)

**Before:**

> Reconstructed $W$ is an exact function of the reconstructed $(\pT,\pPar,q_{3})$, so the five reconstructed inputs share information and do not provide five independent constraints. The relation holds because $W_{\mathrm{reco}}^{2}=(\bar M+q_{0})^{2}-q_{3,\mathrm{reco}}^{2}$, with $\bar M$ an average nucleon mass, and $q_{3,\mathrm{reco}}$ increases with $q_{0}$ at fixed muon kinematics; it is exact apart from the clamp at $W^{2}=0$, which applies to \SI{1.5}{\percent} of simulated events. Only reconstructed $W$ is fixed by the other inputs; reconstructed $\Eavail$ comes from its own calorimetric estimator and is not a function of them. At truth level, $\theta_{\mu}$, and with it $\pT$ and $\pPar$, is measured from a fixed beam axis rather than from the true neutrino direction, so truth $W$ is fixed by $(\pT,\pPar,q_{3})$ only up to that event-by-event angle, of about \SI{1}{mrad}, and the choice of $M$; the residual is within \SI{\pm2}{MeV} for 68\% of events. The definitions are detailed in Ref.~\cite{AnalysisNote2026}, Secs.~\ref*{N-sec:eavail-definition} and~\ref*{N-sec:eavailw-definitions}.

**After:**

> Reconstructed $W$ is an exact function of the reconstructed $(\pT,\pPar,q_{3})$, so the five reconstructed inputs share information and do not provide five independent constraints. The relation holds because $W_{\mathrm{reco}}^{2}=(\bar M+q_{0})^{2}-q_{3,\mathrm{reco}}^{2}$, with $\bar M$ an average nucleon mass, and $q_{3,\mathrm{reco}}$ increases with $q_{0}$ at fixed muon kinematics. This relation is exact apart from the clamp at $W^{2}=0$, which applies to \SI{1.5}{\percent} of simulated events. Only reconstructed $W$ is fixed by the other inputs. Reconstructed $\Eavail$ comes from its own calorimetric estimator and is not a function of them. At truth level, $\theta_{\mu}$, and with it $\pT$ and $\pPar$, is measured from a fixed beam axis rather than from the true neutrino direction. Truth $W$ is therefore fixed by $(\pT,\pPar,q_{3})$ only up to that event-by-event angle, of about \SI{1}{mrad}, and the choice of $M$. The resulting residual in truth $W$ is within \SI{\pm2}{MeV} for 68\% of events. The definitions are detailed in Ref.~\cite{AnalysisNote2026}, Secs.~\ref*{N-sec:eavail-definition} and~\ref*{N-sec:eavailw-definitions}.

- **Reason:** R10: P46, P47 and P48 split at their semicolons; "so truth W is fixed" becomes "Truth W is therefore fixed" (same inference); "the residual" names its quantity ("the resulting residual in truth W", as the source comment's "Truth-W residual"). The pointer stays at the paragraph end.
- **Rule:** R10
- **KEEP ids touched:** none

### II ¶4 (base line 215)

**Before:**

> The external predictions are the untuned GENIE~2.12.10 without (``GENIE CV'') and with (``GENIE + MEC'') the Valencia 2p2h component~\cite{Nieves:2011pp}, which models meson-exchange currents (MEC), for CH; NuWro~21.09~\cite{Golan:2012wx} and GiBUU~2019~\cite{Buss:2011mx}, for carbon. All are per nucleon of their target. The GENIE and NuWro predictions are reweighted exactly, event by event, to the analysis flux, and the GiBUU sample stops at $E_{\nu}\approx\SI{20}{GeV}$. The predictions compute $W$ with the neutron mass for every event, which changes their coarse-cell predictions by at most about one Monte Carlo standard error in each cell where this was evaluated (it cannot be evaluated for GiBUU). They also measure $\pT$ about their own neutrino axis, which differs from the analysis truth $\pT$ by \SI{\pm4}{MeV} for 68\% of events. Hydrogen has no quasielastic, 2p2h, or coherent $\nu_{\mu}$ charged-current channel, so normalizing per nucleon does not remove the difference between the targets: in GENIE's own CH sample, the carbon-only cross section per nucleon exceeds that of CH by \SI{8.3}{\percent} for $W<\SI{1.1}{GeV}$. The NuWro and GiBUU comparisons contain a target difference of this kind, which the tests of Sec.~\ref{sec:joint} do not correct. These comparisons of the predictions with the analysis definitions are given in Ref.~\cite{AnalysisNote2026}, Secs.~\ref*{N-sec:eavailw-axis} and~\ref*{N-sec:eavailw-generators}.

**After:**

> The external predictions for CH are the untuned GENIE~2.12.10 without (``GENIE CV'') and with (``GENIE + MEC'') the Valencia 2p2h component~\cite{Nieves:2011pp}, which models meson-exchange currents (MEC). The predictions for carbon are NuWro~21.09~\cite{Golan:2012wx} and GiBUU~2019~\cite{Buss:2011mx}. All are per nucleon of their target. The GENIE and NuWro predictions are reweighted exactly, event by event, to the analysis flux. The GiBUU sample stops at $E_{\nu}\approx\SI{20}{GeV}$. The predictions compute $W$ with the neutron mass for every event. In each cell where this choice was evaluated, it changes their coarse-cell predictions by at most about one Monte Carlo standard error. Its effect cannot be evaluated for GiBUU. The predictions also measure $\pT$ about their own neutrino axis, which differs from the analysis truth $\pT$ by \SI{\pm4}{MeV} for 68\% of events. Hydrogen has no quasielastic, 2p2h, or coherent $\nu_{\mu}$ charged-current channel, so normalizing per nucleon does not remove the difference between the targets. In GENIE's own CH sample, the carbon-only cross section per nucleon exceeds that of CH by \SI{8.3}{\percent} for $W<\SI{1.1}{GeV}$. The NuWro and GiBUU comparisons contain a target difference of this kind, which the tests of Sec.~\ref{sec:joint} do not correct. These comparisons of the predictions with the analysis definitions are given in Ref.~\cite{AnalysisNote2026}, Secs.~\ref*{N-sec:eavailw-axis} and~\ref*{N-sec:eavailw-generators}.

- **Reason:** R10/R9: the list of predictions is split by target (CH; carbon). P52 split at ", and". The neutron-mass sentence (P53) becomes three: the choice; its size, with the per-cell condition first ("In each cell where this choice was evaluated", R9); the GiBUU exception, which was a parenthesis. "They also measure" gets the explicit subject "The predictions". The target-difference sentence (P55) split at its colon. Pointer stays at the end.
- **Rule:** R10, R9
- **KEEP ids touched:** none

### II ¶5 (base line 238)

**Before:**

> The fine grid is the analysis binning: the published $14\times16$ muon-momentum bins times 7 $\Eavail$, 7 $q_{3}$, and 6 $W$ bins. The generator tests use a coarse $3^{5}$ grid in $(\pT,\pPar,\Eavail,q_{3},W)$ whose edges are the fine edges nearest the simulated tertiles (\nsec{sec:joint5d-design}). A coarse cell is reported if its expected reconstructed signal and its truth weight at the data exposure are both at least 1000 events; \jtNcells{} cells pass, and the others, which hold \SI{0.47}{\percent} of the expected signal, stay in the total only. For GiBUU, whose sample lacks high-energy neutrinos, the domain is the \jtNcellsGiBUU{} supported cells with $\pPar<\SI{6}{GeV/c}$.

**After:**

> The fine grid is the analysis binning: the published $14\times16$ muon-momentum bins times 7 $\Eavail$, 7 $q_{3}$, and 6 $W$ bins. The generator tests use a coarse $3^{5}$ grid in $(\pT,\pPar,\Eavail,q_{3},W)$ whose edges are the fine edges nearest the simulated tertiles. A coarse cell is reported if its expected reconstructed signal and its truth weight at the data exposure are both at least 1000 events. Of the coarse cells, \jtNcells{} pass. The others, which hold \SI{0.47}{\percent} of the expected signal, stay in the total only. For GiBUU, whose sample lacks high-energy neutrinos, the domain is the \jtNcellsGiBUU{} supported cells with $\pPar<\SI{6}{GeV/c}$. The construction of the coarse grid is given in \nsec{sec:joint5d-design}.

- **Reason:** R7: the mid-sentence pointer "(\nsec{sec:joint5d-design})" becomes a plain closing clause, "The construction of the coarse grid is given in ..." (the note section prints the tertile edge rule; ledger b1-65 N: probe). R10: the support-rule sentence (P60) split in three; "Of the coarse cells, \jtNcells{} pass" avoids opening a sentence with a numeral.
- **Rule:** R7, R10
- **KEEP ids touched:** none

### III ¶4 (base line 278) → three paragraphs

**Before:**

> All estimator configurations use five OmniFold iterations with gradient-boosted decision-tree classifiers~\cite{Pedregosa:2011sklearn,Ke:2017lightgbm}, and each result below states which configuration of Table~\ref{tab:estimators} it uses. The iteration count and classifier capacity regularize the unfolding. The nominal settings are the scikit-learn defaults, with LightGBM matched to their capacity, and the refinement capacity of the joint-test estimator was chosen in simulation closure studies; no hyperparameter search was performed on data. The two-observable central value uses configuration~(f): the learner and seed of configuration~(a) with negative-weight background subtraction and the refinement capacity of configuration~(e). The five-observable central value uses configuration~(a), with the purity-based subtraction, whose bias is given in Sec.~\ref{sec:closure}, and the three- and four-observable central values use configuration~(e). The two-dimensional central value is that of its systematic-universe ensemble, so its covariance is built with the same estimator. The joint tests use configuration~(e), the joint-test estimator, whose negative-weight treatment and higher-capacity refinement remove most of the bias of the purity method at nominal truth in the highest-$W$ cells (Sec.~\ref{sec:validation}). Configuration~(e) keeps five iterations by a criterion fixed in advance: 10, 15, or 20 iterations did not reduce its model dependence, measured as the largest residual proxy over the truth changes used in its development (\nsec{sec:gbdt-model-dependence}). [TABLE]

**After:**

> All estimator configurations use five OmniFold iterations with gradient-boosted decision-tree classifiers~\cite{Pedregosa:2011sklearn,Ke:2017lightgbm}. The iteration count and classifier capacity regularize the unfolding. The nominal settings are the scikit-learn defaults, with LightGBM matched to their capacity. The refinement capacity of the joint-test estimator was chosen in simulation closure studies. No hyperparameter search was performed on data.
>
> Each result below states which configuration of Table~\ref{tab:estimators} it uses. The two-observable central value uses configuration~(f): the learner and seed of configuration~(a) with negative-weight background subtraction and the refinement capacity of configuration~(e). The two-dimensional central value is reproducible and is that of its systematic-universe ensemble, so its covariance is built with the same estimator. The five-observable central value uses configuration~(a), with the purity-based subtraction, whose bias is given in Sec.~\ref{sec:closure}. The three- and four-observable central values use configuration~(e). The joint tests use configuration~(e), the joint-test estimator, whose negative-weight treatment and higher-capacity refinement remove most of the bias of the purity method at nominal truth in the highest-$W$ cells (Sec.~\ref{sec:validation}).
>
> Configuration~(e) keeps five iterations by a criterion fixed in advance. Its model dependence is measured as the largest residual proxy over the truth changes used in its development, and 10, 15, or 20 iterations did not reduce it. The criterion and its values are given in \nsec{sec:gbdt-model-dependence}. [TABLE]

- **Reason:** S3. (a) Shared settings and their regularizing role: P72's first clause, P73, and P74 split into nominal settings / refinement capacity chosen in simulation closure studies / "No hyperparameter search was performed on data" (its own sentence, so it covers both settings, as the base's closing clause did). (b) Which configuration serves which result: opens with P72's second clause ("Each result below states which configuration of Table II it uses"); then (f) for 2D; then the reproducibility statement, moved here from Sec. IV B (P125; batch b2 deletes it there) and merged with P77: "The two-dimensional central value is reproducible and is that of its systematic-universe ensemble, so its covariance is built with the same estimator" (contains the required substring; keeps the base's "so" link between the ensemble and the estimator); (a) for 5D with its bias pointer; (e) for 3D/4D (P76 split, R10); (e) for the joint tests. The two lines the estimator registry cites ("The two-observable central value uses configuration~(f): the learner and seed"; "configuration~(e), the joint-test estimator, whose negative-weight treatment") are byte-identical. (c) Configuration (e)'s iteration criterion: "fixed in advance" kept; the measure is stated before the outcome (R9); the pointer becomes a closing clause (R7), "The criterion and its values are given in ..." (the note prints 0.314 and 0.384 there; ledger b1-87 N: probe). The source comment for the five-iteration record moved with the sentence it supports. Table II untouched and still follows (c).
- **Rule:** S3, R10, R9, R7
- **KEEP ids touched:** D1 ("a criterion fixed in advance", kept next to the choice)


---

## Changes, paragraph by paragraph: batch b2 (Secs. IV–V), register round r17

Base: `paper_body.tex` at `f0b26234`, lines 354–753. Only the batch copy of `paper_body.tex`
changed, and only inside that range (lines 1–353 and everything from `\section{What limits the estimator}` on are
byte-identical to base). Row ids in brackets are `ledger.md` (rows b2-*)'s.

### IV A. Comparison with the published measurement (S4; R10, R7) [b2-1 … b2-17]

One paragraph of 230 words becomes two (130 and 105 words).

**¶1, agreement.**
- *Before:* "Of the 205 reported bins, 95.1% agree within 10%; the standardized bin differences formed with the published
  uncertainties have an RMS of …. Against the full published covariance, the descriptive covariance-weighted distance
  is χ²/ndf = …, computed with the pseudo-inverse over the 205 bins, which keeps all 205 eigenmodes (rank 205,
  condition number 1.5e12), so that ndf is that rank. It indicates a correlated shape difference, not a normalization
  difference, spread over many eigenmodes of the published covariance, with no single pT or p∥ band carrying more
  than 15% of it."
- *After:* "Of the 205 reported bins, 95.1% agree within 10%. The standardized bin differences formed with the
  published uncertainties have an RMS of …. Against the full published covariance, the descriptive covariance-weighted
  distance is χ²/ndf = …. It is computed with the pseudo-inverse over the 205 bins, which keeps all 205 eigenmodes
  (rank 205, condition number 1.5e12), so that ndf is that rank. It indicates a correlated shape difference, not a
  normalization difference, spread over many eigenmodes of the published covariance. No single pT or p∥ band carries
  more than 15% of it. Figure 1 shows the principal one-dimensional projections."
- *Why:* result first, then how it is computed, one idea per sentence (R10). The pinv/rank detail stays (outline S4:
  it is a fact). The Fig. 1 sentence, verbatim, moves from the end of the old paragraph to the end of the agreement
  paragraph, which is what the figure shows. "it" in "more than 15% of it" keeps the base's antecedent.
- *KEEP:* **K4** ("descriptive", unchanged).
- The mid-line source comment after "of it." is now on its own line at the head of ¶2 (no change to its text).

**¶2, estimator dependence.**
- *Before:* "… in one run with a fixed seed; at the central value's seed, the refined negative-weight subtraction lowers
  … . We quote the LightGBM result as the central value because its covariance uses the same estimator; this learner
  was chosen after both comparisons were known. The central value and the exact-split cross-check, which differ in
  learner and in background treatment, differ by a per-bin median of 1.03% (maximum 17.6%); [note Sec. 3.2]
  describes both."
- *After:* "… in one run with a fixed seed. At the central value's seed, the refined negative-weight subtraction lowers
  … . We quote the LightGBM result as the central value because its covariance uses the same estimator. This learner
  was chosen after both comparisons were known. The central value and the exact-split cross-check differ in learner
  and in background treatment. Their per-bin difference has a median of 1.03% (maximum 17.6%). Both estimators are
  described in [note Sec. 3.2]."
- *Why:* semicolons become full stops (R10); the pointer becomes a closing clause (R7). The purity-based clause keeps
  both of its objects (the ten seeds and the exact-split values) in one sentence, so the purity scope still covers
  the exact-split numbers.
- *KEEP:* **K5 / D1**: the post-selection sentence directly follows the choice it qualifies (ledger b2-14 probes the
  adjacency).

### IV B. Two-dimensional covariance (S5; R4, R7) [b2-20 … b2-40]

**Order.** Blocks and sizes (base ¶ at 413, unchanged); the statistical block and its coverage test (base ¶ at 477,
rewritten); run periods (base ¶ at 464, unchanged); C_model (base ¶ at 439, unchanged, with its comment block). "Beside
the one above" and "(below)" still read correctly in the new order.

**The statistical block (base ¶4), rewritten as a test report.**
- *Before:* "The statistical block is a bootstrap of 300 replicas drawn at the central value's training seed, with the
  background templates also resampled, with a median statistical uncertainty of 0.676%. An earlier version of the
  statistical band, distinct from the quoted block, was scored in a test specified in advance on 100 closure
  pseudo-experiments at a fixed truth. It undercovered in its tails: pooled over experiments and bins, 91.2% of
  standardized residuals fell within two standard deviations, against 95.4% nominal. A post hoc rescoring … removes
  the tail undercoverage: 97.7% … and 78.1% within one. It is not an independent coverage test, because the simulated
  part of the rebuilt band reuses the resampling mechanism of those pseudo-experiments ([note Sec. 5.2]). The
  two-dimensional central value is reproducible, and its covariance is built with the same estimator."
- *After:* "The statistical block, with a median statistical uncertainty of 0.676%, is a bootstrap of 300 replicas
  drawn at the central value's training seed, in which the background templates are also resampled. A coverage test
  specified in advance scored an earlier version of the statistical band, distinct from the quoted block, on 100
  closure pseudo-experiments at a fixed truth. The band failed the test by undercovering in its tails: pooled over
  experiments and bins, 91.2% of standardized residuals fell within two standard deviations, against 95.4% nominal.
  A post hoc rescoring … removes the tail undercoverage: 97.7% … and 78.1% within one. Because the simulated part of
  the rebuilt band reuses the resampling mechanism of those pseudo-experiments, the rescoring is not an independent
  coverage test. The test and the rescoring are described in [note Sec. 5.2]."
- *Why (R4):* what was tested (an earlier band, not the quoted block), against what (100 closure pseudo-experiments at
  a fixed truth), the criterion as the paper states it (the nominal 95.4% within two standard deviations), the
  outcome (failed, 91.2%). Then the post hoc rescoring in one sentence, and its limitation with the reason first. The
  double "with … with" of the first sentence is gone. The pointer leaves its mid-sentence parenthesis (R7).
- *"Failed":* new word, same fact. Table I prints "an earlier band failed coverage" for this row, and the note's
  sec:coverage prints "The band fails: it undercovers in its tails" (ledger b2-28 carries an N: probe for it). No
  criterion value from the note (the [0.9, 1.1] window) was added.
- *Brief rule 4:* the three bound phrases print byte-identically (`with a median statistical uncertainty of
  \SI{0.676}{\percent}`; `against \SI{95.4}{\percent} nominal`; `removes the tail undercoverage: \SI{97.7}{\percent}
  fall within two standard deviations and \SI{78.1}{\percent} within one`). SEC4-RECEIPTS 15/15.
- *Brief rule 5:* (a) "The band failed the test"; (b) "A post hoc rescoring"; (c) "the rescoring is not an independent
  coverage test", with its reason; (d) Table I's 2D row still finds its test in Sec. IV B (`\ref{sec:uq2d}`).
- *Deleted:* the closing sentence on reproducibility (P125), which batch b1 prints in Sec. III. Ledger b2-32,
  `COLLAPSED→III`, probe fails in this copy by design.
- *Comments:* the r16 comment about that sentence is removed with it; an r17 comment records the move (paraphrased,
  not the printed text) and the source of "failed".
- *KEEP:* **K6** is not in this paragraph in the base either; the paper states the quoted block's untested coverage in
  Sec. VIII A (batch b3's range). **K8** (the omission list, ¶1) is unchanged.
<!-- absence-ok: quotes or summarizes printed paper text, whose paragraph in paper_body.tex carries its own Search line; not a new absence claim -->

### V A. Normalization and closure (S6; R10) [b2-41 … b2-55]

One paragraph of 270 words becomes three (104, 95, 74 words).

**¶1, normalization and signal-only closure checks.** P126–P128 unchanged; the `% Search:` line stays in this paragraph,
beside the configuration-(e) sentence it serves. P129's semicolon becomes a full stop (3D and 4D closures in two
sentences). "These closure tests reweight the simulated signal only." closes the paragraph.

**¶2, closure with backgrounds and the purity bias.**
- *Before:* "Figure 2 shows that, with the purity-based background subtraction, end-to-end pseudo-experiments at
  nominal truth reproduce the input except in the highest-W cells, which are biased by up to 4% in simulation, about
  one quoted standard deviation in one (Eavail,W) cell. This bias is not included in the quoted uncertainties. … leaving
  up to 1% in some joint cells; on data the treatments differ by at most 1.4%."
- *After:* "Figure 2 shows that, with the purity-based background subtraction, end-to-end pseudo-experiments at nominal
  truth reproduce the input except in the highest-W cells. These cells are biased by up to 4% in simulation, about one
  quoted standard deviation in one (Eavail,W) cell. This bias is not included in the quoted uncertainties. … leaving up
  to 1% in some joint cells. On data, the two treatments differ by at most 1.4%. The closure studies are described in
  [note Sec. 5.1]."
- *Why:* result and exception, then the size, then the omission (R10, E6). The pointer stays verbatim at the end; the
  note's tab:closure-map lists both the signal-only and the background-inclusive tests, so it serves ¶1 and ¶2.
- *KEEP:* **K9** "except in the highest-W cells"; **K10** "This bias is not included in the quoted uncertainties." as its
  own sentence (verbatim). Bound phrases `biased by up to \SI{4}{\percent} in simulation`, `reduces it to below
  \SI{0.3}{\percent}`, `leaving up to \SI{1}{\percent} in some joint cells`, `differ by at most \SI{1.4}{\percent}`
  unchanged.
- *Comments:* the background-bias source lines moved from ¶1's comment block to ¶2, next to the sentences they support.

**¶3, the two-observable closure that motivates (f).** The 61-word sentence (P135) is split into the separation count
and the distances from truth. The decision-worded sentence "The two-dimensional result therefore uses the refined
estimator, configuration (f) (…)" is verbatim.

### V B. Generator-sized truth changes (language only) [b2-56 … b2-62]

- P138: "…, $W\ge3$ GeV, with or without background, so background subtraction alone does not explain the residual."
  → "…, $W\ge3$ GeV. The residual appears with or without background, so background subtraction alone does not
  explain it."
- P140: "… within the quoted total uncertainty in about half of those cells, that of the covariance of Sec. V D." → "…
  within the quoted total uncertainty in about half of those cells. This total uncertainty is that of the covariance of
  Sec. V D." (The trailing appositive becomes its own sentence; the bound phrases `by up to \SI{74}{\percent} at high
  $W$`, `it is \SIrange{16}{31}{\percent} in the most affected` and `within the quoted total uncertainty in about half
  of those cells` print once each.)
- Every number, cell and condition unchanged. Rule: R10.

### V C. Coverage (language only) [b2-63 … b2-68]

- P147: "The rate change itself is recovered, and apart from a minor effect the intervals are not too narrow." → "…
  recovered, and, apart from a minor effect, the intervals are not too narrow." Commas only. Nothing else changed.

### Fig. 3 caption (S14) [b2-72]

- *Before:* "Panel (a) uses the random seeds of the estimator's development studies, and panel (b) separate seeds that
  were later also used in its development."
- *After:* "Panel (a) uses the random seeds of the estimator's development studies. Panel (b) uses separate seeds,
  which were later also used in the estimator's development."
- *Why:* the elliptical second clause gets its verb, and "its" (which could read as panel (b)'s) becomes "the
  estimator's", the base's own antecedent. Both facts kept: (a)'s seeds are those of the development studies; (b)'s
  are separate, and were later also used in the development. D1 (the disclosure that qualifies "not used while it was
  chosen") kept. No rater rewrite adopted: sol2.3's "both sets were used during estimator development" drops
  "separate" and "later"; sol2.2's "subsequently used for further development" is close but adds "further".

### V D. Covariance and estimator stability (S7; R10) [b2-74 … b2-82]

- **¶1.** The two semicolons become full stops ("… no other five-observable covariance. The calibration of the joint
  tests in Sec. VII does not use it." and "… beyond a stability limit of 5%. We therefore quote no covariance-based
  generator significance."). The pointer "Ref. [14], Secs. 9.6 and 9.6" becomes `\nsec{sec:eavailw-construction}`,
  printing "Ref. [14], Sec. 9.6". Both labels resolve to 9.6 (`main_note.aux`; ledger b2-79 has both N: probes);
  sec:eavailw-adopted is the "Status" paragraph inside that subsection, so the seed studies and the status are in the
  section cited. A source comment records this. **K11** ("For one pair of seed settings") unchanged.
- **¶2.** "The estimators are also unstable at the level of rounding: rounding-level input changes move …, as they
  move those of the baseline estimator (2.5), so the refinement fails …" → three sentences: the instability; the 2.6
  and the baseline's 2.5 (the "as they move" comparison kept); "The refinement therefore fails a data-stability
  requirement of at most 0.3 (median) and 1.0 (maximum) statistical standard deviations." A comma after "For the
  joint-test estimator". R10.

### V E. Reporting definitions and the precision target (language; R9) [b2-83 … b2-91]

- **¶1.** *Before:* "With it, none of the reporting definitions of a five-observable measurement tested in the study
  meets our 10% precision target, a 10% median half-width for the total 68% interval." *After:* "Our precision target
  is a 10% median half-width for the total 68% interval. With the envelope added, none of the reporting definitions of
  a five-observable measurement tested in the study meets this target." The target is defined before the verdict, as
  the envelope already was (R9). "With it" names its referent; "added" restates the definition sentence's "adds it
  linearly", so the verdict still reads as conditional on the linear prescription. **K12** kept (definition before
  claim; P175 and P176 verbatim). Later "it" (the target) unchanged.
- **¶2.** A comma after "Over these definitions". Otherwise unchanged.
- **Table III:** caption and cells untouched.

### Not touched in this range

Fig. 1, Fig. 2, Fig. 4 captions; Table III; IV B ¶1, run periods, C_model paragraphs (moved whole, text identical); V C
¶1; every `\label`, `\section`, `\subsection`; every `\ref`/`\nsec`/`\napp` target except the V D pointer (S7).

---

## Changes, paragraph by paragraph: register round r17, batch b3 (Secs. VI-VII)

Base: `paper_body.tex` at `f0b26234`, lines 754-1123. Only `paper_body.tex` changed, and only inside that
range (first changed base line 758, last 1119). Base line numbers below are where each paragraph, or its leading source comment, starts. `main_paper.tex` is byte-identical to the base. Row ids in brackets
are `ledger.md` (rows b3-*)'s. Text is quoted as printed, with macros as in the source.

KEEP ids touched in this batch: **K2, K3, K13, D1, D2, D3**, plus the brief's "descriptive" for the target-corrected
evaluations. None was weakened, and none was moved.

### VI. What limits the estimator

#### VI ¶1 (base 759): language, R10 [b3-1 to b3-5]

- **Before:** "Three results point to the unfolded result retaining part of its prior: the residual under a
  generator-sized change of the truth in Sec. V B, which we interpret as regularization bias; the envelope of Sec. V E,
  which tracks the same bias and alone exceeds the precision target in two of the three tested reporting definitions;
  and the upward displacement of the external nulls by the estimator's pull toward its prior, which the calibration of
  Sec. VII E reproduces."
- **After:** "Three results point to the unfolded result retaining part of its prior. The first is the residual under a
  generator-sized change of the truth in Sec. V B, which we interpret as regularization bias. The second is the envelope
  of Sec. V E, which tracks the same bias and alone exceeds the precision target in two of the three tested reporting
  definitions. The third is the upward displacement of the external nulls by the estimator's pull toward its prior,
  which the calibration of Sec. VII E reproduces."
- **Reason:** one 72-word sentence with two semicolons becomes four sentences. "We interpret as" stays, so the
  regularization-bias reading stays an interpretation. The miscoverage sentence ("… whether that bias has the same
  origin is not established") is unchanged.
- **KEEP:** none touched. The source comment gains an r17 line.

#### VI ¶2 (base 770, 224 words): S8, R10; K13 [b3-6 to b3-15]

The CLAIM-ADDITION D-ID block is split into two paragraphs. Both stay between the `% CLAIM-ADDITION D-ID BEGIN`/`END`
markers, and the block's record comment is unchanged, with one added r17 line.

- **¶2, the diagnostic's result (142 words).** The text is the base's, with two semicolons replaced by full stops:
  - "… the tree approximation dominates only 15. Most of the 144 (121) lie in quantities that …";
  - "… but not for every change. The long runs do not converge, so this rests on their last iterates."
- **¶3, its population and scope (82 words):**
  - **Before:** "The diagnostic is binned, signal-only and noise-free, with the detector response fixed at the simulation's, and
    covers only the residuals whose diagnosis is stable under the truth resolution (38% of the joint-cell residuals
    above 2%). What unbinned information could recover, the coverage failure, and the validity of any interval lie
    outside its scope. Within that scope, the residual is consistent with … (note Sec. 9.3)."
  - **After:** "The diagnostic is binned, signal-only and noise-free, with the detector response fixed at the simulation's. It
    covers only the residuals whose diagnosis is stable under the truth resolution (38% of the joint-cell residuals
    above 2%). What unbinned information could recover, the coverage failure, and the validity of any interval lie
    outside its scope. Within that scope, the residual is consistent with … (note Sec. 9.3)."
- **What stays:**
  - The out-of-scope sentence is word for word the base's, as r15's record requires.
  - "Is consistent with … rather than" stays. The E9 draft's "attributes … not to" was not used, because it may
    strengthen the claim.
  - The population (binned, signal-only, noise-free, 38%) comes immediately before the conclusion it scopes (K13).
- **KEEP:** K13.

#### VI ¶3 (base 807): unchanged.

### VII. Application: comparison with generator predictions

#### VII ¶1 (base 818): language, R10; S9 declined [b3-18 to b3-23]

- One sentence is split at its colon: "… but it would still need the same response model. Each external prediction would
  have to be folded through …".
- "We have not compared their power with that of a reconstruction-level test." is unchanged and stays in this
  paragraph (S9 declined; source comment at base :818-820 unchanged).
- **KEEP:** D3 (a negative result stated plainly).

#### VII A ¶1 (base 837): R7 [b3-24 to b3-26]

- **Before:** "… the region of the established low-recoil discrepancy [18,25] (comparisons with pion final-state-interaction
  variations, GENIE's Valencia 2p2h component, and the published measurement: Ref. [14], Secs. 7.7 and 7.8)."
- **After:** "… the region of the established low-recoil discrepancy [18,25]. Comparisons with pion final-state-interaction
  variations, GENIE's Valencia 2p2h component, and the published measurement are given in Ref. [14], Secs. 7.7 and
  7.8."
- **Reason:** a parenthetical pointer becomes a plain closing clause (R7). The targets are unchanged.

#### VII A ¶2 (base 851): unchanged.

#### VII A ¶3 (base 859): R10 [b3-29, b3-30]

- The semicolon after "and at high W" becomes a full stop, so "GiBUU, the most deficient, stops at …" begins its own
  sentence. Nothing else changed.

#### VII B ¶1 (base 874): R10; K2 [b3-34 to b3-38]

- "… with every fine-cell integral held fixed, and the background is the Tune v1 simulation's, with its uncertainty
  bands." becomes two sentences: "… held fixed. The background is the Tune v1 simulation's, with its uncertainty
  bands."
- "We call this hypothesis the hybrid null" (K2) and the three-properties sentences are unchanged.
- **KEEP:** K2 (unchanged, in a touched paragraph).

#### VII B ¶2 (base 892): R10 [b3-39 to b3-44]

- "… and with it the efficiency and the migrations, and the lateral detector bands enter as …" is split at the second
  "and": "… and the migrations. The lateral detector bands enter as …".
- "Poisson pseudo-data and background are drawn from it, and the joint-test estimator unfolds the pseudo-data with the
  other half; a 1.4% normalization …" becomes "Poisson pseudo-data and background are drawn from the source half, and
  the joint-test estimator unfolds the pseudo-data with the other half. A 1.4% normalization …".
- **"It" becomes "the source half".** Once the lateral-band clause is its own sentence, "it" would have no
  antecedent. The note's flowchart (`sec_joint.tex`, "source half reweighted to G; nuisance draws; Poisson
  pseudo-data and background") confirms the reading; the ledger probes it [b3-42].

#### VII B ¶3 (base 910): R10 [b3-45 to b3-50]

- "… and the prediction μ_G; it tests the rate and the shape together …" becomes "… and the prediction μ_G. It tests
  the rate and the shape together …".
- "… adds the prediction's own finite-sample variance to V, a Ledoit–Wolf-shrunk covariance [26] of … pilot
  pseudo-experiments …" becomes "… to V. Here V is a Ledoit–Wolf-shrunk covariance [26] of … pilot
  pseudo-experiments …". The appositive becomes a definition sentence.

#### VII C ¶1-2 (base 927, 937): unchanged.

D2 (A1, A2) is named once, in ¶2, unchanged. The theorem sentence was not split: splitting it could let its conclusion
read as unconditional.

#### VII C ¶3 (base 955): S10, R9, R10; D1, D2 [b3-56 to b3-62]

- **Before:** "The test design was fixed before any observed statistic was computed; its reviewers had already seen
  descriptive per-cell residuals of the data. The computing time available to the calibration was later increased by a
  bounded amount after the observed p values had become visible. The error control above does not depend on this,
  because it holds for any rule that decides when sampling stops. Computing time limits interrupted or prevented
  \jtLostCal calibration and \jtLostPow power pseudo-experiments, and the decisions use the completed ones. When rerun,
  none of the lost calibration pseudo-experiments reaches the observed statistic in any test or shifted null, so their
  outcomes change no decision. Independently written code reproduces every p value and decision. The predeclared
  design and the rerun are described in Ref. [14], Secs. 10.3 and 10.6."
- **After:** "The test design was fixed before any observed statistic was computed. Its reviewers had already seen
  descriptive per-cell residuals of the data. After the observed p values had become visible, the computing time
  available to the calibration was increased by a bounded amount. Under A1 and A2, the error control holds for any
  rule that decides when sampling stops, so it does not depend on this extension. Computing time limits interrupted or
  prevented \jtLostCal calibration and \jtLostPow power pseudo-experiments, and the decisions use the completed ones.
  When rerun, none of the lost calibration pseudo-experiments reaches the observed statistic in any test or shifted
  null, so their outcomes change no decision. Independently written code reproduces every p value and decision. The
  predeclared design and the rerun are described in Ref. [14], Secs. 10.3 and 10.6."
- **The order** follows S10: design fixed, with the reviewers' prior look (D1); the extension, with its timing first
  (D1, at the choice, DECISION-20261004 §3); its consequence for the error control; the lost draws and the rerun in two
  sentences; the recomputation; the pointer.
- **The design sentence.** It is split at its semicolon. "Already" keeps the order of events.
- **The extension.** "Later" is dropped, because the fronted "After the observed p values had become visible" carries
  the time. The record's word "become visible" is kept (r16 review fix 2).
- **The error-control sentence (KEEP, narrowed).** It now names its condition first, as R9 asks and as the brief
  requires ("do not write it as unconditional"). The reason is unchanged: the control holds for any rule that decides
  when sampling stops.
  - "Under A1 and A2" is the hypothesis of the bound in ¶2 ("Under them, the probability … is below the threshold,
    whatever rule determines when sampling stops").
  - The note's `sec:joint5d-frozen` states the same bound, "including the budget extensions" [b3-59].
  - Nothing is added beyond what ¶2 already states. The rater rewrites ("preserves the stated error control", "remains
    valid under this stopping rule") were not adopted.
- **The lost-draw and rerun sentences are word for word the base's.** They are the rewording of DECISION-20261005 §5
  that r16 fixed (source comment above the paragraph), so their meaning is exactly as before.
- **KEEP:** D1 (the design fixed with the reviewers' look; the budget extension, at the choice). D2 (A1 and A2 named,
  by label only, as the condition of the bound).

#### VII D ¶0 (base 982): unchanged. It keeps "concern the hybrid nulls" (K2).

#### VII D (i) (base 985): R10; D2 [b3-64 to b3-67]

- "… of the whole change from the coarse test grid, so convergence of the fine grid has not been shown and the residual
  below it is unmeasured and potentially material." becomes "… of the whole change from the coarse test grid.
  Convergence of the fine grid has therefore not been shown, and the residual below it is unmeasured and potentially
  material."
- "… shrink geometrically; the measured L2 ratios also allow slower convergence." becomes two sentences.
- **The Search line** (`% Search: below the fine grid; … @ afb7e1faddfb`) stays in the paragraph. A local run of
  `absence_claims.py`'s patterns over every changed paragraph finds one match ("unmeasured", here), and this Search
  line covers it.
- **KEEP:** D2 (condition (i)).

#### VII D (ii) (base 998, 199 words): S11, R9, R10; D1-type disclosure [b3-68 to b3-77]

`\label{sec:response}` stays where it was, after the run-in heading.

- **¶(ii)a, the omitted band and why it matters (113 words):**
  - "It has no band for the calorimetric hadronic-energy response, whose uncertainty in MINERvA's recoil-energy
    analyses is derived from …" becomes "It has no band for the calorimetric hadronic-energy response. In MINERvA's
    recoil-energy analyses, the uncertainty of that response is derived from test-beam calorimetry [29] and rises to
    10% at …".
  - "The omission matters for the rejections: restricted to the matched (pT,p∥) projection …, the calibrated tests do
    not reject GENIE 2.12.10 CV (p = … in total and … in shape, a post hoc observation), so …" becomes "The omission
    matters for the rejections. In a post hoc observation, the calibrated tests restricted to the matched (pT,p∥)
    projection of Sec. VII E do not reject GENIE 2.12.10 CV (p = … in total and … in shape), so the information that
    rejects it involves the hadronic axes, on which a response band would act."
  - "A post hoc observation" is kept as a disclosure and now opens the sentence it qualifies (R9). The "so" inference
    stays inside that sentence.
- **¶(ii)b, the ±4% exploratory study and its limits (93 words), a new paragraph:**
  - **Before:** "In an exploratory sensitivity study, scaling … by ±4%, the level …, and re-unfolding the data leaves every
    rejection in place against the original null distributions, with the observed statistics moving by up to about
    11%. The study regenerates no null distribution and tests no other form or size of response change, and neutrons
    and higher-momentum hadrons, which matter at high W, lie outside the test-beam sample; Ref. [14], Sec. 10.8 lists
    the effects it does not test."
  - **After:** "In an exploratory sensitivity study, the simulation's reconstructed recoil energy is scaled by ±4%, the
    level of data–simulation agreement reported for test-beam protons, pions, and electrons of 0.35–2.0 GeV/c [29], and
    the data are re-unfolded. Every rejection stays in place against the original null distributions, and the observed
    statistics move by up to about 11%. The study regenerates no null distribution and tests no other form or size of
    response change. Neutrons and higher-momentum hadrons, which matter at high W, lie outside the test-beam sample. The
    effects the study does not test are listed in Ref. [14], Sec. 10.8."
  - The method comes first and the outcome follows (R9). Each limit is a sentence of its own (R10). The pointer
    becomes a closing sentence (R7).
  - "Exploratory", "against the original null distributions", "up to about 11%" and every limit are unchanged. The
    source comment stays with the paragraph, and an r17 line is added.
- **KEEP:** the post hoc disclosure (the brief's "a post hoc observation"; filed under D1, a post hoc result disclosed
  at its point). The omitted recoil-response band stays (R6's list of disclosures to keep).

#### VII D (iii), (v)-(vi): unchanged.

#### VII D (iv) (base 1026): R10 [b3-79 to b3-84]

- "The resulting shift, at most about 0.07 null standard deviations and measured for the mean only, without noise or
  nuisance draws, enters as the upper-bound shift D." becomes "The resulting shift enters as the upper-bound shift D.
  It is at most about 0.07 null standard deviations, measured for the mean only, without noise or nuisance draws."
- "… resolved no change of the null distributions, and under an extrapolation … all ten decisions remain rejected."
  becomes two sentences: "… resolved no change of the null distributions. Under an extrapolation to the full
  simulation that is conservative by design, all ten decisions remain rejected."

#### VII E ¶1 (base 1047): S12, R10; "descriptive" [b3-86 to b3-94]

- The CH sentence is split at its semicolon: "… does not survive that correction robustly. GiBUU's deep-inelastic events
  on hydrogen do not conserve energy, which affects its correction and possibly its carbon prediction."
- "These target-corrected evaluations are descriptive. The decisions … stand." is unchanged (DECISION-20261020; r16).
- "… up to a multiplier of about 5.2; it probes that one direction." becomes "… up to a multiplier of about 5.2. The
  scan probes that one direction."
- **S12, the pointer.**
  - **Before:** "… are given in Ref. [14], Secs. 10.9, 10.5, and 10.5."
  - **After:** "… are given in Ref. [14], Secs. 10.9 and 10.5."
  - The `N-sec:joint5d-kappa` reference is dropped. Its target, the paragraph "Sensitivity to the sub-fine-grid
    residual" (`sec_joint.tex`:478), lies inside note subsection 10.5 "Decisions" (`sec:joint5d-results`,
    `sec_joint.tex`:416-511), which the pointer still cites. The ch, scan and null-distribution facts therefore all stay
    pointed to.
  - A source comment records this.
- **KEEP:** "descriptive" (unchanged).

#### Table IV (base 1074): unchanged

The caption and every cell are byte-identical to the base (checked by extracting the `table` environment from both
files). The ledger's sentence P270 changes only because the paragraph after the table was split [b3-95].

#### VII E ¶2 (base 1102): R10; K2, K3 [b3-96 to b3-103]

- The first sentence is split at its semicolon: "… into each null distribution. The disagreements they recover were
  already established by …".
- "Restricting the same calibrated tests to matched 3×3 coarse projections …, gives p<0.05, without a multiplicity
  correction, for every test in at least one of the two projections, so this study provides no evidence of …" becomes
  two sentences: "Restricted to matched 3×3 coarse projections …, the same calibrated tests give p<0.05, without a
  multiplicity correction, for every test in at least one of the two projections. This study therefore provides no
  evidence of additional discrimination from the joint five-observable information."
- The power sentence is split at its semicolon: "… with 0.23. At the GENIE 2.12.10 null the shape powers are 0.74,
  0.02, and 0.00."
- **KEEP:** K3 ("no evidence of", unchanged) and K2 ("global assessments of the hybrid nulls", unchanged).

### Not done, by design

- **No fact moved to the note.** No new claim, number, citation or label was added.
- **S9 was not done** (declined).
- **The VII E ¶1 split was not done.** That paragraph carries three ideas (decisions and CH, scan, null locations), but
  the outline proposes only S12 for it, so it was not split into paragraphs.

---

## Changes, batch b4: Sec. VIII (opening paragraph and VIII A), register round r17, move S13

Base: `paper_body.tex` at `f0b26234`, lines 1124–1193. Every change lies inside that range (diff hunks start at
base line 1140). Sentence ids are those of `check_ledger.py --list`.

### VIII ¶1 (opening paragraph): unchanged

- P275–P278 print verbatim. The outline proposes no move for this paragraph, so none was made.
- **KEEP touched:** K14 ("provided the calibration is exact") stays in this paragraph, byte-identical.

### VIII A: source comment block

- One comment pair added at the head of the existing block: "Register round r17 (S13; R2, R6, R10): …". It says the
  nine items, their order, facts and conditions are unchanged, so the item-numbered source list still holds.
- The block stays contiguous with the list. The three `% Search:` lines stay immediately before `\begin{enumerate}`,
  with no blank line between the comment block and `\end{enumerate}`. The absence-claim paragraph runs from line 1141 of the
  edited file to `\end{enumerate}`; it holds 3 Search lines, and both absence patterns it matches (has-not-been-run,
  no-coverage) sit inside it (checked with `tools/registry/absence_claims.py`'s own `paragraph_bounds` and `matches`).
- No printed text was moved into a comment (a 6-word swallowed-text scan, the `swallowed_text.py` rule, finds 0 runs).

### VIII A: the nine items (S13; R2, R6, R10)

The order already follows the outline's grouping: 2D (items 1–2), five observables (3–5), the (Eavail, W) map (6), the
generator tests (7–9). No item was added (S9 declined) and none removed. The list's mean sentence length falls from
22.1 to 16.4 words (17 → 24 sentences).

<!-- absence-ok: this record quotes the paper's own Sec. VIII A items, before and after, whose paragraph carries its Search lines in paper_body.tex; it is not a new claim that a result does not exist -->
#### Item 1 (2D covariance)
- **Before (P279–P281):** "The two-dimensional covariance has not been independently validated. Neither its
  statistical block nor the total has had a coverage test, no coverage is claimed on independent simulated samples or
  simultaneously over all reported bins and projections, and the covariance provides no calibrated significance for
  generator comparisons. Its run-period block is built from … cannot fail."
- **After:** "The two-dimensional covariance has not been independently validated. The coverage of its statistical
  block and of the total has not been tested. We claim no coverage on independent simulated samples or simultaneously
  over all reported bins and projections. The covariance provides no calibrated significance for generator
  comparisons. Its run-period block is built from … cannot fail." (headline and run-period sentence verbatim)
- **Reason:** the three-clause "Neither … nor …, no …, and … no …" sentence becomes three declaratives, one negation
  each. The consequence for the reader (no calibrated significance) is its own sentence.
- **Rule:** R10, R6, S13. **KEEP touched:** K6 (coverage of the 2D statistical block "has not been tested", now in
  those words), K7 (verbatim).
<!-- absence-ok: this record quotes the paper's own Sec. VIII A items, before and after, whose paragraph carries its Search lines in paper_body.tex; it is not a new claim that a result does not exist -->
#### Item 2 (2D learner and shape difference)
- **Before (P282–P283):** "The learner … was selected after both comparisons with the published result were known, so
  the benchmark is a reproduction rather than an independent validation. The source of its correlated shape
  difference has not been identified."
- **After:** "The learner … was selected after both comparisons with the published result were known. The benchmark
  is therefore a reproduction rather than an independent validation. The source of the correlated shape difference
  from the published result has not been identified."
- **Reason:** the disclosure and its consequence become two sentences ("so" → "therefore", same inference). "its"
  had two candidate antecedents once split; "from the published result" names the comparison that Sec. IV A defines
  (the shape difference is measured against the published covariance).
- **Rule:** R10, R6, S13. **KEEP touched:** K5 and D1 (the post-selection disclosure and its inference, wording kept).
<!-- absence-ok: this record quotes the paper's own Sec. VIII A items, before and after, whose paragraph carries its Search lines in paper_body.tex; it is not a new claim that a result does not exist -->
#### Item 3 (source of the residual bias)
- **Unchanged (P284).** It is already one plain declarative with one negation. The base states no consequence, and
  adding one would be a new claim.
<!-- absence-ok: this record quotes the paper's own Sec. VIII A items, before and after, whose paragraph carries its Search lines in paper_body.tex; it is not a new claim that a result does not exist -->
#### Item 4 (regularization residual)
- **Before (P285):** "The residual under the generator-sized truth changes of Sec. V B, interpreted as regularization
  bias, is included in no quoted uncertainty; the five-observable covariance omits it."
- **After:** "The residual under the generator-sized truth changes of Sec. V B is interpreted as regularization bias.
  No quoted uncertainty includes it, and the five-observable covariance omits it."
- **Reason:** definition (what the residual is taken to be) before claim (R9); the semicolon becomes a sentence break
  (R10). "Also/in particular" was not added: the paper does not say the 5D covariance is a quoted uncertainty.
- **Rule:** R9, R10, S13. **KEEP touched:** none (K10 is the purity bias in V A, batch b2/b3, not this residual).
<!-- absence-ok: this record quotes the paper's own Sec. VIII A items, before and after, whose paragraph carries its Search lines in paper_body.tex; it is not a new claim that a result does not exist -->
#### Item 5 (seed dependence)
- **Before (P286–P287):** "The seed dependence … rests on one seed pair. The spread over seed pairs, and the seed
  sensitivity of the five bands built at a fixed seed, which carry \pinnedBandsSqrtTr % of sqrt(Tr C), have not been
  measured."
- **After:** "The seed dependence … rests on one seed pair, and the spread over seed pairs has not been measured. The
  five bands built at a fixed seed carry \pinnedBandsSqrtTr % of sqrt(Tr C), and their seed sensitivity has not been
  measured."
- **Reason:** the compound subject with an embedded relative clause (two unmeasured quantities and a number) becomes
  two sentences: the seed-pair basis with its unmeasured spread, then the fixed-seed bands' share with their unmeasured
  sensitivity. The value macro is unchanged (prints 26.0 %).
- **Rule:** R10, S13. **KEEP touched:** K11 ("rests on one seed pair", verbatim).
<!-- absence-ok: this record quotes the paper's own Sec. VIII A items, before and after, whose paragraph carries its Search lines in paper_body.tex; it is not a new claim that a result does not exist -->
#### Item 6 (map closure)
- **Unchanged (P288).** Already one plain declarative; no consequence is stated in the base, and none was added.
<!-- absence-ok: this record quotes the paper's own Sec. VIII A items, before and after, whose paragraph carries its Search lines in paper_body.tex; it is not a new claim that a result does not exist -->
#### Item 7 (carry-over, condition (i))
- **Before (P289):** "… (condition~(i)); showing this would require a demonstrated bound on the residual below the
  fine grid."
- **After:** "… (condition~(i)). Showing this would require a demonstrated bound on the residual below the fine grid."
- **Reason:** the semicolon becomes a sentence break (R10). The condition ("only if … no more than ±κ δ_fine along
  δ_fine (condition (i))") is byte-identical, and so is the requirement.
- **Rule:** R10, S13. **KEEP touched:** D2 (condition (i) named once).
<!-- absence-ok: this record quotes the paper's own Sec. VIII A items, before and after, whose paragraph carries its Search lines in paper_body.tex; it is not a new claim that a result does not exist -->
#### Item 8 (hadronic response, condition (ii))
- **Before (P290–P291):** "The net effect on each $p$ value of the missing calorimetric hadronic-response band
  (condition~(ii)) has not been measured. The rejections remain conditional on the simulation's hadronic response,
  and their physical interpretation would require a response band drawn through the calibration."
- **After:** "The detector model has no calorimetric hadronic-response band (condition~(ii)), and the net effect of
  the missing band on each $p$ value has not been measured. The rejections remain conditional on the simulation's
  hadronic response. Their physical interpretation would require a response band drawn through the calibration."
- **Reason:** the base's long fronted subject ("The net effect on each p value of the missing … band (condition
  (ii))") put the fact (the band is missing) inside a noun phrase. The item now states the omission first, then
  what is unmeasured, then the consequence, and then what interpretation would need. "The detector model has no …
  band" is condition (ii)'s own statement (base line 1001, "It has no band for the calorimetric hadronic-energy
  response"), not a new fact.
- **Rule:** R9, R10, S13. **KEEP touched:** D2 (condition (ii)).
<!-- absence-ok: this record quotes the paper's own Sec. VIII A items, before and after, whose paragraph carries its Search lines in paper_body.tex; it is not a new claim that a result does not exist -->
#### Item 9 (calibration validity, A1)
- **Before (P292–P294):** "The calibration is valid for the simulated null to the extent that … (A1). No rejection
  rate has been measured for null pseudo-data processed like the data, which would require an independent simulation
  sample: every pseudo-experiment resamples the same simulated events. The conditioning … has not been validated."
- **After:** "The calibration is valid … (A1). Every pseudo-experiment resamples the same simulated events, so
  measuring a rejection rate for null pseudo-data processed like the data would require an independent simulation
  sample. No such rate has been measured. The conditioning … has not been validated." (first and last sentences
  verbatim)
- **Reason:** the base sentence led with the absence and gave its reason after a relative clause and a colon. The new
  order is fact (the shared simulated events), then what testing A1 would need, then the absence, one negation per
  sentence (E10's pattern). The colon's "because" relation is carried by "so".
- **Rule:** R5, R10, S13. **KEEP touched:** D2 (A1 named once, its "to the extent that" verbatim).

### Not changed, and why

- No item was regrouped: the base order already matches the outline's four groups. No group headings or lead-in
  sentence naming the groups were added, because the base gives no group label for items 3 and 6 that a heading
  could state without a new scope claim.
- No consequence was added to items 3, 4, 5 and 6: the base states none, and each candidate would be a new claim.
- No `\label`, `\ref`, pointer, macro or citation changed. The three `\ref`s (sec:coverage, sec:departure,
  sec:central) stay in their items.
