"""Shared plumbing for the Phase-B1 scalar references: the HISTORICAL code, imported, not rewritten.

Everything that defines the historical endpoint -- which rows form the two halves, the tilt, the
acceptance and displacement maps, the regions, the reference model and the recovery statistic --
is taken from the comparison's own modules under `nd-unfolding/pet/configuration_comparison/` and
`nd-unfolding/pet/`, whose bytes are checked against the tree of the campaign code commit
`68cf9d29` before anything is computed (`verify_historical_sources`). A mismatch is a refusal,
not a warning: a scalar reference scored on a drifted endpoint would not be comparable with the
historical PET numbers, and nothing downstream could tell.

Two things here are NOT historical code, and each is checked against historical code:

* `capture_endpoint` calls `report_campaign.build_endpoint` unchanged and records the acceptance,
  prior-mass and displacement maps it builds by wrapping `characterize_regions.region_census` for
  the duration of the call. The maps are therefore the historical function's own arrays, not a
  second construction of them.
* `score_push` repeats the five-line spectra construction inside `score_campaign.score_run`
  because `score_run` accepts only a `Run`, and a `Run` refuses any arm, stage or seed that is not
  on the frozen comparison lists -- correctly, for the comparison. It calls the historical
  `recovery`, `_histogram` and `overshoot_projection` for every number, and
  `test_scalar_references.py` asserts it is bit-identical to `score_run` on the same weights.

PET is diagnostic method development. Nothing here is a publication adoption, an uncertainty
product, a central-value change or a Gate-6 action, and no real data is read.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PET_DIR = REPO / "nd-unfolding" / "pet"
COMPARISON_DIR = PET_DIR / "configuration_comparison"

HISTORICAL_COMMIT = "68cf9d29f8ab1b0f5acd933d4baec1962b29e34d"

# `git rev-parse 68cf9d29:<path>` for every historical file this lane imports. Recorded on
# 2026-09-22 from the local object store; `verify_historical_sources` recomputes the blob id of the
# file the interpreter ACTUALLY loaded and refuses on any difference.
PINNED_BLOBS = {
    "nd-unfolding/pet/configuration_comparison/report_campaign.py":
        "0e032fa1d0e9dbdeec1ea2f821d6dd23f605c7b6",
    "nd-unfolding/pet/configuration_comparison/score_campaign.py":
        "3830ea708c8ee6806eefc571c11e93893a89850c",
    "nd-unfolding/pet/configuration_comparison/run_arm_evaluation.py":
        "ce826f2e10e1759223f6d0e7957dbb482c91e395",
    "nd-unfolding/pet/configuration_comparison/characterize_regions.py":
        "23068602c031bee7b4cbf14846e020dad35df519",
    "nd-unfolding/pet/configuration_comparison/reference_calibration.py":
        "279c46bacf6284be822731a0cf4d3b5cdb932078",
    "nd-unfolding/pet/configuration_comparison/frozen_design.py":
        "ac9dde237e8b4cd08552594b6607cdf65246735d",
    "nd-unfolding/pet/configuration_comparison/stage_splits.py":
        "87583ace8c4af778715be55234aec1a52234ad63",
    "nd-unfolding/pet/configuration_comparison/selection_rule.py":
        "1ef66a69aefb0e6623bcb033abeb9b2ca96d71e8",
    "nd-unfolding/pet/closure_powered_truth_reweight.py":
        "336ef4000abafec8b60b50ba4fb9913f1dad58c1",
    "nd-unfolding/pet/fullevent_fps_dataloader.py":
        "9a715ca0056b95dfaa6ff15ee0b265f13c036a77",
    "nd-unfolding/pet/train_fullevent_nominal.py":
        "9719049cfdcd669a215211821b132910ec3d1ce5",
}

# What the historical report recorded, re-measured by `prepare_populations.py` and refused on a
# difference. Values copied from `configuration_comparison/campaign_report.json` (provenance block).
REPORT_EXPECTATIONS = {
    "closure_npz_sha256": "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625",
    "half_a_rows": 600130,
    "half_b_rows": 600111,
    "half_b_rows_dropped_not_truth_passing": 32,
    "aggregate_reference": 0.6949731568655361,
    "regional_reference": {
        "low_acceptance": 0.013961265748028062,
        "poor": 0.3665375117479021,
        "moderate": 0.77652773176949,
        "good": 0.9754791562972827,
    },
    "scoreable_regions": ["low_acceptance", "moderate", "good"],
    # per_run recovery of the historical weights, used as an end-to-end check of the scorer mirror
    "per_run_recovery": {
        ("ours", 127): 0.32563324433093976,
        ("theirs", 127): 0.4934889970021603,
    },
}

# The historical run whose weights file defines the halves (every final run shares them;
# report_campaign refuses otherwise).
HISTORICAL_CAMPAIGN_DIR = "/pscratch/sd/j/josephrb/campaign-20260920"
HISTORICAL_WEIGHTS = {
    ("ours", 127): "final/ours-seed127/weights/weights_ours_final_127.npz",
    ("theirs", 127): "final/theirs-seed127/weights/weights_theirs_final_127.npz",
}

# Signal-MC members of the closure npz this lane may read. The npz also holds the real measured
# inventory (`measured_*`, `data_*`) and the background inventory; neither is ever opened here.
ALLOWED_NPZ_MEMBERS = frozenset({
    "truth_scalars", "reco_scalars", "pass_reco", "pass_truth", "w_truth", "w_reco",
    "part_reco", "edges_0", "edges_1",
})


def _ensure_paths() -> None:
    """Make the historical modules importable WITHOUT shadowing anything already resolved."""
    for path in (COMPARISON_DIR, PET_DIR):
        if str(path) not in sys.path:
            sys.path.append(str(path))


def git_blob_sha1(path: Path | str) -> str:
    """The id git would give this file's bytes (`git hash-object`)."""
    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def sha256_file(path: Path | str, chunk: int = 1 << 24) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def historical_modules() -> dict[str, Any]:
    """Import the historical modules and return them by short name."""
    _ensure_paths()
    import characterize_regions as cr
    import closure_powered_truth_reweight as cp
    import frozen_design as fd
    import reference_calibration as rc
    import report_campaign as rpt
    import run_arm_evaluation as rae
    import score_campaign as sc
    import stage_splits as ss
    return {"cr": cr, "cp": cp, "fd": fd, "rc": rc, "rpt": rpt, "rae": rae, "sc": sc, "ss": ss}


def verify_historical_sources(extra: Sequence[str] = ()) -> dict[str, Any]:
    """Blob ids of the historical files the interpreter loaded, against the 68cf9d29 tree.

    Checks the file behind each LOADED module (`module.__file__`), not a path assumed to hold it,
    so a copy imported from another checkout would fail here even if the local copy is pristine.
    """
    mods = historical_modules()
    loaded = {Path(m.__file__).resolve() for m in mods.values()}
    for name in extra:
        _ensure_paths()
        loaded.add(Path(__import__(name).__file__).resolve())
    rows = {}
    for path in sorted(loaded):
        rel = str(path.relative_to(REPO))
        got = git_blob_sha1(path)
        want = PINNED_BLOBS.get(rel)
        rows[rel] = {"loaded_from": str(path), "blob_sha1": got, "pinned_68cf9d29": want,
                     "matches": want is not None and got == want}
    bad = [k for k, v in rows.items() if not v["matches"]]
    if bad:
        raise SystemExit(f"[scalar] historical modules differ from {HISTORICAL_COMMIT[:8]} or are "
                         f"unpinned: {bad}. Refusing to score against a drifted endpoint.")
    return {"commit": HISTORICAL_COMMIT, "files": rows, "all_match": True}


def capture_endpoint(closure_npz: Path | str, weights_npz: Path | str
                     ) -> tuple[Any, dict[str, Any], dict[str, np.ndarray]]:
    """`report_campaign.build_endpoint`, unchanged, plus the maps it builds internally.

    The acceptance / prior-mass / displacement maps are recorded by wrapping
    `characterize_regions.region_census` for the duration of the call, so they are the historical
    function's own arrays. Returns (endpoint, context, maps).
    """
    mods = historical_modules()
    cr, rpt = mods["cr"], mods["rpt"]
    captured: dict[str, np.ndarray] = {}
    original = cr.region_census

    def recording_census(acceptance_cells, truth_mass_cells, displacement_cells):
        captured["acceptance"] = np.array(acceptance_cells, dtype=np.float64).ravel()
        captured["prior_mass"] = np.array(truth_mass_cells, dtype=np.float64).ravel()
        captured["displacement"] = np.array(displacement_cells, dtype=np.float64).ravel()
        return original(acceptance_cells, truth_mass_cells, displacement_cells)

    cr.region_census = recording_census
    try:
        endpoint, context = rpt.build_endpoint(closure_npz, weights_npz)
    finally:
        cr.region_census = original
    if set(captured) != {"acceptance", "prior_mass", "displacement"}:
        raise SystemExit("[scalar] build_endpoint no longer calls region_census; the maps "
                         "could not be captured from the historical code")
    return endpoint, context, captured


def reference_curve(acceptance: np.ndarray, displacement: np.ndarray,
                    iterations: Sequence[int]) -> dict[str, Any]:
    """The historical reference model `1-(1-a)^k`, displacement-weighted, at each k.

    Aggregate from `reference_calibration.ceiling`, regional from
    `characterize_regions.regional_reference` -- the functions that produced 0.6949731569 and the
    regional floors at k = 3.
    """
    mods = historical_modules()
    rc, cr = mods["rc"], mods["cr"]
    out = {"iterations": [int(k) for k in iterations], "aggregate": [], "regional": {}}
    for k in iterations:
        out["aggregate"].append(float(rc.ceiling(acceptance, displacement, int(k))))
        for name, value in cr.regional_reference(acceptance, displacement, int(k)).items():
            out["regional"].setdefault(name, []).append(value)
    return out


def score_push(endpoint: Any, push: np.ndarray, scoreable_regions: Sequence[str],
               informational_regions: Sequence[str] = ()) -> dict[str, Any]:
    """Recovery of a push over half B, exactly as `score_campaign.score_run` computes it.

    `push` is aligned to ALL of half B (the run's `dump_rows_b` order), as the engine's push is.
    Adds, beside the historical fields, the normalized spectra and the signed per-bin residual
    (unfolded - target), which the historical record does not carry.
    """
    mods = historical_modules()
    sc, rae = mods["sc"], mods["rae"]
    weights = np.asarray(push, dtype=np.float64)
    selector = endpoint.prior_selector
    if selector is not None and weights.size == np.asarray(selector).size:
        weights = weights[np.asarray(selector, dtype=bool)]
    if weights.size != endpoint.n_prior:
        raise ValueError(f"{weights.size} weights against {endpoint.n_prior} prior events")
    if not np.isfinite(weights).all() or (weights < 0).any():
        raise ValueError("push weights must be finite and non-negative")
    edges = endpoint.edges

    def spectra(mask_a: Any, mask_b: Any) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        prior = sc._histogram(endpoint.eavail_b[mask_b], endpoint.w_truth_b[mask_b], edges)
        unfolded = sc._histogram(endpoint.eavail_b[mask_b],
                                 (endpoint.w_truth_b * weights)[mask_b], edges)
        target = sc._histogram(endpoint.eavail_a[mask_a],
                               (endpoint.w_truth_a * endpoint.tilt_a)[mask_a], edges)
        return prior, unfolded, target

    def one(mask_a: Any, mask_b: Any) -> dict[str, Any]:
        prior, unfolded, target = spectra(mask_a, mask_b)
        scored = rae.recovery(prior, unfolded, target)
        pn, un, tn = (np.asarray(a, float) / np.asarray(a, float).sum()
                      for a in (prior, unfolded, target))
        return {
            "recovery": scored["recovery"],
            "injected_l1": scored["injected_l1"],
            "residual_l1": scored["residual_l1"],
            "overshoot_projection": float(sc.overshoot_projection(prior, unfolded, target)),
            "prior_hist": prior.tolist(), "unfolded_hist": unfolded.tolist(),
            "target_hist": target.tolist(),
            "signed_residual_per_bin": (un - tn).tolist(),
            "injected_per_bin": (tn - pn).tolist(),
        }

    all_a = np.ones(endpoint.eavail_a.shape, dtype=bool)
    all_b = np.ones(endpoint.eavail_b.shape, dtype=bool)
    result = {"aggregate": one(all_a, all_b), "regions": {}, "informational_regions": {}}
    for name in scoreable_regions:
        result["regions"][name] = one(np.asarray(endpoint.region_a) == name,
                                      np.asarray(endpoint.region_b) == name)
    for name in informational_regions:
        in_a = np.asarray(endpoint.region_a) == name
        in_b = np.asarray(endpoint.region_b) == name
        if in_a.any() and in_b.any():
            result["informational_regions"][name] = one(in_a, in_b)
    result["recovery"] = result["aggregate"]["recovery"]
    result["recovery_by_region"] = {k: v["recovery"] for k, v in result["regions"].items()}
    return result


def ess(weights: np.ndarray) -> float:
    """(sum w)^2 / sum w^2 for NON-NEGATIVE weights (refused otherwise)."""
    w = np.asarray(weights, dtype=np.float64)
    if (w < 0).any():
        raise ValueError("ESS is defined here for non-negative weights only")
    s2 = float((w * w).sum())
    return float(w.sum() ** 2 / s2) if s2 > 0 else 0.0


def weight_summary(weights: np.ndarray) -> dict[str, float]:
    w = np.asarray(weights, dtype=np.float64)
    q = np.percentile(w, [0.1, 1, 50, 99, 99.9]) if w.size else [np.nan] * 5
    return {"n": int(w.size), "min": float(w.min()), "max": float(w.max()),
            "mean": float(w.mean()), "p0.1": float(q[0]), "p1": float(q[1]),
            "p50": float(q[2]), "p99": float(q[3]), "p99.9": float(q[4]),
            "ess_over_n": ess(w) / max(w.size, 1)}


def repo_commit() -> str:
    """HEAD of the checkout this file sits in (the pinned compute checkout on the cluster)."""
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], check=True, cwd=str(REPO),
                              capture_output=True, text=True).stdout.strip()
    except Exception:  # noqa: BLE001 -- recorded, not fatal
        return "unknown"


def refuse_historical_output(path: Path | str) -> Path:
    """The historical comparison's outputs are never a write target."""
    resolved = Path(path).resolve()
    if str(resolved).startswith(HISTORICAL_CAMPAIGN_DIR):
        raise SystemExit(f"[scalar] refusing to write under the historical campaign dir: {resolved}")
    if COMPARISON_DIR in resolved.parents or resolved == COMPARISON_DIR:
        raise SystemExit(f"[scalar] refusing to write into configuration_comparison/: {resolved}")
    return resolved


def write_json(path: Path | str, payload: Mapping[str, Any], compact: bool = False) -> None:
    path = refuse_historical_output(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    text = (json.dumps(payload, separators=(",", ":"), allow_nan=False, default=_json_default)
            if compact else
            json.dumps(payload, indent=1, allow_nan=False, default=_json_default))
    tmp.write_text(text + "\n")
    os.replace(tmp, path)


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f"not JSON serializable: {type(obj)}")


def load_populations(path: Path | str) -> dict[str, np.ndarray]:
    """The cached half-A / half-B arrays written by `prepare_populations.py`."""
    with np.load(path, allow_pickle=False) as handle:
        return {k: np.asarray(handle[k]) for k in handle.files}


def endpoint_from_populations(pop: Mapping[str, np.ndarray]) -> Any:
    """Rebuild the historical `score_campaign.Endpoint` from the cached arrays.

    The arrays were copied out of `report_campaign.build_endpoint`'s own Endpoint by
    `prepare_populations.py`, which also verified this reconstruction scores the historical weights
    to the report's recovery; the class is the historical one, so its validation runs again here.
    """
    sc = historical_modules()["sc"]
    return sc.Endpoint(
        eavail_a=pop["ep_eavail_a"], w_truth_a=pop["ep_w_truth_a"], tilt_a=pop["ep_tilt_a"],
        region_a=pop["ep_region_a"].astype("<U32"),
        eavail_b=pop["ep_eavail_b"], w_truth_b=pop["ep_w_truth_b"],
        region_b=pop["ep_region_b"].astype("<U32"),
        prior_selector=pop["ep_prior_selector"].astype(bool))
