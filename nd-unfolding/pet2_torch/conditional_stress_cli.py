#!/usr/bin/env python3
"""Run one matched parent/enriched conditional-information stress job."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .artifacts import (
    atomic_run_directory,
    save_iteration_result,
    write_json,
    write_npz_atomic,
)
from .conditional_fixtures import (
    FAMILIES,
    MODES,
    make_feature_conditional_stress_dataset,
)
from .density_ratio import HAS_TORCH, RatioTrainingConfig, TORCH_IMPORT_ERROR
from .engine import OneIterationConfig, run_iterations
from .evaluation import conditional_closure_metrics
from .features import materialize_feature_view
from .model import ModelConfig
from .utils import (
    array_hash,
    effective_sample_size,
    environment_receipt,
    fingerprint,
    seed_everything,
    weight_summary,
)

ESTIMATOR_SEEDS = (101, 202, 303)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--family", required=True, choices=FAMILIES)
    parser.add_argument("--mode", required=True, choices=MODES)
    parser.add_argument(
        "--recipe",
        choices=("matched-conditional-v1", "smoke"),
        default="matched-conditional-v1",
    )
    parser.add_argument("--events", type=int, default=100_000)
    parser.add_argument("--background-events", type=int, default=10_000)
    parser.add_argument("--max-tokens", type=int, default=7)
    parser.add_argument("--fixture-seed", type=int, default=424242)
    parser.add_argument("--split-seed", type=int, default=424242)
    parser.add_argument("--estimator-seed", type=int, default=101)
    parser.add_argument("--iterations", type=int, default=2)
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-2)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--contract-only", action="store_true")
    return parser.parse_args()


def _recipe(args) -> dict:
    frozen = {
        "events": 100_000,
        "background_events": 10_000,
        "max_tokens": 7,
        "fixture_seed": 424242,
        "split_seed": 424242,
        "estimator_seeds": list(ESTIMATOR_SEEDS),
        "iterations": 2,
        "epochs_per_step": 8,
        "batch_size": 512,
        "optimizer": "AdamW",
        "learning_rate": 1e-4,
        "weight_decay": 1e-2,
    }
    matched = (
        args.recipe == "matched-conditional-v1"
        and args.events == frozen["events"]
        and args.background_events == frozen["background_events"]
        and args.max_tokens == frozen["max_tokens"]
        and args.fixture_seed == frozen["fixture_seed"]
        and args.split_seed == frozen["split_seed"]
        and args.estimator_seed in ESTIMATOR_SEEDS
        and args.iterations == frozen["iterations"]
        and args.epochs == frozen["epochs_per_step"]
        and args.batch_size == frozen["batch_size"]
        and args.learning_rate == frozen["learning_rate"]
        and args.weight_decay == frozen["weight_decay"]
    )
    if args.recipe == "matched-conditional-v1" and not matched:
        raise ValueError(
            "matched conditional parameters differ from the frozen continuation "
            "preregistration; use --recipe smoke for a labeled downgrade"
        )
    return {
        "declared_mode": args.recipe,
        "classification": (
            "matched_feature_conditional_stress_v1"
            if matched
            else "smoke_or_custom_downgrade"
        ),
        "comparison_claim_permitted": matched,
        "frozen_preregistration": frozen,
    }


def _ratio_metrics(
    fixture,
    predicted: np.ndarray,
    expected: np.ndarray,
    *,
    step: str,
) -> dict:
    signal = fixture.dataset.signal
    predicted = np.asarray(predicted, dtype=np.float64)
    expected = np.asarray(expected, dtype=np.float64)
    if predicted.shape != expected.shape or predicted.shape != (signal.reco.n_rows,):
        raise ValueError("conditional stress ratio arrays are not full-order")
    valid = signal.pass_reco if step == "pull" else signal.pass_truth
    base = (
        fixture.dataset.pot_scale
        * (signal.w_reco if step == "pull" else signal.w_truth)
    )
    residual = np.log(predicted[valid]) - np.log(expected[valid])
    expected_weight = base[valid] * expected[valid]
    predicted_weight = base[valid] * predicted[valid]
    paired = fixture.pair_rows.reshape(-1)
    paired = paired[valid[paired]]
    hidden = fixture.hidden_sign[paired]
    group = {}
    for sign in (-1, 1):
        rows = paired[hidden == sign]
        group[str(sign)] = {
            "count": int(len(rows)),
            "expected_ratio_mean": float(np.mean(expected[rows])),
            "predicted_ratio_mean": float(np.mean(predicted[rows])),
            "predicted_ratio_std": float(np.std(predicted[rows])),
        }
    tail = fixture.declared_tail_mask & valid
    return {
        "step": step,
        "row_count": int(valid.sum()),
        "log_ratio_residual": {
            "bias": float(np.mean(residual)),
            "mae": float(np.mean(np.abs(residual))),
            "rmse": float(np.sqrt(np.mean(np.square(residual)))),
            "quantiles": np.quantile(
                residual, [0.0, 0.01, 0.5, 0.99, 1.0]
            ).tolist(),
        },
        "expected_ratio": weight_summary(expected[valid]),
        "predicted_ratio": weight_summary(predicted[valid]),
        "expected_weight": weight_summary(expected_weight),
        "predicted_weight": weight_summary(predicted_weight),
        "ess": {
            "global_expected": effective_sample_size(expected_weight),
            "global_predicted": effective_sample_size(predicted_weight),
            "tail_expected": effective_sample_size(base[tail] * expected[tail]),
            "tail_predicted": effective_sample_size(base[tail] * predicted[tail]),
            "tail_count": int(tail.sum()),
        },
        "hidden_sign_groups": group,
        "full_order": bool(
            np.array_equal(signal.reco.row_index, np.arange(signal.reco.n_rows))
        ),
    }


def _execute(args, output: Path) -> int:
    recipe = _recipe(args)
    fixture = make_feature_conditional_stress_dataset(
        args.family,
        args.mode,
        n_signal=args.events,
        n_background=args.background_events,
        max_tokens=args.max_tokens,
        seed=args.fixture_seed,
        split_seed=args.split_seed,
    )
    pair = fixture.arm_pair
    materialized = {
        "parent": materialize_feature_view(
            fixture.dataset.signal.reco, pair.parent
        ),
        "enriched": materialize_feature_view(
            fixture.dataset.signal.reco, pair.child
        ),
    }
    model_configs = {
        role: ModelConfig(
            continuous_dim=batch.continuous.shape[2],
            coord_dim=batch.coords.shape[2],
            global_dim=batch.globals.shape[1],
            hidden_dim=128,
            num_heads=8,
            transformer_layers=8,
            edge_layers=2,
            k_neighbors=3,
        ).payload()
        for role, batch in materialized.items()
    }
    model_config_fingerprints = {
        payload["fingerprint"] for payload in model_configs.values()
    }
    if len(model_config_fingerprints) != 1:
        raise AssertionError(
            "parent/enriched arms do not have identical model parameter shapes"
        )
    parameter_footing = {
        "model_configs": model_configs,
        "common_model_config_fingerprint": next(
            iter(model_config_fingerprints)
        ),
        "category_vocabularies_fixed": True,
        "trainable_parameter_shape_identical": len(model_config_fingerprints) == 1,
    }
    parameter_footing["fingerprint"] = fingerprint(parameter_footing)
    control_footing = {
        "dataset_manifest_fingerprint": fixture.dataset.manifest()["fingerprint"],
        "fixture_certificate_fingerprint": fixture.exclusivity_certificate[
            "fingerprint"
        ],
        "truth_tensor_sha256": fixture.exclusivity_certificate[
            "truth_tensor_sha256"
        ],
        "expected_ratio_sha256": array_hash(fixture.expected_truth_ratio),
        "fixture_seed": args.fixture_seed,
        "split_seed": args.split_seed,
        "estimator_seed": args.estimator_seed,
        "iterations": args.iterations,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
    }
    control_footing["fingerprint"] = fingerprint(control_footing)
    summary = {
        "status": "contract_only" if args.contract_only else "running",
        "evidence_class": "synthetic-fixture",
        "fixture_kind": "feature_conditional_counterfactual_pairs_v1",
        "family": args.family,
        "mode": args.mode,
        "g2_validation_claim": False,
        "publication_promotion_permitted": False,
        "recipe": recipe,
        "fixture": fixture.specification,
        "exclusivity_certificate": fixture.exclusivity_certificate,
        "dataset_manifest": fixture.dataset.manifest(),
        "arm_pair": {
            "parent_label": pair.parent_label,
            "child_label": pair.child_label,
            "parent": pair.parent.payload(),
            "child": pair.child.payload(),
        },
        "parameter_footing": parameter_footing,
        "control_footing": control_footing,
        "environment": environment_receipt(),
        "results": {},
    }
    write_npz_atomic(
        output / "fixture_evidence.npz",
        pair_rows=fixture.pair_rows,
        hidden_sign=fixture.hidden_sign,
        carrier_sign=fixture.carrier_sign,
        expected_truth_ratio=fixture.expected_truth_ratio,
        declared_tail_mask=fixture.declared_tail_mask,
    )
    if args.contract_only:
        write_json(output / "summary.json", summary)
        print(json.dumps(summary, sort_keys=True))
        return 0
    if not HAS_TORCH:
        summary["status"] = "unavailable"
        summary["reason"] = f"PyTorch unavailable: {TORCH_IMPORT_ERROR}"
        write_json(output / "summary.json", summary)
        print(json.dumps(summary, sort_keys=True))
        return 3
    ratio = RatioTrainingConfig(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        seed=args.estimator_seed,
        device=args.device,
    )
    iteration = OneIterationConfig(
        ratio=ratio,
        split_seed=args.split_seed,
        pot_scale=None,
    )
    for label, arm in (
        (pair.parent_label, pair.parent),
        (pair.child_label, pair.child),
    ):
        seed_settings = seed_everything(args.estimator_seed, deterministic=True)
        result, receipts = run_iterations(
            fixture.dataset, arm, iteration, iterations=args.iterations
        )
        pull_metrics = _ratio_metrics(
            fixture,
            result.pull,
            fixture.expected_truth_ratio,
            step="pull",
        )
        push_metrics = _ratio_metrics(
            fixture,
            result.push,
            fixture.expected_truth_ratio,
            step="push",
        )
        closure = conditional_closure_metrics(
            fixture.dataset,
            result.push,
            fixture.expected_truth_ratio,
            fixture.declared_tail_mask,
            iteration_receipts=receipts,
        )
        result.receipt["seeds"] = seed_settings
        result.receipt["recipe_classification"] = recipe
        result.receipt["conditional_stress"] = {
            "family": args.family,
            "mode": args.mode,
            "role": "parent" if label == pair.parent_label else "enriched",
            "label": label,
            "exclusivity_certificate": fixture.exclusivity_certificate,
            "pull_metrics": pull_metrics,
            "push_metrics": push_metrics,
            "projection_metrics": closure["projection_residuals"],
            "g2_validation_claim": False,
            "publication_promotion_permitted": False,
        }
        safe_label = label.replace("+", "_plus_").replace("/", "_")
        arm_path = output / f"{safe_label}_seed_{args.estimator_seed}"
        save_iteration_result(
            arm_path,
            result,
            config={
                **iteration.payload(),
                "iterations": args.iterations,
                "recipe": recipe,
                "family": args.family,
                "mode": args.mode,
                "role_label": label,
            },
            arm_manifest=arm.payload(),
        )
        summary["results"][label] = {
            "status": "complete_feature_conditional_stress",
            "role": "parent" if label == pair.parent_label else "enriched",
            "relative_path": arm_path.name,
            "recipe_fingerprint": result.receipt["recipe_fingerprint"],
            "pull_metrics": pull_metrics,
            "push_metrics": push_metrics,
            "projection_metrics": closure["projection_residuals"],
            "cap_saturation": closure["cap_saturation"],
            "runtime_seconds": float(
                sum(receipt["runtime_seconds"] for receipt in receipts)
            ),
        }
    summary["status"] = "complete_feature_conditional_stress"
    write_json(output / "summary.json", summary)
    print(json.dumps(summary, sort_keys=True))
    return 0


def main() -> int:
    args = parse_args()
    destination = Path(args.out).expanduser().resolve()
    with atomic_run_directory(destination) as temporary:
        return _execute(args, temporary)


if __name__ == "__main__":
    raise SystemExit(main())
