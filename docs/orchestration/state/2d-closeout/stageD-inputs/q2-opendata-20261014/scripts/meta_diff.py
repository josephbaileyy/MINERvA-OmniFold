"""Compare two meta.py JSON dumps: branch-set differences and byte attribution per tree.

Usage: python -I meta_diff.py <local.json> <remote.json>
Uses the highest cycle of each tree name.
"""
import json, sys

def top_cycles(rec):
    best = {}
    for k, v in rec["trees"].items():
        n, c = k.split(";")
        if n not in best or int(c) > best[n][0]:
            best[n] = (int(c), v)
    return {n: v for n, (c, v) in best.items()}

a, b = (json.load(open(p)) for p in sys.argv[1:3])
print("size local", a["size"], "remote", b["size"], "ratio", round(b["size"] / a["size"], 5))
print("created local", a["created"], "remote", b["created"], "| compress", a["compress"], b["compress"])
ta, tb = top_cycles(a), top_cycles(b)
for n in sorted(set(ta) | set(tb)):
    x, y = ta.get(n), tb.get(n)
    if not x or not y:
        print(n, "present only in", "remote" if y else "local"); continue
    bx, by = x["branches"], y["branches"]
    add, rem = sorted(set(by) - set(bx)), sorted(set(bx) - set(by))
    common = set(bx) & set(by)
    add_bytes = sum(by[k][0] for k in add)
    common_delta = sum(by[k][0] - bx[k][0] for k in common)
    print(f"\n[{n}] entries local={x['entries']} remote={y['entries']} (delta {y['entries'] - x['entries']}); "
          f"branches local={len(bx)} remote={len(by)}; zip local={x['zipbytes']} remote={y['zipbytes']} delta={y['zipbytes'] - x['zipbytes']}")
    print(f"  remote-minus-local: {len(add)} branches, zipbytes {add_bytes}")
    print(f"  local-minus-remote: {len(rem)} branches, zipbytes {sum(bx[k][0] for k in rem)}")
    print(f"  common branches: {len(common)}, zipbytes delta {common_delta}")
    for k in add:
        print(f"    + {k}  zip={by[k][0]}  title={by[k][2]}")
    for k in rem:
        print(f"    - {k}  zip={bx[k][0]}  title={bx[k][2]}")
    big = sorted(common, key=lambda k: -abs(by[k][0] - bx[k][0]))[:8]
    for k in big:
        print(f"    ~ {k}  zip {bx[k][0]} -> {by[k][0]}  title {bx[k][2]!r} -> {by[k][2]!r}" if bx[k][2] != by[k][2] else f"    ~ {k}  zip {bx[k][0]} -> {by[k][0]}")
    tchg = [k for k in common if bx[k][2] != by[k][2]]
    print(f"  common branches whose leaf title/type changed: {len(tchg)} {tchg[:10]}")
