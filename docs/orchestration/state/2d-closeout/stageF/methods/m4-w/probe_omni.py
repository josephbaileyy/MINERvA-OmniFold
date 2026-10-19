"""Q2 on the 5D CV omnifile: truth-W residual vs (pT,p||,q3), and the reco W identity."""
import json, sys, math
import numpy as np
import ROOT
sys.path.insert(0, sys.argv[2])
import common as C

ROOT.gErrorIgnoreLevel = ROOT.kError
fn, out = sys.argv[1], sys.argv[3]
TH = math.radians(20.0)
res = {"file": fn}

def ps_gate(pt, pz):   # u2d.in_truth_phase_space, vectorised (inclusive bounds, atan2 < 20 deg)
    return (pt >= 0) & (pt <= 4.5) & (pz >= 1.5) & (pz <= 60) & (np.arctan2(pt, pz) < TH)

# ---------------- truth (mc_truth_denom) ----------------
d = ROOT.RDataFrame("mc_truth_denom", fn).AsNumpy(["MC", "MC_pz", "MC_q3", "MC_W", "w_truth"])
pt, pz, q3, W, w = (np.asarray(d[k], float) for k in ("MC", "MC_pz", "MC_q3", "MC_W", "w_truth"))
del d
n_all = pt.size
fin_nonW = np.isfinite(pt) & np.isfinite(pz) & np.isfinite(q3) & np.isfinite(w) & (w >= 0) & (w < 1e4)
inps = fin_nonW & ps_gate(pt, pz)
nanW = inps & ~np.isfinite(W)
keep = inps & np.isfinite(W)                      # = und collect_truth_denom_nd kept rows
res["truth"] = {"n_entries": int(n_all), "n_in_ps_finite_nonW": int(inps.sum()),
                "n_W_nonfinite_in_ps": int(nanW.sum()),
                "w_frac_W_nonfinite_in_ps": float(w[nanW].sum() / w[inps].sum()),
                "n_kept": int(keep.sum())}
pt, pz, q3, W, w = (a[keep] * (1000.0 if a is not w else 1.0) for a in (pt, pz, q3, W, w))
res["truth"]["q3sq_minus_pt2_negative"] = int((q3 * q3 - pt * pt < 0).sum())
res["truth"]["q3sq_minus_pt2_negative_wfrac"] = float(w[q3 * q3 - pt * pt < 0].sum() / w.sum())
Wb, disc, enu = C.w_pred(pt, pz, q3, np.full_like(pt, C.M_BAR))
r = W - Wb
res["truth"]["resid_Mbar_MeV"] = C.summarize(r)
res["truth"]["n_Wpred_nan"] = int(np.isnan(Wb).sum())
# per-event M unavailable: oracle (best of M_n, M_p, M_bar) as a lower envelope on the M part
cands = np.stack([C.w_pred(pt, pz, q3, np.full_like(pt, m))[0] for m in (C.M_N, C.M_P, C.M_BAR)])
dif = W[None, :] - cands
with np.errstate(invalid="ignore"):
    ib = np.nanargmin(np.where(np.isfinite(dif), np.abs(dif), np.inf), axis=0)
r_or = np.take_along_axis(dif, ib[None, :], 0)[0]
res["truth"]["resid_oracleM_MeV"] = C.summarize(r_or)
ok = np.isfinite(Wb)
fb = C.wbin(W, C.W_FINE) != C.wbin(np.where(ok, Wb, -1), C.W_FINE)
jb = C.wbin(W, C.W_J) != C.wbin(np.where(ok, Wb, -1), C.W_J)
wo = np.isfinite(cands[ib, np.arange(pt.size)])
fbo = C.wbin(W, C.W_FINE) != C.wbin(np.where(wo, W - r_or, -1), C.W_FINE)
jbo = C.wbin(W, C.W_J) != C.wbin(np.where(wo, W - r_or, -1), C.W_J)
res["truth"]["bin_change"] = {
    "fine_frac_unweighted_Mbar": float(fb.mean()), "fine_frac_weighted_Mbar": float(w[fb].sum() / w.sum()),
    "J_frac_unweighted_Mbar": float(jb.mean()), "J_frac_weighted_Mbar": float(w[jb].sum() / w.sum()),
    "fine_frac_unweighted_oracleM": float(fbo.mean()), "J_frac_unweighted_oracleM": float(jbo.mean()),
    "note": "W_pred NaN rows (q3<pT) count as changed"}
# residual by true-W J bin and by pT
res["truth"]["resid_Mbar_by_W_J_bin"] = [dict(Wbin=[float(a), float(b)], **C.summarize(r[(W >= a) & (W < b)]))
                                         for a, b in zip(C.W_J[:-1], C.W_J[1:])]
pte = [0, 250, 550, 850, 1500, 4500.01]
res["truth"]["resid_Mbar_by_pT"] = [dict(pT=[a, b], **C.summarize(r[(pt >= a) & (pt < b)])) for a, b in zip(pte[:-1], pte[1:])]
del pt, pz, q3, W, w, cands, dif, r, r_or

# ---------------- reco: W_reco^2 = (M_bar+q0)^2 - q3^2, q0 recovered from (pT,p||,q3) ----------------
def reco_check(tree, names, passname):
    dd = ROOT.RDataFrame(tree, fn).Define("pass_i", f"(int){passname}").AsNumpy(names + ["pass_i"])
    a = {k: np.asarray(v, float) for k, v in dd.items()}
    sel = (a["pass_i"] != 0) & np.all([np.isfinite(a[k]) for k in names], axis=0)
    pt, pz, q3, W = (a[k][sel] * 1000.0 for k in names)
    p2 = pt * pt + pz * pz
    emu = np.sqrt(p2 + C.M_MU ** 2)
    aa = emu - pz
    c = 2 * emu * aa - C.M_MU ** 2
    with np.errstate(invalid="ignore"):
        q0 = -aa + np.sqrt(aa * aa - c + q3 * q3)
    Q2 = 2 * (emu + q0) * aa - C.M_MU ** 2
    clamp = ~(Q2 >= 0)
    q0 = np.where(clamp, q3, q0)                  # Q^2 clamp fired -> q3 == q0
    w2 = (C.M_BAR + q0) ** 2 - q3 * q3
    Wp = np.sqrt(np.maximum(w2, 0.0))
    rr = W - Wp
    return {"n_pass_finite": int(sel.sum()), "n_Q2_clamp": int(clamp.sum()), "n_W2_clamp": int((w2 < 0).sum()),
            "resid_MeV": C.summarize(rr), "max_rel": float(np.max(np.abs(rr) / np.maximum(W, 1.0)))}

res["reco_sim"] = reco_check("mc_signal_reco", ["sim", "sim_pz", "sim_q3", "sim_W"], "sim_pass")
res["reco_data"] = reco_check("data", ["measured", "measured_pz", "measured_q3", "measured_W"], "measured_pass")
json.dump(res, open(out, "w"), indent=1)
print(json.dumps(res, indent=1))
