# r22 Step 2 agy triage: chunks 01-03 (68 rows)

Checked against the worktree `$WT` (HEAD ee520a19e; base 9d3054f9). "cur" means comment-stripped, whitespace-collapsed
current text in `$WT/docs/analysis-note/`; "base" means `git show 9d3054f9:docs/analysis-note/<file>`.

| chunk | Q | file tag | class | evidence | fix |
|---|---|---|---|---|---|
| chunk01 | Q1 | sec_execsummary.tex ES1 | MOVED-OK | Scope sentence prints once in cur sec_intro.tex: "\paragraph{Scope.} The results hold for one implementation of unbinned OmniFold, applied to one data set, and for the configurations, observables and deformations tested." The generator-tests sentence prints verbatim in cur sec_execsummary.tex, opening the generator-test paragraph. The summary's `\S\ref{sec:intro}` pointer is gone; this is a ref drop, not a fact. | — |
| chunk01 | Q2 | sec_execsummary.tex ES9 | SUPPORTED | Base sec_method.tex config list: "(a), the same learner with purity-based background subtraction: the five-dimensional central value"; "(e) ... a deterministic LightGBM variant with the unbinned negative-weight background treatment ... refinement classifier"; "(f), the nominal LightGBM configuration above with refined negative-weight subtraction". | — |
| chunk01 | Q4 | sec_execsummary.tex ES16 | SUPPORTED | The inserted sentence is verbatim base ES1: "The generator tests are an application that illustrates calibrated inference with a biased estimator." "joint five-dimensional" comes from the cut base label "Application: joint five-dimensional generator tests". | — |
| chunk01 | Q5 | sec_execsummary.tex ES22 | SUPPORTED | Base sec_joint.tex: "NuWro~21.09 and GiBUU~2019 were generated on carbon ... These target-corrected evaluations are descriptive; the decisions ... are unchanged". Base sec_systematics.tex: "jointly re-unfolding all reweightable knob bands and the flux multisim". Base sec_fps.tex: "only tier~1 is interpreted as an acceptance-supported measurement"; "Tier~2, prior-extrapolated". Base sec_validation.tex: "Coverage $C_k$ is the fraction of all (toy, bin) pairs with $|z|\le k$", with z in units of the band's spread. | — |
| chunk01 | Q6 | sec_intro.tex IN12 | SUPPORTED | The next base sentence: "H1 published the first real-data applications". "Method paper" to "method proposal" is wording. | — |
| chunk01 | Q7 | sec_intro.tex IN17 | SUPPORTED | Base sec_systematics.tex: the unified throw works "by jointly re-unfolding all reweightable knob bands and the flux multisim, perturbed simultaneously per event". | — |
| chunk01 | Q8 | sec_intro.tex IN20 | RATER-WRONG | "That route" is the preceding sentence's "negatively-weighted simulated events as the natural in-method subtraction". The sentence still prints just before it in cur sec_intro.tex. | — |
| chunk01 | Q15 | sec_intro.tex IN46 | SUPPORTED | Base app_pet_pointer.tex: "We are developing unfolding with point-cloud transformer (PET) representations of the full event ... That work is in progress". The appendix title "Future work: point-cloud representations" still prints. | — |
| chunk01 | Q16 | sec_experiment.tex EX7 | SUPPORTED | Base paper_body.tex:29: "in the form of pre-selected analysis ntuples (AnaTuples)". This source is the companion paper, not a note section. "production AnaTuples" still prints in cur app_codebase.tex ("reads production AnaTuples") and in app_release.tex ("earlier production of MINERvA open-data AnaTuples"). | — |
| chunk01 | Q17 | sec_experiment.tex EX14 | MOVED-OK | The flags go to the ledger home (B02-5). `2d-unfolding/2D_OMNIFOLD_REFERENCE.md` holds `isMinosMatchTrack==1` and `minos_trk_is_ok==1`. "Near detector" is in base sec_experiment.tex:5: "The magnetized MINOS near detector ... serves as the muon spectrometer". | — |
| chunk01 | Q20 | sec_experiment.tex EX23 | MOVED-OK | The count prints in cur sec_experiment.tex: "The simulated sample contains $32\,849\,103$ true signal events". The merger and the 100 GB size go to the ledger home `2D_OMNIFOLD_REFERENCE.md` ("trees exceed ROOT's default 100 GB", "Python `TFileMerger` ... to 300 GB"), per B02-11. | — |
| chunk01 | Q26 | sec_method.tex ME27 | MOVED-OK | The per-letter mapping prints in cur Table tab:estimators-matrix: (d) "background bias; generator-sized $\Eavail$ change"; (e) "three- and four-observable central values ...; sixteen-cell ...; precision study ...; generator tests"; (f) "two-observable central value and covariance". The uses are also grouped in the new ME27 text. | — |
| chunk01 | Q28 | sec_method.tex ME35 | MOVED-OK | Cur sec_method.tex item (f): "the refinement classifier of (e), seeded at the estimator seed plus three". Item (e): "whose refinement classifier has 400 trees and 31 leaves". The table row (f) also gives both. | — |
| chunk01 | Q29 | sec_method.tex ME62 | SUPPORTED | The table's own column headers in base are "Configuration & Learner & Background treatment & Results". | — |
| chunk01 | Q33 | sec_method.tex ME76 | SUPPORTED | Base sec_method.tex: "Studies in this note labeled \emph{exact-split} use the exact-split central value (the quoted 2D central value until 2026-10-11) and have not been recomputed." | — |
| chunk01 | Q37 | sec_method.tex ME95 | RATER-WRONG | Wording only. "Additional" was relative to the miss regression, which the same sentence still names as the efficiency correction. "Rather than an idealized shortcut" is rhetoric; "exercises the same code path as the measurement" is kept. | — |
| chunk01 | Q40 | sec_method.tex ME114 | SUPPORTED | Base ME118, same paragraph: "The unbinned unfold has no response-matrix under/overflow to track; reporting bins are applied once to events that all lie inside the grids." | — |
| chunk02 | Q1 | sec_method.tex ME118 | MOVED-OK | Now prints in cur sec_method.tex ME114: "...by construction rather than by truncation: the unbinned unfolding has no response-matrix under- or overflow, and the reporting bins are applied once, to events that all lie inside the grids." | — |
| chunk02 | Q4 | sec_systematics.tex SY6 | REAL | The flagged items are fine. "Re-selected" still defined in cur §uq-higherdim ("Re-selected event loops re-run the selection with one lateral universe active at a time"). Base app_statmethods.tex supports the ranking ("per-bin median relative $\sigma_{i}/X^{\CV}_{i}$"), "PPFX flux band (hadron-production sampling)" and "MinosEfficiency (MINOS muon-match efficiency)". Two unsupported glosses are added, see the REAL list. | R1, R2 |
| chunk02 | Q6 | sec_systematics.tex SY19 | SUPPORTED | Same base paragraph: the flux mode "correlates ... with the rank-1 muon-energy-scale band in the rederived Bashyal joint block. The cross term is rank-2". So the joint block is the flux and muon-energy-scale cross block. | — |
| chunk02 | Q7 | sec_systematics.tex SY22 | MOVED-OK | "Paper-derived" is carried by the preceding cur sentence: "...block of Ref.~\cite{Bashyal:2021tqu}, as rederived here." | — |
| chunk02 | Q8 | sec_systematics.tex SY24 | MOVED-OK | The preceding cur sentence: "each fully re-unfolded with the LightGBM estimator at the central value's training seed (seed~42)". Cur sec_method.tex: "The quoted statistical covariance ... also uses seed~42". The independence of the background stream is carried by "three independent streams". | — |
| chunk02 | Q10 | sec_systematics.tex SY30 | RATER-WRONG | Intensifier "genuinely" removed. The ratio 0.407 and the offset statement are kept. | — |
| chunk02 | Q11 | sec_systematics.tex SY36 | RATER-WRONG | The subsection heading "ML/optimization uncertainty: training-seed variation" still ties $C_{\mathrm{ML}}$ to this block. Wording only. | — |
| chunk02 | Q12 | sec_systematics.tex SY38 | MOVED-OK | Same subsection, cur: "the training-seed block carries it only at its $1/20$ share, a median 0.763 of its diagonal". The block's definition (five training-seed settings) carries "measures LightGBM seed variation". | — |
| chunk02 | Q13 | sec_systematics.tex SY48 | REAL | The base note names EtaNCEL and NormNCRES only as band names. "Neutral-current elastic" and "neutral-current resonant normalization" appear nowhere in the base. "Barely change the unfolding inputs" glosses base "small-input responses" and is fine. | R3 |
| chunk02 | Q14 | sec_systematics.tex SY52 | REAL | The corrections still print in cur §uq-2d-scope: "show the following defects in its construction; the quoted budget corrects each". But "knob bands" became "interaction-model bands". Base app_statmethods.tex says the unified throw perturbs "every reweightable band and the flux multisim", so the rewrite narrows the population. | R4 |
| chunk02 | Q15 | sec_systematics.tex SY58 | SUPPORTED | Same base paragraph: the nominal covariance is "the block sum ... so that per-band covariances add", and "The block sum is an approximation". Endpoints are per band ("$\pm1\sigma$ pair"). | — |
| chunk02 | Q16 | sec_systematics.tex SY62 | MOVED-OK | Cut as a repetition (B03-24). Cur §uq-combine: "which assumes the blocks are independent and the unfolding responds linearly to simultaneous perturbations, so that per-band covariances add". $C_Z$ is defined here and named in base app_release.tex ("$C_{Z}$ ... The five-axis covariance of the configuration-(a) central value"). | — |
| chunk02 | Q17 | sec_systematics.tex SY65 | RATER-WRONG | "Data taken in different run periods" is the same population as "subsets of the data taken in different run periods". "2D" names the earlier budget as the section does throughout ("the earlier 2D budget"). | — |
| chunk02 | Q20 | sec_systematics.tex SY75 | MOVED-OK | Cur §uq-pl: "These data cannot establish which period, if any, is correct." (B03-32) | — |
| chunk02 | Q22 | sec_systematics.tex SY92 | SUPPORTED | $C_{\mathrm{model}}$ is the 2D per-cell relative change $s_k$ (base same paragraph). Base sec_method.tex: "205 of 224 are reported". | — |
| chunk02 | Q23 | sec_systematics.tex SY97 | REAL | Base sec_systematics.tex says only "a pooled, noise-gated or unreported cell". "Set to one" by the gate is stated in base only for the five-dimensional tune ratios (sec_fived16.tex: "pooled over a coarser cell or set to one where the tune's sample fails the ratio's statistical gate"), not for this 2D construction. Probably true, but not stated. | R5 |
| chunk02 | Q25 | sec_systematics.tex SY104 | MOVED-OK | Cur §uq-universes flux paragraph: "Target-nucleon normalization contributes a fully-correlated rank-1 band of \SI{1.4}{\percent}." The internal label "(the miss rows)" was dropped. | — |
| chunk02 | Q26 | sec_systematics.tex SY108 | RATER-WRONG | "Not tight" is carried by the kept clause "They exclude only a median effect above twice that $\sigma$, so an effect below the training noise is not excluded." | — |
| chunk02 | Q27 | sec_systematics.tex SY118 | MOVED-OK | Each block limitation prints at its section, and the pointer sentence keeps the refs. The heading still reads "Seed-related terms reported, not added"; cur §uq-ml has "The interaction itself and the universe\,$\times$\,retraining term are reported and not added" and "carries it only at its $1/20$ share". This passage also carries the unflagged "single-pion" gloss. | R2 (site b) |
| chunk02 | Q28 | sec_systematics.tex SY126 | SUPPORTED | Base SY48 calls EtaNCEL a "small-input response", which is consistent with "leaves the event weights essentially unchanged". The heading change is wording. | — |
| chunk02 | Q29 | sec_systematics.tex SY133 | REAL | Dropping "real" is wording. "Single-pion" is a gloss that is not in base: base has "the Rvn1pi and Rvp1pi bands encode the same shift under the configured nonresonant-pion tune". | R2 (site c) |
| chunk02 | Q31 | sec_systematics.tex SY143 | SUPPORTED | $C_Z$ is defined in cur SY63. The band glosses follow base app_statmethods.tex: "the five kinematic bands (the two beam-angle components, the muon resolution and the two muon energy scales)". | — |
| chunk02 | Q32 | sec_systematics.tex SY145 | RATER-WRONG | The preceding cur sentence: "moves that block's square-root trace by \SI{\latTraceMove}{\percent}". "This aggregate change" refers to it. | — |
| chunk02 | Q33 | sec_systematics.tex SY151 | SUPPORTED | $C_Z$ is defined in cur SY63 and named in base app_release.tex. | — |
| chunk02 | Q35 | sec_systematics.tex SY158 | MOVED-OK | "Later" is kept as "A 5D covariance construction that preceded it". $C_Z$ is defined in cur SY63. | — |
| chunk02 | Q36 | sec_validation.tex VA6 | MOVED-OK | Cur sec_validation.tex: "Reweighting to another generator's shape is a valid known-truth test of the unfolding; it is not a test of the detector model." Also "None of these tests uses pseudo-data whose detector response differs from the unfolding response." "Recovered" is carried by "within the \SI{1.5}{\percent} threshold". "Completeness-divided" is in base: "The band's replicas divide by a bootstrapped completeness". | — |
| chunk02 | Q38 | sec_validation.tex VA16 | RATER-WRONG | Evaluative "naive" removed. The statistical-only diagonal and its limitation are kept. | — |
| chunk02 | Q39 | sec_validation.tex VA25 | SUPPORTED | Same base paragraph: "Validated total uncertainties for all 205 bins ... cannot be obtained from the current inputs. They would require ..." | — |
| chunk03 | Q1 | sec_validation.tex VA32 | RATER-WRONG | Heading subtitle only. The body and the table caption "Closure tests by what they change" are unchanged. | — |
| chunk03 | Q2 | sec_validation.tex VA36 | MOVED-OK | The principle is carried by the next two cur sentences: the ordinary closure is "an identity check that a constant estimator would also pass", and the table "lists, for each test, what it changes ... and what its result can detect". | — |
| chunk03 | Q4 | sec_validation.tex VA42 | SUPPORTED | Base items under the same paragraph: "\emph{Deformation.}", "\emph{Metric.}", "\emph{Iterations.}" | — |
| chunk03 | Q7 | sec_validation.tex VA52 | SUPPORTED | Base VA78: "The band's replicas divide by a bootstrapped completeness". Base VA84-86: "The band was then rebuilt without this term. The quoted statistical block is a third, different ensemble, 300 replicas at the central value's training seed"; "the rebuilt (since superseded) band". | — |
| chunk03 | Q8 | sec_validation.tex VA56 | SUPPORTED | Base sec_systematics.tex: "300 per-event Poisson(1) weight replicas". "Production" bootstrap is the scored band's own bootstrap; B04-16 has it as "the statistical band's per-event Poisson(1) bootstrap". | — |
| chunk03 | Q9 | sec_validation.tex VA63 | SUPPORTED | The term is defined in cur VA52. "The band fails" is carried by "the completeness-divided band undercovers in its tails" and "this is a failure by undercoverage". The gate phrase "lies entirely below its window (Gaussian 0.954)" is intact. "Reimplementation of the scoring" matches the outputs listed. | — |
| chunk03 | Q11 | sec_validation.tex VA74 | RATER-WRONG | "Per-bin $C_2$ below 0.85" is itself the undercoverage statement. It directly follows "too narrow in $\covTwoDNnarrow$". | — |
| chunk03 | Q12 | sec_validation.tex VA78 | MOVED-OK | The division prints in cur VA52 ("whose replicas divide by a bootstrapped completeness"). The post hoc disclosure is kept ("added after the pilot"). "By amendment" goes to the records home R:app_provenance.tex "(amendments 1--2)" (B04-20). | — |
| chunk03 | Q14 | sec_validation.tex VA85 | MOVED-OK | Cur VA52: "The quoted statistical block (\S\ref{sec:uq-boot}) is a separate ensemble of 300 replicas at the central value's training seed". "Since superseded" is in the VA52 definition of the undivided band. The gate phrase is intact. | — |
| chunk03 | Q19 | sec_validation.tex VA117 | RATER-WRONG | The control's DETAIL is wrong; the real run said SAME. "Diagnose standardized pulls and Gaussianity only" keeps the limiting "only". Certifying a band is a coverage claim, which "are not a coverage test" denies. | — |
| chunk03 | Q21 | sec_results.tex RE20 | MOVED-OK | Cur fig:ptslices caption: "so the two differ only as data versus MC prior; no published measurement is used". Cur fig:pzslices caption: "with statistical errors only and no published measurement". The cite key `MINERvA:2021owq` has eprint 2106.16210 (technote.bib). | — |
| chunk03 | Q22 | sec_results.tex RE26 | MOVED-OK | Each figure's own caption describes it. Cur fig:pull: "Per-bin standardized difference ..."; cur fig:model: "Projections of this measurement (dashed) and the published data". | — |
| chunk03 | Q26 | sec_results.tex RE39 | MOVED-OK | Cur sec_results.tex text: "Our flux band carries the per-universe $\nu$--$e$ and inverse-muon-decay constraint weights" (B05-12). "July" is kept where the sweep is defined, in cur sec_systematics.tex: "use the July universe sweep". The new heading "Eigenmode analysis" is supported by the base section ("The eigenmode decomposition (Fig.~\ref{fig:tension})"). | — |
| chunk03 | Q28 | sec_results.tex RE48 | SUPPORTED | The preceding base and cur sentence: "the choice of GBDT estimator spreads the distance over about one unit, a methodological band". "Negligible" is kept ("by a negligible $+0.01$"). | — |
| chunk03 | Q29 | sec_results.tex RE59 | RATER-WRONG | "Requires a new unfolding" and "as in the 3D extension" carry "not a projection" and "unfolded again". The caption opens "Bin-by-bin ratios to MINERvA Tune~v1", so the denominator is stated; "Both maps show the same tune deficit, with ratios above unity over most of the plane" carries "not flat". | — |
| chunk03 | Q30 | sec_3d.tex TD7 | SUPPORTED | Base sec_method.tex: "With at most five high-level features per event"; "few high-level features". | — |
| chunk03 | Q31 | sec_3d.tex TD11 | SUPPORTED | Same as TD7: base sec_method.tex "high-level features". | — |
| chunk03 | Q32 | sec_3d.tex TD19 | REAL | The explicit non-claim "We therefore do not claim that our definition matches ``the published definition.''" was cut as "commentary" (B06-6). It has no N: home; the probe is `X:`. It is a scope limitation on the definition. | R6 |
| chunk03 | Q33 | sec_3d.tex TD29 | MOVED-OK | Cur Table tab:3d-configs caption: "(e) and (f) use refined negative-weight subtraction with a 400-tree, 31-leaf refinement; (a) uses purity-based subtraction"; rows give (e) for "3D and 4D central values, unless stated otherwise" and (a) for the figures. | — |
| chunk03 | Q34 | sec_3d.tex TD32 | SUPPORTED | The table restates base TD29 and TD37. "3D closure" for (a): base sec_method.tex "(a) ... the 3D and 4D injected-bump closures". "Classifier-family cross-check" for (a): base sec_3d.tex "GBDT (configuration~(a)) and Keras-MLP projections". | — |
| chunk03 | Q35 | sec_3d.tex TD37 | MOVED-OK | The details are in cur Table tab:3d-configs: "(e), deterministic LightGBM (the learner of (c))", "(f), LightGBM at seed~42 (the learner of (a))", and the caption's 400-tree, 31-leaf refinement. The label "cross-configuration comparison" no longer prints in sec_3d. It still prints in the executive summary, and the cur sentence names (e) and (f) and says they "differ in learner". | — |
| chunk03 | Q39 | sec_3d.tex TD56 | REAL | Base: "neither manufactures nor destroys the feature". Cur: "recovers the feature". The cur text two sentences earlier says the test "has no pass or fail verdict", with residual ratio 0.102. "Recovers" reads as a verdict on the recovered amount, which the base sentence does not claim. Low severity: gap B06-s-09 asked for literal "recovery" wording. | R7 |
| chunk03 | Q40 | sec_3d.tex TD66 | RATER-WRONG | The narrowing to "the two tested classifier families" was asked for by gap B06-s-10 ("describing agreement between the two tested classifier families"). It states exactly the base's evidence. Dropping "scalar" is redundant in the scalar section. | — |

## REAL rows: base text, new text, fix

Each old_str below occurs exactly once in the current `$WT/docs/analysis-note/` file. Counts checked with Python
`str.count`.

**R1. chunk02 Q4 (SY6), "interaction-model" narrows the 44-band sweep.** The 44 bands include the flux band. Base
Fig. uqbands groups them "by flux, interaction models, normalization, hadronic response, muon reconstruction".
- base: "Detector and model systematics use the July universe sweep"
- new: "Detector and interaction-model systematics use the July universe sweep"
- fix, sec_systematics.tex:
  - old_str: `Detector and interaction-model systematics use the July universe sweep`
  - new_str: `Detector and model systematics use the July universe sweep`

**R2. chunk02 Q4, Q27, Q29, "single-pion" gloss on Rvn1pi and Rvp1pi.** The base never says "single-pion". It says "the
Rvn1pi and Rvp1pi bands encode the same shift under the configured nonresonant-pion tune" and "the duplicated pion
band".
- (a) SY6
  - new: "The band sum omits the nonresonant single-pion band Rvp1pi"
  - old_str: `The band sum omits the nonresonant single-pion band Rvp1pi`
  - new_str: `The band sum omits the nonresonant-pion band Rvp1pi`
- (b) SY118
  - base: "the duplicated pion band (below)"
  - old_str: `for the duplicated single-pion band, below`
  - new_str: `for the duplicated pion band, below`
- (c) SY133
  - base: "Second, the Rvn1pi and Rvp1pi bands encode"
  - old_str: `Second, the two nonresonant single-pion bands, Rvn1pi and Rvp1pi, encode`
  - new_str: `Second, the two bands Rvn1pi and Rvp1pi encode`

**R3. chunk02 Q13 (SY48), band-name glosses written from general knowledge.**
- base: "The two examined small-input responses, EtaNCEL and NormNCRES, are consistent with ..."
- new: "... the neutral-current elastic band EtaNCEL and the neutral-current resonant normalization band NormNCRES, the
  responses are consistent ..."
- fix, sec_systematics.tex:
  - old_str: `the neutral-current elastic band EtaNCEL and the neutral-current resonant normalization band NormNCRES`
  - new_str: `EtaNCEL and NormNCRES`

**R4. chunk02 Q14 (SY55), "interaction-model bands" for "knob bands".** Base app_statmethods.tex states the population
as "simultaneously perturbing every reweightable band and the flux multisim per event".
- base: "by jointly re-unfolding all reweightable knob bands and the flux multisim, perturbed simultaneously per event"
- new: "by perturbing all reweightable interaction-model bands and the flux universes simultaneously in each event and
  re-unfolding jointly"
- fix, sec_systematics.tex:
  - old_str: `by perturbing all reweightable interaction-model bands and the flux universes`
  - new_str: `by perturbing all reweightable bands and the flux universes`
- Same gloss outside my range: sec_3d.tex:203 "simultaneous variation of all reweightable interaction-model bands and
  the flux universes". The base has no "interaction-model" in sec_3d.tex.

**R5. chunk02 Q23 (SY97), the gate mechanism added for the 2D C_model.**
- base: "where a pooled, noise-gated or unreported cell meets another cell"
- new: "Where a pooled cell, a cell set to one by the statistical-noise gate, or an unreported cell meets another cell"
- fix, sec_systematics.tex:
  - old_str: `a cell set to one by the statistical-noise gate`
  - new_str: `a noise-gated cell`
- What would make it SUPPORTED instead: a base-note sentence saying the 2D C_model's gate sets the ratio to one. The
  only such sentence is in sec_fived16.tex, for the five-dimensional tune ratios.

**R6. chunk03 Q32 (TD19), the non-claim about the published definition was dropped.**
- base: "... instead uses charged-pion total energy. We therefore do not claim that our definition matches ``the
  published definition.''"
- new: (the sentence is gone; the ledger B06-6 probes `X:sec_3d.tex::We therefore do not claim`)
- fix, sec_3d.tex:
  - old_str: `and charged-pion total energy in the \texttt{minerva-ml} implementation (App.~\ref{sec:pet}).`
  - new_str: `and charged-pion total energy in the \texttt{minerva-ml} implementation (App.~\ref{sec:pet}). We therefore do not claim that our definition matches ``the published definition.''`

**R7. chunk03 Q39 (TD56), "recovers" is stronger than the base claim.** Low severity.
- base: "On this injection the configuration-(a) estimator neither manufactures nor destroys the feature. That result does
  not extend to configuration~(e)"
- new: "For this injection the configuration-(a) estimator recovers the feature. The recovery is shown for
  configuration~(a) only"
- fix, sec_3d.tex. This is a literal restatement of the base claim that keeps B06-s-09's register:
  - old_str: `For this injection the configuration-(a) estimator recovers the feature. The recovery is shown for configuration~(a) only`
  - new_str: `For this injection the configuration-(a) estimator neither removes the injected feature nor creates a spurious one. That result is shown for configuration~(a) only`

## Counts

MOVED-OK 23, SUPPORTED 25, RATER-WRONG 13, REAL 7 (chunk02 Q4, Q13, Q14, Q23, Q29; chunk03 Q32, Q39), UNSURE 0. Total 68.
