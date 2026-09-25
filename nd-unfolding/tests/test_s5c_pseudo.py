"""Controls for s5c_pseudo's pieces that need no LightGBM or ROOT."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5c_pseudo  # noqa: E402


class HalfSplit(unittest.TestCase):
    def test_deterministic_balanced_and_key_dependent(self):
        a = s5c_pseudo.half_mask(200_000, 7)
        self.assertTrue(np.array_equal(a, s5c_pseudo.half_mask(200_000, 7)))
        self.assertLess(abs(a.mean() - 0.5), 0.005)
        b = s5c_pseudo.half_mask(200_000, 8)
        self.assertLess(abs((a == b).mean() - 0.5), 0.01)


class Purity(unittest.TestCase):
    def setUp(self):
        self.edges = [np.array([0.0, 1.0, 2.0])] * 2
        self.bkg_nd = np.array([[1.0, 0.0], [5.0, 0.5]])

    def test_matches_per_event_definition(self):
        coords = np.array([[0.5, 0.5], [0.5, 0.5], [1.5, 0.5], [1.5, 1.5], [5.0, 0.5]])
        w = s5c_pseudo.purity_weights(coords, np.ones(5), self.bkg_nd, self.edges)
        # bin (0,0): d=2,b=1 -> 0.5; bin (1,0): d=1,b=5 -> 0; bin (1,1): d=1,b=.5 -> .5; outside -> 0
        np.testing.assert_allclose(w, [0.5, 0.5, 0.0, 0.5, 0.0])

    def test_integer_counts_equal_repeated_events(self):
        coords = np.array([[0.5, 0.5], [1.5, 1.5]])
        w = s5c_pseudo.purity_weights(coords, np.array([3.0, 2.0]), self.bkg_nd, self.edges)
        rep = np.array([[0.5, 0.5]] * 3 + [[1.5, 1.5]] * 2)
        wr = s5c_pseudo.purity_weights(rep, np.ones(5), self.bkg_nd, self.edges)
        np.testing.assert_allclose(w, [wr[:3].sum(), wr[3:].sum()])


class Truth(unittest.TestCase):
    def test_nominal_is_one_and_tilt_is_centered(self):
        edges = [np.linspace(0, 1, 3)] * 5
        gen = np.random.default_rng(0).random((1000, 5))
        self.assertTrue(np.all(s5c_pseudo.truth_weight("nominal", gen, edges, 0.3) == 1))
        t = s5c_pseudo.truth_weight("eavail_tilt", gen, edges, 0.3)
        self.assertAlmostEqual(t.min(), 0.85, delta=0.01)
        self.assertAlmostEqual(t.max(), 1.15, delta=0.01)


class CorrelationDeformation(unittest.TestCase):
    def test_preserves_eavail_w_marginal_and_moves_q3(self):
        rng = np.random.default_rng(3)
        n = 200_000
        gen = rng.random((n, 5)) * np.array([4.5, 60, 3.0, 3.0, 3.0])
        gen[:, 3] = gen[:, 2] * 0.8 + rng.random(n)  # q3 correlated with E_avail
        edges = [np.linspace(0, 4.5, 4), np.linspace(0, 60, 4), np.linspace(0, 3, 7),
                 np.linspace(0, 4, 6), np.linspace(0, 3, 6)]
        w = rng.uniform(0.5, 1.5, n)
        r = s5c_pseudo.truth_weight("q3_given_eavail_w", gen, edges, 0.3, w_truth=w)
        self.assertGreater(r.min(), 0.0)
        ew = lambda weights: np.histogram2d(gen[:, 2], gen[:, 4], bins=[edges[2], edges[4]], weights=weights)[0]
        np.testing.assert_allclose(ew(w * r), ew(w), rtol=1e-10)
        q_nom = np.histogram(gen[:, 3], bins=edges[3], weights=w)[0]
        q_def = np.histogram(gen[:, 3], bins=edges[3], weights=w * r)[0]
        self.assertGreater(np.max(np.abs(q_def / q_nom - 1)), 0.02)

    def test_gen_sentinels_neither_enter_the_statistics_nor_break_the_in_grid_marginal(self):
        """The input sample carries -9999 gen sentinels (2,801 pass_truth rows have q3 or W = -9999).
        They must keep r = 1 and must not move the in-grid (E_avail, W) marginal that x_true is built on."""
        rng = np.random.default_rng(5)
        n = 100_000
        gen = rng.random((n, 5)) * np.array([4.5, 60, 3.0, 3.0, 3.0])
        gen[:, 3] = gen[:, 2] * 0.8 + rng.random(n)
        edges = [np.linspace(0, 4.5, 4), np.linspace(0, 60, 4), np.linspace(0, 3, 7),
                 np.linspace(0, 4, 6), np.linspace(0, 3, 6)]
        bad = rng.choice(n, 2000, replace=False)
        gen[bad[:1000], 3] = -9999.0
        gen[bad[1000:], 4] = -9999.0
        gen[bad[:1000], 2] = 0.1          # sentinels sit in the lowest-E_avail row, as in the data
        w = rng.uniform(0.5, 1.5, n)
        r = s5c_pseudo.truth_weight("q3_given_eavail_w", gen, edges, 0.3, w_truth=w)
        np.testing.assert_array_equal(r[bad], 1.0)
        kept = np.histogramdd(gen, bins=edges, weights=w)[0].sum(axis=(0, 1, 3))
        moved = np.histogramdd(gen, bins=edges, weights=w * r)[0].sum(axis=(0, 1, 3))
        np.testing.assert_allclose(moved, kept, rtol=1e-10)
        q_nom = np.histogramdd(gen, bins=edges, weights=w)[0].sum(axis=(0, 1, 2, 4))
        q_def = np.histogramdd(gen, bins=edges, weights=w * r)[0].sum(axis=(0, 1, 2, 4))
        self.assertGreater(np.max(np.abs(q_def / q_nom - 1)), 0.02)

    def test_refuses_nonpositive_amplitude_range(self):
        with self.assertRaises(ValueError):
            s5c_pseudo.truth_weight("q3_given_eavail_w", np.zeros((3, 5)), [np.linspace(0, 1, 3)] * 5, 0.6,
                                    w_truth=np.ones(3))


class SplitKeys(unittest.TestCase):
    def test_per_seed_split_keys_are_distinct_and_deterministic(self):
        keys = [s5c_pseudo.split_key_for(s) for s in range(100000, 100200)]
        self.assertEqual(len(set(keys)), 200)
        self.assertEqual(keys[0], s5c_pseudo.split_key_for(100000))


if __name__ == "__main__":
    unittest.main()
