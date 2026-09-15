"""Re-derive the amended GPU preflight's terminal failure from preserved arrays.

The amended preflight captures inputs, parameters, derivatives, optimizer states
and updates *before* its numerical assertions, so the arrays that decided a
failure survive the failure. This reads those arrays back and reports, per case,
which named tensors exceed the unchanged acceptance tolerance.

It re-applies the launcher's own constants rather than restating a verdict: the
comparison is ``np.allclose(atol=1e-5, rtol=1e-4)``, matching
``compatibility_preflight.ATOL/RTOL``, and the single exempted tensor is the
attention key bias named by ``optimizer_equivalence.key_bias_index``.

This is read-only accounting over preserved evidence. It runs no model, needs no
GPU or TensorFlow, and it cannot convert a failed gate into a passing one.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

# Mirrors compatibility_preflight.ATOL / RTOL; the gate's criterion is unchanged.
ATOL = 1e-5
RTOL = 1e-4
# Mirrors optimizer_equivalence.key_bias_index's structural result.
EXEMPT_INDEX = 27
EXEMPT_TENSOR = f"weight_{EXEMPT_INDEX}"


def _paths(case: Path) -> tuple[Path, Path]:
    """Return the CPU and candidate subdirectories for one case."""
    return case / "cpu", case / "candidate"


def _tensor_name(inventory: Path, index: int) -> str:
    """Resolve a weight index to its recorded variable path, if available."""
    if not inventory.exists():
        return f"weight_{index} (inventory absent)"
    weights = json.loads(inventory.read_text())["weights"]
    return str(weights[index]["path"])


def compare_case(case: Path) -> dict[str, Any]:
    """Report every tensor in one case that exceeds the unchanged tolerance."""
    cpu, candidate = _paths(case)
    inventory = cpu / "variables.json"
    prediction = max(
        float(
            np.max(
                np.abs(
                    np.load(cpu / "prediction.npz")[key].astype(float)
                    - np.load(candidate / "prediction.npz")[key].astype(float)
                )
            )
        )
        for key in np.load(cpu / "prediction.npz").files
    )
    exceeding: list[dict[str, Any]] = []
    worst_slot = 0.0
    for step in (1, 2):
        left = np.load(cpu / f"state-{step}.npz")
        right = np.load(candidate / f"state-{step}.npz")
        if set(left.files) != set(right.files):
            raise ValueError(f"Tensor inventory differs: {case.name} step {step}")
        for name in sorted(left.files):
            a, b = left[name], right[name]
            error = float(np.max(np.abs(a.astype(float) - b.astype(float)), initial=0))
            if name.startswith("slot_"):
                worst_slot = max(worst_slot, error)
            if np.allclose(a, b, atol=ATOL, rtol=RTOL):
                continue
            index = int(name.split("_")[1]) if name.startswith("weight_") else -1
            exceeding.append(
                {
                    "tensor": name,
                    "path": _tensor_name(inventory, index) if index >= 0 else name,
                    "step": step,
                    "shape": list(a.shape),
                    "max_abs": error,
                    "exempted": name == EXEMPT_TENSOR,
                }
            )
    non_exempt = [record for record in exceeding if not record["exempted"]]
    return {
        "case": case.name,
        "gate_record_present": (case / "gate.json").exists(),
        "prediction_max_abs": prediction,
        "worst_optimizer_slot_max_abs": worst_slot,
        "tensors_exceeding_tolerance": exceeding,
        "non_exempt_violations": len(non_exempt),
        "verdict": "WITHIN-AMENDED-GATE" if not non_exempt else "OUTSIDE-AMENDED-GATE",
    }


def analyze(preflight: Path) -> dict[str, Any]:
    """Summarize every captured case under a preflight output directory."""
    cases = sorted(
        path
        for path in preflight.iterdir()
        if path.is_dir() and (path / "cpu" / "state-1.npz").exists()
    )
    if not cases:
        raise ValueError(f"No captured cases under {preflight}")
    results = [compare_case(case) for case in cases]
    outside = [r["case"] for r in results if r["verdict"] == "OUTSIDE-AMENDED-GATE"]
    return {
        "scope": "read-only accounting of a terminal GPU preflight failure",
        "tolerance": {"atol": ATOL, "rtol": RTOL},
        "exempted_tensor": EXEMPT_TENSOR,
        "cases": results,
        "cases_outside_amended_gate": outside,
        "terminal": "PREFLIGHT-FAILED" if outside else "NO-NON-EXEMPT-VIOLATION",
        "non_claim": (
            "A failed gate stays failed. This accounting does not authorize a retry, "
            "a tolerance change, a further exemption, or any learning conclusion."
        ),
    }


def main() -> None:
    """Write the re-derived failure accounting beside the preserved evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preflight",
        type=Path,
        required=True,
        help="Preserved preflight directory containing per-case cpu/ and candidate/",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.preflight)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(result["terminal"], "->", ", ".join(result["cases_outside_amended_gate"]))


if __name__ == "__main__":
    main()
