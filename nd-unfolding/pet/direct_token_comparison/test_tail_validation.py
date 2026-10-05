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
            "execution_path_digests": entry.execution_path_digests(
                HERE.parent.parent.parent
            ),
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

    def test_a_receipt_for_changed_execution_path_code_is_refused(self) -> None:
        digests = entry.execution_path_digests(HERE.parent.parent.parent)
        digests["nd-unfolding/pet/direct_token_comparison/tail_validation.py"] = "0" * 64
        with tempfile.TemporaryDirectory() as scratch:
            path = self.write(
                self.receipt(execution_path_digests=digests), Path(scratch)
            )
            with self.assertRaises(ValueError) as caught:
                entry.require_validation(HERE.parent.parent.parent, path, {(0, 4, 2)})
            self.assertIn("execution path has changed", str(caught.exception))

    def test_an_unrelated_commit_does_not_void_the_receipt(self) -> None:
        # Keying on HEAD meant adding a document silently voided validation. The
        # receipt must survive a commit that does not touch the validated path.
        with tempfile.TemporaryDirectory() as scratch:
            path = self.write(self.receipt(commit="0" * 40), Path(scratch))
            entry.require_validation(HERE.parent.parent.parent, path, {(0, 4, 2)})

    def test_every_execution_path_file_is_digested(self) -> None:
        digests = entry.execution_path_digests(HERE.parent.parent.parent)
        self.assertEqual(set(digests), set(entry.EXECUTION_PATH_FILES))
        self.assertTrue(all(len(v) == 64 for v in digests.values()))

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

    def test_finite_differences_record_each_coordinate(self) -> None:
        record = validation.check_finite_differences(
            self.modules, self.build(), self.criteria, 6
        )
        self.assertEqual(len(record["coordinate_details"]), record["coordinates"])
        for detail in record["coordinate_details"]:
            self.assertGreaterEqual(
                detail["abs_gradient"], record["gradient_floor"]
            )
            for key in ("absolute_error", "relative_error", "plateau_ok"):
                self.assertIn(key, detail)
        self.assertEqual(
            record["worst_coordinate"]["relative_error"], record["max_relative"]
        )

    def test_float64_reference_tracks_the_float32_trajectory(self) -> None:
        captured = validation._two_steps_recording(self.modules, self.build(), "/CPU:0")
        record = validation.check_float64_reference(
            self.modules, captured, self.criteria
        )
        self.assertEqual(record["weights_compared"], 42)
        self.assertTrue(record["passed"], record["failures"])

    def test_allclose_many_handles_differently_shaped_weights(self) -> None:
        """Submission 58493028 died here: 42 tensors of different shapes handed
        to np.asarray raise on the inhomogeneous shape instead of comparing."""
        left = [np.zeros((3, 4)), np.zeros(7), np.zeros((2, 2, 2))]
        right = [np.zeros((3, 4)), np.zeros(7), np.zeros((2, 2, 2))]
        ok, error = validation._allclose_many(left, right, self.criteria)
        self.assertTrue(ok)
        self.assertEqual(error, 0.0)
        right[1] = right[1] + 1.0
        ok, error = validation._allclose_many(left, right, self.criteria)
        self.assertFalse(ok)
        self.assertEqual(error, 1.0)

    def test_allclose_many_refuses_a_length_mismatch(self) -> None:
        ok, error = validation._allclose_many(
            [np.zeros(2)], [np.zeros(2), np.zeros(2)], self.criteria
        )
        self.assertFalse(ok)

    def test_cross_device_classification_runs_on_one_device(self) -> None:
        """The GPU-only path, exercised locally by pointing both sides at the CPU.

        Same device twice must agree on everything, so this is tier 1 and every
        sub-check passes. It cannot prove GPU behaviour, but it does prove the
        function computes and classifies rather than raising -- which is what the
        cluster discovered the hard way.
        """
        record = validation.classify_cross_device(
            self.modules, self.build, self.criteria, devices=("/CPU:0", "/CPU:0")
        )
        self.assertEqual(record["tier"], 1, record)
        self.assertEqual(record["failed"], [])
        self.assertIn("initial_weight_identity", record["subchecks"])
        self.assertFalse(record["subchecks"]["initial_weight_identity"]["exemptible"])

    def test_the_exempt_list_is_what_the_criteria_freeze(self) -> None:
        self.assertEqual(
            set(self.criteria.exempt_subchecks),
            {
                "gradient_agreement",
                "prediction_agreement",
                "updated_weight_agreement",
                "common_operand_replay",
            },
        )

    def test_float64_reference_notices_a_corrupted_trajectory(self) -> None:
        captured = validation._two_steps_recording(self.modules, self.build(), "/CPU:0")
        captured["states"][1][0] = captured["states"][1][0] + 1.0
        record = validation.check_float64_reference(
            self.modules, captured, self.criteria
        )
        self.assertFalse(record["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
