# N-D OmniFold (q3 4th axis + NN track) — Status

**Last updated**: 2026-06-03. Workstream D = the higher-dimensional extension
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

## Next (follow-ons, not blocking)

- **Ascencio low-q3 bin-identical comparison** (q3 binning chosen to allow matching
  2110.13372 — fetch its public release and overlay, the q3 analogue of
  `../3d-unfolding/genie/compare_ascencio_eavail.py`).
- **q3 systematic campaign**: the event loop dumps **CV** q3 only; per-universe q3
  branches are a follow-on, and note q3 is **NOT** lateral-invariant (depends on muon
  kinematics) so lateral universes must dump shifted q3, not reuse CV (unlike Eavail).
- **PET point-cloud track**: the validated NN engine is ready; build the per-hadron
  DataLoader for the vendored `omnifold_nn/` PET model.
- Systematic campaign for q3: the event loop currently dumps **CV** q3 only; the
  per-universe q3 branches (`sim_q3_<band>_<idx>` …) are a follow-on — and note q3
  is **NOT** lateral-invariant (unlike Eavail), since it depends on muon kinematics,
  so lateral muon/beam universes shift it and must be dumped, not reused from CV.
