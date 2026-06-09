# Higher-dimensional OmniFold + the GBDT→NN crossover — design doc

**Status:** design (2026-06-03) — **now implemented**, see below. This document plans
the next dimensional step beyond the completed 3D `d³σ/(dp_T dp_‖ dE_avail)` measurement
and states the criterion for moving from the LightGBM (GBDT) reweighter to a neural-net
OmniFold.

> **Implementation (2026-06-03/04) — scalar phase done; PET follow-up gated.** Tracking in
> `nd-unfolding/ND_OMNIFOLD_STATUS.md` + `ND_OMNIFOLD_RUN_LOG.md`.
> - **Phase 1 (q3, GBDT) — validated.** `nd-unfolding/xsec_nd.py` (N-D extraction,
>   unit-tested), `nd-unfolding/unfold_nd_omnifold_unbinned.py` (the **axis-list
>   driver**), `CVUniverse::RecoQ3()` + `Getq3True` in `runEventLoopOmniFold.cpp`.
>   The 4D unfold `d⁴σ/(dp_T dp_‖ dE_avail dq3)` passes every anchor: Jacobian
>   identity exact, 4D recovers frozen 3D to <2% median, 2D-marginal anchors the
>   paper (4D/3D=0.9960), injected-q3 closure passes.
> - **Phase 2 (scalar NN) — validated.** `omnifold_nn/` vendored (`ViniciusMikuni/omnifold`),
>   `nd-unfolding/omnifold_nn_core.py` (ROOT-free keras-MLP) + `estimator="nn"`. The
>   NN reproduces the GBDT 3D cross section within the ML band (total ratio 1.0078,
>   projections ≤1.4% median). The PET point-cloud path is wired, but the first
>   real-cloud run used the wrong reconstructed-cluster branch and is not a validated
>   physics/method result until rerun with the real non-muon recoil-cluster collection.

**Scope decided with the user:** phased — Phase 1 adds **q3** as a 4th *scalar* axis
(GBDT-native); Phase 2 builds a **point-cloud / NN** track as the longer-term
high-dimensional showcase. The NN is brought in by **vendoring an existing codebase as a
sibling folder** (the way `unbinned_unfolding/` ports rymilton's repo), not by
hand-writing an estimator. GPU is available.

Related: `../LITERATURE_NOTES.md` §C (the recorded "more dimensions" recommendation +
the three pre-publication methodology items), `3d-unfolding/3D_OMNIFOLD_STATUS.md`.

---

## 0. What is already generic (and what is not)

| Layer | File | Dimension-agnostic? |
|---|---|---|
| OmniFold core (pull/push, w=p/(1−p)) | `unbinned_unfolding/python/omnifold.py` | **Yes** — features are `(nevents, nfeatures)` arrays; adding an axis = one more `np.column_stack` column. The `omnifold()` call is unchanged from 2D→3D→ND. |
| Estimators | same | `exact / hist / xgb / lgbm` branches exist. **No NN branch.** |
| Histogramming | `3d-unfolding/unfold_3d_omnifold_unbinned.py::hist3d` | Uses `np.histogramdd` (already N-D) but the wrapper is written for 3 columns. |
| Cross-section extraction / projection | `3d-unfolding/xsec_3d.py` | **No** — `extract_cross_section_3d`, `project_axis`, `project_eavail_marginal` are hardcoded to 3 axes (pt/pz/eavail). Needs an N-D generalization. |
| Covariance (block-sum C_syst+C_stat+C_ML) | `2d-unfolding/uq/analyze_universes.py`, `3d-unfolding/uq_3d/analyze_universes_3d.py` | **Yes (bin-count-agnostic)** — but bin count and covariance null-space grow fast (3D is already 1431 bins, rank 247). |
| New observable input | `MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h` | **No** — a genuinely new reco/truth variable needs a C++ accessor (mirror `NewEavail()` L184 / `GetEAvailableTrue()` L194) **and an event-loop re-run** to dump the branch. This is how E_avail was added in workstream C1. |

**Takeaway:** the *unfolding* is nearly free to extend; the cost is (a) one C++ accessor +
a full 12-playlist event-loop re-run per new observable, and (b) generalizing the
extraction/projection helpers. The covariance pipeline is reused as-is.

---

## 1. The GBDT→NN decision criterion (the headline answer)

**Stay on LightGBM** for fixed-length tabular features at small dimensionality
(d ≲ ~10 continuous features). This covers 2D, 3D, the q3 4D case, and even 5–6 scalar
axes. In this regime GBDTs are scale-free (no feature standardization), CPU-cheap, need no
architecture/tuning search, and match or beat MLPs — the field's NN preference is about
point clouds, not tabular performance.

**Switch to a neural net when *any* of:**
1. **Variable-length / set-valued inputs** — a full final-state particle list / point
   cloud (per-hadron 4-vectors with variable multiplicity). GBDTs structurally cannot
   ingest this; it needs a permutation-invariant **DeepSets/PET** architecture. *This is
   the decisive trigger for this analysis.*
2. **High continuous dimensionality**, d ≳ 10–20 fixed features, where axis-aligned tree
   splits get sparse and an MLP's distributed representation wins.
3. **GPU throughput** — when you want to amortize many per-universe + per-bootstrap
   re-unfolds; NN minibatching on GPU scales where single-threaded exact-GBT does not.

**Rule for this analysis:** q3 (4D, scalar) **stays LightGBM**. The NN becomes *necessary*
only at the point-cloud phase. Crucially, validate the vendored NN as a **same-inputs
cross-check at 3D/4D first** — it must reproduce the frozen GBDT result within the measured
ML band — *before* trusting it on point clouds, where there is no GBDT baseline to anchor
against.

---

## 2. Phase 1 — q3 as a 4th scalar axis (GBDT, end-to-end)

q3 (three-momentum transfer) is the best-motivated 4th axis: it makes the **Ascencio
low-q3 CC-inclusive** comparison (arXiv:2110.13372; `d²σ/dq3 dE_avail`) *bin-identical*
instead of the current mapped cross-check, directly sharpening the low-recoil / 2p2h
narrative.

1. **q3 definition.** Match Ascencio 2110.13372's reco q3 estimator exactly so the
   comparison is bin-identical (document the formula; truth q3 from the generator vertex
   momenta). This choice is the one physics decision to lock before coding.
2. **Event loop (the expensive step).** Add truth + reco q3 accessors to `CVUniverse.h`,
   mirroring `NewEavail()` (L184) and `GetEAvailableTrue()` (L194). Dump
   `sim_q3 / MC_q3 / measured_q3 / sim_background_q3` in `runEventLoopOmniFold`. Re-run the
   12-playlist loop (same shape/cost as the C1 E_avail re-run; use `alloc_run.sh` for the
   >3h allocation).
3. **Generalize extraction.** Refactor `3d-unfolding/xsec_3d.py` → `xsec_nd.py`:
   `extract_cross_section_nd(counts, completeness, flux_pt, ...)`, `project_axis(i)`,
   `project_marginal(drop_axes)` — built on `np.histogramdd` with per-axis `np.diff`
   broadcasting. The 3D entry points stay as thin wrappers so the frozen 3D path is
   untouched.
4. **Driver.** Either parametrize the existing driver over an *axis list* (preferred — one
   code path for 2D/3D/4D), or add a 4D driver that imports the generalized helpers, the
   way `unfold_3d_omnifold_unbinned.py` does `import unfold_2d_omnifold_unbinned as u2d`.
   The OmniFold call just gets a 4-column `column_stack`.
5. **Covariance.** `uq_3d/analyze_universes_3d.py` is bin-count-agnostic — 4D only grows
   the bin count (q3 bins × current 1431). Keep q3 binning **coarse** (the 3D covariance is
   already mostly null space) and reuse the truncated-spectral χ².
6. **Validation anchors (mirror the E_avail pattern).**
   - **q3-marginal must reproduce the frozen 3D result** (Jacobian identity, exactly like
     the E_avail-marginal → 2D anchor).
   - **Injected-q3-shape closure** (a Gaussian truth-q3 bump recovered), reusing the
     `--closure-reweight-eavail` machinery generalized to the new axis.
   - **Ascencio low-q3 bin-identical χ²** as the external check.

---

## 3. Phase 2 — NN / point-cloud track (vendored codebase)

**Recommended vendor: `ViniciusMikuni/omnifold` → a sibling folder `omnifold_nn/`**,
imported via `sys.path` exactly like `unbinned_unfolding/python` is today. Rationale:

- It is the **upstream** implementation and the **only one of the two linked repos with
  PET** (Point-Edge Transformer, arXiv:2404.16091) for point clouds — precisely the
  Phase-2 showcase — plus an MLP for tabular features, keras/TF GPU support, a bootstrap
  flag, and ensembling.
- **Borrow neutrino-domain glue from `rhuang1/OmnifoldT2K`** (which adapts Mikuni's
  algorithm — via AlephOmniFold — to a neutrino experiment): its `NTRIAL`
  ensemble-averaged central value and its `FormatData.py` standardization / outlier
  removal are the patterns to copy, not the engine.

Design points:
- **Vendoring pattern.** Same as `unbinned_unfolding/`: drop the repo in as `omnifold_nn/`,
  add a `sys.path.insert` import in the driver, pin the commit. Keep it self-contained so
  the GBDT path is unaffected.
- **Data interface.** Map our event-loop arrays → the vendored `DataLoader` (reco
  features, truth features, pass-reco/pass-truth flags, per-event weights). Scalars → MLP;
  point cloud → PET with per-particle 4-vectors + a multiplicity mask.
- **Standardization.** Required for NN (the GBDT path was scale-free) — fold in via the
  `FormatData` pattern; document the asymmetry so nobody "standardizes" the GBDT inputs.
- **Reuse the UQ harness unchanged.** Drive the NN per-universe and per-bootstrap exactly
  as the GBDT path (one variance axis per unfold), so `analyze_universes_*.py` and the
  block-sum covariance are untouched.
- **GPU/env.** keras/TF on the available GPU; record the module/conda env and the `device`
  argument used.
- **Ensembling.** Adopt the NTRIAL ensemble-mean central value — the NN path makes this
  natural and directly satisfies a recorded pre-publication item (below).

---

## 4. Interaction with the recorded pre-publication items

From `../LITERATURE_NOTES.md` §C (memory `prepub-methodology-items`):
- **(#2) train/test-split seedscan + ensemble-mean CV** — the NN/NTRIAL path implements
  this natively; the ensemble mean becomes the headline CV with a defensible spread.
- **(#3) unbinned goodness-of-fit** — the NN track is the natural venue (a classifier
  two-sample test reuses the same discriminator infrastructure).
- **(#1) unified-throw vs block-sum covariance** — independent of dimensionality/engine.
  **DONE (2026-06-09):** measured on the real 4D binning — block-sum *underestimates* the
  vertical systematic ~2× (jitter-corrected unified/block sqrt-trace 2.01), concentrated in
  the high-pT/lowest-Eavail corner; adopted as the published 4D systematic via PSD-safe
  fractional-inflation transfer (`adopt_unified_4d.py`). See `FUTURE_DIRECTIONS.md`.

---

## 5. Cost / risk notes

- Each new *observable* (not merely a dimension) costs a C++ accessor + a full event-loop
  re-run — the real expense. The unfolding step itself is nearly free.
- Covariance null-space grows fast with bins. Only **publish** binned projections along
  axes with a physics question attached — q3 first, then a hadronic-system angle / proton
  multiplicity for the high-E_avail DIS-tail excess (open question 6). The **W (hadronic
  invariant mass) axis is DONE** (2026-06-07): added as the 5th OmniFold axis, its W-marginal
  recovers the frozen 4D to 0.11%, and it localizes open question 6 to the high-W DIS corner;
  the (E_avail,W) generator significance is the current closeout (`eavailW_covariance.py`).
  Keep the *unbinned* unfold high-dimensional but project for publication.
- Don't add a blind axis: it inflates bins and covariance null space without buying
  physics.

---

_Critical files referenced (none edited by this doc): `unbinned_unfolding/python/omnifold.py`,
`3d-unfolding/xsec_3d.py`, `3d-unfolding/unfold_3d_omnifold_unbinned.py`,
`MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h` (L184/L194),
`2d-unfolding/uq/analyze_universes.py`, `3d-unfolding/uq_3d/analyze_universes_3d.py`.
External: github.com/ViniciusMikuni/omnifold, github.com/rhuang1/OmnifoldT2K,
arXiv:2404.16091 (PET), arXiv:2110.13372 (Ascencio low-q3)._
