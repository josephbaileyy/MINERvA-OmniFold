#!/usr/bin/env python3
"""MP3-A step 2: the GENIE CH vs carbon-only map over the 109 reported J cells, in null-SD units of the frozen
s5p evaluation (frozen spec PLAN.md §4.2-4.3; BINDING-PHASE1-20261019 D6: reported BESIDE A7, never in place).

Everything that touches the frozen statistic goes through nd-unfolding/s5p_joint.py's own functions
(j_matrix, prediction, Model and Model.apply via ensemble, statistics) and s5p_inference (stat_total,
stat_shape, shape_parts), imported from copies byte-identical to the frozen 4f5a613f modules.

Per G in {GENIE CV, GENIE MEC}:
  mu_CH  = U x (frozen product), the frozen prediction (CONTROL: equals U x of the step-1 rebuild);
  mu_C   = (13/12) U x_C12 (carbon-only per C12 nucleon, target code 1000060120 only);
  f_H    = U x_H1 / mu_CH (tgt 2212); f_other = U x_other / mu_CH;
  r_c    = mu_C / mu_CH, and the shape-normalized r_c (each over its own sum over the 109 cells);
  Delta  = mu_C - mu_CH, in units of sigma_c (three labelled readings, see SIGMA_READINGS);
  metric norms of Delta under W = V + diag Var(mu_G) (labelled readings, see NORM_READINGS), beside the
  null's T (c = 0) median and 95th percentile, recomputed here and checked against joint-evaluate.json;
  DESCRIPTIVE: T at the data with mu_CH replaced by mu_C (not a re-grade).

Usage: python3 mp3a_eval.py --design D --s5c-contract C --v V --frozen-eval J --build-dir B --out OUT
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
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

NULLS = {"GENIE_2_12_10_CV": "genie_cv", "GENIE_2_12_10_MEC": "genie_mec"}
C_PER_CH = 13.0 / 12.0
SIGMA_READINGS = {
    "a_sd_null_result": "SD (ddof 1) over the frozen null ensemble of the J-cell result f = Model.apply(U x) "
                        "(s5p_joint.ensemble): the spread of the unfolded pseudo-experiment result. PRIMARY (the spec's words)",
    "b_sqrt_diag_W": "sqrt(diag W), W = V + diag Var(mu_G): the frozen metric's own per-cell scale (V from the "
                     "MnvTune design pilot, not this generator's null)",
    "c_sd_null_residual": "SD (ddof 1) over the null ensemble of the simulated residual f - (mu_G + eps), eps the "
                          "statistic's own seed-keyed prediction-MC draw (s5p_joint.statistics:158)",
}
NORM_READINGS = {
    "total_W": "stat_total(mu_C, mu_CH, W^-1) = Delta' W^-1 Delta, frozen W = V + diag Var(mu_CH). PRIMARY total",
    "total_WC": "Delta' W_C^-1 Delta, W_C = V + diag Var(mu_C) (the metric if the prediction were mu_C)",
    "total_V": "Delta' V^-1 Delta (V alone, no prediction-MC term)",
    "shape_jac_data": "(q_C - q_CH)' Vs^-1 (q_C - q_CH), Vs = J W J' at the DATA f (s5p_inference.shape_parts), last cell "
                      "dropped: the quadratic form the observed T_shape uses. PRIMARY shape",
    "shape_jac_muC": "stat_shape(f = mu_C, mu = mu_CH, W): Jacobian at mu_C",
    "shape_jac_muCH": "stat_shape(f = mu_CH, mu = mu_C, W): Jacobian at mu_CH",
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
    res = {"schema": "mp3a-eval/1", "argv": sys.argv, "modules": {n: {"file": p, "sha256": sha256(p)} for n, p in mods.items()},
           "numpy": np.__version__, "python": sys.version, "sigma_readings": SIGMA_READINGS,
           "norm_readings": NORM_READINGS, "inputs": {}, "tests": {}}
    design = json.loads(a.design.read_text())
    res["inputs"]["design_sha256"] = sha256(a.design)
    res["inputs"]["s5c_contract_sha256"] = sha256(a.s5c_contract)
    res["inputs"]["v_sha256"] = sha256(a.v)
    res["inputs"]["frozen_eval_sha256"] = sha256(a.frozen_eval)
    sj.check_v(design, a.v)
    V = np.asarray(np.load(a.v, allow_pickle=False)["V"], float)
    supported = json.loads(a.s5c_contract.read_text())["measurement"]["partition_J"]["supported_cells"]
    U, names, pz_index = sj.j_matrix({}, supported)
    model = sj.Model(design, U)
    frozen = json.loads(a.frozen_eval.read_text())
    if frozen["names"] != names:
        raise SystemExit("J cell names differ from the frozen evaluation's")
    cmap, _ = s1.coarse_map(s1.J_EDGES, supported)
    vol = s1.fine_volume()
    fine_shape = s1.fine_shape()
    iW_fine = np.unravel_index(np.arange(vol.size), fine_shape)[4]
    jidx = [np.unravel_index(c, (3, 3, 3, 3, 3)) for c in supported]
    edges = [{ax: (s1.J_EDGES[ax][i[k]], s1.J_EDGES[ax][i[k] + 1]) for k, ax in enumerate(s1.AXES)} for i in jidx]
    rows = {n: {"cell": i, "name": n, **{f"{ax}_lo": e[ax][0] for ax in s1.AXES}, **{f"{ax}_hi": e[ax][1] for ax in s1.AXES}}
            for i, (n, e) in enumerate(zip(names, edges))}

    for key, gen in NULLS.items():
        spec = design["nulls"][key]
        out = {"prediction": spec["prediction"], "prediction_sha256": sha256(spec["prediction"])}
        mu, var = sj.prediction(spec["prediction"], U)
        fz = np.load(a.build_dir / f"mp3a_fine_{gen}.npz")
        out["control_J_rebuilt_vs_frozen"] = rel(U @ fz["xsec_CH_rebuilt"], mu)
        Cp, Hp, Op = (U @ fz[f"xsec_{k}"] for k in ("C12", "H1", "other"))
        vC, vH = (U ** 2) @ fz["sumw2_C12"], (U ** 2) @ fz["sumw2_H1"]
        out["split_closure_J"] = rel(Cp + Hp + Op, mu)
        mu_C = C_PER_CH * Cp
        var_C = C_PER_CH ** 2 * vC
        f_H, f_O = Hp / mu, Op / mu
        r = mu_C / mu
        r_shape = (mu_C / mu_C.sum()) / (mu / mu.sum())
        S = Cp + Hp
        sd_r = C_PER_CH * np.sqrt((Hp / S ** 2) ** 2 * vC + (Cp / S ** 2) ** 2 * vH)  # delta method, C and H independent
        delta = mu_C - mu

        files = sj.product_files(spec["calibration_glob"])
        B = sj.calibration_count(spec)
        if len(files) != B:
            raise SystemExit(f"{key}: {len(files)} calibration products, {B} declared")
        F, seeds = sj.ensemble(model, files)
        dom = np.ones(len(names), bool) if spec.get("domain") != "pz_lt_6" else (pz_index <= 1)
        tt_o, ts_o = sj.statistics(model.f_data[None, :], mu, var, V, dom, 0, draw=False)
        tt_n, ts_n = sj.statistics(F, mu, var, V, dom, spec["surrogate_seed0"], seeds=seeds)
        fe = frozen["tests"][key]
        f0 = fe["variants"]["0.0"]
        out["control_frozen_statistic"] = {
            "B": int(len(files)), "B_frozen": f0["total"]["B"],
            "T_total_obs": [float(tt_o[0]), fe["T_total_obs"]], "T_shape_obs": [float(ts_o[0]), fe["T_shape_obs"]],
            "null_T_total_median": [float(np.median(tt_n)), f0["null_T_total_median"]],
            "null_T_shape_median": [float(np.median(ts_n)), f0["null_T_shape_median"]],
            "null_T_total_sd": [float(np.std(tt_n)), f0["null_T_total_sd"]],
            "null_T_shape_sd": [float(np.std(ts_n)), f0["null_T_shape_sd"]],
            "k_total_c0": [int(np.sum(tt_n >= tt_o[0])), f0["total"]["k"]],
            "k_shape_c0": [int(np.sum(ts_n >= ts_o[0])), f0["shape"]["k"]]}
        out["control_frozen_statistic"]["max_rel_diff"] = max(
            abs(v[0] - v[1]) / abs(v[1]) for k, v in out["control_frozen_statistic"].items()
            if isinstance(v, list) and v[1] != 0)

        # sigma readings
        sd_a = F.std(0, ddof=1)
        W = V + np.diag(var)
        sd_b = np.sqrt(np.diag(W))
        eps = np.array([np.random.default_rng([int(spec["surrogate_seed0"]), int(s), 0x4A02]).normal(size=mu.size)
                        for s in seeds]) * np.sqrt(var)
        sd_c = (F - (mu + eps)).std(0, ddof=1)
        z = {"a_sd_null_result": delta / sd_a, "b_sqrt_diag_W": delta / sd_b, "c_sd_null_residual": delta / sd_c}
        P = F / F.sum(1, keepdims=True)
        dq = mu_C / mu_C.sum() - mu / mu.sum()
        z_shape = dq / P.std(0, ddof=1)
        out["sd_ratio_b_over_a"] = q(sd_b / sd_a)
        out["sd_ratio_c_over_a"] = q(sd_c / sd_a)
        out["null_mean_minus_mu_over_sd_a"] = q((F.mean(0) - mu) / sd_a)

        # metric norms
        Wd = W[np.ix_(dom, dom)]
        Winv = np.linalg.inv(Wd)
        WC = V[np.ix_(dom, dom)] + np.diag(var_C[dom])
        Vd = V[np.ix_(dom, dom)]
        p_d, Vs = si.shape_parts(model.f_data[dom], Wd)
        dqd = (mu_C[dom] / mu_C[dom].sum() - mu[dom] / mu[dom].sum())[:-1]
        norms = {"total_W": si.stat_total(mu_C[dom], mu[dom], Winv),
                 "total_WC": si.stat_total(mu_C[dom], mu[dom], np.linalg.inv(WC)),
                 "total_V": si.stat_total(mu_C[dom], mu[dom], np.linalg.inv(Vd)),
                 "shape_jac_data": float(dqd @ np.linalg.solve(Vs[:-1, :-1], dqd)),
                 "shape_jac_muC": si.stat_shape(mu_C[dom], mu[dom], Wd),
                 "shape_jac_muCH": si.stat_shape(mu[dom], mu_C[dom], Wd)}
        nullT = {s: {"median": float(np.median(t)), "p95": float(np.quantile(t, 0.95)), "sd": float(np.std(t)),
                     "min": float(t.min()), "max": float(t.max())} for s, t in (("total", tt_n), ("shape", ts_n))}
        # DESCRIPTIVE: the observed statistic with mu_CH replaced by mu_C (not a re-grade)
        ttC, tsC = sj.statistics(model.f_data[None, :], mu_C, var, V, dom, 0, draw=False)
        ttC2, tsC2 = sj.statistics(model.f_data[None, :], mu_C, var_C, V, dom, 0, draw=False)
        rr = (model.f_data - mu)[dom]
        cross = float(-2.0 * rr @ Winv @ delta[dom])
        out["metric_norms"] = norms
        out["null_T_c0"] = nullT
        out["descriptive_T_at_data_with_mu_C"] = {
            "label": "DESCRIPTIVE, not a re-grade (BINDING D6; A7 stands)",
            "metric_frozen_W_CH": {"T_total": float(ttC[0]), "T_shape": float(tsC[0])},
            "metric_W_C": {"T_total": float(ttC2[0]), "T_shape": float(tsC2[0])},
            "T_obs_frozen_recomputed": {"T_total": float(tt_o[0]), "T_shape": float(ts_o[0])},
            "total_decomposition": {"cross_term_-2r'W^-1Delta": cross, "Delta'W^-1Delta": norms["total_W"],
                                    "sum": cross + norms["total_W"], "T_C_minus_T_CH": float(ttC[0] - tt_o[0])}}

        # integrated and regional summaries
        def region(m):
            return {"n_cells": int(m.sum()), "mu_CH_sum_cm2": float(mu[m].sum()), "mu_C_sum_cm2": float(mu_C[m].sum()),
                    "r_sum": float(mu_C[m].sum() / mu[m].sum()), "f_H_sum": float(Hp[m].sum() / mu[m].sum()),
                    "r_shape_sum": float((mu_C[m].sum() / mu_C.sum()) / (mu[m].sum() / mu.sum())),
                    "r_cells": q(r[m]), "r_shape_cells": q(r_shape[m]), "f_H_cells": q(f_H[m]),
                    **{f"z_{k}": q(v[m]) for k, v in z.items()}, "z_shape": q(z_shape[m])}
        Wj = np.array([i[4] for i in jidx])
        Ej = np.array([i[2] for i in jidx])
        regs = {"all_109": np.ones(len(names), bool)}
        for j in range(3):
            regs[f"W_J{j} [{s1.J_EDGES['W'][j]},{s1.J_EDGES['W'][j+1]})"] = Wj == j
        for j in range(3):
            regs[f"Eavail_J{j} [{s1.J_EDGES['eavail'][j]},{s1.J_EDGES['eavail'][j+1]})"] = Ej == j
        out["regions_J"] = {k: region(m) for k, m in regs.items()}
        # fine-W regions inside the reported cells (the r5 W0/W1 bins are fine W bins inside J's W < 1.4)
        fw = {}
        for j in range(fine_shape[4]):
            m = (cmap >= 0) & (iW_fine == j)
            tot = float((fz["xsec_CH_rebuilt"][m] * vol[m]).sum())
            c = float((fz["xsec_C12"][m] * vol[m]).sum())
            h = float((fz["xsec_H1"][m] * vol[m]).sum())
            fw[f"W{j} [{s1.FINE['W'][j]},{s1.FINE['W'][j+1]})"] = {"Conly_over_CH_per_nucleon": C_PER_CH * c / tot, "f_H": h / tot}
        tot = float((fz["xsec_CH_rebuilt"][cmap >= 0] * vol[cmap >= 0]).sum())
        ctot = (fz["xsec_C12"][cmap >= 0] * vol[cmap >= 0]).sum()
        for k in fw:
            fw[k]["rel_to_reported_total"] = fw[k]["Conly_over_CH_per_nucleon"] / float(C_PER_CH * ctot / tot)
        out["fine_W_regions_in_reported_cells"] = fw
        out["largest_cells"] = {
            "abs_z_a_top10": [names[i] for i in np.argsort(-np.abs(z["a_sd_null_result"]))[:10]],
            "abs_r_minus_1_top10": [names[i] for i in np.argsort(-np.abs(r - 1))[:10]],
            "abs_r_shape_minus_1_top10": [names[i] for i in np.argsort(-np.abs(r_shape - 1))[:10]]}
        out["cells"] = {"mu_CH": mu.tolist(), "var_mu_CH": var.tolist(), "mu_C": mu_C.tolist(), "var_mu_C": var_C.tolist(),
                        "f_H": f_H.tolist(), "f_other": f_O.tolist(), "r": r.tolist(), "sd_r_mc": sd_r.tolist(),
                        "r_shape": r_shape.tolist(), "delta": delta.tolist(), "sd_a": sd_a.tolist(), "sd_b": sd_b.tolist(),
                        "sd_c": sd_c.tolist(), **{f"z_{k}": v.tolist() for k, v in z.items()}, "z_shape": z_shape.tolist()}
        tag = "CV" if gen == "genie_cv" else "MEC"
        for i, n in enumerate(names):
            rows[n].update({f"f_H_{tag}": f_H[i], f"r_{tag}": r[i], f"sd_r_mc_{tag}": sd_r[i], f"r_shape_{tag}": r_shape[i],
                            f"z_{tag}": z["a_sd_null_result"][i], f"z_sqrtdiagW_{tag}": z["b_sqrt_diag_W"][i],
                            f"z_resid_{tag}": z["c_sd_null_residual"][i], f"z_shape_{tag}": z_shape[i],
                            f"f_other_{tag}": f_O[i]})
        res["tests"][key] = out
        print(key, json.dumps({k: out[k] for k in ("control_J_rebuilt_vs_frozen", "split_closure_J", "control_frozen_statistic",
                                                   "metric_norms", "null_T_c0")}), flush=True)

    a.out.mkdir(parents=True, exist_ok=True)
    cols = list(next(iter(rows.values())).keys())
    with open(a.out / "mp3a_cells.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for n in names:
            w.writerow({k: (f"{v:.10g}" if isinstance(v, float) else v) for k, v in rows[n].items()})
    ru = resource.getrusage(resource.RUSAGE_SELF)
    res["cpu_s"], res["maxrss_kb"], res["wall_s"] = ru.ru_utime + ru.ru_stime, ru.ru_maxrss, time.time() - t0
    (a.out / "mp3a_results.json").write_text(json.dumps(res, indent=1) + "\n")
    ok = all(t["control_J_rebuilt_vs_frozen"]["bitwise_equal"] or t["control_J_rebuilt_vs_frozen"]["max_rel_diff"] <= 1e-10
             for t in res["tests"].values())
    print("CONTROL_J", ok)
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
