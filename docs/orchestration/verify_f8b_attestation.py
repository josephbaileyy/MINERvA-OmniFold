#!/usr/bin/env python3
"""F-8(b) GATE: validate a recorded INDEPENDENT PROSE ATTESTATION. The only thing here that can pass.

WHY THIS EXISTS. `verify_run_receipt_blind_spots.py` is a linter with no passing exit status. The
independent §10.1 readiness review ruled that a mechanical `rc=0` on prose is a FAIL-OPEN GATE --
*"a label is insufficient protection against the systemic risk of a future lane simply citing the
rc=0 result as proof of compliance"* -- and prescribed the shape used here: the linter emits a report
requiring review, and the gate is *"a recorded attestation from the independent prose grader"*.

WHAT THIS VALIDATES, AND WHAT IT EXPLICITLY DOES NOT.

    IT VALIDATES the recorded DECISION and its BINDINGS: that a named independent reviewer, who is
    not the receipt's author -- checked on BOTH role and conversation uuid, not on a prose
    assertion of independence -- recorded a concrete independence basis, gave a per-spot semantic
    finding in their own words for each of the four blind spots, addressed the copying and
    word-salad risk head on, and reached an unambiguous PASS -- and that the attestation is bound by
    digest to the EXACT receipt and the EXACT linter report, both recomputed here from disk.

    IT DOES NOT PROVE THE SEMANTIC TRUTH of that decision. No program can. A reviewer who writes
    four thoughtful-looking findings about a bad receipt produces a valid attestation of a wrong
    judgement. What this buys is that the judgement was MADE, by a NAMED party who is NOT the author,
    against THESE EXACT BYTES, and that it cannot be silently reused for different bytes later.
    That is the whole claim. The pass text says so.

EXIT CODES.
    0  PASS         -- a well-formed, digest-bound, independent, complete, unambiguous PASS.
    2  CANNOT CHECK -- an input could not be read or parsed. Never a pass.
    3  REJECTED     -- the attestation is missing a requirement, mis-bound, self-attested, stale,
                       incomplete per-spot, or does not end in PASS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys

PASS_EXIT = 0
CANNOT_CHECK_EXIT = 2
REJECTED_EXIT = 3

SCHEMA = "f8b-independent-prose-attestation/1"
REQUIRED_SPOTS = ("namespace-packages", "already-imported-modules",
                  "further-subprocess", "shell-route")

# A finding shorter than this is not a semantic judgement; it is a checkbox. This is NOT a quality
# heuristic on prose -- it only rejects an empty or one-word cell, which is a structural defect.
MIN_FINDING_CHARS = 80
MIN_INDEPENDENCE_CHARS = 40
MIN_COPYING_RISK_CHARS = 80

# Identity is STRUCTURED, not prose. Independence is established by two named parties with two
# distinct conversation uuids -- a fact this program can actually check -- and NOT by grading the
# sincerity of a free-text sentence. Prose heuristics were explicitly ruled out for F-8(b); the
# prose basis below carries an emptiness floor only, and the uuid comparison does the real work.
IDENTITY_FIELDS = ("role", "conversation_uuid")

_REPO = pathlib.Path(__file__).resolve().parents[2]


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def validate(att: dict, receipt_sha: str, report_sha: str) -> tuple[int, list[str]]:
    bad: list[str] = []

    if att.get("schema") != SCHEMA:
        return REJECTED_EXIT, ["schema is %r, expected %r" % (att.get("schema"), SCHEMA)]

    # ---- staleness / supersession -------------------------------------------------
    if att.get("superseded_by"):
        bad.append("attestation is SUPERSEDED by %r; a superseded attestation never passes"
                   % att["superseded_by"])
    if att.get("status") and _norm(str(att["status"])) in ("draft", "withdrawn", "retracted"):
        bad.append("attestation status is %r, which is not a filed decision" % att["status"])

    # ---- digest bindings ----------------------------------------------------------
    for key, actual, what in (("receipt_sha256", receipt_sha, "receipt"),
                              ("linter_report_sha256", report_sha, "linter report")):
        claimed = att.get(key)
        if not claimed:
            bad.append("no %s: the attestation is not bound to the %s it judged" % (key, what))
        elif claimed != actual:
            bad.append("%s MISMATCH for the %s: attestation says %s, the file on disk is %s. An "
                       "attestation bound to different bytes than the ones being gated is worthless"
                       % (key, what, str(claimed)[:16], actual[:16]))

    # ---- identity and independence -------------------------------------------------
    def _party(key):
        v = att.get(key)
        if not isinstance(v, dict):
            bad.append("%s is missing or not an object: it must carry %s"
                       % (key, list(IDENTITY_FIELDS)))
            return None
        out = {}
        for f in IDENTITY_FIELDS:
            val = (v.get(f) or "").strip() if isinstance(v.get(f), str) else ""
            if not val:
                bad.append("%s.%s is missing or empty: an unattributed party cannot be shown "
                           "independent of anyone" % (key, f))
            out[f] = val
        return out

    author = _party("receipt_author")
    reviewer = _party("independent_reviewer")
    if author and reviewer:
        for f, why in (("role", "the same lane cannot grade its own filing"),
                       ("conversation_uuid", "one conversation attesting to itself is not review")):
            if author[f] and reviewer[f] and _norm(author[f]) == _norm(reviewer[f]):
                bad.append("SELF-ATTESTATION on %s (%r): %s. F-8(b) requires an INDEPENDENT "
                           "judgement." % (f, reviewer[f], why))

    basis = (att.get("independence_basis") or "").strip()
    if len(basis) < MIN_INDEPENDENCE_CHARS:
        bad.append("independence_basis is absent or too thin (%d chars, need >= %d): the two "
                   "distinct uuids are checked above, but the reviewer must also state in words "
                   "what their independence consists of" % (len(basis), MIN_INDEPENDENCE_CHARS))

    # ---- per-spot semantic findings -------------------------------------------------
    findings = att.get("per_spot_findings")
    if not isinstance(findings, dict):
        bad.append("per_spot_findings is missing or not an object")
    else:
        seen_norm = {}
        for spot in REQUIRED_SPOTS:
            f = findings.get(spot)
            if not isinstance(f, str) or not f.strip():
                bad.append("per_spot_findings[%s] is missing or empty: every blind spot needs its "
                           "own semantic finding" % spot)
                continue
            if len(f.strip()) < MIN_FINDING_CHARS:
                bad.append("per_spot_findings[%s] is %d chars, below the %d-char structural floor: "
                           "that is a checkbox, not a finding" % (spot, len(f.strip()),
                                                                  MIN_FINDING_CHARS))
            key = _norm(f)
            if key in seen_norm:
                bad.append("per_spot_findings[%s] is identical to [%s]: one finding pasted across "
                           "spots is word-salad, not four judgements" % (spot, seen_norm[key]))
            seen_norm[key] = spot
        extra = [k for k in findings if k not in REQUIRED_SPOTS]
        if extra:
            bad.append("per_spot_findings has unknown spot key(s) %s; the four are fixed" % extra)

    # ---- the copying / word-salad risk must be addressed head on --------------------
    risk = (att.get("copying_and_word_salad_risk") or "").strip()
    if len(risk) < MIN_COPYING_RISK_CHARS:
        bad.append("copying_and_word_salad_risk is absent or too thin (%d chars, need >= %d). The "
                   "linter is DEFEATED by keyword-stuffing and by a paste broken under its span "
                   "threshold; the reviewer must say explicitly that the prose is neither"
                   % (len(risk), MIN_COPYING_RISK_CHARS))

    # ---- the verdict itself ---------------------------------------------------------
    verdict = _norm(str(att.get("verdict", "")))
    if verdict in ("cannot", "cannot check", "cannot_check"):
        bad.append("verdict is CANNOT CHECK: never a pass")
    elif verdict in ("fail", "unfit", "reject", "rejected"):
        bad.append("verdict is %r: the reviewer did not pass this receipt" % att.get("verdict"))
    elif verdict != "pass":
        bad.append("verdict is %r, which is not an unambiguous PASS" % att.get("verdict"))

    if bad:
        return REJECTED_EXIT, bad
    return PASS_EXIT, ["bound to receipt %s and linter report %s" % (receipt_sha[:16], report_sha[:16]),
                       "reviewer %r (%s) is not the author %r (%s)"
                       % (reviewer["role"], reviewer["conversation_uuid"][:8],
                          author["role"], author["conversation_uuid"][:8]),
                       "four per-spot findings present, distinct, above the structural floor",
                       "copying and word-salad risk addressed explicitly"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Validate an F-8(b) independent prose attestation.")
    ap.add_argument("--attestation", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--linter-report", required=True)
    a = ap.parse_args(argv)

    try:
        att = json.loads(pathlib.Path(a.attestation).read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        print("[f8b-att] CANNOT CHECK: cannot read/parse attestation %s: %s" % (a.attestation, err),
              file=sys.stderr)
        return CANNOT_CHECK_EXIT
    try:
        receipt_sha = sha256_file(pathlib.Path(a.receipt))
        report_sha = sha256_file(pathlib.Path(a.linter_report))
    except OSError as err:
        print("[f8b-att] CANNOT CHECK: cannot read a bound artifact: %s" % err, file=sys.stderr)
        return CANNOT_CHECK_EXIT

    rc, notes = validate(att, receipt_sha, report_sha)
    stream = sys.stdout if rc == PASS_EXIT else sys.stderr
    for n in notes:
        print("[f8b-att]   %s" % n, file=stream)
    if rc == PASS_EXIT:
        print("[f8b-att] PASS -- a digest-bound, independent, complete prose attestation is on "
              "record for these exact bytes.", file=stream)
        print("[f8b-att] THIS VALIDATES THE RECORDED DECISION AND ITS BINDINGS. It does NOT prove "
              "the decision is semantically correct -- no program can. A thoughtful-looking "
              "attestation of a bad receipt would validate here. What is established is that an "
              "independent named party judged THESE bytes and cannot silently reuse it for others.",
              file=stream)
    else:
        print("[f8b-att] REJECTED (%d problem(s))." % len(notes), file=stream)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
