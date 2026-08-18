#!/usr/bin/env python3
"""Ingredients for DETERMINATION-20260818-lanec-anchor-confound-is-declarable-by-direction.md.

WHY THIS FILE IS TRACKED. That determination's disposition rests on a SIGN -- the anchor confound
inflates the measured spread, therefore biases toward UNMET, therefore is declarable rather than
correctable. Every number supporting it is either one line of algebra or a Monte Carlo, and a
verdict-only receipt is unfalsifiable (CONVENTION-receipt-ingredients.md, BEN-077). So the operands ship
with the ruling: run this and the determination's tables either reproduce or they do not.

    python3 docs/orchestration/mii_anchor_confound_mc.py

THREE CLAIMS, IN INCREASING ORDER OF HOW MUCH THEY COULD BE WRONG:

  (1) EXACT.     E[s^2] = sigma^2 + sigma_d^2/n for one contaminated member of n.
                 Lane A's simplification of the original sigma_d^2 (1-1/n)/(n-1); identical for all n,
                 and the simpler form is why n=6 is four times worse than n=50.
  (2) MC.        The sign survives f_med, a MEDIAN over 285 bins -- and NOT for the c4 reason. c4
                 survives a median because it is UNIFORM; this survives because it is UNIVERSAL: the
                 displaced member is displaced in every bin at once, because it is one run, so there is
                 no clean majority for the median to fall back on.
  (3) THEOREM.   The inflation is governed by E[d_b^2]/n, and at fixed mean displacement Jensen gives
                 E[d_b^2] >= (E|d_b|)^2 with equality IFF d_b is constant. So the CONSTANT-displacement
                 figures are a FLOOR over the whole family of patterns, not three lucky draws -- which
                 is what makes the determination's table a floor rather than the ceiling its first label
                 claimed.

NOTE ON A DISCREPANCY THAT IS DELIBERATELY LEFT IN. Two of lane A's four reported f_med inflations do
not reproduce here (uniform 0..2: 1.31% here vs 1.46%; lognormal: 1.23% vs 1.34%), against an MC
standard error near 0.007%. Constant and half-half match exactly. The E[d^2] law says A's uniform figure
is unreachable by uniform(0,2), whose E[d^2] = 4/3 caps it at 1.32%, so the setups differ -- most likely
a varying sigma_b against an absolute d_b, or lognormal(0, 0.5) whose mean is 1.133 rather than 1. NOT
adjudicated: neither conclusion depends on any of the eight numbers. It is recorded because two lanes
quoting different values for one quantity is what gets copied forward as agreement.

Seeds are literals so the numbers are reproducible; nothing here reads or writes campaign products.
"""
from __future__ import annotations

import numpy as np

N_MEMBERS = 50
N_BINS = 285
TRIALS = 4000
SEED = 20260818

# pattern -> (sampler, exact E[d_b^2]).  d_b is in units of that bin's clean scatter sigma_b.
PATTERNS = {
    "uniform 0..1":     (lambda r, nb: r.uniform(0, 1, nb), 1.0 / 3.0),
    "constant 1":       (lambda r, nb: np.full(nb, 1.0), 1.0),
    "lognormal mean 1": (lambda r, nb: r.lognormal(-0.125, 0.5, nb), float(np.exp(0.25))),
    "uniform 0..2":     (lambda r, nb: r.uniform(0, 2, nb), 4.0 / 3.0),
    "half 0 / half 2":  (lambda r, nb: np.where(r.random(nb) < 0.5, 0.0, 2.0), 2.0),
    "half 0 / half 4":  (lambda r, nb: np.where(r.random(nb) < 0.5, 0.0, 4.0), 8.0),
}


def identity_check() -> int:
    """(1) (1-1/n)/(n-1) == 1/n for every n. Lane A's key."""
    bad = [n for n in (2, 3, 6, 20, 50, 100, 1000, 10 ** 6)
           if abs((1 - 1.0 / n) / (n - 1) - 1.0 / n) > 1e-15]
    print("(1) EXACT  (1-1/n)/(n-1) == 1/n")
    for n in (6, 20, 50, 100):
        print(f"      n={n:<5} sd inflation at sigma_d = sigma : {100*(np.sqrt(1+1.0/n)-1):>6.2f}%")
    print(f"    -> {'PASS' if not bad else 'FAIL at n=' + str(bad)}")
    return 1 if bad else 0


def f_med_mc(pattern, n=N_MEMBERS, nbins=N_BINS, trials=TRIALS, seed=SEED):
    """(2)+(3) inflation of median-over-bins sd when member 0 is displaced in EVERY bin."""
    rng = np.random.default_rng(seed)
    out = np.empty(trials)
    for t in range(trials):
        x = rng.standard_normal((n, nbins))          # sigma_b = 1 in every bin
        clean = np.median(x.std(axis=0, ddof=1))
        y = x.copy()
        y[0] += pattern(rng, nbins)
        out[t] = np.median(y.std(axis=0, ddof=1)) / clean - 1.0
    return out


def main() -> int:
    rc = identity_check()

    print()
    print("(2)+(3) MC: does the sign survive a median over bins, and is the constant case a FLOOR?")
    print(f"    n={N_MEMBERS}, {N_BINS} bins, {TRIALS} trials, seed {SEED}")
    print(f"    {'pattern':<20} {'E[d^2]':>8} {'sqrt(1+E/n)-1':>14} {'measured':>10} {'ratio':>7} {'frac up':>8}")
    prev = None
    for label, (pat, ed2) in PATTERNS.items():
        infl = f_med_mc(pat)
        pred = np.sqrt(1 + ed2 / N_MEMBERS) - 1
        m = float(infl.mean())
        print(f"    {label:<20} {ed2:>8.4f} {100*pred:>13.2f}% {100*m:>9.2f}% "
              f"{m/pred:>7.3f} {float(np.mean(infl > 0)):>8.3f}")
        if label == "constant 1":
            prev = m
        elif prev is not None and ed2 > 1.0 and m <= prev:
            print(f"      !! {label} did NOT exceed the constant case -- the FLOOR claim fails")
            rc = 1
    print("    -> the constant case is exceeded by every larger-E[d^2] pattern, as Jensen requires")

    print()
    print("(4) the sign is certain IN EXPECTATION, not per realisation. How bad can one draw be?")
    infl = f_med_mc(PATTERNS["constant 1"][0])
    q = np.percentile(infl, [0.5, 2.5, 50, 97.5])
    print(f"    P(confound pushes f_med DOWN) = {float(np.mean(infl < 0)):.4f}"
          f"   worst downward excursion = {100*float(infl.min()):+.2f}%")
    print(f"    percentiles 0.5/2.5/50/97.5 = {100*q[0]:+.2f}% {100*q[1]:+.2f}% {100*q[2]:+.2f}% {100*q[3]:+.2f}%")
    print("    against the 16.8% headroom leg B's MET threshold (2.28%) has under its 2.74% bar,")
    print("    so a sub-1% realisation excursion cannot cross it. Caveat real, stated, subsumed.")

    print()
    print("ANCHOR-CONFOUND MC :: " + ("PASS" if rc == 0 else "FAIL"))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
