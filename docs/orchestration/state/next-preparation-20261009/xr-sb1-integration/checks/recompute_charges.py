"""Recompute charged CPU node-h = ElapsedRaw/3600 x billing/256 from sacct -X -P rows (fresh and tracked)."""
import sys, re
from fractions import Fraction as F
def rows(path, cols):
    out = {}
    for l in open(path):
        p = l.rstrip("\n").split("|")
        if len(p) < len(cols) or not p[0].isdigit(): continue
        r = dict(zip(cols, p)); out[r["JobID"]] = r
    return out
def bill(t):
    m = re.findall(r"(?:^|,)billing=(\d+)(?:,|$)", t); assert len(m) == 1, t; return int(m[0])
fresh = rows(sys.argv[1], "JobID JobName Account QOS State ExitCode Submit Start End ElapsedRaw AllocTRES WorkDir".split())
tr_sb1 = rows(sys.argv[2], "JobID JobName User Account QOS State ExitCode Submit Eligible Start End ElapsedRaw MaxRSS MaxDiskRead AllocTRES NodeList WorkDir".split())
tr_xr = rows(sys.argv[3], "JobID JobName State ElapsedRaw AllocTRES Timelimit".split())
groups = {"SB1": [], "XR prior (two-d-followup)": [], "XR recovery (PF)": []}
for j, r in sorted(fresh.items()):
    n = r["JobName"]; g = "SB1" if n.startswith("sb1_") else ("XR recovery (PF)" if n.startswith("xrr_") else "XR prior (two-d-followup)")
    c = F(int(r["ElapsedRaw"]) * bill(r["AllocTRES"]), 256 * 3600)
    t = tr_sb1.get(j) or tr_xr.get(j)
    same = t is not None and t["ElapsedRaw"] == r["ElapsedRaw"] and bill(t["AllocTRES"]) == bill(r["AllocTRES"]) and t["State"] == r["State"]
    groups[g].append((j, n, r["State"], int(r["ElapsedRaw"]), bill(r["AllocTRES"]), c, same))
for g, js in groups.items():
    print(f"## {g}")
    for j, n, st, e, b, c, same in js:
        print(f"  {j} {n:10s} {st:9s} elapsed={e:5d}s billing={b:3d} charged={float(c):.10f} tracked_psv_equal={same}")
    tot = sum(x[5] for x in js); print(f"  total {float(tot):.12f} node-h over {len(js)} jobs")
xr = sum(x[5] for g in ("XR prior (two-d-followup)", "XR recovery (PF)") for x in groups[g])
print(f"## XR cumulative {float(xr):.15f} (report: 0.002313368055555556); SB1 {float(sum(x[5] for x in groups['SB1'])):.6f} (report: 1.162754)")
print(f"## all lanes {float(sum(x[5] for g in groups.values() for x in g)):.6f} node-h; GPU allocations: {sum('gres/gpu' in r['AllocTRES'] for r in fresh.values())}")
