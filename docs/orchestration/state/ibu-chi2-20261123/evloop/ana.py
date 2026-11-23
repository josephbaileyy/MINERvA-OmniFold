# ibuchi offline pass: merged rerun -> binned (M, T, B, N) per variant + data-only scan histograms. Writes ROOT/products.
import sys, json, numpy as np, ROOT
ROOT.EnableImplicitMT(16)
R = "/pscratch/sd/j/josephrb/ibuchi-evloop-20261123"; F = R + "/out/runEventLoopOmniFold_MEFHC.root"
PT = np.array([0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50]); PZ = np.array([1.5,2,2.5,3,3.5,4,4.5,5,6,7,8,9,10,15,20,40,60])
def gidx(pt, pz):
    with np.errstate(invalid="ignore"):
        ip = np.searchsorted(PT, pt, side="right") - 1; iz = np.searchsorted(PZ, pz, side="right") - 1
        ok = np.isfinite(pt) & np.isfinite(pz) & (pt >= 0) & (pt <= 4.5) & (pz >= 1.5) & (pz <= 60) & (ip >= 0) & (ip < 14) & (iz >= 0) & (iz < 16)
    return np.where(ok, ip * 16 + iz, -1)
def kin(p, th): return p / 1000 * np.sin(th), p / 1000 * np.cos(th)
def th3(tx, ty): return np.arctan(np.sqrt(np.tan(tx)**2 + np.tan(ty)**2))
f = ROOT.TFile.Open(F); s = f.Get("dataPOTUsed").GetVal() / f.Get("mcPOTUsed").GetVal(); f.Close()
MU = ["mu_p_total", "mu_p_minos", "mu_used_curv", "mu_trk_quality", "mu_trk_eqp_qp", "mu_mad_p", "mu_thetaX", "mu_thetaY", "mu_theta"]
sig = ROOT.RDataFrame("mc_signal_reco", F).AsNumpy(["sim", "sim_pz", "sim_pass", "w_reco", "MC", "MC_pz", "w_truth"] + MU)
bkg = ROOT.RDataFrame("mc_background", F).AsNumpy(["sim_background", "sim_background_pz", "sim_background_pass", "w_bkg"] + MU)
dat = ROOT.RDataFrame("data", F).AsNumpy(["measured", "measured_pz", "measured_pass"] + MU)
out = {"pot_scale": s, "n_sig": int(len(sig["sim"])), "n_bkg": int(len(bkg["w_bkg"])), "n_data": int(len(dat["measured"]))}
# controls on reco rows
def ctl_kin(a, x, z, passed):
    m = passed & (a["mu_p_total"] > 0)
    pt, pz = kin(a["mu_p_total"][m], a["mu_theta"][m])
    return float(max(np.max(np.abs(pt - a[x][m])), np.max(np.abs(pz - a[z][m])))), float(np.max(np.abs(th3(a["mu_thetaX"][m], a["mu_thetaY"][m]) - a["mu_theta"][m])))
out["C_KIN_sig"], out["C_ANG_sig"] = ctl_kin(sig, "sim", "sim_pz", sig["sim_pass"] != 0)
out["C_KIN_bkg"], out["C_ANG_bkg"] = ctl_kin(bkg, "sim_background", "sim_background_pz", bkg["sim_background_pass"] != 0)
out["C_KIN_data"], out["C_ANG_data"] = ctl_kin(dat, "measured", "measured_pz", dat["measured_pass"] != 0)
# common pieces
tp, tz = sig["MC"].astype(float), sig["MC_pz"].astype(float); wt, wr = sig["w_truth"].astype(float), sig["w_reco"].astype(float)
good = np.isfinite(wt) & np.isfinite(wr) & (wt >= 0) & (wt < 1e4) & (wr >= 0) & (wr < 1e4); wt, wr = wt * s, wr * s
with np.errstate(invalid="ignore"):
    tru = np.isfinite(tp) & np.isfinite(tz) & (tp >= 0) & (tp <= 4.5) & (tz >= 1.5) & (tz <= 60) & (np.arctan2(tp, tz) < np.radians(20))
t = gidx(tp, tz); kt = good & tru & (t >= 0); T = np.bincount(t[kt], weights=wt[kt], minlength=224)
bw = bkg["w_bkg"].astype(float); bok = (bkg["sim_background_pass"] != 0) & np.isfinite(bw) & (bw >= 0) & (bw < 1e6)
dok = dat["measured_pass"] != 0
def Q(a): return (a["mu_trk_quality"] == 1) & ((a["mu_used_curv"] == 0) | (np.abs(a["mu_trk_eqp_qp"]) < 0.3))
def build(sig_pt, sig_pz, sig_sel, b_pt, b_pz, b_sel, d_pt, d_pz, d_sel):
    r = gidx(sig_pt, sig_pz); km = kt & sig_sel & (r >= 0); M = np.zeros((224, 224)); np.add.at(M, (r[km], t[km]), wr[km])
    g = gidx(b_pt, b_pz); mb = bok & b_sel & (g >= 0); Bv = np.bincount(g[mb], weights=bw[mb] * s, minlength=224)
    gd = gidx(d_pt, d_pz); md = dok & d_sel & (gd >= 0); N = np.bincount(gd[md], minlength=224).astype(float)
    return M, Bv, N
sp = sig["sim_pass"] != 0
prod = {}
prod["BASE"] = build(sig["sim"], sig["sim_pz"], sp, bkg["sim_background"], bkg["sim_background_pz"], np.ones(len(bw), bool), dat["measured"], dat["measured_pz"], np.ones(len(dok), bool))
prod["SEL"] = build(sig["sim"], sig["sim_pz"], sp & Q(sig), bkg["sim_background"], bkg["sim_background_pz"], Q(bkg), dat["measured"], dat["measured_pz"], Q(dat))
ks, kb, kd = kin(sig["mu_mad_p"], sig["mu_theta"]), kin(bkg["mu_mad_p"], bkg["mu_theta"]), kin(dat["mu_mad_p"], dat["mu_theta"])
# Signal rows keep sim_pass set on truth-only misses, whose mu_* are -9999 (smoke, 2026-11-23); require a real
# reco muon so -9999 MeV at a -9999 rad angle cannot land in the grid. sim itself is -9999 there, so BASE/SEL are safe.
prod["MAD"] = build(ks[0], ks[1], sp & (sig["mu_mad_p"] > 0), kb[0], kb[1], bkg["mu_mad_p"] > 0, kd[0], kd[1], dat["mu_mad_p"] > 0)
# data-only scans (N only)
pmin, pmo, curv = dat["mu_p_total"] - dat["mu_p_minos"], dat["mu_p_minos"], dat["mu_used_curv"] == 1
D = np.round(np.arange(-0.03, 0.03001, 0.001), 4); scanC, scanR = [], []
for d in D:
    for which, lst in ((curv, scanC), (~curv, scanR)):
        p = np.where(which, pmin + pmo * (1 + d), dat["mu_p_total"]); pt, pz = kin(p, dat["mu_theta"])
        g = gidx(pt, pz); m = dok & (g >= 0); lst.append(np.bincount(g[m], minlength=224))
A = np.round(np.arange(-0.003, 0.003001, 0.00025), 6); scanA = np.zeros((len(A), len(A), 224))
for i, dx in enumerate(A):
    for j, dy in enumerate(A):
        th = th3(dat["mu_thetaX"] + dx, dat["mu_thetaY"] + dy); pt, pz = kin(dat["mu_p_total"], th)
        g = gidx(pt, pz); m = dok & (g >= 0); scanA[i, j] = np.bincount(g[m], minlength=224)
np.savez_compressed(R + "/products/ibuchi_products.npz", T=T, **{f"{k}_{x}": v for k, (M, Bv, N) in prod.items() for x, v in (("M", M), ("B", Bv), ("N", N))},
                    scan_d=D, scanC=np.array(scanC), scanR=np.array(scanR), scan_a=A, scanA=scanA)
out["frac_curv_data"] = float(np.mean(curv[dok])); out["frac_Q_data"] = float(np.mean(Q(dat)[dok]))
print(json.dumps(out))
