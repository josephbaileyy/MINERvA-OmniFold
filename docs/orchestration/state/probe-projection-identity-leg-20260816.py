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
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                os.pardir, os.pardir, os.pardir, "nd-unfolding"))
import p4_lib as P  # noqa: E402

FAIL = []


def check(label, ok, detail):
    print(("  PASS  " if ok else "  FAIL  ") + label + " :: " + detail)
    if not ok:
        FAIL.append(label)


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

    print()
    if FAIL:
        print("PROBE RESULT :: %d EXPECTATION(S) NOT REPRODUCED -> %s" % (len(FAIL), FAIL))
        print("A failure here means the leg's behaviour CHANGED; re-read BEN-316 before trusting it.")
        return 1
    print("PROBE RESULT :: ALL REPRODUCED -- BEN-316 stands as filed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
