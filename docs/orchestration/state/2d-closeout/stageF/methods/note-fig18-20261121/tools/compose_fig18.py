#!/usr/bin/env python3
"""Fig. 18 (fig:3dmodels) redrawn with generator/data ratio panels, from the same pinned pickle and recipe as installed.

usage: python3 compose_fig18.py <note-figstyle-20261113/runs/family4/pickles> <out dir>
       (matplotlib 3.10.8, the version the pickle was written by; figenv/mpl3108)

The arrays come from the installed recipe (note-figpass-20261119/tools/fix_family4.py: the pinned pickle loaded only
through restyle_family4.load(), which checks its sha256, then labels.tsv, palette_lib.apply, texts.tsv and
restyle_family4.restyle(), all unchanged). From that figure this tool reads, for each of the three panels:
  - the bin edges and the four generator predictions (the StepPatches), each tied to its legend label by colour and
    checked equal, bitwise, to the same generator's marker line;
  - the unfolded central values (the errorbar container's data line, which has no error bars), checked equal to the
    duplicate marker line and placed at the bin centres.
It then draws a new figure (the director's Fig. 18 request, 2026-11-21, Joseph's suggestions):
  - under each panel a generator/data ratio panel, labelled "gen. / data" as Fig. 19, with a dashed line at 1, on one
    y range shared by the three ratio panels so that they can be compared with each other;
  - generators as thin step lines only (no markers), the data as points;
  - p_T drawn on 0-2.5 GeV/c (the [2.5, 4.5) bin is left off and listed in the record); p_parallel on a log axis over
    its full range (no bin left off); E_avail on its full drawn range, as installed;
  - one-line y labels, the power of ten as an axis-top multiplier, one legend above the panels, no stamp;
  - the canvas at the printed width (\\textwidth, 6.5 in), so the fonts print at note_print_style's sizes.
After drawing, every step, point and ratio is read back from the figure's artists and must equal the source arrays
bitwise; the drawn texts must not overlap one another, must lie on the canvas, and the legend must not cover any axes.
Any failure stops the run before a file is written.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import StepPatch  # noqa: E402
from matplotlib.ticker import FixedLocator, NullFormatter, NullLocator, ScalarFormatter  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[7]
METH = ROOT / "docs/orchestration/state/2d-closeout/stageF/methods"
sys.path[:0] = [str(METH / "note-figpass-20261119/tools"), str(ROOT)]
import fix_family4 as ff  # noqa: E402  (puts note-figstyle-20261113/tools and -20261117/tools on the path)
import note_print_style as nps  # noqa: E402

NAME = "generators_vs_unfolded_band_central"
GENS = ("GENIE-CV", "Tune-v1", "NuWro", "GiBUU")
DATA_LABEL = "unfolded (this work)"
# per panel: x label, one-line y label, the expected multiplier exponent, the drawn x range, the x scale
PANELS = (
    (r"$p_T$ (GeV/c)", r"$d\sigma/dp_T$ (cm$^2$/(GeV/c)/nucleon)", -38, (0.0, 2.5), "linear"),
    (r"$p_\parallel$ (GeV/c)", r"$d\sigma/dp_\parallel$ (cm$^2$/(GeV/c)/nucleon)", -39, (1.5, 60.0), "log"),
    (r"$E_{\rm avail}$ (GeV)", r"$d\sigma/dE_{\rm avail}$ (cm$^2$/GeV/nucleon)", -38, (0.0, 3.0), "linear"),
)
LOG_TICKS = (2.0, 5.0, 10.0, 20.0, 50.0)
FIGSIZE = nps.figsize(1.0, 0.62)       # 6.5 in x 4.03 in, printed at \textwidth (scale 1)
GEN_LW, DATA_MS = 1.0, 3.5
RATIO_TICKS = (0.0, 0.5, 1.0, 1.5)


def installed_figure(pdir):
    """The figure exactly as the installed recipe builds it (fix_family4.main without the save)."""
    fig = ff.rf4.load(Path(pdir) / f"{NAME}.pdf.figpickle")
    ff.label(fig, NAME)
    ff.palette_lib.apply(fig, NAME, check_fit=False)
    ff.layout_lib.fix_texts(fig, NAME)
    return ff.rf4.restyle(fig, NAME)


def extract(fig):
    """Per panel: edges, data (at the bin centres), {generator: values}, {label: colour}; with consistency checks."""
    if len(fig.axes) != 3:
        raise SystemExit(f"expected 3 axes, found {len(fig.axes)}")
    colours, data_colour, out = {}, None, []
    for i, ax in enumerate(fig.axes):
        steps = [p for p in ax.patches if isinstance(p, StepPatch)]
        marks = {l.get_label(): l for l in ax.lines if l.get_label() in GENS}
        if len(steps) != 4 or sorted(marks) != sorted(GENS) or len(ax.containers) != 1:
            raise SystemExit(f"axes {i}: {len(steps)} steps, marker lines {sorted(marks)}, {len(ax.containers)} containers")
        eb = ax.containers[0]
        if eb.get_label() != DATA_LABEL or eb.has_xerr or eb.has_yerr:
            raise SystemExit(f"axes {i}: data container {eb.get_label()!r} xerr {eb.has_xerr} yerr {eb.has_yerr}")
        dline = eb.lines[0]
        dx, dy = np.asarray(dline.get_xdata(), float), np.asarray(dline.get_ydata(), float)
        dup = [l for l in ax.lines if l.get_label() == "_nolegend_"]
        if len(dup) != 1 or not np.array_equal(np.asarray(dup[0].get_ydata(), float), dy):
            raise SystemExit(f"axes {i}: the duplicate data marker line is missing or differs")
        data_colour = dline.get_color() if data_colour is None else data_colour
        edges, gens = None, {}
        for p in steps:
            vals, e = (np.asarray(a, float) for a in p.get_data()[:2])
            ec = tuple(np.round(p.get_edgecolor(), 6))
            hit = [g for g, l in marks.items() if tuple(np.round(l.get_color(), 6)) == ec]
            if len(hit) != 1:
                raise SystemExit(f"axes {i}: a step's colour {ec} matches marker lines {hit}")
            g = hit[0]
            if not np.array_equal(np.asarray(marks[g].get_ydata(), float), vals):
                raise SystemExit(f"axes {i}: {g}'s step values differ from its marker line")
            if edges is None:
                edges = e
            elif not np.array_equal(edges, e):
                raise SystemExit(f"axes {i}: the generators' edges differ")
            gens[g] = vals
            colours[g] = marks[g].get_color()
        if not np.allclose(dx, 0.5 * (edges[:-1] + edges[1:]), rtol=0, atol=1e-12) or len(dy) != len(edges) - 1:
            raise SystemExit(f"axes {i}: the data points are not at the bin centres")
        out.append({"edges": edges, "x": dx, "data": dy, "gens": gens})
    return out, colours, data_colour


def boxes_overlap(a, b):
    return a.x0 < b.x1 and b.x0 < a.x1 and a.y0 < b.y1 and b.y0 < a.y1


def check_texts(fig):
    """Drawn texts: no pair overlaps, all on the canvas; the legend covers no axes."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W, H = fig.bbox.width, fig.bbox.height
    texts, owned = [], []
    for n, ax in enumerate(fig.axes):
        ax.xaxis._update_ticks(); ax.yaxis._update_ticks()   # noqa: SLF001  (drawn ticks only)
        for t in ax.get_xticklabels() + ax.get_yticklabels():
            lo, hi = sorted(ax.get_xlim() if t in ax.get_xticklabels() else ax.get_ylim())
            v = t.get_position()[0 if t in ax.get_xticklabels() else 1]
            if t.get_text() and t.get_visible() and lo - 1e-12 <= v <= hi + 1e-12:
                texts.append((f"tick {t.get_text()}", t.get_window_extent(r)))
                owned.append((n, texts[-1]))
        for t in (ax.xaxis.label, ax.yaxis.label, ax.yaxis.get_offset_text()):
            if t.get_text() and t.get_visible():
                texts.append((t.get_text(), t.get_window_extent(r)))
                owned.append((n, texts[-1]))
    for lg in fig.legends:
        texts.append(("legend", lg.get_window_extent(r)))
    bad = []
    for k, (na, a) in enumerate(texts):
        if a.x0 < -0.5 or a.y0 < -0.5 or a.x1 > W + 0.5 or a.y1 > H + 0.5:
            bad.append(f"off canvas: {na!r} {a}")
        for nb, b in texts[k + 1:]:
            if boxes_overlap(a, b):
                bad.append(f"overlap: {na!r} / {nb!r}")
    for n, (na, a) in owned:          # an axes' texts stay clear of every other axes (gap of at least 2 px)
        for m, ax in enumerate(fig.axes):
            if m != n and boxes_overlap(a.expanded(1.0, 1.0).padded(2.0), ax.get_window_extent(r)):
                bad.append(f"axes {n}'s {na!r} reaches axes {m}")
    for lg in fig.legends:
        lb = lg.get_window_extent(r)
        for i, ax in enumerate(fig.axes):
            if boxes_overlap(lb, ax.get_window_extent(r)):
                bad.append(f"the legend covers axes {i}")
    return bad, len(texts)


def main():
    pdir, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    src = installed_figure(pdir)
    panels, colours, data_colour = extract(src)
    plt.close(src)

    nps.apply()
    fig, axs = plt.subplots(2, 3, figsize=FIGSIZE, sharex="col",
                            gridspec_kw={"height_ratios": [2.4, 1.25], "hspace": 0.07, "wspace": 0.40})
    record = {"figure": NAME, "panels": []}
    drawn, ratios_all = [], []
    for c, (p, (xlab, ylab, expo, xr, xscale)) in enumerate(zip(panels, PANELS)):
        e, x, d = p["edges"], p["x"], p["data"]
        keep = (e[:-1] >= xr[0] - 1e-12) & (e[1:] <= xr[1] + 1e-12)
        k0, k1 = int(np.argmax(keep)), int(len(keep) - np.argmax(keep[::-1]))
        if not keep[k0:k1].all():
            raise SystemExit(f"panel {c}: the drawn bins are not contiguous")
        ek, xk, dk = e[k0:k1 + 1], x[k0:k1], d[k0:k1]
        top, bot = axs[0, c], axs[1, c]
        rec = {"x_label": xlab, "edges_all": e.tolist(), "edges_drawn": ek.tolist(), "x_scale": xscale,
               "omitted_bins": [[float(e[j]), float(e[j + 1])] for j in range(len(keep)) if not keep[j]],
               "data": dk.tolist(), "gens": {}, "ratio": {}}
        art = {}
        for g in GENS:
            y = p["gens"][g][k0:k1]
            r_ = y / dk
            st = top.stairs(y, ek, color=colours[g], lw=GEN_LW, baseline=None, label=g if c == 0 else None)
            rs = bot.stairs(r_, ek, color=colours[g], lw=GEN_LW, baseline=None)
            art[g] = (st, rs, y, r_)
            rec["gens"][g] = y.tolist()
            rec["ratio"][g] = r_.tolist()
            ratios_all.append(r_)
        dp, = top.plot(xk, dk, marker="o", linestyle="None", ms=DATA_MS, color=data_colour, zorder=5,
                       label=DATA_LABEL if c == 0 else None)
        bot.axhline(1.0, color="0.35", lw=0.8, ls="--", zorder=0)
        top.set_ylim(0.0, max(dk.max(), max(v[2].max() for v in art.values())) * 1.12)
        fmt = ScalarFormatter(useMathText=True)
        fmt.set_powerlimits((0, 0))
        top.yaxis.set_major_formatter(fmt)
        top.set_ylabel(ylab)
        bot.set_ylabel("gen. / data")
        bot.set_xlabel(xlab)
        bot.set_xscale(xscale)
        bot.set_xlim(*xr)
        if xscale == "log":
            bot.xaxis.set_major_locator(FixedLocator(LOG_TICKS))
            bot.xaxis.set_major_formatter(ScalarFormatter())
            bot.xaxis.set_minor_locator(NullLocator())
            bot.xaxis.set_minor_formatter(NullFormatter())
        drawn.append((c, art, dp, ek, xk, dk, expo))
        record["panels"].append(rec)
    rv = np.concatenate(ratios_all)
    pad = 0.05 * (max(rv.max(), 1.0) - min(rv.min(), 1.0))
    rlim = (min(rv.min(), 1.0) - pad, max(rv.max(), 1.0) + pad)
    for c in range(3):
        axs[1, c].set_ylim(*rlim)
        axs[1, c].yaxis.set_major_locator(FixedLocator(RATIO_TICKS))
    record["ratio_ylim_shared"] = list(rlim)
    h, l = axs[0, 0].get_legend_handles_labels()
    order = [l.index(DATA_LABEL)] + [l.index(g) for g in GENS]
    fig.legend([h[i] for i in order], [l[i] for i in order], loc="upper center", ncol=5, frameon=False,
               bbox_to_anchor=(0.5, 1.0), handlelength=1.8, columnspacing=1.4)
    fig.subplots_adjust(left=0.085, right=0.99, bottom=0.115, top=0.875, hspace=0.07, wspace=0.40)
    fig.align_ylabels(axs[:, 0]); fig.align_ylabels(axs[:, 1]); fig.align_ylabels(axs[:, 2])

    # ---- identity: the drawn artists hold the source arrays, bitwise
    fig.canvas.draw()
    for c, art, dp, ek, xk, dk, expo in drawn:
        for g, (st, rs, y, r_) in art.items():
            sd, rd = st.get_data(), rs.get_data()
            if not (np.array_equal(sd.values, y) and np.array_equal(sd.edges, ek)
                    and np.array_equal(rd.values, r_) and np.array_equal(rd.edges, ek)
                    and np.array_equal(r_, panels[c]["gens"][g][np.isin(panels[c]["x"], xk)] / dk)):
                raise SystemExit(f"panel {c} {g}: a drawn step or ratio differs from the source")
        if not (np.array_equal(np.asarray(dp.get_xdata(), float), xk) and np.array_equal(np.asarray(dp.get_ydata(), float), dk)):
            raise SystemExit(f"panel {c}: the drawn data points differ from the source")
        off = axs[0, c].yaxis.get_offset_text().get_text()
        m = re.fullmatch(r"\$\\times\\mathdefault\{10\^\{([\u2212-])(\d+)\}\}\\mathdefault\{\}\$", off)
        if not m or -int(m.group(2)) != expo:
            raise SystemExit(f"panel {c}: multiplier {off!r}, expected 10^{expo}")
        record["panels"][c]["multiplier"] = off
    bad, ntext = check_texts(fig)
    if bad:
        raise SystemExit("text check failed:\n  " + "\n  ".join(bad))
    record["text_check"] = f"{ntext} drawn texts: no overlap, all on the canvas, the legend covers no axes"
    record["figsize_in"] = list(FIGSIZE)
    fig.savefig(out / f"{NAME}.pdf")
    fig.savefig(out / f"{NAME}.png", dpi=200)
    plt.close(fig)
    (out / "compose_fig18.json").write_text(json.dumps(record, indent=1) + "\n")
    print(f"[fig18] wrote {out / NAME}.pdf; {record['text_check']}")
    for c, rec in enumerate(record["panels"]):
        print(f"[fig18] panel {c}: {len(rec['edges_drawn']) - 1} bins drawn, omitted {rec['omitted_bins']}, "
              f"multiplier {rec['multiplier']}")
    print(f"[fig18] shared ratio range {rlim[0]:.4f} .. {rlim[1]:.4f}")


if __name__ == "__main__":
    main()
