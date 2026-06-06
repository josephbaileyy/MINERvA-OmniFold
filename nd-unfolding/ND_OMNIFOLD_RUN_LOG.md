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
