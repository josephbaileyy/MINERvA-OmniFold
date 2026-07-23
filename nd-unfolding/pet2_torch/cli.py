#!/usr/bin/env python3
"""Preregistered synthetic PET2 ablations and contract-only preflight."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .artifacts import atomic_run_directory, save_iteration_result, write_json
from .checkpoints import current_arm_f_outcome
from .density_ratio import HAS_TORCH, RatioTrainingConfig, TORCH_IMPORT_ERROR
from .engine import OneIterationConfig, run_iterations
from .evaluation import conditional_closure_metrics
from .features import (
    build_arm_manifest,
    exact_arm_diff,
    frozen_truth_arm_manifest,
)
from .fixtures import (
    make_known_ratio_closure_dataset,
    make_synthetic_dataset,
)
from .ratio_conventions import fixed_ratio_convention_fixture
from .utils import environment_receipt, fingerprint, seed_everything

PREREGISTERED_ESTIMATOR_SEEDS = (101, 202, 303)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--recipe", choices=("matched-pilot", "smoke"), default="matched-pilot"
    )
    parser.add_argument(
        "--fixture",
        choices=("known-ratio", "three-inventory"),
        default="known-ratio",
    )
    parser.add_argument("--events", type=int, default=256)
    parser.add_argument("--data-events", type=int, default=128)
    parser.add_argument("--background-events", type=int, default=40)
    parser.add_argument("--max-tokens", type=int, default=7)
    parser.add_argument("--fixture-seed", type=int, default=424242)
    parser.add_argument("--estimator-seed", type=int, default=101)
    parser.add_argument("--split-seed", type=int, default=424242)
    parser.add_argument("--iterations", type=int, default=2)
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-2)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--arms", nargs="+", default=["C"])
    parser.add_argument("--contract-only", action="store_true")
    parser.add_argument("--use-overflow", action="store_true")
    parser.add_argument(
        "--muon-token",
        action="store_true",
        help="synthetic-only explicit muon-token seam; physical G2 coordinates are unaudited",
    )
    return parser.parse_args()


def _recipe_status(args) -> dict:
    frozen = {
        "fixture_seed": 424242,
        "split_seed": 424242,
        "estimator_seeds": list(PREREGISTERED_ESTIMATOR_SEEDS),
        "iterations": 2,
        "epochs_per_step": 8,
        "batch_size": 512,
        "optimizer": "AdamW",
        "learning_rate": 1e-4,
        "weight_decay": 1e-2,
    }
    matched = (
        args.recipe == "matched-pilot"
        and args.fixture == "known-ratio"
        and args.fixture_seed == 424242
        and args.split_seed == 424242
        and args.estimator_seed in PREREGISTERED_ESTIMATOR_SEEDS
        and args.iterations == 2
        and args.epochs == 8
        and args.batch_size == 512
        and args.learning_rate == 1e-4
        and args.weight_decay == 1e-2
    )
    if args.recipe == "matched-pilot" and not matched:
        raise ValueError(
            "matched-pilot parameters differ from the frozen preregistration; "
            "use --recipe smoke to record the downgrade explicitly"
        )
    return {
        "declared_mode": args.recipe,
        "classification": "matched_pilot" if matched else "smoke_or_custom_downgrade",
        "frozen_preregistration": frozen,
        "comparison_claim_permitted": matched,
    }


def _execute(args, output: Path) -> int:
    recipe = _recipe_status(args)
    closure = None
    if args.fixture == "known-ratio":
        closure = make_known_ratio_closure_dataset(
            n_signal=args.events,
            n_background=args.background_events,
            max_tokens=args.max_tokens,
            seed=args.fixture_seed,
        )
        dataset = closure.dataset
        capabilities = closure.capabilities
    else:
        dataset, capabilities = make_synthetic_dataset(
            n_signal=args.events,
            n_data=args.data_events,
            n_background=args.background_events,
            max_tokens=args.max_tokens,
            seed=args.fixture_seed,
        )
    muon_override = "token" if args.muon_token else None
    arms = [
        build_arm_manifest(
            arm,
            capabilities,
            muon_representation=muon_override,
            use_overflow_aggregate=args.use_overflow,
        )
        for arm in args.arms
    ]
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
    parameter_footing = {
        "model_capacity": {
            "hidden_dim": iteration.model_hidden_dim,
            "heads": iteration.model_heads,
            "transformer_layers": iteration.model_transformer_layers,
            "edge_layers": iteration.model_edge_layers,
            "k_neighbors": iteration.model_k_neighbors,
        },
        "input_tensor_shape": {
            "continuous_dim": dataset.signal.reco.continuous.shape[2],
            "global_superset_dim": dataset.signal.reco.globals.shape[1],
            "category_vocabularies_fixed": True,
        },
        "identical_across_arms": True,
    }
    parameter_footing["fingerprint"] = fingerprint(parameter_footing)
    summary = {
        "status": "contract_only" if args.contract_only else "running",
        "evidence_class": (
            "portable_synthetic_known_ratio"
            if closure is not None
            else "portable_synthetic_three_inventory"
        ),
        "g2_validation_claim": False,
        "recipe": recipe,
        "dataset_manifest": dataset.manifest(),
        "closure_fixture": None if closure is None else closure.specification,
        "arms": {arm.arm: arm.payload() for arm in arms},
        "truth_arm": frozen_truth_arm_manifest().payload(),
        "arm_f": current_arm_f_outcome(),
        "ratio_convention_fixture": {
            key: value
            for key, value in fixed_ratio_convention_fixture().items()
            if key not in {
                "balanced_logits",
                "physical_logits",
                "tf_balanced_posterior",
                "tf_normalized_odds",
                "tf_odds_ratio",
                "torch_balanced_plus_mass_offset_ratio",
            }
        },
        "environment": environment_receipt(),
        "parameter_footing": parameter_footing,
        "matched_controls": {
            "fixture_seed": args.fixture_seed,
            "estimator_seed": args.estimator_seed,
            "split_seed": args.split_seed,
            "iterations": args.iterations,
            "same_rows": True,
            "same_target": True,
            "same_training_budget": True,
        },
    }
    if len(arms) > 1:
        by_name = {arm.arm: arm for arm in arms}
        summary["declared_arm_diffs"] = {}
        for child in arms:
            parent = by_name.get(child.comparison_parent)
            if parent is not None:
                summary["declared_arm_diffs"][
                    f"{parent.arm}_to_{child.arm}"
                ] = exact_arm_diff(parent, child)
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
    summary["results"] = {}
    for arm in arms:
        seeds = seed_everything(args.estimator_seed, deterministic=True)
        result, iteration_receipts = run_iterations(
            dataset, arm, iteration, iterations=args.iterations
        )
        result.receipt["seeds"] = seeds
        result.receipt["recipe_classification"] = recipe
        metrics = None
        if closure is not None:
            metrics = conditional_closure_metrics(
                dataset,
                result.push,
                closure.expected_truth_ratio,
                closure.declared_tail_mask,
                iteration_receipts=iteration_receipts,
            )
            result.receipt["conditional_closure"] = metrics
        arm_path = output / f"arm_{arm.arm}_seed_{args.estimator_seed}"
        save_iteration_result(
            arm_path,
            result,
            config={
                **iteration.payload(),
                "iterations": args.iterations,
                "recipe": recipe,
            },
            arm_manifest=arm.payload(),
        )
        summary["results"][arm.arm] = {
            "status": "complete_experimental_fixture",
            "estimator_seed": args.estimator_seed,
            "relative_path": arm_path.name,
            "recipe_fingerprint": result.receipt["recipe_fingerprint"],
            "push": result.receipt["push"],
            "runtime_seconds": float(
                sum(item["runtime_seconds"] for item in iteration_receipts)
            ),
            "conditional_closure": metrics,
        }
    summary["status"] = "complete_experimental_fixture"
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
