# Plot Guide — 2D OmniFold study

Reading guide and naming convention for the PNG outputs in
`2d-unfolding/`.

## Naming convention

```
<dataset>_<iter>_<topic>[_<axis>].png
```

| field | values |
|---|---|
| `<dataset>` | `MEHFC` (full 12-playlist), `1A` (single-playlist validation) |
| `<iter>`    | `5iter` (production), `iterscan` (convergence study). Omitted when not applicable. |
| `<topic>`   | `xsec`, `xsec_paper`, `pull_full`, `pull_interior`, `eff`, `fig13`, `truth_vs_paper`, `reweighter_decomp`, `iterscan` |
| `<axis>`    | `pt_slices`, `pz_slices`, `proj_pt`, `proj_pz`, `heatmap`, `strips` |

Topic glossary:

- `xsec` — our own d²σ slices/projections from `plot_2d_cross_section.py`.
- `xsec_paper` — same slices overlaid with the paper's MnvTune-v1 from
  `plot_2d_paper_comparison.py`.
- `pull_full` / `pull_interior` — per-bin pull maps + histograms vs paper
  (full 205 reported bins / 185 strict-interior bins).
- `eff` — efficiency maps; `eff_heatmap` is the standard `hEff2D`,
  `eff_fig5` is the Fig.-5-style remake.
- `fig13` — Fig.-13-style three-way overlay (paper data, OmniFold,
  local MC truth).
- `truth_vs_paper` — paper Tune-v1 model vs local `hTruth2D` shape diagnostic.
- `reweighter_decomp` — per-reweighter dump showing which truth-side
  reweighter carries the low-p_|| shape.

---

## Production plots — full ME FHC, 5-iter

Input: `2d_crossSection_omnifold_MEHFC_5iter.root`.

| File | Producer | Purpose |
|---|---|---|
| `MEHFC_5iter_xsec_pt_slices.png` | `plot_2d_cross_section.py` | 4×4 grid, one panel per p_T bin (14 filled). x = p_||. OmniFold vs MC truth. |
| `MEHFC_5iter_xsec_pz_slices.png` | `plot_2d_cross_section.py` | 4×4 grid, one panel per p_|| bin. x = p_T. |
| `MEHFC_5iter_xsec_proj_pt.png`   | `plot_2d_cross_section.py` | 1D dσ/dp_T with ratio panel. |
| `MEHFC_5iter_xsec_proj_pz.png`   | `plot_2d_cross_section.py` | 1D dσ/dp_|| with ratio panel. |
| `MEHFC_5iter_xsec_eff_heatmap.png` | `plot_2d_cross_section.py` | 2D `hEff2D`, p_|| on x, p_T on y (paper Fig. 5 axes). |
| `MEHFC_5iter_xsec_paper_pt_slices.png` | `plot_2d_paper_comparison.py` | p_T grid overlaid with paper MnvTune-v1; per-panel stat-only χ²/ndf. |
| `MEHFC_5iter_xsec_paper_pz_slices.png` | `plot_2d_paper_comparison.py` | Same for p_|| slicing. |
| `MEHFC_5iter_pull_full.png`      | `compare_to_paper_fullcov.py` | Pull map + histogram, all 205 reported bins. |
| `MEHFC_5iter_pull_interior.png`  | `compare_to_paper_interior.py` | Pull map + histogram, 185 strict-interior bins (pt/p|| ≤ tan 20°). |
| `MEHFC_5iter_fig13.png`          | `plot_2d_threeway_fig13.py` | Fig.-13-style overlay: paper / OmniFold / local MC truth. |
| `MEHFC_5iter_eff_fig5.png`       | `plot_efficiency_fig5_style.py` | Fig.-5-style efficiency map (style-only, paper releases no numerical map). |
| `MEHFC_5iter_truth_vs_paper_strips.png` | `diagnose_truth_shape_vs_paper.py` | Paper Tune-v1 / local MC truth shape per p_|| strip. |

Key diagnostics for the residual low-p_|| deficit: `pull_interior`,
`eff_heatmap`, `truth_vs_paper_strips`, and the first p_|| bin in the
`xsec_paper_pt_slices` panels.

---

## 1A diagnostics

| File | Producer | Purpose |
|---|---|---|
| `1A_iterscan_convergence.png`     | `plot_iter_convergence.py`   | Three-panel iter scan summary (hUnfold2D integral, total xsec, per-bin RMS vs 10-iter). Justifies production 5-iter. |
| `1A_reweighter_decomp_strips.png` | `decompose_truth_weights.py` | Per-reweighter truth-weight decomposition. Shows `FluxAndCV` carries the low-p_|| shape; GENIE/2p2h/RPA/MINOSEff are flat. |

---

## Notes for adding new plots

- Reuse the convention. If `--prefix` / `--out` arguments are exposed,
  pass `MEHFC_5iter_<topic>` (or `1A_<topic>`) so the files self-sort
  alphabetically in `ls`.
- Avoid the legacy `2d_xsec_…`, `compare_<dataset>_paper_…`,
  `<topic>_<dataset>_…` orderings — they predate this convention and
  shouldn't be re-introduced.
- One-shot investigation plots that aren't part of the canonical set
  belong in an `archive_*/` subdirectory rather than the top of
  `2d-unfolding/`.
