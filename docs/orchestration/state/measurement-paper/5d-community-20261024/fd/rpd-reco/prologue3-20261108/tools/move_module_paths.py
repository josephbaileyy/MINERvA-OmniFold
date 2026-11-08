#!/usr/bin/env python3
"""Move module_paths out of the redacted prepare view into a sibling TSV (the director's choice (a)).

The receipt-artifact hook reads the module name nersc_pymon.log, a key of module_paths, as a bare .log citation.
This moves module_paths, unchanged, into module-paths.tsv (one "name<TAB>path" row per module, sorted by name) and
leaves a pointer in the view. It then rebuilds the original view from the two outputs and requires its bytes to
equal the input's, so the move is shown to lose nothing.

usage: move_module_paths.py VIEW_IN VIEW_OUT TSV_OUT
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def serialise(view: dict) -> bytes:
    """The byte form redact_prepare.py writes."""
    return (json.dumps(view, indent=2, sort_keys=True) + "\n").encode()


def main() -> int:
    view_in, view_out, tsv_out = (Path(p) for p in sys.argv[1:4])
    original = view_in.read_bytes()
    view = json.loads(original)
    if serialise(view) != original:
        raise SystemExit("MOVE: the input is not in redact_prepare.py's byte form")
    modules = view["module_paths"]
    for name, path in modules.items():
        if any(c in s for s in (name, path) for c in "\t\n\r"):
            raise SystemExit(f"MOVE: a tab or newline in module row {name!r}")
    tsv = "".join(f"{name}\t{modules[name]}\n" for name in sorted(modules)).encode()
    tsv_out.write_bytes(tsv)
    view["module_paths"] = {
        "moved_to": tsv_out.name,
        "rows": len(modules),
        "tsv_sha256": hashlib.sha256(tsv).hexdigest(),
        "format": "name<TAB>path, one row per module, sorted by name",
    }
    view_out.write_bytes(serialise(view))

    rebuilt = json.loads(view_out.read_bytes())
    rows = [line.split("\t") for line in tsv_out.read_text().splitlines()]
    rebuilt["module_paths"] = {name: path for name, path in rows}
    same = serialise(rebuilt) == original
    print(f"MOVE: view before the move sha256 {hashlib.sha256(original).hexdigest()}")
    print(f"MOVE: committed view sha256 {hashlib.sha256(view_out.read_bytes()).hexdigest()}")
    print(f"MOVE: module-paths.tsv sha256 {hashlib.sha256(tsv).hexdigest()} rows {len(modules)}")
    print(f"MOVE: rebuilt from the committed view and the TSV equals the input byte for byte: {same}")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
