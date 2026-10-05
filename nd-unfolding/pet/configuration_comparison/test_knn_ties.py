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


class BoundaryStraddling(unittest.TestCase):
    """A tie matters only when it decides WHO is in the neighbour set."""

    @staticmethod
    def _cloud(positions):
        x = np.zeros((1, 12, 3), dtype=np.float32)
        x[0, :len(positions), 0] = 1.0
        x[0, :len(positions), 1] = positions
        return x[:, :, [1, 2]], x[:, :, 0] != 0

    def test_a_tie_at_the_kth_boundary_is_counted(self):
        """Distances 1, 2, 4, 4 from the centre: ranks 3 and 4 are equal."""
        coords, real = self._cloud([0.0, 1.0, 2.0, 4.0, -4.0])
        centres, events = ties._boundary_ties(coords, real, 3)
        self.assertEqual((centres, events), (1, 1))

    def test_the_same_tie_is_harmless_at_a_larger_k(self):
        """With k=10 every real token is selected, so ordering cannot matter."""
        coords, real = self._cloud([0.0, 1.0, 2.0, 4.0, -4.0])
        self.assertEqual(ties._boundary_ties(coords, real, 10), (0, 0))

    def test_no_boundary_exists_when_the_event_has_too_few_tokens(self):
        coords, real = self._cloud([0.0, 1.0, -1.0])
        self.assertEqual(ties._boundary_ties(coords, real, 3), (0, 0))

    def test_a_tie_wholly_inside_the_selected_set_is_not_counted(self):
        """Both tied tokens are selected; the block sums, so order cannot matter."""
        coords, real = self._cloud([0.0, 1.0, -1.0, 5.0, 6.0, 7.0])
        self.assertEqual(ties._boundary_ties(coords, real, 3)[0], 0)


class EquidistantWithoutCoordinateTie(unittest.TestCase):
    """The case the first census missed entirely."""

    def test_two_tokens_at_different_places_can_be_equidistant(self):
        x = np.zeros((1, 12, 3), dtype=np.float32)
        x[0, :5, 0] = 1.0
        x[0, :5, 1] = [0.0, 1.0, 2.0, 4.0, -4.0]
        coords, real = x[:, :, [1, 2]], x[:, :, 0] != 0
        # No two tokens share coordinates...
        self.assertEqual(int(_pairs(x)[0]), 0)
        # ...yet the k-th boundary is ambiguous, because +4 and -4 tie in DISTANCE.
        self.assertEqual(ties._boundary_ties(coords, real, 3), (1, 1))
