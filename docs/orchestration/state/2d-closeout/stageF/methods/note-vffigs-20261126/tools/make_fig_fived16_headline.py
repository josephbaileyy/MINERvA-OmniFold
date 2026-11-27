#!/usr/bin/env python3
"""The sixteen-cell headline figure (the readability read's addition, approved by Joseph; the director's request of
2026-11-18).

usage: python3 -I make_fig_fived16_headline.py [--out DIR]

Draws each reported cell's integrated cross section f with error bars sqrt(diag) of the REPORTED covariance
C_total + C_resp + C_PL,5D, cells R00-R15 in order, grouped by their four (pT, p_par) quadrants, each cell labeled by
its E_avail / q3 / W box. Every plotted number is read from one committed record, fd_data_product_cpl.json, held to
its sha256; the script refuses any other bytes. After drawing, it reads the numbers back from the figure's own
artists and asserts that they equal the record's (identity check); it writes nothing if any check fails.
Outputs (beside the script unless --out): fived16_headline.pdf (no creation date, so two runs are byte-identical),
fived16_headline.png (preview) and fived16_headline_values.json (every plotted number, the record's path and sha256,
and the checks).

FIGURE PASS COPY (cov2d, 2026-11-19): this file is note-newfigs-20261118/make_fig_fived16_headline.py with only the
explicit font sizes raised so no word prints under 7 pt at \textwidth (quadrant headers and cell names 7.6 pt, the box
table 7.4 pt; they were 7.2, 7.0 and 6.6), the repository root one level higher (it sits in tools/), and its default
output in this record's figs-src/. The originals are immutable MANIFEST rows. Every check is unchanged.

REDRAW COPY (note-figredraw-20261123, 2026-11-23): the figure pass's copy above, with only the drawing changed. It draws
two variants for Joseph to choose from, each from the same arrays (x, f, sig) and checked by the same identity check
(generalized to a cell drawn by any of several errorbar artists, each cell exactly once):
  A  the same box table, with the row headers in words, alternating column shading through the table, thin
     separators between the quadrants (in place of their shading), and light guides from each point down to its column;
  B  the W range as the marker shape and the E_avail range as the marker fill (solid, light tint, open), with a compact
     legend; only the q3 row
     of the table remains.
ROUND 2 (2026-11-23, the outside reviewer's suggestions as Joseph approved them): one figure, from variant A. It keeps
the four quadrant dividers (through the table) and the three cut rows with their word headers; it removes the dotted
stems; in place of the alternating column shading, one light shade (0.93, the installed figure's) on alternating
quadrants (the 1st and 3rd), carried through the table. Variant B is dropped (round 1's copy, with both variants, is
kept in runs/round1-tools/). Outputs: fived16_headline.pdf (no creation date), .png preview,
fived16_headline_data.json (every plotted point per cell) and fived16_headline_values.json (as the original writes it).
ROUND 3 (2026-11-23, two variants for the reviewer to choose from; round 2's copy is in runs/round2-tools/):
  --variant R  round 2 plus the reviewer's second-turn suggestions (ask-codex2/REPLY2.md): log axis 2.5-65 with ticks
               labelled 3, 5, 10, 20, 50; R04 and R14 labelled with their central values (three significant figures
               from the record, asserted "49.0" and "49.6"); the quadrant headers move above the axes so the two
               labelled points stay clear of them.
  --variant D  the reviewer's first-turn redesign (ask-codex2/REPLY1.md): a 2 x 2 grid of horizontal dot-and-whisker
               panels (rows low/high p_T, columns low/high p_par, each headed by its ranges), a shared linear f axis
               0-60 (1e-40 cm^2/nucleon), each row labelled with its region ID and its E_avail, q3 and W cuts on the
               same line, in Table order (top to bottom) within each quadrant.
  ROUND 4 (2026-11-23, polish of the reviewer's choice 9 R, ask-codex2/REPLY3.md; round 3's copy is in runs/round3-tools/):
  --variant P  variant R with the plot area starting 0.2 in further right (L 1.0 -> 1.2 in), so the left-hand cut-row
               labels ("hadronic energy", "momentum transfer", "hadronic mass" and their symbols) end clear of the
               first quadrant's shaded band; asserted after drawing: every row label ends at least 0.06 in left of it.
  All keep the identity check (horizontal bars for D) and write fived16_headline_values.json exactly as before.
V_F COPY (note-vffigs-20261126, 2026-11-26): the round-4 copy above with only its input changed to the C_e^infl (V_F)
data product (V_F option C, readings #1368; make_values_fived16.py READOUTS["dp"] as #1378 pins it): RECORD,
RECORD_SHA256, COV_KEY (the reported matrix C_total + C_resp + C_PL,5D + DeltaC_e) and the schema the record must carry.
The drawing, every check and every output are unchanged.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "docs/analysis-note"))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.ticker  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
import note_palette as pal  # noqa: E402
import note_print_style as nps  # noqa: E402

RECORD = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/with-vf/data-product/fd_data_product_vf.json"
RECORD_SHA256 = "1a37b082"          # the pin make_values_fived16.py READOUTS["dp"] uses for the reported arm (#1378)
COV_KEY = "C_total_plus_C_resp_plus_C_PL5D_plus_DeltaC_e"
UNIT = 1e-40                       # cm^2/nucleon; tab:fived16-cells prints f in this unit (fv@f-unit)
FULL = 100.0                       # an axis range [0, 100] is the whole axis (the H2 grid's open upper edge)


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


ROWS = (("eavail", r"$E_{\mathrm{avail}}$ (GeV)"), ("q3", r"$q_3$ (GeV/$c$)"), ("W", r"$W$ (GeV)"))


def cond(lo, hi):
    """One axis's range as a short table entry: "any" for the whole axis."""
    if lo == 0 and hi == FULL:
        return "any"
    if lo == 0:
        return f"$<${hi:g}"
    if hi == FULL:
        return f"$>${lo:g}"
    return f"{lo:g}–{hi:g}"


def box_label(box):
    return "; ".join(f"{ax} {cond(*box[ax])}" for ax, _ in ROWS)


def main(variant):
    rec = REPO / RECORD
    digest = sha256(rec)
    if not digest.startswith(RECORD_SHA256):
        raise SystemExit(f"REFUSE: {RECORD} has sha256 {digest}, not the pinned {RECORD_SHA256}")
    d = json.loads(rec.read_text())
    assert d["schema"] == "fd-data-product-vf/1" and d["correlation_of"] == COV_KEY
    cells = d["cells"]
    names = [c["cell"] for c in cells]
    assert names == [f"R{i:02d}" for i in range(16)], names
    f = [x / UNIT for x in d["f"]]
    C = d["matrices"][COV_KEY]
    sig = [math.sqrt(C[i][i]) / UNIT for i in range(16)]
    # the record's own relative sigma of the reported covariance agrees with sqrt(diag)/f
    rel = d["relative_sigma"][COV_KEY]
    assert all(abs(sig[i] / f[i] - rel[i]) < 1e-12 for i in range(16))
    # the four (pT, p_par) quadrants, four cells each, in cell order
    quads = []
    for q in range(4):
        boxes = {(tuple(c["box"]["pt"]), tuple(c["box"]["pz"])) for c in cells[4 * q:4 * q + 4]}
        assert len(boxes) == 1, f"cells {4 * q}-{4 * q + 3} do not share one (pT, p_par) box: {boxes}"
        quads.append(boxes.pop())

    nps.apply()
    W_IN = 6.5
    col = pal.style("this_work", linestyle="None")
    return draw(variant, x_of(), f, sig, names, cells, quads, col, W_IN), (names, cells, f, sig, digest)


def x_of():
    gap = 0.7
    return [i + gap * (i // 4) for i in range(16)]


ROW_WORDS = {"eavail": "hadronic energy\n" r"$E_{\mathrm{avail}}$ (GeV)",
             "q3": "momentum transfer\n" r"$q_3$ (GeV/$c$)",
             "W": "hadronic mass\n" r"$W$ (GeV)"}
LABELLED = {"R04": "49.0", "R14": "49.6"}   # ROUND 3 (R): central values printed beside these points (asserted)
LABELLED_P = dict(LABELLED, R07="3.21")      # FINAL (P, Joseph 2026-11-23): also the smallest cell, which the caption names


def sf3(v):
    """v to three significant figures, trailing zeros kept (49.04 -> "49.0")."""
    return f"{v:.{max(0, 2 - math.floor(math.log10(abs(v))))}f}"


def draw(variant, x, f, sig, names, cells, quads, col, W_IN):
    if variant == "D":
        return draw_d(x, f, sig, names, cells, quads, col, W_IN)
    return draw_r(x, f, sig, names, cells, quads, col, W_IN, variant=variant)


ROW_GAP_MIN_IN = 0.06   # ROUND 4 (P): least room between a cut-row label's right end and the shaded band


def draw_r(x, f, sig, names, cells, quads, col, W_IN, variant="R"):
    """Round 2's figure; log axis 2.5-65 with ticks 3, 5, 10, 20, 50; R04 and R14 labelled with their central values;
    the quadrant headers sit above the axes (the 2.5-65 range brings R04/R14 up to where they were drawn inside)."""
    YLIM = (2.5, 65.0)
    H_IN = 4.21
    fig = plt.figure(figsize=(W_IN, H_IN))
    L, R = (1.2 if variant == "P" else 1.0), 0.06
    y0 = 1.05
    top = 0.40                       # room for the two-line quadrant headers above the axes
    ax_h = H_IN - y0 - top
    ax = fig.add_axes([L / W_IN, y0 / H_IN, (W_IN - L - R) / W_IN, ax_h / H_IN])
    ax.set_yscale("log")
    ax.set_ylim(*YLIM)
    ax.set_xlim(x[0] - 0.8, x[-1] + 0.8)
    assert all(f[i] - sig[i] >= YLIM[0] and f[i] + sig[i] <= YLIM[1] for i in range(16)), "a bar is clipped"
    ax.set_yticks([3, 5, 10, 20, 50])
    ax.set_yticklabels(["3", "5", "10", "20", "50"])
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    tr = ax.get_xaxis_transform()
    fy = lambda inch: -inch / ax_h  # noqa: E731  (inches below the axes, as an axes fraction)
    row_y = [fy(0.36 + 0.27 * r) for r in range(len(ROWS))]
    bottom = row_y[-1] - 0.12 / ax_h
    top_frac = 1.0 + (top - 0.01) / ax_h
    for q, ((pt0, pt1), (pz0, pz1)) in enumerate(quads):
        x0, x1 = x[4 * q] - 0.5, x[4 * q + 3] + 0.5
        if q % 2 == 0:   # one light shade on alternating quadrants, through the table and the header band
            s0 = ax.get_xlim()[0] if q == 0 else (x[4 * q - 1] + x[4 * q]) / 2
            s1 = ax.get_xlim()[1] if q == 3 else (x[4 * q + 3] + x[4 * q + 4]) / 2
            ax.add_patch(Rectangle((s0, bottom), s1 - s0, top_frac - bottom, transform=tr, color="0.93", lw=0,
                                   zorder=0, clip_on=False))
        if q > 0:        # quadrant dividers, through the table and the header band
            xs = (x[4 * q - 1] + x[4 * q]) / 2
            ax.plot([xs, xs], [top_frac, bottom], transform=tr, color="0.55", lw=0.6, clip_on=False, zorder=0.5)
        ax.text((x0 + x1) / 2, 1.0 + 0.04 / ax_h, rf"$p_T$ {pt0:g}–{pt1:g}, $p_\parallel$ {pz0:g}–{pz1:g}" +
                "\n(GeV/$c$)", transform=tr, ha="center", va="bottom", fontsize=7.6)
    idx = list(range(16))
    eb = ax.errorbar([x[i] for i in idx], [f[i] for i in idx], yerr=[sig[i] for i in idx], capsize=2.2,
                     elinewidth=0.9, markersize=4.2, **dict(col))
    ebs = [(idx, eb)]
    labels = {}
    for n, want in (LABELLED_P if variant == "P" else LABELLED).items():
        i = names.index(n)
        labels[n] = sf3(f[i])
        assert labels[n] == want, (n, labels[n], want)
        ax.text(x[i] + 0.28, f[i], labels[n], ha="left", va="center", fontsize=7.0)
    top2 = sorted(range(16), key=lambda i: -f[i])[:2]
    assert sorted(names[i] for i in top2) == sorted(LABELLED), "R04, R14 are not the two largest central values"
    assert variant != "P" or names[min(range(16), key=lambda i: f[i])] == "R07", "R07 is not the smallest central value"
    ax.set_ylabel(r"$f$  ($10^{-40}$ cm$^2$/nucleon)")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=7.6)
    ax.tick_params(axis="x", length=0, pad=2)
    row_texts = []
    for (key, title), y in zip(ROWS, row_y):
        row_texts.append(fig.text(0.06 / W_IN, (y0 + y * ax_h) / H_IN, ROW_WORDS[key], ha="left", va="center",
                                  fontsize=7.0, linespacing=1.0))
        for xi, c in zip(x, cells):
            ax.text(xi, y, cond(*c["box"][key]), transform=tr, ha="center", va="center", fontsize=7.0)
    room = None
    if variant == "P":   # ROUND 4: the row labels end clear of the first quadrant's shaded band (the axes' left edge)
        fig.canvas.draw()
        band_x0 = ax.get_window_extent().x0
        room = {t.get_text().split("\n")[0]: (band_x0 - t.get_window_extent().x1) / fig.dpi for t in row_texts}
        assert min(room.values()) >= ROW_GAP_MIN_IN, f"a cut-row label reaches the shaded band: {room}"
    seen = identity(ebs, x, f, sig, horizontal=False)
    data = {"schema": "note-figredraw-fived16-data/3", "variant": variant, "orientation": "vertical",
            "value_labels": labels, **({"row_label_room_in": room} if room else {}),
            "points": [{"cell": names[i], "axes": 0, "x": seen[i][0], "y": seen[i][1], "f": f[i], "sigma": sig[i]}
                       for i in range(16)]}
    return fig, data


def draw_d(x_unused, f, sig, names, cells, quads, col, W_IN):
    """2 x 2 grid of horizontal dot-and-whisker panels: rows low/high p_T, columns low/high p_par; a shared linear
    f axis 0-60; each row: the region ID and its three hadronic cuts on one line, in Table order (top to bottom)."""
    XLIM = (0.0, 60.0)
    assert all(f[i] - sig[i] >= XLIM[0] and f[i] + sig[i] <= XLIM[1] for i in range(16)), "a bar is clipped"
    pts = sorted({q[0] for q in quads})
    pzs = sorted({q[1] for q in quads})
    assert len(pts) == len(pzs) == 2 and sorted(quads) == sorted((p, z) for p in pts for z in pzs)
    LAB_W, PLOT_W, GAP_C, L0 = 1.36, 1.55, 0.30, 0.08
    PH, TOP, ROW_GAP, B0 = 1.02, 0.40, 0.47, 0.56
    H_IN = B0 + 2 * PH + ROW_GAP + TOP
    fig = plt.figure(figsize=(W_IN, H_IN))
    colx = [L0 + LAB_W, L0 + LAB_W + PLOT_W + GAP_C + LAB_W]
    rowy = [B0 + PH + ROW_GAP, B0]
    assert colx[1] + PLOT_W <= W_IN - 0.05
    yrow = [3.0, 2.0, 1.0, 0.0]                         # Table order, top to bottom
    # the cut columns of the row labels (inches left of the plot area) and their headers
    cols = (("cell", 1.30), ("eavail", 0.98), ("q3", 0.62), ("W", 0.28))
    head = {"cell": "", "eavail": r"$E_{\mathrm{avail}}$", "q3": r"$q_3$", "W": r"$W$"}
    ebs, axes = [], []
    for q, (ptb, pzb) in enumerate(quads):
        r, c = pts.index(ptb), pzs.index(pzb)
        ax = fig.add_axes([colx[c] / W_IN, rowy[r] / H_IN, PLOT_W / W_IN, PH / H_IN])
        axes.append(ax)
        ax.set_xlim(*XLIM)
        ax.set_ylim(-0.6, 3.6)
        ax.set_yticks([])
        ax.set_xticks([0, 10, 20, 30, 40, 50, 60])
        ax.tick_params(axis="x", labelsize=7.0, length=2, pad=1.5, labelbottom=(r == 1))
        for xv in (10, 20, 30, 40, 50):
            ax.axvline(xv, color="0.9", lw=0.5, zorder=0)
        idx = list(range(4 * q, 4 * q + 4))
        eb = ax.errorbar([f[i] for i in idx], yrow, xerr=[sig[i] for i in idx], capsize=2.0, elinewidth=0.9,
                         markersize=4.0, **dict(col))
        ebs.append((idx, eb))
        trl = ax.get_yaxis_transform()   # x in axes fraction, y in data
        for i, yv in zip(idx, yrow):
            for key, off in cols:
                txt = names[i] if key == "cell" else cond(*cells[i]["box"][key])
                ax.text(-off / PLOT_W, yv, txt, transform=trl, ha="left", va="center", fontsize=7.0,
                        fontweight="bold" if key == "cell" else "normal")
        for key, off in cols[1:]:
            ax.text(-off / PLOT_W, 3.6, head[key], transform=trl, ha="left", va="bottom", fontsize=7.0, color="0.3")
        ax.text(0.5, 1.0 + 0.03 / PH, rf"$p_T$ {ptb[0]:g}–{ptb[1]:g}, $p_\parallel$ {pzb[0]:g}–{pzb[1]:g} GeV/$c$",
                transform=ax.transAxes, ha="center", va="bottom", fontsize=7.6)
        if r == 1:
            ax.set_xlabel(r"$f$  ($10^{-40}$ cm$^2$/nucleon)", fontsize=7.5, labelpad=1.5)
    fig.text(0.08 / W_IN, 0.03 / H_IN, r"cuts: $E_{\mathrm{avail}}$ and $W$ in GeV, $q_3$ in GeV/$c$; "
             "“any” = the whole axis", ha="left", va="bottom", fontsize=7.0, color="0.3")
    seen = identity(ebs, None, f, sig, horizontal=True)
    data = {"schema": "note-figredraw-fived16-data/3", "variant": "D", "orientation": "horizontal",
            "points": [{"cell": names[i], "axes": fig.axes.index(axes[i // 4]), "y": seen[i][0], "x": seen[i][1],
                        "f": f[i], "sigma": sig[i]} for i in range(16)]}
    return fig, data


def identity(ebs, x, f, sig, horizontal):
    """The figure's identity check: each cell drawn exactly once, at f, with the bar sqrt(diag) centred on f.
    Returns {cell: (position, value, half bar, bar centre)}; position is x (vertical) or y (horizontal)."""
    seen = {}
    for idx, eb in ebs:
        line, bars = eb.lines[0], eb.lines[2]
        xs, ys = list(line.get_xdata()), list(line.get_ydata())
        pos, val = (ys, xs) if horizontal else (xs, ys)
        segs = bars[0].get_segments()
        assert len(xs) == len(idx) == len(segs)
        k = 0 if horizontal else 1
        for i, pv, vv, sg in zip(idx, pos, val, segs):
            assert i not in seen
            seen[i] = (pv, vv, (sg[1][k] - sg[0][k]) / 2, (sg[1][k] + sg[0][k]) / 2)
    assert sorted(seen) == list(range(16)), "a cell is missing or drawn twice"
    assert all(seen[i][1] == f[i] for i in range(16)), "plotted points differ from the record"
    if x is not None:
        assert all(seen[i][0] == x[i] for i in range(16))
    assert all(abs(seen[i][2] - sig[i]) <= 1e-12 * sig[i] for i in range(16)), "plotted bars differ from sqrt(diag)"
    assert all(abs(seen[i][3] - f[i]) <= 1e-12 * f[i] for i in range(16)), "bars are not centred on f"
    return seen


def run():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE.parent / "figs-src")
    ap.add_argument("--variant", choices=("R", "D", "P"), required=True)
    a = ap.parse_args()
    (fig, data), (names, cells, f, sig, digest) = main(a.variant)
    a.out.mkdir(parents=True, exist_ok=True)
    fig.savefig(a.out / "fived16_headline.pdf", metadata={"CreationDate": None})
    fig.savefig(a.out / "fived16_headline.png", dpi=200)
    (a.out / "fived16_headline_data.json").write_text(json.dumps(data, indent=1) + "\n")
    vals = {
        "schema": "note-newfigs-fived16-headline/1",
        "record": {"path": RECORD, "bytes_digest_sha256": digest, "covariance": COV_KEY},
        "unit": "1e-40 cm^2/nucleon (the cell-integrated cross section f, as tab:fived16-cells)",
        "cells": [{"cell": n, "box": c["box"], "label": box_label(c["box"]), "f": fv, "sigma_reported": s,
                   "relative_sigma_reported": s / fv} for n, c, fv, s in zip(names, cells, f, sig)],
        "checks": {"record_sha256_pinned": True, "relative_sigma_equals_record": True,
                   "plotted_points_equal_record_f": True, "plotted_bars_equal_sqrt_diag": True,
                   "quadrants_share_one_pt_pz_box": True},
    }
    (a.out / "fived16_headline_values.json").write_text(json.dumps(vals, indent=1) + "\n")
    print("wrote", a.out / "fived16_headline.pdf", "; record", digest[:8])


if __name__ == "__main__":
    run()
