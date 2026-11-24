#!/usr/bin/env python3
"""P0 connect checks, run on the login node before anything is staged (director's rulings 1 and 5, 2026-11-23).

usage: p0_checks.py inputs EXPECTED_JSON
       p0_checks.py stat EXPECTED_JSON

inputs  Reads each of flux3's records and factor products that P0 reads in place (EXPECTED_JSON "inputs": path ->
        sha256, from the committed run-61861637 records) with O_NOATIME, and compares its sha256. A missing file, a
        missing O_NOATIME flag or any difference exits 3.
stat    Stats (never opens) the three selected gen2thin flux files and the 24 dumps (EXPECTED_JSON "stat": path ->
        {bytes, inode}, from S1's survey of 2026-11-22) and prints each one's bytes, atime, mtime and inode, then the
        earliest purge exposure (atime + PURGE_DAYS days, the oldest first). A missing file, or bytes or an inode
        different from S1's, exits 3.
Both print one line per file and a final verdict line. Neither writes a file.
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
        print("P0 INPUTS: STOP: this platform has no O_NOATIME")
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
    print(f"P0 INPUTS: {'PASS' if bad == 0 else 'STOP'} ({len(expected)} files, {bad} bad)")
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
        verdict = "same as S1" if same else f"DIFFERS from S1 (bytes {want['bytes']}, inode {want['inode']})"
        print(f"{path}|{info.st_size}|{int(info.st_atime)}|{int(info.st_mtime)}|{info.st_ino}|{verdict}")
    if atimes:
        oldest, path = min(atimes)
        print(f"earliest purge exposure {utc(oldest + PURGE_DAYS * 86400)} ({path}, atime {utc(oldest)})")
    print(f"P0 STAT: {'PASS' if bad == 0 else 'STOP'} ({len(expected)} files, {bad} missing or different)")
    return 0 if bad == 0 else 3


def main(argv: list[str]) -> int:
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
