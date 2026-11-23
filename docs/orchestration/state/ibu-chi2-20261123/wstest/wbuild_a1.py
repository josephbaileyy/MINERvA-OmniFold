import json, numpy as np, ROOT
ROOT.EnableImplicitMT(16)
W = "/pscratch/sd/j/josephrb/oflow-split-20261123"
CV = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root"
a = ROOT.RDataFrame("mc_signal_reco", CV).AsNumpy(["sim", "sim_pz", "sim_pass", "w_reco", "MC", "MC_pz", "w_truth", "MC_q3", "MC_W"])
b = a
out = {"source": CV, "n": int(len(a["MC"]))}
f = ROOT.TFile.Open(CV); s = f.Get("dataPOTUsed").GetVal() / f.Get("mcPOTUsed").GetVal(); f.Close()
tp, tz, rp, rz = (a[k].astype(float) for k in ("MC", "MC_pz", "sim", "sim_pz"))
wt, wr = a["w_truth"].astype(float), a["w_reco"].astype(float)
good = np.isfinite(wt) & np.isfinite(wr) & (wt >= 0) & (wt < 1e4) & (wr >= 0) & (wr < 1e4); wt, wr = wt * s, wr * s
with np.errstate(invalid="ignore"):
    tru = np.isfinite(tp) & np.isfinite(tz) & (tp >= 0) & (tp <= 4.5) & (tz >= 1.5) & (tz <= 60) & (np.arctan2(tp, tz) < np.radians(20))
    rec = (a["sim_pass"] != 0) & np.isfinite(rp) & np.isfinite(rz) & (rp >= 0) & (rp <= 4.5) & (rz >= 1.5) & (rz <= 60)
PT = np.array([0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50]); PZ = np.array([1.5,2,2.5,3,3.5,4,4.5,5,6,7,8,9,10,15,20,40,60])
def gidx(pt, pz):
    ip = np.searchsorted(PT, pt, side="right") - 1; iz = np.searchsorted(PZ, pz, side="right") - 1
    return np.where((ip >= 0) & (ip < 14) & (iz >= 0) & (iz < 16), ip * 16 + iz, -1)
t, r = gidx(tp, tz), gidx(rp, rz)
q3, Wh = b["MC_q3"].astype(float), b["MC_W"].astype(float)
with np.errstate(invalid="ignore"):
    q0 = np.sqrt(Wh**2 + q3**2) - 0.938272; Emu = np.sqrt(tp**2 + tz**2 + 0.105658**2); Enu = Emu + q0; Q2 = q3**2 - q0**2
EE = np.array([0,3,4,5,6,7,8,10,12,15,20,30,50,80,np.inf]); QE = np.array([0,0.05,0.1,0.2,0.3,0.5,0.8,1.2,2,4,np.inf])
ie = np.searchsorted(EE, Enu, side="right") - 1; iq = np.searchsorted(QE, Q2, side="right") - 1
fin = np.isfinite(Enu) & np.isfinite(Q2) & (ie >= 0) & (ie < 14) & (iq >= 0) & (iq < 10)
ab = np.where(fin, ie * 10 + iq, 140); NAB = 141
kt = good & tru & (t >= 0)
A = np.zeros((224, NAB)); np.add.at(A, (t[kt], ab[kt]), wt[kt])
km = kt & rec & (r >= 0)
M4 = np.zeros((224, 224, NAB)); np.add.at(M4, (r[km], t[km], ab[km]), wr[km])
out.update(pot_scale=s, n_nonfinite_truthpass=int((kt & ~fin).sum()), w_nonfinite_frac=float(wt[kt & ~fin].sum() / wt[kt].sum()),
           Enu_q=[float(x) for x in np.nanpercentile(Enu[kt], [1, 50, 99])], Q2_neg_frac=float((Q2[kt] < 0).mean()))
np.savez_compressed(W + "/wsplit_a1.npz", A=A, M4=M4)
print(json.dumps(out))
