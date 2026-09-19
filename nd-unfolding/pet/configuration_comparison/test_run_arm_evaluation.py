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


class TheClosureNeverUnfoldsRealData(unittest.TestCase):
    """The driver unfolded the real measured inventory and never injected.

    Its docstring said the opposite. The score would still have computed --
    weights from unfolding real data, against a target defined by an injection
    that never happened.
    """

    def test_the_loader_is_built_mc_only(self):
        source = Path(rae.__file__).read_text()
        self.assertIn('bkg_mode="mc-only"', source)

    def test_a_returned_measured_loader_is_refused(self):
        source = Path(rae.__file__).read_text()
        self.assertIn("mc-only returned a measured loader", source)

    def test_the_certified_real_data_target_is_NOT_required_here(self):
        source = Path(rae.__file__).read_text()
        self.assertNotIn('"--target-npy"', source)
        self.assertNotIn("precomputed_target", source)

    def test_the_frozen_design_pins_pseudo_data(self):
        import frozen_design as fd
        self.assertEqual(fd.MEASURED_LEG["bkg_mode"], "mc-only")
        self.assertFalse(fd.MEASURED_LEG["is_real_data"])

    def test_the_halves_are_disjoint_and_come_from_the_established_split(self):
        import closure_powered_truth_reweight as cp
        import frozen_design as fd
        a, b = cp.deterministic_halves(50_000, half=10_000,
                                       seed=int(fd.SPLITS["split_seed"]))
        self.assertEqual(np.intersect1d(a, b).size, 0)
        self.assertEqual(a.size, 10_000)
        self.assertEqual(b.size, 10_000)

    def test_the_injection_is_applied_to_truth_passing_rows_only(self):
        source = Path(rae.__file__).read_text()
        self.assertIn("tilt_a[pg_a] = tilt_on_truth", source)
        self.assertIn("eavail[ia][pg_a]", source)

    def test_step_one_uses_pass_reco_and_pass_gen_on_both_sides(self):
        source = Path(rae.__file__).read_text()
        self.assertIn("s1_a = pr[ia] & pg_a", source)
        self.assertIn("s1_b = pr[ib] & pg[ib]", source)

    def test_the_push_must_align_to_half_B(self):
        source = Path(rae.__file__).read_text()
        self.assertIn("not aligned to half B", source)

    def test_the_driver_checks_where_its_modules_came_from(self):
        """Restoring sys.path is a hope; `__file__` is a measurement."""
        source = Path(rae.__file__).read_text()
        self.assertIn("resolved OUTSIDE the pinned checkout", source)
        self.assertIn("Path(m.__file__).resolve()", source)


class TheIncumbentsTrainingPolicy(unittest.TestCase):
    """`MultiFold` defaults to 50 epochs; the incumbent's frozen policy is 8."""

    def test_epochs_is_passed_explicitly(self):
        source = Path(rae.__file__).read_text()
        self.assertIn("epochs=int(recipe.EPOCHS)", source)

    def test_the_recipe_and_the_cost_model_agree_on_epochs(self):
        import training_recipe as recipe
        self.assertEqual(recipe.EPOCHS, 8)

    def test_the_default_would_have_been_six_times_the_policy(self):
        """Read off the vendored engine's source: importing it needs TF."""
        import re
        import training_recipe as recipe
        engine = (Path(rae.__file__).parents[3] / "omnifold_nn" / "omnifold"
                  / "omnifold.py")
        if not engine.exists():
            self.skipTest("vendored engine not in this checkout")
        block = engine.read_text().split("def __init__", 1)[1][:1200]
        default = int(re.search(r"epochs\s*=\s*(\d+)", block).group(1))
        self.assertEqual(default, 50)
        self.assertGreater(default / recipe.EPOCHS, 6.0)

    def test_the_seed_seeds_the_estimator_and_the_subsample_is_held(self):
        source = Path(rae.__file__).read_text()
        self.assertIn("tf.keras.utils.set_random_seed(int(args.seed))", source)
        self.assertIn('seed=int(prod.NOMINAL_SEED_POLICY["subsample_seed"])',
                      source)
