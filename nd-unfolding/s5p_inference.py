#!/usr/bin/env python3
"""s5p Stage 7: the joint-test statistics and their Monte Carlo calibration (library and evaluator).

Statistics on the joint reporting cells of one definition (the assembly's functionals minus the total and
the (E_avail,W) rows), for a fixed prediction mu of those cells and a FIXED weighting matrix V (declared at
Stage 3; calibration by simulation of the complete procedure makes the test valid whatever V is, so V only
sets the power):

* total (rate and shape): ``T = r' V^-1 r``, ``r = f - mu``;
* shape-only: ``f`` and ``mu`` are normalized to their sums over the cells; the normalized residual has the
  propagated covariance ``V_s = J V J'`` with ``J = (I - p 1') / sum f`` whose rank deficiency is exactly one
  (the known constraint), so the last cell is dropped and ``T_s = r_s' V_s^-1 r_s`` over the others (invariant
  to which cell is dropped); no pseudoinverse cutoff is used.

Calibration: ``p = (k + 1) / (B + 1)`` with ``k`` the number of null statistics >= the observed one, with the
exact Clopper-Pearson interval of the tail probability k / B; or the Besag-Clifford sequential rule (stop at
the h-th exceedance: p = h / n; otherwise (k + 1) / (n_max + 1)), which is valid for any stopping. Holm over a
declared family. Power: the fraction of alternative statistics above the null ensemble's (1 - alpha) quantile
defined by the same rank rule, with its exact interval.

MEASURES: test statistics, Monte Carlo p-values and power estimates. CANNOT AUTHORIZE: a rejection claim
outside the frozen family, precision tier and multiplicity rule; any statement about uncalibrated tails.
"""
from __future__ import annotations

import numpy as np
from scipy import stats


def stat_total(f: np.ndarray, mu: np.ndarray, Vinv: np.ndarray) -> float:
    r = np.asarray(f, float) - np.asarray(mu, float)
    return float(r @ Vinv @ r)


def shape_parts(f: np.ndarray, V: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    f = np.asarray(f, float)
    s = f.sum()
    p = f / s
    J = (np.eye(f.size) - np.outer(p, np.ones(f.size))) / s
    return p, J @ V @ J.T


def stat_shape(f: np.ndarray, mu: np.ndarray, V: np.ndarray, drop: int = -1) -> float:
    p, Vs = shape_parts(f, V)
    q = np.asarray(mu, float) / np.asarray(mu, float).sum()
    keep = np.ones(p.size, bool)
    keep[drop] = False
    r = (p - q)[keep]
    return float(r @ np.linalg.solve(Vs[np.ix_(keep, keep)], r))


def mc_pvalue(t_obs: float, t_null: np.ndarray, level: float = 0.95) -> dict:
    t_null = np.asarray(t_null, float)
    B = t_null.size
    k = int(np.sum(t_null >= t_obs))
    a = 1 - level
    lo = 0.0 if k == 0 else float(stats.beta.ppf(a / 2, k, B - k + 1))
    hi = 1.0 if k == B else float(stats.beta.ppf(1 - a / 2, k + 1, B - k))
    return {"p": (k + 1) / (B + 1), "k": k, "B": B, "tail_interval": [lo, hi], "level": level}


def besag_clifford(t_obs: float, t_null_stream, h: int, n_max: int) -> dict:
    """Sequential Monte Carlo p-value: draw nulls in the given order; stop at the h-th exceedance."""
    k = 0
    n = 0
    for t in t_null_stream:
        n += 1
        if t >= t_obs:
            k += 1
            if k == h:
                return {"p": h / n, "stopped_at": n, "exceedances": k, "rule": "h-th exceedance"}
        if n == n_max:
            break
    return {"p": (k + 1) / (n_max + 1), "stopped_at": n, "exceedances": k, "rule": "n_max reached"}


def holm(pvals: dict[str, float], alpha: float = 0.05) -> dict:
    order = sorted(pvals, key=pvals.get)
    m = len(order)
    out, running, stop = {}, 0.0, False
    for i, key in enumerate(order):
        adj = min(1.0, (m - i) * pvals[key])
        running = max(running, adj)
        reject = (not stop) and pvals[key] <= alpha / (m - i)
        stop = stop or not reject
        out[key] = {"p_raw": pvals[key], "p_holm": running, "reject": reject}
    return out


def critical_value(t_null: np.ndarray, alpha: float) -> float:
    """The smallest t with (k(t) + 1) / (B + 1) <= alpha under the rank rule."""
    t = np.sort(np.asarray(t_null, float))[::-1]
    B = t.size
    kmax = int(np.floor(alpha * (B + 1) - 1))
    if kmax < 0:
        return float("inf")
    return float(t[kmax]) if kmax < B else float(-np.inf)


def power(t_alt: np.ndarray, t_null: np.ndarray, alpha: float = 0.05, level: float = 0.95) -> dict:
    t_alt = np.asarray(t_alt, float)
    B = t_null.size
    # reject iff (#{null >= t} + 1) / (B + 1) <= alpha
    rej = np.array([(np.sum(t_null >= t) + 1) / (B + 1) <= alpha for t in t_alt])
    n, x = rej.size, int(rej.sum())
    a = 1 - level
    lo = 0.0 if x == 0 else float(stats.beta.ppf(a / 2, x, n - x + 1))
    hi = 1.0 if x == n else float(stats.beta.ppf(1 - a / 2, x + 1, n - x))
    return {"power": x / n, "n": n, "interval": [lo, hi], "alpha": alpha}


def size(t_valid_null: np.ndarray, t_calib_null: np.ndarray, alpha: float, level: float = 0.95) -> dict:
    """Rejection fraction of independent null validation experiments against the calibration ensemble,
    with the one-sided upper confidence bound."""
    p = power(t_valid_null, t_calib_null, alpha, level)
    x, n = int(round(p["power"] * p["n"])), p["n"]
    ucb = 1.0 if x == n else float(stats.beta.ppf(level, x + 1, n - x))
    return {"rejection_fraction": x / n, "n": n, "upper_bound": ucb, "alpha": alpha}
