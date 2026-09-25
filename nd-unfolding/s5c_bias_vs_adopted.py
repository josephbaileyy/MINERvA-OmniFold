#!/usr/bin/env python3
"""Size the nominal-truth purity-background closure bias against the adopted trunk's quoted total
uncertainty, cell by cell, on the (E_avail, W) projection.

Reads the D1 development summary (mean relative residual and its SE per functional EW0..EW41) and a
projection product carrying ``hCV_marginal`` and ``hCov_proj_eavail_W`` (the adopted projection
``835828bf...`` or its reproduction). Rows are the projector's destination order, which equals the
evaluator's EW order (``hRowIndex`` is the identity over 42 cells; checked).

MEASURES: |bias| / sigma_adopted per cell. CANNOT AUTHORIZE: a real-data bias (the development bias
is at nominal truth with MC background equal to nature), or any change to the adopted product.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--d1-summary", type=Path, required=True)
    ap.add_argument("--projection", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    import ROOT

    f = ROOT.TFile.Open(str(a.projection), "READ")
    h, c, r = f.Get("hCV_marginal"), f.Get("hCov_proj_eavail_W"), f.Get("hRowIndex")
    n = h.GetNbinsX()
    rows = [int(r.GetBinContent(i + 1)) for i in range(r.GetNbinsX())]
    if rows != list(range(n)):
        raise SystemExit(f"hRowIndex is not the identity over {n} cells")
    cv = np.array([h.GetBinContent(i + 1) for i in range(n)])
    sig = np.sqrt(np.array([c.GetBinContent(i + 1, i + 1) for i in range(n)])) / cv
    d1 = json.loads(a.d1_summary.read_text())
    names, g = d1["functional_names"], d1["groups"]["split_F2"]
    cells = []
    for i in range(n):
        k = names.index(f"EW{i}")
        b, se = g["mean_rel"][k], g["se_rel"][k]
        cells.append({"cell": f"EW{i}", "eavail_bin": i // 6, "W_bin": i % 6, "bias_pct": 100 * b, "se_pct": 100 * se,
                      "sigma_adopted_pct": 100 * float(sig[i]), "abs_bias_over_sigma_adopted": abs(b) / float(sig[i])})
    ratio = np.array([x["abs_bias_over_sigma_adopted"] for x in cells])
    sha = hashlib.sha256(a.projection.read_bytes()).hexdigest()
    out = {"schema": "s5c-bias-vs-adopted/1", "projection": str(a.projection), "projection_sha256": sha,
           "d1_summary": str(a.d1_summary), "group": "split_F2", "cells": cells,
           "summary": {"max_ratio": float(ratio.max()), "argmax": cells[int(ratio.argmax())]["cell"],
                       "n_ratio_above_0.5": int(np.sum(ratio > 0.5)), "median_ratio": float(np.median(ratio))}}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["summary"]))
    for x in cells:
        if x["W_bin"] == 5 or x["abs_bias_over_sigma_adopted"] > 0.5:
            print(f"{x['cell']:>5} bias {x['bias_pct']:+.2f}% sigma_adopted {x['sigma_adopted_pct']:.2f}% ratio {x['abs_bias_over_sigma_adopted']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
