# b3 notes (Sec. V, The sixteen-cell cross section): choices a reviewer should know

Revised after the reviewer's ADOPT-AFTER-FIXES verdict (two MINOR fixes):
1. F331: "The five-observable $(\Eavail,W)$ map of the earlier purity-subtracted central value, and its comparisons
   with these generators, are given in ...". This ties the pointer to the four generators named in the previous
   paragraph.
2. F326: two sentences (see below).

## Order and floats

- **Order.** The paragraphs follow the outline:
  - V A has one paragraph, then Table III.
  - V B has ¶1, then Fig. 4 and Table IV, then ¶2 (sensitivity and bootstrap).
  - V C has two paragraphs.
- **Floats:**
  - Table III is F295–F302 and Table IV is F318–F320. Each keeps its `\caption` and then its `\label` where the
    ledger has them, with the tabular verbatim.
  - The lines between `\label` and `\begin{tabular}` are carried from the base at assembly (director).
  - Fig. 4 has `\centering`, because F312's base text shows it.
- **Labels.** `V A` has no label, as in the outline. The labels run in order: `sec:result16`, `tab:result16`,
  `sec:gen16`, `fig:ratio16`, `tab:gen16`, `sec:central`.

## Wording chosen to fit an atom

- **F292.** "for each cell, its box in the five observables, ...". I left out the cell names R00–R15, because no b3
  atom holds them (check c) and Table III lists them.
- **F293 and F294.** I joined the correlation-matrix pointer to the claim: "..., so quantitative comparisons need
  the full covariance, whose correlation matrix is given in Ref. [note], Table N." F294's atom begins
  "Table~\ref*{N-tab:fived16-cells} there gives ...", so it follows as its own sentence.
- **F304 and F305.** The atom is "compared with any prediction ...", so the sentence is "Unfolded results can be
  compared with ...". It is followed by "This makes the two-dimensional result reusable, ...".
- **F306.** "... with five predictions through a $\chi^2$ against the reported covariance plus ..., with a
  shape-only $\chi^2$ beside it." The words "through a $\chi^2$ against" and "with a" are mine.
- **F309 and F310.** These two rows are joined with ", and", as in the base sentence. Splitting them would leave
  "MINERvA Tune~v1 is the simulation's prior." on its own, which reads as a non sequitur.
- **F314 (Fig. 4 caption).** "..., with $\sigma$ the square root of the diagonal of
  $C_{\mathrm{total}}+C_{\mathrm{resp}}$, and the predictions' finite-sample uncertainties are not drawn." The
  ", and" is mine.
- **F326 (reviewer fix 2).** The row is now two sentences: "... which the weakening probes." and "In particular,
  they are not intervals for the $\chi^2$ under the true correlations." Its `after` spans those two consecutive
  sentences, and the checker names it.
- **F329.** "..., in the region of the established low-recoil discrepancy~\cite{...}". The words "in the region of"
  are mine.

## Repeats and atom-forced deviations (atoms win)

- **A required repeat.** "Quantitative comparisons need the full covariance" appears in the text (F293) and in the
  Table III caption (F301). Both are rows.
- **No serial comma:**
  - F296 "$\pT$, $\pPar$ and $q_{3}$"
  - F311 "The GENIE + MEC, NuWro and GiBUU comparisons"
  - F323 "interaction, flux, detector and lateral groups"
- **Semicolons inside atoms:** F296 (inside the parenthesis) and F319 (the Table IV caption).
- **Numerals:** "8 cells" (F308, F315), "16-cell" (F321, F323, F325) and "16 degrees of freedom" (F323), as the
  atoms give them. Elsewhere "sixteen-cell" is spelled out.
- **Fragment.** "$\chi^2$ and its number of degrees of freedom of each prediction ..." starts the Table IV caption
  with a symbol. It is the whole atom.
- **R7.** V A has two note pointers (F293, F294) and one in the Table III caption (F299). V B has none. V C has one
  per paragraph.

## Checks and the smoke build

- See the report for `check_batch.py b3 --build`.
- The b3 GATE count is zero, as expected: the eight bound phrases belong to b2.
- A smoke compile of b1–b3 exits 0 with every `\fvval` key present. Table III is 33 pt overfull in the `article`
  driver's `table*`. That is verbatim material, and the revtex widths differ.
