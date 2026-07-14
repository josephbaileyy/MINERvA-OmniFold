# Figures guide

All PNGs rendered at 200 dpi from the analysis note's vector figures; the note
(`analysis-note.pdf`) contains each figure with its full caption — search the
filename stem there for exact wording and numbers. "Slide" refers to
`outline.md` numbering. B# = backup slide.

## `figures/` — cleared for use anywhere

| File | What it shows | Suggested slide |
|---|---|---|
| `minerva_unfolding_landscape.png` | Published MINERvA measurements arranged by dimensionality — the motivation figure | 3 |
| `migration_resolution.png` | Detector migration/resolution for the unfolded observables | Act 2 support or B3 |
| `MEFHC_5iter_fig13.png` | **Money figure**: unbinned unfold binned into the published 2D d²σ/(dp_T dp_∥) layout vs published points | 8 |
| `MEFHC_5iter_xsec_paper_pt_slices.png` | Same reproduction shown as p_T slices | 8 alt |
| `MEFHC_5iter_xsec_paper_pz_slices.png` | Same reproduction shown as p_∥ slices | 8 alt |
| `MEFHC_5iter_xsec_proj_pt.png` | 1D p_T projection of the reproduced cross section | 8 alt |
| `MEFHC_5iter_xsec_proj_pz.png` | 1D p_∥ projection of the reproduced cross section | 8 alt |
| `MEFHC_5iter_pull_full.png` | Per-bin pulls, OmniFold vs published result | 9 |
| `MEFHC_5iter_xsec_eff_heatmap.png` | Efficiency map entering the cross-section extraction | B2 |
| `MEFHC_fig6_7_uncertainty_pt.png` | Independently rebuilt 2D uncertainty budget vs published, p_T view (**cleared**) | 10 |
| `MEFHC_fig6_7_uncertainty_pz.png` | Same, p_∥ view (**cleared**) | 10 |
| `eavail_marginal_vs_paper_pull_full.png` | Higher-D unfold marginalized back to 2D vs published — the built-in anchor | 11 |
| `eavail_spectrum.png` | Unfolded E_avail spectrum (new axis opened) | 12 |
| `mode_decomp_eavail.png` | Interaction-mode decomposition of E_avail — 2p2h filling the QE–Δ dip | 12 |
| `compare_mec_eavail.png` | 2p2h/MEC model variations vs the unfolded E_avail spectrum | 12 alt |
| `model_comp_projections.png` | Four-generator comparison, projected views (central values) | 13 support |
| `model_comp_ratio_maps.png` | Four-generator ratio maps (central values) | 13 support |
| `excess_eavail_W.png` | The unexplained excess localizing in the (E_avail, W) plane — shape-level only, no significance | 13 |
| `q3_excess_projection.png` | The excess seen in the q3 projection | 13 support |
| `pet_event_displays.png` | Calorimeter-cluster point-cloud event displays | 14 |
| `fps_acceptance_MEFHC.png` | Acceptance across the full (uncut) muon phase space | 14 |
| `classifier_calibration.png` | Classifier calibration check | B3 |
| `negweight_ratio_2d.png` | Background-subtraction (negative-weight) validation | B2 |
| `seedscan_band_pt.png` | ML seed-scan variability band, p_T (2D, cleared) | B5 |
| `seedscan_spread_2d.png` | ML seed-scan spread across the 2D plane (cleared) | B5 |
| `uq_corr_2d.png` | 2D covariance correlation structure (cleared) | B6 |
| `uq_spread_2d.png` | 2D per-bin uncertainty spread (cleared) | B6 |
| `control_corner.png` | 5D control corner plot (central values) | B8 |
| `control_plots.png` | 5D control distributions (central values) | B8 |
| `pet_cardinality.png` / `pet_cardinality_real.png` / `pet_cardinality_withremnant.png` | Point-cloud cardinality distributions (variants) | B9 |
| `pet_cloud_projection_validation.png` | Truth-cloud post-hoc observable projection, validation | B9 |
| `pet_cloud_projection_xsec.png` | Truth-cloud projected cross section | B9 |
| `pet_vs_gbdt.png` / `pet_vs_gbdt_absolute.png` | PET vs GBDT **central-value** comparison (fine; precision comparison is quarantined) | B9 |
| `fps_pilot_compare_MEFHC.png` | Full-phase-space pilot vs restricted phase space (label preliminary) | B10 |
| `fps_prior_envelope_MEFHC.png` | Prior-swap envelope for the FPS extrapolation (label preliminary) | B10 |

## `figures-quarantined-backup-only/` — backup slides only, tagged "uncertainty under regeneration — preliminary"

These embody N-D uncertainty budgets, covariance-based significances, or
precision comparisons currently being regenerated. Never on main slides; no
numbers from them may be quoted.

| File | What it shows |
|---|---|
| `eavailW_band.png` | (E_avail, W) spectrum with quarantined uncertainty band |
| `uq_universe_3d_band_eavail.png` / `uq_universe_3d_band_pt.png` | 3D systematic bands |
| `generators_vs_unfolded_band.png` | Generator comparison against quarantined band |
| `tension_spectrum.png` / `tension_chi2_map.png` / `tension_mode_maps.png` | Covariance-based data–generator tension/χ² maps |
| `compare_3d_fullcov.png` | Full-covariance 3D comparison |
| `ascencio_fullcov_compare.png` | Full-covariance comparison to the published low-q3 (Ascencio) result |
| `pet_vs_gbdt_uncertainty_overlay.png` / `pet_vs_gbdt_uncertainty_ratiomap.png` | PET-vs-GBDT precision comparison |
