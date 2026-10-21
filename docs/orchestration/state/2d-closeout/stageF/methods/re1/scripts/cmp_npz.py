#!/usr/bin/env python3
"""Array-by-array bitwise comparison of two npz files (keys, dtypes, shapes, values)."""
import json, sys
import numpy as np
a, b = np.load(sys.argv[1], allow_pickle=False), np.load(sys.argv[2], allow_pickle=False)
ka, kb = set(a.files), set(b.files)
res = {"only_a": sorted(ka - kb), "only_b": sorted(kb - ka), "differ": {}}
for k in sorted(ka & kb):
    x, y = a[k], b[k]
    if x.dtype != y.dtype or x.shape != y.shape or not np.array_equal(x, y, equal_nan=x.dtype.kind == "f"):
        d = None
        if x.shape == y.shape and x.dtype.kind in "fi":
            d = float(np.nanmax(np.abs(x.astype(float) - y.astype(float))))
        res["differ"][k] = {"dtype": [str(x.dtype), str(y.dtype)], "shape": [list(x.shape), list(y.shape)], "max_abs": d}
res["n_common"] = len(ka & kb)
res["identical"] = not res["only_a"] and not res["only_b"] and not res["differ"]
print(json.dumps(res, indent=1))
sys.exit(0 if res["identical"] else 1)
