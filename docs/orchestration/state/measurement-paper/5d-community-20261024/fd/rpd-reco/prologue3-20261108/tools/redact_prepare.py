#!/usr/bin/env python3
"""Write a redacted view of an RPD-RECO prologue prepare record.

The raw record (prologue-prepare.json) carries environment_snapshot.fingerprints: an unsalted SHA-256 of every
environment value, credential fields included. That map must not reach the repository. The view keeps every other
field unchanged. For each fingerprinted key it keeps only the key name, its presence on the prepare side and on the
worker side, and the comparison: equal, changed, added, removed, excluded or not_compared. The worker side is read
from the worker's STOP record (details.environment.diff and .excluded), when one exists.

usage: redact_prepare.py RAW_PREPARE STOP_JSON_OR_NONE VIEW_OUT
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path


def comparison_table(raw: dict, stop: dict | None) -> dict:
    """Map every fingerprinted key to its presence on each side and its comparison."""
    prepared_keys = set(raw["environment_snapshot"]["fingerprints"])
    if stop is None:
        return {
            key: {"prepare": True, "worker": None, "comparison": "not_compared"}
            for key in sorted(prepared_keys)
        }
    environment = stop["details"]["environment"]
    diff = environment["diff"]
    excluded = set(environment["excluded"])
    added, removed, changed = set(diff["added"]), set(diff["removed"]), set(diff["changed"])
    if not (removed <= prepared_keys and changed <= prepared_keys and not added & prepared_keys):
        raise SystemExit("REDACT: the STOP diff is inconsistent with the prepare record's keys")
    table = {}
    for key in sorted(prepared_keys | added):
        if key in excluded:
            row = {"prepare": key in prepared_keys, "worker": None, "comparison": "excluded"}
        elif key in added:
            row = {"prepare": False, "worker": True, "comparison": "added"}
        elif key in removed:
            row = {"prepare": True, "worker": False, "comparison": "removed"}
        elif key in changed:
            row = {"prepare": True, "worker": True, "comparison": "changed"}
        else:
            row = {"prepare": True, "worker": True, "comparison": "equal"}
        table[key] = row
    return table


def main() -> int:
    raw_path, stop_arg, view_path = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    raw_bytes = raw_path.read_bytes()
    raw = json.loads(raw_bytes)
    stop = None if stop_arg == "NONE" else json.loads(Path(stop_arg).read_text())
    view = copy.deepcopy(raw)
    snapshot = view["environment_snapshot"]
    del snapshot["fingerprints"]
    snapshot["fingerprint_comparison"] = comparison_table(raw, stop)
    view["redaction"] = {
        "source": "prologue-prepare.json",
        "source_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "removed": "environment_snapshot.fingerprints",
        "kept_per_key": "name, presence on the prepare and worker sides, comparison",
        "worker_side_from": None if stop is None else "prologue-worker.STOP.json details.environment",
    }
    view_path.write_text(json.dumps(view, indent=2, sort_keys=True) + "\n")
    print(f"REDACT: source sha256 {view['redaction']['source_sha256']}")
    print(f"REDACT: view sha256 {hashlib.sha256(view_path.read_bytes()).hexdigest()}")
    counts: dict[str, int] = {}
    for row in snapshot["fingerprint_comparison"].values():
        counts[row["comparison"]] = counts.get(row["comparison"], 0) + 1
    print(f"REDACT: keys by comparison {json.dumps(counts, sort_keys=True)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
