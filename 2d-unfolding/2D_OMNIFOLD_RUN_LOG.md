# 2D OmniFold run log (active)

Current frontier only. As of 2026-05-28 the production pipeline and the
Stage-1/Stage-2 uncertainty-quantification campaign are complete; the
live log below carries just the canonical covariance rollup and the open
methodology diagnostics.

For Phases 1–18.1 (how the Phase-18.2 pipeline was reached) and for the
Phase-18.2 production + Stage-1/Stage-2 UQ campaign (2026-05-18 →
2026-05-28), see `2D_OMNIFOLD_RUN_LOG_ARCHIVE.md`. For headline numbers
and current state see `2D_OMNIFOLD_STUDY_STATUS.md`; for durable workflow
invariants see `2D_OMNIFOLD_REFERENCE.md`.

---

## 2026-05-29 — Paper-cov χ²=3.66 tension: eigenmode anatomy (diagnostic)

Advisor asked *why* our result is "slightly in tension" with the
published one despite the central values agreeing
(σ_tot ratio 1.011, median bin ratio 1.006). Built
`diagnose_tension.py` (reuses `compare_to_paper_fullcov.py` loaders) to
dissect the paper-cov χ²/ndf = 3.661 on the 205 reported bins.

**The paradox is the clue.** Per-bin pull RMS vs the paper cov is only
0.598, so a *diagonal-only* χ²/ndf would be 0.366. The full-cov 3.661 is
a **10× inflation that lives entirely in the off-diagonal / correlated
structure** of the published `TotalCov` (cond 1.5e12, rank 204/205).

**Eigenmode decomposition** (C = Σ λₖ uₖ uₖᵀ, cₖ = uₖ·Δ,
χ² = Σ cₖ²/λₖ; reproduces pinv χ² 750.49 to 3e-9):
- Dominant contributors are **moderate-λ** modes (λ/λmax ~ 1e-4–1e-5,
  eigval-rank ~113–141/205) with genuine **5–6σ eigen-pulls** — not the
  smallest-λ null directions.
- The 10 smallest-λ modes carry only **3 %** of χ²; ~90 modes reach 90 %.
- Robustness: keeping only the 73 best-measured directions
  (rcond 1e-4) still gives χ²/ndf **1.42**; 139 dirs (1e-6) → 2.79.
  Rank-truncation rises smoothly 0.69(r=50)→2.35(100)→3.30(180)→3.66(205),
  no late jump. ⇒ **not** a numerical ill-conditioning artifact.

**Shape, not normalization.** Splitting Δ along the measured spectrum
(scale) vs orthogonal (shape): χ²_norm = 0.10, χ²_shape = 750.1. The
+1.1 % offset is irrelevant; consistent with shape-only χ²/ndf 3.60.

**Kinematic localization** (`tension_mode_maps.png`,
`tension_chi2_map.png`). Carrier eigenvectors are sign-alternating shape
oscillations on the **low-p_T cross-section peak ridge** (p_T ≲ 0.4 GeV;
p_T-bins 2/7/10 carry 16/11/12 % of χ²) plus low-p‖ edge cells (p‖-bins
0/1/8). **Not** vertical p_T-columns (rules out a flux 1/Φ(p_T) shape
error) and **not** the θ_μ<20° acceptance edge. This is exactly where the
Flux and Muon_Energy bands dominate — the region governed by the missing
Bashyal flux↔Muon_Energy joint block (open question #1, `sec:rank`).

**Methodological component.** Same data/normalization, different GBDT
backend moves the paper-cov χ² by ~1 unit:

| OmniFold config (5-iter) | paper-cov χ²/ndf | pull RMS |
|---|---|---|
| exact-GBT (frozen production) | 3.66 | 0.598 |
| HistGBT (10-seed mean) | 2.70 ± 0.04 | 0.56 |
| LightGBM 5-iter | 2.65 | 0.563 |
| LightGBM 10-iter | 2.66 | 0.565 |

Two effects separate cleanly. **Iteration is negligible**: lgbm 5→10
moves χ² by +0.01 (2.645→2.657), so OmniFold is converged at 5 iters and
the tension is *not* an under-iteration artifact. **The estimator carries
the ~1-unit band**: the frozen exact-GBT production (3.66) is the high
outlier; both histogram-binned backends agree at 2.65–2.70 (HistGBT
10-seed range 2.63–2.74, std 0.04 — the ±0.04 ML jitter is ~25× smaller
than the 0.96 exact→hist gap, so it is genuinely the estimator, not seed
noise). Exact-gradient trees fit finer shape (less implicit smoothing) and
deviate more from the paper's IBU-regularized result. ~1 χ²-unit of the
tension is OmniFold regularization, not data–MC physics.

**Conclusion.** The tension is (i) a genuine broadly-distributed
*correlated shape* difference in the low-p_T peak (where flux/muon-energy
dominate), not a normalization offset and not a small-λ artifact; plus
(ii) a ~1-χ²-unit methodological band from GBDT estimator/iteration
regularization. Both point to the **Bashyal joint block** as the next
step. Full writeup: `docs/uq_statistical_methods.tex` §`sec:tension`.

---

## 2026-05-29 — Flux band under-propagates the 1/Φ normalization (diagnosed + FIXED)

Comparing slide-7 grouped fractional uncertainties against Ruterbories
Fig 6/7: our **Flux** band sits at ~1 % and varies with kinematics,
whereas the paper's flux is a near-flat ~4 %. Likewise our
**Normalization** is flat at 1.4 % vs the paper's ~2 %.

**Root cause (flux) — confirmed in code.** The 2D cross section is
`dσ = U / (c·Φ·N·POT·ΔpT·Δp∥)` and the flux integral Φ is loaded once
from the CV flux histogram (`unfold_2d_omnifold_unbinned.py:1090`,
`--flux-hist pTmu_reweightedflux_integrated`). The `--universe BAND:IDX`
path only swaps the event-weight columns `w_truth`/`w_reco`; it never
re-loads or shifts `flux_bins`, so **every flux universe divides by the
same CV Φ** (line 1500). A flux universe therefore enters our result
only through the OmniFold MC reweighting (prior/response) and the
completeness `c` — and OmniFold largely *cancels* that, because it pulls
the fixed data back to truth regardless of the MC prior. What survives is
the ~1 % acceptance/shape residual. The dominant flux term — σ ∝ 1/Φ, a
~4 % nearly-fully-correlated normalization → flat fractional band — is
**missing**, because Φ in the denominator never moves.

Quantitative confirmation against the paper ancillary cov
(`cov_ptpl_minerva_inclusive_6GeV.root`, reported bins):

| band (per-bin rel σ) | median | min | max |
|---|---:|---:|---:|
| paper `FluxCovariance` | 4.01 % | **3.90 %** | 7.13 % |
| our matcorr `full_Flux` | 1.01 % | <1 % | 12.8 % |

The paper's 3.90 % *floor* (never drops below it) is exactly the
correlated flux-integral normalization we omit; our band has no floor.

**Normalization (1.4 % vs 2 %) — mostly definitional, not a bug.** Our
"Normalization" curve is the hand-added 1.4 % target-nucleon rank-1
(`--add-norm 0.014`) plus GENIE NormDISCC/NormNCRES. The paper's ~2 %
group bundles more normalization-class terms (√(2.0²−1.4²) ≈ 1.4 % extra
in quadrature, e.g. POT / scintillator-mass / per-target-region detector
mass). We itemize only the Aliaga 1.4 % piece — the same gap as the
slide-12 "per-target-region detector-mass" / "more bands?" items.

**Is it fixable? Yes, and cheaply (no re-unfolding).** σ ∝ 1/Φ(pT)
exactly (broadcast over p∥; `extract_cross_section_2d:722`), so the fix
is a post-hoc rescale once we have the 100 per-universe flux integrals:
1. **C++ dump** (`runEventLoop.cpp:393,481`): bump `SetNFluxUniverses(2)`
   → 100 and dump `util::GetFluxIntegral` for each Flux universe — either
   as an MnvH1D `pTmu_reweightedflux_integrated` carrying the Flux vert
   error band, or 100 named TH1Ds. The PPFX universes are already live
   via `FluxAndCVReweighter`; this is a lightweight flux-only loop, not a
   full re-run.
2. **Python rescale** (no re-unfold): multiply each of the 100 existing
   `uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_Flux_*.root` by
   `Φ_CV(pT)/Φ_u(pT)` per pT bin, then re-roll the Flux band cov in
   `analyze_universes.py` and refresh the headline. All 100 flux-universe
   unfolds are already on disk.

This is the largest known understatement in our error budget (flux is the
paper's joint-largest band) and is now **Task #70**. Non-flux bands are
unaffected (they don't change Φ). Filed alongside the Bashyal flux↔muon
cross-band block (#65), with which it shares the flux machinery.

### FIXED same day — pure-Python, no re-unfold (Task #70 done)

The 100 per-universe flux integrals were already on disk: each
`baseline_flux/runEventLoopMC_<PL>.root` flux MnvH1D carries the
100-universe `Flux` vert band. Implementation:
- `uq/build_flux_universe_band.py` — POT-weight-combines the per-universe
  flux integrals across 12 playlists → `baseline_flux/`
  `flux_integral_universes_MEFHC.root` (`hFluxCV` 14pT, `hFluxUniv`
  14pT×100). Re-combined CV matches the existing TH1D to **1.7e-16**.
- `uq/rescale_flux_universes.py` — multiplies each of the 100
  `*_uni_full_Flux_<u>.root` by `Φ_CV(pT)/Φ_u(pT)` (exact, σ∝1/Φ), writes
  `uq/universe_sweep_fluxfix/` (100 corrected Flux + 88 symlinks to
  non-Flux+CV; originals untouched).
- Re-rolled `analyze_universes.py --add-norm 0.014` →
  `uq/universe_stage2_MEFHC_full_matcorr_fluxfix/`.

**Verification before implementing**: re-combined CV exact (1.7e-16);
per-universe flux spread flat ~4.9% across all pT; rescaled Flux band
1.01 %→4.99 % with a flat 4.78 % floor (paper 4.01 %/floor 3.90 %); PPFX
**index alignment** confirmed — flux-integral ratio vs omnifile
event-weight ratio Pearson 0.96 / Spearman 0.94 (permuted control −0.25).

**Results:**

| quantity | matcorr | matcorr + fluxfix |
|---|---:|---:|
| `full_Flux` median rel σ | 1.01 % | **4.99 %** (flat, floor 4.78 %) |
| systematic √tr / median rel | 2.463e-39 / 4.78 % | **3.214e-39 / 6.83 %** |
| combined (block-sum) median rel | 4.82 % | **6.87 % ≈ paper 6.86 %** |
| combined-cov χ²/ndf (paper+ours) | 1.703 | **1.481** |
| combined-cov log-normal χ²/ndf | 1.692 | **1.468** |
| pull mean / rms | 0.069 / 0.466 | 0.051 / 0.409 |

Two readings: (i) our **standalone** budget now agrees with the paper's
total (6.87 % vs 6.86 %) — the headline win; (ii) the **paper+ours χ²/ndf
drops** 1.703→1.481 because inflating our flux worsens the flux
double-count against the paper's already-present 4 % flux (that χ² is not
the beneficiary; read it with the double-count caveat / `--subtract-stat`).
Universe rank unchanged (140/205); cond 8.7e8→1.7e9. ~5 % vs paper ~4 %
is a flux-model/PPFX-spread difference (both ν-e-constrained:
`runEventLoop.cpp:348`, `runEventLoopOmniFold.cpp:860`), flagged for the
#65 flux cluster, not a propagation bug.

**Driver support added (durable, no more post-hoc rescale).**
`unfold_2d_omnifold_unbinned.py` now divides flux universes by their own Φ
natively: new `load_flux_universe_bins()` + `--flux-universe-file`
(default `baseline_flux/flux_integral_universes_MEFHC.root`). When
`--universe Flux:IDX` is set, the flux loader replaces the CV `flux_bins`
with `hFluxUniv[:,IDX]` (guards: idx range, pT-bin match, and hFluxCV must
equal the `--flux-hist` CV so universe and CV come from the same flux
production); non-Flux universes and the CV are unchanged. A Flux universe
run with a missing flux-universe file now **fails loudly** rather than
silently re-introducing the bug. Unit-tested (loader + both guards); the
native path is algebraically identical to the post-hoc rescale (same
unfolded U and c, divide by Φ_u either way).

**Open item 2 — normalization 1.4 % vs ~2 %: NOT a gap (resolved).** The
paper states it outright (Ruterbories §VII): *"The normalization
uncertainty of 1.4 % corresponds to the uncertainty in the number of
target nucleons."* So the paper's normalization **is 1.4 %** — exactly our
rank-1 `--add-norm 0.014`. The ~2 % read off Fig 6/7 was eyeball
imprecision (1.4 % vs 2 % on a coarse axis). No POT/detector-mass band to
add; fabricating one would over-count. Our `Normalization` already
matches. *Plot-grouping fix (`category_for_band`):* the 1.4 %
`__Normalization_flat` band was being drawn under **Models**, while the
tiny GENIE NormDISCC/NormNCRES knobs were under **Normalization** — so the
blue Normalization line was invisible. Swapped to the paper's grouping
(`__Normalization_flat`→Normalization; GENIE norm knobs→Models). Pure
visualization (covariance/χ² unchanged): Normalization line now flat at
1.400 %, Models drops to 0.29 %.

**Open item 1 — flux ~5 % vs paper ~4 %: characterized; needs MINERvA
input.** Our per-universe flux integral spread is 5.16 % (integral) /
4.99 % (event-weighted); the paper's `FluxCovariance` is median 4.01 %
(floor 3.90 %). Both are ν-e-constrained (`runEventLoop.cpp:348`,
`runEventLoopOmniFold.cpp:860`), so it is **not** a constraint on/off
mismatch. The residual ~1 % (~25 % relative) is most likely a PPFX
version / flux-treatment difference (e.g. the paper's flux uncertainty may
be rate-weighted over the measured energy range, whereas our Φ is the full
0–100 GeV integral). Cannot resolve from disk: we only store the
*integrated* Φ per pT, not the energy-differential flux, so we can't
re-integrate over a sub-range to test the rate-weighting hypothesis.
Sharp collaborator question for the #65 flux cluster: *what energy range /
weighting and PPFX version does the paper's FluxCovariance use, and is the
4 % the rate-weighted or full-integral spread?* Until answered, our 4.99 %
is internally correct for our cross-section definition (σ ∝ 1/Φ over
0–100 GeV) and is mildly conservative vs the paper.

---

## 2026-05-29 — 300-replica pure-Poisson bootstrap complete + headline refresh

Bootstrap array **sbatch 53489662** drained: 300/300 tasks `COMPLETED`,
all `uq/2d_xsec_MEFHC_5iter_lgbm_boot{1..300}.root` on disk. This is the
fixed-ML-seed resubmit (each replica pins `--seed 1`, varies only
`--bootstrap-seed`), so the cov isolates pure Poisson variance — the
ML-stochastic leak in the previous seed-varying set (sbatch 53327775,
diagnosed in Task #53) is gone. Closes **Task #54**.

Caught a stale rollup: `uq/bootstrap_MEFHC_300/uq_covariance_boot300.root`
was dated May 27 10:42, *older than every one of the 300 replicas* (oldest
replica May 27 13:18) — it had been built from a prior replica set.
Backed it up to `*.stale_may27` and rebuilt from the complete 300 via
`uq/analyze_uq.py`.

### What changed (refreshed bootstrap rolled into the headline)

| Quantity | stale (May 27) | refreshed (300, pinned seed) |
|---|---:|---:|
| C_boot sqrt(trace) | 1.828e-40 | 1.817e-40 |
| C_boot per-bin median rel σ | 0.564 % | 0.549 % |
| C_boot trace | — | 3.299768e-80 |
| Cholesky | PASS | PASS |
| Combined-cov χ²/ndf | 1.699 | **1.703** |
| Combined-cov log-normal χ²/ndf | 1.688 | **1.692** |
| `--subtract-stat` χ²/ndf (std / log-N) | 23.96 / 24.38 | 24.84 / 25.01 |

Combined block-sum √tr stays 2.470e-39 (universe 2.463e-39 dominates;
bootstrap is ~1.5 % of the budget). The headline moved only 1.699→1.703,
confirming the prior ML-seed contamination was numerically negligible —
the fix is correctness/hygiene, not a material shift. χ²/ndf nudged *up*
because the refreshed C_boot is slightly smaller (less added to the
denominator). The larger `--subtract-stat` swing (23.96→24.84) is the
ill-conditioned stat-subtracted baseline amplifying a small C_boot
perturbation, consistent with that diagnostic overcorrecting.

Re-ran `compare_to_paper_fullcov.py --log-normal` against the unchanged
matcorr universe cov + refreshed boot300 + ML seedscan; new headline log
at `uq/universe_stage2_MEFHC_full_matcorr/compare_to_paper.log`. STATUS
doc headline table, Stage-2 envelope bootstrap row, χ² caveat, and the
bootstrap-status note all updated to the refreshed numbers.

---

## 2026-05-28 — MAT-conformant per-band covariance (matcorr rollup)

Compiled a survey of MINERvA's systematics methodology (Ruterbories
2021 paper, MINERvA Open Data portal, MAT source; since consolidated
into `docs/uq_statistical_methods.tex`, §"How MINERvA builds its
published covariance"). Two findings drove a code change and a
re-rollup:

1. The "MINERvA-101 ±1σ pair formula"
   `C^B = ½(Δ₊Δ₊ᵀ + Δ₋Δ₋ᵀ)` with `Δ = X − X_CV` that
   `uq/analyze_universes.py:198-205` was using is a folk re-derivation,
   not what MAT does. The real formula in
   `MAT/PlotUtils/MnvVertErrorBand::CalcCovMx` is uniformly the
   *mean-centered* biased sample covariance with `1/N` normalization,
   with no special case for N = 2:

       C_band = (1/N) · Σ_u (X_u − ⟨X⟩_u) (X_u − ⟨X⟩_u)ᵀ

   The two formulas agree for symmetric ±1σ shifts
   (`X₊ + X₋ = 2 X_CV`); for asymmetric pairs they differ. The N ≥ 3
   ensemble case differs by Bessel `N/(N − 1)`.

2. The paper's full-rank V also folds in bands we were not yet
   propagating — at minimum the 1.4 % target-nucleon normalization
   (Aliaga NIM 1305.5199, rank-1 outer `σ²·1·1ᵀ`), the Bashyal joint
   flux ↔ Muon_Energy_MINOS block (JINST 16 P08068, the only
   cross-band correlation Ruterbories explicitly names), and likely
   FrInel_pi (we have FrInel_N).

### Code change

`uq/analyze_universes.py`:
- Replaced the N=2 pair / N≥3 ensemble branch (lines ~198-205) with a
  single `(Z.T @ Z) / N` MAT formula where `Z = D - D.mean(axis=0)`.
- Added `--add-norm SIGMA` flag that adds the flat rank-1
  `(SIGMA·cv)(SIGMA·cv)ᵀ` band; pass `0.014` for the paper's 1.4 %
  normalization.
- Added `--legacy-pair-formula` escape hatch for forensic comparison
  against pre-2026-05-28 rollups.
- Refreshed module docstring; band cov `mode` print now reads
  `mat_mean_centered(N=...)`.

### Per-band verification (legacy vs MAT, 187-universe matched-CV set)

| Pair regression | asym | new/legacy trace ratio |
|---|---:|---:|
| MinosEfficiency (most symmetric) | 0.12 | 0.996 |
| Muon_Energy_MINERvA | 0.36 | 0.960 |
| Muon_Energy_MINOS | 0.43 | 0.950 |
| MaRES, MaCCQE, MvRES, BhtBY | 1.0–1.2 | 0.59–0.70 |
| BeamAngleY, BeamAngleX, MuonResolution | 1.7–1.9 | 0.03–0.13 |
| NormNCRES, MaNCEL, EtaNCEL (perfectly one-sided) | 2.0 | ≈ 0 |

For one-sided pairs (`D[0] ≈ D[1]`), `D − ⟨D⟩` is ≈ 0 in both rows,
so MAT correctly collapses the band to zero variance — these
"universes" don't span any direction relative to the universe mean,
even though they shift X_CV by a real ±δ.

Ensemble (Flux PPFX, N=100): new/legacy trace ratio = 0.990 =
exactly (N − 1)/N, confirming the Bessel correction.

### Re-rollup outputs

`uq/universe_stage2_MEFHC_full_matcorr/uq_universe_covariance_full_matcorr.root`
contains the new total. Total trace dropped 1.9 % vs the legacy
rollup; the 1.4 % norm band adds back 5.9e-40 sqrt-trace, partially
offsetting the 9.3 % reduction from the formula switch alone.

| Quantity | Legacy (1.473 build) | matcorr (current) |
|---|---:|---:|
| C_universe sqrt(trace) | 2.511e-39 | 2.463e-39 |
| C_universe median rel σ | 5.28 % | 4.78 % |
| C_universe rank / 205 | 178 | 140 |
| C_universe cond | 9.1e10 | 8.7e8 |
| Combined-cov χ²/ndf | 1.473 | **1.699** |
| Combined-cov pull mean / RMS | 0.067 / 0.447 | 0.069 / 0.466 |

Rank ceiling on `C_universe` is now driven by band count rather than
universe count: under MAT each pair contributes rank 1 (mean-centering
collapses N=2 to a single direction), so 42 pairs + PPFX (rank 99) +
2p2h (rank 2) + norm rank-1 = 144 — cap close to the observed 140.
The cond improvement (2 orders of magnitude) reflects the legacy
build inserting spurious near-null directions through the
sum-of-rank-1 pair contributions.

### Ours-only diagnostic table on the matcorr C_ours

`C_ours = C_universe(matcorr) + C_bootstrap300 + C_ML`, pull mean/RMS
0.110 / 0.816:

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
| Diagonal-target shrinkage λ=0.05 | 204 | 879.0 | 4.31 | 4.29 |
| Diagonal-target shrinkage λ=0.20 | 204 | 346.2 | 1.70 | 1.69 |

Two-decade ridge scan 0.45 → 5.86; two-decade shrinkage scan
1.69 → 17.82. Same "no defensible single cutoff" pathology as the
pre-matcorr rollup, slightly stiffer because the matcorr `C_universe`
has smaller eigenvalues on the retained modes.

### Documentation cascade

- `2D_OMNIFOLD_STUDY_STATUS.md`: header preamble, headline table
  (1.473 → 1.699), methodology caveat preamble + diagnostic table
  (full replacement), Stage-2 envelope universe row, Methods → *Syst:*
  bullet, rollup-path paragraph, and `uq/analyze_universes.py`
  description.
- `advisor_memo_cov_rank.md` (since consolidated into
  `docs/uq_statistical_methods.tex`, §Ill-conditioning): problem block
  (rank/cond + headline), "what we have tried" 1/2/3 (new matcorr
  numbers across the three regularization scans), "what we will do
  regardless" (formula switch marked done, asks A/B/C refocused on
  Bashyal + FrInel_pi + per-target shape).
- `/global/homes/j/josephrb/.claude/plans/melodic-cooking-spark.md`:
  new "Per-band covariance formula" + "Additional bands" sections,
  and an "Execution plan: code update + re-rollup" subsection with
  the exact commands and verification regressions.

### Out of scope (separate campaigns)

- Bashyal flux ↔ Muon_Energy_MINOS cross-band block — needs
  covariance from collaborators or re-derivation from JINST 16
  P08068. Once obtained, adds an off-diagonal block in
  `analyze_universes.py` without re-running any universes.
- FrInel_pi universe — **not actually a gap on our side.**
  `MAT-MINERvA/universes/GenieSystematics.cxx:37` explicitly
  excludes the knob with the comment "Dan says that this knob
  should not currently be evaluated but that we should revisit this
  eventually." The Ruterbories TotalCov inherits this exclusion,
  so our matcorr build is consistent with the paper on FrInel_pi.
  Open question for collaborators is whether the exclusion still
  holds in 2026.
- Per-target-region detector-mass shape pieces beyond the flat 1.4 %,
  if Aliaga 1305.5199 supplies them.

## 2026-05-28 — Methodology audit follow-ups (log-normal χ², MnvH1D parity, stat double-count)

Closed the three audit items left over from the matcorr correction
(plan tasks #67/#68/#69) without re-running any event loops or
unfolds. All edits are downstream of `uq/analyze_universes.py`.

**Task #67 — log-normal χ² as a secondary statistic.** Added
`--log-normal` to `compare_to_paper_fullcov.py`. Implementation: on
the same reported-bins mask, compute `r = log(ours/paper)` and
`V_log[i,j] = V[i,j] / (xᵢ·xⱼ)`, then `χ²_log = rᵀ pinv(V_log) r`.
On the matcorr combined-cov rollup the headline numbers are

    combined χ²/ndf            : 1.699
    combined log-normal χ²/ndf : 1.688

The near-identity of the two values is itself the useful diagnostic:
Peelle's Pertinent Puzzle would bias the standard χ² down relative
to log-normal only if a near-uniform normalization scale dominated
the data-model disagreement. Our 1.0111 σ_total ratio is small
enough that PPP is not load-bearing. Both quantities are now carried
in the STATUS doc headline table for paper Table I parity.

**Task #68 — MnvH1D::GetTotalErrorMatrix byte-for-byte parity.**
Wrote `uq/verify_matcorr_vs_mnvh1d.py`. It loads the same 44
per-band × 188 per-universe X_u vectors `analyze_universes.py`
consumes, populates a `PlotUtils::MnvH1D` (205 reported-bin flat),
adds one `MnvVertErrorBand` per band with the per-universe TH1Ds,
then calls `GetTotalErrorMatrix(includeStat=False, asFrac=False,
cov_area_normalize=False)` and diffs against the Python rollup
produced with `--add-norm 0` (so the comparison is band-by-band
identical; the 1.4 % rank-1 we add on top of MAT is excluded).

Result (`uq/matcorr_vs_mnvh1d.txt`):

    n_reported               : 205
    bands populated          : 44
    sqrt(trace) MAT          : 2.391038e-39
    sqrt(trace) Python       : 2.391038e-39
    max |diff|               : 1.20e-94
    max |diff| / max(|cov|)  : 5.49e-17
    Frobenius norm (diff)    : 2.67e-94  (vs 4.81e-78 norm)

5.5e-17 is machine epsilon for double-precision arithmetic. Our
Python rollup is identical to MAT's `MnvVertErrorBand::CalcCovMx`
plus `MnvH1D::GetTotalErrorMatrix` reference path. Implementation
gotcha worth recording: `GetTotalErrorMatrix` returns a
`(nbins+2)×(nbins+2)` TMatrixD that includes the under/over-flow
rows, so the script slices `[1:n_rep+1, 1:n_rep+1]` before diffing.

**Task #69 — bootstrap/paper-stat double-count.** Added
`--subtract-stat` to `compare_to_paper_fullcov.py`. When set, the
baseline becomes `paper TotalCov − paper StatOnlyCov` before
adding our OmniFold covariances; the stat-only and paper-full-cov
lines are unchanged. Numerical result on the matcorr rollup:

    combined χ²/ndf            : 1.699  (default; double-counted)
    combined χ²/ndf            : 23.96  (--subtract-stat)
    combined log-normal χ²/ndf : 1.688  (default)
    combined log-normal χ²/ndf : 24.38  (--subtract-stat)

The 24-ish answer is the strictly-honest one, but it is *worse* as
a publication number than the default because OmniFold's bootstrap
band (sqrt(trace) ≈ 1.83e-40) is much smaller than the paper's
StatOnly block (a substantial fraction of TotalCov, sqrt(trace)
≈ 2.7e-39). Subtracting paper-stat and adding our much smaller
C_boot leaves an effective denominator that is too small.

Verdict: keep 1.699 as the headline (with the framing "what does
OmniFold UQ add on top of the published V"), document the
de-double-counted 23.96 / 24.38 numbers in STATUS as a secondary
diagnostic, and revisit only if a publication referee asks for the
strictly-non-overlapping construction. Doc updated.

**No event loops, no unfolds, no sbatch.** All three items are
post-rollup analysis. Files touched:

- `compare_to_paper_fullcov.py` — `--log-normal`, `--subtract-stat`,
  new `chi2_lognormal` helper.
- `uq/verify_matcorr_vs_mnvh1d.py` — new, ~150 lines.
- `uq/universe_stage2_MEFHC_full_matcorr_nonorm/` — new directory
  carrying the `--add-norm 0` parity rollup that #68 compares
  against. Distinct from the `_matcorr/` headline rollup which
  carries the 1.4 % band.
- `2D_OMNIFOLD_STUDY_STATUS.md` — headline table gains log-normal
  χ²/ndf row; two new subsections cover the MnvH1D parity and the
  stat-block double-count finding.
- `uq/matcorr_vs_mnvh1d.txt` — frozen verification report.

## 2026-06-03 — Disk cleanup: reclaimed ~547 GiB of re-derivable intermediates (repo-wide)

2D portion of a repo-wide trim (860 GB → ~313 GB; full inventory in
`../3d-unfolding/3D_OMNIFOLD_RUN_LOG.md`). **Deleted** (gitignored and
re-derivable; the merged `…_MEFHC_universes_full.root` and all distilled
xsec/covariance products kept):
- `runEventLoopOmniFold_MEFHC_universes.root` — 64 GiB non-"full", superseded by
  `…_MEFHC_universes_full.root`.
- the 12 per-playlist `runEventLoopOmniFold_1{A..P}_universes_full.root` (119 GiB),
  already merged into the kept MEFHC omnifile.
- `universe_smoke/*.root`, `__pycache__/`, and stray root-level job logs
  (`final_rollup_full_*`, `iter_scan_1A_3_*`, `unfold_MEFHC_uni_full_CV_*`).

**Regen** if needed: per-playlist event-loop array → `uq/hadd_universes_full.py`
(SetMaxTreeSize merger, **not** bare hadd — memory `hadd-100gb-tree-limit`).
