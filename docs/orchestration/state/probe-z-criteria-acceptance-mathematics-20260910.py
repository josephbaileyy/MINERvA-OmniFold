#!/usr/bin/env python3
"""Probe for RECOMMENDATION-20260910-z-scientific-acceptance-criteria.md.

Every number the recommendation labels PROVEN BOUND or MEASURED that is arithmetic rather than a
file read is produced here, so it can be re-run rather than believed. No compute, no cluster, no
ROOT, no adoption. Read-only apart from stdout.

Run:  python3 docs/orchestration/state/probe-z-criteria-acceptance-mathematics-20260910.py

WHAT EACH SECTION ESTABLISHES, and what it does NOT
---------------------------------------------------
1  rho bound          the sharp two-sided bound on the consumed quadratic form. A THEOREM, checked
                      numerically in both directions with a tightness witness and three controls.
                      It is not a statement about any real covariance.
1b projection        rho is non-increasing under any linear projection of the covariance. A THEOREM,
                      checked with a tightness witness and a control. This is why a rho measured on
                      the 5D trunk bounds rho on every marginal, so the BOUND does not depend on
                      which projection map is designated -- but the reported chi2, ndf and retained
                      rank still do, so the designation is still a precondition.
2  rho_crit           the closed-form inversion that makes the significance criterion
                      threshold-parametric. Synthetic (chi2_0, ndf) PLACEHOLDERS -- no chi2 for any
                      MINERvA projection exists in this tree, and none is asserted here.
3  F7 decision margin MEASURED, from G's committed receipt, reusing `uq_math` rather than restating
                      its formula. A property of G, TRANSFERRED to Z with the direction of the
                      difference not established.
4  normalizer spread  MEASURED. Why `sqrt(Tr C)` is not an admissible null normalizer: three
                      committed sqrt-traces exist for the same null.
5  rev-7 arithmetic   MEASURED. Reproduces the withdrawn `5.00e-41` from its actual operand, which
                      is `values.tex`'s never-printed macro and not G's measured mean shift.

`uq_math` is imported, never restated: a rule retyped is a second implementation.
"""
from __future__ import annotations

import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ND = os.path.join(_HERE, "..", "..", "..", "nd-unfolding")
# Appended, NOT inserted at position 0: an entry at sys.path[0] shadows whatever the caller's
# environment already resolved (OI-136). Nothing here needs to outrank the caller.
sys.path.append(os.path.normpath(_ND))

SEED = 20260910

# ----------------------------------------------------------------- committed operands, cited ----
# nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json, files.A1_candidate_meancentered.parameters
G_MEAN_SHIFT_NORM = 1.878696733368378e-38      # upstream_joint_mean_shift_norm
G_NULL_NORM = 5.8223488501140625e-50           # upstream_fixed_seed_null_norm
G_N_THROWS = 160                               # upstream_n_throws
G_SQRT_TR_NEW = 5.269625166386846e-38          # sqrt_tr_new, the inflated total
G_SQRT_TR_OLD = 4.357790406860002e-38          # sqrt_tr_old, the block-sum footing
# docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md:196 -- the unified throw's own
X_SQRT_TR_UNIFIED = 4.443674e-38
# docs/analysis-note/values.tex:115, `\gbdtFiveMeanShift`. Measured to be defined and used in no
# other .tex -- and ⚠ DO NOT conclude it has no use: `PROCEDURE-gbdtFive-macro-update.md` stages all
# four macros for a note update GATED ON ADOPTION. It is a blocked pipeline, not a finished one, and
# reading it the other way makes the acceptance criterion depend on the adoption it gates. What this
# constant is used for below is narrower: it is the operand rev. 7's withdrawn limit was built from.
VALUES_TEX_MEAN_SHIFT = 1.65e-38


def rho(C0: np.ndarray, Ck: np.ndarray) -> float:
    """Relative spectral perturbation of `Ck` from `C0`, measured in `C0`'s own metric.

    ``rho = || C0^(-1/2) (Ck - C0) C0^(-1/2) ||_2``

    Requires `C0` positive definite. Symmetrized before the norm because the two-sided product of
    symmetric matrices is symmetric only up to round-off.
    """
    w, V = np.linalg.eigh(C0)
    if w[0] <= 0:
        raise ValueError(f"baseline covariance is not positive definite: lambda_min = {w[0]!r}")
    inv_sqrt = V @ np.diag(w ** -0.5) @ V.T
    E = inv_sqrt @ (Ck - C0) @ inv_sqrt
    return float(np.linalg.norm((E + E.T) / 2.0, 2))


def _chi2(C: np.ndarray, d: np.ndarray) -> float:
    """The consumed quantity, in the consumer's own form: `d @ pinv(C) @ d`."""
    return float(d @ np.linalg.pinv(C) @ d)


def section_1_rho_bound(trials: int = 4000, vectors: int = 30) -> None:
    """THEOREM. For C0 > 0, Ck > 0 and rho = rho(C0, Ck) < 1, for EVERY data vector d:

        chi2_0 / (1 + rho)  <=  chi2_k  <=  chi2_0 / (1 - rho)

    Proof: write Ck = C0^(1/2) (I + E) C0^(1/2) with E = C0^(-1/2)(Ck - C0)C0^(-1/2), symmetric with
    ||E||_2 = rho. Then chi2_k = u'(I+E)^(-1)u with u = C0^(-1/2)d, and the eigenvalues of
    (I+E)^(-1) lie in [1/(1+rho), 1/(1-rho)]. The bound is attained when u aligns with E's extreme
    eigenvector, so it is SHARP -- which the tightness witnesses below confirm rather than assume.
    """
    rng = np.random.default_rng(SEED)
    worst_lo, worst_hi = 1.0, 1.0
    tight_lo, tight_hi = 0.0, 0.0
    checked = 0
    for _ in range(trials):
        n = int(rng.integers(2, 9))
        A = rng.normal(size=(n, n))
        C0 = A @ A.T + n * np.eye(n)
        B = rng.normal(size=(n, n))
        Ck = C0 + 0.02 * (B + B.T)
        if np.linalg.eigvalsh(Ck)[0] <= 0:
            continue
        r = rho(C0, Ck)
        if r >= 1.0:
            continue
        for _ in range(vectors):
            d = rng.normal(size=n)
            c0, ck = _chi2(C0, d), _chi2(Ck, d)
            lo, hi = c0 / (1.0 + r), c0 / (1.0 - r)
            worst_lo = min(worst_lo, ck / lo)
            worst_hi = max(worst_hi, ck / hi)
            tight_lo = max(tight_lo, lo / ck)
            tight_hi = max(tight_hi, ck / hi)
            checked += 1
    print("1. THE rho BOUND ON THE CONSUMED QUADRATIC FORM")
    print(f"   {checked} (covariance pair, data vector) evaluations")
    print(f"   lower bound holds: min(chi2_k / lo) = {worst_lo:.12f}   must be >= 1")
    print(f"   upper bound holds: max(chi2_k / hi) = {worst_hi:.12f}   must be <= 1")
    print(f"   sharpness witnessed: lo/chi2_k reaches {tight_lo:.6f}, chi2_k/hi reaches {tight_hi:.6f}")
    assert worst_lo >= 1.0 - 1e-9, "LOWER BOUND VIOLATED"
    assert worst_hi <= 1.0 + 1e-9, "UPPER BOUND VIOLATED"

    # CONTROL A -- silent on good. No perturbation must give exactly zero.
    I2 = np.eye(2)
    r_id = rho(I2, I2)
    print(f"   control A, silent on good:  rho(I, I) = {r_id:.3e}   must be 0")
    assert r_id == 0.0

    # CONTROL B -- fires where the two diagonal-only statistics are exactly blind. This is SPEC
    # 3.7d's own counterexample: identical diagonal, identical trace, 0.9 correlation.
    Corr = np.array([[1.0, 0.9], [0.9, 1.0]])
    s_agg = abs(np.sqrt(np.trace(Corr)) - np.sqrt(np.trace(I2))) / np.sqrt(np.trace(I2))
    s_med = abs(np.median(np.sqrt(np.diag(Corr))) - 1.0) / 1.0
    r_corr = rho(I2, Corr)
    d = np.array([1.0, 0.0])
    print(f"   control B, SPEC 3.7d counterexample: s_agg = {s_agg:.1f}, s_med = {s_med:.1f}, "
          f"rho = {r_corr:.4f}")
    print(f"      the quantity they are blind to: chi2 moves {_chi2(I2, d):.4f} -> "
          f"{_chi2(Corr, d):.4f}, and rho's bound admits it "
          f"[{_chi2(I2, d) / (1 + r_corr):.4f}, {_chi2(I2, d) / (1 - r_corr):.4f}]")
    assert s_agg == 0.0 and s_med == 0.0, "the counterexample no longer isolates the blindness"
    assert r_corr > 0.5, "rho failed to see a pure off-diagonal change"

    # CONTROL C -- the OPPOSITE-DIRECTION bad, which a one-sided check waves through: a spectrum
    # change that eigenvalue summaries CANNOT see because the spectrum is identical. rho must
    # report a LARGE perturbation, and rho >= 1 must be reported as vacuous rather than as a pass.
    C_a, C_b = np.diag([1.0, 4.0]), np.diag([4.0, 1.0])
    r_swap = rho(C_a, C_b)
    ev_a, ev_b = np.linalg.eigvalsh(C_a), np.linalg.eigvalsh(C_b)
    print(f"   control C, identical spectra {ev_a} and {ev_b}, condition number identical:")
    print(f"      chi2 moves {_chi2(C_a, d):.4f} -> {_chi2(C_b, d):.4f} (factor 4); "
          f"rho = {r_swap:.4f} >= 1, so the criterion reports INCONCLUSIVE, never MET")
    assert np.allclose(ev_a, ev_b), "control C no longer holds the spectrum fixed"
    assert r_swap >= 1.0, "rho understated a factor-4 change in the consumed form"
    print()


def section_1b_projection_monotonicity(trials: int = 3000) -> None:
    """THEOREM. For any linear map M with `M C0 M'` nonsingular:

        rho(M C0 M', M Ck M')  <=  rho(C0, Ck)

    Proof: let B = M C0^(1/2), so M C0 M' = BB' and M(Ck-C0)M' = B E B' with E as in section 1.
    Put P = B'(BB')^(-1/2); then P'P = I, so P has orthonormal columns and
    rho_proj = ||P' E P||_2 <= ||E||_2 = rho.

    WHAT IT BUYS, and what it does NOT: a rho measured on the 5D trunk bounds rho on every
    projection at once, so the BOUND is independent of which projection map is designated. The
    reported significance is NOT -- chi2_0, ndf and the retained rank all depend on M.
    """
    rng = np.random.default_rng(SEED + 1)
    worst, n_checked, n_tight = 0.0, 0, 0
    for _ in range(trials):
        nh = int(rng.integers(3, 12))
        nl = int(rng.integers(1, nh))
        A = rng.normal(size=(nh, nh))
        C0 = A @ A.T + nh * np.eye(nh)
        B = rng.normal(size=(nh, nh))
        Ck = C0 + 0.05 * (B + B.T)
        if np.linalg.eigvalsh(Ck)[0] <= 0:
            continue
        # M of the shape `project_cov_nd` builds: each high cell maps to EXACTLY ONE low bin,
        # with a positive width-product weight (project_cov_nd.py:2-11).
        M = np.zeros((nl, nh))
        M[rng.integers(0, nl, size=nh), np.arange(nh)] = rng.uniform(0.1, 3.0, size=nh)
        if np.linalg.matrix_rank(M) < nl:
            continue
        ratio = rho(M @ C0 @ M.T, M @ Ck @ M.T) / rho(C0, Ck)
        worst = max(worst, ratio)
        n_checked += 1
        if ratio > 0.999:
            n_tight += 1
    print("1b. rho IS NON-INCREASING UNDER PROJECTION")
    print(f"   {n_checked} (covariance, projection) pairs, sparse one-cell-to-one-bin M")
    print(f"   max rho_proj / rho_5D = {worst:.12f}   must be <= 1")
    print(f"   tightness witnesses (ratio > 0.999): {n_tight}")
    assert worst <= 1.0 + 1e-9, "PROJECTION MONOTONICITY VIOLATED"
    assert n_tight > 0, "no tightness witness: the bound may be loose and the check uninformative"

    # CONTROL -- M = I is not a projection, so the ratio must be EXACTLY 1, not merely <= 1.
    A = rng.normal(size=(6, 6))
    C0 = A @ A.T + 6 * np.eye(6)
    B = rng.normal(size=(6, 6))
    Ck = C0 + 0.05 * (B + B.T)
    I6 = np.eye(6)
    ratio_id = rho(I6 @ C0 @ I6.T, I6 @ Ck @ I6.T) / rho(C0, Ck)
    print(f"   control, M = I (no projection): ratio = {ratio_id:.12f}   must be exactly 1")
    assert abs(ratio_id - 1.0) < 1e-12
    print()


def section_2_rho_crit() -> None:
    """The closed-form inversion. SYNTHETIC PLACEHOLDERS -- no real chi2 exists in this tree.

    The consumer's map (`eavail_generator_significance.py:111-113`) is
    ``p = chi2.sf(chi2, ndf)`` then ``z = norm.isf(p / 2.0)``, which is strictly increasing in
    chi2. Composing it with section 1's bound gives the significance interval in closed form, and
    inverting it gives the largest rho a claim at threshold T survives:

        claim  z > T :  rho_crit = chi2_0 / chi2_crit(T) - 1
        claim  z < T :  rho_crit = 1 - chi2_0 / chi2_crit(T)

    with ``chi2_crit(T) = chi2.isf(2 * norm.sf(T), ndf)``. So the criterion needs no tolerance
    supplied in advance: it needs T, and reports rho_crit(T) for any T.
    """
    try:
        from scipy import stats
    except ImportError:
        print("2. rho_crit -- SKIPPED, scipy is not importable in this interpreter\n")
        return

    def z_of(chi2: float, ndf: int) -> float:
        return float(stats.norm.isf(stats.chi2.sf(chi2, ndf) / 2.0))

    def chi2_crit(T: float, ndf: int) -> float:
        return float(stats.chi2.isf(2.0 * stats.norm.sf(T), ndf))

    print("2. THE CLOSED-FORM CRITICAL rho  (synthetic chi2_0/ndf placeholders, NOT measurements)")
    print("   CONTROLLED: z_0 fixed at 4.0 and T at 3.0, so ONLY ndf varies.")
    print("     ndf     chi2_0    rho_crit   z at the edge   (z_0-T)*sqrt(2/ndf)")
    for ndf in (7, 42, 247, 4825, 10694):
        c0 = chi2_crit(4.0, ndf)
        rc = c0 / chi2_crit(3.0, ndf) - 1.0
        edge = z_of(c0 / (1.0 + rc), ndf)
        asym = 1.0 * np.sqrt(2.0 / ndf)
        print(f"   {ndf:6d} {c0:10.2f}  {rc:9.6f}   {edge:12.6f}   {asym:19.6f}")
        assert abs(edge - 3.0) < 1e-6, "rho_crit is not the exact edge"
    print("   CONTROLLED: ndf fixed at 42 and T at 3.0, so ONLY the margin varies.")
    print("     z_0     chi2_0    rho_crit")
    for z0 in (3.5, 4.0, 5.0, 6.0):
        c0 = chi2_crit(z0, 42)
        print(f"   {z0:6.1f} {c0:10.2f}  {c0 / chi2_crit(3.0, 42) - 1.0:9.6f}")
    print("   Both scans are one-variable-at-a-time. The asymptote rho_crit ~ (z_0-T)*sqrt(2/ndf)")
    print("   is the practical content: a large-ndf projection admits a SMALL perturbation.")
    print()


def section_3_f7_margin() -> None:
    """MEASURED on G, TRANSFERRED to Z. The only non-formatting decision channel found in the tree.

    F7 (`uq_math.f7_cv_centered_required`) is a real branch: it decides whether the CV-centered
    variant is additionally mandatory. Its operand is ||mean_shift||, and hJointMeanShift is
    "joint throw mean minus CV" (`unified_throw_cov.py:575`), so a CV perturbation dx moves the
    mean shift by exactly -dx and |||ms'|| - ||ms||| <= ||dx|| by the triangle inequality. That
    inequality is a PROVEN BOUND; the margin below is a MEASUREMENT on G.
    """
    import uq_math

    print("3. THE F7 DECISION MARGIN  (MEASURED on G; TRANSFERRED to Z)")
    print(f"   k = uq_math.F7_FLOOR_MULTIPLE = {uq_math.F7_FLOOR_MULTIPLE} (imported, strict >)")
    for label, sqrt_tr in (("sqrt_tr_new, inflated total", G_SQRT_TR_NEW),
                           ("sqrt_tr_old, block footing ", G_SQRT_TR_OLD)):
        floor = uq_math.mean_shift_sampling_floor(sqrt_tr, G_N_THROWS)
        ratio = uq_math.mean_shift_over_floor(G_MEAN_SHIFT_NORM, sqrt_tr, G_N_THROWS)
        required = uq_math.f7_cv_centered_required(G_MEAN_SHIFT_NORM, sqrt_tr, G_N_THROWS)
        dx_flip = G_MEAN_SHIFT_NORM - uq_math.F7_FLOOR_MULTIPLE * floor
        print(f"   {label}: floor = {floor:.6e}, ratio = {ratio:.6f} floors, "
              f"cv_centered_required = {required}")
        print(f"      ||dx|| that would flip the F7 branch (trace held) = {dx_flip:.6e}")
        print(f"      as a multiple of G's observed null: {dx_flip / G_NULL_NORM:.6e}"
              "   <- NORMALIZER-FREE")
        assert required, "G's F7 branch is no longer True; the margin below is not this margin"
    print("   Both are ratios of norms of vectors in the same space, so the factor above does not")
    print("   depend on which normalizer the null is expressed in. That is the whole point of it.")
    print()


def section_4_normalizer_spread() -> None:
    """MEASURED. Three committed sqrt-traces exist for ONE null, so `sqrt(Tr C)` names no unit."""
    print("4. WHY sqrt(Tr C) IS NOT AN ADMISSIBLE NULL NORMALIZER  (MEASURED)")
    ratios = {}
    for label, tr in (("unified throw   (CRITERIA:196)", X_SQRT_TR_UNIFIED),
                      ("block footing   (sqrt_tr_old)", G_SQRT_TR_OLD),
                      ("inflated total  (sqrt_tr_new)", G_SQRT_TR_NEW)):
        ratios[label] = G_NULL_NORM / tr
        print(f"   {label}: null / sqrt(Tr) = {ratios[label]:.6e}")
    lo, hi = min(ratios.values()), max(ratios.values())
    print(f"   spread over the three = {hi / lo - 1.0:.1%} for the SAME measured null.")
    print("   SPEC 6.4 quotes `1.31e-12 of the sqrt-trace`; that reproduces against the UNIFIED")
    print("   THROW's trace, not against G's total. The number is right and the phrase")
    print("   `the sqrt-trace` is a definite description, which is the defect: the reader of 6.4")
    print("   is holding G, whose total gives 1.104889e-12.")
    print()


def section_5_rev7_operand() -> None:
    """MEASURED. The withdrawn `5.00e-41` came from a macro that is defined and never printed."""
    delta = 0.005 / 1.65        # half the last printed unit of `\gbdtFiveMeanShift` = 1.65e-38
    print("5. THE WITHDRAWN 5.00e-41, AND WHOSE NUMBER IT WAS  (MEASURED)")
    print(f"   printed-precision delta of values.tex:115 (1.65e-38) = {delta:.10f}")
    print(f"   delta * 1.65e-38 = {delta * VALUES_TEX_MEAN_SHIFT:.6e}   <- reproduces SPEC 3.7a's 5.00e-41")
    print(f"   delta * G's MEASURED mean shift {G_MEAN_SHIFT_NORM:.6e} = "
          f"{delta * G_MEAN_SHIFT_NORM:.6e}")
    print("   So the surviving `candidate input to S` is (a) formatting-derived and (b) derived from")
    print("   a different object than the one Z is footed on. Its MECHANISM survives; its LIMIT")
    print("   does not, and it is not a scientific cap.")
    print()


def main() -> int:
    print(__doc__.split("Run:")[0].strip())
    print("=" * 78)
    print()
    section_1_rho_bound()
    section_1b_projection_monotonicity()
    section_2_rho_crit()
    section_3_f7_margin()
    section_4_normalizer_spread()
    section_5_rev7_operand()
    print("=" * 78)
    print("ALL ASSERTIONS PASSED. Nothing here adopts, grades or authorizes anything.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
