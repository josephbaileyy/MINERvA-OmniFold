#!/usr/bin/env python3
"""F-8(b): refuse a rehearsal run receipt that does not state P-5's blind spots in its own words.

THE CLAUSE. `REVIEW-CONTRACT-20260822-k0-execution-integrity.md`, F-8, post-rehearsal column, in
full: *"the receipt states the blind spots in the receipt's own words"*. F-8(a), the pre-submission
half, is already filed at `RECEIPT-20260824-k0-f8a-f9-f12-f17a-filings.md` §1.6, itself headed "P-5
-- THE BLIND SPOTS, IN MY OWN WORDS". So the far half is an AUTHORING act, and the prospective
mechanism this file provides is the fail-closed check that the authoring actually happened.

WHAT THIS CAN AND CANNOT DECIDE, stated here rather than left for a reader to over-infer, because a
green check that is read as more than it proves is the failure this repository keeps paying for.

  IT CAN decide three things mechanically:
    (a) a blind-spots section EXISTS in the receipt;
    (b) all FOUR blind spots recorded in F-8(a) are each addressed, by concept, not by wording;
    (c) the section is NOT A TRANSCLUSION -- it shares no long verbatim span with the F-8(a) source.

  IT CANNOT decide whether the words demonstrate UNDERSTANDING. "Own words" in the human sense is
  not machine-checkable, and this file does not pretend otherwise. A PASS here means "authored, not
  copied, and covering all four" -- it does NOT mean "F-8(b) is discharged". Discharge is a grader's
  judgement over the prose. The exit text says so on every pass.

WHY NON-TRANSCLUSION IS THE OPERATIVE TEST. The cheap way to fake this clause is to paste F-8(a)'s
section into the run receipt. That satisfies "the blind spots are stated" and defeats "in the
receipt's own words" completely, and it is the ONLY failure mode a machine can catch reliably. So
that is the one it catches, and the check says that is all it catches.

Exit codes follow the campaign's existing vocabulary:
    0  PASS         -- all four addressed, no transclusion. NOT a discharge of F-8(b).
    2  CANNOT CHECK -- a required input could not be read. Never a pass.
    3  VIOLATION    -- a blind spot is unaddressed, or the section is transcluded.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

OK_EXIT = 0
CANNOT_CHECK_EXIT = 2
VIOLATION_EXIT = 3

# Derived, never a literal: OI-136's finding is that a hardcoded checkout root makes a tool read the
# wrong tree. This file lives at <repo>/docs/orchestration/, so parents[2] is the repo root.
_REPO = pathlib.Path(__file__).resolve().parents[2]

SOURCE_REL = "docs/orchestration/RECEIPT-20260824-k0-f8a-f9-f12-f17a-filings.md"
SOURCE_SECTION = "P-5 — THE BLIND SPOTS, IN MY OWN WORDS"

# A blind spot is matched by CONCEPT, never by a sentence, so a genuine paraphrase passes and a
# reworded copy still has to say the same thing. Each entry needs EVERY group to hit, and a group is
# satisfied by ANY of its alternatives.
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

# A shared verbatim run of this many characters is transclusion, not paraphrase. Chosen well above
# any phrase the two documents would share by necessity (clause names, "blind spot", "sys.modules")
# and well below the length of the shortest real paragraph.
TRANSCLUSION_SPAN = 200


def _norm(text: str) -> str:
    """Collapse whitespace and case so reflowing or re-indenting a paste is still a paste."""
    return re.sub(r"\s+", " ", text).strip().lower()


def extract_section(text: str, heading_contains: str) -> str | None:
    """Return the body under the first heading containing `heading_contains`, else None."""
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
    """Length of the longest common substring, stopped once it reaches `cap`.

    Rolling comparison over `a`'s windows. Returns as soon as `cap` is met, so the cost is bounded
    when a transclusion is present -- the case where the answer already decides the verdict.
    """
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


def check(receipt_text: str, source_text: str) -> tuple[int, list[str]]:
    notes: list[str] = []

    section = extract_section(receipt_text, "blind spot")
    if section is None or not section.strip():
        return VIOLATION_EXIT, [
            "no blind-spots section: the receipt has no heading containing 'blind spot', or it is "
            "empty. F-8(b) requires the receipt to STATE them; an absent section is not an empty "
            "set of blind spots, it is an unwritten receipt."]

    norm_section = _norm(section)

    missing = []
    for spot, groups in sorted(REQUIRED_BLIND_SPOTS.items()):
        for alts in groups:
            if not any(a in norm_section for a in alts):
                missing.append((spot, alts))
                break
    if missing:
        for spot, alts in missing:
            notes.append("blind spot NOT ADDRESSED: %s -- the section says none of %s"
                         % (spot, list(alts)))
        return VIOLATION_EXIT, notes

    src_section = extract_section(source_text, "BLIND SPOTS")
    if src_section is None:
        return CANNOT_CHECK_EXIT, [
            "cannot locate the F-8(a) source section in %s, so the transclusion arm cannot run. A "
            "check that cannot run is never a pass." % SOURCE_REL]

    span = longest_common_span(norm_section, _norm(src_section), TRANSCLUSION_SPAN)
    if span >= TRANSCLUSION_SPAN:
        return VIOLATION_EXIT, [
            "TRANSCLUDED: the receipt's blind-spots section shares a verbatim run of >= %d "
            "characters with F-8(a) §1.6. All four spots being present does not satisfy 'in the "
            "receipt's own words' when the words are the source's. Longest shared span: %d chars."
            % (TRANSCLUSION_SPAN, span)]

    notes.append("all four blind spots addressed by concept")
    notes.append("longest verbatim span shared with F-8(a): %d chars (threshold %d)"
                 % (span, TRANSCLUSION_SPAN))
    return OK_EXIT, notes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--receipt", required=True, help="the rehearsal run receipt to check")
    ap.add_argument("--source", default=str(_REPO / SOURCE_REL),
                    help="the F-8(a) filing whose §1.6 the receipt must not transclude")
    a = ap.parse_args(argv)

    try:
        receipt_text = pathlib.Path(a.receipt).read_text(encoding="utf-8", errors="replace")
    except OSError as err:
        print("[f8b] CANNOT CHECK: cannot read the receipt %s: %s" % (a.receipt, err),
              file=sys.stderr)
        return CANNOT_CHECK_EXIT
    try:
        source_text = pathlib.Path(a.source).read_text(encoding="utf-8", errors="replace")
    except OSError as err:
        print("[f8b] CANNOT CHECK: cannot read the F-8(a) source %s: %s" % (a.source, err),
              file=sys.stderr)
        return CANNOT_CHECK_EXIT

    rc, notes = check(receipt_text, source_text)
    stream = sys.stdout if rc == OK_EXIT else sys.stderr
    for n in notes:
        print("[f8b]   %s" % n, file=stream)
    if rc == OK_EXIT:
        print("[f8b] PASS -- the receipt states all four blind spots and does not transclude "
              "F-8(a).", file=stream)
        print("[f8b] THIS IS NOT A DISCHARGE OF F-8(b). It establishes that the section was "
              "authored, covers all four, and is not a paste. Whether the words demonstrate "
              "understanding is a GRADER's judgement over the prose and is not machine-checkable.",
              file=stream)
    elif rc == VIOLATION_EXIT:
        print("[f8b] VIOLATION -- the receipt does not satisfy F-8(b)'s stated form.", file=stream)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
