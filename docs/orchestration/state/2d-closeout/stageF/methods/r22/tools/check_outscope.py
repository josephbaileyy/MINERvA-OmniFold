"""Check that every out-of-scope Step 1 gap's quoted sentence still prints in NEW (STEP2-PLAN.md §3, step 2).

usage: python3 -I check_outscope.py R22_DIR ANALYZE_PY NEW_PIECES_DIR [--self-test]
NEW_PIECES_DIR holds B01.txt..B15.txt, cut from NEW's note PDF by tools/split_base.py. A gap is out of scope when it
is in gap/gaps.tsv and not in step2/gaps-ws.tsv. Each located out-of-scope quote must still locate, by analyze.py's
key() and locate() (exact or gapped), in the same piece of NEW. UNVERIFIED quotes (not located at the base) are
skipped and listed. --self-test runs on the base pieces (base/pieces/): every quote must locate there, and a copy of
one piece with one quoted passage removed must fail. Exit 1 on any failure."""
import ast
import csv
import re
import sys
from pathlib import Path

R, AN, NEW = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
ns = {}
for node in ast.parse(AN.read_text()).body:
    if isinstance(node, ast.FunctionDef) and node.name in ("key", "locate"):
        exec(compile(ast.Module([node], []), str(AN), "exec"), ns)
exec("import unicodedata, re", ns)
gaps = list(csv.DictReader(open(R / "gap" / "gaps.tsv"), delimiter="\t"))
inscope = {r["id"] for r in csv.DictReader(open(R / "step2" / "gaps-ws.tsv"), delimiter="\t")}
out = [g for g in gaps if g["id"] not in inscope and g["input"] != "paper"]


def run(pieces):
    fails, skipped, n = [], [], 0
    for g in out:
        if g["located"] == "UNVERIFIED":
            skipped.append(g["id"])
            continue
        n += 1
        ns["doc_key"] = {g["input"]: ns["key"](pieces[g["input"]])}
        if not ns["locate"](g["input"], g["quote"]):
            fails.append(f"{g['id']} ({g['input']}): out-of-scope quote no longer prints: {g['quote'][:90]!r}")
    return fails, skipped, n


def load(d):
    return {f"B{i:02d}": (d / f"B{i:02d}.txt").read_text(encoding="utf-8") for i in range(1, 16)}


if "--self-test" in sys.argv:
    base = load(R / "base" / "pieces")
    f0, sk, n = run(base)
    g = next(x for x in out if x["located"] != "UNVERIFIED" and len(x["quote"]) > 60)
    words = g["quote"].split()
    mutated = dict(base)
    t = base[g["input"]]
    i = t.find(words[0] + " " + words[1])
    mutated[g["input"]] = t[:i] + t[i:].replace(words[1], "@@", 1) if i >= 0 else t
    f1, _, _ = run(mutated)
    ok = not f0 and len(f1) >= 1
    print(f"  base pieces: {n} quotes, {len(f0)} failures (want 0); skipped UNVERIFIED {sk}")
    print(f"  one quote mutated ({g['id']}): {len(f1)} failure(s) (want >= 1)")
    print("SELF-TEST ::", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
fails, skipped, n = run(load(NEW))
for f in fails:
    print("  FAIL", f)
print(f"out-of-scope quotes checked {n}, skipped UNVERIFIED {len(skipped)} {skipped}, failures {len(fails)}")
sys.exit(1 if fails else 0)
