"""Check that every held note sentence still prints in NEW's note, exactly (STEP3-PLAN.md section 3).

usage: python3 -I check_held_note.py R22_DIR ANALYZE_PY NEW_PIECES_DIR [--self-test]
The held quotes are step3/held.tsv (tools/step3_gaps.py): every out-of-scope note gap of Step 1 that neither step2's
nor step3's scope carries. Each must still print in the same piece of NEW (B01.txt..B15.txt, cut by tools/split_base.py
from NEW's main_note.pdf) EXACTLY after analyze.py's key() normalization. The gapped locate() is not used, since it
passes a quote with a word changed (tools/check_held.py). A quote that matched only gapped at the base (held.tsv
base_match GAPPED) is checked gapped and listed. --self-test: every quote prints in the base pieces (step2/pieces/), and
a copy with one quote's longest word replaced fails. Exit 1 on any failure."""
import ast
import csv
import sys
from pathlib import Path

R, AN, NEW = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
ns = {}
for node in ast.parse(AN.read_text()).body:
    if isinstance(node, ast.FunctionDef) and node.name in ("key", "locate"):
        exec(compile(ast.Module([node], []), str(AN), "exec"), ns)
exec("import unicodedata, re", ns)
held = list(csv.DictReader(open(R / "step3" / "held.tsv"), delimiter="\t"))


def load(d):
    return {f"B{i:02d}": (d / f"B{i:02d}.txt").read_text(encoding="utf-8") for i in range(1, 16)}


def run(pieces):
    fails, gapped = [], []
    keys = {p: ns["key"](t) for p, t in pieces.items()}
    for g in held:
        if g["base_match"] == "GAPPED":
            gapped.append(g["id"])
            ns["doc_key"] = {g["piece"]: keys[g["piece"]]}
            ok = ns["locate"](g["piece"], g["quote"])
        else:
            ok = ns["key"](g["quote"]) in keys[g["piece"]]
        if not ok:
            fails.append(f"{g['id']} ({g['piece']}): held quote no longer prints exactly: {g['quote'][:90]!r}")
    return fails, gapped


if "--self-test" in sys.argv:
    base = load(R / "step2" / "pieces")
    f0, _ = run(base)
    g = next(x for x in held if len(x["quote"]) > 60 and x["base_match"] == "EXACT")
    word = max(g["quote"].split(), key=len).strip(".,;:()")
    f1, _ = run({**base, g["piece"]: base[g["piece"]].replace(word, "@@")})
    ok = not f0 and len(f1) >= 1
    print(f"  base pieces: {len(held)} held quotes, {len(f0)} failures (want 0) {f0[:2]}")
    print(f"  one quote mutated ({g['id']}): {len(f1)} failure(s) (want >= 1)")
    print("SELF-TEST ::", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
fails, gapped = run(load(NEW))
for f in fails:
    print("  FAIL", f)
print(f"held quotes checked {len(held)} ({len(held) - len(gapped)} exact, gapped {gapped}), failures {len(fails)}")
sys.exit(1 if fails else 0)
