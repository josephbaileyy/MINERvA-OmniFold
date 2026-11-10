# Table span and pending-cell check

Parent: 06a3438f1. Two presentation changes: Table 2's span labels are now “Reported”,
“Without C_PL,5D” and “C_total only”; the graded coverage-test cell in Table 1 has a
line break before “With them:”. The covariance definitions remain in the unchanged
Table 2 caption. No table cell wording, number, key, row order, caption or glossary
text changes. All other manuscript text is byte-identical to the parent after
normalizing only these span labels and the inserted line break (checks.json).

## Hard constraints

- The first span label measures 34.224pt, wholly inside its four-column trimmed
  cmidrule of 114.836pt. It cannot enlarge the last column of the span.
- No siunitx S column is introduced. Existing ordinary l/r columns expand fvval cells.
- Table 2's chi2int-key order is unchanged, and check_round's check 9 returns no failures.
- Table 1 retains the continued-run, repaired-run and over-coverage clauses inside
  the coverage-test cell. Its words are unchanged; only the line break is added.
- The complete status glossary stays in Table 1's caption, byte for byte. It is not
  moved because both the ordinary table and the long filled case fit their page.

## Recommendations adopted or retained

The short span labels are adopted. All p columns remain left-aligned; chi-square
and maximum-|z| remain right-aligned. Covariance labels and flagged-cell lists keep
natural width. The existing group gaps and four addlinespace commands remain.
No optional Cov. rename or Test-label rewording is needed.

A trial with natural-width Truth labels, including the shorter span labels, still
produced a 30.37039pt overfull alignment. Only Truth therefore retains its 3.0cm
ragged column and the four existing breaks at commas. The fixed-width flagged-cell
columns from the earlier draft are already gone. Table 1 keeps its 5.0cm Test column,
ragged text columns, 1.5pt extra row height and 3pt gaps before its second and third
group headings. Estimator and section alignment remain as in the delivered repair.

## Long coverage cell

The scratch proof uses make_values_fived16.ll5d_case and pending_lines, the same
helpers as check_round's fill-test machinery: graded campaign, offset-proceeded
route, over-coverage present, and all four readings set to the longest printed
class label, “no under-coverage detected”. No dummy value is written to the worktree's
values_fived16.tex or committed. This is a targeted longest-cell proof, not the full
all-class fill test; other pending groups retain their current state.

The cell occupied five lines before the break and six after it. “With them:” now
starts its own line, separating the two variants. Both the continued-run and
“Some cells over-cover” clauses remain visible at the end of the cell.

| Build/table | Page | Body height (pt) | Width (pt) |
|---|---:|---:|---:|
| Ordinary Table 1 | 5 | 434.105 | 508.095 |
| Long filled Table 1 | 6 | 481.428 | 508.095 |
| Table 2, either build | 8 | 197.930 | 508.095 |

The filled table uses a float page and fits without a too-large-float warning.
The ordinary and scratch-filled paper builds succeed with no overfull box or
undefined reference. The two table renders were inspected: headers, group gaps,
flagged-cell lists and the expanded coverage cell do not collide or clip.
make_values_fived16.py --check passes all 3811 values, both source-figure checks and
ten listed-truth sentences. Final integrated check_round, blind-copy verification
and standalone-note synchronization remain with the paper integrator.
