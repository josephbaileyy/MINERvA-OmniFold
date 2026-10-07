#!/usr/bin/env python3
"""Tests for the event-identity contract (`nd-unfolding/pet/event_identity.py`) and the parts of
the sidecar exporter that do not need PyROOT.

Every fail-closed check is tested IN THE DIRECTION IT ACTS: a guard gets both a case that must
make it fire and a case that must leave it silent. A guard exercised only on bad input is
indistinguishable from a guard that rejects everything.

Pure: no ROOT, no TensorFlow, no temporary files. Runs on a login node.
"""
import json
import os
import sys
import unittest

import numpy as np

_PET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pet")
if _PET not in sys.path:
    sys.path.insert(0, _PET)
import event_identity as eid  # noqa: E402


def _hash(*arrays):
    """Stand-in for `fullevent_fps_dataloader.inventory_order_hash` with the same contract:
    order- and content-sensitive over dtype, shape and bytes."""
    import hashlib
    h = hashlib.sha256()
    for a in arrays:
        a = np.ascontiguousarray(np.asarray(a))
        h.update(str(a.dtype).encode())
        h.update(repr(a.shape).encode())
        h.update(a.tobytes())
    return h.hexdigest()


class TestPacking(unittest.TestCase):
    def test_roundtrip_over_realistic_values(self):
        run = np.array([111353, 19168, 113000, 0])
        subrun = np.array([1, 40, 500, 0])
        event = np.array([0, 1499, 1233, 0])
        back = eid.unpack_identity(eid.pack_identity(run, subrun, event))
        for got, want in zip(back, (run, subrun, event)):
            np.testing.assert_array_equal(got, want)

    def test_distinct_inputs_give_distinct_keys(self):
        run, subrun, event = np.meshgrid(np.arange(3), np.arange(4), np.arange(5), indexing="ij")
        keys = eid.pack_identity(run.ravel(), subrun.ravel(), event.ravel())
        self.assertEqual(np.unique(keys).size, keys.size)

    def test_in_range_values_do_not_raise(self):
        """The silent direction: the range guard must not fire on values it must accept."""
        hi_run = (1 << eid.RUN_BITS) - 1
        hi_sub = (1 << eid.SUBRUN_BITS) - 1
        hi_evt = (1 << eid.EVENT_BITS) - 1
        eid.pack_identity([0, hi_run], [0, hi_sub], [0, hi_evt])

    def test_out_of_range_raises_per_component(self):
        for run, subrun, event in (((1 << eid.RUN_BITS), 0, 0),
                                   (0, (1 << eid.SUBRUN_BITS), 0),
                                   (0, 0, (1 << eid.EVENT_BITS))):
            with self.assertRaises(eid.IdentityRangeError):
                eid.pack_identity([run], [subrun], [event])

    def test_negative_raises(self):
        with self.assertRaises(eid.IdentityRangeError):
            eid.pack_identity([-1], [0], [0])

    def test_empty_input_is_not_a_range_violation(self):
        self.assertEqual(eid.pack_identity([], [], []).size, 0)


class TestCxxWrappedKey(unittest.TestCase):
    """The C++ `makeEventKey` is reproduced only as a measurement instrument. These tests pin the
    reproduction, and pin the overflow that is the reason the exported key is a different one."""

    def test_reproduces_the_formula_when_it_does_not_overflow(self):
        got = int(eid.cxx_wrapped_key([1], [2], [3])[0])
        self.assertEqual(got, (1 * 10**8 + 2) * 10**8 + 3)

    def test_realistic_run_number_overflows_uint64(self):
        run, subrun, event = 111353, 1, 0
        exact = (run * 10**8 + subrun) * 10**8 + event
        self.assertGreater(exact, 2**64 - 1)                 # the premise, not an assumption
        got = int(eid.cxx_wrapped_key([run], [subrun], [event])[0])
        self.assertEqual(got, exact % 2**64)
        self.assertNotEqual(got, exact)

    def test_the_exported_key_does_not_wrap_on_the_same_input(self):
        run, subrun, event = 111353, 1, 0
        key = eid.pack_identity([run], [subrun], [event])
        got_run, got_subrun, got_event = eid.unpack_identity(key)
        self.assertEqual((int(got_run[0]), int(got_subrun[0]), int(got_event[0])),
                         (run, subrun, event))


class TestOccurrenceIndex(unittest.TestCase):
    def test_zero_everywhere_when_keys_are_unique(self):
        keys = eid.pack_identity([1, 2, 3], [0, 0, 0], [0, 0, 0])
        np.testing.assert_array_equal(eid.occurrence_index(keys), [0, 0, 0])

    def test_ordinals_follow_entry_order_not_sorted_order(self):
        # key 7 appears at rows 0, 3, 4; its ordinals must be 0, 1, 2 in THAT order.
        keys = np.array([7, 5, 6, 7, 7], dtype=np.uint64)
        np.testing.assert_array_equal(eid.occurrence_index(keys), [0, 0, 0, 1, 2])

    def test_occurrences_are_counted_within_a_source(self):
        keys = np.array([7, 7, 7, 7], dtype=np.uint64)
        src = np.array([0, 1, 0, 1])
        np.testing.assert_array_equal(eid.occurrence_index(keys, src), [0, 0, 1, 1])

    def test_source_and_key_and_occurrence_is_unique_by_construction(self):
        rng = np.random.default_rng(0)
        keys = rng.integers(0, 5, size=500).astype(np.uint64)
        src = rng.integers(0, 3, size=500)
        occ = eid.occurrence_index(keys, src)
        triples = {(int(a), int(b), int(c)) for a, b, c in zip(src, keys, occ)}
        self.assertEqual(len(triples), keys.size)

    def test_computing_on_a_subset_gives_a_different_answer_than_subsetting(self):
        """The reason the exporter computes occurrence over the FULL tree.

        Row 0 is dropped by a selection. Computed on the full tree then subset, the surviving
        rows keep ordinals 1 and 2; computed on the subset they would be relabelled 0 and 1, so a
        row's identity would depend on the cut rather than on the event.
        """
        keys = np.array([9, 9, 9], dtype=np.uint64)
        keep = np.array([False, True, True])
        full_then_subset = eid.occurrence_index(keys)[keep]
        subset_then_compute = eid.occurrence_index(keys[keep])
        np.testing.assert_array_equal(full_then_subset, [1, 2])
        np.testing.assert_array_equal(subset_then_compute, [0, 1])
        self.assertFalse(np.array_equal(full_then_subset, subset_then_compute))

    def test_mismatched_source_length_raises(self):
        with self.assertRaises(ValueError):
            eid.occurrence_index(np.array([1, 2], dtype=np.uint64), [0])

    def test_empty(self):
        self.assertEqual(eid.occurrence_index(np.array([], dtype=np.uint64)).size, 0)


class TestUniquenessReport(unittest.TestCase):
    def test_rows_and_keys_are_counted_separately(self):
        keys = np.array([1, 1, 1, 2, 3], dtype=np.uint64)
        rep = eid.uniqueness_report(keys)
        self.assertEqual(rep["n_rows"], 5)
        self.assertEqual(rep["n_distinct"], 3)
        self.assertEqual(rep["n_duplicated_keys"], 1)       # one offending key
        self.assertEqual(rep["n_duplicated_rows"], 3)       # three offending rows
        self.assertEqual(rep["max_multiplicity"], 3)
        self.assertFalse(rep["is_unique"])

    def test_unique_input_reports_unique(self):
        rep = eid.uniqueness_report(np.array([1, 2, 3], dtype=np.uint64))
        self.assertTrue(rep["is_unique"])
        self.assertEqual(rep["n_duplicated_rows"], 0)
        self.assertEqual(rep["examples"], [])

    def test_qualifying_by_source_can_resolve_a_collision(self):
        keys = np.array([4, 4], dtype=np.uint64)
        self.assertFalse(eid.uniqueness_report(keys)["is_unique"])
        self.assertTrue(eid.uniqueness_report(keys, sources=[0, 1])["is_unique"])

    def test_examples_decode_back_to_components(self):
        keys = eid.pack_identity([11, 11], [22, 22], [33, 33])
        ex = eid.uniqueness_report(keys)["examples"][0]
        self.assertEqual((ex["run"], ex["subrun"], ex["event"]), (11, 22, 33))


class TestDuplicateCharacter(unittest.TestCase):
    """Identical duplicate rows and differing duplicate rows have OPPOSITE remedies, so the
    measurement must separate them."""

    def test_identical_rows_are_reported_as_identical(self):
        keys = np.array([1, 1, 2], dtype=np.uint64)
        witness = np.array([[5.0], [5.0], [9.0]])
        got = eid.duplicate_block_character(keys, witness)
        self.assertEqual(got["n_duplicated_keys"], 1)
        self.assertEqual(got["n_blocks_all_identical"], 1)
        self.assertEqual(got["n_blocks_with_difference"], 0)

    def test_differing_rows_are_reported_as_differing(self):
        keys = np.array([1, 1, 2], dtype=np.uint64)
        witness = np.array([[5.0], [6.0], [9.0]])
        got = eid.duplicate_block_character(keys, witness)
        self.assertEqual(got["n_blocks_all_identical"], 0)
        self.assertEqual(got["n_blocks_with_difference"], 1)

    def test_no_duplicates_reports_nothing(self):
        got = eid.duplicate_block_character(np.array([1, 2], dtype=np.uint64),
                                            np.array([[1.0], [2.0]]))
        self.assertEqual(got["n_duplicated_keys"], 0)

    def test_difference_in_any_column_counts(self):
        keys = np.array([1, 1], dtype=np.uint64)
        witness = np.array([[5.0, 1.0], [5.0, 2.0]])
        self.assertEqual(eid.duplicate_block_character(keys, witness)["n_blocks_with_difference"],
                         1)


class TestCrossSource(unittest.TestCase):
    def test_disjoint_sources(self):
        got = eid.cross_source_overlap({"1A": [1, 2], "1B": [3, 4]})
        self.assertTrue(got["disjoint"])
        self.assertEqual(got["pairs"], [])

    def test_overlapping_sources_are_named(self):
        got = eid.cross_source_overlap({"1A": [1, 2, 3], "1B": [3, 4], "1C": [9]})
        self.assertFalse(got["disjoint"])
        self.assertEqual(got["n_overlapping_pairs"], 1)
        self.assertEqual(got["pairs"][0], {"a": "1A", "b": "1B", "n_shared": 1})
        self.assertEqual(got["n_keys_in_more_than_one_source"], 1)

    def test_single_source_is_trivially_disjoint(self):
        self.assertTrue(eid.cross_source_overlap({"1A": [1, 1, 2]})["disjoint"])


class TestInventoryOverlap(unittest.TestCase):
    """Two inventories, two different expected answers: signal vs truth-denom should be the SAME
    set, background vs either should be DISJOINT. One function, both directions tested."""

    def test_equal_sets(self):
        got = eid.inventory_overlap([1, 2, 3], [3, 2, 1])
        self.assertTrue(got["sets_equal"])
        self.assertFalse(got["disjoint"])
        self.assertEqual((got["n_only_a"], got["n_only_b"]), (0, 0))

    def test_disjoint_sets(self):
        got = eid.inventory_overlap([1, 2], [3, 4])
        self.assertTrue(got["disjoint"])
        self.assertFalse(got["sets_equal"])
        self.assertEqual(got["n_shared"], 0)

    def test_partial_overlap_reports_both_sides(self):
        got = eid.inventory_overlap([1, 2, 3], [3, 4])
        self.assertEqual((got["n_shared"], got["n_only_a"], got["n_only_b"]), (1, 2, 1))
        self.assertFalse(got["sets_equal"])
        self.assertFalse(got["disjoint"])

    def test_equal_counts_do_not_imply_equal_sets(self):
        """The reason this is measured rather than inferred from the Phase-18.2 c-invariant."""
        got = eid.inventory_overlap([1, 2], [2, 3])
        self.assertEqual(got["n_a"], got["n_b"])
        self.assertFalse(got["sets_equal"])

    def test_duplicates_do_not_inflate_the_sets(self):
        got = eid.inventory_overlap([1, 1, 2], [1, 2, 2])
        self.assertTrue(got["sets_equal"])
        self.assertEqual(got["n_a"], 2)


class TestVerdict(unittest.TestCase):
    def test_truth_table(self):
        self.assertEqual(eid.verdict_from(True, True), eid.UNIQUE_WITHOUT_SOURCE)
        self.assertEqual(eid.verdict_from(True, False), eid.UNIQUE_WITH_SOURCE)
        self.assertEqual(eid.verdict_from(False, True), eid.NOT_UNIQUE)
        self.assertEqual(eid.verdict_from(False, False), eid.NOT_UNIQUE)

    def test_duplication_within_a_source_is_not_repaired_by_source(self):
        """Adding a column that is constant within the offending block cannot separate it."""
        self.assertEqual(eid.verdict_from(False, True), eid.NOT_UNIQUE)


class TestSourceBoundaries(unittest.TestCase):
    def test_row_to_source_follows_the_declared_order(self):
        np.testing.assert_array_equal(eid.source_index_from_boundaries([2, 0, 3]),
                                      [0, 0, 2, 2, 2])

    def test_check_boundaries_accepts_a_correct_sum(self):
        self.assertTrue(eid.check_boundaries([2, 3], 5))

    def test_check_boundaries_fires_on_a_wrong_sum(self):
        with self.assertRaises(ValueError):
            eid.check_boundaries([2, 3], 6)

    def test_negative_count_raises(self):
        with self.assertRaises(ValueError):
            eid.source_index_from_boundaries([2, -1])


def _good_block(n=4, prefix="sig", bound="deadbeef"):
    values = np.column_stack([np.full(n, 111353), np.arange(1, n + 1), np.arange(n)])
    source = np.zeros(n, np.int16)
    occ = np.zeros(n, np.int32)
    return eid.build_identity_block(prefix, values, source, occ, eid.MC_IDENTITY_FIELDS,
                                    bound, _hash)


class TestIdentityBlock(unittest.TestCase):
    def test_build_then_verify_passes(self):
        """The silent direction for every guard in `verify_identity_block` at once."""
        block = _good_block()
        self.assertTrue(eid.verify_identity_block("sig", block, 4, _hash,
                                                  bound_identity_hash="deadbeef"))

    def test_key_column_is_the_pack_of_the_value_columns(self):
        block = _good_block()
        k = eid.export_keys("sig")
        v = block[k["values"]]
        np.testing.assert_array_equal(block[k["key"]],
                                      eid.pack_identity(v[:, 0], v[:, 1], v[:, 2]))

    def test_data_field_set_is_accepted(self):
        values = np.column_stack([[19168], [2], [295]])
        block = eid.build_identity_block("data", values, [0], [0], eid.DATA_IDENTITY_FIELDS,
                                         "x", _hash)
        self.assertEqual(list(block[eid.export_keys("data")["fields"]]),
                         list(eid.DATA_IDENTITY_FIELDS))

    def test_unknown_field_set_raises(self):
        with self.assertRaises(ValueError):
            eid.build_identity_block("sig", np.zeros((1, 3), int), [0], [0],
                                     ("a", "b", "c"), "x", _hash)

    def test_wrong_value_shape_raises(self):
        with self.assertRaises(ValueError):
            eid.build_identity_block("sig", np.zeros((2, 4), int), [0, 0], [0, 0],
                                     eid.MC_IDENTITY_FIELDS, "x", _hash)

    def test_source_length_mismatch_raises(self):
        with self.assertRaises(ValueError):
            eid.build_identity_block("sig", np.zeros((2, 3), int), [0], [0, 0],
                                     eid.MC_IDENTITY_FIELDS, "x", _hash)

    def test_occurrence_length_mismatch_raises(self):
        with self.assertRaises(ValueError):
            eid.build_identity_block("sig", np.zeros((2, 3), int), [0, 0], [0],
                                     eid.MC_IDENTITY_FIELDS, "x", _hash)


class TestVerifyFiresOnEachDefect(unittest.TestCase):
    """Each check is given exactly the corruption it exists to catch."""

    def test_missing_key_fires(self):
        block = _good_block()
        del block[eid.export_keys("sig")["occurrence"]]
        with self.assertRaises(ValueError) as ctx:
            eid.verify_identity_block("sig", block, 4, _hash)
        self.assertIn("incomplete", str(ctx.exception))

    def test_row_count_disagreement_fires(self):
        with self.assertRaises(ValueError) as ctx:
            eid.verify_identity_block("sig", _good_block(4), 5, _hash)
        self.assertIn("row-aligned", str(ctx.exception))

    def test_tampered_key_column_fires(self):
        block = _good_block()
        block[eid.export_keys("sig")["key"]] = block[eid.export_keys("sig")["key"]].copy()
        block[eid.export_keys("sig")["key"]][0] += np.uint64(1)
        with self.assertRaises(ValueError) as ctx:
            eid.verify_identity_block("sig", block, 4, _hash)
        self.assertIn("packed key", str(ctx.exception))

    def test_reordered_rows_fire_the_digest(self):
        block = _good_block()
        k = eid.export_keys("sig")
        order = [1, 0, 2, 3]
        for name in (k["values"], k["source"], k["occurrence"], k["key"]):
            block[name] = np.asarray(block[name])[order]
        with self.assertRaises(ValueError) as ctx:
            eid.verify_identity_block("sig", block, 4, _hash)
        self.assertIn("digest", str(ctx.exception))

    def test_non_unique_identity_fires(self):
        n = 3
        values = np.column_stack([np.full(n, 5), np.full(n, 6), np.full(n, 7)])
        block = eid.build_identity_block("sig", values, np.zeros(n, np.int16),
                                         np.zeros(n, np.int32), eid.MC_IDENTITY_FIELDS,
                                         "x", _hash)
        with self.assertRaises(ValueError) as ctx:
            eid.verify_identity_block("sig", block, n, _hash)
        self.assertIn("not unique", str(ctx.exception))

    def test_correct_occurrences_make_the_same_rows_pass(self):
        """The paired silent direction for the uniqueness guard: the identical tuples above are
        accepted once `occurrence` distinguishes them, which is the whole point of the column."""
        n = 3
        values = np.column_stack([np.full(n, 5), np.full(n, 6), np.full(n, 7)])
        block = eid.build_identity_block("sig", values, np.zeros(n, np.int16),
                                         np.arange(n, dtype=np.int32), eid.MC_IDENTITY_FIELDS,
                                         "x", _hash)
        self.assertTrue(eid.verify_identity_block("sig", block, n, _hash))

    def test_wrong_bound_hash_fires(self):
        with self.assertRaises(ValueError) as ctx:
            eid.verify_identity_block("sig", _good_block(bound="aaaa"), 4, _hash,
                                      bound_identity_hash="bbbb")
        self.assertIn("different dumps", str(ctx.exception))

    def test_right_bound_hash_is_silent(self):
        self.assertTrue(eid.verify_identity_block("sig", _good_block(bound="aaaa"), 4, _hash,
                                                  bound_identity_hash="aaaa"))


class TestProductionSelectionIsPreserved(unittest.TestCase):
    """The exporter imports the retention predicate from `dump_pointcloud_inputs` rather than
    restating it. These tests hold the imported predicate to the two properties the identity
    export depends on, so a production change that breaks either one fails here first."""

    @classmethod
    def setUpClass(cls):
        import dump_pointcloud_inputs as dpi
        cls.dpi = dpi

    def test_native_miss_is_retained_and_flagged(self):
        keep, pass_reco, pass_truth = self.dpi.select_signal_row(
            sim=self.dpi.SENTINEL, sim_pz=self.dpi.SENTINEL, sim_pass=0, MC=1.2, MC_pz=4.0)
        self.assertTrue(keep, "a native miss must stay in the inventory")
        self.assertFalse(pass_reco)
        self.assertTrue(pass_truth)

    def test_out_of_domain_row_with_no_truth_is_dropped(self):
        keep, _, _ = self.dpi.select_signal_row(sim=1e6, sim_pz=1e6, sim_pass=1,
                                                MC=-9999.0, MC_pz=-9999.0)
        self.assertFalse(keep)

    def test_ordinary_matched_row_is_retained(self):
        keep, pass_reco, pass_truth = self.dpi.select_signal_row(
            sim=1.0, sim_pz=4.0, sim_pass=1, MC=1.1, MC_pz=4.1)
        self.assertTrue(keep and pass_reco and pass_truth)

    def test_exporter_imports_resolve_to_this_checkout(self):
        """The OI-136 guard, exercised on the happy path: a hardcoded `sys.path[0]` in the
        production dumper must not have made these names come from another tree."""
        import export_event_identity as exp
        self.assertEqual(os.path.dirname(os.path.abspath(self.dpi.__file__)),
                         os.path.dirname(os.path.abspath(exp.__file__)))

    def test_identity_is_carried_for_every_retained_row_including_misses(self):
        """End-to-end over the pure path: full-tree identity + production selection + occurrence
        computed before subsetting produces a verifiable, miss-preserving block."""
        rows = [
            (1.0, 4.0, 1, 1.1, 4.1),                                      # matched
            (self.dpi.SENTINEL, self.dpi.SENTINEL, 0, 1.2, 4.2),          # native miss
            (1e6, 1e6, 1, -9999.0, -9999.0),                              # dropped
            (2.0, 5.0, 1, 2.1, 5.1),                                      # matched
        ]
        keep = np.array([self.dpi.select_signal_row(*r)[0] for r in rows])
        self.assertEqual(keep.tolist(), [True, True, False, True])
        values = np.column_stack([np.full(4, 111353), np.full(4, 7), np.arange(4)])
        src = np.zeros(4, np.int16)
        occ = eid.occurrence_index(eid.pack_identity(values[:, 0], values[:, 1], values[:, 2]),
                                   src)
        block = eid.build_identity_block("sig", values[keep], src[keep], occ[keep],
                                         eid.MC_IDENTITY_FIELDS, "bound", _hash)
        self.assertTrue(eid.verify_identity_block("sig", block, 3, _hash,
                                                  bound_identity_hash="bound"))
        # The miss row's own identity survived, unchanged, at its inventory position.
        np.testing.assert_array_equal(block[eid.export_keys("sig")["values"]][1], [111353, 7, 1])


class TestExporterPureParts(unittest.TestCase):
    def test_rederived_hashes_match_the_dump_formulas(self):
        """`rederive_order_hashes` must reproduce exactly what `finalize_g2_arrays` stores;
        otherwise the exporter's binding check would reject every correct sidecar."""
        import export_event_identity as exp
        sig = {"w_truth": np.array([1.5, 2.5], np.float32),
               "pass_truth": np.array([True, False])}
        bkg = {"w_bkg": np.array([0.25, 0.5, 0.75], np.float32)}
        got = exp.rederive_order_hashes(_hash, sig, bkg)
        self.assertEqual(got["sig_identity_hash"],
                         _hash(sig["w_truth"], sig["pass_truth"]))
        self.assertEqual(got["bkg_identity_hash"],
                         _hash(bkg["w_bkg"], np.arange(3, dtype=np.int64)))

    def test_rederived_hash_changes_when_a_row_moves(self):
        import export_event_identity as exp
        a = exp.rederive_order_hashes(_hash,
                                      {"w_truth": np.array([1.0, 2.0], np.float32),
                                       "pass_truth": np.array([True, False])},
                                      {"w_bkg": np.array([1.0], np.float32)})
        b = exp.rederive_order_hashes(_hash,
                                      {"w_truth": np.array([2.0, 1.0], np.float32),
                                       "pass_truth": np.array([False, True])},
                                      {"w_bkg": np.array([1.0], np.float32)})
        self.assertNotEqual(a["sig_identity_hash"], b["sig_identity_hash"])

    def test_inventory_tree_map_covers_every_exported_prefix(self):
        import export_event_identity as exp
        self.assertEqual(set(exp.INVENTORIES), set(eid.INVENTORY_TREE))
        for tree in eid.INVENTORY_TREE.values():
            self.assertIn(tree, eid.TREE_IDENTITY_FIELDS)

    def test_verdict_strings_are_json_round_trippable(self):
        payload = json.dumps({t: eid.UNIQUE_WITH_SOURCE for t in eid.TREE_IDENTITY_FIELDS})
        self.assertEqual(set(json.loads(payload).values()), {eid.UNIQUE_WITH_SOURCE})
        for v in eid.VERDICTS:
            self.assertIsInstance(v, str)


if __name__ == "__main__":
    unittest.main(verbosity=2)
