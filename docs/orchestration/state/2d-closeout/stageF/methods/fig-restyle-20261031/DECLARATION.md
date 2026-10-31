# Restyle of the note's 2D result figures (Figs. 7–14): declaration (2026-10-31, paper rewrite lane)

**Status.** For the director to bind, with its code. The director answered §6's three questions on 2026-10-31, and
they are now rulings.
- **Done:** the code and its tests are committed. Dev draws on a Perlmutter login node ran under the director's approval
  of 2026-10-31; their outputs are never installed or committed. A dry run of the run driver passed (§4).
- **Not done:** the bound run, Joseph's review and any install.
The base is origin/main `bab87aeb3`.

**Under** [DECISION-20261031-joseph-rater-account-figures-chi2-consult.md](../../../../../DECISION-20261031-joseph-rater-account-figures-chi2-consult.md)
item 2 (#574). Joseph chose: "Restyle the note's 2D result figures (Figs. 7–14): readable font sizes, proper axis labels
and units, panel labels, no blank bands. Style only, no number changes; needs a small CPU run of the plotting scripts at
NERSC." The changes come from the figure diagnosis's STYLE list
([FIGURE-DIAGNOSIS-REPORT.md](../figure-diagnosis-20261030/FIGURE-DIAGNOSIS-REPORT.md) §6, `data/changes.tsv`).

## 1. The figures, their files and their producers

The note's Figs. 7–14 are eleven PDFs. Each is installed by `make_figures.sh:228-239` (`install_re2_fig`) from the
committed copy `re2-integration/figs/`. That copy is RE-2 part C's output, drawn on Perlmutter by
`2d-unfolding/re2/partc/re2c_run.sh refined` (steps at `re2c_run.sh:160-170` on `bab87aeb3`), with digests in
`re2/run/partc_r2/partc-r2/SHA256SUMS`. The `run` lines at `make_figures.sh:37-44` draw other versions of these files
and are overridden by the installs, so they are not this restyle's producers.

| note figure | label | file(s) | producer (`2d-unfolding/`) | re2c step |
|---|---|---|---|---|
| 7 | `fig:xsec` | `MEFHC_5iter_fig13`, `MEFHC_5iter_xsec_proj_pt`, `_proj_pz` | `plot_2d_threeway_fig13.py`, `plot_2d_cross_section.py` | fig13, xsec_proj |
| 8 | `fig:pull` | `MEFHC_5iter_pull_full` | `compare_to_paper_fullcov.py` | pull_full |
| 9 | `fig:ptslices` | `MEFHC_5iter_xsec_paper_pt_slices` | `plot_2d_paper_comparison.py` | paper_slices |
| 10 | `fig:pzslices` | `MEFHC_5iter_xsec_paper_pz_slices` | `plot_2d_paper_comparison.py` | paper_slices |
| 11 | `fig:tension` | `tension_spectrum`, `tension_chi2_map` | `diagnose_tension.py` | tension |
| 12 | `fig:tensionmodes` | `tension_mode_maps` | `diagnose_tension.py` | tension |
| 13 | `fig:model` | `model_comp_projections` | `compare_to_models.py` | models |
| 14 | `fig:modelmaps` | `model_comp_ratio_maps` | `compare_to_models.py` | models |

**Other users of the same files.**
- The primer includes `MEFHC_5iter_fig13` (`primer_body.tex`). Its copy is in scope, since the same producer draws
  it (ruling 2).
- The paper includes none of the eleven.
- `make_figures.sh:295` asserts that `MEFHC_5iter_pull_full.pdf` is 864 × 360 pt before it crops
  `paper_validation_residual.pdf`. No `.tex` file includes that crop on `bab87aeb3`. The restyle keeps Fig. 8's canvas
  at 864 × 360, so the assert still holds.
- `xsec_proj` also draws `MEFHC_5iter_xsec_eff_heatmap`. Its pinned copy stays installed, and the restyled run's
  heat map is not installed.

## 2. What changes (STYLE only)

The changes come from the diagnosis's most-supported STYLE rows for these figures (report §6, items 2–7). They are
written as `--style restyle-2026-10`, which is off by default, in the six producers, with shared helpers in
`2d-unfolding/restyle_2026_10.py`.
- **Printed size.** Each figure is drawn at the width the note prints it (`restyle_2026_10.WIDTH`: the
  `\includegraphics` fraction of the 469.755 pt text width). A font size in the code is then its printed size.
- **Fig. 8 keeps its 12 × 5 in canvas.** `make_figures.sh:295` asserts its 864 × 360 pt page before the crop, so its
  text is set larger to print at about 5 pt.

| figure | file(s) | change |
|---|---|---|
| 7 (top), and the primer | `MEFHC_5iter_fig13` | same layout fractions on a 4.03 in canvas; fonts for print; slice labels and "×" factors in math; "MnvTune v1" → "MINERvA Tune v1"; axis titles in math with units; the legend left-aligned in its empty cell; inner rows' hidden tick labels (they showed at the right edge) and colliding end ticks ("60 4") removed |
| 7 (bottom) | `MEFHC_5iter_xsec_proj_pt`, `_pz` | printed size; units "(cm$^2$/(GeV/$c$)/nucleon)"; the y offset in math (×10$^{-38}$); ratio label "This work / GENIE" |
| 8 | `MEFHC_5iter_pull_full` | the same canvas at 14.5 pt; axis labels in math; "pull" → "Standardized difference" in both panels; "Bins"; the sample tag at the same size |
| 9, 10 | `MEFHC_5iter_xsec_paper_pt_slices`, `_pz_slices` | printed size; each panel's interval printed above it, with its unit; y label "$d^2\sigma/dp_T\,dp_\parallel$, scaled"; the legend in the empty cell (Fig. 9) or the top margin (Fig. 10); an x label on every panel with none below; the blank band left by the suppressed title removed |
| 11 | `tension_spectrum`, `tension_chi2_map` | the spectrum's two panels stacked, so the two files have the same height side by side and leave no blank band; labels in math |
| 12 | `tension_mode_maps` | printed size; labels in math; panel labels (a)–(f) above the panels; ticks at whole bins |
| 13 | `model_comp_projections` | printed size; labels and units in math; the model's name without underscores; the y offset in math |
| 14 | `model_comp_ratio_maps` | printed size; labels in math; "(a) This work" and "(b) Published data" above the panels; colour bar "Ratio to MINERvA Tune v1" |

**Why titles are not used.** `technote_style.py` suppresses `set_title` and `suptitle`, which is why Figs. 9 and 10
printed no slice labels. The restyle draws labels as text.

**A row not made as written.** The draft's row for Figs. 9 and 10, "the y axes give their physical units", is not made.
- **Why:** each panel is scaled to its own maximum, and its "×10^n" note gives only the order of that factor. A
  physical unit would need each panel's maximum printed, which is a new number (CONTENT).
- **Instead:** the label says "scaled", as before, and the existing notes stay.

**Not changed:**
- **No plotted number.** Values, errors, bin edges, binning, data order, every scale factor and the colour limits stay
  the same.
- **No colour, marker or line style of a data series.** Note Fig. 13's caption-side colour fix relies on Tune v1 staying
  blue.
- **No CONTENT or PROTECTED row** of `changes.tsv`:
  - no ratio or residual panels;
  - no uncertainty bars on Fig. 13;
  - no mode-rank or χ² annotations on Fig. 12, which its suppressed titles held;
  - no χ²/ndf.
- **No caption in this change.** Two caption sentences must change with the install, as truth fixes through the ledger
  and agy:
  - Fig. 14's "the panels have no printed titles", now that the panels carry labels;
  - Fig. 13's colour, already planned (CAPTION-FIXES.md).
  The other captions stay true, including Fig. 11's "(left)"/"(right)".
- **No other figure.** `technote_style.py` is not edited. With the option off, every producer draws its old figure (§3
  check 2, arm "off").

## 3. The checks

The tools are `fig-restyle-20261031/tools/`, committed with their tests:
- `capture.py`, `artists.py`: the record of what each saved figure draws;
- `compare.py`: checks 3–5;
- `raster.py`: check 2;
- `textsize.py`: check 7;
- `run.sh`, `run_remote.sh`: the run;
- `sheets.py`: Joseph's review sheets (§5.1);
- `selftest.py`, `toy_producer.py`, `mutate.py`: the tests.

1. **The record.** `capture.py` runs each producer as `re2c_run.sh`'s `step` does: `runpy`, with the deploy's
   `2d-unfolding/uq`, `2d-unfolding` and root on `sys.path`.
   - **Data:** `Figure.savefig` is wrapped outermost, after `technote_style`'s `.pdf`-twin wrapper. At each save it
     writes every data artist's arrays and RGBA, hashed bit for bit (`artists.py`):
     - lines, with their style and marker;
     - collections: offsets, segments, data-space paths, colour arrays and limits;
     - images and meshes;
     - data-space patches.
     Text, ticks, spines, grid lines and legends are not captured.
   - **Text:** after the save, it also writes each drawn text's font size (unhashed).
   - **Refusal:** it refuses to run with `TECHNOTE_DARK` set, which recolours every series.
2. **Identity control.** The eleven PDFs of two arms must rasterize at 300 DPI to the committed copies' pixels:
   - **"before":** the base commit's producers;
   - **"off":** the bound commit's producers without the option.
   Cluster PDFs carry timestamps, so they are not byte-compared (RE2-DECLARATION-C §7, ruling Q3).
3. **Equality before and after.** For each figure, the multiset of captured item hashes of "before" and "after" must be
   equal. An added, missing or changed data artist fails. Each step's records must be exactly the figures named.
4. **The other outputs.** These must be identical after the run directories' and deploys' paths are replaced and lines
   reporting a wall time are dropped:
   - `model_comp_report.txt` and `tension_report.txt`;
   - each step's stdout, which carries the χ² and pull printouts.
5. **Inputs.** Both arms must open the same files with the same sha256:
   - each `TFile.Open` is logged, and every existing file named in argv is hashed;
   - E_R is `a5c13fc3…` and the published covariance `6c6dce72…` (`logs/inputs.sha256`).
6. **No stray writes.** No file under `$A/2d-unfolding` or `$A/docs` may be newer than a marker stamped at each arm's
   start.
7. **Printed text size, from what is drawn** (`textsize.py`, which replaces the draft's instrument; see §5.4):
   - every text's font size times printed width over the PDF's page width;
   - each of the eleven must be at least 4.0 pt (ruling 3);
   - and no PDF text of "after" may contain `_` or `^`.
8. **Tests in both directions.**
   - **`selftest.py`, 20 cases on a toy producer with the artist kinds of Figs. 7–14:**
     - silent on an identical rerun, a restyle (size, fonts, labels, panel layout, panel labels, text) and a
       wall-time change;
     - fires on a one-ulp value, an RGBA change (a series; a line alone; a scatter alone), a dropped series, a
       changed input, a report value changed alone, an unnamed figure record and a one-pixel raster change;
     - check 7: a toy text printed at 3.5 pt fails the 4.0 pt floor and is named; the same text at 5.0 pt passes. The
       toy's 13 in canvas is printed at 6.5 in, so the width scaling is exercised.
   - **`MUTATION-RECEIPT.txt` (`mutate.py`):** the control passes, and all 13 mutants of the checkers are killed:
     - colours not hashed;
     - a float32 tolerance;
     - patches skipped;
     - labels hashed;
     - count-only comparison;
     - timing lines kept;
     - outputs or inputs not compared;
     - size-only raster comparison;
     - the size floor's comparison inverted;
     - the printed-width scaling dropped;
     - the wrong wrapper order.
   - **Checks 3 and 7 both ways.**
     - The ASCII check finds 2–30 lines in each of the five old figures checked, and none in the eleven restyled ones.
     - On the old figures, the floor fires for six of the eleven (2.45–3.45 pt: Figs. 7 top, 8, 9, 10, the spectrum
       of 11, and 13). The other five are at 4.05–4.88 pt.

## 4. The run

- **Driver:** `run.sh <base> <bound> <local out dir>`, run from a local clone.
  - **Deploys:** each commit is archived with `git archive` (`technote_style.py`, `2d-unfolding/`, and for the bound
    commit `tools/`), together with a `COMMIT` file. Each is unpacked in a new
    `/pscratch/sd/j/josephrb/2d-closeout-restyle-20261031/run/<base|bound>/deploy`. No existing checkout is moved or
    written, and the run root must not exist.
  - **Arms:** three run in turn (`run_remote.sh`):
    - "before": the base commit's producers;
    - "off": the bound commit's producers, without the option;
    - "after": the bound commit's producers, with the option.
    The checks' own code is the bound commit's in every arm.
- **Steps:** `re2c_run.sh:160-170`'s six figure steps, with the same argv except for output paths.
  - **One change from `re2c_run.sh`:** the working directory is the arm's own directory, not `$A/2d-unfolding`, so that
    nothing is written under `$A`.
  - **Why it is safe:** every default input path of the six producers is absolute (`DEFAULT_*`, `ANC_DIR`). Checks 5
    and 6 confirm it.
- **Where:** a Perlmutter login node, with no Slurm and 0 node-h. Each arm stops itself at 15 minutes (`timeout 900`).
  In the dry run under the dev directory, the "after" arm took 53 s.
- **Fetched back:** the PDFs, captures, logs and `SHA256SUMS`, but no PNGs. The checks run locally and write
  `CHECKS.txt`. The new PDFs and the run's records are committed under `fig-restyle-20261031/figs/` and `run/`.
- **CFS and HPSS:** nothing is written.
- **Dry run** (dev, approved 2026-10-31; outputs not installed or committed): `run.sh bab87aeb3 4437aaf8` under
  `dev/runtest1`. `RUN CHECKS :: PASS`:
  - check 2: 22 of 22 pixel-equal;
  - checks 3–5: COMPARE PASS;
  - check 6: 0 files in each arm;
  - check 7: 5.00–5.92 pt, and no ASCII.

## 5. Integration, after the checks pass and Joseph's review

1. **Joseph's visual review** of the eleven comes before any install. The director shows them to him.
   - `tools/sheets.py` makes one PDF per figure from the bound run's "after" PDFs and the committed copies, old on the
     left and new on the right, both as vector graphics at the figure's printed width.
   - Each sheet must be one page. The sheets and their SHA256SUMS go in `fig-restyle-20261031/review/`.
2. **Install.** `make_figures.sh` installs the eleven from `fig-restyle-20261031/figs/` with the new digests. The RE-2
   install lines stay, as comments, under a dated note.
3. **The RE-2 integration ledger (ruling 1: re-point, do not replace).**
   - **Today:** its eleven `G` rows (`re2-integration/ledger.tsv`, for example `FIG-MEFHC_5iter_fig13`) pin each figure
     to part C's SHA256SUMS and to the copy in `re2-integration/figs/`.
   - **After:** the restyled PDFs are new files with new digests, in `fig-restyle-20261031/figs/`. The eleven rows are
     re-pointed to them and to the restyle run's SHA256SUMS. `check_ledger.py` then reads each copy's directory from
     its row, not from a fixed path.
   - **The history:** part C's copies and records stay where they are. A record, `fig-restyle-20261031/DIGESTS.tsv`,
     gives each figure's old and new digest with both SHA256SUMS entries.
4. **The figure checks after the note build (amended; ruling 4).**
   - **The gate:** check 7, `textsize.py`, on the run's PDFs: the drawn font sizes, scaled to printed width, at a
     4.0 pt floor (ruling 3). Each figure's printed width is `restyle_2026_10.WIDTH`, from its `\includegraphics`.
   - **The record:** the figures are re-cropped from the new note and primer PDFs (`figdiag.py crops`, `measure`) and
     recorded beside the diagnosis's table. That re-crop is a record only, not a gate.
   - **Why the draft's gate was replaced.** The draft made the gate `figdiag.py measure`'s smallest pdftotext word box,
     the diagnosis's instrument. On matplotlib's PDFs that box does not track the drawn size:
     - with matplotlib's default Type 3 fonts, ordinary text measures about 1.9 times its size (5.5 pt reads 10.4);
     - math sub- and superscripts, and a ")" after a superscript, measure 2.2–2.9 pt for text set at 6.5 pt, in every
       font set tried.
   - **Both measurements on the same PDFs** (the dry run's eleven, before and after; `SIZE-MEASURES.tsv`, in pt at
     print):

     | figure | pdftotext min, before | drawn min, before | pdftotext min, after | drawn min, after |
     |---|---|---|---|---|
     | `MEFHC_5iter_fig13` | 2.32 | 3.10 | 2.35 | 5.00 |
     | `MEFHC_5iter_xsec_proj_pt` | 1.71 | 4.05 | 2.35 | 5.89 |
     | `MEFHC_5iter_xsec_proj_pz` | 1.73 | 4.10 | 2.36 | 5.92 |
     | `MEFHC_5iter_pull_full` | 4.43 | 3.03 | 3.49 | 5.12 |
     | `MEFHC_5iter_xsec_paper_pt_slices` | 1.34 | 3.44 | 2.06 | 5.48 |
     | `MEFHC_5iter_xsec_paper_pz_slices` | 1.35 | 3.45 | 2.08 | 5.52 |
     | `tension_spectrum` | 0.83 | 2.45 | 2.19 | 5.50 |
     | `tension_chi2_map` | 7.04 | 4.55 | 2.89 | 5.50 |
     | `tension_mode_maps` | 7.18 | 4.64 | 4.13 | 5.50 |
     | `model_comp_projections` | 1.89 | 3.40 | 2.78 | 5.50 |
     | `model_comp_ratio_maps` | 7.54 | 4.88 | 4.13 | 5.50 |

     - **Old text passes:** the pdftotext minimum passes old figures whose text prints small. Old Fig. 8 reads 4.43 pt
       and draws 3.03; the old χ² map reads 7.04 and draws 4.55.
     - **Restyled text fails:** it fails nine of the eleven restyled figures, at 2.06–3.49 pt, although they draw at
       5.0–5.9 pt.
     - **The drawn sizes are right:** they follow the code's font sizes exactly. They put six old figures below 4.0 pt,
       and none after.
5. **Captions.** The Fig. 14 and Fig. 13 caption fixes (§2) go into the next note round as truth fixes, through the
   ledger and agy (ruling 6).
6. **The note build and its gates.** The note, primer and paper are rebuilt with every gate and the `record-checks.yml`
   steps.

## 6. Rulings (the director, 2026-10-31)

1. **The `G` rows are re-pointed, not replaced in place.**
   - The restyled PDFs are new files with new digests.
   - The eleven `G` rows of `re2-integration/ledger.tsv` are re-pointed to them.
   - A record gives each old and new digest (`DIGESTS.tsv`, §5.2).
   - The old copies stay where they are, as the history.
2. **The primer's `MEFHC_5iter_fig13` is in scope,** since it comes from the same producer (§1, §5.4).
3. **The floor is 4.0 pt,** the anchors' lower bound. The restyle aims for about 5 pt (§5.4).
4. **The size gate is `textsize.py`** (§5.4, amended): drawn font sizes scaled to printed width, at 4.0 pt. The figdiag
   re-crop stays as a record only, since its pdftotext boxes misread matplotlib's Type 3 text.
5. **The units stay off Figs. 9–10.** Printing each panel's maximum would be a new number (§2).
6. **Captions:** Fig. 14's "no printed titles" sentence and Fig. 13's colour fix go into the next note round, as truth
   fixes.
7. **Joseph's review sheets** are one PDF per figure from the bound run's outputs, old on the left and new on the right
   (`tools/sheets.py`, §5.1).

## 7. Follow-ups

- **The diagnosis report's §3 text-size table** compares pdftotext boxes of matplotlib figures with those of LaTeX-set
  anchors, which §5.4 shows are not on one scale. A correction PR, in #584's style, restates the finding on drawn sizes
  (ruling 2 of the director's message of 2026-10-31).
