"""The note palette pass's figure edits, shared by its recipes (palette_family4.py, palette_run.py).

apply(fig, name) makes, on a drawn figure named by its saved file's stem, every edit the record declares, in order:
1. recolour: each data artist's colours (a line's colour and marker face and edge; a collection's and a patch's face
   and edge) whose RGB recolour.tsv maps for that figure take the identity's colour (note_palette.palette_table()),
   each keeping its own alpha; every other colour stays. All of an artist's colours are read before any is set (a
   marker colour left "auto" follows the line's), and a patch's artist alpha is cleared first, so that it cannot
   replace a colour's own alpha. This is what fig-restyle-20261031's compare.py --recolour --palette requires;
2. restyle: each line restyle.tsv names (figure, colour, linestyle, marker) takes styles.tsv's linestyle and marker;
3. hatches: each patch hatches.tsv names (figure, "face" or "edge", its colour before the recolour) takes that hatch
   ("-" for none);
4. drop_titles.tsv: the figure title cleared, the axes stretched into its height;
5. text only: the note's notation (E_{\\rm avail}, p_\\parallel for p_z) and text_fixes.tsv's figure-specific
   replacements (figure, old, new; each must be found in that figure) on axis labels, titles, figure texts and every
   artist's and container's own label; each axes legend rebuilt frameless from its own artists, in its own order and
   place (a legend copies its handles' properties when made); each y axis's "1e-38"-style offset moved into its
   label as 10^n before the unit ("(...)", the last " (" of the label), or kept as a math-text x10^n where the
   axes has no labelled unit.
No datum changes: each recipe's arm-1 capture is checked against its arm 0 on the colour- and style-free hash.
"""
from pathlib import Path

from matplotlib.collections import Collection
from matplotlib.colors import to_hex, to_rgba, to_rgba_array
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.text import Text

HERE = Path(__file__).resolve().parent
REC = HERE.parent
ROOT = HERE.parents[7]
import sys  # noqa: E402

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import note_palette as npal  # noqa: E402


def table(name):
    p = REC / name
    if not p.exists():
        return []
    rows = [ln.split("\t") for ln in p.read_text().splitlines() if ln.strip() and not ln.startswith("#")]
    return rows[1:]


PAL = dict(npal.palette_table())
RECOLOUR = {(r[0], r[1].upper()): r[2] for r in table("recolour.tsv")}
STYLES = {r[0]: (r[1], r[2]) for r in table("styles.tsv")}
RESTYLE = {(r[0], r[1].upper(), r[2], r[3]): r[4] for r in table("restyle.tsv")}
HATCHES = {(r[0], r[1], r[2].upper()): (None if r[3] == "-" else r[3]) for r in table("hatches.tsv")}
TEXT_FIXES = {}
for r in table("text_fixes.tsv"):
    TEXT_FIXES.setdefault(r[0], []).append((r[1], r[2]))
DROP_TITLES = {r[0] for r in table("drop_titles.tsv")}   # figures whose figure title (suptitle) the caption carries
GLOBAL_FIXES = (("E_{avail}", r"E_{\rm avail}"), ("p_z", r"p_\parallel"))
for (fig, ident) in [((k[0]), v) for k, v in RECOLOUR.items()]:
    if ident not in PAL:
        raise SystemExit(f"recolour.tsv: {fig} maps to {ident!r}, which note_palette does not name")


def new_colour(fig, rgba):
    rgba = to_rgba(rgba)
    ident = RECOLOUR.get((fig, to_hex(rgba).upper()[:7]))
    return rgba if ident is None else to_rgba(PAL[ident], rgba[3])


def recolour_artist(a, name):
    """One artist's colours (and line style, hatch) as the record's tables give them."""
    if isinstance(a, Line2D):
        c0 = to_rgba(a.get_color(), a.get_alpha())
        mfc0, mec0 = to_rgba(a.get_markerfacecolor()), to_rgba(a.get_markeredgecolor())
        before = (to_hex(c0).upper()[:7], str(a.get_linestyle()), str(a.get_marker()))
        a.set_color(new_colour(name, c0))
        a.set_markerfacecolor(new_colour(name, mfc0))
        a.set_markeredgecolor(new_colour(name, mec0))
        ident = RESTYLE.get((name,) + before)
        if ident is not None:
            ls, mk = STYLES[ident]
            a.set_linestyle(ls)
            a.set_marker(mk)
    elif isinstance(a, Collection):
        fc = [new_colour(name, c) for c in to_rgba_array(a.get_facecolors())]
        ec = [new_colour(name, c) for c in to_rgba_array(a.get_edgecolors())]
        if a.get_array() is None:   # a mapped collection keeps its colormap
            a.set_facecolor(fc)
        a.set_edgecolor(ec)
    elif isinstance(a, Patch):
        fc, ec = to_rgba(a.get_facecolor()), to_rgba(a.get_edgecolor())
        f0, e0 = to_hex(fc).upper()[:7], to_hex(ec).upper()[:7]
        a.set_alpha(None)
        a.set_facecolor(new_colour(name, fc))
        a.set_edgecolor(new_colour(name, ec))
        for key in ((name, "face", f0), (name, "edge", e0)):
            if key in HATCHES:
                a.set_hatch(HATCHES[key])


def recolour(fig, name):
    for ax in fig.axes:
        skip = {id(ax.patch)} | {id(s) for s in ax.spines.values()}
        for a in ax.get_children():
            if id(a) not in skip:
                recolour_artist(a, name)


def fix_text(s, name, used):
    for a, b in GLOBAL_FIXES:
        s = s.replace(a, b)
    for i, (a, b) in enumerate(TEXT_FIXES.get(name, [])):
        if a in s:
            used.add(i)
            s = s.replace(a, b)
    return s


def relabel(fig, name):
    used = set()
    for ax in fig.axes:
        ax.set_xlabel(fix_text(ax.get_xlabel(), name, used))
        ax.set_ylabel(fix_text(ax.get_ylabel(), name, used))
        ax.set_title(fix_text(ax.get_title(), name, used))
        for a in list(ax.get_children()) + list(ax.containers):
            lab = a.get_label() if hasattr(a, "get_label") else None
            if isinstance(lab, str) and lab and not lab.startswith("_"):
                a.set_label(fix_text(lab, name, used))
            if isinstance(a, Text) and a.get_text():
                a.set_text(fix_text(a.get_text(), name, used))
        leg = ax.get_legend()
        if leg is not None:
            for t in leg.get_texts():
                t.set_text(fix_text(t.get_text(), name, used))
    for t in fig.texts:
        t.set_text(fix_text(t.get_text(), name, used))
    for leg in fig.legends:
        for t in leg.get_texts():
            t.set_text(fix_text(t.get_text(), name, used))
    unused = [TEXT_FIXES[name][i] for i in range(len(TEXT_FIXES.get(name, []))) if i not in used]
    if unused:
        raise SystemExit(f"text_fixes.tsv: {name}: not found in the figure: {unused}")


def _anchor(leg):
    """The legend's bbox_to_anchor as given (its bounds and the transform they were given in), so that the rebuilt
    legend applies that transform once; {} if it had none."""
    b = leg._bbox_to_anchor
    if b is None or not hasattr(b, "_bbox"):
        return {}
    return {"bbox_to_anchor": b._bbox.bounds, "bbox_transform": b._transform}


def in_place(leg, fig):
    """A legend built from proxy handles keeps its keys, recoloured and restyled by the same tables, frameless."""
    name = fig._note_palette_name
    for h in leg.legend_handles:
        if h is not None:
            recolour_artist(h, name)
    leg.set_frame_on(False)


def rebuild_legends(fig):
    for ax in fig.axes:
        leg = ax.get_legend()
        if leg is None:
            continue
        want = [t.get_text() for t in leg.get_texts()]
        h, lab = ax.get_legend_handles_labels()
        pick = dict(zip(lab, h))
        if any(x not in pick for x in want):   # proxy handles, not axes artists: edit the legend's own keys
            in_place(leg, fig)
            continue
        kw = dict({"loc": leg._loc, "frameon": False, "ncol": leg._ncols}, **_anchor(leg))
        leg.remove()
        ax.legend([pick[x] for x in want], want, **kw)
    for leg in list(fig.legends):   # a figure legend: its entries from every axes' labelled artists
        want = [t.get_text() for t in leg.get_texts()]
        pick = {}
        for ax in fig.axes:
            h, lab = ax.get_legend_handles_labels()
            for x, y in zip(lab, h):
                pick.setdefault(x, y)
        if any(x not in pick for x in want):
            in_place(leg, fig)
            continue
        kw = {"loc": leg._loc, "frameon": False, "ncol": leg._ncols, **_anchor(leg), "fontsize": leg._fontsize,
              "handlelength": leg.handlelength, "handletextpad": leg.handletextpad, "columnspacing": leg.columnspacing,
              "borderaxespad": leg.borderaxespad, "markerscale": leg.markerscale}
        leg.remove()
        fig.legend([pick[x] for x in want], want, **kw)


def power_of_ten(fig, check_fit=True):
    from matplotlib.ticker import FuncFormatter, ScalarFormatter
    fig.canvas.draw()
    for ax in fig.axes:
        off = ax.yaxis.get_offset_text().get_text().replace("−", "-")
        if not off.startswith("1e"):
            continue
        e = int(off[2:])
        lab = ax.get_ylabel()
        placed = False
        if lab and " (" in lab:
            old_fmt = ax.yaxis.get_major_formatter()
            ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _p, e=e: f"{v / 10.0 ** e:g}"))
            i = lab.rindex(" (")
            for cand in (lab[:i] + "\n(" + rf"$10^{{{e}}}$ " + lab[i + 2:],     # the unit on its own line
                         lab[:i] + " (" + rf"$10^{{{e}}}$ " + lab[i + 2:]):     # or on one line
                ax.set_ylabel(cand)
                if not check_fit:   # the caller lays the figure out again afterwards (palette_family4)
                    placed = True
                    break
                fig.canvas.draw()
                bb, fb = ax.yaxis.label.get_window_extent(), fig.bbox
                if bb.x0 >= 0 and bb.y0 >= 0 and bb.x1 <= fb.width and bb.y1 <= fb.height:
                    placed = True
                    break
            if not placed:   # the producer's layout has no room for a longer label: keep it, and the factor as x10^n
                ax.set_ylabel(lab)
                ax.yaxis.set_major_formatter(old_fmt)
        if not placed:
            f = ScalarFormatter(useMathText=True)
            f.set_powerlimits((0, 0))
            ax.yaxis.set_major_formatter(f)


def drop_title(fig, name):
    """drop_titles.tsv: the figure's suptitle is cleared and every axes is stretched upward into the freed height
    (bottoms fixed, tops raised by the title's height in figure fraction, at most to 0.98), so no blank band is left.
    Text and layout only."""
    if name not in DROP_TITLES:
        return
    st = getattr(fig, "_suptitle", None)
    if st is None or not st.get_text().strip():
        raise SystemExit(f"drop_titles.tsv: {name} has no figure title")
    fig.canvas.draw()
    h = st.get_window_extent().transformed(fig.transFigure.inverted()).height
    st.set_text("")
    boxes = [ax.get_position() for ax in fig.axes]
    bottom, top = min(b.y0 for b in boxes), max(b.y1 for b in boxes)
    new_top = min(0.98, top + h)
    k = (new_top - bottom) / (top - bottom)
    for ax, b in zip(fig.axes, boxes):
        ax.set_position([b.x0, bottom + (b.y0 - bottom) * k, b.width, b.height * k])


def legend_entries(fig):
    legs = list(fig.legends) + [ax.get_legend() for ax in fig.axes if ax.get_legend() is not None]
    return sorted(t.get_text() for leg in legs for t in leg.get_texts())


def apply(fig, name, check_fit=True):
    """Every declared edit, in order; refuses if a legend entry is lost."""
    fig._note_palette_name = name
    recolour(fig, name)
    relabel(fig, name)
    drop_title(fig, name)
    before = legend_entries(fig)
    rebuild_legends(fig)
    power_of_ten(fig, check_fit)
    if legend_entries(fig) != before:
        raise SystemExit(f"{name}: legend entries {before} became {legend_entries(fig)}")
