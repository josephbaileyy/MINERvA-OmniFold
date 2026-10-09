#!/usr/bin/env python3
"""Reviewer OC-curve spot check (own code): pass probability of one functional vs kappa at N=719."""
from scipy import stats
N = 719; alpha = 0.04 / 412
for k, z, a, b in (("I68", 1.0, 441, 539), ("I95", stats.norm.ppf(0.975), 658, 703)):
    for kap in (0.9, 0.95, 1.0, 1.05, 1.1):
        p = 2 * stats.t.cdf(z / kap, 299) - 1
        print(k, kap, round(p, 5), round(stats.binom.cdf(b, N, p) - stats.binom.cdf(a - 1, N, p), 4))
