"""Export the NOMINAL run's residual field q = r/u per cell. READ-ONLY.
The nominal run is where the 34% fold-forward deficit actually lives, so its residual field is the
adversarial one to apply to the closure's spectrum -- 2.8x the amplitude of the closure's own.
"""
import json, os, sys
import numpy as np
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
W=os.path.join(REPO,"nd-unfolding/pet/fullevent_nominal/pet_fullevent_nominal_weights.npz")
NPZ=os.path.join(REPO,"nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz")
PT=np.array([0,0.07,0.15,0.25,0.33,0.4,0.47,0.55,0.7,0.85,1.0,1.25,1.5,2.5,4.5,30.0],float)
PP=np.array([0.0,0.75,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,6.0,7.0,8.0,9.0,10.0,15.0,20.0,40.0,60.0,120.0],float)
NPT,NPP=len(PT)-1,len(PP)-1; NC=NPT*NPP
z=np.load(W,allow_pickle=True)
push=np.asarray(z["weights_push"],np.float64); imc=np.asarray(z["mc_indices"],np.int64)
R=float(np.asarray(z["step1_class_ratio"]))
z.close()
src=np.load(NPZ,allow_pickle=False)
ts=np.asarray(src["truth_scalars"]); t_pt,t_pp=ts[imc,0].astype(np.float64),ts[imc,1].astype(np.float64); del ts
wt=np.asarray(src["w_truth"],np.float64)[imc]; wr=np.asarray(src["w_reco"],np.float64)[imc]
pr=np.asarray(src["pass_reco"]).astype(bool)[imc]; pg=np.asarray(src["pass_truth"]).astype(bool)[imc]
src.close()
cc=np.clip(np.digitize(t_pt,PT)-1,0,NPT-1)*NPP+np.clip(np.digitize(t_pp,PP)-1,0,NPP-1)
def pc(mask,w):
    num=np.bincount(cc[mask],weights=(w*push)[mask],minlength=NC)
    den=np.bincount(cc[mask],weights=w[mask],minlength=NC)
    sw2=np.bincount(cc[mask],weights=(w[mask]**2),minlength=NC)
    live=den>0; r=np.full(NC,np.nan); r[live]=num[live]/den[live]
    ne=np.zeros(NC); ne[live]=den[live]**2/np.maximum(sw2[live],1e-300)
    return r,ne
r_reco,ne_reco=pc(pr,wr); r_truth,ne_truth=pc(pg,wt)
q=np.full(NC,np.nan); m=np.isfinite(r_reco)&np.isfinite(r_truth)&(r_truth>0); q[m]=r_reco[m]/r_truth[m]
out={"run":"fullevent_nominal","R_step1_class_ratio":R,
 "per_cell_q":[None if not np.isfinite(x) else float(x) for x in q],
 "per_cell_ne_reco":[float(x) for x in ne_reco],
 "per_cell_ne_truth":[float(x) for x in ne_truth],
 "per_cell_r_reco":[None if not np.isfinite(x) else float(x) for x in r_reco],
 "per_cell_r_truth":[None if not np.isfinite(x) else float(x) for x in r_truth]}
print("<<<JSON>>>"); json.dump(out,sys.stdout,indent=1,sort_keys=True); print()
