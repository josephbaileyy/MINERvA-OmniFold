#!/usr/bin/env python3
"""Slide figure: step 1 measured against the target its OWN loss function implies.

THE IDENTITY. OmniFold step 1 trains a classifier to separate data from simulation at
reco level. The loader normalizes the MC side to 1e6 and the data side to 1e6*R. If the
fitted classifier attained the POPULATION minimizer of the weighted cross-entropy it is
actually trained on, then averaging its implied likelihood ratio over the MC leg -- under
the same weights used in training -- returns exactly the ratio of the two class totals,
i.e. R. So R is a self-consistency target the method hands us for free.

  R = 1.1240802949941018

WHAT THE MISS MEASURES. Total deviation from the population optimum. It does NOT
decompose: finite-sample gap, optimization gap and approximation error all live inside it.
The miss is a measurement; its interpretation is open.

DATA, all TRANSCRIBED from committed records.
  DEFAULT schedule, n=1 clean trajectory.
    FINDING-20260807-step1-under-achieves.md sec 7, job 56445883 (the BEN-043 re-train).
    pull_final mean_w_reco | pass_reco = 0.658944.  This run is BIT-FAITHFUL:
    push_stored == push_final to all printed digits, reconstruction_is_checkpoint_based
    = false.  The SUPERSEDED run (56445667, 0.765031 -> 68.1%) is NOT plotted: its
    terminal pull mixes a faithful and an unfaithful checkpoint reload and is the number
    most exposed to that caveat.  It belongs on the checkpoint slide as the clue that
    triggered the audit, never in this count.

  ANNEALED schedule, n=5 REPLICATES (not independent configurations -- they differ only
    in process, node and GPU; VL130's premise).  pull_mean_w_reco at the terminal
    iteration, from each draw's STEP1_TRAJECTORY receipt, checkpoint tier final(BEN-043),
    reproduction_gate all-ok on every draw.

CAVEAT THAT MUST TRAVEL: the contrast is 1 vs 5, not a balanced two-arm design, and the
annealed schedule was SELECTED because it improves this metric -- it cannot be offered as
independent evidence.  Say both out loud.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

R = 1.1240802949941018
DEFAULT_PULL = 0.658944                     # job 56445883, bit-faithful
ANNEALED = {"draw 3": 0.987231, "draw 1": 1.007905, "draw 2": 1.015056,
            "draw 5": 1.029394, "draw 4": 1.051189}

def pct(v):
    return 100.0 * v / R

fig, ax = plt.subplots(figsize=(11.8, 5.9))

xs_def = np.array([0.0])
xs_ann = np.arange(1.55, 1.55 + 0.62 * len(ANNEALED), 0.62)[:len(ANNEALED)]

ax.axhline(100.0, color="black", lw=2.2, zorder=6)
ax.annotate("R = 1.124  —  what a converged step 1 returns by construction",
            xy=(xs_ann[-1] + 0.40, 102.0), ha="right", fontsize=11.5,
            fontweight="bold", color="black")

ax.bar(xs_def, [pct(DEFAULT_PULL)], width=0.52, color="#c2472a",
       edgecolor="black", linewidth=1.2, zorder=4)
ax.bar(xs_ann, [pct(v) for v in ANNEALED.values()], width=0.46, color="#3d6b9c",
       edgecolor="black", linewidth=1.1, zorder=4)

ax.annotate(f"{pct(DEFAULT_PULL):.1f}%", (xs_def[0], pct(DEFAULT_PULL)),
            textcoords="offset points", xytext=(0, 9), ha="center",
            fontsize=19, fontweight="bold", color="#c2472a")
for x, v in zip(xs_ann, ANNEALED.values()):
    ax.annotate(f"{pct(v):.1f}%", (x, pct(v)), textcoords="offset points",
                xytext=(0, 8), ha="center", fontsize=11.5, fontweight="bold",
                color="#2c5580")

ax.text(xs_def[0], 118, "DEFAULT schedule\nONE observed trajectory",
        ha="center", va="bottom", fontsize=12, fontweight="bold", color="#c2472a")
ax.text(float(np.mean(xs_ann)), 118,
        "ANNEALED schedule\nfive REPLICATES — differing only in process / node / GPU",
        ha="center", va="bottom", fontsize=12, fontweight="bold", color="#2c5580")

ax.set_ylim(0, 140)
ax.set_xlim(-0.62, xs_ann[-1] + 0.46)
ax.set_yticks([0, 20, 40, 60, 80, 100])
ax.set_xticks(list(xs_def) + list(xs_ann))
ax.set_xticklabels(["run B"] + list(ANNEALED.keys()), fontsize=10.5)
ax.set_ylabel("step 1's attainment of its own fitted target  (% of R)", fontsize=12.5)
ax.set_title("Step 1 can tell you what its own answer should be.\n"
             "In every trajectory we can measure cleanly, it did not get there.",
             fontsize=14.5, fontweight="bold", pad=14)
for s_ in ("top", "right"):
    ax.spines[s_].set_visible(False)
ax.grid(axis="y", ls=":", alpha=0.45, zorder=0)

fig.text(0.5, -0.09,
         "The miss measures TOTAL deviation from the population optimum and does not "
         "decompose it — finite-sample, optimization and approximation error all sit inside.\n"
         "n = 6 clean trajectories.  The 1-vs-5 contrast is not a balanced design, and the "
         "annealed schedule was chosen BECAUSE it improves this metric.\n"
         "Default: FINDING-20260807 sec 7, job 56445883, bit-faithful.  Annealed: five "
         "STEP1_TRAJECTORY receipts, tier final(BEN-043), reproduction gate all-ok.",
         ha="center", va="top", fontsize=9.3, style="italic", color="#333333")
fig.tight_layout()
fig.savefig("docs/sep-09-presentation/step1_attainment.png", dpi=200, bbox_inches="tight")
print(f"default {pct(DEFAULT_PULL):.2f}%   annealed "
      f"{min(pct(v) for v in ANNEALED.values()):.2f}-{max(pct(v) for v in ANNEALED.values()):.2f}%")
