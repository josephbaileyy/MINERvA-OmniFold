# Table layout pass

Baseline cells: d53af941a (identical to d1d60e74f); before PDF: director-helper-3's d1d60e74f build.
After: locally built main_paper.pdf with the short captions and selected layouts. No new package.

| Table | Width before → after (pt) | Body height before → after (pt) | Median body font before → after |
|---|---|---|---|
| 1 outcomes | 499.4 → 508.1 | 398.5 → 389.4 | 7.97 → 7.97 |
| 2 fake-data tests | 461.1 → 508.1 | 223.4 → 195.0 | 7.97 → 7.97 |

Width/height are PDF booktabs-rule geometry, excluding captions. Raw metrics and cell hashes in
comparison.json. The source between top rule and closing tabular is byte-identical before/after
for each table, as are their captions. Therefore all headers, cell words, values, fvval/fvcase keys,
row order and names survive unchanged. No detail moved to a note; no rows added, removed or split.

## Selected layout

- Both remain Revtex table*, booktabs, footnotesize. tabular* fills textwidth with flexible gaps.
- Table 1: ragged-right Test 5.0cm, Result 9.0cm and Status 1.8cm; estimator categorical left;
  section references right-aligned. tabcolsep stays 3pt. Original Test width retained; modest Result
  widening reduces wrapping without squeezing Test into many more lines. Ragged right removes
  stretched word spacing in the original justified text columns. It remains a dense table.
- Table 2: ragged-right Truth 3.1cm and covariance 1.65cm; three flagged-cell columns 1.25cm each;
  all numerical chi2/p/max columns right-aligned. tabcolsep stays 2pt. Wrapping the cell-list columns
  frees room to widen the truth names, shortening several multi-line rows. No siunitx S columns:
  formatted fvval outputs include math and inequalities, so ordinary r columns preserve them directly.

## Alternatives tried

1. Original: wider justified Test, narrower Result, natural-width Status/cell lists. Retained as before.
2. Table 1 Test 3.75cm / Result 9.8cm: rejected after rendering. The Result column shortened but too
   many Test cells grew to three lines; table became substantially taller. A dedicated float page was
   required. The selected balanced layout preserves the original Test width and improves total height.
3. Selected Table 2: wider Truth plus wrapped flag lists; rendered without collisions and shortened
   body by about 28pt. No need to shrink fonts or remove any of the three covariance groups.

## Validation

main_paper.tex built successfully with latexmk; final log has no overfull box or too-large-float
warning. Tables rendered and inspected: no column overlap, clipped text, rule collision or misaligned
numeric entries detected. make_values_fived16 --check passes (3811 values and all ten listed-truth
sentences). Both cell blocks and captions have exact identical SHA256 before/after. No package
additions: booktabs, array and siunitx were already loaded; only booktabs/array formatting is used.
The original table captions/status definitions were not shortened or reworded in this commit.
