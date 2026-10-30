#!/usr/bin/env python3
"""5D figures (state/measurement-paper/5d-community-20261024/FD-G-FIGURES-DECLARATION.md) for the 5D integration
(DECISION-20261027-joseph-5d-integration-then-second-scope-review.md item 2), drawn only from committed readouts and
the committed H2 definition. No covariance, prediction or data product is opened.

ratio (paper): each prediction's ratio to the data on R00-R15, from Stage G's readout. The default form is
    data/prediction, f/g, with the error bar (f/g) sigma/f, where sigma/f = sqrt(diag(C_total + C_resp))/f (C_resp: the
    adopted extra block, --reported-block-name) is Stage
    G's sigma_total_over_f; --ratio-form prediction-over-data draws g/f = 1 + g_over_f_minus_1 against the data's band
    1 +- sigma/f. GiBUU is drawn on its eight p_parallel < 4.5 cells only, and nothing of it above p_parallel 4.5; by
    default on its own axis under the others' (--gibuu-axis). Each cell's box is printed in a key under the axes.
modes (note): for each 16-cell prediction, the TOP modes of G-DIAG's reported, relative-to-f breakdown, ranked by
    their chi2: each mode's sixteen cell loadings, its relative sigma, its share of the chi2 and the distance along it,
    projection/sigma, in sigma units (whose square is the mode's recorded chi2).
sens (note, optional): the reported chi2 against alpha for G-FOLLOWUP's two families and G-SENS2's three, one panel
    per prediction.

The plot model holds the whole figure: its size, its axes (position, limits, ticks) and one item per drawn artist,
each with its gid, its axes, its style, its values and the readout keys they came from (the sidecar's "plotted").
paint() draws the model and nothing else; control K6 reads the drawn figure back and requires it to be the model:
every value, style, axes and legend handle, no artist without an item, nothing clipped, every text on the page and
no text over another text or over a drawn point. Controls K0-K8 each refuse (exit 1, nothing written). The style is
the article's: publication/release/figs/make_figs.py's style(), COLORS and PDF_META, imported, not copied. Each PDF
has a sidecar JSON with its inputs' sha256, the code's sha256 and the checkout's commit; fd_g_figures_check.py
re-derives every plotted number of a sidecar from the readouts independently.

MEASURES: nothing. The only arithmetic is for display: f/g, (f/g) sigma/f, 1 + g_over_f_minus_1, 1 +- sigma/f and
projection/sigma. CANNOT AUTHORIZE: a caption, a reading, a claim or paper text.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
_REPO = _ND.parent
for _p in (_ND, _REPO / "publication/release/figs"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import fd_g_compare as G  # noqa: E402  (PREDICTIONS, GIBUU_CELLS, C12_LABEL, Stop, report)
import make_figs as MF  # noqa: E402  (the article's style(), COLORS, PDF_META; it selects the Agg backend)
import s1_assemble as sa  # noqa: E402  (sha256, s1.AXES, s1.FINE)

import matplotlib  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.colors import to_hex  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from matplotlib.text import Text  # noqa: E402
from matplotlib.transforms import offset_copy  # noqa: E402

FIGURES = ("ratio", "modes", "sens")
RATIO_FORMS = ("data-over-prediction", "prediction-over-data")
GIBUU_AXES = ("separate", "shared")
INPUTS = ("g_readout", "g_diag_readout", "g_followup_readout", "g_sens2_readout", "f0b_readout", "definition")
PINS = {
    "g_readout": "75a9ddee19a7affe7e3bc10bf0cba8e5ebaa71132686e5ae116f1454d7bafcee",
    "g_diag_readout": "680dc5ef9c40b1ab006657ce020c6acac7e891c68ce36850cf7a7dd2df278d88",
    "g_followup_readout": "cd82517afdfb1dc8383580c8a4c57e82d9b87864e75d28528cb35c4455f6e379",
    "g_sens2_readout": "0f6568aba032e5d9a85f945048494d8fccde3525bb45a1762d6f5d5aaf15b77f",
    "f0b_readout": "b9db935a3187646ba2accaf3865cf4aa26ad72676063c58e7f5e6220224ef17b",
    "definition": "b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89",
}
SCHEMAS = {"g_readout": "fd-g-readout/2", "g_diag_readout": "fd-g-diag-readout/1",
           "g_followup_readout": "fd-g-followup-readout/1", "g_sens2_readout": "fd-g-sens2-readout/1",
           "f0b_readout": "fd-f0b-readout/1", "definition": "h2-definition/1"}
BLOCK = "C_resp"                                # the adopted extra block Stage G names (--reported-block-name)


def reported(name: str = BLOCK) -> str:
    """Stage G's reported matrix with V_g, for the adopted extra block ``name``."""
    return f"C_total + {name} + V_g"


REPORTED = reported()
REPRO = 1e-10                                   # K-controls' relative tolerance between two readouts
EXACT = 1e-12                                   # K6: drawn against model (the same floats, so equal in practice)
ORDER = tuple(p["name"] for p in G.PREDICTIONS)                 # Stage G's order: genie_cv ... mnvtune_v1
SIXTEEN = tuple(p["name"] for p in G.PREDICTIONS if p["cells"] == "all")
TOP = 3                                         # G-DIAG's recorded top modes (its constant "top")
ALPHAS = (0.0, 0.1, 0.25, 0.5, 1.0)
FAMILIES = (("g_followup_readout", "interaction"), ("g_sens2_readout", "flux"), ("g_sens2_readout", "detector"),
            ("g_sens2_readout", "lateral"), ("g_followup_readout", "c_e_systematic"))
SENS_LABEL = "descriptive sensitivity of the reported χ², not an alternative result"
NAME_OF = {"g_followup_readout": "fd_g_followup_readout.json", "g_sens2_readout": "fd_g_sens2_readout.json"}

# --- legend: each prediction's name (the start of Stage G's label), then qualifiers from that label (K7)
SHORT = {"genie_cv": "GENIE 2.12.10 CV, no MEC", "genie_mec": "GENIE 2.12.10 + Valencia MEC", "nuwro": "NuWro 21.09",
         "gibuu": "GiBUU 2019", "mnvtune_v1": "MINERvA Tune v1"}
QUALIFIERS = {"nuwro": (G.C12_LABEL,), "gibuu": (G.C12_LABEL, "p_parallel < 4.5 cells only"),
              "mnvtune_v1": ("prior (not an independent prediction)",)}
# K7: wherever Stage G's label carries one of these, the drawn name carries it too (the director's request item 1)
REQUIRED = (G.C12_LABEL, "prior (not an independent prediction)", "p_parallel < 4.5 cells only")
DISPLAY = (("p_parallel", r"$p_\parallel$"), ("C12", r"$^{12}$C"))  # plain readout text -> drawn text, and back (K7)
COLORS = {"genie_cv": MF.COLORS["GENIE-CV"], "genie_mec": MF.COLORS["GENIE+MEC"], "nuwro": MF.COLORS["NuWro"],
          "gibuu": MF.COLORS["GiBUU"], "mnvtune_v1": "#6b6b6b"}
MARKERS = {"genie_cv": "o", "genie_mec": "s", "nuwro": "^", "gibuu": "D", "mnvtune_v1": "v"}
OFFSET = dict(zip(ORDER, (-0.3, -0.15, 0.0, 0.15, 0.3)))     # each prediction's place inside a cell
FAMILY_STYLE = {"interaction": ("#d62728", "o", "-"), "flux": ("#1f77b4", "s", "-"), "detector": ("#2ca02c", "^", "-"),
                "lateral": ("#ff7f0e", "D", "-"), "c_e_systematic": ("#000000", "v", "--")}
REF = {"color": "#808080", "lw": 0.8, "z": 2}
SEP = {"color": "#bfbfbf", "lw": 0.6, "z": 0}
BAND = "#d9d9d9"
# the key: one row per axis under the ratio axes, each cell's interval on it
KEY_ROWS = ("pt", "pz", "eavail", "q3", "W")
AXIS_TEX = {"pt": r"$p_T$", "pz": r"$p_\parallel$", "eavail": r"$E_{\mathrm{avail}}$", "q3": r"$q_3$", "W": r"$W$"}
AXIS_UNIT = {"pt": "GeV/$c$", "pz": "GeV/$c$", "eavail": "GeV", "q3": "GeV/$c$", "W": "GeV"}
MODES_YLIM = (-1.05, 1.75)                      # loadings are within +-1; the panel's two text lines sit above 1
NAMES = {"ratio": "fd_g_fig_ratio", "modes": "fd_g_fig_modes", "sens": "fd_g_fig_sens"}
LABELS = {"what": "the 5D integration's figures, drawn from committed readouts (FD-G-FIGURES-DECLARATION.md); no new "
                  "statistic",
          "not": "no caption, reading, claim or paper text"}


def report(control, name, ok, why="differs"):
    G.report(control, name, ok, why)


def rel(a, b) -> float:
    """The largest |a - b| / max(|a|, |b|), entries equal counting 0; inf on a shape mismatch or a non-finite entry."""
    a, b = np.atleast_1d(np.asarray(a, float)), np.atleast_1d(np.asarray(b, float))
    if a.shape != b.shape or not (np.all(np.isfinite(a)) and np.all(np.isfinite(b))):
        return float("inf")
    den = np.maximum(np.abs(a), np.abs(b))
    return float(np.max(np.where(a == b, 0.0, np.abs(a - b) / np.where(den > 0, den, 1.0)), initial=0.0))


def display(text: str) -> str:
    for plain, tex in DISPLAY:
        text = text.replace(plain, tex)
    return text


def undisplay(text: str) -> str:
    for plain, tex in DISPLAY:
        text = text.replace(tex, plain)
    return text


def legend_text(name: str) -> str:
    q = QUALIFIERS.get(name, ())
    return display(SHORT[name] + (": " + "; ".join(q) if q else ""))


def cell_index(cells: list[str]) -> list[int]:
    return [int(c[1:]) for c in cells]


# ---------------------------------------------------------------- inputs (K0, K1)


def load(a, pins: dict) -> dict:
    """K0: every input's sha256 is its pin and its schema the declared one."""
    r = {}
    for k in INPUTS:
        path = getattr(a, k)
        got = sa.sha256(path)
        report("K0", f"{k} sha256 is the pin", got == pins[k], f"{got} != {pins[k]}")
        r[k] = json.loads(Path(path).read_text())
        report("K0", f"{k} schema is {SCHEMAS[k]}", r[k].get("schema") == SCHEMAS[k], f"{r[k].get('schema')!r}")
    return r


def check_chain(r: dict, pins: dict, name: str = BLOCK) -> None:
    """K1: the readouts were made from one another and from the same inputs."""
    g, dg, fu, s2, b = (r[k] for k in INPUTS[:5])
    ins = {k: r[k]["inputs_sha256"] for k in INPUTS[:5]}
    report("K1", "G-DIAG, G-FOLLOWUP and G-SENS2 ran on this Stage G readout",
           all(ins[k]["g_readout"] == pins["g_readout"] for k in INPUTS[1:4]))
    report("K1", "G-FOLLOWUP ran on this G-DIAG readout", ins["g_followup_readout"]["g_diag_readout"]
           == pins["g_diag_readout"])
    report("K1", "G-SENS2 ran on, and references, this G-FOLLOWUP readout",
           ins["g_sens2_readout"]["g_followup_readout"] == pins["g_followup_readout"]
           and s2.get("referenced", {}).get("g_followup_readout") == pins["g_followup_readout"])
    report("K1", "every readout ran on this definition", all(ins[k]["definition"] == pins["definition"]
                                                            for k in INPUTS[:5]))
    report("K1", "every readout ran on Stage G's S1 product", all(ins[k]["s1_npz"] == ins["g_readout"]["s1_npz"]
                                                                  for k in INPUTS[:5]))
    xb = g["extra_block"]
    report("K1", f"{name} is adopted, and every readout ran on the same {name}",
           xb["name"] == name and xb["role"] == "adopted" and b["extra_block"]["sha256"] == xb["sha256"]
           and all(ins[k]["extra_block"] == xb["sha256"] for k in INPUTS[1:4]))
    names = [p["name"] for p in g["predictions"]]
    report("K1", "Stage G holds the five predictions in order, with their labels", names == list(ORDER) and all(
        p["label"] == s["label"] and p["sha256"] == s["sha256"] for p, s in zip(g["predictions"], G.PREDICTIONS)))
    report("K1", "every readout ran on the same five predictions", all(
        ins[k][p["name"]] == p["sha256"] for k in INPUTS[1:4] for p in g["predictions"]))
    report("K1", "G-DIAG holds the five predictions in order", [p["name"] for p in dg["predictions"]] == list(ORDER))


# ---------------------------------------------------------------- the cell key (from the definition)


def interval(ax: str, lo: float, hi: float) -> str:
    """A box edge pair as printed: "all" for the axis's full range, "< hi" or "> lo" at one end, else "lo-hi"."""
    a, b = sa.s1.FINE[ax][0], sa.s1.FINE[ax][-1]
    if lo == a and hi == b:
        return "all"
    if lo == a:
        return f"< {hi:g}"
    if hi == b:
        return f"> {lo:g}"
    return f"{lo:g}–{hi:g}"


def cells_key(defn: dict, cells: list[str]) -> list[dict]:
    rc = {f"R{c['id']:02d}": c for c in defn["reporting_cells"] if c.get("reported", True)}
    report("K3", "the definition reports exactly R00-R15", sorted(rc) == sorted(cells) == cells)
    return [{"cell": c, "box": rc[c]["box"], "printed": {ax: interval(ax, *rc[c]["box"][ax]) for ax in sa.s1.AXES}}
            for c in cells]


# ---------------------------------------------------------------- plot models (K2-K5)
#
# The model: figsize, axes [{rect [l, b, w, h] in figure fractions, xlim, ylim, xticks, yticks, off}], legends
# [{id, where (an axes index, or None for the figure), loc, anchor, ncol, title}], and items. Each item has a gid, a
# kind, its source keys, its axes (an index into the model's axes, or None) and its values:
#   line    x, y, style{color, marker, ls}           a series of points, or a curve
#   yerr    x, lo, hi, style{color}                  one vertical segment per point
#   rects   rects [[x0, y0, w, h]], style{color}     the data band
#   bars    x, heights, style{color}                 one mode's loadings
#   ref     orient "h" | "v", value, style           a reference line or a group separator, spanning its axes
#   text    text, at{x, y, coords, dy, ha, va, size, rotation}
#   legend  text, legend (its legend's id), series (the gid of the item its handle shows)
#   ticks   labels, size, rotation                   the axes' x tick labels (shown on no other axes)
#   xlabel, ylabel  text


def item(gid, kind, source, axes, **values) -> dict:
    return {"gid": gid, "kind": kind, "source": source, "axes": axes, **values}


def at(x, y, coords, ha="center", va="center", size=7.0, dy=0.0, rotation=0) -> dict:
    return {"x": x, "y": y, "coords": coords, "dy": dy, "ha": ha, "va": va, "size": size, "rotation": rotation}


def guides(prefix: str, axes: int, n_cells: int, h: float | None) -> list[dict]:
    """The axes' line at h (if any) and its group separators between every four cells."""
    out = [item(f"{prefix}:ref:{axes}", "ref", [], axes, orient="h", value=h, style=REF)] if h is not None else []
    return out + [item(f"{prefix}:sep:{axes}:{j}", "ref", [], axes, orient="v", value=j - 0.5, style=SEP)
                  for j in range(4, n_cells, 4)]


def grid_rects(nr, nc, left, right, bottom, top, hspace, wspace) -> list[list[float]]:
    """GridSpec's axes positions, row by row: hspace and wspace are fractions of the mean axes height and width."""
    w = (right - left) / (nc + (nc - 1) * wspace)
    h = (top - bottom) / (nr + (nr - 1) * hspace)
    return [[left + c * w * (1 + wspace), top - (r + 1) * h - r * h * hspace, w, h] for r in range(nr) for c in range(nc)]


def padded(vals: list[float]) -> list[float]:
    lo, hi = min(vals), max(vals)
    pad = 0.06 * (hi - lo)
    return [float(np.floor((lo - pad) * 20) / 20), float(np.ceil((hi + pad) * 20) / 20)]


def ratio_model(r: dict, form: str, gibuu_axis: str = GIBUU_AXES[0], name: str = BLOCK) -> dict:
    g, b = r["g_readout"], r["f0b_readout"]
    P = {p["name"]: p for p in g["predictions"]}
    cells = list(g["cells"])
    n_cells = len(cells)
    key = cells_key(r["definition"], cells)
    gib = [k["cell"] for k in key if k["box"]["pz"][1] <= 4.5]
    report("K3", "GiBUU's cells are Stage G's p_parallel < 4.5 cells", P["gibuu"]["cells"] == gib ==
           [f"R{c:02d}" for c in G.GIBUU_CELLS])
    report("K3", "every other prediction is on all sixteen cells", all(P[n]["cells"] == cells for n in SIXTEEN))
    ref = P[SIXTEEN[0]]
    f16, s16 = np.array(ref["f"]), np.array(ref["sigma_total_over_f"])
    for n in ORDER:
        p, idx = P[n], cell_index(P[n]["cells"])
        report("K2", f"{n}: f is the same data on its cells", np.array_equal(np.array(p["f"]), f16[idx]))
        report("K2", f"{n}: sigma_total_over_f is the same on its cells",
               np.array_equal(np.array(p["sigma_total_over_f"]), s16[idx]))
        report("K2", f"{n}: the reported covariance is C_total + {name}", p["reported_covariance"] == f"C_total + {name}")
        f, gg = np.array(p["f"]), np.array(p["g"])
        report("K2", f"{n}: f and g are positive", bool(np.all(f > 0) and np.all(gg > 0)))
        report("K2", f"{n}: g/f - 1 is g_over_f_minus_1", rel(gg / f - 1, p["g_over_f_minus_1"]) <= REPRO)
    var, cr = np.array(ref["variant"]["sigma_total_over_f"]), np.array(g["extra_block"]["relative_sigma"])
    report("K2", f"the error bar is C_total + {name}: sigma^2 = sigma(C_total)^2 + sigma({name})^2",
           ref["variant"]["covariance"] == "C_total" and rel(s16 ** 2, var ** 2 + cr ** 2) <= REPRO)
    report("K2", f"F0b's sqrt(diag(C_total + {name}))/f is the same", rel(
        s16, b[f"relative_sigma_plus_{name}"]["C_total"]) <= REPRO and rel(cr, b["extra_block"]["relative_sigma"]) <= REPRO)

    separate = gibuu_axis == "separate"
    axes_of = {n: (1 if separate and n == "gibuu" else 0) for n in ORDER}
    n_axes = 2 if separate else 1
    last = n_axes - 1
    src = "fd_g_readout.json predictions[name={n}]"
    items = []
    for a in range(n_axes):
        items += guides("ratio", a, n_cells, 1.0)
        if form == "prediction-over-data":
            lo, hi = 1.0 - s16, 1.0 + s16
            items.append(item(f"ratio:data:{a}", "rects", [f"{src.format(n=SIXTEEN[0])}.sigma_total_over_f"], a,
                              rects=[[i - 0.45, float(lo[i]), 0.9, float(hi[i] - lo[i])] for i in range(n_cells)],
                              style={"color": BAND}))
        items.append(item(f"ratio:ylabel:{a}", "ylabel", [], a,
                          text="data / prediction" if form == "data-over-prediction" else "prediction / data"))
    for n in ORDER:
        p, a = P[n], axes_of[n]
        x = [i + OFFSET[n] for i in cell_index(p["cells"])]
        style = {"color": COLORS[n], "marker": MARKERS[n], "ls": "None"}
        if form == "data-over-prediction":
            y = np.array(p["f"]) / np.array(p["g"])
            e = y * np.array(p["sigma_total_over_f"])
            items.append(item(f"ratio:{n}", "line", [f"{src.format(n=n)}.f", f"{src.format(n=n)}.g"], a,
                              x=x, y=y.tolist(), cells=p["cells"], style=style))
            items.append(item(f"ratio:{n}:err", "yerr", [f"{src.format(n=n)}.f", f"{src.format(n=n)}.g",
                                                         f"{src.format(n=n)}.sigma_total_over_f"], a,
                              x=x, lo=(y - e).tolist(), hi=(y + e).tolist(), cells=p["cells"],
                              style={"color": COLORS[n]}))
        else:
            y = 1.0 + np.array(p["g_over_f_minus_1"])
            items.append(item(f"ratio:{n}", "line", [f"{src.format(n=n)}.g_over_f_minus_1"], a, x=x, y=y.tolist(),
                              cells=p["cells"], style=style))
        items.append(item(f"ratio:{n}:legend", "legend", [f"{src.format(n=n)}.label"], None, text=legend_text(n),
                          legend="ratio", series=f"ratio:{n}"))
    for row, axn in enumerate(KEY_ROWS):
        dy = -21.0 - 10.5 * row
        items.append(item(f"ratio:keylabel:{axn}", "text", [], last, text=f"{AXIS_TEX[axn]} ({AXIS_UNIT[axn]})",
                          at=at(-0.01, 0.0, "axes", ha="right", size=6.5, dy=dy)))
        for i, k in enumerate(key):
            items.append(item(f"ratio:key:{axn}:{k['cell']}", "text",
                              [f"h2_definition.json reporting_cells[id={i}].box.{axn}"], last,
                              text=k["printed"][axn], at=at(i, 0.0, "xaxis", size=6.0, dy=dy)))
    for j in range(0, n_cells, 4):
        k = key[j]
        report("K3", f"cells {cells[j]}-{cells[j + 3]} share their p_T and p_parallel box",
               all(key[j + m]["box"][ax] == k["box"][ax] for m in range(4) for ax in ("pt", "pz")))
    items.append(item(f"ratio:ticks:{last}", "ticks", [], last, labels=cells, size=6.5, rotation=0))
    if separate:
        rects = [[0.11, 0.53, 0.87, 0.30], [0.11, 0.30, 0.87, 0.17]]
        figsize = [7.0, 5.0]
    else:
        rects = [[0.11, 0.34, 0.87, 0.48]]
        figsize = [7.0, 4.3]
    axes = []
    for a in range(n_axes):
        vals = []
        for it in items:
            if it["axes"] == a and it["kind"] == "line":
                vals += it["y"]
            elif it["axes"] == a and it["kind"] == "yerr":
                vals += it["lo"] + it["hi"]
            elif it["axes"] == a and it["kind"] == "rects":
                vals += [q[1] for q in it["rects"]] + [q[1] + q[3] for q in it["rects"]]
        axes.append({"rect": rects[a], "xlim": [-0.6, n_cells - 0.4], "ylim": padded(vals + [1.0]),
                     "xticks": list(range(n_cells)), "yticks": None, "off": False})
    legends = [{"id": "ratio", "where": None, "loc": "upper center", "anchor": [0.5, 1.0], "ncol": 2, "size": 6.8,
                "title": None}]
    return {"figure": "ratio", "form": form, "gibuu_axis": gibuu_axis, "cells": cells, "key": key,
            "figsize": figsize, "axes": axes, "legends": legends, "items": items}


def mode_text(m: dict) -> tuple[str, str]:
    return (f"mode {m['mode']}: {100 * m['fraction']:.1f}% of $\\chi^2$",
            f"$\\sigma$ = {100 * m['sigma']:.2f}%, distance {m['distance']:+.2f}$\\sigma$")


def modes_model(r: dict, name: str = BLOCK) -> dict:
    g, dg = r["g_readout"], r["g_diag_readout"]
    P = {p["name"]: p for p in g["predictions"]}
    cells = list(g["cells"])
    report("K4", f"G-DIAG recorded its top {TOP} modes", dg["constants"]["top"] == TOP)
    items, panels = [], []
    for i, n in enumerate(SIXTEEN):
        rec = next(p for p in dg["predictions"] if p["name"] == n)
        comp = [c for c in rec["comparisons"] if c["comparison"] == "reported"]
        report("K4", f"{n}: one reported comparison, on {reported(name)}, with Stage G's chi2",
               len(comp) == 1 and comp[0]["matrix"] == reported(name)
               and rel(comp[0]["chi2_stage_g"], P[n]["total"]["chi2"]) <= REPRO and rec["cells"] == cells)
        rt = comp[0]["relative_to_f"]
        top, ranked = rt["top_modes"], rt["modes_by_chi2"]
        for k in range(TOP):
            t, m, a = top[k], ranked[k], i * TOP + k
            report("K4", f"{n} rank {k + 1}: top_modes[{k}] is modes_by_chi2[{k}], with its sigma, chi2 and fraction",
                   sorted(t["loadings"]) == sorted(cells) and t["mode"] == m["mode"]
                   and rel([t["sigma"], t["chi2"], t["fraction"]], [m["sigma"], m["chi2"], m["fraction"]]) <= REPRO)
            report("K4", f"{n} rank {k + 1}: the modes are in descending chi2", k == 0 or ranked[k - 1]["chi2"] >= m["chi2"])
            v = np.array([t["loadings"][c] for c in cells])
            report("K4", f"{n} rank {k + 1}: unit loadings, signed with the largest |loading| positive",
                   abs(float(v @ v) - 1.0) <= REPRO and v[np.argmax(np.abs(v))] > 0)
            dist = m["projection"] / m["sigma"]
            report("K4", f"{n} rank {k + 1}: (projection/sigma)^2 is the mode's chi2", rel(dist ** 2, m["chi2"]) <= REPRO)
            pm = {"prediction": n, "rank": k + 1, "mode": t["mode"], "sigma": m["sigma"], "projection": m["projection"],
                  "distance": dist, "chi2": m["chi2"], "fraction": m["fraction"]}
            panels.append(pm)
            base = f"fd_g_diag_readout.json predictions[name={n}].comparisons[reported].relative_to_f"
            items.append(item(f"modes:{n}:{k + 1}", "bars", [f"{base}.top_modes[{k}].loadings"], a,
                              x=list(range(16)), heights=v.tolist(), style={"color": COLORS[n]}))
            items += guides("modes", a, 16, 0.0)
            for j, txt in enumerate(mode_text(pm)):
                items.append(item(f"modes:{n}:{k + 1}:text{j}", "text",
                                  [f"{base}.modes_by_chi2[{k}].{f}" for f in (("mode", "fraction"),
                                                                             ("sigma", "projection"))[j]], a,
                                  text=txt, at=at(0.02, 0.97 - 0.12 * j, "axes", ha="left", va="top", size=6.3)))
        items.append(item(f"modes:{n}:label", "text", [f"fd_g_readout.json predictions[name={n}].label"], i * TOP,
                          text=legend_text(n), at=at(0.0, 1.0, "axes", ha="left", va="bottom", size=7.0, dy=2.0)))
    for k in range(TOP):
        items.append(item(f"modes:header:{k + 1}", "text", [], k, text=f"rank {k + 1} by $\\chi^2$",
                          at=at(0.5, 1.0, "axes", va="bottom", size=7.5, dy=14.0)))
    items.append(item("modes:ylabel", "text", [], None, text="loading",
                      at=at(0.005, 0.5, "figure", ha="left", size=7.5, rotation=90)))
    rows = len(SIXTEEN)
    for k in range(TOP):
        items.append(item(f"modes:ticks:{(rows - 1) * TOP + k}", "ticks", [], (rows - 1) * TOP + k, labels=cells,
                          size=5.8, rotation=90))
    axes = [{"rect": q, "xlim": [-0.6, 15.6], "ylim": list(MODES_YLIM), "xticks": list(range(16)),
             "yticks": [-1.0, -0.5, 0.0, 0.5, 1.0], "ylabels": j % TOP == 0, "off": False}
            for j, q in enumerate(grid_rects(rows, TOP, 0.07, 0.99, 0.07, 0.93, 0.3, 0.06))]
    return {"figure": "modes", "cells": cells, "panels": panels, "figsize": [7.0, 1.75 * rows + 0.5], "axes": axes,
            "legends": [], "items": items}


def family_text(fam: str, r: dict) -> str:
    groups = (r["g_followup_readout"]["constants"]["families"].get(fam)
              or r["g_sens2_readout"]["constants"]["families"].get(fam))
    return " + ".join(groups) + (" (joint)" if len(groups) > 1 else " alone")


def sens_model(r: dict, name: str = BLOCK) -> dict:
    g = r["g_readout"]
    P = {p["name"]: p for p in g["predictions"]}
    for k in ("g_followup_readout", "g_sens2_readout"):
        s = r[k]["sens"]
        report("K5", f"{k}: the reported matrix and label are G-SENS's", s["reported_matrix"] == reported(name)
               and s["label"] == SENS_LABEL and list(r[k]["constants"]["alphas"]) == list(ALPHAS))
    fams = r["g_sens2_readout"]["referenced"]["families"]
    report("K5", "G-SENS2's referenced families are G-FOLLOWUP's",
           fams == r["g_followup_readout"]["constants"]["families"])
    items, curves, axes = [], [], []
    for a, n in enumerate(ORDER):
        vals = []
        for k, fam in FAMILIES:
            recs = [x for x in r[k]["sens"]["records"] if x["family"] == fam and x["prediction"] == n]
            got = sorted(x["alpha"] for x in recs)
            report("K5", f"{n} {fam}: one record per alpha", got == list(ALPHAS))
            recs.sort(key=lambda x: x["alpha"])
            chi2 = [x["chi2"] for x in recs]
            report("K5", f"{n} {fam}: alpha = 0 is Stage G's reported chi2, with its ndf and label", all(
                x["chi2"] is not None for x in recs) and rel(chi2[0], P[n]["total"]["chi2"]) <= REPRO and all(
                x["ndf"] == P[n]["total"]["ndf"] and x["label"] == SENS_LABEL for x in recs))
            curves.append({"prediction": n, "family": fam, "alphas": list(ALPHAS), "chi2": chi2,
                           "ndf": P[n]["total"]["ndf"]})
            c, mk, ls = FAMILY_STYLE[fam]
            items.append(item(f"sens:{n}:{fam}", "line", [f"{NAME_OF[k]} sens.records[family={fam},prediction={n}]"
                                                          f".alpha,chi2"], a, x=list(ALPHAS), y=chi2,
                              style={"color": c, "marker": mk, "ls": ls}))
            vals += chi2
        items.append(item(f"sens:{n}:label", "text", [f"fd_g_readout.json predictions[name={n}].label"], a,
                          text=legend_text(n).replace(": ", ":\n", 1),
                          at=at(0.0, 1.0, "axes", ha="left", va="bottom", size=6.8, dy=2.0)))
        items.append(item(f"sens:{n}:ndf", "text", [f"fd_g_readout.json predictions[name={n}].total.ndf"], a,
                          text=f"ndf {P[n]['total']['ndf']}",
                          at=at(1.0, 0.0, "axes", ha="right", va="top", size=6.8, dy=-17.0)))
        items.append(item(f"sens:ticks:{a}", "ticks", [], a, labels=[f"{x:g}" for x in ALPHAS], size=6.5,
                          rotation=0))
        items.append(item(f"sens:xlabel:{a}", "xlabel", [], a, text=r"$\alpha$"))
        items.append(item(f"sens:ylabel:{a}", "ylabel", [], a, text=r"$\chi^2$"))
        lo, hi = min(vals), max(vals)
        axes.append({"xlim": [-0.05, 1.05], "ylim": [lo - 0.12 * (hi - lo), hi + 0.12 * (hi - lo)],
                     "xticks": list(ALPHAS), "yticks": None, "off": False})
    axes.append({"xlim": [0.0, 1.0], "ylim": [0.0, 1.0], "xticks": [], "yticks": [], "off": True})
    for q, ax in zip(grid_rects(3, 2, 0.08, 0.99, 0.07, 0.93, 0.62, 0.2), axes):
        ax["rect"] = q
    leg = len(ORDER)
    for k, fam in FAMILIES:
        items.append(item(f"sens:legend:{fam}", "legend", [f"{NAME_OF[k]} constants.families"], None,
                          text=family_text(fam, r), legend="sens", series=f"sens:{ORDER[0]}:{fam}"))
    items.append(item("sens:legend:title", "text", [], None, text="family shrunk"))
    items.append(item("sens:note", "text", [f"{NAME_OF[k]} sens.label" for k in NAME_OF], leg,
                      text=r["g_sens2_readout"]["sens"]["label"].replace(", ", ",\n", 1),
                      at=at(0.5, 0.02, "axes", va="bottom", size=6.5)))
    legends = [{"id": "sens", "where": leg, "loc": "center", "anchor": None, "ncol": 1, "size": 6.8,
                "title": "sens:legend:title"}]
    return {"figure": "sens", "curves": curves, "figsize": [7.0, 6.6], "axes": axes, "legends": legends,
            "items": items}


# ---------------------------------------------------------------- drawing: the model, and nothing else


def by_gid(model: dict) -> dict:
    return {it["gid"]: it for it in model["items"]}


def transform(fig, ax, a: dict):
    base = {"axes": ax.transAxes if ax is not None else None, "figure": fig.transFigure,
            "xaxis": ax.get_xaxis_transform() if ax is not None else None,
            "data": ax.transData if ax is not None else None}[a["coords"]]
    return offset_copy(base, fig=fig, y=a["dy"], units="points") if a["dy"] else base


def paint(model: dict):
    fig = plt.figure(figsize=tuple(model["figsize"]))
    axs = []
    for spec in model["axes"]:
        ax = fig.add_axes(spec["rect"])
        ax.set_xlim(*spec["xlim"])
        ax.set_ylim(*spec["ylim"])
        ax.set_xticks(spec["xticks"])
        if spec["yticks"] is not None:
            ax.set_yticks(spec["yticks"])
        ax.tick_params(labelbottom=False, labelleft=spec.get("ylabels", True))
        if spec["off"]:
            ax.axis("off")
        axs.append(ax)
    I = by_gid(model)
    for it in model["items"]:
        ax = axs[it["axes"]] if it["axes"] is not None else None
        k, st, gid = it["kind"], it.get("style", {}), it["gid"]
        if k == "line":
            ax.plot(it["x"], it["y"], color=st["color"], marker=st["marker"], ls=st["ls"], lw=1.0, ms=3.4, zorder=4,
                    gid=gid)
        elif k == "yerr":
            ax.add_collection(LineCollection([[(x, lo), (x, hi)] for x, lo, hi in zip(it["x"], it["lo"], it["hi"])],
                                             colors=st["color"], linewidths=0.8, zorder=3, gid=gid))
        elif k == "rects":
            for x0, y0, w, h in it["rects"]:
                ax.add_patch(Rectangle((x0, y0), w, h, fc=st["color"], ec="none", zorder=1, gid=gid))
        elif k == "bars":
            for p in ax.bar(it["x"], it["heights"], width=0.75, color=st["color"], zorder=2).patches:
                p.set_gid(gid)
        elif k == "ref":
            (ax.axhline if it["orient"] == "h" else ax.axvline)(it["value"], color=st["color"], lw=st["lw"],
                                                                 zorder=st["z"], gid=gid)
        elif k == "text" and "at" in it:
            a = it["at"]
            (ax if ax is not None else fig).text(a["x"], a["y"], it["text"], transform=transform(fig, ax, a),
                                                 ha=a["ha"], va=a["va"], fontsize=a["size"], rotation=a["rotation"],
                                                 gid=gid)
        elif k == "ticks":
            ax.set_xticks(ax.get_xticks(), it["labels"], fontsize=it["size"], rotation=it["rotation"])
            ax.tick_params(labelbottom=True)
        elif k in ("xlabel", "ylabel"):
            getattr(ax, f"set_{k}")(it["text"])
    for ax, spec in zip(axs, model["axes"]):        # last: setting ticks may widen the view
        ax.set_xlim(*spec["xlim"])
        ax.set_ylim(*spec["ylim"])
    lines = {a.get_gid(): a for ax in axs for a in ax.lines}
    for L in model["legends"]:
        entries = [it for it in model["items"] if it["kind"] == "legend" and it["legend"] == L["id"]]
        host = fig if L["where"] is None else axs[L["where"]]
        kw = {"bbox_to_anchor": tuple(L["anchor"])} if L["anchor"] else {}
        title = I[L["title"]]["text"] if L["title"] else None
        leg = host.legend([lines[e["series"]] for e in entries], [e["text"] for e in entries], loc=L["loc"],
                          ncol=L["ncol"], frameon=False, fontsize=L["size"], handletextpad=0.4, columnspacing=1.2,
                          title=title, title_fontsize=L["size"] + 0.2, **kw)
        for t, e in zip(leg.get_texts(), entries):
            t.set_gid(e["gid"])
        if title:
            leg.get_title().set_gid(L["title"])
    return fig


def draw(name: str, model: dict):
    """The figure, drawn from its model (a module-level lookup, so a planted defect in a test reaches the run)."""
    return paint(model)


# ---------------------------------------------------------------- K6: the drawn figure against the model


def drawn(fig) -> dict:
    """Every artist with a gid, grouped by gid, read back from the figure."""
    out: dict[str, list] = {}
    for a in fig.findobj(lambda o: o.get_gid() is not None):
        out.setdefault(a.get_gid(), []).append(a)
    return out


def legends(fig) -> list:
    return list(fig.legends) + [ax.get_legend() for ax in fig.axes if ax.get_legend() is not None]


def ink(fig) -> list:
    """Every artist that puts ink on the page apart from the axes' frames, ticks and tick labels."""
    out = list(fig.texts)
    for ax in fig.axes:
        out += ax.lines + ax.collections + ax.patches + ax.texts
    for leg in legends(fig):
        out += leg.get_texts() + [leg.get_title()]
    return [a for a in out if a.get_visible() and not (isinstance(a, Text) and a.get_text() == "")]


def same_style(art, style: dict) -> bool:
    if isinstance(art, Line2D):
        return (to_hex(art.get_color()) == to_hex(style["color"]) and art.get_marker() == style["marker"]
                and art.get_linestyle() == {"-": "-", "--": "--", "None": "None", "none": "None"}[style["ls"]])
    if isinstance(art, LineCollection):
        return all(to_hex(c) == to_hex(style["color"]) for c in art.get_colors())
    return to_hex(art.get_facecolor()) == to_hex(style["color"])


def check_values(it: dict, arts: list) -> bool:
    k = it["kind"]
    if k == "line":
        if not (len(arts) == 1 and isinstance(arts[0], Line2D)):
            return False
        xy = np.asarray(arts[0].get_xydata(), float)
        return rel(xy[:, 0], it["x"]) <= EXACT and rel(xy[:, 1], it["y"]) <= EXACT
    if k == "yerr":
        if not (len(arts) == 1 and isinstance(arts[0], LineCollection)):
            return False
        seg = [np.asarray(s, float) for s in arts[0].get_segments()]
        return len(seg) == len(it["x"]) and all(
            s.shape == (2, 2) and s[0, 0] == s[1, 0] == x and rel([s[0, 1], s[1, 1]], [lo, hi]) <= EXACT
            for s, x, lo, hi in zip(seg, it["x"], it["lo"], it["hi"]))
    if k == "rects":
        return all(isinstance(a, Rectangle) for a in arts) and len(arts) == len(it["rects"]) and all(
            rel([a.get_x(), a.get_y(), a.get_width(), a.get_height()], q) <= EXACT for a, q in zip(arts, it["rects"]))
    if k == "bars":
        return all(isinstance(a, Rectangle) for a in arts) and len(arts) == len(it["heights"]) and all(
            rel([a.get_x() + a.get_width() / 2, a.get_y(), a.get_height()], [x, 0.0, h]) <= EXACT
            for a, x, h in zip(arts, it["x"], it["heights"]))
    if k == "ref":
        if not (len(arts) == 1 and isinstance(arts[0], Line2D)):
            return False
        d = arts[0].get_ydata() if it["orient"] == "h" else arts[0].get_xdata()
        return list(map(float, d)) == [it["value"], it["value"]]
    if k in ("text", "legend"):
        return len(arts) == 1 and isinstance(arts[0], Text) and arts[0].get_text() == it["text"]
    return False


def shown_ticks(ax) -> list:
    """The tick labels drawn: visible, non-empty, at a tick inside the view (matplotlib lists others too)."""
    out = []
    for locs, labels, lim in ((ax.get_xticks(), ax.get_xticklabels(), ax.get_xlim()),
                              (ax.get_yticks(), ax.get_yticklabels(), ax.get_ylim())):
        lo, hi = sorted(lim)
        out += [t for x, t in zip(locs, labels) if lo <= x <= hi and t.get_visible() and t.get_text()]
    return out


def overlaps(a, b, tol=0.5) -> bool:
    return min(a.x1, b.x1) - max(a.x0, b.x0) > tol and min(a.y1, b.y1) - max(a.y0, b.y0) > tol


def readback(fig, model: dict) -> None:
    D_ = drawn(fig)
    want = {gid: it for gid, it in by_gid(model).items() if it["kind"] not in ("ticks", "xlabel", "ylabel")}
    name = model["figure"]
    report("K6", f"{name}: the drawn gids are the model's", set(D_) == set(want),
           f"extra {sorted(set(D_) - set(want))[:5]}, missing {sorted(set(want) - set(D_))[:5]}")
    unmodelled = [a for a in ink(fig) if a.get_gid() is None]
    unmodelled += list(fig.lines) + list(fig.patches) + list(fig.images) + list(fig.artists)
    labelled = {(it["axes"], it["kind"]) for it in model["items"] if it["kind"] in ("xlabel", "ylabel")}
    for i, ax in enumerate(fig.axes):
        unmodelled += [f"axes {i} title {t!r}" for t in (ax.get_title(loc) for loc in ("left", "center", "right")) if t]
        unmodelled += [f"axes {i} {k} {getattr(ax, f'get_{k}')()!r}" for k in ("xlabel", "ylabel")
                       if getattr(ax, f"get_{k}")() and (i, k) not in labelled]
    report("K6", f"{name}: every artist with ink is a model item", not unmodelled,
           f"{len(unmodelled)} outside the model, e.g. {unmodelled[:3]}")
    axs = fig.axes
    report("K6", f"{name}: the axes are the model's", len(axs) == len(model["axes"]) and all(
        rel(ax.get_position().bounds, s["rect"]) <= 1e-9 and rel(ax.get_xlim(), s["xlim"]) <= EXACT
        and rel(ax.get_ylim(), s["ylim"]) <= EXACT for ax, s in zip(axs, model["axes"])))
    for gid, it in want.items():
        arts = D_[gid]
        ok = check_values(it, arts)
        if it["kind"] in ("line", "yerr", "rects", "bars", "ref"):
            ok = ok and all(same_style(a, it["style"]) for a in arts if it["kind"] != "ref")
        if it["axes"] is not None:
            ok = ok and all(a.axes is axs[it["axes"]] for a in arts)
        elif it["kind"] == "text" and "at" in it:
            ok = ok and all(a in fig.texts for a in arts)
        report("K6", f"{gid} is drawn as the model holds it (values, style, axes)", ok)
    for it in model["items"]:
        if it["kind"] == "ticks":
            ax = axs[it["axes"]]
            report("K6", f"{it['gid']}: the tick labels are the model's", [t.get_text() for t in
                                                                         ax.get_xticklabels()] == it["labels"])
        elif it["kind"] in ("xlabel", "ylabel"):
            report("K6", f"{it['gid']} is the model's", getattr(axs[it["axes"]], f"get_{it['kind']}")() == it["text"])
    bare = [i for i, ax in enumerate(axs) if ax.axison and not any(it["kind"] == "ticks" and it["axes"] == i
                                                                  for it in model["items"])
            and any(t in shown_ticks(ax) for t in ax.get_xticklabels())]
    report("K6", f"{name}: only the model's axes show x tick labels", not bare, f"axes {bare}")
    for leg in legends(fig):
        for h, t in zip(leg.legend_handles, leg.get_texts()):
            e = want.get(t.get_gid())
            report("K6", f"legend entry {t.get_gid()} shows its own series' handle",
                   e is not None and e["kind"] == "legend" and same_style(h, want[e["series"]]["style"]))
    fig.canvas.draw()
    ren = fig.canvas.get_renderer()
    clipped = []
    for ax in axs:
        x0, x1 = sorted(ax.get_xlim())
        y0, y1 = sorted(ax.get_ylim())
        for a in ax.lines + ax.collections + ax.patches:
            it = want.get(a.get_gid())
            if it is None or it["kind"] == "ref":
                continue
            if isinstance(a, Line2D):
                pts = np.asarray(a.get_xydata(), float)
            elif isinstance(a, LineCollection):
                pts = np.concatenate([np.asarray(s, float) for s in a.get_segments()])
            else:
                pts = np.array([[a.get_x(), a.get_y()], [a.get_x() + a.get_width(), a.get_y() + a.get_height()]])
            if not (np.all(pts[:, 0] >= x0) and np.all(pts[:, 0] <= x1) and np.all(pts[:, 1] >= y0)
                    and np.all(pts[:, 1] <= y1)):
                clipped.append(a.get_gid())
    report("K6", f"{name}: everything drawn lies inside its axes (nothing clipped)", not clipped,
           f"clipped: {sorted(set(clipped))[:5]}")
    page = fig.bbox
    texts = [a for a in ink(fig) if isinstance(a, Text)]
    ticks = [t for ax in axs if ax.axison for t in shown_ticks(ax)]
    ticks += [t for ax in axs if ax.axison for t in (ax.xaxis.label, ax.yaxis.label) if t.get_text()]
    boxes = [(t, t.get_window_extent(ren)) for t in texts + ticks]
    off = [t.get_gid() or t.get_text() for t, bb in boxes if not (
        bb.x0 >= page.x0 - 0.5 and bb.x1 <= page.x1 + 0.5 and bb.y0 >= page.y0 - 0.5 and bb.y1 <= page.y1 + 0.5)]
    report("K6", f"{name}: every text lies on the page", not off, f"off the page: {off[:5]}")
    pairs = [(t.get_gid() or t.get_text(), u.get_gid() or u.get_text())
             for i, (t, bb) in enumerate(boxes) for u, cc in boxes[i + 1:] if overlaps(bb, cc)]
    report("K6", f"{name}: no two texts overlap", not pairs, f"overlapping: {pairs[:5]}")
    data_px = []
    for ax in axs:
        for a in ax.lines:
            it = want.get(a.get_gid())
            if it is not None and it["kind"] == "line":
                data_px += [(it["gid"], p) for p in ax.transData.transform(np.asarray(a.get_xydata(), float))]
        for a in ax.collections:
            if a.get_gid() in want:
                for seg in a.get_segments():
                    data_px += [(a.get_gid(), p) for p in ax.transData.transform(np.asarray(seg, float))]
    bars = [(a.get_gid(), a.get_window_extent(ren)) for ax in axs for a in ax.patches if a.get_gid() in want
            and want[a.get_gid()]["kind"] == "bars"]
    covered = []
    for t, bb in boxes:
        hit = [g for g, q in data_px if bb.x0 <= q[0] <= bb.x1 and bb.y0 <= q[1] <= bb.y1]
        hit += [g for g, b in bars if overlaps(bb, b)]
        if hit:
            covered.append((t.get_gid() or t.get_text(), sorted(set(hit))[:2]))
    report("K6", f"{name}: no text covers a drawn point, bar end or bar", not covered, f"covering: {covered[:5]}")


def check_panels(model: dict) -> None:
    """K6 on the model: each prediction's labels, texts and error bars sit in the axes of its own data, and each
    legend entry names its own series."""
    I = by_gid(model)
    for gid, it in I.items():
        parts = gid.split(":")
        if it["kind"] == "legend":
            want = parts[1] if model["figure"] == "ratio" else parts[2]
            report("K6", f"{gid} names its own series", it["series"].split(":")[-1 if model["figure"] == "sens"
                                                                                   else 1] == want)
            continue
        if len(parts) < 3 or parts[1] not in ORDER:
            continue
        n = parts[1]
        if model["figure"] == "modes":
            data = I[f"modes:{n}:{parts[2]}"] if parts[2].isdigit() else I[f"modes:{n}:1"]
        elif model["figure"] == "sens":
            data = I[f"sens:{n}:{FAMILIES[0][1]}"]
        else:
            data = I[f"ratio:{n}"]
        same = [x["axes"] for x in I.values() if x["kind"] in ("line", "bars") and x["gid"].split(":")[1] == n
                and (model["figure"] != "modes" or x["gid"] == data["gid"])]
        report("K6", f"{gid} sits in its own data's panel", set(same) == {data["axes"]} and it["axes"] == data["axes"])


def check_gibuu(model: dict) -> None:
    """K3 on the model: nothing of GiBUU is drawn at a cell above p_parallel 4.5."""
    if model["figure"] == "ratio":
        for it in model["items"]:
            if it["gid"].startswith("ratio:gibuu") and it["kind"] in ("line", "yerr"):
                report("K3", f"{it['gid']} is on GiBUU's eight cells only, as points", set(it["cells"]) <= set(
                    f"R{c:02d}" for c in G.GIBUU_CELLS) and all(int(round(x - OFFSET["gibuu"])) in G.GIBUU_CELLS
                                                             for x in it["x"])
                       and (it["kind"] == "yerr" or it["style"]["ls"] == "None"))
    if model["figure"] == "modes":
        report("K3", "no GiBUU mode is drawn (16-cell predictions only)",
               not any(it["gid"].startswith("modes:gibuu") for it in model["items"]))


def check_labels(model: dict, r: dict) -> None:
    """K7: every name drawn beside a prediction is the start of Stage G's label for it, and every qualifier drawn
    stands in that label; the five names differ; the sensitivity note is G-SENS's label."""
    P = {p["name"]: p for p in r["g_readout"]["predictions"]}
    report("K7", "the five names differ, and none starts another", all(
        not SHORT[a].startswith(SHORT[b]) for a in ORDER for b in ORDER if a != b))
    for it in model["items"]:
        m = re.fullmatch(r"(?:ratio|modes|sens):([a-z0-9_]+):(?:legend|label)", it["gid"])
        if m:
            n = m.group(1)
            plain = undisplay(it["text"]).replace(":\n", ": ", 1)
            name, _, qual = plain.partition(": ")
            q = QUALIFIERS.get(n, ())
            label = P[n]["label"]
            report("K7", f"{it['gid']} names {n} as Stage G's label does, with its qualifiers",
                   label.startswith(name) and label[len(name):len(name) + 1] in (";", ",", ":", "")
                   and qual == "; ".join(q) and all(x in label for x in q)
                   and all(x in q for x in REQUIRED if x in label))
        if it["gid"] == "sens:note":
            report("K7", "the sensitivity note is G-SENS's label", it["text"].replace(",\n", ", ", 1) == SENS_LABEL)


# ---------------------------------------------------------------- K8 and the outputs


def render(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="pdf", metadata=MF.PDF_META)
    return buf.getvalue()


def check_pdf(name: str, pdf: bytes, again: bytes) -> None:
    report("K8", f"{name}: a PDF with no raster image, its fonts embedded as TrueType",
           pdf.startswith(b"%PDF") and b"/Subtype /Image" not in pdf and b"/FontFile2" in pdf
           and b"/Type3" not in pdf)
    report("K8", f"{name}: drawing it twice gives the same bytes", pdf == again)


def code_record() -> dict:
    files = {"fd_g_figures.py": Path(__file__).resolve(), "make_figs.py": Path(MF.__file__).resolve(),
             "fd_g_compare.py": Path(G.__file__).resolve(), "s1_assemble.py": Path(sa.__file__).resolve(),
             "s5p_stage1_inspect.py": Path(sa.s1.__file__).resolve()}
    rec = {"sha256": {k: sa.sha256(p) for k, p in files.items()}, "commit": None, "clean": None}
    try:
        top = subprocess.run(["git", "-C", str(_ND), "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                             timeout=60)
        if top.returncode == 0:
            root = Path(top.stdout.strip())
            head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True,
                                  timeout=60).stdout.strip()
            st = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--", *map(str, files.values())],
                                capture_output=True, text=True, timeout=60)
            rec.update(commit=head or None, clean=(st.returncode == 0 and st.stdout == ""))
    except (OSError, subprocess.SubprocessError):
        pass
    return rec


def sidecar(name: str, model: dict, pdf: bytes, a, pins: dict, code: dict) -> dict:
    return {"schema": "fd-g-figure-sidecar/1", "labels": LABELS, "figure": name, "file": f"{NAMES[name]}.pdf",
            "pdf_sha256": hashlib.sha256(pdf).hexdigest(), "pdf_bytes": len(pdf),
            "controls_passed": ["K0", "K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8"],
            "inputs_sha256": {k: pins[k] for k in INPUTS}, "code": code,
            "versions": {"python": sys.version.split()[0], "numpy": np.__version__,
                         "matplotlib": matplotlib.__version__},
            "argv": list(sys.argv), "options": {"ratio_form": a.ratio_form, "gibuu_axis": a.gibuu_axis,
                                                **{f"reported_block_{k}": v for k, v in named(a).items()}},
            "plotted": model}


def build_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    for k in INPUTS:
        ap.add_argument("--" + k.replace("_", "-"), dest=k, type=Path, required=True)
    ap.add_argument("--figures", nargs="+", choices=FIGURES, required=True)
    ap.add_argument("--ratio-form", choices=RATIO_FORMS, default=RATIO_FORMS[0])
    ap.add_argument("--gibuu-axis", choices=GIBUU_AXES, default=GIBUU_AXES[0])
    ap.add_argument("--reported-block-name", default=BLOCK,
                    help="the adopted extra block every readout names; default C_resp")
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args(argv)
    if len(set(a.figures)) != len(a.figures):
        ap.error("--figures names a figure twice")
    return a


def named(a) -> dict:
    """The block name as a keyword, only when it is not the default (so the default call is today's). An options
    object without the attribute (a caller from before the option existed) means the default."""
    name = vars(a).get("reported_block_name", BLOCK)
    return {} if name == BLOCK else {"name": name}


MODEL = {"ratio": lambda r, a: ratio_model(r, a.ratio_form, a.gibuu_axis, **named(a)),
         "modes": lambda r, a: modes_model(r, **named(a)), "sens": lambda r, a: sens_model(r, **named(a))}


def run(a, pins=None) -> int:
    pins = PINS if pins is None else pins
    MF.style()
    outs = [a.out_dir / f"{NAMES[n]}{ext}" for n in a.figures for ext in (".pdf", ".json")]
    report("K0", "no output exists (no overwrite)", not any(p.exists() for p in outs),
           ", ".join(str(p) for p in outs if p.exists()))
    r = load(a, pins)
    check_chain(r, pins, **named(a))
    code = code_record()
    done = []
    for n in a.figures:
        model = MODEL[n](r, a)
        check_gibuu(model)
        check_labels(model, r)
        check_panels(model)
        fig = draw(n, model)
        readback(fig, model)
        pdf = render(fig)
        plt.close(fig)
        fig2 = draw(n, model)
        again = render(fig2)
        plt.close(fig2)
        check_pdf(n, pdf, again)
        done.append((n, model, pdf))
        print(f"[FIG] {n}: {len(model['items'])} drawn items, {len(pdf)} bytes", flush=True)
    a.out_dir.mkdir(parents=True, exist_ok=True)
    for n, model, pdf in done:
        meta = json.dumps(sidecar(n, model, pdf, a, pins, code), indent=1, allow_nan=False) + "\n"
        for ext, data in ((".pdf", pdf), (".json", meta.encode())):
            out = a.out_dir / f"{NAMES[n]}{ext}"
            tmp = out.with_name(out.name + ".partial")
            tmp.write_bytes(data)
            os.replace(tmp, out)
            print(json.dumps({"wrote": str(out), "sha256": sa.sha256(out)}), flush=True)
    return 0


def main(argv=None) -> int:
    return run(build_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
