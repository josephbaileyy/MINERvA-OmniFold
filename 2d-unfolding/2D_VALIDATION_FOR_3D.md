# 2D UQ validation sign-off — prerequisites for the 3D systematic campaign

Date: 2026-05-31. Purpose: before lifting the systematic-UQ machinery from 2D to
3D (which re-runs the *same* event-loop registry and the *same* covariance /
inversion code), confirm the 2D products are correct and decide what must be
fixed first. Three checks below; two are green, one is a sharply-localized open
item now tied to the running data/MC-split bootstrap campaign.

## Check #4 — systematic-universe completeness: **GREEN**

`uq/universe_stage2_MEFHC_full_matcorr_fluxfix/` rollup (`rollup.log`):
- **44 bands / 188 universes**, all matching MAT `GetStandardSystematics`.
  Flux = 100 PPFX universes; 2p2h = 3; every other band 2-sided (±1σ).
  6 lateral (BeamAngleX/Y, MuonResolution, GEANT_{Neutron,Pion,Proton},
  Muon_Energy_MINERvA) + 38 vertical.
- Covariance verified **byte-for-byte against MAT `MnvH1D::GetTotalErrorMatrix`**
  — max element-wise rel diff 5.5e-17 (`uq/matcorr_vs_mnvh1d.txt`).
- Flux 1/Φ normalization bug fixed (Task #70): Flux band 1.0 %→**4.99 %**; our
  standalone budget 6.87 % ≈ paper 6.86 %.
- Two benign notes: `EtaNCEL` is null (√tr ~1e-51 — NC-elastic, irrelevant to a
  νμ-CC sample); `FrInel_pi` is *correctly absent* (not in the MAT registry; we
  studied that dial separately and found it sub-percent on E_avail).

→ The 2D systematic propagation is complete and validated. Safe to reuse the
same registry for the 3D event-loop re-run.

## Check #3 — ours-only χ² conditioning: **GREEN on systematics, but see open item**

χ²(ours − paper) inverting our covariance the same way the paper inverts its
TotalCov (full pseudo-inverse), 205 reported bins:

| covariance | rank | cond | χ²/ndf (full pinv) |
|---|---|---|---|
| paper TotalCov | 204 | 1.5e12 | 3.66 |
| OUR `C^syst(fluxfix)+C^boot` | 199 | 6.1e14 | **260** |

The 260 is **not** a physics discrepancy — it is the band-count rank deficiency
(~44 systematic directions, not 205) plus an under-sized stat block. **Decisive
swap test** (change only one block):

| covariance for d = ours − paper | χ²/ndf |
|---|---|
| paper syst + paper stat (= paper Total) | 3.66 |
| OUR syst + OUR boot300 | 260 |
| **OUR syst + paper StatOnly** (swap stat in) | **2.80** |
| paper syst + OUR boot300 (swap syst in) | 666 |

Swapping **only** the stat block collapses 260→2.80 (≈ paper 3.66); swapping the
systematic block instead makes it *worse*. **Our systematics are sound; the
entire inflation is the statistical block.**

The effect is *uniform across all modes*, not a tail artifact (properly
`/k`-normalized leading-mode reduced χ²): paper 2.2–4.8 across k; ours 4.2→260;
`OUR syst + paper StatOnly` tracks the paper (1.8–2.8) at every k. Reason: the
paper `StatOnly` is essentially **diagonal**, adding a variance floor to *every*
mode; our bootstrap stat is 2.55× smaller in σ (6.52× in variance) **and**
wrong-structured (correlated/rank-deficient, not a clean diagonal). Scaling our
bootstrap variance ×6.52 to match the trace only reaches χ²/ndf 76.7, not 2.80 —
so it is **shape, not just magnitude**.

**Rule carried into 3D:** never report a raw-pinv ours-only χ². The 3D cov is
more rank-deficient (more bins, same ~44 directions), so 3D goodness-of-fit must
use a mode-truncated inverse at the effective rank, or the combined paper+ours
cov (2D combined χ²/ndf = 1.48). Quote per-bin pulls otherwise.

## ~~OPEN ITEM~~ — the stat block  ✅ RESOLVED 2026-06-02

Our Poisson-bootstrap stat covariance is 2.55× smaller (and differently
structured) than the paper's `StatOnly` — this was the dominant control on the
ours-only χ² (Check #3) and **open question #1** in
`docs/uq_statistical_methods.tex`. The data/MC-split bootstrap campaign
(`sbatch_unfold_2d_MEFHC_5iter_bootsplit.sh`, arrays 53678615/616; 200 replicas
each, `uq/run_split_analysis.sh` + `uq/compare_split_bootstrap.py`) **resolved
it 2026-06-02:**

- **Closure holds:** `C_data + C_mc ≈ C_both` (trace ratio 1.07, Frobenius 0.21);
  variance splits **data 77% / MC 23%**.
- **The 2.55× gap is genuine, not a bug:** `C_data` *alone* = **0.356×** the
  paper `StatOnly` (and `C_both`/paper = 0.392 = 1/2.55). Our *data*-statistical
  error is really smaller than the paper's binned-D'Agostini stat error
  (OmniFold efficiency), independent of the MC stream.
- **But also a structure difference:** ours is correlated (mean |off-diag| 0.108,
  leading-eigvec overlap with paper only 0.46) vs the paper's ~diagonal (0.009).

**Consequence:** for an ours-only χ² use OUR own combined covariance (do NOT
inflate the stat block to the paper's — that would double-count and mis-structure
it). This unblocked the 3D ours-only goodness-of-fit
(`3d-unfolding/genie/compare_3d_fullcov.py`, run 2026-06-02).

## Flux ~5 % vs paper ~4 %: characterized, needs collaborator input (not a blocker)

Not a propagation bug (the 1/Φ bug is fixed), not a ν-e-constraint mismatch
(both constrained). Residual ~1 % absolute (~25 % rel): ours 4.99 % vs paper
4.01 %. Leading hypothesis = PPFX-version / energy-range weighting (paper may be
rate-weighted over the measured range; ours is the full 0–100 GeV Φ integral).
Not resolvable from disk (we store only integrated Φ). Sharp question for the
#65 flux cluster. Until then ours is internally correct and mildly conservative.
Carries to 3D unchanged (flux is pT-binned; the 3D σ ∝ 1/Φ(pT) the same way).
