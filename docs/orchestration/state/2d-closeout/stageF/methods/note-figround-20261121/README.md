# Figure round, 2026-11-21: Figs. 2 and 3, and the exposure stamp on every figure

Joseph's suggestions, relayed by the director with "use your judgment", on rewrite/journal-voice-20261121 at 17fa81452.

## Fig. 3 (fig:pull, `tools/compose_fig3_round.py`)

It runs the chain that drew the installed figure: note-figstyle-20261117's pull_full arm 1, under which
note-fig23-20261121 relabeled the inset. This tool replaces that relabel with these changes:
- **Inset removed.** It covered the top of the histogram and the zero line. Its mean and SD repeat the caption, and
  the distance per bin, 2.27, is printed in §3.1 (`\chiPaper`).
- **Stamp removed.**
- **Text sizes.** Every text is scaled by 0.70. At \textwidth (scale 1.43), labels print at 8.5 pt and tick labels at
  7.9 pt, where they had printed at about 12 and 11 pt. The colour bar's ticks are set after its rebuild.
- **Bars.** Thin white edges (0.4 pt) in place of 1 pt black ones.
- **Map colour scale.** (−5, 5) becomes (−3, 3), with the colour bar. The map spans −2.57 to 1.91, so nothing
  saturates (checked).
- **Histogram top.** 1.6 × the tallest bar (headroom kept for the inset) becomes 1.15 × (33 → 37.95).

The canvas and page are unchanged at 4.55 × 2.3 in and 327.6 × 165.6 pt, the size the paper's crop in make_figures.sh
asserts.

**Checks** (`runs/fig3/CHECKS.txt`):
- Arm 0 (the installed recipe) is EQUAL-BUT-DATE against the installed file.
- Arm 1, PDF and PNG:
  - all 35 items are in the same order;
  - the bars differ in style only (geometry equal);
  - the image differs in its colour limits only (array equal), and the colour bar with them;
  - no other data changes;
  - the words removed are exactly the inset and the stamp;
  - tick labels follow the new ranges;
  - PDF text overlaps are 0 → 0.

**Caption.** "The inset gives the descriptive quadratic distance…" is dropped.

## Fig. 2 (fig:xsec, `tools/compose_fig2_round.py`)

It runs the installed recipe, note-fig23-20261121's compose_fig2_pubratio.py (figfix's edge fix, then the
OmniFold / published lower panels), and then makes these changes:
- **Stamp removed.**
- **One legend.** The p_T panel's legend is removed. The p∥ panel's stays at its upper right, above the tail, and covers
  no plotted point, bar or histogram vertex (checked).
- **Text sizes.** Set for print at 0.49 \textwidth on the saved, tight-cropped page:
  - p_T: labels 8.4 pt, ticks 7.9 pt;
  - p∥: labels 8.2 pt, ticks 7.7 pt;
  - the tick labels had printed at about 5.9 pt.
- **Lower label.** "This work / published" goes on two lines in both panels, with 3 pt more pad. At the new size, on one
  line it meets the upper label. The upper label moves 2.75 px up in p_T, where the two still met.

**Checks** (`runs/fig2/CHECKS.txt`):
- Arm 0 is EQUAL-BUT-DATE against both installed files.
- Arm 1: every data item is equal (full hashes). The words removed are the stamp and, in p_T, the four legend entries.
  The p_T tick labels change with the size: integer ticks.
- **Overlaps.** The tool's own check, at its final draw, stops the run on any text overlap.
- **The capture's PDF count** (0 → 3) is reported, not used as a gate:
  - after a PDF save, it measures the y labels, which the PDF renderer placed, with the screen renderer's metrics;
  - so it puts the two-line lower label on the tick labels;
  - in the file itself, that label ends 5.6 pt left of the ticks (pdftotext, in CHECKS.txt).
  - A 400 dpi render of the left edge shows the label whole and clear.
- **The PNG counts** are the same misreading, and the installed figure had it too: the label on the ticks at 60 px²
  before, 20 now.

## The stamp on the other ten figures (`tools/strip_stamp.py`, figenv/pdfedit: pikepdf 9.4.2)

Thirteen figures printed "MINERvA ME FHC, 1.06×10^21 POT". Two are redrawn above (Fig. 2's two files and Fig. 3). On
the other ten the stamp is removed from the installed PDF:
- the figures: q3_excess_projection, nn_vs_gbdt_full, mode_decomp_mec_eavail_central, both paper slice figures,
  generators_vs_unfolded_band_central, eavailW_band, eavail_marginal_vs_paper_pull_full, control_plots and
  control_corner;
- nn_vs_gbdt_full has no producer in the tree;
- a deletion this small needs no producer run again.

How the tool works: it removes each text object whose glyph origins all lie inside the stamp's box (from pdftotext).

**Checks:**
- the words after are the words before minus the stamp, each at the same box to 0.1 pt;
- at 200 dpi, no pixel changes outside the stamp box (enlarged by 2 pt);
- the page size is unchanged.

Per-figure records are in `runs/stamp/*.json`. **No included figure still prints the stamp** (`runs/stamp/CHECKS.txt`).

## fig:ptslices caption (journal-editor's routing of codex2's App. C read)

The caption is restored to the original's meaning (sec_results.tex:111 at e89694209): the OmniFold bars alone enter the
panel χ²/n, and they are neither the data's statistical uncertainty nor the reported covariance.
