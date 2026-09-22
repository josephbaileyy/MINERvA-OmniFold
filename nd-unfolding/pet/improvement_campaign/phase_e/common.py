"""Shared plumbing for the Phase-E scalar work: pool caches, replicate samples, pool-level targets,
and the historical recovery statistic scored against them.

The recovery, histogram and overshoot functions are the HISTORICAL ones
(`run_arm_evaluation.recovery`, `score_campaign._histogram`, `score_campaign.overshoot_projection`),
imported through `phase_b/scalar/scalar_common.py`, which checks each loaded file's git blob id
against the comparison's code commit `68cf9d29` and refuses on a difference. What differs from the
historical endpoint is only WHERE the target comes from: Amendment 1 scores against the distorted
truth spectrum of ALL of pool T (not a second half), and the prior is a replicate draw. The
regions are the historical ones: an event's region is its truth (p_T, p_par) cell's, under the
historical acceptance map (`characterize_regions.region_labels_for_events`).

PET is diagnostic method development; only signal-MC simulation is read.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

HERE = Path(__file__).resolve().parent
SCALAR_DIR = HERE.parent / "phase_b" / "scalar"
for _p in (HERE, SCALAR_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import scalar_common as scm  # noqa: E402

SCOREABLE = ("low_acceptance", "moderate", "good")
INFORMATIONAL = ("poor",)
REGION_CODES = {"low_acceptance": 0, "poor": 1, "moderate": 2, "good": 3,
                "outside_the_reporting_grid": -1}
ENDPOINT_EDGES = np.array([0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0])
Q3_EDGES = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.2, 2.0, 100.0])      # N-D reporting grid
HISTORICAL_SIZES = {"prior": 600_130, "pseudo": 600_111}              # PROTOCOL section 5.3

B1_POPULATIONS_SHA256 = "b2b55791a25523ef510a099cbbd0defcf3157ab59af2580c219fe088ccb96da1"


# ------------------------------------------------------------------------------------------- #
# Caches
# ------------------------------------------------------------------------------------------- #
def load_cache(path: Path | str, expected_sha256: str | None = None) -> dict[str, np.ndarray]:
    """A pool cache written by `prepare_pools.py`; refuses on a sha256 mismatch if one is given."""
    if expected_sha256 is not None:
        got = scm.sha256_file(path)
        if got != expected_sha256:
            raise SystemExit(f"[phase-e] cache {path} sha256 {got} != {expected_sha256}")
    with np.load(path, allow_pickle=False) as handle:
        return {k: np.asarray(handle[k]) for k in handle.files}


def positions(cache: Mapping[str, np.ndarray], rows: np.ndarray) -> np.ndarray:
    """Positions in the cache of the given inventory rows (refused if any is absent)."""
    crow = cache["rows"]
    pos = np.searchsorted(crow, rows)
    if (pos >= crow.size).any() or not np.array_equal(crow[np.minimum(pos, crow.size - 1)], rows):
        raise ValueError("rows not in this pool cache")
    return pos


def take(cache: Mapping[str, np.ndarray], rows: np.ndarray) -> dict[str, np.ndarray]:
    """Every per-event array of the cache at the given rows (same order)."""
    pos = positions(cache, rows)
    n = cache["rows"].size
    return {k: v[pos] for k, v in cache.items() if v.ndim >= 1 and v.shape[0] == n}


def truth_view(s: Mapping[str, np.ndarray]) -> dict[str, np.ndarray]:
    """The truth mapping `Distortion.truth_weight` reads."""
    t = s["truth"]
    out = {"pt": t[:, 0], "ppar": t[:, 1], "eavail": t[:, 2], "q3": t[:, 3]}
    for k in ("n_pipm", "n_pi0", "n_p", "n_n"):
        if k in s:
            out[k] = s[k]
    return out


def reco_view(s: Mapping[str, np.ndarray], mask: np.ndarray | None = None) -> dict[str, np.ndarray]:
    """The reco mapping `Distortion.transform` reads (rows selected by ``mask``)."""
    m = slice(None) if mask is None else np.asarray(mask, dtype=bool)
    r = s["reco"]
    out = {"pt": r[m, 0], "ppar": r[m, 1], "eavail": r[m, 2], "q3": r[m, 3]}
    if "tok_E" in s:
        out["tok_E"] = s["tok_E"][m].astype(np.float64)
    return out


# ------------------------------------------------------------------------------------------- #
# Targets and scoring
# ------------------------------------------------------------------------------------------- #
def historical():
    """The historical scoring functions (blob-checked against 68cf9d29 on first use)."""
    if not getattr(historical, "_verified", None):
        historical._verified = scm.verify_historical_sources()
    return scm.historical_modules()


def region_masks(region_code: np.ndarray) -> dict[str, np.ndarray]:
    rc = np.asarray(region_code)
    return {name: rc == code for name, code in REGION_CODES.items() if code >= 0}


def target_spectra(eavail: np.ndarray, w_truth: np.ndarray, weight: np.ndarray,
                   region_code: np.ndarray) -> dict[str, np.ndarray]:
    """The seven-bin truth E_avail spectrum of a whole pool, weighted by w_truth x ``weight``,
    in aggregate and per historical region (np.histogram, as `score_campaign._histogram`)."""
    sc = historical()["sc"]
    w = np.asarray(w_truth, np.float64) * np.asarray(weight, np.float64)
    out = {"aggregate": sc._histogram(eavail, w, ENDPOINT_EDGES)}
    for name, m in region_masks(region_code).items():
        out[name] = sc._histogram(eavail[m], w[m], ENDPOINT_EDGES)
    return out


def _one(prior: np.ndarray, unfolded: np.ndarray, target: np.ndarray) -> dict[str, Any]:
    mods = historical()
    rae, sc = mods["rae"], mods["sc"]
    scored = rae.recovery(prior, unfolded, target)
    pn, un, tn = (np.asarray(a, float) / np.asarray(a, float).sum()
                  for a in (prior, unfolded, target))
    return {"recovery": scored["recovery"], "injected_l1": scored["injected_l1"],
            "residual_l1": scored["residual_l1"],
            "overshoot_projection": float(sc.overshoot_projection(prior, unfolded, target)),
            "prior_hist": np.asarray(prior).tolist(), "unfolded_hist": np.asarray(unfolded).tolist(),
            "target_hist": np.asarray(target).tolist(),
            "signed_residual_per_bin": (un - tn).tolist(), "injected_per_bin": (tn - pn).tolist()}


def score(eavail: np.ndarray, w_truth: np.ndarray, push: np.ndarray, region_code: np.ndarray,
          targets: Mapping[str, np.ndarray], compact: bool = False) -> dict[str, Any]:
    """The historical recovery of a push over the PRIOR sample against pool-level ``targets``,
    aggregate and per region; field-for-field what `scalar_common.score_push` returns."""
    sc = historical()["sc"]
    push = np.asarray(push, np.float64)
    if not np.isfinite(push).all() or (push < 0).any():
        raise ValueError("push weights must be finite and non-negative")
    w = np.asarray(w_truth, np.float64)

    def part(m: Any, tgt: np.ndarray) -> dict[str, Any]:
        prior = sc._histogram(eavail[m], w[m], ENDPOINT_EDGES)
        unfolded = sc._histogram(eavail[m], (w * push)[m], ENDPOINT_EDGES)
        return _one(prior, unfolded, tgt)

    masks = region_masks(region_code)
    res = {"aggregate": part(slice(None), targets["aggregate"]), "regions": {},
           "informational_regions": {}}
    for name in SCOREABLE:
        res["regions"][name] = part(masks[name], targets[name])
    for name in INFORMATIONAL:
        if masks[name].any():
            res["informational_regions"][name] = part(masks[name], targets[name])
    res["recovery"] = res["aggregate"]["recovery"]
    res["recovery_by_region"] = {k: v["recovery"] for k, v in res["regions"].items()}
    if compact:
        return compact_score(res)
    return res


def compact_score(res: Mapping[str, Any]) -> dict[str, Any]:
    agg = res["aggregate"]
    return {"recovery": res["recovery"], "recovery_by_region": res["recovery_by_region"],
            "overshoot_projection": agg["overshoot_projection"],
            "injected_l1": agg["injected_l1"], "residual_l1": agg["residual_l1"],
            "signed_residual_per_bin": agg["signed_residual_per_bin"],
            "injected_per_bin": agg["injected_per_bin"],
            "regions": {k: {"recovery": v["recovery"], "injected_l1": v["injected_l1"],
                            "residual_l1": v["residual_l1"],
                            "signed_residual_per_bin": v["signed_residual_per_bin"]}
                        for k, v in res["regions"].items()},
            "informational": {k: v["recovery"] for k, v in res["informational_regions"].items()}}


def spurious_displacement(eavail: np.ndarray, w_truth: np.ndarray, push: np.ndarray,
                          target: np.ndarray) -> dict[str, Any]:
    """For a response-only distortion (no truth change): where the unfolded spectrum lands
    relative to the undistorted pool-T target. L1 on normalized seven-bin spectra; the prior's own
    L1 to the target is the finite-sample baseline a do-nothing estimator already has."""
    sc = historical()["sc"]
    w = np.asarray(w_truth, np.float64)
    prior = sc._histogram(eavail, w, ENDPOINT_EDGES)
    unfolded = sc._histogram(eavail, w * np.asarray(push, np.float64), ENDPOINT_EDGES)
    pn, un, tn = (np.asarray(a, float) / np.asarray(a, float).sum()
                  for a in (prior, unfolded, target))
    return {"unfolded_minus_target_l1": float(np.abs(un - tn).sum()),
            "prior_minus_target_l1": float(np.abs(pn - tn).sum()),
            "unfolded_minus_prior_l1": float(np.abs(un - pn).sum()),
            "signed_unfolded_minus_target_per_bin": (un - tn).tolist(),
            "signed_prior_minus_target_per_bin": (pn - tn).tolist()}


def joint_hist(x: np.ndarray, y: np.ndarray, w: np.ndarray, ex: np.ndarray, ey: np.ndarray
               ) -> np.ndarray:
    h, _, _ = np.histogram2d(np.asarray(x, float), np.asarray(y, float), bins=[ex, ey],
                             weights=np.asarray(w, float))
    return h.ravel()


def joint_recovery(prior: np.ndarray, unfolded: np.ndarray, target: np.ndarray) -> dict[str, Any]:
    """The historical recovery statistic applied to a flattened joint histogram."""
    rae = historical()["rae"]
    r = rae.recovery(prior, unfolded, target)
    return {"recovery": r["recovery"], "injected_l1": r["injected_l1"],
            "residual_l1": r["residual_l1"]}


# ------------------------------------------------------------------------------------------- #
# Misc
# ------------------------------------------------------------------------------------------- #
def environment() -> dict[str, Any]:
    return {k: os.environ.get(k) for k in ("SLURM_JOB_ID", "SLURM_ARRAY_JOB_ID",
                                          "SLURM_ARRAY_TASK_ID", "OMP_NUM_THREADS",
                                          "SLURM_CPUS_PER_TASK")}


def canonical_sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                     default=scm._json_default).encode()).hexdigest()


def write_json(path: Path | str, payload: Mapping[str, Any], compact: bool = True) -> None:
    scm.write_json(path, payload, compact=compact)
