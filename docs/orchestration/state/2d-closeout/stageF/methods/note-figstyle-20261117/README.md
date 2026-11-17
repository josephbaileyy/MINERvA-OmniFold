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
| tier 1, others | 25, 23, 1, 5, 16, 26–29 | to do |
| tier 1b | 30, 34, then 31 | to do |
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
