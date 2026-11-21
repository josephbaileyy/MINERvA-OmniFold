#!/usr/bin/env python3
"""Fig. 3 (fig:pull, MEFHC_5iter_pull_full): the inset's "chi^2/ndf paper" relabeled "descriptive distance per bin",
the value retained (Joseph's acceptance of codex2's suggestion, relayed by the director on 2026-11-21).

usage: Q3_FIG3_JSON=<record.json> python3 compose_fig3_inset.py <note-figstyle-20261117/tools/palette_run.py> <args...>

The installed Fig. 3 is note-figstyle-20261117's pull_full arm 1: compare_to_paper_fullcov.py under remap_anc.py and
palette_run.py, with --sd-label (that record's runs/pull_full/CHECKS.txt). This tool runs exactly that chain (palette_run
.py as __main__ with the same arguments), with one wrapper under palette_run's save: after its edits, the one drawn text
holding "$\\chi^2$/ndf paper = " has that prefix replaced by "descriptive distance" and, on a new line,
"per bin = " (on one line the label is wider than the histogram panel). The number after it is
not touched. The value is the full-published-covariance chi^2 divided by the number of reported bins
(compare_to_paper_fullcov.py:318-319), which the caption calls the descriptive quadratic distance per reported bin.
Checks: exactly one text holds the old prefix; after the edit the text is the old text with only that prefix changed;
no other text and no datum changes; the edited text's box stays inside its axes; the histogram's y range is raised,
if needed, so that the tallest bar stays 6% of the panel below the inset frame (recorded). Record: $Q3_FIG3_JSON.
"""
import json
import os
import runpy
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from matplotlib.text import Text  # noqa: E402

STEM = "MEFHC_5iter_pull_full"
OLD, NEW = "$\\chi^2$/ndf paper = ", "descriptive distance\nper bin = "
_inner = Figure.savefig
_rec = {}


def texts(fig):
    return [t.get_text() for t in fig.findobj(Text) if t.get_visible() and t.get_text()]


def fix(fig):
    hits = [t for t in fig.findobj(Text) if OLD in t.get_text()]
    if len(hits) != 1 or hits[0].get_text().count(OLD) != 1:
        raise SystemExit(f"fig3: {len(hits)} texts hold {OLD!r}")
    t = hits[0]
    before_all = texts(fig)
    old = t.get_text()
    new = old.replace(OLD, NEW)
    t.set_text(new)
    after_all = texts(fig)
    diff = [(a, b) for a, b in zip(before_all, after_all) if a != b]
    if len(before_all) != len(after_all) or diff != [(old, new)]:
        raise SystemExit(f"fig3: texts changed beyond the inset: {diff}")
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    bb, ab = t.get_window_extent(rend), t.axes.get_window_extent(rend)
    inside = bb.x0 >= ab.x0 - 0.5 and bb.x1 <= ab.x1 + 0.5 and bb.y0 >= ab.y0 - 0.5 and bb.y1 <= ab.y1 + 0.5
    if not inside:
        raise SystemExit(f"fig3: the relabeled inset leaves its axes: text {bb.bounds}, axes {ab.bounds}")
    # the two-line label lowers the inset's frame: the histogram's y range is raised just enough that the tallest bar
    # stays 6% of the panel height below the frame (the bars and the axis limits' lower end are unchanged)
    ax = t.axes
    bars = [pch for pch in ax.patches if isinstance(pch, Rectangle) and pch.get_height() > 0]
    hmax = max(pch.get_y() + pch.get_height() for pch in bars)
    frame = t.get_bbox_patch().get_window_extent(rend) if t.get_bbox_patch() is not None else bb
    fb = (frame.y0 - ab.y0) / ab.height
    lo, hi = ax.get_ylim()
    ylim_before = [lo, hi]
    if (hmax - lo) / (hi - lo) > fb - 0.06:
        ax.set_ylim(lo, lo + (hmax - lo) / (fb - 0.06))
        fig.canvas.draw()
    if (hmax - ax.get_ylim()[0]) / (ax.get_ylim()[1] - ax.get_ylim()[0]) > fb - 0.06 + 1e-9:
        raise SystemExit("fig3: the tallest bar still reaches the inset frame")
    value = old.split(OLD)[1].strip()
    return {"old_text": old, "new_text": new, "value": value, "inset_box_px": list(bb.bounds), "axes_box_px": list(ab.bounds),
            "frame_bottom_axes_fraction": fb, "tallest_bar": hmax, "ylim_before": ylim_before, "ylim_after": list(ax.get_ylim())}


def savefig(self, fname, *a, **k):
    if (isinstance(fname, (str, bytes)) or hasattr(fname, "__fspath__")) and not getattr(self, "_fig3_done", False):
        name = Path(str(fname)).name.split(".")[0]
        if name == STEM:
            _rec.update(fix(self))
            out = os.environ.get("Q3_FIG3_JSON")
            if out:
                Path(out).write_text(json.dumps(_rec, indent=1) + "\n")
            self._fig3_done = True
    return _inner(self, fname, *a, **k)


Figure.savefig = savefig
script = Path(sys.argv[1]).resolve()
sys.argv = [str(script), *sys.argv[2:]]
sys.path.insert(0, str(script.parent))
runpy.run_path(str(script), run_name="__main__")
if not _rec:
    raise SystemExit("fig3: the figure was never saved")
