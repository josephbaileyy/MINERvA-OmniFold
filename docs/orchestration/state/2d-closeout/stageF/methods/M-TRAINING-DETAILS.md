# OmniFold training details, read from the code (record)

**Read by** a Claude agent for the director, 2026-10-20, at origin/main `51da2a62`, read-only. The agent could not write this file; the director saved its report verbatim below.

**CITABLE FOR:** how each estimator configuration trains (model, seeds, in-sample fitting, raw class weights, the miss regressor, the absence of renormalization, the refinement classifier) and where an effective sample size is or is not computed.
**NOT CITABLE FOR:** which launcher and flags produced each published product. That rests on records (`sec_method.tex:79-86`, `sec_5d.tex:153`).

---

I traced all five configurations through the code. Every hyperparameter, weighting rule and clip below is stated in the code. The exceptions are LightGBM's own library defaults and which launcher actually produced each published central value; those are noted where they matter.

Code is at origin/main `51da2a62` (worktree wt-m4). Two corrections to the brief:
- `stageF/methods-rewrite-20261019` is not on origin. I read Table IV from the local ref (`2976acb9`), `paper_body.tex:569-600`.
- Two code families are involved, not one. (a) runs through `unbinned_unfolding/python/omnifold.py` (`ohf.omnifold`). (c), (d) and (e) run through `nd-unfolding/omnifold_nn_core.py` (`omnifold_loop`). They differ on seeds.

## 1. Model, capacity and seeds

- **(a) central value.**
  - 2D: the driver calls `ohf.omnifold` (`2d-unfolding/unfold_2d_omnifold_unbinned.py:2091-2105`).
  - 3D–5D: same call (`nd-unfolding/unfold_nd_omnifold_unbinned.py:1049-1063`).
  - The `lgbm` branch builds `LGBMClassifier` for steps 1 and 2 and `LGBMRegressor` for misses, with `n_estimators=100, num_leaves=8, learning_rate=0.1` (`omnifold.py:203-220`).
  - Seeds: `--seed S` gives step-1 classifier `random_state=S`, step-2 `S+1`, regressor `S+2` (`unfold_2d…:2080-2083`; `unfold_nd…:1042-1045`).
  - If no seed is passed, no `random_state` is set (`unfold_nd…:637`, default None).
  - Defaults differ: the 2D `--estimator` defaults to `exact` (`unfold_2d…:1476-1478`), the ND one to `lgbm` (`unfold_nd…:635`).
  - The 4D and 5D launchers pass `--estimator lgbm --seed 42` (`sbatch_unfold_4d_universes_full.sh:47`; `sbatch_unfold_5d_detector.sh:50,65`).
- **(c) deterministic variant.**
  - Calls `omnifold_loop(kind="lgbm")` (`s5c_unfold.py:124-128`), which uses the same 100/8/0.1 settings (`omnifold_nn_core.py:145`).
  - One `random_state=seed` is shared by all three estimators (`omnifold_nn_core.py:146-148`); the seed is the required `--estimator-seed` (`s5c_unfold.py:153`).
  - Added knobs: `bin_construct_sample_cnt=2^31-1, deterministic=True, force_row_wise=True, num_threads=<allocation>` (`s5c_unfold.py:51-60`).
  - The run refuses to write output unless every estimator carries these knobs (`s5c_unfold.py:129-134`).
- **(d)** is the same unfolding loop as (c) (`s5n_pseudo.py:330`), plus the refinement in section 6.
- **(e)** is (d) with the refinement classifier set to `n_estimators=400, num_leaves=31` (`s5e_candidate.py:33,41-42`).
- **Early stopping:** none for any LightGBM fit. Every `fit` passes only `sample_weight`, with no evaluation set (`omnifold.py:255,270`; `omnifold_nn_core.py:245`; `unfold_2d…:446`).
- **NN cross-check:**
  - Keras MLP with layers 64/128/64, gelu, logit output, weighted sigmoid cross-entropy (`omnifold_nn_core.py:39-49,77-90`).
  - Adam at lr 1e-3, 50 epochs, batch 10000 (`omnifold_nn_core.py:59-61`).
  - Rows are shuffled with a fixed seed of 0, then a 20% `validation_split` drives early stopping (patience 8, best weights restored) (`omnifold_nn_core.py:106-116`). This is the only held-out set anywhere in these loops.

## 2. Training versus evaluation

All five configurations train and evaluate in-sample.
- Step 1 is fit on the reconstructed MC plus data, then evaluated on those same reconstructed MC rows (`omnifold.py:251-257`; `omnifold_nn_core.py:250-257`).
- Step 2 is fit on MCgen⊕MCgen and evaluated on MCgen (`omnifold.py:266-272`; `omnifold_nn_core.py:263-266`).
- `omnifold_loop` has an optional `train_frac`: it fits on a random subset and still evaluates on all rows (`omnifold_nn_core.py:196-204,229-246`). Only `seedscan_split.py:70` uses it. `s5c_unfold` does not pass it, so the default of 1.0 applies (no split).
- There is no cross-fitting.
- In the pseudo-experiments for (c)–(e), the unfolding MC (half A) is kept separate from the pseudo-data source (half B) by a keyed hash (`s5n_pseudo.py:16-20`; `s5c_pseudo.py:119-123`). That separates response from pseudo-data; it is not a classifier holdout.

## 3. Class normalization and the weight conversion

- **Classes are not balanced for LightGBM.** `balance = (kind == "nn")` (`omnifold_nn_core.py:225`). In `omnifold.py` there is no balancing at all, for any backend, including its own `nn` branch (`omnifold.py:224-238,251-270`).
- **Step 1 uses raw weights.**
  - Class 0 is reconstructed MC with `w_push·w_reco`; class 1 is data with `measured_weights` (`omnifold.py:253-256`; `omnifold_nn_core.py:251-254`).
  - Data weights are the purity weights `max(0, D_b − B_b)/D_b` (`unfold_nd…:582-600`; `s5c_pseudo.py:99-112`, times the pseudo-data counts).
  - MC weights are POT-scaled (`unfold_nd…:1053-1060`).
- **Step 2 uses raw weights.**
  - Class 0 is MCgen with `w_truth` (the prior, without `w_push`); class 1 is MCgen with `w_pull·w_truth` (`omnifold.py:266-268`; `omnifold_nn_core.py:263-265`).
  - The new `w_push` is therefore the absolute ratio to the prior (`omnifold.py:272`).
- **Conversion:** w = p/(1−p), with p clipped to [1e-6, 1−1e-6] and NaNs zeroed (`omnifold.py:77-84`; `omnifold_nn_core.py:152-155`). The resulting weights lie in [1e-6, ~1e6]; there is no other cap.
- **NN path in `omnifold_loop` only:** each class is rescaled to N/2 for training, and the ratio W1/W0 is multiplied back afterwards (`omnifold_nn_core.py:158-190,230-246`).

## 4. Misses and fakes

- **Fakes:** MC events failing truth are removed before the loop (`omnifold.py:105-107`; `omnifold_nn_core.py:210-211`). They enter only through the background: in 2D they are part of `hBkgReco2D` and of the injected template (`unfold_2d…:1846-1863`). I did not check whether the ND background dump contains fakes.
- **Misses (step 1):**
  - The weight comes from a "miss regressor" of the same family: LGBMRegressor with the same settings, using LightGBM's default L2 objective (library default).
  - It is fit on truth features of the reconstructed events, with target equal to their step-1 weights.
  - The fit has no `sample_weight` (`omnifold.py:259-262`; `omnifold_nn_core.py:258-260`).
  - It predicts weights for the non-reconstructed events. Those are out-of-sample for the regressor, and the predictions are not clipped.
- **Misses (step 2):** they appear in both MCgen classes like any other truth event (`omnifold.py:266-268`).

## 5. Per-iteration normalization

None. Neither loop rescales `w_pull` or `w_push` to the MC total (`omnifold.py:251-272`; `omnifold_nn_core.py:249-266`). The normalization comes from the raw class weights. The unfolded yield is `histogramdd(MCgen, w_push·w_truth)` (`s5c_unfold.py:138`).

## 6. Background refinement (`refine_stay_positive`)

- Lives at `unfold_2d_omnifold_unbinned.py:412-462`; (d) and (e) call it via `s5n_pseudo.py:264-282`.
- **Input:** a signed sample of observed events at +count and the background template at −weight, with zero-weight rows dropped (`s5n_pseudo.py:222-228`).
- **Classifier:**
  - LGBMClassifier, 100 trees, 8 leaves, lr 0.1 (`unfold_2d…:402-407`), with label `w>0` and `sample_weight=|w|` (`unfold_2d…:443-446`).
  - For (d)/(e) it also gets `random_state=seed+3` and the deterministic knobs (`s5n_pseudo.py:61,234-236`); (e) changes capacity to 400/31.
  - Parameters are verified against the classifier actually built (`s5n_pseudo.py:276-281`).
- **In-sample:** it is fit and evaluated on the same signed rows.
- **Output weights:**
  - g is clipped to [1e-6, 1−1e-6], and the new weight is w̃ = |w|·max(0, 2g−1) for every row, template rows included (`unfold_2d…:447-450`).
  - The clipped fraction is returned. The refined total is recorded but not rescaled to the signed total (`s5n_pseudo.py:295-299`).
- **Feeding step 1:** the refined rows become step 1's "measured" sample (`s5n_pseudo.py:324-326`). The refinement runs once per product, before the OmniFold loop, and is refit for each bootstrap replica (`s5n_pseudo.py:21-24`).

## 7. Effective sample size

- No ESS of the OmniFold push or pull weights is computed in either production loop or in any driver above.
- The Kish ESS (Σw)²/Σw² is computed in four other places:
  - Refinement evidence for (d)/(e): `n_eff_signed_abs` and `n_eff_refined` (`s5n_pseudo.py:301-302`), summarized in `s5n_analyze_dev.py:94-95`.
  - The goodness-of-fit test (`unbinned_gof.py:96`).
  - The Kish ratio of the null-experiment signal source (`s5p_nullexp.py:330`).
  - The MC truth n_eff (`s5p_stage1_inspect.py:144`).

## Proposed paragraph (~150 words)

> Each OmniFold step uses LightGBM gradient-boosted trees (100 trees, 8 leaves, learning rate 0.1, no early stopping), and the miss regressor uses the same settings. Every classifier is trained on the full sample whose weights it then sets, with no held-out or cross-fitted split. The two classes keep their physical weights: in step 1, purity-weighted (or refined) data against reconstructed simulation carrying the current truth weights; in step 2, the prior truth sample against the same sample carrying the pulled-back weights. No class balancing or per-iteration renormalization is applied, so the learned ratio p/(1−p), with p restricted to [10⁻⁶, 1−10⁻⁶], carries the normalization. Truth events without a reconstructed partner receive the prediction of an unweighted regressor of the step-1 weight on truth observables. In the refined configurations, a classifier separating positive from negative weights, trained with |w|, gives every event the weight |w|·max(0, 2g−1). The deterministic variants pin seeds, the bin-construction sample and threading. No effective sample size of the unfolded ensemble is computed.

## Not determinable from code

- Which launcher, seed and flags produced each published central value. The code allows the 2D driver to default to `exact` and the ND drivers to default to no seed, so the "seed 42" and "LightGBM" claims rest on records (note `sec_method.tex:79-86`).
- Which seeds were used for the (c)–(e) coverage and bias runs (`--estimator-seed` is a CLI argument). The note records seed 42 for candidate R (`sec_5d.tex:153`).
- Whether the NN cross-check used the class-balanced `omnifold_loop` or the unbalanced `omnifold.py` `nn` branch.
- Whether the ND background dump includes signal fakes.
- LightGBM's internal defaults (no bagging or feature subsampling, `min_child_samples=20`, L2 regression objective) come from the library, not from repository code. `s5c_unfold.py:13-14` states the no-bagging point.

The paper's current caveat (`paper_body.tex:491-503`) says no record gives the training/evaluation split or the class normalization. The code answers both, as sections 2 and 3 show. Only the ESS gap stands.