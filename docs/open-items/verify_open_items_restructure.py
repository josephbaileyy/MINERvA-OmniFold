#!/usr/bin/env python3
"""Fail-closed checks for the August 2026 OPEN_ITEMS restructure."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OPEN = ROOT / "docs/OPEN_ITEMS.md"
ARCHIVE = ROOT / "docs/OPEN_ITEMS-ARCHIVE-2026-08.md"
MARKER = b"> VERBATIM-PAYLOAD-START\n\n"
ORIGINAL_SHA256 = "7cc80b34e2e025bf3096233f330bffa8fd76f8d584d6d34a8291fb1889e1e9e1"
ORIGINAL_BYTES = 102146
ORIGINAL_NONWS_SHA256 = "ea18ab1dc267529fc8e7ad64574c07713700e8ecc4b69dc90e8fdd1f09467ff1"
ORIGINAL_NONWS_BYTES = 84068
THRESHOLD_BLOCK_SHA256 = "7c52070eb8c95b157a5ddb070b93df5011cfa35ba2e3d53c29609e6517cbc357"

CONTROLLED_STATES = {"OPEN", "BLOCKED", "RUNNING", "WAITING-USER"}
CANONICAL_PROOFS = {
    "D2/niter chronology": (
        "docs/orchestration/CLAIM-CLM-010.md",
        ("niter` 2->3", "56397442", "Undated residual (i)"),
    ),
    "adopted D2 recovery bar": (
        "docs/orchestration/CLAIM-CLM-012.md",
        ("0.4945824", "recovery"),
    ),
    "retired thresholds and self-report": (
        "docs/orchestration/INDEX-retracted-and-superseded-values.md",
        ("recovery >= 0.80", "recovery_criteria_met"),
    ),
    "GBDT close-out footing": (
        "docs/orchestration/RUNBOOK-20260807-gbdt-closeout.md",
        ("purity", "187-universe"),
    ),
    "standard-P4 debt and CI": (
        "docs/orchestration/PROVENANCE-DEBT-20260810-standard-p4.md",
        ("Packet B", "no CI"),
    ),
    "PET measurement/weight decision": (
        "docs/orchestration/DECISION-20260804-B4-STEP3-RECEIPTS.md",
        ("w_reco", "w_truth", "Gate 2"),
    ),
    "PET feature and geometry contract": (
        "nd-unfolding/pet/FULL_EVENT_FEATURE_CONTRACT.md",
        ("MNV101_FULL_PHASE_SPACE=1", "coord_idx", "no-truth-leakage"),
    ),
    "indexed code-defect classes": (
        "KNOWN_ISSUES.md",
        ("Merged TParameters", "J36", "E_avail"),
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def split_pipe_row(line: str) -> list[str]:
    if not line.startswith("|") or not line.endswith("|"):
        raise AssertionError(f"not a pipe-table row: {line!r}")
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in line[1:-1]:
        if char == "|" and not escaped:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        escaped = char == "\\" and not escaped
        if char != "\\":
            escaped = False
    cells.append("".join(current).strip())
    return cells


def verify_conservation() -> None:
    archive = ARCHIVE.read_bytes()
    assert archive.count(MARKER) == 1, "archive payload marker is absent or duplicated"
    payload = archive.split(MARKER, 1)[1]
    compact = re.sub(rb"\s+", b"", payload)
    assert len(payload) == ORIGINAL_BYTES
    assert sha256(payload) == ORIGINAL_SHA256
    assert len(compact) == ORIGINAL_NONWS_BYTES
    assert sha256(compact) == ORIGINAL_NONWS_SHA256

    lines = payload.splitlines(keepends=True)
    threshold = b"".join(lines[435:460])
    assert sha256(threshold) == THRESHOLD_BLOCK_SHA256
    print(
        "conservation: PASS "
        f"(exact={len(payload)} bytes, nonwhitespace={len(compact)} chars, "
        "threshold-retirement block exact)"
    )


def verify_table() -> None:
    raw = OPEN.read_bytes()
    text = raw.decode("utf-8")
    lines = text.splitlines()
    byte_lengths = [len(line.encode("utf-8")) for line in lines]
    assert max(byte_lengths, default=0) <= 400
    assert "<table" not in text.lower()

    table = [line for line in lines if line.startswith("|")]
    assert len(table) >= 3
    rows = [split_pipe_row(line) for line in table]
    widths = {len(row) for row in rows}
    assert widths == {7}, f"column widths differ: {sorted(widths)}"
    assert rows[0] == ["id", "state", "lane/owner", "blocker", "next action", "detail", "as_of"]

    data = rows[2:]
    expected_ids = [f"OI-{number}" for number in range(1, len(data) + 1)]
    assert [row[0] for row in data] == expected_ids
    assert all(row[1] in CONTROLLED_STATES for row in data)
    assert all(row[4].endswith(".") for row in data), "each next action must be one executable sentence"

    link_re = re.compile(r"\[[^]]+\]\(([^)]+)\)")
    pointers = 0
    for row in data:
        links = link_re.findall(row[5])
        assert links, f"{row[0]} has no detail pointer"
        for target in links:
            if re.match(r"^[a-z]+://", target):
                continue
            path = target.split("#", 1)[0]
            resolved = (OPEN.parent / path).resolve()
            assert resolved.exists(), f"{row[0]} pointer does not resolve: {target}"
            pointers += 1

    print(
        f"table: PASS (rows={len(data)}, columns=7, pointers={pointers}, "
        f"lines={len(lines)}, bytes={len(raw)}, max_line_bytes={max(byte_lengths)})"
    )


def verify_canonical_homes() -> None:
    for label, (relative, phrases) in CANONICAL_PROOFS.items():
        path = ROOT / relative
        text = path.read_text(encoding="utf-8")
        missing = [phrase for phrase in phrases if phrase not in text]
        assert not missing, f"{label} missing from {relative}: {missing}"
        print(f"canonical proof: PASS {label} -> {relative} ({', '.join(phrases)})")


if __name__ == "__main__":
    verify_conservation()
    verify_table()
    verify_canonical_homes()
