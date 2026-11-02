#!/usr/bin/env python3
"""The staged 1B declaration's null and flag rule (state/measurement-paper/5d-community-20261024/
FD-1B-STAGED-DECLARATION.md section 5.2, revision 2): the in-interval content each cell, and the joint chi2 region,
would have if the covariance C_T matched the toys' error exactly, under the declared draw laws, which are partly
two-point and so not Gaussian (the audit's R2 on #664).

The null at a truth T is a declared function of the blocks remade at T, evaluated before any toy error is read:

* every drawn universe band is a ``Discrete`` law: its universes' centred shift vectors with their draw probabilities
  (a pair band's two endpoints at 1/2 each, 2p2h's three at 1/3, the flux universes at w_u / sum w, a detector band's
  two endpoints, a lateral band's +-Delta_b(T)/2). Centring is the block estimator's own: the probability-weighted
  mean is removed, so each law's covariance is that band's block exactly;
* stat, normalization and C_model_abs(T) are one Gaussian with their summed covariance. C_model is in the null's
  error on purpose: the rule asks whether C_T's intervals hold their nominal content given the draws' shape, and a
  Gaussian share has content P0 by definition;
* the components must sum to C_T to 1e-12 relative (``check_matched``), or the null refuses.

The content is estimated from ``N_MC`` simulated error vectors at ``NULL_SEED``; its Monte Carlo standard error is
returned, and each flag count is computed at the content minus ``SE_MARGIN`` standard errors, which can only lower the
count and so the false-flag rate. A cell is flagged when its count k has P(Bin(n, p_c) <= k) < ALPHA_CELLS / 16, the
joint region when P(Bin(n, q) <= k) < ALPHA_JOINT: the exact one-sided Clopper-Pearson duality. Per truth, the size
is at most ALPHA_CELLS + ALPHA_JOINT = 0.05 by the union bound; ``size`` returns the exact sum at the null.

``attribute`` splits a flagged cell's under-coverage into bias and width from the toys' pulls (the audit's M1).

MEASURES: arithmetic on supplied blocks and errors. CANNOT AUTHORIZE: a verdict by itself, or any change to C_T.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
from fd_1b_inv import chi2_ppf  # noqa: E402

P0 = math.erf(1 / math.sqrt(2))
N_CELLS = 16
N_TOYS = 300
ALPHA_CELLS = 0.025                     # Bonferroni over the 16 cells: 0.025 / 16 each
ALPHA_JOINT = 0.025
N_MC = 2_000_000
NULL_SEED = 3_642_000
SE_MARGIN = 3.0
CHUNK = 100_000
MATCH_TOL = 1e-12
RANK_REL = 1e-12                        # S1's rank convention


class Refusal(RuntimeError):
    pass


@dataclass(frozen=True)
class Discrete:
    """A band's draw law: rows of ``values`` (k x n) drawn with ``probs`` (k), centred by the weighted mean."""
    values: np.ndarray
    probs: np.ndarray

    @classmethod
    def centred(cls, values, probs) -> "Discrete":
        v, p = np.atleast_2d(np.asarray(values, float)), np.asarray(probs, float)
        if p.ndim != 1 or p.size != v.shape[0] or np.any(p < 0) or not math.isclose(p.sum(), 1.0, abs_tol=1e-12):
            raise Refusal("a draw law needs one non-negative probability per value row, summing to 1")
        p = p / p.sum()
        return cls(v - p @ v, p)

    @classmethod
    def two_point(cls, delta) -> "Discrete":
        """+-delta/2 at 1/2 each: a pair band, a detector band or a lateral band."""
        d = np.asarray(delta, float)
        return cls.centred(np.stack([d / 2, -d / 2]), [0.5, 0.5])

    def cov(self) -> np.ndarray:
        return (self.values * self.probs[:, None]).T @ self.values


def check_matched(laws: list[Discrete], gauss: np.ndarray, C_T: np.ndarray) -> float:
    """The laws' covariances plus the Gaussian's must be C_T: the null is 'exactly matched' by construction."""
    total = gauss + sum((law.cov() for law in laws), np.zeros_like(C_T))
    rel = float(np.max(np.abs(total - C_T)) / np.max(np.abs(C_T)))
    if rel > MATCH_TOL:
        raise Refusal(f"the null's components miss C_T by {rel:.2e} relative (tolerance {MATCH_TOL:g})")
    return rel


def chi2_nonnull(E: np.ndarray, C: np.ndarray) -> tuple[np.ndarray, int]:
    """chi2 of each row of E on C's non-null subspace (eigenvalues above RANK_REL of the largest), and its ndf."""
    lam, V = np.linalg.eigh(C)
    keep = lam > RANK_REL * lam.max()
    Z = E @ V[:, keep]
    return np.sum(Z * Z / lam[keep], axis=1), int(keep.sum())


def simulate(laws: list[Discrete], gauss: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    """n error vectors: one independent draw from every law, plus the Gaussian."""
    dim = gauss.shape[0]
    E = rng.multivariate_normal(np.zeros(dim), gauss, size=n, method="eigh") if np.any(gauss) else np.zeros((n, dim))
    for law in laws:
        E += law.values[rng.choice(law.probs.size, size=n, p=law.probs)]
    return E


def null_contents(laws: list[Discrete], gauss: np.ndarray, C_T: np.ndarray, n_mc: int = N_MC,
                  seed: int = NULL_SEED) -> dict:
    """Per-cell content P(|e_c| <= sigma_c) and the joint content P(chi2 <= F^-1_{chi2(ndf)}(P0)) under the null."""
    match = check_matched(laws, gauss, C_T)
    sigma = np.sqrt(np.diag(C_T))
    _, ndf = chi2_nonnull(np.zeros((1, C_T.shape[0])), C_T)
    cut = chi2_ppf(P0, ndf)
    rng = np.random.default_rng(seed)
    inside, joint, done = np.zeros(C_T.shape[0]), 0, 0
    while done < n_mc:
        m = min(CHUNK, n_mc - done)
        E = simulate(laws, gauss, m, rng)
        inside += np.sum(np.abs(E) <= sigma, axis=0)
        joint += int(np.sum(chi2_nonnull(E, C_T)[0] <= cut))
        done += m
    p, q = inside / n_mc, joint / n_mc
    return {"p_cell": p, "se_cell": np.sqrt(p * (1 - p) / n_mc), "q_joint": q, "se_joint": math.sqrt(q * (1 - q) / n_mc),
            "ndf": ndf, "chi2_cut": cut, "n_mc": n_mc, "seed": seed, "match_rel": match}


def binom_cdf(k: int, n: int, p: float) -> float:
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    return float(sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1)))


def flag_count(p: float, n: int, alpha: float) -> int:
    """The largest count k with P(Bin(n, p) <= k) < alpha (-1 if none): a count at or below it is flagged."""
    k = -1
    while k + 1 <= n and binom_cdf(k + 1, n, p) < alpha:
        k += 1
    return k


def thresholds(null: dict, n: int = N_TOYS) -> dict:
    """The flag counts, each at the null content minus SE_MARGIN Monte Carlo standard errors."""
    p_use = np.clip(null["p_cell"] - SE_MARGIN * null["se_cell"], 0.0, 1.0)
    q_use = min(max(null["q_joint"] - SE_MARGIN * null["se_joint"], 0.0), 1.0)
    a_cell = ALPHA_CELLS / len(p_use)
    k_cell = [flag_count(float(p), n, a_cell) for p in p_use]
    k_joint = flag_count(q_use, n, ALPHA_JOINT)
    return {"n": n, "alpha_cell": a_cell, "alpha_joint": ALPHA_JOINT, "p_used": p_use.tolist(), "q_used": q_use,
            "k_cell": k_cell, "k_joint": k_joint}


def size(null: dict, thr: dict) -> dict:
    """The false-flag probabilities at the null contents: per cell, the union over cells and the joint, per truth."""
    n = thr["n"]
    cells = [binom_cdf(k, n, float(p)) for k, p in zip(thr["k_cell"], null["p_cell"])]
    joint = binom_cdf(thr["k_joint"], n, float(null["q_joint"]))
    return {"cell": cells, "cells_union_bound": float(sum(cells)), "joint": joint,
            "per_truth_union_bound": float(sum(cells) + joint)}


def across_truths(per_truth: list[float]) -> dict:
    """Any flag at any truth: the union bound, and the value if the truths' flags were independent."""
    return {"union_bound": float(sum(per_truth)), "if_independent": float(1 - np.prod([1 - s for s in per_truth]))}


def attribute(errors: np.ndarray, sigma: float, k_flag: int) -> dict:
    """A flagged cell's bias-versus-width split (the audit's M1): the pull mean and standard deviation with their
    standard errors, and the count of the centred errors |e - mean| <= sigma. 'bias' if the centred count is not
    flagged, 'width' if it is flagged and the pull mean is within 2 standard errors of 0, 'both' otherwise."""
    z = np.asarray(errors, float) / sigma
    n = z.size
    mean, sd = float(z.mean()), float(z.std(ddof=1))
    se_mean, se_sd = sd / math.sqrt(n), sd / math.sqrt(2 * (n - 1))
    centred = int(np.sum(np.abs(z - mean) <= 1.0))
    if centred > k_flag:
        label = "bias"
    elif abs(mean) <= 2 * se_mean:
        label = "width"
    else:
        label = "both"
    return {"pull_mean": mean, "pull_mean_se": se_mean, "pull_sd": sd, "pull_sd_se": se_sd,
            "centred_count": centred, "k_flag": k_flag, "driven_by": label}
