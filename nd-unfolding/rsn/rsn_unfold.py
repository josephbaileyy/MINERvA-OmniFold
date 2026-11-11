#!/usr/bin/env python3
"""RSN unfold (RSN-DECLARATION.md §2.3-2.4): one L-5D-PV unfold through pv-ladder/pvl_unfold.py, unchanged, with a
choice of how the unmatched-event regressor is fitted.

    rsn_unfold.py --regressor-weight none|w_truth <pvl_unfold.py arguments>

none     pvl_unfold.main exactly. Used for the NC, G6 and SM steps.
w_truth  omnifold_nn_core.omnifold_loop fits its regressor (omnifold_nn_core.py:258-260) with
         sample_weight = the truth weight of the rows it is given: w_truth on the truth-passing, reco-passing MC rows,
         in the loop's own order (MCgen_weights[pass_reco] there). Used for the WR steps (referee 1.2).
         Nothing else changes: the classifiers, their weights, the seeds and the estimator parameters stay the same.
         The weight is applied by wrapping the regressor that omnifold_nn_core.make_estimators returns (the
         s5c_unfold.estimator_config rebinding, one level further in). omnifold_nn_core.py is not edited.

The product's meta gains "rsn": the regressor weight, how many fits went through the wrapper, their row count and
weight sum, and this file's sha256. With w_truth, the run refuses to write unless every iteration fitted the
regressor through the wrapper with exactly the expected rows.

MEASURES: one unfold. CANNOT AUTHORIZE: any verdict.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ND = _HERE.parent
for _p in (str(_ND / "pv-ladder"), str(_ND)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import omnifold_nn_core as onc  # noqa: E402
import pvl_lib as L  # noqa: E402
import pvl_unfold as PU  # noqa: E402
import s5n_pseudo  # noqa: E402

WEIGHTS = ("none", "w_truth")


class WrapError(RuntimeError):
    """The weighted regressor did not reach the loop as declared."""


def regressor_rows_weight(d: dict) -> np.ndarray:
    """w_truth on the rows omnifold_loop gives its regressor: truth-passing, then reco-passing, in array order."""
    m = np.asarray(d["pass_truth"], bool)
    pr = np.asarray(d["pass_reco"], bool)[m]
    w = np.asarray(d["w_truth"], float)[m][pr]
    if w.size == 0 or not np.all(np.isfinite(w)) or np.any(w <= 0):
        raise WrapError("the regressor's weights must be finite and positive on a non-empty set of rows")
    return w


def weighted(orig, evidence: dict):
    """pvl_unfold.unfold with the regressor fitted on sample_weight = regressor_rows_weight(d)."""

    def unfold(d, cols, seed, threads, iters):
        w = regressor_rows_weight(d)
        true_make = onc.make_estimators
        calls: list[int] = []

        def factory(kind, nvars, seed=None):
            if kind != "lgbm":
                raise WrapError(f"declared for the lgbm estimators only, got {kind!r}")
            clf1, clf2, reg = true_make(kind, nvars, seed=seed)
            inner = reg.fit

            def fit(X, y, *args, **kw):
                if args or kw:
                    raise WrapError("the regressor was fitted with arguments beyond (X, y)")
                if len(X) != w.size or len(y) != w.size:
                    raise WrapError(f"the regressor got {len(X)} rows, not the {w.size} reco-passing truth rows")
                calls.append(int(len(X)))
                return inner(X, y, sample_weight=w)

            reg.fit = fit
            return clf1, clf2, reg

        onc.make_estimators = factory
        try:
            out = orig(d, cols, seed, threads, iters)
        finally:
            onc.make_estimators = true_make
        if calls != [w.size] * int(iters):
            raise WrapError(f"{len(calls)} weighted regressor fits for {iters} iterations")
        evidence.update(fit_calls=len(calls), rows=int(w.size), weight_sum=float(w.sum()))
        return out

    return unfold


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], add_help=False)
    ap.add_argument("--regressor-weight", choices=WEIGHTS, required=True)
    a, rest = ap.parse_known_args(argv)
    evidence: dict = {"fit_calls": None}
    orig_unfold, orig_write = PU.unfold, s5n_pseudo.write_product

    def write(out, arrays, meta):
        if a.regressor_weight == "w_truth" and evidence.get("fit_calls") is None:
            raise WrapError("refusing to write: the weighted regressor never ran")
        rec = {"regressor_weight": a.regressor_weight, **evidence,
               "sample_weight": None if a.regressor_weight == "none" else
               "w_truth on the truth-passing, reco-passing rows (MCgen_weights[pass_reco] in omnifold_loop)",
               "code_sha256": {"rsn_unfold.py": L.sha256_path(__file__)}}
        return orig_write(out, arrays, dict(meta, rsn=rec))

    if a.regressor_weight == "w_truth":
        PU.unfold = weighted(orig_unfold, evidence)
    s5n_pseudo.write_product = write
    try:
        return PU.main(rest)
    finally:
        PU.unfold, s5n_pseudo.write_product = orig_unfold, orig_write


if __name__ == "__main__":
    sys.exit(main())
