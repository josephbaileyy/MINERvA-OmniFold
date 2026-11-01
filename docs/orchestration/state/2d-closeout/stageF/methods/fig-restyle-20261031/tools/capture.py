#!/usr/bin/env python3
"""Run one figure producer as re2c_run.sh's `step` does, recording what each saved figure draws (DECLARATION.md §3).

usage: python3 -I capture.py <capture-dir> <deploy> <script> [args...]

The producer runs in this interpreter: the deploy's 2d-unfolding/uq, 2d-unfolding and root go first on sys.path, and
runpy runs the script as __main__, as at re2c_run.sh:43-46. Before it runs:
  - technote_style is imported, so that its savefig wrapper (the .pdf twin of every .png) is installed first, and
    Figure.savefig is wrapped once more, outermost. At each outer save, every data artist of the figure is written to
    <capture-dir>/<basename of the saved file>.npz, with a JSON index beside it (artists.py);
  - ROOT.TFile.Open is wrapped, if ROOT imports, so each opened file's path and sha256 go to <capture-dir>/opened.tsv.
    Each existing file named in argv is also hashed there (kind "argv"), since a file opened from C++ or by a default
    path is seen only through the wrapper.
It refuses to run with TECHNOTE_DARK set, which recolours every series. The producer's exit status is this script's.
RESTYLE AMENDMENT 1: Axes.hist is wrapped. Each call's values are recorded on the figure (artists.py's "hist-input"
items) and the patches it draws carry gid "restyle-hist", so that compare.py's named binning exception can hold the
values bit for bit while the bins change. After each save, every text of the figure and its axes (ax.texts, fig.texts)
is tested against every data artist's drawn geometry in display coordinates, and each overlap is written to
<capture-dir>/<figure>.overlaps.tsv (overlap.py reports and gates them).
RESTYLE AMENDMENT 2: after each save, every legend entry is written to <capture-dir>/<figure>.legend.tsv (names.py).
"""
import hashlib
import json
import os
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artists  # noqa: E402
import overlap  # noqa: E402

if os.environ.get("TECHNOTE_DARK"):
    sys.exit("capture.py: TECHNOTE_DARK is set; technote_style would recolour every series, so the run is refused")
out, deploy, script = Path(sys.argv[1]), Path(sys.argv[2]).resolve(), sys.argv[3]
args = sys.argv[4:]
out.mkdir(parents=True, exist_ok=True)
opened = out / "opened.tsv"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def note_open(kind, path):
    p = Path(str(path).split("?")[0])
    if p.is_file():
        with open(opened, "a") as f:
            f.write(f"{kind}\t{p.resolve()}\t{sha256(p)}\n")


sys.path[:0] = [str(deploy / "2d-unfolding" / "uq"), str(deploy / "2d-unfolding"), str(deploy)]
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import technote_style  # noqa: E402,F401  (installs its .pdf-twin wrapper before ours)
from matplotlib.figure import Figure  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

_inner = Figure.savefig
_depth = [0]


def savefig(self, fname, *a, **k):
    outer = _depth[0] == 0
    _depth[0] += 1
    try:
        if outer:
            name = Path(str(fname)).name
            arrays, index = artists.collect(self)
            artists.write(out / name, arrays, index)
        result = _inner(self, fname, *a, **k)
        if outer:
            with open(out / f"{name}.overlaps.tsv", "w") as f:
                f.write("text\taxes\tartist\tartist_label\n")
                f.writelines(f"{s!r}\t{n}\t{kind}\t{lab!r}\n" for s, n, kind, lab in overlap.overlaps(self))
        if outer:  # RESTYLE AMENDMENT 2: each legend entry, for names.py
            with open(out / f"{name}.legend.tsv", "w") as f:
                f.write("axes\ttext\n")
                f.writelines(f"{n}\t{t!r}\n" for n, t in artists.legend_texts(self))
        if outer:  # after the save has drawn the figure, so every tick label exists
            with open(out / f"{name}.textsizes.tsv", "w") as f:
                f.write(f"# figure width (in)\t{self.get_size_inches()[0]!r}\n")
                f.writelines(f"{s!r}\t{x}\n" for s, x in artists.texts(self))
        return result
    finally:
        _depth[0] -= 1


Figure.savefig = savefig

from matplotlib.axes import Axes  # noqa: E402
import numpy as _np  # noqa: E402

_hist = Axes.hist


def hist(self, x, *a, **k):
    """Record the values given to hist (artists.py "hist-input") and tag the patches it draws."""
    fig = self.figure
    n = fig.axes.index(self)
    vals = _np.concatenate([_np.ravel(_np.asarray(v, dtype=float)) for v in (x if isinstance(x, (list, tuple)) else [x])])
    fig.__dict__.setdefault("_restyle_hist_inputs", []).append((n, vals))
    out = _hist(self, x, *a, **k)
    for p in self.patches:
        if p.get_gid() is None:
            p.set_gid("restyle-hist")
    return out


Axes.hist = hist
plt.savefig = lambda fname, *a, **k: plt.gcf().savefig(fname, *a, **k)

try:
    import ROOT  # noqa: E402

    _open = ROOT.TFile.Open

    def _logged_open(name, *a, **k):
        note_open("TFile", name)
        return _open(name, *a, **k)

    ROOT.TFile.Open = _logged_open
except ImportError:
    pass

for a in args:  # "PATH", "PATH:histogram", "NAME:PATH" and "--opt=PATH" all name a file
    for part in a.replace("=", ":").split(":"):
        note_open("argv", part)
sys.argv = [script] + args
runpy.run_path(script, run_name="__main__")
with open(out / "capture-done.json", "w") as f:
    json.dump({"script": script, "argv": args}, f, indent=1)
