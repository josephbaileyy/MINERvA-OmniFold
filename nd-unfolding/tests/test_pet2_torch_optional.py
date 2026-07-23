"""Optional PyTorch/safetensors tests; cleanly skipped on login hosts without them."""

import os
import sys
import tempfile
import unittest
from dataclasses import replace

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ND not in sys.path:
    sys.path.insert(0, ND)

from pet2_torch.density_ratio import (
    HAS_TORCH,
    RatioTrainingConfig,
    calibrated_ratio,
    fit_density_ratio,
    predict_logits,
)
from pet2_torch.contracts import TokenBatch
from pet2_torch.engine import OneIterationConfig, run_iterations, run_one_iteration
from pet2_torch.evaluation import conditional_closure_metrics
from pet2_torch.features import build_arm_manifest, materialize_feature_view
from pet2_torch.fixtures import (
    make_known_ratio_closure_dataset,
    make_synthetic_dataset,
)
from pet2_torch.model import ModelConfig, build_model
from pet2_torch.preprocessing import fit_preprocessor
from pet2_torch.public_gregor import inspect_trusted_public_pb
from pet2_torch.utils import file_sha256, seed_everything

if HAS_TORCH:
    import torch
else:
    torch = None

try:
    import safetensors  # noqa: F401

    HAS_SAFETENSORS = True
except ImportError:
    HAS_SAFETENSORS = False


@unittest.skipUnless(HAS_TORCH, "PyTorch is not installed on this host")
class ModelBehavior(unittest.TestCase):
    def setUp(self):
        seed_everything(42)
        self.dataset, self.capabilities = make_synthetic_dataset(
            n_signal=48, n_data=32, n_background=12, seed=4
        )
        arm = build_arm_manifest(
            "D-view", self.capabilities, use_overflow_aggregate=True
        )
        self.batch = materialize_feature_view(self.dataset.signal.truth, arm)
        pre = fit_preprocessor(self.batch, self.dataset.signal.pass_truth)
        self.batch = pre.transform(self.batch)
        self.config = ModelConfig(
            continuous_dim=self.batch.continuous.shape[2],
            coord_dim=self.batch.coords.shape[2],
            global_dim=self.batch.globals.shape[1],
            hidden_dim=32,
            num_heads=4,
            transformer_layers=1,
            edge_layers=1,
            k_neighbors=2,
        )

    def test_seed_policy_disables_nondeterministic_attention(self):
        settings = seed_everything(101, deterministic=True)
        self.assertTrue(settings["deterministic_algorithms"])
        if torch.cuda.is_available():
            self.assertFalse(settings["flash_sdp_enabled"])
            self.assertFalse(settings["memory_efficient_sdp_enabled"])
            self.assertTrue(settings["math_sdp_enabled"])

    def _tensor(self, batch):
        return {
            "continuous": torch.as_tensor(batch.continuous),
            "coords": torch.as_tensor(batch.coords),
            "token_mask": torch.as_tensor(batch.token_mask),
            "type_id": torch.as_tensor(batch.type_id),
            "view_id": torch.as_tensor(batch.view_id),
            "globals_": torch.as_tensor(batch.globals),
        }

    def test_permutation_invariance(self):
        model = build_model(self.config).eval()
        permutation = np.arange(self.batch.continuous.shape[1])[::-1]
        permuted = replace(
            self.batch,
            continuous=self.batch.continuous[:, permutation],
            coords=self.batch.coords[:, permutation],
            token_mask=self.batch.token_mask[:, permutation],
            type_id=self.batch.type_id[:, permutation],
            view_id=self.batch.view_id[:, permutation],
        )
        with torch.no_grad():
            original = model(**self._tensor(self.batch))
            changed = model(**self._tensor(permuted))
        torch.testing.assert_close(original, changed, rtol=2e-5, atol=2e-5)

    def test_padded_values_do_not_change_output(self):
        model = build_model(self.config).eval()
        continuous = self.batch.continuous.copy()
        coords = self.batch.coords.copy()
        continuous[~self.batch.token_mask] = 999.0
        coords[~self.batch.token_mask] = -777.0
        canonical = replace(self.batch, continuous=continuous, coords=coords).validated()
        with torch.no_grad():
            original = model(**self._tensor(self.batch))
            changed = model(**self._tensor(canonical))
        torch.testing.assert_close(original, changed)

    def test_all_declared_arms_have_identical_parameter_tensors(self):
        schemas = []
        for name in (
            "C",
            "D-view",
            "D-typed",
            "E-muon",
            "E-rich-no-charge",
            "E-rich",
        ):
            arm = build_arm_manifest(name, self.capabilities)
            batch = materialize_feature_view(self.dataset.signal.reco, arm)
            config = replace(
                self.config,
                continuous_dim=batch.continuous.shape[2],
                coord_dim=batch.coords.shape[2],
                global_dim=batch.globals.shape[1],
            )
            model = build_model(config)
            schemas.append(
                {
                    key: tuple(value.shape)
                    for key, value in model.state_dict().items()
                }
            )
        self.assertTrue(all(schema == schemas[0] for schema in schemas[1:]))

    def test_tiny_overfit_loss_decreases(self):
        class0 = self.batch.subset(np.arange(16))
        class1 = replace(
            self.batch.subset(np.arange(16, 32)),
            globals=self.batch.globals[16:32] + 3.0,
        ).validated()
        model = build_model(self.config)
        receipt = fit_density_ratio(
            model,
            class0,
            class1,
            np.ones(16),
            np.ones(16) * 3.0,
            RatioTrainingConfig(
                epochs=12,
                batch_size=32,
                learning_rate=3e-3,
                seed=42,
                device="cpu",
            ),
        )
        self.assertLess(receipt["history"][-1], receipt["history"][0])
        self.assertAlmostEqual(
            receipt["log_class_mass_offset"], np.log(3.0), places=6
        )

    def test_learned_analytic_gaussian_ratio(self):
        class GlobalLogit(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = torch.nn.Linear(1, 1)

            def forward(self, continuous, coords, token_mask, type_id, view_id, globals_):
                return self.linear(globals_).squeeze(-1)

        rng = np.random.default_rng(55)
        n = 1024

        def batch(values, name):
            values = np.asarray(values, np.float32)
            return TokenBatch(
                continuous=np.ones((n, 1, 1), np.float32),
                coords=np.zeros((n, 1, 1), np.float32),
                token_mask=np.ones((n, 1), bool),
                type_id=np.ones((n, 1), np.int64),
                view_id=np.zeros((n, 1), np.int64),
                globals=values[:, None],
                row_index=np.arange(n),
                global_names=("x",),
                provenance=name,
            ).validated()

        class0 = batch(rng.normal(-0.5, 1.2, n), "analytic_class0")
        class1 = batch(rng.normal(0.75, 1.2, n), "analytic_class1")
        model = GlobalLogit()
        fit = fit_density_ratio(
            model,
            class0,
            class1,
            np.full(n, 3.0 / n),
            np.full(n, 11.0 / n),
            RatioTrainingConfig(
                epochs=45,
                batch_size=256,
                learning_rate=3e-2,
                weight_decay=0.0,
                seed=55,
                device="cpu",
            ),
        )
        grid = np.linspace(-2.5, 2.5, n, dtype=np.float32)
        grid_batch = batch(grid, "analytic_grid")
        logits = predict_logits(
            model,
            grid_batch,
            RatioTrainingConfig(device="cpu", inference_batch_size=256),
        )
        learned, _ = calibrated_ratio(logits, 3.0, 11.0, 30.0)
        expected_logit = (
            -0.5 * np.square((grid - 0.75) / 1.2)
            + 0.5 * np.square((grid + 0.5) / 1.2)
        )
        expected = np.exp(expected_logit) * 11.0 / 3.0
        self.assertGreater(np.corrcoef(np.log(learned), np.log(expected))[0, 1], 0.98)


@unittest.skipUnless(HAS_TORCH, "PyTorch is not installed on this host")
class OneIterationEngine(unittest.TestCase):
    def test_native_miss_and_full_order_extraction(self):
        seed_everything(9)
        dataset, capabilities = make_synthetic_dataset(
            n_signal=48, n_data=32, n_background=12, seed=9
        )
        arm = build_arm_manifest("C", capabilities)
        result = run_one_iteration(
            dataset,
            arm,
            OneIterationConfig(
                ratio=RatioTrainingConfig(
                    epochs=1,
                    batch_size=64,
                    inference_batch_size=64,
                    learning_rate=1e-3,
                    seed=9,
                    device="cpu",
                ),
                model_hidden_dim=16,
                model_heads=4,
                model_transformer_layers=1,
                model_edge_layers=1,
                model_k_neighbors=2,
                split_seed=91,
            ),
        )
        np.testing.assert_array_equal(result.row_index, np.arange(48))
        self.assertEqual(result.receipt["full_order"]["gap_count"], 0)
        self.assertGreater(result.receipt["native_misses"], 0)
        self.assertTrue(np.all(np.isfinite(result.push)))
        self.assertTrue(np.all(result.push >= 0))

    def test_two_iteration_known_closure_emits_full_metrics(self):
        seed_everything(101)
        fixture = make_known_ratio_closure_dataset(
            n_signal=64, n_background=12, seed=424242
        )
        arm = build_arm_manifest("E-muon", fixture.capabilities)
        result, receipts = run_iterations(
            fixture.dataset,
            arm,
            OneIterationConfig(
                ratio=RatioTrainingConfig(
                    epochs=1,
                    batch_size=64,
                    inference_batch_size=64,
                    learning_rate=1e-3,
                    seed=101,
                    device="cpu",
                ),
                model_hidden_dim=16,
                model_heads=4,
                model_transformer_layers=1,
                model_edge_layers=1,
                model_k_neighbors=2,
                split_seed=424242,
            ),
            iterations=2,
        )
        metrics = conditional_closure_metrics(
            fixture.dataset,
            result.push,
            fixture.expected_truth_ratio,
            fixture.declared_tail_mask,
            iteration_receipts=receipts,
        )
        self.assertEqual(result.receipt["omnifold_iterations"]["count"], 2)
        self.assertEqual(
            result.receipt["split"]["paired_target_rows_share_signal_partition"],
            len(fixture.data_to_signal_row),
        )
        self.assertIn("validation", result.receipt["step1_evaluation"])
        self.assertIn(
            "balanced_weighted_bce",
            result.receipt["step1_evaluation"]["test"],
        )
        self.assertIn("validation", result.receipt["step2_evaluation"])
        self.assertEqual(len(metrics["cap_saturation"]["records"]), 4)
        self.assertIn("mu_pt_x_eavail_x_q3", metrics["projection_residuals"])

    def test_trusted_public_pb_weights_only_census(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "public.pb")
            torch.save(
                {
                    "data": torch.zeros((3, 4, 10)),
                    "truth_labels": torch.zeros((3, 15)),
                    "global_features": torch.zeros((3, 16)),
                },
                path,
            )
            result = inspect_trusted_public_pb(
                path,
                trusted=True,
                expected_sha256=file_sha256(path),
            )
        self.assertEqual(result["row_count"], 3)
        self.assertFalse(result["unfolding_use_permitted"])


@unittest.skipUnless(
    HAS_TORCH and HAS_SAFETENSORS,
    "PyTorch and safetensors are required for portable checkpoint tests",
)
class StrictSaveLoad(unittest.TestCase):
    def test_safetensors_roundtrip_and_shape_rejection(self):
        from safetensors.torch import save_file

        from pet2_torch.artifacts import load_model_strict

        config = ModelConfig(
            continuous_dim=4,
            coord_dim=2,
            global_dim=9,
            hidden_dim=16,
            num_heads=4,
            transformer_layers=1,
            edge_layers=1,
            k_neighbors=2,
        )
        first = build_model(config)
        second = build_model(config)
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "model.safetensors")
            save_file(
                {key: value.detach().contiguous() for key, value in first.state_dict().items()},
                path,
            )
            load_model_strict(path, second)
            for key, value in first.state_dict().items():
                torch.testing.assert_close(value, second.state_dict()[key])
            wrong = build_model(replace(config, hidden_dim=32))
            with self.assertRaisesRegex(ValueError, "shape mismatch"):
                load_model_strict(path, wrong)


if __name__ == "__main__":
    unittest.main(verbosity=2)
