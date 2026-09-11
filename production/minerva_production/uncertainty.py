"""Declared statistical and training perturbations with matched-family assembly."""

from __future__ import annotations

from typing import Any

import numpy as np


def statistical_inputs(
    inputs: dict[str, Any], *, seed: int, mode: str
) -> dict[str, Any]:
    """Resample data and, explicitly when requested, paired reco/truth MC weights.

    Parameters
    ----------
    inputs : dict
        Validated nominal arrays. Fixed normalization inputs are retained.
    seed : int
        Bootstrap seed. MC uses the established offset of 10,000,000.
    mode : str
        Either data-only or data-plus-mc; there is no implicit statistical mode.

    Returns
    -------
    dict
        Shallow copy with new weights; nominal arrays are never mutated.
    """
    if seed < 0 or mode not in {"data-only", "data-plus-mc"}:
        raise ValueError(
            "statistical members require a nonnegative seed and explicit data-only or data-plus-mc mode"
        )
    varied = {**inputs}
    varied["measured_weights"] = inputs["measured_weights"] * np.random.default_rng(
        seed
    ).poisson(1.0, len(inputs["measured"]))
    if mode == "data-plus-mc":
        factors = np.random.default_rng(seed + 10_000_000).poisson(
            1.0, len(inputs["w_truth"])
        )
        varied["w_truth"] = inputs["w_truth"] * factors
        varied["w_reco"] = inputs["w_reco"] * factors
    return varied


def training_config(cfg: dict[str, Any], seed: int) -> dict[str, Any]:
    """Vary only the declared training split using the existing split engine."""
    if cfg["train_fraction"] == 1:
        raise ValueError(
            "ML split members require the nominal train_fraction < 1; do not change the estimator only for replicas"
        )
    if seed < 0:
        raise ValueError("split seed must be nonnegative")
    return {**cfg, "split_seed": seed}


def require_systematic_path() -> None:
    """Refuse a cached adapter that cannot represent selection-complete systematics."""
    raise ValueError(
        "systematic members require selection-complete lateral inputs, per-universe background and flux contracts, and a governing construction; use the retained scalar-5D route. Cached weight-only substitution is unsupported"
    )


def assemble(nominal: dict[str, Any], members: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute the retained sample convention, with mean shift reported separately.

    Parameters
    ----------
    nominal : dict
        Matched nominal result arrays.
    members : list of dict
        At least two verified compatible result arrays, in declared seed order.

    Returns
    -------
    dict
        Mean-centered 1/(N-1) covariance and mean shift; no sum or adoption.
    """
    if len(members) < 2:
        raise ValueError("covariance requires at least two complete members")
    spectra = np.stack([member["xsec"] for member in members])
    if spectra.shape[1:] != nominal["xsec"].shape or not np.all(np.isfinite(spectra)):
        raise ValueError("member spectra must be finite and match nominal support")
    mean = spectra.mean(axis=0)
    centered = spectra - mean
    return {
        "xsec": nominal["xsec"],
        "covariance": centered.T @ centered / (len(members) - 1),
        "mean": mean,
        "mean_shift": mean - nominal["xsec"],
    }
