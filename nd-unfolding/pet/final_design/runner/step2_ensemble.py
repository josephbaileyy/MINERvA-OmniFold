"""[pfd] Estimator-internal step-2 ensemble (PROTOCOL-20260925 Amendment 3b, item 5).

The declared fallback for the N2 finding (the truth step dominates the estimator-seed variance):
at every OmniFold iteration the truth step fits M independently seeded models on the SAME inputs
(same labels, weights, pull and validation split) and the push is the average of the M models'
per-event weights. It recurs inside every run, hence inside every section-9 bootstrap member.
Configured by `RunConfig.step2.ensemble` (`recipe.StepRecipe.ensemble`, serialized only when
!= 1), so M enters the config content hash and the run identity.

M = 1 is not routed through this module at all: `driver_class` returns the B2 class unchanged,
so M = 1 runs the predecessor's code path with its seeds, bit for bit.

Weight space. Each member's weight is the engine's own `MultiFold.reweight` of that member alone
(`omnifold_nn/omnifold/omnifold.py`): w_m = exp(clip(logit_m, -30, 30)), identically
f/(1-f) with f = sigmoid(logit) below the cap, with the engine's fail-closed check on non-finite
logits. The push is the arithmetic mean of the w_m, accumulated as the engine accumulates its own
multi-model average (`avg += w_m / M` in member order, float64), then cast to the push's float32 by
the caller exactly as for one model. Averaging is in WEIGHT space (likelihood-ratio space), not
in logit or probability space: mean_m exp(logit_m) >= exp(mean_m logit_m), and the weight is the
quantity the engine applies.

Seed rule. Member 0 uses the step-2 seed `s = config.step2.seed` unchanged (so member 0 is,
at the first iteration, the M = 1 fit). Member m >= 1 uses
    s_m = run_unfold.derive_seed(s, "step2_ensemble", m)
(sha256 of the tuple's repr, first 4 bytes, mod 2^31), and every per-fit seed of that member
follows the predecessor's rules with s_m in place of s: pre-step global seed
derive_seed(s_m, 2, i, "pre_step"), init derive_seed(s_m, 2, "init", 0 | i), shuffle
derive_seed(s_m, 2, i, "shuffle"), fit derive_seed(s_m, 2, i, "fit"). The validation split is
NOT member-specific (it uses `step2.validation.seed`, shared). For a bootstrap member the config
is `design_inputs.bootstrap_config`'s, so s (and hence every s_m) is that member's step-2 seed.
Members are fitted in order m = 0..M-1, each reseeded before its fit, so a member's fit depends
only on (s_m, iteration, inputs, its own previous model) and not on the others.

Warm start and resume. Each member warm-starts from its own previous-iteration model. Member 0 is
persisted where the predecessor persists the single step-2 model (`iterations/modelsNN.npz`,
keys `s2_*`); members m >= 1 in `iterations/s2membersNN.npz` (keys `mMM_JJJJ`), written BEFORE
`state.json` declares the iteration complete; a resume refuses if that file or any member is
missing. Per-member h5 checkpoints are `weights/iter{i}_step2_member{m:02d}.weights.h5`.

Records. Every step-2 fit record carries `step2_ensemble` = {member, members, step_seed} next to
the predecessor's `fit_seconds`; every epoch record of a member carries
`step2_ensemble_member` in its context; every iteration record carries `step2_ensemble` with the
member seeds, per-member fit / RunModel / predict seconds, and the across-member spread of the
weights on truth-passing events.
"""

from __future__ import annotations

import contextlib
import dataclasses
import os
import time
from pathlib import Path
from typing import Any, Iterator, Sequence

SEED_SALT = "step2_ensemble"
MEMBERS_FILE = "s2members{i:02d}.npz"
WEIGHT_SPACE = ("mean over members of the engine's per-member weight exp(clip(logit, -cap, cap)) "
                "(= f/(1-f) below the cap), accumulated avg += w_m / M in member order")
SEED_RULE = ("member 0: step2.seed; member m >= 1: run_unfold.derive_seed(step2.seed, "
             "'step2_ensemble', m); all per-fit seeds of a member from its seed by the "
             "predecessor's rules; the validation split is shared")


def ensemble_size(config: Any) -> int:
    return int(config.step2.ensemble)


def member_seeds(step2_seed: int, members: int, derive_seed: Any) -> list[int]:
    """The step seed of each member (the rule in the module docstring). Refuses a collision."""
    seeds = [int(step2_seed)] + [int(derive_seed(int(step2_seed), SEED_SALT, m))
                                 for m in range(1, int(members))]
    if len(set(seeds)) != len(seeds):
        raise SystemExit(f"[s2ens] member seeds collide: {seeds}")
    return seeds


def average_member_weights(np: Any, member_weights: Sequence[Any]) -> Any:
    """The push of an M-member ensemble: the engine's own multi-model accumulation
    (`MultiFold.reweight`: zeros, then `+= w / len(models)` per model), over per-member weights.
    For M = 1 this returns w_0 bit for bit."""
    n = len(member_weights)
    if n < 1:
        raise ValueError("no member weights")
    avg = np.zeros(len(member_weights[0]))
    for w in member_weights:
        avg += w / n
    return avg


def spread_record(np: Any, member_weights: Sequence[Any], mask: Any) -> dict[str, Any]:
    """Across-member spread of the weights on the rows of `mask` (truth-passing events): per
    event the members' sample sd over their mean (weights are exp(logit) > 0), summarized."""
    w = np.stack([np.asarray(x, np.float64)[np.asarray(mask, bool)] for x in member_weights])
    if w.shape[0] < 2 or w.shape[1] == 0:
        raise ValueError("a spread needs >= 2 members and >= 1 row")
    rel = w.std(axis=0, ddof=1) / w.mean(axis=0)
    q = np.quantile(rel, [0.5, 0.9, 0.99])
    return {"rows": int(w.shape[1]), "member_mean_weight": [float(x) for x in w.mean(axis=1)],
            "relative_sd_mean": float(rel.mean()), "relative_sd_p50": float(q[0]),
            "relative_sd_p90": float(q[1]), "relative_sd_p99": float(q[2])}


def receipt_record(config: Any, derive_seed: Any) -> dict[str, Any]:
    m = ensemble_size(config)
    return {"members": m, "member_seeds": member_seeds(config.step2.seed, m, derive_seed),
            "seed_rule": SEED_RULE, "weight_space": WEIGHT_SPACE}


def driver_class(B2: type, config: Any, tf: Any, np: Any, ru: Any) -> type:
    """The class that runs `config`: B2 itself when step2.ensemble == 1 (the predecessor's code
    path, unchanged), else the ensemble subclass."""
    if ensemble_size(config) == 1:
        return B2
    return make_step2_ensemble(B2, tf, np, ru)


def make_step2_ensemble(B2: type, tf: Any, np: Any, ru: Any) -> type:
    """Subclass a B2MultiFold-like class (`phase_b/pet/b2_driver.make_b2_multifold`) with the
    step-2 ensemble. `ru` supplies `derive_seed` and `rec` (the `run_unfold` module)."""

    class Step2EnsembleMultiFold(B2):
        EXECUTES_STEP2_ENSEMBLE = True     # run_unfold.RecipeMultiFold refuses M != 1 otherwise

        def __init__(self, *a: Any, **k: Any) -> None:
            self._s2_member = 0
            super().__init__(*a, **k)
            self.s2_members = ensemble_size(self.config)
            if self.s2_members < 2:
                raise SystemExit("[s2ens] the ensemble driver needs step2.ensemble >= 2")
            self.s2_seeds = member_seeds(self.config.step2.seed, self.s2_members,
                                         ru.derive_seed)
            self._s2_models: list[Any] = [None] * self.s2_members
            self._s2_iteration: dict[str, Any] = {}

        # ---- the member's recipe: the step-2 recipe with the member's seed --------------- #
        def step_recipe(self, stepn: int) -> Any:
            step = super().step_recipe(stepn)
            if stepn == 2 and self._s2_member:
                return dataclasses.replace(step, seed=self.s2_seeds[self._s2_member])
            return step

        @contextlib.contextmanager
        def _member(self, m: int) -> Iterator[None]:
            self._s2_member = m
            original = ru.rec.make_epoch_recorder

            def tagged(*a: Any, context: dict[str, Any], **k: Any) -> Any:
                return original(*a, context={**context, "step2_ensemble_member": m}, **k)

            ru.rec.make_epoch_recorder = tagged
            try:
                yield
            finally:
                ru.rec.make_epoch_recorder = original
                self._s2_member = 0

        # ---- M fits per iteration ---------------------------------------------------------- #
        def RunModel(self, labels: Any, weights: Any, iteration: int, model: Any, stepn: int,
                     NTRAIN: Any = None, cached: bool = False) -> None:
            if stepn != 2:
                super().RunModel(labels, weights, iteration, model, stepn, NTRAIN=NTRAIN,
                                 cached=cached)
                return
            run_seconds, fit_seconds = [], []
            for m in range(self.s2_members):
                with self._member(m):
                    if m:   # member 0's pre-step seed was set by B2's seed_step(2, i)
                        tf.keras.utils.set_random_seed(
                            ru.derive_seed(self.s2_seeds[m], 2, iteration, "pre_step"))
                    self.step2_models = ([] if self._s2_models[m] is None
                                         else [self._s2_models[m]])
                    t0 = time.perf_counter()
                    super().RunModel(labels, weights, iteration, model, stepn, NTRAIN=NTRAIN,
                                     cached=cached)
                    run_seconds.append(time.perf_counter() - t0)
                self._s2_models[m] = self.step2_models[0]
                record = self.fit_records[-1]
                record["step2_ensemble"] = {"member": m, "members": self.s2_members,
                                            "step_seed": self.s2_seeds[m]}
                fit_seconds.append(float(record["fit_seconds"]))
                path = Path(record["weights_path"])
                member_path = path.with_name(f"iter{iteration}_step2_member{m:02d}.weights.h5")
                if path.exists():
                    os.replace(path, member_path)
                record["weights_path"] = str(member_path)
            self.step2_models = list(self._s2_models)
            self._s2_iteration = {"iteration": int(iteration), "members": self.s2_members,
                                  "member_seeds": list(self.s2_seeds),
                                  "fit_seconds": fit_seconds, "run_model_seconds": run_seconds}

        # ---- the push: the mean of the members' weights ------------------------------------ #
        def reweight(self, events: Any, model: Any, batch_size: Any = None) -> Any:
            if model is not self.model2:
                return super().reweight(events, model, batch_size=batch_size)
            members = list(self.step2_models)
            if len(members) != self.s2_members or any(x is None for x in members):
                raise SystemExit(f"[s2ens] {len(members)} step-2 models, expected "
                                 f"{self.s2_members}")
            per_member, seconds = [], []
            try:
                for member in members:
                    self.step2_models = [member]
                    t0 = time.perf_counter()
                    per_member.append(super().reweight(events, model, batch_size=batch_size))
                    seconds.append(time.perf_counter() - t0)
            finally:
                self.step2_models = members
            self._s2_iteration["predict_seconds"] = seconds
            self._s2_iteration["spread_on_pass_gen"] = spread_record(
                np, per_member, np.asarray(self.mc.pass_gen, bool))
            return average_member_weights(np, per_member)

        # ---- persistence ------------------------------------------------------------------- #
        def _save_iteration(self, i: int, seconds: float) -> None:
            blobs = {}
            for m in range(1, self.s2_members):
                for j, w in enumerate(self._s2_models[m].get_weights()):
                    blobs[f"m{m:02d}_{j:04d}"] = w
            np.savez(self.state_dir / MEMBERS_FILE.format(i=i), **blobs)  # before state.json
            if self._s2_iteration.get("iteration") == i:
                self.iteration_records[-1]["step2_ensemble"] = dict(self._s2_iteration)
            super()._save_iteration(i, seconds)

        def _restore(self) -> int:
            start = super()._restore()
            self._s2_models = [None] * self.s2_members
            if start == 0:
                return 0
            k = start - 1
            path = self.state_dir / MEMBERS_FILE.format(i=k)
            if not path.exists():
                raise SystemExit(f"[s2ens] {path} is missing; refusing to resume an ensemble")
            self._s2_models[0] = self.step2_models[0]
            with np.load(path) as blob:
                expected = {f"m{m:02d}" for m in range(1, self.s2_members)}
                found = {n.split("_")[0] for n in blob.files}
                if found != expected:
                    raise SystemExit(f"[s2ens] {path} holds members {sorted(found)}, expected "
                                     f"{sorted(expected)}")
                for m in range(1, self.s2_members):
                    tf.keras.utils.set_random_seed(
                        ru.derive_seed(self.s2_seeds[m], 2, "init", 0))
                    member = self.factories[2]()
                    names = sorted(n for n in blob.files if n.startswith(f"m{m:02d}_"))
                    member.set_weights([blob[n] for n in names])
                    self._s2_models[m] = member
            self.step2_models = list(self._s2_models)
            return start

    return Step2EnsembleMultiFold
