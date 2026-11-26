# ME-FHC inclusive muon momentum discrepancy

**The first discrepancy visible against the publication is in the selected MC yield, before unfolding. Its cause remains unresolved.** At reconstructed 40–60 GeV/c, the finer copy of Fig. 2 gives about 20,379 data and 15,185 Tune v1 MC events. Our replay gives 20,355 and 13,283. The two printed copies differ by about 11% in absolute counts, so use the original production histograms for an exact comparison. [Fig. 2 extraction](../ibu-chi2-20261123/fig2/README.md)

## Baseline and event counts

On the released 16 × 14 grid (205 reported cells), ten iterations of signed Bayesian unfolding give 3.07171 versus the published 3.03901, in 10⁻³⁸ cm²/nucleon. The true 40–60 column remains 13.1% high. [Exact edges](inputs/replay/axes.json) · [224 cell results](inputs/replay/cross-section.csv)

| Reco longitudinal momentum (GeV/c) | Selected data, q/p < 0 | Nominal MC incl. background | Published spectrum folded, in-grid efficiency | Fold with all-selected efficiency | Data − all-selected | Nominal feed from true ≥60 |
|---|---:|---:|---:|---:|---:|---:|
| 20–40 | 137,785 | 112,620.5 | 134,608.7 | 137,449.7 | +335.3 | 31.2 |
| 40–60 | 20,355 | 13,283.2 | 18,475.7 | 19,416.3 | +938.7 | 590.6 |
| 60–80 | 2,495 | 1,179.4 | 1,450.9 | 1,497.1 | +997.9 | 411.3 |
| ≥80 | 415 | 285.2 | 340.8 | 348.4 | +66.6 | 49.1 |

At data POT, **true 40–60** has **19,485.0 generated**, **15,677.6 selected anywhere with truth weights**, **15,481.6 with reco weights** and **14,559.4 selected in grid with reco weights**. The corresponding efficiencies are 80.46%, 79.45% and 74.72%. Imposing the Fig. 5 estimate (86.05% over our truth mix) overshoots reco 40–60 by 277 and leaves 994 missing at ≥60. [Weighted stages](inputs/replay/baseline.txt)

## What the controls ruled out

- **Fixed-rate tail efficiency.** The full-phase-space split reproduces the nominal destinations. True 60–80 and ≥80 supply 1,354.0 and 62.2 generated events. Even 100% efficiency and optimal migration of this population add at most 365.3 at reco ≥40, versus 2,003.2 missing. A single tail multiplier needs 2.59 to fit 40–60 or 3.31 to fit ≥60. The Valencia flux swap adds only 63 to the 40–60 published-spectrum fold. [Replay](inputs/replay/baseline.txt)
- **Uniform response changes.** A 1.23× curvature width matches one Fig. 3 migration cell but removes 804 events from 40–60 and 4,088 from 20–40. Removing the 3.6% data curvature scale in longitudinal momentum alone leaves held-out residuals of −3,382, −692 and +238 at 20–40, 40–60 and ≥60. [Width](width.txt) · [Scale](curvature-scale.txt)
- **Charge assignment.** Before the charge cut, the ≥60 fold is short by 1,064.5 negative and 66.9 positive tracks. The shifted cut predicts zero positives for 172 observed on holdout. Track precision favors extra true-tail events, recoil favors extra upward migrants, and the positive-side preference depends on its control-bin normalization. [Sign test](README.md) · [Shape controls](inputs/control/fine-results.json)
- **Unfolding.** The selected-count gap precedes unfolding. The ten smallest covariance modes carry 8.71% of the exact-edge distance. [Six signed projections before and after the edge change](modes/six-modes.csv)

## Minimum counts to resume

Start with **the original generated denominator and selected-anywhere Fig. 5 numerator** at true 40–60, by published transverse bin, with POT and weight definitions. The historical me1A names are `h_pzmu_ptmu_truth_CC` and `h_pzmu_ptmu_CC`. Verify the production version. [MINERvA histogram index](https://github.com/MinervaExpt/MINERvA-101-Cross-Section/wiki/ProjectGoals)

For both sides of 60, extend this to **one MC table**. Use true <20, 20–40, 40–60, 60–80 and ≥80 rows. For each, give generated truth and selected destinations below 40, 40–60, ≥60 and outside reco acceptance, at the same transverse edges. Keep truth and reco weights for the selected cells and other backgrounds separate. Generated totals, selected/generated and destination fractions then distinguish rate, efficiency and migration. Two official selected-data counts at reco 40–60 and ≥60 close the fold at matched POT.

**Reproduce** from the repository root with `bash docs/orchestration/state/precharge-20261125/reproduce.sh`. It writes to a fresh directory using the local branch’s saved inputs. [Dependencies and provenance](REPLAY.md)
