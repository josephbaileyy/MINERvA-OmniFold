#!/usr/bin/env python3
"""Fixed real-row source-to-contract smoke for PET typed descriptors.

This module is deliberately not a production producer. It reads exactly entries
0--15 from two manifest-routed source tuples, builds the existing generic P12
and 13-column detector event representations in the same row operation as the
typed descriptors, and exercises one object-free round trip plus the NumPy CPU
reference encoder. It has no configurable entry range, training path, ROOT scan,
truth-descriptor path, or GPU dependency.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Protocol, Sequence

import numpy as np

from atomic_write import atomic_savez_compressed
import typed_descriptors as typed


SOURCE_SMOKE_SCHEMA_VERSION = "pet-typed-source-smoke-v1"
STARTING_COMMIT = "65e179eb6d7fedc080e58fd0ff13387b41b590a2"
TREE_NAME = "MasterAnaDev"
FIXED_ENTRIES = tuple(range(16))
P12_TOKEN_COUNT = 12
PHOTON_PRESENCE_THRESHOLD = 1.0e-5

ROLE_DATA = np.uint8(1)
ROLE_MC = np.uint8(2)


@dataclass(frozen=True)
class FixedSourceSpec:
    """Manifest-routed identity for one authorized fixed source."""

    role: str
    role_code: np.uint8
    playlist: str
    manifest_relative_path: str
    expected_basename: str
    shard_file_ordinal: int


FIXED_SOURCES = (
    FixedSourceSpec(
        role="data",
        role_code=ROLE_DATA,
        playlist="1B",
        manifest_relative_path="2d-unfolding/playlist_manifests/1B_Data.txt",
        expected_basename=(
            "MasterAnaDev_data_AnaTuple_run00010068_Playlist.root"
        ),
        shard_file_ordinal=1,
    ),
    FixedSourceSpec(
        role="mc",
        role_code=ROLE_MC,
        playlist="1A",
        manifest_relative_path="2d-unfolding/playlist_manifests/1A_MC.txt",
        expected_basename=(
            "MasterAnaDev_mc_AnaTuple_run00110000_Playlist.root"
        ),
        shard_file_ordinal=2,
    ),
)

EVENT_KEY_BRANCHES = ("ev_run", "ev_subrun", "ev_gate")
GENERIC_VALUE_BRANCHES = (
    "cluster_energy",
    "cluster_pos",
    "cluster_z",
    "cluster_view",
    "cluster_time",
    "cluster_isMuontrack",
)
GENERIC_COUNT_BRANCHES = tuple(f"{name}_sz" for name in GENERIC_VALUE_BRANCHES)
EVENT_BRANCHES = (
    "MasterAnaDev_leptonE",
    "MasterAnaDev_minos_trk_p",
    "muon_thetaX",
    "muon_thetaY",
    "isMinosMatchTrack",
    "MasterAnaDev_minos_trk_is_ok",
    "MasterAnaDev_minos_trk_qp",
    "vtx",
)

PHOTON_SCALAR_SUFFIXES = (
    "E",
    "dEdx",
    "time",
    "energy_trkr",
    "energy_ecal",
    "energy_hcal",
    "energy_scal_X",
    "energy_scal_UV",
    "evis_trkr",
    "evis_ecal",
    "evis_hcal",
    "evis_scal_X",
    "evis_scal_UV",
)
PHOTON_SCALAR_BRANCHES = tuple(
    f"gamma{index}_{suffix}"
    for index in (1, 2)
    for suffix in PHOTON_SCALAR_SUFFIXES
)
PHOTON_VECTOR_BRANCHES = tuple(
    f"gamma{index}_direction" for index in (1, 2)
)

BLOB_BASES = (
    "MasterAnaDev_BlobX",
    "MasterAnaDev_BlobY",
    "MasterAnaDev_BlobZ",
    "MasterAnaDev_BlobT",
    "MasterAnaDev_BlobTPos",
    "MasterAnaDev_BlobTotalE",
    "MasterAnaDev_BlobIs3D",
    "MasterAnaDev_BlobNClusters",
)
BLOB_COUNT_BRANCHES = tuple(f"{name}_sz" for name in BLOB_BASES)
PRONG_COUNT_BRANCH = "n_prongs"
PRONG_VECTOR_BRANCHES = (
    "prong_part_score",
    "prong_part_mass",
    "prong_part_charge",
    "prong_part_pid",
    "prong_dEdXMean",
)
PRONG_NESTED_BRANCHES = ("prong_part_pos", "prong_part_E")

REQUIRED_BRANCHES = tuple(
    dict.fromkeys(
        EVENT_KEY_BRANCHES
        + GENERIC_VALUE_BRANCHES
        + GENERIC_COUNT_BRANCHES
        + EVENT_BRANCHES
        + PHOTON_SCALAR_BRANCHES
        + PHOTON_VECTOR_BRANCHES
        + BLOB_BASES
        + BLOB_COUNT_BRANCHES
        + (PRONG_COUNT_BRANCH,)
        + PRONG_VECTOR_BRANCHES
        + PRONG_NESTED_BRANCHES
    )
)

_SCALAR_BRANCHES = set(
    EVENT_KEY_BRANCHES
    + (
        "MasterAnaDev_minos_trk_p",
        "muon_thetaX",
        "muon_thetaY",
        "isMinosMatchTrack",
        "MasterAnaDev_minos_trk_is_ok",
        "MasterAnaDev_minos_trk_qp",
        PRONG_COUNT_BRANCH,
    )
    + PHOTON_SCALAR_BRANCHES
    + GENERIC_COUNT_BRANCHES
    + BLOB_COUNT_BRANCHES
)
_FIXED_WIDTH_BRANCHES = {
    "MasterAnaDev_leptonE": 4,
    "vtx": 4,
    **{name: 3 for name in PHOTON_VECTOR_BRANCHES},
}
_COUNTED_BRANCHES = {
    **{
        name: f"{name}_sz"
        for name in GENERIC_VALUE_BRANCHES
    },
    **{name: f"{name}_sz" for name in BLOB_BASES},
    **{name: PRONG_COUNT_BRANCH for name in PRONG_VECTOR_BRANCHES},
}


class FixedEntryReader(Protocol):
    """Narrow source boundary used by the real reader and synthetic tests."""

    source_uuid: str

    def read_entry(self, entry: int) -> Mapping[str, object]:
        """Read one authorized entry and return only required branch values."""


@dataclass(frozen=True)
class ResolvedSource:
    """A source path resolved from exactly one committed manifest line."""

    spec: FixedSourceSpec
    path: str
    manifest_bytes: bytes


@dataclass(frozen=True)
class SourceContractBatch:
    """Same-row P12, event, typed, event-key, and compact provenance payload."""

    p12_clusters: np.ndarray
    detector_event_block: np.ndarray
    tuple_event_keys: np.ndarray
    source_role: np.ndarray
    descriptors: typed.TypedDescriptorBatch

    def __post_init__(self) -> None:
        rows = self.descriptors.row_count
        if self.p12_clusters.shape != (rows, P12_TOKEN_COUNT, 5):
            raise ValueError("Generic P12 tensor must have shape (rows, 12, 5)")
        if self.p12_clusters.dtype != np.dtype(np.float32):
            raise ValueError("Generic P12 tensor must retain float32 storage")
        if self.detector_event_block.shape != (rows, typed.DETECTOR_EVENT_WIDTH):
            raise ValueError("Detector event block must have shape (rows, 13)")
        if self.detector_event_block.dtype != np.dtype(np.float32):
            raise ValueError("Detector event block must retain float32 storage")
        if self.tuple_event_keys.shape != (rows, 3):
            raise ValueError("Tuple event-key audit block must have shape (rows, 3)")
        if self.source_role.shape != (rows,):
            raise ValueError("Source-role array must have one value per row")
        if not set(int(value) for value in self.source_role).issubset(
            {int(ROLE_DATA), int(ROLE_MC)}
        ):
            raise ValueError("Source-role array contains an unknown role")
        _require_finite("generic P12", self.p12_clusters)
        _require_finite("detector event block", self.detector_event_block)

    @property
    def row_count(self) -> int:
        """Return the number of aligned detector rows."""

        return self.descriptors.row_count


class PyRootFixedEntryReader:
    """Fail-closed PyROOT reader restricted to the predeclared branches and rows."""

    def __init__(self, source_path: str) -> None:
        import ROOT  # type: ignore[import-not-found]

        self._file = ROOT.TFile.Open(source_path, "READ")
        if not self._file or self._file.IsZombie():
            raise OSError(f"Could not open source ROOT file: {source_path}")
        self._tree = self._file.Get(TREE_NAME)
        if self._tree is None:
            self._file.Close()
            raise ValueError(f"Source file has no {TREE_NAME!r} tree")
        if int(self._tree.GetEntries()) < len(FIXED_ENTRIES):
            self._file.Close()
            raise ValueError("Source tree has fewer than the 16 fixed entries")
        missing = [name for name in REQUIRED_BRANCHES if not self._tree.GetBranch(name)]
        if missing:
            self._file.Close()
            raise ValueError(
                f"Populated source is missing required branches: {missing}"
            )
        self._tree.SetBranchStatus("*", 0)
        for name in REQUIRED_BRANCHES:
            self._tree.SetBranchStatus(name, 1)
        self.source_uuid = str(self._file.GetUUID().AsString())
        self.accessed_entries: list[int] = []

    def close(self) -> None:
        """Close the source file."""

        self._file.Close()

    def read_entry(self, entry: int) -> Mapping[str, object]:
        """Read one fixed entry once, with no adaptive access."""

        if entry not in FIXED_ENTRIES:
            raise ValueError(f"Entry {entry} is outside the fixed 0--15 scope")
        if entry in self.accessed_entries:
            raise ValueError(f"Entry {entry} was requested more than once")
        bytes_read = int(self._tree.GetEntry(entry))
        if bytes_read <= 0:
            raise OSError(f"Could not read fixed entry {entry}")
        self.accessed_entries.append(entry)

        values: dict[str, object] = {}
        for name in _SCALAR_BRANCHES:
            values[name] = _python_scalar(getattr(self._tree, name))
        for name, width in _FIXED_WIDTH_BRANCHES.items():
            values[name] = _fixed_sequence(getattr(self._tree, name), width, name)
        for name, count_name in _COUNTED_BRANCHES.items():
            count = _nonnegative_count(values[count_name], count_name)
            values[name] = _fixed_sequence(getattr(self._tree, name), count, name)
        prong_count = _nonnegative_count(values[PRONG_COUNT_BRANCH], PRONG_COUNT_BRANCH)
        for name in PRONG_NESTED_BRANCHES:
            outer = getattr(self._tree, name)
            if len(outer) != prong_count:
                raise ValueError(
                    f"{name} outer count {len(outer)} != n_prongs {prong_count}"
                )
            values[name] = [
                _fixed_sequence(outer[index], 4, f"{name}[{index}]")
                for index in range(prong_count)
            ]
        return values

    def __enter__(self) -> "PyRootFixedEntryReader":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()


def resolve_fixed_sources(repo_root: str | Path) -> tuple[ResolvedSource, ...]:
    """Resolve exactly the first line of each committed fixed-source manifest."""

    root = Path(repo_root)
    resolved: list[ResolvedSource] = []
    for spec in FIXED_SOURCES:
        manifest_path = root / spec.manifest_relative_path
        manifest_bytes = manifest_path.read_bytes()
        lines = manifest_bytes.decode("utf-8").splitlines()
        if not lines or not lines[0].strip() or lines[0].lstrip().startswith("#"):
            raise ValueError(
                f"Manifest {spec.manifest_relative_path} has no source on line 1"
            )
        source_path = lines[0].strip()
        if Path(source_path).name != spec.expected_basename:
            raise ValueError(
                f"First source in {spec.manifest_relative_path} is not the fixed "
                f"{spec.playlist}/{spec.expected_basename} file"
            )
        resolved.append(
            ResolvedSource(spec=spec, path=source_path, manifest_bytes=manifest_bytes)
        )
    return tuple(resolved)


def build_fixed_source_batch(
    reader: FixedEntryReader,
    spec: FixedSourceSpec,
) -> SourceContractBatch:
    """Map entries 0--15 in one pass to generic, event, and typed contracts."""

    p12_rows: list[np.ndarray] = []
    event_rows: list[np.ndarray] = []
    tuple_event_keys: list[tuple[int, int, int]] = []
    photon_rows: list[list[dict[str, object]]] = []
    blob_rows: list[list[dict[str, object]]] = []
    prong_rows: list[list[dict[str, object]]] = []

    for entry in FIXED_ENTRIES:
        raw = reader.read_entry(entry)
        missing = set(REQUIRED_BRANCHES).difference(raw)
        extra = set(raw).difference(REQUIRED_BRANCHES)
        if missing or extra:
            raise ValueError(
                f"Entry {entry} branch mapping mismatch: "
                f"missing={sorted(missing)}, extra={sorted(extra)}"
            )
        p12_rows.append(_build_p12(raw))
        event_rows.append(_build_detector_event_block(raw))
        tuple_event_keys.append(
            tuple(int(raw[name]) for name in EVENT_KEY_BRANCHES)
        )
        photon_rows.append(_build_photons(raw))
        blob_rows.append(_build_blobs(raw))
        prong_rows.append(_build_prongs(raw))

    provenance = typed.RowProvenance(
        source_file_ordinal=np.full(
            len(FIXED_ENTRIES), spec.shard_file_ordinal, dtype=np.uint32
        ),
        source_tree=np.full(
            len(FIXED_ENTRIES), int(typed.SourceTree.MASTER_ANA_DEV), dtype=np.uint8
        ),
        source_entry=np.asarray(FIXED_ENTRIES, dtype=np.uint64),
    )
    descriptors = typed.build_descriptor_batch(
        provenance=provenance,
        photon_rows=photon_rows,
        blob_rows=blob_rows,
        prong_rows=prong_rows,
    )
    batch = SourceContractBatch(
        p12_clusters=np.stack(p12_rows).astype(np.float32, copy=False),
        detector_event_block=np.stack(event_rows).astype(np.float32, copy=False),
        tuple_event_keys=np.asarray(tuple_event_keys, dtype=np.int64),
        source_role=np.full(len(FIXED_ENTRIES), spec.role_code, dtype=np.uint8),
        descriptors=descriptors,
    )
    for contract in typed.FAMILY_CONTRACTS:
        prepared = contract.prepare_features(
            batch.descriptors.families[contract.name],
            _identity_normalization(contract),
        )
        _require_finite(f"{contract.name} transformed descriptors", prepared)
    return batch


def collate_source_batches(
    batches: Sequence[SourceContractBatch],
) -> SourceContractBatch:
    """Collate aligned source batches without padding or truncating typed families."""

    if not batches:
        raise ValueError("At least one source batch is required")
    provenance = typed.RowProvenance(
        source_file_ordinal=np.concatenate(
            [batch.descriptors.provenance.source_file_ordinal for batch in batches]
        ),
        source_tree=np.concatenate(
            [batch.descriptors.provenance.source_tree for batch in batches]
        ),
        source_entry=np.concatenate(
            [batch.descriptors.provenance.source_entry for batch in batches]
        ),
    )
    families: dict[str, typed.RaggedFamilyBatch] = {}
    for contract in typed.FAMILY_CONTRACTS:
        source_families = [
            batch.descriptors.families[contract.name] for batch in batches
        ]
        offsets = [np.asarray([0], dtype=np.int64)]
        token_base = 0
        for family in source_families:
            offsets.append(family.offsets[1:] + token_base)
            token_base += family.token_count
        families[contract.name] = typed.RaggedFamilyBatch(
            name=contract.name,
            offsets=np.concatenate(offsets),
            counts=np.concatenate([family.counts for family in source_families]),
            enabled=np.concatenate([family.enabled for family in source_families]),
            token_mask=np.concatenate(
                [family.token_mask for family in source_families]
            ),
            values={
                field.name: np.concatenate(
                    [family.values[field.name] for family in source_families], axis=0
                )
                for field in contract.fields
            },
            masks={
                field.name: np.concatenate(
                    [family.masks[field.name] for family in source_families], axis=0
                )
                for field in contract.fields
            },
        )
    descriptors = typed.TypedDescriptorBatch(provenance=provenance, families=families)
    return SourceContractBatch(
        p12_clusters=np.concatenate([batch.p12_clusters for batch in batches]),
        detector_event_block=np.concatenate(
            [batch.detector_event_block for batch in batches]
        ),
        tuple_event_keys=np.concatenate([batch.tuple_event_keys for batch in batches]),
        source_role=np.concatenate([batch.source_role for batch in batches]),
        descriptors=descriptors,
    )


def save_source_contract_shard(
    path: str | Path,
    batch: SourceContractBatch,
    shard_provenance: typed.ShardProvenance,
) -> None:
    """Atomically save P12, event, typed, and alignment audit fields together."""

    destination = Path(path)
    if destination.suffix != ".npz":
        raise ValueError("Fixed source smoke shard path must end in .npz")
    arrays = typed.descriptor_shard_arrays(batch.descriptors, shard_provenance)
    arrays.update(
        {
            "source_smoke.schema_version": np.asarray(SOURCE_SMOKE_SCHEMA_VERSION),
            "source_smoke.starting_commit": np.asarray(STARTING_COMMIT),
            "source_smoke.p12_clusters": batch.p12_clusters,
            "source_smoke.detector_event_block": batch.detector_event_block,
            "source_smoke.tuple_event_keys": batch.tuple_event_keys,
            "source_smoke.source_role": batch.source_role,
        }
    )
    atomic_savez_compressed(str(destination), arrays)


def load_source_contract_shard(
    path: str | Path,
) -> tuple[SourceContractBatch, typed.ShardProvenance]:
    """Load and validate one same-row fixed source smoke shard."""

    with np.load(Path(path), allow_pickle=False) as stored:
        if (
            str(stored["source_smoke.schema_version"].item())
            != SOURCE_SMOKE_SCHEMA_VERSION
        ):
            raise ValueError("Unsupported fixed source smoke schema version")
        if str(stored["source_smoke.starting_commit"].item()) != STARTING_COMMIT:
            raise ValueError("Fixed source smoke starting commit does not match")
        descriptors, shard_provenance = typed.descriptor_batch_from_arrays(stored)
        batch = SourceContractBatch(
            p12_clusters=np.asarray(
                stored["source_smoke.p12_clusters"], dtype=np.float32
            ),
            detector_event_block=np.asarray(
                stored["source_smoke.detector_event_block"], dtype=np.float32
            ),
            tuple_event_keys=np.asarray(
                stored["source_smoke.tuple_event_keys"], dtype=np.int64
            ),
            source_role=np.asarray(stored["source_smoke.source_role"], dtype=np.uint8),
            descriptors=descriptors,
        )
    return batch, shard_provenance


def run_fixed_real_smoke(
    repo_root: str | Path,
    output_path: str | Path,
) -> dict[str, object]:
    """Run the authorized two-file, 32-row source-to-contract smoke."""

    resolved_sources = resolve_fixed_sources(repo_root)
    source_batches: dict[str, SourceContractBatch] = {}
    source_uuids: dict[str, str] = {}
    for source in resolved_sources:
        with PyRootFixedEntryReader(source.path) as reader:
            source_batches[source.spec.role] = build_fixed_source_batch(
                reader, source.spec
            )
            if reader.accessed_entries != list(FIXED_ENTRIES):
                raise AssertionError(
                    "Reader accessed entries outside the fixed sequence"
                )
            source_uuids[source.spec.role] = reader.source_uuid

    mc_batch = source_batches["mc"]
    fit_digest = _smoke_fit_digest(resolved_sources)
    normalization = typed.fit_frozen_normalization_for_smoke(
        mc_batch.descriptors,
        fit_inventory_row_selection_digest=fit_digest,
    )
    encoder = typed.ReferenceTypedDescriptorEncoder.initialize(
        normalization, projection_dim=8, seed=0
    )

    combined = collate_source_batches(
        [source_batches[source.spec.role] for source in resolved_sources]
    )
    shard_provenance = _shard_provenance(resolved_sources, source_uuids)
    save_source_contract_shard(output_path, combined, shard_provenance)
    loaded, loaded_provenance = load_source_contract_shard(output_path)
    if loaded_provenance != shard_provenance:
        raise AssertionError("Shard provenance changed during round trip")
    _assert_same_row_round_trip(combined, loaded)
    encoded = encoder.forward(loaded.descriptors, loaded.detector_event_block)
    _require_finite(
        "reference encoder output", encoded.conditioned_detector_event_features
    )

    return {
        "status": "PASS",
        "starting_commit": STARTING_COMMIT,
        "tree": TREE_NAME,
        "entries": [FIXED_ENTRIES[0], FIXED_ENTRIES[-1]],
        "rows": loaded.row_count,
        "required_branch_count": len(REQUIRED_BRANCHES),
        "sources": [
            {
                "role": source.spec.role,
                "playlist": source.spec.playlist,
                "manifest": source.spec.manifest_relative_path,
                "manifest_line": 1,
                "basename": source.spec.expected_basename,
                "uuid": source_uuids[source.spec.role],
            }
            for source in resolved_sources
        ],
        "object_counts": {
            family_name: {
                "data": int(
                    loaded.descriptors.families[family_name].counts[
                        loaded.source_role == ROLE_DATA
                    ].sum()
                ),
                "mc": int(
                    loaded.descriptors.families[family_name].counts[
                        loaded.source_role == ROLE_MC
                    ].sum()
                ),
            }
            for family_name in typed.CONTRACT_BY_NAME
        },
        "smoke_normalization_fit": "fixed MC entries 0--15 only; not persisted",
        "output": str(Path(output_path)),
    }


def _build_p12(raw: Mapping[str, object]) -> np.ndarray:
    vectors: list[list[object]] = []
    for name in GENERIC_VALUE_BRANCHES:
        values = list(raw[name])
        declared = _nonnegative_count(raw[f"{name}_sz"], f"{name}_sz")
        if len(values) != declared:
            raise ValueError(f"{name} length {len(values)} != declared {declared}")
        vectors.append(values)
    lengths = {len(values) for values in vectors}
    if len(lengths) != 1:
        raise ValueError("Generic cluster vectors are not aligned")

    energy, position, z_position, view, time, is_muon = vectors
    retained = [index for index, flag in enumerate(is_muon) if int(flag) == 0]
    columns = [
        [source[index] for index in retained]
        for source in (energy, position, z_position, view, time)
    ]
    output = np.zeros((P12_TOKEN_COUNT, 5), dtype=np.float32)
    if retained:
        aligned = np.asarray(columns, dtype=np.float32).T
        if aligned.shape != (len(retained), 5):
            raise ValueError("Filtered generic cluster matrix has the wrong width")
        order = np.argsort(-aligned[:, 0], kind="stable")
        retained_count = min(len(retained), P12_TOKEN_COUNT)
        output[:retained_count] = aligned[order[:retained_count]]
    _require_finite("generic P12", output)
    return output


def _build_detector_event_block(raw: Mapping[str, object]) -> np.ndarray:
    momentum, momentum_magnitude, theta, phi = _current_cv_muon(raw)
    vertex = np.asarray(raw["vtx"], dtype=np.float64)
    if momentum.shape != (4,) or vertex.shape != (4,):
        raise ValueError("Muon four-vector and vertex must each have width four")
    scalars = np.asarray(
        [[
            momentum_magnitude * math.sin(theta) / 1000.0,
            momentum_magnitude * math.cos(theta) / 1000.0,
        ]],
        dtype=np.float32,
    )
    minos_ok = (
        int(raw["isMinosMatchTrack"]) == 1
        and int(raw["MasterAnaDev_minos_trk_is_ok"]) == 1
    )
    muon = np.asarray(
        [[
            *momentum,
            phi,
            float(raw["MasterAnaDev_minos_trk_qp"]),
            float(minos_ok),
        ]],
        dtype=np.float32,
    )
    vertex3 = np.asarray([vertex[:3]], dtype=np.float32)
    block = np.column_stack(
        [
            scalars[:, 0],
            scalars[:, 1],
            muon[:, 0] / np.float32(1000.0),
            muon[:, 1] / np.float32(1000.0),
            muon[:, 2] / np.float32(1000.0),
            muon[:, 3] / np.float32(1000.0),
            np.cos(muon[:, 4].astype(np.float64)).astype(np.float32),
            np.sin(muon[:, 4].astype(np.float64)).astype(np.float32),
            muon[:, 5] * np.float32(1000.0),
            muon[:, 6],
            vertex3[:, 0] / np.float32(1000.0),
            vertex3[:, 1] / np.float32(1000.0),
            vertex3[:, 2] / np.float32(1000.0),
        ]
    ).astype(np.float32)
    _require_finite("detector event block", block)
    return block[0]


def _current_cv_muon(
    raw: Mapping[str, object],
) -> tuple[np.ndarray, float, float, float]:
    """Mirror the CV ``GetPmu``/angle/``GetMuon4V`` accessor chain.

    The current producer does not build its muon from ``muon_corrected_p``.
    PlotUtils reads the first three ``MasterAnaDev_leptonE`` components,
    evaluates the MINOS subtraction and addition at zero CV offset, and derives
    beam-frame angles from ``muon_thetaX/Y``. The installed central beam-angle
    offsets are both zero.
    """

    lepton = np.asarray(raw["MasterAnaDev_leptonE"], dtype=np.float64)
    if lepton.shape != (4,):
        raise ValueError("MasterAnaDev_leptonE must have width four")
    total_p_nominal = math.sqrt(
        lepton[0] * lepton[0]
        + lepton[1] * lepton[1]
        + lepton[2] * lepton[2]
    )
    minos_p_nominal = float(raw["MasterAnaDev_minos_trk_p"])
    minerva_p = total_p_nominal - minos_p_nominal
    momentum_magnitude = minerva_p + minos_p_nominal

    theta_x = float(raw["muon_thetaX"])
    theta_y = float(raw["muon_thetaY"])
    phi = math.atan2(math.tan(theta_y), math.tan(theta_x))
    sec_theta_x = 1.0 / math.cos(theta_x)
    sec_theta_y = 1.0 / math.cos(theta_y)
    intermediate = math.sqrt(
        1.0 / (sec_theta_x * sec_theta_x + sec_theta_y * sec_theta_y - 1.0)
    )
    theta = math.acos(intermediate)
    if theta_x > 3.14159265 / 2.0 or theta_y > 3.14159265 / 2.0:
        theta = 3.14159265 - theta

    px = momentum_magnitude * math.sin(theta) * math.cos(phi)
    py = momentum_magnitude * math.sin(theta) * math.sin(phi)
    pz = momentum_magnitude * math.cos(theta)
    energy = math.sqrt(105.6583 * 105.6583 + momentum_magnitude * momentum_magnitude)
    momentum = np.asarray([px, py, pz, energy], dtype=np.float64)
    _require_finite("current CV muon", momentum)
    if not math.isfinite(theta) or not math.isfinite(phi):
        raise ValueError("Current CV muon angles are non-finite")
    return momentum, momentum_magnitude, theta, phi


def _build_photons(raw: Mapping[str, object]) -> list[dict[str, object]]:
    photons: list[dict[str, object]] = []
    for index in (1, 2):
        presence_energy = float(raw[f"gamma{index}_E"])
        if not np.isfinite(presence_energy):
            raise ValueError(f"gamma{index}_E is non-finite; presence is ambiguous")
        if presence_energy <= PHOTON_PRESENCE_THRESHOLD:
            continue
        photons.append(
            {
                "direction": raw[f"gamma{index}_direction"],
                "dedx": raw[f"gamma{index}_dEdx"],
                "time": raw[f"gamma{index}_time"],
                "energy_tracker": raw[f"gamma{index}_energy_trkr"],
                "energy_ecal": raw[f"gamma{index}_energy_ecal"],
                "energy_hcal": raw[f"gamma{index}_energy_hcal"],
                "energy_scal_x": raw[f"gamma{index}_energy_scal_X"],
                "energy_scal_uv": raw[f"gamma{index}_energy_scal_UV"],
                "evis_tracker": raw[f"gamma{index}_evis_trkr"],
                "evis_ecal": raw[f"gamma{index}_evis_ecal"],
                "evis_hcal": raw[f"gamma{index}_evis_hcal"],
                "evis_scal_x": raw[f"gamma{index}_evis_scal_X"],
                "evis_scal_uv": raw[f"gamma{index}_evis_scal_UV"],
            }
        )
    return photons


def _build_blobs(raw: Mapping[str, object]) -> list[dict[str, object]]:
    values: dict[str, list[object]] = {}
    for name in BLOB_BASES:
        branch_values = list(raw[name])
        declared = _nonnegative_count(raw[f"{name}_sz"], f"{name}_sz")
        if len(branch_values) != declared:
            raise ValueError(
                f"{name} length {len(branch_values)} != declared {declared}"
            )
        values[name] = branch_values
    counts = {len(branch_values) for branch_values in values.values()}
    if len(counts) != 1:
        raise ValueError("Blob vectors are not aligned")
    blob_count = counts.pop()
    return [
        {
            "position": [
                values["MasterAnaDev_BlobX"][index],
                values["MasterAnaDev_BlobY"][index],
                values["MasterAnaDev_BlobZ"][index],
            ],
            "time": values["MasterAnaDev_BlobT"][index],
            "time_position": values["MasterAnaDev_BlobTPos"][index],
            "total_energy": values["MasterAnaDev_BlobTotalE"][index],
            "is_3d": values["MasterAnaDev_BlobIs3D"][index],
            "cluster_count": values["MasterAnaDev_BlobNClusters"][index],
        }
        for index in range(blob_count)
    ]


def _build_prongs(raw: Mapping[str, object]) -> list[dict[str, object]]:
    count = _nonnegative_count(raw[PRONG_COUNT_BRANCH], PRONG_COUNT_BRANCH)
    for name in PRONG_VECTOR_BRANCHES + PRONG_NESTED_BRANCHES:
        if len(raw[name]) != count:  # type: ignore[arg-type]
            raise ValueError(f"{name} length does not match n_prongs {count}")
    prongs: list[dict[str, object]] = []
    for index in range(count):
        position_and_time = list(raw["prong_part_pos"][index])  # type: ignore[index]
        four_momentum = list(raw["prong_part_E"][index])  # type: ignore[index]
        if len(position_and_time) != 4 or len(four_momentum) != 4:
            raise ValueError(
                "Prong position/time and four-momentum must have width four"
            )
        prongs.append(
            {
                "position": position_and_time[:3],
                "time": position_and_time[3],
                "four_momentum": four_momentum,
                "dedx": raw["prong_dEdXMean"][index],  # type: ignore[index]
                "score": raw["prong_part_score"][index],  # type: ignore[index]
                "mass": raw["prong_part_mass"][index],  # type: ignore[index]
                "charge": raw["prong_part_charge"][index],  # type: ignore[index]
                "raw_pid": raw["prong_part_pid"][index],  # type: ignore[index]
            }
        )
    return prongs


def _identity_normalization(
    contract: typed.FamilyContract,
) -> typed.FamilyNormalization:
    return typed.FamilyNormalization(
        means={
            field.name: np.zeros(field.width, dtype=np.float32)
            for field in contract.fields
            if field.kind == "continuous"
        },
        scales={
            field.name: np.ones(field.width, dtype=np.float32)
            for field in contract.fields
            if field.kind == "continuous"
        },
    )


def _shard_provenance(
    sources: Sequence[ResolvedSource],
    source_uuids: Mapping[str, str],
) -> typed.ShardProvenance:
    manifest_hasher = hashlib.sha256()
    for source in sources:
        manifest_hasher.update(source.spec.manifest_relative_path.encode("utf-8"))
        manifest_hasher.update(b"\0")
        manifest_hasher.update(source.manifest_bytes)
        manifest_hasher.update(b"\0")
    return typed.ShardProvenance(
        manifest_sha256=manifest_hasher.hexdigest(),
        playlist="1B data + 1A StandardMC fixed source smoke",
        production_provenance=tuple(
            sorted(
                (
                    ("purpose", "fixed-real-row-source-to-contract-smoke"),
                    ("starting_commit", STARTING_COMMIT),
                    ("entry_selection", "source-tree entries 0--15 inclusive"),
                    ("source_ordinal_1", "1B_Data.txt manifest line 1"),
                    ("source_ordinal_2", "1A_MC.txt manifest line 1"),
                )
            )
        ),
        source_files=tuple(
            typed.SourceFileMetadata(
                ordinal=source.spec.shard_file_ordinal,
                path=source.path,
                uuid=source_uuids[source.spec.role],
            )
            for source in sources
        ),
    )


def _smoke_fit_digest(sources: Sequence[ResolvedSource]) -> str:
    hasher = hashlib.sha256()
    hasher.update(b"SMOKE ONLY; MC source entries 0--15; typed valid values")
    mc_source = next(source for source in sources if source.spec.role == "mc")
    hasher.update(mc_source.spec.manifest_relative_path.encode("utf-8"))
    hasher.update(b"\0")
    hasher.update(mc_source.manifest_bytes)
    return hasher.hexdigest()


def _assert_same_row_round_trip(
    expected: SourceContractBatch,
    observed: SourceContractBatch,
) -> None:
    for name in (
        "p12_clusters",
        "detector_event_block",
        "tuple_event_keys",
        "source_role",
    ):
        if not np.array_equal(getattr(expected, name), getattr(observed, name)):
            raise AssertionError(f"{name} changed during same-row round trip")
    for name in (
        "source_file_ordinal",
        "source_tree",
        "source_entry",
    ):
        if not np.array_equal(
            getattr(expected.descriptors.provenance, name),
            getattr(observed.descriptors.provenance, name),
        ):
            raise AssertionError(f"Row provenance {name} changed during round trip")
    for contract in typed.FAMILY_CONTRACTS:
        left = expected.descriptors.families[contract.name]
        right = observed.descriptors.families[contract.name]
        for name in ("offsets", "counts", "enabled", "token_mask"):
            if not np.array_equal(getattr(left, name), getattr(right, name)):
                raise AssertionError(
                    f"{contract.name}.{name} changed during round trip"
                )
        for field in contract.fields:
            if not np.array_equal(left.values[field.name], right.values[field.name]):
                raise AssertionError(
                    f"{contract.name}.{field.name} raw values changed during round trip"
                )
            if not np.array_equal(left.masks[field.name], right.masks[field.name]):
                raise AssertionError(
                    f"{contract.name}.{field.name} masks changed during round trip"
                )


def _python_scalar(value: object) -> int | float | bool:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    try:
        integer = int(value)  # type: ignore[arg-type]
        floating = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as error:
        raise ValueError(f"ROOT scalar {value!r} is not numeric") from error
    return integer if floating == integer else floating


def _fixed_sequence(value: object, width: int, name: str) -> list[object]:
    if width < 0:
        raise ValueError(f"{name} has a negative width")
    try:
        observed_width = len(value)  # type: ignore[arg-type]
    except TypeError:
        observed_width = None
    if observed_width is not None and observed_width != width:
        raise ValueError(
            f"{name} exposes width {observed_width}, expected exactly {width}"
        )
    try:
        return [
            _python_scalar(value[index])  # type: ignore[index]
            for index in range(width)
        ]
    except (IndexError, TypeError) as error:
        raise ValueError(
            f"{name} does not expose the declared width {width}"
        ) from error


def _nonnegative_count(value: object, name: str) -> int:
    count = int(value)
    if float(value) != count or count < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return count


def _require_finite(name: str, values: np.ndarray) -> None:
    if not np.all(np.isfinite(values)):
        raise ValueError(f"{name} contains non-finite transformed values")


def main() -> int:
    """CLI for the fixed smoke; the source set and entry range are not configurable."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    summary = run_fixed_real_smoke(args.repo_root, args.output)
    print(json.dumps(summary, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
