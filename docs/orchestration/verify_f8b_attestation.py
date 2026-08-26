#!/usr/bin/env python3
"""F-8(b) CONFORMANCE CHECKER for a recorded INDEPENDENT PROSE ATTESTATION. IT CANNOT PASS EITHER.

THIS FILE IS NOT THE GATE. Nothing in the F-8(b) toolchain returns 0, including this. The gate is a
RECORDED AUTHORITY DECISION citing a well-formed attestation. The best outcome here is exit 11,
ATTESTATION_WELL_FORMED, which means "complete and correctly bound" and never "F-8(b) discharged".

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

THREE RESIDUAL HOLES, NAMED RATHER THAN PAPERED OVER. The independent implementation grade
(`agy-f8b-impl-grade`, `d71dbff7-9710-4bd9-94e3-a0dc3ac436f0`) returned UNFIT on an earlier version
and found each of these. Two are now closed; the third cannot be closed by this program and is
disclosed instead.

    CLOSED -- unknown top-level fields were IGNORED, so `verdict_hedging: "PASS but with some
    reservations"` could sit beside a clean `verdict: PASS`. The schema is now strict, top level and
    party objects both.

    CLOSED -- `conversation_uuid` was any non-empty string, so author `uuid-1234` and reviewer
    `uuid-123` read as two parties. Canonical uuid form is now required.

    OPEN, AND NOT CLOSEABLE HERE -- **nothing binds an attestation to the party it names.** There is
    no signature in this campaign. Anyone who can write the file can type any role and uuid into it,
    or take a real reviewer's attestation and retype the digests for a different receipt. This
    program checks that a distinct party is NAMED, never that they wrote it. Likewise, findings that
    differ by more than a trivial edit are accepted as four judgements whether or not they are;
    `_skeleton` catches the pasted duplicate, not a paraphrased one. **Both are process guarantees,
    not mechanical ones, and citing an exit 0 as if they were mechanical is the error this whole
    redesign exists to prevent.**

WHY IT HAS NO ZERO EXIT, which is a change from the version two reviews rejected.

An earlier version returned 0 on a well-formed attestation. Two independent reviews struck that down
on the same reasoning, and this lane agrees with both:

    `agy-f8b-impl-grade` (d71dbff7): *"Emitting rc=0 while explicitly relying on a printed label to
    disclaim mechanical verification is the same structural failure that was ruled insufficient."*

    `agy-readiness-rerun` (2fbd0b4f): *"The fail-open gate was MOVED... A fail-open surface that can
    be bypassed by spoofing identity is structurally identical to a fail-open surface that can be
    bypassed by spoofing prose."* Asked whether F-8(b) can be closed by machinery at all: **NO**.

The defence that failed was that the linter's green stood for a judgement that had NOT occurred while
this one stands for a judgement that HAS. That difference is real and it is not enough: it holds only
if the attestation is authentic, and **nothing here can establish authenticity** -- there is no
signature, so anyone who can write the file can type any role and uuid into it. The load-bearing
question in F-8(b) is whether a real independent party really read the prose. A machine cannot answer
it. So the machine does not get a green to answer it with.

EXIT CODES. 0 IS UNREACHABLE BY CONSTRUCTION and a test asserts it.
    11  ATTESTATION_WELL_FORMED -- complete and correctly bound. **NOT a discharge of F-8(b)**, and
                       not a finding that the judgement is honest or that the named reviewer wrote
                       it. Discharge is a recorded authority decision that cites this result.
     2  CANNOT CHECK -- an input could not be read or parsed.
     3  REJECTED     -- missing a requirement, mis-bound, self-attested, stale, incomplete per-spot,
                       or does not end in PASS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys

WELL_FORMED_EXIT = 11
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

# STRICT SCHEMA. An unknown top-level key is REJECTED, not ignored. The independent implementation
# grade broke an earlier version by adding `verdict_hedging: "PASS but with some reservations"`
# beside a clean `verdict: PASS` -- the validator read the clean field and ignored the contradiction
# sitting next to it. Any field this program does not check is a field an attestation can carry
# meaning in without the gate seeing it, so there are no such fields.
ALLOWED_TOP_LEVEL = frozenset((
    "schema", "verdict", "receipt_sha256", "linter_report_sha256", "receipt_author",
    "independent_reviewer", "independence_basis", "per_spot_findings",
    "copying_and_word_salad_risk", "status", "superseded_by"))

# A conversation uuid must BE a uuid. Same grade defeated the independence check with author
# `uuid-1234` and reviewer `uuid-123`: distinct strings, so not self-attestation, but not two
# conversations either. Requiring canonical form makes "distinct string" and "distinct conversation"
# the same fact, which is what the check was always assuming.
FILED_STATUS = "filed"

# Identity fields must be printable ASCII. `аuthor` (Cyrillic a) and `author` are two strings and
# one party; rejecting the character class is cheaper and more honest than trying to fold homoglyphs.
ASCII_RE = re.compile(r"^[\x20-\x7e]+$")

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)

_REPO = pathlib.Path(__file__).resolve().parents[2]


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def _skeleton(s: str) -> str:
    """Identity modulo trivial edits: letters only, lowercased.

    The independent grade defeated a plain equality check on the four findings by submitting the
    same 80-character run with a trailing `1` and a trailing `2`. Stripping digits, punctuation and
    spacing makes that one string again. This is NOT a similarity threshold -- there is no distance
    and no tunable number, only a normal form -- because a similarity threshold on prose is exactly
    what was ruled out for F-8(b). It catches the trivial edit and nothing beyond it; see the module
    docstring for what stays open.
    """
    return re.sub(r"[^a-z]", "", s.lower())


def _role_key(s: str) -> str:
    """Role identity modulo punctuation and case -- but NOT modulo digits.

    `_skeleton` strips digits, which is right for findings (`B*80+1` vs `B*80+2` is one finding) and
    WRONG for roles: measured, it collides `codex-school` with `codex-school2` -- two real profiles
    in this repo -- and `agy-g2-gate-verifier` with `agy-g3-gate-verifier`. That direction fails
    closed, so it would have refused honest attestations rather than passing dishonest ones, but it
    is still a false positive and a guard needs testing in both directions.
    """
    return re.sub(r"[^a-z0-9]", "", s.lower())


def validate(att: dict, receipt_sha: str, report_sha: str) -> tuple[int, list[str]]:
    bad: list[str] = []

    if att.get("schema") != SCHEMA:
        return REJECTED_EXIT, ["schema is %r, expected %r" % (att.get("schema"), SCHEMA)]

    unknown = sorted(set(att) - ALLOWED_TOP_LEVEL)
    if unknown:
        bad.append("unknown top-level field(s) %s. This schema is STRICT: a field the validator "
                   "does not check is a field an attestation can carry meaning in unseen -- a "
                   "hedge, a caveat, a second verdict -- while the field it does check stays "
                   "clean. Declare it or remove it." % unknown)

    # ---- staleness / supersession -------------------------------------------------
    if att.get("superseded_by"):
        bad.append("attestation is SUPERSEDED by %r; a superseded attestation never passes"
                   % att["superseded_by"])
    if "status" in att and _norm(str(att.get("status"))) != FILED_STATUS:
        bad.append("attestation status is %r; the only value that means a filed decision is %r. "
                   "This is an ALLOWLIST because the denylist it replaced waved through every "
                   "unfiled-sounding value nobody had thought of -- 'pending' passed."
                   % (att.get("status"), FILED_STATUS))
    if "superseded_by" in att and not (isinstance(att["superseded_by"], str)
                                       and att["superseded_by"].strip()):
        bad.append("superseded_by is present but %r: a falsy or non-string supersession field is "
                   "ambiguous rather than absent. Omit the key, or name the successor."
                   % (att["superseded_by"],))

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
            elif not ASCII_RE.match(val):
                bad.append("%s.%s %r contains non-ASCII characters. A Cyrillic homoglyph makes two "
                           "identical-looking roles compare as distinct parties, which is the whole "
                           "independence check defeated by one invisible byte." % (key, f, val))
            elif f == "conversation_uuid" and not UUID_RE.match(val):
                bad.append("%s.conversation_uuid %r is not a canonical uuid. Two arbitrary strings "
                           "can differ without being two conversations -- a prefix of a real uuid "
                           "would pass an equality test and name nobody." % (key, val))
            out[f] = val
        unknown = sorted(set(v) - set(IDENTITY_FIELDS))
        if unknown:
            bad.append("%s has unknown field(s) %s; the party schema is strict too" % (key, unknown))
        return out

    author = _party("receipt_author")
    reviewer = _party("independent_reviewer")
    if author and reviewer:
        for f, why in (("role", "the same lane cannot grade its own filing"),
                       ("conversation_uuid", "one conversation attesting to itself is not review")):
            # Roles compare on the letters-only normal form, so `close-out lane` and
            # `close out lane` are one party. Uuids are already canonical by the time we get here.
            same = _role_key if f == "role" else _norm
            if author[f] and reviewer[f] and same(author[f]) == same(reviewer[f]):
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
            key = _skeleton(f)
            if key and key in seen_norm:
                bad.append("per_spot_findings[%s] is the same text as [%s] once digits, punctuation "
                           "and spacing are removed: one finding pasted across spots is word-salad, "
                           "not four judgements" % (spot, seen_norm[key]))
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
    return WELL_FORMED_EXIT, ["bound to receipt %s and linter report %s" % (receipt_sha[:16], report_sha[:16]),
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
    assert rc != 0, "this checker must never return 0"

    stream = sys.stdout if rc == WELL_FORMED_EXIT else sys.stderr
    for n in notes:
        print("[f8b-att]   %s" % n, file=stream)
    if rc == WELL_FORMED_EXIT:
        print("[f8b-att] ATTESTATION_WELL_FORMED (exit %d) -- NOT A DISCHARGE OF F-8(b), and not a "
              "pass. The attestation is complete and bound to these exact bytes. That is all this "
              "establishes." % rc, file=stream)
        print("[f8b-att] IT DOES NOT PROVE THE JUDGEMENT IS CORRECT -- no program can -- AND IT DOES "
              "NOT PROVE THE NAMED REVIEWER WROTE IT. There is no signature: whoever can write the "
              "file can type any role and uuid into it. Two independent reviews ruled that a green "
              "exit beside a printed caveat is a fail-open gate, so there is no green here to cite.",
              file=stream)
        print("[f8b-att] F-8(b) IS DISCHARGED BY A RECORDED AUTHORITY DECISION that cites this "
              "result, never by this exit code.", file=stream)
    else:
        print("[f8b-att] REJECTED (%d problem(s))." % len(notes), file=stream)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
