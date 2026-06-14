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
   line colour cycle follows the same palette.

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
