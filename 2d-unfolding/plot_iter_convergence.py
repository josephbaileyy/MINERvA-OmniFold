#!/usr/bin/env python3
"""Plot iteration-scan convergence from the 1/3/5/8/10-iter ROOT files.

Outputs three diagnostic panels:
  1. hUnfold2D integral vs iteration
  2. Total cross section (hXSec2D integrated with bin widths) vs iteration
  3. Per-bin relative RMS deviation from 10-iter result vs iteration
     (shape-convergence metric, not just integral)
"""
import ROOT
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ITERS = [1, 3, 5, 8, 10]
PATH = "/pscratch/sd/j/josephrb/MINERvA101/Documents/2d_crossSection_omnifold_1A_corrected_{i}iter.root"


def load(iter_count):
    f = ROOT.TFile.Open(PATH.format(i=iter_count))
    hUnfold = f.Get("hUnfold2D")
    hXSec = f.Get("hXSec2D")
    u_integral = hUnfold.Integral()
    x_total = hXSec.Integral("width")
    nx, ny = hXSec.GetNbinsX(), hXSec.GetNbinsY()
    xsec_flat = np.array([hXSec.GetBinContent(i, j)
                          for j in range(1, ny + 1)
                          for i in range(1, nx + 1)])
    f.Close()
    return u_integral, x_total, xsec_flat


data = {it: load(it) for it in ITERS}
ref_xsec = data[10][2]
valid = ref_xsec > 0
rel_rms = {it: float(np.sqrt(np.mean(((data[it][2][valid] - ref_xsec[valid])
                                      / ref_xsec[valid]) ** 2)))
           for it in ITERS}

u_vals = [data[it][0] for it in ITERS]
x_vals = [data[it][1] for it in ITERS]
rms_vals = [rel_rms[it] for it in ITERS]

fig, axs = plt.subplots(1, 3, figsize=(15, 4))

axs[0].plot(ITERS, u_vals, "o-", color="C0")
axs[0].set_xlabel("OmniFold iterations")
axs[0].set_ylabel("hUnfold2D integral (events)")
axs[0].set_title("Unfolded event-count convergence")
axs[0].grid(alpha=0.3)

axs[1].plot(ITERS, x_vals, "o-", color="C1")
axs[1].set_xlabel("OmniFold iterations")
axs[1].set_ylabel(r"Total $\sigma$ (cm$^2$/nucleon)")
axs[1].set_title("Total cross-section convergence")
axs[1].grid(alpha=0.3)

axs[2].semilogy(ITERS, rms_vals, "o-", color="C2")
axs[2].set_xlabel("OmniFold iterations")
axs[2].set_ylabel("Per-bin relative RMS vs 10-iter")
axs[2].set_title("Shape convergence (vs 10-iter reference)")
axs[2].grid(alpha=0.3, which="both")

fig.suptitle("2D OmniFold iteration-scan convergence (playlist 1A, corrected pipeline)",
             fontsize=12)
fig.tight_layout()
out = "/pscratch/sd/j/josephrb/MINERvA101/Documents/iter_convergence_1A_corrected.png"
fig.savefig(out, dpi=130)
print(f"wrote {out}")

print("\nSummary:")
print(f"  {'iter':>4}  {'hUnfold2D':>12}  {'total xsec':>12}  {'rel RMS vs 10':>14}")
for it in ITERS:
    print(f"  {it:>4}  {data[it][0]:>12.0f}  {data[it][1]:>12.4e}  {rel_rms[it]:>13.4%}")
