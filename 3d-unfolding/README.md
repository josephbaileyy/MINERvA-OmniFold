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

## Axis definitions (settled — arXiv:2312.16631 Eq. 4)
| Axis | Accessor | Notes |
|---|---|---|
| truth Eavail | `GetEAvailableTrue()` — MAT `calculators/CCQE3DFitFunctions.h:34` | Σ proton KE + Σ π± KE + Σ π⁰/γ total E; excludes n, μ. Matches paper Eq. 4. MeV→GeV. |
| reco Eavail | `NewEavail()` — MAT `LowRecoilPionFunctions.h:41` | tracker+ECAL × 1.17; matched to truth for closure (chosen over spline `GetEavail()`). |

PDF: `../2d-unfolding/reference/Henry_2312.16631_MINERvA_Eavail_lowQ2.pdf`
(reference/ is gitignored). Proposed Eavail binning (finalize from statistics):
`[0, 0.1, 0.2, 0.4, 0.8, 2.0]` GeV.

## Status
- [x] **`xsec_3d.py`** — 3D cross-section extraction + Eavail-marginal +
  1D projections, with numpy self-tests (`python xsec_3d.py`). The marginal
  recovers the 2D cross section to machine precision (3.8e-16). *No real data
  needed yet.*
- [x] **C1 (C++ + re-run)** — Eavail branches added to `runEventLoopOmniFold.cpp`
  (truth `MC_eavail` via `GetEAvailableTrue()`, reco `sim_eavail` /
  `sim_background_eavail` / `measured_eavail` via `NewEavail()`); accessors added
  standalone to `CVUniverse.h`. Build + single-file smoke test passed (eavail
  values physical: truth med 0.95 GeV, reco med 0.66 GeV, no NaN, misses −9999).
  12-playlist re-run launched: `sbatch_evloop_array_3d.sh` (SLURM 53601666) →
  `runEventLoopOmniFold_3D_{1A..1P}.root` (non-destructive). **All 12 COMPLETED**
  (2026-05-30, no log errors); `hadd`-ed → `runEventLoopOmniFold_MEFHC_3D.root`
  (2.8 GB, full MEFHC stats). Eavail sanity OK on full stats: truth mean
  1.93 GeV (0→92 GeV DIS tail), matched reco 1.15 GeV, data 1.54 GeV;
  `sim_eavail` = −9999 for the 12.35M/32.8M truth-signal events failing reco.
- [x] **C2 (driver wiring)** — `unfold_3d_omnifold_unbinned.py`: eavail-aware 3D
  TTree readers + 3-column feature stack + `xsec_3d` extraction/projection.
  Reuses the 2D driver's flux/POT/nucleon/gate helpers via import (CV-only; the
  universe / alt-model / bootstrap machinery is the deferred 3D-UQ campaign).
  Smoke test (`smoke/`, 2 iter) passed: `c=1.0000`, and the 3D integral equals
  the Eavail-marginal 2D integral (2.905e-38) to displayed precision.
- [~] **C3 (validation)** — full-stats unfold done (`xsec_3d_MEFHC_5iter_lgbm.root`,
  5 iter lgbm seed 1, ran ~14 min on the interactive node; c=1.0000). Results
  (`anchor_marginal_vs_paper.txt`, 2026-05-30):
  - **Eavail spectrum physical**: dσ/dE_avail falls monotonically 2.19e-38
    (low-recoil [0,0.1] peak) → 6.8e-41 (catch bin), the expected CC-inclusive
    shape.
  - **Normalization anchor PASS**: marginal total σ = 3.724e-37 vs paper
    3.689e-37 (+0.95%); 3D integral ≡ Eavail-marginal integral (3.079e-38);
    marginal/2D per-bin ratio median 1.0016, mean 1.0079.
  - **Shape anchor ELEVATED**: marginal vs paper full-cov χ²/ndf = **4.98**
    (stat-only 12.48), above the frozen 2D values (default-2D 3.66, lgbm-CV
    2.65). Driven by ~4.4% per-bin scatter the 3rd axis injects into the
    (pT,p||) marginal — a genuine effect of reweighting with Eavail info, NOT a
    normalization/pipeline bug (total σ matches to <1%). Next: the 3D **closure**
    (truth-reweight / hidden-var) decides whether that scatter is statistical
    (closure closes) or a real Eavail-migration bias.

## C1 spec — C++ event-loop changes (ready to apply when we launch the re-run)
In `MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp`, following the
existing `MC`/`MC_pz` (truth tree, ~lines 274–275, 498–500) and `sim`/`sim_pz`
(reco tree, ~lines 494–497) branch pattern:
1. Make the two accessors visible to `CVUniverse` (it already includes
   `TruthFunctions.h`); add `#include` for the `GetEAvailableTrue` /
   `NewEavail` calculators (or add thin wrappers in `event/CVUniverse.h`).
2. Add tree branches: truth `MC_eavail = GetEAvailableTrue()/1000` (GeV);
   reco `sim_eavail = NewEavail()/1000` (GeV). Fill alongside the existing
   pt/pz fills.
3. Rebuild (cmake — heed the build-source-path trap, see memory
   `project_build_source_path`); re-run the 12-playlist array (~3–4 h) →
   a 3D omnifile next to `runEventLoopOmniFold_MEFHC.root`.

## C2 spec — driver generalization
Reuse `../2d-unfolding/unfold_2d_omnifold_unbinned.py` data loading + the
`ohf.omnifold(...)` call (already dimension-agnostic); the feature
`np.column_stack` gains the eavail column. Replace `extract_cross_section_2d` /
`project_xsec_1d` with `xsec_3d.extract_cross_section_3d` /
`project_eavail_marginal` / `project_axis`. Output a TH3D (+ the 2D marginal
for validation).
