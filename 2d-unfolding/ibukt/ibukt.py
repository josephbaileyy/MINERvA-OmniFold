"""Fixed truth deformations and per-cell recovery readings for IBUKT.

This module has no ROOT or scheduler dependency. The reporting grid is read from
its committed configuration, which is checked against the production driver.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypeAlias, cast

import numpy as np
from numpy.typing import NDArray

Array: TypeAlias = NDArray[np.float64]
CONFIG = Path(__file__).with_name("config.json")
RECOVERY_TOLERANCE = 0.02


def configuration() -> dict[str, Any]:
    """Return the committed experiment settings."""
    return cast(dict[str, Any], json.loads(CONFIG.read_text()))


def cells(pt: Array, pz: Array, cfg: dict[str, Any]) -> NDArray[np.int64]:
    """Map coordinates to pT-major ROOT bins, with -1 for under/overflow."""
    pe, ze = np.asarray(cfg["pt_edges"]), np.asarray(cfg["pz_edges"])
    ip = np.searchsorted(pe, pt, side="right") - 1
    iz = np.searchsorted(ze, pz, side="right") - 1
    valid = np.isfinite(pt) & np.isfinite(pz)
    valid &= (ip >= 0) & (ip < len(pe) - 1) & (iz >= 0) & (iz < len(ze) - 1)
    return np.where(valid, ip * (len(ze) - 1) + iz, -1)


def histogram(pt: Array, pz: Array, weights: Array, cfg: dict[str, Any]) -> Array:
    """Sum event weights on the complete rectangular reporting grid."""
    index = cells(pt, pz, cfg)
    valid = index >= 0
    return np.bincount(index[valid], weights=weights[valid], minlength=224)


def within_coordinate(pt: Array, pz: Array, cfg: dict[str, Any]) -> Array:
    """Return a bounded within-cell pT coordinate, zero outside the grid."""
    index = cells(pt, pz, cfg)
    pe = np.asarray(cfg["pt_edges"])
    ip = np.maximum(index, 0) // 16
    coord = (pt - pe[ip]) / (pe[ip + 1] - pe[ip])
    return np.where(index >= 0, coord, 0.0)


def moments(pt: Array, pz: Array, weights: Array, cfg: dict[str, Any]) -> Array:
    """Compute truth-weighted within-cell means for the frozen deformations."""
    mass = histogram(pt, pz, weights, cfg)
    first = histogram(pt, pz, weights * within_coordinate(pt, pz, cfg), cfg)
    return np.divide(first, mass, out=np.zeros(224), where=mass > 0)


def truth_factor(
    name: str,
    pt: Array,
    pz: Array,
    means: Array,
    cfg: dict[str, Any],
    ratios: dict[str, Array],
) -> Array:
    """Evaluate a declared event-level truth factor without modifying response weights.

    Within-cell tilts have exactly zero weighted mean on the full-truth bank
    used to define ``means``. Generator factors are fixed coarse shape stresses.
    """
    if name not in cfg["truths"]:
        raise ValueError(f"undeclared truth: {name}")
    index = cells(pt, pz, cfg)
    inside = index >= 0
    if name == "nominal":
        factor = np.ones(len(pt))
    elif name in ratios:
        factor = np.where(inside, ratios[name].reshape(-1)[np.maximum(index, 0)], 1.0)
    elif name == "bump":
        factor = 1 + 0.2 * np.exp(-(((pt - 0.4) / 0.1) ** 2))
    elif name == "tilt":
        factor = (np.maximum(pz, 1e-6) / 5.0) ** 0.1
    elif name in ("within_plus", "within_minus"):
        sign = 1 if name == "within_plus" else -1
        centered = within_coordinate(pt, pz, cfg) - means[np.maximum(index, 0)]
        factor = np.where(inside, 1 + sign * 0.5 * centered, 1.0)
    else:
        raise ValueError(f"missing generator ratio: {name}")
    if not np.all(np.isfinite(factor)) or np.any(factor <= 0):
        raise ValueError("truth factors must be finite and strictly positive")
    return factor


def poisson_target(features: Array, signed: Array, seed: int) -> tuple[Array, Array]:
    """Expand independent Poisson positive counts, retaining the fixed negative template.

    Positive signal and background entries are sampled in their input order.
    Both estimators subsequently use the very same refined target.
    """
    if len(features) != len(signed) or not np.all(np.isfinite(signed)):
        raise ValueError("invalid signed target")
    positive = signed > 0
    counts = np.random.default_rng([20261117, seed]).poisson(signed[positive])
    if counts.sum() > 20_000_000:
        raise ValueError("pseudo-data size exceeds the declared memory gate")
    expanded = np.repeat(features[positive], counts, axis=0)
    negative = signed < 0
    return (
        np.concatenate((expanded, features[negative])),
        np.concatenate((np.ones(len(expanded)), signed[negative])),
    )


def nominal_recovery(estimates: Array, truth: Array, label: str) -> float:
    """Require noise-free recovery within the engineering tolerance in every cell."""
    if estimates.shape != truth.shape or truth.size == 0 or np.any(truth <= 0):
        raise ValueError(f"{label}: invalid truth or cell alignment")
    if not all(np.all(np.isfinite(x)) for x in (estimates, truth)):
        raise ValueError(f"{label}: nonfinite nominal recovery operand")
    error = float(np.max(np.abs(estimates / truth - 1)))
    if error > RECOVERY_TOLERANCE:
        raise ValueError(f"{label}: {error} > {RECOVERY_TOLERANCE}")
    return error


def recoveries(estimates: Array, truth: Array, prior: Array) -> dict[str, Any]:
    """Classify each cell using a fixed 2% tolerance and a five-draw noise guard.

    The guard is a descriptive Student multiplier, not simultaneous coverage.
    All five paired trials are required; empty truth cells are refused.
    """
    if estimates.shape != (5, len(truth)) or prior.shape != truth.shape:
        raise ValueError("recovery requires exactly five trials and aligned cells")
    if (
        np.any(truth <= 0)
        or np.any(prior <= 0)
        or not all(np.all(np.isfinite(x)) for x in (estimates, truth, prior))
    ):
        raise ValueError("nonpositive truth or nonfinite recovery operand")
    residual = estimates / truth - 1
    mean = residual.mean(axis=0)
    noise = 2.7764451051977987 * residual.std(axis=0, ddof=1) / np.sqrt(5)
    low = np.maximum(np.abs(mean) - noise, 0)
    high = np.abs(mean) + noise
    reading = np.where(
        high <= RECOVERY_TOLERANCE,
        "within tolerance",
        np.where(low > RECOVERY_TOLERANCE, "outside tolerance", "unresolved"),
    )
    return {
        "residuals": residual.tolist(),
        "mean": mean.tolist(),
        "noise_guard": noise.tolist(),
        "reading": reading.tolist(),
        "departure": (truth / prior - 1).tolist(),
    }


def budget(
    rows: str, reservations: dict[str, float], requested_hours: float
) -> dict[str, float]:
    """Price all submitted attempts using sacct plus reservations for missing/active rows.

    Rows are JobIDRaw|JobName|State|ElapsedRaw|NNodes. Failed attempts count.
    Unknown jobs in this campaign and malformed records stop admission.
    """
    if requested_hours <= 0 or not np.isfinite(requested_hours):
        raise ValueError("invalid requested reservation")
    if any(not np.isfinite(x) or x <= 0 for x in reservations.values()):
        raise ValueError("invalid submitted reservation")
    charges = dict(reservations)
    seen: set[str] = set()
    for line in rows.splitlines():
        if not line.strip():
            continue
        job, name, state, elapsed, nodes = line.split("|")
        if "." in job or not name.startswith("ibukt-"):
            continue
        if job not in reservations or job in seen:
            raise ValueError("unknown or duplicate IBUKT allocation")
        seen.add(job)
        seconds, n_nodes = float(elapsed), int(nodes)
        if not np.isfinite(seconds) or seconds < 0 or n_nodes != 1:
            raise ValueError("invalid single-node charge")
        actual = seconds / 3600
        terminal = state.split()[0].rstrip("+") in {
            "COMPLETED",
            "FAILED",
            "CANCELLED",
            "TIMEOUT",
            "OUT_OF_MEMORY",
            "NODE_FAIL",
            "PREEMPTED",
            "BOOT_FAIL",
            "DEADLINE",
        }
        charges[job] = actual if terminal else max(actual, reservations[job])
    total = sum(charges.values()) + requested_hours
    if total > 5.90:
        raise ValueError(f"cap exceeded: {total:.6f} > 5.90 node-hours")
    return {
        "spent_or_reserved": sum(charges.values()),
        "requested": requested_hours,
        "total": total,
    }


def forecast(
    measured_seconds: float, elapsed_seconds: float, prior_hours: float
) -> dict[str, float]:
    """Refuse 34 more pairs unless 18 measured lane walls fit both time bounds.

    Scoring retains 0.10 node-hour. A further minute is reserved for launcher
    overhead. Allocation time is bounded independently of the campaign cap.
    """
    if not all(
        np.isfinite(x) for x in (measured_seconds, elapsed_seconds, prior_hours)
    ):
        raise ValueError("nonfinite preflight time")
    if measured_seconds <= 0 or elapsed_seconds < measured_seconds or prior_hours < 0:
        raise ValueError("invalid preflight time")
    remaining = (
        min(
            5.25 * 3600 - elapsed_seconds,
            (5.90 - prior_hours - 0.10) * 3600 - elapsed_seconds,
        )
        - 60
    )
    projected = 18 * measured_seconds
    if projected > remaining:
        raise ValueError(
            f"STOP: 18 lane walls ({projected:.1f}s) exceed remaining {remaining:.1f}s"
        )
    return {
        "measured_seconds": measured_seconds,
        "elapsed_seconds": elapsed_seconds,
        "prior_hours": prior_hours,
        "projected_seconds": projected,
        "remaining_seconds": remaining,
    }
