# 3D OmniFold (Eavail) — Status

**Last updated**: 2026-05-30. Workstream C framework **complete end-to-end**
(C1 event loop + C2 driver + C3 validation). Full-stats 3D unfold
`d³σ/(dp_T dp_‖ dE_avail)` produced and validated: the Eavail-marginal recovers
the published 2D **normalization**, and an injected-shape **closure passes** — so
the elevated marginal **shape** χ² is genuine data↔MC structure the new axis
exposes, not a method bias. Deferred (by design): the full 3D systematic-UQ
campaign — the 3D driver is CV-only.

Companion docs: `README.md` (orientation, axis-decision table, how-to-run),
`3D_OMNIFOLD_RUN_LOG.md` (this workstream's chronology). Shared invariants live
in the 2D triad — the 3D driver `import`s the 2D helpers, so
`../2d-unfolding/2D_OMNIFOLD_REFERENCE.md` (§ "3D OmniFold extension") governs
POT / nucleons / phase-space gate / flux convention for both. Eavail axis
definitions: arXiv:2312.16631 Eq. 4 (see memory `eavail-3d-extension`).

---

## Goal

Extend the 2D unbinned OmniFold measurement to **3D** by adding available
energy as a third axis: `d³σ/(dp_T dp_‖ dE_avail)`. The physics showcase for
unbinned OmniFold's high-dimensional advantage (adding an observable = adding a
feature; no practical D'Agostini IBU analogue). **Staged scope**: framework +
first closure + the Eavail-marginal-recovers-2D anchor; the full 3D systematic
UQ is a deferred follow-up. Validation anchor (there is no published 3D
reference): the Eavail-marginal must reproduce the frozen 2D result.

---

## Headline (MEFHC 5-iter lgbm, eavail edges [0,0.1,0.2,0.4,0.8,1.5,3.0,100] GeV)

| Quantity | Value |
|---|---|
| Total σ (3D integral) | **3.079e-38 cm²/nucleon** (paper 2D: 3.039e-38; +1.3 %) |
| 3D integral ≡ Eavail-marginal integral | exact (Jacobian identity) |
| Global OmniFold completeness c | **1.0000** (Phase-17 truth-only misses) |
| Eavail spectrum dσ/dE_avail | monotonically falling 2.19e-38 → 6.8e-41 (physical) |
| **Eavail-marginal normalization** vs paper | total σ +0.95 %; per-bin median ratio 1.0016 |
| **Eavail-marginal shape** χ²/ndf (paper full cov) | **4.98** (stat-only 12.48) |
| ↳ frozen 2D references, same script | 3.66 (default 2D) / 2.65 (lgbm-CV) |
| Marginal/2D per-bin scatter | median 1.0016, mean 1.008, std **0.044** |
| **3D closure** (injected +30 % truth-Eavail bump) | **PASS** — bump recovered |
| ↳ Eavail-marginal residual (unfold/ref) | median 0.9999, **std 0.0006**, max\|dev\| 0.0021 |
| ↳ 3D-bin residual std | 0.032 (MC-stat in sparse corners) |

**Key inference.** The closure marginal scatter (0.06 %) is ~70× tighter than
the 4.4 % data-vs-2D marginal scatter. The method is unbiased on the new axis,
so that 4.4 % scatter — and the elevated marginal χ²=4.98 — is **real data↔MC
structure the Eavail dimension exposes**, not a pipeline artifact (total σ
matches to <1 %).

---

## Status by stage

- **C1 — event loop**: DONE (commit `8ca52cc`). Truth `MC_eavail` =
  `GetEAvailableTrue()`, reco `sim_eavail`/`sim_background_eavail`/
  `measured_eavail` = `NewEavail()` (accessors added standalone to
  `CVUniverse.h`). 12-playlist re-run (SLURM 53601666) → hadd
  `runEventLoopOmniFold_MEFHC_3D.root` (2.8 GB; 32.85M truth/reco, 4.12M data).
- **C2 — driver**: DONE (commit `685ffce`). `unfold_3d_omnifold_unbinned.py`:
  eavail-aware readers, 3-col feature stack, `xsec_3d.py` extraction /
  Eavail-marginal / 1D projections. Reuses the 2D helpers via `import`; CV-only.
- **C3 — validation**: DONE (commits `2cb4cde`, `27564a8`, `c73ce30`).
  Eavail-marginal anchor (normalization PASS, shape elevated) +
  reweight closure (PASS). See the headline table.

## Outputs (gitignored ROOT/PNG; numbers captured here + RUN_LOG)

- `xsec_3d_MEFHC_5iter_lgbm.root` — the production 3D cross section (`hXSec3D`,
  `hUnfold3D`, `hOFCompleteness3D`, Eavail-marginal `hXSec2D`, 1D `hXSec_pt/pz/eavail`).
- `closure_3d_MEFHC_eavail_bump.root` — the closure run (+ `*_closureRef` refs).
- `anchor_marginal_vs_paper.txt`, `eavail_marginal_vs_paper_pull_full.png`.

## Next (deferred follow-up — not in the staged scope)

- Full 3D **systematic UQ**: port the universe / bootstrap / ML-covariance
  campaign to 3D (the 2D driver's machinery was intentionally not carried over).
- Eavail **binning study**: the catch-all [3,100] GeV top bin is required for the
  marginal anchor; a finer low-recoil split may be motivated once UQ exists.
- A 3D results section for the technote (`docs/technote/`).
