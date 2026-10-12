"""Read-only: max |c-1| of hOFCompleteness2D over CV>0 cells, per July (purity_newomni) and May (fluxfix) output."""
import ROOT, numpy as np, glob, json, os
R="/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq"
def arr(f,n):
    h=f.Get(n); return np.array([[h.GetBinContent(i,j) for j in range(1,h.GetNbinsY()+1)] for i in range(1,h.GetNbinsX()+1)])
out={}
for tag,pat in [("july",R+"/purity_newomni/2d_xsec_MEFHC_5iter_lgbm_pn_uni_*.root"),("may",R+"/universe_sweep_fluxfix/*.root")]:
    rows={}
    for fn in sorted(glob.glob(pat)):
        f=ROOT.TFile.Open(fn)
        if not f or f.IsZombie() or not f.Get("hOFCompleteness2D"): continue
        c=arr(f,"hOFCompleteness2D"); x=arr(f,"hXSec2D"); m=x>0
        rows[os.path.basename(fn)]=float(np.max(np.abs(c[m]-1))) if m.any() else None
        f.Close()
    out[tag]=rows
print(json.dumps(out))
