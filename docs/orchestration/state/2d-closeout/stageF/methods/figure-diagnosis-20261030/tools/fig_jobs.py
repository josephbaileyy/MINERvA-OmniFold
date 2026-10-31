#!/usr/bin/env python3
"""Write the figure diagnosis's job list (PLAN.md sections 4, 5 and 7), before any rating.

usage: python3 -I fig_jobs.py <data-dir> <png-dir> <caption-dir> <raters, comma-separated>
Writes <data-dir>/jobs.tsv: one row per rating call, with its prompt, its image files (in order) and its caption file.
  - absolute (F1 for a figure, F1T for a table): our 32 items and the two controls, twice per rater (r1, r2); the 14
    matched anchor items and the 5 calibration anchors, once per rater;
  - pairwise (F2): each of our 32 items against its matched anchor (match.tsv), in both orders (AB: A = ours), per
    rater.
A figure is given as its colour, greyscale and (where rendered) deuteranopia images; a table as its colour image.
The controls are ctl-x (paper-fig-3 degraded, figdiag.py control) and dup-x (paper-fig-4 again, under a second id).
Neither the file names given to a rater (run_vision.sh renames them) nor the order of items reveals whose item it is:
the absolute jobs are shuffled with a fixed seed.
Caption files are written by figdiag.py captions into <caption-dir>."""
import csv
import random
import sys
from pathlib import Path

D, PNG, CAP = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
RATERS = sys.argv[4].split(",")
items = {r["id"]: r for r in csv.DictReader(open(D / "items.tsv"), delimiter="\t")}
match = list(csv.DictReader(open(D / "match.tsv"), delimiter="\t"))
cal = [r["anchor"] for r in csv.DictReader(open(D / "calibration.tsv"), delimiter="\t")]
ours = [r["ours"] for r in match]
assert sorted(ours) == sorted(i for i, r in items.items() if r["set"].startswith("ours")), "match.tsv must cover ours"
CONTROLS = {"ctl-x": "paper-fig-3", "dup-x": "paper-fig-4"}   # control id -> the item whose kind and caption it takes


def kind(i):
    return items[CONTROLS.get(i, i)]["kind"]


def images(i):
    stem = "ctl-x" if i == "ctl-x" else CONTROLS.get(i, i)
    if kind(i) == "table":
        return [PNG / f"{stem}.png"]
    out = [PNG / f"{stem}.png", PNG / f"{stem}.grey.png"]
    if (PNG / f"{stem}.deuteranopia.png").exists():
        out.append(PNG / f"{stem}.deuteranopia.png")
    return out


def caption(i):
    return CAP / f"{CONTROLS.get(i, i)}.txt"


rows = []
absolute = [(i, ("r1", "r2")) for i in ours + list(CONTROLS)] + \
           [(i, ("r1",)) for i in sorted({r["anchor"] for r in match}) + cal]
for i, reps in absolute:
    for m in RATERS:
        for rep in reps:
            rows.append(dict(job=f"abs.{i}.{m}.{rep}", kind="abs", item=i, other="", order="", rater=m, rep=rep,
                             prompt="F1T" if kind(i) == "table" else "F1",
                             images=" ".join(str(p) for p in images(i)), caption=str(caption(i))))
random.Random(30).shuffle(rows)
for r in match:
    for m in RATERS:
        for order in ("AB", "BA"):
            a, b = (r["ours"], r["anchor"]) if order == "AB" else (r["anchor"], r["ours"])
            rows.append(dict(job=f"pair.{r['ours']}.{m}.{order}", kind="pair", item=r["ours"], other=r["anchor"],
                             order=order, rater=m, rep="r1", prompt="F2",
                             images=" ".join(str(p) for p in images(a)[:1] + images(b)[:1]),
                             caption=f"{caption(a)} {caption(b)}"))
missing = [p for r in rows for p in r["images"].split() + r["caption"].split() if not Path(p).exists()]
assert not missing, missing[:5]
with open(D / "jobs.tsv", "w", newline="") as f:
    w = csv.DictWriter(f, list(rows[0]), delimiter="\t", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
n_abs = sum(r["kind"] == "abs" for r in rows)
print(f"jobs: {len(rows)} ({n_abs} absolute, {len(rows) - n_abs} pairwise) for raters {RATERS} -> {D / 'jobs.tsv'}")
