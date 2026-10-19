"""Q3: J-cell effect of the generator W convention (fixed M_n, W=0 if W^2<=0) vs the analysis
convention (struck-nucleon M as CVUniverse, NaN rows dropped), with the flux-fix weights r(E)."""
import json, sys, glob, importlib.util, os
import numpy as np
HERE = sys.argv[1]; OUT = sys.argv[2]
S5P = "/pscratch/sd/j/josephrb/s5p-20260926"
REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
G = f"{REPO}/3d-unfolding/genie"
sys.path.insert(0, f"{S5P}/gen5d/code/tree/3d-unfolding/genie")
import gen_to_xsec5d as g5
import ROOT
spec = importlib.util.spec_from_file_location("ffx", f"{S5P}/gen5d_fluxfix/code/gen5d_flux_reweight.py")
ffx = importlib.util.module_from_spec(spec); spec.loader.exec_module(ffx)
ROOT.gErrorIgnoreLevel = ROOT.kError
J = json.load(open(os.path.join(HERE, "jcells.json")))
JE = [np.asarray(J["edges"][a], float) for a in g5.AXES]
SUP = np.asarray(J["supported_cells"])
FE = [g5.EDGES[a] for a in g5.AXES]
z, _, phit_path = ffx.load_phi_t(f"{S5P}/gen5d_fluxfix")
edges, phi_t, Phi_t = z["edges"], z["phi_t_density"], float(z["Phi_t"])

def binidx(x, e):
    i = np.searchsorted(e, x, side="right") - 1
    i = np.where(x == e[-1], e.size - 2, i)
    return np.where((x >= e[0]) & (x <= e[-1]), i, -1)

def jcell(cols):
    """coarse C-order index (pt,pz,eavail,q3,W); -1 outside the fine grid / non-finite."""
    ok = np.ones(cols[0].size, bool)
    for x, e in zip(cols, FE):
        ok &= np.isfinite(x) & (binidx(np.nan_to_num(x, nan=-1e9), e) >= 0)
    ij = [binidx(np.nan_to_num(x, nan=-1e9), e) for x, e in zip(cols, JE)]
    c = np.ravel_multi_index([np.clip(i, 0, 2) for i in ij], (3,) * 5)
    return np.where(ok, c, -1)

def compare(label, base, W_fix, W_ana, w):
    cf = jcell(base + [W_fix]); ca = jcell(base + [W_ana])
    out = {"n_events_in_ps": int(W_fix.size), "n_in_grid_fixed": int((cf >= 0).sum()),
           "n_in_grid_analysis": int((ca >= 0).sum()), "n_W_nan_analysis": int(np.isnan(W_ana).sum()),
           "n_W_zero_fixed": int((W_fix == 0).sum()),
           "n_events_change_Jcell": int((cf != ca).sum()),
           "n_events_change_fine_W_bin": int((binidx(W_fix, FE[4]) != binidx(np.nan_to_num(W_ana, nan=-1), FE[4])).sum())}
    for wl, ww in (("flux_fix_weighted", w), ("unweighted", np.ones_like(w))):
        mf = np.bincount(cf[cf >= 0], ww[cf >= 0], minlength=243)
        ma = np.bincount(ca[ca >= 0], ww[ca >= 0], minlength=243)
        rel = ma[SUP] / mf[SUP] - 1.0
        k = int(np.argmax(np.abs(rel)))
        # MC stat of the difference: events that moved, as a scale
        moved = (cf != ca)
        out[wl] = {"median_abs_rel": float(np.median(np.abs(rel))), "max_abs_rel": float(np.max(np.abs(rel))),
                   "argmax_cell": int(SUP[k]), "argmax_cell_multiindex": [int(i) for i in np.unravel_index(SUP[k], (3,) * 5)],
                   "rel_at_argmax": float(rel[k]), "n_cells_abs_rel_gt_1e-3": int((np.abs(rel) > 1e-3).sum()),
                   "rel_quantiles_signed_10_50_90": [float(q) for q in np.quantile(rel, [.1, .5, .9])],
                   "total_rel_supported": float(ma[SUP].sum() / mf[SUP].sum() - 1),
                   "total_rel_all_cells": float(ma.sum() / mf.sum() - 1),
                   "moved_weight_frac": float(ww[moved].sum() / ww.sum())}
    nf = np.bincount(cf[cf >= 0], minlength=243); sw = np.bincount(cf[cf >= 0], w[cf >= 0], minlength=243)
    sw2 = np.bincount(cf[cf >= 0], w[cf >= 0] ** 2, minlength=243)
    mv = cf != ca
    nin = np.bincount(ca[mv & (ca >= 0)], minlength=243); nout = np.bincount(cf[mv & (cf >= 0)], minlength=243)
    ma = np.bincount(ca[ca >= 0], w[ca >= 0], minlength=243)
    rel = ma[SUP] / sw[SUP] - 1.0
    statrel = np.sqrt(sw2[SUP]) / sw[SUP]
    out["shift_over_mc_stat_rel"] = {"median": float(np.median(np.abs(rel) / statrel)), "max": float(np.max(np.abs(rel) / statrel))}
    order = np.argsort(-np.abs(rel))[:5]
    out["top5_cells"] = [{"cell": int(SUP[i]), "idx": [int(x) for x in np.unravel_index(SUP[i], (3,) * 5)],
                          "rel": float(rel[i]), "n_events_fixed": int(nf[SUP[i]]), "n_moved_in": int(nin[SUP[i]]),
                          "n_moved_out": int(nout[SUP[i]]), "mc_stat_rel": float(statrel[i])} for i in order]
    out["per_cell_rel_weighted"] = {int(c): float(v) for c, v in zip(SUP, (np.bincount(ca[ca >= 0], w[ca >= 0], minlength=243)[SUP] /
                                                                        np.bincount(cf[cf >= 0], w[cf >= 0], minlength=243)[SUP] - 1))}
    return out

res = {"jcells": J["source"], "n_supported": int(SUP.size), "phi_t": phit_path, "inputs": []}

# ---------------- GENIE CV ----------------
gst = f"{G}/genie_mefhc_cv_ALL.gst.root"; flux = f"{G}/flux_mefhc_numu.root"; graphs = f"{G}/xsec_graphs.root"
ev, norm, diag = g5.extract_genie(gst, False, graphs, flux, "flux_numu", 0)
d = ROOT.RDataFrame("gst", gst).AsNumpy(["cc", "Ev", "El", "pxl", "pyl", "pzl", "hitnuc"])
cc = d["cc"].astype(bool); pt = np.hypot(d["pxl"], d["pyl"]); pz = d["pzl"]
in_ps = g5.u3d.u2d.in_truth_phase_space
sel = np.where(np.fromiter((c and in_ps(float(a), float(b), g5.PT[0], g5.PT[-1], g5.PZ[0], g5.PZ[-1])
                            for c, a, b in zip(cc.tolist(), pt.tolist(), pz.tolist())), bool, cc.size))[0]
assert np.array_equal(pt[sel], ev["pt"]) and np.array_equal(pz[sel], ev["pz"])
pmu = np.sqrt(d["pxl"][sel] ** 2 + d["pyl"][sel] ** 2 + pz[sel] ** 2)
Wana = g5.w_struck(d["Ev"][sel], d["El"][sel], pz[sel], pmu, d["hitnuc"][sel])
e_s, c_s = ffx.read_th1(ROOT, flux, "flux_numu")
_, rbin, rng = ffx.flux_weights(e_s, c_s, phi_t, Phi_t, *ffx.GEN_RANGE["genie_cv"])
r = ffx.r_of(d["Ev"][sel], e_s, rbin, rng)
hn = d["hitnuc"][sel]
res["genie_cv"] = {"gst": gst, "hitnuc_counts": {str(int(k)): int(v) for k, v in zip(*np.unique(hn, return_counts=True))},
                   "flux_weight": "r(E) = (phi_t/Phi_t)/phi_s, gen5d_flux_reweight.flux_weights, range 0-50 GeV; "
                                  "the 50-100 GeV supplement sample is NOT included",
                   **compare("genie_cv", [ev["pt"], ev["pz"], ev["eavail"], ev["q3"]], ev["W"], Wana, r)}
res["inputs"] += [gst, flux]
del d

# ---------------- NuWro ----------------
files = sorted(glob.glob(f"{S5P}/gen5d/nuwro_flat5d/nuwro_flat5d_p*.root"))
cols = ["cc", "pt", "pz", "eavail", "W", "weight", "Enu", "q0", "q3", "hitnuc"]
acc = {k: [] for k in cols}
for fn in files:
    dd = ROOT.RDataFrame("nuwro_obs", fn).AsNumpy(cols)
    for k in cols:
        acc[k].append(np.asarray(dd[k]))
d = {k: np.concatenate(v) for k, v in acc.items()}
d = {k: v[d["cc"].astype(bool)] for k, v in d.items()}
m = (np.isfinite(d["pt"]) & np.isfinite(d["pz"]) & (d["pt"] >= g5.PT[0]) & (d["pt"] <= g5.PT[-1])
     & (d["pz"] >= g5.PZ[0]) & (d["pz"] <= g5.PZ[-1]) & (np.arctan2(d["pt"], d["pz"]) < g5.u3d.u2d.MAX_MUON_THETA_RAD))
d = {k: v[m] for k, v in d.items()}
pmu = np.sqrt(d["pt"] ** 2 + d["pz"] ** 2)
Emu = d["Enu"] - d["q0"]
Wana = g5.w_struck(d["Enu"], Emu, d["pz"], pmu, d["hitnuc"])
# check the stored W is the fixed-M_n convention
w2f = g5.CVU_M_N ** 2 + 2 * g5.CVU_M_N * d["q0"] - 4 * d["Enu"] * Emu * np.sin(np.arccos(np.clip(d["pz"] / pmu, -1, 1)) / 2) ** 2
Wfix_re = np.where(w2f > 0, np.sqrt(np.maximum(w2f, 0)), 0.0)
fluxn = f"{G}/flux_mefhc_numu_nuwro.root"
e_s, c_s = ffx.read_th1(ROOT, fluxn, "flux_numu")
_, rbin, rng = ffx.flux_weights(e_s, c_s, phi_t, Phi_t, *ffx.GEN_RANGE["nuwro"])
r = ffx.r_of(d["Enu"], e_s, rbin, rng) * d["weight"]
res["nuwro"] = {"files": files, "stored_W_vs_recomputed_fixedMn_maxabs_GeV": float(np.nanmax(np.abs(d["W"] - Wfix_re))),
                "hitnuc_counts": {str(int(k)): int(v) for k, v in zip(*np.unique(d["hitnuc"], return_counts=True))},
                "flux_weight": "weight_e * r(E), range 0.5-50 GeV; 50-100 GeV supplement NOT included",
                **compare("nuwro", [d["pt"], d["pz"], d["eavail"], d["q3"]], d["W"].astype(float), Wana, r)}
res["inputs"] += files + [fluxn]
res["input_sha256"] = {p: ffx.sha256(p) for p in res["inputs"] + [phit_path]}
json.dump(res, open(OUT, "w"), indent=1)
s = {k: {kk: vv for kk, vv in v.items() if kk != "per_cell_rel_weighted"} if isinstance(v, dict) else v for k, v in res.items()}
print(json.dumps(s, indent=1))
