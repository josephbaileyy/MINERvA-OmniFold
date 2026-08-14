"""Guard the gate freezes: every receipt sha256 must still match the checkout.

Added 2026-07-28 after commit 2732304 silently voided six bindings -- both Gate-4
entry points, the Gate-2 canonical-runtime dataloader, and the Gate-3 launcher
test -- with the whole suite still green. The edits were behaviourally inert on
Perlmutter, so only the hashes changed and nothing caught it.

This test fails on any NEW mismatch. The four pre-existing drifts are allowed by
the verifier's KNOWN_PREEXISTING list; run it with --strict to see those too.
"""
import os
import re
import subprocess
import sys

import pytest

_REPO = os.environ.get("MNV_REPO") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_VERIFIER = os.path.join(_REPO, "docs", "orchestration", "verify_hash_bindings.py")


@pytest.mark.skipif(not os.path.exists(_VERIFIER), reason="verifier not present")
def test_no_new_broken_hash_bindings():
    r = subprocess.run([sys.executable, _VERIFIER, "--root", _REPO],
                       capture_output=True, text=True)
    assert r.returncode == 0, (
        "A receipt sha256 binding no longer matches the file it froze. If the edit "
        "was intended, the owning gate must be deliberately re-run and its receipt "
        "re-issued -- do not just update the hash.\n\n" + r.stdout + r.stderr)


# Launch-code receipts are DISCOVERED, not named. Two reasons, both learned the hard way:
#
#  1. A hardcoded filename plus `pytest.skip(f"{receipt} absent")` is a vacuous pass waiting to
#     happen -- rename or re-date the receipt and the test goes green while checking nothing. The
#     2026-07-31 Gate-4 re-issue is exactly that rename (…-20260721.json -> …-20260731.json).
#  2. A superseded receipt must NOT be checked. Its hashes record what that gate ran against and are
#     preserved under `files_at_issue`; asserting them against the current tree would demand that a
#     re-issue never change any code, which is the opposite of what a re-issue is for.
#
# The floor is the same device as verify_hash_bindings.SHELL_PIN_FLOOR: a discoverer that silently
# matches nothing is the failure mode this file exists to catch. Raise it when a launch-code gate is
# added; lowering it needs the same justification as deleting a guard, because that is what it does.
#
# WAS `_LAUNCH_CODE_FLOOR = 2`, A SCALAR, REPLACED 2026-08-13 (OI-64(g), lane A, against its own commit).
# Two independent defects, and the second is why this is a semantics fix rather than a floor adjustment:
#
#  1. ZERO MARGIN, on a floor whose failure message could not name the real problem. Retiring
#     `…gate4-…20260812.json` that morning took the live count 3 -> 2, exactly the floor.
#     CORRECTION, and lane A's OI-64(g) overstated this: a re-issue-AND-retire does NOT trip it, because
#     the successor adds one live receipt as the predecessor drops one -- net zero, live stays 2. The real
#     trigger is narrower: a retirement with NO same-commit successor, which is the shape of retiring a
#     finished gate's receipt. At zero margin that trips a scalar floor whose message says "expected at
#     least 2" -- arbitrary, and its cheapest exit is lowering a guard this comment calls equivalent to
#     deleting one. The per-family form fails the same case with the message that is actually true:
#     "gate4's code freeze is checked by NOTHING." Same trigger, legible cause, no floor to lower.
#  2. THE SCALAR WAS STRICTLY WEAKER THAN ITS OWN STATED INTENT. "A discoverer that silently matches
#     nothing" is a per-family property: `>= 2` is satisfied by TWO Gate-4 receipts and ZERO Gate-3 ones,
#     which is exactly the blindness it exists to prevent. The test's own name says
#     `gate3_and_gate4`, and the scalar could not express the `and`.
#
# So families are DISCOVERED from every launch-code receipt on disk (live or superseded) and each one is
# required to have at least one LIVE receipt. That is self-maintaining -- a Gate-5 launch-code gate is
# covered the day its first receipt lands, with no constant to remember to raise -- and immune to the
# margin problem, because retiring a predecessor never takes a family's live count below the one its
# successor holds. `_LAUNCH_CODE_REQUIRED` is the residual floor against the whole directory vanishing or
# the filename grammar drifting, which discovery alone cannot catch.
_LAUNCH_CODE_REQUIRED = ("gate3", "gate4")
_LAUNCH_CODE_FAMILY = re.compile(r"-(gate\d+)-launch-code-gate-")


def _launch_code_receipts(live_only=True):
    """(name, payload) per launch-code-gate receipt in state/. live_only filters the retired ones.

    `live_only=False` is what makes family discovery possible: a family whose every receipt is
    superseded is invisible to the live set, and that is precisely the case the per-family assertion
    has to catch.
    """
    import glob
    import json
    out = []
    for p in sorted(glob.glob(os.path.join(_REPO, "docs", "orchestration", "state",
                                           "*launch-code-gate*.json"))):
        try:
            payload = json.load(open(p))
        except (json.JSONDecodeError, OSError):
            continue
        if live_only and (payload.get("status") == "SUPERSEDED" or "files" not in payload):
            continue
        out.append((os.path.basename(p), payload))
    return out


def _families(names):
    """{family: [name, ...]} off the FILENAME grammar. Unparseable names are returned under None."""
    out = {}
    for n in names:
        m = _LAUNCH_CODE_FAMILY.search(n)
        out.setdefault(m.group(1) if m else None, []).append(n)
    return out


@pytest.mark.skipif(not os.path.exists(_VERIFIER), reason="verifier not present")
def test_gate3_and_gate4_launch_code_freezes_specifically():
    """The launch-code gates are the ones a refactor is most likely to touch."""
    import hashlib
    receipts = _launch_code_receipts()
    all_fams = _families(n for n, _ in _launch_code_receipts(live_only=False))
    live_fams = _families(n for n, _ in receipts)

    # The filename grammar is the discoverer here, so a name it cannot parse is a blind spot rather
    # than a curiosity -- it would drop that family out of BOTH sets and cancel silently.
    assert None not in all_fams, (
        f"launch-code receipt name(s) do not match {_LAUNCH_CODE_FAMILY.pattern!r}, so their family "
        f"cannot be determined and they would be silently uncovered: {all_fams[None]}")

    # Residual floor: discovery alone cannot notice the whole directory vanishing.
    missing_required = [f for f in _LAUNCH_CODE_REQUIRED if f not in all_fams]
    assert not missing_required, (
        f"no launch-code receipt AT ALL for {missing_required} -- expected families "
        f"{list(_LAUNCH_CODE_REQUIRED)}. Either the directory moved or the naming changed; a "
        f"discoverer that matches nothing reports success. Found families: {sorted(all_fams)}")

    # The per-family assertion, which is what the scalar floor could not express.
    dead = {f: v for f, v in all_fams.items() if f not in live_fams}
    assert not dead, (
        f"every launch-code receipt for {sorted(dead)} is superseded or has no `files` block, so that "
        f"gate's code freeze is checked by NOTHING while the suite stays green. A re-issue must land "
        f"its successor in the same commit that retires its predecessor. Retired: "
        f"{ {f: v for f, v in dead.items()} }. Live: { {f: v for f, v in live_fams.items()} }")
    for receipt, payload in receipts:
        for role, info in payload["files"].items():
            if not isinstance(info, dict) or "path" not in info:
                continue
            fp = os.path.join(_REPO, info["path"])
            assert os.path.exists(fp), f"{receipt}:{role} missing {info['path']}"
            got = hashlib.sha256(open(fp, "rb").read()).hexdigest()
            assert got == info["sha256"], (
                f"{receipt}:{role} {info['path']} drifted\n"
                f"  frozen {info['sha256']}\n  now    {got}")


@pytest.mark.skipif(not os.path.exists(_VERIFIER), reason="verifier not present")
def test_superseded_receipts_hold_no_live_bindings():
    """A superseded receipt must not keep a live `files` block.

    If it does, the verifier stays red forever on a receipt that no longer owns those files, and the
    only ways out are hand-editing a hash (forbidden) or deleting the record (worse). The convention
    is to rename the block to `files_at_issue` and the inner key to `sha256_at_issue`, which is also
    what takes it out of verify_hash_bindings.collect(). Pin the convention so a future supersession
    cannot half-apply it."""
    import glob
    import json
    for p in sorted(glob.glob(os.path.join(_REPO, "docs", "orchestration", "state", "*.json"))):
        try:
            payload = json.load(open(p))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(payload, dict) or payload.get("status") != "SUPERSEDED":
            continue
        name = os.path.basename(p)
        assert "files" not in payload, (
            f"{name} is SUPERSEDED but still carries a live `files` block; rename it to "
            "`files_at_issue` (and `sha256` -> `sha256_at_issue`)")
        assert payload.get("superseded_by"), f"{name} is SUPERSEDED with no `superseded_by`"
        successor = os.path.join(_REPO, payload["superseded_by"])
        assert os.path.exists(successor), (
            f"{name} points at a successor that does not exist: {payload['superseded_by']}")
        for role, info in (payload.get("files_at_issue") or {}).items():
            assert "sha256" not in info, (
                f"{name}:{role} kept a live `sha256` key under files_at_issue; the verifier's "
                "collector harvests any dict with path+sha256, so this binding is still live")


@pytest.mark.skipif(not os.path.exists(_VERIFIER), reason="verifier not present")
def test_archived_gate2_receipts_hold_no_live_bindings():
    """The same convention, for ARCHIVED Gate-2 runtime receipts under gate2/final/superseded-*/.

    Learned the hard way on 2026-08-05. Archiving the 2026-07-19 and r1 receipts INTO the repo made
    the verifier red again immediately: it walks every receipt it finds, so an archived one goes on
    pinning the code hashes that were current when it was written. The live pins had just been closed
    by the re-issue, and the archives re-broke them.

    Gate-2 receipts use a `code` block rather than `files`, so the sibling test above does not reach
    them. Retiring it is the same move: `code` -> `code_at_issue`, `sha256` -> `sha256_at_issue`,
    every digest preserved verbatim.
    """
    import glob
    import json
    pattern = os.path.join(_REPO, "nd-unfolding", "g2_fullevent", "gate2", "final",
                           "superseded-*", "*RECEIPT*.json")
    found = sorted(glob.glob(pattern))
    assert found, "no archived Gate-2 receipts found; this test would pass vacuously"
    for p in found:
        name = os.path.relpath(p, _REPO)
        payload = json.load(open(p))
        assert payload.get("status") == "SUPERSEDED", (
            f"{name} sits in a superseded-* directory but its status is "
            f"{payload.get('status')!r}; an archived receipt that still claims PASS will be read as "
            f"a live one")
        assert "code" not in payload, (
            f"{name} still carries a live `code` block; rename it to `code_at_issue` (and each "
            f"inner `sha256` -> `sha256_at_issue`) or the verifier stays red on files this receipt "
            f"no longer owns")
        at_issue = payload.get("code_at_issue")
        assert at_issue, f"{name} has neither `code` nor `code_at_issue`"
        for role, info in at_issue.items():
            assert "sha256" not in info, (
                f"{name}:{role} kept a live `sha256` under code_at_issue; the collector harvests any "
                f"dict carrying path+sha256, so that binding is still live")
            assert info.get("sha256_at_issue"), f"{name}:{role} lost its at-issue digest"
        assert payload.get("superseded_by"), f"{name} is SUPERSEDED with no `superseded_by`"
        successor = os.path.join(_REPO, payload["superseded_by"])
        assert os.path.exists(successor), (
            f"{name} points at a successor that does not exist: {payload['superseded_by']}")


# --------------------------------------------------------------------------------------
# FINDINGS long-form index completeness.
#
# CLAUDE.md: "an unindexed finding is one nobody will read, which is how nine of them sat
# orphaned until 2026-08-06", and FINDINGS.md's own index header says "Every
# `FINDING-*.md` in this directory must appear here." That rule was violated again the
# same day it was written down -- FINDING-20260806-j28-reroll-exact.md was created and
# left out of the index -- so it is now checked rather than remembered.
#
# Lives here, in the collected suite, and NOT in docs/orchestration/test_*.py: per
# FINDING-20260802-orchestration-tests-never-run.md those files are never collected, so a
# guard placed there would itself be the antipattern it is meant to prevent.
_ORCH = os.path.join(_REPO, "docs", "orchestration")
_FINDINGS = os.path.join(_ORCH, "FINDINGS.md")


def _indexed_finding_files():
    """Backticked FINDING-*.md names from TABLE ROWS only.

    Prose in the header legitimately mentions the literal patterns `FINDING-*.md` and
    `FINDING-<YYYYMMDD>-<slug>.md`; scanning the whole file would read those as index
    entries pointing at nonexistent files.
    """
    import re
    out = set()
    for line in open(_FINDINGS, encoding="utf-8"):
        if not line.lstrip().startswith("|"):
            continue
        for name in re.findall(r"`(FINDING-\d{8}-[^`]+\.md)`", line):
            out.add(name)
    return out


def test_every_longform_finding_is_indexed():
    on_disk = {f for f in os.listdir(_ORCH)
               if f.startswith("FINDING-") and f.endswith(".md")}
    assert on_disk, "no FINDING-*.md files found -- wrong directory?"
    missing = sorted(on_disk - _indexed_finding_files())
    assert not missing, (
        "these long-form findings are not in the FINDINGS.md index and so are invisible "
        "to a new session: " + ", ".join(missing))


def test_the_index_has_no_dangling_rows():
    dangling = sorted(n for n in _indexed_finding_files()
                      if not os.path.isfile(os.path.join(_ORCH, n)))
    assert not dangling, (
        "the FINDINGS.md index points at files that do not exist (renamed or deleted "
        "without updating the index): " + ", ".join(dangling))
