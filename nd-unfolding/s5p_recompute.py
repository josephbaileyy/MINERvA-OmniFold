"""s5p Stage 6: an independent re-computation of the joint-inference p-values and decisions.

Written from the frozen specification only: contract amendments 1 (T6/T7, the family), 5 (the statistics and
the surrogates), 6/6b/8 (shift variants, determinacy, keyed draws, partial-product exclusion), 7 (the frozen
admission: claims, calibration, validation_and_assurance, power), the design ``state/s5p/prod/design.json`` and
the implementation conventions listed in ``docs/orchestration/HANDOFF-20260928-s5p-parallel-tasks.md`` section 1.
It imports nothing from, and copies no logic of, ``s5p_joint``, ``s5p_inference`` or ``s5p_seqstop`` (a test
enforces the import rule); their docstrings were read as specification text. Every point where the specification
admits more than one reading is listed in ``AMBIGUITIES`` with the reading used here; a documented alternative is
computed beside the primary one where it could change a decision, never substituted for it.

Pipeline, per experiment product ``x`` (``xsec_flat``, a fine-grid density):

* J-cell integrals ``f = sum_{fine in c} x vol`` over the 109 supported cells of partition J (s5c contract);
* simulated experiments only (calibration and power): ``f <- f + sum_b z_b Delta_b`` (lateral surrogate,
  ``Delta_b = (f(endpoint 1) - f(endpoint 0)) / 2`` of the real-data endpoint unfolds), then
  ``f <- f (1 + 0.014 z)``, then ``f <- f + s_num * N(0, 1)`` drawn from ``default_rng([pseudo_seed, 0x4A01])``,
  ``s_num`` the per-cell SD (ddof 1) of the 20 real-data jitter unfolds; the prediction's finite-MC error
  ``eps = sqrt(Var mu) * N(0, 1)`` from ``default_rng([surrogate_seed0, pseudo_seed, 0x4A02])`` perturbs the
  prediction (``mu + eps``) the experiment is compared with;
* ``T_total = r' W^-1 r``, ``r = f - mu`` on the test domain, ``W = V + diag Var(mu)``;
* ``T_shape``: ``p = f / sum f``, ``q = mu / sum mu``, ``W_s = J W J'`` with ``J = (I - p 1') / sum f``, the last
  domain cell dropped, ``T = (p - q)' W_s^-1 (p - q)``.

Calibration: ``k = #{T_null >= T_obs}``, ``p = (k + 1) / (B + 1)``, exact two-sided Clopper-Pearson interval of
``k / B``. Variants of the calibration ensemble ``f -> f + v`` (process shift ``c S``, ``c`` in (0, 1/2, 1), ``S``
bias-aligned at the upper bound; sub-fine residual ``+-kappa delta_M1``); the claim p is the largest over the
variants. Holm over the ten tests with the determinacy rule; the kappa = 3 robustness flag; power per set at 0.05
and 0.005 (rank, claim-rank and determined); the batch-sequential stopping rule re-evaluated at every look.

MEASURES: an independent recomputation of the frozen statistics, p-values, decisions, stopping and power from the
production products, and its agreement with production's own output. CANNOT AUTHORIZE: any rejection, adoption or
grade; agreement verifies the calculation, not the scientific adequacy of the calibration.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Single-threaded BLAS before numpy loads: the 109-cell solves are ~250x slower under login-node thread
# contention (measured 72 s vs 0.3 s for one null at B = 40), and one thread keeps the rounding reproducible.
for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np  # noqa: E402
from scipy import linalg  # noqa: E402
from scipy.special import betaincinv  # noqa: E402

SCHEMA = "s5p-recompute/1"
AXES = ("pt", "pz", "eavail", "q3", "W")
NORM_SD = 0.014
TAG_SURROGATE = 0x4A01
TAG_PREDICTION = 0x4A02
CP_LEVEL = 0.95
LOOK_LEVEL = 0.995
POWER_LEVELS = (0.05, 0.005)
TESTS = ("total", "shape")

AMBIGUITIES = {
    "A1_surrogate_order": "the three additive/multiplicative surrogate terms are applied in the listed order: "
                          "lateral, then normalization (which therefore scales the lateral term), then rounding "
                          "noise (not scaled)",
    "A2_draw_population": "the rounding noise and eps are drawn over all 109 J cells in V's name order and then "
                          "restricted to the test domain (matters only for GiBUU's 72-cell domain)",
    "A3_draw_call": "a Gaussian vector is drawn as rng.standard_normal(109) and scaled per cell (identical to "
                    "rng.normal(0, sd) in numpy; not a multivariate_normal call)",
    "A4_eps_in_shape": "eps perturbs the prediction: the shape test compares p(f) with p(mu + eps), the Jacobian "
                       "is taken at the experiment's own f (s5p_inference docstring); the alternative "
                       "p(f - eps) vs p(mu) differs at second order",
    "A5_bias_operand": "the bias b of the bias-aligned shift is the mean of the surrogated calibration f (without "
                       "eps) minus mu on the test domain, recomputed from the ensemble present at each look; "
                       "u = b / sqrt(b' W^-1 b), a_j = d_j' W^-1 u over the 16 F4 pairs, se = SD(ddof 1)/sqrt(n); "
                       "the same S (from the total metric) shifts both tests",
    "A6_variant_set": "amendment 7 names the process-shift variants c in (0, 1/2, 1) AND the M1 variants F +- "
                      "kappa delta_M1; read as a UNION (3 + 2 variants, c = 0 carrying no M1 term); the cross "
                      "product (9 variants) is computed beside it and any decision it would change is reported. "
                      "2026-09-29: assessed as resolved by the frozen text to the union "
                      "(ASSESSMENT-20260929-s5p-recompute-A6-A8.md); no owner ruling",
    "A7_robust_flag": "RULED 2026-09-29 (RULING-20260929-s5p-A7-robustness-flag.md): the full Holm re-run at "
                      "kappa = 3; a primary rejection is 'robust to the sub-fine residual' iff also rejected there, "
                      "else 'not robust'; every non-rejected test 'not applicable'. Diagnostic kept: A7(b) per test",
    "A7_VS_kappa3_variant_set": "RULED 2026-09-29 (~04:33Z; RULING-20260929-s5p-A7-VS-kappa3-variant-set.md), a "
                                "report-only clarification made then: REPLACE (process-shift variants UNION F +- 3 "
                                "delta_M1; family.robust_labels, family.holm_at_kappa_robust). Diagnostics kept: keep "
                                "both +-2 and +-3 (family.keep_both_kappa3_diagnostic) and the frozen boolean "
                                "(family.frozen_boolean_equivalent_diagnostic)",
    "A8_look_precision": "the sequential rule's T7 half-width is measured on the 99.5% look interval (the same "
                         "interval as the threshold condition); 'contains' is closed at both ends. Sensitivity "
                         "readings (labelled, never used for a verdict): precision on the 95% interval, open "
                         "containment, and both (A8_READINGS; sequential.a8_sensitivity). 2026-09-29: the level is assessed "
                         "as resolved by the frozen text to the 99.5% look interval; closure is not fixed by text and "
                         "changes no stop at any B = 1..1999; no owner ruling",
    "A9_not_calibrated": "a null with B = 0 has p = 1, k = 0 and the interval [0, 1]; at its Holm step it stops "
                         "'undetermined' and is labelled 'not calibrated'",
    "A10_holm_ties": "equal claim p-values are ordered by the family order (design null order, total before "
                     "shape)",
    "A11_power_shift": "power experiments are observations: unshifted, their own surrogates and eps (keyed by the "
                       "power set's surrogate_seed0); the variants shift the null ensemble only",
    "A12_implied_size": "the implied size of a variant v is the fraction of calibration draws shifted by v whose "
                        "rank p against the full unshifted ensemble is <= 0.05",
    "A13_calibration_set": "the calibration ensemble is every finished product (no '.partial-') of the null's glob "
                           "whose seed lies in [seed0, seed0 + final B); a count different from the final status's "
                           "B, a seed outside the range and a missing seed are reported, not repaired",
    "A14_power_null_B": "power is evaluated against the null's final calibration ensemble (the admission's B >= "
                        "1200 floor for the two powered nulls makes the 0.005 level attainable)",
}


# ----------------------------------------------------------------------------------------------- statistics

def cp_interval(k: int, n: int, level: float = CP_LEVEL) -> tuple[float, float]:
    """Exact two-sided Clopper-Pearson interval of a binomial proportion k / n (``[0, 1]`` when n = 0)."""
    if n <= 0:
        return 0.0, 1.0
    tail = (1.0 - level) / 2.0
    lo = 0.0 if k <= 0 else float(betaincinv(k, n - k + 1, tail))
    hi = 1.0 if k >= n else float(betaincinv(k + 1, n - k, 1.0 - tail))
    return lo, hi


def rank_counts(t_obs: np.ndarray, t_null: np.ndarray) -> np.ndarray:
    """``#{t_null >= t}`` for every observed t."""
    srt = np.sort(np.asarray(t_null, dtype=float))
    return srt.size - np.searchsorted(srt, np.atleast_1d(np.asarray(t_obs, dtype=float)), side="left")


def mc_p(k: int, n: int) -> float:
    return (k + 1.0) / (n + 1.0)


def t_total(r: np.ndarray, w_chol) -> np.ndarray:
    """Quadratic form r' W^-1 r for one residual (1-D) or a stack of residuals (rows)."""
    r2 = np.atleast_2d(r)
    sol = linalg.cho_solve(w_chol, r2.T)
    out = np.einsum("ij,ji->i", r2, sol)
    return out if np.ndim(r) == 2 else out[0]


def t_shape(f: np.ndarray, mu: np.ndarray, w: np.ndarray) -> float:
    """Shape-only statistic: normalized residual with the Jacobian at f, last cell dropped."""
    sf = f.sum()
    p = f / sf
    q = mu / mu.sum()
    jac = (np.eye(f.size) - np.outer(p, np.ones(f.size))) / sf
    ws = jac @ w @ jac.T
    d = (p - q)[:-1]
    return float(d @ np.linalg.solve(ws[:-1, :-1], d))


# ----------------------------------------------------------------------------------------------- decisions

def holm_determined(entries: list[dict], alpha: float, level: float = CP_LEVEL) -> list[dict]:
    """Holm step-down on claim p-values with the admission's determinacy rule.

    ``entries``: dicts with ``test``, ``p``, ``k``, ``B`` in family order. Step i (increasing p) compares with
    alpha / (m - i): the 95% interval of k / B entirely below -> rejected; entirely above -> this and every later
    test 'not rejected'; containing it -> this and every later test 'undetermined'.
    """
    m = len(entries)
    order = sorted(range(m), key=lambda i: (entries[i]["p"], i))
    out = [None] * m
    stopped = None
    for step, i in enumerate(order):
        e = entries[i]
        thr = alpha / (m - step)
        lo, hi = cp_interval(e["k"], e["B"], level)
        rec = {"test": e["test"], "step": step, "threshold": thr, "p": e["p"], "k": e["k"], "B": e["B"],
               "interval": [lo, hi], "level": level}
        if stopped is None:
            if hi < thr:
                rec["decision"] = "rejected"
            elif lo > thr:
                stopped = "not rejected"
            else:
                stopped = "undetermined"
        if stopped is not None:
            rec["decision"] = stopped
        out[i] = rec
    return out


ROBUST = "robust to the sub-fine residual"
NOT_ROBUST = "not robust"
NOT_APPLICABLE = "not applicable"


def robust_labels(primary: list[dict], robust: list[dict]) -> dict:
    """The reported kappa = 3 label under the owner's A7 ruling (R7(a), report only): a primary rejection is robust
    iff the full Holm re-run at kappa = 3 also rejects it; every non-rejected test is 'not applicable'."""
    out = {}
    for d, r in zip(primary, robust):
        if d["test"] != r["test"]:
            raise ValueError("primary and robust Holm records are not aligned")
        if d["decision"] != "rejected":
            out[d["test"]] = NOT_APPLICABLE
        else:
            out[d["test"]] = ROBUST if r["decision"] == "rejected" else NOT_ROBUST
    return out


def holm_point(entries: list[dict], alpha: float) -> list[str]:
    """Plain Holm on the point p-values (reference only)."""
    m = len(entries)
    order = sorted(range(m), key=lambda i: (entries[i]["p"], i))
    out = ["not rejected"] * m
    for step, i in enumerate(order):
        if entries[i]["p"] <= alpha / (m - step):
            out[i] = "rejected"
        else:
            break
    return out


def decision_thresholds(alpha: float, m: int) -> list[float]:
    return sorted({alpha / j for j in range(1, m + 1)} | {0.01, 0.05})


# A8 (handoff section 3): the frozen text fixes condition (a) on the 99.5% look interval but not the interval on which
# (b)'s T7 half-width is measured, nor whether "contains" is closed. The PRIMARY reading is the first entry and is
# the only one that feeds any verdict; the others are labelled sensitivity readings, reported beside it.
A8_READINGS = {
    "primary": {"precision_level": LOOK_LEVEL, "boundary": "closed"},
    "A8_alt_precision_95": {"precision_level": CP_LEVEL, "boundary": "closed"},
    "A8_alt_open_boundaries": {"precision_level": LOOK_LEVEL, "boundary": "open"},
    "A8_alt_precision_95_open": {"precision_level": CP_LEVEL, "boundary": "open"},
}


def stop_condition(look: tuple[float, float], prec: tuple[float, float], p: float, thresholds: list[float],
                   boundary: str = "closed") -> dict:
    """Conditions (a) and (b) of the stopping rule from given interval endpoints (a pure function).

    (a) no threshold inside the look interval (``closed``: lo <= t <= hi; ``open``: lo < t < hi);
    (b) the T7 precision at the point estimate p, measured on the precision interval ``prec``: half-width <= 0.05
    for p >= 0.05, <= 0.5 p for 0.01 <= p < 0.05, and below 0.01 an upper end strictly below the smallest
    threshold.
    """
    lo, hi = look
    if boundary == "closed":
        straddled = [t for t in thresholds if lo <= t <= hi]
    elif boundary == "open":
        straddled = [t for t in thresholds if lo < t < hi]
    else:
        raise ValueError(boundary)
    plo, phi = prec
    half = (phi - plo) / 2.0
    if p >= 0.05:
        precise = half <= 0.05
    elif p >= 0.01:
        precise = half <= 0.5 * p
    else:
        precise = phi < min(thresholds)
    return {"stop": (not straddled) and bool(precise), "straddled": straddled, "t7_precise": bool(precise),
            "precision_half_width": half}


def sequential_stop(k: int, n: int, thresholds: list[float], look_level: float = LOOK_LEVEL,
                    precision_level: float | None = None, boundary: str = "closed") -> dict:
    """The frozen per-test stopping condition at one look (amendment 7 calibration.sequential_rule).

    Defaults are the primary reading (precision measured on the look interval, closed containment); the A8
    sensitivity readings pass ``precision_level`` / ``boundary`` explicitly.
    """
    if n <= 0:
        return {"stop": False, "why": "no products"}
    look = cp_interval(k, n, look_level)
    prec = look if precision_level is None or precision_level == look_level else cp_interval(k, n, precision_level)
    p = mc_p(k, n)
    c = stop_condition(look, prec, p, thresholds, boundary)
    out = {"stop": c["stop"], "p": p, "k": int(k), "B": int(n), "look_interval": list(look),
           "straddled": c["straddled"], "t7_precise": c["t7_precise"]}
    if prec is not look:
        out["precision_interval"] = list(prec)
    return out


def stop_readings(k: int, n: int, thresholds: list[float]) -> dict:
    """The stopping condition of one test under every A8 reading (``primary`` first)."""
    return {name: sequential_stop(k, n, thresholds, LOOK_LEVEL, r["precision_level"], r["boundary"])
            for name, r in A8_READINGS.items()}


def stop_verdict(reason, first_stop, B_final) -> str:
    """Whether a controller's final stop agrees with where a reading of the rule first stops.

    'rule met for both tests': the reading must first stop exactly at the final B. 'maximum reached' / 'batches
    exhausted': the reading must not stop before the final B. 'budget': the reading must not stop before the
    budget stop. Without a final status: 'not terminal'.
    """
    if B_final is None or reason is None:
        return "not terminal"
    if reason == "rule met for both tests":
        return "consistent" if first_stop == B_final else "INCONSISTENT"
    if reason in ("maximum reached", "batches exhausted", "budget"):
        return "consistent" if first_stop is None or first_stop >= B_final else "INCONSISTENT"
    return f"unknown reason {reason!r}"


def a8_sensitivity_map(thresholds: list[float], looks=range(200, 2000, 200), final=1999) -> dict:
    """For every look size B and every k, where the A8 readings' stop decisions differ from the primary's."""
    out = {}
    for B in list(looks) + [final]:
        rows = {}
        for k in range(B + 1):
            r = stop_readings(k, B, thresholds)
            prim = r["primary"]["stop"]
            for name in A8_READINGS:
                if name != "primary" and r[name]["stop"] != prim:
                    rows.setdefault(name, []).append({"k": k, "p": mc_p(k, B), "primary_stop": prim,
                                                       "alt_stop": r[name]["stop"]})
        out[str(B)] = {name: {"n_k_differing": len(v), "p_min": min(x["p"] for x in v),
                              "p_max": max(x["p"] for x in v),
                              "alt_stops_where_primary_continues": sum(1 for x in v if x["alt_stop"]),
                              "primary_stops_where_alt_continues": sum(1 for x in v if not x["alt_stop"]),
                              "k_differing": [x["k"] for x in v]}
                       for name, v in rows.items()}
    return out


# ----------------------------------------------------------------------------------------------- geometry

@dataclass
class Geometry:
    cell: np.ndarray            # fine index -> position among the supported J cells, -1 elsewhere
    vol: np.ndarray             # fine bin volumes
    names: list[str]            # 'J<id>' in increasing id
    pz_index: np.ndarray        # coarse pz index of each supported cell
    n: int = field(init=False)

    def __post_init__(self):
        self.n = len(self.names)

    def integrate(self, x: np.ndarray) -> np.ndarray:
        ok = self.cell >= 0
        return np.bincount(self.cell[ok], weights=(x * self.vol)[ok], minlength=self.n)

    def integrate_var(self, sumw2: np.ndarray) -> np.ndarray:
        ok = self.cell >= 0
        return np.bincount(self.cell[ok], weights=(sumw2 * self.vol ** 2)[ok], minlength=self.n)

    def domain(self, name) -> np.ndarray:
        if name is None:
            return np.arange(self.n)
        if name == "pz_lt_6":
            return np.flatnonzero(self.pz_index <= 1)
        raise SystemExit(f"unknown test domain {name!r}")


def build_geometry(fine_edges: dict, j_edges: dict, supported: list[int]) -> Geometry:
    per_axis, widths = [], []
    for ax in AXES:
        fe, je = np.asarray(fine_edges[ax], float), np.asarray(j_edges[ax], float)
        if not all(np.any(np.isclose(fe, e, rtol=0, atol=1e-9)) for e in je):
            raise SystemExit(f"J edge of {ax} is not a fine edge")
        centre = 0.5 * (fe[1:] + fe[:-1])
        idx = np.searchsorted(je, centre, side="right") - 1
        if idx.min() < 0 or idx.max() > je.size - 2:
            raise SystemExit(f"fine cells of {ax} fall outside the J edges")
        per_axis.append(idx)
        widths.append(np.diff(fe))
    ncoarse = [len(j_edges[ax]) - 1 for ax in AXES]
    grids = np.meshgrid(*per_axis, indexing="ij")
    coarse = np.ravel_multi_index([g.ravel() for g in grids], ncoarse)
    vol = np.ones(1)
    for w in widths:
        vol = np.multiply.outer(vol, w)
    vol = vol.ravel()
    sup = sorted(int(c) for c in supported)
    pos = -np.ones(int(np.prod(ncoarse)), dtype=np.int64)
    pos[sup] = np.arange(len(sup))
    pz = np.array([np.unravel_index(c, ncoarse)[1] for c in sup])
    return Geometry(cell=pos[coarse], vol=vol, names=[f"J{c}" for c in sup], pz_index=pz)


# ----------------------------------------------------------------------------------------------- inputs

def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def finished_products(pattern: str) -> list[str]:
    return sorted(p for p in glob.glob(pattern) if ".partial-" not in os.path.basename(p))


SEED_RE = re.compile(r"_s(\d+)\.npz$")


def seed_of(path: str) -> int:
    m = SEED_RE.search(path)
    if not m:
        raise SystemExit(f"no seed in product name {path}")
    return int(m.group(1))


@dataclass
class Product:
    seed: int
    f: np.ndarray               # raw J integrals
    lateral_z: dict
    normalization_z: float
    path: str


def load_product(path: str, geom: Geometry, bands: list[str]) -> Product:
    with np.load(path, allow_pickle=False) as z:
        x = np.asarray(z["xsec_flat"], float)
        meta = json.loads(str(z["meta"]))
    seed = seed_of(path)
    if int(meta["pseudo_seed"]) != seed:
        raise SystemExit(f"{path}: meta pseudo_seed {meta['pseudo_seed']} != file seed {seed}")
    nd = meta["nuisance_draw"]
    lz = nd["lateral_z"]
    if sorted(lz) != sorted(bands):
        raise SystemExit(f"{path}: lateral bands {sorted(lz)} != design {sorted(bands)}")
    if x.size != geom.cell.size:
        raise SystemExit(f"{path}: xsec_flat has {x.size} cells, the grid {geom.cell.size}")
    if not np.all(np.isfinite(x)):
        raise SystemExit(f"{path}: non-finite xsec_flat")
    return Product(seed=seed, f=geom.integrate(x), lateral_z={b: float(lz[b]) for b in bands},
                   normalization_z=float(nd["normalization_z"]), path=path)


@dataclass
class Surrogates:
    bands: list[str]
    delta: np.ndarray           # (n_bands, 109)
    s_num: np.ndarray           # (109,)

    def apply(self, p: Product) -> np.ndarray:
        z = np.array([p.lateral_z[b] for b in self.bands])
        f = p.f + z @ self.delta
        f = f * (1.0 + NORM_SD * p.normalization_z)
        noise = np.random.default_rng([p.seed, TAG_SURROGATE]).standard_normal(f.size)
        return f + self.s_num * noise


def prediction_error(seed0: int, pseudo_seed: int, var_mu: np.ndarray) -> np.ndarray:
    return np.sqrt(var_mu) * np.random.default_rng([seed0, pseudo_seed, TAG_PREDICTION]).standard_normal(var_mu.size)


def load_x(path: str) -> np.ndarray:
    with np.load(path, allow_pickle=False) as z:
        return np.asarray(z["xsec_flat"], float)


def load_shift_file(spec: dict, names: list[str], label: str) -> dict:
    if "none" in spec:
        return {"none": spec["none"]}
    got = sha256(spec["path"])
    if got != spec["sha256"]:
        raise SystemExit(f"{label}: sha256 {got} != declared {spec['sha256']}")
    with np.load(spec["path"], allow_pickle=False) as z:
        if [str(s) for s in z["names"]] != names:
            raise SystemExit(f"{label}: cell names differ from V's")
        return {"D_J": np.asarray(z["D_J"], float), "d_pairs": np.asarray(z["d_pairs"], float),
                "sha256": got, "path": spec["path"]}


# ----------------------------------------------------------------------------------------------- one null

@dataclass
class TestSetup:
    dom: np.ndarray
    mu: np.ndarray
    var_mu: np.ndarray          # full 109
    w: np.ndarray
    w_chol: tuple


def test_setup(v: np.ndarray, mu_full: np.ndarray, var_full: np.ndarray, dom: np.ndarray) -> TestSetup:
    w = v[np.ix_(dom, dom)] + np.diag(var_full[dom])
    return TestSetup(dom=dom, mu=mu_full[dom], var_mu=var_full, w=w, w_chol=linalg.cho_factor(w, lower=True))


def stats_of(f_dom: np.ndarray, mu_dom: np.ndarray, ts: TestSetup) -> dict:
    """Both statistics of one experiment on the domain (f_dom and mu_dom already restricted)."""
    return {"total": float(t_total(f_dom - mu_dom, ts.w_chol)), "shape": t_shape(f_dom, mu_dom, ts.w)}


def bias_aligned_shift(f_cal_dom: np.ndarray, ts: TestSetup, d_pairs_dom: np.ndarray) -> dict:
    b = f_cal_dom.mean(axis=0) - ts.mu
    norm = math.sqrt(float(t_total(b, ts.w_chol)))
    u = b / norm
    winv_u = linalg.cho_solve(ts.w_chol, u)
    a_j = d_pairs_dom @ winv_u
    a = float(a_j.mean())
    se = float(a_j.std(ddof=1) / math.sqrt(a_j.size)) if a_j.size > 1 else float("nan")
    m = max(a + 2.0 * se, 0.0)
    return {"S": m * u, "magnitude": m, "a": a, "se": se, "a_over_se": a / se if se > 0 else float("nan"),
            "bias_norm_W": norm, "n_pairs": int(a_j.size)}


def variant_shifts(S: np.ndarray, delta_m1, coefs, kappa, mode: str) -> dict:
    out = {}
    if mode == "union":
        for c in coefs:
            out[f"c={c:g}"] = c * S
        if delta_m1 is not None:
            out[f"m1=+{kappa:g}"] = kappa * delta_m1
            out[f"m1=-{kappa:g}"] = -kappa * delta_m1
    elif mode == "product":
        signs = (-1, 0, 1) if delta_m1 is not None else (0,)
        for c in coefs:
            for s in signs:
                v = c * S + (s * kappa * delta_m1 if s else 0.0)
                out[f"c={c:g},m1={s * kappa:+g}" if s else f"c={c:g},m1=0"] = v
    else:
        raise SystemExit(f"unknown variant mode {mode}")
    return out


def null_ensembles(f_cal: np.ndarray, eps_cal: np.ndarray, ts: TestSetup, shifts: dict) -> dict:
    """Null statistics per variant: T(f_b + v) against mu + eps_b."""
    dom = ts.dom
    out = {}
    for label, v in shifts.items():
        tt = np.empty(f_cal.shape[0])
        tsh = np.empty(f_cal.shape[0])
        for i in range(f_cal.shape[0]):
            fi = f_cal[i, dom] + v
            mi = ts.mu + eps_cal[i, dom]
            tt[i] = float(t_total(fi - mi, ts.w_chol))
            tsh[i] = t_shape(fi, mi, ts.w)
        out[label] = {"total": tt, "shape": tsh}
    return out


def claim(t_obs: float, ens: dict, test: str) -> dict:
    """Per-variant counts and the claim (largest p) of one observed statistic."""
    per = {}
    B = None
    for label, e in ens.items():
        k = int(rank_counts(t_obs, e[test])[0])
        B = e[test].size
        per[label] = {"k": k, "p": mc_p(k, B)}
    kmax = max(v["k"] for v in per.values())
    arg = [lbl for lbl, v in per.items() if v["k"] == kmax]
    return {"variants": per, "k": kmax, "B": B, "p": mc_p(kmax, B), "argmax": arg,
            "interval": list(cp_interval(kmax, B))}


# ----------------------------------------------------------------------------------------------- evaluator

class Evaluator:
    def __init__(self, design: dict, v_path: str, s5c_contract: dict, root: Path | None = None,
                 variant_mode: str = "union", log=print):
        self.design = design
        self.root = root or Path(".")
        self.log = log
        self.variant_mode = variant_mode
        self.provenance = {}
        vsha = sha256(v_path)
        if design.get("v_sha256") and vsha != design["v_sha256"]:
            raise SystemExit(f"V sha256 {vsha} != design {design['v_sha256']}")
        with np.load(v_path, allow_pickle=False) as z:
            self.v = np.asarray(z["V"], float)
            self.names = [str(s) for s in z["names"]]
        self.provenance["V"] = {"path": v_path, "sha256": vsha}
        pj = s5c_contract["measurement"]["partition_J"]
        first_pred = next(iter(design["nulls"].values()))["prediction"]
        with np.load(first_pred, allow_pickle=False) as z:
            fine_edges = {ax: np.asarray(z[f"edges_{ax}"], float) for ax in AXES}
        self.geom = build_geometry(fine_edges, pj["edges"], pj["supported_cells"])
        if self.geom.names != self.names:
            raise SystemExit("V's cell names differ from the s5c supported J cells")
        self.bands = sorted(design["lateral_endpoints"])
        delta = []
        for b in self.bands:
            e0, e1 = design["lateral_endpoints"][b]
            delta.append((self.geom.integrate(load_x(e1)) - self.geom.integrate(load_x(e0))) / 2.0)
            self.provenance[f"lateral:{b}"] = {"0": {"path": e0, "sha256": sha256(e0)},
                                               "1": {"path": e1, "sha256": sha256(e1)}}
        jit = np.array([self.geom.integrate(load_x(p)) for p in design["data_jitters"]])
        self.provenance["data_jitters"] = [{"path": p, "sha256": sha256(p)} for p in design["data_jitters"]]
        self.sur = Surrogates(bands=self.bands, delta=np.array(delta), s_num=jit.std(axis=0, ddof=1))
        self.f_jitters = jit
        self.f_data = self.geom.integrate(load_x(design["data_central"]))
        self.provenance["data_central"] = {"path": design["data_central"], "sha256": sha256(design["data_central"])}
        self.coefs = [float(c) for c in design["shift_coefficients"]]
        self.alpha = float(design["alpha_family"])

    # -- per-null inputs
    def prediction(self, key: str):
        spec = self.design["nulls"][key]
        with np.load(spec["prediction"], allow_pickle=False) as z:
            fine = {ax: np.asarray(z[f"edges_{ax}"], float) for ax in AXES}
            for ax in AXES:
                if not np.array_equal(fine[ax], np.asarray(self._fine_edges_ref()[ax])):
                    raise SystemExit(f"{key}: fine edges of {ax} differ")
            mu = self.geom.integrate(np.asarray(z["xsec_flat"], float))
            var = self.geom.integrate_var(np.asarray(z["sumw2_flat"], float))
        self.provenance[f"prediction:{key}"] = {"path": spec["prediction"], "sha256": sha256(spec["prediction"])}
        return mu, var

    def _fine_edges_ref(self):
        if not hasattr(self, "_fe"):
            first_pred = next(iter(self.design["nulls"].values()))["prediction"]
            with np.load(first_pred, allow_pickle=False) as z:
                self._fe = {ax: np.asarray(z[f"edges_{ax}"], float) for ax in AXES}
        return self._fe

    def load_ensemble(self, pattern: str, seed_lo: int, seed_hi: int | None):
        files = finished_products(pattern)
        seeds = [seed_of(p) for p in files]
        outside = [s for s in seeds if s < seed_lo or (seed_hi is not None and s >= seed_hi)]
        keep = [p for p, s in zip(files, seeds) if s >= seed_lo and (seed_hi is None or s < seed_hi)]
        prods = [load_product(p, self.geom, self.bands) for p in keep]
        return prods, outside

    def calibration_B(self, key: str) -> dict:
        spec = self.design["nulls"][key]["calibration_n"]
        st_path = spec["sequential_status"]
        if not os.path.exists(st_path):
            return {"final": None, "status_path": st_path}
        st = json.load(open(st_path))
        return {"final": st, "status_path": st_path, "status_sha256": sha256(st_path)}

    def null_context(self, key: str, prods: list[Product], kappa_list=(None,)):
        """Everything the tests of one null need, from the calibration products given."""
        spec = self.design["nulls"][key]
        mu, var = self.prediction(key)
        dom = self.geom.domain(spec["domain"])
        ts = test_setup(self.v, mu, var, dom)
        seed0 = int(spec["surrogate_seed0"])
        f_cal = np.array([self.sur.apply(p) for p in prods]) if prods else np.zeros((0, self.geom.n))
        eps = np.array([prediction_error(seed0, p.seed, var) for p in prods]) if prods else np.zeros((0, self.geom.n))
        ps = load_shift_file(self.design["process_shift"][key], self.names, f"process_shift:{key}")
        m1s = load_shift_file(self.design["m1_shift"][key], self.names, f"m1_shift:{key}")
        # the enforced shift inputs, so a comparison can check production's echoes of them instead of excluding them
        psd, m1d = self.design["process_shift"][key], self.design["m1_shift"][key]
        self.provenance[f"process_shift:{key}"] = (
            {"none": psd["none"]} if "none" in psd else {"path": psd["path"], "sha256": ps["sha256"], "mode": psd["mode"]})
        self.provenance[f"m1_shift:{key}"] = (
            {"none": m1d["none"]} if "none" in m1d else
            {"path": m1d["path"], "sha256": m1s["sha256"], "kappa": m1d["kappa"], "kappa_robust": m1d["kappa_robust"]})
        return {"spec": spec, "mu": mu, "var": var, "ts": ts, "f_cal": f_cal, "eps": eps, "ps": ps, "m1": m1s,
                "seed0": seed0}

    def shifts_for(self, ctx: dict, kappa_key: str = "kappa", mode: str | None = None):
        ts = ctx["ts"]
        mode = mode or self.variant_mode
        if "none" in ctx["ps"]:
            raise SystemExit("a null without a process-shift declaration is refused by the design")
        if ctx["f_cal"].shape[0] == 0:
            return None, {}
        sh = bias_aligned_shift(ctx["f_cal"][:, ts.dom], ts, ctx["ps"]["d_pairs"][:, ts.dom])
        mode_spec = self.design["process_shift"][ctx["key"]]["mode"]
        if mode_spec != "bias_aligned_upper":
            raise SystemExit(f"unsupported process-shift mode {mode_spec}")
        if "none" in ctx["m1"]:
            delta, kappa = None, None
        else:
            delta = ctx["m1"]["D_J"][ts.dom]
            kappa = float(self.design["m1_shift"][ctx["key"]][kappa_key])
        return sh, variant_shifts(sh["S"], delta, self.coefs, kappa, mode)

    def evaluate_null(self, key: str, prods: list[Product]) -> dict:
        ctx = self.null_context(key, prods)
        ctx["key"] = key
        ts = ctx["ts"]
        B = len(prods)
        rec = {"B": B, "domain_cells": int(ts.dom.size)}
        obs = stats_of(self.f_data[ts.dom], ts.mu, ts)
        rec["observed_T"] = obs
        if B == 0:
            rec["tests"] = {t: {"p": 1.0, "k": 0, "B": 0, "interval": [0.0, 1.0], "not_calibrated": True}
                            for t in TESTS}
            return rec, None
        sh, shifts = self.shifts_for(ctx)
        rec["process_shift"] = {k: v for k, v in sh.items() if k != "S"}
        ens = null_ensembles(ctx["f_cal"], ctx["eps"], ts, shifts)
        _, rob_shifts = self.shifts_for(ctx, "kappa_robust") if "none" not in ctx["m1"] else (None, {})
        rob_only = {k: v for k, v in rob_shifts.items() if k not in shifts}
        # A7 fixes the full Holm re-run and the labels; A7-VS (ruled later, report only) fixes the family as
        # "replace": process-shift variants UNION F +- 3 delta_M1. "retain" (claim variants UNION F +- 3 delta_M1)
        # is computed beside it as the keep-both diagnostic.
        ens_rob, ens_rob_replace = dict(ens), dict(ens)
        if rob_only:
            extra = null_ensembles(ctx["f_cal"], ctx["eps"], ts, rob_only)
            ens_rob.update(extra)
            ens_rob_replace = {k: v for k, v in ens.items() if not k.startswith("m1=")}
            ens_rob_replace.update(extra)
        _, prod_shifts = self.shifts_for(ctx, mode="product")
        ens_prod = null_ensembles(ctx["f_cal"], ctx["eps"], ts, {k: v for k, v in prod_shifts.items()})
        tests = {}
        for t in TESTS:
            c = claim(obs[t], ens, t)
            c["unshifted"] = c["variants"]["c=0"]
            c["robust_kappa3_retain_kappa2"] = claim(obs[t], ens_rob, t) if rob_only else None
            c["robust_kappa3_replace_kappa2"] = claim(obs[t], ens_rob_replace, t) if rob_only else None
            cp_ = claim(obs[t], ens_prod, t)
            c["product_reading"] = {k: cp_[k] for k in ("k", "B", "p", "argmax")}
            size = {}
            base = ens["c=0"][t]
            for lbl, e in ens.items():
                if lbl == "c=0":
                    continue
                kk = rank_counts(e[t], base)
                size[lbl] = float(np.mean(mc_p_vec(kk, base.size) <= 0.05))
            c["implied_size"] = size
            half = size.get("c=0.5")
            c["unshifted_not_calibrated_for_data_process"] = bool(half is not None and half > 0.08)
            jit = []
            for j in range(self.f_jitters.shape[0]):
                tj = stats_of(self.f_jitters[j, ts.dom], ts.mu, ts)[t]
                cj = claim(tj, ens, t)
                jit.append({"T": tj, "k": cj["k"], "p": cj["p"]})
            c["observed_jitter"] = {"p": [x["p"] for x in jit], "p_min": min(x["p"] for x in jit),
                                    "p_median": float(np.median([x["p"] for x in jit])),
                                    "p_max": max(x["p"] for x in jit), "n": len(jit), "T": [x["T"] for x in jit]}
            sd0 = float(base.std(ddof=1)) if base.size > 1 else float("nan")
            c["median_shift_in_null_sd"] = {lbl: float(np.median(e[t] - base) / sd0) for lbl, e in ens.items()
                                            if lbl != "c=0"}
            tests[t] = c
        rec["tests"] = tests
        rec["null_T_summary"] = {t: {"mean": float(ens["c=0"][t].mean()), "sd": float(ens["c=0"][t].std(ddof=1)),
                                     "median": float(np.median(ens["c=0"][t])),
                                     "min": float(ens["c=0"][t].min()), "max": float(ens["c=0"][t].max())}
                                 for t in TESTS}
        return rec, {"ens": ens, "ctx": ctx}


def mc_p_vec(k: np.ndarray, n: int) -> np.ndarray:
    return (np.asarray(k, float) + 1.0) / (n + 1.0)


def power_of_set(ev: Evaluator, set_key: str, null_ctx: dict, ens: dict) -> dict:
    spec = ev.design["power"][set_key]
    files = finished_products(spec["glob"])
    prods = [load_product(p, ev.geom, ev.bands) for p in files]
    ts = null_ctx["ts"]
    seed0 = int(spec["surrogate_seed0"])
    n_decl = int(spec["n"])
    rec = {"null": spec["null"], "n_declared": n_decl, "n_present": len(prods),
           "complete": len(prods) == n_decl, "seeds": [p.seed for p in prods]}
    if not prods:
        return rec
    B = next(iter(ens.values()))["total"].size
    rec["B_null"] = B
    for t in TESTS:
        t_alt = []
        for p in prods:
            f = ev.sur.apply(p)[ts.dom]
            m = ts.mu + prediction_error(seed0, p.seed, null_ctx["var"])[ts.dom]
            t_alt.append(float(t_total(f - m, ts.w_chol)) if t == "total" else t_shape(f, m, ts.w))
        t_alt = np.array(t_alt)
        k_per = {lbl: rank_counts(t_alt, e[t]) for lbl, e in ens.items()}
        k_claim = np.max(np.vstack(list(k_per.values())), axis=0)
        k_un = k_per["c=0"]
        out = {}
        for a in POWER_LEVELS:
            rank_un = int(np.sum(mc_p_vec(k_un, B) <= a))
            rank_cl = int(np.sum(mc_p_vec(k_claim, B) <= a))
            det = int(sum(1 for k in k_claim if cp_interval(int(k), B)[1] < a))
            n = len(prods)
            out[f"{a:g}"] = {
                "rank_unshifted": {"count": rank_un, "power": rank_un / n, "interval": list(cp_interval(rank_un, n))},
                "rank_claim": {"count": rank_cl, "power": rank_cl / n, "interval": list(cp_interval(rank_cl, n))},
                "determined_claim": {"count": det, "power": det / n, "interval": list(cp_interval(det, n))},
            }
        rec[t] = out
    return rec


def evaluate(design: dict, v_path: str, s5c_contract: dict, variant_mode: str = "union", log=print,
             sequential: bool = True) -> dict:
    ev = Evaluator(design, v_path, s5c_contract, variant_mode=variant_mode, log=log)
    out = {"schema": SCHEMA, "variant_mode": variant_mode, "ambiguities": AMBIGUITIES, "names": ev.names,
           "alpha_family": ev.alpha, "nulls": {}, "power": {}, "family": {}}
    thresholds = decision_thresholds(ev.alpha, 2 * len(design["nulls"]))
    null_state = {}
    for key, spec in design["nulls"].items():
        st = ev.calibration_B(key)
        base = seed_base_of(design, key)
        final = st["final"]
        B_final = int(final["B"]) if final else None
        hi = base + B_final if B_final is not None else None
        prods, outside = ev.load_ensemble(spec["calibration_glob"], base, hi)
        present = sorted(p.seed for p in prods)
        expect_hi = hi if hi is not None else (present[-1] + 1 if present else base)
        missing = sorted(set(range(base, expect_hi)) - set(present))
        log(f"[{key}] products {len(prods)} final B {B_final} outside-range {len(outside)} missing {len(missing)}")
        rec, state = ev.evaluate_null(key, prods)
        rec["calibration"] = {"seed_base": base, "final_status": final, "status_sha256": st.get("status_sha256"),
                              "final_status_present": final is not None, "products_used": len(prods),
                              "count_matches_final_B": (B_final == len(prods)) if final else None,
                              "seeds_outside_final_range": outside, "missing_seeds_in_range": missing,
                              "partials_excluded": len(glob.glob(spec["calibration_glob"])) -
                              len(finished_products(spec["calibration_glob"]))}
        if sequential:
            rec["sequential"] = verify_sequential(ev, key, prods, thresholds, base, design, B_final)
        out["nulls"][key] = rec
        null_state[key] = state
    entries = []
    for key in design["nulls"]:
        for t in TESTS:
            tr = out["nulls"][key]["tests"][t]
            entries.append({"test": f"{key}:{t}", "p": tr["p"], "k": tr["k"], "B": tr["B"]})
    dec = holm_determined(entries, ev.alpha)
    pt = holm_point(entries, ev.alpha)
    for e, d, p in zip(entries, dec, pt):
        key, t = e["test"].split(":")
        if out["nulls"][key]["tests"][t].get("not_calibrated"):
            d["label"] = "not calibrated"
        d["holm_point"] = p
    out["family"]["decisions"] = dec
    kappa3 = {}
    for vs, field_ in (("retain_kappa2", "robust_kappa3_retain_kappa2"), ("replace_kappa2", "robust_kappa3_replace_kappa2")):
        ents = []
        for e in entries:
            key, t = e["test"].split(":")
            r = out["nulls"][key]["tests"][t].get(field_)
            src = r if r is not None else e  # a null without M1 variants: its robust claim is its claim
            ents.append({"test": e["test"], "p": src["p"], "k": src["k"], "B": src["B"]})
        holm_rob = holm_determined(ents, ev.alpha)
        per_test = {}
        for d, e in zip(dec, ents):  # A7(b), the per-test reading: a labelled, non-adopted diagnostic
            if d["decision"] == "rejected":
                per_test[d["test"]] = bool(cp_interval(e["k"], e["B"])[1] < d["threshold"])
        kappa3[vs] = {"holm": holm_rob, "labels": robust_labels(dec, holm_rob),
                      "boolean_equivalent": {d["test"]: d["decision"] == r["decision"] for d, r in zip(dec, holm_rob)},
                      "A7b_per_test_robust_diagnostic": per_test}
    # A7-VS RULED (RULING-20260929-s5p-A7-VS-kappa3-variant-set.md, received ~2026-09-29T04:33Z, report only): the
    # kappa = 3 family REPLACES the +-2 delta_M1 members by +-3 delta_M1 and keeps the process-shift variants.
    ruled, keep = kappa3["replace_kappa2"], kappa3["retain_kappa2"]
    kappa3["ruling"] = ("A7-VS ruled 2026-09-29 (~04:33Z), a report-only clarification made then (not a recovered "
                        "pre-production definition): the kappa = 3 family is the process-shift variants UNION "
                        "F +- 3 delta_M1 (replace_kappa2). retain_kappa2 (keep both +-2 and +-3) is a diagnostic.")
    kappa3["tests_where_the_sets_differ"] = [d["test"] for d in dec
                                             if ruled["labels"][d["test"]] != keep["labels"][d["test"]]]
    out["family"]["kappa3"] = kappa3
    out["family"]["holm_at_kappa_robust"] = ruled["holm"]
    out["family"]["robust_labels"] = ruled["labels"]
    out["family"]["keep_both_kappa3_diagnostic"] = {"holm": keep["holm"], "labels": keep["labels"]}
    # the frozen evaluator's boolean (equal decision labels in the primary and its kappa = 3 re-run, whose family keeps
    # both +-2 and +-3 as the campaign reports the frozen code): reproduced as a separately named diagnostic
    out["family"]["frozen_boolean_equivalent_diagnostic"] = keep["boolean_equivalent"]
    prod_entries = []
    for key in design["nulls"]:
        for t in TESTS:
            tr = out["nulls"][key]["tests"][t]
            pr = tr.get("product_reading") or {"p": tr["p"], "k": tr["k"], "B": tr["B"]}
            prod_entries.append({"test": f"{key}:{t}", "p": pr["p"], "k": pr["k"], "B": pr["B"]})
    out["family"]["holm_product_variant_reading"] = holm_determined(prod_entries, ev.alpha)
    changed = [a["test"] for a, b in zip(dec, out["family"]["holm_product_variant_reading"])
               if a["decision"] != b["decision"]]
    out["family"]["decisions_changed_by_product_reading"] = changed
    for sk, sspec in design.get("power", {}).items():
        st = null_state.get(sspec["null"])
        if st is None:
            out["power"][sk] = {"null": sspec["null"], "n_present": 0, "note": "null has no calibration ensemble"}
            continue
        out["power"][sk] = power_of_set(ev, sk, st["ctx"], st["ens"])
    out["provenance"] = ev.provenance
    return out


def seed_base_of(design: dict, key: str) -> int:
    """The calibration seed base of a null from amendment 5/7: 1200000 + 20000 i in the family order."""
    order = ["MnvTune_v1", "GENIE_2_12_10_CV", "GENIE_2_12_10_MEC", "NuWro_21_09", "GiBUU_2019"]
    if key in order:
        return 1200000 + 20000 * order.index(key)
    return int(design["nulls"][key]["seed_base"])


def verify_sequential(ev: Evaluator, key: str, prods: list[Product], thresholds: list[float], base: int,
                      design: dict, B_final: int | None, batch: int = 200) -> dict:
    """Re-evaluate the stopping rule at every look on the products of the finished batches.

    The look before batch b (b >= 1) sees the products of batches 0..b-1 (seeds < base + 200 b, capped at the
    maximum). Looks are evaluated up to the final B when a final status exists, otherwise up to the largest B of
    the controller's per-look status files; each look is paired with the status file of the same B.
    """
    spec = design["nulls"][key]
    cn = spec["calibration_n"]
    nmax, nmin = int(cn["max"]), int(cn.get("min") or 0)
    status_dir = os.path.dirname(cn["sequential_status"])
    status_files = {}
    for p in glob.glob(os.path.join(status_dir, f"{glob.escape(key)}-B*.json")):
        m = re.search(r"-B(\d+)\.json$", p)
        if m:
            status_files[int(m.group(1))] = p
    horizon = B_final if B_final is not None else max(status_files, default=0)
    looks, first_stop = [], None
    first_stop_alt = {name: None for name in A8_READINGS if name != "primary"}
    b = 1
    while True:
        edge = base + min(batch * b, nmax)
        sub = [p for p in prods if p.seed < edge]
        if not sub or len(sub) > horizon:
            break
        ctx = ev.null_context(key, sub)
        ctx["key"] = key
        _, shifts = ev.shifts_for(ctx)
        ens = null_ensembles(ctx["f_cal"], ctx["eps"], ctx["ts"], shifts)
        obs = stats_of(ev.f_data[ctx["ts"].dom], ctx["ts"].mu, ctx["ts"])
        n = len(sub)
        k_claim = {t: claim(obs[t], ens, t)["k"] for t in TESTS}
        by_reading = {t: stop_readings(k_claim[t], n, thresholds) for t in TESTS}
        per = {t: by_reading[t]["primary"] for t in TESTS}
        rule = all(per[t]["stop"] for t in TESTS) and n >= nmin
        a8 = {}
        for name in A8_READINGS:
            if name == "primary":
                continue
            r_alt = all(by_reading[t][name]["stop"] for t in TESTS) and n >= nmin
            a8[name] = {"rule_stops": r_alt, "tests": {t: by_reading[t][name] for t in TESTS},
                        "differs_from_primary": r_alt != rule}
            if r_alt and first_stop_alt[name] is None:
                first_stop_alt[name] = n
        st_path = status_files.get(n)
        st = json.load(open(st_path)) if st_path else None
        looks.append({"B": n, "edge_seed": edge, "tests": per, "rule_stops": rule, "below_min_B": n < nmin,
                      "status_file": st_path, "status": st, "a8_sensitivity": a8})
        if rule and first_stop is None:
            first_stop = n
        if edge >= base + nmax or n >= horizon:
            break
        b += 1
    final_path = cn["sequential_status"]
    final = json.load(open(final_path)) if os.path.exists(final_path) else None
    reason = final.get("reason") if final else None
    verdicts = {"primary": stop_verdict(reason, first_stop, B_final)}
    verdicts.update({name: stop_verdict(reason, fs, B_final) for name, fs in first_stop_alt.items()})
    return {"looks": looks, "first_look_where_rule_stops": first_stop, "min_B": nmin, "max_B": nmax,
            "status_files": {str(k): v for k, v in sorted(status_files.items())},
            "final_reason": reason, "stop_verdict": verdicts["primary"],
            "a8_sensitivity": {"readings": A8_READINGS,
                               "first_look_where_rule_stops": {"primary": first_stop, **first_stop_alt},
                               "stop_verdict_by_reading": verdicts,
                               "looks_where_a_reading_differs": [lk["B"] for lk in looks
                                                                 if any(v["differs_from_primary"]
                                                                        for v in lk["a8_sensitivity"].values())],
                               "note": "sensitivity only: the primary reading alone gives the verdict; a "
                                       "disagreement between readings that binds is routed for a ruling"}}


# ----------------------------------------------------------------------------------------------- CLI

def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, float) and not math.isfinite(o):
        return str(o)
    return o


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("evaluate", help="recompute every p-value and decision from the products")
    e.add_argument("--design", required=True)
    e.add_argument("--v", required=True)
    e.add_argument("--s5c-contract", required=True)
    e.add_argument("--out", required=True)
    e.add_argument("--variant-mode", default="union", choices=["union", "product"])
    e.add_argument("--no-sequential", action="store_true")
    e.add_argument("--require-terminal", action="store_true",
                   help="refuse unless every null has a final status (the final verification)")
    m = sub.add_parser("a8-map", help="where the A8 stopping-rule readings differ, over every k at each look size")
    m.add_argument("--m", type=int, default=10, help="family size (Holm levels alpha/j, j = 1..m)")
    m.add_argument("--alpha", type=float, default=0.05)
    m.add_argument("--out", required=True)
    c = sub.add_parser("compare", help="compare a recompute output with production's joint-evaluate.json")
    c.add_argument("--mine", required=True)
    c.add_argument("--production", required=True)
    c.add_argument("--robust-labels", default=None,
                   help="production's robust-labels.json (the ruled A7 label, produced after the evaluation)")
    c.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "evaluate":
        design = json.load(open(a.design))
        if a.require_terminal:
            missing = [k for k, s in design["nulls"].items()
                       if not os.path.exists(s["calibration_n"]["sequential_status"])]
            if missing:
                print(f"NOT TERMINAL: no final status for {missing}", file=sys.stderr)
                return 4
        res = evaluate(design, a.v, json.load(open(a.s5c_contract)), variant_mode=a.variant_mode,
                       sequential=not a.no_sequential)
        res["inputs"] = {"design": a.design, "design_sha256": sha256(a.design), "v": a.v,
                         "s5c_contract": a.s5c_contract, "s5c_contract_sha256": sha256(a.s5c_contract),
                         "code_sha256": sha256(__file__)}
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(jsonable(res), indent=1, sort_keys=True) + "\n")
        print(f"wrote {a.out}")
        return 0
    if a.cmd == "a8-map":
        res = {"schema": "s5p-recompute-a8-map/1", "readings": A8_READINGS, "m": a.m, "alpha": a.alpha,
               "thresholds": decision_thresholds(a.alpha, a.m),
               "map": a8_sensitivity_map(decision_thresholds(a.alpha, a.m)), "code_sha256": sha256(__file__)}
        Path(a.out).write_text(json.dumps(jsonable(res), indent=1, sort_keys=True) + "\n")
        print(f"wrote {a.out}")
        return 0
    if a.cmd == "compare":
        from s5p_recompute_compare import compare_files
        return compare_files(a.mine, a.production, a.out, a.robust_labels)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
