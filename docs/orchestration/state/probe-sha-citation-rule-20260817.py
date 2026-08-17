#!/usr/bin/env python3
"""Measure the proposed sha-identity hook against the repo's REAL commit history, before
deciding whether it can be wired.

PROPOSED RULE (C's, via the mediator): refuse a commit whose message names a sha that does
not touch any file in that commit.

THE QUESTION THE DISPATCH ASKS ME TO ANSWER FIRST is not "can I implement it" but "does it
separate the defect from the innocent case at commit time" -- the mediator predicts the
mirror of check 6's inversion: loud on the innocent. So: run the rule over history and read
what it would have rejected.
"""
import collections
import re
import subprocess
import sys

import pathlib
REPO = str(pathlib.Path(__file__).resolve().parents[3])
N = int(sys.argv[1]) if len(sys.argv) > 1 else 400

# 7-40 hex, word-bounded. Deliberately generous: a rule that under-collects would flatter
# itself, and the point of this survey is to see the FALSE POSITIVES.
TOKEN = re.compile(r"\b([0-9a-f]{7,40})\b")


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                          text=True).stdout


shas = git("log", f"-{N}", "--format=%H").split()
print(f"scanning {len(shas)} commits\n")

paths_cache = {}


def paths(sha):
    if sha not in paths_cache:
        out = git("show", "--pretty=", "--name-only", sha)
        paths_cache[sha] = set(p for p in out.split("\n") if p.strip())
    return paths_cache[sha]


citations = 0
resolvable = 0
would_fail = []
verdicts = collections.Counter()

for sha in shas:
    msg = git("log", "-1", "--format=%B", sha)
    own = paths(sha)
    seen = set()
    for tok in TOKEN.findall(msg):
        if tok in seen:
            continue
        seen.add(tok)
        citations += 1
        # Does it resolve to a commit at all? Many hex tokens are sha256 fragments,
        # digests, job ids in hex -- a rule must not fire on those.
        typ = git("cat-file", "-t", tok + "^{commit}").strip()
        if typ != "commit":
            verdicts["not a commit (digest fragment etc)"] += 1
            continue
        resolvable += 1
        cited = paths(git("rev-parse", tok).strip())
        if own & cited:
            verdicts["shares a path -- rule PASSES"] += 1
        else:
            verdicts["shares NO path -- rule REJECTS"] += 1
            subj = git("log", "-1", "--format=%s", sha).strip()
            would_fail.append((sha[:8], tok, subj[:90]))

print(f"hex tokens seen              {citations}")
print(f"  resolving to a commit      {resolvable}")
for k, v in verdicts.most_common():
    print(f"    {v:5}  {k}")

rate = len(would_fail) / resolvable if resolvable else 0
print(f"\nTHE RULE WOULD REJECT {len(would_fail)} of {resolvable} real sha citations "
      f"({rate:.0%})\n")
print("A SAMPLE OF WHAT IT REJECTS -- read these before believing the rule is safe:")
for c, t, s in would_fail[:25]:
    print(f"  {c} cites {t}   {s}")
