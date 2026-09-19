"""Tests that the recorded schema is self-consistent with the frozen widths."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import frozen_design as fd
import theirs_token_schema as ts


class Widths(unittest.TestCase):
    def test_the_stored_token_loses_exactly_one_column_to_pid(self):
        self.assertEqual(len(ts.TOKEN_COLUMNS) - 1, ts.ENCODER_INPUT_DIM)
        self.assertEqual(ts.ENCODER_INPUT_DIM, fd.THEIRS_COMPLETE["input_dim"])

    def test_add_info_width_matches_the_freeze(self):
        self.assertEqual(len(ts.ADD_INFO_COLUMNS), fd.THEIRS_COMPLETE["add_dim"])

    def test_the_pid_column_is_where_his_loader_indexes_it(self):
        self.assertEqual(ts.TOKEN_COLUMNS[ts.TOKEN_PID_INDEX], "pid")
        self.assertEqual(ts.TOKEN_COLUMNS[ts.TOKEN_LOG_E_INDEX], "log_E")

    def test_the_energy_sum_pids_match_the_manifest(self):
        import r4_manifest as r4
        self.assertEqual(tuple(ts.ENERGY_SUM_PIDS), tuple(r4.ENERGY_SUM_PIDS))

    def test_every_category_declares_all_four_slots(self):
        for name, sources in ts.CATEGORY_SOURCES.items():
            with self.subTest(category=name):
                self.assertEqual(set(sources), {"four_momentum", "dEdx", "coords",
                                                "time"})

    def test_the_substituted_column_is_flagged_where_it_is_used(self):
        self.assertIn("SUBSTITUTED", ts.CATEGORY_SOURCES["prong"]["dEdx"])

    def test_overflow_aggregates_rather_than_truncates(self):
        self.assertIn("AGGREGATES", ts.OVERFLOW_POLICY)
        self.assertIn(6, ts.PID_CODES.values())
        self.assertIn(7, ts.PID_CODES.values())

    def test_what_is_not_yet_known_is_recorded(self):
        self.assertTrue(ts.UNRESOLVED)
        self.assertIn("max_blobs", " ".join(ts.UNRESOLVED))

    def test_the_category_order_is_his(self):
        self.assertEqual(ts.CATEGORY_ORDER, ("muon", "photon", "blob", "prong"))

    def test_muon_and_photon_codes_are_present(self):
        """The earlier reading had only the codes the energy-sum comment listed."""
        self.assertEqual(ts.PID_CODES["muon"], 0)
        self.assertEqual(ts.PID_CODES["photon"], 1)

    def test_the_energy_sort_drops_the_softest_not_the_last(self):
        self.assertIn("DESCENDING", ts.CAP_PATHS["max_objects_only"])
        self.assertIn("softest", ts.CAP_PATHS["max_objects_only"])

    def test_the_blob_momentum_is_constructed_not_copied(self):
        self.assertIn("unit(blob_xyz)", ts.BLOB_FOUR_MOMENTUM)
        self.assertIn("1e-6", ts.BLOB_FOUR_MOMENTUM)

    def test_the_prong_layout_matches_his_indexing(self):
        self.assertEqual(ts.PRONG_DENSE_LAYOUT["four_momentum"], (4, 8))
        self.assertEqual(ts.PRONG_DENSE_LAYOUT["pid"], 11)
