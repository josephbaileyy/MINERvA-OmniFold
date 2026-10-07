#!/usr/bin/env python3
"""Compare the production closure run with fixed_truth_toy.py --no-fluctuation.

Pass condition (pre-registered): on all 14x16 bins, ``hXSec2D`` agrees to a
relative 1e-6 (identical inputs, estimator and GBDT seed; the slack covers only
multithreaded floating-point summation order and is ~2e-4 of the production
statistical sigma's per-bin median, 0.55%), and the toy driver's ``hTruthFixedXSec2D`` and
``hTruthXSec2D`` both equal the production ``hTruthXSec2D`` exactly. Lightgbm
multithreading changes a result by a flipped split rather than by rounding, so this
is in effect an exact-reproduction test; a failure is re-run on both sides twice
before it counts as a failed check (amendment 1).

With ``--rollup`` it also reports the fixed-seed closure residual
``(U0 - T) / (r_b T_b)`` on the reported bins (amendment 1 secondary): the bias the
seed-1 estimator carries into every toy, to separate bias from width.
"""

import argparse
import json
import sys

import numpy as np

from extract_toys import production_band, read_hist

REL_TOL = 1e-6


def max_rel(a, b):
    den = np.maximum(np.abs(a), np.abs(b))
    return float(np.max(np.where(den > 0, np.abs(a - b) / np.where(den > 0, den, 1), 0.0)))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("production")
    ap.add_argument("toy_driver")
    ap.add_argument("--out", required=True)
    ap.add_argument("--rollup", help="production bootstrap rollup (VL162)")
    a = ap.parse_args()
    px, _ = read_hist(a.production, "hXSec2D")
    pt, _ = read_hist(a.production, "hTruthXSec2D")
    tx, _ = read_hist(a.toy_driver, "hXSec2D")
    tf, _ = read_hist(a.toy_driver, "hTruthFixedXSec2D")
    tp, _ = read_hist(a.toy_driver, "hTruthXSec2D")
    res = {"xsec_max_rel_diff": max_rel(px, tx),
           "fixed_truth_equals_production_truth": bool(np.array_equal(tf, pt)),
           "prior_equals_production_truth": bool(np.array_equal(tp, pt)),
           "closure_max_rel_unfold_vs_truth": max_rel(px, pt), "rel_tol": REL_TOL}
    if a.rollup:
        mean, sigma, rep = production_band(a.rollup)
        zb = (px[rep] - tf[rep]) / (sigma[rep] / mean[rep] * tf[rep])
        res["closure_bias_over_sigma"] = {
            "mean": float(zb.mean()), "rms": float(np.sqrt((zb * zb).mean())),
            "median_abs": float(np.median(np.abs(zb))), "max_abs": float(np.abs(zb).max()),
            "frac_abs_gt_1": float((np.abs(zb) > 1).mean())}
    res["pass"] = bool(res["xsec_max_rel_diff"] <= REL_TOL
                       and res["fixed_truth_equals_production_truth"]
                       and res["prior_equals_production_truth"])
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
    print(json.dumps(res))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
