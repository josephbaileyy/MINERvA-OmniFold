# Pre-publication readiness — methodology cross-checks

Single referee-facing index of the validation/robustness studies behind the MINERvA ME FHC
OmniFold cross sections (2D d²σ/dpTdp∥, 3D +E_avail, 4D +q3). Status as of 2026-06-09.
Pointers: `LITERATURE_NOTES.md` (§A audit, §C methodology), `nd-unfolding/ND_OMNIFOLD_*.md`,
`3d-unfolding/uq_3d/`, memory `nd_followon_campaign` / `nd_unfold_io_bound_bank`.

| # | Cross-check | Status | Result / location |
|---|---|---|---|
| 1 | **Unbinned goodness-of-fit** (C2ST) | ✅ done | prior data/MC separable z=33; unfolded indistinguishable AUC 0.501, p=0.17 → PASS. `nd-unfolding/unbinned_gof.py` |
| 2 | **Train/test-split ML band** + ensemble-mean CV | ✅ done (3D); 4D in flight | split ML band 1.24× pure-seed; combined budget +0.04% (sub-dominant). `uq_cov_mlsplit_3d.root`, `ensemble_cv_3d.root` |
| 3 | **Unified-throw vs block-sum** (covariance construction) | ✅ done (4D) — **block-sum underestimates ~2×, adopted** | 160-throw jitter-corrected unified/block sqrt-trace = **2.01** on the real 4D binning; concentrated in the high-pT/lowest-Eavail corner (top 1% of bins = 78% of trace excess). Supersedes the earlier superposition probe (which sat at the jitter floor → falsely leaned block-sum-valid). Adopted via PSD-safe fractional-inflation transfer → `uq_4d/universe_stage2_4d/uq_universe_4d_covariance_combined_uthrow.root`. `unified_throw_cov.py`, `adopt_unified_4d.py` |
| 4 | **q3 as 4th axis** (more dimensions, motivated) | ✅ done + validated | 4D unfold: completeness, exact Jacobian identity, recovers 3D <2%, 2D-marginal anchors paper. Systematic + combined 4D budget in flight (`uq_4d/`) |
| 5 | **NN vs GBDT cross-check** | ✅ done | keras-MLP reproduces GBDT within ML band (ratio 1.008). `omnifold_nn_core.py` |
| 6 | **Point-cloud (PET) track** | ✅ absolute milestone + 4D systematic budget done | real recoil clusters dumped; PET → full-stats absolutely-normalized 4D xsec (closure recovered/truth 0.988; PET/GBDT total 0.912, ~9% = training config not bug). Full PET 4D combined budget (frozen-reweighter) incl. transferred lateral = 23.0% total. `minerva_pet_dataloader.py`, `pet_systematics.py`, `pet_lateral_correction.py` |
| 7 | **Generator comparison** (full-cov χ²) | ✅ done (3D + 4D-projected + (E_avail,W) band) | 3D: Tune-v1 best, GiBUU worst. dσ/dEavail on the adopted 4D cov: GENIE-CV/+MEC/NuWro/GiBUU all miss data at >21σ (>15σ in the DIS tail). (E_avail,W) band now 4-generator (GiBUU regenerated, σ=2.22e-38 = most deficient). **W-resolved**: full 42-bin (E_avail,W) cov (median 14.8%/bin, CV validated to 0.1%) → high-W DIS corner (E_avail≥0.4 & W≥1.8 GeV, 12 bins) GENIE-CV/+MEC/NuWro/GiBUU miss data at 9.0/9.2/10.5/18.2σ. `eavail_generator_significance.py`, `eavailW_covariance.py`, `3d-unfolding/genie/` |
| 8 | **Ascencio low-q3 bin-identical overlay** | machinery done; **blocked on data** | our-side spectra + χ² path ready; needs the 2110.13372 release (HepData/member-gated). `compare_ascencio_q3.py --ascencio-2d` |
| 9 | **Flux↔muon-E covariance** rederivation | ✅ done | ρ≈0.87–0.90, rank-2 block. memory `flux_muonE_covariance_rederivation` |
| 10 | **Covariance rank/stat-block** audit | ✅ done | rank gap is the stat block, not missing bands. memory `rank_gap_is_stat_block` |

## Open items before submission
- **4D combined budget** (C_syst+C_stat+C_ML) — ✅ done, with the unified-throw systematic adopted (`uq_4d/universe_stage2_4d/uq_universe_4d_covariance_combined_uthrow.root`).
- **Full unified-throw covariance** — ✅ done (4D): block-sum underestimates ~2×, adopted (item 3).
- **(E_avail,W) covariance** — ✅ done: frozen-reweighter block-sum on the merged 5D `_universes_full` (`eavailW_covariance.py`, `products/5d/eavailW_covariance.root`, median 14.8%/bin, CV validated to 0.1%). High-W DIS corner (E_avail≥0.4 & W≥1.8 GeV): generators miss the data at 9.0–18.2σ (GiBUU most deficient) — the excess is W-localised in the DIS region.
- **PET vs GBDT** — absolute milestone done; full PET systematic budget done (frozen-reweighter) incl. the transferred lateral band (`products/pet/pet_4d_covariance_combined.root`, total 23.0%); residual = full per-lateral PET reco-cloud re-inference.
- **Ascencio overlay** — drop in the data file (external/member access).

## Methodology stance (for the response-to-referees)
- Covariance is block-summed (`C_syst+C_stat+C_ML`); the unified-throw study tests the
  underlying linearity assumption directly (not just asserts it) and, in 4D, **found it
  broken** (block-sum underestimates ~2×) — so the published 4D systematic adopts the
  unified-throw magnitude rather than the bare block sum.
- Central value: single-run CV, with the ensemble-mean CV (NTRIAL) shown to agree at 0.28%.
- ML/optimization uncertainty includes the train/test split, not just the estimator seed.
- GoF is reported both binned (truncated-spectral χ²) and unbinned (C2ST).
