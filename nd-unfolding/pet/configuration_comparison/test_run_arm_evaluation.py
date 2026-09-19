"""Tests for the injection and the recovery statistic."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np

import run_arm_evaluation as rae


class Injection(unittest.TestCase):
    def test_the_tilt_preserves_the_total(self):
        """A rate change would be undone by normalization and test nothing."""
        e = np.linspace(0, 3, 500)
        w = rae.injected_truth_weights(e, 0.35, 3.0)
        self.assertAlmostEqual(float(w.mean()), 1.0, places=9)

    def test_the_clip_binds(self):
        e = np.linspace(0, 50, 100)
        w = rae.injected_truth_weights(e, 0.35, 3.0)
        self.assertLessEqual(float(w.max() / w.min()), 3.0 / np.exp(0) + 1e-6)

    def test_it_tilts_upward_in_eavail(self):
        e = np.array([0.0, 1.0, 2.0])
        w = rae.injected_truth_weights(e, 0.35, 3.0)
        self.assertLess(w[0], w[1])
        self.assertLess(w[1], w[2])


class Recovery(unittest.TestCase):
    PRIOR = np.array([10.0, 20.0, 30.0, 20.0, 10.0, 5.0, 5.0])
    TARGET = np.array([5.0, 15.0, 30.0, 25.0, 15.0, 8.0, 2.0])

    def test_doing_nothing_scores_zero(self):
        r = rae.recovery(self.PRIOR, self.PRIOR, self.TARGET)
        self.assertAlmostEqual(r["recovery"], 0.0, places=9)

    def test_reaching_the_target_scores_one(self):
        r = rae.recovery(self.PRIOR, self.TARGET, self.TARGET)
        self.assertAlmostEqual(r["recovery"], 1.0, places=9)

    def test_overshoot_is_reported_not_clipped(self):
        over = self.TARGET + (self.TARGET - self.PRIOR)
        r = rae.recovery(self.PRIOR, over, self.TARGET)
        self.assertLess(r["recovery"], 1.0)
        self.assertTrue(r["overshoot_not_clipped"])

    def test_it_is_scale_invariant(self):
        a = rae.recovery(self.PRIOR, self.TARGET * 0.5, self.TARGET)
        self.assertAlmostEqual(a["recovery"], 1.0, places=9)

    def test_a_degenerate_input_is_refused(self):
        with self.assertRaises(ValueError):
            rae.recovery(np.zeros(7), self.TARGET, self.TARGET)

    def test_an_injection_that_displaces_nothing_is_refused(self):
        with self.assertRaises(ValueError):
            rae.recovery(self.PRIOR, self.PRIOR, self.PRIOR)


if __name__ == "__main__":
    unittest.main()
