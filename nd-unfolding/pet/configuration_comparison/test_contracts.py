"""Tests for the identity join, the authorization scope check, and the ceiling calibration.

Each test fixes one way the corresponding check could pass while the thing it guards is
broken. The join tests in particular are written against the failure directions, because
a join returns a correctly-shaped array whatever happens.
"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import authorization_scope as az
import calibrate_cost as cc
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
    """Joins on the COMPOSITE key. `fields=ic.KEY_FIELDS` is the opt-in for an
    inventory whose bare triple has been SHOWN unique -- the three MC trees -- and
    the collision guard still has to hold there."""

    MC = ic.KEY_FIELDS

    def test_source_collision_stops_the_join(self):
        with self.assertRaises(ic.ContractViolation) as caught:
            ic.join_indices([[1, 1, 5]], [[1, 1, 5], [1, 1, 5]], fields=self.MC)
        self.assertIn("not a function", str(caught.exception))

    def test_unmatched_rows_are_minus_one_not_zero(self):
        """Index 0 would silently attach the first source row to every miss."""
        index, matched = ic.join_indices([[9, 9, 9], [1, 1, 5]], [[1, 1, 5]],
                                         fields=self.MC)
        self.assertFalse(bool(matched[0]))
        self.assertEqual(int(index[0]), -1)
        self.assertTrue(bool(matched[1]))

    def test_join_is_order_independent_in_the_source(self):
        """A shuffled source must give the same mapping, or ordering is load-bearing."""
        target = [[1, 1, 1], [1, 1, 2], [1, 1, 3]]
        forward = [[1, 1, 1], [1, 1, 2], [1, 1, 3]]
        shuffled = [[1, 1, 3], [1, 1, 1], [1, 1, 2]]
        ia, _ = ic.join_indices(target, forward, fields=self.MC)
        ib, _ = ic.join_indices(target, shuffled, fields=self.MC)
        self.assertEqual([forward[i] for i in ia], [shuffled[i] for i in ib])

    def test_keys_differing_only_in_the_last_component_do_not_alias(self):
        index, matched = ic.join_indices([[1, 2, 3]], [[1, 2, 4], [1, 3, 3], [2, 2, 3]],
                                         fields=self.MC)
        self.assertFalse(bool(matched[0]))

    def test_unmatched_pass_reco_row_is_a_hard_failure(self):
        with self.assertRaises(ic.ContractViolation) as caught:
            ic.verify_join(fields=self.MC, target_keys=[[1, 1, 1]],
                           source_keys=[[2, 2, 2]], pass_reco=[True], inventory="signal")
        self.assertIn("cannot be zero-filled", str(caught.exception))

    def test_unmatched_native_miss_is_accepted_and_reported(self):
        report = ic.verify_join(fields=self.MC, target_keys=[[1, 1, 1], [2, 2, 2]],
                                source_keys=[[1, 1, 1]],
                                pass_reco=[True, False], inventory="signal")
        self.assertEqual(report["unmatched_rows"], 1)
        self.assertTrue(report["unmatched_are_all_native_misses"])
        self.assertEqual(report["native_miss_rows"], 1)

    def test_target_collision_is_a_hard_failure(self):
        with self.assertRaises(ic.ContractViolation) as caught:
            ic.verify_join(fields=self.MC, target_keys=[[1, 1, 1], [1, 1, 1]],
                           source_keys=[[1, 1, 1]],
                           pass_reco=[True, True], inventory="signal")
        self.assertIn("row identity is not the event identity", str(caught.exception))

    def test_pass_reco_length_mismatch_is_refused(self):
        with self.assertRaises(ic.ContractViolation):
            ic.verify_join(fields=self.MC, target_keys=[[1, 1, 1]],
                           source_keys=[[1, 1, 1]], pass_reco=[True, True],
                           inventory="signal")


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


UUID_A = "GPU-11111111-2222-3333-4444-555555555555"
UUID_B = "GPU-99999999-8888-7777-6666-555555555555"


def _identity(uuid: str) -> dict:
    return {"cuda_visible_devices": "0", "primary_uuid": uuid,
            "primary_pci_bus_id": "00000000:03:00.0",
            "devices": [{"uuid": uuid, "pci_bus_id": "00000000:03:00.0", "name": "A100"}]}


def _throughput(step_seconds: float, batch: int, tokens: int) -> dict:
    return {"repeats": 20, "step_seconds_median": step_seconds,
            "step_seconds_min": step_seconds, "step_seconds_max": step_seconds,
            "coefficient_of_variation": 0.0, "batch": batch, "tokens": tokens,
            "seconds_per_example": step_seconds / batch,
            "examples_per_second": batch / step_seconds}


def _ours_half(uuid: str = UUID_A, tokens=cc.TOKEN_COUNTS, inference: bool = True) -> dict:
    half = {"gpu_identity": _identity(uuid),
            "by_tokens": {str(t): _throughput(0.010 * (t / 12.0), cc.OUR_BATCH, t)
                          for t in tokens}}
    if inference:
        # A forward pass at a third of the training step, which is the right order
        # for forward-only work and keeps the arithmetic checkable by hand.
        half["inference"] = {
            str(t): _throughput(0.010 * (t / 12.0) / 3.0, cc.OUR_BATCH, t)
            for t in tokens}
    return half


def _theirs_half(uuid: str = UUID_A, tokens=cc.TOKEN_COUNTS, factor: float = 6.0,
                 inference: bool = True) -> dict:
    half = {"gpu_identity": _identity(uuid),
            "by_tokens": {
                str(t): {
                    # Same seconds-per-example ratio at both batches, so the expected
                    # ratio is exactly `factor` and the test checks arithmetic, not noise.
                    "native_batch": _throughput(
                        0.010 * (t / 12.0) * factor * (cc.THEIR_BATCH / cc.OUR_BATCH),
                        cc.THEIR_BATCH, t),
                    "matched_batch": _throughput(
                        0.010 * (t / 12.0) * factor, cc.OUR_BATCH, t),
                }
                for t in tokens}}
    if inference:
        half["inference"] = {
            str(t): _throughput(0.010 * (t / 12.0) * factor / 3.0, cc.OUR_BATCH, t)
            for t in tokens}
    return half


class CostReduction(unittest.TestCase):
    """The reducer must accept a genuine pair and reject every degenerate one.

    An earlier version compared TensorFlow's `/device:GPU:0` against PyTorch's
    `NVIDIA A100-SXM4-40GB`, which never compare equal -- so it would have rejected
    every real pair. Both directions are therefore tested.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, ours: dict | None = None, theirs: dict | None = None):
        op, tp = self.root / "ours.json", self.root / "theirs.json"
        if ours is not None:
            op.write_text(json.dumps(ours))
        if theirs is not None:
            tp.write_text(json.dumps(theirs))
        return op, tp

    def test_a_matching_pair_reduces(self):
        op, tp = self._write(_ours_half(), _theirs_half())
        receipt = cc.reduce_halves(op, tp)
        self.assertEqual(receipt["gpu_identity"]["matched_on"],
                         "primary_uuid from nvidia-smi")
        self.assertEqual(sorted(receipt["measured_throughput"]),
                         sorted(str(t) for t in cc.TOKEN_COUNTS))

    def test_the_reduced_ratio_is_the_injected_one(self):
        """Arithmetic, not plumbing: a factor of 6 must come back as 6."""
        op, tp = self._write(_ours_half(), _theirs_half(factor=6.0))
        receipt = cc.reduce_halves(op, tp)
        for row in receipt["measured_throughput"].values():
            self.assertAlmostEqual(row["ratio_per_example_native_batch"], 6.0, places=9)
            self.assertAlmostEqual(row["ratio_per_example_matched_batch"], 6.0, places=9)

    def test_measured_and_projected_are_separate_blocks(self):
        """A GPU-hour is model-derived and must not sit inside the measured block."""
        op, tp = self._write(_ours_half(), _theirs_half())
        receipt = cc.reduce_halves(op, tp)
        measured = json.dumps(receipt["measured_throughput"])
        self.assertNotIn("gpu_hours", measured)
        projected = receipt["projected_evaluation_cost"]
        self.assertIn("budget_model", projected)
        self.assertIn("residual_overhead_caveat", projected)
        self.assertIn("derived_not_measured", projected)
        for row in projected["by_tokens"].values():
            self.assertIn("arm_pair_evaluation_gpu_hours", row)

    def test_the_cross_framework_qualification_survives_reduction(self):
        op, tp = self._write(_ours_half(), _theirs_half())
        receipt = cc.reduce_halves(op, tp)
        self.assertIn("FRAMEWORK-UNMATCHED", receipt["cross_framework_qualification"])

    def test_the_thirty_three_token_projection_exceeds_the_twelve_token_one(self):
        """More tokens must cost more; a flat projection would mean the loop did nothing."""
        op, tp = self._write(_ours_half(), _theirs_half())
        receipt = cc.reduce_halves(op, tp)
        by_tokens = receipt["projected_evaluation_cost"]["by_tokens"]
        self.assertGreater(by_tokens["33"]["arm_pair_evaluation_gpu_hours"],
                           by_tokens["12"]["arm_pair_evaluation_gpu_hours"])

    def test_evaluation_cost_exceeds_fit_cost_once_inference_is_counted(self):
        """Reweighting and validation are 36M presentations against 96M trained."""
        op, tp = self._write(_ours_half(), _theirs_half())
        receipt = cc.reduce_halves(op, tp)
        for row in receipt["projected_evaluation_cost"]["by_tokens"].values():
            self.assertTrue(row["inference_measured"])
            self.assertGreater(row["arm_pair_evaluation_gpu_hours"],
                               row["arm_pair_fit_gpu_hours"])

    def test_unmeasured_inference_is_reported_as_absent_not_as_zero(self):
        """A fit-only number must not be handed back under an evaluation label.

        This is the failure mode the rename guards against: silently reporting fits
        as the evaluation cost understates it by the whole inference leg, and a
        reader cannot tell from the number alone.
        """
        op, tp = self._write(_ours_half(inference=False), _theirs_half(inference=False))
        receipt = cc.reduce_halves(op, tp)
        for row in receipt["projected_evaluation_cost"]["by_tokens"].values():
            self.assertFalse(row["inference_measured"])
            self.assertIsNone(row["arm_pair_evaluation_gpu_hours"])
            self.assertIsNone(row["final_comparison_gpu_hours_by_seeds"])
            self.assertGreater(row["arm_pair_fit_gpu_hours"], 0.0)

    def test_paper_interaction_flags_survive_reduction(self):
        """His arm is the V1-paper model, not PET2's class defaults."""
        op, tp = self._write(_ours_half(), _theirs_half())
        receipt = cc.reduce_halves(op, tp)
        self.assertEqual(receipt["interaction_flags"],
                         {"use_int": False, "local_int": False})
        self.assertIn("OLS_int", receipt["interaction_flag_correction"])

    def test_different_physical_gpus_are_rejected(self):
        op, tp = self._write(_ours_half(UUID_A), _theirs_half(UUID_B))
        with self.assertRaises(SystemExit) as caught:
            cc.reduce_halves(op, tp)
        self.assertIn("different physical GPUs", str(caught.exception))

    def test_a_missing_identity_is_rejected(self):
        broken = _ours_half()
        broken["gpu_identity"] = {}
        op, tp = self._write(broken, _theirs_half())
        with self.assertRaises(SystemExit) as caught:
            cc.reduce_halves(op, tp)
        self.assertIn("missing its GPU identity", str(caught.exception))

    def test_a_missing_half_is_rejected_rather_than_reported_one_sided(self):
        op, tp = self._write(_ours_half(), None)
        with self.assertRaises(SystemExit) as caught:
            cc.reduce_halves(op, tp)
        self.assertIn("refusing to report one", str(caught.exception))

    def test_a_missing_token_count_is_rejected(self):
        op, tp = self._write(_ours_half(), _theirs_half(tokens=(12,)))
        with self.assertRaises(SystemExit) as caught:
            cc.reduce_halves(op, tp)
        self.assertIn("token count 33 is missing", str(caught.exception))

    def test_both_promised_token_counts_are_configured(self):
        self.assertEqual(tuple(cc.TOKEN_COUNTS), (12, 33))

    def test_a_failed_native_cell_still_reduces_from_the_matched_cell(self):
        """Measured 2026-09-18: batch 2048 raised a CUDA config error on an A100.

        The like-for-like matched-batch comparison survived, so the costing must too --
        losing the whole arm to his native batch failing would be a reporting choice
        dressed as a measurement limit.
        """
        theirs = _theirs_half()
        for key in theirs["by_tokens"]:
            theirs["by_tokens"][key]["native_batch"] = {
                "error": "RuntimeError: CUDA error: invalid configuration argument",
                "tokens": int(key), "batch": cc.THEIR_BATCH}
        op, tp = self._write(_ours_half(), theirs)
        receipt = cc.reduce_halves(op, tp)
        for row in receipt["measured_throughput"].values():
            self.assertFalse(row["native_batch_available"])
            self.assertIsNone(row["ratio_per_example_native_batch"])
            self.assertAlmostEqual(row["ratio_per_example_matched_batch"], 6.0, places=9)
            self.assertEqual(row["ratio_used_for_projection"], "matched_batch")
        for row in receipt["projected_evaluation_cost"]["by_tokens"].values():
            self.assertIn("matched_batch", row["ratio_source"])

    def test_a_failed_matched_cell_is_rejected(self):
        """Without the like-for-like cell there is no ratio to report."""
        theirs = _theirs_half()
        theirs["by_tokens"]["12"]["matched_batch"] = {
            "error": "RuntimeError: boom", "tokens": 12, "batch": cc.OUR_BATCH}
        op, tp = self._write(_ours_half(), theirs)
        with self.assertRaises(SystemExit) as caught:
            cc.reduce_halves(op, tp)
        self.assertIn("like-for-like", str(caught.exception))

    def test_projection_uses_the_matched_ratio_not_the_native_one(self):
        """A native ratio inflated by batch must not leak into the cost model."""
        theirs = _theirs_half(factor=6.0)
        for key in theirs["by_tokens"]:
            native = theirs["by_tokens"][key]["native_batch"]
            native["seconds_per_example"] *= 10.0   # a wildly different native figure
        op, tp = self._write(_ours_half(), theirs)
        receipt = cc.reduce_halves(op, tp)
        for key, row in receipt["projected_evaluation_cost"]["by_tokens"].items():
            ours_hours = row["our_evaluation_gpu_hours"]
            self.assertAlmostEqual(row["arm_pair_evaluation_gpu_hours"],
                                   ours_hours * 7.0, places=6)


if __name__ == "__main__":
    unittest.main()


class GateKeyCorrection(unittest.TestCase):
    """`(ev_run, ev_subrun, ev_gate)` is a GATE key on the data tree, not an event key.

    Agent A measured 212,677 repeating keys over 433,304 of 4,119,797 data rows, up to
    multiplicity 5, with ALL duplicate blocks differing in kinematics. These are
    distinct interactions sharing a DAQ gate. The fixtures below are that shape.
    """

    # one gate with three interactions, one with one, one with two
    GATE = np.array([[1, 2, 7], [1, 2, 7], [1, 2, 7], [1, 2, 8], [1, 2, 9], [1, 2, 9]])

    def test_the_bare_triple_collides_on_data_shaped_keys(self):
        report = ic.describe_keys(self.GATE, "data")
        self.assertEqual(report.duplicate_keys, 2)
        self.assertEqual(report.duplicated_row_count, 5)
        self.assertFalse(report.unique)

    def test_occurrence_is_the_ordinal_within_the_gate_in_row_order(self):
        np.testing.assert_array_equal(ic.assign_occurrence(self.GATE), [0, 1, 2, 0, 0, 1])

    def test_the_composite_key_is_unique_where_the_triple_is_not(self):
        composite = ic.with_occurrence(self.GATE)
        self.assertTrue(ic.describe_keys(composite, "join", ic.JOIN_FIELDS).unique)

    def test_joining_on_the_bare_triple_is_refused_not_silently_merged(self):
        """The failure this correction exists to prevent."""
        with self.assertRaises(ic.ContractViolation) as caught:
            ic.join_indices(self.GATE, self.GATE, fields=ic.KEY_FIELDS)
        self.assertIn("collide", str(caught.exception))

    def test_the_composite_join_is_a_bijection_on_gate_shaped_keys(self):
        composite = ic.with_occurrence(self.GATE)
        index, matched = ic.join_indices(composite, composite)
        self.assertTrue(matched.all())
        np.testing.assert_array_equal(index, np.arange(len(self.GATE)))

    def test_mc_shaped_keys_get_occurrence_zero_throughout(self):
        """All three MC trees have zero duplicates, so every ordinal is 0."""
        mc = np.array([[1, 2, i] for i in range(5)])
        np.testing.assert_array_equal(ic.assign_occurrence(mc), np.zeros(5, dtype=int))

    def test_the_join_key_defaults_to_the_composite(self):
        self.assertEqual(ic.JOIN_FIELDS, ic.KEY_FIELDS + ("occurrence",))

    def test_occurrence_carries_its_own_instability_warning(self):
        warning = ic.occurrence_stability_warning(ic.assign_occurrence(self.GATE))
        self.assertEqual(warning["rows_with_non_zero_occurrence"], 3)
        self.assertIn("re-reconstruction", warning["not_guaranteed"])

    def test_row_order_changes_the_ordinal_which_is_the_point_of_the_warning(self):
        """Reverse the production order and a given row gets a different ordinal.

        Permuting WITHIN a gate cannot show this -- those rows are identical in the
        key -- so the fixture reverses the whole inventory and maps the ordinals
        back to their original rows.
        """
        reversed_rows = self.GATE[::-1]
        mapped_back = ic.assign_occurrence(reversed_rows)[::-1]
        self.assertFalse(np.array_equal(ic.assign_occurrence(self.GATE), mapped_back))

    def test_the_measured_evidence_is_carried_in_the_module(self):
        evidence = ic.DATA_GATE_KEY_EVIDENCE
        self.assertEqual(evidence["duplicate_blocks_with_identical_kinematics"], 0)
        self.assertEqual(evidence["repeating_keys"], 212_677)
        self.assertIn("Do NOT", evidence["reading"])

    def test_the_canonical_key_carries_source_and_we_do_not_reimplement_the_join(self):
        """`source` is measured redundant on this inventory, not redundant in general."""
        self.assertEqual(ic.CANONICAL_JOIN_FIELDS,
                         ("source", "ev_run", "ev_subrun", "ev_gate", "occurrence"))
        self.assertIn("event_identity", ic.JOIN_INSTRUMENT["module"])
        self.assertIn("verify_event_identity_sidecar", ic.JOIN_INSTRUMENT["verifier"])
