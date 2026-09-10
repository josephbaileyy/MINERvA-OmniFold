"""Bounded PET v2 source audit with lossless raw capture and separate verdicts.

The reader boundary never selects events. The public runner takes a reader
factory so synthetic validation has no ROOT dependency. Real access belongs to
the separately authorized launcher. No normalization statistics are fitted.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import math
import time
import traceback
from collections import Counter
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

import numpy as np
from numpy.typing import ArrayLike

import typed_descriptor_source_smoke as source
import typed_descriptors as typed

AUDIT_SCHEMA = "pet-v2-source-audit-v1"
SCHEMA_SHA256 = "102a409635e422c6688ee9fa7d98206c1048ae87199679b1a8d5d59c46f1e879"
BRANCH_SHA256 = "a5704bb33229b51d7ed3e185374032d487427133a186c7198eaee29e52b21f69"
ENTRY_STOP = 4096
LIMITS = {
    "wall_seconds": 1800,
    "memory_bytes": 8 * 2**30,
    "output_bytes": 2**30,
    "threads": 4,
    "cpu_seconds": 3600,
}
# Reserve space for both native logs and a terminal receipt, including failures.
FILE_LIMIT = 32 * 2**20
OUTPUT_RESERVE = 4 * FILE_LIMIT
PROHIBITIONS = (
    "do_not_select_passing_subset",
    "do_not_construct_C_ML",
    "do_not_move_central",
    "do_not_start_leg_2",
    "do_not_retry_unchanged",
)
NON_CLAIMS = (
    "Fixed-source telemetry only; deterministic convenience sample, unselected.",
    "No pass_reco, production normalization, fit, training or adoption.",
    "No calibrated PID, population support, disjoint-particle census or coverage.",
    "OI-126 pairing remains declined; existing C_stat is unverified.",
    "No PET total covariance is adopted; Gate 6 remains blocked.",
)


def canonical_json(value: Any) -> bytes:
    """Serialize receipt objects as canonical strict ASCII JSON bytes."""
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("ascii")


def raw_encoding(value: Any) -> dict[str, Any]:
    """Encode numeric bytes, including NaN payloads, without sanitizing values.

    Ragged sequences retain child dtype/shape metadata. Non-numeric malformed
    inputs retain their JSON value or explicit type/repr, never a pickle.
    """
    try:
        numeric = np.asarray(value)
    except (ValueError, TypeError):
        numeric = np.asarray(None)
    if numeric.dtype.kind in "biuf":
        numeric = np.ascontiguousarray(numeric) if numeric.ndim else numeric
        return {
            "dtype": numeric.dtype.str,
            "shape": list(numeric.shape),
            "bytes_base64": base64.b64encode(numeric.tobytes()).decode("ascii"),
        }
    if isinstance(value, (list, tuple)):
        return {"sequence": [raw_encoding(child) for child in value]}
    return {"malformed_type": type(value).__name__, "repr": repr(value)}


def branch_contract() -> dict[str, dict[str, Any]]:
    """Return the explicit numeric structure contract, not historical type data."""
    result = {}
    for name in source.REQUIRED_BRANCHES:
        if name in source._SCALAR_BRANCHES:
            shape = []
        elif name in source.PRONG_NESTED_BRANCHES:
            shape = [None, 4]
        elif name in source._FIXED_WIDTH_BRANCHES:
            shape = [source._FIXED_WIDTH_BRANCHES[name]]
        else:
            shape = [None]
        result[name] = {"shape": shape, "numeric_kinds": "biuf"}
    return result


class AuditReader(Protocol):
    """Expose metadata before any of the 75 payload branches are requested."""

    metadata: dict[str, Any]

    def read_entry(self, entry: int) -> Mapping[str, Any]:
        """Return raw values for one entry, preserving numeric dtypes."""

    def close(self) -> None:
        """Close the single source handle."""


class ResourceLimit(RuntimeError):
    """A hard ceiling stopped the audit; no retry or sample truncation follows."""


class AuditOutput:
    """Write closed, hashed artifacts inside a new, byte-bounded namespace.

    Parameters
    ----------
    directory : Path
        New output directory. Existing output is never overwritten.
    check_resources : callable
        Called before each write and each source operation.
    """

    def __init__(self, directory: Path, check_resources: Callable[[], None]) -> None:
        directory.mkdir(parents=True, exist_ok=False)
        self.directory = directory
        self.check_resources = check_resources
        self.total_bytes = 0
        self.artifacts: dict[str, dict[str, Any]] = {}

    def write(self, name: str, payload: bytes) -> None:
        """Write one artifact or stop before exceeding the output reserve."""
        self.check_resources()
        if len(payload) > FILE_LIMIT or self.total_bytes + len(payload) > (
            LIMITS["output_bytes"] - OUTPUT_RESERVE
        ):
            raise ResourceLimit("output_bytes: artifact would exceed ceiling")
        path = self.directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(payload)
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        self.artifacts[name] = {"sha256": digest, "bytes": len(payload)}
        self.total_bytes += len(payload)


def validate_metadata(metadata: dict[str, Any], spec: source.FixedSourceSpec) -> None:
    """Reject identity, missing branches, or incompatible shapes before payload."""
    if metadata["uuid"] != spec.expected_uuid:
        raise ValueError("ROOT UUID mismatch")
    if metadata["tree"] != source.TREE_NAME:
        raise ValueError("tree mismatch")
    if type(metadata["entries"]) is not int or metadata["entries"] < ENTRY_STOP:
        raise ValueError("short or malformed tree entry count; no backfill")
    if list(metadata["branches"]) != list(source.REQUIRED_BRANCHES):
        raise ValueError("ordered branch metadata mismatch")
    for name, expected in branch_contract().items():
        observed = metadata["branches"][name]
        if np.dtype(observed["dtype"]).kind not in expected["numeric_kinds"]:
            raise ValueError(f"{name}: nonnumeric dtype")
        shape = observed["shape"]
        if len(shape) != len(expected["shape"]) or any(
            actual is not None and wanted is not None and actual != wanted
            for actual, wanted in zip(shape, expected["shape"])
        ):
            raise ValueError(f"{name}: incompatible metadata shape")
        if observed.get("unapproved_count_dependencies"):
            raise ValueError(f"{name}: unapproved count dependency")
        if not observed.get("declaration"):
            raise ValueError(f"{name}: missing verbatim type declaration")


def validate_row(raw: Mapping[str, Any]) -> None:
    """Validate all lengths and integer keys without repairing or dropping rows."""
    if set(raw) != set(source.REQUIRED_BRANCHES):
        raise ValueError("raw branch mapping mismatch")
    for name in source._SCALAR_BRANCHES:
        if np.asarray(raw[name]).shape != ():
            raise ValueError(f"{name}: expected scalar")
    for name in (
        source.EVENT_KEY_BRANCHES
        + source.GENERIC_COUNT_BRANCHES
        + (source.BLOB_COUNT_BRANCHES + (source.PRONG_COUNT_BRANCH,))
    ):
        value = raw[name]
        if not np.isfinite(value) or value != np.floor(value) or value < 0:
            raise ValueError(f"{name}: expected nonnegative integer")
        if value > np.iinfo(np.int64).max:
            raise ValueError(f"{name}: int64 overflow")
    for name, count in source._COUNTED_BRANCHES.items():
        if np.asarray(raw[name]).shape != (int(raw[count]),):
            raise ValueError(f"{name}: counted-vector shape mismatch")
    for name, width in source._FIXED_WIDTH_BRANCHES.items():
        if np.asarray(raw[name]).shape != (width,):
            raise ValueError(f"{name}: fixed width mismatch")
    for name in source.PRONG_NESTED_BRANCHES:
        if len(raw[name]) != raw["n_prongs"] or any(
            np.asarray(vector).shape != (4,) for vector in raw[name]
        ):
            raise ValueError(f"{name}: prong width/count mismatch")
    for names in (source.GENERIC_VALUE_BRANCHES, source.BLOB_BASES):
        if len({len(raw[name]) for name in names}) != 1:
            raise ValueError("unaligned object vectors")


def map_row(
    raw: Mapping[str, Any], spec: source.FixedSourceSpec, entry: int
) -> source.SourceContractBatch:
    """Use the existing mapper on exactly one validated source row."""
    validate_row(raw)
    provenance = typed.RowProvenance(
        np.asarray([spec.shard_file_ordinal], dtype=np.uint32),
        np.asarray([typed.SourceTree.MASTER_ANA_DEV], dtype=np.uint8),
        np.asarray([entry], dtype=np.uint64),
    )
    return source.SourceContractBatch(
        source._build_p12(raw)[None],
        source._build_detector_event_block(raw)[None],
        np.asarray([[raw[name] for name in source.EVENT_KEY_BRANCHES]], dtype=np.int64),
        np.asarray([spec.role_code], dtype=np.uint8),
        typed.build_descriptor_batch(
            provenance=provenance,
            photon_rows=[source._build_photons(raw)],
            blob_rows=[source._build_blobs(raw)],
            prong_rows=[source._build_prongs(raw)],
        ),
    )


# Independent source-to-field table; deliberately does not call mapper builders.
FIELD_TABLE: dict[str, dict[str, tuple[str | tuple[str, ...], slice | int | None]]] = {
    "prongs": {
        "position": ("prong_part_pos", slice(0, 3)),
        "time": ("prong_part_pos", 3),
        "four_momentum": ("prong_part_E", None),
        "dedx": ("prong_dEdXMean", None),
        "score": ("prong_part_score", None),
        "mass": ("prong_part_mass", None),
        "charge": ("prong_part_charge", None),
        "raw_pid": ("prong_part_pid", None),
    },
    "blobs": {
        "position": (
            ("MasterAnaDev_BlobX", "MasterAnaDev_BlobY", "MasterAnaDev_BlobZ"),
            None,
        ),
        "time": ("MasterAnaDev_BlobT", None),
        "time_position": ("MasterAnaDev_BlobTPos", None),
        "total_energy": ("MasterAnaDev_BlobTotalE", None),
        "is_3d": ("MasterAnaDev_BlobIs3D", None),
        "cluster_count": ("MasterAnaDev_BlobNClusters", None),
    },
    "photons": {
        "direction": ("direction", None),
        "dedx": ("dEdx", None),
        "time": ("time", None),
        **{
            f"{kind}_{field}": (f"{kind}_{suffix}", None)
            for kind in ("energy", "evis")
            for field, suffix in (
                ("tracker", "trkr"),
                ("ecal", "ecal"),
                ("hcal", "hcal"),
                ("scal_x", "scal_X"),
                ("scal_uv", "scal_UV"),
            )
        },
    },
}


def expected_field(
    raw: Mapping[str, Any], family: str, name: str, token: int
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """Independently calculate v2 storage and masks from the explicit table."""
    branch, component = FIELD_TABLE[family][name]
    if family == "photons":
        value = raw[f"gamma{token}_{branch}"]
    elif isinstance(branch, tuple):
        value = [raw[column][token] for column in branch]
    else:
        value = raw[branch][token]
    if component is not None:
        value = value[component]
    numeric = np.asarray(value, dtype=np.float64).reshape(-1)
    valid = np.isfinite(numeric) & ~np.isin(numeric, [-999, -9999])
    if family == "prongs" and name in ("score", "mass"):
        valid &= numeric != -1
    categorical = name in ("raw_pid", "charge", "is_3d")
    if categorical:
        valid &= numeric == np.floor(numeric)
    if name in ("position", "direction", "four_momentum"):
        valid[:] = valid.all()
    if family == "prongs" and name == "charge":
        valid &= raw["prong_part_pid"][token] == 3
    safe = np.where(np.isfinite(numeric), numeric, 0)
    dtype = np.int32 if categorical else np.float32
    bounds = np.iinfo(np.int32) if categorical else np.finfo(np.float32)
    if np.any(safe < bounds.min) or np.any(safe > bounds.max):
        raise ValueError(f"{family}.{name}: storage overflow")
    return safe.astype(dtype), valid


def _require_array_equal(actual: ArrayLike, expected: ArrayLike) -> None:
    """Require exact shape/value equality without importing NumPy test utilities."""
    if not np.array_equal(actual, expected):
        raise AssertionError("Array shape or values differ")


def check_mapping(raw: Mapping[str, Any], batch: source.SourceContractBatch) -> None:
    """Require independent values/masks/membership equality for every typed token."""
    members = {
        "prongs": list(range(int(raw["n_prongs"]))),
        "blobs": list(range(len(raw["MasterAnaDev_BlobX"]))),
        "photons": [slot for slot in (1, 2) if raw[f"gamma{slot}_E"] > 1e-5],
    }
    for family, indices in members.items():
        mapped = batch.descriptors.families[family]
        _require_array_equal(mapped.offsets, [0, len(indices)])
        _require_array_equal(mapped.counts, [len(indices)])
        if not mapped.token_mask.all() or not mapped.enabled.all():
            raise AssertionError(f"{family}: structural presence or enablement changed")
        for field in FIELD_TABLE[family]:
            for mapped_index, raw_index in enumerate(indices):
                values, masks = expected_field(raw, family, field, raw_index)
                actual = mapped.values[field][mapped_index]
                if actual.dtype != values.dtype or actual.tobytes() != values.tobytes():
                    raise AssertionError(
                        f"{family}.{field}[{raw_index}]: raw storage mismatch"
                    )
                _require_array_equal(mapped.masks[field][mapped_index], masks)


def identity_normalization() -> typed.FrozenNormalization:
    """Construct diagnostic identity statistics; this object is never fitted."""
    policy = "SOURCE_AUDIT_IDENTITY_NOT_FITTED_NOT_FOR_TRAINING"
    return typed.FrozenNormalization(
        typed.descriptor_schema_digest(),
        hashlib.sha256(policy.encode()).hexdigest(),
        policy,
        {
            contract.name: source._identity_normalization(contract)
            for contract in typed.FAMILY_CONTRACTS
        },
    )


# Preserve the original absolute allowance at the elementary activation, where
# outputs are bounded by one. Dot and pooling error scale with their operands.
ACTIVATION_ATOL = 1e-6


def projection_error_budget(
    features: np.ndarray[Any, Any],
    weight: np.ndarray[Any, Any],
    bias: np.ndarray[Any, Any],
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """Return float64 tanh projections and float32 forward-error allowances.

    The gamma bound covers products, arbitrary-order summation and bias addition.
    Monotonic tanh propagates the dot interval, including saturation. The added
    activation allowance is a checked numerical contract, not a libm guarantee.
    Inputs are the identical float32 operands supplied to both backends.
    """
    values = features.astype(np.float64)
    weights = weight.astype(np.float64)
    offsets = bias.astype(np.float64)
    operations = 2 * features.shape[1] + 2
    unit_roundoff = 2.0**-24
    gamma = operations * unit_roundoff / (1 - operations * unit_roundoff)
    linear = values @ weights + offsets
    magnitude = np.abs(values) @ np.abs(weights) + np.abs(offsets)
    # Include the much smaller float64 oracle arithmetic error and gradual
    # underflow allowance. No relative-to-output criterion is used here.
    oracle_gamma = operations * 2.0**-53 / (1 - operations * 2.0**-53)
    radius = (gamma + oracle_gamma) * magnitude + operations * 2.0**-149
    projected = np.tanh(linear)
    error = (
        np.maximum(
            np.tanh(linear + radius) - projected,
            projected - np.tanh(linear - radius),
        )
        + ACTIVATION_ATOL
    )
    return projected, error


def require_within_budget(
    actual: np.ndarray[Any, Any],
    oracle: np.ndarray[Any, Any],
    budget: np.ndarray[Any, Any],
    label: str,
) -> float:
    """Reject nonfinite results and report the largest used error fraction."""
    difference = np.abs(actual.astype(np.float64) - oracle)
    if not np.isfinite(difference).all() or np.any(difference > budget):
        raise AssertionError(f"{label}: forward rounding budget exceeded")
    return float(np.max(difference / np.maximum(budget, 2.0**-149), initial=0))


class ForwardCheck:
    """Compare fixed seed-zero, width-16 NumPy and Keras projectors, without fit."""

    def __init__(self) -> None:
        import typed_descriptor_keras as adapter

        self.adapter = adapter
        self.normalization = identity_normalization()
        self.reference = typed.ReferenceTypedDescriptorEncoder.initialize(
            self.normalization, projection_dim=16, seed=0
        )
        self.model = adapter.build_keras_typed_descriptor_adapter(
            self.normalization,
            hidden_units=(),
            token_embedding_dim=16,
            activation="tanh",
        )
        self.initialized = False
        self.numerical_checks: list[dict[str, Any]] = []

    def __call__(self, batch: source.SourceContractBatch) -> None:
        """Require finite C0/C1 outputs, exact zero C0, and matched 64-wide rows."""
        inputs = self.adapter.prepare_keras_inputs(
            batch.descriptors, batch.detector_event_block
        )
        if not self.initialized:
            self.model(inputs, training=False)
            for family, encoder in self.reference.family_encoders.items():
                self.model.family_encoders[family].token_mlp.set_weights(
                    [encoder.weight, encoder.bias]
                )
            self.initialized = True
        expected = self.reference.forward(
            batch.descriptors, batch.detector_event_block
        ).conditioned_detector_event_features
        actual = self.model(inputs, training=False).numpy()
        if (
            expected.shape != (batch.descriptors.row_count, 64)
            or not np.isfinite(actual).all()
            or not np.isfinite(expected).all()
        ):
            raise AssertionError("nonfinite or malformed forward output")
        if actual.shape != expected.shape:
            raise AssertionError(
                f"NumPy/Keras forward shapes differ: {expected.shape} != {actual.shape}"
            )
        _require_array_equal(actual[:, :13], expected[:, :13])
        self._check_numerics(batch, inputs, expected, actual)
        for family in FIELD_TABLE:
            inputs[f"{family}_enabled"] = np.zeros_like(inputs[f"{family}_enabled"])
        disabled = self.model(inputs, training=False).numpy()
        if disabled.shape != actual.shape or np.any(disabled[:, 13:] != 0):
            raise AssertionError("C0 must have exactly zero 51 descriptor columns")
        _require_array_equal(disabled[:, :13], batch.detector_event_block)
        disabled_batch = typed.TypedDescriptorBatch(
            provenance=batch.descriptors.provenance,
            families={
                name: replace(family, enabled=np.zeros_like(family.enabled))
                for name, family in batch.descriptors.families.items()
            },
        )
        disabled_reference = self.reference.forward(
            disabled_batch, batch.detector_event_block
        ).conditioned_detector_event_features
        _require_array_equal(disabled, disabled_reference)

    def _check_numerics(
        self,
        batch: source.SourceContractBatch,
        inputs: dict[str, np.ndarray[Any, Any]],
        expected: np.ndarray[Any, Any],
        actual: np.ndarray[Any, Any],
    ) -> None:
        """Check operands exactly, then each backend against the float64 oracle."""
        for family, encoder in self.reference.family_encoders.items():
            ragged = batch.descriptors.families[family]
            layer = self.model.family_encoders[family]
            features = encoder.contract.prepare_features(ragged, encoder.normalization)
            keras_features = layer.prepare_features(
                inputs[f"{family}_values"],
                inputs[f"{family}_masks"],
                inputs[f"{family}_token_mask"],
            ).numpy()
            _require_array_equal(features, keras_features)
            weights = layer.token_mlp.get_weights()
            _require_array_equal(weights[0], encoder.weight)
            _require_array_equal(weights[1], encoder.bias)
            oracle, token_budget = projection_error_budget(
                features, encoder.weight, encoder.bias
            )
            numpy_tokens = encoder.project(ragged)
            keras_tokens = layer.token_mlp(keras_features, training=False).numpy()
            keras_tokens *= ragged.token_mask[:, None]
            oracle *= ragged.token_mask[:, None]
            token_budget *= ragged.token_mask[:, None]
            token_fractions = {
                name: require_within_budget(tokens, oracle, token_budget, name)
                for name, tokens in (("numpy", numpy_tokens), ("keras", keras_tokens))
            }
            output_slice = self.model.family_output_slice(family)
            start_column = output_slice.start
            fractions = {"numpy": 0.0, "keras": 0.0}
            max_budget = 0.0
            max_error = {"numpy": 0.0, "keras": 0.0}
            for row in range(ragged.row_count):
                start, stop = ragged.offsets[row : row + 2]
                count = int(stop - start)
                gamma = count * 2.0**-24 / (1 - count * 2.0**-24)
                pooled = oracle[start:stop].sum(axis=0)
                budget = token_budget[start:stop].sum(axis=0)
                budget += gamma * (
                    np.abs(oracle[start:stop]) + token_budget[start:stop]
                ).sum(axis=0)
                pooled *= ragged.enabled[row]
                budget *= ragged.enabled[row]
                max_budget = max(max_budget, float(budget.max(initial=0)))
                for name, output in (("numpy", expected), ("keras", actual)):
                    observed = output[row, start_column : start_column + 16]
                    fractions[name] = max(
                        fractions[name],
                        require_within_budget(observed, pooled, budget, name),
                    )
                    max_error[name] = max(
                        max_error[name],
                        float(np.max(np.abs(observed - pooled), initial=0)),
                    )
            _require_array_equal(
                actual[:, start_column + 16], expected[:, start_column + 16]
            )
            if len(self.numerical_checks) < len(FIELD_TABLE):
                self.numerical_checks.append(
                    {
                        "family": family,
                        "features_equal": True,
                        "weights_equal": True,
                        "features_sha256": hashlib.sha256(
                            features.tobytes()
                        ).hexdigest(),
                        "weights_sha256": hashlib.sha256(
                            encoder.weight.tobytes()
                        ).hexdigest(),
                        "max_token_error_fraction": token_fractions,
                        "max_pool_error_fraction": fractions,
                        "max_pool_absolute_error": max_error,
                        "max_pool_budget": max_budget,
                    }
                )


def _display(value: Any) -> Any:
    numeric = np.asarray(value)
    if numeric.ndim:
        return [_display(child) for child in numeric]
    scalar = numeric.item()
    return scalar if math.isfinite(scalar) else str(scalar)


class Telemetry:
    """Accumulate check denominators by role and anchor interval, retaining rows."""

    def __init__(self) -> None:
        self.tables: dict[str, dict[str, dict[str, int]]] = {}
        self.discrepancies = 0
        self.histograms: dict[str, Counter[str]] = {}
        self.ranges: dict[str, dict[str, Any]] = {}

    def observe(self, raw: Mapping[str, Any], role: str, entry: int) -> dict[str, Any]:
        """Return token-indexed observations and all simultaneous discrepancies."""
        interval = "anchor_0_16" if entry < 16 else "extension_16_4096"
        tables = self.tables.setdefault(f"{role}/{interval}", {})
        for name in (
            "pid_support_zero",
            "pid_support_later",
            "charge_support",
            "sentinel_score",
            "sentinel_mass",
            "prong_time",
            "photon_direction",
            "blob_cluster_count",
        ):
            tables.setdefault(name, {"eligible": 0, "missing": 0, "discrepancies": 0})
        observations: dict[str, Any] = {
            "role": role,
            "entry": entry,
            "interval": interval,
            "checks": [],
        }

        def check(
            name: str, token: int, eligible: bool, agrees: bool, detail: Any
        ) -> None:
            counts = tables.setdefault(
                name, {"eligible": 0, "missing": 0, "discrepancies": 0}
            )
            counts["eligible" if eligible else "missing"] += 1
            discrepancy = eligible and not agrees
            counts["discrepancies"] += int(discrepancy)
            self.discrepancies += int(discrepancy)
            observations["checks"].append(
                {
                    "check": name,
                    "token": token,
                    "verdict": (
                        "NOT_TESTED"
                        if not eligible
                        else "DISCREPANCY" if discrepancy else "PASS"
                    ),
                    "observation": detail,
                }
            )

        prongs = []
        for token in range(int(raw["n_prongs"])):
            pid, score, mass, charge = (
                raw[name][token]
                for name in (
                    "prong_part_pid",
                    "prong_part_score",
                    "prong_part_mass",
                    "prong_part_charge",
                )
            )
            values = {
                name: _display(raw[name][token])
                for name in source.PRONG_VECTOR_BRANCHES + source.PRONG_NESTED_BRANCHES
            }
            masks = {
                field: expected_field(raw, "prongs", field, token)[1].tolist()
                for field in FIELD_TABLE["prongs"]
            }
            values["masks"] = masks
            values["token"] = token
            values["index_class"] = "zero" if token == 0 else "later"
            momentum = np.asarray(raw["prong_part_E"][token], dtype=np.float64)
            lepton = np.asarray(raw["MasterAnaDev_leptonE"], dtype=np.float64)
            residual = momentum - lepton
            values["tuple_lepton_residual"] = _display(residual)
            values["tuple_lepton_match"] = bool(
                np.isfinite(residual).all()
                and np.allclose(momentum, lepton, rtol=1e-5, atol=0.01)
            )
            # Residuals are diagnostics, not a producer ordering criterion.
            for field, mask in masks.items():
                stored, _ = expected_field(raw, "prongs", field, token)
                self._count(f"{role}/{interval}/prong_valid_missing/{field}", mask)
                self._range(
                    f"{role}/{interval}/prong_valid_range/{field}",
                    stored[np.asarray(mask)],
                )
            prongs.append(values)
            check(
                f"pid_support_{values['index_class']}",
                token,
                True,
                pid in (-999, 0, 3, 8, 13),
                _display(pid),
            )
            check(
                "charge_support",
                token,
                True,
                (
                    charge == -999
                    if pid == -999
                    else (
                        charge in (0, 1, 2)
                        if pid == 3
                        else charge == 0 if pid in (0, 8, 13) else False
                    )
                ),
                [_display(pid), _display(charge), masks["charge"]],
            )
            expected = {
                -999: (-1, -1),
                0: (0, -1),
                3: (1, 105.658),
                8: (None, 938.272),
                13: (None, -1),
            }
            if pid in expected:
                expected_score, expected_mass = expected[pid]
                score_ok = (
                    (0 <= score <= 1)
                    if expected_score is None
                    else abs(score - expected_score) <= 1e-6
                )
                if pid == -999:
                    score_ok = score == -1
                mass_ok = abs(mass - expected_mass) <= (0.01 if pid in (3, 8) else 0)
                check(
                    "sentinel_score",
                    token,
                    True,
                    bool(score_ok),
                    [_display(pid), _display(score)],
                )
                check(
                    "sentinel_mass",
                    token,
                    True,
                    bool(mass_ok),
                    [_display(pid), _display(mass)],
                )
            else:
                check("sentinel_score", token, False, False, _display(score))
                check("sentinel_mass", token, False, False, _display(mass))
            time_value = raw["prong_part_pos"][token][3]
            check(
                "prong_time",
                token,
                bool(masks["time"][0]),
                0 <= time_value <= 10000,
                _display(time_value),
            )
        observations["prongs"] = prongs
        photons = []
        for slot in (1, 2):
            energy = raw[f"gamma{slot}_E"]
            state = (
                "ambiguous"
                if not np.isfinite(energy)
                else "present" if energy > 1e-5 else "absent_thresholded"
            )
            fields = {
                suffix: _display(raw[f"gamma{slot}_{suffix}"])
                for suffix in source.PHOTON_SCALAR_SUFFIXES + ("direction",)
            }
            fields.update(slot=slot, presence=state)
            direction = np.asarray(raw[f"gamma{slot}_direction"], dtype=np.float64)
            valid = bool(
                (np.isfinite(direction) & ~np.isin(direction, [-999, -9999])).all()
            )
            norm = float(np.linalg.norm(direction))
            fields["direction_valid"] = valid
            fields["direction_norm"] = _display(norm)
            fields["subsystem_sums_not_energy_balance"] = {
                kind: _display(
                    sum(
                        raw[f"gamma{slot}_{kind}_{suffix}"]
                        for suffix in ("trkr", "ecal", "hcal", "scal_X", "scal_UV")
                    )
                )
                for kind in ("energy", "evis")
            }
            photons.append(fields)
            check(
                "photon_direction",
                slot,
                state == "present" and valid,
                abs(norm - 1) <= 1e-4,
                fields["direction_norm"],
            )
        observations["photons"] = photons
        blobs = []
        for token in range(len(raw["MasterAnaDev_BlobX"])):
            fields = {name: _display(raw[name][token]) for name in source.BLOB_BASES}
            fields["token"] = token
            count = raw["MasterAnaDev_BlobNClusters"][token]
            valid = np.isfinite(count) and count not in (-999, -9999)
            check(
                "blob_cluster_count",
                token,
                bool(valid),
                count >= 0 and count == np.floor(count),
                _display(count),
            )
            fields["zero_fields"] = [
                name for name in source.BLOB_BASES if raw[name][token] == 0
            ]
            blobs.append(fields)
        observations["blobs"] = blobs
        for prong in prongs:
            self._count(
                f"{role}/{interval}/pid/{prong['index_class']}", prong["prong_part_pid"]
            )
            self._count(
                f"{role}/{interval}/pid_score_mass_charge",
                [
                    prong[f"prong_part_{field}"]
                    for field in ("pid", "score", "mass", "charge")
                ],
            )
            self._count(
                f"{role}/{interval}/pid_charge_mask",
                [
                    prong["prong_part_pid"],
                    prong["prong_part_charge"],
                    prong["masks"]["charge"],
                ],
            )
            self._count(
                f"{role}/{interval}/lepton_match/{prong['index_class']}",
                prong["tuple_lepton_match"],
            )
        for photon in photons:
            self._count(
                f"{role}/{interval}/photon_presence/slot{photon['slot']}",
                photon["presence"],
            )
            for field in source.PHOTON_SCALAR_SUFFIXES:
                self._count(
                    f"{role}/{interval}/photon_zero_sentinel/{field}",
                    (
                        "zero"
                        if photon[field] == 0
                        else "sentinel" if photon[field] in (-999, -9999) else "other"
                    ),
                )
        for blob in blobs:
            self._count(
                f"{role}/{interval}/blob_Is3D_zero_fields",
                [blob["MasterAnaDev_BlobIs3D"], blob["zero_fields"]],
            )
        for name in (
            source.PRONG_VECTOR_BRANCHES
            + source.PRONG_NESTED_BRANCHES
            + source.BLOB_BASES
        ):
            self._range(f"{role}/{interval}/{name}", raw[name])
        for token in range(int(raw["n_prongs"])):
            self._range(
                f"{role}/{interval}/score_by_pid/{_display(raw['prong_part_pid'][token])}",
                raw["prong_part_score"][token],
            )
        observations["cooccurring_counts"] = {
            "prongs": len(prongs),
            "blobs": len(blobs),
            "photons_present": sum(slot["presence"] == "present" for slot in photons),
            "photons_ambiguous": sum(
                slot["presence"] == "ambiguous" for slot in photons
            ),
        }
        return observations

    def _count(self, name: str, value: Any) -> None:
        self.histograms.setdefault(name, Counter())[canonical_json(value).decode()] += 1

    def _range(self, name: str, values: Any) -> None:
        numeric = np.asarray(values, dtype=np.float64).reshape(-1)
        table = self.ranges.setdefault(
            name,
            {
                "finite": 0,
                "nonfinite": 0,
                "sentinel": 0,
                "zero": 0,
                "min": None,
                "max": None,
            },
        )
        finite = numeric[np.isfinite(numeric)]
        table["finite"] += int(finite.size)
        table["nonfinite"] += int(numeric.size - finite.size)
        table["sentinel"] += int(np.isin(numeric, [-999, -9999, -1]).sum())
        table["zero"] += int((numeric == 0).sum())
        if finite.size:
            table["min"] = (
                float(finite.min())
                if table["min"] is None
                else min(table["min"], float(finite.min()))
            )
            table["max"] = (
                float(finite.max())
                if table["max"] is None
                else max(table["max"], float(finite.max()))
            )

    def summary(self) -> dict[str, Any]:
        """Return raw histograms and unconverted ranges, including sentinel counts."""
        return {
            "histograms": {
                name: dict(counts) for name, counts in self.histograms.items()
            },
            "ranges_native_units_including_sentinels": self.ranges,
        }

    def verdicts(self) -> dict[str, Any]:
        """Attach NOT_TESTED to zero eligible denominators, never PASS."""
        return {
            group: {
                name: {
                    **counts,
                    "verdict": (
                        "NOT_TESTED"
                        if not counts["eligible"]
                        else "DISCREPANCY" if counts["discrepancies"] else "PASS"
                    ),
                }
                for name, counts in checks.items()
            }
            for group, checks in self.tables.items()
        }


def _shard_bytes(
    batch: source.SourceContractBatch, provenance: typed.ShardProvenance
) -> bytes:
    arrays = typed.descriptor_shard_arrays(batch.descriptors, provenance)
    arrays.update(
        {
            "audit.schema": np.asarray(AUDIT_SCHEMA),
            "audit.event_keys": batch.tuple_event_keys,
            "audit.source_role": batch.source_role,
            "audit.p12": batch.p12_clusters,
            "audit.event": batch.detector_event_block,
        }
    )
    buffer = io.BytesIO()
    np.savez_compressed(buffer, **arrays)
    buffer.seek(0)
    with np.load(buffer, allow_pickle=False) as loaded:
        _, recovered_provenance = typed.descriptor_batch_from_arrays(loaded)
        if recovered_provenance != provenance or set(loaded.files) != set(arrays):
            raise AssertionError("shard provenance/array inventory round trip failed")
        for name, expected in arrays.items():
            actual = loaded[name]
            if (
                actual.dtype != expected.dtype
                or actual.shape != expected.shape
                or actual.tobytes() != expected.tobytes()
            ):
                raise AssertionError(f"round trip differs: {name}")
    return buffer.getvalue()


def run_audit(
    repo_root: Path,
    output_directory: Path,
    *,
    reader_factory: Callable[[source.ResolvedSource], AuditReader],
    forward_check: Callable[[source.SourceContractBatch], None],
    check_resources: Callable[[], None],
    bindings: dict[str, Any],
) -> dict[str, Any]:
    """Audit only the pinned two sources and [0,4096), retaining partial failures.

    Parameters
    ----------
    repo_root, output_directory : Path
        Checkout root and a new output namespace.
    reader_factory, forward_check, check_resources : callable
        Explicit real or fake boundaries. The receipt records the supplied
        execution mode; only the launcher supplies the real implementations.
    bindings : dict
        Authorization, code, protocol, schema and environment bindings.

    Returns
    -------
    dict
        Terminal receipt. Mapping failures return an incomplete receipt, with
        exact attempted, captured, mapped and completed entry lists.
    """
    output = AuditOutput(output_directory, check_resources)
    receipt: dict[str, Any] = {
        "schema": AUDIT_SCHEMA,
        "bindings": bindings,
        "limits": LIMITS,
        "sources": [],
        "exceptions": [],
        "non_claims": NON_CLAIMS,
        "prohibitions_applied": PROHIBITIONS,
        "mapping": "NOT_TESTED",
        "semantic": "UNRESOLVED",
        "release": "RELEASE_UNVERIFIED",
        "object_families": {
            name: "UNRESOLVED"
            for name in (
                "photons",
                "blobs",
                "prong_hypotheses",
                "shared_objects_primary_lepton",
            )
        },
        "terminal": "INCOMPLETE",
        "checks": {},
    }
    # A durable non-acceptance marker survives a native abort or an uncatchable kill.
    (output_directory / "interrupted.json").write_bytes(
        canonical_json(
            {
                "schema": AUDIT_SCHEMA,
                "terminal": "INCOMPLETE",
                "mapping": "NOT_TESTED",
                "bindings": bindings,
                "non_claims": NON_CLAIMS,
                "recovery": "Absent receipt.json means incomplete; raw files and progress.jsonl are partial evidence only.",
            }
        )
    )
    journal = (output_directory / "progress.jsonl").open("xb", buffering=0)
    started = time.monotonic()
    telemetry = Telemetry()
    readers = []
    payload_hasher = hashlib.sha256()
    branch_hashers = {name: hashlib.sha256() for name in source.REQUIRED_BRANCHES}
    row_keys = []
    groups: dict[tuple[Any, ...], list[int]] = {}
    current: dict[str, Any] = {"phase": "preflight"}
    try:
        if (
            typed.descriptor_schema_digest() != SCHEMA_SHA256
            or source.required_branch_digest() != BRANCH_SHA256
            or len(source.REQUIRED_BRANCHES) != 75
        ):
            raise ValueError("schema/branch binding mismatch")
        sources = source.resolve_fixed_sources(repo_root)
        if (
            tuple(item.spec for item in sources) != source.FIXED_SOURCES
            or len(sources) != 2
        ):
            raise ValueError("fixed source inventory mismatch")
        for resolved in sources:
            spec = resolved.spec
            current = {"phase": "metadata", "role": spec.role}
            progress = {
                "role": spec.role,
                "playlist": spec.playlist,
                "path": resolved.path,
                "manifest": spec.manifest_relative_path,
                "manifest_sha256": resolved.manifest_sha256,
                "manifest_line": 1,
                "requested_entries": list(range(ENTRY_STOP)),
                "attempted_entries": [],
                "captured_entries": [],
                "mapped_entries": [],
                "completed_entries": [],
            }
            receipt["sources"].append(progress)
            check_resources()
            reader = reader_factory(resolved)
            readers.append(reader)
            progress["metadata"] = reader.metadata
            output.write(f"{spec.role}/metadata.json", canonical_json(reader.metadata))
            validate_metadata(reader.metadata, spec)
        provenance = typed.ShardProvenance(
            manifest_sha256=hashlib.sha256(
                canonical_json([item.manifest_sha256 for item in sources])
            ).hexdigest(),
            playlist="1B data + 1A MC bounded unselected source audit",
            production_provenance=(
                ("entry_interval", "[0,4096)"),
                ("purpose", AUDIT_SCHEMA),
            ),
            source_files=tuple(
                typed.SourceFileMetadata(
                    item.spec.shard_file_ordinal, item.path, item.spec.expected_uuid
                )
                for item in sources
            ),
        )
        for resolved, reader, progress in zip(sources, readers, receipt["sources"]):
            spec = resolved.spec
            pending = []
            for entry in range(ENTRY_STOP):
                current = {"phase": "read", "role": spec.role, "entry": entry}
                check_resources()
                progress["attempted_entries"].append(entry)
                journal.write(canonical_json({**current, "event": "attempted"}) + b"\n")
                raw = reader.read_entry(entry)
                identity = {
                    "role": spec.role,
                    "uuid": reader.metadata["uuid"],
                    "tree": source.TREE_NAME,
                    "entry": entry,
                }
                names = list(source.REQUIRED_BRANCHES) + sorted(
                    set(raw) - set(source.REQUIRED_BRANCHES)
                )
                frames = [
                    {**identity, "branch": name, "raw": raw_encoding(raw[name])}
                    for name in names
                    if name in raw
                ]
                payload = canonical_json(frames)
                output.write(f"{spec.role}/raw/{entry:04d}.json", payload)
                payload_hasher.update(len(payload).to_bytes(8, "big") + payload)
                for frame in frames:
                    if frame["branch"] in branch_hashers:
                        encoded = canonical_json(frame)
                        branch_hashers[frame["branch"]].update(
                            len(encoded).to_bytes(8, "big") + encoded
                        )
                progress["captured_entries"].append(entry)
                journal.write(canonical_json({**current, "event": "captured"}) + b"\n")
                current["phase"] = "validate_and_map"
                validate_row(raw)
                observation = telemetry.observe(raw, spec.role, entry)
                output.write(
                    f"{spec.role}/observations/{entry:04d}.json",
                    canonical_json(observation),
                )
                key = [int(raw[name]) for name in source.EVENT_KEY_BRANCHES]
                row_keys.append({**identity, "event_keys": key})
                groups.setdefault((spec.role, spec.playlist, *key), []).append(entry)
                batch = map_row(raw, spec, entry)
                check_mapping(raw, batch)
                _require_array_equal(batch.tuple_event_keys, [key])
                _require_array_equal(batch.source_role, [spec.role_code])
                _require_array_equal(batch.descriptors.provenance.source_entry, [entry])
                _require_array_equal(
                    batch.descriptors.provenance.source_file_ordinal,
                    [spec.shard_file_ordinal],
                )
                pending.append(batch)
                progress["mapped_entries"].append(entry)
                if len(pending) == 16:
                    current["phase"] = "forward_and_round_trip"
                    combined = source.collate_source_batches(pending)
                    check_resources()
                    forward_check(combined)
                    check_resources()
                    payload = _shard_bytes(combined, provenance)
                    name = f"{spec.role}/typed/{entry - 15:04d}-{entry + 1:04d}.npz"
                    output.write(name, payload)
                    # Closed-file bytes must match the round-tripped in-memory archive.
                    if (output.directory / name).read_bytes() != payload:
                        raise AssertionError(
                            "closed shard differs from round-tripped bytes"
                        )
                    progress["completed_entries"].extend(range(entry - 15, entry + 1))
                    journal.write(
                        canonical_json(
                            {
                                **current,
                                "event": "completed_chunk",
                                "entries": list(range(entry - 15, entry + 1)),
                            }
                        )
                        + b"\n"
                    )
                    pending.clear()
        output.write("telemetry-summary.json", canonical_json(telemetry.summary()))
        receipt["terminal"] = "COMPLETE"
        receipt["mapping"] = "PASS"
        receipt["checks"] = {
            name: "PASS"
            for name in (
                "identity_metadata",
                "alignment_membership",
                "independent_typed_values_masks",
                "round_trip",
                "finite_numpy_keras_agreement",
                "C0_C1_64_columns",
            )
        }
    except Exception as error:
        receipt["mapping"] = "FAIL"
        receipt["exceptions"].append(
            {
                **current,
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
            }
        )
    finally:
        for reader in readers:
            try:
                reader.close()
            except Exception as error:
                receipt["terminal"] = "INCOMPLETE"
                receipt["mapping"] = "FAIL"
                receipt["exceptions"].append(
                    {
                        "phase": "close",
                        "type": type(error).__name__,
                        "message": str(error),
                    }
                )
    journal.close()
    receipt["telemetry_summary"] = (
        telemetry.summary()
        if receipt["terminal"] != "COMPLETE"
        else "telemetry-summary.json"
    )
    receipt["semantic"] = "DISCREPANCY" if telemetry.discrepancies else "UNRESOLVED"
    receipt["correspondence_checks"] = telemetry.verdicts()
    receipt["semantic_qualification"] = (
        "Unexplained discrepancies block PASS; release applicability and producer ordering remain unresolved."
    )
    receipt["bounded_payload_sha256"] = payload_hasher.hexdigest()
    receipt["payload_digest_scope"] = "captured_entries only; not a whole-file checksum"
    receipt["per_branch_sha256"] = {
        name: hasher.hexdigest() for name, hasher in branch_hashers.items()
    }
    receipt["ordered_source_rows"] = row_keys
    receipt["duplicate_event_groups"] = [
        {"group": list(key), "entries": entries}
        for key, entries in groups.items()
        if len(entries) > 1
    ]
    receipt["wall_seconds"] = time.monotonic() - started
    receipt["artifacts"] = output.artifacts
    receipt["artifact_bytes_excluding_logs_receipt"] = output.total_bytes
    # The reserved terminal path remains available after a resource check fails.
    payload = canonical_json(receipt)
    if len(payload) > FILE_LIMIT:
        raise ResourceLimit("terminal receipt exceeds reserved file ceiling")
    with (output_directory / "receipt.json").open("xb") as stream:
        stream.write(payload)
    return receipt
