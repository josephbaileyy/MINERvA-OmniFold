#!/usr/bin/env python3
"""Aggregate matched current-engine TensorFlow A/B synthetic pilots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from .artifacts import write_json
from .utils import file_sha256, fingerprint

METRICS = (
    "log_ratio_rmse",
    "log_ratio_bias",
    "max_projection_relative_l1",
    "global_ess",
    "tail_ess",
    "predicted_ratio_q99",
    "predicted_ratio_max",
    "predicted_truth_weight_q99",
    "predicted_truth_weight_max",
    "direction_gate_pass",
    "runtime_seconds",
    "peak_gpu_memory_bytes",
    "signal_rows_per_wall_second",
)


def _summary(values: list[float]) -> dict[str, float]:
    return {
        "mean": float(mean(values)),
        "population_std": float(pstdev(values)) if len(values) > 1 else 0.0,
        "min": float(min(values)),
        "max": float(max(values)),
    }


def _arm_record(payload: dict[str, Any], arm: str) -> dict[str, float]:
    result = payload["arms"][arm]
    metrics = result["conditional_closure"]
    peak = result.get("peak_gpu_memory_bytes")
    return {
        "log_ratio_rmse": float(metrics["log_ratio_residual"]["rmse"]),
        "log_ratio_bias": float(metrics["log_ratio_residual"]["bias"]),
        "max_projection_relative_l1": float(
            max(
                value["relative_l1"]
                for value in metrics["projection_residuals"].values()
            )
        ),
        "global_ess": float(metrics["ess"]["global_predicted"]),
        "tail_ess": float(metrics["ess"]["declared_tail_predicted"]),
        "predicted_ratio_q99": float(
            metrics["predicted_ratio"]["quantiles"]["q99"]
        ),
        "predicted_ratio_max": float(
            metrics["predicted_ratio"]["quantiles"]["q100"]
        ),
        "predicted_truth_weight_q99": float(
            metrics["predicted_truth_weight"]["quantiles"]["q99"]
        ),
        "predicted_truth_weight_max": float(
            metrics["predicted_truth_weight"]["quantiles"]["q100"]
        ),
        "direction_gate_pass": float(bool(metrics["direction_gate"]["pass"])),
        "runtime_seconds": float(result["runtime_seconds"]),
        "peak_gpu_memory_bytes": float(peak) if peak is not None else 0.0,
        "signal_rows_per_wall_second": float(
            result["signal_rows_per_wall_second"]
        ),
    }


def aggregate(
    paths: list[Path],
    *,
    expected_seeds: tuple[int, ...] = (101, 202, 303),
) -> dict[str, Any]:
    runs = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("status") != "complete_experimental_tf_current_engine_ab":
            raise ValueError(f"incomplete TensorFlow A/B pilot: {path}")
        recipe = payload["recipe"]
        if not recipe.get("tf_a_vs_b_comparison_claim_permitted"):
            raise ValueError(f"non-matched TensorFlow A/B recipe: {path}")
        source = payload["source_receipt"]
        if source["git"]["dirty"]:
            raise ValueError(f"dirty TensorFlow A/B source: {path}")
        seed = int(recipe["estimator_seed"])
        runs.append(
            {
                "seed": seed,
                "path": str(path.resolve()),
                "sha256": file_sha256(path),
                "source_commit": source["git"]["commit"],
                "source_files": source["files"],
                "dataset_fingerprint": payload["dataset_manifest"]["fingerprint"],
                "A": _arm_record(payload, "A"),
                "B": _arm_record(payload, "B"),
            }
        )
    keyed = {run["seed"]: run for run in runs}
    if len(keyed) != len(runs) or set(keyed) != set(expected_seeds):
        raise ValueError(
            "TensorFlow A/B seed inventory mismatch: "
            f"found={sorted(keyed)}, expected={list(expected_seeds)}"
        )
    commits = {run["source_commit"] for run in runs}
    files = {fingerprint(run["source_files"]) for run in runs}
    datasets = {run["dataset_fingerprint"] for run in runs}
    if len(commits) != 1 or len(files) != 1 or len(datasets) != 1:
        raise ValueError(
            "TensorFlow A/B source or dataset footing differs: "
            f"commits={commits}, file_sets={files}, datasets={datasets}"
        )
    arms = {
        arm: {
            "seeds": list(expected_seeds),
            "metrics": {
                metric: _summary([keyed[seed][arm][metric] for seed in expected_seeds])
                for metric in METRICS
            },
        }
        for arm in ("A", "B")
    }
    a_rmse = arms["A"]["metrics"]["log_ratio_rmse"]["mean"]
    b_rmse = arms["B"]["metrics"]["log_ratio_rmse"]["mean"]
    closure_improvement = 100.0 * (a_rmse - b_rmse) / a_rmse
    global_ess_degradation = 100.0 * (
        arms["A"]["metrics"]["global_ess"]["mean"]
        - arms["B"]["metrics"]["global_ess"]["mean"]
    ) / arms["A"]["metrics"]["global_ess"]["mean"]
    tail_ess_degradation = 100.0 * (
        arms["A"]["metrics"]["tail_ess"]["mean"]
        - arms["B"]["metrics"]["tail_ess"]["mean"]
    ) / arms["A"]["metrics"]["tail_ess"]["mean"]
    per_seed = [
        keyed[seed]["A"]["log_ratio_rmse"]
        - keyed[seed]["B"]["log_ratio_rmse"]
        for seed in expected_seeds
    ]
    direction_all = all(value > 0 for value in per_seed)
    absolute_gate = all(
        bool(keyed[seed]["B"]["direction_gate_pass"]) for seed in expected_seeds
    )
    tail_not_worse = (
        arms["B"]["metrics"]["predicted_ratio_q99"]["mean"]
        <= 1.10 * arms["A"]["metrics"]["predicted_ratio_q99"]["mean"]
        and arms["B"]["metrics"]["predicted_ratio_max"]["mean"]
        <= 1.10 * arms["A"]["metrics"]["predicted_ratio_max"]["mean"]
    )
    if (
        closure_improvement < -5.0
        or global_ess_degradation > 10.0
        or tail_ess_degradation > 10.0
        or not tail_not_worse
    ):
        decision = "harmful-or-unstable-on-synthetic-pilot"
    elif not absolute_gate:
        decision = "insufficiently-validated-absolute-closure-gate-failed"
    elif abs(closure_improvement) <= 5.0:
        decision = "neutral-at-preregistered-pilot-threshold"
    elif closure_improvement > 5.0 and direction_all:
        decision = "insufficiently-validated-cap-scan-unavailable"
    else:
        decision = "insufficiently-validated"
    result = {
        "status": "complete_matched_tf_ab_synthetic_aggregate",
        "evidence_class": "synthetic-fixture",
        "source_commit": next(iter(commits)),
        "dataset_fingerprint": next(iter(datasets)),
        "expected_seeds": list(expected_seeds),
        "runs": sorted(runs, key=lambda run: run["seed"]),
        "arms": arms,
        "comparison": {
            "B_vs_A": {
                "closure_rmse_improvement_percent": closure_improvement,
                "global_ess_degradation_percent": global_ess_degradation,
                "tail_ess_degradation_percent": tail_ess_degradation,
                "per_seed_closure_rmse_improvement": per_seed,
                "direction_reproduced_all_seeds": direction_all,
                "absolute_direction_gate_pass_all_seeds": absolute_gate,
                "extreme_ratio_tail_within_10_percent": tail_not_worse,
                "cap_sensitivity_available": False,
                "decision": decision,
            }
        },
        "framework_caveats": {
            "single_mc_weight": "w_truth is used for both TensorFlow steps",
            "split_matching_to_pytorch": False,
            "cap_sensitivity_telemetry": False,
            "b_to_c_architecture_claim_permitted": False,
        },
        "g2_validation_claim": False,
        "publication_promotion_permitted": False,
    }
    result["fingerprint"] = fingerprint(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--seeds", nargs="+", type=int, default=[101, 202, 303])
    args = parser.parse_args()
    base = Path(args.base).expanduser().resolve()
    paths = sorted(base.glob("tf_ab_matched_seed*_job*.json"))
    if not paths:
        raise FileNotFoundError(f"no matched TensorFlow A/B pilots under {base}")
    result = aggregate(paths, expected_seeds=tuple(args.seeds))
    write_json(args.out, result)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
