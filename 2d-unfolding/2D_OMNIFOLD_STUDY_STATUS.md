# 2D OmniFold Study — Status

**Last updated**: 2026-05-28. Phase-18.2 production unfold frozen.
Stage-2 ML seedscan closed. The matched-CV 187-universe covariance
rollup is current and **MAT-conformant** — `uq/analyze_universes.py`
uses the mean-centered biased sample cov uniformly (no special pair
case) and adds the 1.4 % target-nucleon normalization as a rank-1
band, matching MAT/PlotUtils/MnvVertErrorBand::CalcCovMx per
`reference/minerva_systematics_sources.md`. The paper+OmniFold
combined-cov comparison is now χ²/ndf = 1.699 (pull mean/RMS
0.069/0.466) on the matcorr rollup
(`uq/universe_stage2_MEFHC_full_matcorr/`). The previous 1.473
headline used the legacy CV-centered pair_sumsq formula and is
superseded. The available N=300 bootstrap covariance used here was
produced with `--seed N` alongside `--bootstrap-seed N`; a fixed-ML-seed
bootstrap rerun should replace only that statistical block when it is
available. Ours-only inverse-cov χ² remains a regularization diagnostic,
not a standalone headline.

Companion docs: `2D_OMNIFOLD_REFERENCE.md` (workflow invariants),
`2D_OMNIFOLD_RUN_LOG.md` (chronology from 2026-05-18 onward),
`2D_OMNIFOLD_RUN_LOG_ARCHIVE.md` (Phases 1–18.1), `PLOT_GUIDE.md`,
`advisor_memo_cov_rank.md` (collaborator-facing memo on the ours-only
rank-deficiency problem and three open paths).

---

## Goal

Reproduce arXiv:2106.16210 (Ruterbories et al., Phys. Rev. D 106, 032001)
— MINERvA ME FHC d²σ/(dp_T dp_||) CC inclusive — with 2D **unbinned**
OmniFold in place of D'Agostini IBU.

---

## Headline (MEFHC 5-iter lgbm, 205 paper-reported bins)

| Quantity | Value |
|---|---|
| Total xsec | **3.073e-38 cm²/nucleon** |
| σ_total(ours) / σ_total(paper) | **1.0111** |
| Median bin ratio (ours/paper) | 1.0064 |
| Bins within 5 % / 10 % / 20 % of paper | 77.6 % / 94.1 % / 98.5 % |
| Paper-cov-only χ²/ndf | **3.661** |
| Combined-cov χ²/ndf (paper + matcorr universe + boot N=300 + ML) | **1.699** |
| Combined-cov log-normal χ²/ndf (Ruterbories Table I parity) | **1.688** |
| Pull mean / RMS (combined cov) | **0.069 / 0.466** |
| Pull mean / RMS (paper cov only) | 0.089 / 0.598 |
| Shape-only χ²/ndf (205 bins, paper cov, unit-area Jacobian) | 3.596 |
| Global OmniFold completeness c | 1.000000 (exact by construction) |

Paper total: 3.039e-38 cm²/nucleon. The 205-bin set is `xs > 0` in
`data_result_ptpl_2D_minerva_inclusive_6GeV.txt` (19 unreported cells
dropped from both sides).

### Methodology caveat on the combined-cov and ours-only χ²

The combined covariance still double-counts systematics shared with the
paper (flux / GENIE / RPA / 2P2H / MINOS). The ours-only inverse-cov χ²
is also genuinely fragile when the covariance is built from finite
universe ensembles. Under the MAT-conformant formula each pair band is
rank-1 (mean-centering collapses N=2 to a single direction); the full
matcorr `C_universe` is rank 140/205 (65 null directions), driven by
band count rather than universe count.

Current matcorr diagnostic, using
`C_ours = C_universe(matcorr) + C_bootstrap300 + C_ML` on the 205
paper-reported bins (pull mean / RMS = 0.110 / 0.816):

| Diagnostic inverse | rank kept | χ² | χ²/rank | χ²/205 |
|---|---:|---:|---:|---:|
| Full positive-eigenvalue inverse | 205 | 48381.8 | 236.0 | 236.0 |
| Eigenvalue cut `λ/λmax > 1e-5` | 71 | 731.8 | 10.31 | 3.57 |
| Eigenvalue cut `λ/λmax > 1e-4` | 39 | 277.4 | 7.11 | 1.35 |
| Eigenvalue cut `λ/λmax > 1e-3` | 13 | 34.7 | 2.67 | 0.17 |
| Ridge `C + 1e-5 λmax I` | 205 | 1201.7 | — | 5.86 |
| Ridge `C + 1e-4 λmax I` | 205 | 376.7 | — | 1.84 |
| Ridge `C + 1e-3 λmax I` | 205 | 92.4 | — | 0.45 |
| Diagonal-target shrinkage λ=0.005 | 204 | 3652.8 | 17.91 | 17.82 |
| Diagonal-target shrinkage λ=0.01 | 204 | 2410.2 | 11.82 | 11.76 |
| Diagonal-target shrinkage λ=0.02 | 204 | 1575.5 | 7.72 | 7.69 |
| Diagonal-target shrinkage λ=0.05 | 204 | 879.0 | 4.31 | 4.29 |
| Diagonal-target shrinkage λ=0.10 | 204 | 555.1 | 2.72 | 2.71 |
| Diagonal-target shrinkage λ=0.20 | 204 | 346.2 | 1.70 | 1.69 |

The regularized ours-only χ² is not a single robust headline: it moves
from χ²/205 ≈ 5.9 to 0.45 over a two-decade ridge scan and from 17.8
to 1.69 over a two-decade shrinkage scan. The useful conclusion is
diagnostic: the naive inverse is dominated by tiny poorly determined
modes; in the retained high-variance modes the central-value
difference is not large. Quote this table and direct per-bin pulls
rather than a single unqualified ours-only χ².

Clean ours-only χ² would need either (a) substantially more universes
to fill the 205-dim space, (b) analytical band cov prescriptions per
systematic (PPFX / MaCCQE / RPA / 2P2H / lateral) replacing the sampled
sum-of-rank-1, or (c) PPFX effective-rank reduction. (a/b/c) are the
three open paths flagged for collaborator input — see
`advisor_memo_cov_rank.md`.

### Matcorr rollup verified byte-for-byte against MAT (2026-05-28)

`uq/verify_matcorr_vs_mnvh1d.py` populates a `PlotUtils::MnvH1D` with
the same per-universe X_u vectors our Python rollup consumes (44
bands, 188 universes, 205 reported bins), then compares
`MnvH1D::GetTotalErrorMatrix(false,false,false)` against the
`--add-norm 0` Python rollup at
`uq/universe_stage2_MEFHC_full_matcorr_nonorm/`. Result: max
element-wise relative diff = **5.5e-17** (machine ε for double), Frobenius
diff = 2.7e-94 vs Frobenius norm 4.8e-78 of either matrix. sqrt(trace)
matches to all seven printed digits (2.391038e-39 = 2.391038e-39). The
1.4 % normalization rank-1 we add on top via `--add-norm 0.014` is
outside MAT's `MnvVertErrorBand` machinery and is the only piece not
covered by this check. Report in `uq/matcorr_vs_mnvh1d.txt`.

### Bootstrap/paper-stat double-count (2026-05-28)

`compare_to_paper_fullcov.py` now exposes `--subtract-stat`, which
replaces the paper baseline by `TotalCov − StatOnlyCov` before adding
OmniFold covariances, so our C_boot is not double-counted against the
paper's stat block. On the matcorr rollup that flag drives χ²/ndf
1.699 → **23.96** (log-normal: 1.688 → **24.38**). The headline still
quotes the double-counted 1.699 because (i) it is the well-defined
"what does OmniFold UQ add on top of the published V" statement, and
(ii) the OmniFold C_boot is much smaller than the IBU stat block the
paper publishes (`√tr(C_boot) = 1.83e-40` vs ~2.7e-39 for paper
TotalCov, so subtracting paper-stat without a comparable replacement
overcorrects). Keep the de-double-counted number on file as a
secondary diagnostic.

---

## Phase 18.2 pipeline (frozen 2026-05-18)

- **Truth-tree-authoritative reco gate.** `mc_signal_reco` filled only
  when `(mc_run, mc_subrun, mc_nthEvtInFile)` is in `mc_truth_denom`.
  Truth-only events appended as native OmniFold miss entries.
- **By-construction completeness c = 1.000000** (32,849,103 entries each
  at MEFHC). The Phase-16 c-division is a no-op self-check.
- **Bilateral dedupe** on the packed `uint64_t` event ID. 133 truth + 7
  reco duplicates skipped (all from one playlist file).
- **Production output**: `2d_crossSection_omnifold_MEFHC_5iter.root` —
  5-iter unfold of `runEventLoopOmniFold_MEFHC.root`, exact GBT.

History of the residual chase (σ/paper = 0.752 → 1.011, χ²/ndf 17 →
3.66): see `2D_OMNIFOLD_RUN_LOG_ARCHIVE.md`.

Iteration convergence (1A iter-scan, archived): 5-iter total σ within
0.026 % of 10-iter, per-bin shape RMS 1.54 %. HistGBT/exact-GBT agree
on total σ to 0.04 % at 10 iters; 5-iter MEFHC identical to 4 sig figs.

---

## Stage-2 UQ envelope

Per-bin spreads over 205 paper-reported bins. The matched-CV universe
row is current. The bootstrap row is the available N=300 covariance
used in the present combined χ²; it varied `--seed N` with
`--bootstrap-seed N`, so it includes a tiny ML-stochastic contribution
that is also measured separately in the ML row. A fixed-ML-seed
bootstrap rerun should replace the statistical block when available.

| Component | N | √tr(C) | Per-bin median rel σ |
|---|---|---|---|
| ML noise (lgbm seedscan) | 10 | 5.061e-41 | 0.166 % |
| Statistical (Poisson bootstrap, seed-varying) | 300 | 1.828e-40 | 0.564 % |
| Systematic (matcorr universe sweep + 1.4% norm rank-1) | 187+1 | 2.463e-39 | 4.783 % |
| **Combined (block sum)** | — | 2.518e-39 | 5.376 % |
| Paper TotalCov (for reference) | — | 2.676e-39 | 6.86 % |

Block sum assumes independence (different RNGs / different physics
sources). The bootstrap seed-varying caveat is numerically small
relative to the universe block, but should be corrected before treating
the statistical covariance as purely Poisson.

**Current top systematic bands** (median rel σ, 205 bins, matched-CV
rollup): Muon_Energy_MINOS 2.571 %, Muon_Energy_MINERvA 1.733 %,
MinosEfficiency 1.502 %, MaRES 0.912 %, MvRES 0.615 %, MaCCQE 0.538 %.
44 bands total — 6 lateral
(BeamAngleX/Y, MuonResolution, GEANT_{Neutron,Pion,Proton},
Muon_Energy_MINERvA) + 38 vertical. Lateral bands re-run the event
loop with shifted detector quantities; vertical bands re-weight only.

**Methods.**
- *Stat*: per-event Poisson(1) on data and MC (independent sub-RNGs;
  same draw on MC truth/reco). The current table uses the available
  N=300 covariance whose replicas varied both `--bootstrap-seed N` and
  `--seed N`; current drivers are patched to pass fixed `--seed 1` with
  `--bootstrap-seed N` varying for the next pure-Poisson replacement.
- *Syst*: MAT-conformant uniform formula
  `C_band = (1/N)·Σ_u (Xᵤ − ⟨X⟩_u)(Xᵤ − ⟨X⟩_u)ᵀ` applied uniformly
  to N ≥ 2 (matches `MAT/PlotUtils/MnvVertErrorBand::CalcCovMx`;
  no special pair case). 1.4 % target-nucleon normalization added
  as a rank-1 outer product `(σ·cv)(σ·cv)ᵀ` at rollup time.
  Bands summed independently (no cross-band block; the Bashyal
  flux↔Muon_Energy_MINOS joint correlation is a documented gap —
  see `advisor_memo_cov_rank.md` ask A). The pre-2026-05-28
  rollup used a CV-centered `½(Δ₊Δ₊ᵀ + Δ₋Δ₋ᵀ)` pair formula that
  agreed with MAT only for symmetric shifts; the matcorr build
  drops total universe trace by 1.9 % vs that legacy
  (BeamAngle/MuonResolution/NC pair bands had asymmetric shifts
  that legacy treated as rank-2 contributions and MAT correctly
  collapses to near-zero variance). Legacy build is still
  reachable via `--legacy-pair-formula` for forensic reproduction.
- *ML*: 10-trial lgbm seedscan, `random_state` pinned via
  `--seed N` (step1=N, step2=N+1, regressor=N+2).

**Current rollup path**:
`sbatch_unfold_2d_MEFHC_5iter_universes_full_CV.sh` produced the matched
full-CV ROOT, then `sbatch_final_rollup_full.sh` produced the legacy
(superseded) `uq/universe_stage2_MEFHC_full/uq_universe_covariance_full.root`.
The current MAT-conformant rollup is regenerated by re-running
`uq/analyze_universes.py` with `--add-norm 0.014` against the same
universe ROOTs, output to
`uq/universe_stage2_MEFHC_full_matcorr/uq_universe_covariance_full_matcorr.root`.
Bootstrap and ML component covariances:
`uq/bootstrap_MEFHC_300/uq_covariance_boot300.root`,
`uq/seedscan_lgbm_ml/uq_covariance_ml.root`.

---

## Calibration: coverage toys (200 closure+bootstrap-seed MEFHC toys)

| Metric | Measured | Theoretical (Gaussian 1σ) |
|---|---|---|
| Mean coverage | 68.71 % | 68.27 % |
| Median coverage | 68.50 % | — |
| ⟨\|residual\|/σ⟩ | 0.794 | √(2/π) = 0.798 |
| Signed residual mean | +0.006 ± 0.082 σ | 0 |

97.56 % of 205 bins meet the 65 % target; only 5 bins fall below.

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
- `uq/analyze_universes.py` — universe covariance rollup.
  MAT-conformant uniform formula
  `C = (1/N)·Σ_u (Xᵤ−⟨X⟩_u)(Xᵤ−⟨X⟩_u)ᵀ` applied to all N ≥ 2.
  `--add-norm SIGMA` adds a flat fully-correlated rank-1 band
  `(SIGMA·cv)(SIGMA·cv)ᵀ` (pass 0.014 for the 1.4 %
  target-nucleon normalization, Aliaga NIM 1305.5199).
  `--legacy-pair-formula` reverts N=2 bands to the pre-2026-05-28
  CV-centered pair_sumsq for forensic reproduction only.
  `--bootstrap-cov` block-sums a bootstrap cov. `--shrinkage λ`
  applies diagonal-target Ledoit-Wolf regularization to the total
  cov for ours-only χ² use (diagonal preserved exactly).
- `uq/_ours_only_chi2.py` — diagnostic for ours-only χ²/ndf via direct
  inverse on the 205 reported bins, with optional `--bootstrap-cov`
  block-sum. Handles paper TH2D axis swap (paper has x=p∥, y=p_T;
  ours has x=p_T, y=p∥).
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
- `combine_flux_MEFHC.py` — POT-weighted MEFHC flux.
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
  `sbatch_hadd_MEFHC.sh`, `sbatch_unfold_2d_MEFHC.sh` — CV production.
- `sbatch_unfold_2d_MEFHC_5iter_seedscan.sh` — 10-trial seedscan.
- `sbatch_rebuild_1A_universes.sh`, `sbatch_evloop_array_universes.sh`,
  `sbatch_hadd_MEFHC_universes.sh` — Stage-2 vertical-only universe
  omnifile (110 weight branches).
- `sbatch_unfold_2d_MEFHC_5iter_universes_full.sh`,
  `sbatch_unfold_2d_MEFHC_5iter_universes_full_CV.sh`,
  `sbatch_hadd_MEFHC_universes_full_v2.sh` — Stage-2 full
  lateral+vertical sweep (187 universes) plus matched lgbm CV.
- `sbatch_final_rollup_full.sh` — publication-grade rollup driver.
- `sbatch_runEventLoop_baseline_flux_array.sh` — per-playlist baseline flux.

Interactive-first rule for unfolds (no `srun` inside sbatch). Templates:
`sbatch_unfold_2d_MEFHC.sh` (128 CPU regular QOS),
`sbatch_iter_scan_2d.sh` (shared QOS 2 CPU).

---

## Data inventory

- `runEventLoopOmniFold_{1A..1P}.root` — per-playlist event loops (CV-only).
- `runEventLoopOmniFold_MEFHC.root` (2.0 GB) — 12-playlist hadd, CV-only.
- `runEventLoopOmniFold_1A_universes.root` (5.3 GB) — Stage-1 universe-
  enabled 1A (110 weight branches; bitwise-identical CV columns).
- `runEventLoopOmniFold_MEFHC_universes.root` (63.7 GB) — Stage-2
  vertical-universe MEFHC (110 weight branches × 2 trees).
- `runEventLoopOmniFold_MEFHC_universes_full.root` (119 GB) — Stage-2
  full lateral+vertical MEFHC (4 trees, 187 universes).
- `2d_crossSection_omnifold_MEFHC_5iter.root` — Phase-18.2 CV production.
- `seedscan/...seed{1..10}.root` — ML envelope trials.
- `uq/bootstrap_MEFHC_300/`, `uq/universe_stage2_MEFHC_full/`,
  `uq/seedscan_lgbm_ml/` — final component covariance ROOTs + PNGs.
- `baseline_flux/` — per-playlist + `runEventLoopMC_MEFHC.root` (POT-
  weighted MEFHC flux).
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
| 5-iter MEFHC unfold, exact GBT | regular QOS, 128 CPU | ~19 h |
| 5-iter MEFHC unfold, HistGBT | 32 CPU dedicated | 17m33s |
| 5-iter MEFHC unfold, lgbm | 128 CPU | 13m24s |
| Seedscan (10 trials, HistGBT) | sbatch array | ~17 min / task |

One node per HistGBT/lgbm trial. Parallel trials on a shared node are
memory-bandwidth bound (4-wide × 32 ≈ 8× slower, 2-wide × 64 ≈ 4.5×
slower). Above 32 threads on a dedicated node is unmeasured — don't
assume more cores help without benchmarking.
