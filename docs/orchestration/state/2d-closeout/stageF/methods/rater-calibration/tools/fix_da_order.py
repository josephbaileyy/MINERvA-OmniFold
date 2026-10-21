"""usage: python3 -I fix_da_order.py TEXT.txt -- if the 'DATA AVAILABILITY' heading follows the first reference
line, move it to just before the section's first sentence; fail if that sentence is not found."""
import sys
p = sys.argv[1]; L = open(p, encoding="utf-8").read().split("\n")
h = [i for i, l in enumerate(L) if l.strip() == "DATA AVAILABILITY"]
r = [i for i, l in enumerate(L) if l.startswith("[1] ")]
if len(h) != 1: sys.exit("FAIL: expected one DATA AVAILABILITY heading, found %d" % len(h))
if not r or h[0] < r[0]: print("data-availability heading in reading order"); sys.exit(0)
b = [i for i, l in enumerate(L) if l.startswith("The input data and simulation are the MINERvA open")]
if len(b) != 1: sys.exit("FAIL: heading out of order and the section's first sentence not found once")
del L[h[0]]; L[b[0]:b[0]] = ["DATA AVAILABILITY", ""]
open(p, "w", encoding="utf-8").write("\n".join(L)); print("moved DATA AVAILABILITY heading back before its text")
