#!/usr/bin/env python3
"""Text overlaps and off-canvas text of a figure producer's saved PDF, measured on one drawn canvas (round 3, 2026-11-23).

usage: python3 -I overlaps.py <out.json> <script> [args...]

Why: capture_any.py's text_overlaps (recorded by capture_palette.py) takes each text's window extent from
fig.canvas.get_renderer() after the save, without drawing the canvas first. Texts placed in data or axes coordinates
can then report positions from a different state of the figure than the legend's (seen in round 3: heatmap numbers
"overlapping" the figure legend). Here, at the producer's first PDF save, the figure's canvas is drawn once at the
figure's dpi and every visible, non-empty text is measured on that same renderer. Tick labels count only if drawn
(as capture_any.py). It records:
  overlaps   pairs of texts whose boxes intersect by more than 0.5 px in both directions (at the figure dpi);
  off_canvas texts whose box extends more than 0.5 px past the figure edge.
The producer runs as __main__ (runpy) with its own directory first on sys.path; its outputs go wherever its own
arguments send them (run_arms.sh gives it a temporary directory).
"""
import json
import runpy
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.text import Text  # noqa: E402

out, script, args = Path(sys.argv[1]), Path(sys.argv[2]).resolve(), sys.argv[3:]
_orig = Figure.savefig
done = []


def measure(fig):
    fig.canvas.draw()
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
        if not t.get_visible() or not t.get_text().strip() or (t.axes is not None and not t.axes.get_visible()):
            continue
        if id(t) in ticklabels and id(t) not in drawn:
            continue
        boxes.append((t.get_text().replace("\n", " "), t.get_window_extent(r)))
    W, H = fig.bbox.width, fig.bbox.height
    ov = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i][1], boxes[j][1]
            w = min(a.x1, b.x1) - max(a.x0, b.x0)
            h = min(a.y1, b.y1) - max(a.y0, b.y0)
            if w > 0.5 and h > 0.5:
                ov.append([boxes[i][0], boxes[j][0], round(w, 1), round(h, 1)])
    off = [[s, [round(b.x0, 1), round(b.y0, 1), round(b.x1, 1), round(b.y1, 1)]] for s, b in boxes
           if b.x0 < -0.5 or b.y0 < -0.5 or b.x1 > W + 0.5 or b.y1 > H + 0.5]
    return {"dpi": fig.dpi, "canvas_px": [W, H], "n_texts": len(boxes), "overlaps": ov, "off_canvas": off}


def savefig(self, fname, *a, **k):
    r = _orig(self, fname, *a, **k)
    if not done and str(fname).endswith(".pdf"):
        done.append(1)
        m = measure(self)
        m["pdf"] = Path(str(fname)).name
        out.write_text(json.dumps(m, indent=1) + "\n")
    return r


Figure.savefig = savefig
sys.argv = [str(script), *args]
sys.path.insert(0, str(script.parent))
runpy.run_path(str(script), run_name="__main__")
if not done:
    raise SystemExit("overlaps.py: the producer saved no PDF")
