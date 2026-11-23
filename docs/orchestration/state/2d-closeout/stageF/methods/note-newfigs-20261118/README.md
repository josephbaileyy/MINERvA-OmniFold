# Two new note figures from committed records (2026-11-18)

**By** cov2d, at the director's request of 2026-11-18. These are two of the readability read's five additions, which Joseph approved:
1. the sixteen-cell headline figure;
2. the run-period graphic.

Both are drawn locally from committed records, at 0 node-h, with no unfold and no new computation.
- Each producer refuses any input whose sha256 differs from its pin.
- After drawing, each producer reads the plotted numbers back from the figure's own artists and asserts that they equal the record's (identity check). It writes nothing if any check fails.
- Both producers use the note's print style (`note_print_style.apply()`, the paper's rcParams).
- The headline figure draws this work in the note palette's red (`note_palette.style("this_work")`), with no legend: it is a single series, which the caption describes (the read of r1 found a "This work" legend could read as a validated measurement).
- The run-period graphic uses black and greys with distinct markers. Its series are run periods and classes, not palette identities, and no colour should read as a generator.

## Run (from this directory)

    python3 -I make_fig_fived16_headline.py      # fived16_headline.pdf, .png (preview), fived16_headline_values.json
    python3 -I make_fig_runperiod_steps.py       # runperiod_steps.pdf, .png (preview), runperiod_steps_values.json

- The PDFs are written without a creation date, so two runs give byte-identical files. This was checked with matplotlib 3.10.1 (miniconda python3).
- The PNG previews are gitignored.
- `docs/analysis-note/make_figures.sh` installs both PDFs into `docs/analysis-note/figures/` by a digest-checked copy, in the "note-newfigs-20261118" block.

## Inputs (each pinned in its producer, and the same pins `make_values_fived16.py` uses)

| figure | record | sha256 | what is read |
|---|---|---|---|
| 1 | `measurement-paper/5d-community-20261024/fd/with-cpl/data-product/fd_data_product_cpl.json` | `d6752d2c` | `f` (cell integrals, cm²/nucleon); `matrices.C_total_plus_C_resp_plus_C_PL5D` (the reported covariance); `cells[].box`; checked against `relative_sigma` |
| 2a | `2d-closeout/stageF/methods/methods-short-20261109/lrows-g/g4-runperiod/runperiod_values.json` | `f63074b1` | `panels.PB/PC.reco_ratio`, `reco_data_stat`, `reco_step_pct`; `pz_edges_GeV` |
| 2b | `measurement-paper/5d-community-20261024/fd/receipts-rpd/run/readout/fd_rpd.json` | `c0b06cfd` | `R1.t`, `R1.sigma`, `R1.classes`, `R1.tbar`; `R1.h` and `R1.sigma_h` for the class recomputation |

## What each figure shows, and its checks

**(1) `fived16_headline.pdf`**
- **What it shows:**
  - each reported cell's integrated cross section f, in units of 10⁻⁴⁰ cm²/nucleon (the unit of tab:fived16-cells), on a log axis;
  - error bars of sqrt(diag) of the reported covariance C_total + C_resp + C_PL,5D;
  - cells R00–R15 in order, grouped by their four (p_T, p_∥) boxes;
  - a three-row table under the axis giving each cell's E_avail, q3 and W range, where "any" means the whole axis.
- **Checks:**
  - the record's pin;
  - sqrt(diag)/f equals the record's `relative_sigma` of the reported covariance (to 1e-12);
  - each group of four cells shares one (p_T, p_∥) box;
  - the plotted points equal f;
  - the half-lengths of the bars equal sqrt(diag), and the bars are centred on f (to 1e-12).
- **Generators:** no generator predictions are drawn. The request made them optional, and this figure is the data product alone.

**(2) `runperiod_steps.pdf`**
- **(a)** The reconstruction-level ratio of the 1G–1M and 1N–1P groups to 1A–1F, R_X/R_A with R_X = (D_X − B_X)/S_X per p_∥ bin summed over p_T, with the data statistical uncertainty.
  - Every playlist's simulation is scaled to its data POT, as in the G4 record's README.
  - Each group's step is in the legend. It is the record's q(8–15 GeV/c)/q(1.5–8 GeV/c) − 1 of the integrated yields: +5.99 % and +1.26 %, the values sec_systematics prints as `rp-pb-reco` and `rp-pc-reco`.
  - Points of the two groups are offset by ±1.5 % in p_∥ (multiplicatively) for legibility.
- **(b)** Each playlist's own p_∥ step t_X across 8 GeV/c, from its five-observable unfold, against the exposure-weighted 1A–1F reference, leaving the playlist out when it is one of 1A–1F.
  - The bars are σ_X: the replica SD, with T's MC variance in quadrature (FD-RPD-DECLARATION.md sec. 5, R1).
  - Each point is marked by its class.
  - The dashed line is t̄/2, half the recombined 1G/1L/1M step.
  - Only the classes print in the note (sec:fived16-pl, `rpd-r1-*`). t_X and σ_X are plotted points and are not printed as numbers.
- **Checks:**
  - both records' pins;
  - each class recomputed by the declaration's rule (FREE if |t_X| ≤ 2σ_X; CARRIES if h_X ≥ 2σ_h,X; else PARTIAL) equals the record's;
  - h_X = t_X − t̄/2 (to 1e-12);
  - every plotted point and bar equals the record's.
- **Levels:** panel (a) is reconstruction level, from the 2D record. Panel (b) is unfolded, from the five-observable per-playlist unfolds. The caption must keep the two levels apart.

## Outputs

| file | sha256 |
|---|---|
| `make_fig_fived16_headline.py` | see the commit |
| `make_fig_runperiod_steps.py` | see the commit |
| `fived16_headline.pdf` | `69833f108f946b9b51c6795b10f1bdce941971ebf683482623735728e3059e6f` |
| `runperiod_steps.pdf` | `1088ae36889bffeea33182c3940bbf1ace4032dab1ff06e91000443618c12606` |

- **Caption drafts:** `caption_drafts.tex`. The section owners write the final captions.
- **Figure-plus-caption read:** Grok and Gemini, in `~/codex-reports/note-measurement/reads/cv-newfigs-r1/`.
