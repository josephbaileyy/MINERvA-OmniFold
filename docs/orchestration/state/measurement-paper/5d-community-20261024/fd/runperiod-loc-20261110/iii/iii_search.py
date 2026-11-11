#!/usr/bin/env python3
"""RPL check (iii): the declared search over the published analysis's text (RPL-DECLARATION.md (iii)).
Input: pdftotext output (no -layout) of arXiv:2106.16210 (latest, v4), and the ancillary README. Prints every hit of
each declared term with 240 characters of context on each side, after de-hyphenating and flattening line breaks.
Usage: python3 -I iii_search.py <paper.txt> <anc README>"""
import re
import sys

TERMS = ["playlist", "run period", "run-period", "1G", "1M", "tilted", "horn", "slip", "MINOS range", "range",
         "curvature", "muon energy scale", "energy scale", "pile-up", "pileup", "intensity", "per-playlist",
         "playlist-dependent", "time period", "as a function of time"]
for path in sys.argv[1:]:
    raw = open(path, encoding="utf-8", errors="replace").read()
    flat = re.sub(r"\s*\n\s*", " ", re.sub(r"-\n(?=[a-z])", "", raw))
    print(f"=== {path.rsplit('/', 1)[-1]}: {len(flat)} characters")
    for term in TERMS:
        pat = re.compile(r"\b" + re.escape(term), re.I)   # a leading boundary only, so plurals match
        hits = list(pat.finditer(flat))
        print(f"--- term {term!r}: {len(hits)} hit(s)")
        for m in hits:
            s, e = max(0, m.start() - 240), min(len(flat), m.end() + 240)
            print(f"    @{m.start()}: ...{flat[s:e]}...")
