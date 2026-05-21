# 2D OmniFold Study — Status

**Last updated**: 2026-05-21. Phase-18.2 production unfold is in. HistGBT
estimator validated 1:1 against exact GBT (5-iter MEHFC). ML-stochasticity
seedscan complete (n=10, sbatch 53192001): total-σ rel spread 0.007%,
per-bin median 0.36%. HistGBT 8-iter convergence check in flight on
interactive 53256254 (seed=1; diff against `seedscan/...seed1.root`).
**Next focus: stat + systematic uncertainty quantification.**

Companion docs: `2D_OMNIFOLD_REFERENCE.md` (workflow invariants),
`2D_OMNIFOLD_RUN_LOG.md` (active chronology from 2026-05-18 onward),
`2D_OMNIFOLD_RUN_LOG_ARCHIVE.md` (Phases 1–18.1 history),
`PLOT_GUIDE.md` (PNG index).

---

## Goal

Reproduce arXiv:2106.16210 (Ruterbories et al., Phys. Rev. D 106, 032001)
— MINERvA ME FHC d²σ/(dp_T dp_||) CC inclusive — with 2D **unbinned**
OmniFold in place of D'Agostini IBU.

---

## Current state — Phase 18.2 pipeline (frozen 2026-05-18)

Defining properties:

- **Truth-tree-authoritative reco gate.** Event loop walks
  `mc_truth_denom` first to build an event-ID key set, then walks the
  reco tree filling `mc_signal_reco` only when the key is in that set.
  Truth-only events appended as native OmniFold miss entries.
- **By-construction completeness `c = 1.000000`** (exact, sub-ppm).
  `mc_signal_reco` entries == `mc_truth_denom` entries (32,849,103
  each at MEHFC). The Phase-16 c-division is now a no-op self-check.
- **Bilateral dedupe** on `(mc_run, mc_subrun, mc_nthEvtInFile)` packed
  into `uint64_t`. At MEHFC: 133 truth and 7 reco duplicates skipped,
  all from `MasterAnaDev_mc_AnaTuple_run00111353_Playlist.root`.
- **Production output**: `2d_crossSection_omnifold_MEHFC_5iter.root`
  from 5-iter unfold of `runEventLoopOmniFold_MEHFC.root`, exact GBT.

How we got here (Phases 1–18.1, attribution of the σ/paper=0.752 and
χ²/ndf≈17 residuals): see `2D_OMNIFOLD_RUN_LOG_ARCHIVE.md`.

---

## Headline numbers (Phase-18.2 MEHFC 5-iter production)

| Quantity | Value |
|---|---|
| mcPOT / dataPOT / potScale | 4.978e21 / 1.057e21 / 0.2124 |
| Weighted MEHFC flux integral | 8.7407e-7 /cm²/POT |
| N fiducial nucleons (tracker geometry) | 3.2353e30 |
| Selected data events (reco) | 4,091,707 |
| `hMeasSub2D` integral (data − bkg) | 3.97257e6 |
| Global OmniFold completeness c | **1.000000** (exact by construction) |
| Total xsec | **3.073e-38 cm²/nucleon** |
| σ_total(ours) / σ_total(paper) | **1.0111** |
| χ²/ndf vs paper (205 paper-reported bins, full cov) | **3.661** |
| Shape-only χ²/ndf (205 bins, total cov) | **3.596** |
| Pull mean / RMS (205 bins) | 0.089 / 0.598 |
| Median bin ratio (ours/paper, 205 bins) | **1.0064** |
| Bins within 5 % / 10 % / 20 % of paper | 77.6 % / 94.1 % / 98.5 % |

Paper total: 3.039e-38 cm²/nucleon. All per-bin numbers are over the
**205 bins the paper reports** (`xs > 0` in
`data_result_ptpl_2D_minerva_inclusive_6GeV.txt`); 19 paper-unreported
cells dropped from both sides.

### χ² vs p_||-min cut (205-bin baseline shrunk by p_||, full cov)

| p_\|\| ≥ (GeV/c) | N bins | χ² | χ²/ndf | median ratio | %<5% |
|---|---|---|---|---|---|
| 1.5 | 205 | 750.49 | 3.661 | 1.0064 | 77.6 % |
| 2.0 | 196 | 685.36 | 3.497 | 1.0059 | 80.1 % |
| 2.5 | 186 | 545.87 | 2.935 | 1.0059 | 81.7 % |
| 3.0 | 175 | 474.84 | 2.713 | 1.0059 | 81.1 % |
| 3.5 | 163 | 452.95 | 2.779 | 1.0073 | 80.4 % |
| 4.0 | 151 | 428.72 | 2.839 | 1.0068 | 79.5 % |

Residual is dominated by sub-2% shape disagreement in the highest p_||
tails. Iteration convergence (1A iter-scan, archived): 5-iter total σ is
within 0.026 % of 10-iter, per-bin shape RMS 1.54 % — well below paper
disagreement. HistGBT/exact-GBT agree on total σ to **0.04 %** at 10
iters; 5-iter MEHFC numbers identical to 4 sig figs.

---

## ML-stochasticity envelope (seedscan n=10, 2026-05-20)

Ten 5-iter MEHFC HistGBT trials, `random_state` pinned via `--seed N`
(step1=N, step2=N+1, regressor=N+2). sbatch array 53192001, dedicated
nodes, per-trial wall ~17 min.

| Metric (205 paper-reported bins) | ML seedscan | Paper (ancillary) | Ratio |
|---|---|---|---|
| Total-σ rel spread | **0.007%** | 4.61% (sqrt(wᵀCw), bin-width weights) | ML ≈ 0.15% of paper |
| Per-bin median rel spread | **0.36%** | 6.86% (total_uncertainty/xsec) | ML ≈ 5% of paper |
| Per-bin p84 rel spread | 0.74% | 9.16% | ML ≈ 8% of paper |
| Per-bin max rel spread | 1.87% | — | — |
| 1D pT / p∥ projection median | 0.13 % / 0.15 % | — | — |

ML noise is **subdominant on every comparison** — not a leading
uncertainty. n=4 → n=10 moved headline numbers within rounding, so the
envelope has converged. Spread distribution is long-tailed (median ≪
mean+std), so medians/p84 are reported instead of std.

Outputs: `seedscan/2d_crossSection_omnifold_MEHFC_5iter_seed{1..10}.root`,
`seedscan/seedscan_spread_2d.png`, `seedscan_band_pt.png`,
`seedscan_band_pz.png`. Re-run: `python3 seedscan/analyze_seedscan.py`.

---

## Uncertainty quantification — next stage

The seedscan closes ML stochasticity. Two remaining uncertainty axes:

### Statistical (data Poisson fluctuations)
Bootstrap on the reco data: resample `data` TTree entries with
replacement, re-unfold each bootstrap sample at fixed seed=1 (HistGBT,
5-iter), accumulate the per-bin covariance across bootstrap unfolds.
Expected cost: ~17 min/trial × N_bootstrap; N≈50 should converge the
diagonal. Same `--seed 1` everywhere makes ML stochasticity cancel out
across the bootstrap (only the data resampling varies).

### Systematic (detector + flux + GENIE)
MnvH2D vertical universes live in `runEventLoopOmniFold_MEHFC.root` —
each systematic universe is an alternative event weight. Per-universe
pipeline:
1. Open the input ROOT, read universe weights for each event in the
   `mc_truth_denom` / `mc_signal_reco` trees.
2. Re-unfold with weights multiplied by the universe weight column,
   seed=1, HistGBT 5-iter.
3. Per-universe Δxsec / xsec_nominal → covariance contribution.

Categories: flux (NA49, pion-yield), GENIE (CCQE Ma, MEC, RES, etc.),
detector (muon energy scale, MINOS efficiency, recoil). Each is its own
universe group; sum diagonals in quadrature → total systematic cov.

Final uncertainty: stat ⊕ syst, compared against the paper's quoted
4.61% total — closes the apples-to-apples comparison the χ²/ndf=3.661
cannot make (since it uses the paper's covariance, not ours).

---

## Paper binning (arXiv:2106.16210)

Authoritative: `minerva_paper_anc/bin_mapping.txt`. TH2D axis labels in
the ancillary ROOT are cosmetic rounding — do not copy into
`util/Binning.h`.

```python
pt_edges = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
            0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]         # 14 bins
pz_edges = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
            6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0]  # 16 bins
```

Phase space: θ_μ < 20°, p_T < 4.5 GeV/c, 1.5 < p_|| < 60 GeV/c. Paper
reports 205/224 bins (19 diagonal cells with pt_hi/pz_lo > tan 20° are
unreported).

---

## Active code (`2d-unfolding/`)

- `unfold_2d_omnifold_unbinned.py` — 2D unbinned OmniFold. Exposes
  `--seed N` (pins step1/step2/regressor random_state) and
  `--estimator {exact,hist}` (HistGBT is ~66× faster, validated 1:1
  against exact at MEHFC).
- `compare_to_paper_fullcov.py` — **canonical** paper-comparison:
  full-cov χ² on 205 reported bins. Produces STATUS headline numbers.
- `compare_to_paper_interior.py` — legacy diagnostic on 185
  strict-interior bins; keep for sensitivity checks, not headline.
- `normalize_xsec_shape.py` — shape-mode comparison with paper
  TotalCovariance propagated through unit-area Jacobian (205 + 185).
- `plot_2d_cross_section.py`, `plot_2d_paper_comparison.py`,
  `plot_2d_paper_comparison_shape.py`, `plot_2d_threeway_fig13.py`,
  `plot_efficiency_fig5_style.py`, `plot_closure_2d.py` — plotting.
- `combine_flux_MEHFC.py` — POT-weighted MEHFC flux from per-playlist.
- `seedscan/analyze_seedscan.py` — N-trial spread heatmap + bands.

C++ event loop in `MINERvA101/MINERvA-101-Cross-Section/`:
- `runEventLoopOmniFold.cpp` — Phase-18.2 truth-authoritative gate +
  bilateral dedupe. Per-reweighter dumps behind `MNV101_DUMP_COMPONENTS`.
- `cuts/MaxPtMu.h`, `util/Binning.h`, `event/CVUniverse.h`.

---

## SLURM scripts (`2d-unfolding/`)

- `sbatch_build.sh` — rebuild C++ event-loop binary.
- `sbatch_evloop_array.sh` — 11-task array, playlists 1B–1P. 1A run separately.
- `sbatch_hadd_MEHFC.sh` — hadd 12 per-playlist → MEHFC.
- `sbatch_unfold_2d_MEHFC.sh` — production 5-iter unfold (128 CPU exact).
- `sbatch_unfold_2d_MEHFC_8iter.sh` — 8-iter HistGBT convergence check (32 CPU, 1 h).
- `sbatch_unfold_2d_MEHFC_5iter_seedscan.sh` — 10-trial seedscan (HistGBT, 32 CPU).
- `sbatch_runEventLoop_baseline_flux_array.sh` — per-playlist baseline flux.
- `sbatch_finalize_MEHFC.sh`, `sbatch_validate_1A_corrected.sh`,
  `sbatch_download_playlist.sh` — finalize / validate / xrdcp helpers.

---

## Data inventory

- `runEventLoopOmniFold_{1A..1P}.root` — per-playlist event-loop outputs.
- `runEventLoopOmniFold_MEHFC.root` (2.0 GB) — hadd of 12 playlists; **contains MnvH2D vertical universes for syst propagation**.
- `2d_crossSection_omnifold_MEHFC_5iter.root` — Phase-18.2 production (the χ²/ndf=3.661 result).
- `2d_crossSection_omnifold_MEHFC_8iter.root` — HistGBT 8-iter convergence check (in flight).
- `seedscan/2d_crossSection_omnifold_MEHFC_5iter_seed{1..10}.root` — n=10 HistGBT trials + spread PNGs.
- `baseline_flux/` — per-playlist baseline + `runEventLoopMC_MEHFC.root` (POT-weighted MEHFC flux).
- `minerva_paper_anc/` — arXiv ancillary release (TH2D, 4 cov matrices, bin_mapping.txt, data CSV, model predictions).

Archives: `archive_pre_phase16/` (pre-Phase-16 outputs, σ_tot=0.752×paper);
`archive_pre_phase18/` (Phase-16/17 superseded ROOTs + scripts; the
2026-05-21 cleanup added `iter_scan_1A/` and `histgbt_smoke/` here as
closed deliverables).

---

## Runtime budget (HistGBT-era)

| Task | Resource | Wall time |
|---|---|---|
| C++ event loop, one playlist | shared QOS, 1 task | ~2 h |
| Event loop, all 12 playlists | 11-task array | ~3–4 h (parallel) |
| 5-iter MEHFC unfold, **exact GBT** | regular QOS, 128 CPU | ~19 h (legacy production) |
| 5-iter MEHFC unfold, **HistGBT** | 32 CPU dedicated | **17m33s** (66× speedup) |
| Seedscan (10 trials, HistGBT) | sbatch array, one node each | ~17 min per task in parallel |

**HistGBT trial config.** Validated baseline: 1 process × 32 threads on
a dedicated node. Parallel trials on a shared node are memory-bandwidth
bound and lose net throughput (4-wide×32 ≈ 8× slower, 2-wide×64 ≈ 4.5×
slower). Always one node per trial. Above 32 threads on a dedicated
node is unmeasured — don't assume more cores help without benchmarking
first.
