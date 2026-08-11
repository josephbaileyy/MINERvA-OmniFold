# 1D IBU on a 1D projection of the 2D OmniFold inputs

> **Phase-16 update (2026-05-10).** The post-fix re-run answers this
> cross-check definitively: with the input-completeness correction
> applied to both pipelines, IBU and 2D-OmniFold each reproduce the
> paper to within ≤ 2.5 % and agree with one another to ~1.7 % (post-fix
> integrals: paper 3.039e-38, OmniFold-2D 3.054e-38 / ratio 1.005, IBU
> 3.003e-38 / ratio 0.988 on p_T, 2.965e-38 / 0.976 on p_||). The
> residual the cross-check was set up to localise was an
> input-completeness correction shared by any pipeline that builds an
> efficiency from `mc_signal_reco`; it was **not** method-specific to
> OmniFold. The "method-blind" interpretation row of the table at the
> bottom is the correct one — both methods now agree with the paper.
> The slide-5 flux-CV hypothesis was independently ruled out in
> Phase 15.

> **Error budget for the POT scale used here (PB5, 2026-08-10).** This chain inherits
> `KNOWN_ISSUES` J36: `build_1d_ibu_inputs.py` reads `hadd`-summed `dataPOTUsed`/`mcPOTUsed` from
> the merged MEFHC omnifile, rewrites them as a single `POTUsed`, and
> `ExtractCrossSection.cpp:225` forms `-dataPOT/mcPOT` from them — a global ratio where the
> per-playlist ratios span **0.1707–0.2371** (`max/min − 1 = 38.90 %`, POT-weighted mean absolute
> mixture error 9.4 %). **The numbers above are quoted with that defect present.**
>
> **Measured, not argued:** comparing `R_glob·Σ_p MC_p` against `Σ_p R_p·MC_p` over the twelve
> per-playlist event-loop outputs, on the analysis' own edges, the reco **shape** changes by at
> most **0.073 % in pT and 0.143 % in p∥** (0.032 % across the low-pT ridge), with the residual
> **+0.119 %** appearing as normalisation rather than shape. The twelve playlists are nearly
> shape-identical in reco pT, so a large reweighting of them is almost pure normalisation.
> Derivation and per-bin table: `VALIDATION_LEDGER.md` (2026-08-09, VERIFIED-NUMERIC).
>
> **Consequence for the integrals above:** the quoted headline is *integrals*, which this defect
> does not bias — J36 is a mixture error and leaves the total unchanged — and the OmniFold-vs-IBU
> agreement carries the *same* global scale on both arms, so it cancels there as well. The
> ≤ 0.15 % bound is therefore an upper limit on a quantity that is already twice-suppressed for
> these particular numbers. It is stated anyway so the claim carries its own error budget rather
> than resting on a reader knowing J36.
>
> **This is bounded, not fixed.** The correct treatment is per-playlist scaling; that repair is one
> of nine sites in the class (`FINDING-20260809-derived-from-merged-extensives.md`) and is not
> scheduled pre-publication. Note also that this bound is a **deterministic recomputation on
> frozen inputs**, not a single draw from a distribution — no unfold is re-run in producing it — so
> it is not exposed to the single-draw failure mode recorded elsewhere in this campaign.

## Purpose

Run MINERvA's D'Agostini IBU on a 1D projection of the **same 2D OmniFold
inputs** that drive the production 2D unfold, then compare to the paper's 1D
projection and to our own 2D OmniFold result projected to 1D. Cross-check
asked for by advisor after seeing the slide deck: localises the residual
low-p_|| deficit to either the unfolding method (2D OmniFold-specific) or
upstream (Φ · N_T · ε / truth-weight side, i.e. the slide-5 flux-CV story).

This is **not** the same as `unbinned_1d_study/`. That directory runs the
educational MINERvA-101 1D event loop (`runEventLoop`) on playlist 1A. This
directory uses the actual 2D production event-loop output
(`runEventLoopOmniFold_MEFHC.root`, all 12 ME FHC playlists) and projects
it; the selection, MINOS-fix patch, reweighters, POT, and phase space are
byte-identical to the 2D production.

## Method

1. `build_1d_ibu_inputs.py` — reads the 2D OmniFold TTrees (`data`,
   `mc_signal_reco`, `mc_background`, **and `mc_truth_denom`**) and
   projects each event onto p_T and p_|| paper edges. Writes
   MnvH1D / MnvH2D inputs that match `ExtractCrossSection`'s contract
   (data, migration, efficiency numerator/denominator, background+fakes,
   flux, fiducial nucleons, POT). Phase-space mask,
   fakes-into-background, and weight conventions mirror
   `unfold_2d_omnifold_unbinned.py`. Post-Phase-16, the efficiency
   denominator and the 2D truth yield used for the per-p_|| harmonic-
   mean flux are filled from `mc_truth_denom` (32.85M canonical truth
   events) — **not** from the `mc_signal_reco` truth-pass subset
   (24.5M). Filling them from the subset would drop the input-
   completeness factor c ≈ 0.745 and reproduce the pre-Phase-16
   ~25 % deficit.

2. `ExtractCrossSection 5` — D'Agostini IBU at 5 iterations (matches the
   2D production iteration count). Auto-detects both `pTmu` and `pZmu`
   prefixes from `*_data` keys and writes `pTmu_crossSection.root` and
   `pZmu_crossSection.root`.

3. `plot_ibu_1d_proj_vs_omnifold.py` — three-way overlay per axis: IBU on
   the 1D projection (this study) vs. our 2D OmniFold result projected to
   1D vs. the paper TH2D projected to 1D. Top panel = absolute, bottom
   panel = ratio to paper.

## Approximations

- **p_|| flux is scalar.** The flux file (`baseline_flux/...`) ships only
  a p_T-binned `pTmu_reweightedflux_integrated`. For the p_|| comparison
  we replicate `fluxIntegral_m2_per_POT` (the integrated flux) across all
  16 p_|| bins. This drops per-Eν shape effects of FluxAndCV inside p_||
  bins. For a 1D projection of a 2D cross section that share the same
  total flux, this is the correct denominator; per-Eν shape inside p_||
  is not the load-bearing thing for the cross-check question.
- **Stat-only IBU.** The TTrees carry only CV weights; no systematic
  universes are propagated. `ExtractCrossSection` will fill missing bands
  with the CV via `AddMissingErrorBandsAndFillWithCV`.

## Running

Submit:
```bash
sbatch sbatch_ibu_1d_projection.sh
```
or run interactively:
```bash
source ../../setup_salloc_env.sh
python3 build_1d_ibu_inputs.py --verbose
ExtractCrossSection 5 runEventLoop_proj_data.root runEventLoop_proj_mc.root
python3 plot_ibu_1d_proj_vs_omnifold.py
```

## Interpreting the outcome

| Observation                                                          | Interpretation                                                                                              |
|----------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| IBU/paper agrees within ~stat scatter on both axes                   | The 16.6 % deficit is in the 2D unfolder (training prior, iteration scheme, 2D-only systematic).            |
| IBU/paper undershoots at low p_||, same shape as 2D OmniFold         | The deficit is upstream of the unfolding method — the slide-5 flux-CV story is correct (now method-blind).  |
| IBU disagrees with our OmniFold-2D 1D projection                     | The 2D OmniFold is doing something IBU isn't on the same inputs (separate diagnostic).                      |

The expected outcome given slide 5's argument is the second row. The third
row would be a surprise and would warrant a closer look at the 2D OmniFold
training before reading too much into the flux diagnosis.
