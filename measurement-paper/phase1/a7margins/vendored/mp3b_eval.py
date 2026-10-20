#!/usr/bin/env python3
"""MP3-B step 2: gate B4, then the NuWro-on-CH readout over the 109 reported J cells, BESIDE A7
(frozen spec PLAN.md §4.3; BINDING-PHASE1-20261019 D6: labelled, never in place of A7; A7 is not re-graded).

Everything that touches the frozen statistic goes through nd-unfolding/s5p_joint.py's own functions (j_matrix,
prediction, Model, ensemble, statistics, test_null, load_shift) and s5p_inference (stat_total, stat_shape,
shape_parts, mc_pvalue, cp_interval, holm, holm_determined), imported from copies byte-identical to the frozen
4f5a613f modules.

  mu_C12 = U x (frozen NuWro product)  [CONTROL: = U x of the step-1 rebuild, bitwise]
  mu_CH  = U x_CH, x_CH = (12/13) x_C12 + (1/13) x_H;  Var(mu_CH) = U^2 sumw2_CH
  B4 (before any readout): (1/13) sqrt(U^2 sumw2_H) <= (1/3) (12/13) sqrt(U^2 sumw2_C12) in every reported cell
  r_c = mu_CH / mu_C12 and its shape form; f_H = (1/13) U x_H / mu_CH
  Delta = mu_CH - mu_C12 over sigma_c, three labelled readings (as MP3-A); metric norms of Delta
  REPLAY (DESCRIPTIVE, not a re-grade): T_total/T_shape at the data with mu replaced by mu_CH, under the frozen
  W = V + diag Var(mu_C12) (PRIMARY) and under W_CH = V + diag Var(mu_CH), against NuWro's FROZEN null T
  distributions (every declared shift variant, the claim rule = the largest p), then A7's own decision rule
  (Holm with determinacy, s5p_inference.holm_determined) over the frozen family with NuWro's two claims replaced.

Usage: python3 mp3b_eval.py --design D --s5c-contract C --v V --frozen-eval J --build-dir B --out OUT
Exit codes: 0 done; 3 a control failed; 4 gate B4 failed (no readout written beyond the gate record).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import resource
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402

import s5p_inference as si  # noqa: E402
import s5p_joint as sj  # noqa: E402
import s5p_stage1_inspect as s1  # noqa: E402

KEY = "NuWro_21_09"
F_C, F_H = 12.0 / 13.0, 1.0 / 13.0
B4_BOUND = 1.0 / 3.0
LABEL = "DESCRIPTIVE, not a re-grade (BINDING D6; A7 stands; reported beside A7, never in place of it)"
SIGMA_READINGS = {
    "a_sd_null_result": "SD (ddof 1) over NuWro's frozen calibration ensemble of the J-cell result f = Model.apply(U x) "
                        "(s5p_joint.ensemble). PRIMARY (MP3-A reading (a))",
    "b_sqrt_diag_W": "sqrt(diag W), W = V + diag Var(mu_C12): the frozen metric's own per-cell scale",
    "c_sd_null_residual": "SD (ddof 1) over the ensemble of f - (mu_C12 + eps), eps the statistic's own seed-keyed "
                          "prediction-MC draw (s5p_joint.statistics)",
}
NORM_READINGS = {
    "total_W": "Delta' W^-1 Delta, frozen W = V + diag Var(mu_C12). PRIMARY total",
    "total_WCH": "Delta' W_CH^-1 Delta, W_CH = V + diag Var(mu_CH)",
    "total_V": "Delta' V^-1 Delta (V alone; not the frozen metric)",
    "shape_jac_data": "(q_CH - q_C12)' Vs^-1 (q_CH - q_C12), Vs = J W J' at the DATA f, last cell dropped: the "
                      "quadratic form the observed T_shape uses. PRIMARY shape",
    "shape_jac_muCH": "stat_shape(f = mu_CH, mu = mu_C12, W): Jacobian at mu_CH",
    "shape_jac_muC12": "stat_shape(f = mu_C12, mu = mu_CH, W): Jacobian at mu_C12",
}


def sha256(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def rel(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    nz = b != 0
    return {"bitwise_equal": bool(np.array_equal(a, b)),
            "max_rel_diff": float(np.max(np.abs(a[nz] - b[nz]) / np.abs(b[nz]))) if nz.any() else 0.0}


def q(x):
    x = np.asarray(x, float)
    return {"min": float(x.min()), "median": float(np.median(x)), "max": float(x.max())}


INTERVAL_RTOL = 1e-12   # Clopper-Pearson ends come from scipy.stats.beta.ppf; a scipy build may move the last ulp


def diff_paths(a, b, path=""):
    """Paths where two JSON-like objects differ: exact equality everywhere, except that a float under a key
    containing 'interval' may differ by <= INTERVAL_RTOL relative (such paths are returned with a '~' prefix and
    do not count as a failure)."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += diff_paths(a.get(k), b.get(k), f"{path}/{k}")
        return out
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff_paths(x, y, f"{path}[{i}]")
        return out
    if a == b:
        return []
    if ("interval" in path and isinstance(a, float) and isinstance(b, float)
            and abs(a - b) <= INTERVAL_RTOL * max(abs(a), abs(b))):
        return ["~" + path]
    return [path]


def same(a, b) -> dict:
    d = diff_paths(json.loads(json.dumps(a)), b)
    hard = [x for x in d if not x.startswith("~")]
    return {"identical": not hard, "bitwise": not d, "differing_paths": hard[:50],
            "interval_last_ulp_paths": [x[1:] for x in d if x.startswith("~")][:50]}


def kstar(B: int, th: float, level: float = 0.95) -> int:
    """The largest exceedance count k whose Clopper-Pearson upper end is below th (-1 if none)."""
    k = -1
    while k + 1 <= B and si.cp_interval(k + 1, B, level)[1] < th:
        k += 1
    return k


def t_critical(nulls: list, ks: int) -> float:
    """Claim rule (k = the largest exceedance count over the variant nulls): rejected iff k <= ks, i.e. iff
    T > max over variants of the (ks+1)-th largest null value."""
    if ks < 0:
        return float("inf")
    return float(max(np.sort(np.asarray(t, float))[::-1][ks] for t in nulls))



def load_setup(a):
    """The frozen design, metric, J map, model and NuWro's frozen prediction (C12)."""
    design = json.loads(a.design.read_text())
    sj.check_v(design, a.v)
    V = np.asarray(np.load(a.v, allow_pickle=False)["V"], float)
    supported = json.loads(a.s5c_contract.read_text())["measurement"]["partition_J"]["supported_cells"]
    U, names, pz_index = sj.j_matrix({}, supported)
    model = sj.Model(design, U)
    frozen = json.loads(a.frozen_eval.read_text())
    if frozen["names"] != names:
        raise SystemExit("J cell names differ from the frozen evaluation's")
    spec = design["nulls"][KEY]
    dom = np.ones(len(names), bool) if spec.get("domain") != "pz_lt_6" else (pz_index <= 1)
    mu_C, var_C = sj.prediction(spec["prediction"], U)
    return {"design": design, "V": V, "supported": supported, "U": U, "names": names, "pz_index": pz_index,
            "model": model, "frozen": frozen, "spec": spec, "dom": dom, "mu_C": mu_C, "var_C": var_C}


def frozen_reproduction(st) -> dict:
    """NuWro's frozen test recomputed through s5p_joint.test_null, the kappa_robust M1 nulls, and A7's decision
    rule on the frozen family; each compared with joint-evaluate.json."""
    design, V, model, frozen, spec, dom = st["design"], st["V"], st["model"], st["frozen"], st["spec"], st["dom"]
    files = sj.product_files(spec["calibration_glob"])
    B = sj.calibration_count(spec)
    if len(files) != B:
        raise SystemExit(f"{KEY}: {len(files)} calibration products, {B} declared")
    F, seeds = sj.ensemble(model, files)
    coefs = [float(c) for c in design.get("shift_coefficients", [0.0])]
    entry = sj.test_null(model, design, KEY, V, st["names"], st["pz_index"], files, coefs)
    nulls = entry.pop("_nulls")
    vnames = list(entry["variants"].keys())
    m1 = design["m1_shift"][KEY]
    d1, _ = sj.load_shift({k: v for k, v in m1.items() if k in ("path", "sha256")}, len(st["names"]))
    robust = {}
    for nm, sv in ((f"m1+{m1['kappa_robust']}", m1["kappa_robust"] * d1), (f"m1-{m1['kappa_robust']}", -m1["kappa_robust"] * d1)):
        robust[nm] = sj.statistics(F + sv, st["mu_C"], st["var_C"], V, dom, spec["surrogate_seed0"], seeds=seeds)
    T_frozen = {"total": frozen["tests"][KEY]["T_total_obs"], "shape": frozen["tests"][KEY]["T_shape_obs"]}
    rob_p = {nm: {s: si.mc_pvalue(T_frozen[s], rn[i]) for i, s in enumerate(("total", "shape"))} for nm, rn in robust.items()}
    fam = {f"{k}:{s}": {"p": frozen["tests"][k][s]["p"], "k": frozen["tests"][k][s]["k"], "B": frozen["tests"][k][s]["B"]}
           for k in design["nulls"] for s in ("total", "shape")}
    fam_r = {f"{k}:{s}": {"p": frozen["tests"][k][s + "_robust"]["p"], "k": frozen["tests"][k][s + "_robust"]["k"],
                          "B": frozen["tests"][k][s + "_robust"]["B"]} for k in design["nulls"] for s in ("total", "shape")}
    al = design["alpha_family"]
    controls = {"frozen_NuWro_test_recomputed": {**same(entry, frozen["tests"][KEY]), "variants": vnames, "B": int(len(files))},
                "robust_nulls_reproduce_frozen": same(rob_p, frozen["tests"][KEY]["robustness_variants"]),
                "holm_determined_reproduces_frozen": {
                    "decisions": same(si.holm_determined(fam, al), frozen["decisions"]),
                    "decisions_robust_kappa": same(si.holm_determined(fam_r, al), frozen["decisions_robust_kappa"]),
                    "holm_point": same(si.holm({k: v["p"] for k, v in fam.items()}, al), frozen["holm_point"])}}
    ok = (controls["frozen_NuWro_test_recomputed"]["identical"] and controls["robust_nulls_reproduce_frozen"]["identical"]
          and all(v["identical"] for v in controls["holm_determined_reproduces_frozen"].values()))
    return {"F": F, "seeds": seeds, "files": files, "nulls": nulls, "vnames": vnames, "robust": robust, "fam": fam,
            "fam_r": fam_r, "T_frozen": T_frozen, "controls": controls, "ok": bool(ok)}


def replay_one(st, fr, mu_new, var_metric) -> dict:
    """The observed statistic with mu replaced by mu_new under W = V + diag var_metric, against NuWro's frozen
    null variants; the claim rule; A7's Holm-with-determinacy over the frozen family with NuWro's claims replaced."""
    design, V, model, frozen, dom = st["design"], st["V"], st["model"], st["frozen"], st["dom"]
    nulls, vnames, T_frozen = fr["nulls"], fr["vnames"], fr["T_frozen"]
    tt, ts = sj.statistics(model.f_data[None, :], mu_new, var_metric, V, dom, 0, draw=False)
    T = {"total": float(tt[0]), "shape": float(ts[0])}
    base = nulls[vnames.index("0.0")]
    out = {"T": T, "T_frozen": T_frozen, "per_variant": {}, "claim": {}, "claim_robust": {}, "in_null_sd": {}, "critical": {}}
    for i, s in enumerate(("total", "shape")):
        pv = {vn: si.mc_pvalue(T[s], nulls[j][i]) for j, vn in enumerate(vnames)}
        for vn in vnames:
            out["per_variant"].setdefault(vn, {})[s] = pv[vn]
        claim = max(pv.values(), key=lambda v: v["p"])
        out["claim"][s] = dict(claim, rule="the largest p over the declared shift variants")
        rp = [si.mc_pvalue(T[s], rn[i]) for rn in fr["robust"].values()]
        out["claim_robust"][s] = dict(max([claim] + rp, key=lambda v: v["p"]),
                                      rule="the claim p with the kappa_robust M1 variants added (report only)")
        sd0, med0 = float(np.std(base[i])), float(np.median(base[i]))
        th = frozen["decisions"][f"{KEY}:{s}"]["threshold"]
        ks = kstar(int(claim["B"]), th)
        tc = t_critical([nulls[j][i] for j in range(len(vnames))], ks)
        out["in_null_sd"][s] = {"null_sd": sd0, "null_median": med0,
                                "frozen_margin_over_median": (T_frozen[s] - med0) / sd0,
                                "replay_margin_over_median": (T[s] - med0) / sd0,
                                "change": (T[s] - T_frozen[s]) / sd0}
        out["critical"][s] = {"frozen_holm_threshold": th, "k_star": ks, "T_critical": tc,
                              "rule": "rejected at the frozen Holm position iff T > T_critical (claim k <= k_star, k_star "
                                      "the largest k whose Clopper-Pearson 95% upper end is below the threshold)",
                              "frozen_T_minus_Tcrit_in_null_sd": (T_frozen[s] - tc) / sd0,
                              "replay_T_minus_Tcrit_in_null_sd": (T[s] - tc) / sd0,
                              "replay_above_T_critical": bool(T[s] > tc)}
    tj, tsj = sj.statistics(model.jitters, mu_new, var_metric, V, dom, 0, draw=False)
    out["observed_jitter_p"] = {}
    for i, (s, tobs) in enumerate((("total", tj), ("shape", tsj))):
        pj = np.max([sj.pvals_against(tobs, nulls[j][i]) for j in range(len(vnames))], axis=0)
        out["observed_jitter_p"][s] = {"min": float(pj.min()), "median": float(np.median(pj)), "max": float(pj.max()),
                                       "n": int(pj.size)}
    fam2, fam2r = dict(fr["fam"]), dict(fr["fam_r"])
    for s in ("total", "shape"):
        fam2[f"{KEY}:{s}"] = {k: out["claim"][s][k] for k in ("p", "k", "B")}
        fam2r[f"{KEY}:{s}"] = {k: out["claim_robust"][s][k] for k in ("p", "k", "B")}
    dec = si.holm_determined(fam2, design["alpha_family"])
    decr = si.holm_determined(fam2r, design["alpha_family"])
    out["holm_determined_replay"], out["holm_determined_replay_robust_kappa"] = dec, decr
    out["decision_changes_vs_frozen"] = {k: [frozen["decisions"][k]["decision"], dec[k]["decision"]]
                                         for k in dec if dec[k]["decision"] != frozen["decisions"][k]["decision"]}
    out["decision_changes_vs_frozen_robust"] = {k: [frozen["decisions_robust_kappa"][k]["decision"], decr[k]["decision"]]
                                                for k in decr if decr[k]["decision"] != frozen["decisions_robust_kappa"][k]["decision"]}
    for s in ("total", "shape"):
        out[f"NuWro_{s}_crosses_frozen_decision"] = dec[f"{KEY}:{s}"]["decision"] != frozen["decisions"][f"{KEY}:{s}"]["decision"]
    return out


def replay_identity_control(st, fr) -> dict:
    """With mu_new = mu_C12 and the frozen metric the replay must return the frozen T, claim p and decisions."""
    o = replay_one(st, fr, st["mu_C"], st["var_C"])
    fz = st["frozen"]["tests"][KEY]
    ok = (o["T"]["total"] == fz["T_total_obs"] and o["T"]["shape"] == fz["T_shape_obs"]
          and all(o["claim"][s]["p"] == fz[s]["p"] and o["claim"][s]["k"] == fz[s]["k"] for s in ("total", "shape"))
          and all(o["claim_robust"][s]["p"] == fz[s + "_robust"]["p"] for s in ("total", "shape"))
          and not o["decision_changes_vs_frozen"] and not o["decision_changes_vs_frozen_robust"]
          and same(o["observed_jitter_p"], fz["observed_jitter_p"])["identical"])
    return {"T": o["T"], "claim_p": {s: o["claim"][s]["p"] for s in ("total", "shape")},
            "frozen_margins_in_null_sd": {s: o["in_null_sd"][s]["frozen_margin_over_median"] for s in ("total", "shape")},
            "frozen_T_minus_Tcrit_in_null_sd": {s: o["critical"][s]["frozen_T_minus_Tcrit_in_null_sd"] for s in ("total", "shape")},
            "identical": bool(ok)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    for k in ("design", "s5c-contract", "v", "frozen-eval", "build-dir", "out"):
        ap.add_argument(f"--{k}", type=Path, required=True)
    a = ap.parse_args(argv)
    t0 = time.time()
    mods = {m.__name__: str(Path(m.__file__).resolve()) for m in (si, sj, s1)}
    for n, p in mods.items():
        if Path(p).parent != HERE:
            raise SystemExit(f"{n} imported from {p}, not from {HERE}")
    a.out.mkdir(parents=True, exist_ok=False)
    res = {"schema": "mp3b-eval/1", "argv": sys.argv, "label": LABEL,
           "modules": {n: {"file": p, "sha256": sha256(p)} for n, p in mods.items()},
           "numpy": np.__version__, "python": sys.version, "sigma_readings": SIGMA_READINGS,
           "norm_readings": NORM_READINGS, "inputs": {}, "controls": {}, "gates": {}}

    def finish(code: int, msg: str) -> int:
        ru = resource.getrusage(resource.RUSAGE_SELF)
        res.update(verdict=msg, exit_code=code, cpu_s=ru.ru_utime + ru.ru_stime, maxrss_kb=ru.ru_maxrss,
                   wall_s=time.time() - t0)
        (a.out / "mp3b_results.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item()) + "\n")
        print(msg, flush=True)
        return code

    for k, p in (("design", a.design), ("s5c_contract", a.s5c_contract), ("v", a.v), ("frozen_eval", a.frozen_eval)):
        res["inputs"][f"{k}_sha256"] = sha256(p)
    st = load_setup(a)
    U, names, dom, mu_C, var_C, V, model = st["U"], st["names"], st["dom"], st["mu_C"], st["var_C"], st["V"], st["model"]
    spec = st["spec"]
    res["inputs"]["prediction_C12"] = {"path": spec["prediction"], "sha256": sha256(spec["prediction"])}
    fz = np.load(a.build_dir / "mp3b_fine_nuwro.npz")
    res["controls"]["J_rebuilt_C12_vs_frozen"] = {"mu": rel(U @ fz["xsec_C12_rebuilt"], mu_C),
                                                  "var": rel((U ** 2) @ fz["sumw2_C12_rebuilt"], var_C)}
    res["controls"]["J_frozen_arrays_in_build_vs_prediction"] = {"mu": rel(U @ fz["xsec_C12_frozen"], mu_C),
                                                                 "var": rel((U ** 2) @ fz["sumw2_C12_frozen"], var_C)}
    if not all(v["bitwise_equal"] for c in res["controls"].values() for v in c.values()):
        return finish(3, "STOP: J-cell C12 control failed")

    # ---------------- B4 first: only the MC variances are read
    var_H = (U ** 2) @ fz["sumw2_H"]
    err_H, err_C = F_H * np.sqrt(var_H), F_C * np.sqrt(var_C)
    ratio = err_H / err_C
    n_H = (U > 0).astype(float) @ fz["nevt_H"]
    worst = int(np.argmax(np.where(dom, ratio, -np.inf)))
    b4 = {"rule": "(1/13) sqrt(U^2 sumw2_H) <= (1/3) (12/13) sqrt(U^2 sumw2_C12) in every reported cell (sumw2 = the "
                  "gen5d convention, normalization constants exact)",
          "n_cells": int(dom.sum()), "ratio": q(ratio[dom]), "worst_cell": names[worst], "worst_ratio": float(ratio[worst]),
          "n_cells_ratio_gt_bound": int(np.sum(ratio[dom] > B4_BOUND)),
          "cells_ratio_gt_bound": [names[i] for i in np.where(dom & (ratio > B4_BOUND))[0]],
          "n_cells_with_zero_H_events": int(np.sum(n_H[dom] == 0)),
          "cells_with_fewer_than_10_H_events": [names[i] for i in np.where(dom & (n_H < 10))[0]],
          "event_factor_that_would_meet_the_bound_at_the_worst_cell": float((ratio[worst] / B4_BOUND) ** 2),
          "pass": bool(np.all(ratio[dom] <= B4_BOUND))}
    res["gates"]["B4"] = b4
    res["b4_cells"] = {"ratio": ratio.tolist(), "n_H_raw": n_H.tolist(), "err_H_contribution": err_H.tolist(),
                       "err_C12_contribution": err_C.tolist()}
    print("B4", json.dumps({k: b4[k] for k in ("ratio", "worst_cell", "worst_ratio", "n_cells_ratio_gt_bound", "pass")}), flush=True)
    if not b4["pass"]:
        return finish(4, "STOP: gate B4 failed; the remedy factor is not fixed (more H events once); no readout")

    # ---------------- the frozen statistic and decision rule, reproduced (controls) before any replay
    fr = frozen_reproduction(st)
    res["controls"].update(fr["controls"])
    res["controls"]["replay_identity_mu_C12"] = replay_identity_control(st, fr)
    ok = fr["ok"] and res["controls"]["replay_identity_mu_C12"]["identical"]
    print("CONTROLS", json.dumps({k: res["controls"][k] for k in ("frozen_NuWro_test_recomputed", "robust_nulls_reproduce_frozen",
                                                                  "holm_determined_reproduces_frozen", "replay_identity_mu_C12")}), flush=True)
    if not ok:
        return finish(3, "STOP: the frozen NuWro statistic or decision rule was not reproduced; no replay")
    F, seeds, nulls, vnames = fr["F"], fr["seeds"], fr["nulls"], fr["vnames"]

    # ---------------- readout
    hJ = U @ fz["xsec_H"]
    mu_CH = U @ fz["xsec_CH"]
    var_CH = (U ** 2) @ fz["sumw2_CH"]
    res["controls"]["combination_identity_J"] = rel(mu_CH, F_C * mu_C + F_H * hJ)
    f_H = F_H * hJ / mu_CH
    r = mu_CH / mu_C
    r_shape = (mu_CH / mu_CH.sum()) / (mu_C / mu_C.sum())
    sd_r = F_H * np.sqrt(var_H / mu_C ** 2 + hJ ** 2 * var_C / mu_C ** 4)   # delta method, C12 and H independent
    delta = mu_CH - mu_C
    sd_a = F.std(0, ddof=1)
    W = V + np.diag(var_C)
    sd_b = np.sqrt(np.diag(W))
    eps = np.array([np.random.default_rng([int(spec["surrogate_seed0"]), int(s), 0x4A02]).normal(size=mu_C.size)
                    for s in seeds]) * np.sqrt(var_C)
    sd_c = (F - (mu_C + eps)).std(0, ddof=1)
    z = {"a_sd_null_result": delta / sd_a, "b_sqrt_diag_W": delta / sd_b, "c_sd_null_residual": delta / sd_c}
    P = F / F.sum(1, keepdims=True)
    dq = mu_CH / mu_CH.sum() - mu_C / mu_C.sum()
    z_shape = dq / P.std(0, ddof=1)

    Wd = W[np.ix_(dom, dom)]
    Winv = np.linalg.inv(Wd)
    WCH = V[np.ix_(dom, dom)] + np.diag(var_CH[dom])
    _, Vs = si.shape_parts(model.f_data[dom], Wd)
    dqd = (mu_CH[dom] / mu_CH[dom].sum() - mu_C[dom] / mu_C[dom].sum())[:-1]
    norms = {"total_W": si.stat_total(mu_CH[dom], mu_C[dom], Winv),
             "total_WCH": si.stat_total(mu_CH[dom], mu_C[dom], np.linalg.inv(WCH)),
             "total_V": si.stat_total(mu_CH[dom], mu_C[dom], np.linalg.inv(V[np.ix_(dom, dom)])),
             "shape_jac_data": float(dqd @ np.linalg.solve(Vs[:-1, :-1], dqd)),
             "shape_jac_muCH": si.stat_shape(mu_CH[dom], mu_C[dom], Wd),
             "shape_jac_muC12": si.stat_shape(mu_C[dom], mu_CH[dom], Wd)}
    base = nulls[vnames.index("0.0")]
    nullT = {s: {"median": float(np.median(t)), "p95": float(np.quantile(t, 0.95)), "sd": float(np.std(t)),
                 "min": float(t.min()), "max": float(t.max())} for s, t in (("total", base[0]), ("shape", base[1]))}

    # ---------------- REPLAY (descriptive, not a re-grade)
    replay = {"label": LABEL, "null": "NuWro_21_09's FROZEN calibration ensemble (pseudo-data from the C12 truth), every "
                                      "declared shift variant; the claim p is the largest over the variants",
              "variants": vnames, "metrics": {"frozen_W": replay_one(st, fr, mu_CH, var_C),
                                              "W_CH": replay_one(st, fr, mu_CH, var_CH)}}
    rr = (model.f_data - mu_C)[dom]
    cross = float(-2.0 * rr @ Winv @ delta[dom])
    replay["metrics"]["frozen_W"]["total_decomposition"] = {
        "cross_term_-2r'W^-1Delta": cross, "Delta'W^-1Delta": norms["total_W"], "sum": cross + norms["total_W"],
        "T_CH_minus_T_C12": replay["metrics"]["frozen_W"]["T"]["total"] - fr["T_frozen"]["total"]}
    tn2, sn2 = sj.statistics(F, mu_C, var_CH, V, dom, spec["surrogate_seed0"], seeds=seeds)
    Tw = replay["metrics"]["W_CH"]["T"]
    replay["diagnostic_null_with_W_CH_metric_unshifted"] = {
        "label": "diagnostic only: NOT the frozen null; the unshifted calibration ensemble re-evaluated with W_CH",
        "null_T_total": {"median": float(np.median(tn2)), "sd": float(np.std(tn2))},
        "null_T_shape": {"median": float(np.median(sn2)), "sd": float(np.std(sn2))},
        "replay_W_CH_vs_it": {"total": si.mc_pvalue(Tw["total"], tn2), "shape": si.mc_pvalue(Tw["shape"], sn2),
                              "total_margin_in_sd": (Tw["total"] - float(np.median(tn2))) / float(np.std(tn2)),
                              "shape_margin_in_sd": (Tw["shape"] - float(np.median(sn2))) / float(np.std(sn2))}}
    m_f, m_w = replay["metrics"]["frozen_W"], replay["metrics"]["W_CH"]
    replay["FIRST_LINE_FLAG"] = {
        "NuWro_shape_would_cross_frozen_threshold_frozen_W": bool(m_f["NuWro_shape_crosses_frozen_decision"]),
        "NuWro_shape_would_cross_frozen_threshold_W_CH": bool(m_w["NuWro_shape_crosses_frozen_decision"]),
        "any_family_decision_changes": bool(m_f["decision_changes_vs_frozen"] or m_w["decision_changes_vs_frozen"]
                                            or m_f["decision_changes_vs_frozen_robust"] or m_w["decision_changes_vs_frozen_robust"])}
    res["replay"], res["metric_norms"], res["null_T_c0"] = replay, norms, nullT

    # ---------------- summaries
    supported = st["supported"]
    cmap, _ = s1.coarse_map(s1.J_EDGES, supported)
    vol = s1.fine_volume()
    fine_shape = s1.fine_shape()
    iW_fine = np.unravel_index(np.arange(vol.size), fine_shape)[4]
    jidx = [np.unravel_index(c, (3, 3, 3, 3, 3)) for c in supported]

    def region(m):
        return {"n_cells": int(m.sum()), "mu_C12_sum_cm2": float(mu_C[m].sum()), "mu_CH_sum_cm2": float(mu_CH[m].sum()),
                "r_sum": float(mu_CH[m].sum() / mu_C[m].sum()), "f_H_sum": float(F_H * hJ[m].sum() / mu_CH[m].sum()),
                "r_shape_sum": float((mu_CH[m].sum() / mu_CH.sum()) / (mu_C[m].sum() / mu_C.sum())),
                "r_cells": q(r[m]), "r_shape_cells": q(r_shape[m]), "f_H_cells": q(f_H[m]),
                **{f"z_{k}": q(v[m]) for k, v in z.items()}, "z_shape": q(z_shape[m])}
    Wj, Ej = np.array([i[4] for i in jidx]), np.array([i[2] for i in jidx])
    regs = {"all_109": np.ones(len(names), bool)}
    for j in range(3):
        regs[f"W_J{j} [{s1.J_EDGES['W'][j]},{s1.J_EDGES['W'][j + 1]})"] = Wj == j
    for j in range(3):
        regs[f"Eavail_J{j} [{s1.J_EDGES['eavail'][j]},{s1.J_EDGES['eavail'][j + 1]})"] = Ej == j
    res["regions_J"] = {k: region(m) for k, m in regs.items()}
    fw = {}
    for j in range(fine_shape[4]):
        m = (cmap >= 0) & (iW_fine == j)
        c, ch, h = (float((fz[k][m] * vol[m]).sum()) for k in ("xsec_C12_frozen", "xsec_CH", "xsec_H"))
        fw[f"W{j} [{s1.FINE['W'][j]},{s1.FINE['W'][j + 1]})"] = {"CH_over_C12_per_nucleon": ch / c if c else None,
                                                                  "f_H": F_H * h / ch if ch else None}
    res["fine_W_regions_in_reported_cells"] = fw
    res["largest_cells"] = {"abs_z_a_top10": [names[i] for i in np.argsort(-np.abs(z["a_sd_null_result"]))[:10]],
                            "abs_r_minus_1_top10": [names[i] for i in np.argsort(-np.abs(r - 1))[:10]],
                            "abs_r_shape_minus_1_top10": [names[i] for i in np.argsort(-np.abs(r_shape - 1))[:10]]}
    res["sd_ratio_b_over_a"], res["sd_ratio_c_over_a"] = q(sd_b / sd_a), q(sd_c / sd_a)
    res["null_mean_minus_mu_over_sd_a"] = q((F.mean(0) - mu_C) / sd_a)
    res["cells"] = {"mu_C12": mu_C.tolist(), "var_mu_C12": var_C.tolist(), "mu_CH": mu_CH.tolist(), "var_mu_CH": var_CH.tolist(),
                    "H_part": hJ.tolist(), "var_H_part": var_H.tolist(), "f_H": f_H.tolist(), "r": r.tolist(),
                    "sd_r_mc": sd_r.tolist(), "r_shape": r_shape.tolist(), "delta": delta.tolist(), "sd_a": sd_a.tolist(),
                    "sd_b": sd_b.tolist(), "sd_c": sd_c.tolist(), **{f"z_{k}": v.tolist() for k, v in z.items()},
                    "z_shape": z_shape.tolist()}
    rows = []
    for i, nm in enumerate(names):
        e = {ax: (s1.J_EDGES[ax][jidx[i][k]], s1.J_EDGES[ax][jidx[i][k] + 1]) for k, ax in enumerate(s1.AXES)}
        rows.append({"cell": i, "name": nm, **{f"{ax}_lo": e[ax][0] for ax in s1.AXES}, **{f"{ax}_hi": e[ax][1] for ax in s1.AXES},
                     "mu_C12": mu_C[i], "mu_CH": mu_CH[i], "f_H": f_H[i], "r": r[i], "sd_r_mc": sd_r[i], "r_shape": r_shape[i],
                     "z": z["a_sd_null_result"][i], "z_sqrtdiagW": z["b_sqrt_diag_W"][i], "z_resid": z["c_sd_null_residual"][i],
                     "z_shape": z_shape[i], "b4_ratio": ratio[i], "n_H_raw": int(n_H[i])})
    with open(a.out / "mp3b_cells.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for row in rows:
            w.writerow({k: (f"{v:.10g}" if isinstance(v, (float, np.floating)) else v) for k, v in row.items()})
    print("REPLAY", json.dumps({m: {"T": replay["metrics"][m]["T"],
                                    "claim": {s: replay["metrics"][m]["claim"][s]["p"] for s in ("total", "shape")},
                                    "in_null_sd": replay["metrics"][m]["in_null_sd"],
                                    "changes": replay["metrics"][m]["decision_changes_vs_frozen"]} for m in replay["metrics"]}), flush=True)
    print("CROSSES_FROZEN_THRESHOLD", json.dumps(replay["FIRST_LINE_FLAG"]), flush=True)
    return finish(0, "DONE: B4 passed; readout and descriptive replay written")


if __name__ == "__main__":
    raise SystemExit(main())
