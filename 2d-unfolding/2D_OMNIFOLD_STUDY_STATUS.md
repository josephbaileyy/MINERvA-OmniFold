# 2D OmniFold Study — Status

**Last updated**: 2026-05-29. Phase-18.2 production unfold frozen; ML
seedscan closed. Canonical uncertainty = matched-CV 187-universe
**MAT-conformant + flux-fixed** covariance
(`uq/universe_stage2_MEFHC_full_matcorr_fluxfix/`), built by
`uq/analyze_universes.py` (mean-centered biased sample cov, no special
pair case, + 1.4 % target-nucleon normalization rank-1; matches
`MnvVertErrorBand::CalcCovMx`) with the per-universe 1/Φ flux
normalization applied (Task #70, 2026-05-29). Our **standalone** combined
budget is now **6.87 % median rel σ ≈ paper total 6.86 %**. Paper+OmniFold
combined-cov χ²/ndf = **1.481** — but that comparison now *double-counts*
flux (we add our ~5 % flux on top of the paper's; see χ² caveats). The
pre-fluxfix matcorr rollup (combined χ²/ndf 1.703, flux band 1 %) and the
legacy CV-centered pair_sumsq rollup (1.473) are superseded.

Companion docs: `2D_OMNIFOLD_REFERENCE.md` (workflow invariants + flag
contracts), `2D_OMNIFOLD_RUN_LOG.md` (current chronology),
`2D_OMNIFOLD_RUN_LOG_ARCHIVE.md` (Phases 1–18.1 + the 2026-05-18→28 UQ
campaign), `PLOT_GUIDE.md`, `docs/uq_statistical_methods.tex` (full UQ
methods writeup: procedures, MINERvA covariance construction, and the
ours-only rank-deficiency + open questions for collaborators).

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
| Combined-cov χ²/ndf (paper + fluxfix universe + boot N=300 + ML) | **1.481** |
| Combined-cov log-normal χ²/ndf (Ruterbories Table I parity) | **1.468** |
| Standalone ours-only combined median rel σ (≈ paper total 6.86 %) | **6.87 %** |
| Pull mean / RMS (combined cov) | **0.051 / 0.409** |
| Pull mean / RMS (paper cov only) | 0.089 / 0.598 |
| Shape-only χ²/ndf (205 bins, paper cov, unit-area Jacobian) | 3.596 |
| Global OmniFold completeness c | 1.000000 (exact by construction) |

Paper total: 3.039e-38 cm²/nucleon. The 205-bin set is `xs > 0` in
`data_result_ptpl_2D_minerva_inclusive_6GeV.txt` (19 unreported cells
dropped from both sides).

**χ² caveats.** (i) The combined cov double-counts systematics shared
with the paper (flux / GENIE / RPA / 2P2H / MINOS), and the flux fix
(Task #70) makes the **flux** double-count larger — we now add our ~5 %
flux on top of the paper's 4 %, which is the main driver of the
1.703→1.481 drop. So 1.481 is a paper+ours number that is *not* the
beneficiary of the flux fix; the flux fix's real win is the standalone
budget (6.87 % ≈ paper 6.86 %). `compare_to_paper_fullcov.py
--subtract-stat` removes only the bootstrap/paper-stat overlap (not the
flux overlap) → overcorrects there; treat it as a secondary diagnostic.
(ii) Ours-only inverse-cov χ² is ill-conditioned — fluxfix
`C_universe` is rank 140/205 (65 null directions, band-count-driven), and
the regularized χ² moves ~2 decades over ridge/shrinkage scans. Quote
per-bin pulls, not a single ours-only χ². Full regularization scan +
discussion: `docs/uq_statistical_methods.tex` (§Ill-conditioning) and
RUN_LOG 2026-05-28 sections.
The matcorr rollup is verified byte-for-byte against MAT `MnvH1D`
(`GetTotalErrorMatrix`): max element-wise rel diff **5.5e-17** (machine ε),
sqrt(trace) matches to 7 digits — report in `uq/matcorr_vs_mnvh1d.txt`.

---

## Stage-2 UQ envelope (205 paper-reported bins)

| Component | N | √tr(C) | Per-bin median rel σ |
|---|---|---|---|
| ML noise (lgbm seedscan) | 10 | 5.061e-41 | 0.166 % |
| Statistical (Poisson bootstrap, pinned ML seed) | 300 | 1.817e-40 | 0.549 % |
| Systematic (fluxfix universe sweep + 1.4% norm rank-1) | 187+1 | 3.214e-39 | 6.830 % |
| **Combined (block sum)** | — | 3.220e-39 | 6.865 % |
| Paper TotalCov (for reference) | — | 2.676e-39 | 6.86 % |

Block sum assumes independence (different RNGs / physics sources). The
flux fix (Task #70) brings our standalone combined budget (6.865 %) into
agreement with the paper total (6.86 %). Top systematic bands (median rel
σ, fluxfix rollup): Flux 4.99 %, Muon_Energy_MINOS 2.31 %,
Muon_Energy_MINERvA 1.29 %, MinosEfficiency 1.47 %,
MaRES 0.55 %, MvRES 0.38 %, MaCCQE 0.36 %. 44 bands (6 lateral: BeamAngleX/Y,
MuonResolution, GEANT_{Neutron,Pion,Proton}, Muon_Energy_MINERvA;
38 vertical). **Bootstrap status (2026-05-29)**: the N=300 cov is now the
pure-Poisson replacement — all 300 replicas pin `--seed 1` and vary only
`--bootstrap-seed` (sbatch 53489662, complete). It supersedes the earlier
seed-varying set that leaked ML stochasticity into the stat block. The
swap moved the headline only 1.699→1.703 (√tr(C_boot) 1.828e-40→1.817e-40),
confirming the prior contamination was numerically negligible.

**Flux 1/Φ normalization — FIXED (Task #70, 2026-05-29).** Previously our
`Flux` band was ~1 % (no floor) vs the paper's ~4 % (floor 3.90 %): the
cross section divided by a fixed CV flux integral Φ in *every* universe
(`--universe` swaps event weights but not `flux_bins`,
`unfold_2d_omnifold_unbinned.py:1090,1500`), so the dominant σ ∝ 1/Φ
normalization was never varied. Fixed analytically (the 100 per-universe
flux integrals were already on disk in the per-playlist flux MnvH1Ds):
`uq/build_flux_universe_band.py` POT-combines them, `uq/rescale_flux_universes.py`
multiplies each Flux-universe cross section by Φ_CV(pT)/Φ_u(pT) — exact,
no re-unfold. Flux band 1.01 %→**4.99 %** (flat, floor 4.78 %); standalone
combined budget 4.82 %→**6.87 % ≈ paper 6.86 %**. PPFX index alignment
verified (Pearson 0.96). The driver now applies this natively —
`--universe Flux:IDX` divides by `hFluxUniv[:,IDX]` via
`--flux-universe-file` (no more post-hoc rescale for future runs).
**Normalization is not a gap**: the paper states (Ruterbories §VII) the
normalization uncertainty *is* 1.4 % (target nucleons) — exactly our
rank-1; the ~2 % read off Fig 6/7 was eyeball imprecision. One residual:
ours ~5 % vs paper ~4 % flux (both ν-e-constrained) is a PPFX-version /
flux-weighting difference, not resolvable from disk (we store only the
integrated Φ) — collaborator question for the #65 flux cluster. See
RUN_LOG 2026-05-29.

Canonical covariance ROOTs:
- systematic (flux-fixed): `uq/universe_stage2_MEFHC_full_matcorr_fluxfix/uq_universe_covariance_full_matcorr_fluxfix.root`
- bootstrap: `uq/bootstrap_MEFHC_300/uq_covariance_boot300.root`
- ML: `uq/seedscan_lgbm_ml/uq_covariance_ml.root`

MAT-conformant formula, the 1.4 % norm rank-1, the legacy pair-formula
escape hatch, and the full rollup path are documented in
`2D_OMNIFOLD_REFERENCE.md`.

---

## Validation (all closed)

- **Closure** (1A lgbm 5-iter, thr = median |residual|): truth-reweight
  gauss_pt 0.046 %, tilt_pz 0.013 % (thr 1.5 %); hidden-var dpT
  A=0.05/0.10/0.30 → 0.57/1.14/3.43 % (thr 3.0 %, leakage linear in A);
  alt-model MaCCQE:0 0.068 %, Flux:50 0.376 % (thr 2.0 %). Hidden-var
  axis `dpT = sim_pT − truth_pT` is a resolution variable (not in the
  feature set); alt-model target is `CV truth × (alt/cv in-acceptance)`.
- **Coverage** (200 closure+bootstrap-seed MEFHC toys): mean 68.71 % vs
  Gaussian 68.27 %; median 68.50 %; ⟨|res|/σ⟩ 0.794 vs √(2/π)=0.798;
  signed mean +0.006 ± 0.082 σ. 97.6 % of 205 bins meet the 65 % target.
- **Completeness** c = 1.000000 exact by construction.
- **Iteration**: 5-iter total σ within 0.026 % of 10-iter (per-bin shape
  RMS 1.54 %); HistGBT/exact-GBT agree on total σ to 0.04 %.

**p_||-min sensitivity** (paper TotalCov only): χ²/ndf 3.66 (205 bins,
p∥≥1.5) → 3.50 / 2.94 / 2.71 / 2.78 / 2.84 at p∥≥2.0/2.5/3.0/3.5/4.0
(196/186/175/163/151 bins); median ratio ≈1.006 throughout. Residual is
dominated by sub-2 % shape disagreement in the highest-p∥ tails.

---

## Phase 18.2 pipeline (frozen 2026-05-18)

- **Truth-tree-authoritative reco gate**: `mc_signal_reco` filled only
  when `(mc_run, mc_subrun, mc_nthEvtInFile)` ∈ `mc_truth_denom`;
  truth-only events appended as native OmniFold miss entries.
- **Bilateral dedupe** on the packed uint64 event ID (133 truth + 7 reco
  duplicates, all from one playlist file).
- **Completeness** c = 1.000000 (32,849,103 entries each at MEFHC); the
  Phase-16 c-division is now a no-op self-check.
- **Production**: `2d_crossSection_omnifold_MEFHC_5iter.root`, exact GBT.

Residual chase (σ/paper 0.752→1.011, χ²/ndf 17→3.66): `RUN_LOG_ARCHIVE`.

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
reports 205/224 bins (19 diagonal cells with pt_hi/pz_lo > tan 20° are
unreported).

---

## Active code (`2d-unfolding/`)

- `unfold_2d_omnifold_unbinned.py` — 2D unbinned OmniFold. Backends
  `--estimator {exact,hist,xgb,lgbm}`, `--device {cpu,cuda}`. Flags for
  seedscan (`--seed`), bootstrap (`--bootstrap-seed`), systematic
  universes (`--universe BAND:IDX`), and closures (`--closure-reweight`,
  `--closure-hidden-dpt`, `--closure-alt-universe`). Flag contracts in
  `2D_OMNIFOLD_REFERENCE.md`.
- `compare_to_paper_fullcov.py` — canonical paper comparison on 205
  reported bins. `--omnifold-cov <ROOT>:<HIST>` (repeatable) block-sums
  OmniFold covs into paper TotalCov; `--subtract-stat` removes the
  paper-stat overlap. Paper-only vs combined χ²/ndf side-by-side; SVD
  pseudo-inverse for rank-deficient cases.
- `normalize_xsec_shape.py` — shape-mode comparison (unit-area Jacobian).
- `compare_to_paper_interior.py` — legacy 185-bin diagnostic.
- `uq/analyze_universes.py` — universe covariance rollup (MAT-conformant;
  `--add-norm SIGMA` rank-1 norm band, `--bootstrap-cov` block-sum,
  `--shrinkage λ` diagonal-target regularization, `--legacy-pair-formula`
  for forensic reproduction).
- `uq/analyze_uq.py` — bootstrap covariance rollup (np.cov ddof=1,
  Cholesky-with-jitter PD check, projection covs).
- `uq/_ours_only_chi2.py` — ours-only χ²/ndf diagnostic (direct inverse,
  handles the paper TH2D axis swap).
- `seedscan/analyze_seedscan.py` — ML-noise covariance rollup.
- `uq/closure/{closure_truth_reweight,closure_hidden_var,closure_alt_model}.py`
  — closure drivers.
- `uq/verify_universe_omnifile.py`, `uq/verify_matcorr_vs_mnvh1d.py` —
  universe-omnifile and MAT-parity sanity checks.
- `uq/hadd_universes_full.py` — TFileMerger wrapper with
  `TTree::SetMaxTreeSize(300 GB)` (ROOT 100 GB auto-rollover workaround).
- `uq/{run_bootstrap,run_universe_array,run_flux_ramp}_interactive.sh`,
  `uq/plot_uncertainty_fig6_7_style.py` — sweep drivers + Fig-6/7 plots.
- `combine_flux_MEFHC.py` — POT-weighted MEFHC flux.
- Plotters: `plot_2d_cross_section.py`, `plot_2d_paper_comparison.py`,
  `plot_2d_paper_comparison_shape.py`, `plot_2d_threeway_fig13.py`,
  `plot_efficiency_fig5_style.py`, `plot_closure_2d.py`.

C++ event loop (`MINERvA101/MINERvA-101-Cross-Section/`):
`runEventLoopOmniFold.cpp` (Phase-18.2 truth gate + bilateral dedupe;
per-reweighter dumps behind `MNV101_DUMP_COMPONENTS`; universe allowlist
via `MNV101_DUMP_UNIVERSES`), `cuts/MaxPtMu.h`, `util/Binning.h`,
`event/CVUniverse.h`.

---

## SLURM scripts (`2d-unfolding/`)

- CV production: `sbatch_build.sh`, `sbatch_evloop_array.sh` (1B–1P; 1A
  separately), `sbatch_hadd_MEFHC.sh`, `sbatch_unfold_2d_MEFHC.sh`.
- Seedscan: `sbatch_unfold_2d_MEFHC_5iter_seedscan.sh` (10 trials).
- Stage-2 universe omnifiles: `sbatch_rebuild_1A_universes.sh`,
  `sbatch_evloop_array_universes{,_full}.sh`,
  `sbatch_hadd_MEFHC_universes{,_full_v2}.sh`.
- Stage-2 full sweep + matched CV:
  `sbatch_unfold_2d_MEFHC_5iter_universes_full{,_CV}.sh`,
  `sbatch_final_rollup_full.sh`.
- Baseline flux: `sbatch_runEventLoop_baseline_flux_array.sh`.

Interactive-first rule for unfolds (no `srun` inside sbatch) — see
`2D_OMNIFOLD_REFERENCE.md` / `AGENTS.md`.

---

## Data inventory

- `runEventLoopOmniFold_{1A..1P}.root` — per-playlist event loops (CV-only).
- `runEventLoopOmniFold_MEFHC.root` (2.0 GB) — 12-playlist hadd, CV-only.
- `runEventLoopOmniFold_1A_universes.root` (5.3 GB) — Stage-1 universe 1A.
- `runEventLoopOmniFold_MEFHC_universes.root` (63.7 GB) — Stage-2
  vertical-universe MEFHC (110 weight branches × 2 trees).
- `runEventLoopOmniFold_MEFHC_universes_full.root` (119 GB) — Stage-2
  full lateral+vertical MEFHC (4 trees, 187 universes).
- `2d_crossSection_omnifold_MEFHC_5iter.root` — Phase-18.2 CV production.
- `seedscan/...seed{1..10}.root` — ML envelope trials.
- `uq/{bootstrap_MEFHC_300,universe_stage2_MEFHC_full_matcorr,seedscan_lgbm_ml}/`
  — canonical component covariance ROOTs + PNGs.
- `baseline_flux/` — per-playlist + `runEventLoopMC_MEFHC.root`.
- `minerva_paper_anc/` — arXiv ancillary (TH2D, 4 cov matrices,
  `bin_mapping.txt`, data CSV, model predictions).

Archives: `archive_pre_phase16/` (σ_tot=0.752×paper);
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
memory-bandwidth bound (4-wide × 32 ≈ 8× slower). Above 32 threads on a
dedicated node is unmeasured — benchmark before assuming more cores help.
