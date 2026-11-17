#!/usr/bin/env python3
"""Run a figure producer through the restyle's capture.py, also recording where each text and axes sits.

usage: python3 -I boxes.py <capture-dir> <deploy> <script> [args...]

The arguments are capture.py's (fig-restyle-20261031/tools/capture.py, which this runs unchanged, with the same argv).
Before it runs, the deploy's technote_style is imported, as capture.py imports it, and Figure.savefig is wrapped once
more, between technote_style's wrapper and capture.py's, which is installed outermost. After each save that reaches this
wrapper, every visible text of the figure (the figure's and each axes' texts, axis labels, tick labels, legend texts)
and every axes are written to <capture-dir>/<basename of the saved file>.boxes.tsv, in figure-fraction coordinates
(x0, y0, x1, y1, origin at the lower left): the text's own extent and, where the text has one, its bbox patch's.
check_sd.py bounds the pixels a label change may move by these boxes. Nothing is drawn differently: the wrapper calls
the save it wraps and then only reads the figure."""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAPTURE = HERE.parent / "fig-restyle-20261031" / "tools" / "capture.py"
out, deploy = Path(sys.argv[1]), Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=True)
sys.path[:0] = [str(deploy / "2d-unfolding" / "uq"), str(deploy / "2d-unfolding"), str(deploy)]
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import technote_style  # noqa: E402,F401  (its .pdf-twin wrapper goes on first, as in capture.py)
from matplotlib.figure import Figure  # noqa: E402

_inner = Figure.savefig


def _row(kind, n, text, bb, fig):
    x0, y0, x1, y1 = bb.transformed(fig.transFigure.inverted()).extents
    return f"{kind}\t{n}\t{text!r}\t{x0!r}\t{y0!r}\t{x1!r}\t{y1!r}\n"


def boxes(fig):
    fig.draw_without_rendering()
    r = fig.canvas.get_renderer()
    rows = [_row("axes", n, "", ax.get_window_extent(r), fig) for n, ax in enumerate(fig.axes)]
    for t in fig.findobj(lambda a: hasattr(a, "get_text") and hasattr(a, "get_window_extent")):
        try:
            s = t.get_text()
        except TypeError:
            continue
        if not (isinstance(s, str) and s.strip() and t.get_visible()):
            continue
        n = fig.axes.index(t.axes) if t.axes in fig.axes else -1
        rows.append(_row("text", n, s, t.get_window_extent(r), fig))
        p = t.get_bbox_patch() if hasattr(t, "get_bbox_patch") else None
        if p is not None:
            rows.append(_row("textbox", n, s, p.get_window_extent(r), fig))
    return rows


def savefig(self, fname, *a, **k):
    result = _inner(self, fname, *a, **k)
    with open(out / f"{Path(str(fname)).name}.boxes.tsv", "w") as f:
        f.write("kind\taxes\ttext\tx0\ty0\tx1\ty1\n")
        f.writelines(boxes(self))
    return result


Figure.savefig = savefig
sys.argv = [str(CAPTURE)] + sys.argv[1:]
runpy.run_path(str(CAPTURE), run_name="__main__")
