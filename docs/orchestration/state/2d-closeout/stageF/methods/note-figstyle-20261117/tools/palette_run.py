#!/usr/bin/env python3
"""Run an unchanged note figure producer in the note palette (arm 1 of a figure that its producer saves directly).

usage: python3 palette_run.py <script> [args...]

The producer runs in this interpreter as __main__ (runpy), with its own directory first on sys.path and sys.argv set to
[script, *args]; not one byte of it changes. Figure.savefig is wrapped, outermost: at a figure's first save, before
anything is written, palette_lib.apply(fig, <stem of the saved file>) makes the record's declared edits (recolour.tsv,
restyle.tsv, hatches.tsv, text_fixes.tsv, the notation, frameless legends, the power of ten in the label). A figure is
edited once, however many files it is saved to (technote_style writes a PDF twin of each PNG through the same figure),
so a colour swap cannot be undone by a second pass. Run under capture_palette.py for the record.
"""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import palette_lib  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
from matplotlib.figure import Figure  # noqa: E402

_inner = Figure.savefig


def savefig(self, fname, *a, **k):
    if not getattr(self, "_note_palette_done", False) and (isinstance(fname, (str, bytes))
                                                            or hasattr(fname, "__fspath__")):
        name = Path(str(fname)).name.split(".")[0]
        palette_lib.apply(self, name)
        self._note_palette_done = True
    return _inner(self, fname, *a, **k)


Figure.savefig = savefig
script, args = Path(sys.argv[1]).resolve(), sys.argv[2:]
sys.argv = [str(script), *args]
sys.path.insert(0, str(script.parent))
runpy.run_path(str(script), run_name="__main__")
