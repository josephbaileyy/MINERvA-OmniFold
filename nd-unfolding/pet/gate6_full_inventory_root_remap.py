#!/usr/bin/env python3
"""Run the frozen full-event extractor while remapping one measured OI-136 insertion.

``fullevent_fps_dataloader.py`` is a hash-bound scientific operand.  At import time it inserts
two paths below the historical primary checkout at ``sys.path[0]``.  This adapter changes only
those two lexical descendants to the same relative paths below the explicitly named immutable
checkout.  The ordinary OI-136 guard remains installed in this interpreter and refuses every
other checkout escape.
"""

from __future__ import annotations

import hashlib
import os
import runpy
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
CANONICAL_PRIMARY_ROOT = Path("/pscratch/sd/j/josephrb/MINERvA-OmniFold")
EXTRACTOR = REPO / "nd-unfolding/pet/extract_fullevent_fps.py"
LOADER = REPO / "nd-unfolding/pet/fullevent_fps_dataloader.py"
EXPECTED_SOURCE_HASHES = {
    EXTRACTOR: "de0f044b612782edb58e152205b426e6dbbca7637b7f3f342a1373fe4dc7d51a",
    LOADER: "e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def remap_primary_path(value):
    """Map only the exact primary root or one of its lexical descendants."""
    try:
        candidate = Path(os.path.normpath(os.fspath(value)))
    except TypeError:
        return value
    if candidate != CANONICAL_PRIMARY_ROOT and CANONICAL_PRIMARY_ROOT not in candidate.parents:
        return value
    relative = candidate.relative_to(CANONICAL_PRIMARY_ROOT)
    replacement = REPO / relative
    if not replacement.exists():
        raise SystemExit(f"[gap1-root-remap][FAIL] mapped path does not exist: {replacement}")
    return str(replacement)


class CheckoutRootPath(list):
    """A normal ``sys.path`` list with one bounded insertion remap."""

    def __init__(self, values):
        super().__init__(values)
        self.redirects: list[dict[str, str]] = []

    def insert(self, index, value):
        mapped = remap_primary_path(value)
        if mapped != value:
            while mapped in self:
                self.remove(mapped)
            self.redirects.append({"requested": os.fspath(value), "mapped": mapped})
            print(f"[gap1-root-remap] {os.fspath(value)} -> {mapped}", file=sys.stderr, flush=True)
        super().insert(index, mapped)


def _validate_checkout() -> None:
    supplied = Path(os.environ.get("G6_GAP1_CODE_ROOT", "")).resolve()
    if supplied != REPO:
        raise SystemExit(f"[gap1-root-remap][FAIL] supplied code root {supplied} != {REPO}")
    expected_head = os.environ.get("G6_GAP1_EXPECTED_HEAD")
    observed_head = subprocess.check_output(
        ["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True
    ).strip()
    if not expected_head or observed_head != expected_head:
        raise SystemExit(
            f"[gap1-root-remap][FAIL] checkout HEAD {observed_head} != {expected_head}"
        )
    for path, expected in EXPECTED_SOURCE_HASHES.items():
        observed = _sha256(path)
        if observed != expected:
            raise SystemExit(
                f"[gap1-root-remap][FAIL] source hash {observed} != {expected} for {path}"
            )


def main() -> None:
    _validate_checkout()
    adapted = CheckoutRootPath(sys.path)
    sys.path = adapted
    os.environ["MNV_REPO"] = str(REPO)
    sys.argv[0] = str(EXTRACTOR)
    try:
        runpy.run_path(str(EXTRACTOR), run_name="__main__")
    except SystemExit as exc:
        if exc.code in (None, 0) and len(adapted.redirects) != 2:
            raise SystemExit(
                f"[gap1-root-remap][FAIL] expected exactly two primary-root inserts; "
                f"observed {len(adapted.redirects)}"
            ) from None
        raise
    else:
        if len(adapted.redirects) != 2:
            raise SystemExit(
                f"[gap1-root-remap][FAIL] expected exactly two primary-root inserts; "
                f"observed {len(adapted.redirects)}"
            )


if __name__ == "__main__":
    main()
