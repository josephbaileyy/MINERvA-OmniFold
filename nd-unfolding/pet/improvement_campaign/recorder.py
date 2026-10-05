"""Per-epoch recorder for the campaign driver, measuring what training EXECUTED.

For every fit (OmniFold iteration x step) and every epoch it writes one JSON line with: train and
validation loss; the learning rate at the epoch's first and last update (and its range, for a
schedule); optimizer updates (the optimizer's own counter); examples and the largest batch
(counted in-graph inside `train_step`); gradient global-norm statistics before and after clipping
(accumulated in-graph inside the optimizer's `_clip_gradients`); for torch-style clipping the
optimizer's own clip-event counter; and weight-tail / effective-sample-size statistics of the
current classifier's reweighting on a fixed probe of held-out label-0 rows.

It also ENFORCES the recipe: at the first optimizer step the pretrained policy is checked tensor by
tensor, and at every epoch end the measured examples, updates and batch size must equal what the
recipe and the split imply, or the fit fails closed. The restore policy (`last` / `best`) is
applied here, at train end, so it does not depend on a Keras callback firing.

Instrumentation is installed once per class (`install_counters`); it only adds `assign` ops on
variables the model never reads.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any, Callable

REWEIGHT_LOGIT_CAP = 30.0   # the engine's `omnifold.REWEIGHT_LOGIT_CAP`, checked at import in run_unfold

_COUNTERS: dict[int, dict[str, Any]] = {}
_PATCHED: set[type] = set()
_CLIP_PATCHED: list[bool] = [False]


def weight_stats(np: Any, w: Any, base: Any | None = None) -> dict[str, Any]:
    """Tail and ESS statistics of positive reweighting factors (optionally times base weights)."""
    w = np.asarray(w, dtype=np.float64)
    if w.size == 0:
        return {"n": 0}
    total = w if base is None else w * np.asarray(base, dtype=np.float64)
    pos = total[total > 0]
    ess = float(pos.sum() ** 2 / np.square(pos).sum()) if pos.size else 0.0
    q = np.quantile(w, [0.5, 0.99, 0.999])
    return {"n": int(w.size), "mean": float(w.mean()), "std": float(w.std()),
            "max": float(w.max()), "min": float(w.min()),
            "q50": float(q[0]), "q99": float(q[1]), "q999": float(q[2]),
            "max_over_mean": float(w.max() / w.mean()) if w.mean() > 0 else None,
            "ess": ess, "ess_fraction": ess / pos.size if pos.size else None}


def install_counters(tf: Any, optimizer_base: type) -> None:
    """Wrap the optimizer base's `_clip_gradients` once, accumulating norm statistics in-graph."""
    if _CLIP_PATCHED[0]:
        return
    original = optimizer_base._clip_gradients

    def _clip_gradients(self: Any, grads: Any) -> Any:
        clipped = original(self, grads)
        slot = _COUNTERS.get(id(self))
        if slot is not None:
            pre = tf.cast(tf.linalg.global_norm([g for g in grads if g is not None]), tf.float64)
            post = tf.cast(tf.linalg.global_norm([g for g in clipped if g is not None]),
                           tf.float64)
            slot["n"].assign_add(1)
            slot["pre_sum"].assign_add(pre)
            slot["pre_max"].assign(tf.maximum(slot["pre_max"], pre))
            slot["post_max"].assign(tf.maximum(slot["post_max"], post))
            changed = tf.abs(pre - post) > 1e-6 * tf.maximum(tf.constant(1.0, tf.float64), pre)
            slot["changed"].assign_add(tf.cast(changed, tf.int64))
        return clipped

    optimizer_base._clip_gradients = _clip_gradients
    _CLIP_PATCHED[0] = True


def patch_train_step(tf: Any, cls: type) -> None:
    """Count rows, the largest batch and the weight sum of every training batch, in-graph."""
    if cls in _PATCHED:
        return
    original = cls.train_step

    def train_step(self: Any, data: Any) -> Any:
        slot = _COUNTERS.get(id(self))
        if slot is not None:
            first = tf.nest.flatten(data[0])[0]
            rows = tf.cast(tf.shape(first)[0], tf.int64)
            slot["rows"].assign_add(rows)
            slot["max_rows"].assign(tf.maximum(slot["max_rows"], rows))
        return original(self, data)

    cls.train_step = train_step
    _PATCHED.add(cls)


def _new_slot(tf: Any) -> dict[str, Any]:
    f64 = dict(trainable=False, dtype=tf.float64)
    i64 = dict(trainable=False, dtype=tf.int64)
    return {"n": tf.Variable(0, **i64), "pre_sum": tf.Variable(0.0, **f64),
            "pre_max": tf.Variable(0.0, **f64), "post_max": tf.Variable(0.0, **f64),
            "changed": tf.Variable(0, **i64), "rows": tf.Variable(0, **i64),
            "max_rows": tf.Variable(0, **i64)}


def _read(slot: dict[str, Any]) -> dict[str, Any]:
    return {k: v.numpy().item() for k, v in slot.items()}


def trainable_digest(np: Any, model: Any) -> str:
    digest = hashlib.sha256()
    for v in model.trainable_variables:
        digest.update(np.ascontiguousarray(v.numpy()).tobytes())
    return digest.hexdigest()


class FitExpectation:
    """What the split and recipe say one epoch of this fit must look like."""

    def __init__(self, n_train: int, batch_size: int) -> None:
        self.n_train = int(n_train)
        self.batch_size = int(batch_size)
        self.updates_per_epoch = math.ceil(self.n_train / self.batch_size)


def make_epoch_recorder(tf: Any, np: Any, *, context: dict[str, Any], sink: Path,
                        expectation: FitExpectation, stopping: Any,
                        lr_at: Callable[[Any], Any], probe: Any = None,
                        pretrained_check: Callable[[Any], dict[str, Any]] | None = None) -> Any:
    """Build the recorder callback for one fit. `probe` = (inputs, base_weights) or None."""

    class EpochRecorder(tf.keras.callbacks.Callback):
        def __init__(self) -> None:
            super().__init__()
            self.summary: dict[str, Any] = {"context": context, "epochs": []}
            self.best_value = math.inf
            self.best_epoch = -1
            self.best_weights = None
            self.wait = 0
            self.first_step_seen = False
            self.digests: list[str] = []

        # ---- helpers ---------------------------------------------------------------------- #
        def _slot(self) -> dict[str, Any]:
            return _COUNTERS[id(self.model.optimizer)]

        def _model_slot(self) -> dict[str, Any]:
            return _COUNTERS[id(self.model)]

        def _emit(self, record: dict[str, Any]) -> None:
            with Path(sink).open("a") as handle:
                handle.write(json.dumps(record, default=repr) + "\n")

        # ---- Keras hooks ------------------------------------------------------------------ #
        def on_train_begin(self, logs: Any = None) -> None:
            _COUNTERS[id(self.model.optimizer)] = _new_slot(tf)
            _COUNTERS[id(self.model)] = _new_slot(tf)
            patch_train_step(tf, type(self.model))
            self.summary["weights_at_train_begin"] = trainable_digest(np, self.model)
            self.summary["optimizer_iterations_at_begin"] = int(
                self.model.optimizer.iterations.numpy())

        def on_train_batch_begin(self, batch: int, logs: Any = None) -> None:
            if self.first_step_seen:
                return
            self.first_step_seen = True
            self.summary["weights_at_first_step"] = trainable_digest(np, self.model)
            if pretrained_check is not None:
                result = pretrained_check(self.model)
                self.summary["pretrained_at_first_step"] = result
                if not result.get("all_equal_to_pretrained"):
                    raise RuntimeError(
                        f"[recorder] pretrained policy declared but the weights at the first "
                        f"optimizer step differ from the state: {result}")

        def on_epoch_begin(self, epoch: int, logs: Any = None) -> None:
            self.t0 = time.perf_counter()
            self.before = {**{f"opt_{k}": v for k, v in _read(self._slot()).items()},
                           **{f"model_{k}": v for k, v in _read(self._model_slot()).items()}}
            self.it0 = int(self.model.optimizer.iterations.numpy())
            self._model_slot()["max_rows"].assign(0)
            clip_events = getattr(self.model.optimizer, "clip_events", None)
            self.torch_clip0 = None if clip_events is None else int(clip_events.numpy())

        def on_epoch_end(self, epoch: int, logs: Any = None) -> None:
            seconds = time.perf_counter() - self.t0
            opt = self.model.optimizer
            it1 = int(opt.iterations.numpy())
            o, m = _read(self._slot()), _read(self._model_slot())
            updates = it1 - self.it0
            examples = m["rows"] - self.before["model_rows"]
            n_clip_calls = o["n"] - self.before["opt_n"]
            lrs = np.asarray(lr_at(np.arange(self.it0, max(it1, self.it0 + 1))), dtype=float)
            record = {
                **context, "epoch": int(epoch),
                "loss": float((logs or {}).get("loss", float("nan"))),
                "val_loss": float((logs or {}).get("val_loss", float("nan"))),
                "lr_first_update": float(lrs[0]), "lr_last_update": float(lrs[-1]),
                "lr_min": float(lrs.min()), "lr_max": float(lrs.max()),
                "optimizer_updates": updates, "examples": examples,
                "max_batch_rows": m["max_rows"],
                "grad_norm_pre_clip_mean": ((o["pre_sum"] - self.before["opt_pre_sum"]) /
                                            n_clip_calls) if n_clip_calls else None,
                "grad_norm_pre_clip_max_so_far": o["pre_max"],
                "grad_norm_post_clip_max_so_far": o["post_max"],
                "updates_changed_by_keras_clip": o["changed"] - self.before["opt_changed"],
                "torch_clip_events": (None if self.torch_clip0 is None else
                                      int(opt.clip_events.numpy()) - self.torch_clip0),
                "seconds": seconds,
            }
            if probe is not None:
                inputs, base = probe
                logit = np.asarray(self.model.predict(inputs, batch_size=expectation.batch_size,
                                                      verbose=0))[:, 0]
                record["probe_nonfinite_logits"] = int((~np.isfinite(logit)).sum())
                logit = np.clip(logit, -REWEIGHT_LOGIT_CAP, REWEIGHT_LOGIT_CAP)
                record["probe_reweight"] = weight_stats(np, np.exp(logit), base)
                record["probe_saturated_fraction"] = float(
                    (np.abs(logit) >= REWEIGHT_LOGIT_CAP).mean())
            problems = []
            if examples != expectation.n_train:
                problems.append(f"examples {examples} != training rows {expectation.n_train}")
            if updates != expectation.updates_per_epoch:
                problems.append(f"updates {updates} != {expectation.updates_per_epoch}")
            if m["max_rows"] != min(expectation.batch_size, expectation.n_train):
                problems.append(f"largest batch {m['max_rows']} != {expectation.batch_size}")
            record["recipe_violations"] = problems
            self.digests.append(trainable_digest(np, self.model))
            record["weights_digest"] = self.digests[-1]
            self.summary["epochs"].append(record)
            self._emit(record)
            if problems:
                raise RuntimeError(f"[recorder] executed epoch differs from the recipe: {problems}")
            # stopping and best-weight tracking, by the recipe
            value = record["val_loss"]
            if value < self.best_value - stopping.min_delta:
                self.best_value, self.best_epoch, self.wait = value, int(epoch), 0
                if stopping.restore == "best":
                    self.best_weights = self.model.get_weights()
            else:
                self.wait += 1
                if stopping.patience is not None and self.wait >= stopping.patience:
                    self.model.stop_training = True
                    self.summary["stopped_early_at_epoch"] = int(epoch)

        def on_train_end(self, logs: Any = None) -> None:
            _COUNTERS.pop(id(self.model.optimizer), None)
            _COUNTERS.pop(id(self.model), None)
            if stopping.restore == "best" and self.best_weights is not None:
                self.model.set_weights(self.best_weights)
            final = trainable_digest(np, self.model)
            self.summary.update({
                "epochs_run": len(self.summary["epochs"]),
                "best_epoch": self.best_epoch, "restore_policy": stopping.restore,
                "final_weights_digest": final,
                "final_weights_equal_epoch": [i for i, d in enumerate(self.digests) if d == final],
            })
            expected = (self.best_epoch if stopping.restore == "best"
                        else len(self.digests) - 1)
            self.summary["restore_executed_as_declared"] = expected in \
                self.summary["final_weights_equal_epoch"]
            if not self.summary["restore_executed_as_declared"]:
                raise RuntimeError(f"[recorder] restore policy {stopping.restore!r} not executed")

    return EpochRecorder()
