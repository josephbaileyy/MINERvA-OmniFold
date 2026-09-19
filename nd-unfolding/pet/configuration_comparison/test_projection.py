"""Tests for the campaign projector.

The load-bearing one is that a missing or failed cell REFUSES rather than
projecting from whatever is left: every cost figure in this lane has been prose
arithmetic, and a table built on an absent measurement looks exactly like one
built on a present measurement.
"""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import project_campaign as pc


def _cell(batch, seconds, section="full_step"):
    return {"batch": batch,
            "sections": {section: {"step_seconds_median": seconds}}}


class Stages(unittest.TestCase):
    def test_the_stage_table_sums_to_the_quoted_pair_count(self):
        self.assertEqual(sum(pc.CAMPAIGN_STAGES.values()), pc.PAIRS)
        self.assertEqual(pc.PAIRS, 17)

    def test_the_campaign_arithmetic_is_the_documented_one(self):
        result = pc.campaign(10.0)
        self.assertEqual(result["subtotal_gpu_hours"], 170.0)
        self.assertEqual(result["retries_gpu_hours"], 42.5)
        self.assertEqual(result["total_gpu_hours"], 212.5)
        self.assertTrue(result["fits_under_ceiling"])

    def test_the_ceiling_counts_what_was_already_spent(self):
        """Joseph raised it to 1,000 INCLUDING previous spending and failures."""
        result = pc.campaign(10.0)
        self.assertEqual(pc.CEILING_GPU_HOURS, 1000.0)
        self.assertAlmostEqual(result["cumulative_gpu_hours"],
                               212.5 + pc.SPENT_BEFORE_THIS_CAMPAIGN)
        self.assertGreater(result["headroom_gpu_hours"], 0)

    def test_the_ceiling_is_a_refusal_not_a_warning(self):
        over = pc.campaign(50.0)
        self.assertFalse(over["fits_under_ceiling"])
        self.assertLess(over["headroom_gpu_hours"], 0)


class Hours(unittest.TestCase):
    def test_the_data_leg_factor_scales_both_legs(self):
        base = pc.evaluation_hours(1e-6, 1e-6)
        scaled = pc.evaluation_hours(1e-6, 1e-6, data_leg_factor=2.0)
        self.assertAlmostEqual(scaled["evaluation_gpu_hours"],
                               2 * base["evaluation_gpu_hours"])

    def test_the_reference_projection_reproduces_the_committed_figure(self):
        """934.6 us/example is COST_UPDATE2's measured ported step."""
        theirs = pc.evaluation_hours(934.6e-6, 134.2e-6)
        self.assertAlmostEqual(theirs["evaluation_gpu_hours"], 41.76, places=1)


class Refusals(unittest.TestCase):
    RECEIPT = {"cells": {
        "optimised|33|2048|train": _cell(2048, 1.0),
        "optimised|33|2048|forward": _cell(2048, 0.2, "forward"),
        "ours_incumbent|33|2048|train": _cell(2048, 0.05),
        "ours_incumbent|33|2048|forward": _cell(2048, 0.02, "forward"),
    }}

    def test_a_complete_set_projects(self):
        result = pc.project(self.RECEIPT, "optimised", "ours_incumbent", 33, 2048)
        self.assertEqual(result["ratio_train_per_example"], 20.0)
        self.assertEqual(result["ratio_inference_per_example"], 10.0)

    def test_a_missing_cell_refuses(self):
        receipt = {"cells": dict(self.RECEIPT["cells"])}
        del receipt["cells"]["optimised|33|2048|train"]
        with self.assertRaises(SystemExit):
            pc.project(receipt, "optimised", "ours_incumbent", 33, 2048)

    def test_a_failed_cell_refuses_rather_than_being_skipped(self):
        receipt = {"cells": dict(self.RECEIPT["cells"])}
        receipt["cells"]["optimised|33|2048|train"] = {
            "batch": 2048, "failed": True, "error": "ResourceExhaustedError()"}
        with self.assertRaises(SystemExit):
            pc.project(receipt, "optimised", "ours_incumbent", 33, 2048)

    def test_an_accumulated_cell_is_charged_against_the_virtual_batch(self):
        receipt = {"cells": dict(self.RECEIPT["cells"])}
        receipt["cells"]["accum4|33|2048|train"] = _cell(
            2048, 1.0, "virtual_batch_train")
        result = pc.project(receipt, "accum4", "ours_incumbent", 33, 2048,
                            theirs_inference="optimised")
        self.assertEqual(result["their_train_section"], "virtual_batch_train")
        self.assertEqual(result["theirs_inference_variant"], "optimised")
        self.assertEqual(result["ratio_train_per_example"], 20.0)

    def test_an_accumulated_cell_refuses_to_guess_its_inference_variant(self):
        receipt = {"cells": dict(self.RECEIPT["cells"])}
        receipt["cells"]["accum4|33|2048|train"] = _cell(
            2048, 1.0, "virtual_batch_train")
        with self.assertRaises(SystemExit):
            pc.project(receipt, "accum4", "ours_incumbent", 33, 2048)


if __name__ == "__main__":
    unittest.main()
