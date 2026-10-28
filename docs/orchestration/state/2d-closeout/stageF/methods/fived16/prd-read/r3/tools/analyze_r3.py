"""Tabulate round 3 of the PRD read: A (paper abstract), B (note abstract), C (title), P01-P26 (body pairs), over the
four runs (sol2 r1, r2; gemini r1, r2). Verdicts only: the truth column is a separate, manual step."""
import re, sys
X = sys.argv[1]
RUNS = ["PR3__r1__sol2", "PR3__r2__sol2", "PR3__r1__gemini", "PR3__r2__gemini"]
ids = ["A", "B"] + [f"P{i:02d}" for i in range(1, 27)]
rows = {}
for r in RUNS:
    t = open(f"{X}/runs/{r}.md").read()
    for i in ids:
        m = re.search(rf"^\**{i}\**:\s*\**VERDICT:\**\s*\**(ACCEPT|DENY|SHORTEN)", t, re.M)
        rows.setdefault(i, []).append(m.group(1) if m else "?")
    for k in ("A", "B"):
        blk = re.search(rf"^\**{k}\**:.*?(?=^\**[B-Z]\d*\**:)", t, re.M | re.S)
        lm = re.search(r"LENGTH:\**\s*\**(ACCEPTABLE|TOO-LONG)", blk.group(0)) if blk else None
        rows.setdefault(k + "-length", []).append(lm.group(1) if lm else "?")
    m = re.search(r"^\**C\**:\s*\**BEST:\**\s*\**(T\d)", t, re.M)
    rows.setdefault("C-title", []).append(m.group(1) if m else "?")
print("item\t" + "\t".join(RUNS) + "\tagreement")
for k, v in rows.items():
    print(k + "\t" + "\t".join(v) + "\t" + ("4/4 " + v[0] if len(set(v)) == 1 else "split"))
