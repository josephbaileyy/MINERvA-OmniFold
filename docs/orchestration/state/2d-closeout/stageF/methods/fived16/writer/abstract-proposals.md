# Proposals for Joseph: abstracts, release text, and the paper's Scope and Limitations (writer W, 2026-10-27)

These files are Joseph's text. Writer W did not edit them. Each site is listed with a proposed form that uses the same
moves as the edits in the body: name the configuration-(a) product, add the sixteen-cell result with a pointer, add no
number, and make no coverage claim. Each proposal also follows the Group C ruling: it says what C_model **is**, and never
that it or the reported covariance "includes", "covers" or "does not include" the regularization bias.
Line numbers are at base 8b0f83fd. In the writer copy, main_note.tex and main_paper.tex sit one line later from line 7
and line 30 respectively, because of the approved `\input` lines. Site numbers are data rows of `scope-sites.tsv`.

## main_note.tex abstract (protected)

| site | line | base words | proposed form |
|---|---|---|---|
| 1 | 63 | "three-, four-, and five-observable MINERvA unfolds, each of which passes marginal-normalization checks against the lower-dimensional result to ≈1–2 %" | "…five-observable MINERvA unfolds, each of which, in configuration (a), passes marginal-normalization checks…". The (e) five-dimensional marginal was never compared (paper_body:169). |
| 2 | 72 | "the regularization bias is largest in this region" | "the regularization bias measured in the five-dimensional validation is largest in this region" |
| 3 | 82 | "The five-dimensional central value and its covariance use the purity subtraction" | "The configuration-(a) five-dimensional central value and its five-axis covariance use the purity subtraction; the sixteen-cell five-dimensional result uses the refined negative-weight subtraction" |
| 4 | 83 | "the central value keeps its bias of up to 4\% in the highest-$W$ cells, which no quoted uncertainty includes" | "that central value keeps its bias of up to 4\% in the highest-$W$ cells, which no uncertainty quoted for it includes" |
| 5 | 87 | "No full five-dimensional comparison of the two background treatments has been made." | **Leave unchanged.** It is still true: the configuration-(a) and sixteen-cell products differ in estimator and in cells, so they do not form such a comparison. Saying so in the abstract would be a new claim, so W does not propose it. |
| 6 | 89 | "The negative-weight treatment is used for the two-, three- and four-dimensional central values, in the generator tests, in some five-dimensional validation studies…" | "…used for the two-, three- and four-dimensional central values and the sixteen-cell five-dimensional result, in the generator tests, in some five-dimensional validation studies…" |
| 7 | 100 | "a residual bias, interpreted as regularization bias, that no quoted uncertainty includes" | "a residual bias, interpreted as regularization bias, that no uncertainty quoted for the configuration-(a) central value includes. For the sixteen-cell result, the model term of the reported covariance is the change in the unfolded data when the prior is reweighted to each generator (GENIE + MEC, NuWro, GiBUU), and a fake-data study compares the estimator's bias with the reported covariance" |
| 8 | 103 | "Statistical intervals miscover at the tested truths" | "Statistical intervals of a deterministic purity-subtracted variant (configuration (c)) miscover at the tested truths" |
| 9 | 104 | "none of the tested reporting definitions satisfies the predeclared 10\% criterion" | "none of the precision study's reporting definitions satisfies the predeclared 10\% criterion; the sixteen-cell result, the same H2 grid after a purity merge of its supported boxes, is reported with total uncertainties". Per the Group E ruling, the abstract does not print a count or σ. |

The abstract does not name the sixteen-cell result anywhere. Whether and how it should do so is Joseph's call, together
with the integrator's packet.

## main_paper.tex abstract (protected), line 44

| site | base words | proposed form |
|---|---|---|
| 10 (FALSE once printed) | "it yields central values only, whose normalizations agree with lower-dimensional results" | "it yields configuration-(a) central values, whose normalizations agree with lower-dimensional results, and a sixteen-cell result in configuration (e) with total uncertainties". The (e) normalization is unchecked, so "whose normalizations agree" must stay attached to the configuration-(a) values. |
| 11 | "Pseudo-experiments measure a background-subtraction bias, a partial recovery of generator-sized truth changes, and statistical undercoverage at the tested truths." | Proposed: "…and statistical undercoverage of a deterministic variant at the tested truths". The fake-data study of the sixteen-cell result is a different study with a different outcome. If the abstract names it, it is NOT CITABLE FOR coverage. |
| 12 | "With a model-dependence envelope added linearly to the uncertainty, no tested reporting definition meets our 10\% precision criterion." | "…no reporting definition tested in the precision study meets our 10\% precision criterion". This matches the edit W made to the findings table. |
| 13 | (FINE) "simulation-calibrated tests of hybrid null hypotheses…" | no change |

## app_release.tex (Joseph's release text, protected)

| site | line | base words | proposed form |
|---|---|---|---|
| 140 | 42 | "event-level unfolding, or the quoted closure, bias and covariance-status measurements" | "…or the quoted closure, bias and covariance-status measurements of the configuration-(a) central value". Whether RC7 covers anything of the sixteen-cell result is for Joseph to decide. W does not know it. |
| 141 | 55 | "**Central values**: the five-axis array and every projection quoted, each with its own checksum" | Joseph decides whether the R00–R15 vector is in the release (outline §1, "the supplemental data file … its release format is his"). If it is: "…the five-axis array of the configuration-(a) central value and every projection quoted, and the sixteen-cell vector R00–R15, each with its own checksum". If it is not: "the five-axis array of the configuration-(a) central value and every projection quoted…". |
| 142 | 56 | "**Covariances** ✓: the five-axis covariance used in this note and its $(\Eavail,W)$ projection" | "the five-axis covariance of the configuration-(a) central value and its $(\Eavail,W)$ projection". Add the sixteen-cell reported covariance only if the release carries it. Otherwise the list omits a covariance the note uses, so it is false by omission if the release is meant to carry every note covariance. |
| 143 | 63 | "that travel with the five-axis covariance used in this note" | "that travel with the five-axis covariance of the configuration-(a) central value" |
| 144 | 86 | "The five-axis covariance used in this note is the file \texttt{z-cv.npz}" | "The five-axis covariance of the configuration-(a) central value is the file \texttt{z-cv.npz}" |

## paper_body.tex Scope (line 46) and Limitations (line 405 at base, 415 in the copy): wording beyond product scoping, for Joseph

W edited only the product scoping in these paragraphs (ledger rows AMB151 and C5):
- **Scope:** one sentence was added: "The sixteen-cell result of Sec. V F also has total uncertainties, whose coverage is not validated."
- **Limitations:** the regularization-bias clause is scoped to the configuration-(a) central value, and a sixteen-cell sentence that only points was added.
<!-- absence-ok: quotes or summarizes the note's printed text, before or after this PR, as the writer's record; not a new absence claim -->

**For Joseph:**
- **"The paper does not deliver a validated five-observable cross-section measurement."** (site 152, left unchanged.) W left it unchanged.
  - It stays true while no coverage or validation claim is made.
  - It will sit beside the integrator's new subsection, titled "A sixteen-cell five-observable measurement". A reader may see the two as being in tension.
  - Possible forms:
    - (a) keep it as it is;
    - (b) "The paper does not deliver a five-observable cross-section measurement whose intervals have validated coverage; the sixteen-cell result of Sec. V F is reported with total uncertainties and a fake-data study."
  - The choice is a reading of "validated", which is Joseph's.
- **"Throughout, a three- to five-observable result is a central value without intervals of validated coverage"** (site 151). W kept it and added the sixteen-cell sentence after the colon clause.
  - Joseph may prefer to merge the two sentences: "Throughout, a three- to five-observable result is a central value without intervals of validated coverage, except that the sixteen-cell result also has total uncertainties, whose coverage is likewise not validated."
- **Limitations** (sites 177, 178). Joseph may want the sixteen-cell limitation stated here in his words. The outline puts the listed truths of the F0b study here: Stage 0c GiBUU, A7 GiBUU, and the q3 tilt.
  - W did not write them, because they are the integrator's numbers and labels.
  - W added a pointer only: "Sec. V F gives the fake-data study's measured comparison of the estimator's bias with its reported covariance."
- **Conclusions.** The conclusions paragraph had no FALSE or AMBIGUOUS site in the sweep. W did not change it.
