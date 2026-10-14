"""Marginal reco/selection census of one AnaTuple file (local path or xrootd URL).
Usage: python -I probe.py <src> <out.json>
Writes entries, branch names, MINOS-match fractions, muon_P sentinel fraction,
an approximate production-precut count, and Meta POT."""
import json
import math
import sys

import numpy as np
import ROOT

src, out = sys.argv[1], sys.argv[2]
f = ROOT.TFile.Open(src)
t = f.Get("MasterAnaDev")
have = sorted(b.GetName() for b in t.GetListOfBranches())
res = {"src": src, "entries": int(t.GetEntries()), "n_branches": len(have), "branches": have}
meta = f.Get("Meta")
if meta:
    pot = {}
    for nm in ("POT_Used", "POT_Total"):
        if meta.GetBranch(nm):
            s = 0.0
            for i in range(meta.GetEntries()):
                meta.GetEntry(i)
                s += getattr(meta, nm)
            pot[nm] = s
    res["meta_pot"] = pot
f.Close()

H = set(have)
cols = [c for c in ("MasterAnaDev_minos_trk_is_ok", "isMinosMatchTrack", "muon_is_minos_match_track",
                    "truth_reco_isMinosMatchTrack", "MasterAnaDev_minos_trk_quality", "MasterAnaDev_muon_P",
                    "MasterAnaDev_minos_trk_p", "MasterAnaDev_minos_trk_qp", "muon_thetaX", "muon_thetaY",
                    "phys_n_dead_discr_pair_upstream_prim_track_proj", "numi_pot") if c in H]
df = ROOT.RDataFrame("MasterAnaDev", src)
if "vtx" in H:
    df = df.Define("vx", "vtx[0]").Define("vy", "vtx[1]").Define("vz", "vtx[2]")
    cols += ["vx", "vy", "vz"]
if "MasterAnaDev_leptonE" in H:
    df = df.Define("pmu_lep", "MasterAnaDev_leptonE.size() >= 3 ? sqrt(MasterAnaDev_leptonE[0]*MasterAnaDev_leptonE[0]"
                   "+MasterAnaDev_leptonE[1]*MasterAnaDev_leptonE[1]+MasterAnaDev_leptonE[2]*MasterAnaDev_leptonE[2]) : -1.0")
    cols.append("pmu_lep")
D = {k: np.asarray(v) for k, v in df.AsNumpy(cols).items()}


def vc(x):
    u, c = np.unique(x, return_counts=True)
    return {str(k): int(n) for k, n in zip(u.tolist(), c.tolist())} if len(u) <= 12 else {"n_unique": int(len(u))}


n = res["entries"]
for c in ("MasterAnaDev_minos_trk_is_ok", "isMinosMatchTrack", "muon_is_minos_match_track",
          "truth_reco_isMinosMatchTrack", "MasterAnaDev_minos_trk_quality"):
    if c in D:
        res["vc_" + c] = vc(D[c])
if "MasterAnaDev_muon_P" in D:
    res["frac_muonP_sentinel"] = float(np.mean(D["MasterAnaDev_muon_P"] <= -9998))
    res["n_muonP_sentinel"] = int(np.sum(D["MasterAnaDev_muon_P"] <= -9998))

# Approximate production precuts (runEventLoopOmniFold.cpp:1710-1715): ZRange, Apothem, theta<20 deg,
# IsMinosMatchMuon (CVUniverse.h:107-114), NoDeadtime(1), IsNeutrino (qp<0). Beam-angle offsets ignored.
def in_hex(x, y, a=850.0):
    x, y = np.abs(x), np.abs(y)
    side = a * 2 / math.sqrt(3)
    inside = (x * x + y * y) < a * a
    inside |= (x <= a) & (y < side / 2)
    inside |= (x <= a) & (y < side - x * (side / 2) / a)
    return inside


if all(k in D for k in ("vx", "vy", "vz", "muon_thetaX", "muon_thetaY")):
    fid = (D["vz"] >= 5980) & (D["vz"] <= 8422) & in_hex(D["vx"], D["vy"])
    th = np.arctan(np.sqrt(np.tan(D["muon_thetaX"]) ** 2 + np.tan(D["muon_thetaY"]) ** 2))
    ang = th < math.radians(20.0)
    mm = (D.get("isMinosMatchTrack", np.ones(n)) == 1) & (D["MasterAnaDev_minos_trk_is_ok"] == 1)
    dead = D["phys_n_dead_discr_pair_upstream_prim_track_proj"] <= 1
    nu = D["MasterAnaDev_minos_trk_qp"] < 0
    steps = {"fid": fid, "fid_ang": fid & ang, "fid_ang_minos": fid & ang & mm,
             "fid_ang_minos_dead": fid & ang & mm & dead, "sel_approx": fid & ang & mm & dead & nu}
    res["cutflow"] = {k: int(v.sum()) for k, v in steps.items()}
    res["frac_minos_given_fid_ang"] = float((fid & ang & mm).sum() / max((fid & ang).sum(), 1))
    if "pmu_lep" in D:
        s = steps["sel_approx"]
        res["sel_pmu_lep_mean_GeV"] = float(np.mean(D["pmu_lep"][s]) / 1e3) if s.any() else None
        res["sel_theta_mean_deg"] = float(np.degrees(np.mean(th[s]))) if s.any() else None
if "numi_pot" in D:
    res["sum_numi_pot_entries"] = float(np.sum(D["numi_pot"]))
res["branches"] = have
with open(out, "w") as fh:
    json.dump(res, fh, indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "branches"}, indent=1))
