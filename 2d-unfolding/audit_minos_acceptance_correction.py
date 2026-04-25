#!/usr/bin/env python3
"""
Audit whether the residual paper comparison gradient has the shape expected
from a missing MINOS/range-out acceptance correction.

This is read-only. It compares:
  1. strip-summed ours/paper cross-section ratios,
  2. implied xsec multipliers needed to match the paper,
  3. inverse-efficiency shape from diagnose_minos_acceptance_2d.py, and
  4. optionally, an external strip correction map once one is found.
"""

import argparse
import csv
import json
import math
import os
import tempfile
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
    from unfold_2d_omnifold_unbinned import PT_EDGES, PZ_EDGES
except ImportError as exc:
    raise RuntimeError(
        "Could not import PT_EDGES/PZ_EDGES from "
        "Documents/unfold_2d_omnifold_unbinned.py. Run from the repository root."
    ) from exc


ANC_DIR = "/pscratch/sd/j/josephrb/MINERvA101/Documents/minerva_paper_anc"
DEFAULT_OURS = "Documents/2d_crossSection_omnifold_1A_minos_fix_5iter.root"
DEFAULT_DIAG = "Documents/minos_acceptance_1A_summary.json"
DEFAULT_OUT_PREFIX = "Documents/minos_acceptance_audit_1A"

N_PT = 14
N_PZ = 16
N = N_PT * N_PZ
TAN_THETA_MAX = math.tan(math.radians(20.0))


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ours", default=DEFAULT_OURS,
                        help="Our 2D cross-section ROOT file containing hXSec2D")
    parser.add_argument("--diagnostic", default=DEFAULT_DIAG,
                        help="JSON from diagnose_minos_acceptance_2d.py")
    parser.add_argument("--external-map", default=None,
                        help="Optional JSON/CSV strip correction map")
    parser.add_argument("--out-prefix", default=DEFAULT_OUT_PREFIX,
                        help="Output prefix for JSON/PNG")
    parser.add_argument("--mask", choices=["strict-interior", "reported"],
                        default="strict-interior",
                        help="Bins used in strip sums")
    return parser.parse_args()


def tmatrix_to_np(tm):
    n = tm.GetNrows()
    arr = np.empty((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            arr[i, j] = float(tm(i, j))
    return arr


def flatten_paper(h):
    """Paper global convention: gid = (ptbin - 1) * 16 + (pzbin - 1)."""
    vals = np.zeros(N, dtype=float)
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    x_is_pt = nx == N_PT
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            ptb, pzb = (ix, iy) if x_is_pt else (iy, ix)
            gid = (ptb - 1) * N_PZ + (pzb - 1)
            vals[gid] = float(h.GetBinContent(ix, iy))
    return vals


def flatten_ours(h):
    vals = np.zeros(N, dtype=float)
    if h.GetNbinsX() != N_PT or h.GetNbinsY() != N_PZ:
        raise RuntimeError(
            f"hXSec2D has shape {h.GetNbinsX()}x{h.GetNbinsY()}, "
            f"expected {N_PT}x{N_PZ}")
    for ix in range(1, N_PT + 1):
        for iy in range(1, N_PZ + 1):
            gid = (ix - 1) * N_PZ + (iy - 1)
            vals[gid] = float(h.GetBinContent(ix, iy))
    return vals


def load_paper():
    path = f"{ANC_DIR}/cov_ptpl_minerva_inclusive_6GeV.root"
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"Could not open paper ancillary ROOT file: {path}")
    try:
        h = f.Get("pt_pl_cross_section")
        cov_stat = tmatrix_to_np(f.Get("StatOnlyCovariance"))
        if not h:
            raise RuntimeError("Missing pt_pl_cross_section in paper ROOT file")
        return flatten_paper(h), np.diag(cov_stat) > 0.0
    finally:
        f.Close()


def load_ours(path):
    f = ROOT.TFile.Open(str(path), "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"Could not open our cross-section ROOT file: {path}")
    try:
        h = f.Get("hXSec2D")
        if not h:
            raise RuntimeError(f"Missing hXSec2D in {path}")
        return flatten_ours(h)
    finally:
        f.Close()


def strict_interior_mask():
    mask = np.zeros(N, dtype=bool)
    for ptb in range(1, N_PT + 1):
        pt_hi = PT_EDGES[ptb]
        for pzb in range(1, N_PZ + 1):
            pz_lo = PZ_EDGES[pzb - 1]
            gid = (ptb - 1) * N_PZ + (pzb - 1)
            mask[gid] = (pt_hi / pz_lo) <= TAN_THETA_MAX
    return mask


def load_diagnostic(path):
    with open(path, encoding="utf-8") as fin:
        data = json.load(fin)
    strips = data["pz_strips"]
    if len(strips) != N_PZ:
        raise RuntimeError(f"Diagnostic has {len(strips)} pz strips, expected {N_PZ}")
    return data, strips


def load_external_map(path):
    if not path:
        return None
    path = Path(path)
    rows = []
    if path.suffix.lower() == ".json":
        with open(path, encoding="utf-8") as fin:
            obj = json.load(fin)
        raw = obj.get("pz_strips", obj if isinstance(obj, list) else None)
        if raw is None:
            raise RuntimeError("JSON external map must be a list or contain pz_strips")
        rows = raw
    else:
        with open(path, newline="", encoding="utf-8") as fin:
            rows = list(csv.DictReader(fin))

    out = {}
    for row in rows:
        lo = float(row.get("pz_low", row.get("pz_min")))
        hi = float(row.get("pz_high", row.get("pz_max")))
        val = row.get("xsec_multiplier", row.get("correction", row.get("factor")))
        if val is None:
            raise RuntimeError(
                "External map rows need xsec_multiplier, correction, or factor")
        out[(lo, hi)] = float(val)
    return out


def build_strip_table(ours, paper, reported, diag_strips, ext_map, mask_mode):
    interior = strict_interior_mask()
    base_mask = reported.copy()
    if mask_mode == "strict-interior":
        base_mask &= interior

    eff = np.asarray([s["efficiency"] for s in diag_strips], dtype=float)
    den = np.asarray([s["truth_weighted"] for s in diag_strips], dtype=float)
    ref = np.asarray(PZ_EDGES[:-1]) >= 20.0
    if den[ref].sum() <= 0.0:
        ref_eff = float(np.nanmedian(eff[eff > 0.0]))
    else:
        ref_eff = float(np.average(eff[ref], weights=den[ref]))

    table = []
    for pzb, (lo, hi) in enumerate(zip(PZ_EDGES[:-1], PZ_EDGES[1:]), start=1):
        strip_mask = np.zeros(N, dtype=bool)
        for ptb in range(1, N_PT + 1):
            gid = (ptb - 1) * N_PZ + (pzb - 1)
            strip_mask[gid] = True
        use = strip_mask & base_mask & (paper > 0.0)
        paper_sum = float(paper[use].sum())
        ours_sum = float(ours[use].sum())
        ratio = ours_sum / paper_sum if paper_sum > 0.0 else 0.0
        implied = 1.0 / ratio if ratio > 0.0 else 0.0
        inv_eff_shape = ref_eff / eff[pzb - 1] if eff[pzb - 1] > 0.0 else 0.0
        external = None
        if ext_map is not None:
            external = ext_map.get((float(lo), float(hi)))

        table.append({
            "pz_low": float(lo),
            "pz_high": float(hi),
            "n_bins": int(use.sum()),
            "paper_sum": paper_sum,
            "ours_sum": ours_sum,
            "ours_over_paper": ratio,
            "implied_xsec_multiplier": implied,
            "diagnostic_efficiency": float(eff[pzb - 1]),
            "inverse_efficiency_shape_to_pz_ge_20": float(inv_eff_shape),
            "fake_weighted_by_reco_bin": float(
                diag_strips[pzb - 1]["fake_weighted_by_reco_bin"]),
            "external_xsec_multiplier": external,
        })
    return table, ref_eff


def write_outputs(prefix, summary):
    json_path = f"{prefix}_summary.json"
    png_path = f"{prefix}_strips.png"

    with open(json_path, "w", encoding="utf-8") as fout:
        json.dump(summary, fout, indent=2, sort_keys=True)
        fout.write("\n")

    strips = summary["pz_strips"]
    pz = np.asarray([0.5 * (s["pz_low"] + s["pz_high"]) for s in strips])
    width = np.asarray([s["pz_high"] - s["pz_low"] for s in strips])
    ratio = np.asarray([s["ours_over_paper"] if s["n_bins"] else np.nan
                        for s in strips])
    implied = np.asarray([s["implied_xsec_multiplier"] if s["n_bins"] else np.nan
                          for s in strips])
    inv_eff = np.asarray([s["inverse_efficiency_shape_to_pz_ge_20"]
                          for s in strips])
    external = np.asarray([
        np.nan if s["external_xsec_multiplier"] is None
        else s["external_xsec_multiplier"]
        for s in strips
    ])

    fig, axs = plt.subplots(2, 1, figsize=(9.0, 8.0), sharex=True)
    axs[0].axhline(1.0, color="#555555", lw=1.0, ls="--")
    axs[0].errorbar(pz, ratio, xerr=width / 2.0, fmt="o-",
                    color="#1f77b4", capsize=2, label="ours / paper")
    axs[0].set_ylabel("strip xsec ratio")
    axs[0].grid(True, alpha=0.25)
    axs[0].legend(frameon=False)

    axs[1].axhline(1.0, color="#555555", lw=1.0, ls="--")
    axs[1].errorbar(pz, implied, xerr=width / 2.0, fmt="s-",
                    color="#d62728", capsize=2,
                    label="paper/ours required")
    axs[1].plot(pz, inv_eff, "^-", color="#2ca02c",
                label="inverse efficiency shape")
    if np.isfinite(external).any():
        axs[1].plot(pz, external, "D-", color="#9467bd",
                    label="external map")
    axs[1].set_xlabel(r"$p_{\parallel}$ (GeV/c)")
    axs[1].set_ylabel("multiplicative factor")
    axs[1].grid(True, alpha=0.25)
    axs[1].legend(frameon=False)

    fig.suptitle("MINOS acceptance audit: required xsec lift vs efficiency shape")
    fig.tight_layout()
    fig.savefig(png_path, dpi=160)
    plt.close(fig)
    return json_path, png_path


def main():
    args = parse_args()
    paper, reported = load_paper()
    ours = load_ours(args.ours)
    diag, diag_strips = load_diagnostic(args.diagnostic)
    ext_map = load_external_map(args.external_map)
    table, ref_eff = build_strip_table(
        ours, paper, reported, diag_strips, ext_map, args.mask)

    valid = [r for r in table if r["n_bins"] > 0 and r["ours_over_paper"] > 0.0]
    implied = np.asarray([r["implied_xsec_multiplier"] for r in valid])
    inv_eff = np.asarray([r["inverse_efficiency_shape_to_pz_ge_20"] for r in valid])
    corr = float(np.corrcoef(implied, inv_eff)[0, 1]) if len(valid) > 1 else 0.0

    summary = {
        "warning": (
            "Read-only audit. These factors are diagnostic multipliers, not an "
            "approved correction."
        ),
        "ours": args.ours,
        "diagnostic": args.diagnostic,
        "external_map": args.external_map,
        "mask": args.mask,
        "reference_efficiency_pz_ge_20": ref_eff,
        "correlation_implied_multiplier_vs_inverse_efficiency_shape": corr,
        "diagnostic_totals": diag.get("totals", {}),
        "pz_strips": table,
    }
    json_path, png_path = write_outputs(args.out_prefix, summary)

    print("[WARN] Read-only audit: these are diagnostic factors, not a correction.")
    print(f"[INFO] ours: {args.ours}")
    print(f"[INFO] diagnostic: {args.diagnostic}")
    print(f"[INFO] mask: {args.mask}")
    print(f"[INFO] ref efficiency pz>=20: {ref_eff:.4f}")
    print(f"[INFO] corr(required multiplier, inverse-eff shape): {corr:.4f}")
    print("[INFO] p_parallel strips:")
    for row in table:
        if row["n_bins"] == 0:
            continue
        ext = ""
        if row["external_xsec_multiplier"] is not None:
            ext = f", external={row['external_xsec_multiplier']:.4f}"
        print(
            f"  {row['pz_low']:4.1f}-{row['pz_high']:4.1f}: "
            f"N={row['n_bins']:2d}, ours/paper={row['ours_over_paper']:.4f}, "
            f"required={row['implied_xsec_multiplier']:.4f}, "
            f"invEffShape={row['inverse_efficiency_shape_to_pz_ge_20']:.4f}"
            f"{ext}"
        )
    print("[INFO] Wrote:")
    print(f"  {json_path}")
    print(f"  {png_path}")


if __name__ == "__main__":
    main()
