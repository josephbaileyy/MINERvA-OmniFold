"""Synthetic compatibility checks for versioned PET descriptor semantics."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import numpy as np

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")

TEST_ROOT = Path(__file__).resolve().parent
PET_ROOT = TEST_ROOT.parent / "pet"
for path in (str(TEST_ROOT), str(PET_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

import typed_descriptor_keras as keras_adapter  # noqa: E402
import typed_descriptors as typed  # noqa: E402
from test_typed_descriptors import (  # noqa: E402
    _shard_provenance,
    _synthetic_fixture,
)

LEGACY_SCHEMA_VERSION = "pet-typed-descriptors-v1"
LEGACY_SCHEMA_DIGEST = (
    "60966a9090b4e86d45f181e913e5d1ab1761c9256a882f8160025dbd489afd08"
)
SMOKE_FIT_DIGEST = "e" * 64


class TypedDescriptorCompatibilityTest(unittest.TestCase):
    """Reject legacy metadata even when stored array shapes remain compatible."""

    def setUp(self) -> None:
        self.batch, _, _, _ = _synthetic_fixture()
        self.normalization = typed.fit_frozen_normalization_for_smoke(
            self.batch,
            fit_inventory_row_selection_digest=SMOKE_FIT_DIGEST,
        )

    def test_v2_shard_and_normalization_round_trip(self) -> None:
        self.assertEqual(typed.SCHEMA_VERSION, "pet-typed-descriptors-v2")
        self.assertNotEqual(typed.descriptor_schema_digest(), LEGACY_SCHEMA_DIGEST)
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            shard_path = directory / "descriptors.npz"
            normalization_path = directory / "normalization.npz"
            typed.save_descriptor_shard(shard_path, self.batch, _shard_provenance())
            typed.save_frozen_normalization(normalization_path, self.normalization)
            recovered, provenance = typed.load_descriptor_shard(shard_path)
            normalization = typed.load_frozen_normalization(normalization_path)
        self.assertEqual(provenance, _shard_provenance())
        self.assertEqual(normalization.schema_digest, typed.descriptor_schema_digest())
        for field_name, masks in self.batch.families["prongs"].masks.items():
            np.testing.assert_array_equal(
                recovered.families["prongs"].masks[field_name], masks
            )

    def test_legacy_shard_version_is_rejected(self) -> None:
        stored = typed.descriptor_shard_arrays(self.batch, _shard_provenance())
        stored["schema_version"] = np.asarray(LEGACY_SCHEMA_VERSION)
        stored["schema_digest"] = np.asarray(LEGACY_SCHEMA_DIGEST)
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "legacy-descriptors.npz"
            np.savez(path, **stored)
            with self.assertRaisesRegex(ValueError, "Unsupported.*schema version"):
                typed.load_descriptor_shard(path)

    def test_legacy_shard_digest_is_rejected_under_current_version(self) -> None:
        stored = typed.descriptor_shard_arrays(self.batch, _shard_provenance())
        stored["schema_digest"] = np.asarray(LEGACY_SCHEMA_DIGEST)
        with self.assertRaisesRegex(ValueError, "schema digest does not match"):
            typed.descriptor_batch_from_arrays(stored)

    def test_legacy_normalization_metadata_is_rejected(self) -> None:
        cases = (
            ("schema_version", LEGACY_SCHEMA_VERSION, "Unsupported.*schema version"),
            ("schema_digest", LEGACY_SCHEMA_DIGEST, "schema digest does not match"),
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            current_path = directory / "current-normalization.npz"
            legacy_path = directory / "legacy-normalization.npz"
            typed.save_frozen_normalization(current_path, self.normalization)
            for field_name, legacy_value, error_pattern in cases:
                with self.subTest(field=field_name):
                    with np.load(current_path, allow_pickle=False) as archive:
                        stored = {name: archive[name] for name in archive.files}
                    stored[field_name] = np.asarray(legacy_value)
                    np.savez(legacy_path, **stored)
                    with self.assertRaisesRegex(ValueError, error_pattern):
                        typed.load_frozen_normalization(legacy_path)

    def test_legacy_digest_in_keras_normalization_config_is_rejected(self) -> None:
        config = keras_adapter.frozen_normalization_to_config(self.normalization)
        config["schema_digest"] = LEGACY_SCHEMA_DIGEST
        with self.assertRaisesRegex(ValueError, "schema digest does not match"):
            keras_adapter.frozen_normalization_from_config(config)


class TypedDescriptorKerasCompatibilityTest(unittest.TestCase):
    """Exercise stale schema rejection through native model restoration."""

    @classmethod
    def setUpClass(cls) -> None:
        try:
            tf = keras_adapter.require_tensorflow()
        except ImportError as error:
            raise unittest.SkipTest(str(error)) from error
        tf.config.set_visible_devices([], "GPU")

    def setUp(self) -> None:
        batch, _, event_block, _ = _synthetic_fixture()
        normalization = typed.fit_frozen_normalization_for_smoke(
            batch,
            fit_inventory_row_selection_digest=SMOKE_FIT_DIGEST,
        )
        self.inputs = keras_adapter.prepare_keras_inputs(batch, event_block)
        self.model = keras_adapter.build_keras_typed_descriptor_adapter(
            normalization, hidden_units=(4,), token_embedding_dim=2
        )
        self.output = np.asarray(self.model(self.inputs, training=False))

    def test_legacy_digest_in_model_config_is_rejected(self) -> None:
        config = self.model.get_config()
        config["normalization_config"]["schema_digest"] = LEGACY_SCHEMA_DIGEST
        with self.assertRaisesRegex(
            (TypeError, ValueError), "schema digest does not match"
        ):
            type(self.model).from_config(config)

    def test_saved_model_with_legacy_digest_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            current_path = directory / "current-adapter.keras"
            legacy_path = directory / "legacy-adapter.keras"
            self.model.save(current_path)
            recovered = keras_adapter.load_keras_typed_descriptor_adapter(current_path)
            np.testing.assert_array_equal(
                self.output, np.asarray(recovered(self.inputs, training=False))
            )
            with (
                zipfile.ZipFile(current_path) as source,
                zipfile.ZipFile(legacy_path, "w") as destination,
            ):
                for member in source.infolist():
                    payload = source.read(member.filename)
                    if member.filename == "config.json":
                        config = json.loads(payload)
                        normalization_config = config["config"]["normalization_config"]
                        normalization_config["schema_digest"] = LEGACY_SCHEMA_DIGEST
                        payload = json.dumps(config).encode("utf-8")
                    destination.writestr(member, payload)
            with self.assertRaisesRegex(
                (TypeError, ValueError), "schema digest does not match"
            ):
                keras_adapter.load_keras_typed_descriptor_adapter(legacy_path)


if __name__ == "__main__":
    unittest.main()
