#!/usr/bin/env python3
"""M3 figure 3: empirical coverage of the 153 reported functionals, Tier-S look at 400 pseudo-experiments per truth.

Estimator: s5c candidate F2 (deterministic LightGBM OmniFold, 5 iterations, 100 trees, 8 leaves, purity-based
background subtraction); intervals: contract amendment 4's bias-corrected statistical intervals (f_hat/(1+beta)
+- the 68% / 95% half-widths). Receipt state/s5c/tier_s/interim_400.json (nd-unfolding/s5c_coverage.py,
--interim 400 --bias-correction). Coverage = hits / 400. Bars: the receipt's one-sided Clopper-Pearson lower and
upper bounds, each at the gate level alpha = 0.05/459 (Bonferroni over 153 functionals x 3 truths). A functional
is 'confidently below' when its upper bound is below the predeclared gate threshold (0.66 at 68%, 0.94 at 95%).
The receipt's third truth (q3_given_eavail_w) is not drawn: its record classifies it as a construction defect
that the verdict does not use (OUTCOME-20260925-s5c-tier-s-futility-fail.md section 3).

  python3 fig_m3_coverage.py [--repo CHECKOUT] [--outdir DIR]
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import m3_common as mc
from m3_common import plt

THR = {"68": 0.66, "95": 0.94}
NOMINAL = {"68": 0.68, "95": 0.95}


def main() -> None:
    a = mc.parse_args(__doc__, Path(__file__).resolve().parent / "out")
    d = mc.load(a.repo, "tier_s")
    names = d["functional_names"]
    assert d["n_functionals"] == len(names) == 153 and d["interim_n"] == 400 and d["complete"]
    assert abs(d["per_comparison_alpha"] - 0.05 / 459) < 1e-15
    grid = {g["truth"]: g for g in d["grid"]}
    order = ([i for i, n in enumerate(names) if n.startswith("EW")]
             + [i for i, n in enumerate(names) if n.startswith("J")] + [names.index("total_integrated")])
    assert len(order) == 153
    n_ew = sum(n.startswith("EW") for n in names)

    def cov(g, lvl):
        k = np.array(g[f"hits{lvl}"])
        return k / g["n_present"], np.array(g[f"lcb{lvl}"]), np.array(g[f"ucb{lvl}"])

    nom, tilt = grid["nominal"], grid["eavail_tilt"]
    assert nom["n_present"] == tilt["n_present"] == 400 and tilt["amplitude"] == 0.2
    below = {(t, l): int(np.sum(cov(grid[t], l)[2] < THR[l])) for t in ("nominal", "eavail_tilt") for l in ("68", "95")}
    # Reproduce paper_body.tex :560-565 before drawing.
    nums = [
        mc.check("E_avail tilt: functionals with 68% UCB < 0.66 (paper '51 of the 153')",
                 below[("eavail_tilt", "68")] == 51, below[("eavail_tilt", "68")]),
        mc.check("E_avail tilt: lowest 68% coverage (paper 'as low as 0.06')",
                 round(float(cov(tilt, "68")[0].min()), 3) == 0.060,
                 (float(cov(tilt, "68")[0].min()), names[int(np.argmin(cov(tilt, "68")[0]))])),
        mc.check("E_avail tilt: functionals with 95% UCB < 0.94 (paper '42 fail at 95%')",
                 below[("eavail_tilt", "95")] == 42, below[("eavail_tilt", "95")]),
        mc.check("nominal: functionals with 95% UCB < 0.94 (paper 'two fail at 95%')",
                 below[("nominal", "95")] == 2,
                 (below[("nominal", "95")], [names[i] for i in np.flatnonzero(cov(nom, "95")[2] < 0.94)])),
        mc.check("nominal: lowest 95% coverage (paper 'the lowest at 0.85')",
                 round(float(cov(nom, "95")[0].min()), 3) == 0.850,
                 (float(cov(nom, "95")[0].min()), names[int(np.argmin(cov(nom, "95")[0]))])),
        mc.check("nominal: functionals with 68% UCB < 0.66 (paper implies none)", below[("nominal", "68")] == 0,
                 below[("nominal", "68")]),
    ]
    for t in ("nominal", "eavail_tilt"):
        for grp, sel in (("EW", lambda n: n.startswith("EW")), ("J", lambda n: n.startswith("J"))):
            m = np.array([sel(n) for n in names])
            nums.append({"claim": f"{t}: confidently-below counts in group {grp} (68%, 95%)",
                         "value": [int(np.sum((cov(grid[t], l)[2] < THR[l]) & m)) for l in ("68", "95")]})

    mc.style()
    # Layout (methods rewrite, fix round 1, REVIEW-1 P4 and finding 14): only the E_avail-tilt truth is drawn (the
    # nominal-truth counts stay in the numbers file and the caption); ticks are integral indices, not internal names.
    fig, ax = plt.subplots(1, 1, figsize=(7.0, 3.0))
    fig.subplots_adjust(left=0.075, right=0.985, top=0.66, bottom=0.17)
    x = np.arange(153)
    sty = {"68": ("o", mc.BLUE, -0.18), "95": ("s", mc.RED, 0.18)}
    t = "eavail_tilt"
    g = grid[t]
    for l in ("68", "95"):
        c, lo, hi = (v[order] for v in cov(g, l))
        mk, col, dx = sty[l]
        bad = hi < THR[l]
        ax.axhline(NOMINAL[l], color=col, lw=0.7)
        ax.axhline(THR[l], color=col, lw=0.6, ls=(0, (3, 2)))
        ax.vlines(x + dx, lo, hi, color=col, lw=0.5, alpha=0.6)
        ax.plot(x[~bad] + dx, c[~bad], mk, ms=2.4, mfc="white", mec=col, mew=0.6,
                label=f"{l}% interval, upper bound $\\geq$ {THR[l]:.2f}")
        ax.plot(x[bad] + dx, c[bad], mk, ms=2.4, color=col, label=f"{l}% interval, upper bound < {THR[l]:.2f}")
    for xb in (n_ew - 0.5, 152 - 0.5):
        ax.axvline(xb, color="0.45", lw=0.6, ls=":")
    ax.set_ylim(-0.02, 1.13)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_ylabel("empirical coverage")
    ax.set_title(rf"signal rate lowered by about 10% with a weak $E_{{\rm avail}}$ slope: upper bound below the gate for {below[(t, '68')]} (68%) and "
                 f"{below[(t, '95')]} (95%) of 153", fontsize=7.4, loc="left")
    for xc, txt in (((n_ew - 1) / 2, r"$(E_{\rm avail},W)$ cells 0–41 and their sum"),
                    (n_ew + (152 - n_ew) / 2, "109 coarse joint cells, by index in the $3^5$ grid"),
                    (152.6, "total")):
        ax.text(xc, 1.075, txt, ha="right" if txt == "total" else "center", va="center", fontsize=6.4, color="0.3")
    ticks = [0, 10, 20, 30, 41] + list(range(n_ew + 7, 150, 15)) + [152]
    ax.set_xticks(ticks)
    ax.set_xticklabels([names[order[k]].lstrip("EWJ") if k < 152 else "total" for k in ticks], fontsize=5.8, rotation=0)
    ax.set_xlim(-1, 153)
    ax.set_xlabel("cell index (projection cell, or coarse joint cell in the $3^5$ grid), then the total", labelpad=2)
    fig.text(0.075, 0.995, "\n".join([
        "Estimator: deterministic LightGBM OmniFold (5 iterations, 100 trees, 8 leaves)",
        "with purity-based background subtraction; statistical intervals corrected",
        "for the nominal-truth bias; 400 pseudo-experiments.",
        "Solid lines: nominal 0.68 / 0.95. Dashed: predeclared gate 0.66 / 0.94.",
        r"Bars: one-sided Clopper–Pearson bounds, each at $\alpha=0.05/459$."]),
        ha="left", va="top", fontsize=6.6, color="0.2")
    h, lab = ax.get_legend_handles_labels()
    fig.legend(h, lab, loc="upper right", bbox_to_anchor=(0.99, 0.995), ncol=1, frameon=False, fontsize=6.6,
               handletextpad=0.3)
    mc.save(fig, a.outdir, "m3_fig3_coverage")
    (a.outdir / "m3_fig3_coverage_numbers.json").write_text(json.dumps(nums, indent=1) + "\n")


if __name__ == "__main__":
    main()
