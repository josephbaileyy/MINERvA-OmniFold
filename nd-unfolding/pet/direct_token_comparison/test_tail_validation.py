"""Tests for the validation battery and the training refusal.

Everything except the cross-device classification runs on CPU, so the battery is
exercised end to end locally before it ever reaches a GPU. Each check is tested in the
direction it acts and, where it is a guard, in the direction it must not act.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import four_arm_representation as fourarm  # noqa: E402
import optimizer_diagnostic as diagnostic  # noqa: E402
import run_four_arm_experiment as entry  # noqa: E402
import tail_validation as validation  # noqa: E402
import typed_descriptor_keras as adapter  # noqa: E402
import typed_descriptors as typed  # noqa: E402
import typed_token_comparison as comparison  # noqa: E402

import run_typed_token_comparison as runner  # noqa: E402

CRITERIA = HERE / "VALIDATION_CRITERIA-20260918.json"


def modules() -> dict:
    return {
        "tf": adapter.require_tensorflow(),
        "fourarm": fourarm,
        "typed": typed,
        "adapter": adapter,
        "runner": runner,
        "comparison": comparison,
        "diagnostic": diagnostic,
        "validation": validation,
    }


class CriteriaTests(unittest.TestCase):
    def test_criteria_load_with_their_digest(self) -> None:
        criteria = validation.load_criteria(CRITERIA)
        self.assertEqual(len(criteria.sha256), 64)
        self.assertEqual(criteria.atol, 1e-5)
        self.assertEqual(criteria.rtol, 1e-4)

    def test_an_unknown_criterion_is_refused(self) -> None:
        criteria = validation.load_criteria(CRITERIA)
        with self.assertRaises(KeyError):
            criteria.check("V99_invented")

    def test_the_frozen_bound_is_the_measured_one(self) -> None:
        criteria = validation.load_criteria(CRITERIA)
        accuracy = criteria.check("V5b_finite_difference_accuracy")
        self.assertEqual(accuracy["step"], 0.01)
        self.assertEqual(accuracy["max_relative_error"], 0.005)
        self.assertIn("measured_basis", accuracy)

    def test_the_withdrawn_claim_is_recorded(self) -> None:
        criteria = validation.load_criteria(CRITERIA)
        self.assertIn("errors_cancel_in_paired_contrasts", criteria.body["withdrawn_claims"])


class TrainingRefusalTests(unittest.TestCase):
    """Training must not start on a receipt that does not cover it."""

    def receipt(self, **overrides) -> dict:
        body = {
            "commit": entry.head_commit(HERE.parent.parent.parent),
            "complete": True,
            "released_widths": [[0, 4, 2], [0, 18, 2]],
        }
        body.update(overrides)
        return body

    def write(self, body: dict, folder: Path) -> Path:
        path = folder / "receipt.json"
        path.write_text(json.dumps(body))
        return path

    def test_a_covering_receipt_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            path = self.write(self.receipt(), Path(scratch))
            result = entry.require_validation(
                HERE.parent.parent.parent, path, {(0, 4, 2)}
            )
            self.assertEqual(len(result["validation_receipt_sha256"]), 64)

    def test_a_receipt_from_another_commit_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            path = self.write(self.receipt(commit="0" * 40), Path(scratch))
            with self.assertRaises(ValueError) as caught:
                entry.require_validation(HERE.parent.parent.parent, path, {(0, 4, 2)})
            self.assertIn("does not describe this code", str(caught.exception))

    def test_an_incomplete_receipt_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            path = self.write(self.receipt(complete=False), Path(scratch))
            with self.assertRaises(ValueError):
                entry.require_validation(HERE.parent.parent.parent, path, {(0, 4, 2)})

    def test_an_unreleased_width_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            path = self.write(self.receipt(), Path(scratch))
            with self.assertRaises(ValueError) as caught:
                entry.require_validation(
                    HERE.parent.parent.parent, path, {(0, 4, 2), (0, 96, 2)}
                )
            self.assertIn("never released", str(caught.exception))


class BatteryTests(unittest.TestCase):
    """The battery, run for real on CPU at a small width."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.modules = modules()
        cls.criteria = validation.load_criteria(CRITERIA)
        cls.arm = fourarm.ARMS_BY_NAME["C"]
        cls.width = (1, 4, 2)

    def build(self, arm=None, width=None):
        return validation.prepare_run(
            self.modules,
            arm or self.arm,
            width or self.width,
            rows=256,
            batch_size=64,
            seed=2401,
            validated_widths=[width or self.width],
        )

    def test_prepare_run_partitions_and_guards(self) -> None:
        prepared = self.build()
        self.assertEqual(prepared.geometry["width"], self.width)
        self.assertEqual(prepared.geometry["padded_positions"], 0)
        fourarm.verify_partition(prepared.buckets, prepared.rows)
        fourarm.verify_plan_covers_events(prepared.plan, prepared.rows)

    def test_prepare_run_refuses_an_unvalidated_width(self) -> None:
        with self.assertRaises(ValueError):
            validation.prepare_run(
                self.modules,
                self.arm,
                (1, 4, 2),
                rows=64,
                batch_size=32,
                seed=1,
                validated_widths=[(1, 5, 2)],
            )

    def test_repeatability_is_bitwise(self) -> None:
        record = validation.check_repeatability(self.modules, self.build, 3)
        self.assertTrue(record["passed"], record)
        self.assertEqual(record["mismatched_weight_indices"], [])

    def test_duplicate_arm_null_holds(self) -> None:
        record = validation.check_duplicate_arm_null(
            self.modules, self.build, self.build, 3
        )
        self.assertTrue(record["passed"], record)

    def test_duplicate_arm_null_detects_a_real_difference(self) -> None:
        # The control: two genuinely different arms must NOT pass, or the check
        # would be incapable of reporting the thing it exists to report.
        other = fourarm.ARMS_BY_NAME["B"]
        record = validation.check_duplicate_arm_null(
            self.modules, self.build, lambda: self.build(arm=other), 3
        )
        self.assertFalse(record["passed"])

    def test_permutation_invariance_holds(self) -> None:
        record = validation.check_permutation_invariance(
            self.modules, self.build(), self.criteria
        )
        self.assertTrue(record["passed"], record)
        self.assertGreater(record["objects_permuted"], 0)

    def test_checkpoint_reload_is_bitwise(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            record = validation.check_checkpoint_reload(
                self.modules, self.build(), Path(scratch)
            )
        self.assertTrue(record["passed"], record)

    def test_finiteness_holds_after_steps(self) -> None:
        prepared = self.build()
        result = validation.run_steps(self.modules, prepared, 3)
        record = validation.check_finiteness(result, prepared)
        self.assertTrue(record["passed"], record)

    def test_input_and_mask_correctness_holds(self) -> None:
        record = validation.check_input_mask_correctness(self.modules, self.build())
        self.assertTrue(record["passed"], record)

    def test_input_mask_check_catches_a_count_mismatch(self) -> None:
        prepared = self.build()
        counts = np.asarray(prepared.inputs["prongs_counts"]).copy()
        counts[0] += 3
        prepared.inputs["prongs_counts"] = counts
        record = validation.check_input_mask_correctness(self.modules, prepared)
        self.assertFalse(record["passed"])

    def test_finite_differences_meet_the_frozen_bound(self) -> None:
        record = validation.check_finite_differences(
            self.modules, self.build(), self.criteria, 8
        )
        self.assertTrue(record["plateau_passed"], record)
        self.assertLessEqual(record["max_relative"], record["limit"], record)

    def test_float64_reference_tracks_the_float32_trajectory(self) -> None:
        captured = validation._two_steps_recording(self.modules, self.build(), "/CPU:0")
        record = validation.check_float64_reference(
            self.modules, captured, self.criteria
        )
        self.assertEqual(record["weights_compared"], 42)
        self.assertTrue(record["passed"], record["failures"])

    def test_float64_reference_notices_a_corrupted_trajectory(self) -> None:
        captured = validation._two_steps_recording(self.modules, self.build(), "/CPU:0")
        captured["states"][1][0] = captured["states"][1][0] + 1.0
        record = validation.check_float64_reference(
            self.modules, captured, self.criteria
        )
        self.assertFalse(record["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
