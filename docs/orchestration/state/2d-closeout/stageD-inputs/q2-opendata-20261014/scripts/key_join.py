"""Join the local and remote copies of one AnaTuple on the event key K and compare per-event values.

Usage: python -I key_join.py <local_path> <remote_url> <tree> <out.json> [N]
  tree: Truth or MasterAnaDev. N (optional): read only the first N entries of each copy.

K = (mc_run, mc_subrun, mc_nthEvtInFile). Compared on shared K: truth kinematics
(mc_incomingE, mc_Q2, mc_w, mc_intType, mc_targetZ), bitwise; the overlay gate
(ev_run, ev_subrun, ev_gate); and for MasterAnaDev also reco MasterAnaDev_muon_P / _theta.
"""
import json, sys, time
import numpy as np
import ROOT

KEY = ["mc_run", "mc_subrun", "mc_nthEvtInFile"]
KIN = ["mc_incomingE", "mc_Q2", "mc_w", "mc_intType", "mc_targetZ"]
GATE = ["ev_run", "ev_subrun", "ev_gate"]
RECO = ["MasterAnaDev_muon_P", "MasterAnaDev_muon_theta"]

def load(src, tree, cols, n):
    t0 = time.time()
    df = ROOT.RDataFrame(tree, src)
    if n:
        df = df.Range(n)
    d = {k: np.asarray(v) for k, v in df.AsNumpy(cols).items()}
    return d, round(time.time() - t0, 1)

def pack(d):
    r, s, e = (d[k].astype(np.int64) for k in KEY)
    assert r.min() >= 0 and s.min() >= 0 and e.min() >= 0 and s.max() < 10**5 and e.max() < 10**5
    return r * 10**10 + s * 10**5 + e

def same_bits(a, b):
    if a.dtype.kind == "f":
        return a.view(np.int64 if a.itemsize == 8 else np.int32) == b.view(np.int64 if b.itemsize == 8 else np.int32)
    return a == b

local, remote, tree, outp = sys.argv[1:5]
n = int(sys.argv[5]) if len(sys.argv) > 5 else 0
cols = KEY + KIN + GATE + (RECO if tree == "MasterAnaDev" else [])
A, ta = load(local, tree, cols, n)
B, tb = load(remote, tree, cols, n)
ka, kb = pack(A), pack(B)
res = {"local": local, "remote": remote, "tree": tree, "first_N": n or "all",
       "read_seconds": {"local": ta, "remote": tb}, "entries_read": {"local": len(ka), "remote": len(kb)}}
ua, ca = np.unique(ka, return_counts=True)
ub, cb = np.unique(kb, return_counts=True)
res["duplicate_K"] = {"local": int((ca > 1).sum()), "remote": int((cb > 1).sum())}
res["K_local"], res["K_remote"] = len(ua), len(ub)
# first occurrence per key for the join
_, ia0 = np.unique(ka, return_index=True)
_, ib0 = np.unique(kb, return_index=True)
common, xa, xb = np.intersect1d(ka[ia0], kb[ib0], return_indices=True)
ia, ib = ia0[xa], ib0[xb]
res["K_intersection"] = len(common)
res["K_only_local"] = len(ua) - len(common)
res["K_only_remote"] = len(ub) - len(common)
for side, k, u in (("only_local", ka, np.setdiff1d(ua, common)), ("only_remote", kb, np.setdiff1d(ub, common))):
    sub = (u // 10**5) % 10**5
    vals, cnt = np.unique(sub, return_counts=True)
    res[f"{side}_by_mc_subrun"] = {int(v): int(c) for v, c in zip(vals, cnt)}
res["mc_run_values"] = {"local": sorted(map(int, np.unique(A["mc_run"]))), "remote": sorted(map(int, np.unique(B["mc_run"])))}
res["n_mc_subruns"] = {"local": int(len(np.unique(A["mc_subrun"]))), "remote": int(len(np.unique(B["mc_subrun"])))}
res["row_order_identical_on_shared"] = bool(np.array_equal(np.sort(ia) == ia, np.ones(len(ia), bool)) and np.all(np.diff(ib[np.argsort(ia)]) > 0))
cmp = {}
for c in KIN + GATE + (RECO if tree == "MasterAnaDev" else []):
    a, b = A[c][ia], B[c][ib]
    eq = same_bits(a, b)
    entry = {"frac_bit_identical": float(eq.mean()) if len(eq) else None, "n_differ": int((~eq).sum())}
    if a.dtype.kind == "f":
        fin = np.isfinite(a) & np.isfinite(b)
        den = np.maximum(np.abs(a[fin]), np.abs(b[fin]))
        rel = np.where(den > 0, np.abs(a[fin] - b[fin]) / np.where(den > 0, den, 1), 0.0)
        entry["max_rel_diff"] = float(rel.max()) if rel.size else None
        entry["n_nonfinite_mismatch"] = int((np.isfinite(a) != np.isfinite(b)).sum())
    cmp[c] = entry
res["compare_on_shared_K"] = cmp
g = np.ones(len(ia), bool)
for c in GATE:
    g &= A[c][ia] == B[c][ib]
res["gate_triple_match_frac"] = float(g.mean()) if len(g) else None
k = np.ones(len(ia), bool)
for c in KIN:
    k &= same_bits(A[c][ia], B[c][ib])
res["all_kinematics_bit_identical_frac"] = float(k.mean()) if len(k) else None
# examples of differences
diff_idx = np.nonzero(~k)[0][:5]
res["examples_kin_differ"] = [{"K": int(common[i]), **{c: [A[c][ia[i]].item(), B[c][ib[i]].item()] for c in KIN}} for i in diff_idx]
json.dump(res, open(outp, "w"), indent=1)
print(json.dumps(res, indent=1))
