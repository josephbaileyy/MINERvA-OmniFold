#!/usr/bin/env python3
"""Fig. 2 (fig:xsec: MEFHC_5iter_xsec_proj_pt, _proj_pz) with the published Tune v1 prediction drawn on the
projection's own bin edges (Joseph's request, relayed by the director on 2026-11-20, item (b)).

usage (exactly as compose_tier2.py: under note-figstyle-20261117/tools/remap_anc.py, optionally under
capture_palette.py, in the tier-2 ROOT environment):
  python3 remap_anc.py <anc dir> compose_fig2_edges.py <xsec.root> <anc dir> <out dir>

The fault: compose_tier2.py adds Fig. 13's "Tune v1: published prediction" line to the projections "as drawn". That
line is compare_to_models.py's ax.step(ctr, y, where="mid") through the bin centres. With unequal bins a mid-step
changes value half-way between neighbouring centres, not at the bin edges, and it starts and ends at the first and last
centres. So the drawn steps do not line up with the bins (p_T: the step between the 2.0 and 3.5 centres changes at 2.75,
where the bin edge is 2.5). The values are per bin and are not touched.

compose_tier2.py runs unchanged (its main(): the four producers, then the composition). Only its final save is wrapped,
as compose_slices_markers.py wraps it. Before each projection figure is saved:
  1. The projection's edges are read from its own prior histogram (the StepPatch labelled ct.TUNE, which
     plot_2d_cross_section.py draws on the result's binning).
  2. The edge check (check_edges) runs on the figure as composed. It must FAIL there, on the published-prediction line
     only, or the run stops. This shows the check detects the fault it guards against.
  3. The published-prediction line keeps its object, style, label, z-order and y values. Only its drawing changes, to
     drawstyle "steps-post" on the edges: x = the n + 1 edges, y = the n bin values plus the last value repeated
     (the post-step convention). Before the change, its x must equal the bin centres (one value per bin, the bins
     paired one to one), or the run stops.
  4. check_edges runs again and must PASS for both axes (the upper panel and the ratio).
check_edges(ax, edges): every Line2D, StepPatch and errorbar container that draws data in the axes shares the
projection's edges. A StepPatch has exactly those edges. An errorbar's points are at the bin centres, and its x half-
widths, if any, are the half bin widths. A line drawn as steps (visible line, drawstyle steps-*) puts its value
changes and its ends exactly on the edges. A line drawn without steps, or only as markers, has each x on an edge or a
centre. A horizontal reference line spanning the axes (x in axes coordinates) is exempt.
Nothing else changes: the slice figures are saved as compose_tier2 saves them (not installed from this run).
Writes <out>/compose_fig2_edges.json (the edges, the check results before and after, the replaced line's values).
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
sys.path.insert(0, str(REPO / "docs/orchestration/state/2d-closeout/stageF/methods/note-figpass-20261119/tools"))
import compose_tier2 as ct  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import StepPatch  # noqa: E402

PROJ = ("MEFHC_5iter_xsec_proj_pt", "MEFHC_5iter_xsec_proj_pz")
TOL = 1e-12
DONE = {}


def close(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return a.shape == b.shape and bool(np.all(np.abs(a - b) <= TOL * np.maximum(1.0, np.abs(b))))


def on_grid(x, grid):
    x = np.asarray(x, float)
    return bool(np.all(np.min(np.abs(x[:, None] - grid[None, :]), axis=1) <= TOL * np.maximum(1.0, np.abs(x))))


def step_boundaries(x, drawstyle):
    """Where a visible steps-* line changes value, and its two ends, from its x data."""
    x = np.asarray(x, float)
    if drawstyle == "steps-mid":
        return np.concatenate([[x[0]], 0.5 * (x[:-1] + x[1:]), [x[-1]]])
    return x   # steps / steps-pre / steps-post: the changes are at the x values themselves


def check_edges(ax, edges):
    """Problems (strings) with any data series in ax not sharing the edges; empty if all share them."""
    edges = np.asarray(edges, float)
    cen, half = 0.5 * (edges[:-1] + edges[1:]), 0.5 * np.diff(edges)
    grid = np.concatenate([edges, cen])
    bad = []
    in_eb = set()
    for c in ax.containers:
        if not hasattr(c, "has_xerr"):
            continue
        x, _, xerr, _, cont = ct.eb(ax, c.get_label())
        in_eb.update(id(a) for a in cont.get_children())
        if not close(x, cen):
            bad.append(f"errorbar {c.get_label()!r}: points not at the bin centres")
        if xerr is not None and not close(xerr, half):
            bad.append(f"errorbar {c.get_label()!r}: x half-widths are not the half bin widths")
    for p in ax.patches:
        if isinstance(p, StepPatch) and not close(p.get_data().edges, edges):
            bad.append(f"StepPatch {p.get_label()!r}: edges differ")
    for ln in ax.lines:
        if id(ln) in in_eb or not ln.get_transform().contains_branch_seperately(ax.transData)[0]:
            continue   # an errorbar's own artists, or a reference line spanning the axes in x
        x = np.asarray(ln.get_xdata(), float)
        if x.size == 0:
            continue
        visible_line = ln.get_linestyle() not in ("None", "none", "", " ")
        ds = ln.get_drawstyle()
        if visible_line and ds.startswith("steps"):
            b = step_boundaries(x, ds)
            if not on_grid(b, edges) or not (close(b.min(), edges[0]) and close(b.max(), edges[-1])):
                bad.append(f"line {ln.get_label()!r}: {ds} steps change or end off the bin edges")
        elif not on_grid(x, grid):
            bad.append(f"line {ln.get_label()!r}: x values off the bin edges and centres")
    return bad


def fix(fig, stem):
    top, bot = fig.axes[0], fig.axes[1]
    prior = [p for p in top.patches if isinstance(p, StepPatch) and p.get_label() == ct.TUNE]
    if len(prior) != 1:
        raise SystemExit(f"edges: {stem}: {len(prior)} prior histograms")
    edges = np.asarray(prior[0].get_data().edges, float)
    cen = 0.5 * (edges[:-1] + edges[1:])
    before = {"top": check_edges(top, edges), "ratio": check_edges(bot, edges)}
    if before["ratio"] or len(before["top"]) != 1 or repr(ct.ANC_NEW) not in before["top"][0]:
        raise SystemExit(f"edges: {stem}: the check before the fix should flag the published-prediction line only; "
                         f"it gave {before}")
    anc = [ln for ln in top.lines if ln.get_label() == ct.ANC_NEW]
    if len(anc) != 1:
        raise SystemExit(f"edges: {stem}: {len(anc)} published-prediction lines")
    ln = anc[0]
    x0, y = np.asarray(ln.get_xdata(), float), np.asarray(ln.get_ydata(), float)
    if not close(x0, cen) or y.size != cen.size or ln.get_drawstyle() != "steps-mid":
        raise SystemExit(f"edges: {stem}: the published-prediction line is not one steps-mid value per bin centre")
    ln.set_drawstyle("steps-post")
    ln.set_data(edges, np.append(y, y[-1]))
    after = {"top": check_edges(top, edges), "ratio": check_edges(bot, edges)}
    if after["top"] or after["ratio"]:
        raise SystemExit(f"edges: {stem}: the edge check fails after the fix: {after}")
    if not np.array_equal(np.asarray(ln.get_ydata(), float)[:-1], y):
        raise SystemExit(f"edges: {stem}: the published-prediction values changed")
    DONE[stem] = {"edges": edges.tolist(), "check_before": before, "check_after": after,
                  "published_prediction_values": y.tolist(), "drawn_x_before": x0.tolist(),
                  "drawn_x_after": edges.tolist()}


def wrapped(self, fname, *a, **k):
    stem = Path(str(fname)).name.split(".")[0]
    if stem in PROJ and stem not in DONE:
        fix(self, stem)
    return _save(self, fname, *a, **k)


_save = ct._inner
ct._inner = wrapped
ct.main()
if set(DONE) != set(PROJ):
    raise SystemExit(f"edges: fixed {sorted(DONE)}, not both projections")
out = Path(sys.argv[3])
(out / "compose_fig2_edges.json").write_text(json.dumps(DONE, indent=1) + "\n")
print(f"[compose_fig2_edges] redrew the published prediction on the projection edges in {len(DONE)} figures; "
      f"edge check: failed before on that line only, passes after on both axes")
