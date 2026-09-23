"""Tests for the 100-replica PET C_stat combiner (#15).

Covers the pure covariance/gate math in `compute_cstat`: replica-mean centering,
CV>0 masking/order, symmetry, PSD via the small Gram spectrum, finite diagonal,
and the known-covariance closed form. Pure numpy (login-runnable)."""
import sys
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND / "pet"))

import combine_cstat_bkgsub_100rep as cc  # noqa: E402


class ComputeCstatTests(unittest.TestCase):
    def test_masks_on_cv_positive_and_orders(self):
        # 5 bins; only bins 0,2,4 have cv>0 -> reported subspace has 3 bins
        X = np.arange(20.0).reshape(4, 5)
        cv = np.array([1.0, 0.0, 2.0, 0.0, 3.0])
        C, rep, sig, rel, stats, gates = cc.compute_cstat(X, cv)
        self.assertTrue(np.array_equal(rep, np.array([True, False, True, False, True])))
        self.assertEqual(C.shape, (3, 3))
        self.assertEqual(stats["n_reported_bins"], 3)

    def test_symmetric_psd_finite(self):
        rng = np.random.default_rng(0)
        cv = np.abs(rng.normal(size=40)) + 0.1        # all cv>0
        X = cv[None, :] * (1.0 + 0.05 * rng.normal(size=(30, 40)))
        C, rep, sig, rel, stats, gates = cc.compute_cstat(X, cv)
        self.assertEqual(gates["symmetry_max_abs"], 0.0)   # C=Z^T Z is exactly symmetric
        self.assertTrue(gates["psd"])
        self.assertTrue(gates["finite_diagonal"])
        # Gram nonzero spectrum is >= ~0
        self.assertGreaterEqual(gates["gram_min_eigenvalue"], -1e-9 * gates["gram_max_eigenvalue"])

    def test_known_covariance_two_replicas(self):
        # Two replicas: C = outer(d,d)/ (n-1) with d = (x1-x2)/... centered.
        # For n=2, Z = [[+delta/2],[-delta/2]] per bin, C = outer(delta,delta)/2.
        cv = np.array([1.0, 1.0])
        x1 = np.array([1.0, 2.0]); x2 = np.array([3.0, 6.0])
        X = np.vstack([x1, x2])
        C, rep, sig, rel, stats, gates = cc.compute_cstat(X, cv)
        delta = x1 - x2                                # [-2, -4]
        expected = np.outer(delta, delta) / 2.0        # /(n-1)=1... n-1=1, but centering halves
        # For n=2: mean=(x1+x2)/2, Z rows = +/- delta/2, C=Z^T Z/(n-1)=2*(delta/2)^2/1
        expected = np.outer(delta / 2, delta / 2) * 2.0
        np.testing.assert_allclose(C, expected, rtol=1e-12, atol=0)
        np.testing.assert_allclose(sig, np.sqrt(np.diag(expected)), rtol=1e-12)

    def test_rejects_too_few_replicas(self):
        with self.assertRaises(ValueError):
            cc.compute_cstat(np.ones((1, 5)), np.ones(5))

    def test_rejects_shape_mismatch(self):
        with self.assertRaises(ValueError):
            cc.compute_cstat(np.ones((3, 5)), np.ones(4))


if __name__ == "__main__":
    unittest.main(verbosity=2)
