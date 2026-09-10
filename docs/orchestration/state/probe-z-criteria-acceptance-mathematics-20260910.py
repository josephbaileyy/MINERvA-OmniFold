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

6  pinv subspace     ⚠ THE LIMIT OF SECTION 1, and a defect in the criterion this probe supported.
                      Section 1 bounds the TRUE inverse; the consumer uses `pinv`. Two near-equal
                      modes straddling the cutoff can SWAP, holding retained RANK fixed while
                      flipping the retained SUBSPACE -- and the bound then fails. Found by the
                      z-independent-assessor lane; reproduced here independently. SYNTHETIC, at
                      condition number ~1e15; whether real Z members do it is UNMEASURED.
7  ndf direction     the `ndf` policy change INCREASES reported significances WHERE retained rank
                      < bin count. I had declined to name a direction; that conflated two
                      comparisons. Also the assessor's.
8  domination        THEOREM. `rho <= d` bounds EVERY `u' C u` functional, so s_agg, s_med, the
                      per-bin distribution and s_proj are all COROLLARIES of leg 1, not independent
                      constraints. Plus the measured concentration case: at equal trace change the
                      per-bin MEDIAN reads exactly 0 while rho separates by n. This is the evidence
                      for the cause3_corr recommendation.
9  support/range     ⚠ FOUR THIRD-LANE FINDINGS, each reproduced independently. `rho` requires a
                      POSITIVE DEFINITE baseline, and Z's construction does not give one -- derived
                      from Z's OWN operands in section 10, not transferred. Section 1b's
                      monotonicity does NOT survive restricting to a support unless the perturbation
                      stays inside range(C0); measured both ways. And domination bounds VALUES, not
                      THRESHOLDS, so it does not imply non-bindingness.
                      ⚠ THE REPAIRS BELOW ARE DEMONSTRATIONS, NOT THE RECOMMENDED CRITERION: Joseph
                      ruled 2026-09-10 not to "add regularization, discard directions, or change
                      inference conventions merely to make a theorem applicable".

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


def _retained_projector(C: np.ndarray, rcond: float = 1e-15):
    """The orthogonal projector onto the subspace `pinv` RETAINS, and that subspace's dimension.

    `numpy.linalg.pinv` keeps modes above `rcond * sigma_max`. The projector is the object the
    criterion must gate on; the dimension is the proxy that is NOT sufficient -- section 6.
    """
    w, V = np.linalg.eigh(C)
    keep = w > rcond * w.max()
    U = V[:, keep]
    return U @ U.T, int(keep.sum())


def _assert_comparison_is_live(build, a: float, b: float, label: str) -> None:
    """PERTURB ONE OPERAND AND CONFIRM THE OUTPUT MOVES. The only test that a comparison is real.

    Ruled by Joseph 2026-09-10, correcting a framing this lane had accepted: an exact `0.000e+00`
    from a float comparison is **a prompt to check, never a finding**. Identical deterministic code
    paths on identical inputs are legitimately bit-equal, and cancellation and underflow also give
    hard zeros. So a near-zero result may NOT be read as evidence that two operands are distinct
    objects, nor as evidence that they are the same one. Only a live response to a perturbation
    distinguishes them.
    """
    C0, Ck = build(a, b), build(a, b)
    P0, _ = _retained_projector(C0)
    Pk, _ = _retained_projector(Ck)
    gap_same = float(np.linalg.norm(P0 - Pk, 2))
    # now move ONE operand across the cutoff and require the gap to respond
    Ck_moved = build(b, a)
    Pm, _ = _retained_projector(Ck_moved)
    gap_moved = float(np.linalg.norm(P0 - Pm, 2))
    print(f"   liveness control ({label}): identical operands -> gap {gap_same:.3e}; "
          f"one operand perturbed -> gap {gap_moved:.4f}")
    if not gap_moved > 0.5:
        raise AssertionError(
            "the comparison did NOT respond to a perturbation, so it is not measuring anything -- "
            "this is the check that a near-zero gap cannot supply")


def section_6_pinv_subspace(n: int = 9) -> None:
    """⚠ THE LIMIT OF SECTION 1, AND IT IS A DEFECT IN THE CRITERION THIS PROBE SUPPORTED.

    FOUND BY THE z-independent-assessor LANE. Reproduced here independently, from its description
    rather than by running its probe, so the confirmation is a second measurement.

    Section 1 bounds `d' C^-1 d` with the TRUE inverse. The consumer computes `d' pinv(C) d`
    (`eavail_generator_significance.py:107,132`) -- and so does `_chi2` above. `pinv` DISCARDS modes
    below `rcond * sigma_max`, so when two members RETAIN DIFFERENT SUBSPACES the interval does not
    transfer, and the recommendation's first terminal-outcome rule gated INCONCLUSIVE on retained
    RANK. Rank is a proxy and it is not sufficient: two near-equal eigenvalues straddling the cutoff
    can SWAP, holding the rank fixed while flipping the retained subspace.

    ⚠ THE CONSTRUCTION IS SYNTHETIC, at condition number ~1e15, and needs two modes to swap.
    WHETHER REAL Z MEMBERS DO THIS IS UNMEASURED AND NOTHING HERE CLAIMS IT. What is established is
    that the GUARD DOES NOT EXCLUDE IT.

    WHY SECTION 1's 120,000 EVALUATIONS MISSED IT: that ensemble is well-conditioned, so nothing
    sits near the cutoff and the subspace never moves. **That is agreement measured over a domain
    that excludes the failing regime** -- the shape `FINDING-20260910`'s amendment 2 identified in
    `SPEC` 6 item 1, reproduced one layer down in a probe written after it. And the excluded regime
    is the one the consumer documents itself in, at `:98-101`: *"a highly-correlated systematic
    covariance ... can be near-singular -> pinv amplifies shape directions"*.

    THE REMEDY, and it chains this probe's own two theorems: gate on RETAINED-SUBSPACE IDENTITY. If
    both members retain the same subspace `S`, let `U` be an orthonormal basis of `S`; the consumed
    form is then `(U'd)' (U' C U)^-1 (U'd)` with a TRUE inverse, and `U'` has orthonormal rows, so
    section 1b gives `rho(U' C0 U, U' Ck U) <= rho(C0, Ck)` and section 1 applies inside `S`.
    """
    rng = np.random.default_rng(SEED + 2)
    Q, _ = np.linalg.qr(rng.normal(size=(n, n)))
    large = [1.0] + [10.0 ** -k for k in range(1, n - 1)]

    def build(a: float, b: float) -> np.ndarray:
        ev = np.array(large[: n - 2] + [a, b])
        return Q @ np.diag(ev) @ Q.T

    d = Q[:, -2].copy()          # aligned with the mode that gets dropped in arm 1

    print("6. THE pinv RETAINED-SUBSPACE LIMIT  (found by the assessor; reproduced independently)")

    # ARM 1 -- the failing regime. Two near-equal modes STRADDLE the cutoff and swap.
    C0, Ck = build(1.2e-15, 0.8e-15), build(0.8e-15, 1.2e-15)
    r = rho(C0, Ck)
    P0, k0 = _retained_projector(C0)
    Pk, kk = _retained_projector(Ck)
    subspace_gap = float(np.linalg.norm(P0 - Pk, 2))
    c0, ck = _chi2(C0, d), _chi2(Ck, d)
    floor = c0 / (1.0 + r)
    print(f"   ARM 1, straddling and swapped: rho = {r:.6f}")
    print(f"      retained rank {k0} vs {kk} -- IDENTICAL: {k0 == kk}")
    print(f"      ||P_0 - P_k||_2 = {subspace_gap:.4f}   (0 = same subspace, 1 = a mode flipped)")
    print(f"      chi2_0 = {c0:.3e}, chi2_k = {ck:.3e}, section-1 floor = {floor:.3e}")
    print(f"      section-1 bound holds: {ck >= floor * (1 - 1e-9)}   <- FALSE is the finding")
    print(f"      RANK branch would fire: {k0 != kk}    SUBSPACE branch fires: {subspace_gap > 1e-8}")
    assert k0 == kk, "the construction no longer holds rank fixed, so it tests the wrong thing"
    assert ck < floor, "the bound was not violated: the construction has stopped reproducing"
    assert subspace_gap > 0.5, "the retained subspace did not move"

    # ARM 2 -- the CORRECTLY-SILENT direction, with rho held at the SAME value so the difference
    # between the arms is attributable to the subspace and to nothing else.
    C0b, Ckb = build(1.2e-13, 0.8e-13), build(0.8e-13, 1.2e-13)
    r2 = rho(C0b, Ckb)
    P0b, kb0 = _retained_projector(C0b)
    # ⚠ `Ckb`, NOT `C0b`. The first version of this line passed `C0b` twice, so the silent control
    # compared an object with ITSELF and would have reported a zero gap whatever the perturbation
    # did -- a control that cannot fail, inside a probe whose subject is a guard that cannot fail.
    #
    # ⚠ AND THE EXACT ZERO IS NOT WHAT ESTABLISHED THAT, though it is what made me look. Corrected
    # on Joseph's ruling: an exact `0.000e+00` from a float comparison is a PROMPT TO CHECK, never a
    # finding. Identical deterministic code paths on identical inputs are legitimately bit-equal, and
    # cancellation and underflow also produce hard zeros. THE TEST IS TO PERTURB ONE OPERAND AND
    # CONFIRM THE OUTPUT MOVES -- which `_assert_comparison_is_live` below does, and which is the
    # only thing that distinguishes a real comparison from a self-comparison.
    Pkb, kbk = _retained_projector(Ckb)
    gap2 = float(np.linalg.norm(P0b - Pkb, 2))
    ck2 = _chi2(Ckb, d)
    lo2, hi2 = _chi2(C0b, d) / (1 + r2), _chi2(C0b, d) / (1 - r2)
    print(f"   ARM 2, same swap but BOTH modes retained: rho = {r2:.6f}  (arm 1: {r:.6f})")
    print(f"      ||P_0 - P_k||_2 = {gap2:.3e}   retained rank {kb0} vs {kbk}")
    print(f"      chi2_k = {ck2:.6e} in [{lo2:.6e}, {hi2:.6e}]: "
          f"{lo2 * (1 - 1e-9) <= ck2 <= hi2 * (1 + 1e-9)}")
    print(f"      SUBSPACE branch fires: {gap2 > 1e-8}   <- must be False (correctly silent)")
    _assert_comparison_is_live(build, 1.2e-15, 0.8e-15, "arm 1's straddling pair")
    assert abs(r2 - r) < 0.05, "rho is not held across the arms, so the arms are not comparable"
    assert gap2 < 1e-8, "arm 2's retained subspace moved; it is not the silent control"
    assert lo2 * (1 - 1e-9) <= ck2 <= hi2 * (1 + 1e-9), "arm 2 violated the bound"
    print("   So the guard is BIDIRECTIONAL on the subspace test and BLIND on the rank test.")
    print()


def section_7_ndf_direction() -> None:
    """The `ndf` policy change has a KNOWN DIRECTION, and the recommendation declined to name it.

    FOUND BY THE ASSESSOR. `D.1(b)` recommends `ndf` = retained rank rather than the bin count
    (`chi2_to_sigma(chi2, n_ea)`, `eavail_generator_significance.py:132`). I wrote that the net sign
    was not determined -- that conflated TWO comparisons. Changing the `ndf` POLICY holds `chi2`
    fixed (it is already computed with `pinv`), and at fixed `chi2` the map is strictly decreasing
    in `ndf`. Since retained rank <= bin count, the change INCREASES reported significances. It is
    distributionally correct AND anti-conservative, and Joseph should get it with its direction.
    """
    try:
        from scipy import stats
    except ImportError:
        print("7. ndf direction -- SKIPPED, scipy is not importable\n")
        return

    def z_of(chi2: float, ndf: int) -> float:
        return float(stats.norm.isf(stats.chi2.sf(chi2, ndf) / 2.0))

    print("7. THE ndf POLICY CHANGE HAS A KNOWN DIRECTION  (synthetic chi2; the SIGN is the claim)")
    print("     chi2      ndf=bins -> z      ndf=rank -> z    increases?")
    for chi2_v, nbin, rank in ((5210.0, 4825, 4800), (86.5, 42, 38), (11263.0, 10694, 10600)):
        zb, zr = z_of(chi2_v, nbin), z_of(chi2_v, rank)
        print(f"   {chi2_v:9.1f}  {nbin:5d} -> {zb:6.4f}   {rank:5d} -> {zr:6.4f}      {zr > zb}")
        assert zr > zb, "the direction claim failed: retained rank did not increase the significance"
    print("   Monotone in ndf at fixed chi2, so the sign is general; the magnitudes are synthetic.")
    print()


def section_8_domination(trials: int = 3000) -> None:
    """THEOREM. `rho <= d` bounds EVERY functional of the form `u' C u`, so leg 1 DOMINATES any
    diagonal-based second leg. This is what decides Joseph's `cause3_corr` question.

        rho(C0, Ck) <= d < 1   =>   for every u with u'C0 u > 0:
                                    u' Ck u / u' C0 u  in  [1 - d, 1 + d]

    Proof: with `w = C0^(1/2) u`, `u'Ck u = w'(I + E)w` and `u'C0 u = w'w`, and `E`'s eigenvalues
    lie in `[-d, d]`. Sharp, for the same reason section 1 is.

    COROLLARIES, each a statistic the specification asked for as a SECOND leg:
      u = e_i        every per-bin VARIANCE moves within [1-d, 1+d], so every per-bin sigma within
                     [sqrt(1-d), sqrt(1+d)] -- bounding s_med, the per-bin max, p90, the whole
                     per-bin movement distribution
      u = 1          the total
      u = rows of M  s_proj, for EVERY projection, designated or not (with section 1b for the trunk)
      Tr            a sum of e_i' C e_i, so s_agg too

    So `s_agg`, `s_med`, the per-bin distribution and `s_proj` are all COROLLARIES of leg 1 rather
    than independent constraints -- and section 1 additionally covers the inverse-quadratic consumer,
    which no diagonal statistic can.
    """
    rng = np.random.default_rng(SEED + 3)
    worst_lo, worst_hi, tight, checked = 1.0, 1.0, 0.0, 0
    for _ in range(trials):
        n = int(rng.integers(2, 10))
        A = rng.normal(size=(n, n))
        C0 = A @ A.T + n * np.eye(n)
        B = rng.normal(size=(n, n))
        Ck = C0 + 0.03 * (B + B.T)
        if np.linalg.eigvalsh(Ck)[0] <= 0:
            continue
        r = rho(C0, Ck)
        if r >= 1.0:
            continue
        functionals = [np.eye(n)[i] for i in range(n)] + [np.ones(n)]
        functionals += [rng.normal(size=n) for _ in range(6)]
        for u in functionals:
            den = float(u @ C0 @ u)
            if den <= 0:
                continue
            ratio = float(u @ Ck @ u) / den
            worst_lo = min(worst_lo, ratio / (1.0 - r))
            worst_hi = max(worst_hi, ratio / (1.0 + r))
            tight = max(tight, ratio / (1.0 + r))
            checked += 1
    print("8. LEG 1 DOMINATES EVERY `u' C u` FUNCTIONAL  (this decides the cause3_corr question)")
    print(f"   {checked} (pair, functional) evaluations, including every e_i and the all-ones vector")
    print(f"   ratio / (1 - rho), min = {worst_lo:.12f}   must be >= 1")
    print(f"   ratio / (1 + rho), max = {worst_hi:.12f}   must be <= 1")
    print(f"   sharpness reached: {tight:.6f}")
    assert worst_lo >= 1.0 - 1e-9, "DOMINATION LOWER SIDE VIOLATED"
    assert worst_hi <= 1.0 + 1e-9, "DOMINATION UPPER SIDE VIOLATED"

    # THE CONCENTRATION CASE -- the STATED reason SPEC 3.6b wanted a second, per-bin leg:
    # "the same trace can be diffuse or concentrated, so the per-bin leg is independently binding."
    # Measured: at EQUAL trace change, s_agg is identical and the per-bin MEDIAN is blind, while
    # rho is n times larger. So the hazard the second leg exists for is one rho sees and the
    # second leg does not.
    n = 50
    C0 = np.eye(n)
    eps = 0.02
    E_diffuse = eps * np.eye(n)
    E_conc = np.zeros((n, n))
    E_conc[0, 0] = eps * n                     # same trace, all in one direction
    print("   CONCENTRATION, equal trace change, n = 50:")
    rows = {}
    for label, E in (("diffuse", E_diffuse), ("concentrated", E_conc)):
        Ck = C0 + E
        s_agg = abs(np.sqrt(np.trace(Ck)) - np.sqrt(np.trace(C0))) / np.sqrt(np.trace(C0))
        s_med = abs(float(np.median(np.sqrt(np.diag(Ck)))) - 1.0)
        rows[label] = (float(np.trace(E)), s_agg, s_med, rho(C0, Ck))
        print(f"      {label:>12}: tr(dC) = {np.trace(E):.4f}  s_agg = {s_agg:.6f}  "
              f"s_med = {s_med:.6f}  rho = {rho(C0, Ck):.6f}")
    assert abs(rows["diffuse"][1] - rows["concentrated"][1]) < 1e-12, "s_agg is not equal: the case is not controlled"
    assert rows["concentrated"][2] == 0.0, "the per-bin median is no longer blind to the concentrated case"
    assert rows["concentrated"][3] > 10 * rows["diffuse"][3], "rho did not separate the two"
    print("      -> s_agg IDENTICAL; the per-bin MEDIAN reads exactly 0 on the concentrated case;")
    print("         rho separates them by n. The second leg's own motivating hazard is one rho sees.")
    print()


def retained_basis(C: np.ndarray, rcond: float = 1e-15) -> np.ndarray:
    """An orthonormal basis of the subspace `pinv` retains. THE SUPPORT DEFINITION `rho` NEEDED.

    Found missing by the third review lane (F1): `rho` as first written required `C_0 > 0` and the
    phrase "on the compared support" was never defined anywhere.

    ⚠ AND THE RANK NUMBER FIRST CITED HERE WAS THE WRONG OBJECT'S -- MY ERROR, INHERITED FROM A
    RELAY AND NOT CHECKED. `app_statmethods.tex:636-637`'s subject is "The standard-P4 5D CANDIDATE
    covariance", i.e. S, the component DONOR (`std_final5_candidate.root`), measured 2026-08-10.
    Rank 263 is S's. It is not G's and it is not Z's, and a first version of this docstring called
    it "the production trunk" -- a definite description doing a citation's work, which is this
    campaign's catalogued failure. Section 10 derives Z's OWN bound instead.

    ⚠ THIS FUNCTION IS A DEMONSTRATION, NOT THE RECOMMENDED CRITERION. Restricting to a retained
    subspace DISCARDS DIRECTIONS, and Joseph ruled 2026-09-10 against doing that "merely to make a
    theorem applicable". It is kept because section 9 needs it to show WHY the repair path was
    abandoned -- monotonicity does not survive it. `U' C_0 U` is positive definite by construction,
    so `rho_S` is well defined; that is all this establishes.
    """
    w, V = np.linalg.eigh(C)
    return V[:, w > rcond * w.max()]


def rho_on_support(C0: np.ndarray, Ck: np.ndarray, rcond: float = 1e-15) -> float:
    """`rho` restricted to `C0`'s retained subspace. Defined for a rank-deficient baseline."""
    U = retained_basis(C0, rcond)
    return rho(U.T @ C0 @ U, U.T @ Ck @ U)


def section_9_support_and_range(trials: int = 4000) -> None:
    """⚠ FOUR FINDINGS FROM THE THIRD REVIEW LANE, EACH REPRODUCED INDEPENDENTLY HERE.

    F1  `rho` was undefined on the object it was proposed for. `retained_basis` above is the fix.
    F2  ⚠ AND MONOTONICITY (section 1b) DOES NOT SURVIVE THE RESTRICTION UNLESS THE PERTURBATION
        STAYS INSIDE `range(C_0)`. Section 1b's proof needs `Ck - C0 = C0^(1/2) E C0^(1/2)`, i.e.
        `range(Ck - C0)` contained in `range(C0)`. Measured below in both directions. This KILLS,
        as written, the claim that a trunk-level `rho` bounds every marginal at once.
    F9  DOMINATION DOES NOT IMPLY NON-BINDINGNESS. Leg 2 is implied by leg 1 iff `rho_crit <= tau`
        -- a statement about THRESHOLDS, not values. Demonstrated below.
    F8  section 8's corollary needs `u' C_0 u > 0`; a zero-variance baseline bin makes the ratio
        unbounded.

    And section 1b's own 1,898-pair ensemble is well-conditioned by construction, so it EXCLUDED
    the rank-deficient regime the production object lives in -- the domain-exclusion shape section
    6 diagnosed, in the section next door. Fourth instance in this probe's own history.
    """
    rng = np.random.default_rng(SEED + 4)
    print("9. SUPPORT, RANGE-CONTAINMENT, AND THE THRESHOLD/VALUE DISTINCTION")

    # ---- F2: monotonicity under restriction, both directions.
    worst_in, worst_out, n_in, n_out = 0.0, 0.0, 0, 0
    for _ in range(trials):
        nh, r, nl = 8, 5, 4
        Q, _ = np.linalg.qr(rng.normal(size=(nh, nh)))
        ev = np.concatenate([rng.uniform(1.0, 4.0, r), np.zeros(nh - r)])
        C0 = Q @ np.diag(ev) @ Q.T                       # rank-deficient, like the trunk
        U = Q[:, :r]
        Bi = rng.normal(size=(r, r))
        Bo = rng.normal(size=(nh, nh))
        deltas = (("inside range(C0)", U @ (0.05 * (Bi + Bi.T)) @ U.T),
                  ("leaking outside", 0.05 * (Bo + Bo.T)))
        M = np.zeros((nl, nh))
        M[rng.integers(0, nl, size=nh), np.arange(nh)] = rng.uniform(0.1, 3.0, size=nh)
        for label, d in deltas:
            Ck = C0 + d
            A0, Ak = M @ C0 @ M.T, M @ Ck @ M.T
            if np.linalg.eigvalsh(A0)[0] <= 1e-9:
                continue
            try:
                rs = rho_on_support(C0, Ck, rcond=1e-12)
            except ValueError:
                continue
            if rs <= 0:
                continue
            ratio = rho(A0, Ak) / rs
            if label.startswith("inside"):
                worst_in, n_in = max(worst_in, ratio), n_in + 1
            else:
                worst_out, n_out = max(worst_out, ratio), n_out + 1
    print(f"   F2  perturbation INSIDE range(C0): max rho_proj/rho_support = {worst_in:.3f} "
          f"over {n_in} trials   (monotonicity HOLDS)")
    print(f"   F2  perturbation LEAKING outside:  max rho_proj/rho_support = {worst_out:.1f} "
          f"over {n_out} trials   (monotonicity FAILS)")
    assert worst_in <= 1.0 + 1e-6, "monotonicity failed even INSIDE the range: the fix is wrong"
    assert worst_out > 10.0, "the leaking case no longer violates; the finding has stopped reproducing"

    # ---- F9: domination bounds VALUES; independence is about THRESHOLDS.
    try:
        from scipy import stats

        def chi2_crit(T, ndf):
            return float(stats.chi2.isf(2.0 * stats.norm.sf(T), ndf))

        print("   F9  domination gives s <= rho, so leg 2 is IMPLIED iff rho_crit <= tau:")
        for ndf in (42, 263, 10694):
            rc = chi2_crit(4.0, ndf) / chi2_crit(3.0, ndf) - 1.0
            sig = float(np.sqrt(1.0 + rc) - 1.0)
            binds = [t for t in (0.001, 0.01, 0.05) if sig > t]
            print(f"       ndf={ndf:6d}: rho_crit={rc:.4f} permits per-bin sigma up to {sig:.4%}; "
                  f"leg 2 BINDS INDEPENDENTLY at tau in {binds}")
            assert binds, "no tau in the tested set binds; F9's regime has vanished"
    except ImportError:
        print("   F9  SKIPPED, scipy not importable")

    # ---- F8: the corollary's own hypothesis, dropped from its table.
    C0 = np.diag([1.0, 1.0, 0.0])
    Ck = np.diag([1.0, 1.0, 0.5])
    U = retained_basis(C0)
    print(f"   F8  C0 = diag(1,1,0): rho on the retained {U.shape[1]}-dim subspace = "
          f"{rho(U.T @ C0 @ U, U.T @ Ck @ U):.6f}, yet the DROPPED bin's variance ratio is "
          f"0.5/0 = inf -- the per-bin corollary is VOID where the baseline variance is zero")
    assert U.shape[1] == 2

    # ---- the concentration sentence, and how much of it is n-specific.
    print("   concentration: the SEPARATION is structural; the 'refused at 1.0' wording is not:")
    for n in (10, 25, 50, 263):
        Cc = np.eye(n)
        E = np.zeros((n, n))
        E[0, 0] = 0.02 * n
        r = rho(Cc, Cc + E)
        print(f"       n={n:4d}: rho={r:.4f}  {'PASSES a 0.2 gate' if r <= 0.2 else 'refused'}")
    print()


def section_10_z_own_rank_bound() -> None:
    """Z's rank deficiency is DERIVABLE FROM Z'S OWN OPERANDS -- no transfer, before Z exists.

    Rank 263 belongs to S. What transfers is the note's ARGUMENT, in its own words
    (`app_statmethods.tex:639-640`): "A sum of ~45 two-endpoint MAT bands plus statistical and ML
    blocks cannot span 10,694 directions, so this is a property of the construction, not a defect."
    Z is built by that same construction (SPEC 1.3a), so the bound follows from Z's manifest.

    OPERANDS, each measured in this checkout:
      45 all_syst_bands              S.component_manifest (V=13 + A=5 + R=27), SPEC 1.3a
      a +-1sigma pair is RANK 1      app_statmethods.tex:301-303, "collapses to the rank-1
                                     1/4 (X+ - X-)(X+ - X-)'"
      Flux is N_u = 100 (PPFX)       app_statmethods.tex:264 -> mean-centered rank <= 99
      C_stat from 100 members        sbatch_bootstrap_5d_gpu.sh:5, --array=1-100%32 -> <= 99
      C_ML from 24 members           sbatch_seedscan_split_5d.sh:5, --array=1-24%24  -> <= 23
      D_Z is a positive diagonal     SPEC 1.3a -> rank-preserving on the inflated block

    ⚠ THE ASSUMPTION, NAMED, AND ITS DIRECTION: the note says "ALMOST all other bands are +-1sigma
    pairs" and its table is labelled "(examples)", so I cannot assert all 44 non-Flux bands are
    two-endpoint. If any is an N-universe multisim the bound RISES by N-2. The bound is therefore
    not tight -- but the CONCLUSION is robust, because it is a counting argument over ~45 bands
    against 10,694 directions, and no plausible band inventory closes that gap.
    """
    n_bands = 45
    n_flux_universes = 100
    n_stat, n_ml = 100, 24
    reported_bins = 10694

    rank_bands = (n_bands - 1) * 1 + (n_flux_universes - 1)     # 44 pairs at rank 1, Flux at <= 99
    bound = rank_bands + (n_stat - 1) + (n_ml - 1)
    print("10. Z's OWN RANK BOUND, DERIVED (no transfer; rank 263 is S's, not Z's)")
    print(f"    44 two-endpoint bands at rank <= 1        -> {n_bands - 1}")
    print(f"    Flux, N_u = {n_flux_universes}, mean-centered           -> {n_flux_universes - 1}")
    print(f"    C_stat, N = {n_stat}                          -> {n_stat - 1}")
    print(f"    C_ML,   N = {n_ml}                           -> {n_ml - 1}")
    print(f"    rank(C_Z) <= {bound}  of {reported_bins} reported bins "
          f"({bound / reported_bins:.2%} of the dimension)")
    print(f"    numerical nulls >= {reported_bins - bound}")
    assert bound < reported_bins / 10, "the counting argument no longer gives a deficient object"
    print("    So C_Z is SINGULAR by construction and `C_Z^(-1/2)` does not exist. Section 1's")
    print("    hypothesis fails on Z's trunk -- not as a defect, as a property of the sum.")
    print(f"    Corroboration, NOT a derivation: S's MEASURED rank is 263 against this bound of "
          f"{bound} for the same construction class.")
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
    section_6_pinv_subspace()
    section_7_ndf_direction()
    section_8_domination()
    section_9_support_and_range()
    section_10_z_own_rank_bound()
    print("=" * 78)
    print("ALL ASSERTIONS PASSED. Nothing here adopts, grades or authorizes anything.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
