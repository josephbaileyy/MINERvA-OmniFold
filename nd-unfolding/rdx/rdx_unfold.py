#!/usr/bin/env python3
"""RDX unfold (RDX-DECLARATION.md rev 3 §2 C3, §4): one L-5D-PV unfold through pv-ladder/pvl_unfold.py, unchanged,
with the misses regressor optionally given the five truthx columns of the RDX sidecar, optionally permuted, weighted
or probed by a held-out transfer fit. RSN's bound rsn_unfold.py is imported for its helpers, never edited.

    rdx_unfold.py --regressor-features std|wide [--truthx-sidecar S --expect-truthx-sha256 H] [--truthx-permute SEED]
                  [--regressor-weight none|w_push_w_truth] [--truth ratio|a7_gibuu|q3] [--transfer] <pvl_unfold.py args>

--regressor-features
  std   the five standard truth features, as pvl_unfold. With no other option this is pvl_unfold.main exactly (X0,
        X0_lat, X0c, X0g, X0q).
  wide  the regressor's rows gain the sidecar's five truthx columns (E_nu, the true vertex, the leading-proton KE),
        at fit and at predict, aligned to the loop's own rows: omnifold_nn_core.omnifold_loop fits on
        MCgen[pass_truth][pass_reco] and predicts on MCgen[pass_truth][~pass_reco] (omnifold_nn_core.py:210-211,
        258-260). The classifiers never see truthx.
--truthx-permute SEED  wide only: the five truthx columns are permuted jointly across all MCgen rows, once, by
        numpy.random.default_rng(SEED).permutation(n), before the loop (the refit nulls X1p, X1pc, X1p2).
--regressor-weight, --truth  as RSN rev 3 (rsn_unfold.py).
--transfer  as RSN's, with RDX's mask default_rng([20261112, k]).random(n) < 0.2 (X1t, X0t).

The sidecar must name the --npz file's sha256 and have exactly one row per MCgen row. The product's meta gains "rdx":
the options, the fit and predict counts, the sidecar's sha256, the permutation seed and this file's sha256. The run
refuses to write unless every iteration fitted and predicted the regressor through the wrapper on exactly the
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
for _p in (str(_ND / "rsn"), str(_ND / "pv-ladder"), str(_ND)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import omnifold_nn_core as onc  # noqa: E402
import pvl_lib as L  # noqa: E402
import pvl_unfold as PU  # noqa: E402
import rsn_unfold as RSN  # noqa: E402
import s5c_unfold  # noqa: E402
import s5n_pseudo  # noqa: E402

FEATURES = ("std", "wide")
TRUTHX_NAMES = ("truthx_enu", "truthx_vtx_x", "truthx_vtx_y", "truthx_vtx_z", "truthx_kep_lead")
TRANSFER_SEED, TRANSFER_FRACTION = 20261112, RSN.TRANSFER_FRACTION
SIDECAR_SCHEMA = "rdx-truthx-sidecar/1"


class RdxError(RuntimeError):
    """The RDX regressor did not reach the loop as declared."""


def mask_of(n: int, k: int) -> np.ndarray:
    return np.random.default_rng([TRANSFER_SEED, k]).random(n) < TRANSFER_FRACTION


def load_sidecar(path: Path, expect_sha: str, npz: Path) -> tuple[np.ndarray, dict]:
    """The sidecar's truthx (one float64 row per MCgen row) after its own and its npz's sha256 checks."""
    if L.sha256_path(path) != expect_sha:
        raise RdxError(f"the truthx sidecar {path} is not sha256 {expect_sha}")
    with np.load(path, allow_pickle=False) as z:
        meta = json.loads(str(z["meta"]))
        tx = np.asarray(z["truthx"])
        names = tuple(str(x) for x in z["truthx_names"])
    if meta.get("schema") != SIDECAR_SCHEMA:
        raise RdxError(f"the sidecar's schema is {meta.get('schema')!r}, not {SIDECAR_SCHEMA}")
    if meta.get("npz_sha256") != L.sha256_path(npz):
        raise RdxError("the sidecar does not belong to this --npz (its npz_sha256 differs)")
    if names != TRUTHX_NAMES:
        raise RdxError(f"the sidecar's columns are {names}, not {TRUTHX_NAMES}")
    if tx.dtype != np.float64 or tx.ndim != 2 or tx.shape[1] != len(TRUTHX_NAMES) or not np.all(np.isfinite(tx)):
        raise RdxError("truthx must be a finite float64 array with five columns")
    return tx, meta


def permuted(tx: np.ndarray, seed: int) -> np.ndarray:
    """The five columns permuted jointly across rows, once."""
    return tx[np.random.default_rng(seed).permutation(len(tx))]


def instrument(orig, evidence: dict, weighted: bool, transfer: bool, tx: np.ndarray | None):
    """pvl_unfold.unfold with the regressor's fit and predict routed through the wrapper: weighted, widened by tx,
    and probed by the transfer fit, as declared."""

    def unfold(d, cols, seed, threads, iters):
        if cols is not None and (transfer or tx is not None):
            raise RdxError("the wide regressor and the transfer diagnostic are declared on all five features only")
        pr, wt, n = RSN.regressor_rows(d)
        m = np.asarray(d["pass_truth"], bool)
        if tx is not None:
            if len(tx) != len(d["MCgen"]):
                raise RdxError(f"the sidecar has {len(tx)} rows; the unfold's MCgen has {len(d['MCgen'])}")
            txm = tx[m]
            tx_fit, tx_pred = txm[pr], txm[~pr]
        ctx = RSN.transfer_context(d, RSN.reporting_map()) if transfer else None
        true_make, true_rw = onc.make_estimators, onc._reweight
        st = {"push": np.ones(n), "clf2": None}
        fits: list[int] = []
        preds: list[int] = []
        sums: list[float] = []
        diag: list[dict] = []

        def rw(events, clf):
            out = true_rw(events, clf)
            if clf is st["clf2"]:
                if len(out) != n:
                    raise RdxError("the second classifier's output is not on the truth-passing rows")
                st["push"] = out
            return out

        def widen(X, extra, what):
            X = np.asarray(X)
            if len(X) != len(extra):
                raise RdxError(f"the regressor's {what} got {len(X)} rows, not the {len(extra)} declared rows")
            return np.hstack([X, extra])

        def factory(kind, nvars, seed=None):
            if kind != "lgbm":
                raise RdxError(f"declared for the lgbm estimators only, got {kind!r}")
            clf1, clf2, reg = true_make(kind, nvars, seed=seed)
            st["clf2"] = clf2
            inner_fit, inner_pred = reg.fit, reg.predict

            def fit(X, y, *args, **kw):
                if args or kw:
                    raise RdxError("the regressor was fitted with arguments beyond (X, y)")
                if len(X) != wt.size or len(y) != wt.size:
                    raise RdxError(f"the regressor got {len(X)} rows, not the {wt.size} reco-passing truth rows")
                Xw = widen(X, tx_fit, "fit") if tx is not None else np.asarray(X)
                sw = wt * np.asarray(st["push"], float)[pr] if weighted else None
                if ctx is not None:
                    k = len(fits)
                    mk = mask_of(len(y), k)
                    probe = type(reg)(**reg.get_params())
                    y_ = np.asarray(y)
                    if sw is None:
                        probe.fit(Xw[~mk], y_[~mk])
                    else:
                        probe.fit(Xw[~mk], y_[~mk], sample_weight=sw[~mk])
                    diag.append(RSN.summarize(probe.predict(Xw[mk]), y_[mk], wt[mk], ctx["cell"][mk],
                                              ctx["acc"][mk], k))
                fits.append(int(len(X)))
                if sw is None:
                    return inner_fit(Xw, y)
                sums.append(float(sw.sum()))
                return inner_fit(Xw, y, sample_weight=sw)

            def predict(X, *args, **kw):
                if args or kw:
                    raise RdxError("the regressor predicted with arguments beyond X")
                preds.append(int(len(X)))
                return inner_pred(widen(X, tx_pred, "predict") if tx is not None else X)

            reg.fit, reg.predict = fit, predict
            return clf1, clf2, reg

        onc.make_estimators, onc._reweight = factory, rw
        try:
            out = orig(d, cols, seed, threads, iters)
        finally:
            onc.make_estimators, onc._reweight = true_make, true_rw
        if fits != [wt.size] * int(iters):
            raise RdxError(f"{len(fits)} instrumented regressor fits for {iters} iterations")
        if tx is not None and preds != [int((~pr).sum())] * int(iters):
            raise RdxError(f"{len(preds)} instrumented regressor predictions for {iters} iterations")
        evidence.update(fit_calls=len(fits), predict_calls=len(preds), rows=int(wt.size),
                        weight_sums=sums if weighted else None)
        if transfer:
            evidence["transfer_records"] = diag
        return out

    return unfold


def _value(rest: list, flag: str) -> str | None:
    return rest[rest.index(flag) + 1] if flag in rest and rest.index(flag) + 1 < len(rest) else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], add_help=False)
    ap.add_argument("--regressor-features", choices=FEATURES, required=True)
    ap.add_argument("--truthx-sidecar", type=Path)
    ap.add_argument("--expect-truthx-sha256")
    ap.add_argument("--truthx-permute", type=int)
    ap.add_argument("--regressor-weight", choices=RSN.WEIGHTS, default="none")
    ap.add_argument("--truth", choices=RSN.TRUTHS, default="ratio")
    ap.add_argument("--transfer", action="store_true")
    a, rest = ap.parse_known_args(argv)
    wide = a.regressor_features == "wide"
    if wide != (a.truthx_sidecar is not None) or (a.truthx_sidecar is None) != (a.expect_truthx_sha256 is None):
        raise RdxError("--truthx-sidecar and --expect-truthx-sha256 go with --regressor-features wide, and only with it")
    if a.truthx_permute is not None and not wide:
        raise RdxError("--truthx-permute is declared for the wide regressor only")
    if a.truth != "ratio" and "--closure" not in rest:
        raise RdxError("a declared truth is for a closure only")
    tx, side = None, None
    if wide:
        npz = _value(rest, "--npz")
        if npz is None:
            raise RdxError("the wide regressor needs pvl_unfold's --npz")
        tx, side = load_sidecar(a.truthx_sidecar, a.expect_truthx_sha256, Path(npz))
        if a.truthx_permute is not None:
            tx = permuted(tx, a.truthx_permute)
    evidence: dict = {"fit_calls": None}
    seen: dict = {}
    orig = (PU.unfold, s5n_pseudo.write_product, L.row_weight, s5c_unfold.load_inputs)
    instrumented = wide or a.regressor_weight != "none" or a.transfer

    def load_inputs(path):
        seen["inputs"] = orig[3](path)
        return seen["inputs"]

    def row_weight(gen, names, ratio, pass_truth):
        r = orig[2](gen, names, ratio, pass_truth)
        if not ratio.get("identity") or not np.all(r == 1.0):
            raise RdxError("a declared truth replaces the identity reweight only")
        t = np.asarray(RSN.truth_rows(a.truth, seen["inputs"]), float)
        if t.shape != r.shape or not np.all(np.isfinite(t)) or np.any(t < 0):
            raise RdxError("the declared truth's reweight is not one finite, non-negative value per row")
        evidence["truth_weight_mean"] = float(t.mean())
        return t

    def write(out, arrays, meta):
        if instrumented and evidence.get("fit_calls") is None:
            raise RdxError("refusing to write: the instrumented regressor never ran")
        rec = {"regressor_features": a.regressor_features, "regressor_weight": a.regressor_weight, "truth": a.truth,
               "transfer": a.transfer, "truthx_permute": a.truthx_permute,
               "truthx_sidecar_sha256": a.expect_truthx_sha256, "truthx_names": list(TRUTHX_NAMES) if wide else None,
               **evidence, "code_sha256": {"rdx_unfold.py": L.sha256_path(__file__),
                                           "rsn_unfold.py": L.sha256_path(RSN.__file__)}}
        if a.truth == "a7_gibuu":
            rec["a7_hypothesis_sha256"] = RSN.A7_HYPOTHESIS_SHA256
        return orig[1](out, arrays, dict(meta, rdx=rec))

    if instrumented:
        PU.unfold = instrument(orig[0], evidence, a.regressor_weight == "w_push_w_truth", a.transfer, tx)
    if a.truth != "ratio":
        L.row_weight, s5c_unfold.load_inputs = row_weight, load_inputs
    s5n_pseudo.write_product = write
    try:
        return PU.main(rest)
    finally:
        PU.unfold, s5n_pseudo.write_product, L.row_weight, s5c_unfold.load_inputs = orig


if __name__ == "__main__":
    sys.exit(main())
