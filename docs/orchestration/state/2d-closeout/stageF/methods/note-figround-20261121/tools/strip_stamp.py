#!/usr/bin/env python3
"""Remove the "MINERvA ME FHC, 1.06 x 10^21 POT" stamp from an installed note figure PDF (cov2d, 2026-11-21; Joseph's
suggestion via the director: Sec. 2 states the exposure, and "ME FHC" is never defined).

usage: python3 strip_stamp.py <in.pdf> <out.pdf> <record.json>       (figenv/pdfedit: pikepdf 9.4.2; pdftotext, pdftoppm)

A deletion only, made on the PDF so that no producer runs again: the stamp's words are located with pdftotext -bbox
(the line "MINERvA ME FHC, ... POT"), their union box is mapped to PDF user space, and every text object (BT ... ET)
whose glyph origins all fall inside that box (enlarged by 1 pt) is deleted from the page's content stream. The graphics
state operators around it are kept. Nothing else in the file is touched (pikepdf rewrites the file structure, not other
content).
Checks (each failure leaves no output):
- the stamp line is found exactly once, and at least one text object is removed;
- an object is removed only if every one of its glyph origins lies inside the box;
- pdftotext's words after = the words before minus exactly the stamp's words, each at the same box (0.1 pt; the
  reading order may change);
- rendered at 200 dpi (pdftoppm -gray), no pixel differs outside the stamp box enlarged by 2 pt;
- the page size is unchanged.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pikepdf

IN, OUT, REC = map(Path, sys.argv[1:4])


def words(pdf):
    xml = subprocess.run(["pdftotext", "-bbox", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    h = float(re.search(r'<page width="[-\d.]+" height="([-\d.]+)"', xml).group(1))
    w = [(float(a), float(b), float(c), float(d), t) for a, b, c, d, t in
         re.findall(r'<word xMin="([-\d.]+)" yMin="([-\d.]+)" xMax="([-\d.]+)" yMax="([-\d.]+)">([^<]*)</word>', xml)]
    return h, w


H, W = words(IN)
starts = [i for i, x in enumerate(W) if x[4] == "MINERvA" and i + 2 < len(W) and W[i + 1][4] == "ME" and W[i + 2][4].startswith("FHC")]
if len(starts) != 1:
    sys.exit(f"strip_stamp: {IN.name}: stamp line found {len(starts)} times")
i0 = starts[0]
i1 = next((j for j in range(i0, min(i0 + 12, len(W))) if W[j][4] == "POT"), None)
if i1 is None:
    sys.exit(f"strip_stamp: {IN.name}: no 'POT' closes the stamp line")
stamp = W[i0:i1 + 1]
x0, x1 = min(s[0] for s in stamp), max(s[2] for s in stamp)
ytop, ybot = min(s[1] for s in stamp), max(s[3] for s in stamp)
box = (x0 - 1, H - ybot - 1, x1 + 1, H - ytop + 1)            # PDF user space (origin lower left)


def inside(p, b):
    return b[0] <= p[0] <= b[2] and b[1] <= p[1] <= b[3]


def mul(a, b):   # 3x3 affine as (a, b, c, d, e, f): [a b 0; c d 0; e f 1]
    return (a[0] * b[0] + a[1] * b[2], a[0] * b[1] + a[1] * b[3], a[2] * b[0] + a[3] * b[2], a[2] * b[1] + a[3] * b[3],
            a[4] * b[0] + a[5] * b[2] + b[4], a[4] * b[1] + a[5] * b[3] + b[5])


pdf = pikepdf.open(IN)
page = pdf.pages[0]
mb = [float(v) for v in page.MediaBox]
ops = pikepdf.parse_content_stream(page)
ctm, stack = (1, 0, 0, 1, 0, 0), []
out, blk, origins, removed = [], None, [], []
tm = tlm = None
for operands, op in ops:
    o = str(op)
    if blk is None:
        if o == "q": stack.append(ctm)
        elif o == "Q": ctm = stack.pop()
        elif o == "cm": ctm = mul(tuple(float(v) for v in operands), ctm)
        if o == "BT":
            blk, origins = [(operands, op)], []; tm = tlm = (1, 0, 0, 1, 0, 0)
            continue
        out.append((operands, op)); continue
    blk.append((operands, op))
    if o == "Td":
        tlm = mul((1, 0, 0, 1, float(operands[0]), float(operands[1])), tlm); tm = tlm
    elif o == "Tm":
        tlm = tuple(float(v) for v in operands); tm = tlm
    elif o in ("Tj", "TJ", "'", '"'):
        m = mul(tm, ctm); origins.append((m[4], m[5]))
    elif o == "ET":
        if origins and all(inside(p, box) for p in origins):
            removed.append([list(p) for p in origins])
        else:
            out.extend(blk)
        blk = None
if not removed:
    sys.exit(f"strip_stamp: {IN.name}: no text object lies inside the stamp box")
page.Contents = pdf.make_stream(pikepdf.unparse_content_stream(out))
with tempfile.TemporaryDirectory() as td:
    tmp = Path(td) / "out.pdf"
    pdf.save(tmp, deterministic_id=True)
    H2, W2 = words(tmp)
    from collections import Counter
    key = lambda w: (w[4], round(w[0], 1), round(w[1], 1), round(w[2], 1), round(w[3], 1))
    want = Counter(key(w) for k, w in enumerate(W) if not (i0 <= k <= i1)); got = Counter(key(w) for w in W2)
    if want != got or H2 != H:   # same words at the same boxes (pdftotext's reading order may change)
        sys.exit(f"strip_stamp: {IN.name}: words after differ from the words before minus the stamp: "
                 f"missing {sorted((want - got).elements())[:6]}, extra {sorted((got - want).elements())[:6]}")
    for f, tag in ((IN, "a"), (tmp, "b")):
        subprocess.run(["pdftoppm", "-r", "200", "-gray", "-singlefile", str(f), str(Path(td) / tag)], check=True)
    def pgm(p):
        b = p.read_bytes(); parts = b.split(b"\n", 3)
        w, h = map(int, parts[1].split()); return w, h, parts[3]
    wa, ha, A = pgm(Path(td) / "a.pgm"); wb, hb, B = pgm(Path(td) / "b.pgm")
    if (wa, ha) != (wb, hb):
        sys.exit(f"strip_stamp: {IN.name}: raster size changed")
    s = 200 / 72.0
    bx0, by0, bx1, by1 = (box[0] - 2) * s, (H - box[3] - 2) * s, (box[2] + 2) * s, (H - box[1] + 2) * s
    nd = nout = 0
    for k in range(len(A)):
        if A[k] != B[k]:
            nd += 1; y, x = divmod(k, wa)
            if not (bx0 <= x <= bx1 and by0 <= y <= by1): nout += 1
    if nout:
        sys.exit(f"strip_stamp: {IN.name}: {nout} pixels differ outside the stamp box")
    OUT.write_bytes(tmp.read_bytes())
REC.write_text(json.dumps({"input": IN.name, "stamp_words": [w[4] for w in stamp], "box_pdf_pt": box,
                           "text_objects_removed": len(removed), "removed_glyph_origins": removed,
                           "pixels_changed_200dpi": nd, "pixels_changed_outside_box": nout, "page_size": mb[2:]}, indent=1) + "\n")
print(f"{IN.name}: removed {len(removed)} text objects ({' '.join(w[4] for w in stamp)}); {nd} pixels changed, all inside the box")
