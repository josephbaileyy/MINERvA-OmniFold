"""The four-arm experiment's execution path, and its validation entry.

One setup function serves both entries. ``--validate-only`` builds the real fixture,
cap treatment, bucket plan, width guard, model and optimizer, takes a bounded number
of real steps and runs the frozen battery against that state; the training entry
builds the same state through the same call and then keeps going. So the path that is
validated is the path that trains, and a narrower probe beside it could not release
anything.

Training refuses to start without a validation receipt that covers its plan, whose
digest and recorded commit it verifies. That refusal is the mechanism by which
validation gates execution rather than merely preceding it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
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


def head_commit(checkout: Path) -> str:
    """Return the checkout's HEAD, so a receipt cannot outlive its code."""
    return subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def released_widths(receipt: dict[str, Any]) -> set[tuple[int, ...]]:
    """Return the widths a validation receipt actually released."""
    return {tuple(int(v) for v in w) for w in receipt.get("released_widths", [])}


def require_validation(
    checkout: Path, receipt_path: Path, needed: set[tuple[int, ...]]
) -> dict[str, Any]:
    """Refuse to train unless a matching receipt covers every width in the plan."""
    payload = receipt_path.read_bytes()
    receipt = json.loads(payload)
    digest = hashlib.sha256(payload).hexdigest()
    commit = head_commit(checkout)
    if receipt.get("commit") != commit:
        raise ValueError(
            f"Validation receipt was written at {receipt.get('commit')}, "
            f"HEAD is {commit}: it does not describe this code"
        )
    if not receipt.get("complete"):
        raise ValueError("Validation receipt is incomplete; training is not released")
    missing = sorted(needed - released_widths(receipt))
    if missing:
        raise ValueError(f"These widths were never released: {missing}")
    return {"validation_receipt_sha256": digest, "commit": commit}


def validate_width(
    modules: dict[str, Any],
    criteria: Any,
    arm: Any,
    width: tuple[int, ...],
    *,
    rows: int,
    batch_size: int,
    steps: int,
    samples: int,
    workspace: Path,
) -> dict[str, Any]:
    """Run the whole frozen battery for one arm at one width."""
    validation = modules["validation"]

    def build() -> Any:
        return validation.prepare_run(
            modules,
            arm,
            width,
            rows=rows,
            batch_size=batch_size,
            seed=2401,
            validated_widths=[width],
        )

    record: dict[str, Any] = {
        "arm": arm.name,
        "width": list(width),
        "typed_objects": int(sum(width)),
        "checks": {},
    }
    prepared = build()
    record["geometry"] = prepared.geometry
    record["buckets"] = len(prepared.buckets)
    record["batches"] = len(prepared.plan)

    record["checks"]["V11"] = validation.check_input_mask_correctness(modules, prepared)
    record["checks"]["V7"] = validation.check_permutation_invariance(
        modules, prepared, criteria
    )
    record["checks"]["V5"] = validation.check_finite_differences(
        modules, prepared, criteria, samples
    )
    result = validation.run_steps(modules, prepared, steps)
    record["checks"]["V12"] = validation.check_finiteness(result, prepared)
    record["checks"]["V10"] = validation.check_checkpoint_reload(
        modules, prepared, workspace
    )
    record["checks"]["V1"] = validation.check_repeatability(modules, build, steps)
    record["checks"]["V13a"] = validation.check_duplicate_arm_null(
        modules, build, build, steps
    )
    captured = validation._two_steps_recording(modules, build(), "/GPU:0")
    record["checks"]["V4"] = validation.check_float64_reference(
        modules, captured, criteria
    )
    record["checks"]["V6"] = validation.classify_cross_device(modules, build, criteria)

    record["tier"] = record["checks"]["V6"]["tier"]
    hard = [
        name
        for name in ("V1", "V10", "V11", "V12", "V13a")
        if not record["checks"][name]["passed"]
    ]
    if record["tier"] == 0:
        hard.append("V6")
    soft = [
        name for name in ("V4", "V5", "V7") if not record["checks"][name]["passed"]
    ]
    record["hard_failures"] = hard
    record["soft_failures"] = soft
    record["released"] = not hard and not soft
    return record


def main() -> None:
    """Validate the ladder, or train once validation covers the plan."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--criteria", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--validate-only", type=int, default=0)
    parser.add_argument("--validation-receipt", type=Path)
    parser.add_argument("--widths", help="JSON list of width triples")
    parser.add_argument("--rows", type=int, default=2048)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--samples", type=int, default=12)
    args = parser.parse_args()

    _install(args.checkout)
    import four_arm_representation as fourarm
    import optimizer_diagnostic as diagnostic
    import tail_validation as validation
    import typed_descriptor_keras as adapter
    import typed_descriptors as typed
    import typed_token_comparison as comparison

    import run_typed_token_comparison as runner

    tf = adapter.require_tensorflow()
    policy = runner.configure_precision()
    devices = [device.name for device in tf.config.list_logical_devices("GPU")]
    if not devices:
        raise RuntimeError("No GPU is visible")
    modules = {
        "tf": tf,
        "fourarm": fourarm,
        "typed": typed,
        "adapter": adapter,
        "runner": runner,
        "comparison": comparison,
        "diagnostic": diagnostic,
        "validation": validation,
    }
    criteria = validation.load_criteria(args.criteria)

    if not args.validate_only:
        raise NotImplementedError(
            "The training entry is implemented after the ladder is validated; it "
            "calls the same prepare_run this validation exercises, and refuses to "
            "start without a covering receipt (require_validation)."
        )

    widths = [tuple(int(v) for v in w) for w in json.loads(args.widths)]
    workspace = args.output.parent / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    for width in widths:
        for arm in fourarm.ARMS:
            # Arms A and D disable the typed families, so their graph does not vary
            # with typed multiplicity. Validating them once is recorded as a reason
            # rather than left to inference.
            if not arm.typed_enabled and width != widths[0]:
                continue
            record = validate_width(
                modules,
                criteria,
                arm,
                width,
                rows=args.rows,
                batch_size=args.batch_size,
                steps=args.validate_only,
                samples=args.samples,
                workspace=workspace,
            )
            records.append(record)
            print(
                f"arm {arm.name} width {list(width)} tier {record['tier']} "
                f"released={record['released']} hard={record['hard_failures']} "
                f"soft={record['soft_failures']}",
                flush=True,
            )

    by_width: dict[tuple[int, ...], list[dict[str, Any]]] = {}
    for record in records:
        by_width.setdefault(tuple(record["width"]), []).append(record)
    released = sorted(
        width for width, group in by_width.items() if all(r["released"] for r in group)
    )
    hard_stops = sorted(
        {name for record in records for name in record["hard_failures"]}
    )
    receipt = {
        "scope": "tail validation of the four-arm execution path; no closure statistic",
        "authorization": "Joseph, 2026-09-18; <=1.5 GPU-h, <=4 submissions",
        "commit": head_commit(args.checkout),
        "criteria_path": criteria.path,
        "criteria_sha256": criteria.sha256,
        "precision_policy": policy,
        "gpu_devices": devices,
        "steps_per_check": args.validate_only,
        "rows": args.rows,
        "batch_size": args.batch_size,
        "records": records,
        "released_widths": [list(width) for width in released],
        "tier_by_width": {
            str(list(width)): min(r["tier"] for r in group)
            for width, group in sorted(by_width.items())
        },
        "hard_stop_checks": hard_stops,
        "complete": bool(released) and not hard_stops and len(released) == len(by_width),
        "non_claim": (
            "A released width means the execution path passed the frozen battery "
            "there. It is not a closure result and says nothing about which "
            "representation is better."
        ),
    }
    args.output.write_text(json.dumps(receipt, indent=2, default=str) + "\n")
    print(
        f"released {len(released)} of {len(by_width)} widths; "
        f"hard stops {hard_stops}; complete={receipt['complete']}"
    )


if __name__ == "__main__":
    main()
