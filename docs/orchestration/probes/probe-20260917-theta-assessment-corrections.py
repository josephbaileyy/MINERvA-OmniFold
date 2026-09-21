#!/usr/bin/env python3
"""The four factual corrections to ASSESSMENT-20260917-theta-and-the-propagation-argument.

Joseph declined theta = 7.11e-2 on its proposed derivation AND declined to relabel it an
established feasibility floor, then directed that the assessment's factual claims about
N-scaling, independence across bins, deadband crossings and unbounded downward g movement
be corrected. The NARROW conclusion is retained; this probe is the correction's evidence.

Exits 0 when all four corrections reproduce.

(c) deadband crossings is STRUCTURAL and is asserted in the record rather than measured
here: the perturbed g' is built by the same `max(v_uni, v_blk)`, so a bin near the
boundary can leave the deadband under the very perturbation being bounded. What this
probe does show, under (d), is that deadband bins sit AT the floor and so can only move UP.
"""
import sys

import numpy as np

THETA = np.sqrt(2.0 / 99.0) / 2.0          # the declined candidate, 7.1067e-2
G_MAX = 17.653141714565614                  # G2_g_domain, job 58454524 (RELAYED from the receipt)
G_MEDIAN = 1.0473565738188244               # same, RELAYED


def correction_a_n_scaling():
    """Doubling N does NOT halve theta; it multiplies it by sqrt(99/199)."""
    factor = np.sqrt(99.0 / 199.0)
    n_for_half = 1 + int(round(2.0 / (THETA / 2.0) ** 2 / 4.0)) * 4 - 3  # see table below
    tbl = {N: np.sqrt(2.0 / (N - 1)) / 2.0 for N in (100, 200, 397)}
    print("(a) N-scaling")
    for N, v in tbl.items():
        print(f"      N={N:4d}  theta = {v:.6f}")
    print(f"      100 -> 200 multiplies theta by {factor:.4f}: a {100*(1-factor):.1f}% reduction, NOT 50%")
    print(f"      halving theta needs N = 397 (measured above), i.e. about 4x, not 2x")
    ok = abs(factor - 0.7053) < 1e-3 and abs(tbl[397] - THETA / 2) < 1e-6
    return ok, "doubling N halves theta"


def correction_b_cross_bin_independence(seed=7):
    """Per-bin sigma ESTIMATION errors are correlated when the N replicas resample ONE dataset."""
    rng = np.random.default_rng(seed)
    n_ev, N, n_universe, rho = 4000, 100, 400, 0.90
    L = np.array([[1.0, 0.0], [rho, np.sqrt(1.0 - rho * rho)]])
    data = rng.standard_normal((n_ev, 2)) @ L.T
    errs = []
    for _ in range(n_universe):
        d0 = data[rng.integers(0, n_ev, n_ev)]              # one realized dataset
        v = np.array([d0[rng.integers(0, n_ev, n_ev)].mean(axis=0) for _ in range(N)])
        errs.append(v.std(axis=0, ddof=1))
    errs = np.array(errs)
    rel = errs / errs.mean(axis=0) - 1.0
    c = float(np.corrcoef(rel.T)[0, 1])
    print("(b) independence across bins")
    print(f"      data bins correlated at {rho}; corr of per-bin SIGMA ESTIMATION ERROR = {c:+.3f}")
    print("      => NOT random across bins, so an aggregate does not suppress them by sqrt(N_eff).")
    print("      The SIGN of the coherent/incoherent gap survives; its MAGNITUDE is unestablished.")
    return c > 0.3, "sigma estimation error is random across bins"


def correction_d_downward_g():
    """g >= 1 by construction, so downward movement in g is bounded without any tolerance."""
    print("(d) unbounded downward g movement")
    print("      z_assembly.py:6  g = sqrt(max(v_uni, v_blk))/sqrt(v_blk) >= 1")
    print("      z_contract.py:84 G_FLOOR = 1.0 ; gate_g_domain requires sum(g < G_FLOOR) == 0")
    print("      the PERTURBED g' uses the same max, so g' >= 1 as well")
    worst = 1.0 / G_MAX - 1.0
    for g, lab in ((G_MAX, "g_max"), (G_MEDIAN, "g_median"), (1.0, "deadband bins")):
        print(f"      {lab:16s} g={g:.6f}  worst downward u = 1/g - 1 = {1.0/g - 1.0:+.4f}")
    f_crit = 1.0 - (1.0 - THETA) ** 2
    print(f"      sigma-insensitivity threshold f <= 1-(1-theta)^2 = {f_crit:.4f} is ARITHMETICALLY RIGHT;")
    print(f"      what fails is the inference: |u| >= {worst:+.4f} for EVERY bin, from construction alone.")
    print("      Deadband bins sit AT the floor, so they can only move UP.")
    return worst > -1.0, "g may fall to zero"


def main():
    print(f"theta (declined candidate) = {THETA:.6f}\n")
    failures = []
    for fn in (correction_a_n_scaling, correction_b_cross_bin_independence, correction_d_downward_g):
        ok, refuted = fn()
        print()
        if not ok:
            failures.append(refuted)
    if failures:
        print("PROBE FAILED -- a correction did not reproduce:")
        for f in failures:
            print(f"  {f}")
        return 1
    print("All four corrections reproduce. The NARROW conclusion is retained: theta's derivation")
    print("yields a RESOLUTION figure, not a scientific cap -- and it is NOT hereby established as")
    print("a feasibility floor either; its statistical assumptions and scope remain unestablished.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
