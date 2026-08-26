#!/usr/bin/env python3
"""Slide figure: where the PET full-event nominal sits relative to its own
50-member bootstrap family, as a function of p_parallel.

EVERY NUMBER HERE IS TRANSCRIBED FROM THE COMMITTED OI-126 RECORD
(docs/OPEN_ITEMS.md, row OI-126), measured on the 257 quotable cells with
nominal 56989462 against the VL132 family 56936015. This script re-plots
recorded summary statistics; it does not re-measure the family, and it must
not be cited as a measurement.

THE THREE BANDS USE THE THREE STATISTICS THE RECORD USES, AND THEY ARE NOT
THE SAME STATISTIC -- that is stated on the figure so a reader cannot take
the bar lengths as one quantity. The bands also do not partition the 257
cells (128 + 63 + 45 = 236); the remaining 21 are not characterised in the
row and are not shown.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (label, n_cells, signed fraction, recorded statistic verbatim-ish)
BANDS = [
    (r"$p_\parallel < 6$ GeV",      128,  4/128,
     "4 of 128 cells outside the\nfull 50-draw range\n(median $z=-0.13$)"),
    (r"$p_\parallel$ 6$-$20 GeV",    63,  44/63,
     "44 of 63 cells: nominal\nexceeds ALL FIFTY replicas\n(median 1.21$\\times$ the largest draw)"),
    (r"$p_\parallel > 20$ GeV",      45, -44/45,
     "44 of 45 cells: nominal\nlies BELOW the family mean\n(the sign reverses)"),
]

HIGH, LOW, OK = "#c2472a", "#2a5fa5", "#8a8f98"

fig, ax = plt.subplots(figsize=(12.5, 5.6))
ys = [2, 1, 0]
for (lab, n, frac, note), y in zip(BANDS, ys):
    col = OK if abs(frac) < 0.10 else (HIGH if frac > 0 else LOW)
    ax.barh(y, frac, height=0.34, color=col, edgecolor="black", linewidth=0.8, zorder=3)
    # annotation ABOVE the bar, growing back toward the zero line -> never collides
    ha = "right" if frac >= 0 else "left"
    ax.text(frac, y + 0.24, note, va="bottom", ha=ha, fontsize=10.5, zorder=4,
            linespacing=1.35)

ax.axvline(0, color="black", lw=1.3, zorder=2)
ax.set_xlim(-1.1, 1.1)
ax.set_ylim(-0.5, 2.95)
ax.set_yticks(ys)
ax.set_yticklabels([f"{lab}\n({n} cells)" for lab, n, _, _ in BANDS], fontsize=12.5)
ax.tick_params(axis="y", length=0, pad=10)
for t in ax.get_yticklabels():
    t.set_fontweight("bold")
ax.set_xticks([-1, -0.5, 0, 0.5, 1])
ax.set_xticklabels(["100%\nnominal LOW", "50%", "0", "50%", "100%\nnominal HIGH"], fontsize=11)
ax.set_xlabel("fraction of cells in the band   (sign = which way the nominal sits)",
              fontsize=12.5, labelpad=8)
ax.set_title("The PET full-event nominal is not inside its own bootstrap family —\n"
             "and the disagreement is organized in $p_\\parallel$, not scattered",
             fontsize=14, fontweight="bold", pad=16)
for s_ in ("top", "right", "left"):
    ax.spines[s_].set_visible(False)
ax.grid(axis="x", ls=":", alpha=0.45, zorder=0)

fig.text(0.5, -0.055,
         "Three DIFFERENT recorded statistics — bar lengths are not one quantity.   "
         "Bands do not partition the 257 quotable cells (236 shown).\n"
         "The nominal's own integral sits at the 98th percentile of the 50 member totals.   "
         "Recorded in OI-126; re-plotted, not re-measured.",
         ha="center", va="top", fontsize=9.5, style="italic", color="#333333")

fig.tight_layout()
fig.savefig("docs/sep-09-presentation/pet_bootstrap_anomaly.png", dpi=200, bbox_inches="tight")
print("wrote docs/sep-09-presentation/pet_bootstrap_anomaly.png")
