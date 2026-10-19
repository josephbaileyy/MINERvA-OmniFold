#!/usr/bin/env python3
"""Independent FWER computation for the s5p batch-sequential Monte Carlo decision rule.

Model: for one true null, conditional on the data the null draws exceed T_obs independently with probability p
(the tail probability); under H0 with an exact calibration p ~ U(0,1) (super-uniform if conservative).
Looks after batches: B_j = 200 j (j = 1..9), B_10 = 1999 (s5p_production.seeds_of_batch, max 1999).
Decision at the final B: reject at threshold c iff the two-sided 95% Clopper-Pearson upper end of k/B < c
(s5p_inference.holm_determined). Stopping: s5p_inference.sequential_decision (99.5% look interval, the frozen
thresholds alpha/j and 0.01, 0.05, precision tier), optional min_B, forced stop at the last look.

Holm reduction (no independence needed): the first true null that Holm-with-determinacy rejects is rejected at a
step whose threshold is <= alpha/m0, so FWER <= sum_{i in I0} P(hi_i < alpha/m0) = m0 * R(alpha/m0).

Computes per-test R(c) exactly (DP over k, numerical integral over p) for
  fixed  : fixed B (1999, 1351, 1200),
  frozen : the coded stopping rule (min_B 0 and 1200),
  adv    : any data-dependent stop on the look grid (union over looks of {hi95 < c}): covers the budget extension,
           budget stops, the transitions and any other choice of WHEN to stop among the ten looks,
and the conditional worst case sup_{p >= c} P(reject | p). Then checks with a direct Monte Carlo of the full
ten-test Holm procedure (five nulls x two tests sharing the stopping time).
"""
from __future__ import annotations

import json
import sys

import numpy as np
from scipy import stats

ALPHA = 0.05
M = 10
LOOKS = [200 * j for j in range(1, 10)] + [1999]
TH = sorted(set([ALPHA / j for j in range(1, M + 1)]) | {0.01, 0.05})


def cp(k, B, level):
    a = 1 - level
    lo = 0.0 if k == 0 else float(stats.beta.ppf(a / 2, k, B - k + 1))
    hi = 1.0 if k == B else float(stats.beta.ppf(1 - a / 2, k + 1, B - k))
    return lo, hi


def seq_stop(k, B, th=TH, look=0.995):
    """Verbatim logic of s5p_inference.sequential_decision (L89-111)."""
    lo, hi = cp(k, B, look)
    p = (k + 1) / (B + 1)
    straddle = [t for t in th if lo < t <= hi]
    half = (hi - lo) / 2
    if hi < min(th):
        precise = True
    elif p >= 0.05:
        precise = half <= 0.05
    elif p >= 0.01:
        precise = half <= 0.5 * p
    else:
        precise = False
    return precise and not straddle


KMAX = 120  # k beyond this never rejects or matters for c <= 0.05 at B <= 1999 (checked: k*(0.05,1999) < 120)


def kstar(c, B, level=0.95):
    """Largest k with CP upper < c (-1 if none)."""
    ks = -1
    for k in range(0, KMAX):
        if cp(k, B, level)[1] < c:
            ks = k
        else:
            break
    return ks


def increments_pmf(p, n):
    return stats.binom.pmf(np.arange(KMAX + 1), n, p)


def rej_prob_given_p(p, c, mode, min_b=0, stop_table=None, kst=None):
    """P(reject | p) for one test."""
    dist = np.zeros(KMAX + 1)
    dist[0] = 1.0  # k before the first batch
    prevB = 0
    rej = 0.0
    alive = np.ones(KMAX + 1)  # mass not yet stopped is dist itself
    for j, B in enumerate(LOOKS):
        inc = increments_pmf(p, B - prevB)
        dist = np.convolve(dist, inc)[: KMAX + 1]  # truncation drops mass with k > KMAX (never rejected)
        prevB = B
        ks = kst[j]
        last = j == len(LOOKS) - 1
        if mode == "adv":
            # union over looks: reject mass where k <= k*; remove it (absorbed as rejected)
            if ks >= 0:
                rej += dist[: ks + 1].sum()
                dist[: ks + 1] = 0.0
        elif mode == "frozen":
            stop = stop_table[j] & (B >= min_b)
            if last:
                stop = np.ones_like(stop)
            if ks >= 0:
                rej += dist[: ks + 1][stop[: ks + 1]].sum()
            dist = np.where(stop, 0.0, dist)
        elif mode.startswith("fixed"):
            pass
    return rej


def integrate(fun, c):
    # p ~ U(0,1); integrand ~1 below c, decays above; dense grid on [0, 20c], tail checked
    hi = min(1.0, 20 * c)
    x, w = np.polynomial.legendre.leggauss(60)
    total = 0.0
    edges = np.concatenate([np.linspace(0, c, 9)[:-1], np.linspace(c, 3 * c, 25)[:-1], np.linspace(3 * c, hi, 9)])
    for a, b in zip(edges[:-1], edges[1:]):
        xs = 0.5 * (b - a) * x + 0.5 * (b + a)
        total += 0.5 * (b - a) * np.sum(w * np.array([fun(t) for t in xs]))
    tail = fun(hi)
    return total, tail


def main():
    out = {"looks": LOOKS, "thresholds": TH}
    stop_table = [np.array([seq_stop(k, B) for k in range(KMAX + 1)]) for B in LOOKS]
    out["frozen_rule_stop_set_at_each_look"] = {B: [int(k) for k in np.flatnonzero(st[:40])] for B, st in zip(LOOKS, stop_table)}
    rows = []
    for m0 in range(1, M + 1):
        c = ALPHA / m0
        kst = [kstar(c, B) for B in LOOKS]
        r = {"m0": m0, "c": c, "kstar_per_look": kst}
        for B in (1999, 1351, 1200):
            ks = kstar(c, B)
            r[f"fixed_B{B}"] = (ks + 1) / (B + 1)  # exact: int_0^1 P(Bin(B,p) <= k) dp = (k+1)/(B+1)
        for mode, mb in (("frozen", 0), ("frozen", 1200), ("adv", 0)):
            f = lambda p: rej_prob_given_p(p, c, mode, mb, stop_table, kst)  # noqa: E731
            val, tail = integrate(f, c)
            key = f"{mode}_minB{mb}" if mode == "frozen" else "adv"
            r[key] = val
            r[key + "_tail_at_20c"] = tail
            ps = np.linspace(c, 1.6 * c, 121)
            cond = np.array([f(p) for p in ps])
            r[key + "_sup_cond_p_ge_c"] = float(cond.max())
            r[key + "_argsup_p_over_c"] = float(ps[cond.argmax()] / c)
        r["FWER_bound_over_alpha"] = {k: m0 * r[k] / ALPHA for k in ("fixed_B1999", "fixed_B1351", "fixed_B1200", "frozen_minB0", "frozen_minB1200", "adv")}
        rows.append(r)
        print(json.dumps({"m0": m0, "c": round(c, 5), **{k: round(v, 4) for k, v in r["FWER_bound_over_alpha"].items()},
                          "sup_cond_adv": round(r["adv_sup_cond_p_ge_c"], 4)}), flush=True)
    out["per_m0"] = rows
    # validity of (k+1)/(B+1) at a data-dependent B: P(phat_tau <= u) for an adversarial stop on the look grid
    vrows = []
    for u in (0.05, 0.01, 0.005, 0.001):
        thr = [int(np.floor(u * (B + 1) - 1)) for B in LOOKS]  # phat <= u  <=> k <= u(B+1) - 1

        def f(p):
            dist = np.zeros(KMAX + 1); dist[0] = 1.0; prev = 0; rej = 0.0
            for B, t in zip(LOOKS, thr):
                dist = np.convolve(dist, increments_pmf(p, B - prev))[: KMAX + 1]; prev = B
                if t >= 0:
                    rej += dist[: t + 1].sum(); dist[: t + 1] = 0.0
            return rej
        val, _ = integrate(f, u)
        vrows.append({"u": u, "P_adv(phat<=u)": val, "ratio": val / u})
        print(json.dumps(vrows[-1]), flush=True)
    out["phat_validity_under_adversarial_stop"] = vrows
    json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "fwer_seq_out.json", "w"), indent=1)


if __name__ == "__main__":
    main()
