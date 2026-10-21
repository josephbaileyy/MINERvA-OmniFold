#!/usr/bin/env python3
"""Run every probe of ledger.md against the printed (comment-stripped, whitespace-collapsed) LaTeX source.

usage: check_ledger.py <worktree> [ledger.md]
P::text   must occur in docs/analysis-note/paper_body.tex (after the rewrite)
MP::text  must occur in docs/analysis-note/main_paper.tex
N:f::text must occur in docs/analysis-note/<f>
Also: every MOVE/ADDED row must carry at least one N: probe; every KEEP row at least one P:/MP: probe.
Exit 1 on any failure."""
import re, sys
from pathlib import Path

wt = Path(sys.argv[1]); ledger = Path(sys.argv[2] if len(sys.argv) > 2 else Path(__file__).with_name("ledger.md"))
D = wt / "docs/analysis-note"

def printed(path):
    src = path.read_text()
    src = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in src.splitlines())
    return re.sub(r"\s+", " ", src)

cache = {}
def text(key):
    if key not in cache:
        cache[key] = printed(D / key)
    return cache[key]

rows = fails = probes = 0
for line in ledger.read_text().splitlines():
    if not line.startswith("| ") or line.startswith("| id ") or line.startswith("|---"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
    if len(cells) != 6:
        continue  # the ADD summary table has four columns
    rid, fact, before, disp, after, probe = cells
    rows += 1
    kinds = set()
    for p in probe.split(" && "):
        p = p.strip().strip("`")
        m = re.match(r"(P|MP|N:[\w.]+)::(.*)$", p)
        if not m:
            print(f"{rid}: MALFORMED probe {p!r}"); fails += 1; continue
        where, lit = m.group(1), re.sub(r"\s+", " ", m.group(2))
        key = "paper_body.tex" if where == "P" else "main_paper.tex" if where == "MP" else where[2:]
        kinds.add("N" if where.startswith("N:") else "P")
        probes += 1
        if lit not in text(key):
            print(f"{rid}: NOT FOUND in {key}: {lit!r}"); fails += 1
    moved = disp.startswith("MOVE") or disp.startswith("ADDED")
    if moved and "N" not in kinds:
        print(f"{rid}: MOVE/ADD row without a note probe"); fails += 1
    if disp.startswith("KEEP") and "P" not in kinds:
        print(f"{rid}: KEEP row without a paper probe"); fails += 1
print(f"ledger rows {rows}, probes {probes}, failures {fails}")
sys.exit(1 if fails else 0)
