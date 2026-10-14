"""Per-playlist selected yields per POT from the May production per-playlist event-loop outputs.
Usage: python -I yields.py <dir_with_runEventLoopOmniFold_<PL>.root> <out.json>
Bin-by-bin proxy for a per-playlist cross section: R = (D/POT_d - B/POT_mc) / (S/POT_mc), i.e. the
background-subtracted data yield over the MC signal-reco yield, both per POT. Each playlist's MC carries its
own flux, so R is (approximately) sigma_data/sigma_MC for that playlist."""
import json
import sys

import numpy as np
import ROOT

d, out = sys.argv[1], sys.argv[2]
PLS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
PT = np.array([0, 0.25, 0.4, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5])
PZ = np.array([1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20, 60])


def arr(f, tree, cols):
    df = ROOT.RDataFrame(tree, f)
    out = []
    for c in cols:
        if c.endswith("_pass"):
            df = df.Define(c + "_i", f"(int){c}")
            out.append(c + "_i")
        else:
            out.append(c)
    return {k.removesuffix("_i"): np.asarray(v) for k, v in df.AsNumpy(out).items()}


def ps(pt, pz):
    return (pt >= 0) & (pt < 4.5) & (pz >= 1.5) & (pz < 60)


res = {}
H = {}
for pl in PLS:
    fn = f"{d}/runEventLoopOmniFold_{pl}.root"
    f = ROOT.TFile.Open(fn)
    potmc, potd = f.Get("mcPOTUsed").GetVal(), f.Get("dataPOTUsed").GetVal()
    f.Close()
    D = arr(fn, "data", ["measured", "measured_pz"])
    S = arr(fn, "mc_signal_reco", ["sim", "sim_pz", "sim_pass", "w_reco"])
    B = arr(fn, "mc_background", ["sim_background", "sim_background_pz", "sim_background_pass", "w_bkg"])
    T = arr(fn, "mc_truth_denom", ["MC", "MC_pz", "w_truth"])
    md = ps(D["measured"], D["measured_pz"])
    ms = (S["sim_pass"] == 1) & ps(S["sim"], S["sim_pz"])
    mb = (B["sim_background_pass"] == 1) & ps(B["sim_background"], B["sim_background_pz"])
    hD = np.histogram2d(D["measured"][md], D["measured_pz"][md], [PT, PZ])[0]
    hS = np.histogram2d(S["sim"][ms], S["sim_pz"][ms], [PT, PZ], weights=S["w_reco"][ms])[0]
    hS2 = np.histogram2d(S["sim"][ms], S["sim_pz"][ms], [PT, PZ], weights=S["w_reco"][ms] ** 2)[0]
    hB = np.histogram2d(B["sim_background"][mb], B["sim_background_pz"][mb], [PT, PZ], weights=B["w_bkg"][mb])[0]
    H[pl] = dict(D=hD, S=hS, S2=hS2, B=hB, potd=potd, potmc=potmc)
    nD, nS, nB, nT = md.sum(), S["w_reco"][ms].sum(), B["w_bkg"][mb].sum(), T["w_truth"].sum()
    r = {"pot_data": potd, "pot_mc": potmc, "N_data_all": int(len(D["measured"])), "N_data_ps": int(nD),
         "S_w": float(nS), "B_w": float(nB), "T_w": float(nT), "N_sig_rows_pass": int(ms.sum()),
         "data_per_1e19": float(nD / potd * 1e19), "mcreco_per_1e19": float((nS + nB) / potmc * 1e19),
         "sig_per_1e19": float(nS / potmc * 1e19), "bkg_per_1e19": float(nB / potmc * 1e19),
         "truth_per_1e19": float(nT / potmc * 1e19), "eff_S_over_T": float(nS / nT),
         "R": float((nD / potd - nB / potmc) / (nS / potmc)), "R_stat": float(np.sqrt(nD) / potd / (nS / potmc))}
    res[pl] = r
    print(pl, {k: (round(v, 5) if isinstance(v, float) and abs(v) < 1e6 else v) for k, v in r.items()}, flush=True)

# 1A vs the other 11 combined, total and per bin
rest = [p for p in PLS if p != "1A"]
agg = {k: sum(H[p][k] for p in rest) for k in ("D", "S", "S2", "B", "potd", "potmc")}
a = H["1A"]


def Rmap(h):
    return (h["D"] / h["potd"] - h["B"] / h["potmc"]) / (h["S"] / h["potmc"])


def Rerr(h):
    return np.sqrt(h["D"]) / h["potd"] / (h["S"] / h["potmc"])


with np.errstate(divide="ignore", invalid="ignore"):
    RA, RR = Rmap(a), Rmap(agg)
    eA, eR = Rerr(a), Rerr(agg)
    ratio = RA / RR
    rerr = ratio * np.sqrt((eA / RA) ** 2 + (eR / RR) ** 2)
    ok = (a["D"] >= 50) & (agg["D"] >= 50) & np.isfinite(ratio)
    pull = (ratio - 1) / rerr
# leave-one-out spread: each playlist vs the other 11, total R
loo = {}
for p in PLS:
    others = [q for q in PLS if q != p]
    g = {k: sum(H[q][k] for q in others) for k in ("D", "S", "B", "potd", "potmc")}
    tot = lambda h: (h["D"].sum() / h["potd"] - h["B"].sum() / h["potmc"]) / (h["S"].sum() / h["potmc"])
    loo[p] = float(tot(H[p]) / tot(g))
w = ok
res["_1A_vs_rest"] = {
    "R_1A_total": res["1A"]["R"],
    "R_rest_total": float((agg["D"].sum() / agg["potd"] - agg["B"].sum() / agg["potmc"]) / (agg["S"].sum() / agg["potmc"])),
    "data_per_1e19_rest": float(agg["D"].sum() / agg["potd"] * 1e19),
    "mcreco_per_1e19_rest": float((agg["S"].sum() + agg["B"].sum()) / agg["potmc"] * 1e19),
    "n_bins_used": int(w.sum()),
    "bin_ratio_median": float(np.median(ratio[w])), "bin_ratio_min": float(np.min(ratio[w])), "bin_ratio_max": float(np.max(ratio[w])),
    "bin_chi2_vs_weighted_mean": float(np.sum(((ratio[w] - np.average(ratio[w], weights=1 / rerr[w] ** 2)) / rerr[w]) ** 2)),
    "bin_weighted_mean_ratio": float(np.average(ratio[w], weights=1 / rerr[w] ** 2)),
    "bin_max_abs_pull_vs_1": float(np.max(np.abs(pull[w]))),
    "ratio_by_pz_bin_all_pt": [float(x) for x in ((a["D"].sum(0) / a["potd"] - a["B"].sum(0) / a["potmc"]) / (a["S"].sum(0) / a["potmc"])
                                                   / ((agg["D"].sum(0) / agg["potd"] - agg["B"].sum(0) / agg["potmc"]) / (agg["S"].sum(0) / agg["potmc"])))],
    "ratio_by_pt_bin_all_pz": [float(x) for x in ((a["D"].sum(1) / a["potd"] - a["B"].sum(1) / a["potmc"]) / (a["S"].sum(1) / a["potmc"])
                                                   / ((agg["D"].sum(1) / agg["potd"] - agg["B"].sum(1) / agg["potmc"]) / (agg["S"].sum(1) / agg["potmc"])))],
    "leave_one_out_R_ratio": loo,
}
print(json.dumps(res["_1A_vs_rest"], indent=1))
json.dump(res, open(out, "w"), indent=1)

# Control: the same per-bin shape test for EVERY playlist against the other 11, with data AND MC-signal stat.
def bintest(p):
    others = [q for q in PLS if q != p]
    g = {k: sum(H[q][k] for q in others) for k in ("D", "S", "S2", "B", "potd", "potmc")}
    h = H[p]
    with np.errstate(divide="ignore", invalid="ignore"):
        r1, r2 = Rmap(h), Rmap(g)
        v1 = (np.sqrt(h["D"]) / h["potd"] / (h["S"] / h["potmc"])) ** 2 + (r1 + h["B"] / h["S"]) ** 2 * h["S2"] / h["S"] ** 2
        v2 = (np.sqrt(g["D"]) / g["potd"] / (g["S"] / g["potmc"])) ** 2 + (r2 + g["B"] / g["S"]) ** 2 * g["S2"] / g["S"] ** 2
        q = r1 / r2
        e = q * np.sqrt(v1 / r1 ** 2 + v2 / r2 ** 2)
    m = (h["D"] >= 50) & (g["D"] >= 50) & np.isfinite(q) & (e > 0)
    mu = np.average(q[m], weights=1 / e[m] ** 2)
    return {"n": int(m.sum()), "wmean": float(mu), "chi2_shape": float(np.sum(((q[m] - mu) / e[m]) ** 2)),
            "max_abs_dev": float(np.max(np.abs(q[m] / mu - 1)))}


ctl = {p: bintest(p) for p in PLS}
for p in PLS:
    print("bintest", p, ctl[p])
res["_bintest_each_vs_rest"] = ctl
json.dump(res, open(out, "w"), indent=1)
