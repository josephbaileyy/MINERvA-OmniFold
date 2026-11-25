# Reads the pT axis of the release's own published-result histogram (arXiv 2106.16210 anc cov_ptpl_minerva_inclusive_6GeV.root).
import sys, hashlib, ROOT
p = sys.argv[1]; print("sha256", hashlib.sha256(open(p, "rb").read()).hexdigest())
f = ROOT.TFile.Open(p); h = f.Get("pt_pl_cross_section")
for name, ax in (("X", h.GetXaxis()), ("Y", h.GetYaxis())):
    print(name, ax.GetTitle(), [round(ax.GetBinLowEdge(i), 6) for i in range(1, ax.GetNbins() + 2)])
