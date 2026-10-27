# Wording packet for Joseph: the sixteen-cell five-observable result in the paper and the note (2026-10-27)

**Why you are reading this.** `DECISION-20261027-joseph-5d-integration-then-second-scope-review.md` item 2: the printed wording of the 5D integration is yours and comes to you before it merges. The PR does not merge until you answer.

**What to read:**
- **`printed-wording.md`** (beside this file) gives every new paragraph and every changed sentence as it prints, with each number resolved:
  - §A: the paper's two new subsections;
  - §B: the note's new chapter, prose only;
  - §C: the 78 changed sentences of the existing text.
- **The tables are in the built PDFs.** Six are in the note (§10) and two in the paper (Tables IV and V).
- **Every number** comes from a committed readout pinned by sha256, through `make_values_fived16.py`. None is typed by hand; a check fails if one is.

**Two inputs have not landed.** The PDFs print `[PENDING: …]` where they go, and the build refuses to ship while either prints:
- the covariance export;
- the two figures from the 5D measurement session (the paper's ratio figure and the note's mode figure).

**What the wording does and does not say:**
- It states the fake-data limitation once, in your f0-limitation decision's words: "the reported uncertainty does not cover the fake-data bias at the GiBUU-like truths or at the $q_3$ tilt".
- Under $C_{\mathrm{total}}+C_{\mathrm{resp}}$ the listed truths are:
  - Stage 0c GiBUU, by cell R06 alone ($z=2.01$);
  - A7 GiBUU;
  - the $q_3$ tilt.

  W3 is no longer listed. Each truth is graded without its own generator's vertex, where it has one.
- It makes no coverage claim, and nowhere says that $C_{\mathrm{model}}$ includes, covers or omits the regularization bias.

## Your questions

**Q1. $C_{\mathrm{model}}$ and the regularization bias.**
- The text says what $C_{\mathrm{model}}$ is: "the change in the unfolded data when the prior is reweighted to each generator (GENIE + MEC, NuWro, GiBUU), unscaled and not a calibrated bound".
- It then points to the fake-data comparison. Whether $C_{\mathrm{model}}$ "includes" the regularization bias is a reading the records do not make.
- **Options:**
  - **(a) leave the text as it is** (recommended: it is true and complete);
  - **(b) add a sentence of your own,** e.g. "it is not constructed as a bound on the estimator's regularization bias";
  - **(c) other.**

**Q2. p-values in the χ² table** (your format decision names χ² with ndf and does not mention p).
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

**Q5. The positive half of the limitation.**
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
