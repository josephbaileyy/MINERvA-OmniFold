# Literature & open-data notes (OmniFold + MINERvA)

Reference notes captured during the 2026-06-03 analysis audit, so future work does
not have to re-derive them. Two threads: (A) the current OmniFold / unbinned-unfolding
literature and how this analysis compares; (B) the MINERvA open-data and data-release
catalogue and which releases are relevant here.

---

## A. OmniFold / unbinned-unfolding literature

### Key references (2025)

- **T2K OmniFold neutrino paper** — Huang et al., "Machine Learning-Assisted Unfolding
  for Neutrino Cross-section Measurements with the OmniFold Technique," Phys. Rev. D
  (2025), **arXiv:2504.06857**. First application of OmniFold to a neutrino cross section
  (public T2K ND280 simulated data).
- **Practical Guide** — Canelli, Cormier, Cudd, ... Nachman, et al., "A Practical Guide
  to Unbinned Unfolding," **arXiv:2507.09582** (Jul 2025). Cross-experiment community
  guidance.
- Foundational: Andreassen et al. OmniFold **arXiv:1911.09107**; H1 demonstrations
  **arXiv:2108.12376**, **arXiv:2303.13620** (all already in `technote.bib`).

### What the 2025 references actually recommend (concrete)

**Uncertainty quantification**
- *Ensembling*: 4–10 ensemble members typical. T2K uses **5 trials** with different
  train/test splits and **averages the reweighting factors into the central value**;
  the residual NN stochastic error is then ~1–2% of the total budget and "negligible."
- *Statistics*: bootstrap ~50–100 runs. T2K uses weighted-Poisson resampling of data
  (each weight-w event redrawn Poisson(w)) and bootstrap-with-replacement for MC stats.
- *Systematics*: ~100 coherent throws. T2K runs **500 toy throws** that each fold
  detector+xsec+flux systematics *and* stat resampling through the **full unfolding**,
  then builds **one covariance from the spread** (Σ from the 500 unfolded results).
- Net: the literature builds a **single unified covariance** from joint throws, capturing
  stat↔syst coupling and the unfolding's nonlinear response.

**Iterations / regularization**
- OmniFold software default = 3 iterations; ≤5 typical in final results. (T2K needed
  20–45 for its neutrino smearing — observable/detector dependent.)
- Do **not** pick the iteration count from truth-level χ² (needs the truth you are trying
  to measure). Unbinned stopping criteria (per-event weight-change → Gaussian about 0)
  are an open research problem.

**Classifier**
- Field standard is a dense NN (2–4 hidden layers, ~100–200 nodes, ReLU/sigmoid, BCE
  loss → likelihood ratio, early stopping ~10–15 epochs, batch O(10³)).
- Reweighting w = f/(1−f) requires **calibrated** classifier output. BCE naturally
  yields the likelihood ratio.
- Preprocessing: z-score standardize; sin/cos for angles; clip/handle negative MC weights.

**Validation diagnostics**
- *Bottom-line test*: unfolded-vs-truth discrepancy must be **smaller** than the original
  reco data-MC discrepancy. (Practical Guide, emphasized.)
- *Stress tests*: unfold MC-against-MC with stochastic and non-observable-dependent
  reweightings; verify the network learns the right dependence.
- *Coverage*: toy experiments should contain truth ~68% of the time.
- *Efficiency*: applying the efficiency correction **post-unfolding** (extrapolate misses
  with a classifier) converges faster than carrying misses through step 2.

**Goodness-of-fit for unbinned / high-D**
- Open problem. χ² on binned projections is used but "less ideal." Suggested unbinned
  alternatives: **Wasserstein distance**, **permutation tests**. No settled standard for
  rank-deficient covariance.

### How THIS analysis compares (audit, 2026-06-03)

| Aspect | This analysis | Literature | Assessment |
|---|---|---|---|
| Classifier | LightGBM GBDT (estimator parity tested) | Dense NN (all published) | Legitimate; add calibration + NN cross-check to pre-empt referees |
| Iterations | 5 (validated <0.03% vs 10-iter) | 3 default, ≤5 typical | Fine; document why 5 suffices here |
| ML noise | 10-seed scan **measures** noise; CV not ensembled | 5 trials **averaged into CV** | Adopt ensemble-mean CV in **3D** (lgbm, stochastic). In **2D** the production CV is deterministic exact-GBT, so ensembling is moot — see finding below |
| Statistics | Poisson bootstrap, 300 (2D)/100 (3D) | 50–100 bootstrap | Adequate |
| Systematics | 187 MAT universes (coherent weight branches) | ~100–500 coherent throws | Strong; MAT-conformant |
| Covariance | **Block-sum** C_syst+C_stat+C_ML | **Unified** single covariance from joint throws | Defensible (independent sources, MAT convention); assumes linear unfolding response — document justification; full unified-throw cross-check is future work |
| Efficiency | completeness c=1 by construction (Phase-18) | post-unfolding extrapolation preferred | Equivalent/strong |
| Bottom-line test | only in a 1D side study | recommended standard | Add to 2D/3D + technote |
| GoF | truncated-spectral χ² on rank-deficient cov | open problem | On par with field; could add Wasserstein/permutation |

**Verdict:** no critical defects. Divergences are refinements, the largest being
(i) ensemble-mean CV (3D only — see below), (ii) bottom-line test, (iii) GBDT-vs-NN
robustness, and the methodological note on block-sum vs unified covariance.

### Audit finding — ensemble-mean / ML-noise (verified 2026-06-03)

Tool: `2d-unfolding/uq/ensemble_mean_cv.py` (reads the existing per-seed xsec files,
no re-unfolding). Key facts established by inspecting the driver, `omnifold.py`, and the
seed ensembles:

- The driver's `--seed` pins only the **GBDT `random_state`** (step-1/step-2 classifier
  + miss regressor); it does **not** vary the train/test split. So the seed scan samples
  model-init stochasticity only.
- The **2D production CV is the `exact` estimator** (`sbatch_unfold_2d_MEFHC.sh` takes the
  driver default `--estimator exact`; run-log line 58 = "exact-GBT (frozen production)").
  sklearn `GradientBoostingClassifier` with default `subsample=1.0`, `max_features=None`
  is **deterministic** — `random_state` is inert. **The 2D published CV therefore has no
  ML stochasticity to ensemble away**; the 0.166% lgbm seed band is a *conservative
  cross-estimator proxy*, not the production estimator's own noise. (The 2D `seedscan_lgbm`
  files sit ~5 seed-σ from the frozen exact CV per-bin while totals agree to 0.01% — that
  gap is the exact↔lgbm shape difference, consistent with the documented estimator parity
  on the total, not under-dispersion.)
- The **3D production CV is `lgbm`** (stochastic). Frozen-vs-ensemble pull is **0.63σ
  median** (p90 1.48) → the single-seed CV is one consistent draw; the lgbm seed band
  (0.450%/bin median) adequately characterizes its ML noise. **Adopting the 10-seed
  ensemble mean is a genuine, low-risk improvement**: it de-noises the 0.45%/bin band to
  ~0.14% (÷√10) and shifts the result negligibly (+0.013% median, ~0% on the total).
  Ensemble file written to `3d-unfolding/xsec_3d_MEFHC_5iter_lgbm_ensemble.root`
  (`hXSec3D_ensemble`).

**Recommendations:** (1) 3D — promote the 10-seed ensemble mean to the central value (or
report it as the headline with a footnote); the change is sub-permille. (2) 2D — no action
on ensembling; instead document that the production estimator is deterministic and that the
lgbm seed band is a conservative ML-noise proxy. (3) Optional, for full literature
alignment: a future seed scan that also varies the train/test split would convert the ML
band from "model-init only" to the T2K-style total ML stochasticity.

---

### Audit finding — bottom-line test (added 2026-06-03)

Tool: `2d-unfolding/uq/bottom_line_test.py` (`--mode closure` default, `--mode data-prior`
diagnostic). The Practical Guide's bottom-line test ("unfolded discrepancy must be smaller
than the original data-MC difference") previously lived only in a 1D side study. Now run
for 2D and 3D on the existing closure outputs, in the bins that carry the injected feature:

- **2D** (1A gaussian-bump truth reweight): injected feature 17.2% RMS, recovery residual
  1.69% → ratio **0.098** (10× better than the feature). PASS.
- **3D** (MEFHC +30% E_avail bump, E_avail projection): injected 18.1%, residual 1.84% →
  ratio **0.102**. PASS.

The naive data-vs-prior form (`--mode data-prior`) gives truth χ²/ndf (534) > reco (278);
this is **expected and not a failure** — detector smearing lowers the reco data-prior
baseline and the stat-only diagonal omits the unfolding's correlated covariance. The proper
full-covariance goodness-of-fit is the existing χ²-vs-paper (1.481) and the generator
comparisons. The closure form is the valid pass/fail and both dims pass with ~10× margin,
consistent with the documented full-stats closure residual (0.046%).

### Audit finding — GBDT calibration + NN cross-check (added 2026-06-03)

Tool: `2d-unfolding/uq/classifier_calibration.py` (subsampled step-1 reco classifier,
data vs MC reco; reliability + GBDT-vs-NN, ~2 min, no full unfold). Addresses the "all
published OmniFold uses NNs; this uses LightGBM" referee concern.

- Step-1 reco AUC ~0.537 (GBDT) / 0.534 (small MLP): data and MC reco are nearly
  indistinguishable in (pt,pz) — the MC models the data well, so the OmniFold reweight
  w=p/(1-p) is a modest correction. Brier ~0.25, reliability curves near-diagonal:
  both classifiers are calibrated, so w=p/(1-p) is valid.
- The TRUE (pt,pz)-binned data/MC ratio still spans ~100% across bins (real reweighting
  to do). **GBDT recovers it to 4.7% median / 35% max; the MLP to 20.9% / 46%** — on this
  low-dimensional tabular problem the GBDT is at least as accurate as (here more accurate
  than) a small dense NN, supporting the production choice.
- **corr(reweight_GBDT, reweight_NN) = 0.92** across bins: the learned reweight is robust
  to the classifier family. (The MLP's larger error is an untuned small net on a subsample,
  not a fundamental NN deficiency.)
- Plot: `2d-unfolding/uq/classifier_calibration.png`. A full NN-estimator unfold is the
  heavier confirmation (add an 'mlp' backend to omnifold.py + sbatch); this classifier-level
  check is the cheap first-order robustness test.

### Audit finding — Ascencio low-q3 comparison (added 2026-06-03)

Tool: `3d-unfolding/genie/compare_ascencio_eavail.py`. Ascencio et al. (arXiv:2110.13372,
PRD 106 032001) measured d2 sigma/(dq3 dE_avail) at <E_nu>~6 GeV with q3<1.2 GeV — the
closest published MINERvA low-recoil inclusive result and it shares the E_avail observable.
It was only in the related-work table (sec_3d.tex:77).

- The script builds our dsigma/dE_avail projection + full combined-covariance band
  (reusing the tested projection machinery in `overlay_generators_band.py`) and overlays
  an external Ascencio spectrum, area-normalized over the shared E_avail range.
- **Phase-space caveat**: Ascencio integrates q3<1.2 GeV; our projection integrates the
  full muon acceptance (all q3). Normalizations differ → the comparison is the dsigma/dE_avail
  SHAPE and the qualitative low-E_avail behaviour, NOT a bin-identical chi2.
- **Status**: the our-side spectrum + band is produced and tested
  (`ascencio_vs_unfolded_eavail.png`); the numerical overlay is STAGED on the 2110.13372
  data release / arXiv ancillary (not publicly fetchable in-session; MINERvA member access).
  Provide it as `eavail_low eavail_high dsigma err` and rerun with `--ascencio`.
- **Qualitative cross-check (citable now)**: Ascencio established that GENIE/NuWro
  underpredict the data in the low-recoil region (the missing-2p2h deficit). This analysis
  independently finds a low-E_avail data excess over all four generators, filled ~46% by
  enabling Valencia 2p2h. The two are consistent — our low-E_avail excess is the same
  low-recoil/2p2h feature Ascencio measured, now seen in the muon-kinematics 3D extension.

## B. MINERvA open data & data releases

### Open data portal — https://minerva.fnal.gov/opendata/
- Pre-selected ROOT AnaTuples (muon or electron candidate), data + simulation.
- Two beam energies: **Low Energy** (⟨Eν⟩~3 GeV) and **Medium Energy** (~6 GeV), each
  FHC and RHC, neutrino and antineutrino.
- Tooling: MinervaExpt GitHub (MAT analysis stack), ME-FHC inclusive tutorial
  (= the MINERvA-101 basis of this repo), Arachne event display, flux release.
- Cite NIM A743 (2014) as the detector reference.
- This analysis uses **ME FHC neutrino** only. Natural scope extensions (not gaps): RHC
  / antineutrino, and the LE samples.

### Data-release page — https://minerva.fnal.gov/data-release-page/
Releases most relevant to the E_avail / low-recoil physics here:

| Release | arXiv | Topic | Relevance |
|---|---|---|---|
| Ascencio et al. 2022 | **2110.13372** | CC-inclusive νμ, **low three-momentum transfer (q3)**, ME ⟨Eν⟩~6 GeV | **Closest published low-recoil inclusive result.** Has xsec + error matrices. The 3D E_avail result is effectively a low-recoil measurement → primary external cross-check for the low-E_avail excess. Currently only in `sec_3d.tex:77` related-work table. |
| Bashyal et al. 2021 | 2104.05769 | Low-hadronic-recoil events to constrain flux + detector energy scale | Already cited; source of the flux↔muon-E joint block (open question #1). |
| Ruterbories et al. 2022 | 2203.08022 | QE-like νμ, simultaneous proton+lepton kinematics, 2–20 GeV | 2p2h/QE-like context; data release exists. |
| Filkins et al. 2020 | 2002.12496 | Double-differential CC-inclusive, LE ⟨Eν⟩~3.5 GeV | LE-energy analogue of the 2D measurement. |
| Cai et al. 2020 | 1910.08658 | Binding energy + transverse-momentum imbalance | Nuclear-effects/2p2h context. |
| Ruterbories et al. 2021 | 2106.16210 | Published 2D d²σ/(dpT dp∥), ME FHC — **the result this repo reproduces** | Baseline target. |

**Action taken from this catalogue:** promote 2110.13372 from table-only to a numerical
comparison against the 3D E_avail / low-recoil projection (see `3d-unfolding/` overlay
and `sec_3d.tex`). Note q3 and E_avail are related but distinct observables — the
comparison is semi-quantitative (shape/direction of the low-recoil excess), not a
bin-identical χ².

---

_Sources: arXiv:2504.06857, arXiv:2507.09582, https://minerva.fnal.gov/opendata/,
https://minerva.fnal.gov/data-release-page/ (fetched 2026-06-03)._
