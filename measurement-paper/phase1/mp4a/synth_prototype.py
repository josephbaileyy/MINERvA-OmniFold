#!/usr/bin/env python3
"""Synthetic prototype of the MP4-A solver (no MINERvA operand is read).

Controls on random smeared Poisson problems:

* S1 unconstrained: with positivity off the half-width equals psi * sqrt(h^T F^+ h) (the CR width);
* S2 t scaled up 1e6: kept as run, but NOT an idle-positivity control (the 1-D problem is so wide that
  positivity still binds); the idle control is S4 at t_scale 2e5 (n_active 0, half-width = CR);
* S3 binding positivity, small n: the endpoints agree with an independent check (scipy SLSQP from many
  starts, prototype only), the KKT residual is small and the Lagrange dual gap closes;
* S4 size and timing: a 3-D smeared problem at the real problem's size (1,331 truth cells, 10,648 reco
  cells) with relative widths in the real range, a few functionals, both endpoints;
* S5 a deliberately ill-conditioned 1-D problem (cond ~1e12, far worse than the real kept spectrum):
  failure must be reported as a status, never as a number.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import sparse
from scipy.optimize import minimize
from scipy.stats import chi2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import osb  # noqa: E402

PSI2 = float(chi2.ppf(0.6827, 1))


def problem1d(rng, n, m, width, t_scale, sparse_cut=1e-4):
    ct = (np.arange(n) + 0.5) / n
    cr = (np.arange(m) + 0.5) / m
    k = np.exp(-0.5 * ((cr[:, None] - ct[None, :]) / width) ** 2)
    k[k < sparse_cut * k.max(axis=0, keepdims=True)] = 0
    eff = rng.uniform(0.2, 0.9, n)
    r = k / k.sum(axis=0, keepdims=True) * eff
    t = t_scale * np.exp(rng.normal(0, 1.5, n))
    b = 0.01 * (r @ t).mean() * rng.uniform(0, 1, m)
    return sparse.csr_matrix(r), t, b


def problem3d(rng, nt=11, nr=22, w=0.7, t_scale=2e5):
    ct = (np.arange(nt) + 0.5) / nt
    cr = (np.arange(nr) + 0.5) / nr
    k1 = np.exp(-0.5 * ((cr[:, None] - ct[None, :]) * nt / w) ** 2)
    k1[k1 < 1e-3] = 0
    k1 /= k1.sum(0, keepdims=True)
    k1 = sparse.csr_matrix(k1)
    kk = sparse.kron(sparse.kron(k1, k1), k1).tocsr()
    n = kk.shape[1]
    eff = rng.uniform(0.2, 0.9, n)
    g = np.indices((nt,) * 3).reshape(3, -1).T / nt
    t = t_scale * np.exp(-((g - 0.3) ** 2).sum(1) / 0.08) * np.exp(rng.normal(0, 0.7, n)) + 0.1
    r = (kk @ sparse.diags(eff)).tocsr()
    b = 1e-4 * (r @ t).mean() * rng.uniform(0, 1, r.shape[0])
    return r, t, b


def fisher(r, t, b):
    e = r @ t + b
    keep = e > 0
    w = sparse.diags(1 / np.sqrt(e[keep])) @ r[keep]
    return np.asarray((w.T @ w).todense())


def cr(f, h):
    v, q = np.linalg.eigh(f)
    pos = v > 1e-12 * v.max()
    c = q[:, pos].T @ h
    return float(np.sqrt(np.sum(c**2 / v[pos])))


def brute(f, t, h, sense, starts, rng):
    """Independent check (prototype only): SLSQP in the original variables from several starts."""
    sign = 1.0 if sense == "min" else -1.0
    cons = [{"type": "ineq", "fun": lambda d: PSI2 - d @ f @ d, "jac": lambda d: -2 * f @ d}]
    best = np.inf
    for _ in range(starts):
        d0 = rng.normal(0, 0.01, t.size) * t
        res = minimize(lambda d: sign * h @ d, d0, jac=lambda d: sign * h, method="SLSQP",
                       bounds=[(-ti, None) for ti in t], constraints=cons, options={"maxiter": 2000, "ftol": 1e-14})
        if res.success and res.x @ f @ res.x <= PSI2 * (1 + 1e-6) and np.all(res.x >= -t * (1 + 1e-9)):
            best = min(best, sign * h @ res.x)
    return sign * best


def ep_record(ep, ht):
    return {"value_rel": ep.value / ht, "status": ep.status, "evals": ep.evals, "n_active": ep.n_active,
            "lsq_status": ep.lsq_status, "lsq_nit_total": ep.lsq_nit_total, "kkt_rel": ep.kkt_rel,
            "kkt_sign_rel": ep.kkt_sign_rel, "gap_rel": abs(ep.feasible_value - ep.dual_value) / ht,
            "g_over_psi2_minus_1": ep.g / PSI2 - 1, "cpu_s": ep.cpu_s}


def main() -> int:
    rng = np.random.default_rng(20261019)
    st = osb.Settings(psi2=PSI2)
    out = {"psi2": PSI2, "settings": st.as_dict(), "S1": [], "S2": [], "S3": [], "S4": {}, "S5": {}}
    for _ in range(3):
        r, t, b = problem1d(rng, 60, 300, 0.04, 50.0)
        f = fisher(r, t, b)
        red = osb.reduce(f, t)
        f_big = fisher(r, t * 1e6, b * 1e6)
        red_big = osb.reduce(f_big, t * 1e6)
        for _ in range(5):
            h = np.zeros(t.size)
            h[rng.choice(t.size, 3, replace=False)] = rng.uniform(0.5, 1.5, 3)
            lo, hi = (osb.endpoint(red, h, s, st, positivity=False) for s in ("min", "max"))
            want = np.sqrt(PSI2) * cr(f, h)
            out["S1"].append({"rel_dev": float(0.5 * (hi.value - lo.value) / want - 1), "evals": lo.evals + hi.evals})
            lo2, hi2 = (osb.endpoint(red_big, h, s, st, positivity=True) for s in ("min", "max"))
            want2 = np.sqrt(PSI2) * cr(f_big, h)
            out["S2"].append({"rel_dev": float(0.5 * (hi2.value - lo2.value) / want2 - 1),
                              "n_active": lo2.n_active + hi2.n_active})
    for _ in range(4):
        r, t, b = problem1d(rng, 12, 40, 0.12, 3.0)
        f = fisher(r, t, b)
        red = osb.reduce(f, t)
        h = np.zeros(t.size)
        h[rng.choice(t.size, 2, replace=False)] = 1.0
        for sense in ("min", "max"):
            ep = osb.endpoint(red, h, sense, st, positivity=True, floor=(-(h @ t) if sense == "min" else None))
            unc = osb.endpoint(red, h, sense, st, positivity=False)
            ref = brute(f, t, h, sense, 30, rng)
            rec = ep_record(ep, h @ t)
            rec.update({"sense": sense, "brute_slsqp_rel": ref / (h @ t), "unconstrained_rel": unc.value / (h @ t),
                        "dev_vs_brute_rel": (ep.value - ref) / (h @ t)})
            out["S3"].append(rec)
    for label, scale in (("t_scale_2e3", 2e3), ("t_scale_2e5", 2e5)):
        r, t, b = problem3d(rng, t_scale=scale)
        f = fisher(r, t, b)
        c0 = time.process_time()
        red = osb.reduce(f, t)
        rows = {"reduce_cpu_s": time.process_time() - c0, "reduced": red.info, "functionals": []}
        idx = np.indices((11,) * 3).reshape(3, -1).T
        for c in range(2):
            lo_c = rng.integers(2, 8, 3)
            h = np.all((idx >= lo_c) & (idx < lo_c + 2), axis=1) * 1.0
            ht = h @ t
            lo = osb.endpoint(red, h, "min", st, positivity=True, floor=-ht)
            hi = osb.endpoint(red, h, "max", st, positivity=True)
            rows["functionals"].append({"cr_rel": np.sqrt(PSI2) * cr(f, h) / ht,
                                        "half_width_rel": 0.5 * (hi.value - lo.value) / ht,
                                        "lo": ep_record(lo, ht), "hi": ep_record(hi, ht)})
        out["S4"][label] = rows
    r, t, b = problem1d(rng, 200, 1500, 0.02, 2000.0)
    f = fisher(r, t, b)
    red = osb.reduce(f, t)
    h = np.zeros(t.size)
    h[100:108] = 1.0
    lo = osb.endpoint(red, h, "min", st, positivity=True, floor=-(h @ t))
    hi = osb.endpoint(red, h, "max", st, positivity=True)
    out["S5"] = {"reduced": red.info, "cr_rel": np.sqrt(PSI2) * cr(f, h) / (h @ t),
                 "lo": ep_record(lo, h @ t), "hi": ep_record(hi, h @ t)}
    Path(sys.argv[1]).write_text(json.dumps(out, indent=1, default=float) + "\n")
    s1 = max(abs(x["rel_dev"]) for x in out["S1"])
    s2 = max(abs(x["rel_dev"]) for x in out["S2"])
    s3 = max(abs(x["dev_vs_brute_rel"]) for x in out["S3"])
    print(json.dumps({"S1_max_abs_rel_dev": s1, "S2_max_abs_rel_dev": s2, "S3_max_abs_dev_vs_brute_rel": s3,
                      "S3": out["S3"], "S4": out["S4"], "S5": out["S5"]}, indent=1, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
