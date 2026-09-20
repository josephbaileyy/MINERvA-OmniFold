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


class TheAttentionUsesTheSameProjectionAsLinear(unittest.TestCase):
    """The attention spelled its own q/k/v projections as raw einsum.

    `flat_projection=True` was therefore true of `Linear` and false of the
    model, while the frozen EXECUTION recorded the layer's answer. At his
    projection_dim of 128, batch 2048 and 34 tokens, the gradient of one of
    those three projections is [128, 128, 2048, 34] float32 = 4.6 GB, and
    there are three: measured OOM on a 40 GB A100.
    """

    def test_the_two_spellings_agree(self):
        import numpy as np
        import tensorflow as tf
        import pet2_keras_port as port
        rng = np.random.default_rng(0)
        x = tf.constant(rng.standard_normal((3, 7, 16)), tf.float32)
        w = tf.constant(rng.standard_normal((11, 16)), tf.float32)
        flat = port.project(x, w, flat=True).numpy()
        einsum = port.project(x, w, flat=False).numpy()
        np.testing.assert_allclose(flat, einsum, rtol=0, atol=2e-5)

    def test_the_attention_carries_a_real_switch(self):
        """A getattr default is invisible to `set_reference_paths`."""
        import pet2_keras_port as port
        attn = port.MultiheadAttention(dim=16, num_heads=2)
        self.assertTrue(hasattr(attn, "flat_projection"))
        self.assertTrue(attn.flat_projection)

    def test_set_reference_paths_now_reaches_the_attention(self):
        import pet2_keras_port as port
        attn = port.MultiheadAttention(dim=16, num_heads=2)
        touched = port.set_reference_paths(attn, flat_projection=False)
        self.assertGreaterEqual(touched["flat_projection"], 2)  # attn + out_proj
        self.assertFalse(attn.flat_projection)

    def test_the_arm_forces_jit_compile(self):
        from pathlib import Path
        import theirs_omnifold_arm as toa
        source = Path(toa.__file__).read_text()
        self.assertIn('kw["jit_compile"] = True', source)
        self.assertIn("def compile(", source)

    def test_the_frozen_execution_claims_both(self):
        import frozen_design as fd
        self.assertTrue(fd.EXECUTION["flat_projection"])
        self.assertTrue(fd.EXECUTION["jit_compile"])
