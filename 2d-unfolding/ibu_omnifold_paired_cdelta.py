#!/usr/bin/env python3
"""Paired OmniFold-vs-IBU method-difference covariance C_delta (Agent C, WS3).

The current same-data OmniFold/IBU/paper chi-squares are DESCRIPTIVE distances: they use a
single-side or naively-summed covariance and never the cross term, so they are not a calibrated
method-difference test. This builds the correct object: push the SAME Poisson data+MC bootstrap
draw through BOTH estimators on ONE shared binned 2D (pT,p||) response, form
    delta_r = x_OF,r - x_IBU,r ,  C_delta = Cov(delta_r) ,
and the method-difference statistic  T = delta_bar^T pinv(C_delta, rank) delta_bar  (declared rank).
Both estimators are the SAME-library binned unfolders with an identical (response, measured, niter)
contract: RooUnfoldBayes (D'Agostini IBU) and RooUnfoldOmnifold (binned OmniFold), from
unbinned_unfolding/build/libRooUnfold.so. Working in unfolded truth-count space: the common
efficiency/flux/nucleon/POT factors multiply both estimators identically and cancel in T (scale-
invariant), so they are omitted; delta is reported in unfolded-count units.

NOTE: this is the tractable, apples-to-apples BINNED method comparison (both on the 14x16 grid at
niter=5). The production OmniFold result is UNBINNED; this test isolates the IBU-vs-OmniFold
ALGORITHM difference under identical binned inputs, which is the object the contract requires.

  python ibu_omnifold_paired_cdelta.py --omnifile 2d-unfolding/runEventLoopOmniFold_MEFHC.root \
      --niter 5 --replicas 200 --seed 20260716 --out 2d-unfolding/uq/ibu_omnifold_cdelta.{root,json}
"""
import argparse, json, os, sys
import numpy as np

PT_EDGES = np.array([0.0, 0.075, 0.15, 0.25, 0.325, 0.4, 0.475, 0.55, 0.7, 0.85,
                     1.0, 1.25, 1.5, 2.5, 4.5])           # 14 bins
PZ_EDGES = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0,
                     10.0, 15.0, 20.0, 40.0, 60.0])        # 16 bins
NPT, NPZ = len(PT_EDGES) - 1, len(PZ_EDGES) - 1
NB = NPT * NPZ                                             # 224


def gbin(pt, pz):
    """Global 0..223 bin, or -1 if outside the reported (pt,pz) range."""
    ip = np.digitize(pt, PT_EDGES) - 1
    iz = np.digitize(pz, PZ_EDGES) - 1
    ok = (ip >= 0) & (ip < NPT) & (iz >= 0) & (iz < NPZ)
    g = np.where(ok, ip * NPZ + iz, -1)
    return g, ok


def load_events(omnifile):
    """Load per-event (pt,pz,weights,pass) arrays via uproot (fast columnar). Exact branches:
    data: measured/measured_pz/measured_pass; mc_signal_reco: sim/sim_pz/sim_pass/MC/MC_pz/w_truth/w_reco;
    mc_truth_denom: MC/MC_pz/w_truth; mc_background: sim_background/_pz/_pass/w_bkg."""
    import ROOT
    def rd(tree, branches):
        # cast every branch to double inside RDataFrame -> AsNumpy returns clean float64
        # (avoids bool/char *_pass dtype quirks).
        df = ROOT.RDataFrame(tree, omnifile)
        alias = {}
        for b in branches:
            df = df.Define("d_" + b, "(double)(" + b + ")"); alias[b] = "d_" + b
        cols = df.AsNumpy(list(alias.values()))
        return {b: np.asarray(cols[alias[b]], dtype=float) for b in branches}
    d = {}
    dc = rd("data", ["measured", "measured_pz", "measured_pass"])
    dpass = dc["measured_pass"].astype(bool)
    d["data_pt"] = dc["measured"][dpass]; d["data_pz"] = dc["measured_pz"][dpass]
    d["data_w"] = np.ones_like(d["data_pt"])                      # data counts (unit weight)
    sc = rd("mc_signal_reco", ["sim", "sim_pz", "sim_pass", "MC", "MC_pz", "w_truth", "w_reco"])
    d["s_rpt"] = sc["sim"]; d["s_rpz"] = sc["sim_pz"]; d["s_tpt"] = sc["MC"]; d["s_tpz"] = sc["MC_pz"]
    d["s_pass"] = sc["sim_pass"]; d["s_wt"] = sc["w_truth"]; d["s_wr"] = sc["w_reco"]
    tc = rd("mc_truth_denom", ["MC", "MC_pz", "w_truth"])
    d["td_tpt"] = tc["MC"]; d["td_tpz"] = tc["MC_pz"]; d["td_w"] = tc["w_truth"]
    bc = rd("mc_background", ["sim_background", "sim_background_pz", "sim_background_pass", "w_bkg"])
    bp = bc["sim_background_pass"].astype(bool)
    d["b_rpt"] = bc["sim_background"][bp]; d["b_rpz"] = bc["sim_background_pz"][bp]; d["b_w"] = bc["w_bkg"][bp]
    fh = ROOT.TFile.Open(omnifile)
    def par(name, default):
        o = fh.Get(name); return float(o.GetVal()) if o else default
    d["dataPOT"] = par("dataPOTUsed", 1.057394261158926e+21)
    d["mcPOT"] = par("mcPOTUsed", 4.978198462880827e+21)
    fh.Close()
    return d


def build_indices(d):
    """Precompute global-bin indices + masks once (nominal weights carried separately)."""
    idx = {}
    g_dr, ok = gbin(d["data_pt"], d["data_pz"]); idx["data_g"] = g_dr; idx["data_ok"] = ok
    g_sr, ok_sr = gbin(d["s_rpt"], d["s_rpz"]); g_st, ok_st = gbin(d["s_tpt"], d["s_tpz"])
    passed = d["s_pass"].astype(bool)
    idx["s_fill"] = passed & ok_sr & ok_st           # reco+truth in-range -> response
    idx["s_fill_r"] = g_sr; idx["s_fill_t"] = g_st
    idx["s_fake"] = passed & ok_sr & (~ok_st)         # reco in-range, truth out -> fake
    g_td, ok_td = gbin(d["td_tpt"], d["td_tpz"]); idx["td_g"] = g_td; idx["td_ok"] = ok_td
    g_b, ok_b = gbin(d["b_rpt"], d["b_rpz"]); idx["b_g"] = g_b; idx["b_ok"] = ok_b
    return idx


def make_response_measured(d, idx, wmul_data=None, wmul_s=None, wmul_td=None, wmul_b=None, potscale=1.0):
    """Return (resp_th2, truth_th1, reco_th1, meas_th1) built from (optionally Poisson-weighted) arrays."""
    import ROOT
    ws = d["s_wt"] * potscale * (wmul_s if wmul_s is not None else 1.0)
    wtd = d["td_w"] * potscale * (wmul_td if wmul_td is not None else 1.0)
    # response reco x truth (matched), truth denom (all), reco (matched+fakes)
    m = idx["s_fill"]
    resp, _, _ = np.histogram2d(idx["s_fill_r"][m], idx["s_fill_t"][m], bins=[np.arange(NB + 1), np.arange(NB + 1)], weights=ws[m])
    truth, _ = np.histogram(idx["td_g"][idx["td_ok"]], bins=np.arange(NB + 1), weights=wtd[idx["td_ok"]])
    reco_matched, _ = np.histogram(idx["s_fill_r"][m], bins=np.arange(NB + 1), weights=ws[m])
    fk = idx["s_fake"]
    reco_fake, _ = np.histogram(idx["s_fill_r"][fk], bins=np.arange(NB + 1), weights=(d["s_wr"] * potscale * (wmul_s if wmul_s is not None else 1.0))[fk])
    reco = reco_matched + reco_fake
    # measured data - POT*bkg
    wd = d["data_w"] * (wmul_data if wmul_data is not None else 1.0)
    meas_d, _ = np.histogram(idx["data_g"][idx["data_ok"]], bins=np.arange(NB + 1), weights=wd[idx["data_ok"]])
    pot = (d["dataPOT"] / d["mcPOT"]) if d["mcPOT"] else 1.0
    if idx["b_g"].size:
        wb = d["b_w"] * pot * (wmul_b if wmul_b is not None else 1.0)
        meas_b, _ = np.histogram(idx["b_g"][idx["b_ok"]], bins=np.arange(NB + 1), weights=wb[idx["b_ok"]])
    else:
        meas_b = np.zeros(NB)
    meas = np.clip(meas_d - meas_b, 0, None)
    # numpy -> ROOT
    def th1(name, a):
        h = ROOT.TH1D(name, name, NB, 0, NB)
        for i in range(NB): h.SetBinContent(i + 1, float(a[i]))
        return h
    hresp = ROOT.TH2D("hresp", "hresp", NB, 0, NB, NB, 0, NB)
    for i in range(NB):
        for j in range(NB):
            if resp[i, j]: hresp.SetBinContent(i + 1, j + 1, float(resp[i, j]))
    return hresp, th1("htruth", truth), th1("hreco", reco), th1("hmeas", meas)


def unfold(kind, hresp, htruth, hreco, hmeas, niter):
    import ROOT
    resp = ROOT.RooUnfoldResponse(hreco, htruth, hresp)
    if kind == "ibu":
        u = ROOT.RooUnfoldBayes(resp, hmeas, niter)
    else:
        try:
            u = ROOT.RooUnfoldOmnifold(resp, hmeas, niter, False)  # useDensity=False (count space)
        except TypeError:
            u = ROOT.RooUnfoldOmnifold(resp, hmeas, niter)
    try: u.SetVerbose(0)
    except Exception: pass
    h = u.Hunfold() if hasattr(u, "Hunfold") else u.Hreco()
    return np.array([h.GetBinContent(i + 1) for i in range(NB)])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--omnifile", default="2d-unfolding/runEventLoopOmniFold_MEFHC.root")
    ap.add_argument("--niter", type=int, default=5)
    ap.add_argument("--replicas", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20260716)
    ap.add_argument("--streams", default="both", choices=["both", "data", "mc"])
    ap.add_argument("--rank", type=int, default=0, help="pinv rank cut (0 = auto by rcond)")
    ap.add_argument("--out", default="2d-unfolding/uq/ibu_omnifold_cdelta")
    a = ap.parse_args()
    import ROOT
    ROOT.gROOT.SetBatch(True); ROOT.gErrorIgnoreLevel = ROOT.kError
    try: ROOT.EnableImplicitMT()      # faster RDataFrame load of the 32.8M-event trees
    except Exception: pass
    ROOT.gSystem.Load("libRooUnfold.so")

    print(f"[load] {a.omnifile}"); d = load_events(a.omnifile); idx = build_indices(d)
    print(f"[load] data={d['data_pt'].size} sig={d['s_rpt'].size} td={d['td_tpt'].size} bkg={d['b_rpt'].size}")

    # nominal
    hR, hT, hRe, hM = make_response_measured(d, idx)
    x_of0 = unfold("of", hR, hT, hRe, hM, a.niter)
    x_ibu0 = unfold("ibu", hR, hT, hRe, hM, a.niter)
    print(f"[nominal] sum x_OF={x_of0.sum():.4e} x_IBU={x_ibu0.sum():.4e} "
          f"rel-diff(total)={(x_of0.sum()-x_ibu0.sum())/x_ibu0.sum():+.3%}")

    rng = np.random.default_rng(a.seed)
    deltas = []
    for r in range(a.replicas):
        wmul_data = rng.poisson(1.0, d["data_pt"].size).astype(float) if a.streams in ("both", "data") else None
        if a.streams in ("both", "mc"):
            wmul_s = rng.poisson(1.0, d["s_rpt"].size).astype(float)
            wmul_td = rng.poisson(1.0, d["td_tpt"].size).astype(float)
            wmul_b = rng.poisson(1.0, d["b_rpt"].size).astype(float)
        else:
            wmul_s = wmul_td = wmul_b = None
        hR, hT, hRe, hM = make_response_measured(d, idx, wmul_data, wmul_s, wmul_td, wmul_b)
        xof = unfold("of", hR, hT, hRe, hM, a.niter)
        xibu = unfold("ibu", hR, hT, hRe, hM, a.niter)
        deltas.append(xof - xibu)
        if (r + 1) % 20 == 0: print(f"  [rep {r+1}/{a.replicas}]", flush=True)
    D = np.array(deltas)                                   # (R, NB)
    rep = (x_of0 > 0) & (x_ibu0 > 0) & (D.std(axis=0) > 0)
    nb = int(rep.sum())
    Dr = D[:, rep]
    delta_bar = (x_of0 - x_ibu0)[rep]
    C = np.cov(Dr, rowvar=False)                           # (nb, nb)
    # statistic with declared rank/pseudoinverse
    rcond = 1e-10
    Cpinv = np.linalg.pinv(C, rcond=rcond) if a.rank <= 0 else _pinv_rank(C, a.rank)
    T = float(delta_bar @ Cpinv @ delta_bar)
    ev = np.linalg.eigvalsh(0.5 * (C + C.T)); rank_eff = int((ev > ev[-1] * rcond).sum())
    from scipy import stats
    dof = a.rank if a.rank > 0 else rank_eff
    pval = float(stats.chi2.sf(T, dof)) if dof > 0 else float("nan")
    out = {
        "estimators": "RooUnfoldBayes (IBU) vs RooUnfoldOmnifold (binned), niter=%d" % a.niter,
        "space": "unfolded truth-count (efficiency/flux/POT common to both -> cancel in T)",
        "grid": "14x16=224 flattened; reported=%d" % nb, "replicas": a.replicas, "streams": a.streams,
        "seed": a.seed, "n_bins": nb, "rank_eff": rank_eff, "dof": dof,
        "nominal_total_OF": float(x_of0.sum()), "nominal_total_IBU": float(x_ibu0.sum()),
        "delta_bar_norm": float(np.linalg.norm(delta_bar)),
        "method_diff_statistic_T": T, "chi2_over_dof": T / dof if dof else None, "p_value": pval,
        "median_abs_delta_over_of": float(np.median(np.abs(delta_bar) / np.clip(x_of0[rep], 1e-30, None))),
        "note": "paired data+MC bootstrap through the SAME response; C_delta captures the cancelling "
                "shared fluctuations the summed-covariance chi2 omits. Systematic-universe pass is a "
                "separate extension (shift the response per MAT universe, both estimators).",
    }
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out + ".json", "w") as fh: json.dump(out, fh, indent=2)
    print(f"[C_delta] reported bins={nb} rank_eff={rank_eff} dof={dof}")
    print(f"[C_delta] T={T:.3f} chi2/dof={T/dof if dof else float('nan'):.3f} p={pval:.3g} "
          f"median|delta|/OF={out['median_abs_delta_over_of']:.3%}")
    print(f"[wrote] {a.out}.json")


def _pinv_rank(C, k):
    u, s, vt = np.linalg.svd(0.5 * (C + C.T))
    inv = np.zeros_like(s); inv[:k] = 1.0 / s[:k]
    return (vt.T * inv) @ u.T


if __name__ == "__main__":
    main()
