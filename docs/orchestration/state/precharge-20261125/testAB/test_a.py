"""Test A (DECLARATION.md): one recoil function for all reco p_parallel bands."""

import json
import sys

import numpy as np
from scipy.optimize import minimize

from common import BANDS, MIN_FOLD, chi2, directions, frame, pvalue

EAV = [-np.inf, 1, 2, 3, 5, 7.5, 10, 15, 20, np.inf]
SGRID = np.round(np.arange(0.90, 1.2001, 0.01), 2)
x = frame()
g = x[(x.sign == "-") & (x.precision == "good")].copy()


def hist(sub, energy=None):
    """Data, MC, MC sum w^2 and MC mean p_parallel/E_avail on the 5 x 9 grid."""
    d = sub[sub.is_data]
    m = sub[~sub.is_data]
    e = m.energy.to_numpy() if energy is None else energy[~sub.is_data.to_numpy()]
    edges = (BANDS, EAV)
    D = np.histogram2d(d.pz, d.energy, edges)[0]
    M = np.histogram2d(m.pz, e, edges, weights=m.w0)[0]
    W2 = np.histogram2d(m.pz, e, edges, weights=m.w0**2)[0]
    PZ = np.histogram2d(m.pz, e, edges, weights=m.w0 * m.pz)[0]
    EA = np.histogram2d(m.pz, e, edges, weights=m.w0 * e)[0]
    return D, M, W2, PZ, EA


def poisson_fit(D, M, design, start):
    use = M > 0
    d, m, X = D[use], M[use], design[use]

    def f(b):
        mu = m * np.exp(X @ b)
        return np.sum(mu - d * np.log(mu)), X.T @ (mu - d)

    r = minimize(f, start, jac=True, method="BFGS", options={"gtol": 1e-9, "maxiter": 10000})
    mu = m * np.exp(X @ r.x)
    hess = X.T @ (mu[:, None] * X)
    dev = 2 * np.sum(d * np.log(np.where(d > 0, d, 1) / mu) - (d - mu))
    return r.x, np.linalg.inv(hess), dev, int(use.sum() - X.shape[1])


def design_sep(shape, z=None, e=None):
    nb, ne = shape
    cols = []
    for i in range(nb):
        a = np.zeros(shape); a[i, :] = 1; cols.append(a)
    for j in range(1, ne):
        b = np.zeros(shape); b[:, j] = 1; cols.append(b)
    if z is not None:
        cols.append(np.outer(z, np.ones(ne)) * np.outer(np.ones(nb), e))
    return np.stack(cols, -1)


def score(D, M, W2, X, beta, cov, floor=True):
    lin = X @ beta
    mu = M * np.exp(lin)
    jac = mu[..., None] * X
    var_par = np.einsum("...p,pq,...q->...", jac, cov, jac)
    var_mc = W2 * np.exp(2 * lin)
    ok = M >= MIN_FOLD
    return chi2(D[ok], mu[ok], var_mc[ok], var_par[ok], floor), int(ok.sum()), mu


def run_direction(name, train, test, out):
    tr, te = g[g.playlist.isin(train)], g[g.playlist.isin(test)]
    D, M, W2, PZ, EA = hist(tr)
    Dh, Mh, W2h, *_ = hist(te)
    z = (PZ.sum(1) / M.sum(1) - 30) / 30
    e = np.log1p(EA.sum(0) / M.sum(0))
    rep = {"direction": name, "z": z.tolist(), "e": e.tolist()}
    print(f"\n## {name}: fit {','.join(train)}; score {','.join(test)}")
    print("held-out cells scored (fold >= 5):", int((Mh >= MIN_FOLD).sum()), "of", Mh.size)
    # A1 separable and interaction
    Xs = design_sep(M.shape)
    bs, cs, devs, ndfs = poisson_fit(D, M, Xs, np.zeros(Xs.shape[-1]))
    Xi = design_sep(M.shape, z, e)
    bi, ci, devi, ndfi = poisson_fit(D, M, Xi, np.r_[bs, 0.0])
    gam, sg = bi[-1], np.sqrt(ci[-1, -1])
    for floor in (True, False):
        c_s, n, mu_s = score(Dh, Mh, W2h, Xs, bs, cs, floor)
        c_i, _, _ = score(Dh, Mh, W2h, Xi, bi, ci, floor)
        tag = "floor 2%" if floor else "no floor"
        print(f"A1 [{tag}] separable held-out chi2 {c_s:.1f}/{n} p={pvalue(c_s, n):.3g};"
              f" interaction chi2 {c_i:.1f}/{n} p={pvalue(c_i, n):.3g}; delta chi2 (sep - int) {c_s - c_i:+.1f}")
        if floor:
            rep["A1"] = {"chi2_sep": c_s, "chi2_int": c_i, "ncells": n, "p_sep": pvalue(c_s, n),
                         "p_int": pvalue(c_i, n), "gamma": gam, "sigma_gamma": sg,
                         "train_dev_sep": devs, "train_ndf_sep": ndfs, "train_dev_int": devi, "train_ndf_int": ndfi}
    print(f"training deviance separable {devs:.1f}/{ndfs}, interaction {devi:.1f}/{ndfi}; gamma {gam:+.4f} +- {sg:.4f} ({gam / sg:+.1f} sigma)")
    print("a_i (log):", np.round(bs[:5], 4).tolist(), " b_j (log, first bin 0):", np.round(np.r_[0, bs[5:]], 4).tolist())
    print("held-out data/separable prediction by cell (fold >= 5):")
    ratio = np.where(Mh >= MIN_FOLD, Dh / np.where(mu_s > 0, mu_s, 1), np.nan)
    print(np.array2string(ratio, precision=3, max_line_width=200))
    # A2 single scale
    trm = ~tr.is_data.to_numpy()
    tem = ~te.is_data.to_numpy()
    Xa = design_sep((M.shape[0], 1))[:, 0, :]  # per-band normalisation only
    Xa = np.repeat(Xa[:, None, :], M.shape[1], 1)
    best = None
    scan = []
    for s in SGRID:
        es = tr.energy.to_numpy() * np.where(trm, s, 1.0)
        Ds, Ms, W2s, *_ = hist(tr, es)
        ba, ca, deva, ndfa = poisson_fit(Ds, Ms, Xa, np.zeros(Xa.shape[-1]))
        scan.append([float(s), deva])
        if best is None or deva < best[1]:
            best = (s, deva, ba, ca, ndfa)
        # per-band s_i: deviance of each band row separately
    s0, dev0, ba, ca, ndfa = best
    eh = te.energy.to_numpy() * np.where(tem, s0, 1.0)
    Dh2, Mh2, W2h2, *_ = hist(te, eh)
    c_a, n_a, _ = score(Dh2, Mh2, W2h2, Xa, ba, ca, True)
    c_a0, _, _ = score(Dh2, Mh2, W2h2, Xa, ba, ca, False)
    scan = np.array(scan)
    # per-band best s_i and a parabola-based 1-sigma (delta dev = 1) on the grid
    per_band = []
    for i in range(M.shape[0]):
        devs_i = []
        for s in SGRID:
            es = tr.energy.to_numpy() * np.where(trm, s, 1.0)
            Ds, Ms, *_ = hist(tr, es)
            d, m = Ds[i], Ms[i]
            k = d.sum() / m.sum()
            mu = k * m
            u = m > 0
            devs_i.append(2 * np.sum(d[u] * np.log(np.where(d[u] > 0, d[u], 1) / mu[u]) - (d[u] - mu[u])))
        devs_i = np.array(devs_i)
        j = int(np.argmin(devs_i))
        inside = SGRID[devs_i <= devs_i[j] + 1]
        per_band.append([float(SGRID[j]), float(inside.min()), float(inside.max()), float(devs_i[j])])
    sig = np.array([max((b[2] - b[1]) / 2, 0.005) for b in per_band])
    sv = np.array([b[0] for b in per_band])
    wmean = float(s0)
    cons = float(np.sum((sv - wmean) ** 2 / sig**2))
    print(f"A2 best common s = {s0:.2f} (training deviance {dev0:.1f}/{ndfa}); held-out chi2 [floor 2%] {c_a:.1f}/{n_a} p={pvalue(c_a, n_a):.3g}; [no floor] {c_a0:.1f}")
    print("A2 per-band best s_i [delta-dev<=1 range]:", [f"{b[0]:.2f} [{b[1]:.2f},{b[2]:.2f}]" for b in per_band],
          f"; consistency chi2 about common s {wmean:.3f}: {cons:.1f}/{len(sv) - 1} (grid-step sigma floor 0.005)")
    rep["A2"] = {"s": float(s0), "chi2": c_a, "ncells": n_a, "p": pvalue(c_a, n_a), "chi2_nofloor": c_a0,
                 "per_band": per_band, "consistency_chi2": cons, "scan": scan.tolist()}
    out.append(rep)


def reading(r):
    a1 = r["A1"]
    zg = a1["gamma"] / a1["sigma_gamma"]
    dchi = a1["chi2_sep"] - a1["chi2_int"]
    if a1["p_sep"] >= 0.01 and abs(zg) < 3 and dchi < 9:
        h = "supports"
    elif a1["p_sep"] < 0.001 or (abs(zg) >= 3 and dchi >= 9):
        h = "contradicts"
    else:
        h = "inconclusive"
    a2 = r["A2"]["p"]
    h2 = "supports" if a2 >= 0.01 else ("contradicts" if a2 < 0.001 else "inconclusive")
    return h, h2, zg, dchi


if __name__ == "__main__":
    out = []
    for name, tr, te in directions():
        run_direction(name, tr, te, out)
    print("\n## Readings against DECLARATION.md")
    for r in out:
        h, h2, zg, dchi = reading(r)
        print(f"{r['direction']}: H_A (A1) {h} [p_sep {r['A1']['p_sep']:.3g}, gamma {zg:+.1f} sigma, held-out delta chi2 {dchi:+.1f}];"
              f" A2 single scale {h2} [s {r['A2']['s']:.2f}, p {r['A2']['p']:.3g}]")
    if len(sys.argv) > 1:
        json.dump(out, open(sys.argv[1], "w"), indent=1, default=float)
