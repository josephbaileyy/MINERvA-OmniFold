"""Read-only: Rvn1pi vs Rvp1pi weight columns, all four weight families, current universe omnifile.

Emits digests and equality flags only (no event values). Usage: python3 rv_columns.py > out.json
"""
import hashlib, json, os, re, time
import numpy as np
import ROOT
ROOT.gROOT.SetBatch(True)
UNI = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root"
FAM = {"mc_signal_reco": ["w_truth", "w_reco"], "mc_truth_denom": ["w_truth"], "mc_background": ["w_bkg"]}


def column(t, n):
    t.SetBranchStatus("*", 0); t.SetBranchStatus(n, 1)
    a = ROOT.RDataFrame(t).AsNumpy([n])[n].astype(np.float64)
    t.SetBranchStatus("*", 1)
    return np.ascontiguousarray(a)


st = os.stat(UNI)
res = {"file": UNI, "size": st.st_size, "mtime": st.st_mtime, "start": time.time(), "trees": {}}
f = ROOT.TFile.Open(UNI, "READ")
for tree, bases in FAM.items():
    t = f.Get(tree)
    names = {b.GetName() for b in t.GetListOfBranches()}
    rt = {"entries": int(t.GetEntries()), "rv_branches_present": sorted(n for n in names if re.search(r"Rv[np][12]pi", n)), "pairs": {}}
    for base in bases:
        cv = column(t, base)
        for i in (0, 1):
            a, b = f"{base}_Rvn1pi_{i}", f"{base}_Rvp1pi_{i}"
            if a not in names or b not in names:
                rt["pairs"][f"{base}_{i}"] = "MISSING"; continue
            x, y = column(t, a), column(t, b)
            rt["pairs"][f"{base}_{i}"] = {
                "sha256_n": hashlib.sha256(x.tobytes()).hexdigest(), "sha256_p": hashlib.sha256(y.tobytes()).hexdigest(),
                "identical": bool(np.array_equal(x, y)), "n_rows_differing": int(np.sum(x != y)),
                "rows_differing_from_cv": int(np.sum(x != cv)), "frac_rows_differing_from_cv": float(np.mean(x != cv))}
    res["trees"][tree] = rt
res["end"] = time.time()
print(json.dumps(res, indent=1, sort_keys=True))
