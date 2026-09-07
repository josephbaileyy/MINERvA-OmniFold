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

    ⚠ SCOPE, stated here because a round-3 note claimed reach this does not have. `v_uni` is an
    ARGUMENT. This gate catches a `g` that disagrees with the operands it was handed; it cannot
    catch a wrong `v_uni`, because it never sees another one to disagree with. In particular a
    `v_uni^cv` that dropped the `+ mean_shift**2` term is self-consistent with the `g` derived
    from it, and this gate passes -- at any shift size.

    §1.3b's requirement is the stronger one: derive `v_uni^cv` from `diag(C_unified)`,
    `diag(C_blocksum)` and `hJointMeanShift` per variant, *"because `g^mean` and `g^cv` differ
    only through the `+ mean_shift²` term and a validator that reconstructs one and reuses it for
    the other cannot detect a dropped shift"*.

    ⚠ THAT GATE NOW EXISTS: `gate_raw_operand_reconstruction` below, added under Joseph's
    2026-09-07 integration authorization. It does not supersede this function -- this one is still
    the per-variant check that a recorded `g` matches the operands it was handed -- but the
    §1.3b obligation is discharged there and no longer left to the caller.
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
    """G3b -- PROPOSED, not inherited. The forward identity `v_uni^cv == v_uni^mean + ms**2`.

    ⚠ REVIEW FINDING 4 REBUILT THIS. Two defects, both of which rejected CORRECT inputs:

      * it raised whenever `ms` was identically zero. A zero shift makes the two variants
        legitimately equal -- that is arithmetic, not a defect. "Both variants must exist" is a
        real requirement (§3.3 condition 14) but it is a requirement about the BUILD, and
        enforcing it from inside an algebraic identity made a valid operand set unusable.
      * it compared the SUBTRACTION `v_cv - v_mean` against `ms**2`, which cancels. Measured on a
        correctly constructed input -- `v_mean = 1`, `ms = 1e-5`, `v_cv = v_mean + ms**2` -- the
        subtraction loses the low bits and the relative residual came out `8.3e-8`, eighty times
        the tolerance. The check failed on exactly the input it was written to accept.

    The repair is to test the identity FORWARD and to scale the allowance by the OPERANDS rather
    than by their difference, elementwise.

    ⚠ AND ITS DISCRIMINATING POWER IS REPORTED, because it is limited and silence about that would
    be worse than the gate's absence. When `ms**2` falls below the CONFIGURED allowance
    `rtol * (|v_cv| + |v_mean|)`, the identity cannot distinguish a correct build from a dropped
    shift. The gate then PASSES and reports `discriminating=False`, so a caller cannot read it as
    assurance.

    ⚠ ROUND 3 CORRECTED BOTH HALVES OF THAT PARAGRAPH.

    *The threshold is the tolerance, not the arithmetic.* The earlier text said "below the float64
    resolution of `v_uni`", which is a different and far narrower claim. Measured at `v_mean = 1`,
    `ms = 1e-5`: `ms**2 = 1e-10` is **4.5e5 ulps** and entirely representable. It is simply
    smaller than the `2e-9` allowance this gate is configured with. The resolution regime needs
    `ms < 1.5e-8`; the tolerance regime -- the one that actually binds -- needs `ms < 4.5e-5`,
    some three thousand times wider. Naming the rarer mechanism understated how often the gate is
    blind.

    ⚠ ROUND 4: the illustration used for that was itself wrong. `(1 + 1e-10) - 1` does NOT return
    `1e-10` exactly; it returns `1.000000082740371e-10`, a relative error of `8.3e-8`. The
    subtraction is exact (Sterbenz); the loss is in rounding `1 + 1e-10` to a double, `0.037` ulps
    of `1.0`. That `8.3e-8` is the very residual round-2 finding 4 measured -- the same
    cancellation, which is why this function tests the identity forward. The point it was offered
    for survives: `ms**2` is recovered to seven significant digits, so this is nowhere near a
    representability limit.

    *And "rely on G3" was unsound.* Measured on that same input with the shift dropped: this gate
    passes non-discriminating and **G3 passes too**. G3 reconstructs `g` from the RECORDED `v_uni`,
    so a `v_uni^cv` built without the shift is self-consistent with the `g` derived from it and
    there is nothing for G3 to disagree with -- not merely in the small-signal regime, but at any
    shift size. G3 is the gate for a MIS-RECORDED `g`; it was never the gate for a mis-built
    `v_uni`, and pointing at it offered assurance that does not exist.

    ⚠ ROUND 4 AGAIN, AND THE REPLACEMENT POINTER WAS ALSO WRONG. The previous text sent the
    reader to §3.3 condition 14, "which checks the operands". It does not. Condition 14 reads in
    full: *"Only one centering variant was produced, or `--out` was defaulted for either."* That
    is a check on whether both variants were PRODUCED and whether an output path was defaulted.
    It never looks at the operands and it cannot detect a dropped shift. Twice now the honest
    finding -- this gate is blind here -- has been softened by naming some other check that turns
    out not to cover it, which is worse than the blindness, because a named fallback stops the
    reader looking.

    So: **when `discriminating=False` the dropped shift is UNTESTED by this check.**

    §1.3b's independent reconstruction from the RAW THROW OPERANDS is now implemented as
    `gate_raw_operand_reconstruction`, and it IS the gate for a mis-built `v_uni`: it derives
    `v_uni^cv` from `v_uni^mean + ms**2` rather than accepting a stored array, so a producer that
    dropped the shift disagrees with it.

    ⚠ BUT IT IS BLIND IN THE SAME REGIME, AND SAYING OTHERWISE WOULD REPEAT THE ERROR THIS
    PARAGRAPH HAS ALREADY MADE TWICE. Both checks compare a difference of order `ms**2` against a
    relative tolerance on operands of order `v_uni`. When `ms**2` falls under that tolerance, the
    reconstruction rebuilds a `g^cv` indistinguishable from `g^mean` and passes too. It reports
    its own `discriminating` flag for exactly this reason. Below the floor NOTHING here detects a
    dropped shift, and the only remedy is operand provenance, not another gate.
    """
    a = np.asarray(v_uni_cv, float)
    b = np.asarray(v_uni_mean, float)
    ms = np.asarray(mean_shift, float)
    require(a.shape == b.shape == ms.shape,
            f"variant coupling: shapes {a.shape}, {b.shape}, {ms.shape} differ")
    require(np.all(np.isfinite(a)) and np.all(np.isfinite(b)) and np.all(np.isfinite(ms)),
            "variant coupling: non-finite operand")

    predicted = b + ms ** 2
    # Elementwise allowance from the magnitudes actually entering the sum -- not from the
    # difference, which is what cancelled.
    allow = rtol * (np.abs(a) + np.abs(b) + ms ** 2)
    dev = np.abs(a - predicted)
    worst = int(np.argmax(dev - allow)) if dev.size else 0
    ok = bool(np.all(dev <= allow))
    signal, noise = ms ** 2, rtol * (np.abs(a) + np.abs(b))
    discriminating = bool(np.any(signal > noise))
    require(ok,
            f"variant coupling: v_uni^cv != v_uni^mean + ms**2 at bin {worst} "
            f"(deviation {float(dev[worst]):.6e} > allowance {float(allow[worst]):.6e}) -- "
            f"the dropped-shift signature")
    return {"max_deviation": float(dev.max()) if dev.size else 0.0,
            "max_allowance": float(allow.max()) if allow.size else 0.0,
            "rtol": rtol, "ms_norm": float(np.linalg.norm(ms)),
            "discriminating": discriminating,
            "n_bins_where_signal_exceeds_noise": int(np.sum(signal > noise)),
            "note": ("PASSED WITHOUT DISCRIMINATING: ms**2 is below the configured allowance "
                     "rtol*(|v_cv|+|v_mean|) in every bin, so a dropped shift would look "
                     "identical here. This is a tolerance limit, not a representability one. The "
                     "dropped shift is UNTESTED by this check and NOTHING IN THIS MODULE covers "
                     "it: G3 reconstructs g from the recorded v_uni, so a v_uni built without the "
                     "shift is self-consistent, and §3.3 condition 14 checks only that both "
                     "variants were produced and that --out was not defaulted. §1.3b's "
                     "independent reconstruction from the raw throw operands remains required."
                     if not discriminating else "discriminating")}


def gate_raw_operand_reconstruction(*, g_recorded, diag_c_unified_mean, diag_c_blocksum,
                                    joint_mean_shift, diag_c_unified_cv=None,
                                    rtol=IDENTITY_RTOL):
    """§1.3b's reconstruction gate: rebuild `g^c` from the THROW OPERANDS, both variants, and
    compare elementwise against what the producer recorded.

    Joseph, 2026-09-07, authorized this integration. §1.3b states the requirement and why the
    other four gates need it:

        *"the validator recomputes `g^c` from the throw operands themselves -- `diag(C_unified)`,
        `diag(C_blocksum)`, and `hJointMeanShift` for the CV-centered variant -- by §1.3a's
        formula, for each variant separately, and compares elementwise against the `g^c` the
        producer wrote. Reading the producer's `hInflation_g` and checking it against itself is
        not this gate. Both variants must be reconstructed independently, because `g^mean` and
        `g^cv` differ only through the `+ mean_shift²` term and a validator that reconstructs one
        and reuses it for the other cannot detect a dropped shift."*

    WHAT MAKES THIS DIFFERENT FROM `gate_g_reconstruction`, which is the whole point: that one
    takes `v_uni` as an ARGUMENT, so a `v_uni^cv` built without the shift is self-consistent with
    the `g` derived from it and passes. Here `v_uni^cv` is **DERIVED** -- `v_uni^mean + ms**2` --
    so the producer never gets to supply the quantity under test. A dropped shift then shows up as
    a disagreement in `g^cv` and in `g^cv` only, which is also how the report names it.

    BOTH VARIANTS ARE REQUIRED. Not as a formality: a caller who passes only `mean` gets the
    reuse failure §1.3b names, and there is no way for this function to notice from one variant.
    `diag_c_unified_cv` is OPTIONAL and is CROSS-CHECKED, never substituted -- if the producer
    stored its own cv diagonal, disagreement with the derived one is reported as
    `stored_cv_deviation` and refused, but the reconstruction itself always uses the derived
    value. A stored operand cannot be allowed to certify itself.

    ⚠ ITS DISCRIMINATING POWER IS REPORTED AND IS LIMITED, in exactly the regime
    `check_variant_coupling` documents. The `mean`/`cv` reconstructions differ only through
    `ms**2`; where that is below `rtol * v_uni`, a dropped shift rebuilds to the same `g` and this
    gate passes. It then reports `discriminating=False`. There is no gate behind this one -- below
    that floor the dropped shift is undetectable by any tolerance-based identity here, and the
    remedy is the operands' provenance.

    Returns the measured operands; raises `ZContractError` on the first disagreement.
    """
    require(isinstance(g_recorded, dict),
            "raw-operand reconstruction: g_recorded must be a {variant: array} mapping")
    missing = [v for v in ("mean", "cv") if v not in g_recorded]
    require(not missing,
            f"raw-operand reconstruction: variant(s) {missing} absent. §1.3b requires BOTH "
            f"variants be reconstructed independently -- one variant cannot expose the reuse "
            f"fault this gate exists to catch.")

    v_uni_mean = np.asarray(diag_c_unified_mean, float)
    v_blk = np.asarray(diag_c_blocksum, float)
    ms = np.asarray(joint_mean_shift, float)
    require(v_uni_mean.shape == v_blk.shape == ms.shape,
            f"raw-operand reconstruction: operand shapes differ -- diag(C_unified^mean) "
            f"{v_uni_mean.shape}, diag(C_blocksum) {v_blk.shape}, mean shift {ms.shape}")
    for name, arr in (("diag(C_unified^mean)", v_uni_mean), ("diag(C_blocksum)", v_blk),
                      ("hJointMeanShift", ms)):
        require(np.all(np.isfinite(arr)), f"raw-operand reconstruction: {name} is not finite")

    # THE DERIVATION. `v_uni^cv` is computed, never accepted -- see the docstring.
    derived = {"mean": v_uni_mean, "cv": v_uni_mean + ms ** 2}

    stored_cv_deviation = None
    if diag_c_unified_cv is not None:
        stored = np.asarray(diag_c_unified_cv, float)
        require(stored.shape == v_uni_mean.shape,
                f"raw-operand reconstruction: stored diag(C_unified^cv) shape {stored.shape} "
                f"!= {v_uni_mean.shape}")
        allow = rtol * (np.abs(stored) + np.abs(derived["cv"]))
        dev = np.abs(stored - derived["cv"])
        stored_cv_deviation = float(dev.max()) if dev.size else 0.0
        require(bool(np.all(dev <= allow)),
                f"raw-operand reconstruction: the STORED diag(C_unified^cv) disagrees with "
                f"v_uni^mean + ms**2 by {stored_cv_deviation:.6e} at worst. The stored operand is "
                f"cross-checked, never substituted, so this is a defect in the operand set itself.")

    per_variant, offenders = {}, []
    for variant in ("mean", "cv"):
        rebuilt, pinned = compute_g(derived[variant], v_blk)
        recorded = np.asarray(g_recorded[variant], float)
        if recorded.shape != rebuilt.shape:
            raise ZContractError(
                f"raw-operand reconstruction: recorded g^{variant} shape {recorded.shape} != "
                f"rebuilt {rebuilt.shape}")
        denom = np.maximum(np.abs(rebuilt), 1.0)      # g >= 1, so this is just |g|
        resid = np.abs(recorded - rebuilt) / denom
        worst = int(np.argmax(resid)) if resid.size else 0
        per_variant[variant] = {
            "max_rel_diff": float(resid.max()) if resid.size else 0.0,
            "worst_bin": worst,
            "n_pinned": int(pinned.sum()),
            "n_inflated": int(np.sum(rebuilt > 1.0)),
        }
        if not bool(np.all(resid <= rtol)):
            offenders.append(f"g^{variant} (max relative difference "
                             f"{float(resid.max()):.6e} at bin {worst})")

    # Can a dropped shift even be seen here? Same floor as `check_variant_coupling`, same reason.
    signal = ms ** 2
    noise = rtol * (np.abs(derived["cv"]) + np.abs(derived["mean"]))
    discriminating = bool(np.any(signal > noise))

    if offenders:
        raise ZContractError(
            f"raw-operand reconstruction FAILED for {offenders}, tolerance {rtol:.0e}. The "
            f"recorded g is not what §1.3a's formula produces from diag(C_unified), "
            f"diag(C_blocksum) and hJointMeanShift. A disagreement on g^cv ALONE is the "
            f"dropped-mean-shift signature; a disagreement on both is a mis-scoped or uninflated "
            f"g. (This gate could{'' if discriminating else ' NOT'} discriminate a dropped shift "
            f"on these operands.)")

    return {
        "per_variant": per_variant,
        "rtol": rtol,
        "ms_norm": float(np.linalg.norm(ms)),
        "stored_cv_cross_checked": diag_c_unified_cv is not None,
        "stored_cv_deviation": stored_cv_deviation,
        "discriminating": discriminating,
        "n_bins_where_signal_exceeds_noise": int(np.sum(signal > noise)),
        "note": ("PASSED WITHOUT DISCRIMINATING: ms**2 is below rtol*(v_uni^cv + v_uni^mean) in "
                 "every bin, so a g^cv built from a dropped shift rebuilds to the same values. "
                 "There is NO further gate behind this one -- treat the dropped shift as "
                 "UNTESTED and rely on the operands' provenance, not on another check."
                 if not discriminating else "discriminating"),
    }


def gate_symmetry_psd(C_Z, rtol=IDENTITY_RTOL):
    """G4. Symmetry and PSD ON THE INFLATED OBJECT, scaled by the object and nothing else.

    ⚠ REVIEW FINDING 2, AND IT IS THE MOST EMBARRASSING ONE IN THIS MODULE. The first version
    tested `lam_min >= -rtol * max(abs(lam_max), 1.0)`. That `max(..., 1.0)` is an ABSOLUTE FLOOR,
    and Z's covariances live at `~1e-38`, so the floor dominated every real comparison and the gate
    admitted any negative eigenvalue smaller than `1e-9`. Measured: `1e-76 * [[1,2],[2,1]]` has
    eigenvalues `-1e-76` and `3e-76` -- materially negative, a third of the spectrum -- and it
    passed.

    **This is the same defect, character for character, that §3.1a of the specification identifies
    as "the whole defect" in `unified_throw_cov.py:517`'s `1e-12 * max(||base||, 1.0)`.** The gate
    written to enforce that finding reproduced it. An absolute floor inside a relative test is this
    campaign's signature bug and it survived because the fixture was `O(1)`.

    The repair is the one §3.1a prescribes: delete the clamp. `lam_min >= -rtol * lam_max` is
    scale-free -- multiply `C` by any `c > 0` and both sides scale together -- so the test is
    invariant under rescaling, which is the property the fixtures now assert directly.

    CHOLESKY IS GONE, and not because it is slow. It tests POSITIVE DEFINITENESS, which is
    strictly stronger than PSD: it refuses any matrix with a null direction. A covariance may
    legitimately have one, and nothing in §1.3a guarantees the assembled object has full rank, so a
    Cholesky gate could refuse a correct Z -- a guard that fires on a correct run. Offering it as
    an equivalent PSD method was wrong. (An earlier draft of this note claimed the object IS
    singular by construction because the zero-denominator bins zero a row of the vertical block
    sum. That is not right either: the residual, lateral, stat and ML terms are added on top and
    generally restore rank. The rank of Z is not established here and no gate depends on it.)
    """
    C = np.asarray(C_Z, float)
    require(C.ndim == 2 and C.shape[0] == C.shape[1], f"psd: not square, shape {C.shape}")
    require(np.all(np.isfinite(C)), "psd: non-finite entries")
    scale = float(np.max(np.abs(C)))
    require(scale > 0, "psd: object is identically zero")
    asym = float(np.max(np.abs(C - C.T)) / scale)
    require(asym <= rtol, f"symmetry: relative asymmetry {asym:.3e} > {rtol:.0e}")

    w = np.linalg.eigvalsh(0.5 * (C + C.T))
    lam_min, lam_max = float(w[0]), float(w[-1])
    require(lam_max > 0, f"psd: no positive eigenvalue (max {lam_max:.6e})")
    # Scale-free. No absolute floor, deliberately -- see the docstring.
    require(lam_min >= -rtol * lam_max,
            f"psd: minimum eigenvalue {lam_min:.6e} is negative beyond tolerance, "
            f"{abs(lam_min) / lam_max:.3e} of the maximum {lam_max:.6e} > {rtol:.0e}")
    return {"rel_asymmetry": asym, "rtol": rtol, "psd_method": "eigvalsh",
            "eigenvalues_computed": True, "lambda_min": lam_min, "lambda_max": lam_max,
            "neg_fraction_of_max": abs(min(lam_min, 0.0)) / lam_max}


# --------------------------------------------------------------------------- the gate suite ----
def run_inflation_gates(*, C_Z, g, pinned_mask, v_uni, v_blk, cov_vert_sum, cov_residual_sum,
                        cov_lateral_sum, cov_stat, cov_ml, bands_vert, bands_residual,
                        bands_lateral, band_inventory, rtol=IDENTITY_RTOL):
    """Run G1-G5 for ONE centering variant and return every measured operand.

    Raises `ZContractError` on the first failure -- fail closed, and never a boolean, because a
    boolean loses which gate spoke. `band_inventory` is required: see `check_band_partition`.
    """
    results = {}
    results["G5_band_partition"] = check_band_partition(bands_vert, bands_residual, bands_lateral,
                                                        band_inventory)
    results["G2_g_domain"] = gate_g_domain(g, pinned_mask, v_blk)
    results["G3_g_reconstruction"] = gate_g_reconstruction(g, v_uni, v_blk, rtol=rtol)
    results["G1_closure_identity"] = gate_closure_identity(
        C_Z, g, cov_vert_sum, cov_residual_sum, cov_lateral_sum, cov_stat, cov_ml, rtol=rtol)
    results["G4_symmetry_psd"] = gate_symmetry_psd(C_Z, rtol=rtol)
    return results


def run_pair_gates(*, g_recorded, diag_c_unified_mean, diag_c_blocksum, joint_mean_shift,
                   diag_c_unified_cv=None, rtol=IDENTITY_RTOL):
    """The gates that span BOTH centering variants, which `run_inflation_gates` cannot see.

    `run_inflation_gates` runs G1-G5 for ONE variant. §1.3b's reconstruction and the variant
    coupling are properties of the PAIR, so a per-variant runner structurally cannot host them --
    which is why the reconstruction obligation went undischarged for four review rounds while
    five gates reported green.
    """
    results = {}
    results["G3R_raw_operand_reconstruction"] = gate_raw_operand_reconstruction(
        g_recorded=g_recorded, diag_c_unified_mean=diag_c_unified_mean,
        diag_c_blocksum=diag_c_blocksum, joint_mean_shift=joint_mean_shift,
        diag_c_unified_cv=diag_c_unified_cv, rtol=rtol)
    if diag_c_unified_cv is not None:
        results["G3b_variant_coupling"] = check_variant_coupling(
            diag_c_unified_cv, diag_c_unified_mean, joint_mean_shift, rtol=rtol)
    return results
