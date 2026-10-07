# Claim-to-evidence index

Every factual and numeric claim in `slides/recommended_pet_configuration.pdf` and in
`CONFIGURATION_COMPARISON-20260918.md`, with its source. Claims are grouped by what
kind of evidence backs them, because that distinction is the point: a measured number,
a code reading and a judgement are three different things and the deck must not blur
them.

**Revision 2, 2026-09-18.** §N lists what revision 1 of the proposal got wrong.
**Revised 2026-09-18 for the matched-comparison goal.** The deck is now an **interim
inventory**; the selection is specified in `MATCHED_COMPARISON_PROPOSAL-20260918.md` and
has not been executed. §L records what was corrected in this revision.

Pins: ours `44142e8c` (branch `pet-direct-token-comparison`); Gregor's
`fc9a099d3c9c060f03cef293c294f9de4eb019cd`. Gregor line numbers are relative to his
checkout root; ours are relative to the repository root.

---

## Z. Corrections and additions, 2026-09-19 (the port milestone)

These supersede rows elsewhere in this index where they conflict.

| id | claim | evidence | kind |
|---|---|---|---|
| Z1 | **Gregor's paper models run with `use_int=False, local_int=False`** — NOT `PET2`'s class defaults of `True`/`True` | `plot_configs/V1Paper.json`; `src/jobs/submit_train_jobs.py:155-169`; `src/scripts/train.py:883-894` (`store_true`, `default=False`) | code reading |
| Z2 | his paper backbone is **2,758,702** parameters, **58.6×** our step-1 PET | `receipts/model-capacity.json`, rebuilt at the paper flags. **Supersedes 2,762,550 / 58.7×**, which measured the non-paper `OLS_int` variant | measured |
| Z3 | the Keras port reproduces `PET2` to **6.7e-16** in float64 and within the measured float32 budget against unmodified upstream | `receipts/PORT_CHECKS-20260919.json`, P-2 | measured |
| Z4 | `r`, the per-example training cost ratio, is **2.7** at 12 tokens and **4.2** at 33 at matched batch, and **3.55** at his native batch under the repair | two independent runs, 58551348 and 58551477, agreeing to 3 % and 1 %. **Supersedes 2.82 / 4.30**, and two significant figures is all the runs support | measured |
| Z5 | inference adds **36 M** forward presentations per evaluation against 96 M trained, at a ratio of 1.88 (12 tokens) and 2.44 (33) | same receipt; budget model in `calibrate_cost.py` | measured + model |
| Z6 | the complete pretrained comparison costs **≈170 GPU-h** at 33 tokens and his native batch under the repair (≈189 at the matched batch) | `COST_UPDATE-20260919.md`. **Supersedes ≈207**, which was fit-only, priced the wrong model, and assumed his batch had to shrink | projection from measurement |
| Z7 | his batch 2048 at 33 tokens needs a **backend repair (math SDPA), not a batch-size change**; largest batch under the default backend is 1024, and the repair runs at **200.85 µs/example**, 14 % cheaper than the matched-batch fallback | `receipts/COST_RECALIBRATION2-20260919.json`, `native_batch_diagnosis` | measured |
| Z8 | `tf.nn.gelu(approximate=False)` differs from torch by **4.1e-9** in float64 | `test_port.py::Activation`; the written-out erf form agrees to 1.1e-16 | measured |
| Z9 | `tf.keras.optimizers.AdamW` differs from `torch.optim.AdamW` by **68 % of the first update** on zero-initialised biases | `receipts/PORT_CHECKS-20260919.json`, P-4 `rejected_alternative`; derivation in `torch_adamw.py` | measured |
| Z10 | PyTorch's `scaled_dot_product_attention` returns an **O(1) wrong answer** for a float32 mask with float64 q/k/v; float32, bf16 and fp16 are unaffected | `receipts/PORT_CHECKS-20260919.json`, `torch_sdpa_mask_dtype_probe` | measured |
| Z11 | the pretrained checkpoint gates the pretrained arm's **tuning and variance pilot**, not only its final runs | `DECISION_PACKET-20260919.md` §1; argument, not measurement | judgement |
| Z12 | `PET2.no_weight_decay()` exists and `train.py` never calls it, so his norms and class tokens **are** weight-decayed | `src/scripts/train.py:2345`, one param group | code reading |

## Z3. The complete-comparison attempt, 2026-09-20 (supersedes §Z and §Z2 where they conflict)

| id | claim | evidence | kind |
|---|---|---|---|
| Z3-1 | **the pretrained checkpoints are reachable**, and "verified unavailable" was a probe from the wrong network: `/global/cfs/cdirs/m4567` is `drwxr-s--x`, traversable but not listable, and the portal returns HTTP/2 200 from Perlmutter | `CHECKPOINT_OBTAINED-20260919.md`; `best_model_pretrain_s.pt` sha256 `7e8331b0…12b1bc`, 34,605,223 B | measured |
| Z3-2 | the checkpoint holds **9 top-level keys**, including an `ema_body` the reference loader does not use | `receipts/CHECKPOINT_INVENTORY_S-20260919.json` | measured |
| Z3-3 | the reference loading policy transfers **139/148 body tensors (98.47 %)** and **26/28 classifier tensors (99.96 %)**, and **every reinitialized tensor is reinitialized by his own pipeline at his own defaults** | `receipts/CHECKPOINT_TRANSFER_REAL-20260919.json`, run with his `_filter_partial_state` against the real file | measured |
| Z3-4 | the pretrained state loads into the Keras port **176/176 tensors, worst difference 0.0** | `receipts/PRETRAINED_STATE_MANIFEST-20260919.json`; `pretrained_init.py` refuses partial coverage in both directions | measured |
| Z3-5 | the **fullevent** data leg is **4,116,128** rows, superseding the 5-D product's 4,091,707; budget factor **1.2645** | `receipts/FULLEVENT_INVENTORY-20260919.json`, sha256 `d466a0c1…29d25e`; loader consumes it in full (`:486,494`) | measured |
| Z3-6 | **R-1 verified independently by this lane**: 12/12, data bare key NOT unique with 220,439 rows needing `occurrence`, 28,579,364 native misses all carrying identity | my own run of `verify_event_identity_sidecar.py`; sidecar sha256 `01e07412…ddd5f95c` | measured |
| Z3-7 | the sidecar's `order_hash_module` sha256 **equals this HEAD's `fullevent_fps_dataloader.py`**, so order provenance binds to the code we run | `e1402370cdb8bd63` both sides | measured |
| Z3-8 | **TF32 was enabled for every GPU measurement this lane took before 2026-09-20**; the frozen policy forbids it and no driver enforced it | `keras_backend.observed_precision_policy()` reports `tf32_enabled: True` by default | measured |
| Z3-9 | at **enforced** FP32 the intended cell costs **410.6 µs/example** against 388.0 with TF32 (+5.8 %), peak **21.7 GiB**, on a **40 GB** A100 | `receipts/PORT_PROFILE_FP32-20260920.json`, job 58586142 | measured |
| Z3-10 | the XLA path differs from eager on **100 % of rows** with TF's TF32 flag off, and the same XLA program differs from ITSELF between batch 2048 and 256 by a median 2.27e-3 per row | `receipts/PRODUCTION_VALIDATION_step1_reco-20260920.json`, row profile | measured, **cause under test** |
| Z3-11 | k-NN ties on the real cloud: **20,695 coordinate tie pairs**, and **28,793 ambiguous k-th boundaries at K=3** / 20,778 at K=10 over 280 M centres | `receipts/KNN_TIE_CENSUS-20260920.json`, full population | measured |
| Z3-12 | **the complete arm cannot be built**: zero of the 46 R4 branches exist in any tree of the 113 GB source, and the cap is 12 | ROOT read of `runEventLoopOmniFold_G2_FPS_MEFHC.root`; `HANDOFF-20260920-complete-comparison.md` §1 | measured |
| Z3-13 | **no comparative result exists.** Neither arm has been trained on the endpoint and no recovery has been measured | — | scope statement |

## Z2. The optimisation pass, 2026-09-19 (later than §Z, and superseding it where they conflict)

| id | claim | evidence | kind |
|---|---|---|---|
| Z2-1 | the ported step at 12 tokens / batch 512 is **forward 134.2, backward 795.3, optimizer apply 5.4 µs/example**; the backward is **85 %** of the step and **6.9× the forward** | `receipts/PORT_PROFILE-20260919.json`, job 58564110, decomposed with a folding control | measured |
| Z2-2 | the cause is `tf.einsum("...i,oi->...o")`'s **gradient**, which materialises the per-example outer product: **58 of 60 OOM tracebacks** are in `einsum_op_impl.h`, at shapes up to `[256,128,16896,10]` = 22.2 GB for a 32,768-number weight | job 58564110's log; shape census by `grep` | measured |
| Z2-3 | **the optimizer is not the bottleneck**: applying all 176 variables costs **6.06 ms** against **4.71 ms** for stock Keras Adam, 1.29× | direct probe, CPU | measured |
| Z2-4 | **WITHDRAWN: "96 % of the step is `apply_gradients`."** It was an artifact of returning `loss + 0.0 * gradient`, which Grappler folds, pruning the whole backward subgraph; the missing time landed in the apply by subtraction | the same probe, plus `folded_backward_control` measuring 1.00 on GPU | withdrawn |
| Z2-5 | the two **bitwise** local-block rewrites (broadcast centre, broadcast key mask) change **neither time nor memory**: 935.5 vs 934.6 µs/example, 16.9 GiB both | job 58564110 | measured, negative |
| Z2-6 | those two rewrites are **bitwise identical** in forward and gradients, in float32 and float64, including on an event whose whole neighbourhood is padding | `test_port.OptimisationEquivalence`, `assert_array_equal` | measured |
| Z2-7 | the **projection rewrite is not bitwise** — 1e-15 relative in float64, 6.5e-7 in float32 — and P-1…P-6 still hold: 216 fields identical, 181 moved, **no verdict changed**, cross-engine agreement improved, P-3's margin over the mutant port 508,145× → **571,199×** | `receipts/PORT_CHECKS_FLAT_PROJECTION-20260919.json`, diffed by `compare_port_checks.py` | measured |
| Z2-8 | **gradient accumulation costs 1.3 %** and makes the virtual batch 2048 fit where the native batch OOMs: 947.8 vs 935.5 µs/example, 17.0 vs 16.9 GiB | job 58564110, `accum4` cell | measured |
| Z2-9 | accumulation reproduces the single-batch update to **1e-14** in float64, takes **exactly one** optimizer step per virtual batch, and clips on the **same global norm** | `test_recipe.Accumulation` | measured |
| Z2-10 | the measured leg is **4,091,707** rows on the 5-D point-cloud product — **2.05× n_mc**, a factor **1.2615** on the example budget and on every absolute GPU-hour, and on **no** ratio | `of_inputs_pc_fullcloud_bkgsub_5d.provenance.json`, three independent fields; corroborated within 0.7 % by the event-identity export | measured, **on a neighbouring product and not on this schema** |
| Z2-11 | in `PORT_PROFILE-20260919.json` the variant named `optimised` means broadcast **plus** projection; in the earlier cancelled job it meant broadcast-only | every cell records its `commit` and its `paths`; `run_note` records what a missing cell means for that run | provenance |
| Z2-12 | the projection rewrite is worth **2.36×** on the full step (935.5 → 396.7 µs/example), **1.78×** forward, **2.52×** backward, and **−25 %** peak memory | `receipts/PORT_PROFILE-20260919.json`, job 58565265, 12 tokens / batch 512 | measured |
| Z2-13 | **XLA is the larger lever**: 4.3× on the untouched port (935.5 → 218.9) and 2.53× on top of the projection rewrite (396.7 → **156.6**), with a **6×** memory collapse to 2.1 GiB | `receipts/PORT_PROFILE_80G-20260919.json`, job 58566629 | measured |
| Z2-14 | **the intended configuration runs**: 33 tokens at his native batch 2048 trains under XLA at **377.7 µs/example in 21.7 GiB**; eager cannot do it on an 80 GB card at all | same receipt | measured |
| Z2-15 | the complete pretrained comparison costs **≈434 GPU-h** at the intended configuration, **≈547** under the larger data leg, against a 600 ceiling with ≈18 consumed | `project_campaign.py` over the same receipt | projection from measurement |
| Z2-16 | the **bitwise-exact** port (no projection rewrite) plus XLA costs **40 % more** than the rewritten one — 218.9 against 156.6 µs/example | same receipt, `broadcast_xla` | measured |
| Z2-17 | **P-1…P-6 hold under XLA**: no verdict changed, zero tensors over their own round-off floor, mutant margin 4.18e5. Scope: XLA's transformations on the **CPU** backend, NOT XLA-GPU's kernels | `receipts/PORT_CHECKS_XLA-20260919.json`; the traced-function refactor it needed is controlled by `receipts/PORT_CHECKS_TRACED_CONTROL-20260919.json` at 397 identical / 0 changed | measured |
| Z2-18 | **WITHDRAWN: the XLA cells of job 58565265.** `_time` did not force a device sync inside the timed region, so a fused XLA kernel was timed by its launch: 2.4 µs/example is **41.1 TFLOPS on a 19.5 TFLOPS float32 peak**. The unfused cells of that job stand, agreeing with independently synced job 58552755 to 0.6 % | the receipt's `run_note`; the repair is in `_time` | withdrawn |

## A. Measured on real MINERvA tuples

| # | claim | source | scope limit |
|---|---|---|---|
| A1 | 12-token cap binds in **64.13 %** (data) / **84.44 %** (MC) of events | `direct_token_comparison/local_validation/20260918-source/source-multiplicity.json`, `sources[*].generic_clusters_nonmuon.fraction_above_cap`; job 58470099 | unselected, unweighted; one file per role |
| A2 | discarded clusters carry a median **20.78 %** / **44.90 %** of non-muon cluster energy (p90 71.5 % / 75.4 %) | same receipt, `tail_energy_share_beyond_cap` | bounds how much the cap *could* matter; does **not** establish predictive importance (the receipt says so in its own `qualification` field) |
| A3 | mean non-muon clusters **74.57** (data) / **102.64** (MC); median 25 / 60; max 1651 / 2349 | same receipt, `generic_clusters_nonmuon` | as A1 |
| A4 | blobs mean **11.15 / 12.45**, median 4 / 6, max 158 / 153; prongs mean 1.47 / 1.75, max 7 / 12; photons mean 0.35 / 0.35, max 2 | same receipt | source-capped at 2 photons |
| A5 | entries read: **17,930** data (playlist 1B, run 00010068) and **186,439** MC (playlist 1A, run 00110000), read in full | same receipt, `entries_read` / `entries_available` | two files, not the playlists |
| A6 | the re-derived energy ranking agrees with the production builder (9 data / 94 MC cross-checks passed) | same receipt, `production_crosschecks_passed`; `characterize_source_multiplicity.py:256-261` | cross-check every 2000 entries |

## B. Derived from A (no new source read)

| # | claim | source |
|---|---|---|
| B1 | a 33-token typed cap binds in **9.2–16.9 %** (data) / **11.4–27.2 %** (MC) | `receipts/typed-object-budget.json`; derivation and its limits in `measure_typed_object_budget.py`; 8 tests in `test_typed_object_budget.py` |
| B2 | mean typed-object count **13.98** / **15.55**, against 74.57 / 102.64 clusters — **5.3×** / **6.6×** fewer tokens | same receipt, `typed_objects.mean_objects` vs `cluster_cloud.mean_objects` |
| B3 | **32.2 % / 37.4 %** of events have ≥12 blobs; **9.2 % / 11.4 %** have ≥33 | derived from the `blobs` histogram in the A1 receipt |
| B4 | the typed figure is an **interval, not a point** | the A1 receipt stores marginal per-family histograms only; the joint is not recoverable. Enforced by `Bracket` tests |
| B5 | our campaign multiplier is **~130 trains** | summed from F16: ~100 `C_stat` replicas + ~12 `C_ML` + 6–8 vertical/flux + ~10 lateral endpoint retrains + nominal + matched floor. An order-of-magnitude figure from the contract's own cost estimate, not a schedule |

## C. Measured on GPU (this campaign)

| # | claim | source | scope limit |
|---|---|---|---|
| C1 | individual routing costs **1.244×** training / **1.257×** inference at 14 typed objects; **1.879×** / **1.318×** at 87 | `direct_token_comparison/local_validation/20260918-a3-cost/cost-half.json`, `cost_summary` | one A100, TF32 off, determinism on, float32; 3 interleaved replicates; families sampled independently, so the joint multiplicity of real events is not reproduced |
| C2 | aggregate overflow reads **1.007×** / **0.978×** at the operating point and **0.994×** / **0.998×** in the tail | same receipt | see C3 |
| C3 | the resolution of that measurement is about **±3.3 %** | derived: arm B is computationally identical to arm A in the pooled configuration and reads `train_ratio_to_A = 0.9669`. The figure script recomputes the floor from the receipt rather than hardcoding it (`make_figures.py`) | an inferred resolution estimate, **not** a quoted uncertainty |
| C4 | inference throughput ratio **1.283×** (median of 3 seeds); all five acceptance checks pass; worst CV 2.03 % | `local_validation/20260917-inference/inference-benchmark.json` | four-object fixture, 50,000 held-out rows, batch 1024, 3 warm-up + 10 timed passes |
| C5 | 10 of 13 widths released, no hard stop at any width, 0–160 objects in a family | `local_validation/20260918-tailval/validation-final.json`, `released_widths`, `hard_stop_checks`, `complete: false` | **incomplete validation** |
| C6 | the three unreleased widths — (0,64,2) and (2,160,12) arm C, (2,12,4) arms B and C — failed **V5 only** | same receipt, per-record `checks` | |
| C7 | cross-device agreement fails equally for pooled and individual (gradients 4.96e-5 vs 4.38e-5; updated weights 1.78e-3 vs 1.68e-3 at 48 blobs); the **pooled** arm fails first as multiplicity grows | same receipt, `tier_by_width` and per-record `classify_cross_device` output | |
| C8 | V5 step sweep: rel. error 1.69e-1 (h=3e-2), 1.84e-2 (h=1e-2, frozen), 1.67e-3 (3e-3), **3.14e-4 (1e-3)**, 1.30e-3 (3e-4); |grad| = 0.0215 | local diagnostic reported in `direct_token_comparison/RECOMMENDATION-20260918.md` §3 and `TAIL_VALIDATION_PLAN-20260918.md` §8 | local CPU sweep at the worst failing coordinate |
| C9 | frozen criteria sha256 `abccd88b4665f2093bd671691298c1a00e31511afdee4a239312f856012fae27` | `direct_token_comparison/VALIDATION_CRITERIA-20260918.json` | frozen **before** execution; not relaxed after failures |

## D. Measured on the synthetic fixture

| # | claim | what the statistic actually measures | source |
|---|---|---|---|
| D1 | paired improvement median **+9.71 %**, mean **+0.82 %** | the paired injected-improvement percentage, individual over pooled, per training seed, on the four-object synthetic fixture | `local_validation/20260917-matrix/matrix-summary.json`, `paired_improvement_percent` = [17.11, 18.85, 8.72, 10.69, 0.93, 26.75, −47.57, −28.94] |
| D2 | 95 % interval **[−20.73 %, +22.37 %]** | a 95 % interval on the **mean across eight training seeds** of D1. Not an interval on production closure, real data, or any physics quantity | same receipt, `paired_mean_95_percent_interval` |
| D3 | paired **p = 0.50**; 6 of 8 seeds favourable | a paired test **across training seeds**. It measures seed-to-seed scatter. **Test-sample uncertainty was not separately estimated** | same receipt |
| D4 | seed-to-seed sd **25.8 points** | scatter of D1 across seeds. Used elsewhere as a **planning assumption** for a different endpoint — different fixture, two arms, different denominator. **Not measured power for the endpoint in `ENDPOINT_SPECIFICATION-20260918.md`** | same receipt |
| D5 | decision **`NO_PASS`**, 142 of 146 checks holding; failures `material_paired_gain`, `favorable_seeds` (these *were* the inconclusive result) and, separately, `shuffle-71/projection0`, `shuffle-71/projection1` | `NO_PASS` may be inconclusive **or** a failed safeguard; `present_matrix_results.py:75-103` refuses to merge the two | same receipt, `checks`, `decision` |
| D6 | `shuffle-71` missed the projection checks marginally: 0.0119 against a 0.01 limit, absolute errors well inside 0.05 | `local_validation/20260917-matrix/matrix-analysis.json` | one of eight null-control jobs |
| D7 | training-cost ratio on the fixture, median **1.118×** over 24 paired jobs | same summary, `compute.paired_direct_over_pooled_ratio` | four-object fixture, not real multiplicity |

**Transfer caveat attached to all of D.** In the fixture every generic slot is noise and
all signal is typed; in production the cluster cloud carries most of the information.
**Neither the direction nor the magnitude of a synthetic effect transfers
automatically.** Two earlier claims of mine — that direction transfers, and that the
fixture gives an upper bound — are **withdrawn**.

## E. Measured by instantiating both models

| # | claim | source |
|---|---|---|
| E1 | our production PET has **47,041** trainable parameters (step 1) and **46,913** (step 2); **93,954** per OmniFold iteration | `receipts/model-capacity.json`, produced by `measure_model_capacity.py` building the actual `omnifold.net.PET` at the driver's configuration |
| E2 | Gregor's `PointGlobalMixedViT` backbone has **890,130** parameters at his Transformer1 settings | same receipt, building `src.models.vit.PointGlobalMixedViT` |
| E3 | ratio **18.9×** | same receipt. **Capacity is not accuracy**: the two models solve different problems, so the ratio measures size only |

## F. Read from our code (production configuration)

| # | claim | citation |
|---|---|---|
| F1 | cloud = non-muon calorimeter clusters, 5 columns (E, pos, z, view, time) | `nd-unfolding/pet/FULL_EVENT_FEATURE_CONTRACT.md` reco-cloud table; `dump_pointcloud_inputs.py:46,67-68` |
| F2 | the muon is removed from the cloud and carried as a 13-feature event block with FiLM conditioning | contract §event_reco; `fullevent_fps_dataloader.py:266` (`DEFAULT_EVT_FEATURES`); `docs/analysis-note/sec_pet.tex:50-54` at `66d35706` |
| F3 | the cap is applied **at dump time**: stable energy-descending sort, top `num_part`, zero-pad | `dump_pointcloud_inputs.py:90-112`; the product is `G2_FPS_MEFHC_P12.npz` |
| F4 | clouds are energy-ranked and truncated or zero-padded to 12 tokens | `docs/analysis-note/sec_pet.tex:56-57` at `66d35706`; `typed_descriptor_source_smoke.py:34,741-768` |
| F5 | overflow leaves no trace — no count, no summed energy, no flag | `dump_pointcloud_inputs.py:90-105` (nothing is written for the discarded rows) |
| F6 | fixed physical divisors; event features z-normalized with frozen reco-MC `pass_reco` statistics; `!pass_reco` rows zeroed post-normalization | contract §preprocessing, §data-semantics note |
| F7 | azimuth carried as (cos φ, sin φ) at both cloud and event level | contract §CLM-008 F10; `fullevent_fps_dataloader.py:178-204` (`coord_idx=(5,6,7)`) |
| F8 | PET: 2 transformer blocks, 2 heads, projection_dim 32, local KNN with K=3 | `train_fullevent_nominal.py:403-407` |
| F9 | KNN coordinates are `(pos, z)` for reco and `(θ, cos φ, sin φ)` for truth; view and time are features, never coordinates | contract §reco cloud, §truth cloud |
| F10 | weighted BCE; Adam 1e-4 annealed to 1e-5; realized LR asserted against the declared policy at runtime; batch 512, niter 3, epochs 8, 2 M subsample; seed 42 frozen | `train_fullevent_nominal.py:47-71, 440-458`; `omnifold_nn/omnifold/omnifold.py:376-386` |
| F11 | `ReduceLROnPlateau(patience=1000, min_lr=1e-7)` and `EarlyStopping` on the MultiFold patience | `omnifold_nn/omnifold/omnifold.py:263-266` |
| F12 | push weight `w = exp(logit)`, identically `f/(1−f)`, computed in logit space | `omnifold_nn/omnifold/omnifold.py:453-470` |
| F13 | background is negweight-refined, fail-closed without the inventory; `purity` is a labelled control | contract §background treatment |
| F14 | data-side scalars must come from an explicit row-aligned source; a silent fallback to MC `reco_scalars` is fail-closed (CLM-007) | contract §CLM-007 |
| F15 | omitted-muon stress closure PASS (L1 0.582 prior → 0.043 full-event, 13.6× better than recoil-only); ordinary self-consistency closure PASS (push median 1.059, marginal L1 0.0021) | contract §P5A validation status |
| F16 | nominal train ≈1.1–1.3 GPU-h; the campaign multiplier is ~100 `C_stat` replicas, ~12 `C_ML` trains, 6–8 vertical universes, ~10 lateral retrains | contract §estimated cost |
| F17 | pooled routing is `tf.math.unsorted_segment_sum` plus an explicit count column | `typed_descriptor_keras.py:390-400` |
| F18 | the typed-descriptor schema serializes raw values and validity masks separately | `typed_descriptors.py:1-7` |

## G. Read from Gregor's code at `fc9a099`

Most of §G was established by the completed audit `gregor-audit/jobs/A_dataset.out.md`,
which carries line citations; those are reused rather than re-derived. Rows marked †
were verified directly for this deck.

| # | claim | citation |
|---|---|---|
| G1 | 10-column token: η, φ, log(pT+1e-6), log(E+1e-6), PID, dE/dx, x/10⁴, y/10⁴, z/10⁴, t/10⁴ | `A_dataset.out.md` §1; `preprocessing.py:546-583, 257-287` |
| G2 | 8 PID codes: 0 muon, 1 photon, 2 blob, 3/4/5 prongs (raw 3/8/13), 6 aggregated blob, 7 aggregated prong; other raw prong PIDs raise; raw PID 9 is counted by a global but has no token code | `A_dataset.out.md` §1; `preprocessing.py:422-437, 672-705` |
| G3 | structurally absent fields are literal zeros, with no validity mask | `A_dataset.out.md` §1; `preprocessing.py:389-406` |
| G4 † | PID is fed as an 8-class categorical: `point_cats = [X[:, :, pid_idx].long()]`, `point_cat_num_classes = [8]` | `train.py:1743, 1033` |
| G5 † | padded rows are all-zero, so their PID index is 0 = the muon code; **the SDPA key-padding mask excludes them and readout is CLS-only, so this is latent, not demonstrated to be harmful** | `dataloader.py:126-132`; `train.py:1776-1800`; `vit.py:356-373`. His own docstring acknowledges it: `train.py:1206` |
| G6 † | 16 global features = 10 base + 6 per-PID log energy sums, computed **after** truncation/aggregation | `A_dataset.out.md` §2; `constants/dataset.py:1-5`; `preprocessing.py:588-596, 564-594` |
| G7 † | global feature 8 is the γγ mass **or zero** when there are not exactly two retained photons | `A_dataset.out.md` §2; `preprocessing.py:680-701` |
| G8 † | joint energy sort happens **only** when the event exceeds `max_objects = 150`; otherwise the saved order is concatenation order muon → photon → blob → prong | `preprocessing.py:546-580` |
| G9 † | the dataloader keeps the **first** `max_particles` rows with no re-sort | `dataloader.py:126-132` (`_pad_or_truncate` returns `tensor[:target_len]`) |
| G10 † | `--max_particles` default **33** | `train.py:470-474` |
| G11 | aggregation is *optional*; when on, keep the top `limit−1` by energy and replace the rest with one token carrying the summed four-momentum and the **unweighted arithmetic mean** of the five auxiliary fields | `A_dataset.out.md` §6; `preprocessing.py:309-339, 494-545` |
| G12 † | `--use-max-blobs-and-prongs` defaults to **False**, so aggregation is off by default | `preprocess_dataset.py:355-377`; `A_dataset.out.md` §6 |
| G13 † | `PointGlobalMixedViT`: mixed encoder + Fourier positional MLP over `pos = X[..., :coord_dim]` with `coord_dim` default 2 (= η, φ); CLS fused with EVT token | `vit.py:226-373`; `train.py:1740` |
| G14 † | Transformer1 settings d_model 128, depth 4, n_heads 8 | `jobs/submit_train_jobs.py:150-151`; `MODELS.md` §1 |
| G15 † | continuous point features pass through `nn.LayerNorm` inside the encoder (`use_cont_layernorm=True`); the global encoder sets it False | `vit.py:135-163, 298-306` |
| G16 † | AdamW, lr 1e-4, weight decay 0.01, 1000-step linear warmup then cosine decay, grad clip 1.0, batch 2048, max_steps 100k (250k in the job script) | `train.py:660-686, 465, 927-937, 2342-2358, 2608-2615`; `submit_train_jobs.py:124` |
| G17 † | Huber on `log1p(target)` for regression by default (`--log1p_loss` default True); weighted cross-entropy for classification | `train.py:732, 2328-2336, 1809-1812` |
| G18 † | defaults on: `--use_pid` True, `use_cond = not --no_use_cond`, `--include-E-sum` True | `train.py:577, 753-756, 1079` |
| G19 | optional backbones: OmniLearned PET2 small/medium/large (128/8/8, 512/16/12, 1024/32/28), HyperScale ParticleViT, BERT | `MODELS.md` §2–3 |
| G20 | pretrained OmniLearned checkpoints: **unreachable** — `gregorkrz/HyperScale` returns 404, `portal.nersc.gov` URLs time out consistently | `gregor-audit/jobs/B_provenance.out.md` items 2–3 |
| G21 | upstream OmniLearned is MIT; the HuggingFace dataset is public CC-BY-4.0; **MC-only rows** | `B_provenance.out.md` items 1, 5 |
| G22 | no unfolding: no data leg in the ML path, no per-event weight field, no pass-reco/pass-truth flag; preprocessing hard-coded to Standard-MC directories and requires MC truth branches | `A_dataset.out.md` §4, §7 |
| G23 | his `E_avail` uses full charged-pion energy plus K±, against our pion-KE definition — an offset of order 140 MeV per π± | memory `gregor-pet2-outcome`; `constants/physics.py:24-31`; `preprocessing.py:767-787` |
| G24 † | pin: `fc9a099d3c9c060f03cef293c294f9de4eb019cd`, "small plotting fixes", 2026-07-20, clean tree; **no release tags, so this is not established to be the paper commit** | `git log -1` in `gregor-audit/minerva-ml`; `gregor-external-artifacts` |

## H. Judgements, clearly labelled as such

These appear in the deck as recommendations or arguments. None is a measurement.

| # | judgement | the argument |
|---|---|---|
| H1 | keep the muon distinguished rather than a cloud token | a distinguished event input cannot be truncated away; an energy-ranked token can |
| H2 | detector-space KNN adjacency is a better prior than (η,φ) Fourier encoding for a calorimetric recoil measurement | an argument from what the measurement is, **not** a measurement |
| H3 | weight decay is not innocuous for a likelihood-ratio classifier | OmniFold's push weight is `exp(logit)` (F12), so shrinking the logit scale biases weights toward 1. An argument from the construction; unmeasured |
| H4 | energy-weighted merging beats unweighted merging for an aggregate token | a 1 GeV and a 10 MeV blob should not contribute equally to a merged position. Unmeasured |
| H5 | test aggregation before routing | aggregation addresses a measured, large information loss at parity cost; routing is unresolved and expensive. A priority judgement under an inconclusive result |
| H6 | reserve embedding index 0 for padding | removes G5's latent hazard at zero cost |
| H7 | the four live items interact, so a matched complete-configuration comparison beats five single-factor experiments | argued in `CONFIGURATION_COMPARISON-20260918.md` §14; not demonstrated |
| H8 | capacity is an open question | 18.9× (E3) is large enough for "we are under-parameterized" to be live. No width scan has ever been run |
| H9 | warmup + cosine decay + gradient clipping is a better-conditioned schedule than constant-Adam-with-a-step-anneal | the standard argument for warmup and cosine in transformer training. **Not measured on our estimator**, which is exactly why it is listed as a candidate to test rather than a change to make |
| H10 | typed objects are worth borrowing *as a candidate* | B2's 5.3×/6.6× token reduction plus B1's much weaker cap binding. The judgement is that this is worth the coverage measurement; it is **not** a claim that the information is preserved |

## I. Anchors for the matched comparison (added this revision)

| # | claim | source | scope limit |
|---|---|---|---|
| M1 | **closure-diagnostic** recovery **0.5126033** (`VL100`) against the adopted criterion **0.494582** (`= 0.80 × ceiling 0.618228`) | job `56552326`, finalized `56562169`; `CLAIM-CLM-012.md` (viii) | **NOT a production baseline. Corrected per `OI-71`:** every artifact of that closure is prefixed `NONQUOTABLE-DIAGNOSTIC.` with `quotable: False`; **`recovery_evaluated` remains `False` at the promoted configuration**; `OI-71` is `WAITING-USER` with **G4 alone surviving** and is not determinable read-only. Whether the number may be quoted is a question the receipt **raises and does not answer** |
| M1b | **the closure's fold-forward is ≈1.011 against the promoted nominal's 0.736746, so it does not exercise the ~34 % normalization deficit — it is *silent* about that failure mode** | `OI-71`(4)(e) | this is why the powered pT closure alone is not representative validation |
| M1c | the closure driver has **no fold-forward computation at all** (`git grep fold_forward` = 0 hits over both closure drivers) | `OI-125` | adding it is ~8 lines and **must not** be done by editing the pinned driver |
| M2 | the closure's run-to-run spread is **1.226e-3** | job `56611837`; `CLAIM-CLM-012.md` (ix) | **same-configuration repeat, NOT seed-to-seed scatter.** It bounds δ from below and **sizes nothing.** The same record notes this margin had once been stated at ~10× its actual confidence |
| M3 | **97.8 %** of the baseline's gap to the ceiling is per-cell scatter; signed bias **−0.0019** | `docs/orchestration/FINDINGS-ARCHIVE-2026-08.md` BEN-038 | implies an arm can win the aggregate by being less noisy per cell; hence the mandatory decomposition |
| M4 | the ceiling **0.618228** is a **reference curve, not a proven bound** — a band was measured at `E_w[r] = 1.0333` | `CLAIM-CLM-012.md` caveat (i); BEN-038 | recovery fractions are relative to a reference |
| M5 | the ordinary self-consistency closure has **structural zero power** — a constant estimator optimizes it | `AUDIT-FINDINGS-20260728.md`; restated at `closure_fullevent_fps.py:4-9` | this is why it is not the endpoint |
| M6 | the injection protocol was predeclared **2026-08-05** and is reused unchanged | `closure_powered_truth_reweight.py:10-33` | amplitude 0.35, clip `|z| ≤ 3`, rate-preserving, truth-passing rows, two disjoint 2 M halves, split seed 7 |
| M7 | evaluation sample: **49,152,885** signal / **4,116,128** data / **564,591** background rows, `num_part` 12, sha256 `fa6b3463…`, 9,897,374,636 bytes | `nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12_RECEIPT.json`, status PASS, job `56120687`, produced 2026-07-19 | the npz itself lives on pscratch, not in the repo |
| M8 | **his representation is absent from our production input for every inventory** — no blob, prong, photon, PID, dE/dx, Michel, per-type-energy-sum or overflow key | re-measured at `44142e8c`: `dump_pointcloud_inputs.py:190-235`; first established at `GREGOR_PET2_OMNIFOLD_ASSESSMENT.md:249-255` (`b65f9ff2`) | this is what blocks Tier B |
| M9 | seed-scatter planning prior **σ ≈ 0.008** | `docs/orchestration/CLAIM-CLM-010.md`: 48 seeds, mean deviation 0.014256, **sd 0.008023** | an **adjacent** statistic, not this endpoint. A planning assumption; stage 4 measures the real thing |
| M10 | a PyTorch OmniFold backend exists — ≈10,900 lines, ≈2,900 of them tests, with `run_iterations` for multiple iterations | `nd-unfolding/pet2_torch/` at `b65f9ff2`, preserved by tag `evidence/prepublication-excluded-gregor-b65f9ff2` | its `model.py` is by its own docstring an **independent** reimplementation, **not Gregor's architecture**; its `g2_adapter.py` never saw the real payload |
| M11 | the `Transformer1` preset: d_model 128, depth 4, heads 8, dropout 0, batch 2048, max_steps 250000, lr 1e-4, wd 0.01, warmup 1000, clip 1.0 | `submit_train_jobs.py:119-153`; `train.py:660-686` | **CORRECTED: `Transformer1` is NOT a model his paper reports** — see M13 |
| M13 | the **paper lineup** is OmniLearned-small (`pretrain_s`), OmniLearned-small-rw (scratch) and OmniLearned-medium / "OL-medium-frozen" (`pretrain_m`, backbone frozen); **Transformer-xsmall/small are under `_disabled_models`** | `plot_configs/V1Paper.json`; `submit_train_jobs.py:155-169` | the paper is *Cross-Domain Transfer with Particle Physics Foundation Models* (`CITATION.bib`), so the **pretrained** arm is its contribution |
| M14 | paper backbone capacity: OmniLearned-small **2,762,550** (**58.7×** our 47,041); medium **52,294,730** (1,112×), **20,989,958** trainable with the backbone frozen | `receipts/model-capacity.json`, both instantiated | capacity is not accuracy |
| M15 | his constructor values as his code builds them: `input_dim` 4, `add_dim` 5, `pid_dim` 8, `cond_dim` 16, `num_coord` 2, **`K = 10` hardcoded** (not the `PET2` default 15); small = 8+2 transformers, 8 heads, `base_dim` 128, `mlp_ratio` 2 | `train.py:1085-1105`; `omnilearned/utils.py:11-32` | read from the factory, not from class defaults |
| M16 | checkpoints are `best_model_pretrain_{s,m}.pt` from `https://portal.nersc.gov/cfs/m4567/checkpoints` — CFS project **m4567**, not ours; **the code silently attempts a download when the file is absent** | `omnilearned/utils.py:58-79`; `B_provenance.out.md` items 2–3 | **P1 and P3 are not runnable** without them |
| M17 | **all three paper arms carry `--zero-cond-feature 2`**, which zeroes global index 2 = `log(hadron_recoil)` | `submit_train_jobs.py:156,165,169`; `preprocessing.py:618-624` | his paper configuration **deliberately removes a hadronic recoil summary** |
| M18 | the cap is a **Python** choice: the dump binds full-length `ROOT.std.vector("double")` cloud buffers and `_pad_tokens` truncates them | `dump_pointcloud_inputs.py:90-112, 252-268`; `FULL_EVENT_INTERFACE_REQUEST.md` "Available NOW" | **so cap, overflow aggregation, merged counts and discarded energy need NO C++** |
| M19 | **the npz carries no event key**; the AnaTuple carries `ev_run`/`ev_subrun`/`ev_gate` | `dump_pointcloud_inputs.py:190-235`; `typed_descriptor_source_smoke.py:86` | so a Python-side join is impossible **because the key is discarded**, not because data is missing. R-1 asks for three scalar branches |
| M20 | `FULL_EVENT_INTERFACE_REQUEST.md` §D is **"Residual-energy summary tokens (optional)"**; §§A–C (muon object, view/time, vertex) **landed**; **no filed request for the typed vocabulary exists**. Owner is **Agent A** | that file, in full | revision 1 cited §D as the typed-object request |
| M21 | truth `E_avail` is already in the npz as `truth_scalars` col 2 (`MC_eavail`) | `dump_pointcloud_inputs.py:79` | so the hadronic injection needs **no new export** |
| M22 | step-cost ratio to ours: **1.6×** (batch 64) and **5.8×** (batch 512) for PET2-small; 7.6× / 40.9× for medium | `receipts/step-cost-scale.json` | **the ratio moves 3.6× with batch, so it is overhead-dominated and is NOT a scaling estimate.** CPU and cross-framework. Its value is refuting both `r≈1` and the 58.7× parameter extrapolation |
| M12 | the prior campaign declined a cross-framework comparison because it would "confound framework, representation, and training engine" | `GREGOR_PET2_OMNIFOLD_ASSESSMENT.md:414-417` | the reason the matched design runs both arms in one engine |

## J. Campaign spend, and where it does not reconcile

| item | GPU device-hours | source |
|---|---:|---|
| representation matrix, 24 paired jobs | 13.27 | `matrix-summary.json`, `compute.job_wall_seconds_total` = 47,778 s |
| A3 geometry probe + width gate, 5 submissions | 0.43 | `GO_NO_GO-20260918.md` §7 (1,563 s) |
| tail validation, 4 of 4 submissions | 0.77 of 1.5 authorized | `validation-final.json`; 2,782 s |
| inference benchmark + matrix closeout | **not itemized** | --- |
| A1 source characterization | (CPU: 2.0 core-h) | `source-multiplicity.json` |
| **campaign total** | **16.0 of 290** | `RECOMMENDATION-20260918.md` |

**These do not sum, and the deck says so.** The itemized rows total 14.47; the
difference is the inference benchmark — including one 35-minute timeout (job 58461843)
that measured nothing — and the matrix closeout, neither of which is separately
itemized in a receipt I can cite. Reported as a gap rather than closed by arithmetic.

## K. Explicitly withdrawn

| withdrawn claim | replaced by |
|---|---|
| "aggregate overflow is free" | C2 + C3: indistinguishable from parity at ±3.3 %, plus real non-compute costs (dump regeneration, schema field, re-validation, fingerprint) |
| "the direction of a synthetic effect transfers" | the transfer caveat under §D |
| "noise-only generic inputs give an upper bound" | withdrawn without replacement |
| "undetected errors cancel in paired contrasts" | the V13 duplicate-arm null, measured in the endpoint's own units |
| "B−A failing makes C−B irrelevant" | the three primary contrasts are read together, not in sequence (`ENDPOINT_SPECIFICATION-20260918.md`) |
| "25.8 points is measured power for this endpoint" | D4: a planning assumption from a different fixture |
| "the execution path is validated across the intended range" | C5: 10 of 13 widths; validation is **incomplete** |

## N. Corrected in revision 2 of the proposal

| revision 1 claim | correction |
|---|---|
| "the exact upstream configuration is the `Transformer1` preset" | **not a paper model** — M13 |
| "his model is 18.9× ours" | that is Transformer1; the paper backbone is **58.7×** — M14 |
| "the representation is blocked on a C++ event-loop deliverable" | **partly false** — cap, overflow, merged counts and discarded energy need no C++ — M18 |
| cited interface-request "§D" for typed objects | §D is residual-energy tokens; **no typed request exists** — M20 |
| "our production baseline on the endpoint is 0.5126033" | a `quotable: False` closure diagnostic, `recovery_evaluated: False` at the promoted configuration — M1 |
| δ = 0.018 justified as the margin over the adopted criterion | **withdrawn** — it rested on M1. Replaced by δ = 0.017 as a *decision anchor*: half the −0.0342 recovery loss the campaign accepted for the LR anneal |
| V-PORT checked forward agreement only | extended to **forward, gradient and weight-update** — forward agreement does not show training is equivalent |
| sizing used normal quantiles | **t-based, iterative**, sized on the upper confidence bound of the pilot's σ |
| "one endpoint" | the injection is a **muon** kinematic; the primary endpoint is now a truth-`E_avail` tilt (M21), with the pT tilt kept as a muon-side control |
| 70 GPU-h as the campaign cost | **a Tier-A ceiling only**; completion is `8c(1+r)` with `r` unmeasured — M22 |

## L. Corrected in the 2026-09-18 matched-comparison revision

| what was wrong | correction |
|---|---|
| the deck read as a **recommendation** | relabelled an **interim inventory**; slide 2 states that no configuration is selected and that retaining ours is a **provisional engineering choice**, not a result |
| "5.3×/6.6× fewer tokens **for a description of the same hadronic system**" | the equivalence is **unmeasured** and is withdrawn; the slide now says so in the same cell |
| slide 11's column header read "**measured** cost" over two `≈ 0` cells | header is now "cost", and each cell is marked *est.* or *measured* |
| "typed-object energy coverage" listed as the prerequisite for three borrowings | corrected to **"absent from the dump"** — coverage was a proxy; absence is the actual blocker |
| coverage presented as **the gate** on the three largest borrowings | **retired as a gate.** Tier B measures the representation directly; coverage survives only as a diagnostic if R4 lands |
| "his schedule is better conditioned and free" stated as a consequence | labelled *judgement, unmeasured on our estimator* |
| the component priority ("test aggregation before routing") | **retired.** Complete configurations are compared instead, because the components interact |
| I read `pet2_torch/engine.py` as **limited to one iteration** | wrong: `run_iterations` loops complete Step-1/Step-2 iterations, so niter 3 is reachable. The module is still not used, for the three reasons at proposal §4 |
| Appendix C's "variance pilot" could be read as the matched comparison's pilot | disambiguated: that pilot is the **retired synthetic** one; stage 4 is a different sample, endpoint and purpose |

## M. Things this deck does not establish

- **That either configuration unfolds better.** No head-to-head on our unfolding task has
  been run; his configuration has never been evaluated on the powered-closure endpoint.
- That our configuration is better than Gregor's, in any category.
- That typed objects preserve the information our cluster cloud carries. **Unmeasured,
  and it is the prerequisite for the three largest borrowings.**
- That aggregation improves closure. **No closure measurement of aggregation exists.**
- That the cap binds as often in the **selected**, POT-weighted population.
- Anything about real-data performance, any covariance, any systematic, any
  central-value change, or any Gate-6 action.
- That `fc9a099` is the commit behind arXiv:2604.12364.
- That the port performs comparably to, better than, or worse than anything. **It has
  been shown to BE his network and to train under our engine. No comparative result
  exists.**
- That the ≈188 GPU-h projection covers his arm at his native batch under the math
  repair, a pretrained rather than scratch backbone, or a same-framework ratio.
