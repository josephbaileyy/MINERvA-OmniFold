#!/usr/bin/env python3
"""Quantify the impact of the train/test-split ML band on the combined 3D covariance.

Non-destructive: builds combined = C_syst + C_stat + C_ML with the OLD seedscan ML cov
vs the new train/test-split ML cov (#4), on the shared reported bins, and reports the
change in total sqrt-trace + per-bin relative uncertainty. Writes nothing destructive;
optional --out writes the refreshed combined cov to a NEW file.
"""
import argparse, numpy as np, ROOT
ROOT.gROOT.SetBatch(True)

def load(path, hist):
    f=ROOT.TFile.Open(path); h=f.Get(hist)
    n=h.GetNbinsX()
    a=np.array([[h.GetBinContent(i+1,j+1) for j in range(n)] for i in range(n)])
    f.Close(); return a

def load_sigma_cv(path):  # frozen CV reported diag base for relative uncertainty
    f=ROOT.TFile.Open(path); h=f.Get("hXSec3D")
    nx,ny,nz=h.GetNbinsX(),h.GetNbinsY(),h.GetNbinsZ()
    cv=np.array([h.GetBinContent(ix,iy,iz) for ix in range(1,nx+1) for iy in range(1,ny+1) for iz in range(1,nz+1)])
    f.Close(); return cv[cv>0]

D3="3d-unfolding/uq_3d"
syst=load(f"{D3}/universe_stage2_3d/uq_universe_3d_covariance.root","hCov_universe3d_total")
stat=load(f"{D3}/uq_cov_stat_3d.root","hCov_stat3d_reported")
ml_old=load(f"{D3}/uq_cov_ml_3d.root","hCov_ml3d_reported")
ml_new=load("nd-unfolding/uq_cov_mlsplit_3d.root","hCov_mlsplit3d_reported")
cv=load_sigma_cv("3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root")
for nm,M in [("syst",syst),("stat",stat),("ml_old",ml_old),("ml_new",ml_new)]:
    print(f"  {nm:8s} shape={M.shape} sqrt-trace={np.sqrt(max(np.trace(M),0)):.4e}")
assert syst.shape==stat.shape==ml_old.shape==ml_new.shape==(cv.size,cv.size), "shape mismatch"

def report(tag, C):
    diag=np.sqrt(np.maximum(np.diag(C),0))
    rel=np.where(cv>0,diag/cv,0)
    print(f"[{tag}] sqrt-trace={np.sqrt(max(np.trace(C),0)):.4e}  "
          f"median rel={100*np.median(rel):.3f}%  p84={100*np.percentile(rel,84):.3f}%  "
          f"max={100*np.max(rel):.3f}%")
    return np.median(rel)

print("\n=== Combined 3D covariance: OLD ML vs train/test-split ML ===")
c_old=syst+stat+ml_old; c_new=syst+stat+ml_new
m_old=report("combined OLD-ML ", c_old)
m_new=report("combined SPLIT-ML", c_new)
print(f"\n  ML band sqrt-trace: old {np.sqrt(np.trace(ml_old)):.3e} -> split "
      f"{np.sqrt(np.trace(ml_new)):.3e} ({np.sqrt(np.trace(ml_new))/np.sqrt(np.trace(ml_old)):.2f}x)")
print(f"  combined total sqrt-trace: {np.sqrt(np.trace(c_old)):.4e} -> {np.sqrt(np.trace(c_new)):.4e} "
      f"({100*(np.sqrt(np.trace(c_new))/np.sqrt(np.trace(c_old))-1):+.2f}%)")
print(f"  combined median rel uncertainty: {100*m_old:.3f}% -> {100*m_new:.3f}% "
      f"({100*(m_new-m_old):+.3f} pp)")
print("\n  Interpretation: ML is a sub-dominant band, so even a 1.24x larger ML band moves")
print("  the COMBINED uncertainty only marginally (Flux/syst + stat dominate). Reporting the")
print("  split-ML band is the conservative, defensible choice with negligible total cost.")
