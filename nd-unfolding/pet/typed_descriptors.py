"""Typed reconstructed-object descriptors for PET method development.

The module defines a detector-side, ragged representation for photons, blobs,
and prongs. It deliberately has no ROOT reader and no truth-object contract.
Raw values and validity masks are serialized separately so calibration and
normalization choices remain replaceable without changing row alignment.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from types import MappingProxyType
from typing import Literal, Mapping, Sequence, TypeAlias

import numpy as np

from atomic_write import atomic_savez_compressed


SCHEMA_VERSION = "pet-typed-descriptors-v1"
TOKEN_PRESENT_KEY = "__present__"
DETECTOR_EVENT_WIDTH = 13
TRUTH_EVENT_WIDTH = 2

PRODUCTION_NORMALIZATION_FITTING_POLICY = (
    "Fit each continuous component using valid values from the predeclared "
    "training reco-MC pass_reco rows only. Reuse the frozen statistics unchanged "
    "for data, validation, inference, and all representation controls."
)
SMOKE_NORMALIZATION_FITTING_POLICY = (
    "SMOKE ONLY: fit valid continuous values from the explicitly supplied smoke "
    "rows. "
    "This artifact is not valid for production, training, or scientific inference."
)

FieldKind: TypeAlias = Literal["continuous", "categorical"]
MaskPolicy: TypeAlias = Literal["independent", "all_components"]
RawObject: TypeAlias = Mapping[str, object]
RawRows: TypeAlias = Sequence[Sequence[RawObject]]


class SourceTree(IntEnum):
    """Source-tree identifiers stored in compact row provenance."""

    MASTER_ANA_DEV = 1
    TRUTH = 2


@dataclass(frozen=True)
class FieldSpec:
    """Describe one raw field owned by a typed-object family.

    Parameters
    ----------
    name : str
        Stable serialized field name.
    width : int
        Number of scalar components per object.
    unit : str
        Raw-unit declaration. ``tuple-native`` labels preserve unresolved
        source conventions instead of silently asserting a conversion.
    kind : {"continuous", "categorical"}
        Encoding behavior for valid values.
    sentinels : tuple[float, ...]
        Raw values converted to false validity masks.
    categories : tuple[int, ...]
        Identity-only vocabulary for categorical fields. Values outside this
        vocabulary use an unknown-code channel and remain unchanged in raw
        storage.
    mask_policy : {"independent", "all_components"}
        Whether validity is retained component by component or cleared for the
        entire vector when any component is invalid.
    """

    name: str
    width: int
    unit: str
    kind: FieldKind = "continuous"
    sentinels: tuple[float, ...] = (-999.0, -9999.0)
    categories: tuple[int, ...] = ()
    mask_policy: MaskPolicy = "independent"

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Field name must not be empty")
        if self.width < 1:
            raise ValueError(f"Field {self.name!r} must have positive width")
        if self.kind not in ("continuous", "categorical"):
            raise ValueError(f"Unsupported field kind {self.kind!r}")
        if self.kind == "continuous" and self.categories:
            raise ValueError(f"Continuous field {self.name!r} cannot have categories")
        if self.kind == "categorical" and not self.categories:
            raise ValueError(f"Categorical field {self.name!r} needs categories")
        if len(set(self.categories)) != len(self.categories):
            raise ValueError(f"Field {self.name!r} has repeated categories")
        if self.mask_policy not in ("independent", "all_components"):
            raise ValueError(f"Unsupported mask policy {self.mask_policy!r}")

    @property
    def storage_dtype(self) -> np.dtype:
        """Return the canonical dtype used for raw serialization."""

        if self.kind == "categorical":
            return np.dtype(np.int32)
        return np.dtype(np.float32)

    @property
    def projected_width(self) -> int:
        """Return this field's value width before validity bits are added."""

        if self.kind == "categorical":
            return self.width * (len(self.categories) + 1)
        return self.width

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible field declaration."""

        return {
            "name": self.name,
            "width": self.width,
            "unit": self.unit,
            "kind": self.kind,
            "sentinels": list(self.sentinels),
            "categories": list(self.categories),
            "mask_policy": self.mask_policy,
        }


@dataclass(frozen=True)
class FamilyNormalization:
    """Valid-only normalization parameters for one object family."""

    means: Mapping[str, np.ndarray]
    scales: Mapping[str, np.ndarray]

    def __post_init__(self) -> None:
        if set(self.means) != set(self.scales):
            raise ValueError("Normalization means and scales must name the same fields")
        frozen_means: dict[str, np.ndarray] = {}
        frozen_scales: dict[str, np.ndarray] = {}
        for field_name in self.means:
            means = np.asarray(self.means[field_name], dtype=np.float32).copy()
            scales = np.asarray(self.scales[field_name], dtype=np.float32).copy()
            if means.shape != scales.shape or means.ndim != 1:
                raise ValueError(
                    f"Normalization field {field_name!r} has incompatible shapes"
                )
            if not np.all(np.isfinite(means)):
                raise ValueError(
                    f"Normalization means for {field_name!r} are not finite"
                )
            if not np.all(np.isfinite(scales)) or np.any(scales <= 0.0):
                raise ValueError(
                    f"Normalization scales for {field_name!r} must be finite "
                    "and positive"
                )
            means.setflags(write=False)
            scales.setflags(write=False)
            frozen_means[field_name] = means
            frozen_scales[field_name] = scales
        object.__setattr__(self, "means", MappingProxyType(frozen_means))
        object.__setattr__(self, "scales", MappingProxyType(frozen_scales))


@dataclass(frozen=True)
class RaggedFamilyBatch:
    """Flat ragged storage for one typed-object family."""

    name: str
    offsets: np.ndarray
    counts: np.ndarray
    enabled: np.ndarray
    token_mask: np.ndarray
    values: Mapping[str, np.ndarray]
    masks: Mapping[str, np.ndarray]

    @property
    def row_count(self) -> int:
        """Return the number of event rows."""

        return int(self.counts.shape[0])

    @property
    def token_count(self) -> int:
        """Return the number of stored ragged records."""

        return int(self.token_mask.shape[0])


@dataclass(frozen=True)
class FamilyContract:
    """Own raw fields, masks, normalization, and feature preparation."""

    name: str
    fields: tuple[FieldSpec, ...]

    def __post_init__(self) -> None:
        field_names = [field.name for field in self.fields]
        if not self.name:
            raise ValueError("Family name must not be empty")
        if not self.fields:
            raise ValueError(f"Family {self.name!r} must declare fields")
        if len(set(field_names)) != len(field_names):
            raise ValueError(f"Family {self.name!r} has repeated field names")

    @property
    def feature_width(self) -> int:
        """Return projector input width, including component validity bits."""

        return sum(field.projected_width + field.width for field in self.fields)

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible family declaration."""

        return {
            "name": self.name,
            "fields": [field.as_dict() for field in self.fields],
        }

    def build_batch(
        self,
        rows: RawRows,
        *,
        enabled: Sequence[bool] | np.ndarray | None = None,
    ) -> RaggedFamilyBatch:
        """Convert raw object rows into flat values and independent masks.

        Every object must contain every declared field. ``None`` explicitly
        represents a missing field. Object presence is structural and is
        controlled only by ``__present__``; no feature, including prong
        dE/dx, is used to infer presence.

        Parameters
        ----------
        rows : sequence of sequence of mappings
            Per-event raw object records.
        enabled : sequence of bool or None, optional
            Per-row family switch. Disabled rows retain raw records and counts
            but encode to the defined all-zero family embedding.

        Returns
        -------
        RaggedFamilyBatch
            Canonical flat storage with masks and explicit counts.
        """

        row_count = len(rows)
        enabled_array = self._coerce_enabled(enabled, row_count)
        field_names = {field.name for field in self.fields}
        flat_objects: list[RawObject] = []
        offsets = np.zeros(row_count + 1, dtype=np.int64)
        for row_index, objects in enumerate(rows):
            for object_index, raw_object in enumerate(objects):
                missing = field_names.difference(raw_object)
                extra = set(raw_object).difference(field_names | {TOKEN_PRESENT_KEY})
                if missing:
                    raise ValueError(
                        f"{self.name} row {row_index} object {object_index} "
                        f"is missing fields {sorted(missing)}"
                    )
                if extra:
                    raise ValueError(
                        f"{self.name} row {row_index} object {object_index} "
                        f"has unknown fields {sorted(extra)}"
                    )
                flat_objects.append(raw_object)
            offsets[row_index + 1] = len(flat_objects)

        token_mask = np.asarray(
            [
                bool(raw_object.get(TOKEN_PRESENT_KEY, True))
                for raw_object in flat_objects
            ],
            dtype=np.bool_,
        )
        values: dict[str, np.ndarray] = {}
        masks: dict[str, np.ndarray] = {}
        for field in self.fields:
            raw_values = np.zeros(
                (len(flat_objects), field.width), dtype=field.storage_dtype
            )
            raw_masks = np.zeros((len(flat_objects), field.width), dtype=np.bool_)
            for object_index, raw_object in enumerate(flat_objects):
                value, mask = self._coerce_field(field, raw_object[field.name])
                raw_values[object_index] = value
                raw_masks[object_index] = mask
            values[field.name] = raw_values
            masks[field.name] = raw_masks

        counts = np.add.reduceat(
            np.pad(token_mask.astype(np.int64), (0, 1)), offsets[:-1]
        )
        empty_rows = offsets[1:] == offsets[:-1]
        counts[empty_rows] = 0
        batch = RaggedFamilyBatch(
            name=self.name,
            offsets=offsets,
            counts=counts,
            enabled=enabled_array,
            token_mask=token_mask,
            values=values,
            masks=masks,
        )
        self.validate_batch(batch)
        return batch

    def _fit_normalization_from_selected_rows(
        self,
        batch: RaggedFamilyBatch,
    ) -> FamilyNormalization:
        """Fit component statistics from an already governed row selection.

        Categorical codes are not normalized. Disabled-family rows remain in
        the fit so the statistics can be held fixed across representation
        arms. The caller owns the row-selection policy; production code must
        supply only the predeclared training reco-MC pass_reco rows.

        Parameters
        ----------
        batch : RaggedFamilyBatch
            A batch produced by this contract.

        Returns
        -------
        FamilyNormalization
            Per-component means and standard deviations. Components without
            valid observations use mean zero and scale one.
        """

        self.validate_batch(batch)
        means: dict[str, np.ndarray] = {}
        scales: dict[str, np.ndarray] = {}
        for field in self.fields:
            if field.kind == "categorical":
                continue
            field_values = np.asarray(batch.values[field.name], dtype=np.float64)
            field_masks = np.asarray(
                batch.masks[field.name], dtype=np.bool_
            ).copy()
            field_masks &= batch.token_mask[:, None]
            field_means = np.zeros(field.width, dtype=np.float32)
            field_scales = np.ones(field.width, dtype=np.float32)
            for component in range(field.width):
                valid_values = field_values[field_masks[:, component], component]
                if valid_values.size == 0:
                    continue
                field_means[component] = np.float32(valid_values.mean())
                standard_deviation = float(valid_values.std())
                if np.isfinite(standard_deviation) and standard_deviation > 0.0:
                    field_scales[component] = np.float32(standard_deviation)
            means[field.name] = field_means
            scales[field.name] = field_scales
        return FamilyNormalization(means=means, scales=scales)

    def prepare_features(
        self,
        batch: RaggedFamilyBatch,
        normalization: FamilyNormalization,
    ) -> np.ndarray:
        """Build finite projector inputs from raw values and masks.

        Invalid values are replaced after mask construction and cannot affect
        the projector. Categorical codes are represented only by code identity,
        with one channel per declared code and one unknown-code channel.

        Parameters
        ----------
        batch : RaggedFamilyBatch
            Raw family batch.
        normalization : FamilyNormalization
            Valid-only continuous statistics.

        Returns
        -------
        numpy.ndarray
            Finite ``float32`` matrix with one row per stored object.
        """

        self.validate_batch(batch)
        prepared: list[np.ndarray] = []
        validity: list[np.ndarray] = []
        for field in self.fields:
            field_values = np.asarray(batch.values[field.name])
            field_masks = np.asarray(
                batch.masks[field.name], dtype=np.bool_
            ).copy()
            field_masks &= batch.token_mask[:, None]
            if field.kind == "continuous":
                if field.name not in normalization.means:
                    raise ValueError(f"Missing normalization mean for {field.name!r}")
                means = np.asarray(normalization.means[field.name], dtype=np.float32)
                scales = np.asarray(normalization.scales[field.name], dtype=np.float32)
                normalized = np.zeros(field_values.shape, dtype=np.float32)
                np.subtract(
                    field_values,
                    means,
                    out=normalized,
                    where=field_masks,
                    casting="unsafe",
                )
                np.divide(normalized, scales, out=normalized, where=field_masks)
                prepared.append(normalized)
            else:
                category_count = len(field.categories)
                one_hot = np.zeros(
                    (batch.token_count, field.width, category_count + 1),
                    dtype=np.float32,
                )
                category_lookup = {
                    category: index for index, category in enumerate(field.categories)
                }
                for component in range(field.width):
                    valid_indices = np.flatnonzero(field_masks[:, component])
                    for token_index in valid_indices:
                        code = int(field_values[token_index, component])
                        code_index = category_lookup.get(code, category_count)
                        one_hot[token_index, component, code_index] = 1.0
                prepared.append(one_hot.reshape(batch.token_count, -1))
            validity.append(field_masks.astype(np.float32))

        features = np.concatenate(prepared + validity, axis=1)
        if features.shape != (batch.token_count, self.feature_width):
            raise AssertionError(
                f"{self.name} prepared width {features.shape[1]} != "
                f"{self.feature_width}"
            )
        if not np.all(np.isfinite(features)):
            raise ValueError(f"{self.name} prepared features are not finite")
        return features

    def validate_batch(self, batch: RaggedFamilyBatch) -> None:
        """Validate ragged structure, explicit counts, and field shapes."""

        if batch.name != self.name:
            raise ValueError(f"Expected family {self.name!r}, got {batch.name!r}")
        offsets = np.asarray(batch.offsets)
        if offsets.ndim != 1 or offsets.size < 1:
            raise ValueError(f"{self.name} offsets must be one-dimensional")
        if offsets[0] != 0 or np.any(np.diff(offsets) < 0):
            raise ValueError(f"{self.name} offsets are not monotonic from zero")
        if offsets[-1] != batch.token_count:
            raise ValueError(f"{self.name} final offset does not match token count")
        if batch.enabled.shape != (batch.row_count,):
            raise ValueError(f"{self.name} enabled mask has the wrong shape")
        if batch.offsets.shape != (batch.row_count + 1,):
            raise ValueError(f"{self.name} offsets have the wrong row count")
        expected_counts = np.zeros(batch.row_count, dtype=np.int64)
        for row_index in range(batch.row_count):
            start, stop = batch.offsets[row_index : row_index + 2]
            expected_counts[row_index] = int(batch.token_mask[start:stop].sum())
        if not np.array_equal(batch.counts, expected_counts):
            raise ValueError(f"{self.name} explicit counts do not match token masks")
        expected_names = {field.name for field in self.fields}
        if set(batch.values) != expected_names or set(batch.masks) != expected_names:
            raise ValueError(f"{self.name} stored fields do not match its contract")
        for field in self.fields:
            expected_shape = (batch.token_count, field.width)
            if batch.values[field.name].shape != expected_shape:
                raise ValueError(f"{self.name}.{field.name} has the wrong value shape")
            if batch.masks[field.name].shape != expected_shape:
                raise ValueError(f"{self.name}.{field.name} has the wrong mask shape")

    @staticmethod
    def _coerce_enabled(
        enabled: Sequence[bool] | np.ndarray | None,
        row_count: int,
    ) -> np.ndarray:
        if enabled is None:
            return np.ones(row_count, dtype=np.bool_)
        enabled_array = np.asarray(enabled, dtype=np.bool_)
        if enabled_array.shape != (row_count,):
            raise ValueError(
                f"Enabled mask shape {enabled_array.shape} does not match "
                f"{row_count} rows"
            )
        return enabled_array

    @staticmethod
    def _coerce_field(
        field: FieldSpec,
        raw_value: object,
    ) -> tuple[np.ndarray, np.ndarray]:
        if raw_value is None:
            return (
                np.zeros(field.width, dtype=field.storage_dtype),
                np.zeros(field.width, dtype=np.bool_),
            )
        numeric = np.asarray(raw_value, dtype=np.float64)
        if numeric.size != field.width:
            raise ValueError(
                f"Field {field.name!r} expected {field.width} components, "
                f"got {numeric.size}"
            )
        numeric = numeric.reshape(field.width)
        valid = np.isfinite(numeric)
        for sentinel in field.sentinels:
            valid &= numeric != sentinel
        safe_numeric = np.where(np.isfinite(numeric), numeric, 0.0)
        if field.kind == "categorical":
            valid &= safe_numeric == np.floor(safe_numeric)
        if field.mask_policy == "all_components" and not np.all(valid):
            valid[:] = False
        stored = safe_numeric.astype(field.storage_dtype)
        return stored, valid.astype(np.bool_)


PHOTON_CONTRACT = FamilyContract(
    name="photons",
    fields=(
        FieldSpec("direction", 3, "unitless", mask_policy="all_components"),
        FieldSpec("dedx", 1, "tuple-native dE/dx (physical unit unresolved)"),
        FieldSpec("time", 1, "tuple-native time (physical unit unresolved)"),
        FieldSpec("energy_tracker", 1, "tuple-native energy (calibration unresolved)"),
        FieldSpec("energy_ecal", 1, "tuple-native energy (calibration unresolved)"),
        FieldSpec("energy_hcal", 1, "tuple-native energy (calibration unresolved)"),
        FieldSpec("energy_scal_x", 1, "tuple-native energy (calibration unresolved)"),
        FieldSpec("energy_scal_uv", 1, "tuple-native energy (calibration unresolved)"),
        FieldSpec("evis_tracker", 1, "tuple-native energy (calibration unresolved)"),
        FieldSpec("evis_ecal", 1, "tuple-native energy (calibration unresolved)"),
        FieldSpec("evis_hcal", 1, "tuple-native energy (calibration unresolved)"),
        FieldSpec("evis_scal_x", 1, "tuple-native energy (calibration unresolved)"),
        FieldSpec("evis_scal_uv", 1, "tuple-native energy (calibration unresolved)"),
    ),
)

BLOB_CONTRACT = FamilyContract(
    name="blobs",
    fields=(
        FieldSpec(
            "position",
            3,
            "tuple-native length (physical unit unresolved)",
            mask_policy="all_components",
        ),
        FieldSpec("time", 1, "tuple-native time (physical unit unresolved)"),
        FieldSpec("time_position", 1, "tuple-native time-position (unit unresolved)"),
        FieldSpec("total_energy", 1, "tuple-native energy (physical unit unresolved)"),
        FieldSpec(
            "is_3d",
            1,
            "raw categorical code",
            kind="categorical",
            categories=(0, 1),
        ),
        FieldSpec("cluster_count", 1, "count"),
    ),
)

PRONG_CONTRACT = FamilyContract(
    name="prongs",
    fields=(
        FieldSpec(
            "position",
            3,
            "tuple-native length (physical unit unresolved)",
            mask_policy="all_components",
        ),
        FieldSpec("time", 1, "tuple-native time (physical unit unresolved)"),
        FieldSpec(
            "four_momentum",
            4,
            "tuple-native momentum/energy (unit unresolved)",
            mask_policy="all_components",
        ),
        FieldSpec("dedx", 1, "tuple-native dE/dx (physical unit unresolved)"),
        FieldSpec("score", 1, "unitless"),
        FieldSpec("mass", 1, "tuple-native energy (physical unit unresolved)"),
        FieldSpec(
            "charge",
            1,
            "raw charge code",
            kind="categorical",
            categories=(-1, 0, 1),
        ),
        FieldSpec(
            "raw_pid",
            1,
            "raw uninterpreted categorical code",
            kind="categorical",
            sentinels=(-999.0, -9999.0),
            categories=(0, 3, 8, 9, 13),
        ),
    ),
)

FAMILY_CONTRACTS = (PHOTON_CONTRACT, BLOB_CONTRACT, PRONG_CONTRACT)
CONTRACT_BY_NAME = {contract.name: contract for contract in FAMILY_CONTRACTS}


@dataclass(frozen=True)
class RowProvenance:
    """Compact per-row source location."""

    source_file_ordinal: np.ndarray
    source_tree: np.ndarray
    source_entry: np.ndarray

    def __post_init__(self) -> None:
        arrays = (
            np.asarray(self.source_file_ordinal),
            np.asarray(self.source_tree),
            np.asarray(self.source_entry),
        )
        if any(array.ndim != 1 for array in arrays):
            raise ValueError("Row-provenance arrays must be one-dimensional")
        if len({array.shape for array in arrays}) != 1:
            raise ValueError("Row-provenance arrays must have equal length")
        if np.any(arrays[0] < 1):
            raise ValueError("Source-file ordinals are one-based and must be positive")
        if np.any(arrays[2] < 0):
            raise ValueError("Source entries are zero-based and must be non-negative")
        allowed_trees = {int(source_tree) for source_tree in SourceTree}
        if not set(int(value) for value in arrays[1]).issubset(allowed_trees):
            raise ValueError("Row provenance contains an unknown source-tree enum")
        row_keys = set(
            zip(
                (int(value) for value in arrays[0]),
                (int(value) for value in arrays[1]),
                (int(value) for value in arrays[2]),
            )
        )
        if len(row_keys) != arrays[0].size:
            raise ValueError(
                "Row provenance must be unique by file ordinal, tree, and entry"
            )

    @property
    def row_count(self) -> int:
        """Return the number of provenance rows."""

        return int(self.source_entry.shape[0])


@dataclass(frozen=True)
class SourceFileMetadata:
    """Shard-level identity for one manifest file."""

    ordinal: int
    path: str
    uuid: str


@dataclass(frozen=True)
class ShardProvenance:
    """Metadata bound once per descriptor shard."""

    manifest_sha256: str
    playlist: str
    production_provenance: tuple[tuple[str, str], ...]
    source_files: tuple[SourceFileMetadata, ...]

    def __post_init__(self) -> None:
        digest = self.manifest_sha256
        is_hexadecimal = all(
            character in "0123456789abcdef" for character in digest
        )
        if len(digest) != 64 or not is_hexadecimal:
            raise ValueError("manifest_sha256 must be a lowercase hexadecimal SHA-256")
        if not self.playlist:
            raise ValueError("Playlist must not be empty")
        ordinals = [source_file.ordinal for source_file in self.source_files]
        if any(ordinal < 1 for ordinal in ordinals):
            raise ValueError("Source-file ordinals are one-based and must be positive")
        if len(set(ordinals)) != len(ordinals):
            raise ValueError("Source-file ordinals must be unique within a shard")
        if any(
            not source_file.path or not source_file.uuid
            for source_file in self.source_files
        ):
            raise ValueError("Each source file needs a path and UUID")

    def as_dict(self) -> dict[str, object]:
        """Return canonical JSON-compatible shard metadata."""

        return {
            "manifest_sha256": self.manifest_sha256,
            "playlist": self.playlist,
            "production_provenance": dict(self.production_provenance),
            "source_files": [
                {
                    "ordinal": source_file.ordinal,
                    "path": source_file.path,
                    "uuid": source_file.uuid,
                }
                for source_file in self.source_files
            ],
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, object]) -> "ShardProvenance":
        """Construct shard metadata from its JSON-compatible form."""

        raw_files = raw["source_files"]
        if not isinstance(raw_files, list):
            raise ValueError("source_files must be a list")
        raw_production = raw["production_provenance"]
        if not isinstance(raw_production, dict):
            raise ValueError("production_provenance must be an object")
        return cls(
            manifest_sha256=str(raw["manifest_sha256"]),
            playlist=str(raw["playlist"]),
            production_provenance=tuple(
                sorted((str(key), str(value)) for key, value in raw_production.items())
            ),
            source_files=tuple(
                SourceFileMetadata(
                    ordinal=int(raw_file["ordinal"]),
                    path=str(raw_file["path"]),
                    uuid=str(raw_file["uuid"]),
                )
                for raw_file in raw_files
            ),
        )


@dataclass(frozen=True)
class TypedDescriptorBatch:
    """Detector-only typed families aligned to output event rows."""

    provenance: RowProvenance
    families: Mapping[str, RaggedFamilyBatch]

    def __post_init__(self) -> None:
        if set(self.families) != set(CONTRACT_BY_NAME):
            raise ValueError("Descriptor batch must contain photons, blobs, and prongs")
        for family_name, contract in CONTRACT_BY_NAME.items():
            family = self.families[family_name]
            contract.validate_batch(family)
            if family.row_count != self.provenance.row_count:
                raise ValueError(f"{family_name} row count does not match provenance")

    @property
    def row_count(self) -> int:
        """Return the number of aligned event rows."""

        return self.provenance.row_count


def build_descriptor_batch(
    *,
    provenance: RowProvenance,
    photon_rows: RawRows,
    blob_rows: RawRows,
    prong_rows: RawRows,
    family_enabled: Mapping[str, Sequence[bool] | np.ndarray] | None = None,
) -> TypedDescriptorBatch:
    """Build all detector descriptor families for aligned event rows.

    Parameters
    ----------
    provenance : RowProvenance
        Compact source location for each output row.
    photon_rows, blob_rows, prong_rows : sequence
        Per-row raw detector objects. Native misses use empty sequences for all
        three families.
    family_enabled : mapping or None, optional
        Per-family, per-row switches. Missing families default to enabled.

    Returns
    -------
    TypedDescriptorBatch
        Validated detector-only descriptor batch.
    """

    row_collections = {
        "photons": photon_rows,
        "blobs": blob_rows,
        "prongs": prong_rows,
    }
    for family_name, rows in row_collections.items():
        if len(rows) != provenance.row_count:
            raise ValueError(
                f"{family_name} has {len(rows)} rows, "
                f"expected {provenance.row_count}"
            )
    enabled_by_family = family_enabled or {}
    unknown_families = set(enabled_by_family).difference(CONTRACT_BY_NAME)
    if unknown_families:
        raise ValueError(f"Unknown family enable masks: {sorted(unknown_families)}")
    families = {
        family_name: CONTRACT_BY_NAME[family_name].build_batch(
            rows,
            enabled=enabled_by_family.get(family_name),
        )
        for family_name, rows in row_collections.items()
    }
    return TypedDescriptorBatch(provenance=provenance, families=families)


def _schema_json() -> str:
    schema = {
        "schema_version": SCHEMA_VERSION,
        "row_provenance": {
            "source_file_ordinal": "uint32, one-based",
            "source_tree": "uint8 SourceTree enum",
            "source_entry": "uint64, zero-based",
        },
        "families": [contract.as_dict() for contract in FAMILY_CONTRACTS],
    }
    return json.dumps(schema, sort_keys=True, separators=(",", ":"))


def descriptor_schema_digest() -> str:
    """Return the SHA-256 of the canonical typed-descriptor schema."""

    return hashlib.sha256(_schema_json().encode("ascii")).hexdigest()


@dataclass(frozen=True)
class FrozenNormalization:
    """Versioned normalization fitted under an explicit inventory policy.

    Production statistics are fitted only on the predeclared training reco-MC
    ``pass_reco`` rows. The resulting object is then reused unchanged for data,
    validation, inference, and representation controls. This module exposes no
    production fitter because it does not own inventory or split selection.

    Parameters
    ----------
    schema_digest : str
        Digest of the exact descriptor schema used during fitting.
    fit_inventory_row_selection_digest : str
        Digest binding the predeclared inventory, split, and selected row IDs.
    fitting_policy : str
        Exact policy describing which rows supplied the statistics.
    families : mapping
        Per-family continuous means and scales.
    """

    schema_digest: str
    fit_inventory_row_selection_digest: str
    fitting_policy: str
    families: Mapping[str, FamilyNormalization]

    def __post_init__(self) -> None:
        if self.schema_digest != descriptor_schema_digest():
            raise ValueError("Normalization schema digest does not match the contract")
        selection_digest = self.fit_inventory_row_selection_digest
        if len(selection_digest) != 64 or any(
            character not in "0123456789abcdef" for character in selection_digest
        ):
            raise ValueError(
                "fit_inventory_row_selection_digest must be a lowercase SHA-256"
            )
        if not self.fitting_policy:
            raise ValueError("Normalization fitting policy must not be empty")
        if set(self.families) != set(CONTRACT_BY_NAME):
            raise ValueError("Normalization must contain photons, blobs, and prongs")
        frozen_families: dict[str, FamilyNormalization] = {}
        for family_name, contract in CONTRACT_BY_NAME.items():
            normalization = self.families[family_name]
            expected_fields = {
                field.name for field in contract.fields if field.kind == "continuous"
            }
            if set(normalization.means) != expected_fields:
                raise ValueError(
                    f"{family_name} normalization fields do not match the contract"
                )
            for field in contract.fields:
                if field.kind != "continuous":
                    continue
                if normalization.means[field.name].shape != (field.width,):
                    raise ValueError(
                        f"{family_name}.{field.name} normalization has the wrong width"
                    )
            frozen_families[family_name] = normalization
        object.__setattr__(
            self, "families", MappingProxyType(frozen_families)
        )


def fit_frozen_normalization_for_smoke(
    batch: TypedDescriptorBatch,
    *,
    fit_inventory_row_selection_digest: str,
) -> FrozenNormalization:
    """Fit a smoke-only normalization object for reference CPU smoke tests.

    This entry point is intentionally unsuitable for production. Production
    normalization must be fitted by an inventory-aware caller using only its
    predeclared training reco-MC ``pass_reco`` rows, then supplied explicitly to
    the encoder.

    Parameters
    ----------
    batch : TypedDescriptorBatch
        Explicitly predeclared method-development smoke rows.
    fit_inventory_row_selection_digest : str
        Digest identifying the exact smoke fitting rows.

    Returns
    -------
    FrozenNormalization
        Frozen valid-only statistics labeled with the smoke-only policy.
    """

    return FrozenNormalization(
        schema_digest=descriptor_schema_digest(),
        fit_inventory_row_selection_digest=fit_inventory_row_selection_digest,
        fitting_policy=SMOKE_NORMALIZATION_FITTING_POLICY,
        families={
            contract.name: contract._fit_normalization_from_selected_rows(
                batch.families[contract.name]
            )
            for contract in FAMILY_CONTRACTS
        },
    )


def save_frozen_normalization(
    path: str | Path,
    normalization: FrozenNormalization,
) -> None:
    """Atomically persist frozen means, scales, digests, and fitting policy."""

    destination = Path(path)
    if destination.suffix != ".npz":
        raise ValueError("Frozen normalization path must end in .npz")
    arrays: dict[str, np.ndarray] = {
        "schema_version": np.asarray(SCHEMA_VERSION),
        "schema_digest": np.asarray(normalization.schema_digest),
        "fit_inventory_row_selection_digest": np.asarray(
            normalization.fit_inventory_row_selection_digest
        ),
        "fitting_policy": np.asarray(normalization.fitting_policy),
    }
    for contract in FAMILY_CONTRACTS:
        family = normalization.families[contract.name]
        for field_name in family.means:
            arrays[f"{contract.name}.mean.{field_name}"] = family.means[field_name]
            arrays[f"{contract.name}.scale.{field_name}"] = family.scales[field_name]
    atomic_savez_compressed(str(destination), arrays)


def load_frozen_normalization(path: str | Path) -> FrozenNormalization:
    """Load and validate a frozen normalization artifact."""

    with np.load(Path(path), allow_pickle=False) as stored:
        if str(stored["schema_version"].item()) != SCHEMA_VERSION:
            raise ValueError("Unsupported frozen-normalization schema version")
        family_normalizations: dict[str, FamilyNormalization] = {}
        for contract in FAMILY_CONTRACTS:
            continuous_fields = (
                field for field in contract.fields if field.kind == "continuous"
            )
            means: dict[str, np.ndarray] = {}
            scales: dict[str, np.ndarray] = {}
            for field in continuous_fields:
                means[field.name] = np.asarray(
                    stored[f"{contract.name}.mean.{field.name}"], dtype=np.float32
                )
                scales[field.name] = np.asarray(
                    stored[f"{contract.name}.scale.{field.name}"], dtype=np.float32
                )
            family_normalizations[contract.name] = FamilyNormalization(
                means=means, scales=scales
            )
        return FrozenNormalization(
            schema_digest=str(stored["schema_digest"].item()),
            fit_inventory_row_selection_digest=str(
                stored["fit_inventory_row_selection_digest"].item()
            ),
            fitting_policy=str(stored["fitting_policy"].item()),
            families=family_normalizations,
        )


def save_descriptor_shard(
    path: str | Path,
    batch: TypedDescriptorBatch,
    shard_provenance: ShardProvenance,
) -> None:
    """Serialize one typed-descriptor shard without object arrays.

    Parameters
    ----------
    path : str or pathlib.Path
        Destination ending in ``.npz``.
    batch : TypedDescriptorBatch
        Detector descriptor rows.
    shard_provenance : ShardProvenance
        Manifest, file, playlist, and production metadata stored once.
    """

    destination = Path(path)
    if destination.suffix != ".npz":
        raise ValueError("Typed descriptor shard path must end in .npz")
    arrays = descriptor_shard_arrays(batch, shard_provenance)
    atomic_savez_compressed(str(destination), arrays)


def descriptor_shard_arrays(
    batch: TypedDescriptorBatch,
    shard_provenance: ShardProvenance,
) -> dict[str, np.ndarray]:
    """Return object-free arrays for embedding descriptors in an aligned shard.

    This is the same serialization contract used by :func:`save_descriptor_shard`.
    It lets a same-row producer place the existing event block, generic P12 tokens,
    and typed descriptors in one atomic artifact instead of constructing a sidecar.
    """

    allowed_ordinals = {
        source_file.ordinal for source_file in shard_provenance.source_files
    }
    row_ordinals = set(int(value) for value in batch.provenance.source_file_ordinal)
    if not row_ordinals.issubset(allowed_ordinals):
        raise ValueError("Row provenance references a file absent from shard metadata")

    arrays: dict[str, np.ndarray] = {
        "schema_version": np.asarray(SCHEMA_VERSION),
        "schema_json": np.asarray(_schema_json()),
        "schema_digest": np.asarray(descriptor_schema_digest()),
        "shard_provenance_json": np.asarray(
            json.dumps(
                shard_provenance.as_dict(), sort_keys=True, separators=(",", ":")
            )
        ),
        "row.source_file_ordinal": np.asarray(
            batch.provenance.source_file_ordinal, dtype=np.uint32
        ),
        "row.source_tree": np.asarray(batch.provenance.source_tree, dtype=np.uint8),
        "row.source_entry": np.asarray(batch.provenance.source_entry, dtype=np.uint64),
    }
    for contract in FAMILY_CONTRACTS:
        family = batch.families[contract.name]
        arrays[f"{contract.name}.offsets"] = np.asarray(family.offsets, dtype=np.int64)
        arrays[f"{contract.name}.counts"] = np.asarray(family.counts, dtype=np.int64)
        arrays[f"{contract.name}.enabled"] = np.asarray(family.enabled, dtype=np.bool_)
        arrays[f"{contract.name}.token_mask"] = np.asarray(
            family.token_mask, dtype=np.bool_
        )
        for field in contract.fields:
            arrays[f"{contract.name}.raw.{field.name}"] = np.asarray(
                family.values[field.name], dtype=field.storage_dtype
            )
            arrays[f"{contract.name}.mask.{field.name}"] = np.asarray(
                family.masks[field.name], dtype=np.bool_
            )
    return arrays


def descriptor_batch_from_arrays(
    stored: Mapping[str, np.ndarray],
) -> tuple[TypedDescriptorBatch, ShardProvenance]:
    """Recover descriptors and shard provenance from object-free arrays."""

    if str(np.asarray(stored["schema_version"]).item()) != SCHEMA_VERSION:
        raise ValueError("Unsupported typed-descriptor schema version")
    if str(np.asarray(stored["schema_json"]).item()) != _schema_json():
        raise ValueError("Typed-descriptor field contract does not match this reader")
    if str(np.asarray(stored["schema_digest"]).item()) != descriptor_schema_digest():
        raise ValueError("Typed-descriptor schema digest does not match this reader")
    shard_provenance = ShardProvenance.from_dict(
        json.loads(str(np.asarray(stored["shard_provenance_json"]).item()))
    )
    provenance = RowProvenance(
        source_file_ordinal=np.asarray(
            stored["row.source_file_ordinal"], dtype=np.uint32
        ),
        source_tree=np.asarray(stored["row.source_tree"], dtype=np.uint8),
        source_entry=np.asarray(stored["row.source_entry"], dtype=np.uint64),
    )
    families: dict[str, RaggedFamilyBatch] = {}
    for contract in FAMILY_CONTRACTS:
        family_name = contract.name
        families[family_name] = RaggedFamilyBatch(
            name=family_name,
            offsets=np.asarray(stored[f"{family_name}.offsets"], dtype=np.int64),
            counts=np.asarray(stored[f"{family_name}.counts"], dtype=np.int64),
            enabled=np.asarray(stored[f"{family_name}.enabled"], dtype=np.bool_),
            token_mask=np.asarray(
                stored[f"{family_name}.token_mask"], dtype=np.bool_
            ),
            values={
                field.name: np.asarray(
                    stored[f"{family_name}.raw.{field.name}"],
                    dtype=field.storage_dtype,
                )
                for field in contract.fields
            },
            masks={
                field.name: np.asarray(
                    stored[f"{family_name}.mask.{field.name}"], dtype=np.bool_
                )
                for field in contract.fields
            },
        )
    batch = TypedDescriptorBatch(provenance=provenance, families=families)
    allowed_ordinals = {
        source_file.ordinal for source_file in shard_provenance.source_files
    }
    if not set(int(value) for value in provenance.source_file_ordinal).issubset(
        allowed_ordinals
    ):
        raise ValueError("Loaded rows reference a file absent from shard metadata")
    return batch, shard_provenance


def load_descriptor_shard(
    path: str | Path,
) -> tuple[TypedDescriptorBatch, ShardProvenance]:
    """Load and validate a typed-descriptor shard.

    Parameters
    ----------
    path : str or pathlib.Path
        Existing ``.npz`` descriptor shard.

    Returns
    -------
    tuple[TypedDescriptorBatch, ShardProvenance]
        Recovered detector rows and once-per-shard provenance.
    """

    with np.load(Path(path), allow_pickle=False) as stored:
        return descriptor_batch_from_arrays(stored)


@dataclass(frozen=True)
class ReferenceFamilyEncoder:
    """Reference CPU projector and masked sum pool for one family."""

    contract: FamilyContract
    normalization: FamilyNormalization
    weight: np.ndarray
    bias: np.ndarray

    def __post_init__(self) -> None:
        if self.bias.ndim != 1 or self.bias.size < 1:
            raise ValueError("Family projector bias must be a non-empty vector")
        expected_shape = (self.contract.feature_width, self.projection_dim)
        if self.weight.shape != expected_shape:
            raise ValueError(
                f"{self.contract.name} projector weight shape {self.weight.shape} "
                f"does not match {expected_shape}"
            )
        if not np.all(np.isfinite(self.weight)) or not np.all(np.isfinite(self.bias)):
            raise ValueError("Family projector parameters must be finite")

    @property
    def projection_dim(self) -> int:
        """Return the per-token projection width."""

        return int(self.bias.shape[0])

    @classmethod
    def initialize(
        cls,
        contract: FamilyContract,
        normalization: FamilyNormalization,
        *,
        projection_dim: int,
        seed: int,
    ) -> "ReferenceFamilyEncoder":
        """Initialize deterministic CPU weights from frozen statistics."""

        if projection_dim < 1:
            raise ValueError("projection_dim must be positive")
        generator = np.random.default_rng(seed)
        scale = np.sqrt(2.0 / (contract.feature_width + projection_dim))
        weight = generator.normal(
            0.0,
            scale,
            size=(contract.feature_width, projection_dim),
        ).astype(np.float32)
        bias = np.zeros(projection_dim, dtype=np.float32)
        return cls(
            contract=contract,
            normalization=normalization,
            weight=weight,
            bias=bias,
        )

    def project(self, batch: RaggedFamilyBatch) -> np.ndarray:
        """Apply the family-specific finite token projection."""

        features = self.contract.prepare_features(batch, self.normalization)
        projected = np.tanh(features @ self.weight + self.bias)
        projected *= batch.token_mask[:, None]
        return projected.astype(np.float32, copy=False)

    def pool(self, batch: RaggedFamilyBatch) -> np.ndarray:
        """Masked-sum-pool tokens and append the explicit object count."""

        projected = self.project(batch)
        pooled = np.zeros((batch.row_count, self.projection_dim + 1), dtype=np.float32)
        for row_index in range(batch.row_count):
            start, stop = batch.offsets[row_index : row_index + 2]
            pooled[row_index, :-1] = projected[start:stop].sum(axis=0)
            pooled[row_index, -1] = np.float32(batch.counts[row_index])
        pooled *= batch.enabled[:, None]
        return pooled


@dataclass(frozen=True)
class TypedEncoderOutput:
    """Reference family embeddings and detector-side event conditioning."""

    family_embeddings: Mapping[str, np.ndarray]
    typed_embedding: np.ndarray
    conditioned_detector_event_features: np.ndarray
    object_counts: Mapping[str, np.ndarray]


@dataclass(frozen=True)
class ReferenceTypedDescriptorEncoder:
    """Reference CPU encoder for synthetic interface and round-trip smokes.

    This NumPy implementation is not a training backend. It performs one
    deterministic finite forward pass and defines the tensor boundary a future
    trainable adapter must preserve.
    """

    family_encoders: Mapping[str, ReferenceFamilyEncoder]

    def __post_init__(self) -> None:
        if set(self.family_encoders) != set(CONTRACT_BY_NAME):
            raise ValueError("Encoder must contain photons, blobs, and prongs")
        projection_dims = set()
        for family_name, contract in CONTRACT_BY_NAME.items():
            encoder = self.family_encoders[family_name]
            if encoder.contract != contract:
                raise ValueError(f"{family_name} encoder has the wrong contract")
            projection_dims.add(encoder.projection_dim)
        if len(projection_dims) != 1:
            raise ValueError("All family projectors must have the same output width")

    @classmethod
    def initialize(
        cls,
        normalization: FrozenNormalization,
        *,
        projection_dim: int = 8,
        seed: int = 0,
    ) -> "ReferenceTypedDescriptorEncoder":
        """Initialize projectors from an explicit frozen normalization."""

        encoders = {
            contract.name: ReferenceFamilyEncoder.initialize(
                contract,
                normalization.families[contract.name],
                projection_dim=projection_dim,
                seed=seed + family_index,
            )
            for family_index, contract in enumerate(FAMILY_CONTRACTS)
        }
        return cls(family_encoders=encoders)

    @classmethod
    def initialize_for_smoke(
        cls,
        batch: TypedDescriptorBatch,
        *,
        fit_inventory_row_selection_digest: str,
        projection_dim: int = 8,
        seed: int = 0,
    ) -> tuple["ReferenceTypedDescriptorEncoder", FrozenNormalization]:
        """Fit supplied smoke rows and initialize the reference CPU encoder."""

        normalization = fit_frozen_normalization_for_smoke(
            batch,
            fit_inventory_row_selection_digest=fit_inventory_row_selection_digest,
        )
        return (
            cls.initialize(
                normalization,
                projection_dim=projection_dim,
                seed=seed,
            ),
            normalization,
        )

    def forward(
        self,
        batch: TypedDescriptorBatch,
        detector_event_features: np.ndarray,
    ) -> TypedEncoderOutput:
        """Pool each family and augment only detector-side FiLM conditioning.

        The 13-column detector event block is never modified in place. Its
        columns remain the leading columns of the conditioned output. The
        2-column truth event block is rejected and has no descriptor path.

        Parameters
        ----------
        batch : TypedDescriptorBatch
            Aligned detector descriptor rows.
        detector_event_features : numpy.ndarray
            Existing detector event block with shape ``(rows, 13)``.

        Returns
        -------
        TypedEncoderOutput
            Family pools, their concatenation, augmented conditioning, and
            explicit raw counts.
        """

        event_array = np.asarray(detector_event_features)
        expected_shape = (batch.row_count, DETECTOR_EVENT_WIDTH)
        if event_array.shape != expected_shape:
            raise ValueError(
                f"Detector event features must have shape {expected_shape}; "
                f"the truth block is not augmented"
            )
        family_embeddings = {
            contract.name: self.family_encoders[contract.name].pool(
                batch.families[contract.name]
            )
            for contract in FAMILY_CONTRACTS
        }
        typed_embedding = np.concatenate(
            [family_embeddings[contract.name] for contract in FAMILY_CONTRACTS],
            axis=1,
        )
        conditioned = np.concatenate(
            [event_array.astype(np.float32, copy=False), typed_embedding], axis=1
        )
        if not np.all(np.isfinite(conditioned)):
            raise ValueError("Typed descriptor forward pass produced non-finite values")
        return TypedEncoderOutput(
            family_embeddings=family_embeddings,
            typed_embedding=typed_embedding,
            conditioned_detector_event_features=conditioned,
            object_counts={
                family_name: family.counts.copy()
                for family_name, family in batch.families.items()
            },
        )
