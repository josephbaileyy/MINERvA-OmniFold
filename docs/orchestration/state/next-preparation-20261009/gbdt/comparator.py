"""Reference reductions for the proposed exact-response comparator (diagnostic D-ID).

Binned, linear-algebra only: no classifier, no training, no resampling. The functions take a
response matrix ``R[reco, truth]`` (expected reco yield per unit truth, efficiency included),
noise-free reco data ``y`` and reporting maps ``H[functional, truth]``. They are exercised here only
on synthetic fixtures (``test_comparator.py``); running them on MINERvA inputs is the proposed
diagnostic and needs its own authorization.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

APPROXIMATION_RATIO = 0.5  # |r_IBU| <= 0.5 |r_GBDT|: the exact-response iteration does far better
FAITHFUL_TOLERANCE = 0.3  # |r_IBU - r_GBDT| <= 0.3 |r_GBDT|: the GBDT behaves like exact IBU
IDENTIFIED_SIGMA = 0.025  # relative CR width at or below half the proposed 5% allowance
WEAK_SIGMA = 0.10  # relative CR width above the proposed 10% total half-width
ELIGIBLE_RESIDUAL = 0.02  # only functionals with |r_GBDT| > 2% enter the branch shares
BRANCH_SHARE = 0.5  # a branch is declared when at least half of the eligible functionals carry it
CONVERGED_RATIO = 0.5  # branch B needs |r_IBU(inf)| <= 0.5 |r_GBDT|
MISSED_QUANTILE = 2.0 / 3.0  # top tercile of missed-event fraction
MISSED_SHARE = 2.0 / 3.0  # bookkeeping implicated if >= 2/3 of the excess sits in that tercile


def ibu(response: np.ndarray, data: np.ndarray, prior: np.ndarray, iterations: int) -> np.ndarray:
    """D'Agostini iterations; returns truth estimates of shape (iterations, n_truth)."""
    efficiency = response.sum(axis=0)
    if np.any(efficiency <= 0):
        raise ValueError("every truth cell needs positive efficiency")
    estimate = prior.astype(float).copy()
    out = np.empty((iterations, estimate.size))
    for k in range(iterations):
        folded = response @ estimate
        ratio = np.divide(data, folded, out=np.zeros_like(data, dtype=float), where=folded > 0)
        estimate = estimate * (response.T @ ratio) / efficiency
        out[k] = estimate
    return out


def chi2_fold(response: np.ndarray, truth_a: np.ndarray, truth_b: np.ndarray) -> float:
    """Noise-free Poisson chi-square of fold(a) against fold(b), variance fold(b)."""
    fa, fb = response @ truth_a, response @ truth_b
    keep = fb > 0
    return float(np.sum((fa[keep] - fb[keep]) ** 2 / fb[keep]))


def fisher(response: np.ndarray, truth: np.ndarray) -> np.ndarray:
    expected = response @ truth
    keep = expected > 0
    weighted = response[keep] / np.sqrt(expected[keep])[:, None]
    return weighted.T @ weighted


@dataclass(frozen=True)
class Width:
    sigma: np.ndarray  # CR standard deviation per functional (inf if a null-space component exists)
    null_fraction: np.ndarray  # share of ||h|| in the numerical null space of F


def cr_width(response: np.ndarray, truth: np.ndarray, maps: np.ndarray,
             rtol: float = 1e-12) -> Width:
    """Cramer-Rao width of h^T t at the analysis exposure, with explicit null-space detection."""
    values, vectors = np.linalg.eigh(fisher(response, truth))
    positive = values > rtol * values.max()
    coeff = maps @ vectors
    null = np.sqrt(np.sum(coeff[:, ~positive] ** 2, axis=1)) / np.linalg.norm(maps, axis=1)
    sigma = np.sqrt(np.sum(coeff[:, positive] ** 2 / values[positive], axis=1))
    sigma = np.where(null > 1e-6, np.inf, sigma)
    return Width(sigma=sigma, null_fraction=null)


def invisible_share(response: np.ndarray, truth: np.ndarray, residual: np.ndarray,
                    maps: np.ndarray, threshold: float = 1.0) -> np.ndarray:
    """Share of each functional's residual h^T d carried by Fisher modes the data cannot see.

    The residual is expanded in the eigenbasis of F; mode i is invisible when its own contribution
    to the noise-free fold chi-square, value_i * component_i**2, is below ``threshold`` (one
    statistical standard deviation at the analysis exposure for threshold 1).
    """
    values, vectors = np.linalg.eigh(fisher(response, truth))
    components = vectors.T @ residual
    weak = values * components**2 < threshold
    total = maps @ residual
    weak_part = maps @ (vectors[:, weak] @ components[weak])
    return np.divide(weak_part, total, out=np.zeros_like(total), where=np.abs(total) > 0)


def classify(r_gbdt: np.ndarray, r_ibu: np.ndarray, sigma_rel: np.ndarray) -> list[dict[str, str]]:
    """Predeclared per-functional labels; see REPORT.md section 6 for the interpretation."""
    labels = []
    for g, i, s in zip(r_gbdt, r_ibu, sigma_rel, strict=True):
        if abs(i) <= APPROXIMATION_RATIO * abs(g):
            iteration = "approximation-dominated"
        elif abs(i - g) <= FAITHFUL_TOLERANCE * abs(g):
            iteration = "iteration-faithful"
        else:
            iteration = "mixed"
        if s <= IDENTIFIED_SIGMA:
            ident = "identified-at-target"
        elif s > WEAK_SIGMA:
            ident = "weakly-identified"
        else:
            ident = "intermediate"
        labels.append({"iteration": iteration, "identifiability": ident})
    return labels


def branch_outcome(labels: list[dict[str, str]], r_gbdt: np.ndarray, r_ibu_inf: np.ndarray,
                   sensitive: np.ndarray) -> dict[str, object]:
    """Predeclared aggregation over one map: branch C, A, B or mixed (REPORT.md section 6).

    C: weakly identified. A: approximation-dominated and identified. B: iteration-faithful,
    identified, and removed by running the exact iteration to convergence. Functionals flagged
    resolution-sensitive, or with |r_GBDT| <= 2%, count toward no branch.
    """
    eligible = (np.abs(r_gbdt) > ELIGIBLE_RESIDUAL) & ~sensitive
    n = int(eligible.sum())
    counts = {"C": 0, "A": 0, "B": 0}
    for i in np.flatnonzero(eligible):
        lab = labels[i]
        if lab["identifiability"] == "weakly-identified":
            counts["C"] += 1
        elif lab["identifiability"] == "identified-at-target":
            if lab["iteration"] == "approximation-dominated":
                counts["A"] += 1
            elif (lab["iteration"] == "iteration-faithful"
                  and abs(r_ibu_inf[i]) <= CONVERGED_RATIO * abs(r_gbdt[i])):
                counts["B"] += 1
    shares = {k: (v / n if n else 0.0) for k, v in counts.items()}
    branch = next((k for k in ("C", "A", "B") if n and shares[k] >= BRANCH_SHARE), "mixed")
    return {"n_eligible": n, "shares": shares, "branch": branch if n else "no-eligible-functional"}


def missed_concentration(excess: np.ndarray, missed_fraction: np.ndarray) -> dict[str, object]:
    """Share of the summed |r_GBDT - r_IBU| carried by functionals in the top missed-event tercile.

    Expected about 1/3 if the excess is unrelated to missed events; bookkeeping (missed-event
    extrapolation) is implicated when the share is at least 2/3.
    """
    cut = np.quantile(missed_fraction, MISSED_QUANTILE)
    top = missed_fraction >= cut
    total = float(np.sum(np.abs(excess)))
    share = float(np.sum(np.abs(excess[top])) / total) if total > 0 else 0.0
    return {"share_top_tercile": share, "bookkeeping_implicated": share >= MISSED_SHARE}
