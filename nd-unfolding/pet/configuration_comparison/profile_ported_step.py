"""Where the ported arm's time and memory actually go, before optimising it further.

`COST_UPDATE2-20260919.md` measured the Keras port at **23.9x** our incumbent per
example in the same engine -- about 8.8x his own PyTorch for the same network --
and put the campaign at ~933 GPU-h against a 600 ceiling. That number says the
port is expensive. It does not say WHY, and three plausible causes have completely
different remedies:

* **the tape**, i.e. the backward pass materialising what an unfused forward left
  behind -- fixed by fusing or by recomputation;
* **the optimizer**, 176 separate variables through a Python-level clip and a
  hand-written AdamW -- fixed by vectorising the update, and cheap to check;
* **the local neighbourhood block**, which reshapes to ``(batch x tokens, K, dim)``
  and runs two transformers there -- his architecture, not our engine, and if it
  dominates then no amount of Keras work will close the gap.

Guessing which one it is, and then optimising for the guess, is the failure this
file exists to avoid. So it decomposes the step into forward / forward+backward /
apply, and reports peak device memory for each, per cell.

It also measures three things the decomposition cannot settle on its own:

* the **algebraic optimisations** already landed in `pet2_keras_port` (broadcast
  centre, broadcast key mask), against the pre-optimisation path they replaced --
  `test_port.OptimisationEquivalence` proves they are the same network bitwise, so
  any difference here is cost alone;
* **XLA**, which is the only fusion available to us in TF 2.15 -- there is no
  `scaled_dot_product_attention` to call;
* **gradient accumulation** at micro-batch 512, which is his own
  ``--grad_accum_steps`` knob and the memory unblock that keeps the recipe.

NOT CITABLE FOR any performance, recovery or adoption claim. This times and
measures memory; it trains nothing to convergence, reads no real source and
touches no matrix or validation receipt.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
import time
import traceback
from typing import Any

WARMUP = 5
REPEATS = 20

# His complete arm, as `configuration_identity.THEIRS_COMPLETE` pins it: PID,
# five auxiliary columns, sixteen globals. Costing the degraded arm would price a
# model we do not intend to run.
HIS_COMPLETE_SETTINGS = {
    "input_dim": 4, "pid": True, "pid_dim": 8, "add_info": True, "add_dim": 5,
    "conditional": True, "cond_dim": 16, "num_coord": 2, "K": 10, "num_classes": 1,
}
VARIANTS = ("baseline", "optimised", "optimised_xla", "accum4", "ours_incumbent")
MODES = ("forward", "train")


def _summarise(times: list[float], batch: int) -> dict[str, Any]:
    median = statistics.median(times)
    return {
        "repeats": len(times),
        "step_seconds_median": median,
        "step_seconds_min": min(times),
        "step_seconds_max": max(times),
        "coefficient_of_variation": (
            statistics.stdev(times) / statistics.mean(times) if len(times) > 1 else 0.0
        ),
        "batch": batch,
        "seconds_per_example": median / batch,
        "microseconds_per_example": 1e6 * median / batch,
    }


def _time(step_fn: Any, batch: int, tf: Any, warmup: int = WARMUP,
          repeats: int = REPEATS) -> dict[str, Any]:
    """Warm up, then time, then read peak device memory for THIS measurement.

    The peak counter is reset after warm-up so that graph construction and
    autotuning scratch do not land in the number, and read after the timed passes
    so it covers the steady state a real fit would sit in.
    """
    for _ in range(warmup):
        value = step_fn()
    try:
        tf.config.experimental.reset_memory_stats("GPU:0")
    except Exception:                                    # pragma: no cover - driver
        pass
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        value = step_fn()
        times.append(time.perf_counter() - start)
    memory = {}
    try:
        info = tf.config.experimental.get_memory_info("GPU:0")
        memory = {"peak_bytes": int(info["peak"]), "current_bytes": int(info["current"])}
    except Exception:                                    # pragma: no cover - driver
        memory = {"peak_bytes": None, "current_bytes": None}
    out = _summarise(times, batch)
    out["device_memory"] = memory
    out["value"] = float(value) if value is not None else None
    out["value_finite"] = bool(out["value"] is None or out["value"] == out["value"])
    return out


def _set_local_block_paths(port: Any, model: Any, *, materialise: bool, tile: bool) -> int:
    """Put every `LocalEmbeddingBlock` on the named path; return how many."""
    found, stack = 0, [model]
    while stack:
        layer = stack.pop()
        if isinstance(layer, port.LocalEmbeddingBlock):
            layer.materialise_pair_mask = materialise
            layer.tile_centre = tile
            found += 1
        stack.extend(getattr(layer, "_port_children", {}).values())
    return found


def _install(repo: Path) -> None:
    root = repo / "nd-unfolding" / "pet" / "configuration_comparison"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def measure_cell(repo: Path, variant: str, tokens: int, batch: int, mode: str,
                 micro_batch: int = 512, allow_cpu: bool = False,
                 warmup: int = WARMUP, repeats: int = REPEATS) -> dict[str, Any]:
    """One (variant, tokens, batch, mode) cell, decomposed.

    `allow_cpu` exists for smoke-testing this file's own code paths off-cluster
    and is recorded in the receipt, because a CPU reading of a GPU cost is not a
    weaker measurement of the same thing -- it is a measurement of something
    else, and nothing downstream may read it as a timing.
    """
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant {variant!r}")
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}")

    _install(repo)
    from keras_backend import record_versions, select_keras_backend

    backend = select_keras_backend()
    import numpy as np
    import tensorflow as tf

    gpus = tf.config.list_logical_devices("GPU")
    if not gpus and not allow_cpu:
        raise SystemExit("[profile] no GPU visible to TensorFlow (fail closed)")

    import pet2_keras_port as port
    import training_recipe as recipe

    rng = np.random.RandomState(0)
    record: dict[str, Any] = {
        "variant": variant, "tokens": tokens, "batch": batch, "mode": mode,
        "precision": "float32", "arm": "theirs_complete",
        "configuration": dict(HIS_COMPLETE_SETTINGS),
        "keras_backend_selection": backend,
        "versions": record_versions(),
        "framework": f"tensorflow {tf.__version__}",
        "gpu": [d.name for d in gpus],
        "warmup": warmup, "repeats": repeats,
    }
    if not gpus:
        record["NOT_A_TIMING"] = (
            "run with --allow-cpu and no GPU present: this exercises the code path "
            "and must never be read as a cost"
        )

    if variant == "ours_incumbent":
        # The vendored production PET, through its own module, exactly as
        # `calibrate_cost.time_ours_step` builds it: this is the promoted
        # incumbent and not a candidate improvement on it.
        import pet2_omnifold_adapter as adapter
        omnifold_root = repo / "omnifold_nn"
        if str(omnifold_root) not in sys.path:
            sys.path.insert(0, str(omnifold_root))
        from omnifold.net import PET, weighted_binary_crossentropy

        schema = adapter.STEP_SCHEMAS["step2_gen"]
        ours = PET(num_feat=schema["num_feat"], num_evt=schema["num_evt"],
                   num_part=tokens, num_heads=2, num_transformer=2,
                   projection_dim=32, local=True, K=3,
                   coord_idx=schema["coord_idx"])
        model = ours.model
        part = tf.constant(np.abs(rng.rand(batch, tokens, schema["num_feat"])),
                           tf.float32)
        evt = tf.constant(rng.randn(batch, schema["num_evt"]), tf.float32)
        labels = tf.constant(np.concatenate(
            [rng.randint(0, 2, (batch, 1)), np.ones((batch, 1))], axis=1), tf.float32)

        def call(training):
            return model([part, evt], training=training)

        def loss_of(predictions):
            return weighted_binary_crossentropy(labels, predictions)

        record["arm"] = "ours_incumbent"
        record["configuration"] = {"architecture": "vendored omnifold.net.PET",
                                   "step": "step2_gen", "K": 3, "heads": 2,
                                   "transformers": 2, "projection_dim": 32}
    else:
        model = port.PET2Port(**HIS_COMPLETE_SETTINGS, **port.preset("small"))
        blocks = _set_local_block_paths(
            port, model, materialise=variant == "baseline", tile=variant == "baseline")
        record["local_blocks_switched"] = blocks
        record["local_block_path"] = ("pre-optimisation (tiled centre, materialised "
                                      "pair mask)" if variant == "baseline"
                                      else "broadcast centre, broadcast key mask")
        x = tf.constant(rng.randn(batch, tokens, 4).astype(np.float32))
        pid = tf.constant(rng.randint(0, 8, (batch, tokens)).astype(np.int32))
        add = tf.constant(rng.randn(batch, tokens, 5).astype(np.float32))
        cond = tf.constant(rng.randn(batch, 16).astype(np.float32))
        labels = tf.constant(rng.randint(0, 2, (batch, 1)).astype("float32"))

        def call(training):
            return model(x, cond, pid, add, training=training)

        def loss_of(predictions):
            return tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(
                labels=labels, logits=predictions))

    jit = variant == "optimised_xla"
    record["jit_compile"] = jit
    function = (lambda fn: tf.function(fn, jit_compile=True)) if jit else tf.function

    if mode == "forward":
        record["sections"] = {
            "forward": _time(function(lambda: tf.reduce_sum(call(False))), batch, tf,
                            warmup, repeats)
        }
        record["trainable_parameters"] = int(
            sum(int(np.prod(w.shape)) for w in model.trainable_variables))
        return record

    schedule = recipe.derive_schedule(batch, examples=batch * 1000)
    sections: dict[str, Any] = {}

    if variant == "accum4":
        # His `-bs 512 --grad_accum_steps 4`. The per-example cost is charged
        # against the VIRTUAL batch, because that is what one optimizer step
        # presents and what the campaign budget counts.
        micro = micro_batch
        steps = recipe.accumulation_steps(batch, micro)
        call(False)                        # build, so the accumulators are shaped
        optimizer = recipe.build_optimizer("theirs", schedule=schedule)
        accumulator = recipe.AccumulatingStep(
            model, optimizer, lambda y, p: tf.reduce_mean(
                tf.nn.sigmoid_cross_entropy_with_logits(labels=y, logits=p)),
            steps, compile_step=True,
            forward=lambda inputs, training: model(*inputs, training=training),
        )

        def one_virtual_batch():
            last = None
            for group in range(steps):
                rows = slice(group * micro, (group + 1) * micro)
                last = accumulator.micro_step(
                    (x[rows], cond[rows], pid[rows], add[rows]), labels[rows])
            return last

        sections["virtual_batch_train"] = _time(one_virtual_batch, batch, tf, warmup, repeats)
        sections["virtual_batch_train"].update(
            accumulation_steps=steps, micro_batch=micro,
            optimizer_applies=accumulator.applies,
            pending_micro_batches=accumulator.pending,
            charged_against="the virtual batch, one optimizer step",
        )
        record["sections"] = sections
        record["trainable_parameters"] = int(
            sum(int(np.prod(w.shape)) for w in model.trainable_variables))
        return record

    call(False)                                   # build, so variables exist
    optimizer = recipe.build_optimizer("theirs", schedule=schedule)
    variables = model.trainable_variables

    @function
    def forward_only():
        return tf.reduce_sum(call(False))

    @function
    def forward_and_backward():
        with tf.GradientTape() as tape:
            loss = loss_of(call(True))
        gradients = tape.gradient(loss, variables)
        return loss + 0.0 * tf.add_n([tf.reduce_sum(g) for g in gradients
                                      if g is not None])

    @function
    def full_step():
        with tf.GradientTape() as tape:
            loss = loss_of(call(True))
        optimizer.apply_gradients(zip(tape.gradient(loss, variables), variables))
        return loss

    sections["forward"] = _time(forward_only, batch, tf, warmup, repeats)
    sections["forward_and_backward"] = _time(forward_and_backward, batch, tf, warmup, repeats)
    sections["full_step"] = _time(full_step, batch, tf, warmup, repeats)
    # Apply is the remainder: timing it alone would need a second set of resident
    # gradients, which is itself a memory change. Reported as a difference and
    # labelled as one.
    sections["apply_by_difference"] = {
        "step_seconds_median": (sections["full_step"]["step_seconds_median"]
                                - sections["forward_and_backward"]["step_seconds_median"]),
        "note": "difference of two medians, not an independent measurement",
    }
    record["sections"] = sections
    record["trainable_parameters"] = int(
        sum(int(np.prod(w.shape)) for w in model.trainable_variables))
    record["optimizer_variables"] = len(variables)
    return record


def merge(cell_dir: Path, expected: list[str]) -> dict[str, Any]:
    """Collect the per-cell files and report what is MISSING rather than eliding it."""
    cells, missing = {}, []
    for key in expected:
        path = cell_dir / (key.replace("|", "_") + ".json")
        if path.exists():
            cells[key] = json.loads(path.read_text())
        else:
            missing.append(key)
    return {
        "scope": ("decomposed cost and peak device memory for the PORTED arm and our "
                  "incumbent; synthetic inputs at his widths; no learning claim"),
        "cells": cells,
        "missing_cells": missing,
        "missing_means": ("the cell's process did not write a receipt -- an OOM kills "
                          "the interpreter, so absence is a measurement, not a gap"),
        "expected_cells": expected,
    }


def expected_cells() -> list[str]:
    keys = []
    for variant in ("baseline", "optimised", "optimised_xla", "ours_incumbent"):
        for tokens in (12, 33):
            for batch in (512, 2048):
                for mode in MODES:
                    keys.append(f"{variant}|{tokens}|{batch}|{mode}")
    for tokens in (12, 33):
        keys.append(f"accum4|{tokens}|2048|train")
    return keys


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--cell")
    parser.add_argument("--cell-dir", type=Path)
    parser.add_argument("--list-cells", action="store_true")
    parser.add_argument("--micro-batch", type=int, default=512)
    parser.add_argument("--warmup", type=int, default=WARMUP)
    parser.add_argument("--repeats", type=int, default=REPEATS)
    parser.add_argument("--allow-cpu", action="store_true",
                        help="smoke-test the code path off-cluster; NOT a timing")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.list_cells:
        print("\n".join(expected_cells()))
        return
    if args.cell:
        variant, tokens, batch, mode = args.cell.split("|")
        try:
            record = measure_cell(args.repo, variant, int(tokens), int(batch), mode,
                                  micro_batch=args.micro_batch,
                                  allow_cpu=args.allow_cpu,
                                  warmup=args.warmup, repeats=args.repeats)
        except Exception as error:                       # noqa: BLE001 - recorded
            record = {"variant": variant, "tokens": int(tokens), "batch": int(batch),
                      "mode": mode, "failed": True, "error": repr(error),
                      "traceback": traceback.format_exc()}
        args.output.write_text(json.dumps(record, indent=2) + "\n")
        print(json.dumps({k: v for k, v in record.items()
                          if k in ("variant", "tokens", "batch", "mode", "failed")}))
        return
    if args.cell_dir:
        args.output.write_text(
            json.dumps(merge(args.cell_dir, expected_cells()), indent=2) + "\n")
        return
    parser.error("one of --cell, --cell-dir or --list-cells is required")


if __name__ == "__main__":
    main()
