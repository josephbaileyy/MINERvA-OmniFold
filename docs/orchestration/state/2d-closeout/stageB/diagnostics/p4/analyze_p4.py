#!/usr/bin/env python3
"""P4 G1 census analysis (runs after the 13 jobs of sbatch_p4.sh). Read-only.

Inputs, under <out>/ (default layout of sbatch_p4.sh):
  <PL>/runEventLoopOmniFold.root   main output of the patched binary (census ON), PL = 1A..1P
  <PL>/g1_census.root              census tree g1_census + counters
  <PL>/provenance.txt              binary sha256 and rc of the job
  ctl1L/...                        unpatched copy on 1L (no-op control; no census file)
Production per-playlist files 2d-unfolding/runEventLoopOmniFold_<PL>.root (May 2026, behind E_U's omnifile
43f8cc16) for the bridge; E_U (pinned) for the reported-cell mask; the repaired per-cell sigma (pinned).

Steps
 0. Gates (any failure -> outcome INCONCLUSIVE (<reason>), never an exception or a silent pass): every job
    output present; provenance rc=0; binary sha256 = the reviewed one (patched for playlists, unpatched for
    the control); census selftestN = nSelftestInjected = 0; counter identity
    nBkgSkipped = nBkgSkippedInReco + nG1 + nG1DupKey; no-op control ctl1L vs 1L IDENTICAL (strict).
 1. Bridge: each <PL> main output vs the May production file, common branches (reported, not a gate:
    equality ties the census to E_U's input; inequality is reported with the json).
 2. Census: per playlist and total, the counters; G1 rows binned on reco (pT, p_par) with the analysis edges
    (reported_cells.PT_EDGES / PZ_EDGES, 14 x 16 = 224 cells), weight w_reco (the CV reco-mode weight). The
    census total wG1 is reported next to the binned sum; their difference is the out-of-grid weight.
    nSigLoopNoTruthPassReco (the truth-key route seen from the signal loop, truth-mode classification) is
    reported against nG1 (all routes, reco-mode classification).
 3. Denominators, from the same jobs' main outputs (hadd convention: MC summed over playlists, scaled by
    sum dataPOTUsed / sum mcPOTUsed as the driver does on the hadded file):
      S_c = sum w_reco over mc_signal_reco rows with sim_pass == 1 in reco cell c
      B_c = sum w_bkg over mc_background rows in reco cell c
      D_c = data rows with measured_pass == 1 in reco cell c
    Per reported cell: f_S = G1_c / S_c, f_SB = G1_c / (S_c + B_c), f_D = scale * G1_c / D_c. The integrals
    integral_f_* are over the whole 224-cell grid, not only the 205 reported cells.
 4. Classification: truth_status (0: no fiducial truth-tree failure record; 1: record, mask valid;
    2: key is in the truth denominator yet absent from the reco tree) and, for status 1, the lowest-numbered
    constraint (bits 0-7 of the mask legend) that failed on the truth-tree row; reco - true medians.
 5. Materiality (pre-declared in DESIGN.md §6): IMPLICATES_E_U if integral_f_S >= 0.5 %, or if any
    reported cell has f_S >= sigma_rel,c / 3, with sigma_rel,c the per-cell total relative sigma of the
    repaired construction (quadrature of universe, boot_vl170, ml in sigma_abs_205_repaired.json, divided by
    E_U). f_S is a first-order proxy for the central-value bias in the matching truth cell, not an unfolded
    shift. A failed gate gives INCONCLUSIVE, with " (would implicate E_U)" appended if the test would fire.
 6. Any run other than the full set (all 12 playlists and --control ctl1L:1L) has its outcome prefixed
    "SMOKE/SUBSET (not the P4 result): ".

  python analyze_p4.py <out dir> <sigma_abs_205_repaired.json> <result.json>
         [--playlists 1A ...] [--control ctl1L:1L]
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
PROD = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
# reported_cells.py from the pinned 09c8bae0 archive (the production checkout at 32e403b8 lacks it)
RC_DIR = "/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/repo/2d-unfolding/uq"
RC_SHA = "2ddf7c9fbe4c0ffc236c3f82e4b81b12204d17005f90b2dcc0f7a5db5e501594"  # origin/main b456fa4d blob
EU = f"{PROD}/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
EU_SHA = "4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c"
SIGMA_SHA = "4e48f6392c9e84a5ad2f9b32bf01ac854f5b63ce2003d3b366a1956b8ee80ef8"
PATCHED_SHA = "d1a7cf346bed88d60e7edc360ca4836ee46a968dc6a7abd4400e066bc4a9c9e0"
UNPATCHED_SHA = "1ab7525e41c4a16eba728ac29dac8bfdcbfa792cc16bb8ca2ba141a24eb950ae"
PLAYLISTS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
COUNTERS = ["nTruthFail", "nTruthFidFailStored", "nTruthFidFailDupKey", "nSigLoopNoTruth",
            "nSigLoopNoTruthPassReco", "wSigLoopNoTruthPassReco", "nBkgSkipped", "nBkgSkippedInReco",
            "nG1", "nG1DupKey", "nG1Status0", "nG1Status1", "nG1Status2", "wG1", "selftestN",
            "nSelftestInjected"]


def sha(p):
    h = hashlib.sha256()
    with open(os.path.realpath(p), "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


if sha(os.path.join(RC_DIR, "reported_cells.py")) != RC_SHA:
    sys.exit(f"[FAIL] {RC_DIR}/reported_cells.py is not origin/main's ({RC_SHA})")
sys.path.insert(0, RC_DIR)
from reported_cells import PT_EDGES, PZ_EDGES, grid_hist_to_array  # noqa: E402


def hist2(x, y, w):
    h, _, _ = np.histogram2d(x, y, bins=[PT_EDGES, PZ_EDGES], weights=w)
    return h


def cols(path, tree, names, sel=None):
    df = ROOT.RDataFrame(tree, path)
    if sel:
        df = df.Filter(sel)
    d = df.AsNumpy(names)
    return {k: np.asarray(v, float) for k, v in d.items()}


def param(f, n):
    o = f.Get(n)
    return None if not o else o.GetVal()


def provenance(d, want_sha):
    """Reason string if the job's provenance fails, else None."""
    p = os.path.join(d, "provenance.txt")
    if not os.path.exists(p):
        return f"{d}: provenance.txt missing"
    t = open(p).read()
    m = re.search(r"^bin=\S+ sha256=([0-9a-f]{64})$", t, re.M)
    if not m or m.group(1) != want_sha:
        return f"{d}: binary sha256 {m.group(1) if m else 'absent'} != {want_sha}"
    if not re.search(r"^rc=0 ", t, re.M):
        return f"{d}: rc != 0"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("sigma_json")
    ap.add_argument("result_json")
    ap.add_argument("--playlists", nargs="+", default=PLAYLISTS)
    ap.add_argument("--control", default="ctl1L:1L", help="CONTROLTAG:PLAYLIST compared strictly")
    a = ap.parse_args()
    od = a.out_dir
    out = {"gates": [], "controls": {}, "bridge": {}, "per_playlist": {}, "playlists": a.playlists,
           "pins": {"reported_cells": RC_SHA, "E_U": EU_SHA, "sigma_json": SIGMA_SHA,
                    "patched_bin": PATCHED_SHA, "unpatched_bin": UNPATCHED_SHA}}
    fail = out["gates"]
    if sha(EU) != EU_SHA:
        fail.append(f"E_U sha256 != {EU_SHA}")
    if sha(a.sigma_json) != SIGMA_SHA:
        fail.append(f"sigma json sha256 != {SIGMA_SHA}")
    ctag, cpl = a.control.split(":")
    for tag, want, need_census in [(pl, PATCHED_SHA, True) for pl in a.playlists] + [(ctag, UNPATCHED_SHA, False)]:
        d = os.path.join(od, tag)
        for fn in ["runEventLoopOmniFold.root"] + (["g1_census.root"] if need_census else []):
            if not os.path.exists(os.path.join(d, fn)) or os.path.getsize(os.path.join(d, fn)) == 0:
                fail.append(f"{d}/{fn} missing or empty")
        r = provenance(d, want)
        if r:
            fail.append(r)
    if fail:
        out["outcome"] = "INCONCLUSIVE (" + "; ".join(fail) + ")"
        if a.playlists != PLAYLISTS or a.control != "ctl1L:1L":
            out["outcome"] = "SMOKE/SUBSET (not the P4 result): " + out["outcome"]
        json.dump(out, open(a.result_json, "w"), indent=1)
        print(out["outcome"])
        sys.exit(3)

    cmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "compare_outputs.py")
    r = subprocess.run([sys.executable, cmp, f"{od}/{ctag}/runEventLoopOmniFold.root",
                        f"{od}/{cpl}/runEventLoopOmniFold.root", "--strict", "--json",
                        f"{od}/cmp_{ctag}.json"], capture_output=True, text=True)
    out["controls"][f"noop_{ctag}_vs_{cpl}"] = "IDENTICAL" if r.returncode == 0 else "DIFFERENT"
    if r.returncode != 0:
        fail.append(f"no-op control {ctag} vs {cpl} DIFFERENT")

    G = np.zeros((len(PT_EDGES) - 1, len(PZ_EDGES) - 1))
    S, B, Dd = np.zeros_like(G), np.zeros_like(G), np.zeros_like(G)
    pot_d = pot_mc = 0.0
    status = np.zeros(3)
    first_fail = {}
    reco_true = []
    tot = {n: 0.0 for n in COUNTERS}
    for pl in a.playlists:
        main_f = f"{od}/{pl}/runEventLoopOmniFold.root"
        cen_f = f"{od}/{pl}/g1_census.root"
        r = subprocess.run([sys.executable, cmp, main_f, f"{PROD}/2d-unfolding/runEventLoopOmniFold_{pl}.root",
                            "--json", f"{od}/cmp_prod_{pl}.json"], capture_output=True, text=True)
        out["bridge"][pl] = "IDENTICAL on common branches" if r.returncode == 0 else "DIFFERENT (see json)"
        fc = ROOT.TFile.Open(cen_f)
        c = {n: param(fc, n) for n in COUNTERS}
        fc.Close()
        out["per_playlist"][pl] = c
        for n in COUNTERS:
            tot[n] += c[n] or 0
        if c["selftestN"] != 0 or c["nSelftestInjected"] != 0:
            fail.append(f"{pl}: self-test active (selftestN {c['selftestN']}, injected {c['nSelftestInjected']})")
        if c["nBkgSkipped"] != c["nBkgSkippedInReco"] + c["nG1"] + c["nG1DupKey"]:
            fail.append(f"{pl}: counter identity nBkgSkipped != nBkgSkippedInReco + nG1 + nG1DupKey")
        g = cols(cen_f, "g1_census", ["reco_pt", "reco_pz", "w_reco", "true_pt", "true_pz", "truth_mask",
                                      "truth_status"])
        G += hist2(g["reco_pt"], g["reco_pz"], g["w_reco"])
        for s in range(3):
            status[s] += np.sum(g["w_reco"][g["truth_status"] == s])
        st1 = g["truth_status"] == 1
        for m, w in zip(g["truth_mask"][st1].astype(int), g["w_reco"][st1]):
            fails = [b for b in range(8) if not (m >> b) & 1]
            key = f"bit{fails[0]}" if fails else "none_failed"
            first_fail[key] = first_fail.get(key, 0.0) + w
        reco_true.append(np.c_[g["reco_pt"], g["true_pt"], g["reco_pz"], g["true_pz"]])
        s = cols(main_f, "mc_signal_reco", ["sim", "sim_pz", "w_reco"], "sim_pass == 1")
        S += hist2(s["sim"], s["sim_pz"], s["w_reco"])
        b = cols(main_f, "mc_background", ["sim_background", "sim_background_pz", "w_bkg"])
        B += hist2(b["sim_background"], b["sim_background_pz"], b["w_bkg"])
        d = cols(main_f, "data", ["measured", "measured_pz"], "measured_pass == 1")
        Dd += hist2(d["measured"], d["measured_pz"], None)
        fm = ROOT.TFile.Open(main_f)
        pot_d += param(fm, "dataPOTUsed")
        pot_mc += param(fm, "mcPOTUsed")
        fm.Close()
    scale = pot_d / pot_mc
    fe = ROOT.TFile.Open(EU)
    eu = grid_hist_to_array(fe.Get("hXSec2D"))
    fe.Close()
    rep = eu > 0
    sj = json.load(open(a.sigma_json))
    sab = {k: np.asarray(v, float) for k, v in sj["sigma_abs"].items()}
    sig = np.sqrt(sab["universe"] ** 2 + sab["boot_vl170"] ** 2 + sab["ml"] ** 2)
    cells = [tuple(c) for c in sj["cells"]]
    if sorted(cells) != sorted(map(tuple, np.argwhere(rep).tolist())):
        fail.append("sigma json cells != E_U reported cells")
    srel = np.array([sig[k] / eu[pt, pz] for k, (pt, pz) in enumerate(cells)])
    with np.errstate(divide="ignore", invalid="ignore"):
        fS, fSB, fD = G / S, G / (S + B), scale * G / Dd
    fS_rep = np.array([fS[pt, pz] for pt, pz in cells])
    out["totals"] = {"counters_summed": tot,
                     "G1_weighted_census_wG1": tot["wG1"], "G1_weighted_binned_on_grid": float(G.sum()),
                     "G1_weighted_out_of_grid": float(tot["wG1"] - G.sum()),
                     "G1_weighted_outside_reported_cells_on_grid": float(G[~rep].sum()),
                     "nG1": tot["nG1"], "nSigLoopNoTruthPassReco": tot["nSigLoopNoTruthPassReco"],
                     "nG1DupKey": tot["nG1DupKey"],
                     "S_weighted": float(S.sum()), "B_weighted": float(B.sum()), "D": float(Dd.sum()),
                     "pot_scale": scale,
                     "integral_f_S_grid224": float(G.sum() / S.sum()) if S.sum() else None,
                     "integral_f_SB_grid224": float(G.sum() / (S + B).sum()) if (S + B).sum() else None,
                     "integral_f_D_grid224": float(scale * G.sum() / Dd.sum()) if Dd.sum() else None}
    out["per_cell"] = {"cells": cells, "f_S": [float(x) for x in fS_rep],
                       "f_SB": [float(fSB[pt, pz]) for pt, pz in cells],
                       "f_D": [float(fD[pt, pz]) for pt, pz in cells],
                       "G1": [float(G[pt, pz]) for pt, pz in cells], "sigma_rel_repaired": list(map(float, srel))}
    finite = np.nan_to_num(fS_rep, nan=0.0)
    out["per_cell_summary"] = {"f_S_median": float(np.median(finite)), "f_S_max": float(np.max(finite)),
                               "n_cells_f_S_ge_sigma_over_3": int(np.sum(finite >= srel / 3)),
                               "n_cells_S_zero": int(np.sum(np.array([S[pt, pz] for pt, pz in cells]) == 0))}
    out["classification"] = {"status_weighted": {str(k): float(v) for k, v in enumerate(status)},
                             "first_failed_truth_constraint_weighted": first_fail}
    rt = np.vstack(reco_true)
    if len(rt):
        out["classification"]["reco_minus_true_pt_median"] = float(np.median(rt[:, 0] - rt[:, 1]))
        out["classification"]["reco_minus_true_pz_median"] = float(np.median(rt[:, 2] - rt[:, 3]))
    fS_int = out["totals"]["integral_f_S_grid224"] or 0.0
    implicates = fS_int >= 0.005 or out["per_cell_summary"]["n_cells_f_S_ge_sigma_over_3"] > 0
    if fail:
        out["outcome"] = "INCONCLUSIVE (" + "; ".join(fail) + ")" + (" (would implicate E_U)" if implicates else "")
    else:
        out["outcome"] = ("MEASURED; IMPLICATES_E_U (report to the director at once)" if implicates else
                          "MEASURED; below the pre-declared materiality bound")
    if a.playlists != PLAYLISTS or a.control != "ctl1L:1L":
        out["outcome"] = "SMOKE/SUBSET (not the P4 result): " + out["outcome"]
    json.dump(out, open(a.result_json, "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("gates", "controls", "bridge", "totals", "per_cell_summary",
                                          "classification", "outcome")}, indent=1))
    sys.exit(0 if not fail else 3)


if __name__ == "__main__":
    main()
