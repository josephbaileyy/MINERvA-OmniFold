#!/usr/bin/env python
"""Classifier calibration + GBDT-vs-NN robustness for the OmniFold step-1 reweight.

Background (audit 2026-06-03, LITERATURE_NOTES.md). Every published OmniFold analysis
uses a neural-network classifier; this analysis uses LightGBM (GBDT). OmniFold's
reweighting w = p/(1-p) is only correct if the classifier output p is a calibrated
posterior probability (Practical Guide arXiv:2507.09582, T2K arXiv:2504.06857). A
referee will ask (a) is the GBDT output calibrated, and (b) does a neural network give
the same answer?

This script answers both at the step-1 reco classifier level (data vs MC reco) -- the
first and most data-driven OmniFold classification -- WITHOUT a full multi-hour unfold:

  1. Train a GBDT (LightGBM, the production estimator) and a small dense NN (sklearn
     MLPClassifier, the literature architecture) on the SAME data-vs-MC-reco problem.
  2. Reliability diagram (calibration_curve) for both on a held-out test set.
  3. Compare the implied per-event reweighting w = p/(1-p) from GBDT vs NN: if the two
     families agree, the OmniFold reweight is robust to the classifier choice.

A full NN-estimator unfold (5 iterations, all playlists) is the heavier confirmation;
see the note at the end for how to run it. Subsampled for speed; runs in ~1-2 min.

Run from repo root after `source setup_salloc_env.sh`:
  python 2d-unfolding/uq/classifier_calibration.py
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse

import numpy as np
import ROOT

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lightgbm import LGBMClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.calibration import calibration_curve
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.preprocessing import StandardScaler


def cols(tree_name, fname, branches, n, mask=None, seed=0):
    rdf = ROOT.RDataFrame(tree_name, fname)
    if mask:
        rdf = rdf.Filter(mask)
    d = rdf.AsNumpy(branches)
    X = np.column_stack([np.asarray(d[b], dtype=float) for b in branches])
    rng = np.random.default_rng(seed)
    if len(X) > n:
        X = X[rng.choice(len(X), n, replace=False)]
    return X


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--omni", default="2d-unfolding/runEventLoopOmniFold_MEFHC.root")
    ap.add_argument("--n", type=int, default=200000, help="events per class (subsample)")
    ap.add_argument("--out", default="2d-unfolding/uq/classifier_calibration.png")
    args = ap.parse_args()

    # Step-1 problem: data reco (label 1) vs MC signal reco (label 0), reco features.
    data = cols("data", args.omni, ["measured", "measured_pz"], args.n,
                mask="measured_pass")
    mc = cols("mc_signal_reco", args.omni, ["sim", "sim_pz"], args.n,
              mask="sim_pass")
    X = np.vstack([data, mc])
    y = np.concatenate([np.ones(len(data)), np.zeros(len(mc))])
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0,
                                          stratify=y)

    # GBDT (production estimator) and dense NN (literature architecture).
    gbm = LGBMClassifier(n_estimators=100, num_leaves=8, learning_rate=0.1, verbose=-1)
    gbm.fit(Xtr, ytr)
    p_gbm = gbm.predict_proba(Xte)[:, 1]

    scaler = StandardScaler().fit(Xtr)
    nn = MLPClassifier(hidden_layer_sizes=(100, 100, 100), activation="relu",
                       alpha=1e-4, batch_size=1024, learning_rate_init=1e-3,
                       early_stopping=True, n_iter_no_change=10, max_iter=200,
                       random_state=0)
    nn.fit(scaler.transform(Xtr), ytr)
    p_nn = nn.predict_proba(scaler.transform(Xte))[:, 1]

    # Metrics
    def report(tag, p):
        auc = roc_auc_score(yte, p)
        brier = brier_score_loss(yte, p)
        print(f"[{tag}] AUC={auc:.4f}  Brier={brier:.4f}")
        return auc, brier
    print("\n===== STEP-1 CLASSIFIER CALIBRATION + GBDT vs NN =====")
    print(f"subsample: {len(data)} data + {len(mc)} MC reco events, 2 reco features")
    report("GBDT (lgbm)", p_gbm)
    report("NN  (MLP)  ", p_nn)

    print(f"AUC ~ 0.5 means data and MC reco are nearly indistinguishable (the MC models")
    print(f"the data well), so the step-1 reweight w=p/(1-p) is a small correction near 1.")

    # The OmniFold-relevant quantity is the *binned density ratio* the classifier learns,
    # not the per-event weight (which at AUC~0.5 is dominated by noise). Test whether each
    # method's reweight reproduces the TRUE (pt,pz)-binned data/MC ratio. Equal subsample
    # sizes -> r_true[bin] = N_data[bin]/N_mc[bin].
    eps = 1e-6
    def w_of(p):
        p = np.clip(p, eps, 1 - eps)
        return p / (1 - p)
    # coarse-ish observable bins for stable per-bin statistics
    pt_e = np.linspace(0, 2.5, 9)
    pz_e = np.linspace(1.5, 20.0, 9)
    is_mc = yte == 0
    Xmc = Xte[is_mc]
    Hd, _, _ = np.histogram2d(Xte[yte == 1][:, 0], Xte[yte == 1][:, 1], bins=[pt_e, pz_e])
    Hm, _, _ = np.histogram2d(Xmc[:, 0], Xmc[:, 1], bins=[pt_e, pz_e])
    occ = (Hd > 50) & (Hm > 50)
    r_true = np.where(Hm > 0, Hd / np.maximum(Hm, 1), 0.0)

    def binned_pred(p):
        w = w_of(p[is_mc])
        Hw, _, _ = np.histogram2d(Xmc[:, 0], Xmc[:, 1], bins=[pt_e, pz_e], weights=w)
        return np.where(Hm > 0, Hw / np.maximum(Hm, 1), 0.0)
    r_gbm = binned_pred(p_gbm)
    r_nn = binned_pred(p_nn)

    def recov(r):
        # how well reweighted-MC matches data per bin: |r_pred - r_true|/r_true
        d = np.abs(r[occ] - r_true[occ]) / np.maximum(r_true[occ], eps)
        return 100 * np.median(d), 100 * d.max()
    g_med, g_max = recov(r_gbm)
    n_med, n_max = recov(r_nn)
    corr = np.corrcoef(r_gbm[occ], r_nn[occ])[0, 1]
    print(f"\n[binned density ratio over {int(occ.sum())} (pt,pz) bins]")
    print(f"  true data/MC ratio spread: {100*(r_true[occ].max()-r_true[occ].min()):.1f}% "
          f"(how much reweighting there is to do)")
    print(f"  GBDT recovers r_true to: median {g_med:.2f}%  max {g_max:.2f}%")
    print(f"  NN   recovers r_true to: median {n_med:.2f}%  max {n_max:.2f}%")
    print(f"  corr(r_GBDT, r_NN) across bins = {corr:.4f}  (binned, not per-event)")

    # Plot: reliability + binned reweight agreement.
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    ax = axes[0]
    for tag, p, c in [("GBDT (lgbm)", p_gbm, "C0"), ("NN (MLP)", p_nn, "C1")]:
        frac, mean = calibration_curve(yte, p, n_bins=15, strategy="quantile")
        ax.plot(mean, frac, "o-", color=c, label=tag, ms=4)
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="perfect")
    ax.set_xlabel("predicted P(data)"); ax.set_ylabel("observed fraction")
    ax.set_title("Step-1 classifier reliability"); ax.legend()

    ax = axes[1]
    ax.scatter(r_true[occ], r_gbm[occ], s=18, c="C0", label="GBDT")
    ax.scatter(r_true[occ], r_nn[occ], s=18, c="C1", marker="^", label="NN")
    lim = [0.9 * r_true[occ].min(), 1.1 * r_true[occ].max()]
    ax.plot(lim, lim, "k--", lw=1, label="truth")
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("true (pt,pz)-binned data/MC ratio")
    ax.set_ylabel("classifier-implied reweight")
    ax.set_title(f"Density-ratio recovery (corr GBDT/NN={corr:.3f})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.out, dpi=120)
    print(f"[OK] wrote {args.out}")
    print("\nFull NN-estimator unfold (heavier confirmation) requires adding an 'mlp'")
    print("backend to unbinned_unfolding/python/omnifold.py and running via sbatch;")
    print("this classifier-level check is the cheap first-order robustness test.")


if __name__ == "__main__":
    main()
