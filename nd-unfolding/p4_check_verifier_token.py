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
  4a. `code_rev` is a LITERAL 40-hex sha AND an ANCESTOR       (the verdict came from this
      of HEAD                                                  history, not a foreign branch)
  4b. every file in scope is byte-identical between that       (a PASS cannot authorize code the
      commit and HEAD                                           verifier never saw)
  4c. every file in scope is byte-identical between that       (the chain executes the working
      commit and the WORKING TREE                                tree, not the commit)

Rule 4 was originally `code_rev == HEAD`, which broke on correct behaviour: any push by another
lane between the PASS and stages 4-6 invalidated a good verdict over commits touching nothing
reviewed. 4a+4b is strictly stronger -- it checks what the rule protects instead of a proxy that
unrelated commits perturb.

REPAIR-9 closes the two ways this rule was still vacuous or evadable (repair-8 verdict, defects
#5 and #4 -- they compound, so they are fixed together):

  * a SYMBOLIC `code_rev` made 4a and 4b vacuous, not merely weak. `merge-base --is-ancestor HEAD
    HEAD` succeeds, and 4b then compared HEAD against HEAD: zero differing files, for every file,
    forever. Measured True for 'HEAD', 'main', 'HEAD~0' and 'HEAD~3'. Only a literal sha names an
    immutable tree, so that is now required.
  * the declared `review_scope` was trusted VERBATIM, so the scope could be arbitrarily narrow --
    one unrelated file satisfied 4b trivially -- and the execution surface was never consulted at
    all when a scope was declared. Scope is now the UNION: the execution surface ALWAYS applies
    and a declared scope can only ADD to it. A verifier may review more than the chain executes;
    it may not authorize less.

Neither of these can be satisfied by reviewing less, which is the property that was missing.

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
    # REPAIR-9, verifier defect #5. `code_rev` must be a LITERAL 40-hex commit id. A symbolic
    # revision made this whole rule vacuous rather than merely weak: "HEAD" passes 4a because
    # `merge-base --is-ancestor HEAD HEAD` succeeds, and 4b then compares HEAD against HEAD and
    # finds zero differing files -- for every file, forever. Measured by repair-8:
    # code_rev_in_history was True for each of 'HEAD', 'main', 'HEAD~0', 'HEAD~3'.
    if not P.is_literal_commit_sha(cr):
        raise P.P4GateError(
            f"{rel} records code_rev={cr!r}, which is not a literal 40-hex commit sha. A symbolic "
            f"revision resolves against the tree it is checked against, so it would make rules 4a "
            f"and 4b compare HEAD with HEAD and pass for every file, forever. Stamp the resolved "
            f"`git rev-parse HEAD` of the reviewed tree.")
    if not P.code_rev_in_history(cr):
        raise P.P4GateError(
            f"{rel} passed code_rev {cr[:12]}, which is not an ancestor of HEAD ({head[:12]}). "
            f"That verdict did not come from this repository's history.")

    # REPAIR-9, verifier defect #4. The declared `review_scope` was trusted VERBATIM: any
    # non-empty list became the whole scope, the execution surface was never consulted, and no
    # minimum was enforced -- so a verdict declaring one unrelated file satisfied 4b trivially.
    # The scope is now a mandatory UNION: the execution surface ALWAYS applies, and a declared
    # scope can only ADD to it. A verifier may review more than the chain executes; it may not
    # authorize less.
    # The surface itself is derived from the IMPORT GRAPH plus the scripts the shell drivers
    # INVOKE (REPAIR-7 item 2 covered imports; repair-9 adds the shell leg, which is how
    # p3s_manifest_summary.py sat outside an 18-module surface).
    surface = P.standard_p4_execution_surface()
    if not surface:
        raise P.P4GateError(
            "could not derive the standard-P4 execution surface; refusing to authorize blind")
    scope = v.get("review_scope")
    declared = []
    if isinstance(scope, list) and scope:
        for x in scope:
            if not isinstance(x, str) or not x.strip():
                raise P.P4GateError(
                    f"{rel} declares a review_scope entry that is not a path ({x!r}); a scope the "
                    f"gate cannot read is not a scope")
            declared.append(x.strip())
    paths = sorted(set(surface) | set(declared))
    extra = sorted(set(declared) - set(surface))
    scope_src = ("UNION of the standard-P4 EXECUTION surface (%d tracked paths) and the verdict's "
                 "declared review_scope (%d declared, %d beyond the surface)"
                 % (len(surface), len(declared), len(extra)))
    ok, differing = P.paths_unchanged_between(cr, head, paths)
    if not ok:
        off = sorted(set(differing) - set(declared))
        raise P.P4GateError(
            f"{rel} reviewed {cr[:12]}, but {len(differing)} file(s) in its scope have CHANGED at "
            f"HEAD ({head[:12]}): {', '.join(differing[:4])}"
            f"{' ...' if len(differing) > 4 else ''}. {len(off)} of them are on the execution "
            f"surface but NOT in the declared review_scope. A PASS cannot authorize code the "
            f"verifier never saw; re-run the verifier.")
    # (4c) REPAIR-9, verifier defect #5 second half. 4b compares two COMMITS, so an UNCOMMITTED
    # edit to a reviewed file was invisible: rule (2) above compares the working tree against the
    # committed blob, but only for the verdict file itself. The chain executes the WORKING TREE.
    ok_wt, dirty = P.paths_unchanged_vs_worktree(cr, paths)
    if not ok_wt:
        raise P.P4GateError(
            f"{rel} reviewed {cr[:12]}, but {len(dirty)} file(s) in its scope differ from that "
            f"commit IN THE WORKING TREE: {', '.join(dirty[:4])}"
            f"{' ...' if len(dirty) > 4 else ''}. The chain runs the working tree, not the commit; "
            f"commit or revert the edit and re-run the verifier.")
    v["_resolved_review_scope"] = scope_src
    if v.get("authorizes_covariance_stages_4_6") is False:
        raise P.P4GateError(f"{rel} explicitly sets authorizes_covariance_stages_4_6=false")
    return rel, v


ENV_VAR = "P4_VERIFIER_PASS"


def require_verifier_token(stage):
    """Entry gate for a covariance stage, to be called FIRST in that stage's `main()`.

    REPAIR-12. Until now the hard gate lived only in `run_p4_standard.sh`, so `P4_VERIFIER_PASS`
    was a property of ONE CALL PATH rather than of covariance construction. The three stage
    modules are individually executable, and invoking them directly -- the only way to run stages
    4-6 without re-running 1-3, which is exactly what "run stages 4-6" asks for -- bypassed the
    token entirely. Lane B found that route by executing the instruction literally and declined to
    use it.

    That is KNOWN_ISSUES #21 one layer out. #21 was "any non-empty string opens the stages"; this
    was "not going through the wrapper opens the stages". The #21 repair strengthened the predicate
    and left it in the same single location, which is why the same class recurred against a
    stronger check.

    THIS RESOLVES, IT DOES NOT SNIFF. The check is `resolve()` -- the same function the wrapper
    calls -- so the token must be the sha256 of an actual verdict receipt that is git-TRACKED and
    byte-identical to its committed blob, whose verdict is PASS, whose `code_rev` is a literal
    ancestor sha, and whose scope is unchanged at HEAD in both the index and the working tree. An
    `os.environ.get(...)` truthiness test would re-open #21 here instead of there: an agent who can
    export a variable can also export a wrong one, and the whole point of the digest is that it
    cannot be invented without committing a falsified receipt under your own name.

    Deliberately raises rather than `sys.exit`s: the caller decides how to report, and a test can
    observe the refusal without a subprocess. Called before any ROOT import in every stage, so the
    gate is demonstrable on a machine that has no ROOT -- if it fired later, the one environment
    where these tests run could not exercise it.
    """
    tok = (os.environ.get(ENV_VAR) or "").strip()
    if not tok:
        raise P.P4GateError(
            f"{stage}: covariance construction requires {ENV_VAR} = the sha256 of a "
            f"standard-p4-verifier verdict with authorizes_covariance_stages_4_6=true. It is unset. "
            f"This module is gated on its own, not only through run_p4_standard.sh, so invoking it "
            f"directly does not skip the gate (repair-12).")
    rel, v = resolve(tok)
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
    # The scope is REPORTED, not merely enforced: `run_p4_standard.sh:99` echoes this line into the
    # run log, so an accepted token leaves behind what it was checked against. An authorization
    # that does not ship the scope it enforced is unfalsifiable -- see
    # docs/orchestration/CONVENTION-receipt-ingredients.md (BEN-077). It matters more now that the
    # scope is a union: "the gate accepted it" and "the gate checked 20 paths" are different claims.
    print(f"TOKEN-OK :: {rel} (verdict=PASS, code_rev={v.get('code_rev')}, "
          f"scope={v.get('_resolved_review_scope')})")
    sys.exit(0)


if __name__ == "__main__":
    main()
