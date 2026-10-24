#!/usr/bin/env python3
"""PV ladder, POST HOC and descriptive: pvl_departure.py's response on PV-2D's 205 (p_T, p_parallel) cells, from the
committed PV-2D ratios and readouts, as context for the EW cells. PV-2D's r is constant on each reported cell, so the
truth-level departure on a cell is r - 1 exactly; the response is |shift| / |r - 1| on cells with |r - 1| > 1 %, and
h / D with D = max_k |r_k - 1|.

MEASURES: arithmetic on committed files (0 node-h). CANNOT AUTHORIZE: any claim.
"""
import json
from pathlib import Path

import numpy as np

PV2D = Path(__file__).resolve().parents[2] / "2d-unfolding" / "pv2d"
VERTICES = ("genie_mec", "nuwro", "gibuu")
MIN_DEP = 0.01


def main():
    P = json.loads((PV2D / "ratios" / "projections.json").read_text())
    cells = np.asarray(P["reported_cells"])
    d = {v: np.asarray(json.loads((PV2D / "ratios" / P["vertices"][v]["ratio_file"]).read_text())["r"],
                       float).ravel()[cells] - 1.0 for v in VERTICES}
    D = np.max(np.abs(np.vstack([d[v] for v in VERTICES])), axis=0)
    for arm in ("a", "ref"):
        X = json.loads((PV2D / "readouts" / f"readout_{arm}.json").read_text())
        parts = []
        for v in VERTICES:
            s, m = np.abs(np.asarray(X["vertices"][v]["shift"])), np.abs(d[v]) > MIN_DEP
            parts.append(f"{v} response median {np.median(s[m] / np.abs(d[v][m])):.3f} on {int(m.sum())} cells")
        h, k = np.asarray(X["envelope"]["h"]), D > MIN_DEP
        print(f"[pvl] L-2D ({arm}): " + "; ".join(parts) + f"; D median {100 * np.median(D):.2f} %; "
              f"h/D median {np.median(h[k] / D[k]):.3f} on {int(k.sum())} cells")


if __name__ == "__main__":
    main()
