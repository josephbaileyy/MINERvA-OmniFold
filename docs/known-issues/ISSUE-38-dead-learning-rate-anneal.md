## The engine's per-iteration learning-rate anneal is dead code, so every iteration trains at full LR (found 2026-08-09)

`MultiFold.Unfold()` calls `self.CompileModels(fixed=True)` after each iteration
(`omnifold_nn/omnifold/omnifold.py:177`). `fixed=True` routes to
`get_optimizer(..., fixed=True)` -> `Adam(learning_rate=1e-5)` instead of `self.LR`, so the evident
intent is to anneal the learning rate once the first iteration has established a coarse solution.

**It has no effect, for two independent reasons.**

1. `CompileModels` compiles `self.model1` and `self.model2` — and those objects are **never trained**.
   `RunModel` trains `model_e`, which at iteration 0 is `tf.keras.models.clone_model(model)` appended to
   `step1_models`/`step2_models`, and at later iterations is that same clone retrieved from those lists.
   It only reaches the trained clones under `if self.n_ensemble > 1`, and
   `train_fullevent_nominal.py:54` sets `n_ensemble = 1`. This is the same trap as issue #26 / BEN-043:
   `self.model1` and `self.model2` are not the trained models.
2. Even where it does reach a clone, `RunModel` **unconditionally recompiles immediately before
   `fit()`**: `self.CompileModel(model_e, num_steps)` at `:292`, with `fixed` defaulting to `False`, i.e.
   the full `self.LR`. Any `fixed=True` compile is therefore overwritten before training in every
   configuration.

So in the publication configuration **every step-1 and step-2 fit runs at the full learning rate with
warm-started weights**, and no annealing occurs at any iteration.

**Why this matters right now rather than as tidy-up.** The 2026-08-09 step-1 trajectory
(`STEP1_TRAJECTORY.slurm-56525829.json`) showed the fold-forward deficit is created *by iterating*:
`push dev` goes `-0.0279 -> -0.1392 -> -0.3446`, with the signature of a collapsing high-ratio tail
(`p95` 4.6474 -> 1.4682, a 3.17x shrink; median 0.13-0.24 throughout, so the mean is a tail phenomenon).
Full-LR retraining of a warm-started classifier every round is exactly the regime in which a learned
representation is reshaped hard enough to lose that tail — so this dead anneal is a **candidate mechanism
for the degradation**, not merely a cosmetic defect. The concurrent step-1 dynamics factorial
(`56531057`) tests warm-start and split reuse but has **no learning-rate arm**; its predeclared
"no arm repairs" branch attributes the residue to "intrinsic push feedback / representation-tail
contraction", for which this would be a cheap fourth arm.

**Do not "fix" this silently.** `omnifold.py` is shared engine code on the gated path, and repairing the
anneal would change every published number. It is recorded here as a measured property of the estimator
that produced the current results.

