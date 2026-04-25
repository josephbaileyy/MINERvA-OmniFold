#!/usr/bin/env python3
"""
Read-only MINOS/range-out acceptance diagnostics for 2D OmniFold inputs.

This script does not correct the unfolding and does not write ROOT outputs. It
summarizes how the patched signal MC maps truth-selected events into reco-passing
events versus p_parallel, with extra visibility into signal fakes.
"""

import argparse
import json
import math
import os
import tempfile
from array import array
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR",
                      os.path.join(tempfile.gettempdir(), "minerva101-mplconfig"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)

try:
    from unfold_2d_omnifold_unbinned import PT_EDGES, PZ_EDGES, get_pot_scales
except ImportError as exc:
    raise RuntimeError(
        "Could not import PT_EDGES/PZ_EDGES from "
        "Documents/unfold_2d_omnifold_unbinned.py. Run this script from the "
        "repository root or keep the unfolding script importable."
    ) from exc


DEFAULT_INPUT = "Documents/runEventLoopOmniFold_1A_minos_fix.root"
DEFAULT_PREFIX = "Documents/minos_acceptance_1A"
PT_LABEL = r"$p_T$ (GeV/c)"
PZ_LABEL = r"$p_{\parallel}$ (GeV/c)"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Diagnose MINOS/range-out acceptance in 2D OmniFold inputs."
    )
    parser.add_argument("--input", default=DEFAULT_INPUT,
                        help=f"Input runEventLoopOmniFold ROOT file "
                             f"(default: {DEFAULT_INPUT})")
    parser.add_argument("--out-prefix", default=DEFAULT_PREFIX,
                        help=f"Output filename prefix (default: {DEFAULT_PREFIX})")
    return parser.parse_args()


def finite_weight(value, limit=1e4):
    return math.isfinite(value) and 0.0 <= value < limit


def safe_divide(num, den):
    out = np.zeros_like(num, dtype=float)
    np.divide(num, den, out=out, where=den > 0.0)
    return out


def centers(edges):
    edges = np.asarray(edges, dtype=float)
    return 0.5 * (edges[:-1] + edges[1:])


def widths(edges):
    edges = np.asarray(edges, dtype=float)
    return edges[1:] - edges[:-1]


def edge_pairs(edges):
    return [[float(lo), float(hi)] for lo, hi in zip(edges[:-1], edges[1:])]


def load_signal_diagnostics(t_sig, pot_scale):
    pt_edges = np.asarray(PT_EDGES, dtype=float)
    pz_edges = np.asarray(PZ_EDGES, dtype=float)
    pt_lo, pt_hi = float(pt_edges[0]), float(pt_edges[-1])
    pz_lo, pz_hi = float(pz_edges[0]), float(pz_edges[-1])

    mc_pt = array("d", [0.0])
    mc_pz = array("d", [0.0])
    sim_pt = array("d", [0.0])
    sim_pz = array("d", [0.0])
    sim_pass = array("B", [0])
    w_truth = array("d", [1.0])
    w_reco = array("d", [1.0])

    t_sig.SetBranchAddress("MC", mc_pt)
    t_sig.SetBranchAddress("MC_pz", mc_pz)
    t_sig.SetBranchAddress("sim", sim_pt)
    t_sig.SetBranchAddress("sim_pz", sim_pz)
    t_sig.SetBranchAddress("sim_pass", sim_pass)
    t_sig.SetBranchAddress("w_truth", w_truth)
    t_sig.SetBranchAddress("w_reco", w_reco)

    truth_den = np.zeros((len(PT_EDGES) - 1, len(PZ_EDGES) - 1), dtype=float)
    reco_num = np.zeros_like(truth_den)
    fake_reco = np.zeros_like(truth_den)

    counts = {
        "entries": int(t_sig.GetEntries()),
        "truth_in_range": 0,
        "reco_in_range": 0,
        "truth_and_reco_in_range": 0,
        "fakes_reco_in_truth_out": 0,
        "bad_weight": 0,
        "outside_truth_and_reco_range": 0,
    }

    for i in range(t_sig.GetEntries()):
        t_sig.GetEntry(i)
        tru_pt = float(mc_pt[0])
        tru_pz = float(mc_pz[0])
        rec_pt = float(sim_pt[0])
        rec_pz = float(sim_pz[0])
        wt = float(w_truth[0])
        wr = float(w_reco[0])

        if not (finite_weight(wt) and finite_weight(wr)):
            counts["bad_weight"] += 1
            continue

        truth_in = (math.isfinite(tru_pt) and math.isfinite(tru_pz) and
                    pt_lo <= tru_pt <= pt_hi and pz_lo <= tru_pz <= pz_hi)
        reco_in = (sim_pass[0] != 0 and
                   math.isfinite(rec_pt) and math.isfinite(rec_pz) and
                   pt_lo <= rec_pt <= pt_hi and pz_lo <= rec_pz <= pz_hi)

        if truth_in:
            ix = np.searchsorted(pt_edges, tru_pt, side="right") - 1
            iy = np.searchsorted(pz_edges, tru_pz, side="right") - 1
            ix = min(ix, truth_den.shape[0] - 1)
            iy = min(iy, truth_den.shape[1] - 1)
            truth_den[ix, iy] += wt * pot_scale
            counts["truth_in_range"] += 1
            if reco_in:
                reco_num[ix, iy] += wr * pot_scale
                counts["truth_and_reco_in_range"] += 1

        if reco_in:
            counts["reco_in_range"] += 1
            if not truth_in:
                ix = np.searchsorted(pt_edges, rec_pt, side="right") - 1
                iy = np.searchsorted(pz_edges, rec_pz, side="right") - 1
                ix = min(ix, fake_reco.shape[0] - 1)
                iy = min(iy, fake_reco.shape[1] - 1)
                fake_reco[ix, iy] += wr * pot_scale
                counts["fakes_reco_in_truth_out"] += 1

        if not truth_in and not reco_in:
            counts["outside_truth_and_reco_range"] += 1

    return truth_den, reco_num, fake_reco, counts


def build_strip_summary(truth_den, reco_num, fake_reco):
    den_pz = truth_den.sum(axis=0)
    num_pz = reco_num.sum(axis=0)
    fake_pz = fake_reco.sum(axis=0)
    eff_pz = safe_divide(num_pz, den_pz)
    fake_frac = safe_divide(fake_pz, num_pz + fake_pz)

    strips = []
    for i, (lo, hi) in enumerate(zip(PZ_EDGES[:-1], PZ_EDGES[1:])):
        strips.append({
            "pz_low": float(lo),
            "pz_high": float(hi),
            "truth_weighted": float(den_pz[i]),
            "reco_passing_weighted_by_truth_bin": float(num_pz[i]),
            "efficiency": float(eff_pz[i]),
            "fake_weighted_by_reco_bin": float(fake_pz[i]),
            "fake_fraction_of_reco_plus_fake": float(fake_frac[i]),
        })
    return strips, den_pz, num_pz, fake_pz, eff_pz


def plot_eff_vs_pz(path, den_pz, num_pz, eff_pz):
    pz_centers = centers(PZ_EDGES)
    pz_widths = widths(PZ_EDGES)

    fig, ax1 = plt.subplots(figsize=(8.5, 5.0))
    ax1.errorbar(pz_centers, eff_pz, xerr=pz_widths / 2.0, fmt="o-",
                 color="#1f77b4", lw=1.6, ms=4, capsize=2)
    ax1.set_xlabel(PZ_LABEL)
    ax1.set_ylabel("Reco-passing / truth weighted efficiency")
    ax1.set_ylim(0.0, min(1.15, max(1.0, float(np.nanmax(eff_pz)) * 1.15)))
    ax1.grid(True, alpha=0.25)

    ax2 = ax1.twinx()
    ax2.step(PZ_EDGES[:-1], den_pz, where="post", color="#777777",
             alpha=0.45, label="truth")
    ax2.step(PZ_EDGES[:-1], num_pz, where="post", color="#d62728",
             alpha=0.45, label="reco pass")
    ax2.set_ylabel("POT-scaled weighted yield")
    ax2.legend(loc="lower right", frameon=False)

    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_eff_2d(path, eff_2d):
    fig, ax = plt.subplots(figsize=(8.0, 5.8))
    mesh = ax.pcolormesh(PZ_EDGES, PT_EDGES, eff_2d, vmin=0.0, vmax=1.0,
                         cmap="viridis", shading="flat")
    ax.set_xlabel(PZ_LABEL)
    ax.set_ylabel(PT_LABEL)
    ax.set_title("Reco-passing efficiency by truth bin")
    cbar = fig.colorbar(mesh, ax=ax)
    cbar.set_label("efficiency")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_fake_vs_pz(path, fake_pz):
    pz_centers = centers(PZ_EDGES)
    pz_widths = widths(PZ_EDGES)

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(pz_centers, fake_pz, width=pz_widths, align="center",
           color="#ff7f0e", edgecolor="black", linewidth=0.5)
    ax.set_xlabel(PZ_LABEL)
    ax.set_ylabel("POT-scaled fake yield")
    ax.set_title("Signal fakes: reco in range, truth out of range")
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_ratio_vs_pz(path, den_pz, num_pz):
    ratio = safe_divide(num_pz, den_pz)
    pz_centers = centers(PZ_EDGES)
    pz_widths = widths(PZ_EDGES)

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.axhline(1.0, color="#555555", lw=1.0, ls="--")
    ax.errorbar(pz_centers, ratio, xerr=pz_widths / 2.0, fmt="s-",
                color="#2ca02c", lw=1.6, ms=4, capsize=2)
    ax.set_xlabel(PZ_LABEL)
    ax.set_ylabel("Reco-passing / truth strip ratio")
    ax.set_ylim(0.0, min(1.15, max(1.0, float(np.nanmax(ratio)) * 1.15)))
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main():
    args = parse_args()
    input_path = Path(args.input)
    out_prefix = Path(args.out_prefix)
    out_prefix.parent.mkdir(parents=True, exist_ok=True)

    f_in = ROOT.TFile.Open(str(input_path), "READ")
    if not f_in or f_in.IsZombie():
        raise RuntimeError(f"Could not open input ROOT file: {input_path}")

    try:
        data_pot, mc_pot, pot_scale = get_pot_scales(f_in)
        t_sig = f_in.Get("mc_signal_reco")
        if not t_sig:
            raise RuntimeError(f"Missing mc_signal_reco in {input_path}")

        truth_den, reco_num, fake_reco, counts = load_signal_diagnostics(
            t_sig, pot_scale)
    finally:
        f_in.Close()

    eff_2d = safe_divide(reco_num, truth_den)
    strips, den_pz, num_pz, fake_pz, eff_pz = build_strip_summary(
        truth_den, reco_num, fake_reco)

    outputs = {
        "summary_json": f"{out_prefix}_summary.json",
        "eff_vs_pz_png": f"{out_prefix}_eff_vs_pz.png",
        "eff_2d_png": f"{out_prefix}_eff_2d.png",
        "fake_vs_pz_png": f"{out_prefix}_fake_vs_pz.png",
        "reco_truth_ratio_vs_pz_png": f"{out_prefix}_reco_truth_ratio_vs_pz.png",
    }

    summary = {
        "warning": (
            "Diagnostic only: this quantifies MINOS/range-out acceptance "
            "behavior and is not an unfolding correction."
        ),
        "input": str(input_path),
        "pot": {
            "dataPOTUsed": data_pot,
            "mcPOTUsed": mc_pot,
            "potScale": pot_scale,
        },
        "phase_space": {
            "pt": [float(PT_EDGES[0]), float(PT_EDGES[-1])],
            "pz": [float(PZ_EDGES[0]), float(PZ_EDGES[-1])],
            "truth_in_range": "0 <= MC <= 4.5 and 1.5 <= MC_pz <= 60",
            "reco_in_range": (
                "sim_pass && 0 <= sim <= 4.5 and 1.5 <= sim_pz <= 60"
            ),
        },
        "bin_edges": {
            "pt": [float(x) for x in PT_EDGES],
            "pz": [float(x) for x in PZ_EDGES],
        },
        "counts": counts,
        "totals": {
            "truth_weighted": float(truth_den.sum()),
            "reco_passing_weighted_by_truth_bin": float(reco_num.sum()),
            "efficiency": float(reco_num.sum() / truth_den.sum())
            if truth_den.sum() > 0.0 else 0.0,
            "fake_weighted_by_reco_bin": float(fake_reco.sum()),
        },
        "pz_strips": strips,
        "pt_bins": edge_pairs(PT_EDGES),
        "pz_bins": edge_pairs(PZ_EDGES),
        "truth_denominator_2d_pt_by_pz": truth_den.tolist(),
        "reco_numerator_2d_pt_by_pz": reco_num.tolist(),
        "efficiency_2d_pt_by_pz": eff_2d.tolist(),
        "fake_yield_2d_pt_by_pz": fake_reco.tolist(),
        "outputs": outputs,
    }

    with open(outputs["summary_json"], "w", encoding="utf-8") as fout:
        json.dump(summary, fout, indent=2, sort_keys=True)
        fout.write("\n")

    plot_eff_vs_pz(outputs["eff_vs_pz_png"], den_pz, num_pz, eff_pz)
    plot_eff_2d(outputs["eff_2d_png"], eff_2d)
    plot_fake_vs_pz(outputs["fake_vs_pz_png"], fake_pz)
    plot_ratio_vs_pz(outputs["reco_truth_ratio_vs_pz_png"], den_pz, num_pz)

    low_eff = eff_pz[0]
    high_mask = np.asarray(PZ_EDGES[:-1]) >= 20.0
    if den_pz[high_mask].sum() > 0.0:
        high_eff = float(np.average(eff_pz[high_mask], weights=den_pz[high_mask]))
    else:
        high_eff = 0.0

    print("[WARN] Diagnostic only: this is not an unfolding correction.")
    print(f"[INFO] Input: {input_path}")
    print(f"[INFO] dataPOT={data_pot:.6e}, mcPOT={mc_pot:.6e}, "
          f"potScale={pot_scale:.6g}")
    print(f"[INFO] truth weighted={truth_den.sum():.6g}, "
          f"reco-passing weighted={reco_num.sum():.6g}, "
          f"eff={summary['totals']['efficiency']:.4f}")
    print(f"[INFO] fake weighted yield={fake_reco.sum():.6g}")
    print(f"[CHECK] efficiency pz 1.5-2.0={low_eff:.4f}; "
          f"weighted average pz >=20={high_eff:.4f}")
    print("[INFO] p_parallel strips:")
    for strip in strips:
        print("  "
              f"{strip['pz_low']:4.1f}-{strip['pz_high']:4.1f}: "
              f"truth={strip['truth_weighted']:.6g}, "
              f"reco={strip['reco_passing_weighted_by_truth_bin']:.6g}, "
              f"eff={strip['efficiency']:.4f}, "
              f"fake={strip['fake_weighted_by_reco_bin']:.6g}")
    print("[INFO] Wrote:")
    for path in outputs.values():
        print(f"  {path}")


if __name__ == "__main__":
    main()
