#!/usr/bin/env python3
"""Retry-1 process-local remap for the one measured OI-136 PET loader insertion.

The receipt-bound full-event loader is historical source and remains byte-identical.  Retry 1 runs
that source under this narrow list adapter: only paths lexically rooted at the known primary
checkout are translated to the same relative path under the explicitly supplied immutable checkout.
The ordinary OI-136 import guard remains installed and still refuses every other checkout escape.
"""

import hashlib
import os
import runpy
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
CANONICAL_PRIMARY_ROOT = Path("/pscratch/sd/j/josephrb/MINERvA-OmniFold")
ORIGINAL_OPERANDS = {
    "materialize_pet_v2_equivalence_target.py":
        "6ae2ee6eaec3c4fc247b54115a8427cfae8e211dbda179d7cc69f2359ddd7fb6",
    "train_pet_v2_equivalence.py":
        "b004a2ce82128eb4391b50beb1b2d78e6adc439067efc1cd30dd5b82ab817832",
    "evaluate_pet_v2_equivalence.py":
        "6640970b246fb848f5f48c934de71dc71e2be6fd768e2fa66bcf4db843a57c54",
}


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def remap_primary_path(value):
    """Map only the exact known primary root or one of its lexical descendants."""
    try:
        candidate = Path(os.path.normpath(os.fspath(value)))
    except TypeError:
        return value
    primary = CANONICAL_PRIMARY_ROOT
    if candidate != primary and primary not in candidate.parents:
        return value
    relative = candidate.relative_to(primary)
    replacement = REPO / relative
    if not replacement.exists():
        raise SystemExit(
            f"[pet-v2-root-remap][FAIL] mapped checkout path does not exist: {replacement}"
        )
    return str(replacement)


class CheckoutRootPath(list):
    """A normal sys.path list whose position-0 inserts remap one measured stale root."""

    def __init__(self, values):
        super().__init__(values)
        self.redirects = []

    def insert(self, index, value):
        mapped = remap_primary_path(value)
        if mapped != value:
            while mapped in self:
                self.remove(mapped)
            self.redirects.append({"requested": os.fspath(value), "mapped": mapped})
            print(
                f"[pet-v2-root-remap] {os.fspath(value)} -> {mapped}",
                file=sys.stderr,
                flush=True,
            )
        super().insert(index, mapped)


def install():
    if isinstance(sys.path, CheckoutRootPath):
        return sys.path
    adapted = CheckoutRootPath(sys.path)
    sys.path = adapted
    return adapted


def run_original(name):
    if name not in ORIGINAL_OPERANDS:
        raise SystemExit(f"[pet-v2-root-remap][FAIL] unapproved original operand: {name}")
    supplied_root = Path(os.environ.get("PETV2_CODE_ROOT", "")).resolve()
    if supplied_root != REPO:
        raise SystemExit(
            f"[pet-v2-root-remap][FAIL] PETV2_CODE_ROOT {supplied_root} != wrapper root {REPO}"
        )
    expected_head = os.environ.get("PETV2_EXPECTED_HEAD")
    observed_head = subprocess.check_output(
        ["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True
    ).strip()
    if not expected_head or observed_head != expected_head:
        raise SystemExit(
            f"[pet-v2-root-remap][FAIL] checkout HEAD {observed_head} != {expected_head}"
        )
    original = Path(__file__).resolve().parent / name
    observed_sha = _sha256(original)
    if observed_sha != ORIGINAL_OPERANDS[name]:
        raise SystemExit(
            f"[pet-v2-root-remap][FAIL] original operand hash {observed_sha} "
            f"!= {ORIGINAL_OPERANDS[name]} for {name}"
        )
    adapted = install()
    sys.argv[0] = str(original)
    try:
        runpy.run_path(str(original), run_name="__main__")
    except SystemExit as exc:
        if exc.code in (None, 0) and not adapted.redirects:
            raise SystemExit(
                "[pet-v2-root-remap][FAIL] original process made no canonical-root insertion"
            ) from None
        raise
    else:
        if not adapted.redirects:
            raise SystemExit(
                "[pet-v2-root-remap][FAIL] original process made no canonical-root insertion"
            )
