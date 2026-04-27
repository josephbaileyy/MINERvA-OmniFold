# 2D OmniFold Study — Status

**Last updated**: 2026-04-27

Companion docs: `2D_OMNIFOLD_REFERENCE.md` (workflow invariants and gotchas),
`2D_OMNIFOLD_RUN_LOG.md` (timestamped chronology), `PLOT_GUIDE.md` (PNG index
and naming convention).

---

## Goal

Reproduce arXiv:2106.16210 (Ruterbories et al., Phys. Rev. D 106, 032001) —
MINERvA ME FHC d²σ/(dp_T dp_||) CC inclusive — with 2D **unbinned** OmniFold
in place of D'Agostini IBU. Validated on playlist 1A, then run on full
12-playlist ME FHC.

---

## Current state

Pipeline is in its final audited state. Full-stats MEHFC 5-iter unfold has
completed on the patched-`IsMinosMatchMuon()` event-loop output. The
remaining low-p_|| disagreement with the paper is attributed to local
flux-CV files differing from the paper-era release; see "Residual
disagreement" below. No further pipeline TODO is expected to close it
without replacing the flux-CV inputs.

For the full chronology of how each finding was reached, see
`2D_OMNIFOLD_RUN_LOG.md`.

---

## Key reference numbers (full ME FHC, patched MINOS, 5-iter production)

| Quantity | Value |
|---|---|
| mcPOT (sum of 12 playlists) | 4.978e21 |
| dataPOT (sum of 12 playlists) | 1.057e21 |
| potScale (data/MC) | 0.2124 |
| Weighted full-MEHFC flux integral | 8.7407e-7 /cm²/POT |
| N fiducial nucleons | 3.2353e30 (tracker geometry constant) |
| Selected data events (reco) | 4,091,707 |
| `hMeasSub2D` integral (data − bkg) | 4.07664e6 |
| `hTruth2D` / `hUnfold2D` integrals | 4.33620e6 / 4.87974e6 |
| Step-2 weight stats | mean 1.1212, range [0.7383, 3.5332] |
| Total xsec (p_T projection = p_|| projection) | 2.285e-38 cm²/nucleon |
| Strict-interior χ²/ndf vs paper (185 bins, full cov) | 17.443 |
| All-reported-bins χ²/ndf (205 bins, full cov) | 20.605 |
| Median bin ratio (ours/paper, strict interior) | 0.8968 |

Paper total (reported): 2.74e-38 cm²/nucleon. Our sum over reported bins is
~16.6 % low; the deficit is concentrated at low p_|| (see below).

### Playlist 1A validation set (post-MINOS-fix)

| Quantity | Value |
|---|---|
| 1A mcPOT / dataPOT / potScale | 4.069e20 / 8.973e19 / 0.2205 |
| 1A 5-iter total xsec | 2.328e-38 cm²/nucleon |
| 1A 5-iter strict-interior χ²/ndf vs paper | 18.4 |
| In-sample closure median ratio / RMS | 1.0000 / 0.0000 |

### Iteration convergence (1A, corrected pre-MINOS-fix scan)

| iter | hUnfold2D | xsec (cm²/nucleon) | rel RMS vs 10-iter |
|---|---|---|---|
| 1 | 448,066 | 2.4775e-38 | 6.95% |
| 3 | 448,958 | 2.4825e-38 | 3.71% |
| 5 | 449,273 | 2.4842e-38 | 2.11% |
| 8 | 449,507 | 2.4855e-38 | 0.78% |
| 10 | 449,649 | 2.4863e-38 | 0.00% |

Production uses **5 iterations** (0.08 % bias on total xsec vs 10-iter;
~17 h runtime saved).

### Residual low-p_|| deficit (MEHFC strip sum-ratio, ours/paper, interior)

| p_|| strip (GeV/c) | ratio | | p_|| strip (GeV/c) | ratio |
|---|---|---|---|---|
| 1.5–2.0 | 0.572 | | 5–6   | 0.849 |
| 2.0–2.5 | 0.635 | | 10–15 | 0.920 |
| 2.5–3.0 | 0.710 | | 20–40 | 0.984 |
| 3.0–3.5 | 0.728 | | 40–60 | 1.006 |

Monotonic gradient. High-p_|| agreement to ~1 % rules out a uniform
normalization error in POT, nucleon count, or bulk background subtraction.

---

## Residual disagreement — attribution

Per-reweighter decomposition (`decompose_truth_weights.py`, with the
`MNV101_DUMP_COMPONENTS` truth-tree dump branches) shows the low-p_||
shape is carried entirely by `FluxAndCVReweighter`. Relative to the
high-p_|| plateau:

| p_|| (GeV/c) | combined truth | FluxAndCV | GENIE | 2p2h | MINOSEff | RPA |
|---|---|---|---|---|---|---|
| 1.5–2.0 | 0.666 | **0.672** | 0.992 | 1.000 | 1.000 | 0.998 |
| 5–6     | 0.679 | **0.704** | 0.961 | 1.016 | 1.000 | 0.987 |
| 10–15   | 0.837 | **0.844** | 0.993 | 1.004 | 1.000 | 0.995 |
| 20–40   | 0.899 | **0.899** | 1.000 | 0.998 | 1.000 | 1.000 |
| 40–60   | 1.101 | **1.101** | 1.000 | 1.002 | 1.000 | 1.000 |

`FluxAndCV` is `PlotUtils::flux_reweighter().GetFluxCVWeight(E_ν, pdg)` —
the nu-e-constrained CV flux divided by the Geant4 baseline. Local files
used:
`opt/lib/data/flux/flux-{gen2thin,g4numiv6}-pdg{14,-14,12,-12}-minervame1D_rearrangedUniverses.root`.

The paper's MnvTune-v1 model curve in
`minerva_paper_anc/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt`
is supposed to include the same flux CV reweighting (paper Sec. V). The
shape ratio paper/ours = 1.41 at p_||=1.5–2 GeV/c — consistent with our
local flux files differing from the paper-era release at low E_ν.

**Conclusion**: full quantitative reproduction of arXiv:2106.16210 needs
the 2021 flux-CV release. Without it, the result stands as the canonical
migrated OmniFold pipeline with an explicit low-p_|| flux-CV systematic.
Decision (2026-04-25, by user): keep the current flux files, finish the
pipeline, document the systematic.

The MINOS-match patch (Phase 11 of the run log) was a real bug fix that
brought the background rate from ~10 % down to 0.35 % (paper ≈ 0.2 %),
but it did not flatten the low-p_|| gradient — confirming the gradient
is truth/weight-side rather than reco-selection-side. Reco selection and
truth phase space are canonical (cross-checked against
`MAT-MINERvA/calculators/CCInclusiveCuts.h::GetCCInclusive2DCuts` and
`CCInclusiveSignal.h::GetCCInclusive2DPhaseSpace`).

---

## Paper binning (arXiv:2106.16210)

Authoritative: `minerva_paper_anc/bin_mapping.txt`. The TH2D axis labels in
the ancillary ROOT file are **cosmetic rounding** (0.075, 0.325, 0.475) —
do not copy them into `util/Binning.h`.

```python
pt_edges = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
            0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]         # 14 bins
pz_edges = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
            6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0]  # 16 bins
```

Phase space: θ_μ < 20°, p_T < 4.5 GeV/c, 1.5 < p_|| < 60 GeV/c.
Paper reports 205/224 bins (19 diagonal bins with pt/p|| > tan 20° are
unreported).

---

## Runtime notes

| Task | Resource | Wall time |
|---|---|---|
| C++ event loop, one playlist | shared QOS, 1 task | ~3.5 h |
| Event loop, all 12 playlists | 11-task array | ~3.7 h (parallel) |
| 2D OmniFold, 5-iter, 1A stats | shared QOS, 2 CPU, 8 GB | ~1.4 h |
| 2D OmniFold, 5-iter, full stats | shared QOS, 4 CPU, 32 GB | ~20 h |

---

## Active code

### C++ event loop (`MINERvA101/MINERvA-101-Cross-Section/`)
- `runEventLoopOmniFold.cpp` — per-playlist event loop; writes 4 TTrees
  (`mc_truth_denom`, `mc_signal_reco`, `mc_background`, `data`) with both
  `p_T` and `p_||` branches. Per-reweighter dump branches behind
  `MNV101_DUMP_COMPONENTS`. Does **not** write `pTmu_fiducial_nucleons`
  (was hadd-corrupted).
- `cuts/MaxPtMu.h`, `util/Binning.h` — paper phase-space cut and binning.
- `event/CVUniverse.h` — kinematic getters and patched MINOS-match
  override (`isMinosMatchTrack && _minos_trk_is_ok`).

### Python (`2d-unfolding/`)
- `unfold_2d_omnifold_unbinned.py` — 2D unbinned OmniFold. Masks data to
  phase space, subtracts background, fills `hUnfold2D` with
  `step2_weights * truth_w_in`, **does not** divide by `hEff2D`.
- `plot_2d_cross_section.py` — slice grids, projections, efficiency map.
- `plot_2d_paper_comparison.py` — same overlaid with paper MINERvA-Tune-v1.
- `plot_2d_threeway_fig13.py` — Fig.-13-style paper / OmniFold / MC overlay.
- `plot_efficiency_fig5_style.py` — Fig.-5-style efficiency map.
- `plot_closure_2d.py` — closure diagnostic.
- `plot_iter_convergence.py` — iter-scan summary.
- `compare_to_paper_fullcov.py` — full-cov χ² on all 205 reported bins.
- `compare_to_paper_interior.py` — strict-interior χ² on 185 bins.
- `combine_flux_MEHFC.py` — POT-weighted MEHFC flux from per-playlist
  baseline-flux ROOTs.
- `decompose_truth_weights.py` — per-reweighter truth-weight decomposition
  using the `MNV101_DUMP_COMPONENTS` dump tree.
- `diagnose_truth_shape_vs_paper.py` — paper Tune-v1 model vs local
  `hTruth2D` shape.

### SLURM (`2d-unfolding/`)
- `sbatch_evloop_array.sh` — per-playlist event-loop array.
- `sbatch_unfold_2d.sh` / `sbatch_unfold_2d_fullstats.sh` — 2D unfold (1A / MEHFC).
- `sbatch_iter_scan_2d.sh` — iter-scan array.
- `sbatch_finalize_MEHFC.sh` — full-cov + interior χ² and plot regen.
- `sbatch_validate_1A_corrected.sh` — end-to-end 1A validation.
- `sbatch_runEventLoop_baseline_flux_array.sh` — regen baseline flux per playlist.
- `download_playlist.sh` + `sbatch_download_playlist.sh` — xrdcp via xfer QOS.

### Data / outputs
- `runEventLoopOmniFold_MEHFC.root` (2.17 GB, hadd of per-playlist).
- `runEventLoopOmniFold_1{B..P}.root` — per-playlist intermediates.
- `runEventLoopOmniFold_1A_minos_fix.root` — patched-MINOS 1A.
- `2d_crossSection_omnifold_MEHFC_5iter.root` — **production** output.
- `2d_crossSection_omnifold_1A_minos_fix_{1,3,5}iter.root` — patched-MINOS 1A.
- `2d_crossSection_omnifold_1A_corrected_{1,3,5,8,10}iter.root` — pre-MINOS-fix iter scan.
- `baseline_flux/` — per-playlist baseline + `runEventLoopMC_MEHFC.root`
  (POT-weighted MEHFC flux).
- `minerva_paper_anc/` — arXiv ancillary release (TH2D, 4 cov matrices,
  bin_mapping.txt, data CSV, model predictions).

### Manifests (`2d-unfolding/playlist_manifests/`)
- `1{A..P}_{MC,Data}.txt` — per-playlist local paths.
