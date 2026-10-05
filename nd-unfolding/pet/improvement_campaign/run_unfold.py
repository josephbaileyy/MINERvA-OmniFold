"""Campaign driver: OmniFold with an explicit, verified recipe for EACH step.

Reuses the engine (`omnifold_nn/omnifold/omnifold.py`) by subclassing, without editing it:
`RunStep1` / `RunStep2` (dual-leg weights, pass masks, pull/push logic) and `reweight` (the
logit-space push with its predeclared cap) are the engine's own. Only `Unfold` and `RunModel`
are replaced, because those are where the engine imposed one batch size, one learning rate, its
own Adam, a batch-dependent validation cut, a global-RNG split and an inert stopping rule
(`phase_a/INTENDED_VS_EXECUTED-20260922.md`). Here each step's `StepRecipe` decides:

* optimizer family and hyper-parameters, within-fit schedule, clipping, rate across iterations;
* batch size (per step), epochs, patience, and which weights leave the fit (`last` / `best`);
* the validation split (its own seeded generator; event-level for step 2);
* initialization (scratch / pretrained, warm start / re-initialize across iterations);
* the seeds for model construction and shuffling, derived per (step, iteration), so a step's
  realization does not depend on what the other step consumed.

After compiling, the EXECUTED optimizer (`model.optimizer`) is checked against the recipe and the
run refuses to train on a mismatch; during training `recorder.py` measures updates, examples,
batch, learning rate, gradient norms and weight tails per epoch and refuses a fit whose executed
epoch differs from the recipe.

CLI: `run_unfold.py --config <RunConfig json> --repo <this checkout> --out <dir> ...`.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import authorization_scope as scope  # noqa: E402
import feature_arms  # noqa: E402
import recorder as rec  # noqa: E402
from recipe import RunConfig, StepRecipe  # noqa: E402


def derive_seed(*parts: Any) -> int:
    return int.from_bytes(hashlib.sha256(repr(parts).encode()).digest()[:4], "big") % (2 ** 31)


# ---------------------------------------------------------------------------------------------- #
# Optimizer from a recipe, and the check that the executed one is that optimizer
# ---------------------------------------------------------------------------------------------- #
def build_optimizer(tf: Any, step: StepRecipe, iteration: int, total_steps: int,
                    training_recipe: Any = None, torch_adamw: Any = None
                    ) -> tuple[Any, dict[str, Any], Callable[[Any], Any]]:
    """(optimizer, declared facts, lr_at(step_indices))."""
    base = step.iteration_lr.base_rate(step.optimizer.learning_rate, iteration)
    declared = {"family": step.optimizer.family, "base_learning_rate": base,
                "schedule": step.schedule.kind, "clipping": step.clipping.kind,
                "max_norm": step.clipping.max_norm, "weight_decay": step.optimizer.weight_decay,
                "beta_1": step.optimizer.beta_1, "beta_2": step.optimizer.beta_2,
                "epsilon": step.optimizer.epsilon, "total_steps": int(total_steps)}
    if step.schedule.kind == "warmup_cosine":
        warmup = max(1, int(round(step.schedule.warmup_fraction * total_steps)))
        if warmup >= total_steps:
            raise ValueError(f"warmup {warmup} does not fit in {total_steps} steps")
        lr = training_recipe.WarmupCosine(base, warmup, total_steps)
        declared["warmup_steps"] = warmup

        def lr_at(steps: Any) -> Any:
            return lr(tf.constant(steps, tf.float64)).numpy()
    else:
        lr = base

        def lr_at(steps: Any) -> Any:
            import numpy as np
            return np.full(len(steps), base)
    opt = step.optimizer
    keras_clip = step.clipping.max_norm if step.clipping.kind == "global_norm" else None
    if opt.family == "adam":
        optimizer = tf.keras.optimizers.Adam(learning_rate=lr, beta_1=opt.beta_1,
                                             beta_2=opt.beta_2, epsilon=opt.epsilon,
                                             global_clipnorm=keras_clip)
    elif opt.family == "adamw":
        optimizer = tf.keras.optimizers.AdamW(learning_rate=lr, weight_decay=opt.weight_decay,
                                              beta_1=opt.beta_1, beta_2=opt.beta_2,
                                              epsilon=opt.epsilon, global_clipnorm=keras_clip)
    elif step.clipping.kind == "global_norm_torch":
        optimizer = training_recipe.ClippedTorchAdamW(
            grad_clip=step.clipping.max_norm, learning_rate=lr,
            weight_decay=opt.weight_decay, beta_1=opt.beta_1, beta_2=opt.beta_2,
            epsilon=opt.epsilon)
    else:
        optimizer = torch_adamw.TorchAdamW(learning_rate=lr, weight_decay=opt.weight_decay,
                                           beta_1=opt.beta_1, beta_2=opt.beta_2,
                                           epsilon=opt.epsilon)
    return optimizer, declared, lr_at


def executed_optimizer_facts(tf: Any, optimizer: Any) -> dict[str, Any]:
    lr = optimizer.learning_rate if not hasattr(optimizer, "_learning_rate") else \
        optimizer._learning_rate
    schedule = isinstance(lr, tf.keras.optimizers.schedules.LearningRateSchedule)
    return {
        "class": type(optimizer).__qualname__, "module": type(optimizer).__module__,
        "schedule_class": type(lr).__qualname__ if schedule else None,
        "base_learning_rate": (float(lr.base_learning_rate) if schedule and
                               hasattr(lr, "base_learning_rate") else
                               None if schedule else float(tf.keras.backend.get_value(lr))),
        "warmup_steps": getattr(lr, "warmup_steps", None),
        "max_steps": getattr(lr, "max_steps", None),
        "keras_weight_decay": getattr(optimizer, "weight_decay", None),
        "torch_weight_decay": getattr(optimizer, "torch_weight_decay", None),
        "global_clipnorm": getattr(optimizer, "global_clipnorm", None),
        "clipnorm": getattr(optimizer, "clipnorm", None),
        "torch_grad_clip": getattr(optimizer, "grad_clip", None),
        "beta_1": float(getattr(optimizer, "beta_1", float("nan"))),
        "beta_2": float(getattr(optimizer, "beta_2", float("nan"))),
        "epsilon": float(getattr(optimizer, "epsilon", float("nan"))),
        "iterations": int(optimizer.iterations.numpy()),
        "is_horovod_wrapped": "horovod" in type(optimizer).__module__,
    }


EXPECTED_CLASS = {"adam": "Adam", "adamw": "AdamW", "torch_adamw": "TorchAdamW"}


def verify_executed_optimizer(executed: dict[str, Any], declared: dict[str, Any]) -> list[str]:
    """Differences between the optimizer the model will train with and the recipe."""
    problems = []
    want_class = ("ClippedTorchAdamW" if declared["clipping"] == "global_norm_torch"
                  else EXPECTED_CLASS[declared["family"]])
    if executed["class"] != want_class:
        problems.append(f"class {executed['class']} != {want_class}")
    if executed["is_horovod_wrapped"]:
        problems.append("optimizer is Horovod-wrapped")
    if executed["iterations"] != 0:
        problems.append(f"optimizer carries state: iterations={executed['iterations']}")
    if not math.isclose(executed["base_learning_rate"] or -1, declared["base_learning_rate"],
                        rel_tol=1e-6):
        problems.append(f"learning rate {executed['base_learning_rate']} != "
                        f"{declared['base_learning_rate']}")
    if (executed["schedule_class"] is not None) != (declared["schedule"] != "constant"):
        problems.append(f"schedule {executed['schedule_class']} vs {declared['schedule']}")
    if declared["schedule"] == "warmup_cosine" and (
            executed["warmup_steps"] != declared["warmup_steps"] or
            executed["max_steps"] != declared["total_steps"]):
        problems.append("warmup/cosine steps differ from the recipe")
    wd = (executed["torch_weight_decay"] if declared["family"] == "torch_adamw"
          else executed["keras_weight_decay"] or 0.0)
    if not math.isclose(float(wd or 0.0), declared["weight_decay"], abs_tol=1e-12):
        problems.append(f"weight decay {wd} != {declared['weight_decay']}")
    clip = {"none": None, "global_norm": executed["global_clipnorm"],
            "global_norm_torch": executed["torch_grad_clip"]}[declared["clipping"]]
    if declared["clipping"] == "none":
        if executed["global_clipnorm"] or executed["clipnorm"] or executed["torch_grad_clip"]:
            problems.append("clipping present but the recipe declares none")
    elif clip is None or not math.isclose(float(clip), declared["max_norm"]):
        problems.append(f"clip {clip} != {declared['max_norm']}")
    for key in ("beta_1", "beta_2", "epsilon"):
        if not math.isclose(executed[key], declared[key], rel_tol=1e-6):
            problems.append(f"{key} {executed[key]} != {declared[key]}")
    return problems


# ---------------------------------------------------------------------------------------------- #
# The engine subclass
# ---------------------------------------------------------------------------------------------- #
class _StepToken:
    """Stands in for the engine's template model: `reweight` only compares it by identity."""

    def __init__(self, step: int) -> None:
        self.step = step


def make_recipe_multifold(MultiFold: type, tf: Any, np: Any) -> type:
    """Build the recipe-driven subclass (the engine is importable only with TensorFlow)."""

    class RecipeMultiFold(MultiFold):
        def __init__(self, name: str, *, config: RunConfig, factories: dict[int, Callable],
                     data: Any, mc: Any, out_dir: Path,
                     pretrained_check: Callable[[Any], dict[str, Any]] | None = None,
                     training_recipe: Any = None, torch_adamw: Any = None,
                     probe_rows: int = 50_000, verbose: bool = False) -> None:
            config.validate()
            self.config = config
            self.factories = factories
            self.out_dir = Path(out_dir)
            self.out_dir.mkdir(parents=True, exist_ok=True)
            self.sink = self.out_dir / "epochs.jsonl"
            self.pretrained_check = pretrained_check
            self.training_recipe, self.torch_adamw = training_recipe, torch_adamw
            self.probe_rows = int(probe_rows)
            self.fit_records: list[dict[str, Any]] = []
            self._split_cache: dict[int, Any] = {}
            super().__init__(name, _StepToken(1), _StepToken(2), data, mc,
                             weights_folder=str(self.out_dir / "weights"),
                             log_folder=str(self.out_dir), niter=config.iterations,
                             batch_size=config.step1.batch_size,
                             epochs=config.step1.stopping.max_epochs,
                             lr=config.step1.optimizer.learning_rate, verbose=verbose)
            # Per-step counts replace the engine's single-batch ones (they are only logged).
            self.num_steps_reco = int(self.mc.nmax + self.data.nmax) // config.step1.batch_size
            self.num_steps_gen = 2 * int(self.mc.nmax) // config.step2.batch_size
            self.log_string(f"[recipe] step1 batch {config.step1.batch_size}, step2 batch "
                            f"{config.step2.batch_size}; config {config.content_hash()}")

        def step_recipe(self, stepn: int) -> StepRecipe:
            return self.config.step1 if stepn == 1 else self.config.step2

        # ---- the loop: the engine's RunStep1/RunStep2, no template compiles -------------- #
        def Unfold(self) -> None:
            self.step1_models, self.step2_models = [], []
            self.mc_weight_reco = getattr(self.mc, "weight_reco", None)
            if self.mc_weight_reco is None:
                self.mc_weight_reco = self.mc.weight
            self.weights_pull = np.ones(self.mc.weight.shape[0], dtype=np.float32)
            self.weights_push = np.ones(self.mc.weight.shape[0], dtype=np.float32)
            self.iteration_records = []
            for i in range(self.niter):
                self.log_string(f"ITERATION: {i + 1}")
                self.RunStep1(i)
                self.RunStep2(i)
                self.iteration_records.append({
                    "iteration": i,
                    "pull": rec.weight_stats(np, self.weights_pull),
                    "push": rec.weight_stats(np, self.weights_push)})

        def reweight(self, events: Any, model: Any, batch_size: Any = None) -> Any:
            step = self.step_recipe(1 if model is self.model1 else 2)
            return super().reweight(events, model, batch_size=step.predict_batch_size)

        # ---- one fit, entirely from the step's recipe ------------------------------------ #
        def _inputs(self, stepn: int) -> tuple[Any, Any]:
            if stepn == 1:
                return (np.concatenate([self.mc.reco, self.data.reco], 0),
                        np.concatenate([self.mc.reco_evt, self.data.reco_evt], 0))
            return (np.concatenate([self.mc.gen, self.mc.gen], 0),
                    np.concatenate([self.mc.gen_evt, self.mc.gen_evt], 0))

        def _split(self, stepn: int, n_rows: int, iteration: int) -> tuple[Any, Any]:
            spec = self.step_recipe(stepn).validation
            key = stepn if spec.fixed_across_iterations else (stepn, iteration)
            if key in self._split_cache:
                return self._split_cache[key]
            rng = np.random.default_rng(derive_seed(spec.seed, stepn, "split",
                                                    None if spec.fixed_across_iterations
                                                    else iteration))
            if stepn == 2 and spec.unit == "event":
                n_events = n_rows // 2
                order = rng.permutation(n_events)
                n_val = int(round(spec.fraction * n_events))
                val_ev, train_ev = order[:n_val], order[n_val:]
                val = np.concatenate([val_ev, val_ev + n_events])
                train = np.concatenate([train_ev, train_ev + n_events])
            else:
                order = rng.permutation(n_rows)
                n_val = int(round(spec.fraction * n_rows))
                val, train = order[:n_val], order[n_val:]
            self._split_cache[key] = (np.sort(train), np.sort(val))
            return self._split_cache[key]

        def RunModel(self, labels: Any, weights: Any, iteration: int, model: Any, stepn: int,
                     NTRAIN: Any = None, cached: bool = False) -> None:
            step = self.step_recipe(stepn)
            cloud, evt = self._inputs(stepn)
            train, val = self._split(stepn, len(labels), iteration)
            y = np.stack([labels, weights], axis=1).astype(np.float32)
            b = step.batch_size
            train_ds = (tf.data.Dataset.from_tensor_slices(((cloud[train], evt[train]), y[train]))
                        .shuffle(len(train), seed=derive_seed(step.seed, stepn, iteration,
                                                             "shuffle"),
                                 reshuffle_each_iteration=True)
                        .batch(b).prefetch(tf.data.AUTOTUNE))
            val_ds = (tf.data.Dataset.from_tensor_slices(((cloud[val], evt[val]), y[val]))
                      .batch(b).prefetch(tf.data.AUTOTUNE))
            models = self.step1_models if stepn == 1 else self.step2_models
            fresh = (iteration == 0 or step.init.across_iterations == "reinitialize"
                     or not models)
            if fresh:
                tf.keras.utils.set_random_seed(derive_seed(step.seed, stepn, "init",
                                                           iteration if iteration and
                                                           step.init.across_iterations ==
                                                           "reinitialize" else 0))
                model_e = self.factories[stepn]()
                models[:] = [model_e]
            else:
                model_e = models[0]
            per_epoch = math.ceil(len(train) / b)
            optimizer, declared, lr_at = build_optimizer(
                tf, step, iteration, step.stopping.max_epochs * per_epoch,
                self.training_recipe, self.torch_adamw)
            from omnifold.net import weighted_binary_crossentropy
            model_e.compile(optimizer=optimizer, loss=weighted_binary_crossentropy,
                            weighted_metrics=[])
            executed = executed_optimizer_facts(tf, model_e.optimizer)
            problems = verify_executed_optimizer(executed, declared)
            if problems:
                raise RuntimeError(f"[recipe] step {stepn} iteration {iteration}: the executed "
                                   f"optimizer is not the declared one: {problems}")
            tf.keras.utils.set_random_seed(derive_seed(step.seed, stepn, iteration, "fit"))
            probe = None
            if self.probe_rows:
                lab0 = val[(labels[val] == 0) & (weights[val] > 0)][: self.probe_rows]
                probe = ((cloud[lab0], evt[lab0]), weights[lab0])
            context = {"iteration": int(iteration), "step": int(stepn),
                       "config_hash": self.config.content_hash()}
            recorder = rec.make_epoch_recorder(
                tf, np, context=context, sink=self.sink,
                expectation=rec.FitExpectation(len(train), b), stopping=step.stopping,
                lr_at=lr_at, probe=probe,
                pretrained_check=(self.pretrained_check if (fresh and stepn == 1 and
                                                            step.init.policy == "pretrained")
                                  else None))
            t0 = time.perf_counter()
            history = model_e.fit(train_ds, epochs=step.stopping.max_epochs,
                                  validation_data=val_ds, verbose=0, callbacks=[recorder])
            seconds = time.perf_counter() - t0
            weights_path = self.out_dir / "weights" / f"iter{iteration}_step{stepn}.weights.h5"
            model_e.save_weights(str(weights_path))
            self.fit_records.append({
                **context, "declared_optimizer": declared, "executed_optimizer": executed,
                "model_class": type(model_e).__qualname__, "fresh_model": fresh,
                "train_rows": int(len(train)), "validation_rows": int(len(val)),
                "validation_digest": hashlib.sha256(np.asarray(val, np.int64).tobytes())
                .hexdigest(),
                "batch_size": b, "updates_per_epoch": per_epoch,
                "fit_seconds": seconds, "history": {k: [float(v) for v in vals]
                                                    for k, vals in history.history.items()},
                "recorder": recorder.summary, "weights_path": str(weights_path)})

    return RecipeMultiFold


# ---------------------------------------------------------------------------------------------- #
# Pretrained-state helpers
# ---------------------------------------------------------------------------------------------- #
def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pretrained_checker(state_npz: Path) -> Callable[[Any], dict[str, Any]]:
    """Compare every exported tensor with the model's live variable, by name."""
    import numpy as np
    with np.load(str(state_npz)) as blob:
        arrays = {name: blob[name] for name in blob.files}

    def check(model: Any) -> dict[str, Any]:
        import pet2_keras_port as port
        inventory = dict(port.parameter_inventory(model.backbone))
        compared = exact = 0
        worst = 0.0
        for name, variable in inventory.items():
            if name not in arrays:
                continue
            live = variable.numpy()
            diff = (float(np.max(np.abs(live - arrays[name].astype(live.dtype))))
                    if live.size else 0.0)
            compared += 1
            exact += int(diff == 0.0)
            worst = max(worst, diff)
        return {"compared": compared, "exactly_equal": exact, "tensors_in_state": len(arrays),
                "tensors_in_model": len(inventory), "worst_abs_difference": worst,
                "all_equal_to_pretrained": compared == len(arrays) == exact}

    return check


# ---------------------------------------------------------------------------------------------- #
# Model factories
# ---------------------------------------------------------------------------------------------- #
def model_factories(config: RunConfig, mods: dict[str, Any], inputs: Any
                    ) -> tuple[dict[int, Callable], Callable | None]:
    PET = mods["net"].PET
    meta = inputs.meta
    s1, s2 = config.model_step1, config.model_step2

    def ours_step1() -> Any:
        return PET(int(inputs.mc["reco"].shape[-1]), num_evt=int(inputs.mc["reco_evt"].shape[1]),
                   num_part=int(inputs.mc["reco"].shape[1]), coord_idx=meta["coord_reco"],
                   **s1.kwargs())

    def step2() -> Any:
        return PET(int(inputs.mc["gen"].shape[-1]), num_evt=int(inputs.mc["gen_evt"].shape[1]),
                   num_part=int(inputs.mc["gen"].shape[1]), coord_idx=meta["coord_gen"],
                   **s2.kwargs())

    check = None
    if s1.kind == "theirs_pet2_small":
        import theirs_omnifold_arm as toa
        init = config.step1.init
        pretrained = init.policy == "pretrained"
        if pretrained:
            got = sha256_of(Path(init.pretrained_state))
            if got != init.pretrained_state_sha256:
                raise SystemExit(f"[recipe] pretrained state sha256 {got} != declared")

        def theirs_step1() -> Any:
            return toa.TheirsCompleteArm(
                num_part=int(inputs.mc["reco"].shape[1]), **s1.kwargs(),
                state_npz=init.pretrained_state if pretrained else None,
                manifest=init.pretrained_manifest if pretrained else None)
        factories = {1: theirs_step1, 2: step2}
        if pretrained:
            check = pretrained_checker(Path(init.pretrained_state))
    else:
        factories = {1: ours_step1, 2: step2}
    return factories, check


# ---------------------------------------------------------------------------------------------- #
# CLI
# ---------------------------------------------------------------------------------------------- #
def _load_numpy_probe() -> Any:
    spec = importlib.util.spec_from_file_location("numpy_probe",
                                                  HERE / "phase_a" / "numpy_probe.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.disable_numpy_sve_probe()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--inputs-npz", type=Path, required=True)
    parser.add_argument("--identity-sidecar", type=Path, required=True)
    parser.add_argument("--theirs-index", type=Path, default=None)
    parser.add_argument("--theirs-cache", type=Path, default=None)
    parser.add_argument("--probe-rows", type=int, default=50_000)
    parser.add_argument("--reference-digests", type=Path, default=None,
                        help="runtime_audit_<arm>.json of the historical driver on the same "
                             "events: the input arrays must match it")
    args = parser.parse_args()

    out = scope.refuse_historical_output(args.out)
    out.mkdir(parents=True, exist_ok=True)
    config = RunConfig.from_json(args.config.read_text())
    arm_spec = feature_arms.get(config.feature_arm)
    scope.refuse_real_data_inputs(
        bkg_mode="mc-only", measured_leg_is_real=False,
        npz_keys_read=[f"{w}_scalars" for w in ("reco", "truth")],
        input_paths=[p for p in (args.inputs_npz, args.theirs_index, args.theirs_cache) if p])
    started = time.perf_counter()
    probe_record = _load_numpy_probe()

    import numpy as np
    import closure_data as cd
    mods = cd.import_historical(args.repo)
    import tensorflow as tf
    import training_recipe
    import torch_adamw
    if mods["omnifold"].REWEIGHT_LOGIT_CAP != rec.REWEIGHT_LOGIT_CAP:
        raise SystemExit("[recipe] the recorder's logit cap differs from the engine's")
    rec.install_counters(tf, next(k for k in tf.keras.optimizers.Adam.__mro__
                                  if "_clip_gradients" in vars(k)))

    inputs = cd.build_closure_inputs(
        mods, np, arm=config.arm, events=config.events, endpoint=config.endpoint,
        inputs_npz=args.inputs_npz, identity_sidecar=args.identity_sidecar,
        theirs_index=args.theirs_index, theirs_cache=args.theirs_cache)
    digests_before_arm = inputs.digests(np)
    reference = None
    if args.reference_digests is not None:
        audit = json.loads(args.reference_digests.read_text())["inputs"]
        reference = {"step1_cloud": audit["step1"]["cloud_digest"],
                     "step1_event": audit["step1"]["event_digest"],
                     "step2_cloud": audit["step2"]["cloud_digest"],
                     "step2_event": audit["step2"]["event_digest"]}
        if reference != digests_before_arm:
            raise SystemExit(f"[recipe] inputs differ from the historical driver's: "
                             f"{digests_before_arm} vs {reference}")
    blocks = feature_arms.apply(
        arm_spec, config.arm,
        {"pdata_reco_evt": inputs.pdata["reco_evt"], "mc_reco_evt": inputs.mc["reco_evt"],
         "mc_gen_evt": inputs.mc["gen_evt"], "pdata_rows": inputs.pdata["rows"],
         "mc_rows": inputs.mc["rows"],
         "pdata_pass_reco": np.ones(len(inputs.pdata["rows"]), bool),
         "mc_pass_reco": inputs.mc["pass_reco"], "mc_pass_gen": inputs.mc["pass_gen"]},
        lambda which, col, rows: cd.read_scalar_column(np, mods["ffd"], args.inputs_npz,
                                                        which, col, rows), np)
    inputs.pdata["reco_evt"] = blocks["pdata_reco_evt"]
    inputs.mc["reco_evt"] = blocks["mc_reco_evt"]
    inputs.mc["gen_evt"] = blocks["mc_gen_evt"]
    pdata, mcb = cd.make_loaders(mods, np, inputs)
    factories, check = model_factories(config, mods, inputs)

    Recipe = make_recipe_multifold(mods["omnifold"].MultiFold, tf, np)
    unfolder = Recipe(config.name, config=config, factories=factories, data=pdata, mc=mcb,
                      out_dir=out, pretrained_check=check, training_recipe=training_recipe,
                      torch_adamw=torch_adamw, probe_rows=args.probe_rows)
    unfolder.Unfold()
    push = np.asarray(unfolder.weights_push, dtype=np.float64)
    weights_file = out / f"weights_{config.arm}_{config.name}.npz"
    np.savez_compressed(weights_file, weights=push, dump_rows_a=inputs.meta["dump_rows_a"],
                        dump_rows_b=inputs.meta["dump_rows_b"], tilt_a=inputs.meta["tilt_a"],
                        pass_gen_a=inputs.meta["pass_gen_a"], pass_gen_b=inputs.mc["pass_gen"],
                        mc_indices=inputs.meta["mc_indices"])
    commit = subprocess.run(["git", "-C", str(args.repo), "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    receipt = {
        "schema": "pet-improvement-run-receipt-v1", "config": config.to_dict(),
        "config_hash": config.content_hash(), "feature_arm": config.feature_arm,
        "feature_arm_hash": arm_spec.content_hash(),
        "feature_columns_added": blocks["added_columns"], "code_commit": commit,
        "inputs_npz": str(args.inputs_npz), "input_digests": digests_before_arm,
        "input_digests_match_historical_driver": (None if reference is None else True),
        "numpy_sve_probe": probe_record, "precision_policy": mods["precision_policy"],
        "sys_path_entries_removed": mods["sys_path_entries_removed"],
        "closure": {k: v for k, v in inputs.meta.items()
                    if k not in ("dump_rows_a", "dump_rows_b", "tilt_a", "pass_gen_a",
                                 "mc_indices")},
        "fits": unfolder.fit_records, "iterations": unfolder.iteration_records,
        "weights_path": str(weights_file), "weights_finite": bool(np.isfinite(push).all()),
        "seconds": time.perf_counter() - started,
        "measured_leg_is_real_data": False, "scored_here": False}
    (out / "receipt.json").write_text(json.dumps(receipt, indent=1, default=repr) + "\n")
    print(json.dumps({"receipt": str(out / "receipt.json"), "seconds": receipt["seconds"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
