# Table repair on the requested overflow-fix parent

Parent: c8a29cdbc. This is the zero-word repair delivered as one commit directly on
that parent. paper_body.tex is byte-identical to the previously verified repair at
06a3438f1, so it retains c8a29cdbc's padding fix and applies the missing row/column
layout changes. No caption, header word, table cell, value, key, name or order changes.
The later optional short-span-label repair e60e0e7e3 remains separate.

Table 1 keeps all existing column widths and tabcolsep 2.25pt. Only vertical space
is added: extrarowheight 1.5pt and addlinespace[3pt] before the second and third italic
group headings. No column is widened or converted to an all-natural layout.

Table 2 keeps only Truth as a fixed 3.0cm ragged column, with four long names broken
at their comma. The all-natural trial in the verified repair overflowed by 42.2616pt,
so the allowed Truth-wrap fallback is retained. Covariance and flagged-cell columns
are natural-width l: minus GENIE + MEC and R02, R06, R07 remain on one line. Every p
column is l, while chi-square and maximum-|z| stay r. Four standalone group gaps
follow Tune v1, GENIE + MEC EW shape, the NuWro closure and GiBUU hybrid.

main_paper.tex builds successfully with fully resolved references. Final log counts:
Table 1 Overfull = 0; Table 2 Overfull = 0; entire paper Overfull = 0. No oversized
float. Both tables fit and their pages were rendered and inspected. Table 1 remains
on page 5 and Table 2 on page 8. The existing note aux and bibliography are untracked
build aids copied from the earlier table worktree.

Removing only the inserted newline/addlinespace commands leaves both table cell
blocks byte-identical to the parent. Checks and content digests are in checks.json.
make_values_fived16.py --check passes 3811 values, both source-figure checks and ten
listed-truth sentences. Integration checks and standalone-note synchronization remain
with director-helper-3. Nothing is pushed or submitted.
