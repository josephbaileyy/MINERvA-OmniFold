#!/usr/bin/env python3
"""Fig. 2 (fig:xsec: MEFHC_5iter_xsec_proj_pt, _proj_pz): the figure round of 2026-11-21 (Joseph's suggestions via the
director).

usage (as compose_fig2_pubratio.py: under remap_anc.py, optionally capture_palette.py, in figenv/rootmpl3108):
  FIG2_ROUND_JSON=<record.json> python3 remap_anc.py <anc> compose_fig2_round.py <xsec.root> <anc> <out dir>

Runs note-fig23-20261121/tools/compose_fig2_pubratio.py (the installed recipe: figfix's edge fix, then the
OmniFold / published lower panels) with one more wrapper under it. At each projection's save, after those edits:
- the "MINERvA ME FHC, 1.06e21 POT" stamp is removed;
- one legend, not two: the left panel's (p_T) legend is removed; the right panel's (p_par) stays at its upper right,
  above the tail, and must cover no plotted point, bar or histogram vertex (checked);
- text sizes: every text is set so that it prints at about 8.5 pt (labels, legend) or 8.0 pt (tick labels, the
  power-of-ten offset) at the figure's printed width (0.49 \\textwidth = 229.3 pt over the saved page width, measured
  after the save's tight bounding box: the record gives the final scale and printed sizes); before, the tick labels
  printed at about 5.9 pt;
- the lower label reads "This work / published" on two lines ("This work /", "published") in both panels: on one line
  it meets, or nearly meets, the upper panel's label (the short lower panel cannot hold it at the new size); if they still meet, the upper
  label moves up by the overlap plus 2 px, its x kept (recorded).
Checks (each failure stops the run): every datum unchanged (the artists' data before and after); the only texts
removed are the stamp and the left legend's entries; no two texts overlap; the legend covers no data.
"""
import json
import os
import runpy
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
METHODS = HERE.parents[1]
sys.path.insert(0, str(METHODS / "note-figpass-20261119/tools"))
import compose_tier2 as ct  # noqa: E402
from matplotlib.patches import StepPatch  # noqa: E402
from matplotlib.text import Text  # noqa: E402

PROJ = ("MEFHC_5iter_xsec_proj_pt", "MEFHC_5iter_xsec_proj_pz")
PUBRATIO = METHODS / "note-fig23-20261121/tools/compose_fig2_pubratio.py"
PRINT_W = 0.49 * 468.0
LABEL_PT, TICK_PT = 8.5, 8.0
DONE = {}


def data_state(fig):
    out = []
    for ax in fig.axes:
        for a in ax.get_children():
            if hasattr(a, "get_xydata"):
                out.append(np.asarray(a.get_xydata(), float).tobytes())
            elif isinstance(a, StepPatch):
                out.append(np.asarray(a.get_data().values, float).tobytes())
            elif hasattr(a, "get_segments"):
                out.append(b"".join(np.asarray(s, float).tobytes() for s in a.get_segments()))
    return out


def texts(fig):
    return [t for t in fig.findobj(Text) if t.get_visible() and t.get_text()]


def overlaps(fig, rend):
    ts = [t for t in texts(fig)]
    tick_drawn = set()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            for tk in axis._update_ticks():
                tick_drawn.update((id(tk.label1), id(tk.label2)))
    alltick = set()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            for tk in axis.get_major_ticks() + axis.get_minor_ticks():
                alltick.update((id(tk.label1), id(tk.label2)))
    ts = [t for t in ts if id(t) not in alltick or id(t) in tick_drawn]
    bbs = [(t, t.get_window_extent(rend)) for t in ts]
    return [(a.get_text(), b.get_text()) for i, (a, ba) in enumerate(bbs) for (b, bb) in bbs[i + 1:]
            if ba.overlaps(bb) and ba.width > 0 and bb.width > 0 and not (a.axes is not None and a.axes.get_legend() is not None
            and a in a.axes.get_legend().get_texts() and b in a.axes.get_legend().get_texts())]


def fix(fig, stem, saved_kw):
    top, bot = fig.axes[0], fig.axes[1]
    before = data_state(fig)
    stamp = [t for t in texts(fig) if t.get_text().startswith("MINERvA ME FHC")]
    if len(stamp) != 1:
        raise SystemExit(f"round: {stem}: {len(stamp)} stamps")
    stamp[0].remove()
    leg = top.get_legend()
    if leg is None:
        raise SystemExit(f"round: {stem}: no legend")
    legend_entries = [t.get_text() for t in leg.get_texts()]
    if stem.endswith("_pt"):
        leg.remove()
    # sizes, in the figure's own points; converted to print below once the saved width is known
    fig.canvas.draw(); rend = fig.canvas.get_renderer()
    tight = fig.get_tightbbox(rend)   # the save uses bbox_inches="tight"
    page_w = (tight.width + 2 * float(saved_kw.get("pad_inches", 0.1))) * 72   # get_tightbbox is in inches
    scale = PRINT_W / page_w
    for t in texts(fig):
        t.set_fontsize(LABEL_PT / scale)
    for ax in (top, bot):
        ax.tick_params(axis="both", labelsize=TICK_PT / scale)
        ax.yaxis.get_offset_text().set_fontsize(TICK_PT / scale)
        ax.xaxis.get_offset_text().set_fontsize(TICK_PT / scale)
    if top.get_legend() is not None:
        for t in top.get_legend().get_texts():
            t.set_fontsize(TICK_PT / scale)
    # split the lower label if, at the new size, it meets the upper one
    fig.canvas.draw()
    # on both panels, so they read alike (on one line it meets or nearly meets the upper label)
    bot.set_ylabel("This work /\npublished"); split = True
    bot.yaxis.labelpad += 3   # the two-line label clears the tick labels at the save's re-draw too
    fig.canvas.draw()
    # if the labels still meet, the upper label moves up by the overlap plus 2 px, its x kept (a text position only)
    moved = 0.0
    ub, lb2 = top.yaxis.label.get_window_extent(rend), bot.yaxis.label.get_window_extent(rend)
    if ub.overlaps(lb2):
        shift = lb2.y1 + 2 - ub.y0
        ta = top.get_window_extent(rend)
        cx, cy = (ub.x0 + ub.x1) / 2, (ub.y0 + ub.y1) / 2 + shift
        x, y = (cx - ta.x0) / ta.width, (cy - ta.y0) / ta.height
        for _ in range(4):   # set_label_coords anchors by alignment: correct until the box centre is (cx, cy)
            top.yaxis.set_label_coords(x, y); fig.canvas.draw()
            b = top.yaxis.label.get_window_extent(rend)
            x += (cx - (b.x0 + b.x1) / 2) / ta.width; y += (cy - (b.y0 + b.y1) / 2) / ta.height
        top.yaxis.set_label_coords(x, y); fig.canvas.draw()
        moved = shift
    # the legend covers no data
    if top.get_legend() is not None:
        lb = top.get_legend().get_window_extent(rend)
        pts = []
        for a in top.get_children():
            if hasattr(a, "get_xydata") and a.get_visible() and a.get_transform().contains_branch_seperately(top.transData)[0]:
                pts.append(a.get_transform().transform(np.asarray(a.get_xydata(), float)))
            elif isinstance(a, StepPatch):
                d = a.get_data(); e, v = np.asarray(d.edges, float), np.asarray(d.values, float)
                xy = np.column_stack([np.repeat(e, 2)[1:-1], np.repeat(v, 2)])
                pts.append(top.transData.transform(xy))
        hit = sum(int(((p[:, 0] >= lb.x0) & (p[:, 0] <= lb.x1) & (p[:, 1] >= lb.y0) & (p[:, 1] <= lb.y1)).sum()) for p in pts)
        if hit:
            raise SystemExit(f"round: {stem}: the legend covers {hit} plotted vertices")
    ov = overlaps(fig, rend)
    if ov:
        raise SystemExit(f"round: {stem}: texts overlap: {ov}")
    if data_state(fig) != before:
        raise SystemExit(f"round: {stem}: a datum changed")
    tight = fig.get_tightbbox(rend)
    page_w2 = (tight.width + 2 * float(saved_kw.get("pad_inches", 0.1))) * 72   # get_tightbbox is in inches
    DONE[stem] = {"stamp_removed": True, "legend": "removed" if stem.endswith("_pt") else "kept (upper right)",
                  "legend_entries": legend_entries, "page_width_pt_estimate": page_w2,
                  "printed_scale": PRINT_W / page_w2, "label_pt_printed": LABEL_PT / scale * PRINT_W / page_w2,
                  "tick_pt_printed": TICK_PT / scale * PRINT_W / page_w2, "lower_label_split": split, "upper_label_moved_px": moved}


def wrapped(self, fname, *a, **k):
    stem = Path(str(fname)).name.split(".")[0]
    if stem in PROJ and stem not in DONE:
        fix(self, stem, k)
    return _save(self, fname, *a, **k)


_save = ct._inner
ct._inner = wrapped          # compose_fig2_pubratio.py and compose_fig2_edges.py wrap this in turn: theirs run first
argv = sys.argv[1:]
sys.argv = [str(PUBRATIO), *argv]
runpy.run_path(str(PUBRATIO), run_name="__main__")
if set(DONE) != set(PROJ):
    raise SystemExit(f"round: fixed {sorted(DONE)}, not both projections")
if os.environ.get("FIG2_ROUND_JSON"):
    Path(os.environ["FIG2_ROUND_JSON"]).write_text(json.dumps(DONE, indent=1) + "\n")
print(f"[compose_fig2_round] {len(DONE)} projections: stamp removed, one legend, print-size text")
