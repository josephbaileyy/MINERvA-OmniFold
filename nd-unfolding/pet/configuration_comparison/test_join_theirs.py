"""Tests for the identity join.

The load-bearing ones are the refusals: a positional fallback, a cross-stream
field mix, and a key packing that could merge two distinct events. Each of those
fails SILENTLY if unguarded, and each would corrupt every downstream row.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np

import join_theirs_to_inventory as jt


class Packing(unittest.TestCase):
    def test_distinct_events_pack_to_distinct_keys(self):
        a = np.array([[110000, 1, 2], [110000, 1, 3], [110000, 2, 2],
                      [110001, 1, 2]], dtype=np.int32)
        self.assertEqual(len(set(jt._pack(a).tolist())), 4)

    def test_a_value_that_would_overflow_is_refused(self):
        """Overflow would merge distinct events, which nothing downstream sees."""
        with self.assertRaises(ValueError):
            jt._pack(np.array([[1 << 21, 0, 0]], dtype=np.int64))

    def test_a_negative_field_is_refused(self):
        with self.assertRaises(ValueError):
            jt._pack(np.array([[-1, 0, 0]], dtype=np.int64))

    def test_the_wrong_field_count_is_refused(self):
        with self.assertRaises(ValueError):
            jt._pack(np.array([[1, 2]], dtype=np.int64))


class Join(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        # Built rows: a superset, deliberately out of inventory order.
        built = np.array([[7, 1, 3], [7, 1, 1], [7, 1, 9], [7, 1, 2]],
                         dtype=np.int32)
        np.savez(self.dir / "a.theirs.npz", identity=built,
                 tokens=np.zeros((4, 2, 5), dtype=np.float32))
        # Inventory: a subset, in its own order.
        self.inventory = np.array([[7, 1, 1], [7, 1, 2], [7, 1, 3]], dtype=np.int32)
        self.sidecar = self.dir / "side.npz"
        np.savez(self.sidecar, data_event_id=self.inventory,
                 data_identity_fields=np.array(["ev_run", "ev_subrun", "ev_gate"]))

    def test_it_matches_by_identity_not_by_position(self):
        result = jt.join(self.sidecar, "data", [self.dir])
        self.assertEqual(result["matched"], 3)
        self.assertEqual(result["unmatched"], 0)
        # Row order is the INVENTORY's; the built file was shuffled.
        index = result["row_index"]
        origin = result["origin"][index]
        self.assertEqual(list(origin[:, 1]), [1, 3, 0])

    def test_an_inventory_row_with_no_built_row_is_reported_not_invented(self):
        inventory = np.array([[7, 1, 1], [7, 1, 42]], dtype=np.int32)
        sidecar = self.dir / "side2.npz"
        np.savez(sidecar, data_event_id=inventory,
                 data_identity_fields=np.array(["ev_run", "ev_subrun", "ev_gate"]))
        result = jt.join(sidecar, "data", [self.dir])
        self.assertEqual(result["matched"], 1)
        self.assertEqual(result["unmatched"], 1)
        self.assertEqual(int(result["row_index"][1]), -1)

    def test_the_superset_does_not_leak_extra_rows(self):
        """Built row (7,1,9) is not in the inventory and must not appear."""
        result = jt.join(self.sidecar, "data", [self.dir])
        self.assertEqual(result["inventory_rows"], 3)
        self.assertEqual(result["built_rows"], 4)

    def test_a_sidecar_declaring_other_fields_is_refused(self):
        """Crossing streams' fields gives a clean zero, which looks like a bug."""
        sidecar = self.dir / "side3.npz"
        np.savez(sidecar, data_event_id=self.inventory,
                 data_identity_fields=np.array(["mc_run", "mc_subrun",
                                                "mc_nthEvtInFile"]))
        with self.assertRaises(SystemExit):
            jt.join(sidecar, "data", [self.dir])


if __name__ == "__main__":
    unittest.main()


class RecoCoverage(unittest.TestCase):
    """The gate must ask about the population that CAN be matched."""

    def test_a_row_without_reco_is_not_counted_against_coverage(self):
        matched = np.array([True, False, True, False])
        reco = np.array([True, False, True, False])
        out = jt.reco_coverage(matched, reco)
        self.assertEqual(out["pass_reco_rows"], 2)
        self.assertEqual(out["pass_reco_unmatched"], 0)
        self.assertEqual(out["pass_reco_fraction"], 1.0)
        self.assertEqual(out["unmatched_without_reco"], 2)

    def test_a_missing_pass_reco_row_is_still_a_failure(self):
        matched = np.array([True, False, True, True])
        reco = np.array([True, True, True, False])
        out = jt.reco_coverage(matched, reco)
        self.assertEqual(out["pass_reco_unmatched"], 1)
        self.assertLess(out["pass_reco_fraction"], 1.0)

    def test_matched_rows_without_reco_are_counted_and_reported(self):
        matched = np.array([True, True, True])
        reco = np.array([True, False, False])
        out = jt.reco_coverage(matched, reco)
        self.assertEqual(out["matched_without_reco"], 2)

    def test_the_observed_campaign_numbers_reproduce(self):
        """The real join: 59.5% of all rows, 100.0000% of pass_reco rows."""
        total, reco_true, matched_reco, matched_no_reco = (
            49_152_885, 20_573_521, 20_573_521, 8_679_708)
        reco = np.zeros(total, bool); reco[:reco_true] = True
        matched = np.zeros(total, bool)
        matched[:matched_reco] = True
        matched[reco_true:reco_true + matched_no_reco] = True
        out = jt.reco_coverage(matched, reco)
        self.assertEqual(out["pass_reco_fraction"], 1.0)
        self.assertEqual(out["unmatched_without_reco"], 19_899_656)
        self.assertAlmostEqual(matched.mean(), 0.59515, places=5)

    def test_a_length_disagreement_is_refused(self):
        with self.assertRaisesRegex(ValueError, "same inventory"):
            jt.reco_coverage(np.ones(4, bool), np.ones(3, bool))
