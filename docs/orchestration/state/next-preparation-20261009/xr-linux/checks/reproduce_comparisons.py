#!/usr/bin/env python3
"""Owner's independent reproduction of the XR comparisons from the output histograms.

    python reproduce_comparisons.py OUTROOT RUNS_JSON REFERENCES_JSON OUT.json

Written apart from ``xr/xr_compare.py`` (no code shared): for each comparison and the control in
``runs.json`` it takes each run's newest attempt whose ``receipt.json`` is ``complete``, re-hashes the
output against the receipt and every frozen reference against ``references.json``, reads ``hXSec2D``
bin by bin, and computes over the reported cells (the reference's GlobalIDs, pT*16 + p_par, 0-based)
the max and median |new/ref - 1| and the relative difference of the area-weighted integral
(correctly rounded sums, ``math.fsum``; the comparator sums with numpy, so the two integral
differences agree only to rounding, ~1e-15 absolute). The reported cells' values (repr) of every
product read are written beside the results. A comparison it cannot form is reported with the
reason. Read-only; small ROOT files only.
"""
import hashlib
import json
import math
import sys
from pathlib import Path


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def hist(path):
    import ROOT
    f = ROOT.TFile.Open(str(path))
    h = f.Get("hXSec2D")
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    vals, widths = {}, {}
    for i in range(nx):
        for j in range(ny):
            g = i * ny + j
            vals[g] = h.GetBinContent(i + 1, j + 1)
            widths[g] = h.GetXaxis().GetBinWidth(i + 1) * h.GetYaxis().GetBinWidth(j + 1)
    axes = ([h.GetXaxis().GetBinLowEdge(i + 1) for i in range(nx + 1)],
            [h.GetYaxis().GetBinLowEdge(j + 1) for j in range(ny + 1)])
    f.Close()
    return vals, widths, axes


def newest(outroot, run):
    best = None
    for d in Path(outroot, run).glob("a*"):
        r = d / "receipt.json"
        if r.is_file() and r.stat().st_size:
            rec = json.loads(r.read_text())
            if rec.get("status") == "complete" and rec.get("run") == run and (best is None or rec["attempt"] > best["attempt"]):
                best = rec
    if best is None:
        return None, "no complete attempt"
    if sha(best["output"]["path"]) != best["output"]["sha256"]:
        return None, "output digest differs from its receipt"
    return best, None


def main(outroot, runs_p, refs_p, out_p):
    runs = json.loads(Path(runs_p).read_text())
    refs = json.loads(Path(refs_p).read_text())["references"]
    cells = refs["E_C"]["reported_globalid"]
    res, values = {}, {}

    def keep(path, xs):
        values[str(path)] = {"sha256": sha(path), "hXSec2D_reported_cells": {str(g): repr(xs[g]) for g in cells}}

    for c in runs["comparisons"] + runs["controls"]:
        new, err = newest(outroot, c["new"])
        if c["ref"] in refs:
            rp = refs[c["ref"]]["path"]
            rerr = None if Path(rp).is_file() and sha(rp) == refs[c["ref"]]["sha256"] else "reference missing or digest differs"
            ref = {"path": rp}
        else:
            ref, rerr = newest(outroot, c["ref"])
            ref = {"path": ref["output"]["path"]} if ref else None
        if err or rerr:
            res[c["id"]] = {"formed": False, "why": err or rerr}
            continue
        xn, w, an = hist(new["output"]["path"])
        xr, _, ar = hist(ref["path"])
        keep(new["output"]["path"], xn)
        keep(ref["path"], xr)
        pos_n = sorted(g for g, v in xn.items() if v > 0)
        pos_r = sorted(g for g, v in xr.items() if v > 0)
        rel = sorted(abs(xn[g] / xr[g] - 1) for g in cells if xr[g] > 0)
        i_n = math.fsum(xn[g] * w[g] for g in cells)
        i_r = math.fsum(xr[g] * w[g] for g in cells)
        res[c["id"]] = {"formed": True, "new": new["output"]["path"], "new_attempt": new["attempt"], "ref": ref["path"],
                        "axes_equal": an == ar, "cells_new_equal_frozen": pos_n == cells,
                        "cells_ref_equal_frozen": pos_r == cells, "n_cells": len(rel),
                        "max_rel_diff_cells": rel[-1], "median_rel_diff_cells": rel[len(rel) // 2],
                        "integral_rel_diff": abs(i_n / i_r - 1),
                        "n_cells_over_1e-8": sum(1 for r in rel if r > 1e-8),
                        "exactly_equal_cells": sum(1 for g in cells if xn[g] == xr[g])}
    Path(out_p).write_text(json.dumps({"comparisons": res, "values": values}, indent=1, sort_keys=True) + "\n")
    for k, v in res.items():
        print(k, {kk: v[kk] for kk in ("max_rel_diff_cells", "integral_rel_diff", "n_cells_over_1e-8")} if v["formed"] else v["why"])


if __name__ == "__main__":
    main(*sys.argv[1:5])
