"""Tests for the on-demand gather."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np

import materialize_theirs as mt

CAP, W, G = 4, 10, 16


class Gather(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.files = []
        for shard in range(3):
            tokens = np.full((2, CAP, 5), shard, dtype=np.float32)
            add = np.full((2, CAP, 5), 10 + shard, dtype=np.float32)
            glob = np.full((2, G), 100 + shard, dtype=np.float32)
            # The marker lives in the PID slot -- packed column 4 -- because
            # the gather applies his feature transform and every other column
            # moves: 0..2 become eta/phi/log pT, 3 is log E, 5 is the
            # log-of-clipped dE/dx and 6..9 are divided by 10000. PID is the
            # categorical index and is carried through unchanged.
            tokens[:, :, 4] = shard * 10 + np.arange(2)[:, None]
            path = self.dir / f"s{shard}.npz"
            np.savez(path, tokens=tokens, add_info=add, globals=glob)
            self.files.append(str(path))
        # built row r -> shard r//2, row r%2
        self.origin = np.array([[s, r] for s in range(3) for r in range(2)],
                               dtype=np.int32)

    def test_it_returns_rows_in_inventory_order_not_shard_order(self):
        row_index = np.array([5, 0, 3])          # shard 2 row 1, shard 0 row 0, ...
        out = mt.materialize(self.files, row_index, self.origin,
                             np.array([0, 1, 2]), np.ones(3, bool),
                             cap=CAP, packed_width=W)
        self.assertAlmostEqual(float(out["packed"][0, 0, 4]), 21.0)  # shard2 row1
        self.assertAlmostEqual(float(out["packed"][1, 0, 4]), 0.0)   # shard0 row0
        self.assertAlmostEqual(float(out["packed"][2, 0, 4]), 11.0)  # shard1 row1

    def test_tokens_and_add_info_are_concatenated_in_that_order(self):
        out = mt.materialize(self.files, np.array([0]), self.origin,
                             np.array([0]), np.ones(1, bool),
                             cap=CAP, packed_width=W)
        # token columns 0..4 then add_info 5..9, in that order. The token
        # slots are shard 0's converted features; the add_info slots carry the
        # marker in dE/dx and shard 0's 10.0 in the scaled position columns.
        self.assertEqual(out["packed"].shape[-1], 10)
        # add_info's dE/dx slot carries his log(|x| + 0.1) of shard 0's 10.0,
        # and the position/time slots are the same 10.0 divided by 10000.
        self.assertAlmostEqual(float(out["packed"][0, 0, 5]),
                               float(np.log(10.1)), places=5)
        np.testing.assert_allclose(out["packed"][0, 0, 6:], 10.0 / 10000.0,
                                   rtol=0, atol=1e-9)

    def test_each_shard_is_opened_at_most_once(self):
        row_index = np.arange(6)
        out = mt.materialize(self.files, row_index, self.origin, np.arange(6),
                             np.ones(6, bool), cap=CAP, packed_width=W)
        self.assertEqual(out["shards_opened"], 3)

    def test_a_shard_with_no_requested_rows_is_not_opened(self):
        out = mt.materialize(self.files, np.array([0, 1]), self.origin,
                             np.array([0, 1]), np.ones(2, bool),
                             cap=CAP, packed_width=W)
        self.assertEqual(out["shards_opened"], 1)

    def test_an_unmatched_PASS_RECO_row_refuses(self):
        """That event his arm cannot see, and ours can."""
        with self.assertRaisesRegex(ValueError, "pass_reco"):
            mt.materialize(self.files, np.array([-1]), self.origin,
                           np.array([0]), np.ones(1, bool),
                           cap=CAP, packed_width=W)

    def test_an_unmatched_row_WITHOUT_reco_is_expected_and_comes_back_zero(self):
        """19.9M of the signal leg. Raising here killed the first tuning task.

        A reconstruction failure means no reconstructed object exists, so there
        is nothing to build a token from; the event enters through the truth
        leg. The earlier version raised on any -1.
        """
        out = mt.materialize(self.files, np.array([-1, 0]), self.origin,
                             np.array([0, 1]), np.array([False, True]),
                             cap=CAP, packed_width=W)
        np.testing.assert_array_equal(out["packed"][0],
                                      np.zeros((CAP, W), np.float32))
        self.assertTrue((out["packed"][1] != 0).any())
        self.assertEqual(out["unmatched_without_reco"], 1)

    def test_a_MATCHED_row_without_reco_also_comes_back_zero(self):
        """The production loader zeroes ours there; his arm must match."""
        out = mt.materialize(self.files, np.array([0, 2]), self.origin,
                             np.array([0, 1]), np.array([False, True]),
                             cap=CAP, packed_width=W)
        np.testing.assert_array_equal(out["packed"][0],
                                      np.zeros((CAP, W), np.float32))
        np.testing.assert_array_equal(out["globals"][0],
                                      np.zeros(G, np.float32))
        self.assertTrue((out["packed"][1] != 0).any())
        self.assertEqual(out["rows_without_reco"], 1)

    def test_pass_reco_must_cover_the_same_inventory(self):
        with self.assertRaisesRegex(ValueError, "same inventory"):
            mt.materialize(self.files, np.arange(4), self.origin,
                           np.array([0]), np.ones(3, bool),
                           cap=CAP, packed_width=W)

    def test_ordering_survives_unmatched_rows_interleaved(self):
        """The sort that skips -1 must not reorder the rows it does fill."""
        row_index = np.array([5, -1, 3, -1, 0])
        reco = np.array([True, False, True, False, True])
        out = mt.materialize(self.files, row_index, self.origin,
                             np.arange(5), reco, cap=CAP, packed_width=W)
        self.assertAlmostEqual(float(out["packed"][0, 0, 4]), 21.0)  # shard2 row1
        self.assertAlmostEqual(float(out["packed"][2, 0, 4]), 11.0)  # shard1 row1
        self.assertAlmostEqual(float(out["packed"][4, 0, 4]), 0.0)   # shard0 row0
        np.testing.assert_array_equal(out["packed"][1],
                                      np.zeros((CAP, W), np.float32))
        np.testing.assert_array_equal(out["packed"][3],
                                      np.zeros((CAP, W), np.float32))


if __name__ == "__main__":
    unittest.main()
