#!/usr/bin/env python3
"""s5p Stage 5: the frozen validation evaluator (targets T1, T4, T5 of contract amendment 1).

Inputs are frozen by the Stage-3 admission record, which names them in a JSON design file:

* ``assembly``: the frozen s5p_assemble product of the selected configuration and reporting definition on the
  real data (functional matrix U, names, f, and the blocks); the NON-statistical probabilistic width
  ``sigma_ns = sqrt(diag(C_prob - C_stat))`` and the bounded component ``h`` are used RELATIVE to f;
* ``sigma_stat_rel``: the frozen relative statistical width of a pseudo-experiment (the design names its
  source, e.g. the mean of per-experiment bootstrap widths), because pseudo-experiments are not bootstrapped
  individually; the conditioning is stated in the receipt;
* ``points``: validation truth points, each a glob of fresh experiment products (``xsec_flat``, ``xtrue_flat``)
  and a declared count (an absent experiment makes the verdict INCOMPLETE, never a smaller n);
* ``alpha_family``: the familywise level of the simultaneous bounds (Bonferroni over functionals x points).

For experiment e, functional f: half-width68 = f_hat * (sqrt(s_stat^2 + s_ns^2) + h_rel), half-width95 =
f_hat * (1.96 sqrt(s_stat^2 + s_ns^2) + h_rel); hit if |f_hat - f_true| <= half-width. T4: every (f, point)
one-sided Clopper-Pearson lower bound at alpha_family / (F G) >= 0.60 (68%) and >= 0.90 (95%). T5 (at the
points marked ``statistical_check``): pulls (f_hat - f_true) / (f_hat s_stat); per functional, the pull SD's
chi-square interval at alpha_family / F must intersect [0.80, 1.25] and its point estimate must lie in it, and
the mean pull's 99.9% band (Bonferroni over F) must contain 0. T1 on the data: median over reported cells of
half-width68 / f <= 10%, 90th percentile <= 25%. A pooled pass certifies nothing per functional.

MEASURES: the frozen criteria on the declared validation population. CANNOT AUTHORIZE: coverage outside the
declared points and nuisance treatment, or any criterion change.
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np
from scipy import stats

THRESH = {"68": 0.60, "95": 0.90}
T5_BAND = (0.80, 1.25)


def cp_lower(k: int, n: int, a: float) -> float:
    return 0.0 if k == 0 else float(stats.beta.ppf(a, k, n - k + 1))


def evaluate(design: dict) -> dict:
    z = np.load(design["assembly"], allow_pickle=False)
    meta = json.loads(str(z["meta"]))
    names = meta["functional_names"]
    U = np.asarray(z["U"], float)
    f = np.asarray(z["f"], float)
    C_ns = np.asarray(z["C_prob"], float) - np.asarray(z["C_stat"], float)
    s_ns = np.sqrt(np.clip(np.diag(C_ns), 0, None)) / f
    h_rel = np.asarray(z["h"], float) / f
    s_stat = np.asarray(design["sigma_stat_rel"], float)
    if s_stat.size != f.size:
        raise SystemExit("sigma_stat_rel does not match the assembly's functionals")
    F = f.size
    points = design["points"]
    G = len(points)
    a_cell = design["alpha_family"] / (F * G)
    out = {"schema": "s5p-validation/1", "design": design, "functional_names": names, "F": F, "G": G,
           "per_comparison_alpha": a_cell, "points": [], "complete": True}
    width = s_ns ** 2
    for pt in points:
        files = sorted(glob.glob(pt["glob"]))
        n = len(files)
        entry = {"name": pt["name"], "n_declared": pt["n"], "n_present": n}
        if n != pt["n"]:
            out["complete"] = False
            entry["missing"] = pt["n"] - n
            out["points"].append(entry)
            continue
        fh = np.array([U @ np.load(p, allow_pickle=False)["xsec_flat"] for p in files])
        ft = np.array([U @ np.load(p, allow_pickle=False)["xtrue_flat"] for p in files])
        prob = np.sqrt(s_stat ** 2 + width)
        hw68 = fh * (prob + h_rel)
        hw95 = fh * (1.96 * prob + h_rel)
        d = np.abs(fh - ft)
        k68, k95 = (d <= hw68).sum(0), (d <= hw95).sum(0)
        lcb68 = np.array([cp_lower(int(k), n, a_cell) for k in k68])
        lcb95 = np.array([cp_lower(int(k), n, a_cell) for k in k95])
        entry.update({"hits68": k68.tolist(), "hits95": k95.tolist(), "lcb68": lcb68.tolist(), "lcb95": lcb95.tolist(),
                      "min_lcb68": float(lcb68.min()), "argmin68": names[int(lcb68.argmin())],
                      "min_lcb95": float(lcb95.min()), "argmin95": names[int(lcb95.argmin())],
                      "T4_pass": bool(lcb68.min() >= THRESH["68"] and lcb95.min() >= THRESH["95"]),
                      "median_relative_error": float(np.median(np.abs(fh / ft - 1))),
                      "median_halfwidth68_rel": float(np.median(hw68 / fh))})
        if pt.get("statistical_check"):
            pulls = (fh - ft) / (fh * s_stat)
            sd = pulls.std(0, ddof=1)
            a_f = design["alpha_family"] / F
            lo = sd * np.sqrt((n - 1) / stats.chi2.ppf(1 - a_f / 2, n - 1))
            hi = sd * np.sqrt((n - 1) / stats.chi2.ppf(a_f / 2, n - 1))
            mp = pulls.mean(0)
            zc = stats.norm.ppf(1 - 0.001 / (2 * F))
            ok_sd = (sd >= T5_BAND[0]) & (sd <= T5_BAND[1]) & (hi >= T5_BAND[0]) & (lo <= T5_BAND[1])
            ok_mean = np.abs(mp) <= zc * sd / np.sqrt(n)
            entry["T5"] = {"pull_sd": sd.tolist(), "pull_sd_interval": [lo.tolist(), hi.tolist()], "mean_pull": mp.tolist(),
                           "failing": [names[i] for i in np.flatnonzero(~(ok_sd & ok_mean))],
                           "pass": bool(np.all(ok_sd & ok_mean))}
        out["points"].append(entry)
    hw68_data = f * (np.sqrt(np.asarray(design.get("sigma_stat_data_rel", s_stat)) ** 2 + width) + h_rel)
    cells = [i for i, nm in enumerate(names) if nm != "total"]
    rel = hw68_data[cells] / f[cells]
    out["T1"] = {"median_halfwidth68_rel": float(np.median(rel)), "p90_halfwidth68_rel": float(np.percentile(rel, 90)),
                 "pass": bool(np.median(rel) <= 0.10 and np.percentile(rel, 90) <= 0.25)}
    if not out["complete"]:
        out["verdict"] = "INCOMPLETE"
    else:
        t4 = all(p["T4_pass"] for p in out["points"])
        t5 = all(p["T5"]["pass"] for p in out["points"] if "T5" in p)
        out["verdict"] = "PASS" if (t4 and t5 and out["T1"]["pass"]) else "FAIL"
        out["failed"] = [x for x, ok in (("T4", t4), ("T5", t5), ("T1", out["T1"]["pass"])) if not ok]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--design", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    res = evaluate(json.loads(a.design.read_text()))
    a.out.write_text(json.dumps(res) + "\n")
    print(json.dumps({"verdict": res["verdict"], "failed": res.get("failed"), "T1": res["T1"],
                      "points": [{k: p.get(k) for k in ("name", "n_present", "min_lcb68", "argmin68", "min_lcb95", "argmin95", "T4_pass")}
                                 for p in res["points"]]}, indent=1))
    return {"PASS": 0, "FAIL": 1, "INCOMPLETE": 4}[res["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
