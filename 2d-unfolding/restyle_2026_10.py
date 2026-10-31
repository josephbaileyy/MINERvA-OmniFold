"""The note's restyle of its 2D result figures, Figs. 7-14 (fig-restyle-20261031/DECLARATION.md).

Each producer of those figures takes ``--style restyle-2026-10``, off by default, so every existing invocation draws the
figure it drew before. With the option, a producer draws its figure at the width the note prints it, so that a font
size here is the printed size, and uses the label strings below. The option changes figure size, layout, fonts, label
strings and text annotations only: no plotted value, colour, marker, line style or colour limit (DECLARATION.md §2,
checked by fig-restyle-20261031/tools/compare.py).

The note's text width is 469.755 pt = 6.5 in (main_note.log, `\\textwidth`); WIDTH gives each figure's printed width,
from its `\\includegraphics` in sec_results.tex.
"""
import matplotlib as mpl

STYLE = "restyle-2026-10"
TEXTWIDTH_IN = 469.755 / 72.27
WIDTH = {  # printed width (in) = the \includegraphics fraction of \textwidth
    "fig13": 0.62 * TEXTWIDTH_IN, "proj": 0.49 * TEXTWIDTH_IN, "pull_full": 0.7 * TEXTWIDTH_IN,
    "slices": 0.99 * TEXTWIDTH_IN, "spectrum": 0.49 * TEXTWIDTH_IN, "chi2_map": 0.49 * TEXTWIDTH_IN,
    "mode_maps": 0.9 * TEXTWIDTH_IN, "projections": 0.85 * TEXTWIDTH_IN, "ratio_maps": 0.9 * TEXTWIDTH_IN,
}
PT = r"$p_T$"
PZ = r"$p_\parallel$"
GEVC = r"(GeV/$c$)"


def add_option(ap):
    """Add the off-by-default --style option to an argparse parser."""
    ap.add_argument("--style", choices=[STYLE], default=None,
                    help=f"{STYLE}: the note's restyle of Figs. 7-14 (presentation only; off by default)")


def on(args):
    return getattr(args, "style", None) == STYLE


def apply(base=7.0):
    """Font sizes for a figure drawn at its printed size: base pt for text, base - 1 for ticks and legends."""
    mpl.rcParams.update({
        "font.size": base, "axes.labelsize": base, "axes.titlesize": base,
        "xtick.labelsize": base - 1, "ytick.labelsize": base - 1, "legend.fontsize": base - 1,
        "figure.titlesize": base, "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5, "xtick.minor.size": 1.5, "ytick.minor.size": 1.5,
        "legend.frameon": False, "legend.handlelength": 1.6, "savefig.pad_inches": 0.02,
    })


def slice_label(label, unit=True):
    """A slice label ("0.00 < p_T < 0.07", "1.5 < p_|| < 2.0") in math, with its unit unless unit=False."""
    s = label.replace("p_||", r"p_\parallel")
    return f"${s}$" + (" " + GEVC if unit else "")


def above(ax, text, size=None):
    """A panel label just above the panel's top-left corner, clear of the data."""
    return ax.text(0.0, 1.02, text, transform=ax.transAxes, ha="left", va="bottom",
                   fontsize=size or mpl.rcParams["font.size"], fontweight="bold")


def size_tag(fig, size):
    """Set the size of technote_style.minerva_tag's sample tag, which it draws at a fixed 8 pt; on a canvas larger
    than its printed size (Fig. 8's, kept for make_figures.sh's page-size assert) 8 pt would print too small."""
    for t in fig.texts + [x for a in fig.axes for x in a.texts]:
        if t.get_text().startswith("MINERvA ME FHC"):
            t.set_fontsize(size)


def integer_ticks(ax):
    """Bin-index axes: ticks at whole bins only."""
    from matplotlib.ticker import MaxNLocator
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))


def corner(ax, text, loc="upper left", size=None, **kw):
    """Plain text in a panel corner, in axes coordinates (not a title, which technote_style suppresses)."""
    x, ha = (0.03, "left") if "left" in loc else (0.97, "right")
    y, va = (0.96, "top") if "upper" in loc else (0.04, "bottom")
    return ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va,
                   fontsize=size or mpl.rcParams["font.size"], **kw)
