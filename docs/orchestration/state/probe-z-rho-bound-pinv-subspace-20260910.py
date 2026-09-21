#!/usr/bin/env python3
"""Falsification probe: RECOMMENDATION-20260910 section 2.1's bound COMPOSED WITH pinv.

Written 2026-09-10 by the Z-criteria independent assessor, against
`RECOMMENDATION-20260910-z-scientific-acceptance-criteria.md` sha256
622a9dcd332d99d6d671c697b3a34003bd20080fe241d0b8147ab5349de3175f at commit 2ebdf095,
and `state/probe-z-criteria-acceptance-mathematics-20260910.py` sha256
e54aa83de40e183d79b33d7b007e72355992ce971eabd12f8b3f5d1ee2cdf9de.

WHAT IS NOT UNDER ATTACK: section 2.1's theorem and section 2.2's projection monotonicity.
Both proofs were checked analytically and are correct, and the theorem is CONFIRMED here as
a control, with the exact inverse.

WHAT THIS SHOWS: the theorem is proven for `d' C^-1 d`, while the consumer computes
`d' pinv(C) d` (`eavail_generator_significance.py:107,132`) and the recommendation's own
`_chi2` (probe :81) uses pinv too. When the two members' retained SUBSPACES differ, the
bound does not transfer -- and B.1(i)/D.2 gate INCONCLUSIVE on the retained RANK, which
D.1(c) itself argues is not the retained subspace. Rank can be equal while the subspace
swaps, so the guard stays silent on a violating member.

LIMIT, stated so this is not over-read: the construction is SYNTHETIC, at condition number
~1e15. Whether real Z members exhibit a same-rank subspace swap is UNMEASURED and is not
claimed here. What is claimed is that the guard as specified does not exclude it, in the
regime the consumer's own comment (:98-101) says it operates in.

Run:  python3 docs/orchestration/state/probe-z-rho-bound-pinv-subspace-20260910.py
No compute, no cluster, no ROOT. Pure numpy; nothing outside this file is read.
"""
import numpy as np

np.set_printoptions(precision=6)


def rho(C0, Ck):                                    # verbatim from the probe, :65
    w, V = np.linalg.eigh(C0)
    if w[0] <= 0:
        raise ValueError("baseline not PD")
    inv_sqrt = V @ np.diag(w ** -0.5) @ V.T
    E = inv_sqrt @ (Ck - C0) @ inv_sqrt
    return float(np.linalg.norm((E + E.T) / 2.0, 2))


def chi2_pinv(C, d):                                # verbatim from the probe, :81
    return float(d @ np.linalg.pinv(C) @ d)


def chi2_exact(C, d):
    return float(d @ np.linalg.inv(C) @ d)


def retained_rank(C, rcond=1e-15):
    s = np.linalg.svd(C, compute_uv=False)
    return int((s > rcond * s.max()).sum())


# Two near-cutoff modes SWAP which side of numpy's default pinv cutoff they sit on.
# numpy pinv default rcond = 1e-15, cutoff = rcond * sigma_max. sigma_max = 1 here.
A, B = 3, 7                                          # the two swapping modes
lam0 = np.ones(10)
lamk = np.ones(10)
lam0[A], lamk[A] = 1.2e-15, 0.8e-15                  # A: retained -> discarded
lam0[B], lamk[B] = 0.8e-15, 1.2e-15                  # B: discarded -> retained

C0, Ck = np.diag(lam0), np.diag(lamk)
d = np.zeros(10)
d[A] = 1.0                                           # all weight on mode A

r = rho(C0, Ck)
lo, hi = chi2_exact(C0, d) / (1 + r), chi2_exact(C0, d) / (1 - r)

print("=" * 78)
print("FALSIFICATION ATTEMPT -- rho bound composed with the consumer's pinv")
print("=" * 78)
print(f"  rho(C0, Ck)                      = {r:.6f}      (bound needs rho < 1)")
print(f"  retained rank, baseline / member = {retained_rank(C0)} / {retained_rank(Ck)}"
      f"      <- IDENTICAL, so D.2's rank-change INCONCLUSIVE does NOT fire")
print(f"  retained SUBSPACE               : mode {A} in baseline, mode {B} in member -- CHANGED")
print()
print("  CONTROL -- the theorem itself, with the EXACT inverse:")
ce0, cek = chi2_exact(C0, d), chi2_exact(Ck, d)
print(f"    chi2_0 = {ce0:.6e}   chi2_k = {cek:.6e}")
print(f"    bound  = [{lo:.6e}, {hi:.6e}]")
print(f"    holds  = {lo <= cek <= hi}   <- theorem CONFIRMED, not under attack")
print()
print("  THE CONSUMED FORM -- pinv, exactly as `_chi2` at probe:81 and consumer :107,132:")
cp0, cpk = chi2_pinv(C0, d), chi2_pinv(Ck, d)
lo_p, hi_p = cp0 / (1 + r), cp0 / (1 - r)
print(f"    chi2_0 = {cp0:.6e}   chi2_k = {cpk:.6e}")
print(f"    bound  = [{lo_p:.6e}, {hi_p:.6e}]")
holds = lo_p <= cpk <= hi_p
print(f"    holds  = {holds}")
if not holds:
    print(f"    VIOLATED: chi2_k / lower_bound = {cpk / lo_p:.6e}  (must be >= 1)")
    print(f"    chi2_k is {lo_p / max(cpk, 1e-300):.3e}x BELOW the bound's floor")
print()
print("  Direction of the error, which is what decides whether it can pass a gate:")
print(f"    chi2 collapses {cp0:.3e} -> {cpk:.3e}, so p rises and Nsigma FALLS.")
print("    A 'stays ABOVE T' claim is thus broken while rho reports"
      f" {r:.3f} -- comfortably inside any rho_crit at large ndf.")
print()
print("  Why the probe's own section 1 did not find this:")
print("    its ensemble's baselines are well-conditioned, so no eigenvalue sits near")
print("    the pinv cutoff and the retained subspace never changes. The consumer's own")
print("    comment (:98-101) says its matrices CAN be near-singular -- the regime the")
print("    ensemble omits is the regime the consumer says it operates in.")


# ---------------------------------------------------------------- the remedy, tested
print()
print("=" * 78)
print("REMEDY TEST -- gate on the retained SUBSPACE, not the retained RANK")
print("=" * 78)


def retained_set(C, rcond=1e-15):
    s, V = np.linalg.eigh(C)
    return frozenset(np.flatnonzero(s > rcond * s.max()).tolist()), s, V


def subspace_identical(C0, Ck, rcond=1e-15):
    """Compare the ORTHOGONAL PROJECTORS onto the retained subspaces, not their dimensions."""
    out = []
    for C in (C0, Ck):
        s, V = np.linalg.eigh(C)
        keep = s > rcond * s.max()
        Vk = V[:, keep]
        out.append(Vk @ Vk.T)
    return float(np.linalg.norm(out[0] - out[1], 2))


cases = {
    "(1) the violating case above -- subspace SWAPS at fixed rank": (C0, Ck),
    "(2) same rho, subspace PRESERVED (both near-cutoff modes retained)": (
        np.diag(np.where(np.arange(10) == A, 1.2e-13, np.where(np.arange(10) == B, 0.8e-13, 1.0))),
        np.diag(np.where(np.arange(10) == A, 0.8e-13, np.where(np.arange(10) == B, 1.2e-13, 1.0))),
    ),
}
for label, (X0, Xk) in cases.items():
    r_ = rho(X0, Xk)
    gap = subspace_identical(X0, Xk)
    c0_, ck_ = chi2_pinv(X0, d), chi2_pinv(Xk, d)
    lo_, hi_ = c0_ / (1 + r_), c0_ / (1 - r_)
    ok = lo_ <= ck_ <= hi_
    fires = gap > 1e-8
    print(f"\n  {label}")
    print(f"    rho = {r_:.6f}   rank {retained_rank(X0)}/{retained_rank(Xk)}"
          f"   ||P_0 - P_k||_2 = {gap:.3e}")
    print(f"    bound holds under pinv           : {ok}")
    print(f"    SUBSPACE guard fires INCONCLUSIVE: {fires}")
    verdict = ("CAUGHT" if (fires and not ok) else
               "correctly silent" if (not fires and ok) else
               "GUARD IS WRONG")
    print(f"    -> {verdict}")

print()
print("  So the subspace guard is bidirectional: it FIRES on the bad case the rank guard")
print("  waves through, and stays SILENT on a same-rho case whose subspace is preserved.")
print("  And the restriction is a projection with orthonormal columns, so the")
print("  recommendation's OWN section 2.2 makes the full-space rho a valid bound on the")
print("  restricted form once subspace identity is required. The remedy uses its own result.")
