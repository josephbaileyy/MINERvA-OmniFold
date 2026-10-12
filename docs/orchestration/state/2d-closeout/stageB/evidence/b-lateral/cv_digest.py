"""Read-only: sha256 of each CV column array (float64 bytes, row order) in the 2D CV omnifile (E_U/L0 input
family, runEventLoopOmniFold_MEFHC.root) and the July dump-mode universes omnifile."""
import ROOT, numpy as np, hashlib, json
R="/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
F={"cv_omnifile":R+"/runEventLoopOmniFold_MEFHC.root","july_universes":R+"/runEventLoopOmniFold_MEFHC_universes_full.root"}
T={"mc_signal_reco":["MC","MC_pz","sim","sim_pz","sim_pass","w_truth","w_reco"],"mc_background":["sim_background","sim_background_pz","sim_background_pass","w_bkg"],
   "mc_truth_denom":["MC","MC_pz","w_truth"]}
out={}
for tag,fn in F.items():
    out[tag]={}
    for tree,names in T.items():
        df=ROOT.RDataFrame(tree,fn); req=[]
        for n in names:
            if n.endswith("_pass"): df=df.Define(n+"_i",f"(int){n}"); req.append(n+"_i")
            else: req.append(n)
        d=df.AsNumpy(req)
        out[tag][tree]={k:hashlib.sha256(np.ascontiguousarray(np.asarray(v,dtype=np.float64)).tobytes()).hexdigest() for k,v in d.items()}
    f=ROOT.TFile.Open(fn); t=f.Get("data"); out[tag]["data_branches"]=[b.GetName() for b in t.GetListOfBranches()]; f.Close()
    df=ROOT.RDataFrame("data",fn); req=[]
    for n in out[tag]["data_branches"]:
        tn=df.GetColumnType(n)
        if "char" in tn.lower() or "bool" in tn.lower(): df=df.Define(n+"_i",f"(int){n}"); req.append(n+"_i")
        else: req.append(n)
    d=df.AsNumpy(req)
    out[tag]["data"]={k:hashlib.sha256(np.ascontiguousarray(np.asarray(v,dtype=np.float64)).tobytes()).hexdigest() for k,v in d.items()}
eq={tree:{k:out["cv_omnifile"][tree][k]==out["july_universes"][tree].get(k) for k in out["cv_omnifile"][tree]} for tree in list(T)+["data"]}
out["equal"]=eq
print(json.dumps(out))
