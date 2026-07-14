"""Shared figure style for the OmniFold analysis-note figures.

Importing this module (``import technote_style``) has three effects, so that
every figure that feeds ``docs/technote/`` is visually consistent:

1. **No plot titles.** ``Axes.set_title``, ``Figure.suptitle`` and the pyplot
   ``title``/``suptitle`` helpers are turned into no-ops. All descriptive
   information lives in the LaTeX caption, never baked into the raster.

2. **One colormap per role.** ``SEQ_CMAP`` (viridis) is the single sequential
   map for magnitude heatmaps; ``DIV_CMAP`` (RdBu_r) is the single diverging map
   for quantities centred on zero (correlation, pull, ratio-minus-one). The
   default ``image.cmap`` is set to ``SEQ_CMAP`` so bare ``imshow`` calls are
   already consistent.

3. **A fixed generator palette.** ``GEN_COLORS`` pins one colour per generator
   so GENIE/Tune/NuWro/GiBUU are the same colour in every figure; the default
   line colour cycle follows the same palette. ``GEN_MARKERS`` pairs each
   generator with a fixed marker shape so overlaid series stay distinguishable
   in grayscale, not just by colour.

4. **Vector twins.** Any ``Figure.savefig``/``pyplot.savefig`` call whose
   output path ends in ``.png`` also writes a sibling ``.pdf`` (same figure,
   PDF backend) next to it, so every raster figure has a vector twin for the
   note without scripts having to save twice.

Scripts reach this module with a depth-agnostic bootstrap::

    import sys, pathlib
    for _a in pathlib.Path(__file__).resolve().parents:
        if (_a / "technote_style.py").exists():
            sys.path.insert(0, str(_a)); break
    import technote_style  # noqa: E402  (no titles + consistent colours)
"""

import matplotlib

matplotlib.use("Agg")  # headless: figures are saved, never shown

import matplotlib as mpl  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

# --- canonical colormaps -------------------------------------------------
SEQ_CMAP = "viridis"   # sequential: magnitude heatmaps
DIV_CMAP = "RdBu_r"    # diverging: correlation / pull / ratio-about-zero

# --- fixed per-generator colours (a generator is one colour everywhere) --
GEN_COLORS = {
    "GENIE":  "#C44E52",  # red
    "Tune":   "#4C72B0",  # blue   (GENIE + MINERvA Tune v1)
    "MEC":    "#4C72B0",  # blue   (alias: Tune v1 enables Valencia 2p2h)
    "NuWro":  "#2ca02c",  # green
    "GiBUU":  "#9467bd",  # purple
    "data":   "k",
}
# palette order used for index-based generator loops (GENIE, Tune/MEC, NuWro, GiBUU)
GEN_PALETTE = ["#C44E52", "#4C72B0", "#2ca02c", "#9467bd"]

# fixed per-generator markers (same generator = same shape everywhere, so
# overlaid series stay distinguishable in grayscale, not just by colour)
GEN_MARKERS = {
    "GENIE":  "o",
    "Tune":   "s",  # GENIE + MINERvA Tune v1 / MnvTune-v1
    "MEC":    "s",  # alias: Tune v1 enables Valencia 2p2h
    "NuWro":  "^",
    "GiBUU":  "D",
    "data":   "o",  # data points keep their existing marker convention
}


def gen_marker(label, default="o"):
    """Marker for a generator given a free-form label (case/substring tolerant)."""
    key = str(label).lower()
    for name, mk in GEN_MARKERS.items():
        if name.lower() in key:
            return mk
    return default

# default line-cycle: the four generator colours first (so a script that colours
# generators by cycle order stays consistent) then six further distinct hues, so
# plots with more than four cycled series (e.g. per-category uncertainty bands)
# do not wrap and reuse a colour.
LINE_CYCLE = GEN_PALETTE + ["#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf", "#ff7f0e"]


def gen_color(label, default="k"):
    """Colour for a generator given a free-form label (case/substring tolerant)."""
    key = str(label).lower()
    for name, col in GEN_COLORS.items():
        if name.lower() in key:
            return col
    return default


# --- apply rcParams ------------------------------------------------------
mpl.rcParams["image.cmap"] = SEQ_CMAP
mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=LINE_CYCLE)

# --- suppress all titles (information belongs in the LaTeX caption) -------
_noop = lambda *a, **k: None
Axes.set_title = _noop
Figure.suptitle = _noop
plt.title = _noop
plt.suptitle = _noop

# --- vector twins: every .png savefig also writes a sibling .pdf ---------
def _make_savefig_with_pdf_twin(orig_savefig):
    if getattr(orig_savefig, "_technote_pdf_twin", False):
        return orig_savefig

    def savefig(self, fname, *args, **kwargs):
        result = orig_savefig(self, fname, *args, **kwargs)
        if isinstance(fname, (str, bytes)) or hasattr(fname, "__fspath__"):
            fname_str = str(fname)
            if fname_str.lower().endswith(".png"):
                pdf_name = fname_str[: -len(".png")] + ".pdf"
                pdf_kwargs = dict(kwargs)
                pdf_kwargs.pop("format", None)
                orig_savefig(self, pdf_name, *args, **pdf_kwargs)
        return result

    savefig._technote_pdf_twin = True
    return savefig


Figure.savefig = _make_savefig_with_pdf_twin(Figure.savefig)
if not getattr(plt.savefig, "_technote_pdf_twin", False):
    _orig_pyplot_savefig = plt.savefig

    def _pyplot_savefig(fname, *args, **kwargs):
        fig = plt.gcf()
        return fig.savefig(fname, *args, **kwargs)

    _pyplot_savefig._technote_pdf_twin = True
    plt.savefig = _pyplot_savefig


# --- optional dark presentation theme (TECHNOTE_DARK=1) -------------------
# Gated on an env var so the analysis-note builds are untouched: figures come
# out on the Nocturne deck ground (docs/jul-16-presentation) instead of white.
# Generator hues keep their identities but move to dark-surface variants
# validated for lightness/chroma/CVD/contrast against #161826; a savefig-time
# fixup remaps artists that scripts hardcode as black/white.
import os as _os

TECHNOTE_DARK = bool(_os.environ.get("TECHNOTE_DARK"))
if TECHNOTE_DARK:
    DARK_BG = "#161826"      # deck ground (--color-bg)
    DARK_PANEL = "#1b1e2e"   # axes panel, one step above the ground
    DARK_SURFACE = "#232532" # legend/bbox surface (--color-surface)
    DARK_INK = "#e9e9ed"     # primary text/data ink (--color-text)
    DARK_MUTED = "#b2b6ca"   # secondary text (neutral-400)
    DARK_GRID = "#3f424d"    # gridlines (neutral-800)
    DARK_SPINE = "#595d6c"   # spines/ticks (neutral-700)

    GEN_COLORS.update({
        "GENIE": "#D96C6C", "Tune": "#5B8ED6", "MEC": "#5B8ED6",
        "NuWro": "#3FA845", "GiBUU": "#A078D0", "data": DARK_INK,
    })
    GEN_PALETTE[:] = ["#D96C6C", "#5B8ED6", "#3FA845", "#A078D0"]
    LINE_CYCLE[:] = GEN_PALETTE + [
        "#B08468", "#E58FCB", "#9397AB", "#C9CA4E", "#3FC8D8", "#FF942E",
    ]
    mpl.rcParams.update({
        "figure.facecolor": DARK_BG, "savefig.facecolor": DARK_BG,
        "axes.facecolor": DARK_PANEL, "axes.edgecolor": DARK_SPINE,
        "axes.labelcolor": DARK_INK, "text.color": DARK_INK,
        "xtick.color": DARK_MUTED, "ytick.color": DARK_MUTED,
        "xtick.labelcolor": DARK_MUTED, "ytick.labelcolor": DARK_MUTED,
        "grid.color": DARK_GRID,
        "legend.facecolor": DARK_SURFACE, "legend.edgecolor": DARK_SPINE,
        "axes.prop_cycle": mpl.cycler(color=LINE_CYCLE),
        "hatch.color": DARK_MUTED,
    })

    import colorsys as _colorsys
    from matplotlib.colors import to_rgba as _to_rgba
    from matplotlib.colors import LinearSegmentedColormap as _LSC

    # Diverging map for dark grounds: RdBu_r's white midpoint glares on the
    # deck, so near-zero fades into the panel instead and the extremes stay
    # bright. Swapped in at savefig time for any image drawn with RdBu_r.
    DARK_DIV_CMAP = _LSC.from_list(
        "technote_dark_div",
        ["#A8CCF8", "#5B8ED6", "#20233A", "#D96C6C", "#F8B8B8"],
    )
    _DIV_SWAP_NAMES = {"RdBu_r", "RdBu", "coolwarm", "bwr"}

    def _rgba(color):
        try:
            r, g, b, a = _to_rgba(color)
        except (TypeError, ValueError):
            return None
        return (r, g, b, a) if a > 0 else None

    def _relight(r, g, b, a, new_l, sat_scale=1.0):
        h, l, s = _colorsys.rgb_to_hls(r, g, b)
        r2, g2, b2 = _colorsys.hls_to_rgb(h, new_l, min(1.0, s * sat_scale))
        return (r2, g2, b2, a)

    def _dark_swap(color):
        """Ink rule (text, lines, markers): light-theme ink -> dark-theme ink."""
        c = _rgba(color)
        if c is None:
            return None
        r, g, b, a = c
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
        chroma = max(r, g, b) - min(r, g, b)
        if lum < 0.20 and chroma < 0.10:                # near-black -> ink
            return (*_to_rgba(DARK_INK)[:3], a)
        if 0.20 <= lum <= 0.82 and chroma < 0.04:       # neutral gray ink ("0.25".."0.7")
            return (*_to_rgba(DARK_MUTED)[:3], a)
        if lum < 0.40 and chroma >= 0.04:               # colored dark ink -> lighten, keep hue
            return _relight(r, g, b, a, 0.70)
        return None

    def _dark_swap_fill(color):
        """Fill rule (patch/collection faces & edges): darken light grounds/pastels."""
        c = _rgba(color)
        if c is None:
            return None
        r, g, b, a = c
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
        chroma = max(r, g, b) - min(r, g, b)
        if lum < 0.20 and chroma < 0.10:                # black fills (e.g. data scatter) -> ink
            return (*_to_rgba(DARK_INK)[:3], a)
        if lum > 0.92 and chroma < 0.05:                # white ground -> panel
            return (*_to_rgba(DARK_PANEL)[:3], a)
        if lum > 0.70:                                  # light pastel band -> dark tint, same hue
            return _relight(r, g, b, a, 0.20, sat_scale=0.9)
        return None

    def _dark_fix_artist(art):
        import numpy as _np
        from matplotlib.lines import Line2D
        from matplotlib.text import Text
        from matplotlib.patches import Patch
        from matplotlib.collections import Collection
        if isinstance(art, Text):
            new = _dark_swap(art.get_color())
            if new is not None:
                art.set_color(new)
            bp = art.get_bbox_patch()
            if bp is not None:
                nf = _dark_swap_fill(bp.get_facecolor())
                if nf is not None:  # light box behind text -> surface, keep alpha
                    bp.set_facecolor((*_to_rgba(DARK_SURFACE)[:3], _to_rgba(bp.get_facecolor())[3]))
                ne = _dark_swap(bp.get_edgecolor())
                if ne is not None:
                    bp.set_edgecolor(DARK_SPINE)
        elif isinstance(art, Line2D):
            for get, set_ in ((art.get_color, art.set_color),
                              (art.get_markerfacecolor, art.set_markerfacecolor),
                              (art.get_markeredgecolor, art.set_markeredgecolor)):
                new = _dark_swap(get())
                if new is not None:
                    set_(new)
        elif isinstance(art, Patch):
            nf = _dark_swap_fill(art.get_facecolor())
            if nf is not None:
                art.set_facecolor(nf)
            ne = _dark_swap(art.get_edgecolor())
            if ne is not None:
                art.set_edgecolor(ne)
        elif isinstance(art, Collection):
            if getattr(art, "get_array", None) and art.get_array() is not None:
                # colormapped collection (pcolormesh etc.): swap the cmap,
                # never the computed facecolors
                if art.get_cmap().name in _DIV_SWAP_NAMES:
                    art.set_cmap(DARK_DIV_CMAP)
                return
            try:
                fcs = art.get_facecolor()
                if len(fcs):
                    new = [(_dark_swap_fill(tuple(c)) or tuple(c)) for c in fcs]
                    art.set_facecolor(new)
                ecs = art.get_edgecolor()
                if len(ecs):
                    new = [(_dark_swap(tuple(c)) or tuple(c)) for c in ecs]
                    art.set_edgecolor(new)
            except (TypeError, ValueError):
                pass

    def _dark_fix_figure(fig):
        if getattr(fig, "_technote_darkfixed", False):
            return
        fig._technote_darkfixed = True
        fig.patch.set_facecolor(DARK_BG)
        for ax in fig.axes:
            ax.patch.set_facecolor(DARK_PANEL)
            for im in ax.images:
                if im.get_cmap().name in _DIV_SWAP_NAMES:
                    im.set_cmap(DARK_DIV_CMAP)
            for sp in ax.spines.values():
                new = _dark_swap(sp.get_edgecolor())
                sp.set_edgecolor(new if new is not None else DARK_SPINE)
            for art in list(ax.get_children()):
                if art is ax.patch:  # the panel was just set; the fill rule must not revisit it
                    continue
                _dark_fix_artist(art)
            leg = ax.get_legend()
            if leg is not None:
                leg.get_frame().set_facecolor(DARK_SURFACE)
                leg.get_frame().set_edgecolor(DARK_SPINE)
                for t in leg.get_texts():
                    new = _dark_swap(t.get_color())
                    if new is not None:
                        t.set_color(new)
                for lh in getattr(leg, "legend_handles", None) or getattr(leg, "legendHandles", []):
                    if lh is not None:
                        _dark_fix_artist(lh)
        for t in fig.texts:
            _dark_fix_artist(t)

    def _make_savefig_dark(orig_savefig):
        if getattr(orig_savefig, "_technote_dark", False):
            return orig_savefig

        def savefig(self, fname, *args, **kwargs):
            _dark_fix_figure(self)
            # transparent figure ground (axes panels stay): the deck paints a
            # gradient behind the plot, so the raster must not carry a hard
            # background rectangle
            kwargs["facecolor"] = "none"
            kwargs["transparent"] = False
            return orig_savefig(self, fname, *args, **kwargs)

        savefig._technote_dark = True
        savefig._technote_pdf_twin = getattr(orig_savefig, "_technote_pdf_twin", False)
        return savefig

    Figure.savefig = _make_savefig_dark(Figure.savefig)


def minerva_tag(fig_or_ax, loc="upper left"):
    """Uniform sample/POT annotation for every data-bearing note figure.

    Places a small ``MINERvA ME FHC, 1.06e21 POT`` tag (rendered with the POT
    in math mode) in a consistent corner.  Titles are suppressed by this
    module, so this tag is how a data figure carries its dataset identity
    without a title bar.  Accepts either a Figure or an Axes; on a Figure it
    annotates the first axes (falling back to a figure-level text if there are
    none).  MC-only figures (migration maps, MC-only corner) should NOT call
    this.
    """
    text = r"MINERvA ME FHC, $1.06\times10^{21}$ POT"
    ax = None
    if isinstance(fig_or_ax, Axes):
        ax = fig_or_ax
    else:  # a Figure
        axes = getattr(fig_or_ax, "axes", None)
        if axes:
            ax = axes[0]
    x, ha = (0.02, "left") if "left" in loc else (0.98, "right")
    y, va = (1.01, "bottom") if "upper" in loc else (0.02, "bottom")
    if ax is not None:
        ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va,
                fontsize=8, color="0.25", zorder=100)
    else:
        fig_or_ax.text(x, 0.99, text, ha=ha, va="top",
                       fontsize=8, color="0.25", zorder=100)


def panel_label(ax, text, loc="upper left", color="black"):
    """Short corner tag identifying one panel of a multi-panel figure.

    Titles are suppressed (above), so a figure with several panels has no
    per-panel identifier; this places a compact ``(a) ...`` tag in a corner,
    keyed to the LaTeX caption, without reintroducing a title bar.
    """
    x, ha = (0.03, "left") if "left" in loc else (0.97, "right")
    y, va = (0.97, "top") if "upper" in loc else (0.03, "bottom")
    ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va,
            fontsize=11, fontweight="bold", color=color,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.6", alpha=0.85))
