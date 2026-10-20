#!/usr/bin/env python3
"""M3 figure 1: nominal-truth closure residual, purity subtraction vs the unbinned negative-weight refinement.

Both arms use the same estimator, s5c candidate F2 (deterministic LightGBM OmniFold, 5 iterations, 100 trees,
8 leaves), background-inclusive pseudo-experiments at nominal truth, development seeds:
  purity      s5c D1 split_F2 group, 9 experiments    (state/s5c/d1/d1_summary.json)
  refined     s5n family N C3_nominal, 60 experiments (state/s5n/stage1/dev_receipt.json): F2 with the
              driver's negweight-refined measured side, refinement classifier 100 trees / 8 leaves
Residual = mean over experiments of (unfolded - truth) / truth; error bar = its standard error.

  python3 fig_m3_background.py [--repo CHECKOUT] [--outdir DIR]
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import m3_common as mc
from m3_common import plt


def main() -> None:
    a = mc.parse_args(__doc__, Path(__file__).resolve().parent / "out")
    d1, s5n = mc.load(a.repo, "d1_summary"), mc.load(a.repo, "s5n_dev")
    names = d1["functional_names"]
    assert s5n["functional_names"] == names
    g = d1["groups"]["split_F2"]
    c3 = s5n["grid"]["C3_nominal"]
    assert g["n_experiments"] == 9 and c3["n_experiments"] == 60
    pur, pur_se = 100 * np.array(g["mean_rel"]), 100 * np.array(g["se_rel"])
    ref, ref_se = 100 * np.array(c3["per_functional"]["mean_rel"]), 100 * np.array(c3["per_functional"]["se_rel"])

    ew = [names.index(f"EW{i}") for i in range(mc.N_EW)]
    jj = [i for i, n in enumerate(names) if n.startswith("J")] + [names.index("total_integrated")]
    high_w = [names.index(f"EW{6 * k + 5}") for k in range(7)]  # highest-W column of the (E_avail, W) projection

    # Reproduce paper_body.tex :521-530 before drawing.
    nums = [
        mc.check("purity: max |residual| over the 7 highest-W (E_avail,W) cells (paper 'up to 4%'), %",
                 round(float(np.max(np.abs(pur[high_w]))), 2) == 4.11, round(float(np.max(np.abs(pur[high_w]))), 3)),
        mc.check("purity: max |residual| over all 153 functionals is in the highest-W column (EW29), %",
                 names[int(np.argmax(np.abs(pur)))] == "EW29", names[int(np.argmax(np.abs(pur)))]),
        mc.check("refined: max |residual| over the 7 highest-W cells < 0.3% (paper 'below 0.3%'), %",
                 float(np.max(np.abs(ref[high_w]))) < 0.3, round(float(np.max(np.abs(ref[high_w]))), 3)),
        mc.check("refined: max |residual| over the 109 J cells (paper 'up to 1% in some joint cells'), %",
                 round(float(np.max(np.abs(ref[jj[:-1]]))), 1) == 1.0,
                 (round(float(np.max(np.abs(ref[jj[:-1]]))), 3), names[jj[int(np.argmax(np.abs(ref[jj[:-1]])))]])),
        mc.check("data: max |refined - purity| (paper 'at most 1.4%'; not plotted), %",
                 round(s5n["controls"]["C7"]["rel_diff_max_abs_pct"], 1) == 1.4,
                 round(s5n["controls"]["C7"]["rel_diff_max_abs_pct"], 3)),
    ]
    nums.append({"claim": "refined: max |residual| over all 42 (E_avail,W) cells (outside the highest-W column), %",
                 "value": [round(float(np.max(np.abs(ref[ew]))), 3), names[ew[int(np.argmax(np.abs(ref[ew])))]]]})

    mc.style()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.0, 4.2), gridspec_kw={"hspace": 0.62})
    fig.subplots_adjust(left=0.075, right=0.985, top=0.93, bottom=0.09)
    lab_p = "purity-based subtraction (9 experiments)"
    lab_r = "unbinned negative-weight refinement (60 experiments)"
    x = np.arange(mc.N_EW)
    ax1.axhline(0, color="k", lw=0.6)
    ax1.errorbar(x - 0.17, pur[ew], pur_se[ew], fmt="o", ms=3.0, color=mc.BLUE, lw=0.8, label=lab_p)
    ax1.errorbar(x + 0.17, ref[ew], ref_se[ew], fmt="s", ms=2.8, color=mc.RED, lw=0.8, label=lab_r)
    mc.ew_axis(ax1)
    ax1.set_xlabel(mc.ew_xlabel(), fontsize=7.5)
    ax1.set_ylabel(r"(unfolded $-$ truth)/truth (%)")
    ax1.set_ylim(-5.0, 3.0)
    ax1.legend(loc="upper left", frameon=False, ncol=2)
    ax1.text(0.0, 1.10, r"(a) $(E_{\rm avail},W)$ projection, 42 cells", transform=ax1.transAxes, fontsize=8)

    xj = np.arange(len(jj))
    ax2.axhline(0, color="k", lw=0.6)
    ax2.errorbar(xj - 0.17, pur[jj], pur_se[jj], fmt="o", ms=2.4, color=mc.BLUE, lw=0.7, label=lab_p)
    ax2.errorbar(xj + 0.17, ref[jj], ref_se[jj], fmt="s", ms=2.2, color=mc.RED, lw=0.7, label=lab_r)
    ax2.axvline(len(jj) - 1.5, color="0.6", lw=0.6, ls=":")
    ax2.set_xlim(-1, len(jj))
    ticks = [k for k in range(len(jj) - 4) if k % 6 == 0] + [len(jj) - 1]
    ax2.set_xticks(ticks)
    ax2.set_xticklabels([names[jj[k]].lstrip("J") if k < len(jj) - 1 else "total" for k in ticks], fontsize=6.0, rotation=0)
    ax2.set_xlabel("coarse joint cell: index in the $3^5$ grid (109 reported cells), then the total "
                   "integrated cross section", fontsize=7.5)
    ax2.set_ylabel(r"(unfolded $-$ truth)/truth (%)")
    ax2.set_ylim(-2.5, 3.2)
    ax2.text(0.0, 1.04, "(b) joint-cell integrals and total", transform=ax2.transAxes, fontsize=8)
    # (X5 Gm9: the in-plot estimator header moved to the article caption.)
    mc.save(fig, a.outdir, "m3_fig1_background")
    (a.outdir / "m3_fig1_background_numbers.json").write_text(json.dumps(nums, indent=1) + "\n")


if __name__ == "__main__":
    main()
