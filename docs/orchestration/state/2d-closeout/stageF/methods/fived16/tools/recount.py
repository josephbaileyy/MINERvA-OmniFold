#!/usr/bin/env python3
"""Word counts for the framing and the move: each abstract's printed words (values resolved), and the paper body's
source tokens (comments, \\cite and \\label removed). Optionally against a base commit.
usage: recount.py <worktree> [--base SHA]"""
import re, subprocess, sys
wt = sys.argv[1]; base = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else None
A = f"{wt}/docs/analysis-note/"
vals = dict(re.findall(r"\\@namedef\{fv@([^}]*)\}\{(.*)\}$", open(A + "values_fived16.tex").read(), re.M))
def src(f, rev=None):
    return subprocess.run(["git", "-C", wt, "show", f"{rev}:docs/analysis-note/{f}"], capture_output=True, text=True).stdout if rev else open(A + f).read()
def abstract_words(t):
    a, b = t.index("\\begin{abstract}"), t.index("\\end{abstract}")
    s = "\n".join(l for l in t[a + 16:b].splitlines() if not l.lstrip().startswith("%"))
    return len(re.sub(r"\\fvval\{([^}]*)\}", lambda m: vals.get(m.group(1), "X"), s).split())
def body_tokens(t):
    t = "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("%"))
    t = re.sub(r"(?<!\\)%.*", "", t); t = re.sub(r"\\(cite|label)\{[^}]*\}", "", t).replace("~", " ")
    return len(t.split())
for name, f, fn in [("paper abstract", "main_paper.tex", abstract_words), ("note abstract", "main_note.tex", abstract_words),
                    ("paper body (source tokens)", "paper_body.tex", body_tokens)]:
    now = fn(src(f)); line = f"{name}: {now}"
    if base:
        line += f" (at {base}: {fn(src(f, base))})"
    print(line)
