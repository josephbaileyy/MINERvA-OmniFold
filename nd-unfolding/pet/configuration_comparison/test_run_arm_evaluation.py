"""Tests for the injection and the recovery statistic."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

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

    def test_overshoot_scores_below_one_like_undershoot(self):
        # This assertion was already here and already correct; the field beside
        # it was called `overshoot_not_clipped` and the docstring said values
        # above 1 mean overshoot. The two were never read together. The score is
        # 1 - residual/injected with residual a sum of absolute values, so it is
        # bounded above by 1 and travelling too far scores below it, exactly as
        # stopping short does. The direction is recovered by
        # `score_campaign.overshoot_projection`, not by this number.
        over = self.TARGET + (self.TARGET - self.PRIOR)
        r = rae.recovery(self.PRIOR, over, self.TARGET)
        self.assertLess(r["recovery"], 1.0)
        self.assertTrue(r["bounded_above_by_one"])

    def test_no_weighting_can_score_above_one(self):
        rng = np.random.default_rng(5)
        for _ in range(200):
            arbitrary = rng.gamma(1.0, 1.0, size=self.PRIOR.size) + 1e-6
            r = rae.recovery(self.PRIOR, arbitrary, self.TARGET)
            self.assertLessEqual(r["recovery"], 1.0 + 1e-12)

    def test_moving_away_from_the_target_scores_below_zero(self):
        away = self.PRIOR - 0.5 * (self.TARGET - self.PRIOR)
        r = rae.recovery(self.PRIOR, np.abs(away), self.TARGET)
        self.assertLess(r["recovery"], 0.0)
        self.assertTrue(r["below_zero_means_worse_than_doing_nothing"])

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


class MeasuredLegIsConsumedNotRebuilt(unittest.TestCase):
    """The J04/D2 defect, in this driver's clothing.

    Calling `build_fullevent_loaders` without a precomputed target re-runs the
    negweight refinement in process. Production was repaired for exactly that
    in August. Here it would be worse than wasteful: the measured leg both arms
    are compared on would not be production's, so the comparison would not be
    about our incumbent.
    """

    def test_the_driver_requires_the_certified_target_and_its_receipt(self):
        source = Path(rae.__file__).read_text()
        self.assertIn('"--target-npy"', source)
        self.assertIn('"--target-receipt"', source)
        self.assertIn("required=True", source)

    def test_the_loader_is_called_with_the_target_and_the_production_bkg_mode(self):
        source = Path(rae.__file__).read_text()
        self.assertIn("precomputed_target=str(args.target_npy)", source)
        self.assertIn("bkg_mode=prod.BKG_MODE", source)

    def test_both_provenance_assertions_are_called_not_retyped(self):
        source = Path(rae.__file__).read_text()
        self.assertIn("prod.assert_target_provenance(", source)
        self.assertIn("prod.assert_consumed_inventory_matches_receipt(", source)

    def test_the_frozen_design_pins_the_measured_leg(self):
        import frozen_design as fd
        self.assertEqual(fd.MEASURED_LEG["bkg_mode"], "negweight-refined")
        self.assertFalse(fd.MEASURED_LEG["rebuilt_in_process"])
        self.assertIn("G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy",
                      fd.MEASURED_LEG["target_npy"])

    def test_the_driver_checks_where_its_modules_came_from(self):
        """Restoring sys.path is a hope; `__file__` is a measurement."""
        source = Path(rae.__file__).read_text()
        self.assertIn("resolved OUTSIDE the pinned checkout", source)
        self.assertIn("Path(m.__file__).resolve()", source)
