# Intended vs executed training recipe: the historical PET comparison (task A1, 2026-09-22)

Scope §4 A and B. **Subject:** the comparison's training path at code commit
`68cf9d29f8ab1b0f5acd933d4baec1962b29e34d` (`configuration_comparison/run_arm_evaluation.evaluate`),
whose full-scale runs are under `/pscratch/sd/j/josephrb/campaign-20260920/{tuning,pilot,final}`.
The historical outputs, thresholds and verdict are untouched. This is diagnostic evidence, not a
verdict about the comparison and not a cause of the recovery shortfall.

## Evidence and how strong each kind is

| tag | evidence | object (sha256) | job |
|---|---|---|---|
| **L1** | Runtime capture. `phase_a/runtime_audit.py` calls the historical `evaluate()` UNMODIFIED from a clean checkout at 68cf9d29, through the unedited OI-136 guard, both arms, seed 17, stage `tuning`, `--max-events 100000` (14,203 step-1 rows, 9,995 step-2 events), **the full historical recipe: 3 iterations x 8 epochs**. It only observes (class-level wrappers on `Model.fit`, `train_step`, the optimizer's `_clip_gradients`, and `MultiFold` via a post-import hook). | `receipts/runtime_audit_ours.json` (a1f48fad…), `receipts/runtime_audit_theirs.json` (8dadb3f3…); guard inventories `receipts/guard-audit-{ours,theirs}.json` | 58742195 (after 58742194, the historical `prematerialize_theirs` for the same subsample) |
| **L2** | Logs the full-scale runs themselves left: engine log `log_<run>.txt` (per-step step counts computed from the engine's own `BATCH_SIZE`), the pickled Keras `history` of every fit (`loss`, `val_loss`, `lr` per epoch), the driver receipt (`realized_learning_rates` is the annealed estimator's interception of `model.optimizer.learning_rate` after each fit-time compile), `allocation.txt`. All 56 runs (32 tuning, 8 pilot, 16 final) = 336 fits. | `receipts/historical_receipts.json` (938b9752…), mined read-only by `phase_a/mine_historical_receipts.py` | login node, guard inventory `receipts/guard-mine.json` |
| **B** | Runtime rebuild of one MC shard of his inputs with the historical builder, compared to the executed shard; per-event muon rule; branch lists of the R4 slim and of the original MC AnaTuple. | `receipts/theirs_build_check.json` (375a0c4c…) | 58742048 |
| **S** | Source reading at 68cf9d29, labelled as such. Never used alone to CONFIRM. | file:line | — |

The L1 subsample is small, so step counts, split sizes and argmin epochs at L1 describe the
mechanism, not the full-scale values; full-scale values come from L2 or, where marked, from the
engine's own formula applied to L2's logged step counts.

## The table

`ours` = production PET on the cluster cloud (step 1) and truth cloud (step 2). `theirs` = PET2-small
pretrained arm at step 1; step 2 is declared identical to ours (`frozen_design.STEP_SCOPE`,
`frozen_design.py:123-140`). "Match" compares executed with intended for that cell.

### Optimizer

| parameter | step | arm | intended (source) | executed (evidence) | match |
|---|---|---|---|---|---|
| optimizer class | 1, 2 | ours | "engine Adam with the annealed policy" (`frozen_design.py:29`) | Keras `Adam` subclass created by `hvd.DistributedOptimizer` (class `Adam`, module `horovod._keras`), all 6 fits (L1 `fits[*].optimizer_at_train_begin.class/class_module/mro`) | yes |
| optimizer class | 1 | theirs | `TorchAdamW(1e-4, wd 0.01) + warmup/cosine + global-norm clip 1.0` (`frozen_design.py:44`) | the same Horovod-wrapped Keras `Adam`, all 3 step-1 fits (L1). `training_recipe.build_optimizer` / `ClippedTorchAdamW` are never reached | **NO — CONFIRMED (hypothesis A)** |
| optimizer class | 2 | theirs | identical to ours' step 2 (`frozen_design.py:126`) | Horovod-wrapped Keras `Adam` (L1) | yes (class) |
| weight decay | 1, 2 | both | ours: none stated; theirs step 1: 0.01 decoupled (`frozen_design.py:44`, `training_recipe.py:47-55`) | `weight_decay = None` in every executed optimizer (L1 `optimizer_at_train_begin.weight_decay`) | ours yes; **theirs step 1 NO — CONFIRMED** |
| gradient clipping | 1, 2 | both | ours: none stated; theirs step 1: global norm 1.0, torch semantics | `clipnorm = global_clipnorm = clipvalue = None` in every fit, and measured: the global gradient norm entering `_clip_gradients` exceeded 1.0 on **100 %** of updates (max 1474 theirs step 1, 877 ours step 1) and clipping changed **no** update (L1 `epochs[*].grad_global_norm_pre_clip`, `clip_changed_norm_in_any_update`) | ours yes; **theirs step 1 NO — CONFIRMED**. Note the scale: with weights normalized to 1e6 per class the loss is O(100) and every update would have been clipped |
| schedule | 1, 2 | both | ours: constant per fit + anneal; theirs step 1: linear warmup then cosine (`training_recipe.WarmupCosine`) | no schedule object (`learning_rate_is_schedule = False`); learning rate identical at every epoch end of every fit (L1). Full scale: the per-epoch `lr` in every one of the 336 histories is constant within the fit (L2 `histories[*].lr`) | ours yes; **theirs step 1 NO — CONFIRMED** |
| betas, epsilon, amsgrad | 1, 2 | both | torch defaults for theirs step 1 (`TORCH_DEFAULTS`: 0.9, 0.999, eps 1e-8) | 0.9, 0.999, eps 1e-7, amsgrad False (L1 `config`) | theirs step 1: eps differs (1e-7 vs 1e-8) |
| optimizer XLA | 1, 2 | both | `EXECUTION.jit_compile = False` (`frozen_design.py:95`, about the model) | executed optimizer config `jit_compile = True` (Keras default; the log prints "Compiled cluster using XLA") (L1) | model-level statement not contradicted; recorded |
| optimizer state across fits | 1, 2 | both | not specified | a NEW optimizer at every fit: `iterations = 0` at train begin, never the same object twice (L1 `optimizer_seen_before = False`) | executed engine behaviour, not a declared choice |

### Learning rate

| parameter | step | arm | intended (source) | executed (evidence) | match |
|---|---|---|---|---|---|
| iteration-0 rate | 1 | both | the rate TUNING selected per arm (`sbatch_campaign.sh`; selection ours 4e-4, theirs 1e-4 in `tuning/selected_learning_rate.json`, L2 `tuning_selection`) | ours 4e-4, theirs 1e-4 at pilot and final (L2 `realized_learning_rates`, per-epoch `lr`); the audit's argument 1e-4 reached both steps (L1) | yes |
| iteration-0 rate | 2 | both | step 2 identical for both arms (`frozen_design.py:126`) | the arm's step-1 selection reaches step 2 through the engine's single `self.LR`: **ours 4e-4, theirs 1e-4** at pilot and final (L2 `summary.final/*.realized_lr_by_fit`, second entry per iteration; per-epoch `lr` of every `_step2.pkl`) | **NO — CONFIRMED (hypothesis B)** |
| iterations 1-2 rate | 1, 2 | both | ours: "annealed policy" (`frozen_design.py:29`); theirs: not stated (warmup/cosine at 1e-4 implied) | **1e-5 for every fit after the first, both arms, both steps**, every stage: `_AnnealedMultiFold.CompileModel` forces `fixed=True` (`annealed_estimator.py:71`) and the engine's `get_optimizer` then uses `min_learning_rate = 1e-5` (`omnifold.py:376-377`) (L1 `compiles[*].fixed_argument_seen_by_base`, lr; L2 `realized_learning_rates`) | ours yes; **theirs NO — CONFIRMED**. Consequence: the tuned rate governs iteration 0 only |

### Batch, updates, examples, epochs, stopping

| parameter | step | arm | intended (source) | executed (evidence) | match |
|---|---|---|---|---|---|
| batch size | 1 | ours / theirs | 512 / 2048 (`frozen_design.py:28,43`) | 512 / 2048: rows of the last batch of every epoch (L1 `epochs[*].last_batch_rows`); full scale: engine log `1661 / 415 training steps at reco` for 850,644 rows (L2 `engine_log`, `engine_log_implied.step1_batch_range`) | yes |
| batch size | 2 | ours | 512 (the shared recipe) | 512 (L1); `2344 steps at gen` for 1,200,286 rows (L2) | yes |
| batch size | 2 | theirs | identical to ours (`frozen_design.py:126`) | **2048** (L1 all 3 step-2 fits); full scale `586 steps at gen` for 1,200,286 rows = batch 2045-2048 (L2, every theirs run of every stage) | **NO — CONFIRMED (hypothesis B)** |
| optimizer updates / epoch | 1, 2 | both | "equal example presentations" (`training_recipe.py` docstring) | L1 (100k subsample): ours 21 / 31, theirs 4 / 7 (step 1 / step 2), measured as `optimizer.iterations` deltas. Full scale, engine formula `floor(0.8 * num_steps)` on L2's logged step counts: ours **1328 / 1875**, theirs **332 / 468** | step 2: theirs gets 4.0x fewer updates per epoch at a 4x lower iteration-0 rate |
| examples / epoch | 1, 2 | both | equal presentations | L1: ours 10,752 / 15,872, theirs 8,192 / 14,336, measured in-graph (rows through `train_step`). Full scale by formula: ours 679,936 / 960,000, theirs 679,936 / 958,464 | yes at full scale (<0.2 %); at small scale the engine's flooring makes them unequal |
| zero-weight rows in step 1 | 1 | both | — | 5,778 of 9,995 MC rows carry weight 0 at step 1 (non-`pass_reco`, `weights_push * w_reco * pass_reco`) and still occupy batch slots (L1 `caches[0].weights_label0.n_zero`) | engine design; recorded |
| epochs | 1, 2 | both | `EPOCHS = 8` (`training_recipe.py:60`) | 8 in every audited fit (L1) and in all 336 full-scale fits (L2 `summary.*.epochs_run = [8]`) | yes |
| early-stopping rule | 1, 2 | both | engine: `EarlyStopping(patience=10, restore_best_weights=True, monitor=val_loss)` + `ReduceLROnPlateau(patience=1000)` + `ModelCheckpoint(save_best_only)` (`omnifold.py:263-275`); the driver passes no `early_stop`, so patience is the default 10 | exactly those callbacks (plus Horovod's broadcast/average callbacks) (L1 `fits[*].callbacks`); **it never fired**: `stopped_epoch = 0` in every fit (L1), 8 epochs everywhere (L2). With patience 10 > 8 epochs it cannot fire | executes as written; inert |
| which weights leave each fit | 1, 2 | both | ambiguous: the engine's `restore_best_weights=True` and best-only checkpoint suggest the best-validation epoch; the frozen design fixes 8 epochs | **the LAST epoch's weights, in 12 of 12 audited fits**, while the validation-loss minimum was the last epoch in only 1 of 12 (L1 `at_train_end`). Keras 2.15 restores best weights only when stopping fires (`keras/src/callbacks.py:2124-2132`, S). Full scale: validation-loss argmin is the last epoch in 30/48 ours-final and **7/48 theirs-final** fits (tuning 17/96 and 16/96, pilot 2/24 and 1/24) (L2 `summary.*.fits_whose_val_loss_argmin_is_last_epoch`); the best-epoch checkpoint on disk is never read for reweighting | **CONFIRMED: restore rule inert**; whether "last" or "best" was intended is not established |

### Validation split, RNG, model identity, initialization

| parameter | step | arm | intended (source) | executed (evidence) | match |
|---|---|---|---|---|---|
| validation split construction | 1, 2 | both | engine: one `np.random.shuffle` of the step's rows at iteration 0, reused; last `NTEST = int(0.2 * num_steps * B)` rows held out (`omnifold.py:233-235, 341-371`) | as written: split fixed across iterations (identical permutation digest in iterations 0-2, L1 `caches`). The permutation is **identical across arms** (step 1 `d1df7d1c…`, step 2 `469cd9a9…`; NumPy state identical at both caches), but the cut point depends on the batch, so the held-out ROWS differ: step 1 ours 3,143 vs theirs 4,372, step 2 ours 4,015 vs theirs 5,244 rows, different row-set digests (L1 `validation_row_set_digest`) | **step 2: NO — CONFIRMED (hypothesis B)**: the declared-identical truth step validates on a different subset in the two arms |
| validation unit | 2 | both | — | rows, not events: step 2 duplicates each event (label 0 and label 1), and the two copies are split independently (S `omnifold.py:352`; L1 split sizes) | recorded |
| RNG seeding | 1, 2 | both | one estimator seed per pair, same for both arms (`frozen_design.SEEDS`; `run_arm_evaluation.py:252` `set_random_seed(seed)`) | one global `set_random_seed` per process; NumPy stream identical across arms at both cache points (L1) | yes |
| step-2 initial weights | 2 | both | "same weights initialisation policy" (`frozen_design.py:126`) — policy, not values | policy identical (scratch `PET`, `run_arm_evaluation.py:392`), but the **realized** iteration-0 step-2 weights differ between arms at the same seed (ours `334eff3f…`, theirs `a6eef389…`, L1 `weights_at_train_begin.digest`): building his step-1 model consumes the global TF RNG first | policy yes; realized init is RNG-coupled to the step-1 arm (uncontrolled, not a policy defect) |
| model across iterations | 1, 2 | both | not specified | iteration 0: a `clone_model` copy of the template (new object); iterations 1-2: the SAME object, warm-started — weights at fit start equal the previous fit's end (L1 `model_seen_before_in_fit`, `warm_start_from_previous_fit_of_this_step = True`) | engine behaviour |
| pretrained weights at the first optimizer step | 1 | theirs | `best_model_pretrain_s.pt via load_pretrained_omnilearned` (`frozen_design.py:45`); `TheirsCompleteArm.get_config` carries the state through `clone_model` | at the first optimizer step of iteration 0 the CLONE's 176 tensors equal `pretrained_state_s.npz` (sha256 `2480f269…`) exactly, 176 / 176, worst difference 0.0 (L1 `fits[0].at_first_optimizer_step.pretrained`); iterations 1-2 start from the fine-tuned weights (warm start). All 28 theirs runs record the template load as exact (L2) | **yes — pretrained weights survive cloning** |
| what "pretrained" covers | 1 | theirs | manifest `receipts/PRETRAINED_STATE_MANIFEST-20260919.json` | by the manifest, `cond_embed.*`, `pid_embed.0.weight`, `add_embed.0.fc1.weight`, `local_physics.mlp.fc1.weight` and the output layer `out.*` are torch-seeded re-initializations, not checkpoint values; everything else is from the checkpoint | as designed |

### Inputs that reach the model (L1 `inputs`, the arrays handed to `from_tensor_slices`)

| parameter | step | arm | intended (source) | executed (evidence) | match |
|---|---|---|---|---|---|
| his token features | 1 | theirs | `[delta_eta, delta_phi, log pT, log E, PID | dEdx, x/1e4, y/1e4, z/1e4, t/1e4]` (`theirs_token_schema.py:39-59`, via `materialize_theirs.py:79-92`) | converted features: eta in [-3.2, 9.0] (within the ±10 clip), phi within ±π, log E ≥ log pT on 99.98 % of real tokens, positions ≤ 0.90 after /1e4, no −9999 sentinel, **no non-finite value** (the stored intermediate carries +inf dE/dx on 5 prong tokens per 20,000 events, B; the conversion removes them), PID values {0,1,2,3,4,6,7} (L1 `inputs.step1.theirs_semantics`) | **yes — the raw-momentum defect is NOT present at runtime**. `theirs_omnifold_arm.py:11,43` still describe `[px, py, pz, log E, PID]`: a stale comment |
| our cluster cloud | 1 | ours | `(E, pos, z, view, time)` scaled (`fullevent_fps_dataloader.py:133-176`) | as declared; `z` spans 4.3-10.0 (uncentred), `time` up to 99.8 (L1 `inputs.step1.cloud`) | yes |
| our step-1 event features | 1 | ours | 13 features incl. `mu_minos_ok` (`fullevent_fps_dataloader.py:266-270`) | `mu_minos_ok` is identically 0 in every row of the subsample: a constant input (L1 `inputs.step1.event`) | recorded (degenerate feature) |
| truth cloud | 2 | both | `(E, px, py, pz, pdg, theta, cos φ, sin φ)` with "keep raw PDG (embed in prod)" (`fullevent_fps_dataloader.py:178-205`) | identical arrays in both arms (cloud `0f970eb2…`, event `a8e02f38…`); the `pdg` column holds **raw PDG codes from −3122 to 2.0e9** (L1 `inputs.step2.cloud`), and `PET` feeds every column to `Dense` layers and the KNN features with no embedding (`net.py:147-155, 290-293`, S) | declared-identical across arms: yes. The "embed in prod" note has no counterpart in the executed network. Shared by both arms, so it cannot explain the between-arm gap; a candidate for the common shortfall (Phase B/C) |
| truth event features | 2 | both | `DEFAULT_TRUTH_EVT_FEATURES = ("pt", "pparallel")` | 2 columns, identical arrays in both arms (L1) | yes |

### His inputs: the three declared differences (B)

| difference | what ran (runtime) | resolvable? |
|---|---|---|
| muon presence from `MasterAnaDev_muon_E > 0` instead of his MINOS match | the builder that produced the shards (`/pscratch/sd/j/josephrb/build_theirs_inputs.py`) is blob-identical to 68cf9d29's (`4fc79a58`); rebuilding 20,000 events of `1A_MC/run00110000` reproduces the executed shard exactly (tokens, add_info, globals, identity); a muon token is present **iff** `muon_E > 0` in 20,000 / 20,000 events (71.3 % have one) | NOT from R4 (the slim has no MINOS branch). The original MC AnaTuple carries `muon_is_minos_match_track`, `muon_is_minos_match_stub`, `minos_track_match`, `isMinosMatchTrack`, `n_minos_matches` — resolvable by a new, manifested extraction. Which flag his `get_muons(only_keep_minos_matched=True)` reads is NOT ESTABLISHED |
| `prong_dEdXMean` for `prong_part_dEdXMean` | the builder reads `prong_dEdXMean` (rebuild identity above) | NO: `prong_part_dEdXMean` is absent from the R4 slim (65 branches) AND from the original MC AnaTuple (4,102 branches) — keep the adapted-arm label |
| proportional token-cap split | the cap (33) binds in 13.3 % of events (2,652 / 20,000); there, a mean of 49.2 objects (45.1 blobs) becomes 27.5 blob tokens, 1.4 prong tokens and aggregate tokens (B `cap_split`) | NO from existing sources: his `max_blobs` / `max_prongs` are not in the repository (`build_theirs_inputs.DECLARED_DIFFERENCES`) — keep the label |

### Provenance of the executed code

* **OI-136 at runtime.** The historical path loads `omnifold.omnifold`, `omnifold.net`, `omnifold.dataloader`,
  `omnifold.utils`, `annealed_estimator` and `atomic_write` from the hardcoded tree
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold`, not from the pinned checkout
  (`fullevent_fps_dataloader.py:57-60` and `train_fullevent_nominal.py` insert it at `sys.path[0]`); the
  driver's own `_shadowed` check covers only `fullevent_fps_dataloader` and `training_recipe`.
  **All loaded files are blob-identical to 68cf9d29** (L1 `module_provenance`: 7 from the hardcoded
  tree, 10 / 16 from the pinned checkout, zero mismatches outside the harness's own files), and that
  tree's HEAD has been `32e403b8` since 2026-08-29 (its reflog), so the full-scale runs loaded the same
  bytes. No effect on what executed; a provenance defect to record.
* **Stage commits.** Tuning launched at `395f296d`, pilot at `c934c527`, final at `33a3f264` (the
  execution checkout's reflog; the launcher asserts HEAD = COMMIT). None differs from 68cf9d29 in any
  training-path file (`git diff --stat` over `omnifold_nn` and `nd-unfolding/pet/**/*.py`, excluding
  scoring/report/test files).
* **Guard.** The unedited guard (blob `3929da3a`) refused NumPy's `lscpu` probe (job 58742046); the
  harness takes NumPy's own fallback (`phase_a/numpy_probe.py`, precedent 2026-09-10). The full-scale
  campaign ran unguarded, so the probe ran there and returned the same `False`.

## Verdicts on the two hypotheses

* **A (optimizer): CONFIRMED.** His arm's step 1 executed Horovod-wrapped Keras Adam with no weight
  decay, no clipping (while every update's gradient norm exceeded the intended clip), no warmup/cosine,
  and 1e-5 after the first iteration — not the declared TorchAdamW recipe.
* **B (shared step 2): CONFIRMED.** The declared-identical truth step differed between arms in batch
  size (2048 vs 512: 4x fewer updates per epoch), iteration-0 learning rate (1e-4 vs 4e-4 at pilot and
  final), and validation subset. The realized step-2 initialization also differs (RNG coupling), which
  is seed variation rather than a policy difference.
* **Also confirmed:** the early-stopping/restore rule is inert, and each fit hands on its last-epoch
  weights even where validation loss rose.
* **Not a defect:** pretrained weights survive cloning; his inputs are the converted features; step-2
  input arrays are identical across arms; the three declared input differences are what ran.

What this does NOT establish: that any of these differences caused the recovery shortfall or the
between-arm gap. That needs the corrected-baseline experiments.
