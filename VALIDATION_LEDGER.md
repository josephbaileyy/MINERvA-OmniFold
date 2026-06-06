# MINERvA-OmniFold Validation Ledger

Validation pass started 2026-06-06. Scope: whole repository, with priority on
technote-cited active results. Criterion: recompute from existing ROOT/NPZ/text
outputs where possible; rerun heavy production only when a check fails and the
smallest required rerun is clear.

## Environment And Test Harness

- `python -m pytest unbinned_unfolding/test -q`: **BLOCKED**. The active
  `root_6_28` Python does not have `pytest` installed.
- `python 3d-unfolding/xsec_3d.py`: **PASS**. Eavail marginal recovers 2D
  cross section to max relative difference `3.84e-16`; 1D projections integrate
  to the same total.
- `python nd-unfolding/xsec_nd.py`: **PASS**. N-D extraction reproduces frozen
  `xsec_3d.py` to `<1e-12`; 4D q3 marginal recovers 3D cross section to max
  relative difference `3.8e-16`; all 1D projections integrate to the same total.

## Known Audit Findings

- Point-cloud PET: **REFRESHED AS A SHAPE/METHOD CROSS-CHECK**. The stale
  `ExtraEnergyClusters_*` PET artifact was replaced after confirming
  `CVUniverse::GetRecoClusters()` reads `cluster_energy`, `cluster_pos`,
  `cluster_z`, and filters `cluster_isMuontrack`. The corrected point-cloud
  chain rebuilt `runEventLoopOmniFold_PC_MEFHC.root` and `of_inputs_pc.npz`,
  then PET training job 54033990 and comparison job 54033991 completed with
  exit `0:0`. The regenerated `pet_vs_gbdt.png` reports area-normalized
  PET-vs-GBDT median shape differences of 3.86% (pT), 2.36% (pz), 2.63%
  (Eavail), and 2.33% (q3). This remains a shape-only comparison because the
  PET run uses a 2M-event subsample.
- Ascencio low-q3 data: **STAGED ONLY** unless a gated data file is supplied.
  Local scripts can produce our-side spectra and synthetic checks, but the real
  2110.13372 numerical overlay is not complete from public in-session data.

## Active 2D Result

- `compare_to_paper_fullcov.py` with the frozen 2D result and paper covariance:
  **PASS**. Recomputed paper full-covariance chi2/ndf is `3.661` on 205 bins.
- Combined paper+ours check: **PASS** when using
  `uq_universe_covariance_full_matcorr_fluxfix.root:hCov_combined` plus
  `uq_covariance_ml.root:hCov2D_reported`. Recomputed combined chi2/ndf is
  `1.481`; log-normal combined chi2/ndf is `1.468`; pull mean/RMS is
  `0.051/0.409`.
- Covariance-file contract: `hCov_combined` already includes the bootstrap
  covariance. Adding `uq_covariance_boot300.root:hCov2D_reported` separately
  double-counts bootstrap and changes the combined chi2/ndf to `1.341`.

## Active 3D And 4D Results

- `compare_3d_fullcov.py` with GENIE, Tune v1, NuWro, and GiBUU: **PASS**.
  Recomputed covariance has sqrt-trace `5.724e-39`, hard rank `247/1431`;
  full-covariance ranking matches the technote: Tune v1 best, GiBUU worst.
- `check_4d_anchors.py`: **PASS**. 4D total is `3.0665e-38`; 4D/3D
  2D-marginal integral ratio is `0.9960`; median projection differences are
  `0.38%` for pT, `0.64%` for pz, and `1.68%` for Eavail.
- `compare_ascencio_q3.py`: **PASS for our-side spectra only**. It produces
  `d sigma/dq3` and low-q3 `Eavail` slices; no real Ascencio chi2 is computed
  without the external gated data file.
- `compare_mlsplit_combined.py`: **PASS**. Train/test-split ML band is `1.24x`
  the seed-only band, but the combined 3D sqrt-trace moves only `+0.04%`.

## Validation Diagnostics

- `bottom_line_test.py --dim 2 --mode closure`: **PASS**. Feature-bin residual
  is `1.6875%` vs injected `17.202%`, ratio `0.0981`.
- `bottom_line_test.py --dim 3 --mode closure`: **PASS**. Feature-bin residual
  is `1.8408%` vs injected `18.061%`, ratio `0.1019`.
- `classifier_calibration.py --n 200000`: **PASS**. GBDT AUC/Brier
  `0.5374/0.2486`; MLP AUC/Brier `0.5338/0.2500`; binned ratio recovery
  median `4.72%` for GBDT and `20.90%` for MLP; GBDT/MLP binned correlation
  `0.9159`.
- `unbinned_gof.py` using stored 3D weights with `--max-per-class 200000`:
  **PASS**. Prior acc/AUC `0.5196/0.5314` with `z=16.70`; unfolded acc/AUC
  `0.5013/0.5022` with `z=1.10`, `p=0.273`. Exact values differ from the
  technote's full-stat/subsample choice, but the conclusion is unchanged.
- Coverage: **PARTIALLY REPRODUCIBLE**. The checkout contains only
  `uq/coverage/coverage_summary.txt`, a stage-1 `n_toys=20` summary, and zero
  coverage toy ROOTs. The technote's 200-toy numbers are documented in
  `docs/uq_statistical_methods.tex` but cannot be regenerated from the present
  artifacts.
