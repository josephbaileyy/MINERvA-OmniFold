#!/usr/bin/env python3
"""Install one arm-1 figure of the note palette pass (each edit an exact substitution, asserted once).

usage: python3 install_palette.py <repo root> <arm-1 PDF> [<arm-1 PDF> ...]

For each PDF (its file name is the installed basename):
  1. copies it to note-figstyle-20261117/figs/ and docs/analysis-note/figures/ (refusing if the record's copy exists
     with other bytes: figs/ files are immutable once committed);
  2. in docs/analysis-note/make_figures.sh, comments out the figure's current install line (install_printstyle_fig,
     install_re2_fig or install_palette_fig with another digest), if it has one, and adds
     "install_palette_fig <basename> <sha256>" after the last install_palette_fig line.
Prints each basename and digest.
"""
import hashlib
import shutil
import sys
from pathlib import Path

R = Path(sys.argv[1]).resolve()
REC = R / "docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261117"
MK = R / "docs/analysis-note/make_figures.sh"
FUNCS = ("install_printstyle_fig", "install_re2_fig", "install_restyle_fig", "install_palette_fig")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


s = MK.read_text()
for src in map(Path, sys.argv[2:]):
    base, h = src.name, sha(src)
    rec = REC / "figs" / base
    if rec.exists() and sha(rec) != h:
        raise SystemExit(f"REFUSE: {rec} exists with other bytes (figs/ is immutable once committed)")
    lines = s.splitlines(True)
    cur = [ln for ln in lines if ln.split()[:2] in ([f, base] for f in FUNCS) and not ln.startswith("#")]
    if len(cur) > 1:
        raise SystemExit(f"REFUSE: {base} has {len(cur)} active install lines")
    if cur and cur[0].split()[:3] == ["install_palette_fig", base, h]:
        print(f"already installed {base} {h}")
        continue
    if cur:
        s = s.replace(cur[0], "# " + cur[0].rstrip("\n") + "   (note palette, 2026-11-17: installed below)\n", 1)
    lines = s.splitlines(True)
    last = max(i for i, ln in enumerate(lines) if ln.startswith("install_palette_fig "))
    lines.insert(last + 1, f"install_palette_fig {base:<40s} {h}\n")
    s = "".join(lines)
    (REC / "figs").mkdir(exist_ok=True)
    shutil.copyfile(src, rec)
    shutil.copyfile(src, R / "docs/analysis-note/figures" / base)
    print(f"installed {base} {h}")
MK.write_text(s)
