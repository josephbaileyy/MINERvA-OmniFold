#!/usr/bin/env python3
"""Bind P4_VERIFIER_PASS to a real verifier verdict (closes KNOWN_ISSUES #21 / inventory A1).

The gate at `run_p4_standard.sh:41` tested only `[[ -z "${P4_VERIFIER_PASS}" ]]`, so ANY
non-empty string authorized covariance construction, and the refusal message named the variable
to set. It was demonstrated load-bearing on 2026-08-07: an autonomous run that self-authorized
would have written a candidate ROOT at stage 4 and died at stage 5, because stages 4-6 had never
executed and were broken three independent ways.

**The fix is deliberately not "check the variable harder."** An agent that can set an env var
can also write a JSON file, so a token bound to a file the agent could create is no gate at all.
The token must resolve to a verdict that is:

  1. a file whose sha256 EQUALS the token                     (the token is not a password,
                                                               it is the digest of the evidence)
  2. TRACKED in git and identical to its committed blob        (so it cannot be fabricated in the
                                                               working tree, and reviewing it is
                                                               reviewing what authorized the run)
  3. `verdict == "PASS"`                                       (BLOCK/absent authorizes nothing)
  4. `code_rev` equal to `git rev-parse HEAD`                  (a PASS on an older patch does not
                                                               authorize this one)

That still does not make forgery impossible -- someone can commit a fake verdict -- but it moves
the act from "set a variable nobody will ever see" to "commit a falsified receipt into the
ledger under your own name," which is the difference between an accident and a decision.

Usage:  p4_check_verifier_token.py --token <sha256>
Exit 0 and print the resolved receipt path, or print TOKEN-REJECT :: <reason> and exit 1.
"""
import argparse, glob, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4_lib as P

RECEIPT_DIR = os.path.join(P.REPO_ROOT, "docs", "orchestration", "runs", "standard-p4-verifier")


def _git(*args):
    return subprocess.check_output(["git", *args], cwd=P.REPO_ROOT, text=True,
                                   stderr=subprocess.DEVNULL).strip()


def resolve(token):
    if not token or not token.strip():
        raise P.P4GateError("empty token")
    token = token.strip().lower()
    if len(token) != 64 or any(c not in "0123456789abcdef" for c in token):
        raise P.P4GateError(
            f"token is not a sha256 ({len(token)} chars). The token must be the digest of a "
            f"committed standard-p4-verifier verdict, not a passphrase.")
    if not os.path.isdir(RECEIPT_DIR):
        raise P.P4GateError(f"no verifier receipt directory at {RECEIPT_DIR}")

    head = _git("rev-parse", "HEAD")
    matches = []
    for p in sorted(glob.glob(os.path.join(RECEIPT_DIR, "*.json"))):
        if P.sha256_file(p) == token:
            matches.append(p)
    if not matches:
        raise P.P4GateError(
            f"no verdict in {os.path.relpath(RECEIPT_DIR, P.REPO_ROOT)} has sha256 {token[:16]}… "
            f"-- the token must be the digest of an actual receipt")
    if len(matches) > 1:
        raise P.P4GateError(f"token matches {len(matches)} receipts; ambiguous")
    path = matches[0]
    rel = os.path.relpath(path, P.REPO_ROOT)

    # (2) tracked AND unmodified -- a receipt invented in the working tree must not authorize
    try:
        _git("ls-files", "--error-unmatch", rel)
    except Exception:
        raise P.P4GateError(f"{rel} is not tracked in git; an untracked verdict authorizes nothing")
    committed = _git("rev-parse", f"HEAD:{rel}")
    worktree = _git("hash-object", rel)
    if committed != worktree:
        raise P.P4GateError(
            f"{rel} differs from its committed blob (working {worktree[:12]} vs committed "
            f"{committed[:12]}); the authorizing verdict must be the reviewed one")

    v = json.load(open(path))
    # (3) verdict
    if str(v.get("verdict", "")).upper() != "PASS":
        raise P.P4GateError(
            f"{rel} records verdict={v.get('verdict')!r}, not PASS -- this authorizes nothing")
    # (4) code_rev pinned to HEAD
    cr = v.get("code_rev")
    if not cr:
        raise P.P4GateError(f"{rel} records no code_rev; cannot tell which patch it passed")
    if not head.startswith(str(cr)) and not str(cr).startswith(head[:len(str(cr))]):
        raise P.P4GateError(
            f"{rel} passed code_rev {cr}, but HEAD is {head[:12]}. A PASS on a different patch "
            f"does not authorize this one; re-run the verifier.")
    if v.get("authorizes_covariance_stages_4_6") is False:
        raise P.P4GateError(f"{rel} explicitly sets authorizes_covariance_stages_4_6=false")
    return rel, v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", required=True)
    a = ap.parse_args()
    try:
        rel, v = resolve(a.token)
    except P.P4GateError as e:
        print(f"TOKEN-REJECT :: {e}"); sys.exit(1)
    except Exception as e:
        print(f"TOKEN-REJECT :: unexpected {type(e).__name__}: {e}"); sys.exit(1)
    print(f"TOKEN-OK :: {rel} (verdict=PASS, code_rev={v.get('code_rev')})")
    sys.exit(0)


if __name__ == "__main__":
    main()
