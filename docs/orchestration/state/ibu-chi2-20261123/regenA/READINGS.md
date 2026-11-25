# regenA readings: comparisons with the published result, our pT edges vs the paper's

For journal-editor (the note lane). Numbers only; the note's wording is Joseph's. Inputs and controls are in
[`README.md`](README.md).
- **OLD:** E_R central on our pT edges (0.07 / 0.33 / 0.47), the committed product. It reproduces RE-2 part C's receipts
  exactly.
- **Paper's edges:** E_R on the paper's pT edges (0.075 / 0.325 / 0.475), from Tier 1. It is the same unfold: the
  column sums agree to 2e-13.

The analysis grid stays ours (option (i)). These are the comparison numbers only.

| quantity (note macro / place, where known) | OLD | paper's edges | source |
|---|---|---|---|
| χ² vs published, TotalCovariance, 205 cells (`\chiPaper`) | 465.42 / 205 = 2.270 | **434.89 / 205 = 2.121** | P1a log |
| per-bin pull mean / RMS (`\pullMean`, `\pullRMS`) | 0.060 / 0.535 | **0.133 / 0.513** | P1a log |
| diagonal-only χ²/ndf | 0.290 | 0.281 | P4 tension_report |
| interior χ², 185 cells | 425.09 / 185 = 2.298 | **393.48 / 185 = 2.127** | P2 log |
| shape χ², 205 cells, total covariance (`sec3_twod.tex:34`, "≈ 465") | 450.21 / 204 = 2.207 | **426.21 / 204 = 2.089** | P3 log |
| shape χ², 185 cells, total covariance | 472.60 / 184 = 2.568 | 384.96 / 184 = 2.092 | P3 log |
| χ²_norm (tension) | 0.04 | 0.04 | P4 |
| χ²_shape (tension) | 465.23 (2.269) | 434.71 (2.121) | P4 |
| σ_tot(ours)/σ_tot(paper), reported cells | 1.0077 | 1.0081 | P4 |
| ours vs MINERvA Tune v1, χ² | 6424.80 (31.34) | 5902.38 (28.79) | P6 receipt |
| published data vs Tune v1, χ² (no input of ours) | 6773.05 | 6773.05 | P6 receipt |
| median per-bin ratio, ours / published | 1.0054 | 1.0075 | P7 receipt |
| bins within 5 / 10 / 20 % | 178 / 195 / 203 (86.8 / 95.1 / 99.0 %) | 175 / 195 / 203 (85.4 / 95.1 / 99.0 %) | P7 receipt |
| strip contrast, 205 cells: R_low, R_high, n_σ | 1.0107, 1.0417, −0.383 | 1.0107, 1.0417, −0.383 | P8b receipt |
| strip contrast, 185 cells: R_low, n_σ | 1.0040, −0.452 | 1.0119, −0.355 | P8b receipt |
| IBU (REF-C2C1 c2) χ²/205 at K = 10 (`c2c1-dibu`) | 1.027 | **0.538** | tier1 |
| E_R vs published, D_ER (`c2c1-der`) | 2.270 | 2.121 | tier1 |
| signed-target IBU χ²/205 at K = 10 | 0.961 | 0.474 | tier1/signed |

Figures on the paper's edges: `out/e/MEFHC_5iter_fig13.{png,pdf}`, `out/e/MEFHC_5iter_pull_full.{png,pdf}`,
`out/e/MEFHC_5iter_pull_interior.{png,pdf}`, `out/e/model_comp_*.{png,pdf}` and `out/e/tension_*.{png,pdf}`. These are
the producers' own styling, not the note's restyled versions. The OLD twins are in `out/old/`.

**Not in A (they need the covariance; part B, waiting on Joseph's path):**
- `\chiCombined` (part C's chi2_std);
- ours-only χ²;
- our stat covariance vs the published StatOnly;
- the Figs. 6–7 uncertainty bands, and the Figs. 6–7 "closer to the published" takeaway (P10).
