#!/usr/bin/env python3
"""The 100-replica C_stat covariance gates must be RELATIVE to the matrix scale, not absolute.

`combine_cstat_bkgsub_100rep.py` shipped (untracked) with two gates that could not fail on this
problem's numbers:

    symmetry   sym_err > 1e-30                        absolute
    PSD        min_eig >= -1e-9 * max(max_eig, 1.0)   the max(...,1.0) pins it to -1e-9 absolute

Measured on the real products, `max|C| = 8.13e-79` and `max_eig = 2.72e-77`, so both thresholds sit
~49 and ~68 orders of magnitude above the quantities they bound. An arbitrarily wrong matrix passes.

These tests are the regression guard for the fix, and the second one is the POWER PROOF: it injects a
gross asymmetry and requires the new gate to fire where the old threshold would not have. Without
that, `test_clean_matrix_passes` alone would be satisfied by a gate that always returns True -- the
BEN-032 / BEN-040 vacuous-check family this repo keeps rediscovering.

Same defect family as the `atol=1e-8` numpy default compared against cross sections of ~1e-38 (CLM-011,
2026-08-06): an absolute tolerance inherited into a problem whose natural scale is ~1e-80.
"""
import os
import sys
import unittest

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PET = os.path.join(ND, "pet")
if PET not in sys.path:
    sys.path.insert(0, PET)

import combine_cstat_bkgsub_100rep as mod  # noqa: E402


def _toy(seed=0, n_rep=8, n_bin=20):
    """Replica cross sections at the REAL scale (~1e-38 xsec, so C ~ 1e-80)."""
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n_rep, n_bin)) * 1e-40
    cv = np.abs(rng.normal(size=n_bin)) * 1e-38
    return X, cv


class CovarianceGatesAreScaleAware(unittest.TestCase):
    def test_module_is_importable_outside_the_cluster(self):
        """`_ND` used to be hardcoded to /pscratch, which made every test below impossible."""
        self.assertTrue(os.path.isdir(mod._ND), mod._ND)
        self.assertFalse(mod._ND.startswith("/pscratch"),
                         "_ND must resolve from __file__, not a scratch-absolute path")

    def test_clean_matrix_passes(self):
        X, cv = _toy()
        C, rep, sig, rel, stats, gates = mod.compute_cstat(X, cv)
        self.assertTrue(gates["symmetry_ok"])
        self.assertTrue(gates["psd"])
        self.assertTrue(gates["finite_diagonal"])
        self.assertEqual(C.shape[0], C.shape[1])

    def test_tolerance_tracks_the_matrix_scale(self):
        """The tolerance must move with the data, which an absolute threshold cannot do."""
        X, cv = _toy()
        _, _, _, _, _, g1 = mod.compute_cstat(X, cv)
        _, _, _, _, _, g2 = mod.compute_cstat(X * 1e6, cv)
        self.assertGreater(g2["covariance_scale_max_abs"], g1["covariance_scale_max_abs"])
        self.assertGreater(g2["symmetry_tolerance_relative"], g1["symmetry_tolerance_relative"])
        # and it is genuinely proportional, not merely monotone
        r_scale = g2["covariance_scale_max_abs"] / g1["covariance_scale_max_abs"]
        r_tol = g2["symmetry_tolerance_relative"] / g1["symmetry_tolerance_relative"]
        self.assertAlmostEqual(r_scale / r_tol, 1.0, places=6)

    def test_POWER_the_old_absolute_gate_would_have_blessed_a_broken_matrix(self):
        """Inject an asymmetry of half the largest entry. The old 1e-30 gate does not fire."""
        X, cv = _toy()
        C, _, _, _, _, gates = mod.compute_cstat(X, cv)
        scale = float(np.abs(C).max())
        bad = C.copy()
        bad[0, 1] += 0.5 * scale
        sym_bad = float(np.abs(bad - bad.T).max())

        self.assertGreater(sym_bad, 0.0)
        # the defect: the old ABSOLUTE threshold cannot see a corruption at this scale
        self.assertFalse(sym_bad > 1e-30,
                         "the old absolute gate would have to fire for this test to be about "
                         "anything -- if it does, the scale assumption changed")
        # the fix: the relative threshold does
        self.assertGreater(sym_bad, gates["symmetry_tolerance_relative"])

    def test_POWER_the_old_psd_tolerance_was_absolute(self):
        """`-1e-9 * max(max_eig, 1.0)` collapses to -1e-9 whenever max_eig < 1."""
        X, cv = _toy()
        _, _, _, _, _, gates = mod.compute_cstat(X, cv)
        max_eig = gates["gram_max_eigenvalue"]
        self.assertLess(max_eig, 1.0, "the toy must sit at the real ~1e-77 scale")
        old_tol = -1e-9 * max(max_eig, 1.0)
        new_tol = -1e-9 * max_eig
        self.assertAlmostEqual(old_tol, -1e-9, places=12)      # pinned, scale-blind
        self.assertGreater(new_tol, old_tol)                    # strictly tighter
        # a negative eigenvalue this problem can produce passes the old gate and fails the new one
        probe = -1e-3 * max_eig
        self.assertGreaterEqual(probe, old_tol)                 # old: blessed
        self.assertLess(probe, new_tol)                         # new: rejected


if __name__ == "__main__":
    unittest.main(verbosity=2)
