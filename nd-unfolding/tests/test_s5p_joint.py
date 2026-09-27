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

    def test_ledoit_wolf_is_scale_equivariant_and_keeps_the_variances(self):
        """Review round 1 F5: shrinking toward (mean variance) x I on raw cells whose variances span 1e5 inflates
        the small-variance cells. The standardized form keeps every diagonal at the sample variance and is
        equivariant under a rescaling of the cells (V(X S) = S V(X) S)."""
        rng = np.random.default_rng(3)
        n, p = 60, 30
        L = rng.normal(size=(p, p)) * 0.3 + np.eye(p)
        X = rng.normal(size=(n, p)) @ L.T
        scale = np.logspace(-3, 2, p)
        Xs = X * scale
        V, s = sj.ledoit_wolf(Xs)
        self.assertTrue(0 <= s <= 1)
        np.testing.assert_allclose(np.diag(V), Xs.var(0, ddof=1), rtol=1e-12)
        V1, s1 = sj.ledoit_wolf(X)
        self.assertAlmostEqual(s, s1, places=12)
        np.testing.assert_allclose(V, V1 * np.outer(scale, scale), rtol=1e-10, atol=0)
        self.assertGreater(np.linalg.eigvalsh(V1).min(), 0)

    def test_ledoit_wolf_constant_cell_stays_zero_variance(self):
        rng = np.random.default_rng(4)
        X = rng.normal(size=(50, 5))
        X[:, 2] = 7.0
        V, _ = sj.ledoit_wolf(X)
        self.assertEqual(V[2, 2], 0.0)
        self.assertTrue(np.all(V[2] == 0.0))

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

    def test_pvals_against_is_the_rank_rule(self):
        rng = np.random.default_rng(8)
        null = rng.chisquare(10, size=999)
        null[:5] = null[5]  # ties
        for t in list(rng.chisquare(10, size=50)) + [null[5], null.max(), null.min(), 1e9]:
            self.assertAlmostEqual(sj.pvals_against(np.array([t]), null)[0], si.mc_pvalue(t, null)["p"], places=15)

    def test_a_process_shift_raises_the_implied_size_and_zero_shift_does_not(self):
        rng = np.random.default_rng(9)
        p, n = 12, 1500
        mu = np.linspace(1, 2, p)
        sd = 0.02 * mu
        V = np.diag(sd ** 2)
        var_mu = np.zeros(p)
        dom = np.ones(p, bool)
        F = mu + rng.normal(size=(n, p)) * sd
        tt0, _ = sj.statistics(F, mu, var_mu, V, dom, 0)
        tt1, _ = sj.statistics(F + 1.0 * sd, mu, var_mu, V, dom, 0)  # a coherent one-sigma shift in every cell
        self.assertGreater(si.power(tt1, tt0, 0.05)["power"], 0.5)
        self.assertLess(si.power(tt0, tt0, 0.05)["power"], 0.06)

    def test_load_shift_checks_digest_and_length(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "D.npz"
            np.savez(f, D_J=np.ones(4))
            spec = {"path": str(f), "sha256": sj.sha256(f)}
            np.testing.assert_array_equal(sj.load_shift(spec, 4), np.ones(4))
            with self.assertRaises(SystemExit):
                sj.load_shift(spec, 5)
            with self.assertRaises(SystemExit):
                sj.load_shift(dict(spec, sha256="0" * 64), 4)
        self.assertIsNone(sj.load_shift(None, 4))


if __name__ == "__main__":
    unittest.main()
