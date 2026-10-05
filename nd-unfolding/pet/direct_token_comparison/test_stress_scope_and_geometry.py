"""Controls for the stress-only gate scope and the production geometry guard.

Joseph's 2026-09-16 decision exempts the variable-length stress geometry from the
cross-device gate for this frozen synthetic campaign, on two conditions: the
discrepancy stays recorded as a failure rather than being waved through, and every
production batch is verified to use the covered geometry. Both conditions are
load-bearing, so both are tested here in the direction they act -- each control
must fire on the bad input *and* stay silent on the good one.

Every geometry fixture is derived from the real producer,
``run_typed_token_comparison.make_fixture`` followed by
``prepare_keras_inputs``, and then mutated. A fixture hand-built to match the
guard could only ever agree with the guard; one built from the producer can
disagree with it, which is the point.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import amended_preflight  # noqa: E402
import run_typed_token_comparison as runner  # noqa: E402
import typed_descriptor_keras as adapter  # noqa: E402

ROWS = 6


def production_inputs(rows: int = ROWS) -> dict[str, Any]:
    """Build exactly what the frozen matrix builds, via the real producer."""
    batch, event, generic, _ = runner.make_fixture(rows, 2401)
    inputs = adapter.prepare_keras_inputs(batch, event)
    inputs.update(
        generic_values=generic, generic_mask=np.ones(generic.shape[:2], dtype=bool)
    )
    return dict(inputs)


def gate_row(case: str, routing: str, terminal: str) -> dict[str, Any]:
    """Build one model row carrying a gate verdict."""
    return {
        "case": case,
        "routing": routing,
        "device": "/device:GPU:0",
        "gate": {"terminal": terminal, "key_bias_index": 27, "key_bias_shape": [4, 8]},
    }


class CoveredGeometryGuard(unittest.TestCase):
    """The guard must accept the production geometry and refuse every departure."""

    def setUp(self) -> None:
        self.inputs = production_inputs()

    def test_production_geometry_is_accepted(self) -> None:
        """The positive control: the real producer's output must pass."""
        measured = runner.assert_covered_geometry(self.inputs, ROWS, label="train")
        self.assertEqual(measured["photons"], 1)
        self.assertEqual(measured["blobs"], 1)
        self.assertEqual(measured["prongs"], 2)
        self.assertEqual(measured["typed_tokens_per_row"], 4)
        self.assertEqual(measured["padded_positions"], 0)

    def test_variable_multiplicity_is_refused(self) -> None:
        """Dropping one object makes the batch padded, which is uncovered."""
        inputs = dict(self.inputs)
        keep = np.ones(len(inputs["prongs_segment_ids"]), dtype=bool)
        keep[0] = False
        for suffix in ("segment_ids", "values", "masks", "token_mask"):
            inputs[f"prongs_{suffix}"] = inputs[f"prongs_{suffix}"][keep]
        counts = inputs["prongs_counts"].copy()
        counts[0] -= 1
        inputs["prongs_counts"] = counts
        with self.assertRaises(ValueError) as caught:
            runner.assert_covered_geometry(inputs, ROWS, label="train")
        self.assertIn("covered width", str(caught.exception))

    def test_uniform_but_unvalidated_width_is_refused(self) -> None:
        """The opposite direction: uniform yet wider than the validated geometry.

        A guard that only looked for ragged rows would wave this through, even
        though the GPU gate never validated an attention sequence of that length.
        """
        batch, event, generic, _ = runner.make_fixture(ROWS, 2401)
        inputs = adapter.prepare_keras_inputs(batch, event)
        inputs.update(
            generic_values=generic, generic_mask=np.ones(generic.shape[:2], dtype=bool)
        )
        extra = np.arange(ROWS, dtype=np.int32)
        order = np.argsort(
            np.concatenate([inputs["prongs_segment_ids"], extra]), kind="stable"
        )
        for suffix in ("values", "masks", "token_mask"):
            column = inputs[f"prongs_{suffix}"]
            inputs[f"prongs_{suffix}"] = np.concatenate([column, column[:ROWS]])[order]
        inputs["prongs_segment_ids"] = np.concatenate(
            [inputs["prongs_segment_ids"], extra]
        )[order]
        inputs["prongs_counts"] = inputs["prongs_counts"] + 1
        with self.assertRaises(ValueError) as caught:
            runner.assert_covered_geometry(dict(inputs), ROWS, label="train")
        self.assertIn("covered width", str(caught.exception))

    def test_token_level_masking_is_refused(self) -> None:
        """Production never token-masks, and the GPU gate never covered it."""
        inputs = dict(self.inputs)
        token_mask = inputs["blobs_token_mask"].copy()
        token_mask[0] = False
        inputs["blobs_token_mask"] = token_mask
        with self.assertRaises(ValueError) as caught:
            runner.assert_covered_geometry(inputs, ROWS, label="train")
        self.assertIn("token-level masking", str(caught.exception))

    def test_disabled_family_is_refused(self) -> None:
        """A disabled family is the preflight's masked stress case, not production."""
        inputs = dict(self.inputs)
        enabled = np.asarray(inputs["photons_enabled"]).copy()
        enabled[1] = False
        inputs["photons_enabled"] = enabled
        with self.assertRaises(ValueError) as caught:
            runner.assert_covered_geometry(inputs, ROWS, label="train")
        self.assertIn("disabled family", str(caught.exception))

    def test_declared_counts_must_match_slots(self) -> None:
        """A count that disagrees with the packed slots is refused."""
        inputs = dict(self.inputs)
        counts = inputs["prongs_counts"].copy()
        counts[2] = 99
        inputs["prongs_counts"] = counts
        with self.assertRaises(ValueError) as caught:
            runner.assert_covered_geometry(inputs, ROWS, label="train")
        self.assertIn("declared counts", str(caught.exception))

    def test_row_count_mismatch_is_refused(self) -> None:
        """Segment ids beyond the declared row count are refused."""
        with self.assertRaises(ValueError) as caught:
            runner.assert_covered_geometry(self.inputs, ROWS - 1, label="test")
        self.assertIn("exceed the row count", str(caught.exception))

    def test_every_row_subset_inherits_the_covered_geometry(self) -> None:
        """The batch argument: uniform over all rows implies uniform over a subset."""
        for selection in ([0], [1, 3], [0, 1, 2, 3, 4, 5], [5, 4]):
            rows = np.asarray(selection, dtype=np.int64)
            selected = runner.select_inputs(self.inputs, rows)
            selected.update(
                photons_enabled=self.inputs["photons_enabled"][rows],
                blobs_enabled=self.inputs["blobs_enabled"][rows],
                prongs_enabled=self.inputs["prongs_enabled"][rows],
            )
            measured = runner.assert_covered_geometry(
                selected, len(rows), label="batch"
            )
            self.assertEqual(measured["padded_positions"], 0)


class StressScopeConsistency(unittest.TestCase):
    """A failure is tolerated only for an authorized stress case, only if declared."""

    def test_clean_pass_is_accepted(self) -> None:
        """No failures, plain PASS, nothing declared."""
        rows = [gate_row("nominal", "direct", "PASS")]
        receipt = {"terminal": "PASS", "stress_failures": []}
        self.assertEqual(amended_preflight.check_stress_consistency(receipt, rows), [])

    def test_declared_stress_failure_is_accepted(self) -> None:
        """The authorized case may fail when the verdict and list say so."""
        rows = [
            gate_row("nominal", "direct", "PASS"),
            gate_row("variable", "direct", "FAILED-STRESS"),
        ]
        receipt = {
            "terminal": amended_preflight.PASS_WITH_STRESS,
            "stress_failures": ["variable/direct"],
        }
        self.assertEqual(
            amended_preflight.check_stress_consistency(receipt, rows),
            ["variable/direct"],
        )

    def test_gated_case_failure_is_refused(self) -> None:
        """A non-stress case must never be excused, however it is declared."""
        rows = [gate_row("nominal", "direct", "FAILED-STRESS")]
        receipt = {
            "terminal": amended_preflight.PASS_WITH_STRESS,
            "stress_failures": ["nominal/direct"],
        }
        with self.assertRaises(ValueError) as caught:
            amended_preflight.check_stress_consistency(receipt, rows)
        self.assertIn("gated case failed", str(caught.exception))

    def test_green_verdict_hiding_a_failure_is_refused(self) -> None:
        """A bare PASS must not survive alongside a failing row."""
        rows = [gate_row("variable", "direct", "FAILED-STRESS")]
        receipt = {"terminal": "PASS", "stress_failures": ["variable/direct"]}
        with self.assertRaises(ValueError) as caught:
            amended_preflight.check_stress_consistency(receipt, rows)
        self.assertIn("verdict disagrees", str(caught.exception))

    def test_undeclared_failure_is_refused(self) -> None:
        """A failing row that the receipt does not list is refused."""
        rows = [gate_row("variable", "direct", "FAILED-STRESS")]
        receipt = {
            "terminal": amended_preflight.PASS_WITH_STRESS,
            "stress_failures": [],
        }
        with self.assertRaises(ValueError) as caught:
            amended_preflight.check_stress_consistency(receipt, rows)
        self.assertIn("disagree with the model rows", str(caught.exception))

    def test_stress_verdict_without_a_failure_is_refused(self) -> None:
        """The opposite direction: the stress verdict cannot be claimed spuriously."""
        rows = [gate_row("nominal", "direct", "PASS")]
        receipt = {
            "terminal": amended_preflight.PASS_WITH_STRESS,
            "stress_failures": [],
        }
        with self.assertRaises(ValueError) as caught:
            amended_preflight.check_stress_consistency(receipt, rows)
        self.assertIn("verdict disagrees", str(caught.exception))

    def test_only_the_authorized_case_is_exempt(self) -> None:
        """The exempt set is exactly what the decision named."""
        self.assertEqual(amended_preflight.STRESS_ONLY_CASES, ("variable",))


if __name__ == "__main__":
    unittest.main()
