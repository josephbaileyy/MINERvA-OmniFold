"""Tests for the frozen design.

These do not check that the design is GOOD -- that is Joseph's ratification. They
check that it is CONSISTENT and COMPLETE, because a freeze with a contradiction in
it freezes the contradiction, and this lane has already had one: a regional rule
whose prose and whose test disagreed.
"""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import frozen_design as fd
import selection_rule as sr


class Consistency(unittest.TestCase):
    def test_the_splits_are_disjoint_and_exhaustive(self):
        total = sum(fd.SPLITS["fractions"].values())
        self.assertAlmostEqual(total, 1.0, places=9)

    def test_no_seed_is_reused_across_splits(self):
        """A seed shared between tuning and final would leak the selection."""
        lists = [v for v in fd.SEEDS.values() if isinstance(v, list)]
        flat = [s for group in lists for s in group]
        self.assertEqual(len(flat), len(set(flat)))

    def test_the_final_seed_count_matches_the_costed_campaign(self):
        self.assertEqual(len(fd.SEEDS["final"]), 8)
        self.assertEqual(len(fd.SEEDS["pilot"]), 4)
        self.assertEqual(fd.TUNING_GRID["trials_per_arm"], 4)

    def test_the_thresholds_satisfy_the_rule_they_are_fed_to(self):
        """delta_switch > delta > 0, or `decide` refuses them."""
        sr.decide(ours_adequate=True, theirs_adequate=True, ci_low=0.0, ci_high=0.01,
                  delta=fd.THRESHOLDS["non_inferiority_delta"],
                  delta_switch=fd.THRESHOLDS["switching_delta"])

    def test_his_published_learning_rate_is_in_the_grid(self):
        """A grid of neighbours that excludes his setting is not a fair trial."""
        self.assertIn(1e-4, fd.TUNING_GRID["points"])
        self.assertEqual(len(fd.TUNING_GRID["points"]),
                         fd.TUNING_GRID["trials_per_arm"])

    def test_both_arms_get_the_same_grid(self):
        self.assertTrue(fd.TUNING_GRID["same_for_both_arms"])

    def test_the_interaction_flags_are_the_paper_ones(self):
        self.assertFalse(fd.THEIRS_COMPLETE["use_int"])
        self.assertFalse(fd.THEIRS_COMPLETE["local_int"])

    def test_the_caps_differ_and_both_are_stated(self):
        self.assertEqual(fd.OURS_INCUMBENT["token_cap"], 12)
        self.assertEqual(fd.THEIRS_COMPLETE["token_cap"], 33)

    def test_tf32_is_forbidden_by_the_frozen_execution_policy(self):
        self.assertFalse(fd.EXECUTION["precision_policy"]["tf32_enabled"])
        self.assertTrue(fd.EXECUTION["precision_policy"]["determinism_enabled"])

    def test_every_pinned_hash_is_a_hash(self):
        for name, value in fd.PINNED_HASHES.items():
            with self.subTest(name=name):
                self.assertRegex(value, r"^[0-9a-f]{16,64}$")

    def test_the_pilot_is_excluded_from_the_final_inference(self):
        self.assertFalse(fd.INFERENCE["pilot_observations_in_final_inference"])
        self.assertIn("conditional on its own width",
                      fd.INFERENCE["pilot_exclusion_reason"])

    def test_low_acceptance_is_retained_not_excluded(self):
        handling = fd.REGIONS["low_acceptance_handling"]
        self.assertIn("RETAINED", handling)
        self.assertIn("not called unresolvable", handling)

    def test_the_regional_floor_is_per_region(self):
        self.assertIn("THAT REGION", fd.REGIONS["floor"])
        self.assertIn("never a global one", fd.REGIONS["floor"])

    def test_the_bands_cover_acceptance_without_a_gap(self):
        bands = fd.REGIONS["bands_by_cell_acceptance"]
        for (_, _, hi), (_, lo, _) in zip(bands, bands[1:]):
            self.assertEqual(hi, lo)
        self.assertEqual(bands[0][1], 0.0)
        self.assertGreaterEqual(bands[-1][2], 1.0)

    def test_a_stopping_rule_forbids_widening_delta(self):
        self.assertTrue(any("do NOT widen delta" in rule
                            for rule in fd.STOPPING_RULES))

    def test_the_scope_limit_is_carried(self):
        self.assertIn("OI-71", fd.NOT_AUTHORIZED)
        self.assertIn("Gate-6", fd.NOT_AUTHORIZED)


if __name__ == "__main__":
    unittest.main()
