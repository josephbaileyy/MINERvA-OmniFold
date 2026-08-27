#!/usr/bin/env python3
"""Slide figure: what the OmniFold loop does to five identical re-fits.

THE CLAIM THIS FIGURE IS ALLOWED TO MAKE: iteration contracts the ENSEMBLE. It does NOT
do so monotonically for every fit. Draw 3 gets worse before it comes back, and any plot
built from per-iteration INCREMENTS would hide that -- each increment is measured against
its own target, so increments across draws are not comparable. This figure therefore plots
only the CUMULATIVE push, whose target is the same fixed R for every draw.

Do NOT say "expels", "diverges" or "converges" from this figure.

TWO LEGS, AND THEY ARE DIFFERENT OBJECTS -- that is why both panels exist.
  RECO leg  : mean push over pass_reco, weighted by w_reco.  Three iterations available.
  TRUTH leg : mean push over pass_gen (== pass_truth, the same 1,999,928 rows), weighted
              by w_truth.  This is the leg the extracted cross section consumes, and its
              terminal relative sd REPRODUCES VL131 to all printed digits:
                  recomputed 2.0474%  /  5.4614%      VL131 2.0474045%  /  5.461426%
              Two iterations available (push_prev = model2 @ iter1, push_final @ iter2).

CHECKPOINT-TIER EXPOSURE IS GRADED, AND THE FIGURE MARKS IT. Measured from the .pkl
histories of all five draws:
  iteration 0 : MOST exposed. iter0_step1 has BEST_IS_LAST=False in 5/5 with val-loss
                gaps up to 6.4% (e.g. 0.115662 best vs 0.123073 last). The last-epoch
                weights for this iteration were never written to disk at all, so no job
                can recover them.
  iteration 1 : mildly exposed. iter1_step2 BEST_IS_LAST=False in 5/5, but gaps are
                0.06-0.11%.
  iteration 2 : clean. _final checkpoints exist, and the stored push is
                reconstruction-free (Gate B(i) bit-exact, max_rel_dev 0.0).
So the dramatic iteration-0 number is the one LEAST entitled to be dramatic. Say it.

Sources: five STEP1_TRAJECTORY receipts (reco leg, per iteration) and five
STEP1_DECOMPOSITION receipts (truth leg, push_prev / push_final), rooted at
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/ --

    draw 1  fullevent_ml_ensemble/member_1/trajectory/{...}.slurm-56847059_1.json
    draw 2  fullevent_floor_42_0/draw_2/{...}.slurm-56863958_2.json
    draw 3  fullevent_floor_42_0/draw_3/{...}.slurm-56863958_3.json
    draw 4  fullevent_floor_42_0/draw_4/{...}.slurm-56863958_4.json
    draw 5  fullevent_floor_42_0/draw_5/{...}.slurm-56863958_5.json

DRAW 1 IS NOT IN THE FLOOR DIRECTORY, AND THAT NEEDS ITS OWN PARAGRAPH. It is
Gate-6 ML-ensemble member 1, reused as the Leg F family's first draw because it
carries the same pin, (estimator, subsample) = (42, 0). It is also the ONLY
passing member of a family whose verdict is BLOCK_GATE6_ML_ENSEMBLE and whose
first prohibition is do_not_select_passing_subset -- so the appearance is bad and
the defence must be measured, not argued. It is measured: this figure reads Leg F,
the family VL130/VL131 define, and every draw reproduces its VL131 slot. Checking
T_d/mean(T) from VL131 against push_d/mean(push) from these receipts gives, in
order, agreement of 4.8e-07 / 7.3e-08 / 2.0e-07 / 4.1e-08 / 3.1e-07, and the
recomputed relative sd is 2.0474040% against VL131's recorded 2.0474045%. ML
ensemble members 2-5 are a different object and are NOT on this plot.

ONE PROVENANCE ASYMMETRY, RECORDED RATHER THAN SMOOTHED. Draw 1 ran with
override_used=true against an archived pre-Gate-5-rerun copy of the target, hash-
bound to 544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9. Draws
2-5 ran with override_used=false and their receipts record sha256=null for the
target. Identical targets are therefore the LEDGER'S ASSERTION and consistent with
the numbers -- draw 1 sits at 0.99907 of the family mean, draw 3 at 0.96702, so
draw 1 is not the outlier -- but four receipts carry no digest, so these files
cannot demonstrate it.

Checkpoint tiers are ('best-epoch', 'best-epoch', 'final(BEN-043)') in 5/5
receipts, matching VL124.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

R = 1.1240802949941018
DRAWS = ["draw 1", "draw 2", "draw 3", "draw 4", "draw 5"]

RECO = {  # push_mean_w_reco, iterations 0/1/2
    "draw 1": [1.708020, 1.263467, 1.102374],
    "draw 2": [1.548166, 1.248092, 1.119044],
    "draw 3": [0.944283, 1.051759, 1.060143],
    "draw 4": [1.529896, 1.258029, 1.087699],
    "draw 5": [1.821082, 1.292841, 1.132679],
}
TRUTH = {  # mean_w_truth over pass_gen, iterations 1/2
    "draw 1": [1.191812, 1.081987],
    "draw 2": [1.179763, 1.094774],
    "draw 3": [1.039768, 1.047281],
    "draw 4": [1.214502, 1.084497],
    "draw 5": [1.212254, 1.106428],
}
RECO_SD = {0: 22.402, 1: 7.939, 2: 2.560}
TRUTH_SD = {1: 6.245, 2: 2.047}

def relsd(vals):
    v = np.asarray(vals, float)
    return 100.0 * v.std(ddof=1) / v.mean()

fig, axes = plt.subplots(1, 2, figsize=(13.4, 5.7),
                         gridspec_kw={"width_ratios": [1.32, 1.0]})

for ax, data, its, sds, title, leg in (
        (axes[0], RECO, [0, 1, 2], RECO_SD,
         "reco leg  —  mean push over pass_reco", "reco"),
        (axes[1], TRUTH, [1, 2], TRUTH_SD,
         "truth leg  —  the leg the cross section consumes", "truth")):

    ax.axhline(R, color="black", lw=1.8, ls="--", zorder=3)
    _ry = R + 0.025 if leg == "reco" else 1.30
    ax.text(its[0] - 0.24, _ry, "R = 1.124", fontsize=10.5,
            fontweight="bold", va="bottom", ha="left", color="black")

    for name in DRAWS:
        hi = name == "draw 3"
        ax.plot(its, data[name], "-o",
                color="#c2472a" if hi else "#8fa6bd",
                lw=3.0 if hi else 1.7, ms=10 if hi else 6.5,
                markeredgecolor="black", markeredgewidth=1.0 if hi else 0.6,
                zorder=6 if hi else 4, label=name if hi else None)

    ax.annotate("draw 3", xy=(its[0], data["draw 3"][0]),
                textcoords="offset points", xytext=(6, -19),
                fontsize=11.5, fontweight="bold", color="#c2472a")

    for it in its:
        ax.annotate(f"across-refit\nrelative sd\n{sds[it]:.2f}%", (it, 0.30),
                    ha="center", fontsize=10, fontweight="bold", color="#333333")

    ax.set_xticks(its)
    ax.set_xticklabels([f"iteration {i}" for i in its], fontsize=11.5,
                       fontweight="bold")
    ax.set_xlim(its[0] - 0.30, its[-1] + 0.44)
    ax.set_ylim(0.15, 2.00)
    ax.set_title(title, fontsize=12.5, fontweight="bold", pad=9)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.grid(axis="y", ls=":", alpha=0.45, zorder=0)

axes[0].set_ylabel("cumulative push, mean over the leg", fontsize=12.5)
axes[0].text(0, 0.60, "MOST checkpoint-tier exposed —\nlast-epoch weights for this\n"
             "iteration were never saved", ha="center", va="center",
             fontsize=8.8, style="italic", color="#8a5a2a")
axes[1].text(1.5, 1.72, "terminal spread REPRODUCES VL131\n2.0474%  /  range 5.4614%",
             ha="center", va="center", fontsize=9.5, fontweight="bold",
             color="#2c5580")

fig.suptitle("Iteration contracts the ensemble — but not each trajectory monotonically.",
             fontsize=15, fontweight="bold", y=1.015)
fig.text(0.5, -0.10,
         "Cumulative push only: every draw aims at the same fixed R, so the draws are "
         "comparable. Per-iteration increments are NOT — each has its own target.\n"
         "Draw 3's excursion on the reco leg is z = -5.11 -> -11.11 -> -2.57 against the "
         "other four: it gets worse, then comes back. Contraction is an ENSEMBLE statement.\n"
         "Identical data, identical 2,000,000-row subsample, pinned seed, no Poisson draw. "
         "The only differences between draws are process, node and GPU.  The CAUSE is not established.",
         ha="center", va="top", fontsize=9.3, style="italic", color="#333333")
fig.tight_layout()
fig.savefig("docs/sep-09-presentation/loop_trajectories.png", dpi=200,
            bbox_inches="tight")

print("reco  sd:", {i: round(relsd([RECO[d][k] for d in DRAWS]), 3)
                    for k, i in enumerate([0, 1, 2])})
print("truth sd:", {i: round(relsd([TRUTH[d][k] for d in DRAWS]), 3)
                    for k, i in enumerate([1, 2])})
