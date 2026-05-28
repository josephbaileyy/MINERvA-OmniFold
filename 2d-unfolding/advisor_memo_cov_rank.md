# Advisor memo — OmniFold ours-only covariance is rank-deficient

**Context.** Reproduction of arXiv:2106.16210 (MINERvA ME FHC d²σ/dpT
dp∥, CC inclusive) using 2D unbinned OmniFold in place of D'Agostini
IBU. Central-value cross-section reproduces the paper to ~1 % per bin;
σ_total(ours)/σ_total(paper) = 1.011. Comparison so far has used the
paper's TotalCov to compute χ². For publication we need an
OmniFold-derived covariance and a clean ours-only χ²/ndf statement.

**Problem.** The OmniFold systematic covariance is built by sampling
MINERvA-101 universe shifts (PPFX flux ×100, ±1σ pairs for ~40 GENIE
knobs, lateral muon-energy / MINOS-efficiency variations, etc. — 187
universes total) using the MAT-conformant mean-centered biased sample
cov `C_band = (1/N)·Σ_u (Xᵤ−⟨X⟩_u)(Xᵤ−⟨X⟩_u)ᵀ` and a 1.4 % flat
target-nucleon normalization rank-1 band. Under this MAT formula
each ±1σ pair contributes rank 1 (mean-centering collapses N=2 to a
single direction), so the per-band rank ceiling for the 187-universe
set is 42 pair bands × 1 + 1 ensemble (PPFX, rank N−1=99) + 1 ensemble
(2p2h, N=3 → rank 2) + 1 norm rank-1 = 144. On the 205-bin matcorr
rollup:

    rank(C_universe, matcorr) = 140 / 205    (65 null directions)
    cond(C_universe)          = 8.7e8        (effective)

Adding the bootstrap and ML blocks barely changes the rank picture:
`C_ours = C_universe + C_bootstrap300 + C_ML` is rank ~145/205 with
cond a few × 10⁸. The rank ceiling here is set by **band count**, not
universe count: it is the MAT formula's collapsing of each pair to
rank 1 that drives the deficiency on a 205-bin set.

On the same matcorr rollup, the combined-cov
(paper TotalCov + C_universe + C_bootstrap300 + C_ML) χ²/ndf vs paper
on 205 bins is **1.699** (pull mean/rms 0.069/0.466), which we
believe is the correct headline. The pre-MAT-conformant rollup gave
1.473 — the move from 1.473 → 1.699 is the legitimate cost of (a)
correctly collapsing one-sided knob pairs (BeamAngleX/Y, MuonResolution,
NormNCRES, MaNCEL, EtaNCEL) to near-zero variance, and (b) using the
biased 1/N normalization on PPFX instead of Bessel ddof=1. A naïve
"ours-only" χ² with the rank-deficient cov is not a usable publication
statistic — across a two-decade ridge scan it spans χ²/205 ≈ 0.45 →
5.86, and across eigenvalue-cut scans it spans χ²/rank ≈ 2.67 → 10.3,
with no defensible single choice of cutoff.

**What we have tried.** (All numbers below are the current matcorr
rollup, post-2026-05-28.)

1. *Eigenvalue-truncated χ² on C_ours = C_universe + C_boot + C_ML*:
   keeping modes with λ/λmax above {1e-3, 1e-4, 1e-5} retains rank
   {13, 39, 71} and gives χ²/rank ∈ {2.67, 7.11, 10.31} (χ²/205 ∈
   {0.17, 1.35, 3.57}). Strongly cutoff-dependent; not a defensible
   single number.

2. *Ridge regularization* (C_ours + ε·λmax·I): ε ∈ {1e-3, 1e-4, 1e-5}
   gives χ²/205 ∈ {0.45, 1.84, 5.86}. Same two-decade sensitivity.

3. *Diagonal-target shrinkage* (Σ̂ = (1-λ)·S + λ·diag(S)) on C_ours:
   λ ∈ {0.005, 0.01, 0.02, 0.05, 0.10, 0.20} gives ours-only
   χ²/205 ∈ {17.8, 11.8, 7.7, 4.3, 2.7, 1.7}. Per-bin pull rms is
   0.816 across the entire λ scan (shrinkage preserves the diagonal
   exactly). Same two-decade sensitivity as the ridge / eigenvalue-cut
   scans — a third regularization knob with the same pathology.

4. *Eigenanalysis of the paper's TotalCov*: cond ~ 1.5e12 — also
   nominally ill-conditioned. **Correction (2026-05-28):** an earlier
   draft of this memo claimed MINERvA-101 builds TotalCov analytically.
   Reading `MAT/PlotUtils/MnvVertErrorBand::CalcCovMx` shows MAT
   samples per-band just like we do, uniformly using the biased
   mean-centered sample cov `(1/N)·Σ_u (Xᵤ−⟨X⟩)(Xᵤ−⟨X⟩)ᵀ` with no
   special pair case. The paper's full-rank V most likely comes from
   (i) bands we don't yet propagate — overall normalization 1.4 %
   (Aliaga NIM `1305.5199`) as a rank-1 outer product, the Bashyal
   flux ↔ Muon_Energy_MINOS joint block (JINST 16 P08068), possibly
   FrInel_pi and per-target shape — and (ii) higher-N bands beyond
   PPFX. See `reference/minerva_systematics_sources.md`.

**Specific asks for MINERvA collaborators.**

A. **Missing bands beyond `MnvVertErrorBand`.** The published
   TotalCov is full-rank where our matcorr per-band sum is rank
   140/205, and we believe the gap is in bands not yet propagated:
   (i) the **Bashyal flux ↔ Muon_Energy_MINOS joint block**
   (JINST 16 P08068) — the only cross-band correlation the
   Ruterbories paper explicitly names; is the joint posterior
   covariance available from MAT-MINERvA, or do we need to
   re-derive it from the published fit? (ii) **FrInel_pi** is
   commented out in `MAT-MINERvA/universes/GenieSystematics.cxx:37`
   with the note "Dan says that this knob should not currently be
   evaluated but that we should revisit this eventually" — is the
   2020-era exclusion still current guidance, and if so, what is
   the documented reason (badly calibrated ±1σ envelope vs external
   data, double-counting with FrAbs_pi / FrPiProd_pi, weight
   pathology)? (iii) Any per-target-region detector-mass shape
   pieces beyond the flat 1.4 % normalization we now add.
   The 1.4 % normalization rank-1 (Aliaga NIM `1305.5199`) is in
   our matcorr build as of 2026-05-28.

B. **PPFX universe correlations.** Our 100 PPFX universes appear to
   sample a much lower-dimensional underlying nuisance model. Is
   there guidance on the effective rank of the PPFX covariance, or a
   recommended principal-component decomposition that would let us
   propagate a fixed-rank flux cov rather than treating the 100
   universes as 100 independent samples?

C. **Publication precedent.** Have other MINERvA-101-based analyses
   that built OmniFold or other unbinned uncertainty covariances run
   into this same rank issue, and if so what did they ultimately
   publish for ours-only χ²?

**What we will do regardless.**

- Final publication-grade result uses the combined cov (paper TotalCov
  + OmniFold universe + bootstrap + ML) for the headline χ²/ndf, with
  the rank-deficiency caveat documented. χ²/ndf = 1.699
  (pull mean/rms 0.069/0.466) on the matcorr rollup.
- Done (2026-05-28): switched `uq/analyze_universes.py` to MAT's
  mean-centered 1/N per-band formula uniformly (deleted the N=2
  CV-centered pair branch). Added `--add-norm 0.014` for the 1.4 %
  target-nucleon normalization rank-1 band. Re-rolled up to
  `uq/universe_stage2_MEFHC_full_matcorr/`. Headline moved from
  1.473 → 1.699 — the change is driven by MAT correctly collapsing
  one-sided knob pairs (BeamAngleX/Y, MuonResolution, MaNCEL,
  NormNCRES, EtaNCEL) to near-zero variance.
- Still to add (asks A/B): Bashyal flux ↔ Muon_Energy_MINOS joint
  block; possibly per-target detector-mass shape. FrInel_pi is
  excluded by MAT-MINERvA itself (intentional, per the in-tree
  comment), so we are *consistent with MAT* on that one — the
  ask there is whether the exclusion should still hold, not how
  to add the knob.
- Shrinkage-regularized ours-only cov reported as a secondary
  characterization with λ disclosed.
- If (B) yields a PPFX effective rank ≪ 100: rebuild the flux block
  from the rank-reduced model and re-roll up. This alone may
  re-allocate enough rank to make the sample-cov approach defensible.

**Pointers for technical inspection.**

- Codebase: `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/`
- Universe sweep driver: `sbatch_unfold_2d_MEFHC_5iter_universes_full.sh`
- Sample-cov build: `uq/analyze_universes.py` (lines ~184-210);
  formula audit + correction plan in `reference/minerva_systematics_sources.md`
- Status doc with full numbers: `2D_OMNIFOLD_STUDY_STATUS.md`
- MINERvA-101 universes consumed:
  `MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp`
  with `MNV101_DUMP_UNIVERSES=` listing the 44 bands currently dumped.
