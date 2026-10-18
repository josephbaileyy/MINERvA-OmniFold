import numpy as np, ROOT
P="/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-production-20261015/results/s5/production_cov.npz"
L="/global/cfs/cdirs/m3246/josephrb/2d-closeout-playlist-term-20261016/playlist_term.npz"
EU="/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
PA="/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root"
for f in (P,L):
    z=np.load(f,allow_pickle=False)
    print(f)
    for k in z.files: print("  ",k,z[k].shape,z[k].dtype)
for f in (EU,PA):
    r=ROOT.TFile.Open(f); print(f)
    for k in r.GetListOfKeys(): print("  ",k.GetName(),k.GetClassName())
    for k in r.GetListOfKeys():
        o=k.ReadObj()
        if o.InheritsFrom("TH2"):
            for ax in (o.GetXaxis(),o.GetYaxis()):
                print("   ",o.GetName(),ax.GetNbins(),[round(ax.GetBinLowEdge(i),3) for i in range(1,ax.GetNbins()+2)], ax.GetTitle())
