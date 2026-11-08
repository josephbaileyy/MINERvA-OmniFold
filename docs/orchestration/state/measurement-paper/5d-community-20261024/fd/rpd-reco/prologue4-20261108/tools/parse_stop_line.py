#!/usr/bin/env python3
"""Parse the classifier's STOP line in a prologue wrapper.out into a JSON file of its entries.

wrapper.out (the prologue wrapper's stdout and stderr) holds exactly one line that begins
"STOP DATA_FREE_TRACE: syscall custody violations: ", followed by a JSON list. This writes that list, unchanged and in
order, with the line's location and the source's sha256, and counts the entries by reason. Nothing is classified or
interpreted. Losslessness is checked two ways: json.dumps of the parsed list must equal the line's JSON text byte for
byte, and the prefix plus that text must equal the whole line. Exits 0 when both hold, 1 otherwise.

usage: parse_stop_line.py WRAPPER_OUT OUT_JSON
(WRAPPER_OUT is recorded as given; pass its repo-relative path.)
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

PREFIX = "STOP DATA_FREE_TRACE: syscall custody violations: "


def main() -> int:
    source, out = Path(sys.argv[1]), Path(sys.argv[2])
    data = source.read_bytes()
    lines = data.decode().split("\n")
    hits = [(number, line) for number, line in enumerate(lines, 1) if line.startswith(PREFIX)]
    if len(hits) != 1:
        raise SystemExit(f"PARSE: expected one STOP line, found {len(hits)}")
    number, line = hits[0]
    text = line[len(PREFIX):]
    entries = json.loads(text)
    same_text = json.dumps(entries) == text
    same_line = PREFIX + json.dumps(entries) == line
    reasons = Counter(entry.get("reason") for entry in entries)
    record = {
        "schema": "rpd-prologue-classifier-stop-entries/1",
        "source_path": str(source),
        "source_bytes_digest_sha256": hashlib.sha256(data).hexdigest(),
        "line_number": number,
        "line_characters": len(line),
        "prefix": PREFIX,
        "entry_count": len(entries),
        "entries_by_reason": dict(sorted(reasons.items())),
        "roundtrip_json_text_equal": same_text,
        "roundtrip_line_equal": same_line,
        "entries": entries,
    }
    out.write_text(json.dumps(record, indent=1) + "\n")
    print(f"PARSE: {source.name} sha256 {record['source_bytes_digest_sha256']}; STOP line {number}, {len(line)} characters")
    print(f"PARSE: {len(entries)} entries; by reason {json.dumps(record['entries_by_reason'], sort_keys=True)}")
    print(f"PARSE: json.dumps(entries) equals the line's JSON text: {same_text}; prefix + it equals the line: {same_line}")
    print(f"PARSE: wrote {out.name} sha256 {hashlib.sha256(out.read_bytes()).hexdigest()}")
    return 0 if same_text and same_line else 1


if __name__ == "__main__":
    sys.exit(main())
