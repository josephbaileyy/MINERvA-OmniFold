#!/usr/bin/env python3
"""G0's revision gate: authenticate pinned files against a NAMED REVISION, not a co-located literal.

BEN-301, and the measured instance is the reason this file exists. On 2026-08-16 the cluster checkout
held wrapper `ee269b09` and a pin literal reading `ee269b09`, so **G0 would have PASSED** -- while the
tree sat 663 commits behind and the run would have carried none of MOVE 2 (anneal attestation), MOVE 3
(the end-of-run recorder the run exists to carry) or MOVE 4. The general form:

    A DIGEST PIN AUTHENTICATES CONTENT AGAINST AN EXPECTATION STORED IN THE SAME TREE, SO IT IS BLIND
    TO THE TREE BEING STALE. BOTH SIDES GO STALE TOGETHER AND AGREE PERFECTLY.

The fix is an expectation the tree cannot supply about itself: the sha256 of `git show <REV>:<path>` for
a revision named from OUTSIDE the tree. Predeclared in
`docs/orchestration/PREDECLARATION-20260816-g0-revision-gate.md`.

    ff_revision_gate.py --repo REPO --rev <40-hex> --file <abs path> [--file ...]
                        [--literal <abs path>=<sha256>] ...

Exit 0 on pass, non-zero with a named reason otherwise. Read-only: runs `git` plumbing and hashes
files. Writes nothing, and never touches the index or working tree.

WHY A REQUIRED --rev WITH NO DEFAULT. A prose rule fails silently when unread; a value check fails
silently when nobody supplies the value; a required argument with no default cannot be silently omitted
-- omission is a refusal. The campaign already paid for the other shape: BEN-317's
`fold_forward_composed_with_annealed_arm` was True on EMPTY input, which is the whole reason it was
replaced by a guard that raises. A guard satisfiable by the absence of its own evidence IS the defect.
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys

LITERAL_SHA1 = re.compile(r"^[0-9a-f]{40}$")


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def git(repo, *args):
    """Run git plumbing, returning (rc, stdout_bytes). Never raises on a non-zero git."""
    p = subprocess.run(("git", "-C", repo) + args, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    return p.returncode, p.stdout


def refuse(msg):
    print(f"[ff-rev] REFUSED: {msg}", file=sys.stderr)
    return 2


def check(repo, rev, files, literals=None):
    """Return 0 if every file matches its blob at `rev` and the tree is AT `rev`."""
    literals = literals or {}

    # ---- 1. the vacuity guard, and it is the first thing a later reader will try to remove --------
    # `FF_EXPECT_REV=HEAD` would resolve to the STALE TREE'S OWN HEAD, every blob would match its own
    # working file, and the gate would pass on exactly the configuration it exists to refuse. That is
    # repair-9's defect verbatim -- "the token gate's staleness check was VACUOUS, not weak: a symbolic
    # code_rev passed it for every file, forever" -- and this is the same defect in a second gate six
    # days later. Mirrors p4_check_verifier_token.py's is_literal_commit_sha. DO NOT relax to accept
    # abbreviations: a 12-hex prefix is resolvable and therefore just as symbolic.
    if not rev:
        return refuse("--rev is empty. It is REQUIRED and has no default: a gate that passes when "
                      "nobody supplies its expectation is satisfiable by absence (BEN-301, BEN-317).")
    if not LITERAL_SHA1.match(rev):
        return refuse(f"--rev {rev!r} is not a literal 40-hex commit sha. Symbolic revisions (HEAD, "
                      f"main, @, HEAD~0), abbreviations and uppercase forms are refused, because a "
                      f"symbolic revision resolves against the stale tree itself and would pass for "
                      f"every file forever (repair-9's vacuous staleness check).")

    # ---- 2. it must be a commit that exists HERE -------------------------------------------------
    rc, _ = git(repo, "cat-file", "-e", rev + "^{commit}")
    if rc != 0:
        return refuse(f"--rev {rev} is well-formed but is not a commit in {repo}. A revision this "
                      f"tree has never seen cannot describe it.")

    # ---- 3. the tree must BE at that revision ----------------------------------------------------
    rc, out = git(repo, "rev-parse", "HEAD")
    if rc != 0:
        return refuse(f"cannot read HEAD of {repo}; this is not a usable git checkout.")
    head = out.decode().strip()
    if head != rev:
        return refuse(f"tree is at {head}, expected {rev}. THIS IS THE BEN-301 CASE: the pinned files "
                      f"may still match literals stored beside them and agree perfectly while the "
                      f"whole checkout is stale. Refusing rather than authenticating a stale tree "
                      f"against its own stale expectation.")

    # ---- 4. THE ACTUAL FIX: compare each file to its blob AT THE NAMED REVISION -------------------
    problems, report = [], []
    for f in files:
        af = os.path.abspath(f)
        if not os.path.isfile(af):
            problems.append(f"{af}: missing on disk")
            continue
        rel = os.path.relpath(af, os.path.abspath(repo))
        if rel.startswith(os.pardir):
            problems.append(f"{af}: outside {repo}, so no revision can describe it")
            continue
        rc, blob = git(repo, "show", f"{rev}:{rel}")
        if rc != 0:
            problems.append(f"{rel}: does not exist at {rev}")
            continue
        want = hashlib.sha256(blob).hexdigest()
        got = sha256_file(af)
        if got != want:
            problems.append(f"{rel}: working file {got[:16]} != blob at {rev[:12]} {want[:16]} "
                            f"(uncommitted drift, or the tree is not the revision it claims)")
            continue
        # The co-located literal is CROSS-CHECKED, never authoritative. If a literal was updated but
        # the revision does not contain that content -- or vice versa -- the two disagree and that is
        # a finding, not a formality.
        lit = literals.get(af)
        if lit is not None and lit != want:
            problems.append(f"{rel}: launcher literal {lit[:16]} disagrees with the blob at "
                            f"{rev[:12]} {want[:16]}. The REVISION is authoritative; the literal is "
                            f"stale or was edited without a commit.")
            continue
        report.append((want, rel))

    if problems:
        print("[ff-rev] REFUSED: pinned files do not match the named revision:", file=sys.stderr)
        for p in problems:
            print(f"[ff-rev]   {p}", file=sys.stderr)
        return 2

    print(f"[ff-rev] PASS  tree is AT {rev} and all {len(report)} pinned file(s) match their blob "
          f"at that revision (not a co-located literal)")
    for want, rel in sorted(report, key=lambda t: t[1]):
        print(f"[ff-rev]    {want}  {rel}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--rev", default=os.environ.get("FF_EXPECT_REV", ""))
    ap.add_argument("--file", action="append", default=[])
    ap.add_argument("--literal", action="append", default=[],
                    help="PATH=SHA256, cross-checked against the blob; never authoritative")
    a = ap.parse_args(argv)
    literals = {}
    for spec in a.literal:
        if "=" not in spec:
            return refuse(f"--literal {spec!r} is not PATH=SHA256")
        p, s = spec.rsplit("=", 1)
        literals[os.path.abspath(p)] = s
    if not a.file:
        return refuse("no --file given; a gate with nothing to check is not a gate")
    return check(a.repo, a.rev, a.file, literals)


if __name__ == "__main__":
    sys.exit(main())
