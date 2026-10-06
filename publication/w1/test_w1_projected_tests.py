"""W1 mechanics on synthetic inputs (no real data): the projection partitions the in-domain cells, and with the
identity in place of a projection the projected statistics equal the frozen-rule replay exactly."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("w1", HERE / "w1_projected_tests.py")
w1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w1)


class Projection(unittest.TestCase):
    def test_partition_of_domain_cells(self):
        rng = np.random.default_rng(1)
        supported = np.sort(rng.choice(243, size=109, replace=False))
        pz = np.array([np.unravel_index(c, w1.GRID)[1] for c in supported])
        for dom in (np.ones(109, bool), pz <= 1):
            for axes in w1.PROJECTIONS.values():
                P = w1.projection_matrix(supported, dom, axes)
                np.testing.assert_array_equal(P.sum(0), np.ones(dom.sum()))
                self.assertTrue(np.all(P.sum(1) >= 1))
                self.assertLessEqual(P.shape[0], 9)

    def test_identity_projection_equals_replay(self):
        rng = np.random.default_rng(2)
        n = 10
        A = rng.normal(size=(n, n))
        V = A @ A.T + n * np.eye(n)
        mu, var = rng.uniform(5, 9, n), rng.uniform(0.01, 0.1, n)
        F = mu + rng.normal(size=(30, n))
        seeds = rng.integers(10**6, 2 * 10**6, 30)
        dom = np.ones(n, bool)
        dom[:2] = False
        P = np.eye(int(dom.sum()))
        a = w1.projected_statistics(F, mu, var, V, dom, P, 1780000, seeds=seeds)
        b = w1.rp.statistics(F, mu, var, V, dom, 1780000, seeds=seeds)
        for x, y in zip(a, b):
            np.testing.assert_allclose(x, y, rtol=1e-12, atol=0)


if __name__ == "__main__":
    unittest.main()
