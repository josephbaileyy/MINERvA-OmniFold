"""Test B (DECLARATION.md): constant curvature offset against a reco-p_parallel rate tilt."""

import json
import sys

import numpy as np
from scipy.optimize import minimize

from common import FLOOR, MIN_FOLD, directions, frame, pvalue

EGRID = np.round(np.arange(-0.0040, 0.00401, 0.0001), 4)
FIT_EDGES = np.arange(25, 60.01, 2.5)
SC = [(40, 50), (50, 60), (60, 80), (80, np.inf)]
x = frame()


def shifted(mc, eps):
    """Per-track reco quantities after q/p -> q/p + eps (curvature tracks only)."""
    qp = mc.qp.to_numpy()
    pz, pt = mc.pz.to_numpy(), mc.pt.to_numpy()
    fe = mc.fracerr.to_numpy()
    curv = (mc.curv.to_numpy() == 1) & np.isfinite(qp) & (qp != 0) & (np.abs(qp) < 999)
    qn = np.where(curv, qp + eps, qp)
    with np.errstate(divide="ignore", invalid="ignore"):
        pc, pcn = 1 / np.abs(qp), 1 / np.abs(qn)
        p = np.hypot(pz, pt)
        scale = np.where(curv, (p + (pcn - pc)) / p, 1.0)
        fen = np.where(curv, fe * qp / qn, fe)
    pzn, ptn = pz * scale, pt * scale
    keep = (ptn >= 0) & (ptn < 4.5) & (pzn >= 20) & np.isfinite(pzn)
    sign = np.where(qn < 0, "-", np.where(qn > 0, "+", "zero"))
    sign = np.where(curv, sign, mc.sign.to_numpy())
    validfe = (mc.curv.to_numpy() == 1) & np.isfinite(fen) & (np.abs(fen) < 9999)
    prec = np.where(validfe, np.where(np.abs(fen) < 0.3, "good", "poor"), "other")
    return pzn, sign, prec, keep


def tables(sub, eps=None, tilt=None):
    """Observable yields: dict of name -> (value, w2) for MC, or counts for data."""
    is_d = sub.is_data.to_numpy()
    if is_d.all():
        pz, sign, prec, keep, w = sub.pz.to_numpy(), sub.sign.to_numpy(), sub.precision.to_numpy(), np.ones(len(sub), bool), np.ones(len(sub))
    else:
        pz, sign, prec, keep = shifted(sub, eps if eps is not None else 0.0)
        w = sub.w0.to_numpy().copy()
        if tilt is not None:
            w = w * np.clip(1 + tilt * (sub.pz.to_numpy() - 25) / 35, 0, None)
    low = sub.energy.to_numpy() < 1
    out = {}

    def add(name, m):
        m = m & keep
        out[name] = (w[m].sum(), (w[m] ** 2).sum())

    neg, pos = sign == "-", sign == "+"
    add("fit", neg & low & (pz >= 25) & (pz < 60))
    for i in range(len(FIT_EDGES) - 1):
        add(f"fitbin{i}", neg & low & (pz >= FIT_EDGES[i]) & (pz < FIT_EDGES[i + 1]))
    add("pos20", pos & (pz >= 20) & (pz < 40))
    for lo, hi in SC:
        b = (pz >= lo) & (pz < hi)
        add(f"S1|{lo}", neg & low & b)
        add(f"S2|{lo}", neg & b)
        add(f"S3|{lo}", pos & b)
        add(f"S4good|{lo}", neg & b & (prec == "good"))
    return out


def fit_bins(t):
    return np.array([t[f"fitbin{i}"][0] for i in range(len(FIT_EDGES) - 1)])


def dev(d, mu):
    return 2 * np.sum(d * np.log(np.where(d > 0, d, 1) / mu) - (d - mu))


def fit_eps(dtr, mtr):
    d = fit_bins(tables(dtr))
    devs, ks = [], []
    for e in EGRID:
        m = fit_bins(tables(mtr, eps=e))
        k = d.sum() / m.sum()
        devs.append(dev(d, k * m)); ks.append(k)
    devs = np.array(devs)
    j = int(np.argmin(devs))
    lo, hi = max(j - 3, 0), min(j + 4, len(EGRID))
    c2, c1, _ = np.polyfit(EGRID[lo:hi], devs[lo:hi], 2)
    sigma = np.sqrt(2 / (2 * c2)) if c2 > 0 else np.nan  # delta dev = 1
    return float(EGRID[j]), float(sigma), float(ks[j]), float(devs[j]), len(d) - 2, devs, float(np.sqrt(d.sum()))


def fit_rate(dtr, mtr):
    d = fit_bins(tables(dtr))
    m0 = fit_bins(tables(mtr))
    centers = 0.5 * (FIT_EDGES[1:] + FIT_EDGES[:-1])
    # model mu = exp(a) * sum over tracks of w (1 + c t); bin-level t from the tilt applied per track
    m1 = fit_bins(tables(mtr, tilt=1.0)) - m0  # sum w t per bin

    def f(b):
        mu = np.exp(b[0]) * (m0 + b[1] * m1)
        mu = np.maximum(mu, 1e-12)
        return np.sum(mu - d * np.log(mu))

    r = minimize(f, [0.0, 0.0], method="Nelder-Mead", options={"xatol": 1e-10, "fatol": 1e-10, "maxiter": 20000})
    k, c = np.exp(r.x[0]), r.x[1]
    mu = k * (m0 + c * m1)
    # Hessian in (k, c)
    J = np.stack([m0 + c * m1, k * m1], 1)
    H = J.T @ (J * (d / mu**2)[:, None])
    return float(k), float(c), np.linalg.inv(H), float(dev(d, mu)), len(d) - 2


def score(obs, pred, var_extra):
    terms = {}
    for lo, _ in SC:
        for s in ("S1", "S2", "S3"):
            o = obs[f"{s}|{lo}"][0]
            mu, w2 = pred[f"{s}|{lo}"]
            if pred[f"base{s}|{lo}"] < MIN_FOLD:
                continue
            v = mu + w2 + var_extra.get(f"{s}|{lo}", 0) + (FLOOR * mu) ** 2
            terms[f"{s}|{lo}"] = (o, mu, (o - mu) ** 2 / v)
        n = obs[f"S2|{lo}"][0]
        kgood = obs[f"S4good|{lo}"][0]
        f = pred["S4f"][lo]
        vf = pred["S4vf"][lo]
        if pred[f"baseS2|{lo}"] >= MIN_FOLD:
            terms[f"S4|{lo}"] = (kgood / n, f, (kgood - n * f) ** 2 / (n * f * (1 - f) + n**2 * vf))
    return terms


def predictions(mte, dte, k, eps=None, tilt=None, base=None):
    t = tables(mte, eps=eps, tilt=tilt)
    pos_norm = tables(dte)["pos20"][0] / t["pos20"][0]
    pred = {}
    for lo, _ in SC:
        for s in ("S1", "S2"):
            pred[f"{s}|{lo}"] = (k * t[f"{s}|{lo}"][0], k**2 * t[f"{s}|{lo}"][1])
        pred[f"S3|{lo}"] = (pos_norm * t[f"S3|{lo}"][0], pos_norm**2 * t[f"S3|{lo}"][1])
        for s in ("S1", "S2", "S3"):
            pred[f"base{s}|{lo}"] = base[f"{s}|{lo}"][0] if base else t[f"{s}|{lo}"][0]
    pred["S4f"], pred["S4vf"] = {}, {}
    return pred, t, pos_norm


def s4_fraction(mte, eps=None, tilt=None):
    """Good fraction among negative tracks per band, and its MC-statistical variance."""
    pz, sign, prec, keep = shifted(mte, eps if eps is not None else 0.0)
    w = mte.w0.to_numpy().copy()
    if tilt is not None:
        w = w * np.clip(1 + tilt * (mte.pz.to_numpy() - 25) / 35, 0, None)
    f, vf = {}, {}
    for lo, hi in SC:
        m = keep & (sign == "-") & (pz >= lo) & (pz < hi)
        g = (prec[m] == "good").astype(float)
        W = w[m]
        fr = (W * g).sum() / W.sum()
        f[lo], vf[lo] = fr, float((W**2 * (g - fr) ** 2).sum() / W.sum() ** 2)
    return f, vf


def run_direction(name, train, test, out):
    tr, te = x[x.playlist.isin(train)], x[x.playlist.isin(test)]
    dtr, mtr = tr[tr.is_data], tr[~tr.is_data]
    dte, mte = te[te.is_data], te[~te.is_data]
    print(f"\n## {name}: fit {','.join(train)}; score {','.join(test)}")
    eps, seps, k, d_eps, ndf, devs, nfit = fit_eps(dtr, mtr)
    print(f"epsilon fit: eps = {eps:+.4f} +- {seps:.4f} (GeV/c)^-1 ({eps / seps:+.1f} sigma), k = {k:.4f},"
          f" training deviance {d_eps:.1f}/{ndf}; deviance at eps=0 {devs[np.argmin(np.abs(EGRID))]:.1f}")
    kr, cr, covr, d_rate, ndfr = fit_rate(dtr, mtr)
    print(f"rate fit: k = {kr:.4f}, c = {cr:+.4f} +- {np.sqrt(covr[1, 1]):.4f}, training deviance {d_rate:.1f}/{ndfr}")
    obs = tables(dte)
    base = tables(mte)
    res = {"direction": name, "eps": eps, "sigma_eps": seps, "k": k, "train_dev_eps": d_eps,
           "rate_k": kr, "rate_c": cr, "train_dev_rate": d_rate, "ndf_fit": ndf}
    for label, kw, kk in [("epsilon", {"eps": eps}, k), ("rate", {"tilt": cr}, kr)]:
        pred, t, pn = predictions(mte, dte, kk, base=base, **kw)
        pred["S4f"], pred["S4vf"] = s4_fraction(mte, **kw)
        extra = {}
        if label == "epsilon":
            up, _, _ = predictions(mte, dte, kk, eps=eps + seps, base=base)
            dn, _, _ = predictions(mte, dte, kk, eps=eps - seps, base=base)
            for key in pred:
                if "|" in key and not key.startswith("base"):
                    extra[key] = (0.5 * (up[key][0] - dn[key][0])) ** 2 + (pred[key][0] / nfit) ** 2 * (key[:2] != "S3")
        else:
            up, _, _ = predictions(mte, dte, kr, tilt=cr + np.sqrt(covr[1, 1]), base=base)
            dn, _, _ = predictions(mte, dte, kr, tilt=cr - np.sqrt(covr[1, 1]), base=base)
            for key in pred:
                if "|" in key and not key.startswith("base"):
                    extra[key] = (0.5 * (up[key][0] - dn[key][0])) ** 2 + (pred[key][0] * np.sqrt(covr[0, 0]) / kr) ** 2 * (key[:2] != "S3")
        for key in [k_ for k_ in extra if k_.startswith("S3")]:
            extra[key] += pred[key][0] ** 2 / max(obs["pos20"][0], 1)
        terms = score(obs, pred, extra)
        tot = sum(v[2] for v in terms.values())
        n = len(terms)
        print(f"-- {label} model, held-out: chi2 {tot:.1f}/{n} p={pvalue(tot, n):.3g}")
        for s in ("S1", "S2", "S3", "S4"):
            part = {kk_: v for kk_, v in terms.items() if kk_.startswith(s)}
            print(f"   {s}: chi2 {sum(v[2] for v in part.values()):6.1f}  " +
                  "  ".join(f"{kk_.split('|')[1]}: obs {v[0]:.4g} pred {v[1]:.4g}" for kk_, v in part.items()))
        res[label] = {"chi2": tot, "n": n, "p": pvalue(tot, n),
                      "terms": {kk_: list(v) for kk_, v in terms.items()}}
    nominal = {f"{s}|{lo}": (obs[f"{s}|{lo}"][0], base[f"{s}|{lo}"][0]) for s in ("S1", "S2", "S3") for lo, _ in SC}
    print("held-out data vs unvaried fold (reference):", {kk_: (v[0], round(v[1], 1)) for kk_, v in nominal.items()})
    res["eps_scan"] = [[float(e), float(d)] for e, d in zip(EGRID, devs)]
    out.append(res)


def reading(r):
    z = r["eps"] / r["sigma_eps"]
    ce, cr = r["epsilon"]["chi2"], r["rate"]["chi2"]
    if abs(z) >= 3 and r["epsilon"]["p"] >= 0.01 and cr - ce >= 9:
        return "supports", z
    if abs(z) < 2 or ce - cr >= 9:
        return "contradicts", z
    return "inconclusive", z


if __name__ == "__main__":
    out = []
    for name, tr, te in directions():
        run_direction(name, tr, te, out)
    print("\n## Readings against DECLARATION.md")
    for r in out:
        h, z = reading(r)
        print(f"{r['direction']}: H_B {h} [eps {r['eps']:+.4f} ({z:+.1f} sigma); held-out chi2 epsilon {r['epsilon']['chi2']:.1f}/{r['epsilon']['n']}"
              f" (p {r['epsilon']['p']:.3g}), rate {r['rate']['chi2']:.1f}/{r['rate']['n']} (p {r['rate']['p']:.3g})]")
    if len(sys.argv) > 1:
        json.dump(out, open(sys.argv[1], "w"), indent=1, default=float)
