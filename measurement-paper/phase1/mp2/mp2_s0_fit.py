#!/usr/bin/env python3
"""MP-2 S0 step 2: the descriptive classifier fits (mp2_s0_declaration.json). DESCRIPTIVE ONLY: no J cell, no hybrid
null and no unfolding is read; the weights are not written out for any downstream use.

Pairs: Tune v1 (label 0) vs NuWro (label 1); NuWro vs NuWro (seeded random half split, the G-vs-G control); Tune v1 vs
Tune v1 (the same control on the MC side). Each on the 5 scalars and on the full feature set.

Usage (root_6_28: lightgbm, sklearn): python3 mp2_s0_fit.py FEATDIR DECLARATION OUTDIR NTHREADS
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

EDGES5 = [np.asarray(e, float) for e in (
    [0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5],
    [1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60],
    [0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100], [0, 0.2, 0.4, 0.6, 0.8, 1.2, 2.0, 100], [0, 1.1, 1.4, 1.8, 2.2, 3.0, 100])]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def fine_cell(X5):
    """np.histogramdd's bin convention (last bin closed on the right), flat C-order index."""
    idx = np.zeros(X5.shape[0], np.int64)
    for i, e in enumerate(EDGES5):
        b = np.searchsorted(e, X5[:, i], side="right") - 1
        b = np.where(X5[:, i] == e[-1], e.size - 2, b)
        idx = idx * (e.size - 1) + b
    return idx


def split3(n, seed, fr):
    perm = np.random.default_rng(seed).permutation(n)
    a, b = int(fr["train"] * n), int((fr["train"] + fr["valid"]) * n)
    return perm[:a], perm[a:b], perm[b:]


def balanced(w, y):
    """Each class sums to half the row count (mean weight 1), so LightGBM's min_sum_hessian_in_leaf keeps its
    usual meaning; AUC and p/(1-p) up to a constant are unchanged by the global scale."""
    out = np.asarray(w, float).copy()
    for c in (0, 1):
        out[y == c] *= 0.5 * y.size / out[y == c].sum()
    return out


def fit_pair(name, X0, w0, X1, w1, feats, decl, nthreads, cells0=None):
    import lightgbm as lgb
    from sklearn.metrics import roc_auc_score
    fr, seed = decl["fits"]["split"], decl["fits"]["split"]["seed"]
    tr0, va0, te0 = split3(X0.shape[0], seed, fr)
    tr1, va1, te1 = split3(X1.shape[0], seed + 1, fr)

    def stack(i0, i1):
        X = np.vstack([X0[i0], X1[i1]])
        y = np.concatenate([np.zeros(i0.size, int), np.ones(i1.size, int)])
        return X, y, balanced(np.concatenate([w0[i0], w1[i1]]), y)
    Xtr, ytr, wtr = stack(tr0, tr1)
    Xva, yva, wva = stack(va0, va1)
    Xte, yte, wte = stack(te0, te1)
    params = dict(decl["fits"]["params"], n_jobs=nthreads)
    clf = lgb.LGBMClassifier(**params)
    t0 = time.time()
    clf.fit(Xtr, ytr, sample_weight=wtr, eval_set=[(Xva, yva)], eval_sample_weight=[wva],
            callbacks=[lgb.early_stopping(decl["fits"]["early_stopping_rounds"], verbose=False)])
    t_fit = time.time() - t0
    t0 = time.time()
    p = clf.predict_proba(Xte)[:, 1]
    t_pred = time.time() - t0
    auc = float(roc_auc_score(yte, p, sample_weight=wte))
    auc_tr = float(roc_auc_score(ytr, clf.predict_proba(Xtr)[:, 1], sample_weight=wtr))
    r = {"pair": name, "features": feats, "n0": int(X0.shape[0]), "n1": int(X1.shape[0]),
         "n_train": int(ytr.size), "n_test": int(yte.size), "auc_test": auc, "auc_train": auc_tr,
         "best_iteration": int(clf.best_iteration_ or params["n_estimators"]), "fit_s": round(t_fit, 2),
         "predict_test_s": round(t_pred, 2), "us_per_train_row_per_iter":
             round(1e6 * t_fit / max(1, ytr.size) / max(1, clf.best_iteration_ or 1), 4)}
    # weights on the class-0 test rows (Tune v1 for the main pair)
    p0 = np.clip(p[yte == 0], 1e-12, 1 - 1e-12)
    w = p0 / (1 - p0)
    wt = w0[te0]
    w = w * wt.sum() / np.sum(wt * w)
    v = wt * w
    ess_v = v.sum() ** 2 / np.sum(v * v)
    ess_t = wt.sum() ** 2 / np.sum(wt * wt)
    lw = np.log(w)
    mu = np.sum(wt * lw) / wt.sum()
    var_tot = float(np.sum(wt * (lw - mu) ** 2) / wt.sum())
    r.update({"kish_ess_over_N": float(ess_v / te0.size), "kish_ess_over_ess_wtruth": float(ess_v / ess_t),
              "max_w_normalised": float(w.max()), "w_quantiles_0.001_0.5_0.999": [float(q) for q in
                                                                                 np.quantile(w, [0.001, 0.5, 0.999])],
              "var_logw_total": var_tot})
    if cells0 is not None:
        c = cells0[te0]
        order = np.argsort(c, kind="stable")
        cs, lws, wts = c[order], lw[order], wt[order]
        starts = np.r_[0, np.nonzero(np.diff(cs))[0] + 1]
        n_c = np.diff(np.r_[starts, cs.size])
        sw = np.add.reduceat(wts, starts)
        m1 = np.add.reduceat(wts * lws, starts) / sw
        m2 = np.add.reduceat(wts * lws * lws, starts) / sw
        var_c = np.maximum(m2 - m1 * m1, 0.0)
        use = n_c >= 20
        r.update({"var_logw_within_cell_pooled": float(np.sum(sw[use] * var_c[use]) / np.sum(sw[use])),
                  "within_over_total": float(np.sum(sw[use] * var_c[use]) / np.sum(sw[use]) / var_tot) if var_tot > 0
                  else None,
                  "n_cells_used": int(use.sum()), "frac_wtruth_in_cells_used": float(sw[use].sum() / sw.sum()),
                  "var_logw_within_cell_median_over_cells": float(np.median(var_c[use]))})
    print("FIT", json.dumps(r), flush=True)
    return r


def main():
    featd, declp, outd, nthreads = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), int(sys.argv[4])
    outd.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    decl = json.loads(declp.read_text())
    import lightgbm
    import sklearn
    res = {"schema": "mp2-s0-fit/1", "argv": sys.argv, "slurm_job": os.environ.get("SLURM_JOB_ID"),
           "host": os.uname().nodename, "python": sys.version.split()[0], "numpy": np.__version__,
           "lightgbm": lightgbm.__version__, "sklearn": sklearn.__version__, "declaration_sha256": sha256(declp),
           "code": {"mp2_s0_fit.py": sha256(Path(__file__).resolve())},
           "inputs": {k: sha256(featd / k) for k in ("s0_tune.npz", "s0_nuwro.npz")}, "fits": []}
    T, N = np.load(featd / "s0_tune.npz"), np.load(featd / "s0_nuwro.npz")
    if np.any(np.asarray(T["targetZ"]) == 1):
        raise SystemExit("hydrogen row in the Tune v1 sample")
    sets = decl["features"]
    XT = {k: np.column_stack([np.asarray(T[c], float) for c in sets[k]]) for k in ("scalars5", "full")}
    XN = {k: np.column_stack([np.asarray(N[c], float) for c in sets[k]]) for k in ("scalars5", "full")}
    wT, wN = np.asarray(T["w"], float), np.asarray(N["w"], float)
    keepN = wN > 0
    cT = fine_cell(XT["scalars5"])
    cN = fine_cell(XN["scalars5"])
    rng = np.random.default_rng(decl["fits"]["gvg_split_seed"])
    hN = rng.random(int(keepN.sum())) < 0.5
    hT = rng.random(wT.size) < 0.5
    for fs in ("scalars5", "full"):
        xn = XN[fs][keepN]
        res["fits"].append(fit_pair("tune_vs_nuwro", XT[fs], wT, xn, wN[keepN], fs, decl, nthreads, cT))
        res["fits"].append(fit_pair("nuwro_vs_nuwro_split", xn[~hN], wN[keepN][~hN], xn[hN], wN[keepN][hN], fs, decl,
                                    nthreads, cN[keepN][~hN]))
        res["fits"].append(fit_pair("tune_vs_tune_split", XT[fs][~hT], wT[~hT], XT[fs][hT], wT[hT], fs, decl,
                                    nthreads, cT[~hT]))
    by = {(f["pair"], f["features"]): f for f in res["fits"]}
    res["summary"] = {fs: {"auc_tune_vs_nuwro": by[("tune_vs_nuwro", fs)]["auc_test"],
                           "auc_nuwro_split": by[("nuwro_vs_nuwro_split", fs)]["auc_test"],
                           "auc_tune_split": by[("tune_vs_tune_split", fs)]["auc_test"],
                           "auc_gap_vs_nuwro_split": by[("tune_vs_nuwro", fs)]["auc_test"]
                           - by[("nuwro_vs_nuwro_split", fs)]["auc_test"]} for fs in ("scalars5", "full")}
    res["n_nuwro_w_zero_dropped"] = int((~keepN).sum())
    res["wall_s"] = round(time.time() - t0, 1)
    (outd / "s0_fit.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print("SUMMARY", json.dumps(res["summary"]), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
