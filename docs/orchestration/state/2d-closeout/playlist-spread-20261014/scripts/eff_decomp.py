"""Split the MC efficiency S/T per playlist into the steps that produce it.

Usage: python -I eff_decomp.py <dir with runEventLoopOmniFold_<PL>.root> <out.json>

Population: mc_signal_reco, every row (each truth-denominator event appears once; truth-only misses carry
sim = -9999 and sim_pass = 0, runEventLoopOmniFold.cpp:881-887). Weights w_truth unless stated.
  f_present      : weight fraction with sim != -9999. MEASURED: this equals the sim_pass == 1 fraction
                   (f_pass_present = 1.0000 in every playlist), i.e. rows that are in the reco tree but fail
                   the selection also carry sim = -9999. So f_present is the reco-selection efficiency, not
                   the reco-tree presence fraction. n_miss_rows - nTruthOnlyMisses_param counts the
                   in-reco-tree-but-failing rows (unweighted).
  f_pass_present : among those rows, weight fraction with sim_pass == 1
  f_grid_pass    : among passing rows, weight fraction with reco (sim, sim_pz) inside the 10x10 grid
  wreco_over_wtruth : sum(w_reco)/sum(w_truth) over passing in-grid rows (reco-only weights, e.g. MINOS efficiency)
  eff = f_present * f_pass_present * f_grid_pass * wreco_over_wtruth  (= S/T of yields.py)
Each is also given by truth p_|| bin (the yields.py p_|| edges).
"""
import json
import sys

import numpy as np
import ROOT

d, out = sys.argv[1], sys.argv[2]
PLS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
PZ = np.array([1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20, 60])


def ingrid(pt, pz):
    return (pt >= 0) & (pt < 4.5) & (pz >= 1.5) & (pz < 60)


res = {}
for pl in PLS:
    fn = f"{d}/runEventLoopOmniFold_{pl}.root"
    df = ROOT.RDataFrame("mc_signal_reco", fn).Define("sp", "(int)sim_pass")
    a = {k: np.asarray(v) for k, v in df.AsNumpy(["sim", "sim_pz", "sp", "w_reco", "w_truth", "MC_pz"]).items()}
    f = ROOT.TFile.Open(fn)
    nmiss = int(f.Get("nTruthOnlyMisses").GetVal())
    f.Close()
    present = a["sim"] > -9000
    passed = present & (a["sp"] == 1)
    grid = passed & ingrid(a["sim"], a["sim_pz"])
    wt, wr = a["w_truth"], a["w_reco"]

    def steps(m):
        T = wt[m].sum()
        P = wt[m & present].sum()
        Q = wt[m & passed].sum()
        G = wt[m & grid].sum()
        S = wr[m & grid].sum()
        return {"f_present": P / T, "f_pass_present": Q / P, "f_grid_pass": G / Q, "wreco_over_wtruth": S / G,
                "eff": S / T}

    r = {"source": fn, "n_rows": int(len(wt)), "n_miss_rows": int((~present).sum()), "nTruthOnlyMisses_param": nmiss}
    r.update(steps(np.ones(len(wt), bool)))
    ib = np.searchsorted(PZ, a["MC_pz"], side="right") - 1
    r["by_truth_pz"] = {f"{PZ[i]}-{PZ[i + 1]}": steps(ib == i) for i in range(len(PZ) - 1)}
    res[pl] = r
    print(pl, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k not in ("by_truth_pz", "source")},
          flush=True)
ref = ["1A", "1B", "1C", "1D"]
keys = ("f_present", "f_pass_present", "f_grid_pass", "wreco_over_wtruth", "eff")
m = {k: np.mean([res[p][k] for p in ref]) for k in keys}
for p in PLS:
    res[p]["rel_to_1A1D_mean"] = {k: res[p][k] / m[k] for k in keys}
    print(p, "rel", {k: round(v, 4) for k, v in res[p]["rel_to_1A1D_mean"].items()})
json.dump(res, open(out, "w"), indent=1)
