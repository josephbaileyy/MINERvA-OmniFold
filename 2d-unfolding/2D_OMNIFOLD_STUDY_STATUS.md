# 2D OmniFold Study — Status

**Last updated**: 2026-05-27. Phase-18.2 production unfold frozen;
Stage-2 UQ closed (187-universe full lateral+vertical sweep, N=300
bootstrap, n=10 seedscan).

Companion docs: `2D_OMNIFOLD_REFERENCE.md` (workflow invariants),
`2D_OMNIFOLD_RUN_LOG.md` (chronology from 2026-05-18 onward),
`2D_OMNIFOLD_RUN_LOG_ARCHIVE.md` (Phases 1–18.1), `PLOT_GUIDE.md`.

---

## Goal

Reproduce arXiv:2106.16210 (Ruterbories et al., Phys. Rev. D 106, 032001)
— MINERvA ME FHC d²σ/(dp_T dp_||) CC inclusive — with 2D **unbinned**
OmniFold in place of D'Agostini IBU.

---

## Headline (MEHFC 5-iter lgbm, 205 paper-reported bins)

| Quantity | Value |
|---|---|
| Total xsec | **3.073e-38 cm²/nucleon** |
| σ_total(ours) / σ_total(paper) | **1.0111** |
| Median bin ratio (ours/paper) | 1.0064 |
| Bins within 5 % / 10 % / 20 % of paper | 77.6 % / 94.1 % / 98.5 % |
| Paper-cov-only χ²/ndf | **3.661** |
| Combined-cov χ²/ndf (paper + universe + boot N=300 + ML) | **0.943** |
| Pull mean / RMS (combined cov) | **0.068 / 0.310** |
| Pull mean / RMS (paper cov only) | 0.089 / 0.598 |
| Shape-only χ²/ndf (205 bins, paper cov, unit-area Jacobian) | 3.596 |
| Global OmniFold completeness c | 1.000000 (exact by construction) |

Paper total: 3.039e-38 cm²/nucleon. The 205-bin set is `xs > 0` in
`data_result_ptpl_2D_minerva_inclusive_6GeV.txt` (19 unreported cells
dropped from both sides).

### Methodology caveat on the 0.943 headline

Combined cov **double-counts** systematics shared with the paper
(flux / GENIE / RPA / 2P2H / MINOS). The naïve ours-only χ²/ndf is
**100** — diagnosed as ill-conditioning, NOT disagreement:
`cond(C_ours) = 5.6×10¹⁴` vs `cond(C_paper) = 1.5×10¹²`, effective
rank 200/205 because 187 universes underspan the 205-bin space. Three
honest readings of agreement:

| Reading | Value |
|---|---|
| Per-bin pull RMS, no inverse (ours-only σ_i) | **0.438** |
| Combined-cov χ²/ndf (conservative upper bound) | **0.943** |
| Truncated-mode χ²/rank, rcond=1e-4 (33 modes) | **0.67** |

Clean ours-only χ² would need either (a) substantially more universes
to fill the 205-dim space or (b) decorrelated combination stripping
shared blocks from C_paper before adding C_ours.

---

## Phase 18.2 pipeline (frozen 2026-05-18)

- **Truth-tree-authoritative reco gate.** `mc_signal_reco` filled only
  when `(mc_run, mc_subrun, mc_nthEvtInFile)` is in `mc_truth_denom`.
  Truth-only events appended as native OmniFold miss entries.
- **By-construction completeness c = 1.000000** (32,849,103 entries each
  at MEHFC). The Phase-16 c-division is a no-op self-check.
- **Bilateral dedupe** on the packed `uint64_t` event ID. 133 truth + 7
  reco duplicates skipped (all from one playlist file).
- **Production output**: `2d_crossSection_omnifold_MEHFC_5iter.root` —
  5-iter unfold of `runEventLoopOmniFold_MEHFC.root`, exact GBT.

History of the residual chase (σ/paper = 0.752 → 1.011, χ²/ndf 17 →
3.66): see `2D_OMNIFOLD_RUN_LOG_ARCHIVE.md`.

Iteration convergence (1A iter-scan, archived): 5-iter total σ within
0.026 % of 10-iter, per-bin shape RMS 1.54 %. HistGBT/exact-GBT agree
on total σ to 0.04 % at 10 iters; 5-iter MEHFC identical to 4 sig figs.

---

## Stage-2 UQ envelope (final)

Per-bin spreads over 205 paper-reported bins, against the MEHFC CV unfold.

| Component | N | √tr(C) | Per-bin median rel σ |
|---|---|---|---|
| ML noise (lgbm seedscan) | 10 | 5.061e-41 | 0.166 % |
| Statistical (Poisson bootstrap) | 300 | 1.828e-40 | 0.564 % |
| Systematic (universe sweep) | 187 | **4.335e-39** | **8.826 %** |
| **Combined (block sum)** | — | 4.339e-39 | ≈8.9 % (univ-dominated) |
| Paper TotalCov (for reference) | — | 2.676e-39 | 6.86 % |

Block sum assumes independence (different RNGs / different physics
sources). Cholesky on combined cov **PASS** without jitter.

**Top systematic bands** (median rel σ, 205 bins): Muon_Energy_MINOS
2.87 %, Muon_Energy_MINERvA 2.32 %, MinosEfficiency 1.93 %, MaRES
1.59 %, GEANT_Pion 1.32 %, MaCCQE 1.26 %. 44 bands total — 6 lateral
(BeamAngleX/Y, MuonResolution, GEANT_{Neutron,Pion,Proton},
Muon_Energy_MINERvA) + 38 vertical. Lateral bands re-run the event
loop with shifted detector quantities; vertical bands re-weight only.

**Methods.**
- *Stat*: per-event Poisson(1) on data and MC (independent sub-RNGs;
  same draw on MC truth/reco). ML seed pinned so noise cancels across
  replicas.
- *Syst*: pair bands (n=2) → `0.5·(Δ_+Δ_+ᵀ + Δ_−Δ_−ᵀ)` (MINERvA-101
  sum-of-squares). Multi-universe (n≥3) → `np.cov(rowvar=False, ddof=1)`.
  Bands summed independently.
- *ML*: 10-trial HistGBT seedscan, `random_state` pinned via
  `--seed N` (step1=N, step2=N+1, regressor=N+2).

**Headline rollup**: `uq/universe_stage2_MEHFC_full/compare_to_paper_combined_cov_full.log`.
**Component covs**: `uq/universe_stage2_MEHFC_full/uq_universe_covariance_full.root`,
`uq/bootstrap_MEHFC_300/uq_covariance_boot300.root`,
`uq/seedscan_lgbm_ml/uq_covariance_ml.root`. Headline pull plot:
`MEHFC_5iter_pull_full.png`.

---

## Calibration: coverage toys (20 closure+bootstrap-seed MEHFC toys)

| Metric | Measured | Theoretical (Gaussian 1σ) |
|---|---|---|
| Mean coverage | 67.90 % | 68.27 % |
| ⟨\|residual\|/σ⟩ | 0.794 | √(2/π) = 0.798 |
| Signed residual mean | −0.013 σ | 0 |

78 % of 205 bins meet the 65 % target; 45 edge bins fall below but are
statistically consistent at N=20 (per-bin coverage resolution ~10 %).

---

## Closure tests (all CLOSED, 1A lgbm 5-iter, threshold = median \|residual\|)

| Test | Result | Threshold |
|---|---|---|
| Truth-reweight `gauss_pt` (A=0.2) | 0.046 % | 1.5 % |
| Truth-reweight `tilt_pz` (α=0.1) | 0.013 % | 1.5 % |
| Hidden-variable (dpT), A=0.05/0.10/0.30 | 0.57 / 1.14 / 3.43 % | 3.0 % |
| Hidden-variable leakage coefficient (signed/A) | 0.113 (linear in A) | — |
| Alt-model MaCCQE:0 vs `hTruthAltExtrapolated` | 0.068 % | 2.0 % |
| Alt-model Flux:50 vs `hTruthAltExtrapolated` | 0.376 % | 2.0 % |

Hidden-variable axis is `dpT = sim_pT − truth_pT` (resolution variable,
NOT in the OmniFold feature set); reference is unaltered CV truth.
Alt-model target is `CV truth × (alt_in_accept / cv_in_accept)` per
bin — the in-acceptance ratio is what OmniFold can mathematically
recover (full-alt-truth comparison is not the closure target since
out-of-acceptance shift is unrecoverable).

---

## p_||-min sensitivity (paper TotalCov only)

| p_\|\| ≥ (GeV/c) | N bins | χ² | χ²/ndf | median ratio | % < 5 % |
|---|---|---|---|---|---|
| 1.5 | 205 | 750.49 | 3.661 | 1.0064 | 77.6 % |
| 2.0 | 196 | 685.36 | 3.497 | 1.0059 | 80.1 % |
| 2.5 | 186 | 545.87 | 2.935 | 1.0059 | 81.7 % |
| 3.0 | 175 | 474.84 | 2.713 | 1.0059 | 81.1 % |
| 3.5 | 163 | 452.95 | 2.779 | 1.0073 | 80.4 % |
| 4.0 | 151 | 428.72 | 2.839 | 1.0068 | 79.5 % |

Residual is dominated by sub-2 % shape disagreement in the highest p_||
tails.

---

## Paper binning (arXiv:2106.16210)

Authoritative: `minerva_paper_anc/bin_mapping.txt`. TH2D axis labels in
the ancillary ROOT are cosmetic rounding — do not copy into `util/Binning.h`.

```python
pt_edges = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
            0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]         # 14 bins
pz_edges = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
            6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0]  # 16 bins
```

Phase space: θ_μ < 20°, p_T < 4.5 GeV/c, 1.5 < p_|| < 60 GeV/c. Paper
reports 205/224 bins (19 diagonal cells with pt_hi/pz_lo > tan 20°
are unreported).

---

## Active code (`2d-unfolding/`)

- `unfold_2d_omnifold_unbinned.py` — 2D unbinned OmniFold. Backends
  `--estimator {exact,hist,xgb,lgbm}`, `--device {cpu,cuda}`. Flags
  for seedscan (`--seed`), bootstrap (`--bootstrap-seed`), systematic
  universes (`--universe BAND:IDX`), and closures (`--closure-reweight`,
  `--closure-hidden-dpt`, `--closure-alt-universe`). Detailed flag
  contracts in `2D_OMNIFOLD_REFERENCE.md`.
- `compare_to_paper_fullcov.py` — canonical paper-comparison on 205
  reported bins. `--omnifold-cov <ROOT>:<HIST>` (repeatable) block-sums
  OmniFold covs into paper TotalCov; reports paper-only and combined
  χ²/ndf side-by-side. SVD pseudo-inverse for rank-deficient cases.
- `normalize_xsec_shape.py` — shape-mode comparison with paper
  TotalCovariance through unit-area Jacobian.
- `compare_to_paper_interior.py` — legacy 185-bin diagnostic.
- `uq/analyze_uq.py` — bootstrap covariance rollup (np.cov ddof=1,
  Cholesky-with-jitter PD check, projection covs).
- `uq/analyze_universes.py` — universe covariance rollup. Pair bands
  → MINERvA-101 sum-of-squares; multi-universe → sample cov. Total =
  block sum over bands. `--bootstrap-cov` block-sums a bootstrap cov.
- `seedscan/analyze_seedscan.py` — ML-noise covariance rollup.
- `uq/closure/closure_truth_reweight.py`, `closure_hidden_var.py`,
  `closure_alt_model.py` — closure drivers.
- `uq/verify_universe_omnifile.py` — universe-omnifile sanity check
  (branch counts, weight shifts, CV regression).
- `uq/hadd_universes_full.py` — TFileMerger wrapper with
  `TTree::SetMaxTreeSize(300 GB)` (works around the ROOT 100 GB
  auto-rollover that corrupted the original hadd at 94 GB).
- `uq/run_bootstrap_interactive.sh`, `run_universe_array_interactive.sh`,
  `run_flux_ramp_interactive.sh` — interactive sweep drivers.
- `combine_flux_MEHFC.py` — POT-weighted MEHFC flux.
- Plotters: `plot_2d_cross_section.py`, `plot_2d_paper_comparison.py`,
  `plot_2d_paper_comparison_shape.py`, `plot_2d_threeway_fig13.py`,
  `plot_efficiency_fig5_style.py`, `plot_closure_2d.py`.

C++ event loop (`MINERvA101/MINERvA-101-Cross-Section/`):
`runEventLoopOmniFold.cpp` (Phase-18.2 truth gate + bilateral dedupe;
per-reweighter dumps behind `MNV101_DUMP_COMPONENTS`; universe
allowlist via `MNV101_DUMP_UNIVERSES`), `cuts/MaxPtMu.h`,
`util/Binning.h`, `event/CVUniverse.h`.

---

## SLURM scripts (`2d-unfolding/`)

- `sbatch_build.sh`, `sbatch_evloop_array.sh` (1B–1P; 1A separately),
  `sbatch_hadd_MEHFC.sh`, `sbatch_unfold_2d_MEHFC.sh` — CV production.
- `sbatch_unfold_2d_MEHFC_5iter_seedscan.sh` — 10-trial seedscan.
- `sbatch_rebuild_1A_universes.sh`, `sbatch_evloop_array_universes.sh`,
  `sbatch_hadd_MEHFC_universes.sh` — Stage-2 vertical-only universe
  omnifile (110 weight branches).
- `sbatch_unfold_2d_MEHFC_5iter_universes_full.sh`,
  `sbatch_hadd_MEHFC_universes_full_v2.sh` — Stage-2 full
  lateral+vertical sweep (187 universes).
- `sbatch_final_rollup_full.sh` — publication-grade rollup driver.
- `sbatch_runEventLoop_baseline_flux_array.sh` — per-playlist baseline flux.

Interactive-first rule for unfolds (no `srun` inside sbatch). Templates:
`sbatch_unfold_2d_MEHFC.sh` (128 CPU regular QOS),
`sbatch_iter_scan_2d.sh` (shared QOS 2 CPU).

---

## Data inventory

- `runEventLoopOmniFold_{1A..1P}.root` — per-playlist event loops (CV-only).
- `runEventLoopOmniFold_MEHFC.root` (2.0 GB) — 12-playlist hadd, CV-only.
- `runEventLoopOmniFold_1A_universes.root` (5.3 GB) — Stage-1 universe-
  enabled 1A (110 weight branches; bitwise-identical CV columns).
- `runEventLoopOmniFold_MEHFC_universes.root` (63.7 GB) — Stage-2
  vertical-universe MEHFC (110 weight branches × 2 trees).
- `runEventLoopOmniFold_MEHFC_universes_full.root` (119 GB) — Stage-2
  full lateral+vertical MEHFC (4 trees, 187 universes).
- `2d_crossSection_omnifold_MEHFC_5iter.root` — Phase-18.2 CV production.
- `seedscan/...seed{1..10}.root` — ML envelope trials.
- `uq/bootstrap_MEHFC_300/`, `uq/universe_stage2_MEHFC_full/`,
  `uq/seedscan_lgbm_ml/` — final component covariance ROOTs + PNGs.
- `baseline_flux/` — per-playlist + `runEventLoopMC_MEHFC.root` (POT-
  weighted MEHFC flux).
- `minerva_paper_anc/` — arXiv ancillary (TH2D, 4 cov matrices,
  `bin_mapping.txt`, data CSV, model predictions).

Archives: `archive_pre_phase16/` (pre-Phase-16 outputs, σ_tot=0.752×paper);
`archive_pre_phase18/` (Phase-16/17 superseded ROOTs + scripts).

---

## Runtime budget (HistGBT-era)

| Task | Resource | Wall |
|---|---|---|
| C++ event loop, one playlist | shared QOS, 1 task | ~2 h |
| Event loop, all 12 playlists | 11-task array | ~3–4 h |
| 5-iter MEHFC unfold, exact GBT | regular QOS, 128 CPU | ~19 h |
| 5-iter MEHFC unfold, HistGBT | 32 CPU dedicated | 17m33s |
| 5-iter MEHFC unfold, lgbm | 128 CPU | 13m24s |
| Seedscan (10 trials, HistGBT) | sbatch array | ~17 min / task |

One node per HistGBT/lgbm trial. Parallel trials on a shared node are
memory-bandwidth bound (4-wide × 32 ≈ 8× slower, 2-wide × 64 ≈ 4.5×
slower). Above 32 threads on a dedicated node is unmeasured — don't
assume more cores help without benchmarking.
