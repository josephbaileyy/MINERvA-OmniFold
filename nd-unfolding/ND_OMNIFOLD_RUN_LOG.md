# N-D OmniFold — Run Log (append-only)

## 2026-06-06 — Workstream F: W (hadronic invariant mass) 5th axis + truth diagnostics

Direction B of `../docs/FUTURE_DIRECTIONS.md` — add a physically-motivated 5th axis to
localise the open +2.2σ high-E_avail DIS-tail excess (DIS = high W). Done while the PET
higher-iteration retrain ran. User ask: investigate the other candidate observables too so
the expensive 12-playlist re-run happens ONCE.

**Investigation result:** W is the ONLY candidate with a clean reco estimator (truth
`GetTrueExperimentersW()` already existed; reco from `GetQ2Reco()` + `GetRecoilE()`).
Proton multiplicity and hadronic angle are clean in TRUTH (`mc_FSPart*`) but reco-limited —
the tuples carry only calorimetric clusters (energy+position), no per-particle id/momentum.
So W becomes a real axis; multiplicity/angle are dumped as TRUTH diagnostics (no reco
estimator yet → can't be OmniFold axes, but ready for the excess investigation).

**Code:**
- `CVUniverse.h`: `RecoW()` (mirrors `RecoQ3`: q0=recoil_E, Q² from muon kinematics,
  W=√(M²+2Mq0−Q²)); truth diagnostics `GetNProtonsTrue()` (KE>110 MeV), `GetNChargedPionsTrue()`,
  `GetHadronAngleTrue()` (polar angle of summed FS-hadron momentum).
- `runEventLoopOmniFold.cpp`: full W mirror of q3 across all sites (truth-denom, signal reco,
  miss-append, background, data, + per-universe lateral shifted `W_truth_/MC_W_/sim_W_` since
  W is muon+recoil dependent like q3). Truth diagnostics `MC_nproton/MC_npip/MC_hadangle` on
  the truth-denom cache + signal reco + miss. W/diagnostic branches are unconditional and the
  shifted-W rides the existing `MNV101_DUMP_UNIVERSES` gate → the EXISTING evloop launchers
  now produce W with NO new script (one re-run gives the full 5D + systematics inputs).
- `unfold_nd_omnifold_unbinned.py`: registered axis `W` (`lateral_invariant=False`,
  edges [0,1.1,1.4,1.8,2.2,3.0,100] GeV). `--axes eavail,q3,W` does the 5D unfold.

**Build:** batch job 54061121 COMPLETED clean (no errors).
**Smoke (interactive salloc 54061557, 1×1A file, `MNV101_DUMP_UNIVERSES=BeamAngleX`) — PASS:**
- mc_signal_reco: MC_W median 1.672 GeV (0.18–11.3), sim_W median 1.579 (reco-pass; W²<0→0
  guard as in reco q3); MC_q3 median 1.767 UNCHANGED (no q3/eavail regression); MC_nproton
  med 1/max 7, MC_npip med 1/max 11, MC_hadangle med 0.422 rad (∈[0,π]).
- data measured_W median 1.634; mc_background sim_background_W median 2.403.
- 16,791 truth-only misses appended, no segfault (W is scalar; q3 vector-rebind hazard N/A).
- shifted-W lateral branches present (MC_W_/sim_W_BeamAngleX_0/1); truth W shifts only 1.8%
  under BeamAngleX = correct (truth W from true muon kinematics is beam-angle-invariant, like
  truth q3). `smoke_W.sh` is the durable smoke driver.

**NEXT (gated on user approval — the expensive step):** re-run the 12-playlist event loop
(`sbatch_evloop_array_4d_universes_full.sh`, now also dumps W + diagnostics) → hadd → 5D
unfold `--axes eavail,q3,W` + anchors (W-marginal recovers the frozen 4D) → 5D covariance.


## 2026-06-06 — Workstream E: PET point cloud → REAL absolute cross section (method milestone)

`/plan` decision (user): elevate the validated PET point-cloud from a *shape* cross-check
(`pet_vs_gbdt.py` area-normalizes because PET trains on a 2M subsample) to a **real,
absolutely-normalized, full-statistics** cross section, at **method-milestone** scope
(closure + GBDT cross-check; full PET systematics deferred). Other directions recorded in
`../docs/FUTURE_DIRECTIONS.md`.

**Key enabler:** `MultiFold.reweight(events, model)` applies the trained classifier to *any*
events, so we train PET on a tractable subsample but **evaluate push weights on the full
32.8M gen cloud** (push weight is a normalization-independent per-event ratio), then bin
through the same absolute path the GBDT driver uses.

Code:
- `minerva_pet_dataloader.py`: added `--reweight-all` (after `of.Unfold()`, build the full
  loader and `of.reweight(full_gen, of.model2)` → save full-stats `w_push`,
  `mc_indices=arange(N)`) and `--closure` (pseudo-data = MC reco of pass_reco events).
- `pet_vs_gbdt.py`: added `--absolute` (+`--closure`) mode — bins `w_push*w_truth` via
  `unfold_nd_omnifold_unbinned.histnd`, reads `hCompletenessND_flat` from the GBDT 4D ROOT
  (completeness is reweight-independent), and calls `xsec_nd.extract_cross_section_nd` with
  the dump's flux/POT/nucleons. Writes `xsec_4d_PET_absolute.root` mirroring the GBDT naming
  and reports absolute total σ + per-axis median |Δ| vs GBDT (closure: recovered/truth ≈ 1,
  completeness=1).
- Launchers: `sbatch_pet_train.sh` extended (`--reweight-all`, env NITER/EPOCHS/TRAIN_EVENTS/
  CLOSURE, time→6h, saves `pet_weights_full.npz` / `pet_weights_closure.npz`); new
  `sbatch_pet_xsec.sh` (CPU/ROOT, absolute extraction + closure gate).

**Plumbing test (PASS):** ran `pet_vs_gbdt.py --absolute` on the existing 2M-subsample
weights → PET total σ 1.657e-39, **PET/GBDT = 0.0540 ≈ 2M/32.8M (0.061)**, per-axis |Δ| ~94%
(pure normalization deficit). Confirms the completeness reshape, flux/POT/nucleon load, and
`extract_cross_section_nd` path are correct; full-stats reweight should scale the total ~×16.4
to ≈2.7e-38 (near the GBDT 3.066e-38), leaving only the genuine PET-vs-GBDT method difference.

**Submitted (2026-06-06):** main chain `pet_train(full) 54050740 → pet_xsec 54050741`;
closure chain `pet_train(closure) 54050742 → pet_xsec(closure) 54050743`. Job ids in
`.pet_milestone_jobs.txt`. Gates: full-stats reweight mean≈1; closure recovered/truth≈1;
absolute PET/GBDT total ratio near 1 within the ML band.

**RESULTS (2026-06-06, all jobs COMPLETED) — milestone ACHIEVED.**
- **Gate 1 (full-stats reweight, mean≈1, finite) — PASS.** main `w_push` over 32.8M gen:
  mean **1.0277** std 0.107 finite; closure: mean **0.9884** std 0.0016 finite.
- **Gate 3 (closure recovered/truth ≈ 1) — PASS (decisive).** PET unfolding MC-reco-as-
  pseudo-data recovers MC truth: total **0.9884**, per-axis median |Δ| **pt 1.14% / pz 1.13%
  / eavail 1.15% / q3 1.13%** (uniform). ⇒ the absolute-extraction machinery
  (`extract_cross_section_nd` + GBDT completeness + flux/POT/nucleons) is **unbiased**;
  `xsec_4d_PET_closure.root`.
- **Gate 2 (absolute PET vs GBDT) — PET total σ = 2.796e-38 vs GBDT 3.066e-38, ratio
  0.9117**; per-axis median |Δ| pt 7.69% / pz 9.88% / eavail 9.31% / q3 6.47%
  (`xsec_4d_PET_absolute.root`, `pet_vs_gbdt_absolute.png`). The ~9% gap is **larger** than
  the ML band — but since closure is exact to ~1%, it is a genuine **training-config**
  difference (PET trained on the 2M subsample, niter=2/epochs=8, vs the full-stats 5-iter
  GBDT), not a normalization bug. PET under-iterates → pushes the real-data result less far
  from the prior than the GBDT does.

**Milestone status:** the PET point cloud now yields a **real, absolutely-normalized,
full-statistics** cross section, validated unbiased by closure (~1%) and cross-checked vs
GBDT (~9%, training-limited). This completes the method milestone (full PET systematics
deferred, `../docs/FUTURE_DIRECTIONS.md`). Obvious next tuning (not required for the
milestone): retrain PET with more iterations/epochs/events to close the ~9% GBDT gap toward
the ML band before the systematics campaign.


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

### 2026-06-04 (cont.) — #4 follow-through: ML-split band in the combined budget
`compare_mlsplit_combined.py` (non-destructive): the train/test-split ML cov is 1.24x the
seed-only ML cov (sqrt-trace 2.131e-40 -> 2.645e-40), but ML is sub-dominant, so the
COMBINED 3D budget moves only +0.04% (sqrt-trace 5.7243e-39 -> 5.7265e-39; median rel
uncertainty 10.374% -> 10.370%). Conclusion: adopt the larger, more honest split-ML band —
negligible total cost, removes the "init-only ML proxy" caveat. (Ascencio data for #2 stays
member-gated: confirmed absent from HepData/in-session, the MINERvA data-release page, and
arXiv ancillary; the overlay is a one-file drop-in.)

### 2026-06-04 (cont.) — A/B/C parallel tracks + #1 result

**#1 unified-throw — COMPLETED (job 53946996), result needs the jitter caveat.**
The +1sigma superposition test (MaCCQE/2p2h/MaRES) found cross-term/linear of 25-58%
(largest MaCCQE x MaRES 58%, per-bin median 24-48%) -- NOT the clean "<10% => linear".
BUT at this magnitude the OmniFold run-to-run jitter floor must be subtracted before
claiming genuine nonlinearity (the difference-of-differences accumulates ~4x the per-unfold
jitter; the ML-split study found ~0.5%/bin). A jitter null-mode was added
(compare_unified_throw.py --null: a 2nd CV unfold at seed+1) and re-run (job 53953284) to
make the number interpretable. Honest status: the single-seed superposition test is a cheap
probe that flags possible nonlinearity; the rigorous object remains a many-throw unified
covariance (where jitter averages down). So #1's answer: block-sum linearity is NOT cleanly
confirmed -> a full unified-throw covariance is the recommended pre-pub study (as flagged).

**B — refreshed combined cov + generator chi2 with split-ML band (job 53950089).**
write_combined_splitml.py wrote uq_combined3d_splitml.root (syst+stat+ML_split). The
4-generator full-cov chi2 ranking is UNCHANGED (Tune-v1 best, GiBUU worst; diagonal chi2/ndf
identical, e.g. Tune-v1 4.8->4.8). The split-ML band raises the cov rank 247->261 and shifts
the truncated chi2 slightly but changes NO physics conclusion -- the robustness check passes.
(compare_3d_fullcov_{oldml,splitml}.png)

**C — NTRIAL ensemble-mean CV (ensemble_cv.py).** The #4 split trials ARE the NTRIAL
ensemble; ensemble_cv.py turns the 24 trials into the ensemble-mean CV product
(ensemble_cv_3d.root: hXSec3D_ensembleMean + hSigma3D_ensembleSpread). Ensemble spread
(ML band) median 0.51%/bin; ensemble-mean vs frozen single-run CV median shift 0.28%.
This is the rhuang1/OmnifoldT2K + Mikuni n_ensemble convention.

**A — per-hadron point cloud (Phase 3): C++ DONE + validated, full pipeline chained.**
CVUniverse::GetTruthFSHadrons (mc_FSPart*, muon+nu dropped) + GetRecoClusters
(ExtraEnergyClusters_*) feed a gated point-cloud dump in runEventLoopOmniFold.cpp
(MNV101_DUMP_POINTCLOUD=1, off by default): per-event part_gen_{E,px,py,pz,pdg} +
part_reco_{E,x,y,z} on signal, part_reco_* on data. Rebuilt + smoke-verified (gen <4.4>,
reco <6.75> per event; example particle E=1179 MeV pdg=2212 proton). Bug found+fixed: the
miss-append (AppendTruthOnlyMisses) must rebind the vector branches via pointer-to-pointer
to empty vectors, else Fill() reads the signal loop's freed locals -> segfault.
dump_pointcloud_inputs.py reads + zero-pads the vectors to num_part=12 (validated on the
smoke file: gen (N,12,5), reco (N,12,4)); minerva_pet_dataloader.py pointcloud mode reads
the resulting npz into the vendored PET. Chained (CV-only, cheap): evloop_pc 53953733 ->
hadd+dump 53953910 -> PET train 53953911.

### 2026-06-04 (cont.) — #1 jitter-null RESOLVES the superposition probe
Jitter null (job 53953284, compare_unified_throw.py --null): ||CV(seed+1)-CV(seed)|| =
3.76e-40, so the difference-of-differences jitter floor (x4) = 1.50e-39. The largest
measured cross term ||cross|| = 1.18e-39 is BELOW that floor (cross/floor = 0.8x). So the
earlier "25-58% cross/linear" is dominated by OmniFold run-to-run jitter, NOT genuine
cross-band nonlinearity. Corrected conclusion: the single-throw superposition probe shows
NO clean evidence of nonlinearity (it is jitter-limited) -> consistent with the block-sum
being valid; the full unified-throw covariance (160 throws, jitter averages down as
1/sqrt(T)) is the definitive test and is running (dump 53956788 done + bank verified ->
throws 53956789 -> combine 53956790).

### 2026-06-04 (cont.) — sweep I/O optimization + 4D combined budget prep (in-flight state)

**q3 sweep is I/O-bound, not compute-bound.** Single-universe unfold timing: npz path 10 min
(16 cpu), full ROOT-read path 35-40 min (32 OR 128 cpu) -> the ~25 min single-threaded
PyROOT GetEntry read dominates; cores past ~16 don't help. So the sweep was switched
regular/128 -> **shared/32/%32** (same per-job time, faster to schedule, ~4x cheaper).

**Read-once bank (sweep_bank.py).** Durable speedup for re-runs: one GetEntry pass per group
banks the 175 VERTICAL universes' weights (mmap'd) instead of 187 re-reads; stage-2 unfolds
read an mmap slice (~10 min, no 120 GB read) and write the sweep's filename + hXSecND_flat
with skip-if-exists. The 12 LATERAL universes stay on the per-universe path (they gate on
shifted kinematics -> different kept-set each). Canonical covariance stays single-code-path
(the shared sweep); the bank is for re-runs (iters/binning) + the 4D unified throw.

**4D combined budget chained.** dump 4D npz (53961411) -> {ML seedscan x24 (53961806),
stat bootstrap x100 (53961808)} -> combine (53961810) -> combined budget (53961846,
analyze_universes_nd --bootstrap-cov C_syst+norm+C_stat+C_ML). bootstrap_nd.py +
combine_cov_nd.py are the lean npz-based 4D stat/ML tools.

**IN-FLIGHT JOB IDS (for resumption):** shared q3 sweep 53960731 -> cov4d 53960732;
sweep-bank dump 53960918; unified-throw run 53956789 -> combine 53956790; point-cloud
pc_down 53953910 -> PET 53953911; 4D budget chain 53961411/806/808/810/846.

**#1 RESOLVED:** jitter-null showed the superposition cross-terms (25-58%) are AT the jitter
floor (0.8x) -> noise, not nonlinearity -> leans block-sum-valid; full 160-throw unified
covariance (running) is the definitive test.

### 2026-06-04 (cont.) — PET point-cloud: pipeline validated, reco-cluster branch WRONG (follow-on)
The Phase-3 PET run exposed (validate-as-it-lands working): (1) shape crash -- gen carried
pdg (5 feat) vs reco 4; fixed (drop pdg, per-step feat counts). (2) NaN loss -- raw scales;
fixed (x1/1000, multiplicative to keep the energy==0 mask, net.py:128). (3) DECISIVE: the
reco cloud is built from the WRONG branch -- ExtraEnergyClusters_* is 94.7% empty in MC and
100% empty in DATA (an auxiliary collection, not the recoil). So PET step-1 (reco) still
NaN's (every cloud masked-empty) and the PET result (push mean 0.30) is NOT trustworthy --
do not report any PET-vs-GBDT number from it. The gen cloud (mc_FSPart, 27% empty, mean 3.17)
is correct.
FIX (follow-on, needs event-loop re-run): CVUniverse::GetRecoClusters should read the real
per-cluster recoil collection -- `cluster_energy`, `cluster_pos`, `cluster_z` (217
clusters/event in data), filtering `cluster_isMuontrack==0` for the non-muon hadronic
clusters. Then rebuild -> re-run the PC event loop -> re-dump (dump_pointcloud_inputs) ->
re-run PET -> pet_vs_gbdt. The whole PET PIPELINE (engine, masking, scalar storage, dump,
comparison) is built + validated; only the reco-cluster source branch is wrong.

### 2026-06-04 (cont.) — unified-throw combine: ratio-product construction is ARTIFACT-prone
Ran the unified-throw combine on 145 throws: unified/block-sum sqrt-trace ratio = 25x, one
eigenmode ~1000x the block-sum's, median rel 17% vs 8%. This is NOT a block-sum refutation --
it is an ARTIFACT. Diagnosis: throw TOTALS are sane (median 2.88e-38, +-6.3%, no outliers),
so the inflation is in a few low-stat BINS, not normalization. Root cause: the throw
MULTIPLIES single-band reweight ratios (w_band/w_cv) across 13 bands; for events with small
w_cv and/or several bands in their tails this compounds into large per-event weights that
land in specific bins (and the 145 throws were produced BEFORE the 99.9pct weight-cap commit
acb0239). Multiplying single-band ratios is NOT equivalent to re-unfolding a genuinely
jointly-shifted sample, so its covariance is not trustworthy.
DECISION: do NOT report the 25x. The methodologically sound #1 cross-check is the jitter-null
SUPERPOSITION test (additive Delta on re-unfolded deltas), which found cross-terms at the
OmniFold jitter floor -> block-sum consistent. A RIGOROUS unified throw requires TRUE
multi-band universes (event loop applying all systematics together per universe) -> a
documented follow-on, not the ratio-product proxy. unified_throw.py keeps the bank/throw
machinery but its combine output carries this caveat.

### 2026-06-04 — CONSOLIDATED bugs & fixes (this campaign)
Single index of every bug/artifact found and how it was resolved (commit in parens):

CODE BUGS (fixed):
1. Unified-throw bank dump OOM (64G) — python-list ratio accumulators at 33M events x ~26
   cols. Fix: typed array('f')/('d')/('b') accumulators (~8x leaner) + 110G. (627a920)
2. Point-cloud miss-append segfault — AppendTruthOnlyMisses Fill() read the signal loop's
   freed local std::vectors. Fix: rebind the part_* vector branches via pointer-to-pointer
   to empty vectors (ROOT object branches need vector<T>**, not vector<T>*). (2ff1dd5)
3. PET step-2 shape crash (expected (12,4) found (12,5)) — gen cloud carried the pdg column.
   Fix: drop pdg + build m2 with the gen feature count. (617d378)
4. PET 'Last val loss nan' — raw feature scales (positions ~1000s mm). Fix: x1/1000
   MULTIPLICATIVE scaling (keeps the energy==0 particle mask, net.py:128). (617d378)
5. LightGBM degenerate-split error (best_split_info.right_count>0) on extreme throws. Fix
   (throw path only, canonical estimator untouched): 99.9pct weight cap + try/except skip.
   (acb0239); same guard added to 4D bootstrap/seedscan (NO cap there -- would bias stat/ML).
   (c70397e)
6. Misleading throw log (printed sum of differential bins ~1e-36, not the integral). Fix:
   log total_xsec. (ae47278)
7. write_combined_splitml relative-path bug (ran from genie/, needed ../). Fixed inline +
   re-run (B job 53950089). 
10. pc_down (dump_pointcloud_inputs.py) OOM-killed at 48G (MaxRSS 50.3G) after looping all
    32.8M signal events -- python LIST of 32.8M small (P,nfeat) clouds + the np.asarray copy
    coexist at the end. Fix (same family as #1): PREALLOCATE contiguous (n,P,nfeat) float32
    arrays, fill by index k, slice [:k] (signal+data); ~15G peak. Launcher also skips the
    re-hadd if the 46G merged omnifile exists + skips the dump if of_inputs_pc.npz exists +
    --mem 48G->96G. Re-launched pc_down 54014343 -> PET 54014344. evloop_pc array (12/12) had
    COMPLETED fine; only the downstream reducer OOM'd. (7c81032)
11. q3 bank sweep universe NormDISCC:0 (banksweep _158) FAILED "sample_weight contains NaN"
    in the LGBM step-2 fit. Root cause: the bank DUMP left 83727 NaNs in NormDISCC_0_wt.npy
    (DIS-norm reweight is 0/0 for events with no nominal DIS contribution); healthy universes
    have 0 NaN. Fix (sweep_bank.py run stage): np.nan_to_num(wt,wr,tdw, nan=0 ...) at load --
    an undefined reweight contributes 0; no-op on finite universes. Re-ran _158 -> 54021365.
    This is the 187th q3 universe that gates cov4d. (uncommitted as of 2026-06-05)

DATA/METHOD BUGS (found; one needs a follow-on):
8. PET reco cloud built from the WRONG branch -- ExtraEnergyClusters_* is 94.7% empty (MC)
   / 100% empty (data). Correct: cluster_energy/cluster_pos/cluster_z, isMuontrack==0.
   FOLLOW-ON (needs event-loop re-run); no PET-vs-GBDT number reported. (35b4130)
9. Unified-throw ratio-product combine ARTIFACT (25x vs block-sum) -- multiplying single-band
   reweight ratios compounds low-w_cv tail events; NOT a valid joint throw. NOT reported.
   Valid #1 = jitter-null superposition (block-sum consistent); rigorous = true multi-band
   universes (follow-on). (29b7676)

EARLIER SESSION (already documented in prior RUN_LOG / omnifold_nn_core / memory): 4D
THnSparseD write segfault (-> flat TH1D); NN class-balance bias + unshuffled validation_split
(-> _balance_weights + permute); xsec_nd ULP exact-equality (-> relative tolerance).

### 2026-06-04 — interactive sweep orchestration + IN-FLIGHT MANIFEST
Batch fairshare throttled to ~2 slots after running hundreds of jobs, so the q3 vertical
bank sweep was moved to an INTERACTIVE node: `run_q3_sweep_interactive.sh` runs INSIDE an
salloc (`salloc --qos interactive ... bash run_q3_sweep_interactive.sh`) and launches up to
10 concurrent `srun --overlap` sweep_bank --run steps (skip-if-exists -> resumable across
salloc windows). MONITOR BY OUTPUT-FILE COUNT, not the salloc stdout (it buffers; a working
run looked "stuck" and was wrongly cancelled once -- lesson logged). PC event loops can run
the same way (run_pc_evloop_interactive.sh) but were put back on batch for simplicity.

IN-FLIGHT MANIFEST (jobs that should be in squeue; anything else is unexpected):
  - q3 vertical sweep: INTERACTIVE salloc (run_q3_sweep_interactive.sh), 175 bank-unfolds
  - q3 lateral: batch unfold4d_lat (sbatch_unfold_4d_lateral.sh), 12 driver unfolds
  - PC chain: batch evloop_pc -> pc_down -> PET (sbatch_evloop_array_pointcloud/pc_downstream/pet_train)
  - 4D stat: batch boot4d (sbatch_bootstrap_4d.sh) x100
  - 4D ML:   batch ssplit4d (sbatch_seedscan_split_4d.sh) x24
  - 4D stat+ML combine: batch comb4d_statml (afterok boot+ssplit)
  - q3 cov4d + 4D budget: run MANUALLY (analyze_universes_nd + combine_4d_budget) once all
    187 q3 universe files are present (the chained batch versions were cancelled in the
    interactive switch to keep the queue free of doomed-dependency zombies).

### 2026-06-06 — PET point-cloud refresh completed with corrected reco-cluster source
Reason for rerun: `pet_vs_gbdt.png` was stale because the first point-cloud chain used
`ExtraEnergyClusters_*`, which the 2026-06-04 audit found to be 94.7% empty in MC and
100% empty in data. Source inspection showed `CVUniverse::GetRecoClusters()` now uses the
real cluster collection (`cluster_energy`, `cluster_pos`, `cluster_z`) and filters
`cluster_isMuontrack`, so the stale artifact was replaced by a full point-cloud refresh.

CPU side was run inside the current interactive allocation, not as a new batch array:
rebuilt/installed `runEventLoopOmniFold`; reran all 12 point-cloud playlist event loops
with `MNV101_DUMP_POINTCLOUD=1`; `hadd` rebuilt
`runEventLoopOmniFold_PC_MEFHC.root` (46 GB, timestamp 2026-06-05 19:26 PDT);
`dump_pointcloud_inputs.py --num-part 12` rebuilt `of_inputs_pc.npz` (5.5 GB,
timestamp 2026-06-05 19:59 PDT). The dump reported:
`signal clouds: gen (32849103, 12, 5), reco (32849103, 12, 3); data
(4091707, 12, 3); num_part=12`. Existing merged/NPZ artifacts were archived with
`.stale_20260606T005039Z` / `.stale_20260606T022515Z` suffixes as applicable.

GPU PET training and comparison then completed:
- PET training job 54033990 (`pet_train`, gpu_shared): COMPLETED 0:0, 00:58:24.
  It ran the real point-cloud `MultiFold` on 2M events, with
  pass_reco=0.621, pass_gen=1.000, and saved `pet_weights.npz` (14 MB). Final smoke
  line: unfolded weights n=2000000, mean=1.0004, std=0.1157, finite=True.
- PET-vs-GBDT comparison job 54033991 (`pet_cmp`, shared): COMPLETED 0:0, 00:00:30.
  It archived the previous plot as `pet_vs_gbdt.png.stale_20260606T061012Z` and
  regenerated `pet_vs_gbdt.png` (109 KB, timestamp 2026-06-05 23:10 PDT).

Refreshed PET-vs-GBDT area-normalized shape median |diff| values:
- pT: 3.86%
- pz: 2.36%
- Eavail: 2.63%
- q3: 2.33%

Interpretation: with the corrected reco-cluster source, the point-cloud PET shape agrees
with the scalar 4D GBDT result at the few-percent level on the PET subsample. This is a
valid refreshed method/shape cross-check. It is not an absolute normalization measurement:
`pet_vs_gbdt.py` intentionally area-normalizes because the PET training uses a subsample.

---

## 2026-06-07 — Workstream E (PET hi-iter retrain) + Workstream F (W 5D unfold) landed

Both in-flight job chains from 2026-06-06 completed and validated.

### Workstream F: W (hadronic invariant mass) as 5th axis — 5D unfold PASS

5D CV event-loop array `evloop5d` (54062311, 12 playlists) COMPLETED, then
`hadd_unfold_5d` (54062313) merged -> `runEventLoopOmniFold_5D_MEFHC.root` (4.5 GB) and
ran the `--axes eavail,q3,W` (5D = pt,pz,eavail,q3,W) unfold (5 iter, lgbm):

- total sigma (5D integral): **3.07e-38 cm^2/nucleon**
- W-marginal -> frozen 4D anchor: **5D/4D = 1.0011** (PASS, <3% target). Per-shared-axis
  median |5D-4D|/4D: pt 0.68%, pz 0.31%, eavail 0.91%, q3 1.48% (max 4.22%). Adding W as a
  feature does not bias the lower-D projections or the total (same discipline as 4D/3D=0.9960).
- new dsigma/dW: 6 bins, all-finite, nonneg, integral 3.07e-38 (consistent with total).
- injected-W-shape closure (`closure_5d_Wbump.root`, A=0.3 bump): **median 1.0000, std 0.0062,
  max|dev| 0.227**; W 1D ratios all 1.000; injected mean factor 1.0000. The 5D machinery
  recovers an injected W shape without bias.

Artifacts: `xsec_5d_MEFHC_5iter_lgbm.root`, `closure_5d_Wbump.root`. The W axis is now a
validated 5th dimension; the 187-universe W systematic campaign remains deferred (binary
already dumps shifted W under MNV101_DUMP_UNIVERSES — no new code needed).

### Workstream E: higher-iteration PET retrain (niter5/epochs10/4M)

`pet_train` (54060166, gpu_shared) COMPLETED 05:53:53 — trained the real point-cloud MultiFold
on 4M events, then ran the **full-stats reweight-all** push-weight evaluation:
- unfolded (train) weights n=4,000,000 mean=1.0101 std=0.1631 finite=True
- full-stats w_push n=**32,849,103** mean=1.0101 std=0.1630 finite=True -> `pet_weights_full_hi.npz` (137 MB)

`pet_xsec` (54060169, CPU) COMPLETED — absolute extraction reusing the frozen GBDT
`hCompletenessND`:
- PET total sigma (4D) = **2.751e-38** cm^2/nucleon (n_truthpass=32,849,103, data_pot=1.057e21)
- GBDT total sigma = 3.066e-38; **PET/GBDT = 0.8970**
- per-axis median |diff| (ABSOLUTE): pt 7.52%, pz 11.57%, eavail 11.08%, q3 6.83%

Artifacts: `xsec_4d_PET_absolute_hi.root`, `pet_vs_gbdt_absolute_hi.png`.

Interpretation: the higher-iteration/epoch/larger-subsample retrain did **not** close the
~10% absolute PET/GBDT normalization gap (0.9117 at niter3/2M -> 0.8970 here); it is
essentially flat. This is consistent with a training-configuration / point-cloud-vs-scalar
architecture difference rather than a bug in the absolute machinery — the absolute extraction
path itself is validated by the clean closure (recovered/truth ~0.99) from the milestone run.
Closing the gap toward the ML band would require a PET-specific systematic/ensemble campaign
(deferred, docs/FUTURE_DIRECTIONS.md), not more iterations of a single training.

---

## 2026-06-07 — (E_avail, W) excess test: open question 6 is DIS-like (high-W)

`excess_eavail_W.py` (job run on interactive node nid004154, ~min) compares the unfolded
5D data cross section to the **GENIE CV prediction** (the OmniFold prior = POT-scaled
`mc_truth_denom`, completeness=1, pushed through the SAME `extract_cross_section_nd`) in the
(E_avail, W) plane. Single I/O pass over the 4.5 GB 5D omnifile (kept 32,846,302 truth events).

**Overall:** data/CV = 1.135 (the known ~13% integrated excess over GENIE CV).

**dσ/dE_avail data/CV rises toward high E_avail** — 1.18, 1.15, 1.09, 1.03, 1.11, 1.17,
**1.22** across the 7 bands; the two highest-E_avail bands (1.5–3.0, 3.0+) carry 25.3% + 31.8%
= **57% of the total positive excess**. This is open question 6's +2.2σ high-E_avail excess
at central value.

**WHERE in W (the new information):** the high-E_avail excess is **predominantly high-W
(DIS/transition)**. Of the positive excess, high-E_avail (≥0.8 GeV) carries **67.2%**, and
**83.2% of that sits at W≥1.8 GeV**. The single largest excess cell is the deep-DIS corner
(E_avail>3, W>3) at **21.9%** of all positive excess; (E_avail 1.5–3, W 1.8–2.2)=10.6% and
(E_avail 1.5–3 / 3+, W 2.2–3)=8.6%/7.1% follow — all high-E_avail × high-W. So the missing
strength behaves like a **deep-inelastic-tail modeling deficit**, exactly the hypothesis the
W axis was added to test.

**Secondary structure:** a low-W (W<1.1) excess of ~24–31% above CV across all E_avail (a
QE-like component, ~25% of positive excess but spread thin), and a localized **deficit**
(data<CV, ratio ~0.89–0.96) at W 1.4–1.8 for low/moderate E_avail (the Δ-resonance region) —
GENIE CV slightly over-predicts there.

**Caveat:** this is vs the GENIE CV only (single generator, no systematic covariance) — it
localizes the central-value excess, it does NOT re-derive the +2.2σ significance. Extending
to NuWro/GiBUU in (E_avail, W) (the `3d-unfolding/genie/` machinery run through W) is the
follow-up to turn this into a generator-band statement. Artifacts:
`products/5d/excess_eavail_W.{root,png}`.

## 2026-06-08 — Three-campaign closeout (PET 4D cov + (E_avail,W) generator band + rigorous unified throw)

Driven under a `/goal` to complete all three recorded follow-ons in parallel. Branch
`nd-campaign-genband-petsyst-uthrow` (off main after the 2026-06-07 work landed). Two
correctness saves this session: (i) `bank_uthrow` stores per-event universe/CV **ratios**
(median 1.0), NOT absolute weights — caught before it inflated both new covariances ~5×;
(ii) on interactive nodes LightGBM oversubscribes all cores across parallel procs (≈0 progress)
— sbatch's cgroup limit (16 cores/task) is required, so all the heavy re-unfolds run via sbatch.

### A. PET 4D combined covariance — `pet_systematics.py` → `products/pet/pet_4d_covariance_combined.root`
Publication-grade completion of the PET milestone (FUTURE_DIRECTIONS Sec 0). Frozen-reweighter
path: the trained full-stats PET push weights (`pet_weights_full.npz`) are held fixed and
re-binned per **reweight** universe (no per-universe re-inference — reweight universes share the
clouds), with the per-event ratios from `bank_uthrow` (verified bit-identical gen ordering to
`of_inputs_pc.npz`, w_truth diff = 0 over 32.85M events) and the CV completeness anchored to the
validated GBDT `hCompletenessND` (median rescale 1.215 → CV total σ 2.80e-38, matches milestone).
**Budget, median per reported bin (4796 bins):** C_syst **18.3%** (block-sum, 12 GENIE knobs +
100 flux universes, flux-dominated), C_stat **4.2%** (100 Poisson bootstraps), C_ML **3.3%**
(CV-vs-hi-iter training spread), **C_total 22.4%** — same syst>stat>ML hierarchy as the GBDT 4D
budget. Lateral (kinematic-shift) universes are the one approximation (frozen reco clouds).

### B. (E_avail,W) generator band — `3d-unfolding/genie/`, `overlay_eavailW_band.py` → `eavailW_band.{png,root}`
Turns open question 6 from a single-generator localization into a **generator-band statement**.
Regenerated GENIE-CV (2M, `gevgen`), GENIE+Valencia-MEC (1.5M), and NuWro (2M; native Enu threaded
through `nuwro_to_flat.C` for an experimenter's-W branch — verified, NuWro W median 1.92 GeV). New
`gen_to_xsec_eavailW.py` / `nuwro_to_xsec_eavailW.py` bin each onto the data's (E_avail,W) axis
(spline / per-event normalisation; W replicates `GetTrueExperimentersW`). **Result: the high-W
DIS excess is generator- AND tune-robust.** All three underpredict the high-E_avail×high-W corner
by 54–58% (data/gen = 1.54 CV, **1.58 +MEC**, 1.56 NuWro); enabling Valencia 2p2h does NOT close
it — it slightly **worsens** the corner (2p2h is low-W) — and NuWro misses it by the same margin.
At W∈[2.2,3.0) all three sit 23–25% below data (data 7.48e-39 vs 5.62–5.76e-39). GiBUU excluded
(`FinalEvents.dat` lacks per-event Enu). Propagated to technote item 6 + FUTURE_DIRECTIONS Sec B.

### C. Rigorous unified-throw covariance — `unified_throw_cov.py` → `uq_4d/unified_throw_cov.root`
The methodologically sound replacement for the artifact-prone ratio-product proxy (2026-06-04):
compose per-**event** weights `w_cv·∏_b ρ_b^{g_b}` (g_b~N(0,1) over the 12 reweight knobs) + one
sampled flux universe, then **re-unfold** each throw (OmniFold), and build the covariance directly
— the construction a true multi-band event-loop universe would produce, for the reweight bands.
75 throws (sbatch array + interactive, incremental-saved) vs a parallel block-sum (12 knobs + 12
flux units). **Result: sqrt-trace unified/block = 1.40 (per-bin σ median 1.16).** A jitter null
(2nd CV unfold) shows the OmniFold run-to-run floor is tiny (sqrt 3.07e-40, ~10× below the
cross-term), so the **jitter-corrected ratio is still 1.40** — the excess is real, not a seed
artifact. So the iterative unfolding combines the systematic bands with a significant **positive
nonlinear cross-term** (97.6% of the block-sum trace) that the block-sum drops: **the block-sum
underestimates the systematic covariance by ~16% per bin (robust median) to ~40% in sqrt-trace.**
This refines the prior single-throw probe ("cross-terms at the jitter floor → leaned block-sum
valid"); the full 12-band joint throw reveals the aggregate nonlinearity the pairwise probe could
not. Caveat: the median (1.16) is the robust statement; the larger sqrt-trace (1.40) is partly
driven by a few high-variance bins where Gaussian-tail throws compound several knobs. The unified
throw is the more conservative, correct object. Artifacts: `uq_4d/unified_throw_cov.root`
(C_unified, C_blocksum, C_cross), throw + block slabs under `uq_4d/uthrow_slabs/`.

## 2026-06-08 (cont.) — Four-extension campaign LAUNCH (rigorous follow-ons to the closeout)

Under a `/goal` to accomplish all four post-closeout extensions. Deep scoping first established
that the cheap shortcuts are blocked by data-alignment gaps (the PC bank, the 5D/W omnifile, and
the stored throw slabs use different event orderings / lack the needed columns), so each extension
needs either an event-loop/generator re-run or a careful bank reconstruction. New code written this
session: `dump_td_q3.py`, `assemble_bank_4d.py`, `pet_lateral_correction.py`,
`3d-unfolding/genie/gibuu_to_xsec_eavailW.py`, launchers `sbatch_td_q3.sh`, `sbatch_assemble_4d.sh`,
`sbatch_uthrow_{cov,block,combine}_4d.sh`, `sbatch_evloop_array_5d_universes_full.sh`,
`sbatch_pet_lateral.sh`, `sbatch_gibuu_mirror.sh`; `compare_unified_throw._xsec_for_weights`
generalized to an N-D truth-denom stack (4D-ready, 3D back-compatible).

### Task 14 — rigorous 4D unified throw (the 3D run was a probe). LAUNCHED, self-contained.
The 3D unified throw measured block-sum underestimation (1.16 median / 1.40 trace) on a coarse
(pt,pz,eavail) grid. To adopt it for the published 4D covariance it must live on the real
(pt,pz,eavail,q3) binning. The throw machinery is binning-agnostic (`d["edges"]` from the bank);
the only missing column was the truth-DENOMINATOR q3 (`bank_uthrow` is 3D). `dump_td_q3.py` recovers
it in one I/O pass over the 4D `_universes_full` omnifile's `mc_truth_denom` (collect_truth_denom_nd
is deterministic -> same ordering; the dump ASSERTS td_w bit-identity to the bank before writing).
`assemble_bank_4d.py` then builds `bank_uthrow_4d/` (q3 from the PC cloud -- verified max|diff|=0 to
the bank rows; data 4D from `of_inputs_4d`; weight arrays symlinked, binning-independent). Chain:
`td_q3`(54189950) -> `asm4d`(54190008) -> 4D throw array + block array -> combine ->
`uq_4d/unified_throw_cov_4d.root` (C_unified_4d/C_blocksum_4d/C_cross_4d, jitter-null corrected).

### Task 15 — PET lateral band, engine-independent. LAUNCHED (`pet_lat` 54190130).
The PET 4D budget froze the reco clouds, so lateral (detector-response) universes contributed ZERO
(its one approximation). `pet_lateral_correction.py` transfers the GBDT-measured lateral FRACTIONAL
covariance (sum of the 6 detector bands from `uq_universe_4d_covariance_combined.root`) onto the PET
bins via the shared 10976-cell grid: laterals are pure detector response, ~independent of the GBDT-vs-
PET density-ratio step, so the fractional response transfers. Adds `C_lateral` + refreshes `C_total`
in `products/pet/pet_4d_covariance_combined.root`. Full per-lateral PET re-inference (re-dump lateral
reco clouds + GPU re-inference) recorded as the residual deferral.

### Task 13 — generator-band significance via the (E_avail,W) covariance. GATING STEP LAUNCHED.
The fully-rigorous (E_avail,W) systematic covariance needs universe weights on the W-carrying events;
the 5D omnifile is CV-only and the W axis postdates the 4D systematic campaign, so the gating step is
a 5D `_universes_full` event-loop re-run (`ev5duni` 54190271, MNV101_DUMP_UNIVERSES, ~24h; the binary
already dumps shifted W). Confirmed NOT needing the multi-day 187-universe re-unfold sweep: the
completion path is the frozen-reweighter block-sum on the (E_avail,W) marginal (same methodology as
`pet_systematics`) + stat bootstrap + transferred lateral, then chi^2/significance of data vs each
generator in the high-W DIS corner (turns "data/gen=1.54" into N-sigma). [Tried + rejected cheaper
paths: PC-bank<->5D-omnifile scalar matching (orderings differ), and per-event W reconstruction from
the truncated 12-particle PC cloud (biased: W piles up 2.3x at W<1.1 and 1.9x at W>3).]

### Task 16 — GiBUU as the 4th band generator. LAUNCHED (`gibuu_mir` 54190366 -> regen).
The real blocker was that FinalEvents.dat was deleted in the cleanup (NOT a missing Enu -- col 15 IS
enu, the muon is ID 902, so experimenter's W is computable with no format change). `gibuu_mirror`
rebuilds the cleaned-up buuinput short-path mirror (CVMFS, compute node) then submits the 80-run regen;
`gibuu_to_xsec_eavailW.py` (written) bins it into (E_avail,W). Lowest-value extension (the band is
already 3-generator robust at 54-58% corner deficit) -- run as low-priority confirmation.

### Task 15 RESULT (DONE 2026-06-09) — PET lateral band folded in.
`pet_lateral_correction.py` transferred the GBDT lateral (6 detector bands) FRACTIONAL covariance
onto all 4796 PET reported bins (full 10976-grid overlap, 0 missing). Sanity: the transferred PET
lateral median frac (4.03%) matches the source GBDT lateral (4.02%) -- the fractional map preserved
magnitude. Updated PET 4D budget (median frac/bin): syst 18.31% / stat 4.18% / ML 3.32% / **lateral
4.03%** -> **TOTAL 23.02%** (was 22.4% with lateral=0). Small, as expected (lateral is subdominant),
but closes the one zero in the PET budget. `products/pet/pet_4d_covariance_combined.root` now carries
C_lateral + refreshed C_total. Residual deferral: full per-lateral PET reco-cloud re-inference.

### Task 13 INTERIM RESULT (2026-06-09) — dsigma/dEavail generator significance (the E_avail projection).
`eavail_generator_significance.py` marginalizes the published 4D combined covariance
(uq_universe_4d_covariance_combined, syst+stat+ML) to the E_avail axis via the project_marginal
linear map (C_y = M C_4d M^T, 7x7) and does a full-covariance chi^2 of data vs each generator's
dsigma/dEavail (the band files' hXSec_eavail). **The unfolded data is incompatible with all three
generators at high significance:** chi^2/ndf(7) = 725/7 (GENIE-CV), 865/7 (GENIE+MEC), 665/7 (NuWro)
-> nominal 25-29 sigma. Honest reading (diagnostics in-script): C_y is correlation-dominated
(condition number 8.7e5, smallest eigenvalue carries the shape direction), so the chi^2 lives in the
shape directions. Per-bin pulls (data-gen)/sqrt(diag) for GENIE-CV: [1.5, 7.7, 5.3, 0.8, 1.6, 4.5,
18.6] with data/gen ratio [1.07, 1.35, 1.18, 1.03, 1.05, 1.16, **2.41**]; the deep-DIS catch bin
[3,100] GeV dominates (18.6 sigma, data/gen 2.4x) BUT the result is robust to dropping it (~10 sigma
from the resolved bins: 7.7 sigma at 0.1-0.2, 5.3 at 0.2-0.4, 4.5 at 1.5-3.0). NuWro similar (broad,
+pulls at low AND high E_avail). So the open-question-6 excess is now a HIGH-SIGNIFICANCE,
multi-generator, full-covariance statement on the E_avail projection -- a broad excess strongest in
the DIS tail. Caveat: the [3,100] catch-bin uncertainty drives the headline number; the W-resolved
corner significance (which W cell) follows from the 5D `_universes_full` campaign (ev5duni, ~24h) ->
the (E_avail,W) covariance. GiBUU pending its regen. Run via the interactive allocation (alloc_run.sh)
because the shared sbatch QoS was backlogged -- per the /goal's short-job guidance.

## 2026-06-09 — Four-extension campaign RESULTS (compute landed)

The four-extension jobs launched the prior session all landed. Results below; tasks 14, 15, 16
DONE, task 13 W-resolved covariance running (`ew_cov` 54221942 afterok the 5D merge 54221741).

### Task 14 RESULT (DONE) — rigorous 4D unified throw + ADOPTED as the published 4D systematic.
The 160-throw 4D unified-throw covariance landed on the real (pt,pz,eavail,q3) analysis binning
(`uq_4d/unified_throw_cov_4d.root`; combine log `uq_4d/uthrow4d_comb_*.out`). Jitter floor is
negligible (sqrt 2.12e-39). **Jitter-corrected unified/block sqrt-trace = 2.01** (raw 2.01), i.e.
the block-sum UNDERESTIMATES the vertical systematic by ~2x in trace -- STRONGER than the 3D probe
(1.40). Per-bin sigma median ratio is 1.004, so the inflation is CONCENTRATED, not broad: the
variance-excess top 1% of bins carry 78% / top 5% carry 100% of the trace excess, and they are all
the **high-pT (pt bins 4-5), lowest-E_avail (0.0-0.1 GeV) corner** -- exactly where the migration
matrix is most off-diagonal and bands couple nonlinearly. p90 sigma ratio 1.60, p99 3.02, max 15.5.
Physically credible (not numerical pathology).

ADOPTION (`adopt_unified_4d.py` -> `uq_4d/.../uq_universe_4d_covariance_combined_uthrow.root`):
directly swapping the rank-160 C_unified into the 4830-bin combined breaks PSD (2285 neg eigenvalues,
most-neg = -1.25% of max), because 160 throws << 4830 bins is a noisy full-matrix estimate. So we
adopt the throw's per-bin MAGNITUDE (which converges fast and carries the cross-term) by transferring
its fractional inflation g_i = max(sigma_uni,sigma_blockbank)/sigma_blockbank >= 1 onto the SWEEP's
own vertical block: C_new = (C_comb - C_vert_sweep) + G C_vert_sweep G -- PSD by construction (verified
min-eig = -2.3e-16 of max = float roundoff). This is the same engine-independent fractional-transfer
logic as the task-15 PET lateral. Published 4D combined cov sqrt-trace 2.10e-38 -> 3.85e-38 (x1.84),
median frac/bin 13.5% -> 14.9%. The conservative max() never under-covers vs the block baseline.

### Task 16 RESULT (DONE) — GiBUU as the 4th band generator.
All 80 GiBUU FinalEvents.dat regenerated (the cleanup had deleted them; col 15 IS Enu, muon ID 902 ->
W computable, no format change). `gibuu_to_xsec_eavailW.py` binned 913,859 in-PS events -> (E_avail,W)
2D xsec, total sigma 2.22e-38 cm^2/nucleon (the MOST deficient generator, matches the validated smoke
test). `gibuu_cv_xsec_eavailW.root` has hXSec_eavailW (TH2D), hXSec_eavail, hXSec_W.

Re-ran `eavail_generator_significance.py` with all 4 generators AND the now-published unified-throw
4D cov (`..._uthrow.root`, hCov_combined4d_total_uthrow): the larger rigorous cov reduces the headline
(GENIE-CV 26.3->22.4 sigma) -- more conservative & honest. dsigma/dEavail: all four miss the data at
>21 sigma overall, >15 sigma in the DIS tail (E_avail>=0.8). GENIE-CV 532/7=22.4s, GENIE+MEC
652/7=24.9s, NuWro 513/7=21.9s, **GiBUU 481/7=21.2s**. Notably GiBUU spreads its deficit across the
WHOLE DIS tail (per-bin pulls 12.3/7.9/12.8 at E_avail 0.8-1.5/1.5-3.0/catch; data/gen 1.59 at
0.8-1.5, 1.36 at 1.5-3.0, 1.91 catch) rather than piling in the catch bin like the GENIE variants --
a qualitatively different, generator-robust confirmation of the high-E_avail excess.

### Task 13 (W-resolved) — DONE. (E_avail,W) frozen-reweighter covariance.
The 12 5D `_universes_full` omnifiles (133 GB) were merged (SetMaxTreeSize, 4.6 min on the
interactive alloc); `eavailW_covariance.py` does ONE CV 5D unfold for the frozen push weights and a
frozen-reweighter block-sum over 13 knob + 100 flux universes (re-binning, no re-inference -- same
methodology as pet_systematics), + diagonal stat + transferred 4D laterals, projects to the
(E_avail,W) marginal, and computes chi^2 / N-sigma of unfolded data vs all 4 generators'
hXSec_eavailW, including a high-W DIS corner sub-block (E_avail>=0.4 & W>=1.8 GeV).

**BUG CAUGHT BY THE SELF-VALIDATION GATE (then fixed):** the first full-stats run failed validation
at max|ratio-1|=1.44 -- the CV (E_avail,W) total came out 5.99e-38 vs the frozen 5D product's
3.07e-38 (~1.95x over-normalization). Diagnosis: `marginal_ew` was proven correct (it reproduces the
frozen product's own projection to ratio 1.000/bin), isolating the fault to `xsec_ew()` completeness:
the numerator was built from RECO-PASS truth events only, but the validated N-D driver
(unfold_nd_omnifold_unbinned.py:642) uses ALL truth-pass events because OmniFold step2 already does
the efficiency correction in truth space (so completeness ~1, signal/truth_denom phase-space match).
The reco restriction double-counted the efficiency -> xsec inflated by ~1/c. Fixed `of_in` to bin the
full truth-pass set. The re-run validates at max|ratio-1|=0.001 (CV total 3.070e-38). Without the
gate this would have put the data ~2x above every generator and produced fake >40-sigma significances.

**RESULT** (`products/5d/eavailW_covariance.root`: C_syst, C_stat, C_lateral, C_total, hData_ew):
C_total sqrt-tr 8.65e-39, **median 14.8%/bin** (MaRES/MvRES/MaCCQE-dominated; flux sqrt-tr 3.44e-39).
Generator chi^2/ndf over the full 42-bin (E_avail,W) plane: GENIE-CV 412.7/42 (16.7s), GENIE+MEC
390.5/42 (16.1s), NuWro 1148.4/42 (31.2s), GiBUU 1930.2/42 (>37s). **High-W DIS corner** (12 bins,
E_avail>=0.4 & W>=1.8 GeV): GENIE-CV 116.9/12 (9.0s), GENIE+MEC 121.1/12 (9.2s), NuWro 149.6/12
(10.5s), **GiBUU 381.1/12 (18.2s = most deficient)**. The excess is a genuine high-W DIS-region
feature (W>~1.8 GeV), not a low-W resonance artefact -- open question 6 is fully W-resolved. All four
extensions (13/14/15/16) now complete.
