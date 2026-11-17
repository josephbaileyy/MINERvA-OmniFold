#!/usr/bin/env python3
"""Figs. 19-22 in the note palette (arm 1): the family-4 pickles, recoloured, then restyled as installed.

usage: python3 palette_family4.py <pickle dir> <out dir>    (matplotlib 3.10.8, the version the pickles were written by)

For each pinned pickle (note-figstyle-20261113/tools/restyle_family4.py's PINNED, loaded only through its load(), which
checks the sha256 before unpickling):
1. every colour of every data artist (a line's colour and marker faces and edges; a collection's and a patch's face
   and edge) whose RGB the record's recolour.tsv maps for that figure takes the identity's colour from note_palette,
   keeping its own alpha. Every other colour stays. This is exactly what fig-restyle-20261031's compare.py --recolour
   --palette requires of the arm-1 capture;
2. each line that restyle.tsv names (figure, colour, linestyle, marker) takes styles.tsv's linestyle and marker;
3. Fig. 20 only (mode_decomp_eavail_central): the four mode bars take their note_palette.MODES hatches, and the
   data - GENIE-CV gap bar loses its hatch, so it is a this-work outline (COMBINED-PLAN.md section 5(a));
4. text only: the axis labels and legend entries take the note's notation (E_{\\rm avail}, p_\\parallel for "p_z");
   each axes legend is rebuilt from its own labelled artists, in its own order and place, frameless, so that its
   keys show the new colours (a legend copies its handles' properties when it is made); each y axis's "1e-38"
   offset moves into its label as 10^n before the unit (an unlabelled axes keeps it as a math-text x10^n);
5. restyle_family4.restyle(), unchanged, sets the fonts and the printed size, as for the installed figures.
No datum changes: compare.py checks the arm-1 capture against arm 0 on the colour- and style-free hash.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import Collection  # noqa: E402
from matplotlib.colors import to_hex, to_rgba, to_rgba_array  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

HERE = Path(__file__).resolve().parent
REC = HERE.parent
ROOT = HERE.parents[7]
OLD = ROOT / "docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261113/tools"
sys.path[:0] = [str(OLD), str(ROOT)]
import restyle_family4 as rf4  # noqa: E402
import note_palette as npal  # noqa: E402

MODE_OF = {"#1F77B4": "QE", "#2CA02C": "RES", "#FF7F0E": "DIS", "#9467BD": "COH"}   # Fig. 20's producer colours


def table(name):
    rows = [ln.split("\t") for ln in (REC / name).read_text().splitlines() if ln.strip() and not ln.startswith("#")]
    return rows[1:]


PAL = dict(npal.palette_table())
RECOLOUR = {(r[0], r[1].upper()): r[2] for r in table("recolour.tsv")}
STYLES = {r[0]: (r[1], r[2]) for r in table("styles.tsv")}
RESTYLE = {(r[0], r[1].upper(), r[2], r[3]): r[4] for r in table("restyle.tsv")}


def new_colour(fig, rgba):
    rgba = to_rgba(rgba)
    ident = RECOLOUR.get((fig, to_hex(rgba).upper()[:7]))
    return rgba if ident is None else to_rgba(PAL[ident], rgba[3])


def recolour(fig, name):
    for ax in fig.axes:
        skip = {id(ax.patch)} | {id(s) for s in ax.spines.values()}
        for a in ax.get_children():
            if id(a) in skip:
                continue
            if isinstance(a, Line2D):
                # all three read before any is set: a marker colour left "auto" follows the line colour
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
                a.set_facecolor([new_colour(name, c) for c in to_rgba_array(a.get_facecolors())])
                a.set_edgecolor([new_colour(name, c) for c in to_rgba_array(a.get_edgecolors())])
            elif isinstance(a, Patch):
                fc, ec = to_rgba(a.get_facecolor()), to_rgba(a.get_edgecolor())   # each with its drawn alpha
                face0, edge0 = to_hex(fc).upper()[:7], to_hex(ec).upper()[:7]
                a.set_alpha(None)          # else the artist's alpha would replace each colour's own (a 0-alpha edge)
                a.set_facecolor(new_colour(name, fc))
                a.set_edgecolor(new_colour(name, ec))
                if name == "mode_decomp_eavail_central":
                    if face0 in MODE_OF:
                        a.set_hatch(npal.MODES[MODE_OF[face0]][1])
                    elif edge0 == "#FF0000":
                        a.set_hatch(None)


TEXT_FIXES = (("E_{avail}", r"E_{\rm avail}"), ("p_z", r"p_\parallel"))   # the note's notation (plan section 5(a))


def fix_text(s):
    for a, b in TEXT_FIXES:
        s = s.replace(a, b)
    return s


def rebuild_legends(fig):
    """Each axes legend again from its own labelled artists, in its order and place, frameless, notation fixed."""
    for ax in fig.axes:
        leg = ax.get_legend()
        if leg is None:
            continue
        want = [t.get_text() for t in leg.get_texts()]
        h, lab = ax.get_legend_handles_labels()
        pick = dict(zip(lab, h))
        kw = {"loc": leg._loc, "frameon": False, "ncol": leg._ncols}
        leg.remove()
        missing = [x for x in want if x not in pick]
        if missing:
            raise SystemExit(f"legend entries without an artist: {missing}")
        ax.legend([pick[x] for x in want], want, **kw)


def power_of_ten(fig):
    """Move each y axis's offset (the "1e-38" above it) into its label, as 10^n before the unit; an axes without a
    label keeps the factor as a math-text offset (x10^n). Tick labels only: no datum changes."""
    from matplotlib.ticker import FuncFormatter, ScalarFormatter
    fig.canvas.draw()
    for ax in fig.axes:
        off = ax.yaxis.get_offset_text().get_text().replace("−", "-")
        if not off.startswith("1e"):
            continue
        e = int(off[2:])
        lab = ax.get_ylabel()
        if lab and " (" in lab:   # the unit is the last " (...)"; the quantity before it may hold its own brackets
            ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _p, e=e: f"{v / 10.0 ** e:g}"))
            i = lab.rindex(" (")
            ax.set_ylabel(lab[:i] + "\n(" + rf"$10^{{{e}}}$ " + lab[i + 2:])   # the unit on its own line
        else:
            f = ScalarFormatter(useMathText=True)
            f.set_powerlimits((0, 0))
            ax.yaxis.set_major_formatter(f)


def relabel(fig):
    """The notation fixes on axis labels and on every artist's and container's own label, so that a legend rebuilt
    from them (here and in restyle_family4.restyle) finds each entry."""
    for ax in fig.axes:
        ax.set_xlabel(fix_text(ax.get_xlabel()))
        ax.set_ylabel(fix_text(ax.get_ylabel()))
        for a in list(ax.get_children()) + list(ax.containers):
            lab = a.get_label() if hasattr(a, "get_label") else None
            if isinstance(lab, str) and lab and not lab.startswith("_"):
                a.set_label(fix_text(lab))
        leg = ax.get_legend()
        if leg is not None:
            for t in leg.get_texts():
                t.set_text(fix_text(t.get_text()))


def main():
    pdir, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    for fname in rf4.PINNED:
        name = fname[: -len(".pdf.figpickle")]
        fig = rf4.load(pdir / fname)
        recolour(fig, name)
        relabel(fig)
        rebuild_legends(fig)
        power_of_ten(fig)
        entries = sorted(t.get_text() for ax in fig.axes if ax.get_legend() for t in ax.get_legend().get_texts())
        fig = rf4.restyle(fig, name)
        after = sorted(t.get_text() for leg in fig.legends + [ax.get_legend() for ax in fig.axes if ax.get_legend()]
                       for t in leg.get_texts())
        if after != entries:
            raise SystemExit(f"{name}: legend entries {entries} became {after}")
        fig.savefig(out / f"{name}.pdf")
        fig.savefig(out / f"{name}.png", dpi=200)
        plt.close(fig)
        print(f"[palette4] wrote {out / name}.pdf")


if __name__ == "__main__":
    main()
