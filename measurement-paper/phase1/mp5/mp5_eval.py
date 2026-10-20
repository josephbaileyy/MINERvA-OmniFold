#!/usr/bin/env python3
"""MP-5 step 3: the J-cell readouts of the two definitional mismatches (BINDING-PHASE1-ADDENDUM-1 section 3 and the
director's MP-5(a) amendment), read out like MP3-A through s5p_joint's own functions (frozen 4f5a613f copies).

(a) truth muon-angle axis. R_c = T_beam(c) / T_nu(c), the analysis-MC (MnvTune v1) J-cell truth content with theta
    from the fixed MAT beam axis over that with theta from the true nu direction (mp5_tune.py). It is a PROXY for each
    generator's own migration: Delta_c = mu_G(c) (R_c - 1) for GENIE CV, GENIE MEC, NuWro and GiBUU. MnvTune v1's
    Delta is zero by construction (its prediction is the beam-axis analysis truth; control T3 and the J-level control
    here). CHECK (GENIE CV only): the rebuilt beam-axis GENIE CV prediction (mp5_genie.py) against mu_G R_c.
(b) generator W convention. Delta_c = mu_G(c) s_c with s_c the M4-W record's own per-cell shift (probe_gen.json
    per_cell_rel_weighted), GENIE CV and NuWro.
Readout per Delta: Delta/sigma_c in three readings (MP3-A section 4.1: (a) null-result SD PRIMARY, (b) sqrt diag W,
(c) null-residual SD), Delta' W^-1 Delta under the frozen W (PRIMARY), the shape form at the data's Jacobian, the
null's T (c = 0) median / 95th percentile / SD recomputed and checked against joint-evaluate.json, and the
DESCRIPTIVE observed T with mu_G replaced by mu_G + Delta (not a re-grade). Descriptive throughout; no gate.
Usage: python3 mp5_eval.py --design D --s5c-contract C --v V --frozen-eval J --tune T --genie G --m4w-gen P
       --declaration X --out OUT
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

PROXY_NULLS = ["GENIE_2_12_10_CV", "GENIE_2_12_10_MEC", "NuWro_21_09", "GiBUU_2019"]
W_NULLS = {"GENIE_2_12_10_CV": "genie_cv", "NuWro_21_09": "nuwro"}
TAG = {"GENIE_2_12_10_CV": "CV", "GENIE_2_12_10_MEC": "MEC", "NuWro_21_09": "NuWro", "GiBUU_2019": "GiBUU"}


def sha256(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def q(x):
    x = np.asarray(x, float)
    return {"min": float(x.min()), "median": float(np.median(x)), "max": float(x.max())}


def rel(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    nz = b != 0
    return {"bitwise_equal": bool(np.array_equal(a, b)),
            "max_rel_diff": float(np.max(np.abs(a[nz] - b[nz]) / np.abs(b[nz]))) if nz.any() else 0.0}


class Null:
    """One generator null: its frozen prediction, calibration ensemble, metric and null T (c = 0), checked bitwise."""

    def __init__(self, key, design, model, V, names, pz_index, frozen):
        spec = design["nulls"][key]
        self.key, self.spec = key, spec
        self.mu, self.var = sj.prediction(spec["prediction"], model.U)
        self.dom = np.ones(len(names), bool) if spec.get("domain") != "pz_lt_6" else (pz_index <= 1)
        files = sj.product_files(spec["calibration_glob"])
        if len(files) != sj.calibration_count(spec):
            raise SystemExit(f"{key}: {len(files)} calibration products, {sj.calibration_count(spec)} declared")
        F, seeds = sj.ensemble(model, files)
        tt_o, ts_o = sj.statistics(model.f_data[None, :], self.mu, self.var, V, self.dom, 0, draw=False)
        tt_n, ts_n = sj.statistics(F, self.mu, self.var, V, self.dom, spec["surrogate_seed0"], seeds=seeds)
        fe = frozen["tests"][key]
        f0 = fe["variants"]["0.0"]
        c = {"B": [int(len(files)), f0["total"]["B"]], "T_total_obs": [float(tt_o[0]), fe["T_total_obs"]],
             "T_shape_obs": [float(ts_o[0]), fe["T_shape_obs"]],
             "null_T_total_median": [float(np.median(tt_n)), f0["null_T_total_median"]],
             "null_T_shape_median": [float(np.median(ts_n)), f0["null_T_shape_median"]],
             "null_T_total_sd": [float(np.std(tt_n)), f0["null_T_total_sd"]],
             "null_T_shape_sd": [float(np.std(ts_n)), f0["null_T_shape_sd"]],
             "k_total_c0": [int(np.sum(tt_n >= tt_o[0])), f0["total"]["k"]],
             "k_shape_c0": [int(np.sum(ts_n >= ts_o[0])), f0["shape"]["k"]]}
        c["bitwise"] = all(v[0] == v[1] for v in c.values())
        c["max_rel_diff"] = max(abs(v[0] - v[1]) / abs(v[1]) for k, v in c.items() if isinstance(v, list) and v[1] != 0)
        c["pass"] = c["k_total_c0"][0] == c["k_total_c0"][1] and c["k_shape_c0"][0] == c["k_shape_c0"][1] \
            and c["B"][0] == c["B"][1] and c["max_rel_diff"] <= 1e-9
        self.control = c
        self.F, self.seeds, self.tt_o, self.ts_o = F, seeds, float(tt_o[0]), float(ts_o[0])
        self.nullT = {s: {"median": float(np.median(t)), "p95": float(np.quantile(t, 0.95)), "sd": float(np.std(t))}
                      for s, t in (("total", tt_n), ("shape", ts_n))}
        W = V + np.diag(self.var)
        eps = np.array([np.random.default_rng([int(spec["surrogate_seed0"]), int(s), 0x4A02]).normal(size=self.mu.size)
                        for s in seeds]) * np.sqrt(self.var)
        self.sd = {"a_sd_null_result": F.std(0, ddof=1), "b_sqrt_diag_W": np.sqrt(np.diag(W)),
                   "c_sd_null_residual": (F - (self.mu + eps)).std(0, ddof=1)}
        d = self.dom
        self.Wd = W[np.ix_(d, d)]
        self.Winv = np.linalg.inv(self.Wd)
        _, self.Vs = si.shape_parts(model.f_data[d], self.Wd)
        self.model, self.V = model, V

    def readout(self, delta, label):
        d = self.dom
        mu2 = self.mu + delta
        z = {k: delta / v for k, v in self.sd.items()}
        dq = (mu2[d] / mu2[d].sum() - self.mu[d] / self.mu[d].sum())[:-1]
        tt, ts = sj.statistics(self.model.f_data[None, :], mu2, self.var, self.V, d, 0, draw=False)
        rr = (self.model.f_data - self.mu)[d]
        cross = float(-2.0 * rr @ self.Winv @ delta[d])
        nt = si.stat_total(mu2[d], self.mu[d], self.Winv)
        return {"label": label, "domain_cells": int(d.sum()),
                "z_on_domain": {k: q(v[d]) for k, v in z.items()},
                "n_abs_z_a_gt": {t: int(np.sum(np.abs(z["a_sd_null_result"][d]) > t)) for t in (0.1, 0.2, 0.5, 1.0)},
                "sum_z_a_sq_on_domain": float(np.sum(z["a_sd_null_result"][d] ** 2)),
                "rel_shift_on_domain": q((delta / self.mu)[d]),
                "norms": {"total_W": nt, "shape_jac_data": float(dq @ np.linalg.solve(self.Vs[:-1, :-1], dq))},
                "null_T_c0": self.nullT,
                "norm_over_null_T_median": {"total": nt / self.nullT["total"]["median"]},
                "descriptive_T_at_data_with_mu_plus_delta": {
                    "label": "DESCRIPTIVE, not a re-grade (A7 stands)",
                    "T_total": float(tt[0]), "T_shape": float(ts[0]), "T_total_frozen": self.tt_o, "T_shape_frozen": self.ts_o,
                    "change_over_null_sd": {"total": (float(tt[0]) - self.tt_o) / self.nullT["total"]["sd"],
                                            "shape": (float(ts[0]) - self.ts_o) / self.nullT["shape"]["sd"]},
                    "total_decomposition": {"cross_term": cross, "norm": nt, "sum": cross + nt,
                                            "T_change": float(tt[0]) - self.tt_o}},
                "_z": z}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    for k in ("design", "s5c-contract", "v", "frozen-eval", "tune", "genie", "m4w-gen", "declaration", "out"):
        ap.add_argument(f"--{k}", type=Path, required=True)
    a = ap.parse_args(argv)
    t0 = time.time()
    mods = {m.__name__: str(Path(m.__file__).resolve()) for m in (si, sj, s1)}
    for n, p in mods.items():
        print("module", n, p, flush=True)
        if Path(p).parent != HERE:
            raise SystemExit(f"{n} imported from {p}, not from {HERE}")
    res = {"schema": "mp5-eval/1", "argv": sys.argv, "modules": {n: {"file": p, "sha256": sha256(p)} for n, p in mods.items()},
           "numpy": np.__version__, "python": sys.version, "inputs": {}, "controls": {}, "a": {}, "b": {}}
    for k in ("design", "s5c_contract", "v", "frozen_eval", "tune", "genie", "m4w_gen", "declaration"):
        res["inputs"][k] = {"path": str(getattr(a, k)), "sha256": sha256(getattr(a, k))}
    design = json.loads(a.design.read_text())
    sj.check_v(design, a.v)
    V = np.asarray(np.load(a.v, allow_pickle=False)["V"], float)
    supported = json.loads(a.s5c_contract.read_text())["measurement"]["partition_J"]["supported_cells"]
    U, names, pz_index = sj.j_matrix({}, supported)
    model = sj.Model(design, U)
    frozen = json.loads(a.frozen_eval.read_text())
    if frozen["names"] != names:
        raise SystemExit("J cell names differ from the frozen evaluation's")
    cmap, ncell = s1.coarse_map(s1.J_EDGES, supported)
    jidx = [np.unravel_index(c, (3, 3, 3, 3, 3)) for c in supported]
    rows = {n: {"cell": i, "name": n, **{f"{ax}_lo": s1.J_EDGES[ax][jj[k]] for k, ax in enumerate(s1.AXES)},
                **{f"{ax}_hi": s1.J_EDGES[ax][jj[k] + 1] for k, ax in enumerate(s1.AXES)}}
            for i, (n, jj) in enumerate(zip(names, jidx))}

    # ---- R_c and its MC error (migrating events only)
    T = np.load(a.tune)
    Tb, Tn = np.asarray(T["J_Tb"], float), np.asarray(T["J_Tn"], float)
    R = Tb / Tn
    R_stored = np.asarray(T["J_Tb_stored"], float) / Tn
    sd_R = np.sqrt(T["J_w2_out"] + T["J_w2_in"]) / Tn
    res["a"]["R_c"] = {"definition": "T_beam / T_nu, both recomputed from the MAD branches (T4); R_stored uses the "
                                     "stored analysis truth for T_beam", "R": q(R), "R_minus_1_abs": q(np.abs(R - 1)),
                       "R_stored_minus_R_maxabs": float(np.max(np.abs(R_stored - R))), "sd_R_mc": q(sd_R),
                       "abs_R_minus_1_over_sd": q(np.abs(R - 1) / np.where(sd_R > 0, sd_R, np.inf)),
                       "n_moved_out_in": [q(T["J_n_out"]), q(T["J_n_in"])],
                       "integrated_ratio": float(Tb.sum() / Tn.sum()),
                       "top10_abs_R_minus_1": [names[i] for i in np.argsort(-np.abs(R - 1))[:10]]}

    # ---- MnvTune v1: its prediction IS the beam-axis truth content (J-level statement of control T3)
    mu_mnv, _ = sj.prediction(design["nulls"]["MnvTune_v1"]["prediction"], U)
    res["controls"]["mnvtune_J_from_beam_axis_content"] = rel(U @ np.asarray(T["mnv_xsec_from_beam"], float), mu_mnv)
    res["controls"]["mnvtune_J_bitwise"] = bool(np.array_equal(U @ np.asarray(T["mnv_xsec_from_beam"], float), mu_mnv))

    nulls = {}
    for key in PROXY_NULLS:
        nulls[key] = Null(key, design, model, V, names, pz_index, frozen)
        res["controls"][f"frozen_statistic_{key}"] = nulls[key].control
        print(key, "frozen statistic bitwise", nulls[key].control["bitwise"], flush=True)
    # E1 (coordinator's GO rule): a null whose frozen statistic does not reproduce is STOPPED (no readout); the others go on
    failed = [k for k, n in nulls.items() if not n.control["pass"]]
    res["E1_stopped_nulls"] = failed
    for k in failed:
        del nulls[k]
    if "GENIE_2_12_10_CV" in failed and "GENIE_2_12_10_MEC" in failed:
        res["stop"] = "the frozen GENIE statistics did not reproduce"
        return finish(res, a.out, t0, rows, names, 3)

    def put(tag, z, extra=None):
        for i, n in enumerate(names):
            rows[n].update({f"z_{tag}": z["a_sd_null_result"][i], f"z_sqrtdiagW_{tag}": z["b_sqrt_diag_W"][i],
                            f"z_resid_{tag}": z["c_sd_null_residual"][i]})
            for k, v in (extra or {}).items():
                rows[n][f"{k}_{tag}"] = v[i]

    for i, n in enumerate(names):
        rows[n].update({"R": R[i], "sd_R_mc": sd_R[i], "R_stored": R_stored[i]})
    # ---- (a) the proxy, four generators
    for key, N in nulls.items():
        delta = N.mu * (R - 1.0)
        r = N.readout(delta, f"(a) proxy: mu_G (R_c - 1), {key}")
        z = r.pop("_z")
        r["mc_error_of_z_a_from_R"] = q((N.mu * sd_R / N.sd["a_sd_null_result"])[N.dom])
        r["top5_abs_z_a"] = [names[i] for i in np.argsort(-np.abs(np.where(N.dom, z["a_sd_null_result"], 0)))[:5]]
        res["a"][key] = r
        put(f"a_{TAG[key]}", z, {"delta": delta})

    # ---- the check, GENIE CV: the beam-axis rebuild against mu_G R_c
    if "GENIE_2_12_10_CV" not in nulls:
        res["a"]["check_GENIE_CV"] = "STOPPED: E1 failed for GENIE CV"
        return finish(res, a.out, t0, rows, names, 3)
    G = np.load(a.genie)
    N = nulls["GENIE_2_12_10_CV"]
    mu_unrot = U @ np.asarray(G["xsec_unrot_full"], float)
    mu_beam = U @ np.asarray(G["xsec_beam_full"], float)
    res["controls"]["genie_unrot_J_equals_frozen_prediction"] = rel(mu_unrot, N.mu)
    sig = N.sd["a_sd_null_result"]
    dchk = mu_beam - N.mu * R
    noise = np.sqrt(G["J_var_out"] + G["J_var_in"] + (N.mu * sd_R) ** 2)
    dz = dchk / sig
    worst = int(np.argmax(np.abs(dz)))
    decl = json.loads(a.declaration.read_text())
    thr = float(decl["proxy_check_threshold"]["threshold"])
    res["a"]["check_GENIE_CV"] = {
        "quantity": "(mu_G,beam - mu_G R_c) / sigma_c(a)", "threshold": thr,
        "max_abs": float(np.abs(dz).max()), "cell_of_max": names[worst], "median_abs": float(np.median(np.abs(dz))),
        "n_cells_above_threshold": int(np.sum(np.abs(dz) > thr)),
        "cells_above_threshold": [names[i] for i in np.where(np.abs(dz) > thr)[0]],
        "proxy_label_for_MEC_NuWro_GiBUU": "UNRELIABLE" if np.any(np.abs(dz) > thr) else "not contradicted by the GENIE CV check",
        "difference_over_its_MC_noise": q((dchk / np.where(noise > 0, noise, np.inf))[noise > 0]),
        "n_cells_zero_noise": int(np.sum(noise == 0)), "genie_native_R": q(mu_beam / N.mu),
        "corr_genie_native_R_minus_1_vs_proxy": float(np.corrcoef(mu_beam / N.mu - 1, R - 1)[0, 1]),
        "genie_beam_migration_n_out_in": [q(G["J_n_out"]), q(G["J_n_in"])]}
    r = N.readout(mu_beam - N.mu, "(a) GENIE CV native: mu_G,beam - mu_G (the check's own Delta)")
    z = r.pop("_z")
    res["a"]["GENIE_CV_native"] = r
    put("a_CVnative", z, {"check_dz": dz, "check_noise_over_sigma": noise / sig})

    # ---- (b) the W convention, the record's own per-cell shift
    m4 = json.loads(a.m4w_gen.read_text())
    for key, g in W_NULLS.items():
        pc = m4[g]["per_cell_rel_weighted"]
        if [int(k) for k in pc] != [int(c) for c in supported]:
            raise SystemExit(f"{g}: the record's cells are not the contract's supported cells")
        s = np.array([pc[str(c)] for c in supported], float)
        fw = m4[g]["flux_fix_weighted"]
        res["controls"][f"m4w_record_reproduces_its_summaries_{g}"] = {
            "median_abs": [float(np.median(np.abs(s))), fw["median_abs_rel"]],
            "max_abs": [float(np.abs(s).max()), fw["max_abs_rel"]],
            "argmax_cell": [int(supported[int(np.argmax(np.abs(s)))]), fw["argmax_cell"]],
            "n_gt_1e-3": [int(np.sum(np.abs(s) > 1e-3)), fw["n_cells_abs_rel_gt_1e-3"]]}
        cc = res["controls"][f"m4w_record_reproduces_its_summaries_{g}"]
        cc["pass"] = all(v[0] == v[1] for v in cc.values())
        if key not in nulls:
            res["b"][key] = "STOPPED: E1 failed"
            continue
        N = nulls[key]
        r = N.readout(N.mu * s, f"(b) W convention: mu_G s_c (M4-W per_cell_rel_weighted), {key}")
        z = r.pop("_z")
        res["b"][key] = r
        put(f"b_{TAG[key]}", z, {"s": s})
    return finish(res, a.out, t0, rows, names, 0 if not failed else 5)


def finish(res, out, t0, rows, names, rc):
    out.mkdir(parents=True, exist_ok=True)
    cols = []
    for n in names:
        cols += [k for k in rows[n] if k not in cols]
    with open(out / "mp5_cells.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for n in names:
            w.writerow({k: (f"{v:.10g}" if isinstance(v, (float, np.floating)) else v) for k, v in rows[n].items()})
    ru = resource.getrusage(resource.RUSAGE_SELF)
    res["cpu_s"], res["maxrss_kb"], res["wall_s"], res["exit"] = ru.ru_utime + ru.ru_stime, ru.ru_maxrss, time.time() - t0, rc
    (out / "mp5_results.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    print("EVAL_CONTROLS", json.dumps({k: (v.get("pass", v.get("bitwise_equal")) if isinstance(v, dict) else v)
                                       for k, v in res["controls"].items()}), "exit", rc, flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
