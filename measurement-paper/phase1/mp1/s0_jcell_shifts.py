#!/usr/bin/env python3
"""MP1-A S0: reco-level shifts of the 109 J cells for species-response passes against the k = 0 control.

For each pass, the weighted reco-level yield per reported J cell (signal rows of mc_signal_reco with sim_pass = 1,
weight w_reco, plus background rows of mc_background with sim_background_pass = 1, weight w_bkg) is compared with the
control's: rel_c = (N_pass,c - N_ctrl,c) / N_ctrl,c. The cell map is the s5p one, imported (fine grid, then the
partition-J coarse map over the s5c contract's supported cells: nd-unfolding/s5p_stage1_inspect.py). The
coordinates are the omnifile's reco (pT, p_||, E_avail, q3, W) in GeV. Rows outside the fine grid are counted.
This is a reco-level description of each pass, before any unfolding; it is not an unfolded J-cell number.

    python -I s0_jcell_shifts.py --repo <deploy root> --control zero.root --pass label=file.root [...] --out x.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import uproot

TREES = {"mc_signal_reco": ("sim", "sim_pz", "sim_eavail", "sim_q3", "sim_W", "sim_pass", "w_reco"),
         "mc_background": ("sim_background", "sim_background_pz", "sim_background_eavail", "sim_background_q3",
                           "sim_background_W", "sim_background_pass", "w_bkg")}


def yields(path: str, cell_of_fine: np.ndarray, n_cells: int, fine_index) -> dict:
    f = uproot.open(path)
    out = {"total": np.zeros(n_cells), "rows_passing": 0, "rows_outside_grid": 0, "rows_unreported_cell": 0}
    for tree, br in TREES.items():
        a = f[tree].arrays(list(br), library="np")
        sel = a[br[5]].astype(int) == 1
        coords = np.stack([a[b][sel].astype(float) for b in br[:5]], axis=1)
        w = a[br[6]][sel].astype(float)
        fi = fine_index(coords)
        inside = fi >= 0
        cell = np.full(fi.shape, -1)
        cell[inside] = cell_of_fine[fi[inside]]
        rep = cell >= 0
        y = np.bincount(cell[rep], weights=w[rep], minlength=n_cells)
        out[tree] = y
        out["total"] = out["total"] + y
        out["rows_passing"] += int(sel.sum())
        out["rows_outside_grid"] += int((~inside).sum())
        out["rows_unreported_cell"] += int((inside & ~rep).sum())
    return out


def summary(rel: np.ndarray) -> dict:
    a = np.abs(rel)
    return {"median_abs": float(np.median(a)), "max_abs": float(a.max()), "max_cell": int(np.argmax(a)),
            "n_abs_over_1pct": int(np.sum(a > 0.01)), "n_abs_over_5pct": int(np.sum(a > 0.05)),
            "min": float(rel.min()), "max": float(rel.max())}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", required=True, type=Path, help="root holding nd-unfolding/ and docs/ (the deploy)")
    ap.add_argument("--control", required=True)
    ap.add_argument("--pass", dest="passes", action="append", required=True, help="label=path")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    sys.path.insert(0, str(a.repo / "nd-unfolding"))
    import s5p_stage1_inspect as s1  # noqa: E402  (the s5p fine grid and partition-J map)
    contract = json.loads((a.repo / "docs/orchestration/state/s5c/contract.json").read_text())
    supported = contract["measurement"]["partition_J"]["supported_cells"]
    cmap, n_cells = s1.coarse_map(s1.J_EDGES, supported)
    ctrl = yields(a.control, cmap, n_cells, s1.fine_index)
    res = {"control": a.control, "n_cells": n_cells, "control_rows": {k: ctrl[k] for k in
           ("rows_passing", "rows_outside_grid", "rows_unreported_cell")},
           "control_total_yield": float(ctrl["total"].sum()), "passes": {}}
    if np.any(ctrl["total"] <= 0):
        print("refusing: a reported cell has no control yield", file=sys.stderr)
        return 2
    for spec in a.passes:
        label, path = spec.split("=", 1)
        y = yields(path, cmap, n_cells, s1.fine_index)
        rel = (y["total"] - ctrl["total"]) / ctrl["total"]
        rel_sig = (y["mc_signal_reco"] - ctrl["mc_signal_reco"]) / np.maximum(ctrl["mc_signal_reco"], 1e-300)
        res["passes"][label] = {
            "file": path, "rows": {k: y[k] for k in ("rows_passing", "rows_outside_grid", "rows_unreported_cell")},
            "total_yield_rel": float(y["total"].sum() / ctrl["total"].sum() - 1.0),
            "cells_total": summary(rel), "cells_signal_only": summary(rel_sig),
            "rel_per_cell": [float(v) for v in rel]}
    text = json.dumps(res, indent=1)
    Path(a.out).write_text(text + "\n")
    for label, p in res["passes"].items():
        c = p["cells_total"]
        print(f"{label:28s} median|rel|={c['median_abs']:.4%} max|rel|={c['max_abs']:.4%} (cell {c['max_cell']}) "
              f"range=[{c['min']:+.4%},{c['max']:+.4%}] n>1%={c['n_abs_over_1pct']} n>5%={c['n_abs_over_5pct']} "
              f"total={p['total_yield_rel']:+.4%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
