# Figure consistency pass, 2026-11-28: TrueType fonts, two tension figures at 8 pt, no sans-serif figure

**By** the limitation-resolver lane, on Joseph's go relayed by the director ("lets do the figure PR with the negweight
fetch"). Presentation only: every plotted array of every figure here is equal to its unchanged recipe's.

## What changed

| part | figure (docs/analysis-note/figures/) | change |
|---|---|---|
| (a) | `MEFHC_5iter_xsec_proj_pt`, `_proj_pz`, `MEFHC_5iter_pull_full`, `MEFHC_5iter_xsec_paper_pz_slices`, `tension_mode_maps` | TrueType (CID) fonts instead of Type 3 |
| (a)+(c) | `tension_spectrum`, `tension_chi2_map` | TrueType fonts; text at 8.0 pt (ticks) and 8.5 pt (labels) printed, from 5.5 and 6.5 pt; canvas 3.185 × 3.4 in (was × 2.6) |
| (b) | `eavail_marginal_vs_paper_pull_full` | the note's serif fonts (DejaVu Serif, Computer Modern mathtext), from DejaVu Sans and Sans Mono; the heat map's axis and tick labels in GeV/c, as Fig. 3 prints them (Joseph 2026-11-28, "we should match them") |
| (b) | `negweight_ratio_2d` | `--print-style`: serif fonts, math axis labels, drawn at its 0.7 \textwidth slot |
| F1 | `control_plots`, `mode_decomp_mec_eavail_central` | none: install lines for the files 430b42db2 installed, which `make_figures.sh` did not pin |

Code: `2d-unfolding/restyle_2026_10.py` (`PRINT_FONT` gains `"pdf.fonttype": 42`, the key `note_print_style.PRINT_RC`
already has) and `docs/analysis-note/test_note_print_style.py` (the key in the pinned set);
`2d-unfolding/plot_negweight_ratio.py` (`--print-style`, off by default; the default output is unchanged);
`docs/analysis-note/freeze_checks.py` (`SANS_ALLOWED = ()`; check 5 fails only on a sans font embedded by a figure,
and lists TeX's own sans, the director's ruling of 2026-11-28; tests in `test_freeze_checks_fonts.py`);
`docs/analysis-note/make_figures.sh` (one
`install_current_fig` block from [`figs/`](figs/), `figs/SHA256SUMS`; a `layered (2026-11-28)` comment on each line it
supersedes; the negweight run line gains `--print-style`).

**Not here.** `MEFHC_5iter_xsec_paper_pt_slices.pdf` (the readability pass redraws it; this record will take its recipe
from that merge). `fd_g_fig_modes.pdf` (deferred by Joseph). The STIX ∥ glyph, bold weights and true Computer Modern
text are out of scope. `proj_pt` needed no size change: it already prints at 7.9 pt (ticks) and 8.4 pt (labels); a
pdfminer per-glyph median of 5.5 pt, read from its mathtext y label, had suggested otherwise.

## Recipes (each figure's installed recipe, run as arm 0; arm 1 is the change)

All on this laptop in `~/cov2d-work/figenv/rootmpl3108` (Python 3.11.18, matplotlib 3.10.8, numpy 1.26.4, ROOT 6.40.04),
under `env -i` where the recipe uses it, BLAS and OpenMP threads 1; the stamp strip in `figenv/pdfedit` (pikepdf 9.4.2).
Inputs: `er.root` 5171c7b8 (`ibu-chi2-20261123/tier1/units/e/`), the ancillary files in `~/cov2d-work/figfetch/anc`
(pins in `regenA4/AMENDMENT-A4.txt`), the 3D product `~/cov2d-work/figfetch/f3d-a/xsec_3d_MEFHC_5iter_lgbm.root`
0dd94830 (`re1/RE1-AMENDMENT-DECLARATION.md:151`), and the two negative-weight ROOT files fetched below.

- **(a), arms 0 and 1:** `ibu-chi2-20261123/regenA4/receipts/regenA4_run.sh` (2d5246a1), unchanged:
  `bash regenA4_run.sh <W> e <W>/docs/orchestration/state/ibu-chi2-20261123/tier1/units/e/er.root <FR>`, with W this
  worktree before (arm 0) and after (arm 1) the `PRINT_FONT` change. It draws Fig. 2 (`compose_fig2_r3.py`), Fig. 3
  (`compose_fig3_r3.py` over `compare_to_paper_fullcov.py --style restyle-2026-10 --print-font --sd-label`, the producer
  as 430b42db2 left it), the slices (`compose_slices_markers.py`, then `strip_stamp.py`) and the tension figures
  (`palette_run.py` over `diagnose_tension.py`). These are the recipes of the files installed before: regenA4 (A4, A4b),
  note-tune-v1-legends-20261126 and FIGS-REPORT-20261127.
- **(c):** [`tools/run_tension_c.sh`](tools/run_tension_c.sh) `<W> <er.root> <FR>`: the tension step above with
  [`tools/fontsize_run.py`](tools/fontsize_run.py) in `palette_run.py`'s place. It applies the palette edits, then
  note-figpass-20261119's `layout_lib.apply()` unchanged (freeze ticks, scale text and floor it, set the canvas,
  `tight_layout`) with this record's [`layout.tsv`](layout.tsv) and no other table.
- **(b) eavail:** [`tools/run_eavail.sh`](tools/run_eavail.sh) `<W> <f17|main> <0|1> <3D root> <FR>`:
  note-figpass-20261119 f17's arm 1 (`layout_run.py`, `LAYOUT_PALETTE=0`, over `remap_anc.py <anc>
  compare_to_paper_fullcov.py --ours <3D>`), then note-figround-20261121's `strip_stamp.py`, with
  [`tools/housefont_run.py`](tools/housefont_run.py) in `layout_run.py`'s place.
  - **Arm 0** (`f17 0`): the producer f17 ran, read from the f17 receipt commit 59963f09b (blob 992eb13f, with
    `uq/reported_cells.py` 54a0ab35), and no house-font step: `layout_run.py` exactly.
  - **Arm 1** (`main 1`): main's producer, which since 430b42db2 labels the heat map's cell boundaries (pT 0, 5, 10, 14;
    every second p∥ one) and its axes in GeV/c, as Fig. 3 prints them. Of the two ways offered, this one, not texts.tsv:
    texts.tsv replaces substrings in every drawn text, so it cannot relabel numeric ticks ("2" occurs in many texts).
    `FIG3_LABELS=1` drops the two texts.tsv rows that renamed the old "p_|| bin" / "p_T bin" labels (each must be
    present; layout_lib stops on a row it cannot find); its third row, "pull" → "standardized difference", stays.
    `HOUSEFONT=1` sets `restyle_2026_10.PRINT_FONT` in rcParams and the serif family and Computer Modern mathtext on
    every drawn text before the layout pass, and one wording row (`HOUSE_TEXTS`, applied by layout_lib like texts.tsv's
    rows): the statistics box's "rms =0.83" reads "rms=0.83", its space having lined the value up with "mean=0.16" in the
    old monospace font (Joseph, 2026-11-28). The x ticks move from every second cell boundary to Fig. 3's four; the y
    ticks keep their places; the canvas and axes boxes do not move.
  - `--style` is not used: under it the histogram takes zero-aligned bins of width 0.15 instead of 30 equal bins, and
    other sizes and labels. The figure stays on our pT edges (KNOWN_ISSUES 103 is unchanged).
- **(b) negweight:** [`tools/run_negweight.sh`](tools/run_negweight.sh) `<W> <0|1> <inputs dir> <FR>`:
  `plot_negweight_ratio.py` (make_figures.sh's run line) without and with `--print-style`.

The installed files are arm 1's (arm c's for the two tension figures): [`figs/`](figs/), `figs/SHA256SUMS`.

## Checks ([`runs/CHECKS.txt`](runs/CHECKS.txt), `python3 tools/checks.py <arms root> <W> 02ae86003006`: CHECKS :: PASS)

- **Arm 0 reproduces the installed file.** (a): all 8 EQUAL-MOD-DATE ([`tools/equal_mod_date.py`](tools/equal_mod_date.py):
  every byte equal once the creation date, the xref offsets and the trailer /ID are masked; bytes_but_date.py needs
  equal lengths, and a file saved under SOURCE_DATE_EPOCH=0 has a 6-byte shorter date). eavail: EQUAL-MOD-DATE.
  negweight: the same words and page size; the July file (4e8033eef, no reproduction record) is not byte-equal, its
  colour bar sitting about 1.8 pt to the right.
- **The data are unchanged.** [`tools/compare_captures.py`](tools/compare_captures.py) on capture_palette.py's records:
  every drawn array (key, dtype, shape, bytes) and the artist index (data, colours, styles) equal between the arms;
  for (a) the texts (strings and sizes) too; for (c) the strings. String changes, each listed in full by checks.py:
  negweight, the two axis labels; eavail, the heat map's two axis labels ("$p_T$ bin" → "$p_T$ (GeV/c)", "$p_\parallel$
  bin" → "$p_\parallel$ (GeV/c)") and its tick labels (0, 2, …, 14 and 0, 2, …, 16 → 0, 0.4, 1, 4.5 and 1.5, 2.5, 3.5,
  4.5, 6, 8, 10, 20, 60), and the statistics box's "rms =0.83" → "rms=0.83", nothing else. The data hash of pull_full, f8c0ed07, is the one FIGS-REPORT-20261127.txt records.
- **Printed values.** eavail: χ²/ndf 4.981 and mean / rms 0.159 / 0.828 in both arms. negweight: from the plotted
  array, median 1.000, RMS 1.4 %, worst −12.6 %, equal to `\nwMedianBin`, `\nwRmsBin`, `\nwWorstBin` (values.tex).
- **Fonts.** Every new file embeds only CID TrueType fonts, none sans. In the note built from this tree (build_all rc 0),
  of the 26 figures main_note.fls reads only `MEFHC_5iter_xsec_paper_pt_slices.pdf` still has Type 3, and none has sans.
- **freeze_checks check 5** ([`runs/freeze-fonts.txt`](runs/freeze-fonts.txt), `--only 5`, on main's build at 02ae8600
  and on this branch's): main's check fails on both (CMSS8, the `^{\mathsf T}` transpose in the prose's math, on 13
  pages, and the two missing labels fig:eff, fig:calibration); this branch's check fails on main's build on exactly the
  two sans figures (p.42 negweight, p.58 eavail) and passes on this branch's, listing the CMSS8 pages.
- **Overlaps.** [`tools/pdf_text_overlaps.py`](tools/pdf_text_overlaps.py) on the saved files: 0 for the (c) and (b)
  figures. (capture_palette.py's text_overlaps reads positions from the draw before layout_lib's resize, and reports
  three for the spectrum's legend, which the saved file shows clear of the tick labels.)
- **Tests.** test_note_print_style.py 6 passed; 2d-unfolding/tests/test_published_axis_widths.py 54 OK under the figenv
  ROOT python (`python3 -m unittest`; bare pytest skips every test without PyROOT).

## The negative-weight inputs ([`fetch/`](fetch/))

The two ROOT files existed only on NERSC (inventory: `negweight-hpss-20260821/inventory.tsv:2,6`). One login-node
ssh, the director's GO after cov2d's ack, 2026-11-28 06:56:58–06:57:04Z, 0 node-h:
`bash fetch/nw_fetch.sh pscratch 0f3d2bad… a82a5689… <dir>`. [`fetch/nw_remote.sh`](fetch/nw_remote.sh) runs the
fence (sacct and squeue; refuses on the protected job families), lstat's each file, reads it with
O_RDONLY|O_NOATIME|O_NOFOLLOW, lstat's it again on the same node, and streams a tar to stdout; nothing is written on
the cluster. [`fetch/nw_verify.py`](fetch/nw_verify.py) extracts only the two files and checks the inventory shas. The
hpss mode (`hsi get` of negweight_runs_8.tar to stdout) was not run. Receipts in [`fetch/run1/`](fetch/run1/): login25,
FENCE CLEAR, both files UNCHANGED (atime, mtime, size), NW-VERIFY :: PASS. The ROOT files are not committed (Joseph,
2026-08-21: do not git-track the negweight ROOT population); `fetch/run1/inputs/SHA256SUMS` names them.
`fetch/test_nw_fetch.py`: 27 tests, local, no ssh.
<!-- absence-ok: states which of the package's two modes this record's own fetch used (pscratch, run once); not a claim that a result or study does not exist -->
