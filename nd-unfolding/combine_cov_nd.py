#!/usr/bin/env python3
"""Build an ND covariance (reported bins = CV>0) from a glob of xsec_flat npz replicas.
Reported mask from the 4D CV product (hXSecND_flat). Writes hCov_<tag>_reported.
  python combine_cov_nd.py --glob 'seedscan_split_4d/res_*.npz' --cv products/4d/xsec_4d_MEFHC_5iter_lgbm.root --tag ml4d --out uq_cov_ml_4d.root
"""
import argparse, glob, numpy as np, ROOT
from replica_manifest import load_replica_manifest
ROOT.gROOT.SetBatch(True)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--glob",required=True); ap.add_argument("--cv",required=True)
    ap.add_argument("--tag",required=True); ap.add_argument("--out",required=True)
    ap.add_argument("--expected-ids", required=True,
                    help="required inclusive replica id range LO-HI, e.g. 1-100")
    a=ap.parse_args()
    lo, hi = (int(v) for v in a.expected_ids.split("-", 1))
    if hi < lo: ap.error("--expected-ids must be LO-HI with HI>=LO")
    paths=sorted(glob.glob(a.glob)); X, ids=load_replica_manifest(paths, set(range(lo, hi+1)))
    f=ROOT.TFile.Open(a.cv); h=f.Get("hXSecND_flat"); cv=np.array([h.GetBinContent(i+1) for i in range(h.GetNbinsX())]); f.Close()
    rep=cv>0; Xr=X[:,rep]; cvr=cv[rep]; Z=Xr-Xr.mean(0); C=(Z.T@Z)/(Xr.shape[0]-1)
    diag=np.sqrt(np.maximum(np.diag(C),0)); rel=np.where(cvr>0,diag/cvr,0)
    print(f"[{a.tag}] {Xr.shape[0]} replicas, reported {int(rep.sum())} bins, sqrt-trace={np.sqrt(max(C.trace(),0)):.3e} median rel={100*np.median(rel):.3f}%")
    rf=ROOT.TFile.Open(a.out,"RECREATE"); n=C.shape[0]; hh=ROOT.TH2D(f"hCov_{a.tag}_reported",a.tag,n,0,n,n,0,n)
    for i in range(n):
        for j in range(n): hh.SetBinContent(i+1,j+1,float(C[i,j]))
    hh.Write(); rf.Close(); print(f"[wrote] {a.out}")
if __name__=="__main__": main()
