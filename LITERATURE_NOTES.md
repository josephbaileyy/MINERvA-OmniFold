# Literature & open-data notes (OmniFold + MINERvA)

Reference notes captured during the 2026-06-03 analysis audit, so future work does
not have to re-derive them. Two threads: (A) the OmniFold / unbinned-unfolding
literature (the 2025 method papers + the broader ML-unfolding family and experimental
landscape) and how this analysis compares; (B) the MINERvA open-data and data-release
catalogue, including the full low-recoil / 2p2h lineage behind the headline result.
Scope note: §A's "what the 2025 references recommend" and the audit-finding subsections
go deep on the two method papers (that was the audit's focus); the landscape and MINERvA
catalogue subsections were broadened on 2026-06-03 for completeness.

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

### Key reference (2026) — the first LHC full-phase-space measurement

**Greif, *A High- and Variable-Dimensional Measurement of the Z+jets Differential Cross
Section with the ATLAS Experiment and Artificial Intelligence*, PhD thesis (UC Irvine),
`arXiv:2608.28449`, submitted 28 Aug 2026, 313 pp.** Read and extracted 2026-09-01.
ATLAS Z(→μμ)+jets unfolded differential in the full phase space of every final-state
charged particle: **6 min / 843 max / 150 mean dimensions per event**, 140.1 fb⁻¹, 247k
selected data events. Supersedes the 24-observable Multifold round (`ATLAS:2024jets`).

> **CITABLE FOR** method, construction, prescription and qualitative results.
> **NOT CITABLE FOR** approved ATLAS numbers. §6.1 (p. 172): the analysis is *in ATLAS
> review*, the paper is *expected September 2026*, and a conference note has been released;
> Figures 6.19–6.22 are watermarked **ATLAS Internal** and 6.23–6.24 **ATLAS Simulation
> Internal**. Cite the conference note or the paper, not the thesis, for any number.

Two lane briefs carry the full extraction and the actions each implies:
[`docs/orchestration/BRIEF-20260901-greif-fps-thesis-implications-for-pet.md`](docs/orchestration/BRIEF-20260901-greif-fps-thesis-implications-for-pet.md)
(PET/FPS) and
[`docs/orchestration/BRIEF-20260901-greif-fps-thesis-implications-for-gbdt5d.md`](docs/orchestration/BRIEF-20260901-greif-fps-thesis-implications-for-gbdt5d.md)
(scalar-5D covariance). What it adds beyond the 2025 references above:

- **A complete UQ prescription for a variable-dimensional unfold** (§6.4). Every source is
  a **full OmniFold re-run from scratch** on the perturbed input; the uncertainty is the
  **signed difference** `Δ_ku = σ̂_ku − σ̂_k`; the total is the **quadrature sum over
  uncorrelated sources**. 12 experimental + 9 theoretical sources. Note this is a *block
  sum over sources*, not a unified throw — cross-source correlation is dropped by
  assumption.
- **Lateral/vertical in their vocabulary** (§6.4): experimental uncertainties *"do not
  shift the particle-level quantities"* → uncertainties on the (unbinned equivalent of the)
  response matrix; theoretical ones are *"a shift in the particle-level prior."* Their claim
  worth having on file: *"unfolding is broadly insensitive to choice of prior so the theory
  uncertainties are all sub-leading"*, with footnote 38 — that treatment is *"the reason
  some unfolded measurements can actually be more accurate than forward folded
  measurements."*
- **`C_ML` analogue** (§6.4.2). Ten seed-varied OmniFold runs; **the central value is the
  event-by-event mean over the ten**; the uncertainty is the **std of bin counts** across
  them; **per-member binning for the nominal only** — systematics use mean weights. Because
  the nominal *is* the ensemble mean, it cannot sit outside its own family, and
  mean-centering vs CV-centering coincide. Third independent instance of the ensemble-mean
  convention this file already recommends (see the ensemble-mean audit finding below), and
  the first to carry the systematics rule.
- **ML noise is reducible, not a fixed tax** (§6.3.2). Pretraining ParT on an auxiliary
  MC-vs-MC task (~14M events, ten independent checkpoints per level) took the ensemble from
  **100 members to 10** and cut the method bias *"dramatically … especially in the tails"*.
  Their assessment: without it the method bias is *"likely too large to make a publishable
  measurement"* in some observables.
- **Statistical uncertainty** (§6.4): Poisson(λ=1) multiplication of event weights, **100**
  replicas for data stat and **25** for MC-training stat; the uncertainty is *"the variance
  in the result produced by this ensemble of bootstraps."* **No** treatment of a
  nominal-to-bootstrap-mean offset and **no** centering diagnostic anywhere — five mentions
  of "bootstrap" in 313 pages. Nothing here bears on the `OI-126` **ruling** — but the coverage
  finding above does constrain how the coverage condition for any future reconsideration is
  DESCRIBED: that bar is above field practice, not a deficiency measured against it.
- **`OmniSequential`** (§6.4, pp. 208–209): a deliberately **non-ML** Gaussian-kernel
  reweighter (Scott's-rule binning, log binning above skewness 2, pick the worst
  `z = (χ² − ndof)/√(2 ndof)`, iterate to `z < 2` on all observables), built *"to avoid
  over-reliance on ML based likelihood ratio estimation techniques."* It is what constructs
  both of their unfolding uncertainties — i.e. they refuse to estimate an ML method's bias
  with the same ML machinery.
- **Hidden-variable uncertainty recipe** (§6.4.1): reweight the alternative generator's
  *particle level* to the nominal's *particle level* in observables that are functions of
  the phase space the unfold already sees, so only genuinely hidden variables survive; then
  re-unfold and difference.
- **The high-dimensional hidden-variable advantage was tested and DID NOT HOLD** (§6.4.1,
  §6.5.2): *"naively an Omnifold based measurement should be less sensitive to hidden
  variables … but this expectation is not borne out."* Their hidden-variable uncertainties
  came out slightly **larger** than 1D IBU's. Causes: OmniFold is data-limited in tails
  (the step-1 networks train on data; IBU bins over them), and the dominant hidden variable
  — truth π/K/p fractions, unconstrained at detector level under the pion-mass assumption —
  stays hidden at full phase space (Fig. 6.20: the unfold returns the prior *exactly*).
  Net (§6.5.3): full phase space cost *"almost no reduction in precision"* vs 24-D — a tie,
  not a gain. **The defensible motivation for FPS is flexibility and information
  preservation, not hidden-variable immunity.**
- **The validation instrument** (§6.5.1): binned χ² vs pseudodata truth **using the full
  covariance**, across **26 observables**, p-value each — it *"allows the method bias and
  uncertainty model to be jointly assessed."* Three details: **exclude from Σ any systematic
  held at nominal in the pseudodata** (they drop the experimental block); Gaussian-smooth a
  band built from an independent sample before it fills Σ, **except** where the band has real
  sharp structure (jet mass, exempted and documented); judge on the correlated χ², not per
  bin (their `mj1` has method bias above total uncertainty in several bins and still returns
  p ≈ 0.26). All 26 clear p > 0.05, minimum 0.0556. *(Table 6.3 is internally consistent:
  five p-values recomputed from its own χ² and DoF reproduce to four decimals.)*
- **A release protocol for an unbinned product** (§6.7), which is the practical answer to
  the unbinned-GoF open problem below — not a solution to it. The public spectra ship with
  two binding usage requirements: **≥5,000 effective events in every bin** of any histogram
  a user builds, and **the user must re-run the pseudodata measurement and compute a χ²/p in
  their own binning and phase space.** Rationale: observables sensitive to unconstrained
  truth-level information *"will fail this check, indicating that the observables cannot be
  constrained with this measurement."* An unbinned result cannot be certified once, so they
  ship the test as an obligation on the consumer.
- **Classifier choice** (§5.6.3): *"Neural networks … are not required and may even be
  sub-optimal. Simpler and computationally cheaper methods such as boosted decision trees
  can also be used to estimate likelihood ratios"* — scoped to *"low- and fixed-dimensional
  measurements."* External support for the LightGBM choice; see the GBDT/NN audit finding
  below. **The scope clause is load-bearing: it does not reach the full-event PET case.**
- **ParT vs PET, head to head** (§6.3.1): they benchmarked ParT, PET, L-GATr and LundNet and
  chose ParT — *"ParT has overall better performance especially in the `Nch` observable.
  Notably PET is more accurate in the `mj2` observable"*, plus faster training. A split
  decision, not a refutation of PET. **The transferable part is the criterion: they ranked
  architectures by method bias in the unfolded observables, not by classifier AUC.**
- **Nobody is doing a coverage study, including them.** `coverag` appears **once** in the
  whole thesis and it is about detector acceptance in the forward region. §6.5.1: *"running
  sufficient bootstraps to observe this is computationally infeasible"*, so they use the
  asymptotic χ² and a p-value. *(Covering control run 2026-09-01, because a
  null over a PDF is a claim about the extraction until proven otherwise: **313 form-feed page breaks
  for 313 pages**, **88 figure captions resolve with their body text**, and single-occurrence body
  terms DO resolve at comparable rarity — `skewness` 1, `pion mass` 2, `Scott` 2, `843` 3.
  Figure-IMAGE text is still unseen, but would not carry a coverage study.)* This does not make the coverage
  demand on `C_stat` wrong — it calibrates it as a standard **above** current field practice
  rather than a gap relative to the literature.
- **First explicit background subtraction in an unbinned measurement** (§6.3.3): *"This is
  the first unbinned and high-dimensional cross section measurement to explicitly subtract a
  background."* A classifier separates detector-level data from itself with the background
  MC appended at **negative weight**, estimating `p_{D−B}(x)/p_D(x)`. **This is the same
  construction as our `app:negweight`** and it means `sec_method.tex`'s survey of background
  handling is now dated — filed as `OI-183`.
- **Open problems they name** (§6.7): acceptance effects in unbinned unfolding when the
  selection involves jets (*"proposed … but have not yet been applied in a real analysis"*),
  and cost — **~25,000 transformer fine-tunings, ~400,000 A100 GPU-hours**, as stated.
- **Census (Table 5.1)** — twelve unbinned-unfolding measurements, all OmniFold. **Six are
  absent from `technote.bib` and from this file**: ATLAS dijets `2502.02062`, CMS min-bias
  `2505.17850`, H1 `2412.14092`, STAR `2307.07718` and `2403.13921`, ALEPH `2507.14349`.
  Filed as `OI-184`. **MINERvA does not appear** (correctly — unpublished), and **T2K
  `2504.06857` is the only neutrino entry**, but Greif's table lists it among *experimental*
  measurements while this file and `sec_method.tex` describe it as a **mock-data** study on
  public ND280 simulation. That classification conflict touches our precedence claim and is
  part of `OI-184`; his table is *"adapted from Ref. [208]"* (the Practical Guide), so the
  label may propagate from there rather than originate with him.
- The world-record dimensionality before this measurement is a **preliminary H1 full-phase-space
  DIS result** reaching *"a few hundred"* dimensions (their Ref. [82], no arXiv id given).
  Every other entry in Table 5.1 is Multifold — a fixed-length list of 4 to 24 observables.

### Broader OmniFold / ML-unfolding landscape

OmniFold (full event as input) vs MultiFold (a chosen observable set) vs UniFold (one
observable); all iterate the same two-step classifier reweighting. Surrounding method
family (all in `technote.bib`, none previously summarized here):
- **Scaffolding simulations with deep learning** — Andreassen et al. **arXiv:2105.04448**
  (high-dimensional deconvolution; the deep-learning scaffolding behind OmniFold).
- **Generative / likelihood-free unfolding alternatives**: GAN unfolding
  **arXiv:1806.00433**; "How to GAN away detector effects" **arXiv:1912.00477**;
  invertible networks **arXiv:2006.06685**; conditional INN iterative unfolding
  **arXiv:2212.08674**; **unbinned profiled unfolding** **arXiv:2302.05390** (folds in
  nuisance-parameter profiling — relevant to the rank-deficient-covariance / GoF problem).
- **Classical binned context** (what OmniFold replaces): D'Agostini IBU, SVD
  (hep-ph/9509307), TUnfold (arXiv:1205.6201), RooUnfold (arXiv:1105.1160).

Experimental maturity (per the Practical Guide synthesis): H1 pioneered OmniFold on real
data (DIS, the two H1 refs above); the original paper demonstrated it on an LHC
jet-substructure example; **T2K (arXiv:2504.06857) is the first neutrino application**, and
the Practical Guide collects real-data results across major experiments from ~2021–2025.

> **UPDATED 2026-09-01 from `arXiv:2608.28449` Table 5.1.** The census is now **twelve**
> measurements, all OmniFold, and six of them are cited nowhere in this repo (see the 2026
> key reference above; filed as `OI-184`). Two corrections to the sentence above: the
> highest-dimensional result is a **preliminary H1 full-phase-space DIS** unfold at *"a few
> hundred"* dimensions, and as of Aug 2026 **ATLAS has an unpublished full-phase-space
> Z+jets measurement at 843 dimensions**. **T2K remains the only neutrino entry**, but
> Greif's table classes it as an *experimental* measurement where this file calls it a
> mock-data study on simulation; that conflict is unresolved here and bears on our
> precedence claim.
This analysis is, to our knowledge, the **first OmniFold application to MINERvA / to a
muon-kinematics + available-energy 3D neutrino cross section**.

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
- **UPDATED 2026-09-01.** Still open, and `arXiv:2608.28449` does not solve it either —
  it uses the binned χ² and states a true frequentist check is computationally infeasible
  (`coverag` appears **once** in 313 pages, about detector acceptance). What it adds is a
  practical route *around* the problem: run the binned χ² in **many projections** (26), and
  **ship the test as an obligation on the consumer** of the unbinned product rather than
  certifying the product once. See the 2026 key reference above.

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
**UPDATED 2026-09-01: there is now an EXTERNAL answer too.** `arXiv:2608.28449` §5.6.3
states that NNs *"are not required and may even be sub-optimal"* for likelihood-ratio
estimation, and that *"boosted decision trees can also be used"* — scoped to *"low- and
fixed-dimensional measurements."* That scope clause fits the scalar unfolds and
**deliberately does not reach the full-event PET case**.

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

### Low-recoil / 2p2h lineage (the physics behind the headline result)

The 3D headline — a low-E_avail excess filled by 2p2h — sits in a well-established MINERvA
low-recoil program that the original notes omitted:

| Release | arXiv | Why it matters here |
|---|---|---|
| **Rodrigues et al. 2016** (PRL 116 071802) | **1511.05944** | **The seminal MINERvA low-recoil paper** — first isolated, in the low-q3 subsample, the event-rate excess between the QE and Δ peaks with enhanced multi-proton final states, i.e. the **2p2h/screening signature** that motivated the MINERvA empirical low-recoil tune. This is the direct ancestor of our low-E_avail finding. **Data release**: arXiv anc `src/1511.05944v3/anc` + https://minerva.fnal.gov/nuke-eff-nu-c-int-at-low-q/. **Added 2026-06-03** to `technote.bib` (key `MINERvA:2016lowrecoil`) and cited in `sec_3d.tex` §2p2h. |
| Ascencio et al. 2022 | 2110.13372 | The ME follow-up of 1511.05944 (d²σ/dq3 dE_avail); already the primary external cross-check above. |
| MINERvA 2023 (Henry, Su et al.) | 2312.16631 | e-ν / e-ν̄ at low momentum transfer — **the source of our available-energy definition** (Eq. 4; memory `ref_minerva_eavail_definition`). Already in bib; not previously in these notes. |
| MINERvA 2024 (multi-neutron ν̄μ CC) | 2310.17014 | Antineutrino **low-E_avail** measurement — the RHC analogue of our low-recoil excess. In bib. |
| Bashyal et al. 2021 | 2104.05769 | Low-recoil events used to constrain flux + muon-E scale (the Bashyal joint block, open question #1). |

Other MINERvA differential measurements in `technote.bib` (broader context, less directly
comparable): pion production 1406.6415 / 2209.07852; QE-like / TKI 1801.01197, 1910.08658,
2203.08022; A-dependent TKI 2503.15047. The flux/detector references are NuMI flux
1607.00704 and the MINERvA NIM/detector papers (1305.5199 etc.).

---

## C. Recommended pre-publication methodology studies (open, user-flagged 2026-06-03)

The audit changes already landed are validations/refinements, not fixes. Four
methodology items remain worth deciding on *before* publication. None blocks the present
result; each tightens a defensible-but-assumed choice. Listed in rough priority.

> **STATUS (2026-06-04 follow-on campaign — see `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md`):**
> - **#1 (unified-throw)** — actioned as a superposition cross-check
>   (`nd-unfolding/compare_unified_throw.py`): the cross term Δ_AB−(Δ_A+Δ_B) from
>   re-unfolded vertical-band shifts directly measures the nonlinearity the block sum
>   drops. Compute in flight (MaCCQE/2p2h/MaRES on the 120 GB 3D universes omnifile).
> - **#2 (train/test-split seedscan)** — **DONE**. `omnifold_loop` gained
>   `train_frac`/`split_seed`; the split ML band is **1.24× the seed-only band**
>   (`nd-unfolding/uq_cov_mlsplit_3d.root`). Folded into the combined budget it shifts the
>   total only **+0.04%** (ML is sub-dominant), so the larger, honest band is essentially
>   free — adopt it. Ensemble-mean CV == frozen CV.
> - **#3 (unbinned GoF)** — **DONE**. Classifier two-sample test
>   (`nd-unfolding/unbinned_gof.py`): the CV prior is separable (z=33) but the unfolded
>   result is indistinguishable from data (AUC 0.501, z=1.4, **p=0.17**) — the unbinned
>   GoF is sensitive and passes, complementing the binned χ².
> - **#4 (more dimensions)** — q3 4D done + validated (Phase 1); q3 systematic campaign
>   in flight (`ND_OMNIFOLD_STATUS.md`).

1. **Covariance construction — unified-throw cross-check of the block-sum.** We report
   `C = C_syst + C_stat + C_ML`, summing independently-generated blocks (MAT convention;
   defensible because the RNG streams and sources are independent). This *assumes the
   unfolding response is linear in the nuisances* — i.e. that propagating stat and syst
   *jointly* through the unfolding in each throw would give the same covariance as summing
   them separately. **Study:** run a single unified-throw covariance (perturb syst
   universe + Poisson stat + ML seed together in each of ~200–500 throws, re-unfold each,
   accumulate one covariance) and compare to the block-sum, per-bin and by leading
   eigenmode. Agreement → block-sum is vindicated and becomes a *measured* fact, not an
   assumption; disagreement localizes the nonlinearity. This is the single item most
   likely to draw a referee question (see the comparison table, §A — "Covariance" row).

2. **Seed scan that also varies the train/test split.** The current 10-seed scan varies
   only the classifier `random_state`, so the ML band (0.14–0.45 %/bin) is a *model-init
   lower bound* on the true ML stochasticity (see §A ensemble-mean finding,
   `2d-unfolding/uq/ensemble_mean_cv.py`). **Study:** extend the scan so each seed also
   redraws the train/test partition (k-fold or fresh random split). This converts
   `C_ML` from an init-only proxy into the full ML stochasticity and lets the ensemble
   *mean* be quoted as the central value with a defensible spread (T2K / Practical Guide
   ensemble convention). Cheap: reuses the existing seedscan harness, no new event loop.

3. **Unbinned goodness-of-fit.** Our GoF is the binned truncated-spectral χ² on the
   rank-deficient covariance (open questions 4–5). The Practical Guide (2507.09582) flags
   a *binning-independent* GoF as the right object for unbinned unfolding and an open
   problem — candidates: a classifier two-sample test (train a discriminator on
   unfolded-weighted MC vs. data-pushed events, report AUC / its permutation null),
   sliced-Wasserstein distance, or an energy/MMD statistic with a permutation p-value.
   **Study:** compute one such metric on the unfolded weighted sample vs. the truth-MC
   prediction, as a cross-check on the binned χ² tension. This is genuinely novel
   territory (no MINERvA precedent), so frame it as a method contribution, not a
   requirement.

4. **More dimensions? — qualified yes, but motivate per-axis; don't go wide for its own
   sake.** OmniFold's structural advantage is exactly that adding an observable = adding a
   feature, with *no* IBU/D'Agostini analogue — so a 4th axis is the natural showcase and
   costs almost nothing in the unbinned step. The cost is downstream: the *reported binned*
   product and its covariance grow combinatorially (3D is already 1431 bins, rank 247/1431
   — the covariance is mostly null space), MC stats thin out per bin, and each new axis
   needs its own truth/reco accessor + closure + binning study. **Recommendation:** add a
   4th axis only with a *specific physics question* it answers, not for dimensionality's
   sake. The best-motivated candidates, in order: (a) **q3 / 3-momentum transfer** — would
   make the Ascencio low-q3 comparison (§A) bin-identical instead of a mapped cross-check,
   directly sharpening the 2p2h narrative; (b) **hadronic-system angle or proton
   multiplicity** — separates 2p2h from RES/DIS in the high-E_avail DIS-tail excess (open
   question 6), which the current axes cannot resolve. A blind 4th axis (e.g. another
   kinematic projection) adds bins and covariance null space without buying physics —
   skip it. Practically: keep the *unbinned* unfold high-dimensional, but only *publish*
   a binned projection along axes with a question attached.

5. **Is a hyperparameter search worth it? (user-flagged 2026-07-03, advisor-comment
   session).** Production HPOs are sklearn `GradientBoosting` defaults at matched
   capacity across backends (100 trees, lr 0.1, depth-3 / `num_leaves=8`), fixed a
   priori with no search — now stated openly in the analysis note (sec_method
   "Hyperparameter choice"). **Study:** a small, closure-driven (never data-driven)
   search — vary capacity (leaves/depth), tree count, and learning rate on the
   simulation-only closure + calibration + coverage suite, and check whether the
   optimum moves the data result by more than the seedscan band. If it does not
   (expected, given the 0.026% iteration-doubling and backend-agreement stability),
   the defaults are vindicated and the note gains a sentence; if it does, the tuned
   config needs its own validation pass. Cheap on the 2D/3D chain (CPU LightGBM);
   keep the search metric strictly simulation-side to preserve the no-tuning-on-result
   property.

---

_Sources: arXiv:2504.06857, arXiv:2507.09582, arXiv:1911.09107, arXiv:1511.05944
(PRL 116 071802), https://minerva.fnal.gov/opendata/,
https://minerva.fnal.gov/data-release-page/,
https://minerva.fnal.gov/nuke-eff-nu-c-int-at-low-q/ (fetched 2026-06-03).
Cross-checked for completeness against the `technote.bib` citation set._
