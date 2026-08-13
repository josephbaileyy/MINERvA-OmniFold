#!/usr/bin/env python3
"""Resolve a moved diagnostic target without mutating an artifact or canonical path."""

from __future__ import annotations

import hashlib
import os


def _sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_precomputed_target(
    recorded_path: str | None,
    override_path: str | None,
    expected_sha256: str | None,
) -> tuple[str | None, dict]:
    """Return the effective path and a fail-closed provenance record.

    Historical PET artifacts embed an absolute path to the Gate-2 target.  If
    the target was subsequently archived, diagnostics must not recreate or
    repoint that canonical path.  An override is accepted only with an exact
    SHA-256 supplied by the caller.
    """
    if not override_path:
        if expected_sha256:
            raise SystemExit(
                "--precomputed-target-sha256 requires "
                "--precomputed-target-override"
            )
        return recorded_path, {
            "override_used": False,
            "recorded_path": recorded_path,
            "effective_path": recorded_path,
            "sha256": None,
        }

    if not expected_sha256:
        raise SystemExit(
            "--precomputed-target-override requires "
            "--precomputed-target-sha256 (fail closed)"
        )
    effective = os.path.abspath(override_path)
    if not os.path.isfile(effective):
        raise SystemExit(f"precomputed-target override is not a file: {effective}")
    actual = _sha256(effective)
    if actual != expected_sha256:
        raise SystemExit(
            f"precomputed-target override sha256 mismatch: {actual} != "
            f"{expected_sha256}"
        )
    return effective, {
        "override_used": True,
        "recorded_path": recorded_path,
        "effective_path": effective,
        "sha256": actual,
    }
