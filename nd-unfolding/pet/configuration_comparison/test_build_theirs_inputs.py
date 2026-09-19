"""Tests for his token construction.

The load-bearing ones are about what the CAP does. His code aggregates the
surplus into PID 6 and 7 rather than truncating, so energy is conserved across
the cap; a builder that dropped the tail would be a different model and no shape
check would see it.
"""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np

import build_theirs_inputs as bti
from theirs_token_schema import PID_CODES

MUON = {"four_momentum": [1.0, 2.0, 3.0, 10.0], "t": 0.5}


def blobs(n, energy=None):
    e = np.arange(1, n + 1, dtype=float) if energy is None else np.asarray(energy)
    return {"E": e, "x": np.full(n, 3.0), "y": np.full(n, 4.0),
            "z": np.zeros(n), "t": np.zeros(n)}


def prongs(n, pid=3):
    return {"E": np.tile([1.0, 0.0, 0.0, 5.0], (n, 1)),
            "pos": np.zeros((n, 4)), "pid": np.full(n, pid),
            "dedx": np.ones(n)}


class Shapes(unittest.TestCase):
    def test_blocks_are_capped_and_padded(self):
        t, a = bti.build_event(MUON, [], blobs(3), prongs(2))
        self.assertEqual(t.shape, (bti.CAP, bti.TOKEN_WIDTH))
        self.assertEqual(a.shape, (bti.CAP, bti.ADD_WIDTH))
        self.assertTrue(np.all(t[6:] == 0))          # 1 muon + 3 blobs + 2 prongs

    def test_the_muon_is_first_and_carries_pid_zero(self):
        t, _ = bti.build_event(MUON, [], blobs(1), prongs(1))
        self.assertEqual(t[0, 4], PID_CODES["muon"])

    def test_category_order_is_muon_photon_blob_prong(self):
        photon = {"four_momentum": [0.0, 0.0, 1.0, 2.0], "dedx": 7.0, "t": 1.0}
        t, _ = bti.build_event(MUON, [photon], blobs(1), prongs(1))
        self.assertEqual([t[i, 4] for i in range(4)],
                         [PID_CODES["muon"], PID_CODES["photon"],
                          PID_CODES["blob"], PID_CODES["prong_3"]])


class BlobMomentum(unittest.TestCase):
    def test_the_blob_momentum_is_constructed_not_copied(self):
        """unit(3,4,0) * E = (0.6E, 0.8E, 0) -- not the coordinates themselves."""
        t, _ = bti.build_event(None, [], blobs(1, energy=[10.0]), prongs(0))
        np.testing.assert_allclose(t[0, :3], [6.0, 8.0, 0.0], rtol=1e-5)

    def test_a_blob_at_the_origin_does_not_divide_by_zero(self):
        b = {"E": np.array([5.0]), "x": np.zeros(1), "y": np.zeros(1),
             "z": np.zeros(1), "t": np.zeros(1)}
        t, _ = bti.build_event(None, [], b, prongs(0))
        self.assertTrue(np.all(np.isfinite(t)))

    def test_the_blob_coordinates_go_to_the_auxiliary_block(self):
        _, a = bti.build_event(None, [], blobs(1, energy=[10.0]), prongs(0))
        np.testing.assert_allclose(a[0, 1:4], [3.0, 4.0, 0.0])
        self.assertEqual(a[0, 0], 0.0)               # blobs have no dE/dx


class Overflow(unittest.TestCase):
    def test_surplus_aggregates_rather_than_truncating(self):
        t, _ = bti.build_event(MUON, [], blobs(60), prongs(0))
        codes = t[:, 4]
        self.assertIn(PID_CODES["aggregate_blob"], codes)
        self.assertLessEqual(int((t[:, 3] != 0).sum()), bti.CAP)

    def test_the_aggregate_carries_the_tail_energy(self):
        """Energy must survive the cap; that is what PID 6 is for."""
        many = blobs(60, energy=np.full(60, 2.0))
        t, _ = bti.build_event(None, [], many, prongs(0))
        row = np.argmax(t[:, 4] == PID_CODES["aggregate_blob"])
        self.assertGreater(np.exp(t[row, 3]), 2.0)   # more than one blob's worth

    def test_nothing_exceeds_the_cap_even_with_both_categories_full(self):
        t, a = bti.build_event(MUON, [], blobs(80), prongs(40))
        self.assertEqual(t.shape[0], bti.CAP)
        self.assertEqual(a.shape[0], bti.CAP)

    def test_the_softest_overflow_not_the_last_listed(self):
        """He sorts by energy descending, so the hardest blobs are kept."""
        t, _ = bti.build_event(None, [], blobs(40), prongs(0))
        kept = np.exp(t[t[:, 4] == PID_CODES["blob"], 3])
        self.assertGreater(kept.min(), 1.5)          # the 1-energy blob overflowed


class Globals(unittest.TestCase):
    SOURCE = {"muon_fuzz_energy": 10.0, "muon_iso_blobs_energy": 5.0,
              "hadron_recoil": 100.0, "passive_id": 20000.0, "passive_od": 10000.0,
              "n_michel": 2, "muon_present": 1, "diphoton_mass": 135.0,
              "charged_pion_prongs": 1}

    def test_the_row_is_sixteen_wide(self):
        row = bti.globals_row(self.SOURCE, np.ones(6))
        self.assertEqual(row.shape, (bti.GLOBAL_WIDTH,))

    def test_the_passive_sum_is_id_plus_od(self):
        row = bti.globals_row(self.SOURCE, np.zeros(6))
        self.assertAlmostEqual(float(row[5]), float(np.log(2.0 + 1.0 + 1e-3)), places=5)

    def test_negatives_are_clipped_as_his_code_clips_them(self):
        source = dict(self.SOURCE, muon_fuzz_energy=-99.0, passive_id=-5.0)
        row = bti.globals_row(source, np.zeros(6))
        self.assertTrue(np.all(np.isfinite(row)))


if __name__ == "__main__":
    unittest.main()
