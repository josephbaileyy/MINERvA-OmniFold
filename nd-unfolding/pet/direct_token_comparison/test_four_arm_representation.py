"""Tests for the four arms, the cap treatments, bucketing, and the width guard.

Every geometry fixture is built by the real producers -- ``build_variable_typed_batch``
and ``adapter.prepare_keras_inputs`` -- and then mutated, so a fixture cannot agree
with the guard by construction. Each guard has a test in the direction it acts and a
test in the direction it must not act.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import four_arm_representation as fourarm  # noqa: E402
import typed_descriptor_keras as adapter  # noqa: E402
import typed_descriptor_source_smoke as smoke  # noqa: E402
import typed_descriptors as typed  # noqa: E402

FAMILIES = tuple(contract.name for contract in typed.FAMILY_CONTRACTS)


def cloud(energies: list[float], *, seed: int = 0) -> np.ndarray:
    """Build one event's cluster block with the given energies."""
    rng = np.random.default_rng(seed)
    block = np.zeros((len(energies), fourarm.CLOUD_WIDTH), dtype=np.float32)
    block[:, 0] = energies
    block[:, 1:5] = rng.normal(size=(len(energies), 4))
    return block


def inputs_for(counts_per_row: np.ndarray, seed: int = 11) -> dict[str, object]:
    """Build real packed inputs for the given per-row family counts."""
    batch = fourarm.build_variable_typed_batch(typed, counts_per_row, seed)
    event = np.zeros((len(counts_per_row), 13), dtype=np.float32)
    return dict(adapter.prepare_keras_inputs(batch, event))


class ArmSpecTests(unittest.TestCase):
    def test_the_four_arms_are_single_factor_changes_from_the_incumbent(self) -> None:
        arms = fourarm.ARMS_BY_NAME
        self.assertEqual(set(arms), {"A", "B", "C", "D"})
        incumbent = arms["A"]
        for name, changed in (
            ("B", "typed_enabled"),
            ("C", None),
            ("D", "cap_treatment"),
        ):
            if changed is None:
                continue
            differences = [
                field
                for field in ("typed_enabled", "routing", "cap_treatment")
                if getattr(arms[name], field) != getattr(incumbent, field)
            ]
            self.assertEqual(differences, [changed], f"arm {name}")

    def test_c_differs_from_b_only_in_routing(self) -> None:
        arms = fourarm.ARMS_BY_NAME
        differences = [
            field
            for field in ("typed_enabled", "routing", "cap_treatment")
            if getattr(arms["C"], field) != getattr(arms["B"], field)
        ]
        self.assertEqual(differences, ["routing"])

    def test_a_and_d_differ_only_in_cap_treatment(self) -> None:
        arms = fourarm.ARMS_BY_NAME
        self.assertEqual(arms["A"].typed_enabled, arms["D"].typed_enabled)
        self.assertEqual(arms["A"].routing, arms["D"].routing)
        self.assertNotEqual(arms["A"].cap_treatment, arms["D"].cap_treatment)

    def test_routing_nothing_individually_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            fourarm.ArmSpec("X", typed_enabled=False, routing="direct",
                            cap_treatment="truncate")

    def test_unknown_cap_treatment_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            fourarm.ArmSpec("X", typed_enabled=True, routing="pooled",
                            cap_treatment="drop")


class CapTreatmentTests(unittest.TestCase):
    def test_truncation_keeps_the_highest_energies_in_order(self) -> None:
        block = fourarm.truncate_cloud(cloud([1.0, 50.0, 3.0] + [2.0] * 12))
        self.assertEqual(block.shape, (fourarm.CAP, fourarm.CLOUD_WIDTH))
        self.assertEqual(block[0, 0], 50.0)
        self.assertTrue(np.all(np.diff(block[:, 0]) <= 0))

    def test_truncation_below_the_cap_keeps_everything_and_pads(self) -> None:
        block = fourarm.truncate_cloud(cloud([5.0, 1.0, 3.0]))
        self.assertEqual(list(block[:3, 0]), [5.0, 3.0, 1.0])
        self.assertTrue(np.all(block[3:] == 0))

    def test_aggregation_conserves_total_energy_exactly(self) -> None:
        energies = [float(value) for value in range(40, 0, -1)]
        block = fourarm.aggregate_cloud(cloud(energies))
        self.assertAlmostEqual(
            float(block[:, 0].sum()), float(sum(energies)), places=3
        )

    def test_truncation_does_not_conserve_energy_when_the_cap_binds(self) -> None:
        # Control for the test above: if truncation also conserved energy, that
        # test would be measuring nothing.
        energies = [float(value) for value in range(40, 0, -1)]
        block = fourarm.truncate_cloud(cloud(energies))
        self.assertLess(float(block[:, 0].sum()), float(sum(energies)))

    def test_aggregate_records_how_many_objects_it_merged(self) -> None:
        block = fourarm.aggregate_cloud(cloud([float(v) for v in range(30, 0, -1)]))
        merged = block[fourarm.CAP - 1, len(fourarm.CLUSTER_CHANNELS) + 1]
        self.assertEqual(int(merged), 30 - (fourarm.CAP - 1))

    def test_only_the_final_slot_is_marked_as_an_aggregate(self) -> None:
        block = fourarm.aggregate_cloud(cloud([float(v) for v in range(20, 0, -1)]))
        flags = block[:, len(fourarm.CLUSTER_CHANNELS)]
        self.assertEqual(list(flags[: fourarm.CAP - 1]), [0.0] * (fourarm.CAP - 1))
        self.assertEqual(flags[fourarm.CAP - 1], 1.0)

    def test_aggregate_auxiliary_channels_are_the_tail_mean(self) -> None:
        block_in = cloud([float(v) for v in range(25, 0, -1)], seed=3)
        ordered = fourarm.order_clusters(block_in)
        tail = ordered[fourarm.CAP - 1 :]
        block = fourarm.aggregate_cloud(block_in)
        np.testing.assert_allclose(
            block[fourarm.CAP - 1, 1:5], tail[:, 1:5].mean(axis=0), rtol=1e-6
        )

    def test_a_cap_that_does_not_bind_leaves_the_input_untouched(self) -> None:
        # The opposite-direction case: no merge, no aggregate marker, no count, and
        # bit-identical to the incumbent treatment.
        block_in = cloud([9.0, 4.0, 7.0])
        aggregated = fourarm.aggregate_cloud(block_in)
        truncated = fourarm.truncate_cloud(block_in)
        np.testing.assert_array_equal(aggregated, truncated)
        self.assertEqual(aggregated[:, len(fourarm.CLUSTER_CHANNELS)].sum(), 0.0)

    def test_exactly_at_the_cap_does_not_merge(self) -> None:
        block_in = cloud([float(v) for v in range(fourarm.CAP, 0, -1)])
        np.testing.assert_array_equal(
            fourarm.aggregate_cloud(block_in), fourarm.truncate_cloud(block_in)
        )

    def test_both_treatments_produce_the_same_shape(self) -> None:
        block_in = cloud([float(v) for v in range(30, 0, -1)])
        self.assertEqual(
            fourarm.aggregate_cloud(block_in).shape,
            fourarm.truncate_cloud(block_in).shape,
        )

    def test_ordering_matches_the_production_builder(self) -> None:
        """The energy ranking must agree with ``_build_p12`` on random events."""
        rng = np.random.default_rng(4242)
        for _ in range(50):
            size = int(rng.integers(1, 30))
            energies = rng.gamma(2.0, 50.0, size=size)
            raw: dict[str, object] = {
                "cluster_energy": energies.tolist(),
                "cluster_pos": [0.0] * size,
                "cluster_z": [0.0] * size,
                "cluster_view": [1] * size,
                "cluster_time": [0.0] * size,
                "cluster_isMuontrack": [0] * size,
            }
            for name in smoke.GENERIC_VALUE_BRANCHES:
                raw[f"{name}_sz"] = size
            production = smoke._build_p12(raw)
            mine = fourarm.truncate_cloud(cloud(energies.tolist()))
            np.testing.assert_allclose(production[:, 0], mine[:, 0], rtol=1e-6)

    def test_discarded_energy_fraction_is_nan_for_an_empty_event(self) -> None:
        fractions = fourarm.discarded_energy_fraction(
            [cloud([]), cloud([float(v) for v in range(24, 0, -1)])]
        )
        self.assertTrue(np.isnan(fractions[0]))
        self.assertGreater(fractions[1], 0.0)

    def test_apply_cap_refuses_an_unknown_treatment(self) -> None:
        with self.assertRaises(ValueError):
            fourarm.apply_cap([cloud([1.0])], "discard")


class BucketingTests(unittest.TestCase):
    def setUp(self) -> None:
        rng = np.random.default_rng(5)
        self.counts = np.stack(
            [
                rng.integers(0, 3, size=40),
                rng.integers(0, 6, size=40),
                rng.integers(1, 4, size=40),
            ],
            axis=1,
        )
        self.inputs = inputs_for(self.counts)
        self.widths = fourarm.typed_widths(self.inputs, 40, FAMILIES)

    def test_measured_widths_equal_the_requested_counts(self) -> None:
        np.testing.assert_array_equal(self.widths, self.counts)

    def test_buckets_partition_the_events(self) -> None:
        buckets = fourarm.bucket_events(self.widths)
        fourarm.verify_partition(buckets, 40)

    def test_a_dropped_event_is_caught(self) -> None:
        buckets = fourarm.bucket_events(self.widths)
        key = next(iter(buckets))
        buckets[key] = buckets[key][1:]
        with self.assertRaises(ValueError):
            fourarm.verify_partition(buckets, 40)

    def test_every_batch_has_one_uniform_width(self) -> None:
        buckets = fourarm.bucket_events(self.widths)
        plan = fourarm.batch_plan(buckets, batch_size=4, seed=1)
        for key, batch in plan:
            for row in batch:
                self.assertEqual(tuple(self.widths[row]), key)

    def test_the_plan_visits_every_event_exactly_once(self) -> None:
        buckets = fourarm.bucket_events(self.widths)
        plan = fourarm.batch_plan(buckets, batch_size=4, seed=1)
        fourarm.verify_plan_covers_events(plan, 40)

    def test_the_plan_does_not_depend_on_the_arm(self) -> None:
        """I4: the partition is a function of the fixture and seed alone.

        Arms A and D disable typed families; if the plan were derived from what the
        model can see, they would get a different batch structure from B and C and
        the typed-object contrast would measure batching as well as representation.
        """
        buckets = fourarm.bucket_events(self.widths)
        first = fourarm.batch_plan(buckets, batch_size=4, seed=1)
        disabled = fourarm.disable_families(dict(self.inputs), FAMILIES)
        widths_disabled = fourarm.typed_widths(disabled, 40, FAMILIES)
        np.testing.assert_array_equal(widths_disabled, self.widths)
        second = fourarm.batch_plan(
            fourarm.bucket_events(widths_disabled), batch_size=4, seed=1
        )
        self.assertEqual([key for key, _ in first], [key for key, _ in second])
        for (_, left), (_, right) in zip(first, second):
            np.testing.assert_array_equal(left, right)

    def test_weights_survive_bucketing(self) -> None:
        buckets = fourarm.bucket_events(self.widths)
        plan = fourarm.batch_plan(buckets, batch_size=4, seed=1)
        weights = np.random.default_rng(9).gamma(2.0, 1.0, size=40)
        fourarm.verify_weights_preserved(plan, weights)

    def test_a_plan_that_loses_a_batch_fails_the_weight_check(self) -> None:
        buckets = fourarm.bucket_events(self.widths)
        plan = fourarm.batch_plan(buckets, batch_size=4, seed=1)[:-1]
        weights = np.random.default_rng(9).gamma(2.0, 1.0, size=40)
        with self.assertRaises(ValueError):
            fourarm.verify_weights_preserved(plan, weights)
        with self.assertRaises(ValueError):
            fourarm.verify_plan_covers_events(plan, 40)

    def test_batch_size_must_be_positive(self) -> None:
        with self.assertRaises(ValueError):
            fourarm.batch_plan(fourarm.bucket_events(self.widths), 0, 1)

    def test_bucket_order_is_shuffled_rather_than_monotone(self) -> None:
        buckets = fourarm.bucket_events(self.widths)
        keys = [key for key, _ in fourarm.batch_plan(buckets, batch_size=4, seed=1)]
        self.assertNotEqual(keys, sorted(keys))


class WidthSetGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = 12
        self.counts = np.tile(np.asarray([1, 1, 2]), (self.rows, 1))
        self.inputs = inputs_for(self.counts)

    def guard(self, widths, **kwargs) -> fourarm.WidthSetGuard:
        return fourarm.WidthSetGuard(widths, FAMILIES, **kwargs)

    def test_a_validated_uniform_width_is_accepted(self) -> None:
        measured = self.guard([(1, 1, 2)]).check_batch(
            self.inputs, self.rows, label="batch"
        )
        self.assertEqual(measured["width"], (1, 1, 2))
        self.assertEqual(measured["padded_positions"], 0)
        self.assertEqual(measured["typed_tokens_per_row"], 4)

    def test_an_unvalidated_width_is_refused(self) -> None:
        with self.assertRaises(ValueError) as caught:
            self.guard([(1, 1, 3)]).check_batch(self.inputs, self.rows, label="batch")
        self.assertIn("not in the validated set", str(caught.exception))

    def test_a_non_uniform_batch_is_refused(self) -> None:
        mixed = inputs_for(
            np.asarray([[1, 1, 2]] * 6 + [[1, 1, 3]] * 6)
        )
        with self.assertRaises(ValueError) as caught:
            self.guard([(1, 1, 2), (1, 1, 3)]).check_batch(
                mixed, self.rows, label="batch"
            )
        self.assertIn("not uniform", str(caught.exception))

    def test_token_masking_is_refused(self) -> None:
        mutated = dict(self.inputs)
        mask = np.asarray(mutated["prongs_token_mask"]).copy()
        mask[0] = False
        mutated["prongs_token_mask"] = mask
        with self.assertRaises(ValueError) as caught:
            self.guard([(1, 1, 2)]).check_batch(mutated, self.rows, label="batch")
        self.assertIn("masking", str(caught.exception))

    def test_an_undeclared_disabled_family_is_refused(self) -> None:
        mutated = fourarm.disable_families(dict(self.inputs), ("blobs",))
        with self.assertRaises(ValueError) as caught:
            self.guard([(1, 1, 2)]).check_batch(mutated, self.rows, label="batch")
        self.assertIn("unless declared", str(caught.exception))

    def test_a_declared_disabling_is_accepted(self) -> None:
        disabled = fourarm.disable_families(dict(self.inputs), FAMILIES)
        measured = self.guard([], declared_disabled=True).check_batch(
            disabled, self.rows, label="armA"
        )
        self.assertTrue(measured["declared_disabled"])

    def test_declaring_disabled_while_enabled_is_refused(self) -> None:
        with self.assertRaises(ValueError) as caught:
            self.guard([(1, 1, 2)], declared_disabled=True).check_batch(
                self.inputs, self.rows, label="armA"
            )
        self.assertIn("declared disabled", str(caught.exception))

    def test_partially_disabled_families_are_refused_either_way(self) -> None:
        partial = fourarm.disable_families(dict(self.inputs), ("photons",))
        with self.assertRaises(ValueError):
            self.guard([(1, 1, 2)]).check_batch(partial, self.rows, label="batch")
        with self.assertRaises(ValueError):
            self.guard([(1, 1, 2)], declared_disabled=True).check_batch(
                partial, self.rows, label="batch"
            )

    def test_declared_counts_must_agree_with_slots(self) -> None:
        mutated = dict(self.inputs)
        counts = np.asarray(mutated["prongs_counts"]).copy()
        counts[0] = 5
        mutated["prongs_counts"] = counts
        with self.assertRaises(ValueError) as caught:
            self.guard([(1, 1, 2)]).check_batch(mutated, self.rows, label="batch")
        self.assertIn("declared counts", str(caught.exception))

    def test_an_empty_validated_set_cannot_train(self) -> None:
        with self.assertRaises(ValueError):
            self.guard([])

    def test_an_empty_validated_set_is_allowed_only_when_declared_disabled(
        self,
    ) -> None:
        self.guard([], declared_disabled=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
