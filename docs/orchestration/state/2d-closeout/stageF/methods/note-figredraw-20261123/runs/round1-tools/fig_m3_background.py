#!/usr/bin/env python3
"""M3 figure 1: nominal-truth closure residual, purity subtraction vs the unbinned negative-weight refinement.

Both arms use the same estimator, s5c candidate F2 (deterministic LightGBM OmniFold, 5 iterations, 100 trees,
8 leaves), background-inclusive pseudo-experiments at nominal truth, development seeds:
  purity      s5c D1 split_F2 group, 9 experiments    (state/s5c/d1/d1_summary.json)
  refined     s5n family N C3_nominal, 60 experiments (state/s5n/stage1/dev_receipt.json): F2 with the
              driver's negweight-refined measured side, refinement classifier 100 trees / 8 leaves
Residual = mean over experiments of (unfolded - truth) / truth; error bar = its standard error.

  python3 fig_m3_background.py [--repo CHECKOUT] [--outdir DIR]

REDRAW COPY (note-figredraw-20261123, 2026-11-23): docs/analysis-note/figures/methods_m3/fig_m3_background.py with
the drawing changed and nothing upstream of it. The inputs, their sha256 pins, the arrays and every mc.check line are
the original's. Changes, presentation only:
  - panel (a) has a broken y axis: a main range of -1 to 2 % and a lower strip of -4.4 to -3.2 % that holds the six
    purity points of the highest-W column; each point (with its bar) is drawn once, in the range that contains it
    whole (asserted), and nothing is clipped;
  - the refinement squares are filled when |t| > t_crit = 3.6 and open otherwise, t = mean_rel / se_rel per functional
    of the receipt's grid.C3_nominal (nd-unfolding/s5n_analyze_dev.py:62-69); the plotted fail count plus the count
    in the one unplotted functional (EW_all_ones) must equal the receipt's n_abs_t_gt_crit;
  - panel (b)'s cells are grouped in blocks by their p_T and p_par coarse bins (tools/jgrid.py, asserted against
    nd-unfolding/s5c_coverage.py), alternate blocks shaded, p_T ranges above the axis, p_par ranges below it; the
    total is set apart on the right;
  - every text at least 7 pt at the printed width (6.5 in canvas, printed at \\linewidth = 6.5 in).
It writes m3_fig1_background_data.json: every plotted series, per functional name: axes, x, y, error, filled.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from matplotlib.lines import Line2D

import jgrid
import m3_common as mc
from m3_common import plt

T_CRIT_EXPECTED = 3.6
MAIN_YLIM, STRIP_YLIM = (-1.0, 2.0), (-4.4, -3.2)


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

    # The nominal closure criterion's per-functional statistic (s5n_analyze_dev.py:62-69, T_CRIT :35).
    t_crit = c3["criterion"]["t_crit"]
    assert t_crit == T_CRIT_EXPECTED, t_crit
    t = np.array(c3["per_functional"]["mean_rel"]) / np.array(c3["per_functional"]["se_rel"])
    assert float(np.max(np.abs(t))) == c3["max_abs_t"], "t does not reproduce the receipt's max_abs_t"
    fail = np.abs(t) > t_crit
    plotted = set(ew) | set(jj)
    unplotted = [i for i in range(len(names)) if i not in plotted]
    n_a, n_b, n_un = int(fail[ew].sum()), int(fail[jj].sum()), int(fail[unplotted].sum())
    nums.append(mc.check("refined: |t| > t_crit plotted (panel a + panel b) + unplotted equals the receipt's "
                         "grid.C3_nominal.n_abs_t_gt_crit",
                         n_a + n_b + n_un == c3["n_abs_t_gt_crit"],
                         {"panel_a_EW": [n_a, len(ew)], "panel_b_J_and_total": [n_b, len(jj)],
                          "unplotted": {names[i]: bool(fail[i]) for i in unplotted},
                          "receipt_n_abs_t_gt_crit": c3["n_abs_t_gt_crit"]}))

    dec = jgrid.verify(a.repo, names)
    E = jgrid.edges(a.repo)

    mc.style()
    W_IN, H_IN = 6.5, 5.75
    fig = plt.figure(figsize=(W_IN, H_IN))

    def box(x0, y0, w, h):
        return fig.add_axes([x0 / W_IN, y0 / H_IN, w / W_IN, h / H_IN])

    ax1 = box(0.62, 3.47, 5.78, 1.42)    # (a) main range
    ax1s = box(0.62, 3.0, 5.78, 0.4)     # (a) lower strip
    ax2 = box(0.62, 0.5, 5.78, 1.62)     # (b)
    lab_p = "purity-based subtraction (9 experiments)"
    lab_r = "unbinned negative-weight refinement (60 experiments)"
    dump = {"schema": "note-figredraw-bkg-data/1", "t_crit": t_crit, "series": []}

    def draw(ax, xs, idx, vals, errs, *, fmt, ms, col, lw, filled, series, axes_name):
        xs, idx = np.asarray(xs, float), list(idx)
        if not idx:
            return
        v, e = vals[idx], errs[idx]
        kw = dict(fmt=fmt, ms=ms, color=col, lw=lw)
        if not filled:
            kw.update(mfc="white", mec=col, mew=0.7)
        ax.errorbar(xs, v, e, **kw)
        lo, hi = ax.get_ylim()
        assert np.all(v - e >= lo) and np.all(v + e <= hi), f"{series} on {axes_name}: a point or bar is clipped"
        dump["series"].append({"series": series, "axes": axes_name, "filled": filled,
                               "points": [{"name": names[i], "x": float(x), "y": float(y), "err": float(s)}
                                          for i, x, y, s in zip(idx, xs, v, e)]})

    # ---- panel (a): the 42 (E_avail, W) cells, broken y axis
    x = np.arange(mc.N_EW)
    for ax, ylim in ((ax1, MAIN_YLIM), (ax1s, STRIP_YLIM)):
        ax.set_ylim(*ylim)
        ax.set_xlim(-0.5, mc.N_EW - 0.5)
        for k in range(1, len(mc.EAVAIL_EDGES) - 1):
            ax.axvline(k * mc.N_W - 0.5, color="0.8", lw=0.5, zorder=0)
    ax1.axhline(0, color="k", lw=0.6)
    in_main = [k for k in range(mc.N_EW) if MAIN_YLIM[0] <= pur[ew[k]] - pur_se[ew[k]]
               and pur[ew[k]] + pur_se[ew[k]] <= MAIN_YLIM[1]]
    in_strip = [k for k in range(mc.N_EW) if k not in in_main]
    assert len(in_main) + len(in_strip) == mc.N_EW
    draw(ax1, x[in_main] - 0.17, [ew[k] for k in in_main], pur, pur_se, fmt="o", ms=3.0, col=mc.BLUE, lw=0.8,
         filled=True, series="purity", axes_name="a_main")
    draw(ax1s, x[in_strip] - 0.17, [ew[k] for k in in_strip], pur, pur_se, fmt="o", ms=3.0, col=mc.BLUE, lw=0.8,
         filled=True, series="purity", axes_name="a_strip")
    for filled in (True, False):
        ks = [k for k in range(mc.N_EW) if bool(fail[ew[k]]) == filled]
        draw(ax1, x[ks] + 0.17, [ew[k] for k in ks], ref, ref_se, fmt="s", ms=2.8, col=mc.RED, lw=0.8,
             filled=filled, series="refined", axes_name="a_main")
    ax1.spines["bottom"].set_visible(False)
    ax1.tick_params(axis="x", bottom=False, labelbottom=False)
    ax1s.spines["top"].set_visible(False)
    ax1.set_yticks([-1, 0, 1, 2])
    ax1s.set_yticks([-4])
    for ax, yy in ((ax1, 0.0), (ax1s, 1.0)):   # the break marks, at both ends of the gap (axes coordinates)
        ax.plot([0.0, 1.0], [yy, yy], transform=ax.transAxes, ls="none", marker=[(-1, -0.5), (1, 0.5)], ms=6,
                color="k", mec="k", mew=0.6, clip_on=False, label="_break")
    ax1s.set_xticks(range(mc.N_EW))
    ax1s.set_xticklabels([str(i % mc.N_W + 1) for i in range(mc.N_EW)], fontsize=7.0)
    ax1s.tick_params(axis="x", length=2, pad=1.5)
    for k in range(len(mc.EAVAIL_EDGES) - 1):
        lo, hi = mc.EAVAIL_EDGES[k], mc.EAVAIL_EDGES[k + 1]
        txt = f"{lo:g}–{hi:g}" if hi < 100 else rf"$\geq${lo:g}"
        ax1.text(k * mc.N_W + (mc.N_W - 1) / 2, 1.0, txt, transform=ax1.get_xaxis_transform(), ha="center",
                 va="bottom", fontsize=7.0, color="0.3")
    ax1s.set_xlabel(r"$(E_{\rm avail},W)$ cell: $W$ bin 1–6 within each $E_{\rm avail}$ bin (GeV, top); "
                    r"$W$ edges 0, 1.1, 1.4, 1.8, 2.2, 3, 100 GeV", fontsize=7.5, labelpad=2)
    fig.text(0.13 / W_IN, (3.0 + 4.89) / 2 / H_IN, r"(unfolded $-$ truth)/truth (%)", rotation=90, ha="center",
             va="center", fontsize=8.5)
    ax1.text(0.0, 1.13, r"(a) $(E_{\rm avail},W)$ projection, 42 cells", transform=ax1.transAxes, fontsize=8)

    # ---- panel (b): the 109 joint cells by (p_T, p_par) block, then the total
    jn = [names[i] for i in jj[:-1]]
    blk = jgrid.blocks(jn)
    xj = np.array([float(k) for k in range(len(jn))] + [len(jn) + 1.0])   # total set apart by one slot
    ax2.set_ylim(-2.5, 3.2)
    ax2.set_xlim(-0.8, xj[-1] + 0.8)
    for b, (ipt, ipz, k0, k1) in enumerate(blk):
        if b % 2 == 0:
            ax2.axvspan(k0 - 0.5, k1 + 0.5, color="0.92", lw=0, zorder=0)
    pt_groups = {}
    for ipt, ipz, k0, k1 in blk:
        g0, g1 = pt_groups.get(ipt, (k0, k1))
        pt_groups[ipt] = (min(g0, k0), max(g1, k1))
    for ipt, (k0, k1) in pt_groups.items():
        if k0 > 0:
            ax2.axvline(k0 - 0.5, color="0.45", lw=0.7, zorder=0.5)
        ax2.text((k0 + k1) / 2, 1.0, rf"$p_T$ {jgrid.rng(E['pt'], ipt)} GeV/$c$", transform=ax2.get_xaxis_transform(),
                 ha="center", va="bottom", fontsize=7.0, color="0.3")
    ax2.axvline(len(jn) + 0.0, color="0.45", lw=0.7, zorder=0.5)
    ax2.axhline(0, color="k", lw=0.6)
    draw(ax2, xj - 0.17, jj, pur, pur_se, fmt="o", ms=2.4, col=mc.BLUE, lw=0.7, filled=True, series="purity",
         axes_name="b")
    for filled in (True, False):
        ks = [k for k in range(len(jj)) if bool(fail[jj[k]]) == filled]
        draw(ax2, xj[ks] + 0.17, [jj[k] for k in ks], ref, ref_se, fmt="s", ms=2.2, col=mc.RED, lw=0.7,
             filled=filled, series="refined", axes_name="b")
    ax2.set_xticks([(k0 + k1) / 2 for _, _, k0, k1 in blk] + [xj[-1]])
    ax2.set_xticklabels([jgrid.rng(E["pz"], ipz) for _, ipz, _, _ in blk] + ["total"], fontsize=7.0)
    ax2.tick_params(axis="x", length=0, pad=2.5)
    ax2.set_xlabel(r"coarse joint cell, in blocks of one $p_T$ bin (top) and one $p_\parallel$ bin (GeV/$c$, below); "
                   r"within a block by $E_{\rm avail}$, $q_3$, $W$ bin", fontsize=7.5, labelpad=2)
    ax2.set_ylabel(r"(unfolded $-$ truth)/truth (%)")
    ax2.text(0.0, 1.10, f"(b) {len(jn)} joint-cell integrals and the total", transform=ax2.transAxes, fontsize=8)

    # ---- legend (figure level, above panel a)
    hs = [Line2D([], [], ls="none", marker="o", ms=3.0, color=mc.BLUE),
          Line2D([], [], ls="none", marker="s", ms=2.8, color=mc.RED),
          Line2D([], [], ls="none", marker="s", ms=2.8, color=mc.RED, mfc="white", mew=0.7)]
    ls = [lab_p, lab_r + rf": $|t|>{t_crit:g}$ (filled)", lab_r + rf": $|t|\leq{t_crit:g}$ (open)"]
    fig.legend(hs, ls, loc="upper left", bbox_to_anchor=(0.55 / W_IN, 1.0 - 0.02 / H_IN), ncol=1, frameon=False,
               fontsize=7.0, handletextpad=0.4, borderaxespad=0.0, labelspacing=0.25)
    fig.text(6.42 / W_IN, 1.0 - 0.08 / H_IN, r"$t$ = mean residual / its standard error;" "\n"
             rf"$t_{{\rm crit}}={t_crit:g}$ of the nominal closure criterion", ha="right", va="top", fontsize=7.0, color="0.25")

    dump["fail_counts"] = {"panel_a": n_a, "panel_b": n_b, "unplotted": n_un,
                           "receipt_n_abs_t_gt_crit": c3["n_abs_t_gt_crit"]}
    dump["j_decoding"] = dec
    mc.save(fig, a.outdir, "m3_fig1_background")
    (a.outdir / "m3_fig1_background_numbers.json").write_text(json.dumps(nums, indent=1) + "\n")
    (a.outdir / "m3_fig1_background_data.json").write_text(json.dumps(dump, indent=1) + "\n")


if __name__ == "__main__":
    main()
