#!/usr/bin/env python3
"""In-panel text against drawn data (RESTYLE AMENDMENT 1): does any text sit on a data line, error bar or marker?

overlaps(fig), called by capture.py after a save (the figure is drawn): for each text in the figure's and its axes'
texts (ax.texts, fig.texts; tick labels, axis labels and legends are not in them), its window extent is tested against
every data artist of artists.items(fig) in display coordinates:
  - a line, its drawn path (and its markers' positions);
  - a LineCollection (error bars), each segment;
  - a PathCollection (scatter), each offset;
  - a patch, its outline.
A crossing or a point inside the text's box is an overlap. Images and meshes are behind the text by design and are not
tested.
usage: python3 -I overlap.py RUN_DIR [--figures a.png,b.png] [--gate]
Prints every overlap of the run's figures; with --gate, exits 1 if any of the named figures has one."""
import sys
from pathlib import Path

import numpy as np
from matplotlib.collections import LineCollection, PathCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.path import Path as MPath
from matplotlib.spines import Spine


def _hits_box(points, box, closed=False):
    if len(points) == 0:
        return False
    pts = np.asarray(points, float)
    if np.any(box.contains_points(pts) if hasattr(box, "contains_points") else
              ((pts[:, 0] >= box.x0) & (pts[:, 0] <= box.x1) & (pts[:, 1] >= box.y0) & (pts[:, 1] <= box.y1))):
        return True
    if len(pts) > 1:
        return MPath(pts).intersects_bbox(box, filled=False)
    return False


def _geometry(a, ax):
    """Display-coordinate point lists of a data artist."""
    if isinstance(a, Line2D):
        xy = a.get_transform().transform(a.get_xydata())
        return [xy] if a.get_linestyle() not in ("None", "none", "") else [xy[i:i + 1] for i in range(len(xy))]
    if isinstance(a, LineCollection):
        tr = a.get_transform()
        return [tr.transform(np.asarray(s, float)) for s in a.get_segments() if len(s)]
    if isinstance(a, PathCollection):
        off = a.get_offsets()
        return [a.get_offset_transform().transform(np.atleast_2d(o)) for o in off] if len(off) else []
    if isinstance(a, Patch) and not isinstance(a, Spine) and a is not ax.patch:
        return [a.get_transform().transform(a.get_path().vertices)]
    return []


def overlaps(fig):
    r = fig.canvas.get_renderer()
    texts = [(None, t) for t in fig.texts] + [(n, t) for n, ax in enumerate(fig.axes) for t in ax.texts]
    out = []
    for n, t in texts:
        if not t.get_visible() or not str(t.get_text()).strip():
            continue
        box = t.get_window_extent(r)
        axes = range(len(fig.axes)) if n is None else [n]
        for m in axes:
            ax = fig.axes[m]
            for a in ax.get_children():
                if not a.get_visible() or not isinstance(a, (Line2D, LineCollection, PathCollection, Patch)):
                    continue
                if isinstance(a, Spine) or a is ax.patch or a is ax.get_legend():
                    continue
                if any(_hits_box(g, box) for g in _geometry(a, ax)):
                    out.append((str(t.get_text()), m, type(a).__name__, str(a.get_label())))
    return out


def main():
    run = Path(sys.argv[1])
    want = None
    if "--figures" in sys.argv:
        want = set(sys.argv[sys.argv.index("--figures") + 1].split(","))
    bad = 0
    for p in sorted(run.glob("capture/*/*.overlaps.tsv")):
        fig = p.name[:-len(".overlaps.tsv")]
        if want is not None and fig not in want:
            continue
        rows = p.read_text().splitlines()[1:]
        bad += bool(rows)
        print(f"{'FAIL' if rows else 'ok  '} {fig}: {len(rows)} overlap(s)")
        for r in rows[:12]:
            print("       " + r)
    print("OVERLAP ::", "PASS" if not bad else f"FAIL ({bad} figure(s))")
    return 1 if (bad and "--gate" in sys.argv) else 0


if __name__ == "__main__":
    sys.exit(main())
