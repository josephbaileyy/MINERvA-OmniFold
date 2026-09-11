"""One cached-input GBDT calculation for nominal, replicas, and closure."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .storage import legacy_module

MODEL = {"n_estimators": 100, "num_leaves": 8, "learning_rate": 0.1, "verbose": -1}
DEFAULTS: dict[str, Any] = {
    "backend": "cached-lgbm-v1",
    "iterations": 5,
    "iteration_policy": "fixed-final",
    "estimator_seed": 42,
    "seed_policy": "same-seed-for-both-classifiers-and-regressor",
    "train_fraction": 1.0,
    "split_seed": 0,
    "model": MODEL,
    "normalization": "fixed-denominator-recomputed-completeness",
}


def resolve_config(raw: dict[str, Any]) -> dict[str, Any]:
    """Resolve and validate the supported cached estimator, without loading events.

    Parameters
    ----------
    raw : dict
        Explicit features, selection, background treatment and optional defaults.

    Returns
    -------
    dict
        Fully resolved scientific configuration. Unsupported policies raise ValueError.
    """
    allowed = set(DEFAULTS) | {"features", "selection", "background"}
    if set(raw) - allowed:
        raise ValueError(f"unknown scalar settings: {sorted(set(raw) - allowed)}")
    cfg = {**copy.deepcopy(DEFAULTS), **raw}
    for key in ("features", "selection", "background"):
        if not cfg.get(key):
            raise ValueError(f"scalar config requires {key}")
    for key in ("backend", "iteration_policy", "seed_policy", "model", "normalization"):
        if cfg[key] != DEFAULTS[key]:
            raise ValueError(f"{key}: only {DEFAULTS[key]!r} is supported")
    if cfg["background"] not in {"signal-only", "preweighted-purity"}:
        raise ValueError(
            "background requires signal-only or preweighted-purity; signed/refined targets need their original driver"
        )
    if (
        not isinstance(cfg["features"], list)
        or not all(isinstance(name, str) and name for name in cfg["features"])
        or len(set(cfg["features"])) != len(cfg["features"])
    ):
        raise ValueError("features must be distinct names in training order")
    for key in ("iterations", "estimator_seed", "split_seed"):
        if type(cfg[key]) is not int or cfg[key] < (1 if key == "iterations" else 0):
            raise ValueError(
                f"{key} must be a valid nonnegative integer (iterations >= 1)"
            )
    if not 0 < cfg["train_fraction"] <= 1:
        raise ValueError("train_fraction must be in (0, 1]")
    return cfg


def validate_contract(
    contract: dict[str, Any],
) -> tuple[list[NDArray[np.float64]], tuple[int, ...]]:
    """Validate bin geometry, units, ordering, and explicit flattened support."""
    if contract.get("ordering") != "C" or contract.get("meaning") not in {
        "density",
        "yield",
    }:
        raise ValueError(
            "contract requires C ordering and density or yield meaning; normalized shapes are unsupported"
        )
    axes = contract.get("axes", [])
    if not axes or len({axis["name"] for axis in axes}) != len(axes):
        raise ValueError("contract requires distinct ordered axes")
    edges = []
    for axis in axes:
        edge = np.asarray(axis["edges"], float)
        if (
            not axis.get("unit")
            or edge.ndim != 1
            or len(edge) < 2
            or not np.all(np.isfinite(edge))
            or not np.all(np.diff(edge) > 0)
        ):
            raise ValueError("axes require units and finite, strictly increasing edges")
        edges.append(edge)
    shape = tuple(len(edge) - 1 for edge in edges)
    support = np.asarray(contract.get("support"))
    if (
        support.dtype != bool
        or support.shape != (int(np.prod(shape)),)
        or not support.any()
    ):
        raise ValueError(
            "support must be an explicit, nonempty full-grid boolean vector"
        )
    if not contract.get("value_unit"):
        raise ValueError("contract requires value_unit")
    return edges, shape


def load_inputs(
    path: Path, cfg: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load aligned arrays once and check all training/extraction prerequisites."""
    with np.load(path, allow_pickle=False) as archive:
        arrays = {key: archive[key] for key in archive.files}
    required = {
        "MCgen",
        "MCreco",
        "measured",
        "pass_truth",
        "pass_reco",
        "meas_pass_reco",
        "w_truth",
        "w_reco",
        "measured_weights",
        "truth_id",
        "reco_id",
        "data_id",
        "denom_nd",
        "flux",
        "data_pot",
        "n_nucleons",
        "metadata",
    }
    if required - arrays.keys():
        raise ValueError(
            f"input missing required arrays: {sorted(required - arrays.keys())}"
        )
    meta = json.loads(str(arrays.pop("metadata")))
    for key in ("selection", "background"):
        if meta.get(key) != cfg[key]:
            raise ValueError(f"input {key} does not match resolved configuration")
    if meta.get("normalization_units") != {
        "flux": "m^-2/POT",
        "data_pot": "POT",
        "n_nucleons": "nucleons",
    }:
        raise ValueError("explicit flux/POT/nucleon normalization units are required")
    if meta.get("denominator_policy") != "fixed-under-bootstrap":
        raise ValueError(
            "cached path requires fixed-under-bootstrap denominator policy"
        )
    if not meta.get("normalization_source"):
        raise ValueError("normalization_source is required")
    features = meta.get("feature_names", [])
    units = meta.get("feature_units", {})
    if set(units) != set(features) or not all(
        isinstance(unit, str) and unit for unit in units.values()
    ):
        raise ValueError("feature_units must declare a unit for every input feature")
    if len(set(features)) != len(features) or not set(cfg["features"]) <= set(features):
        raise ValueError(
            "input feature names must be unique and contain configured features"
        )
    nmc, ndata = len(arrays["MCgen"]), len(arrays["measured"])
    for key, length in (("MCgen", nmc), ("MCreco", nmc), ("measured", ndata)):
        if arrays[key].shape != (length, len(features)) or not np.all(
            np.isfinite(arrays[key])
        ):
            raise ValueError(f"{key}: expected finite aligned feature matrix")
    for key, length in (("truth_id", nmc), ("reco_id", nmc), ("data_id", ndata)):
        ids = arrays[key]
        if (
            ids.shape != (length,)
            or ids.dtype.kind not in "iuUS"
            or len(np.unique(ids)) != length
        ):
            raise ValueError(f"{key}: stable unique event identity required")
    if not np.array_equal(arrays["truth_id"], arrays["reco_id"]):
        raise ValueError("reco/truth event identity or row order differs")
    for key, length in (
        ("pass_truth", nmc),
        ("pass_reco", nmc),
        ("meas_pass_reco", ndata),
    ):
        if arrays[key].dtype != bool or arrays[key].shape != (length,):
            raise ValueError(f"{key}: expected aligned boolean mask")
    for key, length in (("w_truth", nmc), ("w_reco", nmc), ("measured_weights", ndata)):
        weights = arrays[key]
        if (
            weights.shape != (length,)
            or not np.all(np.isfinite(weights))
            or np.any(weights < 0)
        ):
            raise ValueError(f"{key}: expected finite nonnegative aligned weights")
    if not np.any(
        arrays["pass_truth"] & arrays["pass_reco"] & (arrays["w_reco"] > 0)
    ) or not np.any(arrays["meas_pass_reco"] & (arrays["measured_weights"] > 0)):
        raise ValueError("training requires positive signal and measured class totals")
    contract = meta["output_contract"]
    edges, shape = validate_contract(contract)
    if contract["meaning"] != "density" or contract["value_unit"] != "cm^2/nucleon":
        raise ValueError(
            "scalar extraction requires density with base unit cm^2/nucleon"
        )
    if not {axis["name"] for axis in contract["axes"]} <= set(features):
        raise ValueError("extraction axes are missing from the input features")
    if any(axis["unit"] != units[axis["name"]] for axis in contract["axes"]):
        raise ValueError("extraction axis units differ from input feature units")
    flux_axis = meta.get("flux_axis")
    if type(flux_axis) is not int or not 0 <= flux_axis < len(edges):
        raise ValueError("flux_axis must identify an extraction axis")
    if (
        arrays["denom_nd"].shape != shape
        or not np.all(np.isfinite(arrays["denom_nd"]))
        or np.any(arrays["denom_nd"] < 0)
    ):
        raise ValueError(
            "denom_nd: expected finite nonnegative counts on the declared grid"
        )
    if (
        arrays["flux"].shape != (shape[flux_axis],)
        or not np.all(np.isfinite(arrays["flux"]))
        or np.any(arrays["flux"] <= 0)
    ):
        raise ValueError("flux must be positive and finite on the declared flux axis")
    for key in ("data_pot", "n_nucleons"):
        if arrays[key].shape != () or not np.isfinite(arrays[key]) or arrays[key] <= 0:
            raise ValueError(f"{key} must be a positive finite scalar")
    return arrays, meta


def extract(
    inputs: dict[str, Any], meta: dict[str, Any], push: NDArray[np.float64]
) -> dict[str, Any]:
    """Apply the existing cached-replica histogram/completeness normalization."""
    contract = meta["output_contract"]
    edges, _ = validate_contract(contract)
    mask = inputs["pass_truth"]
    columns = [meta["feature_names"].index(axis["name"]) for axis in contract["axes"]]
    truth = inputs["MCgen"][mask][:, columns]
    weights = inputs["w_truth"][mask]
    prior = np.histogramdd(truth, bins=edges, weights=weights)[0]
    unfolded = np.histogramdd(truth, bins=edges, weights=push * weights)[0]
    completeness = np.zeros_like(prior)
    np.divide(prior, inputs["denom_nd"], out=completeness, where=inputs["denom_nd"] > 0)
    xsec, good = legacy_module("xsec_nd").extract_cross_section_nd(
        unfolded,
        completeness,
        inputs["flux"],
        float(inputs["data_pot"]),
        float(inputs["n_nucleons"]),
        edges,
        flux_axis=meta["flux_axis"],
    )
    support = np.asarray(contract["support"])
    if np.any(support & ~good.ravel()):
        raise ValueError(
            "reported support contains undefined completeness; no bin may silently become zero"
        )
    return {
        "xsec": xsec.ravel()[support],
        "unfolded": unfolded,
        "prior": prior,
        "completeness": completeness,
        "normalization_valid": good,
    }


def calculate(
    inputs: dict[str, Any], meta: dict[str, Any], cfg: dict[str, Any]
) -> dict[str, Any]:
    """Run the same existing two-step loop and extraction for every perturbation.

    Parameters
    ----------
    inputs, meta : dict
        Validated arrays and their row/normalization contract.
    cfg : dict
        Resolved estimator settings. Event perturbations belong in inputs.

    Returns
    -------
    dict
        Pull/push factors, aligned identities, intermediate spectra, and density.
    """
    columns = [meta["feature_names"].index(name) for name in cfg["features"]]
    pull, push = legacy_module("omnifold_nn_core").omnifold_loop(
        inputs["MCgen"][:, columns],
        inputs["MCreco"][:, columns],
        inputs["measured"][:, columns],
        inputs["pass_reco"],
        inputs["pass_truth"],
        inputs["meas_pass_reco"],
        cfg["iterations"],
        kind="lgbm",
        MCgen_weights=inputs["w_truth"],
        MCreco_weights=inputs["w_reco"],
        measured_weights=inputs["measured_weights"],
        seed=cfg["estimator_seed"],
        verbose=False,
        train_frac=cfg["train_fraction"],
        split_seed=cfg["split_seed"],
    )
    if not np.all(np.isfinite(pull)) or not np.all(np.isfinite(push)):
        raise ValueError("nonfinite unfolding factors")
    return {
        **extract(inputs, meta, push),
        "pull": pull,
        "push": push,
        "truth_id": inputs["truth_id"][inputs["pass_truth"]],
    }


def closure_inputs(
    inputs: dict[str, Any], meta: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Construct the existing strict signal-MC closure, without bootstrap draws."""
    if meta["background"] != "signal-only":
        raise ValueError(
            "closure requires signal-only input; purity/refined background closure needs its original driver"
        )
    mask = inputs["pass_truth"] & inputs["pass_reco"]
    pseudo = {
        **inputs,
        "measured": inputs["MCreco"][mask].copy(),
        "measured_weights": inputs["w_reco"][mask].copy(),
        "meas_pass_reco": np.ones(int(mask.sum()), bool),
        "data_id": inputs["reco_id"][mask].copy(),
    }
    reference = extract(inputs, meta, np.ones(int(inputs["pass_truth"].sum())))
    return pseudo, reference
