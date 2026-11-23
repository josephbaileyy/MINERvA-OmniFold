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

REDRAW COPY (note-figredraw-20261123, 2026-11-23): docs/analysis-note/figures/methods_m3/fig_m3_coverage.py with the
drawing changed and nothing upstream of it. The input, its pin, the arrays and every mc.check line are the original's.
Changes, presentation only: the one index axis is split into two panels, (a) the 42 (E_avail, W) cells (W bin
within E_avail bin, as Fig. 7(a)) and their sum, set apart; (b) the 109 joint cells in (p_T, p_par) blocks
(tools/jgrid.py, as Fig. 7(b)) and the total, set apart. Markers, filled/open meaning, nominal and threshold lines,
legend entries and the title are unchanged. Every text at least 7 pt at the printed width (6.5 in canvas).
ROUND 2 (2026-11-23, the outside reviewer's suggestions as Joseph approved them): the in-figure header sentence
("signal rate lowered by about 10%, ... of 153") is removed (the caption carries it); the legend gains one entry per
reference line, so the nominal levels (solid: 0.68, 0.95) and the test cutoffs (dashed: 0.66, 0.94) are named
separately, in two columns (68% blue, 95% red); the dash pattern is longer so it reads at print size. Points, bars,
fill rule and panel layout are round 1's.
ROUND 3 (2026-11-23, two variants for the reviewer to choose from; round 2's copy is in runs/round2-tools/):
  --variant R  round 2 plus the reviewer's second-turn suggestions (ask-codex2/REPLY2.md): the solid nominal-coverage
               lines (0.68, 0.95) and their legend entries are dropped; the dashed test cutoffs 0.66/0.94 stay; the
               failure counts "51/153 failures (68%)" and "42/153 failures (95%)" are printed above the plot, each
               counted from the receipt (upper bound < cutoff over the 153 drawn functionals) and asserted equal to
               the mc.check counts.
  --variant D  the reviewer's first-turn redesign (ask-codex2/REPLY1.md): one row per level (68%, 95%; same 0-1
               scale), each headed by its failure count; each row in three sections: the 42 projection cells, the
               109 joint cells, and the projection sum and the integrated total; within the projection and joint
               families the points are ordered by the upper confidence bound (the bound the test uses; stable sort,
               ties in functional order), so the failures cluster on the left; dot = empirical coverage, bar from
               the lower to the upper bound, filled when the upper bound is below the dashed, labelled cutoff.
               Sorting drops the cell identity from the drawing; the dump keeps every point's name and rank.
ROUND 4 (2026-11-23, polish of the reviewer's choice 8 D, ask-codex2/REPLY3.md; round 3's copy is in runs/round3-tools/):
  --variant P  variant D with the legend shortened to one compact key of four entries, shared by both rows (the row
               headings carry the level colours): filled marker = upper bound below the cutoff (fails), open = not,
               bar = lower to upper confidence bound, dashed = test cutoff. The canvas is 0.13 in shorter (one legend
               row instead of two). Points, bars, fill rule, order and every other text are variant D's.
It writes m3_fig3_coverage_data.json: per level, per functional name: panel (and axes index, rank for D), x, coverage,
lower and upper bound, filled.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from matplotlib.legend_handler import HandlerTuple
from matplotlib.lines import Line2D

import jgrid
import m3_common as mc
from m3_common import plt

THR = {"68": 0.66, "95": 0.94}
NOMINAL = {"68": 0.68, "95": 0.95}
YLIM = (-0.02, 1.05)
CUT_LS = (0, (4, 2.5))


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


def main() -> None:
    variant = pop_variant()
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

    dec = jgrid.verify(a.repo, names)
    E = jgrid.edges(a.repo)
    ew_names = [f"EW{i}" for i in range(mc.N_EW)]
    assert [names[i] for i in order[:n_ew]] == ew_names + ["EW_all_ones"], "EW order is not EW0..EW41, sum"
    jn = [names[i] for i in order[n_ew:-1]]
    blk = jgrid.blocks(jn)

    t = "eavail_tilt"
    g = grid[t]
    # ROUND 3: the failure counts printed in the figure, counted over the 153 drawn functionals and tied to the checks
    n_fail = {l: int(np.sum(cov(g, l)[2][order] < THR[l])) for l in ("68", "95")}
    assert n_fail == {"68": below[(t, "68")], "95": below[(t, "95")]} == {"68": 51, "95": 42}, n_fail
    head_txt = {l: f"{n_fail[l]}/{len(order)} failures ({l}%)" for l in ("68", "95")}
    dump = {"schema": "note-figredraw-cov-data/2", "variant": variant, "truth": t, "levels": {},
            "failure_counts": n_fail, "printed_counts": head_txt}
    sty = {"68": ("o", mc.BLUE, -0.18), "95": ("s", mc.RED, 0.18)}
    mc.style()
    if variant == "R":
        fig = draw_r(a, names, order, n_ew, jn, blk, E, g, cov, sty, dump, head_txt)
    else:
        fig = draw_d(a, names, order, n_ew, g, cov, sty, dump, head_txt, polish=(variant == "P"))
    dump["j_decoding"] = dec
    mc.save(fig, a.outdir, "m3_fig3_coverage")
    (a.outdir / "m3_fig3_coverage_numbers.json").write_text(json.dumps(nums, indent=1) + "\n")
    (a.outdir / "m3_fig3_coverage_data.json").write_text(json.dumps(dump, indent=1) + "\n")


def draw_r(a, names, order, n_ew, jn, blk, E, g, cov, sty, dump, head_txt):
    """Round 2's two panels, without the nominal lines, with the failure counts above the legend."""
    # panel positions: (a) 42 cells then the sum one slot apart; (b) 109 cells then the total one slot apart
    pa = order[:n_ew]
    xa = np.array([float(k) for k in range(mc.N_EW)] + [mc.N_EW + 1.0])
    pb = order[n_ew:]
    xb = np.array([float(k) for k in range(len(jn))] + [len(jn) + 1.0])
    W_IN, H_IN = 6.5, 4.95
    fig = plt.figure(figsize=(W_IN, H_IN))

    def box(x0, y0, w, h):
        return fig.add_axes([x0 / W_IN, y0 / H_IN, w / W_IN, h / H_IN])

    axa = box(0.55, 2.62, 5.85, 1.3)
    axb = box(0.55, 0.47, 5.85, 1.45)
    for l in ("68", "95"):
        c_all, lo_all, hi_all = cov(g, l)
        mk, col, dx = sty[l]
        dump["levels"][l] = []
        for ax, idx, xs, pan in ((axa, pa, xa, "a"), (axb, pb, xb, "b")):
            c, lo, hi = c_all[idx], lo_all[idx], hi_all[idx]
            bad = hi < THR[l]
            ax.axhline(THR[l], color=col, lw=0.6, ls=CUT_LS)
            ax.vlines(xs + dx, lo, hi, color=col, lw=0.5, alpha=0.6)
            ax.plot(xs[~bad] + dx, c[~bad], mk, ms=2.4, mfc="white", mec=col, mew=0.6,
                    label=f"{l}% interval, upper bound $\\geq$ {THR[l]:.2f}")
            ax.plot(xs[bad] + dx, c[bad], mk, ms=2.4, color=col, label=f"{l}% interval, upper bound < {THR[l]:.2f}")
            assert np.all(lo >= YLIM[0]) and np.all(hi <= YLIM[1]) and np.all((c >= YLIM[0]) & (c <= YLIM[1]))
            dump["levels"][l] += [{"name": names[i], "panel": pan, "x": float(x + dx), "coverage": float(cc),
                                   "lcb": float(lo_), "ucb": float(hi_), "filled": bool(bb)}
                                  for i, x, cc, lo_, hi_, bb in zip(idx, xs, c, lo, hi, bad)]
    for ax in (axa, axb):
        ax.set_ylim(*YLIM)
        ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_ylabel("empirical coverage")

    # (a): W bin within E_avail bin, then the sum
    for k in range(1, len(mc.EAVAIL_EDGES) - 1):
        axa.axvline(k * mc.N_W - 0.5, color="0.8", lw=0.5, zorder=0)
    axa.axvline(mc.N_EW + 0.0, color="0.45", lw=0.7, zorder=0.5)
    axa.set_xlim(-0.8, xa[-1] + 0.8)
    axa.set_xticks(list(range(mc.N_EW)) + [xa[-1]])
    axa.set_xticklabels([str(i % mc.N_W + 1) for i in range(mc.N_EW)] + ["sum"], fontsize=7.0)
    axa.tick_params(axis="x", length=2, pad=1.5)
    for k in range(len(mc.EAVAIL_EDGES) - 1):
        lo, hi = mc.EAVAIL_EDGES[k], mc.EAVAIL_EDGES[k + 1]
        txt = f"{lo:g}–{hi:g}" if hi < 100 else rf"$\geq${lo:g}"
        axa.text(k * mc.N_W + (mc.N_W - 1) / 2, 1.0, txt, transform=axa.get_xaxis_transform(), ha="center",
                 va="bottom", fontsize=7.0, color="0.3")
    axa.set_xlabel(r"$(E_{\rm avail},W)$ cell: $W$ bin 1–6 within each $E_{\rm avail}$ bin (GeV, top); "
                   r"$W$ edges 0, 1.1, 1.4, 1.8, 2.2, 3, 100 GeV", fontsize=7.5, labelpad=2)
    axa.text(0.0, 1.12, r"(a) $(E_{\rm avail},W)$ projection, 42 cells and their sum", transform=axa.transAxes,
             fontsize=8)

    # (b): (p_T, p_par) blocks, then the total
    for b, (ipt, ipz, k0, k1) in enumerate(blk):
        if b % 2 == 0:
            axb.axvspan(k0 - 0.5, k1 + 0.5, color="0.92", lw=0, zorder=0)
    pt_groups = {}
    for ipt, ipz, k0, k1 in blk:
        g0, g1 = pt_groups.get(ipt, (k0, k1))
        pt_groups[ipt] = (min(g0, k0), max(g1, k1))
    for ipt, (k0, k1) in pt_groups.items():
        if k0 > 0:
            axb.axvline(k0 - 0.5, color="0.45", lw=0.7, zorder=0.5)
        axb.text((k0 + k1) / 2, 1.0, rf"$p_T$ {jgrid.rng(E['pt'], ipt)} GeV/$c$", transform=axb.get_xaxis_transform(),
                 ha="center", va="bottom", fontsize=7.0, color="0.3")
    axb.axvline(len(jn) + 0.0, color="0.45", lw=0.7, zorder=0.5)
    axb.set_xlim(-0.8, xb[-1] + 0.8)
    axb.set_xticks([(k0 + k1) / 2 for _, _, k0, k1 in blk] + [xb[-1]])
    axb.set_xticklabels([jgrid.rng(E["pz"], ipz) for _, ipz, _, _ in blk] + ["total"], fontsize=7.0)
    axb.tick_params(axis="x", length=0, pad=2.5)
    axb.set_xlabel(r"coarse joint cell, in blocks of one $p_T$ bin (top) and one $p_\parallel$ bin (GeV/$c$, below); "
                   r"within a block by $E_{\rm avail}$, $q_3$, $W$ bin", fontsize=7.5, labelpad=2)
    axb.text(0.0, 1.10, f"(b) {len(jn)} joint-cell integrals and the total", transform=axb.transAxes, fontsize=8)

    # legend: per level (column), the open and filled points, then the test cutoff line; the counts above each column
    h, lab = axa.get_legend_handles_labels()
    hl = dict(zip(lab, h))
    hs, ls = [], []
    for l in ("68", "95"):
        mk, col, _ = sty[l]
        for txt in (f"{l}% interval, upper bound $\\geq$ {THR[l]:.2f}", f"{l}% interval, upper bound < {THR[l]:.2f}"):
            hs.append(hl[txt])
            ls.append(txt)
        hs.append(Line2D([], [], color=col, lw=0.6, ls=CUT_LS))
        ls.append(f"test cutoff {THR[l]:.2f} (dashed line)")
    leg = fig.legend(hs, ls, loc="upper center", bbox_to_anchor=(0.53, 1.0 - 0.24 / H_IN), ncol=2, frameon=False,
                     fontsize=7.0, handletextpad=0.5, handlelength=2.6, labelspacing=0.3, columnspacing=2.5)
    fig.canvas.draw()
    inv = fig.transFigure.inverted()
    for k, l in enumerate(("68", "95")):   # each count above its legend column, left-aligned with the column's handles
        bb = leg.get_texts()[3 * k].get_window_extent()
        hb = leg.legend_handles[3 * k].get_window_extent() if hasattr(leg.legend_handles[3 * k], "get_window_extent") \
            else bb
        x0 = inv.transform((min(hb.x0, bb.x0), 0))[0]
        fig.text(x0, 1.0 - 0.03 / H_IN, head_txt[l], ha="left", va="top", fontsize=8, color=sty[l][1],
                 fontweight="bold")
    return fig


def draw_d(a, names, order, n_ew, g, cov, sty, dump, head_txt, polish=False):
    """One row per level; sections: 42 projection cells, 109 joint cells (each ordered by the upper bound), sum+total.
    ROUND 4 (polish=True, variant P): one compact four-entry legend key, and a canvas 0.13 in shorter."""
    ew = order[:n_ew - 1]                  # EW0..EW41
    jsel = order[n_ew:-1]                  # the 109 J cells
    st = [order[n_ew - 1], order[-1]]      # EW_all_ones (the projection sum), total_integrated
    assert names[st[0]] == "EW_all_ones" and names[st[1]] == "total_integrated" and len(ew) == 42 and len(jsel) == 109
    W_IN, H_IN = (6.5, 4.62) if polish else (6.5, 4.75)
    fig = plt.figure(figsize=(W_IN, H_IN))

    def box(x0, y0, w, h):
        return fig.add_axes([x0 / W_IN, y0 / H_IN, w / W_IN, h / H_IN])

    L, R, GAP, W_ST = 0.55, 0.08, 0.1, 0.62
    span = {"proj": (-1.0, 42.0), "joint": (-1.0, 109.0)}
    unit = (W_IN - L - R - 2 * GAP - W_ST) / sum(b - a_ for a_, b in span.values())
    w_proj, w_joint = unit * (span["proj"][1] - span["proj"][0]), unit * (span["joint"][1] - span["joint"][0])
    row_y = {"68": 2.62, "95": 0.55}
    AX_H = 1.38
    axes = {}
    for l in ("68", "95"):
        y = row_y[l]
        axes[(l, "proj")] = box(L, y, w_proj, AX_H)
        axes[(l, "joint")] = box(L + w_proj + GAP, y, w_joint, AX_H)
        axes[(l, "st")] = box(L + w_proj + w_joint + 2 * GAP, y, W_ST, AX_H)
    fam_idx = {"proj": ew, "joint": jsel, "st": st}
    fam_lab = {"proj": r"42 $(E_{\rm avail},W)$ projection cells", "joint": "109 joint cells",
               "st": "sum, total"}
    for k, l in enumerate(("68", "95")):
        c_all, lo_all, hi_all = cov(g, l)
        mk, col, _ = sty[l]
        dump["levels"][l] = []
        for fam in ("proj", "joint", "st"):
            ax = axes[(l, fam)]
            idx = np.array(fam_idx[fam])
            if fam != "st":   # ordered by the upper bound used by the test; stable: ties keep functional order
                idx = idx[np.argsort(hi_all[idx], kind="stable")]
            xs = np.arange(len(idx), dtype=float)
            c, lo, hi = c_all[idx], lo_all[idx], hi_all[idx]
            bad = hi < THR[l]
            ax.axhline(THR[l], color=col, lw=0.6, ls=CUT_LS)
            ax.vlines(xs, lo, hi, color=col, lw=0.6, alpha=0.6)
            ax.plot(xs[~bad], c[~bad], mk, ms=2.4, mfc="white", mec=col, mew=0.6,
                    label=f"{l}% interval, upper bound $\\geq$ {THR[l]:.2f}")
            ax.plot(xs[bad], c[bad], mk, ms=2.4, color=col, label=f"{l}% interval, upper bound < {THR[l]:.2f}")
            assert np.all(lo >= YLIM[0]) and np.all(hi <= YLIM[1]) and np.all((c >= YLIM[0]) & (c <= YLIM[1]))
            if fam != "st":
                assert np.all(np.diff(hi) >= 0), f"{l} {fam}: not ordered by the upper bound"
                assert np.all(bad[:int(bad.sum())]) and not np.any(bad[int(bad.sum()):]), "failures do not lead"
            ai = fig.axes.index(ax)
            dump["levels"][l] += [{"name": names[i], "panel": fam, "axes": ai, "x": float(x),
                                   "rank": (int(x) + 1 if fam != "st" else None), "coverage": float(cc),
                                   "lcb": float(lo_), "ucb": float(hi_), "filled": bool(bb)}
                                  for i, x, cc, lo_, hi_, bb in zip(idx, xs, c, lo, hi, bad)]
            ax.set_ylim(*YLIM)
            ax.set_xlim(*(span[fam] if fam != "st" else (-0.7, 1.7)))
            ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
            if fam == "proj":
                ax.set_ylabel("empirical coverage")
            else:
                ax.tick_params(axis="y", labelleft=False)
            if fam == "st":
                ax.set_xticks([0, 1])
                ax.set_xticklabels(["sum", "total"], fontsize=7.0)
                ax.tick_params(axis="x", length=2, pad=1.5)
            else:
                n = len(idx)
                ticks = [1] + list(range(10 if n < 60 else 20, n + 1, 10 if n < 60 else 20))
                ax.set_xticks([tk - 1 for tk in ticks])
                ax.set_xticklabels([str(tk) for tk in ticks], fontsize=7.0)
                ax.tick_params(axis="x", length=2, pad=1.5)
            ax.text(0.5 if fam == "st" else 0.0, 1.0 + 0.03 / AX_H, fam_lab[fam], transform=ax.transAxes,
                    ha="center" if fam == "st" else "left", va="bottom", fontsize=7.0, color="0.3")
            if fam == "joint":   # the cutoff, labelled above its line at the left (where the failures sit below it)
                ax.text(span["joint"][0] + 1.0, THR[l] + 0.015, f"test cutoff {THR[l]:.2f}", ha="left",
                        va="bottom", fontsize=7.0, color=col)
        axp = axes[(l, "proj")]
        n_row = int(sum(1 for p in dump["levels"][l] if p["filled"]))
        assert n_row == int(head_txt[l].split("/")[0])
        axp.text(0.0, 1.0 + 0.2 / AX_H, f"({'ab'[k]}) {l}% intervals: {head_txt[l].split(' (')[0]} "
                 f"(upper bound below {THR[l]:.2f})", transform=axp.transAxes,
                 ha="left", va="bottom", fontsize=8, color=col, fontweight="bold")
    fig.text((L + (w_proj + GAP + w_joint) / 2) / W_IN, 0.16 / H_IN, "rank within the section: cells ordered by "
             "the upper confidence bound used by the test (1 = lowest)", ha="center", va="bottom", fontsize=7.5)
    if polish:   # ROUND 4: one compact key, shared by the two rows
        hs = [tuple(Line2D([], [], ls="none", marker=sty[l][0], ms=2.6, color=sty[l][1]) for l in ("68", "95")),
              tuple(Line2D([], [], ls="none", marker=sty[l][0], ms=2.6, mfc="white", mec=sty[l][1], mew=0.6)
                    for l in ("68", "95")),
              Line2D([], [], ls="none", marker="|", ms=8, mew=0.6, color="0.3", alpha=0.6),
              Line2D([], [], color="0.3", lw=0.6, ls=CUT_LS)]
        ls = ["upper bound below the cutoff (fails)", "not below", "lower to upper confidence bound", "test cutoff"]
        leg = fig.legend(hs, ls, loc="upper center", bbox_to_anchor=(0.5, 0.995), ncol=4, frameon=False,
                         fontsize=7.0, handletextpad=0.4, handlelength=1.8, columnspacing=1.4,
                         handler_map={tuple: HandlerTuple(ndivide=None, pad=0.4)})
        fig.canvas.draw()
        lb = leg.get_window_extent()
        assert lb.x0 >= 0.04 * fig.dpi and lb.x1 <= (W_IN - 0.04) * fig.dpi, "the key is wider than the canvas"
        dump["legend"] = [t.get_text() for t in leg.get_texts()]
        return fig
    # legend: per level (column), the open and filled points and the dashed cutoff
    hs, ls = [], []
    for l in ("68", "95"):
        mk, col, _ = sty[l]
        hs += [Line2D([], [], ls="none", marker=mk, ms=2.4, mfc="white", mec=col, mew=0.6),
               Line2D([], [], ls="none", marker=mk, ms=2.4, color=col)]
        ls += [f"{l}%: upper bound $\\geq$ {THR[l]:.2f}", f"{l}%: upper bound < {THR[l]:.2f} (fails)"]
    hs.append(Line2D([], [], color="0.3", lw=0.6, ls=CUT_LS))
    ls.append("test cutoff (dashed)")
    hs.append(Line2D([], [], color="0.3", lw=0.6, alpha=0.6))
    ls.append("bar: lower to upper bound")
    fig.legend(hs, ls, loc="upper center", bbox_to_anchor=(0.53, 0.995), ncol=3, frameon=False, fontsize=7.0,
               handletextpad=0.5, handlelength=2.2, labelspacing=0.3, columnspacing=1.6)
    return fig


if __name__ == "__main__":
    main()
