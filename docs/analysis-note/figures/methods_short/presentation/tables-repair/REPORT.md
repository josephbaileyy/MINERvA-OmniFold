# Zero-word table repair

Parent: be76b8310, on figures/methods-table-repair-20261110. No caption, cell word, value, case key,
row name or order changed. No glossary/detail moved. No package added. Both tables stay Revtex
table*, booktabs and footnotesize. Checks and normalized cell hashes are in checks.json.

## Table 2

Tried all columns at natural width, with the requested left-aligned p columns. The fully resolved
paper log reported 42.2616pt alignment overflow, so the all-natural trial was rejected. Final form:

```
@{\extracolsep{\fill}}>{\raggedright\arraybackslash}p{3.0cm}lrllrrllrll@{}
```

Only Truth has a fixed width; every other column is natural width. Only four long Truth names break
at their comma: GENIE + MEC hybrid, GENIE + MEC (E_avail,W) shape, NuWro (pT,p_parallel,E_avail) shape,
and NuWro shape/noise-free closure. The twelve natural truth widths were measured at the table's
footnotesize; these four exceed the 3.0cm column. Short names stay on one line.

All three flagged-cell columns are l and cannot wrap: R02, R06, R07 now stays on one line in each
GiBUU-hybrid entry; there is no isolated R07 continuation line. Covariance names are natural-width l,
so minus GENIE + MEC stays intact. All three p columns are l (one leading digit aligns ordinary
numeric decimal points); chi2 and maximum-|z| columns remain r. Optional addlinespace[3pt] is on its
own line after Tune v1, GENIE + MEC EW shape, NuWro noise-free closure and GiBUU hybrid.

## Table 1

Added extrarowheight=1.5pt locally, and addlinespace[3pt] before the second and third italic headings.
The resolved-reference padding correction (tabcolsep 2.25pt, rather than the parent's 3pt) is carried
into this branch to avoid the known 4.85pt alignment overflow. Test/Result/Status widths, all cell
contents and the full original glossary/caption remain unchanged.

## Fit and verification

| Table | Body height before repair | Body height after | Printed width | Median body font |
|---|---:|---:|---:|---:|
| 1 | 389.4pt | 434.1pt | 508.1pt | 7.97pt |
| 2 | 195.0pt | 197.9pt | 508.1pt | 7.97pt |

Table 1 costs 44.7pt of body height, slightly more than the requested estimate, and still fits on
page 5. Table 2 is on page 8 and fits. The normal paper built with latexmk and fully resolved references;
there are no overfull boxes or too-large-float warnings. The note aux was copied from the already built
identical note sources in the figures worktree; no manuscript/figure output from another lane was edited.
Both table pages were rendered and visually inspected: no split covariance label, stray flagged-cell
line, column collision or clipped float remains. Table 1 row/group separation is visible.

make_values_fived16 --check passes all 3811 values and ten listed-truth sentences. For each table,
after removing only the inserted addlinespace and newline formatting commands, all text from top rule
to closing tabular is byte-identical to be76b8310. Captions are byte-identical without normalization.
Thus every cell/header and all fvval/fvcase keys survive exactly. No scientific number or claim changed.
The integrator owns check 9, the rater build, final referee review and standalone-note synchronization.
