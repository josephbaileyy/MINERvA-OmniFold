You are an independent referee and editor with a working knowledge of how Physical Review D publishes
neutrino cross-section measurements and unfolded measurements in high-energy physics. You have no stake in this paper.

## The decision

A paper intended for PRD reports a neutrino charged-current inclusive cross section measured simultaneously in five
observables and reported in **sixteen cells**. Each cell is a box in the five observables. The authors must choose
how the paper itself presents the sixteen measured values:

- **Option A: a result table in the paper.** One row per cell: the cell label, the box edges in the five observables,
  the cell-integrated cross section f, and its relative uncertainty under the reported covariance. The 16 × 16
  covariance and correlation matrices stay in the companion note, with a pointer.
- **Option B: cell edges in the paper, values in supplemental material.** The paper prints a table of the cell
  boxes only. The sixteen values, their uncertainties and the covariance go in supplemental material attached to the
  article.

A third option is acceptable if you think it is better. If so, define it as precisely as A and B.

## Facts about this paper (do not invent others)

- **The framing.** It is now a measurement paper led by the sixteen-cell result. It is being restructured into the
  usual order: introduction; data, simulation and observables; extraction; uncertainties and validation; the result
  with its generator comparisons; conclusions. The target length is about 8,000 words.
- **How the result is shown now.** As a figure of generator-to-measurement ratios per cell, a table of χ² between the
  result and five generator predictions (16 degrees of freedom; one generator on 8 cells), and a fake-data table.
  Neither the paper's text nor its figures print the sixteen measured values themselves.
- **The companion analysis note** is about 130 pages, public at a URL the paper cites. It prints the full table
  (`note-table.txt`: box edges, f, and σ under three covariance constructions) and the correlation matrix.
- **The cells** are irregular. They come from merging a finer grid for purity, so several boxes are open-ended
  (edges of 100) or span a whole axis. The median per-cell uncertainty is 7.29 %. The cells are strongly correlated,
  mostly through the flux; the paper reports that the χ² values fall by 24–48 % when only the flux correlations are
  weakened by 10 %. So any quantitative use of the values needs the covariance.
- **Supplemental material and data release.** Whether the article will carry the sixteen-value vector and its
  covariance as supplemental data is **not yet decided** by the authors. A separate candidate software and data
  release package exists, not yet deposited, and currently centres on other parts of the analysis.

## Evidence on standard practice (one survey by the authors' team; check it against your own knowledge)

The authors' team extracted every table caption, appendices included, from the LaTeX sources of seven published PRD
measurement papers: MINERvA arXiv:2106.16210, 2110.13372 and 2002.12496; T2K 2004.05434 and 2102.03346; MicroBooNE
2301.03700 and 2310.06082. In these papers:
- tables of per-bin cross-section values: 0 of 7. The papers point to supplemental material or a data release for
  them (4 of 7 mention one in the text);
- χ² tables of models against the data: 5 of 7;
- tables of bin edges: 2 of 7 (the two T2K papers);
- a table of integrated cross sections compared with generators: 1 of 7.

These papers report 44 to 205 bins, judging by their χ² degrees of freedom. The corpus was chosen, not sampled, and
seven papers is a small set.

## Answer in this form

1. **Your recommendation:** A, B or your third option, in one sentence.
2. **The standard case.** What PRD measurement papers usually do, and why. Use the survey above and your own knowledge,
   including any papers with few bins, unbinned or ML-unfolded measurements, and PRD's handling of supplemental
   material. Name every paper you rely on, with an arXiv identifier if you know it, and mark any you are not sure of as
   UNSURE. They will be checked.
3. **Our case.** Which facts above make this paper like or unlike the standard case, and how much each should weigh.
4. **What a reader loses** under each option, and what a referee is likely to ask for under each.
5. **The covariance.** Where the 16 × 16 covariance should live under your recommendation, and why.
6. **Any condition** under which your recommendation would change. For example: the supplemental-data decision going
   one way or the other.

## Rules

- Base everything on this brief, `note-table.txt` and your knowledge of the literature.
- Do not invent numbers about this paper.
- Do not soften a recommendation to be polite.
- You may not edit any file. Write your answer only as your final message.
