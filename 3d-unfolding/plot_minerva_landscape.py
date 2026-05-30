#!/usr/bin/env python3
"""Survey figure: dimensionality of the FULL set of MINERvA differential
cross-section unfolding measurements over time, situating this work's
unbinned-OmniFold 3D result.

Population: every differential cross-section measurement on the MINERvA
data-release page (https://minerva.fnal.gov/data-release-page/); flux,
reconstruction, generator-tuning, and total-only (non-differential) entries are
excluded. 'dims' = number of kinematic variables unfolded *simultaneously*
(a double-differential dsigma/dx dy = 2), classified from each analysis's
headline differential result. Every prior MINERvA measurement uses binned
D'Agostini IBU and reaches at most 2 variables; this work's unbinned OmniFold
reaches 3.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# (year, dims, channel, arxiv)   channel keys -> color/label below
M = [
    (2013, 2, "qe",    "1305.2243"),
    (2013, 2, "qe",    "1305.2234"),
    (2014, 1, "ratio", "1403.2103"),
    (2014, 1, "pion",  "1409.3835"),
    (2015, 1, "pion",  "1406.6415"),
    (2015, 1, "qe",    "1409.4497"),
    (2015, 1, "pion",  "1503.02107"),
    (2016, 2, "nue",   "1509.05729"),
    (2016, 2, "pion",  "1606.07127"),
    (2016, 2, "dis",   "1601.06313"),
    (2016, 1, "dis",   "1604.03920"),  # CC K+
    (2017, 2, "pion",  "1708.03723"),
    (2017, 1, "qe",    "1705.03791"),  # nuclear-dependence ratio
    (2018, 2, "qe",    "1801.01197"),
    (2018, 2, "qe",    "1805.05486"),
    (2018, 2, "pion",  "1711.01178"),
    (2019, 2, "qe",    "1811.02774"),
    (2019, 2, "pion",  "1906.08300"),
    (2020, 2, "incl",  "2002.12496"),
    (2020, 2, "qe",    "1910.08658"),
    (2020, 2, "qe",    "1912.09890"),
    (2020, 1, "pion",  "2002.05812"),
    (2021, 2, "incl",  "2106.16210"),  # the target
    (2022, 2, "qe",    "2203.08022"),
    (2022, 1, "incl",  "2110.13372"),
    (2023, 2, "pion",  "2209.07852"),
    (2023, 1, "pion",  "2210.01285"),  # coherent
    (2023, 1, "qe",    "2310.17014"),  # multi-neutron low-Eavail
    (2024, 2, "nue",   "2312.16631"),
    (2025, 2, "qe",    "2503.15047"),
]

chan = {
    "incl":  ("#1f77b4", "CC inclusive"),
    "qe":    ("#2ca02c", "CCQE / QE-like (incl. TKI)"),
    "pion":  ("#ff7f0e", "Pion production (CC & coherent)"),
    "dis":   ("#9467bd", "DIS / kaon"),
    "nue":   ("#8c564b", r"$\nu_e$"),
    "ratio": ("#7f7f7f", "Nuclear-target ratio"),
}

fig, ax = plt.subplots(figsize=(9.4, 5.2))
ax.axhspan(0.5, 2.5, color="#1f77b4", alpha=0.06, zorder=0)
ax.text(2012.6, 2.47, "binned D'Agostini IBU: $\\leq 2$ variables unfolded "
        "simultaneously  ($N=30$ measurements)", fontsize=8.5, va="top",
        ha="left", color="#33558b", style="italic")

# jitter x for collisions at the same (year, dim)
seen = {}
for yr, d, c, ax_id in M:
    n = seen.get((yr, d), 0); seen[(yr, d)] = n + 1
    xj = yr + (0.0 if n == 0 else (0.16 * ((n + 1) // 2) * (1 if n % 2 else -1)))
    ax.scatter([xj], [d], marker="o", s=62, c=chan[c][0],
               edgecolors="k", lw=0.5, zorder=3)

# this work
ax.scatter([2026], [2], marker="s", s=110, c="#C44E52", edgecolors="k",
           lw=0.9, zorder=4)
ax.scatter([2026], [3], marker="*", s=460, c="#C44E52", edgecolors="k",
           lw=1.0, zorder=5)
ax.annotate("this work\nunbinned ($p_T$, $p_\\parallel$)", (2026, 2), (2025.7, 1.62),
            fontsize=8.2, ha="right", va="top", color="#C44E52", weight="bold")
ax.annotate("this work — unbinned OmniFold\n($p_T$, $p_\\parallel$, $E_{\\rm avail}$)",
            (2026, 3), (2025.6, 3.02), fontsize=9.0, ha="right", va="center",
            color="#C44E52", weight="bold")
ax.annotate("[target]\n2106.16210", (2021, 2), (2021, 2.18), fontsize=7.0,
            ha="center", va="bottom", color="#1f77b4")

ax.set_xlabel("Publication year")
ax.set_ylabel("Kinematic variables unfolded simultaneously")
ax.set_title("MINERvA differential cross-section unfolding: dimensionality over time")
ax.set_yticks([1, 2, 3])
ax.set_ylim(0.4, 3.55)
ax.set_xlim(2012.3, 2026.9)
ax.grid(axis="y", alpha=0.3)

handles = [Line2D([], [], marker="o", ls="", mfc=col, mec="k", ms=8, label=lab)
           for col, lab in chan.values()]
handles += [
    Line2D([], [], marker="s", ls="", mfc="#C44E52", mec="k", ms=8,
           label="this work, OmniFold (2D)"),
    Line2D([], [], marker="*", ls="", mfc="#C44E52", mec="k", ms=15,
           label="this work, OmniFold (3D)"),
]
ax.legend(handles=handles, loc="upper left", fontsize=8.0, framealpha=0.95,
          ncol=2)
fig.tight_layout()
fig.savefig("minerva_unfolding_landscape.png", dpi=150)
print("wrote minerva_unfolding_landscape.png with", len(M), "prior measurements")
