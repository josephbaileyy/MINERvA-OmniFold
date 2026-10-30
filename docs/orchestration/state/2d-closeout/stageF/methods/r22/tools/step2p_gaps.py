"""Compose r22 Step 2's paper gap list (STEP2-PAPER.md section 1) from G1 and G1b.

usage: python3 -I step2p_gaps.py R22_DIR
In scope: G1's 13 paper gaps in step2/gaps-ws.tsv, and the G1b gaps that both classifications call WORDING or
STRUCTURE (G1B-RULES.md section 5). Ids are prefixed G1: or G1b:, since the two runs number their gaps alike.
Held: every out-of-scope paper gap of either run with a located quote (G1's other paper gaps, G1b's other gaps).
Its quoted sentence must still print in NEW (STEP2-PLAN.md section 3, step 2), so an in-scope gap whose own quote is
a held sentence may act only on its other ("pattern") passages; the Joseph pairs (G1 paper-s-06, paper-s-09) are
written as pinned pairs and leave their held twins to the pair.
Writes step2p/gaps.tsv (in scope, with a `held_overlap` column) and step2p/held.tsv (held quotes)."""
import csv
import re
import sys
from pathlib import Path

R = Path(sys.argv[1])
ws = {r["id"]: r for r in csv.DictReader(open(R / "step2/gaps-ws.tsv"), delimiter="\t")}
g1 = [r for r in csv.DictReader(open(R / "gap/gaps.tsv"), delimiter="\t") if r["input"] == "paper"]
g1b = list(csv.DictReader(open(R / "g1b/gaps.tsv"), delimiter="\t"))
lane = {r["id"]: r["class"] for r in csv.DictReader(open(R / "g1b/class-lane.tsv"), delimiter="\t")}
indep = {r["id"]: r["class"] for r in csv.DictReader(open(R / "g1b/class-indep.tsv"), delimiter="\t")}
WS = {"WORDING", "STRUCTURE"}
rows = []
for r in g1:
    w = ws.get(r["id"])
    rows.append(dict(id="G1:" + r["id"], run="G1", model=r["model"], located=r["located"], quote=r["quote"],
                     problem=r["problem"], change=r["change"], lane=w["lane_class"] if w else "",
                     indep=w["indep_class"] if w else "", inscope=w is not None,
                     scope=w["scope"] if w else "", joseph_pair=w["joseph_pair"] if w else "",
                     ledger=w["ledger"] if w else ""))
for r in g1b:
    i = r["id"]
    rows.append(dict(id="G1b:" + i, run="G1b", model=r["model"], located=r["located"], quote=r["quote"],
                     problem=r["problem"], change=r["change"], lane=lane[i], indep=indep[i],
                     inscope=lane[i] in WS and indep[i] in WS, scope="WS" if lane[i] in WS and indep[i] in WS else "",
                     joseph_pair="", ledger=""))


def key(s):
    return re.sub(r"\W+", " ", s).strip().lower()


def overlap(a, b):
    ka, kb = key(a), key(b)
    return kb[:60] in ka or ka[:60] in kb


held = [r for r in rows if not r["inscope"] and r["located"] != "UNVERIFIED"]
cols = ["id", "run", "model", "lane", "indep", "scope", "joseph_pair", "held_overlap", "ledger", "quote", "problem",
        "change"]
with open(R / "step2p/gaps.tsv", "w", newline="") as f:
    w = csv.DictWriter(f, cols, delimiter="\t", extrasaction="ignore")
    w.writeheader()
    for r in rows:
        if r["inscope"]:
            w.writerow({**r, "held_overlap": ",".join(h["id"] for h in held if overlap(r["quote"], h["quote"]))})
with open(R / "step2p/held.tsv", "w", newline="") as f:
    w = csv.DictWriter(f, ["id", "lane", "indep", "quote"], delimiter="\t", extrasaction="ignore")
    w.writeheader()
    for r in held:
        w.writerow(r)
n_in = sum(r["inscope"] for r in rows)
print(f"in scope {n_in} (G1 {sum(r['inscope'] for r in rows if r['run'] == 'G1')}, "
      f"G1b {sum(r['inscope'] for r in rows if r['run'] == 'G1b')}); held {len(held)}; "
      f"UNVERIFIED skipped {sum(r['located'] == 'UNVERIFIED' for r in rows)}")
