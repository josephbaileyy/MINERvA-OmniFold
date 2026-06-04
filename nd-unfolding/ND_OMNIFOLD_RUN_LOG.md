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

**First results + two bug fixes (2026-06-04)**
- Event loop (53905768) completed all 12 playlists; hadd → `runEventLoopOmniFold_4D_MEFHC.root`
  (3.4 GB, POT summed correctly).
- **GBDT npz cross-check leg validated the whole new stack**: `omnifold_loop` (the
  ROOT-free copy of the two-step loop) on the dumped 3D inputs gives total σ =
  **3.0785e-38** — exactly the frozen 3D headline. This confirms the axis-list
  readers (`nn_dump_inputs.py` uses the driver's `collect_*`), `xsec_nd.py`, and the
  loop, independently of ROOT plotting.
- **Bug 1 (fixed): THnSparseD segfault.** The 4D unfold wrote `hXSecND_flat` then
  segfaulted in the 4D `THnSparseD` Python write (C-level, so the driver's
  `try/except` could not catch it), aborting before the projections/anchors/closure.
  Dropped the THnSparse path entirely — the flat TH1D (C-order ravel) + the TH2D
  marginal + 1D projections are the canonical outputs; N-D structure is recovered by
  reshaping with the known edges. Same crash had hung the login-node 3D-repro run.
- **Bug 2 (fixed): NN normalization collapse.** The keras-MLP leg ran end-to-end on
  GPU (TF 2.15, GPU found) and recovered the correct dσ/dpt,dpz,dEavail **shape**,
  but the absolute normalization collapsed to **2.7e-44** (~1e-6 of GBDT): the MLP
  sat at the trivial class-balance bias `p=W1/(W0+W1)` and never learned the x-density
  ratio. Fix: train the NN on class-BALANCED weights (`_balance_weights`) and restore
  the true normalization via `w=(W1/W0)·p/(1-p)` (`_class_ratio`); GBDT keeps raw
  weights (it calibrates the absolute ratio directly). This is exactly the failure the
  "validate NN vs GBDT before trusting it" gate is meant to catch.
- Re-running with both fixes: 4D unfold+anchors+closure (53925395), NN leg (53925396).

**Phase 1 (q3 4D) — VALIDATED (2026-06-04, job 53925395).**
`xsec_4d_MEFHC_5iter_lgbm.root`, d⁴σ/(dp_T dp_‖ dE_avail dq3), lgbm 5-iter, q3 edges
[0,0.2,0.4,0.6,0.8,1.2,2.0,100] GeV:
- completeness c = 1.0000; total σ (4D integral) = **3.066e-38 cm²/nucleon**.
- **Jacobian identity exact**: 2D (p_T,p_‖) marginal integral == 4D integral (3.0665e-38).
- **4D recovers the frozen 3D** (independently run): median rel diff dσ/dp_T 0.38%,
  dσ/dp_‖ 0.64%, dσ/dE_avail 1.68% (max 4.2%) — within ML/stat noise; adding q3 as a
  feature does not bias the lower-D projections.
- **2D-marginal anchors the paper**: 4D/3D = 0.9960 (3D = 3.0789e-38).
- New **dσ/dq3** spectrum produced, all-positive (not required to be monotonic).
- **Injected-q3-shape closure PASSES**: per-q3-bin ratios [1.007, 0.989, 1.005, 1.000,
  1.000, 1.000, 1.000] track the injected mean factor 1.0142 → 4D OmniFold recovers an
  injected q3 shape. `.err` clean (no THnSparse segfault).

**Phase 2 (NN) — 2nd attempt still collapsed; root cause found.** The class-balance fix
alone left the NN at ~0 (even slightly negative = float noise). Diagnosed the real
killer: keras `validation_split` takes the last 20% *without shuffling*, and the step
data is ordered [class0; class1], so the validation set was single-class and
early-stopping/`restore_best_weights` picked a degenerate epoch. Fix: permute before
`fit`. Re-running the NN leg with the shuffle fix (the GBDT leg remains the 3.0785e-38
reference).

**Phase 2 (NN) — VALIDATED (2026-06-04, job 53928526, GPU TF 2.15).** With the
class-balance + shuffle fixes, the keras-MLP OmniFold (same two-step loop, same 3D
inputs, swap classifier) reproduces the GBDT cross section **within the ML band**:
- total σ: NN 3.1024e-38 vs GBDT 3.0785e-38 → **ratio 1.0078** (0.8%).
- per-bin median rel diff: dσ/dE_avail **0.66%**, dσ/dp_T **1.20%**, dσ/dp_‖ **1.36%**
  (max deviations 2.8% / 7.9% / 24.7%, confined to sparse tail bins).
This green-lights the vendored NN engine for the point-cloud phase (the design-doc
gate: the NN must match GBDT on a known case before being trusted where no GBDT
baseline exists). Net conclusion stands: GBDT remains the production engine for scalar
axes (q3 included); the NN is the path for variable-length point clouds, now verified to
agree on tabular inputs. The two NN failure modes found + fixed (class-balance bias;
unshuffled single-class `validation_split`) are documented in `omnifold_nn_core.py` for
whoever drives the PET point-cloud track next.

## 2026-06-04 — Follow-on campaign: all six "next steps" (prepub items + q3 systematics + PET)

Driven by the `/goal` to do all six documented follow-ons, parallelizing across sbatch waits.

**#2 Ascencio low-q3 bin-identical overlay — DONE (code + our-side spectra).**
`compare_ascencio_q3.py`: reshapes the 4D `hXSecND_flat` and projects dσ/dq3 + the
d²σ/(dq3 dEavail) low-q3 slices via `xsec_nd`. Bin-identical χ² path verified end-to-end
with a synthetic drop-in (5 matched q3 bins). Our-side PNGs written
(`ascencio_vs_unfolded_q3_{dq3,eavail_in_q3slices}.png`). The Ascencio data file is the one
remaining drop-in — HepData is Cloudflare/member-gated (not fetchable in-session, same as the
E_avail script); format documented in the script header.

**#5 Unbinned goodness-of-fit — DONE (job 53945834).** `unbinned_gof.py`: Classifier
Two-Sample Test (Lopez-Paz & Oquab) between data reco and OmniFold-reweighted MC reco, with
the CV prior as the sensitivity baseline. Result on the frozen 3D inputs:
- PRIOR/CV: acc 0.5226, AUC 0.5353, z=33.4, p≈5e-244 (classifier easily separates data/MC).
- UNFOLDED: acc 0.5009, AUC 0.5014, z=1.36, **p=0.17** (statistically indistinguishable).
The unbinned GoF is both sensitive (caught the prior mismatch at z=33) and PASSES after
unfolding — OmniFold removes the detectable reco-space mismatch. Weights saved to
`of_weights_3d.npz`.

**#4 Train/test-split seedscan + ensemble-mean CV — DONE (array 53946279, 24 splits +
combine 53947036).** `omnifold_loop` gained `train_frac`/`split_seed` (fit each classifier
on a random 80% subset, evaluate on all) — the genuine ML knob, since LightGBM at the
production settings is otherwise ~deterministic in the estimator seed. `seedscan_split.py`
(per split) + `combine_seedscan_split.py` (ensemble mean + cov):
- ensemble-mean total σ = 3.0786e-38 (matches frozen CV 3.0789e-38); run-to-run 0.016%.
- ML-split cov: sqrt-trace 2.645e-40, median rel 0.51%. **1.24× the pure-seed ML cov** — the
  train/test split adds ~24% ML uncertainty the old seedscan missed (the prepub point).
- ensemble-mean vs frozen CV: median shift 0.28%. Wrote `uq_cov_mlsplit_3d.root`.

**#6 PET point-cloud DataLoader — DONE (job 53946101, GPU TF 2.15).**
`minerva_pet_dataloader.py` adapts our event-loop arrays to the vendored
`omnifold.DataLoader`. Smoke test on GPU: the vendored **MLP** AND **PET** (Point-Edge
Transformer) both unfold our MINERvA data end-to-end through `MultiFold` (finite weights,
mean≈1.0). `pointcloud` mode prints an actionable error listing exactly the per-hadron
branches the event loop must dump (`part_reco_{E,px,py,pz,z}`, `part_gen_{E,px,py,pz,pdg}`
from cluster info + `mc_FSPart*`). Point-cloud track is wired; the one remaining piece is
the event-loop per-hadron dump.

**#1 Unified-throw vs block-sum cross-check — IN FLIGHT (job 53946996).**
`compare_unified_throw.py` (superposition test): the unified throw equals the block sum in
the linear regime, so the decisive cheap test is the cross term
`Delta_AB - (Delta_A + Delta_B)` from re-unfolded vertical-band shifts. `--dump` reads the
120 GB 3D universes omnifile once (extended `collect_signal_nd`/`collect_truth_denom_nd`
with `extra_wbranches`); `--analyze` runs CV + single + joint unfolds for MaCCQE/2p2h/MaRES
and reports the cross-term / linear ratio. Restricted to vertical bands (lateral kinematic
shifts can't compose from single-band dumps).

**#3 q3 systematic campaign — LAUNCHED (chained pipeline).**
C++: `runEventLoopOmniFold.cpp` now dumps shifted q3 for lateral universes
(`q3_truth_/MC_q3_/sim_q3_<band>_<idx>`), mirroring pT/pz at all 3 sites. q3 is NOT
lateral-invariant (verified: reco q3 shifts for 100% of passing events under BeamAngleX, ±1σ
pair brackets CV; truth q3 invariant under beam-angle bands, matching truth pT/pz). Rebuilt +
installed. The nd driver gained a `--universe` path with the q3 swap (`lateral_invariant`
axis flag; eavail keeps CV, q3 swaps for lateral universes) + Flux-universe flux division.
Chain (all dependency-gated): evloop array 53945111 (12 playlists, dump-all +q3) →
hadd 53947173 (SetMaxTreeSize merger) → validation universe 53947729 (MuonResolution:0,
exercises the q3 swap) → full 187-universe sweep 53947731 → 4D covariance 53947732
(`analyze_universes_nd.py`, block-sum + norm band). Outputs land under `uq_4d/`.
