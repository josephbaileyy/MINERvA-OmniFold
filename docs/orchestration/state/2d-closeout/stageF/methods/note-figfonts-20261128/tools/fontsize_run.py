#!/usr/bin/env python3
"""Run an unchanged note figure producer with the palette pass's edits and then this record's print-size edits
(note-figfonts-20261128, part (c): the text of tension_spectrum and tension_chi2_map printed at about 8 pt).

usage: python3 fontsize_run.py <script> [args...]

As note-figpass-20261119/tools/layout_run.py, whose layout_lib.apply() makes the edits, unchanged: every axis keeps
the ticks and tick labels it drew, every text's size is multiplied by the scale and raised to the floor, the canvas
is set to the printed size, and the figure is laid out again with tight_layout(). Only the tables differ: layout_lib
reads its own record's; here LAYOUT is this record's layout.tsv and the other tables (texts, ticks, boxes, moves)
are empty, so no string, tick or axes box is changed by hand. A figure with no layout.tsv row (tension_mode_maps) is
saved exactly as palette_run.py saves it. The producer runs as __main__ and not one byte of it changes.
"""
import os
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REC = HERE.parent
METHODS = HERE.parents[1]
sys.path.insert(0, str(METHODS / "note-figpass-20261119" / "tools"))
sys.path.insert(0, str(METHODS / "note-figstyle-20261117" / "tools"))
import layout_lib  # noqa: E402
import palette_lib  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
from matplotlib.figure import Figure  # noqa: E402

rows = [ln.split("\t") for ln in (REC / "layout.tsv").read_text().splitlines() if ln.strip() and not ln.startswith("#")]
assert rows[0] == ["figure", "width_in", "height_in", "text_scale", "text_floor_pt"], rows[0]
layout_lib.LAYOUT = {r[0]: (float(r[1]), float(r[2]), float(r[3]), float(r[4])) for r in rows[1:]}
layout_lib.TEXTS, layout_lib.TICKS, layout_lib.BOXES, layout_lib.MOVES = {}, {}, {}, {}

_inner = Figure.savefig


def savefig(self, fname, *a, **k):
    if not getattr(self, "_note_layout_done", False) and (isinstance(fname, (str, bytes))
                                                           or hasattr(fname, "__fspath__")):
        name = Path(str(fname)).name.split(".")[0]
        if os.environ.get("LAYOUT_PALETTE", "1") != "0":
            palette_lib.apply(self, name)
        layout_lib.apply(self, name)
        self._note_layout_done = True
    return _inner(self, fname, *a, **k)


Figure.savefig = savefig
script, args = Path(sys.argv[1]).resolve(), sys.argv[2:]
sys.argv = [str(script), *args]
sys.path.insert(0, str(script.parent))
runpy.run_path(str(script), run_name="__main__")
