# ASSESSMENT 2026-10-08 — 2D estimator pairing and engineering (uncertainty preparation, lane A)

**CITABLE FOR:** which estimator produced each existing 2D central-value and uncertainty product, with
the evidence class of each identification; the frozen estimator contract in §2; the row outcomes in
`state/uncertainty-preparation-20261008/a/pairings.tsv`; the engineering checks in
`state/uncertainty-preparation-20261008/a/verification.md`. **NOT CITABLE FOR:** coverage, a
calibration verdict, a seed or backend transfer, any change to a quoted number, adoption, a new
estimator, compute, or publication scope. It grants nothing, reruns nothing and replaces no band.

Base `f8e2bf8535a90d7ed1315530cff3b80860ef9f9c` (plan pin `ad2716d8` plus E's coordination commit),
branch `prep/uncertainty-a-pairing-20261008`. Plan: `PLAN-20261008-uncertainty-investigation-preparation.md`
(blob `fbbc0d65`), goal A. `P` = `docs/orchestration/state/uncertainty-preparation-20261008/`.

## 1. Decision

*Does each central-value/uncertainty pairing describe the same intended 2D estimator, and is an
engineering repair needed before a new statistical test is designed?*

The quoted 2D central value and the quoted 2D uncertainty come from **two different estimators**.
The central value (`3.073e-38 cm²/nucleon`, product sha256 `142a45b0…`) was produced by the
sklearn exact-split `GradientBoosting` backend with an unpinned `random_state`. Every uncertainty
block (statistical `VL170`, systematic universes, ML seed noise) was produced by the LightGBM backend
with a pinned seed: seed 1 for the statistical band and the ML scan's first trial, seed 42 for the
systematic sweep and its matched CV. The two backends' central values differ by a median **1.3** (p84
2.8, max 8.3) statistical-band σ per bin, and by a median **5.1** LightGBM seed σ, so the difference is
not LightGBM seed noise. The exact backend's own seed variation has never been measured. Whether the LightGBM covariances describe the exact estimator's uncertainty
has never been measured. Section 2 states that as the contract; §3 gives the row outcomes.

Within the LightGBM family the blocks are mutually consistent at every level that can be checked
from existing bytes: identical deterministic inputs, identical 205-bin masks and order, identical
normalization, and covariances that reproduce independently to ≤4e-16 (§4). The seed-1/seed-42
split is unmeasured at the covariance level.

## 2. Frozen estimator contract (for B and C)

This section is frozen at the `[uncprep-A] CONTRACT` commit. A later change appears only in A's
`FREEZE` commit, flagged as a change.

### 2.1 The four estimators that exist

| id | role | backend and seeds | input | settings | product (sha256) | evidence class |
|---|---|---|---|---|---|---|
| `E_C` | quoted central value | sklearn `GradientBoostingClassifier`/`Regressor`, library defaults (100 trees, depth 3, learning rate 0.1, subsample 1.0), `random_state=None` | `runEventLoopOmniFold_MEFHC.root` (CV omnifile) | `--iters 5 --use-weights`, background purity down-weight, no bootstrap | `2d_crossSection_omnifold_MEFHC_5iter.root` `142a45b0efc753d9…` | launcher + revision + wall-time signature; **executed-bytes origin unavailable** (job `53116554` log not found) |
| `E_S` | statistical band `VL170` (adopted) | LightGBM (`n_estimators 100, num_leaves 8, learning_rate 0.1`, other library defaults), `--seed 1` → step-1/step-2/regressor `random_state` 1/2/3 | CV omnifile | `--iters 5 --use-weights --bootstrap-seed b` (b = 1…300), streams `both`, purity, CPU | 300 replicas → `uq_covariance_boot300.root` (VL170) `71a75821ceeb6587…` | executed-bytes for the driver: the pilot log (`boot_1_59409026.out`, same launcher, regular lane) prints checkout HEAD `bb4b0b6f`, `GBDT estimator: lgbm`, `Pinned GBDT seeds: 1/2/3`, `streams=both`, `bkg-mode=purity`. The 300 replicas ran as array `59410433` (shared lane, 64 CPUs) under the same launcher, which exits 3 unless the checkout is clean at the expected HEAD; all 303 tasks COMPLETED (`state/ki84-rebuild-20261006/sacct_all.txt`). The per-replica log sweep is in `verification.md` |
| `E_U` | systematic universes + matched CV | LightGBM as `E_S`, `--seed 42` | `runEventLoopOmniFold_MEFHC_universes_full.root` (its CV-level histograms are bitwise those of the CV omnifile) | `--iters 5 --use-weights --universe BAND:IDX`, purity; matched CV omits `--universe` | 187 universes (44 bands) in `uq/universe_sweep_fluxfix/`; CV `uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root` `4f5a1b6d44b9e721…` | launcher + run log + product inputs; executed-bytes logs not located |
| `E_ML` | ML seed-noise block | LightGBM, `--seed 1…10` | CV omnifile | as `E_S` without bootstrap | `uq/seedscan_lgbm_ml/uq_covariance_ml.root` `3b6b48ec89207ae2…` | launcher + run log; recomputed from the 10 trial products to 3.3e-16 |

`E_S` imports `unbinned_unfolding/python/omnifold.py` through the driver's rooted `sys.path` insert,
so the helper came from the canonical checkout `/pscratch/sd/j/josephrb/MINERvA-OmniFold/`, not from
the frozen code checkout the launcher verified. The helper's bytes at run time were not recorded; its
runtime origin is **unavailable** beyond that path. The exact-split path of the helper is unchanged in
effect between `E_C`'s revision and today (`git diff d3239355 HEAD` only wraps it in a backend switch).

### 2.2 Output, binning, order and units (all four estimators)

- `hXSec2D`, `TH2D` 14 (p_T) × 16 (p_∥), edges exactly the paper's (`2D_OMNIFOLD_STUDY_STATUS.md`
  "Paper binning"); units cm² (GeV/c)⁻² nucleon⁻¹; total = Σ x · ΔpT · Δp∥.
- Reported set: **205 bins**. The five masks in use are identical bin for bin: `E_C > 0`,
  `E_U` CV `> 0`, the `VL170` replica mean `> 0`, the ML-scan mean `> 0`, and the paper's
  `StatOnlyCovariance` diagonal `> 0`.
- Covariance index order: row-major over (p_T bin, p_∥ bin), which equals the paper's
  `GlobalID = (Ptbin−1)·16 + (P∥bin−1)` restricted to the reported set. The consumer
  `compare_to_paper_fullcov.py` aligns covariances to the paper by ordinal position and checks only
  the count. Any new covariance must therefore be built over this identical set and order.
- Normalization is identical in `E_C`, `E_U`'s CV and the replicas: data POT `1.0574e21`, MC POT
  `4.9782e21`, nucleons `3.2352943e30` (geometry constant), flux integral `8.7407e-3 m⁻²/POT`,
  identical `hFlux_pt`.

### 2.3 The statistical band's sampling law (`E_S`)

- **Data stream.** One Poisson(1) factor per `data` row inside 0 ≤ p_T ≤ 4.5, 1.5 ≤ p_∥ ≤ 60
  (4,091,707 rows), from `np.random.default_rng(b)`, multiplied into the purity-weighted measured
  weights. The per-reco-bin purity `max(0, (D − B)/D)` is computed once from the observed data and is
  **not** recomputed per replica. The background MC (`mc_background`) is **not** resampled.
- **MC stream.** One Poisson(1) factor per `mc_signal_reco` row (32,849,103 rows, including the
  8,999,007 truth-only miss entries), from `np.random.default_rng(b + 10,000,000)`, applied to
  `w_truth` and `w_reco` of the same row. `mc_truth_denom` is not resampled.
- **Completeness.** Computed from the un-resampled MC truth weights, so each replica divides by the
  central value's completeness. Measured: max |c − 1| = 1.6e-14 over all 300 replicas and in `E_C`.
- The draws are positional over the tree rows in read order after the phase-space masks. Reproducing a
  replica requires the same input file and row order.
- **Band.** Per-bin mean and standard deviation (ddof 1) over the 300 replicas; `C_S` = sample
  covariance (ddof 1) about the replica mean on the 205 bins. √tr `C_S` = 1.9312e-40; median σ/mean
  0.674 %.
- Known conditioning consequences, recorded rather than repaired: fixed purity scales the data-stream
  σ by p per bin (median 0.975, `state/ki84-adopt-20261006/purity_datastream_check.json`).
  Background-MC statistics are absent from the band (driver comment at the deferred-subtraction
  block).

### 2.4 What a statistical validation can and cannot inherit from this contract

1. The adopted band is a property of `E_S`. A validation of the band must run `E_S`'s settings
   (LightGBM, `--seed 1`, purity, both streams, 5 iterations, `--use-weights`). The existing toy
   producer `2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py` defaults to LightGBM with seed 1.
   It is one of the nine new `OI-136` rooted-insert sites (verification §3), so the executed helper's
   origin is not established by the launching tree.
2. **The quoted central is `E_C`.** Validating `E_S`'s band does not validate the uncertainty attached
   to the quoted central value. That needs either (a) a separately established `E_S`→`E_C` transfer
   with a declared observable and tolerance (pairing `P02`, unmeasured), or (b) a decision by Joseph to
   change the quoted central estimator, which this preparation cannot make. A design must name which
   one it assumes.
3. Seeds: `E_S` uses seed 1 and `E_U` seed 42. No covariance-level evidence relates them (`P04`). At
   the central-value level, the seed-42 CV and the seed-1 run differ by a median 0.30 σ_S (max 1.28).
   Re-running the same arguments reproduces a replica to ≤5.8e-9 relative (`VL170`).
4. The ML seed noise of `E_S` is small against its band: σ_ML/σ_S median 0.26 (p84 0.42, max 0.73).
5. A toy design that re-estimates purity per toy, or resamples background MC, tests a different
   conditional variance from the band's. State the difference rather than absorbing it.
6. Event identity keys and population roles are B's to establish. The driver carries no event
   identifier into its outputs.

## 3. Pairing outcomes

_Completed in the FREEZE commit; see `P/a/pairings.tsv`._

## 4. Engineering checks

_Completed in the FREEZE commit; see `P/a/verification.md`._
