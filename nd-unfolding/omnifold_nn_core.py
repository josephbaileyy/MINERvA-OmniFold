#!/usr/bin/env python3
"""ROOT-free neural-net OmniFold core (Phase 2 of HIGHER_DIM_OMNIFOLD_DESIGN.md).

Why this exists separately from unbinned_unfolding/python/omnifold.py: that module
`import ROOT` at the top, so it cannot be imported under a TensorFlow environment
(NERSC `module load tensorflow/2.15.0`). This module is numpy-only at import time and
imports keras lazily, so the same NN engine runs both:
  * in-pipeline, via the estimator="nn" branch added to omnifold.py (where ROOT+TF
    coexist), and
  * standalone, in a ROOT-free TF env, on dumped .npz inputs (the NN-vs-GBDT
    cross-check), reusing the IDENTICAL two-step loop so the comparison isolates the
    classifier (GBDT vs MLP) and nothing else.

The MLP architecture (layer sizes, gelu, logit output + weighted sigmoid-BCE) is taken
from the vendored ViniciusMikuni/omnifold `omnifold/net.py` (MLP, weighted_binary_
crossentropy), so this is an adoption of that codebase's network, wired behind a
scikit-learn-style fit/predict_proba so the validated OmniFold loop is unchanged.

Feature standardization is applied here (NN needs it; the GBDT path is scale-free and
must NOT be standardized -- a deliberate asymmetry, documented in the design doc).
"""
import numpy as np


# ---------------------------------------------------------------------------
# scikit-learn-style keras MLP (classifier + regressor), lazy TF import
# ---------------------------------------------------------------------------
class _StandardScaler:
    def fit(self, X):
        self.mean_ = X.mean(axis=0)
        self.std_ = X.std(axis=0)
        self.std_[self.std_ == 0] = 1.0
        return self

    def transform(self, X):
        return (X - self.mean_) / self.std_


def _build_mlp(nvars, layer_sizes, activation, regression):
    """ViniciusMikuni/omnifold net.py MLP: Dense stack -> Dense(1) logit output."""
    from tensorflow.keras.layers import Dense, Input
    from tensorflow.keras.models import Model
    inp = Input((nvars,))
    h = Dense(layer_sizes[0], activation=activation)(inp)
    for s in layer_sizes[1:]:
        h = Dense(s, activation=activation)(h)
    out = Dense(1, activation=("linear" if regression else None))(h)
    return Model(inp, out)


class KerasMLP:
    """Weighted keras MLP with a scikit-learn-style interface.

    classifier: predict_proba(X)[:,1] = sigmoid(logit); trained with the vendored
    weighted_binary_crossentropy (y packed as [label, weight]).
    regressor:  predict(X) trained with sample-weighted MSE.
    """

    def __init__(self, nvars, regression=False, layer_sizes=(64, 128, 64),
                 activation="gelu", epochs=50, batch_size=10000, lr=1e-3,
                 patience=8, verbose=0):
        self.nvars = nvars
        self.regression = regression
        self.layer_sizes = list(layer_sizes)
        self.activation = activation
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.patience = patience
        self.verbose = verbose
        self.scaler = _StandardScaler()
        self.model = None

    def _compile(self):
        import tensorflow as tf
        from tensorflow import keras
        model = _build_mlp(self.nvars, self.layer_sizes, self.activation,
                           self.regression)
        if self.regression:
            def loss(y_true, y_pred):
                w = y_true[:, 1:2]
                t = y_true[:, 0:1]
                return tf.reduce_mean(w * tf.square(t - y_pred))
        else:
            def loss(y_true, y_pred):  # weighted BCE on logits (net.py convention)
                w = y_true[:, 1:2]
                t = y_true[:, 0:1]
                return tf.reduce_mean(
                    w * tf.nn.sigmoid_cross_entropy_with_logits(labels=t, logits=y_pred))
        model.compile(optimizer=keras.optimizers.Adam(self.lr), loss=loss)
        return model

    def fit(self, X, y, sample_weight=None):
        from tensorflow import keras
        X = np.asarray(X, np.float32)
        y = np.asarray(y, np.float32).reshape(-1)
        if sample_weight is None:
            sample_weight = np.ones(len(y), np.float32)
        sample_weight = np.asarray(sample_weight, np.float32).reshape(-1)
        # Shuffle before fit: keras validation_split takes the LAST fraction
        # WITHOUT shuffling, and OmniFold's step data is ordered [class0; class1],
        # so an unshuffled split makes the validation set single-class -> val_loss
        # is meaningless and early-stopping/restore_best_weights pick a degenerate
        # epoch (observed: the unfolded normalization collapsed to ~0). Permuting
        # first makes the 20% validation split class-representative.
        rng = np.random.default_rng(0)
        perm = rng.permutation(len(y))
        self.scaler.fit(X)
        Xs = self.scaler.transform(X[perm]).astype(np.float32)
        ypack = np.stack([y[perm], sample_weight[perm]], axis=1)
        self.model = self._compile()
        cb = [keras.callbacks.EarlyStopping(monitor="val_loss", patience=self.patience,
                                            restore_best_weights=True)]
        self.model.fit(Xs, ypack, epochs=self.epochs, batch_size=self.batch_size,
                       validation_split=0.2, shuffle=True, callbacks=cb,
                       verbose=self.verbose)
        return self

    def _logit(self, X):
        Xs = self.scaler.transform(np.asarray(X, np.float32)).astype(np.float32)
        return self.model.predict(Xs, batch_size=self.batch_size, verbose=0).reshape(-1)

    def predict(self, X):
        return self._logit(X)

    def predict_proba(self, X):
        p = 1.0 / (1.0 + np.exp(-self._logit(X)))
        return np.column_stack([1.0 - p, p])


# ---------------------------------------------------------------------------
# Classifier/regressor factory
# ---------------------------------------------------------------------------
def make_estimators(kind, nvars, seed=None):
    """Return (clf1, clf2, regressor) for the requested kind.

    kind="nn":   keras MLP (this module). kind="lgbm": LightGBM (matches the
    production GBDT path in omnifold.py). Both expose fit/predict_proba (+predict).
    """
    if kind == "nn":
        kw = dict(nvars=nvars)
        return (KerasMLP(**kw), KerasMLP(**kw), KerasMLP(regression=True, **kw))
    if kind == "lgbm":
        from lightgbm import LGBMClassifier, LGBMRegressor
        d = dict(n_estimators=100, num_leaves=8, learning_rate=0.1, verbose=-1)
        if seed is not None:
            d = dict(d, random_state=int(seed))
        return (LGBMClassifier(**d), LGBMClassifier(**d), LGBMRegressor(**d))
    raise ValueError(f"kind must be 'nn' or 'lgbm', got {kind!r}")


def _reweight(events, clf):
    p = clf.predict_proba(events)[:, 1]
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.nan_to_num(p / (1.0 - p))


def _balance_weights(y, w):
    """Rescale each class's sample weights to an equal total (= N/2).

    OmniFold's w = p/(1-p) assumes the classifier is calibrated in *absolute*
    terms, i.e. p = W1 f1 / (W1 f1 + W0 f0). An MLP trained on imbalanced class
    totals collapses to the trivial bias solution p = W1/(W0+W1) (constant in x):
    the density ratio f1/f0 is never learned and the unfolded normalization
    collapses (observed: ~1e-6 of the GBDT result). Training on class-BALANCED
    weights makes the bias minimum p=0.5, so any x-structure reduces the loss and
    is actually learned; the true normalization W1/W0 is then multiplied back in
    fit_classifier(). GBDT does not need this (it calibrates the absolute ratio
    directly), so balancing is applied only on the NN path.
    """
    w = np.asarray(w, float).copy()
    n = len(y)
    for lab in (0.0, 1.0):
        m = (y == lab)
        tot = w[m].sum()
        if tot > 0:
            w[m] *= (0.5 * n) / tot
    return w


def _class_ratio(y, w):
    """W1/W0 from the original (unbalanced) weights -- the normalization to restore."""
    w = np.asarray(w, float)
    w0 = w[y == 0.0].sum()
    w1 = w[y == 1.0].sum()
    return (w1 / w0) if w0 > 0 else 1.0


# ---------------------------------------------------------------------------
# Two-step OmniFold loop (faithful to unbinned_unfolding/python/omnifold.py,
# estimator-agnostic; ROOT-free)
# ---------------------------------------------------------------------------
def omnifold_loop(MCgen, MCreco, measured, pass_reco, pass_truth, meas_pass_reco,
                  num_iterations, kind, MCgen_weights=None, MCreco_weights=None,
                  measured_weights=None, seed=None, verbose=True):
    MCgen = np.atleast_2d(MCgen); MCreco = np.atleast_2d(MCreco)
    measured = np.atleast_2d(measured)
    if MCgen.shape[0] == 1 and MCgen.shape[1] != MCreco.shape[1]:
        MCgen = MCgen.T
    MCreco = MCreco[pass_truth]; MCgen = MCgen[pass_truth]
    pass_reco = pass_reco[pass_truth]
    MCgen_weights = (np.ones(len(MCgen)) if MCgen_weights is None
                     else np.asarray(MCgen_weights)[pass_truth])
    MCreco_weights = (np.ones(len(MCreco)) if MCreco_weights is None
                      else np.asarray(MCreco_weights)[pass_truth])
    if measured_weights is None:
        measured_weights = np.ones(len(measured))

    meas_lab = np.ones(len(measured[meas_pass_reco]))
    MC_lab = np.zeros(len(MCgen))
    w_pull = np.ones(len(MCgen)); w_push = np.ones(len(MCgen))

    clf1, clf2, reg = make_estimators(kind, MCgen.shape[1], seed=seed)
    use_reg = bool(np.any(~pass_reco))
    balance = (kind == "nn")   # NN needs class-balanced training (see _balance_weights)

    def fit_reweight(clf, X, y, w, eval_X):
        ratio = 1.0
        wfit = w
        if balance:
            ratio = _class_ratio(y, w)
            wfit = _balance_weights(y, w)
        clf.fit(X, y, sample_weight=wfit)
        return ratio * _reweight(eval_X, clf)

    for it in range(num_iterations):
        if verbose:
            print(f"[nn-core] iteration {it} (kind={kind})", flush=True)
        s1x = np.concatenate([MCreco[pass_reco], measured[meas_pass_reco]])
        s1y = np.concatenate([np.zeros(int(pass_reco.sum())), meas_lab])
        s1w = np.concatenate([w_push[pass_reco] * MCreco_weights[pass_reco],
                              np.ones(len(measured[meas_pass_reco]))
                              * measured_weights[meas_pass_reco]])
        new_w = np.ones_like(w_pull)
        new_w[pass_reco] = fit_reweight(clf1, s1x, s1y, s1w, MCreco[pass_reco])
        if use_reg:
            reg.fit(MCgen[pass_reco], new_w[pass_reco])
            new_w[~pass_reco] = reg.predict(MCgen[~pass_reco])
        w_pull = w_push * new_w

        s2x = np.concatenate([MCgen, MCgen])
        s2y = np.concatenate([MC_lab, np.ones(len(MCgen))])
        s2w = np.concatenate([MCgen_weights, w_pull * MCgen_weights])
        w_push = fit_reweight(clf2, s2x, s2y, s2w, MCgen)

    return w_pull, w_push
