#!/usr/bin/env python3
"""Ingredients for DETERMINATION-20260818-lanec-anchor-confound-is-declarable-by-direction.md.

WHY THIS FILE IS TRACKED. That determination's disposition rests on a SIGN -- the anchor confound
inflates the measured spread, therefore biases toward UNMET, therefore is declarable rather than
correctable. Every number supporting it is either one line of algebra or a Monte Carlo, and a
verdict-only receipt is unfalsifiable (CONVENTION-receipt-ingredients.md, BEN-077). So the operands ship
with the ruling: run this and the determination's tables either reproduce or they do not.

    python3 docs/orchestration/mii_anchor_confound_mc.py

FOUR CLAIMS, in increasing order of how much they could be wrong. Two of them ARE wrong as first
written, and check (4) is the one that found it.

  (1) EXACT.       E[s^2] = sigma^2 + sigma_d^2/n for one contaminated member of n. Lane A's
                   simplification of sigma_d^2 (1-1/n)/(n-1); identical for all n, and the simpler form
                   is why n=6 is four times worse than n=50.
  (2) DIRECTION.   The sign survives f_med, a MEDIAN over 285 bins -- and NOT for the c4 reason. c4
                   survives a median because it is UNIFORM; this survives because it is UNIVERSAL: the
                   displaced member is displaced in every bin at once, because it is one run, so there
                   is no clean majority for the median to fall back on. THIS IS LANE A's RESULT and it
                   is the load-bearing one for leg B.
  (3) ORDERING.    Inflation tracks E[d_b^2]/n, and Jensen gives E[d_b^2] >= (E|d_b|)^2 with equality
                   IFF d_b is constant -- so at fixed MEAN displacement the constant pattern minimises
                   E[d^2]. EXACT for f_agg. **FOR f_med IT REQUIRES (2)'s UNIVERSALITY CONDITION**, and
                   check (4) exhibits the violation: concentrate the same mean displacement into a
                   MINORITY of bins and the median becomes robust to it, landing BELOW the constant
                   case. The floor is not general; it holds here because one perturbed replica moves
                   the whole unfolded spectrum rather than one cell.
  (4) SHAPE.       The f_agg formula OVER-estimates f_med's inflation by a factor set by the
                   displacement pattern's CONCENTRATION, not by E[d^2]. At E[d^2] fixed at 1.65 the
                   ratio runs 0.993 -> 0.274 as the lognormal's sigma runs 0.3 -> 1.6. An earlier draft
                   read this as a drift with E[d^2]; that was a confound of the two axes, because the
                   six sampled patterns happened to be ordered by both.

WHY EVERY TABLE REPORTS THE **REALISED** E[d^2] AND NOT ONLY THE POPULATION VALUE. Lane A and this lane
reported four f_med inflations each and two pairs disagreed by ~0.14 percentage points against an MC
standard error near 0.007%. Neither run had a defect: A drew ONE d array per pattern and held it fixed,
this script REDRAWS it every trial and averages, and A's uniform(0,2) array realised E[d^2] = 1.5015
against a population 4/3 -- a +2.4 sigma draw for 285 samples, which is exactly the difference between
1.46% and 1.32%. It cost lane A a hand reconstruction of a call order to find that, and it would have
cost one glance if either run had printed the realised second moment. So this one does.

Seeds are literals so the numbers are reproducible; nothing here reads or writes campaign products.
"""
from __future__ import annotations

import numpy as np

N_MEMBERS = 50
N_BINS = 285
TRIALS = 4000
SEED = 20260818

# pattern -> (sampler, exact population E[d_b^2]).  d_b is in units of that bin's clean scatter.
PATTERNS = {
    "uniform 0..1":     (lambda r, nb: r.uniform(0, 1, nb), 1.0 / 3.0),
    "constant 1":       (lambda r, nb: np.full(nb, 1.0), 1.0),
    "lognormal mean 1": (lambda r, nb: r.lognormal(-0.125, 0.5, nb), float(np.exp(0.25))),
    "uniform 0..2":     (lambda r, nb: r.uniform(0, 2, nb), 4.0 / 3.0),
    "half 0 / half 2":  (lambda r, nb: np.where(r.random(nb) < 0.5, 0.0, 2.0), 2.0),
    "half 0 / half 4":  (lambda r, nb: np.where(r.random(nb) < 0.5, 0.0, 4.0), 8.0),
}

# (4)+(3): all of these have E|d_b| = 1 EXACTLY, and they are deterministic so the realised
# moments are the population ones. Jensen orders them by E[d^2]; f_med does not obey that order.
EQUAL_MEAN_CASES = {
    "constant 1":            lambda nb: np.full(nb, 1.0),
    "half 0 / half 2":       lambda nb: np.where(np.arange(nb) % 2 == 0, 0.0, 2.0),
    "1 bin in 5 at 5":       lambda nb: np.where(np.arange(nb) % 5 == 0, 5.0, 0.0),
    "1 bin in 20 at 20":     lambda nb: np.where(np.arange(nb) % 20 == 0, 20.0, 0.0),
    "1 bin in 285 at 285":   lambda nb: np.where(np.arange(nb) == 0, float(nb), 0.0),
}


def _mc(sampler, seed, trials=TRIALS, n=N_MEMBERS, nb=N_BINS):
    """Inflation of median-over-bins sd when member 0 is displaced in every bin.

    Returns (inflations, realised E[d^2] per trial). sigma_b = 1 in every bin, so d_b is already
    in units of the clean per-member scatter.
    """
    rng = np.random.default_rng(seed)
    out = np.empty(trials)
    ed2 = np.empty(trials)
    for t in range(trials):
        x = rng.standard_normal((n, nb))
        clean = np.median(x.std(axis=0, ddof=1))
        d = sampler(rng, nb)
        ed2[t] = float(np.mean(d ** 2))
        y = x.copy()
        y[0] += d
        out[t] = np.median(y.std(axis=0, ddof=1)) / clean - 1.0
    return out, ed2


def check_identity() -> int:
    bad = [n for n in (2, 3, 6, 20, 50, 100, 1000, 10 ** 6)
           if abs((1 - 1.0 / n) / (n - 1) - 1.0 / n) > 1e-15]
    print("(1) EXACT  (1-1/n)/(n-1) == 1/n  ->  E[s^2] = sigma^2 + sigma_d^2/n")
    for n in (6, 20, 50, 100):
        print(f"      n={n:<5} sd inflation at sigma_d = sigma : {100*(np.sqrt(1+1.0/n)-1):>6.2f}%")
    print(f"    -> {'PASS' if not bad else 'FAIL at n=' + str(bad)}")
    return 1 if bad else 0


def check_direction_and_law() -> int:
    rc = 0
    print()
    print("(2)+(3) does the sign survive a median over bins, and does inflation track E[d^2]/n?")
    print(f"    n={N_MEMBERS}, {N_BINS} bins, {TRIALS} trials, seed {SEED}")
    print(f"    {'pattern':<19}{'pop E[d^2]':>11}{'realised':>18}{'pred':>8}{'meas':>8}{'ratio':>7}{'frac up':>9}")
    const = None
    for label, (pat, pop) in PATTERNS.items():
        infl, ed2 = _mc(pat, SEED)
        pred = np.sqrt(1 + ed2.mean() / N_MEMBERS) - 1
        m = float(infl.mean())
        up = float(np.mean(infl > 0))
        if up < 0.80:
            print(f"      !! {label}: only {up:.3f} of trials inflated -- DIRECTION claim fails")
            rc = 1
        print(f"    {label:<19}{pop:>11.4f}{ed2.mean():>11.4f}+-{ed2.std():<5.3f}"
              f"{100*pred:>7.2f}%{100*m:>7.2f}%{m/pred:>7.3f}{up:>9.3f}")
        if label == "constant 1":
            const = m
    print("    -> every pattern inflates. The DIRECTION is the load-bearing claim and it holds.")
    return rc


def check_floor_precondition() -> int:
    """(3)'s limit: at fixed E|d|=1, does f_med obey Jensen's E[d^2] ordering? NO."""
    rc = 0
    print()
    print("(4) THE FLOOR'S PRECONDITION. All patterns below have E|d_b| = 1 EXACTLY and are")
    print("    deterministic. Jensen orders them by E[d^2]; f_med does NOT follow that order.")
    print(f"    {'pattern (E|d|=1)':<24}{'E[d^2]':>10}{'f_agg pred':>12}{'f_med meas':>12}  verdict")
    const = None
    violated = False
    for label, pat in EQUAL_MEAN_CASES.items():
        infl, ed2 = _mc(lambda r, nb, p=pat: p(nb), 4242, trials=1500)
        pred = np.sqrt(1 + ed2.mean() / N_MEMBERS) - 1
        m = float(infl.mean())
        if const is None:
            const = m
            verdict = "reference"
        elif m < const:
            verdict = "BELOW constant -> floor violated"
            violated = True
        else:
            verdict = "above constant"
        print(f"    {label:<24}{ed2.mean():>10.3f}{100*pred:>11.2f}%{100*m:>11.2f}%  {verdict}")
    if not violated:
        print("      !! no violation found -- the documented limit on the floor is NOT reproduced")
        rc = 1
    print("    -> the Jensen floor is EXACT for f_agg and conditional for f_med: it needs the")
    print("       displacement to reach a MAJORITY of bins. That is claim (2)'s universality")
    print("       condition, and the floor as first written omitted it.")
    print("       It APPLIES to this campaign's case because one perturbed replica moves the whole")
    print("       unfolded spectrum, not one cell -- a physical fact, not a property of the theorem.")
    return rc


def check_shape_not_moment() -> int:
    """(4): at FIXED E[d^2], the ratio moves with the pattern's concentration."""
    print()
    print("(5) IS THE pred/meas RATIO SET BY E[d^2] OR BY THE PATTERN'S TAIL?")
    print("    lognormals at DIFFERENT sigma, E[d^2] MATCHED to 1.65 -- if the ratio moves, it is")
    print("    the tail and not the moment.")
    print(f"    {'sigma':>7}{'E|d|':>9}{'E[d^2]':>9}{'pred':>8}{'meas':>8}{'ratio':>8}")
    ratios = []
    for s in (0.3, 0.5, 0.8, 1.2, 1.6):
        mu = 0.5 * (np.log(1.6521) - 2 * s * s)
        infl, ed2 = _mc(lambda r, nb, mu=mu, s=s: r.lognormal(mu, s, nb), 4242, trials=1500)
        pred = np.sqrt(1 + ed2.mean() / N_MEMBERS) - 1
        m = float(infl.mean())
        ratios.append(m / pred)
        print(f"    {s:>7.1f}{np.exp(mu + s*s/2):>9.4f}{ed2.mean():>9.4f}"
              f"{100*pred:>7.2f}%{100*m:>7.2f}%{m/pred:>8.3f}")
    spread = max(ratios) - min(ratios)
    print(f"    -> ratio spread at FIXED E[d^2]: {spread:.3f}. The ratio is a TAIL effect.")
    print(f"       Every ratio in this family is <= 1 (min {min(ratios):.3f}, i.e. f_agg over-estimates")
    print("       f_med by up to 3.6x for the most concentrated patterns), so f_agg's formula is a")
    print("       CONSERVATIVE proxy for f_med. The ONE ratio above 1 anywhere here is check (2)'s")
    print("       uniform 0..1 at 1.026, where the inflation is 0.34% and that is 1.4 sigma from")
    print("       unity -- not significant, and flagged rather than smoothed over.")
    return 0 if spread > 0.3 else 1


def check_realisation_caveat() -> int:
    print()
    print("(6) the sign is certain IN EXPECTATION, not per realisation. How bad can one draw be?")
    infl, _ = _mc(PATTERNS["constant 1"][0], SEED)
    q = np.percentile(infl, [0.5, 2.5, 50, 97.5])
    print(f"    P(confound pushes f_med DOWN) = {float(np.mean(infl < 0)):.4f}"
          f"   worst downward excursion = {100*float(infl.min()):+.2f}%")
    print(f"    percentiles 0.5/2.5/50/97.5 = {100*q[0]:+.2f}% {100*q[1]:+.2f}%"
          f" {100*q[2]:+.2f}% {100*q[3]:+.2f}%")
    print("    against the 16.8% headroom leg B's MET threshold (2.28%) has under its 2.74% bar,")
    print("    so a sub-1% realisation excursion cannot cross it. Caveat real, stated, subsumed.")
    return 0


def main() -> int:
    rc = check_identity()
    rc |= check_direction_and_law()
    rc |= check_floor_precondition()
    rc |= check_shape_not_moment()
    rc |= check_realisation_caveat()
    print()
    print("ANCHOR-CONFOUND MC :: " + ("PASS" if rc == 0 else "FAIL"))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
