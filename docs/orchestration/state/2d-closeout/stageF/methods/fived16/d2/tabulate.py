"""Tabulate the d2 rater runs through the KEY files: each run's choice and ranking per item, as option ids.

usage: python3 -I tabulate.py <raters-dir>     (raters/inputs/KEY-*.json, raters/runs/{A,B}-{fwd,rev}-{sol2,gemini}.txt)
A label may be written bare ("X") or with its noun ("Form X", "Candidate X"). An item a run does not answer in the
format prints as ??, and the run is reported, not guessed."""
import json
import re
import sys
from collections import Counter
from pathlib import Path

G = Path(sys.argv[1])
ITEMS = {"A": ["A1", "A2"], "B": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B0"]}
LABEL = r"(?:Form |Candidate )?([XYZ])\b"
rows, tally = [], {}
for b, items in ITEMS.items():
    for o in ("fwd", "rev"):
        key = json.loads((G / f"inputs/KEY-{o}.json").read_text())
        for r in ("sol2", "gemini"):
            f = G / f"runs/{b}-{o}-{r}.txt"
            if not f.exists():          # a battery not run in this directory (raters-v2 re-reads battery A only)
                continue
            t = f.read_text()
            cells = []
            for it in items:
                m = re.search(re.escape(it) + r"[^\n]*CHOICE: *" + LABEL, t)
                if not m:
                    cells.append(f"{it} ??")
                    continue
                choice = key[it][m.group(1)]
                rk = re.search(re.escape(it) + r"[^\n]*\n(?:.*\n)*?RANKING: *([^\n]*)", t)
                rank = [key[it][x] for x in re.findall(LABEL, rk.group(1))] if rk else []
                st = re.search(re.escape(it) + r"[^\n]*\n(?:.*\n)*?STRENGTH: *(\d)", t) if b == "B" else None
                cells.append(f"{it} {choice}" + (f" [{'>'.join(rank)}]" if rank else "") + (f" s{st.group(1)}" if st else ""))
                tally.setdefault(it, Counter())[choice] += 1
            if b == "A":
                m = re.search(r"P02: VERDICT: *(\w+)", t)
                cells.append("P02 " + (m.group(1) if m else "??"))
                tally.setdefault("P02", Counter())[m.group(1) if m else "??"] += 1
            rows.append(f"| {b}-{o} | {r} | " + "; ".join(cells) + " |")
print("| battery-order | rater | choices (option ids) |\n|---|---|---|")
print("\n".join(rows))
print("\n| item | tally over the four runs |\n|---|---|")
for it, c in tally.items():
    print(f"| {it} | " + ", ".join(f"{k} {v}" for k, v in c.most_common()) + " |")
