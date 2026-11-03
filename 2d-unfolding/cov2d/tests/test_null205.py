"""1B's null and flag rule (nd-unfolding/fd_1b_null.py), imported unchanged, at COV2D's 205 cells.
    python -B -m pytest -q 2d-unfolding/cov2d/tests/test_null205.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "nd-unfolding"))
import fd_1b_null as n  # noqa: E402

CELLS = 205


def world(seed=3):
    """Laws shaped as COV2D's: one 100-universe weighted band, one 3-universe band, 36 two-point bands, 5 laterals,
    and a Gaussian part; C_T is their exact sum."""
    r = np.random.default_rng(seed)
    w = r.uniform(0.5, 1.5, 100)
    laws = [n.Discrete.centred(r.normal(0, 0.3, (100, CELLS)), w / w.sum()),
            n.Discrete.centred(r.normal(0, 0.3, (3, CELLS)), np.full(3, 1 / 3))]
    laws += [n.Discrete.two_point(r.normal(0, 0.2, CELLS)) for _ in range(36 + 5)]
    A = r.normal(0, 0.1, (CELLS, CELLS))
    gauss = A @ A.T / CELLS + np.diag(r.uniform(0.01, 0.05, CELLS))
    C_T = gauss + sum(l.cov() for l in laws)
    return laws, gauss, C_T


class Null205(unittest.TestCase):
    def test_bonferroni_divisor_is_the_cell_count(self):
        null = {"p_cell": np.full(CELLS, n.P0), "se_cell": np.zeros(CELLS), "q_joint": n.P0, "se_joint": 0.0}
        thr = n.thresholds(null)
        self.assertAlmostEqual(thr["alpha_cell"], 0.025 / CELLS, places=15)
        self.assertEqual(set(thr["k_cell"]), {174})
        self.assertEqual(thr["k_joint"], 188)
        sz = n.size(null, thr)
        self.assertLessEqual(sz["cells_union_bound"], 0.025)
        self.assertLessEqual(sz["per_truth_union_bound"], 0.05)

    def test_matched_null_runs_and_refuses_a_mismatch(self):
        laws, gauss, C_T = world()
        null = n.null_contents(laws, gauss, C_T, n_mc=20_000, seed=5_742_000)
        self.assertEqual(null["p_cell"].shape, (CELLS,))
        self.assertEqual(null["ndf"], CELLS)
        self.assertLess(null["match_rel"], 1e-12)
        self.assertTrue(np.all((null["p_cell"] > 0.55) & (null["p_cell"] < 0.80)))
        with self.assertRaises(n.Refusal):
            n.null_contents(laws, gauss * 1.001, C_T, n_mc=1000)

    def test_power_at_205_cells(self):
        k = n.flag_count(n.P0, 300, 0.025 / CELLS)
        self.assertAlmostEqual(n.binom_cdf(k, 300, 0.58), 0.522, places=3)
        self.assertAlmostEqual(n.binom_cdf(k, 300, 0.55), 0.865, places=3)


if __name__ == "__main__":
    unittest.main()
