# Restyle of the note's 2D result figures (Figs. 7–14): declaration (2026-10-31, paper rewrite lane)

**Status.** A draft, for the director to bind. **No code has changed and nothing has run.** The base is origin/main
`bab87aeb3`.

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
- The primer includes `MEFHC_5iter_fig13` (`primer_body.tex`), so the restyle reaches the primer's copy too.
- The paper includes none of the eleven.
- `make_figures.sh:295` asserts that `MEFHC_5iter_pull_full.pdf` is 864 × 360 pt before it crops
  `paper_validation_residual.pdf`. No `.tex` file includes that crop on `bab87aeb3`. The restyle keeps Fig. 8's canvas
  at 864 × 360, so the assert still holds.
- `xsec_proj` also draws `MEFHC_5iter_xsec_eff_heatmap`. Its pinned copy stays installed, and the restyled run's
  heat map is not installed.

## 2. What changes (STYLE only)

The changes below are the diagnosis's most-supported STYLE rows for these figures (report §6, items 2–7). Each is
limited to how existing content is drawn.

| figure | change |
|---|---|
| all | tick labels, axis titles, legends and annotations enlarged so that every figure meets §5.4's floor at the width the note includes it |
| all | axis, legend and colour-bar labels typeset in math (e.g. $p_T$ (GeV/$c$)), not ASCII (`p_T`, `MINERvA_Tune_v1`) |
| 8 | the axis label "Pull" reads "Standardized difference" (the caption already says it "is descriptive, not a pull between independent results") |
| 9, 10 | each slice panel labelled with its bin interval; the y axes give their physical units, and any scale factor already applied is stated in the label |
| 9, 10, 11 | blank bands removed and the panels enlarged into the space |
| 14 | panel labels "(a) Our result" and "(b) Published data", drawn as text, not titles (`technote_style.py` strips titles) |

**Not changed:**
- **No plotted number.** Values, errors, bin edges, binning, the order of the data, every scale factor, and the colour
  map's limits stay the same. A label may state a scale factor that the code already applies. A rescale of the plotted
  values to new units is out of scope.
- **No colour, marker or line style of a data series.** Note Fig. 13's caption-side colour fix (decision item 4) relies
  on Tune v1 staying blue.
- **No CONTENT or PROTECTED row** of `changes.tsv`: no ratio or residual panels, no uncertainty bars added to Fig. 13,
  no mode-rank annotations on Fig. 12, no χ²/ndf.
- **No caption, and no other note or paper text.** Any caption wording a restyle makes stale goes to the next note
  round as a truth fix, through the ledger and agy.
- **No other figure.** `technote_style.py` is not edited, since every plotting script imports it.

**How the code changes.** Each producer gets a `--style restyle-2026-10` option, off by default. Every existing
invocation then draws the old figure, and the change is confined to the run in §4. The option touches only figure
size, layout, fonts, label strings and text annotations.

## 3. The checks

The checks are in a new `fig-restyle-20261031/tools/`, committed with tests before the run.

1. **Array capture.** A runner (`capture.py`) runs each producer through `re2c_run.sh`'s `step` invocation, with
   `Figure.savefig` wrapped once more. At each save it writes every data artist's arrays to an `.npz`:
   - line x/y data;
   - collection offsets, segments, paths and colour arrays;
   - image and mesh arrays with their extents and colour limits;
   - patch geometry;
   - each artist's face and edge RGBA.
   Text, ticks, spines and the legend frame are not captured.
2. **Identity control: the before run is the committed figure.** The producers at `bab87aeb3` are run first, without
   the option. Their eleven PDFs are rasterized at 300 DPI and must equal the committed copies' rasters pixel for pixel.
   PDFs drawn on the cluster carry timestamps, so they are not byte-compared (RE2-DECLARATION-C §7, ruling Q3). If any
   raster differs, the run stops and comes back.
3. **Equality before and after.** For each figure, the multiset of captured arrays, each with its RGBA, must be equal
   before and after:
   - bit for bit, with no tolerance;
   - per figure, not per axes, since removing blank bands moves panels.
   An added or missing data artist fails.
4. **The producers' other outputs.** Every non-figure output is byte-identical before and after: the χ² and pull
   printouts, the `.txt` and `.json` reports, and each step's stdout with timing lines removed.
5. **Inputs.** Each `TFile.Open` is logged with the file's sha256. Both runs must open the same set, and `E_R` must be
   `a5c13fc3…` (`partb/out/ER/xsec.root`). The published covariance file must be `6c6dce72…`.
6. **No stray writes.** Files under `$A/2d-unfolding` newer than a marker stamped at the start must be none.
7. **Self-tests, in the direction each check acts.**
   - A planted one-ulp change to one value, and a changed RGBA, must fail check 3.
   - An identical rerun of the before code must pass it.
   - A one-pixel change must fail check 2.

## 4. The run

- **Where:** a Perlmutter login node, with no Slurm, `source setup_salloc_env.sh` and 0 node-h. RE-2 measured about
  12 s per plotting step (RE2-DECLARATION-C §8). The whole run is capped at 15 minutes with `timeout 900`, as
  `re2c_run.sh` is.
- **Deploys:** two clean deploys in a new `/pscratch/sd/j/josephrb/2d-closeout-restyle-20261031/`, one of
  `bab87aeb3` and one of the bound commit. No existing checkout is moved or written.
- **Order:**
  1. the before run and check 2;
  2. the after run;
  3. checks 3–6.
  A failure stops the sequence.
- **Fetched back read-only:** the eleven PDFs, the `.npz` captures, the logs, a `SHA256SUMS`, and the opened-file list.
  They are committed under `fig-restyle-20261031/run/`. The new PDFs go in `fig-restyle-20261031/figs/`.
- **CFS and HPSS:** nothing is written.

## 5. Integration, after the checks pass

1. **Install.** `make_figures.sh` installs the eleven from `fig-restyle-20261031/figs/` with the new digests. The RE-2
   install lines stay, as comments, under a dated note.
2. **The RE-2 integration ledger.** Its eleven `G` rows (`re2-integration/ledger.tsv`, for example `FIG-MEFHC_5iter_fig13`)
   pin each figure to part C's SHA256SUMS and the copy in `re2-integration/figs/`. They are re-pointed to the restyle
   run's SHA256SUMS and copies, by a recorded amendment. `check_ledger.py` reads the copy's directory from the row, not
   from a fixed path. Part C's records stay as they are. See question 1.
3. **The note build and its gates.** The note, primer and paper are rebuilt with every gate and the
   `record-checks.yml` steps.
4. **The figure checks, re-cropped from the new note PDF** with the diagnosis tools (`figdiag.py crops` and
   `measure`). Each of Figs. 7–14 must meet both:
   - its smallest printed word-box height (`figdiag.py measure`, the instrument of report §3) is at least 4.0 pt, just under
     the lowest anchor group's median minimum (4.03 pt, anchor C). The note's median was 2.48 pt;
   - no figure text matches a raw-ASCII pattern (`_`, or `^` outside math).
5. **Joseph's visual review** of the eleven, before the merge.

## 6. Questions for the director

1. **The `G` rows.** Should they be re-pointed as in §5.2, or should the restyled copies replace
   `re2-integration/figs/` in place? Re-pointing keeps part C's copy equal to its SHA256SUMS. Replacing them is the
   smaller diff.
2. **The primer.** The primer's copy of `MEFHC_5iter_fig13` changes with the note's. Is that in scope?
3. **The size floor.** Is 4.0 pt (§5.4) the right floor for every figure's smallest text? The anchor groups' medians of
   the minimum are 4.03 to 6.26 pt, and of the tenth percentile 5.05 to 12.18 pt (report §3).
