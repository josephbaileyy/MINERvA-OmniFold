#!/usr/bin/env python3
"""Figs. 6 and 7 after compose_slices_markers.py hold every data item of arm 0 (compose_tier2.py) unchanged.

usage: python3 -I check_slices_markers.py <arm-0 capture dir> <arm-1 capture dir>

Each capture is fig-restyle-20261031/tools/artists.py's index (capture_palette.py): per item a full hash (data,
colours, styles) and an "xhash" (data alone). For each slice figure:
  - the two captures have the same items in the same order (kind and label);
  - every item's xhash is equal (no x or y value moved);
  - an item whose full hash differs may differ only in its marker face colour (mfc, the open published markers), and
    there is exactly one such item per panel;
  - the projections (Fig. 4) are equal item for item, full hash.
Prints one line per figure, then CHECK-SLICES-MARKERS :: PASS or FAIL.
"""
import json
import sys
from pathlib import Path

A0, A1 = Path(sys.argv[1]), Path(sys.argv[2])
PANELS = {"MEFHC_5iter_xsec_paper_pt_slices": 14, "MEFHC_5iter_xsec_paper_pz_slices": 16}


def items(p):
    d = json.loads(p.read_text())
    return d["items"] if isinstance(d, dict) and "items" in d else d


ok = True
for stem, n_panels in PANELS.items():
    a, b = items(A0 / f"{stem}.pdf.json"), items(A1 / f"{stem}.pdf.json")
    same_order = len(a) == len(b) and all(x["kind"] == y["kind"] and x["label"] == y["label"] for x, y in zip(a, b))
    xh = sum(x["xhash"] == y["xhash"] for x, y in zip(a, b))
    diff = [(x, y) for x, y in zip(a, b) if x["hash"] != y["hash"]]
    keys = {k for x, y in diff for k in x["colours"] if x["colours"][k] != y["colours"].get(k)}
    styles = sum(x["style"] != y["style"] for x, y in diff)
    good = same_order and xh == len(a) and keys <= {"mfc"} and styles == 0 and len(diff) == n_panels
    ok &= good
    print(f"{stem}: {len(b)} items (arm 0 {len(a)}), same order {same_order}; xhash equal {xh}; full hash differs "
          f"{len(diff)} (one per panel: {n_panels}), differing colour fields {sorted(keys)}, style changes {styles}: "
          f"{'ok' if good else 'FAIL'}")
for stem in ("MEFHC_5iter_xsec_proj_pt", "MEFHC_5iter_xsec_proj_pz"):
    a, b = items(A0 / f"{stem}.pdf.json"), items(A1 / f"{stem}.pdf.json")
    good = len(a) == len(b) and all(x["hash"] == y["hash"] for x, y in zip(a, b))
    ok &= good
    print(f"{stem}: {len(b)} items, every full hash equal: {'ok' if good else 'FAIL'}")
print(f"CHECK-SLICES-MARKERS :: {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
