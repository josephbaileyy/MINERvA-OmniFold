# 3D OmniFold (Eavail) — Status

**Last updated**: 2026-05-31. Workstream C framework **complete end-to-end**
(C1 event loop + C2 driver + C3 validation). Full-stats 3D unfold
`d³σ/(dp_T dp_‖ dE_avail)` produced and validated: the Eavail-marginal recovers
the published 2D **normalization**, and an injected-shape **closure passes** — so
the elevated marginal **shape** χ² is genuine data↔MC structure the new axis
exposes, not a method bias. **Generator comparison done** (GENIE CV + MINERvA
Tune v1 + independent NuWro, all under-predict and split along Eavail — see
`genie/`). **Statistical UQ in progress**: 100-replica Poisson bootstrap (SLURM
array 53653415). Deferred: the full 3D *systematic*-UQ campaign (needs the
universe-dumping event-loop re-run).

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
- **Generator comparison**: DONE (`genie/`, commits `87cd16e`…`0f4c96d`).
  Truth-level GENIE 2.12.10 CV (gevgen) + MINERvA Tune v1 (from event-loop
  `w_truth`) + independent NuWro 21.09, all on the MINERvA flux in the 3D phase
  space. Totals-in-PS: NuWro 2.34 < GENIE CV 2.52 < Tune v1 2.71 < data 3.08
  (×1e-38); all under-predict, split along Eavail, **data excess at low
  Eavail** the 2D measurement can't resolve (`genie/generators_vs_unfolded.png`;
  technote §6.5). NEUT/GiBUU not pursued (not on CVMFS). Env solved natively
  via UPS `-H` + a compat-lib shim (no container); see `genie/README.md`.
- **Statistical UQ**: IN PROGRESS (commit `5f3f6ec`). `--bootstrap-seed` added
  to the 3D driver (Poisson on data+MC, mirrors 2D); 100-replica array
  (`sbatch_bootstrap_3d.sh`, SLURM 53653415) → `build_bootstrap_band_3d.py`
  for the per-bin statistical band + data error bars.

## Outputs (gitignored ROOT/PNG; numbers captured here + RUN_LOG)

- `xsec_3d_MEFHC_5iter_lgbm.root` — the production 3D cross section (`hXSec3D`,
  `hUnfold3D`, `hOFCompleteness3D`, Eavail-marginal `hXSec2D`, 1D `hXSec_pt/pz/eavail`).
- `closure_3d_MEFHC_eavail_bump.root` — the closure run (+ `*_closureRef` refs).
- `anchor_marginal_vs_paper.txt`, `eavail_marginal_vs_paper_pull_full.png`.

## Next

- **Finish the statistical band**: once the bootstrap array lands, run
  `build_bootstrap_band_3d.py` → per-bin stat covariance + data error bars on the
  spectrum/overlays (in progress).
- Full 3D **systematic UQ** (deferred, large): re-run the 12-playlist event loop
  with `MNV101_DUMP_UNIVERSES` on the 3rd axis, then the ~187-universe re-unfold
  + 3D covariance — the 3D omnifile currently has no universe weights.
- Eavail **binning study**: the catch-all [3,100] GeV top bin is required for the
  marginal anchor; a finer low-recoil split may be motivated once UQ exists.
- Other generators (NEUT/GiBUU) — blocked: not on CVMFS (GiBUU would need a
  from-source build).
- DONE: 3D results + generator comparison in the technote (`docs/technote/` §6).
