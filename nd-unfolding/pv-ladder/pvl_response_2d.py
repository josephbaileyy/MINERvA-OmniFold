#!/usr/bin/env python3
"""PV ladder, POST HOC and descriptive: pvl_departure.py's measures on PV-2D's 205 (p_T, p_parallel) cells, from the
committed PV-2D ratios and readouts (0 node-h). PV-2D's r is constant on each reported cell, so the truth-level
departure on a cell is r - 1 exactly.

Refuses unless every ratio file's sha256 is the one projections.json records, projections.json's is the one each
readout records, and each readout's cells are projections.json's reported cells in the same order.

MEASURES: arithmetic on committed files. CANNOT AUTHORIZE: any claim.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import pvl_departure as D  # noqa: E402
import pvl_lib as L  # noqa: E402

PV2D = _HERE.parents[1] / "2d-unfolding" / "pv2d"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to overwrite {a.out}")
    proj = PV2D / "ratios" / "projections.json"
    P = json.loads(proj.read_text())
    cells = np.asarray(P["reported_cells"])
    d = {}
    for v in D.VERTICES:
        f = PV2D / "ratios" / P["vertices"][v]["ratio_file"]
        if L.sha256_path(f) != P["vertices"][v]["ratio_sha256"]:
            raise SystemExit(f"[FAIL] {f}: sha256 differs from projections.json")
        d[v] = np.asarray(json.loads(f.read_text())["r"], float).ravel()[cells] - 1.0
    out = {"schema": "pvl-response-2d/1", "post_hoc": True, "min_departure": D.MIN_DEP,
           "inputs": {"projections_sha256": L.sha256_path(proj)},
           "code": {"pvl_response_2d.py": L.sha256_path(__file__), "pvl_departure.py": L.sha256_path(D.__file__)},
           "arms": {}}
    for arm in ("a", "ref"):
        path = PV2D / "readouts" / f"readout_{arm}.json"
        X = json.loads(path.read_text())
        if X["ratios_projection_sha256"] != out["inputs"]["projections_sha256"] or list(X["cells"]) != cells.tolist():
            raise SystemExit(f"[FAIL] {path.name}: made against another projections.json or cell order")
        out["inputs"][f"readout_{arm}_sha256"] = L.sha256_path(path)
        rec, _ = D.measures({v: X["vertices"][v]["shift"] for v in D.VERTICES}, np.asarray(X["envelope"]["h"]), d)
        out["arms"][arm] = rec
        hd = rec["h_over_D"]
        print(f"[pvl] L-2D ({arm}): D median {100 * rec['D']['median']:.2f} %; h/D median " +
              ", ".join(f"{k} {v['median']:.3f} ({v['n']})" for k, v in hd.items() if v) +
              f"; same-vertex signed response {rec['same_vertex_signed_response']['median']:.3f}; "
              f"h vertex = D vertex in {rec['h_vertex_is_D_vertex']} of 205")
        for v in D.VERTICES:
            x = rec["vertices"][v]
            print(f"[pvl]   {v}: response {x['response']['median']:.3f}, signed {x['signed_response']['median']:.3f}, "
                  f"same sign {x['same_sign']} of {x['n_cells_above_min']}")
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
