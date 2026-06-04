#!/usr/bin/env python3
"""Unbinned goodness-of-fit for OmniFold via a Classifier Two-Sample Test (C2ST).

Pre-publication methodology item #3 (LITERATURE_NOTES.md sec C; memory
prepub-methodology-items). Binned chi2 throws away the unbinned information OmniFold
is built on; this is the natural unbinned GoF.

Idea (Lopez-Paz & Oquab 2016, arXiv:1610.06545). After OmniFold converges, the
reco-folded reweighted MC must be indistinguishable from data in the FULL unbinned
reco feature space. Train a classifier to separate
    A = data reco            (weights = measured purity weights), label 1
    B = MC reco, reweighted   (weights = w_pull * w_reco),         label 0
on a train split and measure its accuracy on a held-out test split. Under H0 (the two
samples are drawn from the same density) the held-out accuracy -> 0.5 with standard
deviation sqrt(0.25 / n_eff_test); the z-score / two-sided p-value is the GoF. AUC is
reported alongside as a scale-free companion.

The PRIOR (CV, no reweighting: w_pull == 1) is run as the sensitivity baseline -- a
useful GoF must see the data/MC mismatch BEFORE unfolding shrink toward 0.5 AFTER it.

ROOT-free: consumes the of_inputs_*.npz dumped by nn_dump_inputs.py and the validated
omnifold_loop from omnifold_nn_core.py. Run in either env (lgbm default needs no TF):
  python unbinned_gof.py --inputs of_inputs_3d.npz --iters 5
  python unbinned_gof.py --inputs of_inputs_3d.npz --weights-npz of_weights_3d.npz
"""
import argparse
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
if f"{_REPO}/nd-unfolding" not in sys.path:
    sys.path.insert(0, f"{_REPO}/nd-unfolding")
import omnifold_nn_core as onc  # noqa: E402


def _norm_weights(w):
    s = float(np.sum(w))
    return w / s if s > 0 else w


def c2st(featA, wA, featB, wB, seed=0, max_per_class=400_000, n_estimators=200):
    """Classifier two-sample test between weighted samples A and B.

    Returns dict with test accuracy, AUC, the H0 std, z-score and two-sided p-value.
    Each class is normalized to unit total weight so a perfect match -> 0.5 accuracy
    irrespective of the raw sample sizes.
    """
    from lightgbm import LGBMClassifier
    from sklearn.metrics import roc_auc_score
    from scipy import stats

    rng = np.random.default_rng(seed)

    def _sub(feat, w):
        if len(feat) > max_per_class:
            idx = rng.choice(len(feat), size=max_per_class, replace=False)
            return feat[idx], w[idx]
        return feat, w

    featA, wA = _sub(featA, wA)
    featB, wB = _sub(featB, wB)
    wA = _norm_weights(np.asarray(wA, float))
    wB = _norm_weights(np.asarray(wB, float))

    X = np.vstack([featA, featB])
    y = np.concatenate([np.ones(len(featA)), np.zeros(len(featB))])
    w = np.concatenate([wA, wB])

    n = len(y)
    perm = rng.permutation(n)
    X, y, w = X[perm], y[perm], w[perm]
    cut = n // 2
    Xtr, ytr, wtr = X[:cut], y[:cut], w[:cut]
    Xte, yte, wte = X[cut:], y[cut:], w[cut:]

    clf = LGBMClassifier(n_estimators=n_estimators, num_leaves=63, learning_rate=0.05,
                         subsample=0.8, colsample_bytree=0.8, random_state=seed,
                         n_jobs=-1, verbosity=-1)
    clf.fit(Xtr, ytr, sample_weight=wtr)
    p = clf.predict_proba(Xte)[:, 1]
    pred = (p >= 0.5).astype(float)

    # weighted test accuracy (each class already unit-normalized over the full set,
    # so re-normalize within the test split for an unbiased 0.5-centered statistic)
    acc = float(np.sum(wte * (pred == yte)) / np.sum(wte))
    auc = float(roc_auc_score(yte, p, sample_weight=wte))

    # effective test sample size for the H0 spread of a proportion
    n_eff = (np.sum(wte) ** 2) / np.sum(wte ** 2)
    std0 = np.sqrt(0.25 / n_eff)
    z = (acc - 0.5) / std0
    pval = float(2.0 * stats.norm.sf(abs(z)))
    return {"acc": acc, "auc": auc, "std0": float(std0), "n_eff": float(n_eff),
            "z": float(z), "pval": pval}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", default="of_inputs_3d.npz")
    ap.add_argument("--weights-npz", default="",
                    help="npz with w_pull (skip re-running OmniFold). Else run the loop.")
    ap.add_argument("--kind", default="lgbm")
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--max-per-class", type=int, default=400_000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--save-weights", default="",
                    help="if set and the loop is run, save w_pull/w_push here.")
    args = ap.parse_args()

    d = np.load(args.inputs, allow_pickle=True)
    MCgen = d["MCgen"]; MCreco = d["MCreco"]; measured = d["measured"]
    pass_reco = d["pass_reco"]; pass_truth = d["pass_truth"]
    w_reco = d["w_reco"]; w_truth = d["w_truth"]
    measured_weights = d["measured_weights"]
    meas_pass_reco = np.ones(len(measured), dtype=bool)  # measured already reco-passing

    # converged truth-level weights
    if args.weights_npz:
        wd = np.load(args.weights_npz)
        w_pull = wd["w_pull"]
        print(f"[gof] loaded w_pull from {args.weights_npz}")
    else:
        print(f"[gof] running OmniFold loop (kind={args.kind}, iters={args.iters}) "
              f"to get converged weights...")
        w_pull, w_push = onc.omnifold_loop(
            MCgen, MCreco, measured, pass_reco, pass_truth, meas_pass_reco,
            num_iterations=args.iters, kind=args.kind,
            MCgen_weights=w_truth, MCreco_weights=w_reco,
            measured_weights=measured_weights, seed=args.seed, verbose=True)
        if args.save_weights:
            np.savez(args.save_weights, w_pull=w_pull, w_push=w_push)
            print(f"[gof] saved weights -> {args.save_weights}")

    # Build the two reco-level samples. The loop works in the pass_truth subset, so
    # w_pull aligns with MC[pass_truth]; pick the reco-passing events there.
    pr_sub = pass_reco[pass_truth]
    mcreco_sub = MCreco[pass_truth][pr_sub]
    wreco_sub = w_reco[pass_truth][pr_sub]
    wB_unfold = w_pull[pr_sub] * wreco_sub          # OmniFold-reweighted MC reco
    wB_prior = np.ones_like(w_pull)[pr_sub] * wreco_sub  # CV prior (no reweight)

    A = measured[meas_pass_reco]
    wA = measured_weights[meas_pass_reco]

    print(f"[gof] data reco n={len(A)} (sum w={wA.sum():.3e}); "
          f"MC reco n={len(mcreco_sub)} (sum w_unfold={wB_unfold.sum():.3e})")

    prior = c2st(A, wA, mcreco_sub, wB_prior, seed=args.seed,
                 max_per_class=args.max_per_class)
    unfold = c2st(A, wA, mcreco_sub, wB_unfold, seed=args.seed,
                  max_per_class=args.max_per_class)

    def _line(tag, r):
        return (f"  {tag:9s} acc={r['acc']:.4f}  AUC={r['auc']:.4f}  "
                f"(H0: 0.5 +/- {r['std0']:.4f}, n_eff={r['n_eff']:.3e})  "
                f"z={r['z']:.2f}  p={r['pval']:.2e}")

    print("\n===== Unbinned GoF (Classifier Two-Sample Test, reco space) =====")
    print(_line("PRIOR/CV", prior))
    print(_line("UNFOLDED", unfold))
    verdict = ("PASS" if unfold["acc"] < prior["acc"] and unfold["pval"] > 1e-3
               else "INSPECT")
    print(f"\n  Interpretation: unfolding should pull accuracy/AUC toward 0.5 "
          f"(data<->MC indistinguishable).")
    print(f"  prior acc {prior['acc']:.4f} -> unfolded {unfold['acc']:.4f}; "
          f"VERDICT: {verdict}")
    print(f"  (acc near 0.5 with p>~1e-3 = no detectable unbinned mismatch; a large z "
          f"flags residual structure OmniFold did not capture.)")


if __name__ == "__main__":
    main()
