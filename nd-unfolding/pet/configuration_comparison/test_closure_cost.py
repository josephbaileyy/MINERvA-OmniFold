"""The campaign's cost under the structure it now actually has."""
from __future__ import annotations

import unittest

import closure_cost as cc
import frozen_design as fd


class Rows(unittest.TestCase):
    def test_a_stage_gets_its_frozen_share_and_two_halves_inside_it(self):
        for stage, fraction in fd.SPLITS["fractions"].items():
            r = cc.rows(2_000_000, stage)
            self.assertEqual(r["stage_owns"], int(2_000_000 * fraction))
            self.assertEqual(r["half"], r["stage_owns"] // 2)
            self.assertLessEqual(2 * r["half"], r["stage_owns"])

    def test_step_one_sees_pseudo_data_plus_prior_and_step_two_the_prior_twice(self):
        r = cc.rows(2_000_000, "final")
        self.assertEqual(r["step1_ntrain"], r["pdata_rows"] + r["prior_rows"])
        self.assertEqual(r["step2_ntrain"], 2 * r["prior_rows"])

    def test_there_is_no_data_leg(self):
        """`calibrate_cost` adds a 4.1M-row measured leg; the closure has none."""
        import calibrate_cost as old
        r = cc.rows(2_000_000, "final")
        self.assertLess(r["step1_ntrain"], old.ROWS_PER_FIT_STEP1)

    def test_the_pass_fraction_is_the_measured_one(self):
        self.assertAlmostEqual(cc.STEP1_PASS_FRACTION, 0.4141, places=4)


class Hours(unittest.TestCase):
    def test_his_arm_costs_more_per_example_and_so_more_per_evaluation(self):
        ours = cc.evaluation_hours("ours", 2_000_000, "final")
        theirs = cc.evaluation_hours("theirs", 2_000_000, "final")
        self.assertGreater(theirs["hours"], ours["hours"])

    def test_cost_is_linear_in_the_draw(self):
        one = cc.campaign(2_000_000)["hours_without_retries"]
        two = cc.campaign(4_000_000)["hours_without_retries"]
        self.assertAlmostEqual(two / one, 2.0, places=2)

    def test_the_campaign_fits_the_authorised_ceiling(self):
        total = cc.campaign(2_000_000)["hours_with_retries"]
        self.assertLess(total, 1000.0)

    def test_it_says_which_rate_is_not_measured_at_the_run_configuration(self):
        theirs = cc.evaluation_hours("theirs", 2_000_000, "final")
        self.assertFalse(theirs["inference_rate_measured_at_this_configuration"])
        self.assertIn("not his run's", cc.campaign()["caveat"])

    def test_it_records_what_it_supersedes(self):
        self.assertIn("366", cc.campaign()["superseded"])


class Sizing(unittest.TestCase):
    def test_the_established_two_million_half_needs_a_twenty_million_draw(self):
        self.assertEqual(cc.max_events_for_half(2_000_000, "tuning"), 20_000_000)

    def test_the_pilot_half_is_smaller_than_the_final_half(self):
        """So the pilot OVERSTATES variance and sizes the final conservatively."""
        self.assertLess(cc.half_size_for(2_000_000, "pilot"),
                        cc.half_size_for(2_000_000, "final"))
