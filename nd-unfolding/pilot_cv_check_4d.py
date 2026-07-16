#!/usr/bin/env python3
"""Validate uq_4d/corrected/bank_uthrow_4d by re-unfolding the CV and comparing to
the frozen 4D central product. Proves the 5D-sourced truth-denom bins to the same
4D denominator (the one residual risk of assemble_bank_4d_from5d.py).

PASS criteria (declared before inspection):
  * reported-bin count (x_cv > 0) == 4830 (the frozen 4D reported mask size)
  * total xsec within 0.5% of the central total_xsec
  * per reported-bin max|rel diff| small (report it; expected << 1% -- same estimator
    seed, same weights, only the td-array provenance differs)
"""
import sys
import numpy as np

sys.path.insert(0, ".")
import unified_throw_cov as u
from compare_unified_throw import _xsec_for_weights
from xsec_nd import total_xsec
import ROOT

BANK = "uq_4d/corrected/bank_uthrow_4d"
CENTRAL = "products/4d/xsec_4d_MEFHC_5iter_lgbm.root"

d, bands, n_flux = u._load_bank(BANK)
edges = d["edges"]
x = _xsec_for_weights(d, edges, d["w_truth"], d["w_reco"], d["td_w"], 5, 1000)
xf = x.ravel(order="C")
rep = xf > 0
tot = total_xsec(x, edges)
print(f"[cv] reported bins = {int(rep.sum())}  (target 4830)")
print(f"[cv] bank CV total xsec = {tot:.6e}")

f = ROOT.TFile.Open(CENTRAL)
h = f.Get("hXSecND_flat")
c = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])
f.Close()
crep = c > 0
print(f"[central] reported bins = {int(crep.sum())}  total(flat*?)  nbins={c.size}")

# central total via same total_xsec on reshaped central
cshape = (len(edges[0]) - 1, len(edges[1]) - 1, len(edges[2]) - 1, len(edges[3]) - 1)
c_tot = total_xsec(c.reshape(cshape), edges)
print(f"[central] total xsec = {c_tot:.6e}")

same_mask = np.array_equal(rep, crep)
print(f"[cmp] reported-mask identical to central: {same_mask}")
rel_tot = abs(tot - c_tot) / c_tot
print(f"[cmp] total rel diff = {rel_tot:.3e}")
both = rep & crep
with np.errstate(divide="ignore", invalid="ignore"):
    relbin = np.where(c[both] > 0, np.abs(xf[both] - c[both]) / c[both], 0)
print(f"[cmp] per-bin (both-reported) max|rel|={relbin.max():.3e} median={np.median(relbin):.3e}")
verdict = (int(rep.sum()) == 4830) and (rel_tot < 5e-3)
print(f"[VERDICT] bank CV reproduces central: {'PASS' if verdict else 'FAIL'}")
