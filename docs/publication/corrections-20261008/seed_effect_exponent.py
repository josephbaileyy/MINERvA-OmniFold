#!/usr/bin/env python3
"""The seed-effect scaling exponent p in s ~ N^-p, computed from the committed SEED-EFFECT-20260920.json.

PRD release audit ea939701 (U03/G5): the article printed "fitted exponent 0.000" over N = 40, 80, 160. This script
is the calculation that was never committed. It prints the least-squares exponent over the three subset means and
over all seven points, and the two-point 40 -> 80 exponent. MEASURES: nothing new (it re-reads committed numbers).

  python3 seed_effect_exponent.py [path/to/SEED-EFFECT-20260920.json]
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT = ROOT / "docs/orchestration/state/SEED-EFFECT-20260920.json"


def lsq_exponent(points):
    """p in s ~ N^-p by least squares of log s on log N."""
    xs = [math.log(n) for n, _ in points]
    ys = [math.log(s) for _, s in points]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return -slope


def main(argv=None) -> int:
    path = Path((argv or sys.argv[1:] or [DEFAULT])[0])
    d = json.loads(path.read_text())
    pts = [(int(r["n_throws"]), float(r["s_proj"])) for r in d["seed_effect_same_throws"]]
    pts.append((160, float(d["graded_s_proj_N160"])))
    by_n = defaultdict(list)
    for n, s in pts:
        by_n[n].append(s)
    means = sorted((n, sum(v) / len(v)) for n, v in by_n.items())
    two_point = math.log(means[0][1] / means[1][1]) / math.log(means[1][0] / means[0][0])
    out = {"points": len(pts), "means_percent": {n: round(100 * s, 4) for n, s in means},
           "lsq_exponent_three_means": round(lsq_exponent(means), 4),
           "lsq_exponent_all_points": round(lsq_exponent(pts), 4),
           "two_point_exponent_40_to_80": round(two_point, 4)}
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
