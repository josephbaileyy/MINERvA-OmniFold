# Independent verification of C04 (the ν-e/IMD constraint weights) and X01 (the MINOS flux denominator)

**Verifier:** a fresh, read-only session. It wrote its own code and did not reuse the worker's scripts; those were read only to learn which input files they opened.
**Date:** 2026-10-12. **Repo:** origin/main `7edb65fa`. **MAT:** commit `35097b65ab1680db8058f9ede18fecffdc3a1ea3` on NERSC. **NERSC checkout:** `32e403b8`, used for data only.

## Verdicts

| Claim | Verdict |
|---|---|
| **C04**: the adopted 2D Flux band ignores MAT's ν-e+IMD universe weights | **CONFIRMED** |
| C04(a): MAT carries the constraint as per-universe weights on the Flux band plus a correction to the central value (CV); CalcCovMx honours the weights | **CONFIRMED** |
| C04(a): the "MAT-conformant, byte-for-byte" check would have caught missing weights | **No.** Both sides of that check were unweighted, and it ran on the sweep from before the flux fix. |
| C04(b): the publication used a constrained flux | **CONFIRMED, with one gap.** The flux block in the data release (4.01%) is consistent with a constrained flux and not with our unweighted 4.99%. Which constraint file the paper used cannot be determined from the release. |
| C04(c): the worker's numbers | **CONFIRMED.** Every number reproduces. The control reproduces 4.993% and 6.871%. |
| **X01**: `Muon_Energy_MINOS` universes should divide by Φ_MINOS,u, not Φ_CV | **CONFIRMED** |
| X01: the cross block | The adopted 6.87% **contains no** flux×muon-energy cross block, so removing it changes nothing. |

## Evidence: code paths (file:line@sha)

**Our rollup is unweighted.**
- `2d-unfolding/uq/analyze_universes.py:5-19@7edb65fa` describes the method in its docstring.
- `:258-259@7edb65fa` is the code: `Z = D - D.mean(axis=0)`, `cov = Z.T@Z/N_u`. It reads no universe weights anywhere.
- `:19` states that the total is built "minus the Bashyal flux<->Muon_Energy_MINOS cross-band block".

**MAT applies the constraint as weights, and corrects the CV.** All in MAT `35097b65`:
- `PlotUtils/FluxReweighter.cxx:335-339`: when `applyNuEConstraint` is set, `Constrainer().ConstrainHisto(...)` is applied to the ν and ν̄ flux.
- `:506`: the ME constraint file is `FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt`. The FHC-only `nu+e_ME_spectrum.txt` branch at `:508-514` is commented out.
- `PlotUtils/MnvFluxConstraint.h:247-271` (ConstrainHisto) calls three steps:
  - `CorrectFluxUniv` (`:354-391`) only calls `errBand->SetUnivWgt(univ_idx, w)`. The universe histograms themselves are unchanged.
  - `CorrectCV` (`:282-347`) multiplies the CV by (weighted mean ÷ unweighted mean of the universes), so **the CV is constrained too**.
  - `CorrectSpectatorUniv` adjusts the spectator flux bands.
- `FluxReweighter.cxx:1850-1873` (`PropagateNuEConstraintWeights`) copies the weights onto any flux histogram. It is called from `AddFluxErrorBand` (`:1743`), `CheckAndFixFluxErrorBand` (`:1763`) and `FillFluxErrorBand` (`:1797`, `:1817`).
- `PlotUtils/HistWrapper.cxx:305-320`: every event histogram's Flux band is created through `flux_reweighter(...).AddFluxErrorBand(hist)` when `UseNuEConstraint()` is set, so a standard MAT analysis carries the weights onto the cross section.
- `UnfoldUtils/MinervaUnfold/MnvUnfold.cxx:185,370,553,…` propagates `SetUnivWgts` through unfolding.
- `PlotUtils/MnvVertErrorBand.cxx:260-390` (`CalcCovMx`) computes a weighted mean and the weighted covariance Σ w (x−x̄_w)(x−x̄_w)ᵀ / Σw. `MnvH1D::GetTotalErrorMatrix` sums those per-band matrices.
- So a MAT-conformant rollup of a constrained Flux band is the weighted CalcCovMx.
- Our event loop enables the constraint: `MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp:1698` has `SetNuEConstraint(true)`.

**X01 code path.**
- `2d-unfolding/unfold_2d_omnifold_unbinned.py:1373-1389@7edb65fa`: `flux_bins` comes from the CV, and only `universe_branch[0] == "Flux"` swaps in Φ_u. Every other band, `Muon_Energy_MINOS` included, divides by Φ_CV.
- In the event weights, `MAT-MINERvA/weighters/Model.h:66` returns `weight * univ.GetWeightRatioToCV()`. `MAT-MINERvA/universes/MuonSystematics.cxx:188-204` returns `GetSysUniFluxWeightCorrection(..., "Muon_Energy_MINOS", universe)` (the call is at `:202`; the same call appears at `:184` in `GetFluxAndCVWeight`).
  - `FluxAndCVReweighter.h:27-33` itself uses the plain CV flux weight. The correction therefore enters only through `GetWeightRatioToCV`, but it does enter.
- `FluxReweighter.cxx:997-1030` implements the correction for Eν < 15 GeV.
- MAT's flux integral has the matching universes under `use_muon_correlations` (`FluxReweighter.cxx:1360-1398`): (∫sys/∫cv) × Φ_CV(<15 GeV) + Φ_CV(>15 GeV).
- `MINERvA-101-Cross-Section/util/GetFluxIntegral.cpp:25-29` sets `useMuonCorrelations = true`. The per-playlist flux MnvH1Ds carry `Muon_Energy_MINOS` as a vertical band.

## Evidence: NERSC inputs (sha256 re-measured)

- **CV** `…/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root`: `4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c`
- **Universe covariance** `…/uq/universe_stage2_MEFHC_full_matcorr_fluxfix_vl170/uq_universe_covariance_full_matcorr_fluxfix.root`: `077912e3e7a53376c6df89ee1af4a2a504fe1f49423bab88780204beccd952f5`. This matches the pin in `docs/orchestration/state/ki84-adopt-20261006/sha256sums_2d-unfolding_uq.txt`.
- **Bootstrap** `…/uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root`: `71a75821ceeb658710adca30243e39e7184e33f868f58ea56cffe63ba8db0115` (matches the pin).
- **ML** `…/uq/seedscan_lgbm_ml/uq_covariance_ml.root`: `3b6b48ec89207ae29dc7bb0ddc5a41836c359c4805877d663731694b828d5db9` (matches the pin).
- **Combined flux band** `…/baseline_flux/flux_integral_universes_MEFHC.root`: `5eecae84509ba8ededbe8fdee63508d8e36cd057cc0547a940383f80248580eb`.
- **Constraint file** `…/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt`: `e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2`.
- **Per-playlist flux files** `…/baseline_flux/runEventLoopMC_{1A..1P}.root`. Examples: 1A `d54d2a2c…1107`, 1P `3d98169a…77f3`. All 24 MC and Data digests are in `verify_c04.json`.
- **Universe outputs**: 187 files in `…/uq/universe_sweep_fluxfix/`, covering 44 bands and 205 reported cells.
  - sha256 of the concatenated Flux file shas: `39eca81f…dcdc7f`.
  - sha256 of the concatenated MINOS file shas: `519b2b43…dc763`.

**Weights.**
- The Flux band of every per-playlist `pTmu_reweightedflux_integrated` carries `GetUnivWgts()`, and the weights are identical across the 12 playlists.
- They equal the first 100 `Flux` entries of the constraint file exactly (maximum absolute difference 0.0).
- Range 1.06e-5 to 26.95; Σw = 211.0; **effective number of universes n_eff = 19.1**.

**The flux integral itself (POT-combined).**
- Unweighted universe mean / CV = **1.0489**. Weighted mean / CV = **0.99968**. The CV is the constrained flux.
- σ: weighted **3.526%**, unweighted with mean-centring **5.157%**, unweighted with CV-centring 7.109%.
- MAT `CalcCovMx` on a freshly built MnvH1D gives the same: 3.526% with weights, 5.157% without. On 1A's stored band it gives 3.533%.
- `hFluxUniv`/`hFluxCV` match my combination to 1.7e-16.

## Numbers: mine against the worker's

| Quantity | Worker | Mine |
|---|---|---|
| Flux band per-cell median, unweighted | 4.993% | **4.993%** |
| Flux band per-cell median, weighted | 3.65% | **3.655%**; MAT `GetTotalErrorMatrix` with the weights also gives 3.655%, and agrees with numpy to 1.1e-15 |
| Flux band minimum, unweighted → weighted | — | 4.78% → 2.97% |
| Flux band maximum, unweighted → weighted | — | 12.81% → 13.40% |
| Integral σ, unweighted → weighted | 4.89% → 3.56% | **4.893% → 3.557%** |
| Universe mean/CV, per-cell median, unweighted → weighted | 0.957 → 1.0015 | **0.9565 → 1.0015**; integral 0.9562 → 1.0015 |
| CV-centred flux band median, unweighted / weighted | — | 6.64% / 3.69% |
| MAT CalcCovMx flux-integral σ, weighted / unweighted | 3.53% / 5.17% | **3.526% / 5.157%**. The small gap on the unweighted figure is probably per-playlist vs POT-combined; I did not check this. |
| Φ_MINOS,u / Φ_CV (u0 = −1σ, u1 = +1σ) | 1.000419 / 0.995353 | **1.0004186 / 0.9953532**; per playlist the ratios agree to within 1e-6 |
| MINOS band per-cell median, adopted → corrected | 2.305% → 2.281% | **2.305% → 2.281%** |
| MINOS integral σ, adopted → corrected | ~0.11% → ~0.37% | **0.113% → 0.367%** |
| MINOS integral shift (u0, u1), adopted → corrected | — | (−0.169%, +0.058%) → (−0.210%, +0.525%) |

## Control

My own per-band mean-centred covariances on the adopted inputs reproduce the adopted product:
- The universe total matches `hCov_universe_total` to **5.2e-17** (maximum relative difference).
- The worst per-band block differs by 1.4e-6 relative to its own maximum. My inference, not checked, is that this comes from the near-null `EtaNCEL` band, whose √tr is about 1e-51.
- `hCov_combined` equals universe + bootstrap exactly.
- The adopted total equals the sum of its stored per-band blocks plus the normalization block exactly (difference 0.0).

The reproduced figures:
- Flux band median **4.993%**.
- `Muon_Energy_MINOS` median 2.305%.
- Universe+normalization median 6.830%.
- Total C_univ+norm + C_boot(VL170) + C_ML, divided per cell by the CV: median **6.871%**, which matches the quoted 6.87%.
- Integral σ of that total: 5.391%.
- Bootstrap median 0.674%; ML median 0.166%.

## Diagnostic budget table — NOT QUOTABLE (DIAGNOSTIC)

This is a per-cell recomputation over 205 cells. Only the Flux and/or MINOS blocks are swapped; everything else is the adopted construction.

| Variant | Flux median | MINOS median | Systematics median | **Total median** | Total p84 | **Total integral σ** |
|---|---|---|---|---|---|---|
| Adopted: unweighted flux, MINOS ÷ Φ_CV | 4.993% | 2.305% | 6.830% | **6.871%** | 9.50% | **5.391%** |
| C04: weighted flux only | 3.655% | 2.305% | 6.007% | **6.090%** | 9.08% | **4.216%** |
| X01: MINOS ÷ Φ_MINOS,u only | 4.993% | 2.281% | 6.890% | **6.934%** | 9.48% | **5.403%** |
| C04 + X01 | 3.655% | 2.281% | 6.043% | **6.090%** | 9.02% | **4.230%** |

The X01 row's total median rises slightly even though the MINOS median falls. That is a property of taking the median of per-cell sums, not an error.

The weighted band uses n_eff ≈ 19 universes, so its own sampling scatter is roughly ±16% relative on σ (a rough estimate). That is MAT's convention, not a defect of the recomputation.

## What the "MAT-conformant, byte-for-byte" verification covered

- **Where it is claimed:** `docs/analysis-note/app_statmethods.tex:364-369` (in `sec:minerva`) and `:817-818`, and `2D_OMNIFOLD_STUDY_STATUS.md:103-105`. The record is `2d-unfolding/uq/matcorr_vs_mnvh1d.txt`, produced by `uq/verify_matcorr_vs_mnvh1d.py` in commit `b480c261` on 2026-05-28.
- **What it compared:** a fresh `PlotUtils::MnvH1D` built with `AddVertErrorBand(band, N_u)` (`verify_matcorr_vs_mnvh1d.py:108`). **`SetUnivWgts` is never called**, so MAT ran its unweighted path. That was compared with our `--add-norm 0` rollup. Both sides were unweighted, so the check proves only that the formula is identical (mean-centred, 1/N, block sum). **It could not have detected unweighted-vs-weighted universes.** My run shows MAT's own `GetTotalErrorMatrix` moves from 4.993% to 3.655% once the weights are set.
- **Which sweep it ran on:** the pre-fix sweep. The default `--python-cov` is `universe_stage2_MEFHC_full_matcorr/` (`:63`), and the record's √tr of 2.391e-39 equals the pre-fix matcorr total (2.463e-39, sha `4cfc35b4…`) with the normalization block removed. The adopted fluxfix product without normalization has √tr 3.159e-39. **The fluxfix product that is actually quoted was never compared against MAT.**
- **A smaller wording problem:** "max element-wise rel diff 5.5e-17" is really max|diff| ÷ max|cov|, not an element-wise relative difference.
- **A false claim in the status doc:** `2D_OMNIFOLD_STUDY_STATUS.md:154` (and `2D_VALIDATION_FOR_3D.md:92`) says ours and the paper's flux are "both ν-e-constrained". That is false for our band: only the CV flux is constrained. The universe spread is unweighted, and it is centred on a mean that sits 4.9% (flux integral) or 4.4% (cross section) away from the CV.

## Published-side answer

My own parse of `2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV_flux.txt` (sha `a2ba53fd15214370…`, 205 reported cells):
- Flux median **4.014%**, floor 3.900%, maximum 7.13%, integral σ **4.002%**. The block is rank-1 to within 0.04% of its trace.
- The total block has median 6.859%, matching the paper's 6.85%.

The paper's Section V, as quoted in the note at `app_statmethods.tex:336-337`, says the flux uncertainty is "below 4% … thanks to the ν-e-scattering constraint" (Valencia 2019). I did not open the paper PDF myself.

**So the publication used a constrained flux.** Its flux component, 4.01% per cell and 4.00% integral, is incompatible with our unweighted 4.99% (6.64% if CV-centred). It lies between our unweighted figure and our FHC+RHC+IMD-weighted 3.65%.

Why the weighted figure is lower than the published one is still open. The leading inference: MAT `35097b65` loads the combined FHC+RHC+IMD constraint, while a 2021 paper citing Valencia 2019 most likely used the FHC-only ν-e constraint, which is looser. The scatter from n_eff ≈ 19 is also comparable to the gap. The release does not record which constraint file or PPFX version was used, so that point is undeterminable from what is in the repo.

Either way, our band is **not** MAT-conformant: it neither weights the universes nor centres them on the constrained CV.

Aside, not part of this claim: the data-release README cites "Phys.Rev.D 104 (2021) 092007", while `2D_OMNIFOLD_STUDY_STATUS.md` cites PRD 106, 032001.

## Cross block (X01 note)

- The adopted product has no cross-block key, and its total equals the sum of its blocks exactly.
- `rederive_flux_muonE_cross.py` reads the pre-fix `universe_stage2_MEFHC_full_matcorr` product, and nothing in the rollup chain consumes its output.
- **So the 6.87% does not include the ρ=0.900 block, and "removing it" does not apply.**
- MAT's own way of carrying the flux↔muon-energy correlation is the X01 correlated-flux universes. Adding the paper-derived ρ=0.900 block on top of an X01 repair would double-count.
- For information only: adding a route-B rank-2 ρ=0.9 block to the adopted total gives a median of 6.56% and an integral of 5.63%. This depends on the sign convention and is not meaningful for the construction.

## Repair cost

**Both repairs are cheap; no re-unfold is needed.**
- **C04:** the weights are per-universe constants on the band. The universe histograms, and the CV that is already constrained, are exactly what MAT uses. Recompute the Flux block as a weighted CalcCovMx from the 100 existing `universe_sweep_fluxfix` Flux outputs.
- **X01:** Φ is a pure divisor (the same argument as `rescale_flux_universes.py`), so multiplying the 2 existing MINOS outputs by Φ_CV/Φ_MINOS,u (1/1.0004186 and 1/0.9953532) is exact.
- Both changes would alter quoted numbers (6.87%, the figures, the χ² values, the note text), so they need Joseph's decision. I changed nothing.

## Scratch paths

- NERSC, everything I wrote:
  - `/pscratch/sd/j/josephrb/2d-closeout-stageAB-20261012/verify-c04/verify_c04.py` (sha `b48b9e9a…12f5b6`)
  - `verify_c04.json` (sha `0a886293…b3ef`), which holds all results and every input sha256
  - `verify_c04.log` (sha `c6aeab5a…208e`)
  - `followup.py`, which identified the sweep behind the verification record
- Local: `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/42670017-c41b-4c65-9b50-994312a5d203/scratchpad/vc04/`, holding `paper_flux.py`, `verify_c04.py` and `followup.py`.
- Login node only; no Slurm job.

## Worktree status

- `/private/tmp/claude-501/verify-c04-wt`, detached at `7edb65fa`: clean at start and clean at end. It has been **removed**.
- Main checkout `/Users/josephbailey/local-research/MINERvA-OmniFold`: unchanged from the session start (the same 3 modified orchestration files and the same untracked files).
- NERSC checkout at `32e403b8`: unchanged.
- Nothing was edited, committed or pushed.