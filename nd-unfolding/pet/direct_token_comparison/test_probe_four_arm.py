"""Tests for the A3 probe's pure helpers.

The probe's numerical gate is the bound pipeline, driven with different fixtures, so
there is nothing here that re-checks tolerances. What is tested is the part that could
quietly go wrong: the ladder derived from a measured histogram, and the case naming
that keeps a width out of the stress-exempt list -- a collision there would turn a
gating failure into a recorded one.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import amended_preflight as preflight  # noqa: E402
import probe_four_arm_geometry_and_cost as probe  # noqa: E402


class LadderTests(unittest.TestCase):
    def test_a_single_valued_histogram_gives_one_rung(self) -> None:
        self.assertEqual(probe.ladder_from_histogram({"4": 100}, 3), (4,))

    def test_rungs_span_the_measured_distribution(self) -> None:
        histogram = {str(value): 10 for value in range(1, 101)}
        ladder = probe.ladder_from_histogram(histogram, 3)
        self.assertEqual(len(ladder), 3)
        self.assertLess(ladder[0], ladder[-1])
        self.assertGreaterEqual(ladder[0], 1)
        self.assertLessEqual(ladder[-1], 100)

    def test_rungs_are_sorted_and_unique(self) -> None:
        histogram = {"1": 50, "2": 50, "40": 1}
        ladder = probe.ladder_from_histogram(histogram, 4)
        self.assertEqual(list(ladder), sorted(set(ladder)))

    def test_an_empty_histogram_falls_back_to_the_minimum(self) -> None:
        self.assertEqual(probe.ladder_from_histogram({}, 3, minimum=1), (1,))

    def test_the_minimum_is_respected(self) -> None:
        histogram = {"0": 90, "1": 10}
        self.assertNotIn(0, probe.ladder_from_histogram(histogram, 3, minimum=1))

    def test_a_skewed_histogram_is_not_reduced_to_its_mode(self) -> None:
        # 90% of events at one value, a real tail beyond it: the ladder must reach
        # into the tail, or the gate would only ever cover the mode.
        histogram = {"2": 900, **{str(value): 10 for value in range(3, 13)}}
        ladder = probe.ladder_from_histogram(histogram, 3)
        self.assertGreater(max(ladder), 2)


class CaseNameTests(unittest.TestCase):
    def test_names_are_distinct_per_width(self) -> None:
        self.assertNotEqual(probe.case_name((1, 1, 2)), probe.case_name((1, 2, 1)))

    def test_no_name_can_collide_with_the_stress_exemption(self) -> None:
        for width in ((0, 0, 0), (1, 1, 2), (2, 12, 4)):
            self.assertNotIn(probe.case_name(width), preflight.STRESS_ONLY_CASES)

    def test_the_exemption_list_is_what_this_guards_against(self) -> None:
        # If the bound exemption list ever grows, this test tells us here rather
        # than by silently recording a failure that should have gated.
        self.assertEqual(preflight.STRESS_ONLY_CASES, ("variable",))


class FixtureCompatibilityTests(unittest.TestCase):
    """The bound preflight refuses a fixture whose key inventory differs.

    ``amended_preflight`` compares the bundle's arrays against the generated ones and
    raises on any inventory difference, so a replacement fixture builder that drifts
    from the bound one fails on the cluster rather than here. This pins the contract
    at the nominal width, where the two must agree exactly.
    """

    def test_width_cases_match_the_bound_fixture_inventory(self) -> None:
        import numpy as np

        import compatibility_preflight as original
        import four_arm_representation as fourarm
        import run_typed_token_comparison as runner
        import typed_descriptor_keras as adapter
        import typed_descriptors as typed
        import typed_token_comparison as comparison

        tf = adapter.require_tensorflow()
        modules = {
            "tf": tf,
            "fourarm": fourarm,
            "typed": typed,
            "adapter": adapter,
            "runner": runner,
            "comparison": comparison,
        }
        _, bound = original.fixtures()
        nominal = bound["nominal"]
        width = (1, 1, 2)
        _, mine = probe.width_case_builder(modules, [width], 4)()
        case = mine[probe.case_name(width)]
        self.assertEqual(set(nominal), set(case))
        for key in nominal:
            left, right = np.asarray(nominal[key]), np.asarray(case[key])
            self.assertEqual(left.dtype, right.dtype, key)
            self.assertEqual(left.shape, right.shape, key)


class ChildCommandTests(unittest.TestCase):
    """The child invocation must be parseable by the script's own parser.

    The first subprocess split omitted an argument the parser required, so all three
    gate groups died on argv before reaching TensorFlow. One cluster job to find, one
    local test to prevent.
    """

    def test_the_child_command_parses(self) -> None:
        command = probe.gate_child_command(
            Path("/checkout"), [(1, 1, 2)], 4, Path("/work"), Path("/work/g.json")
        )
        args = probe.build_parser().parse_args(command[2:])
        self.assertTrue(args.gate_group_only)
        self.assertEqual(args.checkout, Path("/checkout"))
        self.assertEqual(args.gate_rows, 4)
        self.assertEqual(args.output, Path("/work/g.json"))
        self.assertEqual(args.workspace, Path("/work"))

    def test_the_child_command_carries_the_widths_as_json(self) -> None:
        import json

        widths = [(0, 18, 1), (2, 85, 4)]
        command = probe.gate_child_command(
            Path("/c"), widths, 4, Path("/w"), Path("/w/g.json")
        )
        args = probe.build_parser().parse_args(command[2:])
        self.assertEqual(
            [tuple(w) for w in json.loads(args.widths)], [tuple(w) for w in widths]
        )

    def test_the_child_runs_the_same_file(self) -> None:
        command = probe.gate_child_command(
            Path("/c"), [(1, 1, 2)], 4, Path("/w"), Path("/w/g.json")
        )
        self.assertEqual(Path(command[1]).name, "probe_four_arm_geometry_and_cost.py")

    def test_the_parent_still_demands_a_source_receipt(self) -> None:
        # Relaxing the requirement for children must not let the parent run
        # without the measurement its ladder comes from.
        args = probe.build_parser().parse_args(["--checkout", "/c", "--output", "/o"])
        self.assertIsNone(args.source_receipt)
        self.assertFalse(args.gate_group_only)


class GroupingTests(unittest.TestCase):
    def test_the_bound_pipeline_group_size_is_four(self) -> None:
        self.assertEqual(probe.GROUP, 4)

    def test_a_group_of_the_wrong_size_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            probe.gate_width_group({}, [(1, 1, 2)], 4, Path("/nonexistent"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
