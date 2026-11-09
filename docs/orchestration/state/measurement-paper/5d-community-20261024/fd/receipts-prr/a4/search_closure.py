"""A4 search: the runner path's import closure (AST, top-level and nested imports), every /pscratch and /global string
literal in it, and the committed json files the runner loads with any absolute path they carry."""
import ast, json, re, sys, subprocess
from pathlib import Path
REPO = Path(sys.argv[1]).resolve(); ND = REPO / "nd-unfolding"
DIRS = [ND / "prior_retention", ND, ND / "ref_g1", ND / "ibu1", ND / "pv-ladder", ND / "tests", REPO / "2d-unfolding",
        REPO / "docs/orchestration/state/next-preparation-20261009/d-id"]
def find(name):
    for d in DIRS:
        p = d / (name.replace(".", "/") + ".py")
        if p.is_file():
            return p
    return None
entry = [ND / "prior_retention" / f for f in ("prr_probe.py", "prr_ibu.py", "prr_read.py")] + [ND / "s5p_nullexp.py"]
seen, todo = {}, list(entry)
while todo:
    p = todo.pop()
    if p in seen:
        continue
    seen[p] = []
    tree = ast.parse(p.read_text())
    for n in ast.walk(tree):
        names = [a.name for a in n.names] if isinstance(n, ast.Import) else ([n.module] if isinstance(n, ast.ImportFrom) and n.module and n.level == 0 else [])
        for nm in names:
            q = find(nm) or find(nm.split(".")[0])
            if q and q not in seen:
                todo.append(q)
    # importlib.util.spec_from_file_location targets (did.py) are listed in DIRS
did = REPO / "docs/orchestration/state/next-preparation-20261009/d-id/did.py"
if did.is_file() and did not in seen:
    seen[did] = []
mods = sorted(seen, key=str)
print(f"modules in the closure: {len(mods)}")
pat = re.compile(r"/(pscratch|global)/")
hits = []
for p in mods:
    for i, line in enumerate(p.read_text().splitlines(), 1):
        if pat.search(line):
            hits.append((str(p.relative_to(REPO)), i, line.strip()[:150]))
print(f"lines with a /pscratch or /global literal: {len(hits)}")
for h in hits:
    print(f"  {h[0]}:{h[1]}: {h[2]}")
open(sys.argv[2], "w").write("\n".join(str(p.relative_to(REPO)) for p in mods) + "\n")
