# Supplement float layout repair

Parent: 7de6c6031. The decision is whether Table S6 can print its complete original
flow and table without overlap or squeezed columns, preserving all content and the
surrounding paragraph structure. The figures lane owns the layout; director-helper-3
integrates it and journal-editor reviews the render. Terminal checks are the note
and Supplement builds, the complete float audit and text identity. Local iterations
address specific layout defects; no scientific compute or new review campaign occurs.

## Table S6

The left/right arrangement and caption remain. A TikZ matrix replaces the fixed
picture. All nine nodes size to their exact original text, with padding and gaps;
the two unfolding paths, comparison, decision and return arrows retain their original
connections. The final PDF verifies all flow glyphs inside their boxes and no pair
of boxes overlapping. The right table uses its available minipage width, with ragged
cells, 4pt column padding and arraystretch 1.12. Hyphenation is disabled locally in
both parts. Fonts remain scriptsize. The compact height allows following text onto
the same page, removing the old float page's largely empty remainder.

Added usepackage: **tikz**, in main_supplement.tex only. Libraries: arrows.meta,
matrix, positioning. The shared preamble, note driver and paper are unchanged.

## All floats inspected

| Float | Before page | After page | Result |
|---|---:|---:|---|
| S1 observables | 2 | 2 | Equations and definitions fit; unchanged. |
| S2 sixteen cells | 4 | 4 | Boxes, covariance headings, values and median fit; unchanged. |
| S3 estimators | 7 | 7 | Long Results cells and configuration labels fit; unchanged. |
| S4 covariance groups | 11 | 11 | Thirteen columns and median fit; caption clears rule; unchanged. |
| S5 correlation matrix | 11 | 11 | Lower triangle and labels are separated; unchanged. |
| S6 generative model | 16 | 16 | Text-sized nodes, clear arrows and wider cells; repaired. |
| Figure S1 ratios | 22 | 21 | Legend, panels and cell key fit; asset unchanged. |
| S7 generator comparisons | 23 | 22 | Groups, block headings and footnotes fit; unchanged. |
| S8 covariance sensitivity | 23 | 23 | Columns and signed values fit; unchanged. |

All pages were rendered and checked at print scale; later floats were checked again
after reflow. No other float required source changes. Pagination shortens from 25
to 24 pages. Section and paragraph source order and lengths do not change.

## Content and build checks

The source outside Table S6 is byte-identical to the parent. Its caption and all
27 table-cell contents are byte-identical; all nine original node contents remain,
including jtBatch, jtBcap and every other scientific macro. Digests and checks are
in checks.json. No PDF is edited.

pdftotext -raw extracts both PDFs. Unicode NFKC and joined inter-letter hyphens
(including line-end hyphens) normalize typography. Word-token multisets are equal:
12,313 tokens each, zero removed or added; this permits float reflow without counting
it as a word edit. Removing each page-number footer also leaves exactly the same
2,118 numeric tokens, with zero differences. Source identity separately verifies
content order and unchanged symbols/macros.

main_note.tex and main_supplement.tex build successfully with latexmk. The final
Supplement log has no overfull box, oversized float or unresolved reference. The
baseline Background-cell overflow of 3.2099pt is gone. Existing unrelated font
substitution warnings remain. make_values_fived16.py --check passes 3811 values,
both source-figure checks and ten listed-truth sentences.

Only main_supplement.tex and Table S6 in supplemental_body.tex change, plus this
verification record. Integration checks and standalone-note synchronization remain
with the paper integrator. Nothing is pushed, submitted or deposited.
