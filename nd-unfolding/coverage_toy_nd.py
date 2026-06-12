#!/usr/bin/env python3
"""One coverage toy (closure + bootstrap) for an ND OmniFold unfold (npz-based).

Mirrors the 2D coverage recipe (sbatch_coverage_toys_MEFHC_200.sh: driver
--closure --bootstrap-seed): pseudo-data = the MC reco events themselves
(pass_reco & pass_truth, POT-scaled weights) with a Poisson fluctuation, MC side
independently Poisson-fluctuated (same seed offsets as the driver), unfold,
closure xsec (completeness = 1). The truth reference is toy-independent
(unfluctuated w_truth on pass_truth) and is computed once in the analysis
script (fps_extension_validation.py). Many toys -> per-bin coverage.
  python coverage_toy_nd.py --npz of_inputs_fps.npz --seed 1001 --out cov_fps/res_toy_1.npz
"""
import argparse, sys, numpy as np
_ND="/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
if _ND not in sys.path: sys.path.insert(0,_ND)
from omnifold_nn_core import omnifold_loop
from xsec_nd import extract_cross_section_nd, total_xsec

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--npz",required=True); ap.add_argument("--seed",type=int,required=True)
    ap.add_argument("--iters",type=int,default=5); ap.add_argument("--out",required=True)
    a=ap.parse_args()
    d=np.load(a.npz,allow_pickle=True); ne=int(d["nedges"]); edges=[d[f"edges_{i}"] for i in range(ne)]
    pr=d["pass_reco"].astype(bool); pt=d["pass_truth"].astype(bool)
    cm=pr&pt
    measured=d["MCreco"][cm]
    rng_d=np.random.default_rng(a.seed); rng_m=np.random.default_rng(a.seed+10_000_000)
    mw=d["w_reco"][cm]*rng_d.poisson(1.0,int(cm.sum()))
    bmc=rng_m.poisson(1.0,d["w_truth"].shape[0]).astype(float)
    wt=d["w_truth"]*bmc; wr=d["w_reco"]*bmc
    try:
        wpull,wpush=omnifold_loop(d["MCgen"],d["MCreco"],measured,pr,pt,
            np.ones(measured.shape[0],bool),a.iters,kind="lgbm",MCgen_weights=wt,
            MCreco_weights=wr,measured_weights=mw,seed=a.seed,verbose=False)
    except Exception as e:   # skip a pathological toy (exit 0) so combines aren't blocked
        print(f"[toy {a.seed}] SKIPPED ({type(e).__name__}: {e})"); return
    bins=[np.asarray(e,float) for e in edges]
    samp=np.column_stack([d["MCgen"][pt,i] for i in range(d["MCgen"].shape[1])])
    unf,_=np.histogramdd(samp,bins=bins,weights=wpush*wt[pt])
    comp=np.ones_like(unf)   # closure: completeness = 1 (mirrors the driver)
    xs,_=extract_cross_section_nd(unf,comp,d["flux"],float(d["data_pot"]),float(d["n_nucleons"]),edges)
    np.savez_compressed(a.out,seed=a.seed,xsec_flat=xs.ravel(order="C"),
                        shape=np.array(xs.shape),total_xsec=total_xsec(xs,edges))
    print(f"[toy {a.seed}] total={total_xsec(xs,edges):.4e} -> {a.out}")

if __name__=="__main__": main()
