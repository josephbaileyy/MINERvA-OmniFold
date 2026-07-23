#!/usr/bin/env python3
"""Aggregate bounded, downgraded xps2 recoil-input retraining pilots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from .artifacts import write_json
from .utils import file_sha256, fingerprint

METRICS = (
    "push_ess",
    "push_ess_fraction",
    "push_q01",
    "push_q50",
    "push_q99",
    "push_max",
    "pull_ess",
    "pull_ess_fraction",
    "pull_q01",
    "pull_q50",
    "pull_q99",
    "pull_max",
    "cap_saturated_count",
    "cap10_vs_cap30_max_relative_ess_shift",
    "runtime_seconds",
    "peak_gpu_memory_bytes",
    "mean_step_throughput_rows_per_second",
)


def _summary(values: list[float]) -> dict[str, float]:
    return {
        "mean": float(mean(values)),
        "population_std": float(pstdev(values)) if len(values) > 1 else 0.0,
        "min": float(min(values)),
        "max": float(max(values)),
    }


def _load_run(path: Path) -> dict[str, Any]:
    summary = json.loads(path.read_text(encoding="utf-8"))
    if summary.get("status") != "complete_bounded_xps2_recoil_pilot":
        raise ValueError(f"incomplete xps2 pilot: {path}")
    if (
        summary.get("full_event_evidence")
        or summary.get("typed_object_evidence")
        or summary.get("g2_validation_claim")
        or summary.get("publication_promotion_permitted")
    ):
        raise ValueError(f"xps2 downgrade flags are inconsistent: {path}")
    receipt_path = path.parent / summary["result_relative_path"] / "receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt["git"]["dirty"]:
        raise ValueError(f"dirty xps2 pilot source: {path}")
    iterations = receipt["omnifold_iterations"]["complete_iteration_receipts"]
    if not iterations:
        raise ValueError(f"xps2 pilot has no iteration receipts: {path}")
    fits = [
        step
        for iteration in iterations
        for step in (iteration["step1_fit"], iteration["step2_fit"])
    ]
    cap_ess_shifts = []
    saturated = 0
    for iteration in iterations:
        for step_name in ("step1_inference", "step2_inference"):
            inference = iteration[step_name]
            saturated += int(inference["saturated_count"])
            sensitivity = inference["cap_sensitivity"]
            ess10 = float(sensitivity["cap_10"]["reweighted_ess"])
            ess30 = float(sensitivity["cap_30"]["reweighted_ess"])
            cap_ess_shifts.append(abs(ess10 - ess30) / max(abs(ess30), 1e-12))
    push = summary["push"]
    pull = summary["pull"]
    return {
        "seed": int(summary["estimator_seed"]),
        "selection_seed": int(summary["selection_seed"]),
        "split_seed": int(summary["split_seed"]),
        "path": str(path.resolve()),
        "sha256": file_sha256(path),
        "receipt_path": str(receipt_path.resolve()),
        "receipt_sha256": file_sha256(receipt_path),
        "source_commit": receipt["git"]["commit"],
        "dataset_fingerprint": summary["dataset_manifest"]["fingerprint"],
        "selection_hash": summary["contract_downgrades"]["source_inventory"][
            "selection_hash"
        ],
        "push_ess": float(push["ess"]),
        "push_ess_fraction": float(push["ess"]) / float(push["count"]),
        "push_q01": float(push["quantiles"]["q01"]),
        "push_q50": float(push["quantiles"]["q50"]),
        "push_q99": float(push["quantiles"]["q99"]),
        "push_max": float(push["quantiles"]["q100"]),
        "pull_ess": float(pull["ess"]),
        "pull_ess_fraction": float(pull["ess"]) / float(pull["count"]),
        "pull_q01": float(pull["quantiles"]["q01"]),
        "pull_q50": float(pull["quantiles"]["q50"]),
        "pull_q99": float(pull["quantiles"]["q99"]),
        "pull_max": float(pull["quantiles"]["q100"]),
        "cap_saturated_count": float(saturated),
        "cap10_vs_cap30_max_relative_ess_shift": float(max(cap_ess_shifts)),
        "runtime_seconds": float(summary["runtime_seconds"]),
        "peak_gpu_memory_bytes": float(
            max(int(fit["peak_gpu_memory_bytes"]) for fit in fits)
        ),
        "mean_step_throughput_rows_per_second": float(
            mean(float(fit["throughput_rows_per_second"]) for fit in fits)
        ),
    }


def aggregate(
    paths: list[Path],
    *,
    expected_seeds: tuple[int, ...] = (101, 202, 303),
) -> dict[str, Any]:
    runs = [_load_run(path.resolve()) for path in paths]
    keyed = {run["seed"]: run for run in runs}
    if len(keyed) != len(runs) or set(keyed) != set(expected_seeds):
        raise ValueError(
            f"xps2 seed inventory mismatch: found={sorted(keyed)}, "
            f"expected={list(expected_seeds)}"
        )
    commits = {run["source_commit"] for run in runs}
    datasets = {run["dataset_fingerprint"] for run in runs}
    selections = {run["selection_hash"] for run in runs}
    selection_seeds = {run["selection_seed"] for run in runs}
    split_seeds = {run["split_seed"] for run in runs}
    if any(
        len(values) != 1
        for values in (commits, datasets, selections, selection_seeds, split_seeds)
    ):
        raise ValueError(
            "xps2 matched footing differs: "
            f"commits={commits}, datasets={datasets}, selections={selections}, "
            f"selection_seeds={selection_seeds}, split_seeds={split_seeds}"
        )
    result = {
        "status": "complete_bounded_xps2_retraining_aggregate",
        "evidence_class": "recoil-input-pilot",
        "source_commit": next(iter(commits)),
        "dataset_fingerprint": next(iter(datasets)),
        "selection_hash": next(iter(selections)),
        "selection_seed": next(iter(selection_seeds)),
        "split_seed": next(iter(split_seeds)),
        "expected_estimator_seeds": list(expected_seeds),
        "runs": sorted(runs, key=lambda run: run["seed"]),
        "metrics": {
            metric: _summary([keyed[seed][metric] for seed in expected_seeds])
            for metric in METRICS
        },
        "interpretation": {
            "closure_available": False,
            "architecture_comparison_permitted": False,
            "typed_object_evidence": False,
            "full_event_evidence": False,
            "g2_validation_claim": False,
            "weight_footing": "w_truth proxy for unavailable w_reco",
            "background_footing": "precomputed target; no literal background rows",
            "mask_footing": "historical zero-padding-derived mask",
        },
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
    paths = sorted(base.glob("xps2_practical_seed*_job*/summary.json"))
    if not paths:
        raise FileNotFoundError(f"no practical xps2 pilots under {base}")
    result = aggregate(paths, expected_seeds=tuple(args.seeds))
    write_json(args.out, result)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
