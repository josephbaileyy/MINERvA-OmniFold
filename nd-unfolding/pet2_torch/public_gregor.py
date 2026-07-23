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

    def as_dense_numpy(value: Any, label: str) -> np.ndarray:
        if bool(getattr(value, "is_nested", False)):
            raise ValueError(f"public Gregor {label} unexpectedly uses nested storage")
        if hasattr(value, "detach"):
            value = value.detach().cpu().numpy()
        return np.asarray(value)

    truth = as_dense_numpy(mapping["truth_labels"], "truth_labels")
    globals_ = as_dense_numpy(mapping["global_features"], "global_features")
    if truth.ndim < 2 or globals_.ndim != 2:
        raise ValueError("public truth/global diagnostic arrays have malformed rank")
    if not np.all(np.isfinite(truth)) or not np.all(np.isfinite(globals_)):
        raise ValueError("public Gregor diagnostic arrays contain NaN or infinity")

    data_value = mapping["data"]
    if bool(getattr(data_value, "is_nested", False)):
        if not hasattr(data_value, "values") or not hasattr(data_value, "offsets"):
            raise ValueError("public Gregor nested data lacks values/offsets accessors")
        data = as_dense_numpy(data_value.values(), "data.values")
        offsets = as_dense_numpy(data_value.offsets(), "data.offsets").astype(
            np.int64, copy=False
        )
        if data.ndim != 2 or data.shape[1] < 5:
            raise ValueError("public Gregor jagged values must have shape (tokens,F>=5)")
        if offsets.ndim != 1 or offsets.size < 1 or offsets[0] != 0:
            raise ValueError("public Gregor jagged offsets are malformed")
        if np.any(np.diff(offsets) < 0) or offsets[-1] != data.shape[0]:
            raise ValueError("public Gregor jagged offsets do not delimit stored tokens")
        row_count = int(offsets.size - 1)
        token_counts = np.diff(offsets)
        data_schema: Any = {
            "layout": "nested_jagged",
            "values": list(data.shape),
            "offsets": list(offsets.shape),
            "event_token_counts": {
                "min": int(token_counts.min()) if token_counts.size else 0,
                "max": int(token_counts.max()) if token_counts.size else 0,
                "mean": float(token_counts.mean()) if token_counts.size else 0.0,
                "p50": float(np.quantile(token_counts, 0.50))
                if token_counts.size
                else 0.0,
                "p95": float(np.quantile(token_counts, 0.95))
                if token_counts.size
                else 0.0,
                "p99": float(np.quantile(token_counts, 0.99))
                if token_counts.size
                else 0.0,
            },
        }
        all_zero_slots = 0
        storage_note = (
            "nested jagged storage has no materialized padding slots; PET2 must "
            "construct an explicit mask when batching"
        )
    else:
        data = as_dense_numpy(data_value, "data")
        if data.ndim != 3 or data.shape[2] < 5:
            raise ValueError("public Gregor data must have shape (N,P,F>=5)")
        row_count = int(data.shape[0])
        data_schema = list(data.shape)
        all_zero_slots = int(np.all(data == 0, axis=2).sum())
        data = data.reshape(-1, data.shape[2])
        storage_note = (
            "dense diagnostic storage includes all-zero padding slots; this census "
            "does not infer the PET2 explicit mask from their values"
        )

    rows = [row_count, int(truth.shape[0]), int(globals_.shape[0])]
    if len(set(rows)) != 1:
        raise ValueError("public Gregor arrays have different row counts")
    if not np.all(np.isfinite(data)):
        raise ValueError("public Gregor diagnostic arrays contain NaN or infinity")
    raw_type = data[:, 4].astype(np.int64)
    raw_types, raw_counts = np.unique(raw_type, return_counts=True)
    # This is a census of the public preparation's historical feature-2
    # nonzero convention, not the explicit-mask convention used by PET2.
    feature2_nonzero = data[:, 2] != 0
    return {
        "status": "diagnostic_mc_only",
        "revision": PUBLIC_REVISION,
        "row_count": row_count,
        "schema": {
            "data": data_schema,
            "truth_labels": list(truth.shape),
            "global_features": list(globals_.shape),
        },
        "padding_type_census": {
            "stored_token_count": int(data.shape[0]),
            "all_feature_zero_slots": all_zero_slots,
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
            "storage_note": storage_note,
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
    # Gregor's prepared rows contain nested jagged tensors. PyTorch 2.8's
    # weights-only loader requires these built-in modules to be registered
    # before it can reconstruct the safe tensor containers. This does not
    # enable arbitrary pickle globals and does not relax weights_only=True.
    import torch.nested  # noqa: F401
    import torch._dynamo  # noqa: F401
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
