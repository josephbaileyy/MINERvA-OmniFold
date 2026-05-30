# 3D OmniFold — available-energy extension

Workstream C of the post-tension plan: extend the 2D (pT, p‖) unbinned OmniFold
measurement to **d³σ/(dpT dp‖ dEavail)**, adding available energy as the 3rd
axis. This is the physics showcase for unbinned OmniFold's high-dimensional
advantage (adding an observable = adding a feature; no practical D'Agostini IBU
analogue).

**Staged scope**: build the 3D framework + first closure, and validate by
recovering the published 2D result as the **Eavail-marginal** (the anchor —
there is no published 3D reference). The full 3D *systematic*-UQ campaign is
deferred to a follow-up.

This directory is a sibling of `../2d-unfolding/` and **reuses** its driver,
data (`minerva_paper_anc/`, flux, baseline), and compare/UQ utilities (imported
via a small `sys.path` add). Only 3D-specific code lives here.

## Docs (this workstream)
- **`3D_OMNIFOLD_STATUS.md`** — dashboard: current numbers, stage status, next.
- **`3D_OMNIFOLD_RUN_LOG.md`** — append-only chronology (C1→C2→C3).
- Shared invariants (POT / nucleons / phase-space gate / flux) are in the 2D
  triad: `../2d-unfolding/2D_OMNIFOLD_REFERENCE.md` § "3D OmniFold extension".
  The 3D driver `import`s the 2D helpers, so those contracts apply unchanged.

## Axis definitions (settled — arXiv:2312.16631 Eq. 4)
| Axis | Accessor | Notes |
|---|---|---|
| truth Eavail | `GetEAvailableTrue()` — MAT `calculators/CCQE3DFitFunctions.h:34` | Σ proton KE + Σ π± KE + Σ π⁰/γ total E; excludes n, μ. Matches paper Eq. 4. MeV→GeV. |
| reco Eavail | `NewEavail()` — MAT `LowRecoilPionFunctions.h:41` | tracker+ECAL × 1.17; matched to truth for closure (chosen over spline `GetEavail()`). |

Reference PDF: `../2d-unfolding/reference/Henry_2312.16631_MINERvA_Eavail_lowQ2.pdf`
(reference/ is gitignored). **Eavail binning**:
`[0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100]` GeV — the 100-GeV **catch bin is
required** so the Eavail-marginal captures the full CC-inclusive recoil tail and
equals the 2D result.

## Code
- **`xsec_3d.py`** — 3D cross-section extraction + Eavail-marginal + 1D
  projections; numpy self-tests (`python xsec_3d.py`). Marginal recovers the 2D
  xsec to machine precision (3.8e-16).
- **`unfold_3d_omnifold_unbinned.py`** — the 3D driver: eavail-aware TTree
  readers, 3-column feature stack, `xsec_3d` extraction/projection. Reuses the
  2D driver's flux/POT/nucleon/gate helpers via `import`; CV-only. Supports
  `--closure` / `--closure-reweight-eavail`.
- **`sbatch_evloop_array_3d.sh`** — 12-playlist event loop (C1 re-run).
- **`sbatch_unfold_3d.sh`** — full-stats unfold + auto anchor check (C2/C3).

## How to run
```bash
source ../setup_salloc_env.sh

# Full-stats production unfold (5 iter lgbm) + Eavail-marginal anchor check:
python unfold_3d_omnifold_unbinned.py \
  --omnifile runEventLoopOmniFold_MEFHC_3D.root \
  --mcfile   ../2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root \
  --iters 5 --use-weights --estimator lgbm --seed 1 \
  --out xsec_3d_MEFHC_5iter_lgbm.root
python ../2d-unfolding/compare_to_paper_fullcov.py \
  --ours xsec_3d_MEFHC_5iter_lgbm.root --out-prefix eavail_marginal_vs_paper

# Reweight closure (inject a truth-Eavail bump, check recovery):
python unfold_3d_omnifold_unbinned.py ... \
  --closure --closure-reweight-eavail \
  --closure-eavail-amplitude 0.3 --closure-eavail-center 0.3 --closure-eavail-sigma 0.15 \
  --out closure_3d_MEFHC_eavail_bump.root
```
Note: always pass `--out-prefix` to `compare_to_paper_fullcov.py` from here, or
its default clobbers the tracked 2D pull plot.

The C1/C2 build-and-rerun history and the C3 validation results are in
`3D_OMNIFOLD_RUN_LOG.md`; headline numbers in `3D_OMNIFOLD_STATUS.md`.
