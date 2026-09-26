"""Driver data product (ROOT) vs npz data products; per-functional probe-scale comparison."""
import json
import numpy as np
import ROOT
from common import *
def flat(path, key="hXSecND_flat"):
    f = ROOT.TFile.Open(path, "READ"); h = f.Get(key)
    out = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())], float); f.Close(); return out
# ordering check: the D1 driver ROOT vs the xsec captured in the npz
for t in ("eavail", "q3", "nominal"):
    a = flat(f"{RUNS}/drv/driver_{t}.root"); b = L(f"{RUNS}/drv/driver_{t}.npz")["xsec_flat"]
    print("order check", t, a.size, b.size, "max rel %.2e" % np.max(np.abs(a - b) / np.maximum(np.abs(b), 1e-300)))
drv = U @ flat(f"{S5N}/c7/xsec_5d_driver_negweight_F2.root")
d0 = U @ L(f"{RUNS}/drv/data_b0.npz")["xsec_flat"]
ns = U @ L(f"{RUNS}/rep/rep_data_nosentinel.npz")["xsec_flat"]
j1 = U @ L(f"{RUNS}/rep/rep_data_jitteredge1.npz")["xsec_flat"]
j2 = U @ L(f"{RUNS}/rep/rep_data_jitteredge2.npz")["xsec_flat"]
def s(x): x = np.abs(x); return "max %.3f%% (%s) med %.3f%%" % (100 * x.max(), NAMES[int(x.argmax())], 100 * np.median(x))
orig = R(drv, d0); masked = R(drv, ns)
print("driver vs npz b0:", s(orig)); print("driver vs npz nosentinel:", s(masked))
print("driver vs jitteredge1:", s(R(drv, j1))); print("driver vs jitteredge2:", s(R(drv, j2)))
sc = np.maximum(np.abs(R(j1, d0)), np.abs(R(j2, d0)))
print("probe scale (max of 2 seeds per functional): max %.3f%% med %.3f%%" % (100 * sc.max(), 100 * np.median(sc)))
print("functionals where |driver-npz| > probe scale:", int((np.abs(orig) > sc).sum()), "of 153")
mv = np.abs(np.abs(orig) - np.abs(masked)); mv2 = np.abs(orig - masked)
print("functionals where mask moves |diff| by > probe:", int((mv > sc).sum()), " signed diff moved > probe:", int((mv2 > sc).sum()))
print("  of those, mask SHRINKS |diff|:", int(((mv2 > sc) & (np.abs(masked) < np.abs(orig))).sum()))
# a 3-draw rounding ensemble (b0, j1, j2): spread per functional
ens = np.vstack([d0, j1, j2]); sd = ens.std(0, ddof=1) / ens.mean(0)
z = orig / sd
print("driver-npz diff in units of 3-draw rounding SD: median |z| %.2f, max %.2f, n>3: %d" % (np.median(np.abs(z)), np.abs(z).max(), int((np.abs(z) > 3).sum())))
# EW-only view
print("EW-only: driver-npz", s(orig[:42]), "| probe med %.3f%%" % (100 * np.median(sc[:42])))
ev = json.load(open(f"{S5N}/c7/ev_driver_negweight.json"))
for c in ev["calls"]:
    if c.get("site", "").endswith("refine_stay_positive"):
        e = c.get("evidence", {}); print("driver refinement:", {k: e.get(k) for k in ("refined_sum", "n_clipped", "signed_sum", "clipped_fraction")})
