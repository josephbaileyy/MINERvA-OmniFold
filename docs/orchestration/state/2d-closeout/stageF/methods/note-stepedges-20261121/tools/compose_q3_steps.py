#!/usr/bin/env python3
"""Fig. 5 (fig:q3excess): the marginal panels drawn on their bin edges (the director, 2026-11-21).

usage: Q3STEPS_JSON=<record.json> python3 compose_q3_steps.py <producer> [args with --from-arrays <npz>]

The installed file is note-q3fig-20261121's arm 1: the unchanged producer under that record's compose_q3_labels.py
(the figpass recipe, then the label colours and y labels). This tool runs exactly that, with one more edit at the
save, after compose_q3_labels' own (its checks run first, on the figure as it installs it):
- The lower panels (axes 1: q3; axes 2: E_avail) drew `step(range(n), r, where="mid")`, ticks at the bin indices
  labelled with each bin's low edge. A tick then sat at the centre of its bin's level, and the first and last bins
  were half width. Each bin i now spans [i, i+1]: the line is redrawn steps-post through x = 0..n with the last value
  repeated (the same values, nothing recomputed), the ticks are at 0..n and read the n+1 bin edges from the producer's
  own arrays (q3_e, ea_e in the --from-arrays npz, formatted as the map's tick labels, %.1f), and the x labels lose
  ", low edge". The bins keep the equal display width of the map above (the catch bins end at 100 GeV). A panel whose
  last tick label ("100.0") would cross the canvas's right edge is narrowed from the right just enough to keep it
  0.05 in inside; no text may lie outside the canvas.
Checks (each failure stops the run): the old tick labels are the low edges formatted from the npz; the edge check
(tools/edges.py) fails before the fix on each panel's stepped line and passes after on both panels, ticks included;
each new line's y on the bins equals the old y exactly; the map axes, the reference lines and every other text are
unchanged. The record goes to $Q3STEPS_JSON.
"""
import json
import os
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
METHODS = HERE.parents[1]
LABELS_TOOL = METHODS / "note-q3fig-20261121" / "tools" / "compose_q3_labels.py"
sys.path.insert(0, str(HERE))
import edges as E  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import numpy as np  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.text import Text  # noqa: E402

STEM = "q3_excess_projection"
XLAB = {1: ("$q_3$, low edge (GeV)", "$q_3$ (GeV)"), 2: ("$E_{\\rm avail}$, low edge (GeV)", "$E_{\\rm avail}$ (GeV)")}


def arrays_path(argv):
    if "--from-arrays" not in argv:
        raise SystemExit("FAIL: this tool needs the producer's --from-arrays npz (the bin edges)")
    return argv[argv.index("--from-arrays") + 1]


def texts(fig, skip=()):
    return [(t.get_text(), tuple(map(float, t.get_position())), float(t.get_fontsize()), t.get_color())
            for t in fig.findobj(Text) if t.get_visible() and t.get_text() and id(t) not in skip]


def fix(fig, q3_e, ea_e):
    rec = {}
    fig.canvas.draw()   # axis-label positions are set at a draw: snapshot the texts as they print
    a0 = fig.axes[0]
    img_before = np.ma.filled(np.ma.asarray(a0.get_images()[0].get_array(), float), np.nan).tobytes()
    tick_ids = {id(t) for i in (1, 2) for t in fig.axes[i].get_xticklabels()}
    xl_ids = {id(fig.axes[i].xaxis.label) for i in (1, 2)}
    others_before = texts(fig, tick_ids | xl_ids)
    for i, e in ((1, q3_e), (2, ea_e)):
        ax = fig.axes[i]
        n = len(e) - 1
        steps = [ln for ln in ax.lines if ln.get_drawstyle() == "steps-mid" and E.visible(ln)]
        refs = [ln for ln in ax.lines if ln not in steps]
        if len(steps) != 1:
            raise SystemExit(f"FAIL: axes {i} has {len(steps)} stepped lines, not 1")
        ln = steps[0]
        x0 = np.asarray(ln.get_xdata(), float); y0 = np.asarray(ln.get_ydata(), float)
        if not E.close(x0, np.arange(n)):
            raise SystemExit(f"FAIL: axes {i} line x {x0.tolist()} is not the bin indices 0..{n - 1}")
        old_lab = [t.get_text() for t in ax.get_xticklabels()]
        want_old = [f"{v:.1f}" for v in e[:-1]]
        if old_lab != want_old or not E.close(ax.get_xticks(), np.arange(n)):
            raise SystemExit(f"FAIL: axes {i} ticks {ax.get_xticks().tolist()} {old_lab}, want 0..{n - 1} {want_old}")
        if ax.xaxis.label.get_text() != XLAB[i][0]:
            raise SystemExit(f"FAIL: axes {i} x label {ax.xaxis.label.get_text()!r}, want {XLAB[i][0]!r}")
        disp = np.arange(n + 1, dtype=float)
        new_lab = [f"{v:.1f}" for v in e]
        before = E.check_edges(ax, disp, new_lab)
        if not any("turns or ends off the bin edges" in b for b in before):
            raise SystemExit(f"FAIL: axes {i}: the edge check does not fail before the fix: {before}")
        refs_before = [(r.get_xydata().tobytes(), r.get_linestyle(), r.get_color()) for r in refs]
        ln.set_drawstyle("steps-post")
        ln.set_data(disp, np.append(y0, y0[-1]))
        ax.set_xticks(disp, new_lab)
        ax.set_xlim(0, n)
        ax.set_xlabel(XLAB[i][1])
        after = E.check_edges(ax, disp, new_lab)
        if after:
            raise SystemExit(f"FAIL: axes {i}: the edge check fails after the fix: {after}")
        y1 = np.asarray(ln.get_ydata(), float)
        if not (np.array_equal(y1[:-1], y0) and y1[-1] == y0[-1]):
            raise SystemExit(f"FAIL: axes {i}: the values changed")
        if [(r.get_xydata().tobytes(), r.get_linestyle(), r.get_color()) for r in refs] != refs_before:
            raise SystemExit(f"FAIL: axes {i}: a reference line changed")
        rec[f"axes{i}"] = {"n_bins": n, "edges": [float(v) for v in e], "values": [float(v) for v in y0],
                           "tick_labels_before": old_lab, "tick_labels_after": new_lab,
                           "xlabel": list(XLAB[i]), "check_before": before, "check_after": after}
    # the last edge's label ("100.0") must print inside the canvas: a panel whose last tick label would cross the
    # canvas's right edge (less a margin) is narrowed from the right by that much; its left edge does not move
    margin_in = 0.05
    rend = fig.canvas.get_renderer()
    W_px = fig.bbox.width
    for i in (1, 2):
        ax = fig.axes[i]
        x1 = ax.get_xticklabels()[-1].get_window_extent(rend).x1
        over = x1 - (W_px - margin_in * fig.dpi)
        if over > 0:
            p = ax.get_position()
            ax.set_position([p.x0, p.y0, p.width - over / W_px, p.height])
            rec[f"axes{i}"]["narrowed_in"] = round(over / fig.dpi, 4)
    fig.canvas.draw()
    outside = [t.get_text() for t in fig.findobj(Text) if t.get_visible() and t.get_text()
               and (t.get_window_extent(rend).x1 > W_px + 0.5 or t.get_window_extent(rend).x0 < -0.5)]
    if outside:
        raise SystemExit(f"FAIL: texts outside the canvas: {outside}")
    if np.ma.filled(np.ma.asarray(a0.get_images()[0].get_array(), float), np.nan).tobytes() != img_before:
        raise SystemExit("FAIL: the map changed")
    tick_ids = {id(t) for i in (1, 2) for t in fig.axes[i].get_xticklabels()}
    if texts(fig, tick_ids | xl_ids) != others_before:
        raise SystemExit("FAIL: a text other than the panels' x ticks and x labels changed")
    return rec


_inner = Figure.savefig
_done = set()


def savefig(self, fname, *a, **k):
    if id(self) not in _done and (isinstance(fname, (str, bytes)) or hasattr(fname, "__fspath__")):
        name = Path(str(fname)).name.split(".")[0]
        if name != STEM:
            raise SystemExit(f"FAIL: saved figure {name!r}, this tool is for {STEM}")
        if not getattr(self, "_note_q3fix_done", False):
            raise SystemExit("FAIL: compose_q3_labels' edits did not run first")
        with np.load(ARR) as z:
            rec = fix(self, np.asarray(z["q3_e"], float), np.asarray(z["ea_e"], float))
        out = os.environ.get("Q3STEPS_JSON")
        if out:
            Path(out).write_text(json.dumps(rec, indent=1) + "\n")
        _done.add(id(self))
    return _inner(self, fname, *a, **k)


Figure.savefig = savefig
ARR = arrays_path(sys.argv)
sys.argv = [str(LABELS_TOOL), *sys.argv[1:]]
runpy.run_path(str(LABELS_TOOL), run_name="__main__")
