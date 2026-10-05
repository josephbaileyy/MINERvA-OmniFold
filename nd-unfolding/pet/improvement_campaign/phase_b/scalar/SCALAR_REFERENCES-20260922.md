# Phase B1 — scalar, response-aware references for the historical endpoint (2026-09-22)

**Scope.** PET is diagnostic method development. Everything here is simulation only (signal MC of
`G2_FPS_MEFHC_P12.npz`; no measured or background member of the npz is opened). Nothing here is a
publication adoption, an uncertainty product, a central-value change, a Gate-6 action, or a new
threshold. The historical comparison, its report, thresholds and verdict are untouched; every number
below is scored on that comparison's endpoint by that comparison's own code. A reference or recovery
value here is a measurement on one fixed event sample (the historical halves), not a bound.

## Bottom line (all MEASURED on the historical halves unless labelled)

Historical (8-seed means, `campaign_report.json`): PET ours **0.304**, Gregor's arm **0.417**, floor
**0.556** = 0.8 × reference **0.695** (k = 3). Scalar references at the historical k = 3 (seeds 1-3,
mean ± sd):

| estimator at k = 3 | aggregate | low | moderate | good |
|---|---|---|---|---|
| reference `1-(1-a)^k` (historical construction) | 0.695 | 0.014 | 0.777 | 0.975 |
| floor (0.8 × / 0.6 × reference) | 0.556 | 0.008 | 0.466 | 0.585 |
| binned IBU, reco = muon cells, misses carried (engine) | 0.164 | −0.001 | 0.072 | 0.348 |
| binned IBU, reco = muon cells × reco E_avail, misses carried (engine) | 0.472 | 0.011 | 0.577 | 0.866 |
| scalar OmniFold HGB, muon | 0.140 ± 0.003 | −0.009 | 0.069 | 0.287 |
| scalar OmniFold MLP, muon | 0.211 ± 0.045 | 0.011 | 0.132 | 0.398 |
| scalar OmniFold HGB, muon + reco E_avail | 0.412 ± 0.005 | 0.041 | 0.472 | 0.733 |
| scalar OmniFold HGB, muon + all reco hadronic summaries | 0.415 ± 0.009 | 0.043 | 0.478 | 0.737 |
| scalar OmniFold MLP, muon + all reco hadronic summaries | 0.486 ± 0.065 | 0.063 | 0.552 | 0.849 |
| historical PET ours / theirs (8-seed means) | 0.304 / 0.417 | 0.056 / 0.153 | 0.226 / 0.414 | 0.538 / 0.689 |
| *reference MODEL realized on the scored endpoint* (`diag`, engine normalization) | 0.523 | 0.032 | 0.743 | 0.896 |
| *reference MODEL, analytic, on the scored 7-bin marginal* | 0.578 | — | — | — |
| *oracle truth-level push (the injected function itself)* | 0.984 | 0.991 | 0.973 | 0.959 |

1. **No scalar, response-aware estimator reaches the 0.556 floor at k = 3** on this endpoint. Under
   the historical pseudo-data normalization none reaches the 0.695 reference at any k ≤ 20 except
   textbook efficiency-corrected IBU with reco E_avail (0.923 at k = 2, then degrading; §4.3); with
   rate-matched normalization binned IBU with reco E_avail reaches 0.727 at k = 20. Gregor's arm (0.417) sits at the
   level of the scalar GBDT that is given reco E_avail (0.41); ours (0.304) sits between the
   muon-only references (0.14-0.21) and the E_avail-aware ones (0.41-0.49). **The shortfall below
   the floor is therefore not PET-specific** (MEASURED); how much of ours-vs-theirs is representation
   is not established here.
2. **The 0.695 reference does not describe the scored object.** It weights `1-(1-a)^k` by the
   displacement of the (pT, p‖) cell spectrum; applied under its own assumptions (acceptance only,
   no smearing, misses carried) to the seven-bin E_avail marginal the score is computed on, the same
   model gives **0.578** at k = 3 (0.619 before the score's renormalization); realized on the actual
   halves with the historical pseudo-data normalization it gives **0.523** — below the 0.556 floor
   derived from it. MEASURED (`results/reference_decomposition.json`, `results/ibu.json`, `diag`).
3. **Reco E_avail is the decisive step-1 input** (MEASURED): adding it lifts binned IBU at k = 3 from
   0.164 to 0.472 and scalar GBDT from 0.140 to 0.412; the other hadronic summaries add ≤ 0.01 to the
   GBDT (0.412 → 0.415).
4. **Recovery keeps rising with iterations** for every carry-misses estimator (the misses are carried
   at the prior, so each iteration moves only the accepted fraction): e.g. IBU muon × reco E_avail
   0.472 (k = 3) → 0.648 (k = 10) → 0.683 (best, k = 15); GBDT 0.412 → 0.498 → 0.524 (k = 20); MLP
   (all summaries) 0.486 → 0.578 → 0.654 (k = 15). The historical three iterations sit on the
   steep part of these curves. MEASURED.
5. **The historical pseudo-data normalization costs recovery** (MEASURED): the tilt lowers the
   accepted fraction by a factor 0.898, which the closure's normalization ignores; rate-matched
   normalization adds +0.036 (IBU muon × reco E_avail, k = 3), +0.052 (muon), +0.034 (`diag`).
6. **Truth-only learnability** (a learnability diagnostic of the step-2 input set, NOT a bound):
   with true E_avail among the inputs a GBDT learns the known tilt to 0.999 held-out (MLP 0.91-0.94);
   from true pT, p‖ alone only **0.33 ± 0.001** (GBDT) / 0.35 (MLP), low-acceptance region 0.05.
   INFERRED, not established: a step 2 whose only explicit globals are pT and p‖ (the historical
   PET truth side) must extract E_avail from its particle cloud to exceed ~0.33; whether it does is
   a Phase-B PET measurement, not made here.
7. **The low-acceptance region** (31 % of truth mass): at k = 3 every carry-misses estimator scores
   ≤ 0.063 there (PET theirs 0.153, ours 0.056); only by k = 20 do the MLP (0.30 ± 0.20) and `diag`
   (0.19) move appreciably. Efficiency-corrected IBU reaches 0.56-0.76 at k = 1-10 and then turns
   unstable — the region is not unresolvable, but recovering it requires dividing by acceptance
   ≈ 0.006, which the engine's carry-misses update never does.


## 1. The historical endpoint, reproduced from its own code

`prepare_populations.py` imports the comparison modules at `68cf9d29` (each loaded file's git blob id
is checked against that tree; `scalar_common.PINNED_BLOBS`) and refuses on any disagreement.
Job `58741903` at `36733301`, record `results/populations.json` (sha256 in `results/summary.json`):
**31 / 31 checks agree.**

| check | recomputed | report |
|---|---|---|
| closure npz sha256 | `fa6b3463…a29625` | same |
| half A / half B scored rows; half-B rows dropped (not truth-passing) | 600130 / 600111; 32 | same |
| subsample (`default_rng(0).choice(N, 2e6)`) = recorded `mc_indices` | equal | — |
| stage split + `deterministic_halves` replay = recorded `dump_rows_a/b` | equal | — |
| tilt replay (`clipped_exponential_tilt` on half A) vs recorded `tilt_a` | max dev 0 | — |
| aggregate reference `ceiling(a, d, 3)` | 0.6949731568655357 | 0.6949731568655361 |
| regional references low / poor / moderate / good | 0.013961 / 0.366538 / 0.776528 / 0.975479 | same (≤ 2e-16) |
| `score_run` on historical ours-127 / theirs-127 | 0.3256332443 / 0.4934889970 | same (≤ 1e-15) |
| this lane's `score_push` vs `score_run`, aggregate and every region | bit-identical | — |
| identity sidecar sha256 vs `frozen_design.PINNED_HASHES` | equal | — |
| all 16 final runs share the halves | 16 / 16 | — |

Populations (per half, 600,143 rows each): pass_reco & pass_truth (the step-1 rows) 250,501 (A) /
251,077 (B); truth-only misses 349,629 / 349,034; reco-only rows 13 / 32 (fakes: excluded from step 1
on both sides by the historical driver and inert in step 2); w_truth-weighted acceptance f = 0.4155
(B). **Measured:** the tilt lowers half A's accepted fraction to f_A = 0.3731 against f_B = 0.4155,
ratio **0.898**. The historical driver normalizes the pseudo-data to the prior's *accepted* total
(both `DataLoader(normalize=True)` to 1e6), which equates the two, i.e. it scales the pseudo-data up
by 1/0.898 relative to the prior's misses. This is a property of the historical closure, affecting
every estimator run through it (PET included); its size is measured below (`engine` vs
`rate_matched` rows).

## 2. Inputs (exact fields, units)

From `results/populations.json` (`fields`) and the producer `dump_pointcloud_inputs.py:76-82`:

| name | npz member / column | branch | definition | unit |
|---|---|---|---|---|
| reco_pt, reco_pparallel | `reco_scalars[:,0:2]` | `sim`, `sim_pz` | reconstructed muon pT, p‖ | GeV |
| reco_eavail | `reco_scalars[:,2]` | `sim_eavail` | `NewEavail()` — the 3D E_avail pipeline's reconstructed available energy (`3d-unfolding/3D_OMNIFOLD_STATUS.md`, C1) | GeV |
| reco_q3 | `reco_scalars[:,3]` | `sim_q3` | `RecoQ3()` from reco muon + recoil energy | GeV |
| stored_token_sumE | `part_reco[...,0]` via `build_reco_cloud` | reco clusters | Σ energy of the ≤12 STORED clusters (post-truncation) | GeV |
| stored_token_n | same | | number of stored clusters with E ≠ 0 (≤12) | — |
| true_eavail, true_pt, true_pparallel, true_q3 | `truth_scalars[:,2,0,1,3]` | `MC_eavail`, `MC`, `MC_pz`, `MC_q3` | `GetEAvailableTrue()`, truth muon, `Getq3True()` | GeV |

Reco columns are `-9999` on `!pass_reco` rows and are only read on pass_reco & pass_truth rows (0
non-finite, 0 sentinel there; 4 / 3 negative reco E_avail). True q3 is non-finite on 15 (A) / 21 (B)
truth-passing rows; those are median-filled and counted in every result file (`nonfinite_fills`).
Reco input sets: **(a) `muon`** = reco pT, p‖; **`muon_eavail`** = (a) + reco E_avail (the single
controlled addition); **(b) `muon_had`** = (a) + reco E_avail, reco q3, stored-token ΣE, token count.
Step 2 always reads the four truth scalars (`truth4`). No truth column can enter a reco set
(`features.assert_reco_only`, tested).

## 3. Methods

**Engine semantics mirrored** (`omnifold_nn/omnifold/omnifold.py`, and consistent with A1's runtime
audit, branch `pet-improvement-20260922-phaseA1`, `phase_a/INTENDED_VS_EXECUTED-20260922.md`): step 1
class 0 = prior rows at `push · w_reco · pass_reco` (pass_reco here = pass_reco & pass_gen, as the
driver passes it; other rows weight 0), class 1 = pseudo-data at `w_reco · tilt`, both normalized to
1e6, classes not rebalanced; pull = push · r on step-1 rows, = push elsewhere (misses carried). Step 2
duplicates the pass_gen rows (label 0 at `w_truth`, label 1 at `w_truth · pull`); push = ratio on
pass_gen rows, 1 elsewhere. Logit cap ±30. Score: the historical seven-bin `E_avail` recovery on half
B's push vs half A's tilted target, per region by each event's truth cell.

**Binned IBU** (`binned_unfolding.py`, `run_ibu.py`, k = 1..50). Truth bins = 7 endpoint E_avail bins ×
the 285 (pT, p‖) reporting cells (+1 off-grid cell; 1655 populated). The binned classifier's
Bayes-optimal ratio replaces the network, so `carry_misses` is exactly the engine's algorithm on bins
(proven in `test_classifier_loop_with_a_binned_oracle_is_the_binned_unfolding`); with zero smearing
it obeys `T − t_k = (1−a)^k (T − t_0)` — the historical reference model is this estimator's own
convergence law (tested against `reference_calibration.ceiling`). `efficiency_corrected` is textbook
D'Agostini (step-2 average over accepted events only). Reco binnings: `muon` (reco cells, 225
populated), `muon_eavail` (× 7 reco E_avail bins, 1475 populated), `eavail_only` (7), and `diag` —
**the event's own truth bin used as its reco bin: not an estimator, the reference model realized on
the actual populations and score.** Normalizations: `engine` (historical) and `rate_matched`
(pseudo-data total = 1e6 × f_A/f_B, what POT normalization would supply in a real measurement; known
here because the tilt is).

**Scalar OmniFold** (`scalar_omnifold.py`, `run_scalar_omnifold.py`, iterations 1..20, seeds 1-3):
the engine loop above with sklearn `HistGradientBoostingClassifier` (lr 0.1, ≤400 trees, 31 leaves,
min 200/leaf, early stopping on the weighted validation loss, patience 10) or an MLP (64-64 ReLU, Adam
1e-3, batch 1024, inputs sign·log1p then standardized, ≤30 epochs, early stopping on the weighted
validation log-loss, best epoch restored, warm start off). One fixed 80/20 train/validation split per
step reused at every iteration and prediction on all rows, as the engine does. **Differences from the
historical PET recipe, deliberate:** the learners are refit to convergence at every iteration (the
historical fits ran exactly 8 epochs at 4e-4 then 1e-5 and handed on the last epoch — A1); zero-weight
rows are left out of the fit (identical weighted loss).

**Truth-only learnability** (`run_truth_learnability.py`): **a learnability diagnostic of the step-2
input set, not a detector-level bound.** Half B's truth rows unweighted vs the same rows × the true
tilt; 50/50 train/held-out per seed; seven-bin recovery on the held-out half.

**Anchors** (`run_anchors.py`) and **reference decomposition** (`run_reference_decomposition.py`), see
§4.1-4.2.

## 4. Results

Every number below is from a committed result file under `results/` (sha256 table in
`results/summary.json`); job ids in §6. Per-bin signed residuals, histograms, injected / residual L1,
overshoot projections and weight summaries for every iteration are in the result files; only
summaries are tabulated. "k" is the unfolding iteration.

### 4.1 Anchors (`results/anchors.json`, job 58748397)

| push over half B | aggregate | low | moderate | good | projection |
|---|---|---|---|---|---|
| injected tilt function (half-A spec), ORACLE, not an estimator | 0.984 | 0.991 | 0.973 | 0.959 | 0.988 |
| same, half-B spec | 0.986 | 0.991 | 0.973 | 0.960 | 0.991 |
| identity (do nothing) | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| historical ours, seed 127 | 0.326 | 0.065 | 0.227 | 0.577 | 0.325 |
| historical theirs, seed 127 | 0.493 | 0.182 | 0.473 | 0.813 | 0.495 |

The oracle row is the closure's sampling ceiling (half A ≠ half B) for a push that is a function of
truth E_avail: 1.6 % of the injected L1 is irreducible finite-sample difference.

### 4.2 The reference model on the object that is scored (`results/reference_decomposition.json`, job 58748456)

Analytic, half B only (target = the same events × tilt), acceptance-only law per truth bin:

| k | historical construction (285 cells) | 1995 cell × E_avail bins | → 7-bin marginal, absolute | → 7-bin marginal, as scored |
|---|---|---|---|---|
| 1 | 0.511 | 0.430 | 0.430 | 0.385 |
| 2 | 0.650 | 0.564 | 0.564 | 0.521 |
| 3 | **0.696** | 0.619 | 0.619 | **0.578** |
| 5 | 0.726 | 0.663 | 0.663 | 0.626 |
| 10 | 0.743 | 0.698 | 0.698 | 0.664 |
| 20 | 0.756 | 0.724 | 0.724 | 0.693 |
| 50 | 0.781 | 0.761 | 0.761 | 0.737 |

The first column reproduces the historical 0.695 (on half B instead of the full population: 0.6962).
The drop to 0.619 is the displacement moving from where the (pT, p‖) spectrum is displaced to where
the E_avail spectrum is: the top E_avail bin (3-100 GeV) carries half of the injected L1, and 46 % of
that bin's displacement sits in low-acceptance cells, against 26 % of the cell-spectrum
displacement. The further
drop to 0.578 is the score's renormalization (the law moves only accepted mass, so the total drifts).
This is a property of the reference model, not of any estimator.

### 4.3 Binned IBU vs k (`results/ibu.json`, job 58748148; aggregate)

| variant (reco binning / step-2 rule / pseudo-data normalization) | k=1 | 2 | 3 | 4 | 5 | 10 | 20 | 30 | 50 | best (k) |
|---|---|---|---|---|---|---|---|---|---|---|
| reference `1-(1-a)^k` (historical) | 0.510 | 0.648 | **0.695** | 0.715 | 0.725 | 0.742 | 0.755 | 0.765 | 0.780 | — |
| muon / carry misses / engine | 0.099 | 0.142 | 0.164 | 0.176 | 0.184 | 0.200 | 0.208 | 0.210 | 0.211 | 0.211 (46) |
| muon / carry misses / rate-matched | 0.140 | 0.192 | 0.216 | 0.229 | 0.237 | 0.252 | 0.259 | 0.261 | 0.261 | 0.261 (40) |
| muon / efficiency-corrected / engine | 0.206 | 0.272 | 0.299 | 0.312 | 0.319 | 0.328 | 0.317 | 0.300 | 0.275 | 0.328 (10) |
| muon × reco E_avail / carry misses / engine | 0.264 | 0.396 | **0.472** | 0.522 | 0.557 | 0.648 | 0.682 | 0.674 | 0.659 | 0.683 (15) |
| muon × reco E_avail / carry misses / rate-matched | 0.294 | 0.431 | 0.508 | 0.557 | 0.591 | 0.680 | 0.727 | 0.719 | 0.704 | 0.728 (17) |
| muon × reco E_avail / efficiency-corrected / engine | 0.694 | 0.923 | 0.880 | 0.813 | 0.771 | 0.747 | 0.559 | 0.343 | 0.270 | 0.923 (2) |
| reco E_avail only / carry misses / engine | 0.258 | 0.400 | 0.480 | 0.526 | 0.554 | 0.595 | 0.600 | 0.595 | 0.587 | 0.600 (16) |
| *diag (reference model realized) / carry / engine* | 0.346 | 0.469 | 0.523 | 0.551 | 0.569 | 0.612 | 0.651 | 0.679 | 0.724 | 0.724 (50) |
| *diag / carry / rate-matched* | 0.371 | 0.501 | 0.556 | 0.585 | 0.603 | 0.644 | 0.680 | 0.705 | 0.746 | 0.746 (50) |
| *diag / efficiency-corrected / engine* | 0.708 | 0.708 | 0.708 | 0.708 | 0.708 | 0.708 | 0.708 | 0.708 | 0.708 | 0.708 |

By region (low / moderate / good), selected rows:

| variant | k=1 | k=3 | k=5 | k=10 | k=20 | k=50 |
|---|---|---|---|---|---|---|
| reference | .005/.403/.745 | .014/.777/.975 | .023/.911/.997 | .044/.988/1.00 | .082/1.00/1.00 | .174/1.00/1.00 |
| muon / carry / engine | .000/.030/.207 | −.001/.072/.348 | −.001/.102/.388 | −.002/.149/.410 | −.002/.193/.414 | −.003/.224/.410 |
| muon × reco E_avail / carry / engine | .004/.254/.500 | .011/.577/.866 | .016/.776/.949 | .026/.902/.880 | .040/.724/.791 | .071/.484/.668 |
| muon × reco E_avail / eff.-corr. / engine | .559/.635/.735 | .741/.917/.955 | .690/.803/.915 | .654/.654/.832 | −.424/.494/.748 | −.994/.269/.608 |
| diag / carry / engine | .011/.390/.634 | .032/.743/.896 | .053/.874/.928 | .101/.942/.934 | .188/.951/.934 | .395/.951/.934 |

Signed per-bin residual (unfolded − target, normalized), k = 3, aggregate, bins
[0,.1,.2,.4,.8,1.5,3,100] GeV; injected (target − prior) = [−.016, −.014, −.025, −.036, −.032, −.015,
+.138]:

| push | residual per bin |
|---|---|
| IBU muon / carry / engine | +.011 +.009 +.018 +.029 +.030 +.019 −.116 |
| IBU muon × reco E_avail / carry / engine | +.006 +.005 +.010 +.017 +.020 +.016 −.073 |
| IBU muon × reco E_avail / eff.-corr. / engine | −.000 −.001 −.002 −.004 +.009 −.010 +.008 |
| historical ours seed 127 / theirs seed 127 | +.007 +.006 +.012 +.022 +.027 +.019 −.093 / +.005 +.004 +.007 +.015 +.021 +.018 −.070 |

Every carry-misses estimator and both PET arms undershoot in the same shape: the top E_avail bin is
left short and the deficit is spread over the lower bins (overshoot projection ≈ recovery, never
> 1). Efficiency-corrected IBU overshoots from k = 3 (projection 1.05, rising to 1.17 by k = 10) and then amplifies
noise in the low-acceptance cells (that region goes negative by k = 20): it is not a stable
estimator here, only evidence that the reference is not a bound. Lost pseudo-data weight (reco bins
the prior does not populate) ≤ 5.0e-4 of the total in every variant and iteration.

### 4.4 Scalar OmniFold vs iteration (`results/omnifold_*.json`, array 58748399; mean ± sd over seeds 1-3 [min, max])

Aggregate:

| inputs / learner | it 1 | 2 | 3 | 4 | 5 | 8 | 10 | 15 | 20 |
|---|---|---|---|---|---|---|---|---|---|
| muon / HGB | .086±.002 | .122±.000 | .140±.003 | .151±.003 | .158±.005 | .168±.007 | .170±.008 | .174±.009 | .174±.010 |
| muon / MLP | .109±.003 | .159±.024 | .211±.045 | .213±.036 | .216±.019 | .223±.061 | .245±.044 | .248±.048 | .283±.022 |
| muon + reco E_avail / HGB | .251±.005 | .359±.007 | .412±.005 | .441±.004 | .461±.007 | .488±.007 | .498±.007 | .516±.011 | .524±.011 |
| muon + all reco summaries / HGB | .260±.006 | .368±.007 | .415±.009 | .443±.009 | .461±.007 | .488±.010 | .495±.011 | .509±.010 | .517±.013 |
| muon + all reco summaries / MLP | .316±.028 | .453±.035 | .486±.065 | .495±.048 | .551±.043 | .526±.040 | .578±.066 | .654±.047 | .633±.090 |

By region at iterations 3 / 10 / 20 (low; moderate; good, seed means):

| inputs / learner | it 3 | it 10 | it 20 |
|---|---|---|---|
| muon / HGB | −.009; .069; .287 | −.017; .116; .329 | −.024; .121; .329 |
| muon / MLP | .011; .132; .398 | −.017; .206; .447 | .019; .273; .446 |
| muon + reco E_avail / HGB | .041; .472; .733 | .094; .641; .815 | .136; .663; .812 |
| muon + all / HGB | .043; .478; .737 | .092; .636; .811 | .130; .657; .805 |
| muon + all / MLP | .063; .552; .849 | .111; .722; .928 | .301; .791; .862 |

Signed per-bin residual at iteration 3 (seed mean): muon/HGB +.012 +.010 +.018 +.030 +.031 +.018
−.119; muon+all/HGB +.008 +.006 +.011 +.019 +.022 +.015 −.081; muon+all/MLP +.007 +.004 +.009 +.016
+.019 +.016 −.071 — the same undershoot shape as IBU and PET.

Step diagnostics (in the result files): HGB early-stops at 10-48 trees per fit; MLP at 5-30 epochs.
The truth-space pulled distribution scores within 0.072 of the push at every iteration of every run
(e.g. muon+all/HGB it 3: pull 0.438, push 0.415), so step 2 loses little of what step 1 moves on these
inputs. The detector-level step-1 check in reco E_avail bins is 0.82-0.97 at iteration 1 for the
E_avail-aware sets and 0.33-0.36 for muon-only sets (which do not see reco E_avail). The MLP
seed spread (sd up to 0.09) is larger than the HGB's (≤ 0.013); three seeds on one event sample
measure estimator variability only, not event-sample variability.

### 4.5 Truth-only learnability (`results/truth_learnability.json`, job 58748398)

LEARNABILITY DIAGNOSTIC of the step-2 input set; NOT a detector-level bound and not an unfolding
recovery. Held-out half of half B, mean ± sd over 3 seeds:

| truth inputs / learner | aggregate | low | moderate | good |
|---|---|---|---|---|
| E_avail / HGB | 0.9990 ± 0.0001 | 0.999 | 0.999 | 0.999 |
| E_avail, pT, p‖, q3 / HGB | 0.9990 ± 0.0002 | 0.999 | 0.999 | 0.999 |
| E_avail / MLP (slog1p inputs; raw) | 0.917 ± 0.005; 0.936 ± 0.036 | 0.92 | 0.92 | 0.91 |
| E_avail, pT, p‖, q3 / MLP (slog1p; raw) | 0.911 ± 0.009; 0.935 ± 0.012 | 0.91 | 0.92 | 0.92 |
| pT, p‖ / HGB | 0.329 ± 0.001 | 0.048 | 0.217 | 0.438 |
| pT, p‖ / MLP (slog1p; raw) | 0.349 ± 0.017; 0.346 ± 0.018 | 0.053 | 0.213 | 0.462 |

In-sample values agree with held-out to ≤ 0.002. The tilt is a smooth monotone function of true E_avail alone
(clipped exponential in a standardized coordinate); the GBDT represents it almost exactly, the MLPs leave 6-9 % of the injected L1
(a learner limitation at this size and schedule, not an information limit).

## 5. What these numbers do and do not establish

Established (MEASURED, this sample): the historical populations, tilt, endpoint, reference and scores
are reproduced exactly from the historical code; the scalar references and binned IBU above, on those
populations; the reference model's own value on the scored marginal (0.578 at k = 3) and its
realization with the historical normalization (0.523); the 0.898 accepted-fraction ratio and its cost.

Not established: (i) any bound — the reference is a model, efficiency-corrected IBU exceeds it, and
the oracle push shows 0.984 is available to a truth-level function; (ii) why PET ours scores below the
E_avail-aware scalar references (representation, optimization — A1 measured the 3 × 8-epoch / 1e-5
recipe — or step-2 extraction of E_avail are all open); (iii) event-sample variance: everything here
is one fixed pair of halves and 3 estimator seeds; (iv) any statement about a new threshold. A
recalibrated reference is a prospective recommendation for the campaign, never a retroactive change to
the historical verdict.

Suggested (INFERRED, for the orchestrator): a like-for-like reference for this endpoint is the scalar
GBDT with reco E_avail, ≈ 0.41 at k = 3 and ≈ 0.52 at k = 20, or the reference model evaluated on the
scored marginal (0.578 at k = 3), not 0.695; recovery-vs-iteration for PET with a converged recipe is
the next discriminating measurement.

## 6. Provenance

| item | value |
|---|---|
| historical code | `68cf9d29f8ab1b0f5acd933d4baec1962b29e34d` (blob ids checked at run time) |
| closure npz | `/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz`, sha256 `fa6b3463…a29625` |
| identity sidecar | `/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz`, sha256 `01e07412…d5f95c` |
| halves from | `/pscratch/sd/j/josephrb/campaign-20260920/final/ours-seed127/weights/weights_ours_final_127.npz` (read only) |
| cached populations | `/pscratch/sd/j/josephrb/pet-improvement-20260922/phaseB1/prep/populations.npz`, sha256 `b2b55791…cb96da1` |
| jobs (commit) | prep 58741903 (`36733301`); IBU 58748148 (`4ca3e60d`); anchors 58748397, learnability 58748398, OmniFold 58748399_[0-14] (`c6145ecb`); decomposition 58748456 (`38928e3e`) |
| environment | `root_6_28` conda python 3.11.14, numpy 1.26.4, sklearn 1.8.0; tests also under NERSC `python` module (sklearn 1.9.0) |
| guard | every job through `nd-unfolding/mnv_guarded_run.py` from a clean clone at the job's commit; inventories `guard-<job>.json` beside each output |
| compute | 52.7 CPU core-hours (allocated cores × elapsed), `resources-B1.tsv`; no GPU |

