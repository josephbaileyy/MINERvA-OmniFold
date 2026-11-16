#!/usr/bin/env python3
"""BV96 O1, the M80 table after the consult's correction (consult-astra/answer.txt): per truth, the experiments needed
for 0.8 power at one truth, M80 = [(2.241 + 0.8416) SD(d_m) / (G - 0.05)]^2. G is the model's expected gain,
mean(sd51^2) * 95/96, fixed rather than estimated per truth. SD(d_m) is the larger of its values at rho = 0 and 0.9,
from 40,000 draws of bv96_power_sim.py's model. Seed 7. A planning extrapolation, not a measured power.
usage: python3 -I -B bv96_m80.py <bv96_power_inputs.json>
"""
import json
import statistics as st
import sys

import numpy as np

d = json.load(open(sys.argv[1]))
rows = np.asarray(d["rounding_rows_sigma"])
k = np.sqrt(52 / 51)
sd = np.asarray(d["rounding_sd_sigma"])
gain = float(np.mean(sd ** 2)) * 95 / 96
print(f"mean rounding variance {np.mean(sd ** 2):.6f}; expected gain G {gain:.6f}")
off = {r["truth"]: np.asarray(r["values"]) for r in d["offset_sigma"]}
rng = np.random.default_rng(7)
res = {}
for t, b in off.items():
    sds = []
    for rho in (0.0, 0.9):
        n = 40000
        s = np.sqrt(rho) * rng.standard_normal((n, 1)) + np.sqrt(1 - rho) * rng.standard_normal((n, b.size))
        i_f, i_e = rng.integers(0, 52, n), rng.integers(0, 52, n)
        dm = np.mean((b + s + k * rows[i_e] / np.sqrt(96)) ** 2 - (b + s + k * rows[i_f]) ** 2, axis=1)
        sds.append(float(dm.std()))
    m80 = ((2.241 + 0.8416) * max(sds) / (gain - 0.05)) ** 2
    res[t] = m80
    print(f"{t:15s} SD(d_m) rho 0 {sds[0]:7.2f}  rho 0.9 {sds[1]:7.2f}  M80 {m80:9.0f}  node-h per truth {m80 * 97 * 0.020258:9.0f}")
ng = [t for t in res if t not in ("nominal", "A7_gibuu", "stage0c_gibuu")]
ms = sorted(res[t] for t in ng)
worst = max(ng, key=res.get)
print(f"the {len(ng)} non-nominal non-GiBUU truths: M80 min {ms[0]:.0f}, median {st.median(ms):.0f}, max {ms[-1]:.0f} ({worst})")
