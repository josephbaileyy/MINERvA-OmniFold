#!/usr/bin/env python3
"""Verify the built period inputs against their per-playlist sources (login node, read only).

    python3 verify_inputs.py OUT.json

For each period P in PA, PB, PC, ALL:
  merged omnifile  : mcPOTUsed, dataPOTUsed, hasTruthOnlyMisses, nTruthOnlyMisses equal the per-playlist sums;
                     the four trees' entry counts equal the sums; every branch's values, in order, equal the
                     concatenation of the per-playlist branches (sha256 of the value bytes, tree by tree).
  ALL only         : every branch also equals the production CV omnifile (CFS copy, sha256 43f8cc16...), and its
                     parameters are equal, so the control unfold reads the same events in the same order as XR-L0.
  flux file        : the histogram equals an independent numpy recomputation of the data-POT-weighted mean of
                     the per-playlist fluxes; DataPOTUsedForFluxWeighting equals the merged dataPOTUsed;
                     ALL equals the production flux file (sha256 d40aea69...) bin by bin.
Exits nonzero if any check fails.
"""
import hashlib
import json
import math
import os
import sys

import numpy as np
import ROOT

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import periods as PD  # noqa: E402

ROOT.gROOT.SetBatch(True)
try:
    ROOT.gSystem.Load("libMAT")
except Exception:  # noqa: BLE001
    pass

TREES = ["data", "mc_signal_reco", "mc_background", "mc_truth_denom"]
PARS = ["mcPOTUsed", "dataPOTUsed", "hasTruthOnlyMisses", "nTruthOnlyMisses"]
FLUXH = "pTmu_reweightedflux_integrated"
out_json = sys.argv[1]
res = {"commit": PD.COMMIT, "pins": {k: PD.check_pin(k) for k in ("combine_flux", "cv_omnifile_cfs", "flux_production")},
       "periods": {}}
fails = []


def params(f):
    o = {}
    for k in PARS:
        p = f.Get(k)
        o[k] = None if not p else (float(p.GetVal()) if "double" in p.ClassName() else int(p.GetVal()))
    return o


def tree_arrays(path, tree):
    f = ROOT.TFile.Open(path)
    t = f.Get(tree)
    names = [b.GetName() for b in t.GetListOfBranches()]
    n = int(t.GetEntries())
    f.Close()
    if n == 0:
        return names, n, {b: np.zeros(0) for b in names}
    arr = ROOT.RDataFrame(tree, path).AsNumpy(names)
    return names, n, {b: np.ascontiguousarray(arr[b]) for b in names}


def file_hashes(path):
    """{tree: {"entries": n, "branches": {b: sha256 of dtype+bytes}}} for one file."""
    o = {}
    for t in TREES:
        names, n, a = tree_arrays(path, t)
        o[t] = {"entries": n, "branches": {b: hashlib.sha256(str(a[b].dtype).encode() + a[b].tobytes()).hexdigest()
                                           for b in names}}
    return o


# per-playlist sources: parameters, entries, and incremental concatenation hashers per period
src = {}
concat = {P: {t: {} for t in TREES} for P in PD.PERIODS}
dtypes = {}
for pl in PD.PLS:
    path = PD.per_playlist_omnifile(pl)
    f = ROOT.TFile.Open(path)
    src[pl] = {"path": path, "params": params(f)}
    f.Close()
    src[pl]["entries"] = {}
    for t in TREES:
        names, n, a = tree_arrays(path, t)
        src[pl]["entries"][t] = n
        for P, pls in PD.PERIODS.items():
            if pl not in pls:
                continue
            for b in names:
                dt = str(a[b].dtype)
                h = concat[P][t].setdefault(b, hashlib.sha256(dt.encode()))   # same dtype prefix as file_hashes
                if dtypes.setdefault((t, b), dt) != dt:
                    fails.append(f"dtype of {t}.{b} differs in {pl}")
                h.update(a[b].tobytes())
    print(f"[verify] read {pl}", flush=True)

cfs = file_hashes(PD.PINS["cv_omnifile_cfs"][0])
fcfs = ROOT.TFile.Open(PD.PINS["cv_omnifile_cfs"][0])
cfs_params = params(fcfs)
fcfs.Close()

for P, pls in PD.PERIODS.items():
    path = PD.merged_omnifile(P)
    r = {"playlists": pls, "omnifile": {"path": path, "sha256": PD.sha256(path), "bytes": os.path.getsize(path)}}
    f = ROOT.TFile.Open(path)
    got = params(f)
    f.Close()
    want_seq = {}
    for k in PARS:
        s = 0.0 if k.endswith("POTUsed") else 0
        for pl in pls:
            s = s + src[pl]["params"][k]
        want_seq[k] = s
    r["params"] = {k: {"merged": got[k], "sum_sequential": want_seq[k],
                       "sum_fsum": math.fsum(src[pl]["params"][k] for pl in pls) if k.endswith("POTUsed") else want_seq[k],
                       "rel_diff": (got[k] - want_seq[k]) / want_seq[k] if want_seq[k] else 0.0,
                       "equal": got[k] == want_seq[k]} for k in PARS}
    r["pot_scale"] = got["dataPOTUsed"] / got["mcPOTUsed"]
    for k, v in r["params"].items():
        if k.endswith("POTUsed"):
            if abs(v["rel_diff"]) > 1e-15:
                fails.append(f"{P} {k} {v}")
        elif not v["equal"]:
            fails.append(f"{P} {k} {v}")
    mh = file_hashes(path)
    r["trees"] = {}
    for t in TREES:
        n_want = sum(src[pl]["entries"][t] for pl in pls)
        br = {b: {"merged": mh[t]["branches"][b], "concat": concat[P][t][b].hexdigest()} for b in mh[t]["branches"]}
        same = all(v["merged"] == v["concat"] for v in br.values()) and set(br) == set(concat[P][t])
        r["trees"][t] = {"entries": mh[t]["entries"], "entries_sum": n_want, "entries_equal": mh[t]["entries"] == n_want,
                         "branches_equal_concat": same, "branch_sha256": {b: v["merged"] for b, v in br.items()}}
        if mh[t]["entries"] != n_want or not same:
            fails.append(f"{P} tree {t}: entries {mh[t]['entries']} vs {n_want}, branches_equal {same}")
    if P == "ALL":
        eq = {t: mh[t] == cfs[t] for t in TREES}
        r["equals_production_cv_omnifile"] = {"trees": eq, "params": got == cfs_params, "reference": PD.PINS["cv_omnifile_cfs"]}
        if not all(eq.values()) or got != cfs_params:
            fails.append(f"ALL differs from the production CV omnifile: {eq}, params {got} vs {cfs_params}")

    # flux
    fpath = PD.flux_file(P)
    ff = ROOT.TFile.Open(fpath)
    h = ff.Get(FLUXH)
    nb = h.GetNbinsX()
    fl = np.array([h.GetBinContent(i) for i in range(1, nb + 1)])
    fe = np.array([h.GetBinError(i) for i in range(1, nb + 1)])
    f_pot_mc = ff.Get("POTUsed").GetVal()
    f_pot_d = ff.Get("DataPOTUsedForFluxWeighting").GetVal()
    tag = ff.Get("periodPlaylists").GetTitle()
    ff.Close()
    phi, err2, wd, wmc = [], [], [], []
    for pl in pls:
        fm = ROOT.TFile.Open(f"{PD.BASE_FLUX}/runEventLoopMC_{pl}.root")
        hm = fm.Get(FLUXH)
        phi.append([hm.GetBinContent(i) for i in range(1, nb + 1)])
        err2.append([hm.GetBinError(i) ** 2 for i in range(1, nb + 1)])
        wmc.append(fm.Get("POTUsed").GetVal())
        fd = ROOT.TFile.Open(f"{PD.BASE_FLUX}/runEventLoopData_{pl}.root")
        wd.append(fd.Get("POTUsed").GetVal())
    phi, err2, wd = np.array(phi), np.array(err2), np.array(wd)
    exp = (phi * wd[:, None]).sum(0) / wd.sum()
    exp_e = np.sqrt((err2 * wd[:, None] ** 2).sum(0)) / wd.sum()
    flux_pl_pot = {pl: {"flux_data_POTUsed": float(wd[i]), "omnifile_dataPOTUsed": src[pl]["params"]["dataPOTUsed"],
                        "equal": float(wd[i]) == src[pl]["params"]["dataPOTUsed"]} for i, pl in enumerate(pls)}
    r["flux"] = {"path": fpath, "sha256": PD.sha256(fpath), "periodPlaylists": tag,
                 "bins_m2_per_POT": fl.tolist(), "integral_m2_per_POT": float(fl.sum()),
                 "max_rel_diff_vs_numpy": float(np.max(np.abs(fl / exp - 1))),
                 "max_abs_diff_err_vs_numpy": float(np.max(np.abs(fe - exp_e))),
                 "DataPOTUsedForFluxWeighting": f_pot_d, "POTUsed": f_pot_mc,
                 "data_pot_equals_omnifile": f_pot_d == got["dataPOTUsed"],
                 "data_pot_rel_diff_vs_omnifile": f_pot_d / got["dataPOTUsed"] - 1,
                 "per_playlist_data_pot": flux_pl_pot}
    if tag != ",".join(pls) or r["flux"]["max_rel_diff_vs_numpy"] > 1e-14:
        fails.append(f"{P} flux mismatch {r['flux']['max_rel_diff_vs_numpy']} tag {tag}")
    if abs(r["flux"]["data_pot_rel_diff_vs_omnifile"]) > 1e-15:
        fails.append(f"{P} flux data POT {f_pot_d} vs omnifile {got['dataPOTUsed']}")
    if P == "ALL":
        fp = ROOT.TFile.Open(PD.PINS["flux_production"][0])
        hp = fp.Get(FLUXH)
        pv = np.array([hp.GetBinContent(i) for i in range(1, nb + 1)])
        pe = np.array([hp.GetBinError(i) for i in range(1, nb + 1)])
        r["flux"]["equals_production_flux"] = {
            "bins_equal": bool(np.array_equal(pv, fl)), "errors_equal": bool(np.array_equal(pe, fe)),
            "max_rel_diff": float(np.max(np.abs(fl / pv - 1))),
            "POTUsed_equal": fp.Get("POTUsed").GetVal() == f_pot_mc,
            "DataPOT_equal": fp.Get("DataPOTUsedForFluxWeighting").GetVal() == f_pot_d,
            "reference": PD.PINS["flux_production"]}
        fp.Close()
        e = r["flux"]["equals_production_flux"]
        if not (e["bins_equal"] and e["errors_equal"] and e["POTUsed_equal"] and e["DataPOT_equal"]):
            fails.append(f"ALL flux differs from production: {e}")
    vm = f"{PD.NS}/tmp/flux_viamain_{P}.root"
    if P in ("PA", "ALL"):
        fv = ROOT.TFile.Open(vm)
        hv = fv.Get(FLUXH)
        vv = np.array([hv.GetBinContent(i) for i in range(1, nb + 1)])
        ve = np.array([hv.GetBinError(i) for i in range(1, nb + 1)])
        r["flux"]["equals_combiner_main"] = {"path": vm, "bins_equal": bool(np.array_equal(vv, fl)),
                                             "errors_equal": bool(np.array_equal(ve, fe)),
                                             "POTUsed_equal": fv.Get("POTUsed").GetVal() == f_pot_mc,
                                             "DataPOT_equal": fv.Get("DataPOTUsedForFluxWeighting").GetVal() == f_pot_d}
        fv.Close()
        e = r["flux"]["equals_combiner_main"]
        if not (e["bins_equal"] and e["errors_equal"] and e["POTUsed_equal"] and e["DataPOT_equal"]):
            fails.append(f"{P} flux differs from the combiner main(): {e}")
    res["periods"][P] = r
    print(f"[verify] {P}: POT d={got['dataPOTUsed']:.6e} mc={got['mcPOTUsed']:.6e} scale={r['pot_scale']:.6f} "
          f"flux={fl.sum():.7e}", flush=True)

tot_d = sum(res["periods"][P]["params"]["dataPOTUsed"]["merged"] for P in ("PA", "PB", "PC"))
res["period_data_pot_share"] = {P: res["periods"][P]["params"]["dataPOTUsed"]["merged"] / tot_d for P in ("PA", "PB", "PC")}
res["period_mc_signal_share"] = {P: res["periods"][P]["trees"]["mc_signal_reco"]["entries"] /
                                 res["periods"]["ALL"]["trees"]["mc_signal_reco"]["entries"] for P in ("PA", "PB", "PC")}
res["source_params"] = src
res["fails"] = fails
res["verdict"] = "PASS" if not fails else "FAIL"
json.dump(res, open(out_json, "w"), indent=1)
print(json.dumps({"verdict": res["verdict"], "fails": fails, "data_pot_share": res["period_data_pot_share"],
                  "mc_signal_share": res["period_mc_signal_share"]}, indent=1))
sys.exit(0 if not fails else 1)
