# 3D OmniFold (Eavail) — Status

**Last updated**: 2026-07-16. Workstream C framework **complete end-to-end**
(C1 event loop + C2 driver + C3 validation). **2026-06-03 literature audit**
(see `../LITERATURE_NOTES.md`): no critical defects; added the 3D bottom-line
test (PASS, ratio 0.102) and an **ensemble-mean** 3D CV
(`xsec_3d_MEFHC_5iter_lgbm_ensemble.root`, lgbm seed band 0.45→0.14 %/bin, shift
~0); staged the **Ascencio low-q3** corroboration
(`genie/compare_ascencio_eavail.py`, arXiv:2110.13372) and folded the
open-question resolutions into `docs/technote/sec_openquestions.tex` (3D GoF =
rank-247 truncated-spectral χ²; the high-E_avail DIS-tail excess is the one
remaining physics item). Full-stats 3D unfold
`d³σ/(dp_T dp_‖ dE_avail)` produced and validated: the Eavail-marginal recovers
the published 2D **normalization**, and an injected-shape **closure passes** — so
the elevated marginal shape distance is consistent with data↔MC structure the
new axis resolves and is not explained by nonclosure of that tested
deformation. **Generator comparison done** with **four**
generators (GENIE CV + MINERvA Tune v1 + NuWro 21.09 + GiBUU 2019), all
under-predict and split along Eavail — see `genie/` and technote §6. **Full
systematic + statistical UQ DONE** (2026-06-02): the 187-universe sweep was
re-unfolded into the combined covariance C_syst+C_stat+C_ML at
`uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root` (Flux-dominated, same
band ordering as 2D); the generator comparison now carries that full-cov
systematic band.

**2026-07-16 covariance-gate override:** the 3D central value, dimensional
anchor, and closure controls remain valid. The historical rank-247 block-sum
covariance and every covariance-dependent generator $\chi^2$/significance are
now **CANDIDATE/QUARANTINED**, not publication numbers. Under the corrected
dependency contract, the quotable 3D covariance is projected from the final
adopted 5D trunk after the selection-complete lateral replacement. Statements
below that call the old 3D UQ “DONE” are retained as chronology and are
superseded by this gate.

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
feature; no practical D'Agostini IBU analogue). **Scope (now complete)**:
framework + first closure + the Eavail-marginal-recovers-2D anchor, the
4-generator comparison, and the full 3D systematic UQ (combined covariance).
Validation anchor (there is no published 3D
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
  space. Totals-in-PS: GiBUU 2.22 < NuWro 2.34 < GENIE CV 2.52 < Tune v1 2.71 <
  data 3.08 (×1e-38); all under-predict, split along Eavail, **data excess at
  low Eavail** the 2D measurement can't resolve (`genie/generators_vs_unfolded.png`;
  technote §6.5). **GiBUU 2019 added as the 4th generator** via a native
  containerless Perlmutter build (integrated −21.9 %, most deficient; see
  `setup_gibuu.sh`, memory `gibuu-native-perlmutter`); NEUT still not pursued
  (not on CVMFS). GENIE env solved natively via UPS `-H` + a compat-lib shim
  (no container); see `genie/README.md`.
- **FSI dial variation**: DONE for `FrInel_pi` (`genie/run_fsi_reweight.sh`,
  `run_parallel_fsi.sh`, `fsi_variation_xsec3d.py`). GENIE `grwght1p` reweights
  the same 2M CV events at ±1σ (dial=0 reproduces CV exactly). **FrInel_pi is
  sub-percent here**: total σ-in-PS ±0.03 %, dσ/dE_avail ≤ 0.74 % — far below
  the ~10–18 % low-E_avail data excess, so it can't explain it (justifies MAT's
  exclusion; uq open question #2). `FrAbs_pi` is the natural next dial.
- **Statistical UQ**: DONE. `--bootstrap-seed` on the 3D driver (Poisson on
  data+MC, mirrors 2D); the per-replica bootstrap band feeds the C_stat block of
  the combined covariance below.
- **Systematic UQ**: DONE (2026-06-02). 187-universe sweep + seedscan, re-unfolded
  and rolled up into the combined covariance C_syst+C_stat+C_ML at
  `uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root` (Flux-dominated, same
  band ordering as 2D, rank 247/1431). Full-cov χ² computed for all four
  generators (incl. GiBUU). Plan/record: `3D_SYSTEMATIC_UQ_PLAN.md`, memory
  `3d-systematic-campaign-gaps`.

## Outputs (gitignored ROOT/PNG; numbers captured here + RUN_LOG)

- `xsec_3d_MEFHC_5iter_lgbm.root` — the production 3D cross section (`hXSec3D`,
  `hUnfold3D`, `hOFCompleteness3D`, Eavail-marginal `hXSec2D`, 1D `hXSec_pt/pz/eavail`).
- `closure_3d_MEFHC_eavail_bump.root` — the closure run (+ `*_closureRef` refs).
- `anchor_marginal_vs_paper.txt`, `eavail_marginal_vs_paper_pull_full.png`.

## Next

- Eavail **binning study** (the remaining open item): the catch-all [3,100] GeV
  top bin is required for the marginal anchor; a finer low-recoil split is now
  motivatable since the systematic UQ exists.
- **Pre-publication methodology items** (user-flagged 2026-06-03; full write-up in
  `../LITERATURE_NOTES.md` §C):
  1. **Covariance** — cross-check the block-sum `C_syst+C_stat+C_ML` against a
     single *unified-throw* covariance (perturb syst+stat+ML jointly per throw,
     re-unfold) to validate the linear-response assumption.
  2. **Seed scan** — extend the seedscan to also vary the **train/test split**
     (not just the GBDT `random_state`), turning `C_ML` from a model-init lower
     bound into the full ML stochasticity and justifying an ensemble-mean CV.
  3. **Unbinned GoF** — add a binning-independent goodness-of-fit (classifier
     two-sample / sliced-Wasserstein / MMD with a permutation null) as a
     cross-check on the binned truncated-spectral χ².
  4. **More dimensions** — only with a specific physics question per axis; best
     candidates are **q3** (makes the Ascencio low-q3 comparison bin-identical)
     and **hadronic angle / proton multiplicity** (separates 2p2h from the
     high-E_avail DIS tail). Keep the unbinned unfold high-dim; publish binned
     projections only along motivated axes.
- **Higher-dimensional + NN design doc** (2026-06-03): `../docs/HIGHER_DIM_OMNIFOLD_DESIGN.md`
  plans Phase 1 (q3 as a 4th scalar axis, GBDT-native: needs a `CVUniverse.h` accessor +
  event-loop re-run, an N-D `xsec_nd.py`, q3-marginal/closure anchors) and Phase 2 (a
  vendored `ViniciusMikuni/omnifold` NN/PET point-cloud track), with the explicit
  GBDT→NN crossover criterion. Design/hand-off only — no code yet.
- DONE: framework, full-stats unfold, 4-generator comparison (incl. GiBUU),
  statistical + systematic UQ (combined covariance), the 2p2h / FSI-dial
  decomposition of the low-Eavail excess, and the 3D writeup in the technote
  (`docs/technote/` §6, incl. §sec:3d-syst).
