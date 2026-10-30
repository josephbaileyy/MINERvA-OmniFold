"""Count r22's gap classes (RULES.md §5, counting): per run, each class's share is the sum of its gaps' SHARE values,
rescaled to 100 when the run's shares do not sum to 100 (the raw sum is printed). Per document x rater: the paper's one
run; the note's mean over its valid pieces, equal weight (15 for sol2; 13 for gemini, whose B06 and B08 runs failed both
attempts), and sol2 also over the pieces gemini has. UNVERIFIED and UNRESOLVED are their own columns, so the shares of a
run sum to 100. PROTECTED-B2-DETAIL is set apart, and PROTECTED+DETAIL counts it under PROTECTED as the committed rule
does (director's ruling, 2026-10-29).

usage: python3 -I count_classes.py R22_DIR CLASS_TSV [--json OUT]"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

R, CF = Path(sys.argv[1]), Path(sys.argv[2])
CLASSES = ["PROTECTED", "PROTECTED-B2-DETAIL", "STRUCTURE", "WORDING", "UNRESOLVED", "UNVERIFIED"]
gaps = list(csv.DictReader(open(R / "gap" / "gaps.tsv"), delimiter="\t"))
cls = {r["id"]: r for r in csv.DictReader(open(CF), delimiter="\t")}
assert {g["id"] for g in gaps} <= set(cls), "class file misses rows of gaps.tsv"
COLS = CLASSES + ["PROTECTED+DETAIL"]
assert all(c["class"] in CLASSES for c in cls.values()), "unknown class"
runs = defaultdict(list)
for g in gaps:
    runs[(g["input"], g["model"])].append(g)
per_run = {}
for (inp, m), gs in sorted(runs.items()):
    raw = sum(float(g["share"]) for g in gs)
    sh = {c: 0.0 for c in COLS}
    n = {c: 0 for c in COLS}
    for g in gs:
        c = cls[g["id"]]["class"]
        for col in [c] + (["PROTECTED+DETAIL"] if c.startswith("PROTECTED") else []):
            sh[col] += float(g["share"]) * 100 / raw
            n[col] += 1
    per_run[f"{inp}|{m}"] = {"raw_sum": raw, "share": sh, "n": n}
out = {"per_run": per_run, "summary": {}}
pieces = [f"B{i:02d}" for i in range(1, 16)]
both = [i for i in pieces if f"{i}|sol2" in per_run and f"{i}|gemini" in per_run]
for label, inputs, m in [("paper|sol2", ["paper"], "sol2"), ("paper|gemini", ["paper"], "gemini"),
                         ("note|sol2", pieces, "sol2"), (f"note|sol2 ({len(both)})", both, "sol2"),
                         ("note|gemini", pieces, "gemini")]:
    rs = [per_run[f"{i}|{m}"] for i in inputs if f"{i}|{m}" in per_run]
    out["summary"][label] = {
        "runs": len(rs), "pieces": [i for i in inputs if f"{i}|{m}" in per_run],
        "share": {c: sum(r["share"][c] for r in rs) / len(rs) for c in COLS},
        "n": {c: sum(r["n"][c] for r in rs) for c in COLS},
        "raw_sums_not_100": [f"{i}|{m}" for i in inputs if f"{i}|{m}" in per_run
                             and abs(per_run[f"{i}|{m}"]["raw_sum"] - 100) > 1e-9]}
print(f"{'doc|rater':16s} runs " + " ".join(f"{c[:11]:>12s}" for c in COLS))
for k, s in out["summary"].items():
    print(f"{k:16s} {s['runs']:4d} " + " ".join(f"{s['share'][c]:6.1f} ({s['n'][c]:3d})" for c in COLS)
          + (f"  rescaled: {s['raw_sums_not_100']}" if s["raw_sums_not_100"] else ""))
if "--json" in sys.argv:
    Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(out, indent=1))
