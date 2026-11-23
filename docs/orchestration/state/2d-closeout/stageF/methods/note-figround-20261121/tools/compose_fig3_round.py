#!/usr/bin/env python3
"""Fig. 3 (fig:pull, MEFHC_5iter_pull_full): the figure round of 2026-11-21 (Joseph's suggestions via the director).

usage: FIG3_ROUND_JSON=<record.json> python3 compose_fig3_round.py <note-figstyle-20261117/tools/palette_run.py> <args...>

Runs note-figstyle-20261117's pull_full arm 1 chain (palette_run.py, remap_anc.py, compare_to_paper_fullcov.py
--sd-label), the recipe under note-fig23-20261121's inset relabel, which this replaces. After palette_run's edits:
- the inset (mean, SD and the descriptive distance per bin) is removed: it covered the top of the histogram and the
  zero line, the caption states the plotted quantity, and the distance per bin is in Sec. 3.1;
- the "MINERvA ME FHC, 1.06e21 POT" stamp is removed;
- every text is scaled by 0.70, so that at its printed width (\\textwidth = 468 pt on a 327.6 pt canvas, scale 1.43)
  the labels print at about 8.5 pt and the tick labels at about 7.9 pt (they printed at about 12 and 11 pt);
- the histogram bars take thin white edges (0.4 pt) in place of 1 pt black ones;
- the map's colour scale goes from (-5, 5) to (-3, 3), the colour bar with it; every map value lies inside (checked);
- the histogram's top goes from 1.6 x the tallest bar (headroom for the inset) to 1.15 x.
Checks (each failure stops the run): the image array, the bar geometry and every other datum are unchanged; the only
texts removed are the inset and the stamp; every remaining text keeps its string; all texts lie inside the canvas.
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

STEM = "MEFHC_5iter_pull_full"
SCALE, CLIM, EDGE_LW = 0.70, (-3.0, 3.0), 0.4
_inner = Figure.savefig
_rec = {}


def vis_texts(fig):
    return [t for t in fig.findobj(Text) if t.get_visible() and t.get_text()]


def drawn_texts(fig):
    """The texts that are drawn: tick labels only of ticks inside the view (matplotlib skips the others)."""
    ticklabels, drawn = set(), set()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            for tk in axis.get_major_ticks() + axis.get_minor_ticks():
                ticklabels.update((id(tk.label1), id(tk.label2)))
            for tk in axis._update_ticks():
                drawn.update(id(l) for l in (tk.label1, tk.label2) if l.get_visible())
    return [t for t in vis_texts(fig) if id(t) not in ticklabels or id(t) in drawn]


def fix(fig):
    map_ax, hist_ax = fig.axes[0], fig.axes[1]
    ims = map_ax.get_images()
    if len(ims) != 1:
        raise SystemExit(f"fig3: {len(ims)} images in the map axes")
    im = ims[0]
    arr = np.ma.filled(np.ma.asarray(im.get_array(), float), np.nan)
    if not (np.nanmin(arr) > CLIM[0] and np.nanmax(arr) < CLIM[1]):
        raise SystemExit(f"fig3: map values {np.nanmin(arr)}..{np.nanmax(arr)} leave {CLIM}")
    bars = [p for p in hist_ax.patches if isinstance(p, Rectangle)]
    geom = [(p.get_x(), p.get_y(), p.get_width(), p.get_height()) for p in bars]
    before = [(t.get_text(), t.get_fontsize()) for t in vis_texts(fig)]
    inset = [t for t in vis_texts(fig) if "ndf paper" in t.get_text() or "descriptive distance" in t.get_text()]
    stamp = [t for t in vis_texts(fig) if t.get_text().startswith("MINERvA ME FHC")]
    if len(inset) != 1 or len(stamp) != 1:
        raise SystemExit(f"fig3: {len(inset)} insets, {len(stamp)} stamps")
    removed = [inset[0].get_text(), stamp[0].get_text()]
    inset[0].remove(); stamp[0].remove()
    for t in vis_texts(fig):
        t.set_fontsize(t.get_fontsize() * SCALE)
    for ax in fig.axes:   # tick labels created at draw take the axis's size
        for which in ("x", "y"):
            ticks = ax.xaxis.get_major_ticks() if which == "x" else ax.yaxis.get_major_ticks()
            if ticks:
                ax.tick_params(axis=which, labelsize=ticks[0].label1.get_fontsize())
        ax.xaxis.get_offset_text().set_fontsize(ax.xaxis.get_offset_text().get_fontsize())
    for p in bars:
        p.set_edgecolor("white"); p.set_linewidth(EDGE_LW)
    old_clim = im.get_clim()
    im.set_clim(*CLIM)
    if im.colorbar is not None:
        im.colorbar.update_normal(im)
        cax = im.colorbar.ax   # update_normal rebuilds the colour bar's ticks at the old size
        tick = map_ax.yaxis.get_major_ticks()[0].label1.get_fontsize()
        cax.tick_params(labelsize=tick)
    # the headroom (x1.6) held the inset; with the inset gone the top is 1.15 x the tallest bar
    hmax = max(p.get_y() + p.get_height() for p in bars)
    ylim_before = list(hist_ax.get_ylim())
    hist_ax.set_ylim(ylim_before[0], 1.15 * hmax)
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    after = [(t.get_text(), t.get_fontsize()) for t in vis_texts(fig)]
    out = [t.get_text() for t in drawn_texts(fig) if (lambda b: b.x0 < -0.5 or b.y0 < -0.5 or b.x1 > fig.bbox.width + 0.5
                                                      or b.y1 > fig.bbox.height + 0.5)(t.get_window_extent(rend))]
    if out:
        raise SystemExit(f"fig3: texts outside the canvas: {out}")
    if not np.array_equal(np.ma.filled(np.ma.asarray(im.get_array(), float), np.nan), arr, equal_nan=True):
        raise SystemExit("fig3: the map changed")
    if [(p.get_x(), p.get_y(), p.get_width(), p.get_height()) for p in bars] != geom:
        raise SystemExit("fig3: the bars changed")
    kept_before = sorted(s for s, _ in before if s not in removed)
    if sorted({s for s, _ in after} - {""}) != sorted(set(kept_before)) and not set(s for s, _ in after) <= set(kept_before) | {s for s, _ in after if s.replace(".", "").replace("−", "").lstrip("-").isdigit()}:
        raise SystemExit("fig3: a text other than the inset and the stamp changed or vanished")
    return {"removed_texts": removed, "font_scale": SCALE, "font_sizes_after": sorted({round(f, 3) for _, f in after}),
            "printed_scale": 468 / (fig.get_size_inches()[0] * 72), "clim_before": list(old_clim), "clim_after": list(CLIM),
            "map_min": float(np.nanmin(arr)), "map_max": float(np.nanmax(arr)), "bar_edges": ["white", EDGE_LW],
            "n_bars": len(bars), "hist_ylim_before": ylim_before, "hist_ylim": list(hist_ax.get_ylim()), "tallest_bar": hmax}


def savefig(self, fname, *a, **k):
    if (isinstance(fname, (str, bytes)) or hasattr(fname, "__fspath__")) and not getattr(self, "_fig3r_done", False):
        if Path(str(fname)).name.split(".")[0] == STEM:
            _rec.update(fix(self))
            if os.environ.get("FIG3_ROUND_JSON"):
                Path(os.environ["FIG3_ROUND_JSON"]).write_text(json.dumps(_rec, indent=1) + "\n")
            self._fig3r_done = True
    return _inner(self, fname, *a, **k)


Figure.savefig = savefig
script = Path(sys.argv[1]).resolve()
sys.argv = [str(script), *sys.argv[2:]]
sys.path.insert(0, str(script.parent))
runpy.run_path(str(script), run_name="__main__")
if not _rec:
    raise SystemExit("fig3: the figure was never saved")
