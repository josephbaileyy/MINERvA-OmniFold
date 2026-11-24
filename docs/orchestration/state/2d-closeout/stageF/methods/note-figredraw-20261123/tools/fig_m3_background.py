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
ROUND 2 (2026-11-23, the outside reviewer's suggestions as Joseph approved them): the legend has one entry per method
(deterministic purity control, 9 pseudo-experiments; low-capacity negative-weight refinement, 60 pseudo-experiments) and a separate short key for
the filled / open refinement squares (|t| > 3.6 / |t| <= 3.6); the in-figure text block defining t and t_crit is
removed (the caption defines them); the canvas is 0.2 in shorter. Ranges, points and markers are round 1's.
ROUND 3 (2026-11-23, two variants for the reviewer to choose from; round 2's copy is in runs/round2-tools/):
  --variant R  round 2 plus the reviewer's second-turn suggestions (ask-codex2/REPLY2.md): the last W bin of each
               E_avail block is labelled ">=3" (W >= 3 GeV) and lightly shaded through both ranges of panel (a); panel
               (b) carries "up to 14 standard errors" at the largest-|t| cell (asserted: J88, |t| = receipt max_abs_t
               = 14.42; "14" is floor(max_abs_t)).
  --variant D  the reviewer's first-turn redesign (ask-codex2/REPLY1.md): panel (a) is two E_avail-W heatmaps (purity
               control | refinement) with the bin edges of nd-unfolding/project_cov_nd.py AXIS_EDGES (asserted, and
               EW<k> = (E_avail bin k // 6, W bin k % 6) asserted by tools/jgrid.py verify_ew), one shared zero-centred
               diverging scale, the signed residual printed in every cell (2 decimals; the refinement's value in bold
               when |t| > 3.6); the colour array is the residual array (asserted after drawing, as is every printed
               string). The heatmaps draw no error; the dump keeps it. Panel (b) is round 2's.
ROUND 4 (2026-11-23, polish of the reviewer's choice 7 D, ask-codex2/REPLY3.md; round 3's copy is in runs/round3-tools/):
  --variant P  variant D with (1) the method legend (purity circles, refinement squares) and the filled/open key for
               the refinement squares moved from the top of the figure into panel (b), where those markers are drawn,
               as one boxed legend at its upper right (asserted clear of every panel-(b) point and bar after drawing); panel
               (a)'s heatmaps keep their titles and colour bar; (2) variant R's "up to 14 standard errors" callout at
               the largest-|t| joint cell (asserted: J88, |t| = receipt max_abs_t = 14.42; "14" = floor(max_abs_t)).
               The canvas is shorter (no legend band on top) and panel (b) 0.23 in taller; its y range is unchanged.
It writes m3_fig1_background_data.json: every plotted series, per functional name: axes, x, y, error, filled; for
variant D also the heatmaps: per functional name, the cell, value, error, printed text and bold state.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from matplotlib.colors import Normalize
from matplotlib.legend_handler import HandlerTuple
from matplotlib.lines import Line2D

import jgrid
import m3_common as mc
from m3_common import plt

T_CRIT_EXPECTED = 3.6
MAIN_YLIM, STRIP_YLIM = (-1.0, 2.0), (-4.4, -3.2)


def pop_variant() -> str:
    """ROUND 3: take --variant R|D (ROUND 4: or P) off the command line (m3_common.parse_args is unchanged)."""
    if "--variant" not in sys.argv:
        raise SystemExit("--variant R|D|P is required (round 3)")
    k = sys.argv.index("--variant")
    v = sys.argv[k + 1]
    del sys.argv[k:k + 2]
    if v not in ("R", "D", "P"):
        raise SystemExit(f"--variant must be R, D or P, not {v}")
    return v


def fmt_res(v: float) -> str:
    """A heatmap cell's printed residual (%): two decimals, a true minus sign."""
    return f"{v:.2f}".replace("-", "\u2212")


def main() -> None:
    variant = pop_variant()
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

    # ROUND 3: the largest |t| (the annotation of variant R) is a joint cell of panel (b): J88, |t| = 14.42.
    i_tmax = int(np.argmax(np.abs(t)))
    assert names[i_tmax] == "J88" and i_tmax in jj, names[i_tmax]
    assert round(c3["max_abs_t"], 2) == 14.42 and abs(t[i_tmax]) == c3["max_abs_t"], c3["max_abs_t"]
    n_se = math.floor(c3["max_abs_t"])
    assert n_se == 14
    nums.append({"claim": "round 3: largest |t| (receipt max_abs_t) and its functional",
                 "value": [c3["max_abs_t"], names[i_tmax]]})

    mc.style()
    lab_p = "deterministic purity control (9 pseudo-experiments)"
    lab_r = "low-capacity negative-weight refinement (60 pseudo-experiments)"
    dump = {"schema": "note-figredraw-bkg-data/2", "variant": variant, "t_crit": t_crit, "series": []}
    W_IN, H_IN = {"R": (6.5, 5.55), "D": (6.5, 5.65), "P": (6.5, 5.42)}[variant]
    fig = plt.figure(figsize=(W_IN, H_IN))

    def box(x0, y0, w, h):
        return fig.add_axes([x0 / W_IN, y0 / H_IN, w / W_IN, h / H_IN])

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

    def panel_b(ax2):
        """Round 2's panel (b): the 109 joint cells by (p_T, p_par) block, then the total. Returns the x positions."""
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
            ax2.text((k0 + k1) / 2, 1.0, rf"$p_T$ {jgrid.rng(E['pt'], ipt)} GeV/$c$",
                     transform=ax2.get_xaxis_transform(), ha="center", va="bottom", fontsize=7.0, color="0.3")
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
        ax2.set_xlabel(r"coarse joint cell, in blocks of one $p_T$ bin (top) and one $p_\parallel$ bin (GeV/$c$, "
                       r"below); within a block by $E_{\rm avail}$, $q_3$, $W$ bin", fontsize=7.5, labelpad=2)
        ax2.set_ylabel(r"(unfolded $-$ truth)/truth (%)")
        ax2.text(0.0, 1.10, f"(b) {len(jn)} joint-cell integrals and the total", transform=ax2.transAxes, fontsize=8)
        return xj

    def callout(ax2, xj):
        """ROUND 3 (R; ROUND 4 also P): "up to 14 standard errors" at the largest-|t| cell (a refinement square of b)."""
        kx = jj.index(i_tmax)
        ann = ax2.annotate(f"up to {n_se} standard errors", xy=(xj[kx] + 0.17, ref[i_tmax]), xytext=(-4, 30),
                           textcoords="offset points", ha="right", va="bottom", fontsize=7.0, color="0.15",
                           arrowprops=dict(arrowstyle="-", color="0.3", lw=0.6, shrinkA=1, shrinkB=3))
        dump["annotation"] = {"text": ann.get_text(), "at": names[i_tmax], "abs_t": float(abs(t[i_tmax])),
                              "receipt_max_abs_t": c3["max_abs_t"], "xy": [float(v) for v in ann.xy]}

    def legend_in_b(ax2):
        """ROUND 4 (P): the method legend and the refinement-square key, as one legend inside panel (b) at its upper
        right, where the circles and squares are drawn. Asserted after drawing: no panel-(b) point or bar end lies
        inside the legend's box."""
        hs = [Line2D([], [], ls="none", marker="o", ms=3.0, color=mc.BLUE),
              Line2D([], [], ls="none", marker="s", ms=2.8, color=mc.RED),
              (Line2D([], [], ls="none", marker="s", ms=2.8, color=mc.RED),
               Line2D([], [], ls="none", marker="s", ms=2.8, color=mc.RED, mfc="white", mew=0.7))]
        labs = [lab_p, lab_r, rf"refinement squares: filled $|t|>{t_crit:g}$, open $|t|\leq{t_crit:g}$"]
        leg = ax2.legend(hs, labs, loc="upper right", bbox_to_anchor=(1.0, 1.0), ncol=1, frameon=True,
                         fancybox=False, framealpha=1.0, edgecolor="0.6", fontsize=7.0, handletextpad=0.4,
                         borderaxespad=0.45, borderpad=0.35, labelspacing=0.25, handlelength=2.0,
                         handler_map={tuple: HandlerTuple(ndivide=None, pad=0.6)})
        leg.get_frame().set_linewidth(0.5)
        leg.set_zorder(5)   # above the block shading and the p_T divider (a white box with a thin edge)
        fig.canvas.draw()
        bb = leg.get_window_extent()
        inside = []
        for s in dump["series"]:
            if s["axes"] != "b":
                continue
            for p in s["points"]:
                for yy in (p["y"] - p["err"], p["y"], p["y"] + p["err"]):
                    X, Y = ax2.transData.transform((p["x"], yy))
                    if bb.x0 - 2 <= X <= bb.x1 + 2 and bb.y0 - 2 <= Y <= bb.y1 + 2:
                        inside.append(p["name"])
        assert not inside, f"panel (b) points or bars under the legend: {sorted(set(inside))}"
        dump["legend_b"] = {"entries": [t.get_text() for t in leg.get_texts()], "clear_of_points": True}

    def legends():
        """Round 2's legend: one entry per method, then the short key for the refinement squares."""
        hs = [Line2D([], [], ls="none", marker="o", ms=3.0, color=mc.BLUE),
              Line2D([], [], ls="none", marker="s", ms=2.8, color=mc.RED)]
        fig.legend(hs, [lab_p, lab_r], loc="upper left", bbox_to_anchor=(0.55 / W_IN, 1.0 - 0.02 / H_IN), ncol=1,
                   frameon=False, fontsize=7.0, handletextpad=0.4, borderaxespad=0.0, labelspacing=0.25)
        hk = [Line2D([], [], ls="none", marker="s", ms=2.8, color=mc.RED),
              Line2D([], [], ls="none", marker="s", ms=2.8, color=mc.RED, mfc="white", mew=0.7)]
        fig.legend(hk, [rf"$|t|>{t_crit:g}$", rf"$|t|\leq{t_crit:g}$"], loc="upper right",
                   bbox_to_anchor=(6.42 / W_IN, 1.0 - 0.02 / H_IN), ncol=2, frameon=False, fontsize=7.0,
                   handletextpad=0.4, borderaxespad=0.0, columnspacing=1.2, title="refinement squares:",
                   title_fontsize=7.0, alignment="left")

    if variant == "R":   # variants D and P (ROUND 4: P = D polished) take the else branch
        ax1 = box(0.62, 3.47, 5.78, 1.42)    # (a) main range
        ax1s = box(0.62, 3.0, 5.78, 0.4)     # (a) lower strip
        ax2 = box(0.62, 0.5, 5.78, 1.62)     # (b)
        # ---- panel (a): the 42 (E_avail, W) cells, broken y axis
        x = np.arange(mc.N_EW)
        for ax, ylim in ((ax1, MAIN_YLIM), (ax1s, STRIP_YLIM)):
            ax.set_ylim(*ylim)
            ax.set_xlim(-0.5, mc.N_EW - 0.5)
            for k in range(1, len(mc.EAVAIL_EDGES) - 1):
                ax.axvline(k * mc.N_W - 0.5, color="0.8", lw=0.5, zorder=0)
            for k in range(len(mc.EAVAIL_EDGES) - 1):   # ROUND 3: the W >= 3 GeV column, lightly shaded
                ax.axvspan(k * mc.N_W + mc.N_W - 1.5, k * mc.N_W + mc.N_W - 0.5, color="0.93", lw=0, zorder=0)
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
        assert mc.W_EDGES[-2] == 3.0 and mc.W_EDGES[-1] == 100.0
        wlab = [str(i + 1) for i in range(mc.N_W - 1)] + [rf"$\geq${mc.W_EDGES[-2]:g}"]
        ax1s.set_xticklabels([wlab[i % mc.N_W] for i in range(mc.N_EW)], fontsize=7.0)
        ax1s.tick_params(axis="x", length=2, pad=1.5)
        for k in range(len(mc.EAVAIL_EDGES) - 1):
            lo, hi = mc.EAVAIL_EDGES[k], mc.EAVAIL_EDGES[k + 1]
            txt = f"{lo:g}–{hi:g}" if hi < 100 else rf"$\geq${lo:g}"
            ax1.text(k * mc.N_W + (mc.N_W - 1) / 2, 1.0, txt, transform=ax1.get_xaxis_transform(), ha="center",
                     va="bottom", fontsize=7.0, color="0.3")
        ax1s.set_xlabel(r"$(E_{\rm avail},W)$ cell: $W$ bin within each $E_{\rm avail}$ bin (GeV, top); "
                        r"$W$ edges 0, 1.1, 1.4, 1.8, 2.2, 3 GeV; shaded: $W\geq3$ GeV", fontsize=7.5, labelpad=2)
        fig.text(0.13 / W_IN, (3.0 + 4.89) / 2 / H_IN, r"(unfolded $-$ truth)/truth (%)", rotation=90, ha="center",
                 va="center", fontsize=8.5)
        ax1.text(0.0, 1.13, r"(a) $(E_{\rm avail},W)$ projection, 42 cells", transform=ax1.transAxes, fontsize=8)
        xj = panel_b(ax2)
        callout(ax2, xj)
        legends()
        axes_named = (("a_main", ax1), ("a_strip", ax1s), ("b", ax2))
    else:
        # ---- panel (a), variant D: two E_avail-W heatmaps, one shared zero-centred diverging scale
        dump["ew_decoding"] = jgrid.verify_ew(a.repo, names, mc.EAVAIL_EDGES, mc.W_EDGES)
        nE, nW = len(mc.EAVAIL_EDGES) - 1, mc.N_W
        vmax = math.ceil(2 * float(max(np.max(np.abs(pur[ew])), np.max(np.abs(ref[ew]))))) / 2
        norm = Normalize(-vmax, vmax)
        cmap = plt.get_cmap("PuOr_r")
        hy0, hh, hw = (2.97, 1.72, 2.42) if variant == "D" else (3.1, 1.72, 2.42)
        hp = box(0.72, hy0, hw, hh)
        hr = box(0.72 + hw + 0.2, hy0, hw, hh)
        cb = box(0.72 + 2 * hw + 0.32, hy0, 0.1, hh)
        ax2 = box(0.62, 0.5, 5.78, 1.62) if variant == "D" else box(0.62, 0.5, 5.78, 1.85)
        dump["heatmaps"] = {}
        meshes = {}
        for ax, ser, vals, errs, title in ((hp, "purity", pur, pur_se, lab_p), (hr, "refined", ref, ref_se, lab_r)):
            arr = np.empty((nE, nW))
            for k in range(mc.N_EW):
                arr[k // nW, k % nW] = vals[ew[k]]
            m = ax.pcolormesh(np.arange(nW + 1), np.arange(nE + 1), arr, cmap=cmap, norm=norm, edgecolors="white",
                              linewidth=0.4)
            m.set_gid(f"heat:{ser}")
            meshes[ser] = m
            cells = []
            for k in range(mc.N_EW):
                iE, iW = divmod(k, nW)
                v = float(vals[ew[k]])
                bold = ser == "refined" and bool(fail[ew[k]])
                txt = ax.text(iW + 0.5, iE + 0.5, fmt_res(v), ha="center", va="center", fontsize=7.0,
                              fontweight="bold" if bold else "normal",
                              color="white" if abs(v) > 0.55 * vmax else "black")
                assert txt.get_text() == fmt_res(vals[ew[k]]) and (txt.get_fontweight() == "bold") == bold
                cells.append({"name": names[ew[k]], "iE": iE, "iW": iW, "value": v, "err": float(errs[ew[k]]),
                              "text": txt.get_text(), "bold": bold})
            dump["heatmaps"][ser] = cells
            ax.set_xlim(0, nW)
            ax.set_ylim(0, nE)
            ax.set_xticks(range(nW + 1))
            ax.set_xticklabels([f"{e:g}" for e in mc.W_EDGES], fontsize=7.0)
            ax.set_yticks(range(nE + 1))
            ax.set_yticklabels([f"{e:g}" for e in mc.EAVAIL_EDGES] if ser == "purity" else [], fontsize=7.0)
            ax.tick_params(length=2, pad=1.5)
            ax.set_xlabel(r"$W$ (GeV), bin edges", fontsize=7.5, labelpad=1.5)
            ax.set_title(title.replace(" (", "\n("), fontsize=7.5, pad=3, linespacing=1.0)
            for sp in ax.spines.values():
                sp.set_linewidth(0.5)
        hp.set_ylabel(r"$E_{\rm avail}$ (GeV), bin edges", fontsize=7.5, labelpad=2)
        # the colour arrays are the residual arrays, bit for bit (read back from the drawn meshes)
        for ser, vals in (("purity", pur), ("refined", ref)):
            got = np.asarray(meshes[ser].get_array(), np.float64).reshape(-1)
            assert got.tobytes() == np.asarray(vals[ew], np.float64).tobytes(), f"{ser}: colour array is not the residual"
            assert meshes[ser].norm is norm
        assert norm.vmin == -norm.vmax == -vmax
        dump["heatmap_scale"] = {"cmap": cmap.name, "vmin": -vmax, "vmax": vmax}
        cbar = fig.colorbar(meshes["purity"], cax=cb)
        cbar.set_ticks([-4, -2, 0, 2, 4])
        cbar.ax.tick_params(labelsize=7.0, length=2, pad=1.5)
        cbar.outline.set_linewidth(0.5)
        cbar.set_label(r"(unfolded $-$ truth)/truth (%)", fontsize=7.5, labelpad=2)
        assert t_crit == 3.6
        hp.text(0.0, 1.0 + 0.42 / hh, r"(a) $(E_{\rm avail},W)$ projection, 42 cells: mean residual (%) per cell; "
                r"refinement value in bold where $|t|>3.6$", transform=hp.transAxes, fontsize=8, va="bottom")
        xj = panel_b(ax2)
        if variant == "D":
            legends()
        else:                 # ROUND 4 (P): the legend inside panel (b), and the callout of variant R
            callout(ax2, xj)
            legend_in_b(ax2)
        axes_named = (("heat_purity", hp), ("heat_refined", hr), ("colorbar", cb), ("b", ax2))
        assert sum(c["bold"] for c in dump["heatmaps"]["refined"]) == n_a

    dump["axes_index"] = {k: fig.axes.index(v) for k, v in axes_named}
    dump["fail_counts"] = {"panel_a": n_a, "panel_b": n_b, "unplotted": n_un,
                           "receipt_n_abs_t_gt_crit": c3["n_abs_t_gt_crit"]}
    dump["j_decoding"] = dec
    mc.save(fig, a.outdir, "m3_fig1_background")
    (a.outdir / "m3_fig1_background_numbers.json").write_text(json.dumps(nums, indent=1) + "\n")
    (a.outdir / "m3_fig1_background_data.json").write_text(json.dumps(dump, indent=1) + "\n")


if __name__ == "__main__":
    main()
