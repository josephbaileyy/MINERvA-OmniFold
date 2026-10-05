"""Copy a closed audit directory and verify every file without importing ROOT."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def digest(path: Path) -> str:
    """Return SHA-256 of the complete closed file."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inventory(root: Path) -> dict[str, dict[str, Any]]:
    """Hash all regular files; reject symlinks and special files."""
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlink refused: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"Nonregular file refused: {path}")
        files[path.relative_to(root).as_posix()] = {
            "bytes": path.stat().st_size,
            "sha256": digest(path),
        }
    return files


def write_json(path: Path, value: Any) -> None:
    """Create an evidence JSON file without overwriting an existing file."""
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def main() -> None:
    """Verify source bindings, copy once, and compare source and destination."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--receipt-sha256", required=True)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    destination = args.destination.resolve()
    if destination == source or source in destination.parents:
        raise ValueError("Destination must be outside the source tree")
    if destination.exists():
        raise FileExistsError(destination)
    receipt_path = source / "audit/receipt.json"
    if digest(receipt_path) != args.receipt_sha256:
        raise ValueError("Source receipt differs from the committed receipt")
    receipt = json.loads(receipt_path.read_bytes())
    accounting = json.loads((source / "audit/accounting.json").read_bytes())
    if accounting["receipt_sha256"] != args.receipt_sha256:
        raise ValueError("Accounting does not bind the source receipt")
    before = inventory(source)
    for name, expected in receipt["artifacts"].items():
        if before.get("audit/" + name) != expected:
            raise ValueError(f"Receipt-bound artifact mismatch: {name}")
    for name, expected in accounting["closed_auxiliary_artifacts"].items():
        if before.get("audit/" + name) != expected:
            raise ValueError(f"Accounting-bound artifact mismatch: {name}")
    destination.mkdir(parents=True)
    write_json(
        destination / "STARTED.json",
        {
            "source": str(source),
            "destination": str(destination),
            "started_utc": datetime.now(timezone.utc).isoformat(),
            "complete_only_if": "COMPLETE.json exists and its manifest hash verifies",
        },
    )
    shutil.copytree(source, destination / "payload")
    copied = inventory(destination / "payload")
    after = inventory(source)
    if before != after or before != copied:
        raise ValueError("Source changed or destination does not exactly match")
    write_json(destination / "manifest.json", before)
    summary = {
        "kind": "CFS_AUDIT_PRESERVATION_ONLY",
        "source": str(source),
        "destination": str(destination / "payload"),
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "receipt_sha256": args.receipt_sha256,
        "manifest_sha256": digest(destination / "manifest.json"),
        "preserver_sha256": digest(Path(__file__)),
        "copied_files": len(before),
        "copied_bytes": sum(record["bytes"] for record in before.values()),
        "receipt_artifacts_verified": len(receipt["artifacts"]),
        "accounting_auxiliary_files_verified": len(
            accounting["closed_auxiliary_artifacts"]
        ),
        "source_before_after_equal": True,
        "destination_readback_equal": True,
        "root_source_opens": 0,
        "scratch_original_retained": True,
    }
    write_json(destination / "COMPLETE.json", summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
