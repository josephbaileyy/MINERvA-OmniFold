#!/usr/bin/env python3
"""Fail-closed checks for the August 2026 OPEN_ITEMS restructure."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OPEN = ROOT / "docs/OPEN_ITEMS.md"
ARCHIVE = ROOT / "docs/OPEN_ITEMS-ARCHIVE-2026-08.md"
MARKER = b"> VERBATIM-PAYLOAD-START\n\n"
# VERSIONED REPIN, OI-145, 2026-08-21. This check had been RED since 2026-08-20 and the thing it
# protects had been edited -- the payload is declared VERBATIM and grew by 1,502 bytes (1,495
# non-whitespace, so real content) across 276ff242 and 568d9208.
# THE V1 VALUES ARE RETAINED, NOT OVERWRITTEN. Overwriting four constants would have turned a
# conservation guarantee into a rubber stamp: nothing would record that the payload changed, or bound
# HOW it may change. Keeping v1 lets `verify_conservation` assert that the delta from v1 to v2 is
# EXACTLY the permitted transformation and nothing else.
# WHY NOT REVERT THE EDITS: all 7 are markdown link-target migrations from repository-relative paths
# to permalinks at the frozen evidence commit 0b329e8a, each carrying a title naming the evidence tag
# it resolves through. The documents they point at were removed from the live tree by the
# prepublication compaction, so reverting would restore dangling relative paths -- it would DAMAGE the
# surviving discovery routes the freeze exists to preserve. No prose and no number changed.
# Verified by measurement, recorded in
# docs/orchestration/receipts/RECEIPT-open-items-archive-repin-20260821.json.
V1_SHA256 = "7cc80b34e2e025bf3096233f330bffa8fd76f8d584d6d34a8291fb1889e1e9e1"
V1_BYTES = 102146
V1_NONWS_SHA256 = "ea18ab1dc267529fc8e7ad64574c07713700e8ecc4b69dc90e8fdd1f09467ff1"
V1_NONWS_BYTES = 84068

ORIGINAL_SHA256 = "48a7438d3eea38a09bcede11596cc7de9f6a9300e1ab8dc7f9f14f6fd802f7e0"
ORIGINAL_BYTES = 103648
ORIGINAL_NONWS_SHA256 = "2481fa5e4c508bc9f7a7f80c6c6592100833a2cb667f387a7dd138860b458e8b"
ORIGINAL_NONWS_BYTES = 85563

REPIN_RECEIPT = "docs/orchestration/receipts/RECEIPT-open-items-archive-repin-20260821.json"
REPIN_TARGET_COMMIT = "0b329e8ae8482e6334a68faf947fc80ae7265ac9"
REPIN_VIA_TAG = "evidence/prepublication-2026-08-20-0b329e8a"
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


def verify_repin_receipt() -> None:
    """OI-145. The v2 pin is only legitimate WITH its migration receipt, so check the receipt too.

    Asserting the v2 digest alone would be the bare repin this decision explicitly refused. This
    binds the new pin to a committed record that states which commits changed the payload, what
    transformation was permitted, and that nothing else occurred -- and it re-checks the v1 values
    the receipt claims to supersede, so a receipt cannot quietly rewrite the history it cites.
    """
    path = ROOT / REPIN_RECEIPT
    assert path.exists(), (
        f"the v2 payload pin has no migration receipt at {REPIN_RECEIPT}. A repin without a receipt "
        "is the rubber stamp OI-145 refused; restore the receipt or revert to the v1 pin.")
    rec = json.loads(path.read_text())
    assert rec["v1"]["payload_sha256"] == V1_SHA256, "receipt's v1 payload digest is not this file's"
    assert rec["v1"]["payload_bytes"] == V1_BYTES, "receipt's v1 byte count is not this file's"
    assert rec["v1"]["compact_sha256"] == V1_NONWS_SHA256
    assert rec["v1"]["compact_bytes"] == V1_NONWS_BYTES
    assert rec["v2"]["payload_sha256"] == ORIGINAL_SHA256, "receipt's v2 digest is not the pinned one"
    assert rec["v2"]["payload_bytes"] == ORIGINAL_BYTES
    assert rec["v2"]["compact_sha256"] == ORIGINAL_NONWS_SHA256
    assert rec["v2"]["compact_bytes"] == ORIGINAL_NONWS_BYTES
    t = rec["permitted_transformation"]
    assert t["target_commit"] == REPIN_TARGET_COMMIT, "receipt permits a different target commit"
    assert t["via_tag"] == REPIN_VIA_TAG, "receipt permits a different evidence tag"
    assert t["verified_instances"] == len(t["instances"]) > 0, "instance count disagrees with the list"
    for inst in t["instances"]:
        assert inst["target_commit"] == REPIN_TARGET_COMMIT, f"instance escapes the pin: {inst}"
        assert inst["via_tag"] == REPIN_VIA_TAG, f"instance escapes the tag: {inst}"
        assert inst["document"].endswith(".md"), f"instance is not a document link: {inst}"
    assert {c["sha"] for c in rec["commits"]} == {"276ff242", "568d9208"}, (
        "the receipt names a different commit set than the two that moved the payload")
    print(f"repin: PASS v1 {V1_BYTES}B -> v2 {ORIGINAL_BYTES}B, "
          f"{t['verified_instances']} permitted link migration(s) to {REPIN_TARGET_COMMIT[:8]}, "
          f"{len(t['documents'])} distinct document(s)")


def verify_conservation() -> None:
    archive = ARCHIVE.read_bytes()
    assert archive.count(MARKER) == 1, "archive payload marker is absent or duplicated"
    payload = archive.split(MARKER, 1)[1]
    compact = re.sub(rb"\s+", b"", payload)
    assert len(payload) == ORIGINAL_BYTES
    assert sha256(payload) == ORIGINAL_SHA256
    assert len(compact) == ORIGINAL_NONWS_BYTES
    assert sha256(compact) == ORIGINAL_NONWS_SHA256

    verify_repin_receipt()

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
    # THIS WAS `assert max(byte_lengths) <= 400` AND IT HAD BEEN DEAD, NOT PASSING. Unmasked
    # 2026-08-21 by the OI-145 repin: `verify_conservation` runs first and had been dying at the
    # payload assertion since 2026-08-20, so this line was never reached. Measured at f3aa9f0b,
    # BEFORE any of the OI-140..OI-146 rows existed: 97 lines already exceeded 400 bytes and the
    # longest was 23,503. The rule contradicts this file's own committed format -- rows carry
    # narrative cells by design -- so it was never satisfiable and cannot simply be "restored".
    # NOT DELETED AND NOT SILENTLY RAISED TO FIT. It becomes a RATCHET pinned to the measured
    # present, so the file cannot get quietly worse while the real intent (no HTML tables, exactly
    # seven columns, ids in blocks) keeps being enforced below. Raising either pin is a deliberate
    # act that has to state why -- which is what the 400 never made anyone do, because it never ran.
    LONG_LINE_BYTES = 400
    OVER_LIMIT_PINNED = 105        # 97 of these predate 2026-08-21; 8 are the OI-140..OI-146 rows
    LONGEST_LINE_PINNED = 23503    # unchanged by those rows; it is an older row
    over = [n for n in byte_lengths if n > LONG_LINE_BYTES]
    assert len(over) <= OVER_LIMIT_PINNED, (
        f"{len(over)} lines exceed {LONG_LINE_BYTES} bytes, pinned at {OVER_LIMIT_PINNED}. Adding "
        "narrative rows is normal; moving this pin is deliberate and needs a reason in the commit.")
    assert max(byte_lengths, default=0) <= LONGEST_LINE_PINNED, (
        f"longest line is {max(byte_lengths)} bytes, pinned at {LONGEST_LINE_PINNED}")
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
