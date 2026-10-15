#!/usr/bin/env python3
"""Synthetic plumbing smoke for analyze_p1.py (login node; no unfold, no real replica).

  python smoke_analyze_p1.py --work DIR --p1-sha SHA --report SMOKE.json [--xr-dir DIR]

Builds fake outputs in the analyze_p1 layout: hXSec2D = E_U x (1 + noise) with known per-arm scales
(fixed 1.0, joint 1.03 x the fixed noise plus a small independent part, bkg 0.2 x independent noise), each
with the provenance records the gates read. The unit output carries XR-L0's own hXSec2D. Then runs
analyze_p1 on four trees: (a) complete -> arms OK, b == 1 PASS, ratio medians near 1.03 and 0.2;
(b) one fixed replica missing -> fixed INCONCLUSIVE and both ratios INCONCLUSIVE;
(c) one joint replica with --seed 43 -> joint INCONCLUSIVE; (d) unit hXSec2D scaled by 1 + 1e-6 -> b == 1 FAIL.
"""
import argparse
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


AN = load("analyze_p1", HERE / "analyze_p1.py")


def write(path, src, x_fn, rc, sha, p1s=None):
    import ROOT
    f = ROOT.TFile.Open(str(src))
    h = f.Get("hXSec2D").Clone("hXSec2D")
    h.SetDirectory(0)
    f.Close()
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    x = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(ny)] for i in range(nx)])
    y = x_fn(x)
    for i in range(nx):
        for j in range(ny):
            h.SetBinContent(i + 1, j + 1, float(y[i, j]))
    path.parent.mkdir(parents=True, exist_ok=True)
    g = ROOT.TFile.Open(str(path), "RECREATE")
    h.Write()
    ROOT.TNamed("runConfig", json.dumps(rc, sort_keys=True)).Write()
    ROOT.TNamed("driverSha256", sha).Write()
    if p1s is not None:
        ROOT.TNamed("p1Streams", json.dumps(p1s, sort_keys=True)).Write()
    g.Close()


def build(out, p1_sha, n=20, drop=None, badseed=None, unit_scale=1.0):
    rng = np.random.default_rng(12345)
    base = {"bkg_mode": "purity", "estimator": "lgbm", "iters": 5, "use_weights": True, "universe": None,
            "closure": False, "seed": 42, "omnifile": "OMNI", "mcfile": "FLUX"}
    for k in range(1, n + 1):
        ef, ej, eb = (rng.standard_normal((14, 16)) for _ in range(3))
        noise = {"fixed": 0.01 * ef, "joint": 0.01 * 1.03 * (ef + 0.1 * ej) / np.sqrt(1.01), "bkg": 0.002 * eb}
        for arm, streams in AN.ARMS.items():
            if drop == (arm, k):
                continue
            rc = dict(base, bootstrap_seed=k, bootstrap_streams=streams)
            if arm != "fixed":
                rc["unit_factors"] = False
            if badseed == (arm, k):
                rc["seed"] = 43
            write(AN.replica_path(out, arm, k), AN.EU_DEFAULT, lambda x, e=noise[arm]: x * (1 + e), rc,
                  AN.PROD_SHA if arm == "fixed" else p1_sha,
                  None if arm == "fixed" else {"bootstrap_seed": k, "streams": streams})
    rc = dict(base, bootstrap_seed=1, bootstrap_streams="three", unit_factors=True)
    write(AN.unit_path(out), AN.L0_DEFAULT, lambda x: x * unit_scale, rc, p1_sha,
          {"bootstrap_seed": 1, "streams": "three"})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", required=True)
    ap.add_argument("--p1-sha", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--xr-dir", default=str(AN.XR_DIR_DEFAULT))
    a = ap.parse_args()
    cases = {"a_complete": {}, "b_missing_fixed_boot5": {"drop": ("fixed", 5)},
             "c_joint_boot3_seed43": {"badseed": ("joint", 3)}, "d_unit_scaled_1e-6": {"unit_scale": 1 + 1e-6}}
    rep = {}
    for name, kw in cases.items():
        out = Path(a.work, name)
        if out.exists():
            shutil.rmtree(out)
        build(out, a.p1_sha, **kw)
        rj = Path(a.work, f"{name}.json")
        AN.main(["--out-root", str(out), "--result", str(rj), "--p1-sha", a.p1_sha, "--xr-dir", a.xr_dir])
        r = json.loads(rj.read_text())
        rep[name] = {"arms": {k: v["status"] for k, v in r["arms"].items()},
                     "ratios": {k: {kk: v.get(kk) for kk in ("status", "median", "median_jackknife_se")}
                                for k, v in r["ratios"].items()},
                     "b_eq_1": r["b_eq_1"]["verdict"],
                     "b_eq_1_max_rel": r["b_eq_1"].get("xr_compare", {}).get("max_rel_diff_cells"),
                     "n_cells": r["n_cells"], "cells_equal_E_C": r["cells_equal_E_C_reported_globalid"]}
    ok = (rep["a_complete"]["b_eq_1"] == "PASS" and set(rep["a_complete"]["arms"].values()) == {"OK"}
          and abs(rep["a_complete"]["ratios"]["sigma_joint_over_sigma_fixed"]["median"] - 1.03) < 0.03
          and abs(rep["a_complete"]["ratios"]["sigma_bkg_over_sigma_fixed"]["median"] - 0.2) < 0.05
          and rep["b_missing_fixed_boot5"]["arms"]["fixed"] == "INCONCLUSIVE"
          and rep["b_missing_fixed_boot5"]["ratios"]["sigma_joint_over_sigma_fixed"]["status"] == "INCONCLUSIVE"
          and rep["c_joint_boot3_seed43"]["arms"]["joint"] == "INCONCLUSIVE"
          and rep["c_joint_boot3_seed43"]["arms"]["fixed"] == "OK"
          and rep["d_unit_scaled_1e-6"]["b_eq_1"] == "FAIL")
    rep["PASS"] = bool(ok)
    Path(a.report).write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    print(json.dumps(rep, indent=1))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
