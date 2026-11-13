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

## CITABLE FOR / NOT CITABLE FOR

**CITABLE FOR:**
- that the five redrawn figures plot the committed figures' data, colours and line styles bit for bit (drawn-data
  hashes);
- that their data files are byte-equal;
- each figure's printed text size;
- the install pins.

**NOT CITABLE FOR:** any value, caption or reading; any figure not listed above; Joseph's approval of the look, which
comes in the end-of-task batch.
