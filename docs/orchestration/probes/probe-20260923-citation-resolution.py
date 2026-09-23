#!/usr/bin/env python3
"""Rounds 61-62 of the review-residue loop, made re-runnable (review #15a finding 4).

    probe-20260923-citation-resolution.py [BASE [REV]]      (defaults 177af61b 75bdde7e)

Reads every file at REV via `git show`, not the working tree, so the result depends only on the two
revisions and on which objects this clone holds. The operands are the `.md` files changed between
BASE and REV.

  A  sha-like tokens (7-40 lower-hex, at least one letter and one digit) in the WHOLE of each file,
     counted by occurrence; the distinct ones that do not resolve as a COMMIT (`git cat-file -e
     <t>^{commit}`) are listed. Most are content digests, not commits.
  B  the same tokens restricted to lines ADDED between BASE and REV that resolve to NO object at all
     and whose surrounding 70/40 characters read like a commit citation.
  C  `module.symbol` / `path.py::symbol` code spans on added lines, where `module` is the basename of
     a tracked .py file, resolved as a def/class/assignment in that file. A miss whose symbol is
     `py`/`sh` is a file name that the pattern misreads as `module.symbol`, not a citation.

Always exits 0: it is a lister, and a human classifies what it prints. The result DEPENDS ON THE
CLONE: a token that sits in a remote this clone has not fetched counts as unresolved.
"""
import os
import re
import subprocess
import sys

BASE, REV = (sys.argv[1:] + ["177af61b", "75bdde7e"][len(sys.argv[1:]):])[:2]
SHA = re.compile(r"(?<![0-9a-fA-F/._-])([0-9a-f]{7,40})(?![0-9a-fA-F])")
CTX = re.compile(r"commit|\bsha\b|HEAD|\bat [0-9a-f]{7}|pushed|landed|\^|\.\.", re.I)


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True)


def shaish(s):
    return bool(re.search(r"[a-f]", s) and re.search(r"\d", s))


def resolves(obj):
    return git("cat-file", "-e", obj).returncode == 0


files = [f for f in git("diff", "--name-only", "-z", BASE, REV, "--", "*.md").stdout.split("\0") if f]
occ, unres = 0, set()
for f in files:
    r = git("show", f"{REV}:{f}")
    if r.returncode:
        continue                          # deleted at REV
    for m in SHA.finditer(r.stdout):
        if shaish(m.group(1)):
            occ += 1
            if not resolves(m.group(1) + "^{commit}"):
                unres.add(m.group(1))
print(f"A  {BASE}..{REV}: {len(files)} .md file(s), {occ} sha-like occurrence(s), "
      f"{len(unres)} distinct not resolving as a commit in this clone")

added, cur = [], None
for L in git("diff", "-U0", BASE, REV, "--", "*.md").stdout.splitlines():
    if L.startswith("+++ "):
        cur = L[6:]
    elif L.startswith("+"):
        added.append((cur, L))
hits = []
for f, L in added:
    for m in SHA.finditer(L):
        s = m.group(1)
        if shaish(s) and not resolves(s):
            ctx = L[max(0, m.start() - 70):m.end() + 40]
            if CTX.search(ctx):
                hits.append((f, s, ctx))
print(f"B  {len(hits)} token(s) on added lines resolving to NO object, in commit-like context")
for h in hits:
    print("   ", h[0], "|", h[1], "|", h[2])

py = [p for p in git("ls-files", "-z", "--", "*.py").stdout.split("\0") if p]
bymod = {}
for p in py:
    bymod.setdefault(os.path.basename(p)[:-3], []).append(p)
seen, ok, miss = set(), 0, []
for f, L in added:
    for m in re.finditer(r"`([\w/.-]+\.py)::(\w+)`|`([A-Za-z_]\w*)\.([A-Za-z_]\w*)(?:\(\))?`", L):
        if m.group(1):
            cand, sym, key = [p for p in py if p == m.group(1) or p.endswith("/" + m.group(1))], m.group(2), m.group(0)
        else:
            cand, sym, key = bymod.get(m.group(3), []), m.group(4), m.group(0)
            if not cand:
                continue                  # not a module of this repo
        if key in seen:
            continue
        seen.add(key)
        pat = re.compile(rf"^\s*(def|class)\s+{sym}\b|^\s*{sym}\s*=", re.M)
        if any(pat.search(git("show", f"{REV}:{c}").stdout) for c in cand):
            ok += 1
        else:
            miss.append((f, key, sym in ("py", "sh")))
print(f"C  {ok} resolve, {len(miss)} do not; {sum(x[2] for x in miss)} of the misses are file names")
for f, key, isname in miss:
    if not isname:
        print("   ", f, "|", key)
sys.exit(0)
