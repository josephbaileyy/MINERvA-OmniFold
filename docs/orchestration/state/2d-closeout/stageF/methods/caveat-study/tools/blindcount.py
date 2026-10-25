"""blindcount.py ID START_REGEX -- blind a pdftotext dump the way the rater copies are blinded, and count words.
Keep: from the first line matching START_REGEX (the abstract's first line) to the end of the body, plus appendices.
Drop: everything before START; the acknowledgments (heading to the next Appendix heading or the reference list);
the reference list (from its first entry to the next Appendix heading, or to the end); a supplement (from a second
'(Dated' line, which revtex prints at a supplement's head); arXiv stamps, DOI lines and bare page numbers.
Writes blind/ID.txt and prints the word counts and the cuts."""
import re, sys
i_d, start = sys.argv[1], sys.argv[2]
markers_after = int(sys.argv[3]) if len(sys.argv) > 3 else 0  # ignore ack/refs headings before this line (a table of contents)
L = open(f"txt/{i_d}.txt", encoding="utf-8", errors="replace").read().split("\n")
s = next(i for i, l in enumerate(L) if re.search(start, l.lstrip("\f")))
APP = re.compile(r"^(Appendix|APPENDIX)\b")
ACK = re.compile(r"^(ACKNOWLEDG|Acknowledg)")
REF = re.compile(r"^(\[1\]( |$)|References$|REFERENCES$)")
DATED = [i for i, l in enumerate(L) if l.startswith("(Dated") and i > s]
end = DATED[0] if DATED else len(L)
keep, mode, cuts = [], "body", []
for i in range(s, end):
    l = L[i]
    if mode != "body" and APP.match(l):
        mode = "body"; cuts.append(f"resume at {i+1}: {l[:40]}")
    elif mode == "body" and i >= markers_after and ACK.match(l):
        mode = "ack"; cuts.append(f"ack from {i+1}")
    elif mode in ("body", "ack") and i >= markers_after and REF.match(l):
        mode = "refs"; cuts.append(f"refs from {i+1}")
    if mode != "body": continue
    if re.match(r"^\s*arXiv:\d{4}\.\d{4,5}", l) or re.match(r"(?i)^\s*(doi|https?://doi\.org)", l) or re.match(r"^\s*\d{1,3}\s*$", l):
        continue
    keep.append(l)
open(f"blind/{i_d}.txt", "w").write("\n".join(keep))
words = sum(1 for w in " ".join(keep).split() if re.search(r"[A-Za-z0-9]", w))
print(f"{i_d}\tstart={s+1}\tsupp_cut={DATED[0]+1 if DATED else '-'}\twords={words}\t{'; '.join(cuts)}")
