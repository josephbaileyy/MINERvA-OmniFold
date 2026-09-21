#!/usr/bin/env python3
"""Re-measure, from THIS lane, the refutation of its own §5.7 claim.

`PROPOSAL-20260916-B-and-S-bounded-determinism-control.md` §5.7 asserted that
`((1+gamma)**2 - 1)` "bounds every projection" of the inflated block. That is FALSE.
Refuted by owners.tsv:15 at 5a6d32fb34b99da2f3974e46e22082be0a746d3d (T5d); this probe is
this lane's INDEPENDENT reproduction, written so the claim is never taken on relay again.

WHY THE ORIGINAL VERIFICATION MISSED IT: the fixture was entrywise non-negative, so it
sampled only the regime where the bound holds. A fixture drawn from the rule cannot
disagree with it. The three blocks below are all PSD and all weights are non-negative --
what changes is the SIGN STRUCTURE of the block's entries on the projected directions.

Run: python3 docs/orchestration/probes/probe-20260917-projection-bound-counterexample.py
Exits 0 when the refutation reproduces (i.e. when rows 2 and 3 VIOLATE the limit).
"""
import sys

import numpy as np

GAMMA = 0.30
LIMIT = (1.0 + GAMMA) ** 2 - 1.0
N_DRAW = 200_000

CASES = (
    ("entrywise non-negative", np.array([[1.0, 0.5], [0.5, 1.0]]), False),
    ("anti-correlated -0.999", np.array([[1.0, -0.999], [-0.999, 1.0]]), True),
    ("exactly singular -1.0", np.array([[1.0, -1.0], [-1.0, 1.0]]), True),
)


def worst_projected_ratio(C, *, n_draw=N_DRAW, seed=0):
    """max over non-negative w and |gamma_i| <= GAMMA of |w' dC w| / |w' C w|.

    `dC = G C + C G + G C G` is EXACT for finite diagonal G (that part of §5.7 stands);
    the question is only whether the scalar factor survives a projection.
    """
    rng = np.random.default_rng(seed)
    n = C.shape[0]
    worst = 0.0
    for _ in range(n_draw):
        w = rng.random(n)                              # non-negative contracting weights
        G = np.diag(rng.choice([-GAMMA, GAMMA], size=n))
        dC = G @ C + C @ G + G @ C @ G
        den = w @ C @ w
        if abs(den) < 1e-300:
            continue
        ratio = abs(w @ dC @ w) / abs(den)
        worst = max(worst, ratio)
    return worst


def main():
    print(f"gamma = {GAMMA}   limit ((1+gamma)^2 - 1) = {LIMIT:.4f}   draws = {N_DRAW}")
    failures = []
    for name, C, expect_violation in CASES:
        eig = np.linalg.eigvalsh(C)
        psd = bool(eig[0] >= -1e-12)
        worst = worst_projected_ratio(C)
        violates = worst > LIMIT * (1.0 + 1e-9)
        mark = "VIOLATES" if violates else "holds"
        print(f"  {name:24s} eig=({eig[0]:+.3f},{eig[1]:+.3f}) PSD={psd}  "
              f"worst={worst:.4g}  {mark}")
        if violates != expect_violation:
            failures.append(f"{name}: expected violation={expect_violation}, got {violates}")
    if failures:
        print("\nPROBE FAILED -- the refutation did not reproduce:")
        for f in failures:
            print(f"  {f}")
        return 1
    print("\nRefutation reproduces. 'Non-negative contracting weights' is NOT the sufficient")
    print("condition: the inflated block's entries must also be non-negative on the projected")
    print("directions, and the failure is UNBOUNDED because w'Cw can approach zero.")
    print("LIVE, not contrived: AGENTS.md:27 records the historical 3D block-sum at rank 247.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
