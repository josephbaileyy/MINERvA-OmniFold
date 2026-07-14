#!/usr/bin/env python3
"""Fig.-6/7-style fractional uncertainty projections for 2D OmniFold.

The MINERvA paper's Figs. 6 and 7 show 1D projected fractional
uncertainties versus p_parallel and p_T.  This script reproduces that
style from the current 2D OmniFold UQ products:

  - per-band universe covariance from analyze_universes.py
  - bootstrap covariance for the statistical component
  - optional ML-seed covariance, included in the total and only drawn when
    it is large enough to be visible

The projection is covariance-exact: C_1D = P C_2D P^T, where P contains
the orthogonal-axis bin widths used to turn d^2sigma/(dpT dpz) into
d sigma/dpT or d sigma/dpz.
"""
from __future__ import annotations
import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)


import argparse
import os
import sys
from collections import OrderedDict
from pathlib import Path

_cache_base = os.environ.get("TMPDIR", "/tmp")
os.environ.setdefault("MPLCONFIGDIR", os.path.join(_cache_base, "mplconfig"))
os.environ.setdefault("XDG_CACHE_HOME", os.path.join(_cache_base, "xdg-cache"))
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)
os.makedirs(os.environ["XDG_CACHE_HOME"], exist_ok=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import ROOT

from analyze_universes import CATEGORY_ORDER, category_for_band


BASE_DIR = Path(__file__).resolve().parents[1]
PT_EDGES = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
                     0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ_EDGES = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
                     6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])

STYLE = {
    "Total": {"color": "black", "linestyle": "-", "linewidth": 2.4},
    "Statistical": {"color": "black", "linestyle": ":", "linewidth": 2.1},
    "Flux": {"color": "#b48cff", "linestyle": "-", "linewidth": 2.0},
    "Models": {"color": "#d62728", "linestyle": "-", "linewidth": 2.0},
    "Normalization": {"color": "#1f77b4", "linestyle": "-", "linewidth": 2.0},
    "Hadronic response": {"color": "#2ca02c", "linestyle": "-", "linewidth": 2.0},
    "Muon reconstruction": {"color": "#f2b21b", "linestyle": "-", "linewidth": 2.0},
    "ML": {"color": "#777777", "linestyle": "--", "linewidth": 1.6},
    "Published total": {"color": "#444444", "linestyle": "-.", "linewidth": 2.0},
}


def die(msg: str) -> None:
    sys.exit(f"[FAIL] {msg}")


def open_root(path: str) -> ROOT.TFile:
    rf = ROOT.TFile.Open(path)
    if not rf or rf.IsZombie():
        die(f"cannot open {path}")
    return rf


def th2_to_array(h) -> np.ndarray:
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    arr = np.zeros((nx, ny), dtype=float)
    for ix in range(nx):
        for iy in range(ny):
            arr[ix, iy] = h.GetBinContent(ix + 1, iy + 1)
    return arr


def cov_hist_to_array(h) -> np.ndarray:
    n = h.GetNbinsX()
    if h.GetNbinsY() != n:
        die(f"{h.GetName()} is not square")
    cov = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            cov[i, j] = h.GetBinContent(i + 1, j + 1)
    return cov


def load_xsec(path: str) -> tuple[np.ndarray, np.ndarray]:
    rf = open_root(path)
    h = rf.Get("hXSec2D")
    if not h:
        die(f"hXSec2D missing in {path}")
    xsec = th2_to_array(h)
    rf.Close()
    if xsec.shape != (len(PT_EDGES) - 1, len(PZ_EDGES) - 1):
        die(f"unexpected hXSec2D shape {xsec.shape}")
    reported = xsec > 0
    if int(reported.sum()) != 205:
        print(f"[WARN] reported-bin mask has {int(reported.sum())} bins, not 205")
    return xsec, reported


def load_named_cov(path: str, hist_name: str) -> np.ndarray:
    rf = open_root(path)
    h = rf.Get(hist_name)
    if not h:
        rf.Close()
        die(f"{hist_name} missing in {path}")
    cov = cov_hist_to_array(h)
    rf.Close()
    return cov


def load_universe_groups(path: str, shape: tuple[int, int]) -> OrderedDict[str, np.ndarray]:
    rf = open_root(path)
    groups = OrderedDict((cat, np.zeros(shape, dtype=float)) for cat in CATEGORY_ORDER)
    n_bands = 0
    for key in rf.GetListOfKeys():
        name = key.GetName()
        if not name.startswith("hCov_universe_"):
            continue
        if name in {"hCov_universe_total"}:
            continue
        band = name[len("hCov_universe_"):]
        h = rf.Get(name)
        cov = cov_hist_to_array(h)
        if cov.shape != shape:
            rf.Close()
            die(f"{name} has shape {cov.shape}, expected {shape}")
        groups[category_for_band(band)] += cov
        n_bands += 1
    rf.Close()
    if n_bands == 0:
        die(f"no hCov_universe_<band> histograms found in {path}")
    return groups


def load_paper_total(paper_root: str, reported: np.ndarray):
    """Published central values on the (pt, pz) grid + TotalCovariance
    restricted to the reported bins, in the same pt-major C order this
    script's projection uses (paper global id = ipt*N_PZ + ipz, cf.
    compare_to_paper_fullcov.flatten_th2d)."""
    n_pt, n_pz = len(PT_EDGES) - 1, len(PZ_EDGES) - 1
    rf = open_root(paper_root)
    h = rf.Get("pt_pl_cross_section")
    tm = rf.Get("TotalCovariance")
    if not h or not tm:
        rf.Close()
        die(f"pt_pl_cross_section / TotalCovariance missing in {paper_root}")
    x_is_pt = h.GetNbinsX() == n_pt
    xsec = np.zeros((n_pt, n_pz), dtype=float)
    for ix in range(1, h.GetNbinsX() + 1):
        for iy in range(1, h.GetNbinsY() + 1):
            ptb, pzb = (ix, iy) if x_is_pt else (iy, ix)
            xsec[ptb - 1, pzb - 1] = h.GetBinContent(ix, iy)
    n = tm.GetNrows()
    if n != n_pt * n_pz:
        rf.Close()
        die(f"paper TotalCovariance is {n}x{n}, expected {n_pt * n_pz}")
    cov = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            cov[i, j] = tm(i, j)
    rf.Close()
    idx = np.flatnonzero(reported.ravel(order="C"))
    return xsec, cov[np.ix_(idx, idx)]


def projection_matrix(axis: str, reported: np.ndarray) -> np.ndarray:
    flat_reported = reported.ravel(order="C")
    n_reported = int(flat_reported.sum())
    if axis == "pt":
        mat = np.zeros((len(PT_EDGES) - 1, n_reported), dtype=float)
    elif axis == "pz":
        mat = np.zeros((len(PZ_EDGES) - 1, n_reported), dtype=float)
    else:
        raise ValueError(axis)

    col = 0
    dpt = np.diff(PT_EDGES)
    dpz = np.diff(PZ_EDGES)
    for ix in range(len(PT_EDGES) - 1):
        for iy in range(len(PZ_EDGES) - 1):
            if not reported[ix, iy]:
                continue
            if axis == "pt":
                mat[ix, col] = dpz[iy]
            else:
                mat[iy, col] = dpt[ix]
            col += 1
    assert col == n_reported
    return mat


def central_projection(xsec: np.ndarray, reported: np.ndarray, axis: str) -> np.ndarray:
    masked = np.where(reported, xsec, 0.0)
    if axis == "pt":
        return np.sum(masked * np.diff(PZ_EDGES)[None, :], axis=1)
    if axis == "pz":
        return np.sum(masked * np.diff(PT_EDGES)[:, None], axis=0)
    raise ValueError(axis)


def fractional_projection(cov: np.ndarray, proj: np.ndarray, central: np.ndarray) -> np.ndarray:
    cov_1d = proj @ cov @ proj.T
    sigma = np.sqrt(np.maximum(np.diag(cov_1d), 0.0))
    with np.errstate(divide="ignore", invalid="ignore"):
        frac = np.where(np.abs(central) > 0, sigma / np.abs(central), 0.0)
    return frac


def draw_one(axis: str, edges: np.ndarray, curves: OrderedDict[str, np.ndarray],
             out_png: str, title: str | None, ymax: float | None) -> None:
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    order = [
        "Total",
        "Published total",
        "Statistical",
        "Flux",
        "Models",
        "Normalization",
        "Hadronic response",
        "Muon reconstruction",
        "ML",
    ]
    for label in order:
        if label not in curves:
            continue
        ax.stairs(curves[label], edges, label=label, **STYLE[label])

    ax.set_xlim(edges[0], edges[-1])
    if ymax is None:
        max_y = max(float(np.nanmax(v)) for v in curves.values())
        ymax = max(0.15, 1.12 * max_y)
    ax.set_ylim(0.0, ymax)
    ax.set_ylabel("Fractional uncertainty")
    if axis == "pt":
        ax.set_xlabel(r"Muon transverse momentum (GeV/c)")
    else:
        ax.set_xlabel(r"Muon longitudinal momentum (GeV/c)")
    if title:
        ax.set_title(title)
    ax.grid(True, alpha=0.25, linewidth=0.7)
    ax.legend(loc="upper center", ncol=3, fontsize=9, frameon=False)
    for spine in ax.spines.values():
        spine.set_linewidth(1.2)
    ax.tick_params(width=1.1)
    technote_style.minerva_tag(ax)
    fig.tight_layout()
    fig.savefig(out_png, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xsec-root",
                        default=str(BASE_DIR / "2d_crossSection_omnifold_MEFHC_5iter.root"))
    parser.add_argument("--universe-root",
                        default=str(BASE_DIR / "uq/universe_stage2_MEFHC_full/uq_universe_covariance_full.root"))
    parser.add_argument("--bootstrap-root",
                        default=str(BASE_DIR / "uq/bootstrap_MEFHC_300/uq_covariance_boot300.root"))
    parser.add_argument("--ml-root",
                        default=str(BASE_DIR / "uq/seedscan_lgbm_ml/uq_covariance_ml.root"))
    parser.add_argument("--out-prefix",
                        default=str(BASE_DIR / "uq/universe_stage2_MEFHC_full/MEFHC_fig6_7_uncertainty"))
    parser.add_argument("--title", default="MEFHC 2D OmniFold uncertainty")
    parser.add_argument("--no-title", action="store_true")
    parser.add_argument("--ymax", type=float, default=None,
                        help="Fixed y-axis upper bound. Default autosizes with a 0.15 floor.")
    parser.add_argument("--paper-root", default="",
                        help="Paper data-release ROOT (cov_ptpl_minerva_inclusive_6GeV.root); "
                             "when given, overlay the published total as a dash-dot line.")
    parser.add_argument("--include-ml", choices=("auto", "always", "never"), default="auto")
    parser.add_argument("--ml-show-threshold", type=float, default=0.002,
                        help="Draw ML in auto mode if max projected fractional uncertainty exceeds this.")
    args = parser.parse_args()

    ROOT.gROOT.SetBatch(True)

    xsec, reported = load_xsec(args.xsec_root)
    n_reported = int(reported.sum())
    shape = (n_reported, n_reported)
    groups = load_universe_groups(args.universe_root, shape)
    groups["Statistical"] += load_named_cov(args.bootstrap_root, "hCov2D_reported")

    ml_cov = None
    if args.include_ml != "never" and args.ml_root:
        if os.path.exists(args.ml_root):
            ml_cov = load_named_cov(args.ml_root, "hCov2D_reported")
            if ml_cov.shape != shape:
                die(f"ML covariance shape {ml_cov.shape}, expected {shape}")
        elif args.include_ml == "always":
            die(f"ML covariance requested but missing: {args.ml_root}")

    total_cov = np.zeros(shape, dtype=float)
    for cov in groups.values():
        total_cov += cov
    if ml_cov is not None:
        total_cov += ml_cov

    os.makedirs(os.path.dirname(args.out_prefix) or ".", exist_ok=True)
    title = None if args.no_title else args.title
    summary_lines = [
        "Fig.-6/7-style fractional uncertainty projections",
        f"xsec_root: {args.xsec_root}",
        f"universe_root: {args.universe_root}",
        f"bootstrap_root: {args.bootstrap_root}",
        f"ml_root: {args.ml_root if ml_cov is not None else '(not used)'}",
        f"n_reported: {n_reported}",
        "",
    ]

    # optional published-total overlay from the paper data release
    paper_xsec = paper_cov = None
    if args.paper_root:
        paper_xsec, paper_cov = load_paper_total(args.paper_root, reported)

    # decide the ML line ONCE across both projections: drawing it in one
    # panel but not its twin reads as an inconsistency, not a threshold
    show_ml = False
    if ml_cov is not None:
        if args.include_ml == "always":
            show_ml = True
        elif args.include_ml == "auto":
            for axis in ("pz", "pt"):
                proj = projection_matrix(axis, reported)
                central = central_projection(xsec, reported, axis)
                if float(np.nanmax(fractional_projection(ml_cov, proj, central))) >= args.ml_show_threshold:
                    show_ml = True
                    break

    for axis, edges, suffix in (("pz", PZ_EDGES, "pz"), ("pt", PT_EDGES, "pt")):
        proj = projection_matrix(axis, reported)
        central = central_projection(xsec, reported, axis)
        curves = OrderedDict()
        curves["Total"] = fractional_projection(total_cov, proj, central)
        if paper_cov is not None:
            curves["Published total"] = fractional_projection(
                paper_cov, proj, central_projection(paper_xsec, reported, axis))
        for cat in CATEGORY_ORDER:
            if np.trace(groups[cat]) > 0:
                curves[cat] = fractional_projection(groups[cat], proj, central)
        if ml_cov is not None and show_ml:
            curves["ML"] = fractional_projection(ml_cov, proj, central)

        out_png = f"{args.out_prefix}_{suffix}.png"
        draw_one(axis, edges, curves, out_png, title, args.ymax)
        print(f"[wrote] {out_png}")

        summary_lines.append(f"{axis} projection:")
        for label, curve in curves.items():
            summary_lines.append(
                f"  {label:22s} median={100*np.median(curve):7.3f}% "
                f"max={100*np.max(curve):7.3f}%"
            )
        if ml_cov is not None and "ML" not in curves:
            ml_curve = fractional_projection(ml_cov, proj, central)
            summary_lines.append(
                f"  {'ML (not drawn)':22s} median={100*np.median(ml_curve):7.3f}% "
                f"max={100*np.max(ml_curve):7.3f}%"
            )
        summary_lines.append("")

    summary_path = f"{args.out_prefix}_summary.txt"
    with open(summary_path, "w") as fh:
        fh.write("\n".join(summary_lines))
        fh.write("\n")
    print(f"[wrote] {summary_path}")


if __name__ == "__main__":
    main()
