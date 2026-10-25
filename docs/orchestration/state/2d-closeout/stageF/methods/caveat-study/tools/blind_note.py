"""blind_note.py IN OUT -- blind the analysis note's pdftotext dump: keep the abstract, the body and the appendices;
drop the title block, the table of contents, the acknowledgments and the references, e-mail lines and page numbers."""
import re, sys
L = open(sys.argv[1]).read().split("\n")
idx = lambda rx, lo=0: next(i for i in range(lo, len(L)) if re.match(rx, L[i].lstrip("\f")))
a = idx(r"Abstract$") + 1; t0 = idx(r"Contents$"); t1 = idx(r"Introduction and motivation$", t0 + 10)
k0 = idx(r"Acknowledgments$", t1); g = idx(r"Guide to the appendices$", k0); r = idx(r"References$", g)
keep = [l for l in L[a:t0] + L[t1:k0] + L[g:r] if not re.match(r"^\s*\d{1,3}\s*$", l) and "@stanford.edu" not in l]
open(sys.argv[2], "w").write("\n".join(keep))
w = sum(1 for x in " ".join(keep).split() if re.search(r"[A-Za-z0-9]", x))
print(f"ours-note\tabstract from {a+1}; TOC cut {t0+1}-{t1}; ack cut {k0+1}-{g}; refs from {r+1}\twords={w}")
