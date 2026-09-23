#!/usr/bin/env python3
"""`p4_validate_active_lateral_fps.mat_gates` must report rank and must not infer the reported count.

KNOWN_ISSUES #46. `psd` is a negativity test, so an exact-zero eigenvalue passes it; the receipt now
carries `rank_at_1em10_lambda_max` beside it. `n_reported` was `sum(diag > 0)`, which drops a reported
cell whose ensemble variance is exactly zero; it is now the matrix dimension, and such cells are
listed in `zero_diag_reported_idx`.
"""
import os
import sys
import unittest

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ND)

import p4_validate_active_lateral_fps as v  # noqa: E402

N_CELLS = 266


def _gram(n_rep, n_cells, seed=0):
    """C = Z^T Z / (n-1) from centred replicas: rank <= n_rep - 1 by construction."""
    rng = np.random.default_rng(seed)
    Z = rng.normal(size=(n_rep, n_cells)) * 1e-39
    Z -= Z.mean(axis=0)
    return Z.T @ Z / (n_rep - 1)


class MatGatesRank(unittest.TestCase):
    def test_rank_deficient_gram_reports_its_rank_while_psd_stays_true(self):
        r = v.mat_gates(_gram(50, N_CELLS), "rank49")
        self.assertTrue(r["psd"])  # psd answers its own question; it is not tightened
        self.assertLessEqual(r["rank_at_1em10_lambda_max"], 49)
        self.assertGreaterEqual(r["rank_at_1em10_lambda_max"], 45)  # not vacuously zero
        self.assertEqual(r["n_reported"], N_CELLS)

    def test_full_rank_matrix_reports_full_rank(self):
        """The field must not read low on a healthy matrix (tests the direction it stays silent)."""
        r = v.mat_gates(_gram(400, N_CELLS, seed=1), "full")
        self.assertEqual(r["rank_at_1em10_lambda_max"], N_CELLS)
        self.assertEqual(r["zero_diag_reported_idx"], [])

    def test_zero_matrix_has_rank_zero(self):
        r = v.mat_gates(np.zeros((N_CELLS, N_CELLS)), "zero")
        self.assertEqual(r["rank_at_1em10_lambda_max"], 0)


class MatGatesReportedCount(unittest.TestCase):
    def test_zeroed_diagonal_cell_is_counted_and_listed(self):
        C = _gram(400, N_CELLS, seed=2)
        k = 137
        C[k, :] = 0.0
        C[:, k] = 0.0
        r = v.mat_gates(C, "zero-diag")
        self.assertEqual(r["n_reported"], N_CELLS)
        self.assertEqual(r["zero_diag_reported_idx"], [k])
        self.assertTrue(r["diag_finite_nonneg"])

    def test_old_inference_would_have_undercounted_this_fixture(self):
        """Control: the fixture really does have a zero diagonal, so the old rule reads 265."""
        C = _gram(400, N_CELLS, seed=2)
        C[137, :] = 0.0
        C[:, 137] = 0.0
        self.assertEqual(int(np.sum(np.diag(C) > 0)), N_CELLS - 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
