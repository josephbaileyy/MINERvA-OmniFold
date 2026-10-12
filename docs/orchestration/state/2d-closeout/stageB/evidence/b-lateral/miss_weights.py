"""Read-only: on mc_signal_reco rows with sim_pass==0, compare dump w_truth_<u>, dump CV w_truth and active
w_truth; and completeness-style sums: signal-tree truth weight in truth phase space vs mc_truth_denom sum,
per file, for the CV and for universe u."""
import json, sys, numpy as np, ROOT
R="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; u=sys.argv[1]
DUMP=R+"/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root"
ACT=R+f"/nd-unfolding/active_universe_5d/standard/merged/runEventLoopOmniFold_5D_MEFHC_active_{u}.root"
def inps(pt,pz):  # truth phase space rectangle (theta<20 enforced upstream by the event loop)
    return np.isfinite(pt)&np.isfinite(pz)&(pt>=0)&(pt<4.5)&(pz>1.5)&(pz<60)
def full(fn,tree,names):
    df=ROOT.RDataFrame(tree,fn); req=[]
    for n in names:
        if n.endswith("_pass"): df=df.Define(n+"_i",f"(int){n}"); req.append(n+"_i")
        else: req.append(n)
    d=df.AsNumpy(req); return {(k[:-2] if k.endswith("_pass_i") else k):np.asarray(v,dtype=np.float64) for k,v in d.items()}
o={"universe":u}
d=full(DUMP,"mc_signal_reco",["MC","MC_pz","sim_pass","w_truth",f"w_truth_{u}"])
a=full(ACT,"mc_signal_reco",["w_truth"])
np_=d["sim_pass"]==0
wd=d[f"w_truth_{u}"]; wc=d["w_truth"]; wa=a["w_truth"]
o["nonpass_rows"]=int(np_.sum())
o["nonpass_dumpU_eq_dumpCV"]=int((wd[np_]==wc[np_]).sum())
o["nonpass_act_eq_dumpCV"]=int((wa[np_]==wc[np_]).sum())
o["nonpass_act_eq_dumpU"]=int((wa[np_]==wd[np_]).sum())
p=~np_
o["pass_dumpU_eq_dumpCV"]=int((wd[p]==wc[p]).sum()); o["pass_rows"]=int(p.sum())
m=inps(d["MC"],d["MC_pz"])
o["sig_truth_sum_in_ps"]={"dump_cv":float(wc[m].sum()),"dump_u":float(wd[m].sum()),"active":float(wa[m].sum())}
del d,a
t=full(DUMP,"mc_truth_denom",["MC","MC_pz","w_truth",f"w_truth_{u}"]); ta=full(ACT,"mc_truth_denom",["MC","MC_pz","w_truth"])
mt=inps(t["MC"],t["MC_pz"]); mta=inps(ta["MC"],ta["MC_pz"])
o["denom_sum_in_ps"]={"dump_cv":float(t["w_truth"][mt].sum()),"dump_u":float(t[f"w_truth_{u}"][mt].sum()),"active":float(ta["w_truth"][mta].sum())}
o["denom_dumpU_eq_dumpCV"]=int((t[f"w_truth_{u}"]==t["w_truth"]).sum()); o["denom_rows"]=int(len(mt))
print(json.dumps(o))
