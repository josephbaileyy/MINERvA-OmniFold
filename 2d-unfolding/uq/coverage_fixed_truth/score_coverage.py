#!/usr/bin/env python3
"""Score fixed-truth 2D coverage toys against the production statistical band.

Definitions, windows and the verdict rule are pre-registered in
``docs/orchestration/PREREG-20261005-2d-fixed-truth-coverage.md``; this file is
their executable form and must not be changed after any full-run result is seen.

For toy ``t`` and reported bin ``b``::

    sigma_b = scale * r_b * T_b,   r_b = prod_sigma_b / prod_mean_b   (VL162 band)
    z_tb    = (U_tb - T_b) / sigma_b

Pooled coverage ``C_k`` is the fraction of (toy, bin) pairs with ``|z| <= k``.
Every toy carries the same reported bins, so ``C_k`` is the mean over toys of the
per-toy fraction, and intervals come from resampling toys (never bins), which keeps
each toy's bin correlations intact.

Amendment 1 adds a secondary, the replica form ``U_tb * T_b / P_tb``, where ``P`` is
the toy's bootstrapped MC truth prior. The VL162 replicas divide by a completeness
``c = sum(b w_truth) / sum(w_truth)`` per truth bin, which equals ``P / T``. The
central value and the toys have ``c = 1``. Scoring the replica form against the same
band tells whether a primary miscoverage comes from that term in the band.
"""

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

LEVEL_FINAL = 0.95
LEVEL_INTERIM = 0.995
N_MIN_FINAL = 150
N_MIN_INTERIM = 100
N_BOOT = 20_000
BOOT_SEED = 20_261_005
# Band-to-scatter ratio tolerated as "nominal": [0.9, 1.1].
BAND_RATIO_TOLERANCE = (0.9, 1.1)
CONTROL_SCALES = (0.7, 1.3)


def gauss_coverage(k):
    return math.erf(k / math.sqrt(2.0))


NOMINAL = {1: gauss_coverage(1.0), 2: gauss_coverage(2.0)}
WINDOWS = {k: (gauss_coverage(k * BAND_RATIO_TOLERANCE[0]),
               gauss_coverage(k * BAND_RATIO_TOLERANCE[1])) for k in (1, 2)}


class InvalidInput(ValueError):
    """The toy set or band fails a pre-registered validity check (a stop condition)."""


class InsufficientToys(ValueError):
    """Fewer completed toys than the pre-registered minimum for this look."""


def standardized_residuals(U, T, prod_mean, prod_sigma, reported, scale=1.0):
    """Return ``z`` with shape (n_toys, n_reported_bins)."""
    U = np.asarray(U, dtype=float)
    rep = np.asarray(reported, dtype=bool)
    T_r, m_r, s_r = (np.asarray(a, dtype=float)[rep] for a in (T, prod_mean, prod_sigma))
    U_r = U[:, rep]
    if not np.all(np.isfinite(U_r)):
        raise InvalidInput("non-finite unfolded value in a reported bin")
    if np.any(T_r <= 0) or np.any(m_r <= 0) or np.any(s_r <= 0):
        raise InvalidInput("fixed truth, production mean and production sigma must be "
                           "positive in every reported bin")
    sigma = scale * (s_r / m_r) * T_r
    return (U_r - T_r[None, :]) / sigma[None, :]


def replica_form(U, P, T, reported):
    """``U * T / P`` on reported bins (the VL162 replicas' completeness division)."""
    rep = np.asarray(reported, dtype=bool)
    P = np.asarray(P, dtype=float)
    if np.any(P[:, rep] <= 0):
        raise InvalidInput("toy prior must be positive in every reported bin")
    out = np.array(U, dtype=float, copy=True)
    out[:, rep] = out[:, rep] * np.asarray(T, dtype=float)[rep][None, :] / P[:, rep]
    return out


def per_toy_statistics(z):
    a = np.abs(z)
    return {"f1": (a <= 1.0).mean(axis=1), "f2": (a <= 2.0).mean(axis=1),
            "msq": (z * z).mean(axis=1), "mz": z.mean(axis=1)}


def toy_bootstrap_intervals(stats, level, n_boot=N_BOOT, seed=BOOT_SEED):
    n = stats["f1"].size
    idx = np.random.default_rng(seed).integers(0, n, size=(n_boot, n))
    lo, hi = 100 * (1 - level) / 2, 100 * (1 + level) / 2
    out = {}
    for key, stat in (("C1", stats["f1"]), ("C2", stats["f2"]),
                      ("pull_mean", stats["mz"])):
        boot = stat[idx].mean(axis=1)
        out[key] = [float(np.percentile(boot, lo)), float(np.percentile(boot, hi))]
    boot = np.sqrt(stats["msq"][idx].mean(axis=1))
    out["pull_rms"] = [float(np.percentile(boot, lo)), float(np.percentile(boot, hi))]
    return out


def classify(ci, window):
    """'inside', 'below', 'above' (CI disjoint from window) or 'overlap'."""
    if window[0] <= ci[0] and ci[1] <= window[1]:
        return "inside"
    if ci[1] < window[0]:
        return "below"
    if ci[0] > window[1]:
        return "above"
    return "overlap"


def verdict(intervals):
    """PASS, FAIL-undercoverage, FAIL-overcoverage, FAIL-mixed or INCONCLUSIVE."""
    cls = {k: classify(intervals[f"C{k}"], WINDOWS[k]) for k in (1, 2)}
    if all(c == "inside" for c in cls.values()):
        return "PASS", cls
    outside = {c for c in cls.values() if c in ("below", "above")}
    if outside == {"below"}:
        return "FAIL-undercoverage", cls
    if outside == {"above"}:
        return "FAIL-overcoverage", cls
    if outside:
        return "FAIL-mixed", cls
    return "INCONCLUSIVE", cls


def score(U, T, prod_mean, prod_sigma, reported, scale=1.0, level=LEVEL_FINAL,
          n_boot=N_BOOT, seed=BOOT_SEED):
    z = standardized_residuals(U, T, prod_mean, prod_sigma, reported, scale)
    st = per_toy_statistics(z)
    ci = toy_bootstrap_intervals(st, level, n_boot, seed)
    v, cls = verdict(ci)
    a = np.abs(z)
    c1_bin, c2_bin = (a <= 1).mean(axis=0), (a <= 2).mean(axis=0)
    return {
        "scale": scale, "level": level, "n_toys": int(z.shape[0]), "n_bins": int(z.shape[1]),
        "C1": float(st["f1"].mean()), "C2": float(st["f2"].mean()),
        "pull_rms": float(math.sqrt(st["msq"].mean())), "pull_mean": float(st["mz"].mean()),
        "intervals": ci, "verdict": v, "classification": cls,
        "per_bin": {"C1_median": float(np.median(c1_bin)), "C1_min": float(c1_bin.min()),
                    "C1_max": float(c1_bin.max()), "C2_median": float(np.median(c2_bin)),
                    "C2_min": float(c2_bin.min()),
                    "rms_median": float(np.median(np.sqrt((z * z).mean(axis=0)))),
                    "mean_abs_bias_median": float(np.median(np.abs(z.mean(axis=0))))},
    }


def positive_control(base, scaled):
    """Pre-registered sensitivity check on the real toy outputs.

    ``base`` is the scale-1 result; ``scaled`` maps each control scale to its result.
    (i) shrinking the band by 0.7 must move both coverage CIs entirely below the
    scale-1 point estimates, and widening by 1.3 entirely above; (ii) if the scale-1
    verdict is PASS, the scaled verdicts must be FAIL-undercoverage and
    FAIL-overcoverage, otherwise that PASS is void.
    """
    lo, hi = scaled[CONTROL_SCALES[0]], scaled[CONTROL_SCALES[1]]
    detect = all(lo["intervals"][f"C{k}"][1] < base[f"C{k}"] < hi["intervals"][f"C{k}"][0]
                 for k in (1, 2))
    flagged = (lo["verdict"] == "FAIL-undercoverage" and hi["verdict"] == "FAIL-overcoverage")
    return {"detects_both_directions": bool(detect),
            "scaled_verdicts": {str(s): scaled[s]["verdict"] for s in CONTROL_SCALES},
            "flags_miscoverage": bool(flagged),
            "passes": bool(detect and (flagged or base["verdict"] != "PASS"))}


def run(npz_path, stage, min_index=1, max_index=200):
    d = np.load(npz_path)
    keep = (d["toy_index"] >= min_index) & (d["toy_index"] <= max_index)
    if np.any(d["T_max_abs_diff"] != 0):
        raise InvalidInput("the stored truth differs between toys; the fixed-truth premise fails")
    level, n_min = ((LEVEL_INTERIM, N_MIN_INTERIM) if stage == "interim"
                    else (LEVEL_FINAL, N_MIN_FINAL))
    U = d["U"][keep]
    if U.shape[0] < n_min:
        raise InsufficientToys(f"{U.shape[0]} toys < pre-registered minimum {n_min} for {stage}")
    args = (U, d["T"], d["prod_mean"], d["prod_sigma"], d["reported"])
    base = score(*args, scale=1.0, level=level)
    scaled = {s: score(*args, scale=s, level=level) for s in CONTROL_SCALES}
    pc = positive_control(base, scaled)
    final = base["verdict"]
    if stage == "final" and final == "PASS" and not pc["passes"]:
        final = "INCONCLUSIVE (positive control failed)"
    if stage == "interim":
        final = ("STOP: " + base["verdict"] + " (futility)" if base["verdict"].startswith("FAIL")
                 else "CONTINUE")
    secondary = None
    if "P" in d.files:
        secondary = score(replica_form(U, d["P"][keep], d["T"], d["reported"]), *args[1:],
                          scale=1.0, level=level)
    return {"stage": stage, "nominal": NOMINAL, "windows": WINDOWS,
            "secondary_replica_form": secondary,
            "band_ratio_tolerance": BAND_RATIO_TOLERANCE,
            "toy_index_range": [int(d["toy_index"][keep].min()), int(d["toy_index"][keep].max())],
            "result": base, "controls": {str(s): r for s, r in scaled.items()},
            "positive_control": pc, "decision": final}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("npz")
    ap.add_argument("--stage", choices=["pilot", "interim", "final"], required=True)
    ap.add_argument("--min-index", type=int, default=1)
    ap.add_argument("--max-index", type=int, default=200)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.stage == "pilot":
        # The pilot exercises the scorer on 2-3 toys; no verdict is defined there.
        d = np.load(a.npz)
        z = standardized_residuals(d["U"], d["T"], d["prod_mean"], d["prod_sigma"], d["reported"])
        rep = d["reported"]
        ratio = d["prod_mean"][rep] / d["T"][rep]
        res = {"stage": "pilot", "n_toys": int(z.shape[0]), "n_bins": int(z.shape[1]),
               "per_toy": {k: v.tolist() for k, v in per_toy_statistics(z).items()},
               "T_max_abs_diff": d["T_max_abs_diff"].tolist(),
               "data_over_mc_truth": {q: float(np.percentile(ratio, p)) for q, p in
                                      (("p0", 0), ("p16", 16), ("p50", 50), ("p84", 84),
                                       ("p100", 100))}}
        if "P" in d.files:
            zr = standardized_residuals(replica_form(d["U"], d["P"], d["T"], rep), d["T"],
                                        d["prod_mean"], d["prod_sigma"], rep)
            res["per_toy_replica_form"] = {k: v.tolist()
                                           for k, v in per_toy_statistics(zr).items()}
    else:
        try:
            res = run(a.npz, a.stage, a.min_index, a.max_index)
        except InvalidInput as exc:
            res = {"stage": a.stage, "decision": "INVALID", "reason": str(exc)}
        except InsufficientToys as exc:
            res = {"stage": a.stage, "decision": "INSUFFICIENT-TOYS", "reason": str(exc)}
    Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True))
    print(json.dumps({k: res[k] for k in ("stage", "decision") if k in res}))
    return 2 if res.get("decision") in ("INVALID", "INSUFFICIENT-TOYS") else 0


if __name__ == "__main__":
    sys.exit(main())
