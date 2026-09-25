"""Level-1 evidence: run the historical comparison driver UNMODIFIED and record what executed.

Task A1 (scope §4 A and B). The comparison's training path is
`configuration_comparison/run_arm_evaluation.evaluate` at commit
`68cf9d29f8ab1b0f5acd933d4baec1962b29e34d`. This harness imports that function from a checkout
pinned to that commit and calls it with the historical arguments on a small event subsample. It
changes nothing the driver does; it OBSERVES by wrapping, at class level, the objects the driver
reaches:

* `keras` `Model.fit` -- appends one recorder callback and records the fit's arguments, callback
  configuration, the model and optimizer actually used (class, MRO with source files, full
  `get_config()`), and the returned history;
* `Model.train_step` of each trained class -- counts the rows of every batch in-graph, so batch
  size and examples per epoch are measured, not derived;
* the Keras optimizer base `_clip_gradients` -- records the global gradient norm entering and
  leaving clipping on every update, so "clipping actually applied" is a measurement;
* `omnifold.omnifold.MultiFold` (via a post-import hook, so the module is resolved by the
  historical code's own `sys.path` manipulation and not pre-empted by this harness) --
  `__init__`, `cache`, `RunModel`, `CompileModel` and `reweight`, recording step counts, the
  validation split, RNG state digests, training weights and the arrays that reach the model.

Nothing is monkeypatched in a way that alters arithmetic: every wrapper calls the original with
the original arguments and returns its result; the in-graph counters are `assign` ops on
variables the model never reads.

What is measured per fit (arm x iteration x OmniFold step): optimizer class/config, learning rate
per epoch, pre/post-clip gradient norms, batch rows, examples and optimizer updates per epoch,
epochs run, EarlyStopping state and whether it fired, which epoch's weights survive the fit,
weight digests at fit start and at the first optimizer step, warm start across iterations, model
and optimizer identity across fits, and -- for the pretrained arm -- a tensor-by-tensor comparison
of the weights at the first optimizer step against the exported pretrained state.

Module provenance: after the run every loaded module whose file lies in a MINERvA-OmniFold
checkout is recorded with its git blob id and compared to the blob `git ls-tree` reports for the
same path at the historical commit (`--tree-listing`), so the claim "the code under test is the
historical commit's" is itself a runtime measurement. The historical driver inserts the hardcoded
tree `/pscratch/sd/j/josephrb/MINERvA-OmniFold` at `sys.path[0]` (OI-136), so some modules
resolve there; the blob comparison is what says whether that changed the executed code.

NOT CITABLE FOR any recovery or performance claim: the subsample is tiny by design.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.abc
import importlib.util
import inspect
import json
import os
import random
import sys
import time
from pathlib import Path
from typing import Any

HISTORICAL_COMMIT = "68cf9d29f8ab1b0f5acd933d4baec1962b29e34d"
HARDCODED_ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
CHECKOUT_MARKERS = ("VALIDATION_LEDGER.md", "nd-unfolding")


# --------------------------------------------------------------------------- #
# Pure helpers (no TensorFlow; unit-tested locally)
# --------------------------------------------------------------------------- #
def git_blob_id(path: Path) -> str:
    """The id `git hash-object` gives a file, computed without git."""
    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_tree_listing(text: str) -> dict[str, str]:
    """`git ls-tree -r <commit>` output -> {path: blob id}."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        meta, _tab, path = line.partition("\t")
        parts = meta.split()
        if len(parts) == 3 and parts[1] == "blob":
            out[path] = parts[2]
    return out


def checkout_root_of(path: str) -> str | None:
    """The nearest enclosing directory holding both checkout markers, or None."""
    here = Path(path).resolve().parent
    for candidate in (here, *here.parents):
        if all((candidate / marker).exists() for marker in CHECKOUT_MARKERS):
            return str(candidate)
    return None


def module_provenance(modules: dict[str, Any], tree: dict[str, str],
                      labels: dict[str, str]) -> dict[str, Any]:
    """Every loaded module inside a checkout, with its blob compared to the historical tree."""
    rows = []
    for name, module in sorted(modules.items()):
        origin = getattr(module, "__file__", None)
        if not origin or not str(origin).endswith(".py"):
            continue
        root = checkout_root_of(origin)
        if root is None:
            continue
        rel = str(Path(origin).resolve().relative_to(root))
        blob = git_blob_id(Path(origin))
        expected = tree.get(rel)
        rows.append({
            "module": name, "file": str(Path(origin).resolve()), "checkout_root": root,
            "root_label": labels.get(root, "UNLABELLED"), "relpath": rel, "blob": blob,
            "historical_blob": expected,
            "matches_historical_commit": expected is not None and blob == expected,
        })
    by_root: dict[str, int] = {}
    for row in rows:
        by_root[row["root_label"]] = by_root.get(row["root_label"], 0) + 1
    mismatched = [r for r in rows if not r["matches_historical_commit"]]
    return {"modules": rows, "count_by_root": by_root,
            "all_match_historical_commit": not mismatched,
            "mismatched": [(r["module"], r["root_label"], r["relpath"]) for r in mismatched]}


def jsonable(value: Any) -> Any:
    """Best-effort conversion of Keras/NumPy config values to JSON."""
    if isinstance(value, (str, bool, type(None))):
        return value
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    for attr in ("item",):
        if hasattr(value, attr):
            try:
                return jsonable(value.item())
            except Exception:  # noqa: BLE001 - non-scalar arrays fall through
                pass
    if hasattr(value, "numpy"):
        try:
            return jsonable(value.numpy().tolist())
        except Exception:  # noqa: BLE001
            pass
    return repr(value)


def class_provenance(cls: type) -> list[dict[str, Any]]:
    """The MRO of `cls`, each with the source file it was loaded from."""
    out = []
    for klass in cls.__mro__:
        if klass is object:
            continue
        try:
            source = inspect.getsourcefile(klass)
        except TypeError:
            source = None
        out.append({"qualname": klass.__qualname__, "module": klass.__module__,
                    "source_file": source})
    return out


def column_stats(np: Any, array: Any, names: list[str] | None = None,
                 real_mask: Any = None) -> dict[str, Any]:
    """Per-column min/max/mean/std over real rows (tokens) or events."""
    a = np.asarray(array, dtype=np.float64)
    width = a.shape[-1]
    flat = a.reshape(-1, width)
    if real_mask is None:
        real = np.any(flat != 0, axis=1) if a.ndim == 3 else np.ones(flat.shape[0], bool)
    else:
        real = np.asarray(real_mask, bool).reshape(-1)
    rows = flat[real]
    cols = []
    for j in range(width):
        col = rows[:, j]
        cols.append({
            "column": j, "name": (names[j] if names and j < len(names) else None),
            "n": int(col.size),
            "min": float(col.min()) if col.size else None,
            "max": float(col.max()) if col.size else None,
            "mean": float(col.mean()) if col.size else None,
            "std": float(col.std()) if col.size else None,
            "frac_exact_zero": float((col == 0).mean()) if col.size else None,
            "n_unique_capped": int(min(np.unique(col).size, 1000)) if col.size else 0,
        })
    out = {"shape": list(a.shape), "real_rows": int(real.sum()),
           "real_fraction": float(real.mean()) if real.size else None,
           "nonfinite": int((~np.isfinite(a)).sum()), "columns": cols}
    if a.ndim == 3:
        per_event = np.asarray(array).reshape(a.shape[0], a.shape[1], width)
        n_real = np.any(per_event != 0, axis=2).sum(axis=1)
        out["tokens_per_event"] = {"min": int(n_real.min()), "max": int(n_real.max()),
                                   "mean": float(n_real.mean()),
                                   "frac_at_cap": float((n_real == a.shape[1]).mean())}
    return out


def theirs_token_semantics(np: Any, packed: Any, pid_codes: dict[str, int] | None
                           ) -> dict[str, Any]:
    """Checks that the packed block reaching his model holds converted features.

    Converted: [eta, phi, log pT, log E, PID | dEdx, x/1e4, y/1e4, z/1e4, t/1e4].
    The pre-repair defect fed raw [px, py, pz, log E] and millimetre positions (up to 8.2e4).
    A real token is one with log E != 0 (the arm's own mask).
    """
    p = np.asarray(packed, dtype=np.float64)
    real = p[..., 3] != 0
    t = p[real]
    if t.size == 0:
        return {"real_tokens": 0}
    eta, phi, logpt, loge, pid = t[:, 0], t[:, 1], t[:, 2], t[:, 3], t[:, 4]
    pos = t[:, 6:9]
    pid_values = sorted({int(v) for v in np.unique(pid)})
    muon_code = None if not pid_codes else pid_codes.get("muon")
    per_event_real = np.any(p[..., 3] != 0, axis=-1)
    if muon_code is not None:
        has_muon = np.any((p[..., 4] == muon_code) & (p[..., 3] != 0), axis=-1)
        muon_fraction = float(has_muon[per_event_real].mean()) if per_event_real.any() else None
    else:
        muon_fraction = None
    return {
        "real_tokens": int(real.sum()),
        "eta_within_clip_10": bool(np.all(np.abs(eta) <= 10.0 + 1e-6)),
        "phi_within_pi": bool(np.all(np.abs(phi) <= np.pi + 1e-5)),
        "logE_ge_logpT_fraction": float(np.mean(loge >= logpt - 1e-4)),
        "max_abs_first_three_columns": float(np.max(np.abs(t[:, :3]))),
        "max_abs_position_columns": float(np.max(np.abs(pos))),
        "dEdx_min": float(t[:, 5].min()), "dEdx_max": float(t[:, 5].max()),
        "dEdx_sentinel_present": bool(np.any(t[:, 5] <= -9000)),
        "pid_values": pid_values, "pid_codes": pid_codes,
        "pid_integer_valued": bool(np.all(pid == np.round(pid))),
        "events_with_any_token": int(per_event_real.sum()),
        "fraction_of_reco_events_with_muon_token": muon_fraction,
        "reading": ("raw momenta would put |col0..2| up to ~1e4-1e5 and phi outside [-pi, pi]; "
                    "converted features keep eta within the clip, phi within pi and "
                    "log E >= log pT for every real token"),
    }


def weights_summary(np: Any, w: Any) -> dict[str, Any]:
    w = np.asarray(w, dtype=np.float64)
    pos = w[w > 0]
    ess = float(pos.sum() ** 2 / (pos ** 2).sum()) if pos.size else None
    return {"n": int(w.size), "sum": float(w.sum()), "min": float(w.min()) if w.size else None,
            "max": float(w.max()) if w.size else None, "n_zero": int((w == 0).sum()),
            "n_negative": int((w < 0).sum()), "ess_positive": ess,
            "sha256": hashlib.sha256(np.ascontiguousarray(w).tobytes()).hexdigest()}


def digest_arrays(arrays: list[Any]) -> str:
    digest = hashlib.sha256()
    for a in arrays:
        digest.update(memoryview(a.tobytes()))
    return digest.hexdigest()


def np_random_state_digest(np: Any) -> str:
    kind, keys, pos, has_gauss, cached = np.random.get_state()
    digest = hashlib.sha256(np.asarray(keys).tobytes())
    digest.update(f"{kind}:{pos}:{has_gauss}:{cached}".encode())
    return digest.hexdigest()


def python_random_state_digest() -> str:
    return hashlib.sha256(repr(random.getstate()).encode()).hexdigest()


# --------------------------------------------------------------------------- #
# Post-import hook: patch a module right after the HISTORICAL code imports it
# --------------------------------------------------------------------------- #
class PostImportHook(importlib.abc.MetaPathFinder):
    """Run a callback right after a named module executes, without resolving it ourselves.

    `find_spec` defers to the rest of `sys.meta_path` (including the OI-136 guard's finder), so
    the file found is exactly the one the importing code would have found; only the loader's
    `exec_module` is wrapped.
    """

    def __init__(self, callbacks: dict[str, Any]):
        self.callbacks = dict(callbacks)
        self._busy: set[str] = set()
        self.fired: dict[str, str] = {}

    def find_spec(self, fullname: str, path: Any = None, target: Any = None) -> Any:
        if fullname not in self.callbacks or fullname in self._busy:
            return None
        self._busy.add(fullname)
        try:
            spec = importlib.util.find_spec(fullname)
        finally:
            self._busy.discard(fullname)
        if spec is None or spec.loader is None:
            return spec
        loader = spec.loader
        original = loader.exec_module
        callback = self.callbacks[fullname]
        hook = self

        def exec_module(module: Any) -> None:
            original(module)
            hook.fired[fullname] = str(getattr(module, "__file__", None))
            callback(module)

        loader.exec_module = exec_module
        return spec


# --------------------------------------------------------------------------- #
# The audit: state shared by the wrappers
# --------------------------------------------------------------------------- #
class Audit:
    def __init__(self, arm: str, state_npz: Path | None):
        self.arm = arm
        self.state_npz = state_npz
        self.context: dict[str, Any] = {}
        self.fits: list[dict[str, Any]] = []
        self.multifold: dict[str, Any] = {}
        self.caches: list[dict[str, Any]] = []
        self.compiles: list[dict[str, Any]] = []
        self.reweights: list[dict[str, Any]] = []
        self.inputs: dict[str, Any] = {}
        self.clip_vars: dict[int, Any] = {}
        self.batch_vars: dict[int, Any] = {}
        self.end_digest_by_step: dict[int, str] = {}
        self.seen_model_ids: dict[int, int] = {}
        self.seen_optimizer_ids: list[int] = []
        self.errors: list[str] = []
        self.patched_train_step: set[type] = set()


def _optimizer_facts(tf: Any, optimizer: Any) -> dict[str, Any]:
    try:
        config = jsonable(optimizer.get_config())
    except Exception as exc:  # noqa: BLE001
        config = f"get_config failed: {exc!r}"
    lr = optimizer.learning_rate
    return {
        "class": type(optimizer).__qualname__,
        "class_module": type(optimizer).__module__,
        "mro": class_provenance(type(optimizer)),
        "config": config,
        "learning_rate_type": type(lr).__qualname__,
        "learning_rate_is_schedule": isinstance(
            lr, tf.keras.optimizers.schedules.LearningRateSchedule),
        "learning_rate_value": float(tf.keras.backend.get_value(lr))
        if not isinstance(lr, tf.keras.optimizers.schedules.LearningRateSchedule) else None,
        "iterations_at_record": int(optimizer.iterations.numpy()),
        "clipnorm": getattr(optimizer, "clipnorm", None),
        "global_clipnorm": getattr(optimizer, "global_clipnorm", None),
        "clipvalue": getattr(optimizer, "clipvalue", None),
        "weight_decay": getattr(optimizer, "weight_decay", None),
        "is_horovod_wrapped": "horovod" in type(optimizer).__module__,
        "id": id(optimizer),
    }


def _callback_facts(callbacks: list[Any]) -> list[dict[str, Any]]:
    keys = ("monitor", "patience", "min_delta", "mode", "baseline", "restore_best_weights",
            "start_from_epoch", "factor", "min_lr", "cooldown", "save_best_only",
            "save_weights_only", "filepath", "verbose")
    out = []
    for cb in callbacks:
        facts = {"class": type(cb).__qualname__, "module": type(cb).__module__}
        for key in keys:
            if hasattr(cb, key):
                facts[key] = jsonable(getattr(cb, key))
        out.append(facts)
    return out


def _pretrained_comparison(np: Any, model: Any, state_npz: Path) -> dict[str, Any]:
    """Every exported tensor against the model's live variable, by name."""
    port = sys.modules.get("pet2_keras_port")
    if port is None or not hasattr(model, "backbone"):
        return {"applicable": False}
    inventory = dict(port.parameter_inventory(model.backbone))
    with np.load(str(state_npz)) as blob:
        arrays = {name: blob[name] for name in blob.files}
    exact, worst, compared = 0, 0.0, 0
    missing = sorted(set(arrays) - set(inventory))
    differing: list[tuple[str, float]] = []
    for name, variable in inventory.items():
        if name not in arrays:
            continue
        live = variable.numpy()
        ref = arrays[name].astype(live.dtype)
        diff = float(np.max(np.abs(live - ref))) if live.size else 0.0
        compared += 1
        worst = max(worst, diff)
        if diff == 0.0:
            exact += 1
        else:
            differing.append((name, diff))
    differing.sort(key=lambda item: -item[1])
    return {"applicable": True, "state_npz": str(state_npz), "tensors_in_state": len(arrays),
            "tensors_in_model": len(inventory), "compared": compared, "exactly_equal": exact,
            "worst_abs_difference": worst, "state_tensors_missing_from_model": missing[:10],
            "largest_differences": differing[:5],
            "all_equal_to_pretrained": compared == len(arrays) and exact == compared}


def _weights_digest(np: Any, model: Any) -> dict[str, Any]:
    """Digest of the TRAINABLE variables only.

    `model.get_weights()` would also carry the `loss_tracker` metric's running state, which
    changes on every batch and would make "same weights" comparisons meaningless.
    """
    arrays = [np.ascontiguousarray(v.numpy()) for v in model.trainable_variables]
    return {"digest": digest_arrays(arrays), "tensors": len(arrays),
            "parameters": int(sum(a.size for a in arrays)),
            "non_trainable_variables": len(model.non_trainable_variables)}


def make_recorder(tf: Any, np: Any, audit: Audit, record: dict[str, Any],
                  callbacks: list[Any]) -> Any:
    """The per-fit recorder. Appended LAST, so it observes every other callback's effect."""

    class Recorder(tf.keras.callbacks.Callback):
        def __init__(self) -> None:
            super().__init__()
            self.epoch_rows0 = 0
            self.epoch_iter0 = 0
            self.epoch_t0 = 0.0
            self.batches = 0
            self.norms_pre: list[float] = []
            self.norms_post: list[float] = []
            self.first_step_done = False

        def _vars(self) -> tuple[Any, Any]:
            return audit.clip_vars[id(self.model.optimizer)], audit.batch_vars[id(self.model)]

        def on_train_begin(self, logs: Any = None) -> None:
            opt = self.model.optimizer
            audit.clip_vars[id(opt)] = {
                "pre": tf.Variable(-1.0, trainable=False, dtype=tf.float32),
                "post": tf.Variable(-1.0, trainable=False, dtype=tf.float32),
                "calls": tf.Variable(0, trainable=False, dtype=tf.int64)}
            audit.batch_vars[id(self.model)] = {
                "rows": tf.Variable(0, trainable=False, dtype=tf.int64),
                "last": tf.Variable(0, trainable=False, dtype=tf.int64),
                "wsum": tf.Variable(0.0, trainable=False, dtype=tf.float64)}
            record["optimizer_at_train_begin"] = _optimizer_facts(tf, opt)
            record["weights_at_train_begin"] = _weights_digest(np, self.model)
            prev = audit.end_digest_by_step.get(record["step"])
            record["warm_start_from_previous_fit_of_this_step"] = (
                None if prev is None else prev == record["weights_at_train_begin"]["digest"])
            if audit.state_npz is not None and hasattr(self.model, "backbone"):
                record["pretrained_at_train_begin"] = _pretrained_comparison(
                    np, self.model, audit.state_npz)
            record["model_pretrained_attribute"] = jsonable(
                getattr(self.model, "pretrained", "ABSENT"))
            record["epochs"] = []

        def on_train_batch_begin(self, batch: int, logs: Any = None) -> None:
            if self.first_step_done:
                return
            self.first_step_done = True
            opt = self.model.optimizer
            record["at_first_optimizer_step"] = {
                "optimizer_iterations": int(opt.iterations.numpy()),
                "weights": _weights_digest(np, self.model),
            }
            if audit.state_npz is not None and hasattr(self.model, "backbone"):
                record["at_first_optimizer_step"]["pretrained"] = _pretrained_comparison(
                    np, self.model, audit.state_npz)

        def on_epoch_begin(self, epoch: int, logs: Any = None) -> None:
            clip, batch = self._vars()
            self.epoch_rows0 = int(batch["rows"].numpy())
            self.epoch_iter0 = int(self.model.optimizer.iterations.numpy())
            self.epoch_t0 = time.perf_counter()
            self.batches = 0
            self.norms_pre, self.norms_post = [], []

        def on_train_batch_end(self, batch: int, logs: Any = None) -> None:
            clip, _ = self._vars()
            self.batches += 1
            self.norms_pre.append(float(clip["pre"].numpy()))
            self.norms_post.append(float(clip["post"].numpy()))

        def on_epoch_end(self, epoch: int, logs: Any = None) -> None:
            clip, batch = self._vars()
            opt = self.model.optimizer
            pre = np.asarray(self.norms_pre)
            post = np.asarray(self.norms_post)
            es = [cb for cb in callbacks if type(cb).__name__ == "EarlyStopping"]
            es_state = None
            if es:
                cb = es[0]
                es_state = {"wait": int(cb.wait), "best": jsonable(cb.best),
                            "best_epoch": int(getattr(cb, "best_epoch", -1)),
                            "stopped_epoch": int(cb.stopped_epoch),
                            "model_stop_training": bool(self.model.stop_training)}
            record["epochs"].append({
                "epoch": int(epoch),
                "logs": jsonable(dict(logs or {})),
                "learning_rate_end": float(tf.keras.backend.get_value(opt.learning_rate)),
                "train_batches": self.batches,
                "optimizer_updates": int(opt.iterations.numpy()) - self.epoch_iter0,
                "examples": int(batch["rows"].numpy()) - self.epoch_rows0,
                "last_batch_rows": int(batch["last"].numpy()),
                "clip_calls_total": int(clip["calls"].numpy()),
                "grad_global_norm_pre_clip": {
                    "mean": float(pre.mean()) if pre.size else None,
                    "max": float(pre.max()) if pre.size else None,
                    "min": float(pre.min()) if pre.size else None,
                    "frac_above_1": float((pre > 1.0).mean()) if pre.size else None,
                    "first5": [float(x) for x in pre[:5]]},
                "grad_global_norm_post_clip_max": float(post.max()) if post.size else None,
                "clip_changed_norm_in_any_update": bool(
                    np.any(np.abs(pre - post) > 1e-6 * np.maximum(1.0, pre))) if pre.size
                else None,
                "early_stopping_state": es_state,
                "weights_digest_after_epoch": _weights_digest(np, self.model)["digest"],
                "seconds": time.perf_counter() - self.epoch_t0,
            })

        def on_train_end(self, logs: Any = None) -> None:
            digest = _weights_digest(np, self.model)["digest"]
            matches = [e["epoch"] for e in record["epochs"]
                       if e["weights_digest_after_epoch"] == digest]
            val = [e["logs"].get("val_loss") for e in record["epochs"]]
            best = (int(np.nanargmin(np.asarray(val, dtype=float)))
                    if val and all(v is not None for v in val) else None)
            record["at_train_end"] = {
                "weights_digest": digest,
                "weights_equal_end_of_epoch": matches,
                "epochs_run": len(record["epochs"]),
                "val_loss_argmin_epoch": best,
                "final_weights_are_best_val_epoch": (best in matches) if best is not None
                else None,
                "final_weights_are_last_epoch": bool(record["epochs"]) and
                (record["epochs"][-1]["epoch"] in matches),
            }
            audit.end_digest_by_step[record["step"]] = digest

    return Recorder()


def install_keras_instrumentation(tf: Any, np: Any, audit: Audit) -> dict[str, Any]:
    """Class-level wrappers on Keras `Model.fit` and the optimizer's clipping step."""
    import keras  # the Keras TF bundles; recorded, not chosen

    model_cls = tf.keras.Model
    original_fit = model_cls.fit

    # The optimizer base that owns `_clip_gradients` (Keras 2.15: `_BaseOptimizer`).
    owner = None
    for klass in tf.keras.optimizers.Adam.__mro__:
        if "_clip_gradients" in vars(klass):
            owner = klass
            break
    if owner is None:
        raise RuntimeError("no optimizer class in Adam's MRO defines _clip_gradients")
    original_clip = owner._clip_gradients

    def clip_wrapper(self: Any, grads: Any) -> Any:
        slot = audit.clip_vars.get(id(self))
        clipped = original_clip(self, grads)
        if slot is not None:
            pre = tf.linalg.global_norm([g for g in grads if g is not None])
            post = tf.linalg.global_norm([g for g in clipped if g is not None])
            slot["pre"].assign(tf.cast(pre, tf.float32))
            slot["post"].assign(tf.cast(post, tf.float32))
            slot["calls"].assign_add(1)
        return clipped

    owner._clip_gradients = clip_wrapper

    def patch_train_step(cls: type) -> None:
        if cls in audit.patched_train_step:
            return
        original_step = cls.train_step

        def train_step(self: Any, data: Any) -> Any:
            slot = audit.batch_vars.get(id(self))
            if slot is not None:
                x, y = data[0], data[1]
                first = tf.nest.flatten(x)[0]
                rows = tf.cast(tf.shape(first)[0], tf.int64)
                slot["rows"].assign_add(rows)
                slot["last"].assign(rows)
                slot["wsum"].assign_add(tf.reduce_sum(tf.cast(y[:, 1], tf.float64)))
            return original_step(self, data)

        cls.train_step = train_step
        audit.patched_train_step.add(cls)

    def fit(self: Any, *args: Any, **kwargs: Any) -> Any:
        ctx = dict(audit.context)
        callbacks = list(kwargs.get("callbacks") or [])
        record: dict[str, Any] = {
            "arm": audit.arm, "iteration": ctx.get("iteration"), "step": ctx.get("stepn"),
            "model_class": class_provenance(type(self)),
            "model_id": id(self),
            "model_is_template": id(self) in (audit.multifold.get("model1_id"),
                                                 audit.multifold.get("model2_id")),
            "model_seen_before_in_fit": id(self) in audit.seen_model_ids,
            "optimizer_id": id(self.optimizer),
            "optimizer_seen_before": id(self.optimizer) in audit.seen_optimizer_ids,
            "fit_kwargs": {k: jsonable(v) for k, v in kwargs.items()
                           if k in ("epochs", "steps_per_epoch", "validation_steps",
                                    "verbose", "batch_size", "shuffle")},
            "train_element_spec": repr(getattr(args[0] if args else kwargs.get("x"),
                                               "element_spec", None)),
            "callbacks": _callback_facts(callbacks),
        }
        audit.seen_model_ids[id(self)] = audit.seen_model_ids.get(id(self), 0) + 1
        audit.seen_optimizer_ids.append(id(self.optimizer))
        patch_train_step(type(self))
        recorder = make_recorder(tf, np, audit, record, callbacks)
        kwargs["callbacks"] = callbacks + [recorder]
        t0 = time.perf_counter()
        history = original_fit(self, *args, **kwargs)
        record["fit_seconds"] = time.perf_counter() - t0
        record["history"] = jsonable(history.history)
        record["weights_after_fit_return"] = _weights_digest(np, self)["digest"]
        audit.fits.append(record)
        return history

    model_cls.fit = fit
    return {"fit_owner": class_provenance(model_cls)[0],
            "clip_owner": {"qualname": owner.__qualname__, "module": owner.__module__,
                           "source_file": inspect.getsourcefile(owner)},
            "keras_version": getattr(keras, "__version__", None),
            "tensorflow_version": tf.__version__}


def multifold_callback(tf: Any, np: Any, audit: Audit):
    """Returns the post-import callback that wraps `omnifold.omnifold.MultiFold`."""

    def patch(module: Any) -> None:
        MultiFold = module.MultiFold
        audit.multifold["class"] = class_provenance(MultiFold)
        orig_init = MultiFold.__init__
        orig_cache = MultiFold.cache
        orig_run = MultiFold.RunModel
        orig_compile = MultiFold.CompileModel
        orig_reweight = MultiFold.reweight

        def __init__(self: Any, *a: Any, **kw: Any) -> None:
            orig_init(self, *a, **kw)
            audit.multifold.update({
                "instance_class": class_provenance(type(self)),
                "BATCH_SIZE": int(self.BATCH_SIZE), "EPOCHS": int(self.EPOCHS),
                "LR": float(self.LR), "patience": int(self.patience),
                "train_frac": float(self.train_frac), "niter": int(self.niter),
                "n_ensemble": int(self.n_ensemble),
                "num_steps_reco": int(self.num_steps_reco),
                "num_steps_gen": int(self.num_steps_gen),
                "mc_nmax": int(self.mc.nmax), "data_nmax": int(self.data.nmax),
                "model1_id": id(self.model1), "model2_id": id(self.model2),
                "model1_class": type(self.model1).__qualname__,
                "model2_class": type(self.model2).__qualname__,
                "model1_pretrained_attribute": jsonable(getattr(self.model1, "pretrained",
                                                                "ABSENT")),
            })

        def cache(self: Any, label: Any, weights: Any, stepn: int, cached: bool,
                  NTRAIN: int) -> Any:
            entry = {"iteration": audit.context.get("iteration"), "step": int(stepn),
                     "cached_flag": bool(cached), "train_take": int(NTRAIN),
                     "rows": int(len(label)),
                     "np_random_state_before": np_random_state_digest(np),
                     "python_random_state_before": python_random_state_digest()}
            w = np.asarray(weights, dtype=np.float64)
            lab = np.asarray(label)
            entry["weights_label0"] = weights_summary(np, w[lab == 0])
            entry["weights_label1"] = weights_summary(np, w[lab == 1])
            out = orig_cache(self, label, weights, stepn, cached, NTRAIN)
            idx = np.asarray(self.idx_1 if stepn == 1 else self.idx_2)
            entry["idx_digest"] = hashlib.sha256(idx.astype(np.int64).tobytes()).hexdigest()
            val_rows = np.sort(idx[int(NTRAIN):]).astype(np.int64)
            entry["validation_rows"] = int(val_rows.size)
            entry["validation_row_set_digest"] = hashlib.sha256(val_rows.tobytes()).hexdigest()
            entry["np_random_state_after"] = np_random_state_digest(np)
            entry["train_element_spec"] = repr(out[0].element_spec)
            audit.caches.append(entry)
            key = f"step{stepn}"
            if not cached and key not in audit.inputs:
                audit.inputs[key] = describe_inputs(np, self, stepn, audit.arm)
            return out

        def RunModel(self: Any, labels: Any, weights: Any, iteration: int, model: Any,
                     stepn: int, NTRAIN: int = 1000, cached: bool = False) -> Any:
            prev = dict(audit.context)
            audit.context = {"iteration": int(iteration), "stepn": int(stepn),
                             "NTRAIN": int(NTRAIN)}
            t0 = time.perf_counter()
            try:
                return orig_run(self, labels, weights, iteration, model, stepn, NTRAIN, cached)
            finally:
                audit.context = prev
                audit.caches[-1]["runmodel_seconds"] = time.perf_counter() - t0

        def CompileModel(self: Any, model: Any, num_steps: Any, fixed: bool = False) -> Any:
            out = orig_compile(self, model, num_steps, fixed)
            audit.compiles.append({
                "context": dict(audit.context), "model_id": id(model),
                "model_is_template": id(model) in (id(self.model1), id(self.model2)),
                "fixed_argument_seen_by_base": bool(fixed),
                "num_steps_argument": jsonable(num_steps),
                "optimizer": _optimizer_facts(tf, model.optimizer)})
            return out

        def reweight(self: Any, events: Any, model: Any, batch_size: Any = None) -> Any:
            out = orig_reweight(self, events, model, batch_size)
            audit.reweights.append({"iteration": audit.context.get("iteration"),
                                    "which": "step1" if model is self.model1 else "step2",
                                    "batch_size_argument": batch_size,
                                    "weights": weights_summary(np, out)})
            return out

        MultiFold.__init__ = __init__
        MultiFold.cache = cache
        MultiFold.RunModel = RunModel
        MultiFold.CompileModel = CompileModel
        MultiFold.reweight = reweight

    return patch


def describe_inputs(np: Any, mf: Any, stepn: int, arm: str) -> dict[str, Any]:
    """The arrays `cache` hands to `from_tensor_slices`, described column by column."""
    ffd = sys.modules.get("fullevent_fps_dataloader")
    tts = sys.modules.get("theirs_token_schema")
    if stepn == 1:
        cloud = np.concatenate([mf.mc.reco, mf.data.reco], 0)
        evt = (np.concatenate([mf.mc.reco_evt, mf.data.reco_evt], 0)
               if getattr(mf.mc, "reco_evt", None) is not None else None)
        if arm == "theirs":
            names = (list(getattr(tts, "TOKEN_COLUMNS", ())) +
                     list(getattr(tts, "ADD_INFO_COLUMNS", ()))) if tts else None
            evt_names = None
        else:
            names = list(getattr(ffd, "RECO_CLOUD_COLS", ())) if ffd else None
            evt_names = list(getattr(ffd, "DEFAULT_EVT_FEATURES", ())) if ffd else None
    else:
        cloud = np.asarray(mf.mc.gen)
        evt = np.asarray(mf.mc.gen_evt) if getattr(mf.mc, "gen_evt", None) is not None else None
        names = ["E", "px", "py", "pz", "pdg", "theta", "cos_phi", "sin_phi"]
        evt_names = list(getattr(ffd, "DEFAULT_TRUTH_EVT_FEATURES", ())) if ffd else None
    out = {"cloud": column_stats(np, cloud, names),
           "cloud_digest": hashlib.sha256(np.ascontiguousarray(cloud).tobytes()).hexdigest(),
           "event": column_stats(np, evt, evt_names) if evt is not None else None,
           "event_digest": (hashlib.sha256(np.ascontiguousarray(evt).tobytes()).hexdigest()
                            if evt is not None else None),
           "cloud_column_names_source": (
               "theirs_token_schema.TOKEN_COLUMNS + ADD_INFO_COLUMNS"
               if (arm == "theirs" and stepn == 1) else
               "fullevent_fps_dataloader.RECO_CLOUD_COLS" if stepn == 1 else
               "fullevent_fps_dataloader.build_truth_cloud docstring layout")}
    if stepn == 1 and arm == "theirs":
        pid_codes = dict(getattr(tts, "PID_CODES", {})) if tts else None
        out["theirs_semantics"] = theirs_token_semantics(np, cloud, pid_codes)
    return out


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def build_args(cli: argparse.Namespace) -> argparse.Namespace:
    """The historical driver's own argument namespace, as its launcher would build it."""
    return argparse.Namespace(
        arm=cli.arm, seed=cli.seed, stage=cli.stage, learning_rate=cli.learning_rate,
        niter=cli.niter, output=cli.out_dir / f"historical_receipt_{cli.arm}.json",
        dry_run=False, repo=cli.historical_repo, inputs_npz=cli.inputs_npz,
        theirs_index=cli.theirs_index,
        weights_folder=cli.out_dir / cli.arm / "weights", max_events=cli.max_events,
        theirs_state_npz=cli.theirs_state_npz if cli.arm == "theirs" else None,
        theirs_manifest=cli.theirs_manifest if cli.arm == "theirs" else None,
        identity_sidecar=cli.identity_sidecar, theirs_cache=cli.theirs_cache,
        half_size=None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--historical-repo", type=Path, required=True,
                        help="checkout pinned to the historical commit (clean)")
    parser.add_argument("--tree-listing", type=Path, required=True,
                        help="`git ls-tree -r` of the historical commit")
    parser.add_argument("--arm", choices=("ours", "theirs"), required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--stage", choices=("tuning", "pilot", "final"), required=True)
    parser.add_argument("--learning-rate", type=float, required=True)
    parser.add_argument("--niter", type=int, default=3)
    parser.add_argument("--max-events", type=int, required=True)
    parser.add_argument("--inputs-npz", type=Path, required=True)
    parser.add_argument("--theirs-index", type=Path, required=True)
    parser.add_argument("--theirs-cache", type=Path, default=None)
    parser.add_argument("--theirs-state-npz", type=Path, required=True)
    parser.add_argument("--theirs-manifest", type=Path, required=True)
    parser.add_argument("--identity-sidecar", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--label-root", action="append", default=[],
                        help="LABEL=PATH for the module provenance table")
    cli = parser.parse_args()

    repo = cli.historical_repo.resolve()
    tree = parse_tree_listing(cli.tree_listing.read_text())
    labels = {str(repo): "historical_checkout_68cf9d29"}
    for item in cli.label_root:
        label, _eq, path = item.partition("=")
        labels[str(Path(path).resolve())] = label
    cli.out_dir.mkdir(parents=True, exist_ok=True)
    (cli.out_dir / cli.arm).mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    sys_path_before = list(sys.path)

    # TensorFlow is imported here, before the driver's own first import of it (inside
    # `configure_production_precision`). On Perlmutter's tensorflow/2.15.0 there is no tf_keras
    # shim, so the backend choice `keras_backend.select_keras_backend` makes is the same either
    # way; this is recorded below rather than assumed.
    from numpy_probe import disable_numpy_sve_probe

    numpy_probe = disable_numpy_sve_probe()
    import numpy as np
    import tensorflow as tf

    audit = Audit(cli.arm, cli.theirs_state_npz if cli.arm == "theirs" else None)
    keras_info = install_keras_instrumentation(tf, np, audit)
    hook = PostImportHook({"omnifold.omnifold": multifold_callback(tf, np, audit)})
    sys.meta_path.insert(0, hook)

    # The driver as its launcher runs it: its own directory first on sys.path.
    driver_dir = repo / "nd-unfolding" / "pet" / "configuration_comparison"
    sys.path.insert(0, str(driver_dir))
    import run_arm_evaluation as rae  # noqa: E402  (resolved from the pinned checkout)

    args = build_args(cli)
    receipt = None
    error = None
    try:
        receipt = rae.evaluate(args)
    except BaseException as exc:  # noqa: BLE001 - recorded, then re-raised after writing
        error = f"{type(exc).__name__}: {exc}"
        raise_later = exc
    else:
        raise_later = None
    finally:
        record = {
            "schema": "pet-improvement-A1-runtime-audit-v1",
            "historical_commit": HISTORICAL_COMMIT,
            "historical_repo": str(repo),
            "arm": cli.arm, "seed": cli.seed, "stage": cli.stage,
            "learning_rate_argument": cli.learning_rate, "niter": cli.niter,
            "max_events": cli.max_events,
            "driver_module_file": getattr(rae, "__file__", None),
            "evaluate_source_file": inspect.getsourcefile(rae.evaluate),
            "post_import_hooks_fired": hook.fired,
            "numpy_sve_probe": numpy_probe,
            "keras_instrumentation": keras_info,
            "environment": {k: os.environ.get(k) for k in (
                "TF_DETERMINISTIC_OPS", "NVIDIA_TF32_OVERRIDE", "TF_USE_LEGACY_KERAS",
                "CUBLAS_WORKSPACE_CONFIG", "SLURM_JOB_ID", "PYTHONDONTWRITEBYTECODE")},
            "sys_path_before_driver": sys_path_before,
            "sys_path_after_run": list(sys.path),
            "multifold": audit.multifold,
            "compiles": audit.compiles,
            "caches": audit.caches,
            "fits": audit.fits,
            "reweights": audit.reweights,
            "inputs": audit.inputs,
            "historical_receipt": receipt,
            "error": error,
            "wall_seconds": time.perf_counter() - started,
            "module_provenance": module_provenance(dict(sys.modules), tree, labels),
            "input_files": {
                "inputs_npz": str(cli.inputs_npz),
                "theirs_state_npz_sha256": (sha256_of(cli.theirs_state_npz)
                                            if cli.arm == "theirs" else None),
                "identity_sidecar": str(cli.identity_sidecar),
                "theirs_cache": str(cli.theirs_cache) if cli.theirs_cache else None},
        }
        out = cli.out_dir / f"runtime_audit_{cli.arm}.json"
        out.write_text(json.dumps(record, indent=1, default=repr) + "\n")
        print(f"[audit] wrote {out}")
    if raise_later is not None:
        raise raise_later
    return 0


if __name__ == "__main__":
    sys.exit(main())
