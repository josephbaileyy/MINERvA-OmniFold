# Compact deformation figure

Baseline: 3045fcbb5, whose producer and figure layout are unchanged from d53af941a.
Only the deformation producer and its regenerated paper-only PDF/PNG change, plus
this verification record. Captions, manuscript sources and all data files are unchanged.

## Layout and integration

Use `figures/methods_short/m3_fig2_deformation.pdf` at textwidth, **508pt**.
The figure canvas is 508 × 374.4pt rather than 508 × 496.8pt: 24.6% less height.
Each panel now has its own y-axis label; the x-axis label is one line, only below
panel (b). Both legends occupy the empty upper-left area inside their axes. Panel
titles sit above their energy-bin headings. The decreased spacing preserves the
height of the actual plotting regions and every authored font size. The existing
caption applies without changes.

## Data identity

The producer checked the three committed input records against m3_common's SHA256
pins and its plotting arrays against the pinned presentation_original_arrays.json.
checks.json repeats these data-only pins and verifies that the input bytes are
committed at the baseline. Both emitted arrays.json and numbers.json are byte-identical
to the baseline, covering all plotted means, standard errors and injected changes.
All 42 cells, offsets, axis limits and tick values are unchanged.

The two estimator configurations are unchanged: panel (a) is the lower-capacity
100-tree, 8-leaf refinement from the development record; panel (b) is the reported
400-tree, 31-leaf refinement from the assessment record. Their distinction remains
explicit in the titles and repaired caption.

## Printed text and overlap checks

The unchanged figtext.py measures each LTFigure's characters in full-paper before
and after proofs. Both proofs use the repaired captions and the Figure 3 asset at
508pt; the other figures retain their current inclusions. Raw measurements are in
before-font-sizes.txt and after-font-sizes.txt.

| Figure | Printed width (pt) | Median before → after (pt) | Maximum before → after (pt) |
|---|---:|---:|---:|
| 1 | 437 | 6.5 → 6.5 | 7.8 → 7.8 |
| 2 | 201 | 4.8 → 4.8 | 5.7 → 5.7 |
| 3 | 508 | 8.3 → 8.3 | 9.3 → 9.3 |
| 4 | 508 | 8.3 → 8.3 | 9.3 → 9.3 |
| 5 | 245 | 8.3 → 8.3 | 9.3 → 9.3 |
| 6 | 508 | 8.6 → 8.6 | 9.3 → 9.3 |

Captions measure 9.0pt. Figure 3's raw minimum remains 3.0pt because rotated glyphs
are measured by their transformed geometry; its authored ticks/legends/titles are
8.3pt and axis labels 9.3pt. Figures 1 and 2 remain below target: their regeneration
is stopped at the separately reported estimator-input gap; this commit substitutes
no operands or assets.

The regenerated PNG and its inclusion in the full-paper PDF were inspected. No
legend intersects the data, no axis label collides with ticks, and the panel titles,
energy-bin headings and caption remain separated and unclipped. The panel (b) y-axis
label and the single-line x-axis label are legible at the intended printed width.

## Validation

The original producer's numerical assertions pass, as does its exact frozen-array
comparison. make_values_fived16.py --check passes 3811 values, two source-figure checks
and ten listed-truth sentences. Both full-paper print proofs build successfully;
the after log has no overfull box, undefined reference or oversized float. No new
scientific computation was performed. Integration checks and standalone-note
synchronization remain with the paper integrator.
