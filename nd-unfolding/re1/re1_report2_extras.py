#!/usr/bin/env python3
"""RE-1 report 2: the few numbers the review found missing, with their own provenance (arithmetic, no unfold).

    re1_report2_extras.py --cur3d CUR3D.root --p3 P3.root --eu E_U.root \
        --c5 P5C.npz --cur5d CUR5D.root --trunk z-cv.npz --npz5d of_inputs_5d.npz \
        --expect-{cur3d,p3,eu,c5,cur5d,trunk,npz5d}-sha256 S --out extras.json

* the 3D data total, ``hXSec3D.Integral("width")``, on the current product and on P3 (the note's 3.08e-38);
* the per-cell (pT, p||) scatter of the E_avail marginal against E_U on E_U's reported cells: the SD of
  ``hXSec2D / E_U`` (the note's ~4.4 %), with its median, on the current product and on P3;
* the 5D (c) - (a) movement in the adopted trunk's total sigma on its support, by ``re1_nd_movement``'s own
  ``pair`` (the declared readout gives (e) - (c) and (e) - (a) only).

MEASURES: descriptive numbers. CANNOT AUTHORIZE: a claim; DECISION-20260920 section 4's measurements travel with
any number in trunk sigma.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import re1_nd_movement as M  # noqa: E402

NAMES = ("cur3d", "p3", "eu", "c5", "cur5d", "trunk", "npz5d")


def th2(path: Path) -> np.ndarray:
    import ROOT
    f = ROOT.TFile.Open(str(path), "READ")
    h = f.Get("hXSec2D")
    a = np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY() + 1)] for i in range(1, h.GetNbinsX() + 1)])
    f.Close()
    return a


def total3d(path: Path) -> float:
    import ROOT
    f = ROOT.TFile.Open(str(path), "READ")
    v = float(f.Get("hXSec3D").Integral("width"))
    f.Close()
    return v


def scatter(marg: np.ndarray, eu: np.ndarray) -> dict:
    cells = eu > 0
    r = marg[cells] / eu[cells]
    return {"n_cells": int(cells.sum()), "sd_ratio": float(r.std(ddof=0)), "sd_ratio_ddof1": float(r.std(ddof=1)),
            "median_ratio": float(np.median(r)), "mean_ratio": float(r.mean())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    for k in NAMES:
        ap.add_argument(f"--{k}", type=Path, required=True)
        ap.add_argument(f"--expect-{k}-sha256", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    got = {k: M.sha256_path(getattr(a, k)) for k in NAMES}
    if any(got[k] != getattr(a, f"expect_{k}_sha256") for k in NAMES):
        print(f"input digests {got} differ from the expected ones", file=sys.stderr)
        return 4
    eu = th2(a.eu)
    out = {"schema": "re1-report2-extras/1", "inputs_sha256": got, "code_sha256": M.sha256_path(Path(__file__).resolve()),
           "total3d": {"current": total3d(a.cur3d), "p3": total3d(a.p3)},
           "marginal_vs_EU_scatter": {"current": scatter(th2(a.cur3d), eu), "p3": scatter(th2(a.p3), eu)}}
    shape = M.SHAPES[5]
    xc, mc = M.load_product(a.c5, shape, {"bkg_mode": "purity", "config": "deterministic", "data": True})
    if mc["input_npz_sha256"] != got["npz5d"]:
        raise RuntimeError("--c5 was not unfolded from --npz5d")
    xa = M.load_current(a.cur5d, 5, shape)
    e = np.load(a.npz5d, allow_pickle=True)
    vol = M.volumes([np.asarray(e[f"edges_{i}"], float) for i in range(int(e["nedges"]))])
    z = np.load(a.trunk, allow_pickle=False)
    rows = np.asarray(z["hRowIndex5D"], int)
    sig = np.full(int(np.prod(shape)), np.nan)
    sig[rows] = np.sqrt(np.diag(z["hCov_combined5d_total_uthrow"]))
    cells = np.flatnonzero((xa > 0) & (xc > 0))
    cells = cells[np.isin(cells, rows)]
    out["c_minus_a_5d_on_trunk_support"] = {"n_cells": int(cells.size),
                                            "trunk_central_equals_current": bool(np.array_equal(
                                                np.asarray(z["hXSecND_flat"], float), xa)),
                                            **M.pair(xc, xa, cells, vol, sig[cells])}
    a.out.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"total3d": out["total3d"], "scatter_sd": {k: v["sd_ratio"] for k, v in
                                                                 out["marginal_vs_EU_scatter"].items()}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
