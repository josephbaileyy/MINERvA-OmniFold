"""Inference primitives shared by `decide.py`, `coverage.py` and `sizing.py` (PROTOCOL-20260925).

* **Level of one bound (section 6 preamble, section 8).** A bound is one-sided at
  `alpha_family / m`, Bonferroni over the `m` members of the declared decision set, and, under
  the two-look sequential rule, at half of that per look: `alpha = 0.05 / m / looks_planned`.
* **Replicate-level bounds**: one-sided Student-t bounds on replicate means (paired differences
  are replicate-level values too).
* **Pooled failure rate (B1)**: exact one-sided Clopper-Pearson bounds.
* **Pooled coverage (C1, C3, C5)**: replicate-cluster percentile bootstrap.
* **Cost ratio (section 6.7)**: delta method on log mean costs.
* **Requirements and the sequential rule (section 8).** A requirement is a list of parts, each a
  point or a bound compared with a threshold. At a look a requirement is PASS if every part passes,
  FAIL if some part is decisively failed (the interval lies wholly on the wrong side of its
  threshold) or if this is the last planned look, else CONTINUE (an interval straddles its
  threshold: look 2 adds n2 = n1 replicates). A part with no interval (a pure point rule) is
  decided at the first look.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

import numpy as np
from scipy import stats

ALPHA_FAMILY = 0.05
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_SEED = 20260925


def per_bound_alpha(m: int, looks_planned: int = 1, alpha: float = ALPHA_FAMILY) -> float:
    """One-sided level of one bound: Bonferroni over m, split equally over the planned looks."""
    if m < 1 or looks_planned not in (1, 2):
        raise ValueError(f"m={m}, looks_planned={looks_planned}")
    return alpha / m / looks_planned


@dataclass(frozen=True)
class TBound:
    n: int
    mean: float
    sd: float | None
    lb: float | None
    ub: float | None
    alpha: float

    def as_dict(self) -> dict[str, Any]:
        return {"n": self.n, "mean": self.mean, "sd": self.sd, "lb": self.lb, "ub": self.ub,
                "alpha_one_sided": self.alpha}


def t_bounds(values: Iterable[float], alpha: float) -> TBound:
    """One-sided (1 - alpha) Student-t lower and upper bounds on the mean (each one-sided)."""
    v = np.asarray(list(values), dtype=np.float64)
    if v.size == 0:
        raise ValueError("no values")
    if not np.isfinite(v).all():
        raise ValueError("non-finite replicate value")
    if v.size < 2:
        return TBound(int(v.size), float(v.mean()), None, None, None, alpha)
    sd = float(v.std(ddof=1))
    half = float(stats.t.ppf(1.0 - alpha, v.size - 1)) * sd / math.sqrt(v.size)
    return TBound(int(v.size), float(v.mean()), sd, float(v.mean()) - half,
                  float(v.mean()) + half, alpha)


def clopper_pearson(x: int, n: int, alpha: float) -> tuple[float, float]:
    """One-sided (1 - alpha) exact lower and upper bounds on a binomial probability."""
    if n <= 0 or not 0 <= x <= n:
        raise ValueError(f"x={x}, n={n}")
    lo = 0.0 if x == 0 else float(stats.beta.ppf(alpha, x, n - x + 1))
    hi = 1.0 if x == n else float(stats.beta.ppf(1.0 - alpha, x + 1, n - x))
    return lo, hi


def cluster_bootstrap_bounds(hits: np.ndarray, alpha: float, draws: int = BOOTSTRAP_DRAWS,
                             seed: int = BOOTSTRAP_SEED) -> dict[str, Any]:
    """Pooled rate of a (replicate x cell) 0/1 array with replicate-cluster percentile bounds.

    `hits` has one row per replicate (the cluster) and one column per pooled cell (bin); NaN cells
    are excluded. Rows are resampled with replacement; the pooled rate of each resample is the
    mean over its non-NaN cells. Bounds are the alpha and 1 - alpha percentiles.
    """
    h = np.asarray(hits, dtype=np.float64)
    if h.ndim != 2 or h.shape[0] < 2:
        raise ValueError(f"need >= 2 replicates, got shape {h.shape}")
    ok = np.isfinite(h)
    s = np.where(ok, h, 0.0).sum(axis=1)
    c = ok.sum(axis=1).astype(np.float64)
    point = float(s.sum() / c.sum())
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, h.shape[0], size=(draws, h.shape[0]))
    rates = s[idx].sum(axis=1) / c[idx].sum(axis=1)
    return {"point": point, "lb": float(np.quantile(rates, alpha)),
            "ub": float(np.quantile(rates, 1.0 - alpha)), "alpha_one_sided": alpha,
            "n_replicates": int(h.shape[0]), "n_cells": int(c.sum()), "draws": draws,
            "seed": seed}


def cost_ratio_lb(cost_large: Sequence[float], cost_small: Sequence[float], alpha: float,
                  unfoldings_large: float = 1.0, unfoldings_small: float = 1.0,
                  fixed_large: float = 0.0, fixed_small: float = 0.0) -> dict[str, Any]:
    """Lower bound of total-cost ratio large/small (section 6.7) by the delta method on log costs.

    Total cost = unfoldings x mean per-unfolding GPU-hours + fixed (inference). The variance of
    log(total) is (unfoldings x sd / sqrt(n))^2 / total^2 (delta method); the two packages'
    measurements are independent; the bound uses the normal quantile.
    """
    out = {}
    for tag, c, u, f in (("large", cost_large, unfoldings_large, fixed_large),
                         ("small", cost_small, unfoldings_small, fixed_small)):
        v = np.asarray(c, dtype=np.float64)
        if v.size < 2 or not np.isfinite(v).all() or (v <= 0).any():
            raise ValueError(f"{tag}: need >= 2 positive per-unfolding cost measurements")
        total = u * v.mean() + f
        se_log = u * v.std(ddof=1) / math.sqrt(v.size) / total
        out[tag] = {"n": int(v.size), "mean_per_unfolding": float(v.mean()),
                    "sd_per_unfolding": float(v.std(ddof=1)), "unfoldings": u, "fixed": f,
                    "total": float(total), "se_log_total": float(se_log)}
    diff = math.log(out["large"]["total"]) - math.log(out["small"]["total"])
    se = math.hypot(out["large"]["se_log_total"], out["small"]["se_log_total"])
    z = float(stats.norm.ppf(1.0 - alpha))
    out.update({"ratio": math.exp(diff), "lb": math.exp(diff - z * se), "se_log_ratio": se,
                "alpha_one_sided": alpha, "method": "delta method on log costs, normal"})
    return out


# ------------------------------------------------------------------------------------------- #
# Requirements and the sequential rule
# ------------------------------------------------------------------------------------------- #
PASS, FAIL, CONTINUE, INCOMPLETE = "PASS", "FAIL", "CONTINUE", "INCOMPLETE"


@dataclass
class Part:
    """One comparison. `kind` is 'point' (the estimate is compared) or 'bound' (lb for >=/>,
    ub for <=). `lb`/`ub` (at the look's level) decide whether a failure is decisive."""
    label: str
    op: str                          # '>=', '>', '<='
    threshold: float
    kind: str
    estimate: float | None = None
    lb: float | None = None
    ub: float | None = None

    def value(self) -> float | None:
        if self.kind == "point":
            return self.estimate
        return self.lb if self.op in (">=", ">") else self.ub

    def passes(self) -> bool:
        v = self.value()
        if v is None:
            return False
        return {">=": v >= self.threshold, ">": v > self.threshold,
                "<=": v <= self.threshold}[self.op]

    def decisively_fails(self) -> bool:
        if self.op in (">=", ">"):
            other = self.ub
            if other is None:
                return self.kind == "point" and not self.passes()
            return other < self.threshold if self.op == ">=" else other <= self.threshold
        other = self.lb
        if other is None:
            return self.kind == "point" and not self.passes()
        return other > self.threshold

    def as_dict(self) -> dict[str, Any]:
        return {"label": self.label, "op": self.op, "threshold": self.threshold,
                "kind": self.kind, "estimate": self.estimate, "lb": self.lb, "ub": self.ub,
                "passes": self.passes(), "decisively_fails": self.decisively_fails()}


@dataclass
class Verdict:
    rule: str
    verdict: str
    parts: list[Part] = field(default_factory=list)
    numbers: dict[str, Any] = field(default_factory=dict)
    reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {"rule": self.rule, "verdict": self.verdict,
                "parts": [p.as_dict() for p in self.parts], "numbers": self.numbers,
                "reason": self.reason}


def decide(rule: str, parts: list[Part], look: int, looks_planned: int,
           numbers: dict[str, Any] | None = None) -> Verdict:
    if not 1 <= look <= looks_planned:
        raise ValueError(f"look {look} of {looks_planned}")
    if all(p.passes() for p in parts):
        v = PASS
    elif any(p.decisively_fails() for p in parts) or look == looks_planned:
        v = FAIL
    else:
        v = CONTINUE
    return Verdict(rule, v, parts, numbers or {})


def incomplete(rule: str, reason: str, numbers: dict[str, Any] | None = None) -> Verdict:
    return Verdict(rule, INCOMPLETE, [], numbers or {}, reason)


def ucb80_sd(sd: float, df: int) -> float:
    """80 % upper confidence bound of a normal sd from a sample sd with df degrees of freedom."""
    return sd * math.sqrt(df / stats.chi2.ppf(0.20, df))


def jsonable(obj: Any) -> Any:
    """Nested structure with non-finite floats replaced by None (strict JSON)."""
    if isinstance(obj, dict):
        return {k: jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    if isinstance(obj, (np.floating, float)):
        return float(obj) if math.isfinite(obj) else None
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return jsonable(obj.tolist())
    return obj
