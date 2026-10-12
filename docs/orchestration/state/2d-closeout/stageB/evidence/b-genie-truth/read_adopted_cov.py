"""Read-only: dump the adopted universe covariance file's TH2D objects (names, shapes, contents)."""
import hashlib, json, sys
import numpy as np
import ROOT
p = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq/universe_stage2_MEFHC_full_matcorr_fluxfix/uq_universe_covariance_full_matcorr_fluxfix.root"
h = hashlib.sha256(open(p, "rb").read()).hexdigest()
f = ROOT.TFile.Open(p, "READ")
out, keys = {}, []
for k in f.GetListOfKeys():
    o = k.ReadObj(); keys.append([k.GetName(), k.GetClassName(), o.GetTitle()])
    if o.InheritsFrom("TH2") and o.GetNbinsX() == o.GetNbinsY() and o.GetNbinsX() > 100:
        n = o.GetNbinsX()
        out[k.GetName()] = np.array([[o.GetBinContent(i + 1, j + 1) for j in range(n)] for i in range(n)])
    elif o.InheritsFrom("TNamed") and not o.InheritsFrom("TH1"):
        keys[-1].append(o.GetTitle()[:2000])
np.savez_compressed(sys.argv[1] + ".npz", **out)
json.dump({"path": p, "sha256": h, "keys": keys}, open(sys.argv[1] + ".json", "w"), indent=1)
print(h, len(out))
