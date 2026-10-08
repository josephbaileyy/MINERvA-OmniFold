#!/usr/bin/env python3
"""Largest relative shift of the observed joint statistics under the W2 recoil scale (the article's "about 11%").

Reads the committed frozen evaluation and the three committed W2 re-evaluations (rr0 = -4%, rr1 = +4%, rrzero =
unscaled re-unfold control) and prints, for each baseline, the largest |T_shifted / T_baseline - 1| over the ten
tests and both signs, with its operands. MEASURES: nothing new (it re-reads committed evaluator outputs).

  python3 publication/w2/w2b_statistic_shift.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "docs/orchestration/state/s5p/stage7/joint/joint-evaluate.json"
W2 = ROOT / "publication/w2/w2b-results"
SIGN = {"rr0": "-4%", "rr1": "+4%"}


def stat(d, null, s):
    return float(d["tests"][null]["T_total_obs" if s == "total" else "T_shape_obs"])


def main() -> int:
    fz = json.loads(FROZEN.read_text())
    runs = {k: json.loads((W2 / k / "joint-evaluate.json").read_text()) for k in ("rr0", "rr1", "rrzero")}
    for base_name, base in (("frozen observed statistic", fz), ("unscaled re-unfold (rrzero)", runs["rrzero"])):
        best = max(((abs(stat(runs[v], n, s) / stat(base, n, s) - 1), v, n, s)
                    for v in SIGN for n in fz["tests"] for s in ("total", "shape")))
        r, v, n, s = best
        print(f"baseline {base_name}: max |dT/T| = {r:.4f} at {n} {s}, {SIGN[v]}: "
              f"T {stat(base, n, s):.3f} -> {stat(runs[v], n, s):.3f}")
    ctrl = max(abs(stat(runs["rrzero"], n, s) / stat(fz, n, s) - 1) for n in fz["tests"] for s in ("total", "shape"))
    print(f"control: unscaled re-unfold vs frozen, max |dT/T| = {ctrl:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
