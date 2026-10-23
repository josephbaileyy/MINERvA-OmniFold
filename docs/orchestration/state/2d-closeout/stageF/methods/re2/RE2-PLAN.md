# RE-2 plan: rebuild the adopted 2D result with the refined estimator (plan only; nothing runs)

**Written by** the re-1 lane (Claude) for the director, 2026-10-23, under
[`DECISION-20261023-joseph-2d-refined-integrate-ci.md`](../../../../../DECISION-20261023-joseph-2d-refined-integrate-ci.md)
item 1 ("Step 1 is a plan, and runs nothing"). It is based on `origin/main` `9cf49713`. **No job has run under it, and no
job may run until the director binds a declaration made from it.**

**CITABLE FOR:**
- what depends on the adopted 2D result;
- what this plan proposes to rebuild, re-evaluate or leave alone, and why;
- the measured unit costs it uses;
- the projected charge against the 2D closeout ceiling;
- the controls and stop rules it proposes.

**NOT CITABLE FOR:**
- any new number: none exists yet;
- the adoption of a rebuilt result, which is Joseph's decision;
- a coverage claim for either estimator;
- any deliverable wording (the director writes it).

**In brief:**
- **What is rebuilt:**
  - the 2D central value;
  - all four blocks of its covariance (universe, statistical, seed, run-period);
  - the comparison with MINERvA's published result;
  - every number printed from them.
- **New code:** a 2D path that can run the refined estimator on universes, laterals, bootstrap replicas, seed panels
  and run periods. No existing path can do that at the 400/31 refinement (§3).
- **Projected charge:** **67 node-h; worst case 84 node-h at 1.25× the projection.** The proposed grant is ≤ 90.
  The 2D closeout ceiling has **660.53** node-h left (§4). The cost does **not** exceed what remains, so it does not
  go back to Joseph on cost.

---

## 1. The estimators, by registry name

`tools/registry/whatis.py` at `9cf49713`:

| role | registry name | definition (registry) |
|---|---|---|
| current adopted 2D central value, `E_U` | `a-central-lgbm` | configuration (a): LightGBM 100 trees, 8 leaves, learning rate 0.1, purity subtraction, seed 42 in 2D |
| the refined arm of RE-1's C2 and D2 | **none** (see below) | (a) with `--bkg-mode negweight-refined` and the Stay-Positive refinement classifier at 400 trees / 31 leaves, `random_state` = seed + 3 = 45: `2d-unfolding/re1/re1_2d.py:70-75` (`ESTIMATOR_SEED = 42`, `REFINE_OVERRIDE = {"n_estimators": 400, "num_leaves": 31}`) |
| the 5D joint-test estimator | `e-R-joint-test` | configuration (e): the **deterministic** LightGBM (c) with the 400/31 refinement |
| the 2D negative-weight equivalence study | `2d-exact-negweight-refined` | the exact-split estimator with `--bkg-mode negweight-refined` at the driver's built-in 100/8 refinement (`2d-unfolding/sbatch_bkgnw_exact_refined.sh:47`) |

The Search lines, verbatim:
- `a-central-lgbm`: `Search: configuration (a); (a) central value: LightGBM, seed 42 in 2D; (a) central-value estimator; configuration 1 (note, before register batch b5); LightGBM seed-42 matched CV (2D); LightGBM, 100 trees, 8 leaves, learning rate 0.1, --seed 42, purity subtraction; production 5D estimator (lgbm, five iterations, seed 42) @ 9cf497137947`
- `e-R-joint-test`: `Search: configuration (e); (e) joint-test estimator; (e) joint-test estimator; joint-test estimator; R (s5e candidate); R (s5p baseline_estimator); configuration 1 = R; R = paper configuration (e); s5e candidate R = the joint-test estimator; --candidate R; --candidate R (contract implementation); refinement 400 trees, 31 leaves; refinement 400/31; 400-tree, 31-leaf Stay-Positive refinement; s5p data unfold @ 9cf497137947`
- `2d-exact-negweight-refined`: `Search: sbatch_bkgnw_exact_refined.sh @ 9cf497137947`

**The estimator Joseph adopted is not in the registry.** It is the C2 refined arm and D2: configuration (a)'s
non-deterministic LightGBM at seed 42 with the 400/31 refinement. It is neither (e), which is built on the
deterministic (c), nor `2d-exact-negweight-refined`, which uses the exact-split base and the 100/8 refinement.
- **Proposal:** register it before any RE-2 job, e.g. as `a-refined-400-31`. The registry
  (`docs/orchestration/registry/`) is outside this lane's file set, so the director would add it.
- **Throughout this plan,** "refined" means this estimator. "Purity" means `a-central-lgbm`.

## 2. The dependency inventory

The action is one of:
- **rebuild**: a new product is made with the refined estimator;
- **re-evaluate**: the same producer is re-run on the rebuilt products, at about 0 node-h on a login node;
- **reword**: text that describes the estimator;
- **unchanged**.

The inventory was built from `origin/main` `9cf49713` by read-only searches of the deliverable sources, records
and code. The lines quoted here were cross-checked by hand; the search notes themselves are not committed. Path prefixes: `S/` is `docs/orchestration/state/2d-closeout/`, `N/` is `docs/analysis-note/`, `D` is
`2d-unfolding/unfold_2d_omnifold_unbinned.py` (`74a4ed69…`).

### 2.1 Products

| # | product | made by | consumed by | action | reason |
|---|---|---|---|---|---|
| P1 | `E_U` `4f5a1b6d…` (`uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root`) | `sbatch_unfold_2d_MEFHC_5iter_universes_full_CV.sh:43-50` (purity by default, `D:1362-1365`). Regenerated by XR L0 to 1.4e-11 (`docs/orchestration/state/next-preparation-20261009/xr-linux/REPORT.md:243`) | every item below | **rebuild** as `E_R` | it is the adopted central value. RE-1's D2 (`71ca3e5f…`, `re1/RE1-REPORT-2.md` §3) is already this unfold on data, but as an npz without the ROOT objects the consumers read: `hXSec2D` with bin errors, truth, completeness, flux |
| P2 | universe block: the July `purity_newomni` sweep, 187 universes + CV (`S/stageB/evidence/b-genie-truth/sweeps.json` "pn/"). S5 uses 175 (100 Flux + 75 others; `S/stageC/production/DESIGN.md:273`) | `sbatch_unfold_2d_MEFHC_5iter_universes_full_puritynew.sh:67-75`, array 55677843 | S5 | **rebuild**, 175 universe unfolds | each universe is a purity unfold; the decision rebuilds "its covariance" (DECISION item 1) |
| P3 | laterals, S3: 10 active lateral files | Stage C production, `S/stageC/production/sbatch_prod.sh:83` (hard-coded `--bkg-mode purity`) | S5 | **rebuild**, 10 unfolds | the same reason |
| P4 | statistical block, S1: 300 three-stream bootstrap replicas (data, signal MC, background rows) | `2d-unfolding/driver_p1.py` (`3056e625…`), which refuses every background mode except purity (`:1582-1587`) | S5 | **rebuild**, 300 replicas; **new code** | the refined estimator must be resampled through its own background treatment |
| P5 | background-only stream, S2: 100 replicas | the same | S5 controls (bkg-only fraction) | **rebuild**, 100 | the same |
| P6 | seed block, C08 / S4: (i) 20 replicas × seeds {45, 48, 51, 54}; (ii) 7 universes × 5 seed sets + CV at 4 seeds | `driver_p1.py`; driver | S5 | **rebuild**, 80 + 35 + 4 | the seed main effect of the refined estimator has never been measured |
| P7 | S5 rollup `production_cov.npz` `6689d2fc…`, `s5.json` `8c815149…`, `uq_production_covariance.root` `34cf33f9…` (`S/stageC/production/REPORT.md:25`) | `S/stageC/production/s5_rollup.py` (`6c437004…`), login, 0 node-h | combination, Stage F | **rebuild** from P2–P6 | it pins `E_U` and the purity inputs (`s5_rollup.py:56-73`) |
| P8 | period unfolds: 37 (control; P_A, P_B, P_C at seeds 42 and 43; 10 bootstrap replicas each) | `S/period-unfold-20261014/scripts/sbatch_period_unfold.sh:76-77` (hard-coded purity) | C_PL | **rebuild**, 37 | C_PL's double ratios are period/pooled ratios of this estimator |
| P9 | C_PL `playlist_term.npz` `c1723cb5…` | `S/playlist-term/scripts/playlist_term.py` (`b21d03ce…`). It is scaled by x = `E_U` (`:142`) and stops unless x equals `E_U` (`:117-121`) | Q | **rebuild** from P8 with x = `E_R` | it is scaled to, and checked against, `E_U` |
| P10 | Q = S5 total + C_PL, `s5_plus_playlist.npz` `8ccb4d72…` | `S/playlist-term/scripts/combine_s5.py` (`0c6ac3a0…`), login. Check 2 requires the central values inside S5, C_PL and `work_cov` to agree to 1e-12 (`:124-131`) | Stage F, `values.tex` | **rebuild** as `Q_R` | it is a sum of P7 and P9 |
| P11 | Stage F rebuild outputs: `budget_Q.json`, χ² files, figure inputs (`S/stageF/rebuild/outputs/`) | `S/stageF/rebuild/scripts/run_rebuild.sh`, `build_q_products.py` (`050c5b0d…`), login. The digests are hard-coded (`build_q_products.py:50,52`) | `values.tex`, figures, `check_sec4_receipts.py` | **re-evaluate** on `E_R`, `Q_R` | post-processing; new pins and control references |
| P12 | `E_U`-only receipts (`docs/orchestration/receipts/2d-lgbm42-20261011/`): agreement windows, published-covariance χ² and pulls, Tune v1 χ², tension report, model comparison, learner metrics | `agreement_windows_receipt.py`, `receipt_model_chi2_2d.py`, `compare_to_models.py`, `diagnose_tension.py`. **No argv or run script was committed** | `values.tex`, figures | **re-evaluate** on `E_R`, with explicit `--ours` | these producers default to the exact-split product `E_C` (e.g. `agreement_windows_receipt.py:62`, `compare_to_paper_fullcov.py:42`), so the run must name `E_R` explicitly and commit its argv |
| P13 | `remote_reduce.json`, Fig. 1's central-value source (`S/stageF/rebuild/scripts/make_fig1_q.py:83`; checks at `:103-107`) | earlier reduction | Fig. 1 | **re-evaluate**: a new `remote_reduce.json` from `E_R` (no code change) | Fig. 1 does not read the ROOT file |
| P14 | release arrays (`publication/release/figs/export_fig_arrays.py:72`, `fig_numbers.py:84-95`, RC7) | — | release | **unchanged** here | they already point at `E_C` and are stale (`docs/publication/release/RC7-README.md:22`). A new release candidate is a separate release decision |

### 2.2 Printed numbers

Each macro lives in `N/values.tex`. The declaration will commit `re2/inventory.tsv`, made by a script that greps
every use of each macro and each figure label across `N/`, so that the integration step has a complete,
re-runnable list rather than this summary.

| group | macros, with values.tex line | depends on | action |
|---|---|---|---|
| published comparison | `\sigTwoD` 3.073e-38 (:46), `\ratioTot` 1.011 (:48), `\medianBinRatio` 1.008 (:83), `\binsFive` / `\binsTen` / `\binsTwenty` 82.9 / 95.6 / 99.0 (:84-86), `\pullMean` / `\pullRMS` / `\pullRMSr` 0.074 / 0.564 / 0.56 (:87-89), `\chiPaper` 2.65 (:125) | `E_U` + the published result | re-evaluate (P12) |
| published-side values | `\sigTwoDpaper` 3.039e-38 (:47), `\uqPaper` 6.85 (:144), `\uqPaperIntegral` 4.61 (:149) | published result only | **unchanged** |
| exact-split comparators | `\chiPaperExact` 3.66 (:126), `\chiPaperExactSeeded` 3.57 (:127) | exact-split, configuration (b) | **unchanged** values; the text comparing them to `\chiPaper` is reworded |
| combined covariance | `\chiCombined` 0.964 (:129), `\chiCombinedLog` 0.987 (:132), `\chiCombinedSubStat` 6.01 (:134) | `E_U`, Q, published | re-evaluate (P11) |
| uncertainty budget | `\uqMedian` 6.45 (:140), `\uqIntegral` 4.75 (:146), `\uqSFiveMedian` 6.04 (:153), `\fluxBand` 3.75 (:155) | Q, `E_U` | re-evaluate (P11) |
| unattributed | `\rhoFluxMuon` 0.900 (:157); `\fpsAbove` 46 (:274) | no producer is named; `\fpsAbove` is consistent with 4.502/3.073 | **find the producer** before the rebuild; re-evaluate if it reads `E_U` or Q |
| purity coverage history | `\covTwoD*` (:104-121), `\pullFrac` / `\pullMeanAbs` / `\pullGauss` (:123-124) | the purity estimator at seed 1, signal only (VL169, `OUTCOME-20261005-2d-fixed-truth-coverage-fail.md`); no `E_U` or Q | **unchanged** values. They become history of the purity estimator, so the text that applies them to the quoted covariance is reworded |
| negative-weight study | `\nw*` (:363-394) | the hist and exact backends | **unchanged** |

Literal numbers printed outside `values.tex` that come from Q's blocks: the block tables (`tab:uq`,
`tab:variance-sources`, `tab:band-medians`, `tab:combine`, `N/sec_results.tex:189-215`, `N/app_statmethods.tex:83-106,
269-298,449-482`); the C08, S1 and C_PL text values (`N/sec_systematics.tex:24-114,164-186,294-330,405-494`); and the
ranks and conditioning (`N/app_statmethods.tex:739-818,849-894`). All are **re-evaluated** from `budget_Q` of `Q_R`.
`N/sec_systematics.tex:446-454` (pooled vs period) is re-evaluated from the rebuilt P8.

### 2.3 Figures

| figure | where it is printed | producer | action |
|---|---|---|---|
| `MEFHC_5iter_fig13`, `_xsec_proj_pt` / `_pz`, `_pull_full`, `_xsec_paper_pt_slices` / `_pz_slices` | `N/sec_results.tex:38-40,110,120,139`; `primer_body.tex:339` | `make_figures.sh:34-42`, which hard-codes the `E_U` filename (`:34`) | re-evaluate on `E_R` |
| `tension_*`, `model_comp_*` | `N/sec_results.tex:255-300` | `diagnose_tension.py`, `compare_to_models.py` | re-evaluate |
| `MEFHC_fig6_7_uncertainty_pt` / `_pz`, `uq_spread_2d`, `uq_corr_2d` | `N/sec_systematics.tex:54-55,153-154` | `run_rebuild.sh:97-101`; installed by sha (`make_figures.sh:166-169`) | re-evaluate on `Q_R` |
| `paper_fig1_validation` | `N/paper_body.tex:378` | `make_fig1_q.py` (P13); installed by sha (`make_figures.sh:170`) | re-evaluate |
| `MEFHC_5iter_xsec_eff_heatmap` | `N/sec_validation.tex:377` | `plot_2d_cross_section.py:346-366` (`hEff2D` from the `E_U` file) | re-evaluate, after a control shows `hEff2D` is the same under both estimators. If it is, the figure is unchanged |

### 2.4 Higher-dimensional statements that compare against the 2D result

| file:line | content | action |
|---|---|---|
| `N/sec_3d.tex:130-134` | "must reproduce the 2D result of §results"; +0.95 % (it reproduces only against the published bins: RE1-REPORT-2 §4, rulings PR #268 item 3); median marginal/2D 1.0016 (against `E_U`) | re-evaluate the median ratio and scatter against `E_R` with `re1_f_numbers.py` / `re1_report2_extras.py` on P3 (RE-1 P3 `8bc7e2d3…`). The wording is fixed at integration (DECISION item 3) |
| `N/sec_3d.tex:136-139,156,165-166,174-176` | χ² 4.98 "above the 2D values" (`\chiPaper`); the ~4.4 % scatter; "~70× tighter" | re-evaluate the scatter and the comparison against `E_R`, and the comparator `\chiPaper` (P12). The 4.98 itself is against the published covariance and is unchanged by RE-2 |
| `N/paper_body.tex:91,481-483`; `main_paper.tex:79-80`; `main_note.tex:75-77`; `sec_execsummary.tex:43-44`; `sec_summary.tex:30-33`; `sec_intro.tex:102-104`; `primer_body.tex:161-162,372-373,532-533`; `main_primer.tex:45` | "marginal normalizations agree at about 1–2 %" | **find the producer** (none is named). Re-evaluate the 3D link against `E_R` |
| `N/sec_fps.tex:47-50,112-113`; `sec_summary.tex:110` | the control reproduces `\sigTwoD`; σ_ext is `\fpsAbove` above it | re-evaluate after P12 |
| `N/sec_5d.tex:56-57` | the 2D reproduction row (configurations (a), (b)) | reword |

The 5D/joint-test numbers do not depend on `E_U`: they project the configuration (e) 5D unfold. This includes
`N/sec_joint.tex:563-615`, `N/sec_eavailw.tex:49-53` and the joint-test references to MINERvA's published 2D result.
They are **unchanged**.

### 2.5 Statements describing the estimator (reword at adoption)

- `N/main_note.tex:92-97`, `sec_execsummary.tex:136`, `sec_method.tex:73-74,195-198,216-218,230-232`: "central values
  and uncertainties use the purity subtraction".
- `N/app_negweight.tex:18-19,250,319-320,359-364`: purity is the default for the reproduction measurement.
- `N/paper_body.tex:285-289,310-313,402-404`: configuration (a) defined with purity.
- `N/sec_summary.tex:58-60`: "the quoted central values keep the purity bias".
- `N/app_codebase.tex:17-22`.
- `N/result_status_rows.tex:18`, and the records document: `app_history.tex:65-76,202` (values), `app_provenance.tex:43-45`
  (`E_U` path and sha). Also the generated `records_estimators.tex` and `records_results_index.tex`, which regenerate
  from the registry.
- `docs/analysis-note/check_sec4_receipts.py:120-133` binds `\uqMedian`, `\uqIntegral` and the S1 median. Its
  computed side reads the Q receipts, so it must be repointed at `Q_R`.

### 2.6 Validation history (§5.2 and the appendices)

| item | estimator | action | reason |
|---|---|---|---|
| VL169 fixed-truth coverage FAIL; VL170 rescoring; KI-85 single-toy test (`N/sec_validation.tex:210-318`; `OUTCOME-20261005-2d-fixed-truth-coverage-fail.md`) | purity, seed 1, signal only | **unchanged** as a record. The text that ties it to the quoted covariance is reworded: it tests the purity band at seed 1, not `Q_R` | it was never a test of Q: Q's adoption excludes "a coverage, calibration or validation statement about the adopted covariance" (`DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md:23`) |
| 1A closures, the 200-toy pull diagnostic, the 5- vs 10-iteration and hist vs exact checks (`N/sec_validation.tex:22-133,334-373`) | signal-only closures (no background) | **unchanged** | no background enters, so the background treatment cannot change them |
| exact-split analyses (`N/app_statmethods.tex:645-733,820-847,909-985`) | configuration (b) | **unchanged** | not `E_U` |
| RE-1 C2 (`re1/RE1-REPORT-2.md` §2) | both arms | **unchanged**; it is the evidence for the switch | — |
| a coverage test of `Q_R` | — | **not in this plan** (§6) | none exists for either covariance |

## 3. The code RE-2 needs

**What no existing path can do.** The refinement size is fixed at 100/8 in the driver:
- `refine_stay_positive` builds `LGBMClassifier(n_estimators=100, num_leaves=8, …)` (`D:402-407`) and is passed only
  `random_state` (`D:2037-2041`).
- So the driver's own `--bkg-mode negweight-refined` gives a different estimator from `E_R`.
- The driver's bootstrap never resamples the background: "intentionally NOT bootstrapped" (`D:2008-2017`).
- `driver_p1.py`'s three-stream bootstrap refuses every mode except purity (`2d-unfolding/driver_p1.py:1582-1587`).
- `re1_2d.py` has universes and laterals switched off (`universe_branch=None`, `re1_2d.py:153-158`), and has no
  bootstrap or seed option (`:70`).

**Proposal: `2d-unfolding/re2/re2_2d.py`, a new path in this lane's file set.**
- It extends `re1_2d.py`, calling the driver's and `driver_p1.py`'s loaders and bootstrap code as modules, as
  `re1_2d.py` does now.
- It adds `--universe` / `--lateral-file`, `--bootstrap-seed` with `--bootstrap-streams three|bkg`, `--seed`, and
  per-period inputs.
- Its `--arm purity|refined` switch is unchanged.
- In the refined arm, the background stream resamples the background MC rows that enter as −w events, by the same
  Poisson stream key as `driver_p1.py`'s purity background stream. Then the refinement is fitted.
- No existing producer is edited.
- **Decision for the director (R1):** this design, or a copy of the driver with a refinement-size option. The
  recommendation is the extension, because RE-1's driver-equivalence tests and K1 already cover its central path.

**Its unit tests (declared with the code):**
- the purity arm equals the driver and `driver_p1.py` bit for bit, on a synthetic omnifile, for a universe, a
  lateral, a three-stream replica, a background-only replica and a period input;
- the refined arm, with the override removed, equals the driver's `negweight-refined` bit for bit (the RE-1
  `DriverEquivalence` precedent);
- the background stream changes only the −w rows, and has the expected Poisson mean.

## 4. Costs and the ceiling

### 4.1 Measured unit costs

| unit | measured | node-h | source |
|---|---|---|---|
| refined vs purity, same path, same input | refined arm 214.1 s, purity arm 202.5 s on 64 CPUs (mean of 20 seeds); refinement fit 7.9 s | ratio **1.057** | the committed C2 products' metadata, `re1/run2/readouts/nominal_s{1..20}.npz` |
| refined data unfold (D2) | 428.9 s on 64 CPUs, from the cache | 0.030 | `d2_data_refined.npz` metadata (`seconds`); J3 60129319, 3,264 s, 0.9067 node-h for 42 unfolds (`re1/run2/ledger.tsv`) |
| CV data unfold, driver | 836 s, 64 CPUs, shared (XR L0); 649–2,003 s in the pilot | 0.058; 0.0754 mean, 0.0933 p84 | `xr-linux/REPORT.md:243`; `S/stageC/pilot/REPORT.md:278` |
| universe unfold, selective read | packed two per node, 736–910 s per pack | ≈ 0.115 per unfold (3.5611 / 31) | `S/stageC/production/REPORT.md:189` |
| universe unfold, all branches | 2,497 s at 128 CPUs | 0.3468 | `S/stageC/pilot/REPORT.md:281` |
| lateral | 1,911–2,848 s, 128 CPUs | 0.27–0.40 each | `S/stageC/production/REPORT.md:396-405` |
| bootstrap replica (S1), packed 4 per node | 607–774 s per pack | ≈ 0.0446 (13.2003 / 296) | `S/stageC/production/REPORT.md:191` |
| S2 and S4(i) replicas | 605–663 s per pack | ≈ 0.043 | the same, `:192-193` |
| period central | 440–866 s, 64 shared CPUs | 0.031–0.060 | `S/period-unfold-20261014/REPORT.md:117-132` |
| Stage C production, total | 539 allocations, 153 ran | **29.0297** | `S/stageC/production/REPORT.md:24` |

**What is not measured:** a refined universe, lateral, bootstrap or period unit. The plan uses the purity unit × a
**planning factor of 1.25**. That covers the measured 1.057 refinement overhead plus loader and path differences.
A pilot (J0) measures the real units before the production jobs are sized, and is a gate (§5).

### 4.2 Projected charge per job (packed as in Stage C production)

| job | content | count | unit (purity, node-h) | projected at 1.25 | worst case (1.25×) |
|---|---|---|---|---|---|
| J0 pilot and controls | K1 suite (§5.1); unit timing on 4 universes, 1 lateral, 8 replicas, 1 period | — | measured | 1.5 | 1.9 |
| J1 central and C0 | `E_R` (ROOT, all objects); `C0_unit`; `C0_cv` | 3 | 0.0933 | 0.35 | 0.44 |
| J2 universes | 175 July bands, selective read | 175 | 0.115 | 25.2 | 31.4 |
| J3 laterals | the 10 active lateral files | 10 | 0.40 | 5.0 | 6.3 |
| J4 S1 | three-stream replicas | 300 | 0.0446 | 16.7 | 20.9 |
| J5 S2 | background-only replicas | 100 | 0.043 | 5.4 | 6.7 |
| J6 S4(i) | 20 replicas × 4 seeds | 80 | 0.043 | 4.3 | 5.4 |
| J7 S4(ii) | 7 universes × 5 seed sets + CV at 4 seeds | 39 | 0.115 / 0.0933 | 5.5 | 6.8 |
| J8 periods | control + 3 × 2 seeds + 30 replicas | 37 | 0.060 | 2.8 | 3.5 |
| rollup, C_PL, Q, Stage F, receipts, figures | login node | — | 0 | 0 | 0 |
| **total** | | | | **66.8** | **83.4** |

- **Proposed grant: ≤ 90 node-h,** regular or shared QOS, each job < 12 h.
- If the selective universe read cannot be used with the refined path, the all-branch unit (0.3468) applies. J2
  then becomes 75.8 projected / 94.8 worst, and the total 117.4 / 146.7. That is still inside the remaining
  ceiling, but it would need the grant raised. J0 settles this.

### 4.3 The ceiling

- **The definition is in §3 item 2** of
  [`AUTHORIZATION-20261012-2d-closeout-delegation.md`](../../../../../AUTHORIZATION-20261012-2d-closeout-delegation.md)
  (`:52-58`), not §2. The DECISION's "§2" (`DECISION-20261023…:32`) mis-cites it.
- **The ceiling:** "≤ 700 charged CPU node-hours on m3246, recomputed from `sacct` by every gate".
- **Spent under it: 39.4714 node-h.** Each grant's charge below was re-read against live `sacct` on 2026-10-23, and
  every job matches:

| grant | cap | charged | record |
|---|---|---|---|
| Stages A–B | 2.0 | 0 | `AUTHORIZATION-20261012-2d-closeout-stageAB.md:26`; `S/stageA/REPORT.md:28`; `S/stageB/REPORT.md:29` |
| flux repair | 1.0 | 0 | `AUTHORIZATION-20261012-2d-closeout-fluxrepair.md:45`; `S/c04-repair/REPORT.md:44` |
| Stage B diagnostics | 3.0 | 1.2524 | `S/stageB/diagnostics/REPORT.md:32` |
| Stage C pilot | 20.0 | 7.2479 | `S/stageC/pilot/REPORT.md:24` |
| period-unfold test | 6.0 | 1.9414 | `S/period-unfold-20261014/REPORT.md:24` |
| Stage C production | 100.0 | 29.0297 | `S/stageC/production/REPORT.md:24` |
| **total** | **132.0** | **39.4714** | |

- **Remaining: 660.53 node-h** against charges. Against committed grants it is 568.0; whether a finished grant's
  unused cap returns to the pool is not recorded.
- **RE-1's 1.680 node-h** (`re1/ledger.txt:4` + `re1/run2/ledger.tsv`) ran under DECISION-20261020's 30 node-h grant.
  No record puts it under the 700. If the director counts it, 658.85 remains.
- SF-1, IBU-1 and JIT-1 are outside the 700 by their own records (`DECISION-20261019-joseph-methods-first-and-measurement-compute.md:56-57`).
- **The RE-2 worst case (83.4, or 146.7 with all-branch reads) fits inside what remains.** The cost does not go back
  to Joseph.
- The group pool is the tighter limit: `iris` showed m3246 at 2,286.8 node-h left on 2026-10-23.

## 5. Controls, seeds, decision rules and stops

### 5.1 Controls (each before its product is used)

Each control below fails closed: a failure stops the jobs that depend on it.
- **K1-C** (central): `re2_2d.py --arm purity` on the CV omnifile reproduces `E_U`'s `hXSec2D` on its 205 cells to
  ≤ 1e-8 relative. The precedent is K1-2D: 2.3e-13 at 64 threads (`re1/RE1-REPORT-2.md` §1). The refined arm
  reproduces D2 `71ca3e5f…` bit for bit at 64 threads.
- **K1-U** (universes): the purity arm reproduces three July `pn/` universes, chosen in the declaration, to ≤ 1e-8.
  The precedent is Stage C pilot K1 (`S/stageC/pilot/REPORT.md:28-41`).
- **K1-L** (laterals): the purity arm reproduces one Stage C S3 lateral product to ≤ 1e-8.
- **K1-B** (bootstrap): the purity arm, three-stream and background-only, reproduces one S1 and one S2 replica of
  Stage C production (same seed and stream) to ≤ 1e-8.
  - `C0_unit`: with all weights set to 1, the bootstrap equals the CV, in both arms.
- **K1-P** (periods): the purity arm reproduces `pu_CTRL` and `pu_PA_s42` (`S/period-unfold-20261014/outputs/analysis.json`) to ≤ 1e-8.
- **K1-R** (the refined path): with the 400/31 override removed, the refined arm equals the driver's own
  `negweight-refined` bit for bit on one universe.
- **K1-roll** (post-processing): `s5_rollup.py`, `playlist_term.py` and `combine_s5.py`, with their pins made
  parameters, re-run on the **purity** inputs and reproduce `6689d2fc…`, `c1723cb5…` and `8ccb4d72…` bit for bit.
  Only then do they run on the refined inputs. The same holds for `run_rebuild.sh` against its current outputs, and
  for every P12 receipt against its committed file.
- **Mode guard:** every refined product records `bkg_mode = negweight-refined` and the 400/31 classifier parameters.
  Every consumer refuses an input of the other mode. No such check exists in the C_PL scripts today.

### 5.2 Seeds

- Estimator seed 42: OmniFold estimators `random_state` 42/43/44, refinement 45, as `E_U` and D2 used.
- The bootstrap seeds and stream keys of Stage C production, replica for replica, so every refined replica has a
  paired purity replica.
- The seed panel {42, 45, 48, 51, 54} and the period seeds {42, 43}, as before.
- No new seed is introduced.

### 5.3 Readouts and rules fixed before any output

- **Readouts (descriptive):**
  - per block (universe, stat, C08, C_PL) and for `Q_R`: the median per-cell σ, the integral σ, and the per-cell
    ratio to the purity block, with percentiles;
  - `E_R` − `E_U` in `Q_R`'s σ, which is D2 re-read in the new σ;
  - the published comparison (P12) and `budget_Q` of `Q_R`;
  - the rank and conditioning of `Q_R`.
- **Structural acceptance:** each must hold, or `Q_R` is not delivered and the report says why.
  - `Q_R` is symmetric and positive semi-definite to the tolerance S5 used.
  - It is on exactly `E_U`'s 205 cells. If `E_R`'s reported set differs, the run stops for the director.
  - Every block's construction is unchanged from S5 / C_PL / the combination, except for the estimator.
- **No threshold selects the result.** Adopting `E_R` and `Q_R` is Joseph's decision, from the report. The plan
  fixes no σ-ratio band that would choose between estimators.

### 5.4 What stops the rebuild

- **A failed control.** Any K1 fails: the dependent jobs do not run.
- **Time and charge.**
  - A job beyond 1.25× its projection is stopped by Slurm and reported. It is never resubmitted without the
    director.
  - A split of a declared job's limit is raised first.
- **The J0 gate.** If the measured refined units, times the declared counts, exceed the grant, the plan returns to
  the director before J2.
- **Refinement health.** Any refined unfold whose refinement clips more than 1 % of the signed mass, or whose
  refined/signed sum leaves [0.99, 1.01]. RE-1 saw at most 4.6e-4 clipped and 1.000018.
- **Input integrity.** A pscratch-only input fails its digest. These are the universe omnifile `220c479e…`
  (171 GB, present on 2026-10-23), the July sweep and the period inputs.
- **Purity products.** Any purity product would be overwritten. RE-2 writes only to a new namespace.

## 6. Not in this plan

- **A coverage test of `Q_R`.** None exists for Q either: its adoption excludes any coverage statement (`DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md:23`). The purity band's test
  (VL169/VL170) cost 13.33 + 18.1 node-h. A refined coverage test would be a separate grant.
- **A new release candidate** (P14), the newer FHC open-data release, and the 3D/4D covariances.

## 7. What the note and paper need in the interim

These are facts for the director's wording (DECISION item 1: "the note and paper print the current 2D result, and
say plainly …"):
1. **The quoted 2D result is still `E_U`.** It is configuration (a), purity subtraction, with Q = S5 total + C_PL
   (`DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md`).
2. **RE-1's C2:**
   - In a nominal-truth 2D closure with background (20 seeds, both estimators on the same pseudo-data), the purity
     estimator's mean residual exceeds 1 σ_stat in 14 of 205 cells, up to +5.89 σ_stat.
   - The flagged cells are the lowest-p∥ row (1.5–2.0 GeV/c) and five cells at the high-pT boundary.
   - The refined estimator stays within ±0.44 σ_stat in every cell.
   - The integrated difference is −0.198 %.
   - This is a closure, not a coverage test (`re1/RE1-REPORT-2.md` §2).
3. **On data,** the refined central value differs from `E_U` by at most 0.497 σ_total (median 0.060), with an integral
   change of −0.139 % (§3 there).
4. **Joseph decided on 2026-10-23** to move the adopted 2D result to the refined estimator, with its covariance, its
   published comparison and its printed numbers rebuilt. Until that lands, the quoted numbers are `E_U`'s.
5. **OI-6** (the background-treatment revisit) is in progress, with C2 as its first result (DECISION item 2).
6. **Unchanged:**
   - the published-result values;
   - the exact-split comparators;
   - the signal-only closures;
   - the 5D/joint-test results, which already use configuration (e).
   The purity coverage test (VL169) stays a test of the purity band at seed 1, not of the quoted covariance.

## 8. Decisions for the director before a declaration

| # | decision | recommended |
|---|---|---|
| R1 | the code path | extend `re1_2d.py` as `re2/re2_2d.py` (§3) |
| R2 | rebuild scope | all four Q blocks, as the DECISION says "its covariance" |
| R3 | the refined background stream | Poisson over the −w background rows under `driver_p1.py`'s stream key, then refit the refinement per replica |
| R4 | the registry | add the 2D estimator (e.g. `a-refined-400-31`) before any job |
| R5 | the grant | ≤ 90 node-h after J0, raised only if J0 shows all-branch reads are needed (≤ 150) |
| R6 | whether RE-1's 1.68 node-h counts against the 700 | the director's call; the plan fits either way |
| R7 | the unattributed numbers (`\rhoFluxMuon`, `\fpsAbove`, the 1–2 % normalizations) | find their producers in the declaration; any that cannot be found are reported as not re-evaluated |
