#!/usr/bin/env python3
"""Write the pilot's digest-bound manifest from explicitly named source files.

A separate entry point rather than a subcommand of `z_pilot.py`, because the launcher must be
able to build and inspect the manifest WITHOUT running a build -- and because a single command
that both declared its inputs and consumed them would let one invocation choose its own evidence.

Every digest is measured here from the file on disk. `--throw-sha256` is the one digest a caller
may ASSERT, and it is checked against the measurement rather than recorded in place of it: that
is the authorized precursor product's identity, and the pilot must refuse a different file.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import z_contract as contract
import z_pilot as pilot


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--provenance", type=Path, default=None)
    parser.add_argument("--producing-revision", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-step", required=True)
    parser.add_argument("--input-kind", default="real", choices=("real", "synthetic"))
    for role in pilot.SOURCE_ROLES:
        parser.add_argument(f"--{role}", required=True, type=Path)
    parser.add_argument("--parent-format", default="opaque",
                        choices=("npz", "root", "opaque"))
    parser.add_argument("--throw-sha256", default=None,
                        help="the authorized precursor product digest; checked, not trusted")
    parser.add_argument("--stat-key", required=True)
    parser.add_argument("--ml-key", required=True)
    parser.add_argument("--allow-overwrite", action="store_true")
    args = parser.parse_args(argv)

    def fmt(path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".npz":
            return "npz"
        if suffix == ".root":
            return "root"
        return "opaque"

    sources = {}
    for role in pilot.SOURCE_ROLES:
        path = getattr(args, role)
        spec: dict = {"path": str(path), "format": args.parent_format if role == "parent"
                      else fmt(path)}
        if role == "throw" and args.throw_sha256:
            spec["expect_sha256"] = args.throw_sha256
        sources[role] = spec

    try:
        result = pilot.build_manifest(
            args.out,
            sources=sources,
            run={"id": args.run_id, "step": args.run_step},
            producing_revision=args.producing_revision,
            stat_key=args.stat_key,
            ml_key=args.ml_key,
            input_kind=args.input_kind,
            allow_overwrite=args.allow_overwrite,
            provenance_path=args.provenance,
        )
    except contract.ZContractError as exc:
        print(json.dumps({"manifest_status": "FAILED", "reason": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps({"manifest_status": "BOUND", "manifest": result["manifest"],
                      "manifest_sha256": result["manifest_stamp"]["sha256"],
                      "footing": result["footing"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
