#!/usr/bin/env python3
"""Run one note figure producer and record what each saved figure draws, colours and styles included (the note palette
pass, 2026-11-17; COMBINED-PLAN.md section 5(b)).

usage: python3 capture_palette.py <capture-dir> <script> [args...]

As note-figstyle-20261113/tools/capture_any.py, but each record is the full index of fig-restyle-20261031's
artists.py collect(): kind, axes, label, gid, "hash" (data, colours, styles), "dhash" (colours left out), "xhash"
(colours and line styles left out), and each item's "colours" and "style". That is the record fig-restyle's
compare.py reads, so its --recolour / --palette / --styles / --restyle checks run on it unchanged.
At each save, <capture-dir>/<saved file name>.json (the index) and .npz (the arrays) are written by artists.write(),
and <saved file name>.texts (JSON, not named .json so that compare.py does not read it as a figure) holds the
canvas size, every visible text's font size and string, and capture_any.py's text_overlaps (pairs of drawn
texts whose boxes intersect).
The producer runs as __main__ (runpy) with its own directory first on sys.path; its exit status is this script's.
"""
import json
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[7]
ARTISTS = ROOT / "docs/orchestration/state/2d-closeout/stageF/methods/fig-restyle-20261031/tools/artists.py"
sys.path.insert(0, str(ARTISTS.parent))
import artists  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.text import Text  # noqa: E402


# capture_any.py's text_overlaps(), unchanged (note-figstyle-20261113/tools/capture_any.py)
def text_overlaps(fig):
    """Tick labels count only if drawn: Axis._update_ticks() returns the ticks inside the view, as draw() uses them."""
    r = fig.canvas.get_renderer()
    ticklabels, drawn = set(), set()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            for t in axis.get_major_ticks() + axis.get_minor_ticks():
                ticklabels |= {id(t.label1), id(t.label2)}
            for t in axis._update_ticks():
                drawn |= {id(x) for x in (t.label1, t.label2) if x.get_visible()}
    boxes = []
    for t in fig.findobj(Text):
        if not t.get_visible() or not t.get_text().strip():
            continue
        if id(t) in ticklabels and id(t) not in drawn:
            continue
        try:
            boxes.append((t.get_text(), t.get_window_extent(r)))
        except Exception:
            continue
    out = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i][1], boxes[j][1]
            w = min(a.x1, b.x1) - max(a.x0, b.x0)
            h = min(a.y1, b.y1) - max(a.y0, b.y0)
            if w > 0.5 and h > 0.5:
                out.append([boxes[i][0], boxes[j][0], round(w * h, 1)])
    return out


out, script, args = Path(sys.argv[1]), Path(sys.argv[2]).resolve(), sys.argv[3:]
out.mkdir(parents=True, exist_ok=True)
_orig = Figure.savefig
_depth = [0]


def savefig(self, fname, *a, **k):
    outer = _depth[0] == 0
    _depth[0] += 1
    try:
        r = _orig(self, fname, *a, **k)
    finally:
        _depth[0] -= 1
    if outer and (isinstance(fname, (str, bytes)) or hasattr(fname, "__fspath__")):
        name = Path(str(fname)).name
        arrays, index = artists.collect(self)
        artists.write(out / name, arrays, index)
        (out / f"{name}.texts").write_text(json.dumps(   # not .json: compare.py reads every */*.json as a figure
            {"size_in": [float(x) for x in self.get_size_inches()],
             "texts": [[float(s), t] for s, t in artists.texts(self)],
             "text_overlaps": text_overlaps(self)}, indent=1) + "\n")
    return r


Figure.savefig = savefig
sys.argv = [str(script), *args]
sys.path.insert(0, str(script.parent))
runpy.run_path(str(script), run_name="__main__")
