#!/usr/bin/env python3
"""Run a figure producer unchanged under capture_any.py, and also pickle every saved figure (note figure style, group C,
family 4; the director's method ruling of 2026-11-15: figure pickles for producers that must not change).

usage: python3 capture_pickle.py <pickle-dir> <capture-dir> <script> [args...]

Before capture_any.py runs, Figure.savefig is wrapped: after each save, <pickle-dir>/<saved file name>.figpickle holds
pickle.dumps(fig), and <pickle-dir>/PICKLES.tsv gains a row (file name, sha256, matplotlib version, savefig keyword
arguments as repr). capture_any.py, run next through runpy with argv [capture-dir, script, args...], wraps savefig in
turn, so every save is both captured and pickled. The producer itself is not modified. Nothing is written outside the
two directories except what the producer writes itself."""
import hashlib
import pickle
import runpy
import sys
from pathlib import Path

import matplotlib
from matplotlib.figure import Figure

HERE = Path(__file__).resolve().parent
pdir = Path(sys.argv[1]); pdir.mkdir(parents=True, exist_ok=True)
_orig = Figure.savefig


def savefig(self, fname, *a, **k):
    r = _orig(self, fname, *a, **k)
    name = Path(str(fname)).name
    blob = pickle.dumps(self)
    (pdir / f"{name}.figpickle").write_bytes(blob)
    with open(pdir / "PICKLES.tsv", "a") as f:
        f.write(f"{name}.figpickle\t{hashlib.sha256(blob).hexdigest()}\t{matplotlib.__version__}\t{k!r}\n")
    return r


Figure.savefig = savefig
sys.argv = [str(HERE / "capture_any.py"), *sys.argv[2:]]
runpy.run_path(str(HERE / "capture_any.py"), run_name="__main__")
