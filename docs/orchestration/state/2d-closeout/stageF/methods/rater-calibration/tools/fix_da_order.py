"""usage: python3 -I fix_da_order.py TEXT.txt -- put the 'DATA AVAILABILITY' heading back in reading order.

Case 1 (r12): the heading follows the first reference line. Move it to just before the section's first sentence.
Case 2 (r17): the heading precedes the 'ACKNOWLEDGMENTS' heading, and the block just before it is the tail of the
acknowledgments (it ends with the AI statement's last sentence). pdftotext emitted that tail and the heading ahead of
the acknowledgments column. Move the tail and the heading to just before the section's first sentence, so the order
is ACKNOWLEDGMENTS, acknowledgment text, its tail, DATA AVAILABILITY, data-availability text.
Case 2b (r17 accuracy fixes): as case 2, and the ACKNOWLEDGMENTS heading itself was emitted inside the reference list.
Move it to just before the acknowledgments' first sentence.
Case 3 (r18): the headings are in reading order, but the data-availability text after its first line was emitted
between the acknowledgments' end and the DATA AVAILABILITY heading, and the heading and first sentence come last,
just before the reference list. Move the continuation to just after the first sentence's block.
Case 4 (#413 at a55e2686, before r19): the first lines of reference [1] were emitted inside the last paragraph of the
body, ahead of the ACKNOWLEDGMENTS heading, and the rest of [1] follows the data-availability text. Blinding cuts the
references at '[1] ', so it dropped the end of the body, the acknowledgments and the data-availability section. Move the
fragment to just before the rest of [1] and rejoin the paragraph it split. This runs first; cases 1-3 then apply.
Case 5 (the 5B text round, 2026-10-31): as case 2 (the acknowledgments' tail and both headings first), and the first
references, [1] to part of [n], were emitted after the acknowledgments' first part and ahead of the data-availability
text, whose last sentence is followed by the rest of [n] and then [n+1]. Blinding cuts at '[1] ', so it dropped the
data-availability section. Move the fragment to just before the rest of [n]. This runs after case 4; case 2 then
applies.
Fail if the section's first sentence is not found once, if case 2's tail is not the acknowledgments' end, if case 4's
fragment or its continuation is not where that layout puts them, or if a reference line precedes the heading in a layout
no case describes. Every move keeps the word multiset."""
import re
import sys
p = sys.argv[1]; L = open(p, encoding="utf-8").read().split("\n")
words0 = sorted(" ".join(L).split())
h = [i for i, l in enumerate(L) if l.strip() == "DATA AVAILABILITY"]
r = [i for i, l in enumerate(L) if l.startswith("[1] ")]
a = [i for i, l in enumerate(L) if l.strip() == "ACKNOWLEDGMENTS"]
if len(h) != 1: sys.exit("FAIL: expected one DATA AVAILABILITY heading, found %d" % len(h))
first = "The input data and simulation are the MINERvA open"
if len(r) == 1 and len(a) == 1 and r[0] < a[0] < h[0]:  # case 4
    k = r[0]
    while k < len(L) and L[k].strip():
        k += 1
    frag = L[r[0]:k]
    if frag[-1].rstrip().endswith((".", "]")):
        sys.exit("FAIL: a [1] line precedes ACKNOWLEDGMENTS but it reads as a whole reference, not a fragment")
    end = [i for i in range(h[0], len(L)) if L[i].rstrip().endswith("does not reproduce.")]
    if len(end) != 1: sys.exit("FAIL: case 4 layout but the data-availability text's last sentence not found once")
    c = end[0] + 1
    while c < len(L) and not L[c].strip():
        c += 1
    nxt = [i for i in range(c, len(L)) if L[i].startswith("[")]
    if c == len(L) or L[c].startswith("[") or not nxt or not L[nxt[0]].startswith("[2] ") or nxt[0] - c > 4:
        sys.exit("FAIL: case 4 layout but the rest of [1] is not the block between the data-availability text and [2]")
    # the fragment split a sentence when the text before it does not end one; then drop the blank lines on both sides
    s0, s1 = r[0], k
    while s1 < len(L) and not L[s1].strip():
        s1 += 1
    if s0 > 1 and not L[s0 - 1].strip() and L[s0 - 2].rstrip()[-1:] not in ".?!:":
        while s0 > 0 and not L[s0 - 1].strip():
            s0 -= 1
    L[c:c] = frag
    del L[s0:s1]
    r = [i for i, l in enumerate(L) if l.startswith("[1] ")]
    h = [i for i, l in enumerate(L) if l.strip() == "DATA AVAILABILITY"]
    a = [i for i, l in enumerate(L) if l.strip() == "ACKNOWLEDGMENTS"]
    assert len(r) == 1 and a[0] < h[0] < r[0], (a, h, r)
    assert sorted(" ".join(L).split()) == words0, "word multiset changed"
    open(p, "w", encoding="utf-8").write("\n".join(L))
    print("moved reference [1]'s first %d lines out of the body, to before the rest of [1]" % len(frag))
if len(r) == 1 and len(a) == 1 and h[0] < a[0] < r[0]:  # case 5
    b = [i for i, l in enumerate(L) if l.startswith(first)]
    if len(b) == 1 and r[0] < b[0]:
        k = r[0]
        while k < len(L) and L[k].strip():
            k += 1
        frag = L[r[0]:k]
        nums = [int(m.group(1)) for m in (re.match(r"^\[(\d+)\] ", l) for l in frag) if m]
        if frag[-1].rstrip().endswith((".", "]")) or not nums:
            sys.exit("FAIL: case 5 layout but the [1] block before the data-availability text is not a fragment")
        end = [i for i in range(b[0], len(L)) if L[i].rstrip().endswith("does not reproduce.")]
        if len(end) != 1: sys.exit("FAIL: case 5 layout but the data-availability text's last sentence not found once")
        c = end[0] + 1
        while c < len(L) and not L[c].strip():
            c += 1
        nxt = [i for i in range(c, len(L)) if L[i].startswith("[")]
        if c == len(L) or L[c].startswith("[") or not nxt or not L[nxt[0]].startswith("[%d] " % (nums[-1] + 1)) \
                or nxt[0] - c > 4:
            sys.exit("FAIL: case 5 layout but the rest of [%d] is not the block between the data-availability text "
                     "and [%d]" % (nums[-1], nums[-1] + 1))
        s1 = k
        while s1 < len(L) and not L[s1].strip():
            s1 += 1
        L[c:c] = frag
        del L[r[0]:s1]
        r = [i for i, l in enumerate(L) if l.startswith("[1] ")]
        h = [i for i, l in enumerate(L) if l.strip() == "DATA AVAILABILITY"]
        a = [i for i, l in enumerate(L) if l.strip() == "ACKNOWLEDGMENTS"]
        b = [i for i, l in enumerate(L) if l.startswith(first)]
        assert len(r) == 1 and b[0] < r[0], (b, r)
        assert sorted(" ".join(L).split()) == words0, "word multiset changed"
        print("moved references [1] to part of [%d] (%d lines) out of the acknowledgments, to before the rest of [%d]"
              % (nums[-1], len(frag), nums[-1]))
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
if len(a) == 1 and a[0] < h[0]:  # case 3: the DA text's continuation precedes its heading
    e = [i for i in range(a[0], h[0]) if L[i].rstrip().endswith("responsibility for the content.")]
    if len(e) == 1:
        cont = L[e[0] + 1:h[0]]
        body = [l for l in cont if l.strip()]
        if body and body[-1].rstrip().endswith("does not reproduce."):
            b = [i for i, l in enumerate(L) if l.startswith(first)]
            if len(b) != 1 or b[0] < h[0]:
                sys.exit("FAIL: case 3 layout but the data-availability section's first sentence not found once after its heading")
            j = b[0]
            while j + 1 < len(L) and L[j + 1].strip():
                j += 1
            head = L[h[0]:j + 1]
            del L[e[0] + 1:j + 1]
            L[e[0] + 1:e[0] + 1] = [""] + head + [l for l in cont if l.strip()] + [""]
            h2 = [i for i, l in enumerate(L) if l.strip() == "DATA AVAILABILITY"][0]
            b2 = [i for i, l in enumerate(L) if l.startswith(first)][0]
            c2 = [i for i, l in enumerate(L) if l.rstrip().endswith("does not reproduce.")][0]
            assert e[0] < h2 < b2 < c2, (e[0], h2, b2, c2)
            open(p, "w", encoding="utf-8").write("\n".join(L))
            print("moved the data-availability text's continuation (%d lines) after its first sentence" % len(body))
            sys.exit(0)
if not r or h[0] < r[0]: print("data-availability heading in reading order"); sys.exit(0)
b = [i for i, l in enumerate(L) if l.startswith(first)]
if len(b) != 1: sys.exit("FAIL: heading out of order and the section's first sentence not found once")
if h[0] < b[0]:  # case 1 is a heading emitted after its text; this is some other layout
    sys.exit("FAIL: a reference line precedes the DATA AVAILABILITY heading, which already precedes its text: no case describes this layout")
del L[h[0]]; L[b[0]:b[0]] = ["DATA AVAILABILITY", ""]
assert sorted(" ".join(L).split()) == words0, "word multiset changed"
open(p, "w", encoding="utf-8").write("\n".join(L)); print("moved DATA AVAILABILITY heading back before its text")
