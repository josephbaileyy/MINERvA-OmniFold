# Full-phase-space (FPS) pilot — 1A acceptance study + honesty battery

**2026-06-09.** Decision memo for extending the OmniFold measurement beyond the
published muon phase space (θ<20°, 1.5<p∥<60 GeV/c, pT<4.5 GeV/c). Pilot chain:
jobs 54232749 (build) → 54232780 (FPS 1A event loop, 1h36) → 54233015 (pilot
battery, 12 min on 16 cpus). All artifacts under `nd-unfolding/` /
`products/5d/`; figures `fps_acceptance_1A.png`, `fps_pilot_compare_1A.png`.

## What was built

- `runEventLoopOmniFold.cpp` gained **`MNV101_FULL_PHASE_SPACE`**: drops the
  four truth muon kinematic cuts from the signal definition (keeps tracker
  ZRange/Apothem). Reco selection (incl. MINOS match) unchanged; the
  truth-authoritative gate automatically reclassifies former kinematic
  "fakes" as signal and grows the miss set. Launcher
  `sbatch_evloop_1A_fps.sh` → `runEventLoopOmniFold_5D_FPS_1A.root`
  (537 MB vs 379 MB standard).
- `unfold_nd_omnifold_unbinned.py` gained additive `--pt-edges/--pz-edges/
  --full-phase-space` (θ-gate lift). Default path regression-tested (1-iter
  smoke reproduces the standard config; completeness 1.0 both paths).
  Extended grid = exact paper edges + catch bins
  (pT: +[4.5,30]; p∥: +[0,0.75,1.5] split low bin and +[60,120]).
- Flux: `pTmu_reweightedflux_integrated` is **constant in pT** (spread 2e-14%),
  so catch-bin flux is exact by bin-centre remap — no flux regeneration needed.

## Acceptance study (1A, weighted truth, ν_μ CC in tracker fiducial)

| region | share of total truth rate |
|---|---|
| inside published phase space | **66.4%** |
| p∥ < 1.5 GeV/c | 22.4% |
| θ > 20° (rectangle ok) | 11.2% |
| p∥ > 60 / pT > 4.5 tails | 0.02% / 0.00% |
| **dead cells (eff < 2%)** | **27.7%** |

The published cuts hide a full third of the rate. Efficiency is ~0.65 and flat
throughout the published region and degrades smoothly across the θ>20° wedge
(partial MINOS acceptance); the genuinely dead region is the p∥<1.5 strip and
the high-pT staircase corner. ≈6% of the total rate is **new and measurable**
(eff between 2% and the plateau); ≈28% is prior-extrapolation territory.

## Honesty battery (1A pilot unfolds, 2D (pT,p∥), lgbm 5-iter, seed 1)

1. **Anchor — PASS (decisive).** The FPS unfold restricted to the published
   phase-space sub-block reproduces the control unfold (standard omnifile,
   paper grid, same settings) to **integral ratio 0.9995**, per-cell median
   1.0005, median |ratio−1| **0.65%** over all 185 populated reported cells.
   Opening the phase space does not damage the measurement inside it.
2. **Prior swap (MnvTune-v1 prior vs bare-GENIE prior).** After correcting the
   bare-GENIE run's no-weights normalization artifact (global 1/pot_scale —
   see code-debt note), totals agree to **2.6%**, and per-cell:
   - published-PS cells: median |Δ| **3.0%**, p90 8.9% (shape-only 1.9%);
   - new/extrapolated cells: median **5.1%**, p90 **22.7%**, max 32%
     (largest in the p∥>60 catch row and high-pT column — the dead cells).
   Prior dependence is real but *quantified and localized*: small where there
   is acceptance, tens-of-percent in the dead regions.

## Recommendation: GO, with two-tier reporting

Proceed to the full 12-playlist FPS campaign with the reporting convention:

- **Tier 1 (measurement):** all cells with eff ≥ ~2% — the published region
  (anchored at 0.65%) plus the measurable extension (~6% of rate, mostly the
  θ>20° wedge and the p∥ 0.75–1.5 edge).
- **Tier 2 (prior-extrapolated):** dead cells (~28% of rate), published but
  explicitly flagged, carrying a **prior-dependence band** (the tune-vs-GENIE
  spread as the first band; the campaign should add a NuWro-shaped prior
  reweight as a third prior for a proper envelope).

This is the honest version of "full phase space": OmniFold's miss treatment
provides the extrapolation; the prior band declares its cost.

### Full-campaign cost estimate (from pilot timings)
- 12-playlist FPS CV event loop: 1h36/playlist as a 12-array (shared, 2 cpu) —
  one evening. CV unfolds + anchors: minutes each.
- `_universes_full` FPS re-run for the systematic campaign: same shape as the
  existing 4D/5D campaigns (~12h walls, ~130 GB merged, SetMaxTreeSize merger),
  then the 187-universe sweep via `sweep_bank.py` (shared QoS), bootstrap,
  split-seedscan, unified throw (the high-pT/low-p∥ corner made the 4D block
  sum fail ×2 — in FPS the migration-heavy corner is *in* the measurement, so
  the unified throw is mandatory, not optional).
- New validation: hidden-variable closure + coverage toys restricted to the
  extension regions; 3-prior envelope.

### Code debt noted
- `unfold_nd_omnifold_unbinned.py` no-`--use-weights` mode hands OmniFold
  unscaled unit MC weights while binning with POT-scaled `w_truth`: global
  normalization low by pot_scale (≈4.54 here). Corrected exactly in
  `fps_pilot_compare.py` (calibrated-classifier constant-offset argument).
  Fix properly when next touching the driver — carefully, since closure mode
  without weights is internally consistent as-is.
