"""Compare two r22 class files row by row: python3 -I compare_classes.py R22_DIR A.tsv B.tsv [--tsv OUT]
Prints the agreement on class, a confusion table, and every disagreement with both reasons."""
import csv
import sys
from collections import Counter
from pathlib import Path

R = Path(sys.argv[1])
A = {r["id"]: r for r in csv.DictReader(open(sys.argv[2]), delimiter="\t")}
B = {r["id"]: r for r in csv.DictReader(open(sys.argv[3]), delimiter="\t")}
G = {r["id"]: r for r in csv.DictReader(open(R / "gap" / "gaps.tsv"), delimiter="\t")}
assert set(A) == set(B) == set(G), "class files and gaps.tsv differ"
conf = Counter((A[k]["class"], B[k]["class"]) for k in G)
agree = sum(v for (a, b), v in conf.items() if a == b)
print(f"rows {len(G)}  class agreement {agree} ({100 * agree / len(G):.1f} %)")
cl = ["PROTECTED", "PROTECTED-B2-DETAIL", "STRUCTURE", "WORDING", "UNRESOLVED", "UNVERIFIED"]
print("A \\ B      " + " ".join(f"{c[:9]:>9s}" for c in cl))
for a in cl:
    print(f"{a[:10]:10s} " + " ".join(f"{conf[(a, b)]:9d}" for b in cl))
dis = [k for k in G if A[k]["class"] != B[k]["class"]]
if "--tsv" in sys.argv:
    with open(sys.argv[sys.argv.index("--tsv") + 1], "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["id", "share", "A_class", "A_item", "A_reason", "B_class", "B_item", "B_reason", "quote"])
        for k in dis:
            w.writerow([k, G[k]["share"], A[k]["class"], A[k]["item"], A[k]["reason"], B[k]["class"], B[k]["item"],
                        B[k]["reason"], G[k]["quote"]])
for k in dis:
    print(f"\n{k} sh={G[k]['share']}  A={A[k]['class']} [{A[k]['item']}]  B={B[k]['class']} [{B[k]['item']}]\n"
          f"  A: {A[k]['reason']}\n  B: {B[k]['reason']}")
