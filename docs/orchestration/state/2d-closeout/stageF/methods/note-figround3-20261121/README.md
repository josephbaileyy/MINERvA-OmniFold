# Figure round 3, 2026-11-21: Figs. 2 and 3

Joseph and the rewrite helper approved this round (relayed by the director), on rewrite/journal-voice-20261121 at
177c549c2. Each tool runs the installed recipe (note-figround-20261121's) with one more wrapper under it.

## Fig. 3 (fig:pull, `tools/compose_fig3_r3.py`)

- **Histogram x axis.** It runs −3 to +3, symmetric about 0 like the map's ±3 colour scale. The bars span −2.70 to 1.95,
  so nothing is clipped (checked).
- **Crop.** The file is saved cropped to its drawn content (bbox_inches "tight", pad 0.02 in).
  - The 4.55 × 2.3 in canvas had left about an inch of empty space below the panels.
  - The page goes from 327.6 × 165.6 pt to 292.9 × 130.0 pt.
  - At \textwidth the panels print about 11% larger, and the figure takes less height.
- **Text.** Rescaled for the new printed scale, 1.59, so labels still print at 8.5 pt and ticks at 7.9 pt.
- **Checks** (`runs/fig3/CHECKS.txt`):
  - arm 0 (round 2's recipe) is EQUAL-BUT-DATE against the installed file;
  - arm 1 has all 35 data items equal (full hashes) and no word changed;
  - PDF overlaps are 0.
- **The paper's crop.** make_figures.sh asserts the old 327.6 × 165.6 page before its pdfcrop of the left panel
  (paper_validation_residual.pdf). No .tex file includes that crop, the committed crop is unchanged, and the build does
  not run make_figures.sh. The assertion is left for the structural rewiring at the end.

## Fig. 2 (fig:xsec, `tools/compose_fig2_r3.py`)

- **Published prediction.** It is drawn black dashed above the blue solid prior, as before the restyle, where it had
  been blue dashed. Its data, dashes and width are unchanged.
- **Legend** (p∥ panel only). "Tune v1: our simulation (the prior)" reads "Tune v1 prior (this work)", and "Tune v1:
  published prediction" reads "Tune v1 published prediction". The legend is rebuilt in place, so its handles show the
  new colour, and it covers no plotted vertex (checked).
- **Checks** (`runs/fig2/CHECKS.txt`):
  - arm 0 (round 2's recipe) is EQUAL-BUT-DATE against both installed files;
  - arm 1's data are equal with colours left out, and only the published-prediction line differs (colour);
  - the strings equal arm 0's apart from the two renames;
  - the tool's overlap check at its final draw passes;
  - the lower label ends 5.6 pt left of the lower tick labels in the PDF.
- **The capture's overlap counts** (unchanged from round 2) misread the auto-placed y labels, as round 2's README
  explains.
- **Caption.** The approved wording, "…the unfolding prior and the published prediction, respectively, which nearly
  coincide." Register n31's clause is unchanged.
