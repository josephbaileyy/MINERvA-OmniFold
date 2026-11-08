#!/usr/bin/env python3
"""Check that no environment-value fingerprint from the raw prepare record reaches a file bound for the repo.

Checks, each recorded:
  1. the view has no environment_snapshot.fingerprints map;
  2. no 64-hex string appears anywhere under the view's environment_snapshot or environment_after_setup;
  3. no fingerprint value from the raw record appears in the view, or in any other listed file. The fingerprint of
     the empty string (a public constant) is counted apart: in the view it fails, elsewhere it is reported only;
  4. every 64-hex string elsewhere in the view is listed by its JSON path, for the record.
Prints CHECK lines and a final verdict; exits 0 on PASS, 1 on FAIL.

usage: check_redaction.py RAW_PREPARE VIEW [OTHER_FILE ...]
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HEX64 = re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])")
EMPTY = hashlib.sha256(b"").hexdigest()
ENV_SECTIONS = ("environment_snapshot", "environment_after_setup")


def walk(node, path=""):
    """Yield (json_path, text) for every key and string value."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield f"{path}/{key}#key", str(key)
            yield from walk(value, f"{path}/{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk(value, f"{path}[{index}]")
    elif isinstance(node, str):
        yield path, node


def main() -> int:
    raw = json.loads(Path(sys.argv[1]).read_text())
    view_path = Path(sys.argv[2])
    others = [Path(p) for p in sys.argv[3:]]
    fingerprints = raw["environment_snapshot"]["fingerprints"]
    by_value: dict[str, list[str]] = {}
    for key, value in fingerprints.items():
        by_value.setdefault(value.lower(), []).append(key)
    view = json.loads(view_path.read_text())
    failures = 0
    print(f"CHECK: raw fingerprints {len(fingerprints)} keys, {len(by_value)} distinct values")

    present = "fingerprints" in view.get("environment_snapshot", {})
    print(f"CHECK 1 view environment_snapshot.fingerprints present: {present}")
    failures += present

    env_hex = [
        (path, match)
        for path, text in walk(view)
        if path.lstrip("/").split("/")[0] in ENV_SECTIONS
        for match in HEX64.findall(text)
    ]
    print(f"CHECK 2 64-hex strings under {'/'.join(ENV_SECTIONS)} in the view: {len(env_hex)}")
    for path, _ in env_hex:
        print(f"  at {path}")
    failures += bool(env_hex)

    for target in [view_path, *others]:
        text = target.read_text(errors="replace").lower()
        hits = sorted(value for value in by_value if value in text)
        secret = [value for value in hits if value != EMPTY]
        empty = EMPTY in hits
        print(
            f"CHECK 3 {target.name}: fingerprint values found {len(secret)}"
            f"; empty-string fingerprint found {empty}"
        )
        for value in secret:
            print(f"  fingerprint of keys {sorted(by_value[value])}")
        failures += bool(secret) or (empty and target == view_path)

    elsewhere = [
        (path, match)
        for path, text in walk(view)
        if path.lstrip("/").split("/")[0] not in ENV_SECTIONS
        for match in HEX64.findall(text)
    ]
    print(f"CHECK 4 other 64-hex strings in the view (record only): {len(elsewhere)}")
    for path, match in elsewhere:
        print(f"  {path} {match}")

    verdict = "PASS" if failures == 0 else "FAIL"
    print(f"REDACTION CHECK: {verdict}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
