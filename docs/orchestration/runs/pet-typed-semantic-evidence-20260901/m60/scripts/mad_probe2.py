#!/usr/bin/env python3
"""READ-ONLY follow-up probe: sentinel inventory, blob 2D/3D coordinate validity,
and per-playlist data/MC semantic identity. No writes."""
import json
import math
import sys
from collections import Counter, defaultdict

import ROOT

TREE = "MasterAnaDev"
NEEDED = [
    "n_prongs", "prong_nParticles", "prong_part_score", "prong_part_mass",
    "prong_part_charge", "prong_part_pid", "prong_dEdXMean", "prong_part_E",
    "prong_part_pos", "gamma1_E", "gamma1_direction", "gamma1_time",
    "MasterAnaDev_BlobX", "MasterAnaDev_BlobY", "MasterAnaDev_BlobZ",
    "MasterAnaDev_BlobT", "MasterAnaDev_BlobTPos", "MasterAnaDev_BlobIs3D",
    "MasterAnaDev_BlobX_sz", "vtx",
]


def summarize(path, n_entries):
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        return {"__error__": "open_failed(BLIND, not zero)"}
    t = f.Get(TREE)
    if not t:
        f.Close()
        return {"__error__": "no_tree(BLIND, not zero)"}
    missing = [b for b in NEEDED if not t.GetBranch(b)]
    t.SetBranchStatus("*", 0)
    for b in NEEDED:
        if t.GetBranch(b):
            t.SetBranchStatus(b, 1)
    n = min(n_entries, int(t.GetEntries()))
    pid_mass = defaultdict(set)
    pid_charge = defaultdict(set)
    pid_score = {}
    pid_n = Counter()
    sent = Counter()
    prongs = 0
    blob_xtab = Counter()
    blobs = 0
    dirnorm = [1e9, -1e9]
    tpos = [1e9, -1e9]
    pos_c3 = [1e9, -1e9]
    blobt = [1e9, -1e9]
    outer_eq_nprongs = 0
    widths = set()
    nparts_max = 0
    for i in range(n):
        t.GetEntry(i)
        if float(t.gamma1_E) > 1e-5:
            d = [float(t.gamma1_direction[k]) for k in range(3)]
            nrm = math.sqrt(sum(x * x for x in d))
            dirnorm[0] = min(dirnorm[0], nrm)
            dirnorm[1] = max(dirnorm[1], nrm)
        nb = int(t.MasterAnaDev_BlobX_sz)
        for j in range(nb):
            blobs += 1
            is3d = int(t.MasterAnaDev_BlobIs3D[j])
            x = float(t.MasterAnaDev_BlobX[j])
            y = float(t.MasterAnaDev_BlobY[j])
            tp = float(t.MasterAnaDev_BlobTPos[j])
            bt = float(t.MasterAnaDev_BlobT[j])
            blobt[0] = min(blobt[0], bt); blobt[1] = max(blobt[1], bt)
            tpos[0] = min(tpos[0], tp); tpos[1] = max(tpos[1], tp)
            key = "is3d=%d x0=%d y0=%d tpos0=%d" % (
                is3d, int(x == 0.0), int(y == 0.0), int(tp == 0.0))
            blob_xtab[key] += 1
        npr = int(t.n_prongs)
        if len(t.prong_part_E) == npr and len(t.prong_part_pos) == npr:
            outer_eq_nprongs += 1
        for k in range(npr):
            prongs += 1
            nparts_max = max(nparts_max, int(t.prong_nParticles[k]))
            pid = int(t.prong_part_pid[k])
            m = float(t.prong_part_mass[k])
            c = int(t.prong_part_charge[k])
            s = float(t.prong_part_score[k])
            de = float(t.prong_dEdXMean[k])
            pid_n[pid] += 1
            pid_mass[pid].add(round(m, 3))
            pid_charge[pid].add(c)
            lo, hi = pid_score.get(pid, (s, s))
            pid_score[pid] = (min(lo, s), max(hi, s))
            if de == -999.0:
                sent["dEdXMean_-999"] += 1
            if m == -1.0:
                sent["mass_-1"] += 1
            if s == -1.0:
                sent["score_-1"] += 1
            if c == -999:
                sent["charge_-999"] += 1
            if c == 2:
                sent["charge_eq_2"] += 1
            if pid == -999:
                sent["pid_-999"] += 1
            widths.add(len(t.prong_part_pos[k]) if k < len(t.prong_part_pos) else -1)
            if k < len(t.prong_part_pos):
                pos_c3[0] = min(pos_c3[0], float(t.prong_part_pos[k][3]))
                pos_c3[1] = max(pos_c3[1], float(t.prong_part_pos[k][3]))
    f.Close()
    return {
        "entries": n, "missing_branches": missing,
        "blobs": blobs, "prongs": prongs,
        "outer_len_eq_nprongs_entries": outer_eq_nprongs,
        "prong_nParticles_max": nparts_max,
        "prong_pos_inner_widths": sorted(widths),
        "gamma1_dir_norm_minmax": dirnorm if dirnorm[0] < 1e9 else "BLIND(no photons)",
        "BlobTPos_minmax": tpos if tpos[0] < 1e9 else "BLIND",
        "BlobT_minmax": blobt if blobt[0] < 1e9 else "BLIND",
        "prong_pos_c3_minmax": pos_c3 if pos_c3[0] < 1e9 else "BLIND",
        "pid_table": {str(p): {"n": pid_n[p], "mass": sorted(pid_mass[p]),
                              "charge": sorted(pid_charge[p]),
                              "score_range": pid_score[p]}
                      for p in sorted(pid_n)},
        "sentinel_counts_over_prongs": dict(sent),
        "blob_is3d_zero_crosstab": dict(sorted(blob_xtab.items())),
    }


def main():
    n = int(sys.argv[1])
    out = {}
    for spec in sys.argv[2:]:
        label, path = spec.split("=", 1)
        out[label] = summarize(path, n)
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
