"""Read-only: dump hBkgReco2D per July-sweep universe (and CV) as JSON arrays."""
import glob, json, os, re, sys
import ROOT
d, out = sys.argv[1], sys.argv[2]
def arr(f, n):
    h = f.Get(n)
    return [h.GetBinContent(i, j) for i in range(1, h.GetNbinsX() + 1) for j in range(1, h.GetNbinsY() + 1)]
res = {}
for f in sorted(glob.glob(os.path.join(d, "2d_xsec_MEFHC_5iter_lgbm_pn_uni_*.root"))):
    tag = re.sub(r".*_pn_uni_(.*)\.root", r"\1", f)
    fu = ROOT.TFile.Open(f)
    res[tag] = {"B": arr(fu, "hBkgReco2D"), "X": arr(fu, "hXSec2D")}
    fu.Close()
json.dump(res, open(out, "w"))
print("wrote", len(res))
