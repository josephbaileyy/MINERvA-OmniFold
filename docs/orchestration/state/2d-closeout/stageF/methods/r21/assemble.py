#!/usr/bin/env python3
"""Assemble r21's paper_body.tex from the writer's batches b1..b4.

usage: python3 -I assemble.py <worktree> <writer-dir> [--check]

The new body is:
- the base's header comment block, as it stands;
- one r21 comment line;
- b1.tex, b2.tex, b3.tex and b4.tex, concatenated.
Two things the writer did not carry are then restored:
- the five FIVED16 source-marker pairs. fived16/check_ledger.py (its rule 7), fived16/prd-read/tools/make_inputs.py and
  fived16/tools/packet_text.py read the blocks between them. Each base BEGIN line is copied verbatim and wraps the
  same subsection's prose, found by its heading or label in the new text;
- each table's lines between its `\\label` and `\\begin{tabular}` (`\\centering`, the font size, `\\tabcolsep`).
  The ledger's table rows start at `\\begin{tabular}`, so the writer never saw them.
--check exits 0 only if the tree's paper_body.tex equals the assembly."""
import re
import subprocess
import sys
from pathlib import Path

W, WD = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
BASE = "78df7327"
base = subprocess.run(["git", "-C", str(W), "show", f"{BASE}:docs/analysis-note/paper_body.tex"], capture_output=True,
                      text=True, check=True).stdout
begins = re.findall(r"^% FIVED16-BEGIN.*$", base, re.M)
assert len(begins) == 5 and begins[0].startswith("% FIVED16-BEGIN DECISION"), len(begins)
header = base.split("\n")[:3]
assert all(l.startswith("%") for l in header), header
body = "\n".join((WD / f"b{k}.tex").read_text().rstrip("\n") for k in (1, 2, 3, 4)) + "\n"

# (start anchor in the new text, end anchor): each block runs from the line after the start anchor to just before the
# end anchor, as in the base.
BLOCKS = [("\\subsection{Reporting cells}", "\\section{Uncertainties and validation}"),
          ("\\label{sec:cov16}", "\\subsection{"),
          ("\\label{sec:fd16}", "\\section{The sixteen-cell cross section}"),
          ("\\subsection{Result}", "\\subsection{"),
          ("\\label{sec:gen16}", "\\subsection{")]
for (a, b), beg in zip(BLOCKS, begins):
    i = body.index(a)
    i = body.index("\n", i) + 1
    j = body.index(b, i)
    j = body.rfind("\n", 0, j) + 1
    body = body[:i] + beg + "\n" + body[i:j].rstrip("\n") + "\n% FIVED16-END\n\n" + body[j:]
assert body.count("% FIVED16-BEGIN") == 5 and body.count("% FIVED16-END") == 5

# Each table's lines between its \label and \begin{tabular} (\centering, the font size, \tabcolsep), from the base
for m in re.finditer(r"\\label\{(tab:[^}]*)\}", base):
    pre = base[m.end():base.index("\\begin{tabular}", m.end())].strip()
    lab = m.group(0)
    assert body.count(lab) == 1, lab
    k = body.index(lab) + len(lab)
    t = body.index("\\begin{tabular}", k)
    if pre and pre not in body[k:t]:
        body = body[:t] + pre + "\n  " + body[t:]

# The absence claims' support. The rewrite dropped the base's comments, so each absence claim's Search line comes back
# into its paragraph: the base's own line for that claim, or the note's Search line for the same claim. Each is cut from
# its source by its opening words, so nothing is retyped.
note_summary = (W / "docs/analysis-note/sec_summary.tex").read_text()
def search_line(text, start):
    hit = [l for l in text.splitlines() if l.startswith(start)]
    assert len(hit) >= 1, start
    return hit[0]
S_16 = search_line(base, "% Search: coverage of the sixteen-cell intervals;")
S_CM = search_line(base, "% Search: coverage of C_model at held-out truths;")
S_PL = search_line(base, "% Search: run-period block;")
S_2D = search_line(note_summary, "% Search: held-out simulation; held-out-MC re-test; S1 has not been coverage-tested")
SUPPORT = [("Interval coverage has not been validated.", S_16),
           ("its coverage at truths held out of its construction has not been validated", S_CM),
           ("The coverage of this block and of the total covariance has not been tested", S_2D),
           ("Because the block is built from the observed", S_PL),
           ("The two-dimensional covariance has not been independently validated", S_2D),
           ("The sixteen-cell result also has total uncertainties, whose coverage is not validated", S_16)]
lines = body.split("\n")
for frag, sup in SUPPORT:
    hit = [k for k, l in enumerate(lines) if frag in l and not l.lstrip().startswith("%")]
    assert len(hit) == 1, (frag, len(hit))
    k = hit[0]
    while k + 1 < len(lines) and lines[k + 1].strip() and not lines[k + 1].lstrip().startswith(("\\item", "\\end{", "\\begin{")):
        k += 1
    lines.insert(k + 1, sup)
body = "\n".join(lines)

out = "\n".join(header) + ("\n% r21 (2026-10-29): the body was rewritten from a reverse outline and a fact ledger "
                           "(docs/orchestration/state/2d-closeout/stageF/methods/r21/). The base's per-number source "
                           "comments, with their evidence routes, are in git history at 78df7327.\n\n") + body
# One line per paragraph and per comment block, as reflow_tex.py --note keeps every hand-written note source (its
# reflow_text, imported; paper_body.tex is not in its keep-comments-in-place set).
sys.path.insert(0, str(W / "docs/analysis-note"))
from reflow_tex import reflow_text  # noqa: E402
out = reflow_text(out, True)[0]
target = W / "docs/analysis-note/paper_body.tex"
if "--check" in sys.argv:
    same = target.read_text() == out
    print("assemble --check:", "OK" if same else "DIFFERS")
    sys.exit(0 if same else 1)
target.write_text(out)
print("assembled paper_body.tex:", len(out.splitlines()), "lines; FIVED16 blocks 5; table preambles restored")
