"""Login-safe contract tests for the opt-in PET2-family backend."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ND not in sys.path:
    sys.path.insert(0, ND)

from pet2_torch.checkpoints import arm_f_eligibility, current_arm_f_outcome
from pet2_torch.aggregate_pilots import _comparison
from pet2_torch.contracts import PAD_CATEGORY, TokenBatch
from pet2_torch.density_ratio import (
    balanced_weighted_bce_numpy,
    calibrated_ratio,
)
from pet2_torch.features import (
    TYPE_GENERIC,
    TYPE_OVERFLOW,
    build_arm_manifest,
    exact_arm_diff,
    materialize_feature_view,
)
from pet2_torch.fixtures import (
    analytic_gaussian_problem,
    make_known_ratio_closure_dataset,
    make_synthetic_dataset,
    truncate_with_overflow,
)
import pet2_torch.g2_adapter as g2_adapter
from pet2_torch.g2_adapter import load_publication_g2, preflight_g2_mini_packet
from pet2_torch.engine import OneIterationConfig, resolve_pot_scale
from pet2_torch.evaluation import conditional_closure_metrics
from pet2_torch.preprocessing import fit_preprocessor, preprocessor_from_payload
from pet2_torch.public_gregor import (
    PUBLIC_REVISION,
    adapt_loaded_public_mapping,
    inspect_local_public_artifact,
    inspect_trusted_public_pb,
)
from pet2_torch.ratio_conventions import fixed_ratio_convention_fixture
from pet2_torch.utils import file_sha256, stable_partition, stable_split
from pet2_torch.xps2_adapter import inspect_xps2_packet, open_xps2_memmap
from pet2_torch.xps2_pilot import build_xps2_recoil_dataset


class ThreeInventoryContract(unittest.TestCase):
    def setUp(self):
        self.dataset, self.capabilities = make_synthetic_dataset(
            n_signal=80, n_data=48, n_background=16, seed=7
        )

    def test_data_mc_background_detector_schema_symmetry(self):
        signal = self.dataset.signal.reco
        data = self.dataset.measured.data
        background = self.dataset.measured.background
        self.assertEqual(signal.continuous.shape[1:], data.continuous.shape[1:])
        self.assertEqual(signal.continuous.shape[1:], background.continuous.shape[1:])
        self.assertEqual(signal.coords.shape[1:], data.coords.shape[1:])
        self.assertEqual(signal.global_names, data.global_names)
        self.assertEqual(signal.global_names, background.global_names)

    def test_truth_leakage_fields_absent_from_step1_schema(self):
        reco = self.dataset.signal.reco
        forbidden = {"pdg", "truth", "generator", "inttype", "current", "signal_label"}
        for name in reco.global_names:
            self.assertFalse(any(word in name.lower() for word in forbidden))
        self.assertNotIn("source_kind", reco.global_names)
        self.assertNotIn("source_kind", self.dataset.measured.data.global_names)

    def test_literal_background_order_and_signed_provenance(self):
        measured = self.dataset.measured
        literal = measured.literal_target()
        self.assertEqual(
            literal.n_rows, measured.data.n_rows + measured.background.n_rows
        )
        np.testing.assert_allclose(
            literal.continuous[: measured.data.n_rows], measured.data.continuous
        )
        np.testing.assert_allclose(
            literal.continuous[measured.data.n_rows :], measured.background.continuous
        )
        self.assertTrue(np.all(measured.raw_signed_weights[: measured.data.n_rows] >= 0))
        self.assertTrue(np.all(measured.raw_signed_weights[measured.data.n_rows :] <= 0))
        self.assertTrue(np.all(measured.refined_weights >= 0))

    def test_native_misses_are_masked_but_truth_present(self):
        signal = self.dataset.signal
        misses = signal.pass_truth & ~signal.pass_reco
        self.assertGreater(int(misses.sum()), 0)
        self.assertFalse(np.any(signal.reco.token_mask[misses]))
        self.assertTrue(np.all(signal.reco.type_id[misses] == PAD_CATEGORY))
        self.assertTrue(np.any(signal.truth.token_mask[misses]))
        self.assertTrue(np.all(signal.reco.muon_present[misses] == 0))

    def test_separate_reco_truth_weights_are_not_collapsed(self):
        self.assertFalse(
            np.array_equal(self.dataset.signal.w_reco, self.dataset.signal.w_truth)
        )

    def test_signal_fake_population_fails_closed(self):
        signal = self.dataset.signal
        pass_reco = signal.pass_reco.copy()
        row = int(np.flatnonzero(~signal.pass_truth)[0])
        pass_reco[row] = True
        with self.assertRaisesRegex(ValueError, "fakes"):
            replace(signal, pass_reco=pass_reco).validated()

    def test_deterministic_full_row_alignment(self):
        rows = self.dataset.signal.reco.row_index
        np.testing.assert_array_equal(rows, np.arange(len(rows)))
        np.testing.assert_array_equal(rows, self.dataset.signal.truth.row_index)


class MaskTypeAndFailureContract(unittest.TestCase):
    def setUp(self):
        self.dataset, self.capabilities = make_synthetic_dataset(
            n_signal=64, n_data=40, n_background=12, seed=12
        )

    def test_category_zero_is_never_a_real_type(self):
        batch = self.dataset.signal.truth
        self.assertTrue(np.all(batch.type_id[batch.token_mask] >= 1))
        self.assertTrue(np.all(batch.type_id[~batch.token_mask] == 0))

    def test_explicit_mask_not_energy(self):
        batch = self.dataset.signal.truth
        continuous = batch.continuous.copy()
        location = np.argwhere(batch.token_mask)[0]
        continuous[tuple(location) + (0,)] = 0.0
        modified = replace(batch, continuous=continuous).validated()
        self.assertTrue(modified.token_mask[tuple(location)])

    def test_nan_real_token_fails(self):
        batch = self.dataset.signal.truth
        continuous = batch.continuous.copy()
        location = np.argwhere(batch.token_mask)[0]
        continuous[tuple(location) + (0,)] = np.nan
        with self.assertRaisesRegex(ValueError, "NaN"):
            replace(batch, continuous=continuous).validated()

    def test_oov_type_fails(self):
        batch = self.dataset.signal.truth
        type_id = batch.type_id.copy()
        location = tuple(np.argwhere(batch.token_mask)[0])
        type_id[location] = 99
        with self.assertRaisesRegex(ValueError, "vocabulary"):
            replace(batch, type_id=type_id).validated(max_type=15)

    def test_real_type_zero_fails(self):
        batch = self.dataset.signal.truth
        type_id = batch.type_id.copy()
        location = tuple(np.argwhere(batch.token_mask)[0])
        type_id[location] = 0
        with self.assertRaisesRegex(ValueError, "real tokens"):
            replace(batch, type_id=type_id).validated()

    def test_malformed_shape_fails(self):
        batch = self.dataset.signal.truth
        with self.assertRaisesRegex(ValueError, "coords"):
            replace(batch, coords=batch.coords[:, :-1]).validated()

    def test_muon_missing_is_zero_masked_not_sentinel(self):
        batch = self.dataset.signal.reco
        missing = ~batch.muon_present
        self.assertGreater(int(missing.sum()), 0)
        self.assertTrue(np.all(batch.muon_continuous[missing] == 0))
        self.assertFalse(np.any(batch.muon_continuous == -9999))


class OverflowAndArmContract(unittest.TestCase):
    def setUp(self):
        self.dataset, self.capabilities = make_synthetic_dataset(
            n_signal=72, n_data=44, n_background=14, seed=21
        )

    def test_overflow_energy_is_conserved(self):
        batch = self.dataset.signal.truth
        self.assertGreater(int(np.count_nonzero(batch.overflow_energy)), 0)
        aggregate_energy = np.where(
            batch.type_id == TYPE_OVERFLOW, batch.continuous[:, :, 0], 0.0
        ).sum(axis=1)
        np.testing.assert_allclose(
            aggregate_energy, batch.overflow_energy, rtol=2e-6, atol=1e-6
        )

    def test_direct_truncation_rejects_nonfinite(self):
        continuous = np.ones((2, 4, 3), dtype=np.float32)
        continuous[0, 0, 0] = np.nan
        types = np.ones((2, 4), dtype=np.int64)
        views = np.ones((2, 4), dtype=np.int64)
        mask = np.ones((2, 4), dtype=bool)
        with self.assertRaisesRegex(ValueError, "NaN"):
            truncate_with_overflow(continuous, types, views, mask, 3)

    def test_arm_c_to_d_typed_changes_only_declared_type_controls(self):
        c = build_arm_manifest("C", self.capabilities)
        d = build_arm_manifest("D-typed", self.capabilities)
        diff = exact_arm_diff(c, d)
        self.assertEqual(set(diff), {"arm", "use_real_types", "disabled_features"})
        c_view = materialize_feature_view(self.dataset.signal.reco, c)
        d_view = materialize_feature_view(self.dataset.signal.reco, d)
        np.testing.assert_allclose(c_view.continuous, d_view.continuous)
        np.testing.assert_allclose(c_view.globals, d_view.globals)
        self.assertTrue(np.all(c_view.type_id[c_view.token_mask] == TYPE_GENERIC))
        self.assertGreater(len(np.unique(d_view.type_id[d_view.token_mask])), 1)

    def test_muon_and_richer_global_blocks_are_isolated(self):
        c = build_arm_manifest("C", self.capabilities)
        muon = build_arm_manifest("E-muon", self.capabilities)
        rich = build_arm_manifest("E-rich-no-charge", self.capabilities)
        self.assertEqual(c.active_globals, ("mu_pt", "mu_pparallel"))
        self.assertEqual(
            muon.active_globals,
            (
                "mu_pt",
                "mu_pparallel",
                "mu_energy",
                "mu_cos_phi",
                "mu_sin_phi",
            ),
        )
        muon_diff = exact_arm_diff(c, muon)
        self.assertEqual(set(muon_diff), {"arm", "active_globals"})
        rich_diff = exact_arm_diff(muon, rich)
        self.assertEqual(set(rich_diff), {"arm", "active_globals"})
        c_view = materialize_feature_view(self.dataset.signal.reco, c)
        muon_view = materialize_feature_view(self.dataset.signal.reco, muon)
        rich_view = materialize_feature_view(self.dataset.signal.reco, rich)
        np.testing.assert_allclose(c_view.continuous, muon_view.continuous)
        np.testing.assert_array_equal(c_view.type_id, muon_view.type_id)
        self.assertFalse(np.array_equal(c_view.globals, muon_view.globals))
        self.assertFalse(np.array_equal(muon_view.globals, rich_view.globals))

    def test_view_and_overflow_are_separate_ablations(self):
        base = build_arm_manifest("C", self.capabilities)
        view = build_arm_manifest("D-view", self.capabilities)
        changed = build_arm_manifest(
            "D-view", self.capabilities, use_overflow_aggregate=True
        )
        view_diff = exact_arm_diff(base, view)
        self.assertEqual(
            set(view_diff), {"arm", "use_detector_view", "disabled_features"}
        )
        diff = exact_arm_diff(view, changed)
        self.assertNotIn("use_detector_view", diff)
        self.assertEqual(
            set(diff), {"use_overflow_aggregate", "disabled_features"}
        )
        self.assertNotIn("use_real_types", diff)

    def test_muon_token_and_global_are_explicit(self):
        global_arm = build_arm_manifest("E-muon", self.capabilities)
        token_arm = build_arm_manifest(
            "E-muon", self.capabilities, muon_representation="token"
        )
        diff = exact_arm_diff(global_arm, token_arm)
        self.assertIn("muon_representation", diff)
        global_view = materialize_feature_view(self.dataset.signal.reco, global_arm)
        token_view = materialize_feature_view(self.dataset.signal.reco, token_arm)
        self.assertEqual(token_view.continuous.shape[1], global_view.continuous.shape[1] + 1)
        misses = ~self.dataset.signal.pass_reco
        self.assertFalse(np.any(token_view.token_mask[misses, 0]))
        self.assertTrue(np.all(token_view.type_id[misses, 0] == 0))


class PreprocessingAndSplitContract(unittest.TestCase):
    def setUp(self):
        self.dataset, _ = make_synthetic_dataset(
            n_signal=80, n_data=48, n_background=16, seed=19
        )

    def test_fit_uses_selected_real_tokens_only(self):
        batch = self.dataset.signal.reco
        fit_rows = self.dataset.signal.pass_reco.copy()
        fit_rows[::3] = False
        pre = fit_preprocessor(batch, fit_rows)
        transformed = pre.transform(batch)
        self.assertTrue(np.all(transformed.continuous[~batch.token_mask] == 0))
        self.assertEqual(pre.global_count, int(fit_rows.sum()))
        self.assertNotIn("-9999", json.dumps(pre.payload()))

    def test_preprocessing_roundtrip_manifest(self):
        batch = self.dataset.signal.reco
        pre = fit_preprocessor(batch, self.dataset.signal.pass_reco)
        recovered = preprocessor_from_payload(pre.payload())
        np.testing.assert_allclose(pre.token_mean, recovered.token_mean)
        self.assertEqual(pre.global_names, recovered.global_names)

    def test_split_is_key_deterministic_under_reordering(self):
        signal = self.dataset.signal
        first = stable_split(
            signal.reco.row_index, 123, identity=signal.event_key
        )
        order = np.arange(signal.reco.n_rows)[::-1]
        second = stable_split(
            signal.reco.row_index[order], 123, identity=signal.event_key[order]
        )
        keyed_first = {tuple(key): value for key, value in zip(signal.event_key, first)}
        keyed_second = {
            tuple(key): value for key, value in zip(signal.event_key[order], second)
        }
        self.assertEqual(keyed_first, keyed_second)

    def test_vectorized_three_way_partition_is_stable(self):
        rows = np.arange(100_000, dtype=np.int64)
        identities = np.column_stack((rows // 1000, rows % 1000))
        assignment = stable_partition(
            rows, 424242, (0.7, 0.15, 0.15), identity=identities
        )
        counts = np.bincount(assignment, minlength=3) / len(rows)
        np.testing.assert_allclose(counts, [0.7, 0.15, 0.15], atol=0.01)
        order = np.arange(len(rows))[::-1]
        reversed_assignment = stable_partition(
            rows[order], 424242, (0.7, 0.15, 0.15), identity=identities[order]
        )
        np.testing.assert_array_equal(assignment, reversed_assignment[order])


class DensityRatioContract(unittest.TestCase):
    def test_analytic_unequal_mass_calibration(self):
        problem = analytic_gaussian_problem(np.linspace(-4, 4, 101))
        ratio, telemetry = calibrated_ratio(
            problem["balanced_logit"],
            problem["mass0"],
            problem["mass1"],
            30.0,
        )
        np.testing.assert_allclose(ratio, problem["physical_ratio"], rtol=1e-12)
        self.assertAlmostEqual(
            telemetry["log_class_mass_offset"],
            np.log(problem["mass1"] / problem["mass0"]),
        )

    def test_log_ratio_cap_telemetry(self):
        ratio, telemetry = calibrated_ratio(
            np.array([-100.0, 0.0, 100.0]),
            1,
            1,
            5,
            reference_weights=np.array([1.0, 2.0, 3.0]),
        )
        self.assertEqual(telemetry["saturated_count"], 2)
        self.assertAlmostEqual(telemetry["saturated_weight_fraction"], 4.0 / 6.0)
        self.assertEqual(
            set(telemetry["cap_sensitivity"]), {"cap_5", "cap_10", "cap_20"}
        )
        self.assertIn(
            "reweighted_ess", telemetry["cap_sensitivity"]["cap_5"]
        )
        self.assertTrue(np.all(np.isfinite(ratio)))
        self.assertTrue(np.all(ratio >= 0))

    def test_balanced_bce_rejects_negative_weights(self):
        with self.assertRaisesRegex(ValueError, "weights1"):
            balanced_weighted_bce_numpy(
                np.zeros(2), np.zeros(2), np.ones(2), np.array([1.0, -1.0])
            )

    def test_tf_odds_and_torch_mass_offset_are_same_physical_ratio(self):
        fixture = fixed_ratio_convention_fixture()
        self.assertTrue(fixture["equivalent"])
        np.testing.assert_allclose(
            fixture["tf_odds_ratio"],
            fixture["torch_balanced_plus_mass_offset_ratio"],
            rtol=1e-13,
        )
        self.assertIn("no stochastic classifier", fixture["scope"])


class AnalyticConditionalClosure(unittest.TestCase):
    def setUp(self):
        self.fixture = make_known_ratio_closure_dataset(
            n_signal=160, n_background=24, seed=424242
        )

    def test_pseudodata_is_aligned_with_known_event_weight(self):
        fixture = self.fixture
        rows = fixture.data_to_signal_row
        np.testing.assert_allclose(
            fixture.dataset.measured.data.continuous,
            fixture.dataset.signal.reco.continuous[rows],
        )
        expected_mass = (
            fixture.dataset.signal.w_reco[rows] * fixture.analytic_reco_ratio
        )
        np.testing.assert_allclose(
            fixture.dataset.measured.refined_weights[: len(rows)], expected_mass
        )
        np.testing.assert_array_equal(
            fixture.dataset.measured.aligned_signal_row[: len(rows)], rows
        )
        self.assertTrue(
            np.all(fixture.dataset.measured.aligned_signal_row[len(rows) :] == -1)
        )
        self.assertTrue(
            np.all(fixture.dataset.measured.refined_weights[len(rows) :] == 0)
        )

    def test_exact_direction_passes_full_iteration_metrics(self):
        fixture = self.fixture
        metrics = conditional_closure_metrics(
            fixture.dataset,
            fixture.expected_truth_ratio,
            fixture.expected_truth_ratio,
            fixture.declared_tail_mask,
        )
        self.assertTrue(metrics["direction_gate"]["pass"])
        self.assertEqual(metrics["log_ratio_residual"]["rmse"], 0.0)
        self.assertIn("mu_pt_x_mu_pparallel", metrics["projection_residuals"])
        self.assertIn("mu_pt_x_eavail_x_q3", metrics["projection_residuals"])
        self.assertGreater(metrics["ess"]["declared_tail_expected"], 0)
        self.assertIn("total_saturated_weight_mass", metrics["cap_saturation"])

    def test_inverted_direction_fails(self):
        fixture = self.fixture
        metrics = conditional_closure_metrics(
            fixture.dataset,
            1.0 / fixture.expected_truth_ratio,
            fixture.expected_truth_ratio,
            fixture.declared_tail_mask,
        )
        self.assertFalse(metrics["direction_gate"]["pass"])
        self.assertGreater(metrics["log_ratio_residual"]["rmse"], 0.25)


class FailClosedExternalSeams(unittest.TestCase):
    def test_absent_g2_fails_closed(self):
        with self.assertRaisesRegex(FileNotFoundError, "fail closed"):
            load_publication_g2(
                "/definitely/absent/g2.npz",
                "/definitely/absent/target.npy",
                "/definitely/absent/receipt.json",
            )

    def test_public_mapping_is_diagnostic_only(self):
        mapping = {
            "data": np.zeros((3, 4, 10)),
            "truth_labels": np.zeros((3, 15)),
            "global_features": np.zeros((3, 16)),
        }
        mapping["data"][0, 0, 2] = 1.0
        result = adapt_loaded_public_mapping(mapping)
        self.assertEqual(result["revision"], PUBLIC_REVISION)
        self.assertFalse(result["publication_omnifold_eligible"])
        self.assertEqual(
            result["padding_type_census"]["raw_type_zero_but_feature2_nonzero"], 1
        )

    def test_public_adapter_never_downloads(self):
        with self.assertRaises(FileNotFoundError):
            inspect_local_public_artifact("/definitely/absent/public.pb")

    def test_public_pb_requires_explicit_trust_before_deserialization(self):
        with tempfile.TemporaryDirectory() as td:
            artifact = Path(td) / "public.pb"
            artifact.write_bytes(b"unknown")
            with self.assertRaisesRegex(ValueError, "trusted=True"):
                inspect_trusted_public_pb(
                    artifact,
                    trusted=False,
                    expected_sha256=file_sha256(artifact),
                )

    def test_truth_phi_boundary_uses_periodic_coordinates(self):
        eps = 1e-7
        part_gen = np.zeros((1, 2, 5), dtype=np.float32)
        part_gen[0, :, 0] = 2_000.0
        part_gen[0, :, 1] = -1_000.0
        part_gen[0, 0, 2] = eps * 1_000.0
        part_gen[0, 1, 2] = -eps * 1_000.0
        part_gen[0, :, 3] = 500.0
        part_gen[0, :, 4] = 211
        truth_scalars = np.ones((1, 4), dtype=np.float32)
        batch = g2_adapter._truth_batch(part_gen, truth_scalars)
        self.assertEqual(batch.coords.shape[2], 3)
        self.assertLess(
            np.linalg.norm(batch.coords[0, 0] - batch.coords[0, 1]), 1e-5
        )

    def test_g2_compressed_production_size_refuses_before_numpy_load(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "packet.npz"
            path.write_bytes(b"x" * 32)
            original = g2_adapter.MAX_G2_MINI_PACKET_BYTES
            try:
                g2_adapter.MAX_G2_MINI_PACKET_BYTES = 16
                with self.assertRaisesRegex(ValueError, "refusing before np.load"):
                    preflight_g2_mini_packet(path)
            finally:
                g2_adapter.MAX_G2_MINI_PACKET_BYTES = original

    def test_g2_row_inventory_refuses_from_headers_before_materialization(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "rows.npz"
            np.savez_compressed(
                path,
                **{
                    key: np.zeros((6, 1), dtype=np.uint8)
                    for key in g2_adapter.REQUIRED_G2_KEYS
                },
            )
            original = g2_adapter.MAX_G2_MINI_PACKET_ROWS
            try:
                g2_adapter.MAX_G2_MINI_PACKET_ROWS = 5
                with self.assertRaisesRegex(ValueError, "row bound"):
                    preflight_g2_mini_packet(path)
            finally:
                g2_adapter.MAX_G2_MINI_PACKET_ROWS = original

    def test_current_arm_f_is_unavailable_without_fallback(self):
        outcome = current_arm_f_outcome()
        self.assertEqual(outcome["status"], "unavailable")
        self.assertIsNone(outcome["fallback"])

    def test_arm_f_rejects_missing_and_unlicensed_manifest(self):
        outcome = arm_f_eligibility(
            None,
            None,
            expected_architecture_fingerprint="a",
            expected_preprocessing_fingerprint="p",
            expected_tensor_shapes={},
        )
        self.assertEqual(outcome["status"], "unavailable")
        self.assertIsNone(outcome["fallback"])

        with tempfile.TemporaryDirectory() as td:
            checkpoint = Path(td) / "weights.safetensors"
            manifest = Path(td) / "manifest.json"
            checkpoint.write_bytes(b"not-a-real-checkpoint")
            manifest.write_text(
                json.dumps(
                    {
                        "checkpoint_sha256": file_sha256(checkpoint),
                        "weight_license": "unknown",
                        "weight_redistribution_permitted": False,
                        "architecture_fingerprint": "a",
                        "preprocessing_fingerprint": "p",
                        "tensor_shapes": {},
                        "source_url": "https://example.invalid",
                        "source_commit": "deadbeef",
                    }
                ),
                encoding="utf-8",
            )
            outcome = arm_f_eligibility(
                str(checkpoint),
                str(manifest),
                expected_architecture_fingerprint="a",
                expected_preprocessing_fingerprint="p",
                expected_tensor_shapes={},
            )
        self.assertEqual(outcome["status"], "unavailable")
        self.assertTrue(any("license" in reason for reason in outcome["reasons"]))
        self.assertIsNone(outcome["fallback"])

    def test_tiny_g2_seam_recovers_raw_target_mass_without_claim(self):
        ns, nd, nb, p = 6, 4, 2, 3
        rng = np.random.default_rng(81)
        pass_reco = np.array([True, False, True, False, True, True])
        pass_truth = np.ones(ns, bool)

        def reco_block(n, valid):
            cloud = rng.uniform(10, 100, (n, p, 3)).astype(np.float32)
            view = rng.integers(1, 4, (n, p), dtype=np.int64)
            cloud[~valid] = 0
            view[~valid] = 0
            scalars = rng.uniform(0.1, 3, (n, 4)).astype(np.float32)
            muon = rng.uniform(1, 100, (n, 7)).astype(np.float32)
            vertex = rng.uniform(-100, 100, (n, 3)).astype(np.float32)
            muon[~valid] = -9999
            vertex[~valid] = -9999
            return cloud, view, scalars, muon, vertex

        sig = reco_block(ns, pass_reco)
        data = reco_block(nd, np.ones(nd, bool))
        bkg = reco_block(nb, np.ones(nb, bool))
        part_gen = rng.uniform(10, 100, (ns, p, 5)).astype(np.float32)
        part_gen[:, :, 4] = 211
        w_truth = rng.uniform(0.5, 2, ns)
        w_reco = rng.uniform(0.5, 2, ns)
        w_bkg = rng.uniform(0.5, 2, nb)
        bkg_indices = np.arange(nb)
        arrays = {
            "part_reco": sig[0],
            "reco_view": sig[1],
            "reco_scalars": sig[2],
            "reco_muon": sig[3],
            "reco_vertex": sig[4],
            "reco_time": np.zeros((ns, p), np.float32),
            "part_gen": part_gen,
            "truth_scalars": rng.uniform(0.1, 3, (ns, 4)).astype(np.float32),
            "pass_reco": pass_reco,
            "pass_truth": pass_truth,
            "w_reco": w_reco,
            "w_truth": w_truth,
            "measured_pc": data[0],
            "data_view": data[1],
            "measured_scalars": data[2],
            "data_muon": data[3],
            "data_vertex": data[4],
            "data_time": np.zeros((nd, p), np.float32),
            "bkg_part_reco": bkg[0],
            "bkg_view": bkg[1],
            "bkg_reco_scalars": bkg[2],
            "bkg_muon": bkg[3],
            "bkg_vertex": bkg[4],
            "bkg_time": np.zeros((nb, p), np.float32),
            "w_bkg": w_bkg,
            "bkg_indices": bkg_indices,
            "petSchemaVersion": "g2-fullevent-v1",
            "hasFullEventSchema": 1,
            "fullPhaseSpace": 1,
            "estimator_fingerprint": "pet-fullevent-fps-v1",
            "data_pot": 1.0,
        }
        arrays["sig_identity_hash"] = g2_adapter._legacy_order_hash(
            w_truth, pass_truth
        )
        arrays["data_identity_hash"] = g2_adapter._legacy_order_hash(data[0])
        arrays["bkg_identity_hash"] = g2_adapter._legacy_order_hash(
            w_bkg, bkg_indices
        )
        with tempfile.TemporaryDirectory() as td:
            g2_path = os.path.join(td, "g2.npz")
            target_path = os.path.join(td, "target.npy")
            receipt_path = os.path.join(td, "receipt.json")
            np.savez_compressed(g2_path, **arrays)
            normalized = np.linspace(1, 2, nd + nb).astype(np.float32)
            np.save(target_path, normalized, allow_pickle=False)
            receipt = {
                "input_preflight": {"sha256": file_sha256(g2_path)},
                "step1_feed": {
                    "weights": {"sha256": file_sha256(target_path)},
                    "normalized_sum": float(normalized.sum()),
                },
                "runtime_target": {
                    "n_measured_rows": nd + nb,
                    "refined_sum": 42.0,
                    "pot_scale": 0.25,
                },
            }
            with open(receipt_path, "w", encoding="utf-8") as handle:
                json.dump(receipt, handle)
            dataset, capabilities = load_publication_g2(
                g2_path, target_path, receipt_path
            )
        self.assertAlmostEqual(dataset.measured.refined_weights.sum(), 42.0)
        self.assertEqual(dataset.pot_scale, 0.25)
        self.assertEqual(
            dataset.pot_scale_source, "gate2_receipt.runtime_target.pot_scale"
        )
        with self.assertRaisesRegex(ValueError, "explicitly supply"):
            resolve_pot_scale(dataset, None)
        with self.assertRaisesRegex(ValueError, "differs"):
            resolve_pot_scale(dataset, 1.0)
        self.assertEqual(resolve_pot_scale(dataset, 0.25), 0.25)
        self.assertAlmostEqual(
            resolve_pot_scale(dataset, 0.25) * dataset.signal.w_reco.sum(),
            0.25 * w_reco.sum(),
        )
        np.testing.assert_allclose(
            dataset.signal.reco.globals[pass_reco, :2], sig[2][pass_reco, :2]
        )  # G2 scalar branches are already GeV; never divide by 1000 here.
        np.testing.assert_allclose(
            dataset.signal.reco.globals[pass_reco, 5:7],
            sig[2][pass_reco, 2:4],
        )
        self.assertFalse(dataset.schema["g2_validation_claim"])
        self.assertIn("absent-publication-G2", dataset.schema["g2_units_assumption"])
        self.assertFalse(capabilities.real_object_types)
        with self.assertRaisesRegex(ValueError, "real reconstructed object types"):
            build_arm_manifest("D-typed", capabilities)
        build_arm_manifest("D-view", capabilities)
        build_arm_manifest("E-muon", capabilities)
        build_arm_manifest("E-rich-no-charge", capabilities)
        with self.assertRaisesRegex(ValueError, "charge global"):
            build_arm_manifest("E-rich", capabilities)
        with self.assertRaisesRegex(ValueError, "muon-token KNN"):
            build_arm_manifest(
                "E-muon", capabilities, muon_representation="token"
            )


class XPS2BoundedMemmap(unittest.TestCase):
    def test_read_only_bounded_deterministic_packet(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            n = 200
            arrays = {
                "part_gen": np.arange(n * 3 * 5, dtype=np.float32).reshape(n, 3, 5),
                "part_reco": np.arange(n * 3 * 3, dtype=np.float32).reshape(n, 3, 3),
                "pass_reco": np.arange(n) % 2 == 0,
                "pass_truth": np.ones(n, bool),
                "w_truth": np.linspace(0.5, 2.0, n),
                "measured_pc": np.linspace(
                    0.1, 4.0, 61 * 3 * 3, dtype=np.float32
                ).reshape(61, 3, 3),
                "measured_weights": np.linspace(0.8, 1.2, 61),
            }
            for name, value in arrays.items():
                np.save(root / f"{name}.npy", value, allow_pickle=False)
            first = open_xps2_memmap(root, max_rows=23, seed=424242)
            second = open_xps2_memmap(root, max_rows=23, seed=424242)
            self.assertEqual(first.row_count, n)
            self.assertEqual(first.receipt["selected_rows"], 23)
            self.assertFalse(first.receipt["w_reco_available"])
            self.assertFalse(first.receipt["full_event_evidence"])
            self.assertTrue(all(not value.flags.writeable for value in first.arrays.values()))
            np.testing.assert_array_equal(first.selected_rows, second.selected_rows)
            packet = first.read_packet()
            self.assertEqual(packet["part_gen"].shape[0], 23)
            np.testing.assert_array_equal(
                packet["w_truth"], arrays["w_truth"][first.selected_rows]
            )
            census = inspect_xps2_packet(root, max_rows=23, seed=424242)
            self.assertEqual(census["packet_arrays"]["part_gen"]["shape"][0], 23)
            self.assertFalse(census["publication_omnifold_eligible"])
            dataset = build_xps2_recoil_dataset(
                root, max_mc_rows=23, max_data_rows=13, seed=424242
            )
            self.assertEqual(dataset.signal.reco.n_rows, 23)
            self.assertEqual(dataset.measured.data.n_rows, 13)
            self.assertEqual(dataset.measured.background.n_rows, 0)
            np.testing.assert_array_equal(
                dataset.signal.w_reco, dataset.signal.w_truth
            )
            self.assertFalse(dataset.schema["full_event_evidence"])
            self.assertFalse(dataset.schema["typed_object_evidence"])

    def test_row_limit_and_missing_array_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "max_rows"):
                open_xps2_memmap(td, max_rows=1_000_001)
            with self.assertRaises(FileNotFoundError):
                open_xps2_memmap(td, max_rows=1)


class ContractOnlyCLI(unittest.TestCase):
    def test_top_level_package_import_is_root_tf_torch_free(self):
        command = [
            sys.executable,
            "-c",
            (
                "import sys, pet2_torch; "
                "assert 'torch' not in sys.modules; "
                "assert 'tensorflow' not in sys.modules; "
                "assert 'ROOT' not in sys.modules"
            ),
        ]
        env = dict(os.environ)
        env["PYTHONPATH"] = ND
        completed = subprocess.run(
            command, env=env, text=True, capture_output=True, check=False
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_manifest_fingerprints_are_deterministic_and_sensitive(self):
        first, capabilities = make_synthetic_dataset(
            n_signal=32, n_data=24, n_background=8, seed=404
        )
        second, _ = make_synthetic_dataset(
            n_signal=32, n_data=24, n_background=8, seed=404
        )
        self.assertEqual(
            first.manifest()["fingerprint"], second.manifest()["fingerprint"]
        )
        plain = build_arm_manifest("C", capabilities)
        view = build_arm_manifest("D-view", capabilities)
        self.assertNotEqual(
            plain.payload()["fingerprint"], view.payload()["fingerprint"]
        )

    def test_contract_cli_runs_without_torch(self):
        with tempfile.TemporaryDirectory() as td:
            output = os.path.join(td, "run")
            command = [
                sys.executable,
                "-m",
                "pet2_torch.cli",
                "--out",
                output,
                "--contract-only",
                "--events",
                "32",
                "--data-events",
                "24",
                "--background-events",
                "8",
                "--arms",
                "C",
                "D-view",
                "D-typed",
                "E-muon",
                "E-rich-no-charge",
            ]
            env = dict(os.environ)
            env["PYTHONPATH"] = ND
            completed = subprocess.run(
                command, env=env, text=True, capture_output=True, check=False
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            with open(os.path.join(output, "summary.json"), encoding="utf-8") as handle:
                summary = json.load(handle)
            self.assertEqual(summary["status"], "contract_only")
            self.assertFalse(summary["g2_validation_claim"])
            self.assertEqual(summary["arm_f"]["status"], "unavailable")

    def test_tf_ab_stress_contract_is_self_locating_and_login_safe(self):
        with tempfile.TemporaryDirectory() as td:
            output = os.path.join(td, "tf_ab.json")
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pet2_torch.tf_ab_conditional_stress",
                    "--out",
                    output,
                    "--contract-only",
                    "--events",
                    "64",
                ],
                cwd="/tmp",
                env={**os.environ, "PYTHONPATH": ND},
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            with open(output, encoding="utf-8") as handle:
                result = json.load(handle)
            self.assertEqual(result["status"], "contract_only")
            self.assertFalse(result["recipe"]["layer_equivalence_claim"])
            self.assertFalse(result["g2_validation_claim"])

    def test_delta_launcher_is_one_gpu_bounded_and_selftests(self):
        launcher = os.path.join(ND, "pet2_torch", "sbatch_pet2_fixture_delta.sh")
        body = Path(launcher).read_text(encoding="utf-8")
        self.assertIn("#SBATCH --job-name=pet2x_onearm", body)
        self.assertIn("#SBATCH --gpus-per-node=1", body)
        self.assertIn("#SBATCH --cpus-per-task=8", body)
        self.assertIn("module load pytorch-conda/2.8", body)
        self.assertIn("forbidden active checkout", body)
        syntax = subprocess.run(["bash", "-n", launcher], capture_output=True, text=True)
        self.assertEqual(syntax.returncode, 0, syntax.stderr)
        with tempfile.TemporaryDirectory() as td:
            env = dict(os.environ)
            env.update(
                {
                    "PET2_REPO": os.path.dirname(ND),
                    "PET2_OUT_BASE": os.path.join(td, "isolated"),
                    "PET2_DELTA_SELFTEST": "1",
                    "PET2_ARM": "C",
                    "PET2_ESTIMATOR_SEED": "101",
                    "PET2_MODE": "matched-pilot",
                }
            )
            check = subprocess.run(
                ["bash", launcher], env=env, capture_output=True, text=True
            )
        self.assertEqual(check.returncode, 0, check.stderr)
        self.assertIn("no submit, no module load, no training", check.stdout)

    def test_pilot_decision_requires_global_and_tail_ess(self):
        keyed = {
            ("base", 101): {
                "log_ratio_rmse": 1.0,
                "direction_gate_pass": 1,
            },
            ("child", 101): {
                "log_ratio_rmse": 0.9,
                "direction_gate_pass": 1,
            },
        }
        summaries = {
            "base": {
                "metrics": {
                    "log_ratio_rmse": {"mean": 1.0},
                    "global_ess": {"mean": 100.0},
                    "tail_ess": {"mean": 100.0},
                    "cap_saturated_count": {"mean": 0.0},
                }
            },
            "child": {
                "metrics": {
                    "log_ratio_rmse": {"mean": 0.9},
                    "global_ess": {"mean": 95.0},
                    "tail_ess": {"mean": 80.0},
                    "cap_saturated_count": {"mean": 0.0},
                }
            },
        }
        result = _comparison(keyed, summaries, "child", "base", (101,))
        self.assertGreater(result["closure_rmse_improvement_percent"], 5.0)
        self.assertEqual(
            result["decision"], "harmful-or-unstable-on-synthetic-pilot"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
