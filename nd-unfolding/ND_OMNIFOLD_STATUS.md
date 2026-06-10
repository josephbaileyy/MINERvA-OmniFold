# N-D OmniFold (4D q3 / 5D W / PET / FPS) — Status

**Last updated**: 2026-06-09 (doc slimmed to dashboard form per the canonical-home
convention in `../AGENTS.md`; all narrative detail is in `ND_OMNIFOLD_RUN_LOG.md`,
all verified numbers in `../VALIDATION_LEDGER.md`, bugs in `../KNOWN_ISSUES.md`,
open items in `../docs/OPEN_ITEMS.md`).

## Frozen results (one line each; numbers ledger-verified)

| Result | Headline | Artifact |
|---|---|---|
| 4D xsec d⁴σ/(dpT dp∥ dEavail dq3) | σ=3.066e-38, 4D/3D anchor 0.9960, closure PASS | `products/4d/xsec_4d_MEFHC_5iter_lgbm.root` |
| 4D combined covariance (ADOPTED unified throw) | block-sum underestimates ×2.01 → adopted; √tr 3.85e-38, median 13.5–14.9%/bin | `uq_4d/universe_stage2_4d/uq_universe_4d_covariance_combined_uthrow.root` |
| 5D xsec (+W) | 5D/4D anchor 1.0011, injected-W closure PASS | `products/5d/xsec_5d_MEFHC_5iter_lgbm.root` |
| (E_avail,W) covariance + significance | median 14.8%/bin; high-W DIS corner missed 9.0/9.2/10.5/18.2σ (GENIE/+MEC/NuWro/GiBUU) | `products/5d/eavailW_covariance.root` |
| dσ/dEavail generator significance | all four generators >21σ overall, >15σ in DIS tail | `3d-unfolding/genie/` + adopted 4D cov |
| PET absolute milestone | closure 0.9884; PET/GBDT 0.9117 (training-config gap); combined budget 23.0% | `products/pet/` |
| NN cross-check | keras-MLP/GBDT total ratio 1.0078 | `omnifold_nn_core.py` |
| Unbinned GoF (C2ST) | prior z=33 → unfolded z=1.4, p=0.17 PASS | `unbinned_gof.py` |
| ML split-seedscan | split band 1.24× pure-seed; combined +0.04% | `uq_cov_mlsplit_3d.root` |
| Reco-level control + migration plots | data/MC 1.12 uniform; diag purity ~0.6/axis | `products/5d/control_plots.png`, `migration_resolution.png` |

## In flight — FPS campaign (decision memo `FPS_PILOT.md`: GO, two-tier reporting)

- 1A pilot: anchor PASS (0.65% median), 33.6% of rate outside published cuts,
  prior swap 3.0%/5.1% median (in/out of acceptance).
- **MEFHC battery DONE (2026-06-10, 54244120): anchor gate PASS** (integral
  0.9994, 0.57% median/cell; control = frozen 2D exactly). FPS total
  **σ = 4.502e-38 cm²/nucleon** (+46% vs restricted); closure exact on the
  extended grid. Numbers in `../VALIDATION_LEDGER.md`.
- **3-prior envelope DONE (54244178)**: totals spread ±1.5%; per-cell
  half-spread median 2.9% (published) vs 7.9% / p90 62% (extension) — the
  tier-2 band. `products/5d/fps_prior_envelope_MEFHC.png`.
- **UQ stage RUNNING**: `_universes_full` array 54254627 (9/12 done) →
  SetMaxTreeSize merge 54254628 (~190 GB; unified throw mandatory in FPS).
  Then: matched CV + 187-universe sweep, bootstrap, split-seedscan, unified
  throw, extension-region closure/coverage.

## Next

1. FPS MEFHC anchor gate → launch FPS `_universes_full` UQ stage.
2. FPS extension-region validation: hidden-variable closure + coverage toys.
3. Open/deferred items: `../docs/OPEN_ITEMS.md` (Ascencio gated data, NEUT,
   PET per-lateral, W-resolved laterals, multi-band unified throw).

Companion docs: `ND_OMNIFOLD_RUN_LOG.md` (chronology; all campaign narratives
2026-06-03 → present). Shared invariants: `../2d-unfolding/2D_OMNIFOLD_REFERENCE.md`
(the N-D driver imports the 2D helpers).
