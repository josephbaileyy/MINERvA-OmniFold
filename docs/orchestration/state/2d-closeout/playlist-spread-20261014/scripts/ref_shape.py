"""Proxy R = (D/POT_d - B/POT_mc)/(S/POT_mc) of the full data set against the low-intensity 1A-1E subset, by bin.

Usage: python -I ref_shape.py <dir with runEventLoopOmniFold_<PL>.root> <out.json>

Every playlist's MC is scaled to its own data POT before summing (the per-playlist mix), so the comparison
isolates the playlist spread from the J36 mix error. Grid and cuts as in the triage yields.py. Stat: data only.
Also gives each group (1A-1E, 1F, 1G-1M, 1N-1P) against 1A-1E.
"""
import json
import sys

import numpy as np
import ROOT

d, out = sys.argv[1], sys.argv[2]
PLS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
PT = np.array([0, 0.25, 0.4, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5])
PZ = np.array([1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20, 60])
GROUPS = {"all": PLS, "1A-1E": PLS[:5], "1F": ["1F"], "1G-1M": ["1G", "1L", "1M"], "1N-1P": ["1N", "1O", "1P"]}


def h2(x, y, w=None):
    return np.histogram2d(x, y, [PT, PZ], weights=w)[0]


H = {}
for pl in PLS:
    fn = f"{d}/runEventLoopOmniFold_{pl}.root"
    f = ROOT.TFile.Open(fn)
    potmc, potd = f.Get("mcPOTUsed").GetVal(), f.Get("dataPOTUsed").GetVal()
    f.Close()
    D = ROOT.RDataFrame("data", fn).AsNumpy(["measured", "measured_pz"])
    S = ROOT.RDataFrame("mc_signal_reco", fn).Define("sp", "(int)sim_pass").Filter("sp == 1").AsNumpy(["sim", "sim_pz", "w_reco"])
    B = ROOT.RDataFrame("mc_background", fn).Define("bp", "(int)sim_background_pass").Filter("bp == 1").AsNumpy(
        ["sim_background", "sim_background_pz", "w_bkg"])
    k = potd / potmc
    H[pl] = dict(D=h2(D["measured"], D["measured_pz"]), S=k * h2(S["sim"], S["sim_pz"], S["w_reco"]),
                 B=k * h2(B["sim_background"], B["sim_background_pz"], B["w_bkg"]))
    print(pl, "loaded", flush=True)


def R(pls, axis=None):
    D, S, B = (sum(H[p][q] for p in pls) for q in ("D", "S", "B"))
    if axis is not None:
        D, S, B = D.sum(axis), S.sum(axis), B.sum(axis)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (D - B) / S, np.sqrt(D) / S


res = {"_grid": {"pt_edges_GeV": PT.tolist(), "pz_edges_GeV": PZ.tolist(), "layout": "10x10 rows = p_T bins"}}
ref = PLS[:5]
for g, pls in GROUPS.items():
    if g == "1A-1E":
        continue
    others = [p for p in ref if p not in pls]
    r = {}
    for name, ax in (("total", "tot"), ("by_pz", 0), ("by_pt", 1), ("bin", None)):
        if ax == "tot":
            a, ea = R(pls, (0, 1))
            b, eb = R(ref, (0, 1))
        else:
            a, ea = R(pls, ax)
            b, eb = R(ref, ax)
        q = a / b
        # 'all' contains the reference: its error uses the independent part only (approximate, conservative)
        eq = q * np.sqrt((ea / a) ** 2 + (eb / b) ** 2)
        r[name] = np.round(q, 5).tolist() if np.ndim(q) else float(q)
        r[name + "_data_stat"] = np.round(eq, 5).tolist() if np.ndim(eq) else float(eq)
    Dg = sum(H[p]["D"] for p in pls)
    Dr = sum(H[p]["D"] for p in ref)
    q = np.array(r["bin"])
    eq = np.array(r["bin_data_stat"])
    ok = (Dg >= 50) & (Dr >= 50) & np.isfinite(q) & (eq > 0)
    mu = np.average(q[ok], weights=1 / eq[ok] ** 2)
    r["bins_used"] = int(ok.sum())
    r["bin_shape_chi2_about_weighted_mean"] = float(np.sum(((q[ok] - mu) / eq[ok]) ** 2))
    r["bin_ratio_min_max"] = [float(q[ok].min()), float(q[ok].max())]
    r["bin"] = np.where(ok, q, np.nan).round(5).tolist()
    res[g + "_vs_1A-1E"] = r
    print(g, {k: v for k, v in r.items() if k in ("total", "by_pz", "by_pt", "bins_used", "bin_shape_chi2_about_weighted_mean",
                                                   "bin_ratio_min_max")}, flush=True)
json.dump(res, open(out, "w"), indent=1)
