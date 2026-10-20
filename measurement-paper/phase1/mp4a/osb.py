"""One-at-a-time strict bounds (OSB) with positivity: a Lagrangian search over ``scipy.optimize.lsq_linear``.

Problem (MP4-A, PLAN section 5.3, frozen by BINDING-PHASE1-20261019 section 2). For a functional ``h``
on the truth grid, noise-free nominal data ``y = R t + b`` and whitening ``W = diag(1 / (R t + b))`` on
the reco cells with positive expectation,

    min / max  h . lam   subject to   || W^{1/2} (y - R lam - b) ||^2 <= psi2,   lam >= 0.

With ``delta = lam - t`` the constraint is ``delta^T F delta <= psi2`` with ``F = R^T W R`` (D-ID's
``fisher``), and positivity is ``delta >= -t``.

Exact algebraic reductions (no approximation beyond D-ID's own numerical-rank convention):

1. ``F = V diag(lambda) V^T`` (``numpy.linalg.eigh``, as D-ID's widths). ``G = diag(sqrt(lambda_+))
   V_+^T`` over D-ID's positive set ``lambda > 1e-12 max(lambda)``, so ``||G delta||^2 = delta^T F
   delta`` on that set; the dropped modes are D-ID's null modes (the caller checks them against the
   sparse whitened response).
2. ``u = diag(lambda_+^{-1/2}) V_+^T h``, so ``G^T u = V_+ V_+^T h = h_r`` and ``h_r . delta = u . (G
   delta)``. A functional whose null fraction ``||V_0^T h|| / ||h||`` exceeds D-ID's 1e-6 is a hole
   (``sigma = inf`` without positivity); the caller reduces it exactly or leaves it unresolved.

Lagrangian search. For ``s > 0`` the inner problem ``min_{delta >= -t} || G delta + s u ||^2`` (one
``lsq_linear`` call) is the Lagrangian of the lower endpoint with multiplier ``mu = 1 / (2 s)``; its
solution satisfies the KKT conditions of the endpoint problem when ``g(s) = ||G delta(s)||^2 = psi2``.
``g`` is non-decreasing in ``s`` and ``g(s) <= s^2 ||u||^2`` (projection onto a convex set containing
0), so ``s0 = psi / ||u||`` brackets from below (and is the exact answer when positivity is idle). The
root of ``phi(s) = sqrt(g(s)) - psi`` is found by an Illinois (modified regula falsi) iteration with a
bisection safeguard; the upper endpoint uses ``-u``. Each evaluation also gives a Lagrange dual value
and, when feasible, a primal value; their difference certifies the endpoint up to the accuracy of the
inner solves, which is checked by an independent KKT residual.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import lsq_linear

EIG_RTOL = 1e-12  # D-ID widths_from_eig
NULL_TOL = 1e-6  # D-ID widths_from_eig hole rule
GOOD_LSQ = (1, 2, 3)  # lsq_linear: 1 KKT/first-order < tol, 2 cost change < tol, 3 unconstrained optimal


@dataclass(frozen=True)
class Settings:
    """Declared convergence settings (recorded in DECLARATION.json before any constrained number)."""

    psi2: float
    g_rtol: float = 1e-9  # stop when |g(s) / psi2 - 1| <= g_rtol
    max_evals: int = 60  # inner lsq_linear calls per endpoint
    floor_rtol: float = 1e-6  # a feasible point within floor_rtol * |floor| of a positivity floor is optimal
    method: str = "bvls"
    lsq_solver: str = "exact"  # used only with method='trf'
    lsq_tol: float = 1e-12
    lsq_max_iter: int | None = 6915  # 5 n at grid T2 (n = 1383)
    bracket_growth: float = 2.0
    s_max_factor: float = 1e12  # no bracket below s0 * s_max_factor: endpoint "non-binding"

    def as_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


@dataclass
class Reduced:
    """The reduced problem on one grid: G (k x n) and the coefficient map u = coef @ h."""

    g: np.ndarray
    coef: np.ndarray
    vectors_null: np.ndarray
    values: np.ndarray
    t: np.ndarray
    info: dict = field(default_factory=dict)


def reduce(fisher: np.ndarray, t: np.ndarray) -> Reduced:
    values, vectors = np.linalg.eigh(fisher)
    pos = values > EIG_RTOL * values.max()
    vp = vectors[:, pos]
    sq = np.sqrt(values[pos])
    return Reduced(g=sq[:, None] * vp.T, coef=vp.T / sq[:, None], vectors_null=vectors[:, ~pos], values=values,
                   t=np.asarray(t, float),
                   info={"n": int(t.size), "k": int(pos.sum()), "n_null": int((~pos).sum()),
                         "eig_max": float(values.max()), "eig_min": float(values.min()),
                         "eig_min_kept": float(values[pos].min())})


def null_fraction(red: Reduced, h: np.ndarray) -> float:
    """D-ID's null fraction ||V_0^T h|| / ||h||."""
    return float(np.linalg.norm(red.vectors_null.T @ h) / np.linalg.norm(h))


@dataclass
class Endpoint:
    value: float  # optimum of h_r . delta (min or max), absolute units
    s: float
    g: float
    evals: int
    converged: bool
    status: str
    feasible_value: float  # best value at a feasible evaluated point (>= a min, <= a max)
    dual_value: float  # best Lagrange dual value (<= a min, >= a max)
    n_active: int
    lsq_status: list
    lsq_nit_total: int
    kkt_rel: float  # max |stationarity| on free variables / ||G^T (s u)||_inf at the final inner solve
    kkt_sign_rel: float  # most negative multiplier on bound variables, same scale (>= 0 is correct)
    cpu_s: float
    wall_s: float
    x: np.ndarray | None = None


def _kkt(red: Reduced, active_mask: np.ndarray, gx: np.ndarray, su: np.ndarray) -> tuple[float, float]:
    """Independent KKT residual of the inner solve, on lsq_linear's own active set (a variable moved to
    its bound by bvls's step can sit 1 ulp above it)."""
    grad = red.g.T @ (gx + su)  # gradient of 0.5 ||G x + s u||^2
    scale = float(np.max(np.abs(red.g.T @ su))) or 1.0
    at_bound = np.asarray(active_mask) != 0
    free = ~at_bound
    stat = float(np.max(np.abs(grad[free]))) / scale if free.any() else 0.0
    sign = float(np.min(grad[at_bound])) / scale if at_bound.any() else 0.0
    return stat, sign


def endpoint(red: Reduced, h: np.ndarray, sense: str, st: Settings, positivity: bool = True,
             keep_x: bool = False, floor: float | None = None) -> Endpoint:
    """min (sense='min') or max (sense='max') of h_r . delta over the whitened ball (and positivity).

    ``floor`` (min only): a lower bound on h . delta implied by positivity alone (``-h . t`` when h >= 0,
    since h . lam >= 0). A feasible point that reaches it is optimal whether or not the ball binds, so
    the search stops there with status ``positivity-floor``."""
    if floor is not None and sense != "min":
        raise ValueError("a positivity floor is a lower bound: min only")
    c0, w0 = time.process_time(), time.time()
    u = red.coef @ h
    if sense == "max":
        u = -u
    elif sense != "min":
        raise ValueError(sense)
    unorm = float(np.linalg.norm(u))
    n = red.t.size
    lb = -red.t if positivity else np.full(n, -np.inf)
    bounds = (lb, np.full(n, np.inf))
    psi, psi2 = float(np.sqrt(st.psi2)), st.psi2
    statuses: list = []
    nit = [0]
    evals = [0]
    best = {"feas": np.inf, "dual": -np.inf}
    last = {}

    def evaluate(s: float):
        kw = {"lsq_solver": st.lsq_solver} if st.method == "trf" else {}
        res = lsq_linear(red.g, -s * u, bounds=bounds, method=st.method, tol=st.lsq_tol, max_iter=st.lsq_max_iter,
                         **kw)
        evals[0] += 1
        statuses.append(int(res.status))
        nit[0] += int(res.nit)
        gx = red.g @ res.x
        g = float(gx @ gx)
        val = float(u @ gx)
        r = gx + s * u
        dual = float((r @ r) / (2 * s) - s * unorm**2 / 2 - psi2 / (2 * s))
        ok = int(res.status) in GOOD_LSQ
        if ok:
            best["dual"] = max(best["dual"], dual)
            if g <= psi2 * (1 + st.g_rtol):
                best["feas"] = min(best["feas"], val)
        last.update(s=s, g=g, val=val, res=res, gx=gx, ok=ok)
        if (ok and floor is not None and g <= psi2 * (1 + st.g_rtol)
                and val <= floor + st.floor_rtol * abs(floor)):
            at_floor[0] = True
        return g, ok

    at_floor = [False]

    def done(g: float) -> bool:
        return at_floor[0] or abs(g / psi2 - 1.0) <= st.g_rtol

    status = None
    s_lo = psi / unorm
    g_lo, ok = evaluate(s_lo)
    if not ok:
        status = "inner-failed"
    elif g_lo > psi2 * (1 + st.g_rtol):
        status = "projection-bound-violated"
    elif done(g_lo):
        status = "converged"
    else:
        s_hi, g_hi = s_lo, g_lo
        while True:
            s_hi *= st.bracket_growth
            if s_hi > st.s_max_factor * (psi / unorm):
                status = "non-binding"
                break
            if evals[0] >= st.max_evals:
                status = "max-evals"
                break
            g_hi, ok = evaluate(s_hi)
            if not ok:
                status = "inner-failed"
                break
            if done(g_hi):
                status = "converged"
                break
            if g_hi > psi2:
                break
            s_lo, g_lo = s_hi, g_hi
        if status is None:
            f_lo, f_hi = np.sqrt(g_lo) - psi, np.sqrt(g_hi) - psi
            side = 0
            while True:
                if evals[0] >= st.max_evals:
                    status = "max-evals"
                    break
                s_new = (s_lo * f_hi - s_hi * f_lo) / (f_hi - f_lo)
                if not (s_lo < s_new < s_hi):
                    s_new = 0.5 * (s_lo + s_hi)
                g, ok = evaluate(s_new)
                if not ok:
                    status = "inner-failed"
                    break
                if done(g):
                    status = "converged"
                    break
                f = np.sqrt(g) - psi
                if f < 0:
                    s_lo, f_lo = s_new, f
                    if side == -1:
                        f_hi *= 0.5
                    side = -1
                else:
                    s_hi, f_hi = s_new, f
                    if side == 1:
                        f_lo *= 0.5
                    side = 1
                if s_hi - s_lo <= 1e-15 * s_hi:
                    status = "bracket-collapsed"
                    break
    if at_floor[0] and status == "converged":
        status = "positivity-floor"
    res, gx, s = last["res"], last["gx"], last["s"]
    stat, sign_ = _kkt(red, res.active_mask, gx, s * u)
    sgn = 1.0 if sense == "min" else -1.0
    return Endpoint(value=sgn * last["val"], s=float(s), g=float(last["g"]), evals=evals[0],
                    converged=(status in ("converged", "positivity-floor")), status=status,
                    feasible_value=sgn * best["feas"], dual_value=sgn * best["dual"],
                    n_active=int(np.sum(res.active_mask != 0)), lsq_status=sorted(set(statuses)),
                    lsq_nit_total=nit[0], kkt_rel=stat, kkt_sign_rel=sign_,
                    cpu_s=time.process_time() - c0, wall_s=time.time() - w0, x=(res.x if keep_x else None))
