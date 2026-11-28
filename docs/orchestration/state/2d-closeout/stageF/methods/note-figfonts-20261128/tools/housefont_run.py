#!/usr/bin/env python3
"""Run an unchanged note figure producer with note-figpass-20261119's layout edits, in the note's house fonts
(note-figfonts-20261128, part (b): eavail_marginal_vs_paper_pull_full.pdf, which printed DejaVu Sans and Sans Mono).

usage: HOUSEFONT=1 [FIG3_LABELS=1] python3 housefont_run.py <script> [args...]
       (HOUSEFONT=0 FIG3_LABELS=0: layout_run.py exactly, the control)

As note-figpass-20261119/tools/layout_run.py with LAYOUT_PALETTE=0 (the installed figure's arm 1, runs/f17), with one
step more. At a figure's first save, before layout_lib.apply() (so that the layout is made with the new metrics):
  - rcParams take restyle_2026_10.PRINT_FONT, the keys of note_print_style.PRINT_RC that name fonts or their embedding
    (serif DejaVu Serif, Computer Modern mathtext, TrueType embedding);
  - every drawn text whose family is not serif (the producer's DejaVu Sans, and the monospace of its statistics box,
    compare_to_paper_fullcov.py: family="monospace") is set to serif.
No size, string, position, datum, colour or style is changed by this step. The producer's --style is NOT used: under it
the histogram's bins change from 30 equal bins to zero-aligned bins of width 0.15 (compare_to_paper_fullcov.py), and
its sizes, labels and canvas change too. layout_lib then makes the installed figure's edits from note-figpass-20261119's
own tables (6.5 x 7.5 in, every text at least 10 pt, its axes boxes, texts.tsv's wording), unchanged, but for one
declared exception: with FIG3_LABELS=1 (the producer from main, which since 430b42db2 labels the heat map's cell
boundaries and axes in GeV/c as Fig. 3 does; Joseph 2026-11-28, "we should match them"), the two texts.tsv rows that
renamed the old axis labels "p_|| bin" and "p_T bin" are dropped, since the producer no longer draws those strings and
layout_lib stops on a row it cannot find. Each must be present to be dropped; texts.tsv's other row (pull ->
standardized difference) stays.
With HOUSEFONT=1, one wording row is added (HOUSE_TEXTS, applied by layout_lib like texts.tsv's rows, so it must be
found): the statistics box's "rms =0.83" reads "rms=0.83". Its space lined the value up with "mean=0.16" in the old
monospace font and looks stray in serif (Joseph 2026-11-28).
"""
import os
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
METHODS = HERE.parents[1]
REPO = HERE.parents[7]
sys.path.insert(0, str(METHODS / "note-figpass-20261119" / "tools"))
sys.path.insert(0, str(REPO / "2d-unfolding"))
import layout_lib  # noqa: E402
import restyle_2026_10 as rs  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.text import Text  # noqa: E402

HOUSE = os.environ.get("HOUSEFONT", "1") != "0"
FIG = "eavail_marginal_vs_paper_pull_full"
SUPERSEDED = [("p_|| bin", "$p_\\parallel$ bin"), ("p_T bin", "$p_T$ bin")]   # texts.tsv rows, as layout_lib reads them
if os.environ.get("FIG3_LABELS", "0") == "1":
    rows = layout_lib.TEXTS.get(FIG, [])
    for r in SUPERSEDED:
        assert r in rows, (r, rows)
    layout_lib.TEXTS[FIG] = [r for r in rows if r not in SUPERSEDED]
    print(f"[housefont_run] FIG3_LABELS: texts.tsv rows dropped {SUPERSEDED}; kept {layout_lib.TEXTS[FIG]}",
          file=sys.stderr)
HOUSE_TEXTS = [("rms =", "rms=")]
if HOUSE:
    assert rs.PRINT_FONT.get("pdf.fonttype") == 42, rs.PRINT_FONT
    layout_lib.TEXTS[FIG] = layout_lib.TEXTS.get(FIG, []) + HOUSE_TEXTS
_inner = Figure.savefig
CHANGED = {}


def house(fig, name):
    """Each Text keeps the family and the mathtext font set it was created with (FontProperties reads rcParams once,
    at creation), so both are set on every drawn text as well as in rcParams (for texts made at the final draw)."""
    matplotlib.rcParams.update(rs.PRINT_FONT)
    math = rs.PRINT_FONT["mathtext.fontset"]
    n = m = 0
    for t in fig.findobj(Text):
        if [f.lower() for f in t.get_fontfamily()] != ["serif"]:
            t.set_fontfamily("serif"); n += 1
        if t.get_fontproperties().get_math_fontfamily() != math:
            t.set_math_fontfamily(math); m += 1
    CHANGED[name] = {"family": n, "mathtext": m}


def savefig(self, fname, *a, **k):
    if not getattr(self, "_note_layout_done", False) and (isinstance(fname, (str, bytes))
                                                           or hasattr(fname, "__fspath__")):
        name = Path(str(fname)).name.split(".")[0]
        if HOUSE:
            house(self, name)
        layout_lib.apply(self, name)
        self._note_layout_done = True
    return _inner(self, fname, *a, **k)


Figure.savefig = savefig
script, args = Path(sys.argv[1]).resolve(), sys.argv[2:]
sys.argv = [str(script), *args]
sys.path.insert(0, str(script.parent))
try:
    runpy.run_path(str(script), run_name="__main__")
finally:
    if HOUSE:
        print(f"[housefont_run] texts set to serif: {CHANGED}", file=sys.stderr)
