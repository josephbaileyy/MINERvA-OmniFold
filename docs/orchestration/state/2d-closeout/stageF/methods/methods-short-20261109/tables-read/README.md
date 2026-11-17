# Tables S9–S12 merged into S9 and S10: layout and meaning read (2026-11-12)

**What changed.** Joseph's read of 800579be, via the director: the four headline-test tables each floated alone on a
`[p]` page, half empty, with narrow ragged columns and stacked `\newline` lists. The fix follows the director's order.
- Tests 1–10 are now one table for what each tests and how it is built (`tab:tests-spec`, S9). A second table gives
  statistic, threshold and result (`tab:tests-result`, S10).
- Both are full width, in `\small`, with X columns. Cell lists are comma-separated phrases or short labelled sentences.
- Row 9's result spans the statistic, threshold and result columns.
- They sit at the start of S8, straight after its opening paragraph. The fresh referee's structure point 10 (283f3044)
  asks for the same placement: "consolidate at the start or end of S8".

**Why the tables break across pages.** Each merged table runs past a page, even at `\footnotesize` after rebalancing
the columns: S9 by 62–95 pt and S10 by 45–56 pt. S10's row 10 grows further once LL5D is graded. Two alternatives were
tried and rejected:
- A float that size takes whole pages.
- An afterpage landscape page pushed the floats past Table S11 and swapped the table numbers.

So each table is an `xltabular` (tabularx X columns inside longtable), sitting in the text flow with its header repeated
under "Table S<n>, continued". Every page break falls where the next row does not fit. Page 22 ends at y = 654 pt
against a 720 pt text bottom, and row 8 needs about 62 pt.

**Gates extended** to count an xltabular as a table, so the numbering stays checked:
- `docs/analysis-note/check_supp_pointers.py` now has a self-test case with an xltabular between two tables. That case
  caught a `re.findall` capture-group bug before the commit.
- `rater-calibration/make_supp_rater_copy.sh` counts table environments.

The paper's `\stab{S14}{tab:prr-rho}` is now `\stab{S12}`, as check_supp_pointers required, and the Supplement's own
pointer to `tab:tests-result2` (test 6) now points to `tab:tests-result`.

**Meaning read.** An independent general-purpose subagent, read-only, worked from `pairs.tsv`: 33 changed cells, old
against new, exported from HEAD 283f3044 against the working tree.
- First pass: 27 OK, 6 DEFECT, all grouping or scope losses from flattening the lists. Every fix was applied, with full
  stops or labels where the reader proposed semicolons:
  - 3a's per-cell $z$ read as a covariance term;
  - "the estimator, IBU" read as an appositive;
  - "one factor at a time" reached IBU;
  - test 5 lost "paired replicas" on the 2D IBU count;
  - test 7's variants and ensemble were untagged;
  - test 8 lost "drawn".
- One typography point was also fixed: test 8's result began a sentence with a lowercase "two".
- Confirmation pass on the seven re-worded cells: 7 OK.
- Every `\fvval`, `\fvgroup`, `\fvgroupalt` and `\fvcase` is identical per cell. Rows 9 and 10 carry their text
  verbatim, apart from row 9's "Statistic and threshold as 10." lead-in.

**Builds** (make_supp_rater_copy.sh, make_rater_copy.sh):
- Supplement: 33 pages, 15 of 15 table captions, 4 of 4 figure captions, no overfull boxes.
- Paper: 17 pages, multiset PASS.
- check_round --fill-test PASS. make_values_fived16.py regenerated with no change, and its --self-test PASSES.
