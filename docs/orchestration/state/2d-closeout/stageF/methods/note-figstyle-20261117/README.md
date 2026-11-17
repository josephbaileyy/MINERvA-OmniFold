# The note's figure palette pass (cov2d, from 2026-11-17)

**Under** COMBINED-PLAN.md sections 5 and 7 (note-measurement). Joseph approved the plan and its palette on 2026-11-17,
and the director assigned this pass to cov2d.
- **The palette:** the paper's colours, `#CC79A7` for GENIE CV, and this work in red in every figure.
- **Base:** origin/draft/note-round2-20261108 at `2fe070fec`.
- **The earlier record stays unchanged:** `note-figstyle-20261113/`, whose `figs/` files are immutable. Its tools and
  pickles are reused from their committed paths.

**Status:** in progress.

| family | figures | state |
|---|---|---|
| 4 | 19, 20, 21, 22 | installed |
| band, q3, spec, ctrl | 25, 23, 16, 1 | installed |
| stat | 5 | unchanged (the director's ruling: the palette changes nothing, and its label stays) |
| gbdt | 26–29 | installed |
| cov5d, bkg5d | 30, 34 | pinned: the palette changes nothing; install lines added |
| tier 1b | 31 | to do |
| tier 2 | 8, 7, 9–10, 6, 11–14 | to do (the inputs were fetched on 2026-11-17) |

## The palette and its rules

- **`note_palette.py`** (repo root) names one colour, line style and marker per identity, with exact-key lookup only.
  It has no side effects, and the fonts and sizes stay in `note_print_style.PRINT_RC`.
- **`docs/analysis-note/test_note_palette.py`** holds the rules:
  - a CIE76 ΔE of at least 14 between the seven line colours, in normal vision and in simulated protanopia,
    deuteranopia and tritanopia (Machado 2009). The smallest values are 20.6, 20.0, 16.6 and 14.9, the plan's
    figures;
  - a unique style per identity;
  - the paper hexes are those of `publication/release/figs/make_figs.py`;
  - only exact keys resolve;
  - importing the module has no effect.
- **This record's tables:**
  - `palette.tsv` is `note_palette.palette_table()`, generated from it;
  - `recolour.tsv` maps each figure's installed colours to an identity, with the producer lines that set them;
  - `styles.tsv` and `restyle.tsv` give the one marker change: GENIE CV's points become down-triangles in Fig. 19, so
    they no longer share this work's circle.

## The method (two arms per figure)

- **Arm 0** redraws in the installed style and must reproduce the installed file:
  - byte-equal apart from the PDF creation date (`tools/bytes_but_date.py`, which masks only `/CreationDate (D:…)`
    and fails on any other differing byte);
  - pixel-equal at 300 DPI (fig-restyle-20261031's `raster.py`).
- **Arm 1** draws in the note palette. Its captured data artists must equal arm 0's on the colour- and style-free
  hash, and each colour and line style must be exactly what the tables map. That check is fig-restyle-20261031's
  `compare.py --recolour --palette --styles --restyle`, unchanged.
- **The edits:** `tools/palette_lib.py` makes every edit the tables declare, and nothing else.
  - **Tables:** `recolour.tsv`; `restyle.tsv` with `styles.tsv`; `hatches.tsv`; and `text_fixes.tsv`, whose
    figure-specific text replacements must each be found; and `drop_titles.tsv`.
  - **Text:** the note's notation (E_{\rm avail}, p_∥).
  - **Legends:** frameless. One is rebuilt from its artists where every entry has one; otherwise its own keys are
    recoloured in place. A rebuilt legend keeps its anchor and transform, and an entry lost anywhere stops the run.
  - **Power of ten:** the y axis's power of ten goes into its label. The label is tried on two lines, then on one,
    and kept only if it fits the canvas; otherwise the factor stays as a math-text ×10ⁿ.
- **Recipes:**
  - `tools/palette_run.py` runs an unchanged producer and applies the edits once per figure, before its first save.
  - `tools/palette_family4.py` does the same on the family-4 pickles.
  - Not one producer byte changes.
- **Running the arms:** `tools/arms.sh` runs both arms of one figure and its checks: bytes_but_date, raster, compare,
  and text overlaps. Each arm must capture at least one figure, and the same files, because compare.py alone passes
  on none.
- **Installing:** `tools/install_palette.py` copies an arm-1 PDF to `figs/` and the note. It comments out the old
  install line and adds an `install_palette_fig` line.
- **Capture:** `tools/capture_palette.py` records each saved figure: the full `artists.py` index, with colours and
  styles, as `compare.py` reads it, plus texts and capture_any.py's text overlaps.
- **Environments:** venvs built for this pass on the laptop with `uv`, run under `env -i` with an empty HOME, all on
  Python 3.12.2:
  - matplotlib 3.10.8 with numpy 1.26.4;
  - matplotlib 3.11.2 with numpy 2.5.4;
  - matplotlib 3.11.1 with numpy 2.5.4.

## Family 4: Figs. 19–22 (installed)

- **Recipe:** `tools/palette_family4.py <note-figstyle-20261113/runs/family4/pickles> <out>`, under matplotlib 3.10.8.
  - It loads each pickle only through `restyle_family4.load()`, which checks the pickle's sha256 first.
  - It recolours by `recolour.tsv`, sets the Fig. 20 hatches, and fixes notation in text only (E_{\rm avail}, p_∥).
  - It rebuilds the axes legends frameless, and moves the `1e-38` offsets into the axis labels.
  - It then calls `restyle_family4.restyle()` unchanged, and checks that no legend entry is lost.
- **Arm 0** is `restyle_family4.py`, unchanged.
- **Checks:** `runs/family4/CHECKS.txt` (`tools/checks_family4.sh`):
  - arm 0 is EQUAL-BUT-DATE and 0 px against the files at `2fe070fec`, in all four;
  - arm 1 against arm 0 gives COMPARE :: PASS;
  - text overlaps go 1→0, 2→2, 0→0 and 1→1. The remaining three were already in the installed files.
- **Changes as drawn:**
  - this work is red filled circles;
  - the generators take the paper colours, and GENIE CV is pink down-triangles;
  - Fig. 20's modes are four greys with hatches, and its data − GENIE-CV gap is a this-work outline, not a hatch;
  - Fig. 21's GENIE CV bar is pale pink and the MEC addition orange;
  - Fig. 22's Ascencio point is a black open square.
- **Install:** `make_figures.sh` installs the four from `figs/` (`install_palette_fig`). Their print-style lines stay
  as comments.

## Figs. 25, 23, 16 and 1 (installed)

Each was run with `tools/arms.sh` under matplotlib 3.10.8, with the fake-ROOT stand-in its family used on 11-13.
Arm 0 reproduces the file installed at `2fe070fec` (EQUAL-BUT-DATE, 0 px), and arm 1's compare passes. Each
`runs/<family>/CHECKS.txt` ends with the installed copy against that arm 1.

- **Fig. 25 (`band`):** `overlay_eavailW_band.py --from-arrays …/family5/dumps/band_arrays.npz --print-style`.
  - Its GENIE+MEC was the Tune blue (`MPL_COLOR`); it is now the paper's orange.
  - GENIE CV is pink down-triangles, and the data are this work's red.
  - The figure legend is rebuilt at its anchor.
- **Fig. 23 (`q3`):** `q3_excess_projection.py --from-arrays …/q3_arrays.npz --print-style`.
  - The axis labels are in math, with units in parentheses.
  - The ratio reads "unfolded / GENIE prior", as the producer computes (its docstring: the unfolded counts over the
    GENIE prior). The director accepted this over the plan's "Unfolded / Tune v1".
  - The E_avail marginal (firebrick) takes this work's red. Black is left as drawn, because the colour bar's dividers
    share it.
  - The text-overlap count rises from 23 to 29. Every added pair is the longer y label against the heatmap's in-cell
    numbers, which the colour bar separates in the drawn figure.
- **Fig. 16 (`spec`):** `plot_eavail_spectrum.py --from-arrays …/family4/dumps/eavail_spectrum_arrays.npz
  --print-style`.
  - All of it is this work, now in red.
  - ×10⁻³⁸ is in the y label, and the catch bin reads 6.74×10⁻⁴¹.
- **Fig. 1 (`ctrl`):** `make_control_plots.py --from-arrays …/family1b/dumps/control_plots_ext_arrays.npz
  --extended-display --print-style`.
  - The MC signal (MnvTune v1) is Tune blue, and the MC background is grey.
  - The same run draws Fig. 3 (`migration_resolution`, which the primer shares). It is not reinstalled, by the
    director's ruling.
- **Not changed, by the director's rulings:**
  - Fig. 5: hRel2D's "std/mean" could not be traced to f_CV in the producer of the installed dump.
  - Fig. 3.

## Figs. 26–29 (`gbdt`, installed)

- **Recipe:** `nd-unfolding/gbdt_model_dependence/analyze.py --out <dir> --print-style`, under matplotlib 3.11.2.
- **Arm 0** is byte-equal to the four files installed at `2fe070fec` (EQUAL; these PDFs carry no date).
- **Arm 1's edit** is `drop_titles.tsv`. Each figure's baked-in figure title (the producer's suptitle,
  analyze.py:388, :441, :465, :526) is cleared, its content being the caption's. Every axes is stretched upward into
  the freed height, so no blank band is left.
- **Colours unchanged:** the series are truths and studies (D1, q3 stress, W1, W3; nominal, W2), not palette
  identities.
- **Checks** (`runs/gbdt/CHECKS.txt`):
  - the compare passes;
  - text overlaps go 1→0 in gbdt_recovery and stay 0→0 in the other three;
  - the installed copies equal a fresh arm 1 exactly.

## Figs. 30 and 34 (pinned)

- **Recipes:** `docs/analysis-note/figures/methods_m3/fig_m3_coverage.py` and `fig_m3_background.py`, each with
  `--repo <worktree> --outdir <dir>`. They run under the laptop's base conda (matplotlib 3.10.1, numpy 1.26.4), the
  version that drew the installed files.
- **Arm 0** writes `m3_fig3_coverage.pdf` and `m3_fig1_background.pdf`. They are byte-equal to the installed
  `paper_fig_coverage.pdf` and `paper_fig_bkg_residual.pdf`, the hand-renamed copies (`INSTALLED=` in arms.sh).
- **No palette edit:** no identity is drawn. Blue and red are the 68 % and 95 % intervals in Fig. 30, and the two
  background methods in Fig. 34.
- **Install lines:** both gain an `install_palette_fig` line, so their installed bytes are pinned for the first time
  (COMBINED-PLAN.md section 5(b), tier 1b). The plan's panel split and labels for these figures are not made.

## CI: inherited failures

The record-checks steps at this branch's commits pass, apart from the failures below. Each fails identically at the
base it came from, rerun in a clean worktree on 2026-11-17, and the director approved the push with them documented.
The first three fail at `2fe070fec`; the fourth came in with the merge of 95ae9114 and fails identically there:
- `test_check_sec4_receipts.py` expects the old partc-r2 budget path. Its two files are byte-identical at the base.
- `check_note_records.py --self-test`: "40 of 41 planted defects".
- `reflow_tex.py --note --check`: 12 sources at the base, and 14 after the merge.
- `test_build_all.py`: 7 failures (ResultLineNamesItsObjectTest ×3, StruckOnlyInHistoryTest, PostedNoteIsOutwardTest,
  ExemptionGuardTest ×2), identical at 95ae9114.
