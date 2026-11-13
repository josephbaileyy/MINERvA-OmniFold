"""The methods paper's figure style, for the analysis note's figures, opt-in and without side effects.

Importing this module changes nothing. ``apply()`` sets the paper's figure rcParams (PRINT_RC), and
``figsize(width_frac, aspect)`` gives a canvas whose width is the figure's printed width in the note, so that a
font size in points prints at that size. A producer calls both only when asked (each producer's ``--print-style``),
so its default output is unchanged.

PRINT_RC is the dict at ``docs/analysis-note/figures/methods_short/make_figures.py:287-289`` on
draft/methods-short-20261109 at a871379960f2 (PR #977), plus one key, ``font.serif``. The paper's "serif" resolves
to DejaVu Serif, matplotlib's bundled serif, in its committed PDFs (pdffonts on paper_rounding_shifts.pdf at that
head), and naming it here keeps the font the same on a machine with other serif fonts installed.
``test_note_print_style.py`` checks the paper's values.

This is not ``technote_style``: importing that module turns every title into a no-op and writes a PDF twin of every
PNG, which would change a producer's output. A producer that already imports ``technote_style`` keeps doing so.
"""

PAPER_RC = {"font.family": "serif", "mathtext.fontset": "cm", "font.size": 8.5,
            "axes.labelsize": 9.3, "xtick.labelsize": 8.3, "ytick.labelsize": 8.3,
            "axes.linewidth": .6, "pdf.fonttype": 42}
PRINT_RC = dict(PAPER_RC, **{"font.serif": ["DejaVu Serif"]})

# The note's \textwidth: letter paper with 1 in margins (docs/analysis-note/preamble.tex:10, geometry margin=1in).
NOTE_TEXTWIDTH_IN = 6.5


def figsize(width_frac, aspect):
    """(width, height) in inches for a figure printed at width_frac of the note's text width; aspect = height/width."""
    w = width_frac * NOTE_TEXTWIDTH_IN
    return (w, w * aspect)


def apply():
    """Set the paper's figure rcParams. Call it before the figure is created."""
    import matplotlib as mpl
    mpl.rcParams.update(PRINT_RC)
