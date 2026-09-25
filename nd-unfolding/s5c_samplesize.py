#!/usr/bin/env python3
"""Exact binomial sample sizes and assurance for the s5c feasibility receipt (plan §§5, 7).

Every bound is Clopper-Pearson (exact). Simultaneity over ``m`` comparisons uses Bonferroni
(per-comparison one-sided level ``0.05/m``), and the probability that ALL comparisons pass is
bounded below by ``1 - m (1 - q)`` where ``q`` is one comparison's pass probability at the design
value -- a bound valid under any dependence between comparisons (functionals of one experiment
are correlated). ``q**m`` (independence) is reported beside it for orientation only.

Gates (plan §7 defaults):
  coverage: simultaneous one-sided 95% LCB > 0.66 (68% intervals) and > 0.94 (95% intervals)
  size:     simultaneous one-sided 95% UCB <= 0.06 at alpha = 0.05; <= 1.2 alpha at 0.01, 0.001
  p-values: simultaneous 95% CP interval, max distance from the estimate to an endpoint
            <= 0.005 for p >= 0.05 and <= 0.25 p for 0.001 <= p < 0.05
"""
from __future__ import annotations

import argparse
import json
import math

from scipy.stats import beta, binom


def cp_lower(k: int, n: int, a: float) -> float:
    return 0.0 if k == 0 else float(beta.ppf(a, k, n - k + 1))


def cp_upper(k: int, n: int, a: float) -> float:
    return 1.0 if k == n else float(beta.ppf(1 - a, k + 1, n - k))


def min_k_lower_above(n: int, thr: float, a: float) -> int | None:
    """Smallest k with cp_lower(k, n, a) > thr, or None."""
    if cp_lower(n, n, a) <= thr:
        return None
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if cp_lower(mid, n, a) > thr:
            hi = mid
        else:
            lo = mid + 1
    return lo


def max_k_upper_below(n: int, thr: float, a: float) -> int | None:
    """Largest k with cp_upper(k, n, a) <= thr, or None."""
    if cp_upper(0, n, a) > thr:
        return None
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if cp_upper(mid, n, a) <= thr:
            lo = mid
        else:
            hi = mid - 1
    return lo


def coverage_assurance(n: int, p_true: float, thr: float, m: int) -> dict:
    a = 0.05 / m
    k = min_k_lower_above(n, thr, a)
    q = 0.0 if k is None else float(binom.sf(k - 1, n, p_true))
    return {"n": n, "k_min": k, "q": q, "assurance_lower_bound": max(0.0, 1 - m * (1 - q)),
            "assurance_if_independent": q**m}


def size_assurance(n: int, alpha: float, bound: float, m: int, p_true: float | None = None) -> dict:
    a = 0.05 / m
    k = max_k_upper_below(n, bound, a)
    p = alpha if p_true is None else p_true
    q = 0.0 if k is None else float(binom.cdf(k, n, p))
    return {"n": n, "k_max": k, "q": q, "assurance_lower_bound": max(0.0, 1 - m * (1 - q)),
            "assurance_if_independent": q**m}


def smallest_n(fn, target: float, lo: int = 10, hi: int = 2_000_000) -> dict | None:
    """Smallest n (to 1% resolution above 1000) whose assurance lower bound reaches target."""
    if fn(hi)["assurance_lower_bound"] < target:
        return None
    while hi - lo > max(1, lo // 100):
        mid = (lo + hi) // 2
        if fn(mid)["assurance_lower_bound"] >= target:
            hi = mid
        else:
            lo = mid
    return fn(hi)


def pvalue_B(p: float, reported: int) -> int:
    """Smallest B whose simultaneous 95% CP interval meets the precision rule at true p."""
    a2 = 0.05 / reported / 2
    tol = 0.005 if p >= 0.05 else 0.25 * p

    def ok(B: int) -> bool:
        k = round(p * B)
        ph = k / B
        return max(ph - cp_lower(k, B, a2), cp_upper(k, B, a2) - ph) <= tol

    lo, hi = 10, 10
    while not ok(hi):
        lo, hi = hi, hi * 2
    while hi - lo > max(1, lo // 200):
        mid = (lo + hi) // 2
        lo, hi = (lo, mid) if ok(mid) else (mid, hi)
    return hi


def build(target: float) -> dict:
    out = {"schema": "s5c-samplesize/1", "assurance_target": target, "coverage": [], "size": [], "pvalue": []}
    for F in (8, 16, 32, 43):
        for G in (1, 2, 3, 4):
            m = F * G
            for label, thr, design in (("68", 0.66, 0.6827), ("68-if-true-0.70", 0.66, 0.70),
                                       ("95", 0.94, 0.9545), ("95-if-true-0.96", 0.94, 0.96)):
                res = smallest_n(lambda n: coverage_assurance(n, design, thr, m), target)
                out["coverage"].append({"functionals": F, "grid_points": G, "m": m, "interval": label,
                                        "threshold": thr, "design_true_coverage": design, "result": res})
    for S in (1, 2, 4, 8):
        for alpha, bound in ((0.05, 0.06), (0.01, 0.012), (0.001, 0.0012)):
            res = smallest_n(lambda n: size_assurance(n, alpha, bound, S), target, hi=50_000_000)
            out["size"].append({"null_scenarios": S, "alpha": alpha, "ucb_bound": bound, "result": res})
    for R in (1, 4, 8):
        for p in (0.5, 0.2, 0.05, 0.02, 0.01, 0.005, 0.001):
            out["pvalue"].append({"reported_comparisons": R, "true_p": p, "B_required": pvalue_B(p, R)})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--assurance", type=float, default=0.8)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    res = build(a.assurance)
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
