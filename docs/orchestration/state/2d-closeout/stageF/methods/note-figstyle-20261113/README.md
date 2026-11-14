# The note's figures in the methods paper's style: group L (2026-11-13)

**By** director-helper-2, on the director's task 3 for #952. Joseph: the note's "plots don't look as good as the paper
and supplement".

**Under** the director's rulings of 2026-11-13. The plan is approved:
- one opt-in shared style, with a test that pins its values to the paper's;
- three arms per producer, with identity and data-diff checks;
- re-pins.

Group L (committed inputs, run locally at 0 node-h) has a go. Group R (the eleven 2D figures restyled on 2026-10-31)
gets a font-only pass. Group C (inputs on pscratch) waits for each script's go by sha, and for LL5D's atime-post.

**Scope:** layout and styling only. No plotted value, word or number changes, with one kind of exception: a label
string or tick label shown differently, each listed below. Every figure goes to Joseph in one before/after batch at
the end.

## The style

`note_print_style.py`, at the repo root, has no side effects on import:
- `apply()` sets `PRINT_RC`, which is the paper's rcParams (`docs/analysis-note/figures/methods_short/make_figures.py:287-289`
  on draft/methods-short-20261109 at a871379960f2) plus `font.serif = ["DejaVu Serif"]`. DejaVu Serif is the font the
  paper's "serif" resolves to in its committed PDFs.
- `figsize(width_frac, aspect)` sizes a canvas to its printed width in the note (6.5 in text width).
- `docs/analysis-note/test_note_print_style.py` checks the values: 4 tests, passing on matplotlib 3.11.2 and 3.10.1.

The module is separate from `technote_style.py` because importing that module turns every title into a no-op and
writes a PDF twin of each PNG. 56 scripts import it.

## The checks, per producer (`runs/CHECKS.txt`)

There are three arms:
- **before:** the base 96705540d, from a detached checkout;
- **off:** the new code without `--print-style`;
- **after:** the new code with it.

The interpreter is the matplotlib version each committed figure was made with: 3.11.2 for the gbdt figures and 3.10.8
for the landscape, both on Python 3.12, with `env -i` and an empty HOME. The checks:
- **Identity:** before and off reproduce the committed outputs. That proves the inputs and environment are the pinned
  ones.
- **Data files:** after's data files are byte-equal to the committed ones.
- **Drawn data:** `tools/capture_any.py` records each saved figure's data artists. It uses
  `fig-restyle-20261031/tools/artists.py` unchanged, imported from its committed path (sha256 `feb486fe…`). The full
  hash covers data, colours and line styles. `tools/compare_any.py` requires the multisets to be equal, before against
  after.
- **Collisions:** the capture also lists text-on-text collisions. Tick labels count only where drawn
  (`Axis._update_ticks()`).

| producer | figures | identity (before, off) | data | drawn data | printed text | text collisions, before → after |
|---|---|---|---|---|---|---|
| `nd-unfolding/gbdt_model_dependence/analyze.py --print-style` | gbdt_recovery, _bias_spread, _coverage, _prior_response | 14 of 14 files byte-equal, both arms (4 PDF, 4 SVG, 5 CSV, summary.json) | 5 CSV and summary.json byte-equal | equal, all four | 5.1–7.0 → 8.3–9.3 pt | 0→1, 0→0, 2→0, 0→0 |
| `3d-unfolding/plot_minerva_landscape.py --print-style` | minerva_unfolding_landscape | rasters (pdftoppm -r 100) pixel-equal, both arms | (inputs hard-coded in the script) | equal | 4.7–6.7 → 7.0–9.3 pt | 1→1 |

The remaining collisions are touching boxes, not overlapping text:
- **gbdt_recovery:** two legend entries, "q3 stress" and "W1 historical", touch by 31 px².
- **The landscape:** two legend columns touch by 8 px².

## The layout changes the printed size needed

At the printed width, the 8.5–9.3 pt text no longer fit the layouts drawn for 10.2 in and 9.4 in canvases. No string
changes. Under `--print-style` only:
- **All five figures:**
  - panel titles are at the body size (`axes.titlesize` = 8.5 pt);
  - each canvas is 6.5 in wide (0.97 × 6.5 in for the landscape), with its height set for the text.
- **gbdt_recovery:**
  - The identical per-column x label is set once, under the row (`supxlabel`).
  - The "100" tick label is left blank where it collided with "200". "200" stays, because Fig. 26's caption cites the
    iteration maxima.
- **gbdt_bias_spread:**
  - The identical x label is set once.
  - The log-axis minor ticks are at 2× and 5× per decade, because adjacent minor labels collided.
- **gbdt_prior_response:**
  - The identical x label is set once.
  - Each panel title wraps after its "; ".
- **gbdt_coverage:** the two panels are stacked, the heat map over the coverage panel, each at full width.
- **The landscape:** the legend is below the axes in three columns. At the printed size it covered the "this work"
  annotation.

The producers' suptitles stay. They are part of the figure, and removing text is not a style change.

## Installed and pinned

The five "after" PDFs are in `figs/`. `docs/analysis-note/make_figures.sh` installs them after the sync loop, by a
digest-checked copy (`install_printstyle_fig`):

| figure | sha256 |
|---|---|
| gbdt_recovery.pdf | `62bf4a83…` |
| gbdt_bias_spread.pdf | `f1786f48…` |
| gbdt_coverage.pdf | `422ef3f7…` |
| gbdt_prior_response.pdf | `44537431…` |
| minerva_unfolding_landscape.pdf | `bf1f14ea…` |

The landscape's `run` line gains `--print-style`.

**Left as they are:**
- **The gbdt package's own `results/`:** the package's default style stays its record.
- **`nd-unfolding/gbdt_model_dependence/build_evidence.json`:** it pins the old gbdt PDFs, but it is a dated build
  receipt. Its values.tex and test_build_all.py pins are already stale (`8bf48801` and `120bc43a` against today's
  `168d9b56` and `88ad1645`), and nothing reads it (`git grep build_evidence.json -- '*.py' '*.sh'`: none).
- **The archive `SOURCE-MANIFEST.tsv` files and `docs/ben-research-presentation/`:** both are historical.

## The rest of group L, not redrawn

- **fd_g_fig_modes** (`nd-unfolding/fd_g_figures.py`) and **paper_fig_coverage**
  (`docs/analysis-note/figures/methods_m3/fig_m3_coverage.py`) already use the article's style: make_figs.py's
  `style()`, serif with CM maths at 8 pt.
  - Each prints at 0.93 scale (about 7.4 pt).
  - fd_g_figures.py's plot model and readback controls (K0–K8) would make a resize a declared change of its own.
- **paper_fig2_joint** (`publication/release/figs/make_figs.py`) is already the article's style. Its input npz is
  written on Perlmutter by `export_fig_arrays.py` and is not committed, so it is not redrawn here.
- **paper_joint_nulls** (`docs/analysis-note/figures/plot_joint_null_distributions_physlabels.py`) reads the frozen
  `/pscratch/sd/j/josephrb/pub-release-20261006/frozen/inference_sufficient.npz` (receipt
  `docs/publication/release/RECEIPT-20261006-inference-sufficient-frozen.json`). That input is not committed, so it
  moves to group C.
- **nn_vs_gbdt_full:** its producer, `nd-unfolding/plot_nn_vs_gbdt_full.py`, which `make_figures.sh:55` names, is not
  in the repository (`git ls-files` finds no such file). The figure is left unchanged, with a follow-up row in
  ISSUES.md. The producer is not recreated (the director's ruling).
  <!-- absence-ok: the search is stated in the same sentence (git ls-files at the branch head) -->

## Group C, family 1 (2026-11-14): make_control_plots.py (Figs. 1 and 3) and plot_control_corner.py

**Method, the director's go of 2026-11-14:** one cluster read per family, then all styling locally.
- **The code, committed and gated first** (0f52ab2ab, 7d7b85522): each producer splits into fill (ROOT) and draw, with
  `--dump-arrays`, `--from-arrays` and `--print-style`, all opt-in.
- **Local identity test** (`tools/identity_family1.py` with `tools/fakeroot/ROOT.py`): synthetic inputs, a fake ROOT and
  stand-in edges. With no flag the producers draw PNGs byte-identical to those at 2cac548bd, and `--from-arrays` on
  their own dump draws byte-identical PNGs.

**The connects**, on a login node at 0 node-h, each by the director's go on its sha:
- **The presence check** (`tools/figc_presence.sh` fa6ae0f4, launcher a866065c; `runs/family1/connect-presence.session.txt`):
  - the fence passed;
  - no overlap, by path, realpath, the G2R prefix or device:inode, against the 1146 LL5D atime-pre paths (column sha256
    71bd8498, equal to the bulk 908d3922's by cov2d's check) and the 18 G2R inputs;
  - all 53 group C inputs present;
  - stat and realpath only.
- **family1** (`tools/figc_family1.sh` 2cc6be4f, launcher 071f3e2a; `runs/family1/connect-family1.session.txt`), 03:46:45–03:49:28Z:
  - the RUNNING marker for cov2d's fence;
  - a fresh clone at 0f52ab2ab;
  - env python 3.11.14, matplotlib 3.10.8 (the committed PDFs' version), numpy 1.26.4.

| arm | wall | CPU |
|---|---|---|
| ctrl-off | 26.8 s | 78.9 s |
| corner-off | 55.2 s | 90.7 s |
| ctrl-from | 5.5 s | 12.1 s |
| corner-from | 5.5 s | 12.1 s |

The fetched tar's sha256 is 01171756, equal to the cluster's.

**The dumps** (`runs/family1/dumps/`, force-added as deliberate receipt members):

| dump | size | sha256 |
|---|---|---|
| control_plots_arrays.npz | 17666 B | c1793d0f… |
| control_corner_arrays.npz | 19180 B | 5b44a80b… |

For all three figures, the from-arrays capture hashes equal off's (`runs/family1/cap-off/`, `cap-from/`), so each dump
holds every drawn value.

**Per figure:**
- **migration_resolution (Fig. 3): PASS.**
  - off is pixel-equal to the committed PDF (pdftoppm -r 100).
  - Print style from the dump: the plot axes' drawn data are bit-equal to off (57/57 items, `runs/family1/cap-after/`).
  - The five per-panel colour bars become one shared bar; that is the only change in the colour-bar axes.
  - The "diag median" annotations move above each map.
  - Printed text: 2.4–3.2 pt becomes 6.5–7.5 pt.
  - Installed, sha256 7ea7fd45.
- **control_corner: identity baseline accepted by the director's ruling (a).**
  - off differs from the committed PDF only in where the dataset tag sits, inside the top-left panel against above the
    figure.
  - Their printed text is identical, 56 lines with 0 sorted differences, including every r_MC and r_data value.
  - The tag moved with technote_style.py 1e7c28688 (2026-07-15, "fix plot header clipping"), after the committed
    corner (6749ddf8e, 2026-07-05). The producer and its input are unchanged since then; the input's mtime is
    2026-06-07.
  - Print style: drawn data bit-equal to off (67/67); the legend moves into the empty upper triangle.
  - Printed text: 3.0–4.1 pt becomes 6.5–8.3 pt.
  - Installed, sha256 09f29102.
- **control_plots (Fig. 1): PASS on the second identity try, by the director's ruling (c).**
  - The committed PDF (1b2925259, 2026-07-09, sha256 1191cc0c…) was drawn by code that was never committed: finer q3
    and W binning, with compressed catch bins.
  - Its binning and display were recovered from the PDF's vector paths (`tools/edges_from_pdf.py`, tolerance 0.001 data
    units) into `make_control_plots.py --extended-display` (7d7b85522).
  - **The extension connect** (`tools/figc_family1b.sh` 4e713548, launcher 02cc7f35;
    `runs/family1b/connect-family1b.session.txt`), 10:36:24–10:38:01Z on login34:
    - it ran after sacct showed LL5D 61255888 COMPLETED (2026-11-13 21:57:32–23:12:46 PST; `runs/family1b/sacct-61255888.txt`);
    - the fence passed, with no overlap against 1164 guard paths;
    - a fresh clone at 7d7b85522, with porcelain 0 before and after;
    - matplotlib 3.10.8;
    - ctrl-ext took 26.1 s wall and 86.2 s CPU; ctrl-ext-from took 5.4 s and 12.9 s. Their PNGs are byte-equal.
    - The tar's sha256 is 16e04848, and the fetched copy matches. The dump, `runs/family1b/dumps/control_plots_ext_arrays.npz`
      (22644 B, sha256 815e6c0a…), is force-added as a receipt member.
  - **The identity test** (`tools/identity_fig1.py`, `runs/family1b/identity/`) has four parts: the sorted words; every
    drawn path's vertices, by colour, to 0.02 pt; the catch bins and their "100" labels; and the pixels at 100 dpi.
    - **Controls:** the committed PDF against itself passes all four. Against family 1's off arm, which uses the
      analysis binning, it fails all four.
    - **Try 1** (the connect's PDF): FAIL. The binning (every path group's x extents), the ratio panels (0.00 pt) and the
      catch-bin labels matched. The spectrum panels' upper y limit differed: the committed headroom is 2.6 × the largest
      drawn value, not 2.2. One "10^6" tick label was missing as a result. The three "//" marks also differed in form.
    - **Try 2** (the director's go): the headroom and the mark's form were recovered from the committed PDF's tick
      positions and text spans. `EXT_YTOP = 2.6`, and the mark is `$/\!/$` at the tick size less 1 pt, both under
      `--extended-display` only. The redraw from the dump through the producer's CLI passes all four parts: 109 of 109
      words, 571 of 571 paths with Δ 0.0000 pt, and 0 differing pixels (also 0 at 300 dpi).
    - The local environment reproduces the connect's arm exactly (`try2-env-local-vs-cluster.txt`).
    - The PDF bytes still differ, because the mark is written earlier in the page's content stream. Its glyphs and
      coordinates are the same.
    - With no flag, the producers still draw byte-identical PNGs (`try2-noflag-family1.txt`, IDENTITY-FAMILY1 PASS).
  - **Print style** from the dump: Fig. 1's drawn data are hash-equal to the extended off arm (50 of 50,
    `runs/family1b/cap-off/`, `cap-after/`). Printed text goes from 4.8–7.6 pt to 7.3–9.3 pt (0.99 of the text width).
    - The capture lists three text overlaps. All three involve the legend cell's tick labels, and that axis is turned off
      (`ax_leg.axis("off")`), so none is drawn.
    - Installed, sha256 59aab046 (d4c7494f8). Then, at the director's request after his review of p. 12, the last resolved
      tick label before the catch bin is left blank on the q3 and W panels ("10" and "5"), under `--print-style` only.
      At the printed size those labels ran into the catch bin's "100" ("10100"). The ticks stay. The drawn data are
      still hash-equal to the off arm (50 of 50, `runs/family1b/cap-after-ticks/`). Installed, sha256 dcea96fa.

## CITABLE FOR / NOT CITABLE FOR

**CITABLE FOR:**
- that the five redrawn figures plot the committed figures' data, colours and line styles bit for bit (drawn-data
  hashes);
- that their data files are byte-equal;
- each figure's printed text size;
- the install pins.

**NOT CITABLE FOR:** any value, caption or reading; any figure not listed above; Joseph's approval of the look, which
comes in the end-of-task batch.
