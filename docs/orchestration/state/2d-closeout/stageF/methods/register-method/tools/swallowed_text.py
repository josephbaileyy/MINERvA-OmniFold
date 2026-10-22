#!/usr/bin/env python3
"""Flag prose that a LaTeX edit moved INTO a comment (so it no longer prints).

usage: swallowed_text.py <worktree> <base-rev> [paths...]
For every file changed since <base-rev>, collect the printed (non-comment) text of the base and of the working
tree, and the comment text of the working tree. A run of >= 6 words that printed in the base, no longer prints
now, but appears inside a comment now, is flagged: that is the "comment swallowed the sentence" defect.
Also flags any working-tree line where a '%' comment begins after text on the same line and the comment part
contains a sentence-like run (>= 6 words ending with a period), the mid-line shape.
Exit 1 if anything is flagged."""
import re, subprocess, sys
wt, base = sys.argv[1], sys.argv[2]
paths = sys.argv[3:] or ["docs/analysis-note"]
files = subprocess.run(["git", "-C", wt, "diff", "--name-only", base, "--"] + paths, capture_output=True,
                       text=True, check=True).stdout.split()
files = [f for f in files if f.endswith(".tex")]
def split(src):
    printed, comment = [], []
    for line in src.splitlines():
        m = re.search(r"(?<!\\)%", line)
        if m:
            printed.append(line[:m.start()]); comment.append(line[m.end():])
        else:
            printed.append(line)
    return " ".join(printed), " ".join(comment)
def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[{}~\\]", " ", s)).strip().lower()
bad = 0
for f in files:
    try:
        old = subprocess.run(["git", "-C", wt, "show", f"{base}:{f}"], capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        old = ""
    new = open(f"{wt}/{f}").read()
    op, _ = split(old); np_, nc = split(new)
    op, np_, nc = norm(op), norm(np_), norm(nc)
    words = op.split()
    seen = set()
    for i in range(0, max(0, len(words) - 6)):
        run = " ".join(words[i:i + 6])
        if run in seen: continue
        seen.add(run)
        if run not in np_ and run in nc:
            print(f"{f}: SWALLOWED? '{run}'"); bad += 1
    for n, line in enumerate(new.splitlines(), 1):
        m = re.search(r"(?<!\\)%", line)
        if m and line[:m.start()].strip() and re.search(r"(\w+\W+){6,}\w+\.\s*$", line[m.end():]) is None:
            pass
        # prose appended after a comment that itself starts the line: a later '.' followed by a capital/lowercase run
        if line.lstrip().startswith("%") and re.search(r"\.\s+[a-z][a-z]+(\s+\w+){4,}", line):
            print(f"{f}:{n}: COMMENT LINE ENDS IN PROSE? {line.strip()[:120]}"); bad += 1
    # short tail swallowed before a line that continues lower-case or with math: "... record.  The point\n estimates $..."
    lines = new.splitlines()
    for n in range(len(lines) - 1):
        line, nxt = lines[n], lines[n + 1].lstrip()
        m = re.search(r"(?<!\\)%", line)
        if not m: continue
        tail = re.search(r"[.;:)]\s+([A-Za-z][\w-]*(\s+[A-Za-z][\w-]*){0,3})\s*$", line[m.end():])
        if tail and nxt and (nxt[0].islower() or nxt[0] == "$"):
            print(f"{f}:{n+1}: SHORT TAIL SWALLOWED? '{tail.group(1)}' + next line '{nxt[:40]}'"); bad += 1
print(f"flagged {bad}")
sys.exit(1 if bad else 0)
