#!/usr/bin/env python3
"""Summarize the fixed PET typed-descriptor smoke without widening its scope.

The input shard must be the 32-row artifact produced by
``typed_descriptor_source_smoke.py`` from entries 0--15 of the two bound
sources.  This probe records mask support, raw categorical codes, and raw-scale
telemetry.  It does not infer physical units, calibration, population support,
or production normalization from the fixed sample.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Mapping

import numpy as np

import typed_descriptor_source_smoke as source_smoke
import typed_descriptors as typed


PROBE_SCHEMA = "pet-typed-semantic-fixed-sample-v1"
ROLE_NAMES = {
    int(source_smoke.ROLE_DATA): "data",
    int(source_smoke.ROLE_MC): "mc",
}


def _sha256_bytes(*arrays: np.ndarray) -> str:
    """Hash array dtype, shape, and canonical C-order bytes in sequence."""

    hasher = hashlib.sha256()
    for array in arrays:
        canonical = np.ascontiguousarray(array)
        hasher.update(canonical.dtype.str.encode("ascii"))
        hasher.update(b"\0")
        hasher.update(json.dumps(canonical.shape).encode("ascii"))
        hasher.update(b"\0")
        hasher.update(canonical.tobytes(order="C"))
        hasher.update(b"\0")
    return hasher.hexdigest()


def _component_summary(
    values: np.ndarray,
    validity: np.ndarray,
) -> list[dict[str, int | float | None]]:
    """Return reproducible valid-only raw-scale telemetry by component."""

    summaries: list[dict[str, int | float | None]] = []
    for component_index in range(values.shape[1]):
        component_values = values[validity[:, component_index], component_index]
        summary: dict[str, int | float | None] = {
            "component": component_index,
            "valid_count": int(component_values.size),
            "invalid_count": int(values.shape[0] - component_values.size),
            "minimum": None,
            "maximum": None,
            "sum": 0.0,
            "sum_of_squares": 0.0,
        }
        if component_values.size:
            finite_values = component_values.astype(np.float64, copy=False)
            summary.update(
                {
                    "minimum": float(finite_values.min()),
                    "maximum": float(finite_values.max()),
                    "sum": float(finite_values.sum()),
                    "sum_of_squares": float(np.square(finite_values).sum()),
                }
            )
        summaries.append(summary)
    return summaries


def _categorical_support(
    values: np.ndarray,
    validity: np.ndarray,
) -> list[dict[str, object]]:
    """Return observed valid categorical codes and their counts by component."""

    support: list[dict[str, object]] = []
    for component_index in range(values.shape[1]):
        component_values = values[validity[:, component_index], component_index]
        codes, counts = np.unique(component_values.astype(np.int64), return_counts=True)
        support.append(
            {
                "component": component_index,
                "codes": [
                    {"code": int(code), "count": int(count)}
                    for code, count in zip(codes, counts, strict=True)
                ],
            }
        )
    return support


def _role_token_mask(
    family: typed.RaggedFamilyBatch,
    source_role: np.ndarray,
    role_code: int,
) -> np.ndarray:
    """Select family tokens whose owning event row has the requested role."""

    row_lengths = np.diff(family.offsets)
    token_roles = np.repeat(source_role, row_lengths)
    if token_roles.shape != family.token_mask.shape:
        raise AssertionError("Token roles do not align with the family token mask")
    return token_roles == role_code


def _summarize_field(
    field: typed.FieldSpec,
    family: typed.RaggedFamilyBatch,
    source_role: np.ndarray,
) -> dict[str, object]:
    """Summarize one field separately for the fixed data and MC rows."""

    role_summaries: dict[str, object] = {}
    for role_code, role_name in ROLE_NAMES.items():
        selected_tokens = _role_token_mask(family, source_role, role_code)
        values = np.asarray(family.values[field.name][selected_tokens])
        masks = np.asarray(family.masks[field.name][selected_tokens], dtype=np.bool_)
        token_mask = np.asarray(family.token_mask[selected_tokens], dtype=np.bool_)
        validity = masks & token_mask[:, None]
        role_summary: dict[str, object] = {
            "stored_token_count": int(values.shape[0]),
            "present_token_count": int(token_mask.sum()),
            "values_and_masks_sha256": _sha256_bytes(values, masks, token_mask),
            "components": _component_summary(values, validity),
        }
        if field.kind == "categorical":
            role_summary["valid_code_support"] = _categorical_support(
                values, validity
            )
        role_summaries[role_name] = role_summary
    return {
        "contract": field.as_dict(),
        "fixed_sample_observations": role_summaries,
    }


def _summarize_family(
    contract: typed.FamilyContract,
    family: typed.RaggedFamilyBatch,
    source_role: np.ndarray,
) -> dict[str, object]:
    """Summarize counts and fields for one typed-object family."""

    count_summary: dict[str, object] = {}
    for role_code, role_name in ROLE_NAMES.items():
        selected_rows = source_role == role_code
        counts = np.asarray(family.counts[selected_rows], dtype=np.int64)
        count_summary[role_name] = {
            "row_count": int(counts.size),
            "rows_with_objects": int(np.count_nonzero(counts)),
            "object_count": int(counts.sum()),
            "minimum_per_row": int(counts.min()),
            "maximum_per_row": int(counts.max()),
            "counts_sha256": _sha256_bytes(counts),
        }
    return {
        "counts": count_summary,
        "fields": {
            field.name: _summarize_field(field, family, source_role)
            for field in contract.fields
        },
    }


def _count_prongs_by_role(
    family: typed.RaggedFamilyBatch,
    source_role: np.ndarray,
    predicate: np.ndarray,
) -> dict[str, int]:
    """Count selected present prong tokens separately for data and MC."""

    if predicate.shape != family.token_mask.shape:
        raise ValueError("Prong diagnostic predicate has the wrong shape")
    return {
        role_name: int(
            np.count_nonzero(
                _role_token_mask(family, source_role, role_code)
                & family.token_mask
                & predicate
            )
        )
        for role_code, role_name in ROLE_NAMES.items()
    }


def _build_contract_diagnostics(
    batch: source_smoke.SourceContractBatch,
) -> dict[str, object]:
    """Record narrow fixed-sample diagnostics at unsettled contract seams."""

    source_role = np.asarray(batch.source_role, dtype=np.uint8)
    prongs = batch.descriptors.families["prongs"]
    charge = np.asarray(prongs.values["charge"][:, 0], dtype=np.int64)
    charge_is_valid = np.asarray(prongs.masks["charge"][:, 0], dtype=np.bool_)
    raw_pid = np.asarray(prongs.values["raw_pid"][:, 0], dtype=np.int64)
    raw_pid_is_valid = np.asarray(prongs.masks["raw_pid"][:, 0], dtype=np.bool_)
    energy = np.asarray(prongs.values["four_momentum"][:, 3], dtype=np.float64)
    energy_is_valid = np.asarray(
        prongs.masks["four_momentum"][:, 3], dtype=np.bool_
    )
    mass = np.asarray(prongs.values["mass"][:, 0], dtype=np.float64)
    mass_is_valid = np.asarray(prongs.masks["mass"][:, 0], dtype=np.bool_)
    score = np.asarray(prongs.values["score"][:, 0], dtype=np.float64)
    score_is_valid = np.asarray(prongs.masks["score"][:, 0], dtype=np.bool_)

    charge_field = next(
        field
        for field in typed.CONTRACT_BY_NAME["prongs"].fields
        if field.name == "charge"
    )
    declared_charge_codes = set(charge_field.categories)
    charge_support = Counter(
        int(code)
        for code in charge[charge_is_valid & prongs.token_mask]
    )
    charge_codes_outside_contract = {
        str(code): count
        for code, count in sorted(charge_support.items())
        if code not in declared_charge_codes
    }

    valid_charge_and_pid = charge_is_valid & raw_pid_is_valid & prongs.token_mask
    charge_pid_pairs = Counter(
        (int(charge_code), int(pid_code))
        for charge_code, pid_code in zip(
            charge[valid_charge_and_pid],
            raw_pid[valid_charge_and_pid],
            strict=True,
        )
    )

    photons = batch.descriptors.families["photons"]
    photon_direction = np.asarray(
        photons.values["direction"], dtype=np.float64
    )
    photon_direction_is_valid = (
        np.asarray(photons.masks["direction"], dtype=np.bool_).all(axis=1)
        & photons.token_mask
    )
    photon_direction_norm = np.linalg.norm(photon_direction, axis=1)
    valid_direction_norm = photon_direction_norm[photon_direction_is_valid]
    if not valid_direction_norm.size:
        raise ValueError("The fixed source smoke contains no valid photon direction")

    return {
        "classification": "FIXED_SAMPLE_DIAGNOSTICS_NOT_SEMANTIC_DECISIONS",
        "prong_charge": {
            "declared_categories": sorted(declared_charge_codes),
            "observed_valid_code_counts": {
                str(code): count for code, count in sorted(charge_support.items())
            },
            "observed_codes_outside_declared_categories": (
                charge_codes_outside_contract
            ),
            "valid_charge_raw_pid_pair_counts": {
                f"charge={charge_code},raw_pid={pid_code}": count
                for (charge_code, pid_code), count in sorted(
                    charge_pid_pairs.items()
                )
            },
        },
        "prong_structure": {
            "present_tokens_with_invalid_raw_pid": _count_prongs_by_role(
                prongs, source_role, ~raw_pid_is_valid
            ),
            "present_tokens_with_valid_raw_pid_zero": _count_prongs_by_role(
                prongs, source_role, raw_pid_is_valid & (raw_pid == 0)
            ),
            "present_tokens_with_valid_energy_at_most_1e_6": (
                _count_prongs_by_role(
                    prongs, source_role, energy_is_valid & (energy <= 1.0e-6)
                )
            ),
            "present_tokens_with_valid_mass_minus_one": _count_prongs_by_role(
                prongs, source_role, mass_is_valid & (mass == -1.0)
            ),
            "present_tokens_with_valid_score_minus_one": _count_prongs_by_role(
                prongs, source_role, score_is_valid & (score == -1.0)
            ),
        },
        "photon_direction": {
            "valid_vector_count": int(valid_direction_norm.size),
            "minimum_norm": float(valid_direction_norm.min()),
            "maximum_norm": float(valid_direction_norm.max()),
            "maximum_absolute_deviation_from_one": float(
                np.max(np.abs(valid_direction_norm - 1.0))
            ),
        },
    }


def build_probe_record(shard_path: Path) -> dict[str, object]:
    """Build the fixed-sample semantic telemetry record.

    Parameters
    ----------
    shard_path : pathlib.Path
        Existing fixed source-smoke shard.

    Returns
    -------
    dict[str, object]
        JSON-compatible telemetry with explicit non-claims.

    Raises
    ------
    ValueError
        If the shard is not the fixed two-source, 32-row smoke artifact.
    """

    batch, provenance = source_smoke.load_source_contract_shard(shard_path)
    source_role = np.asarray(batch.source_role, dtype=np.uint8)
    role_counts = {
        role_name: int(np.count_nonzero(source_role == role_code))
        for role_code, role_name in ROLE_NAMES.items()
    }
    expected_role_counts = {"data": 16, "mc": 16}
    if role_counts != expected_role_counts or batch.row_count != 32:
        raise ValueError(
            "The semantic probe requires exactly 16 fixed data rows and "
            "16 fixed MC rows"
        )
    if len(provenance.source_files) != 2:
        raise ValueError("The semantic probe requires exactly two bound sources")

    return {
        "schema": PROBE_SCHEMA,
        "classification": "FIXED_SAMPLE_TELEMETRY_NOT_AN_ESTIMATE",
        "result": "PASS",
        "scope": {
            "established": (
                "Field-level mask support, categorical codes, and raw-scale "
                "telemetry for the already-bound entries 0--15 in each source."
            ),
            "not_established": [
                "physical units or calibration",
                "population support or category completeness",
                "production normalization",
                "production-scale multiplicity or segment-sum behavior",
                "scientific performance or coverage",
            ],
        },
        "source_smoke": {
            "schema": source_smoke.SOURCE_SMOKE_SCHEMA_VERSION,
            "starting_commit": source_smoke.STARTING_COMMIT,
            "committed_receipt": (
                "docs/orchestration/state/"
                "pet-typed-descriptor-fixed-source-smoke-20260901.json"
            ),
            "row_count": batch.row_count,
            "rows_by_role": role_counts,
            "tree": source_smoke.TREE_NAME,
            "entries": {
                "first": source_smoke.FIXED_ENTRIES[0],
                "last": source_smoke.FIXED_ENTRIES[-1],
                "inclusive": True,
            },
            "combined_manifest_sha256": provenance.manifest_sha256,
            "bound_manifests": [
                {
                    "role": source.role,
                    "path": source.manifest_relative_path,
                    "sha256": source.expected_manifest_sha256,
                }
                for source in source_smoke.FIXED_SOURCES
            ],
            "sources": [
                {
                    "ordinal": source_file.ordinal,
                    "basename": Path(source_file.path).name,
                    "uuid": source_file.uuid,
                }
                for source_file in provenance.source_files
            ],
            "shard_sha256": hashlib.sha256(shard_path.read_bytes()).hexdigest(),
        },
        "descriptor_schema_sha256": typed.descriptor_schema_digest(),
        "probe_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "contract_diagnostics": _build_contract_diagnostics(batch),
        "families": {
            contract.name: _summarize_family(
                contract,
                batch.descriptors.families[contract.name],
                source_role,
            )
            for contract in typed.FAMILY_CONTRACTS
        },
    }


def write_probe_record(path: Path, record: Mapping[str, object]) -> None:
    """Write one deterministic JSON probe record.

    Parameters
    ----------
    path : pathlib.Path
        Destination path ending in ``.json``.
    record : mapping
        JSON-compatible probe record.

    Raises
    ------
    ValueError
        If the output path does not end in ``.json``.
    """

    if path.suffix != ".json":
        raise ValueError("Probe output path must end in .json")
    path.write_text(
        json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    """Run the fixed-sample semantic telemetry probe."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shard", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    write_probe_record(arguments.output, build_probe_record(arguments.shard))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
