"""Tests for substituting his step-1 inputs into the production loaders."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np

import theirs_loader_substitution as sub


class FakeLoader:
    def __init__(self, rows, cloud_width=5, evt_width=13):
        self.reco = np.zeros((rows, 12, cloud_width), dtype=np.float32)
        self.reco_evt = np.zeros((rows, evt_width), dtype=np.float32)
        self.gen = np.arange(rows * 3, dtype=np.float32).reshape(rows, 3)
        self.weight = np.full(rows, 0.5, dtype=np.float32)
        self.pass_reco = np.ones(rows, dtype=bool)


def theirs(rows):
    return {"packed": np.ones((rows, 33, 10), dtype=np.float32),
            "globals": np.full((rows, 16), 2.0, dtype=np.float32)}


class Gather(unittest.TestCase):
    def test_it_gathers_by_the_row_index_not_by_position(self):
        blocks = {"packed": np.arange(4 * 33 * 10, dtype=np.float32
                                      ).reshape(4, 33, 10),
                  "globals": np.arange(4 * 16, dtype=np.float32).reshape(4, 16)}
        index = np.array([3, 1, 0, 2])
        packed, glob = sub.gather(blocks, index, np.array([0, 1]))
        np.testing.assert_array_equal(packed[0], blocks["packed"][3])
        np.testing.assert_array_equal(glob[1], blocks["globals"][1])

    def test_an_unmatched_row_raises_rather_than_zero_filling(self):
        """A zero-filled event would be scored as a failure of his arm."""
        blocks = theirs(4)
        index = np.array([0, -1, 2, 3])
        with self.assertRaises(sub.UnmatchedRows):
            sub.gather(blocks, index, np.array([0, 1, 2]))


class Substitution(unittest.TestCase):
    def test_only_step1_reco_changes(self):
        data, mc = FakeLoader(5), FakeLoader(7)
        report = sub.substitute_step1(data, mc,
                                      (theirs(5)["packed"], theirs(5)["globals"]),
                                      (theirs(7)["packed"], theirs(7)["globals"]))
        self.assertEqual(report["substituted"], ["reco", "reco_evt"])
        self.assertTrue(report["step2_untouched"])
        self.assertEqual(data.reco.shape, (5, 33, 10))
        self.assertEqual(mc.reco_evt.shape, (7, 16))

    def test_the_truth_side_is_byte_identical_afterwards(self):
        mc = FakeLoader(7)
        gen_before = mc.gen.copy()
        sub.substitute_step1(FakeLoader(5), mc,
                             (theirs(5)["packed"], theirs(5)["globals"]),
                             (theirs(7)["packed"], theirs(7)["globals"]))
        np.testing.assert_array_equal(mc.gen, gen_before)

    def test_weights_and_flags_survive(self):
        mc = FakeLoader(7)
        w, p = mc.weight.copy(), mc.pass_reco.copy()
        sub.substitute_step1(FakeLoader(5), mc,
                             (theirs(5)["packed"], theirs(5)["globals"]),
                             (theirs(7)["packed"], theirs(7)["globals"]))
        np.testing.assert_array_equal(mc.weight, w)
        np.testing.assert_array_equal(mc.pass_reco, p)

    def test_a_row_count_change_is_refused(self):
        """Different populations would make the difference look like a method."""
        with self.assertRaises(ValueError):
            sub.substitute_step1(FakeLoader(5), FakeLoader(7),
                                 (theirs(4)["packed"], theirs(4)["globals"]),
                                 (theirs(7)["packed"], theirs(7)["globals"]))


if __name__ == "__main__":
    unittest.main()
