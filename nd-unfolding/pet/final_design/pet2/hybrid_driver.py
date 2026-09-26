"""Hybrid PET OmniFold driver: PET2-small (pretrained or scratch) at step 1, our truth PET at step 2.

The predecessor's replicate path trains our PET at both steps (`phase_b/pet/b2_driver.B2MultiFold`,
reached from `confirm/run_replicate.py`, which refuses any arm but `ours`). This module adapts that
driver WITHOUT editing it: `HybridMultiFold` subclasses `B2MultiFold`, so everything the predecessor
verified is inherited unchanged --

* the A1 recipe driver (`run_unfold.RecipeMultiFold`): per-step `StepRecipe` (optimizer family,
  TorchAdamW weight decay, torch-style global-norm clip, warmup fraction + cosine schedule, batch,
  epochs, split, init, iteration rate), the check that the EXECUTED optimizer is the declared one
  (the run refuses otherwise), the per-epoch recorder that refuses a fit whose executed epoch
  differs from the recipe, and, for the pretrained policy, the recorder's own first-step check;
* B2's per-step seeding (`seed_step`: every fit depends only on its own (step seed, step,
  iteration), so the two steps' random streams are decoupled), the efficiency-corrected step 2,
  per-iteration `iterations/iterNN.npz` (pull, push over every prior row) and `modelsNN.npz`,
  bit-exact resume and the deadline.

What is added:

* **step-1 inputs are PET2's** (`substitute_theirs`): the reco cloud and event block of the
  pseudodata and the prior are replaced by PET2's packed tokens and globals for the SAME rows
  (`theirs_rows.py`), after the row alignment is checked; step 2 keeps our truth inputs (with the
  config's B2 input arm, which may not touch step 1);
* **an initialization verification at the first optimizer step of every freshly built step-1
  model** (`InitVerifier`): the 176 backbone tensors are digested and compared with the exported
  pretrained state `2480f269...`. Pretrained variant: all 176 must equal it. Scratch variant: every
  tensor must differ from it except tensors whose exported value is a constant fill (the signature
  of a deterministic initializer that pretraining never moved -- measured: 5 such tensors, the
  conditional-embedding biases/norm and the output bias; they start identical in both variants
  by construction). A violation raises before the first update; the record goes to
  `init_verification.json` and the receipt;
* **measurements**: step-1 per-epoch wall time, training-only time and steady-state throughput
  (examples/s, excluding the first batches of the epoch), and the TensorFlow allocator's peak GPU
  memory per OmniFold step (fit + reweight), appended to `resources.jsonl` and the fit records.

PET is diagnostic method development; simulation only.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
import weakref
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

import numpy as np

SCHEMA = "pet-final-design-hybrid-driver/1"
EXPECT = ("pretrained", "scratch")
STEADY_SKIP_BATCHES = 10


# ------------------------------------------------------------------------------------------- #
# Configuration checks (no TensorFlow)
# ------------------------------------------------------------------------------------------- #
def variant_of(config: Any) -> str:
    return "pretrained" if config.step1.init.policy == "pretrained" else "scratch"


def check_hybrid_config(config: Any, b2_arm: Any, pinned_state_sha256: str) -> dict[str, Any]:
    """Refuse a config that is not a PET2-step-1 / our-PET-step-2 hybrid, before any data."""
    problems = []
    if config.arm != "theirs" or config.model_step1.kind != "theirs_pet2_small":
        problems.append(f"step 1 must be PET2-small on its own inputs (arm {config.arm!r}, model "
                        f"{config.model_step1.kind!r})")
    if config.model_step2.kind != "ours_pet":
        problems.append("step 2 must be our truth PET")
    if b2_arm.step1_reco_scalars or b2_arm.step1_cloud_summaries:
        problems.append(f"B2 arm {b2_arm.name!r} changes step-1 inputs; PET2's inputs are fixed")
    init = config.step1.init
    if init.policy == "pretrained" and init.pretrained_state_sha256 != pinned_state_sha256:
        problems.append(f"pretrained state sha256 {init.pretrained_state_sha256} is not the pinned "
                        f"export {pinned_state_sha256}")
    if problems:
        raise SystemExit(f"[pet2] not a PET2 hybrid config: {problems}")
    return {"variant": variant_of(config), "step1_model": config.model_step1.kind,
            "step2_model": config.model_step2.kind, "b2_arm": b2_arm.name,
            "pinned_state_sha256": pinned_state_sha256}


# ------------------------------------------------------------------------------------------- #
# Initialization verification (numpy; the model side is a list of (name, array))
# ------------------------------------------------------------------------------------------- #
def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def compare_init(named_live: Iterable[tuple[str, np.ndarray]],
                 reference: Mapping[str, np.ndarray], expect: str) -> dict[str, Any]:
    """Per-tensor digests of the live model against the exported state, and the verdict."""
    if expect not in EXPECT:
        raise ValueError(f"expect {expect!r}")
    live = list(named_live)
    names = [n for n, _ in live]
    tensors: dict[str, Any] = {}
    for name, value in live:
        value = np.asarray(value)
        entry: dict[str, Any] = {"shape": list(value.shape), "model_sha256": _sha(value)}
        if name in reference:
            ref = np.asarray(reference[name]).astype(value.dtype)
            entry["reference_sha256"] = _sha(ref)
            entry["equal"] = bool(ref.shape == value.shape and entry["reference_sha256"]
                                  == entry["model_sha256"])
            entry["reference_constant"] = bool(ref.size and np.all(ref == ref.flat[0]))
        tensors[name] = entry
    missing_in_reference = sorted(set(names) - set(reference))
    missing_in_model = sorted(set(reference) - set(names))
    compared = [t for t in tensors.values() if "equal" in t]
    equal = [n for n, t in tensors.items() if t.get("equal")]
    differ = [n for n, t in tensors.items() if "equal" in t and not t["equal"]]
    equal_nonconstant = [n for n in equal if not tensors[n]["reference_constant"]]
    coverage_ok = not missing_in_reference and not missing_in_model and len(set(names)) == \
        len(names) == len(reference)
    if expect == "pretrained":
        ok = coverage_ok and len(equal) == len(reference)
        rule = "every model tensor equals the exported pretrained tensor (176/176)"
    else:
        ok = coverage_ok and not equal_nonconstant and len(differ) > 0
        rule = ("every model tensor differs from the exported pretrained tensor, except tensors "
                "whose exported value is a constant fill (a deterministic initializer "
                "pretraining left unchanged)")
    return {"expect": expect, "rule": rule, "ok": bool(ok),
            "tensors_in_model": len(names), "tensors_in_reference": len(reference),
            "compared": len(compared), "equal": len(equal), "differ": len(differ),
            "equal_names": equal, "equal_nonconstant_names": equal_nonconstant,
            "missing_in_reference": missing_in_reference, "missing_in_model": missing_in_model,
            "parameters": int(sum(int(np.prod(t["shape"])) for t in tensors.values())),
            "model_digest": hashlib.sha256("".join(t["model_sha256"] for t in tensors.values())
                                           .encode()).hexdigest(),
            "tensors": tensors}


class InitVerifier:
    """Compares a PET2 model's backbone with the exported pretrained state."""

    def __init__(self, reference_npz: Path, reference_sha256: str, expect: str,
                 inventory: Callable[[Any], list[tuple[str, Any]]]) -> None:
        got = hashlib.sha256(Path(reference_npz).read_bytes()).hexdigest()
        if got != reference_sha256:
            raise SystemExit(f"[pet2] reference state sha256 {got} != {reference_sha256}")
        with np.load(reference_npz) as blob:
            self.reference = {k: blob[k] for k in blob.files}
        self.reference_npz, self.reference_sha256 = str(reference_npz), reference_sha256
        self.expect = expect
        self.inventory = inventory

    def check(self, model: Any) -> dict[str, Any]:
        named = [(n, v.numpy()) for n, v in self.inventory(model)]
        out = compare_init(named, self.reference, self.expect)
        out.update({"reference_npz": self.reference_npz,
                    "reference_sha256": self.reference_sha256})
        return out


# ------------------------------------------------------------------------------------------- #
# Step-1 input substitution
# ------------------------------------------------------------------------------------------- #
def substitute_theirs(inputs: Any, theirs: Mapping[str, Any]) -> dict[str, Any]:
    """Replace the step-1 reco cloud/event block of the pseudodata and the prior by PET2's.

    `theirs["pdata"]` / `theirs["prior"]` must have been gathered for exactly `inputs.pdata["rows"]`
    / `inputs.mc["rows"]` (checked by digest); nothing at step 2 is touched."""
    record: dict[str, Any] = {}
    for side, leg, block in (("pdata", "pdata", inputs.pdata), ("mc", "prior", inputs.mc)):
        rows = np.asarray(block["rows"], np.int64)
        if rows.size and np.any(np.diff(rows) <= 0):
            raise SystemExit(f"[pet2] {side} rows are not sorted; PET2 legs are gathered sorted")
        want = hashlib.sha256(rows.tobytes()).hexdigest()
        if theirs["legs"][leg]["rows_sha256"] != want:
            raise SystemExit(f"[pet2] PET2 {leg} leg was gathered for other rows")
        packed, glob = theirs[leg]["packed"], theirs[leg]["globals"]
        if packed.shape[0] != rows.size or glob.shape[0] != rows.size:
            raise SystemExit(f"[pet2] PET2 {leg} leg has the wrong length")
        record[side] = {"rows": int(rows.size), "rows_sha256": want,
                        "replaced": {"reco": [list(np.shape(block["reco"])), list(packed.shape)],
                                     "reco_evt": [list(np.shape(block["reco_evt"])),
                                                  list(glob.shape)]},
                        "packed_sha256": _sha(packed), "globals_sha256": _sha(glob)}
        block["reco"], block["reco_evt"] = packed, glob
    gen_before = _sha(np.asarray(inputs.mc["gen"]))
    record["step2_inputs_untouched"] = {"mc_gen_sha256": gen_before}
    inputs.meta["coord_reco"] = None
    inputs.meta["step1_inputs"] = "PET2-small packed tokens (33 x 10) + 16 globals"
    return record


# ------------------------------------------------------------------------------------------- #
# The engine subclass
# ------------------------------------------------------------------------------------------- #
def make_hybrid_multifold(MultiFold: type, tf: Any, np_: Any) -> type:
    import b2_driver as b2d
    B2 = b2d.make_b2_multifold(MultiFold, tf, np_)

    class HybridMultiFold(B2):
        def __init__(self, *a: Any, init_verifier: InitVerifier, **k: Any) -> None:
            super().__init__(*a, **k)
            self.init_verifier = init_verifier
            self.init_path = self.out_dir / "init_verification.json"
            self.init_records: list[dict[str, Any]] = (
                json.loads(self.init_path.read_text()) if self.init_path.exists() else [])
            self.resources_path = self.out_dir / "resources.jsonl"
            self._fit_context: dict[str, Any] | None = None
            self._restoring = False
            self.gpu_device = "GPU:0"
            base = self.factories[1]
            self.factories = dict(self.factories)
            self.factories[1] = self._instrumented(base)

        # ---- step-1 models carry the verification and the meter ---------------------- #
        def _instrumented(self, base: Callable[[], Any]) -> Callable[[], Any]:
            driver = weakref.ref(self)
            classes: dict[type, type] = {}

            def factory() -> Any:
                model = base()
                cls = type(model)
                if cls not in classes:
                    class Instrumented(cls):  # type: ignore[misc, valid-type]
                        def fit(self, *a: Any, callbacks: Any = None, **k: Any) -> Any:
                            extra = driver().step1_callbacks(self)
                            return super().fit(*a, callbacks=list(callbacks or []) + extra, **k)
                    Instrumented.__qualname__ = f"Instrumented[{cls.__qualname__}]"
                    classes[cls] = Instrumented
                model.__class__ = classes[cls]
                model._pfd_restored = self._restoring
                return model

            return factory

        def step1_callbacks(self, model: Any) -> list[Any]:
            ctx = self._fit_context or {}
            out = [self._meter_callback(ctx)]
            if ctx.get("fresh") and not getattr(model, "_pfd_restored", False):
                out.insert(0, self._init_callback(ctx))
            return out

        def _init_callback(self, ctx: dict[str, Any]) -> Any:
            driver = self

            class FirstStepInitCheck(tf.keras.callbacks.Callback):
                fired = False

                def on_train_batch_begin(self, batch: int, logs: Any = None) -> None:
                    if self.fired:
                        return
                    self.fired = True
                    record = driver.init_verifier.check(self.model)
                    record.update({"iteration": ctx["iteration"], "step": 1,
                                   "optimizer_iterations": int(
                                       self.model.optimizer.iterations.numpy()),
                                   "checked_at": "on_train_batch_begin of batch 0 (before the "
                                                 "first optimizer update of a freshly built "
                                                 "model)",
                                   "slurm_job_id": __import__("os").environ.get("SLURM_JOB_ID")})
                    if record["optimizer_iterations"] != 0:
                        record["ok"] = False
                        record["problem"] = "optimizer already stepped"
                    driver.init_records.append(record)
                    tmp = driver.init_path.with_suffix(".json.tmp")
                    tmp.write_text(json.dumps(driver.init_records, indent=1) + "\n")
                    tmp.replace(driver.init_path)
                    brief = {k: record[k] for k in ("expect", "ok", "compared", "equal", "differ")}
                    driver.log_string(f"[pet2] init verification at the first step: {brief}")
                    if not record["ok"]:
                        raise RuntimeError(f"[pet2] step-1 initialization is not the declared "
                                           f"{record['expect']} state: {brief} "
                                           f"{record['equal_nonconstant_names'][:5]}")

            return FirstStepInitCheck()

        def _meter_callback(self, ctx: dict[str, Any]) -> Any:
            n_train, batch = int(ctx.get("n_train", 0)), int(ctx.get("batch_size", 1))
            driver = self

            class ThroughputMeter(tf.keras.callbacks.Callback):
                def __init__(self) -> None:
                    super().__init__()
                    self.epochs: list[dict[str, Any]] = []

                def on_epoch_begin(self, epoch: int, logs: Any = None) -> None:
                    self.t0 = time.perf_counter()
                    self.ends: list[float] = []

                def on_train_batch_end(self, batch_i: int, logs: Any = None) -> None:
                    self.ends.append(time.perf_counter())

                def on_epoch_end(self, epoch: int, logs: Any = None) -> None:
                    t1 = time.perf_counter()
                    n = len(self.ends)
                    sizes = [batch] * max(n - 1, 0) + [n_train - batch * (n - 1)] if n else []
                    skip = min(STEADY_SKIP_BATCHES, max(n - 2, 0))
                    window = self.ends[-1] - self.ends[skip] if n > skip + 1 else float("nan")
                    examples = sum(sizes[skip + 1:])
                    self.epochs.append({
                        "epoch": int(epoch), "batches": n, "batch_size": batch,
                        "examples": int(sum(sizes)),
                        "train_seconds": (self.ends[-1] - self.t0) if n else None,
                        "epoch_seconds_incl_validation": t1 - self.t0,
                        "steady_window_batches": max(n - skip - 1, 0),
                        "steady_examples_per_second": (examples / window
                                                       if window and window > 0 else None),
                        "train_examples_per_second": (sum(sizes) / (self.ends[-1] - self.t0)
                                                      if n else None)})

                def on_train_end(self, logs: Any = None) -> None:
                    driver._last_meter = self.epochs

            return ThroughputMeter()

        # ---- one fit ------------------------------------------------------------------ #
        def RunModel(self, labels: Any, weights: Any, iteration: int, model: Any, stepn: int,
                     NTRAIN: Any = None, cached: bool = False) -> None:
            step = self.step_recipe(stepn)
            models = self.step1_models if stepn == 1 else self.step2_models
            fresh = (iteration == 0 or step.init.across_iterations == "reinitialize"
                     or not models)
            train, _val = self._split(stepn, len(labels), iteration)
            self._fit_context = {"step": stepn, "iteration": int(iteration), "fresh": bool(fresh),
                                 "n_train": int(len(train)), "batch_size": int(step.batch_size)}
            self._last_meter = None
            try:
                super().RunModel(labels, weights, iteration, model, stepn, NTRAIN=NTRAIN,
                                 cached=cached)
            finally:
                self._fit_context = None
            if stepn == 1 and self._last_meter is not None:
                self.fit_records[-1]["step1_throughput"] = self._last_meter

        # ---- per-step GPU memory and wall time ---------------------------------------- #
        def _measured(self, stepn: int, i: int, run: Callable[[int], None]) -> None:
            try:
                tf.config.experimental.reset_memory_stats(self.gpu_device)
                can = True
            except Exception:  # noqa: BLE001  (no GPU: CPU tests)
                can = False
            t0 = time.perf_counter()
            run(i)
            record = {"iteration": int(i), "step": stepn, "seconds": time.perf_counter() - t0,
                      "gpu_peak_bytes": None, "gpu_current_bytes": None}
            if can:
                info = tf.config.experimental.get_memory_info(self.gpu_device)
                record.update({"gpu_peak_bytes": int(info["peak"]),
                               "gpu_current_bytes": int(info["current"])})
            with self.resources_path.open("a") as handle:
                handle.write(json.dumps(record) + "\n")
            self.log_string(f"[pet2] step {stepn} iteration {i}: {record}")

        def RunStep1(self, i: int) -> None:
            self._measured(1, i, super().RunStep1)

        def RunStep2(self, i: int) -> None:
            self._measured(2, i, super().RunStep2)

        # ---- resume: restored models are not freshly initialized ---------------------- #
        def _restore(self) -> int:
            self._restoring = True
            try:
                return super()._restore()
            finally:
                self._restoring = False

    return HybridMultiFold


# ------------------------------------------------------------------------------------------- #
# Receipt helpers
# ------------------------------------------------------------------------------------------- #
def recipe_audit(ru: Any, config: Any, fit_records: list[dict[str, Any]]) -> dict[str, Any]:
    """Every fit's executed optimizer re-verified against its declaration, and the declaration
    against the config's step recipe; every epoch's recorder verdict."""
    fits = []
    for fit in fit_records:
        step = config.step1 if fit["step"] == 1 else config.step2
        declared, executed = fit["declared_optimizer"], fit["executed_optimizer"]
        problems = list(ru.verify_executed_optimizer(executed, declared))
        base = step.iteration_lr.base_rate(step.optimizer.learning_rate, fit["iteration"])
        for key, want in (("family", step.optimizer.family), ("schedule", step.schedule.kind),
                          ("clipping", step.clipping.kind), ("max_norm", step.clipping.max_norm),
                          ("weight_decay", step.optimizer.weight_decay)):
            if declared[key] != want:
                problems.append(f"declared {key} {declared[key]} != config {want}")
        if not math.isclose(declared["base_learning_rate"], base, rel_tol=1e-12):
            problems.append("declared base rate differs from the config")
        epochs = fit["recorder"].get("epochs", [])
        violations = [e["recipe_violations"] for e in epochs if e.get("recipe_violations")]
        fits.append({"step": fit["step"], "iteration": fit["iteration"],
                     "class": executed["class"], "declared": declared,
                     "batch_size": fit["batch_size"], "updates_per_epoch":
                         fit["updates_per_epoch"], "epochs_run": len(epochs),
                     "torch_clip_events": [e.get("torch_clip_events") for e in epochs],
                     "lr_first_update": [e.get("lr_first_update") for e in epochs],
                     "lr_last_update": [e.get("lr_last_update") for e in epochs],
                     "problems": problems, "recorder_violations": violations,
                     "restore_executed_as_declared":
                         fit["recorder"].get("restore_executed_as_declared")})
    return {"fits": fits, "all_as_declared": all(not f["problems"] and not f["recorder_violations"]
                                                 for f in fits)}
