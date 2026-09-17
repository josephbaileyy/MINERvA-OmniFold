"""A3: gate the realized bucket widths, and measure per-arm GPU cost.

Two questions in one short job, both of which the proposal currently answers with an
estimate:

1. **Does the cross-device gate pass at the widths this experiment would actually
   train at?** Bucketing removes padding, but it does not validate a *width*: the
   frozen guard pins one geometry and says so in its own refusal -- the GPU gate never
   validated a padded or variable-length batch. So every width the fixture can realize
   is gated here, using the campaign's own ``trace``/``replay``/``validate`` machinery
   rather than a second implementation of it, and the receipt's validated set is what
   ``WidthSetGuard`` will later refuse to train outside of.

2. **What does each arm cost on the real device at the measured multiplicity?** The
   local CPU probe established that the premium grows with multiplicity and is not
   FLOP-driven; this converts it into a GPU number for sizing.

The width ladder is derived from the A1 receipt's measured histograms by quantile
matching, not from the full support of the distribution. That is a deliberate
consequence of requiring complete gate coverage without dropping events: a fixture
sampling the full support would realize more distinct widths than can be gated, and
the alternative -- training only inside gated buckets -- would silently drop events and
break the partition invariant. Families are sampled independently, so the realized
width set is the product of the ladders; the joint multiplicity correlation of real
events is not reproduced, and that is a stated limitation rather than a hidden one.

Nothing here trains to convergence, produces a closure number, or touches a frozen
receipt.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
import tempfile
import time
from typing import Any

import numpy as np


def _install(checkout: Path) -> None:
    """Put the checkout's modules first."""
    for root in (
        checkout / "nd-unfolding" / "pet" / "direct_token_comparison",
        checkout / "nd-unfolding" / "pet",
    ):
        if not root.is_dir():
            raise ValueError(f"Not a directory: {root}")
        sys.path.insert(0, str(root))


def ladder_from_histogram(
    histogram: dict[str, int], points: int, *, minimum: int = 0
) -> tuple[int, ...]:
    """Pick up to ``points`` representative counts from a measured histogram.

    Evenly spaced quantiles are the obvious choice and they fail on exactly the
    distributions this has to handle. With 90% of events at one multiplicity and a
    real tail beyond it -- the measured shape, where the median is far below the mean
    -- the 0.1, 0.5 and 0.9 quantiles are all the mode, the ladder collapses to a
    single rung, and the gate then covers no multiplicity the tail ever produces.

    So the quantiles are computed on a fine grid reaching to the far tail, reduced to
    the distinct values that grid actually hits, and then thinned evenly across those
    distinct values. That yields ``points`` rungs whenever the distribution has that
    many distinct values, and the top rung always sits in the tail rather than at the
    mode.
    """
    counts = np.repeat(
        np.fromiter((int(k) for k in histogram), dtype=np.int64),
        np.fromiter((int(v) for v in histogram.values()), dtype=np.int64),
    )
    if counts.size == 0:
        return (minimum,)
    if points < 1:
        raise ValueError("points must be positive")
    grid = np.linspace(0.05, 0.995, 64)
    candidates = np.unique(
        np.clip(np.quantile(counts, grid).round().astype(np.int64), minimum, None)
    )
    if len(candidates) <= points:
        return tuple(int(value) for value in candidates)
    picks = np.linspace(0, len(candidates) - 1, points).round().astype(np.int64)
    return tuple(int(value) for value in np.unique(candidates[picks]))


GROUP = 4  # the bound freezer and preflight both require exactly four cases


def width_case_builder(modules: dict[str, Any], widths: list[tuple[int, ...]], rows: int) -> Any:
    """Return a drop-in replacement for ``compatibility_preflight.fixtures``.

    The cross-device gate is a bound artifact (`amended_preflight.py`,
    `optimizer_equivalence.py`, both hash-bound in ``amended-manifest.json``), and a
    numerical gate restated in a second place is how two gates come to disagree. So
    this changes only the *fixtures* the bound pipeline runs on, and the gate logic,
    its tolerances and its verdict remain the single bound implementation.
    """
    fourarm = modules["fourarm"]
    typed = modules["typed"]
    adapter = modules["adapter"]
    runner = modules["runner"]

    def fixtures() -> tuple[Any, dict[str, dict[str, Any]]]:
        cases: dict[str, dict[str, Any]] = {}
        norm = None
        for width in widths:
            counts = np.tile(np.asarray(width, dtype=np.int64), (rows, 1))
            batch = fourarm.build_variable_typed_batch(typed, counts, seed=2401)
            event = np.zeros((rows, 13), dtype=np.float32)
            truth = np.zeros((rows, 2), dtype=np.float32)
            if norm is None:
                norm = typed.fit_frozen_normalization_for_smoke(
                    batch,
                    fit_inventory_row_selection_digest=runner.digest_arrays([truth]),
                )
            inputs = dict(adapter.prepare_keras_inputs(batch, event))
            inputs.update(
                generic_values=np.zeros((rows, 12, 5), dtype=np.float32),
                generic_mask=np.ones((rows, 12), dtype=bool),
            )
            cases[case_name(width)] = inputs
        return norm, cases

    return fixtures


def case_name(width: tuple[int, ...]) -> str:
    """Name a width case so it can never land in the stress-exempt list.

    ``STRESS_ONLY_CASES = ("variable",)``: a case called ``variable`` would have its
    failure *recorded rather than gating*, which is the opposite of what a gate run
    is for. These names cannot collide with it.
    """
    return "w" + "-".join(str(value) for value in width)


def gate_child_command(
    checkout: Path,
    widths: list[tuple[int, ...]],
    rows: int,
    workspace: Path,
    payload: Path,
) -> list[str]:
    """Build the child invocation, as a value a test can parse.

    The first attempt at the subprocess split omitted an argument the parser
    requires, so all three groups died on argv before reaching TensorFlow -- a defect
    that cost a cluster job to discover and that ``build_parser`` plus one local test
    now catch.
    """
    return [
        sys.executable,
        str(Path(__file__).resolve()),
        "--gate-group-only",
        "--checkout",
        str(checkout),
        "--widths",
        json.dumps([list(width) for width in widths]),
        "--gate-rows",
        str(rows),
        "--workspace",
        str(workspace),
        "--output",
        str(payload),
    ]


def gate_group_in_subprocess(
    checkout: Path, widths: list[tuple[int, ...]], rows: int, workspace: Path
) -> dict[str, Any]:
    """Run one gate group in a **fresh interpreter** and return its record.

    Not an optimization -- a requirement. The bound preflight calls
    ``tf.config.threading.set_intra_op_parallelism_threads(7)``, which TensorFlow
    permits only before initialization, so any process that has already touched TF
    cannot run it: the first attempt measured cost first, initialized TF doing so, and
    every gate group then died with "Intra op parallelism cannot be modified after
    initialization". That looked exactly like twelve widths failing the gate and was
    nothing of the kind.

    A subprocess also keeps the bound preflight's global TensorFlow configuration from
    leaking between groups, so each group's verdict stands on its own.
    """
    import subprocess

    payload = workspace / "group.json"
    command = gate_child_command(checkout, widths, rows, workspace, payload)
    finished = subprocess.run(command, capture_output=True, text=True)
    if payload.exists():
        record = json.loads(payload.read_text())
    else:
        record = {
            "widths": [list(width) for width in widths],
            "verdict": "FAIL",
            "error": "the gate subprocess wrote no record",
        }
    record["subprocess_returncode"] = finished.returncode
    record["subprocess_stderr_tail"] = finished.stderr[-2000:]
    return record


def gate_width_group(
    modules: dict[str, Any],
    widths: list[tuple[int, ...]],
    rows: int,
    workspace: Path,
) -> dict[str, Any]:
    """Run the bound cross-device gate on one group of exactly four widths."""
    from unittest.mock import patch

    if len(widths) != GROUP:
        raise ValueError(f"The bound pipeline requires exactly {GROUP} cases")
    original = modules["original"]
    freezer = modules["freezer"]
    preflight = modules["preflight"]
    names = tuple(case_name(width) for width in widths)
    overlap = set(names) & set(preflight.STRESS_ONLY_CASES)
    if overlap:
        raise ValueError(f"Case names collide with the stress exemption: {overlap}")
    builder = width_case_builder(modules, widths, rows)
    bundle = workspace / "bundle"
    gpu_out = workspace / "gpu"
    record: dict[str, Any] = {"widths": [list(w) for w in widths], "cases": list(names)}
    with patch.object(original, "CASES", names), patch.object(
        original, "fixtures", builder
    ):
        try:
            with patch.object(
                sys, "argv", [str(freezer.__file__), "--output", str(bundle)]
            ):
                freezer.main()
            with patch.object(
                sys,
                "argv",
                [
                    str(preflight.__file__),
                    "--bundle",
                    str(bundle),
                    "--output",
                    str(gpu_out),
                    "--device",
                    "gpu",
                ],
            ):
                preflight.main()
            record["verdict"] = "PASS"
        except (AssertionError, ValueError, RuntimeError) as failure:
            record["verdict"] = "FAIL"
            record["error"] = f"{type(failure).__name__}: {failure}"
    receipt = gpu_out / "receipt.json"
    if receipt.exists():
        body = json.loads(receipt.read_text())
        record["receipt_terminal"] = body.get("terminal")
        record["rows"] = [
            {
                key: row.get(key)
                for key in ("case", "routing", "terminal", "stress_only")
            }
            for row in body.get("rows", [])
        ]
    return record


def measure_arm_cost(
    modules: dict[str, Any],
    arm: Any,
    width: tuple[int, ...],
    *,
    rows: int,
    batch_size: int,
    steps: int,
) -> dict[str, Any]:
    """Time one arm's training step and inference pass on the GPU."""
    tf = modules["tf"]
    fourarm = modules["fourarm"]
    typed = modules["typed"]
    adapter = modules["adapter"]
    runner = modules["runner"]
    comparison = modules["comparison"]

    counts = np.tile(np.asarray(width, dtype=np.int64), (rows, 1))
    batch = fourarm.build_variable_typed_batch(typed, counts, seed=17)
    rng = np.random.default_rng(17)
    event = rng.normal(size=(rows, 13)).astype(np.float32)
    clouds = [
        np.column_stack(
            [
                rng.gamma(2.0, 50.0, size=size),
                rng.normal(size=(size, 4)),
                np.zeros((size, len(fourarm.AGGREGATE_CHANNELS))),
            ]
        ).astype(np.float32)
        for size in rng.integers(4, 40, size=rows)
    ]
    generic = fourarm.apply_cap(clouds, arm.cap_treatment)
    inputs = dict(adapter.prepare_keras_inputs(batch, event))
    inputs.update(
        generic_values=generic,
        generic_mask=np.ones(generic.shape[:2], dtype=bool),
    )
    if not arm.typed_enabled:
        inputs = fourarm.disable_families(
            inputs, [contract.name for contract in typed.FAMILY_CONTRACTS]
        )
    truth = rng.normal(size=(rows, 2)).astype(np.float32)
    target = np.exp(0.4 * np.tanh(truth[:, 0] * truth[:, 1])).astype(np.float32)
    norm = typed.fit_frozen_normalization_for_smoke(
        batch, fit_inventory_row_selection_digest=runner.digest_arrays([truth])
    )
    tf.keras.utils.set_random_seed(17)
    model = comparison.build_comparison(norm, routing=arm.routing)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="mse")
    slice_ = runner.select_inputs(inputs, np.arange(batch_size))
    labels = target[:batch_size]
    model(slice_)
    for _ in range(3):
        model.train_on_batch(slice_, labels)
    start = time.perf_counter()
    for _ in range(steps):
        model.train_on_batch(slice_, labels)
    train_ms = (time.perf_counter() - start) / steps * 1e3
    runner.predict_ratio(model, inputs, packed=True, batch_size=batch_size)
    start = time.perf_counter()
    runner.predict_ratio(model, inputs, packed=True, batch_size=batch_size)
    infer_ms = (time.perf_counter() - start) * 1e3
    return {
        "arm": arm.name,
        "typed_enabled": arm.typed_enabled,
        "routing": arm.routing,
        "cap_treatment": arm.cap_treatment,
        "typed_objects": int(sum(width)),
        "train_ms_per_step": train_ms,
        "inference_ms_per_pass": infer_ms,
        "inference_rows": rows,
    }


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser, shared by the parent and its gate children."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    # Parent-only, and therefore NOT required at the parser level: a gate child has
    # no use for it, and requiring it here is what made the children die on argv.
    parser.add_argument("--source-receipt", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--gate-rows", type=int, default=4)
    parser.add_argument("--cost-rows", type=int, default=20000)
    parser.add_argument("--batch-size", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--ladder-points", type=int, default=2)
    parser.add_argument("--blob-ladder-points", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--tail-cost-rows", type=int, default=4000)
    parser.add_argument(
        "--cost-receipt",
        type=Path,
        help=(
            "reuse an earlier run's measured cost instead of re-measuring it; the "
            "cost half is valid on its own and there is no reason to spend the device "
            "time twice"
        ),
    )
    parser.add_argument("--gate-group-only", action="store_true")
    parser.add_argument("--widths")
    parser.add_argument("--workspace", type=Path)
    return parser


def main() -> None:
    """Gate every realizable width, then time the four arms."""
    args = build_parser().parse_args()

    if not args.gate_group_only and args.source_receipt is None:
        raise ValueError("--source-receipt is required unless --gate-group-only")

    _install(args.checkout)
    import amended_preflight as preflight
    import compatibility_preflight as original
    import four_arm_representation as fourarm
    import freeze_preflight_initialization as freezer
    import typed_descriptor_keras as adapter
    import typed_descriptors as typed
    import typed_token_comparison as comparison

    import run_typed_token_comparison as runner

    if args.gate_group_only:
        # Child mode. Nothing here may touch TensorFlow's configuration or query a
        # device first: the bound preflight sets intra-op parallelism, which
        # TensorFlow accepts only before initialization. The fixture builder uses the
        # numpy paths alone, so `tf` is deliberately absent from this dict.
        if not args.widths or args.workspace is None:
            raise ValueError("--gate-group-only needs --widths and --workspace")
        child = {
            "fourarm": fourarm,
            "typed": typed,
            "adapter": adapter,
            "runner": runner,
            "comparison": comparison,
            "original": original,
            "freezer": freezer,
            "preflight": preflight,
        }
        widths = [tuple(int(v) for v in width) for width in json.loads(args.widths)]
        args.workspace.mkdir(parents=True, exist_ok=True)
        record = gate_width_group(child, widths, args.gate_rows, args.workspace)
        args.output.write_text(json.dumps(record, indent=2, default=str) + "\n")
        print(f"group verdict: {record['verdict']}")
        return

    tf = adapter.require_tensorflow()
    policy = runner.configure_precision()
    devices = [device.name for device in tf.config.list_logical_devices("GPU")]
    if not devices:
        raise RuntimeError("No GPU is visible; this probe measures device behaviour")
    modules = {
        "tf": tf,
        "fourarm": fourarm,
        "typed": typed,
        "adapter": adapter,
        "runner": runner,
        "comparison": comparison,
        "original": original,
        "freezer": freezer,
        "preflight": preflight,
    }

    source = json.loads(args.source_receipt.read_text())
    by_role = {entry["role"]: entry for entry in source["sources"]}
    reference = by_role.get("mc", source["sources"][0])
    ladders = {
        "photons": ladder_from_histogram(
            reference["photons"]["histogram"], args.ladder_points
        ),
        "blobs": ladder_from_histogram(
            reference["blobs"]["histogram"], args.blob_ladder_points
        ),
        "prongs": ladder_from_histogram(
            reference["prongs"]["histogram"], args.ladder_points, minimum=1
        ),
    }
    widths = [
        (photons, blobs, prongs)
        for photons in ladders["photons"]
        for blobs in ladders["blobs"]
        for prongs in ladders["prongs"]
    ]

    if args.cost_receipt is not None:
        earlier = json.loads(args.cost_receipt.read_text())
        costs = earlier["cost_measurements"]
        summary = earlier["cost_summary"]
        cost_points = [
            (label, tuple(block["width"]), None) for label, block in summary.items()
        ]
        print(f"reusing measured cost from {args.cost_receipt}", flush=True)
    else:
        # Cost runs FIRST and its numbers are written before the gate starts. The gate
        # is the long half, and a timeout there must not also destroy the cheap
        # measurement the sizing depends on.
        #
        # Two operating points, both from the measurement rather than from the ladder:
        # the rounded MEAN multiplicity, which is where the experiment would sit, and one
        # high blob rung, because the measured distribution is skewed enough that the mean
        # does not describe the expensive tail.
        def rounded_mean(family: str, minimum: int = 0) -> int:
            return max(minimum, int(round(float(reference[family]["mean"]))))

        mean_width = (
            rounded_mean("photons"),
            rounded_mean("blobs"),
            rounded_mean("prongs", 1),
        )
        tail_width = (rounded_mean("photons"), max(ladders["blobs"]), rounded_mean("prongs", 1))
        cost_points = [
            ("mean_multiplicity", mean_width, args.cost_rows),
            ("tail_multiplicity", tail_width, args.tail_cost_rows),
        ]
        costs: list[dict[str, Any]] = []
        for label, width, rows in cost_points:
            for _ in range(args.repeats):
                for arm in fourarm.ARMS:
                    record = measure_arm_cost(
                        modules,
                        arm,
                        width,
                        rows=rows,
                        batch_size=args.batch_size,
                        steps=args.steps,
                    )
                    record["operating_point"] = label
                    costs.append(record)
                    print(
                        f"cost {label} arm={arm.name} K={sum(width)} "
                        f"train={record['train_ms_per_step']:.1f} ms "
                        f"infer={record['inference_ms_per_pass']:.1f} ms",
                        flush=True,
                    )

        summary: dict[str, Any] = {}
        for label, width, _ in cost_points:
            block: dict[str, Any] = {"width": list(width), "typed_objects": int(sum(width))}
            for arm in fourarm.ARMS:
                mine = [
                    row
                    for row in costs
                    if row["arm"] == arm.name and row["operating_point"] == label
                ]
                block[arm.name] = {
                    "train_ms_median": statistics.median(
                        row["train_ms_per_step"] for row in mine
                    ),
                    "inference_ms_median": statistics.median(
                        row["inference_ms_per_pass"] for row in mine
                    ),
                }
            baseline = block["A"]["train_ms_median"]
            infer_baseline = block["A"]["inference_ms_median"]
            for arm in fourarm.ARMS:
                block[arm.name]["train_ratio_to_A"] = (
                    block[arm.name]["train_ms_median"] / baseline if baseline else None
                )
                block[arm.name]["inference_ratio_to_A"] = (
                    block[arm.name]["inference_ms_median"] / infer_baseline
                    if infer_baseline
                    else None
                )
            # A and D carry identical token counts by construction, so a systematic
            # difference between them is a defect in the measurement, not a property of
            # the arms. Recorded rather than asserted: a timing probe should report a
            # suspicious reading, not refuse to write one.
            block["a_d_train_parity_ratio"] = block["D"]["train_ratio_to_A"]
            block["a_d_parity_within_10_percent"] = (
                block["D"]["train_ratio_to_A"] is not None
                and abs(block["D"]["train_ratio_to_A"] - 1.0) <= 0.10
            )
            summary[label] = block

        partial = {
            "scope": "A3 cost half only; the gate had not run when this was written",
            "precision_policy": policy,
            "gpu_devices": devices,
            "cost_measurements": costs,
            "cost_summary": summary,
            "gate_records": [],
            "gate_complete": False,
        }
        args.output.write_text(json.dumps(partial, indent=2, allow_nan=False) + "\n")
    print("cost half written; starting the gate", flush=True)

    # The bound pipeline takes exactly four cases at a time, so widths are gated in
    # groups of four. A short ladder is deliberate: every width the fixture can
    # realize must be gated, because the alternative -- training only inside gated
    # buckets -- would drop events and break the partition invariant.
    while len(widths) % GROUP:
        widths.append(widths[-1])
    groups = [widths[i : i + GROUP] for i in range(0, len(widths), GROUP)]

    gates: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as scratch:
        for index, group in enumerate(groups):
            workspace = Path(scratch) / f"group{index}"
            workspace.mkdir()
            gates.append(
                gate_group_in_subprocess(
                    args.checkout, group, args.gate_rows, workspace
                )
            )
            print(
                f"gate group {index} widths={gates[-1]['widths']}: "
                f"{gates[-1]['verdict']}",
                flush=True,
            )

    per_width: dict[tuple[int, ...], str] = {}
    for record in gates:
        rows_by_case = {row["case"]: row for row in record.get("rows", [])}
        for width in record["widths"]:
            name = case_name(tuple(width))
            row = rows_by_case.get(name)
            if row is not None and row.get("terminal") is not None:
                verdict = str(row["terminal"])
            else:
                verdict = record["verdict"]
            per_width[tuple(width)] = verdict
    failed = sorted(w for w, verdict in per_width.items() if verdict != "PASS")
    validated = sorted(w for w, verdict in per_width.items() if verdict == "PASS")

    receipt = {
        "scope": (
            "A3 preparation: cross-device gate coverage at realizable widths, and "
            "per-arm GPU cost. No training to convergence, no closure statistic."
        ),
        "authorization": "A3, Joseph, 2026-09-18, ceiling 1 GPU-hour",
        "precision_policy": policy,
        "gpu_devices": devices,
        "source_receipt": str(args.source_receipt),
        "reference_role": reference["role"],
        "ladders": {family: list(values) for family, values in ladders.items()},
        "widths_enumerated": [list(width) for width in sorted(set(widths))],
        "gate_records": gates,
        "gate_verdict_by_width": {
            str(list(width)): verdict for width, verdict in sorted(per_width.items())
        },
        "validated_widths": [list(width) for width in validated],
        "failed_widths": [list(width) for width in failed],
        "gate_complete": bool(validated)
        and not failed
        and set(validated) == set(widths),
        "cost_measurements": costs,
        "cost_summary": summary,
        "limitations": [
            "Families are sampled independently, so the realized width set is the "
            "product of the per-family ladders; the joint multiplicity correlation of "
            "real events is not reproduced.",
            "The ladder is quantile-matched to the measured histograms, not their full "
            "support, because complete gate coverage without dropping events requires "
            "a finite width set.",
            "Cost is cost. A cheaper arm is not a better one and nothing here bears on "
            "closure.",
        ],
    }
    args.output.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    print(
        f"validated {len(validated)} of {len(set(widths))} widths; "
        f"gate_complete={receipt['gate_complete']}"
    )
    for label, block in summary.items():
        for arm in ("A", "B", "C", "D"):
            print(
                f"{label} arm {arm}: train {block[arm]['train_ms_median']:.1f} ms "
                f"({block[arm]['train_ratio_to_A']:.3f}x A), inference "
                f"{block[arm]['inference_ms_median']:.1f} ms "
                f"({block[arm]['inference_ratio_to_A']:.3f}x A)"
            )


if __name__ == "__main__":
    main()
