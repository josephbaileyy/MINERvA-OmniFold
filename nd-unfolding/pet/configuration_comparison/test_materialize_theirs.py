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
            tokens[:, :, 0] += np.arange(2)[:, None]      # row marker
            path = self.dir / f"s{shard}.npz"
            np.savez(path, tokens=tokens, add_info=add, globals=glob)
            self.files.append(str(path))
        # built row r -> shard r//2, row r%2
        self.origin = np.array([[s, r] for s in range(3) for r in range(2)],
                               dtype=np.int32)

    def test_it_returns_rows_in_inventory_order_not_shard_order(self):
        row_index = np.array([5, 0, 3])          # shard 2 row 1, shard 0 row 0, ...
        out = mt.materialize(self.files, row_index, self.origin,
                             np.array([0, 1, 2]), cap=CAP, packed_width=W)
        self.assertAlmostEqual(float(out["packed"][0, 0, 0]), 3.0)   # shard2 row1
        self.assertAlmostEqual(float(out["packed"][1, 0, 0]), 0.0)   # shard0 row0
        self.assertAlmostEqual(float(out["packed"][2, 0, 0]), 2.0)   # shard1 row1

    def test_tokens_and_add_info_are_concatenated_in_that_order(self):
        out = mt.materialize(self.files, np.array([0]), self.origin,
                             np.array([0]), cap=CAP, packed_width=W)
        np.testing.assert_allclose(out["packed"][0, 0, :5], 0.0)
        np.testing.assert_allclose(out["packed"][0, 0, 5:], 10.0)

    def test_each_shard_is_opened_at_most_once(self):
        row_index = np.arange(6)
        out = mt.materialize(self.files, row_index, self.origin, np.arange(6),
                             cap=CAP, packed_width=W)
        self.assertEqual(out["shards_opened"], 3)

    def test_a_shard_with_no_requested_rows_is_not_opened(self):
        out = mt.materialize(self.files, np.array([0, 1]), self.origin,
                             np.array([0, 1]), cap=CAP, packed_width=W)
        self.assertEqual(out["shards_opened"], 1)

    def test_an_unmatched_row_refuses(self):
        with self.assertRaises(ValueError):
            mt.materialize(self.files, np.array([-1]), self.origin,
                           np.array([0]), cap=CAP, packed_width=W)


if __name__ == "__main__":
    unittest.main()
