"""The two pins records, committed gzipped, against the committed p0 records that name them as predecessors.

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
        "gz": "77ddff10062e17a97f311827266628643ba75a0fa8c993c250ca24cb9c2caa21",
        "raw": "ce181449d5ba6dbafc4a5831b7918c4d3cc538114062ce23c5e464291bcc3f76",
        "raw_bytes": 12069,
        "dry_run": True,
    },
    "run": {
        "gz": "36b6738110cfc651ecbfb8b4f7f95fd0dba11891a395558973e1e9141fd0871e",
        "raw": "52fc41f41cf17954ceddab8c581aa327a62d160c059cbee8bf2941c1880e5c8a",
        "raw_bytes": 12053,
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
