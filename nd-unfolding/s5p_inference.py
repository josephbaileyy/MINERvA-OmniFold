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


def cp_interval(k: int, B: int, level: float) -> tuple[float, float]:
    a = 1 - level
    lo = 0.0 if k == 0 else float(stats.beta.ppf(a / 2, k, B - k + 1))
    hi = 1.0 if k == B else float(stats.beta.ppf(1 - a / 2, k + 1, B - k))
    return lo, hi


def holm_thresholds(alpha: float, m: int) -> list[float]:
    """Every level a Holm step can compare a raw p-value with: alpha / j, j = 1..m."""
    return sorted(alpha / j for j in range(1, m + 1))


def sequential_decision(k: int, B: int, thresholds: list[float], look_level: float = 0.995) -> dict:
    """The frozen batch-sequential stopping rule of a calibration ensemble (s5p amendment 7 candidate).

    With k exceedances in B null draws, stop only when the exact Clopper-Pearson interval of the tail
    probability at ``look_level`` (Bonferroni over at most ten looks: 0.995) (a) contains no decision threshold
    (every Holm, 0.05 and 0.01 comparison is determined) and (b) meets the T7 precision at the point estimate
    p = (k + 1) / (B + 1): half-width <= 0.05 for p >= 0.05, <= 0.5 p for 0.01 <= p < 0.05, and below 0.01 an
    upper end below the smallest threshold (a one-sided bound). Continuing is always allowed up to the
    declared maximum."""
    lo, hi = cp_interval(k, B, look_level)
    p = (k + 1) / (B + 1)
    straddle = [th for th in thresholds if lo < th <= hi]
    half = (hi - lo) / 2
    if hi < min(thresholds):
        precise, tier = True, "one-sided bound below every threshold"
    elif p >= 0.05:
        precise, tier = half <= 0.05, "absolute half-width <= 0.05"
    elif p >= 0.01:
        precise, tier = half <= 0.5 * p, "relative half-width <= 0.5 p"
    else:
        precise, tier = False, "p < 0.01 without a bound below every threshold"
    return {"k": k, "B": B, "p": p, "look_interval": [lo, hi], "look_level": look_level,
            "straddled_thresholds": straddle, "precise": precise, "tier": tier, "stop": precise and not straddle}


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


def holm_determined(entries: dict[str, dict], alpha: float = 0.05, level: float = 0.95) -> dict:
    """Holm step-down with the determinacy rule of the s5p admission (review round 2 M3). ``entries`` maps a
    test to its claim {"p", "k", "B"}. In increasing p, step i compares with alpha / (m - i): the test is
    REJECTED if the exact Clopper-Pearson interval (``level``) of k / B lies entirely below the threshold; the
    procedure STOPS with 'not rejected' for this and every later test if the interval lies entirely above; it
    STOPS with 'undetermined' for this and every later test if the interval contains the threshold (no claim
    either way at that level; more calibration draws would decide)."""
    order = sorted(entries, key=lambda k: entries[k]["p"])
    m = len(order)
    out, state = {}, None
    for i, key in enumerate(order):
        e = entries[key]
        th = alpha / (m - i)
        lo, hi = cp_interval(int(e["k"]), int(e["B"]), level)
        if state is None:
            if hi < th:
                decision = "rejected"
            elif lo > th:
                state = decision = "not rejected"
            else:
                state = decision = "undetermined"
        else:
            decision = state
        out[key] = {"p": e["p"], "k": int(e["k"]), "B": int(e["B"]), "threshold": th, "interval": [lo, hi],
                    "level": level, "decision": decision}
    return out


def power_determined(t_alt: np.ndarray, t_nulls: list, alpha: float, level: float = 0.95) -> dict:
    """The fraction of alternative experiments the admission's rule would REJECT at ``alpha``: under the claim rule
    k is the largest exceedance count over the null variants, and a rejection needs the Clopper-Pearson interval
    of k / B entirely below alpha (review round 2 M3)."""
    t_alt = np.asarray(t_alt, float)
    ks = []
    for tn in t_nulls:
        s = np.sort(np.asarray(tn, float))
        ks.append(s.size - np.searchsorted(s, t_alt, side="left"))
    k = np.max(np.array(ks), axis=0)
    B = np.asarray(t_nulls[0]).size
    rej = np.array([cp_interval(int(x), B, level)[1] < alpha for x in k])
    n, x = rej.size, int(rej.sum())
    lo, hi = cp_interval(x, n, level)
    return {"power": x / n, "n": n, "interval": [lo, hi], "alpha": alpha, "B": B, "rule": "claim rule with determinacy"}


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
