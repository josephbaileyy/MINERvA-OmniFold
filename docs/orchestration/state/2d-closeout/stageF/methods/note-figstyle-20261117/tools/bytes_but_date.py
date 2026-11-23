#!/usr/bin/env python3
"""Byte identity of two matplotlib PDFs apart from their creation date (the note palette pass, arm 0).

usage: python3 bytes_but_date.py A.pdf B.pdf [A2.pdf B2.pdf ...]

matplotlib writes the save time into /CreationDate (D:YYYYMMDDHHMMSS and an offset). For each pair, the files must
have the same length, each exactly one /CreationDate (D:...) value, and be byte-equal once both values are masked: every
differing byte lies inside the date. Prints, per pair, EQUAL (the files are equal outright), EQUAL-BUT-DATE (with both
dates), or DIFFER (with the count of differing bytes outside the date). Exit 1 unless every pair is EQUAL or
EQUAL-BUT-DATE.
"""
import re
import sys
from pathlib import Path

DATE = re.compile(rb"/CreationDate \(D:[0-9]{14}[^)]*\)")
args = sys.argv[1:]
if not args or len(args) % 2:
    sys.exit(__doc__)
bad = 0
for a, b in zip(args[::2], args[1::2]):
    x, y = Path(a).read_bytes(), Path(b).read_bytes()
    if x == y:
        print(f"EQUAL {Path(a).name}")
        continue
    dx, dy = DATE.findall(x), DATE.findall(y)
    if len(x) != len(y) or len(dx) != 1 or len(dy) != 1:
        print(f"DIFFER {Path(a).name}: lengths {len(x)} {len(y)}, dates {len(dx)} {len(dy)}")
        bad = 1
        continue
    mx, my = DATE.sub(lambda m: b"#" * len(m.group(0)), x), DATE.sub(lambda m: b"#" * len(m.group(0)), y)
    n = sum(1 for p, q in zip(mx, my) if p != q)
    if n:
        print(f"DIFFER {Path(a).name}: {n} byte(s) outside the date")
        bad = 1
    else:
        print(f"EQUAL-BUT-DATE {Path(a).name}: {dx[0].decode()} vs {dy[0].decode()}")
sys.exit(bad)
