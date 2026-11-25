# ibuchi rebuild: binned (M, T, B, N, Mflow) on the OLD and the paper (E) pT edges, from this lane's merged evloop output.
# Same selections and weights as evloop/ana.py BASE. Writes ROOT/products/rebuild/rebuild.npz only.
import os, json, numpy as np, ROOT
ROOT.EnableImplicitMT(16)
R = "/pscratch/sd/j/josephrb/ibuchi-evloop-20261123"; F = R + "/out/runEventLoopOmniFold_MEFHC.root"
PZ = np.array([1.5,2,2.5,3,3.5,4,4.5,5,6,7,8,9,10,15,20,40,60])
EDGES = {"OLD": np.array([0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50]),
         "E":   np.array([0,0.075,0.15,0.25,0.325,0.40,0.475,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50])}
def gidx(PT, pt, pz):
    with np.errstate(invalid="ignore"):
        ip = np.searchsorted(PT, pt, side="right") - 1; iz = np.searchsorted(PZ, pz, side="right") - 1
        ok = np.isfinite(pt) & np.isfinite(pz) & (pt >= 0) & (pt <= 4.5) & (pz >= 1.5) & (pz <= 60) & (ip >= 0) & (ip < 14) & (iz >= 0) & (iz < 16)
    return np.where(ok, ip * 16 + iz, -1)
f = ROOT.TFile.Open(F); s = f.Get("dataPOTUsed").GetVal() / f.Get("mcPOTUsed").GetVal(); f.Close()
sig = ROOT.RDataFrame("mc_signal_reco", F).Define("sp_i", "(int)sim_pass").AsNumpy(["sim", "sim_pz", "sp_i", "w_reco", "MC", "MC_pz", "w_truth", "mu_p_total"])
bkg = ROOT.RDataFrame("mc_background", F).Define("bp_i", "(int)sim_background_pass").AsNumpy(["sim_background", "sim_background_pz", "bp_i", "w_bkg"])
dat = ROOT.RDataFrame("data", F).Define("mp_i", "(int)measured_pass").AsNumpy(["measured", "measured_pz", "mp_i"])
g = lambda a, k: np.asarray(a[k], dtype=float)
tp, tz, wt, wr = g(sig, "MC"), g(sig, "MC_pz"), g(sig, "w_truth"), g(sig, "w_reco")
good = np.isfinite(wt) & np.isfinite(wr) & (wt >= 0) & (wt < 1e4) & (wr >= 0) & (wr < 1e4); wt, wr = wt * s, wr * s
with np.errstate(invalid="ignore"):
    tru = np.isfinite(tp) & np.isfinite(tz) & (tp >= 0) & (tp <= 4.5) & (tz >= 1.5) & (tz <= 60) & (np.arctan2(tp, tz) < np.radians(20))
sp = g(sig, "sp_i") != 0; mp = g(sig, "mu_p_total") > 0
bw = g(bkg, "w_bkg"); bok = (g(bkg, "bp_i") != 0) & np.isfinite(bw) & (bw >= 0) & (bw < 1e6)
dok = g(dat, "mp_i") != 0
out = {}
for X, PT in EDGES.items():
    t = gidx(PT, tp, tz); kt = good & tru & (t >= 0); T = np.bincount(t[kt], weights=wt[kt], minlength=224)
    r = gidx(PT, g(sig, "sim"), g(sig, "sim_pz")); km = kt & sp & (r >= 0); M = np.zeros((224, 224)); np.add.at(M, (r[km], t[km]), wr[km])
    kf = kt & sp & mp & (r < 0); Mflow = np.bincount(t[kf], weights=wr[kf], minlength=224)
    gb = gidx(PT, g(bkg, "sim_background"), g(bkg, "sim_background_pz")); mb = bok & (gb >= 0); B = np.bincount(gb[mb], weights=bw[mb] * s, minlength=224)
    gd = gidx(PT, g(dat, "measured"), g(dat, "measured_pz")); md = dok & (gd >= 0); N = np.bincount(gd[md], minlength=224).astype(float)
    out.update({f"{X}_M": M, f"{X}_T": T, f"{X}_B": B, f"{X}_N": N, f"{X}_Mflow": Mflow})
os.makedirs(R + "/products/rebuild", exist_ok=True)
np.savez_compressed(R + "/products/rebuild/rebuild.npz", pot_scale=s, **out)
print(json.dumps({"pot_scale": s, **{k: float(v.sum()) for k, v in out.items()}}))
