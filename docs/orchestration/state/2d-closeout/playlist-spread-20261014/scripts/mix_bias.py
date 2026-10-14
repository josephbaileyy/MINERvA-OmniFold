"""Playlist-mix bias and playlist-spread decomposition, binned, from the per-playlist event-loop outputs.

Usage: python -I mix_bias.py <dir with runEventLoopOmniFold_<PL>.root> <out.json> [n_toys]

The production merges the 12 per-playlist files with hadd (summed mcPOTUsed / dataPOTUsed, concatenated trees)
and the producer scales all MC by ONE ratio, sum(POT_data)/sum(POT_mc). That gives each playlist's MC a share
proportional to its MC POT. The data mix is proportional to data POT. This script compares two binned unfolds of the
same pooled data on the 10x10 (p_T, p_||) grid of the triage yields.py:

  pooled : every MC histogram = (sum_p POT_d,p / sum_p POT_mc,p) * sum_p H_p          (what hadd + producer do)
  dw     : every MC histogram = sum_p (POT_d,p / POT_mc,p) * H_p                    (each playlist at its own data POT)

Estimators (binned; NOT OmniFold):
  bbb : bin-by-bin, U_j = (D_j - B_j) * T_j / S_j  (S reco-binned signal passing, T truth-binned truth-denominator)
  ibu : D'Agostini, 5 iterations, response R[reco, truth] from signal events passing reco with reco and truth in the
        grid, efficiency sum_i R_ij / T_j, prior = T of the same mix.

MC statistical error of the pooled/dw ratio: Poisson(1) event-level bootstrap of every MC tree (signal, background),
applied to both mixes at once; data Poisson-fluctuated per bin.
The truth denominator is taken from mc_signal_reco (all rows, w_truth); its weight sum equals mc_truth_denom's
(checked by align.py on 1L and 1P, and re-checked here for every playlist).
"""
import json
import sys

import numpy as np
import ROOT

d, out = sys.argv[1], sys.argv[2]
NTOY = int(sys.argv[3]) if len(sys.argv) > 3 else 20
PLS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
GROUPS = {"1A-1F": PLS[:6], "1G-1M": ["1G", "1L", "1M"], "1N-1P": ["1N", "1O", "1P"]}
PT = np.array([0, 0.25, 0.4, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5])
PZ = np.array([1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20, 60])
NB = 100


def flat(pt, pz):
    """Flat bin index ipt*10+ipz on the grid, -1 outside."""
    ix = np.searchsorted(PT, pt, side="right") - 1
    iy = np.searchsorted(PZ, pz, side="right") - 1
    ok = (ix >= 0) & (ix < 10) & (iy >= 0) & (iy < 10)
    return np.where(ok, ix * 10 + iy, -1)


def cols(fn, tree, names, ints=()):
    df = ROOT.RDataFrame(tree, fn)
    outn = []
    for c in names:
        if c in ints:
            df = df.Define(c + "_i", f"(int){c}")
            outn.append(c + "_i")
        else:
            outn.append(c)
    return {k.removesuffix("_i"): np.asarray(v) for k, v in df.AsNumpy(outn).items()}


EV = {}
meta = {}
for pl in PLS:
    fn = f"{d}/runEventLoopOmniFold_{pl}.root"
    f = ROOT.TFile.Open(fn)
    potmc, potd = f.Get("mcPOTUsed").GetVal(), f.Get("dataPOTUsed").GetVal()
    f.Close()
    D = cols(fn, "data", ["measured", "measured_pz"])
    S = cols(fn, "mc_signal_reco", ["sim", "sim_pz", "sim_pass", "w_reco", "MC", "MC_pz", "w_truth"], ints=("sim_pass",))
    B = cols(fn, "mc_background", ["sim_background", "sim_background_pz", "sim_background_pass", "w_bkg"],
             ints=("sim_background_pass",))
    Tden = cols(fn, "mc_truth_denom", ["w_truth"])
    ir = np.where(S["sim_pass"] == 1, flat(S["sim"], S["sim_pz"]), -1)
    it = flat(S["MC"], S["MC_pz"])
    ib = np.where(B["sim_background_pass"] == 1, flat(B["sim_background"], B["sim_background_pz"]), -1)
    idd = flat(D["measured"], D["measured_pz"])
    EV[pl] = dict(ir=ir, it=it, wr=S["w_reco"], wt=S["w_truth"], ib=ib, wb=B["w_bkg"],
                  Dh=np.bincount(idd[idd >= 0], minlength=NB).astype(float), potd=potd, potmc=potmc)
    meta[pl] = {"source": fn, "pot_data": potd, "pot_mc": potmc,
                "sumw_truth_signal_reco": float(S["w_truth"].sum()), "sumw_truth_denom": float(Tden["w_truth"].sum()),
                "truth_rows_outside_grid": int((it < 0).sum())}
    print(pl, meta[pl], flush=True)


def hists(pl, ps=None, pb=None):
    """Per-playlist binned histograms; ps/pb are optional bootstrap multiplicities."""
    e = EV[pl]
    wr = e["wr"] if ps is None else e["wr"] * ps
    wt = e["wt"] if ps is None else e["wt"] * ps
    wb = e["wb"] if pb is None else e["wb"] * pb
    sel = e["ir"] >= 0
    S = np.bincount(e["ir"][sel], weights=wr[sel], minlength=NB)
    both = sel & (e["it"] >= 0)
    R = np.bincount(e["ir"][both] * NB + e["it"][both], weights=wr[both], minlength=NB * NB).reshape(NB, NB)
    tin = e["it"] >= 0
    T = np.bincount(e["it"][tin], weights=wt[tin], minlength=NB)
    bs = e["ib"] >= 0
    Bh = np.bincount(e["ib"][bs], weights=wb[bs], minlength=NB)
    return dict(S=S, R=R, T=T, B=Bh)


def mix(H, kind, pls=PLS):
    potd = sum(EV[p]["potd"] for p in pls)
    potmc = sum(EV[p]["potmc"] for p in pls)
    out = {}
    for k in ("S", "R", "T", "B"):
        if kind == "pooled":
            out[k] = potd / potmc * sum(H[p][k] for p in pls)
        else:
            out[k] = sum(EV[p]["potd"] / EV[p]["potmc"] * H[p][k] for p in pls)
    return out


def bbb(Dsum, M):
    with np.errstate(divide="ignore", invalid="ignore"):
        return (Dsum - M["B"]) * M["T"] / M["S"]


def ibu(Dsum, M, n_iter=5):
    R, T = M["R"], M["T"]
    with np.errstate(divide="ignore", invalid="ignore"):
        P = np.where(T > 0, R / T, 0.0)             # P(reco i | truth j), includes efficiency
        eff = P.sum(0)
        dsub = np.clip(Dsum - M["B"], 0, None)
        t = T.copy()
        for _ in range(n_iter):
            fold = P @ t
            t = np.where(eff > 0, t * (P.T @ np.where(fold > 0, dsub / fold, 0.0)) / eff, 0.0)
    return t


def proj(v):
    m = v.reshape(10, 10)
    return m.sum(1), m.sum(0)  # over p_|| -> p_T marginal; over p_T -> p_|| marginal


def compare(Dsum, H):
    P, W = mix(H, "pooled"), mix(H, "dw")
    r = {}
    for name, fn_ in (("bbb", bbb), ("ibu", ibu)):
        up, uw = fn_(Dsum, P), fn_(Dsum, W)
        ok = np.isfinite(up) & np.isfinite(uw) & (uw > 0)
        pt_p, pz_p = proj(np.where(ok, up, 0))
        pt_w, pz_w = proj(np.where(ok, uw, 0))
        r[name] = dict(total=float(up[ok].sum() / uw[ok].sum() - 1), bin=np.where(ok, up / np.where(uw > 0, uw, 1) - 1, np.nan),
                       pt=pt_p / np.where(pt_w > 0, pt_w, 1) - 1, pz=pz_p / np.where(pz_w > 0, pz_w, 1) - 1)
    # pieces: efficiency only (B from dw in both) and background only (eff from dw in both), bin-by-bin
    Pe = dict(P, B=W["B"])
    Pb = dict(W, B=P["B"])
    for name, M in (("bbb_eff_only", Pe), ("bbb_bkg_only", Pb)):
        up, uw = bbb(Dsum, M), bbb(Dsum, W)
        ok = np.isfinite(up) & np.isfinite(uw) & (uw > 0)
        r[name] = dict(total=float(up[ok].sum() / uw[ok].sum() - 1))
    effP = P["S"].sum() / P["T"].sum()
    effW = W["S"].sum() / W["T"].sum()
    r["eff_total_pooled"], r["eff_total_dw"] = float(effP), float(effW)
    r["bkg_total_pooled"], r["bkg_total_dw"] = float(P["B"].sum()), float(W["B"].sum())
    return r


H0 = {p: hists(p) for p in PLS}
Dsum0 = sum(EV[p]["Dh"] for p in PLS)
nominal = compare(Dsum0, H0)
rng = np.random.default_rng(20261014)
toys = []
for k in range(NTOY):
    Hk = {p: hists(p, rng.poisson(1.0, len(EV[p]["wr"])), rng.poisson(1.0, len(EV[p]["wb"]))) for p in PLS}
    Dk = rng.poisson(Dsum0).astype(float)
    toys.append(compare(Dk, Hk))
    print("toy", k, {n: round(toys[-1][n]["total"], 6) for n in ("bbb", "ibu")}, flush=True)


def tstd(key, sub):
    return np.nanstd(np.array([t[key][sub] for t in toys]), axis=0, ddof=1)


res = {"_meta": meta, "_mix_weights": {}, "_toys": NTOY}
gpotd = sum(EV[p]["potd"] for p in PLS)
gpotmc = sum(EV[p]["potmc"] for p in PLS)
for p in PLS:
    res["_mix_weights"][p] = {"data_share": EV[p]["potd"] / gpotd, "mc_share": EV[p]["potmc"] / gpotmc,
                              "potd_over_potmc": EV[p]["potd"] / EV[p]["potmc"],
                              "lambda_dw_over_pooled": (EV[p]["potd"] / EV[p]["potmc"]) / (gpotd / gpotmc)}
res["global_potd_over_potmc"] = gpotd / gpotmc
for name in ("bbb", "ibu"):
    res[name] = {"total_bias": nominal[name]["total"], "total_bias_mcstat": float(tstd(name, "total")),
                 "pt_marginal_bias": nominal[name]["pt"].tolist(), "pt_marginal_mcstat": tstd(name, "pt").tolist(),
                 "pz_marginal_bias": nominal[name]["pz"].tolist(), "pz_marginal_mcstat": tstd(name, "pz").tolist(),
                 "bin_bias_10x10_pt_rows": np.round(nominal[name]["bin"], 6).reshape(10, 10).tolist(),
                 "bin_bias_mcstat_10x10": np.round(tstd(name, "bin"), 6).reshape(10, 10).tolist()}
    b = nominal[name]["bin"]
    w = (Dsum0 >= 50) & np.isfinite(b)
    res[name]["bins_used_D_ge_50"] = int(w.sum())
    res[name]["bin_bias_min_max_D_ge_50"] = [float(b[w].min()), float(b[w].max())]
for name in ("bbb_eff_only", "bbb_bkg_only"):
    res[name] = {"total_bias": nominal[name]["total"], "total_bias_mcstat": float(tstd(name, "total"))}
for k in ("eff_total_pooled", "eff_total_dw", "bkg_total_pooled", "bkg_total_dw"):
    res[k] = nominal[k]

# Q2: per-playlist factors and the group shape of the proxy R = (D/POT_d - B/POT_mc) / (S/POT_mc)
fac = {}
for p in PLS:
    h, e = H0[p], EV[p]
    D, B, S, T = e["Dh"].sum(), h["B"].sum(), h["S"].sum(), h["T"].sum()
    fac[p] = {"data_per_1e19": D / e["potd"] * 1e19, "bkg_per_1e19_mc": B / e["potmc"] * 1e19,
              "dsub_per_1e19": (D / e["potd"] - B / e["potmc"]) * 1e19, "sig_reco_per_1e19_mc": S / e["potmc"] * 1e19,
              "truth_per_1e19_mc": T / e["potmc"] * 1e19, "eff_S_over_T": S / T,
              "R": (D / e["potd"] - B / e["potmc"]) / (S / e["potmc"])}
ref = {k: np.mean([fac[p][k] for p in ["1A", "1B", "1C", "1D"]]) for k in fac["1A"]}
for p in PLS:
    fac[p]["rel_to_1A1D_mean"] = {k: fac[p][k] / ref[k] for k in ("dsub_per_1e19", "eff_S_over_T", "truth_per_1e19_mc", "R")}
res["factors"] = fac


def Rmap(pls):
    D = sum(EV[p]["Dh"] for p in pls)
    potd = sum(EV[p]["potd"] for p in pls)
    potmc = sum(EV[p]["potmc"] for p in pls)
    S = sum(H0[p]["S"] for p in pls)
    B = sum(H0[p]["B"] for p in pls)
    return D, S, B, potd, potmc


def Rof(D, S, B, potd, potmc):
    with np.errstate(divide="ignore", invalid="ignore"):
        return (D / potd - B / potmc) / (S / potmc)


shape = {}
Dall, Sall, Ball, pda, pma = Rmap(PLS)
for g, pls in GROUPS.items():
    D, S, B, pd, pm = Rmap(pls)
    rest = [p for p in PLS if p not in pls]
    Dr, Sr, Br, pdr, pmr = Rmap(rest)
    q = Rof(D, S, B, pd, pm) / Rof(Dr, Sr, Br, pdr, pmr)
    qe = q * np.sqrt(1 / np.maximum(D, 1) + 1 / np.maximum(Dr, 1))
    ok = (D >= 50) & (Dr >= 50) & np.isfinite(q)
    pt = Rof(D.reshape(10, 10).sum(1), S.reshape(10, 10).sum(1), B.reshape(10, 10).sum(1), pd, pm) / \
        Rof(Dr.reshape(10, 10).sum(1), Sr.reshape(10, 10).sum(1), Br.reshape(10, 10).sum(1), pdr, pmr)
    pz = Rof(D.reshape(10, 10).sum(0), S.reshape(10, 10).sum(0), B.reshape(10, 10).sum(0), pd, pm) / \
        Rof(Dr.reshape(10, 10).sum(0), Sr.reshape(10, 10).sum(0), Br.reshape(10, 10).sum(0), pdr, pmr)
    tot = Rof(D.sum(), S.sum(), B.sum(), pd, pm) / Rof(Dr.sum(), Sr.sum(), Br.sum(), pdr, pmr)
    # data-only and MC-efficiency-only shape: data per POT ratio and MC (S/T) ratio by p_|| (reco-binned S, truth-binned T)
    Tg = sum(H0[p]["T"] for p in pls)
    Tr = sum(H0[p]["T"] for p in rest)
    dpz = (D.reshape(10, 10).sum(0) / pd) / (Dr.reshape(10, 10).sum(0) / pdr)
    epz = (S.reshape(10, 10).sum(0) / Tg.reshape(10, 10).sum(0)) / (Sr.reshape(10, 10).sum(0) / Tr.reshape(10, 10).sum(0))
    dpt = (D.reshape(10, 10).sum(1) / pd) / (Dr.reshape(10, 10).sum(1) / pdr)
    ept = (S.reshape(10, 10).sum(1) / Tg.reshape(10, 10).sum(1)) / (Sr.reshape(10, 10).sum(1) / Tr.reshape(10, 10).sum(1))
    shape[g] = {"playlists": pls, "R_ratio_total_vs_rest": float(tot),
                "R_ratio_by_pz": pz.tolist(), "R_ratio_by_pt": pt.tolist(),
                "data_per_pot_ratio_by_pz": dpz.tolist(), "mc_eff_ratio_by_pz": epz.tolist(),
                "data_per_pot_ratio_by_pt": dpt.tolist(), "mc_eff_ratio_by_pt": ept.tolist(),
                "R_ratio_10x10_pt_rows": np.round(np.where(ok, q, np.nan), 5).reshape(10, 10).tolist(),
                "R_ratio_10x10_data_stat": np.round(np.where(ok, qe, np.nan), 5).reshape(10, 10).tolist()}
res["group_shape"] = shape
res["_grid"] = {"pt_edges_GeV": PT.tolist(), "pz_edges_GeV": PZ.tolist(),
                "flat_index": "ipt*10+ipz; 10x10 lists are rows = p_T bins, columns = p_|| bins"}
json.dump(res, open(out, "w"), indent=1, default=float)
print(json.dumps({k: res[k] for k in ("bbb_eff_only", "bbb_bkg_only", "eff_total_pooled", "eff_total_dw",
                                      "bkg_total_pooled", "bkg_total_dw", "global_potd_over_potmc")}, indent=1))
for name in ("bbb", "ibu"):
    print(name, {k: v for k, v in res[name].items() if not k.startswith("bin_bias_") or k.endswith("D_ge_50")})
