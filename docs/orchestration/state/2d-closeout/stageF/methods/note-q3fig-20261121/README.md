# Fig. 5 (fig:q3excess): label colours and the lower panels' y label

Joseph's figure job, relayed by the director on 2026-11-21, on the draft at d9fba038e:
- **(a)** The ratio map's in-cell labels were black on every cell, so they vanished on the darkest blues (0.66) and reds
  (1.26). Each label now takes the colour that reads on its cell, white on dark and black on light. The colour scale
  is unchanged.
- **(b)** The lower panels' y axis read "unfolded / GENIE prior", while the caption names the comparator the MINERvA
  Tune v1 prior. It is the same prior (GENIE 2.12.6 + Tune v1, the producer's weights `w_truth`), so the axis now reads
  "unfolded / Tune v1 prior".

## The recipe

The installed file was note-figpass-20261119's arm 1 (its `runs/q3/CHECKS.txt`):
- the unchanged producer `nd-unfolding/q3_excess_projection.py --from-arrays note-figstyle-20261113/runs/family5/dumps/q3_arrays.npz --print-style`;
- run under `note-figpass-20261119/tools/layout_run.py` (palette_lib, then layout_lib) in `figenv/mpl3108`, with the
  11-13 fake-ROOT stand-in.

`tools/compose_q3_labels.py` runs the same recipe, then makes the two fixes before anything is written:
- **(a)** For each label, the cell's colour comes from the drawn image's own colormap and norm. The label is white when
  white has the higher WCAG contrast against the cell's relative luminance L, that is when 1.05/(L+0.05) > (L+0.05)/0.05
  (the crossover is L = 0.1791). Otherwise it is black.
  - The usual matplotlib annotated-heatmap rule thresholds the norm value. That fails on a diverging map, where both
    ends are dark, so the luminance is used instead.
- **(b)** The y labels of axes 1 and 2, the only two texts reading "unfolded / GENIE prior", are set to the new string.

The tool stops the run on any failure of these checks:
- each label sits on one cell centre and prints that cell's value to 2 decimals;
- there is one label per finite cell, and every label was black before the fix;
- after the fix, the image's array, colormap and norm limits are unchanged, and so is every text's string, position
  and size, apart from (b)'s two strings;
- only map labels change colour, and the number that do equals the number set white.

The per-cell record (value, cell RGB, luminance, label colour) is `runs/q3/compose_q3_labels.json`.

## The checks (`runs/q3/CHECKS.txt`, `bash tools/run_q3.sh <worktree> d9fba038e`, then INSTALL=1)

- **Arm 0** is the installed recipe. Against docs/analysis-note/figures/q3_excess_projection.pdf at d9fba038e it is
  EQUAL-BUT-DATE and 0 differing pixels at 300 DPI.
- **Arm 1 against arm 0, data artists:** fig-restyle compare.py gives "equal" for all 7 data artists (full hashes:
  data, colours, styles), COMPARE :: PASS. The ratio values, the colour scale and the marginals are unchanged.
- **Drawn strings:** all 87 strings are equal after arm 0's two "unfolded / GENIE prior" become "unfolded / Tune v1
  prior". The canvas is 6.5 × 5.0 in, with a smallest font of 7.0 pt. The PDF has 0 text overlaps in both arms.
- **Labels:** 34 labels, one per finite cell, with 15 white and 19 black.
  - White: 0.66, 0.66, 0.71 and the reds from 1.17 to 1.26.
  - Black values span 0.81 to 1.17.
  - White labels are on L ≤ 0.1787 and black on L ≥ 0.1908.
  - The two cells printed "1.17" sit on either side of the crossover, so one label is white and the other black. At
    that luminance both colours give about the same contrast.
- **Installed:** docs/analysis-note/figures/q3_excess_projection.pdf is arm 1's PDF, with sha256 57130b95… (CHECKS.txt
  gives the full digest).

## Caption

The caption's parenthetical "(labeled ``unfolded / GENIE prior'')" names the old axis text, so it now reads
"unfolded / Tune v1 prior". This is a separate commit, so it can be dropped if the rewrite owns that sentence.

## Seen, not changed

The lower panels draw `step(..., where="mid")` over bin indices, and each tick is labelled with its bin's low edge
("$q_3$, low edge (GeV)"). Each tick therefore sits at the centre of its bin's flat segment, not at the segment's left
end, and the first and last bins are drawn at half width. This is reported to the director, not changed here.
