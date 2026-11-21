#!/usr/bin/env python3
"""Check compose_fig2_edges.py's projections against compose_tier2.py's, from capture_palette.py captures.

usage: python3 check_fig2_edges.py <committed capture dir> <arm 0 capture dir> <arm 1 capture dir> <arm 1 out dir>

<committed capture dir>: note-figpass-20261119/runs/markers/capture/arm1, which captured the installed projections.
Arm 0 is compose_tier2.py unchanged, and arm 1 is compose_fig2_edges.py, in the same environment on the same inputs.
For each projection, it passes only if all of these hold:
  - arm 0's item hashes equal the committed capture's, in order (arm 0 draws the installed figure);
  - arm 1 has the same items in the same order. Every item's hash is equal except exactly one: the line labelled
    "Tune v1: published prediction". That line's colours are equal, its style differs only in drawstyle (steps-mid to
    steps-post), its x is the edges in compose_fig2_edges.json, and its y equals arm 0's on the bins with the last
    value repeated once;
  - every drawn string and its font size are equal between the arms (.texts).
"""
import json
import sys
from pathlib import Path

import numpy as np

STEMS = ("MEFHC_5iter_xsec_proj_pt", "MEFHC_5iter_xsec_proj_pz")
ANC = "Tune v1: published prediction"


def idx(d, stem):
    i = json.loads((d / f"{stem}.pdf.json").read_text())
    return i["items"] if isinstance(i, dict) else i


def main():
    com, a0, a1, out = map(Path, sys.argv[1:5])
    rep = json.loads((out / "compose_fig2_edges.json").read_text())
    ok = True
    for stem in STEMS:
        ic, ia, ib = idx(com, stem), idx(a0, stem), idx(a1, stem)
        same0 = [x["hash"] for x in ic] == [x["hash"] for x in ia]
        order = [(x["kind"], x.get("label")) for x in ia] == [(x["kind"], x.get("label")) for x in ib]
        diff = [(x, y) for x, y in zip(ia, ib) if x["hash"] != y["hash"]]
        one = len(diff) == 1 and diff[0][0].get("label") == ANC
        detail = "n/a"
        if one:
            x, y = diff[0]
            sd = {k for k in set(x["style"]) | set(y["style"]) if x["style"].get(k) != y["style"].get(k)}
            za, zb = np.load(a0 / f"{stem}.pdf.npz"), np.load(a1 / f"{stem}.pdf.npz")
            A, B = za[f"i{x['i']}.xy"], zb[f"i{y['i']}.xy"]
            edges = np.asarray(rep[stem]["edges"], float)
            one = (x["colours"] == y["colours"] and sd == {"drawstyle"} and x["style"]["drawstyle"] == "steps-mid"
                   and y["style"]["drawstyle"] == "steps-post" and np.array_equal(B[:, 0], edges)
                   and np.array_equal(A[:, 1], B[:-1, 1]) and B[-1, 1] == B[-2, 1])
            detail = f"x {A[:, 0].size} centres -> {B[:, 0].size} edges, y equal on the bins"
        ta, tb = (json.loads((d / f"{stem}.pdf.texts").read_text()) for d in (a0, a1))
        texts = ta == tb
        good = same0 and order and one and texts
        ok &= good
        print(f"{stem}: arm 0 = committed capture ({len(ic)} items) {same0}; arm 1 same items and order {order}; "
              f"{len(ia) - len(diff)} equal, {len(diff)} differ, the published-prediction line only and only its "
              f"drawing {one} ({detail}); strings equal {texts}: {'ok' if good else 'FAIL'}")
    print(f"CHECK-FIG2-EDGES :: {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
