#!/usr/bin/env python3
"""Score the figure diagnosis's replies under rules fixed before any rating (PLAN.md sections 3 and 5).

usage: python3 -I fig_score.py <data-dir> <runs-dir> <probe-key-file>
Rules:
  1. Vision probe: a rater is usable only if both of its probe replies give the key's digits exactly.
  2. Degraded control: a usable rater's scores are used only if, in BOTH of its ctl-x replies, D1 <= 2 and D3 <= 2,
     and its CHANGES name the text size (font|text|label|tick ... size, or tiny, or small) and the colours
     (colou?r|palette|red|green|colormap).
  3. Noise floor: the largest per-dimension difference between dup-x and paper-fig-4, over a rater's reps. A difference
     between two items no larger than the floor is not read as a finding.
  4. An item's score on a dimension: the median over a rater's reps, then the mean over the raters that pass 1 and 2.
  5. Pairwise: per item and dimension, a rater favours ours only if it picks ours in both orders; anchor likewise;
     otherwise TIE. Reported per rater, not combined.
Writes <data-dir>/scores.tsv, pairwise.tsv and takeaways.tsv (each 30-second takeaway, for a fact check against the
item's own text), and prints the probe, control and noise-floor results."""
import csv
import re
import statistics as st
import sys
from pathlib import Path

D, RUNS, KEY = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]).read_text().strip()
jobs = list(csv.DictReader(open(D / "jobs.tsv"), delimiter="\t"))
DIMS = ("D1", "D2", "D3", "D4", "D5", "D6", "D7")
SIZE = re.compile(r"(font|text|label|tick|lettering|annotation)\w*[^.\n]{0,40}\bsize|\btiny\b|\bsmall\b|\benlarg|\bincrease", re.I)
COLOUR = re.compile(r"colou?r|palette|\bred\b|\bgreen\b|colormap|colour map", re.I)


def reply(job):
    f = RUNS / f"{job}.txt"
    return f.read_text(errors="replace") if f.exists() else ""


def parse_abs(t):
    s = {d: int(m.group(1)) for d in DIMS for m in [re.search(rf"^{d}:\s*([1-5])\b", t, re.M)] if m}
    take = re.search(r"^TAKEAWAY:\s*(.+)$", t, re.M)
    ch = t.split("CHANGES:", 1)[1].split("END")[0] if "CHANGES:" in t else ""
    return s, take.group(1).strip() if take else "", ch


raters = sorted({j["rater"] for j in jobs})
usable = []
for m in raters:
    got = [re.search(r"NUMBER:\s*([0-9]+)", reply(f"probe.{m}.r{k}")) for k in (1, 2)]
    ok = all(g and g.group(1) == KEY for g in got)
    print(f"probe {m}: {'PASS' if ok else 'FAIL'} ({[g.group(1) if g else None for g in got]})")
    if not ok:
        continue
    ctl = [parse_abs(reply(f"abs.ctl-x.{m}.{r}")) for r in ("r1", "r2")]
    cok = all(s.get("D1", 9) <= 2 and s.get("D3", 9) <= 2 and SIZE.search(ch) and COLOUR.search(ch) for s, _, ch in ctl)
    print(f"control {m}: {'PASS' if cok else 'FAIL'} "
          f"({[(s.get('D1'), s.get('D3'), bool(SIZE.search(ch)), bool(COLOUR.search(ch))) for s, _, ch in ctl]})")
    if cok:
        usable.append(m)
floor = {}
for m in usable:
    a = [parse_abs(reply(f"abs.dup-x.{m}.{r}"))[0] for r in ("r1", "r2")]
    b = [parse_abs(reply(f"abs.paper-fig-4.{m}.{r}"))[0] for r in ("r1", "r2")]
    floor[m] = max((abs(x.get(d, 0) - y.get(d, 0)) for x in a for y in b for d in DIMS if d in x and d in y), default=0)
    print(f"noise floor {m}: {floor[m]}")
items = sorted({j["item"] for j in jobs if j["kind"] == "abs"})
rows, takes = [], []
for i in items:
    row = {"item": i}
    for d in DIMS:
        per = []
        for m in usable:
            v = [parse_abs(reply(j["job"]))[0].get(d) for j in jobs
                 if j["kind"] == "abs" and j["item"] == i and j["rater"] == m]
            v = [x for x in v if x is not None]
            if v:
                per.append(st.median(v))
                row[f"{d}.{m}"] = st.median(v)
        row[d] = round(st.mean(per), 2) if per else ""
    rows.append(row)
    for j in jobs:
        if j["kind"] == "abs" and j["item"] == i and j["rater"] in usable:
            takes.append(dict(item=i, job=j["job"], takeaway=parse_abs(reply(j["job"]))[1], verdict=""))
pair = []
for i in sorted({j["item"] for j in jobs if j["kind"] == "pair"}):
    for m in usable:
        r = {}
        for o in ("AB", "BA"):
            t = reply(f"pair.{i}.{m}.{o}")
            for d in DIMS + ("OVERALL",):
                mm = re.search(rf"^{d}:\s*(A|B|EQUAL)\b", t, re.M)
                pick = mm.group(1) if mm else None
                r.setdefault(d, []).append(None if pick is None else "EQUAL" if pick == "EQUAL" else
                                           "ours" if (pick == "A") == (o == "AB") else "anchor")
        pair.append({"item": i, "rater": m, **{d: (v[0] if v[0] == v[1] and v[0] in ("ours", "anchor") else "TIE")
                                               for d, v in r.items()}})
for name, data in (("scores", rows), ("pairwise", pair), ("takeaways", takes)):
    if data:
        cols = list(dict.fromkeys(k for r in data for k in r))
        with open(D / f"{name}.tsv", "w", newline="") as f:
            w = csv.DictWriter(f, cols, delimiter="\t", lineterminator="\n")
            w.writeheader()
            w.writerows(data)
print(f"usable raters: {usable}; items scored: {len(rows)}; pairwise rows: {len(pair)}")
