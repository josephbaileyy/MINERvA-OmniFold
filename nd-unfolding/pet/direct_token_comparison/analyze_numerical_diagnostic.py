"""Reduce saved numerical traces; no result releases calibration or training."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from numerical_diagnostic import (
    ATOL,
    RTOL,
    digest,
    save_errors,
    write_json,
    verify_seal,
)

CELLS = ("on-0", "off-0", "off-1", "on-1")


def compare_trace(
    left: Path, right: Path, output: Path, *, shared: bool = False
) -> dict[str, Any]:
    """Save all elementwise comparisons and identify the first changed operation."""
    output.mkdir(parents=True, exist_ok=False)
    nodes = json.loads((left / "index.json").read_text())
    other_nodes = json.loads((right / "index.json").read_text())
    if [node["name"] for node in nodes] != [node["name"] for node in other_nodes]:
        raise ValueError("Trace operation inventory mismatch")
    records = {}
    for node in nodes:
        with np.load(left / node["file"], allow_pickle=False) as source:
            cpu = dict(source)
        with np.load(right / node["file"], allow_pickle=False) as source:
            target = dict(source)
        key = "shared_output" if shared else "output"
        records[node["name"]] = save_errors(
            output / node["file"], cpu["output"], target[key]
        )
        if shared:
            if not np.array_equal(cpu["a"], target["shared_a"]) or not np.array_equal(
                cpu["b"], target["shared_b"]
            ):
                raise ValueError("Common-operand replay changed inputs")
    for name, key in (
        ("route", "actual"),
        *[
            (f"{family}.prepared", "actual")
            for family in ("photons", "blobs", "prongs")
        ],
    ):
        if shared:
            break
        with np.load(left / f"{name}.npz", allow_pickle=False) as source:
            a = source[key]
        with np.load(right / f"{name}.npz", allow_pickle=False) as source:
            b = source[key]
        records[name] = save_errors(output / f"{name}.npz", a, b)
    if not shared:
        for key in ("mask", "counts"):
            with np.load(left / "route.npz", allow_pickle=False) as source:
                a = source[key]
            with np.load(right / "route.npz", allow_pickle=False) as source:
                b = source[key]
            records["route." + key] = save_errors(output / f"route.{key}.npz", a, b)
            records["route." + key]["passes"] = bool(np.array_equal(a, b))
    result = {
        "first_unequal_operation": next(
            (key for key, value in records.items() if value.get("unequal_elements", 1)),
            None,
        ),
        "first_tolerance_failure": next(
            (key for key, value in records.items() if not value["passes"]), None
        ),
        "failing_elements": sum(
            value.get("failing_elements", 0) for value in records.values()
        ),
        "compared_elements": sum(
            value.get("elements", 0) for value in records.values()
        ),
        "maximum_absolute_error": max(
            (value.get("maximum_absolute_error") or 0 for value in records.values()),
            default=0,
        ),
        "comparisons": records,
    }
    write_json(output / "summary.json", result)
    return result


def float64_comparisons(trace: Path, propagated: Path, output: Path) -> dict[str, Any]:
    """Save local-operand and propagated float64 errors and roundoff envelopes."""
    output.mkdir(parents=True, exist_ok=False)
    nodes = json.loads((trace / "index.json").read_text())
    records = {}
    with np.load(propagated, allow_pickle=False) as source:
        chain = dict(source)
    for node in nodes:
        name = node["name"]
        with np.load(trace / node["file"], allow_pickle=False) as source:
            arrays = dict(source)
        records[name] = {
            "local": save_errors(
                output / f"{name}.local.npz", arrays["output"], arrays["reference64"]
            )
        }
        local_error = np.abs(
            arrays["output"].astype(np.float64) - arrays["reference64"]
        )
        payload = {
            "local_absolute_error": local_error,
            "local_fp32_bound": arrays["ordinary_fp32_bound"],
            "local_exceeds_illustrative_bound": local_error
            > arrays["ordinary_fp32_bound"],
        }
        if name in chain:
            records[name]["propagated"] = save_errors(
                output / f"{name}.propagated.npz", arrays["output"], chain[name]
            )
            propagated_error = np.abs(arrays["output"].astype(np.float64) - chain[name])
            payload.update(
                propagated_absolute_error=propagated_error,
                propagated_fp32_bound=chain[name + ".bound"],
                propagated_exceeds_illustrative_bound=propagated_error
                > chain[name + ".bound"],
            )
        records[name]["illustrative_budget"] = {
            "local_exceeding_elements": int(
                np.count_nonzero(payload["local_exceeds_illustrative_bound"])
            ),
            "propagated_exceeding_elements": (
                int(np.count_nonzero(payload["propagated_exceeds_illustrative_bound"]))
                if "propagated_exceeds_illustrative_bound" in payload
                else None
            ),
            "changes_acceptance_criteria": False,
        }
        np.savez(output / f"{name}.budget.npz", **payload)
    write_json(output / "summary.json", records)
    return records


def analyze(directory: Path, output: Path, device: str) -> dict[str, Any]:
    """Measure four predeclared process cells and fail closed on capture integrity."""
    output.mkdir(parents=True, exist_ok=False)
    settings, captures = {}, {}
    results: dict[str, Any] = {
        "scope": "Numerical diagnostic only",
        "calibration_authorized": False,
        "atol": ATOL,
        "rtol": RTOL,
        "cells": {},
        "repeatability": {},
        "between_policy": {},
        "integrity_errors": [],
    }
    for cell in CELLS:
        path = directory / cell
        verify_seal(path)
        if (
            json.loads((path / "terminal.json").read_text())["terminal"]
            != "COMPLETE_DIAGNOSTIC"
        ):
            raise ValueError("Incomplete worker: " + cell)
        settings[cell] = json.loads((path / "settings.json").read_text())
        captures[cell] = json.loads((path / "capture.json").read_text())
        if settings[cell]["requested_device"] != device or settings[cell][
            "tf32_enabled"
        ] != cell.startswith("on"):
            results["integrity_errors"].append(
                cell + ": device or TF32 setting mismatch"
            )
        if (
            not settings[cell]["determinism_enabled"]
            or settings[cell]["mixed_precision_global_policy"] != "float32"
        ):
            results["integrity_errors"].append(
                cell + ": precision/determinism mismatch"
            )
        parity = captures[cell]["parity"]
        if not all(
            all(value.values()) if isinstance(value, dict) else value
            for value in parity.values()
        ):
            results["integrity_errors"].append(
                cell + ": instrumentation/weight parity failure"
            )
        for label in ("cpu", "target"):
            for repetition in range(3):
                nodes = json.loads(
                    (path / f"{label}-{repetition}/index.json").read_text()
                )
                expected = "GPU:0" if label == "target" and device == "gpu" else "CPU:0"
                if any(expected not in node["device"] for node in nodes):
                    results["integrity_errors"].append(
                        cell + ": operation device mismatch"
                    )
                if any(node["dtype"] != "<f4" for node in nodes):
                    results["integrity_errors"].append(
                        cell + ": non-FP32 operation output"
                    )
        results["cells"][cell] = {
            "cpu_target": compare_trace(
                path / "cpu-0", path / "target-0", output / cell / "cpu-target"
            ),
            "common_operands": compare_trace(
                path / "cpu-0",
                path / "target-0",
                output / cell / "common-operands",
                shared=True,
            ),
        }
        for label in ("cpu", "target"):
            float64_comparisons(
                path / f"{label}-0",
                path / "propagated64.npz",
                output / cell / (label + "-float64"),
            )
            for repetition in (1, 2):
                key = f"{cell}-{label}-repeat{repetition}"
                results["repeatability"][key] = compare_trace(
                    path / f"{label}-0", path / f"{label}-{repetition}", output / key
                )
    if len({entry["pid"] for entry in settings.values()}) != 4:
        results["integrity_errors"].append("Four separate processes are required")
    for field in ("source_sha256", "versions"):
        if any(settings[cell][field] != settings[CELLS[0]][field] for cell in CELLS):
            results["integrity_errors"].append("Cross-process mismatch: " + field)
    if any(
        captures[cell]["bundle_hashes"] != captures[CELLS[0]]["bundle_hashes"]
        for cell in CELLS
    ):
        results["integrity_errors"].append("Cross-process input/weight/config mismatch")
    for label in ("cpu", "target"):
        for mode in ("on", "off"):
            key = f"{mode}-{label}-cross-process"
            results["repeatability"][key] = compare_trace(
                directory / f"{mode}-0/{label}-0",
                directory / f"{mode}-1/{label}-0",
                output / key,
            )
        key = label + "-on-off"
        results["between_policy"][key] = compare_trace(
            directory / f"on-0/{label}-0", directory / f"off-0/{label}-0", output / key
        )
    results["repeatability_exact"] = all(
        record["first_unequal_operation"] is None
        for record in results["repeatability"].values()
    )
    if not results["repeatability_exact"]:
        results["integrity_errors"].append(
            "Same-device repeatability failed; retain numerical evidence"
        )
    results["terminal"] = (
        "COMPLETE_DIAGNOSTIC"
        if not results["integrity_errors"]
        else "INSTRUMENT_INVALID"
    )
    write_json(output / "summary.json", results)
    inventory = {
        str(path.relative_to(directory)): digest(path)
        for path in directory.rglob("*")
        if path.is_file() and path.name != "artifact-manifest.json"
    }
    write_json(output / "artifact-manifest.json", inventory)
    return results


def main() -> None:
    """Write measurements before reporting any instrument-integrity failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", choices=("cpu", "gpu"), required=True)
    args = parser.parse_args()
    result = analyze(args.directory, args.output, args.device)
    if result["integrity_errors"]:
        raise SystemExit("Diagnostic instrument invalid; saved evidence retained")


if __name__ == "__main__":
    main()
