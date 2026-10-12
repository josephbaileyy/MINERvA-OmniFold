"""Read-only: where do active w_truth and dump w_truth_<u> differ for one lateral universe, and by how much,
on mc_signal_reco and mc_truth_denom; truth-level weighted 2D histograms in the truth phase space."""
import json, sys, numpy as np, ROOT
R="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; u=sys.argv[1]
DUMP=R+"/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root"
ACT=R+f"/nd-unfolding/active_universe_5d/standard/merged/runEventLoopOmniFold_5D_MEFHC_active_{u}.root"
PT=np.array([0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.0,1.25,1.5,2.5,4.5]); PZ=np.array([1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,6.0,7.0,8.0,9.0,10.0,15.0,20.0,40.0,60.0])
def cols(fn,tree,names,lo,hi):
    df=ROOT.RDataFrame(tree,fn).Range(lo,hi); req=[]
    for n in names:
        if n.endswith("_pass"): df=df.Define(n+"_i",f"(int){n}"); req.append(n+"_i")
        else: req.append(n)
    d=df.AsNumpy(req); return {(k[:-2] if k.endswith("_pass_i") else k):np.asarray(v,dtype=np.float64) for k,v in d.items()}
out={"universe":u}
for tree,extra,ptk,pzk in [("mc_signal_reco",["sim_pass"],"MC","MC_pz"),("mc_truth_denom",[],"MC","MC_pz")]:
    _f=ROOT.TFile.Open(DUMP); N=_f.Get(tree).GetEntries(); _f.Close(); CH=4_000_000
    acc={"rows":0,"differ":0,"differ_pass":0,"differ_nonpass":0,"max_rel":0.0,"sum_abs_rel":0.0}
    Hd=np.zeros((14,16)); Ha=np.zeros((14,16))
    for lo in range(0,N,CH):
        hi=min(N,lo+CH)
        d=cols(DUMP,tree,[ptk,pzk,f"w_truth_{u}"]+extra,lo,hi); a=cols(ACT,tree,[ptk,pzk,"w_truth"],lo,hi)
        assert np.array_equal(d[ptk],a[ptk]) and np.array_equal(d[pzk],a[pzk])
        wd=d[f"w_truth_{u}"]; wa=a["w_truth"]; df=wd!=wa
        acc["rows"]+=hi-lo; acc["differ"]+=int(df.sum())
        if extra:
            p=d["sim_pass"]!=0; acc["differ_pass"]+=int((df&p).sum()); acc["differ_nonpass"]+=int((df&~p).sum())
        with np.errstate(divide="ignore",invalid="ignore"):
            r=np.abs(wd-wa)/np.where(wa!=0,np.abs(wa),1.0)
        if df.any(): acc["max_rel"]=max(acc["max_rel"],float(r[df].max())); acc["sum_abs_rel"]+=float(r[df].sum())
        ok=np.isfinite(d[ptk])&np.isfinite(d[pzk])
        Hd+=np.histogram2d(d[ptk][ok],d[pzk][ok],bins=[PT,PZ],weights=wd[ok])[0]; Ha+=np.histogram2d(a[ptk][ok],a[pzk][ok],bins=[PT,PZ],weights=wa[ok])[0]
    m=Ha>0
    acc["truth_hist_max_rel"]=float(np.max(np.abs(Hd[m]-Ha[m])/Ha[m])); acc["truth_hist_sum_rel"]=float(abs(Hd.sum()-Ha.sum())/Ha.sum())
    acc["mean_rel_on_differ"]=acc["sum_abs_rel"]/max(acc["differ"],1)
    out[tree]=acc
print(json.dumps(out))
