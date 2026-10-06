import sys, json, os, numpy as np
sys.dont_write_bytecode=True
UQ="/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq"; sys.path.insert(0,UQ)
import analyze_uq as au, ROOT
X=[];P=[]
for s in range(1,301):
    f=ROOT.TFile.Open(f"{UQ}/2d_xsec_MEFHC_5iter_lgbm_boot{s}.root")
    x=au.th2_to_array(f.Get("hXSec2D")); c=au.th2_to_array(f.Get("hOFCompleteness2D")); f.Close()
    X.append(x); P.append(x*c)
X=np.stack(X);P=np.stack(P)
mo=X.mean(0); so=X.std(0,ddof=1); mp=P.mean(0); sp=P.std(0,ddof=1); rep=mo>0
r=sp[rep]/so[rep]
bs=json.load(open("/pscratch/sd/j/josephrb/ki84-rebuild-20261006/tools/ki84_binsets.json"))
g=np.full(so.shape,np.nan); g[rep]=r
def q(a): a=np.asarray(a); return dict(median=round(float(np.median(a)),4),p16=round(float(np.percentile(a,16)),4),p84=round(float(np.percentile(a,84)),4),min=round(float(a.min()),4),max=round(float(a.max()),4),n=int(a.size))
out=dict(all=q(r), frac_gt1=float((r>1).mean()), sqrt_tr_ratio=float(np.sqrt((sp[rep]**2).sum()/(so[rep]**2).sum())),
 median_rel_old=float(np.median(so[rep]/mo[rep])), median_rel_new=float(np.median(sp[rep]/mp[rep])), mean_new_over_old=q(mp[rep]/mo[rep]))
for k in ("low_c2_lt_0p85","rms_gt_2","pz_40_60_column"):
    out[k]=q([g[i,j] for i,j in bs[k]])
print(json.dumps(out,indent=1))
json.dump(dict(out, grid=[[None if np.isnan(v) else float(v) for v in row] for row in g]),open("/pscratch/sd/j/josephrb/ki84-rebuild-20261006/predict_from_vl162.json","w"),indent=1)
