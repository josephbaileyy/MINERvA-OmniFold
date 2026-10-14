"""Per-playlist beam intensity and MINOS-match fraction from a sample of MasterAnaDev AnaTuples (login-node read).

Usage: python -I intensity.py <manifest_dir> <out.json> <n_data_files> <n_mc_files>

For each playlist it reads n_data_files Data and n_mc_files MC AnaTuples, spread evenly through the
playlist manifest (<PL>_Data.txt, <PL>_MC.txt), and keeps reco vertices in the tracker fiducial volume
(5980 < z < 8422 mm, hexagon apothem 850 mm; MAT-MINERvA TargetUtils::IsInHexagon). It reports:
  - numi_pot (1e12 POT per spill) and batch POT per MAT-MINERvA MinervaUniverse::GetBatchPOT();
  - the fraction of fiducial-vertex events that pass the MINOS match the event loop uses
    (isMinosMatchTrack == 1 && MasterAnaDev_minos_trk_is_ok == 1, CVUniverse::HasMINOSMatch);
  - the fraction with tdead = phys_n_dead_discr_pair_upstream_prim_track_proj <= 1 (NoDeadtime(1) is
    PlotUtils::Maximum, i.e. <= 1), and the fraction passing match && tdead<=1 && minos_trk_qp<0 (IsNeutrino);
  - for matched MC events, the mean MINOS-efficiency CV weight of MAT-MINERvA
    MinosMuonEfficiencyCorrection::GetCorrection(p_MINOS, batch_pot, FHC), re-implemented below.
It also sums Meta/POT_Used over the files read and gives fiducial-vertex and chain-passing events per POT.
This is a proxy population (fiducial reco vertex, any interaction), not the analysis selection.
"""
import json
import sys

import numpy as np
import ROOT

man, out, ND, NM = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
PLS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]


def pick(lst, n):
    if n >= len(lst):
        return lst
    idx = np.unique(np.linspace(0, len(lst) - 1, n).round().astype(int))
    return [lst[i] for i in idx]


def inhex(x, y, a=850.0):
    side = a * 2 / np.sqrt(3)
    slope = (side / 2) / a
    xp, yp = np.abs(x), np.abs(y)
    return (xp * xp + yp * yp < a * a) | ((xp <= a) & (yp * yp < side / 2)) | ((xp <= a) & (yp < side - xp * slope))


def batch_pot(numi, bs, rvb):
    bp = numi / 6.0
    bp = np.where((bs == 1) & (rvb < 3), numi / 4.0, bp)
    bp = np.where((bs == 1) & (rvb >= 3), numi / 8.0, bp)
    bp = np.where((bs == 2) & (rvb < 5), numi / 5.0, bp)
    bp = np.where((bs == 2) & (rvb >= 5), numi / 10.0, bp)
    return bp


def poly(c, x):
    return sum(ci * x ** i for i, ci in enumerate(c))


LO = [0.705549, 0.499846, -0.364875, 0.131063, -0.0228281, 0.00154069]
HI = [0.959697, -0.139194, 0.175986, -0.0802815, 0.0162377, -0.00122259]
POT_LO, POT_HI = 3.9385, 8.0311


def minos_corr(p_gev, bpot):
    p = np.clip(p_gev, 1.0, 4.0)
    c1, c2 = poly(HI, p) - 1.0, poly(LO, p) - 1.0
    a1, b1, a2, b2 = POT_HI, POT_HI ** 2, POT_LO, POT_LO ** 2
    det = a1 * b2 - b1 * a2
    A = (c1 * b2 - b1 * c2) / det
    B = (a1 * c2 - c1 * a2) / det
    return 1.0 + A * bpot + B * bpot * bpot


COLS = ["numi_pot", "batch_structure", "reco_vertex_batch", "isMinosMatchTrack", "MasterAnaDev_minos_trk_is_ok",
        "MasterAnaDev_minos_trk_p", "MasterAnaDev_minos_trk_qp", "phys_n_dead_discr_pair_upstream_prim_track_proj", "vx", "vy", "vz"]


def pot_used(files):
    tot = 0.0
    for fn in files:
        f = ROOT.TFile.Open(fn)
        m = f.Get("Meta")
        for e in m:
            tot += float(e.POT_Used)
        f.Close()
    return tot


def read(files):
    df = ROOT.RDataFrame("MasterAnaDev", files)
    df = df.Define("vx", "MasterAnaDev_vtx[0]").Define("vy", "MasterAnaDev_vtx[1]").Define("vz", "MasterAnaDev_vtx[2]")
    df = df.Filter("vz > 5980 && vz < 8422")
    a = {k: np.asarray(v) for k, v in df.AsNumpy(COLS).items()}
    m = inhex(a["vx"], a["vy"])
    return {k: v[m] for k, v in a.items()}


res = {}
for pl in PLS:
    r = {}
    for kind, n in (("Data", ND), ("MC", NM)):
        lst = [x.strip() for x in open(f"{man}/{pl}_{kind}.txt") if x.strip()]
        files = pick(lst, n)
        a = read(files)
        pot = pot_used(files)
        bp = batch_pot(a["numi_pot"], a["batch_structure"], a["reco_vertex_batch"])
        match = (a["isMinosMatchTrack"] == 1) & (a["MasterAnaDev_minos_trk_is_ok"] == 1)
        tdead_ok = a["phys_n_dead_discr_pair_upstream_prim_track_proj"] <= 1
        nu = a["MasterAnaDev_minos_trk_qp"] < 0
        w = minos_corr(a["MasterAnaDev_minos_trk_p"][match] / 1000.0, bp[match])
        r[kind] = {"files": files, "n_fiducial": int(len(bp)),
                   "numi_pot_mean": float(a["numi_pot"].mean()), "numi_pot_median": float(np.median(a["numi_pot"])),
                   "batch_pot_mean": float(bp.mean()), "batch_pot_p90": float(np.percentile(bp, 90)),
                   "minos_match_frac": float(match.mean()),
                   "tdead_le1_frac": float(tdead_ok.mean()),
                   "pot_used_sum": pot,
                   "fiducial_per_1e17_pot": float(len(bp) / pot * 1e17),
                   "chain_per_1e17_pot": float((match & tdead_ok & nu).sum() / pot * 1e17),
                   "match_tdead_nu_frac": float((match & tdead_ok & nu).mean()),
                   "minos_corr_mean_on_matched": float(w.mean()) if len(w) else None,
                   "batch_structure_counts": {str(k): int(v) for k, v in zip(*np.unique(a["batch_structure"], return_counts=True))}}
    for k in ("minos_match_frac", "tdead_le1_frac", "match_tdead_nu_frac", "fiducial_per_1e17_pot", "chain_per_1e17_pot"):
        r[k + "_data_over_mc"] = r["Data"][k] / r["MC"][k]
    res[pl] = r
    print(pl, {k: {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk != "files"}
               if isinstance(v, dict) else round(v, 4) for k, v in r.items()}, flush=True)
json.dump(res, open(out, "w"), indent=1)
