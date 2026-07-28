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


@pytest.mark.skipif(not os.path.exists(_VERIFIER), reason="verifier not present")
def test_gate3_and_gate4_launch_code_freezes_specifically():
    """The launch-code gates are the ones a refactor is most likely to touch."""
    import hashlib
    import json
    for receipt in ("p3f-pet-gate3-launch-code-gate-20260720.json",
                    "p3f-pet-gate4-launch-code-gate-20260721.json"):
        p = os.path.join(_REPO, "docs", "orchestration", "state", receipt)
        if not os.path.exists(p):
            pytest.skip(f"{receipt} absent")
        for role, info in json.load(open(p))["files"].items():
            if not isinstance(info, dict) or "path" not in info:
                continue
            fp = os.path.join(_REPO, info["path"])
            assert os.path.exists(fp), f"{receipt}:{role} missing {info['path']}"
            got = hashlib.sha256(open(fp, "rb").read()).hexdigest()
            assert got == info["sha256"], (
                f"{receipt}:{role} {info['path']} drifted\n"
                f"  frozen {info['sha256']}\n  now    {got}")
