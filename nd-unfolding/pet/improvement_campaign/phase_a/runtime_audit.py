"""Level-1 evidence: OBSERVE the historical training path while it executes.

Task A1 Part 1 requires runtime capture, and requires the code under observation to
be the historical commit's, unmodified. This harness satisfies both without editing
a single historical file:

* **The binding to the commit is measured, not assumed.** `verify_historical_modules`
  compares the git blob id of every file on the training path against that path's
  blob at `HISTORICAL_COMMIT`, and refuses to run on a mismatch. A checkout pinned
  by `git rev-parse HEAD` proves what the tree's HEAD is; this proves what the
  interpreter is about to import, which is the stronger statement and the one
  `OI-136` exists because of.

* **The instrumentation is a subclass installed on the module object**, not a patch
  to a file. `run_arm_evaluation.evaluate` resolves `from omnifold.omnifold import
  MultiFold` INSIDE the function body, at call time, so rebinding that attribute
  before calling `evaluate` reaches it; `annealed_estimator.make_annealed_multifold`
  then subclasses the instrumented class and the MRO is
  `_AnnealedMultiFold -> _Instrumented -> MultiFold`. Every observation is therefore
  taken from the object the engine actually built, after the engine built it.

WHAT IS OBSERVED, AND WHERE EACH OBSERVATION IS TAKEN
-----------------------------------------------------
`_Instrumented.CompileModel`
    Runs after `super().CompileModel`, so `model.optimizer` is the compiled
    optimizer. Records its class, the FILE that class was loaded from, its full
    `get_config()`, and explicit probes for `weight_decay`, `clipnorm`,
    `global_clipnorm` and `clipvalue` -- the four fields hypothesis A's intended
    recipe names and a `get_config()` reader could skip. Also records the effective
    `fixed` flag it was called with, which is what the annealed subclass overrides.

`_Instrumented.RunModel`
    Records the engine's own per-fit scalars (`BATCH_SIZE`, `EPOCHS`, `patience`,
    `train_frac`, `num_steps_reco`, `num_steps_gen`) and a digest of the numpy RNG
    state at entry, so RNG consumption can be compared across arms.

the `fit` wrapper
    Installed on the clone the engine is about to train. Records the keyword
    arguments the engine passes -- `epochs`, `steps_per_epoch`, `validation_steps`
    -- rather than recomputing them from the engine's formula, because recomputing
    is a second implementation of the thing under test. Also records the engine's
    own callback list (class, file, and the attributes that decide stopping), and
    the FIRST BATCH of the dataset handed to `fit`, which is the only place the
    arrays that actually reach the model can be inspected.

`_FitRecorder`
    A Keras callback appended to (never replacing) the engine's callbacks. Per
    epoch it reads `optimizer.learning_rate` and `optimizer.iterations` -- the
    authoritative count of optimizer updates applied -- and the logs. At
    `on_train_begin` it digests the clone's weights and compares them
    VARIABLE BY VARIABLE against the pre-clone model, which is the measurement
    that decides whether pretrained state survives `tf.keras.models.clone_model`.
    At `on_train_end` it reads the engine's `EarlyStopping` instance for
    `stopped_epoch` and `wait`, so "the rule never fired" is measured rather than
    argued from `patience > epochs`.

WHAT THIS HARNESS DELIBERATELY DOES NOT DO
------------------------------------------
It does not score, compare arms on recovery, or write anywhere near the historical
output directory. It takes one extra batch from each training dataset for the input
stats; that creates an independent tf.data iterator and does not rebind the one
`fit` consumes, but it is recorded in the receipt because an audit that perturbs
its subject must say so. Nothing here is a verdict: the receipt is a transcription
of observed fields, and the intended-versus-executed judgement is made in
`INTENDED_VS_EXECUTED-20260922.md` against it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# The commit the report names. The training path is byte-identical at the commit
# the tuning stage ran from (395f296d) and the one the pilot/final ran from
# (33a3f264); see INTENDED_VS_EXECUTED-20260922.md for that diff.
HISTORICAL_COMMIT = "68cf9d29f8ab1b0f5acd933d4baec1962b29e34d"

# Every file whose content decides what the training path does. A mismatch on any
# of them means this process is not observing the historical configuration.
AUDITED_MODULES = (
    "omnifold_nn/omnifold/omnifold.py",
    "omnifold_nn/omnifold/net.py",
    "omnifold_nn/omnifold/dataloader.py",
    "nd-unfolding/pet/annealed_estimator.py",
    "nd-unfolding/pet/fullevent_fps_dataloader.py",
    "nd-unfolding/pet/closure_powered_truth_reweight.py",
    "nd-unfolding/pet/configuration_comparison/run_arm_evaluation.py",
    "nd-unfolding/pet/configuration_comparison/frozen_design.py",
    "nd-unfolding/pet/configuration_comparison/training_recipe.py",
    "nd-unfolding/pet/configuration_comparison/theirs_omnifold_arm.py",
    "nd-unfolding/pet/configuration_comparison/theirs_token_schema.py",
    "nd-unfolding/pet/configuration_comparison/theirs_loader_substitution.py",
    "nd-unfolding/pet/configuration_comparison/pretrained_init.py",
    "nd-unfolding/pet/configuration_comparison/stage_splits.py",
    "nd-unfolding/pet/configuration_comparison/keras_backend.py",
    "nd-unfolding/pet/configuration_comparison/materialize_theirs.py",
    "nd-unfolding/pet/configuration_comparison/prematerialize_theirs.py",
)

# Attributes that decide a callback's behaviour. Read off the INSTANCE the engine
# constructed, so a default the driver never passed is visible as the value used.
CALLBACK_FIELDS = ("patience", "monitor", "restore_best_weights", "mode",
                   "min_lr", "factor", "cooldown", "save_best_only",
                   "save_weights_only", "min_delta", "baseline", "start_from_epoch")

# The optimizer fields hypothesis A's intended recipe names. Probed explicitly
# because `get_config()` omits a key on some Keras lineages and an absent key
# reads the same as an absent feature.
OPTIMIZER_PROBES = ("learning_rate", "weight_decay", "clipnorm", "global_clipnorm",
                    "clipvalue", "use_ema", "beta_1", "beta_2", "epsilon", "amsgrad")


def _git(repo: Path, *args: str) -> str:
    """One git command in `repo`, stdout stripped. Raises on non-zero exit."""
    done = subprocess.run(("git", "-C", str(repo)) + args,
                          check=True, capture_output=True, text=True)
    return done.stdout.strip()


def sha256_of(path: Path) -> str:
    """Hex digest of a file's bytes, for citation outside git."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_historical_modules(repo: Path, commit: str = HISTORICAL_COMMIT,
                              ) -> dict[str, Any]:
    """Refuse unless every training-path file is byte-identical to `commit`.

    Compares git blob ids: equal blob id IS byte-identity, with no tolerance to
    argue about. `git hash-object` is applied to the WORKTREE file rather than the
    index, because the index can hold a staged version the interpreter will never
    read -- and in a shared checkout it frequently does.
    """
    resolved = _git(repo, "rev-parse", commit)
    files: dict[str, Any] = {}
    mismatched: list[str] = []
    for rel in AUDITED_MODULES:
        path = repo / rel
        if not path.is_file():
            mismatched.append(rel)
            files[rel] = {"present": False}
            continue
        at_commit = _git(repo, "rev-parse", f"{commit}:{rel}")
        in_worktree = _git(repo, "hash-object", str(path))
        match = at_commit == in_worktree
        if not match:
            mismatched.append(rel)
        files[rel] = {
            "present": True,
            "blob_at_commit": at_commit,
            "blob_in_worktree": in_worktree,
            "identical": match,
            "sha256": sha256_of(path),
        }
    if mismatched:
        raise SystemExit(
            f"[audit] refusing to run: {mismatched} differ from {commit[:8]} "
            "or are absent. This process would observe a training path that is "
            "not the historical one, and its receipt would say otherwise.")
    return {"commit": commit, "commit_resolved": resolved,
            "files": files, "all_identical": True}


def _digest_weights(weights: list[Any]) -> dict[str, Any]:
    """A whole-model digest plus per-tensor digests, from numpy arrays.

    Per-tensor digests are what make the clone comparison answerable: a single
    whole-model digest can only say "different", while the per-tensor list says
    HOW MANY tensors changed, which distinguishes "cloning reset everything" from
    "one head was re-initialised".
    """
    import numpy as np

    whole = hashlib.sha256()
    each: list[dict[str, Any]] = []
    for index, array in enumerate(weights):
        arr = np.ascontiguousarray(np.asarray(array))
        one = hashlib.sha256(arr.tobytes()).hexdigest()
        whole.update(one.encode())
        each.append({"index": index, "shape": list(arr.shape),
                     "dtype": str(arr.dtype), "sha256": one,
                     "size": int(arr.size)})
    return {"model_sha256": whole.hexdigest(), "tensor_count": len(each),
            "tensors": each}


def _compare_weight_sets(before: dict[str, Any], after: dict[str, Any],
                         ) -> dict[str, Any]:
    """How many tensors the clone kept, positionally, from the pre-clone model."""
    pairs = list(zip(before["tensors"], after["tensors"]))
    same = [p for p in pairs if p[0]["sha256"] == p[1]["sha256"]]
    # A shape change would make the positional comparison meaningless, so it is
    # reported rather than folded into the identical/changed split.
    reshaped = [p[0]["index"] for p in pairs if p[0]["shape"] != p[1]["shape"]]
    return {
        "tensors_compared": len(pairs),
        "tensors_identical": len(same),
        "tensors_changed": len(pairs) - len(same),
        "fraction_identical": (len(same) / len(pairs)) if pairs else None,
        "shape_mismatches": reshaped,
        "count_before": before["tensor_count"],
        "count_after": after["tensor_count"],
    }


def _tensor_stats(np: Any, array: Any, name: str) -> dict[str, Any]:
    """Scale and finiteness of one array reaching the model, per last-axis feature.

    The per-feature split is the point. `eta/phi/log-pT/log-E` and raw millimetre
    momenta differ by four orders of magnitude in ONE column, and a whole-array
    min/max hides which column that is.
    """
    arr = np.asarray(array, dtype=np.float64)
    finite = np.isfinite(arr)
    flat_nonzero = arr[finite & (arr != 0.0)]
    per_feature: list[dict[str, Any]] = []
    if arr.ndim >= 2:
        moved = arr.reshape(-1, arr.shape[-1])
        for feature in range(moved.shape[-1]):
            column = moved[:, feature]
            keep = column[np.isfinite(column) & (column != 0.0)]
            per_feature.append({
                "feature": feature,
                "nonzero_count": int(keep.size),
                "min": float(keep.min()) if keep.size else None,
                "median": float(np.median(keep)) if keep.size else None,
                "max": float(keep.max()) if keep.size else None,
                "abs_max": float(np.abs(keep).max()) if keep.size else None,
            })
    return {
        "name": name,
        "shape": list(arr.shape),
        "dtype": str(np.asarray(array).dtype),
        "finite_fraction": float(finite.mean()),
        "nonzero_abs_max": (float(np.abs(flat_nonzero).max())
                            if flat_nonzero.size else None),
        "per_feature": per_feature,
    }


def _first_batch_stats(tf: Any, np: Any, dataset: Any, label: str,
                       ) -> dict[str, Any]:
    """Statistics of the first batch of `dataset`, as the model would receive it."""
    try:
        batch = next(iter(dataset.take(1)))
    except Exception as exc:  # pragma: no cover - environment-dependent
        return {"label": label, "error": repr(exc)}
    inputs, targets = batch
    parts: list[Any] = list(inputs) if isinstance(inputs, tuple) else [inputs]
    names = (["cloud", "event_globals"] if isinstance(inputs, tuple)
             else ["cloud"])
    stats = [_tensor_stats(np, part.numpy(), name)
             for part, name in zip(parts, names)]
    label_col = np.asarray(targets.numpy())
    return {
        "label": label,
        "input_component_count": len(parts),
        "inputs_is_tuple": isinstance(inputs, tuple),
        "inputs": stats,
        # `labels` is np.stack((label, weight), axis=1) in the engine's `cache`,
        # so column 0 is the class and column 1 the per-example weight.
        "labels": {
            "shape": list(label_col.shape),
            "class_values": sorted({float(v) for v in label_col[:, 0][:4096]}),
            "weight_min": float(label_col[:, 1].min()),
            "weight_max": float(label_col[:, 1].max()),
            "weight_mean": float(label_col[:, 1].mean()),
            "weight_finite_fraction": float(np.isfinite(label_col[:, 1]).mean()),
        },
    }


def _callback_facts(callbacks: Any) -> list[dict[str, Any]]:
    """Class, defining file and behaviour-deciding attributes of each callback."""
    import inspect

    facts: list[dict[str, Any]] = []
    for callback in callbacks or []:
        cls = type(callback)
        try:
            source = inspect.getfile(cls)
        except Exception:  # pragma: no cover - builtins have no file
            source = None
        fields = {}
        for field in CALLBACK_FIELDS:
            if hasattr(callback, field):
                value = getattr(callback, field)
                fields[field] = (value if isinstance(value, (int, float, str, bool,
                                                             type(None)))
                                 else repr(value))
        facts.append({"class": f"{cls.__module__}.{cls.__qualname__}",
                      "loaded_from": source, "fields": fields})
    return facts


def _optimizer_facts(tf: Any, optimizer: Any) -> dict[str, Any]:
    """Everything about the optimizer the engine actually attached to the model."""
    import inspect

    cls = type(optimizer)
    try:
        source = inspect.getfile(cls)
    except Exception:  # pragma: no cover
        source = None
    try:
        config = tf.keras.optimizers.serialize(optimizer)
    except Exception as exc:  # pragma: no cover - Horovod wrappers may refuse
        config = {"serialize_error": repr(exc)}
    probes: dict[str, Any] = {}
    for field in OPTIMIZER_PROBES:
        if not hasattr(optimizer, field):
            probes[field] = "ATTRIBUTE_ABSENT"
            continue
        value = getattr(optimizer, field)
        try:
            probes[field] = float(tf.keras.backend.get_value(value))
        except Exception:
            probes[field] = (value if isinstance(value, (int, float, str, bool,
                                                         type(None)))
                             else repr(value))
    # A Horovod DistributedOptimizer wraps the real one; the wrapped object is
    # where weight decay and clipping would live, so it is unwrapped explicitly
    # rather than left to `get_config` to mention or not.
    inner = getattr(optimizer, "_optimizer", None)
    return {
        "class": f"{cls.__module__}.{cls.__qualname__}",
        "loaded_from": source,
        "mro": [f"{c.__module__}.{c.__qualname__}" for c in cls.__mro__[:6]],
        "serialized": config,
        "probes": probes,
        "wraps_inner_optimizer": (None if inner is None else
                                  f"{type(inner).__module__}.{type(inner).__qualname__}"),
        "is_horovod_wrapped": "horovod" in cls.__module__.lower(),
    }


def make_recorder_callback(tf: Any, np: Any, records: list[dict[str, Any]]):
    """A Keras callback class that appends one record per fit into `records`."""

    class _FitRecorder(tf.keras.callbacks.Callback):
        """Per-epoch observation of one `model.fit`, plus the clone comparison."""

        def __init__(self, context: dict[str, Any],
                     pre_clone_weights: dict[str, Any] | None,
                     engine_callbacks: Any) -> None:
            super().__init__()
            self._record: dict[str, Any] = dict(context)
            self._pre_clone = pre_clone_weights
            self._engine_callbacks = engine_callbacks
            self._epochs: list[dict[str, Any]] = []
            self._batches = 0
            self._started = 0.0
            records.append(self._record)

        def _lr(self) -> float | None:
            try:
                return float(tf.keras.backend.get_value(
                    self.model.optimizer.learning_rate))
            except Exception:  # pragma: no cover
                return None

        def _iterations(self) -> int | None:
            try:
                return int(tf.keras.backend.get_value(
                    self.model.optimizer.iterations))
            except Exception:  # pragma: no cover
                return None

        def on_train_begin(self, logs: Any = None) -> None:
            self._started = time.perf_counter()
            at_begin = _digest_weights(self.model.get_weights())
            self._record["weights_at_train_begin"] = {
                "model_sha256": at_begin["model_sha256"],
                "tensor_count": at_begin["tensor_count"],
            }
            # THE CLONE TEST. The engine trains `tf.keras.models.clone_model(model)`
            # at iteration 0; if cloning drops loaded state, the tensors here differ
            # from the model the driver handed in and no pretrained weight is
            # present at the first optimizer step.
            if self._pre_clone is not None:
                self._record["vs_pre_clone_model"] = _compare_weight_sets(
                    self._pre_clone, at_begin)
            self._record["optimizer_iterations_at_train_begin"] = self._iterations()
            self._record["learning_rate_at_train_begin"] = self._lr()

        def on_train_batch_end(self, batch: int, logs: Any = None) -> None:
            self._batches += 1

        def on_epoch_end(self, epoch: int, logs: Any = None) -> None:
            logs = logs or {}
            self._epochs.append({
                "epoch": int(epoch),
                "learning_rate": self._lr(),
                # `iterations` is the optimizer's own counter of applied updates
                # and is therefore the executed update count, not a derivation
                # from batch size and row count.
                "optimizer_iterations": self._iterations(),
                "batches_seen_cumulative": self._batches,
                "loss": (float(logs["loss"]) if "loss" in logs else None),
                "val_loss": (float(logs["val_loss"]) if "val_loss" in logs
                             else None),
                "logged_keys": sorted(logs.keys()),
            })

        def on_train_end(self, logs: Any = None) -> None:
            self._record["epochs"] = self._epochs
            self._record["epochs_run"] = len(self._epochs)
            self._record["batches_total"] = self._batches
            self._record["seconds"] = time.perf_counter() - self._started
            self._record["optimizer_iterations_at_train_end"] = self._iterations()
            at_end = _digest_weights(self.model.get_weights())
            self._record["weights_at_train_end"] = {
                "model_sha256": at_end["model_sha256"],
                "tensor_count": at_end["tensor_count"],
            }
            # Read the ENGINE's own EarlyStopping instance: `stopped_epoch` is
            # non-zero only if the rule fired, and `wait` is how close it came.
            stopping: list[dict[str, Any]] = []
            for callback in self._engine_callbacks or []:
                if type(callback).__name__ != "EarlyStopping":
                    continue
                stopping.append({
                    "patience": getattr(callback, "patience", None),
                    "monitor": getattr(callback, "monitor", None),
                    "stopped_epoch": getattr(callback, "stopped_epoch", None),
                    "wait_at_end": getattr(callback, "wait", None),
                    "restore_best_weights": getattr(callback,
                                                    "restore_best_weights", None),
                    "fired": bool(getattr(callback, "stopped_epoch", 0)),
                })
            self._record["early_stopping"] = stopping

    return _FitRecorder


def instrument(MultiFold: Any, tf: Any, np: Any, records: dict[str, Any]) -> Any:
    """A `MultiFold` subclass that observes compilation, fitting and cloning.

    `records` accumulates four lists: `compiles`, `fits`, `run_model_entries` and
    `first_batches`. It is an explicit parameter for the same reason
    `annealed_estimator.make_annealed_multifold` takes one -- a module-level or
    defaulted accumulator would be shared between the two arms and the receipt
    would attribute one arm's fits to the other while both arms ran correctly.
    """
    Recorder = make_recorder_callback(tf, np, records["fits"])

    class _Instrumented(MultiFold):
        """Observation only: every method calls through and changes no behaviour."""

        def CompileModel(self, model, num_steps, fixed=False):
            out = super().CompileModel(model, num_steps, fixed=fixed)
            records["compiles"].append({
                "fixed_effective": bool(fixed),
                "num_steps_argument": (float(num_steps)
                                       if isinstance(num_steps, (int, float))
                                       else repr(num_steps)),
                "engine_lr_attribute": float(self.LR),
                "optimizer": _optimizer_facts(tf, model.optimizer),
                "loss": getattr(model, "loss", None).__name__ if callable(
                    getattr(model, "loss", None)) else repr(
                        getattr(model, "loss", None)),
                "model_id": id(model),
            })
            return out

        def RunModel(self, labels, weights, iteration, model, stepn,
                     NTRAIN=1000, cached=False):
            # The models the DRIVER handed in, before the engine clones them.
            # Digested here because at iteration 0 `super().RunModel` replaces
            # the trained object with `clone_model(model)` and the pre-clone
            # state is unrecoverable afterwards.
            source_model = self.model1 if stepn == 1 else self.model2
            pre_clone = _digest_weights(source_model.get_weights())
            entry = {
                "iteration": int(iteration),
                "stepn": int(stepn),
                "ntrain_argument": int(NTRAIN),
                "cached_argument": bool(cached),
                "engine": {
                    "BATCH_SIZE": int(self.BATCH_SIZE),
                    "EPOCHS": int(self.EPOCHS),
                    "LR": float(self.LR),
                    "patience": int(self.patience),
                    "train_frac": float(self.train_frac),
                    "num_steps_reco": int(self.num_steps_reco),
                    "num_steps_gen": int(self.num_steps_gen),
                    "start": int(self.start),
                    "n_ensemble": int(self.n_ensemble),
                    "niter": int(self.niter),
                    "size": int(self.size),
                },
                "pre_clone_model": {
                    "model_sha256": pre_clone["model_sha256"],
                    "tensor_count": pre_clone["tensor_count"],
                    "is_driver_model1" if stepn == 1 else "is_driver_model2": True,
                },
                # Digest of the numpy RNG state at entry, so two arms' RNG
                # consumption can be compared without recording the state itself.
                "numpy_rng_state_sha256": hashlib.sha256(
                    np.asarray(np.random.get_state()[1]).tobytes()).hexdigest(),
                "model_is_carried_from_previous_iteration": bool(iteration >= 1),
            }
            records["run_model_entries"].append(entry)

            harness = self

            def wrap_fit(target_model: Any) -> None:
                """Record `fit`'s arguments and append the recorder callback."""
                if getattr(target_model, "_mnv_fit_wrapped", False):
                    return
                original = target_model.fit

                def fit(*a: Any, **kw: Any):
                    train_data = a[0] if a else kw.get("x")
                    callbacks = kw.get("callbacks")
                    context = {
                        "iteration": int(iteration),
                        "stepn": int(stepn),
                        "arm_batch_size": int(harness.BATCH_SIZE),
                        "fit_kwargs": {
                            "epochs": kw.get("epochs"),
                            "steps_per_epoch": kw.get("steps_per_epoch"),
                            "validation_steps": kw.get("validation_steps"),
                            "verbose": kw.get("verbose"),
                            "has_validation_data": "validation_data" in kw,
                        },
                        "engine_callbacks": _callback_facts(callbacks),
                        "model_id": id(target_model),
                        "pre_clone_model_sha256": pre_clone["model_sha256"],
                    }
                    records["first_batches"].append({
                        "iteration": int(iteration), "stepn": int(stepn),
                        "train": _first_batch_stats(tf, np, train_data,
                                                    "train_data"),
                        "validation": _first_batch_stats(
                            tf, np, kw["validation_data"], "validation_data")
                        if "validation_data" in kw else None,
                    })
                    recorder = Recorder(context, pre_clone, callbacks)
                    kw["callbacks"] = list(callbacks or []) + [recorder]
                    return original(*a, **kw)

                target_model.fit = fit
                target_model._mnv_fit_wrapped = True

            # The engine compiles the clone immediately before fitting it, so
            # hooking `CompileModel` is where the clone first becomes reachable.
            outer_compile = self.CompileModel

            def compile_and_wrap(model_e, steps, fixed=False):
                out = outer_compile(model_e, steps, fixed=fixed)
                wrap_fit(model_e)
                return out

            self.CompileModel = compile_and_wrap
            try:
                return super().RunModel(labels, weights, iteration, model, stepn,
                                        NTRAIN, cached)
            finally:
                # Restore the bound method so the post-iteration
                # `CompileModels(fixed=True)` is observed by the class, not by a
                # closure that captured the previous iteration's context.
                del self.CompileModel

    return _Instrumented


def build_args(cli: argparse.Namespace, arm: str) -> argparse.Namespace:
    """The `run_arm_evaluation.evaluate` argument object for one arm.

    `evaluate` takes a namespace, not a parsed command line, so the harness can
    call it directly. The seed and learning rate are still taken from the frozen
    lists: `main`'s guards do not run on this path, and an off-grid value would
    make the observation describe a configuration the campaign never had.
    """
    return argparse.Namespace(
        arm=arm,
        seed=cli.seed,
        stage=cli.stage,
        learning_rate=cli.learning_rate,
        niter=cli.niter,
        repo=cli.repo,
        inputs_npz=cli.inputs_npz,
        theirs_index=cli.theirs_index,
        weights_folder=Path(cli.out) / f"weights-{arm}",
        max_events=cli.max_events,
        half_size=cli.half_size,
        theirs_state_npz=cli.theirs_state_npz,
        theirs_manifest=cli.theirs_manifest,
        identity_sidecar=cli.identity_sidecar,
        theirs_cache=(cli.theirs_cache if arm == "theirs" else None),
        output=None,
        dry_run=False,
    )


def audit_arm(cli: argparse.Namespace, arm: str) -> dict[str, Any]:
    """Run one arm through the historical driver with instrumentation installed."""
    repo = Path(cli.repo).resolve()
    comparison = repo / "nd-unfolding" / "pet" / "configuration_comparison"
    for extra in (str(comparison), str(repo / "nd-unfolding" / "pet"),
                  str(repo / "omnifold_nn")):
        if extra not in sys.path:
            sys.path.insert(0, extra)

    from keras_backend import (configure_production_precision,  # noqa: E402
                               observed_precision_policy, record_versions,
                               select_keras_backend)

    backend = select_keras_backend()
    precision_applied = configure_production_precision(strict=True)

    import numpy as np  # noqa: E402
    import tensorflow as tf  # noqa: E402

    import omnifold.omnifold as engine  # noqa: E402
    import run_arm_evaluation as driver  # noqa: E402

    records: dict[str, Any] = {"compiles": [], "fits": [],
                               "run_model_entries": [], "first_batches": []}
    original = engine.MultiFold
    # `evaluate` resolves `from omnifold.omnifold import MultiFold` inside its own
    # body, so rebinding the module attribute here reaches that resolution. The
    # FILE is untouched; only this process's view of the name changes.
    engine.MultiFold = instrument(original, tf, np, records)
    try:
        started = time.perf_counter()
        receipt = driver.evaluate(build_args(cli, arm))
        elapsed = time.perf_counter() - started
    finally:
        engine.MultiFold = original

    loaded = {}
    for name in ("omnifold.omnifold", "omnifold.net", "omnifold.dataloader",
                 "run_arm_evaluation", "annealed_estimator", "training_recipe",
                 "fullevent_fps_dataloader", "frozen_design",
                 "closure_powered_truth_reweight", "theirs_omnifold_arm",
                 "theirs_token_schema", "stage_splits"):
        module = sys.modules.get(name)
        if module is None or not getattr(module, "__file__", None):
            loaded[name] = {"imported": module is not None, "file": None}
            continue
        path = Path(module.__file__).resolve()
        loaded[name] = {
            "imported": True,
            "file": str(path),
            "sha256": sha256_of(path),
            "inside_expected_repo": str(path).startswith(str(repo)),
        }

    return {
        "arm": arm,
        "seconds": elapsed,
        "environment": {
            "keras_backend_choice": backend,
            "versions": record_versions(),
            "precision_applied": precision_applied,
            # Re-observed AFTER training, because a policy that took at startup
            # and was overwritten by a later import is the failure mode.
            "precision_observed_after_run": observed_precision_policy(),
            "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "gpus_visible": [d.name for d in tf.config.list_physical_devices("GPU")],
        },
        "modules_actually_loaded": loaded,
        "driver_receipt": receipt,
        "observations": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True,
                        help="the pinned checkout to observe")
    parser.add_argument("--out", type=Path, required=True,
                        help="output directory; must not be under the historical "
                             "campaign output root")
    parser.add_argument("--arms", default="ours,theirs")
    parser.add_argument("--stage", choices=("tuning", "pilot", "final"),
                        default="tuning")
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--niter", type=int, default=2)
    parser.add_argument("--max-events", type=int, default=2_000_000)
    parser.add_argument("--half-size", type=int, default=None)
    parser.add_argument("--inputs-npz", type=Path, required=True)
    parser.add_argument("--theirs-index", type=Path, required=True)
    parser.add_argument("--theirs-state-npz", type=Path, required=True)
    parser.add_argument("--theirs-manifest", type=Path, required=True)
    parser.add_argument("--identity-sidecar", type=Path, required=True)
    parser.add_argument("--theirs-cache", type=Path, default=None)
    parser.add_argument("--commit", default=HISTORICAL_COMMIT)
    args = parser.parse_args()

    out = Path(args.out).resolve()
    if "campaign-20260920" in out.parts:
        raise SystemExit(
            f"[audit] refusing to write into {out}: the historical campaign's "
            "outputs are preserved unmodified")
    out.mkdir(parents=True, exist_ok=True)

    identity = verify_historical_modules(Path(args.repo).resolve(), args.commit)

    arms = [a for a in args.arms.split(",") if a]
    results = []
    for arm in arms:
        result = audit_arm(args, arm)
        results.append(result)
        # Written per arm, so a second arm that dies on the queue still leaves the
        # first arm's observation on disk rather than losing both.
        (out / f"runtime_audit-{arm}.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(f"[audit] {arm}: {len(result['observations']['fits'])} fits observed")

    payload = {
        "task": "A1 Part 1 evidence level 1 (runtime capture of the historical path)",
        "historical_module_identity": identity,
        "harness_perturbation": (
            "one extra batch is drawn from each dataset handed to fit, through an "
            "independent tf.data iterator, for the input-semantics statistics; the "
            "recorder callback is APPENDED to the engine's callback list and "
            "replaces none of them"),
        "invocation": {k: str(v) for k, v in vars(args).items()},
        "arms": results,
    }
    (out / "runtime_audit.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"[audit] -> {out / 'runtime_audit.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
