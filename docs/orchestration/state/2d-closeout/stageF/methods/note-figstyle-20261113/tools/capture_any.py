#!/usr/bin/env python3
"""Run one note figure producer and record what each saved figure draws (note figure style, director 2026-11-13).

usage: python3 capture_any.py <capture-dir> <script> [args...]

The producer runs in this interpreter as __main__ (runpy), with its own directory first on sys.path and sys.argv set
to [script, *args]. Before it runs, Figure.savefig is wrapped. At each save, the figure's record goes to
<capture-dir>/<saved file name>.json:
  - "items": every data artist's hashes from fig-restyle-20261031/tools/artists.py collect(), used unchanged and
    imported from its committed path (its sha256 is in the record). "hash" covers data, colours and styles; "dhash"
    leaves the colours out; "xhash" leaves colours and line styles out;
  - "texts": every visible text's font size in points and its string (artists.texts(), not hashed);
  - "size_in": the canvas size in inches;
  - "text_overlaps": every pair of visible, non-empty texts whose drawn boxes intersect (display coordinates, after
    the save's draw), as [text, text, overlap area in px^2]. Not a data check: it finds layout collisions.
The producer's exit status is this script's. Nothing is written outside <capture-dir> except what the producer
writes itself.
"""
import hashlib
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
artists_sha = hashlib.sha256(ARTISTS.read_bytes()).hexdigest()
_orig = Figure.savefig


def savefig(self, fname, *a, **k):
    r = _orig(self, fname, *a, **k)
    if isinstance(fname, (str, bytes)) or hasattr(fname, "__fspath__"):
        _, index = artists.collect(self)
        rec = {"artists_py_sha256": artists_sha, "size_in": [float(x) for x in self.get_size_inches()],
               "items": [{k2: it[k2] for k2 in ("kind", "axes", "label", "hash", "dhash", "xhash")} for it in index],
               "texts": [[float(s), t] for s, t in artists.texts(self)], "text_overlaps": text_overlaps(self)}
        (out / (Path(str(fname)).name + ".json")).write_text(json.dumps(rec, indent=1) + "\n")
    return r


Figure.savefig = savefig
sys.argv = [str(script), *args]
sys.path.insert(0, str(script.parent))
runpy.run_path(str(script), run_name="__main__")
