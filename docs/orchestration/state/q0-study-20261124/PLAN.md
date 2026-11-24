# The q0 study: how much independent information reco q0 carries beyond reco E_avail and the muon (plan, fixed before computing)

**Who and why.** The director requested this for Joseph on 2026-11-24, before Joseph and Ben choose the 5D measurement's
variables and before Ben's (b) is declared. It is **descriptive**: it licenses no note wording, and the variable
choice stays Joseph's and Ben's. It uses simulation only, at 0 node-h. tier3-design commits this plan before any
quantity below is computed.

## 1. Definitions (file:line)

- **q0, the calorimetric recoil:** `<tree>_recoil_E`, the full energy transfer. RecoQ3 and RecoW use it:
  `MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h:208–209` (RecoQ3) and `:227–228` (RecoW). Its definition
  comment is at `:199`.
- **Reco E_avail:** `NewEavail()`, which is (tracker recoil − tracker muon fuzz) + (ECAL recoil − ECAL muon fuzz),
  times 1.17. See `CVUniverse.h:185–192`.
- **Reco q3:** `RecoQ3()`, `CVUniverse.h:208–219`. It uses Q² = 2 Eν (Eμ − pμ cos θμ) − m_μ², with Eν = Eμ + q0 and
  Q² clamped at 0, so q3 = √(Q² + q0²).
- **q0 is not stored in the omnifile.** It is recovered exactly from (pT, p∥, reco q3) by inverting RecoQ3, as
  M4-W did:
  - `docs/orchestration/state/2d-closeout/stageF/methods/M4-W-RECORD.md:104`;
  - the code is `docs/orchestration/state/2d-closeout/stageF/methods/m4-w/probe_omni.py:62–77`, with
    M_mu = 105.6583 MeV at `m4-w/common.py:7`;
  - Eμ = √(pT² + p∥² + M_mu²), a = Eμ − p∥, c = 2 Eμ a − M_mu², and q0 = −a + √(a² − c + q3²);
  - if the resulting Q² = 2 (Eμ + q0) a − M_mu² is < 0, then RecoQ3's clamp fired and q0 = q3 (`probe_omni.py:73–75`).
  - On sim, M4-W measured 20,498,013 passing rows with a W-identity max abs residual of 3.2e-7 MeV, and the Q² clamp
    fired 0 times (`M4-W-RECORD.md:106–108`).
- **The reco W identity**, used as a control: W² = (M̄ + q0)² − q3², clamped at 0 (`probe_omni.py:76–77`), with
  M̄ = (1.5 M_n + M_p)/2.5 (`m4-w/common.py:6`).
- **Truth q3 and truth W:** the `MC_q3` and `MC_W` branches (named as in
  `docs/orchestration/state/eavail-switch-pricing-20261031/step0/eavail_step0.py:51`). They are on the
  `mc_signal_reco` tree beside the reco branches: `.../step0/step0-treecheck-transcript.txt:6` lists the
  signal-only branches `sim, sim_W, sim_eavail, sim_pass, sim_pz, sim_q3, w_reco`.
- **Units:** the omnifile stores GeV (`probe_omni.py:66` multiplies by 1000). Everything below is in GeV.

## 2. Inputs (simulation only)

- **The file:** `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/runEventLoopOmniFold_5D_MEFHC.root`, sha256
  `b6d2651cfdbc52790cc7ed6032f2062a3e0ea50c12d63725beba29098dd5175a`. It is the `cv_omnifile` in
  `docs/orchestration/state/s5c/contract.json`, and the note's 5D unfold reads its events through `of_inputs_5d.npz`,
  which P2 proved equal (contract.json `/identities/input_npz/note`).
- **The tree:** `mc_signal_reco` only. The rows used are those with `sim_pass` true; 20,498,013 are expected
  (`step0-treecheck-transcript.txt:9`). **The `data` tree and every "measured" key are never opened.**
- **The weights:** `w_reco`, the CV reco weight.
- **The extract** runs once on a login node under the director's GO for its sha (`q0_extract.py` with its connect). It
  writes, for the passing rows:
  - float32 columns: `pt, pz, eavail, q3, W` (reco), `q0` (recovered in float64 on the node, then stored as float32),
    `w_reco`, `q3_true`, `W_true`;
  - int8 columns: `q0_status` (0 recovered, 1 RecoQ3's Q² clamp fired so q0 = q3, 2 a non-finite input or output) and
    `in_truth_ps` (the truth phase-space gate of `probe_omni.py:13–14`: 0 ≤ pT ≤ 4.5, 1.5 ≤ p∥ ≤ 60, atan2 < 20°).
- **The extract's STOPs:**
  - the omnifile's sha256 (read O_NOATIME) is not the pin;
  - a named branch is missing;
  - the passing count is not 20,498,013;
  - the omnifile's atime changed;
  - **the recovery control fails:** max |W − W(q0)| > 1e-6 GeV over rows with q0_status = 0 and W² ≥ 0.

## 3. The readings

All quantities are weighted by `w_reco`. Rows with `w_reco ≤ 0` or a non-finite value in a reading's columns are
excluded from that reading, and their count and weight fraction are reported. Weighted quantiles use the weighted CDF
with linear interpolation, evaluated at the cumulative-weight midpoints.

**The coarse muon grid.** It takes the 2D analysis grid's edges (`2d-unfolding/re2/re2_driver.py:44–48`) and uses
these subsets of them:
- pT: 0, 0.25, 0.47, 0.70, 1.00, 1.50, 4.50 GeV;
- p∥: 1.5, 3.0, 4.5, 6.0, 9.0, 20.0, 60.0 GeV.
That gives 36 cells, bin-inclusive on the left; the last edge is inclusive. **The merge rule, applied before any
reading and on unweighted counts of the eligible rows only:** a cell with fewer than 50,000 rows merges into the
neighbour of lower pT in the same p∥ row, and the lowest-pT cell merges into the next higher one. This repeats until no
cell is below 50,000. Rows outside the grid form an "outside" group, which is reported separately and included in
"overall".

1. **Correlation of q0 with E_avail.** The weighted Pearson correlation, and the weighted Spearman correlation (the
   weighted Pearson of weighted mid-ranks). They are given overall and per merged coarse cell, on all passing rows
   with q0_status = 0.
2. **The conditional spread of q0 given E_avail.** The weighted 16 %, 50 % and 84 % quantiles of q0 in the declared
   reco E_avail bins 0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0 and 100 GeV. These are the 5D fine E_avail edges,
   `eavail_step0.py:41–47`, row 3. Each bin also reports its row count and weight. This is on all passing rows with
   q0_status = 0.
3. **What q0 adds for truth q3, and separately for truth W.**
   - **The regressor:** scikit-learn `HistGradientBoostingRegressor`. The director's brief named LightGBM; sklearn's
     histogram GBM is equivalent for this descriptive purpose and leaves the laptop's shared Python untouched, so no
     install is needed (the director's ruling, 2026-11-24).
   - **Hyperparameters:** loss = "squared_error", learning_rate = 0.1, max_iter = 300, max_leaf_nodes = 63,
     min_samples_leaf = 200, l2_regularization = 0.0, max_bins = 255, early_stopping = False,
     random_state = 20261124. The fit uses sample_weight = w_reco. Both predictors use the same thread count:
     OMP_NUM_THREADS = 4 for every fit and predict.
   - **Two predictors per target:** A uses features (pT, p∥, E_avail); B uses (pT, p∥, E_avail, q0).
   - **The split:**
     - The eligible rows (q0_status = 0, finite target, w_reco > 0) are split 50/50 by
       `np.random.default_rng(20261124).permutation`.
     - The regressors fit on a seeded subsample of **2,000,000 rows of the first half** and are scored on
       **2,000,000 rows of the second half**, drawn by `np.random.default_rng(20261125)` without replacement. Both
       predictors use the same rows.
     - The subsample is fixed here. Correlations and quantiles (readings 1, 2, 4) use all passing rows.
   - **The scores:** residual r = truth − prediction on the scoring rows. The 68 % half-width is (weighted q84 −
     weighted q16)/2 of r, and the RMS is √(weighted mean of r²).
   - **Reported:** both widths for A and for B, and the ratios B/A. These are given overall and per merged coarse cell;
     a cell with fewer than 2,000 scoring rows reports its count only.
4. **The recovery fractions.** The fraction of passing rows, unweighted and weighted, with q0 ≤ 0, with q0_status = 1
   (Q² clamp) and with q0_status = 2 (non-finite). Also the recovery control's max |W − W(q0)| and the count of rows
   where W² < 0 (W clamped to 0).

## 4. Outputs and handling

- The outputs are `results.json` and `results.txt`, written by `q0_analyze.py`, with the extract's npz sha256 checked
  against the connect's record before use.
- The plan, the code, the extract records and the outputs, all with their sha256, go in a PR. **The results go to the
  director first.**
- The local analysis runs after the MSR rerun (`run-local-3`) finishes, so the two don't compete for the laptop.
- Nothing here changes any note text or any declared analysis.
