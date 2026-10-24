#!/usr/bin/env python3
"""PV ladder: each rung's readout cell sets (DECLARATION.md §2.1), written by the pilot before any vertex run.

Per readout space ("fine", "EW", "J", "PTPZ") of the rung, the cells with positive recorded central value (the rung's
NC target for arm e) that meet s5p's support rule there: expected reco-level signal (w_reco, reco-passing rows) and
truth-selected weight (w_truth, truth-passing rows) both >= 1000, summed over the space's cells. For "PTPZ" the cells
are L-2D's 205 reported cells (PV-2D projections.json) where the projection is positive.

Refuses on the 5D npz unless the rule reproduces s5p's own sets: the 39 EW cells (all but EW11, EW36, EW37) and 109
J cells (contract amendment 1).

MEASURES: cell support. CANNOT AUTHORIZE: any verdict.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import pvl_lib as L  # noqa: E402

# readouts: the headline and secondary spaces (DECLARATION.md §2.1); nc: the extra spaces the NC is also read on
SPACES = {"L-EW": {"headline": "EW", "secondary": [], "nc": ["J"]}, "L-3D": {"headline": "fine", "secondary": ["J", "PTPZ"], "nc": []},
          "L-4D": {"headline": "fine", "secondary": ["J", "PTPZ"], "nc": []},
          "L-5D-PV": {"headline": "EW", "secondary": ["J", "PTPZ"], "nc": []}}
S5C_CONTRACT = _HERE.parents[1] / "docs" / "orchestration" / "state" / "s5c" / "contract.json"
PV2D_PROJECTIONS = _HERE.parents[1] / "2d-unfolding" / "pv2d" / "ratios" / "projections.json"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--config", type=Path, default=_HERE / "config.json")
    ap.add_argument("--rung", required=True, choices=sorted(L.RUNGS))
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to overwrite {a.out}")
    rc = json.loads(a.config.read_text())["rungs"][a.rung]
    for spec in (rc["npz"], rc["nc"]["e"]):
        if L.sha256_path(spec["path"]) != spec["sha256"]:
            raise SystemExit(f"[FAIL] {spec['path']}: sha256 differs from the config")
    z = np.load(rc["npz"]["path"], allow_pickle=True)
    names = L.npz_axes(z)
    inputs = {k: z[k] for k in ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco")}
    s = L.support(inputs, names)
    cv = L.integrated(np.load(rc["nc"]["e"]["path"], allow_pickle=True)["xsec_flat"], names)
    ptpz = set(json.loads(PV2D_PROJECTIONS.read_text())["reported_cells"])
    out = {"schema": "pvl-cells/1", "rung": a.rung, "axes": list(names), "support_min": L.SUPPORT_MIN,
           "headline": SPACES[a.rung]["headline"], "secondary": SPACES[a.rung]["secondary"],
           "nc_spaces": SPACES[a.rung].get("nc", []),
           "inputs": {"npz": rc["npz"], "cv": rc["nc"]["e"], "pv2d_projections_sha256": L.sha256_path(PV2D_PROJECTIONS)},
           "code": {"pvl_cells.py": L.sha256_path(__file__), "pvl_lib.py": L.sha256_path(L.__file__)}, "spaces": {}}
    for space in [SPACES[a.rung]["headline"]] + SPACES[a.rung]["secondary"] + SPACES[a.rung].get("nc", []):
        sig = L.readout_space(s["reco_signal"], names, space)
        tru = L.readout_space(s["truth_selected"], names, space)
        x = L.readout_space(cv, names, space)
        ok = (x > 0) & (sig >= L.SUPPORT_MIN) & (tru >= L.SUPPORT_MIN)
        if space == "PTPZ":
            ok = (x > 0) & np.isin(np.arange(x.size), sorted(ptpz))
        out["spaces"][space] = {"n_space": int(x.size), "n_cv_positive": int((x > 0).sum()),
                                "cells": [int(i) for i in np.flatnonzero(ok)]}
        print(f"[pvl] {a.rung} {space}: {int(ok.sum())} cells of {x.size} ({int((x > 0).sum())} with CV > 0)")
    if names == L.AXES5:
        ew, j = out["spaces"]["EW"]["cells"], out["spaces"]["J"]["cells"]
        j_s5c = sorted(json.loads(S5C_CONTRACT.read_text())["measurement"]["partition_J"]["supported_cells"])
        if ew != L.ew_headline().tolist() or j != j_s5c:
            raise SystemExit(f"[FAIL] the support rule gives {len(ew)} EW and {len(j)} J cells, not s5p's 39 and "
                             f"s5c's 109 supported J cells")
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
