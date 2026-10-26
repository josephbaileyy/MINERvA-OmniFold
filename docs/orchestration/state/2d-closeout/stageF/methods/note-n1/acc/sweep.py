"""Purity-scope sweep: every printed sentence of the note, paper and primer that mentions the background treatment.

usage: python3 -I sweep.py <docs/analysis-note dir> <out.tsv>
Builds come from the \\input closures of main_note.tex, main_paper.tex and main_primer.tex; comments are stripped;
sentences are split as check_ledger.py does, and each sentence is kept with its source file and first line number.
"""
import re, sys
from pathlib import Path
D = Path(sys.argv[1]); out = Path(sys.argv[2])
PATS = {
 "purity": r"purit",
 "(D-B)/D": r"\(D\s*-\s*B\)\s*/\s*D|D-B",
 "fixed before training": r"fixed\s+(\\emph\{)?before\}?\s+training",
 "default": r"\bdefault",
 "binned correction/subtraction": r"binned\s+(purity\s+)?(correction|subtraction|weight)",
 "reproduction measurement": r"reproduction\s+measurement",
 "negative-weight": r"negative[- ]weight",
 "refined": r"\brefined\b",
 "background subtraction/treatment": r"background[- ](subtraction|treatment|removal)",
 "does not use it": r"(do|does|did)\s+not\s+use\s+(it|the|this)",
 "improved removal (primer)": r"improved\s+removal|removal\s+of\s+background",
}
def closure(main):
    seen, order = set(), []
    def walk(name):
        f = D / (name if name.endswith(".tex") else name + ".tex")
        if not f.exists() or f in seen: return
        seen.add(f); order.append(f)
        for l in f.read_text().splitlines():
            s = re.sub(r"(?<!\\)%.*", "", l)
            for m in re.finditer(r"\\(?:input|include)\{([^}]*)\}", s): walk(m.group(1))
    walk(main); return order
rows = []
for build in ["main_note", "main_paper", "main_primer"]:
    for f in closure(build):
        lines = f.read_text().splitlines()
        # map each char of stripped text back to a line number
        buf, lmap = [], []
        for i, l in enumerate(lines, 1):
            s = re.sub(r"(?<!\\)%.*", "", l) + " "
            buf.append(s); lmap += [i] * len(s)
        text = "".join(buf)
        for m in re.finditer(r"(?:[^.?!]|\.(?=\d)|\.(?!\s+[A-Z\\$(0-9]))+[.?!]?", text):
            s = re.sub(r"\s+", " ", m.group(0)).strip()
            if not s: continue
            hits = [k for k, p in PATS.items() if re.search(p, s, re.I)]
            if hits:
                rows.append((build, f.name, lmap[min(m.start() + len(m.group(0)) - len(m.group(0).lstrip()), len(lmap) - 1)], ",".join(hits), s))
uniq = {}
for r in rows: uniq.setdefault((r[1], r[2], r[4]), r)
with out.open("w") as o:
    o.write("build\tfile\tline\tpatterns\tsentence\n")
    for r in uniq.values(): o.write("\t".join(map(str, r)) + "\n")
print(len(uniq), "sentences;", {b: sum(1 for r in uniq.values() if r[0] == b) for b in ["main_note", "main_paper", "main_primer"]})
