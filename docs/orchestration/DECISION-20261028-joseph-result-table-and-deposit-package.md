# DECISION 2026-10-28 — Joseph: the paper prints the sixteen-cell result table; the data-deposit package is prepared, not deposited

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- r19's outline (`state/2d-closeout/stageF/methods/r19/outline.md` §2) adds a compact result table, `tab:result16`.
- The director's survey of seven PRD measurement papers found no per-bin values table in any of them. The
  director's first account of it, that those papers all report 44–205 bins, was wrong: T2K arXiv:2102.03346 reports
  5, 4 and 3.
- Joseph asked for an independent judgement. The consult (`secondary-results/astra-consult-table-20261028/`, PR #439)
  recommended option C:
  - the sixteen-row table in the paper, with one marginal uncertainty column (C_total + C_resp), a statement that
    quantitative use needs the full covariance, a note that the entries are cell integrals, and an explanation of the
    "100" edges;
  - the cell definitions, vector, covariance and correlation matrix in a versioned, machine-readable repository cited
    by the article.
- A data deposit is publication, and the standing rule is that nothing is deposited. So the director asked Joseph
  whether to prepare the package or deposit it.

Joseph's answers, verbatim. On the table and the deposit:

> yes keep the table with that advice applied. we can do the recommended deposit too for now

sha256 of the text plus a final newline begins `c3ffb79cadd5b82d`.

On what happens to the deposit now, the option he selected:

> Prepare it, don't deposit (Recommended)

sha256 of the text plus a final newline begins `d2db70342b24c042`.

## What is decided

1. **The paper prints `tab:result16`,** with the consult's advice applied:
   - one uncertainty column, the reported C_total + C_resp, labelled as marginal;
   - the caption, or the first sentence after it, states that quantitative comparisons need the full covariance;
   - the entries are cell-integrated cross sections, not differential densities;
   - the "100" edges are explained as what they are, without being replaced by infinity.

   Every entry is an existing `\fvval` key from the pinned data product, as r19's outline §2 requires.
2. **The deposit package is prepared, not deposited.**
   - It holds the cell definitions, the measured vector, the reported covariance and the correlation matrix, in a
     machine-readable form with a README giving the cell order, units and covariance convention. It has enough
     precision to reproduce the paper's χ², and it identifies GiBUU's eight-cell subset.
   - It is built from the committed data product (`fd/data-product/fd_data_product.json`, `b79556f0`), verified
     against it, and committed as a candidate.
   - **Nothing is uploaded, and no DOI is minted,** until Joseph releases it. That comes after his review with Ben and
     the MINERvA collaboration review.
3. **The paper's citation of the deposit and its data-availability wording** are drafted as proposals for Joseph in the
   final draft (d). The data-availability text stays his.

## Not changed

- Q8 (whether the article carries supplemental data) and the release text (`app_release.tex`) are Joseph's.
- Claims, KI-85, `\pubhold`, the abstracts' final wording and the title are Joseph's. Nothing is submitted, deposited
  or tagged.
