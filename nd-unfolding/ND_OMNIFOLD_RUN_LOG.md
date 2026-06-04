# N-D OmniFold — Run Log (append-only)

## 2026-06-03 — Workstream D kickoff: q3 4th axis + NN track

Implemented `../docs/HIGHER_DIM_OMNIFOLD_DESIGN.md` end-to-end.

**Axis-list refactor + N-D math**
- `xsec_nd.py`: N-D extraction/projection on `np.histogramdd`. Self-tests pass,
  incl. bit-equivalence-to-<1e-12 vs the frozen `3d-unfolding/xsec_3d.py` and the
  4D q3-marginal→3D Jacobian identity (max rel 3.8e-16).
- `unfold_nd_omnifold_unbinned.py`: driver parametrized over an `EXTRA_AXES`
  registry (pt,pz fixed; eavail,q3 as configurable extra axes). `--axes eavail`
  reproduces 3D; `--axes eavail,q3` is the 4D unfold. Launched an `--axes eavail`
  reproduction on the existing 3D omnifile as the refactor's validation.

**C++ q3 (event loop)**
- Added `CVUniverse::RecoQ3()` (calorimetric, `LowRecoilFunctions::GetLowRecoilQ3`
  lineage) + used MAT `Getq3True()` for truth; dumped `sim_q3/MC_q3/measured_q3/
  sim_background_q3` in `runEventLoopOmniFold.cpp` (24 q3 touchpoints, symmetric
  with the eavail schema). Verified branches `MasterAnaDev_recoil_E`, `mc_Q2`,
  `mc_primFSLepton` exist in the raw tuples.
- Built (`make -j8 runEventLoopOmniFold` + `make install`, exit 0) → fresh
  `MINERvA101/opt/bin/runEventLoopOmniFold`.
- Smoke test on one 1A file: truth MC_q3 ∈ [0.05, 85] GeV median 1.77 (clean);
  reco q3 median sane (1.5–3.8 GeV) with large calorimetric tails (max ~1e5 GeV
  on pathological recoil) that the catch-all top q3 bin absorbs, mirroring reco
  Eavail. Confirmed RecoQ3/Getq3True run without error.
- Submitted the 12-playlist re-run: **SLURM 53905768** (array 1-12) →
  `runEventLoopOmniFold_4D_${PL}.root` (CV-only). Chained: **53906839**
  (afterok) hadds → `runEventLoopOmniFold_4D_MEFHC.root`, runs the 4D CV unfold
  `xsec_4d_MEFHC_5iter_lgbm.root`, the anchors (`check_4d_anchors.py`), and the
  injected-q3 closure.

**NN / point-cloud track (Phase 2)**
- Vendored `ViniciusMikuni/omnifold` → `../omnifold_nn/` (git clone; PET + MLP,
  keras/TF — the only linked repo with a point-cloud net). Env: no TF in the ROOT
  conda env, but `module load tensorflow/2.15.0` is available (matches the repo's
  `tensorflow>=2.15` req) and GPU-capable.
- `omnifold_nn_core.py`: ROOT-free keras-MLP (from the vendored `net.py`) behind a
  sklearn fit/predict_proba with standardization + the estimator-agnostic two-step
  loop. `omnifold.py` got an `estimator="nn"` branch delegating to it (lazy TF).
- NN-vs-GBDT cross-check (same loop, same inputs, swap classifier): leg 1
  **53906721** (CPU/ROOT) dumps `of_inputs_3d.npz` + runs the GBDT leg
  (`res_lgbm_3d.npz`); leg 2 **53906748** (GPU, afterok) runs the keras-MLP leg
  (`res_nn_3d.npz`).

Outcomes (anchors, NN comparison) to be appended when the jobs land.
