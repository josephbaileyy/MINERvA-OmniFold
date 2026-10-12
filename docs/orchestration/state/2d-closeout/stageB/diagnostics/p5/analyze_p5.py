#!/usr/bin/env python3
"""P5 analysis: does dividing by the miss-row completeness reproduce a correctly weighted unfold?

Rules fixed before any data (DESIGN.md §6; review-p5 finding 1).

Inputs (hXSec2D / hOFCompleteness2D, 205 reported cells = E_U hXSec2D > 0, C order over (pT, p_par)):
  a     out/xsec_MaRES_0_off<tag>.root   production driver: miss rows carry the CV proxy, then / c
  b     out/xsec_MaRES_0_on<tag>.root    driver_p5.py: miss rows carry their mc_truth_denom MaRES_0 weight
  cv    E_U uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root (4f5a1b6d...)
  j0,j1 July uq/purity_newomni/2d_xsec_MEFHC_5iter_lgbm_pn_uni_MaRES_{0,1}.root
  ml    uq/seedscan_lgbm_ml/uq_covariance_ml.root (3b6b48ec..., pinned): sigma_ML = sqrt(diag hCov2D_reported)

Gates (MEASURED requires all; otherwise INCONCLUSIVE; a scientific result is never a reason to retry):
  G-a  override report ALL_PASS with n_override = 8,999,007; run b's p5MissWeightOverride sha256 equals the npz's
  G-b  max |c_b - 1| <= 1e-9
  G-c  c_a equals the July MaRES_0 completeness to <= 1e-12 relative
  G-p  provenance: driverSha256 a = 6be77c51..., b = DIAG_SHA; omnifoldHelperSha256 equal in both and = e9623412...;
       runConfig equal apart from out and miss_weight_override; a carries no p5MissWeightOverride
  G-f  every r1 and r3 finite
Metrics (reported): d = b - a; sigma_band = |j0 - j1|/2; r1 = |d|/sigma_band; r2 = |d|/|a - cv|; r3 = |d|/sigma_ML;
  median/p84/max; integral change; Pearson and Spearman correlation across cells of d/a with (c_a - 1)
  (descriptive: G2 predicts the change tracks the completeness deviation); bridge |a - j0|/sigma_band.
Routing (descriptive, fixed now):
  r1 rule = median r1 > 0.10 over 205 cells, or max r1 > 0.30 over cells with sigma_band >= 1e-3 x CV
  MATERIAL                               iff the r1 rule holds AND median r3 > 2
  NOT RESOLVED ABOVE TRAINER NOISE       iff the r1 rule holds AND median r3 <= 2 (size criterion held, noise
                                         criterion failed)
  NOT MATERIAL                           otherwise
Conditional follow-up (DESIGN §7): a seed-43 pair, only if the seed-42 routing is MATERIAL or NOT RESOLVED, after a
  budget check (actual sacct charges + the pair's enforced 1.25 node-h <= 3.0) and the director's go-ahead.
  --confirm (refused unless --tag _s43) compares the two pairs on z = d / sigma_ML per cell, over the cells with
  sigma_band >= 1e-3 x CV: CONFIRMED iff both pairs are MEASURED and Pearson(z43, z42) >= 0.5; INCONCLUSIVE if either
  pair is not MEASURED or the correlation is not finite; NOT CONFIRMED otherwise. Spearman is reported alongside.
  Final routing (fixed before data):
    seed-42 MATERIAL      + CONFIRMED      -> MATERIAL
    seed-42 MATERIAL      + NOT CONFIRMED  -> NOT RESOLVED ABOVE TRAINER NOISE
    seed-42 NOT RESOLVED  + CONFIRMED      -> MATERIAL iff the r1 rule holds on dbar = (d42 + d43)/2;
                                              otherwise NOT MATERIAL (coherent but below the size threshold)
                                              (director ruling 2026-10-12, frozen before any seed-42 result)
    seed-42 NOT RESOLVED  + NOT CONFIRMED  -> NOT RESOLVED ABOVE TRAINER NOISE
    seed-42 NOT MATERIAL                   -> no seed-43 pair (--confirm refuses)
    any INCONCLUSIVE                       -> INCONCLUSIVE

  python analyze_p5.py <out_dir> <report.json> [--tag _s43] [--confirm]
"""
import argparse
import hashlib
import json

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
D2 = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
PN = f"{D2}/uq/purity_newomni"
ML = f"{D2}/uq/seedscan_lgbm_ml/uq_covariance_ml.root"
ML_SHA = "3b6b48ec89207ae29dc7bb0ddc5a41836c359c4805877d663731694b828d5db9"
PROD_SHA = "6be77c51805547bac2d864ce77c7bc636607cf43194bd2f4ad1a7c14db621257"
DIAG_SHA = "f71b5759bf01422fa8c6b6e5432885b34d1f127653df1165a0adb7527bdb12d2"
HELPER_SHA = "e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a"
N_MISS = 8999007


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def arr(path, name):
    f = ROOT.TFile.Open(path)
    h = f.Get(name)
    a = np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY() + 1)]
                  for i in range(1, h.GetNbinsX() + 1)])
    ar = np.array([[h.GetXaxis().GetBinWidth(i) * h.GetYaxis().GetBinWidth(j)
                    for j in range(1, h.GetNbinsY() + 1)] for i in range(1, h.GetNbinsX() + 1)])
    f.Close()
    return a, ar


def named(path):
    f = ROOT.TFile.Open(path)
    out = {}
    for k in ("runConfig", "driverSha256", "omnifoldHelperSha256", "p5MissWeightOverride"):
        o = f.Get(k)
        out[k] = o.GetTitle() if o else None
    f.Close()
    return out


def stats(v):
    return {"median": float(np.median(v)), "p84": float(np.percentile(v, 84)), "max": float(np.max(v))}


def rank(v):
    r = np.empty(v.size)
    r[np.argsort(v, kind="stable")] = np.arange(v.size)
    return r


def pair(out_dir, tag, rep):
    F = {"a": f"{out_dir}/xsec_MaRES_0_off{tag}.root", "b": f"{out_dir}/xsec_MaRES_0_on{tag}.root",
         "cv": f"{D2}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root",
         "j0": f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_MaRES_0.root",
         "j1": f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_MaRES_1.root", "ml": ML}
    rep["inputs"] = {k: {"path": p, "sha256": sha(p)} for k, p in F.items()}
    g = rep["gates"] = {}
    g["ml_pinned"] = rep["inputs"]["ml"]["sha256"] == ML_SHA
    cv2, area2 = arr(F["cv"], "hXSec2D")
    m = (cv2 > 0).ravel()
    X = {k: arr(F[k], "hXSec2D")[0].ravel()[m] for k in ("a", "b", "cv", "j0", "j1")}
    C = {k: arr(F[k], "hOFCompleteness2D")[0].ravel()[m] for k in ("a", "b", "j0")}
    area = area2.ravel()[m]
    fml = ROOT.TFile.Open(ML)
    hml = fml.Get("hCov2D_reported")
    sig_ml = np.sqrt(np.array([hml.GetBinContent(i + 1, i + 1) for i in range(hml.GetNbinsX())]))
    fml.Close()

    ovj = json.load(open(f"{out_dir}/override_MaRES_0.json"))
    ov_sha = sha(f"{out_dir}/override_MaRES_0.npz")
    na, nb = named(F["a"]), named(F["b"])
    g["G-a_override"] = bool(ovj.get("ALL_PASS")) and ovj.get("n_override") == N_MISS \
        and nb["p5MissWeightOverride"] is not None and f"sha256={ov_sha}" in nb["p5MissWeightOverride"]
    g["G-b_max_abs_c_on_minus_1"] = float(np.max(np.abs(C["b"] - 1)))
    g["G-c_max_rel_c_off_vs_july"] = float(np.max(np.abs(C["a"] / C["j0"] - 1)))
    ca = json.loads(na["runConfig"]) if na["runConfig"] else None   # absent provenance fails G-p, not the script
    cb = json.loads(nb["runConfig"]) if nb["runConfig"] else None
    strip = lambda c: None if c is None else {k: v for k, v in c.items() if k not in ("out", "miss_weight_override")}
    g["G-p_provenance"] = (ca is not None and cb is not None
                           and na["driverSha256"] == PROD_SHA and nb["driverSha256"] == DIAG_SHA
                           and na["omnifoldHelperSha256"] == nb["omnifoldHelperSha256"] == HELPER_SHA
                           and strip(ca) == strip(cb) and na["p5MissWeightOverride"] is None)
    rep["provenance"] = {"a": {k: v for k, v in na.items() if k != "runConfig"}, "b": {k: v for k, v in nb.items()
                                                                                    if k != "runConfig"},
                         "runConfig_a": ca, "runConfig_b": cb}

    d = X["b"] - X["a"]
    s_a = X["a"] - X["cv"]
    sig = np.abs(X["j0"] - X["j1"]) / 2
    floor = sig >= 1e-3 * X["cv"]
    r1, r2, r3 = np.abs(d) / sig, np.abs(d) / np.abs(s_a), np.abs(d) / sig_ml
    g["G-f_finite_r1_r3"] = bool(np.all(np.isfinite(r1)) and np.all(np.isfinite(r3)))
    x, y = d / X["a"], C["a"] - 1
    rep["metrics"] = {
        "c_off_minus_1": stats(np.abs(y)),
        "rel_change_b_over_a": stats(np.abs(x)),
        "r1_abs_d_over_sigma_band": stats(r1),
        "r1_floored_cells": stats(r1[floor]), "n_floored_cells": int(floor.sum()),
        "r2_abs_d_over_universe_shift": stats(r2),
        "r3_abs_d_over_sigma_ml": stats(r3),
        "sigma_ml_over_sigma_band_median": float(np.median(sig_ml / sig)),
        "integral_rel_change": float((d * area).sum() / (X["a"] * area).sum()),
        "corr_d_over_a_vs_c_off_minus_1": {"pearson": float(np.corrcoef(x, y)[0, 1]),
                                           "spearman": float(np.corrcoef(rank(x), rank(y))[0, 1])},
        "bridge_abs_a_minus_july_over_sigma_band": stats(np.abs(X["a"] - X["j0"]) / sig),
    }
    ok = (g["ml_pinned"] and g["G-a_override"] and g["G-b_max_abs_c_on_minus_1"] <= 1e-9
          and g["G-c_max_rel_c_off_vs_july"] <= 1e-12 and g["G-p_provenance"] and g["G-f_finite_r1_r3"])
    rep["outcome"] = "MEASURED" if ok else "INCONCLUSIVE"
    if ok:
        mr = rep["metrics"]
        size = mr["r1_abs_d_over_sigma_band"]["median"] > 0.10 or mr["r1_floored_cells"]["max"] > 0.30
        r3_med = mr["r3_abs_d_over_sigma_ml"]["median"]
        rep["routing"] = ("MATERIAL" if (size and r3_med > 2) else
                          "NOT RESOLVED ABOVE TRAINER NOISE" if size else "NOT MATERIAL")
    else:
        rep["routing"] = None
    return d, floor, sig_ml, sig


def r1_rule(d, sig, floor):
    """The size criterion: median |d|/sigma_band > 0.10 over 205 cells, or max over the floored cells > 0.30."""
    r1 = np.abs(d) / sig
    return bool(np.median(r1) > 0.10 or np.max(r1[floor]) > 0.30)


FINAL = {("MATERIAL", "CONFIRMED"): "MATERIAL",
         ("MATERIAL", "NOT CONFIRMED"): "NOT RESOLVED ABOVE TRAINER NOISE",
         # ("NOT RESOLVED ABOVE TRAINER NOISE", "CONFIRMED") is decided in confirm() by the r1 rule on the
         # seed mean (director ruling 2026-10-12)
         ("NOT RESOLVED ABOVE TRAINER NOISE", "NOT CONFIRMED"): "NOT RESOLVED ABOVE TRAINER NOISE"}


def confirm(z43, z42, floor, out43, out42, routing42, d43, d42, sig):
    """Seed-43 confirmation on z = d / sigma_ML; returns the confirm record with the final routing."""
    if routing42 == "NOT MATERIAL":
        raise SystemExit("REFUSE: seed-42 routing is NOT MATERIAL; no seed-43 pair is declared (DESIGN §7)")
    flat = np.ptp(z43[floor]) == 0 or np.ptp(z42[floor]) == 0   # corrcoef of a constant is rounding residue
    pr = float("nan") if flat else float(np.corrcoef(z43[floor], z42[floor])[0, 1])
    sr = float("nan") if flat else float(np.corrcoef(rank(z43[floor]), rank(z42[floor]))[0, 1])
    if out43 != "MEASURED" or out42 != "MEASURED" or not np.isfinite(pr):
        verdict = "INCONCLUSIVE"
    else:
        verdict = "CONFIRMED" if pr >= 0.5 else "NOT CONFIRMED"
    dbar = (d42 + d43) / 2
    size_mean = r1_rule(dbar, sig, floor)
    if verdict == "INCONCLUSIVE":
        final = "INCONCLUSIVE"
    elif (routing42, verdict) == ("NOT RESOLVED ABOVE TRAINER NOISE", "CONFIRMED"):
        final = "MATERIAL" if size_mean else "NOT MATERIAL (coherent across seeds but below the r1 size threshold)"
    else:
        final = FINAL[(routing42, verdict)]
    r1m = np.abs(dbar) / sig
    return {"seed42_outcome": out42, "seed42_routing": routing42, "statistic": "z = d / sigma_ML",
            "n_cells": int(floor.sum()), "pearson_z43_z42_floored": pr, "spearman_z43_z42_floored": sr,
            "r1_seed_mean": {"median": float(np.median(r1m)), "max_floored": float(np.max(r1m[floor])),
                             "rule_holds": size_mean},
            "verdict": verdict, "final_routing": final}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("report")
    ap.add_argument("--tag", default="", help="'' for seed 42, '_s43' for the conditional seed-43 pair")
    ap.add_argument("--confirm", action="store_true", help="seed-43 confirmation: compare d43 with d42")
    a = ap.parse_args()
    if a.confirm and a.tag != "_s43":
        raise SystemExit("REFUSE: --confirm needs --tag _s43 (it must never compare seed 42 with itself)")
    if a.tag not in ("", "_s43"):
        raise SystemExit(f"REFUSE: unknown --tag {a.tag!r}")
    rep = {"tag": a.tag}
    d, floor, sig_ml, sig = pair(a.out_dir, a.tag, rep)
    if a.confirm:
        r42 = {}
        d42, floor42, sig_ml42, sig42 = pair(a.out_dir, "", r42)
        rep["seed42"] = {k: r42[k] for k in ("outcome", "routing", "gates", "metrics")}
        rep["confirm"] = confirm(d / sig_ml, d42 / sig_ml42, floor42, rep["outcome"], r42["outcome"],
                                 r42["routing"], d, d42, sig42)
    json.dump(rep, open(a.report, "w"), indent=1)
    print(json.dumps({k: rep.get(k) for k in ("gates", "outcome", "routing", "confirm")}, indent=1))
    print(json.dumps(rep["metrics"], indent=1))


if __name__ == "__main__":
    main()
