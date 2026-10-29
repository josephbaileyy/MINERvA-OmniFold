"""Cut note round n4's two scored pieces from the note's pdftotext dump, blinded as in the earlier rounds.

usage: python3 -I split_front.py NOTE_TXT OUTDIR

The pieces, as in rounds n1-n3:
  N01  Abstract, Executive summary, Sec. 1: "Abstract" up to "Contents", then the body's "Introduction and
       motivation" up to "The MINERvA experiment";
  N10b "Summary and outlook" up to "Acknowledgments".
The blinding is the n1-n3 splitter's (lane scratchpad xmodel/split_note_heads.py, copied here so that it survives):
the title block, the table of contents, author e-mail lines and the repository URL are removed, the deposit
placeholder clause is removed, and a bare page number before a form feed is dropped. Each heading must be found once,
in order."""
import json
import re
import sys
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
L = src.read_text(encoding="utf-8").split("\n")


def find(rx, lo=0):
    hits = [i for i in range(lo, len(L)) if re.match(rx, L[i].lstrip("\f").strip())]
    if not hits:
        sys.exit(f"FAIL: heading {rx!r} not found after line {lo + 1}")
    return hits[0]


a = find(r"^Abstract$")
t0 = find(r"^Contents$", a)
t1 = find(r"^Introduction and motivation$", t0)
n02 = find(r"^The MINERvA experiment", t1)
s0 = find(r"^Summary and outlook$", n02)
k0 = find(r"^Acknowledgments$", s0)
PIECES = [("N01", "Abstract, Executive summary, Sec. 1", [(a, t0), (t1, n02)]),
          ("N10b", "Summary and outlook", [(s0, k0)])]


def clean(lines):
    s = "\n".join(lines)
    s = re.sub(r"\n[ \t]*\d{1,3}[ \t]*\n(?=\s*\f)", "\n", s)
    s = re.sub(r"https?://\S*josephbaileyy\S*|github\.com/josephbaileyy\S*", "[repository]", s)
    s = s.replace(", identified at deposit: [snapshot identifier pending deposit]", "")
    return "\n".join(l for l in s.split("\n") if not re.search(r"@stanford\.edu", l))


out.mkdir(parents=True, exist_ok=True)
meta = []
for pid, title, ranges in PIECES:
    txt = clean([l for s, e in ranges for l in L[s:e]])
    (out / f"{pid}.txt").write_text(txt)
    meta.append({"id": pid, "title": title, "lines": [[s + 1, e + 1] for s, e in ranges],
                 "words": sum(1 for w in txt.split() if re.search(r"[A-Za-z0-9]", w))})
json.dump(meta, open(out / "pieces.json", "w"), indent=1)
for m in meta:
    print(m["id"], m["words"], m["title"])
