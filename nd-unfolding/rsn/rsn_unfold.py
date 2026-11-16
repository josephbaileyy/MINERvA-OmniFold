#!/usr/bin/env python3
"""RSN unfold (RSN-DECLARATION.md §2.3-2.6): one L-5D-PV unfold through pv-ladder/pvl_unfold.py, unchanged, with a
choice of how the unmatched-event regressor is fitted, an optional declared closure truth, and an optional transfer
diagnostic beside the loop.

    rsn_unfold.py --regressor-weight none|w_push_w_truth [--truth ratio|a7_gibuu|q3] [--transfer] <pvl_unfold.py args>

--regressor-weight
  none            pvl_unfold.main exactly: the NC, G6, SM, TR and WU steps.
  w_push_w_truth  omnifold_nn_core.omnifold_loop fits its regressor (omnifold_nn_core.py:258-260) with
                  sample_weight = w_push x w_truth on the rows it is given, the truth-passing, reco-passing MC rows in
                  the loop's own order. This is the population the loop reweights at that iteration, the same weight
                  as T3's MW arm (tier3/t3p_arms.py:15-16). w_push is the loop's own value: the output of
                  omnifold_nn_core._reweight for the loop's second classifier (ones before the first iteration). The
                  WR steps (referee 1.2 and F1.1) use it.
--truth (closures only, with the identity reweight tune_v1.json)
  ratio     the pvl-ratio/1 file's reweight, as pvl_unfold.py.
  a7_gibuu  F0b's A7 GiBUU hybrid truth: s5p_truths.hypothesis_weight with the committed null-gibuu_cv-F.json
            (sha256 pinned) at amplitude 1.
  q3        F0b's synthetic q3 tilt: s5c_pseudo.truth_weight("q3_given_eavail_w", amplitude 0.3).
--transfer  F1.2(ii): at every iteration, before the loop's own regressor fit, a separate regressor with the same class
            and parameters is fitted on the rows a seeded mask leaves (fraction TRANSFER_FRACTION masked, seed
            [TRANSFER_SEED, iteration]), with the step's own sample weight, and it predicts the masked rows. Their known
            step-1 weight is compared with the prediction, overall, per reporting cell and per decile of the fine
            truth cell's acceptance. The loop's own fits, arrays and estimators are untouched.

The product's meta gains "rsn": the options, the fit count, the weight sums, the transfer records and this file's
sha256. The run refuses to write unless every iteration fitted the regressor through the wrapper with exactly the
expected rows.

MEASURES: one unfold. CANNOT AUTHORIZE: any verdict.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ND = _HERE.parent
_ROOT = _ND.parent
for _p in (str(_ND / "pv-ladder"), str(_ND)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import omnifold_nn_core as onc  # noqa: E402
import pvl_lib as L  # noqa: E402
import pvl_unfold as PU  # noqa: E402
import s2_h2_scope as S2  # noqa: E402
import s5c_pseudo  # noqa: E402
import s5c_unfold  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_truths  # noqa: E402

WEIGHTS = ("none", "w_push_w_truth")
TRUTHS = ("ratio", "a7_gibuu", "q3")
A7_HYPOTHESIS = _ROOT / "docs/orchestration/state/s5p/ratios/nullsF/null-gibuu_cv-F.json"
A7_HYPOTHESIS_SHA256 = "0080495c911143be29bbd780063a85b2890cd30d10c1e5b29f1f5cdb71013a77"
Q3_AMPLITUDE = 0.3
DEFINITION = _ND / "pv-ladder/readouts/h2_definition.json"
DEFINITION_SHA256 = "b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89"
TRANSFER_SEED, TRANSFER_FRACTION = 20261111, 0.2
N_DECILES = 10


class WrapError(RuntimeError):
    """The instrumented regressor did not reach the loop as declared."""


def regressor_rows(d: dict) -> tuple[np.ndarray, np.ndarray, int]:
    """(pass_reco among the truth-passing rows, w_truth on the regressor's rows, the truth-passing count)."""
    m = np.asarray(d["pass_truth"], bool)
    pr = np.asarray(d["pass_reco"], bool)[m]
    w = np.asarray(d["w_truth"], float)[m][pr]
    if w.size == 0 or not np.all(np.isfinite(w)) or np.any(w <= 0):
        raise WrapError("the regressor's weights must be finite and positive on a non-empty set of rows")
    return pr, w, int(m.sum())


def reporting_map() -> np.ndarray:
    if L.sha256_path(DEFINITION) != DEFINITION_SHA256:
        raise WrapError("the H2 definition is not the approved one")
    cell, _ = S2.h2_of_fine()
    return np.asarray(json.loads(DEFINITION.read_text())["h2_to_reporting_cell"])[cell]


def transfer_context(d: dict, rmap: np.ndarray) -> dict:
    """Per regressor row: its reporting cell and its fine truth cell's acceptance (w_truth share that is reconstructed)."""
    m = np.asarray(d["pass_truth"], bool)
    gen = np.asarray(d["MCgen"], float)[m]
    wt = np.asarray(d["w_truth"], float)[m]
    pr = np.asarray(d["pass_reco"], bool)[m]
    f = L.flat_index(gen, L.AXES5)
    ok = f >= 0
    n = int(np.prod([len(L.FINE[a]) - 1 for a in L.AXES5]))
    den = np.bincount(f[ok], weights=wt[ok], minlength=n)
    num = np.bincount(f[ok & pr], weights=wt[ok & pr], minlength=n)
    acc = np.where(den > 0, num / np.where(den > 0, den, 1.0), np.nan)
    frow = f[pr]
    return {"cell": np.where(frow >= 0, rmap[np.maximum(frow, 0)], -1), "acc": np.where(frow >= 0, acc[np.maximum(frow, 0)], np.nan)}


def mask_of(n: int, k: int) -> np.ndarray:
    return np.random.default_rng([TRANSFER_SEED, k]).random(n) < TRANSFER_FRACTION


def summarize(pred, y, w, cell, acc, k: int) -> dict:
    """The transfer record of iteration k on the masked rows: prediction against the known step-1 weight."""
    pred, y, w = (np.asarray(a, float) for a in (pred, y, w))
    d = pred - y
    sy = float((w * y).sum())
    out = {"iteration": k, "n_masked": int(y.size), "rel_bias": float((w * d).sum() / sy),
           "rel_rms": float(np.sqrt((w * d * d).sum() / w.sum()) / (sy / w.sum()))}
    cb = []
    for c in range(16):
        s = cell == c
        den = float((w[s] * y[s]).sum())
        cb.append(float((w[s] * pred[s]).sum() / den - 1.0) if den > 0 else None)
    out["cell_bias"] = cb
    ok = np.isfinite(acc)
    edges = np.quantile(acc[ok], np.linspace(0, 1, N_DECILES + 1)) if ok.any() else np.zeros(N_DECILES + 1)
    b = np.clip(np.searchsorted(edges, acc[ok], side="right") - 1, 0, N_DECILES - 1)
    dec = []
    for i in range(N_DECILES):
        s = b == i
        den = float((w[ok][s] * y[ok][s]).sum())
        dec.append(float((w[ok][s] * d[ok][s]).sum() / den) if den > 0 else None)
    out["acceptance_edges"], out["acceptance_decile_rel_bias"] = edges.tolist(), dec
    return out


def instrument(orig, evidence: dict, weighted: bool, transfer: bool):
    """pvl_unfold.unfold with the regressor's fit routed through the wrapper (and, if declared, weighted and the
    transfer diagnostic run beside it)."""

    def unfold(d, cols, seed, threads, iters):
        if transfer and cols is not None:
            raise WrapError("the transfer diagnostic is declared on the five truth features only")
        pr, wt, n = regressor_rows(d)
        ctx = transfer_context(d, reporting_map()) if transfer else None
        true_make, true_rw = onc.make_estimators, onc._reweight
        st = {"push": np.ones(n), "clf2": None}
        calls: list[int] = []
        sums: list[float] = []
        diag: list[dict] = []

        def rw(events, clf):
            out = true_rw(events, clf)
            if clf is st["clf2"]:
                if len(out) != n:
                    raise WrapError("the second classifier's output is not on the truth-passing rows")
                st["push"] = out
            return out

        def factory(kind, nvars, seed=None):
            if kind != "lgbm":
                raise WrapError(f"declared for the lgbm estimators only, got {kind!r}")
            clf1, clf2, reg = true_make(kind, nvars, seed=seed)
            st["clf2"] = clf2
            inner = reg.fit

            def fit(X, y, *args, **kw):
                if args or kw:
                    raise WrapError("the regressor was fitted with arguments beyond (X, y)")
                if len(X) != wt.size or len(y) != wt.size:
                    raise WrapError(f"the regressor got {len(X)} rows, not the {wt.size} reco-passing truth rows")
                sw = wt * np.asarray(st["push"], float)[pr] if weighted else None
                if ctx is not None:
                    k = len(calls)
                    mk = mask_of(len(y), k)
                    probe = type(reg)(**reg.get_params())
                    X_, y_ = np.asarray(X), np.asarray(y)
                    if sw is None:
                        probe.fit(X_[~mk], y_[~mk])
                    else:
                        probe.fit(X_[~mk], y_[~mk], sample_weight=sw[~mk])
                    diag.append(summarize(probe.predict(X_[mk]), y_[mk], wt[mk], ctx["cell"][mk], ctx["acc"][mk], k))
                calls.append(int(len(X)))
                if sw is None:
                    return inner(X, y)
                sums.append(float(sw.sum()))
                return inner(X, y, sample_weight=sw)

            reg.fit = fit
            return clf1, clf2, reg

        onc.make_estimators, onc._reweight = factory, rw
        try:
            out = orig(d, cols, seed, threads, iters)
        finally:
            onc.make_estimators, onc._reweight = true_make, true_rw
        if calls != [wt.size] * int(iters):
            raise WrapError(f"{len(calls)} instrumented regressor fits for {iters} iterations")
        evidence.update(fit_calls=len(calls), rows=int(wt.size), weight_sums=sums if weighted else None)
        if transfer:
            evidence["transfer_records"] = diag
        return out

    return unfold


def truth_rows(truth: str, inputs: dict) -> np.ndarray:
    gen, edges, w = inputs["MCgen"], inputs["edges"], np.asarray(inputs["w_truth"], float)
    if truth == "q3":
        return s5c_pseudo.truth_weight("q3_given_eavail_w", gen, edges, Q3_AMPLITUDE, w_truth=w)
    if L.sha256_path(A7_HYPOTHESIS) != A7_HYPOTHESIS_SHA256:
        raise WrapError("the A7 GiBUU hypothesis is not the pinned one")
    return s5p_truths.hypothesis_weight(gen, edges, w, json.loads(A7_HYPOTHESIS.read_text()), 1.0)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], add_help=False)
    ap.add_argument("--regressor-weight", choices=WEIGHTS, required=True)
    ap.add_argument("--truth", choices=TRUTHS, default="ratio")
    ap.add_argument("--transfer", action="store_true")
    a, rest = ap.parse_known_args(argv)
    if a.truth != "ratio" and "--closure" not in rest:
        raise WrapError("a declared truth is for a closure only")
    evidence: dict = {"fit_calls": None}
    seen: dict = {}
    orig = (PU.unfold, s5n_pseudo.write_product, L.row_weight, s5c_unfold.load_inputs)

    def load_inputs(path):
        seen["inputs"] = orig[3](path)
        return seen["inputs"]

    def row_weight(gen, names, ratio, pass_truth):
        r = orig[2](gen, names, ratio, pass_truth)
        if not ratio.get("identity") or not np.all(r == 1.0):
            raise WrapError("a declared truth replaces the identity reweight only")
        t = np.asarray(truth_rows(a.truth, seen["inputs"]), float)
        if t.shape != r.shape or not np.all(np.isfinite(t)) or np.any(t < 0):
            raise WrapError("the declared truth's reweight is not one finite, non-negative value per row")
        evidence["truth_weight_mean"] = float(t.mean())
        return t

    def write(out, arrays, meta):
        if (a.regressor_weight != "none" or a.transfer) and evidence.get("fit_calls") is None:
            raise WrapError("refusing to write: the instrumented regressor never ran")
        rec = {"regressor_weight": a.regressor_weight, "truth": a.truth, "transfer": a.transfer, **evidence,
               "sample_weight": None if a.regressor_weight == "none" else
               "w_push x w_truth on the truth-passing, reco-passing rows (T3's MW population)",
               "code_sha256": {"rsn_unfold.py": L.sha256_path(__file__)}}
        if a.truth == "a7_gibuu":
            rec["a7_hypothesis_sha256"] = A7_HYPOTHESIS_SHA256
        return orig[1](out, arrays, dict(meta, rsn=rec))

    if a.regressor_weight != "none" or a.transfer:
        PU.unfold = instrument(orig[0], evidence, a.regressor_weight == "w_push_w_truth", a.transfer)
    if a.truth != "ratio":
        L.row_weight, s5c_unfold.load_inputs = row_weight, load_inputs
    s5n_pseudo.write_product = write
    try:
        return PU.main(rest)
    finally:
        PU.unfold, s5n_pseudo.write_product, L.row_weight, s5c_unfold.load_inputs = orig


if __name__ == "__main__":
    sys.exit(main())
