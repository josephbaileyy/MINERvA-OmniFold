#!/usr/bin/env python3
"""Atomically publish one F-17(b) JSON record without overwriting evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import sys


def preserve(source: Path, destination: Path) -> dict:
    """Validate and atomically publish source at destination, refusing clobber."""
    payload = source.read_bytes()
    json.loads(payload)
    digest = hashlib.sha256(payload).hexdigest()

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.parent / (
        f".{destination.name}.tmp-{os.getpid()}-{secrets.token_hex(4)}"
    )
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if hashlib.sha256(temporary.read_bytes()).hexdigest() != digest:
            raise OSError("temporary record digest differs from source")

        # link() is an atomic no-clobber publish when both paths share a
        # filesystem.  The temporary file is deliberately created beside the
        # destination, even when source came from a different filesystem.
        os.link(temporary, destination)
        directory_fd = os.open(destination.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)

    if hashlib.sha256(destination.read_bytes()).hexdigest() != digest:
        raise OSError("published record digest differs from source")
    return {"bytes": len(payload), "path": str(destination), "sha256": digest}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    try:
        receipt = preserve(args.source, args.destination)
    except (FileExistsError, FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        print(f"REFUSE: F-17(b) record was not published: {exc}", file=sys.stderr)
        return 13
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
