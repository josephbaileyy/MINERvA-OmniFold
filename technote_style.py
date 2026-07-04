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
