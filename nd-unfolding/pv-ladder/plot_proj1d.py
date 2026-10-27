#!/usr/bin/env python3
"""Figures for the PV ladder's post-hoc 1D-projection addendum, from readouts/proj1d.json only.

  proj1d_5d.pdf        L-5D-PV projected to each axis;
  proj1d_ew_direct.pdf L-EW projected to E_avail and W;
  joint_ew_5d.pdf      L-5D-PV on the 39 EW cells, not projected, one column per W bin (summing a column over
                       E_avail gives one W point of proj1d_5d.pdf).
Top rows: the same data unfolded with each vertex's prior (markers, s) against its truth-level departure (lines, d).
Bottom rows: the NuWro closure, (1 + b)(1 + dc) - 1 (markers) against dc (line).
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_HERE = Path(__file__).resolve().parent
VERT = {"genie_mec": ("GENIE+MEC", "#2a78d6", "o"), "nuwro": ("NuWro", "#eb6834", "s"),
        "gibuu": ("GiBUU", "#1baf7a", "^")}
LABEL = {"pt": r"$p_T$ [GeV/c]", "pz": r"$p_\parallel$ [GeV/c]", "eavail": r"$E_\mathrm{avail}$ [GeV]",
         "q3": r"$q_3$ [GeV]", "W": r"$W$ [GeV]"}
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3de"
TOP = "Same data, prior swapped\n(near 0 = data-driven) [%]"
BOTTOM = "NuWro-like data, nominal prior\n(on the line = recovered) [%]"


def style(a, edges):
    n = len(edges) - 1
    a.axhline(0, color=MUTED, lw=1, zorder=1)
    a.set_xticks(np.arange(n + 1))
    a.set_xticklabels([f"{e:g}" for e in edges], rotation=90 if n > 8 else 0, fontsize=8)
    a.set_xlim(0, n)
    a.grid(axis="y", color=GRID, lw=1)
    a.set_axisbelow(True)
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        a.spines[sp].set_color(MUTED)
    a.tick_params(colors=INK)


def draw(top, bottom, ax, sel=slice(None)):
    """One column: ``ax`` is a readout record; ``sel`` picks its bins."""
    pick = lambda x: np.asarray(x, float)[sel]  # noqa: E731
    n = len(pick(ax["x_nominal"]))
    xe, xc = np.arange(n + 1), np.arange(n) + 0.5
    for i, (v, (name, col, mk)) in enumerate(VERT.items()):
        top.stairs(100 * pick(ax["vertices"][v]["d"]), xe, color=col, lw=2, label=f"{name} − nominal, truth level")
        top.plot(xc + (i - 1) * 0.15, 100 * pick(ax["vertices"][v]["s"]), mk, color=col, ms=7, mec="white", mew=1.2,
                 label=f"same data, {name} prior: change in result")
    c = ax["closure_nuwro"]
    dc, b = pick(c["dc"]), pick(c["b"])
    _, col, mk = VERT["nuwro"]
    bottom.stairs(100 * dc, xe, color=col, lw=2, label="NuWro − nominal, truth level")
    bottom.plot(xc, 100 * ((1 + b) * (1 + dc) - 1), mk, color=col, ms=7, mfc="white", mew=2,
                label="NuWro-like pseudo-data, nominal prior: unfolded result − nominal")


def finish(fig, A, title, path):
    A[0, 0].set_ylabel(TOP, color=INK)
    A[1, 0].set_ylabel(BOTTOM, color=INK)
    h0, l0 = A[0, 0].get_legend_handles_labels()
    h1, l1 = A[1, 0].get_legend_handles_labels()
    fig.legend(h0, l0, loc="upper center", ncol=3, frameon=False, fontsize=8.5, bbox_to_anchor=(0.5, 1.0))
    fig.legend(h1, l1, loc="lower center", ncol=2, frameon=False, fontsize=8.5, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle(title, y=1.06, color=INK)
    fig.tight_layout(rect=(0, 0.04, 1, 0.93))
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def projections(J, rung, axes, path, title):
    fig, A = plt.subplots(2, len(axes), figsize=(3.6 * len(axes), 6.4), squeeze=False, sharey="row")
    for j, axis in enumerate(axes):
        draw(A[0, j], A[1, j], J["rungs"][rung][axis])
        for a in A[:, j]:
            style(a, J["edges"][axis])
        A[1, j].set_xlabel(LABEL[axis] + " (bin edges)", color=INK)
    finish(fig, A, title, path)


def joint(J, rung, path, title):
    """The EW cells by W bin; an unsupported cell is left empty."""
    ew = J["rungs"][rung]["EW"]
    nE, nW = len(J["edges"]["eavail"]) - 1, len(J["edges"]["W"]) - 1
    full = {"x_nominal": np.full(nE * nW, np.nan), "vertices": {}, "closure_nuwro": {}}
    cells = np.asarray(ew["cells"])

    def spread(vals):
        g = np.full(nE * nW, np.nan)
        g[cells] = vals
        return g

    full["x_nominal"] = spread(ew["x_nominal"])
    full["vertices"] = {v: {k: spread(ew["vertices"][v][k]) for k in "sd"} for v in VERT}
    full["closure_nuwro"] = {k: spread(ew["closure_nuwro"][k]) for k in ("dc", "b")}
    fig, A = plt.subplots(2, nW, figsize=(3.0 * nW, 6.6), sharey=True)
    We = J["edges"]["W"]
    for j in range(nW):
        draw(A[0, j], A[1, j], full, sel=np.arange(nE) * nW + j)
        for a in A[:, j]:
            style(a, J["edges"]["eavail"])
        A[0, j].set_title(f"W {We[j]:g}–{We[j + 1]:g} GeV", fontsize=10, color=INK)
        A[1, j].set_xlabel(LABEL["eavail"] + " (bin edges)", color=INK)
    finish(fig, A, title, path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--readout", type=Path, default=_HERE / "readouts" / "proj1d.json")
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args(argv)
    J = json.loads(a.readout.read_text())
    a.out_dir.mkdir(parents=True, exist_ok=True)
    projections(J, "L-5D-PV", ["pt", "pz", "eavail", "q3", "W"], a.out_dir / "proj1d_5d.pdf",
                "5D unfolding projected to each variable: lines = generator difference at truth level, "
                "markers = unfolded result")
    projections(J, "L-EW", ["eavail", "W"], a.out_dir / "proj1d_ew_direct.pdf",
                "Direct 2D (E_avail, W) unfolding, projected: lines = truth difference, markers = unfolded result")
    joint(J, "L-5D-PV", a.out_dir / "joint_ew_5d.pdf",
          "5D unfolding, joint (E_avail, W) cells, not projected: one column per W bin "
          "(lines = truth difference, markers = unfolded result)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
