#!/usr/bin/env python3
"""READ-ONLY MAD branch-semantics probe. No writes, no production output.

Phase A: branch metadata (title/leaf-counter/class) for the PET typed-descriptor
         branch families, one file per ME-FHC playlist, data and MC.
Phase B: bounded value statistics (first N entries of one data + one MC file)
         that decide component order, unit family, and per-prong vs per-particle
         indexing questions the official documentation does not answer.
"""
import json
import math
import sys
from collections import defaultdict

import ROOT

TREE = "MasterAnaDev"
META_BRANCHES = [
    "n_prongs", "prong_nParticles", "prong_part_score", "prong_part_mass",
    "prong_part_charge", "prong_part_pid", "prong_dEdXMean", "prong_part_E",
    "prong_part_pos",
    "gamma1_direction", "gamma2_direction", "gamma1_time", "gamma1_E",
    "gamma1_P", "gamma1_px", "gamma1_py", "gamma1_pz", "gamma1_dEdx",
    "MasterAnaDev_BlobX", "MasterAnaDev_BlobY", "MasterAnaDev_BlobZ",
    "MasterAnaDev_BlobT", "MasterAnaDev_BlobTPos", "MasterAnaDev_BlobTotalE",
    "MasterAnaDev_BlobIs3D", "MasterAnaDev_BlobNClusters",
    "MasterAnaDev_BlobX_sz", "MasterAnaDev_BlobTPos_sz",
    "MasterAnaDev_BlobView", "MasterAnaDev_BlobTPosPerCluster",
    "vtx",
]


def branch_meta(path):
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        return {"__error__": "open_failed"}
    t = f.Get(TREE)
    if not t:
        f.Close()
        return {"__error__": "no_tree"}
    out = {"__entries__": int(t.GetEntries())}
    for name in META_BRANCHES:
        b = t.GetBranch(name)
        if not b:
            out[name] = None
            continue
        cls = b.GetClassName() if hasattr(b, "GetClassName") else ""
        out[name] = {"title": b.GetTitle(), "class": cls}
    f.Close()
    return out


def stats(values):
    if not values:
        return "BLIND(no values collected)"
    v = sorted(values)
    return {"n": len(v), "min": v[0], "med": v[len(v) // 2], "max": v[-1]}


def value_probe(path, nmax):
    f = ROOT.TFile.Open(path, "READ")
    t = f.Get(TREE)
    t.SetBranchStatus("*", 0)
    for name in META_BRANCHES:
        if t.GetBranch(name):
            t.SetBranchStatus(name, 1)
    n = min(nmax, int(t.GetEntries()))
    acc = defaultdict(list)
    pid_tab = defaultdict(lambda: {"n": 0, "mass": set(), "charge": set(),
                                   "score_min": None, "score_max": None})
    len_agreement = {"E_eq_nprongs": 0, "pos_eq_nprongs": 0,
                     "E_eq_sum_nparticles": 0, "nparticles_gt1": 0,
                     "nparticles_values": set(), "entries": 0}
    widths = {"pos": set(), "E": set()}
    for i in range(n):
        t.GetEntry(i)
        len_agreement["entries"] += 1
        # --- photons
        e1 = float(t.gamma1_E)
        if e1 > 1e-5:
            d = [float(t.gamma1_direction[k]) for k in range(3)]
            acc["gamma1_dir_norm"].append(math.sqrt(sum(x * x for x in d)))
            acc["gamma1_time"].append(float(t.gamma1_time))
            acc["gamma1_dEdx"].append(float(t.gamma1_dEdx))
            p = [float(t.gamma1_px), float(t.gamma1_py), float(t.gamma1_pz)]
            pm = math.sqrt(sum(x * x for x in p))
            acc["gamma1_P_over_E"].append(float(t.gamma1_P) / e1 if e1 else float("nan"))
            if pm > 0:
                cos = sum(a * b for a, b in zip(d, p)) / (pm * math.sqrt(sum(x * x for x in d)) or 1.0)
                acc["cos(dir,p)"].append(cos)
        # --- event vertex, for a unit anchor
        acc["vtx_x"].append(float(t.vtx[0]))
        acc["vtx_z"].append(float(t.vtx[2]))
        acc["vtx_t"].append(float(t.vtx[3]))
        # --- blobs
        nb = int(t.MasterAnaDev_BlobX_sz)
        for j in range(nb):
            acc["BlobX"].append(float(t.MasterAnaDev_BlobX[j]))
            acc["BlobY"].append(float(t.MasterAnaDev_BlobY[j]))
            acc["BlobZ"].append(float(t.MasterAnaDev_BlobZ[j]))
            acc["BlobT"].append(float(t.MasterAnaDev_BlobT[j]))
            acc["BlobTPos"].append(float(t.MasterAnaDev_BlobTPos[j]))
            acc["BlobTotalE"].append(float(t.MasterAnaDev_BlobTotalE[j]))
            acc["BlobIs3D"].append(int(t.MasterAnaDev_BlobIs3D[j]))
        # --- prongs
        npr = int(t.n_prongs)
        lE = len(t.prong_part_E)
        lpos = len(t.prong_part_pos)
        nparts = [int(t.prong_nParticles[k]) for k in range(npr)] if t.GetBranch("prong_nParticles") else []
        len_agreement["nparticles_values"].update(nparts)
        if any(x > 1 for x in nparts):
            len_agreement["nparticles_gt1"] += 1
        if lE == npr:
            len_agreement["E_eq_nprongs"] += 1
        if lpos == npr:
            len_agreement["pos_eq_nprongs"] += 1
        if nparts and lE == sum(nparts):
            len_agreement["E_eq_sum_nparticles"] += 1
        for k in range(lpos):
            widths["pos"].add(len(t.prong_part_pos[k]))
            row = [float(x) for x in t.prong_part_pos[k]]
            for c, val in enumerate(row):
                acc[f"prong_pos_c{c}"].append(val)
        for k in range(lE):
            widths["E"].add(len(t.prong_part_E[k]))
            row = [float(x) for x in t.prong_part_E[k]]
            for c, val in enumerate(row):
                acc[f"prong_E_c{c}"].append(val)
            if len(row) == 4:
                p2 = row[0] ** 2 + row[1] ** 2 + row[2] ** 2
                m2 = row[3] ** 2 - p2
                acc["prong_sqrt(E2-p2)"].append(math.copysign(math.sqrt(abs(m2)), m2))
        for k in range(npr):
            pid = int(t.prong_part_pid[k])
            mass = float(t.prong_part_mass[k])
            chg = int(t.prong_part_charge[k])
            sc = float(t.prong_part_score[k])
            acc["prong_dEdXMean"].append(float(t.prong_dEdXMean[k]))
            acc["prong_score"].append(sc)
            e = pid_tab[pid]
            e["n"] += 1
            e["mass"].add(round(mass, 3))
            e["charge"].add(chg)
            e["score_min"] = sc if e["score_min"] is None else min(e["score_min"], sc)
            e["score_max"] = sc if e["score_max"] is None else max(e["score_max"], sc)
    f.Close()
    return {
        "entries_read": n,
        "stats": {k: stats(v) for k, v in sorted(acc.items())},
        "prong_len_agreement": {k: (sorted(v) if isinstance(v, set) else v)
                                for k, v in len_agreement.items()},
        "prong_inner_widths": {k: sorted(v) for k, v in widths.items()},
        "pid_table": {str(k): {"n": v["n"], "mass_values": sorted(v["mass"])[:8],
                               "charge_values": sorted(v["charge"]),
                               "score_min": v["score_min"], "score_max": v["score_max"]}
                      for k, v in sorted(pid_tab.items())},
    }


def main():
    mode = sys.argv[1]
    if mode == "meta":
        result = {p: branch_meta(p) for p in sys.argv[2:]}
    else:
        nmax = int(sys.argv[2])
        result = {p: value_probe(p, nmax) for p in sys.argv[3:]}
    print(json.dumps(result, indent=1, default=str))


if __name__ == "__main__":
    main()
