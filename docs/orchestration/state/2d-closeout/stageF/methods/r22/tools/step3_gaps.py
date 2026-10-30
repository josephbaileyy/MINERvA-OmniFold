"""Write r22 Step 3's note gap list and held list (STEP3-PLAN.md section 1).

usage: python3 -I step3_gaps.py R22_DIR ANALYZE_PY
In scope: the note gaps of openai-review/REVIEW.md with verdict ALLOW or ALLOW-NARROW
(DECISION-20261030-joseph-adopt-openai-review.md item 1). An ALLOW gap enters as gemini proposed (gap/gaps.tsv
`change`); an ALLOW-NARROW gap only in the reviewer's narrowed form (REVIEW.md's last column). The paper gaps of
REVIEW.md wait for the paper's next round and are listed, not written.
Held: every other note gap of Step 1 (gap/gaps.tsv) outside both step2/gaps-ws.tsv and this round's scope, with a
located quote. Each held quote is located in its base piece (step2/pieces/, the adopted note) by analyze.py's key(),
exactly; `base_match` says EXACT or GAPPED (located only by the gapped locate(), as a float splitting the sentence).
A held quote is FACT-holdable (STEP2-PAPER.md section 5, the director's rule for later note rounds too) when an in-scope
gap's quote overlaps it, unless it is Joseph's text or a claim: either classification of its gap cites A1, A4, A5 or
A7, or it is the FROZEN sentence, or a check_sec4 gate-bound phrase. Writes step3/gaps.tsv and step3/held.tsv."""
import ast
import csv
import re
import sys
from pathlib import Path

R, AN = Path(sys.argv[1]), Path(sys.argv[2])
ns = {}
for node in ast.parse(AN.read_text()).body:
    if isinstance(node, ast.FunctionDef) and node.name in ("key", "locate"):
        exec(compile(ast.Module([node], []), str(AN), "exec"), ns)
exec("import unicodedata, re", ns)
key = ns["key"]

gaps = {r["id"]: r for r in csv.DictReader(open(R / "gap" / "gaps.tsv"), delimiter="\t")}
step2 = {r["id"] for r in csv.DictReader(open(R / "step2" / "gaps-ws.tsv"), delimiter="\t")}
cls = {}
for side in ("lane", "indep"):
    for r in csv.DictReader(open(R / "gap" / f"class-{side}-after522.tsv"), delimiter="\t"):
        cls.setdefault(r["id"], {})[side] = (r["class"], r["item"], r["reason"])
review = []
for line in open(R / "openai-review" / "REVIEW.md"):
    if re.match(r"^\| [12] \|", line):
        c = [x.strip() for x in line.strip().strip("|").split(" | ")]
        review.append(dict(passno=c[0], id=c[1], group=c[2], verdict=c[3], reason=c[5], narrowed=c[6]))
pieces = {f"B{i:02d}": (R / "step2" / "pieces" / f"B{i:02d}.txt").read_text(encoding="utf-8") for i in range(1, 16)}
pkey = {p: key(t) for p, t in pieces.items()}
# Quotes carried to the base (STEP2-PLAN.md section 2: "carried to the new base by quote"): the note round's B06 added
# a table, so this unchanged sentence now prints "Table 16" (step2/STEP2-NOTE-REPORT.md, out-of-scope check).
CARRY = {"B09-g-09": ("in the order of Table 15.", "in the order of Table 16.")}
FROZEN = "Interval coverage has not been validated."
GATE = ["lies entirely below its window (Gaussian 0.954)", "removes the tail undercoverage"]
OWNED = re.compile(r"\bA[1457]\b")


def match(g):
    if key(g["quote"]) in pkey[g["input"]]:
        return "EXACT"
    ns["doc_key"] = {g["input"]: pkey[g["input"]]}
    return "GAPPED" if ns["locate"](g["input"], g["quote"]) else "NONE"


def overlap(a, b):
    ka, kb = key(a), key(b)
    return kb[:60] in ka or ka[:60] in kb


for gid, (old, new) in CARRY.items():
    assert gaps[gid]["quote"].count(old) == 1, gid
    gaps[gid] = dict(gaps[gid], quote=gaps[gid]["quote"].replace(old, new), carried=f"{old} -> {new}")
inscope, paper = [], []
for rv in review:
    if rv["verdict"] == "KEEP":
        continue
    g = gaps[rv["id"]]
    if g["input"] == "paper":
        paper.append(rv["id"])
        continue
    eff = g["change"] if rv["verdict"] == "ALLOW" else rv["narrowed"]
    inscope.append(dict(id=rv["id"], piece=g["input"], group=rv["group"], verdict=rv["verdict"],
                        joseph_pair="yes" if rv["group"] in ("A1", "A4", "A5", "A7") else "",
                        base_match=match(g), carried=g.get("carried", ""), quote=g["quote"], problem=g["problem"], gemini_change=g["change"],
                        effective_change=eff, review_reason=rv["reason"]))
ids3 = {r["id"] for r in inscope}
held = []
for gid, g in gaps.items():
    if g["input"] == "paper" or gid in step2 or gid in ids3 or g["located"] == "UNVERIFIED":
        continue
    c = cls.get(gid, {})
    items = " ".join(f"{v[0]} {v[1]}" for v in c.values())
    owned = bool(OWNED.search(items)) or FROZEN in g["quote"] or any(x in g["quote"] for x in GATE)
    acted = [r["id"] for r in inscope if r["piece"] == g["input"] and overlap(r["quote"], g["quote"])]
    held.append(dict(id=gid, piece=g["input"], base_match=match(g),
                     hold="EXACT" if owned or not acted else "FACT", acted_on_by=",".join(acted),
                     lane=" ".join(c.get("lane", ("", "", ""))[:2]), indep=" ".join(c.get("indep", ("", "", ""))[:2]),
                     quote=g["quote"]))
for name, rows in (("gaps", inscope), ("held", held)):
    out = R / "step3" / f"{name}.tsv"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
print(f"in scope: {len(inscope)} note gaps over {len({r['piece'] for r in inscope})} pieces; Joseph pairs: "
      f"{[r['id'] for r in inscope if r['joseph_pair']]}; base match: "
      f"{ {m: sum(r['base_match'] == m for r in inscope) for m in ('EXACT', 'GAPPED', 'NONE')} }")
print(f"paper gaps deferred to the paper's next round: {paper}")
print(f"held: {len(held)} ({sum(h['hold'] == 'FACT' for h in held)} FACT-holdable, "
      f"{sum(h['hold'] == 'EXACT' for h in held)} exact); base match: "
      f"{ {m: sum(h['base_match'] == m for h in held) for m in ('EXACT', 'GAPPED', 'NONE')} }")
