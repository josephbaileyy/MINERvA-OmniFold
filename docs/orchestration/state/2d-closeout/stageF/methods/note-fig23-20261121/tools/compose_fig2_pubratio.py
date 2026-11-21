#!/usr/bin/env python3
"""Fig. 2 (fig:xsec: MEFHC_5iter_xsec_proj_pt, _proj_pz): the lower panels as OmniFold / published MINERvA
(Joseph's acceptance of codex2's suggestion, relayed by the director on 2026-11-21). The upper panels, the prior curves
included, are unchanged.

usage (as compose_fig2_edges.py: under note-figstyle-20261117/tools/remap_anc.py, optionally under capture_palette.py,
in the tier-2 ROOT environment):
  python3 remap_anc.py <anc dir> compose_fig2_pubratio.py <xsec.root> <anc dir> <out dir>

The installed Fig. 2 is note-figfix-20261120's: compose_tier2.py, with compose_fig2_edges.py wrapping its save (the
published prediction redrawn on the projection edges). This tool runs exactly that, compose_fig2_edges.py as __main__,
with one more wrapper under it, so at each projection's save the edge fix is made first and then:
  - the lower panel's points, which the producer draws as this result / prior (plot_2d_cross_section.py:182-192), are
    recomputed in place as this result / published: y = f_i / p_i, with f_i the OmniFold points of the upper panel and
    p_i the published points drawn there ("Published (PRD 104, 092007)", one per bin centre). The vertical bars become
    the OmniFold bars over p_i (finite weighted-sample statistics only; the published points carry no bars in the
    figure). The horizontal bars, the markers and the style are kept; the caps move with the bars.
  - the unity reference line keeps its style but takes the published points' colour (it drew in the prior's colour,
    which named the old denominator);
  - the axis label "This work / prior" reads "This work / published". It overruns the short lower panel into the
    upper panel's label column, so the upper y label moves up by the overlap plus 2 px (x unchanged; recorded);
  - the lower panel's ticks are at 1 - h/2, 1 and 1 + h/2 for the range (1 - h, 1 + h), so none sits at the joint;
  - the y range: the smallest symmetric range about 1, in steps of 0.05, that holds every new point and bar with a
    0.02 margin (recorded). The producer's (0.7, 1.3) was set for the ratio to the prior; the ratio to the published
    result differs from 1 by a few percent, which that range flattens onto the reference line.
Checks (each failure stops the run): the upper panel's OmniFold and published x are the same bin centres; the old lower
points equal f_i / prior_i (the prior histogram of the upper panel) to 1e-12, which pairs the bins; the new points equal
f_i / p_i exactly as computed; nothing in the upper panel changes; the edge check (check_fig: note-stepedges-20261121/tools/edges.py's rules, errorbar-aware) passes on both panels after
the change. Writes <out>/compose_fig2_pubratio.json (per bin: edges, f_i, p_i,
ratio, bar).
"""
import json
import runpy
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
METHODS = HERE.parents[1]
sys.path.insert(0, str(METHODS / "note-figpass-20261119/tools"))
sys.path.insert(0, str(METHODS / "note-stepedges-20261121/tools"))
import compose_tier2 as ct  # noqa: E402
import edges as E  # noqa: E402
from matplotlib.colors import to_rgba  # noqa: E402
from matplotlib.patches import StepPatch  # noqa: E402

PROJ = ("MEFHC_5iter_xsec_proj_pt", "MEFHC_5iter_xsec_proj_pz")
FIGFIX = METHODS / "note-figfix-20261120/tools/compose_fig2_edges.py"
OLD_Y, NEW_Y = "This work / prior", "This work / published"
DONE = {}


def top_state(ax):
    out = []
    for a in ax.get_children():
        if hasattr(a, "get_xydata"):
            out.append((type(a).__name__, a.get_label(), np.asarray(a.get_xydata(), float).tobytes()))
        elif isinstance(a, StepPatch):
            d = a.get_data(); out.append(("StepPatch", a.get_label(), np.asarray(d.values).tobytes()))
    return out


def check_fig(ax, edges):
    """edges.py's rules made errorbar-aware (as note-figfix-20261120's check_edges): each errorbar container's points
    are at the bin centres, its x half-widths are the half bin widths and its x caps sit on the edges; its own artists
    are then exempt, and every other line is judged by edges.py (steps on the edges, markers at the centres)."""
    edges = np.asarray(edges, float); cen = 0.5 * (edges[:-1] + edges[1:]); half = 0.5 * np.diff(edges)
    bad, own = [], set()
    for c in ax.containers:
        if not hasattr(c, "has_xerr"):
            continue
        line, caps, cols = c.lines
        own.update(id(a) for a in (line, *caps, *cols))
        x = np.asarray(line.get_xdata(), float)
        if not E.close(x, cen):
            bad.append(f"errorbar {c.get_label()!r}: points not at the bin centres")
        if c.has_xerr:
            hx = cols[0].get_segments()
            w = np.array([abs(sg[1][0] - sg[0][0]) / 2 for sg in hx])
            if not E.close(w, half):
                bad.append(f"errorbar {c.get_label()!r}: x half-widths are not the half bin widths")
        for cp in caps:
            if cp.get_marker() == "|" and not E.on_grid(np.asarray(cp.get_xdata(), float), edges):
                bad.append(f"errorbar {c.get_label()!r}: x caps off the bin edges")
    for ln in ax.lines:
        if id(ln) in own or not ln.get_transform().contains_branch_seperately(ax.transData)[0]:
            continue
        x = np.asarray(ln.get_xdata(), float)
        if x.size == 0:
            continue
        ds = ln.get_drawstyle()
        if E.visible(ln) and ds.startswith("steps"):
            b = E.drawn_x(ln)
            if not E.on_grid(b, edges) or not (E.close(b.min(), edges[0]) and E.close(b.max(), edges[-1])):
                bad.append(f"line {ln.get_label()!r}: {ds} turns or ends off the bin edges")
        elif not E.visible(ln):
            if not E.on_grid(x, cen):
                bad.append(f"markers {ln.get_label()!r}: points not at the bin centres")
        elif not E.on_grid(x, np.concatenate([edges, cen])):
            bad.append(f"line {ln.get_label()!r}: x values off the bin edges and centres")
    for pch in ax.patches:
        if isinstance(pch, StepPatch) and not E.close(pch.get_data().edges, edges):
            bad.append(f"StepPatch {pch.get_label()!r}: edges differ")
    return bad


def fix(fig, stem):
    top, bot = fig.axes[0], fig.axes[1]
    before_top = top_state(top)
    xf, f, xerr_f, yerr_f, _ = ct.eb(top, ct.THIS)
    pub = [ln for ln in top.lines if ln.get_label() == ct.PUB]
    prior = [p for p in top.patches if isinstance(p, StepPatch) and p.get_label() == ct.TUNE]
    if len(pub) != 1 or len(prior) != 1:
        raise SystemExit(f"pubratio: {stem}: {len(pub)} published lines, {len(prior)} prior histograms")
    xp, p = np.asarray(pub[0].get_xdata(), float), np.asarray(pub[0].get_ydata(), float)
    edges = np.asarray(prior[0].get_data().edges, float); t = np.asarray(prior[0].get_data().values, float)
    cen = 0.5 * (edges[:-1] + edges[1:])
    if not (E.close(xf, cen) and E.close(xp, cen)):
        raise SystemExit(f"pubratio: {stem}: OmniFold or published points are not at the bin centres")
    if len(bot.containers) != 1:
        raise SystemExit(f"pubratio: {stem}: {len(bot.containers)} errorbar containers in the lower panel")
    c = bot.containers[0]
    line, caps, cols = c.lines
    if any(cp.get_marker() not in ("|", "_") for cp in caps):
        raise SystemExit(f"pubratio: {stem}: an errorbar cap is neither an x cap '|' nor a y cap '_'")
    xr, r_old = np.asarray(line.get_xdata(), float), np.asarray(line.get_ydata(), float)
    if not E.close(xr, cen) or not E.close(r_old, np.where(t > 0, f / np.where(t > 0, t, 1), 0)):
        raise SystemExit(f"pubratio: {stem}: the lower points are not this result / prior on the bins")
    if np.any(p <= 0):
        raise SystemExit(f"pubratio: {stem}: a published value is not positive")
    r = f / p
    e = yerr_f / p
    line.set_ydata(r)
    hx, vy = cols   # x bars (horizontal), y bars (vertical), as errorbar(xerr=, yerr=) draws them
    hseg = [np.array([[s[0][0], r[i]], [s[1][0], r[i]]]) for i, s in enumerate(hx.get_segments())]
    vseg = [np.array([[cen[i], r[i] - e[i]], [cen[i], r[i] + e[i]]]) for i in range(len(r))]
    hx.set_segments(hseg); vy.set_segments(vseg)
    for cp in caps:   # x caps sit at the point's height; y caps at the ends of the vertical bar
        y0 = np.asarray(cp.get_ydata(), float)
        if cp.get_marker() == "|":
            cp.set_ydata(r)
        else:
            cp.set_ydata(np.where(y0 < r_old, r - e, r + e))
    refs = [ln for ln in bot.lines if ln is not line and not ln.get_transform().contains_branch_seperately(bot.transData)[0]]
    if len(refs) != 1:
        raise SystemExit(f"pubratio: {stem}: {len(refs)} reference lines in the lower panel")
    refs[0].set_color(pub[0].get_markerfacecolor() if to_rgba(pub[0].get_markerfacecolor())[3] > 0
                      else pub[0].get_markeredgecolor())
    if bot.get_ylabel() != OLD_Y:
        raise SystemExit(f"pubratio: {stem}: lower label {bot.get_ylabel()!r}")
    bot.set_ylabel(NEW_Y)
    # the longer label overruns the short lower panel and meets the upper panel's label in the same column: the upper
    # label moves up by the overlap plus 2 px, its x unchanged (a text position only; no datum of the upper panel moves)
    fig.canvas.draw(); rend = fig.canvas.get_renderer()
    ul, ll = top.yaxis.label, bot.yaxis.label
    ub, lb = ul.get_window_extent(rend), ll.get_window_extent(rend)
    shift = lb.y1 + 2 - ub.y0 if (lb.x0 < ub.x1 and ub.x0 < lb.x1) else 0.0
    moved = 0.0
    if shift > 0:
        ta = top.get_window_extent(rend)
        cx, cy = (ub.x0 + ub.x1) / 2, (ub.y0 + ub.y1) / 2 + shift
        x, y = (cx - ta.x0) / ta.width, (cy - ta.y0) / ta.height
        for _ in range(3):   # set_label_coords anchors by the label's alignment: correct until the box centre is (cx, cy)
            top.yaxis.set_label_coords(x, y); fig.canvas.draw()
            b = ul.get_window_extent(rend)
            x += (cx - (b.x0 + b.x1) / 2) / ta.width; y += (cy - (b.y0 + b.y1) / 2) / ta.height
        top.yaxis.set_label_coords(x, y); fig.canvas.draw()
        moved = shift
    ub, lb = ul.get_window_extent(rend), ll.get_window_extent(rend)
    if lb.overlaps(ub) or ub.y1 > fig.bbox.height or lb.y0 < 0:
        raise SystemExit(f"pubratio: {stem}: the axis labels still meet or leave the canvas ({ub.bounds}, {lb.bounds})")
    lo, hi = float(np.min(r - e)), float(np.max(r + e))
    ylim = tuple(bot.get_ylim())
    half = 0.05 * np.ceil((max(1 - lo, hi - 1) + 0.02) / 0.05 - 1e-9)
    bot.set_ylim(1 - half, 1 + half)
    # ticks inside the range, so the top one does not meet the upper panel's 0 at the joint
    bot.set_yticks([1 - half / 2, 1.0, 1 + half / 2], [f"{1 - half / 2:.2f}", "1.00", f"{1 + half / 2:.2f}"])
    if top_state(top) != before_top:
        raise SystemExit(f"pubratio: {stem}: the upper panel changed")
    chk = {"top": check_fig(top, edges), "ratio": check_fig(bot, edges)}
    # the upper panel's prior/prediction are steps on the edges, the points markers at the centres: both must pass
    if chk["top"] or chk["ratio"]:
        raise SystemExit(f"pubratio: {stem}: edge check fails: {chk}")
    if not np.array_equal(np.asarray(line.get_ydata(), float), r):
        raise SystemExit(f"pubratio: {stem}: the new points are not f/p")
    DONE[stem] = {"edges": edges.tolist(), "omnifold": f.tolist(), "omnifold_bar": yerr_f.tolist(),
                  "published": p.tolist(), "prior": t.tolist(), "ratio_to_prior_before": r_old.tolist(),
                  "ratio_to_published": r.tolist(), "ratio_bar": e.tolist(), "ylim_before": list(ylim),
                  "ylim_after": list(bot.get_ylim()), "upper_label_moved_px": moved, "edge_check_after": chk, "label": [OLD_Y, NEW_Y]}


def wrapped(self, fname, *a, **k):
    stem = Path(str(fname)).name.split(".")[0]
    if stem in PROJ and stem not in DONE:
        fix(self, stem)
    return _save(self, fname, *a, **k)


_save = ct._inner
ct._inner = wrapped          # compose_fig2_edges.py wraps this in turn, so its edge fix runs first
argv = sys.argv[1:]
sys.argv = [str(FIGFIX), *argv]
runpy.run_path(str(FIGFIX), run_name="__main__")
if set(DONE) != set(PROJ):
    raise SystemExit(f"pubratio: redrew {sorted(DONE)}, not both projections")
(Path(argv[2]) / "compose_fig2_pubratio.json").write_text(json.dumps(DONE, indent=1) + "\n")
print(f"[compose_fig2_pubratio] lower panels redrawn as OmniFold / published in {len(DONE)} figures")
