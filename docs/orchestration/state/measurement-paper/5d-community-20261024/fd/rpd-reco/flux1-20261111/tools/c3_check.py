#!/usr/bin/env python3
"""Check where the code put the canonical fingerprint-bearing prepare record (C3), and that nothing sent is it.

At #848's head a4c3e556, custody prepare writes the canonical prestage record owner-only outside the run, at
custody.private_prepare_path(run, "prestage", connect_id) =
realpath(run).parent/.rpd-private/sha256(realpath(run) NUL "prestage" NUL connect_id)/prestage.json,
and leaves in the run a reference, prestage-reference.json, naming its path and sha256.
Checks, each recorded:
  1. the reference's schema, run, prepare name, and that its path equals the location recomputed here;
  2. the record is under ROOT/.rpd-private and not under the run directory;
  3. the record and its directory are owned by this uid, with no group or other bits (modes printed);
  4. the record's sha256 equals the reference's, and it holds environment_snapshot.fingerprints (the count printed);
  5. ROOT/.rpd-private holds exactly that one file (every entry listed by type, mode and relative path);
  6. no file on the send list lies under .rpd-private, or has the record's sha256.
Prints C3 lines and a verdict; exits 0 on PASS, 1 on FAIL.

usage: c3_check.py ROOT RUN SEND_FILE [SEND_FILE ...]
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
from pathlib import Path


def main() -> int:
    root, run = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    send = [Path(p) for p in sys.argv[3:]]
    failures = 0

    def check(label: str, ok: bool) -> None:
        nonlocal failures
        print(f"C3 {label}: {'ok' if ok else 'FAIL'}")
        failures += not ok

    reference = json.loads((run / "prestage-reference.json").read_text())
    item = reference["private_prepare"]
    path = Path(item["path"])
    token = hashlib.sha256(
        (str(run) + "\0" + "prestage" + "\0" + reference["connect_id"]).encode()
    ).hexdigest()
    expected = (run.parent / ".rpd-private" / token / "prestage.json").resolve()
    print(f"C3 reference schema {reference.get('schema')}; status {reference.get('status')}; "
          f"prepare_name {reference.get('prepare_name')}; run {reference.get('run')}")
    print(f"C3 private path {path}")
    print(f"C3 recomputed   {expected}")
    check("1 reference names the recomputed location",
          reference.get("schema") == "fd-rpd-reco-private-prepare-reference/1"
          and reference.get("prepare_name") == "prestage"
          and reference.get("run") == str(run)
          and path.resolve() == expected)
    check("2 under ROOT/.rpd-private and not under the run",
          (root / ".rpd-private") in path.resolve().parents and run not in path.resolve().parents)
    info, parent = os.lstat(path), os.lstat(path.parent)
    print(f"C3 record mode {stat.filemode(info.st_mode)} uid {info.st_uid}; "
          f"directory mode {stat.filemode(parent.st_mode)} uid {parent.st_uid}; this uid {os.getuid()}")
    check("3 owner-only file and directory",
          stat.S_ISREG(info.st_mode) and stat.S_ISDIR(parent.st_mode)
          and info.st_uid == os.getuid() and parent.st_uid == os.getuid()
          and info.st_mode & 0o077 == 0 and parent.st_mode & 0o077 == 0)
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    record = json.loads(data)
    count = len(record.get("environment_snapshot", {}).get("fingerprints", {}))
    print(f"C3 record sha256 {digest} (reference {item.get('sha256')}); environment fingerprints {count} keys")
    check("4 digest equals the reference and the record carries the fingerprints",
          digest == item.get("sha256") and count > 0)
    entries = []
    for dirpath, dirnames, filenames in os.walk(root / ".rpd-private"):
        dirnames.sort()
        for name in sorted(dirnames) + sorted(filenames):
            full = Path(dirpath) / name
            st = os.lstat(full)
            entries.append((stat.filemode(st.st_mode), str(full.relative_to(root))))
    for mode, rel in entries:
        print(f"C3 private entry {mode} {rel}")
    files = [rel for mode, rel in entries if mode.startswith("-")]
    check("5 .rpd-private holds exactly the one record",
          files == [str(path.resolve().relative_to(root))] and all(m[0] in "-d" for m, _ in entries))
    leaked = [str(p) for p in send
              if ".rpd-private" in p.resolve().parts or hashlib.sha256(p.read_bytes()).hexdigest() == digest]
    print(f"C3 send files examined {len(send)}; under .rpd-private or equal to the record: {leaked}")
    check("6 nothing on the send list is the record", not leaked)
    print(f"C3 CHECK: {'PASS' if failures == 0 else 'FAIL'}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
