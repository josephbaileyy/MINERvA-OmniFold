#!/usr/bin/env python3
"""BV96 O1: the declared power simulation (BV96-DECLARATION.md §8), fixed before its inputs were read.

usage: python3 -I -B bv96_power_sim.py <inputs.json> [--reps R]

THE MODEL. It is a model, not a measurement. At a truth T, with per-functional bias b (sigma_rel units, from the
noise-free closure of (e) at one of F0b's 17 development truths) and per-cell bias bc (relative), each pseudo-experiment
m draws:
- statistical noise s ~ N(0, 1) per functional, equicorrelated with rho in {0, 0.5, 0.9}. On the cells, s_c ~ N(0,
  sigma_pc^2), the same rho, with sigma_pc = S1's per-cell statistical sigma / the receipt's data-over-pseudo factor;
- F's rounding deviation eps: one of the 52 centred rounding rows of the stability input, scaled by sqrt(52/51) so its
  variance is sd51^2 (ddof 1), resampled with replacement. The same row gives the cells' deviation;
- E96's residual: an independent resampled row divided by sqrt(96).
The null of BV96's power is "E96 removes F's rounding variance and leaves its bias unchanged":
  e^E = b + s + eps'/sqrt(96),   e^F = b + s + eps.
Then §6 exactly: d_m = mean_j[(e^E)^2 - (e^F)^2]; A_T, SE_T (ddof 1); E-better if A_T + 2.241 SE_T < -0.05; F-better if
A_T - 2.241 SE_T > +0.05; harm at a cell if D_Tc - 2.955 SE_Tc > 0.25 V^F_Tc.

THE READINGS, fixed now:
- per truth, M and rho: P(E-better at T), P(F-better at T), P(harm at any cell at T);
- per M and rho: P(E-better at both) = P_a * P_b over the 136 pairs of distinct truths (the reserved truths are
  independent draws), summarised by its median, 10th percentile and minimum;
- THE HEADLINE, the director's O1 criterion: at each M, the minimum over rho of the median over pairs of P(E-better at
  both). M = 30 stands if it is >= 0.8. Otherwise the smallest M in {20, 30, 40, 60} that reaches 0.8 is reported, with
  its price at §9's unit.
Seed 20261110. numpy only.
"""
import argparse
import hashlib
import itertools
import json
import sys

import numpy as np

SEED = 20261110
MS = (20, 30, 40, 60)
RHOS = (0.0, 0.5, 0.9)
Z_T, Z_CELL, MARGIN, HARM = 2.241, 2.955, 0.05, 0.25
UNIT, UNIT_MAX, GEN, DRY = 0.020258, 0.027529, 0.414722, 9


def price(M):
    n = 2 * M * 97 + 2 * 97 + 2
    return n, n * UNIT + GEN


def simulate(rng, b, bc, rows, rows_c, spc, M, rho, reps):
    nf, nc, nr = b.size, bc.size, rows.shape[0]
    k = np.sqrt(nr / (nr - 1))

    def noise(n, scale):
        z0 = rng.standard_normal((reps, M, 1))
        z = rng.standard_normal((reps, M, n))
        return (np.sqrt(rho) * z0 + np.sqrt(1 - rho) * z) * scale

    i_f = rng.integers(0, nr, (reps, M))
    i_e = rng.integers(0, nr, (reps, M))
    s = noise(nf, 1.0)
    eE = b + s + k * rows[i_e] / np.sqrt(96)
    eF = b + s + k * rows[i_f]
    d = np.mean(eE ** 2 - eF ** 2, axis=2)                       # reps x M
    A, SE = d.mean(axis=1), d.std(axis=1, ddof=1) / np.sqrt(M)
    e_better = A + Z_T * SE < -MARGIN
    f_better = A - Z_T * SE > MARGIN
    sc = noise(nc, spc)
    rE = bc + sc + k * rows_c[i_e] / np.sqrt(96)
    rF = bc + sc + k * rows_c[i_f]
    D = rE ** 2 - rF ** 2                                        # reps x M x 16
    Dm, Ds = D.mean(axis=1), D.std(axis=1, ddof=1) / np.sqrt(M)
    VF = rF.var(axis=1, ddof=1)
    harm = np.any(Dm - Z_CELL * Ds > HARM * VF, axis=1)
    return float(e_better.mean()), float(f_better.mean()), float(harm.mean())


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs")
    ap.add_argument("--reps", type=int, default=2000)
    a = ap.parse_args(argv)
    raw = open(a.inputs, "rb").read()
    d = json.loads(raw)
    rows, rows_c = np.asarray(d["rounding_rows_sigma"]), np.asarray(d["rounding_rows_cells"])
    spc = np.asarray(d["s1_stat_rel_sigma"]) / d["data_sigma_over_pseudo_sigma"]
    truths = d["truth_names"]
    off = {r["truth"]: np.asarray(r["values"]) for r in d["offset_sigma"]}
    offc = {r["truth"]: np.asarray(r["values"]) for r in d["offset_cells"]}
    print(f"inputs sha256 {hashlib.sha256(raw).hexdigest()}; seed {SEED}; reps {a.reps}; truths {len(truths)}")
    print("bias scale per truth (median |b_j| in sigma_rel; RMS cell bias):")
    for t in truths:
        b = off[t]
        print(f"  {t:16s} median|b| {np.median(np.abs(b)):8.3f}  max|b| {np.max(np.abs(b)):9.3f}  "
              f"rms cell {np.sqrt(np.mean(np.square(offc[t]))):.5f}")
    rng = np.random.default_rng(SEED)
    res = {}
    for M in MS:
        for rho in RHOS:
            for t in truths:
                res[(M, rho, t)] = simulate(rng, off[t], offc[t],
                                            rows, rows_c, spc, M, rho, a.reps)
    print("\nper truth, P(E-better) / P(F-better) / P(harm), at M = 30:")
    for t in truths:
        print(f"  {t:16s} " + "  ".join(f"rho {r}: {res[(30, r, t)][0]:.3f}/{res[(30, r, t)][1]:.3f}/{res[(30, r, t)][2]:.3f}"
                                         for r in RHOS))
    print("\nP(E-better at both) over the 136 pairs (median / 10th pct / min), and the headline:")
    head = {}
    for M in MS:
        meds = []
        for rho in RHOS:
            p = np.array([res[(M, rho, x)][0] * res[(M, rho, y)][0] for x, y in itertools.combinations(truths, 2)])
            meds.append(float(np.median(p)))
            print(f"  M {M:2d} rho {rho}: {np.median(p):.3f} / {np.percentile(p, 10):.3f} / {p.min():.3f}")
        head[M] = min(meds)
        n, nh = price(M)
        print(f"  M {M:2d} HEADLINE (min over rho of the median): {head[M]:.3f}   [{n} unfolds, {nh:.1f} node-h expected]")
    ok30 = head[30] >= 0.8
    reach = [M for M in MS if head[M] >= 0.8]
    print(f"\nBV96-POWER :: M = 30 {'STANDS' if ok30 else 'BELOW 0.8'} (headline {head[30]:.3f}); "
          f"smallest M reaching 0.8: {reach[0] if reach else 'none of ' + str(MS)}"
          + (f", {price(reach[0])[1]:.1f} node-h expected" if reach else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
