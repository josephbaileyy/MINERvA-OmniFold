#!/usr/bin/env python3
"""Survey figure: dimensionality of MINERvA differential cross-section unfolding
over time, situating this work's unbinned-OmniFold 3D result.

Representative (non-exhaustive) set of published MINERvA differential
measurements, drawn from the MINERvA data-release page
(https://minerva.fnal.gov/data-release-page/). 'dims' = the maximum number of
kinematic variables unfolded *simultaneously* (a double-differential
dsigma/dx dy counts as 2). Every prior MINERvA result uses binned D'Agostini
iterative Bayesian unfolding (IBU) and reaches at most 2 variables; this work
uses unbinned OmniFold and reaches 3.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# (year, dims, label-or-None, kind)  kind: 'binned' | 'this2d' | 'this3d'
M = [
    (2013, 1, None,                                              "binned"),  # 1305.2234 nubar QE
    (2014, 1, None,                                              "binned"),  # 1403.2103 nuclear ratios
    (2015, 1, "CC 1$\\pi^+$",                                    "binned"),  # 1406.6415
    (2017, 1, None,                                              "binned"),  # 1708.03723 CC pi0
    (2018, 2, None,                                              "binned"),  # 1801.01197 nubar QE (pT,p||)
    (2018, 2, "$\\mu$-p TKI",                                    "binned"),  # 1805.05486
    (2019, 2, None,                                              "binned"),  # 1811.02774 QE-like 2D
    (2020, 2, None,                                              "binned"),  # 1910.08658 QE-like mu&p
    (2020, 2, "CC-incl 3.5 GeV\n($p_T$, $p_\\parallel$)",       "binned"),  # 2002.12496
    (2021, 2, "CC-incl 6 GeV\n($p_T$, $p_\\parallel$)  [target]","binned"),  # 2106.16210
    (2023, 2, None,                                              "binned"),  # 2209.07852 CC1pi+ mu&pi
    (2024, 2, "$\\nu_e$ low-$Q^2$\n($E_{\\rm avail}$, $p_T$)",  "binned"),  # 2312.16631
    (2025, 2, None,                                              "binned"),  # 2503.15047 A-dep TKI
    (2026, 2, "this work\nunbinned ($p_T$, $p_\\parallel$)",      "this2d"),
    (2026, 3, "this work — unbinned OmniFold\n($p_T$, $p_\\parallel$, $E_{\\rm avail}$)", "this3d"),
]

style = {
    "binned": dict(marker="o", s=72, c="#4C72B0", edgecolors="k", lw=0.6, zorder=3),
    "this2d": dict(marker="s", s=100, c="#C44E52", edgecolors="k", lw=0.8, zorder=4),
    "this3d": dict(marker="*", s=420, c="#C44E52", edgecolors="k", lw=0.9, zorder=5),
}

fig, ax = plt.subplots(figsize=(8.8, 5.0))
ax.axhspan(0.5, 2.5, color="#4C72B0", alpha=0.07, zorder=0)
ax.text(2012.9, 2.47, "binned D'Agostini IBU: $\\leq 2$ variables unfolded simultaneously",
        fontsize=8.5, va="top", ha="left", color="#33558b", style="italic")

# jitter x for collisions at the same (year, dim)
seen = {}
for yr, d, lab, kind in M:
    n = seen.get((yr, d), 0); seen[(yr, d)] = n + 1
    xj = yr + (0.16 * n if kind == "binned" else 0.0)
    ax.scatter([xj], [d], **style[kind])
    if lab and kind == "binned":
        # per-label nudges to avoid the 2020/2021 collision
        dx, dy, ha = 0.0, 0.17, "center"
        if lab.startswith("CC-incl 3.5"):
            dx, dy, ha = -0.7, 0.34, "center"
        elif lab.startswith("CC-incl 6"):
            dx, dy, ha = 0.55, 0.15, "center"
        ax.annotate(lab, (xj, d), (xj + dx, d + dy), fontsize=7.8, ha=ha,
                    va="bottom", color="0.15")

ax.annotate("this work\nunbinned ($p_T$, $p_\\parallel$)", (2026, 2), (2025.6, 1.66),
            fontsize=8.2, ha="right", va="top", color="#C44E52", weight="bold")
ax.annotate("this work — unbinned OmniFold\n($p_T$, $p_\\parallel$, $E_{\\rm avail}$)",
            (2026, 3), (2025.55, 3.0), fontsize=8.8, ha="right", va="center",
            color="#C44E52", weight="bold")

ax.set_xlabel("Publication year")
ax.set_ylabel("Kinematic variables unfolded simultaneously")
ax.set_title("MINERvA differential cross-section unfolding: dimensionality over time")
ax.set_yticks([1, 2, 3])
ax.set_ylim(0.4, 3.55)
ax.set_xlim(2012.5, 2026.8)
ax.grid(axis="y", alpha=0.3)

legend = [
    Line2D([], [], marker="o", ls="", mfc="#4C72B0", mec="k", ms=8,
           label="MINERvA, binned D'Agostini IBU (13 measurements shown)"),
    Line2D([], [], marker="s", ls="", mfc="#C44E52", mec="k", ms=8,
           label="this work, unbinned OmniFold (2D)"),
    Line2D([], [], marker="*", ls="", mfc="#C44E52", mec="k", ms=15,
           label="this work, unbinned OmniFold (3D)"),
]
ax.legend(handles=legend, loc="upper left", fontsize=8.3, framealpha=0.95)
fig.tight_layout()
fig.savefig("minerva_unfolding_landscape.png", dpi=150)
print("wrote minerva_unfolding_landscape.png")
