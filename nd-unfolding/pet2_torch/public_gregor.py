"""Optional diagnostic seam for Gregor's immutable public MC-only revision."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import argparse
import json

import numpy as np

from .artifacts import write_json
from .utils import file_sha256

PUBLIC_REVISION = "32e2f5040ff2678a2ef7ca1bc0b450b324f4fd83"
PUBLIC_DATASET = "gregorkrzmanc/minerva-ml"
PUBLIC_LICENSE = "CC-BY-4.0"
REQUIRED_MAPPING_KEYS = {"data", "truth_labels", "global_features"}


def inspect_local_public_artifact(path: str | Path) -> dict[str, Any]:
    """Hash a user-staged artifact without downloading or deserializing it."""
    artifact = Path(path).expanduser().resolve()
    if not artifact.is_file():
        raise FileNotFoundError(
            f"public Gregor artifact is not staged: {artifact}; this adapter never downloads it"
        )
    return {
        "status": "diagnostic_mc_only",
        "dataset": PUBLIC_DATASET,
        "revision": PUBLIC_REVISION,
        "license": PUBLIC_LICENSE,
        "path": str(artifact),
        "bytes": artifact.stat().st_size,
        "sha256": file_sha256(artifact),
        "publication_omnifold_eligible": False,
        "missing_contract_legs": [
            "real data inventory",
            "physics event weights",
            "pass_reco/pass_truth",
            "native miss/fake flags",
            "stable event identities",
            "literal aligned backgrounds",
        ],
    }


def adapt_loaded_public_mapping(mapping: Mapping[str, Any]) -> dict[str, Any]:
    """Validate an explicitly loaded mapping; never uses unsafe pickle internally."""
    missing = sorted(REQUIRED_MAPPING_KEYS - set(mapping))
    if missing:
        raise ValueError(f"public mapping lacks required diagnostic keys: {missing}")
    arrays = {
        key: np.asarray(
            mapping[key].detach().cpu().numpy()
            if hasattr(mapping[key], "detach")
            else mapping[key]
        )
        for key in REQUIRED_MAPPING_KEYS
    }
    rows = [arrays[key].shape[0] for key in sorted(REQUIRED_MAPPING_KEYS)]
    if len(set(rows)) != 1:
        raise ValueError("public Gregor arrays have different row counts")
    data = arrays["data"]
    truth = arrays["truth_labels"]
    globals_ = arrays["global_features"]
    if data.ndim != 3 or data.shape[2] < 5:
        raise ValueError("public Gregor data must have shape (N,P,F>=5)")
    if truth.ndim < 2 or globals_.ndim != 2:
        raise ValueError("public truth/global diagnostic arrays have malformed rank")
    if not all(np.all(np.isfinite(value)) for value in arrays.values()):
        raise ValueError("public Gregor diagnostic arrays contain NaN or infinity")
    all_zero = np.all(data == 0, axis=2)
    raw_type = data[:, :, 4].astype(np.int64)
    raw_types, raw_counts = np.unique(raw_type, return_counts=True)
    # This is a census of the public preparation's historical feature-2
    # nonzero convention, not the explicit-mask convention used by PET2.
    feature2_nonzero = data[:, :, 2] != 0
    return {
        "status": "diagnostic_mc_only",
        "revision": PUBLIC_REVISION,
        "row_count": rows[0],
        "schema": {
            "data": list(data.shape),
            "truth_labels": list(truth.shape),
            "global_features": list(globals_.shape),
        },
        "padding_type_census": {
            "all_feature_zero_slots": int(all_zero.sum()),
            "feature2_nonzero_candidate_slots": int(feature2_nonzero.sum()),
            "raw_type_counts": {
                str(int(key)): int(value)
                for key, value in zip(raw_types, raw_counts)
            },
            "raw_type_zero_but_feature2_nonzero": int(
                np.sum((raw_type == 0) & feature2_nonzero)
            ),
            "warning": (
                "raw census only: public preparation has no PET2 explicit token "
                "mask and category 0 may collide with a physical source category"
            ),
        },
        "publication_omnifold_eligible": False,
        "reason": "prepared MC rows lack the complete OmniFold inventory contract",
    }


def inspect_trusted_public_pb(
    path: str | Path,
    *,
    trusted: bool,
    expected_sha256: str,
) -> dict[str, Any]:
    """Inspect an explicitly trusted staged torch archive with safe tensor loading."""
    artifact = Path(path).expanduser().resolve()
    if not trusted:
        raise ValueError("public .pb inspection requires explicit trusted=True")
    if artifact.suffix != ".pb":
        raise ValueError("trusted public diagnostic must use the staged .pb artifact")
    metadata = inspect_local_public_artifact(artifact)
    if not expected_sha256 or metadata["sha256"] != expected_sha256:
        raise ValueError("public .pb SHA-256 is absent or differs from the caller's value")
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError(f"PyTorch is unavailable for trusted .pb inspection: {exc}") from exc
    try:
        mapping = torch.load(
            artifact,
            map_location="cpu",
            weights_only=True,
        )
    except Exception as exc:
        raise ValueError(
            "trusted .pb did not pass PyTorch weights-only deserialization; "
            "unsafe pickle fallback is forbidden"
        ) from exc
    if not isinstance(mapping, Mapping):
        raise ValueError("trusted public .pb payload is not a tensor mapping")
    census = adapt_loaded_public_mapping(mapping)
    return {
        **metadata,
        **census,
        "deserialization": "torch.load(weights_only=True)",
        "trusted_by_caller": True,
        "unfolding_use_permitted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--trusted", action="store_true")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = inspect_trusted_public_pb(
        args.path,
        trusted=args.trusted,
        expected_sha256=args.expected_sha256,
    )
    write_json(args.out, result)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
