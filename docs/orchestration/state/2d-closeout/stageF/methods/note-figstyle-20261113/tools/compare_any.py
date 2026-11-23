#!/usr/bin/env python3
"""Compare two capture_any.py arms (note figure style, director 2026-11-13).

usage: python3 compare_any.py <arm A dir> <arm B dir> [--widths widths.tsv]

For every saved file recorded in both arms, the multiset of "hash" (data, colours and line styles: artists.py) must be
equal: the figure draws the same data in the same colours and styles. Exit 1 on any difference, or if the two arms
saved different file names.
With --widths (tsv: saved file name, printed width as a fraction of the note's 6.5 in text width), it also prints each
figure's smallest and largest text size as printed: the size in points times printed width / canvas width.
"""
import json
import sys
from collections import Counter
from pathlib import Path

a, b = Path(sys.argv[1]), Path(sys.argv[2])
widths = {}
if "--widths" in sys.argv:
    for line in Path(sys.argv[sys.argv.index("--widths") + 1]).read_text().splitlines():
        if line and not line.startswith("#"):
            name, frac = line.split("\t")
            widths[name] = float(frac)
ra = {p.name: json.loads(p.read_text()) for p in sorted(a.glob("*.json"))}
rb = {p.name: json.loads(p.read_text()) for p in sorted(b.glob("*.json"))}
fail = 0
if set(ra) != set(rb):
    print(f"FAIL saved files differ: only A {sorted(set(ra) - set(rb))}, only B {sorted(set(rb) - set(ra))}")
    fail = 1


def printed(rec, name):
    key = name[:-len(".json")]
    if key not in widths or not rec["texts"]:
        return ""
    k = widths[key] * 6.5 / rec["size_in"][0]
    s = [t[0] * k for t in rec["texts"]]
    return f"; printed text {min(s):.1f}-{max(s):.1f} pt (canvas {rec['size_in'][0]:.2f} in)"


for name in sorted(set(ra) & set(rb)):
    ha, hb = Counter(i["hash"] for i in ra[name]["items"]), Counter(i["hash"] for i in rb[name]["items"])
    ok = ha == hb and len(ra[name]["items"]) > 0
    fail |= not ok
    print(f"{'ok  ' if ok else 'FAIL'} {name}: {len(ra[name]['items'])} vs {len(rb[name]['items'])} data artists, "
          f"hash multisets {'equal' if ha == hb else 'DIFFER'}{printed(ra[name], name)} -> {printed(rb[name], name).lstrip('; ')}"
          f"; text overlaps {len(ra[name].get('text_overlaps', []))} -> {len(rb[name].get('text_overlaps', []))}")
    for o in rb[name].get("text_overlaps", []):
        print(f"       B overlap: {o[0][:40]!r} x {o[1][:40]!r} ({o[2]} px^2)")
print(f"COMPARE :: {'FAIL' if fail else 'PASS'}")
sys.exit(1 if fail else 0)
