#!/usr/bin/env python3
"""The fine-grid convergence ratios of condition (i): ||D_M1 / f_mid|| / ||D_F2 / f_coarse|| per generator.

D_M1 is the noise-free asimov at the fine-ratio null truth minus that at the twofold-merged ("mid") truth, and D_F2
the fine-ratio minus the coarse-ratio asimov, each on the 109 supported J cells (s5p pair-difference products,
stage3/m1/fine-minus-mid-<g>.npz and stage3/f2/delta-<g>.npz; fields D_J and f_B_mean, where f_B_mean is the
reference asimov of each difference). The norm is the L2 norm of the per-cell RELATIVE differences, each relative to
its own reference. This reproduces the recorded ratios (campaign-state.json m1 row: 0.76, 0.86, 0.54, 0.50; the
article's 0.50-0.86). The raw (unweighted) L2 ratio does not (0.78, 0.58, 0.35, 0.50), which is why the article's
earlier "unweighted (L2) norm" was corrected (PRD release audit ea939701, J09/G6).

MEASURES: nothing new. CANNOT AUTHORIZE: any statement about convergence below the fine grid.

  python3 m1_f2_norm_ratio.py DIR      # DIR holds delta-<g>.npz and fine-minus-mid-<g>.npz for the four generators
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

GENERATORS = ("genie_cv", "genie_mec", "nuwro_cv", "gibuu_cv")


def ratios(d: Path) -> dict:
    out = {}
    for g in GENERATORS:
        m1, f2 = np.load(d / f"fine-minus-mid-{g}.npz"), np.load(d / f"delta-{g}.npz")
        rel = np.linalg.norm(m1["D_J"] / m1["f_B_mean"]) / np.linalg.norm(f2["D_J"] / f2["f_B_mean"])
        raw = np.linalg.norm(m1["D_J"]) / np.linalg.norm(f2["D_J"])
        out[g] = {"relative_L2": float(rel), "raw_L2": float(raw)}
    return out


def main(argv=None) -> int:
    d = Path((argv or sys.argv[1:])[0])
    r = ratios(d)
    rel = [v["relative_L2"] for v in r.values()]
    print(json.dumps({"per_generator": r, "relative_L2_range": [min(rel), max(rel)]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
