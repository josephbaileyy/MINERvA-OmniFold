#!/usr/bin/env python3
"""Slide figure: what the PET C_stat bootstrap family is actually measuring.

Numbers TRANSCRIBED from the committed ledger (VALIDATION_LEDGER.md VL131, VL132):
  Poisson prediction on n_data = 4,116,128 ...... 0.0493 %
  fixed-seed / fixed-data run-to-run spread ..... 2.047 %  (n=5, TERMINAL)  = 41.5x
  full 50-member bootstrap family spread ........ 5.167 %                  = 104.8x
The fixed-seed floor is 15.70 % of the family VARIANCE; residual 4.744 % (96.2x).

CAVEATS THAT TRAVEL WITH VL131 AND MUST STAY ON THE SLIDE: subsample numerator
rather than the published full-inventory total; the quadrature decomposition
assumes independence; n=5, so each sd carries sizable fractional uncertainty; and
attributing the residual to the map's response to the Poisson draw is an
INTERPRETATION, not a measurement. cap_saturation_frac = 0.0 on all five draws,
so none of this is a logit-clipping artefact.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

POISSON = 0.0493
BARS = [
    ("Poisson expectation\n$n_{\\rm data}=4{,}116{,}128$", POISSON, "#8a8f98",
     "what 'statistical' should mean"),
    ("Same seed, same data,\nseparate processes", 2.047, "#c2472a",
     "$41.5\\times$ Poisson  —  nothing was resampled"),
    ("Full 50-member\nbootstrap family", 5.167, "#2a5fa5",
     "$105\\times$ Poisson  —  quoted as $C_{\\rm stat}$"),
]

fig, ax = plt.subplots(figsize=(12.0, 5.0))
ys = [2, 1, 0]
for (lab, val, col, note), y in zip(BARS, ys):
    ax.barh(y, val, height=0.42, color=col, edgecolor="black", linewidth=0.9, zorder=3)
    ax.text(val * 1.10, y, f"  {val:g}%", va="center", ha="left",
            fontsize=13, fontweight="bold", zorder=4)
    ax.text(val * 1.10, y - 0.29, f"  {note}", va="center", ha="left",
            fontsize=10.5, color="#333333", zorder=4)

ax.set_xscale("log")
ax.set_xlim(0.03, 40)
ax.set_ylim(-0.55, 2.6)
ax.set_yticks(ys)
ax.set_yticklabels([b[0] for b in BARS], fontsize=12)
ax.tick_params(axis="y", length=0, pad=10)
for t in ax.get_yticklabels():
    t.set_fontweight("bold")
ax.set_xlabel("relative spread of the extracted total cross section  (%, log scale)",
              fontsize=12.5, labelpad=8)
ax.set_title("The bootstrap 'statistical' uncertainty is ~100$\\times$ Poisson —\n"
             "and a sixth of its variance is there when nothing is resampled",
             fontsize=14, fontweight="bold", pad=16)
for s_ in ("top", "right", "left"):
    ax.spines[s_].set_visible(False)
ax.grid(axis="x", ls=":", alpha=0.45, zorder=0)

fig.text(0.5, -0.05,
         "Fixed-seed floor = 15.70% of the family VARIANCE; residual 4.744% (96.2$\\times$ Poisson).   "
         "cap_saturation_frac = 0.0 on all five draws, so this is not logit clipping.\n"
         "VL131 caveats travel with these numbers: subsample numerator, independence assumed in the "
         "quadrature split, n=5, and the residual's attribution is an INTERPRETATION.",
         ha="center", va="top", fontsize=9.5, style="italic", color="#333333")
fig.tight_layout()
fig.savefig("docs/sep-09-presentation/cstat_variance_budget.png", dpi=200, bbox_inches="tight")
print("wrote docs/sep-09-presentation/cstat_variance_budget.png")
