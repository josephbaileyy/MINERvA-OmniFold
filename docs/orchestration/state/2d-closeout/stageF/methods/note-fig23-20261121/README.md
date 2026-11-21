# Figs. 2 and 3: the lower panels as OmniFold / published, and the inset relabeled

Joseph accepted two of codex2's rating suggestions (relayed by the director, 2026-11-21):
- **Fig. 2 (fig:xsec):** the lower panels show OmniFold / published MINERvA, and the upper panels keep the prior curves.
- **Fig. 3 (fig:pull):** the inset's "χ²/ndf paper" reads "descriptive distance per bin", with the value kept.

The work runs on the cov2d check branch off rewrite/journal-voice-20261121 (ec2aac4fd, then bc3580a94).

## Fig. 2 (`tools/compose_fig2_pubratio.py`)

- **The recipe.** The installed Fig. 2 is note-figfix-20261120's recipe: compose_tier2.py, with compose_fig2_edges.py
  wrapping its save so the published prediction steps on the projection edges.
  - This tool runs exactly that recipe, with one more wrapper under compose_fig2_edges's own, so the edge fix is made
    first.
  - Inputs: the read-only fetch of 2026-11-17 (xsec.root a5c13fc3, cov_ptpl_minerva_inclusive_6GeV.root 6c6dce72).
  - Environment: figenv/rootmpl3108.
- **The lower panel.** Its points are recomputed in place.
  - Each point is f_i / p_i: the OmniFold point of the upper panel over the published point drawn there.
  - The vertical bars are the OmniFold bars over p_i (finite weighted-sample statistics only).
  - The horizontal bars, markers and caps are kept.
- **The reference line** takes the published points' colour. It had used the prior's colour, which named the old
  denominator.
- **The label** "This work / prior" reads "This work / published".
- **The y range** is the smallest symmetric range about 1, in steps of 0.05, that holds every point and bar with a
  0.02 margin. That gives 0.9 to 1.1, with ticks at 0.95, 1.00 and 1.05, so no tick sits at the joint.
  - The producer's (0.7, 1.3) had flattened a few-percent ratio onto the reference line.
- **The upper panel's y label** moves up 3–4 px, so it does not meet the longer lower label, which overruns the short
  panel. Its x is unchanged, and it is a text position only.
- **Checks**, any of which stops the run:
  - the points sit at the bin centres;
  - the old lower points equal f / prior on the bins (to 1e-12);
  - the new points equal f / p exactly;
  - the upper panel's artists are unchanged;
  - the edge check passes on both panels. It applies note-stepedges-20261121's edges.py rules, made errorbar-aware:
    points at the centres, x half-widths equal to the half bin widths, x caps on the edges;
  - the labels neither overlap nor leave the canvas.

### Checks (`runs/fig2/CHECKS.txt`; `bash tools/run_fig23.sh <worktree> <base>`, then INSTALL=1)

- **Arm 0** (the figfix recipe) against the installed proj_pt and proj_pz: both EQUAL-BUT-DATE.
- **Arm 1 against arm 0**, for each figure in PDF and PNG:
  - all 18 items are in the same order;
  - the upper panel differs in nothing;
  - in the lower panel, 7 items carry new data (the ratio points, bars and caps), and the reference line differs in
    colour only;
  - the strings differ only in the lower label and the lower ticks.
- **Text overlaps:** 0 in the PDFs; the PNG count does not increase.
- **Values** (`runs/fig2/compose_fig2_pubratio.json`, per bin: edges, f, its bar, p, prior, the old ratio and the new
  one):
  - the ratio is f/p exactly;
  - p_T runs 0.968 to 1.037; p∥ runs 0.935 to 1.061.

### The new lower panels, for the §3.1 text (from the run record)

- **p_T:**
  - [0, 0.07) gives 0.968 ± 0.005, and [0.07, 0.15) gives 0.986 ± 0.003;
  - 1.002 to 1.019 from 0.15 to 1.5 GeV/c;
  - [1.5, 2.5) gives 1.025 ± 0.002, and [2.5, 4.5) gives 1.037 ± 0.005.
- **p∥:**
  - 0.999 to 1.018 from 1.5 to 20 GeV/c;
  - [20, 40) gives 1.061 ± 0.002, and [40, 60) gives 0.935 ± 0.006.
- The ± values are the OmniFold weight statistics over p. The published uncertainties are not drawn.

## Fig. 3 (`tools/compose_fig3_inset.py`)

- **The recipe.** The installed Fig. 3 is note-figstyle-20261117's pull_full arm 1: compare_to_paper_fullcov.py under
  remap_anc.py and palette_run.py, with --sd-label. This tool runs that chain and then edits the inset text.
  - "$\chi^2$/ndf paper = " becomes "descriptive distance" and, on a new line, "per bin = ". On one line the label is
    wider than the histogram panel.
  - The value 2.27 is unchanged.
- **The histogram's y range** is raised from (0, 55.44) to (0, 59.91), so the tallest bar (33) stays 6% of the panel
  below the taller inset frame. The bars are unchanged.

### Checks (`runs/fig3/CHECKS.txt`)

- **Arm 0** against the installed MEFHC_5iter_pull_full.pdf: EQUAL-BUT-DATE.
- **Arm 1 against arm 0:**
  - all 35 data items are equal (full hashes);
  - the strings differ only in the inset, with the value kept;
  - the canvas is unchanged at 4.55 × 2.3 in, and the page at 327.6 × 165.6 pt, as make_figures.sh asserts;
  - text overlaps are 0 → 0 in the PDF.
- **Record:** `runs/fig3/compose_fig3_inset.json`.

## Not changed

docs/analysis-note/make_figures.sh pins these PDFs at shas that were already stale before this record: the Fig. 2
pins predate note-figfix-20261120. The build does not run that script, and this record leaves it as found.
