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
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
import note_palette as pal  # noqa: E402
import note_print_style as nps  # noqa: E402

RECORD = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/with-cpl/data-product/fd_data_product_cpl.json"
RECORD_SHA256 = "d6752d2c"          # the pin make_values_fived16.py READOUTS["dp"] uses for the reported arm
COV_KEY = "C_total_plus_C_resp_plus_C_PL5D"
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


def main():
    rec = REPO / RECORD
    digest = sha256(rec)
    if not digest.startswith(RECORD_SHA256):
        raise SystemExit(f"REFUSE: {RECORD} has sha256 {digest}, not the pinned {RECORD_SHA256}")
    d = json.loads(rec.read_text())
    assert d["schema"] == "fd-data-product-cpl/1" and d["correlation_of"] == COV_KEY
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
    return draw(x_of(), f, sig, names, cells, quads, col, W_IN), (names, cells, f, sig, digest)


def x_of():
    gap = 0.7
    return [i + gap * (i // 4) for i in range(16)]


ROW_WORDS = {"eavail": "hadronic energy\n" r"$E_{\mathrm{avail}}$ (GeV)",
             "q3": "momentum transfer\n" r"$q_3$ (GeV/$c$)",
             "W": "hadronic mass\n" r"$W$ (GeV)"}
def draw(x, f, sig, names, cells, quads, col, W_IN):
    H_IN = 3.95
    fig = plt.figure(figsize=(W_IN, H_IN))
    L, R = 1.0, 0.06
    y0 = 1.05
    ax_h = H_IN - y0 - 0.06
    ax = fig.add_axes([L / W_IN, y0 / H_IN, (W_IN - L - R) / W_IN, ax_h / H_IN])
    ax.set_yscale("log")
    ax.set_ylim(1.5, 160)
    ax.set_xlim(x[0] - 0.8, x[-1] + 0.8)
    tr = ax.get_xaxis_transform()
    fy = lambda inch: -inch / ax_h  # noqa: E731  (inches below the axes, as an axes fraction)
    row_y = [fy(0.36 + 0.27 * r) for r in range(len(ROWS))]
    bottom = row_y[-1] - 0.12 / ax_h
    for q, ((pt0, pt1), (pz0, pz1)) in enumerate(quads):
        x0, x1 = x[4 * q] - 0.5, x[4 * q + 3] + 0.5
        if q % 2 == 0:   # one light shade on alternating quadrants, through the table, out to the dividers / axis edge
            s0 = ax.get_xlim()[0] if q == 0 else (x[4 * q - 1] + x[4 * q]) / 2
            s1 = ax.get_xlim()[1] if q == 3 else (x[4 * q + 3] + x[4 * q + 4]) / 2
            ax.add_patch(Rectangle((s0, bottom), s1 - s0, 1.0 - bottom, transform=tr, color="0.93", lw=0, zorder=0,
                                   clip_on=False))
        if q > 0:        # quadrant dividers, through the table
            xs = (x[4 * q - 1] + x[4 * q]) / 2
            ax.plot([xs, xs], [1.0, bottom], transform=tr, color="0.55", lw=0.6, clip_on=False, zorder=0.5)
        ax.text((x0 + x1) / 2, 0.985, rf"$p_T$ {pt0:g}–{pt1:g}, $p_\parallel$ {pz0:g}–{pz1:g}" + "\n(GeV/$c$)",
                transform=tr, ha="center", va="top", fontsize=7.6)
    idx = list(range(16))
    eb = ax.errorbar([x[i] for i in idx], [f[i] for i in idx], yerr=[sig[i] for i in idx], capsize=2.2,
                     elinewidth=0.9, markersize=4.2, **dict(col))
    ebs = [(idx, eb)]
    ax.set_ylabel(r"$f$  ($10^{-40}$ cm$^2$/nucleon)")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=7.6)
    ax.tick_params(axis="x", length=0, pad=2)
    for (key, title), y in zip(ROWS, row_y):
        fig.text(0.06 / W_IN, (y0 + y * ax_h) / H_IN, ROW_WORDS[key], ha="left", va="center", fontsize=7.0,
                 linespacing=1.0)
        for xi, c in zip(x, cells):
            ax.text(xi, y, cond(*c["box"][key]), transform=tr, ha="center", va="center", fontsize=7.0)

    # identity check: the numbers the figure holds equal the record's (each cell exactly once over the artists)
    seen = {}
    for idx, eb in ebs:
        line, bars = eb.lines[0], eb.lines[2]
        xs, ys = list(line.get_xdata()), list(line.get_ydata())
        segs = bars[0].get_segments()
        assert len(xs) == len(idx) == len(segs)
        for i, xv, yv, sg in zip(idx, xs, ys, segs):
            assert i not in seen
            seen[i] = (xv, yv, (sg[1][1] - sg[0][1]) / 2, (sg[1][1] + sg[0][1]) / 2)
    assert sorted(seen) == list(range(16)), "a cell is missing or drawn twice"
    assert all(seen[i][0] == x[i] and seen[i][1] == f[i] for i in range(16)), "plotted points differ from the record"
    assert all(abs(seen[i][2] - sig[i]) <= 1e-12 * sig[i] for i in range(16)), "plotted bars differ from sqrt(diag)"
    assert all(abs(seen[i][3] - f[i]) <= 1e-12 * f[i] for i in range(16)), "bars are not centred on f"
    data = {"schema": "note-figredraw-fived16-data/2",
            "points": [{"cell": names[i], "x": seen[i][0], "f": f[i], "sigma": sig[i]} for i in range(16)]}
    return fig, data


def run():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE.parent / "figs-src")
    a = ap.parse_args()
    (fig, data), (names, cells, f, sig, digest) = main()
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
