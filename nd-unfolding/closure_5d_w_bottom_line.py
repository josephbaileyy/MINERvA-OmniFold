#!/usr/bin/env python3
"""Score the 5D injected-W closure (PREREG-20261012-5d-injected-w-closure.md).

Reads two driver outputs from the same job:
  --injected   unfold_nd_omnifold_unbinned.py --closure --closure-reweight-axis W ...
  --null       the same command without --closure-reweight-axis (plain closure).
The null run's hClosureRefND is the nominal (un-reweighted) MC truth cross section, the
`nom` operand of the bottom-line statistic; the injected run supplies `unf` (hXSecND) and
`ref` (hClosureRefND, the bump-reweighted truth).

The primary statistic is NOT re-implemented here: it is `bottom_line_ratio` from
2d-unfolding/uq/bottom_line_test.py, the instrument behind the 2D and 3D injected-feature
recoveries, applied to the W-marginal projection. Projections use the driver's own
`project_axis` / `project_marginal` and edges.

Rules (frozen in the plan before submission):
  positive control  injected truth-pass mean weight factor >= 1.01, else INVALID
  primary           W-marginal bottom-line ratio < 0.20  -> PASS, else FAIL
  secondary         joint (E_avail, W) unfolded/reference ratios, descriptive only
"""
import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

import numpy as np
import ROOT

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

import unfold_nd_omnifold_unbinned as drv  # noqa: E402
from xsec_nd import project_axis, project_marginal  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "bottom_line_test", REPO / "2d-unfolding" / "uq" / "bottom_line_test.py")
blt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(blt)

AXES = ["eavail", "q3", "W"]
POSITIVE_CONTROL_MIN = 1.01
TOL = 0.20


def edges5d():
    return [list(drv.u2d.PT_EDGES), list(drv.u2d.PZ_EDGES)] + [drv.EXTRA_AXES[a]["edges"] for a in AXES]


def read_flat(path, name, shape):
    f = ROOT.TFile.Open(str(path))
    if not f or f.IsZombie():
        sys.exit(f"[FAIL] cannot open {path}")
    h = f.Get(name)
    if not h:
        sys.exit(f"[FAIL] {name} missing in {path}")
    v = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())], dtype=float)
    f.Close()
    if v.size != int(np.prod(shape)):
        sys.exit(f"[FAIL] {name} has {v.size} bins, expected {int(np.prod(shape))}")
    return v.reshape(shape, order="C")


def injected_mean_factor(log_path):
    vals = re.findall(r"injected mean factor=([0-9.eE+-]+)", Path(log_path).read_text())
    if len(vals) != 1:
        sys.exit(f"[FAIL] expected one 'injected mean factor' line in {log_path}, found {len(vals)}")
    return float(vals[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--injected", required=True)
    ap.add_argument("--injected-log", required=True)
    ap.add_argument("--null", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    edges = edges5d()
    shape = tuple(len(e) - 1 for e in edges)
    unf = read_flat(a.injected, "hXSecND_flat", shape)
    ref = read_flat(a.injected, "hClosureRefND_flat", shape)
    nom = read_flat(a.null, "hClosureRefND_flat", shape)
    null_unf = read_flat(a.null, "hXSecND_flat", shape)

    def per_bin(u, r):
        m = r > 0
        q = u[m] / r[m]
        return dict(median=float(np.median(q)), std=float(np.std(q)),
                    max_abs_dev=float(np.max(np.abs(q - 1))), n=int(m.sum()))

    wi = 2 + AXES.index("W")
    w_edges, w_unf = project_axis(unf, edges, wi)
    _, w_ref = project_axis(ref, edges, wi)
    _, w_nom = project_axis(nom, edges, wi)
    w_unf, w_ref, w_nom = (np.asarray(x, dtype=float) for x in (w_unf, w_ref, w_nom))

    factor = injected_mean_factor(a.injected_log)
    control_ok = factor >= POSITIVE_CONTROL_MIN
    bl = blt.bottom_line_ratio(w_unf, w_ref, w_nom, TOL)

    keep = [2 + AXES.index("eavail"), wi]
    drop = [i for i in range(len(edges)) if i not in keep]
    ew_unf = project_marginal(unf, edges, drop_axes=drop)
    ew_ref = project_marginal(ref, edges, drop_axes=drop)
    ew_nom = project_marginal(nom, edges, drop_axes=drop)
    ew_ratio = np.full(ew_ref.shape, np.nan)
    np.divide(ew_unf, ew_ref, out=ew_ratio, where=ew_ref > 0)
    ew_inj = np.full(ew_ref.shape, np.nan)
    np.divide(ew_ref, ew_nom, out=ew_inj, where=ew_nom > 0)
    finite = np.isfinite(ew_ratio)

    if not control_ok:
        verdict = "INVALID"
    else:
        verdict = bl["verdict"]

    out = {
        "plan": "docs/orchestration/PREREG-20261012-5d-injected-w-closure.md",
        "inputs": {"injected": a.injected, "null": a.null, "injected_log": a.injected_log},
        "positive_control": {"injected_mean_factor": factor, "min": POSITIVE_CONTROL_MIN,
                             "ok": bool(control_ok)},
        "w_edges": [float(x) for x in w_edges],
        "w_marginal": {
            "injected_deviation_per_bin": [float(x) for x in np.where(w_nom > 0, w_ref / np.where(w_nom > 0, w_nom, 1) - 1, np.nan)],
            "unfolded_over_reference_per_bin": [float(x) for x in np.where(w_ref > 0, w_unf / np.where(w_ref > 0, w_ref, 1), np.nan)],
        },
        "primary_bottom_line": {k: (float(v) if isinstance(v, (float, np.floating)) else v)
                                for k, v in bl.items() if k not in ("mask", "feature_mask")},
        "primary_feature_bins": [int(i) for i in np.flatnonzero(bl["feature_mask"])],
        "per_bin_5d_injected": per_bin(unf, ref),
        "per_bin_5d_null": per_bin(null_unf, nom),
        "secondary_eavail_w": {
            "n_cells": int(ew_ratio.size), "n_finite": int(finite.sum()),
            "median_ratio": float(np.nanmedian(ew_ratio)),
            "max_abs_dev": float(np.nanmax(np.abs(ew_ratio - 1))),
            "ratio_map": [[(float(x) if np.isfinite(x) else None) for x in row] for row in ew_ratio],
            "injected_map": [[(float(x) if np.isfinite(x) else None) for x in row] for row in ew_inj],
            "highest_w_column": [(float(x) if np.isfinite(x) else None) for x in ew_ratio[:, -1]],
        },
        "verdict": verdict,
    }
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("positive_control", "primary_bottom_line",
                                          "per_bin_5d_injected", "per_bin_5d_null", "verdict")},
                     indent=1))


if __name__ == "__main__":
    main()
