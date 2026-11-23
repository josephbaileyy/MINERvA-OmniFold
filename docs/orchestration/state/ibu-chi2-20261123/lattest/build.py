import sys, os, json, numpy as np, ROOT
from concurrent.futures import ProcessPoolExecutor
W = "/pscratch/sd/j/josephrb/oflow-split-20261123"; LD = "/pscratch/sd/j/josephrb/cov2d-inputs-20261104/laterals"
files = {"CV": W + "/cv.root"}
for b in ("Muon_Energy_MINOS", "Muon_Energy_MINERvA", "MuonResolution", "BeamAngleX", "BeamAngleY"):
    for i in (0, 1): files[f"{b}_{i}"] = f"{LD}/runEventLoopOmniFold_5D_MEFHC_active_{b}_{i}.root"
PT = np.array([0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50]); PZ = np.array([1.5,2,2.5,3,3.5,4,4.5,5,6,7,8,9,10,15,20,40,60])
def gidx(pt, pz):
    ip = np.searchsorted(PT, pt, side="right") - 1; iz = np.searchsorted(PZ, pz, side="right") - 1
    return np.where((ip >= 0) & (ip < 14) & (iz >= 0) & (iz < 16), ip * 16 + iz, -1)
def build(item):
    name, p = item
    ROOT.EnableImplicitMT(4)
    f = ROOT.TFile.Open(p); s = f.Get("dataPOTUsed").GetVal() / f.Get("mcPOTUsed").GetVal(); f.Close()
    a = ROOT.RDataFrame("mc_signal_reco", p).AsNumpy(["sim", "sim_pz", "sim_pass", "w_reco", "MC", "MC_pz", "w_truth"])
    tp, tz, rp, rz = (a[k].astype(float) for k in ("MC", "MC_pz", "sim", "sim_pz"))
    wt, wr = a["w_truth"].astype(float), a["w_reco"].astype(float)
    good = np.isfinite(wt) & np.isfinite(wr) & (wt >= 0) & (wt < 1e4) & (wr >= 0) & (wr < 1e4)
    wt, wr = wt * s, wr * s
    with np.errstate(invalid="ignore"):
        tru = np.isfinite(tp) & np.isfinite(tz) & (tp >= 0) & (tp <= 4.5) & (tz >= 1.5) & (tz <= 60) & (np.arctan2(tp, tz) < np.radians(20))
        rec = (a["sim_pass"] != 0) & np.isfinite(rp) & np.isfinite(rz) & (rp >= 0) & (rp <= 4.5) & (rz >= 1.5) & (rz <= 60)
    t = gidx(tp, tz); r = gidx(rp, rz)
    kt = good & tru & (t >= 0); T = np.bincount(t[kt], weights=wt[kt], minlength=224)
    km = good & tru & rec & (t >= 0) & (r >= 0); M = np.zeros((224, 224)); np.add.at(M, (r[km], t[km]), wr[km])
    b = ROOT.RDataFrame("mc_background", p).AsNumpy(["sim_background", "sim_background_pz", "sim_background_pass", "w_bkg"])
    bp, bz, bw = (b[k].astype(float) for k in ("sim_background", "sim_background_pz", "w_bkg"))
    ok = (b["sim_background_pass"] != 0) & np.isfinite(bp) & np.isfinite(bz) & np.isfinite(bw) & (bw >= 0) & (bw < 1e6)
    g = gidx(bp, bz); m = ok & (g >= 0); B = np.bincount(g[m], weights=bw[m] * s, minlength=224)
    np.savez(f"{W}/lat/{name}.npz", M=M, T=T, B=B, pot_scale=s, n=len(tp))
    return name, int(len(tp)), float(s)
os.makedirs(W + "/lat", exist_ok=True)
with ProcessPoolExecutor(6) as ex:
    for res in ex.map(build, files.items()): print(*res, flush=True)
