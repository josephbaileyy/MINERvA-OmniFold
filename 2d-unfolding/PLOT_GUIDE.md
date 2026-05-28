# Plot Guide — 2D OmniFold study

Reading guide and naming convention for the PNG outputs in
`2d-unfolding/`.

## Naming convention

```
<dataset>_<iter>_<topic>[_<axis>].png
```

| field | values |
|---|---|
| `<dataset>` | `MEFHC` (full 12-playlist), `1A` (single-playlist validation) |
| `<iter>`    | `5iter` (production), `iterscan` (convergence study). Omitted when not applicable. |
| `<topic>`   | `xsec`, `xsec_paper`, `xsec_paper_*_shape`, `pull_full`, `pull_interior`, `pull_interior_shape`, `eff`, `fig13`, `truth_vs_paper`, `reweighter_decomp`, `iterscan`, `minos_fix_bkg_fraction`, `ibu_1d_proj` |
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
- `*_shape` suffix — self-normalized shape `(1/σ_tot)·d²σ/(dpT dp||)`
  computed identically on ours and paper over the same 205 reported bins
  (paper TotalCovariance propagated through the unit-area Jacobian; ndf
  reduced by 1). Cancels the absolute flux scale so what survives is
  Eν-dependent FluxCV shape.
- `minos_fix_bkg_fraction` — side-by-side per-(p_T, p_||) background
  fraction heatmap, pre- vs post-`IsMinosMatchMuon()` patch on 1A.
- `ibu_1d_proj` — IBU run on a 1D projection of the 2D OmniFold inputs,
  overlaid against our 2D OmniFold projected to 1D and the paper TH2D
  projected to 1D. Originally set up to test whether the residual paper
  deficit was method-blind; post-Phase-16 (with the analogous
  input-completeness fix applied to `build_1d_ibu_inputs.py`) confirms
  IBU and 2D OmniFold both reproduce the paper to ≤ 2.5 % and agree
  with one another to ~1.7 %. Produced and stored under
  `ibu_1d_projection/`.

---

## Production plots — full ME FHC, 5-iter

Input: `2d_crossSection_omnifold_MEFHC_5iter.root` (Phase-18.2 pipeline).

The plots below are regenerated from the production output. Earlier
revisions are archived: pre-Phase-16 (which used the no-completeness
formula and showed the 0.572× low-p_|| deficit) under
`archive_pre_phase16/`; Phase-16-postfix and Phase-17/18.0/18.1 era
artifacts under `archive_pre_phase18/`.

| File | Producer | Purpose |
|---|---|---|
| `MEFHC_5iter_xsec_pt_slices.png` | `plot_2d_cross_section.py` | 4×4 grid, one panel per p_T bin (14 filled). x = p_||. OmniFold vs MC truth. |
| `MEFHC_5iter_xsec_pz_slices.png` | `plot_2d_cross_section.py` | 4×4 grid, one panel per p_|| bin. x = p_T. |
| `MEFHC_5iter_xsec_proj_pt.png`   | `plot_2d_cross_section.py` | 1D dσ/dp_T with ratio panel. |
| `MEFHC_5iter_xsec_proj_pz.png`   | `plot_2d_cross_section.py` | 1D dσ/dp_|| with ratio panel. |
| `MEFHC_5iter_xsec_eff_heatmap.png` | `plot_2d_cross_section.py` | 2D `hEff2D` (absolute selection efficiency), paper-Fig.-5 axes. |
| `MEFHC_5iter_xsec_paper_pt_slices.png` | `plot_2d_paper_comparison.py` | p_T grid overlaid with paper MnvTune-v1; per-panel stat-only χ²/ndf. |
| `MEFHC_5iter_xsec_paper_pz_slices.png` | `plot_2d_paper_comparison.py` | Same for p_|| slicing. |
| `MEFHC_5iter_pull_full.png`      | `compare_to_paper_fullcov.py` | Pull map + histogram, all 205 reported bins. |
| `MEFHC_5iter_pull_interior.png`  | `compare_to_paper_interior.py` | Pull map + histogram, 185 strict-interior bins (pt/p|| ≤ tan 20°). |
| `MEFHC_5iter_fig13.png`          | `plot_2d_threeway_fig13.py` | Fig.-13-style overlay: paper / OmniFold / local MC truth. |
| `MEFHC_5iter_eff_fig5.png`       | `plot_efficiency_fig5_style.py` | Fig.-5-style efficiency map (style-only, paper releases no numerical map). |
| `MEFHC_5iter_xsec_paper_pt_slices_shape.png` | `plot_2d_paper_comparison_shape.py` | p_T grid, self-normalized shape vs paper; per-panel χ²/ndf from propagated C_shape diagonal. |
| `MEFHC_5iter_xsec_paper_pz_slices_shape.png` | `plot_2d_paper_comparison_shape.py` | Same for p_|| slicing. |
| `MEFHC_5iter_pull_interior_shape.png` | `plot_2d_paper_comparison_shape.py` | Pull map + histogram for the 185 strict-interior shape comparison. |
| `truth_shape_unweighted_MEFHC_strips.png` | `diagnose_truth_shape_unweighted.py` | Phase-16 truth-shape attribution: local unweighted vs local MnvTune-v1 weighted vs paper MnvTune-v1, all on the canonical mc_truth_denom denominator. The "paper / weighted" curve is flat near 1.0 across p_|| = 1.5–9 GeV/c, ruling out the generator-config / reweighter-chain hypothesis. |
| `ibu_1d_projection/MEFHC_5iter_ibu_1d_proj_pt.png` | `ibu_1d_projection/plot_ibu_1d_proj_vs_omnifold.py` | 3-way overlay of dσ/dp_T: IBU on a 1D projection of the 2D inputs vs our 2D OmniFold projected to 1D vs paper TH2D projected to 1D. IBU and OmniFold overlap (method-blind). |
| `ibu_1d_projection/MEFHC_5iter_ibu_1d_proj_pz.png` | `ibu_1d_projection/plot_ibu_1d_proj_vs_omnifold.py` | Same for p_||. |
| `uq/universe_stage2_MEFHC_full/MEFHC_fig6_7_uncertainty_pz.png` | `uq/plot_uncertainty_fig6_7_style.py` | Paper-Fig.-6-style fractional uncertainty vs muon longitudinal momentum, using exact 2D covariance projection and grouped Flux/Models/Normalization/Statistical/Hadronic response/Muon reconstruction components. |
| `uq/universe_stage2_MEFHC_full/MEFHC_fig6_7_uncertainty_pt.png` | `uq/plot_uncertainty_fig6_7_style.py` | Paper-Fig.-7-style fractional uncertainty vs muon transverse momentum, from the same grouped covariance budget. |
| `uq/universe_stage2_MEFHC_full/MEFHC_fig6_7_uncertainty_with_ml_pt.png` | `uq/plot_uncertainty_fig6_7_style.py --include-ml always` | Same p_T view with the small ML component forced into the legend. |

---

## 1A / standing diagnostics (independent of unfold output)

| File | Producer | Purpose |
|---|---|---|
| `1A_iterscan_convergence.png` | `plot_iter_convergence.py` | Three-panel iter scan summary (hUnfold2D integral, total xsec, per-bin RMS vs 10-iter). Justifies production 5-iter. Independent of Phase 16 — same shape post-fix because the iter-stability argument is about convergence of the OmniFold weights, not the absolute scale. |
| `MEFHC_5iter_minos_fix_bkg_fraction.png` | `plot_minos_fix_bkg_fraction.py` | 1A pre-/post-`IsMinosMatchMuon()` patch background-fraction heatmap. Documents Phase 11 (10% → 0.35% bkg-fraction reduction) which is C++-event-loop-side and unaffected by Phase 16. |
| `compare_flux_to_paper_2019.png` | `compare_flux_to_paper_2019.py` | Phase 15 paper-era flux comparison (paper / local ratio across 1.5–10 GeV). Documents the flux-CV ruleout. |

---

## Notes for adding new plots

- Reuse the convention. If `--prefix` / `--out` arguments are exposed,
  pass `MEFHC_5iter_<topic>` (or `1A_<topic>`) so the files self-sort
  alphabetically in `ls`.
- Avoid the legacy `2d_xsec_…`, `compare_<dataset>_paper_…`,
  `<topic>_<dataset>_…` orderings — they predate this convention and
  shouldn't be re-introduced.
- One-shot investigation plots that aren't part of the canonical set
  belong in an `archive_*/` subdirectory rather than the top of
  `2d-unfolding/`.
