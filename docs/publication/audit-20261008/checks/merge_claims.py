"""Merge the claim skeleton with the four mapping files into one claim-to-artifact table; derive primary class + UP flag."""
import csv, re, sys
from collections import Counter, OrderedDict
S = sys.argv[1]
sk = list(csv.DictReader(open(f"{S}/claims-skeleton.tsv"), delimiter="\t"))
src = {}
for tag, f in (("lead", "lead-rows.tsv"), ("A", "agent-A-rows.tsv"), ("B", "agent-B-rows.tsv"), ("C", "agent-C-rows.tsv")):
    for r in csv.DictReader(open(f"{S}/{f}"), delimiter="\t"):
        src.setdefault(r["id"], []).append((tag, r))
out = []
for s in sk:
    rows = src.get(s["id"], [])
    if s["id"] == "R03":
        rows = [(t, r) for t, r in rows]
        for t, r in rows:
            out.append((s, t, r, "R03a (literature range)" if t == "B" else "R03b (±4% scale and application)"))
        continue
    if s["id"] == "J21":
        rows = [x for x in rows if x[0] == "lead"] + [x for x in rows if x[0] == "C"]
        out.append((s, "lead+C", rows[0][1], None)); continue
    if not rows:
        print("NO ROW", s["id"]); continue
    out.append((s, rows[0][0], rows[0][1], None))
OVERRIDE = {  # lead-auditor adjustments after spot checks (documented in the report)
    "R05": "SO / ME(the printed '~11%' is in no committed record) + UP",
    "A02": "SO + UP (W2 shifted data unfolds are pscratch-only; see R04/R05)",
}
def primary(c):
    c = c.upper()
    for k in ("ME", "SO-NOINDEP", "SO", "RR"):
        if re.search(r"(^|[^A-Z-])" + re.escape(k) + r"($|[^A-Z-])", c): return k
    return "?"
cols = ["id", "section", "location", "claim", "printed", "class", "primary_class", "UP", "receipt", "receipt_value_check",
        "underlying_artifact", "independent_check", "preservation_route", "preservation_verified", "gap_and_fix", "mapped_by"]
w = csv.writer(open(f"{S}/CLAIM-TABLE.tsv", "w"), delimiter="\t", lineterminator="\n")
w.writerow(cols)
cnt, up = Counter(), 0
for s, tag, r, idover in out:
    cid = idover.split()[0] if idover else s["id"]
    cls = OVERRIDE.get(cid, r["class"])
    # primary = worst component (ME > SO-NOINDEP > SO > RR) for any row that mixes
    comps = [primary(x) for x in re.split(r"/|;", cls)]
    order = ["ME", "SO-NOINDEP", "SO", "RR"]
    pc = min((c for c in comps if c in order), key=order.index, default="?")
    u = "UP" if "UP" in cls.upper().replace("SUPPORT", "") else ""
    if pc == "RR" and not u:
        u = "UP"; cls += " + UP(release payload: RC4 tarball/npz have no durable copy)"
    cnt[pc] += 1; up += bool(u)
    claim = s["claim (as printed)"] + (f" [{idover}]" if idover else "")
    w.writerow([cid, s["section"], s["location"], claim, s["printed value(s)"], cls, pc, u, r["receipt"], r["receipt_value_check"],
                r["underlying_artifact"], r["independent_check"], r["preservation_route"], r["preservation_verified"],
                r["gap_and_fix"], tag])
print("rows", len(out), dict(cnt), "UP", up)
