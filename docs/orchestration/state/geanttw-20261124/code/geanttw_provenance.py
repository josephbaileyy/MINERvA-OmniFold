#!/usr/bin/env python3
"""The event-loop source's provenance (DECLARATION.md §2): the canonical tree, synced into B, against MP-1 S0's
src_base rows committed beside this file (S0-src_base.sha256). M alone does not pin the event-loop source: only 10 of
its 46 files are tracked, so the canonical tree is the source and this check is its pin.

    geanttw_provenance.py --manifest S0-src_base.sha256 --tree SYNCED_TREE --deploy DEPLOY \
                          [--rel MINERvA101/MINERvA-101-Cross-Section]

PASS (exit 0) requires all of:
  - the synced tree's files are exactly the manifest's paths: no file missing, no file extra;
  - every file's sha256 equals its manifest row;
  - every file tracked by the deploy (at M) under --rel equals its manifest row, byte for byte.
FAIL is exit 1, with every breach printed; unusable input (an unreadable or malformed manifest) is exit 2.
Runs under the login node's /usr/bin/python3 (3.6).
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys

ROW = re.compile(r"^([0-9a-f]{64})  (\S.*)$")


class Unusable(Exception):
    pass


def manifest(path):
    rows = {}
    for ln in open(path).read().splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        m = ROW.match(ln)
        if not m:
            raise Unusable("malformed manifest row: %r" % ln)
        if m.group(2) in rows:
            raise Unusable("duplicate manifest path: %r" % m.group(2))
        rows[m.group(2)] = m.group(1)
    if not rows:
        raise Unusable("the manifest has no rows")
    return rows


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_files(root):
    out = set()
    for d, _dirs, files in os.walk(root):
        for f in files:
            out.add(os.path.relpath(os.path.join(d, f), root))
    return out


def check(rows, tree, deploy, rel):
    problems = []
    have = tree_files(tree)
    for p in sorted(set(rows) - have):
        problems.append("missing from the synced tree: %s" % p)
    for p in sorted(have - set(rows)):
        problems.append("not in the manifest: %s" % p)
    for p in sorted(have & set(rows)):
        got = sha(os.path.join(tree, p))
        if got != rows[p]:
            problems.append("sha256 mismatch: %s (%s, manifest %s)" % (p, got, rows[p]))
    tracked = subprocess.check_output(["git", "-C", deploy, "ls-files", "--", rel]).decode().split("\n")
    for t in [t for t in tracked if t]:
        p = os.path.relpath(t, rel)
        if p not in rows:
            problems.append("tracked at M but not in the manifest: %s" % p)
        elif sha(os.path.join(deploy, t)) != rows[p]:
            problems.append("tracked at M but differs from the manifest: %s" % p)
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--deploy", required=True)
    ap.add_argument("--rel", default="MINERvA101/MINERvA-101-Cross-Section")
    a = ap.parse_args(argv)
    try:
        rows = manifest(a.manifest)
    except (Unusable, OSError) as e:
        print("UNUSABLE %s" % e)
        return 2
    problems = check(rows, a.tree, a.deploy, a.rel)
    for p in problems:
        print("PROVENANCE %s" % p)
    print("SOURCE_PROVENANCE %s: %d manifest rows, %d problem(s)" % ("FAIL" if problems else "PASS", len(rows),
                                                                    len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
