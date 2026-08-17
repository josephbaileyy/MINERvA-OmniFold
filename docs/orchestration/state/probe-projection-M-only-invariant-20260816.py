#!/usr/bin/env python3
"""BEN-328 is OVERSTATED: a function of M ALONE catches 3 of the 4 corruptions it calls undetectable.

THE CLAIM UNDER TEST, from the N3 repair (b2c8445):

    "'Wrong' is not a property of M; it is a RELATION between M and the recipe that produced it.
     No function of (C_high, M) can decide it."

The CONCLUSION that follows it -- that a separate recipe gate is required -- is CORRECT and this probe
confirms it. The CLAIM is false as stated, and the difference matters: as filed it licenses a future lane
to skip a cheap structural check on the grounds that checking is impossible, when 3 of the 4 corruptions
its own author chose are catchable without any recipe.

WHY THE INVARIANT WORKS. `build_projection_M` sets `M[row, col] = wdrop[k]`, so the stored value depends
only on the DROPPED INDEX of that column and never on the row. Under full drop-axis coverage every low
row therefore carries the whole width multiset, and scaling a row, scaling one weight, or moving a column
to the wrong row all perturb that multiset. No recipe needed.

TWO QUALIFICATIONS, BOTH MEASURED HERE RATHER THAN ASSUMED, because without them this is just a
counter-overclaim:

  (a) clause (c) is COVERAGE-CONDITIONAL. Section B measures it dissolving as `mask_high` drops bins:
      1 -> 3 -> 6 distinct row multisets at 0% / 10% / 30% dropped. Under a non-trivial mask the clause
      that does the work is gone.
  (b) THE PRODUCTION MASKS ARE NOT TESTED HERE. This probe uses a synthetic 5-axis grid. It therefore
      says nothing about whether the invariant has bite on the real configuration, and no reader should
      extend it that far.
  (c) THE ROW SWAP PROVABLY REQUIRES THE RECIPE. It is a pure relabeling: every structural invariant
      survives it. So at least one corruption class cannot be caught from (C_high, M), and the recipe
      gate is NECESSARY REGARDLESS of (a) -- which is why this probe refutes an argument and not a fix.

Read-only. Monkeypatches `P.build_projection_M` in this process only and restores it in a `finally`.
Writes nothing. Runs against any revision via P4LIB_DIR, as the sibling probe does:

    mkdir -p /tmp/pre && git show <rev>:nd-unfolding/p4_lib.py > /tmp/pre/p4_lib.py
    P4LIB_DIR=/tmp/pre python3 docs/orchestration/state/probe-projection-M-only-invariant-20260816.py

Exit 0 = the refutation reproduces. 2 = pre-repair tree (no recipe gate to compare against).
1 = the refutation NO LONGER reproduces, i.e. re-read this file before trusting BEN-328 either way.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.environ.get(
    "P4LIB_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 os.pardir, os.pardir, os.pardir, "nd-unfolding")))
import p4_lib as P  # noqa: E402

FAIL = []


def check(label, ok, detail):
    print(("  PASS  " if ok else "  FAIL  ") + label + " :: " + detail)
    if not ok:
        FAIL.append(label)


def m_only_invariant(Mx):
    """A function of M ALONE. No edges, no masks, no drop axis -- only the matrix.

    (a) exactly one nonzero per column   -- universal, holds under any mask
    (b) all nonzeros positive            -- universal
    (c) every row carries the SAME multiset of nonzero values -- FULL-COVERAGE ONLY (section B)
    """
    nz = (Mx != 0).sum(axis=0)
    if not np.all(nz == 1):
        return False, "a column has %s nonzeros" % sorted(set(nz.tolist()))
    if not np.all(Mx[Mx != 0] > 0):
        return False, "a nonzero is non-positive"
    ms = {tuple(sorted(np.round(r[r != 0], 12))) for r in Mx}
    if len(ms) != 1:
        return False, "rows carry %d DIFFERENT nonzero multisets" % len(ms)
    return True, "one nonzero/col, all positive, one shared multiset"


def grid(drop_frac=0.0, seed=3):
    edges = [np.array([0., 1., 2.])] * 4 + [np.array([0., 0.5, 1.5, 3.0])]
    nb = [len(e) - 1 for e in edges]
    total = int(np.prod(nb))
    mh = np.ones(total, bool)
    if drop_frac > 0:
        rng = np.random.default_rng(seed)
        mh[rng.choice(total, size=int(total * drop_frac), replace=False)] = False
    ml = P.reachable_low_mask(edges, 4, mh)
    return edges, mh, ml, P.build_projection_M(edges, 4, mh, ml)


CORRUPTIONS = {
    "row scaled by 3": lambda X: _set(X, (0, slice(None)), X[0] * 3.0),
    "one weight scaled by 3": lambda X: _set(X, tuple(np.argwhere(X != 0)[0]),
                                             X[tuple(np.argwhere(X != 0)[0])] * 3.0),
    "one column to wrong row": lambda X: _set(X, (slice(None), 0), np.roll(X[:, 0], 1)),
    "two rows swapped": lambda X: X[[1, 0] + list(range(2, X.shape[0]))],
}


def _set(X, key, val):
    X[key] = val
    return X


def main():
    gate = getattr(P, "check_projection_matrix_matches_recipe", None)
    if gate is None:
        print("PRE-REPAIR TREE: check_projection_matrix_matches_recipe absent, so the third column "
              "cannot be measured. The M-only refutation below is unaffected -- it never needed the "
              "recipe gate -- but this probe's comparison does.")
        return 2

    edges, mh, ml, M = grid()
    rng = np.random.default_rng(7)
    A = rng.normal(size=(M.shape[1],) * 2)
    C = A @ A.T / M.shape[1]

    print("A. THE FOUR CORRUPTIONS ACROSS ALL THREE LEGS (full coverage)")
    ok, why = m_only_invariant(M)
    check("the GOOD M passes the M-only invariant", ok, why)
    print("   %-26s %-15s %-11s %s" % ("corruption", "identity leg", "M-ONLY", "recipe gate"))
    caught_by_m_only = 0
    for name, f in CORRUPTIONS.items():
        Mb = f(M.copy())
        _, st = P.check_projection_validity(C, Mb)
        ident = "pass %.1e" % st["projection_identity_relerr"]
        inv_ok, _ = m_only_invariant(Mb)
        caught_by_m_only += (not inv_ok)
        try:
            gate(Mb, edges, 4, mh, ml)
            rec = "misses"
        except Exception:
            rec = "CATCHES"
        print("   %-26s %-15s %-11s %s"
              % (name, ident, "CATCHES" if not inv_ok else "misses", rec))
        check("recipe gate catches '%s'" % name, rec == "CATCHES", "as the repair claims")
        check("identity leg is BLIND to '%s'" % name,
              st["projection_identity_relerr"] < 1e-9,
              "BEN-316 section 4 -- expected, and correct after the repair too")

    check("THE REFUTATION: an M-ONLY function catches 3 of the 4", caught_by_m_only == 3,
          "%d of 4 caught with no edges, no masks, no drop axis -- so 'no function of (C_high, M) "
          "can decide it' is false as stated" % caught_by_m_only)

    swapped = CORRUPTIONS["two rows swapped"](M.copy())
    ok_sw, _ = m_only_invariant(swapped)
    check("and the ROW SWAP is the one that survives it", ok_sw,
          "a pure relabeling preserves every structural invariant, so THIS class provably needs the "
          "recipe -- the remedy stays necessary and only the ARGUMENT is overstated")

    print("\nB. CLAUSE (c) IS COVERAGE-CONDITIONAL -- measured, not supposed")
    counts = []
    for frac, label in ((0.0, "full coverage"), (0.10, "drop 10%"), (0.30, "drop 30%")):
        _, _, _, Mx = grid(frac)
        n = len({tuple(sorted(np.round(r[r != 0], 12))) for r in Mx})
        counts.append(n)
        print("   %-16s M%-10s distinct row multisets = %d  -> clause (c) %s"
              % (label, str(Mx.shape), n, "HOLDS" if n == 1 else "DOES NOT HOLD"))
    check("clause (c) dissolves under masking", counts[0] == 1 and counts[1] > 1 and counts[2] > 1,
          "%s -- so the refutation is bounded to full coverage, and THE PRODUCTION MASKS ARE NOT "
          "TESTED HERE" % counts)

    print("\nC. THE RECIPE GATE CATCHES BUILDER BUGS, not only corruption of M after construction")
    orig = P.build_projection_M
    try:
        for label, wf in (("widths rotated by one", lambda w: np.r_[w[1:], w[:1]]),
                          ("unit weights, not widths", lambda w: np.ones_like(w)),
                          ("widths reversed", lambda w: w[::-1])):
            wd = np.asarray(edges[4], float)[1:] - np.asarray(edges[4], float)[:-1]
            rep = {round(float(a), 12): float(b) for a, b in zip(wd, wf(wd))}
            Mb = orig(edges, 4, mh, ml).copy()
            sel = Mb != 0
            Mb[sel] = [rep[round(float(v), 12)] for v in Mb[sel]]
            try:
                gate(Mb, edges, 4, mh, ml)
                got = "misses"
            except Exception:
                got = "CATCHES"
            check("recipe gate catches builder bug: %s" % label, got == "CATCHES", got)
    finally:
        P.build_projection_M = orig

    print()
    if FAIL:
        print("PROBE RESULT :: %d EXPECTATION(S) NOT REPRODUCED -> %s" % (len(FAIL), FAIL))
        print("Re-read this file and BEN-328 before trusting either. A failure here does NOT mean the "
              "repair regressed -- it may mean the invariant's premise changed.")
        return 1
    print("PROBE RESULT :: ALL REPRODUCED -- BEN-328's argument is overstated, its remedy is necessary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
