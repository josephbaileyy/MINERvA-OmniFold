#!/usr/bin/env python3
"""Overlay HistGBT vs exact-GBT 1A iter-scan convergence.

Reads both sets of 1/3/5/8/10-iter ROOT files (exact-GBT in the parent dir,
HistGBT here), then plots three diagnostic panels:
  1. hUnfold2D integral vs iteration
  2. Total cross section (hXSec2D integrated with bin widths) vs iteration
  3. Per-bin relative RMS deviation from each estimator's own 10-iter result
     (shape-convergence — does HistGBT plateau earlier?)

The third panel is the headline answer to "does HistGBT converge faster?".
"""
import os

import ROOT
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


ITERS = [1, 3, 5, 8, 10]
HERE = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
EXACT_PATH = os.path.join(HERE, "2d_crossSection_omnifold_1A_{i}iter.root")
HIST_PATH = os.path.join(HERE, "histgbt_iter_scan",
                         "2d_crossSection_omnifold_1A_{i}iter_histgbt.root")


def load(path):
    f = ROOT.TFile.Open(path)
    h_u = f.Get("hUnfold2D")
    h_x = f.Get("hXSec2D")
    u_int = h_u.Integral()
    x_tot = h_x.Integral("width")
    nx, ny = h_x.GetNbinsX(), h_x.GetNbinsY()
    flat = np.array([h_x.GetBinContent(i, j)
                     for j in range(1, ny + 1)
                     for i in range(1, nx + 1)])
    f.Close()
    return u_int, x_tot, flat


def collect(path_tmpl):
    return {it: load(path_tmpl.format(i=it)) for it in ITERS}


def shape_rms(data):
    ref = data[10][2]
    valid = ref > 0
    return {it: float(np.sqrt(np.mean(
        ((data[it][2][valid] - ref[valid]) / ref[valid]) ** 2)))
            for it in ITERS}


exact = collect(EXACT_PATH)
hist = collect(HIST_PATH)

exact_rms = shape_rms(exact)
hist_rms = shape_rms(hist)

print(f"{'iter':>4}  "
      f"{'exact_uInt':>12}  {'exact_xsec':>11}  {'exact_rms':>10}  "
      f"{'hist_uInt':>12}  {'hist_xsec':>11}  {'hist_rms':>10}")
for it in ITERS:
    eu, ex, _ = exact[it]
    hu, hx, _ = hist[it]
    print(f"{it:>4}  "
          f"{eu:>12.0f}  {ex:>11.4e}  {exact_rms[it]:>10.4%}  "
          f"{hu:>12.0f}  {hx:>11.4e}  {hist_rms[it]:>10.4%}")

fig, axs = plt.subplots(1, 3, figsize=(15, 4))

axs[0].plot(ITERS, [exact[it][0] for it in ITERS], "o-",
            color="C0", label="exact GBT")
axs[0].plot(ITERS, [hist[it][0] for it in ITERS], "s--",
            color="C3", label="HistGBT")
axs[0].set_xlabel("OmniFold iterations")
axs[0].set_ylabel("hUnfold2D integral (events)")
axs[0].set_title("Unfolded event-count convergence")
axs[0].legend(loc="best")
axs[0].grid(alpha=0.3)

axs[1].plot(ITERS, [exact[it][1] for it in ITERS], "o-",
            color="C0", label="exact GBT")
axs[1].plot(ITERS, [hist[it][1] for it in ITERS], "s--",
            color="C3", label="HistGBT")
axs[1].set_xlabel("OmniFold iterations")
axs[1].set_ylabel(r"Total $\sigma$ (cm$^2$/nucleon)")
axs[1].set_title("Total cross-section convergence")
axs[1].legend(loc="best")
axs[1].grid(alpha=0.3)

axs[2].semilogy(ITERS, [exact_rms[it] for it in ITERS], "o-",
                color="C0", label="exact GBT")
axs[2].semilogy(ITERS, [hist_rms[it] for it in ITERS], "s--",
                color="C3", label="HistGBT")
axs[2].set_xlabel("OmniFold iterations")
axs[2].set_ylabel("Per-bin rel RMS vs own 10-iter")
axs[2].set_title("Shape convergence")
axs[2].legend(loc="best")
axs[2].grid(alpha=0.3, which="both")

fig.suptitle("1A iteration-scan convergence: exact GBT vs HistGBT "
             "(Phase-18.2 pipeline)", fontsize=12)
fig.tight_layout()
out = os.path.join(HERE, "histgbt_iter_scan",
                   "1A_iterscan_convergence_hist_vs_exact.png")
fig.savefig(out, dpi=130)
print(f"\nwrote {out}")
