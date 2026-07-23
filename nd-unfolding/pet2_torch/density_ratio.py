"""Calibrated weighted binary density-ratio training."""

from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from .contracts import TokenBatch, concatenate_batches
from .utils import effective_sample_size, fingerprint, weight_summary

try:
    import torch
    import torch.nn.functional as F

    HAS_TORCH = True
    TORCH_IMPORT_ERROR = None
except ImportError as exc:
    torch = None
    F = None
    HAS_TORCH = False
    TORCH_IMPORT_ERROR = exc


@dataclass(frozen=True)
class RatioTrainingConfig:
    epochs: int = 8
    batch_size: int = 512
    learning_rate: float = 1e-4
    weight_decay: float = 1e-2
    log_ratio_cap: float = 30.0
    seed: int = 101
    device: str = "cpu"
    inference_batch_size: int = 4096

    def validated(self) -> "RatioTrainingConfig":
        if min(self.epochs, self.batch_size, self.inference_batch_size) < 1:
            raise ValueError("epochs and batch sizes must be positive")
        if self.learning_rate <= 0 or self.weight_decay < 0:
            raise ValueError("invalid optimizer parameters")
        if self.log_ratio_cap <= 0:
            raise ValueError("log_ratio_cap must be positive")
        return self

    def payload(self) -> dict[str, Any]:
        payload = asdict(self.validated())
        payload["fingerprint"] = fingerprint(payload)
        return payload


def calibrated_ratio(
    logits: np.ndarray,
    class0_mass: float,
    class1_mass: float,
    log_ratio_cap: float,
    reference_weights: np.ndarray | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Convert balanced class-conditional logits to a physical measure ratio."""
    logits = np.asarray(logits, dtype=np.float64)
    if not np.all(np.isfinite(logits)):
        raise ValueError("nonfinite classifier logits")
    if class0_mass <= 0 or class1_mass <= 0:
        raise ValueError("class masses must be positive")
    offset = math.log(class1_mass / class0_mass)
    raw_log_ratio = logits + offset
    clipped = np.clip(raw_log_ratio, -log_ratio_cap, log_ratio_cap)
    ratio = np.exp(clipped)
    saturated = np.abs(raw_log_ratio) >= log_ratio_cap
    checked_reference = None
    saturated_weight_mass = None
    saturated_weight_fraction = None
    if reference_weights is not None:
        checked_reference = np.asarray(reference_weights, dtype=np.float64)
        if checked_reference.shape != logits.shape:
            raise ValueError("reference_weights and logits shapes differ")
        if (
            not np.all(np.isfinite(checked_reference))
            or np.any(checked_reference < 0)
            or checked_reference.sum() <= 0
        ):
            raise ValueError("reference_weights must be finite, nonnegative, and positive-mass")
        saturated_weight_mass = float(checked_reference[saturated].sum())
        saturated_weight_fraction = saturated_weight_mass / float(
            checked_reference.sum()
        )
    sensitivity = {}
    for cap in sorted({10.0, 20.0, float(log_ratio_cap)}):
        cap_saturated = np.abs(raw_log_ratio) >= cap
        cap_ratio = np.exp(np.clip(raw_log_ratio, -cap, cap))
        item = {
            "log_ratio_cap": cap,
            "saturated_count": int(cap_saturated.sum()),
            "saturated_fraction": (
                float(cap_saturated.mean()) if cap_saturated.size else 0.0
            ),
            "ratio_quantiles": np.quantile(
                cap_ratio, [0, 0.01, 0.5, 0.99, 1]
            ).tolist(),
        }
        if checked_reference is not None:
            reweighted = checked_reference * cap_ratio
            cap_mass = float(checked_reference[cap_saturated].sum())
            item.update(
                {
                    "saturated_reference_weight_mass": cap_mass,
                    "saturated_reference_weight_fraction": cap_mass
                    / float(checked_reference.sum()),
                    "reweighted_mass": float(reweighted.sum()),
                    "reweighted_ess": effective_sample_size(reweighted),
                }
            )
        sensitivity[f"cap_{cap:g}"] = item
    telemetry = {
        "class0_mass": float(class0_mass),
        "class1_mass": float(class1_mass),
        "log_class_mass_offset": float(offset),
        "log_ratio_cap": float(log_ratio_cap),
        "saturated_count": int(saturated.sum()),
        "saturated_fraction": float(saturated.mean()) if saturated.size else 0.0,
        "saturated_weight_mass": saturated_weight_mass,
        "saturated_weight_fraction": saturated_weight_fraction,
        "logit_quantiles": np.quantile(logits, [0, 0.01, 0.5, 0.99, 1]).tolist(),
        "ratio_quantiles": np.quantile(ratio, [0, 0.01, 0.5, 0.99, 1]).tolist(),
        "cap_sensitivity": sensitivity,
    }
    return ratio, telemetry


def balanced_weighted_bce_numpy(
    logits0: np.ndarray,
    logits1: np.ndarray,
    weights0: np.ndarray,
    weights1: np.ndarray,
) -> float:
    """Reference loss used by login-safe analytic tests."""
    logits0 = np.asarray(logits0, dtype=np.float64)
    logits1 = np.asarray(logits1, dtype=np.float64)
    weights0 = np.asarray(weights0, dtype=np.float64)
    weights1 = np.asarray(weights1, dtype=np.float64)
    if logits0.shape != weights0.shape or logits1.shape != weights1.shape:
        raise ValueError("logits and weights must have matching one-dimensional shapes")
    for name, value in (("weights0", weights0), ("weights1", weights1)):
        if np.any(value < 0) or not np.all(np.isfinite(value)) or value.sum() <= 0:
            raise ValueError(f"{name} must be finite, nonnegative, and have positive mass")
    loss0 = np.logaddexp(0.0, logits0)
    loss1 = np.logaddexp(0.0, -logits1)
    return 0.5 * (
        float(np.dot(weights0, loss0) / weights0.sum())
        + float(np.dot(weights1, loss1) / weights1.sum())
    )


def evaluate_density_ratio(
    model,
    class0: TokenBatch,
    class1: TokenBatch,
    weights0: np.ndarray,
    weights1: np.ndarray,
    config: RatioTrainingConfig,
) -> dict[str, Any]:
    """Evaluate a fitted classifier without changing model or optimizer state."""
    class0 = class0.validated()
    class1 = class1.validated()
    weights0 = np.asarray(weights0, dtype=np.float64)
    weights1 = np.asarray(weights1, dtype=np.float64)
    if weights0.shape != (class0.n_rows,) or weights1.shape != (class1.n_rows,):
        raise ValueError("evaluation weights do not align with class inventories")
    logits0 = predict_logits(model, class0, config)
    logits1 = predict_logits(model, class1, config)
    return {
        "balanced_weighted_bce": balanced_weighted_bce_numpy(
            logits0, logits1, weights0, weights1
        ),
        "class0": weight_summary(weights0),
        "class1": weight_summary(weights1),
        "logit_class0_quantiles": np.quantile(
            logits0, [0, 0.01, 0.5, 0.99, 1]
        ).tolist(),
        "logit_class1_quantiles": np.quantile(
            logits1, [0, 0.01, 0.5, 0.99, 1]
        ).tolist(),
    }


def _torch_batch(batch: TokenBatch, indices: np.ndarray, device: str) -> dict[str, Any]:
    return {
        "continuous": torch.as_tensor(batch.continuous[indices], device=device),
        "coords": torch.as_tensor(batch.coords[indices], device=device),
        "token_mask": torch.as_tensor(batch.token_mask[indices], device=device),
        "type_id": torch.as_tensor(batch.type_id[indices], device=device),
        "view_id": torch.as_tensor(batch.view_id[indices], device=device),
        "globals_": torch.as_tensor(batch.globals[indices], device=device),
    }


def fit_density_ratio(
    model,
    class0: TokenBatch,
    class1: TokenBatch,
    weights0: np.ndarray,
    weights1: np.ndarray,
    config: RatioTrainingConfig,
) -> dict[str, Any]:
    """Train the balanced weighted classifier.

    Coefficients are normalized independently by the complete supplied class
    masses.  Calibration later restores their physical mass ratio explicitly.
    """
    if not HAS_TORCH:
        raise RuntimeError(f"PyTorch is unavailable: {TORCH_IMPORT_ERROR}")
    config = config.validated()
    class0 = class0.validated()
    class1 = class1.validated()
    combined = concatenate_batches((class0, class1), "ratio_class0_then_class1")
    weights0 = np.asarray(weights0, dtype=np.float64)
    weights1 = np.asarray(weights1, dtype=np.float64)
    if weights0.shape != (class0.n_rows,) or weights1.shape != (class1.n_rows,):
        raise ValueError("ratio weights do not align with class inventories")
    for name, values in (("weights0", weights0), ("weights1", weights1)):
        if not np.all(np.isfinite(values)) or np.any(values < 0) or values.sum() <= 0:
            raise ValueError(f"{name} must be finite, nonnegative, and have positive mass")
    mass0 = float(weights0.sum())
    mass1 = float(weights1.sum())
    labels = np.concatenate(
        (np.zeros(class0.n_rows, dtype=np.float32), np.ones(class1.n_rows, dtype=np.float32))
    )
    coefficients = np.concatenate((0.5 * weights0 / mass0, 0.5 * weights1 / mass1))
    n = combined.n_rows
    model.to(config.device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )
    generator = torch.Generator(device="cpu")
    generator.manual_seed(config.seed)
    history: list[float] = []
    started = time.perf_counter()
    model.train()
    for _epoch in range(config.epochs):
        permutation = torch.randperm(n, generator=generator).numpy()
        total = 0.0
        for start in range(0, n, config.batch_size):
            indices = permutation[start : start + config.batch_size]
            tensor = _torch_batch(combined, indices, config.device)
            logits = model(**tensor)
            y = torch.as_tensor(labels[indices], device=config.device)
            coeff = torch.as_tensor(
                coefficients[indices], device=config.device, dtype=logits.dtype
            )
            per_event = F.binary_cross_entropy_with_logits(logits, y, reduction="none")
            # N/batch makes the shuffled minibatch gradient an unbiased
            # estimate of the complete normalized objective.
            loss = (per_event * coeff).sum() * (n / len(indices))
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            total += float((per_event * coeff).sum().detach().cpu())
        history.append(float(total))
    elapsed = time.perf_counter() - started
    return {
        "history": history,
        "class0": weight_summary(weights0),
        "class1": weight_summary(weights1),
        "class0_mass": mass0,
        "class1_mass": mass1,
        "log_class_mass_offset": math.log(mass1 / mass0),
        "runtime_seconds": elapsed,
        "throughput_rows_per_second": (n * config.epochs / elapsed) if elapsed else None,
        "peak_gpu_memory_bytes": (
            int(torch.cuda.max_memory_allocated(config.device))
            if str(config.device).startswith("cuda") and torch.cuda.is_available()
            else 0
        ),
    }


def predict_logits(model, batch: TokenBatch, config: RatioTrainingConfig) -> np.ndarray:
    if not HAS_TORCH:
        raise RuntimeError(f"PyTorch is unavailable: {TORCH_IMPORT_ERROR}")
    batch = batch.validated()
    model.eval()
    output = np.empty(batch.n_rows, dtype=np.float64)
    with torch.no_grad():
        for start in range(0, batch.n_rows, config.inference_batch_size):
            stop = min(start + config.inference_batch_size, batch.n_rows)
            indices = np.arange(start, stop)
            tensor = _torch_batch(batch, indices, config.device)
            output[start:stop] = model(**tensor).detach().cpu().numpy()
    if not np.all(np.isfinite(output)):
        raise ValueError("model inference produced nonfinite logits")
    return output


def infer_ratio(
    model,
    batch: TokenBatch,
    fit_receipt: dict[str, Any],
    config: RatioTrainingConfig,
    reference_weights: np.ndarray | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    logits = predict_logits(model, batch, config)
    return calibrated_ratio(
        logits,
        fit_receipt["class0_mass"],
        fit_receipt["class1_mass"],
        config.log_ratio_cap,
        reference_weights,
    )
