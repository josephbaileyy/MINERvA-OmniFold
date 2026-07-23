#!/usr/bin/env python3
"""Aggregate matched PET2 fixture pilots without selecting on their outcome."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from .artifacts import write_json
from .utils import file_sha256, fingerprint

DIRECT_PARENT = {
    "D-view": "C",
    "D-typed": "C",
    "E-muon": "C",
    "E-rich-no-charge": "E-muon",
    "E-rich": "E-rich-no-charge",
}


def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _extract_run(summary_path: Path) -> dict[str, Any]:
    summary = _load(summary_path)
    if summary.get("status") != "complete_experimental_fixture":
        raise ValueError(f"incomplete pilot summary: {summary_path}")
    if not summary.get("recipe", {}).get("comparison_claim_permitted"):
        raise ValueError(f"non-matched recipe in aggregate: {summary_path}")
    results = summary.get("results", {})
    if len(results) != 1:
        raise ValueError(f"one-arm/one-seed result required: {summary_path}")
    arm, result = next(iter(results.items()))
    seed = int(result["estimator_seed"])
    metrics = result.get("conditional_closure")
    if not metrics:
        raise ValueError(f"missing analytic closure metrics: {summary_path}")
    receipt_path = summary_path.parent / result["relative_path"] / "receipt.json"
    receipt = _load(receipt_path)
    iterations = receipt.get("omnifold_iterations", {}).get(
        "complete_iteration_receipts", []
    )
    if not iterations:
        raise ValueError(f"missing complete iteration receipts: {receipt_path}")
    peak_memory = max(
        int(step.get("peak_gpu_memory_bytes", 0))
        for iteration in iterations
        for step in (iteration["step1_fit"], iteration["step2_fit"])
    )
    final = iterations[-1]
    projection_l1 = max(
        value["relative_l1"]
        for value in metrics["projection_residuals"].values()
    )
    return {
        "arm": arm,
        "seed": seed,
        "summary_path": str(summary_path),
        "summary_sha256": file_sha256(summary_path),
        "receipt_path": str(receipt_path),
        "receipt_sha256": file_sha256(receipt_path),
        "source_commit": receipt["git"]["commit"],
        "source_dirty": bool(receipt["git"]["dirty"]),
        "recipe_fingerprint": result["recipe_fingerprint"],
        "log_ratio_rmse": float(metrics["log_ratio_residual"]["rmse"]),
        "log_ratio_bias": float(metrics["log_ratio_residual"]["bias"]),
        "max_projection_relative_l1": float(projection_l1),
        "global_ess": float(metrics["ess"]["global_predicted"]),
        "tail_ess": float(metrics["ess"]["declared_tail_predicted"]),
        "cap_saturated_count": int(
            metrics["cap_saturation"]["total_saturated_count"]
        ),
        "runtime_seconds": float(result["runtime_seconds"]),
        "peak_gpu_memory_bytes": peak_memory,
        "final_step1_validation_bce": float(
            final["step1_evaluation"]["validation"]["balanced_weighted_bce"]
        ),
        "final_step1_test_bce": float(
            final["step1_evaluation"]["test"]["balanced_weighted_bce"]
        ),
        "final_step2_validation_bce": float(
            final["step2_evaluation"]["validation"]["balanced_weighted_bce"]
        ),
        "final_step2_test_bce": float(
            final["step2_evaluation"]["test"]["balanced_weighted_bce"]
        ),
    }


def _summary(values: list[float]) -> dict[str, float]:
    return {
        "mean": float(mean(values)),
        "population_std": float(pstdev(values)) if len(values) > 1 else 0.0,
        "min": float(min(values)),
        "max": float(max(values)),
    }


def aggregate(
    summary_paths: list[Path],
    *,
    expected_arms: tuple[str, ...],
    expected_seeds: tuple[int, ...],
) -> dict[str, Any]:
    runs = [_extract_run(path.resolve()) for path in summary_paths]
    keyed = {(item["arm"], item["seed"]): item for item in runs}
    if len(keyed) != len(runs):
        raise ValueError("duplicate arm/seed result")
    expected = {(arm, seed) for arm in expected_arms for seed in expected_seeds}
    missing = sorted(expected - set(keyed))
    extra = sorted(set(keyed) - expected)
    if missing or extra:
        raise ValueError(f"pilot inventory mismatch: missing={missing}, extra={extra}")
    commits = {item["source_commit"] for item in runs}
    dirty = [item for item in runs if item["source_dirty"]]
    if len(commits) != 1 or dirty:
        raise ValueError(
            f"pilot source footing differs or is dirty: commits={commits}, "
            f"dirty={[(x['arm'], x['seed']) for x in dirty]}"
        )
    metric_names = (
        "log_ratio_rmse",
        "log_ratio_bias",
        "max_projection_relative_l1",
        "global_ess",
        "tail_ess",
        "cap_saturated_count",
        "runtime_seconds",
        "peak_gpu_memory_bytes",
        "final_step1_validation_bce",
        "final_step1_test_bce",
        "final_step2_validation_bce",
        "final_step2_test_bce",
    )
    arms = {}
    for arm in expected_arms:
        selected = [keyed[(arm, seed)] for seed in expected_seeds]
        arms[arm] = {
            "seeds": list(expected_seeds),
            "metrics": {
                name: _summary([float(item[name]) for item in selected])
                for name in metric_names
            },
        }
    comparisons = {}
    for child, parent in DIRECT_PARENT.items():
        if child not in arms or parent not in arms:
            continue
        parent_rmse = arms[parent]["metrics"]["log_ratio_rmse"]["mean"]
        child_rmse = arms[child]["metrics"]["log_ratio_rmse"]["mean"]
        closure_improvement = 100.0 * (parent_rmse - child_rmse) / parent_rmse
        parent_ess = arms[parent]["metrics"]["global_ess"]["mean"]
        child_ess = arms[child]["metrics"]["global_ess"]["mean"]
        ess_degradation = 100.0 * (parent_ess - child_ess) / parent_ess
        per_seed_improvement = [
            keyed[(parent, seed)]["log_ratio_rmse"]
            - keyed[(child, seed)]["log_ratio_rmse"]
            for seed in expected_seeds
        ]
        cap_not_worse = (
            arms[child]["metrics"]["cap_saturated_count"]["mean"]
            <= arms[parent]["metrics"]["cap_saturated_count"]["mean"]
        )
        beneficial = (
            closure_improvement > 5.0
            and ess_degradation <= 10.0
            and all(value > 0 for value in per_seed_improvement)
            and cap_not_worse
        )
        if beneficial:
            decision = "beneficial-on-synthetic-pilot"
        elif closure_improvement < -5.0 or ess_degradation > 10.0:
            decision = "harmful-or-unstable-on-synthetic-pilot"
        elif abs(closure_improvement) <= 5.0 and abs(ess_degradation) <= 10.0:
            decision = "neutral-at-preregistered-pilot-threshold"
        else:
            decision = "insufficiently-validated"
        comparisons[f"{child}_vs_{parent}"] = {
            "closure_rmse_improvement_percent": closure_improvement,
            "global_ess_degradation_percent": ess_degradation,
            "per_seed_closure_rmse_improvement": per_seed_improvement,
            "direction_reproduced_all_seeds": all(
                value > 0 for value in per_seed_improvement
            ),
            "cap_saturation_not_worse": cap_not_worse,
            "decision": decision,
            "publication_promotion_permitted": False,
        }
    payload = {
        "status": "complete_matched_synthetic_pilot_aggregate",
        "evidence_class": "synthetic-fixture",
        "source_commit": next(iter(commits)),
        "expected_arms": list(expected_arms),
        "expected_seeds": list(expected_seeds),
        "runs": sorted(runs, key=lambda item: (item["arm"], item["seed"])),
        "arms": arms,
        "comparisons": comparisons,
        "decision_thresholds": {
            "closure_improvement_percent_strictly_greater_than": 5.0,
            "global_ess_degradation_percent_maximum": 10.0,
            "direction_must_repeat_all_seeds": True,
            "cap_saturation_must_not_worsen": True,
        },
        "g2_validation_claim": False,
        "publication_promotion_permitted": False,
    }
    payload["fingerprint"] = fingerprint(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--arms",
        nargs="+",
        default=[
            "C",
            "D-view",
            "D-typed",
            "E-muon",
            "E-rich-no-charge",
            "E-rich",
        ],
    )
    parser.add_argument("--seeds", nargs="+", type=int, default=[101, 202, 303])
    args = parser.parse_args()
    base = Path(args.base).expanduser().resolve()
    paths = sorted(base.glob("pet2x_matched-pilot_*_job*/summary.json"))
    if not paths:
        raise FileNotFoundError(f"no matched-pilot summaries under {base}")
    result = aggregate(
        paths,
        expected_arms=tuple(args.arms),
        expected_seeds=tuple(args.seeds),
    )
    write_json(args.out, result)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
