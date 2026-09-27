#!/usr/bin/env python3
"""s5p pre-freeze measurements with the frozen metric V, WITHOUT any observed-data statistic.

``units``: for each external null G, the non-centrality of its null T and the sizes of the declared residuals in
null-T units, from the noise-free full-MC asimovs (review round 2 M1; confirmation review F5): with
b = f_asimov(fine null) - mu_G on the test domain and W = V + diag Var(mu_G), lambda = b' W^-1 b; a shift delta of the
null ensemble moves T by dT ~ 2 b' W^-1 delta + delta' W^-1 delta, and the null T's SD is ~ sqrt(2 n + 4 lambda)
(a non-central chi-square approximation); reported for delta = F2 (coarse vs fine), M1 (fine vs merged-x2), 2 M1
(the claim variant), 3 M1 (the robustness variant) and the D16 bias-aligned upper bound.

``devpower``: the design pilot's development power: the P1r-P3r ensembles against the pilot's MnvTune-null
ensemble (the draws that built V: optimistic), at 0.05 and 0.005, rank rule and the determinacy rule, for the total
and the shape test. The data are never read.

MEASURES: pre-freeze descriptive numbers. CANNOT AUTHORIZE: a claim or a change of the frozen rules.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import s5p_inference as si
import s5p_joint as sj


def cells_of(path: str, U: np.ndarray) -> np.ndarray:
    return U @ sj.xs(path)


def units(design: dict, V: np.ndarray, U: np.ndarray, pz_index: np.ndarray, asim: dict) -> dict:
    out = {}
    for key, g in asim["generators"].items():
        spec = design["nulls"][key]
        mu, var = sj.prediction(spec["prediction"], U)
        dom = np.ones(U.shape[0], bool) if spec.get("domain") != "pz_lt_6" else (pz_index <= 1)
        W = V[np.ix_(dom, dom)] + np.diag(var[dom])
        Wi = np.linalg.inv(W)
        fine, coarse, mid = (cells_of(g[k], U) for k in ("fine", "coarse", "mid"))
        b = (fine - mu)[dom]
        lam = float(b @ Wi @ b)
        n = int(dom.sum())
        sd = float(np.sqrt(2 * n + 4 * lam))
        def dT(delta):
            d = delta[dom]
            return float((2 * b @ Wi @ d + d @ Wi @ d) / sd)
        e = {"domain_cells": n, "lambda": lam, "null_T_sd_approx": sd,
             "F2_coarse_minus_fine": dT(coarse - fine), "M1_mid_minus_fine": dT(mid - fine),
             "M1_claim_variant_2x": max(dT(2 * (fine - mid)), dT(-2 * (fine - mid))),
             "M1_robust_variant_3x": max(dT(3 * (fine - mid)), dT(-3 * (fine - mid)))}
        pspec = design["process_shift"][key]
        D, pairs = sj.load_shift(pspec, U.shape[0])
        # the bias-aligned upper bound along b (the evaluator uses the calibration mean; the asimov bias stands in here)
        u = b / np.sqrt(lam) if lam > 0 else np.zeros_like(b)
        a_j = np.array([dj[dom] @ Wi @ u for dj in pairs])
        m = max(a_j.mean() + 2 * a_j.std(ddof=1) / np.sqrt(len(a_j)), 0.0)
        S = np.zeros(U.shape[0])
        S[dom] = m * u
        e["D16_bias_aligned_upper"] = dT(S)
        e["D16_a_over_se"] = float(a_j.mean() / (a_j.std(ddof=1) / np.sqrt(len(a_j))))
        out[key] = e
    return out


def devpower(design: dict, V: np.ndarray, U: np.ndarray, model: sj.Model, pilot: dict) -> dict:
    spec = design["nulls"]["MnvTune_v1"]
    mu, var = sj.prediction(spec["prediction"], U)
    dom = np.ones(U.shape[0], bool)
    F0, s0 = sj.ensemble(model, sj.product_files(pilot["null_glob"]))
    tt0, ts0 = sj.statistics(F0, mu, var, V, dom, 101, seeds=s0)
    out = {"null_n": int(len(F0))}
    for key, g in pilot["alternatives"].items():
        Fa, sa = sj.ensemble(model, sj.product_files(g))
        tta, tsa = sj.statistics(Fa, mu, var, V, dom, 202, seeds=sa)
        out[key] = {"n": int(len(Fa))}
        for s, ta, tn in (("total", tta, tt0), ("shape", tsa, ts0)):
            out[key][s] = {str(al): {"rank": si.power(ta, tn, al), "determined": si.power_determined(ta, [tn], al)}
                           for al in (0.05, 0.005)}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("cmd", choices=("units", "devpower"))
    ap.add_argument("--design", type=Path, required=True)
    ap.add_argument("--v", type=Path, required=True)
    ap.add_argument("--inputs", type=Path, required=True, help="JSON: asimov products per generator (units) or pilot globs (devpower)")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    design = json.loads(a.design.read_text())
    stage1 = json.loads(Path(design["stage1"]).read_text())
    supported = json.loads(Path(design["s5c_contract"]).read_text())["measurement"]["partition_J"]["supported_cells"]
    U, names, pz_index = sj.j_matrix(stage1, supported)
    V = np.asarray(np.load(a.v, allow_pickle=False)["V"], float)
    inp = json.loads(a.inputs.read_text())
    if a.cmd == "units":
        res = units(design, V, U, pz_index, inp)
    else:
        res = devpower(design, V, U, sj.Model(design, U), inp)
    res = {"schema": f"s5p-prefreeze-{a.cmd}/1", "design_sha256": sj.sha256(a.design), "v_sha256": sj.sha256(a.v),
           "inputs": inp, "code_sha256": sj.sha256(Path(__file__).resolve()), "result": res}
    a.out.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res["result"], indent=1)[:4000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
