"""Tests for fd_1b_null: the staged 1B declaration's draw-matched null and flag rule (section 5.2, revision 2)."""
from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parents[1]
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_1b_null as fn  # noqa: E402
import s1_assemble as sa  # noqa: E402

N_TEST = 400_000


def phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


class Laws(unittest.TestCase):
    def test_pair_law_is_s1s_pair_block(self):
        rng = np.random.default_rng(1)
        plus, minus = rng.normal(size=16), rng.normal(size=16)
        law = fn.Discrete.centred(np.stack([plus, minus]), [0.5, 0.5])
        np.testing.assert_allclose(law.cov(), sa.mat_cov(np.stack([plus, minus])), rtol=0, atol=1e-14)

    def test_two_point_is_quarter_delta_delta(self):
        d = np.arange(1.0, 17.0)
        np.testing.assert_allclose(fn.Discrete.two_point(d).cov(), np.outer(d, d) / 4, rtol=1e-15)

    def test_weighted_law_is_s1s_flux_block(self):
        rng = np.random.default_rng(2)
        X, w = rng.normal(size=(100, 16)), rng.uniform(0.5, 3.0, 100)
        law = fn.Discrete.centred(X, w / w.sum())
        np.testing.assert_allclose(law.cov(), sa.mat_cov(X, w), rtol=1e-12, atol=1e-14)

    def test_three_universe_law_is_s1s_mean_centred_block(self):
        X = np.random.default_rng(3).normal(size=(3, 16))
        np.testing.assert_allclose(fn.Discrete.centred(X, [1 / 3] * 3).cov(), sa.mat_cov(X), rtol=1e-12, atol=1e-14)

    def test_bad_probabilities_refuse(self):
        with self.assertRaises(fn.Refusal):
            fn.Discrete.centred(np.zeros((2, 3)), [0.5, 0.6])


class Matched(unittest.TestCase):
    def setUp(self):
        self.d = np.linspace(1.0, 2.0, 4)
        self.law = fn.Discrete.two_point(self.d)
        self.gauss = np.diag([1.0, 2.0, 3.0, 4.0])
        self.C = self.law.cov() + self.gauss

    def test_silent_when_matched(self):
        self.assertLessEqual(fn.check_matched([self.law], self.gauss, self.C), fn.MATCH_TOL)

    def test_fires_when_not_matched(self):
        with self.assertRaises(fn.Refusal):
            fn.check_matched([self.law], self.gauss, self.C * (1 + 1e-9))

    def test_null_refuses_unmatched(self):
        with self.assertRaises(fn.Refusal):
            fn.null_contents([self.law], self.gauss, 1.01 * self.C, n_mc=1000)


class Contents(unittest.TestCase):
    def test_gaussian_null_is_p0(self):
        C = np.array([[2.0, 0.5], [0.5, 1.0]])
        null = fn.null_contents([], C, C, n_mc=N_TEST, seed=11)
        for p, se in zip(null["p_cell"], null["se_cell"]):
            self.assertLess(abs(p - fn.P0), 5 * se)
        self.assertLess(abs(null["q_joint"] - fn.P0), 5 * null["se_joint"])
        self.assertEqual(null["ndf"], 2)

    def test_dominant_two_point_lowers_content(self):
        """The audit's example: d (+-1) + N(0, r^2) with d = 2r has content 0.593 inside its exact sigma."""
        d, r = 2.0, 1.0
        law, gauss = fn.Discrete.two_point(np.array([2 * d])), np.array([[r * r]])
        null = fn.null_contents([law], gauss, law.cov() + gauss, n_mc=N_TEST, seed=12)
        s = math.sqrt(d * d + r * r)
        exact = phi((s - d) / r) - phi((-s - d) / r)
        self.assertAlmostEqual(exact, 0.5933, places=4)
        self.assertLess(abs(null["p_cell"][0] - exact), 5 * null["se_cell"][0])

    def test_many_two_point_bands_approach_p0(self):
        # unequal amplitudes: equal ones make a lattice, whose content inside sigma is not P0
        amps = np.random.default_rng(14).uniform(0.5, 1.5, 40)
        laws = [fn.Discrete.two_point(np.array([a])) for a in amps]
        C = sum(law.cov() for law in laws)
        null = fn.null_contents(laws, np.zeros((1, 1)), C, n_mc=N_TEST, seed=13)
        self.assertLess(abs(null["p_cell"][0] - fn.P0), 0.01)

    def test_seed_fixes_the_null(self):
        law = fn.Discrete.two_point(np.array([1.0, 2.0]))
        g = np.eye(2)
        a = fn.null_contents([law], g, law.cov() + g, n_mc=20_000, seed=5)
        b = fn.null_contents([law], g, law.cov() + g, n_mc=20_000, seed=5)
        np.testing.assert_array_equal(a["p_cell"], b["p_cell"])
        self.assertEqual(a["q_joint"], b["q_joint"])


class Chi2(unittest.TestCase):
    def test_full_rank_equals_cholesky(self):
        rng = np.random.default_rng(7)
        A = rng.normal(size=(16, 16))
        C = A @ A.T + 16 * np.eye(16)
        E = rng.normal(size=(50, 16))
        chi2, ndf = fn.chi2_nonnull(E, C)
        L = np.linalg.cholesky(C)
        ref = np.sum(np.linalg.solve(L, E.T) ** 2, axis=0)
        np.testing.assert_allclose(chi2, ref, rtol=1e-9)
        self.assertEqual(ndf, 16)

    def test_null_space_is_dropped(self):
        v = np.array([1.0, 1.0, 0.0])
        C = np.diag([1.0, 1.0, 0.0]) + 0.0 * np.outer(v, v)
        _, ndf = fn.chi2_nonnull(np.zeros((1, 3)), C)
        self.assertEqual(ndf, 2)


class Flags(unittest.TestCase):
    def test_binom_cdf_edges(self):
        self.assertEqual(fn.binom_cdf(-1, 10, 0.5), 0.0)
        self.assertEqual(fn.binom_cdf(10, 10, 0.5), 1.0)
        self.assertAlmostEqual(fn.binom_cdf(5, 10, 0.5), 638 / 1024, places=14)

    def test_revision_0_thresholds_by_the_duality(self):
        """Revision 0's 181 and 190 (scipy's Clopper-Pearson in arith.py) come back from the binomial duality."""
        self.assertEqual(fn.flag_count(fn.P0, 300, 0.05 / 16), 181)
        self.assertEqual(fn.flag_count(fn.P0, 300, 0.05), 190)

    def test_flag_count_is_the_boundary(self):
        p, n, a = 0.66, 300, 0.01
        k = fn.flag_count(p, n, a)
        self.assertLess(fn.binom_cdf(k, n, p), a)
        self.assertGreaterEqual(fn.binom_cdf(k + 1, n, p), a)

    def test_margin_only_lowers_counts(self):
        null = {"p_cell": np.array([0.68, 0.70]), "se_cell": np.array([0.001, 0.001]), "q_joint": 0.68,
                "se_joint": 0.001}
        thr = fn.thresholds(null)
        for k, p in zip(thr["k_cell"], null["p_cell"]):
            self.assertLessEqual(k, fn.flag_count(float(p), 300, fn.ALPHA_CELLS / 2))

    def test_size_is_within_alpha_per_truth(self):
        null = {"p_cell": np.full(16, fn.P0), "se_cell": np.zeros(16), "q_joint": fn.P0, "se_joint": 0.0}
        s = fn.size(null, fn.thresholds(null))
        self.assertLessEqual(s["cells_union_bound"], fn.ALPHA_CELLS)
        self.assertLessEqual(s["joint"], fn.ALPHA_JOINT)
        self.assertLessEqual(s["per_truth_union_bound"], fn.ALPHA_CELLS + fn.ALPHA_JOINT)
        self.assertGreater(s["joint"], 0.0)
        self.assertAlmostEqual(s["per_truth_union_bound"], s["cells_union_bound"] + s["joint"], places=15)

    def test_across_truths(self):
        a = fn.across_truths([0.04, 0.04])
        self.assertAlmostEqual(a["union_bound"], 0.08)
        self.assertAlmostEqual(a["if_independent"], 1 - 0.96 ** 2)


class Attribution(unittest.TestCase):
    def test_pure_bias(self):
        e = np.random.default_rng(8).normal(1.0, 0.6, 300)
        a = fn.attribute(e, 1.0, fn.flag_count(fn.P0, 300, fn.ALPHA_CELLS / 16))
        self.assertLessEqual(int(np.sum(np.abs(e) <= 1.0)), a["k_flag"])
        self.assertEqual(a["driven_by"], "bias")

    def test_pure_width(self):
        e = np.random.default_rng(9).normal(0.0, 1.6, 300)
        e -= e.mean()
        a = fn.attribute(e, 1.0, fn.flag_count(fn.P0, 300, fn.ALPHA_CELLS / 16))
        self.assertEqual(a["driven_by"], "width")

    def test_both(self):
        e = np.random.default_rng(10).normal(0.8, 1.5, 300)
        a = fn.attribute(e, 1.0, fn.flag_count(fn.P0, 300, fn.ALPHA_CELLS / 16))
        self.assertEqual(a["driven_by"], "both")


if __name__ == "__main__":
    unittest.main()
