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
  4a. `code_rev` is an ANCESTOR of HEAD                        (the verdict came from this
                                                               history, not a foreign branch)
  4b. every file the verdict REVIEWED is byte-identical        (a PASS cannot authorize code the
      between that commit and HEAD                              verifier never saw)

Rule 4 was originally `code_rev == HEAD`, which broke on correct behaviour: any push by another
lane between the PASS and stages 4-6 invalidated a good verdict over commits touching nothing
reviewed. 4a+4b is strictly stronger -- it checks what the rule protects instead of a proxy that
unrelated commits perturb. Scope comes from the verdict's `review_scope` if declared, else the
whole standard-P4 surface, which is the wider and safer default.

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
    # (4) REPAIR-6c. This required `code_rev == HEAD` and was wrong for the same reason the
    # receipt gate was: it breaks on CORRECT behaviour. Another lane pushing between the verifier
    # PASS and stages 4-6 -- which happened today, eight commits mid-run -- would reject a valid
    # verdict over commits touching nothing the verifier reviewed.
    #
    # Replaced by a pair that is STRICTLY STRONGER than equality, because it checks the thing the
    # rule protects rather than a proxy unrelated commits perturb:
    #   (4a) the reviewed commit must be an ANCESTOR of HEAD -- catches a verdict carried in from
    #        a foreign branch or a rewritten history;
    #   (4b) every file the verdict actually REVIEWED must be byte-identical between that commit
    #        and HEAD -- so a PASS cannot authorize code the verifier never saw.
    # The verdict may declare its own scope in `review_scope`; absent that, the fallback is every
    # tracked file on the standard-P4 surface, the wider and therefore safer assumption.
    cr = v.get("code_rev")
    if not cr:
        raise P.P4GateError(f"{rel} records no code_rev; cannot tell which patch it passed")
    cr = str(cr).strip()
    if not P.code_rev_in_history(cr):
        raise P.P4GateError(
            f"{rel} passed code_rev {cr[:12]}, which is not an ancestor of HEAD ({head[:12]}). "
            f"That verdict did not come from this repository's history.")

    scope = v.get("review_scope")
    if isinstance(scope, list) and scope:
        paths, scope_src = sorted(str(x) for x in scope), "declared review_scope"
    else:
        paths = P.tracked_files_matching(P.STANDARD_P4_SURFACE_GLOBS, rev=head)
        scope_src = "default standard-P4 surface (%d tracked files)" % len(paths)
    if not paths:
        raise P.P4GateError("could not resolve a review scope; refusing to authorize blind")
    ok, differing = P.paths_unchanged_between(cr, head, paths)
    if not ok:
        raise P.P4GateError(
            f"{rel} reviewed {cr[:12]}, but {len(differing)} file(s) it covered have CHANGED at "
            f"HEAD ({head[:12]}): {', '.join(differing[:4])}"
            f"{' ...' if len(differing) > 4 else ''}. A PASS cannot authorize code the verifier "
            f"never saw; re-run the verifier.")
    v["_resolved_review_scope"] = scope_src
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
