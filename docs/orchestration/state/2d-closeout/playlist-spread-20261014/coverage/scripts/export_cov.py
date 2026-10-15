"""Export the quoted 2D covariance (VL175) and the per-universe unfolded outputs to one scratch .npz.

Usage: python -I export_cov.py <out.npz> <out_controls.json>

Reads (paths fixed below, sha256 re-measured and recorded):
  - VL175 repaired rollup  uq_universe_covariance_c04x01.root  (per-band blocks, normalization, hCov_combined)
  - ML covariance          uq_covariance_ml.root : hCov2D_reported
  - central E_U            2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root : hXSec2D
  - per-universe outputs   uq/universe_sweep_fluxfix/2d_xsec_MEFHC_5iter_lgbm_uni_full_<BAND>_<IDX>.root : hXSec2D
  - MINOS rescale          c04 build minos_rescaled.npz : x_rescaled (2 x 205)  (KI 96 repair of Muon_Energy_MINOS)
  - Flux universe weights  first 100 'Flux' rows of the nu-e+IMD constraint file (as the C04 build)
Control: block sum (hCov_combined + ML) per-cell median must reproduce VL175's 6.0898 %.
"""
import glob
import hashlib
import json
import os
import re
import sys

import numpy as np
import ROOT

out_npz, out_json = sys.argv[1], sys.argv[2]
REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
NS = "/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012"
P = {
    "rollup_vl175": f"{NS}/build/uq_universe_covariance_c04x01.root",
    "ml": f"{REPO}/uq/seedscan_lgbm_ml/uq_covariance_ml.root",
    "E_U": f"{REPO}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root",
    "minos_rescaled": f"{NS}/build/minos_rescaled.npz",
    "constraint": f"{REPO}/../MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt",
}
EXPECT = {
    "rollup_vl175": "da92c5d2567647e8613bb3a6522176dbd9a287970082b45ac9e83e24684b1948",
    "ml": "3b6b48ec89207ae29dc7bb0ddc5a41836c359c4805877d663731694b828d5db9",
    "E_U": "4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c",
    "minos_rescaled": "8912376ef2a6cfce8bed515cc945d9d5778cf5c838154a685435c3c7ce25416d",
    "constraint": "e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2",
}
SWEEP = f"{REPO}/uq/universe_sweep_fluxfix"
PT_EDGES = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ_EDGES = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])


def sha(p):
    h = hashlib.sha256()
    with open(os.path.realpath(p), "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def th2(h):
    return np.array([[h.GetBinContent(i + 1, j + 1) for j in range(h.GetNbinsY())] for i in range(h.GetNbinsX())])


def edges(ax):
    return np.array([ax.GetBinLowEdge(i) for i in range(1, ax.GetNbins() + 2)])


ctrl = {"inputs": {}}
for k, p in P.items():
    s = sha(p)
    ctrl["inputs"][k] = {"path": os.path.realpath(p), "sha256": s, "expected": EXPECT[k], "ok": s == EXPECT[k]}
    if s != EXPECT[k]:
        sys.exit(f"[FAIL] sha256 mismatch for {p}")

f = ROOT.TFile.Open(P["E_U"])
h = f.Get("hXSec2D")
assert np.allclose(edges(h.GetXaxis()), PT_EDGES) and np.allclose(edges(h.GetYaxis()), PZ_EDGES)
EU = th2(h)
f.Close()

f = ROOT.TFile.Open(P["rollup_vl175"])
cells_h = f.Get("hReportedCells")
cellmask = th2(cells_h) == 1.0
cells = np.flatnonzero(cellmask.ravel(order="C"))
assert np.array_equal(cells, np.flatnonzero((EU > 0).ravel(order="C"))), "reported set != E_U > 0"
blocks = {}
for k in f.GetListOfKeys():
    n = k.GetName()
    if n.startswith("hCov_"):
        blocks[n] = th2(f.Get(n))
f.Close()
f = ROOT.TFile.Open(P["ml"])
blocks["ML"] = th2(f.Get("hCov2D_reported"))
f.Close()

xrep = EU.ravel(order="C")[cells]
bs = blocks["hCov_combined"] + blocks["ML"]
med = 100 * float(np.median(np.sqrt(np.diag(bs)) / xrep))
ctrl["control_block_sum_median_pct"] = {"measured": med, "VL175": 6.0898, "ok": bool(abs(med - 6.0898) < 5e-4)}

# per-universe unfolded outputs
RX = re.compile(r"2d_xsec_MEFHC_5iter_lgbm_uni_full_(?P<b>.+)_(?P<i>\d+)\.root$")
uni = {}
for p in sorted(glob.glob(f"{SWEEP}/2d_xsec_MEFHC_5iter_lgbm_uni_full_*.root")):
    m = RX.search(os.path.basename(p))
    if not m:
        continue
    f = ROOT.TFile.Open(p)
    x = th2(f.Get("hXSec2D")).ravel(order="C")[cells]
    f.Close()
    uni.setdefault("full_" + m.group("b"), {})[int(m.group("i"))] = x
mr = np.load(P["minos_rescaled"])
uni["full_Muon_Energy_MINOS"] = {0: mr["x_rescaled"][0], 1: mr["x_rescaled"][1]}
cons = []
with open(P["constraint"]) as fc:
    for line in fc:
        t = line.split()
        if len(t) == 3 and t[0] == "Flux":
            cons.append((int(t[1]), float(t[2])))
wflux = np.array([v for i, v in sorted(cons) if i < 100])
ctrl["flux_weights"] = {"n": int(wflux.size), "sum": float(wflux.sum()), "n_eff": float(wflux.sum() ** 2 / (wflux ** 2).sum())}

# controls: recompute two blocks from the universes
def cov_mc(X, w=None):
    w = np.ones(len(X)) if w is None else w
    mu = (w[:, None] * X).sum(0) / w.sum()
    Z = X - mu
    return (Z.T * w) @ Z / w.sum()


XF = np.stack([uni["full_Flux"][i] for i in range(100)])
cf = cov_mc(XF, wflux)
ctrl["control_flux_block_rel_maxdiff"] = float(np.abs(cf - blocks["hCov_universe_full_Flux"]).max() / np.abs(cf).max())
XM = np.stack([uni["full_Muon_Energy_MINOS"][i] for i in range(2)])
cm = cov_mc(XM)
ctrl["control_minos_block_rel_maxdiff"] = float(np.abs(cm - blocks["hCov_universe_full_Muon_Energy_MINOS"]).max() / np.abs(cm).max())
ctrl["n_universe_bands"] = len(uni)
ctrl["n_universe_outputs"] = int(sum(len(v) for v in uni.values()))
ctrl["n_cov_blocks"] = len(blocks)
ctrl["n_reported"] = int(cells.size)

save = {"EU": EU, "cells": cells, "wflux": wflux}
for k, v in blocks.items():
    save["cov__" + k] = v
for b, d in uni.items():
    save["uni__" + b] = np.stack([d[i] for i in sorted(d)])
np.savez(out_npz, **save)
json.dump(ctrl, open(out_json, "w"), indent=1)
print(json.dumps({k: v for k, v in ctrl.items() if k != "inputs"}, indent=1))
