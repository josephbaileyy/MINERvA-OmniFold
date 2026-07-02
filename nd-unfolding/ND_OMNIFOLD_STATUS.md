# N-D OmniFold (4D q3 / 5D W / PET / FPS) — Status

**Last updated**: 2026-07-02 (doc slimmed to dashboard form per the canonical-home
convention in `../AGENTS.md`; all narrative detail is in `ND_OMNIFOLD_RUN_LOG.md`,
all verified numbers in `../VALIDATION_LEDGER.md`, bugs in `../KNOWN_ISSUES.md`,
open items in `../docs/OPEN_ITEMS.md`).

## Frozen results (one line each; numbers ledger-verified)

| Result | Headline | Artifact |
|---|---|---|
| 4D xsec d⁴σ/(dpT dp∥ dEavail dq3) | σ=3.066e-38, 4D/3D anchor 0.9960, closure PASS | `products/4d/xsec_4d_MEFHC_5iter_lgbm.root` |
| 4D combined covariance (ADOPTED unified throw) | block-sum underestimates ×2.01 → adopted; √tr 3.85e-38, median 13.5–14.9%/bin | `uq_4d/universe_stage2_4d/uq_universe_4d_covariance_combined_uthrow.root` |
| 5D xsec (+W) | 5D/4D anchor 1.0011, injected-W closure PASS | `products/5d/xsec_5d_MEFHC_5iter_lgbm.root` |
| (E_avail,W) covariance + significance (W-resolved laterals ADOPTED) | median 14.9%/bin; high-W DIS corner missed 8.9/9.2/15.6/22.4σ (GENIE/+MEC/NuWro/GiBUU) — W-resolved block deepens NuWro/GiBUU tension (#4 closed 2026-06-13) | `products/5d/eavailW_covariance_wlat.root` |
| dσ/dEavail generator significance | all four generators >21σ overall, >15σ in DIS tail | `3d-unfolding/genie/` + adopted 4D cov |
| PET absolute milestone | closure 0.9884; PET/GBDT 0.9117 (training-config gap); clean budget 11.7% (rebank 2026-06-12; pre-#12 published 23.0% was inflated ×2, conservative) | `products/pet/pet_4d_covariance_combined_rebank.root` |
| NN cross-check | keras-MLP/GBDT total ratio 1.0078 | `omnifold_nn_core.py` |
| Unbinned GoF (C2ST) | prior z=33 → unfolded z=1.4, p=0.17 PASS | `unbinned_gof.py` |
| ML split-seedscan | split band 1.24× pure-seed; combined +0.04% | `uq_cov_mlsplit_3d.root` |
| Reco-level control + migration plots | data/MC 1.12 uniform; diag purity ~0.6/axis | `products/5d/control_plots.png`, `migration_resolution.png` |
| Ascencio bin-identical cross-check | full-cov χ²/ndf 1.68/2 (p=0.43) on maximal common grid — consistent | `compare_ascencio_fullcov.py`, `products/4d/ascencio_fullcov_compare.png` |
| 5D GBDT combined covariance (ADOPTED unified throw, 2026-07-01/02) | block-sum median 13.4%/bin, Models/2p2h now dominant (Flux sub-dominant, first time W axis is in); unified/block trace ratio 1.539 (mild vs 4D's 2.01) → adopted, median 13.7%/bin | `uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root` |
| PET 5D vs GBDT uncertainty — **INDICATIVE, 2M-train anchor** | PET WORSE: median 14.8% (PET) vs 13.3% (GBDT) block-sum, ratio 1.192, PET tighter in only 38% of 10550 common bins (contrast 4D: COMPARABLE); PET-side unified/block ratio 5.711 flagged, not adopted (needs to be understood) | `products/pet/pet_vs_gbdt_uncertainty_5d_summary.json`, `products/pet/pet_5d_covariance_combined_unified_wlat_summary.json` |
| Truth-cloud coverage fix (Tier 2, 2026-06-28/29) | miss-row truth cloud coverage 72.6%→99.9995%; E_avail cloud-projectable (98.8% within, RMS 0.082); W NOT cloud-projectable (19.7% within, RMS 3.24 GeV); 2.3% saturated rows carry median bias −0.035 | `products/pet/fullcloud/pointcloud_projection_summary.json` |

## In flight — PET capstone (kickoff 2026-06-19: raw-data unbinned unfolding beyond the measured phase space)

- **Step 1 (close the PET-vs-GBDT CV gap) DONE-ish**: 4D rebank gap is
  ~9% (PET/GBDT 0.9117); full 32.8M-event horovod unfolding is now the
  standing capability (memmap+rank-stride dataloader, commit 423285b).
- **Step 2 (FPS-on-raw-inputs capstone) IN FLIGHT**: the FPS point-cloud
  inputs needed a cloud-fixed re-dump first (old ones predate the 06-28
  truth-cloud fix) — evloop/hadd/npz all DONE 2026-06-29/30
  (`runEventLoopOmniFold_PC_FPS_MEFHC.root`, `of_inputs_pc_fps.npz`,
  32,917,278 signal clouds). **Full-stats PET FPS train (job 55288409,
  horovod, train=40,000,000, ranks=4, niter=5, epochs=8) is RUNNING**
  (queued 2026-06-29→2026-07-01, currently mid-iteration). Remaining after
  it lands: NuWro 3-prior envelope (MnvTune/bare-GENIE priors already
  exist from the 2D/5D pilots; `build_fps_prior_nuwro_5d.py` for the 5D
  NuWro leg is drafted but not yet run) → Tier-2 retraining-response
  analysis at 8-10M events → per-event-weight covariance so any observable
  inherits the band.

## In flight — 5D uncertainty open questions

- **PET 5D unified/block ratio (5.711) NOT understood/NOT adopted**: PET's
  own unified-throw check (frozen 2M-train reweighter) gives a much larger
  unified/block inflation than the GBDT-side 5D check (1.539) or the PET 4D
  precedent — needs investigation before any PET 5D unified-throw number is
  quoted. `products/pet/pet_5d_covariance_combined_unified_wlat_summary.json`.
- **Note-text catch-up**: the full-stats PET numbers, the 5D GBDT
  uncertainty statement (now Models/2p2h-dominant, unified-throw adopted),
  and the PET 5D verdict (WORSE, indicative/2M-train) are not yet reflected
  in the analysis note — see `../docs/OPEN_ITEMS.md`.

## Next

1. PET FPS full-stats train (55288409) drains → NuWro 3-prior envelope →
   Tier-2 retraining-response → per-event-weight covariance (the capstone
   Step 2 chain).
2. Understand the PET 5D unified/block 5.711x ratio before quoting any PET
   5D unified-throw number.
3. Fold the landed 5D GBDT unified-throw-adopted covariance and the PET 5D
   verdict into the analysis note.
4. Open/deferred items: `../docs/OPEN_ITEMS.md`.

Companion docs: `ND_OMNIFOLD_RUN_LOG.md` (chronology; all campaign narratives
2026-06-03 → present). Shared invariants: `../2d-unfolding/2D_OMNIFOLD_REFERENCE.md`
(the N-D driver imports the 2D helpers).
