#!/usr/bin/env python3
"""Local identity test for family 1 (make_control_plots.py, plot_control_corner.py): note figure style, group C.

usage: python3 identity_family1.py <base sha> <scratch dir>     (run with the matplotlib the figures were made with)
On synthetic inputs (no ROOT: tools/fakeroot/ROOT.py serves deterministic histograms; the corner's load() is replaced
by synthetic events; the edges by stand-ins), it requires, for each producer:
  1. the refactored producer with no flag draws byte-identical PNGs to the producer at <base sha> (git show);
  2. --from-arrays on its own --dump-arrays draws byte-identical PNGs (the dump holds every drawn value).
Exit 1 on any difference. It writes only under <scratch dir>, and two temporary copies of the base producers next to
the new ones, removed at exit.
"""
import importlib, os, subprocess, sys
from pathlib import Path
import numpy as np
base, scratch = sys.argv[1], Path(sys.argv[2])
HERE = Path(__file__).resolve().parent
ROOTDIR = HERE.parents[7]
ND = ROOTDIR / "nd-unfolding"
sys.path[:0] = [str(HERE / "fakeroot"), str(ND)]
E = {"pt": np.array([0, .07, .15, .25, .33, .4, .47, .55, .7, .85, 1, 1.25, 1.5, 2.5, 4.5]),
     "pz": np.array([1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 7, 8, 9, 10, 15, 20, 60.]),
     "eavail": np.array([0, .1, .2, .4, .8, 1.5, 3, 100.]), "q3": np.array([0, .2, .4, .6, .8, 1.2, 2, 100.]),
     "W": np.array([0, 1.1, 1.4, 1.8, 2.2, 3, 100.])}
rng = np.random.default_rng(3)
def ev(n):
    x = {"pt": rng.gamma(2, .3, n), "pz": rng.gamma(3, 2, n) + 1.5, "eavail": rng.gamma(1.5, .3, n),
         "q3": rng.gamma(2, .3, n), "W": rng.gamma(4, .4, n)}
    x["w"] = rng.uniform(.5, 1.5, n); return x
data, mc = ev(20000), ev(60000); data["w"] = np.ones(20000)
import matplotlib.pyplot as plt
tmp = []
fail = 0
try:
    for prod, pngs in (("make_control_plots", ["control_plots", "migration_resolution"]), ("plot_control_corner", ["control_corner"])):
        orig = ND / f"_base_{prod}.py"; tmp.append(orig)
        orig.write_bytes(subprocess.run(["git", "show", f"{base}:nd-unfolding/{prod}.py"], cwd=ROOTDIR, check=True, capture_output=True).stdout)
        out = {k: scratch / prod / k for k in ("base", "new", "from")}
        for d in out.values(): d.mkdir(parents=True, exist_ok=True)
        dump = scratch / prod / "dump.npz"
        for modname, o, extra in ((f"_base_{prod}", out["base"], []), (prod, out["new"], ["--dump-arrays", str(dump)]),
                                  (prod, out["from"], ["--from-arrays", str(dump)])):
            m = importlib.import_module(modname); m.edges_for = lambda a: E[a]
            if hasattr(m, "load"): m.load = lambda args: (data, mc)
            sys.argv = [modname + ".py", "--outdir", str(o)] + extra; m.main(); plt.close("all")
        for p in pngs:
            for arm in ("new", "from"):
                same = (out["base"] / f"{p}.png").read_bytes() == (out[arm] / f"{p}.png").read_bytes()
                fail |= not same
                print(f"{'ok  ' if same else 'FAIL'} {prod} {p}.png: base == {arm}")
        print(f"     {prod} dump {dump.stat().st_size} bytes")
finally:
    for t in tmp: t.unlink(missing_ok=True)
print(f"IDENTITY-FAMILY1 :: {'FAIL' if fail else 'PASS'}")
sys.exit(1 if fail else 0)
