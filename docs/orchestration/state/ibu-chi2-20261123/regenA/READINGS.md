# regenA readings: comparisons with the published result, our pT edges vs the paper's

For journal-editor (the note lane). Numbers only; the note's wording is Joseph's. Inputs and controls are in
[`README.md`](README.md).
- **OLD:** E_R central on our pT edges (0.07 / 0.33 / 0.47), the committed product. It reproduces RE-2 part C's receipts
  exactly.
- **Paper's edges:** E_R on the paper's pT edges (0.075 / 0.325 / 0.475), from Tier 1. It is the same unfold: the
  column sums agree to 2e-13.

The analysis grid stays ours (option (i)).

**The "where printed" column was checked by grep against the note's source in this branch's tree (head 7713ce6c, main merged)**, for the
macro definitions in `docs/analysis-note/values.tex` and for literals in `docs/analysis-note/sec3_twod.tex`. "Not
printed" means no grep match in sec3_twod.tex, values.tex or appC_supplementary.tex. A first version of this table
mapped sec3_twod.tex:34 to P3's shape χ²; journal-editor caught it, and that sentence is P4's decomposition.

| quantity | where printed in the note | OLD | paper's edges | source |
|---|---|---|---|---|
| χ²/205 vs published, TotalCovariance | `\chiPaper`, values.tex:47 (2.27) | 465.42 / 205 = 2.270 | **434.89 / 205 = 2.121** | P1a log |
| per-bin pull mean | `\pullMean`, values.tex:18 (0.060) | 0.060 | **0.133** | P1a log |
| per-bin pull RMS | `\pullRMS` / `\pullRMSr`, values.tex:19–20 (0.535 / 0.54) | 0.535 | **0.513** | P1a log |
| diagonal-only χ²/ndf | sec3_twod.tex:24 literal "0.29" | 0.290 | **0.281** | P4 tension_report |
| χ²_norm (tension decomposition) | sec3_twod.tex:34 "χ²_norm = 0.04" | 0.04 | 0.04 | P4 tension_report |
| χ²_shape (tension decomposition) | sec3_twod.tex:34 "χ²_shape ≃ 465" | 465.23 (2.269) | **434.71 (2.121), ≃ 435** | P4 tension_report |
| median per-bin ratio, ours / published | `\medianBinRatio`, values.tex:14 (1.005) | 1.0054 | **1.0075** | P7 receipt `results.median_bin_ratio` |
| percent of bins within 5 % | `\binsFive`, values.tex:15 (86.8) | 86.8 (178) | **85.4 (175)** | P7 `results.within_5_percent` |
| within 10 % | `\binsTen`, values.tex:16 (95.1) | 95.1 (195) | 95.1 (195) | P7 `results.within_10_percent` |
| within 20 % | `\binsTwenty`, values.tex:17 (99.0) | 99.0 (203) | 99.0 (203) | P7 `results.within_20_percent` |
| integral ratio, ours / published, reported cells | `\ratioTot`, values.tex:10 (1.010) | 1.00978 | 1.00978 | P7 `headline_totals_oi130.values.ratio_integrals_reported` |
| bare-sum ratio, ours / published | not printed (`\ratioTot` uses the integrals) | 1.0077 | 1.0081 | P5 report, P7 `ratio_bare_sums` |
| Tune v1 / published rate | sec3_twod.tex:11 "0.91" | 0.9124 | 0.9124 (no input of ours) | P5 model_comp_report |
| IBU (REF-C2C1 c2) χ²/205, K = 10 | `\fvval{c2c1-dibu}`, sec3_twod.tex:36 and appC_supplementary.tex:44 | 1.027 | **0.538** | tier1 |
| E_R vs published, D_ER | `\fvval{c2c1-der}`, same places | 2.270 | 2.121 | tier1 |
| signed-target IBU χ²/205, K = 10 | not printed | 0.961 | 0.474 | tier1/signed |
| interior χ², 185 cells | not printed | 425.09 / 185 = 2.298 | 393.48 / 185 = 2.127 | P2 log |
| unit-area shape χ², 205 cells (normalize_xsec_shape) | not printed (a different definition from line 34's) | 450.21 / 204 = 2.207 | 426.21 / 204 = 2.089 | P3 log |
| unit-area shape χ², 185 cells | not printed | 472.60 / 184 = 2.568 | 384.96 / 184 = 2.092 | P3 log |
| ours vs Tune v1, χ² | not printed | 6424.80 (31.34) | 5902.38 (28.79) | P6 receipt |
| published data vs Tune v1, χ² | not printed | 6773.05 | 6773.05 | P6 receipt |
| strip contrast, 205 cells: R_low, R_high, n_σ | not printed | 1.0107, 1.0417, −0.383 | 1.0107, 1.0417, −0.383 | P8b receipt |
| strip contrast, 185 cells: R_low, n_σ | not printed | 1.0040, −0.452 | 1.0119, −0.355 | P8b receipt |

## sec3_twod.tex:11 literals not produced by regenA

These literals are on the same line as the 0.91 rate above:
- "Per bin, the OmniFold projections agree with the published result to within 2%, except at the edges of the phase
  space";
- "the ratio rises from 0.97 in the lowest pT bin to 1.04 in the highest";
- "is 1.06 and 0.93 in the two highest p‖ bins".

They are ratios of the 1D projections, ours over published, which `fig:xsec` draws.

**Producer:** `2d-unfolding/compare_to_models.py`'s `project()` (P5), the same projection that P5's
`model_comp_projections` figure uses. P5 draws these projections but **does not print their per-bin ratios**, so no regenA
output holds them. Binding them needs a readout of `project()` on OLD and E: ours with our axis, published with the
release axis, then the per-bin ratio. That is an **A-type** product (central values only, 0 node-h), but it is
**not declared**. It would need an amendment and the director's GO. Its OLD run must reproduce the note's 0.97, 1.04,
1.06, 0.93 and the 2 % bound at the note's rounding.

"In every pT and p‖ slice, the unfolded spectrum is closer to the published cross section than to the prior" (the same
line): producer `check_fig67_takeaway.py` (note-figpass tools, `fig67_takeaway.json`). It is **part B (P10)**, because
its projections come from `plot_uncertainty_fig6_7_style.py`, which needs the covariance inputs.

## Figures

On the paper's edges: `out/e/MEFHC_5iter_fig13.{png,pdf}`, `out/e/MEFHC_5iter_pull_full.{png,pdf}`,
`out/e/MEFHC_5iter_pull_interior.{png,pdf}`, `out/e/model_comp_*.{png,pdf}` and `out/e/tension_*.{png,pdf}`. These are
the producers' own styling, not the note's restyled versions. The OLD twins are in `out/old/`.

## Not in A (part B, waiting on Joseph's path)

These need the covariance:
- `\chiCombined` (part C's chi2_std);
- ours-only χ²;
- our stat covariance vs the published StatOnly;
- the Figs. 6–7 bands, and the takeaway above.
