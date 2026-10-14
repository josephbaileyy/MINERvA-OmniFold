"""Read-only event-identity probe on MINERvA ME-FHC MC AnaTuples (stage-d-inputs lane, 2026-10-14).

Opens each file READ, reads only integer identity branches, writes nothing.
Key tested: K = (mc_run, mc_subrun, mc_nthEvtInFile).
"""
import sys, os, json, hashlib
import numpy as np
import ROOT
ROOT.gROOT.SetBatch(True)

KEYS = ["mc_run", "mc_subrun", "mc_nthEvtInFile"]
out = {"python": sys.version.split()[0], "root": ROOT.gROOT.GetVersion(), "files": []}

def read(tree_name, path, extra):
    f = ROOT.TFile.Open(path, "READ")
    t = f.Get(tree_name)
    names = [b.GetName() for b in t.GetListOfBranches()]
    have = [k for k in KEYS + extra if k in names]
    n = t.GetEntries()
    f.Close()
    df = ROOT.RDataFrame(tree_name, path)
    arr = df.AsNumpy(have)
    return n, names, {k: np.asarray(arr[k]).astype(np.int64) for k in have}

def pack(d):
    return (d["mc_run"] << 40) | (d["mc_subrun"] << 24) | d["mc_nthEvtInFile"]

for path in sys.argv[1:]:
    rec = {"path": path, "size_B": os.path.getsize(path)}
    ident_like = []
    nR, namesR, R = read("MasterAnaDev", path, [])
    nT, namesT, T = read("Truth", path, [])
    rec["reco_tree"] = {"name": "MasterAnaDev", "entries": int(nR), "n_branches": len(namesR)}
    rec["truth_tree"] = {"name": "Truth", "entries": int(nT), "n_branches": len(namesT)}
    rec["identity_like_branches_reco"] = sorted(b for b in namesR if any(s in b.lower() for s in ("run", "subrun", "nthevt", "gate", "slice", "spill")) and len(b) < 40)[:60]
    rec["identity_like_branches_truth"] = sorted(b for b in namesT if any(s in b.lower() for s in ("run", "subrun", "nthevt", "gate", "slice", "spill")) and len(b) < 40)[:60]
    for k in ("mc_nthEvtInFile",):
        assert k in R and k in T, (k, path)
    # ranges (bit-width check for the pack)
    for lab, d in (("reco", R), ("truth", T)):
        rec[lab + "_ranges"] = {k: [int(d[k].min()), int(d[k].max())] for k in KEYS}
        assert d["mc_subrun"].max() < (1 << 16) and d["mc_nthEvtInFile"].max() < (1 << 24) and d["mc_subrun"].min() >= 0 and d["mc_nthEvtInFile"].min() >= 0
    kR = pack(R); kT = pack(T)
    uR, cR = np.unique(kR, return_counts=True)
    uT, cT = np.unique(kT, return_counts=True)
    rec["reco_unique_keys"] = int(uR.size)
    rec["reco_dup_keys"] = int((cR > 1).sum()); rec["reco_max_mult"] = int(cR.max())
    rec["truth_unique_keys"] = int(uT.size)
    rec["truth_dup_keys"] = int((cT > 1).sum()); rec["truth_max_mult"] = int(cT.max())
    inT = np.isin(uR, uT)
    rec["reco_keys_found_in_truth"] = int(inT.sum())
    rec["reco_keys_not_in_truth"] = int((~inT).sum())
    rec["truth_keys_without_reco"] = int(uT.size - np.isin(uT, uR).sum())
    # nth alone / (run,nth) alone: how much work subrun does
    rec["nth_unique_values_reco"] = int(np.unique(R["mc_nthEvtInFile"]).size)
    rec["run_subrun_pairs_truth"] = int(np.unique((T["mc_run"] << 16) | T["mc_subrun"]).size)
    # per (run,subrun): is truth nth contiguous 0..n-1 ?
    rs = (T["mc_run"] << 16) | T["mc_subrun"]
    order = np.lexsort((T["mc_nthEvtInFile"], rs))
    rs_s = rs[order]; nth_s = T["mc_nthEvtInFile"][order]
    bounds = np.flatnonzero(np.diff(rs_s)) + 1
    starts = np.r_[0, bounds]; ends = np.r_[bounds, rs_s.size]
    contiguous = 0; first_nonzero = 0
    for s, e in zip(starts, ends):
        seg = nth_s[s:e]
        if seg[0] != 0: first_nonzero += 1
        if seg[-1] - seg[0] + 1 == seg.size and np.all(np.diff(seg) == 1): contiguous += 1
    rec["truth_subruns"] = int(starts.size); rec["truth_subruns_contiguous_from_min"] = int(contiguous); rec["truth_subruns_not_starting_at_0"] = int(first_nonzero)
    # duplicate example characterization (reco): first 3 dup keys, entry indices
    if rec["reco_dup_keys"]:
        dk = uR[cR > 1][:3]
        rec["reco_dup_examples_entries"] = [np.flatnonzero(kR == x)[:5].tolist() for x in dk]
    out["files"].append(rec)
    print(json.dumps(rec), flush=True)
print("SUMMARY " + json.dumps({"python": out["python"], "root": out["root"], "n_files": len(out["files"])}))
