#!/usr/bin/env python3
"""Figs. 6 and 7 (fig:ptslices, fig:pzslices) with markers that no longer hide each other (Joseph's read of draft
e5c56bcc2, relayed by the director on 2026-11-19, item 1). Presentation only.

usage (exactly as compose_tier2.py: under capture_palette.py and note-figstyle-20261117/tools/remap_anc.py, in the
tier-2 ROOT environment):
  python3 capture_palette.py <capture> remap_anc.py <anc dir> compose_slices_markers.py <xsec.root> <anc dir> <out>
      [--pt-ncols 3] [--pz-ncols 3] [--logx]

compose_tier2.py runs unchanged (its main(), which runs the four producers and composes Figs. 4, 6 and 7). Only its
final save is wrapped: before the slice figures are saved, each panel's two point series are restyled:
  - "This work (OmniFold)" and "Published (PRD 104, 092007)" markers at MS_SCALE (0.6) of their drawn size;
  - the published markers open (face colour "none"; edge colour unchanged);
  - every error bar and cap drawn above every marker (zorder), so no marker hides a bar.
No x or y value changes (no offset), so every data item keeps its xhash. The figure legend is drawn again from the
restyled handles with the same entries, order and keywords. The projections (Fig. 4) are saved untouched.
--pt-ncols 3 / --pz-ncols 3 lay the panels out in three columns (canvas taller, same width); the y label goes to the new first
column and the x label to each column's lowest panel. Without it the four-column grid is kept.
check_slices_markers.py checks the captures against the tier-2 run's committed captures.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import compose_tier2 as ct  # noqa: E402

MS_SCALE = 0.6
SLICES = ("MEFHC_5iter_xsec_paper_pt_slices", "MEFHC_5iter_xsec_paper_pz_slices")
def _opt(flag, default):
    if flag in sys.argv:
        k = sys.argv.index(flag)
        v = int(sys.argv[k + 1])
        del sys.argv[k:k + 2]
        return v
    return default


NCOLS_BY = {SLICES[0]: _opt("--pt-ncols", 4), SLICES[1]: _opt("--pz-ncols", 4)}
NCOLS = 4
FONT_FLOOR = float(_opt("--font-floor", 0))
PUB_SCALE = _opt("--pub-size-percent", 60) / 100     # the open published markers' size, as a fraction of drawn
PUB_MEW = _opt("--pub-edge-hundredths", 0) / 100     # their edge width in points (0: unchanged)
TOP_IN = {SLICES[0]: _opt("--pt-top-hundredths", 0) / 100, SLICES[1]: _opt("--pz-top-hundredths", 0) / 100}   # points at the printed size (the canvas prints at \textwidth)
LOGX_PT = "--logx" in sys.argv   # the p_T-slices figure only: its x axis is p_parallel (1.5-60 GeV/c); the
if LOGX_PT:                      # p_parallel-slices figure's x axis is p_T from 0, where a log axis does not apply
    sys.argv.remove("--logx")
DONE = set()
REPORT = {}


def restyle(fig, stem):
    global NCOLS
    NCOLS = NCOLS_BY[stem]
    LOGX = LOGX_PT and stem == SLICES[0]
    panels = [ax for ax in fig.axes if ax.get_visible() and any(c.get_label() == ct.THIS for c in ax.containers)]
    n_series = 0
    for ax in panels:
        conts = [c for c in ax.containers if c.get_label() in (ct.THIS, ct.PUB)]
        if sorted(c.get_label() for c in conts) != sorted([ct.THIS, ct.PUB]):
            raise SystemExit(f"markers: {stem}: a panel lacks one of the two point series")
        top = max(c.lines[0].get_zorder() for c in conts)
        for c in conts:
            line, caps, cols = c.lines
            if c.get_label() == ct.PUB:
                line.set_markersize(line.get_markersize() * PUB_SCALE)
                line.set_markerfacecolor("none")
                if PUB_MEW:
                    line.set_markeredgewidth(PUB_MEW)
            else:
                line.set_markersize(line.get_markersize() * MS_SCALE)
            for a in (*caps, *cols):
                a.set_zorder(top + 1)
            n_series += 1
    if LOGX:
        from matplotlib.ticker import FixedLocator, NullFormatter, ScalarFormatter
        for ax in panels:
            lo, hi = ax.get_xlim()
            edges = [p.get_data().edges for p in ax.patches if p.get_label() == ct.TUNE][0]
            ax.set_xscale("log")
            ax.set_xlim(max(lo, float(edges[0])), hi)
            ax.xaxis.set_major_locator(FixedLocator([2, 5, 10, 20, 50]))
            ax.xaxis.set_major_formatter(ScalarFormatter())
            ax.xaxis.set_minor_formatter(NullFormatter())
    else:
        for ax in panels:                                      # ticks frozen, as the figure pass does
            (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()  # set_xticks widens the view to reach an
            ax.set_xticks([v for v in ax.get_xticks() if x0 <= v <= x1])   # off-view tick: keep only the
            ax.set_xlim(x0, x1)                                # drawn ticks and restore the limits
    if True:
        for ax in panels:
            (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
            ax.set_yticks([v for v in ax.get_yticks() if y0 <= v <= y1])
            ax.set_ylim(y0, y1)
    if NCOLS != 4:
        relayout(fig, panels, NCOLS)
    if LOGX:
        for ax in panels:
            if ax.get_xlabel():
                ax.set_xlabel(ax.get_xlabel() + ", log scale")
    if TOP_IN[stem]:
        grow_top(fig, TOP_IN[stem])
    old = fig.legends[0]
    h, lab = panels[0].get_legend_handles_labels()
    pick = dict(zip(lab, h))
    order = [t.get_text() for t in old.get_texts()]
    back = {ct.PRIOR_NEW: ct.TUNE}
    kwl = {"loc": old._loc, "frameon": False, "ncol": old._ncols, **ct.palette_lib._anchor(old),
           "fontsize": old._fontsize}
    old.remove()
    leg = fig.legend([pick[back.get(x, x)] for x in order], order, **kwl)
    if NCOLS != 4:
        place_legend(fig, leg, panels)
    if FONT_FLOOR:
        from matplotlib.text import Text
        for ax in panels:                                      # tick labels are made at draw time
            for which, axis in (("major", ax.xaxis), ("major", ax.yaxis)):
                size = axis.get_major_ticks()[0].label1.get_fontsize() if axis.get_major_ticks() else FONT_FLOOR
                if size < FONT_FLOOR:
                    ax.tick_params(axis="x" if axis is ax.xaxis else "y", which="both", labelsize=FONT_FLOOR)
        for txt in fig.findobj(Text):
            if txt.get_text() and txt.get_fontsize() < FONT_FLOOR:
                txt.set_fontsize(FONT_FLOOR)
    hidden = [(round(a.get_position().x0, 3), round(a.get_position().y0, 3)) for a in fig.axes if not a.get_visible()]
    REPORT.setdefault("hidden_axes", {})[stem] = hidden
    fig.canvas.draw()   # place the rebuilt legend and the new ticks before the capture measures text boxes
    REPORT[stem] = {"panels": len(panels), "series_restyled": n_series, "ncols": NCOLS, "logx": LOGX, "font_floor": FONT_FLOOR}


def relayout(fig, panels, ncols):
    """Panels on an ncols grid: same width, same panel aspect; the figure grows to fit the rows."""
    w, h = fig.get_size_inches()
    boxes = [ax.get_position() for ax in panels]
    x0 = min(b.x0 for b in boxes)
    x1 = max(b.x1 for b in boxes)
    y1 = max(b.y1 for b in boxes)
    pw, ph = boxes[0].width * w, boxes[0].height * h          # inches
    old_cols = sorted({round(b.x0, 4) for b in boxes})
    old_rows = sorted({round(b.y0, 4) for b in boxes}, reverse=True)
    gx = (old_cols[1] - old_cols[0]) * w - pw                  # gaps, inches
    gy = (old_rows[0] - old_rows[1]) * h - ph
    if FONT_FLOOR:                                             # room for 7 pt tick labels between columns
        gx += 0.15
    nrows = -(-len(panels) // ncols)
    span = (x1 - x0) * w
    pw2 = (span - (ncols - 1) * gx) / ncols
    ph2 = ph * pw2 / pw
    top_in, bot_in = (1 - y1) * h, min(b.y0 for b in boxes) * h
    h2 = top_in + nrows * ph2 + (nrows - 1) * gy + bot_in
    ylab = panels[0].get_ylabel()
    xlab = next(ax.get_xlabel() for ax in panels if ax.get_xlabel())
    fig.set_size_inches(w, h2)
    for k, ax in enumerate(panels):
        r, c = divmod(k, ncols)
        left = x0 * w + c * (pw2 + gx)
        bottom = h2 - top_in - (r + 1) * ph2 - r * gy
        ax.set_position([left / w, bottom / h2, pw2 / w, ph2 / h2])
        ax.set_ylabel(ylab if c == 0 else "")
        lowest = (r == nrows - 1) or (k + ncols >= len(panels))
        ax.set_xlabel(xlab if lowest else "")
    for t in fig.texts:                                        # the suptitle-like header keeps its inches from the top
        x, y = t.get_position()
        t.set_position((x, 1 - (1 - y) * h / h2))


def grow_top(fig, dh):
    """dh more inches at the top of the canvas: axes keep their inches from the bottom; figure texts and a
    figure-fraction legend anchor keep their inches from the top."""
    w, h = fig.get_size_inches()
    h2 = h + dh
    fig.set_size_inches(w, h2)
    for ax in fig.axes:
        b = ax.get_position()
        ax.set_position([b.x0, b.y0 * h / h2, b.width, b.height * h / h2])
    for t in fig.texts:
        x, y = t.get_position()
        t.set_position((x, 1 - (1 - y) * h / h2))
    for leg in fig.legends:
        bb = leg._bbox_to_anchor
        if bb is not None and hasattr(bb, "_bbox"):
            x0, y0, bw, bh = bb._bbox.bounds
            leg.set_bbox_to_anchor((x0, 1 - (1 - y0) * h / h2, bw, bh * h / h2), transform=bb._transform)


def place_legend(fig, leg, panels):
    """The legend in the first empty grid slot of the last row, or below the grid if the last row is full."""
    w, h = fig.get_size_inches()
    last = panels[-1].get_position()
    if len(panels) % NCOLS:
        step = panels[1].get_position().x0 - panels[0].get_position().x0
        leg.set_bbox_to_anchor((last.x0 + step, last.y0, last.width, last.height), transform=fig.transFigure)
        leg.set_bbox_to_anchor((last.x1 + 0.01, last.y0, last.width, last.height), transform=fig.transFigure)
        leg._loc = 6   # center left, just right of the last panel (the empty slot's column has no labels there)
    else:
        leg.set_bbox_to_anchor((0.5, 0.0), transform=fig.transFigure)
        leg._loc = 8


def wrapped(self, fname, *a, **k):
    stem = Path(str(fname)).name.split(".")[0]
    if stem in SLICES and stem not in DONE:
        restyle(self, stem)
        DONE.add(stem)
    return _save(self, fname, *a, **k)


_save = ct._inner
ct._inner = wrapped
ct.main()
if DONE != set(SLICES):
    raise SystemExit(f"markers: restyled {sorted(DONE)}, not both slice figures")
out = Path(sys.argv[3])
import json  # noqa: E402
(out / "compose_slices_markers.json").write_text(json.dumps({"ms_scale": MS_SCALE, **REPORT}, indent=1) + "\n")
print(f"[compose_slices_markers] restyled {len(DONE)} slice figures, ncols {NCOLS_BY}, log p_parallel {LOGX_PT}")
