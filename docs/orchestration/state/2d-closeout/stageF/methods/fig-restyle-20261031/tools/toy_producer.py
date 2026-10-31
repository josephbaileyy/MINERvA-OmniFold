"""A stand-in producer for selftest.py: the artist kinds of note Figs. 7-14, drawn in an old and a restyled form.

usage: toy_producer.py INPUT.npy OUT_PREFIX [--style restyle-2026-10] [--ulp] [--rgba] [--line-rgba] [--scatter-rgba]
                        [--drop] [--report-ulp] [--timing T]
It reads INPUT.npy, draws a figure (two panels with a step line, error bars, a filled band, bars and a scatter; a heat
map with a colour bar) and saves OUT_PREFIX.png (technote_style writes the .pdf twin), and writes OUT_PREFIX_report.txt.
--style restyle-2026-10 changes only presentation: figure size, fonts, label strings, panel arrangement (a blank third
panel is removed), panel labels and a text note. The defects selftest.py plants:
  --ulp   moves one plotted value by one unit in the last place;
  --rgba  changes the error-bar series' colour;
  --line-rgba changes only the step line's colour (a Line2D with no collection beside it);
  --scatter-rgba changes only the scatter's face colour (a collection);
  --report-ulp moves the reported value by one ulp and leaves the figure alone;
  --drop  leaves one series out;
  --timing T prints a different wall time, which the comparison must ignore."""
import sys

import matplotlib.pyplot as plt
import numpy as np

import technote_style  # noqa: F401

inp, prefix = sys.argv[1], sys.argv[2]
restyle = "--style" in sys.argv and sys.argv[sys.argv.index("--style") + 1] == "restyle-2026-10"
d = np.load(inp)
x, y, e, z = d[0], d[1], d[2], d[3:7]
if "--ulp" in sys.argv:
    y = y.copy()
    y[3] = np.nextafter(y[3], np.inf)
col = "#4C72B0" if "--rgba" not in sys.argv else "#4C72B1"

if restyle:
    plt.rcParams.update({"font.size": 11, "axes.labelsize": 12, "legend.fontsize": 10})
    fig, axs = plt.subplots(2, 1, figsize=(6, 7))
else:
    fig, axs3 = plt.subplots(1, 3, figsize=(13, 4))
    axs3[2].set_axis_off()
    axs = axs3[:2]
ax = axs[0]
ax.step(x, y, where="mid", color="k" if "--line-rgba" not in sys.argv else "#010101", label="data" if not restyle else "Published data")
ax.errorbar(x, y, yerr=e, fmt="o", color=col, label="MINERvA_Tune_v1" if not restyle else "MINERvA Tune v1")
ax.fill_between(x, y - e, y + e, color="#C44E52", alpha=0.3)
if "--drop" not in sys.argv:
    ax.bar(x, 0.5 * y, width=0.4, color="#2ca02c")
ax.scatter(x, y + 1, color="#9467bd" if "--scatter-rgba" not in sys.argv else "#9467be", s=12)
ax.set_xlabel("p_T (GeV/c)" if not restyle else r"$p_T$ (GeV/$c$)")
ax.legend()
im = axs[1].imshow(z, origin="lower", cmap="RdBu_r", vmin=0.7, vmax=1.3)
fig.colorbar(im, ax=axs[1], label="ratio" if not restyle else "Ratio to MINERvA Tune v1")
if restyle:
    for a, lab in zip(axs, ("(a)", "(b)")):
        a.text(0.02, 0.92, lab, transform=a.transAxes)
    fig.text(0.5, 0.01, "panel note", ha="center")
fig.tight_layout()
fig.savefig(prefix + ".png", dpi=60)
t = sys.argv[sys.argv.index("--timing") + 1] if "--timing" in sys.argv else "1.0"
with open(prefix + "_report.txt", "w") as f:
    c2 = float(((y - x) ** 2).sum())
    if "--report-ulp" in sys.argv:
        c2 = float(np.nextafter(c2, np.inf))
    f.write(f"chi2 = {c2:.17g}\nelapsed {t} s\n")
