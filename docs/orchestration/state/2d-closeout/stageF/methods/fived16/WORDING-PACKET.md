# Wording packet for Joseph: the sixteen-cell five-observable result in the paper and the note (2026-10-27)

**Why you are reading this.** `DECISION-20261027-joseph-5d-integration-then-second-scope-review.md` item 2: the printed wording of the 5D integration is yours and comes to you before it merges. The PR does not merge until you answer.

**What to read:**
- **`printed-wording.md`** (beside this file) gives every new paragraph and every changed sentence as it prints, with each number resolved:
  - §A: the paper's two new subsections;
  - §B: the note's new chapter, prose only;
  - §C: the 78 changed sentences of the existing text.
- **The tables are in the built PDFs.** Six are in the note (§10) and two in the paper (Tables IV and V).
- **Every number** comes from a committed readout pinned by sha256, through `make_values_fived16.py`. None is typed by hand; a check fails if one is.

**The inputs have landed** (#414, main 0a73bde1), and the four placeholders are swapped:
- the note prints the correlation matrix of C_total + C_resp (Table 13), generated from the data product (`fd_data_product.json`, pinned `b79556f0`);
- the paper's covariance sentence now reads "The note gives the cells, the central values, the per-group uncertainties and the correlation matrix of the reported covariance.";
- the paper prints the ratio figure (Fig. 5) and the note the modes figure (Fig. 30). Each is checked byte-equal to its committed source by `make_values_fived16.py --check`.

**New in the note's GiBUU sentence (§10.4), from the GiBUU aggregate (#416, `fd_gibuu_enu_aggregate.json`, pinned `66dcbd6d`):** "In the GENIE CV and NuWro samples, which stop at E_ν = 50 GeV, at least 11.71% and 12.59% of each generator's cross section in the phase space above p∥ = 4.5 GeV/c comes from E_ν > 20 GeV, against 0.83% and 0.77% between p∥ = 1.5 and 4.5 GeV/c: these are the parts that a sample stopping at E_ν = 20 GeV cannot hold, not GiBUU numbers." The C_model paragraph's band share now reads "at least 4.9–5.3%" for the same reason: both samples stop at 50 GeV, so each share is a lower bound. This is yours to keep or drop.

The figure captions are drafts, and they are yours (Q10).

**What the wording does and does not say:**
- It states the fake-data limitation once, in your f0-limitation decision's words: "the reported uncertainty does not cover the fake-data bias at the GiBUU-like truths or at the $q_3$ tilt".
- Under $C_{\mathrm{total}}+C_{\mathrm{resp}}$ the listed truths are:
  - Stage 0c GiBUU, by cell R06 alone ($z=2.01$);
  - A7 GiBUU;
  - the $q_3$ tilt.

  W3 is no longer listed. Each truth is graded without its own generator's vertex, where it has one.
- It makes no coverage claim, and nowhere says that $C_{\mathrm{model}}$ includes, covers or omits the regularization bias.

## The independent PRD read (decision item 3), in brief

The full tables, with the raters' quotes and a truth column for every shortening, are in `prd-read/REPORT.md`. The raters were sol2 (gpt-6.1-sol) and agy (gemini), blind, through `run_x.sh`.
- **Q3:** **(i) three sentences > (ii) one short sentence > (iii) one long sentence, in all 24 pairwise runs,** both orders and both models, with no order flips.
- **Q4:** the raters split. sol2 chose one decimal (2 of 2 runs) and gemini integers (2 of 2).
- **Q1, Q7, Q9 and the other qualifiers:** all four runs would shorten the Q9 envelope sentence (C03) and the Q1 clause (C05/C22).
  - **sol2 keeps every limitation** and shortens the wording.
  - **gemini drops the limitations** ("not a calibrated bound", "whose coverage is not validated"). Each of those cuts leaves a sentence false as read.
  - **Shortest true forms:** Q1, "it is generator-shape model dependence, not a calibrated bound"; Q9, "Unlike the envelope of Sec. V E, its model term is a covariance built from three generator shifts." Q7 stays as written.
- **Unanimous and true, not applied:** cut C10 and C14; shorten C03, C18 and C21; and C08, whose drafted form is ambiguous now that Sec. VII B uses C_resp.
- **Q5:** **agy does not agree with the decided sentence.** It reads "stays within the reported uncertainty" as within 1σ, while the criterion allows 2σ (A7 NuWro reaches 1.34σ). It accepts "the bias passes both criteria: no cell beyond 2σ and p ≥ 0.01" and "the bias is within 2σ in every cell and p ≥ 0.01". The numbers hold under every form. **Applied (director, 2026-10-27) as a truth fix:** "At the other 9 truths the bias passes both criteria: no cell beyond 2σ and p ≥ 0.01." Your sentence's "stays within the reported uncertainty" reads as within 1σ, while the criterion allows 2σ.
- **Applied to the paper:** the unanimous true shortenings and the two accuracy fixes (C06, C08). Every change, with its rater verdicts, is in the change table of `prd-read/REPORT.md`.
- **Next:** your decision moves the non-final configurations to the note (`move/MOVE-OUTLINE.md`, `move/config-inventory.md`). The abstracts are re-proposed after the move.

## Your questions

**Q1. $C_{\mathrm{model}}$ and the regularization bias.**
- The text says what $C_{\mathrm{model}}$ is: "the change in the unfolded data when the prior is reweighted to each generator (GENIE + MEC, NuWro, GiBUU), unscaled and not a calibrated bound".
- It then points to the fake-data comparison. Whether $C_{\mathrm{model}}$ "includes" the regularization bias is a reading the records do not make.
- **Options:**
  - **(a) leave the text as it is** (recommended: it is true and complete);
  - **(b) add a sentence of your own,** e.g. "it is not constructed as a bound on the estimator's regularization bias";
  - **(c) other.**

**Q2 — answered (DECISION-20261027-joseph-5d-wording-q2-q5 item 1): no p-values; the text was already in that form.** p-values in the χ² table (your format decision names χ² with ndf and does not mention p).
- **(i) As drafted:**
  - the table prints χ² with ndf and shape-only;
  - the four "no covariance-based significance" sentences are scoped to the configuration-(a) covariance, with a pointer to the sixteen-cell comparison.
- **(ii) With p-values:**
  - each χ² gains its $p$: GENIE CV $5.9\times10^{-16}$, GENIE + MEC $1.5\times10^{-48}$, NuWro $2.1\times10^{-31}$, GiBUU $9.3\times10^{-10}$, Tune v1 $1.7\times10^{-60}$; shape-only likewise;
  - the four sentences then read "no significance based on the configuration-(a) covariance is quoted; the sixteen-cell comparison quotes $p$ for each prediction (§x)".
- **Choose (i) or (ii).**

**Q3. The sensitivity sentence.** Your presentation decision says the paper prints one quantified sentence on the correlation sensitivity.
- **(i) As drafted,** three sentences, as the director accepted:
  > "Weakening only the flux correlations by 10 % lowers the χ² of the 16-cell predictions by 24–48 %. The same change to the detector or lateral correlations lowers it by at most 18 %. With the correlations of the interaction, flux, detector and lateral groups removed, every 16-cell prediction keeps χ² ≥ 45 for 16 degrees of freedom."
- **(ii) One sentence, in the paper:**
  > "Weakening only the flux correlations by 10 % lowers the χ² of the 16-cell predictions by 24–48 %, against at most 18 % for the detector or lateral correlations."

  The χ² ≥ 45 clause then moves to the note.
- **The bounds,** recomputed from the readouts: flux 23.8–47.6 %, detector 9.6–17.9 %, lateral 9.1–16.1 %, joint minimum 45.33/16.
- **GiBUU** is not in the sentence. Its 8-cell values are in the note's table.

**Q4. χ² precision in the paper.**
- **As drafted:** the paper prints integers, as in your example "109/16"; the note prints two decimals (109.35/16).
- **Alternative:** two decimals in both.

**Q5 — answered (same decision, item 2), and applied in the paper and the note:** "At the other 9 truths the bias stays within the reported uncertainty by both criteria: no cell beyond 2σ and p ≥ 0.01." The positive half of the limitation.
- **As drafted:** "At the other 9 truths neither criterion is met". This describes the triggers and makes no reading.
- **Alternative,** positive-first as in the October draft: "At the other 9 truths the reported uncertainty covers the fake-data bias". That is a reading of the triggers as coverage of the bias, which is yours to make or not.

**Q6. The abstracts.** Both abstracts are yours and unchanged. Each now prints something false once the result prints.
- **Paper abstract:**
  - "it yields central values only" is false: the paper reports the sixteen-cell result with total uncertainties;
  - "whose normalizations agree" covers only configuration (a);
  - "no tested reporting definition meets our 10% precision criterion" should name the precision study's definitions.
- **Note abstract:**
  - "The five-dimensional central value and its covariance use the purity subtraction … which no quoted uncertainty includes";
  - "The negative-weight treatment is used for the two-, three- and four-dimensional central values";
  - "that no quoted uncertainty includes".

The writer's proposed forms, site by site, are in `writer/abstract-proposals.md`.
- **They are proposals only.** Each names the configuration-(a) product, adds the sixteen-cell result, and makes no coverage claim.
- **Neither abstract names the new result yet.** Whether it should is your call.
- **The executive summary** likewise has no results item for it. A proposed item: "A sixteen-cell five-observable cross section, configuration (e), with total uncertainties (§10)".

**Q7. Scope and Limitations (paper).** The writer printed product scoping in both paragraphs, and those sentences are in this PR for your approval:
- **Scope:** "The sixteen-cell result of Sec. V F also has total uncertainties, whose coverage is not validated."
  - This is the director's ruling 3: it keeps the 7.3 % median from being read as a validated uncertainty.
- **Limitations:** the regularization-bias clause is scoped to configuration (a), with a pointer to Sec. V F.
<!-- absence-ok: quotes or summarizes the note's and paper's printed text, or a ruling about it, as this PR's record; not a new absence claim -->

**Further wording that is yours, offered with options** (`writer/abstract-proposals.md`, last section):
- "The paper does not deliver a validated five-observable cross-section measurement": (a) keep, or (b) "… whose intervals have validated coverage; the sixteen-cell result of Sec. V F is reported with total uncertainties and a fake-data study";
- whether the sixteen-cell limitation is also stated in Limitations, in your words.

**Q8. Release text and the supplemental data file.**
- App. G's release lists name "the five-axis covariance used in this note" as the only covariance. Proposed scopings are in `writer/abstract-proposals.md`.
- Whether the release and the paper's supplemental file carry f, $C_{\mathrm{total}}+C_{\mathrm{resp}}$ and the cell boxes, and in what format, is yours. The covariance export now being made is the input.

**Q9. One placement sentence (paper reviewer's request, drafted for you):**
> "Its model term differs from the study's envelope: there, the largest shift of a cell over five generator-sized truth changes, added linearly to the half-width; here, a covariance built from three generator shifts."

It sits right after the precision study's "none … meets this target", so that a reader does not compare the 7.29 % median with the 10 % target on different terms. It makes no claim about the target. Keep, reword or drop it.

**Q10. The two figure captions (drafts; yours).**
- **Paper, Fig. 5:** "Data over prediction, f/g, on the sixteen cells for the five predictions of Table V. Each error bar is (f/g) σ/f, with σ the square root of the diagonal of C_total + C_resp; the predictions' finite-sample uncertainties are not drawn. GiBUU (lower panel) is shown on its 8 cells with p∥ < 4.5 GeV/c only. The key below the axes gives each cell's box. The χ² of Table V uses the full covariance, whose correlations the error bars do not show." The last sentence follows FD-G-FIGURES-REPORT's ruling 10.
- **Note, Fig. 30:** "The three eigenmodes that carry the largest shares of each sixteen-cell prediction's χ² (columns, by rank), for GENIE CV, GENIE + MEC, NuWro and MINERvA Tune v1 (rows), from the reported comparison on C_total + C_resp + V_g relative to f. The bars are each mode's unit loadings on R00–R15, signed so that the largest loading is positive. Each panel gives the mode's share of the χ², its relative σ and the prediction's distance along it, the projection over σ. The residual is (f − g)/f, so a positive distance means that the data lie above the prediction along the mode as signed. GiBUU, compared on 8 cells, has no modes here."
- Each clause is taken from FD-G-FIGURES-DECLARATION.md's figure rows and its K2–K4 controls.

## For the final draft: items that are yours, from the move and the framing (2026-10-27)

**Title** (outside the abstract block, so it is not edited; DECISION-20261027-joseph-measurement-framing). The options, with the PRD read's choice (round 3, all four runs chose T1; `prd-read/r3/`):
- T0 (current): "Performance and limitations of multidimensional OmniFold unfolding with MINERvA open data"
- **T1:** "Simultaneous measurement of the ν_μ charged-current inclusive cross section on hydrocarbon in five observables from MINERvA open data"
- T2: "Charged-current inclusive ν_μ cross section on hydrocarbon in muon kinematics, available energy, three-momentum transfer and hadronic invariant mass from MINERvA open data"
- T3: "Five-dimensional ν_μ charged-current inclusive cross section measured with unbinned unfolding of MINERvA open data"

**The abstracts** are drafted in the tree (paper 204 words, from 117; note 349, from 583), led by the sixteen-cell result, with no configuration label and every number through `\fvval`. Round 3: the paper abstract's length is ACCEPTABLE in 4/4 runs; the note abstract is TOO-LONG in 2/4 (sol2). The limitation clauses change when 1A and 3D report (DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap).

**Data availability** (main_paper.tex, yours; not edited). After the move, Sec. VII A no longer quotes the (E_avail, W) map's numbers, so "It recomputes … the numbers quoted in Sec. VII A, and it regenerates the analysis note's figures of the joint-test null distributions and the (E_avail, W) map" points at numbers the paper no longer prints. Proposed: "It recomputes every p value, decision, robustness result, and power figure of the joint tests and the five-observable (E_avail, W) map's numbers quoted in the analysis note, and it regenerates the note's figures of the joint-test null distributions and of that map."

**Release scopings (app_release.tex, yours; not edited).** Round 2 accepted R1–R4 ("…of the configuration-(a) central value") in all four runs (`prd-read/r2/`). Whether the release carries the sixteen-cell vector and its covariance stays Q8.
<!-- absence-ok: states which printed text is not edited and why (it is Joseph's), and quotes the data-availability sentence; not a claim that a result is absent -->
