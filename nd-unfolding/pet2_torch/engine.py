"""One-iteration native PyTorch OmniFold engine."""

from __future__ import annotations

import time
import copy
from dataclasses import asdict, dataclass, replace
from typing import Any

import numpy as np

from .contracts import CanonicalDataset
from .density_ratio import (
    HAS_TORCH,
    RatioTrainingConfig,
    evaluate_density_ratio,
    fit_density_ratio,
    infer_ratio,
)
from .features import (
    ArmManifest,
    frozen_truth_arm_manifest,
    materialize_feature_view,
)
from .model import ModelConfig, build_model
from .preprocessing import fit_preprocessor
from .utils import (
    array_hash,
    fingerprint,
    seed_everything,
    stable_partition,
    weight_summary,
)


@dataclass(frozen=True)
class OneIterationConfig:
    ratio: RatioTrainingConfig
    model_hidden_dim: int = 128
    model_heads: int = 8
    model_transformer_layers: int = 8
    model_edge_layers: int = 2
    model_k_neighbors: int = 3
    train_fraction: float = 0.7
    validation_fraction: float = 0.15
    split_seed: int = 424242
    pot_scale: float | None = None
    iteration_index: int = 1

    def payload(self) -> dict[str, Any]:
        if (
            self.train_fraction <= 0
            or self.validation_fraction <= 0
            or self.train_fraction + self.validation_fraction >= 1
        ):
            raise ValueError("train/validation fractions must leave a positive test split")
        if self.pot_scale is not None and (
            not np.isfinite(self.pot_scale) or self.pot_scale <= 0
        ):
            raise ValueError("configured pot_scale must be finite and positive")
        if self.iteration_index < 1:
            raise ValueError("iteration_index must be positive")
        payload = asdict(self)
        payload["ratio"] = self.ratio.payload()
        payload["fingerprint"] = fingerprint(payload)
        return payload


@dataclass
class OneIterationResult:
    push: np.ndarray
    pull: np.ndarray
    row_index: np.ndarray
    step1_model: Any
    step2_model: Any
    reco_preprocessor: Any
    truth_preprocessor: Any
    receipt: dict[str, Any]


def resolve_pot_scale(dataset: CanonicalDataset, requested: float | None) -> float:
    """Bind engine normalization to the dataset/receipt scale.

    G2 is stricter than portable fixtures: the caller must repeat the
    receipt-bound value explicitly so an omitted CLI/config field cannot
    silently become unity.
    """
    dataset = dataset.validated()
    bound = float(dataset.pot_scale)
    source = str(dataset.schema.get("source", ""))
    if requested is None:
        if source == "publication_g2":
            raise ValueError(
                "G2 engine call must explicitly supply the receipt-bound pot_scale"
            )
        return bound
    requested = float(requested)
    if not np.isfinite(requested) or requested <= 0:
        raise ValueError("configured pot_scale must be finite and positive")
    if not np.isclose(requested, bound, rtol=0.0, atol=1e-14):
        raise ValueError(
            f"configured pot_scale {requested} differs from dataset-bound scale {bound}"
        )
    return bound


def _model_config(batch, config: OneIterationConfig) -> ModelConfig:
    return ModelConfig(
        continuous_dim=batch.continuous.shape[2],
        coord_dim=batch.coords.shape[2],
        global_dim=batch.globals.shape[1],
        hidden_dim=config.model_hidden_dim,
        num_heads=config.model_heads,
        transformer_layers=config.model_transformer_layers,
        edge_layers=config.model_edge_layers,
        k_neighbors=config.model_k_neighbors,
        max_type_id=15,
        max_view_id=7,
    ).validated()


def run_one_iteration(
    dataset: CanonicalDataset,
    arm: ArmManifest,
    config: OneIterationConfig,
    initial_push: np.ndarray | None = None,
) -> OneIterationResult:
    """Run one complete Step-1/Step-2 iteration and infer every signal row."""
    if not HAS_TORCH:
        raise RuntimeError("PyTorch is unavailable; the contract and fixture paths remain usable")
    started = time.perf_counter()
    dataset = dataset.validated()
    pot_scale = resolve_pot_scale(dataset, config.pot_scale)
    config.payload()
    signal = dataset.signal
    measured = dataset.measured
    reco = materialize_feature_view(signal.reco, arm)
    truth_arm = frozen_truth_arm_manifest()
    truth = materialize_feature_view(signal.truth, truth_arm)
    target = materialize_feature_view(measured.literal_target(), arm)
    test_fraction = 1.0 - config.train_fraction - config.validation_fraction
    fractions = (config.train_fraction, config.validation_fraction, test_fraction)
    signal_partition = stable_partition(
        reco.row_index,
        config.split_seed,
        fractions,
        identity=signal.event_key,
    )
    target_partition = stable_partition(
        target.row_index,
        config.split_seed + 1,
        fractions,
    )
    paired_target_count = 0
    if measured.aligned_signal_row is not None:
        alignment = measured.aligned_signal_row
        paired = alignment >= 0
        target_partition[paired] = signal_partition[alignment[paired]]
        paired_target_count = int(paired.sum())
    signal_split = signal_partition == 0
    target_split = target_partition == 0
    reco_fit = signal_split & signal.pass_reco
    truth_fit = signal_split & signal.pass_truth
    reco_pre = fit_preprocessor(reco, reco_fit)
    truth_pre = fit_preprocessor(truth, truth_fit)
    reco = reco_pre.transform(reco)
    truth = truth_pre.transform(truth)
    target = reco_pre.transform(target)
    n = reco.n_rows
    push0 = np.ones(n, dtype=np.float64) if initial_push is None else np.asarray(
        initial_push, dtype=np.float64
    )
    if push0.shape != (n,) or not np.all(np.isfinite(push0)) or np.any(push0 < 0):
        raise ValueError("initial_push must be finite, nonnegative, and full-order")
    step1_mc_rows = signal_split & signal.pass_reco
    step1_target_rows = target_split
    step1_w0 = (
        pot_scale * signal.w_reco[step1_mc_rows] * push0[step1_mc_rows]
    ) / config.train_fraction
    step1_w1 = measured.refined_weights[step1_target_rows] / config.train_fraction
    step1_config = _model_config(reco, config)
    step1_model_seed = config.ratio.seed + 10_000 * config.iteration_index + 1001
    step2_model_seed = config.ratio.seed + 10_000 * config.iteration_index + 1002
    step1_seed_settings = seed_everything(step1_model_seed, deterministic=True)
    model1 = build_model(step1_config)
    fit1 = fit_density_ratio(
        model1,
        reco.subset(step1_mc_rows),
        target.subset(step1_target_rows),
        step1_w0,
        step1_w1,
        config.ratio,
    )
    step1_evaluation = {}
    for partition_index, partition_name in enumerate(
        ("train", "validation", "test")
    ):
        mc_rows = (signal_partition == partition_index) & signal.pass_reco
        target_rows = target_partition == partition_index
        step1_evaluation[partition_name] = evaluate_density_ratio(
            model1,
            reco.subset(mc_rows),
            target.subset(target_rows),
            pot_scale * signal.w_reco[mc_rows] * push0[mc_rows],
            measured.refined_weights[target_rows],
            config.ratio,
        )
    pull = push0.copy()
    ratio1, infer1 = infer_ratio(
        model1,
        reco.subset(signal.pass_reco),
        fit1,
        config.ratio,
        pot_scale
        * signal.w_reco[signal.pass_reco]
        * push0[signal.pass_reco],
    )
    pull[signal.pass_reco] *= ratio1
    # Native truth-only misses retain the previous push through Step 1.
    if not np.array_equal(pull[~signal.pass_reco], push0[~signal.pass_reco]):
        raise AssertionError("native-miss pull weights changed during Step 1")
    step2_rows = signal_split & signal.pass_truth
    step2_w0 = (
        pot_scale * signal.w_truth[step2_rows] / config.train_fraction
    )
    step2_w1 = step2_w0 * pull[step2_rows]
    step2_config = _model_config(truth, config)
    step2_seed_settings = seed_everything(step2_model_seed, deterministic=True)
    model2 = build_model(step2_config)
    fit2 = fit_density_ratio(
        model2,
        truth.subset(step2_rows),
        truth.subset(step2_rows),
        step2_w0,
        step2_w1,
        config.ratio,
    )
    step2_evaluation = {}
    for partition_index, partition_name in enumerate(
        ("train", "validation", "test")
    ):
        rows = (signal_partition == partition_index) & signal.pass_truth
        base_weights = pot_scale * signal.w_truth[rows]
        step2_evaluation[partition_name] = evaluate_density_ratio(
            model2,
            truth.subset(rows),
            truth.subset(rows),
            base_weights,
            base_weights * pull[rows],
            config.ratio,
        )
    push = np.ones(n, dtype=np.float64)
    ratio2, infer2 = infer_ratio(
        model2,
        truth.subset(signal.pass_truth),
        fit2,
        config.ratio,
        pot_scale * signal.w_truth[signal.pass_truth],
    )
    push[signal.pass_truth] = ratio2
    if not np.all(np.isfinite(push)) or np.any(push < 0):
        raise ValueError("one-iteration extraction produced invalid push weights")
    # Complete ordering is a hard extraction contract, independent of training subset.
    if not np.array_equal(reco.row_index, np.arange(n, dtype=np.int64)):
        raise ValueError("full-order extraction requires row_index == arange(N)")
    receipt = {
        "status": "experimental_fixture_or_pilot_only",
        "dataset_manifest": dataset.manifest(),
        "arm_manifest": arm.payload(),
        "truth_arm_manifest": truth_arm.payload(),
        "config": config.payload(),
        "model_step1": step1_config.payload(),
        "model_step2": step2_config.payload(),
        "seed_policy": {
            "ratio_minibatch_seed": config.ratio.seed,
            "step1_model_seed": step1_model_seed,
            "step2_model_seed": step2_model_seed,
            "step1_determinism": step1_seed_settings,
            "step2_determinism": step2_seed_settings,
        },
        "preprocessing_step1": reco_pre.payload(),
        "preprocessing_step2": truth_pre.payload(),
        "split": {
            "seed": config.split_seed,
            "train_fraction": config.train_fraction,
            "validation_fraction": config.validation_fraction,
            "test_fraction": test_fraction,
            "signal_train_count": int(signal_split.sum()),
            "target_train_count": int(target_split.sum()),
            "signal_partition_counts": {
                name: int(np.sum(signal_partition == index))
                for index, name in enumerate(("train", "validation", "test"))
            },
            "target_partition_counts": {
                name: int(np.sum(target_partition == index))
                for index, name in enumerate(("train", "validation", "test"))
            },
            "signal_split_hash": array_hash(signal_partition),
            "target_split_hash": array_hash(target_partition),
            "identity_basis": (
                "physical_event_key" if signal.event_key is not None else "stable_row_index"
            ),
            "paired_target_rows_share_signal_partition": paired_target_count,
            "uniform_inclusion_probability": config.train_fraction,
            "inverse_inclusion_correction": 1.0 / config.train_fraction,
        },
        "pot_scale": {
            "resolved": pot_scale,
            "dataset_bound": dataset.pot_scale,
            "source": dataset.pot_scale_source,
            "caller_explicit": config.pot_scale is not None,
            "signal_reco_mass_full": float(pot_scale * signal.w_reco.sum()),
            "signal_truth_mass_full": float(pot_scale * signal.w_truth.sum()),
            "measured_target_mass_full": float(measured.refined_weights.sum()),
        },
        "step1_fit": fit1,
        "step1_evaluation": step1_evaluation,
        "step1_inference": infer1,
        "step2_fit": fit2,
        "step2_evaluation": step2_evaluation,
        "step2_inference": infer2,
        "native_misses": int(np.sum(signal.pass_truth & ~signal.pass_reco)),
        "push": weight_summary(push),
        "pull": weight_summary(pull),
        "full_order": {
            "count": n,
            "row_index_hash": array_hash(reco.row_index),
            "gap_count": 0,
            "duplicate_count": 0,
        },
        "runtime_seconds": time.perf_counter() - started,
    }
    receipt["recipe_fingerprint"] = fingerprint(
        {
            "dataset": receipt["dataset_manifest"]["fingerprint"],
            "reco_arm": receipt["arm_manifest"]["fingerprint"],
            "truth_arm": receipt["truth_arm_manifest"]["fingerprint"],
            "config": receipt["config"]["fingerprint"],
            "step1_model": receipt["model_step1"]["fingerprint"],
            "step2_model": receipt["model_step2"]["fingerprint"],
            "step1_preprocessing": receipt["preprocessing_step1"]["fingerprint"],
            "step2_preprocessing": receipt["preprocessing_step2"]["fingerprint"],
        }
    )
    return OneIterationResult(
        push=push,
        pull=pull,
        row_index=reco.row_index.copy(),
        step1_model=model1,
        step2_model=model2,
        reco_preprocessor=reco_pre,
        truth_preprocessor=truth_pre,
        receipt=receipt,
    )


def run_iterations(
    dataset: CanonicalDataset,
    arm: ArmManifest,
    config: OneIterationConfig,
    *,
    iterations: int = 2,
) -> tuple[OneIterationResult, list[dict[str, Any]]]:
    """Run the declared number of complete Step-1/Step-2 iterations."""
    if iterations < 1:
        raise ValueError("iterations must be positive")
    push = None
    receipts: list[dict[str, Any]] = []
    result = None
    for iteration_index in range(1, iterations + 1):
        iteration_config = replace(config, iteration_index=iteration_index)
        result = run_one_iteration(dataset, arm, iteration_config, initial_push=push)
        push = result.push
        receipts.append(result.receipt)
    assert result is not None
    history = [
        {
            "iteration_index": item["config"]["iteration_index"],
            "recipe_fingerprint": item["recipe_fingerprint"],
            "push": item["push"],
            "pull": item["pull"],
            "runtime_seconds": item["runtime_seconds"],
        }
        for item in receipts
    ]
    complete_iteration_receipts = [copy.deepcopy(item) for item in receipts]
    result.receipt["omnifold_iterations"] = {
        "count": iterations,
        "history": history,
        "complete_iteration_receipts": complete_iteration_receipts,
    }
    result.receipt["recipe_fingerprint"] = fingerprint(
        {
            "final_iteration_recipe": result.receipt["recipe_fingerprint"],
            "iteration_recipe_fingerprints": [
                item["recipe_fingerprint"] for item in receipts
            ],
            "iteration_count": iterations,
        }
    )
    return result, receipts
