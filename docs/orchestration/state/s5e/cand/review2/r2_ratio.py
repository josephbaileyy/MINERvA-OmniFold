#!/usr/bin/env python3
"""Review round 2: rebuild the W2/W3 shape ratios from the generator ROOT files with independent code."""
import hashlib, json, sys
import numpy as np
import ROOT
R2 = "/pscratch/sd/j/josephrb/s5e-20260925/review2"
out = {}
for f in ("w2-genie-mec-over-cv-eavailW.json", "w3-nuwro-over-genie-pt-pz-eavail.json"):
    r = json.load(open(f"{R2}/inputs/{f}"))
    arrs = []
    for side in ("numerator", "denominator"):
        p = r[side]["path"]
        ok_sha = hashlib.sha256(open(p, "rb").read()).hexdigest() == r[side]["sha256"]
        tf = ROOT.TFile.Open(p); h = tf.Get(r["histogram"])
        nd = 3 if h.InheritsFrom("TH3") else 2
        nb = [h.GetNbinsX(), h.GetNbinsY()] + ([h.GetNbinsZ()] if nd == 3 else [])
        ax = [h.GetXaxis(), h.GetYaxis()] + ([h.GetZaxis()] if nd == 3 else [])
        ed = [np.array([a.GetBinLowEdge(i) for i in range(1, n + 2)]) for a, n in zip(ax, nb)]
        edges_ok = all(np.allclose(e, np.asarray(x)) for e, x in zip(ed, r["edges"]))
        c = np.zeros(nb)
        for idx in np.ndindex(*nb):
            c[idx] = h.GetBinContent(*[i + 1 for i in idx])
        tf.Close()
        arrs.append(c); out.setdefault(f, {})[side] = {"sha_ok": ok_sha, "edges_ok": edges_ok, "n_nonpos": int((c <= 0).sum())}
    num, den = arrs
    vol = np.ones(num.shape)
    for d, e in enumerate(r["edges"]):
        vol = vol * np.diff(e).reshape([-1 if i == d else 1 for i in range(num.ndim)])
    ok = (num > 0) & (den > 0)
    fn = np.where(ok, num * vol, 0); fd = np.where(ok, den * vol, 0)
    rho = np.ones(num.shape); rho[ok] = (fn[ok] / fn.sum()) / (fd[ok] / fd.sum())
    nclip = int(((rho < 0.25) | (rho > 4)).sum()); rho = np.clip(rho, 0.25, 4)
    committed = np.asarray(r["shape_ratio"]).reshape(num.shape)
    out[f].update({"max_abs_diff_vs_committed": float(np.max(np.abs(rho - committed))), "n_no_info": int((~ok).sum()), "n_clipped": nclip,
                   "volume_matters_only_via_normalization": True,
                   "rho_without_volume_max_diff": float(np.max(np.abs(np.clip(np.where(ok, (num / num[ok].sum()) / (den / den[ok].sum()), 1), .25, 4) - committed)))})
json.dump(out, open(R2 + "/r2_ratio.json", "w"), indent=1)
print(json.dumps(out, indent=1))
