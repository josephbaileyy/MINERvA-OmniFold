"""S1 seed-null diagnosis D1 and D2 (director, 2026-10-25). Login node, synthetic data only, no cross-section values.

D1: build the B0 estimators (s5c_unfold.estimator_config over omnifold_nn_core.make_estimators, config
"deterministic", as s5p_numerics.unfold_one -> s5c_unfold.unfold does) and the refinement classifier
(s5n_pseudo.refine_params after s5e_candidate.install("R"), as s5p_numerics.main installs it, ->
unfold_2d_omnifold_unbinned._make_bkg_classifier, as s5n_pseudo.refine does) for
seeds 42 and 45 from the deploy that ran S1, fit each on a tiny synthetic set, and dump LightGBM's effective
parameters from the trained model string.

D2: on a synthetic two-class set, the same factories give identical predictions for seeds 42 and 45 under the
production settings, and different ones with one stochastic setting on (subsample 0.8, subsample_freq 1) and with
LightGBM's default bin sampling (bin_construct_sample_cnt 200000) on more rows than that.
    python3 -I -B diag_seed.py <deploy>
"""
import json
import sys
from pathlib import Path

import numpy as np

D = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(D / "nd-unfolding"))
import omnifold_nn_core as onc  # noqa: E402
import s5c_unfold  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5e_candidate  # noqa: E402

print("s5e_candidate.install('R') override:", s5e_candidate.install("R"))  # as s5p_numerics.main does

THREADS = 8
KEYS = ("seed", "data_random_seed", "bagging_seed", "feature_fraction_seed", "extra_seed", "drop_seed",
        "objective_seed", "deterministic", "bin_construct_sample_cnt", "bagging_fraction", "bagging_freq",
        "pos_bagging_fraction", "neg_bagging_fraction", "feature_fraction", "feature_fraction_bynode",
        "extra_trees", "force_row_wise", "num_threads", "num_iterations", "num_leaves")
print("module files:", {m.__name__: m.__file__ for m in (onc, s5c_unfold, s5n_pseudo)})
import lightgbm  # noqa: E402
print("lightgbm", lightgbm.__version__)


def b0(seed, extra):
    rec = []
    with s5c_unfold.estimator_config(extra, rec):
        ests = onc.make_estimators("lgbm", 5, seed=seed)
    return ests, rec


def refinement(seed, override=None):
    u2d = s5n_pseudo.load_u2d()
    params = dict(s5n_pseudo.refine_params(seed, THREADS), **(override or {}))
    return u2d._make_bkg_classifier("lgbm", params, "cpu"), params


def effective(clf):
    text = clf.booster_.model_to_string()
    block = text[text.index("parameters:"):text.index("end of parameters")]
    out = {}
    for line in block.splitlines():
        if line.startswith("[") and ": " in line:
            k, v = line[1:-1].split(": ", 1)
            if k in KEYS:
                out[k] = v
    return out


rng = np.random.default_rng(7)


def dataset(n):
    x = rng.normal(size=(n, 5))
    y = (x[:, 0] + 0.5 * x[:, 1] ** 2 + rng.normal(scale=1.0, size=n) > 0.5).astype(int)
    return x, y


x_small, y_small = dataset(4000)
extra = s5c_unfold.config_params("deterministic", THREADS)
print("D1 config_params('deterministic') =", extra)
for seed in (42, 45):
    ests, rec = b0(seed, extra)
    clf = ests[0]
    clf.fit(x_small, y_small)
    print(f"D1 B0 clf1 seed {seed}: get_params", {k: rec[0][0].get(k) for k in ("random_state", "subsample", "subsample_freq", "colsample_bytree", "deterministic", "bin_construct_sample_cnt", "force_row_wise", "num_threads")})
    print(f"D1 B0 clf1 seed {seed}: effective", effective(clf))
    rclf, params = refinement(seed)
    rclf.fit(x_small, y_small)
    print(f"D1 refinement seed {seed}: params", {k: params.get(k) for k in ("random_state", "deterministic", "bin_construct_sample_cnt", "force_row_wise", "num_threads")})
    print(f"D1 refinement seed {seed}: effective", effective(rclf))

x_big, y_big = dataset(400_000)
x_eval, _ = dataset(20_000)


def pred_b0(seed, ex):
    ests, _ = b0(seed, ex)
    clf = ests[0]
    clf.fit(x_big, y_big)
    return clf.predict_proba(x_eval)[:, 1]


def pred_ref(seed, override):
    rclf, _ = refinement(seed, override)
    rclf.fit(x_big, y_big)
    return rclf.predict_proba(x_eval)[:, 1]


cases = [
    ("B0 production deterministic (as S1)", lambda s: pred_b0(s, extra)),
    ("B0 deterministic + subsample 0.8, subsample_freq 1", lambda s: pred_b0(s, dict(extra, subsample=0.8, subsample_freq=1))),
    ("B0 deterministic but bin_construct_sample_cnt default 200000 (400000 rows)", lambda s: pred_b0(s, {k: v for k, v in extra.items() if k != "bin_construct_sample_cnt"})),
    ("refinement production (as S1)", lambda s: pred_ref(s, None)),
    ("refinement + subsample 0.8, subsample_freq 1", lambda s: pred_ref(s, {"subsample": 0.8, "subsample_freq": 1})),
    ("refinement with bin_construct_sample_cnt 200000 (400000 rows)", lambda s: pred_ref(s, {"bin_construct_sample_cnt": 200000})),
]
for name, f in cases:
    p42, p45 = f(42), f(45)
    print(json.dumps({"D2": name, "seeds": [42, 45], "bitwise_equal": bool(np.array_equal(p42, p45)),
                      "max_abs_diff_synthetic_prob": float(np.max(np.abs(p42 - p45)))}))
