"""Read-only: per-band median relative half-difference of the July (purity_newomni) lateral universes
vs the July CV, over cells with CV > 0; and the same for the adopted May sweep (universe_sweep_fluxfix)."""
import ROOT, numpy as np, json, hashlib
R="/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq"
def arr(fn):
    f=ROOT.TFile.Open(fn); h=f.Get("hXSec2D")
    a=np.array([[h.GetBinContent(i,j) for j in range(1,h.GetNbinsY()+1)] for i in range(1,h.GetNbinsX()+1)]); f.Close(); return a
def sha(fn):
    return hashlib.sha256(open(fn,"rb").read()).hexdigest()
out={}
for tag,d,pre,cv in [("july",R+"/purity_newomni","2d_xsec_MEFHC_5iter_lgbm_pn_uni_","2d_xsec_MEFHC_5iter_lgbm_pn_uni_CV.root"),
                     ("may",R+"/universe_sweep_fluxfix","2d_xsec_MEFHC_5iter_lgbm_uni_full_",None)]:
    import os
    cvf = d+"/"+cv if cv else R+"/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
    c=arr(cvf); m=c>0
    out[tag]={"cv":cvf,"cv_sha":sha(cvf),"ncells":int(m.sum()),"bands":{}}
    for b in ["BeamAngleX","BeamAngleY","MuonResolution","Muon_Energy_MINERvA","Muon_Energy_MINOS"]:
        f0=d+"/"+pre+b+"_0.root"; f1=d+"/"+pre+b+"_1.root"
        if not (os.path.exists(f0) and os.path.exists(f1)): out[tag]["bands"][b]="missing"; continue
        a0=arr(f0); a1=arr(f1)
        half=np.abs(a1-a0)[m]/2/c[m]; disp=((a0+a1)/2-c)[m]/c[m]
        out[tag]["bands"][b]={"median_rel_half":float(np.median(half)),"max_rel_half":float(half.max()),
                             "median_abs_disp":float(np.median(np.abs(disp))),"sha0":sha(f0),"sha1":sha(f1)}
print(json.dumps(out,indent=1))
