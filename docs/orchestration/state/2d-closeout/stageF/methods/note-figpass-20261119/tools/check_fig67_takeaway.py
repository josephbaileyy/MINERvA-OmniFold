#!/usr/bin/env python3
"""The Figs. 6 and 7 takeaway (DECISION-20261120b: Joseph, "for fig 6/7 we can add the claim"), measured on the
figures' own drawn arrays.

usage: python3 check_fig67_takeaway.py <capture dir> <out json>

<capture dir> holds the markers run's arm-1 captures (runs/markers/capture/arm1: the .pdf.json index and .pdf.npz
arrays that capture_palette.py wrote while the installed figures were drawn; the installed PDFs are byte-equal to
arm 1's outputs, runs/markers/CHECKS.txt). For each slice panel of MEFHC_5iter_xsec_paper_pt_slices and _pz_slices:
  result    = the one red circle series (#C0392B, marker o: the unfolded cross section; the | and _ artists are its
              error-bar caps),
  published = the one black-edged square series (marker s: the published data),
  prior     = the one step histogram labelled "... Tune v1" (the simulation's truth, GENIE 2.12.6 + MINERvA Tune v1),
each read at the result's bin centres, over bins where the scaled result exceeds 0.05 (the panel's own scale).
The panel's two numbers are the median over those bins of |published/result - 1| and of |prior/result - 1|.
Refuses (exit 1) unless every panel has exactly one series of each kind with the result's bins, and writes, per figure,
the panel count, the count of panels where the prior differs more than the published data, and the ranges.
"""
import json
import sys
from pathlib import Path

import numpy as np

STEMS = {"pt": "MEFHC_5iter_xsec_paper_pt_slices", "pz": "MEFHC_5iter_xsec_paper_pz_slices"}
RED = "C0392B"


def step_height(v, xi):
    for p, q in zip(v[:-1], v[1:]):
        if abs(p[1] - q[1]) < 1e-15 and p[0] <= xi < q[0]:
            return p[1]
    return np.nan


def panels(cap, stem):
    idx = json.loads((cap / f"{stem}.pdf.json").read_text())
    idx = idx["items"] if isinstance(idx, dict) else idx
    arr = np.load(cap / f"{stem}.pdf.npz")
    out = []
    for a in sorted({it["axes"] for it in idx}):
        its = [it for it in idx if it["axes"] == a and it["kind"] in ("line", "patch")]
        lines = [it for it in its if it["kind"] == "line" and arr[f"i{it['i']}.xy"].shape[0] > 2]
        red = [it for it in lines if RED in str(it["colours"].get("mfc", "")) and it["style"].get("marker") == "o"]
        blk = [it for it in lines if str(it["colours"].get("mec", "")).startswith("['#000000")
               and it["style"].get("marker") == "s"]
        pat = [it for it in its if it["kind"] == "patch" and "Tune v1" in str(it.get("label", ""))]
        if not red and not blk and not pat:
            continue                                   # a legend or empty axes
        if (len(red), len(blk), len(pat)) != (1, 1, 1):
            sys.exit(f"REFUSE: {stem} axes {a}: {len(red)} result, {len(blk)} published, {len(pat)} prior series")
        r, b = arr[f"i{red[0]['i']}.xy"], arr[f"i{blk[0]['i']}.xy"]
        v = arr[f"i{pat[0]['i']}.vertices"]
        if len(b) != len(r) or not np.allclose(b[:, 0], r[:, 0], rtol=1e-12, atol=0):
            sys.exit(f"REFUSE: {stem} axes {a}: the published points are not on the result's bins")
        yr, yb = r[:, 1], b[:, 1]
        yp = np.array([step_height(v, xi) for xi in r[:, 0]])
        m = (yr > 0.05) & np.isfinite(yp)
        if m.sum() < 3:
            sys.exit(f"REFUSE: {stem} axes {a}: fewer than 3 bins above 0.05")
        out.append({"axes": int(a), "bins": int(m.sum()),
                    "median_rel_published": float(np.median(np.abs(yb[m] / yr[m] - 1))),
                    "median_rel_prior": float(np.median(np.abs(yp[m] / yr[m] - 1)))})
    return out


def main():
    cap, outp = Path(sys.argv[1]), Path(sys.argv[2])
    rec = {"decision": "DECISION-20261120b", "capture": str(cap), "figures": {}}
    for k, stem in STEMS.items():
        ps = panels(cap, stem)
        pub = [p["median_rel_published"] for p in ps]
        pri = [p["median_rel_prior"] for p in ps]
        rec["figures"][k] = {
            "stem": stem, "panels": len(ps),
            "panels_prior_differs_more": sum(p["median_rel_prior"] > p["median_rel_published"] for p in ps),
            "published_min": min(pub), "published_max": max(pub), "prior_min": min(pri), "prior_max": max(pri),
            "per_panel": ps}
        f = rec["figures"][k]
        print(f"{stem}: {f['panels_prior_differs_more']} of {f['panels']} panels; median relative difference from the "
              f"published points {f['published_min']:.3f}-{f['published_max']:.3f}, from the prior "
              f"{f['prior_min']:.3f}-{f['prior_max']:.3f}")
    outp.write_text(json.dumps(rec, indent=1) + "\n")


if __name__ == "__main__":
    main()
