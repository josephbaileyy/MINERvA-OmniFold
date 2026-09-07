#!/usr/bin/env python3
"""Z's assembly algebra (SPEC §1.3a) and the five inflation gates (§1.3b).

    C_Z^c  =  D_Z^c (sum_V C_b) D_Z^c  +  sum_R C_b  +  sum_A L_b  +  C_stat  +  C_ML

    g^c[i] =  sqrt(max(v_uni^c[i], v_blk[i])) / sqrt(v_blk[i])  >= 1,   pinned to 1 where
              v_blk[i] == 0;      D_Z^c = diag(g^c)

`v_uni^c` is the diagonal of the unified-throw covariance for centering variant `c`; `v_blk` is the
diagonal of the VERTICAL block sum `sum_V C_b`. The construction mirrors `adopt_unified_5d.py:
108-113`, which is the producer this validator must be able to disagree with.

THE FIVE GATES, and why five rather than four
---------------------------------------------
Review round 2 (spec rev. 3) found the first four JOINTLY SATISFIABLE BY AN UNINFLATED OBJECT:
`g == 1` everywhere passes the closure identity, `g >= 1`, the zero-denominator rule and PSD. So
gate 3 -- independent reconstruction of `g^c` from its own operands -- is the one that has to
exist, and the other four do not substitute for it.

  G1  closure identity     C_Z^c reproduces from its declared parts within IDENTITY_RTOL
  G2  g domain             g >= 1, finite, and exactly 1 where v_blk == 0
  G3  g reconstruction     recompute g^c from diag(C_uni^c), diag(C_blk); per variant, each from
                           ITS OWN operands -- never the producer's recorded g
  G4  symmetry and PSD     on the INFLATED object, not on the block sum
  G5  band partition       V/R/A disjoint and exhaustive (z_contract.check_band_partition)

G3b -- THE VARIANT-COUPLING IDENTITY, and it is NOT in the spec's own list
-------------------------------------------------------------------------
§3.3 condition 4b names a failure that "survives the first mutation entirely": a DROPPED SHIFT, in
which `g^cv` equals `g^mean` because the producer reused one variant's operands for both. The spec
says to catch it by reconstructing per variant from its own operands, which detects reuse only if
the two operands happen to differ.

There is an exact identity available instead, and it is derivable from facts the spec already
measures. Centering about the CV versus about the throw mean differ by the outer product of the
shift, and `hJointMeanShift` is measured to be *"joint throw mean minus CV"*
(`unified_throw_cov.py:575`):

    C_uni^cv = C_uni^mean + ms ms^T        =>        v_uni^cv - v_uni^mean = ms**2

So the two variants and the recorded shift are related by an identity that a dropped shift breaks
by construction, whatever the producer reused. `check_variant_coupling` gates it.

**This gate is proposed, not inherited.** It is stricter than §1.3b as written. It is implemented
because it closes a failure §3.3 already names, and it is flagged here rather than folded in
silently so a reviewer can reject it without unpicking the rest.

NO ACCEPTANCE BOUNDARY APPEARS IN THIS MODULE. Everything gated here is a structural identity whose
tolerance is arithmetic (`IDENTITY_RTOL`, §3.3 condition 2). The scientific boundaries live in
`z_contract.Z_BOUNDARIES` and are withheld.
"""

from __future__ import annotations

import numpy as np

from z_contract import (IDENTITY_RTOL, G_FLOOR, ZContractError, require,
                        check_band_partition)

CENTERING_VARIANTS = ("cv", "mean")


# ------------------------------------------------------------------------------ g and D_Z ------
def compute_g(v_uni, v_blk):
    """§1.3a's inflation factor. Returns `(g, pinned_mask)`.

    `pinned_mask` marks the bins where `v_blk == 0` and `g` was pinned to exactly 1 -- the receipt
    must carry that count (§1.5), because "pinned" and "computed to 1" are different facts and only
    one of them is evidence of anything.
    """
    v_uni = np.asarray(v_uni, float)
    v_blk = np.asarray(v_blk, float)
    require(v_uni.shape == v_blk.shape,
            f"g: operand shapes differ, v_uni {v_uni.shape} vs v_blk {v_blk.shape}")
    require(v_uni.ndim == 1, f"g: operands must be 1-D diagonals, got {v_uni.ndim}-D")
    require(np.all(np.isfinite(v_uni)), "g: v_uni contains non-finite entries")
    require(np.all(np.isfinite(v_blk)), "g: v_blk contains non-finite entries")
    require(np.all(v_uni >= 0), "g: v_uni has negative variance")
    require(np.all(v_blk >= 0), "g: v_blk has negative variance")

    pinned = v_blk == 0.0
    g = np.ones_like(v_blk)
    m = ~pinned
    g[m] = np.sqrt(np.maximum(v_uni[m], v_blk[m])) / np.sqrt(v_blk[m])
    return g, pinned


def assemble(g, cov_vert_sum, cov_residual_sum, cov_lateral_sum, cov_stat, cov_ml):
    """§1.3a. `D_Z (sum_V) D_Z + sum_R + sum_A + C_stat + C_ML`.

    `D_Z (sum_V) D_Z` is formed as `g[:,None] * S_V * g[None,:]`, which is the same object as the
    matrix product and avoids materialising a 10,694^2 diagonal.
    """
    g = np.asarray(g, float)
    parts = {"vert": cov_vert_sum, "residual": cov_residual_sum, "lateral": cov_lateral_sum,
             "stat": cov_stat, "ml": cov_ml}
    n = g.size
    for name, M in parts.items():
        M = np.asarray(M, float)
        require(M.shape == (n, n), f"assemble: {name} has shape {M.shape}, expected {(n, n)}")
        require(np.all(np.isfinite(M)), f"assemble: {name} contains non-finite entries")
    S_V = np.asarray(cov_vert_sum, float)
    inflated = g[:, None] * S_V * g[None, :]
    return (inflated
            + np.asarray(cov_residual_sum, float)
            + np.asarray(cov_lateral_sum, float)
            + np.asarray(cov_stat, float)
            + np.asarray(cov_ml, float))


# ------------------------------------------------------------------------------- the gates -----
def gate_closure_identity(C_Z, g, cov_vert_sum, cov_residual_sum, cov_lateral_sum,
                          cov_stat, cov_ml, rtol=IDENTITY_RTOL):
    """G1. The assembled object reproduces from its declared parts."""
    rebuilt = assemble(g, cov_vert_sum, cov_residual_sum, cov_lateral_sum, cov_stat, cov_ml)
    C_Z = np.asarray(C_Z, float)
    require(C_Z.shape == rebuilt.shape,
            f"closure: shape {C_Z.shape} != rebuilt {rebuilt.shape}")
    scale = np.max(np.abs(rebuilt))
    require(scale > 0, "closure: rebuilt object is identically zero")
    resid = float(np.max(np.abs(C_Z - rebuilt)) / scale)
    require(resid <= rtol, f"closure identity: relative residual {resid:.3e} > {rtol:.0e}")
    return {"max_rel_residual": resid, "rtol": rtol}


def gate_g_domain(g, pinned_mask, v_blk):
    """G2. `g >= 1`, finite, and EXACTLY 1 where `v_blk == 0`.

    §3.3 condition 4. The pinned bins are checked against `v_blk` rather than against the mask the
    producer supplied, so a producer that mis-declared its own mask is caught.
    """
    g = np.asarray(g, float)
    v_blk = np.asarray(v_blk, float)
    pinned_mask = np.asarray(pinned_mask, bool)
    require(np.all(np.isfinite(g)), "g domain: non-finite entries")
    below = int(np.sum(g < G_FLOOR))
    require(below == 0, f"g domain: {below} bins below the floor g >= {G_FLOOR}")
    expected_pinned = v_blk == 0.0
    require(np.array_equal(pinned_mask, expected_pinned),
            f"g domain: declared pinned mask disagrees with v_blk == 0 in "
            f"{int(np.sum(pinned_mask != expected_pinned))} bins")
    bad = int(np.sum(g[expected_pinned] != 1.0))
    require(bad == 0, f"g domain: {bad} zero-denominator bins are not exactly 1")
    return {"n_pinned": int(expected_pinned.sum()), "n_gt_one": int(np.sum(g > 1.0)),
            "g_min": float(g.min()), "g_median": float(np.median(g)), "g_max": float(g.max())}


def gate_g_reconstruction(g_recorded, v_uni, v_blk, rtol=IDENTITY_RTOL):
    """G3. Recompute `g` from its own operands and compare with what the producer recorded.

    This is the gate the other four do not substitute for: an uninflated object (`g == 1`
    everywhere) passes closure, the floor, the zero rule and PSD, and fails only here.
    """
    g_recorded = np.asarray(g_recorded, float)
    g_rebuilt, _ = compute_g(v_uni, v_blk)
    require(g_recorded.shape == g_rebuilt.shape,
            f"g reconstruction: shape {g_recorded.shape} != {g_rebuilt.shape}")
    denom = np.maximum(np.abs(g_rebuilt), 1.0)     # g >= 1, so this is just |g|
    resid = float(np.max(np.abs(g_recorded - g_rebuilt) / denom))
    require(resid <= rtol,
            f"g reconstruction: max relative difference {resid:.3e} > {rtol:.0e} -- the recorded "
            f"g is not the one its own operands produce")
    return {"max_rel_diff": resid, "rtol": rtol}


def check_variant_coupling(v_uni_cv, v_uni_mean, mean_shift, rtol=IDENTITY_RTOL):
    """G3b -- PROPOSED, not inherited. `v_uni^cv - v_uni^mean == ms**2`.

    Catches the dropped shift of §3.3 condition 4b by an exact identity rather than by hoping the
    two variants' operands happen to differ. See the module docstring for the derivation.
    """
    a = np.asarray(v_uni_cv, float)
    b = np.asarray(v_uni_mean, float)
    ms = np.asarray(mean_shift, float)
    require(a.shape == b.shape == ms.shape,
            f"variant coupling: shapes {a.shape}, {b.shape}, {ms.shape} differ")
    lhs = a - b
    rhs = ms ** 2
    scale = max(float(np.max(np.abs(rhs))), float(np.max(np.abs(lhs))))
    if scale == 0.0:
        # Both variants identical AND the shift identically zero. Not an arithmetic failure, but a
        # zero shift means the two variants are the same object, which the two-variant requirement
        # exists to prevent. Fail closed and say which of the two facts was observed.
        raise ZContractError(
            "variant coupling: the recorded mean shift is identically zero, so the cv- and "
            "mean-centered variants are the same object. §1.6 requires both variants and "
            "§3.3 condition 14 refuses a single-variant build.")
    resid = float(np.max(np.abs(lhs - rhs)) / scale)
    require(resid <= rtol,
            f"variant coupling: max relative residual {resid:.3e} > {rtol:.0e} -- "
            f"v_uni^cv - v_uni^mean does not equal ms**2, which is the dropped-shift signature")
    return {"max_rel_residual": resid, "rtol": rtol,
            "ms_norm": float(np.linalg.norm(ms))}


def gate_symmetry_psd(C_Z, rtol=IDENTITY_RTOL, method="eigvalsh"):
    """G4. Symmetry and PSD ON THE INFLATED OBJECT.

    `method="eigvalsh"` returns the full spectrum's extremes, which is what §5.2 assumes and what
    would make §3.7d's `s_eig` a byproduct rather than a new cost. `method="cholesky"` is cheaper
    and returns no spectrum; the caller chooses, and the receipt records which ran, because "PSD
    passed" means different things about what else is now known.
    """
    C = np.asarray(C_Z, float)
    require(C.ndim == 2 and C.shape[0] == C.shape[1], f"psd: not square, shape {C.shape}")
    require(np.all(np.isfinite(C)), "psd: non-finite entries")
    scale = float(np.max(np.abs(C)))
    require(scale > 0, "psd: object is identically zero")
    asym = float(np.max(np.abs(C - C.T)) / scale)
    require(asym <= rtol, f"symmetry: relative asymmetry {asym:.3e} > {rtol:.0e}")

    Csym = 0.5 * (C + C.T)
    out = {"rel_asymmetry": asym, "rtol": rtol, "psd_method": method}
    if method == "cholesky":
        try:
            np.linalg.cholesky(Csym)
        except np.linalg.LinAlgError as exc:
            raise ZContractError(f"psd: Cholesky failed on the inflated object: {exc}") from exc
        out["eigenvalues_computed"] = False
        return out
    if method != "eigvalsh":
        raise ZContractError(f"psd: unknown method {method!r}; use 'eigvalsh' or 'cholesky'")
    w = np.linalg.eigvalsh(Csym)
    lam_min, lam_max = float(w[0]), float(w[-1])
    require(lam_min >= -rtol * max(abs(lam_max), 1.0),
            f"psd: minimum eigenvalue {lam_min:.6e} is negative beyond tolerance "
            f"(max {lam_max:.6e})")
    out.update({"eigenvalues_computed": True, "lambda_min": lam_min, "lambda_max": lam_max})
    return out


# --------------------------------------------------------------------------- the gate suite ----
def run_inflation_gates(*, C_Z, g, pinned_mask, v_uni, v_blk, cov_vert_sum, cov_residual_sum,
                        cov_lateral_sum, cov_stat, cov_ml, bands_vert, bands_residual,
                        bands_lateral, psd_method="eigvalsh", rtol=IDENTITY_RTOL):
    """Run G1-G5 for ONE centering variant and return every measured operand.

    Raises `ZContractError` on the first failure -- fail closed, and never a boolean, because a
    boolean loses which gate spoke.
    """
    results = {}
    results["G5_band_partition"] = check_band_partition(bands_vert, bands_residual, bands_lateral)
    results["G2_g_domain"] = gate_g_domain(g, pinned_mask, v_blk)
    results["G3_g_reconstruction"] = gate_g_reconstruction(g, v_uni, v_blk, rtol=rtol)
    results["G1_closure_identity"] = gate_closure_identity(
        C_Z, g, cov_vert_sum, cov_residual_sum, cov_lateral_sum, cov_stat, cov_ml, rtol=rtol)
    results["G4_symmetry_psd"] = gate_symmetry_psd(C_Z, rtol=rtol, method=psd_method)
    return results
