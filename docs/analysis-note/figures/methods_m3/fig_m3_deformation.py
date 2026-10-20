#!/usr/bin/env python3
"""M3 figure 2: fractional recovery residual by (E_avail, W) cell, nominal truth and generator-sized deformations.

Left column, s5n family N (state/s5n/stage1/dev_receipt.json): s5c F2 deterministic LightGBM (5 iterations,
100 trees, 8 leaves) with the negweight-refined measured side, refinement classifier 100 trees / 8 leaves;
60 background-inclusive development experiments per truth (C3 nominal, C4 GiBUU/GENIE E_avail shape).
The injected per-cell truth change of C4 is from state/s5n/stage1/truth_check.json (M1_ratio - 1).
Right column, s5e candidate R = the joint-test estimator (state/s5e/cand/assess_receipt.json): family N with the
refinement classifier at 400 trees / 31 leaves; fresh assessment seeds, 40 nominal experiments (A1) and 20 per
withheld truth W1 (NuWro E_avail), W2 (GENIE MEC, (E_avail,W)), W3 (NuWro (pT,p||,E_avail)). The band is the
adopted C_EW total sigma per cell that A4 compares with (assess_receipt A4.adopted_total_sigma_pct).
Residual = mean over experiments of (unfolded - truth) / truth, truth = the deformed truth of each experiment.

  python3 fig_m3_deformation.py [--repo CHECKOUT] [--outdir DIR]
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import m3_common as mc
from m3_common import plt


def per(point: dict) -> tuple[np.ndarray, np.ndarray]:
    pf = point["per_functional"]
    return 100 * np.array(pf["mean_rel"])[: mc.N_EW], 100 * np.array(pf["se_rel"])[: mc.N_EW]


def main() -> None:
    a = mc.parse_args(__doc__, Path(__file__).resolve().parent / "out")
    s5n, truth, s5e = mc.load(a.repo, "s5n_dev"), mc.load(a.repo, "s5n_truth"), mc.load(a.repo, "s5e_assess")
    names = s5n["functional_names"]
    assert s5e["functional_names"] == names and names[: mc.N_EW] == [f"EW{i}" for i in range(mc.N_EW)]
    n_nom, n_gib = s5n["grid"]["C3_nominal"], s5n["grid"]["C4_eavail_shape"]
    assert n_nom["n_experiments"] == 60 and n_gib["n_experiments"] == 60
    r = s5e["points"]
    assert r["nominal"]["n"] == 40 and all(r[w]["n"] == 20 for w in ("W1", "W2", "W3"))
    nn, nn_se = per(n_nom)
    ng, ng_se = per(n_gib)
    inj = 100 * (np.array(truth["departures"]["eavail_shape"]["M1_ratio"][: mc.N_EW]) - 1)
    rn, rn_se = per(r["nominal"])
    rw = {w: per(r[w]) for w in ("W1", "W2", "W3")}
    sig_adopt = np.array(s5e["A4"]["adopted_total_sigma_pct"])
    md = np.max(np.abs(np.array([rw[w][0] for w in rw])), axis=0)

    # Reproduce paper_body.tex :539-549 before drawing.
    amax = lambda v: (round(float(np.max(np.abs(v))), 2), f"EW{int(np.argmax(np.abs(v)))}")  # noqa: E731
    nums = [
        mc.check("family N, GiBUU/GENIE E_avail: max |residual| over 42 EW cells (paper 'up to 74% at high W'), %",
                 round(float(np.max(np.abs(ng))), 0) == 74 and amax(ng)[1] == "EW29", amax(ng)),
        mc.check("family N, GiBUU/GENIE E_avail: EW7 residual (record: 'largest cells several percent off'), %",
                 -10 < ng[7] < -2, round(float(ng[7]), 2)),
        mc.check("R, W2 (GENIE MEC): max |residual| over EW (paper lower end '16%'), %",
                 round(float(np.max(np.abs(rw["W2"][0]))), 0) == 16, amax(rw["W2"][0])),
        mc.check("R, W1 (NuWro E_avail): max |residual| over EW (paper upper end '31%'), %",
                 round(float(np.max(np.abs(rw["W1"][0]))), 0) == 31, amax(rw["W1"][0])),
        mc.check("R, W3 (NuWro 3D): max |residual| over EW inside 16-31%, %",
                 16 <= float(np.max(np.abs(rw["W3"][0]))) <= 31.5, amax(rw["W3"][0])),
        mc.check("R: cells with max_W |residual| <= adopted total sigma (paper 'about half'), of 42",
                 int(np.sum(md <= sig_adopt + 1e-9)) == len(s5e["A4"]["cells_model_dependence_within_adopted_sigma"]) == 20,
                 int(np.sum(md <= sig_adopt + 1e-9))),
    ]
    nums.append({"claim": "family N nominal (C3): max |residual| over EW, %", "value": amax(nn)})
    nums.append({"claim": "R nominal (A1): max |residual| over EW, %", "value": amax(rn)})
    nums.append({"claim": "family N GiBUU: median |residual| over EW, %", "value": round(float(np.median(np.abs(ng))), 2)})

    mc.style()
    # Layout (methods rewrite, fix round 1, REVIEW-1 P3): the nominal-truth row is not drawn; its maxima are in the
    # numbers file and the caption (the (d) nominal squares are Fig. 2(a)'s refinement arm).
    fig, (a_ng, a_rw) = plt.subplots(1, 2, figsize=(7.0, 3.3), sharex=True, gridspec_kw={"wspace": 0.16})
    fig.subplots_adjust(left=0.075, right=0.99, top=0.74, bottom=0.15)
    x = np.arange(mc.N_EW)
    for ax in (a_ng, a_rw):
        ax.axhline(0, color="k", lw=0.6)
        mc.ew_axis(ax, label_rows=True)
    a_ng.stairs(inj, np.arange(mc.N_EW + 1) - 0.5, color=mc.GREY, lw=0.9,
                label=r"injected truth change (deformed/nominal $-$ 1)")
    a_ng.errorbar(x, ng, ng_se, fmt="o", ms=3.0, color=mc.PURPLE, lw=0.7,
                  label=r"residual, GiBUU/GENIE $E_{\rm avail}$ (60 exp.)")
    edges = np.arange(mc.N_EW + 1) - 0.5
    a_rw.stairs(sig_adopt, edges, baseline=-sig_adopt, fill=True, color="0.88", lw=0,
                label=r"$\pm$ quoted total $\sigma$ of the $(E_{\rm avail},W)$ projection")
    for (w, lab, fmt, col), dx in zip((("W1", r"NuWro $E_{\rm avail}$", "o", mc.BLUE),
                                        ("W2", r"GENIE MEC $(E_{\rm avail},W)$", "^", mc.GREEN),
                                        ("W3", r"NuWro $(p_T,p_\parallel,E_{\rm avail})$", "D", mc.PURPLE)),
                                       (-0.22, 0.0, 0.22)):
        m, se = rw[w]
        a_rw.errorbar(x + dx, m, se, fmt=fmt, ms=2.6, color=col, lw=0.7, label=f"{lab} (20 exp.)")
    a_ng.set_ylim(-40, 100)
    a_rw.set_ylim(-40, 100)
    a_ng.legend(loc="upper left", frameon=False)
    a_rw.legend(loc="upper left", frameon=False)
    a_ng.set_ylabel("(unfolded $-$ truth)/truth (%)")
    a_rw.tick_params(labelleft=True)
    for ax in (a_ng, a_rw):
        ax.set_xlabel(r"$(E_{\rm avail},W)$ cell: $W$ bin 1–6 within each $E_{\rm avail}$ bin (GeV, top)", fontsize=7.2)
    a_ng.set_title("(a) with unbinned background refinement,\nrefinement classifier 100 trees, 8 leaves",
                   fontsize=7.2, loc="left", pad=11)
    a_rw.set_title("(b) joint-test estimator: as (a), with refinement\nclassifier 400 trees, 31 leaves",
                   fontsize=7.2, loc="left", pad=11)
    fig.text(0.075, 0.995, "\n".join([
        "Both panels: deterministic LightGBM OmniFold unfolding (5 iterations, 100 trees, 8 leaves);",
        "pseudo-experiments include backgrounds. (b): assessment seeds, since used in development.",
        r"$W$ bin 6 is $W\geq3$ GeV. Error bars: standard error of the mean over experiments."]),
        ha="left", va="top", fontsize=6.8, color="0.2")
    mc.save(fig, a.outdir, "m3_fig2_deformation")
    (a.outdir / "m3_fig2_deformation_numbers.json").write_text(json.dumps(nums, indent=1) + "\n")


if __name__ == "__main__":
    main()
