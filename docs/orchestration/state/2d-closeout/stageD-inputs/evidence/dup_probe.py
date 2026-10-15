"""Read-only: characterize duplicate (mc_run, mc_subrun, mc_nthEvtInFile) blocks in one AnaTuple."""
import sys, json
import numpy as np, ROOT
ROOT.gROOT.SetBatch(True)
path = sys.argv[1]
res = {"path": path}
for tree in ("Truth", "MasterAnaDev"):
    f = ROOT.TFile.Open(path, "READ"); t = f.Get(tree)
    names = {b.GetName() for b in t.GetListOfBranches()}; f.Close()
    kin = [b for b in ("mc_incomingE", "mc_Q2", "mc_w", "mc_intType", "mc_current", "mc_incoming", "mc_targetZ", "mc_nthEvtInSpill", "ev_gate", "ev_subrun", "ev_run") if b in names]
    cols = ["mc_run", "mc_subrun", "mc_nthEvtInFile"] + kin
    a = ROOT.RDataFrame(tree, path).AsNumpy(cols)
    a = {k: np.asarray(v) for k, v in a.items()}
    key = (a["mc_run"].astype(np.int64) << 40) | (a["mc_subrun"].astype(np.int64) << 24) | a["mc_nthEvtInFile"].astype(np.int64)
    u, inv, c = np.unique(key, return_inverse=True, return_counts=True)
    dupmask = c[inv] > 1
    r = {"kin_branches": kin, "dup_rows": int(dupmask.sum()), "dup_keys": int((c > 1).sum())}
    r["dup_subruns"] = sorted(set(int(x) for x in a["mc_subrun"][dupmask]))
    # for each dup key, are the two rows identical on all kin branches?
    idx = np.flatnonzero(dupmask); order = np.argsort(key[idx], kind="stable"); idx = idx[order]
    same = 0; diff = 0
    for i in range(0, idx.size, 2):
        p, q = idx[i], idx[i + 1]
        if all(np.array_equal(a[k][p], a[k][q]) for k in kin): same += 1
        else: diff += 1
    r["pairs_identical_on_kin"] = same; r["pairs_differing"] = diff
    r["dup_entry_range"] = [int(np.flatnonzero(dupmask).min()), int(np.flatnonzero(dupmask).max())] if dupmask.any() else None
    # after dedupe by key: unique count
    r["unique_after_dedupe"] = int(u.size); r["rows"] = int(key.size)
    res[tree] = r
    if tree == "Truth": tk = set(u.tolist())
    else: res["reco_unique_keys_all_in_truth"] = bool(set(u.tolist()) <= tk)
print(json.dumps(res))
