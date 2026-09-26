#!/usr/bin/env python3
"""The s5e diagnosis receipt: items D0-D7 of ``docs/orchestration/state/s5e/contract.json`` (and
amendment 1) from the committed-table products, with the contract's interpretation rules evaluated
mechanically.

Residuals are relative, (f_hat - f_true)/f_true, over the 153 s5c reported functionals; the decisive
departure metric is the median and the maximum of |residual| over the 42 (E_avail,W) cells. Forward-fold
agreement is a chi2 of reco-level histograms: on pseudo-experiments with the measured side's own
variance (sum of squared weights), on the noise-free construction with the analysis-exposure Poisson
variance F_true (the folded truth model); cells with variance <= 0 are skipped.

MEASURES: the diagnosis quantities. CANNOT AUTHORIZE: a cause beyond the contract's attribution rule, a
candidate (a later amendment), or any coverage statement.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

import s5c_assemble
import s5c_coverage as sc

N_EW = 42
TRUTHS = {"nominal": ("nominal", 0.0, 300000), "eavail": ("eavail_shape", 1.0, 301000),
          "q3": ("q3_given_eavail_w", 0.3, 302000)}


def load(path: Path) -> dict:
    z = np.load(path, allow_pickle=False)
    out = {k: np.asarray(z[k]) for k in z.files if k != "meta"}
    out["meta"] = json.loads(str(z["meta"]))
    return out


def rel(fh, ft):
    return (np.asarray(fh, float) - ft) / ft


def ew_stats(r) -> dict:
    a = np.abs(np.asarray(r)[:N_EW])
    return {"median_abs_pct": 100 * float(np.median(a)), "max_abs_pct": 100 * float(a.max()),
            "argmax": f"EW{int(a.argmax())}"}


def chi2(a, b, var) -> tuple[float, int]:
    a, b, var = (np.asarray(x, float) for x in (a, b, var))
    ok = var > 0
    return float(np.sum((a[ok] - b[ok]) ** 2 / var[ok])), int(ok.sum())


def ew_var(p5, shape) -> np.ndarray:
    return np.asarray(p5).reshape(shape).sum(axis=(0, 1, 3)).ravel()


def d0(runs: Path, s5n: Path, U) -> dict:
    """Iteration-5 traced unfolds against the s5n products they re-derive (bitwise)."""
    out = {"pairs": [], "n_equal": 0, "n_compared": 0}

    def cmp(name, prod, ref, key="xsec_it5_flat"):
        if not ref.exists():
            out["pairs"].append({"name": name, "reference": str(ref), "status": "reference missing"})
            return
        p, r = np.load(prod), np.load(ref)
        xs, xr = p[key], r["xsec_flat"]
        eq = bool(np.array_equal(xs, xr))
        teq = bool(np.array_equal(p["xtrue_flat"], r["xtrue_flat"])) if "xtrue_flat" in r.files else None
        out["pairs"].append({"name": name, "xsec_equal": eq, "xtrue_equal": teq,
                             "max_rel_fn_diff": float(np.max(np.abs(rel(U @ xs, U @ xr))))})
        out["n_compared"] += 1
        out["n_equal"] += int(eq and teq is not False)

    for t, (tn, a, base) in TRUTHS.items():
        for i in range(4):
            s = base + i
            cmp(f"trace_{t}_bkg_s{s}", runs / "trace" / f"trace_{t}_bkg_s{s}.npz", s5n / "dev" / f"{tn}_a{a:g}_s{s}.npz")
    for t in ("eavail", "q3"):
        tn, a, base = TRUTHS[t]
        for i in range(4):
            s = base + i
            cmp(f"trace_{t}_sig_s{s}", runs / "trace" / f"trace_{t}_sig_s{s}.npz",
                s5n / "diag" / f"diag_sigonly_{tn}_a{a:g}_s{s}.npz")
    for s in range(300004, 300012):
        cmp(f"bkg_b0_s{s}", runs / "bkg" / f"bkg_b0_s{s}.npz", s5n / "dev" / f"nominal_a0_s{s}.npz", key="xsec_flat")
    p, r = np.load(runs / "drv" / "data_b0.npz"), np.load(s5n / "c7" / "data_negweight.npz")
    out["data_b0_vs_s5n_c7_npz_equal"] = bool(np.array_equal(p["xsec_flat"], r["xsec_flat"]))
    out["data_b0_vs_s5n_c7_max_rel_fn_diff"] = float(np.max(np.abs(rel(U @ p["xsec_flat"], U @ r["xsec_flat"]))))
    return out


def d1_d2(runs: Path, s5n: Path, U, names) -> dict:
    res = {"D1": {}, "D2": {}}
    for t in TRUTHS:
        drv = load(runs / "drv" / f"driver_{t}.npz")
        asi = load(runs / "asimov" / f"asimov_b0_{t}.npz")
        rd = rel(drv["fn_unf"], drv["fn_true"])
        ra = rel(asi["fn_push"][4], asi["fn_true"])
        res["D1"][t] = {"driver_residual": ew_stats(rd), "npz_residual_k5": ew_stats(ra),
                        "driver_minus_npz_residual_pp": {
                            "median_abs": 100 * float(np.median(np.abs(rd - ra))),
                            "max_abs": 100 * float(np.max(np.abs(rd - ra))),
                            "argmax": names[int(np.argmax(np.abs(rd - ra)))]},
                        "residual_correlation_EW": float(np.corrcoef(rd[:N_EW], ra[:N_EW])[0, 1]),
                        "truth_rel_diff_max": float(np.max(np.abs(rel(drv["fn_true"], asi["fn_true"])))),
                        "driver_r": drv["meta"]["r"], "input_parity": drv["meta"]["input_parity"],
                        "problems": drv["meta"]["problems"]}
    base = load(runs / "asimov" / "asimov_b0_eavail.npz")
    b5 = U @ base["xsec_it5_flat"]
    for name in ("asimov_eavail_upcast", "asimov_eavail_jitter1", "asimov_eavail_seedper"):
        p = load(runs / "asimov" / f"{name}.npz")
        f = U @ p["xsec_flat"]
        res["D2"][name] = {"xsec_equal_to_b0_k5": bool(np.array_equal(p["xsec_flat"], base["xsec_it5_flat"])),
                           "max_rel_fn_diff_pct": 100 * float(np.max(np.abs(rel(f, b5)))),
                           "median_rel_fn_diff_pct": 100 * float(np.median(np.abs(rel(f, b5)))),
                           "residual_EW_k5": ew_stats(rel(f, base["fn_true"]))}
    d = load(runs / "drv" / "data_b0.npz")
    fd = U @ d["xsec_flat"]
    for name in ("data_seedper", "data_upcast", "data_jitter1"):
        p = load(runs / "drv" / f"{name}.npz")
        f = U @ p["xsec_flat"]
        res["D2"][name] = {"xsec_equal_to_data_b0": bool(np.array_equal(p["xsec_flat"], d["xsec_flat"])),
                           "max_rel_fn_diff_pct": 100 * float(np.max(np.abs(rel(f, fd)))),
                           "median_rel_fn_diff_pct": 100 * float(np.median(np.abs(rel(f, fd)))),
                           "argmax": names[int(np.argmax(np.abs(rel(f, fd))))]}
    try:
        drv = U @ s5c_assemble.read_flat(str(s5n / "c7" / "xsec_5d_driver_negweight_F2.root"))
        dd = rel(drv, fd)
        res["D2"]["driver_c7_vs_npz_data_b0"] = {"max_rel_fn_diff_pct": 100 * float(np.max(np.abs(dd))),
                                                "median_rel_fn_diff_pct": 100 * float(np.median(np.abs(dd))),
                                                "argmax": names[int(np.argmax(np.abs(dd)))]}
        for name in ("data_seedper", "data_upcast", "data_jitter1"):
            f = U @ load(runs / "drv" / f"{name}.npz")["xsec_flat"]
            res["D2"]["driver_c7_vs_" + name] = {"max_rel_fn_diff_pct": 100 * float(np.max(np.abs(rel(drv, f)))),
                                                 "median_rel_fn_diff_pct": 100 * float(np.median(np.abs(rel(drv, f))))}
    except Exception as exc:  # noqa: BLE001 - ROOT absent: record, do not guess
        res["D2"]["driver_c7_vs_npz_data_b0"] = {"error": repr(exc)}
    ev = json.loads((s5n / "c7" / "ev_driver_negweight.json").read_text())
    ref = [c.get("evidence") for c in ev["calls"] if c.get("site", "").endswith("refine_stay_positive")]
    res["D2"]["refinement_driver_c7"] = ref[0] if ref else None
    res["D2"]["refinement_npz_data_b0"] = d["meta"]["refinement"]
    return res


def trace_point(files: list[Path], shape) -> dict:
    """Seed-averaged per-iteration diagnostics for one truth point and background setting."""
    P = [load(f) for f in files]
    K = P[0]["fn_push"].shape[0]
    res_push = np.array([[rel(p["fn_push"][k], p["fn_true"]) for k in range(K)] for p in P])  # seeds x K x 153
    res_pull = np.array([[rel(p["fn_pull"][k], p["fn_true"]) for k in range(K)] for p in P])
    resA = np.array([[rel(p["fn_push"][k], p["fn_true_A"]) for k in range(K)] for p in P])
    m_push, m_pull, m_A = res_push.mean(0), res_pull.mean(0), resA.mean(0)
    out = {"n_seeds": len(P), "K": K, "per_k": []}
    for k in range(K):
        row = {"k": k + 1, "push_vs_true": ew_stats(m_push[k]), "pull_vs_true": ew_stats(m_pull[k]),
               "push_vs_A_truth": ew_stats(m_A[k])}
        c_push = [chi2(p["reco_ew_D"], p["reco_ew_push"][k], ew_var(p["reco5d_Dvar"], shape)) for p in P]
        c_pull = [chi2(p["reco_ew_D"], p["reco_ew_pull"][k], ew_var(p["reco5d_Dvar"], shape)) for p in P]
        c_true = [chi2(p["reco_ew_D"], p["reco_ew_true"], ew_var(p["reco5d_Dvar"], shape)) for p in P]
        row["ew_chi2_mean"] = {"D_vs_push": float(np.mean([c[0] for c in c_push])),
                               "D_vs_pull": float(np.mean([c[0] for c in c_pull])),
                               "D_vs_true": float(np.mean([c[0] for c in c_true])), "ncell": c_push[0][1]}
        if f"reco5d_push_it{k + 1}" in P[0]:
            c5 = [chi2(p["reco5d_D"], p[f"reco5d_push_it{k + 1}"], p["reco5d_Dvar"]) for p in P]
            t5 = [chi2(p["reco5d_D"], p["reco5d_true"], p["reco5d_Dvar"]) for p in P]
            u5 = [chi2(p[f"reco5d_push_it{k + 1}"], p["reco5d_true"], p["reco5d_Dvar"]) for p in P]
            row["reco5d_chi2_mean"] = {"D_vs_push": float(np.mean([c[0] for c in c5])),
                                       "D_vs_true": float(np.mean([c[0] for c in t5])),
                                       "push_vs_true": float(np.mean([c[0] for c in u5])), "ncell": c5[0][1]}
        # step-2 response: truth-cell sums of w_push against w_pull (pass + fail)
        s2 = np.mean([(p["truth_ew_pass_wpush"][k] + p["truth_ew_fail_wpush"][k]) /
                      np.maximum(p["truth_ew_pass_wpull"][k] + p["truth_ew_fail_wpull"][k], 1e-300) - 1 for p in P], 0)
        row["step2_push_over_pull_minus1_pct"] = {"median_abs": 100 * float(np.median(np.abs(s2))),
                                                  "max_abs": 100 * float(np.max(np.abs(s2)))}
        out["per_k"].append(row)
    # missed-event regression at k = 1 and k = 5: per truth (E_avail,W) cell
    for k in (1, 5):
        if k > K:
            continue
        q = {}
        for key in ("pass", "fail"):
            q[f"mean_new_w_{key}"] = np.mean([p[f"truth_ew_{key}_wnew"][k - 1] / np.maximum(p[f"truth_ew_{key}_w"][k - 1], 1e-300) for p in P], 0)
            q[f"mean_r_{key}"] = np.mean([p[f"truth_ew_{key}_wr"][k - 1] / np.maximum(p[f"truth_ew_{key}_w"][k - 1], 1e-300) for p in P], 0)
        eff = np.mean([p["truth_ew_pass_w"][0] / np.maximum(p["truth_ew_pass_w"][0] + p["truth_ew_fail_w"][0], 1e-300) for p in P], 0)
        gap_w = q["mean_new_w_fail"] - q["mean_new_w_pass"]
        gap_r = q["mean_r_fail"] - q["mean_r_pass"]
        out[f"missed_event_k{k}"] = {
            "efficiency_by_EW": eff.tolist(),
            "fill_minus_pass_new_w": gap_w.tolist(), "truth_r_fail_minus_pass": gap_r.tolist(),
            "median_abs_fill_minus_pass_pct": 100 * float(np.median(np.abs(gap_w))),
            "median_abs_r_fail_minus_pass_pct": 100 * float(np.median(np.abs(gap_r))),
            "mean_new_w_pass": q["mean_new_w_pass"].tolist(), "mean_new_w_fail": q["mean_new_w_fail"].tolist(),
            "mean_r_pass": q["mean_r_pass"].tolist(), "mean_r_fail": q["mean_r_fail"].tolist()}
    out["mean_residual_EW_by_k"] = {k + 1: (100 * m_push[k][:N_EW]).round(3).tolist() for k in (0, 4, 9, 19) if k < K}
    return out


def asimov_series(p: dict, shape, nominal_true5d=None) -> dict:
    K = p["fn_push"].shape[0]
    var5 = p["reco5d_true"]
    varew = ew_var(var5, shape)
    prior_chi_ew = chi2(p["reco_ew_prior"], p["reco_ew_true"], varew)[0]
    prior_chi_5d = chi2(p["reco5d_prior"], p["reco5d_true"], var5)[0]
    rows = []
    for k in range(K):
        r = rel(p["fn_push"][k], p["fn_true"])
        rp = rel(p["fn_pull"][k], p["fn_true"])
        row = {"k": k + 1, "push": ew_stats(r), "pull": ew_stats(rp)}
        c = chi2(p["reco_ew_push"][k], p["reco_ew_true"], varew)[0]
        row["ew_chi2_push_vs_true"] = c
        row["ew_explained_fraction"] = 1.0 - c / prior_chi_ew if prior_chi_ew > 0 else None
        if f"reco5d_push_it{k + 1}" in p:
            c5 = chi2(p[f"reco5d_push_it{k + 1}"], p["reco5d_true"], var5)[0]
            row["reco5d_chi2_push_vs_true"] = c5
            row["reco5d_explained_fraction"] = 1.0 - c5 / prior_chi_5d if prior_chi_5d > 0 else None
        rows.append(row)
    return {"K": K, "S_dep_ew": prior_chi_ew, "S_dep_reco5d": prior_chi_5d,
            "ncell_reco5d": int((var5 > 0).sum()), "per_k": rows,
            "residual_EW_pct_by_k": {k + 1: (100 * rel(p["fn_push"][k], p["fn_true"])[:N_EW]).round(3).tolist()
                                     for k in (0, 4, 9, 14, 19, 29) if k < K},
            "mean_fill_fail": p["mean_fill_fail"].tolist()}


def d3_to_d6(runs: Path, shape) -> dict:
    res = {"D3": {}, "D4": {}, "D5": {}}
    for t, (tn, a, base) in TRUTHS.items():
        for bk in ("bkg", "sig"):
            files = [runs / "trace" / f"trace_{t}_{bk}_s{base + i}.npz" for i in range(4)]
            res["D3"][f"{t}_{bk}"] = trace_point(files, shape)
    for t in TRUTHS:
        res["D4"][t] = asimov_series(load(runs / "asimov" / f"asimov_b0_{t}.npz"), shape)
    for t in ("eavail", "q3"):
        res["D5"][f"capacity_{t}"] = asimov_series(load(runs / "asimov" / f"asimov_cap_{t}.npz"), shape)
        res["D5"][f"missed_unity_{t}"] = asimov_series(load(runs / "asimov" / f"asimov_unity_{t}.npz"), shape)
    return res


def rules(r: dict) -> dict:
    """The contract's predeclared interpretation rules, per departure (numbers beside each verdict)."""
    out = {}
    for t in ("eavail", "q3"):
        b0 = r["D4"][t]["per_k"]
        med = [x["push"]["median_abs_pct"] for x in b0]
        chi = [x["ew_chi2_push_vs_true"] for x in b0]
        k_best = int(np.argmin(med)) + 1
        uc = {"median_k5": med[4], "best_k": k_best, "median_best": med[k_best - 1],
              "relative_drop": 1 - med[k_best - 1] / med[4], "ew_chi2_k5": chi[4], "ew_chi2_best": chi[k_best - 1]}
        uc["fires"] = bool(uc["relative_drop"] >= 0.30 and chi[k_best - 1] < chi[4])
        cap = r["D5"][f"capacity_{t}"]["per_k"]
        cc = {}
        for k in (5, 15):
            m_cap, m_b0 = cap[k - 1]["push"]["median_abs_pct"], med[k - 1]
            cc[f"k{k}"] = {"capacity": m_cap, "b0": m_b0, "relative_drop": 1 - m_cap / m_b0,
                           "fires": bool(1 - m_cap / m_b0 >= 0.30)}
        un = r["D5"][f"missed_unity_{t}"]["per_k"]
        mu = {}
        for k in (5, 15, 30):
            m_u, m_b0 = un[k - 1]["push"]["median_abs_pct"], med[k - 1]
            mu[f"k{k}"] = {"unity": m_u, "b0": m_b0, "relative_drop": 1 - m_u / m_b0,
                           "ew_chi2_unity": un[k - 1]["ew_chi2_push_vs_true"], "ew_chi2_b0": chi[k - 1],
                           "fires": bool(1 - m_u / m_b0 >= 0.30 and un[k - 1]["ew_chi2_push_vs_true"] <= chi[k - 1])}
        # observability: best tested estimator (min median over B0 k<=30 and capacity k<=15)
        cands = [("b0", x["k"], x["push"]["median_abs_pct"], x.get("reco5d_explained_fraction"), x["ew_explained_fraction"]) for x in b0]
        cands += [("capacity", x["k"], x["push"]["median_abs_pct"], x.get("reco5d_explained_fraction"), x["ew_explained_fraction"]) for x in cap]
        best = min(cands, key=lambda c: c[2])
        ef = best[3] if best[3] is not None else best[4]
        ob = {"best_estimator": best[0], "best_k": best[1], "median_best": best[2], "median_b0_k5": med[4],
              "explained_fraction_at_best": ef, "explained_fraction_basis": "reco5d" if best[3] is not None else "EW projection",
              "ew_explained_fraction_at_best": best[4]}
        ob["fires"] = bool(ef is not None and ef >= 0.95 and best[2] >= 0.5 * med[4])
        out[t] = {"under_converged": uc, "capacity_limited": cc, "missed_event_limited": mu, "observability_limited": ob}
    return out


def d7(runs: Path, U, names, shape) -> dict:
    seeds = list(range(300000, 300012))

    def get(kind, s):
        if kind in ("b0", "sig") and s < 300004:
            p = load(runs / "trace" / f"trace_nominal_{'bkg' if kind == 'b0' else 'sig'}_s{s}.npz")
            return U @ p["xsec_it5_flat"], U @ p["xtrue_flat"], p["reco5d_D"]
        p = load(runs / "bkg" / f"bkg_{kind}_s{s}.npz")
        return U @ p["xsec_flat"], U @ p["xtrue_flat"], p["reco5d_D"]

    data = {k: [get(k, s) for s in seeds] for k in ("b0", "sig", "refcap", "exptmpl")}
    out = {"seeds": seeds}
    for k in ("b0", "sig", "refcap", "exptmpl"):
        r = np.array([rel(f, t) for f, t, _ in data[k]])
        m, se = r.mean(0), r.std(0, ddof=1) / math.sqrt(len(seeds))
        t = m / se
        out[f"closure_{k}"] = {"max_abs_t": float(np.max(np.abs(t))), "n_abs_t_gt_3.6": int(np.sum(np.abs(t) > 3.6)),
                               "mean_rel_total_pct": 100 * float(m[names.index("total_integrated")]),
                               "max_abs_mean_pct": 100 * float(np.max(np.abs(m))), "argmax": names[int(np.argmax(np.abs(m)))]}
    for k in ("b0", "refcap", "exptmpl"):
        d = np.array([(f - fs) / t for (f, t, _), (fs, _, _) in zip(data[k], data["sig"])])
        m, se = d.mean(0), d.std(0, ddof=1) / math.sqrt(len(seeds))
        tt = m / se
        worst = np.argsort(-np.abs(tt))[:12]
        out[f"paired_{k}_minus_sig"] = {
            "max_abs_t": float(np.max(np.abs(tt))), "n_abs_t_gt_3.6": int(np.sum(np.abs(tt) > 3.6)),
            "n_abs_t_gt_3": int(np.sum(np.abs(tt) > 3)), "max_abs_mean_pct": 100 * float(np.max(np.abs(m))),
            "median_abs_mean_pct": 100 * float(np.median(np.abs(m))),
            "total_integrated_pct": 100 * float(m[names.index("total_integrated")]),
            "worst": [{"name": names[i], "mean_pct": 100 * float(m[i]), "se_pct": 100 * float(se[i]), "t": float(tt[i])} for i in worst],
            "mean_pct": (100 * m).tolist(), "se_pct": (100 * se).tolist()}
    b = out["paired_b0_minus_sig"]
    for k in ("refcap", "exptmpl"):
        v = out[f"paired_{k}_minus_sig"]
        idx = [names.index(w["name"]) for w in b["worst"]]
        out[f"{k}_effect_on_b0_worst_cells"] = [{"name": names[i], "b0_pct": b["mean_pct"][i], "variant_pct": v["mean_pct"][i],
                                                 "variant_se_pct": v["se_pct"][i]} for i in idx]
    # reco-level subtraction residual map vs truth-level paired difference, in the EW projection
    dr = np.mean([ew_var(D, shape) / np.maximum(ew_var(Ds, shape), 1e-300) - 1 for (_, _, D), (_, _, Ds) in zip(data["b0"], data["sig"])], 0)
    dt = np.array(b["mean_pct"][:N_EW]) / 100
    from scipy.stats import spearmanr  # noqa: PLC0415
    out["reco_EW_subtraction_residual_pct"] = (100 * dr).round(3).tolist()
    out["spearman_reco_EW_residual_vs_truth_EW_paired"] = float(spearmanr(dr, dt).correlation)
    return out


def repairs(runs: Path, s5n: Path, U, names) -> dict:
    """Amendment 2: the edge-safe precision probe, the sentinel-row mask probe and the driver parity.
    The D2 attribution rule is applied with the edge-safe probe scale."""
    out = {"note": "D2 entries asimov_eavail_jitter1 and data_jitter1 are the CONFOUNDED original probe "
                   "(exact zeros pushed off the grid edge 0; amendment 2) and are not a rounding measurement"}
    rep = runs / "rep"
    base = load(runs / "asimov" / "asimov_b0_eavail.npz")
    b5 = U @ base["xsec_it5_flat"]
    p = load(rep / "rep_asimov_eavail_jitteredge1.npz")
    f = U @ p["xsec_flat"]
    out["asimov_eavail_edge_safe_jitter"] = {"max_rel_pct": 100 * float(np.max(np.abs(rel(f, b5)))),
                                             "median_rel_pct": 100 * float(np.median(np.abs(rel(f, b5))))}
    d = U @ load(runs / "drv" / "data_b0.npz")["xsec_flat"]
    scale = []
    for s in (1, 2):
        f = U @ load(rep / f"rep_data_jitteredge{s}.npz")["xsec_flat"]
        x = np.abs(rel(f, d))
        scale.append(x)
        out[f"data_edge_safe_jitter{s}"] = {"max_rel_pct": 100 * float(x.max()), "median_rel_pct": 100 * float(np.median(x)),
                                           "argmax": names[int(x.argmax())]}
    scale = np.maximum(*scale)
    drv = U @ s5c_assemble.read_flat(str(s5n / "c7" / "xsec_5d_driver_negweight_F2.root"))
    ns = U @ load(rep / "rep_data_nosentinel.npz")["xsec_flat"]
    orig, masked = np.abs(rel(drv, d)), np.abs(rel(drv, ns))
    out["data_sentinel_mask"] = {
        "nosentinel_vs_b0_max_rel_pct": 100 * float(np.max(np.abs(rel(ns, d)))),
        "nosentinel_vs_b0_median_rel_pct": 100 * float(np.median(np.abs(rel(ns, d)))),
        "driver_vs_npz_b0": {"max_pct": 100 * float(orig.max()), "median_pct": 100 * float(np.median(orig)), "argmax": names[int(orig.argmax())]},
        "driver_vs_npz_nosentinel": {"max_pct": 100 * float(masked.max()), "median_pct": 100 * float(np.median(masked)), "argmax": names[int(masked.argmax())]},
        "edge_safe_probe_scale_max_pct": 100 * float(scale.max()), "edge_safe_probe_scale_median_pct": 100 * float(np.median(scale)),
        "functionals_where_mask_moves_the_difference_by_more_than_the_probe": int(np.sum(np.abs(orig - masked) > scale)),
        "rule": "a pipeline factor is named only if switching it alone moves the driver-npz difference by more than the edge-safe probe scale"}
    a0 = load(runs / "drv" / "driver_eavail.npz")
    an = load(rep / "rep_asimov_eavail_nosentinel.npz")
    rd, rn, rb = rel(a0["fn_unf"], a0["fn_true"]), rel(U @ an["xsec_flat"], an["fn_true"]), rel(b5, base["fn_true"])
    out["asimov_eavail_driver_vs_npz"] = {"with_sentinel_rows_max_pp": 100 * float(np.max(np.abs(rd - rb))),
                                          "with_sentinel_rows_median_pp": 100 * float(np.median(np.abs(rd - rb))),
                                          "without_sentinel_rows_max_pp": 100 * float(np.max(np.abs(rd - rn))),
                                          "without_sentinel_rows_median_pp": 100 * float(np.median(np.abs(rd - rn)))}
    par = load(rep / "rep_driver_nominal_parity.npz")
    out["driver_parity"] = par["meta"]["input_parity"]
    out["driver_parity_nominal_residual"] = ew_stats(rel(par["fn_unf"], par["fn_true"]))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--s5c-contract", type=Path, required=True)
    ap.add_argument("--runs", type=Path, required=True, help="the s5e runs/diag directory")
    ap.add_argument("--s5n-runs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    U, names = sc.reported_functionals(json.loads(a.s5c_contract.read_text()))
    probe = load(a.runs / "asimov" / "asimov_b0_nominal.npz")
    shape = (14, 16, 7, 7, 6)
    assert probe["reco5d_true"].size == int(np.prod(shape))
    rec = {"schema": "s5e-diag/1", "functional_names": names}
    rec["D0"] = d0(a.runs, a.s5n_runs, U)
    rec.update(d1_d2(a.runs, a.s5n_runs, U, names))
    rec.update(d3_to_d6(a.runs, shape))
    rec["D6"] = {"geometry": json.loads((a.runs / "geometry.json").read_text()),
                 "S_dep": {t: {"ew": rec["D4"][t]["S_dep_ew"], "reco5d": rec["D4"][t]["S_dep_reco5d"],
                               "ncell_reco5d": rec["D4"][t]["ncell_reco5d"]} for t in TRUTHS}}
    rec["D7"] = d7(a.runs, U, names, shape)
    if (a.runs / "rep").is_dir():
        rec["D2_repairs"] = repairs(a.runs, a.s5n_runs, U, names)
    rec["interpretation_rules"] = rules(rec)
    a.out.write_text(json.dumps(rec, indent=1, default=float) + "\n")
    print(json.dumps({"D0": {k: rec["D0"][k] for k in ("n_equal", "n_compared", "data_b0_vs_s5n_c7_npz_equal")},
                      "rules": {t: {k: v.get("fires", v) for k, v in r.items()} for t, r in rec["interpretation_rules"].items()}},
                     indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
