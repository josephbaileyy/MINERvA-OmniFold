#!/usr/bin/env python3
"""Consumer-inversion measurements for PACKET-20260910-z-consumer-set-and-endpoint-requirements.md.

DELIBERATELY A SEPARATE FILE. The `rho` probe
(`probe-z-criteria-acceptance-mathematics-20260910.py`) is the record of a RETIRED approach and is
frozen as history -- Joseph discontinued the universal-bound approach on 2026-09-10 and directed
that its machinery not be extended. Nothing here computes `rho`, bounds a projection, or repairs
F1/F2. These are measurements of what the DECLARED CONSUMERS do when they invert.

Run: python3 docs/orchestration/state/probe-z-consumer-inversion-20260910.py
"""
from __future__ import annotations

import sys

import numpy as np


def section_1_solve_vs_pinv() -> None:
    """THE FAILURE-MODE SPLIT ACROSS THE CONSUMER SET, and it is not a stylistic difference.

    Measured in-tree: two N-D comparators invert with `np.linalg.solve`
    (`compare_ascencio_fullcov.py:188`, `compare_ascencio_fine.py:94`); the E_avail significance
    module uses `pinv` (`eavail_generator_significance.py:107`); and the 2D headline module uses the
    Moore-Penrose pseudo-inverse via SVD, RATIFIED in `app_statmethods.tex:53-58`.

    `solve` is often defended as failing loudly on a singular matrix. It does -- on an EXACTLY
    singular one. That is not the case Z presents.
    """
    d3 = np.array([1.0, 1.0, 1.0])
    print("1. solve vs pinv, exactly singular (rank 2 of 3)")
    C = np.diag([1.0, 1.0, 0.0])
    try:
        np.linalg.solve(C, d3)
        raise AssertionError("solve did not raise on an exactly singular matrix")
    except np.linalg.LinAlgError as exc:
        print(f"   solve -> RAISES LinAlgError: {exc}   (fails loudly, as advertised)")
    print(f"   pinv  -> chi2 = {float(d3 @ np.linalg.pinv(C) @ d3):.4f}   "
          f"(silently drops the null direction)")

    print("   NEAR-singular, which is what a floating-point rank-deficient sum actually looks like:")
    C2 = np.diag([1.0, 1.0, 1e-18])
    chi2_solve = float(d3 @ np.linalg.solve(C2, d3))
    chi2_pinv = float(d3 @ np.linalg.pinv(C2) @ d3)
    print(f"   solve -> chi2 = {chi2_solve:.6e}   <- NO EXCEPTION, absurd value")
    print(f"   pinv  -> chi2 = {chi2_pinv:.6e}   <- truncated, plausible value")
    assert chi2_solve > 1e12, "the near-singular inflation no longer reproduces"
    assert chi2_pinv < 10.0, "pinv no longer truncates"
    print()


def section_2_z_shaped_spectrum(n: int = 400, n_bands: int = 44,
                                n_stat: int = 100, n_ml: int = 24) -> None:
    """Does Z's CONSTRUCTION SHAPE produce exact zeros, or a mixed-sign round-off tail?

    Z is a sum of rank-1 two-endpoint MAT band outer products plus two finite-ensemble sample
    blocks (`SPEC` 1.3a; band rank-1 at `app_statmethods.tex:301-303`; N=100 and N=24 from
    `sbatch_bootstrap_5d_gpu.sh:5` and `sbatch_seedscan_split_5d.sh:5`).

    ⚠ WHAT IS STRUCTURAL AND WHAT IS SYNTHETIC, because only one half transfers.
    STRUCTURAL: a floating-point sum of outer products has NO exact zero eigenvalues, and its
    null-space eigenvalues carry MIXED SIGN at the round-off scale. That is a property of the
    arithmetic and does not depend on which vectors are summed.
    SYNTHETIC: the magnitudes, the condition number and the chi2 inflation factor. The real Z bands
    are not these bands, and the actual tail scale is UNMEASURED.
    """
    rng = np.random.default_rng(20260910)
    C = np.zeros((n, n))
    for _ in range(n_bands):
        v = rng.normal(size=n)
        C += np.outer(v, v)
    for N in (n_stat, n_ml):
        X = rng.normal(size=(N, n))
        X -= X.mean(0)
        C += X.T @ X / N
    ev = np.linalg.eigvalsh(C)
    r_expected = n_bands + (n_stat - 1) + (n_ml - 1)
    tail = ev[:n - r_expected]

    print(f"2. A Z-SHAPED SUM: dimension {n}, expected rank <= {r_expected}")
    print(f"   exact zeros in the spectrum: {int((ev == 0.0).sum())}   <- the key question")
    print(f"   lambda_max = {ev[-1]:.3e}   lambda_min = {ev[0]:.3e}")
    print(f"   the {len(tail)} null-space eigenvalues: min {tail.min():.3e}  max {tail.max():.3e}")
    print(f"   mixed sign in the tail: {bool((tail < 0).any() and (tail > 0).any())}")
    d = rng.normal(size=n)
    try:
        print(f"   solve -> chi2 = {float(d @ np.linalg.solve(C, d)):.6e}   <- NO EXCEPTION")
    except np.linalg.LinAlgError:
        print("   solve -> RAISES (would be the safe outcome, and is NOT what happens)")
    print(f"   pinv  -> chi2 = {float(d @ np.linalg.pinv(C) @ d):.6e}")
    assert int((ev == 0.0).sum()) == 0, "exact zeros appeared; the structural claim would change"
    assert (tail < 0).any() and (tail > 0).any(), "the tail is single-signed; PSD framing changes"
    print("   => a PSD test at exactly 0 fails on a correct object, and 'effective POSITIVE rank'")
    print("      above a cutoff is the only well-posed count. Structural half only.")
    print()


def section_3_positive_control() -> None:
    """The full-rank case, where solve and pinv AGREE -- so the split above is not universal.

    This is the control without which section 1 would read as 'solve is always wrong'. The 2D
    consumer inverts a 205x205 covariance whose rank scan rises smoothly to 205
    (`app_statmethods.tex:630-634`), i.e. full rank -- and there the two agree to round-off.
    """
    rng = np.random.default_rng(7)
    n = 205
    A = rng.normal(size=(n, n))
    C = A @ A.T + n * np.eye(n)          # full rank, well conditioned
    d = rng.normal(size=n)
    a = float(d @ np.linalg.solve(C, d))
    b = float(d @ np.linalg.pinv(C) @ d)
    print("3. POSITIVE CONTROL: full-rank, well-conditioned (the 2D consumer's regime)")
    print(f"   solve = {a:.10f}   pinv = {b:.10f}   relative difference = {abs(a-b)/a:.3e}")
    assert abs(a - b) / a < 1e-9, "solve and pinv disagree at full rank; the control is broken"
    print("   => the failure mode is a property of the OBJECT's rank, not of the CALL. A consumer")
    print("      using solve is correct where its covariance is full rank and unsafe where it is not.")
    print()


def main() -> int:
    print(__doc__.split("Run:")[0].strip())
    print("=" * 78)
    print()
    section_1_solve_vs_pinv()
    section_2_z_shaped_spectrum()
    section_3_positive_control()
    print("=" * 78)
    print("ALL ASSERTIONS PASSED. Adopts nothing, grades nothing, authorizes nothing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
