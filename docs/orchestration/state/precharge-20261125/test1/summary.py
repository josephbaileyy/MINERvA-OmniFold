"""Condense test1.json: held-out yields, good/poor ratio and positive rate per fit."""

import json
from pathlib import Path

import numpy as np

runs = json.loads((Path(__file__).resolve().parent / "test1.json").read_text())
bands = ["20-40", "40-50", "50-60", "60-80", "80-inf"]
for r in runs:
    b = r["bands"]
    v = lambda k: np.array(b[k][:3])  # data, fold, w-fold
    print(f"\n## w({r['var']}) {r['form']}, fit on {','.join(r['train'])}; deviance {r['deviance']:.1f}/{r['ndf']}")
    print(f"{'reco':>7} | {'neg data':>8} {'fold':>8} {'w-fold':>8} {'d/wf':>5} | "
          f"{'good/poor d':>11} {'fold':>6} {'w-fold':>6} | {'pos/neg d':>9} {'fold':>6} {'w-fold':>6}")
    for k in bands:
        a, g, p = v(f"-|all|{k}"), v(f"-|good|{k}"), v(f"-|poor|{k}")
        q = v(f"+|all|{k}")
        gp, pn = g / p, q / a
        print(f"{k:>7} | {a[0]:8.0f} {a[1]:8.1f} {a[2]:8.1f} {a[0] / a[2]:5.2f} | "
              f"{gp[0]:11.2f} {gp[1]:6.2f} {gp[2]:6.2f} | {pn[0]:9.4f} {pn[1]:6.4f} {pn[2]:6.4f}")
    ge60 = sum(v(f"-|all|{k}") for k in bands[3:])
    print(f"reco >= 60 negative: data {ge60[0]:.0f}, fold {ge60[1]:.1f} (excess {ge60[0] - ge60[1]:+.1f}),"
          f" w-fold {ge60[2]:.1f} (data - w-fold {ge60[0] - ge60[2]:+.1f})")
