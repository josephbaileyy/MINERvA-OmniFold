# Estimator registry — quoted-result provenance (Agent D, integration)

Every cross-section result the analysis note may quote is one of the estimators
below. This registry is the single map from a quoted number to its estimator,
central product, backend, seed/config fingerprint, covariance product, and
commit/summary source. **Rule:** never pair a central value from one estimator
with a covariance from another (issue #3); never relabel one PET variant as
another (issues #2/#14). Numbers themselves live only in `VALIDATION_LEDGER.md`;
this file maps provenance, not values.

Status legend: **FINAL** (ledger-verified, quotable) · **ADOPTED** (ledger-verified
replacement, quotable with stated caveats) · **CANDIDATE** (committed but not the
final adopted object — gate in prose) · **GATED** (blocked on unfinished compute —
placeholder only) · **QUARANTINED** (superseded/unquotable, cross-check only).

Config-fingerprint convention (extends Agent A's `pet-fullevent-fps-v1`, commit
`b7ba96f`): every covariance component must carry the identical estimator
fingerprint as its central product (reject on mismatch). Fingerprint fields =
{estimator ID, backend+version, feature schema, preprocessing, iters, estimator
seed, train_frac (ML band), reported-bin mask/order, input NPZ/bank}.

## Scalar OmniFold estimators

| ID | Dim / axes | Backend | Central product | Est. seed / config | Covariance product | Status | Commit / summary |
|---|---|---|---|---|---|---|---|
| `omnifold-2d-sklearn` | 2D (p_T,p_∥) | **2D sklearn GBDT** (HistGradientBoosting; the 2D pipeline predates the LightGBM ND track) | `2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root` | 5 iter, `--use-weights`; phase-space mask + bkg subtraction | 2D dedicated `hCov_combined` (incl. bootstrap) + `hCov2D_reported` (ML) | **FINAL** (Phase 18.2; reproduces arXiv:2106.16210) | AGENTS.md §2D; ledger "Active 2D Result" |
| `omnifold-3d-lgbm` | 3D (p_T,p_∥,E_avail) | **LightGBM** (`omnifold_nn_core`, kind=lgbm) | 3D central (`3d-unfolding/`) | 5 iter, est seed 42 | dedicated 3D block-sum, √tr 5.724e-39, rank 247/1431 | central **FINAL**; cov **FINAL** (ledger "Active 3D") | ledger "Active 3D And 4D Results" |
| `omnifold-4d-lgbm` | 4D (p_T,p_∥,E_avail,q3) | **LightGBM** | `nd-unfolding/products/4d/xsec_4d_MEFHC_5iter_lgbm.root` (σ 3.0665e-38) | 5 iter, est seed 42; `of_inputs_4d.npz` | corrected combined (block-sum) `nd-unfolding/uq_4d/corrected/universe_stage2_4d/uq_universe_4d_covariance_combined.root` — **support-limited lateral** | central **FINAL**; combined cov **CANDIDATE** (final adopted = + unified-throw inflation + Agent A standard lateral, **GATED**) | central `1913122`; P6-4D ledger 2026-07-16; `...combined.summary.json` |
| `omnifold-5d-lgbm` | 5D (p_T,p_∥,E_avail,q3,W) | **LightGBM** | `nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root` | 5 iter, est seed 42; `of_inputs_5d.npz` | adopted mean-centered `uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware_uthrow.root` √tr 5.8077e-38 (mean shift 1.654e-38 separate); CV-centered variant 6.2367e-38 | **ADOPTED** (ledger-verified). Caveat: lateral still support-limited until #16 five-band coverage (publication gate) | `07c18ae`; ledger 2026-07-14 |
| `omnifold-fps-lgbm` | FPS extended (p_T,p_∥,…) | **LightGBM** | FPS CV product (`nd-unfolding/uq_fps/…`) | 5 iter, est seed 42; extended-FPS edges | FPS UQ (in flight) | **GATED** (old FPS adopted quarantined; corrected FPS UQ pending) | OPEN_ITEMS §FPS; ledger quarantine |

## PET (point-cloud) estimators — keep all three distinct (issues #2, #14)

| ID | Representation | Central product | Covariance product | Status | Note |
|---|---|---|---|---|---|
| `pet-recoil-legacy` | recoil cloud, **unit measured weights** (unsubtracted) | `products/pet/` unit-weight replicas | old PET stat/total budgets | **QUARANTINED** cross-check | superseded by bkgsub; never quote as precision |
| `pet-recoil-bkgsub` | recoil cloud (`GetRecoClusters`) + truth-hadron cloud, **background-subtracted** | `products/pet/bkgsub/pet_ctotal_bkgsub_5d_final.npz` (C_total √tr 3.8777e-38, med 15.103%; 4D marginal med 12.365%) | five-block PSD sum (C_syst/C_retrain/C_ML/C_stat/C_lateral) | **CANDIDATE / recoil-only cross-check** — NOT a full-event precision claim; 20 stat replicas (100 planned, not run) | ledger 2026-07-14; recoil-only per KNOWN_ISSUES #19 |
| `pet-fullevent-fps-v1` | full-event FPS (event_reco/event_data/event_truth: muon + recoil + truth particles) | — none — | — none — | **GATED** (KNOWN_ISSUES #19; OPEN_ITEMS full-event gate) | Agent A `b7ba96f` fingerprint; no full-event covariance exists yet; no recoil-PET component transfers to it |

## Cross-estimator rules (enforce in prose, captions, tables)
1. **#3 no cross pairing:** e.g. do not attach a PET (any variant) covariance to a
   LightGBM central, or a 2D-sklearn covariance to a 5D LightGBM central.
2. **#2 backend labels:** every quoted σ/uncertainty states its estimator ID or at
   least its backend (2D sklearn vs ND LightGBM vs recoil PET vs full-event PET).
3. **#14 PET separation:** `pet-recoil-legacy`, `pet-recoil-bkgsub`, and
   `pet-fullevent-fps-v1` must be distinct in text, captions, tables, figure
   provenance. "full phase space" ≠ "full-event" ≠ "recoil cloud".
4. **#8 4D covariance:** the 4D adopted covariance (with error bars / "model
   dominated" language) is GATED until the corrected *adopted* 4D (lateral swap)
   is committed. Quote only the CANDIDATE combined with an explicit caveat, or the
   exact 5D→4D marginal once the final adopted 5D is committed.

## Gated / placeholder claims (see integration checklist)
- 4D adopted covariance + error bars (issue #8) — GATED on Agent A standard lateral + unified-throw.
- (E_avail,W) generator significances (issue #6 numerics) — recompute from tracked arrays; old values quarantined.
- Full-event PET results (issue #14) — GATED on #19.
- FPS covariance-dependent claims — GATED.
