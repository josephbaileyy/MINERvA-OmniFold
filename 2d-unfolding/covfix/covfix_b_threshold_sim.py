"""COVFIX rev 12 §4.5: the simulated pass probability of §4.4's (b) SUPPORT rule.

  python3 -B covfix_b_threshold_sim.py --cov <covariance-reported.csv> --cells all|none|R00,R03,... --truths 3|2
                                       [--replicas 20000] [--seed 20261124]

The model is §6.2's zero-bias Gaussian law under uniform scale inflation:
- each toy's centred estimate is x ~ N(0, s²·K_m), where K_m is the frozen measured set's submatrix of the reported
  covariance, symmetrized as (K + Kᵀ)/2;
- s is chosen so that the true joint coverage of the reported 68.27 % ellipsoid is c: F_{χ²_k}(q/s²) = c, with
  q = F⁻¹_{χ²_k}(0.6827).

The readings, per truth over 300 toys:
- the joint count, #{xᵀK_m⁻¹x ≤ q};
- each cell's 1σ count, #{|x_i| ≤ √K_ii}.

SUPPORT holds when, at every one of T independent truths, the joint count is ≥ 185 and no cell is vetoed. A cell is
vetoed when its count is ≤ the largest c with P(X ≤ c) ≤ 0.05/(k·T), for X ~ Bin(300, 0.6827).

Printed for c = 68.27 %, 64 %, 62 % and 60 %: the pass rate with its binomial SE over the replicas. Also printed:
- the veto count;
- the exact deficit bound: the largest d with P(X ≤ d | 0.60) ≤ 0.05/((k+1)·T);
- the exact one-sided 95 % lower bound at 185.

With --cells none (k = 0 measured cells), it records "no measured-set test" and simulates nothing (§4.4).

Everything is in correlation units, because both readings are invariant under a per-cell rescaling.

MEASURES: pass probabilities of a declared rule under a declared model. DECIDES: nothing by itself. Under §4.5, a nominal
pass rate below 0.90 in either branch sends the threshold back to Joseph.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys

import numpy as np
from scipy.stats import beta, binom, chi2

N_TOYS, P_NOM, JOINT_MIN = 300, 0.6827, 185
COVERAGES = (0.6827, 0.64, 0.62, 0.60)


def load_cov(path: str) -> tuple[list[str], np.ndarray]:
    with open(path, newline="") as fh:
        rows = list(csv.reader(fh))
    names = rows[0][1:]
    if [r[0] for r in rows[1:]] != names:
        raise SystemExit("the covariance's row labels do not match its column labels")
    k = np.array([[float(v) for v in r[1:]] for r in rows[1:]])
    return names, (k + k.T) / 2


def correlation(k: np.ndarray) -> np.ndarray:
    d = np.sqrt(np.diag(k))
    if not np.all(d > 0):
        raise SystemExit("a diagonal entry is not positive")
    return k / np.outer(d, d)


def veto_count(k: int, t: int) -> int:
    """The largest c with P(X <= c) <= 0.05/(k*T); a cell at or below it is vetoed (-1: none)."""
    a = 0.05 / (k * t)
    cs = [c for c in range(N_TOYS + 1) if binom.cdf(c, N_TOYS, P_NOM) <= a]
    return max(cs) if cs else -1


def deficit_bound(k: int, t: int) -> int:
    a = 0.05 / ((k + 1) * t)
    return max(d for d in range(N_TOYS + 1) if binom.cdf(d, N_TOYS, 0.60) <= a)


def scale_for(c: float, k: int) -> float:
    """s with F_{chi2_k}(q / s^2) = c."""
    q = chi2.ppf(P_NOM, k)
    return float(np.sqrt(q / chi2.ppf(c, k)))


def pass_rate(r: np.ndarray, t: int, c: float, replicas: int, rng: np.random.Generator,
              chunk: int = 500) -> tuple[float, float]:
    k = r.shape[0]
    q, veto, s = chi2.ppf(P_NOM, k), veto_count(k, t), scale_for(c, k)
    lchol = np.linalg.cholesky(r)
    rinv = np.linalg.inv(r)
    passed = done = 0
    while done < replicas:
        n = min(chunk, replicas - done)
        z = rng.standard_normal((n, t, N_TOYS, k)) @ lchol.T * s
        joint = np.einsum("...i,ij,...j->...", z, rinv, z) <= q
        jc = joint.sum(axis=2)                                  # (n, t)
        cc = (np.abs(z) <= 1.0).sum(axis=2)                     # (n, t, k)
        ok = (jc >= JOINT_MIN).all(axis=1) & (cc > veto).all(axis=(1, 2))
        passed += int(ok.sum())
        done += n
    p = passed / replicas
    return p, float(np.sqrt(p * (1 - p) / replicas))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cov", required=True)
    ap.add_argument("--cells", required=True,
                    help="'all', 'none' (k = 0) or comma-separated labels (the frozen measured set)")
    ap.add_argument("--truths", type=int, choices=(2, 3), required=True)
    ap.add_argument("--replicas", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20261124)
    a = ap.parse_args(argv)
    names, kfull = load_cov(a.cov)
    if a.cells == "none":
        print(json.dumps({"cells": [], "k": 0, "truths": a.truths, "result": "no measured-set test"}, indent=1))
        return 0
    sel = names if a.cells == "all" else a.cells.split(",")
    if not sel or len(set(sel)) != len(sel) or set(sel) - set(names):
        raise SystemExit("the cell list is empty, repeated or names an unknown cell")
    idx = [names.index(c) for c in sel]
    r = correlation(kfull[np.ix_(idx, idx)])
    k = len(sel)
    rng = np.random.default_rng(a.seed)
    out = {"cells": sel, "k": k, "truths": a.truths, "replicas": a.replicas, "seed": a.seed,
           "cond_correlation": float(np.linalg.cond(r)), "joint_min": JOINT_MIN,
           "veto_count": veto_count(k, a.truths), "every_cell_needs": veto_count(k, a.truths) + 1,
           "deficit_bound": deficit_bound(k, a.truths),
           "lower_bound_at_185": float(beta.ppf(0.05, JOINT_MIN, N_TOYS - JOINT_MIN + 1)), "pass_rate": {}}
    for c in COVERAGES:
        p, se = pass_rate(r, a.truths, c, a.replicas, rng)
        out["pass_rate"][f"{c:.4f}"] = {"p": p, "se": se, "scale": scale_for(c, k)}
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
