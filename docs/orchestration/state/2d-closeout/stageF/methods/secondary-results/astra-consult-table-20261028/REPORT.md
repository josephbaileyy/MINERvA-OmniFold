# Independent consult: should the paper print the sixteen-cell result table? (2026-10-28)

**Asked for by** Joseph (2026-10-28): "can you have an independent astra session judge this decision? make sure it
considers both standard and our case". The decision is whether r19's paper prints a sixteen-row result table
(option A) or only the cell edges, with the values in supplemental material (option B).

**Run by** the paper-tighten lane, as director.

**MEASURES:** nothing. It is advice from a model, recorded as given.

**CITABLE FOR:** what the consult recommended, from which inputs.

**NOT CITABLE FOR:** APS or PRD policy, or what published papers do, beyond the identities and table contents
checked below. The decision is Joseph's.

## How it was run

- **Model and account:** `gpt-6-astra`, reasoning `high`, sandbox `read-only`, on `codex-school`, rc 0. The run log
  is not committed (`*.log` is ignored); its sha256 begins `938389ed6ae1eeb7`.
  - The first attempt, on `codex-school2`, waited on an open stdin and was stopped. The second, with stdin closed,
    stopped at codex-school2's usage limit before answering. Both accounts are on the delegation allow-list.
- **Inputs** (`inputs/`, digests in `SHA256SUMS`): the brief (`PROMPT.md`), with both options, the facts of the
  paper, and the director's seven-paper survey of table captions; and the note's rendered table
  (`note-table.txt`, from the #413 build at `a55e2686`).
- **Not given:** the director's recommendation, the second scope review's request for a result table, and any rater
  score.
- **Web access:** it opened public arXiv pages for 2106.16210 and 2102.03346, and it cites others.
- **The answer:** `answer.txt`, verbatim.

## What it recommends, in brief

**Option C:** print A's sixteen-row table in the paper, and deposit the cell definitions, the measured vector, the
reported covariance and the correlation matrix together in a versioned, machine-readable repository cited by the
article. Keep the note for detailed documentation.
- The uncertainty column is the reported C_total + C_resp, labelled marginal, with a statement that quantitative
  comparisons need the full covariance.
- The caption says the entries are cell integrals, not differential densities, and explains the "100" edges.
- If neither supplemental material nor a repository release happens, A is still preferable to B. The missing reusable
  covariance is then a separate defect.

## Checked by the director

- **Its correction of the brief holds.** T2K arXiv:2102.03346's χ² caption reads "ndof of χ²_tot is equal to 5, 4,
  and 3", so that paper reports 5, 4 and 3 cross-section bins and points to a release for the values. The brief's "44
  to 205 bins" was the director's error, from a misread of the director's own extraction.
- **Its new precedent holds.** arXiv:1302.4908, "Measurement of the Inclusive NuMu Charged Current Cross Section on
  Carbon in the Near Detector of the T2K Experiment", Related DOI 10.1103/PhysRevD.87.092003. Its source has
  `tab:result` ("The differential cross-section measurement, with its statistical and systematic errors") and
  `tab:totcov` ("The total fractional covariance matrix"). Its bin count, given in the answer as 20, was not counted.
- **The seven corpus identities** were verified on 2026-10-23 (`register-prd-study/REPORT.md` §1), and 2405.20041 on
  2026-10-27 (`astra-consult-2-20261027/REPORT.md`).
- **Not checked:** its statements about APS supplemental-material and data-availability guidance.

## Not changed

- r19's outline and the paper. Option C needs a data deposit, which is publication and Joseph's decision (Q8 and the
  data-availability text).
- Claims, KI-85, `\pubhold`, data-availability and release text are Joseph's. Nothing is submitted, deposited or
  tagged.
