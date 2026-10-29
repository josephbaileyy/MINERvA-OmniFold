"""Frozen positive control for docs/orchestration/audit_validator_tolerance_units.py. Parsed, never imported.

`mat_gates` as it stood in `nd-unfolding/p4_validate_active_lateral_fps.py` at c9ee6fe2a, verbatim, before OI-12
made its diagonal bound relative. It mixes units in one function: the asymmetry and PSD checks are relative and the
diagonal bound is the absolute `-1e-30`. It is kept so the auditor's sweep still has a real instance to find.
"""
import numpy as np


def mat_gates(C, tag):
    r = {"shape": list(C.shape), "all_finite": bool(np.all(np.isfinite(C)))}
    Cs = 0.5 * (C + C.T)
    ev = np.linalg.eigvalsh(Cs)
    r["rel_asymmetry"] = float(np.max(np.abs(C - C.T)) / max(1e-300, np.max(np.abs(C))))
    r["min_over_max_eig"] = float(ev[0] / max(1e-300, abs(ev[-1])))
    r["psd"] = bool(ev[0] >= -1e-12 * abs(ev[-1]))
    d = np.diag(C)
    r["diag_finite_nonneg"] = bool(np.all(np.isfinite(d)) and np.all(d >= -1e-30))
    r["sqrt_trace"] = float(np.sqrt(np.clip(np.trace(Cs), 0, None)))
    # The matrix is defined on the reported cells, so its dimension IS the reported count.
    # sum(d > 0) undercounts: a reported cell with zero ensemble variance has d == 0.
    r["n_reported"] = int(C.shape[0])
    r["zero_diag_reported_idx"] = [int(i) for i in np.flatnonzero(d == 0)]
    # `psd` only asks whether any eigenvalue is negative, so an exact zero passes it. This
    # sibling records how many directions carry variance at the declared 1e-10*lambda_max cutoff.
    lam_max = float(ev[-1])
    r["rank_at_1em10_lambda_max"] = int(np.sum(ev > 1e-10 * lam_max)) if lam_max > 0 else 0
    print(f"[{tag}] shape={r['shape']} finite={r['all_finite']} psd={r['psd']} "
          f"rank@1e-10={r['rank_at_1em10_lambda_max']}/{r['n_reported']} "
          f"zero_diag={len(r['zero_diag_reported_idx'])} sqrt_tr={r['sqrt_trace']:.4e}")
    return r
