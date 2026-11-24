# Impact inventory: where the pT edge difference reaches (2026-11-24)

**What this is.** A list of every place in the repo that reads the published products or compares our result with
them, at main `c720db69b` plus this PR. Nothing was rerun. The director asked for it before any rerun is decided. It
was swept by a read-only search subagent (Claude, Explore). I checked these claims against the files before
committing:
- `Binning.h` is included nowhere; every include is commented out;
- `2d-unfolding/driver_p1.py:32` hard-codes 0.07 / 0.33 / 0.47;
- `strip_ratio_receipt.json:11` records the 0.0714 area deviation;
- `check_fig67_takeaway.py` exists;
- the `sec3_twod.tex:11` and `appC_supplementary.tex:31` sentences;
- `2D_OMNIFOLD_STUDY_STATUS.md:265-266`.

**Classes.**
- AFFECTED-COMPARE: compares densities across the two grids.
- AFFECTED-AREA: uses `bin_mapping.txt`'s printed edges as widths or areas for published values.
- UNAFFECTED: both sides are on our grid, or it reads only GlobalIDs or cell identities.
- UNCLEAR.

**A classification is reasoning unless marked measured.**

## Two facts that change where the fix lives

- **Our grid is not set by `util/Binning.h:6`.** Every `#include "Binning.h"` is commented out (for example
  `runEventLoopOmniFold.cpp:53`). The 0.07 / 0.33 / 0.47 grid is hard-coded as `PT_EDGES` in:
  - `2d-unfolding/driver_p1.py:32`
  - `unfold_2d_omnifold_unbinned.py:32`
  - `re2/re2_driver.py:44`
  - `pv2d/unfold_2d_pv2d.py:50`
- **The repo saw the exact axis and rejected it.** `strip_ratio_receipt.json:11` records a 0.0714 maximum area
  deviation between the release TH2D axis and the printed edges. That is 0.075/0.07 − 1. The axis is called
  "cosmetic" in:
  - `2D_OMNIFOLD_STUDY_STATUS.md:265-266`
  - `2D_OMNIFOLD_REFERENCE.md:450`
  - `compare_to_paper_interior.py:38`
  - `normalize_xsec_shape.py:51`
  - `strip_ratio_receipt.py:158-160`
  
  Code that uses the TH2D's own axis widths gets the published areas right.
- **Already on 0.075:** `ibu_1d_projection/build_1d_ibu_inputs.py:37` and `ibu_omnifold_paired_cdelta.py:26`. The
  flux histogram `pTmu_reweightedflux_integrated` is also on 0.075 (`runEventLoop.cpp:407`), which matters only if its
  bins differ (UNCLEAR).

## A. Reads published products, no comparison with our result

| # | path:line | what | class |
|---|---|---|---|
| A1 | `2d-unfolding/compare_to_paper_fullcov.py:52-96,216-225` | loaders; GlobalID mapping | UNAFFECTED |
| A2 | `2d-unfolding/uq/reported_cells.py:6,23` | cell identity | UNAFFECTED, measured |
| A3 | `2d-unfolding/tests/test_reported_cells.py:55,71` | GlobalID tests | UNAFFECTED, measured |
| A4 | `2d-unfolding/ibukt/rehearse.py:78-97` | reported-mask probe | UNAFFECTED, measured |
| A5 | `ibukt/test_ibukt.py:33-53`, `ibukt/test_signed_data.py:18,152-159` | synthetic fixtures | UNAFFECTED, measured |
| A6 | `ref_c2c1/test_ref_c2c1.py:305-312` | synthetic published TH2D | UNAFFECTED, measured |
| A7 | `uq/rederive_flux_muonE_cross.py:31,67` | published covariances only | UNAFFECTED |
| A8 | `receipt_model_chi2_2d.py:199-200` | CSV vs TH2D round-trip | UNAFFECTED, measured |
| A9 | `ibub/config.json:10` | hash pin only (COVFIX and COV2D read none) | UNAFFECTED, measured |
| A10 | `state/2d-closeout/stageB/evidence/local-verify-c04/paper_flux.py:7-10,30-33` | published integral with bin_mapping areas; possibly the source of `\uqPaperIntegral` (`values.tex:66` says it has no receipt) | AFFECTED-AREA, measured |
| A11 | `state/2d-closeout/per-period-benchmark-20261106/r4_power_txt.py:24-30` | published step ratio with 0.07 widths | AFFECTED-AREA |
| A12 | `per-period-benchmark-20261106/spectrum_gap_txt.py:12` | published covariance eigen-gaps | UNAFFECTED |
| A13 | `per-period-benchmark-20261106/receipts/connect1/smoke.py:32` (+ `connect1.sh:125`, `remote1.sh:68`) | CSV vs ROOT control | UNAFFECTED, measured |
| A14 | `per-period-benchmark-20261106/test_per_period_benchmark.py:37` | fixtures | UNAFFECTED |
| A15 | `state/uqpaper-median-20261006/paper_median.py:24-33` | published-only median σ | UNAFFECTED |
| A16 | `state/uncertainty-preparation-20261008/e/recompute/rc_pairing.py:38-44,66-67,89-94` | GlobalID, orientation | UNAFFECTED, measured |
| A17 | `state/next-preparation-20261009/structure/checks/equivalence.py:117-118`, `real_operands.py:50-56,88` | synthetic / equivalence | UNAFFECTED |
| A18 | `stageF/rebuild/outputs/recompute/inspect.py:5`, `inspect2.py:2` | list keys | UNAFFECTED |
| A19 | `stageF/methods/note-figstyle-20261117/tools/remap_anc.py:7-33` | remap directory | UNAFFECTED |
| A20 | about 20 staging and hash scripts (`re1_f_chain.sh`, `refc2c1_*_login/submit.sh`, `connect2.sh`, `delete_copies*.py`, `check-consumer-set-20260910.py`, …) | copy, link, hash | UNAFFECTED |
| A21 | `stageA/scripts/analyze.py:25-26,43` | `pt_edges_equal_paper` against the printed edges | UNCLEAR: passes by construction |

## B. Compares our 2D result, or a projection of it, with published data or model tables

| # | path:line | what | class |
|---|---|---|---|
| B1 | `compare_to_paper_fullcov.py:236-242,277-285` | χ²(ours − published), pulls; `\chiPaper`, `\pullMean`, `\pullRMS`, `\chiCombined`, fig:pull | AFFECTED-COMPARE |
| B2 | `compare_to_paper_interior.py:38-41,86-90,127-159` | interior-mask χ² | AFFECTED-COMPARE |
| B3 | `compare_to_models.py:37-39,61-73,108,137-158,194` | σ_tot ratios; ours vs data and vs tune; 1D projections with 0.07 widths | COMPARE + AREA, measured |
| B4 | `normalize_xsec_shape.py:51-53,89-97,132-154` | unit-area shapes, 0.07 widths; χ²_shape ≈ 465 | COMPARE + AREA, measured |
| B5 | `plot_2d_paper_comparison_shape.py:86-101` | plots B4 | AFFECTED-COMPARE |
| B6 | `diagnose_tension.py:44,100-124,206` | eigenmodes of ours − published | AFFECTED-COMPARE |
| B7 | `agreement_windows_receipt.py:65-85,147-157,168-192` | per-bin ratio windows; integrals use each TH2D's own widths | COMPARE (ratios); UNCLEAR (integrals, `\ratioTot`) |
| B8 | `strip_ratio_receipt.py:46,158-163,180-186` | strip integrals with printed-edge areas | COMPARE + AREA, measured |
| B9 | `receipt_model_chi2_2d.py:215-221` | ours vs data, ours vs tune | AFFECTED-COMPARE |
| B10 | `plot_2d_threeway_fig13.py:81-90,201-212,322` | Fig. 13 mosaic; published points on our slices | AFFECTED-COMPARE |
| B11 | `ibu_1d_projection/plot_ibu_1d_proj_vs_omnifold.py:37-86,117-122,168-173` | IBU 1D is on 0.075 (fine, measured); OmniFold vs paper crosses grids | AFFECTED-COMPARE (OmniFold side) |
| B12 | `uq/_ours_only_chi2.py:85-99,154` | direct-inverse χ² | AFFECTED-COMPARE |
| B13 | `uq/compare_split_bootstrap.py:31,106-123` | our stat covariance vs published StatOnly | AFFECTED-COMPARE |
| B14 | `uq/plot_uncertainty_fig6_7_style.py:55,174-237` | "Published total" projections, 0.07 widths | COMPARE + AREA, measured |
| B15 | `ibukt/signed_data.py:66-77,98-118` | E_R and IBU K=5/10 vs published (asserts 465.415, 0.83, 1.03) | AFFECTED-COMPARE |
| B16 | `ref_c2c1/ref_c2c1_read.py:42,88-108,240` | D_ER 2.270, D_IBU 1.0266 vs published (T is same-grid) | AFFECTED-COMPARE |
| B17 | `pv2d/pv2d_analyze.py:116-122,297` | relative σ, ours vs published | UNCLEAR |
| B18 | `re2/partc/re2c_build_q.py:611-615` | our stat covariance vs published StatOnly (0.407, 0.425) | AFFECTED-COMPARE |
| B19 | `re2/partc/re2c_run.sh:134-166`, `sbatch_analyze_MEFHC_*.sh`, `sbatch_finalize_MEFHC.sh:36-37`, `uq/final_rollup_full.sh:151`, `uq/rollup_vl170_adoption.sh:57,61` | wrappers | AFFECTED-COMPARE |
| B20 | `docs/analysis-note/make_figures.sh:37-44,126` | runs the comparison producers | AFFECTED-COMPARE |
| B21–B31 | this lane: `truthtest`, `priortest`, `variants`, `foldtest` (+ `posthoc_exclude`), `bkgtest`, `oflow`, `evloop/score_evloop.py`, `flux/fluxrw`, `lattest`, `wstest` | `pub/F` on 0.07 areas, or distance to published | AFFECTED (AREA and/or COMPARE); `truthtest`, `priortest` and `foldtest` measured |
| B32 | `ibu-chi2-20261123/fig2/score_fig2.py` | Fig. 2 counts with 0.07 areas | COMPARE + AREA, measured (this PR's `edges/` corrects it) |
| B33 | `state/2d-closeout/b1-a2-projection-20261122/b1_projection.py:211-287` | E_R − published in covariance modes | AFFECTED-COMPARE |
| B34 | `per-period-benchmark-20261106/per_period_benchmark.py:283-299,525-529,640-660` | periods vs published; 0.07 widths | COMPARE + AREA |
| B35 | `stageA/scripts/analyze.py:52-64` | published integral with our areas | COMPARE + AREA, measured |
| B36 | `stageF/rebuild/scripts/build_q_products.py:557-565` | `paper_ratios` covariance comparison | AFFECTED-COMPARE |
| B37 | `stageF/rebuild/outputs/recompute/recompute.py:33-50` | published values on the 224 grid; downstream use not read | UNCLEAR |
| B38 | `stageF/methods/note-figpass-20261119/tools/compose_tier2.py:122-198`, `compose_slices_markers.py` | fig:xsec published curves; published points on slice panels | COMPARE + AREA |
| B39 | `note-figpass-20261119/tools/check_fig67_takeaway.py:9-17,62-77` | **the Figs. 6–7 "closer to the published" takeaway** | AFFECTED-COMPARE |
| B40 | Fig. 3 pull chains (`compose_fig3_*`, `run_fig23.sh`, `run_round.sh`, `run_r3.sh`, `figc_*`, `connect-sd*.sh`), `c04-repair/scripts/run_repair.sh`, `receipts-cov2d/g2r/re2shapes/package/re2c_run_g2r.sh` | wrappers | AFFECTED-COMPARE |

Unaffected by construction: closure, coverage, pseudo-data, COVFIX, COV2D and IBUB (both sides on our grid), and the
IBU 1D projection path (on 0.075).

## Analysis-note locations

**Built into `main_note`:**
- `sec3_twod.tex:5` — the integral is reproduced to about 1 % (`\ratioTot`).
- `sec3_twod.tex:11` — "closer to the published cross section than to the prior" (the Figs. 6–7 takeaway, B39). The
  same line has Tune v1 at 0.91 of the published integral, and "0.97 in the lowest pT bin", which is row 0.
- `sec3_twod.tex:15-19` — fig:xsec projections with the published curve.
- `sec3_twod.tex:22` — `\sigTwoD`, `\sigTwoDpaper`, `\ratioTot`, and `\uqIntegral` vs `\uqPaperIntegral`.
- `sec3_twod.tex:24` — median ratio, 5/10/20 % windows, pulls, `\chiPaper`.
- `sec3_twod.tex:28-31` — fig:pull.
- `sec3_twod.tex:34` — χ²_norm = 0.04 and χ²_shape ≈ 465.
- `sec3_twod.tex:36` — `c2c1-dibu` = 1.03 and `c2c1-der` = 2.27 (`c2c1-T` is same-grid).
- `sec3_twod.tex:43` — `\chiCombined`.
- `sec3_twod.tex:50,59,74` — the "Published total" row (UNCLEAR).
- `sec3_twod.tex:79` — flux band 3.72 vs 4.01 % (UNCLEAR).
- `sec3_twod.tex:81` — stat ratios 0.407 / 0.425.
- `appC_supplementary.tex:7,14-17,23-25` — tension figures.
- `appC_supplementary.tex:30-32` — "In all 14 pT slices … move toward the published values".
- `appC_supplementary.tex:37-39` — the p‖ slices.
- `appC_supplementary.tex:42,44` — distances to published.
- `appC_supplementary.tex:214` — the 3D marginal pull figure.

**Primer and records:**
- `primer_body.tex:107,156`
- `records_r03_twod.tex:14`
- `sec_tension.tex:4-6`

**Not input by any document:**
- `sec_results.tex:98-186`
- `sec_systematics.tex:32-33`

## Receipts

About 157 receipt files in `docs/orchestration/state` quote such numbers. This count comes from pattern matching, so
it is approximate:
- 64 hold `PAPER (stat+syst)` χ² lines;
- 81 hold 465.41 or 2.270x;
- 12 are model-χ² receipts;
- 5 are agreement or strip receipts.

The IBU χ²/205 = 1.03 appears in 7 `D_IBU` files and in 5 documents that quote "1.03".

**Outside this inventory's scope (not listed):**
- `3d-unfolding/sbatch_unfold_3d.sh:49`
- `publication/release/figs/export_fig_arrays.py:59`
- `docs/orchestration/receipts/2d-lgbm42-20261011/lgbm_central_metrics.py`
