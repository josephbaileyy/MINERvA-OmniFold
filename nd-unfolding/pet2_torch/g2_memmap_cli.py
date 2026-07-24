#!/usr/bin/env python3
"""CLI for receipt-bound production-G2 NPZ conversion and verification."""

from __future__ import annotations

import argparse
import json

from .g2_memmap import (
    DEFAULT_CHUNK_BYTES,
    convert_g2_npz_to_memmap,
    open_g2_memmap_inventory,
)


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    convert = subparsers.add_parser("convert")
    convert.add_argument("--source", required=True)
    convert.add_argument("--out", required=True)
    convert.add_argument("--expected-sha256", required=True)
    convert.add_argument("--expected-size-bytes", required=True, type=int)
    convert.add_argument("--timestamp-utc", required=True)
    convert.add_argument("--chunk-bytes", type=int, default=DEFAULT_CHUNK_BYTES)
    convert.add_argument("--no-resume", action="store_true")
    verify = subparsers.add_parser("verify")
    verify.add_argument("--source", required=True)
    verify.add_argument("--directory", required=True)
    verify.add_argument("--chunk-bytes", type=int, default=DEFAULT_CHUNK_BYTES)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "convert":
        manifest = convert_g2_npz_to_memmap(
            args.source,
            args.out,
            expected_sha256=args.expected_sha256,
            expected_size_bytes=args.expected_size_bytes,
            timestamp_utc=args.timestamp_utc,
            chunk_bytes=args.chunk_bytes,
            resume=not args.no_resume,
        )
    else:
        inventory = open_g2_memmap_inventory(
            args.directory,
            source_npz=args.source,
            chunk_bytes=args.chunk_bytes,
        )
        try:
            manifest = inventory.manifest
        finally:
            inventory.close()
    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
