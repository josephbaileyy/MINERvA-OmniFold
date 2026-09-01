"""Synthetic-only tests for the PET typed-descriptor interface."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

import numpy as np


ND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PET_ROOT = os.path.join(ND_ROOT, "pet")
if PET_ROOT not in sys.path:
    sys.path.insert(0, PET_ROOT)

import typed_descriptors as typed  # noqa: E402


SMOKE_FIT_DIGEST = "b" * 64


def _photon(index: int, *, sentinel_pattern: bool = False) -> dict[str, object]:
    base = float(index + 1)
    return {
        "direction": [
            0.1 * base,
            -999.0 if sentinel_pattern else -0.2 * base,
            0.9,
        ],
        "dedx": -999.0 if sentinel_pattern else 2.0 + base,
        "time": 10.0 + base,
        "energy_tracker": 20.0 + base,
        "energy_ecal": 30.0 + base,
        "energy_hcal": -9999.0 if sentinel_pattern else 5.0 + base,
        "energy_scal_x": 2.0 + base,
        "energy_scal_uv": 3.0 + base,
        "evis_tracker": 18.0 + base,
        "evis_ecal": 27.0 + base,
        "evis_hcal": 4.0 + base,
        "evis_scal_x": 1.0 + base,
        "evis_scal_uv": 2.0 + base,
    }


def _blob(index: int, *, sentinel_pattern: bool = False) -> dict[str, object]:
    base = float(index + 1)
    return {
        "position": [
            base,
            -999.0 if sentinel_pattern else -2.0 * base,
            5000.0 + base,
        ],
        "time": 5.0 + base,
        "time_position": None if sentinel_pattern else 0.5 * base,
        "total_energy": 10.0 + base,
        "is_3d": index % 2,
        "cluster_count": -999.0 if sentinel_pattern else float(index % 7 + 1),
    }


def _prong(
    index: int,
    raw_pid: int,
    *,
    sentinel_pattern: bool = False,
) -> dict[str, object]:
    base = float(index + 1)
    return {
        "position": [base, -999.0 if sentinel_pattern else -base, 6000.0 + base],
        "time": -999.0 if sentinel_pattern else 20.0 + base,
        "four_momentum": [
            10.0 * base,
            5.0 * base,
            -999.0 if sentinel_pattern else 30.0 * base,
            50.0 * base,
        ],
        "dedx": -999.0 if sentinel_pattern else 1.5 * base,
        "score": 0.1 * base,
        "mass": 100.0 + base,
        "charge": -999.0 if sentinel_pattern else (-1 if index % 2 else 1),
        "raw_pid": raw_pid,
    }


def _synthetic_fixture(
    *,
    family_enabled: dict[str, np.ndarray] | None = None,
) -> tuple[typed.TypedDescriptorBatch, np.ndarray, np.ndarray, np.ndarray]:
    provenance = typed.RowProvenance(
        source_file_ordinal=np.asarray([1, 1, 2], dtype=np.uint32),
        source_tree=np.asarray(
            [
                typed.SourceTree.TRUTH,
                typed.SourceTree.MASTER_ANA_DEV,
                typed.SourceTree.MASTER_ANA_DEV,
            ],
            dtype=np.uint8,
        ),
        source_entry=np.asarray([7, 8, 9], dtype=np.uint64),
    )

    photon_rows = [
        [],
        [_photon(0, sentinel_pattern=True)],
        [_photon(1), _photon(2, sentinel_pattern=True)],
    ]
    blob_rows = [
        [],
        [_blob(0, sentinel_pattern=True), _blob(1)],
        [_blob(index, sentinel_pattern=index == 17) for index in range(90)],
    ]
    raw_pids = [0, 3, 8, 9, 13, -999]
    prong_rows = [
        [],
        [_prong(0, 3, sentinel_pattern=True), _prong(1, 8)],
        [
            _prong(index, raw_pid, sentinel_pattern=index in (1, 5))
            for index, raw_pid in enumerate(raw_pids)
        ],
    ]
    batch = typed.build_descriptor_batch(
        provenance=provenance,
        photon_rows=photon_rows,
        blob_rows=blob_rows,
        prong_rows=prong_rows,
        family_enabled=family_enabled,
    )

    generator = np.random.default_rng(41)
    p12_clusters = generator.normal(size=(3, 12, 5)).astype(np.float32)
    detector_event_block = generator.normal(
        size=(3, typed.DETECTOR_EVENT_WIDTH)
    ).astype(np.float32)
    truth_event_block = generator.normal(
        size=(3, typed.TRUTH_EVENT_WIDTH)
    ).astype(np.float32)
    return batch, p12_clusters, detector_event_block, truth_event_block


def _initialize_smoke_encoder(
    batch: typed.TypedDescriptorBatch,
    *,
    projection_dim: int,
    seed: int,
) -> tuple[typed.ReferenceTypedDescriptorEncoder, typed.FrozenNormalization]:
    return typed.ReferenceTypedDescriptorEncoder.initialize_for_smoke(
        batch,
        fit_inventory_row_selection_digest=SMOKE_FIT_DIGEST,
        projection_dim=projection_dim,
        seed=seed,
    )


def _shard_provenance() -> typed.ShardProvenance:
    return typed.ShardProvenance(
        manifest_sha256="a" * 64,
        playlist="1A",
        production_provenance=(
            ("producer_commit", "0123456789abcdef"),
            ("schema", typed.SCHEMA_VERSION),
        ),
        source_files=(
            typed.SourceFileMetadata(1, "source/playlist/file-1.root", "uuid-1"),
            typed.SourceFileMetadata(2, "source/playlist/file-2.root", "uuid-2"),
        ),
    )


def _assert_family_equal(
    test_case: unittest.TestCase,
    left: typed.RaggedFamilyBatch,
    right: typed.RaggedFamilyBatch,
) -> None:
    test_case.assertEqual(left.name, right.name)
    for attribute in ("offsets", "counts", "enabled", "token_mask"):
        np.testing.assert_array_equal(
            getattr(left, attribute), getattr(right, attribute)
        )
    test_case.assertEqual(set(left.values), set(right.values))
    for field_name in left.values:
        np.testing.assert_array_equal(left.values[field_name], right.values[field_name])
        np.testing.assert_array_equal(left.masks[field_name], right.masks[field_name])


def _replace_family(
    batch: typed.TypedDescriptorBatch,
    family: typed.RaggedFamilyBatch,
) -> typed.TypedDescriptorBatch:
    families = dict(batch.families)
    families[family.name] = family
    return typed.TypedDescriptorBatch(provenance=batch.provenance, families=families)


def _reverse_within_rows(
    family: typed.RaggedFamilyBatch,
) -> typed.RaggedFamilyBatch:
    order_parts = []
    for row_index in range(family.row_count):
        start, stop = family.offsets[row_index : row_index + 2]
        order_parts.append(np.arange(stop - 1, start - 1, -1, dtype=np.int64))
    order = np.concatenate(order_parts) if order_parts else np.zeros(0, dtype=np.int64)
    return replace(
        family,
        token_mask=family.token_mask[order],
        values={
            field_name: values[order]
            for field_name, values in family.values.items()
        },
        masks={field_name: masks[order] for field_name, masks in family.masks.items()},
    )


class TypedDescriptorRoundTripTest(unittest.TestCase):
    """Exercise the complete synthetic descriptor boundary."""

    def setUp(self) -> None:
        (
            self.batch,
            self.p12_clusters,
            self.detector_event_block,
            self.truth_event_block,
        ) = _synthetic_fixture()

    def test_raw_contract_avoids_disallowed_interpretations(self) -> None:
        photon_fields = {field.name for field in typed.PHOTON_CONTRACT.fields}
        blob_fields = {field.name for field in typed.BLOB_CONTRACT.fields}
        self.assertNotIn("energy", photon_fields)
        self.assertTrue(
            {
                "energy_tracker",
                "energy_ecal",
                "energy_hcal",
                "energy_scal_x",
                "energy_scal_uv",
                "evis_tracker",
                "evis_ecal",
                "evis_hcal",
                "evis_scal_x",
                "evis_scal_uv",
            }.issubset(photon_fields)
        )
        self.assertNotIn("four_momentum", blob_fields)
        raw_pid = next(
            field for field in typed.PRONG_CONTRACT.fields if field.name == "raw_pid"
        )
        self.assertEqual(raw_pid.categories, (0, 3, 8, 9, 13))
        self.assertIn("uninterpreted", raw_pid.unit)

    def test_exact_serialization_masks_and_provenance_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = os.path.join(temporary_directory, "typed.npz")
            shard = _shard_provenance()
            typed.save_descriptor_shard(path, self.batch, shard)
            recovered, recovered_shard = typed.load_descriptor_shard(path)

        self.assertEqual(shard, recovered_shard)
        np.testing.assert_array_equal(
            self.batch.provenance.source_file_ordinal,
            recovered.provenance.source_file_ordinal,
        )
        np.testing.assert_array_equal(
            self.batch.provenance.source_tree,
            recovered.provenance.source_tree,
        )
        np.testing.assert_array_equal(
            self.batch.provenance.source_entry,
            recovered.provenance.source_entry,
        )
        for family_name in typed.CONTRACT_BY_NAME:
            _assert_family_equal(
                self,
                self.batch.families[family_name],
                recovered.families[family_name],
            )

    def test_shard_write_is_atomic_on_failure(self) -> None:
        def fail_after_partial_write(path: str, **_arrays: np.ndarray) -> None:
            with open(path, "wb") as partial:
                partial.write(b"PK\x03\x04partial")
            raise RuntimeError("synthetic interrupted write")

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = os.path.join(temporary_directory, "typed.npz")
            typed.save_descriptor_shard(path, self.batch, _shard_provenance())
            original = Path(path).read_bytes()
            with mock.patch(
                "atomic_write.np.savez_compressed",
                side_effect=fail_after_partial_write,
            ):
                with self.assertRaisesRegex(RuntimeError, "interrupted"):
                    typed.save_descriptor_shard(
                        path, self.batch, _shard_provenance()
                    )
            self.assertEqual(Path(path).read_bytes(), original)
            self.assertFalse(
                any(
                    name.startswith(".atomic_")
                    for name in os.listdir(temporary_directory)
                )
            )

            absent_path = os.path.join(temporary_directory, "absent.npz")
            with mock.patch(
                "atomic_write.np.savez_compressed",
                side_effect=fail_after_partial_write,
            ):
                with self.assertRaisesRegex(RuntimeError, "interrupted"):
                    typed.save_descriptor_shard(
                        absent_path, self.batch, _shard_provenance()
                    )
            self.assertFalse(os.path.exists(absent_path))

    def test_duplicate_compact_provenance_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be unique"):
            typed.RowProvenance(
                source_file_ordinal=np.asarray([1, 1], dtype=np.uint32),
                source_tree=np.asarray(
                    [typed.SourceTree.MASTER_ANA_DEV] * 2, dtype=np.uint8
                ),
                source_entry=np.asarray([4, 4], dtype=np.uint64),
            )

    def test_a11_add_leaves_p12_and_event_block_byte_identical(self) -> None:
        a00_p12 = self.p12_clusters.copy()
        a00_event = self.detector_event_block.copy()
        a11_add = {
            "p12_clusters": self.p12_clusters.copy(),
            "event_block": self.detector_event_block.copy(),
            "typed_descriptors": self.batch,
        }
        self.assertEqual(a00_p12.tobytes(), a11_add["p12_clusters"].tobytes())
        self.assertEqual(a00_event.tobytes(), a11_add["event_block"].tobytes())
        self.assertEqual(a00_p12.dtype, a11_add["p12_clusters"].dtype)
        self.assertEqual(a00_event.dtype, a11_add["event_block"].dtype)

    def test_normalization_is_explicit_frozen_and_persisted(self) -> None:
        encoder, normalization = _initialize_smoke_encoder(
            self.batch, projection_dim=7, seed=17
        )
        self.assertEqual(
            normalization.schema_digest, typed.descriptor_schema_digest()
        )
        self.assertEqual(
            normalization.fit_inventory_row_selection_digest, SMOKE_FIT_DIGEST
        )
        self.assertEqual(
            normalization.fitting_policy,
            typed.SMOKE_NORMALIZATION_FITTING_POLICY,
        )
        production_policy = typed.PRODUCTION_NORMALIZATION_FITTING_POLICY
        self.assertIn("training reco-MC pass_reco rows only", production_policy)
        for reuse_target in ("data", "validation", "inference", "controls"):
            self.assertIn(reuse_target, production_policy)

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = os.path.join(temporary_directory, "normalization.npz")
            typed.save_frozen_normalization(path, normalization)
            recovered = typed.load_frozen_normalization(path)
        self.assertEqual(recovered.schema_digest, normalization.schema_digest)
        self.assertEqual(
            recovered.fit_inventory_row_selection_digest,
            normalization.fit_inventory_row_selection_digest,
        )
        self.assertEqual(recovered.fitting_policy, normalization.fitting_policy)
        for family_name in typed.CONTRACT_BY_NAME:
            for field_name in normalization.families[family_name].means:
                np.testing.assert_array_equal(
                    recovered.families[family_name].means[field_name],
                    normalization.families[family_name].means[field_name],
                )
                np.testing.assert_array_equal(
                    recovered.families[family_name].scales[field_name],
                    normalization.families[family_name].scales[field_name],
                )

        explicit = typed.ReferenceTypedDescriptorEncoder.initialize(
            recovered, projection_dim=7, seed=17
        )
        expected = encoder.forward(self.batch, self.detector_event_block)
        observed = explicit.forward(self.batch, self.detector_event_block)
        np.testing.assert_array_equal(
            expected.typed_embedding, observed.typed_embedding
        )

    def test_normalization_uses_only_valid_components(self) -> None:
        family = self.batch.families["photons"]
        _, frozen = _initialize_smoke_encoder(
            self.batch, projection_dim=7, seed=18
        )
        normalization = frozen.families["photons"]
        values = family.values["energy_hcal"][:, 0]
        valid = family.masks["energy_hcal"][:, 0] & family.token_mask
        self.assertAlmostEqual(
            float(normalization.means["energy_hcal"][0]),
            float(values[valid].mean()),
        )

        original_features = typed.PHOTON_CONTRACT.prepare_features(
            family, normalization
        )
        changed_values = {
            field_name: field_values.copy()
            for field_name, field_values in family.values.items()
        }
        invalid = ~family.masks["energy_hcal"][:, 0]
        changed_values["energy_hcal"][invalid, 0] = np.float32(1.0e30)
        changed_family = replace(family, values=changed_values)
        changed_features = typed.PHOTON_CONTRACT.prepare_features(
            changed_family, normalization
        )
        np.testing.assert_array_equal(original_features, changed_features)

    def test_masked_values_cannot_change_the_pooled_representation(self) -> None:
        encoder, _ = _initialize_smoke_encoder(
            self.batch, projection_dim=7, seed=19
        )
        before = encoder.forward(self.batch, self.detector_event_block)

        family = self.batch.families["prongs"]
        changed_values = {
            field_name: field_values.copy()
            for field_name, field_values in family.values.items()
        }
        invalid = ~family.masks["dedx"]
        changed_values["dedx"][invalid] = np.float32(-1.0e25)
        changed_batch = _replace_family(
            self.batch, replace(family, values=changed_values)
        )
        after = encoder.forward(changed_batch, self.detector_event_block)
        np.testing.assert_array_equal(
            before.family_embeddings["prongs"], after.family_embeddings["prongs"]
        )

    def test_blob_and_prong_pooling_are_permutation_invariant(self) -> None:
        encoder, _ = _initialize_smoke_encoder(
            self.batch, projection_dim=6, seed=23
        )
        reference = encoder.forward(self.batch, self.detector_event_block)
        permuted = self.batch
        for family_name in ("blobs", "prongs"):
            permuted = _replace_family(
                permuted, _reverse_within_rows(permuted.families[family_name])
            )
        observed = encoder.forward(permuted, self.detector_event_block)
        for family_name in ("blobs", "prongs"):
            np.testing.assert_allclose(
                reference.family_embeddings[family_name],
                observed.family_embeddings[family_name],
                rtol=1.0e-6,
                atol=1.0e-6,
            )

    def test_explicit_counts_recover_uncapped_multiplicity(self) -> None:
        expected = {
            "photons": np.asarray([0, 1, 2]),
            "blobs": np.asarray([0, 2, 90]),
            "prongs": np.asarray([0, 2, 6]),
        }
        for family_name, expected_counts in expected.items():
            np.testing.assert_array_equal(
                self.batch.families[family_name].counts, expected_counts
            )
            self.assertEqual(
                self.batch.families[family_name].offsets[-1],
                int(expected_counts.sum()),
            )

    def test_family_disable_mask_produces_the_null_embedding(self) -> None:
        enabled = {
            family_name: np.asarray([True, False, True], dtype=np.bool_)
            for family_name in typed.CONTRACT_BY_NAME
        }
        disabled_batch, _, detector_event_block, _ = _synthetic_fixture(
            family_enabled=enabled
        )
        encoder, _ = _initialize_smoke_encoder(
            disabled_batch, projection_dim=5, seed=31
        )
        output = encoder.forward(disabled_batch, detector_event_block)
        for family_name in typed.CONTRACT_BY_NAME:
            np.testing.assert_array_equal(
                output.family_embeddings[family_name][1],
                np.zeros(6, dtype=np.float32),
            )
            self.assertGreater(disabled_batch.families[family_name].counts[1], 0)

    def test_prong_presence_is_independent_of_dedx_and_other_masks(self) -> None:
        prongs = self.batch.families["prongs"]
        ordinary_first = int(prongs.offsets[1])
        self.assertTrue(prongs.token_mask[ordinary_first])
        self.assertFalse(prongs.masks["dedx"][ordinary_first, 0])
        self.assertFalse(prongs.masks["time"][ordinary_first, 0])
        self.assertFalse(prongs.masks["charge"][ordinary_first, 0])
        self.assertFalse(np.any(prongs.masks["position"][ordinary_first]))
        self.assertFalse(np.any(prongs.masks["four_momentum"][ordinary_first]))
        self.assertTrue(prongs.masks["score"][ordinary_first, 0])
        self.assertTrue(prongs.masks["mass"][ordinary_first, 0])
        self.assertTrue(prongs.masks["raw_pid"][ordinary_first, 0])

    def test_vector_mask_policy_rejects_partial_sentinel_contamination(self) -> None:
        photons = self.batch.families["photons"]
        blobs = self.batch.families["blobs"]
        prongs = self.batch.families["prongs"]
        photon_index = int(photons.offsets[1])
        blob_index = int(blobs.offsets[1])
        prong_index = int(prongs.offsets[1])

        self.assertFalse(np.any(photons.masks["direction"][photon_index]))
        self.assertFalse(np.any(blobs.masks["position"][blob_index]))
        self.assertFalse(np.any(prongs.masks["position"][prong_index]))
        self.assertFalse(np.any(prongs.masks["four_momentum"][prong_index]))
        self.assertTrue(photons.masks["time"][photon_index, 0])
        self.assertTrue(blobs.masks["total_energy"][blob_index, 0])
        self.assertTrue(prongs.masks["score"][prong_index, 0])
        self.assertTrue(prongs.masks["mass"][prong_index, 0])

    def test_native_miss_has_empty_families_and_no_truth_mutation(self) -> None:
        truth_before = self.truth_event_block.tobytes()
        encoder, _ = _initialize_smoke_encoder(
            self.batch, projection_dim=4, seed=37
        )
        output = encoder.forward(self.batch, self.detector_event_block)
        self.assertEqual(
            int(self.batch.provenance.source_tree[0]), int(typed.SourceTree.TRUTH)
        )
        for family_name in typed.CONTRACT_BY_NAME:
            self.assertEqual(self.batch.families[family_name].counts[0], 0)
            np.testing.assert_array_equal(
                output.family_embeddings[family_name][0],
                np.zeros(5, dtype=np.float32),
            )
        self.assertEqual(truth_before, self.truth_event_block.tobytes())

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = os.path.join(temporary_directory, "typed.npz")
            typed.save_descriptor_shard(path, self.batch, _shard_provenance())
            with np.load(path, allow_pickle=False) as stored:
                self.assertFalse(any(key.startswith("truth.") for key in stored.files))

    def test_raw_pid_codes_and_sentinel_mask_survive(self) -> None:
        prongs = self.batch.families["prongs"]
        stress_start, stress_stop = prongs.offsets[2:4]
        observed = prongs.values["raw_pid"][stress_start:stress_stop, 0]
        np.testing.assert_array_equal(observed, [0, 3, 8, 9, 13, -999])
        observed_mask = prongs.masks["raw_pid"][stress_start:stress_stop, 0]
        np.testing.assert_array_equal(
            observed_mask, [True, True, True, True, True, False]
        )

    def test_one_finite_cpu_forward_appends_film_conditioning(self) -> None:
        event_before = self.detector_event_block.tobytes()
        truth_before = self.truth_event_block.tobytes()
        encoder, _ = _initialize_smoke_encoder(
            self.batch, projection_dim=8, seed=43
        )
        output = encoder.forward(self.batch, self.detector_event_block)
        expected_typed_width = 3 * (8 + 1)
        self.assertEqual(output.typed_embedding.shape, (3, expected_typed_width))
        self.assertEqual(
            output.conditioned_detector_event_features.shape,
            (3, typed.DETECTOR_EVENT_WIDTH + expected_typed_width),
        )
        self.assertTrue(
            np.all(np.isfinite(output.conditioned_detector_event_features))
        )
        self.assertEqual(event_before, self.detector_event_block.tobytes())
        self.assertEqual(
            self.detector_event_block.tobytes(),
            output.conditioned_detector_event_features[
                :, : typed.DETECTOR_EVENT_WIDTH
            ].tobytes(),
        )
        with self.assertRaisesRegex(ValueError, "truth block is not augmented"):
            encoder.forward(self.batch, self.truth_event_block)
        self.assertEqual(truth_before, self.truth_event_block.tobytes())

        head_weight = np.linspace(
            -0.1,
            0.1,
            output.conditioned_detector_event_features.shape[1],
            dtype=np.float32,
        )
        logits = output.conditioned_detector_event_features @ head_weight
        self.assertTrue(np.all(np.isfinite(logits)))


if __name__ == "__main__":
    unittest.main()
