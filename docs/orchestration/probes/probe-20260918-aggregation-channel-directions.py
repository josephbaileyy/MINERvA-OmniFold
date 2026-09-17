#!/usr/bin/env python3
"""Which movement channel does a per-bin tolerance actually control? MEASURED, both directions.

THIS PROBE EXISTS BECAUSE I GOT BOTH DIRECTION LABELS BACKWARDS. I told two lanes that a per-bin
tolerance `delta_bin` is "non-conservative under movement coherent across a destination cell's 1,568
contributors, over-conservative under cancelling movement." Both halves are wrong. `[91eaa2]` caught
it; this is my own re-measurement, which agrees with the correction and refines one part of it.

  * COHERENT movement is BENIGN and EXACT. `sigma -> (1+d)*sigma` sends `C -> (1+d)^2 * C`
    IDENTICALLY, so every quadratic form -- every projected variance, on every map -- moves by
    exactly `(1+d)^2 - 1`, independent of N, of the weights, and of the correlation structure. The
    coherent column below is invariant across N in {2, 10, 200, 1568} and across all three
    structures, which is the whole point: AGGREGATION AVERAGES A COHERENT MOVE, IT DOES NOT AMPLIFY
    IT, and 1,568 does not multiply it. The factor 2 is variance being quadratic in sigma, not a
    projection effect at all.
  * CANCELLING movement over a NEAR-CANCELLING source is the unbounded channel. Same mechanism that
    refuted this lane's §5.7 projection-bound claim, one level down: it needs BOTH a non-uniform
    perturbation AND an anti-correlated source, so a search varying only the magnitude of a uniform
    move passes universally and sees nothing.

AND THE FACTOR IS NOT "ABOUT N". It DECREASES with N here at fixed epsilon, because severity is set
by how small `w^T C w` is, not by how many cells aggregate. A peer reported ~200x at N=200 where
this returns ~5050x; that disagreement across constructions is itself the evidence that N is not the
governing variable. Do not restate this channel as N-scaling. Claim 4 below asserts the decrease.

THE CORRECTED CONCLUSION IS STRONGER THAN THE WRONG ONE, AND IT REVERSES MY RECOMMENDATION:
`delta_bin` is EXACT on the coherent channel and VACUOUS on the cancelling one. That argues L3's
primacy better than "weak proxy in both directions" did -- and it means L2 must be KEPT as a cheap
declared diagnostic rather than demoted, because it is the only free control on the coherent channel.

WHY NO A-PRIORI BOUND EXISTS FOR C_Z. For positive weights and a POSITIVE-DEFINITE C the excursion
is bounded by `((1+d)^2-1) * lambda_max/lambda_min`, and `z_assembly.py:44-46` records both ends, so
this looked like a zero-compute lookup. But the pilot's own table
(`lane/z-assembly-pilot-20260914:nd-unfolding/ND_OMNIFOLD_RUN_LOG.md`) records for C_Z cv:
`lambda_min = -1.2750516323643892e-90`, `lambda_max = 2.229223998752954e-75`,
`neg_fraction_of_max = 5.719710684424999e-16`, and 5214 NEGATIVE EIGENVALUES of the 10,694-dim
spectrum. Two cautions on that last figure. (1) It lives in the pilot's SEPARATELY PERSISTED spectra
(`z_pilot.py:275,290`, a deliberate second independent `eigvalsh` with `verdict: None`), NOT in
`z-receipt-cv.json`, which carries only the extrema -- a reader who checks the receipt will not find
it. (2) `n_negative` NAMES TWO DIFFERENT QUANTITIES in this repository: `unified_throw_cov.py:372`
computes it as `nonzero(x_cv < 0)` -- negative BIN VALUES, which the census records as ZERO. Only
`z_pilot.py`'s is an eigenvalue count. Anyone grepping the name will hit the other one first and
conclude this figure is wrong.
lambda_min is NEGATIVE, so the bound does not exist. Passing the PSD gate is a statement about
ARITHMETIC (5.72e-16 of lambda_max), not about definiteness, and supplies no bound here. Whether
M1's 42 rows actually probe the near-null subspace is decidable from the diagonal of `M1 C_Z M1^T`
-- which IS the M1 product the one deferred claim already needs. Not a new study.

A NOTE ON THE TOLERANCE, because the first version of this probe FAILED and was right to. The
identity in claim 1 is exact, but `w^T C w` in the near-cancelling constructions is a
catastrophically cancelling sum (2e-9 built from terms of order 1), so the QUADRATIC FORM resolves
the coherent factor only to ~2e-5 relative. The cancellation that defines the dangerous channel also
degrades the measurement of the benign one. So claim 1 is split: 1a tests the identity elementwise
on the matrix, where it is exact; 1b tests the form in a 1% window, which still excludes any
N-dependent amplification by three orders of magnitude.

Exits 0 while the measured directions still hold, 1 if they stop reproducing.
No Z payload is read, no cluster access is used, synthetic matrices only.
"""
import numpy as np


def var_y(w, sig, R):
    return float(w @ (np.outer(sig, sig) * R) @ w)


def rel(w, sig0, R, u):
    v0 = var_y(w, sig0, R)
    return (var_y(w, sig0 * (1.0 + u), R) - v0) / v0, v0


D = 1e-3
EXACT = (1.0 + D) ** 2 - 1.0


def structures(N):
    rho = -1.0 / (N - 1) + 1e-9      # w^T R w = 0 exactly at rho = -1/(N-1): maximal cancellation
    Rnc = np.full((N, N), rho)
    np.fill_diagonal(Rnc, 1.0)
    return (("uncorrelated       ", np.eye(N)),
            ("positive rho=+0.5  ", np.full((N, N), 0.5) + 0.5 * np.eye(N)),
            ("NEAR-CANCELLING src", Rnc))


def moves(N):
    return (np.full(N, +D),
            np.where(np.arange(N) % 2 == 0, +D, -D))


def main():
    print(f"delta = {D:g} applied to per-bin SIGMA; change reported in destination VARIANCE;")
    print("weights are bin widths, so STRICTLY POSITIVE throughout.\n")
    for N in (2, 10, 200, 1568):
        w, s = np.ones(N), np.ones(N)
        coh, can = moves(N)
        for nm, R in structures(N):
            rc, v0 = rel(w, s, R, coh)
            rk, _ = rel(w, s, R, can)
            print(f"N={N:5d} {nm} min-eig(R)={np.linalg.eigvalsh(R).min():+.2e} "
                  f"w^T C w={v0:.4e} | COHERENT {rc / D:9.4f}x d | cancelling {rk / D:12.4f}x d")
        print()
    print(f"ANALYTIC: coherent moves EVERY quadratic form by (1+d)^2-1 = {EXACT:.10e} "
          f"= {EXACT / D:.6f}x d,")
    print("independent of N, of the weights, and of R. Aggregation cannot amplify it.")

    fail = []
    for N in (2, 10, 200, 1568):
        w, s = np.ones(N), np.ones(N)
        coh, can = moves(N)
        for nm, R in structures(N):
            # CLAIM 1a -- the IDENTITY, tested where it is exact: elementwise on the matrix.
            C0 = np.outer(s, s) * R
            C1 = np.outer(s * (1 + coh), s * (1 + coh)) * R
            if not np.allclose(C1, (1.0 + D) ** 2 * C0, rtol=1e-14, atol=0.0):
                fail.append(f"N={N} {nm.strip()}: C' != (1+d)^2 C elementwise")
            # CLAIM 1b -- the quadratic form, at PHYSICS scale rather than machine scale.
            # NOTE the deliberate 1% window: in the near-cancelling constructions `w^T C w` is a
            # catastrophically cancelling sum (2e-9 from terms of order 1), so the FORM cannot
            # resolve the identity better than ~2e-5 relative even though 1a holds exactly. A
            # 1e-12 window here FAILED on exactly those rows -- the cancellation that defines the
            # dangerous channel also degrades the measurement of the benign one. The window still
            # excludes any N-dependent amplification by three orders of magnitude.
            rc, _ = rel(w, s, R, coh)
            if abs(rc / D - EXACT / D) > 0.01:                # CLAIM 1b
                fail.append(f"N={N} {nm.strip()}: coherent {rc / D:.6f}x d not ~{EXACT / D:.3f}x d")
            rk, _ = rel(w, s, R, can)
            near = nm.startswith("NEAR")
            if not near and rk / D > 1.0:                      # CLAIM 2
                fail.append(f"N={N} {nm.strip()}: cancelling {rk / D:.4f}x d should be <1x")
            if near and rk / D < 100.0:                        # CLAIM 3
                fail.append(f"N={N} near-cancelling: only {rk / D:.4f}x d, channel not reproducing")

    def nc(N):                                                 # CLAIM 4: NOT N-scaling
        w, s = np.ones(N), np.ones(N)
        return rel(w, s, structures(N)[2][1], moves(N)[1])[0] / D

    a, b, c = nc(10), nc(200), nc(1568)
    if not a > b > c:
        fail.append(f"N-monotonicity: {a:.1f} {b:.1f} {c:.1f} -- expected DECREASING, "
                    f"so the channel is not N-scaling")

    print()
    if fail:
        print("PROBE FAILED -- the measured directions stopped reproducing:")
        for f in fail:
            print("  " + f)
        return 1
    print("PROBE OK: coherent EXACT on 12/12 (N x structure); cancelling benign off the")
    print("near-cancelling source; near-cancelling channel live; and its factor DECREASES")
    print(f"with N ({a:.1f} -> {b:.1f} -> {c:.1f}), so it is NOT N-scaling.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
