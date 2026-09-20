"""Tests that the recorded schema is self-consistent with the frozen widths."""

from __future__ import annotations

import os
import unittest

import numpy as np

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


class HisFeaturesNotTheIntermediate(unittest.TestCase):
    """The model sees eta/phi/log pT, not the stored four-momentum.

    `preprocessing.py:239-288` converts and line 287 stacks exactly those four;
    `preprocessing.py:343-344` divides positions by 10000. The build stores the
    pre-conversion form, and feeding THAT to the model is not his
    configuration. Measured, job 58602446: raw momenta reach 8.2e4, the first
    step-1 fit returned `Last val loss nan`, and the engine's reweight gate
    refused 10,000 non-finite logits.
    """

    def test_the_conversion_matches_his_function_on_the_same_momenta(self):
        rng = np.random.default_rng(0)
        fm = rng.normal(0.0, 5.0, (40, 3))
        energy = rng.gamma(2.0, 3.0, 40) + 0.01
        packed = np.zeros((1, 40, 10))
        packed[0, :, :3] = fm
        packed[0, :, 3] = np.log(energy + 1e-6)
        packed[0, :, 4] = 2
        packed[0, :, 5:] = 1.0                      # keep rows non-zero
        got = ts.convert_packed(packed)[0, :, :4]
        want = ts.convert_to_eta_phi_pt(
            np.column_stack([fm, energy]))
        np.testing.assert_allclose(got[:, :3], want[:, :3], rtol=0, atol=1e-12)
        np.testing.assert_allclose(got[:, 3], want[:, 3], rtol=0, atol=1e-12)

    def test_positions_and_time_are_divided_by_ten_thousand(self):
        packed = np.zeros((1, 1, 10))
        packed[0, 0] = [1, 1, 1, 0.0, 2, 0.7, 10000.0, 5000.0, -2500.0, 400.0]
        out = ts.convert_packed(packed)
        np.testing.assert_allclose(out[0, 0, 6:10], [1.0, 0.5, -0.25, 0.04])
        # dE/dx is not DIVIDED, but it does get his own transform.
        self.assertAlmostEqual(out[0, 0, 5], float(np.log(0.8)))

    def test_zero_padding_stays_exactly_zero(self):
        """Converting a pad gives [0,0,-13.8,-13.8,0] and the mask reads
        `log E != 0`, so every pad would become a token."""
        packed = np.zeros((2, 3, 10))
        packed[0, 0] = [1, 1, 1, 2.0, 2, 0, 0, 0, 0, 0]
        out = ts.convert_packed(packed)
        self.assertTrue((out[0, 1:] == 0).all())
        self.assertTrue((out[1] == 0).all())
        self.assertFalse((out[0, 0] == 0).all())

    def test_eta_is_clipped_and_degenerate_momenta_give_zero(self):
        packed = np.zeros((1, 2, 10))
        packed[0, 0] = [0, 0, 5.0, 1.0, 2, 1, 0, 0, 0, 0]   # p == pz
        packed[0, 1] = [0, 0, 0, 1.0, 2, 1, 0, 0, 0, 0]     # p == 0
        out = ts.convert_packed(packed)
        self.assertEqual(out[0, 0, 0], 0.0)
        self.assertEqual(out[0, 1, 0], 0.0)
        self.assertTrue(np.isfinite(out).all())

    def test_the_schema_records_the_corrected_columns(self):
        self.assertEqual(ts.TOKEN_COLUMNS,
                         ("delta_eta", "delta_phi", "log_pt", "log_E", "pid"))
        self.assertEqual(ts.COORD_DIVISOR, 10000.0)
        self.assertIn("x_over_1e4", ts.ADD_INFO_COLUMNS)

    def test_the_gather_applies_it(self):
        from pathlib import Path
        import materialize_theirs as mt
        source = Path(mt.__file__).read_text()
        self.assertIn("tts.convert_packed(packed)", source)


class DedxSentinel(unittest.TestCase):
    """`preprocessing.py:827-832`. MINERvA writes -999 for "no dE/dx"."""

    def test_the_sentinel_becomes_zero_before_the_log(self):
        self.assertAlmostEqual(float(ts.preprocess_dedx(np.array([-999.0]))[0]),
                               float(np.log(0.1)))

    def test_infinities_and_large_values_clip_to_one_hundred(self):
        got = ts.preprocess_dedx(np.array([np.inf, -np.inf, 150.0, 100.0]))
        np.testing.assert_allclose(got, np.log(100.1), rtol=0, atol=1e-12)

    def test_it_takes_the_absolute_value(self):
        self.assertAlmostEqual(float(ts.preprocess_dedx(np.array([-3.0]))[0]),
                               float(np.log(3.1)))

    def test_convert_packed_applies_it_to_the_dedx_column(self):
        packed = np.zeros((1, 2, 10))
        packed[0, 0] = [1, 1, 1, 2.0, 3, -999.0, 0, 0, 0, 0]
        packed[0, 1] = [1, 1, 1, 2.0, 3, 2.5, 0, 0, 0, 0]
        out = ts.convert_packed(packed)
        self.assertAlmostEqual(float(out[0, 0, 5]), float(np.log(0.1)))
        self.assertAlmostEqual(float(out[0, 1, 5]), float(np.log(2.6)))

    def test_the_raw_sentinel_would_dominate_the_feature(self):
        """Why it matters: measured mean -134, std 341 on the prior leg."""
        raw = np.array([-999.0] * 60 + [2.0] * 40)
        self.assertLess(raw.mean(), -100.0)
        self.assertGreater(ts.preprocess_dedx(raw).std(), 0.0)
        self.assertLess(abs(ts.preprocess_dedx(raw).mean()), 5.0)
