#!/usr/bin/env python3
"""Small ROOT-free uncertainty helpers shared by production and tests."""

from pathlib import Path

import numpy as np


def guarded_ratio(ratio, name="ratio", invalid_policy="error", clip=(1e-2, 1e2)):
    """Validate a universe/CV ratio and make any neutralization explicit."""
    ratio = np.asarray(ratio, dtype=float)
    bad = ~np.isfinite(ratio) | (ratio <= 0.0)
    if np.any(bad):
        message = f"{name} contains {int(bad.sum())}/{ratio.size} non-finite or non-positive values"
        if invalid_policy == "error":
            raise ValueError(message)
        if invalid_policy != "neutral":
            raise ValueError(f"unknown invalid-ratio policy: {invalid_policy}")
        print(f"[ratio][WARN] {message}; replacing with neutral ratio 1", flush=True)
        ratio = ratio.copy()
        ratio[bad] = 1.0
    if clip is None:
        return ratio
    clipped = (ratio < clip[0]) | (ratio > clip[1])
    if np.any(clipped):
        print(f"[ratio][WARN] {name}: clipping {int(clipped.sum())}/{ratio.size} "
              f"ratios to {clip}", flush=True)
    return np.clip(ratio, *clip)


def require_truth_ratio_bank(bank, bands, expected_flux=100):
    """Require every truth-side +/- endpoint and an exact contiguous flux inventory."""
    bank = Path(bank)
    missing = [f"sig_{band}_t_{idx}.npy" for band in bands for idx in (0, 1)
               if not (bank / f"sig_{band}_t_{idx}.npy").is_file()]
    if missing:
        raise ValueError(f"incomplete truth-ratio bank {bank}: missing {missing}")

    flux_ids = set()
    malformed = []
    prefix = "sig_flux_t_"
    for path in bank.glob(f"{prefix}*.npy"):
        suffix = path.name[len(prefix):-4]
        if suffix.isdigit():
            flux_ids.add(int(suffix))
        else:
            malformed.append(path.name)
    expected = set(range(int(expected_flux)))
    if malformed or flux_ids != expected:
        raise ValueError(
            f"invalid flux bank {bank}: malformed={sorted(malformed)} "
            f"missing={sorted(expected-flux_ids)} extra={sorted(flux_ids-expected)}"
        )
    return list(range(int(expected_flux)))


def _positive_finite_ratio(ratio, name="ratio"):
    ratio = np.asarray(ratio, dtype=float)
    bad = ~np.isfinite(ratio) | (ratio <= 0.0)
    if np.any(bad):
        raise ValueError(
            f"{name} contains {int(bad.sum())}/{ratio.size} non-finite or non-positive values"
        )
    return ratio


def interpolate_asymmetric_ratio(g, rho_plus, rho_minus):
    """Interpolate an asymmetric nuisance, preserving both +/-1 sigma branches.

    rho(g) = rho_plus**g for g>=0 and rho_minus**(-g) for g<0.
    Invalid or zero ratios are rejected instead of silently becoming CV.
    """
    plus = _positive_finite_ratio(rho_plus, "rho_plus")
    minus = _positive_finite_ratio(rho_minus, "rho_minus")
    if plus.shape != minus.shape:
        raise ValueError(f"rho shape mismatch: {plus.shape} != {minus.shape}")
    gg = np.asarray(g, dtype=float)
    if not np.all(np.isfinite(gg)):
        raise ValueError("nuisance g must be finite")
    if gg.ndim == 0:
        if float(gg) == 0.0:
            return np.ones_like(plus)
        return plus ** float(gg) if gg > 0 else minus ** float(-gg)
    try:
        gb = np.broadcast_to(gg, plus.shape)
    except ValueError as exc:
        raise ValueError(f"g shape {gg.shape} is not broadcastable to ratios {plus.shape}") from exc
    out = np.ones_like(plus)
    pos = gb > 0
    neg = gb < 0
    out[pos] = plus[pos] ** gb[pos]
    out[neg] = minus[neg] ** (-gb[neg])
    return out


def mat_covariance(universes):
    """MAT production convention: universe-mean centered, biased 1/N."""
    X = np.asarray(universes, dtype=float)
    if X.ndim != 2 or X.shape[0] < 2:
        raise ValueError("universes must have shape (N>=2, nbins)")
    if not np.all(np.isfinite(X)):
        raise ValueError("universes contain non-finite values")
    Z = X - X.mean(axis=0, keepdims=True)
    return (Z.T @ Z) / X.shape[0]


def joint_throw_covariance(throws, cv):
    """Mean-centered joint covariance plus the separately reported mean shift."""
    X = np.asarray(throws, dtype=float)
    cv = np.asarray(cv, dtype=float)
    if X.ndim != 2 or X.shape[1:] != cv.shape:
        raise ValueError(f"throws/CV shape mismatch: {X.shape} vs {cv.shape}")
    if X.shape[0] < 2 or not np.all(np.isfinite(X)) or not np.all(np.isfinite(cv)):
        raise ValueError("need at least two finite throws and a finite CV")
    mean = X.mean(axis=0)
    return mat_covariance(X), mean - cv


def project_covariance(covariance, projection):
    C = np.asarray(covariance, dtype=float)
    M = np.asarray(projection, dtype=float)
    if C.ndim != 2 or C.shape[0] != C.shape[1]:
        raise ValueError("covariance must be square")
    if M.ndim != 2 or M.shape[1] != C.shape[0]:
        raise ValueError(f"projection/covariance shape mismatch: {M.shape}, {C.shape}")
    if not np.all(np.isfinite(C)) or not np.all(np.isfinite(M)):
        raise ValueError("projection inputs must be finite")
    return M @ C @ M.T


def finite_observable_mask(coords, weights=None):
    x = np.asarray(coords, dtype=float)
    if x.ndim != 2:
        raise ValueError("coords must have shape (events, observables)")
    mask = np.all(np.isfinite(x), axis=1)
    if weights is not None:
        w = np.asarray(weights, dtype=float)
        if w.shape != (x.shape[0],):
            raise ValueError("weight/event shape mismatch")
        mask &= np.isfinite(w)
    return mask


def active_selection_masks(truth, reco, pt_range, pz_range, reco_flags=None):
    """ROOT-free selection kernel used to prove active-lateral migrations."""
    truth = np.asarray(truth, dtype=float)
    reco = np.asarray(reco, dtype=float)
    if truth.shape != reco.shape or truth.ndim != 2 or truth.shape[1] < 2:
        raise ValueError("truth and reco must have matching (events, >=2) shapes")
    tfin = finite_observable_mask(truth)
    rfin = finite_observable_mask(reco)
    t = (tfin & (truth[:, 0] >= pt_range[0]) & (truth[:, 0] <= pt_range[1])
         & (truth[:, 1] >= pz_range[0]) & (truth[:, 1] <= pz_range[1]))
    r = (rfin & (reco[:, 0] >= pt_range[0]) & (reco[:, 0] <= pt_range[1])
         & (reco[:, 1] >= pz_range[0]) & (reco[:, 1] <= pz_range[1]))
    if reco_flags is not None:
        flags = np.asarray(reco_flags, dtype=bool)
        if flags.shape != (truth.shape[0],):
            raise ValueError("reco flag/event shape mismatch")
        r &= flags
    return t, r
