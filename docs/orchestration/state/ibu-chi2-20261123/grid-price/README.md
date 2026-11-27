# Pricing the pT-grid question: (ii) move the analysis to the paper's grid; (i) redo only the comparisons (2026-11-24)

**By** the `ibu-chi-squared-issue` session (Claude Opus 5.5), at the director's request, after Joseph's decision: keep
doing (i), and price (ii) for him to take to Ben. Read-only. Nothing in this record ran. The finding behind it is
[`../edges/`](../edges/README.md): the paper's pT edges are 0.075 / 0.325 / 0.475, and ours are 0.07 / 0.33 / 0.47.
Its site list is [`../edges/IMPACT-INVENTORY.md`](../edges/IMPACT-INVENTORY.md).

**Sources.** Two read-only search subagents (Claude, Explore) swept the run records. I checked three of the cited
charges against main `75c63def7`:
- J1 0.2528 node-h at `2d-closeout/stageF/methods/re2/RE2-PARTB-REPORT.md:52`;
- VL170 18.107 at `ki84-rebuild-20261006/budget.json:32`;
- COV2D 112.74 at `measurement-paper/5d-community-20261024/fd/receipts-cov2d/a2/bulk/README.md:75-79`.

I also checked the production background path myself, and the director confirmed it independently. All paths below are
relative to `docs/orchestration/state/` unless they start with `2d-unfolding/`.

## Three facts that set the price

1. **The event loop needs no rerun.** `runEventLoopOmniFold.cpp` only fills unbinned TTrees (`out->Fill()` at :637,
   :910, :1296, :1516, :1612). Its only phase-space cuts are the outer bounds (for example p‖ < 60 GeV at :1739). The
   `Binning.h` include is commented out (:53). The omnifiles do not depend on the pT grid.
2. **Production training does not see the interior pT edges, but nothing stores per-event weights.**
   - Production is `bkg_mode = negweight-refined`. 432 committed records carry it, against 9 with `purity`, and
     `2d-unfolding/re2/partc/re2c_export_cov.py:111` requires it.
   - On that path `re2_driver.py:2063-2067` replaces the purity weights with ones. Background enters at −w per event
     (bounds only, `:387-393`), and the refinement is unbinned in (pT, p‖).
   - Every driver, though, writes only histograms binned on `PT_EDGES`. The step weights were dropped on purpose for
     J1 (`2d-closeout/stageF/methods/re2/RE2-DECLARATION-B.md:51,65,597`), when the C2ST that needed them left RE-2's
     scope.
   
   So a negweight-refined product needs its driver **rerun** on the new edges. The rerun has identical training
   inputs; LightGBM reproduces to ≤ 1e-8 (`measurement-paper/5d-community-20261024/COV2D-DECLARATION.md:83-85`).
   The result is expected to be the old unfold re-binned. That is expected, not measured.
3. **Purity-mode products genuinely re-unfold.** `build_measured_training_2d` weights each data event by its reco
   bin's (D − B)/D on our grid (`2d-unfolding/re2/re2_driver.py:405-442`).

**The flux needs nothing.** The flux histogram is already on the paper's pT edges, and its 14 values are equal
(`2d-closeout/stageA/REPORT.md:168-171`; `s5p/gen5d/gen5d-fluxfix.json:694-698`, `"hFluxCV_values_all_equal": true`).

## A. Price of (ii)

**Charge is CPU node-h. No 2D job has recorded GPU or Delta use.** "Elapsed" marks a record with sacct elapsed but no
charge.

### Products in use (the note reads E_R, Q_R and G2R: `docs/analysis-note/make_figures.sh:195-215,362-364`)

| product | class | runs | recorded charge | evidence |
|---|---|---|---|---|
| E_R central (RE-2 J1) | rerun, same inputs | 3 | 0.2528 | `2d-closeout/stageF/methods/re2/RE2-PARTB-REPORT.md:52` |
| Q_R (RE-2 part B: 175 universes, 10 laterals, 300 bootstrap, 80 C08 seeds, 37 periods, 39 diagnostics) | rerun, same inputs | 644 | 47.7083 (core 43.0202) | `RE2-PARTB-REPORT.md:9,50-70` |
| RE-2 J0 pilot | rerun only if re-piloted | 34 | 5.4755 | `RE2-J0-REPORT.md:31-34` |
| COV2D (toys, pseudo-data, natures) | rerun, same inputs | 1,572 labels in 27 attempts | 112.74 | `measurement-paper/5d-community-20261024/fd/receipts-cov2d/a2/bulk/README.md:18-24,75-79` |
| G2R | rerun, same inputs | 529 in 12 jobs | 1.2411 recorded; the 12 unfold jobs have **no charge recorded**, elapsed 62.28 h; priced 73.6–93.7, cap 110 | `measurement-paper/5d-community-20261024/fd/receipts-cov2d/g2r/unfolds-all/README.md:13-14`; `.../unfolds-all/sacct-utc.txt:1-12`; `COV2D-G2R-BINDING-1.md:21,29` |
| PV2D, refined arm | rerun, same inputs | 4 | 3.1439 | `2d-closeout/stageF/methods/pv2d/LEDGER.tsv`; `pv2d/REPORT.md:74,373-376` |
| PV2D, arm (a) | re-unfold (purity) | 6 | 4.2617 | same |
| IBUB | not run (binned IBU on our 14 × 16 grid) | 0 | 0; plan about 9.2, cap 11.48 | `IBUB-BINDING-2.md:5`; `IBUB-DECLARATION.md:48,318-327` |

### Grading truths on our grid (they must be refilled at event level, not re-binned)

| truth | graded readings | charge to remake | evidence |
|---|---|---|---|
| COV2D `truth_xsec.npz`, per nature | COV2D UNDER-COVERS at both tunes; IBUB's planned readout | inside COV2D's 6.89 pre-bulk | `COV2D-ADDENDUM-A4.md:114,169`; `COV2D-DECLARATION.md:165-169` |
| F1 G18 / AR23 truth ratios | COV2D natures' truths | 1.3275 | `fd/LEDGER.tsv` rows 20, 21, 26, 29, 31 |
| generator truths: `pvl_lib.FINE` pT axis is ours (`pvl_lib.py:20`); gen5d products, the u = 2 ratio map, FINE histograms | the generator comparisons | event-level refill; no charge found | cov2d's read, via the director |
| toy natures: `cov2d_pseudo` `truth_cell` on `PT_EDGES` (:149 on) | COV2D coverage | inside COV2D | cov2d's read, via the director |
| VL169 fixed truth (superseded, purity) | 2D coverage FAIL | inside 13.325 | `coverage-2d-20261005/budget.json:972-990` |
| PV2D closure truths | PV2D closures | 1.1822 | `pv2d/LEDGER.tsv` |

Every reading graded on these would be re-graded under its own declaration's review.

### COVFIX, priced as its own line

- **State:** COVFIX has run only P0, locally at 0 node-h (`2d-closeout/covfix-20261122/p0/run/README.md:3`).
- **Plan:** 410.55–411.22 CPU node-h expected, ceiling 541.50 (`COVFIX-DECLARATION.md:418-433`; `COVFIX-BINDING-1.md`).
  Rev 12, not yet bound, raises the ceiling to 600.00 CPU and adds 25.8 GPU node-h
  (`DECISION-20261124-joseph-covfix-rev12-cpu-rule-and-seven-decisions.md:13,40`).
- **Grid-bound pieces:** its carried blocks are all on our 14 × 16 grid: K0 (COV2D's reported covariance), C_b from
  IBUKT A2's vertices, C_model, COV2D's C_T, and the A1p band ratios. §5–§7's bars are defined on our grid's modes. Also,
  `re2c_export_cov.py:106` asserts that hXSec2D's axes equal `PT_EDGES`.
- **Under (ii):** COVFIX becomes a revision with rebuilt inputs, whichever class its toy unfolds fall in. Its own spend
  is about the same either way, because it is planned and not yet spent.
- **The cost is calendar:** rebuilding its inputs (Q_R, COV2D, G2R, C_model, IBUKT A2) and re-reading a 12-round
  declaration.
- **Timing:** the director estimates COVFIX's first sealed spend at about 2026-12-02 to 12-05. (ii) is cheapest if
  decided before then.

### Superseded products (purity era; rerun only if still cited)

| product | runs | charge | evidence |
|---|---|---|---|
| Stage C production S5 (Q before 10-24) | 153 run | 29.0297 | `2d-closeout/stageC/production/REPORT.md:24,292-300` |
| Stage C pilot / Stage B diagnostics / period-unfold | — | 7.2479 / 1.2524 / 1.9414 | `RE2-PLAN.md:328-336` |
| VL170 bootstrap | 300 | 18.107 | `ki84-rebuild-20261006/budget.json:32` |
| VL169 coverage | 100 toys | 13.325 | `coverage-2d-20261005/budget.json:972-990` |
| July universe sweeps 55677842 / 55677843, plus CVs | 187 each | **no charge recorded**; elapsed 132.51 h + 132.04 h + 1.43 h | `next-preparation-20261009/speed/operands/sacct_universe_sweeps_batch.psv`; `speed/REPORT.md:86-87` |
| E_C exact-GBT, 53116554 | 1 | **no charge recorded**; elapsed 19.31 h | `next-preparation-20261009/speed/REPORT.md:85` |
| lgbm ML seed scan | 10 | **no charge recorded** | `2d-unfolding/2D_OMNIFOLD_REFERENCE.md:258` |

### Totals (CPU node-h; GPU 0)

| scope | recorded | with elapsed where there is no charge |
|---|---|---|
| **(ii), products in use:** E_R + Q_R 53.18 (+5.48 if re-piloted), COV2D 112.74, G2R 1.24, PV2D 7.41, grading truths 2.51 beyond those included | **≈ 177** (182 with the pilot) | **≈ 239–244** (G2R's 62.28 h) |
| planned spend that would move onto the new grid: IBUB about 9.2; COVFIX 410.6–411.2 (ceiling 541.5, or 600 + 25.8 GPU under rev 12) | not extra if decided before it is spent | — |
| superseded purity products, only if still cited | 70.9 recorded | up to about 357 with the July sweeps and E_C elapsed |

**Calendar.** From records, first declaration to merged records took:

| product | calendar |
|---|---|
| RE-2 | about 1.4 days (PR #275 → #343) |
| COV2D | about 5 days (11-02 → PR #917) |
| G2R | about 2 days to PR #1145, plus cr/xk to 11-16 |
| PV2D | about 1 day |
| COVFIX | 12 read rounds over 2 days, not yet bound |

They chain: COV2D needs E_R, G2R needs COV2D, COVFIX needs all three. **Estimate, not measured:** about 1.5–3 weeks of
review calendar for (ii) on the products in use. Compute is not the long pole; at the recorded charges it is days of
queue at most.

**Review stages each rebuilt product passes again.** Its own record shows the stages: declaration, agy/codex/fresh-Claude
reads, binding with a price, director GO, Joseph's adoption (RE-2, G2R), and records PR.

**A cheap fix that pays back either way.** Add an option to the drivers to write the final per-event unfolded weights
(float32, keyed by event id). That is about 0.13–0.26 GB per unfold for about 33 M MC events. With it, any later
change of binning is a re-histogram, not a rerun. Not implemented; suggested only.

## B. Scope of (i): what the comparisons with the published result need

Our grid stays the analysis grid. The published-side fixes cost nothing: use the TH2D's own axis widths, not
`bin_mapping.txt`'s printed edges. The inventory's AREA rows (A10, A11, B3, B4, B8, B14, B34, B35, B38 and this lane's
tests) need only that. COMPARE rows need our result on the paper's edges, which means a driver rerun, because no
weights are stored.

| need | what reruns on the paper's edges | recorded unit charge | serves |
|---|---|---|---|
| **Tier 1:** the central value | E_R alone (one J1-type run) | ≤ 0.2528 for J1's 3 runs | B1 `\chiPaper` and pulls, B2, B4–B10, B12's central, B33, B38, B39 (the Figs. 6–7 takeaway) |
| **Tier 1:** the IBU χ²/205 | `ref_c2c1` c2 central, plus `ibukt/signed_data` at K = 5/10, with the driver's `PT_EDGES` set to the paper's | c2 central 3:36.74 on 64 CPUs (`fd/receipts-ref-c2c1/step2/units-centrals/c2_central.time`); E_R full rerun 9:55.42 (`er.time`) | B15, B16, `sec3_twod.tex:36` |
| Tier 2: our stat covariance vs the published StatOnly | Q_R's 300 bootstrap replicas | about 0.0446 each, about 13.4 total (`RE2-PLAN.md:260`) | B13, B18, B36; `sec3_twod.tex:81` |
| Tier 2: `\chiCombined`; Figs. 6–7 uncertainty vs "Published total" | Q_R's universes (175) and laterals, plus bootstrap | universes about 0.115 each, about 20 (`RE2-PLAN.md:258`); in total ≤ Q_R's 47.7 | B1 `\chiCombined`, B12, B14 |
| none | published-side area fix | 0 | the AREA rows |

**Priced draft declaration for Tier 1.** It is a draft; nothing runs without its binding and the director's GO.
- **Runs:**
  1. E_R central on the paper's pT edges, with E_R's argv otherwise unchanged;
  2. `ref_c2c1` c2 central on the same edges;
  3. `signed_data` K = 5 and K = 10.
- **Inputs:** the same omnifile and flux E_R used (`ref_c2c1/config.json` `inputs`). The flux histogram is already on
  the paper's edges.
- **Controls:**
  - with the OLD edges, each run reproduces its committed product: E_R to ≤ 1e-8 (C-REF), and the D_IBU 1.0266 and
    D_ER 2.270 readouts;
  - with the new edges, the summed counts over each p‖ column equal the OLD run's. The interior pT edges do not change
    a column's total.
- **Readings:** `\chiPaper`, the pulls, D_ER and D_IBU on the paper's edges, each against the published TotalCovariance.
  Descriptive, no thresholds, because the question is what the numbers become.
- **Price:** about 0.25–0.5 CPU node-h expected, cap 1.0, on one shared or regular node.

Tier 2 would get its own declaration if the note keeps those comparisons. Its estimate is about 13–50 CPU node-h, with
the per-run figures above as the anchors.

**Already running for this lane:** `ibuchi_rb` (job 61926143; director GO; declaration sha `8b4a978b…`, to be
committed with its results in a separate records PR) rebuilds this lane's binned IBU inputs on both edge sets. It is the first measured IBU χ²/205 on the
paper's edges, for this lane's evloop build, not E_R's.
