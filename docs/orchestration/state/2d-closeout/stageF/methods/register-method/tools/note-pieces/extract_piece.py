"""Extract one blinded chapter-sized piece from an anchor's pdftotext dump.

usage: python3 -I extract_piece.py IN OUT START END HEAD_REGEX
Lines [START, END) (1-based). HEAD_REGEX must match one of the first three lines (asserted). Drops: bare page
numbers before/after a form feed, arXiv stamp lines, DOI lines. Prints word count and page range.
"""
import re, sys
inp, out, a, b, rx = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
L = open(inp, encoding="utf-8").read().split("\n")
page, pg = 1, []
for l in L:
    page += l.count("\f"); pg.append(page)
seg = L[a - 1:b - 1]
assert any(re.search(rx, s.replace("\f", "").strip()) for s in seg[:3]), seg[:3]
t = "\n".join(seg)
t = re.sub(r"\n[ \t]*\d{1,3}[ \t]*\n(?=\s*\f)", "\n", t)
t = re.sub(r"\f[ \t]*\d{1,3}[ \t]*\n", "\f\n", t)
t = re.sub(r"(?m)^\s*arXiv:\d{4}\.\d{4,5}(v\d+)?\b.*$", "", t)
t = re.sub(r"(?mi)^\s*(doi|https?://doi\.org)\S*.*$", "", t)
t = t.replace("\f", "\n")
if len(seg) and t and t.split("\n", 1)[0].strip() == "" :
    pass
t = re.sub(r"\n{3,}", "\n\n", t).strip() + "\n"
open(out, "w", encoding="utf-8").write(t)
nz = [i for i in range(a - 1, b - 1) if L[i].strip()]
print(f"{out}: lines {a}-{b - 1}, pages {pg[nz[0]]}-{pg[nz[-1]]}, words {len(t.split())}")
