"""Write r22's gap table for classification: one row per gap of every real (non-control) run in gap/gaps.json.

usage: python3 -I gap_table.py R22_DIR [SUB]      writes R22_DIR/SUB/gaps.tsv (SUB: gap, the default, or g1b)
Columns: id (input-model-n, model s = sol2, g = gemini), input, model, n, share, located (exact/gapped/UNVERIFIED),
scope, quote, problem, change. Control runs are left out (RULES.md §5)."""
import csv
import json
import sys
from pathlib import Path

R = Path(sys.argv[1])
SUB = sys.argv[2] if len(sys.argv) > 2 else "gap"
d = json.loads((R / SUB / "gaps.json").read_text())
with open(R / SUB / "gaps.tsv", "w", newline="") as fh:
    w = csv.writer(fh, delimiter="\t", lineterminator="\n")
    w.writerow(["id", "input", "model", "n", "share", "located", "scope", "quote", "problem", "change"])
    for k in sorted(d):
        r = d[k]
        if r["input"].endswith("-ctl"):
            continue
        for g in r["gaps"]:
            w.writerow([f"{r['input']}-{r['model'][0]}-{g['n']:02d}", r["input"], r["model"], g["n"], g["share"],
                        g["located"] or "UNVERIFIED", g["scope"].strip('"'), g["quote"], g["problem"], g["change"]])
