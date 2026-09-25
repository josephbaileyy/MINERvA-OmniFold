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


if __name__ == "__main__":
    unittest.main()
