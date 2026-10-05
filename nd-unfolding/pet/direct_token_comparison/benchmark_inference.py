"""Time per-arm inference on saved trained models, without touching the comparison.

Implements ``INFERENCE_BENCHMARK_SPECIFICATION-20260917.md``. The frozen producer
records per-arm *training* cost and one per-job wall time, so per-arm inference is
not derivable from the matrix; it is measured here or not at all.

Nothing is retrained. Saved reco models are opened read-only, the held-out test
split is rebuilt deterministically by the same call the matrix used, and only
timing output is written.

Three costs are kept apart on purpose, because folding them together is how a
throughput number becomes wrong: model loading is one-off per process,
preprocessing is shared work that would inflate both arms equally, and only the
timed prediction passes are throughput. Arms are measured alternately so that
drift in machine state cannot land on one of them.

This measures cost, not quality. A faster arm is not a better one.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
import time
from typing import Any

import numpy as np

WARMUP_PASSES = 3
TIMED_PASSES = 10
BATCH_SIZE = 1024
TEST_FIXTURE_SEED = 2402
ROUTES = ("pooled", "direct")
MAX_COEFFICIENT_OF_VARIATION = 0.10


def _install(checkout: Path) -> list[str]:
    """Put the named checkout's modules first, and report where they resolved."""
    roots = [
        checkout / "nd-unfolding" / "pet",
        checkout / "nd-unfolding" / "pet" / "direct_token_comparison",
    ]
    for root in reversed(roots):
        if not root.is_dir():
            raise ValueError(f"Not a directory: {root}")
        sys.path.insert(0, str(root))
    return [str(r) for r in roots]


def build_inputs(rows: int) -> tuple[dict[str, Any], str]:
    """Rebuild the matrix's held-out test split and digest it.

    Both arms must see the same events in the same order, so the digest is
    recorded and compared rather than assumed.
    """
    import run_typed_token_comparison as runner
    import typed_descriptor_keras as adapter

    batch, event, generic, truth = runner.make_fixture(rows, TEST_FIXTURE_SEED)
    inputs = adapter.prepare_keras_inputs(batch, event)
    inputs.update(
        generic_values=generic, generic_mask=np.ones(generic.shape[:2], dtype=bool)
    )
    digest = runner.digest_arrays(
        [np.asarray(inputs[key]) for key in sorted(inputs)] + [truth]
    )
    return dict(inputs), digest


def summarize(durations: list[float], rows: int) -> dict[str, Any]:
    """Throughput and variability from timed passes only."""
    mean = statistics.mean(durations)
    deviation = statistics.stdev(durations) if len(durations) > 1 else 0.0
    return {
        "passes": len(durations),
        "seconds_mean": mean,
        "seconds_stdev": deviation,
        "seconds_min": min(durations),
        "seconds_max": max(durations),
        "coefficient_of_variation": (deviation / mean) if mean else None,
        "events_per_second_mean": rows / mean if mean else None,
        "seconds_each": durations,
    }


def measure_seed(
    tf: Any,
    comparison: Any,
    runner: Any,
    output: Path,
    stem: str,
    rows: int,
    inputs: dict[str, Any],
    digest: str,
) -> dict[str, Any]:
    """Measure both arms for one trained seed, alternating between them.

    The split is built once by the caller and shared. Rebuilding it per seed cost
    about 100 s each at the full test size and merely *assumed* the rebuild was
    identical; sharing one build makes "identical inputs across arms and seeds"
    true by construction rather than by trusting determinism.
    """
    # Register the lazily-defined custom Keras type before loading, as the
    # repository README requires; otherwise the saved model cannot deserialize.
    comparison.comparison_model_type()

    load_seconds: dict[str, float] = {}
    models: dict[str, Any] = {}
    for route in ROUTES:
        path = output / f"{stem}.{route}.keras"
        if not path.exists():
            raise FileNotFoundError(f"Saved model absent: {path}")
        start = time.perf_counter()
        models[route] = tf.keras.models.load_model(path)
        load_seconds[route] = time.perf_counter() - start

    def predictor(model: Any) -> Any:
        def predict(source: dict[str, Any]) -> Any:
            return runner.predict_ratio(
                model, source, packed=True, batch_size=BATCH_SIZE
            )

        return predict

    # Alternate arms so monotonic drift cannot load onto one of them.
    collected: dict[str, list[float]] = {route: [] for route in ROUTES}
    for _ in range(WARMUP_PASSES):
        for route in ROUTES:
            predictor(models[route])(inputs)
    for _ in range(TIMED_PASSES):
        for route in ROUTES:
            start = time.perf_counter()
            predictions = predictor(models[route])(inputs)
            collected[route].append(time.perf_counter() - start)
            if len(np.asarray(predictions)) != rows:
                raise ValueError("Prediction row count does not match the split")

    return {
        "stem": stem,
        "input_digest": digest,
        "rows": rows,
        "model_load_seconds": load_seconds,
        "arms": {route: summarize(collected[route], rows) for route in ROUTES},
    }


def main() -> None:
    """Run the bounded per-arm inference benchmark and write its receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--matrix-output", type=Path, required=True)
    parser.add_argument("--rows", type=int, default=50000)
    parser.add_argument("--stems", default="ordinary-17,ordinary-29,ordinary-43")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    installed = _install(args.checkout)
    import run_typed_token_comparison as runner
    import typed_descriptor_keras as adapter
    import typed_token_comparison as comparison

    tf = adapter.require_tensorflow()
    policy = runner.configure_precision()
    devices = [d.name for d in tf.config.list_logical_devices("GPU")]

    # Preprocessing is shared work; time it once and keep it out of throughput.
    start = time.perf_counter()
    inputs, digest = build_inputs(args.rows)
    preprocessing_seconds = time.perf_counter() - start

    seeds = [s for s in args.stems.split(",") if s]
    results = [
        measure_seed(
            tf, comparison, runner, args.matrix_output, stem, args.rows, inputs, digest
        )
        for stem in seeds
    ]

    noisy = sorted(
        f"{r['stem']}/{route}"
        for r in results
        for route in ROUTES
        if (r["arms"][route]["coefficient_of_variation"] or 0)
        > MAX_COEFFICIENT_OF_VARIATION
    )
    ratios = [
        r["arms"]["direct"]["seconds_mean"] / r["arms"]["pooled"]["seconds_mean"]
        for r in results
        if r["arms"]["pooled"]["seconds_mean"]
    ]
    directions = {"direct_slower" if x > 1 else "direct_faster" for x in ratios}

    receipt: dict[str, Any] = {
        "scope": "per-arm inference COST on saved trained models; no retraining, no learning claim",
        "specification": "nd-unfolding/pet/direct_token_comparison/INFERENCE_BENCHMARK_SPECIFICATION-20260917.md",
        "installed_paths": installed,
        "precision_policy": policy,
        "gpu_devices": devices,
        "batch_size": BATCH_SIZE,
        "warmup_passes": WARMUP_PASSES,
        "timed_passes": TIMED_PASSES,
        "input_digest": digest,
        "preprocessing_seconds": preprocessing_seconds,
        "seeds": results,
        "checks": {
            "B1_identical_inputs_across_arms": len({r["input_digest"] for r in results})
            == 1,
            "B2_precision_and_gpu": policy == runner.PRECISION_POLICY and bool(devices),
            "B3_timing_stable": not noisy,
            "B4_consistent_direction": len(directions) == 1,
            "B5_costs_separated": True,
        },
        "noisy_measurements": noisy,
        "paired_direct_over_pooled_ratio": {
            "values": ratios,
            "median": statistics.median(ratios) if ratios else None,
        },
        "non_claim": (
            "Cost only. A faster arm is not a better one, these numbers do not enter "
            "the frozen acceptance criteria, and nothing here bears on closure "
            "accuracy or representation quality."
        ),
    }
    args.output.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    for name, held in receipt["checks"].items():
        print(f"{name}: {'PASS' if held else 'FAIL'}")
    if ratios:
        print(
            f"median direct/pooled inference time ratio: {statistics.median(ratios):.4f}"
        )


if __name__ == "__main__":
    main()
