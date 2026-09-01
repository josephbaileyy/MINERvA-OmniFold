"""Focused tests for the fixed PET real-row source-to-contract smoke."""

from __future__ import annotations

import hashlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


ND_ROOT = Path(__file__).resolve().parents[1]
PET_ROOT = ND_ROOT / "pet"
if str(PET_ROOT) not in sys.path:
    sys.path.insert(0, str(PET_ROOT))

import dump_pointcloud_inputs as current_dump  # noqa: E402
import fullevent_fps_dataloader as current_loader  # noqa: E402
import typed_descriptor_source_smoke as smoke  # noqa: E402
import typed_descriptors as typed  # noqa: E402


class FakeFixedReader:
    """Record every requested entry and expose deterministic branch mappings."""

    source_uuid = "fake-source-uuid"

    def __init__(self, records: list[dict[str, object]]) -> None:
        self.records = records
        self.accessed_entries: list[int] = []

    def read_entry(self, entry: int) -> dict[str, object]:
        self.accessed_entries.append(entry)
        return self.records[entry]


def _raw_entry(entry: int) -> dict[str, object]:
    cluster_count = 15
    raw: dict[str, object] = {
        "ev_run": 10068,
        "ev_subrun": 4,
        "ev_gate": 1000 + entry,
        "MasterAnaDev_leptonE": [300.0, 400.0, 2500.0, 2600.0],
        "MasterAnaDev_minos_trk_p": 1500.0,
        "muon_thetaX": 0.1,
        "muon_thetaY": -0.2,
        "isMinosMatchTrack": 1,
        "MasterAnaDev_minos_trk_is_ok": 1,
        "MasterAnaDev_minos_trk_qp": -0.0004,
        "vtx": [10.0, -20.0, 6000.0, 0.0],
        "cluster_energy": [float(index + 1) for index in range(cluster_count)],
        "cluster_pos": [float(10 * index) for index in range(cluster_count)],
        "cluster_z": [float(5000 + index) for index in range(cluster_count)],
        "cluster_view": [index % 3 + 1 for index in range(cluster_count)],
        "cluster_time": [float(-20 + index) for index in range(cluster_count)],
        "cluster_isMuontrack": [
            1 if index in (2, 7) else 0 for index in range(cluster_count)
        ],
        "n_prongs": 3,
        "prong_part_pos": [
            [1.0, 2.0, 3.0, 4.0],
            [5.0, -999.0, 7.0, 8.0],
            [9.0, 10.0, 11.0, 12.0],
        ],
        "prong_part_E": [
            [10.0, 20.0, 30.0, 40.0],
            [50.0, 60.0, -999.0, 80.0],
            [90.0, 100.0, 110.0, 120.0],
        ],
        "prong_part_score": [0.1, 0.2, 0.3],
        "prong_part_mass": [100.0, 200.0, 300.0],
        "prong_part_charge": [1, -999, -1],
        "prong_part_pid": [0, 9, 13],
        "prong_dEdXMean": [-999.0, 2.0, 3.0],
    }
    for name in smoke.GENERIC_VALUE_BRANCHES:
        raw[f"{name}_sz"] = cluster_count

    for photon_index, presence_energy in ((1, 100.0), (2, -999.0)):
        raw[f"gamma{photon_index}_E"] = presence_energy
        raw[f"gamma{photon_index}_direction"] = (
            [0.1, -999.0, 0.9]
            if photon_index == 1 and entry == 0
            else [0.1, 0.2, 0.9]
        )
        raw[f"gamma{photon_index}_dEdx"] = -999.0 if entry == 0 else 3.0
        raw[f"gamma{photon_index}_time"] = 12.0
        for suffix, value in (
            ("energy_trkr", 20.0),
            ("energy_ecal", 30.0),
            ("energy_hcal", 5.0),
            ("energy_scal_X", 2.0),
            ("energy_scal_UV", 3.0),
            ("evis_trkr", 18.0),
            ("evis_ecal", 27.0),
            ("evis_hcal", 4.0),
            ("evis_scal_X", 1.0),
            ("evis_scal_UV", 2.0),
        ):
            raw[f"gamma{photon_index}_{suffix}"] = value

    blob_values = {
        "MasterAnaDev_BlobX": [1.0, 2.0],
        "MasterAnaDev_BlobY": [3.0, 4.0],
        "MasterAnaDev_BlobZ": [5001.0, 5002.0],
        "MasterAnaDev_BlobT": [10.0, -999.0],
        "MasterAnaDev_BlobTPos": [0.5, 0.7],
        "MasterAnaDev_BlobTotalE": [50.0, 75.0],
        "MasterAnaDev_BlobIs3D": [1, 0],
        "MasterAnaDev_BlobNClusters": [3, 5],
    }
    for name, values in blob_values.items():
        raw[name] = values
        raw[f"{name}_sz"] = len(values)
    return raw


def _records() -> list[dict[str, object]]:
    return [_raw_entry(entry) for entry in smoke.FIXED_ENTRIES]


def _spec(role: str, ordinal: int) -> smoke.FixedSourceSpec:
    return smoke.FixedSourceSpec(
        role=role,
        role_code=smoke.ROLE_DATA if role == "data" else smoke.ROLE_MC,
        playlist="1B" if role == "data" else "1A",
        manifest_relative_path=f"manifest/{role}.txt",
        expected_basename=f"{role}.root",
        shard_file_ordinal=ordinal,
    )


def _shard() -> typed.ShardProvenance:
    return typed.ShardProvenance(
        manifest_sha256=hashlib.sha256(b"fixed source smoke").hexdigest(),
        playlist="fixed source smoke",
        production_provenance=(("purpose", "unit test"),),
        source_files=(
            typed.SourceFileMetadata(1, "manifest/data.root", "uuid-data"),
            typed.SourceFileMetadata(2, "manifest/mc.root", "uuid-mc"),
        ),
    )


class FixedSourceMappingTest(unittest.TestCase):
    """Prove the mapper retains current generic/event bytes and typed semantics."""

    def setUp(self) -> None:
        self.records = _records()
        self.reader = FakeFixedReader(self.records)
        self.batch = smoke.build_fixed_source_batch(
            self.reader, _spec("data", 1)
        )

    def test_accesses_exactly_entries_zero_through_fifteen_once(self) -> None:
        self.assertEqual(self.reader.accessed_entries, list(range(16)))
        np.testing.assert_array_equal(
            self.batch.descriptors.provenance.source_entry, np.arange(16)
        )
        self.assertEqual(self.batch.row_count, 16)

    def test_generic_p12_matches_current_joint_padding_byte_for_byte(self) -> None:
        raw = self.records[0]
        keep = [
            index
            for index, flag in enumerate(raw["cluster_isMuontrack"])
            if flag == 0
        ]
        columns = [
            [raw[name][index] for index in keep]
            for name in (
                "cluster_energy",
                "cluster_pos",
                "cluster_z",
                "cluster_view",
                "cluster_time",
            )
        ]
        cloud, view, time = current_dump.pad_reco_cloud_tokens(
            *columns, smoke.P12_TOKEN_COUNT
        )
        current = np.column_stack([cloud, view, time]).astype(np.float32)
        self.assertEqual(current.tobytes(), self.batch.p12_clusters[0].tobytes())

    def test_event_block_matches_current_loader_byte_for_byte(self) -> None:
        raw = self.records[0]
        momentum, magnitude, theta, phi = smoke._current_cv_muon(raw)
        scalars = np.asarray(
            [[
                magnitude * np.sin(theta) / 1000.0,
                magnitude * np.cos(theta) / 1000.0,
            ]],
            dtype=np.float32,
        )
        muon = np.asarray(
            [[*momentum, phi, raw["MasterAnaDev_minos_trk_qp"], 1.0]],
            dtype=np.float32,
        )
        vertex = np.asarray([raw["vtx"][:3]], dtype=np.float32)
        current = current_loader._event_block(
            current_loader.evt_blocks(
                scalars=scalars,
                muon=muon,
                vertex=vertex,
            ),
            current_loader.DEFAULT_EVT_FEATURES,
            None,
        )
        self.assertEqual(
            current[0].tobytes(), self.batch.detector_event_block[0].tobytes()
        )

    def test_mapping_keeps_raw_semantics_and_independent_masks(self) -> None:
        photon_fields = set(self.batch.descriptors.families["photons"].values)
        blob_fields = set(self.batch.descriptors.families["blobs"].values)
        self.assertNotIn("energy", photon_fields)
        self.assertNotIn("four_momentum", blob_fields)

        photons = self.batch.descriptors.families["photons"]
        self.assertEqual(photons.counts[0], 1)
        self.assertFalse(np.any(photons.masks["direction"][0]))
        self.assertFalse(photons.masks["dedx"][0, 0])
        self.assertTrue(photons.masks["time"][0, 0])

        prongs = self.batch.descriptors.families["prongs"]
        first_start = int(prongs.offsets[0])
        first_stop = int(prongs.offsets[1])
        np.testing.assert_array_equal(
            prongs.values["raw_pid"][first_start:first_stop, 0], [0, 9, 13]
        )
        self.assertTrue(prongs.token_mask[first_start])
        self.assertFalse(prongs.masks["dedx"][first_start, 0])

    def test_count_mismatch_and_missing_branch_fail_closed(self) -> None:
        bad_count = _records()
        bad_count[4]["cluster_time_sz"] = 14
        with self.assertRaisesRegex(ValueError, "cluster_time length"):
            smoke.build_fixed_source_batch(
                FakeFixedReader(bad_count), _spec("data", 1)
            )

        missing = _records()
        del missing[2]["gamma1_time"]
        with self.assertRaisesRegex(ValueError, "branch mapping mismatch"):
            smoke.build_fixed_source_batch(
                FakeFixedReader(missing), _spec("data", 1)
            )

    def test_nonfinite_event_output_and_wrong_prong_width_fail_closed(self) -> None:
        nonfinite = _records()
        nonfinite[3]["muon_thetaX"] = np.nan
        with self.assertRaisesRegex(ValueError, "non-finite transformed"):
            smoke.build_fixed_source_batch(
                FakeFixedReader(nonfinite), _spec("data", 1)
            )

        wrong_width = _records()
        wrong_width[5]["prong_part_E"][1] = [1.0, 2.0, 3.0]
        with self.assertRaisesRegex(ValueError, "width four"):
            smoke.build_fixed_source_batch(
                FakeFixedReader(wrong_width), _spec("data", 1)
            )


class FixedSourceRoundTripTest(unittest.TestCase):
    """Exercise collation, one atomic artifact, reload, and the CPU reference."""

    def test_collated_round_trip_and_mc_only_smoke_normalization(self) -> None:
        data = smoke.build_fixed_source_batch(
            FakeFixedReader(_records()), _spec("data", 1)
        )
        mc_records = _records()
        for record in mc_records:
            record["gamma1_energy_ecal"] = 130.0
        mc = smoke.build_fixed_source_batch(
            FakeFixedReader(mc_records), _spec("mc", 2)
        )
        combined = smoke.collate_source_batches([data, mc])
        self.assertEqual(combined.row_count, 32)
        np.testing.assert_array_equal(
            combined.source_role,
            np.asarray([smoke.ROLE_DATA] * 16 + [smoke.ROLE_MC] * 16),
        )

        fit_digest = hashlib.sha256(b"fixed MC rows only").hexdigest()
        normalization = typed.fit_frozen_normalization_for_smoke(
            mc.descriptors,
            fit_inventory_row_selection_digest=fit_digest,
        )
        self.assertEqual(
            normalization.families["photons"].means["energy_ecal"][0],
            np.float32(130.0),
        )
        encoder = typed.ReferenceTypedDescriptorEncoder.initialize(
            normalization, projection_dim=4, seed=7
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "same-row-smoke.npz"
            smoke.save_source_contract_shard(path, combined, _shard())
            self.assertEqual([item.name for item in path.parent.iterdir()], [path.name])
            loaded, loaded_shard = smoke.load_source_contract_shard(path)

        self.assertEqual(loaded_shard, _shard())
        self.assertEqual(
            combined.p12_clusters.tobytes(), loaded.p12_clusters.tobytes()
        )
        self.assertEqual(
            combined.detector_event_block.tobytes(),
            loaded.detector_event_block.tobytes(),
        )
        output = encoder.forward(
            loaded.descriptors, loaded.detector_event_block
        )
        self.assertTrue(
            np.all(np.isfinite(output.conditioned_detector_event_features))
        )

    def test_collation_rejects_duplicate_compact_provenance(self) -> None:
        first = smoke.build_fixed_source_batch(
            FakeFixedReader(_records()), _spec("data", 1)
        )
        duplicate = smoke.build_fixed_source_batch(
            FakeFixedReader(_records()), _spec("mc", 1)
        )
        with self.assertRaisesRegex(ValueError, "must be unique"):
            smoke.collate_source_batches([first, duplicate])

    def test_manifest_resolution_uses_only_first_committed_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for spec in smoke.FIXED_SOURCES:
                manifest = root / spec.manifest_relative_path
                manifest.parent.mkdir(parents=True, exist_ok=True)
                manifest.write_text(
                    f"/routed/{spec.expected_basename}\n/not/read/other.root\n",
                    encoding="utf-8",
                )
            resolved = smoke.resolve_fixed_sources(root)
            provenance = smoke._shard_provenance(
                resolved, {"data": "uuid-data", "mc": "uuid-mc"}
            )
        self.assertEqual(
            [Path(source.path).name for source in resolved],
            [spec.expected_basename for spec in smoke.FIXED_SOURCES],
        )
        self.assertEqual(
            provenance.production_provenance,
            tuple(sorted(provenance.production_provenance)),
        )


if __name__ == "__main__":
    unittest.main()
