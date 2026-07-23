"""Strict arm-F checkpoint eligibility.

Arm F has no random fallback.  Missing, inaccessible, unlicensed, or mismatched
weights return a tested ``unavailable`` outcome.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .utils import file_sha256

REQUIRED_MANIFEST_KEYS = {
    "checkpoint_sha256",
    "weight_license",
    "weight_redistribution_permitted",
    "architecture_fingerprint",
    "preprocessing_fingerprint",
    "tensor_shapes",
    "source_url",
    "source_commit",
}


def arm_f_eligibility(
    checkpoint_path: str | None,
    manifest_path: str | None,
    *,
    expected_architecture_fingerprint: str,
    expected_preprocessing_fingerprint: str,
    expected_tensor_shapes: Mapping[str, Any],
) -> dict[str, Any]:
    reasons: list[str] = []
    if not checkpoint_path:
        reasons.append("checkpoint file is inaccessible/not supplied")
    if not manifest_path:
        reasons.append("checkpoint manifest is absent")
    checkpoint = Path(checkpoint_path).resolve() if checkpoint_path else None
    manifest_file = Path(manifest_path).resolve() if manifest_path else None
    if checkpoint is not None and not checkpoint.is_file():
        reasons.append(f"checkpoint does not exist: {checkpoint}")
    if manifest_file is not None and not manifest_file.is_file():
        reasons.append(f"manifest does not exist: {manifest_file}")
    if reasons:
        return {"arm": "F", "status": "unavailable", "reasons": reasons, "fallback": None}
    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "arm": "F",
            "status": "unavailable",
            "reasons": [f"invalid manifest: {type(exc).__name__}: {exc}"],
            "fallback": None,
        }
    missing = sorted(REQUIRED_MANIFEST_KEYS - set(manifest))
    if missing:
        reasons.append(f"manifest missing keys: {missing}")
    if manifest.get("weight_license") in (None, "", "unknown", "unlicensed"):
        reasons.append("checkpoint weight license is absent or unknown")
    if manifest.get("weight_redistribution_permitted") is not True:
        reasons.append("checkpoint redistribution/use permission is not affirmative")
    if manifest.get("architecture_fingerprint") != expected_architecture_fingerprint:
        reasons.append("architecture fingerprint mismatch")
    if manifest.get("preprocessing_fingerprint") != expected_preprocessing_fingerprint:
        reasons.append("preprocessing fingerprint mismatch")
    if manifest.get("tensor_shapes") != dict(expected_tensor_shapes):
        reasons.append("checkpoint tensor-shape manifest mismatch")
    actual_sha = file_sha256(checkpoint)
    if manifest.get("checkpoint_sha256") != actual_sha:
        reasons.append("checkpoint SHA-256 mismatch")
    return {
        "arm": "F",
        "status": "eligible" if not reasons else "unavailable",
        "reasons": reasons,
        "fallback": None,
        "checkpoint_sha256": actual_sha,
        "manifest": manifest if not reasons else None,
    }


def current_arm_f_outcome() -> dict[str, Any]:
    """Campaign-locked outcome for the inaccessible, unlicensed Gregor weights."""
    return {
        "arm": "F",
        "status": "unavailable",
        "reasons": [
            "advertised checkpoint files are inaccessible",
            "no immutable checkpoint checksum is published",
            "checkpoint weight license is unknown",
            "strict architecture/preprocessing/tensor compatibility is unproven",
        ],
        "fallback": None,
    }
