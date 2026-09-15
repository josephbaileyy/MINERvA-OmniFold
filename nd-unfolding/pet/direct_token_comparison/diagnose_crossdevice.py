"""Decompose a cross-device weight divergence into gradient, Adam and geometry parts.

Implements stage D1 of
``CROSSDEVICE_DIAGNOSTIC_SPECIFICATION-20260915.md`` over evidence the amended
preflight captured *before* its assertions, so a failed run's deciding arrays are
still available. It runs offline: no GPU, no TensorFlow, no allocation.

A post-Adam weight difference has at least two causes with opposite consequences.
Either the forward/backward computation agrees and Adam amplified float32 gradient
rounding in a small-gradient coordinate, or the code path genuinely computes
something different across devices. Reporting only the weight difference cannot tell
them apart, so this separates the operands from the arithmetic:

* ``replay-{origin}-{device}`` replays Adam from one frozen initial state using one
  origin's captured gradients on both devices. Identical operands, different device,
  so any disagreement is Adam arithmetic rather than a different gradient.
* ``float64-{origin}-{step}`` replays the same operands in float64, bracketing each
  native float32 trajectory.

The decision rule is predeclared in the specification and is applied here as written;
this module selects a branch, it does not invent one.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

# Unchanged acceptance tolerance; mirrors compatibility_preflight.ATOL / RTOL.
ATOL = 1e-5
RTOL = 1e-4
# Predeclared branch thresholds from the specification.
GRADIENT_LIMIT = 1e-6
COMMON_OPERAND_LIMIT = 1e-7
PREDICTION_LIMIT = 1e-5
# The one approved exemption, and the tensor that failed job 58354898.
EXEMPT = "weight_27"
SUBJECT = "weight_24"
WEIGHTS = 42
ORIGINS = ("cpu", "candidate")
PHASES = {1: "eager.npz", 2: "second.npz"}


def _max_abs(left: Any, right: Any) -> float:
    """Return the maximum absolute difference between two arrays."""
    return float(
        np.max(np.abs(np.asarray(left, float) - np.asarray(right, float)), initial=0.0)
    )


def _worst(left: Any, right: Any, names: list[str]) -> tuple[str, float]:
    """Return the worst-disagreeing name and its error over shared keys."""
    worst, value = "", 0.0
    for name in names:
        error = _max_abs(left[name], right[name])
        if error >= value:
            worst, value = name, error
    return worst, value


def gradient_agreement(case: Path) -> dict[str, Any]:
    """M1: per-weight CPU-vs-GPU gradient agreement at both Adam steps."""
    result: dict[str, Any] = {}
    for step, filename in PHASES.items():
        left = np.load(case / "cpu" / filename)
        right = np.load(case / "candidate" / filename)
        names = [f"gradient_{i}" for i in range(WEIGHTS)]
        worst, value = _worst(left, right, names)
        subject = int(SUBJECT.split("_")[1])
        result[f"step{step}"] = {
            "worst_tensor": worst,
            "worst_max_abs": value,
            "subject_max_abs": _max_abs(
                left[f"gradient_{subject}"], right[f"gradient_{subject}"]
            ),
            "subject_gradient_scale": float(
                np.max(np.abs(np.asarray(left[f"gradient_{subject}"], float)))
            ),
            "loss_max_abs": _max_abs(left["loss"], right["loss"]),
        }
    return result


def common_operand_replay(case: Path) -> dict[str, Any]:
    """M2: same gradient operands replayed on both devices, per origin."""
    result: dict[str, Any] = {}
    for origin in ORIGINS:
        per_origin: dict[str, Any] = {}
        for step in (1, 2):
            left = np.load(case / f"replay-{origin}-cpu" / f"step-{step}.npz")
            right = np.load(case / f"replay-{origin}-candidate" / f"step-{step}.npz")
            if set(left.files) != set(right.files):
                raise ValueError(f"Replay inventory differs: {case.name} {origin}")
            weights = sorted(n for n in left.files if n.startswith("weight_"))
            slots = sorted(n for n in left.files if n.startswith("slot_"))
            worst_weight, weight_error = _worst(left, right, weights)
            worst_slot, slot_error = _worst(left, right, slots)
            per_origin[f"step{step}"] = {
                "worst_weight": worst_weight,
                "worst_weight_max_abs": weight_error,
                "worst_slot": worst_slot,
                "worst_slot_max_abs": slot_error,
            }
        result[origin] = per_origin
    return result


def float64_bracketing(case: Path) -> dict[str, Any]:
    """M3: does float64 Adam on an origin's own gradients reproduce its trajectory?"""
    result: dict[str, Any] = {}
    for origin in ORIGINS:
        native_root = case / ("cpu" if origin == "cpu" else "candidate")
        per_origin: dict[str, Any] = {}
        for step in (1, 2):
            high = np.load(case / f"float64-{origin}-{step}.npz")
            native = np.load(native_root / f"state-{step}.npz")
            names = [f"weight_{i}" for i in range(WEIGHTS)]
            worst, value = _worst(high, native, names)
            within = all(
                np.allclose(high[n], native[n], atol=ATOL, rtol=RTOL) for n in names
            )
            per_origin[f"step{step}"] = {
                "worst_weight": worst,
                "worst_max_abs": value,
                "within_tolerance": bool(within),
            }
        result[origin] = per_origin
    return result


def token_geometry(case: Path) -> dict[str, Any]:
    """M4: token-position count and padded fraction implied by the packed cloud."""
    result: dict[str, Any] = {}
    for origin in ORIGINS:
        arrays = np.load(case / f"{origin}-tokens.npz")
        cloud, presence = arrays["token_0"], arrays["token_1"]
        positions = int(np.prod(presence.shape))
        active = int(np.count_nonzero(presence))
        result[origin] = {
            "cloud_shape": list(cloud.shape),
            "presence_shape": list(presence.shape),
            "token_positions": positions,
            "active_positions": active,
            "padded_positions": positions - active,
            "padded_fraction": (positions - active) / positions if positions else 0.0,
        }
    return result


def amplification(case: Path) -> dict[str, Any]:
    """M5: ratio of post-Adam weight difference to gradient difference."""
    result: dict[str, Any] = {}
    for step, filename in PHASES.items():
        gradient_left = np.load(case / "cpu" / filename)
        gradient_right = np.load(case / "candidate" / filename)
        weight_left = np.load(case / "cpu" / f"state-{step}.npz")
        weight_right = np.load(case / "candidate" / f"state-{step}.npz")
        rows: list[dict[str, Any]] = []
        for index in range(WEIGHTS):
            gradient_error = _max_abs(
                gradient_left[f"gradient_{index}"], gradient_right[f"gradient_{index}"]
            )
            weight_error = _max_abs(
                weight_left[f"weight_{index}"], weight_right[f"weight_{index}"]
            )
            rows.append(
                {
                    "tensor": f"weight_{index}",
                    "gradient_max_abs": gradient_error,
                    "weight_max_abs": weight_error,
                    "ratio": (
                        (weight_error / gradient_error) if gradient_error > 0 else None
                    ),
                }
            )
        rows.sort(key=lambda row: float(row["weight_max_abs"]), reverse=True)
        result[f"step{step}"] = rows[:5]
    return result


def decide(case_result: dict[str, Any]) -> dict[str, Any]:
    """Apply the specification's predeclared branch rule, in its stated order."""
    gradients = case_result["M1_gradient_agreement"]
    common = case_result["M2_common_operand_replay"]
    high = case_result["M3_float64_bracketing"]
    prediction = case_result["prediction_max_abs"]

    bracketing_holds = all(
        step["within_tolerance"] for origin in high.values() for step in origin.values()
    )
    worst_common = max(
        max(step["worst_weight_max_abs"], step["worst_slot_max_abs"])
        for origin in common.values()
        for step in origin.values()
    )
    worst_subject_gradient = max(step["subject_max_abs"] for step in gradients.values())

    if not bracketing_holds:
        branch, reason = "C", "A float64 replay does not reproduce its own trajectory"
    elif worst_subject_gradient > GRADIENT_LIMIT or worst_common > COMMON_OPERAND_LIMIT:
        branch, reason = (
            "B",
            "Gradients or identical-operand Adam disagree beyond the predeclared limits",
        )
    elif prediction <= PREDICTION_LIMIT:
        branch, reason = (
            "A",
            "Computation agrees; divergence is Adam amplification of gradient rounding",
        )
    else:
        branch, reason = "B", "Predictions disagree beyond the predeclared limit"
    return {
        "branch": branch,
        "reason": reason,
        "worst_subject_gradient_max_abs": worst_subject_gradient,
        "worst_common_operand_max_abs": worst_common,
        "float64_bracketing_holds": bracketing_holds,
        "prediction_max_abs": prediction,
    }


def analyze_case(case: Path) -> dict[str, Any]:
    """Run every D1 measurement for one case and apply the decision rule."""
    result: dict[str, Any] = {
        "case": case.name,
        "prediction_max_abs": _max_abs(
            np.load(case / "cpu" / "prediction.npz")["prediction"],
            np.load(case / "candidate" / "prediction.npz")["prediction"],
        ),
        "M1_gradient_agreement": gradient_agreement(case),
        "M2_common_operand_replay": common_operand_replay(case),
        "M3_float64_bracketing": float64_bracketing(case),
        "M4_token_geometry": token_geometry(case),
        "M5_amplification": amplification(case),
    }
    result["decision"] = decide(result)
    return result


def analyze(preflight: Path) -> dict[str, Any]:
    """Analyze every captured case, so the failing one has passing controls."""
    cases = sorted(
        path
        for path in preflight.iterdir()
        if path.is_dir() and (path / "cpu" / "state-1.npz").exists()
    )
    if not cases:
        raise ValueError(f"No captured cases under {preflight}")
    results = [analyze_case(case) for case in cases]
    branches = {r["case"]: r["decision"]["branch"] for r in results}
    return {
        "scope": "offline decomposition of a cross-device divergence; no GPU was used",
        "tolerance": {"atol": ATOL, "rtol": RTOL},
        "thresholds": {
            "gradient": GRADIENT_LIMIT,
            "common_operand": COMMON_OPERAND_LIMIT,
            "prediction": PREDICTION_LIMIT,
        },
        "exempt_tensor": EXEMPT,
        "subject_tensor": SUBJECT,
        "cases": results,
        "branch_by_case": branches,
        "non_claim": (
            "A reproducibility decomposition. It does not measure learning, closure or "
            "compute cost, and it is not evidence for or against any representation."
        ),
    }


def main() -> None:
    """Write the D1 decomposition beside the preserved evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.preflight)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    for case, branch in result["branch_by_case"].items():
        print(f"{case}: branch {branch}")


if __name__ == "__main__":
    main()
