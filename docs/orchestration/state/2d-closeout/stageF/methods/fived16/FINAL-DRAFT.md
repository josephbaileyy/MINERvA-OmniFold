# The final draft (d): a decision packet for Joseph (2026-10-28)

**From** the paper rewrite lane, through the director. **Under:** `DECISION-20261027-joseph-5d-integration-then-second-scope-review.md` item 2 (the printed wording is yours and comes to you before #413 merges); the director's work order of 2026-10-28.

**How to read it.** Each item is numbered. It quotes the current printed text exactly, generated from the sources with every value resolved (`final-draft/make_final_draft.py`, which stops if a quoted passage no longer prints). Any proposal stands beside it, with its source and one line of reason. Every protected text of yours is shown unedited. Nothing is submitted, deposited or tagged, and #413 stays a draft PR until you approve.

**The PDFs** (built from #413 at the commit holding this file, `build_all.sh` rc 0):
- the paper: `final-draft/main_paper.pdf`;
- the note: `final-draft/main_note.pdf`;
- the paper redline against the pre-integration base `8b0f83fd`: `final-draft/redline-paper.pdf` (latexdiff, by
  `final-draft/make_redline.sh`). Deleted text is struck through in red, and inserted text is underlined in blue. Tables
  print whole, without markup inside. A "??" appears only inside deleted text, where it refers to a label r19 removed
  (Sec. VI's sections, its tables and Fig. 4, and Table I).

## 1. What changed since you last read it

1. **The 5D integration:** the sixteen-cell five-observable cross section (configuration (e)), with its reported covariance C_total + C_resp, fake-data tests and generator comparison, in the paper and in a new note chapter (§10).
2. **The move:** the non-final configurations, the calibrated hybrid-null tests and their detail now print in the note; the paper points to them.
3. **r19's structure:** the paper is a measurement paper in six sections (Introduction; Data, simulation and observables; Cross-section extraction; Uncertainties and validation; The sixteen-cell cross section; Discussion and conclusions); Table I is folded into the text.
4. **Step (c):** the GENIE v3 held-out bias test (F1) in Sec. I, both abstracts, IV H and the note; the flux-correlation bootstrap band (3D) beside the kept α = 0.1 sentences.
5. **`tab:result16`:** the sixteen-cell result table (Table III), one marginal uncertainty column, with your advice applied (DECISION-20261028, result table).

## 2. The title

**Current (T0):**
> Performance and limitations of multidimensional OmniFold unfolding with MINERvA open data

T0 is the methods framing ("Performance and limitations"); the paper is now led by its measurement. **The options** (`WORDING-PACKET.md`; PRD read round 3 chose T1 in all four runs):
- **T1:** "Simultaneous measurement of the ν_μ charged-current inclusive cross section on hydrocarbon in five observables from MINERvA open data"
- **T2:** "Charged-current inclusive ν_μ cross section on hydrocarbon in muon kinematics, available energy, three-momentum transfer and hadronic invariant mass from MINERvA open data"
- **T3:** "Five-dimensional ν_μ charged-current inclusive cross section measured with unbinned unfolding of MINERvA open data"

**Reason in one line:** the abstract, Sec. I and the result now lead with the cross section, which T0 does not name.

## 3. The two abstracts (drafts; the final wording is yours)

**3.0 The paper abstract as it prints (228 words):**
> We report a simultaneous measurement of the ν_μ charged-current inclusive cross section in five observables, the muon transverse and longitudinal momenta, available hadronic energy, three-momentum transfer and hadronic invariant mass, unfolded without binning with OmniFold from MINERvA medium-energy open data and reported in sixteen cells with a covariance whose median per-cell uncertainty is 7.29%. Three external generator predictions compared on all sixteen cells give χ² of 109–272 for 16 degrees of freedom, and GiBUU, on 8 cells, 58. The coverage of the intervals has not been validated; a bias test at two held-out GENIE v3 truths finds the estimator's bias below the reported uncertainty in every cell but does not test interval widths. In a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic q3 tilt. The sixteen-cell χ² values fall by 24–48% when only the flux correlations are weakened by 10%. The same unfolding reproduces the integral of the published muon-kinematic cross section within about 1%, with a correlated shape difference. Pseudo-experiments measure a background-subtraction bias that negative-weight subtraction largely removes, a partial recovery of generator-sized truth changes, and statistical undercoverage of a deterministic purity-subtracted variant at the tested truths. As an illustration, simulation-calibrated tests of hybrid null hypotheses for five generator predictions all reject at the 5% familywise level, with no evidence of gain over matched coarse projections.
<!-- absence-ok: quotes printed limitation wording for Joseph; not a new absence claim -->

**The note abstract as it prints (373 words):**
> This note documents an unbinned, simultaneous unfolding of MINERvA medium-energy ν_μ charged-current inclusive open data with OmniFold, and its validation. Its principal result is a cross section in five observables, muon transverse and longitudinal momentum, available energy (E_avail), three-momentum transfer (q3) and hadronic invariant mass (W), in sixteen cells, with a covariance of statistical, flux, interaction, detector, lateral, normalization, generator-shape and calorimetric-response terms; its median per-cell uncertainty is 7.29%. Three external generator predictions compared on all sixteen cells give χ² between 109 and 272 for 16 degrees of freedom, and GiBUU, on its 8 cells, 58. The coverage of the result's intervals has not been validated; a bias test at two held-out GENIE v3 truths finds the estimator's bias below the reported uncertainty in every cell but does not test interval widths. In a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic q3 tilt. The sixteen-cell χ² values fall by 24–48% when only the flux correlations are weakened by 10%. The note also gives the reproduction of the published double-differential cross section in muon momentum, whose integral agrees within about one percent, with a correlated shape difference and a covariance that has not been independently validated; three- and four-observable central values; and an earlier purity-subtracted five-observable central value on a finer grid, whose covariance does not meet its specification's acceptance criteria and whose quoted uncertainties omit that estimator's background bias of up to 4% at high W and its regularization bias. The validation studies show that negative-weight background subtraction removes most of the purity method's bias, that generator-sized truth changes are recovered only in part, a residual interpreted as regularization bias, that statistical intervals of a deterministic purity-subtracted variant miscover at the tested truths, and that no tested reporting definition meets a predeclared 10% precision criterion. Joint tests calibrated in simulation reject hybrid null hypotheses for five generator predictions at a 5% family-wise error rate; they are not physical exclusions, show no evidence of discrimination beyond matched coarse projections, omit an uncertainty on the calorimetric recoil response and assume an unshown convergence of the fine grid on which the null hypotheses are defined, and NuWro's total-test rejection is not robust to a hydrocarbon-target correction.
<!-- absence-ok: quotes printed limitation wording for Joseph; not a new absence claim -->

**3.1 The joint-test sentence is stale after the move.** The paper abstract still says:
> As an illustration, simulation-calibrated tests of hybrid null hypotheses for five generator predictions all reject at the 5% familywise level, with no evidence of gain over matched coarse projections.
The joint tests now print in the note only; the paper body reaches them through one pointer, and its body sentence says "additional discrimination" where this sentence says "gain" (agy-b4 Q2). **Options:** (a) keep it, as an illustration of the note; (b) drop it from the paper abstract, where the note abstract keeps its form ("Joint tests calibrated in simulation reject hybrid null hypotheses for five generator predictions at a 5% family-wise er…"); (c) your words. *Reason:* the abstract reports a result the paper no longer prints.

**3.2 The 1A addition (step (c)).** Both abstracts' coverage sentence now reads:
> The coverage of the intervals has not been validated; a bias test at two held-out GENIE v3 truths finds the estimator's bias below the reported uncertainty in every cell but does not test interval widths.
<!-- absence-ok: quotes printed limitation wording for Joseph; not a new absence claim -->
> The coverage of the result's intervals has not been validated; a bias test at two held-out GENIE v3 truths finds the estimator's bias below the reported uncertainty in every cell but does not test interval widths.
<!-- absence-ok: quotes printed limitation wording for Joseph; not a new absence claim -->
Read as printed by PRD read r6 (sol2 ×2, gemini) and agy with a control; no rater form passed both, so the drafts stand (`prd-read/REPORT.md`, "Round 6"). *Reason:* the decision says the paper names 1A as a bias test, not a coverage test.

**3.3 The note abstract's length.** 373 words (348 before (c)). sol2 called it too long in 2 of 4 runs of round 3; gemini, acceptable in 2 of 2. No rater's shorter form passed the truth column. **A shorter version is drafted only if you ask,** because it would be new wording.

**3.4 Two wordings of one limitation.** Sec. I (PRD read r5's form) says "Interval coverage has not been validated."; the abstracts say "The coverage of the intervals has not been validated" (paper) and "The coverage of the result's intervals has not been validated" (note). **Options:** align them, or keep each as read. *Reason:* each form was read and accepted where it prints; the choice is register only.
<!-- absence-ok: quotes printed limitation wording for Joseph; not a new absence claim -->

## 4. The flux band (3D): replace the α = 0.1 sentence, or keep both

**The paper (Sec. V B), as it prints:**
> Weakening only the flux correlations by 10% lowers the χ² of the 16-cell predictions by 24–48%. The same change to the detector or lateral correlations lowers it by at most 18%. With the correlations of the interaction, flux, detector and lateral groups removed, every 16-cell prediction keeps χ²≥45 for 16 degrees of freedom. The flux correlations are estimated from 100 hadron-production (PPFX) flux universes [16], weighted by the neutrino–electron and inverse-muon-decay constraint. Bootstrapping these universes, with the flux variances kept, gives 16th–84th percentile bands for each 16-cell χ², with edges within 6.2% of the reported value and a median at most 1.0% above it. These bands describe the scatter of the χ² from estimating the correlations with these universes, not its sensitivity to incorrect correlations, which the weakening probes; they are not intervals for the χ² under the true correlations.

**The note (§10.4), as it prints:**
> Weakening only the flux correlations by 10% lowers the χ² of the 16-cell predictions by 24–48%. The same change to the detector or lateral correlations lowers it by at most 18%. With the correlations of the interaction, flux, detector and lateral groups removed, every 16-cell prediction keeps χ²≥45 for 16 degrees of freedom. Table 18 gives each group's sensitivity, GiBUU's eight-cell values included. These are descriptive sensitivities of the reported χ², not alternative results: one group's correlations are shrunk toward the diagonal by a fraction α of the way, with its variances kept. The flux correlations are themselves estimated from the 100 PPFX flux universes, weighted by the neutrino–electron and inverse-muon-decay constraint (§10.2). Rebuilding the flux block from 2000 bootstrap replicates of those universes, with its variances kept, gives 16–84% percentile bands of the total χ²: GENIE 2.12.10 CV 106–112 around 109, GENIE 2.12.10 + Valencia MEC 262–283 around 272, NuWro 21.09 185–191 around 188, MINERvA Tune v1 315–350 around 330, and GiBUU 2019, on its 8 cells, 57–59 around 58. In each, the bootstrap median lies above the reported value, by 0.25, 1.22, 0.75, 3.12 and 0.16 in the same order. These bands measure the estimation scatter of the reported χ² given these universes, not how much it would change if the flux correlations were wrong, which the weakening above probes; they are not intervals for the χ² under the true correlations.

**The abstracts' and Sec. I's flux sentences are unchanged by (c).** The paper abstract:
> The sixteen-cell χ² values fall by 24–48% when only the flux correlations are weakened by 10%.
Sec. I:
> The generator χ² depends on the flux correlations: weakening only them by 10% lowers the χ² of the sixteen-cell predictions by 24–48% (Sec. V B).

**Options:** (a) keep both, as now; (b) replace the α sentences with the band, as DECISION-20261027 (limitation plan) item 3 first said ("replaces"). *Reason for (a):* they answer different questions. The weakening probes sensitivity to incorrect correlations; the band is the estimation scatter of the χ² given these universes, and not an interval for the χ² under the true correlations (FD-FLUX-BOOT-BINDING ruling 2).

## 5. F1, the GENIE v3 held-out bias test

**5.1 The Sec. I sentence, as it prints:**
> Interval coverage has not been validated. At two held-out GENIE v3 truths, a bias test finds the estimator's bias below the reported uncertainty in every cell, but does not test interval widths.
<!-- absence-ok: quotes printed limitation wording for Joseph; not a new absence claim -->

**Beside it, what it rests on.** At G18_10a_02_11b's cell R11, the −8.5 % bias stays below σ mainly through C_model's GiBUU vertex. |b|/σ is 0.62 under the full reported covariance, 0.93 without the GiBUU vertex and 1.07 under C_e + C_resp alone (the independent review of `589f0780`; `c1a/REPORT.md`). **"The reported uncertainty" in that sentence includes C_model,** which the paper calls "not a calibrated bound". The sentence is true as written; whether to say so in the text is yours.

**5.2 IV H's paragraph, as it prints (164 words):**
> Two GENIE v3 tunes, G18_10a_02_11b and AR23_20i_00_000, were generated for this test and held out of the analysis. Each reweights the simulated truth by the tune's shape ratio to GENIE CV, built as for the C_model components; the detector response is the simulation's and is not probed. For each tune, 20 Poisson pseudo-experiments and a noise-free closure are compared with the truth using the full reported covariance. Both tunes satisfy both bias criteria: the pseudo-experiment means give χ²=11.84 (p=0.76) and 16.86 (p=0.39), respectively, with |z|≤0.65 in every cell of the means and closures. Both are GENIE tunes and use the same quasielastic cross-section model; G18_10a_02_11b also uses a Valencia-family MEC model, as does the GENIE + MEC component of C_model. They provide partial evidence and are not independent tests. Omitting that component gives χ²=15.15 (p=0.51) and 24.60 (p=0.077), respectively, as a descriptive comparison. These tests assess bias, not coverage: only event counts fluctuate, without variation of systematic parameters, so interval widths cannot be tested.

**Beside it, the alternative** (PRD read r6, sol2 r2's form, 154 words; true in the truth column, and agy reads it SAME; it does not replace the paragraph):
> Two GENIE v3 tunes, G18_10a_02_11b and AR23_20i_00_000, were generated for this test and held out of the analysis. Each reweights the simulated truth using its shape ratio to GENIE CV, constructed as for the C_model components. The simulated detector response is not probed. For each tune, 20 Poisson pseudo-experiments and a noise-free closure are compared with the truth using the full reported covariance. Both tunes satisfy the bias criteria: the pseudo-experiment means give χ²=11.84 (p=0.76) and 16.86 (p=0.39), respectively, with |z|≤0.65 in every cell of the means and closures. The tunes share a quasielastic cross-section model; G18_10a_02_11b and the GENIE + MEC component of C_model also use Valencia-family MEC models. These tests provide partial evidence and are not independent. Omitting that C_model component gives χ²=15.15 (p=0.51) and 24.60 (p=0.077), respectively, as a descriptive comparison. The tests assess bias, not coverage: only event counts fluctuate, with systematic parameters fixed, so interval widths cannot be tested.

*Reason to consider it:* shorter, same facts; it leaves the "GENIE tunes" ground of "partial evidence" to the first sentence.

## 6. Data and release (all protected text yours, shown unedited)

**6.1 Q8, supplemental data.** Whether the article and the release carry the sixteen-cell vector, C_total + C_resp and the cell boxes, and in what format, is open and yours.

**6.2 The deposit candidate** (`measurement-paper/5d-community-20261024/fd/deposit-candidate/`): prepared, not deposited (DECISION-20261028 item 2). It holds the cell definitions, f, the reported covariance and the correlation matrix, verified against the data product (`b79556f0`).
- **DRAFT proposal, the paper's citation of it** (no identifier exists, so none is cited): in `tab:result16`'s caption, "The cell definitions, measured vector, reported covariance and correlation matrix are given in machine-readable form in Ref. [deposit]", with Ref. [deposit] a bibliography entry whose identifier is a `\pubhold`.
- **DRAFT proposal, Data Availability:** a sentence after the release-package sentence, "The sixteen-cell result's cell definitions, measured vector, reported covariance and correlation matrix are prepared for deposit in machine-readable form," followed by your `\pubhold` for its identifier.
- **`predictions-reference.json`:** the five predictions' g and V_g, labelled "reference predictions used for the paper's χ²; not part of the measurement". **Options:** in the deposit, or not. *Reason:* with it, the paper's χ² can be reproduced; without it, the deposit is the measurement alone.

**6.3 Data Availability (protected), as it prints:**
> The input data and simulation are the MINERvA open-data AnaTuples, released under CC0 [12]. This analysis used an earlier production of that release; its 2,374 input files are identified by SHA256 checksum in the records cited in Ref. [14], App. G. A candidate release package of about 16 MB, not yet deposited, requires only numpy, scipy, and matplotlib. It recomputes every p value, decision, robustness result, and power figure of the joint tests and the numbers quoted in Sec. V C, and it regenerates the analysis note's figures of the joint-test null distributions and the (E_avail,W) map. The other quoted numbers, except the multiplier scan, and the event-level processing require the archived analysis products, the open-data AnaTuples, and the generator samples produced for this analysis; Ref. [14], App. G states what each part of the release does and does not reproduce. [HOLD: deposit identifier and access route, after the separately authorized release decision.]
- **One stale pointer, one clause still true.** "of the joint tests" is still true of the package: it recomputes the
  joint tests' p values and decisions, which now print in the note rather than the article. The stale part is "the
  numbers quoted in Sec. V C": that section now quotes none. **Proposal** (`WORDING-PACKET.md`, after
  the move), which keeps "of the joint tests", replaces the Sec. V C clause with the map's numbers
  as quoted in the note, and so refers the figure clause to "that map": "It recomputes every p value, decision, robustness result, and power figure of the joint tests and the five-observable (E_avail, W) map's numbers quoted in the analysis note, and it regenerates the note's figures of the joint-test null distributions and of that map."
- **The release-package sentence**, quoted by 2 of 3 P1 runs after r19:
> A candidate release package of about 16 MB, not yet deposited, requires only numpy, scipy, and matplotlib. It recomputes every p value, decision, robustness result, and power figure of the joint tests and the numbers quoted in Sec. V C, and it regenerates the analysis note's figures of the joint-test null distributions and the (E_avail,W) map.
  The raters' readings (their own rewrites: not fact-checked, and both carry the stale "Sec. V C"):
  - sol2 run 2: "A release package of approximately 16 MB has been prepared but has not yet been deposited. It requires NumPy, SciPy, and Matplotlib and reproduces the joint tests’ p values, decisions, robustness results, and power estimates; the numerical results in Sec. V C; and the companion note’s figures showing the joint-test null distributions and the (Eavail , W ) map."
  - sol2 run 3: "A proposed release package (approximately 16 MB), requiring NumPy, SciPy, and Matplotlib, reproduces the joint-test p values, decisions, robustness results, and power estimates; the numerical results in Sec. V C; and the analysis note’s figures showing the joint-test null distributions and the (Eavail , W ) map. The package has not yet been deposited."

  Run 2 gives "not yet deposited" a clause of its own; run 3 moves it to a last sentence of its own.

**6.4 `app_release.tex:9`'s figure list (protected):**
> It also regenerates, from packaged arrays, figures that the article cites from this note: the (E_avail,W) excess map (Fig. 24), the null distributions of the joint tests (Fig. 31), and the one-dimensional generator projections.
The article now reaches the joint tests' null distributions only through one pointer (r19, K8). **Options:** keep; or say "figures that the article cites from this note, directly or through its pointers" (DRAFT). `app_release.tex:29`'s "the arrays behind the article's figures" is still right: Figs. 1–3 are the same three figures.

**6.5 R1–R4, the release scopings, as proposals** (round 2 accepted each in all four runs; `prd-read/r2/inputs/proposals.tsv`). *Reason:* each names which central value the release's covariance belongs to, now that the note reports two results.

- **R1.** Now: "or the quoted closure, bias and covariance-status measurements." → proposed: "or the quoted closure, bias and covariance-status measurements of the configuration-(a) central value."
- **R2.** Now: "Covariances: the five-axis covariance used in this note and its (E_avail,W) projection," → proposed: "Covariances: the five-axis covariance of the configuration-(a) central value and its (E_avail,W) projection,"
- **R3.** Now: "The four measurements that travel with the five-axis covariance used in this note" → proposed: "The four measurements that travel with the five-axis covariance of the configuration-(a) central value"
- **R4.** Now: "The five-axis covariance used in this note is the file z-cv.npz," → proposed: "The five-axis covariance of the configuration-(a) central value is the file z-cv.npz,"

## 7. Wording pairs and questions

**7.1 O3, side by side.** The paper (base wording, kept):
> We interpret the residual as regularization bias, because it persists over the tested iteration numbers and classifier capacities.
The note:
> No single cause is established, and no estimator change within the scope of the study meets the recovery requirement, set before the test, for the GiBUU-to-GENIE departure.
*Reason:* the paper interprets; the note establishes no single cause. Any softening is yours.

**7.2 Q4, the rounding instability.** The paper says:
> The joint-test estimator is unstable at the level of rounding. Rounding-level changes of its inputs move its results by up to 2.6 statistical standard deviations, and those of its lower-capacity development variant by up to 2.5, so it fails a data-stability requirement of at most 0.3 (median) and 1.0 (maximum) statistical standard deviations. This spread lies inside the data-bootstrap statistical uncertainty, but it limits how exactly the central values can be reproduced.
Whether the final uncertainty accounts for this instability is open; no proposal is made, and r19 prints nothing new on it.

## 8. Reading notes, not edits

**8.1 gemini's five** (r20's pairwise; they concern r20's wording, which was not adopted and is reverted, so they are style points to judge by reading):

- "Ten, 15 or 20" mixes spelled-out words and numerals.
- The serial comma was dropped.
- "so it keeps five" reads as colloquial.
- "far upward" reads as an intensifier.
- The Limitations lead nests a parenthetical inside a semicolon.

**8.2 P02's**, the Sec. I sentence as it prints:
> The validation studies assess the result through the two-dimensional reproduction, background-subtraction tests, recovery of generator-sized truth changes, a coverage test and a fake-data study of estimator bias. They examine whether the unfolding gives reliable multidimensional cross sections when the simulation mismodels the truth by generator-sized amounts.
agy, against the pre-round-3 text: "AFTER drops the fact and limitation that the studies "show how far the result can be trusted", replacing it with the broader and purely procedural phrasing "assess the result", and alters "the background subtraction" to "background-subtraction tests"." PRD reads r4 and r5 accepted the change 3 of 3 each, so nothing is edited.

## 9. The register result, as measured

- **r19 (the measurement paper's order) was adopted:** the blind pairwise preferred it 4 of 4, with no order flip (`r19/REPORT.md`).
- **r20 was not adopted:** 2 of 4 (sol2 for it, gemini against), and its text is reverted (`r20/REPORT.md`).
- **P1, the absolute rubric (sol2), for the kept text: 3, 3, 3.** The published PRD anchors score **3.67** under the same calibrated prompt. The paper's text stays below them on this measure.
- The paper's register rounds are closed.

## 10. Deferred to the note round n4 (recorded, not fixed)

1. **The note's inconsistency on its main result:**
   - `main_note.tex:72` says "Its principal result is a cross section in five observables";
   - `sec_execsummary.tex:6` says "The main results are the validation findings";
   - `sec_summary.tex:4` says the same, a second site.
2. **"Calibration" in the interval sense** (second review F2; director 2026-10-28). N1 defines a test's calibration
   beside interval coverage. r19 changed `sec_5d.tex:8` to "Coverage asks". These six sites still use the interval
   sense: `sec_5d.tex:90`, `sec_5d.tex:179`, `sec_validation.tex:4`, `sec_pet_campaigns.tex:61`,
   `sec_pet_campaigns.tex:119` and `app_statmethods_nd.tex:62`.

## 11. Untouched, and yours

- **KI-85** (`KNOWN_ISSUES.md` row 85): "OPEN, DEFERRED 2026-10-06; diagnostic 2026-10-07 consistent with (b)". "Joseph ruled 2026-10-06 that the held-out-MC re-test is deferred until after the publication package and is not pre-registered." Nothing here changes it.
- **`\pubhold`:** 2 uses in `main_paper.tex`, unchanged, including the deposit identifier in Data Availability.
- **Claims:** every claim's wording is yours; this packet changes none beyond the drafts marked here.
<!-- absence-ok: quotes printed and protected text, decisions and rater readings for Joseph; not a new absence claim -->
