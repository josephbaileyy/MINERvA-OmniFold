"""Check that every held paper sentence still prints in NEW's paper (STEP2-PAPER.md section 1; STEP2-PLAN.md section 3).

usage: python3 -I check_held.py R22_DIR ANALYZE_PY NEW_MANUSCRIPT [--pair-applied ID ...] [--self-test BASE_MANUSCRIPT]
The held quotes are step2p/held.tsv (written by tools/step2p_gaps.py): every out-of-scope paper gap of G1 and G1b
with a located quote. Each must still locate in NEW_MANUSCRIPT (the blinded rater copy, make_rater_copy.sh's
.blind.txt) EXACTLY, after analyze.py's key() normalization (case, Unicode and non-alphanumerics folded). The note
round's gapped locate() is not used: it accepts a quote split into up to four pieces, so it passes a held sentence with
a word changed (this script's self-test showed it), and a held sentence must stay as it is. A held gap that a pinned Joseph pair replaces is
exempt only when that pair is applied and named with --pair-applied (G1b:paper-s-05 is the Data availability
sentence of the A1 pair G1:paper-s-09). --self-test: every held quote locates in BASE_MANUSCRIPT, and a copy with the
quote's longest word replaced fails. Exit 1 on any failure."""
import ast
import csv
import sys
from pathlib import Path

R, AN, NEW = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
args = sys.argv[4:]
EXEMPT_BY_PAIR = {"G1:paper-s-09": {"G1b:paper-s-05"}}
applied = set()
if "--pair-applied" in args:
    i = args.index("--pair-applied") + 1
    while i < len(args) and not args[i].startswith("--"):
        applied.add(args[i])
        i += 1
exempt = set().union(*(EXEMPT_BY_PAIR.get(p, set()) for p in applied)) if applied else set()
ns = {}
for node in ast.parse(AN.read_text()).body:
    if isinstance(node, ast.FunctionDef) and node.name == "key":
        exec(compile(ast.Module([node], []), str(AN), "exec"), ns)
exec("import unicodedata, re", ns)
held = list(csv.DictReader(open(R / "step2p" / "held.tsv"), delimiter="\t"))


def run(text):
    dk = ns["key"](text)
    return [f"{g['id']}: held quote no longer prints exactly: {g['quote'][:90]!r}" for g in held
            if g["id"] not in exempt and ns["key"](g["quote"]) not in dk]


if "--self-test" in args:
    base = Path(args[args.index("--self-test") + 1]).read_text(encoding="utf-8")
    f0 = run(base)
    g = next(x for x in held if len(x["quote"]) > 60)
    word = max(g["quote"].split(), key=len).strip(".,;:()")  # the quote's longest word, replaced wherever it prints
    f1 = run(base.replace(word, "@@"))
    ok = not f0 and len(f1) >= 1
    print(f"  base: {len(held)} held quotes, {len(f0)} failures (want 0) {f0[:2]}")
    print(f"  one quote mutated ({g['id']}): {len(f1)} failure(s) (want >= 1)")
    print("SELF-TEST ::", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
fails = run(NEW.read_text(encoding="utf-8"))
for f in fails:
    print("  FAIL", f)
print(f"held quotes checked {len(held) - len(exempt)}, exempt by applied pair {sorted(exempt)}, failures {len(fails)}")
sys.exit(1 if fails else 0)
