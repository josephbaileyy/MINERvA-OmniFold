"""Tests for the threshold translation: the arithmetic, and its refusals."""

from __future__ import annotations

import unittest

import threshold_translation as tt


class Translation(unittest.TestCase):
    def test_l1_is_twice_total_variation(self):
        self.assertAlmostEqual(tt.injected_truth_mass_fraction(0.2733), 0.13665)

    def test_residual_at_full_recovery_is_zero(self):
        self.assertAlmostEqual(tt.residual_truth_mass_fraction(1.0), 0.0)

    def test_residual_at_zero_recovery_is_the_whole_injection(self):
        self.assertAlmostEqual(tt.residual_truth_mass_fraction(0.0),
                               tt.injected_truth_mass_fraction())

    def test_recovery_above_one_does_not_give_a_negative_residual(self):
        """The reference is not a bound, so R > 1 happens; it must not go negative."""
        self.assertEqual(tt.residual_truth_mass_fraction(1.4), 0.0)

    def test_a_margin_costs_its_share_of_the_injection(self):
        self.assertAlmostEqual(tt.margin_cost(0.02), 0.02 * 0.13665)

    def test_the_translation_scales_with_the_injection_not_the_estimator(self):
        """Halve the injected displacement and the same margin means half the mass."""
        self.assertAlmostEqual(tt.margin_cost(0.02, displacement=0.2733) / 2.0,
                               tt.margin_cost(0.02, displacement=0.13665))

    def test_adequacy_floor_is_a_fraction_of_the_calculated_reference(self):
        self.assertAlmostEqual(tt.adequacy_floor(0.80), 0.80 * 0.7131)

    def test_negative_margins_and_impossible_fractions_are_refused(self):
        with self.assertRaises(ValueError):
            tt.margin_cost(-0.01)
        for fraction in (0.0, -0.5, 1.5):
            with self.subTest(fraction=fraction):
                with self.assertRaises(ValueError):
                    tt.adequacy_floor(fraction)

    def test_an_impossible_l1_displacement_is_refused(self):
        with self.assertRaises(ValueError):
            tt.injected_truth_mass_fraction(2.5)


class Policy(unittest.TestCase):
    PREFERRED = dict(fraction_of_reference=0.80, delta=0.02, delta_switch=0.04,
                     regional_fraction=0.60)

    def test_the_preferred_policy_translates(self):
        policy = tt.describe_policy(**self.PREFERRED)
        self.assertAlmostEqual(policy["adequacy"]["recovery_floor"], 0.57048)
        # 0.42952 * 0.13665, recomputed independently rather than carried over.
        self.assertAlmostEqual(policy["adequacy"]["residual_truth_mass_permitted"],
                               0.0586939, places=7)
        self.assertAlmostEqual(policy["non_inferiority"]["additional_misplaced_truth_mass"],
                               0.002733, places=6)
        self.assertAlmostEqual(policy["switching"]["additional_misplaced_truth_mass"],
                               0.005466, places=6)

    def test_switching_must_exceed_the_margin(self):
        with self.assertRaises(ValueError):
            tt.describe_policy(0.80, delta=0.04, delta_switch=0.04, regional_fraction=0.6)

    def test_the_regional_floor_may_not_be_stricter_than_the_global_one(self):
        with self.assertRaises(ValueError):
            tt.describe_policy(0.80, 0.02, 0.04, regional_fraction=0.95)

    def test_the_reference_is_labelled_calculated(self):
        policy = tt.describe_policy(**self.PREFERRED)
        self.assertIn("CALCULATED", policy["reference"]["status"])
        self.assertIn("not a bound", policy["reference"]["status"])


if __name__ == "__main__":
    unittest.main(verbosity=1)


class TheApplicableReference(unittest.TestCase):
    """Pinned before any comparative result. One chosen after is not a reference."""

    def test_the_reference_is_quoted_with_its_iteration_count(self):
        import frozen_design as fd
        self.assertEqual(fd.REFERENCE["iterations"], 3)
        self.assertIn(3, fd.REFERENCE["by_iterations"])
        self.assertEqual(fd.REFERENCE["aggregate"],
                         fd.REFERENCE["by_iterations"][3])

    def test_it_rises_with_iterations_and_is_below_one(self):
        import frozen_design as fd
        values = [fd.REFERENCE["by_iterations"][k] for k in (1, 2, 3, 4)]
        self.assertEqual(values, sorted(values))
        self.assertLess(values[-1], 1.0)

    def test_the_adequacy_floor_is_the_fraction_times_the_reference(self):
        import frozen_design as fd
        self.assertAlmostEqual(
            fd.REFERENCE["adequacy_floor"],
            fd.THRESHOLDS["adequacy_fraction_of_reference"] * fd.REFERENCE["aggregate"])

    def test_the_low_acceptance_reference_is_small_but_not_a_write_off(self):
        """0.014 at k=3. The band is retained and scored against its OWN
        reference, which is what keeps a small number from reading as a
        failure."""
        import frozen_design as fd
        self.assertLess(fd.REFERENCE["regional"]["low_acceptance"], 0.05)
        self.assertGreater(fd.REFERENCE["regional"]["low_acceptance"], 0.0)

    def test_every_region_has_a_reference(self):
        import characterize_regions as cr
        import frozen_design as fd
        for name, _lo, _hi in cr.SAFEGUARD_REGIONS:
            self.assertIn(name, fd.REFERENCE["regional"], msg=name)
