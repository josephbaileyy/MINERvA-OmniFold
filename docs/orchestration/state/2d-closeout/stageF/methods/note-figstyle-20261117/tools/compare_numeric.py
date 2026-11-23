#!/usr/bin/env python3
"""Tier 2's arm-0 identity where the drawn data come out of a linear-algebra routine (the tension figures, Figs. 11-12):
the local arrays against a cluster capture's, within a tolerance.

usage: python3 compare_numeric.py <reference .png.json> <local .png.json> [--rtol R]

The tension producer draws eigenvalues and eigenvectors of the published covariance. On another LAPACK the same inputs
give the same values to rounding, not bit for bit, so the colour-free hashes differ while every printed number agrees.
The reference is fig-restyle-20261031 run-a2's after capture, the one cluster capture of these figures with its arrays
(.npz) committed; its colour-free hashes equal note-figstyle-20261113 family 2's (the installed files') item for item,
so its arrays are the installed figures' data.
Items are paired in order (kind and axes must match). Each array the reference holds for a data field must exist
locally with the same shape and agree within rtol (relative to the reference's largest magnitude in that array). An
array that agrees only after its sign is flipped (an eigenvector's sign is arbitrary) is reported as SIGN and counted
apart; it is not a failure of the data, but the drawn map shows the opposite colours. Prints NUMERIC-IDENTITY :: PASS
or FAIL (and the count of sign-flipped arrays); exit 1 on FAIL.
"""
import json
import sys
from pathlib import Path

import numpy as np

COLOUR_STYLE = {"color", "mfc", "mec", "face", "edge", "cmap", "clim", "linestyle", "marker", "drawstyle"}
rj, lj = Path(sys.argv[1]), Path(sys.argv[2])
rtol = float(sys.argv[sys.argv.index("--rtol") + 1]) if "--rtol" in sys.argv else 1e-9
ri = [x for x in json.loads(rj.read_text()) if x["kind"] != "hist-input"]
li = json.loads(lj.read_text())
rz, lz = np.load(str(rj)[:-5] + ".npz"), np.load(str(lj)[:-5] + ".npz")
ok, worst, flips, n = len(ri) == len(li) and len(ri) > 0, 0.0, 0, 0
print(f"items: {len(ri)} reference, {len(li)} local")
for x, y in zip(ri, li):
    if (x["kind"], x["axes"]) != (y["kind"], y["axes"]):
        print(f"  FAIL pairing: {x['kind']}/{x['axes']} vs {y['kind']}/{y['axes']}")
        ok = False
        continue
    for k in [k for k in rz.files if k.startswith(f"i{x['i']}.")]:
        field = k.split(".", 1)[1]
        if field.split(".")[0] in COLOUR_STYLE or field.endswith(".mask"):
            continue
        lk = f"i{y['i']}.{field}"
        a = rz[k].astype(float)
        if lk not in lz.files or lz[lk].shape != a.shape:
            got = lz[lk].shape if lk in lz.files else None
            print(f"  FAIL {x['kind']} {field}: missing or shape {got} vs {a.shape}")
            ok = False
            continue
        b, n = lz[lk].astype(float), n + 1
        scale = max(np.nanmax(np.abs(a)) if a.size else 0.0, 1e-300)
        d = np.nanmax(np.abs(a - b)) / scale if a.size else 0.0
        if d <= rtol:
            worst = max(worst, d)
        elif a.size and np.nanmax(np.abs(a + b)) / scale <= rtol:
            flips += 1
            print(f"  SIGN {x['kind']} on axes {x['axes']} {field}: equal after a sign flip")
        else:
            print(f"  FAIL {x['kind']} on axes {x['axes']} {field}: max relative difference {d:.3g} > {rtol:g}")
            ok = False
print(f"arrays compared: {n}; largest relative difference {worst:.3g} (rtol {rtol:g}); sign-flipped arrays {flips}")
print(f"NUMERIC-IDENTITY :: {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
