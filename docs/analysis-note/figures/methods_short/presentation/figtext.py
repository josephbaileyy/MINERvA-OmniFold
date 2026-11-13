"""Printed sizes of the text inside each figure of a built PDF (pdfminer LTFigure contents), against the caption size."""
import sys, statistics, re
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTFigure, LTChar, LTTextContainer, LTTextLine
pdf = sys.argv[1]
def chars(o):
    if isinstance(o, LTChar): yield o
    elif hasattr(o, "__iter__"):
        for x in o: yield from chars(x)
for pno, page in enumerate(extract_pages(pdf), 1):
    figs = [o for o in page if isinstance(o, LTFigure)]
    cap = []
    for o in page:
        if isinstance(o, LTTextContainer):
            txt = o.get_text()
            if re.match(r"\s*(FIG|TABLE)\.", txt):
                cap += [c.size for c in chars(o) if c.get_text().strip()]
    for f in figs:
        cs = [c for c in chars(f) if c.get_text().strip()]
        if not cs: continue
        sz = sorted(c.size for c in cs)
        small = sorted(cs, key=lambda c: c.size)[:1]
        w = f.x1 - f.x0
        print(f"p{pno} figure {w:.0f}pt wide: {len(cs)} chars, min {sz[0]:.1f}pt, median {statistics.median(sz):.1f}pt, max {sz[-1]:.1f}pt"
              + (f" | caption median {statistics.median(cap):.1f}pt" if cap else ""))
