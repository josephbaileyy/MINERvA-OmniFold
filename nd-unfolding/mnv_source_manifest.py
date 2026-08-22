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
import pathlib
import stat
import subprocess
import sys

# ONE DEFINITION OF "CHECKOUT", IMPORTED RATHER THAN RESTATED. A-2(c), (d) and (e) all turn on the
# same marker pair the OI-136 guard uses, and a second copy of that pair here would drift silently
# the first time either moved -- which is exactly how `AGENTS.md` became the wrong marker. This file
# is a preflight tool run by absolute path, so its own directory is sys.path[0]; the import resolves
# beside it, and it is deliberately NOT routed through the guard (see the launchers' preamble for
# the trust-order reason). `tests/test_source_manifest_constitution.py` asserts the two agree.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mnv_guarded_run import MARKERS, is_checkout  # noqa: E402

OK_EXIT = 0
CANNOT_CHECK_EXIT = 2
DRIFT_EXIT = 3

#: Extensions the contract names. Deliberately not "every tracked file": the manifest exists to pin
#: what can EXECUTE or be IMPORTED, and widening it to data would make it move for reasons that are
#: not about code and train readers to re-baseline it.
SOURCE_SUFFIXES = (".py", ".sh")

SCHEMA = "mnv_source_manifest/1"

#: Directories never descended into when hunting for a NESTED checkout (A-2(d)). `.git` holds no
#: checkout and walking it on a real tree is pure cost; the rest are the transient-worktree and
#: cache names the OI-136 probe already excludes for the same reason -- and `.claude/worktrees/` is
#: the named instance: a peer's live audit worktree made the OI-136 ratchet read 369 instead of 58.
#: NOTE THE ASYMMETRY, IT IS DELIBERATE: they are skipped from the SEARCH, not forgiven. A nested
#: checkout under `.claude/worktrees/` inside a code root is still a defect -- it is just one that
#: must not exist there at all, which `--require-no-nested-checkout` reports separately below.
PRUNE_DIRS = (".git", "__pycache__")



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
        # A-2(c)(d)(e)(g), MEASURED ON EVERY BUILD and recorded whether or not the matching
        # `--require-*` flag was passed. Recording unconditionally is the same rule P-3 applies to
        # `repo_origin_count`: an absent key cannot distinguish "there was no nested checkout" from
        # "nobody looked", and this record is read later by people who did not run the command.
        "constitution": {
            "is_checkout": is_checkout(pathlib.Path(os.path.abspath(repo))),
            "markers": list(MARKERS),
            "nested_checkouts": nested_checkouts(repo),
            "enclosing_checkout": enclosing_checkout(repo),
            **writable_sources(repo, rels),
        },
    }


def nested_checkouts(repo: str) -> list[str]:
    """A-2(d): every checkout STRICTLY BENEATH `repo`. Empty is the passing answer.

    WHY IT MATTERS AND WHY IT IS NOT PEDANTRY. `mnv_guarded_run.checkout_root_of` returns the
    INNERMOST matching ancestor -- deliberately, so a frozen deployment inside another directory
    resolves to itself rather than to whatever sits above it. Turn that around and a checkout nested
    INSIDE the code root resolves to ITSELF, which is not `--expect-root`, so every module under it
    is refused: the guard fails closed on a tree the operator believes is approved. The named
    instance is in the contract's own A-2: a peer's live `.claude/worktrees/` audit checkout made the
    OI-136 ratchet read 369 instead of the recorded 58.

    `.git` and `__pycache__` are pruned because neither can contain a checkout and walking them on a
    real tree is pure cost. NOTHING ELSE IS PRUNED -- in particular `.claude/worktrees/` is walked,
    because a nested checkout there is the defect rather than an exemption from it.
    """
    root = os.path.abspath(repo)
    found = []
    for dirpath, dirnames, _files in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in PRUNE_DIRS]
        if os.path.abspath(dirpath) == root:
            continue
        if is_checkout(pathlib.Path(dirpath)):
            found.append(os.path.relpath(dirpath, root))
            # Do not descend into a checkout we have already refused: one report per nest.
            dirnames[:] = []
    return sorted(found)


def enclosing_checkout(repo: str) -> str | None:
    """A-2(e): the nearest ANCESTOR of `repo` that is itself a checkout, or None.

    The same hazard from the other side, and it is not symmetrical in its consequence. Nested-inside
    means `checkout_root_of` on a module under the code root can resolve to the OUTER tree when the
    code root itself stops looking like one -- and more practically, it means the "immutable" tree is
    a subdirectory of something a peer can rewrite. `None` is the passing answer.
    """
    cur = pathlib.Path(os.path.abspath(repo)).parent
    while True:
        if is_checkout(cur):
            return str(cur)
        if cur.parent == cur:
            return None
        cur = cur.parent


def writable_sources(repo: str, rels: list[str]) -> dict:
    """A-2(g). Returns both definitions of "writable", because they are not the same question.

    WHICH ONE IS ENFORCED, AND WHY -- stated here rather than left to the reader:

      * `mode_writable` -- any of the three write bits set (`mode & 0o222`) on a tracked source file
        or on its containing directory. THIS IS THE ENFORCED ONE. It is what `chmod -R a-w over the
        source` produces, which is the contract's own wording, and it is a property of the TREE.
      * `uid_writable` -- `os.access(path, os.W_OK)` for the process running this check. REPORTED,
        NOT ENFORCED. It answers "could I write it", which is a property of WHO IS ASKING: it is
        false for a peer's tree the operator cannot touch (and that tree is not protected at all),
        and it is true for root regardless of any mode bit.

    Enforcing the uid form alone would pass a tree that any other account, or the same account after
    one `chmod`, can still rewrite mid-run -- and the hazard A-2(g) guards is mutation DURING the
    run, not mutation by this process.

    WHAT NEITHER FORM CAN DO, said plainly: the owner may `chmod` the bits back, and root ignores
    them. This prevents ACCIDENTAL mutation and makes deliberate mutation leave a trace in A-2(f);
    it is not a security boundary. Directories are included because write on a directory permits
    replacing a read-only file by unlink-and-create.
    """
    root = os.path.abspath(repo)
    mode_w, uid_w, dirs = [], [], set()
    for rel in rels:
        full = os.path.join(root, rel)
        dirs.add(os.path.dirname(full))
        try:
            m = os.stat(full).st_mode
        except OSError:
            continue
        if stat.S_IMODE(m) & 0o222:
            mode_w.append(rel)
        if os.access(full, os.W_OK):
            uid_w.append(rel)
    for d in sorted(dirs):
        if d == root:
            # The root directory itself is excluded: `.git` lives in it and git must stay able to
            # write there, so `chmod a-w` on the root would break the very tools that check it.
            continue
        try:
            if stat.S_IMODE(os.stat(d).st_mode) & 0o222:
                mode_w.append(os.path.relpath(d, root) + "/")
        except OSError:
            continue
    return {"mode_writable": sorted(mode_w), "uid_writable": sorted(uid_w)}


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
    ap.add_argument("--require-checkout", action="store_true",
                    help="A-2(c): refuse unless the tree carries BOTH guard markers, so the guard "
                         "would call it a checkout. Without this the guard exits 2 -- 'we could "
                         "not look' -- and a 2 read as clean is the whole OI-136 failure mode")
    ap.add_argument("--require-no-nested-checkout", action="store_true",
                    help="A-2(d): refuse if ANY checkout exists strictly beneath the code root. "
                         "checkout_root_of returns the INNERMOST match, so a nested checkout "
                         "resolves to itself, is not --expect-root, and every module under it is "
                         "refused on a tree the operator believes is approved")
    ap.add_argument("--require-not-nested", action="store_true",
                    help="A-2(e): refuse if the code root is itself inside another checkout")
    ap.add_argument("--require-readonly", action="store_true",
                    help="A-2(g): refuse if any tracked source file, or a directory containing "
                         "one, still carries a write bit. See writable_sources() for which of the "
                         "two definitions of 'writable' this enforces and why")
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

    # A-2(c)(d)(e)(g). EVERY CHECK RUNS BEFORE ANY RETURNS, so one command reports the whole set --
    # a reader who fixes the first refusal and re-runs should not discover a second one behind it.
    con = live["constitution"]
    refusals = []
    if a.require_checkout and not con["is_checkout"]:
        refusals.append(f"A-2(c): {a.repo} is not a checkout by the guard's own definition (needs "
                        f"{' and '.join(MARKERS)}). The guard would exit 2 on it, and 2 is 'we "
                        f"could not look', never 'we checked and it was clean'.")
    if a.require_no_nested_checkout and con["nested_checkouts"]:
        refusals.append(
            f"A-2(d): {len(con['nested_checkouts'])} checkout(s) exist BENEATH the code root: "
            f"{con['nested_checkouts'][:10]}. `checkout_root_of` returns the innermost match, so "
            f"every module under one of these resolves to IT rather than to --expect-root and is "
            f"refused -- on a tree you believe is approved. A peer's live `.claude/worktrees/` "
            f"audit checkout is the recorded instance: it made the OI-136 ratchet read 369 "
            f"instead of 58. Remove them from the code root; do not add an exclusion.")
    if a.require_not_nested and con["enclosing_checkout"]:
        refusals.append(
            f"A-2(e): the code root is nested inside the checkout {con['enclosing_checkout']}. An "
            f"'immutable' tree that is a subdirectory of another checkout is immutable only until "
            f"someone touches the outer one.")
    if a.require_readonly and con["mode_writable"]:
        refusals.append(
            f"A-2(g): {len(con['mode_writable'])} tracked source path(s) still carry a write bit, "
            f"e.g. {con['mode_writable'][:5]}. Apply write protection over the SOURCE (not `.git`, "
            f"which git must keep writing):\n"
            f"[srcman]     cd {a.repo} && git ls-files -z | xargs -0 chmod a-w\n"
            f"[srcman]     git ls-files -z | xargs -0 -n1 dirname | sort -zu | xargs -0 chmod a-w\n"
            f"[srcman]   To undo: the same two lines with `u+w`. "
            f"(For information only, NOT enforced: {len(con['uid_writable'])} of them are writable "
            f"by THIS uid. That is a fact about who is asking, not about the tree.)")
    if refusals:
        for r in refusals:
            print(f"[srcman] REFUSING: {r}", file=sys.stderr)
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
