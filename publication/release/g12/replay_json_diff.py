"""Leaf-by-leaf comparison of two replay.json files (G12 review cycle 1): every differing leaf, with its relative difference."""
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:3])
diffs, n = [], [0]
def walk(x, y, path=""):
    if isinstance(x, dict) and isinstance(y, dict):
        for k in sorted(set(x) | set(y)):
            if k not in x or k not in y: diffs.append((path + "/" + k, "one-sided", None)); continue
            walk(x[k], y[k], path + "/" + k)
    elif isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y): diffs.append((path, "len", None)); return
        for i, (u, v) in enumerate(zip(x, y)): walk(u, v, "%s[%d]" % (path, i))
    else:
        n[0] += 1
        if x != y:
            rel = abs(x - y) / max(abs(x), abs(y)) if isinstance(x, float) and isinstance(y, float) else None
            diffs.append((path, type(x).__name__, rel))
walk(a, b)
print("regenerated", sys.argv[1], "| preserved", sys.argv[2])
print("leaves", n[0], "differing", len(diffs))
for d in diffs: print(" ", d)
