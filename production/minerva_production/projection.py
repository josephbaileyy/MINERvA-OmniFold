"""Linear projections that preserve declared support, axis order, and correlations."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from .scalar import validate_contract
from .storage import legacy_module


def projection_map(
    contract: dict[str, Any], keep: list[str]
) -> tuple[NDArray[np.float64], dict[str, Any]]:
    """Build a linear map onto complete fibers of the declared source support.

    Parameters
    ----------
    contract : dict
        Ordered axes, edges, units, C ordering and full-grid support mask.
    keep : list of str
        Destination axes in requested order, which may differ from source order.

    Returns
    -------
    ndarray, dict
        Map from supported source cells to supported destination cells and its
        contract. Partial fibers fail rather than implying missing cells are zero.
    """
    edges, shape = validate_contract(contract)
    names = [axis["name"] for axis in contract["axes"]]
    if not keep or len(set(keep)) != len(keep) or not set(keep) <= set(names):
        raise ValueError("keep must list distinct source axes in destination order")
    retained = [names.index(name) for name in keep]
    dropped = [axis for axis in range(len(shape)) if axis not in retained]
    dest_shape = tuple(shape[axis] for axis in retained)
    support = np.asarray(contract["support"], bool)
    indices = np.array(list(np.ndindex(shape)))
    dest_flat = np.ravel_multi_index(
        tuple(indices[:, axis] for axis in retained), dest_shape
    )
    full_counts = np.bincount(dest_flat, minlength=int(np.prod(dest_shape)))
    present_counts = np.bincount(dest_flat[support], minlength=len(full_counts))
    partial = (present_counts > 0) & (present_counts != full_counts)
    if np.any(partial):
        raise ValueError(
            f"incomplete source support in destination cells {np.flatnonzero(partial).tolist()}; a partial marginal needs an explicit scientific contract"
        )
    dest_support = present_counts > 0
    dest_rows = np.cumsum(dest_support) - 1
    weights = np.ones(int(support.sum()))
    if contract["meaning"] == "density":
        for axis in dropped:
            weights *= np.diff(edges[axis])[indices[support, axis]]
    projection = np.zeros((int(dest_support.sum()), int(support.sum())))
    projection[dest_rows[dest_flat[support]], np.arange(int(support.sum()))] = weights
    output = {
        **contract,
        "axes": [contract["axes"][axis] for axis in retained],
        "support": dest_support.tolist(),
    }
    return projection, output


def project(
    arrays: dict[str, Any], contract: dict[str, Any], keep: list[str]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Project a central vector and its compatible covariance without retraining."""
    projection, output = projection_map(contract, keep)
    central = arrays["xsec"]
    if central.shape != (projection.shape[1],) or not np.all(np.isfinite(central)):
        raise ValueError("central vector does not match declared supported cells")
    projected = {"xsec": projection @ central, "projection": projection}
    if "covariance" in arrays:
        covariance = arrays["covariance"]
        if covariance.shape != (len(central), len(central)) or not np.all(
            np.isfinite(covariance)
        ):
            raise ValueError("covariance does not match central support")
        scale = np.max(np.abs(covariance))
        if np.max(np.abs(covariance - covariance.T)) > 1e-12 * scale:
            raise ValueError("covariance is not symmetric at relative tolerance 1e-12")
        projected["covariance"] = legacy_module("uq_math").project_covariance(
            covariance, projection
        )
    for key in ("mean", "mean_shift"):
        if key in arrays:
            projected[key] = projection @ arrays[key]
    return projected, output
