"""The analysis note's figure palette: one colour, line style and marker per series identity, opt-in, no side effects.

Joseph approved it on 2026-11-17 (COMBINED-PLAN.md section 5(a), note-measurement):
- the paper's colours, as read from publication/release/figs/make_figs.py: COLORS, and this work in #c0392b;
- #CC79A7 for GENIE CV, which the paper drew in the Tune blue;
- "this work" in red in every figure.
Fonts and sizes stay in note_print_style.PRINT_RC. This module only names styles; adding them to PRINT_RC would
change every --print-style output and its pinned test.

Identities are looked up by their exact key (``style("genie_cv")``). There is no substring or case matching:
technote_style's substring lookup could take "GENIE" for "GENIE + MEC". An unknown key raises KeyError.
``test_note_palette.py`` holds the rules:
- every identity has a unique (colour, line style, marker) triple;
- the line colours keep a CIE76 ΔE of at least 14 between every pair, in normal vision and in simulated protanopia,
  deuteranopia and tritanopia (Machado et al. 2009, severity 1);
- the paper's hexes are the paper producer's.
"""

LONG_DASH = (0, (6.0, 2.0))

# key: (label, colour, line style for a line or step ("None" for points only), marker for points (used where the
#       identity is drawn as sparse points; "None" if it is only ever a line), marker face ("full", "none" or "fill"))
IDENTITIES = {
    "this_work":        ("This work",                 "#c0392b", "--",       "o",    "full"),
    "published":        ("Published MINERvA",         "#000000", "None",     "s",    "none"),
    "published_second": ("Ascencio et al.",           "#000000", "None",     "^",    "none"),
    "reco_data":        ("Data (reconstructed)",      "#000000", "None",     "o",    "full"),
    "tune_v1":          ("MINERvA Tune v1",           "#2a78d6", "-",        "s",    "full"),
    "genie_cv":         ("GENIE 2.12.10 CV",          "#CC79A7", "--",       "v",    "full"),
    "genie_cv_fill":    ("GENIE 2.12.10 CV (bar)",    "#F0D4E4", "-",        "None", "fill"),
    "genie_mec":        ("GENIE + Valencia MEC",      "#eb6834", "-.",       "None", "full"),
    "nuwro":            ("NuWro",                     "#1baf7a", ":",        "^",    "full"),
    "gibuu":            ("GiBUU",                     "#4a3aa7", LONG_DASH,  "D",    "full"),
    "mc_background":    ("MC background",             "#BBBBBB", "-",        "None", "fill"),
    "null_distribution": ("Null distribution",        "#2a78d6", "-",        "None", "fill"),
}
# The interaction modes: four greys, each with its own hatch.
MODES = {"QE": ("#4d4d4d", "///"), "RES": ("#7a7a7a", "\\\\\\"), "DIS": ("#a6a6a6", "xx"), "COH": ("#cfcfcf", "..")}
THIS_WORK_BAND_ALPHA = 0.22          # the +-1 sigma fill of this work, no edge
NULL_ALPHA = 0.8                     # the null distributions' fill, in the Tune blue
NOT_REPORTED = {"facecolor": "#E6E6E6", "edgecolor": "0.55", "hatch": "///", "label": "not reported"}
SEQUENTIAL_CMAP = "viridis"
DIVERGING_CMAP = "RdBu_r"            # centred at 0 (a difference) or 1 (a ratio)

# The seven line colours the colour-blindness rule covers (the series that are drawn as lines or points).
LINE_IDENTITIES = ("this_work", "published", "tune_v1", "genie_cv", "genie_mec", "nuwro", "gibuu")


def _row(key):
    if key not in IDENTITIES:          # exact key only: no substring, no case folding
        raise KeyError(f"no note palette identity {key!r}; known: {sorted(IDENTITIES)}")
    return IDENTITIES[key]


def label(key):
    """The identity's legend name."""
    return _row(key)[0]


def color(key):
    """The identity's colour, a hex string."""
    return _row(key)[1]


def style(key, **extra):
    """Keyword arguments for Axes.plot / errorbar: colour, line style and marker of the identity, plus ``extra``."""
    _, c, ls, mk, face = _row(key)
    kw = {"color": c, "linestyle": ls, "marker": mk}
    if mk != "None":
        kw["markerfacecolor"] = c if face == "full" else "none"
        kw["markeredgecolor"] = c
    kw.update(extra)
    return kw


def step_style(key, **extra):
    """Keyword arguments for Axes.stairs / step: colour and line style only."""
    _, c, ls, _, _ = _row(key)
    kw = {"color": c, "linestyle": "-" if ls == "None" else ls}
    kw.update(extra)
    return kw


def palette_table():
    """Rows (identity, hex) for every identity and mode ("mode_QE", ...): the palette file the record's recolour check
    reads (fig-restyle-20261031/tools/compare.py --palette). test_note_palette.py holds it to this module."""
    rows = [(k, v[1].upper()) for k, v in IDENTITIES.items()]
    rows += [(f"mode_{m}", c.upper()) for m, (c, _) in MODES.items()]
    return rows
