"""Guard the gate freezes: every receipt sha256 must still match the checkout.

Added 2026-07-28 after commit 2732304 silently voided six bindings -- both Gate-4
entry points, the Gate-2 canonical-runtime dataloader, and the Gate-3 launcher
test -- with the whole suite still green. The edits were behaviourally inert on
Perlmutter, so only the hashes changed and nothing caught it.

This test fails on any NEW mismatch. The four pre-existing drifts are allowed by
the verifier's KNOWN_PREEXISTING list; run it with --strict to see those too.
"""
import os
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
_LAUNCH_CODE_FLOOR = 2


def _launch_code_receipts():
    """(name, payload) for every LIVE launch-code-gate receipt in state/."""
    import glob
    import json
    out = []
    for p in sorted(glob.glob(os.path.join(_REPO, "docs", "orchestration", "state",
                                           "*launch-code-gate*.json"))):
        try:
            payload = json.load(open(p))
        except (json.JSONDecodeError, OSError):
            continue
        if payload.get("status") == "SUPERSEDED" or "files" not in payload:
            continue
        out.append((os.path.basename(p), payload))
    return out


@pytest.mark.skipif(not os.path.exists(_VERIFIER), reason="verifier not present")
def test_gate3_and_gate4_launch_code_freezes_specifically():
    """The launch-code gates are the ones a refactor is most likely to touch."""
    import hashlib
    receipts = _launch_code_receipts()
    assert len(receipts) >= _LAUNCH_CODE_FLOOR, (
        f"found only {len(receipts)} live launch-code-gate receipt(s), expected at least "
        f"{_LAUNCH_CODE_FLOOR}. Either a gate lost its receipt or every candidate was filtered out "
        f"as superseded -- a discoverer that matches nothing reports success. Found: "
        f"{[n for n, _ in receipts]}")
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
