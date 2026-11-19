# The note's figure pass (cov2d, from 2026-11-19)

**Requested by** the director on 2026-11-19, from director-helper-3's deterministic quality counts
(`~/codex-reports/note-measurement/quality/deterministic-1acece939.md`) and the figure plumbing
(`~/codex-reports/note-measurement/figure-plumbing.md`).
- **Base:** origin/draft/note-round2-20261108 at `c3b4e8842`.
- **Scope:** presentation only. No datum, number or colour changes. A caption changes only where it names a panel's position.
- **Earlier records:** `note-figstyle-20261113/` and `note-figstyle-20261117/` stay unchanged; their `figs/` files are immutable. This record reuses their tools and dumps from their committed paths.

**Status:** in progress.

| chunk | figures | state |
|---|---|---|
| A1 | 17 (fig:eavail-marg), 23 (fig:q3excess) | Fig. 23 drawn again at its printed size; Fig. 17 split into its two panels at full width (LaTeX only) |
| A2 | width classes; text under 7 pt | to do |
| B | the duplicates (Figs. 7, 9, 10, 13; 20, 21), by Joseph's ruling of 2026-11-19 | to do |

## The method (two arms per redrawn figure)

- **Arm 0** runs the unchanged producer under the palette pass's `note-figstyle-20261117/tools/palette_run.py`, the
  recipe that drew the installed file. It must reproduce that file at the base:
  - byte-equal apart from the PDF creation date (`bytes_but_date.py`);
  - pixel-equal at 300 DPI (`raster.py`).
- **Arm 1** runs the same producer under `tools/layout_run.py`. This applies the same palette edits, then
  `tools/layout_lib.py`'s layout edits, once per figure, before its first save. Not one producer byte changes.
- **The layout edits** come from this record's tables:
  - **ticks frozen:** every axis keeps the major ticks and tick labels it drew;
  - **`layout.tsv`:** the canvas at its printed size, with every text size times a scale and raised to a floor;
  - **`ticks.tsv`:** a tick-label rotation;
  - **`boxes.tsv`:** each axes placed in a box, in inches. Without boxes, the figure gets `tight_layout()`.
- **The checks** (`tools/arms_layout.sh`, written to `runs/<family>/CHECKS.txt`):
  - arm 1 against arm 0 passes fig-restyle-20261031's `compare.py` with no restyle tables, so every data item's full hash must be equal: data, colours and line styles;
  - the multiset of drawn strings must be equal;
  - per arm: the canvas size, the smallest and median font size, and the text overlaps (capture_any.py's measure).
- **Install:** `tools/install_layout.py` copies an arm-1 PDF to `figs/` and the note. It comments out the old install
  line and adds an `install_layout_fig` line to make_figures.sh's "note-figpass-20261119" block.

## Chunk A1

### Fig. 23 (fig:q3excess), redrawn

- **Recipe:** `nd-unfolding/q3_excess_projection.py --from-arrays note-figstyle-20261113/runs/family5/dumps/q3_arrays.npz --print-style`.
  - It runs under matplotlib 3.10.8 (`figenv/mpl3108`), with the 11-13 fake-ROOT stand-in, as the palette pass did.
- **The new layout:** a 6.5 × 5.0 in canvas, printed at \textwidth, which is scale 1.0.
  - The ratio map is on its own row. Its column labels are horizontal, and its in-cell values are at 7 pt (5.5 pt before).
  - The q3 and E_avail marginals are on the row below, with horizontal tick labels.
  - Every text is at least 7 pt (floor 7.0, scale 1.0).
- **Checks** (`runs/q3/CHECKS.txt`):
  - arm 0 is EQUAL-BUT-DATE and 0 px against the installed file;
  - COMPARE :: PASS (7 data artists);
  - the 87 drawn strings are equal;
  - text overlaps go from 29 to 0 in the capture.
  - In the note PDF, quality_checks' overlapping strings for Fig. 23 go from 50 to 0.
- **Caption:** the panel positions change from "left / center / right" to "top / lower left / lower right". That
  sentence is the chunk's one caption hunk (one Grok read).

### Fig. 17 (fig:eavail-marg), LaTeX only

- **Why not redrawn:** its producer (`compare_to_paper_fullcov.py`) reads config (a)'s
  `3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root`, which is only on pscratch.
- **The layout:** the installed 864 × 360 pt canvas is split by `\includegraphics` trim into its two panels:
  - the grid panel, kept from x = 5 to 430 pt;
  - the distribution panel, kept from x = 430 to 858 pt.
- **How it prints:** each panel prints at scale 1.0 (it was 0.38). The distribution panel follows on the next page, in
  a continuation float that reads "Figure 17: continued, the per-bin differences in distribution." The figure keeps
  one number and one label.
- **Measured in the note PDF** (quality_checks):
  - the smallest word-like text is 8.0 pt (3.0 before), and the median is 10.0 pt (3.8 before);
  - the superscripts ("21" in 10²¹ POT) are 5.6 pt (2.1 before).
  - **Below 7 pt pending a producer re-render:** the superscripts.
- **freeze_checks' font check** allows a sans-serif font only on the pages of four named figures, Fig. 17 among them.
  It now also allows the page after fig:eavail-marg's label (`SANS_CONTINUED`), where the continuation prints.
- **The re-render's input fetch** is prepared but not run:
  - script: `~/cov2d-work/figfetch/fetch-3d-a.sh`, a read-only O_NOATIME copy of the one file;
  - pin: `0dd94830821576a3b060fae2d4a20564610c535ed06046cd1eb05cd11885dd59`
    (re1/RE1-AMENDMENT-DECLARATION.md:151; re1/run2/launch/re1_f_env.sh:2).
  - It waits for the director's go.

## Gates for chunk A1

- **Build:** rc 0, with 0 undefined references.
- **freeze_checks** (checks 1, 3, 5 and 7, base PDF at c3b4e8842, with an empty allow-list) passes:
  - the numbers diff finds 5565 tokens in each build, with 0 unexplained;
  - labels, fonts and accents pass.
- **quality_checks:**
  - figures with overlapping strings go from 4 to 3;
  - figures with a 10th-percentile text size under 7 pt go from 26 to 24, and those with a median under 7 pt from 18 to 17;
  - distinct printed widths go from 12 to 13, because Fig. 17's panels are new widths (chunk A2 sets the classes);
  - for Figs. 17 and 23, see above;
  - the count of figures with any text under 7 pt stays at 32, because the sub- and superscripts of both figures remain under 7 pt.
