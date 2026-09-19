"""Tests for the real-input k-NN tie census.

The load-bearing ones are that a tie between REAL tokens is counted and a tie
between PADDED tokens is not. Padded slots sit at the same place by construction,
so an instrument that counted them would report ties on every event and say
nothing.
"""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np

import census_knn_ties as ties


def _keys(x, coords=(1, 2), mask=0):
    real = x[:, :, mask] != 0
    return ties._keys(x[:, :, list(coords)], real, 0)


def _pairs(x, **kw):
    key = _keys(x, **kw)
    ordered = np.sort(key, axis=1)
    return (ordered[:, 1:] == ordered[:, :-1]).sum(axis=1)


class Census(unittest.TestCase):
    def _event(self, energies, coords):
        x = np.zeros((1, len(energies), 3), dtype=np.float32)
        x[0, :, 0] = energies
        x[0, :, 1:] = coords
        return x

    def test_two_real_tokens_at_the_same_place_are_one_tie(self):
        x = self._event([1, 1, 0], [[5.0, 7.0], [5.0, 7.0], [0.0, 0.0]])
        self.assertEqual(int(_pairs(x)[0]), 1)

    def test_padded_tokens_sharing_a_place_are_NOT_a_tie(self):
        """They always do, so counting them would report ties on every event."""
        x = self._event([1, 0, 0, 0], [[5.0, 7.0], [0.0, 0.0], [0.0, 0.0],
                                       [0.0, 0.0]])
        self.assertEqual(int(_pairs(x)[0]), 0)

    def test_a_padded_token_does_not_tie_with_a_real_one_at_the_same_place(self):
        x = self._event([1, 0], [[0.0, 0.0], [0.0, 0.0]])
        self.assertEqual(int(_pairs(x)[0]), 0)

    def test_negative_zero_ties_with_positive_zero(self):
        """They are the same PLACE, and differ only in bits."""
        x = self._event([1, 1], [[0.0, -0.0], [0.0, 0.0]])
        self.assertEqual(int(_pairs(x)[0]), 1)

    def test_distinct_coordinates_are_not_a_tie(self):
        x = self._event([1, 1], [[5.0, 7.0], [5.0, 8.0]])
        self.assertEqual(int(_pairs(x)[0]), 0)

    def test_three_tokens_at_one_place_are_two_adjacent_pairs(self):
        x = self._event([1, 1, 1], [[2.0, 2.0]] * 3)
        self.assertEqual(int(_pairs(x)[0]), 2)

    def test_the_coordinate_columns_are_honoured(self):
        """Ties in columns we do NOT use as coordinates must not count."""
        x = np.zeros((1, 2, 4), dtype=np.float32)
        x[0, :, 0] = [1, 1]
        x[0, 0, 1:] = [5.0, 7.0, 1.0]
        x[0, 1, 1:] = [5.0, 9.0, 1.0]        # differs in column 2, ties in 3
        self.assertEqual(int(_pairs(x, coords=(1, 2))[0]), 0)
        self.assertEqual(int(_pairs(x, coords=(1, 3))[0]), 1)


if __name__ == "__main__":
    unittest.main()
