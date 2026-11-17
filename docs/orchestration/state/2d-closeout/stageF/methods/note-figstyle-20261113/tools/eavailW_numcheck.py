#!/usr/bin/env python3
"""eavailW_band numerical identity check (note figure style, group C family 5; the director's ruling (b), 2026-11-15).

usage: python3 eavailW_numcheck.py <f5 run dir> <out dir>      (with tools/fakeroot5 on PYTHONPATH, for the import of ROOT)
1. The three TH1 readbacks (base commit's ROOT path, new default path, new default path from the dump) hold the same
   histograms with equal edges and contents, bit for bit.
2. The new --print-style matplotlib figure, drawn from the run's dump, plots exactly the off readback's values: per
   panel, each generator's step values and points equal hEa_<label> / hW_<label>, and the data points equal hData_ea /
   hData_W; the step edges equal the histograms' edges.
Prints EAVAILW-NUMCHECK :: PASS or FAIL."""
import importlib.util, sys
from pathlib import Path
import numpy as np
run, outd = Path(sys.argv[1]), Path(sys.argv[2]); outd.mkdir(parents=True, exist_ok=True)
rb = {k: np.load(run / d / "eavailW_band_root_th1.npz") for k, d in (("base", "out-base"), ("off", "out"), ("from", "out-from"))}
ok = True
keys = sorted(rb["off"].files)
for k in ("base", "from"):
    same = sorted(rb[k].files) == keys and all(np.array_equal(rb[k][n], rb["off"][n]) for n in keys)
    print(f"{'ok  ' if same else 'FAIL'} readback {k} == off ({len(keys) // 2} TH1)"); ok &= same
HERE = Path(__file__).resolve().parent
prod = HERE.parents[7] / "3d-unfolding" / "genie" / "overlay_eavailW_band.py"
spec = importlib.util.spec_from_file_location("ovl", prod); ovl = importlib.util.module_from_spec(spec); spec.loader.exec_module(ovl)
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import StepPatch
captured = {}
_orig = plt.Figure.savefig
def grab(self, fname, *a, **k):
    captured.setdefault("fig", self); return _orig(self, fname, *a, **k)
plt.Figure.savefig = grab
sys.argv = [str(prod), "--data", "x", "--from-arrays", str(run / "out" / "band_arrays.npz"), "--print-style", "--png", str(outd / "eavailW_band.png")]
ovl.main()
fig = captured["fig"]; off = rb["off"]
with np.load(run / "out" / "band_arrays.npz") as z:
    labels = [str(x) for x in z["labels"]]
for ax, tag, dname, gname in ((fig.axes[0], "eavail", "hData_ea", "hEa_"), (fig.axes[1], "W", "hData_W", "hW_")):
    steps = [p for p in ax.patches if isinstance(p, StepPatch)]
    pts = [l for l in ax.lines if len(l.get_xdata())]
    for i, lab in enumerate(labels):
        v, e = steps[i].get_data().values, steps[i].get_data().edges
        c, ce = off[f"{gname}{lab}__contents"], off[f"{gname}{lab}__edges"]
        good = np.array_equal(v, c) and np.array_equal(e, ce) and np.array_equal(pts[i].get_ydata(), c)
        print(f"{'ok  ' if good else 'FAIL'} {tag} {lab}: steps and points == {gname}{lab} ({len(c)} bins)"); ok &= good
    good = np.array_equal(pts[len(labels)].get_ydata(), off[f"{dname}__contents"])
    print(f"{'ok  ' if good else 'FAIL'} {tag} data points == {dname}"); ok &= good
print("EAVAILW-NUMCHECK ::", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
