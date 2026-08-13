#!/usr/bin/env python3
"""Answer, by measurement, whether the file that is about to EXECUTE is the committed one.

THE TRAP THIS EXISTS TO CATCH
-----------------------------
A commit lands in the repo and everybody believes the thing running on scratch changed. It did
not, because nothing copied it. This has now happened twice in one day on this campaign:

  * `OI-57` / `GATE5_CODE_ROOT` -- the `train_fullevent_replica.py:112` repair was committed to a
    tree that the executing array does not read, so an unrepaired driver nearly shipped.
  * The Gate-5 reconciler -- `reconcile_gate5_family.py` was extended on `main` while the copy at
    `/pscratch/sd/j/josephrb/gate5-reconcile-lanec/` still held the previous logic. A run against
    the stale copy would have produced a confidently-formatted artifact from superseded checks and
    nothing in its output would have said so.

Both have the same signature: **the repo and the executing copy are two different facts, and every
report conflates them.** A git sha in a receipt is evidence about the repo, not about what ran.

WHY A THIRD STATE IS THE WHOLE POINT
------------------------------------
The naive check is "is this file's content in the repo?" -- and it is exactly wrong, because a
STALE copy answers YES. The previous version of the reconciler was committed, is in the repo's
history, and hashes to a real blob. A boolean check passes on precisely the file you are trying to
catch. So this tool reports three states and never collapses them:

  CURRENT              content == the blob at `<expect_path>` in HEAD. The only good state.
  STALE_BUT_COMMITTED  content is a real blob somewhere in repo history, but NOT HEAD's. This is
                       the trap state. It is the one that looks fine in every other check.
  UNCOMMITTED          content is in no commit at all -- a local edit, or a hand-patched copy.

`STALE_BUT_COMMITTED` and `UNCOMMITTED` are both failures, and they are reported distinctly
because they have different repairs: re-deploy versus find out who edited scratch by hand.

There is a fourth, rarer state kept separate rather than folded into `UNCOMMITTED`:
`IN_ODB_UNREACHABLE` -- the blob exists in the object database (someone ran `git add` and never
committed) but no commit contains it. Reporting that as "committed" because `cat-file -e` succeeds
would be the same class of error this file is about, so `--find-object` over `--all` is what
decides reachability, not object existence.

USAGE
-----
    verify_executing_copy_is_committed.py --repo <git_tree> \
        --pair <executing_path>=<repo_relative_path> [--pair ...] [--json out.json]

Exit 0 only if EVERY pair is CURRENT. Exit 3 if any pair is stale, uncommitted or missing.
Exit 2 for a usage or repository error -- which is deliberately NOT 3, so "the tool could not
look" can never be misread as "the tool looked and found drift", or vice versa.

The repo argument may itself be a deployed copy; this tool compares a file against a tree and does
not assume the tree is authoritative. Point `--repo` at the tree you believe is the source of
truth, and note in your receipt which tree that was.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys

# The only good state; every other value is a failure and the caller must not treat them alike.
STATE_CURRENT = "CURRENT"
STATE_STALE = "STALE_BUT_COMMITTED"
STATE_UNCOMMITTED = "UNCOMMITTED"
STATE_IN_ODB_UNREACHABLE = "IN_ODB_UNREACHABLE"
STATE_MISSING = "MISSING"

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_DRIFT = 3


def blob_oid(data: bytes) -> str:
    """Git's blob object id for exactly these bytes.

    Computed here rather than shelled out to `git hash-object` on purpose: `hash-object` applies
    the target path's clean filters and `.gitattributes` text conversion, so it can return a
    different oid for the same bytes depending on where the file sits. This function is a pure
    function of the bytes, which is what a drift check needs.
    """
    header = b"blob %d\0" % len(data)
    return hashlib.sha1(header + data).hexdigest()


def _git(repo: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _is_git_repo(repo: str) -> bool:
    r = _git(repo, "rev-parse", "--git-dir")
    return r.returncode == 0


def head_blob_oid(repo: str, repo_relpath: str) -> str | None:
    """The oid git records for `repo_relpath` in HEAD, or None if HEAD has no such path."""
    r = _git(repo, "rev-parse", f"HEAD:{repo_relpath}")
    if r.returncode != 0:
        return None
    return r.stdout.strip() or None


def blob_in_odb(repo: str, oid: str) -> bool:
    return _git(repo, "cat-file", "-e", f"{oid}^{{blob}}").returncode == 0


def commits_whose_diff_touches_blob(repo: str, oid: str, limit: int = 5) -> list[str]:
    """Commits anywhere in the repo whose DIFF introduces or removes this exact blob.

    Precision matters in the name: `--find-object` searches diffs, not trees, so this returns the
    commit that ADDED the content and also the commit that later REPLACED it. Both are useful for
    saying which version is running, but neither is the claim "this commit's tree has it" -- a
    function called `commits_containing_blob` would be asserting more than the command measures,
    which is BEN-149's shape and worth avoiding in a tool written to catch that class.

    A non-empty result is still a sound reachability test for our purpose: if a commit's diff
    touches the blob, some commit's tree held it. Object existence is NOT reachability -- a
    `git add` with no commit puts a blob in the object database that no commit ever contained.
    """
    r = _git(repo, "log", "--all", "--oneline", "--no-abbrev-commit", f"--find-object={oid}")
    if r.returncode != 0:
        return []
    lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
    return lines[:limit]


def classify(repo: str, executing_path: str, repo_relpath: str) -> dict:
    """One pair's verdict, with every ingredient the verdict rests on.

    Per CONVENTION-receipt-ingredients: the operands ship with the verdict, so the reported state
    can be contradicted by the reported hashes rather than having to be taken on faith.
    """
    out = {
        "executing_path": executing_path,
        "repo_relpath": repo_relpath,
        "executing_blob_oid": None,
        "executing_sha256": None,
        "head_blob_oid": None,
        "state": None,
        "commits_whose_diff_touches_executing_content": [],
        "explanation": None,
    }

    if not os.path.isfile(executing_path):
        out["state"] = STATE_MISSING
        out["explanation"] = (
            "No file at the executing path. Nothing is running this, or it runs from somewhere "
            "other than where the report says it does."
        )
        return out

    with open(executing_path, "rb") as fh:
        data = fh.read()
    oid = blob_oid(data)
    out["executing_blob_oid"] = oid
    out["executing_sha256"] = hashlib.sha256(data).hexdigest()

    head_oid = head_blob_oid(repo, repo_relpath)
    out["head_blob_oid"] = head_oid

    if head_oid is not None and oid == head_oid:
        out["state"] = STATE_CURRENT
        out["explanation"] = "Executing bytes are HEAD's bytes for this path."
        return out

    commits = commits_whose_diff_touches_blob(repo, oid)
    out["commits_whose_diff_touches_executing_content"] = commits

    if commits:
        out["state"] = STATE_STALE
        out["explanation"] = (
            "Executing content IS committed, but it is not HEAD's content for this path. This is "
            "the trap state: a repo commit that never reached the executing copy. Re-deploy."
        )
        return out

    if blob_in_odb(repo, oid):
        out["state"] = STATE_IN_ODB_UNREACHABLE
        out["explanation"] = (
            "The blob is in the object database but no commit contains it -- typically a `git add` "
            "with no commit. Not committed; do not read object existence as provenance."
        )
        return out

    out["state"] = STATE_UNCOMMITTED
    out["explanation"] = (
        "Executing content appears in no commit in this repo. Either it was edited in place, or "
        "the source of truth is a different tree than the one given as --repo."
    )
    return out


def parse_pair(spec: str) -> tuple[str, str]:
    if "=" not in spec:
        raise ValueError(
            f"--pair needs <executing_path>=<repo_relative_path>, got {spec!r}"
        )
    left, right = spec.split("=", 1)
    if not left or not right:
        raise ValueError(f"--pair has an empty side: {spec!r}")
    return left, right


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True, help="git tree treated as the source of truth")
    ap.add_argument(
        "--pair",
        action="append",
        default=[],
        metavar="EXEC=REPOREL",
        help="executing file path = its path relative to --repo. Repeatable.",
    )
    ap.add_argument("--json", dest="json_out", default=None, help="write the full report here")
    args = ap.parse_args(argv)

    if not args.pair:
        print("verify: no --pair given; nothing to check", file=sys.stderr)
        return EXIT_USAGE

    if not _is_git_repo(args.repo):
        print(f"verify: --repo is not a git repository: {args.repo}", file=sys.stderr)
        return EXIT_USAGE

    try:
        pairs = [parse_pair(p) for p in args.pair]
    except ValueError as exc:
        print(f"verify: {exc}", file=sys.stderr)
        return EXIT_USAGE

    head = _git(args.repo, "rev-parse", "HEAD").stdout.strip()
    results = [classify(args.repo, ex, rel) for ex, rel in pairs]

    report = {
        "tool": "verify_executing_copy_is_committed.py",
        "repo": os.path.abspath(args.repo),
        "repo_head": head,
        "results": results,
        "n_checked": len(results),
        "n_current": sum(1 for r in results if r["state"] == STATE_CURRENT),
        "states": sorted({r["state"] for r in results}),
        "all_current": all(r["state"] == STATE_CURRENT for r in results),
    }

    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(report, fh, indent=2, sort_keys=True)
            fh.write("\n")

    for r in results:
        print(f"{r['state']:<20} {r['executing_path']}  ({r['repo_relpath']})")
        if r["state"] != STATE_CURRENT:
            print(f"  head={r['head_blob_oid']} executing={r['executing_blob_oid']}")
            print(f"  {r['explanation']}")

    print(
        f"\nrepo {report['repo']} @ {head}\n"
        f"{report['n_current']} of {report['n_checked']} CURRENT"
    )
    return EXIT_OK if report["all_current"] else EXIT_DRIFT


if __name__ == "__main__":
    sys.exit(main())
