"""NumPy-only conditional-closure and pilot telemetry."""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np

from .contracts import CanonicalDataset
from .utils import effective_sample_size, weight_summary


def _quantile_edges(values: np.ndarray, bins: int) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    edges = np.unique(np.quantile(values, np.linspace(0.0, 1.0, bins + 1)))
    if edges.size < 2:
        center = float(values[0])
        edges = np.asarray([center - 0.5, center + 0.5])
    edges[0] = np.nextafter(edges[0], -np.inf)
    edges[-1] = np.nextafter(edges[-1], np.inf)
    return edges


def _projection_residual(
    coordinates: np.ndarray,
    expected_weights: np.ndarray,
    predicted_weights: np.ndarray,
    bins_per_axis: int,
) -> dict[str, Any]:
    coordinates = np.asarray(coordinates, dtype=np.float64)
    edges = [
        _quantile_edges(coordinates[:, column], bins_per_axis)
        for column in range(coordinates.shape[1])
    ]
    expected = np.histogramdd(coordinates, bins=edges, weights=expected_weights)[0]
    predicted = np.histogramdd(coordinates, bins=edges, weights=predicted_weights)[0]
    residual = predicted - expected
    expected_mass = float(expected.sum())
    denom = np.maximum(expected, 1e-12)
    occupied = (expected > 0) | (predicted > 0)
    return {
        "dimensions": int(coordinates.shape[1]),
        "shape": list(expected.shape),
        "expected_mass": expected_mass,
        "predicted_mass": float(predicted.sum()),
        "relative_l1": float(np.abs(residual).sum() / max(expected_mass, 1e-12)),
        "occupied_bin_rms_fractional": float(
            np.sqrt(np.mean(np.square(residual[occupied] / denom[occupied])))
        ),
        "max_abs_fractional": float(
            np.max(np.abs(residual[occupied]) / denom[occupied])
        ),
    }


def _cap_summary(iteration_receipts: Iterable[dict[str, Any]]) -> dict[str, Any]:
    records = []
    for receipt in iteration_receipts:
        for step in ("step1_inference", "step2_inference"):
            item = receipt.get(step, {})
            records.append(
                {
                    "iteration": int(receipt.get("config", {}).get("iteration_index", 0)),
                    "step": step,
                    "saturated_count": int(item.get("saturated_count", 0)),
                    "saturated_fraction": float(item.get("saturated_fraction", 0.0)),
                    "saturated_weight_mass": item.get("saturated_weight_mass"),
                    "saturated_weight_fraction": item.get("saturated_weight_fraction"),
                }
            )
    return {
        "records": records,
        "total_saturated_count": int(
            sum(record["saturated_count"] for record in records)
        ),
        "total_saturated_weight_mass": float(
            sum(
                record["saturated_weight_mass"] or 0.0
                for record in records
            )
        ),
    }


def conditional_closure_metrics(
    dataset: CanonicalDataset,
    predicted_truth_ratio: np.ndarray,
    expected_truth_ratio: np.ndarray,
    declared_tail_mask: np.ndarray,
    *,
    iteration_receipts: Iterable[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Evaluate a full-iteration result against aligned analytic truth weights."""
    dataset = dataset.validated()
    signal = dataset.signal
    predicted = np.asarray(predicted_truth_ratio, dtype=np.float64)
    expected = np.asarray(expected_truth_ratio, dtype=np.float64)
    tail = np.asarray(declared_tail_mask, dtype=bool)
    n = signal.truth.n_rows
    if predicted.shape != (n,) or expected.shape != (n,) or tail.shape != (n,):
        raise ValueError("closure ratio/tail arrays must have full signal-row shape")
    if (
        not np.all(np.isfinite(predicted))
        or not np.all(np.isfinite(expected))
        or np.any(predicted <= 0)
        or np.any(expected <= 0)
    ):
        raise ValueError("closure ratios must be finite and strictly positive")
    valid = signal.pass_truth
    if not np.any(valid) or not np.any(tail & valid):
        raise ValueError("closure evaluation requires truth rows and a declared tail")
    base = dataset.pot_scale * signal.w_truth
    expected_weights = base[valid] * expected[valid]
    predicted_weights = base[valid] * predicted[valid]
    log_residual = np.log(predicted[valid]) - np.log(expected[valid])
    globals_ = signal.truth.globals[valid]
    names = signal.truth.global_names
    column = {name: names.index(name) for name in names}
    projections = {
        "mu_pt_x_mu_pparallel": _projection_residual(
            globals_[:, [column["mu_pt"], column["mu_pparallel"]]],
            expected_weights,
            predicted_weights,
            6,
        ),
        "eavail_x_q3": _projection_residual(
            globals_[:, [column["eavail"], column["q3"]]],
            expected_weights,
            predicted_weights,
            6,
        ),
        "mu_pt_x_eavail_x_q3": _projection_residual(
            globals_[:, [column["mu_pt"], column["eavail"], column["q3"]]],
            expected_weights,
            predicted_weights,
            4,
        ),
    }
    tail_valid = tail[valid]
    log_rmse = float(np.sqrt(np.mean(np.square(log_residual))))
    max_projection_l1 = max(
        record["relative_l1"] for record in projections.values()
    )
    return {
        "status": "evaluated_against_analytic_aligned_fixture",
        "truth_row_count": int(valid.sum()),
        "native_miss_count": int(np.sum(valid & ~signal.pass_reco)),
        "log_ratio_residual": {
            "bias": float(log_residual.mean()),
            "rmse": log_rmse,
            "mae": float(np.abs(log_residual).mean()),
            "quantiles": np.quantile(
                log_residual, [0, 0.01, 0.5, 0.99, 1]
            ).tolist(),
        },
        "expected_ratio": weight_summary(expected[valid]),
        "predicted_ratio": weight_summary(predicted[valid]),
        "expected_truth_weight": weight_summary(expected_weights),
        "predicted_truth_weight": weight_summary(predicted_weights),
        "ess": {
            "global_expected": effective_sample_size(expected_weights),
            "global_predicted": effective_sample_size(predicted_weights),
            "declared_tail_expected": effective_sample_size(
                expected_weights[tail_valid]
            ),
            "declared_tail_predicted": effective_sample_size(
                predicted_weights[tail_valid]
            ),
            "declared_tail_count": int(tail_valid.sum()),
        },
        "cap_saturation": _cap_summary(iteration_receipts),
        "projection_residuals": projections,
        "direction_gate": {
            "log_ratio_rmse_max": 0.25,
            "max_projection_relative_l1": 0.25,
            "pass": bool(log_rmse <= 0.25 and max_projection_l1 <= 0.25),
        },
        "g2_validation_claim": False,
    }
