#!/usr/bin/env python3
"""Tier 2's arm-0 identity: a local redraw of a Figs. 6-14 producer against the cluster's capture of the installed file.

usage: python3 compare_cluster.py <cluster capture .png.json> <local arm-0 capture .png.json>

Figs. 7-14 were drawn on Perlmutter (note-figstyle-20261113 family 2, the after arm, whose PDFs are the installed ones),
and that run's capture.py recorded each figure's data artists. A local draw of the same producer on the fetched inputs
(the same two files, sha256-checked) cannot be pixel-equal: the renderer's environment differs. So the identity is the
data, as COMBINED-PLAN.md section 5(b) has it ("compare against a local default draw, not bitwise across
architectures"):
  - the multiset of colour-free hashes ("dhash") of the data artists must be equal, leaving out the cluster tool's own
    "hist-input" items (the 10-31 capture.py also recorded each Axes.hist call's values, which capture_palette.py does
    not; the bars themselves are compared);
  - each figure's drawn texts must be the same strings (capture.py's textsizes.tsv beside the cluster record, and
    capture_palette.py's .texts beside the local one), as multisets.
Prints DATA-IDENTITY :: PASS or FAIL; exit 1 on FAIL.
"""
import json
import sys
from collections import Counter
from pathlib import Path

cj, lj = Path(sys.argv[1]), Path(sys.argv[2])
a = [x for x in json.loads(cj.read_text()) if x["kind"] != "hist-input"]
b = json.loads(lj.read_text())
da, db = Counter(x["dhash"] for x in a), Counter(x["dhash"] for x in b)
ok = da == db and len(a) > 0
print(f"data: {len(a)} cluster items, {len(b)} local; colour-free hash multisets {'equal' if da == db else 'DIFFER'}")
if da != db:
    print("  cluster only:", [(x["kind"], x["label"]) for x in a if (da - db)[x["dhash"]]][:6])
    print("  local only:  ", [(x["kind"], x["label"]) for x in b if (db - da)[x["dhash"]]][:6])
ts = cj.with_name(cj.name[: -len(".json")] + ".textsizes.tsv")
tc = Counter(ln.split("\t", 1)[1] for ln in ts.read_text().splitlines()[1:] if "\t" in ln) if ts.exists() else None
tl = Counter(t for _, t in json.loads(lj.with_name(lj.name[: -len(".json")] + ".texts").read_text())["texts"])
if tc is None:
    print("texts: no cluster textsizes record")
    ok = False
else:
    same = tc == tl
    ok &= same
    print(f"texts: {sum(tc.values())} cluster, {sum(tl.values())} local; {'equal' if same else 'DIFFER'}")
    if not same:
        print("  cluster only:", list((tc - tl).elements())[:6])
        print("  local only:  ", list((tl - tc).elements())[:6])
print(f"DATA-IDENTITY :: {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
