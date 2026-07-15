#!/usr/bin/env python3
"""Measured-data bootstrap helpers for PET full-retraining replicas."""

import os
import tempfile
import numpy as np


def poisson_event_weights(data_weights, mc_weights, seed):
    """Independent data/MC Poisson draws; one MC draw stays event-coherent."""
    data_weights = np.asarray(data_weights)
    mc_weights = np.asarray(mc_weights)
    data_dtype = data_weights.dtype if np.issubdtype(data_weights.dtype, np.floating) else np.dtype(float)
    mc_dtype = mc_weights.dtype if np.issubdtype(mc_weights.dtype, np.floating) else np.dtype(float)
    rd = np.random.default_rng(int(seed))
    rm = np.random.default_rng(int(seed) + 10_000_000)
    data = (data_weights * rd.poisson(1.0, data_weights.size)).astype(data_dtype, copy=False)
    mc = (mc_weights * rm.poisson(1.0, mc_weights.size)).astype(mc_dtype, copy=False)
    return data, mc


def mc_poisson_factor(n_events, seed):
    """The canonical coherent MC draw, reproducible by training and extraction."""
    return np.random.default_rng(int(seed) + 10_000_000).poisson(
        1.0, int(n_events)).astype(np.uint8)


def validate_full_replica_weights(weights, n_events, seed):
    """Reject PET weight files that cannot support coherent full-grid extraction."""
    required = {"w_push", "mc_indices", "mc_bootstrap_factor", "bootstrap_seed"}
    missing = required.difference(weights.files)
    if missing:
        raise ValueError(f"PET replica weights missing keys: {sorted(missing)}")
    saved_seed = int(np.asarray(weights["bootstrap_seed"]).item())
    if saved_seed != int(seed):
        raise ValueError(f"PET replica seed mismatch: file={saved_seed}, requested={seed}")
    idx = np.asarray(weights["mc_indices"])
    w_push = np.asarray(weights["w_push"])
    factor = np.asarray(weights["mc_bootstrap_factor"])
    if idx.ndim != 1 or w_push.ndim != 1 or factor.ndim != 1:
        raise ValueError("PET replica weights, indices, and MC factors must be 1D")
    if not (idx.size == w_push.size == factor.size == int(n_events)):
        raise ValueError(
            f"PET replica does not cover the full MC sample: "
            f"idx/weights/factors={idx.size}/{w_push.size}/{factor.size}, expected={n_events}")
    if not np.array_equal(idx, np.arange(int(n_events), dtype=idx.dtype)):
        raise ValueError("PET replica mc_indices must be the ordered full-sample range")
    if not np.all(np.isfinite(w_push)) or not np.all(np.isfinite(factor)):
        raise ValueError("PET replica weights or MC bootstrap factors are non-finite")
    expected_factor = mc_poisson_factor(n_events, seed)
    if not np.array_equal(factor, expected_factor):
        raise ValueError("stored MC bootstrap factor does not match the canonical seed draw")


def write_xsec_replica(path, seed, xsec, edges):
    """Atomically write the strict replica artifact consumed by covariance combiners."""
    xsec = np.asarray(xsec, dtype=float)
    shape = tuple(len(np.asarray(e)) - 1 for e in edges)
    if xsec.shape != shape:
        raise ValueError(f"cross-section shape {xsec.shape} does not match edges {shape}")
    if not np.all(np.isfinite(xsec)):
        raise ValueError("cross-section replica contains non-finite values")
    from xsec_nd import total_xsec
    total = float(total_xsec(xsec, edges))
    if not np.isfinite(total):
        raise ValueError("cross-section replica integral is non-finite")

    path = os.path.abspath(os.fspath(path))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        prefix=os.path.basename(path) + ".", suffix=".tmp.npz",
        dir=os.path.dirname(path), delete=False)
    tmp = handle.name
    handle.close()
    try:
        np.savez_compressed(tmp, seed=np.asarray(int(seed)),
                            xsec_flat=xsec.ravel(order="C"),
                            shape=np.asarray(shape, dtype=np.int64),
                            total_xsec=np.asarray(total))
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return total


def retrained_bootstrap_toy(seed=1):
    """Small classifier toy demonstrating data fluctuation -> retrain -> changed push."""
    from sklearn.linear_model import LogisticRegression

    rng = np.random.default_rng(721)
    mc = rng.normal(0.0, 1.0, (600, 1))
    data = rng.normal(0.45, 1.0, (450, 1))
    X = np.vstack([mc, data])
    y = np.r_[np.zeros(len(mc)), np.ones(len(data))]

    def fit(data_w):
        sw = np.r_[np.ones(len(mc)), data_w]
        clf = LogisticRegression(C=10.0, solver="lbfgs", random_state=0).fit(X, y, sample_weight=sw)
        p = np.clip(clf.predict_proba(mc)[:, 1], 1e-8, 1 - 1e-8)
        return p / (1.0 - p)

    nominal = fit(np.ones(len(data)))
    data_boot, _ = poisson_event_weights(np.ones(len(data)), np.ones(len(mc)), seed)
    return nominal, fit(data_boot)
