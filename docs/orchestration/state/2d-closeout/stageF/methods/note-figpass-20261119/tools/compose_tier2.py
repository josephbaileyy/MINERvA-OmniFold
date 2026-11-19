#!/usr/bin/env python3
"""Figs. 7, 9, 10 and 13 with each series drawn once (Joseph's ruling of 2026-11-19; the director's chunk B rulings
(1) option (a) and (2) option (i)).

usage (under note-figstyle-20261117/tools/remap_anc.py, in the tier-2 ROOT environment, as the palette pass ran them):
  python3 remap_anc.py <anc dir> compose_tier2.py <xsec.root> <anc dir> <out dir>

The four producers run unchanged in this process (runpy, as __main__, with the palette pass's restyle arguments
--style restyle-2026-10 --print-font). Each figure they save is held, not written, after the palette pass's edits
(note-figstyle-20261117/tools/palette_lib.apply, as its arm 1 drew the installed files):
  plot_2d_cross_section.py   -> MEFHC_5iter_xsec_proj_pt, _proj_pz (Fig. 7's lower panels)
  compare_to_models.py       -> model_comp_projections (Fig. 13)
  plot_2d_threeway_fig13.py  -> MEFHC_5iter_fig13 (Fig. 7's upper panel, the slice mosaic)
  plot_2d_paper_comparison.py -> MEFHC_5iter_xsec_paper_pt_slices, _pz_slices (Figs. 9 and 10)
Then:
(1) Fig. 13 into Fig. 7's projections. Fig. 13's "This work" line must equal the projection's (same x, y to 1e-12),
    so the two figures share coordinates. Fig. 13's published line is added to the projection's upper axes as drawn.
    Its Tune v1 line is MINERvA's published-ancillary prediction, a different series from the projection's Tune v1
    histogram (our simulation's truth, the prior). It is added dashed, under its source's name. The prior's legend
    entry names its source, and the ratio's axis label names the prior.
(2) The mosaic into Figs. 9 and 10. Each mosaic panel is matched to the slice panel whose "This work" points are
    proportional to its own (the two producers scale each panel differently). The ratio must be constant over the
    panel's bins (relative 1e-12), which also pairs the bins. The mosaic's prior histogram, divided by that ratio, must
    equal the slice panel's prior histogram (relative 1e-12): the mosaic draws the prior, not the ancillary curve. The
    mosaic's published points and their bars (the statistical-covariance diagonal), scaled by the panel's ratio, are
    added to the slice panel. That is the one series the mosaic draws that Figs. 9 and 10 did not. Each figure legend
    gains the published entry, and its prior entry names its source as in Fig. 7.
The mosaic and Fig. 13 are not written. The four composed figures are saved as the producers saved them (same
names and savefig keywords), PDF and PNG. Run under capture_palette.py; check_tier2.py then checks the captures.
"""
import json
import runpy
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[7]
PAL = ROOT / "docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261117/tools"
sys.path[:0] = [str(PAL)]
import palette_lib  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

P2 = ROOT / "2d-unfolding"
STYLE = ["--style", "restyle-2026-10", "--print-font"]
THIS, PUB, TUNE = "This work (OmniFold)", "Published (PRD 104, 092007)", "GENIE 2.12.6 + MINERvA Tune v1"
PRIOR_NEW = "Tune v1: our simulation (the prior)"
ANC_NEW = "Tune v1: published prediction"
RATIO_OLD, RATIO_NEW = "This work / GENIE", "This work / prior"
TOL = 1e-12
HELD = {}
_inner = Figure.savefig


def hold(self, fname, *a, **k):
    if isinstance(fname, (str, bytes)) or hasattr(fname, "__fspath__"):
        stem = Path(str(fname)).name.split(".")[0]
        if stem not in HELD:
            palette_lib.apply(self, stem)
            HELD[stem] = (self, dict(k))
    return None


def run(script, args):
    saved = sys.argv
    sys.argv = [str(script), *args]
    sys.path.insert(0, str(script.parent))
    try:
        runpy.run_path(str(script), run_name="__main__")
    finally:
        sys.argv = saved
        sys.path.remove(str(script.parent))


def eb(ax, label):
    """An errorbar container's points and half-lengths: (x, y, xerr, yerr)."""
    c = [c for c in ax.containers if c.get_label() == label]
    if len(c) != 1:
        raise SystemExit(f"compose: {len(c)} errorbar containers {label!r} in an axes")
    line, _caps, cols = c[0].lines
    x, y = np.asarray(line.get_xdata(), float), np.asarray(line.get_ydata(), float)
    half = []
    for col in cols:
        seg = col.get_segments()
        half.append(np.array([max(abs(s[1][0] - s[0][0]), abs(s[1][1] - s[0][1])) / 2 for s in seg]))
    xerr, yerr = (half[0], half[1]) if len(half) == 2 else (None, half[-1])
    return x, y, xerr, yerr, c[0]


def rel(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.max(np.abs(a - b) / np.maximum(np.abs(b), 1e-300))) if a.size else 0.0


def relegend(ax, order, rename=None, **extra):
    rename = rename or {}
    h, lab = ax.get_legend_handles_labels()
    pick = dict(zip(lab, h))
    old = ax.get_legend()
    kw = {"loc": old._loc, "frameon": False, "ncol": old._ncols, **palette_lib._anchor(old)} if old else {}
    kw.update(extra)
    if old:
        old.remove()
    ax.legend([pick[x] for x in order], [rename.get(x, x) for x in order], **kw)


def main():
    xsec, anc, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_held"   # the producers write their text reports here; their figures are held, not written
    tmp.mkdir(exist_ok=True)
    Figure.savefig = hold
    run(P2 / "plot_2d_cross_section.py", ["--infile", xsec, "--prefix", str(tmp / "MEFHC_5iter_xsec"), *STYLE])
    run(P2 / "compare_to_models.py", ["--ours", xsec, "--out-prefix", str(tmp / "model_comp"), *STYLE])
    run(P2 / "plot_2d_threeway_fig13.py", ["--infile", xsec, "--paper", str(anc / "cov_ptpl_minerva_inclusive_6GeV.root"),
                                           "--out", str(tmp / "MEFHC_5iter_fig13.png"), *STYLE])
    run(P2 / "plot_2d_paper_comparison.py", ["--infile", xsec, "--prefix", str(tmp / "MEFHC_5iter_xsec_paper"), *STYLE])
    Figure.savefig = _inner
    report = {"fig7": {}, "slices": {}}

    # (1) Fig. 13 into Fig. 7's projections
    mc = HELD["model_comp_projections"][0]
    for k, stem in enumerate(("MEFHC_5iter_xsec_proj_pt", "MEFHC_5iter_xsec_proj_pz")):
        fig, kw = HELD[stem]
        top, bot = fig.axes[0], fig.axes[1]
        src = {ln.get_label(): ln for ln in mc.axes[k].lines}
        x7, y7, _, _, _ = eb(top, THIS)
        xs, ys = np.asarray(src[THIS].get_xdata(), float), np.asarray(src[THIS].get_ydata(), float)
        if xs.shape != x7.shape or rel(xs, x7) > TOL or rel(ys, y7) > TOL:
            raise SystemExit(f"compose: {stem}: Fig. 13's This work is not the projection's")
        for lab, new_lab, ls in ((PUB, PUB, None), (TUNE, ANC_NEW, "--")):
            ln = Line2D([], [])
            ln.update_from(src[lab])   # style; update_from also copies the source's transform, reset below
            ln.set_transform(top.transData)
            ln.set_data(src[lab].get_xdata(), src[lab].get_ydata())
            ln.set_label(new_lab)
            ln.set_zorder(src[lab].get_zorder())
            if ls:
                ln.set_linestyle(ls)
            top.add_line(ln)
        relegend(top, [THIS, PUB, TUNE, ANC_NEW], rename={TUNE: PRIOR_NEW}, loc="upper right")
        if bot.get_ylabel() != RATIO_OLD:
            raise SystemExit(f"compose: {stem}: ratio label {bot.get_ylabel()!r}")
        bot.set_ylabel(RATIO_NEW)
        report["fig7"][stem] = {"this_work_rel": max(rel(xs, x7), rel(ys, y7)), "added": [PUB, ANC_NEW],
                                "renamed": {TUNE: PRIOR_NEW, RATIO_OLD: RATIO_NEW}}

    # (2) the mosaic's published points into Figs. 9 and 10
    mos = HELD["MEFHC_5iter_fig13"][0]
    mos_axes = [ax for ax in mos.axes if any(c.get_label() == THIS for c in ax.containers)]
    used = set()
    for stem in ("MEFHC_5iter_xsec_paper_pt_slices", "MEFHC_5iter_xsec_paper_pz_slices"):
        fig, kw = HELD[stem]
        panels = [ax for ax in fig.axes if ax.get_visible() and any(c.get_label() == THIS for c in ax.containers)]
        rows = []
        for i, ax in enumerate(panels):
            x9, y9, xe9, _, _ = eb(ax, THIS)
            match = None
            for j, m in enumerate(mos_axes):
                if j in used:
                    continue
                _, ym, _, _, _ = eb(m, THIS)
                if ym.shape != y9.shape:
                    continue
                nz = np.isfinite(ym) & np.isfinite(y9) & (ym != 0) & (y9 != 0)
                if not nz.any() or not np.array_equal(ym == 0, y9 == 0):
                    continue
                r = y9[nz] / ym[nz]
                if np.max(np.abs(r / np.median(r) - 1)) < TOL:
                    match = (j, m, float(np.median(r)), float(np.max(np.abs(r / np.median(r) - 1))))
                    break
            if match is None:
                raise SystemExit(f"compose: {stem} panel {i}: no mosaic panel with proportional This work")
            j, m, r, dev = match
            used.add(j)
            # the mosaic's prior is the slice panel's prior
            st = [p for p in ax.patches if p.get_label() == TUNE]
            if len(st) != 1:
                raise SystemExit(f"compose: {stem} panel {i}: {len(st)} prior histograms")
            prior9 = np.asarray(st[0].get_data().values, float)
            tl = [ln for ln in m.lines if ln.get_label() == TUNE]
            if len(tl) != 1:
                raise SystemExit(f"compose: mosaic panel {j}: {len(tl)} prior lines")
            priorm = np.asarray(tl[0].get_ydata(), float)[0::2]   # stair_xy: each bin's value twice
            if priorm.shape != prior9.shape or rel(priorm * r, prior9) > 1e-9:
                raise SystemExit(f"compose: {stem} panel {i}: the mosaic's prior is not the slice's "
                                 f"(max rel {rel(priorm * r, prior9):.2e})")
            _, pm, _, pe, pcont = eb(m, PUB)
            pline = pcont.lines[0]
            ax.errorbar(x9, pm * r, yerr=pe * r, xerr=xe9, fmt="s", color=pline.get_color(),
                        ecolor=pline.get_color(), markersize=2.3, elinewidth=0.6, capsize=1.0, label=PUB, zorder=3)
            rows.append({"panel": i, "mosaic_panel": j, "ratio": r, "this_work_ratio_dev": dev,
                         "prior_rel": rel(priorm * r, prior9), "n_bins": int(y9.size),
                         "published_finite": int(np.isfinite(pm).sum())})
        if len(rows) != len(panels):
            raise SystemExit(f"compose: {stem}: {len(rows)} of {len(panels)} panels matched")
        # the figure legend gains the published entry, after This work
        old = fig.legends[0]
        want = [t.get_text() for t in old.get_texts()]
        h, lab = panels[0].get_legend_handles_labels()
        pick = dict(zip(lab, h))
        order = [w for w in want if w == THIS] + [PUB] + [w for w in want if w != THIS]
        names = {TUNE: PRIOR_NEW}   # the prior names its source, as in Fig. 7 (the ancillary curve is drawn there)
        kwl = {"loc": old._loc, "frameon": False, "ncol": old._ncols, **palette_lib._anchor(old),
               "fontsize": old._fontsize}
        old.remove()
        fig.legend([pick[x] for x in order], [names.get(x, x) for x in order], **kwl)
        report["slices"][stem] = rows
    if len(used) != len(mos_axes):
        raise SystemExit(f"compose: {len(mos_axes) - len(used)} mosaic panels matched no slice panel")

    for stem in ("MEFHC_5iter_xsec_proj_pt", "MEFHC_5iter_xsec_proj_pz", "MEFHC_5iter_xsec_paper_pt_slices",
                 "MEFHC_5iter_xsec_paper_pz_slices"):
        fig, kw = HELD[stem]
        kw.pop("dpi", None)
        fig.savefig(out / f"{stem}.pdf", **kw)
        fig.savefig(out / f"{stem}.png", dpi=200, **kw)
    (out / "compose_tier2.json").write_text(json.dumps(report, indent=1) + "\n")
    print(f"[compose_tier2] wrote 4 figures; mosaic panels matched {len(used)} of {len(mos_axes)}")
    plt.close("all")


if __name__ == "__main__":
    main()
