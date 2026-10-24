"""Fig. 1 drawn by make_figs.fig1 to a 300-dpi PNG with Agg, plus the legend's bounding box in that PNG's pixels,
taken from the same canvas (read-only: writes into outdir)."""
import sys, importlib.util, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
mf_path, npz, outdir, uq, tag = sys.argv[1:6]
spec = importlib.util.spec_from_file_location("make_figs", mf_path); mf = importlib.util.module_from_spec(spec); spec.loader.exec_module(mf)
orig = matplotlib.figure.Figure.savefig
info = {}
def savefig(self, fname, *a, **k):
    if str(fname).endswith("fig1_validation.pdf"):
        png = Path(outdir) / f"{tag}.png"
        orig(self, png, dpi=300)
        self.set_dpi(300); self.canvas.draw()
        H = self.bbox.height
        for ax in self.axes:
            lg = ax.get_legend()
            if lg:
                e = lg.get_window_extent()
                info["legend_px"] = [e.x0, H - e.y1, e.x1, H - e.y0]
        info["size_px"] = [self.bbox.width, H]
    return orig(self, fname, *a, **k)
matplotlib.figure.Figure.savefig = savefig
mf.style(); mf.fig1(np.load(npz), Path(outdir), uq)
print(json.dumps(info))
