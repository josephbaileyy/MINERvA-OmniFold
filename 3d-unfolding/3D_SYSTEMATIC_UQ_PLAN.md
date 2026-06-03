# 3D systematic-UQ campaign — prep / gap analysis

Date: 2026-05-31. Goal: produce the 3D systematic covariance
`d³σ/(dpT dp‖ dEavail)` mirroring the validated 2D campaign
(`2d-unfolding/uq/universe_stage2_MEFHC_full_matcorr_fluxfix/`). Prerequisites
from the 2D sign-off are in `2d-unfolding/2D_VALIDATION_FOR_3D.md` (systematics
GREEN; stat block is the one open item — resolve via the data/MC split before
any 3D ours-only χ²).

## What already exists
- 3D CV result `xsec_3d_MEFHC_5iter_lgbm.root` + bootstrap stat band
  (`uq_3d/stat_band_3d.root`, 100 replicas, 0.16–0.44 % — `build_bootstrap_band_3d.py`).
- 3D CV omnifile `runEventLoopOmniFold_MEFHC_3D.root` (2.84 GB) — **CV weights
  only** (`w_truth`/`w_reco`; no universe branches).
- 3D driver `unfold_3d_omnifold_unbinned.py` imports the 2D driver (`u2d`) and
  reuses its phase-space / flux / POT machinery, but **exposes no `--universe`
  flag** (only `--bootstrap-seed`).
- Event-loop binary `MINERvA101/opt/bin/runEventLoopOmniFold` already writes the
  E_avail branches (`MC_eavail`/`sim_eavail`/`sim_background_eavail`/`measured_eavail`).

## The gaps (in dependency order)

### Gap 1 — lateral-shifted E_avail dump  ✅ RESOLVED: NOT NEEDED (premise was wrong)
**Original premise (WRONG):** that the dump-all mode freezes E_avail at CV for
"the 6 lateral bands (BeamAngleX/Y, MuonResolution, GEANT_{Neutron,Pion,Proton},
Muon_Energy_MINERvA)" and that GEANT_Pion/Proton lateral shifts move the E_avail
axis. Investigated 2026-05-31 (read the 44-band/188-universe 2D dump
`runEventLoopOmniFold_MEFHC_universes_full.root` + the MAT systematic classes):

- **GEANT_Neutron/Pion/Proton are VERTICAL (weight-only)**, not lateral. They
  reweight CV E_avail via `w_reco_GEANT_*_<idx>` (already dumped) — no kinematic
  shift exists or is needed. The hadronic-response systematic IS captured.
- **The only lateral bands are muon/beam**: BeamAngleX/Y, MuonResolution,
  Muon_Energy_MINERvA, Muon_Energy_MINOS (5 bands, 10 universes). Their
  systematic classes (`MuonSystematics`, `AngleSystematics`,
  `MuonResolutionSystematics`) override **only** muon momentum/angle getters
  (`GetPmu*`, `GetThetaXmu/Ymu`). `NewEavail()` reads only
  `blob_recoil_E_tracker/ecal` + `muon_fuzz_*`; `GetEAvailableTrue()` reads only
  truth `mc_FSPartE`. **None of those branches are overridden by any lateral
  band**, so E_avail is *invariant* under every lateral universe — freezing it at
  CV is physically correct, not a bug.

**Net:** no C++ change, no rebuild needed. (A lateral-E_avail dump was prototyped
and reverted on 2026-05-31; only an explanatory NOTE comment remains in
`runEventLoopOmniFold.cpp`. The installed binary is unchanged.) All 44 bands are
handled correctly by the existing dump schema: 39 vertical via weights, 5 lateral
via shifted pT/pz with CV E_avail.

### Gap 2 — re-run the 3D event loop in dump-all mode  (compute)  ✅ DONE 2026-05-31
Ran `sbatch_evloop_array_3d_universes_full.sh` (array 1-12, `MNV101_DUMP_UNIVERSES=1`,
8 cpu / 48 G / 24 h; per-playlist 11min–2h22m), merged with
`sbatch_hadd_3d_universes_full.sh` → `runEventLoopOmniFold_MEFHC_3D_universes_full.root`.
- **Built + validated:** 120 GB; trees mc_signal_reco/mc_truth_denom = 32,849,103,
  data = 4,119,797, mc_background = 658,227; 187 universe `w_reco_<band>_<idx>`
  branches + CV `MC_eavail`/`sim_eavail` present. Quota OK (11.7/20 TB).
- **No longer depends on Gap 1** (moot) — the current installed binary already
  dumps everything needed (vertical weights + lateral pT/pz; E_avail invariant).
- **⚠ hadd 100 GB trap:** plain `hadd -f` ABORTS merging these files (the combined
  trees exceed ROOT's 100 GB `TTree::fgMaxTreeSize` rollover → SIGABRT, 94 GB
  partial missing data+bkg). The hadd sbatch therefore uses the Python
  `TFileMerger` with `SetMaxTreeSize=300GB` (`../2d-unfolding/uq/hadd_universes_full.py`,
  mem 64 G). Never use bare `hadd` for `_universes_full` omnifiles. See memory
  `hadd-100gb-tree-limit`.

### Gap 3 — wire `--universe` into the 3D driver  (code)  ✅ DONE 2026-05-31
Added to `unfold_3d_omnifold_unbinned.py`: `--universe BAND:IDX` and
`--flux-universe-file` (default points at the 2D file; flux is pT-binned so it is
reused verbatim). `universe_branch` is plumbed into `collect_signal_3d` and
`collect_truth_denom_3d`, reusing the `u2d._universe_*_branch` /
`_universe_kine_branches` / `load_flux_universe_bins` helpers. For lateral bands
it swaps (pT, pz) only and keeps CV `MC_eavail` / `sim_eavail` (Gap 1 finding:
E_avail invariant). Flux:IDX divides by Φ_u (Task #70). Validation guards mirror
2D: requires `--use-weights`; incompatible with `--closure` and `--bootstrap-seed`.
- **Verified:** argparse + all guards fire; end-to-end against the CV-only
  omnifile raises the clear "branch missing — re-run with MNV101_DUMP_UNIVERSES"
  error (the only remaining dependency is Gap 2). CV path is provably inert
  (every change guarded by `universe_branch is not None`); a CV non-regression
  unfold reproduced the canonical integral.
- **Deferred (not needed for the sweep):** `--alt-universe` / alt-model closure.
  It is a closure-validation feature, separable from the systematic sweep; the 2D
  `--closure-alt-universe` machinery can be ported later if wanted.

### Gap 4 — sweep + rollup  (mirror 2D)  ✅ COMPLETE 2026-06-02

**DONE.** Sweep 53699271 drained 187/187; seedscan 53700874 10/10. Final rollup
ran → `uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root`
(`hCov_universe3d_total` syst-only, `hCov_combined3d_total` = C_syst+C_stat+C_ML,
per-band TH2D, `hSigma` TH3D, pt/pz/eavail PNGs, summary.txt). **Combined budget:**
√trace 5.724e-39, median 10.4%/bin, p84 15%, rank 247/1431. Systematics dominate
(C_syst √tr 5.710e-39 ≫ C_stat 3.51e-40, C_ML 2.13e-40). **Dominant bands:** Flux
(3.22e-39, median 5.4%) > 2p2h (2.42e-39) > Muon_Energy_MINERvA (1.84e-39) >
Muon_Energy_MINOS (1.77e-39) > MaCCQE (1.32e-39) — Flux-led, same ordering as 2D.
Pure-norm bands (EtaNCEL/MaNCEL/NormDISCC/NormNCRES) ≈0 as expected for
CC-inclusive. **Next:** put this band on the generator-comparison plots
(`3d-unfolding/genie/`), previously stat-only.

#### Build record (all pieces, 2026-05-31):
- **`sbatch_unfold_3d_MEFHC_5iter_universes_full.sh`** (BUILT): array 1-200%20,
  regular QOS 128 cpu / 2 h, reads `uq_3d/universes_full_list.txt` (187 lines,
  generated, identical band:idx set to 2D), calls `unfold_3d ... --universe
  <BAND:IDX> --seed 42` → `uq_3d/universe_sweep/3d_xsec_MEFHC_5iter_lgbm_uni_full_<TAG>.root`.
  Skip-if-exists + skip-if-beyond-list guards. Needs the Gap 2 omnifile (present).
- **`uq_3d/analyze_universes_3d.py`** (BUILT): full-3D-grid rollup. Reads `hXSec3D`
  from CV + each universe, MAT mean-centered 1/N per-band cov on reported bins
  (cv>0), `--add-norm 0.014` rank-1, total → `uq_universe_3d_covariance.root`
  (`hCov_universe3d_total` + per-band + `hSigma_universe3d_total` TH3D) + per-axis
  (pt/pz/eavail) grouped-sigma PNGs + summary. Syntax-checked.
- **Eavail-marginal 2D cov (free):** reuse `../2d-unfolding/uq/analyze_universes.py`
  on the same sweep ROOTs (it reads `hXSec2D`, the Eavail-marginal the 3D driver
  writes) → directly comparable to the paper anchor covariance.
- **Statistical covariance (DONE 2026-05-31):** `uq_3d/build_bootstrap_cov_3d.py`
  turns the 100 bootstrap replicas (`uq_3d/xsec_3d_boot*.root`) into a full 3D
  stat cov on the SAME reported-bin flattening (`uq_3d/uq_cov_stat_3d.root`:
  `hCov_stat3d_reported`, 1431 bins, √tr 3.5e-40, median rel 0.69%/bin, rank
  99=nrep-1). `analyze_universes_3d.py --bootstrap-cov uq_3d/uq_cov_stat_3d.root`
  block-sums it → `hCov_combined3d_total`.
- **ML band / C_ML (seedscan) — BUILT + LAUNCHED 2026-05-31:**
  `sbatch_unfold_3d_MEFHC_5iter_seedscan.sh` (array 1-10, CV omnifile, vary only
  `--seed`) → `seedscan_3d/3d_xsec_MEFHC_5iter_lgbm_seed<N>.root` (array 53700874).
  C_ML built by the same converter generalized with `--label`:
  `build_bootstrap_cov_3d.py --label ml3d --replicas 'seedscan_3d/3d_xsec_*_seed*.root'
  --out-root uq_cov_ml_3d.root`. The rollup's `--bootstrap-cov` now takes MULTIPLE
  covs, so the full budget is one call:
  `analyze_universes_3d.py ... --bootstrap-cov uq_3d/uq_cov_stat_3d.root:hCov_stat3d_reported
  uq_3d/uq_cov_ml_3d.root:hCov_ml3d_reported` → `hCov_combined3d_total` = C_syst+C_stat+C_ML.
- **Lateral path VALIDATED 2026-05-31:** `Muon_Energy_MINERvA:0` smoke unfold on
  the real omnifile fired all pT/pz swaps (eavail kept CV), gave a sane −1.4%
  integral shift, completeness 0.87 (efficiency compensates), 1431/1431 bins
  shifted. Full 187-job sweep launched (array 53699271).

## Carry-forward decisions (locked from 2D)
- **Flux 1/Φ fix**: use `--flux-universe-file` natively (no post-hoc rescale).
- **Normalization**: 1.4 % rank-1 (`--add-norm 0.014`) — paper Ruterbories §VII.
- **χ² inversion**: truncated/regularized or combined cov — NEVER raw pinv
  (Check #3). Resolve the stat-block open item (data/MC split) before any 3D
  ours-only goodness-of-fit.
- **Flux↔muon-E cross block** (ρ≈0.9, rank-2): physically real but does not
  change rank; optional to carry into 3D.

## Suggested order
0. ~~Gap 1 (C++ + rebuild)~~ — **moot** (E_avail invariant under lateral bands; no fix needed).
1. ~~Gap 3 (driver flags)~~ — **DONE** (`--universe`/`--flux-universe-file` wired + verified).
2. ~~Gap 2 (dump-all event loop + hadd)~~ — **DONE** (120 GB omnifile built + validated).
3. ~~Gap 4~~ — **DONE 2026-06-02**: 187-job sweep + seedscan drained, full rollup
   ran → `uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root`
   (`hCov_combined3d_total`). Campaign complete; next is the generator-comparison band.
