#!/usr/bin/env python3
"""Run an unchanged note figure producer with the palette pass's edits and then this record's layout edits.

usage: python3 layout_run.py <script> [args...]

As note-figstyle-20261117/tools/palette_run.py (the producer runs as __main__, not one byte of it changes), but at a
figure's first save, before anything is written, palette_lib.apply(fig, stem) and then layout_lib.apply(fig, stem)
are made, once per figure. Arm 0 of this record is palette_run.py itself, which reproduces the installed file.
With LAYOUT_PALETTE=0 (a figure the palette pass did not edit, whose installed file is the plain producer's), the
palette edits are skipped and arm 0 is the plain producer (arms_layout.sh with ARM0=plain).
"""
import os
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PALETTE_TOOLS = HERE.parents[1] / "note-figstyle-20261117" / "tools"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PALETTE_TOOLS))
import layout_lib  # noqa: E402
import palette_lib  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
from matplotlib.figure import Figure  # noqa: E402

_inner = Figure.savefig


def savefig(self, fname, *a, **k):
    if not getattr(self, "_note_layout_done", False) and (isinstance(fname, (str, bytes))
                                                           or hasattr(fname, "__fspath__")):
        name = Path(str(fname)).name.split(".")[0]
        if os.environ.get("LAYOUT_PALETTE", "1") != "0":   # 0: a figure the palette pass left as drawn
            palette_lib.apply(self, name)
        layout_lib.apply(self, name)   # a figure with no layout.tsv row is saved as arm 0 draws it
        self._note_layout_done = True
    return _inner(self, fname, *a, **k)


Figure.savefig = savefig
script, args = Path(sys.argv[1]).resolve(), sys.argv[2:]
sys.argv = [str(script), *args]
sys.path.insert(0, str(script.parent))
runpy.run_path(str(script), run_name="__main__")
