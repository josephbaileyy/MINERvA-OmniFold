"""Measure how each routing's step cost grows with typed-object multiplicity.

Local, CPU, and deliberately cheap: it trains nothing to convergence and produces
no learning statistic. It exists because the cost premium of individual-object
routing is **not** FLOP-driven -- at width 32 the feed-forward block dominates and
is linear in token count, which predicts about 1.06x at four typed objects against
the 1.118x actually measured on a GPU. The excess is the direct route's
ragged-to-dense repacking, so cost at a higher multiplicity has to be measured
rather than extrapolated.

The measurement is anchored: run at the finished matrix's geometry (one photon, one
blob, two prongs) it must reproduce that campaign's GPU-measured training ratio of
1.118 to within run-to-run scatter. If the anchor drifts, the curve is not usable
and nothing here should be quoted.

Ratios, not absolutes, transfer from this CPU probe to a GPU. Absolute per-job cost
needs the bounded GPU probe in ``DECISION_PACKET-20260917.md`` (A3).
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

ANCHOR_COUNTS = {"photons": 1, "blobs": 1, "prongs": 2}
ANCHOR_GPU_TRAIN_RATIO = 1.118
GENERIC_SLOTS = 12  # the production top-12-by-energy cap
ROUTES = ("pooled", "direct")


def _install(checkout: Path) -> None:
    """Put the named checkout's modules first."""
    for root in (
        checkout / "nd-unfolding" / "pet" / "direct_token_comparison",
        checkout / "nd-unfolding" / "pet",
    ):
        if not root.is_dir():
            raise ValueError(f"Not a directory: {root}")
        sys.path.insert(0, str(root))


def build_fixture(
    typed: Any, runner: Any, rows: int, seed: int, counts: dict[str, int], slots: int
) -> tuple[Any, Any, Any, Any]:
    """Build the frozen fixture with per-family object counts made variable.

    Mirrors ``run_typed_token_comparison.make_fixture`` exactly except for the
    counts, so the timing difference is attributable to multiplicity alone. Prong
    fields alternate the two real ``raw_pid`` values so added objects are
    distinguishable rather than duplicates.
    """
    rng = np.random.default_rng(seed)
    truth = rng.normal(size=(rows, 2)).astype(np.float32)
    reco = truth + rng.normal(0, 0.15, size=truth.shape)
    collections: dict[str, list[list[dict[str, Any]]]] = {}
    for contract in typed.FAMILY_CONTRACTS:
        family: list[list[dict[str, Any]]] = []
        for row in range(rows):
            objects = []
            for index in range(counts[contract.name]):
                fields = {
                    field.name: ([1.0] * field.width if field.width > 1 else 1.0)
                    for field in contract.fields
                }
                if contract.name == "prongs":
                    leading = index % 2 == 0
                    fields.update(
                        raw_pid=3 if leading else 8,
                        charge=2 if leading else 0,
                        score=1.0,
                        mass=105.658 if leading else 938.272,
                        time=float(reco[row, index % 2]),
                    )
                objects.append(fields)
            family.append(objects)
        collections[contract.name] = family
    provenance = typed.RowProvenance(
        source_file_ordinal=np.ones(rows, dtype=np.uint32),
        source_tree=np.full(rows, typed.SourceTree.MASTER_ANA_DEV, dtype=np.uint8),
        source_entry=np.arange(rows, dtype=np.uint64),
    )
    batch = typed.build_descriptor_batch(
        provenance=provenance,
        photon_rows=collections["photons"],
        blob_rows=collections["blobs"],
        prong_rows=collections["prongs"],
    )
    event = rng.normal(size=(rows, 13)).astype(np.float32)
    generic = rng.normal(size=(rows, slots, 5)).astype(np.float32)
    return batch, event, generic, truth


def measure_one(
    modules: dict[str, Any],
    counts: dict[str, int],
    *,
    rows: int,
    batch_size: int,
    steps: int,
    slots: int,
) -> dict[str, Any]:
    """Time one training step and one full inference pass for both routings."""
    typed, adapter, comparison, runner = (
        modules["typed"],
        modules["adapter"],
        modules["comparison"],
        modules["runner"],
    )
    tf = modules["tf"]
    batch, event, generic, truth = build_fixture(typed, runner, rows, 17, counts, slots)
    norm = typed.fit_frozen_normalization_for_smoke(
        batch, fit_inventory_row_selection_digest=runner.digest_arrays([truth])
    )
    inputs = adapter.prepare_keras_inputs(batch, event)
    inputs.update(
        generic_values=generic,
        generic_mask=np.ones(generic.shape[:2], dtype=bool),
    )
    target = np.exp(0.4 * np.tanh(truth[:, 0] * truth[:, 1])).astype(np.float32)
    timings: dict[str, dict[str, float]] = {}
    for routing in ROUTES:
        tf.keras.utils.set_random_seed(17)
        model = comparison.build_comparison(norm, routing=routing)
        model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="mse")
        slice_ = runner.select_inputs(inputs, np.arange(batch_size))
        labels = target[:batch_size]
        model(slice_)
        for _ in range(2):  # warm up: graph tracing and kernel selection
            model.train_on_batch(slice_, labels)
        start = time.perf_counter()
        for _ in range(steps):
            model.train_on_batch(slice_, labels)
        train_ms = (time.perf_counter() - start) / steps * 1e3
        runner.predict_ratio(model, inputs, packed=True, batch_size=batch_size)
        start = time.perf_counter()
        runner.predict_ratio(model, inputs, packed=True, batch_size=batch_size)
        infer_ms = (time.perf_counter() - start) * 1e3
        timings[routing] = {"train_ms": train_ms, "infer_ms": infer_ms}
    return {
        "counts": dict(counts),
        "typed_objects": sum(counts.values()),
        "generic_slots": slots,
        "timings": timings,
        "train_ratio": timings["direct"]["train_ms"] / timings["pooled"]["train_ms"],
        "infer_ratio": timings["direct"]["infer_ms"] / timings["pooled"]["infer_ms"],
    }


def main() -> None:
    """Sweep typed multiplicity and report the direct/pooled cost ratio."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--rows", type=int, default=2048)
    parser.add_argument("--batch-size", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=15)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    _install(args.checkout)
    import typed_descriptor_keras as adapter
    import typed_descriptors as typed
    import typed_token_comparison as comparison

    import run_typed_token_comparison as runner

    modules = {
        "typed": typed,
        "adapter": adapter,
        "comparison": comparison,
        "runner": runner,
        "tf": adapter.require_tensorflow(),
    }

    plan = [
        ANCHOR_COUNTS,
        {"photons": 2, "blobs": 4, "prongs": 2},
        {"photons": 2, "blobs": 8, "prongs": 4},
        {"photons": 2, "blobs": 14, "prongs": 4},
        {"photons": 2, "blobs": 26, "prongs": 4},
    ]
    # Replicates are the OUTER loop, so drift in machine state spreads across every
    # multiplicity instead of concentrating on whichever one it coincided with. With
    # the configurations outermost, one busy minute made the K=14 ratio read 1.217 in
    # one run and 1.479 in another; the ordering, not the model, produced that.
    collected: dict[int, list[dict[str, Any]]] = {}
    for _ in range(args.repeats):
        for counts in plan:
            collected.setdefault(sum(counts.values()), []).append(
                measure_one(
                    modules,
                    counts,
                    rows=args.rows,
                    batch_size=args.batch_size,
                    steps=args.steps,
                    slots=GENERIC_SLOTS,
                )
            )
    rows: list[dict[str, Any]] = []
    for counts in plan:
        replicates = collected[sum(counts.values())]
        train = [r["train_ratio"] for r in replicates]
        infer = [r["infer_ratio"] for r in replicates]
        rows.append(
            {
                "counts": dict(counts),
                "typed_objects": sum(counts.values()),
                "train_ratio_median": statistics.median(train),
                "train_ratio_min": min(train),
                "train_ratio_max": max(train),
                "train_ratio_each": train,
                "infer_ratio_median": statistics.median(infer),
                "infer_ratio_min": min(infer),
                "infer_ratio_max": max(infer),
                "infer_ratio_each": infer,
                "pooled_train_ms_median": statistics.median(
                    r["timings"]["pooled"]["train_ms"] for r in replicates
                ),
                "direct_train_ms_median": statistics.median(
                    r["timings"]["direct"]["train_ms"] for r in replicates
                ),
            }
        )
        print(
            f"K={rows[-1]['typed_objects']:3d}  train ratio "
            f"{rows[-1]['train_ratio_median']:.3f} "
            f"[{rows[-1]['train_ratio_min']:.3f}, {rows[-1]['train_ratio_max']:.3f}]"
            f"  infer ratio {rows[-1]['infer_ratio_median']:.3f} "
            f"[{rows[-1]['infer_ratio_min']:.3f}, {rows[-1]['infer_ratio_max']:.3f}]",
            flush=True,
        )

    anchor = next(r for r in rows if r["counts"] == ANCHOR_COUNTS)
    receipt = {
        "scope": "COST SCALING ONLY, local CPU; no learning statistic and no closure claim",
        "rows": args.rows,
        "batch_size": args.batch_size,
        "steps": args.steps,
        "repeats": args.repeats,
        "generic_slots": GENERIC_SLOTS,
        "measurements": rows,
        "anchor": {
            "counts": ANCHOR_COUNTS,
            "local_train_ratio_median": anchor["train_ratio_median"],
            "gpu_train_ratio_measured": ANCHOR_GPU_TRAIN_RATIO,
            "absolute_difference": abs(
                anchor["train_ratio_median"] - ANCHOR_GPU_TRAIN_RATIO
            ),
        },
        "non_claim": (
            "Ratios only. A cheaper routing is not a better one, and nothing here "
            "bears on closure accuracy. Absolute per-job GPU cost is not measured."
        ),
    }
    if args.output:
        args.output.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    print(
        f"anchor: local {anchor['train_ratio_median']:.3f} vs GPU "
        f"{ANCHOR_GPU_TRAIN_RATIO:.3f}"
    )


if __name__ == "__main__":
    main()
