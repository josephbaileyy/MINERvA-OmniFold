#!/usr/bin/env python3
"""Inputs for an external caption read of one redrawn-figure batch (the director's request, 2026-11-17).

usage: python3 caption_read_inputs.py <repo worktree> <base commit> <out dir> <batch name> <label=file[,file...]> ...

For each figure (a \\label and the installed PDF stem(s) it shows): the PDF as installed at <base> ("old") and as now
installed in the worktree ("new") are rendered to PNG at 110 DPI with pdftoppm, and the figure's caption is read from
the worktree's docs/analysis-note/*.tex: the \\caption{...} (balanced braces) of the figure environment holding that
\\label, or, if no file holds the label, of the environment whose \\includegraphics names the first stem. Writes
<out dir>/inputs/<label>/{old_*.png,new_*.png,caption.txt} and <out dir>/prompt.txt, and prints what it wrote.
"""
import re
import subprocess
import sys
from pathlib import Path

wt, base, out, batch = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), sys.argv[4]
specs = [a.split("=", 1) for a in sys.argv[5:]]
note = wt / "docs/analysis-note"
tex = {p: p.read_text() for p in note.glob("*.tex")}


def caption_at(src, pos):
    """The \\caption{...} of the figure environment around pos."""
    start = src.rfind("\\begin{figure", 0, pos)
    end = src.find("\\end{figure", pos)
    env = src[start:end]
    i = env.find("\\caption")
    if i < 0:
        return None
    j = env.index("{", i)
    depth, k = 0, j
    while k < len(env):
        depth += {"{": 1, "}": -1}.get(env[k], 0)
        if depth == 0:
            return env[j + 1:k]
        k += 1
    return None


def find(label, stem):
    for p, s in tex.items():
        m = s.find(f"\\label{{{label}}}")
        if m >= 0:
            return p.name, caption_at(s, m)
    for p, s in tex.items():
        m = re.search(r"\\includegraphics(\[[^\]]*\])?\{" + re.escape(stem) + r"(\.pdf)?\}", s)
        if m:
            return p.name, caption_at(s, m.start())
    return None, None


rows = []
for label, files in specs:
    d = out / "inputs" / label.replace(":", "_")
    d.mkdir(parents=True, exist_ok=True)
    stems = files.split(",")
    for st in stems:
        old = subprocess.run(["git", "-C", str(wt), "show", f"{base}:docs/analysis-note/figures/{st}.pdf"],
                             capture_output=True, check=True).stdout
        (d / f"old_{st}.pdf").write_bytes(old)
        for tag, pdf in (("old", d / f"old_{st}.pdf"), ("new", note / "figures" / f"{st}.pdf")):
            subprocess.run(["pdftoppm", "-r", "110", "-png", "-singlefile", str(pdf), str(d / f"{tag}_{st}")], check=True)
        (d / f"old_{st}.pdf").unlink()
    src, cap = find(label, stems[0])
    (d / "caption.txt").write_text(f"{label} ({src})\n{cap}\n" if cap else f"{label}: CAPTION NOT FOUND\n")
    rows.append(f"- {d.relative_to(out)}: {', '.join(stems)} (caption from {src})")
prompt = f"""You are a careful scientific figure reviewer. READ-ONLY task: do not modify, create or delete any file; write
nothing to disk; give your whole answer on standard output only.

Batch "{batch}" of an analysis note's figures was redrawn in a new colour palette (and, for some, a few text-only
edits: notation, a power of ten moved into an axis label, a baked-in figure title removed, a resize). For each figure
directory below you have old_*.png (the figure as it was), new_*.png (as redrawn) and caption.txt (the caption as it now
stands in the note):
{chr(10).join(rows)}

For each figure answer three questions, quoting the caption or the figure text you rely on:
1. Does the caption still describe the NEW figure correctly? List every statement it makes that the new figure
   contradicts (a colour, marker, line style, panel, label or quantity name that is now different). "None" if none.
2. Was any text or caveat that was printed in the OLD figure (a title, annotation, legend entry, axis label, note)
   lost in the NEW figure, and if so is it carried by the caption? List each lost item verbatim and say whether the
   caption carries it.
3. Does the NEW figure show anything the old one did not (a new label, a changed number, a different quantity)?
Then give one line per figure: "<label>: OK" or "<label>: FLAG - <short reason>".
Do not comment on aesthetics or suggest improvements. Report only differences between the old and new figures and
caption mismatches.
"""
(out / "prompt.txt").write_text(prompt)
print("\n".join(rows))
