import numpy as np, ROOT
PA="/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root"
r=ROOT.TFile.Open(PA)
for k in r.GetListOfKeys():
    o=k.ReadObj(); print(k.GetName(),k.GetClassName(), o.GetTitle())
    if o.InheritsFrom("TH2"):
        for ax in (o.GetXaxis(),o.GetYaxis()):
            print("   ",ax.GetNbins(),[round(ax.GetBinLowEdge(i),3) for i in range(1,ax.GetNbins()+2)], ax.GetTitle())
    if o.InheritsFrom("TMatrixTBase<double>"):
        print("   ",o.GetNrows(),o.GetNcols(),o.GetRowLwb())
z=np.load("/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-production-20261015/results/s5/production_cov.npz")
print(sorted(k for k in z.files if k.startswith("band_")))
