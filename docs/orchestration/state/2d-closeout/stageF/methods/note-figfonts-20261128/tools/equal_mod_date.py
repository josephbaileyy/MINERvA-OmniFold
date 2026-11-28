#!/usr/bin/env python3
"""equal_mod_date.py: are two PDFs the same apart from their creation date? (note-figfonts-20261128)

usage: python3 -I equal_mod_date.py A.pdf B.pdf [A2.pdf B2.pdf ...]

bytes_but_date.py (note-figstyle-20261117/tools) needs equal lengths, so it cannot compare a file dated by the clock
("D:20261127225537-07'00'") with one saved under SOURCE_DATE_EPOCH=0 ("D:19700101000000Z"): the date is 6 bytes
shorter, and so every xref offset after it moves. This masks exactly three things and compares every other byte:
  - the value of /CreationDate (...);
  - the xref table (from "xref" to "trailer") and the startxref offset, which only locate objects;
  - the trailer /ID [...] (pikepdf's deterministic_id hashes the whole file, the date included; strip_stamp.py saves so).
Prints EQUAL-MOD-DATE or DIFFER per pair; exit 1 if any pair differs.
"""
import re
import sys


def norm(b):
    b = re.sub(rb"/CreationDate\s*\([^)]*\)", b"/CreationDate()", b)
    b = re.sub(rb"\nxref\n.*?\ntrailer", b"\nxref\ntrailer", b, flags=re.S)
    b = re.sub(rb"startxref\s*\d+", b"startxref", b)
    b = re.sub(rb"/ID\s*\[\s*<[0-9A-Fa-f]*>\s*<[0-9A-Fa-f]*>\s*\]", b"/ID[]", b)
    return b


def main(args):
    if not args or len(args) % 2:
        print(__doc__.split("\n\n")[1]); return 2
    bad = 0
    for a, b in zip(args[::2], args[1::2]):
        ra, rb_ = open(a, "rb").read(), open(b, "rb").read()
        same = norm(ra) == norm(rb_)
        bad += not same
        print(f"{'EQUAL-MOD-DATE' if same else 'DIFFER'} {a.rsplit('/', 1)[-1]}: lengths {len(ra)} {len(rb_)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
