#!/usr/bin/env python3
"""
Compare our local CV flux (the nu-e-constrained ME FHC flux that
`FluxAndCVReweighter` reads from the CVS-checkout
`MATFluxAndReweightFiles/flux/` tree) against the public 2019 MINERvA
flux release (Aliaga et al., PRD 100 092001, arXiv:1906.00111).

The 2019 release is the paper-era nu-e-constrained ME flux. arXiv:2106.16210
(Ruterbories) cites it. Our local files are timestamped 2021-07-07 and
yield a 1.41x too-low shape at p_||=1.5-2 GeV/c. This script lets us see
whether the local CV flux disagrees with the 2019 ancillary at low E_nu
in a way that explains the residual.

What the script does
--------------------
  1. For each of the 12 ME FHC playlists 1A..1P, read the per-playlist
     data POT from baseline_flux/runEventLoopData_<P>.root.
  2. Map each playlist to its CV flux file via the FluxReweighter
     `playlistString()` mapping: 1A..1F -> 1D, 1G/1L/1M -> 1M,
     1N/1O/1P -> 1N. (Three unique flux files cover all 12 playlists.)
  3. Sum data POTs by flux-file group, then build a POT-weighted CV
     E_nu flux (`flux_E_cvweighted` from gen2thin files) and Geant4
     baseline (`flux_E_unweighted` from g4numiv6 files).
  4. If --paper-flux is given, overlay the paper curve on the CV flux
     and produce a ratio panel (paper/ours).
  5. Always emit the local CV and unweighted curves as a CSV so the
     overlay can be reproduced or compared with anything else.

The paper-flux file
-------------------
The 2019 release is at https://minerva.fnal.gov/minerva-fluxes/ under
"Earlier Neutrino-Mode Flux" (PRD 100 092001), accessible from the
arXiv:1906.00111 ancillary files. Pass either:
  * a ROOT file with a 1D flux histogram (TH1*/MnvH1D); name with
    --paper-flux-hist if not auto-detected; or
  * a 2-column whitespace/CSV text file `E_nu_GeV  flux` (units
    /m^2/POT/GeV by default; --paper-flux-units to override).

Outputs
-------
  * compare_flux_to_paper_2019.png  -- 3-panel plot
  * compare_flux_to_paper_2019.csv  -- per-Enu-bin numerics

Read-only on the filesystem outside the working dir.
"""

import argparse
import csv
import os
import sys
import tempfile

os.environ.setdefault(
    "MPLCONFIGDIR",
    os.path.join(tempfile.gettempdir(), "minerva101-mplconfig"),
)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import ROOT

ROOT.gROOT.SetBatch(True)

# ---------------------------------------------------------------------------
# Static configuration

PLAYLISTS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G",
             "1L", "1M", "1N", "1O", "1P"]

# FluxReweighter::playlistString() mapping for ME FHC.
PLAYLIST_TO_FLUX = {
    "1A": "minervame1D", "1B": "minervame1D", "1C": "minervame1D",
    "1D": "minervame1D", "1E": "minervame1D", "1F": "minervame1D",
    "1G": "minervame1M", "1L": "minervame1M", "1M": "minervame1M",
    "1N": "minervame1N", "1O": "minervame1N", "1P": "minervame1N",
}

FLUX_DIR = "/pscratch/sd/j/josephrb/minerva/minerva_large_files/MATFluxAndReweightFiles/flux"
BASE_DIR = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux"

# CV-weighted (nu-e constrained) lives in the gen2thin file.
# Geant4 baseline (denominator of the weight) lives in the g4numiv6 file.
CV_FILE_FMT = "flux-gen2thin-pdg14-{tag}_rearrangedUniverses.root"
CV_HIST = "flux_E_cvweighted"
UNW_FILE_FMT = "flux-g4numiv6-pdg14-{tag}_rearrangedUniverses.root"
UNW_HIST = "flux_E_unweighted"


# ---------------------------------------------------------------------------
# I/O helpers

def read_pot_data(playlist):
    path = f"{BASE_DIR}/runEventLoopData_{playlist}.root"
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"could not open {path}")
    par = f.Get("POTUsed")
    if not par:
        raise RuntimeError(f"POTUsed missing in {path}")
    return float(par.GetVal())


def read_th1_as_arrays(path, hist_name):
    """Return (low_edges, high_edges, contents). Bin contents in
    /m^2/POT/GeV (the FluxReweighter convention)."""
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"could not open {path}")
    h = f.Get(hist_name)
    if not h:
        raise RuntimeError(f"{hist_name} missing in {path}")
    n = h.GetNbinsX()
    lo = np.array([h.GetBinLowEdge(i) for i in range(1, n + 1)], dtype=float)
    hi = np.array([h.GetBinLowEdge(i + 1) for i in range(1, n + 1)], dtype=float)
    contents = np.array([h.GetBinContent(i) for i in range(1, n + 1)],
                        dtype=float)
    return lo, hi, contents


# ---------------------------------------------------------------------------
# Local POT-weighted CV flux

def aggregate_local_flux():
    """POT-weighted average across the 3 unique CV flux files."""
    pot_by_tag = {}
    for p in PLAYLISTS:
        tag = PLAYLIST_TO_FLUX[p]
        pot_by_tag[tag] = pot_by_tag.get(tag, 0.0) + read_pot_data(p)

    pot_total = sum(pot_by_tag.values())
    print(f"[info] read 12 playlists, total data POT = {pot_total:.4e}")
    for tag, pot in pot_by_tag.items():
        print(f"        {tag}: POT = {pot:.4e} ({100 * pot / pot_total:.2f}%)")

    ref_lo = ref_hi = None
    cv_sum = unw_sum = None
    for tag, pot in pot_by_tag.items():
        cv_path = f"{FLUX_DIR}/{CV_FILE_FMT.format(tag=tag)}"
        unw_path = f"{FLUX_DIR}/{UNW_FILE_FMT.format(tag=tag)}"

        lo, hi, cv = read_th1_as_arrays(cv_path, CV_HIST)
        _, _, unw = read_th1_as_arrays(unw_path, UNW_HIST)

        if ref_lo is None:
            ref_lo, ref_hi = lo, hi
            cv_sum = pot * cv
            unw_sum = pot * unw
        else:
            if not (np.allclose(lo, ref_lo) and np.allclose(hi, ref_hi)):
                raise RuntimeError(f"binning mismatch for {tag}")
            cv_sum += pot * cv
            unw_sum += pot * unw

    cv_avg = cv_sum / pot_total
    unw_avg = unw_sum / pot_total
    return ref_lo, ref_hi, cv_avg, unw_avg


# ---------------------------------------------------------------------------
# Paper flux loader

def load_paper_flux(path, hist_name=None, units_scale=1.0):
    """Return (E_nu, flux) at bin centers / sample points."""
    if path.endswith(".root"):
        f = ROOT.TFile.Open(path, "READ")
        if not f or f.IsZombie():
            raise RuntimeError(f"could not open {path}")
        if hist_name is None:
            keys = [k.GetName() for k in f.GetListOfKeys()]
            cands = [k for k in keys
                     if "flux" in k.lower() or "phi" in k.lower()]
            if len(cands) != 1:
                raise RuntimeError(
                    f"could not auto-detect flux hist in {path}; "
                    f"keys = {keys}; pass --paper-flux-hist")
            hist_name = cands[0]
            print(f"[info] auto-detected paper hist: {hist_name}")
        h = f.Get(hist_name)
        if not h:
            raise RuntimeError(f"{hist_name} missing in {path}")
        n = h.GetNbinsX()
        x = np.array([h.GetBinCenter(i) for i in range(1, n + 1)])
        y = np.array([h.GetBinContent(i) for i in range(1, n + 1)])
        return x, y * units_scale

    # Plain text / CSV. Two supported layouts:
    #   2 columns:  E_nu_GeV, flux
    #   3 columns:  bin_low_GeV, bin_high_GeV, flux  (used by the
    #               arXiv:1906.00111 ancillary release)
    # Header lines and lines beginning with '#' are skipped.
    rows = []
    with open(path) as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.replace(",", " ").split()
            try:
                vals = [float(x) for x in parts]
            except ValueError:
                continue
            rows.append(vals)
    if not rows:
        raise RuntimeError(f"no data rows in {path}")
    ncols = max(len(r) for r in rows)
    if ncols >= 3:
        arr = np.array([r for r in rows if len(r) >= 3])
        x = 0.5 * (arr[:, 0] + arr[:, 1])
        y = arr[:, 2]
    elif ncols == 2:
        arr = np.array(rows)
        x = arr[:, 0]
        y = arr[:, 1]
    else:
        raise RuntimeError(f"need >=2 numeric columns in {path}, got {ncols}")
    return x, y * units_scale


def rebin_paper_to_local(paper_x, paper_y, lo, hi):
    """Linearly interpolate paper (E_nu_center, flux) to bin centers
    of the local binning. Returns one value per local bin."""
    centers = 0.5 * (lo + hi)
    return np.interp(centers, paper_x, paper_y, left=np.nan, right=np.nan)


# ---------------------------------------------------------------------------
# Plot + dump

def write_csv(path, lo, hi, cv, unw, paper=None):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        cols = ["enu_low", "enu_high", "enu_center", "local_cv",
                "local_unweighted", "local_cv_over_unweighted"]
        if paper is not None:
            cols += ["paper_cv", "paper_over_local"]
        w.writerow(cols)
        centers = 0.5 * (lo + hi)
        ratio_corr = np.where(unw > 0, cv / unw, np.nan)
        if paper is not None:
            paper_over_local = np.where(cv > 0, paper / cv, np.nan)
        for i in range(len(lo)):
            row = [lo[i], hi[i], centers[i], cv[i], unw[i], ratio_corr[i]]
            if paper is not None:
                row += [paper[i], paper_over_local[i]]
            w.writerow(row)


def make_plot(out_path, lo, hi, cv, unw, paper=None):
    centers = 0.5 * (lo + hi)
    width = hi - lo

    if paper is not None:
        fig, axs = plt.subplots(3, 1, figsize=(9.0, 11.0), sharex=True,
                                gridspec_kw=dict(height_ratios=[3, 2, 2]))
    else:
        fig, axs = plt.subplots(2, 1, figsize=(9.0, 8.0), sharex=True,
                                gridspec_kw=dict(height_ratios=[3, 2]))

    ax = axs[0]
    ax.step(lo, cv, where="post", lw=1.6, color="C0",
            label="Local CV (gen2thin, POT-wtd MEHFC)")
    ax.step(lo, unw, where="post", lw=1.0, color="C0", alpha=0.4,
            label="Local Geant4 baseline (g4numiv6)")
    if paper is not None:
        ax.step(lo, paper, where="post", lw=1.6, color="C3",
                label="Paper 2019 ancillary (PRD 100 092001)")
    ax.set_yscale("log")
    ax.set_ylabel(r"$\Phi(E_\nu)$  [/m$^2$/POT/GeV]")
    ax.set_xlim(0.0, 20.0)
    ax.legend(loc="best")
    ax.grid(True, which="both", alpha=0.3)
    ax.set_title("ME FHC nu-mu flux: local CVS-checkout vs 2019 release")

    ax = axs[1]
    corr = np.where(unw > 0, cv / unw, np.nan)
    ax.step(lo, corr, where="post", lw=1.4, color="C2")
    ax.axhline(1.0, color="k", lw=0.5, alpha=0.5)
    ax.set_ylabel("CV / Geant4\n(nu-e constraint factor)")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0.0, 20.0)

    if paper is not None:
        ax = axs[2]
        ratio = np.where(cv > 0, paper / cv, np.nan)
        ax.step(lo, ratio, where="post", lw=1.4, color="C3")
        ax.axhline(1.0, color="k", lw=0.5, alpha=0.5)
        ax.set_ylabel("Paper / Local")
        ax.set_ylim(0.5, 1.6)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0.0, 20.0)

    axs[-1].set_xlabel(r"$E_\nu$  [GeV]")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paper-flux", default=None,
                   help="Path to a 2019-release flux file (ROOT or text).")
    p.add_argument("--paper-flux-hist", default=None,
                   help="Histogram name inside a ROOT --paper-flux file.")
    p.add_argument("--paper-flux-units", default="per_m2_per_pot_per_gev",
                   choices=["per_m2_per_pot_per_gev", "per_cm2_per_pot_per_gev"],
                   help="Units of the paper flux. Local files are "
                        "/m^2/POT/GeV.")
    p.add_argument("--out-png",
                   default="compare_flux_to_paper_2019.png")
    p.add_argument("--out-csv",
                   default="compare_flux_to_paper_2019.csv")
    args = p.parse_args()

    lo, hi, cv, unw = aggregate_local_flux()

    paper_at_local = None
    if args.paper_flux is not None:
        scale = 1.0
        if args.paper_flux_units == "per_cm2_per_pot_per_gev":
            scale = 1.0e4  # cm^-2 -> m^-2
        paper_x, paper_y = load_paper_flux(args.paper_flux,
                                           args.paper_flux_hist, scale)
        paper_at_local = rebin_paper_to_local(paper_x, paper_y, lo, hi)
        print(f"[info] loaded paper flux from {args.paper_flux} "
              f"({len(paper_x)} sample points, "
              f"E_nu in [{paper_x.min():.2f}, {paper_x.max():.2f}] GeV)")

    print()
    print(f"{'E_nu (GeV)':>12} {'local_CV':>12} {'CV/G4':>8} "
          f"{'paper':>12} {'paper/local':>12}")
    centers = 0.5 * (lo + hi)
    for i, c in enumerate(centers):
        if c < 1.0 or c > 10.0:
            continue
        corr = cv[i] / unw[i] if unw[i] > 0 else float("nan")
        if paper_at_local is not None:
            pap = paper_at_local[i]
            ratio = pap / cv[i] if cv[i] > 0 else float("nan")
            print(f"{c:>12.3f} {cv[i]:>12.4e} {corr:>8.3f} "
                  f"{pap:>12.4e} {ratio:>12.4f}")
        else:
            print(f"{c:>12.3f} {cv[i]:>12.4e} {corr:>8.3f}")

    write_csv(args.out_csv, lo, hi, cv, unw, paper_at_local)
    make_plot(args.out_png, lo, hi, cv, unw, paper_at_local)
    print(f"\n[ok] wrote {args.out_csv}")
    print(f"[ok] wrote {args.out_png}")


if __name__ == "__main__":
    main()
