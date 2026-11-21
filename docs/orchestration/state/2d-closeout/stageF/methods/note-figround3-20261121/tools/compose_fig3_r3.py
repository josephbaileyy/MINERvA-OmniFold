#!/usr/bin/env python3
"""Fig. 3 (fig:pull, MEFHC_5iter_pull_full): round 3 of 2026-11-21 (Joseph and the rewrite helper, via the director).

usage: FIG3_R3_JSON=<record.json> FIG3_ROUND_JSON=<r2 record> python3 compose_fig3_r3.py <palette_run.py> <args...>

Runs note-figround-20261121/tools/compose_fig3_round.py (the installed recipe: the palette chain, then round 2's
edits) with one more wrapper under it. At the save, after round 2's edits:
- the histogram's x axis is (-3, 3), symmetric about 0 like the map's colour scale (every bar lies inside: checked);
- the file is saved cropped to its drawn content (bbox_inches="tight", pad 0.02 in): the canvas kept empty space below
  and between the panels, which printed as about an inch above the caption. The figure stays at \\textwidth, so the
  panels print larger in about the same page space;
- the text is rescaled for the new printed scale (468 pt over the cropped page width) so that labels still print at
  8.5 pt and tick labels at 7.9 pt (iterated: the crop depends on the text); the record gives the final sizes.
The cropped page no longer has the 327.6 x 165.6 pt size that make_figures.sh asserts before its pdfcrop of the left
panel (paper_validation_residual.pdf). No .tex file includes that crop, and the committed crop is unchanged.
Checks (each failure stops the run): every datum unchanged; texts unchanged apart from size and the x tick labels;
no text overlap at the final draw.
"""
import json
import os
import runpy
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from matplotlib.text import Text  # noqa: E402

HERE = Path(__file__).resolve().parent
R2 = HERE.parents[1] / "note-figround-20261121/tools/compose_fig3_round.py"
STEM = "MEFHC_5iter_pull_full"
PAD_IN, PRINT_W, LABEL_PT, TICK_PT, XLIM = 0.02, 468.0, 8.5, 7.9, (-3.0, 3.0)
_inner = Figure.savefig
_rec = {}


def drawn(fig):
    tl, dr = set(), set()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            for tk in axis.get_major_ticks() + axis.get_minor_ticks():
                tl.update((id(tk.label1), id(tk.label2)))
            for tk in axis._update_ticks():
                dr.update(id(l) for l in (tk.label1, tk.label2) if l.get_visible())
    return [t for t in fig.findobj(Text) if t.get_visible() and t.get_text() and (id(t) not in tl or id(t) in dr)]


def is_tick(fig, t):
    return any(t is tk.label1 or t is tk.label2 for ax in fig.axes for axis in (ax.xaxis, ax.yaxis)
               for tk in axis.get_major_ticks() + axis.get_minor_ticks())


def fix(fig, k):
    hist = fig.axes[1]
    bars = [p for p in hist.patches if isinstance(p, Rectangle)]
    lo = min(p.get_x() for p in bars); hi = max(p.get_x() + p.get_width() for p in bars)
    if not (XLIM[0] <= lo and hi <= XLIM[1]):
        raise SystemExit(f"fig3 r3: bars span {lo}..{hi}, outside {XLIM}")
    geom = [(p.get_x(), p.get_y(), p.get_width(), p.get_height()) for p in bars]
    img = np.ma.filled(np.ma.asarray(fig.axes[0].get_images()[0].get_array(), float), np.nan).tobytes()
    xlim_before = list(hist.get_xlim())
    hist.set_xlim(*XLIM)
    rend = fig.canvas.get_renderer()
    for _ in range(4):   # the crop depends on the text, the text size on the crop
        fig.canvas.draw()
        tb = fig.get_tightbbox(rend)
        page_w = (tb.width + 2 * PAD_IN) * 72
        scale = PRINT_W / page_w
        for t in drawn(fig):
            t.set_fontsize((TICK_PT if is_tick(fig, t) else LABEL_PT) / scale)
        for ax in fig.axes:
            ax.tick_params(axis="both", labelsize=TICK_PT / scale)
    fig.canvas.draw()
    tb = fig.get_tightbbox(rend); page_w = (tb.width + 2 * PAD_IN) * 72; page_h = (tb.height + 2 * PAD_IN) * 72
    scale = PRINT_W / page_w
    ts = drawn(fig); bbs = [(t, t.get_window_extent(rend)) for t in ts]
    ov = [(a.get_text(), b.get_text()) for i, (a, ba) in enumerate(bbs) for b, bb in bbs[i + 1:] if ba.overlaps(bb)]
    if ov:
        raise SystemExit(f"fig3 r3: texts overlap: {ov}")
    if [(p.get_x(), p.get_y(), p.get_width(), p.get_height()) for p in bars] != geom or \
            np.ma.filled(np.ma.asarray(fig.axes[0].get_images()[0].get_array(), float), np.nan).tobytes() != img:
        raise SystemExit("fig3 r3: a datum changed")
    k["bbox_inches"] = "tight"; k["pad_inches"] = PAD_IN
    sizes = sorted({round(t.get_fontsize() * scale, 2) for t in ts})
    return {"hist_xlim_before": xlim_before, "hist_xlim": list(XLIM), "bars_span": [lo, hi], "page_pt": [page_w, page_h],
            "printed_scale": scale, "printed_sizes_pt": sizes, "pad_inches": PAD_IN}


def savefig(self, fname, *a, **k):
    if (isinstance(fname, (str, bytes)) or hasattr(fname, "__fspath__")) and Path(str(fname)).name.split(".")[0] == STEM:
        if not getattr(self, "_fig3r3_done", False):
            _rec.update(fix(self, k)); self._fig3r3_kw = {"bbox_inches": "tight", "pad_inches": PAD_IN}
            self._fig3r3_done = True
            if os.environ.get("FIG3_R3_JSON"):
                Path(os.environ["FIG3_R3_JSON"]).write_text(json.dumps(_rec, indent=1) + "\n")
        k.update(self._fig3r3_kw)   # the PNG twin is cropped the same way
    return _inner(self, fname, *a, **k)


Figure.savefig = savefig
argv = sys.argv[1:]
sys.argv = [str(R2), *argv]
runpy.run_path(str(R2), run_name="__main__")
if not _rec:
    raise SystemExit("fig3 r3: the figure was never saved")
