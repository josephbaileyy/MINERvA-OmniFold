"""Synthetic check: where the GBDT seed acts in the two 2D backends (no MINERvA data, no training on products).

Settings are the production ones in unbinned_unfolding/python/omnifold.py: LightGBM
(n_estimators=100, num_leaves=8, learning_rate=0.1, verbose=-1) and sklearn exact
GradientBoostingClassifier with library defaults. The data imitate an OmniFold step-1 problem:
two continuous features, two weighted classes with a smooth density ratio.

Usage (scratch venv with lightgbm 4.6.0 and scikit-learn):
    OMP_NUM_THREADS=2 python seed_mechanism_check.py --out seed_mechanism_check.json
Exit status 0 when every check ran; the JSON records each observed outcome.
"""
import argparse
import json
import os
import tempfile

import numpy as np

LGBM = dict(n_estimators=100, num_leaves=8, learning_rate=0.1, verbose=-1)


def step1_problem(n, rng):
    """Two-class weighted sample: class 0 ~ N(0, 1)^2, class 1 ~ N(0.15, 1.1)^2."""
    x0 = rng.normal(0.0, 1.0, size=(n, 2))
    x1 = rng.normal(0.15, 1.1, size=(n, 2))
    x = np.concatenate([x0, x1])
    y = np.concatenate([np.zeros(n), np.ones(n)])
    w = np.concatenate([rng.gamma(4.0, 0.25, n), np.ones(n)])
    return x, y, w


def lgbm_predict(x, y, w, seed, threads, extra=None):
    from lightgbm import LGBMClassifier

    clf = LGBMClassifier(**LGBM, random_state=seed, n_jobs=threads, **(extra or {}))
    clf.fit(x, y, sample_weight=w)
    return clf.predict_proba(x)[:, 1]


def bin_mappers(x, w, seed):
    """Text of the constructed Dataset's bin mappers (the part before the per-row data)."""
    import lightgbm as lgb

    ds = lgb.Dataset(x, label=np.zeros(len(x)), weight=w,
                     params={"seed": seed, "verbose": -1}, free_raw_data=False).construct()
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "ds.txt")
        ds._dump_text(p)
        with open(p) as f:
            text = f.read()
    head = []
    for line in text.splitlines():
        if line.startswith("weights") or line.startswith("query"):
            break
        head.append(line)
    return "\n".join(head)


def maxdiff(a, b):
    return float(np.max(np.abs(a - b)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rng = np.random.default_rng(20261009)
    res = {}

    # L1: rows above the default bin_construct_sample_cnt (200,000): does the seed change the model?
    x, y, w = step1_problem(200_000, rng)  # 400,000 rows in total
    p1 = lgbm_predict(x, y, w, seed=1, threads=2)
    p2 = lgbm_predict(x, y, w, seed=2, threads=2)
    res["L1_rows_400k_seed1_vs_seed2_max_abs_dprob"] = maxdiff(p1, p2)

    # L2: same rows, bin construction from every row: does the seed still matter?
    q1 = lgbm_predict(x, y, w, seed=1, threads=2, extra={"subsample_for_bin": len(x)})
    q2 = lgbm_predict(x, y, w, seed=2, threads=2, extra={"subsample_for_bin": len(x)})
    res["L2_rows_400k_allrow_binning_seed1_vs_seed2_max_abs_dprob"] = maxdiff(q1, q2)

    # L3: fewer rows than the bin sample: does the seed matter?
    xs, ys, ws = step1_problem(60_000, rng)  # 120,000 rows
    r1 = lgbm_predict(xs, ys, ws, seed=1, threads=2)
    r2 = lgbm_predict(xs, ys, ws, seed=2, threads=2)
    res["L3_rows_120k_seed1_vs_seed2_max_abs_dprob"] = maxdiff(r1, r2)

    # L4: fixed seed, Poisson(1)-resampled weights (a bootstrap replica): are the bin mappers the same?
    wb = w * rng.poisson(1.0, size=len(w))
    res["L4_fixed_seed_bootstrap_weights_same_bin_mappers"] = bin_mappers(x, w, 1) == bin_mappers(x, wb, 1)
    res["L4_control_seed1_vs_seed2_same_bin_mappers"] = bin_mappers(x, w, 1) == bin_mappers(x, w, 2)

    # L5: thread count at a fixed seed: bitwise equal?
    t1 = lgbm_predict(x, y, w, seed=1, threads=1)
    res["L5_seed1_threads1_vs_threads2_max_abs_dprob"] = maxdiff(t1, p1)

    # L6: rerun at identical arguments: bitwise equal?
    p1b = lgbm_predict(x, y, w, seed=1, threads=2)
    res["L6_rerun_identical_args_max_abs_dprob"] = maxdiff(p1, p1b)

    # X1: sklearn exact GBT, library defaults: does random_state change the model?
    from sklearn.ensemble import GradientBoostingClassifier

    xe, ye, we = step1_problem(20_000, rng)
    e = []
    for seed in (1, 2, None):
        clf = GradientBoostingClassifier(random_state=seed)
        clf.fit(xe, ye, sample_weight=we)
        e.append(clf.predict_proba(xe)[:, 1])
    res["X1_exact_seed1_vs_seed2_max_abs_dprob"] = maxdiff(e[0], e[1])
    res["X1_exact_seed1_vs_None_max_abs_dprob"] = maxdiff(e[0], e[2])

    # X2: same with tied feature values (rounded features) to expose tie-breaking randomness.
    xr = np.round(xe, 1)
    f = []
    for seed in (1, 2):
        clf = GradientBoostingClassifier(random_state=seed)
        clf.fit(xr, ye, sample_weight=we)
        f.append(clf.predict_proba(xr)[:, 1])
    res["X2_exact_rounded_features_seed1_vs_seed2_max_abs_dprob"] = maxdiff(f[0], f[1])

    import lightgbm
    import sklearn

    res["versions"] = {"lightgbm": lightgbm.__version__, "sklearn": sklearn.__version__,
                       "numpy": np.__version__}
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(res, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
