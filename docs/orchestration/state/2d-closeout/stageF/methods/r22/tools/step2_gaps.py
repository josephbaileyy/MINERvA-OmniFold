"""Write r22 Step 2's gap list: every Step 1 gap that both classifications call WORDING or STRUCTURE after #522.

usage: python3 -I step2_gaps.py R22_DIR      writes R22_DIR/step2/gaps-ws.tsv and prints the counts
Columns: id, input, model, share, lane_class, indep_class, scope (WS, or the #524 allowance), joseph_pair (yes for an
A1/A4 edit, which goes to Joseph as a pinned before/after pair before adoption), ledger (a ledger or note home named by
either, or #524's home), quote, problem, change. A gap that either classification calls PROTECTED, UNRESOLVED or
UNVERIFIED is left out, except the gaps DECISION-20261030-joseph-r22-protected-gaps.md (#524) allows (STEP2-PLAN.md
§1)."""
import csv
import sys
from collections import Counter
from pathlib import Path

R = Path(sys.argv[1])
G = list(csv.DictReader(open(R / "gap" / "gaps.tsv"), delimiter="\t"))
A = {r["id"]: r for r in csv.DictReader(open(R / "gap" / "class-lane-after522.tsv"), delimiter="\t")}
B = {r["id"]: r for r in csv.DictReader(open(R / "gap" / "class-indep-after522.tsv"), delimiter="\t")}
WS = {"WORDING", "STRUCTURE"}
# #524 item 1: sol2's ten protected gaps; the A1/A4 ones go to Joseph as before/after pairs before adoption.
SOL2_TEN = {"paper-s-09": "A1", "B01-s-04": "A4", "B01-s-10": "A4", "paper-s-06": "A4", "B02-s-01": "B2",
            "B02-s-02": "B2", "B03-s-01": "B2", "B06-s-04": "B2", "B09-s-01": "B2", "B15-s-02": "B2"}
# #524 item 2: gemini's B2 run history whose fact the ledger keeps, and which drops no limitation, disclosure,
# qualifier or reported number from both documents. Each names its home; the round carries an R: probe on it.
GEMINI_HISTORY = {"B04-g-09": "OUTCOME-20261005-2d-fixed-truth-coverage-fail.md:1, :65-67; "
                              "state/coverage-2d-20261005/recompute/recompute_comparison.json"}
ALLOWED = set(SOL2_TEN) | set(GEMINI_HISTORY)
keep = [g for g in G if (A[g["id"]]["class"] in WS and B[g["id"]]["class"] in WS) or g["id"] in ALLOWED]
assert ALLOWED <= {g["id"] for g in G}, ALLOWED - {g["id"] for g in G}
with open(R / "step2" / "gaps-ws.tsv", "w", newline="") as fh:
    w = csv.writer(fh, delimiter="\t", lineterminator="\n")
    w.writerow(["id", "input", "model", "share", "lane_class", "indep_class", "scope", "joseph_pair", "ledger", "quote",
                "problem", "change"])
    for g in keep:
        a, b = A[g["id"]], B[g["id"]]
        homes = "; ".join(x for x in (a["item"], b["item"]) if "ledger" in x or "home" in x or "note" in x or "#522" in x)
        scope = ("#524 sol2 " + SOL2_TEN[g["id"]] if g["id"] in SOL2_TEN else
                 "#524 gemini history" if g["id"] in GEMINI_HISTORY else "WS")
        if g["id"] in GEMINI_HISTORY:
            homes = "ledger: " + GEMINI_HISTORY[g["id"]]
        pair = "yes" if SOL2_TEN.get(g["id"]) in ("A1", "A4") else ""
        w.writerow([g["id"], g["input"], g["model"], g["share"], a["class"], b["class"], scope, pair, homes, g["quote"],
                    g["problem"], g["change"]])
c = Counter((g["input"], g["model"]) for g in keep)
print(len(keep), "of", len(G), "gaps; paper", sum(v for (i, m), v in c.items() if i == "paper"),
      "note", sum(v for (i, m), v in c.items() if i != "paper"))
print("by scope:", dict(Counter(("#524" if g["id"] in ALLOWED else "WS") for g in keep)))
print("sol2 per note piece:", sorted(v for (i, m), v in c.items() if i != "paper" and m == "sol2"))
print("gemini per note piece:", sorted(v for (i, m), v in c.items() if i != "paper" and m == "gemini"))
