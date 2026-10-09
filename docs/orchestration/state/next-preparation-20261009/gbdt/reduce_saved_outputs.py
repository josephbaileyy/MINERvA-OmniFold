#!/usr/bin/env python3
"""Saved-output reductions and design arithmetic for the scalar-5D GBDT successor design.

Reads only committed operands (``nd-unfolding/gbdt_model_dependence/inputs/operands.npz``,
its inventory and two s5e receipts). It imports NumPy and SciPy, never a repository module, so no
production code can be resolved from another checkout. It performs no fit, toy, resampling or
training, and writes one JSON file.

Usage, from the repository root::

    python3 docs/orchestration/state/next-preparation-20261009/gbdt/reduce_saved_outputs.py \
        --out docs/orchestration/state/next-preparation-20261009/gbdt/results.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[5]
SYNTH = ROOT / "nd-unfolding/gbdt_model_dependence"
OPERANDS = SYNTH / "inputs/operands.npz"
INVENTORY = SYNTH / "inputs/inventory.json"
ASSESS = ROOT / "docs/orchestration/state/s5e/cand/assess_receipt.json"
DIAG = ROOT / "docs/orchestration/state/s5e/diag/diag_receipt.json"

GROUPS = ("EW", "J", "H2")
DEPARTURES = ("eavail_gibuu", "q3", "W1", "W2", "W3")
# Departure truth -> data prior carrying the same ratio file (inventory ratio_sha256 identity).
PRIOR_OF = {"eavail_gibuu": "d1", "W1": "d2", "W2": "d3", "W3": "d4"}
# Noise-free B0 traces -> assessment truth of the same ratio identity.
TRACE_OF = {"eavail_gibuu": "gibuu", "q3": "q3", "W1": "w1", "W3": "w3"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def masks(z: Any) -> dict[str, np.ndarray]:
    return {g: (z["groups"] == g) & z["reported"] for g in GROUPS}


def rel(estimate: np.ndarray, truth: np.ndarray) -> np.ndarray:
    return estimate / truth - 1.0


def ensemble(z: Any, point: str) -> dict[str, np.ndarray]:
    estimate, truth = z[f"assessment_{point}"], z[f"assessment_{point}_truth"]
    residual = rel(estimate, truth)
    n = residual.shape[0]
    bias = residual.mean(axis=0)
    sd = residual.std(axis=0, ddof=1)
    return {"n": n, "residual": residual, "bias": bias, "sd": sd, "se": sd / math.sqrt(n)}


def med(values: np.ndarray) -> float:
    return float(np.median(values))


def integrity(z: Any) -> dict[str, Any]:
    inventory = json.loads(INVENTORY.read_text())
    observed = sha256(OPERANDS)
    if observed != inventory["operands_sha256"]:
        raise SystemExit(f"operands digest {observed} != inventory {inventory['operands_sha256']}")
    counts = {g: int(((z["groups"] == g)).sum()) for g in GROUPS}
    reported = {g: int(m.sum()) for g, m in masks(z).items()}
    return {
        "operands_sha256": observed,
        "inventory_sha256": sha256(INVENTORY),
        "assess_receipt_sha256": sha256(ASSESS),
        "diag_receipt_sha256": sha256(DIAG),
        "functional_counts": counts,
        "reported_counts": reported,
    }


def receipt_crosscheck(z: Any) -> dict[str, Any]:
    """Compare ensemble means/SDs with the s5e assessment receipt (its own primary operand)."""
    receipt = json.loads(ASSESS.read_text())
    names = [str(n) for n in z["names"]]
    worst: dict[str, float] = {}
    for point in ("nominal",) + DEPARTURES:
        e = ensemble(z, point)
        per = receipt["points"][point]["per_functional"]
        diffs_mean, diffs_sd = [], []
        for j, name in enumerate(receipt["functional_names"]):
            if name not in names:
                continue
            i = names.index(name)
            diffs_mean.append(abs(e["bias"][i] - per["mean_rel"][j]))
            diffs_sd.append(abs(e["sd"][i] - per["rel_sd"][j]))
        worst[point] = max(max(diffs_mean), max(diffs_sd))
    shared = sorted(set(receipt["functional_names"]) & set(names))
    return {
        "n_receipt_functionals": len(receipt["functional_names"]),
        "n_compared": len(shared),
        "max_abs_diff": worst,
    }


def headline(z: Any) -> dict[str, Any]:
    m = masks(z)
    names = [str(n) for n in z["names"]]
    out: dict[str, Any] = {}
    w3, w3t = z["trace_b0_w3"], z["trace_b0_w3_truth"]
    for k in (5, 200):
        r = np.abs(rel(w3[k - 1], w3t)) * 100
        out[f"W3_trace_K{k}"] = {
            "J_median_pct": med(r[m["J"]]),
            "J_max_pct": float(r[m["J"]].max()),
            "H2_median_pct": med(r[m["H2"]]),
        }
    e = ensemble(z, "W3")
    i = names.index("EW29")
    out["W3_assessment_EW29"] = {"bias_pct": e["bias"][i] * 100, "sd_pct": e["sd"][i] * 100}
    i = names.index("EW7")
    out["W3_assessment_EW7"] = {"bias_pct": e["bias"][i] * 100, "sd_pct": e["sd"][i] * 100}
    sigma = z["sigma"].std(axis=0, ddof=1)
    nominal, truth = z["assessment_nominal"], z["assessment_nominal_truth"]
    i = names.index("EW41")
    hits = int((np.abs(nominal[:, i] - truth[:, i]) <= sigma[i]).sum())
    out["nominal_EW41_hits68"] = {"hits": hits, "n": int(nominal.shape[0])}
    return out


def bias_variance(z: Any) -> dict[str, Any]:
    """K=5 assessment ensembles (candidate R): is the error bias or repeat variance?"""
    m = masks(z)
    out: dict[str, Any] = {}
    for point in ("nominal",) + DEPARTURES:
        e = ensemble(z, point)
        t = e["bias"] / e["se"]
        share = e["bias"] ** 2 / (e["bias"] ** 2 + e["sd"] ** 2)
        out[point] = {
            g: {
                "n": e["n"],
                "median_abs_bias_pct": med(np.abs(e["bias"][m[g]]) * 100),
                "max_abs_bias_pct": float(np.abs(e["bias"][m[g]]).max() * 100),
                "median_sd_pct": med(e["sd"][m[g]] * 100),
                "median_abs_bias_over_sd": med(np.abs(e["bias"][m[g]]) / e["sd"][m[g]]),
                "fraction_abs_t_gt_3p6": float(np.mean(np.abs(t[m[g]]) > 3.6)),
                "median_bias_share_of_mse": med(share[m[g]]),
            }
            for g in GROUPS
        }
    return out


def asimov_vs_ensemble(z: Any) -> dict[str, Any]:
    """Noise-free B0 K=5 residual against the R K=5 ensemble mean of the same ratio identity."""
    m = masks(z)
    out: dict[str, Any] = {}
    for point, trace in TRACE_OF.items():
        r_nf = rel(z[f"trace_b0_{trace}"][4], z[f"trace_b0_{trace}_truth"])
        e = ensemble(z, point)
        out[point] = {}
        for g in GROUPS:
            a, b, se = r_nf[m[g]], e["bias"][m[g]], e["se"][m[g]]
            out[point][g] = {
                "pearson": float(np.corrcoef(a, b)[0, 1]),
                "median_abs_diff_pct": med(np.abs(a - b) * 100),
                "median_abs_ensemble_bias_pct": med(np.abs(b) * 100),
                "median_abs_diff_over_se": med(np.abs(a - b) / se),
                "slope_ensemble_on_noise_free": float(np.dot(a, b) / np.dot(a, a)),
            }
    return out


def convergence(z: Any) -> dict[str, Any]:
    m = masks(z)
    nominal_truth = z["trace_nominal_truth"]
    out: dict[str, Any] = {}
    for key in ("w3", "gibuu", "w1", "q3", "nominal"):
        trace, truth = z[f"trace_b0_{key}"], z[f"trace_b0_{key}_truth"]
        kmax = trace.shape[0]
        residual = rel(trace, truth)
        departure = truth / nominal_truth - 1.0
        out[key] = {"K_available": kmax}
        for g in GROUPS:
            r = np.abs(residual[:, m[g]]) * 100
            ks = [k for k in (1, 5, 10, 20, 30, 40, 100, 200) if k <= kmax]
            row: dict[str, Any] = {f"median_abs_pct_K{k}": med(r[k - 1]) for k in ks}
            row["max_abs_pct_K5"] = float(r[4].max())
            row[f"max_abs_pct_K{kmax}"] = float(r[kmax - 1].max())
            row["fraction_cells_worse_at_Kmax_than_K5"] = float(np.mean(r[kmax - 1] > r[4]))
            half = max(kmax // 2, 5)
            row["median_abs_drift_pp_Khalf_to_Kmax"] = med(np.abs(r[kmax - 1] - r[half - 1]))
            if key != "nominal":
                dep = departure[m[g]]
                eligible = np.abs(dep) > 0.01
                if eligible.any():
                    est = trace[:, m[g]] / nominal_truth[m[g]] - 1.0
                    for k in (5, kmax):
                        rho = est[k - 1][eligible] / dep[eligible]
                        row[f"recovered_fraction_K{k}"] = {
                            "n_cells": int(eligible.sum()),
                            "median": med(rho),
                            "fraction_below_0": float(np.mean(rho < 0)),
                            "fraction_in_0_1": float(np.mean((rho >= 0) & (rho <= 1))),
                            "fraction_above_1": float(np.mean(rho > 1)),
                        }
            out[key][g] = row
    for key in ("w3", "gibuu", "q3"):
        cap, truth = z[f"trace_cap10_{key}"], z[f"trace_cap10_{key}_truth"]
        b0, b0truth = z[f"trace_b0_{key}"], z[f"trace_b0_{key}_truth"]
        out[f"capacity_{key}"] = {
            g: {
                "cap400_31_K10_median_abs_pct": med(np.abs(rel(cap[9], truth))[m[g]] * 100),
                "b0_K10_median_abs_pct": med(np.abs(rel(b0[9], b0truth))[m[g]] * 100),
            }
            for g in GROUPS
        }
    return out


def prior_pull(z: Any) -> dict[str, Any]:
    """Linear prior-pull prediction r_T ~= -s_T (closure residual vs data shift under prior T)."""
    m = masks(z)
    cv = z["CV"]
    out: dict[str, Any] = {}
    for point, prior in PRIOR_OF.items():
        r = ensemble(z, point)["bias"]
        s = z[f"prior_{prior}"] / cv - 1.0
        out[point] = {"prior": prior}
        for g in GROUPS:
            a, b = r[m[g]], -s[m[g]]
            out[point][g] = {
                "pearson_r_vs_minus_s": float(np.corrcoef(a, b)[0, 1]),
                "slope_r_on_minus_s": float(np.dot(a, b) / np.dot(b, b)),
                "fraction_r2_explained_by_minus_s": float(1 - np.sum((a - b) ** 2) / np.sum(a**2)),
                "median_abs_r_pct": med(np.abs(a) * 100),
                "median_abs_r_plus_s_pct": med(np.abs(a - b) * 100),
            }
    return out


def model_allowance(z: Any) -> dict[str, Any]:
    """Cellwise max |K=5 ensemble bias| over development departures against the 5% proposal."""
    m = masks(z)
    biases = np.array([np.abs(ensemble(z, p)["bias"]) for p in DEPARTURES])
    upper = np.array(
        [np.abs(ensemble(z, p)["bias"]) + 3.0 * ensemble(z, p)["se"] for p in DEPARTURES]
    )
    out: dict[str, Any] = {"departures": list(DEPARTURES)}
    for g in GROUPS:
        b = biases[:, m[g]].max(axis=0) * 100
        leave_one = {
            DEPARTURES[i]: med(np.delete(biases[:, m[g]], i, axis=0).max(axis=0) * 100)
            for i in range(len(DEPARTURES))
        }
        out[g] = {
            "median_max_abs_bias_pct": med(b),
            "p90_max_abs_bias_pct": float(np.percentile(b, 90)),
            "fraction_cells_max_abs_bias_le_5pct": float(np.mean(b <= 5.0)),
            "fraction_cells_max_abs_bias_le_10pct": float(np.mean(b <= 10.0)),
            "median_with_3se_pct": med(upper[:, m[g]].max(axis=0) * 100),
            "leave_one_departure_out_median_pct": leave_one,
        }
    return out


def visibility(z: Any) -> dict[str, Any]:
    """Reco-imprint of the noise-free residual relative to the departure's own reco signal (s5e D4)."""
    diag = json.loads(DIAG.read_text())
    m = masks(z)
    nominal_truth = z["trace_nominal_truth"]
    out: dict[str, Any] = {}
    for name, trace in (("eavail", "gibuu"), ("q3", "q3")):
        d4 = diag["D4"][name]
        truth = z[f"trace_b0_{trace}_truth"]
        dep = np.abs(truth / nominal_truth - 1.0)
        rows = {}
        for entry in d4["per_k"]:
            k = entry["k"]
            if k not in (1, 5, 10, 20, 30):
                continue
            r = np.abs(rel(z[f"trace_b0_{trace}"][k - 1], truth))
            rows[f"K{k}"] = {
                "lambda_ew": entry["ew_chi2_push_vs_true"],
                "lambda_5d": entry["reco5d_chi2_push_vs_true"],
                "reco_amplitude_ratio_5d": math.sqrt(entry["reco5d_chi2_push_vs_true"] / d4["S_dep_reco5d"]),
                "truth_amplitude_ratio_J_rms": float(
                    math.sqrt(np.mean(r[m["J"]] ** 2) / np.mean(dep[m["J"]] ** 2))
                ),
                "omnibus_excess_sigma_5d": (entry["reco5d_chi2_push_vs_true"])
                / math.sqrt(2 * d4["ncell_reco5d"] + 4 * entry["reco5d_chi2_push_vs_true"]),
            }
        out[name] = {"S_dep_reco5d": d4["S_dep_reco5d"], "ncell_reco5d": d4["ncell_reco5d"], "per_k": rows}
    return out


def fold_misfit_series() -> dict[str, Any]:
    """Noise-free fold misfit per iteration (s5e D4/D5): does it fall monotonically, as exact EM must?"""
    diag = json.loads(DIAG.read_text())
    out: dict[str, Any] = {}
    for section, name in (("D4", "eavail"), ("D4", "q3"), ("D5", "capacity_eavail"),
                          ("D5", "capacity_q3"), ("D5", "missed_unity_eavail"),
                          ("D5", "missed_unity_q3")):
        per_k = diag[section][name]["per_k"]
        ew = [e["ew_chi2_push_vs_true"] for e in per_k]
        five = [(e["k"], e.get("reco5d_chi2_push_vs_true")) for e in per_k]
        five = [(k, v) for k, v in five if v is not None]
        rises_ew = [per_k[i + 1]["k"] for i in range(len(ew) - 1) if ew[i + 1] > ew[i]]
        rises_5d = [five[i + 1][0] for i in range(len(five) - 1) if five[i + 1][1] > five[i][1]]
        last = five[-1][1]
        prior_point = [v for k, v in five if k <= five[-1][0] // 2][-1]
        out[f"{section}_{name}"] = {
            "K": per_k[-1]["k"],
            "lambda_ew_first_last": [ew[0], ew[-1]],
            "lambda_5d_by_k": dict((str(k), v) for k, v in five),
            "ew_increases_at_k": rises_ew,
            "five_d_increases_at_k": rises_5d,
            "lambda_5d_last_over_half_k": last / prior_point,
            "median_abs_ew_residual_pct_first_last": [
                per_k[0]["push"]["median_abs_pct"], per_k[-1]["push"]["median_abs_pct"]],
        }
    return out


# ----------------------------------------------------------------------------- design arithmetic


def cp_lower(hits: int, n: int, alpha: float) -> float:
    return 0.0 if hits == 0 else float(stats.beta.ppf(alpha, hits, n - hits + 1))


def min_hits_for_lower(n: int, alpha: float, bound: float) -> int:
    """Smallest hit count whose one-sided exact lower bound is >= bound (bisection on hits)."""
    lo, hi = 0, n
    if cp_lower(n, n, alpha) < bound:
        return n + 1
    while lo < hi:
        mid = (lo + hi) // 2
        if cp_lower(mid, n, alpha) >= bound:
            hi = mid
        else:
            lo = mid + 1
    return lo


def lower_bound_design(n_tests: int, alpha_fw: float, bound: float, p_true: float,
                       assurance: float) -> dict[str, Any]:
    """Smallest N per case: every test's one-sided exact lower bound >= bound, union-bound assurance."""
    alpha = alpha_fw / n_tests
    for n in range(50, 200001):
        h = min_hits_for_lower(n, alpha, bound)
        if h > n:
            continue
        fail_one = float(stats.binom.cdf(h - 1, n, p_true))
        if 1.0 - n_tests * fail_one >= assurance:
            return {"N": n, "min_hits": h, "per_test_alpha": alpha, "fail_prob_one": fail_one}
    raise ValueError("no N found")


def design(costs: dict[str, float]) -> dict[str, Any]:
    nominal68, nominal95 = 0.682689492137, 0.95
    families = {"H2_27": 27, "J_109": 109, "reported_175": 175}
    out: dict[str, Any] = {"assumptions": {}}
    for label, f in families.items():
        for cases in (1, 4):
            for level, (bound, p) in {"I68": (0.63, nominal68), "I95": (0.92, nominal95)}.items():
                tests = f * cases * 2  # both levels are in the family
                key = f"{label}_cases{cases}_{level}"
                out[key] = lower_bound_design(tests, 0.05, bound, p, 0.80)
    # Cost of reconstructing each experiment's interval by the frozen procedure.
    t_pseudo = costs["pseudo_f32_K5_s"]
    node_threads, steps_per_node, packing = 256, 8, 1.25
    per_unfold_node_h = t_pseudo / (steps_per_node * 3600) * packing
    recipes = {
        "central_only": 1,
        "central_plus_30_bootstrap": 31,
        "central_plus_100_bootstrap": 101,
        "central_plus_100_bootstrap_plus_187_universes": 288,
    }
    n_case = max(out["J_109_cases4_I68"]["N"], out["J_109_cases4_I95"]["N"])
    out["assumptions"] = {
        "pseudo_unfold_seconds_K5_32threads": t_pseudo,
        "steps_per_node": steps_per_node,
        "node_threads": node_threads,
        "packing_allowance": packing,
        "node_h_per_unfold": per_unfold_node_h,
        "reserve_rule": "admitted = subtotal / 0.8",
        "N_per_case_used": n_case,
        "cases": 4,
    }
    validation = {}
    for name, unfolds in recipes.items():
        sub = 4 * n_case * unfolds * per_unfold_node_h
        validation[name] = {"unfolds_per_experiment": unfolds, "subtotal_node_h": sub,
                            "admitted_node_h": sub / 0.8}
    out["validation_cost"] = validation
    speed = {}
    sub = validation["central_plus_100_bootstrap_plus_187_universes"]["subtotal_node_h"]
    for f in (0.5, 0.8, 0.95):
        for s in (2, 5, 10, 100):
            amdahl = 1.0 / ((1 - f) + f / s)
            speed[f"f{f}_s{s}"] = {"amdahl": amdahl, "admitted_node_h": sub / amdahl / 0.8}
    out["speedup_sensitivity_full_recipe"] = speed
    return out


def diagnostic_cost() -> dict[str, Any]:
    """Price of the proposed exact-response comparator (no GBDT fit; linear algebra only)."""
    rows = 20_402_110  # s5e geometry receipt rows_eligible for input npz 07fccc1a...
    columns = 5 + 5 + 4  # truth axes, reco axes, pass flags/weight/split key
    extract_bytes = rows * columns * 4
    return {
        "event_rows": rows,
        "columns_float32": columns,
        "column_extract_bytes": extract_bytes,
        "column_extract_GiB": extract_bytes / 2**30,
        "binning_passes": "one pass per truth resolution (3) x weight set (nominal + 5 departures)",
        "dense_fisher_7776_bytes": 7776**2 * 8,
        "planning_cpu_core_hours": [1.0, 4.0],
        "reserve_rule": "admitted = subtotal / 0.8",
        "admitted_cpu_core_hours_upper": 4.0 / 0.8,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    with np.load(OPERANDS, allow_pickle=False) as z:
        z = {k: z[k] for k in z.files}
        result = {
            "schema": "gbdt-successor-saved-reductions/1",
            "integrity": integrity(z),
            "receipt_crosscheck": receipt_crosscheck(z),
            "headline_reproduction": headline(z),
            "bias_variance_K5": bias_variance(z),
            "noise_free_vs_ensemble_K5": asimov_vs_ensemble(z),
            "convergence": convergence(z),
            "prior_pull": prior_pull(z),
            "model_allowance": model_allowance(z),
            "visibility": visibility(z),
            "fold_misfit_series": fold_misfit_series(),
            "design": design({"pseudo_f32_K5_s": 293.973}),
            "diagnostic_cost": diagnostic_cost(),
        }
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
