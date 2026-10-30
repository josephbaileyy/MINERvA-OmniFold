"""List, for each held sentence that paper pass 2 may reword, the out-of-scope gap whose change must NOT be made.

usage: python3 -I step2p_pass2_oos.py R22_DIR
STEP2-PAPER.md section 5, rule (a): a held-for-facts sentence may be reworded only if its out-of-scope gap's own change
is not made. This writes step2p/pass2/oos-changes.tsv: the held id (check_held.py FACT_HELD), its quote, the gap's
problem and change, and both classifications with their reasons (G1: gap/class-*-after522.tsv, as step2_gaps.py; G1b:
g1b/class-*.tsv)."""
import csv
import sys
from pathlib import Path

R = Path(sys.argv[1])
src = (R / "tools" / "check_held.py").read_text()
FACT_HELD = eval(src.split("FACT_HELD = ", 1)[1].split("\napplied", 1)[0])
gaps = {"G1:" + r["id"]: r for r in csv.DictReader(open(R / "gap/gaps.tsv"), delimiter="\t")}
gaps |= {"G1b:" + r["id"]: r for r in csv.DictReader(open(R / "g1b/gaps.tsv"), delimiter="\t")}
cls = {}
for run, tmpl in (("G1", "gap/class-{}-after522.tsv"), ("G1b", "g1b/class-{}.tsv")):
    for side in ("lane", "indep"):
        for r in csv.DictReader(open(R / tmpl.format(side)), delimiter="\t"):
            cls.setdefault(f"{run}:{r['id']}", {})[side] = f"{r['class']} [{r['item']}]: {r['reason']}"
out = R / "step2p" / "pass2" / "oos-changes.tsv"
with open(out, "w", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["held_id", "quote", "problem", "change_not_made", "lane", "indep"])
    for i in sorted(FACT_HELD):
        g, c = gaps[i], cls.get(i, {})
        w.writerow([i, g["quote"], g["problem"], g["change"], c["lane"], c["indep"]])
print(f"wrote {out}: {len(FACT_HELD)} rows")
