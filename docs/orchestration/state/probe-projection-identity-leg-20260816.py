#!/usr/bin/env python3
"""Probe for BEN-316: what can `p4_lib.check_projection_validity`'s second leg actually measure?

The executable form of the finding, per CLAUDE.md's rule that a check costs zero and cannot be
skipped while a document costs tokens in every future session. Read-only: imports p4_lib, mutates
`P.project` in this process only, restores it, and writes nothing.

    cd nd-unfolding && python3 ../docs/orchestration/state/probe-projection-identity-leg-20260816.py

Findings it reproduces (FINDING-20260816-the-gate-that-measures-blas-blocking-noise.md):
  1. the row loop IS `MH @ M.T` -- so `err` measures BLAS accumulation order, nothing else;
  2. measured ~1.9e-16 against a 1e-9 threshold: ~5.4e6x headroom, and EXACTLY 0.0 on the repo
     test's own fixture, where `assertLess(relerr, 1e-12)` therefore cannot fail;
  3. it DOES catch a value-changing edit to project() -- so "a check that cannot fail" is too
     strong; it is a source-drift regression guard;
  4. it does NOT catch an error in the premise both legs share -- a corrupted M passes.
"""
import os
import sys

import numpy as np

# Locate nd-unfolding from THIS FILE, not from cwd: running a probe by path puts the probe's own
# directory on sys.path and not the caller's, so `cd nd-unfolding && python3 ../path/to/probe.py`
# would otherwise fail on the import. Measured 2026-08-16.
#
# P4LIB_DIR OVERRIDE, added 2026-08-16 BEFORE the N3 repair landed, so that "before vs after" is one
# command rather than a narrative. `check_projection_validity` is expected to change, and once it does
# this probe measures the NEW behaviour and the pre-repair numbers become unreproducible from the
# working tree alone. That is exactly BEN-317's rule -- record the state before the thing that
# overwrites it -- applied to this lane's own baseline. To measure any revision:
#
#   mkdir -p /tmp/pre && git show <rev>:nd-unfolding/p4_lib.py > /tmp/pre/p4_lib.py
#   P4LIB_DIR=/tmp/pre python3 docs/orchestration/state/probe-projection-identity-leg-20260816.py
#
# PRE-REPAIR BASELINE, recorded here so a later reader does not have to trust a commit message:
#   nd-unfolding/p4_lib.py sha256 aa3470e45040398a00064f83fef853cffc3172e27fce2ff0d19ac1258bd7de65
#   at HEAD 67c94df. Every number this probe asserts was measured against THAT file.
sys.path.insert(0, os.environ.get(
    "P4LIB_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 os.pardir, os.pardir, os.pardir, "nd-unfolding")))
import p4_lib as P  # noqa: E402

print(f"probing p4_lib from {os.path.dirname(os.path.abspath(P.__file__))}")

FAIL = []       # BEN-316 expectations (sections 1-4): true on the pre- AND post-repair tree
RFAIL = []      # N3-repair expectations (section 5): true ONLY on the repaired tree


def check(label, ok, detail):
    print(("  PASS  " if ok else "  FAIL  ") + label + " :: " + detail)
    if not ok:
        FAIL.append(label)


def rcheck(label, ok, detail):
    """Same, but for the repair's expectations, kept in a SEPARATE bucket. Mixing them would make
    one exit code mean both 'BEN-316 no longer reproduces' and 'the repair has not landed yet',
    which are opposite conclusions."""
    print(("  PASS  " if ok else "  FAIL  ") + label + " :: " + detail)
    if not ok:
        RFAIL.append(label)


def main():
    rng = np.random.default_rng(20260816)
    n_hi, n_lo = 240, 60
    A = rng.normal(size=(n_hi, n_hi))
    C = A @ A.T / n_hi                                     # symmetric PSD
    M = np.zeros((n_lo, n_hi))
    M[np.arange(n_hi) % n_lo, np.arange(n_hi)] = 1.0       # a genuine block-sum projection

    print("1. what the leg measures")
    C_low, st = P.check_projection_validity(C, M)
    err = st["projection_identity_relerr"]
    MH = M @ C
    one_shot = MH @ M.T
    direct = np.zeros_like(C_low)
    for i in range(n_lo):
        direct[i, :] = MH[i, :] @ M.T
    check("row loop equals the one-shot product to float noise only",
          np.max(np.abs(direct - one_shot)) < 1e-12 and not np.array_equal(direct, one_shot),
          "max|direct - MH@M.T| = %.3e, bit-identical=False -> BLAS accumulation order"
          % np.max(np.abs(direct - one_shot)))
    check("project() is bit-identical to the one-shot",
          np.array_equal(C_low, one_shot), "max|diff| = 0.0")
    check("threshold is >=1e6x the measured error",
          1e-9 / max(err, 1e-300) > 1e6,
          "relerr = %.3e vs threshold 1e-9 -> headroom %.2e x" % (err, 1e-9 / max(err, 1e-300)))

    print("2. the repo test's own fixture")
    Ct = np.diag([4.0, 9.0, 16.0])
    Mt = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 1.0]])
    _, stt = P.check_projection_validity(Ct, Mt)
    check("relerr is EXACTLY zero there, so assertLess(relerr, 1e-12) cannot fail",
          stt["projection_identity_relerr"] == 0.0,
          "tests/test_p4_repair.py:143 asserts %r < 1e-12" % stt["projection_identity_relerr"])

    print("3. it DOES catch a value-changing edit to project() -- 'cannot fail' is too strong")
    orig = P.project
    try:
        P.project = lambda C_high, M_: 2.0 * orig(C_high, M_)   # still symmetric, still PSD
        caught = False
        try:
            P.check_projection_validity(C, M)
        except Exception as e:
            caught, msg = True, str(e)
        check("scale-x2 edit to project() is caught", caught,
              msg[:78] if caught else "gate passed a doubled covariance")
    finally:
        P.project = orig

    print("4. it does NOT catch an error in the premise both legs share")
    M_bad = M.copy()
    M_bad[0, :] *= 3.0                                      # wrong projection matrix, not a project() bug
    _, sb = P.check_projection_validity(C, M_bad)
    check("corrupted M passes -- shared-premise errors are invisible",
          sb["projection_identity_relerr"] < 1e-9,
          "relerr = %.3e, gate PASSED on a wrong M" % sb["projection_identity_relerr"])

    # ---------------------------------------------------------------- the N3 repair, 2026-08-16
    # Sections 1-4 are BEN-316's findings and hold on BOTH trees: the identity leg is still blind to
    # a wrong M after the repair, deliberately and by construction, and section 4 must keep passing.
    # What the repair adds is a SEPARATE gate on M, so section 5 FAILS on the pre-repair tree and
    # PASSES after. That is the whole point of the P4LIB_DIR override: before-vs-after is this one
    # command, run twice, and neither run is a narrative.
    print("5. THE REPAIR: is M ITSELF gated, against the recipe that produced it?")
    gate = getattr(P, "check_projection_matrix_matches_recipe", None)
    if gate is None:
        rcheck("a gate on M exists at all", False,
               "check_projection_matrix_matches_recipe absent -- PRE-REPAIR tree: nothing on this "
               "path can see that the MAP is wrong, only that the product was recomputed")
    else:
        edges = [np.array([0., 1., 2.])] * 4 + [np.array([0., 0.5, 1.5, 3.0])]
        nb = [len(e) - 1 for e in edges]
        mh = np.ones(int(np.prod(nb)), bool)
        ml = P.reachable_low_mask(edges, 4, mh)
        Mr = P.build_projection_M(edges, 4, mh, ml)
        st = gate(Mr, edges, 4, mh, ml)
        rcheck("the good M passes the recipe gate", st["projection_M_recipe_max_abs_diff"] == 0.0,
               "max|diff| = %r via %s" % (st["projection_M_recipe_max_abs_diff"],
                                          st["projection_M_recipe_route"]))
        Mr_bad = Mr.copy()
        Mr_bad[0, :] *= 3.0                                 # the SAME corruption as section 4
        caught = False
        try:
            gate(Mr_bad, edges, 4, mh, ml)
        except Exception as e:
            caught, msg = True, str(e)
        rcheck("the corruption that section 4 shows is INVISIBLE to the identity leg is CAUGHT here",
               caught, (msg[:96] if caught else "the recipe gate ACCEPTED a corrupted M"))
    bs = getattr(P, "_block_sum_projection", None)
    if bs is None:
        rcheck("the identity leg has a non-matmul route", False,
               "_block_sum_projection absent -- PRE-REPAIR tree: `direct` is the same BLAS product "
               "re-associated, so the identity measures accumulation order (section 1)")
    else:
        import inspect
        body = inspect.getsource(bs).split('"""')[-1]
        rcheck("that route contains no matrix multiplication",
               "@" not in body and ".dot(" not in body and "matmul" not in body,
               "checked structurally; a numeric check cannot separate two routes that agree to 1e-16")

    print()
    if FAIL:
        print("PROBE RESULT :: %d BEN-316 EXPECTATION(S) NOT REPRODUCED -> %s" % (len(FAIL), FAIL))
        print("A failure in 1-4 means the leg's behaviour CHANGED; re-read BEN-316 before trusting it.")
        return 1
    print("BEN-316 (sections 1-4) :: ALL REPRODUCED -- stands as filed, and section 4 is EXPECTED to "
          "keep passing after the repair: the identity leg is blind to M by construction.")
    if RFAIL:
        print("N3 REPAIR (section 5) :: NOT PRESENT -> %s" % RFAIL)
        print("PROBE RESULT :: PRE-REPAIR TREE -- the defect is live and M is ungated.")
        return 2
    print("N3 REPAIR (section 5) :: PRESENT -- M is gated against its recipe and the corruption that "
          "passes the identity leg at ~1e-17 is rejected.")
    print("PROBE RESULT :: REPAIRED TREE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
