#!/usr/bin/env python3
"""`p4_validate_active_lateral_fps.mat_gates`'s diagonal bound must be relative and able to fail at the real scale.

OI-12. The bound read `d >= -1e-30`, absolute, beside an asymmetry check and a PSD check that are both relative
(docs/orchestration/VALIDATOR-TOLERANCE-UNITS-20260808.md §2). It now reads `d >= -1e-12 * |ev[-1]|`, line 68's
units. The scale here is the adopted FPS lateral's own: its receipt's `sqrt_trace` over its 266 reported cells.

Honest severity, as for `p4_lib`'s BEN-044 repair (tests/test_p4_guard_mutations.py): the old bound was LATENT,
not a live hole. For symmetric input min(diag) >= min(eigenvalue), so a negative diagonal is a negative eigenvalue,
and the relative PSD check rejects it first. With the same threshold the repaired bound is still subsumed. The
tests show that rather than claim more.
"""
import json
import os
import sys
import unittest

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ND)

import p4_validate_active_lateral_fps as v  # noqa: E402

RECEIPT = os.path.join(ND, "active_universe_5d", "fps", "covariance", "p4_summary_active_lateral_fps.json")


def _adopted():
    with open(RECEIPT) as f:
        return json.load(f)["active"]


def _gram_at_adopted_scale(seed=0):
    """A full-rank 266-cell covariance whose trace equals the adopted matrix's."""
    a = _adopted()
    n = a["n_reported"]
    Z = np.random.default_rng(seed).normal(size=(2 * n, n))
    Z -= Z.mean(axis=0)
    C = Z.T @ Z
    return C * (a["sqrt_trace"] ** 2 / np.trace(C))


def _isolate(C, k, value):
    """Zero cell k's row and column and set its variance, so its eigenvalue is exactly `value`."""
    C = C.copy()
    C[k, :] = 0.0
    C[:, k] = 0.0
    C[k, k] = value
    return C


class RelativeDiagonalAtTheRealScale(unittest.TestCase):
    def setUp(self):
        self.C = _gram_at_adopted_scale()
        self.lam = float(np.linalg.eigvalsh(self.C)[-1])

    def test_the_scale_is_the_adopted_matrix(self):
        a = _adopted()
        self.assertEqual(self.C.shape, (266, 266))
        self.assertAlmostEqual(float(np.sqrt(np.trace(self.C))) / a["sqrt_trace"], 1.0, places=12)
        self.assertLess(float(np.max(np.diag(self.C))), 1e-75)

    def test_a_clean_covariance_passes(self):
        r = v.mat_gates(self.C, "clean")
        self.assertTrue(r["diag_finite_nonneg"])
        self.assertTrue(r["psd"])

    def test_the_old_absolute_bound_accepted_a_corruption_49_orders_above_the_signal(self):
        C = self.C.copy(); C[3, 3] = -1e-31
        self.assertTrue(bool(np.all(np.diag(C) >= -1e-30)), "the BEN-044 shape")

    def test_the_repaired_bound_rejects_that_corruption(self):
        C = self.C.copy(); C[3, 3] = -1e-31
        self.assertFalse(v.mat_gates(C, "neg-diag")["diag_finite_nonneg"])

    def test_the_psd_check_already_rejected_it(self):
        """Why the old bound was latent, not exploitable."""
        C = self.C.copy(); C[3, 3] = -1e-31
        self.assertFalse(v.mat_gates(C, "neg-diag")["psd"])

    def test_the_bound_both_sides_of_its_threshold(self):
        inside = v.mat_gates(_isolate(self.C, 5, -1e-13 * self.lam), "inside")
        outside = v.mat_gates(_isolate(self.C, 5, -2e-12 * self.lam), "outside")
        self.assertTrue(inside["diag_finite_nonneg"], "round-off at the real scale must pass")
        self.assertFalse(outside["diag_finite_nonneg"])

    def test_the_verdict_does_not_depend_on_the_units(self):
        """Relative means the same matrix in O(1) units gives the same verdicts."""
        for value in (-1e-13 * self.lam, -2e-12 * self.lam):
            C = _isolate(self.C, 5, value)
            small, big = v.mat_gates(C, "1e-79"), v.mat_gates(C / self.lam, "O(1)")
            self.assertEqual((small["diag_finite_nonneg"], small["psd"]), (big["diag_finite_nonneg"], big["psd"]))

    def test_passing_psd_implies_passing_the_diagonal(self):
        """The subsumption, on the adopted receipt's own numbers: its min/max eigenvalue sits inside the bound."""
        a = _adopted()
        self.assertTrue(a["psd"] and a["diag_finite_nonneg"])
        self.assertGreaterEqual(a["min_over_max_eig"], -1e-12)

    def test_a_zero_matrix_still_passes(self):
        """`|ev[-1]| = 0` makes the bound `d >= 0`; an all-zero diagonal meets it."""
        self.assertTrue(v.mat_gates(np.zeros((4, 4)), "zero")["diag_finite_nonneg"])

    def test_a_non_finite_diagonal_is_refused_before_the_bound(self):
        """`eigvalsh` raises on a NaN, so the matrix never reaches the diagonal bound: refused, not passed."""
        C = self.C.copy(); C[0, 0] = np.nan
        with self.assertRaises(np.linalg.LinAlgError):
            v.mat_gates(C, "nan")


if __name__ == "__main__":
    unittest.main()
