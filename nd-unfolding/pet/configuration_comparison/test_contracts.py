"""Tests for the identity join, the authorization scope check, and the ceiling calibration.

Each test fixes one way the corresponding check could pass while the thing it guards is
broken. The join tests in particular are written against the failure directions, because
a join returns a correctly-shaped array whatever happens.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import authorization_scope as az
import identity_contract as ic
import reference_calibration as rc

ACCEPTANCE_MAP = (
    HERE.parent.parent / "products" / "pet" / "fullevent_fps"
    / "acceptance_map_fullevent_fps.json"
)


class Keys(unittest.TestCase):
    def test_collisions_are_counted_not_deduplicated(self):
        report = ic.describe_keys([[1, 1, 5], [1, 1, 5], [1, 1, 6]], "t")
        self.assertEqual((report.rows, report.distinct), (3, 2))
        self.assertEqual(report.duplicate_keys, 1)
        self.assertEqual(report.duplicated_row_count, 2)
        self.assertFalse(report.unique)

    def test_float_keys_are_refused_rather_than_cast(self):
        """A float key loses precision above 2**53 and compares unequal after a round trip."""
        with self.assertRaises(ic.ContractViolation):
            ic.describe_keys(np.array([[1.0, 1.0, 5.0]]), "t")

    def test_wrong_width_is_refused(self):
        with self.assertRaises(ic.ContractViolation):
            ic.describe_keys([[1, 2]], "t")

    def test_negative_components_are_refused(self):
        with self.assertRaises(ic.ContractViolation):
            ic.describe_keys([[1, -1, 5]], "t")


class Join(unittest.TestCase):
    def test_source_collision_stops_the_join(self):
        with self.assertRaises(ic.ContractViolation) as caught:
            ic.join_indices([[1, 1, 5]], [[1, 1, 5], [1, 1, 5]])
        self.assertIn("not a function", str(caught.exception))

    def test_unmatched_rows_are_minus_one_not_zero(self):
        """Index 0 would silently attach the first source row to every miss."""
        index, matched = ic.join_indices([[9, 9, 9], [1, 1, 5]], [[1, 1, 5]])
        self.assertFalse(bool(matched[0]))
        self.assertEqual(int(index[0]), -1)
        self.assertTrue(bool(matched[1]))

    def test_join_is_order_independent_in_the_source(self):
        """A shuffled source must give the same mapping, or ordering is load-bearing."""
        target = [[1, 1, 1], [1, 1, 2], [1, 1, 3]]
        forward = [[1, 1, 1], [1, 1, 2], [1, 1, 3]]
        shuffled = [[1, 1, 3], [1, 1, 1], [1, 1, 2]]
        ia, _ = ic.join_indices(target, forward)
        ib, _ = ic.join_indices(target, shuffled)
        self.assertEqual([forward[i] for i in ia], [shuffled[i] for i in ib])

    def test_keys_differing_only_in_the_last_component_do_not_alias(self):
        index, matched = ic.join_indices([[1, 2, 3]], [[1, 2, 4], [1, 3, 3], [2, 2, 3]])
        self.assertFalse(bool(matched[0]))

    def test_unmatched_pass_reco_row_is_a_hard_failure(self):
        with self.assertRaises(ic.ContractViolation) as caught:
            ic.verify_join(target_keys=[[1, 1, 1]], source_keys=[[2, 2, 2]],
                           pass_reco=[True], inventory="signal")
        self.assertIn("cannot be zero-filled", str(caught.exception))

    def test_unmatched_native_miss_is_accepted_and_reported(self):
        report = ic.verify_join(target_keys=[[1, 1, 1], [2, 2, 2]],
                                source_keys=[[1, 1, 1]],
                                pass_reco=[True, False], inventory="signal")
        self.assertEqual(report["unmatched_rows"], 1)
        self.assertTrue(report["unmatched_are_all_native_misses"])
        self.assertEqual(report["native_miss_rows"], 1)

    def test_target_collision_is_a_hard_failure(self):
        with self.assertRaises(ic.ContractViolation) as caught:
            ic.verify_join(target_keys=[[1, 1, 1], [1, 1, 1]],
                           source_keys=[[1, 1, 1]],
                           pass_reco=[True, True], inventory="signal")
        self.assertIn("row identity is not the event identity", str(caught.exception))

    def test_pass_reco_length_mismatch_is_refused(self):
        with self.assertRaises(ic.ContractViolation):
            ic.verify_join(target_keys=[[1, 1, 1]], source_keys=[[1, 1, 1]],
                           pass_reco=[True, True], inventory="signal")


class InventorySymmetry(unittest.TestCase):
    def test_symmetric_field_sets_pass(self):
        result = ic.check_inventory_symmetry(
            {"signal": ["blob_e", "prong_pid"], "data": ["prong_pid", "blob_e"],
             "background": ["blob_e", "prong_pid"]}
        )
        self.assertTrue(result["symmetric"])
        self.assertEqual(result["field_count"], 2)

    def test_a_field_missing_from_data_is_leakage_and_raises(self):
        with self.assertRaises(ic.ContractViolation) as caught:
            ic.check_inventory_symmetry(
                {"signal": ["blob_e", "prong_pid"], "data": ["blob_e"],
                 "background": ["blob_e", "prong_pid"]}
            )
        self.assertIn("inventory label", str(caught.exception))

    def test_empty_input_is_refused(self):
        with self.assertRaises(ic.ContractViolation):
            ic.check_inventory_symmetry({})


class Provenance(unittest.TestCase):
    def test_a_non_digest_is_refused(self):
        with self.assertRaises(ic.ContractViolation):
            ic.provenance_record(source_files={"a.root": "not-a-digest"},
                                 manifests={}, dump_npz_sha256="0" * 64)

    def test_missing_sources_are_refused(self):
        with self.assertRaises(ic.ContractViolation):
            ic.provenance_record(source_files={}, manifests={}, dump_npz_sha256="0" * 64)

    def test_a_valid_record_sorts_its_keys(self):
        record = ic.provenance_record(
            source_files={"b.root": "a" * 64, "a.root": "b" * 64},
            manifests={"m.txt": "c" * 64}, dump_npz_sha256="d" * 64)
        self.assertEqual(list(record["source_files"]), ["a.root", "b.root"])


class AuthorizationScope(unittest.TestCase):
    def test_a_read_inside_a1_passes(self):
        report = az.require_within_authorization(["ev_run", "cluster_energy", "n_prongs"])
        self.assertTrue(report.within_authorization)

    def test_a_blob_value_branch_exceeds_a1(self):
        """A1 covers MasterAnaDev_BlobTotalE_sz -- the count -- not the values."""
        with self.assertRaises(az.AuthorizationError) as caught:
            az.require_within_authorization(["cluster_energy", "MasterAnaDev_BlobTotalE"])
        self.assertIn("MasterAnaDev_BlobTotalE", str(caught.exception))
        self.assertIn("needs a new authorization", str(caught.exception))

    def test_unexercised_authorized_branches_are_reported_not_fatal(self):
        report = az.compare_scope(["ev_run"])
        self.assertTrue(report.within_authorization)
        self.assertIn("cluster_energy", report.unexercised)

    def test_empty_authorization_permits_nothing(self):
        with self.assertRaises(az.AuthorizationError):
            az.compare_scope(["ev_run"], authorized=[])

    def test_the_smoke_guard_is_wider_than_a1(self):
        """The measured finding: the existing guard cannot fire on an overrun."""
        import typed_descriptor_source_smoke as smoke
        audit = az.audit_guard(smoke.REQUIRED_BRANCHES)
        self.assertTrue(audit["guard_is_wider_than_authorization"])
        self.assertIn("MasterAnaDev_BlobX",
                      audit["branches_the_guard_would_permit_but_a1_does_not"])
        self.assertIn("cannot fire", audit["consequence"])

    def test_typed_object_gap_names_the_values_not_the_counts(self):
        gap = az.typed_object_gap(["MasterAnaDev_BlobTotalE", "MasterAnaDev_BlobTotalE_sz"])
        self.assertEqual(gap["needs_new_authorization"], ["MasterAnaDev_BlobTotalE"])
        self.assertEqual(gap["already_authorized"], ["MasterAnaDev_BlobTotalE_sz"])


class ReferenceCalibration(unittest.TestCase):
    def setUp(self):
        self.product = json.loads(ACCEPTANCE_MAP.read_text())

    def test_reproduces_the_committed_truth_mass_curve(self):
        """A reimplementation is only trustworthy if it reproduces a committed number."""
        checked = rc.verify_against_product(self.product)
        self.assertEqual(sorted(checked, key=int), ["1", "2", "3", "4"])
        for entry in checked.values():
            self.assertTrue(entry["agrees"])
            self.assertLess(entry["deviation"], 1e-12)

    def test_a_corrupted_product_field_is_detected(self):
        bad = dict(self.product)
        bad["ideal_recovery_percell_truthmass_weighted_by_k"] = {"3": 0.5}
        with self.assertRaises(ValueError):
            rc.verify_against_product(bad)

    def test_the_ceiling_spans_nearly_the_unit_interval_across_weightings(self):
        """The applicability demonstration: an inherited ceiling is arbitrary."""
        sens = rc.weighting_sensitivity(
            self.product["acceptance_cells_pt_major"],
            self.product["truth_mass_cells_pt_major"], 3)
        values = list(sens.values())
        self.assertLess(min(values), 0.05)
        self.assertGreater(max(values), 0.95)
        self.assertGreater(max(values) - min(values), 0.9)

    def test_attainable_fraction_is_monotone_in_iterations(self):
        a = [0.0, 0.2, 0.9]
        f1 = rc.attainable_fraction(a, 1)
        f3 = rc.attainable_fraction(a, 3)
        self.assertTrue(np.all(f3 >= f1))
        self.assertEqual(f1[0], 0.0)  # a zero-acceptance cell stays unreachable at any k

    def test_zero_acceptance_cells_are_never_recoverable(self):
        self.assertEqual(rc.ceiling([0.0, 0.0], [1.0, 1.0], 50), 0.0)

    def test_invalid_inputs_are_refused(self):
        for bad in ([-0.1], [1.1], [float("nan")]):
            with self.assertRaises(ValueError):
                rc.attainable_fraction(bad, 3)
        with self.assertRaises(ValueError):
            rc.attainable_fraction([0.5], 0)
        with self.assertRaises(ValueError):
            rc.ceiling([0.5], [-1.0], 3)
        with self.assertRaises(ValueError):
            rc.ceiling([0.5], [0.0], 3)
        with self.assertRaises(ValueError):
            rc.ceiling([0.5, 0.5], [1.0], 3)


if __name__ == "__main__":
    unittest.main()
