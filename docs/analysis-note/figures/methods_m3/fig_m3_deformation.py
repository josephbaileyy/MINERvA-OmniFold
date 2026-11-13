#!/usr/bin/env python3
"""Fractional recovery residuals for reported and lower-capacity estimators.

Supplement figure, s5n family N (state/s5n/stage1/dev_receipt.json): s5c F2 deterministic LightGBM (5 iterations,
100 trees, 8 leaves) with the negweight-refined measured side, refinement classifier 100 trees / 8 leaves;
60 background-inclusive development experiments per truth (C3 nominal, C4 GiBUU/GENIE E_avail shape).
The injected per-cell truth change of C4 is from state/s5n/stage1/truth_check.json (M1_ratio - 1).
Paper figure, s5e candidate R = the joint-test estimator (state/s5e/cand/assess_receipt.json): family N with the
refinement classifier at 400 trees / 31 leaves; fresh assessment seeds, 40 nominal experiments (A1) and 20 per
withheld truth W1 (NuWro E_avail), W2 (GENIE MEC, (E_avail,W)), W3 (NuWro (pT,p||,E_avail)). The adopted C_EW total
sigma per cell (assess_receipt A4.adopted_total_sigma_pct) is no longer drawn: that covariance fails its acceptance
criteria, so a comparison with it says nothing about the reported uncertainty (the short methods paper's W-15, the
director's decision of 2026-11-09 on IR-sol, #988). It stays in the numbers file as a record.
Residual = mean over experiments of (unfolded - truth) / truth, truth = the deformed truth of each experiment.

  python3 fig_m3_deformation.py [--repo CHECKOUT] [--outdir DIR]
"""
from __future__ import annotations

import hashlib
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
    assert s5e["candidate"] == "R", "paper figure requires the reported estimator"
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
    # m5/Fm7 and s11c (#977): the withheld truths' injected changes (full-sample, M1 @ x(W) / M1 @ x(nominal) - 1) and the
    # reported estimator at the GiBUU-to-GENIE E_avail change (assess_receipt points.eavail_gibuu, 20 experiments)
    m5 = mc.load(a.repo, "m5_injected")
    assert m5["control_W1"]["pass"] and m5["control_W2"]["pass"]
    assert all(s["support_cells_empty_in_every_seed"] == 0 for s in m5["sets"].values())
    inj_w = {w: np.array(m5["injected_change_pct"][w]) for w in ("W1", "W2", "W3")}
    assert r["eavail_gibuu"]["n"] == 20
    rg, rg_se = per(r["eavail_gibuu"])
    UNSUPPORTED = (11, 36, 37)   # EW cells failing the support rule (stage1_inspect.json mc.EW reported, #977 Fm7)
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
        mc.check("R: cells with max_W |residual| <= adopted total sigma (a record only: no longer printed, W-15), of 42",
                 int(np.sum(md <= sig_adopt + 1e-9)) == len(s5e["A4"]["cells_model_dependence_within_adopted_sigma"]) == 20,
                 int(np.sum(md <= sig_adopt + 1e-9))),
    ]
    nums += [
        mc.check("R, GiBUU/GENIE E_avail (s11c): max |residual| over EW (paper s5e-gibuu-ewmax '73.86' at high W), %",
                 round(float(np.max(np.abs(rg))), 2) == 73.86 and amax(rg)[1] == "EW29", amax(rg)),
        mc.check("m5: max |injected change| W1, W2, W3 (m5_injected.json max_abs_injected_pct), %",
                 [amax(inj_w[w]) for w in ("W1", "W2", "W3")] == [(21.39, "EW6"), (14.84, "EW37"), (27.51, "EW7")],
                 [amax(inj_w[w]) for w in ("W1", "W2", "W3")]),
    ]
    nums.append({"claim": "family N nominal (C3): max |residual| over EW, %", "value": amax(nn)})
    nums.append({"claim": "R nominal (A1): max |residual| over EW, %", "value": amax(rn)})
    nums.append({"claim": "family N GiBUU: median |residual| over EW, %", "value": round(float(np.median(np.abs(ng))), 2)})

    reference_path = Path(__file__).parents[1] / "methods_short/presentation_original_arrays.json"
    reference_pins = json.loads(reference_path.with_name("inputs.json").read_text())
    reference_key = "docs/analysis-note/figures/methods_short/presentation_original_arrays.json"
    assert hashlib.sha256(reference_path.read_bytes()).hexdigest() == reference_pins[reference_key]
    original = json.loads(reference_path.read_text())["deformation"]
    current = {"left_residual_se_pct": [ng.tolist(), ng_se.tolist()],
               "injected_change_pct": inj.tolist(),
               "right_residual_se_pct": {w: [m.tolist(), se.tolist()] for w, (m, se) in rw.items()},
               "injected_change_pct_reported": {w: v.tolist() for w, v in inj_w.items()},
               "right_gibuu_residual_se_pct": [rg.tolist(), rg_se.tolist()]}
    assert current == original, "deformation numerical arrays changed from presentation baseline"
    a.outdir.mkdir(parents=True, exist_ok=True)
    (a.outdir / "m3_fig2_deformation_arrays.json").write_text(json.dumps(current, indent=2) + "\n")
    mc.style()
    plt.rcParams.update({"font.size": 8.5, "axes.labelsize": 9.3,
                         "xtick.labelsize": 8.3, "ytick.labelsize": 8.3,
                         "legend.fontsize": 8.3})
    # small multiples (the director's Gm10 ruling, 2026-11-12, on the fresh referee's minor 10 and Joseph's overlap
    # remark): one panel per truth, each with its own injected-change step, on one shared y scale; the plotted arrays
    # are unchanged (asserted above against presentation_original_arrays.json)
    fig_paper, a_rws = plt.subplots(4, 1, sharex=True, sharey=True, figsize=(508 / 72, 5.8))
    fig_paper.subplots_adjust(left=43.18 / 508, right=0.99, top=0.915, bottom=0.075, hspace=0.12)
    fig_lowcap, a_ng = plt.subplots(figsize=(468 / 72, 2.8))
    fig_lowcap.subplots_adjust(left=43.18 / 468, right=0.99, top=0.77, bottom=0.20)
    x = np.arange(mc.N_EW)
    for ax in (a_ng, *a_rws):
        ax.axhline(0, color="k", lw=0.6)
        mc.ew_axis(ax, label_rows=ax is a_ng or ax is a_rws[0])
        ax.tick_params(axis="x", labelsize=8.3, labelbottom=ax is a_ng or ax is a_rws[-1])
        for label in ax.texts:
            label.set_fontsize(8.3)
    a_ng.stairs(inj, np.arange(mc.N_EW + 1) - 0.5, color=mc.GREY, lw=0.9,
                label=r"injected truth change (deformed/nominal $-$ 1)")
    a_ng.errorbar(x, ng, ng_se, fmt="o", ms=3.0, color=mc.PURPLE, lw=0.7,
                  label=r"residual, GiBUU/GENIE $E_{\rm avail}$ (60 exp.)")
    # the figure referee read (secondary-results/referee-figure-deformation-20261112, the director's B1-B3, B6): each
    # injected-change curve has its own dash pattern and legend sample, markers carry dark outlines, the shading is
    # stronger and hatched, and the legend sits above the axes; the green is darkened here only (m3_common keeps its own)
    GREEN_DK = "#0d7a52"
    for ax in a_rws:
        for c in UNSUPPORTED:
            ax.axvspan(c - 0.5, c + 0.5, facecolor="0.86", edgecolor="0.6", hatch="////", lw=0, zorder=0)
    # the GiBUU case's injected change is the left panel's inj: the same truth (eavail_shape), ratio file
    # (s5n/eavail-ratio-gibuu-over-genie.json, sha 45cc3e0a = truth_check.json eavail_ratio_sha256) and amplitude 1.0
    # (s5e/cand-assess-tasks.tsv aeavail_gibuu_*)
    assert truth["eavail_ratio_sha256"].startswith("45cc3e0a") and truth["departures"]["eavail_shape"]["amplitude"] == 1.0
    series = (("W1", r"NuWro $E_{\rm avail}$ shape", "o", mc.BLUE, rw["W1"], inj_w["W1"]),
              ("W2", r"GENIE + MEC $(E_{\rm avail},W)$ shape", "^", GREEN_DK, rw["W2"], inj_w["W2"]),
              ("W3", r"NuWro $(p_T,p_\parallel,E_{\rm avail})$ shape", "D", mc.PURPLE, rw["W3"], inj_w["W3"]),
              ("GiBUU", r"GiBUU-to-GENIE $E_{\rm avail}$ shape", "s", mc.RED, (rg, rg_se), inj))
    for ax, (w, lab, fmt, col, (m, se), injc) in zip(a_rws, series):
        step = ax.stairs(injc, np.arange(mc.N_EW + 1) - 0.5, color="0.25", lw=0.9, ls=(0, (4, 1.5)),
                         label="injected truth change")
        mark = ax.errorbar(x, m, se, fmt=fmt, ms=3.1, mec="0.15", mew=0.35, color=col, lw=0.7,
                           label="residual (mean, s.e.)")
        ax.text(0.006, 0.93, lab, transform=ax.transAxes, ha="left", va="top", fontsize=8.6, color=col, zorder=5,
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.9, pad=1.0))
        if ax is a_rws[0]:
            fig_paper.legend(handles=[mark, step], loc="upper right", bbox_to_anchor=(0.99, 1.0), ncol=2,
                             frameon=False, fontsize=8.0, handlelength=2.6, columnspacing=1.6)
    a_ng.set_ylim(-40, 100)
    a_ng.set_yticks(np.arange(-40, 101, 20))
    a_rws[0].set_ylim(-40, 80)
    a_rws[0].set_yticks(np.arange(-40, 81, 40))
    a_ng.legend(loc="upper left", frameon=False)
    a_ng.set_ylabel("(unfolded $-$ truth)/truth (%)")
    fig_paper.supylabel("(unfolded $-$ truth)/truth and injected change (%)", fontsize=9.3, x=0.005)
    xlabel = r"$(E_{\rm avail},W)$ cell: $W$ bin 1–6 within each $E_{\rm avail}$ bin (GeV, top)"
    for ax in (a_ng, a_rws[-1]):
        ax.set_xlabel(xlabel, fontsize=9.3)
    a_ng.set_title(
        "Lower-capacity variant with background refinement,\n"
        "refinement classifier 100 trees, 8 leaves",
        fontsize=8.3,
        loc="left",
        y=1.16,
        pad=0,
    )
    mc.save(fig_paper, a.outdir, "m3_fig2_deformation")
    mc.save(fig_lowcap, a.outdir, "m3_fig2_deformation_lowcap")
    (a.outdir / "m3_fig2_deformation_numbers.json").write_text(json.dumps(nums, indent=1) + "\n")


if __name__ == "__main__":
    main()
