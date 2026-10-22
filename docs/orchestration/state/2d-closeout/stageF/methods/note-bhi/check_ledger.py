#!/usr/bin/env python3
"""Run every probe of ledger.md (batch bhi) against the worktree, and the base copies for B: probes.

usage: check_ledger.py <worktree> [ledger.md] [--plant]
N:f::text  occurs in printed (comment-stripped, whitespace-collapsed) docs/analysis-note/<f>
X:f::text  does NOT occur there
B:f::text  occurs byte for byte (\\n = newline) in the raw <f>, in the worktree AND in base/<f> (protected text)
MP::text   occurs in printed docs/analysis-note/main_paper.tex
Every row needs at least one probe. --plant adds a false N:, X: and B: probe and requires all three to fail.
Exit 1 on any failure."""
import re, sys
from pathlib import Path

args = [a for a in sys.argv[1:] if not a.startswith("--")]
wt = Path(args[0]); ledger = Path(args[1]) if len(args) > 1 else Path(__file__).with_name("ledger.md")
D = wt / "docs/analysis-note"; BASE = Path(__file__).with_name("base")

def printed(path):
    src = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in path.read_text().splitlines())
    return re.sub(r"\s+", " ", src)

cache = {}
def text(key, raw=False, root=D):
    k = (key, raw, root)
    if k not in cache:
        cache[k] = (root / key).read_text() if raw else printed(root / key)
    return cache[k]

def run(rid, probe):
    m = re.match(r"(N|X|B):([\w.]+)::(.*)$|MP::(.*)$", probe, re.S)
    if not m:
        return f"{rid}: MALFORMED probe {probe!r}"
    if m.group(4) is not None:
        lit = re.sub(r"\s+", " ", m.group(4))
        return None if lit in text("main_paper.tex") else f"{rid}: NOT FOUND in main_paper.tex: {lit!r}"
    kind, f, lit = m.group(1), m.group(2), m.group(3)
    if kind == "B":
        lit = lit.replace("\\n", "\n") if "\\n" in lit else lit
        lit = lit.replace("\n", "\n")
        bad = [r for r, root in (("after", D), ("base", BASE)) if lit not in text(f, True, root)]
        return f"{rid}: PROTECTED text not byte-identical ({', '.join(bad)}) in {f}: {lit[:70]!r}" if bad else None
    lit = re.sub(r"\s+", " ", lit)
    found = lit in text(f)
    if kind == "N" and not found:
        return f"{rid}: NOT FOUND in {f}: {lit!r}"
    if kind == "X" and found:
        return f"{rid}: STILL PRINTED in {f}: {lit!r}"
    return None

rows = probes = 0; fails = []
for line in ledger.read_text().splitlines():
    if not line.startswith("| ") or line.startswith("| id ") or line.startswith("|---"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
    if len(cells) != 6:
        continue
    rid, probe = cells[0], cells[5]
    rows += 1
    ps = [p.strip().strip("`") for p in probe.split(" && ") if p.strip().strip("`")]
    if not ps:
        fails.append(f"{rid}: row without a probe")
    for p in ps:
        probes += 1
        r = run(rid, p)
        if r: fails.append(r)
if "--plant" in sys.argv:
    planted = [run("PLANT-N", "N:app_release.tex::2,375 inventoried AnaTuple input files"),
               run("PLANT-X", "X:app_release.tex::RC7's own verifier"),
               run("PLANT-B", "B:app_release.tex::RC7's own verifier, run on the packaged files in an empty directory, reproduces")]
    ok = all(planted)
    for r in planted: print("  planted ->", r)
    print(f"plant test: {'PASS (all 3 planted probes fail)' if ok else 'FAIL (a planted probe passed)'}")
    if not ok: fails.append("plant test")
for f in fails: print(f)
print(f"ledger rows {rows}, probes {probes}, failures {len(fails)}")
sys.exit(1 if fails else 0)
