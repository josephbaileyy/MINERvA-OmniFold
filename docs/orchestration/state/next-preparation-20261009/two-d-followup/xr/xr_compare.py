#!/usr/bin/env python3
"""XR comparisons: frozen 1e-8 reproduction criterion on the 205 reported cells and their integral.

    xr_compare.py --outroot OUTROOT --out RESULT.json [--refs-dir DIR]

For each comparison in ``manifest/runs.json`` (and its negative control) it uses the newest
complete attempt of the new run (its receipt must be ``complete``, name that run, cite the
outroot's own ``admission.json`` by path and sha256, and its output digest must match the receipt)
and the reference: a frozen product from ``manifest/references.json`` (its sha256 must
match) or another XR run's output. ``--refs-dir`` replaces the reference products' directory
(tests only); the digests are still enforced.

Verdict per comparison:
* PASS: identical reported-cell sets (hXSec2D > 0, paper GlobalID) equal to the frozen 205, and
  max |x_new / x_ref - 1| <= 1e-8 over every cell and over the area-weighted integral;
* FAIL: the same cell sets, and the maximum exceeds 1e-8. The maximum, the integral difference and
  every exceeding cell (GlobalID, relative difference) are reported;
* INCONCLUSIVE: a missing or incomplete run, a receipt or digest mismatch, different histogram
  axes (bin counts or edges), or different cell sets.
A control expected to differ is MET when its verdict is FAIL.

Reads small ROOT products only (PyROOT); writes one JSON.
"""

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOL = 1e-8


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    import ROOT
    import numpy as np
    f = ROOT.TFile.Open(str(path))
    h = f.Get("hXSec2D")
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    x = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(ny)] for i in range(nx)])
    w = np.array([[h.GetXaxis().GetBinWidth(i + 1) * h.GetYaxis().GetBinWidth(j + 1) for j in range(ny)]
                  for i in range(nx)])
    edges = ([h.GetXaxis().GetBinLowEdge(i + 1) for i in range(nx + 1)],
             [h.GetYaxis().GetBinLowEdge(j + 1) for j in range(ny + 1)])
    f.Close()
    return x, w, edges


def newest_complete(outroot, run):
    best = None
    adm_path = Path(outroot, "admission.json")
    adm_sha = sha(adm_path) if adm_path.is_file() else None
    for d in sorted(Path(outroot, run).glob("a*"), key=lambda d: int(d.name[1:]) if d.name[1:].isdigit() else -1):
        rec = d / "receipt.json"
        if rec.is_file() and rec.stat().st_size:
            r = json.loads(rec.read_text())
            if r.get("status") == "complete":
                best = (r, d)
    if best is None:
        return None, f"no complete attempt of {run}"
    r, d = best
    if r.get("run") != run or r.get("admission", {}).get("sha256") != adm_sha \
            or Path(r.get("admission", {}).get("path", "")) != adm_path.resolve():
        return None, f"{run}: the receipt names another run or admission than {adm_path}"
    out = Path(r["output"]["path"])
    if not out.is_file() or sha(out) != r["output"]["sha256"]:
        return None, f"{run}: output missing or differs from its receipt digest"
    return {"path": str(out), "sha256": r["output"]["sha256"], "attempt": r["attempt"]}, None


def compare(new, ref, cells):
    import numpy as np
    xn, w, en = read(new)
    xr, _, er = read(ref)
    if xn.shape != xr.shape or en != er:
        return {"verdict": "INCONCLUSIVE", "why": "histogram axes differ", "shape_new": list(xn.shape),
                "shape_ref": list(xr.shape)}
    gid = lambda x: [int(i * 16 + j) for i, j in np.argwhere(x > 0)]
    if gid(xn) != cells or gid(xr) != cells:
        return {"verdict": "INCONCLUSIVE", "why": "reported-cell sets differ from the frozen 205",
                "n_new": len(gid(xn)), "n_ref": len(gid(xr))}
    m = xr > 0
    rel = np.abs(xn[m] / xr[m] - 1)
    integ_n, integ_r = float(np.sum(xn[m] * w[m])), float(np.sum(xr[m] * w[m]))
    integ = abs(integ_n / integ_r - 1)
    ids = np.array(cells)
    over = [{"globalid": int(g), "rel_diff": float(r)} for g, r in zip(ids, rel) if r > TOL]
    mx = max(float(rel.max()), integ)
    return {"verdict": "PASS" if mx <= TOL else "FAIL", "max_rel_diff_cells": float(rel.max()),
            "argmax_globalid": int(ids[int(rel.argmax())]), "median_rel_diff_cells": float(np.median(rel)),
            "integral_rel_diff": integ, "n_cells": int(m.sum()), "n_cells_over_tol": len(over),
            "cells_over_tol": sorted(over, key=lambda o: -o["rel_diff"]), "tolerance": TOL,
            "exactly_equal_cells": int(np.sum(xn[m] == xr[m]))}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outroot", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--refs-dir")
    a = ap.parse_args(argv)
    runs = json.loads((HERE / "manifest" / "runs.json").read_text())
    refs = json.loads((HERE / "manifest" / "references.json").read_text())["references"]
    if runs["criterion"]["max_abs_rel_diff"] != TOL:
        raise SystemExit("the frozen tolerance and this comparator disagree")
    cells = refs["E_C"]["reported_globalid"]
    result = {"schema": "xr-comparisons/1", "tolerance": TOL, "outroot": a.outroot, "comparisons": {}}
    for c in runs["comparisons"] + runs["controls"]:
        new, err = newest_complete(a.outroot, c["new"])
        if c["ref"] in refs:
            r = refs[c["ref"]]
            path = Path(a.refs_dir, Path(r["path"]).name) if a.refs_dir else Path(r["path"])
            ref = {"path": str(path), "sha256": r["sha256"]} if path.is_file() and sha(path) == r["sha256"] else None
            rerr = None if ref else f"reference {c['ref']} missing or its sha256 differs"
        else:
            ref, rerr = newest_complete(a.outroot, c["ref"])
        if err or rerr:
            res = {"verdict": "INCONCLUSIVE", "why": err or rerr}
        else:
            res = compare(new["path"], ref["path"], cells)
            res.update(new=new, ref=ref)
        if "expect" in c:
            res["control_met"] = res["verdict"] == "FAIL"
        res["question"] = c.get("question") or c.get("why")
        result["comparisons"][c["id"]] = res
    Path(a.out).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    for k, v in result["comparisons"].items():
        print(f"{k}: {v['verdict']}" + (f" max {v['max_rel_diff_cells']:.3e} integral {v['integral_rel_diff']:.3e}"
                                        if "max_rel_diff_cells" in v else f" ({v.get('why')})"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
