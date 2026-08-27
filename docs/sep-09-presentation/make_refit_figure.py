#!/usr/bin/env python3
"""Slide figure: the same fit, five times, on the same data.

Numbers TRANSCRIBED from VALIDATION_LEDGER.md VL131 (n=5, TERMINAL). Each draw is a
SEPARATE training process at identical data, identical 2,000,000-row subsample,
set_random_seed(42), and NO Poisson draw. T_d = sum_j w_truth[j]*push_d[j] over
pass_truth (1,999,928 pass_truth rows).

Poisson expectation on n_data = 4,116,128 is 0.0493% -- drawn as the hairline band.

CAVEATS THAT MUST TRAVEL: subsample numerator, not the published full-inventory
total; n=5; cap_saturation_frac = 0.0 on every draw, so this is not logit clipping.
The CAUSE of the disagreement is NOT established -- do not label it.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

T = np.array([1777414.2639656093, 1798419.1422631375, 1720400.4336576774,
              1781536.5944523546, 1817562.850543105])
MEANPUSH = [1.0776, 1.0913, 1.0472, 1.0825, None]   # draw 5 mean(push) not recorded
POISSON_REL = 0.000493
m = T.mean()
rel = 100.0 * (T - m) / m

fig, ax = plt.subplots(figsize=(11.5, 5.2))
x = np.arange(1, 6)

ax.axhspan(-100*POISSON_REL, 100*POISSON_REL, color="#8a8f98", alpha=0.55, zorder=2)
ax.axhline(0, color="black", lw=1.0, ls="--", zorder=3)
ax.plot(x, rel, "o", ms=15, color="#c2472a", markeredgecolor="black",
        markeredgewidth=1.1, zorder=5)

for xi, ri, mp in zip(x, rel, MEANPUSH):
    lab = f"{ri:+.2f}%" + (f"\nmean(push)\n{mp}" if mp else "\nmean(push)\nnot recorded")
    ax.annotate(lab, (xi, ri), textcoords="offset points",
                xytext=(0, 20 if ri >= 0 else -52), ha="center", fontsize=10.5, zorder=6)

ax.annotate("Poisson expectation, $\\pm$0.0493%\n(the band, not a line)",
            xy=(5.34, 0), xytext=(5.34, 1.35), fontsize=10.5, style="italic",
            color="#333333", ha="center",
            arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.1))

ax.set_xlim(0.55, 6.0)
ax.set_ylim(-5.1, 3.4)
ax.set_xticks(x)
ax.set_xticklabels([f"re-fit {i}" for i in x], fontsize=12, fontweight="bold")
ax.set_ylabel("extracted total, relative to the mean of the five  (%)", fontsize=12.5)
ax.set_title("Same data. Same subsample. Same seed. No Poisson draw.\n"
             "Five separate training processes, five different cross sections.",
             fontsize=14, fontweight="bold", pad=16)
for s_ in ("top", "right"):
    ax.spines[s_].set_visible(False)
ax.grid(axis="y", ls=":", alpha=0.45, zorder=0)

fig.text(0.5, -0.06,
         f"Full range {100*(T.max()-T.min())/m:.2f}% of the mean;  relative sd 2.047% = "
         "41.5$\\times$ the Poisson expectation.   The learned map is moving, not the data.\n"
         "VL131, n=5, TERMINAL.  Subsample numerator, not the published total.  "
         "cap_saturation_frac = 0.0 on all five draws.  The CAUSE is not established.",
         ha="center", va="top", fontsize=9.5, style="italic", color="#333333")
fig.tight_layout()
fig.savefig("docs/sep-09-presentation/refit_spread.png", dpi=200, bbox_inches="tight")
print(f"range {100*(T.max()-T.min())/m:.3f}%  sd(rel) {100*T.std(ddof=1)/m:.3f}%")
