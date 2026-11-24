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
It writes m3_fig3_coverage_data.json: per level, per functional name: panel, x, coverage, lower and upper bound,
filled.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from matplotlib.lines import Line2D

import jgrid
import m3_common as mc
from m3_common import plt

THR = {"68": 0.66, "95": 0.94}
NOMINAL = {"68": 0.68, "95": 0.95}
YLIM = (-0.02, 1.05)
CUT_LS = (0, (4, 2.5))


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

    dec = jgrid.verify(a.repo, names)
    E = jgrid.edges(a.repo)
    ew_names = [f"EW{i}" for i in range(mc.N_EW)]
    assert [names[i] for i in order[:n_ew]] == ew_names + ["EW_all_ones"], "EW order is not EW0..EW41, sum"
    jn = [names[i] for i in order[n_ew:-1]]
    blk = jgrid.blocks(jn)

    # panel positions: (a) 42 cells then the sum one slot apart; (b) 109 cells then the total one slot apart
    pa = order[:n_ew]
    xa = np.array([float(k) for k in range(mc.N_EW)] + [mc.N_EW + 1.0])
    pb = order[n_ew:]
    xb = np.array([float(k) for k in range(len(jn))] + [len(jn) + 1.0])

    mc.style()
    W_IN, H_IN = 6.5, 4.95
    fig = plt.figure(figsize=(W_IN, H_IN))

    def box(x0, y0, w, h):
        return fig.add_axes([x0 / W_IN, y0 / H_IN, w / W_IN, h / H_IN])

    axa = box(0.55, 2.62, 5.85, 1.3)
    axb = box(0.55, 0.47, 5.85, 1.45)
    sty = {"68": ("o", mc.BLUE, -0.18), "95": ("s", mc.RED, 0.18)}
    t = "eavail_tilt"
    g = grid[t]
    dump = {"schema": "note-figredraw-cov-data/1", "truth": t, "levels": {}}
    for l in ("68", "95"):
        c_all, lo_all, hi_all = cov(g, l)
        mk, col, dx = sty[l]
        dump["levels"][l] = []
        for ax, idx, xs, pan in ((axa, pa, xa, "a"), (axb, pb, xb, "b")):
            c, lo, hi = c_all[idx], lo_all[idx], hi_all[idx]
            bad = hi < THR[l]
            ax.axhline(NOMINAL[l], color=col, lw=0.7)
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

    # legend: per level (column), the open and filled points, then the nominal level and the test cutoff lines
    h, lab = axa.get_legend_handles_labels()
    hl = dict(zip(lab, h))
    hs, ls = [], []
    for l in ("68", "95"):
        mk, col, _ = sty[l]
        for txt in (f"{l}% interval, upper bound $\\geq$ {THR[l]:.2f}", f"{l}% interval, upper bound < {THR[l]:.2f}"):
            hs.append(hl[txt])
            ls.append(txt)
        hs += [Line2D([], [], color=col, lw=0.7), Line2D([], [], color=col, lw=0.6, ls=CUT_LS)]
        ls += [f"nominal coverage {NOMINAL[l]:.2f} (solid line)", f"test cutoff {THR[l]:.2f} (dashed line)"]
    fig.legend(hs, ls, loc="upper center", bbox_to_anchor=(0.53, 0.995), ncol=2, frameon=False, fontsize=7.0,
               handletextpad=0.5, handlelength=2.6, labelspacing=0.3, columnspacing=2.5)
    dump["j_decoding"] = dec
    mc.save(fig, a.outdir, "m3_fig3_coverage")
    (a.outdir / "m3_fig3_coverage_numbers.json").write_text(json.dumps(nums, indent=1) + "\n")
    (a.outdir / "m3_fig3_coverage_data.json").write_text(json.dumps(dump, indent=1) + "\n")


if __name__ == "__main__":
    main()
