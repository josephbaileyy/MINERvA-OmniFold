#!/usr/bin/env python3
"""One statistical-bootstrap replica of an ND OmniFold unfold (lean, npz-based).

Poisson-resamples the measured (data) and MC events, re-unfolds, saves the reported-bin
xsec flat. Many replicas -> C_stat (combine_cov_nd.py). Mirrors the nd driver's
--bootstrap-seed (data Poisson + MC Poisson) but from the npz so no 120 GB read.
  python bootstrap_nd.py --npz of_inputs_4d.npz --seed 7 --out boot_nd/res_boot_7.npz
"""
import argparse, sys, numpy as np
_ND="/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
if _ND not in sys.path: sys.path.insert(0,_ND)
from omnifold_nn_core import omnifold_loop
from xsec_nd import extract_cross_section_nd, project_axis, total_xsec

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--npz",required=True); ap.add_argument("--seed",type=int,required=True)
    ap.add_argument("--iters",type=int,default=5); ap.add_argument("--out",required=True)
    ap.add_argument("--estimator-seed", type=int, default=42,
                    help="fixed estimator seed; bootstrap seed varies only event weights")
    a=ap.parse_args()
    d=np.load(a.npz,allow_pickle=True); ne=int(d["nedges"]); edges=[d[f"edges_{i}"] for i in range(ne)]
    rng_d=np.random.default_rng(a.seed)
    rng_m=np.random.default_rng(a.seed + 10_000_000)
    mw=d["measured_weights"]*rng_d.poisson(1.0,d["measured_weights"].shape[0])
    bmc=rng_m.poisson(1.0,d["w_truth"].shape[0]).astype(float)
    wt=d["w_truth"]*bmc; wr=d["w_reco"]*bmc
    wpull,wpush=omnifold_loop(d["MCgen"],d["MCreco"],d["measured"],d["pass_reco"],d["pass_truth"],
        np.ones(len(d["measured"]),bool),a.iters,kind="lgbm",MCgen_weights=wt,MCreco_weights=wr,
        measured_weights=mw,seed=a.estimator_seed,verbose=False)
    m=d["pass_truth"]; bins=[np.asarray(e,float) for e in edges]
    samp=np.column_stack([d["MCgen"][m,i] for i in range(d["MCgen"].shape[1])])
    unf,_=np.histogramdd(samp,bins=bins,weights=wpush*wt[m]); ofin,_=np.histogramdd(samp,bins=bins,weights=wt[m])
    dn=d["denom_nd"]; comp=np.zeros_like(ofin); nz=dn>0; comp[nz]=ofin[nz]/dn[nz]
    xs,_=extract_cross_section_nd(unf,comp,d["flux"],float(d["data_pot"]),float(d["n_nucleons"]),edges)
    np.savez_compressed(a.out,seed=a.seed,xsec_flat=xs.ravel(order="C"),shape=np.array(xs.shape),total_xsec=total_xsec(xs,edges))
    print(f"[boot {a.seed}] total={total_xsec(xs,edges):.4e} -> {a.out}")
if __name__=="__main__": main()
