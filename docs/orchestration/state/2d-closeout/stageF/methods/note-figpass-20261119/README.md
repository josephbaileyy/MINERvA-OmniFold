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
| A2 | width classes; text under 7 pt | three width classes in LaTeX; Figs. 33, 36 drawn again at printed size; Figs. 26, 27 with larger fonts |
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
  - **The Grok read** (`~/codex-reports/note-measurement/reads/figpass-A1/grok/report.md`) passed the caption and
    Fig. 17. It found two unchanged body sentences in sec_3d that still named Fig. 23's old panels.
  - **The fix:** those pointers now read top, lower left and lower right (commit ed1dcb2f9).
  - **The re-read** (`reads/figpass-A1-r2/grok/report.md`) passed.

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

## Chunk A2: width classes and text under 7 pt

### Width classes (LaTeX only)

Every figure outside chunk B is printed at one of three widths:

| class | width | figures |
|---|---|---|
| full | `\textwidth` | 1, 2, 3, 12, 14, 15, 17 (both panels), 18, 19, 22, 23, 25, and the ones already there (26–36 except 35) |
| single | `0.7\textwidth` | 6, 8, 16, 24, 35 |
| two-panel / tall | `0.49\textwidth` per panel | 4, 5, 11 (pairs) |

- **What changed:**
  - 0.99, 0.97, 0.95, 0.92, 0.90 and 0.85 became full;
  - 0.62, 0.66 and 0.55 became single;
  - Fig. 24 (fig:eavailWexcess, a tall two-row figure) moves up to single (0.7), not down to 0.49, so its words print at 8 pt.
- **Not yet:** the figures of chunk B (7, 9, 10, 13, 20, 21) keep their widths until B re-lays them out.
- **Fig. 17:** both panels are at `\textwidth` (scale about 1.1).
- **Distinct printed widths** go from 13 (12 at the base) to 5: the three classes plus 0.62 and 0.85, both in chunk B.

### Figures drawn again with a 7 pt floor

Each is drawn at its printed size with `layout.tsv` (scale 1.0, floor 7 pt) and `boxes.tsv`.

- **Fig. 33 (fig:coverage-5d-paper, `m3_fig3_coverage`):**
  - recipe `docs/analysis-note/figures/methods_m3/fig_m3_coverage.py --repo <wt> --outdir <dir>`, under the laptop's base conda (matplotlib 3.10.1), the recipe of the installed file;
  - `ARM0=plain`, because the palette pass made no edit;
  - arm 0 is EQUAL (byte for byte) and 0 px against the installed file;
  - 12 data artists equal, 29 strings equal;
  - every font is at least 7.0 pt (5.8 before, median 6.4).
- **Fig. 36 (fig:bkg-residual-note, `m3_fig1_background`):**
  - same recipe, with arm 0 under the palette pass's text fix; arm 0 is EQUAL and 0 px against the installed file (figs-r2);
  - 17 data artists equal, 90 strings equal;
  - every font is at least 7.0 pt (5.5 before);
  - panel (a) is taller, so its title clears the E_avail bin labels (both are placed in axes fractions).
- **The overlap counts:** capture_any.py's legend overlaps in arm 1 come from that measure, not the figure. They do not show on the page, and quality_checks finds 0 overlapping strings in both figures in the note PDF.

### Figs. 26 and 27: cov2d's own producers, larger fonts

- **Why copies:** the originals in note-newfigs-20261118 are immutable MANIFEST rows. So `tools/make_fig_fived16_headline.py` and `tools/make_fig_runperiod_steps.py` are copies that change only:
  - the explicit font sizes: 7.4 to 7.6 pt, which were 6.6 to 7.2;
  - panel (b)'s lower y limit in Fig. 27, so its larger panel label clears the 1B bar;
  - the repository root depth and the default output (`figs-src/`, not committed).
- **What stays:** every input pin, check and identity assertion. Their `*_values.json` are byte-identical to the originals'.
- **The PDFs** carry no creation date (`97766f5c`, `4496bcf8`).
- **sec_fived16.tex's comments** naming the installed digests are updated; they do not print.

### Not changed, and why

| figure | under 7 pt | why not here |
|---|---|---|
| 1, 3, 15, 16, 19, 22–25, 30 | sub- and superscripts only (math text at 70 % of an 8–8.5 pt font) | a floor cannot lift them without enlarging every font; the width class already scales them up where it widens |
| 2 (fig:control-corner) | the r_MC / r_data subscripts | the same; a redraw at full width spread the corner grid apart for no gain |
| 6, 11, 12, 14 (tier 2) | tick labels at 5.5–6.1 pt (restyle_2026_10's sizes) | a local re-render is possible (inputs fetched on 2026-11-17, ROOT environment), but it is not cheap; candidates for a follow-up chunk |
| 18 (fig:calibration) | 3.2–4.0 pt | no producer (ISSUES.md:1292; the director ruled it is not recreated) |
| 28 (fig:fived16-modes) | 4.1–5.4 pt | pinned in make_values_fived16.py FIGURES; a redraw needs a new sidecar with K0–K8 passed |
| 34 (fig:joint5d-nulls) | legend at 6.0 pt | arm 0 does not reproduce the installed file on this laptop (90086 px differ; the arm64 / x86_64 draw difference recorded in note-figstyle-20261113's CHECKS-families3to6.txt) |
| 17 superscripts | 6.1 pt | the producer re-render (its own chunk; the input was fetched on 2026-11-19) |
| 7, 9, 10, 13, 20, 21 | — | chunk B |

### Gates for chunk A2

Base: the A1 build at ed1dcb2f9.

- **Build:** rc 0, with 0 undefined references.
- **freeze_checks** (checks 1, 3, 5 and 7, empty allow-list) passes:
  - the numbers diff finds 5540 tokens in each build, with 0 unexplained;
  - labels, fonts and accents pass.
- **quality_checks:**
  - figures with a 10th-percentile text size under 7 pt: 24 → 17;
  - figures with a median under 7 pt: 17 → 12;
  - distinct printed widths: 13 → 5;
  - figures with overlapping strings: 3, all unchanged here (Figs. 9 and 10 are chunk B; Fig. 27's one is the t̄ bar over its t);
  - figures with any text under 7 pt: 32, all from sub- and superscripts, with Fig. 18 and the chunk B and tier-2 figures as above.

