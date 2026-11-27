#!/usr/bin/env python3
"""PTMC: C-COUPLE measured on the real CV omnifile, read-only, before any binding (the director's question of
2026-11-27). It reproduces the driver's two loaders' row rules (re2_driver.py at M: collect_truth_denom_arrays and
collect_signal_arrays_2d, use_weights; the POT scale is a common factor and is left out) with RDataFrame.AsNumpy, then
compares, per truth cell of M's grid (ROOT's cells), the multiset of (truth pT, truth p||, w_truth) over the canonical
denominator's rows with that over the truth-passing signal rows (w = 0 left out). It writes nothing; the result is
JSON on stdout.

  python3 ptmc_couple_check.py OMNIFILE
"""
import json
import math
import sys

import numpy as np

PT = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ = np.array([1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60])
THETA = math.radians(20.0)


def cells(pt, pz):
    ix = np.searchsorted(PT, pt, side="right") - 1
    iy = np.searchsorted(PZ, pz, side="right") - 1
    ok = (ix >= 0) & (ix < PT.size - 1) & (iy >= 0) & (iy < PZ.size - 1)
    return np.where(ok, ix * (PZ.size - 1) + iy, -1)


def main(path):
    import ROOT
    f = ROOT.TFile.Open(path)
    br = {t: sorted(b.GetName() for b in f.Get(t).GetListOfBranches()) for t in ("mc_truth_denom", "mc_signal_reco")}
    flag = f.Get("hasTruthOnlyMisses")
    n_miss = f.Get("nTruthOnlyMisses")
    out = {"hasTruthOnlyMisses": int(flag.GetVal()) if flag else None,
           "nTruthOnlyMisses": int(n_miss.GetVal()) if n_miss else None,
           "id_branches": {t: [b for b in ("mc_run", "mc_subrun", "mc_nthEvtInFile") if b in br[t]] for t in br}}
    f.Close()
    d = ROOT.RDataFrame("mc_truth_denom", path).AsNumpy(["MC", "MC_pz", "w_truth"])
    s = ROOT.RDataFrame("mc_signal_reco", path).AsNumpy(["MC", "MC_pz", "w_truth", "w_reco"])
    dpt, dpz, dw = (np.asarray(d[k], float) for k in ("MC", "MC_pz", "w_truth"))
    lo_pt, hi_pt, lo_pz, hi_pz = PT[0], PT[-1], PZ[0], PZ[-1]
    d_ok = (np.isfinite(dpt) & np.isfinite(dpz) & np.isfinite(dw) & (dw >= 0) & (dw < 1e4)
            & (dpt >= lo_pt) & (dpt <= hi_pt) & (dpz >= lo_pz) & (dpz <= hi_pz))
    spt, spz, sw, swr = (np.asarray(s[k], float) for k in ("MC", "MC_pz", "w_truth", "w_reco"))
    w_ok = np.isfinite(sw) & np.isfinite(swr) & (sw >= 0) & (sw < 1e4) & (swr >= 0) & (swr < 1e4)
    with np.errstate(invalid="ignore"):
        tru_ok = (np.isfinite(spt) & np.isfinite(spz) & (spt >= lo_pt) & (spt <= hi_pt) & (spz >= lo_pz)
                  & (spz <= hi_pz) & (np.arctan2(spt, spz) < THETA))
    s_ok = w_ok & tru_ok
    out["rows"] = {"denominator_total": int(dpt.size), "denominator_kept": int(d_ok.sum()),
                   "signal_total": int(spt.size), "signal_bad_w": int((~w_ok).sum()),
                   "signal_truth_pass": int(s_ok.sum())}

    def rec(pt, pz, w, m):
        g = cells(pt[m], pz[m])
        k = (g >= 0) & (w[m] != 0)
        r = np.rec.fromarrays([g[k], pt[m][k], pz[m][k], w[m][k]], names="g,pt,pz,w")
        r.sort(order=["g", "pt", "pz", "w"])
        return r
    a, b = rec(dpt, dpz, dw, d_ok), rec(spt, spz, sw, s_ok)
    ca, cb = np.bincount(a["g"], minlength=224), np.bincount(b["g"], minlength=224)
    sa = np.bincount(a["g"], weights=a["w"], minlength=224)
    sb = np.bincount(b["g"], weights=b["w"], minlength=224)
    both = (sa > 0) & (sb > 0)
    out["multiset_exact_equal"] = bool(a.size == b.size and np.array_equal(a, b))
    out["n_cells_count_mismatch"] = int((ca != cb).sum())
    out["count_mismatch_cells"] = [[int(j), int(ca[j]), int(cb[j])] for j in np.flatnonzero(ca != cb)[:40]]
    out["sum_max_rel_dev"] = float(np.max(np.abs(sb[both] / sa[both] - 1))) if both.any() else None
    out["n_one_sided_cells"] = int(((sa > 0) != (sb > 0)).sum())
    # where counts agree, the sorted tuples matched in order: how far apart are they?
    dev = {"pt": 0.0, "pz": 0.0, "w_rel": 0.0}
    n_diff_rows, n_cells_tuple_diff = 0, 0
    for j in np.flatnonzero((ca == cb) & (ca > 0)):
        x, y = a[a["g"] == j], b[b["g"] == j]
        if not np.array_equal(x, y):
            n_cells_tuple_diff += 1
            ne = (x["pt"] != y["pt"]) | (x["pz"] != y["pz"]) | (x["w"] != y["w"])
            n_diff_rows += int(ne.sum())
            dev["pt"] = max(dev["pt"], float(np.max(np.abs(x["pt"] - y["pt"]))))
            dev["pz"] = max(dev["pz"], float(np.max(np.abs(x["pz"] - y["pz"]))))
            dev["w_rel"] = max(dev["w_rel"], float(np.max(np.abs(x["w"] / y["w"] - 1))))
    out["equal_count_cells_with_tuple_differences"] = n_cells_tuple_diff
    out["differing_rows_in_those_cells"] = n_diff_rows
    out["sorted_pair_max_deviation"] = dev
    # how many signal tuples have an exact (pt, pz, w) twin in the denominator, globally
    ka = np.rec.fromarrays([a["pt"], a["pz"], a["w"]], names="pt,pz,w")
    kb = np.rec.fromarrays([b["pt"], b["pz"], b["w"]], names="pt,pz,w")
    out["signal_tuples_with_exact_denominator_twin"] = int(np.isin(kb.view(np.dtype((np.void, 24))),
                                                                   ka.view(np.dtype((np.void, 24)))).sum())
    out["n_denominator_tuples"], out["n_signal_tuples"] = int(a.size), int(b.size)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
