#!/usr/bin/env python3
"""A-2(f): the source manifest of an execution tree, and the comparison that makes it a gate.

WHAT IT ANSWERS, AND WHAT IT DOES NOT.
`REVIEW-CONTRACT-20260822-k0-execution-integrity.md` A-2(f) requires, of `MNV_CODE_ROOT`: "a full
source manifest: sha256 of every tracked `*.py` and `*.sh`, sorted, plus one digest over that list;
re-verified after every leg; any difference aborts." This file writes that manifest and compares
against it. It answers *"are the bytes in this tree the bytes that were approved"*.

IT IS NOT `verify_executing_copy_is_committed.py` AND IT IS NOT THE OI-136 GUARD, and the three are
answering three different questions. The parity checker answers "is the file at this path the
COMMITTED one" -- against git, per named pair. This answers "has ANY source byte in the tree moved
since the run started" -- against a recorded snapshot, over the whole tree, including files nobody
thought to name. The guard answers "which files did the interpreter ACTUALLY LOAD". Run 4 printed
`5 of 5 CURRENT` honestly while the third answer was false, which is why none of them substitutes
for another.

WHY A SNAPSHOT AND NOT JUST GIT. A-2(b) already requires `git status --porcelain` to be empty, and
`--require-clean` checks it. But "clean" is a statement about tracked content at one instant; the
manifest is what makes the SECOND measurement, after the last leg, comparable to the first. A tree
that went dirty and back again between them is invisible to git and visible here only if a byte
differs -- so this is a necessary check, not a sufficient one, and the pairing with (g) write
protection is what closes it.

THE DIGEST IS OVER THE LISTING, NOT OVER A SET. `<sha256>  <relpath>\\n` per line, sorted by relpath,
sha256 of the concatenation. So a RENAME moves the digest even when every file's own digest is
unchanged -- deliberately, because a rename is exactly how a hijack arrives without a content diff.

EXIT CODES follow the two checkers this sits beside rather than inventing a third convention:
    0 -- measured, and (in --compare) identical
    2 -- COULD NOT LOOK (not a git tree, no manifest, unreadable file, tree not clean)
    3 -- MEASURED DIFFERENCE
2 is deliberately not 3, so "we could not check" can never be read as "we checked and it matched".
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys

OK_EXIT = 0
CANNOT_CHECK_EXIT = 2
DRIFT_EXIT = 3

#: Extensions the contract names. Deliberately not "every tracked file": the manifest exists to pin
#: what can EXECUTE or be IMPORTED, and widening it to data would make it move for reasons that are
#: not about code and train readers to re-baseline it.
SOURCE_SUFFIXES = (".py", ".sh")

SCHEMA = "mnv_source_manifest/1"


def _git(repo: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", repo, *args],
                          capture_output=True, text=True, check=False)


def is_git_tree(repo: str) -> bool:
    return _git(repo, "rev-parse", "--git-dir").returncode == 0


def tracked_sources(repo: str) -> list[str]:
    r = _git(repo, "ls-files", "-z")
    if r.returncode != 0:
        raise OSError(f"git ls-files failed in {repo}: {r.stderr.strip()}")
    rels = [p for p in r.stdout.split("\0") if p]
    return sorted(p for p in rels if p.endswith(SOURCE_SUFFIXES))


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build(repo: str) -> dict:
    """The manifest. Raises OSError if any tracked source cannot be read -- never silently skipped:
    an unreadable file is the interesting case, and dropping it would shrink the listing and move
    the digest in a way that looks like a legitimate change."""
    rels = tracked_sources(repo)
    files = {}
    for rel in rels:
        files[rel] = sha256_file(os.path.join(repo, rel))
    listing = "".join(f"{files[rel]}  {rel}\n" for rel in rels)
    head = _git(repo, "rev-parse", "HEAD").stdout.strip() or None
    porcelain = _git(repo, "status", "--porcelain").stdout
    dirty = [l for l in porcelain.splitlines() if l.strip()]
    return {
        "schema": SCHEMA,
        "built_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "repo": os.path.abspath(repo),
        "head": head,
        # A COUNT AND THE LINES, not a boolean: "how dirty" is the number a reader needs, and a
        # boolean would let 721 entries and 1 entry read identically.
        "dirty_count": len(dirty),
        "dirty": dirty[:50],
        "suffixes": list(SOURCE_SUFFIXES),
        "file_count": len(rels),
        "files": files,
        "listing_sha256": hashlib.sha256(listing.encode()).hexdigest(),
    }


def compare(recorded: dict, live: dict) -> dict:
    """Set difference in BOTH directions plus content drift. Identity, never a floor."""
    a, b = recorded.get("files", {}), live.get("files", {})
    removed = sorted(set(a) - set(b))
    added = sorted(set(b) - set(a))
    changed = sorted(p for p in (set(a) & set(b)) if a[p] != b[p])
    return {
        "identical": not (removed or added or changed),
        "removed": removed, "added": added, "changed": changed,
        "recorded_digest": recorded.get("listing_sha256"),
        "live_digest": live.get("listing_sha256"),
        "recorded_head": recorded.get("head"), "live_head": live.get("head"),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="mnv_source_manifest.py", description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True, help="the execution tree to measure")
    ap.add_argument("--write", help="write the manifest here (JSON)")
    ap.add_argument("--compare", help="compare the live tree against this recorded manifest")
    ap.add_argument("--require-clean", action="store_true",
                    help="A-2(b): refuse (exit 2) unless git status --porcelain emits zero lines")
    ap.add_argument("--label", default="", help="free text carried into the record")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    if not a.write and not a.compare:
        print("[srcman] COULD NOT LOOK: give --write and/or --compare; measuring nothing and "
              "exiting 0 is exactly the shape this file exists to prevent", file=sys.stderr)
        return CANNOT_CHECK_EXIT
    if not is_git_tree(a.repo):
        print(f"[srcman] COULD NOT LOOK: {a.repo} is not a git tree", file=sys.stderr)
        return CANNOT_CHECK_EXIT
    try:
        live = build(a.repo)
    except OSError as err:
        print(f"[srcman] COULD NOT LOOK: {err}", file=sys.stderr)
        return CANNOT_CHECK_EXIT
    live["label"] = a.label

    if live["file_count"] == 0:
        print("[srcman] COULD NOT LOOK: zero tracked .py/.sh found. A zero here is a broken "
              "search, never a clean tree.", file=sys.stderr)
        return CANNOT_CHECK_EXIT

    print(f"[srcman] {a.repo}: {live['file_count']} tracked source files, "
          f"listing sha256 {live['listing_sha256']}, HEAD {live['head']}, "
          f"dirty {live['dirty_count']}")

    if a.require_clean and live["dirty_count"] != 0:
        print(f"[srcman] REFUSING: --require-clean and git status --porcelain emitted "
              f"{live['dirty_count']} line(s). An execution tree that is not clean is not the tree "
              f"anyone approved. First few: {live['dirty'][:5]}", file=sys.stderr)
        return CANNOT_CHECK_EXIT

    rc = OK_EXIT
    if a.compare:
        try:
            with open(a.compare, encoding="utf-8") as fh:
                recorded = json.load(fh)
        except (OSError, ValueError) as err:
            print(f"[srcman] COULD NOT LOOK: cannot read recorded manifest {a.compare}: {err}",
                  file=sys.stderr)
            return CANNOT_CHECK_EXIT
        if recorded.get("schema") != SCHEMA:
            print(f"[srcman] COULD NOT LOOK: {a.compare} is not a {SCHEMA} record",
                  file=sys.stderr)
            return CANNOT_CHECK_EXIT
        d = compare(recorded, live)
        if d["identical"]:
            print(f"[srcman] SOURCE MANIFEST IDENTICAL ({live['file_count']} files, "
                  f"{live['listing_sha256']})")
        else:
            print("[srcman] SOURCE MANIFEST MOVED -- the tree that is executing is not the tree "
                  "that was approved.", file=sys.stderr)
            print(f"[srcman]   recorded {d['recorded_digest']} at HEAD {d['recorded_head']}",
                  file=sys.stderr)
            print(f"[srcman]   live     {d['live_digest']} at HEAD {d['live_head']}",
                  file=sys.stderr)
            for kind in ("removed", "added", "changed"):
                for p in d[kind][:25]:
                    print(f"[srcman]   {kind.upper():8s} {p}", file=sys.stderr)
            rc = DRIFT_EXIT
    if a.write:
        os.makedirs(os.path.dirname(os.path.abspath(a.write)) or ".", exist_ok=True)
        with open(a.write, "w", encoding="utf-8") as fh:
            json.dump(live, fh, indent=2, sort_keys=True)
        print(f"[srcman] wrote {a.write}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
