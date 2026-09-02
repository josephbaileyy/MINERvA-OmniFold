#!/usr/bin/env python3
"""READ-ONLY: per-pid crosstab of dEdXMean validity, sqrt(E^2-p^2), charge and score.
One file per ME-FHC playlist per role, so playlist and role are both varied. No writes."""
import json, math, sys
from collections import Counter, defaultdict
import ROOT

NEEDED = ["n_prongs","prong_part_pid","prong_part_mass","prong_part_charge",
          "prong_part_score","prong_dEdXMean","prong_part_E"]
SENT = (-999.0, -9999.0)

def one(path, n_entries):
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        return {"__error__": "open_failed(BLIND not zero)"}
    t = f.Get("MasterAnaDev")
    if not t:
        f.Close(); return {"__error__": "no_tree(BLIND not zero)"}
    t.SetBranchStatus("*", 0)
    for b in NEEDED:
        if t.GetBranch(b): t.SetBranchStatus(b, 1)
    n = min(n_entries, int(t.GetEntries()))
    npid = Counter(); dvalid = Counter(); m2 = defaultdict(Counter)
    chg = defaultdict(Counter); scr = {}; mass = defaultdict(Counter)
    for i in range(n):
        t.GetEntry(i)
        npr = int(t.n_prongs)
        lE = len(t.prong_part_E)
        for k in range(npr):
            pid = int(t.prong_part_pid[k])
            npid[pid] += 1
            d = float(t.prong_dEdXMean[k])
            if d not in SENT: dvalid[pid] += 1
            chg[pid][int(t.prong_part_charge[k])] += 1
            mass[pid][round(float(t.prong_part_mass[k]), 3)] += 1
            s = float(t.prong_part_score[k])
            lo, hi = scr.get(pid, (s, s)); scr[pid] = (min(lo, s), max(hi, s))
            if k < lE and len(t.prong_part_E[k]) == 4:
                r = [float(x) for x in t.prong_part_E[k]]
                v = r[3]**2 - (r[0]**2 + r[1]**2 + r[2]**2)
                m2[pid][round(math.copysign(math.sqrt(abs(v)), v), 3)] += 1
    f.Close()
    return {"entries": n, "prongs": sum(npid.values()),
            "by_pid": {str(p): {"n": npid[p], "dedx_valid": dvalid[p],
                                "mass": dict(mass[p].most_common(4)),
                                "sqrt_E2_p2": dict(m2[p].most_common(4)),
                                "charge": dict(chg[p]),
                                "score_range": scr[p]}
                       for p in sorted(npid)}}

def main():
    n = int(sys.argv[1])
    print(json.dumps({s.split("=",1)[0]: one(s.split("=",1)[1], n) for s in sys.argv[2:]},
                     indent=1, default=str))

if __name__ == "__main__":
    main()
