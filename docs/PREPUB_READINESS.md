# Pre-publication readiness — methodology cross-checks

Single referee-facing index of the validation/robustness studies behind the MINERvA ME FHC
OmniFold cross sections (2D d²σ/dpTdp∥, 3D +E_avail, 4D +q3). Status as of 2026-06-04.
Pointers: `LITERATURE_NOTES.md` (§A audit, §C methodology), `nd-unfolding/ND_OMNIFOLD_*.md`,
`3d-unfolding/uq_3d/`, memory `nd_followon_campaign` / `nd_unfold_io_bound_bank`.

| # | Cross-check | Status | Result / location |
|---|---|---|---|
| 1 | **Unbinned goodness-of-fit** (C2ST) | ✅ done | prior data/MC separable z=33; unfolded indistinguishable AUC 0.501, p=0.17 → PASS. `nd-unfolding/unbinned_gof.py` |
| 2 | **Train/test-split ML band** + ensemble-mean CV | ✅ done (3D); 4D in flight | split ML band 1.24× pure-seed; combined budget +0.04% (sub-dominant). `uq_cov_mlsplit_3d.root`, `ensemble_cv_3d.root` |
| 3 | **Unified-throw vs block-sum** (covariance construction) | superposition probe done; full throw in flight | jitter-null: cross-terms at the jitter floor (0.8×) → no clean nonlinearity → leans block-sum-valid. Full 160-throw `unified_throw.py` is the definitive test |
| 4 | **q3 as 4th axis** (more dimensions, motivated) | ✅ done + validated | 4D unfold: completeness, exact Jacobian identity, recovers 3D <2%, 2D-marginal anchors paper. Systematic + combined 4D budget in flight (`uq_4d/`) |
| 5 | **NN vs GBDT cross-check** | ✅ done | keras-MLP reproduces GBDT within ML band (ratio 1.008). `omnifold_nn_core.py` |
| 6 | **Point-cloud (PET) track** | pipeline wired; reco-cloud source fix required | vendored MLP+PET engine runs, but the first real-cloud attempt used `ExtraEnergyClusters_*`, which is mostly/fully empty. Do not report PET-vs-GBDT until the event loop reads the real non-muon recoil clusters and the comparison is rerun. `minerva_pet_dataloader.py`, `dump_pointcloud_inputs.py` |
| 7 | **Generator comparison** (full-cov χ²) | ✅ done (3D); 4D blocked | Tune-v1 best, GiBUU worst; robust to split-ML band. 4D needs generator-sample regen (samples cleaned) |
| 8 | **Ascencio low-q3 bin-identical overlay** | machinery done; **blocked on data** | our-side spectra + χ² path ready; needs the 2110.13372 release (HepData/member-gated). `compare_ascencio_q3.py --ascencio-2d` |
| 9 | **Flux↔muon-E covariance** rederivation | ✅ done | ρ≈0.87–0.90, rank-2 block. memory `flux_muonE_covariance_rederivation` |
| 10 | **Covariance rank/stat-block** audit | ✅ done | rank gap is the stat block, not missing bands. memory `rank_gap_is_stat_block` |

## Open items before submission
- **Finish the 4D combined budget** (C_syst+C_stat+C_ML) — chained, draining (`uq_4d/`).
- **Full unified-throw covariance** — running; will replace the jitter-limited superposition probe as the definitive block-sum validation.
- **PET vs GBDT** — first fix the reco-cluster source (`cluster_energy`, positions, and muon-track filtering), then quantify whether the point cloud adds information beyond (pT,p∥,E_avail,q3) scalars.
- **Ascencio overlay** — drop in the data file (external/member access).
- **q3 generator comparison** — needs GENIE/NuWro/GiBUU sample regen (event samples were cleaned).

## Methodology stance (for the response-to-referees)
- Covariance is block-summed (`C_syst+C_stat+C_ML`); the unified-throw study tests the
  underlying linearity assumption directly (not just asserts it).
- Central value: single-run CV, with the ensemble-mean CV (NTRIAL) shown to agree at 0.28%.
- ML/optimization uncertainty includes the train/test split, not just the estimator seed.
- GoF is reported both binned (truncated-spectral χ²) and unbinned (C2ST).
