"""Controls for s5p_joint: Ledoit-Wolf shrinkage is positive definite with its weight in [0, 1]; the observed
and simulated statistics share one metric; a null ensemble drawn from the same process gives uniform p-values
(the rank test's size) and a shifted observation gives a small p."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5p_inference as si  # noqa: E402
import s5p_joint as sj  # noqa: E402


class Tests(unittest.TestCase):
    def test_ledoit_wolf_is_positive_definite(self):
        rng = np.random.default_rng(0)
        X = rng.normal(size=(40, 60))  # fewer samples than dimensions
        V, s = sj.ledoit_wolf(X)
        self.assertTrue(0 <= s <= 1)
        self.assertGreater(np.linalg.eigvalsh(V).min(), 0)

    def test_rank_test_size_and_power_through_statistics(self):
        rng = np.random.default_rng(1)
        p, n = 8, 400
        mu = np.linspace(1, 2, p)
        cov = np.diag((0.02 * mu) ** 2)
        V = cov
        var_mu = (0.005 * mu) ** 2
        dom = np.ones(p, bool)
        def draw(k, shift=0.0):
            return mu * (1 + shift) + rng.multivariate_normal(np.zeros(p), cov, size=k) + rng.normal(size=(k, p)) * np.sqrt(var_mu)
        tt_null, _ = sj.statistics(draw(n) - 0.0, mu, var_mu, V, dom, 100)
        rej = 0
        for i in range(200):
            tt_o, _ = sj.statistics(draw(1), mu, var_mu, V, dom, 0, draw=False)
            rej += si.mc_pvalue(tt_o[0], tt_null)["p"] <= 0.05
        self.assertLess(rej / 200, 0.12)
        tt_o, _ = sj.statistics(draw(1, shift=0.05), mu, var_mu, V, dom, 0, draw=False)
        self.assertLess(si.mc_pvalue(tt_o[0], tt_null)["p"], 0.05)


if __name__ == "__main__":
    unittest.main()
