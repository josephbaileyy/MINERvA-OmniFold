#!/usr/bin/env python3
"""P2-G2 analysis: P5's analysis (stageB/diagnostics/p5/analyze_p5.py, 8f37fd7f...) on the Flux universe chosen by
select_flux.py, with the Flux re-declarations frozen in stageC/pilot/DESIGN.md §6 before any job. Changes from
analyze_p5.py, and nothing else:
  - universe Flux:23 (from select_flux.json, sha256 pinned below); run a = the P2 derived Flux_23 run (seed 42) or
    the seed-43 off run; run b = the P2-G2 on run;
  - sigma_band = select_flux.json sigma_band.per_cell (weighted std of July Flux_0..99 with the nu-e+IMD constraint
    weights), replacing |j0 - j1|/2; the floor sigma_band >= 1e-3 x CV is unchanged (205 of 205 cells floored);
  - G-c reference = the July Flux_23 product (eb8414af...); the bridge is |a - July Flux_23| / sigma_band;
  - G-p pins the production driver 74a4ed69... and driver_g2.py eb258cad... (P5's patch on 74a4ed69, body
    identical); G-u adds that both runs' runConfig universe is Flux:23;
  - n_override = 8,999,007 (nTruthOnlyMisses of the omnifile; universe independent), unchanged;
  - r1/r3 thresholds 0.10, 0.30 and 2 and the routing and seed-43 logic are P5's, unchanged.

  python analyze_g2.py <a.root> <b.root> <override.json> <override.npz> <report.json>
         [--tag _s43 --confirm --a42 <a42.root> --b42 <b42.root>]

Routing (P5 DESIGN §6-7, unchanged):
  r1 rule = median r1 > 0.10 over 205 cells, or max r1 > 0.30 over the floored cells
  MATERIAL iff the r1 rule holds AND median r3 > 2; NOT RESOLVED ABOVE TRAINER NOISE iff the r1 rule holds AND
  median r3 <= 2; NOT MATERIAL otherwise. Seed-43 confirmation: CONFIRMED iff both pairs MEASURED and
  Pearson(z43, z42) >= 0.5 over the floored cells; INCONCLUSIVE if either pair is not MEASURED or r is not finite;
  final routing per FINAL below and confirm() (frozen row: any INCONCLUSIVE -> INCONCLUSIVE).
"""
import argparse
import hashlib
import json
import os

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
D2 = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
PN = f"{D2}/uq/purity_newomni"
ML = f"{D2}/uq/seedscan_lgbm_ml/uq_covariance_ml.root"
ML_SHA = "3b6b48ec89207ae29dc7bb0ddc5a41836c359c4805877d663731694b828d5db9"
PROD_SHA = "74a4ed69c3fa9c4ae5b6866f36343212b8d3f903fddde6c7bd40c382c1167d56"
DIAG_SHA = "eb258cadfc2b0ab7191e400eb13564a2866d393e18b830c3f2d5a7d12349cc99"   # driver_g2.py
HELPER_SHA = "e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a"
N_MISS = 8999007
UNI = "Flux:23"
SEL = "/pscratch/sd/j/josephrb/2d-closeout-stageC-pilot-20261013/select/select_flux.json"
SEL_SHA = "35ce6226116a0415255408e341b2ae4dafa8102830185c0eaf9b0b68aea1e0b0"
J0 = f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_Flux_23.root"
J0_SHA = "eb8414af4d9c06e4be80fc190ddfbd8734e0470b7f6e30c1790cebe6cb171141"
FLUXU = f"{D2}/baseline_flux/flux_integral_universes_MEFHC.root"   # absolute (P5 used the relative default)


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


def pair(fa, fb, ovjson, ovnpz, rep):
    F = {"a": fa, "b": fb, "cv": f"{D2}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root", "j0": J0, "ml": ML,
         "select": SEL}
    rep["inputs"] = {k: {"path": p, "sha256": sha(p)} for k, p in F.items()}
    g = rep["gates"] = {}
    g["ml_pinned"] = rep["inputs"]["ml"]["sha256"] == ML_SHA
    g["select_pinned"] = rep["inputs"]["select"]["sha256"] == SEL_SHA and rep["inputs"]["j0"]["sha256"] == J0_SHA
    sel = json.load(open(SEL))
    cv2, area2 = arr(F["cv"], "hXSec2D")
    m = (cv2 > 0).ravel()
    g["select_matches"] = (sel["choice"]["universe"] == UNI and sel["choice"]["july_product"]["sha256"] == J0_SHA
                           and sel["cells"] == [[int(i), int(j)] for i, j in np.argwhere(cv2 > 0)])
    X = {k: arr(F[k], "hXSec2D")[0].ravel()[m] for k in ("a", "b", "cv", "j0")}
    C = {k: arr(F[k], "hOFCompleteness2D")[0].ravel()[m] for k in ("a", "b", "j0")}
    area = area2.ravel()[m]
    fml = ROOT.TFile.Open(ML)
    hml = fml.Get("hCov2D_reported")
    sig_ml = np.sqrt(np.array([hml.GetBinContent(i + 1, i + 1) for i in range(hml.GetNbinsX())]))
    fml.Close()

    ovj = json.load(open(ovjson))
    ov_sha = sha(ovnpz)
    na, nb = named(F["a"]), named(F["b"])
    g["G-a_override"] = bool(ovj.get("ALL_PASS")) and ovj.get("n_override") == N_MISS \
        and nb["p5MissWeightOverride"] is not None and f"sha256={ov_sha}" in nb["p5MissWeightOverride"]
    g["G-b_max_abs_c_on_minus_1"] = float(np.max(np.abs(C["b"] - 1)))
    g["G-c_max_rel_c_off_vs_july"] = float(np.max(np.abs(C["a"] / C["j0"] - 1)))
    ca = json.loads(na["runConfig"]) if na["runConfig"] else None   # absent provenance fails G-p, not the script
    cb = json.loads(nb["runConfig"]) if nb["runConfig"] else None
    g["G-u_universe"] = (ca is not None and cb is not None and ca.get("universe") == cb.get("universe") == UNI
                         and ca.get("flux_universe_file") == cb.get("flux_universe_file") == FLUXU)
    rep["universe_recorded"] = {"a": None if ca is None else ca.get("universe"),
                                "b": None if cb is None else cb.get("universe")}
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
    sig = np.asarray(sel["sigma_band"]["per_cell"], float)   # re-declared Flux sigma_band (DESIGN §6)
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
    ok = (g["ml_pinned"] and g["select_pinned"] and g["select_matches"] and g["G-u_universe"]
          and g["G-a_override"] and g["G-b_max_abs_c_on_minus_1"] <= 1e-9
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
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("override_json")
    ap.add_argument("override_npz")
    ap.add_argument("report")
    ap.add_argument("--tag", default="", help="'' for seed 42, '_s43' for the conditional seed-43 pair")
    ap.add_argument("--confirm", action="store_true", help="seed-43 confirmation: compare d43 with d42")
    ap.add_argument("--a42")
    ap.add_argument("--b42")
    a = ap.parse_args()
    if a.confirm and (a.tag != "_s43" or not a.a42 or not a.b42):
        raise SystemExit("REFUSE: --confirm needs --tag _s43 and the seed-42 pair (--a42, --b42)")
    if a.confirm and len({os.path.realpath(p) for p in (a.a, a.b, a.a42, a.b42)}) != 4:
        raise SystemExit("REFUSE: the seed-43 and seed-42 pairs must be four distinct files")
    if a.tag not in ("", "_s43"):
        raise SystemExit(f"REFUSE: unknown --tag {a.tag!r}")
    rep = {"tag": a.tag, "universe": UNI}
    d, floor, sig_ml, sig = pair(a.a, a.b, a.override_json, a.override_npz, rep)
    if a.confirm:
        r42 = {}
        d42, floor42, sig_ml42, sig42 = pair(a.a42, a.b42, a.override_json, a.override_npz, r42)
        rep["seed42"] = {k: r42[k] for k in ("outcome", "routing", "gates", "metrics")}
        rep["confirm"] = confirm(d / sig_ml, d42 / sig_ml42, floor42, rep["outcome"], r42["outcome"],
                                 r42["routing"], d, d42, sig42)
    json.dump(rep, open(a.report, "w"), indent=1)
    print(json.dumps({k: rep.get(k) for k in ("gates", "outcome", "routing", "confirm")}, indent=1))
    print(json.dumps(rep["metrics"], indent=1))


if __name__ == "__main__":
    main()
