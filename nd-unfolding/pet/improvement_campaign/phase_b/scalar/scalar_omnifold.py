"""Two-step OmniFold on scalar inputs, mirroring `omnifold_nn/omnifold/omnifold.py` step for step.

What is mirrored from the engine (MultiFold.Unfold / RunStep1 / RunStep2 / RunModel / reweight):

* step 1: class 0 = prior rows with weight ``push * w_reco * pass_reco``, class 1 = pseudo-data rows
  with their weight; the new pull is ``push * exp(logit)`` on pass_reco rows and ``push`` elsewhere;
* step 2: the pass_gen rows twice, class 0 weight ``w_truth``, class 1 weight ``w_truth * pull``;
  the new push is ``exp(logit)`` on pass_gen rows and 1 elsewhere (not a product with the old push);
* the classes are NOT rebalanced: the prior's reco leg is normalized to 1e6 over pass_reco rows and
  the pseudo-data to 1e6 (`DataLoader(normalize=True)`), exactly as the historical driver built them;
* ``w = exp(clip(logit, -30, 30))`` (`REWEIGHT_LOGIT_CAP`);
* a train/validation split drawn ONCE per step and reused at every iteration (the engine shuffles
  `idx_1`/`idx_2` on the first, uncached call and reuses them), train fraction 0.8, early stopping on
  the weighted validation loss, and prediction on ALL rows (in-sample, as the engine does).

Deliberate differences, stated rather than hidden:

* the classifiers are scalar (sklearn HistGradientBoosting or a small MLP), not PET;
* rows whose weight is identically zero (prior rows failing pass_reco in step 1, rows failing
  pass_gen in step 2) are left out of the fit -- they contribute nothing to a weighted loss, so the
  fitted function is the same, and it is 2x cheaper;
* boosted trees are refit from scratch at every iteration (there is no warm start for a changed
  target); the MLP may warm-start across iterations like the engine's clone-and-continue, but is not
  given the engine's annealed learning rate.
"""
from __future__ import annotations

import time
from typing import Any, Callable, Protocol

import numpy as np

import binned_unfolding as bu

LOGIT_CAP = 30.0          # omnifold.py REWEIGHT_LOGIT_CAP
TRAIN_FRAC = 0.8          # MultiFold default train_frac


class RatioClassifier(Protocol):
    def fit(self, X_tr: np.ndarray, y_tr: np.ndarray, w_tr: np.ndarray, X_va: np.ndarray,
            y_va: np.ndarray, w_va: np.ndarray) -> dict[str, Any]: ...

    def logit(self, X: np.ndarray) -> np.ndarray: ...


def _capped_ratio(logit: np.ndarray) -> tuple[np.ndarray, int]:
    logit = np.asarray(logit, dtype=np.float64)
    if not np.isfinite(logit).all():
        raise ValueError(f"{int((~np.isfinite(logit)).sum())} non-finite logits (fail closed)")
    saturated = int((np.abs(logit) >= LOGIT_CAP).sum())
    return np.exp(np.clip(logit, -LOGIT_CAP, LOGIT_CAP)), saturated


def _split(n: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    idx = rng.permutation(n)
    n_tr = int(TRAIN_FRAC * n)
    return idx[:n_tr], idx[n_tr:]


def run_scalar_omnifold(*, X_reco_mc: np.ndarray, X_reco_data: np.ndarray, X_gen_mc: np.ndarray,
                        pass_reco_mc: np.ndarray, pass_gen_mc: np.ndarray,
                        w_truth_mc: np.ndarray, w_reco_mc: np.ndarray, w_data: np.ndarray,
                        make_step1: Callable[[int], RatioClassifier],
                        make_step2: Callable[[int], RatioClassifier],
                        iterations: int, seed: int, warm_start: bool = False,
                        callback: Callable[[dict[str, Any]], None] | None = None,
                        ) -> dict[str, np.ndarray]:
    """Run `iterations` OmniFold iterations; call ``callback`` with every iteration's record.

    ``X_reco_mc`` / ``X_gen_mc`` are aligned to ALL prior rows (their values are read only where
    the corresponding flag is true); ``X_reco_data`` to the pseudo-data rows. Returns the final
    ``{"pull", "push"}``.
    """
    s1 = np.asarray(pass_reco_mc, dtype=bool)
    pg = np.asarray(pass_gen_mc, dtype=bool)
    w_t = np.asarray(w_truth_mc, dtype=np.float64).copy()
    w_r = np.asarray(w_reco_mc, dtype=np.float64).copy()
    w_d = np.asarray(w_data, dtype=np.float64).copy()
    c = bu.ENGINE_NORMALIZATION / w_r[s1].sum()
    w_t *= c
    w_r *= c
    w_d *= bu.ENGINE_NORMALIZATION / w_d.sum()

    rng = np.random.default_rng(int(seed))
    n_mc1 = int(s1.sum())
    X1 = np.concatenate([np.asarray(X_reco_mc)[s1], np.asarray(X_reco_data)], axis=0)
    y1 = np.concatenate([np.zeros(n_mc1), np.ones(len(w_d))])
    tr1, va1 = _split(X1.shape[0], rng)
    n_pg = int(pg.sum())
    Xg = np.asarray(X_gen_mc)[pg]
    X2 = np.concatenate([Xg, Xg], axis=0)
    y2 = np.concatenate([np.zeros(n_pg), np.ones(n_pg)])
    tr2, va2 = _split(X2.shape[0], rng)

    push = np.ones(w_t.shape[0], dtype=np.float64)
    pull = push.copy()
    model1 = make_step1(0) if warm_start else None
    model2 = make_step2(0) if warm_start else None
    for k in range(1, iterations + 1):
        m1 = model1 if warm_start else make_step1(k)
        w1 = np.concatenate([(push * w_r)[s1], w_d])
        t0 = time.perf_counter()
        info1 = m1.fit(X1[tr1], y1[tr1], w1[tr1], X1[va1], y1[va1], w1[va1])
        ratio1, sat1 = _capped_ratio(m1.logit(np.asarray(X_reco_mc)[s1]))
        info1.update({"seconds": time.perf_counter() - t0, "saturated": sat1,
                      "class_sums": [float(w1[:n_mc1].sum()), float(w1[n_mc1:].sum())],
                      "rows": [n_mc1, int(len(w_d))]})
        prev_push = push
        pull = push.copy()
        pull[s1] = push[s1] * ratio1

        m2 = model2 if warm_start else make_step2(k)
        w2 = np.concatenate([w_t[pg], (w_t * pull)[pg]])
        t0 = time.perf_counter()
        info2 = m2.fit(X2[tr2], y2[tr2], w2[tr2], X2[va2], y2[va2], w2[va2])
        ratio2, sat2 = _capped_ratio(m2.logit(Xg))
        info2.update({"seconds": time.perf_counter() - t0, "saturated": sat2,
                      "class_sums": [float(w2[:n_pg].sum()), float(w2[n_pg:].sum())],
                      "rows": [n_pg, n_pg]})
        push = np.ones_like(push)
        push[pg] = ratio2
        if callback is not None:
            callback({"iteration": k, "pull": pull, "push": push, "prev_push": prev_push,
                      "step1": info1, "step2": info2, "w_reco_normalized": w_r,
                      "w_data_normalized": w_d})
    return {"pull": pull, "push": push}


# --------------------------------------------------------------------------------------------- #
# Classifiers
# --------------------------------------------------------------------------------------------- #
def _weighted_logloss(y: np.ndarray, p: np.ndarray, w: np.ndarray) -> float:
    p = np.clip(p, 1e-12, 1.0 - 1e-12)
    return float(-(w * (y * np.log(p) + (1.0 - y) * np.log1p(-p))).sum() / w.sum())


class HGBRatio:
    """HistGradientBoostingClassifier on a weighted binary target; logit = its raw score."""

    def __init__(self, seed: int, threads: int | None = None, **params: Any) -> None:
        from sklearn.ensemble import HistGradientBoostingClassifier
        defaults = dict(learning_rate=0.1, max_iter=400, max_leaf_nodes=31,
                        min_samples_leaf=200, l2_regularization=0.0, early_stopping=True,
                        n_iter_no_change=10, tol=1e-7, scoring="loss")
        defaults.update(params)
        self.params = defaults
        self.model = HistGradientBoostingClassifier(random_state=int(seed), **defaults)

    def fit(self, X_tr, y_tr, w_tr, X_va, y_va, w_va) -> dict[str, Any]:
        self.model.fit(X_tr, y_tr, sample_weight=w_tr, X_val=X_va, y_val=y_va,
                       sample_weight_val=w_va)
        p_va = self.model.predict_proba(X_va)[:, 1]
        return {"model": "hgb", "n_iter": int(self.model.n_iter_),
                "val_logloss": _weighted_logloss(y_va, p_va, w_va)}

    def logit(self, X: np.ndarray) -> np.ndarray:
        return np.asarray(self.model.decision_function(X), dtype=np.float64)


class MLPRatio:
    """A small sklearn MLP trained epoch by epoch with early stopping on the WEIGHTED validation
    log-loss and the best epoch restored. (The historical engine's EarlyStopping never fired --
    patience 10 > 8 epochs -- so each PET fit handed on its LAST epoch; this reference is meant to
    be a well-converged scalar learner instead, and says so.) Inputs pass through ``transform``
    ("slog1p" = sign(x) log(1+|x|), default, because E_avail / p_parallel / q3 are heavy-tailed and a
    standardized raw coordinate crowds the bulk into a sliver; "raw" = none) and are then
    standardized with statistics frozen at the first fit, so a warm start sees the same coordinates
    at every iteration."""

    def __init__(self, seed: int, hidden: tuple[int, ...] = (64, 64), lr: float = 1e-3,
                 batch_size: int = 1024, max_epochs: int = 30, patience: int = 4,
                 alpha: float = 1e-5, transform: str = "slog1p") -> None:
        from sklearn.neural_network import MLPClassifier
        if transform not in ("slog1p", "raw"):
            raise ValueError(f"unknown transform {transform!r}")
        self.transform = transform
        self.params = dict(hidden=list(hidden), lr=lr, batch_size=batch_size,
                           max_epochs=max_epochs, patience=patience, alpha=alpha,
                           transform=transform)
        self.model = MLPClassifier(hidden_layer_sizes=hidden, activation="relu", solver="adam",
                                   learning_rate_init=lr, batch_size=batch_size, alpha=alpha,
                                   max_iter=1, shuffle=True, random_state=int(seed))
        self.max_epochs, self.patience = int(max_epochs), int(patience)
        self.mean: np.ndarray | None = None
        self.scale: np.ndarray | None = None

    def _t(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        return np.sign(X) * np.log1p(np.abs(X)) if self.transform == "slog1p" else X

    def _z(self, X: np.ndarray) -> np.ndarray:
        return (self._t(X) - self.mean) / self.scale

    def fit(self, X_tr, y_tr, w_tr, X_va, y_va, w_va) -> dict[str, Any]:
        import copy
        import warnings
        if self.mean is None:
            self.mean = self._t(X_tr).mean(axis=0)
            sd = self._t(X_tr).std(axis=0)
            self.scale = np.where(sd > 0, sd, 1.0)
        Z_tr, Z_va = self._z(X_tr), self._z(X_va)
        best, best_state, stale, history = np.inf, None, 0, []
        for _epoch in range(self.max_epochs):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.model.partial_fit(Z_tr, y_tr, sample_weight=w_tr, classes=np.array([0., 1.]))
            loss = _weighted_logloss(y_va, self.model.predict_proba(Z_va)[:, 1], w_va)
            history.append(loss)
            if loss < best - 1e-7:
                best, stale = loss, 0
                best_state = (copy.deepcopy(self.model.coefs_),
                              copy.deepcopy(self.model.intercepts_))
            else:
                stale += 1
                if stale >= self.patience:
                    break
        if best_state is not None:
            self.model.coefs_, self.model.intercepts_ = best_state
        return {"model": "mlp", "epochs_run": len(history), "best_epoch": int(np.argmin(history)) + 1,
                "val_logloss": float(best), "val_history": history}

    def logit(self, X: np.ndarray) -> np.ndarray:
        p = np.clip(self.model.predict_proba(self._z(X))[:, 1], 1e-15, 1.0 - 1e-15)
        return np.log(p) - np.log1p(-p)


class BinnedOracleRatio:
    """The Bayes-optimal classifier that sees only a bin index (column 0 of X): log of the class-1
    to class-0 weight ratio in the bin, over ALL rows it is shown (train and validation). Used by
    the tests to prove this loop and `binned_unfolding.binned_omnifold` are the same algorithm."""

    def __init__(self, n_bins: int) -> None:
        self.n_bins = int(n_bins)
        self.table: np.ndarray | None = None

    def fit(self, X_tr, y_tr, w_tr, X_va, y_va, w_va) -> dict[str, Any]:
        b = np.concatenate([X_tr[:, 0], X_va[:, 0]]).astype(np.int64)
        y = np.concatenate([y_tr, y_va])
        w = np.concatenate([w_tr, w_va])
        s1 = np.bincount(b[y == 1], weights=w[y == 1], minlength=self.n_bins)
        s0 = np.bincount(b[y == 0], weights=w[y == 0], minlength=self.n_bins)
        # A bin with prior weight but no class-1 weight gets ratio 0 (capped at exp(-30), as the
        # engine's clip would); a bin with no prior weight is never evaluated on a prior row.
        with np.errstate(divide="ignore", invalid="ignore"):
            self.table = np.where(s0 > 0, np.where(s1 > 0, np.log(s1 / s0), -10 * LOGIT_CAP),
                                  0.0)
        return {"model": "binned-oracle"}

    def logit(self, X: np.ndarray) -> np.ndarray:
        return self.table[np.asarray(X[:, 0], dtype=np.int64)]
