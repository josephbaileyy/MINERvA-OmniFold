#!/usr/bin/env python3
"""Write the public record of the one protected-path read (cov2d's condition, binding by the director, 2026-11-11).

From the owner-only prestage record RAW, for the listed exception (the MPARAMFILES constraint file), copy into OUT:
its original (as written and resolved), the sha256 prepare measured, the sha256 of both staged copies (recomputed here
from the copies under the run, never from the original), stat_before and stat_after (device, inode, bytes, mtime_ns,
atime_ns) and the UTC staging window (custody copy(): one stat-bracketed staging, with two O_NOATIME reads).
It also lists every staged original that overlaps a protected path of the config. Only the exception may.
Nothing from the environment sections of RAW is copied. Exits 0 on PASS, 1 on FAIL; OUT is written either way.

usage: protected_read.py RAW CONFIG OUT
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import sys
from pathlib import Path

EXCEPTION = (
    "/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/"
    "sorted_NuEConstraint_FHC_RHC_IMD.txt"
)
RELATIVE = "FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"
STAT_FIELDS = {"device", "inode", "bytes", "mtime_ns", "atime_ns"}


def forms(path: str) -> set[str]:
    return {os.path.normpath(path), os.path.realpath(path)}


def overlaps(a: str, b: str) -> bool:
    return any(
        x == y or x.startswith(y.rstrip("/") + "/") or y.startswith(x.rstrip("/") + "/")
        for x in forms(a)
        for y in forms(b)
    )


def sha256(path: str) -> str | None:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def utc(ns: object) -> str | None:
    if not isinstance(ns, int):
        return None
    return datetime.datetime.fromtimestamp(ns / 1e9, datetime.timezone.utc).isoformat(timespec="microseconds")


def main() -> int:
    raw = json.loads(Path(sys.argv[1]).read_text())
    protected = json.loads(Path(sys.argv[2]).read_text())["cov2d_protected_paths"]
    out = Path(sys.argv[3])
    problems: list[str] = []
    files = raw.get("files", {})
    dependencies = [
        item
        for item in raw.get("mat_dependencies", [])
        if item.get("environment_key") == "MPARAMFILES" and item.get("relative_path") == RELATIVE
    ]
    if len(dependencies) != 1:
        problems.append(f"exception dependency entries: {len(dependencies)}, expected 1")
    entry = dependencies[0] if dependencies else {}
    original = entry.get("original")
    item = files.get(original, {}) if isinstance(original, str) else {}
    if not item:
        problems.append("the exception's original is not among the staged files")
    if isinstance(original, str) and os.path.realpath(EXCEPTION) != os.path.realpath(original):
        problems.append(f"the staged original {original} does not resolve to the listed exception")
    for side in ("stat_before", "stat_after"):
        value = item.get(side)
        if not (isinstance(value, dict) and set(value) == STAT_FIELDS and all(isinstance(v, int) for v in value.values())):
            problems.append(f"{side} is missing or lacks the five fields")
    if item.get("stat_before") != item.get("stat_after"):
        problems.append("stat_before differs from stat_after")
    window = item.get("staging_utc_ns")
    if not (
        isinstance(window, dict)
        and set(window) == {"started", "ended"}
        and all(isinstance(window[k], int) for k in ("started", "ended"))
        and window["started"] <= window["ended"]
    ):
        problems.append("staging_utc_ns is missing or malformed")
        window = {}
    measured = item.get("sha256")
    copies = {path: sha256(path) for path in (item.get("staged"), entry.get("staged")) if isinstance(path, str)}
    if len(copies) != 2 or any(value != measured for value in copies.values()):
        problems.append("a staged copy's sha256 differs from the measured original's, or a copy is missing")
    if entry.get("sha256") != measured:
        problems.append("the dependency entry's sha256 differs from the staged file's")
    overlapping = sorted(
        {name for name in files for path in protected if overlaps(name, path)}
    )
    others = [name for name in overlapping if os.path.realpath(name) != os.path.realpath(EXCEPTION)]
    if others:
        problems.append(f"other staged originals overlap protected paths: {others}")
    record = {
        "schema": "rpd-flux1-protected-read/1",
        "status": "PASS" if not problems else "FAIL",
        "problems": problems,
        "exception_as_listed": EXCEPTION,
        "original_resolved": original,
        "reads": "one stat-bracketed staging, with two O_NOATIME reads (custody copy(): noatime_digest, then stage_copy)",
        "sha256_measured_by_prepare": measured,
        "staged_copies_sha256": copies,
        "stat_before": item.get("stat_before"),
        "stat_after": item.get("stat_after"),
        "staging_utc_ns": window or None,
        "staging_utc": {k: utc(v) for k, v in window.items()} if window else None,
        "staged_originals": len(files),
        "staged_originals_overlapping_protected": overlapping,
    }
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
    print(f"PROTECTED READ: {record['status']}")
    for line in problems:
        print(f"  problem: {line}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
