"""What a matplotlib figure draws, as arrays: the record behind DECLARATION.md §3 check 3.

collect(fig) walks every axes of the figure, colour-bar axes included, and keeps each data artist:
  - Line2D: its data (x, y), colour, marker face and edge colours, line style, marker and draw style;
  - a collection: offsets; for a LineCollection its segments; for a QuadMesh its coordinates; for any other collection
    drawn in data coordinates its path vertices and codes; its colour array, colour limits and colour map; its face and
    edge colours;
  - an image: its array and mask, extent, colour limits and colour map;
  - a patch drawn in data coordinates (bars, filled regions): its vertices in data coordinates, face and edge colours.
It skips text, ticks, spines, grid lines, legends and the axes background, and any patch or path not in data
coordinates. These are what a restyle may change. Each kept artist is one item. Its hash is sha256 over its kind and
each field's name and bytes, with numbers as contiguous float64 and a masked array as its data (masked entries NaN)
plus its mask. Labels, axes index and scale are written to the index for reading, but are not hashed.
A figure's record is the multiset of its items' hashes; compare.py compares two records.
RESTYLE AMENDMENT 1 adds, per item, "dhash" (the same hash with the colour fields left out: color, mfc, mec, face,
edge, cmap) and "colours" (those fields as hex strings), so that compare.py --recolour can hold the data bit for bit
while checking each series' colour against the palette; "gid" (a patch drawn by Axes.hist carries
"restyle-hist", set by capture.py); and items of kind "hist-input", one per Axes.hist call (capture.py), hashing the
values hist was given, which compare.py's named binning exception compares bit for bit."""
import hashlib
import json

import numpy as np
from matplotlib.collections import Collection, LineCollection, QuadMesh
from matplotlib.colors import to_rgba, to_rgba_array
from matplotlib.image import AxesImage
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.spines import Spine


def _num(x):
    if np.ma.isMaskedArray(x):
        return np.ascontiguousarray(np.ma.filled(x.astype(float), np.nan), dtype=np.float64), np.ma.getmaskarray(x)
    return np.ascontiguousarray(np.asarray(x, dtype=np.float64)), None


COLOUR_FIELDS = ("color", "mfc", "mec", "face", "edge", "cmap")


def _hex(v):
    a = np.atleast_2d(np.asarray(v, dtype=float))
    return ["#%02X%02X%02X%02X" % tuple(int(round(x * 255)) for x in r[:4]) for r in a] if a.size else []


def _item(kind, fields):
    h = hashlib.sha256(kind.encode())
    d = hashlib.sha256(kind.encode())
    arrays = {}
    for k in sorted(fields):
        v = fields[k]
        hs = (h,) if k in COLOUR_FIELDS else (h, d)
        for x in hs:
            x.update(b"\0" + k.encode() + b"\0")
        if isinstance(v, str):
            for x in hs:
                x.update(v.encode())
            continue
        a, m = _num(v)
        for x in hs:
            x.update(str(a.shape).encode() + a.tobytes())
        arrays[k] = a
        if m is not None:
            for x in hs:
                x.update(b"mask" + np.ascontiguousarray(m).tobytes())
            arrays[k + ".mask"] = m
    colours = {k: (fields[k] if isinstance(fields[k], str) else _hex(fields[k])) for k in fields if k in COLOUR_FIELDS}
    return h.hexdigest(), d.hexdigest(), colours, arrays


def _in_data(artist, ax):
    try:
        return artist.get_transform().contains_branch(ax.transData)
    except Exception:
        return False


def _cmap(a):
    c = getattr(a, "get_cmap", None)
    return c().name if c and c() is not None else ""


def _clim(a):
    return np.asarray(a.get_clim(), dtype=float) if a.get_array() is not None else np.zeros(0)


def items(fig):
    """Yield (kind, axes index, label, fields) for every data artist of fig."""
    for n, ax in enumerate(fig.axes):
        skip = {id(ax.patch)} | {id(s) for s in ax.spines.values()}
        if ax.get_legend() is not None:
            skip.add(id(ax.get_legend()))
        for a in ax.get_children():
            if id(a) in skip or isinstance(a, Spine) or not a.get_visible():
                continue
            if isinstance(a, Line2D):
                yield "line", n, a.get_label(), {
                    "xy": a.get_xydata(), "color": to_rgba(a.get_color(), a.get_alpha()),
                    "mfc": to_rgba(a.get_markerfacecolor()), "mec": to_rgba(a.get_markeredgecolor()),
                    "linestyle": str(a.get_linestyle()), "marker": str(a.get_marker()),
                    "drawstyle": str(a.get_drawstyle())}, a.get_gid()
            elif isinstance(a, AxesImage):
                yield "image", n, a.get_label(), {
                    "array": a.get_array(), "extent": a.get_extent(), "clim": _clim(a), "cmap": _cmap(a)}, a.get_gid()
            elif isinstance(a, Collection):
                f = {"offsets": a.get_offsets(), "face": to_rgba_array(a.get_facecolors()),
                     "edge": to_rgba_array(a.get_edgecolors()), "cmap": _cmap(a)}
                if a.get_array() is not None:
                    f["array"], f["clim"] = a.get_array(), _clim(a)
                if isinstance(a, LineCollection):
                    segs = a.get_segments()
                    f["segments"] = np.concatenate([np.asarray(s, float) for s in segs]) if segs else np.zeros((0, 2))
                    f["segment_lengths"] = np.array([len(s) for s in segs], float)
                elif isinstance(a, QuadMesh):
                    f["coordinates"] = a.get_coordinates()
                elif _in_data(a, ax):
                    paths = a.get_paths()
                    f["vertices"] = np.concatenate([p.vertices for p in paths]) if paths else np.zeros((0, 2))
                    f["codes"] = np.concatenate([p.codes if p.codes is not None else np.zeros(len(p.vertices))
                                                 for p in paths]) if paths else np.zeros(0)
                yield type(a).__name__, n, a.get_label(), f, a.get_gid()
            elif isinstance(a, Patch) and _in_data(a, ax):
                v = a.get_patch_transform().transform(a.get_path().vertices)
                yield "patch", n, a.get_label(), {
                    "vertices": v, "face": to_rgba(a.get_facecolor()), "edge": to_rgba(a.get_edgecolor())}, a.get_gid()


def hist_inputs(fig):
    """(kind, axes, label, fields, gid) for each Axes.hist call capture.py recorded on the figure."""
    for n, x in getattr(fig, "_restyle_hist_inputs", []):
        yield "hist-input", n, "", {"values": x}, "restyle-hist"


def collect(fig):
    arrays, index = {}, []
    for i, (kind, n, label, fields, gid) in enumerate(list(items(fig)) + list(hist_inputs(fig))):
        h, dh, colours, arr = _item(kind, fields)
        for k, v in arr.items():
            arrays[f"i{i}.{k}"] = v
        ax = fig.axes[n] if n is not None else None
        index.append({"i": i, "kind": kind, "axes": n, "label": str(label), "hash": h, "dhash": dh,
                      "colours": colours, "gid": gid,
                      "scale": [ax.get_xscale(), ax.get_yscale()] if ax is not None else None})
    return arrays, index


def texts(fig):
    """(font size in pt, text) for every visible, non-empty text the figure draws: figure and axes texts, axis labels,
    tick labels, offset texts, legend texts. Not hashed: a restyle changes these. textsize.py scales them to print."""
    out = []
    for t in fig.findobj(lambda a: hasattr(a, "get_text") and hasattr(a, "get_fontsize")):
        try:
            s = t.get_text()
        except TypeError:
            continue
        shown = t.get_visible() and (t.axes is None or t.axes.get_visible())
        if isinstance(s, str) and s.strip() and shown:
            out.append((float(t.get_fontsize()), s.replace("\t", " ").replace("\n", " ")))
    return out


def write(stem, arrays, index):
    stem = str(stem)
    np.savez(stem + ".npz", **arrays)
    with open(stem + ".json", "w") as f:
        json.dump(index, f, indent=1)
