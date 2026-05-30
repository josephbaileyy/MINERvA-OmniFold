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
- [ ] **C1 (C++ + re-run, deferred by decision)** — see spec below.
- [ ] **C2 (driver wiring)** — generalize the 2D driver's data loaders + feature
  stacking + binning to read/use the Eavail branches, then call `xsec_3d` for
  extraction/projection.
- [ ] **C3 (validation)** — 3D closure (truth-reweight, hidden-var) vs the 2D
  thresholds; **Eavail-marginal must reproduce the frozen 2D χ² vs paper**.

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
