#!/usr/bin/env python3
"""ENS1 power simulation (ENS1-DECLARATION.md §5.3): what FD-STAB's §4.3 statistic reads for the ensemble E_N.

A model, not a measurement. Per functional j, one fit's rounding deviation is sigma_j * e in pseudo-data sigma units,
with log sigma_j ~ N(mu, tau^2) over the 153 functionals (a fixed population per scenario) and an equicorrelation rho
between functionals (one shared factor per fit). A fraction c of each fit's variance is COMMON to the N fits of one
input (it is a function of the input, so averaging cannot remove it); the rest is independent across fits.

Calibration: (mu, tau) are fitted so that ONE fit (N = 1) at P = 25 reproduces FD-STAB's control, mean median 0.759
and mean max 6.83 (fd_stab.json, readout-2, sha256 653356ae...). The statistic is scale-equivariant in sigma, so
max/median fixes tau and the median then fixes mu. The model's SD51 median and max are printed as a check against
the record's 0.581 and 2.515, which the fit does not use.

Then the ensemble at P = 10 and N in {64, 96}; N = 96 is declared (the director's ruling after the N = 64 rows read
P(pass) of about 0.8 with exact 1/sqrt(N)). The bars are 0.3 / 1.0 on the mean over pairs.
Gaussian fits use the exact scaling sigma_E = sigma * sqrt(c + (1 - c) / N); the heavy-tailed scenario (Student t,
3 dof, unit variance) averages 64 draws explicitly.

    python3 ens_power_sim.py > ens_power_sim.out.txt
"""
from __future__ import annotations

import math
import sys

import numpy as np

SEED = 20261107
F = 153
TARGET_MED, TARGET_MAX = 0.7590659388438921, 6.827531337314785    # fd_stab.json stability.control
TARGET_SD51_MED, TARGET_SD51_MAX = 0.5813263504107288, 2.515279781523872
BOUND_MEDIAN, BOUND_MAX = 0.3, 1.0
N_GRID, N_ENS, P_ENS = (64, 96), 96, 10   # N = 96 is the declared ensemble (director, 2026-11-07)


def draw(rng, n_inputs: int, reps: int, rho: float, tail: str, n_avg: int, c: float) -> np.ndarray:
    """(reps, n_inputs, F) unit-scale deviations of one estimator output per input: the mean of n_avg fits."""
    def fits(k):
        shape = (reps, n_inputs, k, F)
        if tail == "gauss":
            z = rng.standard_normal(shape)
            g = rng.standard_normal((reps, n_inputs, k, 1))
        else:  # Student t, 3 dof, scaled to unit variance
            z = rng.standard_t(3, shape) / math.sqrt(3.0)
            g = rng.standard_t(3, (reps, n_inputs, k, 1)) / math.sqrt(3.0)
        return math.sqrt(1 - rho) * z + math.sqrt(rho) * g
    common = fits(1)[:, :, 0, :]
    if tail == "gauss":
        idio = fits(1)[:, :, 0, :] / math.sqrt(n_avg)
    else:
        idio = np.mean(fits(n_avg), axis=2)
    return math.sqrt(c) * common + math.sqrt(1 - c) * idio


def statistic(dev: np.ndarray, sigma: np.ndarray, pairs: int) -> tuple[np.ndarray, np.ndarray]:
    """FD-STAB §4.3 per replication: r = output(x_s) - output(x) (the base is input 0), the larger |r|/1 of each
    disjoint pair, then the median and max over functionals, then the mean over the pairs."""
    r = (dev[:, 1:, :] - dev[:, :1, :]) * sigma
    z = np.abs(r)
    m = np.maximum(z[:, 0:2 * pairs:2, :], z[:, 1:2 * pairs:2, :])
    return np.median(m, axis=2).mean(axis=1), np.max(m, axis=2).mean(axis=1)


def population(tau: float) -> np.ndarray:
    q = (np.arange(F) + 0.5) / F
    from statistics import NormalDist
    return np.exp(tau * np.array([NormalDist().inv_cdf(v) for v in q]))


def calibrate(rho: float, tail: str, rng) -> tuple[float, float]:
    best = None
    for tau in np.linspace(0.3, 2.0, 35):
        s = population(tau)
        med, mx = statistic(draw(rng, 51, 300, rho, tail, 1, 0.0), s, 25)
        ratio = mx.mean() / med.mean()
        err = abs(math.log(ratio / (TARGET_MAX / TARGET_MED)))
        if best is None or err < best[0]:
            best = (err, tau, med.mean())
    _, tau, med = best
    return tau, TARGET_MED / med   # sigma_j = scale * population(tau)


def main() -> int:
    rng = np.random.default_rng(SEED)
    print(f"# ENS1 power simulation, seed {SEED}; python {sys.version.split()[0]}, numpy {np.__version__}")
    print(f"# targets (one fit, P = 25): mean median {TARGET_MED:.3f}, mean max {TARGET_MAX:.2f}; "
          f"check only: SD51 median {TARGET_SD51_MED:.3f}, max {TARGET_SD51_MAX:.3f}")
    print(f"# ensemble N in {N_GRID} (declared {N_ENS}), P = {P_ENS}; bars mean median <= {BOUND_MEDIAN}, mean max <= {BOUND_MAX}")
    print(f"# 1/sqrt(N) expectation from the record: median {TARGET_MED / math.sqrt(N_ENS):.3f}, "
          f"max {TARGET_MAX / math.sqrt(N_ENS):.3f}; c* (common fraction at which the expected max meets 1.0) = "
          f"{(1 / TARGET_MAX) ** 2 - 1 / N_ENS:.4f} under exact scaling")
    print("tail  rho   tau   one-fit(P=25) med/max   SD51 med/max   N    c       E[med]  E[max]  sd(max)  P(pass)")
    for tail in ("gauss", "t3"):
        for rho in (0.0, 0.5, 0.9):
            tau, scale = calibrate(rho, tail, rng)
            s = scale * population(tau)
            med1, mx1 = statistic(draw(rng, 51, 400, rho, tail, 1, 0.0), s, 25)
            d1 = draw(rng, 52, 400, rho, tail, 1, 0.0)
            sd = np.std(np.concatenate([np.zeros((400, 1, F)), (d1[:, 1:, :] - d1[:, :1, :]) * s], axis=1),
                        axis=1, ddof=1)
            sd_med, sd_max = float(np.median(np.median(sd, axis=1))), float(np.median(np.max(sd, axis=1)))
            for n_ens, c in [(n, c) for n in N_GRID for c in (0.0, 0.002, 0.005, 0.01, 0.02, 0.05)]:
                chunks = [2000] if tail == "gauss" else [50] * 6
                res = [statistic(draw(rng, 2 * P_ENS + 1, n, rho, tail, n_ens, c), s, P_ENS) for n in chunks]
                med, mx = np.concatenate([r[0] for r in res]), np.concatenate([r[1] for r in res])
                ok = (med <= BOUND_MEDIAN) & (mx <= BOUND_MAX)
                print(f"{tail:5s} {rho:4.1f} {tau:5.2f}   {med1.mean():6.3f} / {mx1.mean():5.2f}        "
                      f"{sd_med:5.3f} / {sd_max:5.2f}   {n_ens:3d}  {c:6.3f}  {med.mean():6.3f}  {mx.mean():6.3f}  "
                      f"{mx.std():6.3f}   {ok.mean():6.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
