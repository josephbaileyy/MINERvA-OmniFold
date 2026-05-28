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
