#!/usr/bin/env python3
"""d2s0 connect checks (P0's p0_checks.py plus a stage mode), run on the login node before anything is staged.

usage: d2s0_checks.py inputs EXPECTED_JSON
       d2s0_checks.py stat EXPECTED_JSON
       d2s0_checks.py stage SOURCE SHA256 DESTINATION

inputs  Reads each in-place input (EXPECTED_JSON "inputs": path -> sha256): flux4's records and factor products, from
        the committed run-62051670 records, and p0e1's run/pins.json and run/p0.json, from the committed run-20261127
        records.
        Each is read with O_NOATIME and its sha256 compared. A missing file, a missing O_NOATIME flag or any
        difference exits 3.
stat    Stats (never opens) the three selected gen2thin flux files, the 24 dumps, the 12 RDX omnifiles and the
        true-energy sidecar (EXPECTED_JSON "stat": path -> {bytes, inode}; S1's survey of 2026-11-22 for the
        first 27, the sidecar probe of 2026-11-26 for the other 13) and prints each one's bytes, atime, mtime and
        inode, then the earliest purge exposure (atime + PURGE_DAYS days, the oldest first). A missing file, or
        bytes or an inode different from the record, exits 3.
stage   Copies SOURCE to DESTINATION byte for byte: SOURCE read once with O_NOATIME and its sha256 required to equal
        SHA256; DESTINATION created exclusively (O_EXCL, mode 0600, never overwritten), written, flushed and synced,
        then read back and its sha256 required to equal SHA256. A failure after DESTINATION is created tries to remove
        it and exits 3; if that removal fails, or the process is interrupted, a partial DESTINATION can remain. The
        connect stops before starting the runner in every such case.
inputs and stat print one line per file and a final verdict line and write no file; stage prints one line.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time

PURGE_DAYS = 56  # pscratch purges files unread for 8 weeks (gen_flux2.py's PURGE_DAYS)


def utc(epoch: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


def noatime_sha256(path: str, flag: int) -> str:
    descriptor = os.open(path, os.O_RDONLY | flag)
    checksum = hashlib.sha256()
    with os.fdopen(descriptor, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            checksum.update(block)
    return checksum.hexdigest()


def check_inputs(expected: dict[str, str]) -> int:
    flag = getattr(os, "O_NOATIME", None)
    if flag is None:
        print("INPUTS: STOP: this platform has no O_NOATIME")
        return 3
    bad = 0
    for path, want in sorted(expected.items()):
        try:
            got = noatime_sha256(path, flag)
        except OSError as error:
            print(f"MISSING {path}: {error}")
            bad += 1
            continue
        ok = got == want
        bad += not ok
        print(f"{'ok ' if ok else 'DIFF'} sha256 {got} (expected {want}) {path}")
    print(f"INPUTS: {'PASS' if bad == 0 else 'STOP'} ({len(expected)} files, {bad} bad)")
    return 0 if bad == 0 else 3


def check_stat(expected: dict[str, dict[str, int]]) -> int:
    bad = 0
    atimes = []
    print("name|bytes|atime|mtime|inode|verdict")
    for path, want in sorted(expected.items()):
        try:
            info = os.stat(path)
        except OSError as error:
            print(f"{path}|MISSING: {error}")
            bad += 1
            continue
        same = info.st_size == want["bytes"] and info.st_ino == want["inode"]
        bad += not same
        atimes.append((info.st_atime, path))
        verdict = "same as recorded" if same else f"DIFFERS from the record (bytes {want['bytes']}, inode {want['inode']})"
        print(f"{path}|{info.st_size}|{int(info.st_atime)}|{int(info.st_mtime)}|{info.st_ino}|{verdict}")
    if atimes:
        oldest, path = min(atimes)
        print(f"earliest purge exposure {utc(oldest + PURGE_DAYS * 86400)} ({path}, atime {utc(oldest)})")
    print(f"STAT: {'PASS' if bad == 0 else 'STOP'} ({len(expected)} files, {bad} missing or different)")
    return 0 if bad == 0 else 3


def stage(source: str, expected: str, destination: str) -> int:
    flag = getattr(os, "O_NOATIME", None)
    if flag is None:
        print("STAGE: STOP: this platform has no O_NOATIME")
        return 3
    try:
        descriptor = os.open(source, os.O_RDONLY | flag)
        with os.fdopen(descriptor, "rb") as stream:
            data = stream.read()
    except OSError as error:
        print(f"STAGE: STOP: cannot read {source}: {error}")
        return 3
    got = hashlib.sha256(data).hexdigest()
    if got != expected:
        print(f"STAGE: STOP: {source} sha256 {got}, expected {expected}")
        return 3
    try:
        out = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except OSError as error:
        print(f"STAGE: STOP: cannot create {destination}: {error}")
        return 3
    try:
        with os.fdopen(out, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        with open(destination, "rb") as stream:
            back = hashlib.sha256(stream.read()).hexdigest()
        if back != expected:
            raise OSError(f"read back sha256 {back}")
    except OSError as error:
        try:
            os.unlink(destination)
        except OSError as removal:
            print(f"STAGE: could not remove the partial {destination}: {removal}")
        print(f"STAGE: STOP: {destination} not written byte for byte: {error}")
        return 3
    print(f"STAGE: PASS sha256 {expected} {source} -> {destination}")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 5 and argv[1] == "stage":
        return stage(argv[2], argv[3], argv[4])
    if len(argv) != 3 or argv[1] not in {"inputs", "stat"}:
        print(__doc__)
        return 2
    with open(argv[2], encoding="utf-8") as handle:
        expected = json.load(handle)
    if argv[1] == "inputs":
        return check_inputs(expected["inputs"])
    return check_stat(expected["stat"])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
