# Plot Guide — 2D OmniFold study

Reading guide for the PNG outputs.

- **Production** plots use the full ME FHC stats (`_MEHFC_5iter_`).
- **1A validation** plots (`_1A_corrected_interactive_5iter_*` /
  `compare_1A_corrected_interactive_*`) use playlist 1A only (~8.5 % stats)
  and exist to show the corrected pipeline reproduces 1A closure and
  matches the MEHFC result shape.
- **Closure** plots (`closure_2d_1A_corrected_*`) use MC-as-data on 1A.
- **Iter scan** plot (`iter_convergence_1A_corrected.png`) uses the 1A
  iteration scan.

---

## Production d²σ plots — `plot_2d_cross_section.py`

Input: `2d_crossSection_omnifold_MEHFC_5iter.root`

| File | Purpose |
|---|---|
| `2d_xsec_MEHFC_5iter_pt_slices.png` | 4×4 grid, one panel per p_T bin (14 filled). x = p_||. OmniFold vs MC truth. |
| `2d_xsec_MEHFC_5iter_pz_slices.png` | 4×4 grid, one panel per p_|| bin. x = p_T. |
| `2d_xsec_MEHFC_5iter_projection_pt.png` | 1D dσ/dp_T with ratio panel. |
| `2d_xsec_MEHFC_5iter_projection_pz.png` | 1D dσ/dp_|| with ratio panel. |
| `2d_xsec_MEHFC_5iter_efficiency.png` | 2D `hEff2D` (p_|| on x-axis, p_T on y-axis to match paper Fig. 5). |

Key diagnostic for the low-p_|| deficit: the efficiency panel, and the
p_T projection's first p_|| bin in the slice plots.

---

## Paper comparison — `plot_2d_paper_comparison.py`

Input: production ROOT + paper ancillary (`minerva_paper_anc/`).

| File | Purpose |
|---|---|
| `2d_paper_compare_MEHFC_5iter_pt_slices.png` | Same p_T grid, overlaid with MINERvA Tune v1. Per-panel stat-only χ²/ndf annotated. |
| `2d_paper_compare_MEHFC_5iter_pz_slices.png` | Same for p_|| slicing. |

## Pull summaries — `compare_to_paper_{fullcov,interior}.py`

| File | Bins | χ²/ndf |
|---|---|---|
| `compare_MEHFC_paper_pull_summary.png` | all 205 reported | 1089.7 |
| `compare_MEHFC_paper_interior.png` | 185 strict-interior (pt/p|| ≤ tan 20°) | 17.0 |

Left panel: (ours − paper) / σ_total heatmap. Right: pull histogram.
The strict-interior plot is the physics-meaningful comparison — it masks
the diagonal phase-space turnover where the paper doesn't report.

## 1A validation plots — same scripts

| File | Purpose |
|---|---|
| `2d_xsec_1A_corrected_interactive_5iter_*.png` | 1A-only counterparts of the 5 production plots. |
| `2d_paper_compare_1A_corrected_interactive_5iter_*.png` | 1A-only paper-comparison slice grids. |
| `compare_1A_corrected_interactive_paper_pull_summary.png` | 1A full-cov pulls. |
| `compare_1A_corrected_interactive_paper_interior.png` | 1A strict-interior pulls (χ²/ndf = 19.5). |

## Closure — `plot_closure_2d.py`

Input: `2d_crossSection_omnifold_1A_corrected_5iter_closure.root`
(MC-as-data on 1A). Ratio formula in the script computes
`hUnfold2D / hTruth2D` directly (both at data POT).

| File | Purpose |
|---|---|
| `closure_2d_1A_corrected_ratio_heatmap.png` | `hUnfold2D / hTruth2D` on (p_T, p_||) grid. |
| `closure_2d_1A_corrected_ratio_hist.png` | Ratio histogram with stats box. |
| `closure_2d_1A_corrected_projection_pt.png` | 1D p_T projection, unfolded vs truth. |
| `closure_2d_1A_corrected_projection_pz.png` | Same for p_||. |

In-sample closure is trivial (pseudo-data = MC reco → step-2 returns
identity per event → unfold ≡ truth). Current actual: median 1.0000,
RMS 0.0000, 100 % within 5 %. A more informative test would hold out
half the MC; this mode does not.

## Iteration convergence — `plot_iter_convergence.py`

Input: `2d_crossSection_omnifold_1A_corrected_{1,3,5,8,10}iter.root`.

| File | Purpose |
|---|---|
| `iter_convergence_1A_corrected.png` | 3 summary panels: hUnfold2D integral, total xsec, per-bin relative RMS vs 10-iter. |

Justifies production 5-iter (0.08 % bias vs 10-iter, saves ~17 h wall time).

## Investigation plots

| File | Purpose |
|---|---|
| `eff_2d_compare.png` | 2D efficiency heatmap pair: 1A-corrected vs MEHFC-corrected. |
| `eff_vs_pz.png` | Mean `hEff2D` over p_T per p_|| strip. Shows efficiency rising from 0.56 at p_||=1.5–2 to ~0.89 plateau — tracks the low-p_|| deficit gradient. |
