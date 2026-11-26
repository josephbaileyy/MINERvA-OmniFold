"""Test C: a smooth true-E_nu reweight, anchored to the published cross section in-grid.

Implements DECLARATION.md. Reads the saved event tables through ../test1/events.py, the
true E_nu column (inputs/enu/<pl>.csv.gz) and the Truth-tree denominators
(inputs/truth/<pl>.csv.gz), both written by controls.py after P1-P3 pass.

    python3 test_c.py out.json            # the declared test
    python3 test_c.py --closure out.json  # code check: no Data rows and no true E_nu read

--closure replaces true E_nu by a stand-in built from the true muon and reco recoil, builds
stand-in denominators from the selected rows, and replaces every observed count by the MC
expectation under a known injected w. A correct implementation recovers the injected
coefficients and gives chi2 near 0. It reads no Data row.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "test1"))
sys.path.insert(0, str(HERE.parent))
from events import TRAINING, VALIDATION, load  # noqa: E402
from score import PT, PZ, period_mc  # noqa: E402

FLOOR, MIN_FOLD = 0.02, 5.0
FIT_EDGES = np.arange(20, 102, 2.0)  # Test 1's E_vis bins
BANDS = [(40, 50), (50, 60), (60, 80), (80, np.inf)]
EAVAIL = [-np.inf, 1, 2, 5, 10, 20, np.inf]
NCELL, NEBIN, EBIN = 224, 401, 0.5
ECENTER = (np.arange(NEBIN) + 0.5) * EBIN
FORMS = ["pwlinear", "quadratic", "cubic"]  # primary first
CLOSURE = "--closure" in sys.argv


def basis(e, form, lo, hi):
    """Design matrix of log w: the ../test1/test1.py bases without the constant column.

    log w = 0 at E_nu <= lo and is constant above hi. The anchor cancels a constant
    in-grid, so a constant column would be set only by the few unanchored rows.
    """
    t = (np.clip(e, lo, hi) - lo) / (hi - lo)
    if form == "quadratic":
        return np.stack([t, t**2], 1)
    if form == "cubic":
        return np.stack([t, t**2, t**3], 1)
    knots = np.linspace(0, 1, 7)[1:-1]
    return np.column_stack([t] + [np.maximum(t - k, 0) for k in knots])


def classes(x):
    """0: published phase space (anchored), 1: other fiducial nu_mu CC (free), 2: unchanged."""
    fidcc = (~x.is_data) & (x.origin == "nu_mu_CC") & (x.fid == 1)
    in_ps = (fidcc & (x.true_pz >= 1.5) & (x.true_pz < 60.0) & (x.true_pt >= 0.0)
             & (x.true_pt < 4.5) & (np.arctan2(x.true_pt, x.true_pz) < np.deg2rad(20)))
    cls = np.where(in_ps, 0, np.where(fidcc, 1, 2))
    cell = np.full(len(x), -1)
    cell[in_ps] = ((np.searchsorted(PT, x.true_pt[in_ps], side="right") - 1) * 16
                   + np.searchsorted(PZ, x.true_pz[in_ps], side="right") - 1)
    assert cell[in_ps].min() >= 0 and cell[in_ps].max() < NCELL
    return cls, cell


def load_inputs():
    x = load()
    x["a"] = np.where(x.is_data, 1.0, x.fold * x.own_scale)
    x["enu"] = np.nan
    pls = sorted(x.playlist.unique())
    if CLOSURE:
        mc = ~x.is_data
        stand = np.where(x.true_pz > 0, np.hypot(x.true_pt, x.true_pz) + x.energy.clip(lower=0), x.evis)
        x.loc[mc, "enu"] = stand[mc]
    else:
        for pl in pls:
            m = (x.playlist == pl) & ~x.is_data
            e = pd.read_csv(HERE / "inputs" / "enu" / f"{pl}.csv.gz").true_enu.to_numpy()
            assert len(e) == m.sum(), pl
            x.loc[m, "enu"] = e
    cls, cell = classes(x)
    x["cls"], x["cell"] = cls, cell
    if CLOSURE:
        H = np.zeros((NCELL, NEBIN))
        s = x[x.cls == 0]
        k = np.minimum((s.enu / EBIN).astype(int), NEBIN - 1)
        np.add.at(H, (s.cell.to_numpy(), k.to_numpy()), s.tune_weight.to_numpy())
        gen = sum(period_mc[f"{pl}_T"] for pl in pls)
        H *= np.where(H.sum(1) > 0, gen / np.where(H.sum(1) > 0, H.sum(1), 1), 0)[:, None]
        choice = "closure stand-in"
    else:
        ctl = json.loads((HERE / "controls.json").read_text())
        choice = ctl["P2"]["version"]
        H = np.zeros((NCELL, NEBIN))
        for pl in pls:
            t = pd.read_csv(HERE / "inputs" / "truth" / f"{pl}.csv.gz")
            t = t[t.cell < NCELL]
            v = t.sumw - (t.sumwdup if choice == "deduplicated" else 0)
            np.add.at(H, (t.cell.to_numpy(), t.ebin.to_numpy()), v.to_numpy())
    return x, H, choice


class Model:
    """Per-row weight factor f(beta) and its Jacobian for one form and support."""

    def __init__(self, x, H, form, lo, hi):
        self.H, self.form, self.lo, self.hi = H, form, lo, hi
        self.Xk = basis(ECENTER, form, lo, hi)
        self.G = H.sum(1)
        self.p = self.Xk.shape[1]

    def cellterms(self, beta):
        wk = np.exp(self.Xk @ beta)
        Gp = self.H @ wk
        ok = self.G > 0
        r = np.where(ok, self.G / np.where(ok, Gp, 1), 1.0)
        M = np.where(ok[:, None], (self.H * wk) @ self.Xk / np.where(ok, Gp, 1)[:, None], 0.0)
        return r, M

    def factor(self, rows, beta):
        X = basis(rows.enu.to_numpy(), self.form, self.lo, self.hi)
        w = np.exp(X @ beta)
        r, M = self.cellterms(beta)
        cls, cell = rows.cls.to_numpy(), rows.cell.to_numpy()
        f = np.where(cls == 0, w * r[np.maximum(cell, 0)], np.where(cls == 1, w, 1.0))
        D = np.where((cls == 0)[:, None], X - M[np.maximum(cell, 0)], np.where((cls == 1)[:, None], X, 0.0))
        return f, f[:, None] * D


def fit_rows(x, pls):
    return x[x.playlist.isin(pls) & (x.sign == "-") & (x.precision == "good")
             & x.pz.between(20, 40, inclusive="left")]


def support(x):
    s = fit_rows(x, TRAINING)
    s = s[~s.is_data]
    o = np.argsort(s.enu.to_numpy())
    cw = np.cumsum(s.a.to_numpy()[o])
    q = s.enu.to_numpy()[o][np.searchsorted(cw, 0.99 * cw[-1])]
    return 20.0, float(np.ceil(q / 10) * 10), float(q)


def binned(rows, edges, var, wts):
    return np.histogram(rows[var], edges, weights=wts)[0]


def observed(rows, edges, var, model, beta_true):
    """Data counts, or the MC expectation under beta_true in closure mode."""
    if CLOSURE:
        mc = rows[~rows.is_data]
        f, _ = model.factor(mc, beta_true)
        return binned(mc, edges, var, mc.a.to_numpy() * f)
    return binned(rows[rows.is_data], edges, var, None).astype(float)


def fit(x, model, pls, beta_true):
    s = fit_rows(x, pls)
    mc = s[~s.is_data]
    d = observed(s, FIT_EDGES, "evis", model, beta_true)
    idx = np.digitize(mc.evis.to_numpy(), FIT_EDGES) - 1
    inb = (idx >= 0) & (idx < len(FIT_EDGES) - 1)
    mc, idx, a = mc[inb], idx[inb], mc.a.to_numpy()[inb]
    nb = len(FIT_EDGES) - 1
    use = np.bincount(idx, weights=a, minlength=nb) > 0

    def mu_J(beta):
        f, J = model.factor(mc, beta)
        mu = np.bincount(idx, weights=a * f, minlength=nb)
        Jb = np.stack([np.bincount(idx, weights=a * J[:, k], minlength=nb) for k in range(model.p)], 1)
        return mu[use], Jb[use]

    def nll(beta):
        mu, J = mu_J(beta)
        return np.sum(mu - d[use] * np.log(mu)), J.T @ (1 - d[use] / mu)

    r = minimize(nll, np.zeros(model.p), jac=True, method="BFGS", options={"gtol": 1e-8, "maxiter": 2000})
    mu, J = mu_J(r.x)
    cov = np.linalg.inv(J.T @ (J / mu[:, None]))
    du = d[use]
    dev = 2 * np.sum(du * np.log(np.where(du > 0, du, 1) / mu) - (du - mu))
    return r.x, cov, float(dev), int(use.sum() - model.p), f"{r.success} ({r.message})"


def term_masks(rows):
    pz, en = rows.pz.to_numpy(), rows.energy.to_numpy()
    sign, prec = rows.sign.to_numpy(), rows.precision.to_numpy()
    out = {}
    for lo, hi in BANDS:
        b = (pz >= lo) & (pz < hi)
        for j in range(len(EAVAIL) - 1):
            out[f"T1|{lo}|{EAVAIL[j]}"] = b & (sign == "-") & (en >= EAVAIL[j]) & (en < EAVAIL[j + 1])
        out[f"neg|{lo}"] = b & (sign == "-")
        out[f"good|{lo}"] = b & (sign == "-") & (prec == "good")
        out[f"T3|{lo}"] = b & (sign == "+")
    b = (pz >= 20) & (pz < 40)
    for j in range(len(EAVAIL) - 1):
        out[f"X20|{EAVAIL[j]}"] = b & (sign == "-") & (en >= EAVAIL[j]) & (en < EAVAIL[j + 1])
    return out


def score(x, model, pls, beta, cov, beta_true):
    h = x[x.playlist.isin(pls)]
    mc, data = h[~h.is_data], h[h.is_data]
    a = mc.a.to_numpy()
    f, J = model.factor(mc, beta)
    mm = term_masks(mc)
    if CLOSURE:
        ft, _ = model.factor(mc, beta_true)
        obs = {k: float((a * ft)[m].sum()) for k, m in mm.items()}
    else:
        dm = term_masks(data)
        obs = {k: float(m.sum()) for k, m in dm.items()}
    y = {}
    for k, m in mm.items():
        jk = (a[:, None] * J)[m].sum(0)
        y[k] = dict(obs=obs[k], nom=float(a[m].sum()), mu=float((a * f)[m].sum()),
                    w2=float(((a * f) ** 2)[m].sum()), nom_w2=float((a[m] ** 2).sum()),
                    par=float(jk @ cov @ jk), J=jk)
    terms = {}
    for k, v in y.items():
        if k.startswith(("T1", "T3")) and v["nom"] >= MIN_FOLD:
            for lab, mu, w2, par in (("C", v["mu"], v["w2"], v["par"]), ("nominal", v["nom"], v["nom_w2"], 0.0)):
                var = mu + w2 + par + (FLOOR * mu) ** 2
                terms.setdefault(lab, {})[k] = (v["obs"], mu, (v["obs"] - mu) ** 2 / var)
    for lo, _ in BANDS:
        n_all, n_good = y[f"neg|{lo}"], y[f"good|{lo}"]
        if n_all["nom"] < MIN_FOLD:
            continue
        m_all, m_good = mm[f"neg|{lo}"], mm[f"good|{lo}"]
        g = m_good[m_all].astype(float)
        for lab, wts, jac in (("C", a * f, True), ("nominal", a, False)):
            W = wts[m_all]
            fr = float((W * g).sum() / W.sum())
            vmc = float((W**2 * (g - fr) ** 2).sum() / W.sum() ** 2)
            vpar = 0.0
            if jac:
                jf = (n_good["J"] - fr * n_all["J"]) / W.sum()
                vpar = float(jf @ cov @ jf)
            n, k = n_all["obs"], n_good["obs"]
            terms[lab][f"T2|{lo}"] = (k / n, fr, (k - n * fr) ** 2 / (n * fr * (1 - fr) + n**2 * (vmc + vpar)))
    return y, terms


def pvalue(c, n):
    return float(stats.chi2.sf(c, n))


def summarize(terms):
    tot = sum(v[2] for v in terms.values())
    parts = {t: sum(v[2] for k, v in terms.items() if k.startswith(t)) for t in ("T1", "T2", "T3")}
    return float(tot), len(terms), pvalue(tot, len(terms)), parts


def reading(res):
    prim = [r for r in res if r["form"] == "pwlinear"]
    sup = all(r["C"]["p"] >= 0.01 and r["nominal"]["chi2"] - r["C"]["chi2"] >= 9 for r in prim)
    con = all(r["C"]["p"] < 0.001 for r in prim)
    return "supports" if sup else "contradicts" if con else "inconclusive"


def test1_central():
    t1 = json.loads((HERE.parent / "test1" / "test1.json").read_text())
    for r in t1:
        if r["form"] == "pwlinear" and r["var"] == "evis" and r["train"] == TRAINING:
            return {lo: r["bands"][f"-|all|{lo}-{hi}"][2] for lo, hi in
                    [(40, 50), (50, 60), (60, 80), (80, "inf")]}
    return {}


def main():
    out_path = [a for a in sys.argv[1:] if not a.startswith("--")]
    x, H, choice = load_inputs()
    lo, hi, q99 = support(x)
    print(f"Mode: {'CLOSURE (stand-in E_nu, MC-expectation pseudo-data, no Data rows read)' if CLOSURE else 'declared test'}")
    print(f"Denominators: {choice}; generated in-grid weight {H.sum():.1f}")
    print(f"Support: lo {lo} GeV, hi {hi} GeV (99th percentile of fold-weighted E_nu in the training fit sample {q99:.2f})")
    t1 = test1_central() if not CLOSURE else {}
    results = []
    dirs = [("primary", TRAINING, VALIDATION), ("swap", VALIDATION, TRAINING)]
    for form in FORMS:
        model = Model(x, H, form, lo, hi)
        beta_true = np.zeros(model.p)
        if CLOSURE:  # inject log w rising to +0.3 at hi, flat below the midpoint
            beta_true = np.linalg.lstsq(model.Xk, 0.3 * np.clip((ECENTER - (lo + hi) / 2) / ((hi - lo) / 2), 0, 1), rcond=None)[0]
        for name, train, test in dirs:
            beta, cov, dev, ndf, ok = fit(x, model, train, beta_true)
            y, terms = score(x, model, test, beta, cov, beta_true)
            sc, sn = summarize(terms["C"]), summarize(terms["nominal"])
            r = {"form": form, "direction": name, "train": train, "beta": beta.tolist(), "cov": cov.tolist(),
                 "fit_deviance": dev, "fit_ndf": ndf, "converged": ok,
                 "C": {"chi2": sc[0], "n": sc[1], "p": sc[2], "parts": sc[3]},
                 "nominal": {"chi2": sn[0], "n": sn[1], "p": sn[2], "parts": sn[3]},
                 "terms": {k: list(v) for k, v in terms["C"].items()},
                 "yields": {k: {kk: vv for kk, vv in v.items() if kk != "J"} for k, v in y.items()}}
            if CLOSURE:
                r["beta_true"] = beta_true.tolist()
            results.append(r)
            print(f"\n### form {form}, {name}: fit on {','.join(train)}")
            print(f"fit deviance {dev:.1f}/{ndf}{' (deviance/ndf > 3)' if dev > 3 * ndf else ''}; converged {ok}")
            print("log w coefficients", np.round(beta, 4).tolist(), "+-", np.round(np.sqrt(np.diag(cov)), 4).tolist())
            if CLOSURE:
                print("injected          ", np.round(beta_true, 4).tolist())
            grid = np.r_[20, 30, 40, 50, 60, 80, 100, 120, 150]
            print("w at E_nu", dict(zip(grid.tolist(), np.round(np.exp(basis(grid.astype(float), form, lo, hi) @ beta), 3).tolist())))
            print(f"held-out chi2: C {sc[0]:.1f}/{sc[1]} p={sc[2]:.3g} (T1 {sc[3]['T1']:.1f}, T2 {sc[3]['T2']:.1f}, T3 {sc[3]['T3']:.1f});"
                  f" nominal {sn[0]:.1f}/{sn[1]} p={sn[2]:.3g}")
            for lo_b, hi_b in BANDS:
                v = y[f"neg|{lo_b}"]
                share = (v["mu"] - v["nom"]) / (v["obs"] - v["nom"]) if v["obs"] != v["nom"] else float("nan")
                extra = f"  Test 1 w(E_vis) {t1[lo_b]:.1f}" if lo_b in t1 and name == "primary" else ""
                print(f"  negative reco {lo_b}-{hi_b}: obs {v['obs']:.1f} fold {v['nom']:.1f} C {v['mu']:.1f} +- {np.sqrt(v['par']):.1f}"
                      f" (share of excess {share:+.2f}){extra}")
            for lo_b, hi_b in BANDS:
                v = y[f"T3|{lo_b}"]
                print(f"  positive reco {lo_b}-{hi_b}: obs {v['obs']:.1f} fold {v['nom']:.1f} C {v['mu']:.1f} +- {np.sqrt(v['par']):.1f}")
            print("  20-40 transfer, negative by E_avail:",
                  [(EAVAIL[j], round(y[f"X20|{EAVAIL[j]}"]["obs"], 1), round(y[f"X20|{EAVAIL[j]}"]["mu"], 1)) for j in range(len(EAVAIL) - 1)])
    verdict = reading(results)
    if CLOSURE:
        print(f"\nClosure only (stand-in E_nu, pseudo-data): the reading logic returns {verdict!r}; this is a code check, not a result.")
    else:
        print(f"\nReading for H_C (primary form, both directions): {verdict}")
    if out_path:
        json.dump({"mode": "closure" if CLOSURE else "declared", "support": [lo, hi, q99], "denominators": choice,
                   "reading": verdict, "results": results}, open(out_path[0], "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
