# 2D OmniFold Study — Status

**Last updated**: 2026-05-20 (Phase-18.2 production unfold and 1A iter-scan
landed; HistGBT estimator ported and validated; ML-stochasticity seedscan
**complete (n=10, sbatch 53192001)** — total-σ spread 0.007%, per-bin
median 0.36%.)

Companion docs: `2D_OMNIFOLD_REFERENCE.md` (workflow invariants and gotchas),
`2D_OMNIFOLD_RUN_LOG.md` (timestamped chronology of all phases),
`PLOT_GUIDE.md` (PNG index and naming convention).

---

## Goal

Reproduce arXiv:2106.16210 (Ruterbories et al., Phys. Rev. D 106, 032001) —
MINERvA ME FHC d²σ/(dp_T dp_||) CC inclusive — with 2D **unbinned** OmniFold
in place of D'Agostini IBU. Validated on playlist 1A, then run on full
12-playlist ME FHC.

---

## Current state

Pipeline is finalized at **Phase 18.2** (2026-05-18). Defining properties:

- **Truth-tree-authoritative reco gate.** Event loop walks `mc_truth_denom`
  first to build an event-ID key set, then walks the reco tree filling
  `mc_signal_reco` only when the key is in the truth-denom set. Truth-only
  events are appended as native OmniFold miss entries.
- **By-construction completeness.** `mc_signal_reco` entries ==
  `mc_truth_denom` entries (32,849,103 each at MEHFC). Global OmniFold input
  completeness `c = 1.000000` exact (sub-ppm). The Phase-16 phenomenological
  c-division is now a no-op self-check.
- **Upstream-dup tolerant.** Both truth and reco loops dedupe on
  `(mc_run, mc_subrun, mc_nthEvtInFile)` packed into a `uint64_t` key. At
  MEHFC scale the WARN logs report 133 truth and 7 reco duplicate entries
  skipped, all originating in `MasterAnaDev_mc_AnaTuple_run00111353_Playlist.root`.
- **Production output**: `2d_crossSection_omnifold_MEHFC_5iter.root` from
  5-iter unfold of `runEventLoopOmniFold_MEHFC.root`.

Pre-Phase-18 baselines preserved under `archive_pre_phase16/` (pre-Phase-16
postfix) and `archive_pre_phase18/` (Phase-16/17 superseded artifacts).

---

## Key reference numbers (full ME FHC, 5-iter production)

Current headline values are from Phase-18.2 unfold (job 53116554,
2026-05-19). The 7-entry reco-side dedupe vs Phase-18.1 produced a ~0.1
shift in χ²/ndf (3.565 → 3.661 on the 205-bin full cov), within the
expected sub-ppm event-level shift.

| Quantity | Value |
|---|---|
| mcPOT / dataPOT / potScale | 4.978e21 / 1.057e21 / 0.2124 |
| Weighted MEHFC flux integral | 8.7407e-7 /cm²/POT |
| N fiducial nucleons (tracker geometry) | 3.2353e30 |
| Selected data events (reco) | 4,091,707 |
| `hMeasSub2D` integral (data − bkg) | 3.97257e6 |
| `hTruth2D` / `hUnfold2D` integrals | 5.77954e6 / 6.56409e6 |
| `hOFInputTruth2D` / `hOFTruthDenom2D` integrals | 5.77954e6 / 5.77954e6 |
| Global OmniFold input completeness c | **1.000000** (exact by construction) |
| Step-2 weight stats | mean 1.1321, range [0.7472, 3.6948] |
| Total xsec (p_T projection = p_\|\| projection) | **3.073e-38 cm²/nucleon** |
| σ_total(ours) / σ_total(paper) | **1.0111** |
| χ²/ndf vs paper (205 paper-reported bins, full cov) | **3.661** |
| Shape-only χ²/ndf (205 bins, total cov) | **3.596** |
| Pull mean / RMS (205 reported bins, full cov) | 0.089 / 0.598 |
| Median bin ratio (ours/paper, 205 bins) | **1.0064** |
| Bins within 5 % / 10 % / 20 % of paper (205 bins) | 77.6 % / 94.1 % / 98.5 % |

Paper total (reported): 3.039e-38 cm²/nucleon. All per-bin numbers are
over the 205 bins the paper reports (`xs > 0` in
`data_result_ptpl_2D_minerva_inclusive_6GeV.txt`); the 19 paper-unreported
cells are dropped from both sides.

### χ² vs p_||-min cut (MEHFC, 205-bin baseline shrunk by p_||, full cov)

| p_\|\| ≥ (GeV/c) | N bins | χ² | χ²/ndf | median ratio | %<5% |
|---|---|---|---|---|---|
| 1.5 | 205 | 750.49 | 3.661 | 1.0064 | 77.6 % |
| 2.0 | 196 | 685.36 | 3.497 | 1.0059 | 80.1 % |
| 2.5 | 186 | 545.87 | 2.935 | 1.0059 | 81.7 % |
| 3.0 | 175 | 474.84 | 2.713 | 1.0059 | 81.1 % |
| 3.5 | 163 | 452.95 | 2.779 | 1.0073 | 80.4 % |
| 4.0 | 151 | 428.72 | 2.839 | 1.0068 | 79.5 % |

χ²/ndf is approximately p_||-flat post-Phase-16; the residual is dominated
by sub-2% shape disagreement in the highest p_|| tails (see Residual
disagreement below).

---

## Iteration convergence

Production uses **5 iterations**. Phase-18.2 1A iter-scan (job
53116867_[1,3,5,8,10], rerun for OOM as 53118557_3) re-validates the
choice on the post-Phase-18 input:

| iter | hUnfold2D | xsec (cm²/nucleon) | rel RMS vs 10-iter |
|---|---|---|---|
| 1  | 551,609 | 3.0501e-38 | 4.999% |
| 3  | 552,016 | 3.0523e-38 | 2.534% |
| 5  | 551,972 | 3.0521e-38 | 1.537% |
| 8  | 552,069 | 3.0526e-38 | 0.555% |
| 10 | 552,124 | 3.0529e-38 | 0.000% |

Total xsec is locked in by iter-3 (5-iter is within 0.026% of 10-iter,
well under 0.5%). Per-bin shape RMS at 5-iter is 1.54% — small vs the
paper-comparison disagreement (χ²/ndf ≈ 3.7). An 8-iter MEHFC parallel
run (job 53159240) is queued behind the 2026-05-20 NERSC maintenance
window for an explicit production cross-check; expected to land ~2026-05-28.

---

## GBDT estimator (HistGBT port, 2026-05-19)

The original code uses sklearn `GradientBoostingClassifier`
(`unbinned_unfolding/python/omnifold.py`), which is **single-threaded by
design** — the 128-CPU production allocation has only one core actually
working. Ported to `HistGradientBoostingClassifier` (256-quantile
histogram binning, OpenMP-parallel) gated behind a new
`--estimator {exact,hist}` flag (`exact` is the default for back-compat).
Matched defaults: 100 trees, `max_leaf_nodes=8` (≈ depth 3), `lr=0.1`.

### Speedup vs exact GBT

| Run | Wall time | Notes |
|---|---|---|
| Exact GBT, 5-iter MEHFC (production) | 69,523 s (19h18m) | 128 CPU, single-threaded |
| HistGBT, 1-iter MEHFC (smoke 2026-05-19) | 355 s | 32 CPU, OMP_NUM_THREADS=32 |
| **HistGBT, 5-iter MEHFC** | **1,053 s (17m33s)** | **32 CPU; 66× speedup measured** |

1-iter wallclock ratio ≈ **40×**; full 5-iter unfold **66×** measured
(**~79×** on pure training time after subtracting ~180 s one-shot I/O).

### Iteration convergence comparison (1A, 2026-05-19)

Per-bin relative shape RMS vs each estimator's own 10-iter asymptote:

| iter | exact GBT | HistGBT |
|---|---|---|
| 1 | 5.00% | 2.43% |
| 3 | 2.53% | 1.16% |
| 5 | 1.54% | 0.86% |
| 8 | 0.55% | 0.67% |
| 10 | 0 (ref) | 0 (ref) |

HistGBT plateaus **~2× faster** through iter 5. The two estimators
converge to total σ that agree to **0.04%** (exact 10-iter =
3.0529e-38, hist 10-iter = 3.0516e-38) — well within expected ML-noise
budget. 5 iterations remains the production choice for consistency with
the existing iter-scan analysis and the queued seed scan, but is more
than enough for HistGBT (5-iter HistGBT shape stability ≈ 7-iter
exact GBT).

Comparison plot: `histgbt_iter_scan/1A_iterscan_convergence_hist_vs_exact.png`.

### Validation status

5-iter MEHFC HistGBT (interactive 53179085, 2026-05-19) closed the
validation:

| | Exact 5-iter | HistGBT 5-iter |
|---|---|---|
| Total σ (cm²/nucleon) | 3.073e-38 | 3.073e-38 ✓ (4 sig figs) |
| σ / paper | 1.0111 | 1.0111 ✓ |
| hUnfold2D | 6.56409e+06 | 6.5627e+06 (−0.02%) |
| step2 sum | 3.719e+07 | 3.718e+07 |
| step2 mean | 1.1321 | 1.1317 |
| c | 1.0000 | 1.0000 |

Output: `histgbt_smoke/2d_crossSection_omnifold_MEHFC_5iter_histgbt.root`.
The 1A 10-iter 0.04% asymptotic gap between estimators does not
survive to MEHFC at the production iter count — the methods land on
the same physics answer.

---

## ML-stochasticity seedscan (n=10, 2026-05-20)

Advisor's headline ask: how much does the OmniFold result move when only
the ML training stochasticity changes? Ten 5-iter MEHFC HistGBT trials
were run with `random_state` pinned via `--seed N` (step1 = N, step2 =
N+1, regressor = N+2) so each trial is reproducible and the only
difference between trials is the seed. sbatch array 53192001 on
dedicated nodes; per-trial wall ~17 min.

| Metric | Value |
|---|---|
All per-bin stats below are over the **205 paper-reported bins**
(`cross_section > 0` in `data_result_ptpl_2D_minerva_inclusive_6GeV.txt`).
The 19 paper-unreported cells are dropped; no additional strict-interior
mask is applied.

| Metric | Value |
|---|---|
| Total σ across 10 trials | 3.0728e-38 ± 2.2e-42 cm²/nucleon |
| **Total-σ relative spread** | **0.007%** |
| Per-bin rel spread — median (p50) | **0.36%** |
| — p16 / p84 | 0.18% / 0.74% |
| — max single bin | 1.87% |
| Shape-only (each trial / its own σ_tot), median | 0.36% |
| 1D pT projection, median rel spread | 0.13% |
| 1D p∥ projection, median rel spread | 0.15% |

`p84` is the 84th percentile across the 205 reported bins (one-sided
+1σ-equivalent of the per-bin spread distribution). Median / p16 / p84
are reported because the spread distribution has a long tail driven by
a handful of low-statistics bins; `mean ± std` would overstate the
typical bin.

ML noise is **well below the paper's reported uncertainty** on every
comparison. Paper totals computed from the ancillary release
(`minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV_total.txt` +
`data_result_ptpl_2D_minerva_inclusive_6GeV.txt`):

| Quantity | ML seedscan (n=10) | Paper (ancillary) | Ratio |
|---|---|---|---|
| Total σ relative uncertainty | 0.007% | 4.61% (sqrt(wᵀCw), bin-width weights) | ML ≈ 0.15% of paper |
| Per-bin median rel uncertainty (205 bins) | 0.36% | 6.86% (total_uncertainty / xsec) | ML ≈ 5% of paper |
| Per-bin p84 rel uncertainty (205 bins) | 0.74% | 9.16% | ML ≈ 8% of paper |

So ML stochasticity is **not a leading uncertainty** — confidently
subdominant to the systematics the paper reports (flux, energy scale,
cross-section model) and to the systematics still to be characterized
in this method. Going from n=4 → n=10 moved the headline numbers
marginally (0.008%→0.007% on total σ; 0.36% per-bin median in both),
indicating the envelope has converged.

Outputs: `seedscan/2d_crossSection_omnifold_MEHFC_5iter_seed{1..10}.root`,
`seedscan/seedscan_spread_2d.png`, `seedscan_band_pt.png`,
`seedscan_band_pz.png`. Re-run: `python3 seedscan/analyze_seedscan.py`.

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

Phase space: θ_μ < 20°, p_T < 4.5 GeV/c, 1.5 < p_|| < 60 GeV/c. Paper reports
205/224 bins (19 diagonal bins with pt/p|| > tan 20° are unreported).

---

## Runtime notes

| Task | Resource | Wall time |
|---|---|---|
| C++ event loop, one playlist | shared QOS, 1 task | ~2 h (1E was 2h07m on Phase-18.2) |
| Event loop, all 12 playlists | 11-task array | ~3-4 h (parallel) |
| hadd MEHFC | shared QOS | < 1 min |
| 2D OmniFold, 5-iter, 1A stats, exact GBT | shared QOS, 2 CPU | ~1.5 h |
| 2D OmniFold, 5-iter, full MEHFC, exact GBT | regular QOS, 128 CPU | ~19 h (≈3h50m/iter × 5) |
| 2D OmniFold, 1A iter scan {1,3,5,8,10}, HistGBT | interactive, 32 CPU | ~6.5 min total |
| 2D OmniFold, 1-iter MEHFC, HistGBT | interactive, 32 CPU | ~6 min |
| 2D OmniFold, 5-iter MEHFC, HistGBT | interactive, 32 CPU | 17m33s measured (66× speedup) |

**Ideal HistGBT trial configuration (2026-05-19).** Validated baseline is
1 process × 32 threads on a dedicated node (17m33s). Memory-bandwidth
contention makes parallel trials on a shared node a net loss: 4-wide × 32
≈ 8× slower per trial, 2-wide × 64 ≈ 4.5× slower per trial. Run the
seedscan as an sbatch array (one node per task), never as 4×/2× srun on
an interactive. Per-trial scaling above 32 threads on a dedicated node
is unmeasured — sklearn HistGBT typically caps at ~16–32 threads/fit, so
don't assume more cores help without a one-trial benchmark first. See
RUN_LOG "Ideal HistGBT trial configuration" entry.

---

## How we got here

For the full chronology, see `2D_OMNIFOLD_RUN_LOG.md`. One-line summary of
the residual-driving phases:

| Phase | Symptom | Fix |
|---|---|---|
| 16 (2026-05-08) | σ/paper = 0.752, χ²/ndf = 17.4 with monotonic low-p_\|\| deficit | Missing OmniFold input-completeness correction: `unfold` now divides by `hOFCompleteness2D = hOFInputTruth2D / hOFTruthDenom2D`, not by absolute selection efficiency. Result: σ/paper = 1.0049, χ²/ndf = 3.188. |
| 17 (2026-05-14) | c=0.75 is a phenomenological band-aid; OmniFold should handle truth-only events natively | Event-ID matching on `(mc_run, mc_subrun, mc_nthEvtInFile)`. Reco loop populates a key set; truth-denom loop appends miss entries for unmatched truth-pass events. |
| 18 (2026-05-14) | Phase 17 left c=1.018 — 48,349 reco-tree-only entries had no truth-denom match (CC-numu daughter-muon matching ambiguity) | Truth-tree-authoritative reco gate: truth-denom loop runs first and builds `truthDenomIDs`; reco loop fills `mc_signal_reco` only when key ∈ `truthDenomIDs`. c lands at 1.0000. |
| 18.1 (2026-05-15) | 98-entry deficit at MEHFC, traced to 1,102 doubled truth entries in `run00111353_Playlist.root` (upstream re-tupling artifact) | Truth-side dedupe via `seenKeys` set; WARN log emits skip count. |
| 18.2 (2026-05-18) | 7-entry reco surplus at MEHFC from same AnaTuple's reco-side double-fill | Reco-side mirror dedupe; c now exact to sub-ppm. |

The Phase-15/16 attribution work definitively ruled out the residual being
caused by: flux-CV file mismatch (0.90 flat ratio cancels in xsec),
AnaTuple generator-config mismatch (local truth + MnvTune-v1 reproduces
paper ancillary ≤1% across p_|| = 1.5-9 GeV/c), selection cut mismatch, or
reweighter-chain version. Method-blindness was confirmed by IBU 1D-projection
cross-check (post-Phase-16): IBU and OmniFold-2D agree on the same inputs
to ~1.7%, both reproduce paper to within ~1-2%.

---

## Residual disagreement

The remaining ~3 χ²/ndf is dominated by sub-2% shape disagreement in the
highest p_|| tails (paper / weighted reaches 1.15 at 40-60 GeV/c). Attributed
to a small reweighter-detail effect at high E_ν; not an OmniFold pathology,
not a missing-input problem, and consistent with MC statistical noise in
the tails. Not pursued further — see `2D_OMNIFOLD_RUN_LOG.md` Phase 15-16
for the full attribution chain.

Note that the AnaTuple double-fill in `run00111353_Playlist.root` (1,102
truth duplicates + 7 reco duplicates) was an **upstream MINERvA AnaTuple
issue** that has been silently inflating the 1E efficiency denominator in
every prior analysis using that file. Effect: ~3×10⁻⁴ in 1E, ~3×10⁻⁵ in
MEHFC — below MINERvA systematics but flagged for AnaTuple producers.

---

## Active code

### C++ event loop (`MINERvA101/MINERvA-101-Cross-Section/`)
- `runEventLoopOmniFold.cpp` — per-playlist event loop with Phase-18.2
  truth-authoritative gate + bilateral dedupe. Writes 4 TTrees
  (`mc_truth_denom`, `mc_signal_reco`, `mc_background`, `data`) with both
  `p_T` and `p_||` branches. Per-reweighter dump branches behind
  `MNV101_DUMP_COMPONENTS`. `MNV101_DISABLE_TRUTH_MISSES=1` falls back to
  legacy behavior.
- `cuts/MaxPtMu.h`, `util/Binning.h` — paper phase-space cut and binning.
- `event/CVUniverse.h` — kinematic getters and patched MINOS-match
  override (`isMinosMatchTrack && _minos_trk_is_ok`).

### Python (`2d-unfolding/`)
- `unfold_2d_omnifold_unbinned.py` — 2D unbinned OmniFold. Masks data to
  phase space, subtracts background, fills `hUnfold2D` with
  `step2_weights * truth_w_in`, divides by `hOFCompleteness2D`. Under
  Phase 18.2 this division is a no-op (c=1) but kept as a regression
  check. Exposes `--seed N` (pins sklearn GBDT random_state across
  step1/step2/regressor for the ML-stochasticity seed scan) and
  `--estimator {exact,hist}` (default `exact`; `hist` swaps in
  HistGradientBoosting via `unbinned_unfolding/python/omnifold.py`).
- `plot_2d_cross_section.py` — slice grids, projections, efficiency map.
- `plot_2d_paper_comparison.py` — overlay with paper MINERvA-Tune-v1.
- `plot_2d_threeway_fig13.py` — Fig.-13-style paper / OmniFold / MC overlay.
- `plot_efficiency_fig5_style.py` — Fig.-5-style efficiency map.
- `plot_closure_2d.py` — closure diagnostic.
- `plot_iter_convergence.py` — iter-scan summary.
- `seedscan/analyze_seedscan.py` — load N seed-trial ROOTs and emit
  per-bin mean/std, total-σ spread, shape-only spread, and a 14×16
  rel-spread heatmap + pT/pz band plots. Outputs to its own cwd.
- `histgbt_iter_scan/compare_iter_convergence.py` — overlay 1/3/5/8/10-iter
  exact-GBT and HistGBT 1A unfolds: hUnfold2D, total σ, and per-bin
  shape RMS vs each estimator's own 10-iter asymptote.
- `compare_to_paper_fullcov.py` — full-cov χ² on 205 paper-reported
  bins. This is the canonical paper-comparison; produces the χ²/ndf
  numbers reported in STATUS.
- `compare_to_paper_interior.py` — legacy diagnostic: strict-interior
  χ² on 185 bins (excludes the 20 paper-reported bins that straddle
  the θ_μ = 20° cone). Useful for sensitivity checks; not the
  headline number.
- `normalize_xsec_shape.py` — produces `*_shape.root` for shape-mode
  comparisons; emits 205-bin (canonical) and 185-bin (diagnostic)
  shape χ² with paper TotalCovariance propagated through the
  unit-area Jacobian.
- `plot_2d_paper_comparison_shape.py` — shape-mode paper-comparison plots.
- `combine_flux_MEHFC.py` — POT-weighted MEHFC flux from per-playlist
  baseline-flux ROOTs.

Phase 15/16 attribution one-offs (`compare_flux_to_paper_2019.py`,
`diagnose_truth_shape_unweighted.py`, `verify_eff_fix_predicted_xsec.py`,
`plot_minos_fix_bkg_fraction.py`) were deleted on 2026-05-19; their
findings live in `2D_OMNIFOLD_RUN_LOG.md` and source can be recovered
from git history if needed.

### SLURM (`2d-unfolding/`)
- `sbatch_build.sh` — rebuild C++ event-loop binary into
  `MINERvA101/opt/bin/`.
- `sbatch_evloop_array.sh` — 11-task array, playlists 1B–1P. 1A is run
  separately.
- `sbatch_hadd_MEHFC.sh` — hadd 12 per-playlist ROOTs into MEHFC.
- `sbatch_unfold_2d_MEHFC.sh` — 2D OmniFold unfold, 5-iter, full-node 128 CPU.
- `sbatch_unfold_2d_MEHFC_8iter.sh` — parallel 8-iter MEHFC run (job
  53159240, queued behind 2026-05-20 maintenance).
- `sbatch_unfold_2d_MEHFC_5iter_seedscan.sh` — 10-trial seedscan array
  (`--array=1-10`, `--seed=$SLURM_ARRAY_TASK_ID`, 128 CPU). Job
  53180443_[1-10] queued behind maintenance; currently configured for
  exact GBT.
- `sbatch_unfold_2d_MEHFC_histgbt_smoke.sh` — 1-iter MEHFC HistGBT
  smoke test (32 CPU, 1h). Not used as the actual smoke was run via
  `srun --jobid=` into interactive 53179085.
- `sbatch_iter_scan_2d.sh` — 1A iter-scan array (1, 3, 5, 8, 10), exact
  GBT. The HistGBT companion scan was run inline via `srun --jobid=`
  into the interactive (~6.5 min total).
- `sbatch_runEventLoop_baseline_flux_array.sh` — regen per-playlist baseline
  flux.
- `sbatch_finalize_MEHFC.sh` — combined finalize step.
- `sbatch_validate_1A_corrected.sh` — end-to-end 1A validation.
- `sbatch_download_playlist.sh` — xrdcp via xfer QOS.

Pre-Phase-18 versions of these scripts are preserved in
`archive_pre_phase18/` with git history.

### Data / outputs
- `runEventLoopOmniFold_{1A..1P}.root` — per-playlist event-loop outputs
  (Phase 18.2).
- `runEventLoopOmniFold_MEHFC.root` (2.0 GB) — hadd of 12 per-playlist ROOTs.
- `2d_crossSection_omnifold_MEHFC_5iter.root` — production unfold output;
  Phase-18.1 baseline in place, Phase-18.2 re-unfold (job 53116554) writes
  same path on completion.
- `2d_crossSection_omnifold_1A_5iter.root` — 1A unfold; the iter-scan
  produces `2d_crossSection_omnifold_1A_{1,3,5,8,10}iter.root` siblings.
- `histgbt_iter_scan/2d_crossSection_omnifold_1A_{1,3,5,8,10}iter_histgbt.root`
  — HistGBT companion iter-scan (seed=1, 32 CPU, 32-thread OMP).
- `histgbt_smoke/2d_crossSection_omnifold_MEHFC_1iter_histgbt_smoke.root`
  — 1-iter MEHFC smoke for HistGBT validation.
- `histgbt_smoke/2d_crossSection_omnifold_MEHFC_5iter_histgbt.root` —
  5-iter MEHFC HistGBT (validation #16, measurement in flight as of
  2026-05-19 ~20:50 UTC).
- `seedscan/2d_crossSection_omnifold_MEHFC_5iter_seed{1..10}.root` —
  n=10 HistGBT 5-iter MEHFC trials (sbatch array 53192001, completed
  2026-05-20). Spread analysis PNGs alongside:
  `seedscan_spread_2d.png` (14×16 rel-spread heatmap),
  `seedscan_band_pt.png` / `seedscan_band_pz.png` (1D projection bands).
- `baseline_flux/` — per-playlist baseline + `runEventLoopMC_MEHFC.root`
  (POT-weighted MEHFC flux).
- `minerva_paper_anc/` — arXiv ancillary release (TH2D, 4 cov matrices,
  bin_mapping.txt, data CSV, model predictions).

### Archives (preserved for provenance)
- `archive_pre_phase16/` — pre-Phase-16 unfold outputs and derived plots
  (σ_total = 0.752 × paper).
- `archive_pre_phase18/` — Phase-16/17 era artifacts: pre-Phase-18 MEHFC
  ROOT (the headline "before" snapshot), superseded SLURM scripts,
  superseded SLURM logs. Trimmed on 2026-05-19: the four per-playlist
  and side-experiment ROOTs (`1M`, `1N`, `1A_phase17`, `1A_fakes-routed`,
  ~840MB total) were removed since their narrative is captured in the
  run log and they're reconstructible from an older commit if needed.

### Manifests (`2d-unfolding/playlist_manifests/`)
- `1{A..P}_{MC,Data}.txt` — per-playlist local paths.
