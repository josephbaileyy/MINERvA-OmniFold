#!/usr/bin/env python3
"""Z's statistics. SPEC §3.7a (the null ratio), §3.7b (cause 3), §3.7d (correlation candidates).

EVERY FUNCTION HERE RETURNS A NUMBER AND GRADES NOTHING. No acceptance boundary is imported, none
is compared against, and none is defaulted. §3.6d's ordering rule is the reason: the statistic is
defined first and its boundary second, and at this baseline every cause-3 and null boundary is
withheld (`z_contract.Z_BOUNDARIES`). Grading lives in `z_validator`, which must ask
`z_contract.boundary(...)` and be refused.

THE POPULATION AND THE STATISTIC (§3.7b)
----------------------------------------
The population is the FINITE DECLARED OFFSET SET `K = {0, k1, ..., k_{N-1}}`, predeclared in full.
The statistic is the MAXIMUM over `K`, and the reason is the quantifier in the claim -- *"no
declared offset moves the printed value beyond its declared limit"* is quantified over every
member, and a universally quantified claim is graded by the extremum, not by a spread. It is NOT
because the population is finite: a standard deviation over a finite declared set is a perfectly
well-defined descriptive statistic, and this packet computes finite-set covariances itself. The SD
and the per-member table are reported and grade nothing.

WHAT THESE STATISTICS CANNOT SEE (§3.7d)
----------------------------------------
`s_agg` reads `Tr C_Z`; `s_med` reads `diag(C_Z)`. Both are functions of the diagonal alone, so a
change confined to the off-diagonal is invisible to both -- measured: `I2` and `[[1,.9],[.9,1]]`
return exactly 0.0 on both while the uncertainty on their sum and difference move +37.8% and
-68.4%. `project_cov_nd.py` marginalises the assembled covariance as `M C M^T`, so this is a live
use in this tree and not a textbook aside. The correlation candidates below exist for that; none is
adopted and none has a boundary.
"""

from __future__ import annotations

import numpy as np

from z_contract import require

# --------------------------------------------------------------------- the null ratio (§3.7a) --


def support_mask(x_cv):
    """The reported-support predicate, `x_cv > 0` (`unified_throw_cov.py:370`).

    Returned as a mask rather than applied, so a caller records the PREDICATE'S RESULT and a
    validator can recompute `n_rep` from it instead of trusting a recorded integer. A retyped
    `10694` would be a second implementation of this predicate (§1.2).
    """
    x = np.asarray(x_cv, float)
    require(x.ndim == 1, f"support: expected a 1-D flat CV, got {x.ndim}-D")
    require(np.all(np.isfinite(x)), "support: CV contains non-finite entries")
    return x > 0.0


def null_ratio(x_cv, x_cv2, mask=None):
    """`r_null = ||x_cv2 - x_cv|| / ||x_cv||`, both norms over the reported support.

    Numerator and denominator are L2 norms of the SAME cross-section vector in the same units over
    the same population, so the ratio is dimensionless by construction rather than by assertion.
    `sqrt(Tr C_Z)` is rejected as a denominator on the record: it divides a central-value
    difference by an uncertainty scale, so a larger covariance would license a LESS deterministic
    CV, and it makes `M(i)` depend on the object `M(i)` is a precondition for.

    Returns the ratio and both operands' norms. It does NOT compare against `epsilon` -- that
    boundary is withheld (§3.7a, rev. 17).
    """
    x1 = np.asarray(x_cv, float)
    x2 = np.asarray(x_cv2, float)
    require(x1.shape == x2.shape, f"null: shapes {x1.shape} != {x2.shape}")
    m = support_mask(x1) if mask is None else np.asarray(mask, bool)
    require(m.shape == x1.shape, f"null: mask shape {m.shape} != CV shape {x1.shape}")
    n_rep = int(m.sum())
    require(n_rep > 0, "null: the reported support is empty")
    a, b = x1[m], x2[m]
    denom = float(np.linalg.norm(a))
    # A zero denominator ABORTS; it is never pinned to 1. That is the opposite of §1.3a's g rule,
    # and deliberately so: here a zero denominator means the CV is empty, which is not a state any
    # ratio should survive. `unified_throw_cov.py:517`'s `max(..., 1.0)` clamp is the defect §3.1a
    # measures -- the repair is to delete a clamp, not to invent a scale.
    require(denom > 0.0, "null: ||x_cv|| is zero over the reported support -- abort, never pin")
    num = float(np.linalg.norm(b - a))
    return {"r_null": num / denom, "num_norm": num, "cv_norm": denom, "n_rep": n_rep}


def reconstruct_null_ratio(x_cv, x_cv2, mask):
    """§3.3 condition 11b: rebuild the ratio from the PERSISTED operands.

    The point is what it does NOT read: the producer's recorded `fixed_seed_null_norm`. Reading
    that back and comparing it with itself is not a check, which is the shape §1.3b rejected for
    `g`. Rev. 17 also corrected the operand -- the numerator compares two INTERNALLY re-unfolded
    CVs, so the denominator must come from the same run's persisted `x_cv`, not from a separately
    produced ROOT, which would presume the determinism the null is testing.
    """
    m = np.asarray(mask, bool)
    require(m.sum() > 0, "null reconstruction: persisted support predicate selects no bins")
    return null_ratio(x_cv, x_cv2, mask=m)


# ---------------------------------------------------------------- cause 3 statistics (§3.7b) ---
def _sqrt_trace(C):
    C = np.asarray(C, float)
    require(C.ndim == 2 and C.shape[0] == C.shape[1], f"sqrt_tr: not square, {C.shape}")
    tr = float(np.trace(C))
    require(tr >= 0, f"sqrt_tr: negative trace {tr:.6e}")
    return np.sqrt(tr)


def per_bin_sigma(C):
    d = np.diag(np.asarray(C, float))
    require(np.all(d >= 0), "per-bin sigma: negative variance on the diagonal")
    return np.sqrt(d)


def printed_median(C, x_cv, mask):
    """`q = median_i(sigma_i / x_i)` over the reported support -- the note's per-bin summary.

    `x_cv` is held fixed at the `k = 0` member by the caller: the central value is not a
    covariance-construction quantity, so varying it here would measure a different thing.
    """
    m = np.asarray(mask, bool)
    sig = per_bin_sigma(C)[m]
    x = np.asarray(x_cv, float)[m]
    require(np.all(x > 0), "printed median: support contains non-positive CV entries")
    return float(np.median(sig / x))


def s_agg(cov_by_offset, baseline_key=0):
    """Maximum relative change in `sqrt(Tr C_Z)` over the declared offset set."""
    require(baseline_key in cov_by_offset, f"s_agg: baseline {baseline_key!r} absent")
    base = _sqrt_trace(cov_by_offset[baseline_key])
    require(base > 0, "s_agg: baseline sqrt-trace is zero")
    per = {k: _sqrt_trace(C) for k, C in cov_by_offset.items()}
    rel = {k: abs(v - base) / base for k, v in per.items()}
    worst = max(rel, key=rel.get)
    return {"s_agg": rel[worst], "argmax_offset": worst, "baseline": base,
            "per_member": per, "per_member_rel": rel,
            "sd_of_members": float(np.std(list(per.values()), ddof=1)) if len(per) > 1 else 0.0}


def s_med(cov_by_offset, x_cv, mask, baseline_key=0):
    """Maximum relative change in the printed per-bin median over the declared offset set."""
    require(baseline_key in cov_by_offset, f"s_med: baseline {baseline_key!r} absent")
    per = {k: printed_median(C, x_cv, mask) for k, C in cov_by_offset.items()}
    base = per[baseline_key]
    require(base > 0, "s_med: baseline printed median is zero")
    rel = {k: abs(v - base) / base for k, v in per.items()}
    worst = max(rel, key=rel.get)
    return {"s_med": rel[worst], "argmax_offset": worst, "baseline": base,
            "per_member": per, "per_member_rel": rel,
            "sd_of_members": float(np.std(list(per.values()), ddof=1)) if len(per) > 1 else 0.0}


def per_bin_movement(cov_by_offset, mask, baseline_key=0):
    """`m_i = max_k |sigma_i^(k) - sigma_i^(0)| / sigma_i^(0)`, with its distribution.

    REPORTED, GRADING NOTHING (§3.7b item 3 / D2). Rev. 16 withdrew the recommendation to make this
    a third binding leg: applying the printed median's precision to it is a new tolerance choice,
    not a consequence of that summary's formatting, and a missing data release does not prevent
    specifying a scientifically motivated per-bin tolerance. The argmax bin is reported because it
    is what makes CONCENTRATION visible -- a median can hold still while a few bins move a lot.
    """
    m = np.asarray(mask, bool)
    require(baseline_key in cov_by_offset, f"per-bin movement: baseline {baseline_key!r} absent")
    s0 = per_bin_sigma(cov_by_offset[baseline_key])[m]
    require(np.all(s0 > 0), "per-bin movement: baseline sigma has zero entries on the support")
    worst = np.zeros_like(s0)
    for k, C in cov_by_offset.items():
        if k == baseline_key:
            continue
        worst = np.maximum(worst, np.abs(per_bin_sigma(C)[m] - s0) / s0)
    support_idx = np.flatnonzero(m)
    amax = int(np.argmax(worst)) if worst.size else -1
    return {"median": float(np.median(worst)), "p90": float(np.percentile(worst, 90)),
            "max": float(worst.max()) if worst.size else 0.0,
            "argmax_support_index": amax,
            "argmax_grid_index": int(support_idx[amax]) if worst.size else -1,
            "n_support": int(m.sum())}


# ------------------------------------------------- correlation candidates (§3.7d) -- NONE ADOPTED
def s_proj(cov_by_offset, functionals, baseline_key=0):
    """Maximum relative change in `sqrt(u^T C u)` over a PREDECLARED set of linear functionals.

    `functionals` is a 2-D array whose ROWS are the `u` -- in practice the rows of
    `project_cov_nd.py`'s width-weighted `M`, plus the all-ones vector. A predeclared set keeps this
    a falsifiable measurement rather than a search over functionals until one moves.

    Incremental I/O is zero: the two exact legs already materialise the full matrix
    (`adopt_unified_5d.py:46-49` reads a TH2D through `np.frombuffer`, not bin by bin).
    """
    U = np.atleast_2d(np.asarray(functionals, float))
    require(baseline_key in cov_by_offset, f"s_proj: baseline {baseline_key!r} absent")
    C0 = np.asarray(cov_by_offset[baseline_key], float)
    require(U.shape[1] == C0.shape[0],
            f"s_proj: functional width {U.shape[1]} != dimension {C0.shape[0]}")

    def _vals(C):
        C = np.asarray(C, float)
        q = np.einsum("ij,jk,ik->i", U, C, U)
        require(np.all(q >= 0), "s_proj: negative quadratic form -- C is not PSD on these u")
        return np.sqrt(q)

    base = _vals(C0)
    require(np.all(base > 0), "s_proj: a predeclared functional has zero baseline uncertainty")
    worst, arg_k, arg_u = 0.0, baseline_key, -1
    per = {}
    for k, C in cov_by_offset.items():
        rel = np.abs(_vals(C) - base) / base
        per[k] = float(rel.max())
        if per[k] > worst:
            worst, arg_k, arg_u = per[k], k, int(np.argmax(rel))
    return {"s_proj": worst, "argmax_offset": arg_k, "argmax_functional": arg_u,
            "per_member": per, "n_functionals": int(U.shape[0])}


def correlation_matrix(C):
    C = np.asarray(C, float)
    d = np.sqrt(np.diag(C))
    require(np.all(d > 0), "correlation: zero variance on the diagonal")
    return C / np.outer(d, d)


def s_corr(cov_by_offset, baseline_key=0):
    """Relative Frobenius change in the CORRELATION matrix -- the diagonal divided out.

    Cannot be satisfied by the diagonal, which is the whole point: it is the leg that sees what
    `s_agg` and `s_med` are blind to.
    """
    require(baseline_key in cov_by_offset, f"s_corr: baseline {baseline_key!r} absent")
    R0 = correlation_matrix(cov_by_offset[baseline_key])
    n0 = float(np.linalg.norm(R0, "fro"))
    require(n0 > 0, "s_corr: baseline correlation matrix is zero")
    per = {k: float(np.linalg.norm(correlation_matrix(C) - R0, "fro") / n0)
           for k, C in cov_by_offset.items()}
    worst = max(per, key=per.get)
    return {"s_corr": per[worst], "argmax_offset": worst, "per_member": per}


def s_eig(cov_by_offset, baseline_key=0):
    """Relative change in the LEADING eigenvalue.

    The most expensive of the three and the least interpretable. `~1-3 min` per member at the real
    `10,694` dimension on a laptop-class machine -- a LOCAL TIMING ESTIMATE, transferred elsewhere
    with runtime unestablished, since an eigensolve depends on hardware, thread count and the
    numerical library. If PSD is checked by `eigvalsh` (`z_assembly.gate_symmetry_psd`'s default,
    and what §5.2 assumes) the spectrum is already computed and this is a byproduct; if PSD is
    checked by Cholesky it is not. That is a conditional, not a saving.
    """
    require(baseline_key in cov_by_offset, f"s_eig: baseline {baseline_key!r} absent")

    def _lead(C):
        C = np.asarray(C, float)
        return float(np.linalg.eigvalsh(0.5 * (C + C.T))[-1])

    base = _lead(cov_by_offset[baseline_key])
    require(base > 0, "s_eig: baseline leading eigenvalue is not positive")
    per = {k: abs(_lead(C) - base) / base for k, C in cov_by_offset.items()}
    worst = max(per, key=per.get)
    return {"s_eig": per[worst], "argmax_offset": worst, "baseline": base, "per_member": per}
