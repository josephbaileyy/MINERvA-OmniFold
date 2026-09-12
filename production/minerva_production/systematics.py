"""Matched scalar universe families; diagnostic construction without adoption."""

from __future__ import annotations

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from .root_input import ADAPTER_SOURCES, prepare
from .storage import (
    ROOT,
    check_output,
    code_identity,
    digest,
    fingerprint,
    legacy_module,
    load_result,
    save_result,
)
from .universe_input import LATERAL_BANDS, resolve_universe


def inventory(raw: dict[str, Any]) -> dict[str, Any]:
    """Validate a complete declared single-band inventory, never an inferred glob."""
    required = {"band", "expected_indices", "members"}
    if required - raw.keys() or set(raw) - (required | {"flux_universe_file"}):
        raise ValueError(
            "systematic inventory requires band, expected_indices and members; only Flux accepts flux_universe_file"
        )
    resolve_universe({"band": raw["band"], "index": 0})
    expected = raw["expected_indices"]
    if (
        not isinstance(expected, list)
        or len(expected) < 2
        or any(type(index) is not int or index < 0 for index in expected)
        or len(set(expected)) != len(expected)
    ):
        raise ValueError(
            "expected_indices must declare at least two distinct nonnegative universe indices"
        )
    if raw["band"] in LATERAL_BANDS and set(expected) != {0, 1}:
        raise ValueError("native lateral bands require both endpoints 0 and 1")
    members = raw["members"]
    if not isinstance(members, list) or any(
        not isinstance(member, dict) or set(member) != {"index", "input"}
        for member in members
    ):
        raise ValueError("each systematic member requires index and input ROOT path")
    for member in members:
        resolve_universe({"band": raw["band"], "index": member["index"]})
        if not isinstance(member["input"], str) or not member["input"]:
            raise ValueError(
                "member input must name an existing ROOT source, not a weight ratio"
            )
    if len(members) != len(expected) or {member["index"] for member in members} != set(
        expected
    ):
        raise ValueError(
            "systematic member inventory is missing, duplicated or unexpected"
        )
    if (raw["band"] == "Flux") != ("flux_universe_file" in raw):
        raise ValueError(
            "Flux inventory requires its per-universe flux table; other bands must omit it"
        )
    if "flux_universe_file" in raw and (
        not isinstance(raw["flux_universe_file"], str) or not raw["flux_universe_file"]
    ):
        raise ValueError(
            "flux_universe_file must name the native per-universe flux table"
        )
    return {
        **raw,
        "expected_indices": sorted(expected),
        "members": sorted(members, key=lambda member: member["index"]),
    }


def calculation_identity(cfg: dict[str, Any]) -> dict[str, Any]:
    """Bind the selected estimator, adapter and retained covariance implementation."""
    return {
        "scalar": code_identity(backend=cfg["backend"]),
        "sources": {
            path: digest(ROOT / path)
            for path in (
                *ADAPTER_SOURCES,
                "production/minerva_production/systematics.py",
                "nd-unfolding/uq_math.py",
            )
        },
    }


def validate_pairing(
    inputs: dict[str, Any], metadata: dict[str, Any], nominal: dict[str, Any]
) -> None:
    """Require matching data, calibration, definitions and producer dependencies."""
    reference = nominal["input_contract"]
    for key in (
        "selection",
        "background",
        "feature_names",
        "feature_units",
        "normalization_units",
        "denominator_policy",
        "flux_axis",
        "adapter_sources",
        "measured_inventory_sha256",
    ):
        if key not in reference or reference[key] != metadata.get(key):
            raise ValueError(f"systematic/nominal input mismatch: {key}")
    if (
        reference["normalization_source"]["flux_sha256"]
        != metadata["normalization_source"]["flux_sha256"]
    ):
        raise ValueError("systematic baseline flux differs from the nominal")
    if (
        reference["normalization_source"]["mc_pot"]
        != metadata["normalization_source"]["mc_pot"]
    ):
        raise ValueError("systematic MC exposure differs from the nominal")
    for key in ("data_pot", "n_nucleons"):
        if float(inputs[key]) != reference["normalization_values"][key]:
            raise ValueError(
                f"systematic normalization differs from the nominal: {key}"
            )
    for key in ("axes", "ordering", "meaning", "value_unit", "projection_domain"):
        if metadata["output_contract"].get(key) != nominal["output_contract"].get(key):
            raise ValueError(f"systematic output contract differs from nominal: {key}")


def assemble(nominal: dict[str, Any], members: list[dict[str, Any]]) -> dict[str, Any]:
    """Reuse MAT 1/N covariance and retain the CV-centered second moment and shift."""
    import numpy as np

    spectra = np.stack([member["xsec"] for member in members])
    if spectra.shape[1:] != nominal["xsec"].shape:
        raise ValueError("systematic spectra do not match nominal support")
    covariance, shift = legacy_module("uq_math").joint_throw_covariance(
        spectra, nominal["xsec"]
    )
    delta = spectra - nominal["xsec"]
    return {
        "xsec": nominal["xsec"],
        "covariance": covariance,
        "covariance_cv_centered": delta.T @ delta / len(members),
        "mean": spectra.mean(axis=0),
        "mean_shift": shift,
    }


def execute(
    args: argparse.Namespace, cfg: dict[str, Any], family: dict[str, Any]
) -> None:
    """Run or assemble a single declared systematic family against its nominal."""
    from .scalar import calculate, load_inputs

    nominal_arrays, nominal = load_result(args.nominal)
    identity = nominal["identity"]
    code = calculation_identity(cfg)
    if (
        identity.get("operation") != "unfold_gbdt"
        or identity.get("config") != cfg
        or identity.get("code") != code["scalar"]
    ):
        raise ValueError(
            "systematics require a matching nominal estimator, settings and calculation dependencies"
        )
    reference = nominal.get("input_contract", {})
    if (
        reference.get("variation", {}).get("mode") != "nominal"
        or reference.get("selection") != "nd-standard-v1"
    ):
        raise ValueError(
            "systematics require a nominal scalar-root input, not an unidentified cache or shifted source"
        )
    if cfg["features"] != reference["feature_names"]:
        raise ValueError(
            "systematic feature selection must match the prepared native scalar axes"
        )
    base = {
        "config": cfg,
        "code": code,
        "nominal": fingerprint(nominal),
        "inventory": fingerprint(family),
    }
    if args.action == "run":
        for member in family["members"]:
            index = member["index"]
            variation = {"band": family["band"], "index": index}
            source = (args.input / member["input"]).resolve()
            prepare_config = {
                **reference["preparation_config"],
                "universe": variation,
            }
            if "flux_universe_file" in family:
                prepare_config["flux_universe_file"] = str(
                    (args.input / family["flux_universe_file"]).resolve()
                )
            sources = {"events": source, "flux": Path(prepare_config["flux_file"])}
            if "flux_universe_file" in prepare_config:
                sources["flux_universes"] = Path(prepare_config["flux_universe_file"])
            input_hashes = {name: digest(path) for name, path in sources.items()}
            member_identity = {
                **base,
                "operation": "systematic-member",
                "variation": variation,
                "sources": input_hashes,
            }
            output = args.output / f"member_{index}"
            if check_output(output, member_identity, args.resume):
                continue
            args.output.mkdir(parents=True, exist_ok=True)
            with TemporaryDirectory(prefix="prepared-", dir=args.output) as temporary:
                cache = Path(temporary) / "events.npz"
                prepare(prepare_config, source, cache)
                inputs, metadata = load_inputs(cache, cfg)
                for name, path in sources.items():
                    if metadata["source_digests"].get(str(path)) != input_hashes[name]:
                        raise ValueError("systematic source changed during preparation")
                validate_pairing(inputs, metadata, nominal)
                source_support = metadata["output_contract"]["support"]
                metadata = {**metadata, "output_contract": nominal["output_contract"]}
                arrays = calculate(inputs, metadata, cfg)
                save_result(
                    output,
                    arrays,
                    {
                        "identity": member_identity,
                        "output_contract": nominal["output_contract"],
                        "source_support": source_support,
                        "input_contract": metadata,
                    },
                )
        return
    members, bindings = [], {}
    for member in family["members"]:
        index = member["index"]
        arrays, record = load_result(args.input / f"member_{index}")
        expected = {
            **base,
            "operation": "systematic-member",
            "variation": {"band": family["band"], "index": index},
        }
        actual = record["identity"]
        if {
            key: value for key, value in actual.items() if key != "sources"
        } != expected or record["output_contract"] != nominal["output_contract"]:
            raise ValueError(
                f"systematic member {index}: nominal, inventory, code or support mismatch"
            )
        source_keys = {"events", "flux"} | (
            {"flux_universes"} if family["band"] == "Flux" else set()
        )
        if (
            not isinstance(actual.get("sources"), dict)
            or set(actual["sources"]) != source_keys
        ):
            raise ValueError(f"systematic member {index} lacks source bindings")
        members.append(arrays)
        bindings[str(index)] = fingerprint(record)
    combined_identity = {**base, "operation": "systematic-combine", "members": bindings}
    if check_output(args.output, combined_identity, args.resume):
        return
    save_result(
        args.output,
        assemble(nominal_arrays, members),
        {
            "identity": combined_identity,
            "output_contract": nominal["output_contract"],
            "covariance_contract": {
                "source": "systematic",
                "band": family["band"],
                "indices": family["expected_indices"],
                "centering": "universe-mean",
                "divisor": "N",
                "mean_shift": "reported separately",
                "cv_centered_variant": "covariance_cv_centered",
                "combination": "single declared band only",
                "adoption": "quarantined diagnostic; neither centering is an adopted scalar covariance",
            },
        },
    )
