"""Test 1 of the Gemini Hydrogen-high read r1: an out-of-region E_vis rate tilt.

Fit a smooth weight w(E_vis), E_vis = reco p_parallel + E_avail, on good-curvature
(|sigma(q/p)/(q/p)| < 0.30) negative tracks at reco p_parallel 20-40 GeV/c in the six
training playlists, multiplying the all-selected fold of ../score.py event by event.
Apply the same w to every simulated track (both signs, all precisions, signal and
background) in the six held-out playlists and compare with held-out data. MC is scaled
by each playlist's own data/MC POT ratio, as in the existing controls. The swap (fit on
the held-out six, predict the training six) is also reported.

A variant w(E_avail) is fitted the same way, to separate a dependence on E_vis from one
on recoil alone at fixed reco p_parallel.
"""

import json
import sys

import numpy as np
from scipy.optimize import minimize

from events import TRAINING, VALIDATION, load

FIT_EDGES = {"evis": np.arange(20, 102, 2.0), "energy": np.r_[-1, np.arange(0, 62, 2.0)]}
BANDS = [(20, 40), (40, 50), (50, 60), (60, 80), (80, np.inf)]
EAVAIL = [-np.inf, 1, 2, 5, 10, 20, np.inf]
EVIS = [20, 40, 50, 60, 70, 80, 100, np.inf]
x = load()
x["w0"] = np.where(x.is_data, 1.0, x.fold * x.own_scale)
x["w0sq"] = np.where(x.is_data, 1.0, (x.fold * x.own_scale) ** 2)


def basis(v, form, var):
    """Design matrix of log w. Constant beyond the fit support (no extrapolated slope)."""
    lo, hi = (20.0, 80.0) if var == "evis" else (0.0, 40.0)
    t = (np.clip(v, lo, hi) - lo) / (hi - lo)
    if form == "quadratic":
        return np.stack([np.ones_like(t), t, t**2], 1)
    if form == "cubic":
        return np.stack([np.ones_like(t), t, t**2, t**3], 1)
    knots = np.linspace(0, 1, 7)[1:-1]  # piecewise-linear log w, 5 interior knots
    return np.column_stack([np.ones_like(t), t] + [np.maximum(t - k, 0) for k in knots])


def fit(frame, form, var):
    edges = FIT_EDGES[var]
    sel = frame[(frame.sign == "-") & (frame.precision == "good")
                & frame.pz.between(20, 40, inclusive="left")]
    d = np.histogram(sel[sel.is_data][var], edges)[0].astype(float)
    m = np.histogram(sel[~sel.is_data][var], edges, weights=sel[~sel.is_data].w0)[0]
    c = 0.5 * (edges[1:] + edges[:-1])
    use = m > 0
    X, d, m = basis(c[use], form, var), d[use], m[use]

    def nll(b):
        mu = m * np.exp(X @ b)
        return np.sum(mu - d * np.log(mu))

    def grad(b):
        return X.T @ (m * np.exp(X @ b) - d)

    r = minimize(nll, np.zeros(X.shape[1]), jac=grad, method="BFGS", options={"gtol": 1e-8})
    mu = m * np.exp(X @ r.x)
    hess = X.T @ (mu[:, None] * X)
    dev = 2 * np.sum(d * np.log(np.where(d > 0, d, 1) / mu) - (d - mu))
    return r.x, np.linalg.inv(hess), dev, int(use.sum() - X.shape[1])


def weights(frame, beta, form, var):
    return np.exp(basis(frame[var].to_numpy(), form, var) @ beta)


def predict(frame, beta, cov, form, var, cuts, key=None, edges=None):
    """Observed, nominal fold, w-weighted fold, its fit-parameter error (linear) and MC stat."""
    f = frame[cuts(frame)]
    data, mc = f[f.is_data], f[~f.is_data]
    group = (lambda g: np.digitize(g[key], edges) - 1) if key else (lambda g: np.zeros(len(g), int))
    n = (len(edges) - 1) if key else 1
    obs = np.bincount(group(data), minlength=n)[:n].astype(float)
    gi = group(mc)
    ok = (gi >= 0) & (gi < n)
    nom = np.bincount(gi[ok], weights=mc.w0[ok], minlength=n)
    X = basis(mc[var].to_numpy()[ok], form, var)
    central = np.bincount(gi[ok], weights=mc.w0.to_numpy()[ok] * np.exp(X @ beta), minlength=n)
    jac = (mc.w0.to_numpy()[ok] * np.exp(X @ beta))[:, None] * X  # d(yield)/d(beta), per track
    J = np.stack([np.bincount(gi[ok], weights=jac[:, k], minlength=n) for k in range(X.shape[1])], 1)
    err = np.sqrt(np.einsum("ip,pq,iq->i", J, cov, J))
    mcstat = np.sqrt(np.bincount(gi[ok], weights=mc.w0sq.to_numpy()[ok] * np.exp(2 * X @ beta), minlength=n))
    return obs, nom, central, err, mcstat


def band(lo, hi):
    return lambda g: g.pz.between(lo, hi, inclusive="left") if np.isfinite(hi) else g.pz >= lo


def fmt(obs, nom, cen, err, mcs):
    pull = (obs - cen) / np.sqrt(max(obs, 1) + mcs**2 + err**2)
    return (f"data {obs:7.0f}  fold {nom:9.1f} (d/f {obs / nom:5.3f})  w-fold {cen:9.1f} "
            f"+- {err:6.1f} fit +- {mcs:5.1f} mc (d/wf {obs / cen:5.3f})  pull {pull:+6.1f}")


def report(train, test, form, var, out):
    beta, cov, dev, ndf = fit(x[x.playlist.isin(train)], form, var)
    h = x[x.playlist.isin(test)]
    print(f"\n### w({var}), form {form}: fit on {','.join(train)}; predict {','.join(test)}")
    print(f"fit deviance {dev:.1f} / ndf {ndf}; log w coefficients {np.round(beta, 3).tolist()}")
    grid = np.r_[20, 30, 40, 45, 50, 55, 60, 70, 80] if var == "evis" else np.r_[0, 2, 5, 10, 20, 30, 40]
    import pandas as pd
    print("w at", var, dict(zip(grid.tolist(), np.round(weights(pd.DataFrame({var: grid}), beta, form, var), 3).tolist())))
    res = {"form": form, "var": var, "train": train, "deviance": dev, "ndf": ndf, "beta": beta.tolist(), "bands": {}}
    for sign in ["-", "+"]:
        for prec in ["all", "good", "poor"]:
            print(f"-- sign {sign}, precision {prec}: yields")
            for lo, hi in BANDS:
                def cut(g, lo=lo, hi=hi, sign=sign, prec=prec):
                    c = band(lo, hi)(g) & (g.sign == sign)
                    return c & (g.precision == prec) if prec != "all" else c
                o, n, c, lh, s = predict(h, beta, cov, form, var, cut)
                print(f"  reco {lo:>3}-{hi:<4} " + fmt(o[0], n[0], c[0], lh[0], s[0]))
                res["bands"][f"{sign}|{prec}|{lo}-{hi}"] = [o[0], n[0], c[0], lh[0], s[0]]
    for lo, hi in BANDS:
        print(f"-- negative, reco {lo}-{hi}: by E_avail {EAVAIL}")
        cut = lambda g, lo=lo, hi=hi: band(lo, hi)(g) & (g.sign == "-")
        o, n, c, lh, s = predict(h, beta, cov, form, var, cut, "energy", EAVAIL)
        for i in range(len(o)):
            if o[i] + n[i] > 0:
                print(f"  E_avail [{EAVAIL[i]}, {EAVAIL[i + 1]}) " + fmt(o[i], n[i], c[i], lh[i], s[i]))
        res["bands"][f"eavail|{lo}-{hi}"] = np.c_[o, n, c, lh, s].tolist()
    out.append(res)


if __name__ == "__main__":
    out = []
    print("Training:", TRAINING, "Held out:", VALIDATION)
    for var in ["evis", "energy"]:
        for form in ["quadratic", "cubic", "pwlinear"]:
            report(TRAINING, VALIDATION, form, var, out)
    for var in ["evis", "energy"]:
        report(VALIDATION, TRAINING, "pwlinear", var, out)
    json.dump(out, open(sys.argv[1], "w"), indent=1, default=float) if len(sys.argv) > 1 else None
