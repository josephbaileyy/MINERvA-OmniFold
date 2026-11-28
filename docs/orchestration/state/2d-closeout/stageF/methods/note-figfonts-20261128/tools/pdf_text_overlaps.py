#!/usr/bin/env python3
"""pdf_text_overlaps.py: overlapping words in a figure PDF as it was saved (note-figfonts-20261128).

usage: python3 -I pdf_text_overlaps.py <file.pdf> [...]

capture_palette.py's text_overlaps reads each text's window extent at save time without a new draw, so after
layout_lib.apply() resizes the canvas, an artist placed at draw time (a legend with loc="best") still has the position
of the last draw, at the old size, and can be reported as overlapping texts it does not touch. This reads the saved
file instead: pdftotext -bbox gives every word's box; two words overlap if their boxes intersect by more than 0.5 pt
in both directions (words of one text line abut and do not count). Prints the overlapping pairs and a count; exit 1 if
any file has one.
"""
import re
import subprocess
import sys


def words(pdf):
    out = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
    return [(m.group(5), *map(float, m.group(1, 2, 3, 4))) for m in re.finditer(
        r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', out)]


def main(args):
    bad = 0
    for pdf in args:
        w = words(pdf); hits = []
        for i in range(len(w)):
            for j in range(i + 1, len(w)):
                a, b = w[i], w[j]
                dx = min(a[3], b[3]) - max(a[1], b[1]); dy = min(a[4], b[4]) - max(a[2], b[2])
                if dx > 0.5 and dy > 0.5:
                    hits.append((a[0], b[0], round(dx, 1), round(dy, 1)))
        bad += bool(hits)
        print(f"{pdf.rsplit('/', 1)[-1]}: {len(w)} words, {len(hits)} overlapping pairs {hits[:8]}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
