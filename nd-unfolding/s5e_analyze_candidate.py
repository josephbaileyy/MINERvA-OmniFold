#!/usr/bin/env python3
"""s5e candidate receipt: development checks K1-K5 and assessment criteria A1-A5 of contract
amendment 3, evaluated mechanically from the committed-table products.

Residuals are relative, (f_hat - f_true)/f_true, over the 153 s5c reported functionals; pulls use the
candidate's declared sigma (the K5 bootstrap of one development experiment). The criteria and their
thresholds are read from the amendment file itself, so this script cannot drift from what was frozen.

MEASURES: the candidate's development and assessment statistics. CANNOT AUTHORIZE: adoption, a coverage
validation (development scale), or a corrected central value.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
from pathlib import Path

import numpy as np

import s5c_assemble
import s5c_coverage as sc

N_EW = 42


def load_fn(path, U):
    z = np.load(path, allow_pickle=False)
    out = {"f": U @ np.asarray(z["xsec_flat"], float), "meta": json.loads(str(z["meta"]))}
    if "xtrue_flat" in z.files:
        out["t"] = U @ np.asarray(z["xtrue_flat"], float)
    return out


def sigma_from(boot_dir: Path, U, first: int, last: int) -> tuple[np.ndarray, np.ndarray]:
    reps = np.array([load_fn(boot_dir / f"boot_b{b}.npz", U)["f"] for b in range(first, last + 1)])
    return reps.std(0, ddof=1), reps


def point(files, U, sig) -> dict:
    P = [load_fn(f, U) for f in files]
    rel = np.array([(p["f"] - p["t"]) / p["t"] for p in P])
    pull = np.array([(p["f"] - p["t"]) / sig for p in P])
    n = len(P)
    m, se = rel.mean(0), rel.std(0, ddof=1) / math.sqrt(n)
    t = m / se
    mp, sd = pull.mean(0), pull.std(0, ddof=1)
    ew = np.abs(m[:N_EW])
    return {"n": n, "mean_rel": m, "se_rel": se, "t": t, "mean_pull": mp, "pull_sd": sd, "pull": pull, "rel": rel,
            "summary": {"n": n, "max_abs_t": float(np.max(np.abs(t))), "n_abs_t_gt_3.6": int(np.sum(np.abs(t) > 3.6)),
                        "ew_median_abs_pct": 100 * float(np.median(ew)), "ew_max_abs_pct": 100 * float(ew.max()),
                        "ew_argmax": f"EW{int(ew.argmax())}", "all_max_abs_pct": 100 * float(np.max(np.abs(m))),
                        "pooled_cov68": float(np.mean(np.abs(pull) <= 1.0)), "pooled_cov95": float(np.mean(np.abs(pull) <= 1.96)),
                        "pooled_pull_sd": float(pull.std(ddof=1)), "pull_sd_median": float(np.median(sd)),
                        "pull_sd_min": float(sd.min()), "pull_sd_max": float(sd.max())},
            "per_functional": {"mean_rel": m.tolist(), "se_rel": se.tolist(), "rel_sd": rel.std(0, ddof=1).tolist(),
                               "mean_pull": mp.tolist(), "pull_sd": sd.tolist(),
                               "cov68": np.mean(np.abs(pull) <= 1.0, 0).tolist(), "cov95": np.mean(np.abs(pull) <= 1.96, 0).tolist()}}


def c3(pt: dict, crit: dict) -> dict:
    bad_t = np.abs(pt["t"]) > crit["t_crit"]
    bad_p = (np.abs(pt["mean_pull"]) > crit["mean_pull_max"]) & (np.abs(pt["t"]) > crit["t_with_pull"])
    return {"n_abs_t_gt_crit": int(bad_t.sum()), "n_pull_and_t": int(bad_p.sum()), "pass": bool(not bad_t.any() and not bad_p.any())}


def calibration(pt: dict, reps: np.ndarray, crit: dict) -> dict:
    n = pt["n"]
    se_sd = 1.0 / math.sqrt(2 * (n - 1))
    sd = pt["pull_sd"]
    outside = np.mean((sd < 1 - 3 * se_sd) | (sd > 1 + 3 * se_sd))
    pooled = pt["summary"]["pooled_pull_sd"]
    # correlated check on the 42 EW cells: Mahalanobis with the replica covariance, Hartlap-corrected
    nr, p = reps.shape[0], N_EW
    C = np.cov(reps[:, :N_EW], rowvar=False, ddof=1)
    Ci = np.linalg.inv(C) * (nr - p - 2) / (nr - 1)
    sig = reps.std(0, ddof=1)
    resid = pt["pull"][:, :N_EW] * sig[:N_EW]
    maha = np.einsum("ij,jk,ik->i", resid, Ci, resid)
    lo, hi = crit["mahalanobis_mean_window_times_p"]
    out = {"pooled_pull_sd": pooled, "fraction_pull_sd_outside_3se": float(outside), "se_pull_sd": se_sd,
           "mahalanobis_mean": float(maha.mean()), "mahalanobis_window": [lo * p, hi * p], "hartlap": (nr - p - 2) / (nr - 1)}
    out["pass"] = bool(crit["pooled_pull_sd_window"][0] <= pooled <= crit["pooled_pull_sd_window"][1]
                       and outside <= crit["max_fraction_outside_3se"] and lo * p <= maha.mean() <= hi * p)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--amendment", type=Path, required=True)
    ap.add_argument("--s5c-contract", type=Path, required=True)
    ap.add_argument("--adopted-sigma", type=Path, required=True, help="state/s5c/d1/bias_vs_adopted.json (sigma_adopted_pct per EW cell)")
    ap.add_argument("--ns", type=Path, required=True, help="the s5e namespace")
    ap.add_argument("--s5n-runs", type=Path, required=True)
    ap.add_argument("--stage", choices=("development", "assessment"), required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    am = json.loads(a.amendment.read_text())
    crit = am["criteria"]
    U, names = sc.reported_functionals(json.loads(a.s5c_contract.read_text()))
    runs = a.ns / "runs" / "cand"
    sig, reps = sigma_from(runs / "dev" / "sigma", U, *am["development"]["K5"]["bootstrap_seeds"])
    rec = {"schema": "s5e-candidate/1", "candidate": am["candidate"]["name"], "stage": a.stage,
           "sigma_replicas": int(reps.shape[0]), "functional_names": names}
    rec["sigma_rel_pct"] = (100 * sig / np.abs(reps.mean(0))).tolist()
    s5n_b0 = {"eavail": sorted(glob.glob(str(a.s5n_runs / "dev" / "eavail_shape_a1_s*.npz"))),
              "q3": sorted(glob.glob(str(a.s5n_runs / "dev" / "q3_given_eavail_w_a0.3_s*.npz")))}
    b0 = {k: point(v, U, sig)["summary"] for k, v in s5n_b0.items()}
    rec["B0_reference_s5n"] = b0
    if a.stage == "development":
        d = runs / "dev"
        K1 = point(sorted(glob.glob(str(d / "k1_R" / "nominal_a0_s*.npz"))), U, sig)
        K1b = point(sorted(glob.glob(str(d / "k1_B0" / "nominal_a0_s*.npz"))), U, sig)
        paired = np.array([(r - b) for r, b in zip(K1["rel"], K1b["rel"])])
        pm, pse = paired.mean(0), paired.std(0, ddof=1) / math.sqrt(paired.shape[0])
        K2 = point(sorted(glob.glob(str(d / "k2" / "eavail_shape_a1_s*.npz"))), U, sig)
        K3 = point(sorted(glob.glob(str(d / "k3" / "q3_given_eavail_w_a0.3_s*.npz"))), U, sig)
        tol = crit["departure_not_worse_relative"]
        k23 = {}
        for name, pt, ref in (("K2", K2, b0["eavail"]), ("K3", K3, b0["q3"])):
            s = pt["summary"]
            k23[name] = {"candidate": s, "b0_median": ref["ew_median_abs_pct"], "b0_max": ref["ew_max_abs_pct"],
                         "pass_not_worse": bool(s["ew_median_abs_pct"] <= (1 + tol) * ref["ew_median_abs_pct"]
                                                and s["ew_max_abs_pct"] <= (1 + tol) * ref["ew_max_abs_pct"])}
        base = load_fn(d / "k4" / "k4_base.npz", U)["f"]
        k4 = {}
        for nm in ("k4_seed43", "k4_perm1", "k4_perm2"):
            f = load_fn(d / "k4" / f"{nm}.npz", U)["f"]
            k4[nm] = {"max_abs_over_sigma": float(np.max(np.abs(f - base) / sig)), "bitwise_equal": bool(np.array_equal(f, base))}
        rec["K1"] = {"R": K1["summary"], "R_per_functional": K1["per_functional"], "criterion": c3(K1, crit["C3"]), "B0_same_seeds": K1b["summary"], "B0_criterion": c3(K1b, crit["C3"]),
                     "paired_R_minus_B0": {"max_abs_t": float(np.max(np.abs(pm / pse))), "max_abs_mean_pct": 100 * float(np.max(np.abs(pm)))}}
        rec["K2_K3"] = k23
        rec["K2_K3_per_functional_mean_rel"] = {"K2": K2["per_functional"]["mean_rel"], "K3": K3["per_functional"]["mean_rel"]}
        rec["K4"] = {"probes": k4, "pass": bool(all(v["max_abs_over_sigma"] <= crit["seed_movement_max_sigma"] for v in k4.values()))}
        rec["K5"] = {"calibration_on_K1": calibration(K1, reps, crit["calibration"])}
        rec["development_exit"] = bool(rec["K1"]["criterion"]["pass"] and k23["K2"]["pass_not_worse"] and k23["K3"]["pass_not_worse"])
    else:
        A = runs / "assess"
        pts = {k: point(sorted(glob.glob(str(A / k / "*.npz"))), U, sig) for k in am["assessment"]["points"]}
        rec["points"] = {k: {**v["summary"], "per_functional": v["per_functional"]} for k, v in pts.items()}
        rec["A1"] = c3(pts["nominal"], crit["C3"])
        rec["A2"] = calibration(pts["nominal"], reps, crit["calibration"])
        base = load_fn(A / "a3" / "a3_base.npz", U)["f"]
        a3 = {nm: float(np.max(np.abs(load_fn(A / "a3" / f"{nm}.npz", U)["f"] - base) / sig)) for nm in ("a3_seed43", "a3_perm1", "a3_perm2")}
        data = load_fn(A / "data" / "data_R.npz", U)["f"]
        dsig = np.array([load_fn(f, U)["f"] for f in sorted(glob.glob(str(A / "data" / "boot" / "boot_b*.npz")))]).std(0, ddof=1)
        up = load_fn(A / "data" / "data_R_upcast.npz", U)["f"]  # float64 handling, same values: the probe's baseline
        rec["data_upcast_equals_data_R"] = bool(np.array_equal(up, data))
        jit = [np.abs(load_fn(f, U)["f"] - up) / dsig for f in sorted(glob.glob(str(A / "data" / "data_R_jitteredge*.npz")))]
        jmax = np.max(np.array(jit), axis=0)
        rec["A3"] = {"seed_and_permutation_max_over_sigma": a3,
                     "data_rounding_probe_over_data_sigma": {"median": float(np.median(jmax)), "max": float(jmax.max()),
                                                             "argmax": names[int(jmax.argmax())]}}
        rec["A3"]["pass"] = bool(max(a3.values()) <= crit["seed_movement_max_sigma"]
                                 and np.median(jmax) <= crit["rounding_median_max_sigma"] and jmax.max() <= crit["rounding_max_sigma"])
        adopted = np.array([c["sigma_adopted_pct"] for c in json.loads(a.adopted_sigma.read_text())["cells"]]) / 100
        md = np.max(np.abs(np.array([pts[w]["mean_rel"][:N_EW] for w in am["assessment"]["withheld"]])), axis=0)
        useful = md <= adopted
        rec["A4"] = {"model_dependence_by_EW_pct": (100 * md).round(3).tolist(), "adopted_total_sigma_pct": (100 * adopted).round(3).tolist(),
                     "cells_model_dependence_within_adopted_sigma": [f"EW{i}" for i in np.flatnonzero(useful)],
                     "n_useful_cells": int(useful.sum()), "pass_nonempty_scope": bool(useful.any())}
        b0sig = sc.stat_covariance(U, a.s5n_runs / "sigma", 1, 200)
        b0s = np.sqrt(np.diag(b0sig))
        ratio = sig[:N_EW] / b0s[:N_EW]
        rec["A5"] = {"sigma_R_over_sigma_B0_EW_median": float(np.median(ratio)), "max": float(ratio.max()),
                     "pass": bool(np.median(ratio) <= crit["useful_width"]["median_ratio_max"] and ratio.max() <= crit["useful_width"]["max_ratio_max"])}
        dB0 = U @ s5c_assemble.read_flat(str(a.ns / "runs" / "diag" / "drv" / "data_b0.npz"))
        rec["data"] = {"method_sensitivity_R_minus_B0_pct": {"median_abs": 100 * float(np.median(np.abs(data / dB0 - 1))),
                                                            "max_abs": 100 * float(np.max(np.abs(data / dB0 - 1))),
                                                            "argmax": names[int(np.argmax(np.abs(data / dB0 - 1)))]},
                       "data_sigma_over_pseudo_sigma_EW_median": float(np.median(dsig[:N_EW] / sig[:N_EW])),
                       "data_sigma_rel_pct_EW_median": 100 * float(np.median(dsig[:N_EW] / np.abs(data[:N_EW]))),
                       "data_boot_replicas": int(len(glob.glob(str(A / "data" / "boot" / "boot_b*.npz"))))}
        rec["verdict"] = ("A_PASS_DEVELOPMENT_SCALE" if all(rec[k]["pass"] for k in ("A1", "A2", "A3", "A5")) and rec["A4"]["pass_nonempty_scope"]
                          else "A_FAIL")
    a.out.write_text(json.dumps(rec, indent=1, default=float) + "\n")
    brief = {k: rec[k] for k in ("K1", "K4", "development_exit", "A1", "A2", "A3", "A5", "verdict") if k in rec}
    print(json.dumps(brief, default=float)[:4000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
