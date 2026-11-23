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
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE.parent / "figs-src")
    a = ap.parse_args()
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
    fig, ax = plt.subplots(figsize=nps.figsize(1.0, 0.50))
    gap = 0.7
    x = [i + gap * (i // 4) for i in range(16)]
    for q, ((pt0, pt1), (pz0, pz1)) in enumerate(quads):
        x0, x1 = x[4 * q] - 0.5, x[4 * q + 3] + 0.5
        if q % 2 == 0:
            ax.axvspan(x0, x1, color="0.93", lw=0, zorder=0)
        ax.text((x0 + x1) / 2, 0.985, rf"$p_T$ {pt0:g}–{pt1:g}, $p_\parallel$ {pz0:g}–{pz1:g}" + "\n(GeV/$c$)",
                transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=7.6)
    eb = ax.errorbar(x, f, yerr=sig, capsize=2.2, elinewidth=0.9, markersize=4.2,
                     **pal.style("this_work", linestyle="None"))
    ax.set_yscale("log")
    ax.set_ylim(1.5, 160)
    ax.set_xlim(x[0] - 0.8, x[-1] + 0.8)
    ax.set_ylabel(r"$f$  ($10^{-40}$ cm$^2$/nucleon)")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=7.6)
    ax.tick_params(axis="x", length=0, pad=2)
    tr = ax.get_xaxis_transform()
    for r, (key, title) in enumerate(ROWS):
        y = -0.115 - 0.075 * r
        ax.text(x[0] - 0.9, y, title, transform=tr, ha="right", va="center", fontsize=7.4)
        for xi, c in zip(x, cells):
            ax.text(xi, y, cond(*c["box"][key]), transform=tr, ha="center", va="center", fontsize=7.4)
    fig.tight_layout(pad=0.3)

    # identity check: the numbers the figure holds equal the record's
    line, caps, bars = eb.lines[0], eb.lines[1], eb.lines[2]
    xs, ys = list(line.get_xdata()), list(line.get_ydata())
    segs = bars[0].get_segments()
    half = [(s[1][1] - s[0][1]) / 2 for s in segs]
    mid = [(s[1][1] + s[0][1]) / 2 for s in segs]
    assert xs == x and ys == f, "plotted points differ from the record"
    assert all(abs(h - s) <= 1e-12 * s for h, s in zip(half, sig)), "plotted bars differ from sqrt(diag)"
    assert all(abs(m - v) <= 1e-12 * v for m, v in zip(mid, f)), "bars are not centred on f"

    a.out.mkdir(parents=True, exist_ok=True)
    fig.savefig(a.out / "fived16_headline.pdf", metadata={"CreationDate": None})
    fig.savefig(a.out / "fived16_headline.png", dpi=200)
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
    main()
