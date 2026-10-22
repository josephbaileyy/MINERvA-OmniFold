"""List heading positions (section and subsection) in the note's pdftotext dump, with page and word offsets.
usage: python3 -I heads.py note.txt [min_line]
A heading is a line that is exactly a section number (e.g. '6', 'A', '6.3', 'C.4'), followed by a blank line and a
title line. Prints line number (1-based, of the number line), page, number, title.
"""
import re, sys
lines = open(sys.argv[1], encoding="utf-8").read().split("\n")
lo = int(sys.argv[2]) if len(sys.argv) > 2 else 400
page = 1; pg = []
for l in lines:
    page += l.count("\f"); pg.append(page)
for i in range(lo, len(lines) - 2):
    s = lines[i].replace("\f", "").strip()
    if re.fullmatch(r"(\d{1,2}|[A-J])(\.\d{1,2})?", s) and lines[i + 1].strip() == "" and lines[i + 2].strip():
        t = lines[i + 2].strip()
        if len(t) > 3 and t[0].isupper():
            print(f"{i+1}\tp{pg[i]}\t{s}\t{t[:70]}")
