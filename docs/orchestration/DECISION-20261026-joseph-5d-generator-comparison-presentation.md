# DECISION 2026-10-26 — Joseph: how the 5D generator comparison is presented, and a comparator check first

**Recorded by** the paper-tighten lane, as director.

**What led to it.** Joseph asked for the presentation options for the 5D data-against-generator comparison
(`DECISION-20261026-joseph-gsens-per-group-split.md`, item 3). The director offered four:
1. a χ²/ndf table under the reported covariance, with one quantified sentence on its correlation sensitivity;
2. the table with sensitivity columns;
3. a qualitative statement with ratio plots only;
4. option 1 plus a figure of the cell-contrast modes that carry the χ².

The director recommended option 1 in the paper and option 4 in the note, with the sensitivity table, the G-DIAG
breakdown, the R04 look and the fake-data limitation in the note. He also offered a check of length-matched published
comparisons before the wording is fixed.

Joseph's answer, verbatim:

> sure queue the check of other publications and I also agree with your recommendation for option 1 in the paper and 4 in the note

sha256 of the text plus a final newline begins `5c9ee150595567a8`.

## What is decided

1. **The paper uses option 1.** It prints the χ²/ndf table of each prediction under the reported covariance,
   C_total + C_resp + V_g, with shape-only beside it and GiBUU on its eight cells. A ratio figure goes with it, and one
   quantified sentence on the correlation sensitivity.
   - That sentence names the covariance group that carries the sensitivity, once the per-group split has reported.
   - The fake-data limitation for GiBUU-like truths is stated where the GiBUU comparison is given.
2. **The note uses option 4.** It carries option 1's table and sentence. It adds:
   - a figure of the cell-contrast modes that carry the χ², with each prediction's distance along them;
   - the G-SENS sensitivity tables;
   - the G-DIAG breakdown;
   - the R04 look;
   - the fake-data results.
3. **No diagonal-only χ² is printed.**
4. **A comparator check comes before any wording is written.** The paper rewrite lane runs it, read-only.
   - At least four published neutrino cross-section papers that compare data with generator predictions using a full
     covariance, each verified on its arXiv abstract page.
   - For each, it records with quotes:
     - the form of the χ² table;
     - full against diagonal χ²;
     - any statement about correlation sensitivity, its wording and where it sits;
     - any sensitivity variant or mode decomposition.
   - If the practice differs from this decision, the lane reports it to the director, and Joseph decides again.
5. **The wording itself is Joseph's.** It is drafted with the 5D section's integration, and agy checks it.

## Not changed

- Claims, KI-85, `\pubhold`, data-availability and release text are Joseph's. Nothing is submitted, deposited or
  tagged.
