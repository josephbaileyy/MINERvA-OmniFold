#!/usr/bin/env python3
"""Install one arm-1 figure of the note figure pass (each edit an exact substitution, asserted once).

usage: python3 install_layout.py <repo root> [--figs-dir figs-r2] <arm-1 PDF> [<arm-1 PDF> ...]

--figs-dir <dir> (default figs): the record subdirectory the copy goes to. figs/ files are immutable once committed,
so a figure installed a second time goes to figs-r2/. The first such install adds, after the last install_layout_fig
line, one line NFP="$REPO/.../note-figpass-20261119/<dir>" that the following install lines read; an install into
figs/ is refused once that line exists (it would read the wrong directory).

For each PDF (its file name is the installed basename):
  1. copies it to note-figpass-20261119/figs/ and docs/analysis-note/figures/ (refusing if the record's copy exists
     with other bytes: figs/ files are immutable once committed);
  2. in docs/analysis-note/make_figures.sh, comments out the figure's active install lines (any install_*
     function with that basename; an older line can still be active above the one that overrides it), and adds "install_layout_fig <basename> <sha256>" after the last
     install_layout_fig line (the "note-figpass-20261119" block, which must exist).
Prints each basename and digest.
"""
import hashlib
import shutil
import sys
from pathlib import Path

R = Path(sys.argv[1]).resolve()
ARGS = sys.argv[2:]
SUB = "figs"
if ARGS[:1] == ["--figs-dir"]:
    SUB, ARGS = ARGS[1], ARGS[2:]
NFP_LINE = f'NFP="$REPO/docs/orchestration/state/2d-closeout/stageF/methods/note-figpass-20261119/{SUB}"\n'
REC = R / "docs/orchestration/state/2d-closeout/stageF/methods/note-figpass-20261119"
MK = R / "docs/analysis-note/make_figures.sh"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


s = MK.read_text()
if "install_layout_fig() {" not in s:
    raise SystemExit("REFUSE: make_figures.sh has no install_layout_fig block")
if SUB == "figs" and any(ln.startswith('NFP="') and not ln.rstrip().endswith('/figs"') for ln in s.splitlines()):
    raise SystemExit("REFUSE: make_figures.sh already re-points NFP past figs/; an install into figs/ would read it")
for src in map(Path, ARGS):
    base, h = src.name, sha(src)
    rec = REC / SUB / base
    if rec.exists() and sha(rec) != h:
        raise SystemExit(f"REFUSE: {rec} exists with other bytes (figs/ is immutable once committed)")
    lines = s.splitlines(True)
    cur = [ln for ln in lines if not ln.startswith("#") and len(ln.split()) >= 3 and ln.split()[0].startswith("install_")
           and ln.split()[0].endswith("fig") and ln.split()[1] == base]
    if cur and cur[-1].split()[:3] == ["install_layout_fig", base, h]:
        print(f"already installed {base} {h}")
        continue
    for ln in cur:   # every active line (an older one may still be active above a later one that overrides it)
        s = s.replace(ln, "# " + ln.rstrip("\n") + "   (figure pass, 2026-11-19: installed below)\n", 1)
    if len(cur) > 1:
        print(f"note: {base} had {len(cur)} active install lines; all are now comments")
    lines = s.splitlines(True)
    anchor = [i for i, ln in enumerate(lines) if ln.startswith("install_layout_fig ") or ln.startswith("install_layout_fig() {")]
    last = max(anchor)
    if lines[last].startswith("install_layout_fig() {"):   # the first install: after the function's closing brace
        last = next(i for i in range(last, len(lines)) if lines[i].startswith("}"))
    new = [f"install_layout_fig {base:<40s} {h}\n"]
    if SUB != "figs" and NFP_LINE not in lines:
        new.insert(0, NFP_LINE)
    lines[last + 1:last + 1] = new
    s = "".join(lines)
    (REC / SUB).mkdir(exist_ok=True)
    shutil.copyfile(src, rec)
    shutil.copyfile(src, R / "docs/analysis-note/figures" / base)
    print(f"installed {base} {h}")
MK.write_text(s)
