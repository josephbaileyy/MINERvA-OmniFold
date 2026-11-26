#!/usr/bin/env python3
"""Fig. 5 (fig:q3excess, q3_excess_projection): the installed recipe, then two presentation fixes (Joseph, via the
director, 2026-11-21).

usage: Q3FIX_JSON=<record.json> python3 compose_q3_labels.py <producer> [args...]

The installed file is note-figpass-20261119's arm 1: the unchanged producer, run under that record's layout_run.py
(palette_lib.apply, then layout_lib.apply, at the figure's first save). This tool runs the same, and then, before
anything is written:
(a) each in-cell value label of the ratio map takes the colour, white or black, that has the higher WCAG contrast
    against its cell's colour (relative luminance from the drawn image's own colormap and norm). Before the fix every
    label is black, which vanishes on the darkest cells. The color scale is not touched.
(b) the two lower panels' y-axis label "unfolded / GENIE prior" reads "unfolded / MINERvA Tune v1 prior", the caption's name
    for the same prior (GENIE 2.12.6 + MINERvA Tune v1; the producer's weights w_truth).
Checks (each failure stops the run): every label sits on one cell centre and prints that cell's value to 2 decimals;
there is one label per finite cell; every label is black before the fix; the image's array, colormap, norm limits and
every text's string, position and size are the same after the fix, apart from (b)'s two strings; exactly two texts
carried the old label. The per-cell record (value, cell colour, luminance, label colour) goes to $Q3FIX_JSON.
"""
import hashlib
import json
import os
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
METHODS = HERE.parents[1]
sys.path.insert(0, str(METHODS / "note-figpass-20261119" / "tools"))
sys.path.insert(0, str(METHODS / "note-figstyle-20261117" / "tools"))
import layout_lib  # noqa: E402
import palette_lib  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import numpy as np  # noqa: E402
from matplotlib.colors import to_rgba  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

STEM = "q3_excess_projection"
OLD_Y, NEW_Y = "unfolded / GENIE prior", "unfolded /\nMINERvA Tune v1 prior"
WHITE, BLACK = "white", "black"


def luminance(rgba):
    """WCAG 2.x relative luminance of an sRGB colour."""
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgba[:3]]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def label_colour(L):
    """The one of white (L=1) and black (L=0) with the higher contrast ratio against luminance L."""
    return WHITE if (1.0 + 0.05) / (L + 0.05) > (L + 0.05) / (0.0 + 0.05) else BLACK


def state(fig):
    """Every drawn text (string, position, size, colour) and the map image's data and scale."""
    im = fig.axes[0].get_images()[0]
    a = np.ma.filled(np.ma.asarray(im.get_array(), dtype=float), np.nan)
    texts = [(t.get_text(), tuple(map(float, t.get_position())), float(t.get_fontsize()), to_rgba(t.get_color()))
             for t in fig.findobj(lambda o: isinstance(o, matplotlib.text.Text)) if t.get_visible() and t.get_text()]
    return {"image": hashlib.sha256(a.tobytes()).hexdigest(), "cmap": im.cmap.name,
            "clim": (float(im.norm.vmin), float(im.norm.vmax), float(getattr(im.norm, "vcenter", np.nan))),
            "texts": texts}


def fix(fig):
    ax0 = fig.axes[0]
    ims = ax0.get_images()
    if len(ims) != 1:
        raise SystemExit(f"FAIL: the map axes holds {len(ims)} images, not 1")
    im = ims[0]
    if im.get_alpha() not in (None, 1, 1.0):
        raise SystemExit(f"FAIL: the map image has alpha {im.get_alpha()}; the cell colour would not be the cmap's")
    a = np.ma.filled(np.ma.asarray(im.get_array(), dtype=float), np.nan)
    before = state(fig)
    cells, seen = [], set()
    for t in ax0.texts:
        x, y = map(float, t.get_position())
        c, r = int(round(x)), int(round(y))
        if abs(x - c) > 1e-9 or abs(y - r) > 1e-9 or not (0 <= r < a.shape[0] and 0 <= c < a.shape[1]):
            raise SystemExit(f"FAIL: label {t.get_text()!r} at ({x}, {y}) is not on a cell centre")
        v = a[r, c]
        if not np.isfinite(v) or t.get_text() != f"{v:.2f}":
            raise SystemExit(f"FAIL: label {t.get_text()!r} at cell (row {r}, col {c}) but the cell holds {v!r}")
        if to_rgba(t.get_color()) != to_rgba(BLACK):
            raise SystemExit(f"FAIL: label {t.get_text()!r} is {t.get_color()!r} before the fix, not black")
        if (r, c) in seen:
            raise SystemExit(f"FAIL: two labels on cell (row {r}, col {c})")
        seen.add((r, c))
        rgba = tuple(float(u) for u in im.cmap(im.norm(v)))
        L = luminance(rgba)
        col = label_colour(L)
        t.set_color(col)
        cells.append({"row": r, "col": c, "label": t.get_text(), "value": float(v),
                      "cell_rgb": [round(u, 6) for u in rgba[:3]], "luminance": round(L, 6), "label_colour": col})
    nfin = int(np.isfinite(a).sum())
    if len(cells) != nfin:
        raise SystemExit(f"FAIL: {len(cells)} labels for {nfin} finite cells")
    hits = [t for t in fig.findobj(lambda o: isinstance(o, matplotlib.text.Text)) if t.get_text() == OLD_Y]
    owners = [A for A in fig.axes if A.yaxis.label in hits]
    if len(hits) != 2 or len(owners) != 2 or fig.axes.index(owners[0]) != 1 or fig.axes.index(owners[1]) != 2:
        raise SystemExit(f"FAIL: {len(hits)} texts read {OLD_Y!r} (owners {[fig.axes.index(A) for A in owners]}); "
                         "want exactly the y labels of axes 1 and 2")
    for A in owners:
        A.set_ylabel(NEW_Y)
    after = state(fig)
    # identity: the image and its scale are unchanged; texts differ only by (a)'s colours and (b)'s two strings
    for k in ("image", "cmap", "clim"):
        if before[k] != after[k]:
            raise SystemExit(f"FAIL: {k} changed: {before[k]} -> {after[k]}")
    if len(before["texts"]) != len(after["texts"]):
        raise SystemExit("FAIL: the number of drawn texts changed")
    label_ids = {id(t) for t in ax0.texts}
    allt = [t for t in fig.findobj(lambda o: isinstance(o, matplotlib.text.Text)) if t.get_visible() and t.get_text()]
    nstr = ncol = 0
    for t, b, f in zip(allt, before["texts"], after["texts"]):
        if b[1:3] != f[1:3]:
            raise SystemExit(f"FAIL: text {b[0]!r} moved or resized")
        if b[0] != f[0]:
            if (b[0], f[0]) != (OLD_Y, NEW_Y):
                raise SystemExit(f"FAIL: undeclared string change {b[0]!r} -> {f[0]!r}")
            nstr += 1
        if b[3] != f[3]:
            if id(t) not in label_ids:
                raise SystemExit(f"FAIL: text {b[0]!r} changed colour but is not a map label")
            ncol += 1
    if nstr != 2:
        raise SystemExit(f"FAIL: {nstr} string changes, want 2")
    nwhite = sum(c["label_colour"] == WHITE for c in cells)
    if ncol != nwhite:
        raise SystemExit(f"FAIL: {ncol} colour changes, but {nwhite} labels were set white")
    return {"cells": cells, "n_labels": len(cells), "n_white": nwhite, "n_black": len(cells) - nwhite,
            "string_changes": [[OLD_Y, NEW_Y, 2]], "image_sha256": before["image"], "cmap": before["cmap"],
            "clim_vmin_vmax_vcenter": list(before["clim"]), "n_texts": len(before["texts"]),
            "rule": "label white if contrast(white) > contrast(black) against the cell's WCAG relative luminance L, "
                    "i.e. 1.05/(L+0.05) > (L+0.05)/0.05"}


_inner = Figure.savefig
_rec = {}


def savefig(self, fname, *a, **k):
    if not getattr(self, "_note_q3fix_done", False) and (isinstance(fname, (str, bytes)) or hasattr(fname, "__fspath__")):
        name = Path(str(fname)).name.split(".")[0]
        if name != STEM:
            raise SystemExit(f"FAIL: saved figure {name!r}, this tool is for {STEM}")
        palette_lib.apply(self, name)
        layout_lib.apply(self, name)
        _rec.update(fix(self))
        out = os.environ.get("Q3FIX_JSON")
        if out:
            Path(out).write_text(json.dumps(_rec, indent=1) + "\n")
        self._note_q3fix_done = True
    return _inner(self, fname, *a, **k)


Figure.savefig = savefig
script, args = Path(sys.argv[1]).resolve(), sys.argv[2:]
sys.argv = [str(script), *args]
sys.path.insert(0, str(script.parent))
runpy.run_path(str(script), run_name="__main__")
