#!/usr/bin/env python3
"""Extra checks: (1) continuous-monitoring adversarial bound (a stop allowed after EVERY draw, B = 1..1999, covering
lost seeds and any look schedule); (2) validity of phat = (k+1)/(B+1) at the frozen rule's stopping B; (3) a direct
Monte Carlo of the whole family: five nulls x (total, shape) sharing each null's stopping time, Holm with
determinacy, global null (m0 = 10), p's independent or equal within a null."""
from __future__ import annotations

import json
import sys

import numpy as np
from scipy import stats

sys.path.insert(0, sys.argv[1])  # the worktree's nd-unfolding, to use the production functions verbatim
import s5p_inference as si  # noqa: E402

ALPHA, M = 0.05, 10
LOOKS = [200 * j for j in range(1, 10)] + [1999]
TH = sorted(set(si.holm_thresholds(ALPHA, M)) | {0.01, 0.05})


def kstar(c, B):
    ks = -1
    for k in range(0, 200):
        if si.cp_interval(k, B, 0.95)[1] < c:
            ks = k
        else:
            break
    return ks


def leg(fun, c, n=60):
    x, w = np.polynomial.legendre.leggauss(n)
    edges = np.concatenate([np.linspace(0, c, 9)[:-1], np.linspace(c, 3 * c, 25)[:-1], np.linspace(3 * c, min(1, 20 * c), 9)])
    tot = 0.0
    for a, b in zip(edges[:-1], edges[1:]):
        xs = 0.5 * (b - a) * x + 0.5 * (b + a)
        tot += 0.5 * (b - a) * np.sum(w * np.array([fun(t) for t in xs]))
    return tot


def continuous_adv():
    res = []
    for m0 in (1, 2, 5, 10):
        c = ALPHA / m0
        ks = np.array([kstar(c, B) for B in range(1, 2000)])
        K = int(ks.max()) + 2

        def f(p):
            d = np.zeros(K + 1); d[0] = 1.0; rej = 0.0
            for B in range(1, 2000):
                d = np.concatenate([[d[0] * (1 - p)], d[1:] * (1 - p) + d[:-1] * p])  # one more draw
                t = ks[B - 1]
                if t >= 0:
                    rej += d[: t + 1].sum(); d[: t + 1] = 0.0
            return rej
        v = leg(f, c, 24)
        res.append({"m0": m0, "c": c, "R_over_c": v / c, "FWER_bound_over_alpha": m0 * v / ALPHA,
                    "sup_cond_at_p_eq_c": f(c)})
        print(json.dumps(res[-1]), flush=True)
    return res


def frozen_phat_validity():
    stop_tab = {B: np.array([si.sequential_decision(k, B, TH)["stop"] for k in range(300)]) for B in LOOKS}
    out = []
    for u in (0.05, 0.01, 0.005, 0.001):
        def f(p):
            d = np.zeros(300); d[0] = 1.0; prev = 0; acc = 0.0
            for j, B in enumerate(LOOKS):
                d = np.convolve(d, stats.binom.pmf(np.arange(300), B - prev, p))[:300]; prev = B
                st = stop_tab[B] if j < len(LOOKS) - 1 else np.ones(300, bool)
                ks = np.arange(300)
                hit = st & ((ks + 1) / (B + 1) <= u)
                acc += d[hit].sum(); d = np.where(st, 0.0, d)
            return acc
        v = leg(f, u, 40)
        out.append({"u": u, "P_frozen(phat_tau<=u)": v, "ratio": v / u})
        print(json.dumps(out[-1]), flush=True)
    return out


def family_mc(nrep=400000, seed=7, corr="independent"):
    rng = np.random.default_rng(seed)
    nn = 5
    rej_any = 0
    # precompute: the frozen controller's stop decision for a null needs both tests' (k,B); tabulate sequential stop per (k,B)
    stop_tab = {B: np.array([si.sequential_decision(k, B, TH)["stop"] for k in range(2001)]) for B in LOOKS}
    hi95 = {B: np.array([si.cp_interval(k, B, 0.95)[1] for k in range(2001)]) for B in LOOKS}
    lo95 = {B: np.array([si.cp_interval(k, B, 0.95)[0] for k in range(2001)]) for B in LOOKS}
    H = np.array([hi95[B] for B in LOOKS])
    batch = 20000
    done = 0
    while done < nrep:
        n = min(batch, nrep - done)
        p = rng.uniform(size=(n, nn, 2))
        if corr == "equal":
            p[:, :, 1] = p[:, :, 0]
        k = np.zeros((n, nn, 2), int)
        stopped = np.zeros((n, nn), bool)
        fk = np.zeros((n, nn, 2), int); fB = np.zeros((n, nn), int)
        prev = 0
        for j, B in enumerate(LOOKS):
            if corr == "equal":
                u = rng.random((n, nn, B - prev))
                inc = (u[..., None] < p[:, :, None, :]).sum(axis=2)
            else:
                inc = rng.binomial(B - prev, p)
            k = k + inc; prev = B
            st = stop_tab[B][np.minimum(k, 2000)].all(axis=2) if j < len(LOOKS) - 1 else np.ones((n, nn), bool)
            new = st & ~stopped
            fk[new] = k[new]; fB[new] = B
            stopped |= st
        # Holm with determinacy over the 10 tests, ordering by phat
        kk = fk.reshape(n, 10); BB = np.repeat(fB, 2, axis=1)
        ph = (kk + 1) / (BB + 1)
        order = np.argsort(ph, axis=1, kind="stable")
        alive = np.ones(n, bool); anyrej = np.zeros(n, bool)
        for i in range(10):
            idx = order[:, i]
            ki = kk[np.arange(n), idx]; Bi = BB[np.arange(n), idx]
            th = ALPHA / (10 - i)
            hi = H[np.searchsorted(np.array(LOOKS), Bi), np.minimum(ki, 2000)]
            r = alive & (hi < th)
            anyrej |= r
            alive &= r
        rej_any += int(anyrej.sum()); done += n
    f = rej_any / nrep
    se = np.sqrt(f * (1 - f) / nrep)
    out = {"corr": corr, "nrep": nrep, "FWER": f, "se": se, "FWER_over_alpha": f / ALPHA}
    print(json.dumps(out), flush=True)
    return out


if __name__ == "__main__":
    res = {"continuous_adv": continuous_adv(), "frozen_phat_validity": frozen_phat_validity(),
           "family_mc_indep": family_mc(400000, 7, "independent")}
    json.dump(res, open("fwer_extra_out.json", "w"), indent=1)
