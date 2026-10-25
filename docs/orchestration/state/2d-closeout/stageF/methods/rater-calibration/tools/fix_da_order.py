"""usage: python3 -I fix_da_order.py TEXT.txt -- put the 'DATA AVAILABILITY' heading back in reading order.

Case 1 (r12): the heading follows the first reference line. Move it to just before the section's first sentence.
Case 2 (r17): the heading precedes the 'ACKNOWLEDGMENTS' heading, and the block just before it is the tail of the
acknowledgments (it ends with the AI statement's last sentence). pdftotext emitted that tail and the heading ahead of
the acknowledgments column. Move the tail and the heading to just before the section's first sentence, so the order
is ACKNOWLEDGMENTS, acknowledgment text, its tail, DATA AVAILABILITY, data-availability text.
Case 2b (r17 accuracy fixes): as case 2, and the ACKNOWLEDGMENTS heading itself was emitted inside the reference list.
Move it to just before the acknowledgments' first sentence.
Fail if the section's first sentence is not found once, or if case 2's tail is not the acknowledgments' end."""
import sys
p = sys.argv[1]; L = open(p, encoding="utf-8").read().split("\n")
h = [i for i, l in enumerate(L) if l.strip() == "DATA AVAILABILITY"]
r = [i for i, l in enumerate(L) if l.startswith("[1] ")]
a = [i for i, l in enumerate(L) if l.strip() == "ACKNOWLEDGMENTS"]
if len(h) != 1: sys.exit("FAIL: expected one DATA AVAILABILITY heading, found %d" % len(h))
first = "The input data and simulation are the MINERvA open"
if len(a) == 1 and h[0] < a[0]:
    t1 = h[0]
    while t1 > 0 and not L[t1 - 1].strip():  # blank lines between the tail and the heading
        t1 -= 1
    t0 = t1
    while t0 > 0 and L[t0 - 1].strip():
        t0 -= 1
    tail = L[t0:t1]
    if not tail or not tail[-1].rstrip().endswith("responsibility for the content."):
        sys.exit("FAIL: heading precedes ACKNOWLEDGMENTS but the block before it is not the acknowledgments' tail")
    del L[t0:h[0] + 1]
    b = [i for i, l in enumerate(L) if l.startswith(first)]
    if len(b) != 1: sys.exit("FAIL: the data-availability section's first sentence not found once")
    L[b[0]:b[0]] = tail + ["", "DATA AVAILABILITY", ""]
    a2 = [i for i, l in enumerate(L) if l.strip() == "ACKNOWLEDGMENTS"][0]
    r2 = [i for i, l in enumerate(L) if l.startswith("[1] ")]
    if r2 and a2 > r2[0]:  # case 2b: pdftotext also emitted the heading inside the reference list
        t = [i for i, l in enumerate(L) if l.startswith("The authors thank the MINERvA Collaboration")]
        if len(t) != 1 or t[0] > r2[0]:
            sys.exit("FAIL: ACKNOWLEDGMENTS heading in the reference list and the acknowledgments' first sentence not found once")
        del L[a2]
        L[t[0]:t[0]] = ["ACKNOWLEDGMENTS", ""]
        print("moved the ACKNOWLEDGMENTS heading out of the reference list, to before the acknowledgments' first sentence")
        a2 = [i for i, l in enumerate(L) if l.strip() == "ACKNOWLEDGMENTS"][0]
    h2 = [i for i, l in enumerate(L) if l.strip() == "DATA AVAILABILITY"][0]
    b2 = [i for i, l in enumerate(L) if l.startswith(first)][0]
    assert a2 < h2 < b2, (a2, h2, b2)
    open(p, "w", encoding="utf-8").write("\n".join(L))
    print("moved the acknowledgments' tail (%d lines) and the DATA AVAILABILITY heading back into reading order"
          % len(tail))
    sys.exit(0)
if not r or h[0] < r[0]: print("data-availability heading in reading order"); sys.exit(0)
b = [i for i, l in enumerate(L) if l.startswith(first)]
if len(b) != 1: sys.exit("FAIL: heading out of order and the section's first sentence not found once")
del L[h[0]]; L[b[0]:b[0]] = ["DATA AVAILABILITY", ""]
open(p, "w", encoding="utf-8").write("\n".join(L)); print("moved DATA AVAILABILITY heading back before its text")
