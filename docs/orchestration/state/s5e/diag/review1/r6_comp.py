"""Is the npz completeness 1? (explains driver comp=1 closure vs npz truth agreement)"""
import numpy as np
from common import *
d = L(f"{RUNS}/drv/driver_eavail.npz"); a = L(f"{RUNS}/asimov/asimov_b0_eavail.npz")
nz = a["xtrue_flat"] != 0
print("xtrue nonzero cells driver/npz:", int((d["xtrue_flat"] != 0).sum()), int(nz.sum()))
q = d["xtrue_flat"][nz] / a["xtrue_flat"][nz]
print("driver/npz xtrue ratio: min %.6f max %.6f median %.6f" % (q.min(), q.max(), np.median(q)))
z = np.load("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz", allow_pickle=True)
dn = z["denom_nd"]; print("denom_nd shape", dn.shape, "sum %.1f" % dn.sum())
edges = [np.asarray(z[f"edges_{i}"], float) for i in range(int(z["nedges"]))]
g = z["MCgen"]; pt = z["pass_truth"].astype(bool); wt = z["w_truth"]
ofin, _ = np.histogramdd(g[pt], bins=edges, weights=wt[pt])
m = dn > 0
c = ofin[m] / dn[m]
print("completeness ofin/denom over denom>0 cells: min %.4f median %.4f max %.4f ; sum ofin %.1f sum denom %.1f" % (c.min(), np.median(c), c.max(), ofin.sum(), dn.sum()))
