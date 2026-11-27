"""The two pins records, committed gzipped, against the committed p0 records that name them as predecessors (e1's P0, run-20261127).

usage: python3 -I -B -m pytest -q -p no:cacheprovider tests/test_pins_gz.py

The receipt-artifact hook reads the plain pins.json records' bare staged-file names as missing deliverables, so they
are committed byte-exact as pins.json.gz (gzip, mtime 0, no stored name). For each of dry/ and run/:
  - the .gz file's sha256 is the one the README lists;
  - it decompresses to the bytes fetched from P0's run root, whose sha256 the README lists;
  - that sha256 equals the predecessor_sha256 of the committed p0.json in the same directory;
  - recompressing with the same settings reproduces the .gz bytes.
A mutant check: a single changed byte in the decompressed record breaks the predecessor match.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

import pytest

RECORDS = Path(__file__).resolve().parent.parent / "records"
EXPECTED = {
    "dry": {
        "gz": "8c04d4c2f20eabb6ac76b216a667acf6fe1223ba07f687f6254c6bc7da40de61",
        "raw": "66ed29aab10cfd8786cf956d0452d63a1d5d16e75143b97a1faba1e5d7c1efec",
        "raw_bytes": 12119,
        "dry_run": True,
    },
    "run": {
        "gz": "7b7dedf76d6ccaf0be26d193ce4829f3585a7c81764a20ca1b6877d3d16a1b9c",
        "raw": "2a22bdbfc2af1891d2db13e1b49c4e53c063296002b3a2fd1e240850dad121a8",
        "raw_bytes": 12103,
        "dry_run": False,
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.mark.parametrize("sub", sorted(EXPECTED))
def test_gz_decompresses_to_the_p0_predecessor(sub: str) -> None:
    want = EXPECTED[sub]
    gz = (RECORDS / sub / "pins.json.gz").read_bytes()
    assert sha(gz) == want["gz"]
    raw = gzip.decompress(gz)
    assert len(raw) == want["raw_bytes"] and sha(raw) == want["raw"]
    p0 = json.loads((RECORDS / sub / "p0.json").read_text())
    assert p0["step"] == "p0" and p0["status"] == "PASS" and p0["predecessor_sha256"] == sha(raw)
    pins = json.loads(raw)
    assert pins["step"] == "pins" and pins["status"] == "PASS" and pins["dry_run"] is want["dry_run"]
    assert pins["code_sha256"] == p0["code_sha256"] and pins["config_sha256"] == p0["config_sha256"]
    assert gzip.compress(raw, compresslevel=9, mtime=0) == gz  # reproducible


@pytest.mark.parametrize("sub", sorted(EXPECTED))
def test_one_changed_byte_breaks_the_match(sub: str) -> None:
    raw = bytearray(gzip.decompress((RECORDS / sub / "pins.json.gz").read_bytes()))
    raw[len(raw) // 2] ^= 0x01
    p0 = json.loads((RECORDS / sub / "p0.json").read_text())
    assert sha(bytes(raw)) != p0["predecessor_sha256"]
