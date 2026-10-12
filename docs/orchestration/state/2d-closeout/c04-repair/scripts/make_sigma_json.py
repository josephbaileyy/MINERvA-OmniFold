#!/usr/bin/env python3
"""Per-cell absolute sigma vectors of the repaired construction, in remote_reduce.json's cell order.

For the Fig. 1 re-make (the paper-tighten lane's repaired-operand check). Same objects as remote_reduce.json's
`sigma_abs`: universe = hSigma_universe_total of the rollup, boot_vl170 and ml = hStd2D of their files, read at
(pT bin, p_par bin) = cell + 1. Control: the same reader on the adopted rollup must reproduce remote_reduce's
universe vector, and boot/ml must reproduce theirs (the repair leaves those two unchanged).

  python make_sigma_json.py <remote_reduce.json> <repaired rollup .root> <adopted rollup .root> <out.json>
"""
import hashlib
import json
import os
import sys

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
D = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
BOOT = f"{D}/uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root"
ML = f"{D}/uq/seedscan_lgbm_ml/uq_covariance_ml.root"


def sha(p):
    return hashlib.sha256(open(os.path.realpath(p), "rb").read()).hexdigest()


def read(path, obj, cells):
    f = ROOT.TFile.Open(path)
    h = f.Get(obj)
    v = np.array([h.GetBinContent(pt + 1, pz + 1) for pt, pz in cells])
    f.Close()
    return v


rr_path, rep_path, adopt_path, out_path = sys.argv[1:5]
rr = json.load(open(rr_path))
cells = rr["cells"]
ref = {k: np.asarray(v, float) for k, v in rr["sigma_abs"].items()}
rep = {"universe": read(rep_path, "hSigma_universe_total", cells),
       "boot_vl170": read(BOOT, "hStd2D", cells), "ml": read(ML, "hStd2D", cells)}
ctl_u = read(adopt_path, "hSigma_universe_total", cells)
control = {
    "adopted_universe_vs_remote_reduce_bitwise": bool(np.array_equal(ctl_u, ref["universe"])),
    "adopted_universe_vs_remote_reduce_max_rel": float(np.max(np.abs(ctl_u / ref["universe"] - 1))),
    "boot_vl170_vs_remote_reduce_bitwise": bool(np.array_equal(rep["boot_vl170"], ref["boot_vl170"])),
    "ml_vs_remote_reduce_bitwise": bool(np.array_equal(rep["ml"], ref["ml"])),
}
out = {
    "what": "per-cell absolute sigma, C04+X01-repaired construction, 205 cells in remote_reduce.json order",
    "cells": cells,
    "sigma_abs": {k: [float(x) for x in v] for k, v in rep.items()},
    "sources": {"universe": {"path": rep_path, "object": "hSigma_universe_total", "sha256": sha(rep_path)},
                "boot_vl170": {"path": BOOT, "object": "hStd2D", "sha256": sha(BOOT)},
                "ml": {"path": ML, "object": "hStd2D", "sha256": sha(ML)},
                "cell_order": {"path": "docs/orchestration/state/next-preparation-20261009/two-d-path/operands/"
                                       "remote_reduce.json", "sha256": sha(rr_path)}},
    "control": control,
    "universe_ratio_repaired_over_adopted": {
        "median": float(np.median(rep["universe"] / ctl_u)), "min": float((rep["universe"] / ctl_u).min()),
        "max": float((rep["universe"] / ctl_u).max())},
}
json.dump(out, open(out_path, "w"), indent=1)
print(json.dumps(control, indent=1))
print(json.dumps(out["universe_ratio_repaired_over_adopted"]))
sys.exit(0 if all(v for k, v in control.items() if k.endswith("bitwise")) else 2)
