"""Row-joined comparison of the approximate production selection between two copies of one AnaTuple.
Usage: python -I pair.py <srcA> <srcB> <out.json>
Key: (run, subrun, gate-or-nthEvt, ordinal within that key) -- (run,subrun,gate) is a gate key, so the
within-key ordinal distinguishes slices; the report says whether the key sequences agree."""
import json
import math
import sys

import numpy as np
import ROOT

A_src, B_src, out = sys.argv[1:4]
VAR = ["MasterAnaDev_minos_trk_is_ok", "isMinosMatchTrack", "MasterAnaDev_minos_trk_qp", "MasterAnaDev_minos_trk_p",
       "muon_thetaX", "muon_thetaY", "phys_n_dead_discr_pair_upstream_prim_track_proj", "MasterAnaDev_muon_P"]


def load(src):
    f = ROOT.TFile.Open(src)
    H = {b.GetName() for b in f.Get("MasterAnaDev").GetListOfBranches()}
    pot = 0.0
    meta = f.Get("Meta")
    for i in range(meta.GetEntries()):
        meta.GetEntry(i)
        pot += meta.POT_Used
    f.Close()
    key = ["mc_run", "mc_subrun", "mc_nthEvtInFile"] if "mc_nthEvtInFile" in H else ["ev_run", "ev_subrun", "ev_gate"]
    df = (ROOT.RDataFrame("MasterAnaDev", src).Define("vx", "vtx[0]").Define("vy", "vtx[1]").Define("vz", "vtx[2]")
          .Define("pl", "sqrt(MasterAnaDev_leptonE[0]*MasterAnaDev_leptonE[0]+MasterAnaDev_leptonE[1]*MasterAnaDev_leptonE[1]"
                  "+MasterAnaDev_leptonE[2]*MasterAnaDev_leptonE[2])"))
    D = {k: np.asarray(v) for k, v in df.AsNumpy(key + [c for c in VAR if c in H] + ["vx", "vy", "vz", "pl"]).items()}
    k = D[key[0]].astype(np.int64) * 10**11 + D[key[1]].astype(np.int64) * 10**6 + D[key[2]].astype(np.int64)
    order = np.argsort(k, kind="stable")
    ks = k[order]
    first = np.r_[0, np.flatnonzero(np.diff(ks)) + 1]
    ordn = np.arange(len(ks)) - np.repeat(first, np.diff(np.r_[first, len(ks)]))
    ordinal = np.empty_like(ordn)
    ordinal[order] = ordn
    D["K"] = k * 100 + ordinal
    D["_key"] = key
    D["_pot"] = pot
    D["_nbr"] = len(H)
    return D


def sel(D):
    x, y = np.abs(D["vx"]), np.abs(D["vy"])
    a = 850.0
    side = a * 2 / math.sqrt(3)
    hexa = ((x * x + y * y) < a * a) | ((x <= a) & (y < side / 2)) | ((x <= a) & (y < side - x * (side / 2) / a))
    fid = (D["vz"] >= 5980) & (D["vz"] <= 8422) & hexa
    th = np.arctan(np.sqrt(np.tan(D["muon_thetaX"]) ** 2 + np.tan(D["muon_thetaY"]) ** 2))
    D["th"] = th
    mm = (D["isMinosMatchTrack"] == 1) & (D["MasterAnaDev_minos_trk_is_ok"] == 1)
    return fid & (th < math.radians(20)) & mm & (D["phys_n_dead_discr_pair_upstream_prim_track_proj"] <= 1) & (D["MasterAnaDev_minos_trk_qp"] < 0)


A, B = load(A_src), load(B_src)
sA, sB = sel(A), sel(B)
_, ia, ib = np.intersect1d(A["K"], B["K"], return_indices=True)
r = {"A": A_src, "B": B_src, "key": A["_key"], "entries": [len(A["K"]), len(B["K"])], "joined": int(len(ia)),
     "same_entry_order": bool(len(A["K"]) == len(B["K"]) and np.array_equal(A["K"], B["K"])),
     "sel_total": [int(sA.sum()), int(sB.sum())], "pot_used": [A["_pot"], B["_pot"]], "n_branches": [A["_nbr"], B["_nbr"]]}
a, b = sA[ia], sB[ib]
r.update({"sel_both": int((a & b).sum()), "sel_A_only": int((a & ~b).sum()), "sel_B_only": int((~a & b).sum()),
          "sel_unjoined": [int(sA.sum() - a.sum()), int(sB.sum() - b.sum())]})
both = a & b
for c in ("pl", "th", "vz", "MasterAnaDev_minos_trk_p", "MasterAnaDev_muon_P"):
    if c in A and c in B and both.any():
        x, y = A[c][ia][both], B[c][ib][both]
        r["identical_frac_" + c] = float(np.mean(x == y))
        r["max_absdiff_" + c] = float(np.max(np.abs(x - y)))
# Why do A-only / B-only rows differ? Break down by component.
for tag, m, S, T, ii, jj in (("A_only", a & ~b, A, B, ia, ib), ("B_only", ~a & b, B, A, ib, ia)):
    if m.any():
        r[tag + "_other_copy_is_ok_vc"] = {str(k): int(v) for k, v in zip(*np.unique(T["MasterAnaDev_minos_trk_is_ok"][jj][m], return_counts=True))}
        r[tag + "_other_copy_isMinosMatchTrack_vc"] = {str(k): int(v) for k, v in zip(*np.unique(T["isMinosMatchTrack"][jj][m], return_counts=True))}
        r[tag + "_mean_pl_GeV"] = float(np.mean(S["pl"][ii][m]) / 1e3)
# Old-copy muon_P sentinel among events selected in B
if "MasterAnaDev_muon_P" in A:
    r["A_muonP_sentinel_among_B_selected_joined"] = int((A["MasterAnaDev_muon_P"][ia][b] <= -9998).sum())
    r["A_muonP_sentinel_among_A_selected"] = int((A["MasterAnaDev_muon_P"][sA] <= -9998).sum())
# Mechanism: where do the is_ok / muon_P differences sit relative to fiducial+angle?
okA, okB = A["MasterAnaDev_minos_trk_is_ok"][ia], B["MasterAnaDev_minos_trk_is_ok"][ib]
x, y = np.abs(B["vx"][ib]), np.abs(B["vy"][ib])
side = 850.0 * 2 / math.sqrt(3)
hexa = ((x * x + y * y) < 850.0 ** 2) | ((x <= 850.0) & (y < side / 2)) | ((x <= 850.0) & (y < side - x * (side / 2) / 850.0))
fidang = (B["vz"][ib] >= 5980) & (B["vz"][ib] <= 8422) & hexa & (B["th"][ib] < math.radians(20))
d = okA != okB
r["n_is_ok_differs"] = int(d.sum())
r["n_is_ok_differs_in_fid_ang"] = int((d & fidang).sum())
r["n_is_ok_differs_in_fid_ang_and_matched"] = int((d & fidang & (B["isMinosMatchTrack"][ib] == 1)).sum())
r["n_is_ok_differs_in_fid"] = int((d & (B["vz"][ib] >= 5980) & (B["vz"][ib] <= 8422) & hexa).sum())
json.dump(r, open(out, "w"), indent=1)
print(json.dumps({k: v for k, v in r.items() if k not in ("A", "B")}))
