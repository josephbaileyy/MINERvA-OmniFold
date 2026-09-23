#!/usr/bin/env python3
"""Name the object a check measured: the HEAD sha and whether the tree it read was clean.

A green that cannot be mapped to a commit cannot be cited (KNOWN_ISSUES rows 60 and 64). Every
check that reads working-tree bytes should print the line this module formats beside its verdict,
so a reader of the verdict can tell "exit 0 at <sha>, clean" from "exit 0 on somebody's edits".

    python3 lib/tree_state.py [PATH] [--scope PATHSPEC]

This is the ONE implementation. Callers load it by FILE PATH with importlib (never via sys.path,
see OI-136) and never copy it; a standalone copy of a caller may vendor this file beside itself.

States, and what each licenses:
    clean    no tracked change and no nonignored untracked file inside the scope: the bytes read
             are HEAD's bytes, so the verdict is a statement about HEAD.
    dirty    at least one of the above: the verdict is about this working tree only.
    no-git   PATH is not inside a git work tree (e.g. a `git archive` export): no sha exists, so
             the verdict can be cited only against whatever identifies the export.
    unknown  git exists but a query failed; treat exactly like dirty.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "--no-optional-locks", "-C", str(cwd), *args],
                          capture_output=True, text=True)


def describe(path: str | os.PathLike, scope: str | None = None) -> dict:
    """Return ``{"head", "tree", "tracked_changes", "untracked", "scope", "toplevel"}``.

    ``scope`` is a pathspec relative to the repository top level; ``None`` means the whole tree.
    Counts are ``None`` whenever ``tree`` is not ``clean``/``dirty``.
    """
    cwd = Path(path)
    if cwd.is_file():
        cwd = cwd.parent
    state = {"head": None, "tree": "no-git", "tracked_changes": None, "untracked": None,
             "scope": scope or ".", "toplevel": None}
    try:
        top = _git(cwd, "rev-parse", "--show-toplevel")
    except OSError:
        return state
    if top.returncode != 0:
        return state
    toplevel = top.stdout.strip()
    state["toplevel"] = toplevel
    head = _git(cwd, "rev-parse", "--verify", "--quiet", "HEAD^{commit}")
    status = _git(Path(toplevel), "status", "--porcelain=v1", "--untracked-files=normal",
                  "--", scope or ".")
    if head.returncode != 0 or status.returncode != 0:
        state["tree"] = "unknown"
        state["head"] = head.stdout.strip() or None
        return state
    state["head"] = head.stdout.strip()
    rows = [line for line in status.stdout.splitlines() if line]
    state["untracked"] = sum(1 for line in rows if line.startswith("??"))
    state["tracked_changes"] = len(rows) - state["untracked"]
    state["tree"] = "clean" if not rows else "dirty"
    return state


def resolve_rev(path: str | os.PathLike, rev: str) -> str:
    """Full commit sha for ``rev`` in the repository containing ``path``; raises ValueError."""
    cwd = Path(path)
    if cwd.is_file():
        cwd = cwd.parent
    result = _git(cwd, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")
    if result.returncode != 0 or not result.stdout.strip():
        raise ValueError(f"cannot resolve {rev!r} to a commit")
    return result.stdout.strip()


def format_state(state: dict) -> str:
    """One line, stable field order, e.g. ``head=<sha> tree=clean scope=docs/orchestration``."""
    tree = state["tree"]
    if tree == "dirty":
        tree = f"dirty(tracked={state['tracked_changes']},untracked={state['untracked']})"
    return f"head={state['head'] or 'none'} tree={tree} scope={state['scope']}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--scope", default=None)
    args = ap.parse_args()
    print(format_state(describe(args.path, args.scope)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
