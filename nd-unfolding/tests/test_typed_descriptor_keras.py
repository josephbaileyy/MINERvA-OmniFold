"""Synthetic CPU tests for the trainable typed-descriptor Keras adapter."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")

TEST_ROOT = Path(__file__).resolve().parent
ND_ROOT = TEST_ROOT.parent
PET_ROOT = ND_ROOT / "pet"
for path in (str(TEST_ROOT), str(PET_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

import typed_descriptor_keras as keras_adapter  # noqa: E402
import typed_descriptors as typed  # noqa: E402
from test_typed_descriptors import _synthetic_fixture  # noqa: E402


SMOKE_FIT_DIGEST = "e" * 64


def _copy_inputs(inputs: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    return {name: values.copy() for name, values in inputs.items()}


def _reverse_family_tokens(
    inputs: dict[str, np.ndarray],
    family_name: str,
) -> None:
    segment_ids = inputs[f"{family_name}_segment_ids"]
    order_parts = [
        np.flatnonzero(segment_ids == row)[::-1]
        for row in range(inputs[keras_adapter.DETECTOR_INPUT_KEY].shape[0])
    ]
    order = np.concatenate(order_parts)
    for suffix in ("values", "masks", "segment_ids", "token_mask"):
        key = f"{family_name}_{suffix}"
        inputs[key] = inputs[key][order]


def _raw_field_offset(contract: typed.FamilyContract, field_name: str) -> int:
    offset = 0
    for field in contract.fields:
        if field.name == field_name:
            return offset
        offset += field.width
    raise ValueError(f"Unknown field {field_name!r}")


def _projected_field_offset(
    contract: typed.FamilyContract,
    field_name: str,
) -> int:
    offset = 0
    for field in contract.fields:
        if field.name == field_name:
            return offset
        offset += field.projected_width
    raise ValueError(f"Unknown field {field_name!r}")


class TypedDescriptorKerasTest(unittest.TestCase):
    """Exercise the uncapped trainable adapter without real detector inputs."""

    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.tf = keras_adapter.require_tensorflow()
        except ImportError as error:
            raise unittest.SkipTest(str(error)) from error
        cls.tf.config.set_visible_devices([], "GPU")

    def setUp(self) -> None:
        (
            self.batch,
            self.p12_clusters,
            self.detector_event_block,
            self.truth_event_block,
        ) = _synthetic_fixture()
        self.normalization = typed.fit_frozen_normalization_for_smoke(
            self.batch,
            fit_inventory_row_selection_digest=SMOKE_FIT_DIGEST,
        )
        self.inputs = keras_adapter.prepare_keras_inputs(
            self.batch, self.detector_event_block
        )
        self.model = keras_adapter.build_keras_typed_descriptor_adapter(
            self.normalization,
            hidden_units=(12, 8),
            token_embedding_dim=6,
            activation="tanh",
        )
        self.output = self.model(self.inputs, training=False)

    def test_module_import_does_not_import_tensorflow(self) -> None:
        script = (
            "import sys; "
            f"sys.path.insert(0, {str(PET_ROOT)!r}); "
            "import typed_descriptor_keras; "
            "assert 'tensorflow' not in sys.modules"
        )
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        completed = subprocess.run(
            [sys.executable, "-c", script],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_empty_native_miss_and_ninety_blob_row_are_uncapped(self) -> None:
        self.assertEqual(self.inputs["blobs_values"].shape[0], 92)
        np.testing.assert_array_equal(self.inputs["blobs_counts"], [0, 2, 90])

        typed_columns = np.asarray(self.output)[:, typed.DETECTOR_EVENT_WIDTH :]
        np.testing.assert_array_equal(
            typed_columns[0], np.zeros(typed_columns.shape[1], dtype=np.float32)
        )
        blob_slice = self.model.family_output_slice("blobs")
        np.testing.assert_array_equal(
            np.asarray(self.output)[:, blob_slice.stop - 1],
            np.array([0.0, 2.0, 90.0], dtype=np.float32),
        )

    def test_pooling_is_permutation_invariant_within_families(self) -> None:
        permuted = _copy_inputs(self.inputs)
        for family_name in ("photons", "blobs", "prongs"):
            _reverse_family_tokens(permuted, family_name)
        observed = self.model(permuted, training=False)
        np.testing.assert_allclose(
            np.asarray(self.output), np.asarray(observed), rtol=1.0e-6, atol=1.0e-6
        )

    def test_component_masks_and_unknown_pid_identity(self) -> None:
        photons = self.batch.families["photons"]
        photon_index = int(photons.offsets[1])
        self.assertFalse(np.any(photons.masks["direction"][photon_index]))
        self.assertTrue(photons.masks["time"][photon_index, 0])

        changed = _copy_inputs(self.inputs)
        contract = typed.PRONG_CONTRACT
        raw_pid_offset = _raw_field_offset(contract, "raw_pid")
        changed["prongs_values"][0, raw_pid_offset] = 42.0
        changed["prongs_masks"][0, raw_pid_offset] = True
        family_layer = self.model.family_encoders["prongs"]
        features = family_layer.prepare_features(
            changed["prongs_values"],
            changed["prongs_masks"],
            changed["prongs_token_mask"],
        )
        projected_offset = _projected_field_offset(contract, "raw_pid")
        raw_pid_field = next(
            field for field in contract.fields if field.name == "raw_pid"
        )
        encoded_pid = np.asarray(features)[
            0,
            projected_offset : projected_offset + raw_pid_field.projected_width,
        ]
        np.testing.assert_array_equal(encoded_pid, [0, 0, 0, 0, 0, 1])

    def test_tensor_feature_preparation_matches_committed_contract(self) -> None:
        for contract in typed.FAMILY_CONTRACTS:
            with self.subTest(family=contract.name):
                expected = contract.prepare_features(
                    self.batch.families[contract.name],
                    self.normalization.families[contract.name],
                )
                family_layer = self.model.family_encoders[contract.name]
                observed = family_layer.prepare_features(
                    self.inputs[f"{contract.name}_values"],
                    self.inputs[f"{contract.name}_masks"],
                    self.inputs[f"{contract.name}_token_mask"],
                )
                np.testing.assert_allclose(
                    expected, np.asarray(observed), rtol=0.0, atol=1.0e-6
                )

    def test_disabled_family_contribution_is_exactly_zero(self) -> None:
        for contract in typed.FAMILY_CONTRACTS:
            with self.subTest(family=contract.name):
                disabled = _copy_inputs(self.inputs)
                disabled[f"{contract.name}_enabled"][:] = False
                observed = np.asarray(self.model(disabled, training=False))
                family_slice = self.model.family_output_slice(contract.name)
                np.testing.assert_array_equal(
                    observed[:, family_slice],
                    np.zeros(
                        (
                            self.batch.row_count,
                            family_slice.stop - family_slice.start,
                        )
                    ),
                )

    def test_masked_numerical_values_have_no_influence(self) -> None:
        changed = _copy_inputs(self.inputs)
        for contract in typed.FAMILY_CONTRACTS:
            values_key = f"{contract.name}_values"
            masks_key = f"{contract.name}_masks"
            changed[values_key][~changed[masks_key]] = np.float32(1.0e20)
        observed = self.model(changed, training=False)
        np.testing.assert_array_equal(np.asarray(self.output), np.asarray(observed))

    def test_forward_and_trainable_gradients_are_finite_on_cpu(self) -> None:
        tensor_inputs = {
            name: self.tf.convert_to_tensor(values)
            for name, values in self.inputs.items()
        }
        with self.tf.GradientTape() as tape:
            output = self.model(tensor_inputs, training=True)
            loss = self.tf.reduce_sum(
                self.tf.square(output[:, typed.DETECTOR_EVENT_WIDTH :])
            )
        gradients = tape.gradient(loss, self.model.trainable_variables)
        self.assertTrue(np.all(np.isfinite(np.asarray(output))))
        self.assertTrue(gradients)
        for gradient in gradients:
            self.assertIsNotNone(gradient)
            self.assertTrue(np.all(np.isfinite(np.asarray(gradient))))
        for variable in self.model.trainable_variables:
            self.assertIn("CPU", variable.handle.device.upper())

    def test_native_keras_save_and_load_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "typed-adapter.keras"
            self.model.save(path)
            recovered = keras_adapter.load_keras_typed_descriptor_adapter(path)
            observed = recovered(self.inputs, training=False)
        np.testing.assert_allclose(
            np.asarray(self.output), np.asarray(observed), rtol=0.0, atol=0.0
        )
        self.assertEqual(recovered.get_config(), self.model.get_config())

    def test_detector_and_truth_schema_widths_are_unchanged(self) -> None:
        detector_before = self.detector_event_block.tobytes()
        truth_before = self.truth_event_block.tobytes()
        observed = np.asarray(self.output)
        self.assertEqual(
            detector_before,
            observed[:, : typed.DETECTOR_EVENT_WIDTH].tobytes(),
        )
        self.assertEqual(typed.TRUTH_EVENT_WIDTH, 2)
        with self.assertRaisesRegex(ValueError, "truth descriptors are not defined"):
            keras_adapter.prepare_keras_inputs(
                self.batch, self.truth_event_block
            )
        truth_inputs = _copy_inputs(self.inputs)
        truth_inputs[keras_adapter.DETECTOR_INPUT_KEY] = self.truth_event_block
        with self.assertRaisesRegex(ValueError, "truth block is not augmented"):
            self.model(truth_inputs, training=False)
        self.assertEqual(truth_before, self.truth_event_block.tobytes())


if __name__ == "__main__":
    unittest.main()
