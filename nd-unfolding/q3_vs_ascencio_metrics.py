#!/usr/bin/env python3
"""Quantify how our 4D low-recoil result DIFFERS from Ascencio (arXiv:2110.13372).

Ascencio measured d2sigma/(dq3 dEavail) for q3 < 1.2 GeV, integrated over the muon
kinematics. Our 4D unfold (pT, pz, Eavail, q3) has two handles Ascencio does not:
  (1) q3 REACH beyond their 1.2 GeV cut -- how much of the low-Eavail (2p2h-region)
      signal/excess sits at q3 > 1.2 GeV, outside their window;
  (2) the MUON-KINEMATIC dependence of the excess (they integrate pT/pz out) -- is the
      low-Eavail data/GENIE excess flat in pT, or does it vary?

Reuses q3_excess_projection.py's construction: recompute the GENIE-CV prior numerator
from the omnifile and divide the saved unfolded counts by it (cancels efficiency/flux/
norm -> bin-by-bin data/GENIE). No frozen product is modified.
"""
import sys
import numpy as np
import ROOT

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if p not in sys.path:
        sys.path.insert(0, p)
import unfold_2d_omnifold_unbinned as u2d
import unfold_nd_omnifold_unbinned as und

OMNI = f"{_REPO}/nd-unfolding/runEventLoopOmniFold_4D_MEFHC.root"
CV = f"{_REPO}/nd-unfolding/xsec_4d_MEFHC_5iter_lgbm.root"
ASCENCIO_Q3_MAX = 1.2   # their q3 acceptance edge

pt_e = np.asarray(u2d.PT_EDGES, float); pz_e = np.asarray(u2d.PZ_EDGES, float)
ea_e = np.asarray(und.EXTRA_AXES["eavail"]["edges"], float)
q3_e = np.asarray(und.EXTRA_AXES["q3"]["edges"], float)
edges = [pt_e, pz_e, ea_e, q3_e]
shape = tuple(len(e) - 1 for e in edges)
THMAX = u2d.MAX_MUON_THETA_RAD

# --- GENIE-CV prior numerator from the omnifile (truth-pass, w_truth, POT-scaled) ---
f = ROOT.TFile.Open(OMNI)
_, _, pot_scale = u2d.get_pot_scales(f); f.Close()
ROOT.EnableImplicitMT()
df = ROOT.RDataFrame("mc_signal_reco", OMNI)
c = df.AsNumpy(["MC", "MC_pz", "MC_eavail", "MC_q3", "w_truth"])
pt = np.asarray(c["MC"], float); pz = np.asarray(c["MC_pz"], float)
ea = np.asarray(c["MC_eavail"], float); q3 = np.asarray(c["MC_q3"], float)
wt = np.asarray(c["w_truth"], float) * pot_scale
fin = np.isfinite(pt) & np.isfinite(pz)
m = fin & (pt >= pt_e[0]) & (pt <= pt_e[-1]) & (pz >= pz_e[0]) & (pz <= pz_e[-1])
m &= (np.arctan2(np.where(fin, pt, 0.0), np.where(fin, pz, 1.0)) < THMAX)
prior, _ = np.histogramdd(np.column_stack([pt[m], pz[m], ea[m], q3[m]]), bins=edges, weights=wt[m])

fc = ROOT.TFile.Open(CV); h = fc.Get("hUnfoldND_flat")
unfold = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())]).reshape(shape, order="C")
fc.Close()

# axes: 0=pT 1=pz 2=Eavail 3=q3
iq_lo = np.searchsorted(q3_e, ASCENCIO_Q3_MAX + 1e-9) - 1   # last q3 bin fully inside <1.2
q3_in = slice(0, iq_lo)      # q3 < 1.2  (Ascencio window)
q3_out = slice(iq_lo, shape[3])  # q3 >= 1.2 (beyond Ascencio)
ea_dip = slice(0, 3)         # Eavail < 0.4 GeV (the 2p2h dip: bins [0,.1],[.1,.2],[.2,.4])


def ratio(u, p):
    return u.sum() / p.sum() if p.sum() > 0 else float("nan")


print(f"[q3 edges] {q3_e.tolist()}  -> Ascencio window = first {iq_lo} bins (q3<{ASCENCIO_Q3_MAX})")
print(f"[Eavail edges] {ea_e.tolist()}  -> 'dip' = Eavail<0.4 (first 3 bins)\n")

tot_u, tot_p = unfold.sum(), prior.sum()
print(f"=== (1) q3 REACH beyond Ascencio's q3<{ASCENCIO_Q3_MAX} GeV ===")
print(f" full phase space        data/GENIE = {ratio(unfold,prior):.3f}")
ui, pi = unfold[:, :, :, q3_in].sum(), prior[:, :, :, q3_in].sum()
uo, po = unfold[:, :, :, q3_out].sum(), prior[:, :, :, q3_out].sum()
print(f" q3<1.2 (Ascencio)       data/GENIE = {ui/pi:.3f}   (rate: {100*ui/tot_u:.1f}% of data)")
print(f" q3>1.2 (beyond)         data/GENIE = {uo/po:.3f}   (rate: {100*uo/tot_u:.1f}% of data)")
exc = unfold - prior
exc_in = exc[:, :, :, q3_in].sum(); exc_out = exc[:, :, :, q3_out].sum(); exc_tot = exc.sum()
print(f" fraction of TOTAL data-GENIE excess at q3>1.2 (outside Ascencio): {100*exc_out/exc_tot:.1f}%")

print(f"\n=== (1b) the same, restricted to the low-Eavail 2p2h dip (Eavail<0.4) ===")
ud_in = unfold[:, :, ea_dip, q3_in].sum(); pd_in = prior[:, :, ea_dip, q3_in].sum()
ud_out = unfold[:, :, ea_dip, q3_out].sum(); pd_out = prior[:, :, ea_dip, q3_out].sum()
print(f" dip & q3<1.2            data/GENIE = {ud_in/pd_in:.3f}")
print(f" dip & q3>1.2 (beyond)   data/GENIE = {ud_out/pd_out:.3f}")
exd = exc[:, :, ea_dip, :]
print(f" fraction of the DIP excess at q3>1.2: {100*exd[:,:,:,q3_out].sum()/exd.sum():.1f}%")

print(f"\n=== (2) MUON-KINEMATIC dependence Ascencio integrates out ===")
print(" low-Eavail (<0.4) data/GENIE in pT slices (flat => excess factorizes from muon kin.):")
for i in range(shape[0]):
    u_i = unfold[i, :, ea_dip, :].sum(); p_i = prior[i, :, ea_dip, :].sum()
    if p_i > 0 and u_i > 0:
        print(f"   pT [{pt_e[i]:.2f},{pt_e[i+1]:.2f}]  data/GENIE = {u_i/p_i:.3f}   ({100*u_i/unfold[:,:,ea_dip,:].sum():.1f}% of dip rate)")
rr = []
for i in range(shape[0]):
    u_i = unfold[i, :, ea_dip, :].sum(); p_i = prior[i, :, ea_dip, :].sum()
    if p_i > 0 and u_i > 1e-3 * unfold[:, :, ea_dip, :].sum():
        rr.append(u_i / p_i)
rr = np.array(rr)
print(f" spread of the dip excess across populated pT slices: "
      f"min {rr.min():.3f}, max {rr.max():.3f}, RMS/mean {rr.std()/rr.mean()*100:.1f}%")
