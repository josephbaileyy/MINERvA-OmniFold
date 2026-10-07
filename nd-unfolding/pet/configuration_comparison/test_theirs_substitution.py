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
        packed, glob = sub.gather(blocks, index, np.array([0, 1]),
                                  np.ones(4, bool))
        np.testing.assert_array_equal(packed[0], blocks["packed"][3])
        np.testing.assert_array_equal(glob[1], blocks["globals"][1])

    def test_an_unmatched_pass_reco_row_raises_rather_than_zero_filling(self):
        """A zero-filled event would be scored as a failure of his arm."""
        blocks = theirs(4)
        index = np.array([0, -1, 2, 3])
        with self.assertRaises(sub.UnmatchedRows):
            sub.gather(blocks, index, np.array([0, 1, 2]), np.ones(4, bool))

    def test_an_unmatched_row_WITHOUT_reco_is_expected_and_zeroed(self):
        """No reco means no reconstructed object, so no token can exist.

        These events live only in the AnaTuple's Truth tree. Demanding a built
        input for them was a gate on the wrong population -- it reported 59.5%
        for a join covering 100% of what it can cover.
        """
        blocks = theirs(4)
        index = np.array([0, -1, 2, 3])
        reco = np.array([True, False, True, True])
        packed, glob = sub.gather(blocks, index, np.array([0, 1, 2]), reco)
        np.testing.assert_array_equal(packed[1], np.zeros_like(packed[1]))
        np.testing.assert_array_equal(glob[1], np.zeros_like(glob[1]))
        self.assertTrue((packed[0] != 0).any())

    def test_a_MATCHED_row_without_reco_is_also_zeroed(self):
        """The 8.68M matched-but-!pass_reco rows are the ones that matter.

        The production loader zeroes its reco block there. His arm keeping real
        reco content on 18% of the signal leg would see information ours does
        not, and that difference would read as a method effect.
        """
        blocks = theirs(4)
        index = np.array([0, 1, 2, 3])
        reco = np.array([True, False, True, False])
        packed, glob = sub.gather(blocks, index, np.arange(4), reco)
        self.assertTrue((packed[[1, 3]] == 0).all())
        self.assertTrue((packed[[0, 2]] != 0).all())
        self.assertTrue((glob[[1, 3]] == 0).all())

    def test_gather_does_not_mutate_the_source_blocks(self):
        blocks = theirs(3)
        before = blocks["packed"].copy()
        sub.gather(blocks, np.arange(3), np.arange(3),
                   np.array([True, False, True]))
        np.testing.assert_array_equal(blocks["packed"], before)

    def test_pass_reco_must_cover_the_same_inventory_as_the_index(self):
        """A short pass_reco would mis-assign the flag without raising."""
        with self.assertRaisesRegex(ValueError, "same inventory"):
            sub.gather(theirs(4), np.arange(4), np.arange(3), np.ones(3, bool))


class ZeroNonReco(unittest.TestCase):
    def test_it_zeroes_exactly_the_non_reco_rows(self):
        packed = np.ones((4, 33, 10), np.float32)
        glob = np.ones((4, 16), np.float32)
        reco = np.array([True, False, True, False])
        p2, g2 = sub.zero_non_reco(packed, glob, reco)
        self.assertTrue((p2[[1, 3]] == 0).all() and (p2[[0, 2]] == 1).all())
        self.assertTrue((g2[[1, 3]] == 0).all() and (g2[[0, 2]] == 1).all())

    def test_a_length_disagreement_is_refused(self):
        with self.assertRaisesRegex(ValueError, "same events"):
            sub.zero_non_reco(np.ones((4, 2, 2)), np.ones((4, 3)),
                              np.ones(3, bool))


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
