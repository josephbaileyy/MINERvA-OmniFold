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

METRIC_NAMES = (
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
    manifest = summary.get("arms", {}).get(arm)
    if not isinstance(manifest, dict):
        raise ValueError(f"missing arm manifest in summary: {summary_path}")
    variant_flags = [
        label
        for label, enabled in (
            ("muon-token", manifest.get("muon_representation") == "token"),
            ("overflow", bool(manifest.get("use_overflow_aggregate"))),
        )
        if enabled
    ]
    if len(variant_flags) > 1:
        raise ValueError(f"confounded representation variant: {summary_path}")
    variant = variant_flags[0] if variant_flags else "base"
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
        "variant": variant,
        "seed": seed,
        "summary_path": str(summary_path),
        "summary_sha256": file_sha256(summary_path),
        "receipt_path": str(receipt_path),
        "receipt_sha256": file_sha256(receipt_path),
        "source_commit": receipt["git"]["commit"],
        "source_dirty": bool(receipt["git"]["dirty"]),
        "dataset_fingerprint": summary["dataset_manifest"]["fingerprint"],
        "parameter_footing_fingerprint": summary["parameter_footing"]["fingerprint"],
        "control_footing_fingerprint": fingerprint(
            {
                key: value
                for key, value in summary["matched_controls"].items()
                if key != "estimator_seed"
            }
        ),
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


def _validate_common_footing(runs: list[dict[str, Any]]) -> str:
    commits = {item["source_commit"] for item in runs}
    dirty = [item for item in runs if item["source_dirty"]]
    datasets = {item["dataset_fingerprint"] for item in runs}
    parameters = {item["parameter_footing_fingerprint"] for item in runs}
    controls = {item["control_footing_fingerprint"] for item in runs}
    if (
        len(commits) != 1
        or dirty
        or len(datasets) != 1
        or len(parameters) != 1
        or len(controls) != 1
    ):
        raise ValueError(
            "pilot footing differs or is dirty: "
            f"commits={commits}, datasets={datasets}, parameters={parameters}, "
            f"controls={controls}, "
            f"dirty={[(x['arm'], x['variant'], x['seed']) for x in dirty]}"
        )
    return next(iter(commits))


def _arm_metric_summary(
    keyed: dict[tuple[str, int], dict[str, Any]],
    labels: tuple[str, ...],
    seeds: tuple[int, ...],
) -> dict[str, Any]:
    output = {}
    for label in labels:
        selected = [keyed[(label, seed)] for seed in seeds]
        output[label] = {
            "seeds": list(seeds),
            "metrics": {
                name: _summary([float(item[name]) for item in selected])
                for name in METRIC_NAMES
            },
        }
    return output


def _comparison(
    keyed: dict[tuple[str, int], dict[str, Any]],
    summaries: dict[str, Any],
    child: str,
    parent: str,
    seeds: tuple[int, ...],
) -> dict[str, Any]:
    parent_rmse = summaries[parent]["metrics"]["log_ratio_rmse"]["mean"]
    child_rmse = summaries[child]["metrics"]["log_ratio_rmse"]["mean"]
    closure_improvement = 100.0 * (parent_rmse - child_rmse) / parent_rmse
    parent_ess = summaries[parent]["metrics"]["global_ess"]["mean"]
    child_ess = summaries[child]["metrics"]["global_ess"]["mean"]
    ess_degradation = 100.0 * (parent_ess - child_ess) / parent_ess
    parent_tail_ess = summaries[parent]["metrics"]["tail_ess"]["mean"]
    child_tail_ess = summaries[child]["metrics"]["tail_ess"]["mean"]
    tail_ess_degradation = (
        100.0 * (parent_tail_ess - child_tail_ess) / parent_tail_ess
    )
    per_seed_improvement = [
        keyed[(parent, seed)]["log_ratio_rmse"]
        - keyed[(child, seed)]["log_ratio_rmse"]
        for seed in seeds
    ]
    cap_not_worse = (
        summaries[child]["metrics"]["cap_saturated_count"]["mean"]
        <= summaries[parent]["metrics"]["cap_saturated_count"]["mean"]
    )
    beneficial = (
        closure_improvement > 5.0
        and ess_degradation <= 10.0
        and tail_ess_degradation <= 10.0
        and all(value > 0 for value in per_seed_improvement)
        and cap_not_worse
    )
    if beneficial:
        decision = "beneficial-on-synthetic-pilot"
    elif (
        closure_improvement < -5.0
        or ess_degradation > 10.0
        or tail_ess_degradation > 10.0
    ):
        decision = "harmful-or-unstable-on-synthetic-pilot"
    elif (
        abs(closure_improvement) <= 5.0
        and abs(ess_degradation) <= 10.0
        and abs(tail_ess_degradation) <= 10.0
    ):
        decision = "neutral-at-preregistered-pilot-threshold"
    else:
        decision = "insufficiently-validated"
    return {
        "closure_rmse_improvement_percent": closure_improvement,
        "global_ess_degradation_percent": ess_degradation,
        "tail_ess_degradation_percent": tail_ess_degradation,
        "per_seed_closure_rmse_improvement": per_seed_improvement,
        "direction_reproduced_all_seeds": all(
            value > 0 for value in per_seed_improvement
        ),
        "cap_saturation_not_worse": cap_not_worse,
        "decision": decision,
        "publication_promotion_permitted": False,
    }


def aggregate(
    summary_paths: list[Path],
    *,
    expected_arms: tuple[str, ...],
    expected_seeds: tuple[int, ...],
) -> dict[str, Any]:
    runs = [_extract_run(path.resolve()) for path in summary_paths]
    nonbase = [
        (item["arm"], item["seed"], item["variant"])
        for item in runs
        if item["variant"] != "base"
    ]
    if nonbase:
        raise ValueError(f"base-arm aggregate received representation variants: {nonbase}")
    keyed = {(item["arm"], item["seed"]): item for item in runs}
    if len(keyed) != len(runs):
        raise ValueError("duplicate arm/seed result")
    expected = {(arm, seed) for arm in expected_arms for seed in expected_seeds}
    missing = sorted(expected - set(keyed))
    extra = sorted(set(keyed) - expected)
    if missing or extra:
        raise ValueError(f"pilot inventory mismatch: missing={missing}, extra={extra}")
    source_commit = _validate_common_footing(runs)
    arms = _arm_metric_summary(keyed, expected_arms, expected_seeds)
    comparisons = {}
    for child, parent in DIRECT_PARENT.items():
        if child not in arms or parent not in arms:
            continue
        comparisons[f"{child}_vs_{parent}"] = _comparison(
            keyed, arms, child, parent, expected_seeds
        )
    payload = {
        "status": "complete_matched_synthetic_pilot_aggregate",
        "evidence_class": "synthetic-fixture",
        "source_commit": source_commit,
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


def aggregate_variants(
    summary_paths: list[Path],
    *,
    expected_variants: tuple[str, ...],
    expected_seeds: tuple[int, ...],
) -> dict[str, Any]:
    runs = [_extract_run(path.resolve()) for path in summary_paths]
    if any(item["arm"] != "C" for item in runs):
        raise ValueError("representation-variant aggregate accepts only C-arm parents")
    keyed = {(item["variant"], item["seed"]): item for item in runs}
    if len(keyed) != len(runs):
        raise ValueError("duplicate representation-variant/seed result")
    expected = {
        (variant, seed)
        for variant in expected_variants
        for seed in expected_seeds
    }
    missing = sorted(expected - set(keyed))
    extra = sorted(set(keyed) - expected)
    if missing or extra:
        raise ValueError(
            f"representation-variant inventory mismatch: missing={missing}, extra={extra}"
        )
    source_commit = _validate_common_footing(runs)
    summaries = _arm_metric_summary(keyed, expected_variants, expected_seeds)
    comparisons = {
        f"{variant}_vs_base": _comparison(
            keyed, summaries, variant, "base", expected_seeds
        )
        for variant in expected_variants
        if variant != "base"
    }
    payload = {
        "status": "complete_matched_synthetic_representation_aggregate",
        "evidence_class": "synthetic-fixture",
        "source_commit": source_commit,
        "parent_arm": "C",
        "expected_variants": list(expected_variants),
        "expected_seeds": list(expected_seeds),
        "runs": sorted(runs, key=lambda item: (item["variant"], item["seed"])),
        "variants": summaries,
        "comparisons": comparisons,
        "decision_thresholds": {
            "closure_improvement_percent_strictly_greater_than": 5.0,
            "global_and_tail_ess_degradation_percent_maximum": 10.0,
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
    parser.add_argument(
        "--variants",
        nargs="+",
        choices=("base", "muon-token", "overflow"),
        help="aggregate separately tagged C-arm representation ablations",
    )
    args = parser.parse_args()
    base = Path(args.base).expanduser().resolve()
    if args.variants:
        slugs = {
            "base": "C",
            "muon-token": "C_muon_token",
            "overflow": "C_overflow",
        }
        paths = [
            path
            for variant in args.variants
            for path in sorted(
                base.glob(
                    f"pet2x_matched-pilot_{slugs[variant]}_seed*_job*/summary.json"
                )
            )
        ]
    else:
        paths = [
            path
            for arm in args.arms
            for path in sorted(
                base.glob(
                    "pet2x_matched-pilot_"
                    f"{arm.replace('-', '_')}_seed*_job*/summary.json"
                )
            )
        ]
    if not paths:
        raise FileNotFoundError(f"no matched-pilot summaries under {base}")
    if args.variants:
        result = aggregate_variants(
            paths,
            expected_variants=tuple(args.variants),
            expected_seeds=tuple(args.seeds),
        )
    else:
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
