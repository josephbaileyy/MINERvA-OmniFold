#!/usr/bin/env python3
"""Write a refreshed combined 3D covariance with the train/test-split ML band.
combined_split = C_syst(hCov_universe3d_total) + C_stat + C_ML_split  (reported bins).
Non-destructive: new file. hist named hCov_combined3d_total so compare_3d_fullcov.py
can consume it unchanged."""
import numpy as np, ROOT
ROOT.gROOT.SetBatch(True)
def load(p,h):
    f=ROOT.TFile.Open(p); hh=f.Get(h); n=hh.GetNbinsX()
    a=np.array([[hh.GetBinContent(i+1,j+1) for j in range(n)] for i in range(n)]); f.Close(); return a
D3="."
syst=load("../uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root","hCov_universe3d_total")
stat=load("../uq_3d/uq_cov_stat_3d.root","hCov_stat3d_reported")
mls =load("../../nd-unfolding/uq_cov_mlsplit_3d.root","hCov_mlsplit3d_reported")
assert syst.shape==stat.shape==mls.shape, (syst.shape,stat.shape,mls.shape)
C=syst+stat+mls; n=C.shape[0]
out="../uq_3d/universe_stage2_3d/uq_combined3d_splitml.root"
f=ROOT.TFile.Open(out,"RECREATE")
h=ROOT.TH2D("hCov_combined3d_total","combined syst+stat+ML(split) reported",n,0,n,n,0,n)
for i in range(n):
    for j in range(n): h.SetBinContent(i+1,j+1,float(C[i,j]))
h.Write(); f.Close()
print(f"[wrote] {out}  sqrt-trace={np.sqrt(max(C.trace(),0)):.4e}")
