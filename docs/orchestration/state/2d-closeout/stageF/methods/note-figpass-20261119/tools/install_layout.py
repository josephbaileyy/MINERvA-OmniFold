#!/usr/bin/env python3
"""Install one arm-1 figure of the note figure pass (each edit an exact substitution, asserted once).

usage: python3 install_layout.py <repo root> <arm-1 PDF> [<arm-1 PDF> ...]

For each PDF (its file name is the installed basename):
  1. copies it to note-figpass-20261119/figs/ and docs/analysis-note/figures/ (refusing if the record's copy exists
     with other bytes: figs/ files are immutable once committed);
  2. in docs/analysis-note/make_figures.sh, comments out the figure's current active install line (any install_*
     function with that basename), if it has one, and adds "install_layout_fig <basename> <sha256>" after the last
     install_layout_fig line (the "note-figpass-20261119" block, which must exist).
Prints each basename and digest.
"""
import hashlib
import shutil
import sys
from pathlib import Path

R = Path(sys.argv[1]).resolve()
REC = R / "docs/orchestration/state/2d-closeout/stageF/methods/note-figpass-20261119"
MK = R / "docs/analysis-note/make_figures.sh"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


s = MK.read_text()
if "install_layout_fig() {" not in s:
    raise SystemExit("REFUSE: make_figures.sh has no install_layout_fig block")
for src in map(Path, sys.argv[2:]):
    base, h = src.name, sha(src)
    rec = REC / "figs" / base
    if rec.exists() and sha(rec) != h:
        raise SystemExit(f"REFUSE: {rec} exists with other bytes (figs/ is immutable once committed)")
    lines = s.splitlines(True)
    cur = [ln for ln in lines if not ln.startswith("#") and len(ln.split()) >= 3 and ln.split()[0].startswith("install_")
           and ln.split()[0].endswith("_fig") and ln.split()[1] == base]
    if len(cur) > 1:
        raise SystemExit(f"REFUSE: {base} has {len(cur)} active install lines")
    if cur and cur[0].split()[:3] == ["install_layout_fig", base, h]:
        print(f"already installed {base} {h}")
        continue
    if cur:
        s = s.replace(cur[0], "# " + cur[0].rstrip("\n") + "   (figure pass, 2026-11-19: installed below)\n", 1)
    lines = s.splitlines(True)
    anchor = [i for i, ln in enumerate(lines) if ln.startswith("install_layout_fig ") or ln.startswith("install_layout_fig() {")]
    last = max(anchor)
    if lines[last].startswith("install_layout_fig() {"):   # the first install: after the function's closing brace
        last = next(i for i in range(last, len(lines)) if lines[i].startswith("}"))
    lines.insert(last + 1, f"install_layout_fig {base:<40s} {h}\n")
    s = "".join(lines)
    (REC / "figs").mkdir(exist_ok=True)
    shutil.copyfile(src, rec)
    shutil.copyfile(src, R / "docs/analysis-note/figures" / base)
    print(f"installed {base} {h}")
MK.write_text(s)
