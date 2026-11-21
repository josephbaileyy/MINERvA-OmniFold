"""Bin-edge checks for stepped series (note-stepedges-20261121; the Fig. 2 check_edges, note-figfix-20261120, made
general: no compose_tier2 dependency).

check_edges(ax, edges, tick_labels=None) returns problems (strings), empty if every data series in ax shares the edges:
- a line with a visible line style and a steps drawstyle: the x of its drawn (stepped) path, the points where it
  turns, must all lie on the edges, and the path must start at edges[0] and end at edges[-1] (full-width end bins);
- a line with no visible line style (markers only; a steps drawstyle draws nothing there and matplotlib puts the
  markers on the data points): its points must be at the bin centres;
- any other line in data x: its points must be on the edges or the centres;
- lines whose x is not in data coordinates (axhline and the like) are exempt;
- with tick_labels: the axis's ticks are at the edges and read tick_labels.
"""
import numpy as np
from matplotlib.cbook import STEP_LOOKUP_MAP


def close(a, b, tol=1e-9):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return a.shape == b.shape and bool(np.all(np.abs(a - b) <= tol * max(1.0, float(np.max(np.abs(b))) if b.size else 1.0)))


def on_grid(x, grid, tol=1e-9):
    x, grid = np.asarray(x, float), np.asarray(grid, float)
    return bool(np.all(np.min(np.abs(x[:, None] - grid[None, :]), axis=1) <= tol * max(1.0, float(np.max(np.abs(grid))))))


def drawn_x(ln):
    """x of the path matplotlib draws for the line (its drawstyle applied)."""
    x = np.asarray(ln.get_xdata(), float)
    y = np.asarray(ln.get_ydata(), float)
    ds = ln.get_drawstyle()
    return np.asarray(STEP_LOOKUP_MAP[ds](x, y)[0], float) if ds in STEP_LOOKUP_MAP else x


def visible(ln):
    return ln.get_linestyle() not in ("None", "none", "", " ")


def check_edges(ax, edges, tick_labels=None):
    edges = np.asarray(edges, float)
    cen = 0.5 * (edges[:-1] + edges[1:])
    bad = []
    for ln in ax.lines:
        if not ln.get_transform().contains_branch_seperately(ax.transData)[0]:
            continue
        x = np.asarray(ln.get_xdata(), float)
        if x.size == 0:
            continue
        ds = ln.get_drawstyle()
        if visible(ln) and ds.startswith("steps"):
            b = drawn_x(ln)
            if not on_grid(b, edges) or not (close(b.min(), edges[0]) and close(b.max(), edges[-1])):
                bad.append(f"line {ln.get_label()!r}: {ds} turns or ends off the bin edges")
        elif not visible(ln):
            if not on_grid(x, cen):
                bad.append(f"markers {ln.get_label()!r}: points not at the bin centres")
        elif not on_grid(x, np.concatenate([edges, cen])):
            bad.append(f"line {ln.get_label()!r}: x values off the bin edges and centres")
    if tick_labels is not None:
        t = np.asarray(ax.get_xticks(), float)
        lab = [s.get_text() for s in ax.get_xticklabels()]
        if not close(t, edges):
            bad.append(f"ticks at {t.tolist()}, not at the edges")
        elif lab != list(tick_labels):
            bad.append(f"tick labels {lab}, want {list(tick_labels)}")
    return bad
