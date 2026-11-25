# Descriptive, not declared. Run read-only on login02 (root_6_28 env), cwd /dev/shm. Output: overflow.out.
import ROOT, numpy as np
f = "/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/out/runEventLoopOmniFold_MEFHC.root"
a = ROOT.RDataFrame("mc_signal_reco", f).Define("sp_i", "(int)sim_pass").AsNumpy(["sim", "sim_pz", "sp_i", "w_reco", "MC", "MC_pz", "mu_p_total"])
g = lambda k: np.asarray(a[k], dtype=float)
tp, tz, wr, rp, rz, mp, sp = g("MC"), g("MC_pz"), g("w_reco"), g("sim"), g("sim_pz"), g("mu_p_total"), g("sp_i")
good = np.isfinite(wr) & (wr >= 0) & (wr < 1e4)
with np.errstate(invalid="ignore"):
    tru = np.isfinite(tp) & (tp >= 0) & (tp <= 4.5) & (tz >= 1.5) & (tz <= 60) & (np.arctan2(tp, tz) < np.radians(20))
sel = good & tru & (sp != 0) & (mp > 0)
ingrid = (rp >= 0) & (rp < 4.5) & (rz >= 1.5) & (rz < 60)
for lo, hi, name in ((40, 60, "true40-60"), (20, 40, "true20-40"), (10, 15, "true10-15")):
    m = sel & (tz >= lo) & (tz < hi); W = float(wr[m].sum())
    fr = lambda c: float(wr[m & c].sum()) / W
    print(name, "W", int(W), "ingrid %.4f" % fr(ingrid), "pz>=60 %.4f" % fr(rz >= 60), "pz<1.5 %.4f" % fr(rz < 1.5), "pt>=4.5 %.4f" % fr(rp >= 4.5))
