# N-D OmniFold (q3 4th axis + NN track) — Status

**Last updated**: 2026-06-06. Workstream D = the higher-dimensional extension
planned in `../docs/HIGHER_DIM_OMNIFOLD_DESIGN.md`. Two tracks, both **implemented
this session**; the q3 measurement is **compute-in-flight** (event loop running).

Companion docs: `ND_OMNIFOLD_RUN_LOG.md` (chronology). Shared invariants
(POT / nucleons / phase-space gate / flux) live in the 2D triad
(`../2d-unfolding/2D_OMNIFOLD_REFERENCE.md`) — the N-D driver `import`s the 2D
helpers, exactly as the 3D driver does.

---

## What is implemented (code complete + unit-tested)

- **`xsec_nd.py`** — N-D cross-section extraction / projection
  (`extract_cross_section_nd`, `project_marginal(drop_axes)`, `project_axis(i)`,
  `total_xsec`). Generalizes `../3d-unfolding/xsec_3d.py` to any axis count via
  `np.histogramdd` + per-axis `np.diff` broadcasting. **Self-tests pass**, incl. a
  test that it reproduces the frozen `xsec_3d.py` to <1e-12 and the 4D
  q3-marginal→3D Jacobian identity to 4e-16. The frozen 3D module is left
  untouched.
- **`unfold_nd_omnifold_unbinned.py`** — the **axis-list driver**. The first two
  axes are always (pt, pz) (fiducial gate + per-pt flux, structural); every further
  axis is an entry in the `EXTRA_AXES` registry (`eavail`, `q3`) giving its
  truth/reco/data/bkg branches + edges. `--axes eavail,q3` does the 4D unfold;
  `--axes eavail` reproduces 3D. Generic multi-axis readers, `np.histogramdd`
  binning, completeness, extraction (xsec_nd), 1D projections, and the
  marginal anchors (drop trailing axes → lower-D; the 2D marginal is written as
  `hXSec2D` for the paper anchor). Closure with an injected bump on any axis
  (`--closure-reweight-axis q3`). Validation: an `--axes eavail` run reproduces the
  frozen 3D result (the only difference from the 3D driver is the generalization).
- **C++ q3 (Workstream D event loop)** — `CVUniverse::RecoQ3()` (calorimetric
  low-recoil reconstruction, MAT `LowRecoilFunctions::GetLowRecoilQ3` lineage:
  q0 = `<tree>_recoil_E`, Q² from muon kinematics, q3 = √(Q²+q0²)) and truth
  `Getq3True()` (canonical MAT, mc_Q2 + true muon). Dumped as
  `sim_q3 / MC_q3 / measured_q3 / sim_background_q3` alongside the eavail branches
  in `runEventLoopOmniFold.cpp`. **Built + smoke-tested**: truth q3 clean
  (0.05–85 GeV, median 1.77); reco q3 median sane with the expected calorimetric
  tails that land in the catch-all top q3 bin (same pattern as reco Eavail).
- **NN / point-cloud track (Phase 2)** — `../omnifold_nn/` is the vendored
  `ViniciusMikuni/omnifold` (PET + MLP, keras/TF, the only linked repo with a point
  cloud architecture). `omnifold_nn_core.py` is a **ROOT-free** NN engine: a keras
  MLP (from the vendored `net.py`, weighted sigmoid-BCE) behind a sklearn
  fit/predict_proba with input standardization, plus an estimator-agnostic copy of
  the validated two-step loop. `omnifold.py` gains an **`estimator="nn"`** branch
  delegating to it (lazy TF import, so the ROOT env still loads).

## Results (2026-06-04) — both phases DONE

**Phase 1 (q3 4D) — VALIDATED.** `xsec_4d_MEFHC_5iter_lgbm.root`,
d⁴σ/(dp_T dp_‖ dE_avail dq3): completeness 1.0000, total σ 3.066e-38; Jacobian
identity exact (2D-marginal == 4D integral); 4D recovers frozen 3D to <2% median
(pt 0.38%, pz 0.64%, Eavail 1.68%); 2D-marginal anchors the paper (4D/3D=0.9960);
injected-q3 closure passes (ratios track the 1.0142 bump); new dσ/dq3 produced.

**Phase 2 (NN) — VALIDATED.** keras-MLP OmniFold reproduces GBDT within the ML band:
total ratio **1.0078**, projections agree to 0.66%/1.20%/1.36% median. Two NN bugs
found + fixed en route (class-balance bias; unshuffled single-class `validation_split`)
— now documented in `omnifold_nn_core.py`. Engine green-lit for the point-cloud phase.

(Full SLURM trail in `ND_OMNIFOLD_RUN_LOG.md`: event loop 53905768, 4D unfold
53925395, NN 53928526; first runs 53906839/53906748 surfaced the THnSparse + NN bugs.)

## Follow-on campaign (2026-06-04) — all six "next steps" actioned

See `ND_OMNIFOLD_RUN_LOG.md` (2026-06-04 entry) for full detail. Summary:

- **#2 Ascencio low-q3 overlay — DONE (code).** `compare_ascencio_q3.py` produces our
  d²σ/(dq3 dEavail) + dσ/dq3 on Ascencio's binning; bin-identical χ² verified with a
  synthetic drop-in. The 2110.13372 data file is Cloudflare/member-gated (not fetchable
  in-session) — drop it in to finish the overlay (format in the script header).
- **#5 Unbinned GoF — DONE (job 53945834).** `unbinned_gof.py` C2ST: prior data/MC
  separable (z=33), unfolded indistinguishable (z=1.4, p=0.17). Sensitive + PASSES.
- **#4 Train/test-split seedscan — DONE (array 53946279).** `omnifold_loop` train/test
  split; ensemble-mean CV matches frozen CV; ML-split band 1.24× the pure-seed ML band
  (the split adds real ML variance). `uq_cov_mlsplit_3d.root`.
- **#6 PET point-cloud rerun — DONE; shape-only cross-check available.**
  The stale `ExtraEnergyClusters_*` point-cloud chain was replaced by a rerun using
  the corrected reco-cluster source (`cluster_energy`, `cluster_pos`, `cluster_z`,
  excluding `cluster_isMuontrack`). The refreshed CPU chain rebuilt
  `runEventLoopOmniFold_PC_MEFHC.root` and `of_inputs_pc.npz`; PET training
  job 54033990 and comparison job 54033991 both completed successfully. The
  regenerated `pet_vs_gbdt.png` gives PET-vs-GBDT area-normalized shape median
  differences of 3.86% (pT), 2.36% (pz), 2.63% (Eavail), and 2.33% (q3).
  Treat this as a method/shape cross-check, not an absolute cross-section result,
  because the PET run uses a 2M-event subsample.
- **#1 Unified-throw cross-check — IN FLIGHT (job 53946996).** `compare_unified_throw.py`
  superposition test (cross term vs block sum) on the 120 GB 3D universes omnifile.
- **#3 q3 systematic campaign — LAUNCHED (chained).** C++ shifted-q3 for lateral
  universes (built + verified: reco q3 shifts 100% under BeamAngleX), nd `--universe` +
  q3 swap (`lateral_invariant` flag), `analyze_universes_nd.py`. Pipeline:
  evloop 53945111 → hadd 53947173 → validate 53947729 → sweep 53947731 → cov 53947732,
  outputs under `uq_4d/`.
