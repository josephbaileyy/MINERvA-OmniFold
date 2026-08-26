#!/usr/bin/env python3
"""F-8(b) MECHANICAL LINTER. It can never pass. It can only say REVIEW REQUIRED, or refuse.

THE CLAUSE. `REVIEW-CONTRACT-20260822-k0-execution-integrity.md`, F-8, post-rehearsal column:
*"the receipt states the blind spots in the receipt's own words"*. F-8(a) is filed at
`RECEIPT-20260824-k0-f8a-f9-f12-f17a-filings.md` §1.6.

WHY THIS FILE HAS NO PASSING EXIT STATUS, which is the whole design.

An earlier version returned rc=0 on mechanically acceptable prose. It was graded FIT as a prefilter
and then the independent §10.1 readiness review ruled that exact behaviour a FAIL-OPEN GATE, and it
was right. Two demonstrated defeats, both of which had returned rc=0:

    KEYWORD-STUFFING, one line, no content:
        # blind spots
        origin is none sys.modules child process .sh

    MORAL PASTE, F-8(a) §1.6 with the word "potato" interleaved to break every 200-char run.

The readiness review's reasoning, and the reason a label was not enough: *"a mechanical check that
outputs a green rc=0 creates a strong anchoring effect, degrading the likelihood that a subsequent
human or grader will perform the 'mandatory' prose judgment with sufficient skepticism… a label is
insufficient protection against the systemic risk of a future lane simply citing the rc=0 result as
proof of compliance."*

So the fix is not a better heuristic -- no word count, no keyword density, no different span
threshold, all explicitly ruled out. The fix is that **THERE IS NO GREEN TO CITE**. The best outcome
this file can produce is exit 10, REVIEW_REQUIRED, which no pipeline can mistake for success.

THE ACTUAL F-8(b) GATE IS ELSEWHERE: a separately recorded independent prose attestation, validated
by `verify_f8b_attestation.py`. That validator is the only thing in this pair that can return 0, and
it can do so only while bound to this linter's report digest and the receipt digest.

EXIT CODES. 0 IS UNREACHABLE BY CONSTRUCTION and a test asserts it.
    10  REVIEW_REQUIRED -- mechanically acceptable. NOT a pass. Prose attestation still required.
     2  CANNOT CHECK    -- an input could not be read. Never a pass.
     3  NO SECTION      -- no blind-spots section, or it is empty.
     4  INCOMPLETE      -- a blind spot is not addressed.
     5  TRANSCLUDED     -- the section shares a long verbatim run with F-8(a) §1.6.
Three distinct refusal codes because "absent", "incomplete" and "copied" are different defects and
collapsing them would hide which one fired.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys

REVIEW_REQUIRED_EXIT = 10
CANNOT_CHECK_EXIT = 2
NO_SECTION_EXIT = 3
INCOMPLETE_EXIT = 4
TRANSCLUDED_EXIT = 5

REPORT_SCHEMA = "f8b-linter-report/1"

# Derived, never a literal. OI-136: a hardcoded checkout root makes a tool read the wrong tree.
# This file lives at <repo>/docs/orchestration/, so parents[2] is the repo root.
_REPO = pathlib.Path(__file__).resolve().parents[2]

SOURCE_REL = "docs/orchestration/RECEIPT-20260824-k0-f8a-f9-f12-f17a-filings.md"

REQUIRED_BLIND_SPOTS = {
    "namespace-packages": [
        ("namespace",),
        ("spec.origin", "find_spec", "origin is none", "no origin"),
    ],
    "already-imported-modules": [
        ("sys.modules",),
        ("install(", "before the guard", "already imported", "pre-import", "preimport"),
    ],
    "further-subprocess": [
        ("subprocess", "child process", "child interpreter", "spawn"),
    ],
    "shell-route": [
        (".sh", "shell route", "b-5"),
    ],
}

TRANSCLUSION_SPAN = 200


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def extract_section(text: str, heading_contains: str) -> str | None:
    lines = text.split("\n")
    start = None
    level = 0
    for i, ln in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m and heading_contains.lower() in m.group(2).lower():
            start = i + 1
            level = len(m.group(1))
            break
    if start is None:
        return None
    out = []
    for ln in lines[start:]:
        m = re.match(r"^(#{1,6})\s+", ln)
        if m and len(m.group(1)) <= level:
            break
        out.append(ln)
    return "\n".join(out)


def longest_common_span(a: str, b: str, cap: int) -> int:
    if not a or not b:
        return 0
    best = 0
    n = len(a)
    for i in range(n):
        if n - i <= best:
            break
        j = best + 1
        while i + j <= n and a[i:i + j] in b:
            best = j
            if best >= cap:
                return best
            j += 1
    return best


def lint(receipt_text: str, source_text: str) -> tuple[int, list[str], dict]:
    """Return (exit_code, notes, report_fields). NEVER returns 0."""
    facts: dict = {"spots_addressed": [], "spots_unaddressed": [], "longest_shared_span": None}

    section = extract_section(receipt_text, "blind spot")
    if section is None or not section.strip():
        return NO_SECTION_EXIT, [
            "NO SECTION: no heading containing 'blind spot', or it is empty. An absent section is "
            "not an empty set of blind spots; it is an unwritten receipt."], facts

    norm_section = _norm(section)
    facts["section_sha256"] = sha256_text(section)

    for spot, groups in sorted(REQUIRED_BLIND_SPOTS.items()):
        if all(any(a in norm_section for a in alts) for alts in groups):
            facts["spots_addressed"].append(spot)
        else:
            facts["spots_unaddressed"].append(spot)
    if facts["spots_unaddressed"]:
        return INCOMPLETE_EXIT, [
            "INCOMPLETE: blind spot(s) not addressed: %s" % facts["spots_unaddressed"]], facts

    src_section = extract_section(source_text, "BLIND SPOTS")
    if src_section is None:
        return CANNOT_CHECK_EXIT, [
            "CANNOT CHECK: the F-8(a) source section could not be located in %s, so the "
            "transclusion arm cannot run. A check that cannot run is never a pass." % SOURCE_REL], facts

    span = longest_common_span(norm_section, _norm(src_section), TRANSCLUSION_SPAN)
    facts["longest_shared_span"] = span
    if span >= TRANSCLUSION_SPAN:
        return TRANSCLUDED_EXIT, [
            "TRANSCLUDED: shares a verbatim run of >= %d characters with F-8(a) §1.6 (measured %d). "
            "All four spots being present does not satisfy 'in the receipt's own words' when the "
            "words are the source's." % (TRANSCLUSION_SPAN, span)], facts

    return REVIEW_REQUIRED_EXIT, [
        "all four blind spots addressed by concept",
        "longest verbatim span shared with F-8(a): %d chars (threshold %d)" % (span, TRANSCLUSION_SPAN),
    ], facts


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="F-8(b) mechanical linter. Never returns 0.")
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--source", default=str(_REPO / SOURCE_REL))
    ap.add_argument("--report", help="write the structured REVIEW_REQUIRED report here (JSON)")
    a = ap.parse_args(argv)

    receipt_path = pathlib.Path(a.receipt)
    try:
        receipt_text = receipt_path.read_text(encoding="utf-8", errors="replace")
        receipt_sha = sha256_file(receipt_path)
    except OSError as err:
        print("[f8b-lint] CANNOT CHECK: cannot read receipt %s: %s" % (a.receipt, err), file=sys.stderr)
        return CANNOT_CHECK_EXIT
    try:
        source_text = pathlib.Path(a.source).read_text(encoding="utf-8", errors="replace")
    except OSError as err:
        print("[f8b-lint] CANNOT CHECK: cannot read F-8(a) source %s: %s" % (a.source, err),
              file=sys.stderr)
        return CANNOT_CHECK_EXIT

    rc, notes, facts = lint(receipt_text, source_text)
    assert rc != 0, "the linter must never return 0"

    stream = sys.stderr if rc != REVIEW_REQUIRED_EXIT else sys.stdout
    for n in notes:
        print("[f8b-lint]   %s" % n, file=stream)

    if rc == REVIEW_REQUIRED_EXIT:
        report = {
            "schema": REPORT_SCHEMA,
            "status": "REVIEW_REQUIRED",
            "receipt_path": str(receipt_path),
            "receipt_sha256": receipt_sha,
            "linter_exit_code": rc,
            **facts,
            "this_is_not_a_pass": (
                "REVIEW_REQUIRED is NOT compliance with F-8(b) and NOT a pass. This linter has no "
                "passing exit status by construction, because a green result was ruled a fail-open "
                "gate by the independent 10.1 readiness review. It is defeated by keyword-stuffing "
                "and by a paste broken under the span threshold, both demonstrated. F-8(b) is gated "
                "ONLY by a separately recorded independent prose attestation validated by "
                "verify_f8b_attestation.py, which must bind this report's digest and the receipt's."),
        }
        text = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if a.report:
            pathlib.Path(a.report).write_text(text, encoding="utf-8")
            print("[f8b-lint] wrote report %s (sha256 %s)"
                  % (a.report, sha256_text(text)), file=stream)
        else:
            print(text, file=stream)
        print("[f8b-lint] REVIEW REQUIRED (exit %d) -- NOT A PASS. An independent prose attestation "
              "is required and is the actual F-8(b) gate." % rc, file=stream)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
