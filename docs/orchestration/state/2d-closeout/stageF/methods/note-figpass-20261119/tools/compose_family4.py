#!/usr/bin/env python3
"""Figs. 20 and 21 as one figure, each series drawn once (Joseph's ruling of 2026-11-19, "I just don't want there to be
duplicates"; the director's chunk B).

usage: python3 compose_family4.py <pickle dir> <out dir>    (matplotlib 3.10.8, the version the pickles were written by)

Fig. 21 (compare_mec_eavail_central) draws three series: the GENIE CV without 2p2h (pale pink bars), the Valencia MEC
addition stacked on it (orange), and the unfolded data. Its data line is Fig. 20's (mode_decomp_eavail_central) item for
item, and its CV bars reach the top of Fig. 20's mode stack, which sums to the same CV. So the one new series is the
MEC addition. This recipe:
1. loads both pinned pickles only through note-figstyle-20261113/tools/restyle_family4.load(), which checks each
   sha256 first;
2. makes the palette pass's edits on each (note-figstyle-20261117/tools/palette_lib.apply), as for the installed files;
3. checks that Fig. 21's CV bar tops equal Fig. 20's stack tops, and that its data line equals Fig. 20's
   (relative 1e-12);
4. adds Fig. 21's MEC rectangles to Fig. 20's axes, each a new Rectangle with the same corner, width, height, colours,
   alpha, hatch, line width and z-order. Its legend entry, "+ Valencia MEC (2p2h)", goes after the modes;
5. lays the figure out with restyle_family4.restyle(), unchanged, at full width (LAYOUT and LEGEND_BELOW are given for
   the new name), and saves mode_decomp_mec_eavail_central.pdf and .png.
Run it under capture_palette.py. check_compose.py then proves that the new figure's items are Fig. 20's plus Fig. 21's
MEC items, bit for bit and nothing else, against the palette pass's committed arm-1 captures.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[7]
OLD = ROOT / "docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261113/tools"
PAL = ROOT / "docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261117/tools"
sys.path[:0] = [str(OLD), str(PAL), str(ROOT)]
import palette_lib  # noqa: E402
import restyle_family4 as rf4  # noqa: E402

BASE, SRC, NEW = "mode_decomp_eavail_central", "compare_mec_eavail_central", "mode_decomp_mec_eavail_central"
MEC = "+ Valencia MEC (2p2h)"
CV = "GENIE-CV (no 2p2h)"
DATA = "unfolded data"


def handles(ax):
    h, lab = ax.get_legend_handles_labels()
    return dict(zip(lab, h))


def rects(container):
    return list(container.patches) if hasattr(container, "patches") else [container]


def main():
    pdir, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    figs = {}
    for name in (BASE, SRC):
        fig = rf4.load(pdir / f"{name}.pdf.figpickle")
        palette_lib.apply(fig, name, check_fit=False)
        figs[name] = fig
    ax, sax = figs[BASE].axes[0], figs[SRC].axes[0]
    if len(figs[BASE].axes) != 1 or len(figs[SRC].axes) != 1:
        raise SystemExit("compose: each figure must have one axes")
    hb, hs = handles(ax), handles(sax)
    for need, h in ((MEC, hs), (CV, hs), (DATA, hs), (DATA, hb)):
        if need not in h:
            raise SystemExit(f"compose: no legend handle {need!r}")
    # the CV bar tops equal the top of the mode stack, bin by bin; the data line is the same
    cv_tops = [r.get_y() + r.get_height() for r in rects(hs[CV])]
    stack_top = {}
    for p in ax.patches:
        if p.get_label() == DATA or not isinstance(p, Rectangle):
            continue
        x = round(p.get_x(), 9)
        stack_top[x] = max(stack_top.get(x, 0.0), p.get_y() + p.get_height())
    xs = [round(r.get_x(), 9) for r in rects(hs[CV])]
    gap_lo = {}   # the data - GENIE-CV outline starts at the CV top: the stack's own top is below it at most by rounding
    if not all(x in stack_top for x in xs):
        raise SystemExit(f"compose: CV bars at {xs}, mode stack at {sorted(stack_top)}")
    tops = np.array([stack_top[x] for x in xs])
    # the stack's highest patch in each bin is the gap outline, which starts at the CV top: take the outline's bottom
    for p in ax.patches:
        if isinstance(p, Rectangle) and np.allclose(p.get_edgecolor()[:3], palette_lib.to_rgba(palette_lib.PAL["this_work"])[:3]):
            gap_lo[round(p.get_x(), 9)] = p.get_y()
    lo = np.array([gap_lo.get(x, np.nan) for x in xs])
    rel_cv = np.max(np.abs(lo / np.array(cv_tops) - 1))
    db, ds = hb[DATA], hs[DATA]
    yb = np.asarray((db[0] if isinstance(db, tuple) else db).get_ydata(), float)
    ys = np.asarray((ds[0] if isinstance(ds, tuple) else ds).get_ydata(), float)
    rel_data = np.max(np.abs(ys / yb - 1))
    print(f"[compose] CV bar tops / data-GENIE-CV outline bottoms - 1: max {rel_cv:.2e}; data lines: max {rel_data:.2e}")
    if not (rel_cv < 1e-12 and rel_data < 1e-12):
        raise SystemExit("compose: Fig. 21's CV or data is not Fig. 20's")
    # copy the MEC addition
    first = True
    for r in rects(hs[MEC]):
        n = Rectangle(r.get_xy(), r.get_width(), r.get_height(), facecolor=r.get_facecolor(),
                      edgecolor=r.get_edgecolor(), linewidth=r.get_linewidth(), hatch=r.get_hatch(),
                      zorder=r.get_zorder(), label=MEC if first else "_nolegend_")
        n.set_alpha(r.get_alpha())
        ax.add_patch(n)
        first = False
    want = [t.get_text() for t in ax.get_legend().get_texts()]
    i = max(k for k, w in enumerate(want) if w.startswith("GENIE-CV")) + 1   # after the modes
    want = want[:i] + [MEC] + want[i:]
    pick = handles(ax)
    leg = ax.get_legend()
    ax.legend([pick[w] for w in want], want, loc=leg._loc, frameon=False)
    plt.close(figs[SRC])
    rf4.LAYOUT[NEW] = (1.0, 0.55)
    rf4.LEGEND_BELOW[NEW] = 3
    fig = rf4.restyle(figs[BASE], NEW)
    got = palette_lib.legend_entries(fig)
    if sorted(want) != got:
        raise SystemExit(f"compose: legend {got}, wanted {sorted(want)}")
    fig.savefig(out / f"{NEW}.pdf")
    fig.savefig(out / f"{NEW}.png", dpi=200)
    print(f"[compose] wrote {out / NEW}.pdf; legend {want}")


if __name__ == "__main__":
    main()
